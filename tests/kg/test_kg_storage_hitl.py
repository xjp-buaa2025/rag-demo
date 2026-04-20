import json, os, pytest
from backend.kg_storage import (
    write_stage_state, read_stage_state,
    write_stage_report, read_stage_report,
    write_translations, read_translations,
    STAGE_STATE_FILES, STAGE_REPORT_FILES, TRANSLATIONS_FILE,
    StageState, StageReport, StageStats, StageIssue, StageDiff,
)

def test_stage_state_roundtrip(tmp_path, monkeypatch):
    monkeypatch.setattr("backend.kg_storage.STORAGE_DIR", str(tmp_path))
    import backend.kg_storage as ks
    ks.STAGE_STATE_FILES = {s: str(tmp_path / f"stage_{s}_state.json") for s in ["bom","manual"]}

    state = StageState(stage="bom", status="awaiting_review")
    write_stage_state("bom", state)
    loaded = read_stage_state("bom")
    assert loaded is not None
    assert loaded.status == "awaiting_review"

def test_stage_report_roundtrip(tmp_path, monkeypatch):
    import backend.kg_storage as ks
    ks.STAGE_REPORT_FILES = {s: str(tmp_path / f"stage_{s}_report.json") for s in ["bom","manual"]}

    report = StageReport(
        stage="bom",
        generated_at="2026-04-20T00:00:00Z",
        stats=StageStats(
            entities_count=150, triples_count=287,
            relation_breakdown={"isPartOf": 200, "matesWith": 87},
            confidence_histogram=[0.1, 0.2, 0.4, 0.2, 0.1],
            bom_coverage_ratio=None,
            isolated_entities_count=5,
            low_confidence_count=12,
        ),
        issues=[],
        diff=None,
    )
    write_stage_report("bom", report)
    loaded = read_stage_report("bom")
    assert loaded is not None
    assert loaded.stats.entities_count == 150

def test_translations_roundtrip(tmp_path, monkeypatch):
    import backend.kg_storage as ks
    ks.TRANSLATIONS_FILE = str(tmp_path / "translations.json")

    write_translations({"COMPRESSOR ROTOR": "压气机转子", "isPartOf": "属于"})
    loaded = read_translations()
    assert loaded["COMPRESSOR ROTOR"] == "压气机转子"
