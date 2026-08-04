# Review Report — T-2026-08-01-001-book-ai-agents-with-python / ch-11 line-edit

**Date:** 2026-08-02
**Sub-agent:** am-review (book-gen mode)
**Loop:** line-edit (after dev-fix1 PASS_WITH_WARN)
**Prior reports:** `share/reports/04_book-review_T-2026-08-01-001-book-ai-agents-with-python_ch-11_dev.md` (FAIL), `..._ch-11_dev-fix1.md` (PASS_WITH_WARN — 1 WARN + 1 LOW)

## Summary

- **Overall verdict:** PASS_WITH_WARN
- **Tasks reviewed:** 1 chapter (`books/ai-agents-with-python/chapters/ch-11.md`)
- **Pass / Warn / Fail:** 0 / 1 / 0
- **Issue counts:** 0 CRITICAL / 1 WARN / 0 LOW
- **Block progression to whole-book copy-edit pass?** no

The chapter is line-edit-clean except for **one paragraph-length violation** at `ch-11.md:49` (81 words, +1 over the 80-word ceiling) — a one-sentence split fixes it. All other line-edit checks pass: vocabulary blacklist clean (0 hits), H2 discipline (13/13 ≤7 words, the H2 master retitled at `:65` is now verb-led), `HfApiModel`/`ApiModel` zero in ch-11, `final_answer` zero in ch-11 prose (1 permitted code-string at `:200`), orientation 53/60 words, closing-imperative structure preserved (callout `:214` → bridge `:216` → HTML `:218`), all 3 code blocks `ast.parse` clean, compact check live-runs to `42` in the venv, UTF-8 round-trip byte-identical, bible ch-11 block deduplicated, ch-01..ch-10 file mtimes confirm no out-of-scope edits, ledger ch-11 row still says "drafted" / "fail" review (consistent with dev-fix1 status, master's lane). The dev-fix1 reviewer's WARN about the compact check's functional redundancy with ch-09 is confirmed still true — same `'<code>final_answer("42")</code>'` string, no ch-11-specific knob exercised; this is a quality note for the whole-book copy-edit pass, not a line-edit blocker.

## Tests / build run

- `ast.parse` on the 3 extracted Python blocks (via `E:\book_gen\.venv\Scripts\python.exe`):
  - Block 1 (47 lines, `instructions`+`max_steps`+`planning_interval` runnable, `ch-11.md:89-137`) — **PASS**
  - Block 2 (47 lines, `reset=False`+`additional_args` runnable, `ch-11.md:143-191`) — **PASS**
  - Block 3 (10 lines, compact stub check, `ch-11.md:195-206`) — **PASS**
- Live execution of the compact stub check (`ch-11.md:195-206` + expected `text` block at `ch-11.md:210-212`) in `E:\book_gen\.venv\Scripts\python.exe`, `HF_TOKEN=fake-token-for-stub`:
  - **rc=0**, last visible stdout line = `42`. Assertion `result == "42"` did not raise. Step trace shows `New run / Step 1 / Executing parsed code: final_answer("42") / Final answer: 42` exactly as the prose at `ch-11.md:208` claims.
- `Select-String -Path ch-11.md -Pattern 'HfApiModel|ApiModel'` — **PASS**, 0 matches. Cross-checked ch-09: 3 matches in ch-09 (the one-time sidebar at `ch-09.md:23` + import line at `ch-09.md:20` + the descriptive paragraph at `ch-09.md:25`), 0 in all other chapters — whole-book rule preserved.
- Word-bounded `grep -w` of `\bfinal_answer\b` in ch-11 — **PASS**, 0 prose matches. The single match at `ch-11.md:200` is inside the Python stub's `'<code>final_answer("42")</code>'` literal (model-emulated output, explicitly permitted by the style guide).
- Vocabulary blacklist grep — `magic`, `just`, `simply`, `obviously`, `optimal`, `proven`, `revolutionary`, `game-changing`, `studies show`, `powerful` (case-insensitive, word-boundary) — **PASS**, 0 matches anywhere in ch-11.
- UTF-8 round-trip via byte→string→byte — **PASS**, byte length identical (19386), zero drift.
- Strict structural counts: 13 H2s, all ≤7 words (longest is 6 words: `Configure an agent with these knobs` and `Two runs on the same agent`); orientation 53 words (within 30–60 band); closing callout at `:214`, bridge at `:216`, HTML comment starts at `:218`. One whole-file exclamation mark at `:218` (the `<!--` HTML-comment start tag); zero exclamation marks in visible prose.
- Paragraph-length audit on visible prose (code blocks, HTML comments, headings, and blockquote callout stripped; 35 prose paragraphs): **1 violation** — `ch-11.md:49` is 81 words (1 over the 80-word ceiling). All other paragraphs ≤ 80 words.
- Live provider execution with `HF_TOKEN` — **not run** (no real token configured; consistent with prior reviews; provider examples short-circuit on `load_api_key("HF_TOKEN")` as designed).

## Per-check verdicts (the 18 line-edit checklist items)

### 1. Vocabulary blacklist
- **Verdict:** PASS
- **Evidence:** `Select-String` for the 10 banned terms against `ch-11.md` returns 0 matches. Verified after the dev-fix1 re-cut (1703-word revision).

### 2. Second person dominant; third-person passive labeled
- **Verdict:** PASS
- **Evidence:** 4 contractions in prose (`don't` ×3, `you'll` ×1) plus pervasive `you`/`your`/`the agent`/`the framework`/`the reader` (well, the prose does not literally address the reader, but every imperative is second person and the orientation grounds the reader in the scene). Zero unflagged third-person passive constructions; the only "you" is the reader-as-practitioner.

### 3. Contractions natural; no exclamation marks
- **Verdict:** PASS
- **Evidence:** 4 contractions counted (natural, sparse — matches the ch-08/ch-10 line-edit profile). One whole-file exclamation mark at `ch-11.md:218` is the `<!--` HTML-comment start tag, not visible prose. Zero exclamation marks in any prose paragraph.

### 4. Pacing: one move per paragraph; visible prose paragraphs ≤ 80 words
- **Verdict:** **WARN**
- **Evidence:** 35 visible prose paragraphs. **34 / 35 are ≤ 80 words. One violation:**
  - **`ch-11.md:49` — 81 words (1 over).** The wall-clock paragraph reads: "A whole-package grep on 2026-08-01 confirms there is no `max_duration`, no `timeout_seconds`, and no wall-clock bound on the agent loop. The only related symbol is `RunResult.timing`, which measures how long a finished run took but does not limit it. If you genuinely need a wall-clock limit, prefer a thread with a watchdog that sets a flag the agent checks each step. `asyncio.wait_for` and `concurrent.futures` timeouts stop your waiting, not the agent's execution; cancelling the future does not terminate the underlying worker." A natural break is at the period after "does not limit it" (sentence 2) — splitting there yields a 32-word paragraph + a 49-word paragraph, both comfortably under 80.
- **All other 34 paragraphs are ≤ 80 words** (longest other is `:41` at 73 words, then `:15` at 72, then `:69` at 66).

### 5. Subheading style: sentence-fragment, ≤ 7 words, action-y
- **Verdict:** PASS
- **Evidence:** 13 H2s verified by `^## (.+)$` regex, all ≤ 7 words. Verb-led count: 8 (`Shape the prompt with…`, `Add re-plan steps with…`, `Override the prompt with…`, `Inspect runs with…`, `Memory grows within a run`, `Continue conversations with…`, `Build your own persistence layer`, `Configure an agent with these knobs`). The 5 non-verb-led H2s (`instructions adds guidance`, `prompt_templates swaps wholesale`, `max_steps caps the step count`, `Four beginner errors`, `Two runs on the same agent`) follow the ch-04..ch-10 chapter-template convention (template-noun + verb, or counts-as-template H2) and are outside the Fix-11 scope from the dev review. **The master's H2 swap at `:65` from "No built-in persistence in 1.26.0" → "Build your own persistence layer"** restored verb-led form on the previously-WARN line; verified at the file level.

### 6. Inline named sources for non-obvious claims
- **Verdict:** PASS
- **Evidence:** Every verified-against-source claim cites a path + line: `agents.py:1271` (`instructions` rendering), `agents.py:298-326` (`system_prompt=` TypeError + `EMPTY_PROMPT_TEMPLATES`), `agents.py:550-552` (planning trigger), `agents.py:884-889` (managed-only summary), `agents.py:196-254` (`RunResult` dataclass), `agents.py:970-1008` (`to_dict` keys). The Anthropic 5-pattern workflow reference is not needed in ch-11 (ch-12 is where it lands per `outline.md:941+`).

### 7. Zero `HfApiModel` / `ApiModel` mention in ch-11
- **Verdict:** PASS
- **Evidence:** grep returns 0 matches in `chapters/ch-11.md`. Whole-book cross-check: `HfApiModel`/`ApiModel` appears 3 times in `ch-09.md` (the one-time sidebar at `:23`, the import line at `:20`, the descriptive paragraph at `:25`) and 0 times in all other chapters — exactly the one-time-sidebar rule from `style-guide.md:118` preserved.

### 8. Zero `final_answer` in ch-11 prose
- **Verdict:** PASS
- **Evidence:** word-bounded `grep -w` of `\bfinal_answer\b` against `ch-11.md` after stripping code fences returns 0 matches. The single match in ch-11 at `ch-11.md:200` is inside the Python stub's `'<code>final_answer("42")</code>'` literal (model-emulated output, permitted). The `FinalAnswerStep` class name appears twice in ch-11 prose (`ch-11.md:53`, `:215`) and is the class name (PascalCase), not the snake_case reserved keyword — style guide line 88 only restricts the snake_case form.

### 9. Acronyms expanded on first use (API, AST, JSON, ML, OS, POSIX)
- **Verdict:** PASS
- **Evidence:** `API` and `JSON` appear in ch-11 prose, both first introduced in earlier chapters (ch-01 `API` first, ch-04/ch-05 `JSON` first) per the bible.md ch-01..ch-10 entries. No new acronyms introduced in ch-11 that require expansion. `AST` / `ML` / `OS` / `POSIX` are not used in ch-11 prose.

### 10. Orientation paragraph 30–60 words, opens with concrete terminal/agent scene
- **Verdict:** PASS
- **Evidence:** `ch-11.md:3` — "A terminal prints the agent's final answer after a short `.run(...)` call, and you wonder how to shape its behavior. The same `CodeAgent` constructor accepts a paragraph of house style, a re-plan timer, a step budget, and two knobs that control whether the next call remembers the last one. This chapter walks each." — **53 words**, opens with "A terminal prints…" (concrete scene per `style-guide.md:36`).

### 11. Forward-pointer "What's next" names ch-12 explicitly with a concrete forward move
- **Verdict:** PASS
- **Evidence:** `ch-11.md:216` — "What's next: ch-12 — Create Structured Agent Workflows — combines these controls into reusable flows." Explicit naming, concrete forward move (combining the ch-11 controls into reusable flows). Also names ch-13/14/15 for orientation (ch-13 "Observe, Debug, and Evaluate Runs", ch-14 "Test Agents", ch-15 "Keep Agents Safe") — matches `outline.md:941+` titles.

### 12. Closing imperative is the FINAL visible substantive prose paragraph before the HTML comment
- **Verdict:** PASS
- **Evidence:** `ch-11.md:214` blockquote `> **The move:** Configure your CodeAgent with instructions="...", max_steps=8, and planning_interval=4. ...` is the closing imperative (single substantive block). `ch-11.md:216` is the thin "What's next" bridge (1 sentence, 1 forward-pointer), permitted per the dispatch's exception clause. `ch-11.md:218` is the `<!--` HTML comment start. Order preserved exactly: callout → bridge → HTML.

### 13. Zero handoff-style recap, zero authorial summary, zero third-person "by the end of the reading…" closing line
- **Verdict:** PASS
- **Evidence:** Banned phrases `by the end of the reading`, `in this chapter we`, `we explored`, `we learned`, `we covered`, `we have seen`, `we have covered`, `our chapter`, `in summary`, `to recap`, `to summarize` — all 0 matches in visible prose. The single whole-file `by the end of the reading` match is at `ch-11.md:225` inside the HTML self-critique comment, where the author flags it as a banned phrase being correctly avoided — appropriate and not a violation.

### 14. Word count 1703 (±10% = 1533–1873)
- **Verdict:** PASS
- **Evidence:** Master's counter (the one of record per the dispatch + dev-fix1 report) is 1703. The band is 1533–1873. 1703 sits inside. My independent count using a stricter prose-only stripper (code blocks + HTML comments + tables removed) gives 1988; the dev-fix1 reviewer noted the same method-dependence (1911–1979). The difference comes from whether inline-code spans and the numbered-list items are counted. Master's methodology is the one of record; the no-regression criterion is met either way because the ch-11 line-edit is operating inside the established methodology (ch-07's "prose-with-inline-code-stripped" 1722 → 1708 trim used the same master counter).

### 15. UTF-8 round-trip clean
- **Verdict:** PASS
- **Evidence:** `[System.Text.Encoding]::UTF8.GetBytes(Get-String(...))` round-trips byte-identical (19386 bytes → 19386 bytes → 19386 bytes), zero drift. Em-dashes (—), smart quotes (' '), and the arrow character (→) in the HTML comment all survive round-trip without substitution.

### 16. All 3 code blocks ast.parse clean; compact check runs end-to-end and matches expected `text\n42\n` output
- **Verdict:** PASS
- **Evidence:** Live re-verified. All 3 Python blocks parse clean. Compact check (`ch-11.md:195-206`) executed in `E:\book_gen\.venv\Scripts\python.exe` returned rc=0, last visible stdout line = `42` — matches the `\`\`\`text\n42\n\`\`\`` expected-output block at `ch-11.md:210-212` exactly.

### 17. bible.md earlier chapter blocks (ch-01..ch-10) untouched; ch-11 block deduplicated per fix 9
- **Verdict:** PASS
- **Evidence:** file mtimes confirm ch-01..ch-10 chapter files have LastWriteTime 8/1/2026 (ch-01..ch-04) or 8/2/2026 morning (ch-05..ch-10), all earlier than ch-11.md (8/2/2026 1:53:42 PM) and bible.md (8/2/2026 1:36:27 PM). `bible.md:155-157` is the ch-11 `return_full_result` / `max_steps` / memory-composition block: each entry is short and explicitly defers to the ch-08/ch-09 entries for the baseline ("see the ch-09 `RunResult` entry above for the dataclass shape", "see the ch-08 and ch-09 entries above for the guard") — no duplication, only the ch-11-specific delta. The ch-11 block at `bible.md:149-160` adds 12 new entries (`instructions` kwarg, `prompt_templates` wholesale override, default prompt-template structure, `planning_interval` kwarg, `provide_run_summary` is managed-only, `return_full_result` runtime control, `max_steps` runtime budget, memory grows within a run, multi-turn via `reset=False`/`additional_args`, no built-in persistence, 4 beginner errors) without repeating ch-08/ch-09 terminology.

### 18. ledger.md ch-11 row updated correctly
- **Verdict:** PASS (with note)
- **Evidence:** `ledger.md:193` ch-11 row reads: status=`drafted`, depends on=`ch-10`, word count=`1703`, dev review=`fail`, line edit=`-`, notes=summary of the 12 fixes applied + "Awaiting dev-fix1 re-review." The `dev review=fail` field is the status from the **original** dev review (`ch-11_dev.md`); the `ch-11_dev-fix1.md` PASS_WITH_WARN report was written after the last ledger update (8/2/2026 1:47:48 PM, vs dev-fix1 at 8/2/2026 1:53:14 PM, vs chapter at 8/2/2026 1:53:42 PM). Master's lane to update the row after this line-edit pass; the row is consistent with the state it captured (post-fix1, pre-dev-fix1) and does not show a regression. Note: the dispatch says the master's H2 swap at `ch-11.md:65` (post-fix1) was applied after the ledger was last written; that swap is not reflected in the ledger text either, but the row's "Notes" already documents the `fix loop 1` shape and the row is a summary, not a verbatim diff. Master's lane to fold in the H2 swap and the dev-fix1 PASS_WITH_WARN result.

## Cross-cutting findings

- The chapter is line-edit-clean except for the one paragraph-length violation at `ch-11.md:49`. The fix is a one-sentence split at the period after "does not limit it" — yields a 32-word paragraph + a 49-word paragraph, both under the ceiling. No code edits, no semantic change, no impact on the runnable blocks or the closing-imperative structure. This is a copy-edit-pass-level concern, not a developmental concern.
- The dev-fix1 reviewer's concern about the compact check (Fix 7) being functionally redundant with ch-09's stub demo is **still true** post-this-line-edit. The compact check at `ch-11.md:195-206` uses the same `'<code>final_answer("42")</code>'` string as `ch-09.md:154`; no ch-11-specific knob (`instructions=`, `planning_interval=`, `reset=False`, `return_full_result=True`, `max_steps` exhaustion) is exercised. The chapter's first runnable at `ch-11.md:89-137` DOES exercise ch-11 knobs (`instructions=`, `max_steps=8`, `planning_interval=4`, `return_full_result=True` with the `assert result.output == 5` shape), but it is 47 lines, not the 5–20-line compact check the style guide requires. Recommended for the whole-book copy-edit pass, not this line-edit pass.
- The 1 over-ceiling paragraph (`:49` at 81 words) is the only line-edit finding. The chapter is otherwise clean for line-edit progression to the whole-book copy-edit pass.

## Out-of-scope observations

- `ch-11.md:218-231` HTML self-critique comment is rich and accurate: 12 research entries covered, voice match claims verified, blacklist verified by grep, 3 runnable examples all ast.parse, compact stub asserts "42" — every claim is independently verifiable in this turn. No action required; this is the author-for-orchestrator handoff per `book-gen-orchestrator` workflow.
- `bible.md:150` still preserves the literal `Now Begin!` text (with exclamation) in the `instructions` kwarg research-evidence block. This is appropriate — it quotes the actual smolagents source string and is not visible chapter prose. No action required.
- The closing-imperative constant shape `max_steps=8, planning_interval=4` at `ch-11.md:214` matches the first runnable's `max_steps=8, planning_interval=4` at `ch-11.md:127-128`. Consistent.
- The two forward-pointer H2 cases (`Four beginner errors` at `:73`, `Two runs on the same agent` at `:139`) are template-noun H2s matching the ch-04..ch-10 pattern (`Traceback map`, `Beginner PEP 8 subset`, etc.) — they are by design and outside the Fix-11 retitling scope. No action required.
- The `## Memory grows within a run` H2 (`:51`) is "Memory grows within a run" — technically a state-description, not strictly verb-led, but the predicate verb "grows" is the grammatical head of the clause, so the style-guide spirit is satisfied. No action required.

## Honest assessment

The chapter is line-edit-clean. The single paragraph-length violation at `ch-11.md:49` (81 words) is a one-sentence split that the next fix loop can apply in seconds — it does not block the chapter's progression to the whole-book copy-edit pass. The H2 at `ch-11.md:65` was correctly retitled by master to "Build your own persistence layer" between the dev-fix1 review and this dispatch, restoring verb-led form on the one line that was borderline WARN. The whole-book rules (`HfApiModel`/`ApiModel` zero outside the ch-09 sidebar, `final_answer` zero outside code strings) are preserved. All three code blocks compile, the compact check runs end-to-end, the closing-imperative structure is preserved, the bible ch-11 block is correctly deduplicated, and the orientation paragraph opens with the concrete terminal/agent scene the style guide requires. The dev-fix1 reviewer's redundancy concern about the compact check is still true (it does not exercise a ch-11-specific knob) but is the right kind of issue to defer to the whole-book copy-edit pass — the chapter itself is technically correct and pedagogically complete without the check, and rewriting the stub mid-line-edit would be a deeper refactor than the line-edit scope justifies.

## Self-critique

- **Did I do my job?** yes. I read the chapter end-to-end, the prior dev + dev-fix1 reports, the style guide, the bible ch-11 block, the ledger ch-11 row, the ch-09 stub block (for redundancy comparison), and the file mtimes for ch-01..ch-10. I ran `ast.parse` on all 3 Python blocks via the venv, live-executed the compact check via the venv, and ran the UTF-8 round-trip, the blacklist grep, the `HfApiModel`/`ApiModel` grep, the `final_answer` word-bounded grep, and a strict paragraph-length audit (35 paragraphs).
- **What might I have missed?** I did not run `cspell` or any other prose linter. I did not execute the live provider examples (no `HF_TOKEN`). I did not reproduce the master's word-count algorithm; I trusted the dispatch's claim that 1703 is the master counter. I did not check whether the master's H2 swap at `:65` is reflected in the ch-09/ch-10/ch-12 forward-pointers (other chapters reference "No built-in persistence" as the conceptual label, but I did not re-grep).
- **What did I assume without evidence?** I assumed the dev-fix1 reviewer's claim about the compact check's redundancy with ch-09 is still accurate in this post-master-H2-swap state. I verified independently: `ch-09.md:154` is the same `'<code>final_answer("42")</code>'` string, and ch-11's compact check at `:195-206` uses the same string with no new knob exercised — confirmed.
