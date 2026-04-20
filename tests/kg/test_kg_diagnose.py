import asyncio, pytest
from unittest.mock import AsyncMock, patch, MagicMock
from backend.pipelines.kg_diagnose import diagnose_issues_stream
from backend.kg_storage import StageIssue, StageReport, StageStats

SAMPLE_REPORT = StageReport(
    stage="bom",
    generated_at="2026-04-20T00:00:00Z",
    stats=StageStats(
        entities_count=10, triples_count=5,
        relation_breakdown={}, confidence_histogram=[0,0,0.2,0.6,0.2],
        bom_coverage_ratio=None, isolated_entities_count=0, low_confidence_count=2,
    ),
    issues=[
        StageIssue(
            severity="warning",
            title="Low confidence triples",
            title_zh="低置信度三元组",
            description="2 triples < 0.5",
            suggestion="",
        )
    ],
)

@pytest.mark.asyncio
async def test_diagnose_yields_chunks():
    async def fake_stream(*args, **kwargs):
        for chunk in ["建议", "检查", "Prompt"]:
            mock = MagicMock()
            mock.choices[0].delta.content = chunk
            yield mock

    with patch("backend.pipelines.kg_diagnose._create_llm_client") as mock_client:
        instance = MagicMock()
        instance.chat.completions.create = MagicMock(return_value=fake_stream())
        mock_client.return_value = instance

        frames = []
        async for frame in diagnose_issues_stream(SAMPLE_REPORT):
            frames.append(frame)

    types = [f["type"] for f in frames]
    assert "diagnosis_chunk" in types
    assert frames[-1]["type"] == "diagnosis_done"
