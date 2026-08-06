"""Tests for dedup_results.py - URL canonicalization + dedup.

Stdlib-only fixtures. The tests target ``canonicalize`` and ``dedup``
directly. Two spec fixtures:

1. ``test_dedup_results_strips_utm`` - the same URL with ``?utm_source=foo``
   and ``?utm_medium=bar`` is dedup'd to a single entry.
2. ``test_dedup_results_normalizes_trailing_slash`` - ``example.com/path``
   and ``example.com/path/`` are dedup'd to a single entry.
"""
import dedup_results as dr


# ---------------------------------------------------------------------------
# 1) utm_* query params are stripped during canonicalization
# ---------------------------------------------------------------------------


def test_dedup_results_strips_utm():
    """Same URL with different utm_* params dedup to one entry."""
    results = [
        {
            "url": "https://example.com/article?utm_source=foo",
            "title": "Article",
            "snippet": "snippet text",
            "source": "exa",
        },
        {
            "url": "https://example.com/article?utm_medium=bar",
            "title": "Article (medium dup)",
            "snippet": "snippet text 2",
            "source": "firecrawl",
        },
        {
            "url": "https://example.com/article",
            "title": "Article (clean)",
            "snippet": "snippet text 3",
            "source": "ddg",
        },
    ]
    deduped = dr.dedup(results)
    assert len(deduped) == 1, f"expected 1 entry, got {len(deduped)}"
    # First occurrence wins; its source is preserved.
    assert deduped[0]["source"] == "exa"
    assert deduped[0]["title"] == "Article"
    # Canonical URL has no utm_* params and lowercased scheme + host.
    assert deduped[0]["url"] == "https://example.com/article"


# ---------------------------------------------------------------------------
# 2) Trailing slash on the path is normalized
# ---------------------------------------------------------------------------


def test_dedup_results_normalizes_trailing_slash():
    """``/path`` and ``/path/`` dedup to one entry."""
    results = [
        {
            "url": "https://example.com/path",
            "title": "Path A",
            "snippet": "snippet A",
            "source": "exa",
        },
        {
            "url": "https://example.com/path/",
            "title": "Path A trailing",
            "snippet": "snippet A trailing",
            "source": "firecrawl",
        },
    ]
    deduped = dr.dedup(results)
    assert len(deduped) == 1, f"expected 1 entry, got {len(deduped)}"
    assert deduped[0]["url"] == "https://example.com/path"
    assert deduped[0]["source"] == "exa"


# ---------------------------------------------------------------------------
# Extra hardening: canonicalize lowercases scheme + host and keeps root /
# ---------------------------------------------------------------------------


def test_canonicalize_lowercases_host_and_scheme():
    """Scheme and host are lowercased; root path stays '/'.

    We preserve the root ``/`` for forward compatibility (some servers
    distinguish ``example.com`` from ``example.com/``); the spec only
    requires normalizing trailing slashes on non-root paths.
    """
    canon = dr.canonicalize("HTTPS://Example.COM/")
    assert canon == "https://example.com/", f"got {canon!r}"


def test_canonicalize_keeps_other_query_params():
    """utm_* stripped, other query params preserved."""
    canon = dr.canonicalize(
        "https://example.com/x?utm_source=foo&id=42&page=2"
    )
    # Order-stable: parse_qsl preserves input order.
    assert "utm_source" not in canon
    assert "id=42" in canon
    assert "page=2" in canon
