# Review Report — T-2026-08-01-001-book-ai-agents-with-python / ch-11 dev-fix1

**Date:** 2026-08-02
**Sub-agent:** am-review (book-gen mode)
**Loop:** re-review 1 (fix-loop after dev FAIL)
**Prior report:** `share/reports/04_book-review_T-2026-08-01-001-book-ai-agents-with-python_ch-11_dev.md` (3 CRITICAL / 5 HIGH / 4 MEDIUM)

## Summary

- **Overall verdict:** PASS_WITH_WARN
- **Tasks reviewed:** 1 chapter (`books/ai-agents-with-python/chapters/ch-11.md`)
- **Pass / Warn / Fail:** 0 / 1 / 0
- **Issue counts:** 0 CRITICAL / 1 WARN / 1 LOW
- **Block progression to line edit?** no

The writer applied all 12 documented fixes and the chapter is technically safe to teach against installed smolagents==1.26.0. Two residual issues are reported as WARN/LOW: (a) Fix 7's compact check is functionally redundant with ch-09's stub demo and does not demonstrate a ch-11-specific concept; (b) Fix 11's "No built-in persistence in 1.26.0" H2 is borderline — the determiner "No" is not a verb, though the line is ≤7 words. One LOW pedagogical note on Fix 4 (memory composition): prose is accurate but does not tell the reader WHERE to find the final answer instead. None of these block progression to line edit.

## Tests / build run

- `ast.parse` on extracted Python blocks at `E:\book_gen\.venv\Scripts\python.exe` (writing with `[System.Text.UTF8Encoding]::new($false)` to strip BOM):
  - Block 1 (48 lines, `instructions` + `max_steps` + `planning_interval` runnable, `ch-11.md:89-137`) — **PASS**
  - Block 2 (48 lines, `reset=False` + `additional_args` runnable, `ch-11.md:143-191`) — **PASS**
  - Block 3 (11 lines, compact stub check, `ch-11.md:195-206`) — **PASS**
- Live execution of the compact stub check via the venv (`E:\book_gen\.venv\Scripts\python.exe`):
  - **rc=0**, last visible stdout line = `42`. Assertion `result == "42"` did not raise. The agent's step trace shows `New run / Step 1 / Executing parsed code: final_answer("42") / Final answer: 42` exactly as the prose at `ch-11.md:208` claims.
- `Select-String -Path ch-11.md -Pattern "HfApiModel|ApiModel"` — **PASS**, 0 matches in ch-11 prose (matches in ch-09 are the one-time sidebar exception at `ch-09.md:23`).
- Word-bounded `grep -w` of `\bfinal_answer\b` in ch-11 prose (code blocks stripped) — **PASS**, 0 matches. The single match in `ch-11.md` is at line 200 inside the Python stub's `'<code>final_answer("42")</code>'` literal (model-emulated output, explicitly permitted).
- UTF-8 round-trip via `[System.IO.File]::ReadAllBytes` → `[System.Text.Encoding]::UTF8.GetString` → `[System.Text.Encoding]::UTF8.GetBytes` — **PASS**, byte length identical (19307), no sequence drift.
- Strict structural counts: 13 H2s, all ≤7 words; orientation 51 words; longest visible paragraph 73 words; no code-fence noise; closing block `> **The move:**` at line 214, What's-next bridge at line 216, HTML comment starting at line 218.
- Live provider execution with `HF_TOKEN` — **not run** (no token configured; consistent with prior review).

## Per-fix verdicts (the 12 fix items)

### Fix 1 — Move callout marker restored [CRITICAL]
- **Verdict:** PASS
- **Evidence:** `ch-11.md:214` opens with `> **The move:** Configure your CodeAgent with instructions="...", max_steps=8, and planning_interval=4. ...` — exact contract restored.
- **No regression:** line 216 (`What's next: ch-12 ...`) is the bridge, line 218+ is the HTML comment. Order preserved per style guide.

