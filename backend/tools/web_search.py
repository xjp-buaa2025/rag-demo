"""
backend/tools/web_search.py

Thin wrapper around Tavily Search API with on-disk cache and graceful degradation.
Used by the assembly-scheme S1 pipeline (and other stages on demand).

Behavior:
  - No api_key → returns empty results (does not crash)
  - Cache hit → skip API call (cache key = sha256(query)[:16])
  - API exception → log and return empty results
  - Excerpt always truncated to 500 chars
"""

from __future__ import annotations

from dataclasses import dataclass, asdict
from pathlib import Path
from typing import List, Optional
import hashlib
import json
import logging
import os

from tavily import TavilyClient

logger = logging.getLogger(__name__)


@dataclass
class SearchResult:
    id: str
    url: str
    title: str
    excerpt: str
    confidence: float
    raw_score: Optional[float] = None


class WebSearchClient:
    """Tavily wrapper. See module docstring."""

    EXCERPT_MAX_LEN = 500

    def __init__(
        self,
        api_key: Optional[str] = None,
        cache_dir: Optional[Path] = None,
    ):
        self.api_key = api_key if api_key is not None else os.getenv("TAVILY_API_KEY")
        self.cache_dir = Path(cache_dir) if cache_dir else Path("storage/web_cache")
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        self._client: Optional[TavilyClient] = None
        if self.api_key:
            try:
                self._client = TavilyClient(api_key=self.api_key)
            except Exception as e:
                logger.error("Failed to init TavilyClient: %s", e)
                self._client = None

    def _cache_path(self, query: str) -> Path:
        h = hashlib.sha256(query.encode("utf-8")).hexdigest()[:16]
        return self.cache_dir / f"{h}.json"

    def search(self, query: str, max_results: int = 5) -> List[SearchResult]:
        if not self._client:
            logger.warning("Tavily not configured; web_search returns empty for query=%r", query)
            return []

        # Cache check
        cp = self._cache_path(query)
        if cp.exists():
            try:
                cached = json.loads(cp.read_text(encoding="utf-8"))
                return [SearchResult(**r) for r in cached]
            except Exception as e:
                logger.warning("Cache read failed for %s: %s; refetching", cp, e)

        # API call
        try:
            resp = self._client.search(query=query, max_results=max_results)
        except Exception as e:
            logger.error("Tavily search failed for query=%r: %s", query, e)
            return []

        results: List[SearchResult] = []
        for item in resp.get("results", []):
            url = item.get("url", "")
            content = item.get("content", "")
            results.append(
                SearchResult(
                    id=f"ws-{hashlib.sha256(url.encode('utf-8')).hexdigest()[:8]}",
                    url=url,
                    title=item.get("title", ""),
                    excerpt=content[: self.EXCERPT_MAX_LEN],
                    confidence=float(item.get("score", 0.5)),
                    raw_score=item.get("score"),
                )
            )

        # Write cache
        try:
            cp.write_text(
                json.dumps([asdict(r) for r in results], ensure_ascii=False, indent=2),
                encoding="utf-8",
            )
        except Exception as e:
            logger.warning("Cache write failed for %s: %s", cp, e)

        return results
