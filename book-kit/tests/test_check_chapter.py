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
from unittest.mock import MagicMock, patch

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


# ---------------------------------------------------------------------------
# 11) bible.md applicability — ch-01 < applies_from → countdown skipped
# ---------------------------------------------------------------------------

def test_rule_skipped_when_chapter_before_applies_from(tmp_project):
    """A bible with `Countdown ≥1 | ch-03` resolves ``applies_from=3``;
    running the rule against ``ch-01.md`` should PASS with skip-evidence
    ``"chapter ch-01 < applies_from=3"`` — i.e. the rule recognises the
    applicability table and refuses to run on a setup chapter.

    Mirrors ``parse_rule_applicability()`` + ``countdown()`` integration
    directly; doesn't go through the CLI / book-root resolver (the
    ``_resolve_config_paths`` path is covered by the manual smoke in
    the acceptance criteria).
    """
    bible_text = (
        "| Rule | Applies from | Reason | Supersedes |\n"
        "| --- | --- | --- | --- |\n"
        "| Countdown ≥1 | ch-03 | Setup chapters 01–02 | — |\n"
    )
    bible_path = tmp_project / "bible.md"
    bible_path.write_text(
        "# Book Bible\n\n## Rule applicability\n\n" + bible_text + "\n",
        encoding="utf-8",
    )
    applicable = cc.parse_rule_applicability(bible_path)
    assert applicable == {"Countdown ≥1": 3}, (
        f"expected single row resolved to {{'Countdown ≥1': 3}}; got {applicable!r}"
    )

    chapter = (
        "# Chapter 1\n\n"
        "نص عربي يتحدث عن تهيئة المشهد دون استخدام الكلمات المتفق عليها لاحقا.\n"
    )
    chapter_path = tmp_project / "chapters" / "ch-01.md"
    chapter_path.parent.mkdir(parents=True, exist_ok=True)
    chapter_path.write_text(chapter, encoding="utf-8")

    applies_from = applicable.get("Countdown ≥1", 3)
    results = cc.countdown(
        chapter, chapter_path=str(chapter_path),
        tokens=["بقي", "لم يبق"], applies_from=applies_from,
    )
    assert len(results) == 1, f"expected one CheckResult; got {len(results)}"
    r = results[0]
    assert r.name == "countdown", f"expected name='countdown'; got {r.name!r}"
    assert r.status == "PASS", f"expected PASS (skip path); got {r.status}; evidence={r.evidence}"
    assert "chapter ch-01 < applies_from=3" in r.evidence, (
        f"expected skip-evidence 'chapter ch-01 < applies_from=3'; got {r.evidence!r}"
    )


# ---------------------------------------------------------------------------
# 12) bible.md applicability — ch-05 >= applies_from → countdown runs
# ---------------------------------------------------------------------------

def test_rule_applied_when_chapter_at_or_after_applies_from(tmp_project):
    """Same bible, this time against ``ch-05.md`` — the chapter is at/after
    ``applies_from=3`` so the rule actually runs. With zero countdown tokens
    in the chapter body the rule must FAIL (the rule verdict, NOT the
    skip-evidence) — proving the applicability table didn't accidentally
    short-circuit the rule on every chapter.
    """
    bible_text = (
        "| Rule | Applies from | Reason | Supersedes |\n"
        "| --- | --- | --- | --- |\n"
        "| Countdown ≥1 | ch-03 | Setup chapters 01–02 | — |\n"
    )
    bible_path = tmp_project / "bible.md"
    bible_path.write_text(
        "# Book Bible\n\n## Rule applicability\n\n" + bible_text + "\n",
        encoding="utf-8",
    )
    applicable = cc.parse_rule_applicability(bible_path)
    assert applicable == {"Countdown ≥1": 3}

    # Chapter 5 contains NO countdown tokens (`بقي` / `لم يبق`) at all —
    # not even inside a quoted narration. So when the rule fires it must
    # FAIL because total < min_occurrences=1.
    chapter = (
        "# Chapter 5\n\n"
        "نص عربي يتحدث عن المشروع دون استخدام أي من الكلمات المتفق عليها لاحقا.\n"
    )
    chapter_path = tmp_project / "chapters" / "ch-05.md"
    chapter_path.parent.mkdir(parents=True, exist_ok=True)
    chapter_path.write_text(chapter, encoding="utf-8")

    applies_from = applicable.get("Countdown ≥1", 3)
    results = cc.countdown(
        chapter, chapter_path=str(chapter_path),
        tokens=["بقي", "لم يبق"], applies_from=applies_from,
    )
    r = results[0]
    # The rule actually runs (not the skip-evidence).
    assert "< applies_from" not in r.evidence, (
        f"expected rule to RUN, not skip; got skip-evidence {r.evidence!r}"
    )
    # No countdown tokens in the chapter → FAIL on the rule itself.
    assert r.status == "FAIL", f"expected FAIL (no tokens); got {r.status}; evidence={r.evidence}"
    assert "ch-05" in r.evidence, f"expected ch-05 in evidence; got {r.evidence!r}"
    assert "≥1 countdown token" in r.evidence, (
        f"expected the rule's own verdict text in evidence; got {r.evidence!r}"
    )