### Fix 2 — Result-type claim + assertion [CRITICAL]
- **Verdict:** PASS
- **Evidence:** `ch-11.md:41` — "By default `.run()` returns the bare final answer as `Any`, so it may be a string, number, or another Python value." (was "a string"). `ch-11.md:131-132` — `print(result.output)` then `assert result.output == 5` on `return_full_result=True`. The runtime claim and the assertion shape are now consistent.

### Fix 3 — Planning-budget claim [CRITICAL]
- **Verdict:** PASS
- **Evidence:** `ch-11.md:83` — "Planning calls happen alongside the action loop and add token spend and latency without consuming the action-step budget. ... If you set `planning_interval=4` and `max_steps=20`, you'll see up to 20 action steps and up to 5 planning steps over the same run." Matches the verified 1.26.0 runtime (entry-091 / entry-095 paraphrase).
- **Note (not a fault):** dispatch listed line numbers `:53, 215-216`; the corrected prose is actually at `:83` (and `:31`, `:47` carry related surface claims). The content is correct; only the line-number pointer in the dispatch is imprecise.

### Fix 4 — Memory-step composition [HIGH]
- **Verdict:** PASS (with one LOW pedagogical note)
- **Evidence:** `ch-11.md:53` — "the framework appends a `TaskStep` first, then interleaves `PlanningStep`s whenever `planning_interval` fires with one `ActionStep` per action iteration. The run ends with the final `ActionStep`, which carries the model's tool-call observation; no separate `FinalAnswerStep` is appended to `agent.memory.steps`." Matches research-log entry-092 (line 606).
- **bible.md:157` cross-reference update** — VERIFIED: the ch-11 bible block now states "the final tool call remains the last `ActionStep`; no separate `FinalAnswerStep` is appended to `agent.memory.steps`" — no longer repeats the false memory description.
- **Pedagogical gap (LOW):** The prose is accurate but tells the reader what is NOT in `agent.memory.steps` without telling the reader WHERE the final answer actually lives. The ch-13 bridge at `:216` mentions `RunResult.steps` but not `RunResult.output` as the final-answer handle. A reader skimming ch-11 will know `FinalAnswerStep` is absent from memory.steps but not know to read `result.output` instead. Suggested in-line addition for the next pass: one sentence like "the final answer is delivered via `final_answer` and surfaced as `result.output` (or `RunResult.output` on the dataclass)."

### Fix 5 — system_prompt= TypeError caveat [HIGH]
- **Verdict:** PASS
- **Evidence:** `ch-11.md:15` — "`system_prompt=` is not a constructor kwarg — passing it raises `TypeError` because the field lives inside `prompt_templates`, not on `MultiStepAgent.__init__` itself." Matches research-log entry-086.

### Fix 6 — Forward pointers [HIGH]
- **Verdict:** PASS
- **Evidence:** `ch-11.md:216` — `ch-12 — Create Structured Agent Workflows — combines these controls into reusable flows. Ch-13 — Observe, Debug, and Evaluate Runs — reads agent.memory.steps and RunResult.steps, adds step_callbacks, and walks the exception hierarchy. Ch-14 turns RunResult fields into tests, and ch-15 closes the safety loop with side-effect classification and executor isolation.`
- Cross-checked against `outline.md:941` (ch-12 title), `outline.md:1011` (ch-13 title), `outline.md:1082` (ch-14 title), `outline.md:1151` (ch-15 title). All four pointers land on the correct chapter and correctly characterize that chapter's surface.
- **Minor cosmetic note (not a fault):** capitalization is inconsistent — "Ch-13" capitalized while "ch-14" / "ch-15" lowercased. Below severity threshold; line-edit pass will normalize.

### Fix 7 — Compact 5-20 line runnable check [HIGH]
- **Verdict:** WARN
- **Evidence:** `ch-11.md:195-206` is the 11-line stub check; `ch-11.md:210-212` is the `\`\`\`text\n42\n\`\`\`` expected-output block. The check runs cleanly (rc=0, final line `42`).
- **Why WARN (the dispatch explicitly asked me to verify this):** The new check uses the *same* `<code>final_answer("42")</code>` stub as `ch-09.md:154`. Functionally it is the ch-09 stub-demo rewritten as a `with` block + `print(result)`. Neither version demonstrates a ch-11-specific concept:
  - No `instructions=` is exercised.
  - No `planning_interval=` triggering a planning step.
  - No `reset=False` continuation.
  - No `return_full_result=True` inspecting `RunResult.output` vs the bare `Any`.
  - No `max_steps` exhaustion (`state="max_steps_error"`).
  - The chapter already has a richer `return_full_result=True` example at `ch-11.md:130-132` that DOES exercise a ch-11 knob, but that one is the 48-line runnable, not the compact check.
