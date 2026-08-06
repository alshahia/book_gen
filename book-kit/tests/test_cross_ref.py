"""Tests for cross_ref.py — cross-reference resolver + book_check integration.

Each test writes a tiny fixture chapter set to ``tmp_project/chapters/`` and
exercises ``cross_ref.run_cross_ref()`` directly (no subprocess / no mocks).
The book_check integration test (#6) is the one exception — it spawns
``book_check.py`` to confirm the FAIL/PASS line reaches stderr end-to-end.

Mirrors the file-based-fixture style of ``test_check_chapter.py``: literal
chapter text on disk, no mocking of the extractor/resolver pipeline.

H1 headings intentionally avoid ``Chapter N`` phrasing so the
``RE_ENG_CHAPTER`` pattern doesn't auto-match every chapter title (which
would break the no-refs baseline). Only the explicit `[ch-NN]`,
`(ch-NN.md#anchor)`, or Arabic-numeric forms are counted.
"""
import json
import subprocess
import sys
from pathlib import Path

# conftest.py already prepends book-kit/book_workflow/scripts to sys.path.
import cross_ref

KIT_ROOT = Path(__file__).resolve().parents[1]
BOOK_CHECK_SCRIPT = KIT_ROOT / "book_workflow" / "scripts" / "book_check.py"


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _write_chapter(tmp_project, name, text):
    p = tmp_project / "chapters" / name
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(text, encoding="utf-8")
    return p


def _run_on_chapters(tmp_project):
    """Run cross_ref.run_cross_ref on every chapter file in ``tmp_project``."""
    chapters_dir = tmp_project / "chapters"
    return cross_ref.run_cross_ref(
        sorted(chapters_dir.glob("ch-*.md")),
        book_root=tmp_project,
    )


# ---------------------------------------------------------------------------
# 1) Good refs all resolve
# ---------------------------------------------------------------------------

def test_good_refs_all_resolve(tmp_project):
    """3 chapters with valid ``[ch-NN]`` + ``(ch-NN.md#anchor)`` refs → 0 broken.

    Counts:
      ch-01.md: ``[ch-02]`` + ``[ch-03]`` = 2 refs
      ch-02.md: ``(ch-01.md#setup)``        = 1 ref
      ch-03.md: ``(ch-02.md#causes)``       = 1 ref
      total = 4 resolved, 0 broken.
    """
    _write_chapter(tmp_project, "ch-01.md",
        "# Title\n\n## Setup\n\nInitial setup paragraph.\n\n"
        "## Beginning\n\n"
        "This chapter sets up [ch-02] and references [ch-03].\n")
    _write_chapter(tmp_project, "ch-02.md",
        "# Title\n\n## Causes\n\nThe causes section.\n\n"
        "Reference back to (ch-01.md#setup).\n")
    _write_chapter(tmp_project, "ch-03.md",
        "# Title\n\n## Resolution\n\nThe resolution.\n\n"
        "See (ch-02.md#causes) for the causes.\n")

    result = _run_on_chapters(tmp_project)
    assert result["broken"] == [], f"expected no broken refs, got: {result['broken']}"
    assert result["resolved"] == 4
    assert result["total"] == 4


# ---------------------------------------------------------------------------
# 2) Broken anchor — non-existent #anchor target
# ---------------------------------------------------------------------------

def test_broken_anchor(tmp_project):
    """Reference to a non-existent ``#anchor`` → broken with correct reason."""
    _write_chapter(tmp_project, "ch-01.md",
        "# Title\n\n## Setup\n\nInitial setup paragraph.\n")
    _write_chapter(tmp_project, "ch-02.md",
        "# Title\n\n## Causes\n\nThe causes section.\n\n"
        "See (ch-01.md#nonexistent) for more.\n")

    result = _run_on_chapters(tmp_project)
    assert len(result["broken"]) == 1, f"expected 1 broken; got {len(result['broken'])}: {result['broken']}"
    b = result["broken"][0]
    assert b["from_file"] == "ch-02.md"
    assert "nonexistent" in b["expected_target"]
    assert "no such anchor" in b["reason"]
    assert result["resolved"] == 0


# ---------------------------------------------------------------------------
# 3) Broken chapter — non-existent ch-NN file
# ---------------------------------------------------------------------------

