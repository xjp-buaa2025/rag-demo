"""Shared fixtures for assembly-scheme router tests."""
from pathlib import Path
from unittest.mock import MagicMock
import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from backend.state import AppState
from backend.pipelines.assembly_scheme.skill_loader import SkillRegistry
from backend.tools.web_search import WebSearchClient
from backend.routers.assembly_design import router as assembly_router

SKILL_ROOT = Path(__file__).resolve().parents[2] / "skills" / "aero-engine-assembly-scheme"


@pytest.fixture
def app_with_assembly_router(tmp_path, monkeypatch):
    """A FastAPI app with assembly_design router and a minimal AppState mock."""
    # Redirect storage dir to tmp so tests don't pollute real storage/
    monkeypatch.setattr(
        "backend.routers.assembly_design.SCHEMES_DIR",
        tmp_path / "assembly_schemes",
    )
    (tmp_path / "assembly_schemes").mkdir()

    skill = SkillRegistry(SKILL_ROOT)
    skill.load()

    state = AppState(
        qdrant_client=MagicMock(),
        embedding_mgr=MagicMock(),
        llm_client=None,           # task_card returns placeholder
        active_model_label="test",
        skill_registry=skill,
        web_search_client=WebSearchClient(api_key=None, cache_dir=tmp_path / "web_cache"),
    )

    app = FastAPI()
    app.state.app_state = state
    app.include_router(assembly_router)
    return app


@pytest.fixture
def client(app_with_assembly_router):
    return TestClient(app_with_assembly_router)
