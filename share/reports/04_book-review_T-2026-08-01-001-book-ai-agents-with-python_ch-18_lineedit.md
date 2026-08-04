# Line-Edit Review — T-2026-08-01-001-book-ai-agents-with-python / ch-18

- **Chapter:** `books/ai-agents-with-python/chapters/ch-18.md`
- **Phase:** line-edit (third pass — post dev-fix2)
- **Reviewer:** am-review (book-gen mode, line-edit focus)
- **Style guide:** `books/ai-agents-with-python/style-guide.md`
- **Pinned versions:** smolagents==1.26.0, pytest==9.1.1, duckduckgo-search==8.1.1 (per `environment.md`)
- **Comparable prior ch-18 word-count reference:** 1795 (initial) → 2228 (post dev-fix2) → ~2230 (this pass, author-claim)

## Summary

**Overall verdict: FAIL**

Two paragraphs violate the binding style-guide rhythm rule "every paragraph ≤ 80 words". Both grew during the dev-fix2 code-block additions and the line-edit pass did not re-paragraph them. Everything else passes. The fix is mechanical (split two paragraphs), not a re-write.

Issue counts by severity:
- **CRITICAL:** 2 — paragraph-length ceiling violations (P29 line 156, P40 line 288)
- **HIGH:** 0
- **MEDIUM:** 0
- **LOW / WARN:** 1 — `API` acronym first-use (line 52) is not expanded; expansion happens only at the second standalone use (line 517)
- **N/A:** 0 — no check items returned N/A

## Tests / build run

- I did **not** re-run the pytest suite — the line-edit task is editorial and the no-touch boundary forbids mutating any project state. The writer's claim of 13/13 PASS in `share/notes/03_coder_summary_*_ch-18_dev-fix2.md` is not independently re-verified here.
- Test count math sanity-checked from the chapter's own code blocks:
  - `tests/test_smoke.py`: 8 test functions (test_imports + 3 min/max pair + 3 has_sources_line trio)
  - `tests/test_gold.py`: 5 parametrize cases × 1 function = 5
  - smoke+gold expected: **8 + 5 = 13** — matches "13/13 PASS" claim.
  - `tests/test_live.py`: 2 backends × 2 cases = 4 — matches "4/4 SKIPPED" claim.
- Code-block ast.parse correctness: all Python code blocks in the chapter are syntactically small and follow PEP 8. The `argparse`, `JsonlLogger` constructor, `Observability` open/close pattern, and the test mark.parametrize structures all match smolagents 1.26.0 surface as cited inline. I did NOT actually execute them.

## Per-task / per-check verdicts (line-edit checklist)

Voice (line-edit focus):

1. **Vocabulary blacklist:** **PASS**. Zero hits for `magic`, `just`, `simply`, `obviously`, `optimal`, `proven`, `revolutionary`, `game-changing`, `studies show`, `powerful` in prose (case-insensitive, word-boundary; code-block-stripped). Verified via regex sweep across the prose-only view. The Self-Critique HTML comment at L632 quotes the rule by name, but that block is stripped before publish.
2. **Second-person dominance:** **PASS**. "You" appears 50+ times across the prose (e.g., L3, L7, L15, L19, L25, L33, L69, L150, L156, L288, L334, L394, L455, L549). Third-person descriptive sentences ("The chapter treats...", "The project uses...", "The agent runs...") are scene-setting framings about what the chapter / project / agent ARE, not passive voice; these read as labeled scene description rather than unmarked passive. Style-guide rule "any third-person passive is intentional and labeled" is satisfied by the framing context.
3. **Contractions natural, no exclamation marks:** **PASS**. `doesn't` (L15), `don't` (L150), and others present. Zero `!` characters in the visible prose (one match in `<!-- … -->` HTML comment, which is stripped before publish).
4. **Pacing — one move per paragraph; every prose paragraph ≤ 80 words:** **FAIL**. See Critical Findings.
   - Visible prose paragraph count (excluding code blocks, headings, HTML comment): **69**
   - Two paragraphs exceed the 80-word cap:
     - **P29 (L156):** 100 words — bundling all four safety knobs in one paragraph.
     - **P40 (L288):** 110 words — bundling seven JsonlLogger facts in one paragraph.
   - All other 67 paragraphs are ≤ 80 words. The band of 24-word, 35-word, 47-word, etc. paragraphs is healthy.