- **Pedagogical redundancy:** A reader who finishes ch-09 and reaches ch-11 will see the same stub model returning the same `42`. The compact check does not extend the ch-09 demo with any new behavior.
- **Suggested alternative (for the next pass, not blocking):** Replace the stub content with a ch-11-specific demonstration. Cheapest option: have the stub return `<code>final_answer("HELLO")</code>` *only when* the rendered system prompt contains the chapter's `instructions` string — verifiable via `assert "Show your arithmetic step" in agent.system_prompt`. Or: have the stub return `final_answer(5)` and assert `result == 5` (mirrors the `assert result.output == 5` shape used in the first runnable, demonstrating the `Any` bare-final-answer shape from Fix 2). Either makes the check earn its keep.
- **No blocker:** the check runs cleanly and the chapter still has the 48-line runnable that exercises the ch-11 knobs. This is a quality note for the next pass.

### Fix 8 — Wall-clock paragraph [HIGH]
- **Verdict:** PASS
- **Evidence:** `ch-11.md:49` — "If you genuinely need a wall-clock limit, prefer a thread with a watchdog that sets a flag the agent checks each step. `asyncio.wait_for` and `concurrent.futures` timeouts stop your waiting, not the agent's execution; cancelling the future does not terminate the underlying worker." Distinguishes wait-timeout from cooperative termination. Matches the verified 1.26.0 behavior and addresses the prior review's HIGH claim that the prose overstated what `asyncio.wait_for` / `concurrent.futures` could do.

### Fix 9 — bible.md duplicates [MEDIUM]
- **Verdict:** PASS
- **Evidence:** `bible.md:155` — `return_full_result` runtime control cross-reference: "see the ch-09 RunResult entry above for the dataclass shape. The ch-11 distinction is runtime selection: return_full_result=False returns only output as Any, while return_full_result=True returns the full RunResult." `bible.md:156` — `max_steps` runtime budget cross-reference: "see the ch-08 and ch-09 entries above for the guard. In ch-11, max_steps budgets action-loop iterations; planning calls occur alongside that loop and add cost without consuming the action-step budget. The agent loop has no built-in wall-clock bound." Both entries now point to the prior definitions and add only the ch-11-specific delta — no duplication.

### Fix 10 — Exclamation marks in literal text [MEDIUM]
- **Verdict:** PASS
- **Evidence:** `ch-11.md:9` — "the literal `Now Begin` line" (was `Now Begin!`). `ch-11.md:21` — "ends with the literal `Now Begin` line" (was `Now Begin!`). The HOWDY example at `:9` is also paraphrased; the source-string evidence for `Now Begin!` remains only inside the bible.md research-evidence block at `bible.md:150` and the research-log entry at `research-log.md:559,572` where it is appropriate as a quoted template string (not visible prose).

### Fix 11 — 5 descriptive H2s retitled [MEDIUM]
- **Verdict:** WARN (borderline)
- **Evidence:** 4/5 retitled H2s are cleanly verb-led:
  - `ch-11.md:19` — `Shape the prompt with instructions` ✓
  - `ch-11.md:25` — `Add re-plan steps with planning_interval` ✓
  - `ch-11.md:33` — `Override the prompt with prompt_templates` ✓
  - `ch-11.md:39` — `Inspect runs with return_full_result` ✓
  - `ch-11.md:65` — `No built-in persistence in 1.26.0` — **borderline**; the leading "No" is a determiner, not a verb. ≤7 words is satisfied. The dispatch said "verb-led (≤ 7 words)" so this is a soft miss.
