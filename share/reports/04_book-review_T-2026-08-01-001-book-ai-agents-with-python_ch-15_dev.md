# Review Report — T-2026-08-01-001-book-ai-agents-with-python / ch-15 developmental

**Date:** 2026-08-02
**Sub-agent:** review
**Loop:** initial

## Summary
- **Overall verdict:** FAIL
- **Tasks reviewed:** 1
- **Pass / Warn / Fail:** 0 / 0 / 1
- **Issue counts by severity:** 2 CRITICAL / 2 HIGH / 0 MEDIUM / 0 LOW
- **Block release:** yes

The chapter has the intended safety content and its first two executable examples pass fresh verification, but it fails hard acceptance gates: the required ch-17 forward pointer is missing, one visible paragraph is 85 words, the raw `final_answer` rule check finds the framework terminator in code, and smolagents API claims are not consistently attributed inline.

## Tests / build run
- Fresh Python verification with `E:\book_gen\.venv\Scripts\python.exe`: extracted all 3 `python` fences; `ast.parse` passed for blocks 1–3.
- Fresh runtime execution of blocks 1–2 with the pinned venv: exit code 0. Block 1 printed successful `math`/`json` results and blocked `os`/`requests` with `InterpreterError`; block 2 completed with `result.state == "success"` and the URL answer.
- Fresh venv introspection: smolagents `1.26.0`; `PythonInterpreterTool` exposes `authorized_imports`; `CodeAgent` exposes `executor_type` with `local`, `blaxel`, `e2b`, `modal`, `docker`; `RunResult` exposes `output`, `state`, `steps`, `token_usage`, `timing`.
- Block 3 was not executed end-to-end in this review because its documented example writes a JSONL file and the dispatch boundary forbids writing any file other than the review report. AST parsing passed; the coder's claimed block-3 run was not independently reproduced.
- Exact PowerShell gate A (`Select-String ... -Pattern "HfApiModel|ApiModel"`): exit code 0, `A_COUNT=0`.
- Exact PowerShell gate B (`Select-String ... -Pattern "\bfinal_answer\b"`): exit code 0, `B_COUNT=1`, at `chapters/ch-15.md:84` inside the runnable stub code. This is not prose, but the requested whole-file command is not zero.
- No documented `coder/resources/` test command was available for this book-gen dispatch; relying on the fresh checks above plus source inspection.

## Per-task verdicts

### ch-15 — Keep Agents Safe and Responsible
- **Verdict:** FAIL
- **Spec match:** The chapter covers the ten named research themes, the safety outcome, the four side-effect categories, import fencing, executor choices, loop guards, web limits, secret hygiene, redaction, and the closing imperative. It does not satisfy all hard checklist gates.
- **Correctness:** The verified runtime API shape is correct for the checked examples. The chapter correctly states the `RunResult` field set and the executor literal set, and the import-fence example rejects unauthorized imports.
- **Style:** The opening orientation is 59 words and concrete (`chapters/ch-15.md:3-3`), H2 headings are action-oriented and at most 6 words (`chapters/ch-15.md:5,13,19,33,57,63,106,114,148,158`), blacklist scan is zero, and the imperative/What's-next ordering is correct (`chapters/ch-15.md:164-166`). One visible prose paragraph is 85 words, violating the ≤80-word gate (`chapters/ch-15.md:59-60`).
- **Tests:** All three blocks parse; blocks 1–2 run successfully in the pinned venv. Block 3 was not rerun because it writes a file prohibited by the dispatch boundary. The exact final-answer whole-file command finds one bare `final_answer` in the stub (`chapters/ch-15.md:84`).
- **Evidence:** `chapters/ch-15.md:7-11` (OWASP/NIST/Anthropic framing); `:21-31` (side-effect categories); `:35-55` (`authorized_imports` and local evaluator); `:59-67` (executor and guard claims); `:108-112` (web-tool limits); `:116-146` (secret hygiene and redaction); `:148-156` (four beginner errors); `:160-166` (pointers and close); `bible.md:172-182` (ch-15 append); `ledger.md:241-241` (draft row).
- **Issues:**
  - [CRITICAL] `chapters/ch-15.md:160-162` omits the required forward pointer to **ch-17 — Choose and Operate Model Backends**. Entry-142 requires forward pointers including ch-17, and the dispatch explicitly requires the outline numbering for ch-16, ch-17, ch-18, and ch-19. The chapter names ch-16, ch-18, and ch-19 only.
  - [CRITICAL] The exact required whole-file `final_answer` check is non-zero: `chapters/ch-15.md:84` contains the bare framework terminator inside the runnable `StubModel` code. The prose body is clean, and `final_answer_checks` is correctly allowed, but the specified command does not meet the stated “must be 0” result.
  - [HIGH] `chapters/ch-15.md:59-60` is an 85-word visible prose paragraph, exceeding the required maximum of 80 words. The writer's HTML self-critique claim at `chapters/ch-15.md:190-192` is therefore stale.
  - [HIGH] Several non-obvious smolagents API/behavior claims lack inline attribution to the 1.26.0 docs or installed source, despite the research-grounding gate. Examples include the `authorized_imports` constructor/`None` semantics at `chapters/ch-15.md:35-37`, executor support and provider requirements at `:59-61`, `max_steps` defaults and validator call semantics at `:65-67`, web-tool defaults at `:108-110`, and `RunResult` contents at `:116`. A source-location reference appears later (`:55`), but it does not provide inline attribution for all of these separate API claims.
