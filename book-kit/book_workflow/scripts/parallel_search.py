"""parallel_search.py - merge Exa + Firecrawl results; optional DuckDuckGo fallback.

CLI::

    python parallel_search.py "<query>" [--max-results N] [--fallback]
        [--exa-results <path>] [--firecrawl-results <path>]
        [--task <task-id>]

Stdlib-only. No new dependencies.

The script is a thin orchestrator on top of ``dedup_results``. The agent
calls the Exa + Firecrawl MCP layers first (they require OAuth tokens and
LLM-side tool invocations), writes each layer's JSON list to a temp file,
then passes the file paths to this CLI. The CLI:

1. Loads each layer's results (or treats a missing path as an empty list).
2. Tags every entry with ``source: "exa"`` or ``source: "firecrawl"``.
3. Deduplicates by canonical URL (``dedup_results.canonicalize``).
4. If ``--fallback`` is set and the union has fewer than 3 unique URLs,
   invokes ``duckduckgo_search.py`` (a stdlib subprocess) and appends
   ``source: "ddg"`` entries.
5. Appends one ``layer=exa|firecrawl|ddg results=N`` line per layer to
   ``share/notes/01_research_<task>_search-trail.md`` (creating the file
   if needed).

In tests the script is invoked through the ``parallel_search()`` pure
function which takes ``exa_fn``, ``firecrawl_fn``, ``ddg_fn`` callables
directly so we can mock network without touching the network.

Exit codes: 0 = success, 2 = input error (bad JSON in the file args).
"""
from __future__ import annotations

import argparse
import io
import json
import os
import subprocess
import sys
from pathlib import Path

# ---------------------------------------------------------------------------
# Force UTF-8 stdio FIRST, before any argparse / print call. (WARN #15+#22)
# ---------------------------------------------------------------------------
for _stream in (sys.stdout, sys.stderr):
    try:
        _stream.reconfigure(encoding="utf-8")
    except (AttributeError, io.UnsupportedOperation):
        pass


# Reuse the canonicalize + dedup helpers. The ``import`` below is
# intentional: parallel_search lives next to dedup_results in the same
# scripts/ directory, so the relative import is reliable. When loaded as a
# module from the book-kit/tests/ conftest path-prepend, ``dedup_results``
# is importable as a top-level name.
import dedup_results


SCRIPT_DIR = Path(__file__).resolve().parent
DDG_SCRIPT = SCRIPT_DIR / "duckduckgo_search.py"

UNIQUE_THRESHOLD = 3


def _load_layer(path: str | None) -> list[dict]:
    """Read a JSON list from ``path``; return ``[]`` for None or missing file.

    Strips a UTF-8 BOM if present (PowerShell's ``Out-File -Encoding utf8``
    emits one and would otherwise cause ``json.JSONDecodeError``).
    """
    if not path:
        return []
    p = Path(path)
    if not p.exists():
        return []
    try:
        text = p.read_text(encoding="utf-8-sig")
    except (OSError, json.JSONDecodeError):
        return []
    try:
        data = json.loads(text)
    except json.JSONDecodeError:
        return []
    if not isinstance(data, list):
        return []
    return [entry for entry in data if isinstance(entry, dict)]


def _tag(results: list[dict], source: str) -> list[dict]:
    """Rewrite each entry's ``source`` field to the given layer name."""
    out: list[dict] = []
    for entry in results:
        copy = dict(entry)
        copy["source"] = source
        out.append(copy)
    return out


def _invoke_ddg(query: str, max_results: int) -> list[dict]:
    """Call ``duckduckgo_search.py`` as a subprocess; return its JSON list.

    Falls back to an empty list on any failure so the parent pipeline
    continues. The error is surfaced on stderr for log auditing.
    """
    if not DDG_SCRIPT.exists():
        print(f"parallel_search: ddg script missing: {DDG_SCRIPT}", file=sys.stderr)
        return []
    try:
        proc = subprocess.run(
            [sys.executable, str(DDG_SCRIPT), query, "--max-results", str(max_results)],
            capture_output=True,
            text=True,
            timeout=30,
            check=False,
        )
    except (OSError, subprocess.SubprocessError) as exc:
        print(f"parallel_search: ddg subprocess failed: {exc}", file=sys.stderr)
        return []
    if proc.returncode != 0:
        print(
            f"parallel_search: ddg exited {proc.returncode}: {proc.stderr.strip()}",
            file=sys.stderr,
        )
        return []
    try:
        data = json.loads(proc.stdout)
    except json.JSONDecodeError as exc:
        print(f"parallel_search: ddg returned bad JSON: {exc}", file=sys.stderr)
        return []
    if not isinstance(data, list):
        return []
    return [entry for entry in data if isinstance(entry, dict)]


