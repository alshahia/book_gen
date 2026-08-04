# Book Developmental Review — T-2026-08-01-001-book-ai-agents-with-python / ch-19

**Date:** 2026-08-03
**Sub-agent:** am-review
**Loop:** initial
**Scope:** developmental review only; no source or book files edited.

## Summary
- **Overall verdict:** FAIL
- **Tasks reviewed:** 1
- **Pass / Warn / Fail:** 0 / 0 / 1
- **Issue counts:** 5 CRITICAL, 5 HIGH, 3 MEDIUM, 0 LOW
- **Block release?** yes

The chapter has a strong explanatory spine and most requested topics are present, but the capstone shown is not the claimed manager-routed runnable project. The `run()` helper bypasses the manager, the researcher has no source tool, the revision loop can return an unreviewed failing draft, and the live path is deliberately unimplemented.

## Tests / build run
- Fresh in-memory extraction of all 10 fenced Python blocks followed by `ast.parse` with Python — **10/10 PASS**.
- Fresh static chapter audit — blacklist 0, `HfApiModel` 0, bare `final_answer` 0, visible exclamation marks 0, H2 headings over 7 words 0, UTF-8 round-trip clean.
- No temporary project or pytest run was performed: the dispatch hard boundary permits writing only the review artifact, so creating extracted test files would violate the boundary. The writer's reported smoke 11/11 and gold 2/2 results are therefore not independently reproduced.
- Installed-source verification read from `E:\book_gen\.venv\Lib\site-packages\smolagents\agents.py`: constructor accepts independent `managed_agents`, `step_callbacks`, `final_answer_checks`, and `logger` (`agents.py:294-351`); managed-agent calls wrap `run()` and use inner `name`, `task`, and `final_answer` variables (`agents.py:868-890`).

## Required review checklist

| # | Check | Verdict | Evidence / finding |
|---:|---|---|---|
| 1 | Outline coverage: entries 179–190 and all required topics | **FAIL** | The chapter covers the manager shape, model tiers, Jinja correction, loop, layout, gates, logs, tests, directional cost, four errors, and closing reflection (`ch-19.md:7-12`, `:19-31`, `:105-107`, `:204-226`, `:238-286`, `:440-720`). However, the required runnable capstone is not implemented as described: researcher `tools=[]` (`ch-19.md:48-63`), `agent.py` is absent from the required package tree (`ch-19.md:208-217`), and live wiring raises `NotImplementedError` (`ch-19.md:661-694`). Next-step pointers are only implicit in the reflection (`ch-19.md:714-720`). |
| 2 | Voice match | **WARN** | Conversational, second-person prose and contractions are consistent (`ch-19.md:3`, `:714-720`); no visible exclamation marks were found. Four prose paragraphs exceed the ≤80-word accessibility rule, including 94 words at `ch-19.md:7-9`, 86 at `:17`, 81 at `:29`, and 91 at `:31`. |
| 3 | Vocabulary blacklist | **PASS** | Fresh word-boundary scan of visible chapter content found zero hits for all listed blacklist terms. |
| 4 | Bible consistency / untouched | **PASS** | `bible.md` was read for comparison and no write was made. Its ch-16 rules support the chapter's intended pattern (`bible.md:181-189`). |
| 5 | Research grounding with installed-source citations | **FAIL** | Manager registration and Jinja handoff cite installed source (`ch-19.md:15`, `:29`). The evaluator loop is attributed to earlier chapters but has no inline installed-source citation for the `additional_args`/reset behavior (`ch-19.md:105-107`). More importantly, the prose claims source collection while the shown researcher has no source tool (`ch-19.md:48-63`). |
| 6 | Project structure, guards, tests, per-agent logs | **FAIL** | CLI and module guards are present (`ch-19.md:395-424`, `:426-436`), and the three test files plus four-role log design are shown (`ch-19.md:219-226`, `:284-350`). The required `src/work_assistant/agent.py` module is missing from the tree, the live test is a placeholder (`ch-19.md:686-694`), and the manager logger is constructed but the manager is not run by the public helper (`ch-19.md:141-156`, `:158-186`). |
| 7 | Code-block correctness | **FAIL** | AST parsing is clean for all 10 Python blocks. Positive checks: manager `tools=[]` and three managed agents (`ch-19.md:142-156`), independent specialist models/budgets/checks (`:48-100`), and bounded loop constant (`:124-125`). Failures: reviewer-to-writer calls omit the required `reset=False` pattern (`:160-183`); the manager's own `final_answer_checks` is absent (`:142-156`); the researcher declares `tools=[]` despite the source-gathering contract (`:48-63`); and the last failed review still triggers a revision which is returned without a subsequent review (`:165-184`). |
| 8 | Beginner accessibility | **FAIL** | Opening orientation is within the 30–60-word target by the chapter's stated count (`ch-19.md:3`). H2s are verb-led and ≤7 words (`:5`, `:13`, `:19`, `:27`, `:105`, `:204`, `:238`, `:284`, `:352`, `:440`, `:698`, `:704`, `:714`). Four paragraphs exceed 80 words as cited under check 2, violating the explicit paragraph cap. |
| 9 | Closing-imperative contract | **PASS** | The `> **The move:**` block is the final visible substantive prose before the HTML comment (`ch-19.md:720-722`); the reflection precedes it and is second-person (`:714-718`), with no “What’s next” bridge. |
| 10 | `HfApiModel` rule | **PASS** | Fresh word-boundary scan found zero body occurrences (`ch-19.md:1-721`). |
| 11 | `final_answer` prose discipline | **PASS** | Fresh word-boundary scan found zero bare `final_answer` occurrences in the visible body; `final_answer_checks` occurrences are allowed. Runtime string construction is split as documented (`ch-19.md:196-199`, `:490-495`). |
| 12 | UTF-8 clean | **PASS** | Fresh UTF-8 decode/round-trip check completed with zero errors. |
| 13 | No-regression ledger/bible | **FAIL** | `bible.md` was not changed in this review, but the current ledger row remains `drafted` with Dev review `-` rather than a developmental-review state (`ledger.md:284`). A prior Edit-vs-Write operation and preservation of ch-01–ch-18 rows cannot be proven from the current file alone. |
| 14 | Acronyms expanded on first use | **FAIL** | `JSONL` appears without expansion in the opening (`ch-19.md:3`); `CLI` appears before any expansion (`:357`, `:438`); `API` appears in the opening/model discussion before the later expansion (`:23`, `:712`); and `JSON` has no standalone first-use expansion in the chapter. |
| 15 | Test executability | **FAIL** | AST syntax passes, and the gold snippets include a passing-first-review and a revision-triggered case (`ch-19.md:607-657`). Independent pytest execution was blocked by the write-only boundary. The live case explicitly raises `NotImplementedError` when a key is present (`ch-19.md:678-694`), so the claimed runnable capstone is incomplete. |
| 16 | No test-artifact leakage | **PASS** | Fresh file search found no `_ch19_old.txt`, `_validate_ch19/`, `.bak`, or matching old/backup artifacts under `books/ai-agents-with-python/`. |

