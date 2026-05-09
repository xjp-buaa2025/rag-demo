"""Verify all 8 stage schemas are valid JSON Schema documents and stage1 validates a sample."""
from pathlib import Path
import json
import pytest
import jsonschema

SCHEMA_DIR = Path(__file__).resolve().parents[2] / "skills" / "aero-engine-assembly-scheme" / "templates" / "schemas"

ALL_SCHEMAS = [
    "stage1.schema.json", "stage2.schema.json", "stage3.schema.json",
    "stage4a.schema.json", "stage4b.schema.json", "stage4c.schema.json",
    "stage4d.schema.json", "stage5.schema.json",
]


@pytest.mark.parametrize("name", ALL_SCHEMAS)
def test_schema_is_valid_jsonschema(name):
    path = SCHEMA_DIR / name
    assert path.exists(), f"{name} missing"
    schema = json.loads(path.read_text(encoding="utf-8"))
    jsonschema.Draft202012Validator.check_schema(schema)


def test_stage1_schema_validates_sample():
    schema = json.loads((SCHEMA_DIR / "stage1.schema.json").read_text(encoding="utf-8"))
    sample = {
        "scheme_id": "scheme-20260508-a1b2c3",
        "subject": {
            "system": "PT6A 高压压气机",
            "system_en": "PT6A HPC",
            "scope": ["3 级轴流 + 1 级离心"],
            "design_intent": "工艺优化",
            "constraints": {"primary": "可靠性"},
        },
        "kg_snapshot": {"part_count": 35, "assembly_count": 13},
        "web_search_results": [],
        "compliance_scope": ["AS9100D §8.1"],
        "task_card_md": "## 任务说明书\nPT6A HPC ...",
    }
    jsonschema.validate(instance=sample, schema=schema)


def test_stage4c_schema_accepts_skipped():
    schema = json.loads((SCHEMA_DIR / "stage4c.schema.json").read_text(encoding="utf-8"))
    skipped = {"skipped": True, "skip_reason": "v1 GD&T data not available", "stack_ups": []}
    jsonschema.validate(instance=skipped, schema=schema)


def test_stage4d_schema_accepts_skipped():
    schema = json.loads((SCHEMA_DIR / "stage4d.schema.json").read_text(encoding="utf-8"))
    skipped = {"skipped": True, "skip_reason": "v1 key parts data not available"}
    jsonschema.validate(instance=skipped, schema=schema)


def test_pt6a_hpc_stage1_golden_validates():
    """The PT6A HPC golden example must validate against stage1 schema."""
    schema = json.loads((SCHEMA_DIR / "stage1.schema.json").read_text(encoding="utf-8"))
    golden_path = SCHEMA_DIR.parent / "golden" / "pt6a_hpc_stage1.json"
    assert golden_path.exists(), f"golden file missing: {golden_path}"
    instance = json.loads(golden_path.read_text(encoding="utf-8"))
    jsonschema.validate(instance=instance, schema=schema)
