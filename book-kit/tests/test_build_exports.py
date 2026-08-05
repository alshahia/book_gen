"""Tests for build_exports.py — TOC + glossary + index + Arabic-Indic numerals + RTL detection."""
from pathlib import Path

from build_exports import (
    arabic_indic,
    chapter_title,
    style_directive,
)


def test_self_check_passes():
    """build_exports has no --self-check mode — it runs main directly. Verify it exits 0 with JSON output."""
    import subprocess
    import sys
    r = subprocess.run(
        [sys.executable, str(Path(__file__).parent.parent / "book_workflow" / "scripts" / "build_exports.py")],
        capture_output=True, text=True, timeout=30,
    )
    assert r.returncode == 0, r.stderr
    assert '"chapters"' in r.stdout


def test_arabic_indic_basic():
    assert arabic_indic(1) == "\u0661"
    assert arabic_indic(12) == "\u0661\u0662"
    assert arabic_indic(123) == "\u0661\u0662\u0663"
    assert arabic_indic(0) == "\u0660"


def test_arabic_indic_round_trip():
    for n in (1, 5, 10, 42, 100, 999):
        result = arabic_indic(n)
        assert all("\u0660" <= c <= "\u0669" for c in result)
        assert len(result) == len(str(n))


def test_chapter_title_basic():
    text = "# My Chapter\n\nbody\n"
    assert chapter_title(text) == "My Chapter"


def test_chapter_title_with_fallback():
    text = "no header here\n"
    assert chapter_title(text, fallback="fallback-name") == "fallback-name"


def test_style_directive_ltr_explicit(tmp_path):
    (tmp_path / "style-guide.md").write_text(
        "# Style\n\nrtl: false\nlanguage: en\n", encoding="utf-8",
    )
    out = style_directive(tmp_path / "style-guide.md")
    assert out["rtl"] is False
    assert out["language"] == "en"


def test_style_directive_rtl_explicit(tmp_path):
    (tmp_path / "style-guide.md").write_text(
        "# Style\n\nrtl: true\nlanguage: ar\n", encoding="utf-8",
    )
    out = style_directive(tmp_path / "style-guide.md")
    assert out["rtl"] is True
    assert out["language"] == "ar"


def test_style_directive_heuristic_arabic_body(tmp_path):
    """No explicit directive but body is majority-Arabic → detected as RTL/ar."""
    arabic_body = "\u0647\u0630\u0627 \u0641\u0642\u0631\u0629 \u0639\u0631\u0628\u064a\u0629 \u0637\u0648\u064a\u0644\u0629 " * 30
    (tmp_path / "style-guide.md").write_text(arabic_body, encoding="utf-8")
    out = style_directive(tmp_path / "style-guide.md")
    assert out["rtl"] is True
    assert out["language"] == "ar"


def test_style_directive_missing(tmp_path):
    """Missing file → defaults to LTR/en."""
    out = style_directive(tmp_path / "no-such-file.md")
    assert out["rtl"] is False
    assert out["language"] == "en"
