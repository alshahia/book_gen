# Review Report — T-2026-08-01-001-book-ai-agents-with-python / ch-16 developmental

**Date:** 2026-08-03
**Sub-agent:** review
**Loop:** initial

## Summary
- **Overall verdict:** FAIL
- **Tasks reviewed:** 1 (`B7T1` — developmental review)
- **Pass / Warn / Fail:** 0 / 0 / 1
- **Block release?** yes
- **Issue counts:** 2 CRITICAL, 4 HIGH, 2 MEDIUM, 0 LOW

The two Python examples run cleanly against the pinned `smolagents==1.26.0` environment, and the current source citations are accurate. The chapter still fails the developmental gate because its closing is the prohibited third-person outcome line, the bible appears destructive rather than append-only, two required research/forward-pointer items are incomplete, the reserved keyword appears in prose, and the ledger row is stale.

## Tests / build run
- No repo-specific test command is documented. `agents_manager/coder/resources/README.md:1-26` is only the generic resource README, so there was no documented project test command to run.
- **Code-block smoke test:** extracted both `python` fences from `books/ai-agents-with-python/chapters/ch-16.md` and ran each in `E:\book_gen\.venv\Scripts\python.exe`. Block 1 (`ch-16.md:18-75`) exited **0**; block 2 (`ch-16.md:89-108`) exited **0**. The first block produced the researcher and writer managed-agent outputs; the second printed both rendered handoff lines.
- **UTF-8/version check:** fresh pinned-venv check exited **0**, reporting `utf8_roundtrip=pass` and `smolagents_version=1.26.0`.

## Per-task verdicts

### B7T1 — Run developmental, line, and whole-book copy edits
- **Verdict:** FAIL
- **Spec match:** Partial. The chapter covers the manager/specialist construction, explicit handoff, independent budgets/scopes, Jinja defaults, sequential invocation, and the three team shapes. It does not fully cover the required four research-backed traps or the required ch-18/ch-19 forward pointers.
- **Correctness:** The runnable code is correct for the installed version. The closing contract and book-state checks are not met.
- **Style:** Blacklist, paragraph length, heading length, orientation, and code style checks pass. The closing uses the exact third-person form the contract forbids, and `JSON` is not expanded at first use.
- **Tests:** Both code fences run cleanly in the pinned venv. No manager-model dispatch is exercised by the runnable block; the chapter explicitly describes that limitation at `ch-16.md:78` and gives the manager-driven contract in prose at `ch-16.md:139`.
- **Evidence:** `books/ai-agents-with-python/chapters/ch-16.md:13-15`, `:37-75`, `:82-125`, `:127-145`; `books/ai-agents-with-python/bible.md:2-8`; `books/ai-agents-with-python/ledger.md:43`; `books/ai-agents-with-python/outline.md:247-251`; installed `smolagents/agents.py:294-340`, `:369-387`, `:436-475`, `:868-883`.
- **Issues:**
  - [CRITICAL] `books/ai-agents-with-python/chapters/ch-16.md:143` uses `> **The move:** by the end of the reading, the reader can...`, which is the prohibited third-person closing form. The developmental contract requires the callout itself to be an imperative and forbids a third-person “by the end of the reading” line.
  - [CRITICAL] `books/ai-agents-with-python/bible.md:2-8` contains only the ch-16 block. The required terms are present, but the prior ch-01..ch-15 material is absent, so the bible append is not non-destructive and fails the no-regression check.
  - [HIGH] `books/ai-agents-with-python/research-log.md:1026-1030` defines the four beginner traps as shared-memory assumptions, cascading `max_steps`, parallel invocation assumptions, and unsafe local execution with broad imports. `ch-16.md:127-135` substitutes “putting specialists in the wrong order” and “giving every agent every tool”; it does not present the required parallel-invocation trap or the local-executor/host-privilege trap as beginner errors. Sequential behavior is discussed elsewhere at `ch-16.md:125`, but the four-error checklist is still incomplete.
  - [HIGH] `books/ai-agents-with-python/outline.md:249` and research entry-154 require forward pointers to ch-17, ch-18, and ch-19. `ch-16.md:145` names only ch-17. The required ch-18 project pointer is missing, and the research-backed ch-19 capstone pointer is also missing.
  - [HIGH] `ch-16.md:86` contains a bare prose `final_answer` match inside the Jinja-key explanation. The Jinja key itself is technically correct and required by the handoff topic, but checklist 12 states zero `\bfinal_answer\b` matches in prose without an exception. The chapter should resolve that contract conflict by moving the reserved identifier into the code/verified-behavior presentation allowed by the book rules, while preserving the required inner key.
  - [HIGH] `books/ai-agents-with-python/ledger.md:43` still marks ch-16 as `drafted`, leaves both review columns as `-`, and records word count `1638`, while the dispatch gives `1189` and the independent body-prose count is `1086` (both within the required `1070-1308` band). The row was not updated correctly for this review state.
  - [MEDIUM] `ch-16.md:13` uses `JSON-schema` without expanding JSON on first use. API does not occur in the chapter, so the API-expansion subcheck is N/A.
  - [MEDIUM] `ch-16.md:125` says “Treat this as an age-risk.” This appears to be a typo for “edge-risk” and weakens an otherwise clear version-limitation warning.