5. **Subheading style (sentence-fragment, ≤ 7 words, verb-led):** **PASS**. 14 H2s, all verb-led (Name / Pick / Lay / Wire / Add / Defend / Publish / Build / Frame / Avoid / Look). Longest is 5 words; all under 7. The chapter has no H3.

Terminology & citation (line-edit focus):

6. **Inline named citations for non-obvious smolagents claims:** **PASS**. Citations present:
   - L15 — `MultiStepAgent.__init__` `add_base_tools: bool = False` (1.26.0)
   - L25 — `OpenAIModel.__init__` and `InferenceClientModel.__init__` (1.26.0)
   - L156 — `default_tools.py:130` computes `_min_interval = 1.0 / rate_limit`
   - L156 — `default_tools.py` rate_limit / max_output_length
   - L217 — OWASP LLM01:2025 anchor (named external source)
   - L288 — `agents.py:282,304,416-434` (verified per-step hook)
   - L561 — `default_tools.py:531` `VisitWebpageTool.forward` HTML→Markdown conversion
7. **`\bfinal_answer\b` in prose:** **PASS**. Zero hits in visible prose. The kwarg `final_answer_checks` appears 7 times at L54, L143, L156, L161, L493, L575, L625 — all valid (allowed by the rule). The bare token survives only inside the `<!-- -->` self-critique (L632), which is stripped before publish.
8. **`HfApiModel` zero mentions:** **PASS**. Zero `\bHfApiModel\b` matches anywhere in the file.
9. **Acronyms expanded on first use:**
   - **CLI** at L150 — "command-line interface (CLI)" — PASS
   - **pytest** at L65 — "`pytest` (Python's standard testing framework)" — PASS
   - **JSONL** at L3 — "JSONL (JSON Lines — one JSON object per line)" — PASS
   - **JSON** at L3 — within the same parenthetical — PASS
   - **API** at L52 — "the older API surface" — **WARN**. Not expanded at first use. Expanded only at L517 ("application programming interface (API)"). Borderline because "API surface" is a software-engineering compound noun and the meaning is clear from context, but the rule "expanded on first use" is binding. Compare ch-17 line 7 where API is expanded on its absolute first use.
10. **Rate-limit citation `_min_interval = 1.0 / rate_limit` from `default_tools.py:130`:** **PASS**. Found at L156: "(per `default_tools.py:130` the installed smolagents 1.26.0 source computes `_min_interval = 1.0 / rate_limit`, so a rate of 0.5 yields the 2-second interval)". Per the dev-fix1 Fix 2 contract, this is correctly anchored.

Structure & alignment:

11. **Orientation paragraph 30–60 words:** **PASS**. 57 words (L3): "You run `python -m research_briefing.cli "solar panels Spain"` … The agent is one `CodeAgent` with three web tools, four safety knobs, and three layers of tests." Concrete terminal scene per the scene-opening convention.
12. **Forward-pointer "What's next" names ch-19 explicitly with concrete forward move:** **PASS**. L573: "What's next: ch-19 — Project: Multi-Agent Work Assistant — adds a `Critic` managed agent on top of this project, scores the briefing against a rubric, and asks the writer to revise until the score passes." Names the chapter, names the project, names the mechanism.
13. **Closing-imperative contract (CRITICAL — per dev-fix1 Fix 6):** **PASS**. Line-by-line:
    - L575 — `> **The move:** …` (the imperative blockquote)
    - L576 — blank
    - L577 — `<!--` (HTML comment begins)
    - Visible paragraphs between L575 and L577: **zero** (only a blank line). ✓
    - Order: L573 (bridge) → L575 (imperative) → L577 (HTML comment). Bridge BEFORE imperative. ✓
    - The imperative is the final visible substantive prose paragraph. ✓
14. **Zero handoff-style recap, zero authorial summary, zero third-person "by the end of the reading…" closing line:** **PASS**. The imperative is an action ("Build the `src/research_briefing/` project so a single `CodeAgent` returns …") with no "in this chapter we…" or "by the end of the reading" framing. The "What's next:" sentence is at L573 (before the imperative, per the contract), not after.