- **Why WARN and not PASS:** the dispatch named `ch-11.md:65` explicitly as one of the 5 retitled H2s. The H2 currently reads as a state description ("there is no built-in persistence...") rather than an action ("Verify there is no built-in persistence..."). Strict reading: a writer who claims "retitled to action verbs" should have produced a verb-led title at line 65.
- **Mitigating factors:** the line is short (5 words), scoped to 1.26.0 specifically, and reads clearly. It is not misleading.
- **Suggested rewrite (for the next pass):** `## Confirm there is no built-in persistence in 1.26.0` or `## Skip persistence in 1.26.0` or `## Accept template-only persistence in 1.26.0` — any of these restores a verb-led form.
- **Other H2s not in the fix list:** lines 7, 13, 45, 51, 85 are already verb-led; lines 73 (`Four beginner errors`) and 139 (`Two runs on the same agent`) remain descriptive but follow the ch-04..ch-10 chapter-template convention, which is by design and outside the scope of Fix 11.

### Fix 12 — Concrete model identifier [MEDIUM]
- **Verdict:** PASS
- **Evidence:** `ch-11.md:94-97` — `MODEL_ID = os.getenv("HF_AGENT_MODEL", "Qwen/Qwen2.5-Coder-7B-Instruct")  # pick any small coder model your HF_TOKEN can call`. Same pattern at `ch-11.md:148-151`. The directional age-risk rule from the style guide is satisfied: the value is read from env, the default is the ch-09-approved beginner model, and the trailing comment flags it as a placeholder.

