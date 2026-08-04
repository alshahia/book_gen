# Developmental Review — T-2026-08-01-001-book-ai-agents-with-python / ch-14

**Date:** 2026-08-02
**Sub-agent:** am-review
**Pass:** developmental review

## Summary

- **Overall verdict:** FAIL
- **Block chapter acceptance?** yes
- **Issue counts:** 1 CRITICAL, 2 HIGH, 1 LOW
- **Core outcome:** Met in the chapter and verified by the runnable pytest suite, but the closing contract and two explicit consistency/grounding gates are not met.

## Tests / build run

- `Select-String -Path "E:\book_gen\books\ai-agents-with-python\chapters\ch-14.md" -Pattern "HfApiModel|ApiModel"` — PASS, 0 matches.
- `Select-String -Path "E:\book_gen\books\ai-agents-with-python\chapters\ch-14.md" -Pattern "\bfinal_answer\b"` — PASS after classification: 1 match, solely inside the Python code block at `chapters/ch-14.md:73`; 0 prose-body matches.
- Extracted the Python block to the approved temporary directory and ran `E:\book_gen\.venv\Scripts\python.exe -m pytest <temp> --collect-only -q` — exit 0; 4 tests collected (`add`, `reverse`, `color`, `failure_records_max_steps`). Temporary file removed after verification.
- `E:\book_gen\.venv\Scripts\python.exe -m pytest <temp> -v` — exit 0; 4 passed in 1.52s under pytest 9.1.1 with pytest-asyncio 1.4.0 loaded in strict mode.
- Python AST/compile gate — PASS; the extracted 63-line test block parses and compiles.
- Installed smolagents 1.26.0 signature inspection — PASS: `Model.generate(self, messages, stop_sequences=None, response_format=None, tools_to_call_from=None, **kwargs) -> ChatMessage`; `MultiStepAgent.__init__` includes `step_callbacks=` and `logger=` and does not include `monitor=`; `.run()` includes `max_steps=` and `return_full_result=`; `RunResult` exposes `output`, `state`, `steps`, `token_usage`, and `timing`; `AgentMaxStepsError` exists and subclasses `AgentError`.
- Strict UTF-8 decode — PASS, zero errors.

## Required review checklist

### 1. Outline coverage — PASS

All twelve research entries are represented:

- entry-121: nondeterminism, prompt sensitivity, and network/provider flakiness at `chapters/ch-14.md:7-11`.
- entry-122: subclass `Model` and override `generate`, not `__call__`, at `chapters/ch-14.md:15-19` and `:65-74`.
- entry-123: `max_steps=1` at `chapters/ch-14.md:23-27`, `:89-93`, and `:102-112`.
- entry-124: action assertions through `step_callbacks` at `chapters/ch-14.md:31-33`, `:83-95`, and `:106`.
- entry-125: `logger=` rather than `monitor=` at `chapters/ch-14.md:37-39` and `:77-93`.
- entry-126: `return_full_result=True` and `RunResult` assertions at `chapters/ch-14.md:102-105` and `:121-127`.
- entry-127: `(task, expected_answer)` gold cases at `chapters/ch-14.md:49-51` and `:60-62`.
- entry-128: fixture and `pytest.raises(AgentMaxStepsError)` at `chapters/ch-14.md:43-45`, `:87-95`, and `:110-116`.
- entry-129: pytest-asyncio basics with synchronous `.run()` at `chapters/ch-14.md:131-133`.
- entry-130: `pytest.mark.parametrize` at `chapters/ch-14.md:49-51` and `:98-100`.
- entry-131: four beginner errors at `chapters/ch-14.md:135-143`.
- entry-132: forward pointers to safety, model backends, and both projects at `chapters/ch-14.md:163-169`.

### 2. Voice match — PASS

Conversational technical voice, second-person instructions, natural contractions, and zero exclamation marks are visible throughout, including `chapters/ch-14.md:7-19`, `:121-149`, and `:159-169`.

### 3. Vocabulary blacklist — PASS

Case-insensitive word-boundary scan of visible prose found zero instances of `magic`, `just`, `simply`, `obviously`, `optimal`, `proven`, `revolutionary`, `game-changing`, `studies show`, or `powerful`.

### 4. Bible consistency — FAIL

The required ch-14 block exists and contains stub model, `pytest.fixture`, `pytest.raises`, `pytest.mark.parametrize`, `pytest-asyncio`, and `AgentMaxStepsError` at `bible.md:164-171`. However, its **Stub model** entry at `bible.md:165` duplicates the established Stub model entries at `bible.md:112` and `bible.md:122` instead of pointing back and adding only the chapter-specific testing distinction.

### 5. Research grounding — FAIL

Most non-obvious API claims cite installed source, including direct `generate` dispatch (`chapters/ch-14.md:15`), per-run step precedence (`:23`), max-step state (`:27`), callback dispatch (`:31`), and `RunResult` structure (`:125`). Two smolagents behavior claims lack inline docs/source attribution: base `Model` initialization behavior at `chapters/ch-14.md:19` and logger behavior under `LogLevel.OFF` at `chapters/ch-14.md:39`. The latter is especially relevant because the example depends on a custom logger still recording calls while visible logging is off.

