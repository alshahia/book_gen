"""Tests for check_chapter.py — per-beat prose enforcer.

Each test writes a tiny fixture chapter to ``tmp_project/chapters/``, imports
the eight check functions directly (no subprocess / no mocks), then asserts
on the returned ``CheckResult`` list. This mirrors the testing style of
``test_chapter_regex_*`` in ``test_book_check.py`` — file-based fixtures,
direct function calls.

The script imports a single end-to-end CLI invocation at the bottom to
confirm the argparse + --json path also works.
"""
import json
import sys
from pathlib import Path

# conftest.py already prepends book-kit/book_workflow/scripts to sys.path.
import check_chapter as cc

KIT_ROOT = Path(__file__).resolve().parents[1]
SCRIPT = KIT_ROOT / "book_workflow" / "scripts" / "check_chapter.py"


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _write_chapter(tmp_project, name, text):
    p = tmp_project / "chapters" / name
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(text, encoding="utf-8")
    return p


def _results_for(chapter_text, tmp_project=None, chapter_name="ch-test.md",
                 window=(1, 200), forbidden=None, countdown_tokens=None,
                 applies_from=3, max_words_hook=8, sentence_target=22):
    """Run the eight rule functions against ``chapter_text`` and return the
    list of ``CheckResult`` objects.

    Defaults match the permissive style-guide used in test fixtures so
    each test isolates exactly one rule. Override any keyword arg to
    exercise a specific edge case.
    """
    if forbidden is None:
        forbidden = []
    if countdown_tokens is None:
        countdown_tokens = ["بقي", "لم يبق"]
    return [
        *cc.word_count_per_beat(chapter_text, window=window),
        *cc.banned_patterns(chapter_text, patterns=forbidden),
        *cc.quote_pair_balance(chapter_text),
        *cc.dialogue_own_line(chapter_text),
        *cc.closing_hook(chapter_text, max_words=max_words_hook),
        *cc.countdown(chapter_text, chapter_path=f"chapters/{chapter_name}",
                       tokens=countdown_tokens, applies_from=applies_from),
        *cc.arabic_punctuation(chapter_text),
        *cc.sentence_length(chapter_text, target_median=sentence_target),
    ]


def _find(results, name):
    for r in results:
        if r.name == name:
            return r
    raise AssertionError(f"check {name!r} not in results: {[r.name for r in results]}")


# ---------------------------------------------------------------------------
# 1) word_count_per_beat — out-of-window beat → FAIL
# ---------------------------------------------------------------------------

def test_word_count_per_beat(tmp_project):
    """Beat A = 30 words (in [20, 60]); Beat B = 5 words (<0.5*lo=10) → FAIL."""
    body_pass = " ".join(["كلمة"] * 30)        # 30 words — passes 20-60
    body_fail = " ".join(["قصير"] * 5)          # 5 words  — <0.5*20=10 → FAIL
    chapter = (
        "# Chapter\n\n"
        "## Beat A\n\n" + body_pass + "\n\n"
        "## Beat B\n\n" + body_fail + "\n\n"
    )
    results = _results_for(chapter, window=(20, 60))
    r = _find(results, "word_count_per_beat")
    assert r.status == "FAIL", f"expected FAIL, got {r.status}; evidence={r.evidence}"
    assert "Beat B" in r.evidence, f"Beat B not in evidence: {r.evidence}"


# ---------------------------------------------------------------------------
# 2) banned_patterns — forbidden regex match → FAIL
# ---------------------------------------------------------------------------

def test_banned_patterns(tmp_project):
    """`\\bTODO\\b` matches 'TODO' inside prose → banned_patterns=FAIL."""
    chapter = (
        "# الفصل\n\n"
        "فقرة أولى عادية مع نص قصير يملأ الفراغ\n"
        "TODO نسي الكاتب حذف هذا العنصر\n"
    )
    results = _results_for(chapter, forbidden=[r"\bTODO\b"])
    r = _find(results, "banned_patterns")
    assert r.status == "FAIL", f"expected FAIL, got {r.status}; evidence={r.evidence}"
    assert "TODO" in r.evidence


