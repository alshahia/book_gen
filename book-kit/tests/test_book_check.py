"""Tests for book_check.py — chapter regex, fence balance, glossary parser, source-map parser,
tolerance override (style-guide.md frontmatter), per-chapter source_ratio + glossary_drift_exempt,
and JSON Schema validation for frozen-lines + translate-progress."""
from pathlib import Path

from book_check import (
    CHAPTER,
    DEFAULT_TOLERANCES,
    FENCE,
    fence_balance,
    glossary_terms,
    parse_style_guide_tolerances,
    source_map,
    untranslated_english_ratio,
    word_count,
)

KIT_ROOT = Path(__file__).resolve().parents[1]
FIXTURES = KIT_ROOT / "tests" / "fixtures"


def test_self_check_passes():
    import subprocess
    import sys
    r = subprocess.run(
        [sys.executable, str(Path(__file__).parent.parent / "book_workflow" / "scripts" / "book_check.py"), "--self-check"],
        capture_output=True, text=True, timeout=30,
    )
    assert r.returncode == 0, r.stderr


def test_chapter_regex_accepts_slug_suffixed():
    assert CHAPTER.match("ch-01-prompt-chaining.md")
    assert CHAPTER.match("ch-02-routing.md")
    assert CHAPTER.match("ch-21.md")
    assert CHAPTER.match("introduction.md")
    assert CHAPTER.match("preface.md")


def test_chapter_regex_rejects_non_chapters():
    assert not CHAPTER.match("random-file.md")
    assert not CHAPTER.match("README.md")
    assert not CHAPTER.match("style-guide.md")


def test_fence_balance_even():
    assert fence_balance("```\nbody\n```\n") == 0


def test_fence_balance_unclosed_open():
    assert fence_balance("```\nbody without closing\n") == 1


def test_word_count_arabic_and_english():
    txt = "hello world مرحبا بالعالم"
    n = word_count(txt)
    assert n >= 4  # 2 english + 2 arabic words minimum


def test_untranslated_english_ratio_all_english():
    txt = "the quick brown fox jumps over the lazy dog " * 10
    r = untranslated_english_ratio(txt)
    assert r > 0.95


def test_untranslated_english_ratio_all_arabic():
    txt = "هذا نص عربي طويل لاختبار النسبة " * 10
    r = untranslated_english_ratio(txt)
    assert r < 0.05


def test_source_map_parse(tmp_project):
    (tmp_project / "source-map.md").write_text(
        "| chapter | source | word_min | word_max | required_h2 | freeze_code |\n"
        "|---|---|---:|---:|---|:-:|\n"
        "| ch-01.md | x.txt | 100 | 500 | - | yes |\n",
        encoding="utf-8",
    )
    smap = source_map(tmp_project / "source-map.md")
    assert "ch-01.md" in smap
    assert smap["ch-01.md"]["source"] == "x.txt"
    assert smap["ch-01.md"]["word_min"] == 100
    assert smap["ch-01.md"]["word_max"] == 500


def test_source_map_missing(tmp_project):
    smap = source_map(tmp_project / "no-source-map.md")
    assert smap == {}


def test_glossary_terms_basic(tmp_project):
    (tmp_project / "glossary.md").write_text(
        "| English | Arabic |\n"
        "|---|---|\n"
        "| Agent | وكيل |\n"
        "| Tool use | استخدام الأدوات |\n",
        encoding="utf-8",
    )
    terms = glossary_terms(tmp_project / "glossary.md")
    assert any("وكيل" in t for t in terms)
    assert any("استخدام" in t for t in terms)


def test_glossary_terms_skips_separator(tmp_project):
    (tmp_project / "glossary.md").write_text(
        "| English | Arabic |\n"
        "|---|---|\n"
        "| Term | مصطلح |\n",
        encoding="utf-8",
    )
    terms = glossary_terms(tmp_project / "glossary.md")
    assert "مصطلح" in terms


# --- tolerance override tests (style-guide.md frontmatter) ---

def test_parse_style_guide_tolerances_no_file(tmp_project):
    tols = parse_style_guide_tolerances(tmp_project / "no-such.md")
    assert tols == DEFAULT_TOLERANCES


