"""Tests for book_check.py continuity check (P8).

Mirrors the file-based-fixture style of test_book_check.py: literal
chapter text on disk, no mocks. Exercises the three new helpers:

- parse_bible_anchors: extract `## Continuity anchor` tables from bible.md
- _check_continuity: per-anchor PASS/FAIL arc across the chapters in scope
- parse_tracked_motifs: extract `## Tracked motifs` bullets from style-guide.md
- coin_arc: per-motif PASS/FAIL arc across all `chapters/ch-*.md` files

Each fixture creates ``tmp_path/book/{chapters,bible.md,style-guide.md}``
and exercises the helpers directly. The two spec-required cases are:

1. PASS case — all chapters in scope contain the motif (continuity + coin_arc).
2. FAIL case — ch-03 omits the motif (continuity + coin_arc).
"""
import json
import subprocess
import sys
from pathlib import Path

import book_check

KIT_ROOT = Path(__file__).resolve().parents[1]
BOOK_CHECK_SCRIPT = KIT_ROOT / "book_workflow" / "scripts" / "book_check.py"


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _make_book_root(tmp_path, chapter_specs, *, bible=None, style_guide=None):
    """Create a minimal book root under ``tmp_path/book/``."""
    root = tmp_path / "book"
    chapters = root / "chapters"
    chapters.mkdir(parents=True)
    for ch_name, content in chapter_specs.items():
        (chapters / ch_name).write_text(content, encoding="utf-8")
    if bible is not None:
        (root / "bible.md").write_text(bible, encoding="utf-8")
    if style_guide is not None:
        (root / "style-guide.md").write_text(style_guide, encoding="utf-8")
    return root


# ---------------------------------------------------------------------------
# Bible anchor parser
# ---------------------------------------------------------------------------


def test_parse_bible_anchors_basic(tmp_path):
    """Anchors table parses into keyword/quote/scope dicts."""
    bible = (
        "## Continuity anchor\n\n"
        "| Keyword | Quote | Scope |\n"
        "|---|---|---|\n"
        "| silver coin | a coin engraved with a date | ch-01..ch-05 |\n"
        "| locket | the locket her mother left her | ch-02..ch-04 |\n"
    )
    root = _make_book_root(tmp_path, {}, bible=bible)
    anchors = book_check.parse_bible_anchors(root / "bible.md")
    assert len(anchors) == 2
    assert anchors[0]["keyword"] == "silver coin"
    assert anchors[0]["quote"] == "a coin engraved with a date"
    assert anchors[0]["scope_start"] == 1
    assert anchors[0]["scope_end"] == 5
    assert anchors[1]["keyword"] == "locket"
    assert anchors[1]["scope_end"] == 4


def test_parse_bible_anchors_handles_smart_quotes(tmp_path):
    """Surrounding ASCII / smart quotes on the quote cell are stripped."""
    bible = (
        "## Continuity anchor\n\n"
        "| Keyword | Quote | Scope |\n"
        "|---|---|---|\n"
        '| silver coin | \u201cglinted in the light\u201d | ch-01..ch-03 |\n'
    )
    root = _make_book_root(tmp_path, {}, bible=bible)
    anchors = book_check.parse_bible_anchors(root / "bible.md")
    assert len(anchors) == 1
    assert anchors[0]["quote"] == "glinted in the light"


def test_parse_bible_anchors_handles_endash_scope():
    """WARN #19 inheritance: scope accepts ASCII '-' AND U+2013 en-dash."""
    import tempfile
    with tempfile.TemporaryDirectory() as td:
        root = Path(td)
        (root / "chapters").mkdir(parents=True)
        # ASCII form
        (root / "bible.md").write_text(
            "## Continuity anchor\n\n"
            "| Keyword | Quote | Scope |\n|---|---|---|\n| coin | phr | ch-01..ch-03 |\n",
            encoding="utf-8",
        )
        a_ascii = book_check.parse_bible_anchors(root / "bible.md")
        assert a_ascii[0]["scope_start"] == 1 and a_ascii[0]["scope_end"] == 3
        # en-dash form (U+2013 between chapter numbers, no ..)
        (root / "bible.md").write_text(
            "## Continuity anchor\n\n"
            "| Keyword | Quote | Scope |\n|---|---|---|\n"
            "| coin | phr | ch\u201301..ch\u201303 |\n",
            encoding="utf-8",
        )
        a_endash = book_check.parse_bible_anchors(root / "bible.md")
        assert a_endash[0]["scope_start"] == 1 and a_endash[0]["scope_end"] == 3


