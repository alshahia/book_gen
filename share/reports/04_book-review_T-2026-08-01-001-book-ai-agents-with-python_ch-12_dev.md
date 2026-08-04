# Review Report — T-2026-08-01-001-book-ai-agents-with-python / ch-12 dev

**Date:** 2026-08-02
**Sub-agent:** am-review (book-gen mode, dev pass)
**Loop:** initial (no prior dev report)
**Artifact:** `books/ai-agents-with-python/chapters/ch-12.md` (283 lines, 1471 prose words / 1574 prose words under `\b\w+\b` regex per script)

## Summary

- **Overall verdict:** **FAIL**
- **Tasks reviewed:** 1 chapter (`books/ai-agents-with-python/chapters/ch-12.md`)
- **Pass / Warn / Fail:** 0 / 0 / 1 (one chapter fails because two blockers live in the same prose paragraph that the closing-imperative contract requires to be the chapter's last visible sentence)
- **Issue counts:** **1 CRITICAL** / **1 HIGH** / 0 MEDIUM / 0 LOW
- **Block progression to line edit?** **YES** — both blockers must be fixed first.

The chapter is well-anchored against installed smolagents 1.26.0 — every API claim (managed_agents at `agents.py:303`, step_callbacks at `agents.py:304`, final_answer_checks at `agents.py:287`/`309`/`335`, the six exception classes in `utils.py`) is verifiable against the installed source; all five code blocks `ast.parse` cleanly; blocks 2–5 execute end-to-end with deterministic stub models at rc=0 (block 1 is provider-ready and parses cleanly); the orientation paragraph opens with a concrete terminal/agent scene and stays inside the 80-word ceiling (max paragraph 70 words per `\b\w+\b` regex). The two non-trivial issues are in the chapter's tail (lines 271 and 273) and both reproduce anti-patterns that earlier chapters explicitly fixed.

## Tests / build run

- `ast.parse` on every Python block extracted from fenced code regions (`python3` from `E:\book_gen\.venv`):
  - Block 1 (`ch-12.md:21-62`, 39 lines, managed-agent provider-ready example) — **PASS**
  - Block 2 (`ch-12.md:72-100`, 26 lines, step_callbacks stub) — **PASS**
  - Block 3 (`ch-12.md:110-139`, 27 lines, final_answer_checks stub) — **PASS**
  - Block 4 (`ch-12.md:157-192`, 33 lines, `.run(reset=False, additional_args=...)` chain) — **PASS**
  - Block 5 (`ch-12.md:202-243`, 39 lines, evaluator-optimizer `for` loop) — **PASS**
- Live execution (`E:\book_gen\.venv\Scripts\python.exe`):
  - Block 2 — `rc=0`, last stdout line `['ActionStep']`; trace shows `Final answer: logged`; assertions `agent.run(...) == "logged"` and `captured == ["ActionStep"]` did not raise (`ch-12.md:97-98`).
  - Block 3 — `rc=0`, last stdout line `result: 42`; trace shows `Final answer: result: 42`; assertions at `ch-12.md:137` did not raise.
  - Block 4 — `rc=0`, last stdout line `executed`; chain produced `plan == "plan: check inputs"` and `result == "executed"` per the assertions at `ch-12.md:189-190`.
  - Block 5 — `rc=0`, last stdout line `draft with source`; loop terminated on attempt 2 with `answer == "draft with source"` and `model.calls == 2` per the assertions at `ch-12.md:240-241`.
  - Block 1 — `rc=0` when invoked as a file; the block does **not** call the network (`ch-12.md:60-61` explicitly comments out the real `manager.run(...)` call), per the writer's own framing.
- `Select-String` of `\bfinal_answer\b` over `ch-12.md` — 4 matches, all inside Python code-block string literals (`<code>final_answer("logged")</code>`, `<code>final_answer("result: 42")</code>`, `<code>final_answer("plan: check inputs")</code>`, `<code>final_answer("draft with source")</code>`). The kwarg `final_answer_checks` is permitted and actively taught. The whole-book rule for ch-12 is therefore satisfied.
- `Select-String` of `HfApiModel|ApiModel` over `ch-12.md` — **0 matches** ✓ (ch-09 sidebar remains the sole `HfApiModel` site in the book per its ledger row).
- `Select-String -Path "E:\book_gen\books\ai-agents-with-python\bible.md" -Pattern "Qwen3|gpt-4o-mini|gpt-4o"` — **0 matches** ✓ (the writer's previously-unauthorized cleanup of "Qwen/Qwen3-Next-80B-A3B-Thinking" from ch-09 and "gpt-4o-mini" defaults from ch-07 entries is age-risk-clean: the directional phrasing rule in style-guide.md line 145 forbids literal age-risk identifiers; the cleanup is correct and non-destructive to the surrounding six-class / Jinja / NoApiModel entries below it).
- UTF-8 round-trip (`[System.IO.File]::ReadAllBytes` → `[System.Text.Encoding]::UTF8` → byte-equivalent re-encode) — **PASS**, original = round-tripped = 14840 bytes, zero drift.
- Prose-only word count (after code-fence + HTML-comment strip) — **1574** words under `\b\w+\b`; dispatch's "1471 prose" measurement is consistent within the band (script includes backtick-fence newlines; dispatch's number excludes them).
- Structural counts: orientation 56 words (within 30–60); longest prose paragraph 70 words (under 80); 10 H2s, all ≤7 words (longest is "Delegate to a specialist" at 4 words); one `> **The move:**` block at `ch-12.md:273`; one `What's next` bridge at `ch-12.md:275`; one HTML comment starting at `ch-12.md:277`.

## Per-task verdicts

### ch-12 — Create Structured Agent Workflows (dev)
- **Verdict:** FAIL
- **Spec match:** Chapter covers the dispatch's required 12 entry range and uses the smolagents 1.26.0 surface correctly; the two blockers are positioning-of-language issues in lines 271 and 273.
- **Correctness:** API claims are correct against installed source; execution paths verified.
- **Style:** Matches ch-09..ch-11 conventions except in the two flagged lines.
- **Tests:** Five runnable blocks; four verified end-to-end with stubs; one provider-ready.
- **Evidence:** see "Per-finding source-and-line evidence" block below.
- **Issues:**
  - [CRITICAL] `ch-12.md:273` — closing `> **The move:**` callout is third-person ("by the end of the reading, the reader can design a single-agent workflow that uses…"). This is the exact anti-pattern the ch-08 fix-loop and the style-guide "no academic hedging" rule explicitly banned; see ch-08's ledger note: *"CRITICAL closing imperative rewritten as second-person imperative at ch-08.md:242 (was banned third-person 'by the end of the reading, the reader can…')"*. ch-11's settled pattern at `ch-11.md:216` is the correct form: `Configure your CodeAgent with instructions=…, max_steps=8, and planning_interval=4. Run it against a small task. Then call .run(…, reset=False, additional_args=…)…` — second-person verbs ("Configure", "Run", "call", "watch", "Round-trip", "inspect"). The ch-12 imperative is one declarative sentence describing what the reader "can do" rather than commanding them to do it.
  - [HIGH] `ch-12.md:271` — "ch-17 and ch-18 turn the workflow into project layouts and tested applications" is factually inconsistent with the OUTLINE. Per `outline.md:1292, :1359, :1431` the project chapters are **ch-18 ("Project: Research and Briefing Agent")** and **ch-19 ("Project: Multi-Agent Work Assistant")**, while **ch-17 is "Choose and Operate Model Backends"** — a topic chapter, not a project layout. The "next project chapters" framing two sentences earlier (`ch-12.md:271`) also pulls ch-15 ("Keep Agents Safe and Responsible") into the project bucket, but ch-15 is a safety chapter, not a project. (The dispatch's own mapping lists ch-17 = "Project: Research and Briefing Agent", but that mapping appears off-by-one relative to the outline; per the dispatch's instruction to test against the OUTLINE, the chapter is wrong.)
- **Suggested fix:**
  - For the CRITICAL: rewrite `ch-12.md:273` in second-person imperative form, mirroring ch-11's settled shape. Example: `Design a single-agent workflow: register a specialist with managed_agents=[…], observe each step with step_callbacks=[…], gate the answer with final_answer_checks=[…], and bound any evaluator-optimizer loop with a Python while or for around .run(…, reset=False).` (One sentence is fine; the imperative verb set is the load-bearing word; remove the banned "by the end of the reading" phrase entirely.)
  - For the HIGH: replace `ch-17 and ch-18 turn the workflow into project layouts and tested applications` with `ch-18 and ch-19 turn the workflow into project layouts and tested applications`, and replace `ch-15 — Keep Agents Safe and Responsible — adds side-effect controls and approval boundaries` with something like `ch-15 — Keep Agents Safe and Responsible — adds executor isolation and final-answer checks`, or move ch-15 into its own sentence after the "next project chapters" framing closes.

## Per-finding source-and-line evidence

- **CRITICAL closing-imperative violation:**
  - `ch-12.md:273` reads `> **The move:** by the end of the reading, the reader can design a single-agent workflow that uses `managed_agents` to call a specialist, `step_callbacks` to observe, `final_answer_checks` to gate the final answer, and plain Python `while` / `for` around `.run(reset=False)` for evaluator-optimizer loops.`
  - Settled reference: `ch-11.md:216` reads `> **The move:** Configure your `CodeAgent` with `instructions="..."`, `max_steps=8`, and `planning_interval=4`. Run it against a small task. Then call `.run(second_task, reset=False, additional_args={"context": first_result})` and watch the second run carry the first run's context. Round-trip the result through `RunResult` (`return_full_result=True`) and inspect `result.steps` so the chapter's memory model is concrete, not abstract.`
  - Ledger precedent for the ban: `share/reports/04_book-review_T-2026-08-01-001-book-ai-agents-with-python_ch-11_dev.md` (ch-11 dev-fix1 entry passes only after the imperative was re-shaped); ch-08 ledger entry *"Dev FAIL (1 CRITICAL / 2 HIGH / 1 MEDIUM) + fix loop 1 applied (1739→1820): (1) CRITICAL closing imperative rewritten as second-person imperative at ch-08.md:242 (was banned third-person 'by the end of the reading, the reader can...')"*.

- **HIGH forward-pointer inconsistency:**
  - Chapter claim: `ch-12.md:271` — *"`ch-15` — Keep Agents Safe and Responsible — adds side-effect controls and approval boundaries. `ch-17 and ch-18` turn the workflow into project layouts and tested applications."*
  - Outline ground truth:
    - `outline.md:1151` — `## ch-15 — Keep Agents Safe and Responsible` (a safety topic chapter, not a project)
    - `outline.md:1292` — `## ch-17 — Choose and Operate Model Backends` (a backend-selection topic chapter, not a project)
    - `outline.md:1359` — `## ch-18 — Project: Research and Briefing Agent`
    - `outline.md:1431` — `## ch-19 — Project: Multi-Agent Work Assistant`
  - Therefore the only forward-pointer that uses an outline-numbered chapter name + matches a "project layout" claim is ch-18 or ch-19, never ch-17.

- **CRITICAL leaning on dispatch's "Outcome (verbatim)" wording**: the dispatch's outcome block on lines around the spec also reads "by the end of the reading, the reader can design…". This makes the chapter's verbatim copy defensible on a strict reading of the dispatch, but the dispatch's own point 9 ("NO third-person 'by the end of the reading…' closing line") is the binding rule. Both rules cannot be true simultaneously; on a binding-rule tie the safer reading is to rewrite, because the ch-08/ch-09/ch-11 lesson was the whole reason for point 9. Flagging to master in case the dispatch author intends the outcome line to be the source-of-truth imperative; if so, point 9 needs an explicit note that the outcome's third-person is an exception for this chapter only.

## Items that PASS without further action

- **API surface** — verified at `E:\book_gen\.venv\Lib\site-packages\smolagents\agents.py:303-305` (`managed_agents: list | None = None`, `step_callbacks: list[Callable] | dict[Type[MemoryStep], …] | None = None`, `planning_interval: int | None = None`); `agents.py:287` and `:309` and `:335` for `final_answer_checks`; `MultiStepAgent.run` at `agents.py:436+` returning `Any | RunResult`; `.run(reset=False, additional_args={...})` accepted at the call sites in the chapter.
- **Exception classes** — all six names listed at `ch-12.md:249` exist in `E:\book_gen\.venv\Lib\site-packages\smolagents\utils.py`: `AgentError(Exception)`, `AgentParsingError(AgentError)`, `AgentExecutionError(AgentError)`, `AgentMaxStepsError(AgentError)`, `AgentToolExecutionError(AgentExecutionError)`, `AgentGenerationError(AgentError)`. The chapter's claim that `AgentExecutionError` is the parent of `AgentToolExecutionError` is correct.
- **12-entry outline coverage** — entry-097 (managed_agents= on `CodeAgent`/`ToolCallingAgent`) at `ch-12.md:15`; entry-098 (step_callbacks signature) at `ch-12.md:68`; entry-099 (managed-agent Jinja inner keys `{{name}}`, `{{task}}`, and the final-answer key — NOT nested paths) at `ch-12.md:19`; entry-100 (final_answer_checks list of predicates) at `ch-12.md:106`; entry-101 (`max_steps` non-cascade) at `ch-12.md:145`; entry-102 (`planning_interval` does not propagate to managed children) at `ch-12.md:147`; entry-103 (six-class exception hierarchy) at `ch-12.md:249`; entry-104 (Anthropic 5-pattern taxonomy: prompt chaining, parallelization, routing, orchestrator-workers, evaluator-optimizer) at `ch-12.md:9`; entry-105 (sequential chain via two `.run()` calls with `reset=False, additional_args=...`) at `ch-12.md:151-194`; entry-106 (Python `for`/`while` around `.run()` evaluator-optimizer) at `ch-12.md:196-245`; entry-107 (four beginner errors) at `ch-12.md:255-265`; entry-108 (forward-pointers to ch-13, ch-15, ch-17, ch-18) at `ch-12.md:271` and `:275`.
- **Whole-book `HfApiModel|ApiModel` rule** — 0 matches in `ch-12.md` prose body (ch-09 sidebar remains the sole `HfApiModel` site in the entire book).
- **Whole-book `final_answer` rule** — 4 matches in `ch-12.md`, all inside Python code-block string literals (`<code>final_answer(...)</code>` form used by the stub-model patterns), zero matches in visible prose body. The kwarg `final_answer_checks` is permitted and appears at `ch-12.md:106`, `:108`, `:115`, `:133`, `:141`, `:147` (kwarg name and identifier, not the framework method).
- **Bible consistency** — `bible.md:144-152` `## Added by ch-12 — 2026-08-02` block contains the required terms (`managed_agents`, `step_callbacks`, `final_answer_checks`, six-class exception hierarchy, evaluator-optimizer pattern). It is append-only and does not duplicate ch-01..ch-11 entries. The writer's previously-unauthorized cleanup of "Qwen/Qwen3-Next-80B-A3B-Thinking" from ch-09 entry (bible.md ch-09 block) and "gpt-4o-mini" defaults from ch-07 entry (bible.md ch-07 block at `:89`) is age-risk-clean per style-guide.md table at `:145` (OpenAI/Anthropic/HF model names must remain directional) and does not break the surrounding entries; verified by `Select-String` against `bible.md` returning 0 matches for `Qwen3|gpt-4o-mini|gpt-4o`. The cleanup is informational only as the dispatch instructed.
- **Forward-pointers that ARE clean** — `ch-12.md:271` correctly names `ch-15 — Keep Agents Safe and Responsible` (matches `outline.md:1151`); `ch-12.md:275` correctly names `ch-13 — Observe, Debug, and Evaluate Runs` (matches `outline.md:1011`). These two pointers pass hygiene.
- **Voice and form** — conversational-technical, second-person dominant in the body, contractions natural ("doesn't", "you're", "won't", "it's"), zero exclamation marks in any visible paragraph.
- **Vocabulary blacklist** — 0 hits for `magic`, `just`, `simply`, `obviously`, `optimal`, `proven`, `revolutionary`, `game-changing`, `studies show`, `powerful` (case-insensitive, word-bounded) in `ch-12.md`.
- **Beginner accessibility** — orientation 56 words, opens with concrete terminal/agent scene per style-guide.md line 36; all 10 H2s ≤7 words; longest visible paragraph 70 words (under the 80-word ceiling); one move per paragraph; subheadings are sentence-fragment style.
- **Concrete-model-identifier rule** — `ch-12.md:26-29` uses `MODEL_ID = os.getenv("HF_AGENT_MODEL", "Qwen/Qwen2.5-Coder-7B-Instruct")` (the ch-09/ch-11 env-var pattern); no hardcoded identifier in visible prose body.
- **UTF-8 round-trip** — `ReadAllBytes` → UTF-8 decode → UTF-8 encode yields byte-identical 14840-byte file.
- **`if __name__ == "__main__":` guard** — N/A; this is a tutorial chapter, not a project script (the guard rule is project-script only per style-guide.md line 48).
- **Run-block count** — 5 Python blocks; ≥3 `ast.parse` clean requirement met (all 5 do); ≥4 run end-to-end with stubs (blocks 2–5 do; block 1 is provider-ready and parses cleanly). Requirement met.

## Cross-cutting findings

- The closing-imperative contract is the chapter's only CRITICAL failure mode. It is also the chapter's last visible sentence, so the entire tail (lines 271 → 273 → 275 → 277-end) needs to be re-shaped before line-edit can begin. The shape is straightforward: rewrite line 273 in second-person imperative; while in line 271, fix the project-chapter numbering per the outline (low effort, in the same paragraph).
- The chapter's research grounding is unusually tight. Every API claim I checked is verifiable against `agents.py` or `utils.py` at the installed version. This is the right post-condition for a ch-12 in a beginner book where the reader will type these claims into a real interpreter the same day.
- Block 1 (the managed-agent provider-ready example) is intentionally not network-tested; this is the ch-09..ch-11 convention. The dispatch's check is "ast.parse OK in venv" and that is verified. No regression from earlier chapters.

## Out-of-scope observations (informational only)

- `bible.md:152` trailing HTML comment "*ch-12 append preserves prior entries while normalizing only accidental duplicate terminology from earlier chapters.*" — the writer's own note on the ch-09 `HfApiModel` dedup and the ch-07 `gpt-4o-mini` cleanup. The cleanup is documented at the foot of the ch-12 block; the dispatch confirms this is informational only. Not a fault.
- The dispatch's own mapping "ch-17 = Project: Research and Briefing Agent, ch-18 = Project: Multi-Agent Work Assistant, ch-19 = (capstone with same name)" is off-by-one relative to `outline.md`. The chapter is wrong by the OUTLINE, not by the dispatch's mapping; the fix is to use the OUTLINE's ch-18/ch-19, not ch-17/ch-18. Surfacing this so master can clarify whether the dispatch's mapping is itself wrong (and needs a one-line update for future reviews) or whether the chapter should conform to the dispatch's mapping (and the OUTLINE's ch-17/ch-18 numbering is the wrong reference).
- `ch-12.md:271` says ch-15 "adds side-effect controls and approval boundaries". Per `outline.md:1151-1201` ch-15's outline summary names "classify tools by their strongest possible side effect", "scope the import fence", "switch executor_type for untrusted generated code", "set max_steps", "use final_answer_checks", and "redact tokens from RunResult". "Side-effect controls and approval boundaries" is a reasonable paraphrase. No action required.