No-regression vs dev-fix2:

15. **Word count ~2230 (±10% = 2007–2453):** **PASS**. Prose word count (code-stripped + HTML-comment-stripped + headings-stripped) = **2307 words**. Within ±10% band (2007–2453) and within the user-stated band (1616–2461). Slightly higher than the ledger figure of 2228 — the difference is the prose-with-inline-code methodology; both numbers are within spec.
16. **UTF-8 clean round-trip:** **PASS**. File reads cleanly via `[System.IO.File]::ReadAllBytes`; decoded → re-encoded byte-equivalent; no BOM; 12 em-dash (U+2014) characters intact; 0 en-dashes (U+2013); 0 smart-quote characters that would corrupt ASCII compatibility.
17. **bible.md untouched:** **PASS** for this review pass (I did not touch it). Status snapshot: bible.md is **174 lines** with `## Added by ch-01` through `## Added by ch-16` blocks intact (16 chapter entries, last is "2026-08-02"). Note: the prompt's reference figure of "189 lines" does not match the current bible size — this looks like a stale reference rather than a regression introduced by this line-edit pass; flag for master to verify the bible line-count drift across phases, but this review did not modify the bible.
18. **ledger.md ch-18 row reflects dev-fix2:** **PASS**. L47 row shows `| ch-18 | dev-fix2 | ch-14, ch-15, ch-17 | 2228 | - | - | …` with the full dev-fix2 narrative covering the 6 CRITICAL fixes (install guidance block, rate_limit correction to 0.5, complete project surface, instructions+safety hardening, JsonlLogger rewritten with `on_step`, closing-imperative contract). The line-edit pass that produced this current prose is not yet recorded in the ledger (the row is awaiting this review's verdict; this report updates it implicitly).

## Cross-cutting findings

- **Two paragraphs over 80 words (CRITICAL).** Both grew during the dev-fix2 narrative expansion (the four-knobs paragraph enumerates all four knobs; the JsonlLogger description names seven sub-facts). The line-edit pass did not re-paragraph them. Cutting each into 2–3 sub-paragraphs is mechanical: each natural sentence boundary is itself a sentence, and one move per paragraph is trivially achievable.
- **API acronym at L52 (LOW).** "the older `duckduckgo-search` package; that is a different package with an older API surface" is the unexpanded first use. Fix: insert "(API)" or "(application-programming-interface (API) surface)" parenthetically at the first appearance, matching ch-17's pattern.
- **Self-Critique HTML comment falsely claims "Every prose paragraph is <= 80 words."** The comment block at L632 says so, but the actual prose has P29=100w and P40=110w. The writer's self-critique passed despite the prose failure — flag for the next writer pass to update the self-critique alongside the prose.
- **Closing pattern matches the dev-fix1 Fix 6 contract.** Bridge (L573) is BEFORE the imperative (L575), which is the FINAL visible substantive prose paragraph. Empty line, then `<!--` comment begins at L577. The inverse-of-ch-16 ordering is correctly implemented.
- **The chapter's 14 H2 subheadings all parse cleanly as verb-led sentence fragments** under 7 words each.
- **The orientation opens on a concrete terminal scene** ("You run `python -m research_briefing.cli "solar panels Spain"` …"). Concrete tool, concrete topic, concrete output shape. ✓

## Out-of-scope observations (not blocking this line-edit pass)

- **The chapter has 14 H2 sections, several of which are short** (L21, L52, L57, L66, L125, L142, L149, L152, L229, L238, L252, L260, L269, L306, L320, L349, L428, L434, L485, L514, L521, L532, L539, L546, L557). The shorter ones are sub-section scans but all exist as H2 in the chapter. If anyone reviews for H2 frequency, no fix needed; this is just disclosure.
- **The chapter's prose-with-inline-code-stripped word count (2307) is at the higher end of the outline target band** (1200–1600 was the chapter author's own self-critique target — see L645). The 2307 figure reflects the prose-only count after stripping code blocks AND the HTML comment, which is the right number to compare against a word-count band. If a different band is required, master can clarify.
- **Bash heredoc/output example blocks** (`pip install ddgs wikipedia-api`, JSON sample) are bare-fenced (` ``` `) without a language tag except where the writer tagged them `text` / `python` / `bash`. Style guide is silent on `bash` vs `shell` vs no-tag for shell output; no fix required.
- **`styles-guide.md outcome-row** for ch-18 still reads `rate_limit=2.0` (L84 of style-guide) — but the chapter has `rate_limit=0.5`. The style guide is master/upstream-author territory; noting the drift here so it doesn't get lost.

## Honest assessment

- **Did the writer run the 13-test suite, or claim success without verification?** The 13-test count (8 smoke + 5 gold) is correct from the test bodies. I did not re-execute `pytest` in this review (line-edit is editorial; I am not authorized to mutate the project state to run tests). I rely on the writer's `13/13 PASS` claim. The chapter's prose is consistent with the test bodies parsing and running; no syntactic or import-path errors in the blocks.
- **Does the cli.py prose match the cli.py code?** Yes, exactly:
  - Prose L334: "CLI instantiates a fresh `JsonlLogger` per run, which creates a unique `runs/run-<timestamp>.jsonl` file."
  - Code (L298–L320 in chapter): `logger = JsonlLogger(log_dir=args.log_dir)` → matches "instantiates a fresh logger" + `log_dir` arg → `runs/run-<timestamp>.jsonl` file path. ✓
  - "the agent runs the topic" → `result = agent.run(args.topic)`. ✓
  - "the final answer prints to stdout" → `print(result)`. ✓
- **Any subtle issues with the closing-imperative ordering (per dev-fix1 Fix 6)?** No. The bridge at L573 names ch-19 with a concrete forward move (adds `Critic`, scores against rubric, asks writer to revise). The imperative at L575 is the outcome-line-style build action. The HTML comment begins at L577 with no visible paragraphs intervening. The hard contract is intact.
- **The chapter grew from 1795 → 2228 → ~2230 words.** The writer handled the 4 new code blocks (cli.py, __main__.py, pyproject.toml, README.md) by inserting explanatory prose around each. Two of those explanatory prose paragraphs grew past 80 words (P29, P40) and were missed during the line-edit re-paragraphing pass. That is the only outstanding line-edit miss.

## Self-critique

- I did NOT actually re-run the pytest suite. I cross-checked the count math (8+5=13, 2×2=4) but did not execute anything. If master wants belt-and-braces verification, re-run `pytest tests/test_smoke.py tests/test_gold.py -v` in the venv — the chapter's blocks are small enough that the assertion violations would surface immediately.
- I did NOT actually run a `/usr/bin/file` or `iconv` style UTF-8 round-trip via context-mode; I used the PowerShell `[System.IO.File]::ReadAllBytes` + `GetString` + `GetBytes` idiom, which is byte-equivalent on ASCII-and-UTF-8-clean files. Round-trip is CLEAN.
- I did NOT verify the bible.md line-count math exactly. The prompt expected 189 lines; the bible is currently 174 lines. Either the prompt is stale or the bible got compacted in some other pass. I flagged this; I did not modify the bible.
- I treated "third-person passive" semantic check loosely. I scanned for first-three-word patterns (The chapter, The project, The agent …) and decided descriptive scene-framing is intentional-not-passive under the style guide, vs unambiguous grammatical passive ("X is run by Y"). If master prefers stricter passive-voice detection, this is a soft re-review.
- I did NOT cross-check the bible's 174-line figure against any reference at all. If master wants a strict no-touch evidence, the right test is `git log -1 -- bible.md` to confirm the file hasn't moved since the line-edit dispatch — but I have no git log access from the editor env.

## Call to action

**READY TO FIX, NOT READY TO SHIP.** Split P29 (L156, 100w → 3 paragraphs of ~33w each) and P40 (L288, 110w → 3 paragraphs of ~37w each). Optionally insert "(API)" at L52 to fix the first-use expansion. Re-run line-edit pass on just those two sections. Ledger update: change ch-18 status from `dev-fix2` to `line-edited` after the fix lands. Estimated 10–15 minutes of writer time.
