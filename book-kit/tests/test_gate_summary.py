"""Tests for gate_summary.py - per-chapter gate artifact emitter.

Stdlib-only fixtures. The tests target the pure functions directly:

* ``_derive_status`` - the canonical APPROVED / FIX-LOOP-N / REJECTED logic.
* ``render_gate`` - the byte-stable markdown block producer.
* ``_read_check_chapter`` / ``_read_book_check`` / ``_read_review`` - the
  I/O loaders (each exercised against a tmp_path fixture with hand-crafted
  payloads).
* ``_summarize_book_check`` / ``_summarize_review`` - the per-line label
  + evidence producers.

The script's CLI (``main``) is exercised by a few subprocess / direct-call
end-to-end tests that confirm the exit-code mapping and the --out path
validation guard. Mirrors the test style of P2/P3/P4/P5.
"""
import json
import sys
from pathlib import Path

# conftest.py already prepends book-kit/book_workflow/scripts to sys.path.
import gate_summary as gs

KIT_ROOT = Path(__file__).resolve().parents[1]
SCRIPT = KIT_ROOT / "book_workflow" / "scripts" / "gate_summary.py"


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _write_chapter(root, name="ch-01.md", text=None):
    p = root / "chapters" / name
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(text or "# Chapter\n\nBody text here.\n", encoding="utf-8")
    return p


def _write_review(reports_dir, task_id, name="04_review_T-2026-08-05-001_P5.md",
                  body="# Review\n\n## Verdict\nPASS\n"):
    p = reports_dir / task_id / name
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(body, encoding="utf-8")
    return p


def _write_check_chapter_json(reports_dir, task_id, chapter_label, checks):
    p = reports_dir / task_id / f"check_chapter_{chapter_label}.json"
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps({"chapter": chapter_label, "checks": checks}),
                 encoding="utf-8")
    return p


def _write_book_check_json(reports_dir, task_id, payload):
    p = reports_dir / task_id / "book_check.json"
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(payload), encoding="utf-8")
    return p


def _fake_review_with_high():
    return (
        "# Review\n\n"
        "## Per-task verdicts\n\n"
        "### HIGH\n\n"
        "Some HIGH issue.\n\n"
        "### file.py:42 - high issue\n\n"
        "details\n"
    )


def _fake_review_with_critical():
    return (
        "# Review\n\n"
        "## Per-task verdicts\n\n"
        "### CRITICAL\n\n"
        "Some CRITICAL issue.\n\n"
        "### file.py:10 - critical sub\n\n"
        "details\n"
    )


def _clean_review():
    return "# Review\n\n## Per-task verdicts\n\nNo findings.\n"


# ---------------------------------------------------------------------------
# 1) Status logic - APPROVED
# ---------------------------------------------------------------------------


def test_status_approved_when_all_pass_and_no_review_findings(tmp_path):
    """All checks PASS, review has 0 HIGH/CRITICAL -> APPROVED, exit 0."""
    _write_chapter(tmp_path, "ch-01.md", "# Title\n\nbody " * 80 + "\n")
    reports = tmp_path / "reports"
    _write_check_chapter_json(reports, "T-1", "ch-01", [
        {"name": "word_count_per_beat", "status": "PASS", "evidence": "ok"},
        {"name": "closing_hook", "status": "PASS", "evidence": "ok"},
    ])
    _write_review(reports, "T-1", body=_clean_review())
    rc = gs.main([
        "--book", str(tmp_path),
        "--chapter", "ch-01",
        "--review", str(reports / "T-1" / "04_review_T-2026-08-05-001_P5.md"),
        "--task", "T-1",
        "--reports-dir", str(reports),
    ])
    assert rc == 0, f"expected APPROVED (rc=0); got rc={rc}"


# ---------------------------------------------------------------------------
# 2) Status logic - FIX-LOOP-N
# ---------------------------------------------------------------------------