def _append_trail(trail_path: Path, line: str) -> None:
    """Append one line to ``trail_path``; create parent dirs as needed.

    Silently swallows errors so a permission glitch in the notes dir does
    not break the search. The CLI prints a stderr notice on failure.
    """
    try:
        trail_path.parent.mkdir(parents=True, exist_ok=True)
        with trail_path.open("a", encoding="utf-8") as handle:
            handle.write(line.rstrip("\n") + "\n")
    except OSError as exc:
        print(f"parallel_search: cannot write trail: {exc}", file=sys.stderr)


def parallel_search(
    query: str,
    max_results: int = 10,
    fallback: bool = False,
    *,
    exa_fn=None,
    firecrawl_fn=None,
    ddg_fn=None,
    trail_path: Path | None = None,
) -> list[dict]:
    """Pure orchestrator. Returns the merged + deduped list of results.

    ``exa_fn`` / ``firecrawl_fn`` / ``ddg_fn`` are zero-arg-or-callable
    adapters that take ``(query, max_results)`` and return a list of
    ``{"url", "title", "snippet"}`` dicts. Defaulting to empty-list
    callables keeps the function testable without any network or MCP.
    ``trail_path`` defaults to
    ``share/notes/01_research_<task>_search-trail.md`` when omitted.
    """
    exa_raw = (exa_fn or _empty_results)(query, max_results)
    firecrawl_raw = (firecrawl_fn or _empty_results)(query, max_results)
    exa_tagged = _tag(exa_raw, "exa")
    firecrawl_tagged = _tag(firecrawl_raw, "firecrawl")
    merged = exa_tagged + firecrawl_tagged
    deduped = dedup_results.dedup(merged)

    # Trail: log primary layers first.
    if trail_path is None:
        trail_path = Path("share/notes/01_research_search-trail.md")
    _append_trail(
        trail_path,
        f"layer=exa results={len(exa_raw)} query={json.dumps(query)}",
    )
    _append_trail(
        trail_path,
        f"layer=firecrawl results={len(firecrawl_raw)} query={json.dumps(query)}",
    )

    unique_count = len({entry["url"] for entry in deduped if entry.get("url")})
    if fallback and unique_count < UNIQUE_THRESHOLD:
        ddg_raw = (ddg_fn or _invoke_ddg_for_layer)(query, max_results)
        ddg_tagged = _tag(ddg_raw, "ddg")
        deduped = dedup_results.dedup(deduped + ddg_tagged)
        _append_trail(
            trail_path,
            f"layer=ddg results={len(ddg_raw)} query={json.dumps(query)}",
        )

    return deduped


def _empty_results(query: str, max_results: int) -> list[dict]:
    """Default no-op layer: returns an empty list."""
    return []


def _invoke_ddg_for_layer(query: str, max_results: int) -> list[dict]:
    """Layer-style adapter around the DDG subprocess."""
    return _invoke_ddg(query, max_results)


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
        help="maximum results per layer (default: 10)",
    )
    parser.add_argument(
        "--fallback",
        action="store_true",
        help="if primary union < 3 unique URLs, invoke DuckDuckGo fallback",
    )
    parser.add_argument(
        "--exa-results",
        type=str,
        default=None,
        help="path to a JSON file containing Exa results (default: empty)",
    )
    parser.add_argument(
        "--firecrawl-results",
        type=str,
        default=None,
        help="path to a JSON file containing Firecrawl results (default: empty)",
    )
    parser.add_argument(
        "--task",
        type=str,
        default="search",
        help="task id used to name the search-trail file (default: 'search')",
    )
    args = parser.parse_args(argv)

    exa_raw = _load_layer(args.exa_results)
    firecrawl_raw = _load_layer(args.firecrawl_results)
    exa_tagged = _tag(exa_raw, "exa")
    firecrawl_tagged = _tag(firecrawl_raw, "firecrawl")
    merged = exa_tagged + firecrawl_tagged
    deduped = dedup_results.dedup(merged)

    trail_path = Path(f"share/notes/01_research_{args.task}_search-trail.md")
    _append_trail(
        trail_path,
        f"layer=exa results={len(exa_raw)} query={json.dumps(args.query)}",
    )
    _append_trail(
        trail_path,
        f"layer=firecrawl results={len(firecrawl_raw)} query={json.dumps(args.query)}",
    )

    unique_count = len({entry["url"] for entry in deduped if entry.get("url")})
    if args.fallback and unique_count < UNIQUE_THRESHOLD:
        ddg_raw = _invoke_ddg(args.query, args.max_results)
        ddg_tagged = _tag(ddg_raw, "ddg")
        deduped = dedup_results.dedup(deduped + ddg_tagged)
        _append_trail(
            trail_path,
            f"layer=ddg results={len(ddg_raw)} query={json.dumps(args.query)}",
        )

    json.dump(deduped, sys.stdout, ensure_ascii=False)
    sys.stdout.write("\n")
    return 0


if __name__ == "__main__":
    sys.exit(main())
