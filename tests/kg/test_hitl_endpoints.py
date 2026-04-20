import json, pytest
from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock

from backend.main import app

client = TestClient(app)

def _write_bom_fixture(tmp_path):
    import backend.kg_storage as ks
    data = {
        "entities": [{"id": "P1", "name": "ROTOR", "type": "Assembly"}],
        "triples": [{"head": "BOLT", "relation": "isPartOf", "tail": "ROTOR",
                     "confidence": 1.0, "source": "BOM", "head_type": "Part", "tail_type": "Assembly"}],
        "stats": {"entities_count": 1, "triples_count": 1},
        "generated_at": "2026-04-20T00:00:00Z",
    }
    ks.write_stage("bom", data)
    return data

def test_get_report_returns_200(tmp_path, monkeypatch):
    import backend.kg_storage as ks
    monkeypatch.setattr(ks, "STORAGE_DIR", str(tmp_path))
    ks.STAGE_FILES = {s: str(tmp_path / f"stage_{s}_triples.json") for s in ["bom","manual","cad"]}
    ks.STAGE_REPORT_FILES = {s: str(tmp_path / f"stage_{s}_report.json") for s in ["bom","manual"]}
    _write_bom_fixture(tmp_path)

    resp = client.get("/kg/stage1/report")
    assert resp.status_code == 200
    body = resp.json()
    assert "stats" in body
    assert "issues" in body

def test_approve_sets_state(tmp_path, monkeypatch):
    import backend.kg_storage as ks
    monkeypatch.setattr(ks, "STORAGE_DIR", str(tmp_path))
    ks.STAGE_STATE_FILES = {s: str(tmp_path / f"stage_{s}_state.json") for s in ["bom","manual"]}
    ks.STAGE_FILES = {s: str(tmp_path / f"stage_{s}_triples.json") for s in ["bom","manual","cad"]}
    _write_bom_fixture(tmp_path)

    resp = client.post("/kg/stage1/approve")
    assert resp.status_code == 200
    state = ks.read_stage_state("bom")
    assert state is not None
    assert state.status == "approved"

def test_patch_triple_modifies_json(tmp_path, monkeypatch):
    import backend.kg_storage as ks
    monkeypatch.setattr(ks, "STORAGE_DIR", str(tmp_path))
    ks.STAGE_FILES = {s: str(tmp_path / f"stage_{s}_triples.json") for s in ["bom","manual","cad"]}
    _write_bom_fixture(tmp_path)

    resp = client.patch("/kg/stage1/triples/0", json={
        "head": "BOLT_UPDATED", "relation": "isPartOf", "tail": "ROTOR", "confidence": 1.0
    })
    assert resp.status_code == 200
    updated = ks.read_stage("bom")
    assert updated["triples"][0]["head"] == "BOLT_UPDATED"

def test_post_triple_appends(tmp_path, monkeypatch):
    import backend.kg_storage as ks
    monkeypatch.setattr(ks, "STORAGE_DIR", str(tmp_path))
    ks.STAGE_FILES = {s: str(tmp_path / f"stage_{s}_triples.json") for s in ["bom","manual","cad"]}
    _write_bom_fixture(tmp_path)

    resp = client.post("/kg/stage1/triples", json={
        "head": "SEAL", "relation": "isPartOf", "tail": "ROTOR",
        "confidence": 1.0, "source": "expert", "head_type": "Part", "tail_type": "Assembly"
    })
    assert resp.status_code == 200
    updated = ks.read_stage("bom")
    assert len(updated["triples"]) == 2