def test_status_fix_loop_when_check_fails(tmp_path):
    """Any check FAIL -> FIX-LOOP-N, exit 1. N honours --loop."""
    _write_chapter(tmp_path, "ch-01.md", "# Title\n\nbody " * 80 + "\n")
    reports = tmp_path / "reports"
    _write_check_chapter_json(reports, "T-2", "ch-01", [
        {"name": "word_count_per_beat", "status": "FAIL", "evidence": "boom"},
    ])
    _write_review(reports, "T-2", body=_clean_review())
    rc = gs.main([
        "--book", str(tmp_path),
        "--chapter", "ch-01",
        "--review", str(reports / "T-2" / "04_review_T-2026-08-05-001_P5.md"),
        "--task", "T-2",
        "--reports-dir", str(reports),
        "--loop", "3",
    ])
    assert rc == 1, f"expected FIX-LOOP (rc=1); got rc={rc}"
    out = (reports / "T-2" / "02_gate_ch-01_T-2.md").read_text(encoding="utf-8")
    assert "FIX-LOOP-3" in out, f"expected FIX-LOOP-3 in artifact; got:\n{out}"


# ---------------------------------------------------------------------------
# 3) Status logic - REJECTED
# ---------------------------------------------------------------------------


def test_status_rejected_when_review_has_critical(tmp_path):
    """Review has CRITICAL -> REJECTED, exit 1."""
    _write_chapter(tmp_path, "ch-01.md", "# Title\n\nbody\n")
    reports = tmp_path / "reports"
    _write_check_chapter_json(reports, "T-3", "ch-01", [
        {"name": "word_count_per_beat", "status": "PASS", "evidence": "ok"},
    ])
    _write_review(reports, "T-3", body=_fake_review_with_critical())
    rc = gs.main([
        "--book", str(tmp_path),
        "--chapter", "ch-01",
        "--review", str(reports / "T-3" / "04_review_T-2026-08-05-001_P5.md"),
        "--task", "T-3",
        "--reports-dir", str(reports),
    ])
    assert rc == 1, f"expected REJECTED (rc=1); got rc={rc}"
    out = (reports / "T-3" / "02_gate_ch-01_T-3.md").read_text(encoding="utf-8")
    assert "REJECTED" in out, f"expected REJECTED in artifact; got:\n{out}"
    assert "1 critical" in out, f"expected 1 critical in Reviewer line; got:\n{out}"


# ---------------------------------------------------------------------------
# 4) Path validation - --out outside --book rejected
# ---------------------------------------------------------------------------


def test_path_validation_rejects_outside_book(tmp_path):
    """--out pointing outside --book is rejected with exit 2 + clear error."""
    _write_chapter(tmp_path, "ch-01.md", "# Title\n\nbody\n")
    reports = tmp_path / "reports"
    _write_check_chapter_json(reports, "T-4", "ch-01", [])
    _write_review(reports, "T-4", body=_clean_review())
    outside = tmp_path.parent / "outside-book.md"  # sibling of tmp_path
    rc = gs.main([
        "--book", str(tmp_path),
        "--chapter", "ch-01",
        "--review", str(reports / "T-4" / "04_review_T-2026-08-05-001_P5.md"),
        "--task", "T-4",
        "--reports-dir", str(reports),
        "--out", str(outside),
    ])
    assert rc == 2, f"expected path-validation reject (rc=2); got rc={rc}"
    assert not outside.exists(), "out-of-book path must NOT be created"


# ---------------------------------------------------------------------------
# 5) Missing review file -> input error
# ---------------------------------------------------------------------------


def test_missing_review_returns_2(tmp_path):
    """--review pointing to a non-existent file -> exit 2, no artifact written."""
    _write_chapter(tmp_path, "ch-01.md", "# Title\n\nbody\n")
    reports = tmp_path / "reports"
    rc = gs.main([
        "--book", str(tmp_path),
        "--chapter", "ch-01",
        "--review", str(tmp_path / "no-such-review.md"),
        "--task", "T-5",
        "--reports-dir", str(reports),
    ])
    assert rc == 2, f"expected missing-review reject (rc=2); got rc={rc}"


# ---------------------------------------------------------------------------
# 6) Missing chapter file -> input error
# ---------------------------------------------------------------------------