def test_parse_bible_anchors_missing_file(tmp_path):
    """Missing bible.md -> empty list."""
    root = tmp_path / "book"
    root.mkdir(parents=True)
    (root / "chapters").mkdir()
    anchors = book_check.parse_bible_anchors(root / "no-such.md")
    assert anchors == []


# ---------------------------------------------------------------------------
# _check_continuity
# ---------------------------------------------------------------------------


def test_check_continuity_pass_all_present(tmp_path):
    """PASS case: all 3 chapters in scope contain the motif keyword."""
    chapters = {
        "ch-01.md": "# T\n\nThe silver coin glinted in the morning light.\n",
        "ch-02.md": "# T\n\nHe turned the silver coin over in his palm.\n",
        "ch-03.md": "# T\n\nShe paid the merchant with a silver coin at last.\n",
    }
    bible = (
        "## Continuity anchor\n\n"
        "| Keyword | Quote | Scope |\n|---|---|---|\n"
        "| silver coin | glinted in the morning light | ch-01..ch-03 |\n"
    )
    root = _make_book_root(tmp_path, chapters, bible=bible)
    anchors = book_check.parse_bible_anchors(root / "bible.md")
    results = book_check._check_continuity(root, anchors)
    assert len(results) == 1
    assert results[0]["status"] == "PASS"
    assert results[0]["chapters_missing"] == []
    # Arc labels: first=introduced, middle=mentioned, last=paid
    arc = results[0]["arc"]
    assert "(introduced)" in arc and "(mentioned)" in arc and "(paid)" in arc


def test_check_continuity_fail_ch03_omits_keyword(tmp_path):
    """Spec fixture: 3-chapter where ch-03 omits motif -> FAIL."""
    chapters = {
        "ch-01.md": "# T\n\nThe silver coin glinted in the morning light.\n",
        "ch-02.md": "# T\n\nHe turned the silver coin over in his palm.\n",
        "ch-03.md": "# T\n\nShe paid the merchant with gold at last.\n",  # no silver coin
    }
    bible = (
        "## Continuity anchor\n\n"
        "| Keyword | Quote | Scope |\n|---|---|---|\n"
        "| silver coin | glinted in the morning light | ch-01..ch-03 |\n"
    )
    root = _make_book_root(tmp_path, chapters, bible=bible)
    anchors = book_check.parse_bible_anchors(root / "bible.md")
    results = book_check._check_continuity(root, anchors)
    assert len(results) == 1
    assert results[0]["status"] == "FAIL"
    assert "ch-03" in results[0]["chapters_missing"]
    assert "ch-01" not in results[0]["chapters_missing"]
    # Arc labels: ch-03 should be (missing)
    assert "(missing)" in results[0]["arc"]


# ---------------------------------------------------------------------------
# parse_tracked_motifs
# ---------------------------------------------------------------------------


def test_parse_tracked_motifs_basic(tmp_path):
    """Bullets under `## Tracked motifs` parse into a motif list."""
    style_guide = (
        "## Word-count windows\n\n| ch-01 | 100 - 500 |\n\n"
        "## Tracked motifs\n\n"
        "- silver coin\n"
        "- locket\n"
        "- compass\n"
    )
    root = _make_book_root(tmp_path, {}, style_guide=style_guide)
    motifs = book_check.parse_tracked_motifs(root / "style-guide.md")
    assert motifs == ["silver coin", "locket", "compass"]


def test_parse_tracked_motifs_strips_trailing_colon_reason(tmp_path):
    """A bullet like `- motif: reason` is stored as just `motif`."""
    style_guide = "## Tracked motifs\n\n- silver coin: introduced ch-01\n"
    root = _make_book_root(tmp_path, {}, style_guide=style_guide)
    motifs = book_check.parse_tracked_motifs(root / "style-guide.md")
    assert motifs == ["silver coin"]