- **Suggested fix:** Add the ch-17 backend pointer, decide how the mandated whole-file keyword gate is reconciled with the required runnable terminator (or remove the bare terminator from the code example), split the 85-word paragraph, and add inline smolagents 1.26.0 source/doc citations at each API-claim cluster.

## Required review checklist

1. **Outline coverage:** PASS for entry-133 through entry-142 content in prose (`chapters/ch-15.md:7-11`, `:15-17`, `:21-31`, `:35-61`, `:63-112`, `:114-166`). Entry-142's required ch-17 pointer is missing; see FAIL above.
2. **Voice match:** PASS. Conversational technical voice, second-person instructions, contractions (`chapters/ch-15.md:17`, `:31`, `:61`), and no exclamation marks.
3. **Vocabulary blacklist:** PASS. Fresh case-insensitive word-boundary scan returned zero hits for all ten prohibited terms.
4. **Bible consistency:** WARN. The required ch-15 block exists at `bible.md:172-182` and contains the requested terms and redaction pattern. It intentionally restates some previously established cross-chapter surfaces, especially `final_answer_checks` and `RunResult`; the safety-specific additions are non-duplicative, but the block is not strictly free of repeated API terminology.
5. **Research grounding:** FAIL. OWASP, NIST, and Anthropic are named at `chapters/ch-15.md:7-11` and `:15`; smolagents 1.26.0 API claims are not all individually or cluster-wise attributed inline. See HIGH issue above.
6. **Forward-pointer hygiene:** FAIL. ch-16 is correctly named at `chapters/ch-15.md:160,166`; ch-18 and ch-19 are correctly named at `:162`; required ch-17 is absent.
7. **Code-block correctness:** PASS for AST and fresh blocks 1–2. Runtime introspection confirms the requested signatures and all five `RunResult` fields. Block 3 AST-parses but was not rerun due the no-other-file-write boundary.
8. **Beginner accessibility:** FAIL. Orientation, headings, and most paragraph sizing pass, but `chapters/ch-15.md:59-60` is 85 words.
9. **Closing-imperative contract:** PASS. The `> **The move:**` callout is at `chapters/ch-15.md:164`; the only visible material after it is the permitted one-sentence bridge at `:166`, followed by the HTML comment.
10. **Concrete model identifier rule:** PASS. No concrete provider model identifier appears in visible prose or code; `small-coding-model` is a generic fallback string at `chapters/ch-15.md:75`, not a provider/model identifier.
11. **UTF-8 clean:** PASS. Fresh `bytes.decode("utf-8")` round-trip completed without error.
12. **No-regression vs prior chapters:** WARN. `bible.md` is append-only and the ch-15 block is present; `ledger.md:241` correctly records the draft row and 1532 words. The ledger's claims that all visible paragraphs are ≤80 and that all requested pointers are present are stale, so they must be corrected when the fixes land.

## Cross-cutting findings
- The HTML self-critique at `chapters/ch-15.md:170-200` claims all gates pass, but it is stale on paragraph length and ch-17 coverage. Treat it as internal handoff metadata, not verification evidence.
- The chapter teaches a strong safety boundary, but the exact acceptance command and the runnable stub syntax conflict: the code needs the framework terminator to demonstrate `CodeAgent`, while the requested raw grep gate rejects it. Master should resolve this contract before acceptance rather than silently treating the command as prose-only.
- No source files, book files, ledger, bible, task files, notes, or traces were edited by this review; only the requested report is written.

## Out-of-scope observations (informational only)
- The research log labels the ch-15 research section as `## ch-14 — Keep Agents Safe and Responsible` at `research-log.md:897`, while the later section labels ch-15 as `## ch-15 — Coordinate Multiple Agents` at `:961`. This is bookkeeping drift in the research log, not a chapter-content failure.
- The chapter's code does not demonstrate `executor_type` construction; it explains the kwarg and the fresh signature check confirms it. A runnable Docker/provider example would require optional infrastructure and is not required by the assigned outcome.

## Honest assessment
This chapter is close on substance and the checked smolagents behavior is technically grounded in the installed 1.26.0 runtime. It is not acceptable as submitted because it misses a required chapter dependency pointer, exceeds the hard paragraph limit, fails the literal bare-keyword gate in its runnable code, and overstates its inline attribution coverage. Fix those acceptance issues and rerun the full checklist before developmental approval.

## Self-critique
- **Did I do my job?** Yes.
- **What might I have missed?**
  - I did not execute block 3 because the dispatch forbade its JSONL file write; its AST and source were inspected.
  - I did not run a full external citation URL fetch; the chapter's named citations and research-log sources were checked locally.
  - No coder summary or documented book-gen test command was present, so no coder claims were independently compared.
- **What did I assume without evidence?**
  - I treated `small-coding-model` as a generic placeholder rather than a concrete provider identifier; it is not paired with a provider namespace or known model family.
  - I treated the Bible repetition as a WARN rather than a FAIL because the repeated terms are required safety cross-references, while the new safety claims are distinct.
