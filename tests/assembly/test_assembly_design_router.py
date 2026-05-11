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
        "subject_system": "Test", "design_intent": "工艺优化",
    }).json()
    sid = create["scheme_id"]
    for stage_key in ["2", "3", "4a", "4b", "4c", "4d", "5"]:
        resp = client.post(
            f"/assembly-design/scheme/{sid}/stage/{stage_key}",
            json={"action": "generate"},
        )
        assert resp.status_code == 501, f"stage {stage_key} should be 501, got {resp.status_code}"


def test_save_edits_overwrites_stage1(client):
    create = client.post("/assembly-design/scheme/new", json={
        "subject_system": "PT6A HPC", "design_intent": "工艺优化",
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
        "subject_system": "Test", "design_intent": "工艺优化",
    }).json()
    sid = create["scheme_id"]
    resp = client.post(
        f"/assembly-design/scheme/{sid}/stage/1",
        json={"action": "unknown"},
    )
    assert resp.status_code == 400


def test_reflux_endpoint_returns_501_for_v1(client):
    create = client.post("/assembly-design/scheme/new", json={
        "subject_system": "Test", "design_intent": "工艺优化",
    }).json()
    sid = create["scheme_id"]
    resp = client.post(f"/assembly-design/scheme/{sid}/reflux", json={"approved": []})
    assert resp.status_code == 501


def test_iterate_endpoint_returns_501_for_v1(client):
    create = client.post("/assembly-design/scheme/new", json={
        "subject_system": "Test", "design_intent": "工艺优化",
    }).json()
    sid = create["scheme_id"]
    resp = client.post(f"/assembly-design/scheme/{sid}/iterate", json={"target_stage_key": "4a"})
    assert resp.status_code == 501


def test_export_endpoint_returns_501_for_v1(client):
    create = client.post("/assembly-design/scheme/new", json={
        "subject_system": "Test", "design_intent": "工艺优化",
    }).json()
    sid = create["scheme_id"]
    resp = client.get(f"/assembly-design/scheme/{sid}/export")
    assert resp.status_code == 501