def test_parse_tracked_motifs_missing_section(tmp_path):
    """No `## Tracked motifs` block -> empty list."""
    style_guide = "## Word-count windows\n\n| ch-01 | 100 - 500 |\n"
    root = _make_book_root(tmp_path, {}, style_guide=style_guide)
    motifs = book_check.parse_tracked_motifs(root / "style-guide.md")
    assert motifs == []


# ---------------------------------------------------------------------------
# coin_arc
# ---------------------------------------------------------------------------


def test_coin_arc_pass_all_present(tmp_path):
    """PASS case: motif present in all 3 chapters."""
    chapters = {
        "ch-01.md": "# T\n\nThe compass pointed north.\n",
        "ch-02.md": "# T\n\nHe checked the compass again.\n",
        "ch-03.md": "# T\n\nThe compass led them home.\n",
    }
    style_guide = "## Tracked motifs\n\n- compass\n"
    root = _make_book_root(tmp_path, chapters, style_guide=style_guide)
    motifs = book_check.parse_tracked_motifs(root / "style-guide.md")
    arcs = book_check.coin_arc(root, motifs)
    assert len(arcs) == 1
    assert arcs[0]["motif"] == "compass"
    assert arcs[0]["status"] == "PASS"
    assert arcs[0]["chapters_missing"] == []
    arc = arcs[0]["arc"]
    assert "(introduced)" in arc and "(mentioned)" in arc and "(paid)" in arc


def test_coin_arc_fail_ch03_omits_motif(tmp_path):
    """Spec fixture: 3-chapter where ch-03 omits motif -> FAIL."""
    chapters = {
        "ch-01.md": "# T\n\nThe compass pointed north.\n",
        "ch-02.md": "# T\n\nHe checked the compass again.\n",
        "ch-03.md": "# T\n\nThey reached home at last.\n",  # no compass
    }
    style_guide = "## Tracked motifs\n\n- compass\n"
    root = _make_book_root(tmp_path, chapters, style_guide=style_guide)
    motifs = book_check.parse_tracked_motifs(root / "style-guide.md")
    arcs = book_check.coin_arc(root, motifs)
    assert len(arcs) == 1
    assert arcs[0]["status"] == "FAIL"
    assert "ch-03" in arcs[0]["chapters_missing"]
    assert "(missing)" in arcs[0]["arc"]


# ---------------------------------------------------------------------------
# End-to-end: book_check.py main() emits the new JSON keys
# ---------------------------------------------------------------------------


def test_book_check_main_emits_continuity_and_coin_arc_json(tmp_path):
    """Running book_check.py as a subprocess emits the new P8 JSON keys."""
    chapters = {
        "ch-01.md": "# T\n\nThe silver coin glinted in the morning light.\n",
        "ch-02.md": "# T\n\nHe turned the silver coin over in his palm.\n",
        "ch-03.md": "# T\n\nShe paid the merchant with gold at last.\n",
    }
    bible = (
        "## Continuity anchor\n\n"
        "| Keyword | Quote | Scope |\n|---|---|---|\n"
        "| silver coin | glinted in the morning light | ch-01..ch-03 |\n"
    )
    style_guide = "## Tracked motifs\n\n- compass\n"
    root = _make_book_root(tmp_path, chapters, bible=bible, style_guide=style_guide)
    # Suppress untranslated_english noise by raising tolerance.
    (root / "style-guide.md").write_text(
        "---\ntolerances:\n  untranslated_english: 0.99\n---\n\n"
        + style_guide,
        encoding="utf-8",
    )
    r = subprocess.run(
        [sys.executable, str(BOOK_CHECK_SCRIPT), str(root)],
        capture_output=True, text=True, timeout=30,
    )
    # Even if a chapter-level check fails, the JSON payload is still on stdout.
    data = json.loads(r.stdout.splitlines()[0])
    assert "continuity" in data, f"continuity key missing: {list(data)}"
    assert "coin_arc" in data, f"coin_arc key missing: {list(data)}"
    assert data["continuity"][0]["status"] == "FAIL"
    assert "ch-03" in data["continuity"][0]["chapters_missing"]
    assert data["coin_arc"][0]["motif"] == "compass"
    assert data["coin_arc"][0]["status"] == "FAIL"
    assert data["summary"]["checks"]["continuity"] == 1
    assert data["summary"]["checks"]["coin_arc"] == 1
