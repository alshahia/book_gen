# Developmental Review — T-2026-08-01-001-book-ai-agents-with-python / ch-11

**Date:** 2026-08-02
**Sub-agent:** am-review
**Pass:** developmental review

## Summary

- **Overall verdict:** FAIL
- **Chapter reviewed:** `books/ai-agents-with-python/chapters/ch-11.md`
- **Per-task Pass / Warn / Fail:** 0 / 0 / 1
- **Issue counts:** 3 CRITICAL / 5 HIGH / 4 MEDIUM / 0 LOW
- **Block progression to line edit?** yes

The chapter is structurally readable and covers most requested surfaces, but it cannot progress because two core smolagents explanations are false, the first runnable contains a type assertion that valid agent output can fail, and the mandatory closing callout is absent.

## Tests / build run

- `Select-String -Path "E:\book_gen\books\ai-agents-with-python\chapters\ch-11.md" -Pattern "HfApiModel|ApiModel"` — **PASS**, 0 matches.
- `Select-String -Path "E:\book_gen\books\ai-agents-with-python\chapters\ch-11.md" -Pattern "\bfinal_answer\b"` — **PASS**, 0 matches.
- Case-insensitive word-boundary blacklist scan — **PASS**, 0 matches.
- Strict UTF-8 decode using `UTF8Encoding(false, true)` — **PASS**, zero decode errors.
- Venv AST check with `E:\book_gen\.venv\Scripts\python.exe` — **PASS**, 2/2 Python blocks parsed with `ast.parse`.
- Installed API signature probe against smolagents 1.26.0 — **PASS for the requested surface**: `MultiStepAgent.__init__` contains `prompt_templates`, `instructions`, `max_steps`, and `planning_interval`; `.run()` contains `reset`, `additional_args`, and `return_full_result`; neither signature contains `max_duration` or `chat_messages`.
- `RunResult` dataclass probe — **PASS**, fields are `output`, `state`, `steps`, `token_usage`, and `timing`.
- Runtime stub probe, `final_answer(5)` with default return mode — **FAIL for manuscript claim**: `.run()` returned `int` value `5`, not `str`. This disproves `ch-11.md:41` and makes the assertion at `ch-11.md:129` unsafe.
- Runtime planning probe, `max_steps=1, planning_interval=1` — **FAIL for manuscript claim**: run completed with `state="success"`, 2 model calls, and memory types `TaskStep`, `PlanningStep`, `ActionStep`. A planning call does not consume the action-step budget as claimed at `ch-11.md:83`.
- Structural scan — orientation 51–53 words depending inline-code tokenization; longest visible prose paragraph below 80 words; longest H2 6 words; 13 H2s.
- Full live provider execution — **not run** because the examples intentionally require `HF_TOKEN`; syntax and API semantics were tested independently with the installed venv and deterministic stubs.

## Required checklist