def test_missing_chapter_returns_2(tmp_path):
    """Chapter file does not exist -> exit 2."""
    reports = tmp_path / "reports"
    _write_review(reports, "T-6")
    rc = gs.main([
        "--book", str(tmp_path),
        "--chapter", "ch-99",
        "--review", str(reports / "T-6" / "04_review_T-2026-08-05-001_P5.md"),
        "--task", "T-6",
        "--reports-dir", str(reports),
    ])
    assert rc == 2, f"expected missing-chapter reject (rc=2); got rc={rc}"


# ---------------------------------------------------------------------------
# 7) render_gate - byte-stable block producer
# ---------------------------------------------------------------------------


def test_render_gate_byte_stable(tmp_path):
    """render_gate is byte-stable for a given input - no timestamps, fixed order."""
    block = gs.render_gate(
        "ch-03",
        word_count=712,
        window=(600, 750),
        book_check_status="PASS",
        book_check_evidence="",
        reviewer_status="PASS",
        reviewer_evidence="(0 critical, 1 high)",
        frozen_count=2,
        frozen_lines=[41, 88],
        open_questions=1,
        status="APPROVED",
    )
    expected_lines = [
        "## Gate: ch-03 - APPROVED",
        "Word count: 712 (window 600-750) [OK]",
        "Book-check: PASS",
        "Reviewer: PASS (0 critical, 1 high)",
        "Frozen lines touched: 2 (lines 41, 88)",
        "Open questions: 1",
    ]
    # ``block`` ends with a single newline; ``splitlines()`` strips the
    # trailing empty entry. The artifact file as written has 7 lines
    # (6 content + 1 trailing newline).
    assert block.splitlines() == expected_lines, (
        f"render_gate output drifted:\nexpected: {expected_lines}\n"
        f"got:      {block.splitlines()}"
    )
    # The string ends with one newline.
    assert block.endswith("\n"), "render_gate must end with a single newline"
    assert not block.endswith("\n\n"), "render_gate must NOT end with a double newline"


# ---------------------------------------------------------------------------
# 8) _derive_status - pure function exhaustively
# ---------------------------------------------------------------------------


def test_derive_status_matrix():
    """The status matrix is exactly what plan §P6 prescribes."""
    # All PASS, no review -> APPROVED
    assert gs._derive_status(
        [{"status": "PASS"}], critical=0, high=0, loop_n=1
    ) == "APPROVED"
    # Any FAIL -> FIX-LOOP-N
    assert gs._derive_status(
        [{"status": "FAIL"}], critical=0, high=0, loop_n=1
    ) == "FIX-LOOP-1"
    assert gs._derive_status(
        [{"status": "PASS"}, {"status": "FAIL"}], critical=0, high=0, loop_n=4
    ) == "FIX-LOOP-4"
    # Any HIGH -> FIX-LOOP-N
    assert gs._derive_status(
        [{"status": "PASS"}], critical=0, high=1, loop_n=2
    ) == "FIX-LOOP-2"
    # Any CRITICAL -> REJECTED (even if check passes)
    assert gs._derive_status(
        [{"status": "PASS"}], critical=1, high=0, loop_n=1
    ) == "REJECTED"
    # CRITICAL dominates over FAIL/HIGH
    assert gs._derive_status(
        [{"status": "FAIL"}], critical=1, high=1, loop_n=1
    ) == "REJECTED"


# ---------------------------------------------------------------------------
# 9) _read_review - counts CRITICAL and HIGH headers case-sensitively
# ---------------------------------------------------------------------------


def test_read_review_counts_critical_and_high():
    """The review loader pins the canonical severity-header lines.

    Case-sensitive on the severity markers: only the exact strings
    ``### CRITICAL`` and ``### HIGH`` (top-of-line) increment the
    severity counts. Sub-issues are every other ``### `` header
    (including the lowercase ``### critical subsection`` form, which
    is a sub-issue header, not a severity marker).
    """
    import tempfile
    text = (
        "# Review\n\n"
        "### CRITICAL\n"
        "### HIGH\n"
        "### file.py:1 - high issue\n"
        "### file.py:2 - sub-issue under HIGH\n"
        "### critical subsection (lowercase, IS a sub-issue header)\n"
    )
    with tempfile.NamedTemporaryFile("w", suffix=".md", delete=False, encoding="utf-8") as f:
        f.write(text)
        p = Path(f.name)
    try:
        crit, high, sub, _raw = gs._read_review(p)
    finally:
        p.unlink()
    assert crit == 1, f"expected 1 CRITICAL header; got {crit}"
    assert high == 1, f"expected 1 HIGH header; got {high}"
    # Sub-issues: 3 (the file.py:1 + file.py:2 + lowercase critical subsection)
    assert sub == 3, f"expected 3 sub-issues; got {sub}"


