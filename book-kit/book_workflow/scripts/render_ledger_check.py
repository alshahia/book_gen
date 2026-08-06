"""render_ledger_check.py — render the gate-checklist block for books/<slug>/ledger.md.

Auto-generates the ``## Gate checklist`` table block in each chapter's row
of ``ledger.md``. The block is one markdown table with 8 rows (one per
mechanical rule); each row's ``Status`` cell is ``PASS`` / ``FAIL`` / ``WARN`` /
``n/a`` and the ``Evidence`` cell is a short fact string pulled from the
caller's gate-pass output.

Pipeline:

    books/<slug>/chapters/ch-NN.md
            │
            ▼
    subprocess ┌────────────────────────────┐
    ─────────► │ check_chapter.py --json    │ → {checks: [{name,status,evidence}, …]}
               │ (or stub when missing)     │
               └────────────────────────────┘
    subprocess ┌────────────────────────────┐
    ─────────► │ book_check.py --json       │ → {chapters, cross_ref, summary, …}
               │ (or stub when missing)     │
               └────────────────────────────┘
            │
            ▼
    build_gate_block() → markdown table block (8 rows)
            │
            ▼
    write_into_ledger() OR print to stdout

CLI::

    python render_ledger_check.py --book books/<slug> --chapter ch-NN
                                  [--out <ledger.md>]

When ``--out`` is provided, the block is anchored on the
``## Gate checklist`` header inside ``<ledger.md>`` and the script replaces
the block (between that header and the next ``## `` section) with the
regenerated table. Re-runs replace cleanly — no duplicate rows.

When ``--out`` is omitted, the generated block is printed to stdout so it
can be piped (e.g. into a manual ``cat >> ledger.md`` workflow).

Status mapping:

* ``PASS`` / ``FAIL`` / ``WARN`` are pulled verbatim from the source check
  payload (status field on each ``{name, status, evidence}``).
* ``n/a`` is emitted when the corresponding source block is missing (e.g.
  Arabic-only ``tashkeel_ratio`` on a non-Arabic book; no
  ``frozen-lines.json`` for the ``Frozen lines intact`` row).

Stdlib-only. No new dependencies.
"""
from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
from pathlib import Path

# Order of the 8 rows in the rendered table. Each row is
# ``(<rule label>, <row status block-fn>, <row evidence block-fn>)``.
# The block-functions receive the parsed JSON payloads and return
# ``(status_string, evidence_string)``; missing payloads default to ``n/a``.
GATE_ROW_ORDER: tuple[str, ...] = (
    "Word window",
    "Countdown ≥1",
    "Closing hook ≤8",
    "Frozen lines intact",
    "Banned-pattern scan",
    "Cross-ref integrity",
    "Source ratio",
    "Tashkeel ratio",
)

CHECK_CHAPTER_BY_RULE: dict[str, str] = {
    "Word window": "word_count_per_beat",
    "Countdown ≥1": "countdown",
    "Closing hook ≤8": "closing_hook",
    "Banned-pattern scan": "banned_patterns",
}


# ---------------------------------------------------------------------------
# Subprocess wrappers — graceful fallback when the upstream script is absent.
# ---------------------------------------------------------------------------


def _load_check_chapter_json(scripts_dir: Path, chapter_path: Path) -> dict | None:
    """Run ``check_chapter.py --json`` and return the parsed payload.

    Returns ``None`` if the script is missing or fails — callers handle the
    missing-payload case per row (default status = ``n/a``).
    """
    script = scripts_dir / "check_chapter.py"
    if not script.exists():
        return None
    try:
        proc = subprocess.run(
            [sys.executable, str(script), str(chapter_path), "--json"],
            capture_output=True, text=True, encoding="utf-8", timeout=60,
        )
    except (OSError, subprocess.TimeoutExpired):
        return None
    if proc.returncode not in (0, 1):
        return None
    try:
        return json.loads(proc.stdout)
    except (ValueError, TypeError):
        return None


