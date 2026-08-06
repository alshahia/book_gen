"""gate_summary.py - per-chapter gate artifact emitter for book-kit.

CLI::

    python gate_summary.py --book <books/<slug>/> --chapter ch-NN
                           --review <share/reports/04_review_*.md>
                           [--task <task-id>] [--reports-dir <path>]
                           [--out <path-under-book>] [--loop N]

Reads (in order):

  * ``<book>/chapters/ch-NN.md``         word count + frozen-line surface
  * ``<book>/bible.md``                  rules-applicability (read for context,
                                         not required for v1)
  * ``<book>/frozen-lines.json``         per-chapter frozen-line declarations
  * ``<book>/ledger.md``                 Open questions section
  * ``<reports>/<task>/check_chapter_ch-NN.md`` (or ``.json``)  P2 output
  * ``<reports>/<task>/book_check.json``                          P3 output
  * ``<reports>/<task>/04_review_<task>.md``                      am-review

Status logic (verbatim from plan §P6):

  * ``APPROVED``   all checks PASS and review has 0 HIGH/CRITICAL
  * ``FIX-LOOP-N`` any FAIL or any review HIGH (N = attempt count, default 1)
  * ``REJECTED``   review has any CRITICAL finding

Default output: ``<reports>/<task>/02_gate_ch-NN_<task>.md`` (auto-created).

Optional ``--out <path>`` writes the same block to a path under ``--book``
(used by orchestrator/CI to land the artifact next to the chapter).
A path outside ``--book`` is rejected (defensive guard; P4 #14 inheritance).

Review parsing: counts ``### CRITICAL`` and ``### HIGH`` headers
(case-sensitive, top-of-line) and the ``### `` sub-issues under each.

Exit codes:
  * 0  APPROVED
  * 1  FIX-LOOP-N  or  REJECTED   (gate did not approve)
  * 2  input error (missing file, path validation, JSON decode)

The sample output template in this docstring is ASCII-only on purpose:
the ``[OK]`` token replaces the U+2713 check mark from the plan sample
because Windows cp1256 terminals (the kit's worst-case target) crash
on any non-ASCII char in the argparse help text.  See the implementation
notes for the ponytail rationale.

  ponytail: ASCII-only docstring keeps ``--help`` from crashing on
            Windows-cp1256 (P4 #15 + P5 #22 inheritance).  The actual
            artifact file uses the original ``[OK]`` / ``-`` literals -
            it is written as UTF-8, so the file is portable.

Stdlib-only. No new dependencies.
"""
from __future__ import annotations

import argparse
import io
import json
import re
import sys
from pathlib import Path

# ---------------------------------------------------------------------------
# Force UTF-8 stdio FIRST, before any argparse / print call.
#
# Inherited from P4 #15 + P5 #20: argparse fires ``print_help()`` during
# ``parse_args(argv)``; on Windows-cp1256 (the kit's worst-case terminal)
# any non-ASCII char in the docstring (U+2713 check mark, U+2013 en-dash,
# U+2265 greater-equal, etc.) raises ``UnicodeEncodeError: 'charmap' codec
# can't encode character '\\uXXXX'``.  Calling ``reconfigure(encoding="utf-8")``
# on the streams before any argparse code runs keeps ``--help`` clean even
# if a future edit reintroduces a non-ASCII glyph.
# ---------------------------------------------------------------------------
for _stream in (sys.stdout, sys.stderr):
    try:
        _stream.reconfigure(encoding="utf-8")
    except (AttributeError, io.UnsupportedOperation):
        pass


# ---------------------------------------------------------------------------
# Word-count helper (local copy - script-independence contract from P2/P3)
# ---------------------------------------------------------------------------

_FENCE = re.compile(r"```.*?```", re.DOTALL)
_WORD = re.compile(r"\b[\w'\-\u2018\u2019]+\b", re.UNICODE)


def _read_text(path):
    """Read text with UTF-8 -> cp1256 -> cp1252 -> latin-1 fallback."""
    p = Path(path)
    try:
        return p.read_text(encoding="utf-8")
    except UnicodeDecodeError:
        for enc in ("cp1256", "cp1252"):
            try:
                return p.read_text(encoding=enc)
            except UnicodeDecodeError:
                continue
        return p.read_text(encoding="latin-1")


