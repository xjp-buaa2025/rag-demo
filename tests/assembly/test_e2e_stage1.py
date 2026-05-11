"""E2E smoke test: create scheme → run stage 1 → fetch back → validate against schema."""
from pathlib import Path
import json
import jsonschema
import pytest


SKILL_ROOT = Path(__file__).resolve().parents[2] / "skills" / "aero-engine-assembly-scheme"


def test_e2e_stage1_full_cycle(client):
    # 1. Create scheme
    create_resp = client.post("/assembly-design/scheme/new", json={
        "subject_system": "PT6A 高压压气机",
        "subject_system_en": "PT6A HPC",
        "subject_scope": ["3 级轴流 + 1 级离心"],
        "design_intent": "工艺优化",
        "constraints": {"primary": "可靠性", "secondary": "维修性"},
    })
    assert create_resp.status_code == 200
    sid = create_resp.json()["scheme_id"]

    # 2. Run stage 1 generate
    gen_resp = client.post(
        f"/assembly-design/scheme/{sid}/stage/1",
        json={"action": "generate", "payload": {}},
    )
    assert gen_resp.status_code == 200
    stage1 = gen_resp.json()

    # 3. Validate against schema
    schema = json.loads(
        (SKILL_ROOT / "templates" / "schemas" / "stage1.schema.json").read_text(encoding="utf-8")
    )
    jsonschema.validate(instance=stage1, schema=schema)

    # 4. Fetch back via GET
    get_resp = client.get(f"/assembly-design/scheme/{sid}")
    assert get_resp.status_code == 200
    fetched = get_resp.json()
    assert fetched["meta"]["scheme_id"] == sid
    assert "stage1" in fetched
    assert fetched["stage1"]["task_card_md"]
    assert "1" in fetched["meta"]["stages_done"]

    # 5. List should include this scheme
    list_resp = client.get("/assembly-design/scheme/list")
    assert any(s["scheme_id"] == sid for s in list_resp.json()["schemes"])