def test_parse_style_guide_tolerances_partial_override(tmp_project):
    (tmp_project / "style-guide.md").write_text(
        "---\ntolerances:\n  untranslated_english: 0.50\nlanguage: ar\n---\n# style\n",
        encoding="utf-8",
    )
    tols = parse_style_guide_tolerances(tmp_project / "style-guide.md")
    assert tols["untranslated_english"] == 0.50  # overridden
    assert tols["source_ratio"] == DEFAULT_TOLERANCES["source_ratio"]  # fallback
    assert tols["stuck_threshold_min"] == DEFAULT_TOLERANCES["stuck_threshold_min"]  # fallback


def test_parse_style_guide_tolerances_percentage(tmp_project):
    (tmp_project / "style-guide.md").write_text(
        "---\ntolerances:\n  source_ratio: 50%\n---\n",
        encoding="utf-8",
    )
    tols = parse_style_guide_tolerances(tmp_project / "style-guide.md")
    assert tols["source_ratio"] == 0.50  # 50% → 0.50


def test_parse_style_guide_tolerances_malformed_value_keeps_default(tmp_project):
    (tmp_project / "style-guide.md").write_text(
        "---\ntolerances:\n  untranslated_english: not-a-number\n---\n",
        encoding="utf-8",
    )
    tols = parse_style_guide_tolerances(tmp_project / "style-guide.md")
    assert tols["untranslated_english"] == DEFAULT_TOLERANCES["untranslated_english"]


# --- source-map.md per-chapter override tests ---

def test_source_map_per_chapter_ratio_override(tmp_project):
    (tmp_project / "source-map.md").write_text(
        "| chapter | source | word_min | word_max | required_h2 | freeze_code | source_ratio_override | glossary_drift_exempt |\n"
        "|---|---|---:|---:|---|:-:|:-:|:-:|\n"
        "| ch-01.md | x.txt | 0 | 9999 | - | yes | 0.50 | no |\n"
        "| ch-02.md | y.txt | 0 | 9999 | - | yes | - | yes |\n",
        encoding="utf-8",
    )
    smap = source_map(tmp_project / "source-map.md")
    assert smap["ch-01.md"]["source_ratio_override"] == 0.50
    assert smap["ch-01.md"]["glossary_drift_exempt"] is False
    assert smap["ch-02.md"]["source_ratio_override"] is None
    assert smap["ch-02.md"]["glossary_drift_exempt"] is True


def test_source_map_percentage_ratio_override(tmp_project):
    (tmp_project / "source-map.md").write_text(
        "| chapter | source | word_min | word_max | required_h2 | freeze_code | source_ratio_override | glossary_drift_exempt |\n"
        "|---|---|---:|---:|---|:-:|:-:|:-:|\n"
        "| ch-01.md | x.txt | 0 | 9999 | - | yes | 60% | no |\n",
        encoding="utf-8",
    )
    smap = source_map(tmp_project / "source-map.md")
    assert smap["ch-01.md"]["source_ratio_override"] == 0.60


# --- JSON Schema validation (frozen-lines.json + .translate-progress.json) ---

import shutil
import subprocess
import sys


def _run_book_check(tmp_project):
    """Invoke book_check.py as a subprocess on tmp_project; return CompletedProcess."""
    return subprocess.run(
        [sys.executable, str(KIT_ROOT / "book_workflow" / "scripts" / "book_check.py"), str(tmp_project)],
        capture_output=True, text=True, timeout=30,
    )


def test_schema_valid_frozen_lines(tmp_project):
    """A frozen-lines.json that satisfies the schema must NOT trigger a schema FAIL."""
    shutil.copy(FIXTURES / "frozen-lines-valid.json", tmp_project / "frozen-lines.json")
    r = _run_book_check(tmp_project)
    assert r.returncode == 0, f"expected PASS, got rc={r.returncode}, stderr={r.stderr}"
    assert "FAIL: schema" not in r.stderr, f"unexpected schema failure: {r.stderr}"


def test_schema_invalid_frozen_lines(tmp_project):
    """A mutated frozen-lines.json (missing required 'chapters' field) must FAIL with rc=2
    and the field name must appear in stderr."""
    shutil.copy(FIXTURES / "frozen-lines-invalid.json", tmp_project / "frozen-lines.json")
    r = _run_book_check(tmp_project)
    assert r.returncode == 2, f"expected FAIL (rc=2), got rc={r.returncode}, stderr={r.stderr}"
    assert "FAIL: schema" in r.stderr, f"missing FAIL: schema line in stderr: {r.stderr}"
    assert "chapters" in r.stderr.lower(), f"field name 'chapters' missing from stderr: {r.stderr}"
