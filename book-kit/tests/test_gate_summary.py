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

P17 additions:
* ``chunk_for_review`` - pure-Python chunking helper used by the
  orchestrator's Phase 7 splitting strategy. Tested against a 3000-word
  fixture (12 H3 sections, 3117 words) that the spec requires to produce
  exactly 4 chunks.
* Reviewer invocation count - the artifact gains a ``Reviewer
  invocations: N`` line (P17) controlled by the new ``--reviewer-invocations``
  CLI flag (default 1).
"""
import json
import re
import sys
from pathlib import Path

# conftest.py already prepends book-kit/book_workflow/scripts to sys.path.
import gate_summary as gs

KIT_ROOT = Path(__file__).resolve().parents[1]
SCRIPT = KIT_ROOT / "book_workflow" / "scripts" / "gate_summary.py"
FIXTURES = KIT_ROOT / "tests" / "fixtures"

# Word regex mirrors gate_summary._WORD (kept local so the chunk_for_review
# helper stays a pure function with no module-level coupling).
_WORD = re.compile(r"\b[\w'\-\u2018\u2019]+\b", re.UNICODE)
_H3_BREAK = re.compile(r"(?m)(?=^### )")


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
        reviewer_invocations=1,
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
        "Reviewer invocations: 1",
        "Frozen lines touched: 2 (lines 41, 88)",
        "Open questions: 1",
    ]
    # ``block`` ends with a single newline; ``splitlines()`` strips the
    # trailing empty entry. The artifact file as written has 8 lines
    # (7 content + 1 trailing newline).
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


# ---------------------------------------------------------------------------
# P17 - chunk_for_review helper (pure function used by orchestrator Phase 7)
# ---------------------------------------------------------------------------


def chunk_for_review(text, max_tokens=800):
    """Split chapter text into review chunks of <= ``max_tokens`` words.

    Algorithm (matches the orchestrator Phase 7 splitting strategy):

    1. If ``len(words) <= max_tokens``, return ``[text]`` as a single chunk
       (one reviewer invocation; no splitting needed).
    2. Otherwise, split the text at H3 headings (lines beginning with
       ``### ``). The lookahead keeps the H3 line attached to the section
       it introduces.
    3. Greedily group consecutive sections into chunks whose total word
       count stays under ``max_tokens``. Flush the current chunk whenever
       adding the next section would push it over the budget.
    4. If a single section still exceeds ``max_tokens`` (oversized H3),
       fall through to paragraph splitting and then to a word-window
       last resort. This is the defensive path that prevents a runaway
       chunk when a writer crams too many words into one section.
    """
    words = len(_WORD.findall(text))
    if words <= max_tokens:
        return [text]
    sections = _H3_BREAK.split(text)
    sections = [s for s in sections if s.strip()]
    if len(sections) <= 1:
        return _chunk_by_paragraphs(text, max_tokens)
    chunks: list[str] = []
    current = ""
    current_words = 0
    for section in sections:
        sec_words = len(_WORD.findall(section))
        # Oversized section: flush whatever we have, then split this one.
        if sec_words > max_tokens:
            if current:
                chunks.append(current)
                current = ""
                current_words = 0
            chunks.extend(_chunk_by_paragraphs(section, max_tokens))
            continue
        # Adding this section would overflow -> flush.
        if current and current_words + sec_words > max_tokens:
            chunks.append(current)
            current = section
            current_words = sec_words
            continue
        # Otherwise accumulate.
        current += section
        current_words += sec_words
    if current:
        chunks.append(current)
    return chunks


def _chunk_by_paragraphs(text, max_tokens):
    """Paragraph-level fallback when no H3 boundaries are available."""
    paragraphs = re.split(r"\n\s*\n", text)
    paragraphs = [p for p in paragraphs if p.strip()]
    if len(paragraphs) <= 1:
        return _chunk_by_words(text, max_tokens)
    chunks: list[str] = []
    current = ""
    current_words = 0
    for p in paragraphs:
        pw = len(_WORD.findall(p))
        if pw > max_tokens:
            if current:
                chunks.append(current)
                current = ""
                current_words = 0
            chunks.extend(_chunk_by_words(p, max_tokens))
            continue
        if current and current_words + pw > max_tokens:
            chunks.append(current)
            current = p
            current_words = pw
            continue
        if current:
            current += "\n\n" + p
        else:
            current = p
        current_words += pw
    if current:
        chunks.append(current)
    return chunks


def _chunk_by_words(text, max_tokens):
    """Word-window last resort when even a single paragraph exceeds budget."""
    words = text.split()
    return [
        " ".join(words[i:i + max_tokens])
        for i in range(0, len(words), max_tokens)
    ]


# ---------------------------------------------------------------------------
# P17 tests - Reviewer invocations field in the gate artifact
# ---------------------------------------------------------------------------


def test_render_gate_includes_invocation_count(tmp_path):
    """``render_gate`` surfaces ``reviewer_invocations`` as a dedicated
    field that sits immediately after the ``Reviewer:`` line (P17)."""
    block = gs.render_gate(
        "ch-07",
        word_count=712,
        window=(600, 750),
        book_check_status="PASS",
        book_check_evidence="",
        reviewer_status="PASS",
        reviewer_evidence="(0 critical, 0 high)",
        reviewer_invocations=4,
        frozen_count=0,
        frozen_lines=[],
        open_questions=0,
        status="APPROVED",
    )
    assert "Reviewer invocations: 4" in block, (
        f"missing invocation count line; got:\n{block}"
    )
    lines = block.splitlines()
    rev_idx = next(i for i, ln in enumerate(lines) if ln.startswith("Reviewer:"))
    assert lines[rev_idx + 1] == "Reviewer invocations: 4", (
        f"invocation line must follow Reviewer: directly; got:\n{lines}"
    )


def test_invocation_count_default_is_one(tmp_path):
    """When ``--reviewer-invocations`` is omitted the artifact reports 1."""
    _write_chapter(tmp_path, "ch-01.md", "# Title\n\nbody " * 80 + "\n")
    reports = tmp_path / "reports"
    _write_check_chapter_json(reports, "T-P17-def", "ch-01", [
        {"name": "word_count_per_beat", "status": "PASS", "evidence": "ok"},
    ])
    _write_review(reports, "T-P17-def", body=_clean_review())
    rc = gs.main([
        "--book", str(tmp_path),
        "--chapter", "ch-01",
        "--review", str(reports / "T-P17-def" / "04_review_T-2026-08-05-001_P5.md"),
        "--task", "T-P17-def",
        "--reports-dir", str(reports),
    ])
    assert rc == 0, f"expected APPROVED (rc=0); got rc={rc}"
    out = (reports / "T-P17-def" / "02_gate_ch-01_T-P17-def.md").read_text(
        encoding="utf-8"
    )
    assert "Reviewer invocations: 1" in out, (
        f"default invocation count must be 1; got:\n{out}"
    )


def test_invocation_count_via_cli_flag(tmp_path):
    """``--reviewer-invocations N`` propagates N into the artifact."""
    _write_chapter(tmp_path, "ch-12.md", "# Title\n\nbody " * 80 + "\n")
    reports = tmp_path / "reports"
    _write_check_chapter_json(reports, "T-P17-cli", "ch-12", [
        {"name": "word_count_per_beat", "status": "PASS", "evidence": "ok"},
    ])
    _write_review(reports, "T-P17-cli", body=_clean_review())
    rc = gs.main([
        "--book", str(tmp_path),
        "--chapter", "ch-12",
        "--review", str(reports / "T-P17-cli" / "04_review_T-2026-08-05-001_P5.md"),
        "--task", "T-P17-cli",
        "--reports-dir", str(reports),
        "--reviewer-invocations", "7",
    ])
    assert rc == 0, f"expected APPROVED (rc=0); got rc={rc}"
    out = (reports / "T-P17-cli" / "02_gate_ch-12_T-P17-cli.md").read_text(
        encoding="utf-8"
    )
    assert "Reviewer invocations: 7" in out, (
        f"--reviewer-invocations 7 must surface; got:\n{out}"
    )


# ---------------------------------------------------------------------------
# P17 tests - chunk_for_review algorithm + E2E with invocation count
# ---------------------------------------------------------------------------


def test_chunk_for_review_short_text_returns_one_chunk():
    """Text shorter than ``max_tokens`` returns the original text intact."""
    short = "# Title\n\nA short paragraph of prose for testing.\n" * 5
    chunks = chunk_for_review(short, max_tokens=800)
    assert len(chunks) == 1, f"expected 1 chunk; got {len(chunks)}"
    assert chunks[0] == short, "short text must be returned as-is"


def test_chunk_for_review_long_chapter_yields_four_chunks():
    """The 3000-word long-chapter fixture must produce exactly 4 chunks.

    This is the spec contract for P17: ``1 fixture chapter with 3000 words
    -> orchestrator runs 4 chunks -> 1 consolidated review``.  Each chunk
    must stay at or under the 800-token budget so a reviewer prompt that
    reads the chunk plus checklist never overflows the model's context.
    """
    text = (FIXTURES / "long-chapter.md").read_text(encoding="utf-8")
    total_words = len(_WORD.findall(text))
    assert 2950 <= total_words <= 3200, (
        f"fixture must be ~3000 words; got {total_words}"
    )
    chunks = chunk_for_review(text, max_tokens=800)
    assert len(chunks) == 4, (
        f"expected 4 chunks for 3000-word fixture; got {len(chunks)}"
    )
    for i, c in enumerate(chunks):
        wc = len(_WORD.findall(c))
        assert wc <= 800, f"chunk {i} has {wc} words; exceeds max 800"


def test_chunk_for_review_oversized_section_splits():
    """A single H3 section exceeding ``max_tokens`` must split further.

    Defensive test: the orchestrator's spec allows a chapter to have one
    fat H3 section (e.g. a long code-listing section).  ``chunk_for_review``
    must split it via the paragraph -> word-window fallback chain so the
    reviewer never receives a chunk larger than the budget.
    """
    long_para = "x " + "word " * 900
    text = (
        "# Title\n\n## Section\n\n"
        "### Oversized\n\n" + long_para + "\n\n"
        "### Small\n\nshort body\n"
    )
    chunks = chunk_for_review(text, max_tokens=800)
    assert len(chunks) >= 2, (
        f"oversized section must split into >=2 chunks; got {len(chunks)}"
    )
    for i, c in enumerate(chunks):
        wc = len(_WORD.findall(c))
        assert wc <= 800, f"chunk {i} has {wc} words; exceeds max 800"


def test_chunk_for_review_e2e_with_invocation_count(tmp_path):
    """End-to-end: the chunk count drives the gate artifact's invocation line.

    Splits the 3000-word fixture via ``chunk_for_review`` (4 chunks), then
    runs ``gate_summary`` with ``--reviewer-invocations`` equal to the
    chunk count and confirms the artifact reports the same N.  This ties
    the splitting algorithm (orchestrator-side) to the invocation count
    (gate artifact-side) so the two pieces agree on what ``N`` means.
    """
    text = (FIXTURES / "long-chapter.md").read_text(encoding="utf-8")
    chunks = chunk_for_review(text, max_tokens=800)
    n_invocations = len(chunks)
    assert n_invocations == 4, f"preflight: expected 4 chunks; got {n_invocations}"

    _write_chapter(tmp_path, "ch-long.md", text)
    reports = tmp_path / "reports"
    _write_check_chapter_json(reports, "T-P17-e2e", "ch-long", [
        {"name": "word_count_per_beat", "status": "PASS", "evidence": "ok"},
    ])
    _write_review(reports, "T-P17-e2e", body=_clean_review())
    rc = gs.main([
        "--book", str(tmp_path),
        "--chapter", "ch-long",
        "--review", str(reports / "T-P17-e2e" / "04_review_T-2026-08-05-001_P5.md"),
        "--task", "T-P17-e2e",
        "--reports-dir", str(reports),
        "--reviewer-invocations", str(n_invocations),
    ])
    assert rc == 0, f"expected APPROVED (rc=0); got rc={rc}"
    out = (reports / "T-P17-e2e" / "02_gate_ch-long_T-P17-e2e.md").read_text(
        encoding="utf-8"
    )
    assert f"Reviewer invocations: {n_invocations}" in out, (
        f"expected Reviewer invocations: {n_invocations}; got:\n{out}"
    )
