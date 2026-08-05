"""Tests for fix_source_urls.py — pdftotext URL/line artifact repair."""
from pathlib import Path

from fix_source_urls import (
    URL_DOUBLED_SEG_RE,
    URL_TRAILING_DOTDOT_RE,
    URL_TRAILING_HASH_RE,
    URL_TRAILING_PAGENUM_RE,
    fix_all,
    fix_doubled_segments,
    fix_pure_digit_lines,
    fix_trailing_dotdot,
    fix_trailing_hash,
    fix_trailing_page_numbers,
    fix_truncated_urls,
)


def test_self_check_passes():
    """The --self-check mode in __main__ must complete without error."""
    import subprocess
    import sys
    r = subprocess.run(
        [sys.executable, str(Path(__file__).parent.parent / "book_workflow" / "scripts" / "fix_source_urls.py"), "--self-check"],
        capture_output=True, text=True, timeout=30,
    )
    assert r.returncode == 0, r.stderr
    assert "self-check OK" in r.stdout


def test_drop_pure_digit_page_number():
    lines = [
        "1. Source, https://example.com/foo",
        "28",
        "",
        "2. Another, https://example.com/bar",
    ]
    out, dropped = fix_pure_digit_lines(lines)
    assert dropped == 1
    assert "28" not in out
    assert any("https://example.com/foo" in line for line in out)
    assert any("https://example.com/bar" in line for line in out)


def test_drop_only_after_url_line():
    """A pure-digit line that's NOT after a URL must be preserved (e.g. part of TOC)."""
    lines = [
        "Chapter 1",
        "28",  # not after URL
    ]
    out, dropped = fix_pure_digit_lines(lines)
    assert dropped == 0
    assert out == lines


def test_strip_trailing_page_number():
    lines = [
        "1. Skill Boost, https://www.cloudskillsboost.google/6",
        "2. Other, https://www.tbench.ai/5",
    ]
    out, fixed = fix_trailing_page_numbers(lines)
    assert fixed == 2
    assert "https://www.cloudskillsboost.google" in out[0]
    assert "/6" not in out[0]
    assert "https://www.tbench.ai" in out[1]
    assert "/5" not in out[1]


def test_strip_trailing_page_number_multisegment():
    """`/a/b/c/14` should strip only the trailing `/14`, not an interior slash."""
    lines = ["See https://example.com/a/b/c/14"]
    out, fixed = fix_trailing_page_numbers(lines)
    assert fixed == 1
    assert "https://example.com/a/b/c" in out[0]


def test_keep_arxiv_legitimate_digits():
    """`https://arxiv.org/abs/1706.03762` must NOT be touched (5-digit suffix)."""
    lines = ["See https://arxiv.org/abs/1706.03762"]
    out, fixed = fix_trailing_page_numbers(lines)
    assert fixed == 0
    assert "https://arxiv.org/abs/1706.03762" in out[0]


def test_strip_doubled_segment():
    lines = ["Reference https://www.langchain.com/langgraphlanggraph"]
    out, fixed = fix_doubled_segments(lines)
    assert fixed == 1
    assert "https://www.langchain.com/langgraph" in out[0]
    assert "langgraphlanggraph" not in out[0]


def test_keep_legitimate_whitepaper_foo():
    """`whitepaper-foo` must NOT be mistakenly deduped to `whitepaper-f`."""
    lines = ["Reference https://www.example.com/whitepaper-foo"]
    out, fixed = fix_doubled_segments(lines)
    assert fixed == 0
    assert "https://www.example.com/whitepaper-foo" in out[0]


def test_strip_trailing_dotdot():
    lines = ["See https://www.trickle.so/blog/how-to-build-google-a2a-project.."]
    out, fixed = fix_trailing_dotdot(lines)
    assert fixed == 1
    assert "project." in out[0]
    assert "project.." not in out[0]


def test_strip_trailing_hash_keeps_slash():
    lines = ["Profile https://www.linkedin.com/in/marco-fago/#"]
    out, fixed = fix_trailing_hash(lines)
    assert fixed == 1
    assert "https://www.linkedin.com/in/marco-fago/" in out[0]
    assert "fago/#" not in out[0]


def test_join_truncated_url():
    lines = [
        "See https://www.businesstoday.in/tech-today/news/story/30-of-microsofts-code-is-now-ai",
        "-generated-says-ceo-satya-nadella-474167-2025-04-30",
    ]
    out, joins = fix_truncated_urls(lines)
    assert joins == 1
    assert "https://www.businesstoday.in/tech-today/news/story/30-of-microsofts-code-is-now-ai-generated-says-ceo-satya-nadella-474167-2025-04-30" in out[0]


def test_join_skips_pure_digit_next_line():
    """A URL followed by a pure-digit line must NOT be joined (page number)."""
    lines = [
        "See https://www.example.com/foo",
        "28",
    ]
    out, joins = fix_truncated_urls(lines)
    assert joins == 0
    assert "https://www.example.com/foo" in out[0]
    assert out[1] == "28"


def test_fix_all_idempotent():
    text = (
        "References\n"
        "1.\u200b Example, https://www.example.com/whitepaper-foo\n"
        "28\n"
        "2.\u200b Another, https://www.cloudskillsboost.google/6\n"
    )
    new_text, counts = fix_all(text)
    # Run again on the fixed output — should be no-op.
    again, counts2 = fix_all(new_text)
    assert all(v == 0 for v in counts2.values()), f"idempotency failed: {counts2}"
    assert new_text == again


def test_fix_all_combined():
    text = (
        "References\n"
        "1.\u200b Skill Boost, https://www.cloudskillsboost.google/6\n"
        "2.\u200b Profile, https://www.linkedin.com/in/marco-fago/#\n"
        "28\n"
    )
    new_text, counts = fix_all(text)
    assert counts["stripped_trailing_page_nums"] == 1
    assert counts["stripped_trailing_hash"] == 1
    assert counts["dropped_digit_lines"] == 1
    assert "https://www.cloudskillsboost.google" in new_text
    assert "https://www.linkedin.com/in/marco-fago/" in new_text
    assert "28" not in new_text.split("\n")  # the pure-digit line is gone