def test_broken_chapter(tmp_project):
    """Reference to a non-existent ``ch-99`` → broken with correct reason."""
    _write_chapter(tmp_project, "ch-01.md",
        "# Title\n\n## Setup\n\nSee [ch-99] for more.\n")

    result = _run_on_chapters(tmp_project)
    assert len(result["broken"]) == 1
    b = result["broken"][0]
    assert b["from_file"] == "ch-01.md"
    assert "ch-99" in b["expected_target"]
    assert "no such file" in b["reason"]
    assert result["resolved"] == 0


# ---------------------------------------------------------------------------
# 4) Arabic-Indic digits normalize to ASCII
# ---------------------------------------------------------------------------

def test_arabic_numerals(tmp_project):
    """``الفصل ٠٣`` (Arabic-Indic ٠٣ = ASCII 03) resolves to ch-03.

    Counts:
      ch-03.md heading ``## الفصل 3`` → self-ref to ch-03 (heading match) = 1
      ch-04.md ``الفصل ٠٣`` → arabic_chapter target=3 → resolves           = 1
      ch-04.md ``[ch-02]`` → bracket_ch target=2 → resolves                = 1
      total = 3 resolved, 0 broken.
    """
    _write_chapter(tmp_project, "ch-01.md",
        "# Title\n\n## Setup\n\nInitial setup paragraph.\n")
    _write_chapter(tmp_project, "ch-02.md",
        "# Title\n\n## Mid\n\nMid chapter.\n")
    _write_chapter(tmp_project, "ch-03.md",
        "# Title\n\n## الفصل 3\n\nReference target chapter.\n")
    _write_chapter(tmp_project, "ch-04.md",
        "# Title\n\n## Intro\n\n"
        "Discussed in الفصل ٠٣ and referenced via [ch-02].\n")

    result = _run_on_chapters(tmp_project)
    assert result["broken"] == [], (
        f"Arabic-Indic ref should resolve; got broken: {result['broken']}"
    )
    assert result["resolved"] == 3, f"expected 3 resolved, got {result['resolved']}"
    assert result["total"] == 3


# ---------------------------------------------------------------------------
# 5) No refs at all → 0 broken / 0 resolved
# ---------------------------------------------------------------------------

def test_no_refs_no_broken(tmp_project):
    """Chapters with no cross-references at all → 0/0 baseline.

    H1 uses plain ``# Title`` (no ``Chapter N`` phrasing) and H2/H3 use
    generic words, so none of the regex patterns fire.
    """
    _write_chapter(tmp_project, "ch-01.md",
        "# Title\n\n## Setup\n\n"
        "Just prose with no cross-references anywhere.\n")
    _write_chapter(tmp_project, "ch-02.md",
        "# Title\n\n## More\n\nPure prose, nothing here.\n")

    result = _run_on_chapters(tmp_project)
    assert result["broken"] == []
    assert result["resolved"] == 0
    assert result["total"] == 0


# ---------------------------------------------------------------------------
# 6) book_check.py surfaces FAIL: cross_ref in stderr
# ---------------------------------------------------------------------------

def test_book_check_emits_cross_ref_check(tmp_project):
    """book_check.py emits ``FAIL: cross_ref`` line in stderr on broken ref.

    The fixture has a planted broken anchor in ch-02.md; the integration
    code in book_check.py is expected to detect it, emit a per-broken-ref
    FAIL line to stderr, and exit 1.
    """
    _write_chapter(tmp_project, "ch-01.md",
        "# Title\n\n## Setup\n\nInitial setup paragraph.\n")
    _write_chapter(tmp_project, "ch-02.md",
        "# Title\n\n## Causes\n\nThe causes section.\n\n"
        "See (ch-01.md#nonexistent) for more.\n")
    _write_chapter(tmp_project, "ch-03.md",
        "# Title\n\n## Resolution\n\nThe resolution.\n")

    proc = subprocess.run(
        [sys.executable, str(BOOK_CHECK_SCRIPT), str(tmp_project)],
        capture_output=True, text=True, encoding="utf-8", timeout=30,
    )
    assert "FAIL: cross_ref" in proc.stderr, (
        f"expected 'FAIL: cross_ref' in stderr; got: {proc.stderr!r}"
    )
    assert "nonexistent" in proc.stderr, (
        f"expected broken-anchor name in stderr; got: {proc.stderr!r}"
    )
    assert proc.returncode == 1, (
        f"book_check.py should exit 1 on broken refs; got {proc.returncode}"
    )
