"""Tests for backend.tools.web_search.WebSearchClient (Tavily wrapper)."""
from pathlib import Path
from unittest.mock import MagicMock, patch
import pytest

from backend.tools.web_search import WebSearchClient, SearchResult


def test_no_api_key_returns_empty(tmp_path):
    """Without TAVILY_API_KEY, search returns empty list (graceful degradation)."""
    client = WebSearchClient(api_key=None, cache_dir=tmp_path)
    results = client.search("test query")
    assert results == []


@patch("backend.tools.web_search.TavilyClient")
def test_search_returns_parsed_results(mock_tavily_cls, tmp_path):
    mock_client = MagicMock()
    mock_client.search.return_value = {
        "results": [
            {"url": "https://example.com/a", "title": "Title A", "content": "Excerpt A", "score": 0.9},
            {"url": "https://example.com/b", "title": "Title B", "content": "Excerpt B", "score": 0.5},
        ]
    }
    mock_tavily_cls.return_value = mock_client

    client = WebSearchClient(api_key="fake-key", cache_dir=tmp_path)
    results = client.search("aviation engine assembly", max_results=5)

    assert len(results) == 2
    assert isinstance(results[0], SearchResult)
    assert results[0].url == "https://example.com/a"
    assert results[0].title == "Title A"
    assert results[0].confidence == 0.9
    assert results[0].id.startswith("ws-")


@patch("backend.tools.web_search.TavilyClient")
def test_cache_hit_avoids_second_api_call(mock_tavily_cls, tmp_path):
    mock_client = MagicMock()
    mock_client.search.return_value = {
        "results": [{"url": "https://example.com/x", "title": "T", "content": "C", "score": 0.5}]
    }
    mock_tavily_cls.return_value = mock_client
    client = WebSearchClient(api_key="fake", cache_dir=tmp_path)

    client.search("query-cached")  # 1st call hits Tavily
    client.search("query-cached")  # 2nd call hits cache
    client.search("query-cached")  # 3rd call hits cache

    assert mock_client.search.call_count == 1


@patch("backend.tools.web_search.TavilyClient")
def test_search_failure_returns_empty(mock_tavily_cls, tmp_path):
    """If Tavily raises, search degrades to empty list (no crash)."""
    mock_client = MagicMock()
    mock_client.search.side_effect = RuntimeError("network error")
    mock_tavily_cls.return_value = mock_client

    client = WebSearchClient(api_key="fake", cache_dir=tmp_path)
    results = client.search("any")
    assert results == []


@patch("backend.tools.web_search.TavilyClient")
def test_excerpt_truncated_to_500_chars(mock_tavily_cls, tmp_path):
    long_content = "x" * 1000
    mock_client = MagicMock()
    mock_client.search.return_value = {
        "results": [{"url": "https://example.com/y", "title": "T", "content": long_content, "score": 0.7}]
    }
    mock_tavily_cls.return_value = mock_client
    client = WebSearchClient(api_key="fake", cache_dir=tmp_path)
    results = client.search("any")
    assert len(results) == 1
    assert len(results[0].excerpt) == 500