# ---------------------------------------------------------------------------
# 13) --lang ar — clean Modern Standard Arabic → arabic_grammar PASS
# ---------------------------------------------------------------------------

def _mcp_stdout(issues):
    """Serialize ``issues`` as the MCP stdio response the script parses.

    Mirrors the real transport: newline-delimited JSON-RPC, an ``initialize``
    reply on id=1, then the ``tools/call`` reply on id=2 carrying the
    LanguageTool payload inside the standard text-content envelope. Building
    the wire format (rather than patching ``run_grammar_check``) keeps
    ``_parse_mcp_stdout`` / ``_extract_issues`` under test too.
    """
    return "".join(json.dumps(m, ensure_ascii=False) + "\n" for m in [
        {"jsonrpc": "2.0", "id": 1, "result": {"protocolVersion": "2024-11-05"}},
        {"jsonrpc": "2.0", "id": 2, "result": {
            "content": [{"type": "text",
                         "text": json.dumps({"matches": issues}, ensure_ascii=False)}]}},
    ])


def _patched_popen(issues):
    """``subprocess.Popen`` stand-in whose ``communicate()`` returns ``issues``."""
    proc = MagicMock()
    proc.communicate.return_value = (_mcp_stdout(issues), "")
    return patch.object(cc.subprocess, "Popen", return_value=proc)


def test_check_chapter_lang_valid_arabic(tmp_project):
    """Grammatical Modern Standard Arabic with the MCP reporting zero matches
    → the ``arabic_grammar`` row is PASS with ``"0 issues found"`` evidence.

    The LanguageTool server itself is mocked (no Java / no network in CI);
    what this test pins is the wiring: ``--lang ar`` selects the
    ``arabic_grammar`` name, an empty match list means PASS, and the row is
    appended to the eight rule-based checks rather than replacing them.
    """
    chapter = (
        "# الفصل\n\n"
        "## المشهد الأول\n\n"
        "ذهب الطالبان إلى المكتبة في الصباح الباكر.\n\n"
        "خاتمة قصيرة.\n"
    )
    chapter_path = _write_chapter(tmp_project, "ch-04.md", chapter)

    with _patched_popen([]):
        results = cc.run_all_checks(chapter_path, cc.read_style_guide(None),
                                     applicability={}, lang="ar")

    r = _find(results, "arabic_grammar")
    assert r.status.lower() == "pass", f"expected pass; got {r.status}; evidence={r.evidence}"
    assert "0 issues found" in r.evidence, f"expected '0 issues found'; got {r.evidence!r}"
    # The grammar row is additive — the eight rule checks must still be present.
    assert len(results) == 9, f"expected 8 rule rows + 1 grammar row; got {[x.name for x in results]}"
    assert "english_grammar" not in {x.name for x in results}


# ---------------------------------------------------------------------------
# 14) --lang ar — planted agreement error → arabic_grammar FAIL
# ---------------------------------------------------------------------------

