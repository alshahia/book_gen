"""duckduckgo_search.py - thin DuckDuckGo HTML scraper for the research pipeline.

CLI::

    python duckduckgo_search.py "<query>" [--max-results N]

Internally calls DuckDuckGo's no-JS HTML endpoint
(``https://html.duckduckgo.com/html/?q=...``) via ``urllib.request`` and
parses the server-rendered result list with stdlib-only regexes. Returns
a JSON list ``[{"url": ..., "title": ..., "snippet": ...}]`` to stdout.

This is the third-tier fallback in the multi-source research protocol:

    built-in ``websearch`` (Exa)   ->  ``firecrawl`` MCP   ->  DuckDuckGo

The agent invokes this script (or imports ``duckduckgo_search``) when both
primary layers return fewer than three unique URLs. Per P9 spec, the
``parallel_search.py --fallback`` orchestrator calls into this module.

Stdlib-only. No new dependencies.
"""
from __future__ import annotations

import argparse
import io
import json
import re
import sys
import urllib.error
import urllib.parse
import urllib.request

# ---------------------------------------------------------------------------
# Force UTF-8 stdio FIRST, before any argparse / print call. (WARN #15+#22)
# ---------------------------------------------------------------------------
for _stream in (sys.stdout, sys.stderr):
    try:
        _stream.reconfigure(encoding="utf-8")
    except (AttributeError, io.UnsupportedOperation):
        pass


# Default User-Agent. DuckDuckGo HTML returns a captcha for unidentified
# clients; a real-browser UA bypasses the gate for light queries.
_USER_AGENT = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
    "AppleWebKit/537.36 (KHTML, like Gecko) "
    "Chrome/124.0 Safari/537.36"
)
_ENDPOINT = "https://html.duckduckgo.com/html/"

# Result block: <a class="result__a" href="...">TITLE</a> ... snippet
# class="result__snippet". DDG renders result blocks inside <div class="result">
# but the href is sometimes wrapped in ``//duckduckgo.com/l/?uddg=...``.
_LINK = re.compile(
    r'<a[^>]+class="result__a"[^>]+href="(?P<url>[^"]+)"[^>]*>(?P<title>.*?)</a>',
    re.IGNORECASE | re.DOTALL,
)
_SNIPPET = re.compile(
    r'<a[^>]+class="result__snippet"[^>]*>(?P<snippet>.*?)</a>',
    re.IGNORECASE | re.DOTALL,
)
_TAG_STRIP = re.compile(r"<[^>]+>")
_WS = re.compile(r"\s+")


def _clean(html: str) -> str:
    """Strip HTML tags and collapse whitespace for snippet/title text."""
    text = _TAG_STRIP.sub(" ", html)
    return _WS.sub(" ", text).strip()


def _resolve_url(raw: str) -> str:
    """Convert DDG's redirect URLs (``//duckduckgo.com/l/?uddg=...``) to the
    real destination URL when possible. Falls back to the raw value.
    """
    if not raw:
        return ""
    if raw.startswith("//"):
        raw = "https:" + raw
    if "duckduckgo.com/l/?" in raw or "uddg=" in raw:
        parsed = urllib.parse.urlparse(raw)
        qs = urllib.parse.parse_qs(parsed.query)
        target = qs.get("uddg", [None])[0]
        if target:
            return urllib.parse.unquote(target)
    return raw


def duckduckgo_search(query: str, max_results: int = 10) -> list[dict]:
    """Run a single DuckDuckGo HTML search and return the parsed results.

    The function is import-safe (no network side effect at import time). If
    the network call fails (DNS, timeout, non-2xx, etc.) an empty list is
    returned and the error is written to stderr so the caller can log it
    without crashing the parent pipeline.
    """
    if not query or not query.strip():
        return []
    capped = max(1, int(max_results))
    params = urllib.parse.urlencode({"q": query, "kl": "us-en"})
    url = f"{_ENDPOINT}?{params}"
    request = urllib.request.Request(url, headers={"User-Agent": _USER_AGENT})
    try:
        with urllib.request.urlopen(request, timeout=20) as response:
            body = response.read().decode("utf-8", errors="replace")
    except (urllib.error.URLError, urllib.error.HTTPError, TimeoutError, OSError) as exc:
        print(f"duckduckgo_search: network error: {exc}", file=sys.stderr)
        return []

    links = list(_LINK.finditer(body))
    snippets = list(_SNIPPET.finditer(body))
    results: list[dict] = []
    for idx, match in enumerate(links[:capped]):
        url = _resolve_url(match.group("url"))
        title = _clean(match.group("title"))
        snippet = ""
        if idx < len(snippets):
            snippet = _clean(snippets[idx].group("snippet"))
        if not url:
            continue
        results.append({"url": url, "title": title, "snippet": snippet})
    return results


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(
        description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument("query", help="search query string")
    parser.add_argument(
        "--max-results",
        type=int,
        default=10,
        help="maximum number of results to return (default: 10)",
    )
    args = parser.parse_args(argv)

    results = duckduckgo_search(args.query, args.max_results)
    json.dump(results, sys.stdout, ensure_ascii=False)
    sys.stdout.write("\n")
    return 0


if __name__ == "__main__":
    sys.exit(main())