| # | Check | Verdict | Evidence |
|---|---|---|---|
| 1 | Outline coverage, entry-085..entry-096 | **FAIL** | Most entries appear, but entry-086's required statement that direct `system_prompt=` raises `TypeError` is absent at `ch-11.md:13-17`; entry-092 is described incorrectly at `ch-11.md:53`; entry-095 repeats the false planning-budget claim at `ch-11.md:83`; entry-096's forward mapping is stale at `ch-11.md:43,189`. |
| 2 | Voice match | **FAIL** | Second-person, conversational tone and contractions generally match, but visible prose contains exclamation marks inside the quoted literal at `ch-11.md:9,21`, violating the absolute no-exclamation rule in `style-guide.md:163-165`. |
| 3 | Vocabulary blacklist | **PASS** | 0 case-insensitive word-boundary matches for all ten prohibited expressions. |
| 4 | Bible consistency | **FAIL** | The ch-11 block exists and contains all required terms at `bible.md:149-160`, but `RunResult` and `max_steps` repeat prior definitions at `bible.md:20,121,130`; `bible.md:157` also repeats the incorrect memory-step description. |
| 5 | Research grounding | **FAIL** | Source citations are frequent, but source interpretation is not reliable: `ch-11.md:53,83` contradict fresh 1.26.0 runtime probes. The timeout recommendation at `ch-11.md:49` also overstates what `concurrent.futures` and `asyncio.wait_for` can do for synchronous `.run()`. |
| 6 | Code-block correctness | **FAIL** | Signatures and 2/2 AST checks pass, but `assert isinstance(result, str)` at `ch-11.md:129` is invalid for legitimate non-string final output. Installed 1.26.0 returned integer `5` from a valid stub run. |
| 7 | Beginner accessibility | **FAIL** | Orientation length, paragraph length, and H2 length pass (`ch-11.md:3`; all visible paragraphs; `ch-11.md:7-136`). Several H2s are descriptive topics rather than action-y moves, notably `ch-11.md:19,33,39,51,65`. The chapter also lacks the style guide's required 5–20-line runnable check with expected output (`style-guide.md:53-59`). |
| 8 | Closing-imperative contract | **FAIL** | `ch-11.md:187` is imperative and correctly precedes the thin bridge, but it is a plain paragraph. The required `> **The move:**` callout does not exist anywhere in the chapter. |
| 9 | Forward-pointer hygiene | **FAIL** | `ch-11.md:189` names ch-12, but assigns it ch-13's current title/content. It then assigns testing to ch-13 instead of ch-14 and safety to ch-14 instead of ch-15; compare `outline.md:941-1101,1151-1171`. |
| 10 | UTF-8 clean | **PASS** | Strict byte decode completed with zero errors. |
| 11 | No regression vs prior chapters | **FAIL** | The ledger row is correctly `drafted`, depends on ch-10, and records 1758 words at `ledger.md:193`. The Bible append is physically non-destructive, but its duplicate and false claims at `bible.md:155-157` violate the consistency requirement. |

## Per-task verdicts

### T-2026-08-01-001-book-ai-agents-with-python / ch-11 — developmental review

- **Verdict:** FAIL
- **Outcome match:** Partial. The chapter teaches every named knob and ends with a near-verbatim imperative at `ch-11.md:187`, but core explanations of `max_steps`, memory-step composition, and default result type are wrong.
- **Voice and structure:** Readable and within the supplied length ceilings, but the closing callout and runnable-check formats do not satisfy the style guide.
- **Technical correctness:** Fails fresh installed-runtime verification.
- **Evidence:** `ch-11.md:41,49,53,83,129,187,189`; `bible.md:155-157`; `outline.md:941-1171`; runtime results listed above.

### Issues