# ---------------------------------------------------------------------------
# 10) _read_frozen_lines - parses manifest or returns 0
# ---------------------------------------------------------------------------


def test_read_frozen_lines_counts_manifest_entries(tmp_path):
    """A seeded manifest with N entries -> (N, sorted line numbers)."""
    fp = tmp_path / "frozen-lines.json"
    fp.write_text(json.dumps({
        "chapters": {
            "ch-01.md": {
                "frozen_lines": [
                    {"line_number": 41, "sha256": "x"},
                    {"line_number": 88, "sha256": "x"},
                ]
            }
        }
    }), encoding="utf-8")
    n, lines = gs._read_frozen_lines(tmp_path, "ch-01.md")
    assert n == 2, f"expected 2 entries; got {n}"
    assert lines == [41, 88], f"expected sorted line numbers; got {lines}"


def test_read_frozen_lines_returns_zero_when_no_manifest(tmp_path):
    """No frozen-lines.json -> (0, [])."""
    n, lines = gs._read_frozen_lines(tmp_path, "ch-01.md")
    assert n == 0
    assert lines == []


# ---------------------------------------------------------------------------
# 11) _read_open_questions - counts numbered items under ## Open questions
# ---------------------------------------------------------------------------


def test_read_open_questions_counts_numbered_items(tmp_path):
    """A ledger.md with N numbered items under ## Open questions -> N."""
    ledger = tmp_path / "ledger.md"
    ledger.write_text(
        "# Ledger\n\n"
        "## Open questions\n\n"
        "1. First question.\n"
        "2. Second question.\n"
        "3. Third question.\n\n"
        "## Other section\n"
        "1. This one is in another section, not counted.\n",
        encoding="utf-8",
    )
    assert gs._read_open_questions(tmp_path) == 3


def test_read_open_questions_returns_zero_when_no_ledger(tmp_path):
    """No ledger.md -> 0."""
    assert gs._read_open_questions(tmp_path) == 0


# ---------------------------------------------------------------------------
# 12) End-to-end manual smoke on books/daily-focus/ (real fixture)
# ---------------------------------------------------------------------------


def test_end_to_end_daily_focus_artifact_shape(tmp_path):
    """Run the script against a real daily-focus chapter and confirm all 5
    spec fields are present in the output.

    Uses the actual ``books/daily-focus/chapters/ch-01.md`` and the
    committed P4 review. This is the acceptance-criterion #4 smoke.
    """
    # KIT_ROOT = book-kit/; repo root = book-kit/../ = workspace root.
    repo_root = KIT_ROOT.parent
    book = repo_root / "books" / "daily-focus"
    review = repo_root / "share" / "reports" / "04_review_T-2026-08-05-001_P4.md"
    if not book.exists() or not review.exists():
        import pytest
        pytest.skip("real daily-focus fixture or P4 review not present in this checkout")
    # Use a tmp task id so we don't pollute share/reports.
    task_id = "T-smoke-gate"
    reports = tmp_path / "reports"
    rc = gs.main([
        "--book", str(book),
        "--chapter", "ch-01",
        "--review", str(review),
        "--task", task_id,
        "--reports-dir", str(reports),
    ])
    # P4 review has no CRITICAL / HIGH -> APPROVED, exit 0.
    assert rc == 0, f"daily-focus smoke: expected APPROVED (rc=0); got rc={rc}"
    out_path = reports / task_id / f"02_gate_ch-01_{task_id}.md"
    assert out_path.exists(), f"artifact not written: {out_path}"
    text = out_path.read_text(encoding="utf-8")
    # All 5 spec fields must be present.
    for field in (
        "## Gate: ch-01 -",
        "Word count:",
        "Book-check:",
        "Reviewer:",
        "Frozen lines touched:",
        "Open questions:",
    ):
        assert field in text, f"field missing from artifact: {field!r}\n{text}"
