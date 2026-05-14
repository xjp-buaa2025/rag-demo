"""Tests for backend.routers.assembly_design."""
import json
import pytest


def test_create_scheme_returns_id_and_meta(client):
    resp = client.post("/assembly-design/scheme/new", json={
        "subject_system": "PT6A HPC",
        "subject_scope": ["3 级轴流"],
        "design_intent": "工艺优化",
        "constraints": {"primary": "可靠性"},
    })
    assert resp.status_code == 200
    data = resp.json()
    assert "scheme_id" in data
    assert data["scheme_id"].startswith("scheme-")
    assert data["meta"]["subject"]["system"] == "PT6A HPC"


def test_list_schemes_includes_created(client):
    client.post("/assembly-design/scheme/new", json={
        "subject_system": "Test A",
        "subject_scope": ["3 级轴流"],
        "design_intent": "工艺优化",
    })
    resp = client.get("/assembly-design/scheme/list")
    assert resp.status_code == 200
    items = resp.json()["schemes"]
    assert any(s["subject"]["system"] == "Test A" for s in items)


def test_get_scheme_404_when_missing(client):
    resp = client.get("/assembly-design/scheme/scheme-nonexistent")
    assert resp.status_code == 404


def test_run_stage1_generate_writes_stage1_json(client):
    create = client.post("/assembly-design/scheme/new", json={
        "subject_system": "PT6A HPC",
        "subject_scope": ["3 级轴流"],
        "design_intent": "工艺优化",
        "constraints": {"primary": "可靠性"},
    }).json()
    sid = create["scheme_id"]

    resp = client.post(
        f"/assembly-design/scheme/{sid}/stage/1",
        json={"action": "generate", "payload": {}},
    )
    assert resp.status_code == 200, resp.text
    body = resp.json()
    assert body["scheme_id"] == sid
    assert body["subject"]["system"] == "PT6A HPC"
    assert "task_card_md" in body


def test_run_stage_other_returns_501(client):
    create = client.post("/assembly-design/scheme/new", json={
        "subject_system": "Test", "subject_scope": ["3 级轴流"], "design_intent": "工艺优化",
    }).json()
    sid = create["scheme_id"]
    for stage_key in ["4c", "4d", "5"]:
        resp = client.post(
            f"/assembly-design/scheme/{sid}/stage/{stage_key}",
            json={"action": "generate"},
        )
        assert resp.status_code == 501, f"stage {stage_key} should be 501, got {resp.status_code}"


def test_stage4a_requires_stage3_first(client):
    """POST /stage/4a must 409 if stage3 has not been run."""
    create_resp = client.post(
        "/assembly-design/scheme/new",
        json={
            "subject_system": "PT6A HPC",
            "subject_scope": ["3 级轴流"],
            "design_intent": "工艺优化",
        },
    )
    scheme_id = create_resp.json()["scheme_id"]
    r = client.post(
        f"/assembly-design/scheme/{scheme_id}/stage/4a",
        json={"action": "generate", "payload": {}},
    )
    assert r.status_code == 409, r.text
    assert "stage3" in r.text.lower()


def test_stage4a_runs_after_s1_s2_s3(client):
    """Happy path: S1 → S2 → S3 → S4a."""
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
    assert client.post(f"/assembly-design/scheme/{scheme_id}/stage/1",
                       json={"action": "generate", "payload": {}}).status_code == 200
    assert client.post(f"/assembly-design/scheme/{scheme_id}/stage/2",
                       json={"action": "generate", "payload": {}}).status_code == 200
    assert client.post(f"/assembly-design/scheme/{scheme_id}/stage/3",
                       json={"action": "generate", "payload": {}}).status_code == 200

    r4a = client.post(
        f"/assembly-design/scheme/{scheme_id}/stage/4a",
        json={"action": "generate", "payload": {}},
    )
    assert r4a.status_code == 200, r4a.text
    body = r4a.json()
    assert "procedures" in body
    assert len(body["procedures"]) >= 1
    assert "topology" in body
    proc_ids = {p["id"] for p in body["procedures"]}
    topo_ids = set(body["topology"]["sequence"])
    assert proc_ids == topo_ids, f"topology mismatch: {proc_ids} vs {topo_ids}"

    final = client.get(f"/assembly-design/scheme/{scheme_id}").json()
    assert "stage4a" in final
    assert "4a" in final["meta"]["stages_done"]


def test_save_edits_overwrites_stage1(client):
    create = client.post("/assembly-design/scheme/new", json={
        "subject_system": "PT6A HPC", "subject_scope": ["3 级轴流"], "design_intent": "工艺优化",
    }).json()
    sid = create["scheme_id"]
    # First run generate
    client.post(f"/assembly-design/scheme/{sid}/stage/1", json={"action": "generate"})
    # Then save edits
    edits = {"task_card_md": "## 用户编辑后的卡", "scheme_id": sid, "subject": {"system": "edited"}}
    resp = client.post(
        f"/assembly-design/scheme/{sid}/stage/1",
        json={"action": "save_edits", "payload": edits},
    )
    assert resp.status_code == 200
    # Verify get_scheme returns the edits
    got = client.get(f"/assembly-design/scheme/{sid}").json()
    assert "用户编辑后的卡" in got["stage1"]["task_card_md"]