def _word_count(text):
    """Count word tokens (Latin + Arabic); code fences stripped first."""
    clean = _FENCE.sub("", text)
    return len(_WORD.findall(clean))


# ---------------------------------------------------------------------------
# Field readers
# ---------------------------------------------------------------------------

def _read_check_chapter(reports_dir, task_id, chapter_label):
    """Return ``(checks_list, source)`` from P2 output, or ``([], None)``.

    Looks for ``check_chapter_ch-NN.json`` first (cleanest), then falls
    back to the ``.md`` form (default output of P2's non-JSON mode).
    Returns the parsed ``checks: [{name, status, evidence}, ...]`` list
    plus a short source label so the gate artifact can cite provenance.
    """
    base = reports_dir / task_id
    json_path = base / f"check_chapter_{chapter_label}.json"
    md_path = base / f"check_chapter_{chapter_label}.md"
    if json_path.exists():
        try:
            data = json.loads(json_path.read_text(encoding="utf-8"))
            return list(data.get("checks") or []), f"check_chapter:{json_path.name}"
        except (OSError, ValueError):
            pass
    if md_path.exists():
        try:
            text = md_path.read_text(encoding="utf-8")
        except OSError:
            return [], None
        # Markdown form: "## Check: <name> | <STATUS>\n\n<evidence>\n\n"
        checks: list[dict] = []
        for m in re.finditer(
            r"^##\s+Check:\s+(?P<name>\S+)\s*\|\s*(?P<status>PASS|FAIL|WARN)\s*$\n+(?P<evidence>.*?)(?=^##\s|\Z)",
            text,
            re.MULTILINE | re.DOTALL,
        ):
            checks.append({
                "name": m.group("name"),
                "status": m.group("status"),
                "evidence": m.group("evidence").strip(),
            })
        if checks:
            return checks, f"check_chapter:{md_path.name}"
    return [], None


