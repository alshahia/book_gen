"""Build a deterministic markdown index of phase reports.

CLI::

    python index_reports.py [--regen] [--reports-dir <path>]

Without ``--regen``, the generated INDEX.md content is printed to stdout.
With ``--regen``, it is written to ``<reports-dir>/INDEX.md``.

Only top-level files named ``0X_*.md`` for phases 00 through 08 are indexed.
Reports are grouped by phase and sorted by date descending within each phase.

Stdlib-only. No new dependencies.
"""
from __future__ import annotations

import argparse
import io
import re
import sys
from itertools import islice
from pathlib import Path


def _force_utf8_stdio():
    """Keep argparse help and rendered markdown portable on Windows."""
    for stream in (sys.stdout, sys.stderr):
        try:
            stream.reconfigure(encoding="utf-8")
        except (AttributeError, io.UnsupportedOperation):
            pass


_force_utf8_stdio()

_NO_VALUE = "\N{EM DASH}"
_REPORT_NAME = re.compile(
    r"^(?P<phase>0[0-8])_(?P<label>[^_]+?)(?:_.*)?\.md$",
    re.IGNORECASE,
)
_DATE = re.compile(r"\b\d{4}-\d{2}-\d{2}\b")
_VERDICT_FENCE = re.compile(
    r"^[ \t]*```[ \t]*verdict\b[^\r\n]*\r?\n"
    r"(?P<body>.*?)(?=^[ \t]*```[ \t]*$|\Z)",
    re.IGNORECASE | re.MULTILINE | re.DOTALL,
)
_VERDICT_TOKEN = re.compile(
    r"(?<![A-Z0-9_])"
    r"(?:PASS|FAIL|APPROVED|FIX-LOOP|REJECTED|READY_FOR_REVIEW)"
    r"(?![A-Z0-9_])",
    re.IGNORECASE,
)
_VERDICT_LINE = re.compile(r"\bVerdict\s*:\s*(?P<value>.*)$", re.IGNORECASE)
_AUTO_ACCEPTED = re.compile(r"\[auto-accepted\s+triageable\]", re.IGNORECASE)


def _read_head(path: Path, limit: int = 200) -> list[str]:
    """Read at most ``limit`` lines, replacing malformed UTF-8 bytes."""
    try:
        with path.open("r", encoding="utf-8", errors="replace") as handle:
            return list(islice(handle, limit))
    except OSError:
        return []


def _next_token(text: str) -> str | None:
    """Return the next markdown-cell token in normalized uppercase form."""
    match = re.search(r"[A-Za-z][A-Za-z0-9_-]*", text)
    return match.group(0).upper() if match else None


def _table_cells(line: str) -> list[str] | None:
    """Split a markdown table row, or return None for non-table text."""
    stripped = line.strip()
    if "|" not in stripped:
        return None
    return [cell.strip() for cell in stripped.strip("|").split("|")]


def _status_from_table(lines: list[str]) -> str | None:
    """Return the first data value under the first Status table column."""
    for index, line in enumerate(lines):
        header = _table_cells(line)
        if header is None:
            continue
        status_indexes = [
            cell_index
            for cell_index, cell in enumerate(header)
            if cell.strip("`*_ ").casefold() == "status"
        ]
        if not status_indexes:
            continue
        status_index = status_indexes[0]
        for candidate_line in lines[index + 1:]:
            if not candidate_line.strip():
                continue
            cells = _table_cells(candidate_line)
            if cells is None:
                break
            if all(re.fullmatch(r":?-{3,}:?", cell) for cell in cells):
                continue
            if status_index < len(cells):
                return _next_token(cells[status_index])
            break
        return None
    return None


def parse_status(lines: list[str]) -> str:
    """Parse report status using the plan's first-match priority order."""
    text = "".join(lines[:200])

    for fence in _VERDICT_FENCE.finditer(text):
        token = _VERDICT_TOKEN.search(fence.group("body"))
        if token:
            return token.group(0).upper()

    if _AUTO_ACCEPTED.search(text):
        return "PASS_WITH_WARN"

    for line in lines[:200]:
        verdict = _VERDICT_LINE.search(line)
        if verdict:
            token = _next_token(verdict.group("value"))
            if token:
                return token

    return _status_from_table(lines[:200]) or _NO_VALUE


def parse_date(path: Path, lines: list[str]) -> str:
    """Return the first filename date, then first date in the first 30 lines."""
    match = _DATE.search(path.name)
    if match:
        return match.group(0)
    match = _DATE.search("".join(lines[:30]))
    return match.group(0) if match else _NO_VALUE


def _scan_reports(reports_dir: Path) -> dict[str, list[tuple[str, str, str, str]]]:
    """Return report rows grouped by two-digit phase prefix."""
    grouped: dict[str, list[tuple[str, str, str, str]]] = {}
    try:
        paths = list(reports_dir.iterdir())
    except OSError:
        return grouped

    for path in paths:
        if not path.is_file():
            continue
        match = _REPORT_NAME.fullmatch(path.name)
        if not match:
            continue
        lines = _read_head(path)
        phase = match.group("phase")
        phase_label = f"{phase} {match.group('label')}"
        grouped.setdefault(phase, []).append(
            (phase_label, path.name, parse_date(path, lines), parse_status(lines))
        )
    return grouped


def _date_sort_key(row: tuple[str, str, str, str]) -> tuple[bool, int, str]:
    date = row[2]
    date_number = int(date.replace("-", "")) if date != _NO_VALUE else 0
    return (date == _NO_VALUE, -date_number, row[1].casefold())


def render_index(reports_dir: Path) -> str:
    """Render byte-stable INDEX.md content for ``reports_dir``."""
    lines = [
        "| Phase | File | Date | Status |",
        "|---|---|---|---|",
    ]
    grouped = _scan_reports(Path(reports_dir))
    if not grouped:
        lines.append("No reports found")
        return "\n".join(lines) + "\n"

    for phase in sorted(grouped):
        for phase_label, filename, date, status in sorted(
            grouped[phase], key=_date_sort_key
        ):
            lines.append(f"| {phase_label} | {filename} | {date} | {status} |")
    return "\n".join(lines) + "\n"


def main(argv=None):
    parser = argparse.ArgumentParser(
        description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument(
        "--regen",
        action="store_true",
        help="write INDEX.md under --reports-dir instead of printing it",
    )
    parser.add_argument(
        "--reports-dir",
        type=Path,
        default=Path("share/reports"),
        help="reports directory to scan (default: share/reports)",
    )
    args = parser.parse_args(argv)

    reports_dir = args.reports_dir.resolve()
    content = render_index(reports_dir)
    if not args.regen:
        sys.stdout.write(content)
        return 0

    out_path = (reports_dir / "INDEX.md").resolve()
    if out_path.parent != reports_dir:
        print(
            f"index_reports: INDEX.md must be under reports dir: {reports_dir}",
            file=sys.stderr,
        )
        return 2
    try:
        reports_dir.mkdir(parents=True, exist_ok=True)
        out_path.write_text(content, encoding="utf-8")
    except OSError as exc:
        print(f"index_reports: cannot write {out_path}: {exc}", file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    sys.exit(main())