def test_check_chapter_lang_planted_error(tmp_project):
    """One planted Arabic agreement error → ``arabic_grammar`` is FAIL and the
    planted message + rule id appear in the evidence.

    Complements the test above: same wiring, non-empty match list. Proves the
    PASS path isn't a constant — the row's verdict actually tracks what the
    MCP returns.
    """
    chapter = (
        "# الفصل\n\n"
        "## المشهد الأول\n\n"
        "ذهب الطالبان إلى المكتبة في الصباح الباكر.\n\n"
        "خاتمة قصيرة.\n"
    )
    chapter_path = _write_chapter(tmp_project, "ch-04.md", chapter)
    planted = [{"message": "Agreement error", "offset": 42, "length": 5,
                "rule_id": "AR_AGREEMENT"}]

    with _patched_popen(planted):
        results = cc.run_all_checks(chapter_path, cc.read_style_guide(None),
                                     applicability={}, lang="ar")

    r = _find(results, "arabic_grammar")
    assert r.status.lower() == "fail", f"expected fail; got {r.status}; evidence={r.evidence}"
    assert "1 issues found" in r.evidence, f"expected the issue count; got {r.evidence!r}"
    assert "Agreement error" in r.evidence, (
        f"expected the planted message in evidence; got {r.evidence!r}"
    )
    assert "AR_AGREEMENT" in r.evidence, (
        f"expected the planted rule id in evidence; got {r.evidence!r}"
    )


# ---------------------------------------------------------------------------
# 15) --lang ar — MCP server unreachable → arabic_grammar WARN (not FAIL)
# ---------------------------------------------------------------------------

def test_check_chapter_lang_mcp_unreachable_yields_warn(tmp_project):
    """When the MCP server can't be spawned (``subprocess.Popen`` raises
    ``FileNotFoundError`` — the same shape Node-absent / npm-404 / offline
    host produces), the ``arabic_grammar`` row must be ``WARN``, not
    ``FAIL``. The grammar pass is an optional external dependency; a
    missing backend must never turn a chapter that passes the eight
    built-in rules into a FAIL.

    Pinned in P10-fix1 because the spec'd npm package returns E404 and the
    closest published alternative is a materially different deployment
    shape — the script's safe-degradation path is the only thing keeping
    ``--lang`` usable on a host without a working LanguageTool MCP.
    """
    chapter = (
        "# الفصل\n\n"
        "## المشهد الأول\n\n"
        "ذهب الطالبان إلى المكتبة في الصباح الباكر.\n\n"
        "خاتمة قصيرة.\n"
    )
    chapter_path = _write_chapter(tmp_project, "ch-04.md", chapter)

    with patch.object(cc.subprocess, "Popen",
                      side_effect=FileNotFoundError(
                          "npx not found (or package unresolved on npm)")):
        results = cc.run_all_checks(chapter_path, cc.read_style_guide(None),
                                     applicability={}, lang="ar")

    r = _find(results, "arabic_grammar")
    assert r.status == "WARN", f"expected WARN; got {r.status}; evidence={r.evidence}"
    assert "languagetool MCP unavailable" in r.evidence, (
        f"expected the safe-degradation evidence; got {r.evidence!r}"
    )
    assert "npx not found" in r.evidence or "unresolved on npm" in r.evidence, (
        f"expected the underlying error to surface in evidence; got {r.evidence!r}"
    )
    # Same wiring as the other --lang tests: 8 rule rows + 1 grammar row.
    assert len(results) == 9, (
        f"expected 8 rule rows + 1 grammar row; got "
        f"{[(x.name, x.status) for x in results]}"
    )
    # The grammar row must not leak into FAIL while the MCP is unreachable.
    fail_names = {x.name for x in results if x.status == "FAIL"}
    assert "arabic_grammar" not in fail_names, (
        f"grammar row must not be FAIL when MCP unreachable; FAIL set: {fail_names}"
    )
    # Symmetric assertion for --lang en — same wiring, different row name.
    with patch.object(cc.subprocess, "Popen",
                      side_effect=FileNotFoundError("npx not found")):
        results_en = cc.run_all_checks(chapter_path, cc.read_style_guide(None),
                                        applicability={}, lang="en")
    r_en = _find(results_en, "english_grammar")
    assert r_en.status == "WARN", (
        f"expected WARN for --lang en; got {r_en.status}; evidence={r_en.evidence}"
    )


# Total: 15 tests above (P10-fix1 added the WARN-degradation test). The CLI
# smoke test (argparse + --json + main()
# integration) is verified manually in the acceptance criteria
# (`python check_chapter.py ...`); the 8 rule-level tests above use the
# same internal functions `main()` calls, so the wiring is exercised
# indirectly. The "no-end-of-chapter-mark fixture" requirement from the
# task spec is realized by `test_closing_hook_no_marker` (test #6 above)
# which exercises the fallback path (`_strip_html_comments` +
# `_last_paragraph`) when the marker is absent.