## Per-task verdicts

### CH-19 — Developmental review of capstone chapter
- **Verdict:** FAIL
- **Spec match:** The prose describes the intended four-agent capstone, but the executable design does not route the public request through the manager and cannot perform real research or live execution.
- **Correctness:** The evaluator loop iterates on low scores, but its exhaustion path returns a draft that has not passed review. The shown researcher has no web/source tool, and the manager instance is bypassed.
- **Style:** The chapter's structure, closing form, vocabulary discipline, and syntax are mostly compliant. Paragraph-length and acronym failures remain.
- **Tests:** All extracted Python blocks parse. The reported smoke/gold counts were not independently run because the hard boundary forbids creating the temporary project; the live test is intentionally unimplemented.
- **Evidence:** `ch-19.md:48-63`, `:124-186`, `:208-226`, `:661-694`; installed `smolagents/agents.py:294-351`, `:868-890`; `ledger.md:284`.
- **Issues:**
  - [CRITICAL] `ch-19.md:158-186` returns the `run()` helper that directly invokes `researcher`, `writer`, and `reviewer`; the `manager` returned by `build_team()` is never called. This does not implement manager-routes-to-specialists behavior.
  - [CRITICAL] `ch-19.md:48-63` constructs the researcher with `tools=[]`, despite the acceptance contract requiring real source collection and source-per-claim verification (`ch-19.md:7-9`). The chapter's live path cannot satisfy that contract.
  - [CRITICAL] `ch-19.md:165-184` revises after the final permitted failed review and then returns that unreviewed revision. The function can finish below the threshold, contrary to the stated “until the score passes” contract.
  - [CRITICAL] `ch-19.md:686-694` raises `NotImplementedError` for keyed live execution, so the advertised runnable capstone is not runnable in its real mode.
  - [CRITICAL] `ch-19.md:208-217` omits the required `src/work_assistant/agent.py` module from the project structure, while the checklist requires it explicitly.
  - [HIGH] `ch-19.md:160-183` uses `additional_args` but does not use `reset=False` for the writer's revision conversation, despite the required ch-11 pattern and the chapter's own claim at `:107`.
  - [HIGH] `ch-19.md:142-156` gives the manager no independent `final_answer_checks`, although the requested per-agent configuration requires independently set checks across the team.
  - [HIGH] `ch-19.md:461-463` declares `smolagents>=1.26.0`, not the pinned `smolagents==1.26.0` target stated by the dispatch.
  - [HIGH] `ch-19.md:7-9`, `:17`, `:29`, and `:31` exceed the style guide's 80-word paragraph limit.
  - [HIGH] `ch-19.md:3`, `:23`, `:357`, `:438`, and `:712` use JSONL, API, and CLI before expansion; JSON is not expanded in the chapter.
  - [MEDIUM] `ch-19.md:700-702` says a minimum full run makes four round trips, but the shown `run()` helper makes no manager model call; this cost statement describes an intended architecture rather than the executable path.
  - [MEDIUM] `ch-19.md:714-720` provides a natural closing reflection but only implicit next-step pointers; entry-190's requested pointers should name concrete follow-on directions without adding a post-imperative bridge.
  - [MEDIUM] `ledger.md:284` remains `drafted` with no developmental-review result; the reviewer cannot confirm the required ledger update provenance, and may not edit it under the dispatch boundary.