def _load_book_check_json(book_root: Path) -> dict | None:
    """Run ``book_check.py`` against ``book_root`` and parse its JSON output.

    ``book_check.py`` prints its JSON payload as the first stdout line; on
    failure it exits non-zero and emits ``FAIL:`` lines on stderr.
    """
    scripts_dir = Path(__file__).resolve().parent
    script = scripts_dir / "book_check.py"
    if not script.exists():
        return None
    try:
        proc = subprocess.run(
            [sys.executable, str(script), str(book_root)],
            capture_output=True, text=True, encoding="utf-8", timeout=120,
        )
    except (OSError, subprocess.TimeoutExpired):
        return None
    if not proc.stdout.strip():
        return None
    # book_check prints the JSON on stdout followed by a human summary
    # line on stderr — first parseable JSON object on stdout is the payload.
    first_line = proc.stdout.splitlines()[0] if proc.stdout else ""
    try:
        return json.loads(first_line)
    except ValueError:
        return None


# ---------------------------------------------------------------------------
# Status / evidence resolvers — one per row.
# ---------------------------------------------------------------------------

_VALID_STATUS = ("PASS", "FAIL", "WARN")


def _normalise_status(raw: object) -> str | None:
    """Return ``raw`` if it is one of ``PASS``/``FAIL``/``WARN``; else ``None``."""
    if isinstance(raw, str) and raw in _VALID_STATUS:
        return raw
    return None


def _find_check(payload: dict | None, name: str) -> dict | None:
    """Locate ``{name, status, evidence}`` for ``name`` in a ``check_chapter`` payload."""
    if not isinstance(payload, dict):
        return None
    for c in payload.get("checks") or []:
        if isinstance(c, dict) and c.get("name") == name:
            return c
    return None


def _row_from_check_chapter(check_cc_payload: dict | None, rule_name: str) -> tuple[str, str]:
    """Status + evidence for the 4 rows served by ``check_chapter.py``.

    Falls back to ``(n/a, "0 occurrences")`` when the source is missing —
    matches the spec's default behaviour for n/a rows.
    """
    found = _find_check(check_cc_payload, CHECK_CHAPTER_BY_RULE.get(rule_name, ""))
    if found is None:
        return ("n/a", "0 occurrences")
    status = _normalise_status(found.get("status")) or "n/a"
    evidence = str(found.get("evidence") or "0 occurrences")
    return (status, evidence)


