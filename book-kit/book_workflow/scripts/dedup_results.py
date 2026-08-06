"""dedup_results.py - URL canonicalization + dedup for multi-source search.

CLI::

    python dedup_results.py results.json
    python dedup_results.py -          # read JSON from stdin

Importable as a library::

    from dedup_results import canonicalize, dedup

Canonicalization rules (verbatim from plan section P9, item 5):

* lowercase scheme + host
* strip ``utm_*`` query parameters (utm_source, utm_medium, utm_campaign,
  utm_term, utm_content, utm_id)
* normalize trailing slash on the path (collapse ``/path/`` -> ``/path``
  and treat bare ``/`` as empty)
* preserve everything else verbatim

Dedup keeps the first occurrence of each canonical URL. Source-tagged
results from the multi-source pipeline (``source: "exa" | "firecrawl" |
"ddg"``) survive the round-trip.

Stdlib-only. No new dependencies.
"""
from __future__ import annotations

import argparse
import io
import json
import re
import sys
from urllib.parse import parse_qsl, urlencode, urlsplit, urlunsplit

# ---------------------------------------------------------------------------
# Force UTF-8 stdio FIRST, before any argparse / print call. (WARN #15+#22)
# ---------------------------------------------------------------------------
for _stream in (sys.stdout, sys.stderr):
    try:
        _stream.reconfigure(encoding="utf-8")
    except (AttributeError, io.UnsupportedOperation):
        pass


# utm_* keys to strip from the query string before canonicalization.
# Other query parameters are preserved verbatim (order-stable by re-encoding).
_STRIP_PARAMS = {
    "utm_source",
    "utm_medium",
    "utm_campaign",
    "utm_term",
    "utm_content",
    "utm_id",
}


def canonicalize(url: str) -> str:
    """Return a canonical form of ``url`` per the P9 spec."""
    if not url:
        return ""
    raw = url.strip()
    parts = urlsplit(raw)
    scheme = (parts.scheme or "http").lower()
    host = (parts.hostname or "").lower()
    netloc = host
    if parts.port:
        netloc = f"{host}:{parts.port}"
    # Path: collapse trailing slash except for the root "/".
    path = parts.path or ""
    if len(path) > 1 and path.endswith("/"):
        path = path.rstrip("/")
    # Query: drop utm_* keys, preserve the rest, stable order.
    filtered = [
        (k, v)
        for k, v in parse_qsl(parts.query, keep_blank_values=True)
        if k.lower() not in _STRIP_PARAMS
    ]
    query = urlencode(filtered)
    fragment = parts.fragment  # fragments are kept verbatim (not specified as stripped)
    return urlunsplit((scheme, netloc, path, query, fragment))


def dedup(results: list[dict]) -> list[dict]:
    """Deduplicate by canonical URL; keep the first occurrence.

    Each result is a ``{"url", "title", "snippet", "source"}`` dict. The
    ``url`` field is rewritten to its canonical form. Non-dict entries are
    passed through unchanged so callers can mix in metadata without losing
    it.
    """
    seen: set[str] = set()
    out: list[dict] = []
    for entry in results:
        if not isinstance(entry, dict) or "url" not in entry:
            out.append(entry)
            continue
        canon = canonicalize(entry.get("url", ""))
        if canon in seen:
            continue
        seen.add(canon)
        # Preserve original key order; only rewrite ``url``.
        new_entry = dict(entry)
        new_entry["url"] = canon
        out.append(new_entry)
    return out


def _load_input(path: str | None) -> list:
    """Read a JSON list from a file path or stdin (``-``).

    Strips a UTF-8 BOM if present so PowerShell-produced input files
    (which emit a BOM by default) parse cleanly.
    """
    if path is None or path == "-":
        data = sys.stdin.read()
    else:
        with open(path, "r", encoding="utf-8-sig") as handle:
            data = handle.read()
    parsed = json.loads(data)
    if not isinstance(parsed, list):
        raise ValueError(f"dedup_results: input must be a JSON list, got {type(parsed).__name__}")
    return parsed


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(
        description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument(
        "path",
        nargs="?",
        default="-",
        help="JSON file with a list of results (default: stdin, use '-' explicitly)",
    )
    args = parser.parse_args(argv)

    try:
        results = _load_input(args.path)
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        print(f"dedup_results: {exc}", file=sys.stderr)
        return 2

    deduped = dedup(results)
    json.dump(deduped, sys.stdout, ensure_ascii=False)
    sys.stdout.write("\n")
    return 0


if __name__ == "__main__":
    sys.exit(main())