- [CRITICAL] `ch-11.md:187` omits the mandatory `> **The move:**` callout marker. The sentence is imperative, but the explicit whole-book closing contract says the callout itself must be present and final before the allowed bridge.
- [CRITICAL] `ch-11.md:41,129` claim the bare answer is a string and assert `isinstance(result, str)`. Installed smolagents 1.26.0 validly returned the integer `5` from `final_answer(5)`. `RunResult.output` and the bare result are `Any`, so the runnable can fail even when the agent succeeds.
- [CRITICAL] `ch-11.md:83` says a planning step consumes `max_steps` and that two plan/action iterations total four budgeted steps. Fresh runtime evidence disproves this: `max_steps=1, planning_interval=1` completed successfully after one planning model call and one action model call. `max_steps` budgets action-loop iterations, while planning calls add cost without consuming that counter.
- [HIGH] `ch-11.md:53` says an iteration appends an `ActionStep` *or* a `PlanningStep`, followed by a `FinalAnswerStep`. Installed 1.26.0 produced `TaskStep + PlanningStep + ActionStep`; planning and action both occur, and a successful final tool call remains the final `ActionStep`. The same false model is appended to the whole-book Bible at `bible.md:157`.
- [HIGH] `ch-11.md:13-17` never states entry-086's required correction: `system_prompt=` is not a constructor kwarg and raises `TypeError`. It explains `prompt_templates` replacement but leaves the named beginner trap incomplete; compare `research-log.md:563-567`.
- [HIGH] `ch-11.md:43,189` use stale chapter numbering. Current `outline.md:941-1101,1151-1171` places structured workflows in ch-12, observe/debug/evaluate in ch-13, testing in ch-14, and safety in ch-15.
- [HIGH] `ch-11.md:85-185` does not provide the required compact runnable check with an expected-output block; the examples are roughly 40 lines each, and the second has no failing check. This violates `style-guide.md:53-59` independently of the incorrect assertion in the first block.
- [HIGH] `ch-11.md:49` advises wrapping synchronous `.run()` with `asyncio.wait_for` or `concurrent.futures` as a wall-clock cap. `asyncio.wait_for` needs an awaitable, and a future timeout stops waiting but does not necessarily stop the underlying worker. The prose must distinguish a wait timeout from terminating agent execution.
- [MEDIUM] `bible.md:155-156` redefines `RunResult` and `max_steps` after those terms were already established at `bible.md:20,121,130`. The requested append must add ch-11-specific distinctions or cross-reference existing entries instead of duplicating them.
- [MEDIUM] `ch-11.md:9,21` contain visible exclamation marks in the literal prompt text, conflicting with `style-guide.md:163-165`. Preserve the technical fact without reproducing the punctuation in visible prose, or document an explicit quotation exception in the style contract.
- [MEDIUM] H2s at `ch-11.md:19,33,39,51,65` are descriptive labels rather than action-y fragments, contrary to `style-guide.md:23-26` and checklist item 7.
- [MEDIUM] The concrete model identifier at `ch-11.md:118,169` conflicts with the directional age-risk rule in `style-guide.md:139-153`. Read the model identifier from configuration or use the book's approved directional pattern.

- **Suggested fix:** Correct the four runtime/API explanations first, replace the broken assertion with an assertion on the known example outcome or `RunResult` state/fields, add one compact deterministic check with expected output, repair the current chapter pointers, deduplicate/correct the Bible append, and restore the exact closing callout form.

## Cross-cutting findings

- The incorrect planning-budget and memory-step claims originate upstream: `research-log.md:603-607,623-627` contains the same false interpretation. Fixing only chapter prose would leave the next writer exposed to the same error.
- `research-log.md:554-633` still labels entries 085–096 as ch-10 and carries pre-renumbering forward pointers, while the current manuscript and outline place this material in ch-11. That stale metadata likely caused the broken bridge.
- Syntax-only verification was insufficient here. Both code blocks parse, yet one contains a semantically invalid assertion and the prose misstates runtime behavior.

## Out-of-scope observations

- `environment.md:81-89` does not record ch-11 as tested. Update it only in the appropriate writer/master lane after corrected examples are revalidated.
- The style-guide outcome table at `style-guide.md:77` asks for `planning_interval=2`, a three-step run, and inspection of `RunResult.steps`, while the dispatch's verbatim outcome is broader. Master should resolve that stale contract before the fix loop so the writer is not judged against two different closing actions.

## Honest assessment

This draft is clear enough to read but not technically safe to teach. The planning-budget claim, memory-step model, and default-result-type claim are all central to the chapter and fail against the installed 1.26.0 runtime; one of them directly breaks the runnable's assertion. The chapter needs a focused correctness pass and an upstream research correction before developmental approval.

## Self-critique

- **Did I do my job?** yes — I read the chapter, outline, style guide, Bible, ledger, environment, relevant research entries, and controller review rules; I ran fresh source/signature, AST, encoding, structural, and deterministic runtime checks.
- **What might I have missed?** I did not execute the live Hugging Face examples because no token is configured, and I did not assess model-quality claims with a live provider.
- **What did I assume without evidence?** I accepted the supplied 1758-word count rather than reproducing the writer's exact prose-count algorithm; independent structural counts still confirmed all requested length ceilings.