- **Suggested fix:** Refactor one public `run()` path so the manager performs delegation, give the researcher its source tool(s), make revision attempts stop before an unreviewed return or raise on exhaustion, implement real backend wiring, add the missing module, pin dependencies, then re-run smoke/gold/live and perform a line-length/acronym pass.

## Cross-cutting findings
- The chapter conflates an illustrative direct-call orchestration helper with the advertised smolagents manager workflow. That is the central correctness defect: the manager's managed-agent tool schema is built (`smolagents/agents.py:369-387`) but never exercised by `run()`.
- The evaluator-optimizer loop does actually loop for low scores: the reviewer call is followed by a writer call and another reviewer iteration (`ch-19.md:165-183`), and the gold test demonstrates one revision (`:635-657`). It is nevertheless unsafe at exhaustion because the final revision is not scored.
- The reviewer-to-writer handoff does use `additional_args`, not `chat_messages`, which is directionally correct (`ch-19.md:176-182`), but it does not demonstrate or preserve the required `reset=False` multi-turn pattern.
- The manager's JSONL file is created, but because `manager.run()` is never called, it does not constitute a manager trace of routing (`ch-19.md:141-156`, `:158-186`).
- The chapter's source citations are useful for constructor and template facts, but source-gathering and evaluator behavior need citations that support the exact runnable implementation, not only the HTML self-critique.

## Out-of-scope observations (informational only)
- The prose says the manager sees specialists “like tools” and correctly mirrors the installed source's managed-agent setup (`ch-19.md:15`; `agents.py:369-387`).
- `PerAgentJsonlLogger` uses a timestamped filename per role and flushes each record (`ch-19.md:298-347`), but it does not close the handles on normal CLI completion; this is outside the requested developmental checklist and is not counted as a release blocker.
- The chapter's `pyproject.toml` lists `hatchling` as a build requirement but does not show a reader install command for it; this is a reproducibility concern outside the primary findings.

## Honest assessment
The writer correctly explains the intended manager-plus-three-specialists shape and the Jinja inner-key contract, and the low-score test proves that the reviewer/evaluator path can loop once. The implementation does not correctly implement that pattern: the public helper bypasses the manager, the researcher cannot retrieve sources, and the loop can return an unreviewed failing revision. The closing reflection is natural and remains second-person, but the chapter is not ready to ship until the executable capstone and its tests match the outcome.

## Self-critique
- **Did I do my job?** Partial: I completed fresh static checks and inspected the installed runtime source, but the write-only boundary prevented a fresh pytest run from an extracted temporary project.
- **What might I have missed?** The exact coder's test harness and any external files not embedded in `ch-19.md`; no coder summary matching this task id was present under `share/notes` during discovery.
- **What did I assume without evidence?** I treated the required `agent.py` listing as binding because it is explicit in the dispatch checklist, even though the chapter's own tree and prose describe seven package modules. I did not assume the reported smoke/gold counts were true without rerunning them.

## Closing outcome verification

Required outcome:

> by the end of the reading, the reader has a runnable `src/work_assistant/` capstone project with a manager `CodeAgent` (no direct tools, three `managed_agents`) that routes a free-text request through a researcher (sources), a writer (prose), and a reviewer (numeric score + revision request), each with its own `model`, `tools`, `max_steps`, `final_answer_checks`, and JSONL logger; the reviewer runs an evaluator-optimizer loop with the writer until the score passes.

The closing callout at `ch-19.md:720` describes this target, but it is not verified as implemented: it says the manager routes, while `run()` directly calls the three specialists (`ch-19.md:158-186`), and it says the loop continues until the score reaches the bar, while the exhaustion path returns an unreviewed draft (`:165-184`).