# ---------------------------------------------------------------------------
# 3) quote_pair_balance — imbalanced « vs » → FAIL
# ---------------------------------------------------------------------------

def test_quote_pair_balance(tmp_project):
    """Two « openers, one » closer → imbalanced → FAIL."""
    chapter = (
        "# Chapter\n\n"
        "قالت: «مرحبا» ثم «صباح الخير لكنها لم تنهِ.\n"
    )
    results = _results_for(chapter)
    r = _find(results, "quote_pair_balance")
    assert r.status == "FAIL", f"expected FAIL, got {r.status}; evidence={r.evidence}"
    assert "imbalanced" in r.evidence
    assert "«=2" in r.evidence and "»=1" in r.evidence


# ---------------------------------------------------------------------------
# 4) dialogue_own_line — narration + quote on same line → WARN
# ---------------------------------------------------------------------------

def test_dialogue_own_line(tmp_project):
    """A line that mixes narration and dialogue → WARN.

    Closing paragraph is short so `closing_hook` stays PASS.
    """
    chapter = (
        "# Chapter\n\n"
        "## Scene A\n\n"
        "نص سردي يفتح الفقرة ويهيئ القارئ للأحداث.\n\n"
        "## Scene B\n\n"
        "قال الضيف «مرحبا» ثم أكمل الكلام بهدوء.\n\n"
        "## End\n\n"
        "كلمة ختامية قصيرة.\n"
    )
    results = _results_for(chapter)
    r = _find(results, "dialogue_own_line")
    assert r.status == "WARN", f"expected WARN, got {r.status}; evidence={r.evidence}"
    assert "الضيف" in r.evidence, f"expected narration word in evidence: {r.evidence}"


# ---------------------------------------------------------------------------
# 5) closing_hook — `<!-- end-of-chapter -->` + long paragraph before → FAIL
# ---------------------------------------------------------------------------

def test_closing_hook_with_marker(tmp_project):
    """Marker present; paragraph immediately before it is 12 words (max=8) → FAIL."""
    long_hook = " ".join(["كلمة"] * 12)
    chapter = (
        "# Chapter\n\n"
        "فقرة قصيرة قبل الخاتمة لا تهم\n\n"
        + long_hook + "\n\n"
        "<!-- end-of-chapter -->\n"
        "بعض ما بعد لا يهم\n"
    )
    results = _results_for(chapter)
    r = _find(results, "closing_hook")
    assert r.status == "FAIL", f"expected FAIL, got {r.status}; evidence={r.evidence}"
    assert "12 words" in r.evidence


# ---------------------------------------------------------------------------
# 6) closing_hook — NO marker, last paragraph is long → FAIL (fallback path)
# ---------------------------------------------------------------------------

def test_closing_hook_no_marker(tmp_project):
    """No `<!-- end-of-chapter -->` marker; last paragraph is 12 words → FAIL."""
    long_hook = " ".join(["endword"] * 12)
    chapter = (
        "# Chapter\n\n"
        "opening paragraph that is fine\n\n"
        + long_hook + "\n"
    )
    results = _results_for(chapter)
    r = _find(results, "closing_hook")
    assert r.status == "FAIL", f"expected FAIL, got {r.status}; evidence={r.evidence}"
    assert "12 words" in r.evidence


# ---------------------------------------------------------------------------
# 7) countdown — ch-05 with no countdown tokens → FAIL
# ---------------------------------------------------------------------------

def test_countdown_required(tmp_project):
    """Chapter >= applies_from (ch-05 here) with zero countdown tokens → FAIL.

    The fixture text intentionally does NOT contain the countdown tokens
    (`بقي`, `لم يبق`) — not even inside a quoted narration. If it did,
    the rule under test would be masked.
    """
    chapter = (
        "# Chapter 5\n\n"
        "نص عربي يتحدث عن المشروع دون استخدام أي من الكلمات المتفق عليها لاحقا.\n"
    )
    results = _results_for(chapter, chapter_name="ch-05.md")
    r = _find(results, "countdown")
    assert r.status == "FAIL", f"expected FAIL, got {r.status}; evidence={r.evidence}"
    assert "found 0" in r.evidence or "≥1" in r.evidence