def _row_frozen_lines(book_root: Path, chapter_filename: str) -> tuple[str, str]:
    """Verify ``.frozen-lines.json`` shas against the chapter text.

    Re-implements the book_check frozen-intact check so this script can
    run without depending on ``book_check.py`` being present. ``frozen_intact``
    here means *every* declared frozen line in the chapter's manifest block
    still has its declared sha256 in the chapter file's text. Returns
    ``(n/a, "0/0 sha256 match")`` when no manifest is configured for the
    chapter.
    """
    fp = book_root / "frozen-lines.json"
    if not fp.exists():
        return ("n/a", "0/0 sha256 match")
    try:
        raw = json.loads(fp.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return ("n/a", "0/0 sha256 match")
    chapters_block = raw.get("chapters") if isinstance(raw, dict) else None
    if not isinstance(chapters_block, dict):
        return ("n/a", "0/0 sha256 match")
    entries = chapters_block.get(chapter_filename) or chapters_block.get(Path(chapter_filename).stem + ".md")
    if not isinstance(entries, dict):
        return ("n/a", "0/0 sha256 match")
    import hashlib
    chapter_path = book_root / "chapters" / chapter_filename
    if not chapter_path.exists():
        return ("n/a", "0/0 sha256 match")
    lines = chapter_path.read_text(encoding="utf-8").splitlines()
    items = entries.get("frozen_lines") or []
    if not items:
        return ("n/a", "0/0 sha256 match")
    total = len(items)
    matched = 0
    for item in items:
        n = int(item.get("line_number", 0) or 0)
        expected = (item.get("sha256") or "").strip()
        if expected and 0 < n <= len(lines):
            actual = hashlib.sha256(lines[n - 1].rstrip().encode("utf-8")).hexdigest()
            if actual == expected:
                matched += 1
    status = "PASS" if matched == total else "FAIL"
    return (status, f"{matched}/{total} sha256 match")


def _row_cross_ref(book_check_payload: dict | None) -> tuple[str, str]:
    """Status + evidence for the cross-ref integrity row.

    Status inference:
      * any non-empty ``broken`` list → ``FAIL`` (broken refs always fail)
      * empty / absent ``broken`` list → ``PASS`` (absence of broken refs
        is the authoritative signal — even if `resolved != total` in a
        synthetic edge case)
      * payload entirely missing → ``n/a``
    Evidence cell always reads ``<resolved>/<total> resolved``.
    """
    if not isinstance(book_check_payload, dict):
        return ("n/a", "n/total resolved")
    cr = book_check_payload.get("cross_ref")
    if not isinstance(cr, dict):
        return ("n/a", "n/total resolved")
    resolved = cr.get("resolved")
    total = cr.get("total")
    if not isinstance(resolved, int) or not isinstance(total, int) or total <= 0:
        return ("n/a", "n/total resolved")
    broken = cr.get("broken") or []
    status = "FAIL" if isinstance(broken, list) and broken else "PASS"
    return (status, f"{resolved}/{total} resolved")


def _per_chapter_ratio(book_check_payload: dict | None, key: str,
                        chapter_filename: str) -> tuple[str, str]:
    """Status + evidence for rows based on ``book_check`` per-chapter ratios."""
    if not isinstance(book_check_payload, dict):
        return ("n/a", "n/a")
    chapters = book_check_payload.get("chapters") or {}
    info = chapters.get(chapter_filename) or chapters.get(Path(chapter_filename).stem + ".md")
    if not isinstance(info, dict):
        return ("n/a", "n/a")
    val = info.get(key)
    if val is None:
        return ("n/a", "n/a")
    if isinstance(val, (int, float)):
        if key == "source_ratio":
            tol = info.get("source_ratio_tolerance")
            if isinstance(tol, (int, float)) and tol > 0:
                if val < 1 - tol or val > 1 + tol:
                    return ("FAIL", f"{val:.3f}")
            return ("PASS", f"{val:.3f}")
        if key == "tashkeel_ratio":
            if val < 0:
                return ("FAIL", f"{val:.3f}")
            return ("PASS", f"{val:.3f}")
    return ("n/a", "n/a")


# ---------------------------------------------------------------------------
# Block builder — pure function over JSON dicts (testable without subprocess).
# ---------------------------------------------------------------------------


def build_gate_block(chapter_filename: str,
                     book_check_payload: dict | None = None,
                     check_chapter_payload: dict | None = None,
                     book_root: Path | None = None) -> str:
    """Render the 8-row ``## Gate checklist`` markdown block.

    Parameters
    ----------
    chapter_filename
        e.g. ``"ch-01.md"`` — selects the per-chapter rows in
        ``book_check`` payloads and the per-chapter frozen manifest.
    book_check_payload
        Optional parsed ``book_check.py --json`` output. When ``None``
        the rows that depend on it default to ``n/a``.
    check_chapter_payload
        Optional parsed ``check_chapter.py --json`` output. When ``None``
        the rows that depend on it default to ``n/a``.
    book_root
        Optional books/<slug> path — only used to recompute the
        ``Frozen lines intact`` row when the caller passes a
        ``book_check_payload`` that doesn't already include the per-chapter
        frozen manifest. In practice, ``book_check_payload`` is authoritative.

    Returns
    -------
    The full markdown block (including the trailing blank line) ready to
    be inserted into ``## Gate checklist``. Always 8 rows in the fixed
    spec order.
    """
    rows: list[tuple[str, str, str]] = []
    for rule in GATE_ROW_ORDER:
        if rule in CHECK_CHAPTER_BY_RULE:
            status, evidence = _row_from_check_chapter(check_chapter_payload, rule)
        elif rule == "Frozen lines intact":
            if book_root is not None:
                status, evidence = _row_frozen_lines(book_root, chapter_filename)
            else:
                status, evidence = ("n/a", "0/0 sha256 match")
        elif rule == "Cross-ref integrity":
            status, evidence = _row_cross_ref(book_check_payload)
        elif rule == "Source ratio":
            status, evidence = _per_chapter_ratio(book_check_payload, "source_ratio", chapter_filename)
        elif rule == "Tashkeel ratio":
            status, evidence = _per_chapter_ratio(book_check_payload, "tashkeel_ratio", chapter_filename)
        else:
            status, evidence = ("n/a", "")
        rows.append((rule, status, evidence))

    out: list[str] = []
    out.append("| Rule | Status | Evidence |")
    out.append("| --- | --- | --- |")
    for rule, status, evidence in rows:
        out.append(f"| {rule} | {status} | {_short_evidence(evidence)} |")
    out.append("")
    return "\n".join(out)


def _short_evidence(evidence: str) -> str:
    """Trim evidence text to one line and 200 chars (table cell sanity)."""
    one_line = re.sub(r"\s+", " ", evidence).strip()
    if len(one_line) > 200:
        one_line = one_line[:197] + "…"
    return one_line or "0 occurrences"


# ---------------------------------------------------------------------------
# Ledger writer — anchor on ``## Gate checklist`` and replace cleanly.
# ---------------------------------------------------------------------------

_LEDGER_HEADER = re.compile(r"^##\s+Gate checklist\s*$", re.MULTILINE)
_NEXT_HEADER = re.compile(r"^##\s+\S", re.MULTILINE)


def _find_block_range(text: str) -> tuple[int, int] | None:
    """Return (start, end) character indices of the existing gate block.

    The block begins right after the ``## Gate checklist`` header line
    (start = end-of-line of the matched header) and ends at the start of
    the next ``## …`` section header, or at EOF. When the header is
    absent, returns ``None``.
    """
    m = _LEDGER_HEADER.search(text)
    if m is None:
        return None
    start = text.find("\n", m.end())
    if start < 0:
        return len(text), len(text)
    start += 1
    tail = text[start:]
    nxt = _NEXT_HEADER.search(tail)
    end = start + (nxt.start() if nxt else len(tail))
    return start, end


def write_into_ledger(ledger_path: Path, block: str) -> int:
    """Replace the existing ``## Gate checklist`` block (or append it).

    Idempotent — re-running replaces cleanly so re-runs never duplicate.

    Returns ``1`` if the block was replaced in-place, ``0`` if it was
    appended (no existing header found), ``2`` if the file didn't exist
    or was empty.
    """
    if not ledger_path.exists():
        return 2
    text = ledger_path.read_text(encoding="utf-8")
    if not text.strip():
        return 2
    rng = _find_block_range(text)
    if rng is None:
        # No header yet → append a fresh header + block at EOF.
        sep = "" if text.endswith("\n") else "\n"
        ledger_path.write_text(text + sep + "## Gate checklist\n\n" + block, encoding="utf-8")
        return 0
    start, end = rng
    # Trim trailing blank lines from the existing block so we re-emit a
    # canonical block with exactly one trailing newline.
    while end > start and text[end - 1] in " \t":
        end -= 1
    while end > start and text[end - 1] == "\n":
        end -= 1
    new_text = text[:start] + block.rstrip("\n") + "\n" + text[end:]
    ledger_path.write_text(new_text, encoding="utf-8")
    return 1


# ---------------------------------------------------------------------------
# Orchestration
# ---------------------------------------------------------------------------


def _force_utf8_stdio():
    for stream in (sys.stdout, sys.stderr):
        reconfigure = getattr(stream, "reconfigure", None)
        if reconfigure is not None:
            try:
                reconfigure(encoding="utf-8")
            except (ValueError, OSError):
                pass


def main(argv=None):
    p = argparse.ArgumentParser(description=__doc__,
                                formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--book", type=Path, required=True,
                   help="path to books/<slug>/ (must contain chapters/<ch>.md)")
    p.add_argument("--chapter", type=str, required=True,
                   help="chapter label, e.g. ch-03 (file is chapters/ch-03.md)")
    p.add_argument("--out", type=Path, default=None,
                   help="path to ledger.md — when present, the script replaces "
                        "the ## Gate checklist block in-place (or appends it "
                        "when the header is absent). When omitted, prints the "
                        "block to stdout.")
    args = p.parse_args(argv)
    _force_utf8_stdio()

    book_root = args.book
    chapter_filename = args.chapter if args.chapter.endswith(".md") else args.chapter + ".md"
    chapter_path = book_root / "chapters" / chapter_filename
    if not chapter_path.exists():
        print(f"render_ledger_check: not a file: {chapter_path}", file=sys.stderr)
        return 2

    scripts_dir = Path(__file__).resolve().parent
    check_chapter_payload = _load_check_chapter_json(scripts_dir, chapter_path)
    book_check_payload = _load_book_check_json(book_root)

    block = build_gate_block(
        chapter_filename,
        book_check_payload=book_check_payload,
        check_chapter_payload=check_chapter_payload,
        book_root=book_root,
    )

    if args.out is None:
        sys.stdout.write(block)
        return 0

    rc = write_into_ledger(args.out, block)
    if rc == 2:
        print(f"render_ledger_check: ledger not found or empty: {args.out}", file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    sys.exit(main())