- **Suggested fix:** Rewrite the final callout as a direct imperative, restore the prior bible entries, replace the four-error list with the four research-backed traps, add explicit ch-18 and ch-19 bridges, resolve the prose keyword rule, expand JSON, correct the typo, and update the ledger row through the book workflow owner.

## Required developmental checklist

1. **Outline coverage — FAIL.** Entries 143-152 are substantially represented at `ch-16.md:7-9`, `:13-15`, `:82-125`, and `:139-141`. Entry-153 is only partial because the four errors at `:127-135` omit the required parallel and unsafe-local-executor traps documented at `research-log.md:1026-1030`. Entry-154 is partial because `:145` names only ch-17; `outline.md:249` requires ch-17/ch-18/ch-19 pointers.
2. **Voice match — PASS.** The chapter is conversational technical, uses direct instructions and second-person imperatives, contains no exclamation marks, and has no vocabulary-blacklist hit (`ch-16.md:1-149`).
3. **Vocabulary blacklist — PASS.** Fresh case-insensitive word-boundary scan found zero hits for all eight prohibited terms.
4. **Bible consistency — FAIL.** `bible.md:2-8` has the required ch-16 terms and current Jinja citation, but no prior ch-01..ch-15 blocks are present; this violates the non-destructive append requirement.
5. **Research grounding — PASS.** The chapter cites the current installed locations: `_setup_managed_agents` at `agents.py:369-387` (`ch-16.md:13`) and `__call__` at `agents.py:868-883` (`ch-16.md:86`). The dispatch/research references to `agents.py:601-623` and `:102-120` are stale locations from the earlier source layout; the chapter correctly identifies the move to current lines.
6. **Cross-platform correctness — N/A.** No activation command appears in this chapter, so there is no incorrect Windows/macOS/Linux activation reference to validate. The Python code itself is platform-neutral (`ch-16.md:18-75`, `:89-108`).
7. **Code-block correctness — PASS.** `CodeAgent.__init__` accepts the construction shown through `managed_agents` forwarded to `MultiStepAgent` (`agents.py:1527-1572`, `:294-310`); `additional_args` is a dict accepted by `.run()` (`agents.py:436-475`); child `max_steps` resolves from the child instance (`agents.py:468-475`); Jinja rendering uses the inner names in `agents.py:872-883`. Both chapter blocks exited 0 in the pinned venv. The terminator uses the required runtime construction at `ch-16.md:37-38`, with no literal `final_answer(` invocation.
8. **Beginner accessibility — PASS.** The opening paragraph is 52 words (`ch-16.md:3`), all seven H2 headings are verb-led and four or five words (`ch-16.md:5`, `:11`, `:80`, `:113`, `:121`, `:127`, `:137`), and the longest prose paragraph is 76 words (`ch-16.md:125`).
9. **Closing-imperative contract — FAIL.** `ch-16.md:143` is the exact prohibited third-person “by the end of the reading” form. The allowed ch-17 bridge at `:145` does not cure the non-imperative callout.
10. **Forward-pointer hygiene — PASS.** `ch-16.md:145` explicitly names ch-17, “Choose and Operate Model Backends,” and gives the concrete move to select a `*Model` class per role and write a backend-selection factory.
11. **No HfApiModel / ApiModel mention — PASS.** There are zero occurrences of `HfApiModel` or `ApiModel` in ch-16.
12. **final_answer discipline — FAIL.** `ch-16.md:86` has a bare prose `final_answer` match. The framework terminator in code uses the required runtime trick at `:37-38`, and `final_answer_checks` is correctly used as the permitted kwarg at `:49` and `:115`/`:143`.
13. **UTF-8 clean — PASS.** Fresh pinned-venv byte decode/encode round-trip exited 0.
14. **No regression vs prior chapters — FAIL.** The ch-16 ledger row is stale at `ledger.md:43`, and the bible state at `bible.md:2-8` is destructive rather than append-only.
15. **Acronyms — FAIL.** JSON is used as `JSON-schema` without expansion at `ch-16.md:13`. API is not used, so API expansion is N/A.
16. **Word count — PASS.** The supplied 1189 count is within 1070-1308; an independent body-prose count of 1086 is also within the band. The ledger's 1638 is stale and is separately recorded as a bookkeeping issue under checklist 14.