def test_unknown_action_returns_400(client):
    create = client.post("/assembly-design/scheme/new", json={
        "subject_system": "Test", "subject_scope": ["3 级轴流"], "design_intent": "工艺优化",
    }).json()
    sid = create["scheme_id"]
    resp = client.post(
        f"/assembly-design/scheme/{sid}/stage/1",
        json={"action": "unknown"},
    )
    assert resp.status_code == 400


def test_reflux_endpoint_returns_501_for_v1(client):
    create = client.post("/assembly-design/scheme/new", json={
        "subject_system": "Test", "subject_scope": ["3 级轴流"], "design_intent": "工艺优化",
    }).json()
    sid = create["scheme_id"]
    resp = client.post(f"/assembly-design/scheme/{sid}/reflux", json={"approved": []})
    assert resp.status_code == 501


def test_iterate_endpoint_returns_501_for_v1(client):
    create = client.post("/assembly-design/scheme/new", json={
        "subject_system": "Test", "subject_scope": ["3 级轴流"], "design_intent": "工艺优化",
    }).json()
    sid = create["scheme_id"]
    resp = client.post(f"/assembly-design/scheme/{sid}/iterate", json={"target_stage_key": "4a"})
    assert resp.status_code == 501


def test_export_endpoint_returns_501_for_v1(client):
    create = client.post("/assembly-design/scheme/new", json={
        "subject_system": "Test", "subject_scope": ["3 级轴流"], "design_intent": "工艺优化",
    }).json()
    sid = create["scheme_id"]
    resp = client.get(f"/assembly-design/scheme/{sid}/export")
    assert resp.status_code == 501


def test_create_scheme_rejects_empty_scope(client):
    """subject_scope=[] must be rejected at the API boundary, not silently passed through."""
    resp = client.post(
        "/assembly-design/scheme/new",
        json={
            "subject_system": "PT6A HPC",
            "subject_scope": [],
            "design_intent": "工艺优化",
            "constraints": {"primary": "可靠性"},
        },
    )
    assert resp.status_code == 422, f"expected 422, got {resp.status_code}: {resp.text}"


def test_create_scheme_accepts_single_element_scope(client):
    """A 1-element scope must succeed."""
    resp = client.post(
        "/assembly-design/scheme/new",
        json={
            "subject_system": "PT6A HPC",
            "subject_scope": ["3 级轴流"],
            "design_intent": "工艺优化",
            "constraints": {"primary": "可靠性"},
        },
    )
    assert resp.status_code == 200, resp.text
    assert resp.json()["meta"]["subject"]["scope"] == ["3 级轴流"]


def test_concurrent_stage_writes_are_serialized(client, monkeypatch):
    """Two threads hitting the same stage must not corrupt stages_done.

    We don't measure throughput — we measure that meta.json after both writes
    has each stage_key listed exactly once (no duplicate, no missing).
    """
    import threading

    # 1) Create a scheme
    resp = client.post(
        "/assembly-design/scheme/new",
        json={
            "subject_system": "PT6A HPC",
            "subject_scope": ["3 级轴流"],
            "design_intent": "工艺优化",
            "constraints": {"primary": "可靠性"},
        },
    )
    scheme_id = resp.json()["scheme_id"]

    errors: list = []

    def hit_stage_one():
        try:
            r = client.post(
                f"/assembly-design/scheme/{scheme_id}/stage/1",
                json={"action": "generate", "payload": {}},
            )
            assert r.status_code == 200, r.text
        except Exception as e:
            errors.append(e)

    t1 = threading.Thread(target=hit_stage_one)
    t2 = threading.Thread(target=hit_stage_one)
    t1.start(); t2.start()
    t1.join(); t2.join()

    assert not errors, f"thread errors: {errors}"

    # Re-fetch and check stages_done has no duplicates
    final = client.get(f"/assembly-design/scheme/{scheme_id}").json()
    assert final["meta"]["stages_done"].count("1") == 1, final["meta"]["stages_done"]


def test_stage2_requires_stage1_first(client):
    """POST /stage/2 must 409 if stage1 has not been run yet."""
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
    resp = client.post(
        f"/assembly-design/scheme/{scheme_id}/stage/2",
        json={"action": "generate", "payload": {}},
    )
    assert resp.status_code == 409, resp.text
    assert "stage1" in resp.text.lower()


