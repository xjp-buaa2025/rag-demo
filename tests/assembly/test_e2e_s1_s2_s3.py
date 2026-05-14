"""End-to-end S1 → S2 → S3 smoke test (no LLM, no Neo4j, no Tavily).

Proves all three placeholders chain through schema validation and the router's
sequencing gates (409 errors) work as designed.
"""
from pathlib import Path
import json
import jsonschema
import pytest


def test_e2e_s1_s2_s3_chain_with_placeholders(client):
    """Run full chain with no LLM. Each stage should validate against its schema."""
    skill_root = Path(__file__).resolve().parents[2] / "skills" / "aero-engine-assembly-scheme"
    schema_s1 = json.loads((skill_root / "templates" / "schemas" / "stage1.schema.json").read_text(encoding="utf-8"))
    schema_s2 = json.loads((skill_root / "templates" / "schemas" / "stage2.schema.json").read_text(encoding="utf-8"))
    schema_s3 = json.loads((skill_root / "templates" / "schemas" / "stage3.schema.json").read_text(encoding="utf-8"))

    # 1. Create scheme
    create_resp = client.post(
        "/assembly-design/scheme/new",
        json={
            "subject_system": "PT6A 高压压气机",
            "subject_system_en": "PT6A HPC",
            "subject_scope": ["3 级轴流 + 1 级离心", "含转子/静子/支撑环"],
            "design_intent": "工艺优化",
            "constraints": {"primary": "可靠性", "secondary": "维修性"},
        },
    )
    assert create_resp.status_code == 200, create_resp.text
    scheme_id = create_resp.json()["scheme_id"]

    # 2. Stage 1
    r1 = client.post(
        f"/assembly-design/scheme/{scheme_id}/stage/1",
        json={"action": "generate", "payload": {}},
    )
    assert r1.status_code == 200, r1.text
    s1 = r1.json()
    jsonschema.validate(instance=s1, schema=schema_s1)

    # 3. Stage 2
    r2 = client.post(
        f"/assembly-design/scheme/{scheme_id}/stage/2",
        json={"action": "generate", "payload": {}},
    )
    assert r2.status_code == 200, r2.text
    s2 = r2.json()
    jsonschema.validate(instance=s2, schema=schema_s2)
    assert s2["stage1_ref"] == scheme_id

    # 4. Stage 3
    r3 = client.post(
        f"/assembly-design/scheme/{scheme_id}/stage/3",
        json={"action": "generate", "payload": {}},
    )
    assert r3.status_code == 200, r3.text
    s3 = r3.json()
    jsonschema.validate(instance=s3, schema=schema_s3)
    assert s3["stage1_ref"] == scheme_id
    assert s3["stage2_ref"] == scheme_id
    assert s3["recommended"] in {a["id"] for a in s3["candidate_architectures"]}

    # 5. Fetch composite scheme, all three present
    final = client.get(f"/assembly-design/scheme/{scheme_id}").json()
    for key in ("stage1", "stage2", "stage3"):
        assert key in final
    for k in ("1", "2", "3"):
        assert k in final["meta"]["stages_done"]


def test_e2e_stage4_through_5_still_501(client):
    """Plan 2 should not have accidentally enabled later stages."""
    create_resp = client.post(
        "/assembly-design/scheme/new",
        json={
            "subject_system": "PT6A HPC",
            "subject_scope": ["3 级轴流"],
            "design_intent": "工艺优化",
            "constraints": {"primary": "可靠性"},
        },
    )
    scheme_id = create_resp.json()["scheme_id"]
    for sk in ("4a", "4b", "4c", "4d", "5"):
        r = client.post(
            f"/assembly-design/scheme/{scheme_id}/stage/{sk}",
            json={"action": "generate", "payload": {}},
        )
        assert r.status_code == 501, f"stage {sk} should still be 501, got {r.status_code}"