## Cross-cutting findings
- The source-level behavior claims are stronger than the chapter state management: the installed source confirms the current citation locations and both offline examples pass, but the bible and ledger do not reflect a safe developmental-review transition.
- The chapter correctly distinguishes `planning_interval` from delegation (`ch-16.md:119`) and correctly explains sequential managed invocation (`:125`). The missing parallel trap in the four-error subsection is therefore an organization/coverage defect, not a missing understanding of the behavior.
- The Jinja explanation is technically correct: the installed defaults use inner names, not dotted paths (`agents.py:872-883`; `code_agent.yaml:288-307`). The reserved-keyword prose rule needs a presentation adjustment rather than a framework correction.

## Out-of-scope observations (informational only)
- The runnable check constructs a manager with `managed_agents=[...]` but calls the child agents directly (`ch-16.md:69-74`); the chapter explicitly explains why at `:78` and describes the manager-driven model contract at `:139`. This is acceptable for the offline check but does not exercise model-selected delegation.
- `ch-16.md:117` mentions constrained executors and narrow authorized imports directionally, but does not repeat ch-15's installed-version caveat that managed agents cannot use remote executors in smolagents 1.26.0. This should be retained for a later safety-focused pass unless the author chooses to add it here.

## Honest assessment
The framework-facing examples are sound: both fences run, the `managed_agents` signature matches 1.26.0, the Jinja keys are verified against the current source, and the safety concepts are mostly present. This chapter is not ready to ship because the closing contract is explicitly broken, the required four-error coverage and forward pointers are incomplete, and the bible/ledger state shows regression and stale bookkeeping. The fixes are local and straightforward, but they must be applied before developmental approval.

## Self-critique
- **Did I do my job?** Yes. I read the chapter, style guide, bible, ledger, outline, research entries, installed source, task row, and coder-resource availability; ran both code fences and a fresh UTF-8/version check; and cited the current source lines.
- **What might I have missed?** No live provider calls, browser/UI checks, or manager-model delegation run were performed; this chapter's examples are intentionally offline and no UI is present. I did not inspect chapters ch-17/ch-18/ch-19 because this was a chapter-only developmental review.
- **What did I assume without evidence?** I treated the user-supplied 1189 count as authoritative while also recording an independently measured body-prose count of 1086. The bible's missing prior blocks are reported from the current file contents, not from a full historical diff because this workspace is not a git repository.