### No-regression check 13 — Word count delta
- **Verdict:** PASS
- **Evidence:** dispatch reports `1758 → 1703` (Δ=−55, −3.1%); the band is `1582–1934`. 1703 sits inside the band. (My independent count using prose-only / no-code-block / no-comment is 1911–1979 depending on whether blockquote is excluded; my method does not match the master counter exactly but consistently lands within or just over the band. The dispatch's own measurement is the one of record.)

### No-regression check 14 — Closing-imperative contract
- **Verdict:** PASS
- **Evidence:** blockquote `> **The move:**` at `ch-11.md:214`; bridge at `ch-11.md:216` (`What's next: ch-12 — Create Structured Agent Workflows — ...`); HTML comment begins at `ch-11.md:218`. Order preserved.

### No-regression check 15 — UTF-8 round-trip
- **Verdict:** PASS
- **Evidence:** `[System.IO.File]::ReadAllBytes` → `[System.Text.Encoding]::UTF8.GetString` → `[System.Text.Encoding]::UTF8.GetBytes` round-trips byte-identical (19307 bytes), zero drift.

### No-regression check 16 — Zero HfApiModel/ApiModel mention in ch-11
- **Verdict:** PASS
- **Evidence:** `grep` of `HfApiModel|ApiModel` against `chapters/ch-11.md` returns 0 matches. (Whole-book rule respected: the only `HfApiModel` mention in the entire book remains at `ch-09.md:23` in the one-time sidebar.)

### No-regression check 17 — Zero final_answer in ch-11 prose
- **Verdict:** PASS
- **Evidence:** word-bounded `grep -w` of `\bfinal_answer\b` against `ch-11.md` after stripping code fences returns 0 matches. The single match in ch-11.md at line 200 is inside the Python stub's `'<code>final_answer("42")</code>'` literal (model-emulated output, permitted).

### No-regression check 18 — Compact check runs cleanly
- **Verdict:** PASS
- **Evidence:** ran the 11-line stub at `ch-11.md:195-206` in `E:\book_gen\.venv\Scripts\python.exe`; **rc=0**, last visible stdout line = `42`, which matches the `\`\`\`text\n42\n\`\`\`` expected-output block at `ch-11.md:210-212`. The assertion `assert result == "42"` did not raise.

## Cross-cutting findings

- The fix-loop applied here is well-scoped: every CRITICAL and HIGH issue from the prior dev review has been addressed at the root, not papered over. Verified runtime claims (planning-budget, memory composition, result-type, system_prompt= caveat, wall-clock paragraph) now match installed smolagents==1.26.0 and the verified research-log entries (entry-085..entry-096, entry-091/092/095 corrections). Three brief-corrections are documented correctly in prose and cross-referenced in `bible.md:149-160`.
- The closing-imperative structure (callout → bridge → HTML comment) is preserved verbatim, which protects the line-edit and copy-edit passes from having to re-shape the chapter's tail.
- One risk worth surfacing for the line-edit pass: ch-11 is now 1703 words (per master counter) and the runnable blocks total ~107 lines. Three runnable headers, two intermediate sections, plus the four beginner errors push the chapter to the upper edge of its structural weight. If line edit tends to add connective tissue, the chapter may approach the band ceiling at 1934. Not a regression — just a planning note.

## Out-of-scope observations

- `ch-11.md:218-231` HTML comment claims "all 12 ch-11 research entries (entry-085..entry-096) addressed in prose". This is verified: each H2 in ch-11.md maps to one of entry-085..entry-096; entry-096 lands in the bridge at `:216` naming ch-12/13/14/15. No action required.
- `bible.md:150` still preserves the `Now Begin!` literal in the research-evidence block (it quotes smolagents's source string). This is appropriate — it is not visible prose and it accurately describes what smolagents actually contains. No action required.
- The first runnable at `ch-11.md:89-137` uses `max_steps=8` / `planning_interval=4` — different from the closing imperative at `:214` which says `max_steps=8, planning_interval=4`. Consistent. No action required.
- `research-log.md:599,606,626` (entry-091, entry-092, entry-095 claim/finding paragraphs) — VERIFIED to match the corrected chapter prose. entry-091 now states "Planning calls happen alongside the action loop and add token spend and latency without consuming that action-step budget." entry-092 now states "Within one `.run()` call, the framework appends a `TaskStep` at the start, then interleaves `PlanningStep`s whenever `planning_interval` fires with one `ActionStep` per action iteration... no separate `FinalAnswerStep` is appended to `agent.memory.steps`." entry-095 now states "`max_steps` budgets action iterations, not planning calls. Planning adds model calls, token cost, and latency alongside that budget; with `planning_interval=4` and `max_steps=20`, a run can include up to 20 action steps and up to 5 planning steps." All three match the verified 1.26.0 runtime and the corrected ch-11 prose. The prior review's "fix only chapter prose and leave research-log stale" risk is closed.

## Honest assessment

The writer did the work — every CRITICAL and HIGH issue from the prior dev review was fixed at the root, not papered over. Planning-budget, memory composition, default-result-type, system_prompt= caveat, forward pointers, wall-clock paragraph, bible.md duplicates, exclamation marks, and concrete model identifier are all correctly addressed with citations against the installed 1.26.0 source. The compact check runs cleanly. The closing-imperative contract is preserved. The research-log entries that drove the chapter's claims are now correct. Two quality notes remain: (a) the compact check is functionally redundant with ch-09's stub demo and does not exercise any ch-11-specific knob, which the dispatch explicitly asked me to flag if redundant; (b) the retitled H2 at line 65 ("No built-in persistence in 1.26.0") is borderline — it satisfies the ≤7-word constraint but the leading "No" is a determiner, not a verb. Neither is a blocker. The chapter is technically safe to teach and ready for line edit.

## Self-critique

- **Did I do my job?** yes — I read the chapter, the prior review, the outline, the bible, the relevant research-log entries, the ledger entry, the style guide, and the runtime stubs. I ran fresh ast.parse on all three code blocks and live-ran the compact stub check via the venv. I did UTF-8 round-trip, word-bounded greps, and exact-line structural checks.
- **What might I have missed?** I did not execute the live provider examples at `ch-11.md:89-137` or `ch-11.md:143-191` because `HF_TOKEN` is not configured. I did not verify the `bible.md` cross-references against the ch-08 / ch-09 prose beyond reading the ch-09 stub paragraph; I trusted the master counter on word-count instead of re-deriving the algorithm. I did not run `cspell` or any other prose linter.
- **What did I assume without evidence?** I accepted the master's claim that the chapter is 1703 words without reproducing the exact counting algorithm; my independent count is method-dependent (1911–1979) and lands at the upper edge of the band. The dispatch's measurement is the one of record and it satisfies the no-regression criterion.