def test_stage2_runs_after_stage1(client):
    """Happy path: create scheme → run stage1 → run stage2 → fetch and see both."""
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
    r1 = client.post(
        f"/assembly-design/scheme/{scheme_id}/stage/1",
        json={"action": "generate", "payload": {}},
    )
    assert r1.status_code == 200, r1.text
    r2 = client.post(
        f"/assembly-design/scheme/{scheme_id}/stage/2",
        json={"action": "generate", "payload": {}},
    )
    assert r2.status_code == 200, r2.text
    body = r2.json()
    assert "user_needs" in body
    assert "dfa_score" in body
    assert body["stage1_ref"] == scheme_id
    final = client.get(f"/assembly-design/scheme/{scheme_id}").json()
    assert "stage1" in final
    assert "stage2" in final
    assert "2" in final["meta"]["stages_done"]


def test_stage2_save_edits(client):
    """save_edits action writes payload verbatim, no LLM call."""
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
    client.post(
        f"/assembly-design/scheme/{scheme_id}/stage/1",
        json={"action": "generate", "payload": {}},
    )
    edited = {
        "stage1_ref": scheme_id,
        "user_needs": [{"id": "U99", "text": "陛下手改", "weight": 5}],
        "engineering_metrics": [{"id": "M99", "name": "X", "target": ">=1", "linked_needs": ["U99"]}],
        "assembly_features": [{"id": "F99", "name": "X", "spec": "X", "linked_metrics": ["M99"]}],
        "key_characteristics": [{"id": "KC99", "name": "X", "target": "X", "criticality": "low", "linked_features": ["F99"]}],
        "dfa_score": {"overall": 0.5, "theoretical_min_parts": 1, "actual_parts": 1, "bottlenecks": []},
        "risks": [{"id": "R99", "text": "X", "severity": 1, "linked_kcs": ["KC99"]}],
    }
    r = client.post(
        f"/assembly-design/scheme/{scheme_id}/stage/2",
        json={"action": "save_edits", "payload": edited},
    )
    assert r.status_code == 200, r.text
    final = client.get(f"/assembly-design/scheme/{scheme_id}").json()
    assert final["stage2"]["user_needs"][0]["id"] == "U99"


def test_stage3_requires_stage2_first(client):
    """POST /stage/3 must 409 if stage2 has not been run."""
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
    r = client.post(
        f"/assembly-design/scheme/{scheme_id}/stage/3",
        json={"action": "generate", "payload": {}},
    )
    assert r.status_code == 409, r.text
    assert "stage2" in r.text.lower()


def test_stage3_runs_after_stage1_stage2(client):
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
    assert client.post(f"/assembly-design/scheme/{scheme_id}/stage/1",
                       json={"action": "generate", "payload": {}}).status_code == 200
    assert client.post(f"/assembly-design/scheme/{scheme_id}/stage/2",
                       json={"action": "generate", "payload": {}}).status_code == 200
    r3 = client.post(f"/assembly-design/scheme/{scheme_id}/stage/3",
                     json={"action": "generate", "payload": {}})
    assert r3.status_code == 200, r3.text
    body = r3.json()
    assert "candidate_architectures" in body
    assert len(body["candidate_architectures"]) >= 2
    assert body["recommended"] in {a["id"] for a in body["candidate_architectures"]}
    assert body["stage1_ref"] == scheme_id
    assert body["stage2_ref"] == scheme_id

    final = client.get(f"/assembly-design/scheme/{scheme_id}").json()
    assert "stage3" in final
    assert "3" in final["meta"]["stages_done"]


def test_stage4b_requires_stage4a_first(client):
    """POST /stage/4b must 409 if stage4a has not been run."""
    create_resp = client.post(
        "/assembly-design/scheme/new",
        json={
            "subject_system": "PT6A HPC",
            "subject_scope": ["3 级轴流"],
            "design_intent": "工艺优化",
        },
    )
    scheme_id = create_resp.json()["scheme_id"]
    r = client.post(
        f"/assembly-design/scheme/{scheme_id}/stage/4b",
        json={"action": "generate", "payload": {}},
    )
    assert r.status_code == 409, r.text
    assert "stage4a" in r.text.lower()


def test_stage4b_runs_after_full_chain(client):
    """Happy path: S1 → S2 → S3 → S4a → S4b."""
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
    assert client.post(f"/assembly-design/scheme/{scheme_id}/stage/1",
                       json={"action": "generate", "payload": {}}).status_code == 200
    assert client.post(f"/assembly-design/scheme/{scheme_id}/stage/2",
                       json={"action": "generate", "payload": {}}).status_code == 200
    assert client.post(f"/assembly-design/scheme/{scheme_id}/stage/3",
                       json={"action": "generate", "payload": {}}).status_code == 200
    assert client.post(f"/assembly-design/scheme/{scheme_id}/stage/4a",
                       json={"action": "generate", "payload": {}}).status_code == 200

    r4b = client.post(
        f"/assembly-design/scheme/{scheme_id}/stage/4b",
        json={"action": "generate", "payload": {}},
    )
    assert r4b.status_code == 200, r4b.text
    body = r4b.json()
    assert "tools" in body
    assert "dfa_tooling_score" in body

    final = client.get(f"/assembly-design/scheme/{scheme_id}").json()
    assert "stage4b" in final
    assert "4b" in final["meta"]["stages_done"]