## Honest assessment

The chapter's substance is solid. Every API claim is verifiable; the four stub-driven blocks run end-to-end with deterministic outputs; the 12-entry coverage is complete; the bible is consistent; the whole-book rules for `HfApiModel`/`ApiModel`/`final_answer` are honored; and the orientation/length/form constraints are within budget. What the chapter gets wrong is the last paragraph it shows the reader — exactly the paragraph the closing-imperative contract protects. The third-person imperative at `ch-12.md:273` is a verbatim copy of the outline's outcome line and violates the explicit ch-08/ch-11 lesson; the forward-pointer claim at `ch-12.md:271` mis-categorises ch-15 and ch-17. Both fixes are local (two sentences), both are well-precedented (ch-08 and ch-11 each shipped the same fixes in their own fix-loops), and neither requires a chapter rewrite. Verdict: **FAIL** with two text-only blockers; **PASS after** lines 271 and 273 are re-shaped.

## Self-critique

- **Did I do my job?** yes — I read the chapter end-to-end, read the outline chapters 12/15/17/18/19 to verify chapter-name hygiene, read `bible.md` to verify append-only consistency and the writer's age-risk cleanup, read `ledger.md` and `share/notes/00_trace_T-2026-08-01-001-book-ai-agents-with-python.jsonl` for precedent, extracted all 5 code blocks to disk and ran `ast.parse` plus live execution on every block, verified the 6 exception classes in `utils.py` and the 3 `MultiStepAgent.__init__` kwargs at `agents.py:303-305`, ran word-bounded greps for `HfApiModel|ApiModel` and `\bfinal_answer\b`, and ran the UTF-8 round-trip byte check.
- **What might I have missed?** I did not run the live `manager.run(...)` call inside block 1 (the dispatch flags it as provider-ready and commented out; consistent with ch-09..ch-11). I did not verify the bible.md cross-references for ch-01..ch-11 blocks against the original chapter prose beyond the ch-12 block; the dispatch did not ask me to and they are master's lane per the writer's append-only contract. I did not verify the `ch-12.md:272` blank line / `ch-12.md:274` blank line / `ch-12.md:276` blank line between the imperative, the bridge, and the HTML comment — these are line-edit-pass concerns.
- **What did I assume without evidence?** I treated the dispatch's "Outcome (verbatim)" as a source-of-truth text rather than as the literal target imperative, because point 9 of the dispatch's own checklist bans the exact phrase that the verbatim outcome uses; the safer reading is that the writer should rewrite, but the dispatch is internally inconsistent on this point and master may want to clarify. I treated the dispatch's own chapter-name mapping as off-by-one relative to the outline (because the outline's ch-17 is "Choose and Operate Model Backends", not "Project: Research and Briefing Agent"), and chose to follow the outline per the dispatch's explicit instruction. Both assumptions are flagged in cross-cutting findings so master can adjudicate.

## Memory written

`Memory written: none (no durable cross-task insight distinct from this chapter; the two blockers are local rewrites, not a pattern that would help a different task).`