### 6. Forward-pointer hygiene — PASS

The chapter uses the current outline numbering and titles: ch-17 at `chapters/ch-14.md:163`, ch-18 and ch-19 at `:165`, and ch-15 at `:169` and `:173`.

### 7. Code-block correctness — PASS

The code block at `chapters/ch-14.md:53-117` parses, collects four tests, and passes all four. Installed signatures confirm the `Model.generate`, `logger=`, `step_callbacks=`, `return_full_result=True`, `RunResult`, and `AgentMaxStepsError` surfaces. The passing run also demonstrates that pytest-asyncio is not required for these synchronous test functions.

### 8. Beginner accessibility — PASS

The opening is a concrete terminal/pytest scene at `chapters/ch-14.md:3` and measures 49 words, within the 30–60-word gate. Every visible prose paragraph is at most 68 words. All 13 H2 subheadings at `chapters/ch-14.md:5-167` are action-oriented fragments of 3–4 words, below the seven-word limit. Paragraphs consistently make one move and then supply evidence or a tradeoff.

### 9. Closing-imperative contract — FAIL

The `> **The move:**` callout is correctly the last substantive action block before a thin “What's next” bridge and the HTML comment (`chapters/ch-14.md:171-175`). Its sentence is not imperative, however: it repeats the third-person outcome wording, “by the end of the reading, the reader can…”. This is the exact prohibited pattern named by the dispatch and conflicts with the style guide's reader-action contract at `style-guide.md:31`, `:38`, and `:61-87`.

### 10. Concrete model identifier rule — PASS

No hardcoded provider model identifier or `model_id=` appears. The chapter appropriately uses `StubModel` throughout (`chapters/ch-14.md:15-19`, `:65-74`, and `:89-93`).

### 11. UTF-8 clean — PASS

Strict UTF-8 decoding and byte round-trip succeeded with zero errors.

### 12. No-regression vs prior chapters — PASS_WITH_WARN

The ledger's ch-14 row is present, preserves dependency `ch-13`, records 1498 words, and remains at `drafted` pending this review (`ledger.md:229`). The bible append is physically non-destructive and follows prior chapter blocks (`bible.md:164-171`), but the duplicate Stub model definition is the checklist-4 failure above.

## Per-task verdict

### ch-14 developmental review — FAIL

- **Spec match:** The chapter teaches and demonstrates the complete requested pytest workflow.
- **Correctness:** The embedded suite is executable and all four cases pass against smolagents 1.26.0.
- **Style:** Voice, paragraph length, headings, blacklist, and forward pointers pass; the required final action is not written as an imperative.
- **Evidence:** `chapters/ch-14.md:3-173`, `bible.md:112`, `:122`, `:164-171`, `ledger.md:229`.
- **Issues:**
  - **[CRITICAL]** `chapters/ch-14.md:171` uses the explicitly prohibited third-person “by the end of the reading, the reader can…” closing instead of a direct imperative. Rewrite only the move sentence as a second-person command while preserving its position before the thin bridge.
  - **[HIGH]** `bible.md:165` repeats the Stub model definition already established at `bible.md:112` and `:122`, violating the required non-duplication gate. Replace it with a pointer to the established term plus only ch-14's pytest-specific extension.
  - **[HIGH]** `chapters/ch-14.md:19` and `:39` make smolagents behavior claims without inline attribution to the 1.26.0 docs or installed source. Add compact installed-source citations at both claims.
- **Suggested fix:** Apply the three narrow manuscript/bible fixes above, then re-run the same grep, AST, collection, and full pytest gates.

## Cross-cutting findings

- The technical teaching path is coherent: deterministic boundary → stub → bounded run → callbacks/logger → fixture/parameterization → failure state → async boundary → suite layering.
- The code is stronger than the current verdict suggests; the FAIL is driven by explicit book-level contracts, not a broken test suite.

## Out-of-scope observations

- **[LOW]** The dispatch context reports 12 H2 subheadings, but the file contains 13 (`chapters/ch-14.md:5-167`). This does not violate the stated ≤7-word/action-fragment requirement and does not need a chapter edit unless 12 was intended as a hard structural count.

## Honest assessment

The chapter successfully installs the promised testing move, and the example is genuinely runnable: four tests collect and pass against the pinned environment. It is not ready for acceptance because the closing repeats a known prohibited pattern, the bible duplicates an established term, and two API behavior claims miss the required inline grounding. These are narrow fixes; the chapter does not need structural rework.

## Self-critique

- **Did I do my job?** Yes. I read the chapter, outline, research contract, style guide, bible, and ledger; inspected installed smolagents signatures; and independently ran collection and execution.
- **What might I have missed?** I did not compare every sentence against the full text of research entries 121–132 because the relevant entry block was beyond the first capped research-log read; I used the dispatch's explicit entry requirements and the outline's ch-14 mapping as the binding checklist.
- **What did I assume without evidence?** I treated the H2 count mismatch as informational because no checklist item requires exactly 12 headings. I also treated the temporary extraction file as test infrastructure and removed it immediately after the run.
