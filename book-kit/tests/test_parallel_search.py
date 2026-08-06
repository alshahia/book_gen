"""Tests for parallel_search.py - merge Exa + Firecrawl; DuckDuckGo fallback.

Stdlib-only fixtures. The tests target the ``parallel_search()`` pure
function directly by injecting mock ``exa_fn`` / ``firecrawl_fn`` /
``ddg_fn`` callables so we never touch the network or the MCP layer.

Three spec fixtures:

1. ``test_parallel_search_primary_ok``  - both primary layers return 5+
   unique URLs; union has 8+ unique URLs without invoking fallback.
2. ``test_parallel_search_fallback_triggered``  - both primary layers
   return 0; with ``--fallback`` the DDG layer is invoked and the result
   list contains DDG-tagged entries.
3. ``test_parallel_search_no_fallback``  - both primary layers return 0;
   without ``--fallback`` the result is an empty list (no error).
"""
from pathlib import Path

import parallel_search as ps


KIT_ROOT = Path(__file__).resolve().parents[1]
SCRIPT = KIT_ROOT / "book_workflow" / "scripts" / "parallel_search.py"


# ---------------------------------------------------------------------------
# Mock layer factories
# ---------------------------------------------------------------------------


def _exa_factory(items):
    """Return a callable with the ``(query, max_results) -> list[dict]`` shape."""

    def _fn(query, max_results):
        return list(items)

    return _fn


def _exa_factory_5():
    """Five unique Exa URLs with 1 deliberate duplicate so dedup must work."""
    return _exa_factory(
        [
            {"url": "https://exa.example.com/a", "title": "Exa A", "snippet": "A"},
            {"url": "https://exa.example.com/b", "title": "Exa B", "snippet": "B"},
            {"url": "https://exa.example.com/c", "title": "Exa C", "snippet": "C"},
            {"url": "https://exa.example.com/d", "title": "Exa D", "snippet": "D"},
            {"url": "https://exa.example.com/e", "title": "Exa E", "snippet": "E"},
            {"url": "https://exa.example.com/a", "title": "Exa A dup", "snippet": "A"},
        ]
    )


def _firecrawl_factory_5():
    """Five Firecrawl URLs that share one URL with Exa to force dedup."""
    return _exa_factory(
        [
            {"url": "https://fc.example.com/a", "title": "FC A", "snippet": "a"},
            {"url": "https://fc.example.com/b", "title": "FC B", "snippet": "b"},
            {"url": "https://fc.example.com/c", "title": "FC C", "snippet": "c"},
            {"url": "https://fc.example.com/d", "title": "FC D", "snippet": "d"},
            {"url": "https://fc.example.com/e", "title": "FC E", "snippet": "e"},
            {"url": "https://exa.example.com/b", "title": "Exa B dup", "snippet": "B"},
        ]
    )


def _ddg_factory_3():
    """Three DDG fallback URLs to satisfy the >=3 threshold."""
    return _exa_factory(
        [
            {"url": "https://ddg.example.com/x", "title": "DDG X", "snippet": "x"},
            {"url": "https://ddg.example.com/y", "title": "DDG Y", "snippet": "y"},
            {"url": "https://ddg.example.com/z", "title": "DDG Z", "snippet": "z"},
        ]
    )


def _silent_ddg():
    """Return a DDG callable that asserts it was never invoked."""

    def _fn(query, max_results):
        raise AssertionError("DDG fallback should not have been invoked")

    return _fn


# ---------------------------------------------------------------------------
# 1) Primary layers sufficient - no fallback
# ---------------------------------------------------------------------------


def test_parallel_search_primary_ok(tmp_path):
    """Both layers return 5+ results; union has 8+ unique URLs, no fallback."""
    trail = tmp_path / "trail.md"
    results = ps.parallel_search(
        "python testing",
        max_results=10,
        fallback=True,
        exa_fn=_exa_factory_5(),
        firecrawl_fn=_firecrawl_factory_5(),
        ddg_fn=_silent_ddg(),
        trail_path=trail,
    )
    urls = [entry["url"] for entry in results]
    unique = set(urls)
    assert len(unique) >= 8, f"expected 8+ unique URLs, got {len(unique)}: {unique}"
    # No DDG layer entries because the threshold was met by the union.
    sources = {entry.get("source") for entry in results}
    assert "ddg" not in sources, f"DDG layer should not fire, got sources={sources}"
    # Each non-empty entry carries its source tag.
    for entry in results:
        assert entry.get("source") in {"exa", "firecrawl"}, entry
    # Trail contains one line per primary layer (no DDG line).
    trail_text = trail.read_text(encoding="utf-8")
    assert "layer=exa" in trail_text
    assert "layer=firecrawl" in trail_text
    assert "layer=ddg" not in trail_text


# ---------------------------------------------------------------------------
# 2) Both primary layers empty + --fallback -> DDG invoked
# ---------------------------------------------------------------------------


def test_parallel_search_fallback_triggered(tmp_path):
    """Both primary layers return 0; --fallback invokes DuckDuckGo."""
    trail = tmp_path / "trail.md"
    empty = _exa_factory([])
    invoked = {"ddg": 0}

    def ddg(query, max_results):
        invoked["ddg"] += 1
        return _ddg_factory_3()(query, max_results)

    results = ps.parallel_search(
        "obscure query",
        max_results=10,
        fallback=True,
        exa_fn=empty,
        firecrawl_fn=empty,
        ddg_fn=ddg,
        trail_path=trail,
    )
    assert invoked["ddg"] == 1, "DDG layer should be invoked exactly once"
    ddg_entries = [entry for entry in results if entry.get("source") == "ddg"]
    assert len(ddg_entries) == 3, f"expected 3 DDG entries, got {len(ddg_entries)}"
    urls = {entry["url"] for entry in ddg_entries}
    assert urls == {
        "https://ddg.example.com/x",
        "https://ddg.example.com/y",
        "https://ddg.example.com/z",
    }
    trail_text = trail.read_text(encoding="utf-8")
    assert "layer=ddg" in trail_text


# ---------------------------------------------------------------------------
# 3) Both primary layers empty + NO --fallback -> empty list, no error
# ---------------------------------------------------------------------------


def test_parallel_search_no_fallback(tmp_path):
    """Both layers return 0; without --fallback the result is empty (no error)."""
    trail = tmp_path / "trail.md"
    empty = _exa_factory([])
    results = ps.parallel_search(
        "obscure query",
        max_results=10,
        fallback=False,
        exa_fn=empty,
        firecrawl_fn=empty,
        ddg_fn=_silent_ddg(),
        trail_path=trail,
    )
    assert results == [], f"expected empty list, got {results!r}"
    trail_text = trail.read_text(encoding="utf-8")
    assert "layer=exa" in trail_text
    assert "layer=firecrawl" in trail_text
    assert "layer=ddg" not in trail_text