def _read_book_check(reports_dir, task_id):
    """Return parsed ``book_check.py`` JSON, or ``None``."""
    p = reports_dir / task_id / "book_check.json"
    if not p.exists():
        return None
    try:
        return json.loads(p.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return None


def _read_review(path):
    """Return ``(critical_count, high_count, raw)`` from a review report.

    Counts top-of-line ``### CRITICAL`` and ``### HIGH`` headers
    (case-sensitive, exact match per dispatch).  Sub-issues under each
    section (any ``### `` header beneath a top-level severity header) are
    summed separately so the gate artifact can show the breakdown.
    """
    if not path or not Path(path).exists():
        return 0, 0, 0, ""
    text = _read_text(path)
    # Top-level severity headers. The dispatch pins these as the canonical
    # signal; we use line-anchored matches so headers buried inside a code
    # block are NOT counted (the ``^`` anchor + ``re.MULTILINE`` flag handles
    # that for the typical report).
    critical = len(re.findall(r"^###\s+CRITICAL\s*$", text, re.MULTILINE))
    high = len(re.findall(r"^###\s+HIGH\s*$", text, re.MULTILINE))
    # Sub-issues: any ``### `` header that is NOT one of the top-level
    # severity markers above. This gives a coarse "findings count" that
    # the gate artifact can surface.
    sub_issues = 0
    for header in re.findall(r"^###\s+(\S.*)$", text, re.MULTILINE):
        h = header.strip()
        if h in ("CRITICAL", "HIGH"):
            continue
        sub_issues += 1
    return critical, high, sub_issues, text


def _read_frozen_lines(book_root, chapter_filename):
    """Return ``(count, [line_numbers])`` from ``<book>/frozen-lines.json``.

    When no manifest is present, returns ``(0, [])`` so the gate artifact
    can render ``0 (none declared)`` cleanly.
    """
    fp = Path(book_root) / "frozen-lines.json"
    if not fp.exists():
        return 0, []
    try:
        raw = json.loads(fp.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return 0, []
    chapters = raw.get("chapters") if isinstance(raw, dict) else None
    if not isinstance(chapters, dict):
        return 0, []
    entries = chapters.get(chapter_filename) or chapters.get(Path(chapter_filename).stem + ".md")
    if not isinstance(entries, dict):
        return 0, []
    items = entries.get("frozen_lines") or []
    nums: list[int] = []
    for item in items:
        if not isinstance(item, dict):
            continue
        n = item.get("line_number")
        if isinstance(n, int) and n > 0:
            nums.append(n)
    return len(items), sorted(nums)


def _read_open_questions(book_root):
    """Count numbered items under ``## Open questions`` in ``<book>/ledger.md``.

    Matches lines beginning with ``<digit>.`` or ``-<digit>.`` (the two
    common markdown list-prefixes for numbered items).  Returns 0 when
    the section or the file is absent.
    """
    fp = Path(book_root) / "ledger.md"
    if not fp.exists():
        return 0
    try:
        text = fp.read_text(encoding="utf-8")
    except OSError:
        return 0
    m = re.search(r"^##\s+Open questions\b(.*?)(?=^##\s|\Z)", text, re.MULTILINE | re.DOTALL | re.IGNORECASE)
    if not m:
        return 0
    body = m.group(1)
    return len(re.findall(r"^\s*[-*]?\s*\d+\.\s+\S", body, re.MULTILINE))


# ---------------------------------------------------------------------------
# Status logic - verbatim from plan §P6
# ---------------------------------------------------------------------------

def _derive_status(checks, critical, high, loop_n):
    """Return one of ``APPROVED`` / ``FIX-LOOP-N`` / ``REJECTED``."""
    if critical > 0:
        return "REJECTED"
    any_fail = any((c.get("status") == "FAIL") for c in checks)
    if any_fail or high > 0:
        return f"FIX-LOOP-{loop_n}"
    return "APPROVED"


# ---------------------------------------------------------------------------
# Book-check summary - 1 line, "<STATUS> (<N> warn: <check> ...)"
# ---------------------------------------------------------------------------

# Hard-fail rules (any non-zero count -> FAIL).
_BOOK_CHECK_FAIL_RULES = (
    "fence_balance",
    "forbidden_patterns",
    "word_window",
    "cross_ref",
    "untranslated_english",
    "frozen_lines",
    "missing_h2",
)
# Soft-warn rules (any non-zero count -> WARN, listed in evidence).
_BOOK_CHECK_WARN_RULES = (
    "glossary_drift",
    "source_ratio",
    "tashkeel",
)


def _summarize_book_check(book_check_payload, chapter_filename):
    """Return ``(status_label, evidence_text)`` for the Book-check line.

    Status mapping (per the spec sample's spirit):

      * any FAIL rule > 0          -> ``FAIL``  with per-rule breakdown
      * any WARN rule > 0          -> ``WARN``  with per-rule breakdown
      * no failures / no warns     -> ``PASS``
      * payload missing            -> ``n/a``   (no evidence)
    """
    if not isinstance(book_check_payload, dict):
        return "n/a", ""
    chapters = book_check_payload.get("chapters") or {}
    info = chapters.get(chapter_filename) or chapters.get(Path(chapter_filename).stem + ".md") or {}
    summary = book_check_payload.get("summary") or {}
    checks = summary.get("checks") or {}
    if not checks:
        return "n/a", ""

    fail_counts = {r: int(checks.get(r, 0) or 0) for r in _BOOK_CHECK_FAIL_RULES}
    warn_counts = {r: int(checks.get(r, 0) or 0) for r in _BOOK_CHECK_WARN_RULES}

    fail_total = sum(fail_counts.values())
    warn_total = sum(warn_counts.values())

    if fail_total > 0:
        rule_s = ", ".join(
            f"{n} {rule}" for rule, n in fail_counts.items() if n > 0
        )
        return "FAIL", f"({rule_s})"

    if warn_total > 0:
        parts: list[str] = []
        if warn_counts.get("glossary_drift", 0) > 0:
            drifts = info.get("glossary_drift") or []
            first = drifts[0] if isinstance(drifts, list) and drifts else ""
            if first:
                parts.append(f"{warn_counts['glossary_drift']} warn: glossary_drift "
                             f"({len(drifts) if isinstance(drifts, list) else 0} "
                             f"missing, e.g. {first})")
            else:
                parts.append(f"{warn_counts['glossary_drift']} warn: glossary_drift")
        if warn_counts.get("source_ratio", 0) > 0:
            tol = info.get("source_ratio_tolerance")
            tol_s = f" (tol {tol})" if isinstance(tol, (int, float)) else ""
            parts.append(f"{warn_counts['source_ratio']} warn: source_ratio{tol_s}")
        if warn_counts.get("tashkeel", 0) > 0:
            parts.append(f"{warn_counts['tashkeel']} warn: tashkeel")
        if not parts:
            parts.append(f"{warn_total} warn(s)")
        return "WARN", "(" + "; ".join(parts) + ")"

    return "PASS", ""


# ---------------------------------------------------------------------------
# Reviewer line
# ---------------------------------------------------------------------------

def _summarize_review(critical, high, sub_issues):
    """Return ``(status_label, evidence_text)`` for the Reviewer line.

    The spec sample shows ``PASS (0 critical, 1 high)`` - so the status
    follows the same status logic as the overall gate but only considers
    the review signal.
    """
    if critical > 0:
        return "REJECTED", f"({critical} critical, {high} high)"
    if high > 0:
        return "FAIL", f"({critical} critical, {high} high)"
    if sub_issues > 0:
        return "PASS", f"({critical} critical, {high} high)"
    return "PASS", f"({critical} critical, {high} high)"


# ---------------------------------------------------------------------------
# Output rendering
# ---------------------------------------------------------------------------

def render_gate(chapter_label, *, word_count, window,
                 book_check_status, book_check_evidence,
                 reviewer_status, reviewer_evidence,
                 frozen_count, frozen_lines,
                 open_questions, status):
    """Render the canonical gate-artifact markdown block.

    Output is byte-stable for a given input (no timestamps, no random
    ordering) so reviewers can diff successive runs.
    """
    lo, hi = window
    lines: list[str] = []
    lines.append(f"## Gate: {chapter_label} - {status}")
    lines.append(
        f"Word count: {word_count} (window {lo}-{hi}) [OK]"
    )
    bc = book_check_status
    bc_ev = f" {book_check_evidence}" if book_check_evidence else ""
    lines.append(f"Book-check: {bc}{bc_ev}")
    lines.append(f"Reviewer: {reviewer_status} {reviewer_evidence}".rstrip())
    if frozen_count == 0:
        lines.append("Frozen lines touched: 0 (none declared)")
    else:
        nums_s = ", ".join(str(n) for n in frozen_lines) if frozen_lines else "?"
        lines.append(f"Frozen lines touched: {frozen_count} (lines {nums_s})")
    lines.append(f"Open questions: {open_questions}")
    lines.append("")  # trailing blank
    return "\n".join(lines)


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def _extract_task_from_review_path(review_path):
    """Pull a ``T-YYYY-MM-DD-NNN`` token from a review path, or None."""
    m = re.search(r"(T-\d{4}-\d{2}-\d{2}-\d{3})", str(review_path))
    return m.group(1) if m else None


def _resolve_reports_dir(reports_arg):
    """Return the reports root as an absolute Path."""
    p = Path(reports_arg)
    if p.is_absolute():
        return p
    return (Path.cwd() / p).resolve()


def main(argv=None):
    p = argparse.ArgumentParser(
        description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    p.add_argument("--book", type=Path, required=True,
                   help="path to books/<slug>/ (must contain chapters/<ch>.md)")
    p.add_argument("--chapter", type=str, required=True,
                   help="chapter label, e.g. ch-03 (file is chapters/ch-03.md)")
    p.add_argument("--review", type=Path, required=True,
                   help="path to 04_review_*.md report (counts CRITICAL / HIGH headers)")
    p.add_argument("--task", type=str, default=None,
                   help="task id used in the output filename (default: extract "
                        "from --review path; fallback: T-2026-08-05-001)")
    p.add_argument("--reports-dir", type=Path, default=Path("share/reports"),
                   help="root for upstream artifacts (default: share/reports)")
    p.add_argument("--out", type=Path, default=None,
                   help="optional override for the output path. When set, "
                        "the path must resolve to a location under --book "
                        "(defensive guard; P4 #14 inheritance).")
    p.add_argument("--loop", type=int, default=1,
                   help="fix-loop attempt count (default: 1). Embedded in "
                        "the FIX-LOOP-N status when applicable.")
    p.add_argument("--window", type=str, default="600-750",
                   help="beat word window lo-hi (default: 600-750, matches "
                        "the check_chapter.py default for Arabic fiction)")
    args = p.parse_args(argv)

    book_root = args.book
    chapter_filename = args.chapter if args.chapter.endswith(".md") else args.chapter + ".md"
    chapter_path = book_root / "chapters" / chapter_filename
    if not chapter_path.exists():
        print(f"gate_summary: chapter not found: {chapter_path}", file=sys.stderr)
        return 2

    # --- 0. Validate review path early - missing review is an input error,
    #     not a free pass (plan §P6 status logic keys off the review signal). ---
    if not args.review.exists():
        print(f"gate_summary: review not found: {args.review}", file=sys.stderr)
        return 2

    # --- 1. Word count from the chapter file ---
    chapter_text = _read_text(chapter_path)
    n_words = _word_count(chapter_text)

    # --- 2. Window ---
    try:
        lo_s, hi_s = args.window.split("-", 1)
        lo, hi = int(lo_s), int(hi_s)
        if not (0 < lo < hi):
            raise ValueError
        window = (lo, hi)
    except (ValueError, AttributeError):
        print(f"gate_summary: invalid --window {args.window!r} (expected LO-HI)", file=sys.stderr)
        return 2

    # --- 3. Resolve task id (CLI override -> review-path token -> default) ---
    task_id = args.task or _extract_task_from_review_path(args.review) or "T-2026-08-05-001"

    # --- 4. Reports dir (absolute so the default lands at <cwd>/share/reports) ---
    reports_dir = _resolve_reports_dir(args.reports_dir)

    # --- 5. P2 / P3 / review payloads ---
    checks, _cc_src = _read_check_chapter(reports_dir, task_id, args.chapter)
    book_check_payload = _read_book_check(reports_dir, task_id)
    critical, high, sub_issues, _review_text = _read_review(args.review)

    # --- 6. Frozen lines + open questions from the book root ---
    frozen_count, frozen_lines = _read_frozen_lines(book_root, chapter_filename)
    open_q = _read_open_questions(book_root)

    # --- 7. Status logic ---
    status = _derive_status(checks, critical, high, args.loop)

    # --- 8. Book-check + reviewer summary lines ---
    bc_status, bc_evidence = _summarize_book_check(book_check_payload, chapter_filename)
    rv_status, rv_evidence = _summarize_review(critical, high, sub_issues)

    # --- 9. Render ---
    block = render_gate(
        args.chapter,
        word_count=n_words,
        window=window,
        book_check_status=bc_status,
        book_check_evidence=bc_evidence,
        reviewer_status=rv_status,
        reviewer_evidence=rv_evidence,
        frozen_count=frozen_count,
        frozen_lines=frozen_lines,
        open_questions=open_q,
        status=status,
    )

    # --- 10. Write to default or override path ---
    if args.out is not None:
        # P4 #14 inheritance: --out must resolve under --book.
        try:
            book_resolved = book_root.resolve()
            out_resolved = args.out.resolve()
        except OSError:
            print(f"gate_summary: invalid path: {args.out}", file=sys.stderr)
            return 2
        if book_resolved != out_resolved and book_resolved not in out_resolved.parents:
            print(
                f"ERROR: --out must be under --book path "
                f"(got {args.out}, book root {book_root})",
                file=sys.stderr,
            )
            return 2
        out_path = args.out
    else:
        out_path = reports_dir / task_id / f"02_gate_{args.chapter}_{task_id}.md"

    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(block, encoding="utf-8")

    print(
        f"gate_summary: wrote {out_path} (status={status}, "
        f"words={n_words}, critical={critical}, high={high})",
        file=sys.stderr,
    )

    # --- 11. Exit code mapping ---
    if status == "APPROVED":
        return 0
    return 1


if __name__ == "__main__":
    sys.exit(main())
