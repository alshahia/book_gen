"""Tests for book_check.py — chapter regex, fence balance, glossary parser, source-map parser."""
from pathlib import Path

from book_check import (
    CHAPTER,
    FENCE,
    fence_balance,
    glossary_terms,
    source_map,
    untranslated_english_ratio,
    word_count,
)


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
    assert CHAPTER.match("app-a-advanced-prompting.md")
    assert CHAPTER.match("app-g-coding-agents.md")


def test_chapter_regex_rejects_non_chapters():
    assert not CHAPTER.match("random.md")
    assert not CHAPTER.match("README.md")
    assert not CHAPTER.match("chapters.md")  # the dir itself, not a chapter


def test_fence_balance_even():
    text = "Here is code:\n\n```\nfoo\n```\n\nAnd more.\n"
    assert fence_balance(text) == 0


def test_fence_balance_unclosed_open():
    text = "Here is code:\n\n```\nfoo\n"
    assert fence_balance(text) == 1


def test_word_count_arabic_and_english():
    text = "Hello world\n\n" + "\u0645\u0631\u062d\u0628\u0627 \u0628\u0627\u0644\u0639\u0627\u0644\u0645\n"
    assert word_count(text) >= 4


def test_untranslated_english_ratio_all_english():
    text = "This is a sample paragraph with several english words here."
    assert untranslated_english_ratio(text) > 0.9


def test_untranslated_english_ratio_all_arabic():
    text = "\u0647\u0630\u0627 \u0641\u0642\u0631\u0629 \u0639\u0631\u0628\u064a\u0629 \u062c\u0645\u064a\u0644\u0629 \u062c\u062f\u0627"
    assert untranslated_english_ratio(text) < 0.1


def test_source_map_parse(tmp_project):
    (tmp_project / "source-map.md").write_text(
        "# Source map\n\n"
        "| ch-01.md | ch-01.txt | 100 | 1000 | Overview, Method |\n"
        "| ch-02.md | ch-02.txt | 200 | 2000 | - Overview |\n",
        encoding="utf-8",
    )
    smap = source_map(tmp_project / "source-map.md")
    assert smap["ch-01.md"]["source"] == "ch-01.txt"
    assert smap["ch-01.md"]["word_min"] == 100
    assert smap["ch-01.md"]["word_max"] == 1000
    assert "Overview" in smap["ch-01.md"]["required_h2"]
    assert "Method" in smap["ch-01.md"]["required_h2"]
    assert smap["ch-02.md"]["required_h2"] == ["Overview"]


def test_source_map_missing(tmp_project):
    (tmp_project / "source-map.md").unlink()
    assert source_map(tmp_project / "source-map.md") == {}


def test_glossary_terms_basic(tmp_project):
    (tmp_project / "glossary.md").write_text(
        "| English | Arabic |\n"
        "|---|---|\n"
        "| Reflection | \u0627\u0644\u062a\u0623\u0645\u0644 (Reflection) |\n"
        "| Tool use | \u0627\u0633\u062a\u062e\u062f\u0627\u0645 \u0627\u0644\u0623\u062f\u0648\u0627\u062a |\n",
        encoding="utf-8",
    )
    terms = glossary_terms(tmp_project / "glossary.md")
    assert any("\u0627\u0644\u062a\u0623\u0645\u0644" in t for t in terms)
    assert any("\u0627\u0633\u062a\u062e\u062f\u0627\u0645" in t for t in terms)


def test_glossary_terms_skips_separator(tmp_project):
    (tmp_project / "glossary.md").write_text(
        "| English | Arabic |\n"
        "|---|---|\n"
        "| Term | \u0645\u0635\u0637\u0644\u062d |\n",
        encoding="utf-8",
    )
    terms = glossary_terms(tmp_project / "glossary.md")
    assert "\u0645\u0635\u0637\u0644\u062d" in terms
