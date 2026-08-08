"""FastMCP wrappers for book knowledge-graph queries."""
import os
import sys
from pathlib import Path

for stream in (sys.stdout, sys.stderr):
    reconfigure = getattr(stream, "reconfigure", None)
    if reconfigure:
        try:
            reconfigure(encoding="utf-8")
        except (ValueError, OSError):
            pass

try:
    from fastmcp import FastMCP
except ImportError:
    FastMCP = None

try:
    from . import query
except ImportError:
    import query

if FastMCP is not None:
    mcp = FastMCP(name="book-kg")

    @mcp.tool
    def trace_path(motif: str, ch_start: int = 1, ch_end: int = 9999) -> list[dict]:
        """Return ordered motif mentions across chapters."""
        return query.trace_path(motif, ch_start, ch_end)

    @mcp.tool
    def motifs_in_chapter(chapter: str) -> list[str]:
        """Return motifs mentioned in a chapter."""
        return query.motifs_in_chapter(chapter)

    @mcp.tool
    def contradicts(line: str) -> list[dict]:
        """Return frozen-line occurrences that conflict with an expected state."""
        return query.contradicts(line)

    @mcp.tool
    def references(chapter: str) -> list[dict]:
        """Return chapter references targeting a chapter."""
        return query.references(chapter)
else:
    mcp = None


if __name__ == "__main__":
    if mcp is None:
        raise SystemExit("FastMCP is required: pip install fastmcp")
    mcp.run()