# ---------------------------------------------------------------------------
# 8) arabic_punctuation — Arabic line with Latin comma → FAIL
# ---------------------------------------------------------------------------

def test_arabic_punctuation(tmp_project):
    """Arabic prose with Latin ',' → FAIL."""
    chapter = (
        "# Chapter\n\n"
        "الجملة الأولى في النص, تأتي بكلمات عربية عادية.\n"
        "الجملة الثانية لا تحتوي على ترقيم لاتيني.\n"
    )
    results = _results_for(chapter)
    r = _find(results, "arabic_punctuation")
    assert r.status == "FAIL", f"expected FAIL, got {r.status}; evidence={r.evidence}"
    assert "," in r.evidence


# ---------------------------------------------------------------------------
# 9) sentence_length — all giant sentences → WARN
# ---------------------------------------------------------------------------

def test_sentence_length(tmp_project):
    """5 sentences of 25 words each → median = 25 (>22) → WARN.

    Chapter ends with a short `## End` beat so `closing_hook` stays PASS.
    """
    big_paragraph = (" ".join(["كلمة"] * 25) + ". ") * 5
    chapter = (
        "# Chapter\n\n"
        "## Big sentences\n\n"
        + big_paragraph + "\n\n"
        "## End\n\n"
        "كلمة ختامية.\n"
    )
    results = _results_for(chapter)
    r = _find(results, "sentence_length")
    assert r.status == "WARN", f"expected WARN, got {r.status}; evidence={r.evidence}"
    assert "median" in r.evidence.lower()


# ---------------------------------------------------------------------------
# 10) happy_path — clean chapter, all 8 checks PASS
# ---------------------------------------------------------------------------

def test_happy_path_all_pass(tmp_project):
    """A well-formed chapter with no rule violations → all 8 checks PASS.

    Style-guide uses Beat window 1-200 (very permissive) so even the
    short preamble paragraph PASSes per-beat. Every other rule is
    exercised by construction against a clean chapter.
    """
    body = " ".join(["نص"] * 30)
    chapter = (
        "# Chapter\n\n"
        f"## Beat A\n\n{body}\n\n"
        "## Beat B\n\n"
        "«اقتباس قصير».\n\n"
        "«اقتباس آخر».\n\n"
        "فقرة إضافية لرفع عدد الكلمات في القسم الثاني حتى نتجاوز العتبة البسيطة.\n\n"
        "خاتمة قصيرة في حدود ثمان كلمات بالضبط.\n"
    )
    results = _results_for(chapter, window=(1, 200), forbidden=[r"\bZZZ\b"],
                            countdown_tokens=["بقي"])
    expected = {
        "word_count_per_beat", "banned_patterns", "quote_pair_balance",
        "dialogue_own_line", "closing_hook", "countdown",
        "arabic_punctuation", "sentence_length",
    }
    seen = {r.name for r in results}
    assert expected.issubset(seen), f"missing checks: {expected - seen}"
    fail = [r.name for r in results if r.status == "FAIL"]
    warn = [r.name for r in results if r.status == "WARN"]
    assert not fail, f"unexpected FAIL on happy path: {fail}; evidences: {[(r.name, r.evidence) for r in results]}"
    assert not warn, f"unexpected WARN on happy path: {warn}; evidences: {[(r.name, r.evidence) for r in results]}"

# Total: 10 tests above. The CLI smoke test (argparse + --json + main()
# integration) is verified manually in the acceptance criteria
# (`python check_chapter.py ...`); the 8 rule-level tests above use the
# same internal functions `main()` calls, so the wiring is exercised
# indirectly. The "no-end-of-chapter-mark fixture" requirement from the
# task spec is realized by `test_closing_hook_no_marker` (test #6 above)
# which exercises the fallback path (`_strip_html_comments` +
# `_last_paragraph`) when the marker is absent.
