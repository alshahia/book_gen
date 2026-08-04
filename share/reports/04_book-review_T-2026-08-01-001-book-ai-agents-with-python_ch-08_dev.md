# Review Report — T-2026-08-01-001-book-ai-agents-with-python / ch-08 developmental

**Date:** 2026-08-02
**Sub-agent:** review
**Loop:** initial

## Summary
- **Overall verdict:** FAIL
- **Tasks reviewed:** 1
- **Pass / Warn / Fail:** 0 / 0 / 1
- **Issue counts:** 1 CRITICAL / 2 HIGH / 1 MEDIUM / 0 LOW
- **Block release?** yes

The chapter teaches the requested plain-Python loop and both runnable examples work in the project venv, but it does not satisfy the binding closing-imperative contract or PEP 8 cleanliness. Its DIY framework-comparison claims also need inline source attribution before acceptance.

## Tests / build run
- No documented test/build command exists in `agents_manager/coder/resources/` (only the resources README), so no repository test command was available.
- Fresh in-memory extraction of both fenced Python blocks, executed with `E:\book_gen\.venv\Scripts\python.exe`: block 1 exited 0 with mocked `requests.post`; the `done` path returned `Python is a programming language.` and a never-done response raised `RuntimeError: Stopped after 2 steps.`
- Fresh execution of the offline block with the included stub exited 0; it produced the deterministic lookup/result/done trace and the never-done stub raised the `max_steps` error.
- Fresh AST compilation occurred as part of both venv executions and passed.
- No PEP 8 linter is installed in the venv (`python -m ruff --version` and `python -m pycodestyle --version` both exited 1 with `No module named ...`). A line-length scan found two violations: `ch-08.md:108` (81 characters) and `ch-08.md:159` (82 characters).
- Fresh fatal UTF-8 decode/round-trip check passed for `ch-08.md` (16,289 bytes; zero decode errors).

## Per-task verdicts

### B6T1 — Draft ch-08: How Agents Work: A Toy Agent from Scratch
- **Verdict:** FAIL
- **Spec match:** The chapter covers the four-step loop, prompt contract, parsing, dictionary dispatch, result feed, two termination paths, ch-07 comparison, DIY costs, beginner errors, offline stub, understanding-vs-adoption framing, and the ch-09 pointer. It uses no prohibited smolagents framework surface. The draft misses the required imperative form for the closing move and has two PEP 8 line-length violations.
- **Correctness:** Both code blocks execute successfully in the venv under the required mocked/offline conditions. The live-path loop checks `done` and `max_steps`; the offline loop demonstrates both paths when driven by the test stubs (`ch-08.md:91-125`, `ch-08.md:157-204`).
- **Style:** The orientation paragraph is 56 words (`ch-08.md:3`). All prose paragraphs measured at 63 words or fewer, and each H2 is seven words or fewer and action-oriented (`ch-08.md:5-228`). The chapter has 10 H2 subheadings, not the stated context count of 12. The code is not PEP 8 clean at `ch-08.md:108` and `ch-08.md:159`.
- **Tests:** Fresh venv execution passed both code paths described above. No project-level documented test command was available. Static checks found the PEP 8 line-length failures.
- **Evidence:** `ch-08.md:3`, `ch-08.md:5-44`, `ch-08.md:46-130`, `ch-08.md:136-236`; `style-guide.md:42-59`, `style-guide.md:89-112`.
- **Issues:**
  - [CRITICAL] `ch-08.md:234` presents the `The move` callout as a third-person outcome statement beginning “by the end of the reading” rather than as an imperative action. The binding contract requires the callout to deliver the closing imperative, with no third-person closing line. The permitted thin bridge at `ch-08.md:236` does not change the callout's non-imperative form.
  - [HIGH] `ch-08.md:108` contains an 81-character line and `ch-08.md:159` contains an 82-character line. The style guide requires PEP 8-clean runnable blocks and states that a reviewer will fail a chapter for code-block violations (`style-guide.md:44-49`).
  - [HIGH] The DIY framework-comparison claims at `ch-08.md:210-214` (“no parallel tool calls,” “no schema-aware retries,” and what a framework will automate) have no inline named source. Named citations exist for the loop/reference and control-flow claims (`ch-08.md:9`, `ch-08.md:30`, `ch-08.md:38`, `ch-08.md:140`) and for the forward pointer (`ch-08.md:236`), but the comparison paragraph itself needs the relevant named API/framework sources.
- **Suggested fix:** Rewrite the move callout as a same-day imperative, wrap the two overlong code lines, and add inline named citations to the DIY-cost/framework-comparison claims.

## Required review checklist

1. **Outline coverage — PASS.** Entries 191–202 are all represented: loop anatomy and observe–decide–act–observe (`ch-08.md:7-11`), prompt anatomy (`ch-08.md:15-24`), action parsing (`ch-08.md:28-32`), dispatch (`ch-08.md:34-38`), result feed (`ch-08.md:132-134`), termination (`ch-08.md:136-140`), ch-07 comparison (`ch-08.md:40-44`), two DIY costs (`ch-08.md:208-214`), four beginner errors (`ch-08.md:216-226`), offline stub (`ch-08.md:142-206`), ch-09 pointer (`ch-08.md:236`), and understanding-vs-adoption framing (`ch-08.md:228-232`).
2. **Voice match — PASS.** The prose is conversational and technical, addresses the reader directly, uses natural contractions where appropriate, and contains no exclamation marks (`ch-08.md:3-44`, `ch-08.md:208-236`; `style-guide.md:157-180`).
3. **Vocabulary blacklist — PASS.** A case-insensitive word-boundary scan found zero hits for all listed terms across the chapter, including the HTML comment (`ch-08.md:1-244`; `style-guide.md:182-193`).
4. **Bible consistency — PASS.** The required dated append exists at `bible.md:113-122` and contains Agent loop, Observe–decide–act–observe, Action parsing, Tool dispatch, Result feed, Termination signal, `max_steps` guard, and Stub model. It is an append after the ch-01–ch-07 blocks and does not rewrite them (`bible.md:34-113`).
5. **Research grounding — FAIL.** The chapter names ReAct/Yao and Anthropic's *Building effective agents* (`ch-08.md:9`), Python stdlib sources (`ch-08.md:30`, `ch-08.md:38`, `ch-08.md:140`), and smolagents documentation (`ch-08.md:236`), but the framework-comparison claims in the DIY-cost section are uncited in place (`ch-08.md:210-214`).
6. **Plain-Python rule — PASS.** The chapter body has zero occurrences of `from smolagents`, `import smolagents`, `@tool`, `CodeAgent`, `ToolCallingAgent`, `MultiStepAgent`, `InferenceClientModel`, `HfApiModel`, `ApiModel`, `FinalAnswerTool`, and `final_answer`. The imports are stdlib plus `requests` and `python-dotenv`, with the ch-07-style helper (`ch-08.md:46-80`; `ch-08.md:61-66`).
7. **Code-block correctness — FAIL.** Both blocks have main guards (`ch-08.md:127-129`, `ch-08.md:201-204`) and pass the fresh venv runtime checks, including deterministic offline behavior (`ch-08.md:148-206`). However, the two overlong lines at `ch-08.md:108` and `ch-08.md:159` violate the required PEP 8-clean condition.
8. **Beginner accessibility — PASS with a structural warning.** The opening orientation is 56 words (`ch-08.md:3`), all measured prose paragraphs are ≤80 words, and all 10 actual H2 headings are ≤7 words and action-oriented (`ch-08.md:5-228`). The supplied context says 12 H2 headings, but the file contains 10; this is recorded as a MEDIUM cross-cutting finding rather than failing the paragraph/subheading rules themselves.
9. **Closing-imperative contract — FAIL.** The `The move` callout is not an imperative and contains the prohibited third-person “by the end of the reading” formulation (`ch-08.md:234`). The next bridge is thin and names ch-09, but the callout itself must be rewritten to the required reader action before the HTML comment (`ch-08.md:236-244`).
10. **Forward-pointer hygiene — PASS.** The bridge names ch-09 explicitly and names the “Why Use a Framework” intro that ch-09 opens with (`ch-08.md:236`; `outline.md:741-751`).
11. **30-line honesty — PASS.** The prose says “roughly thirty-line move,” not a strict 30-line implementation (`ch-08.md:44`). The actual `run_agent` implementation spans `ch-08.md:91-125`, so the hedge is honest.
12. **Termination semantics — PASS.** The live toy returns on `action == "done"` and raises at the `max_steps` guard (`ch-08.md:98-113`). The offline block returns on `done` and raises after the bounded `for` loop (`ch-08.md:163-183`); both paths passed fresh runtime checks.
13. **No HfApiModel / ApiModel mention — PASS.** A whole-file word-boundary scan found zero `HfApiModel` and `ApiModel` occurrences in ch-08 (`ch-08.md:1-244`).
14. **UTF-8 clean — PASS.** A fresh fatal UTF-8 decode/round-trip check passed with zero errors for the chapter file.
15. **No-regression vs prior chapters — PASS.** The ch-08 ledger row remains coherent as a drafted chapter with word count 1739, dependency ch-07, and the plain-Python/offline-stub note (`ledger.md:49-73`, `ledger.md:145-157`). The bible append is non-destructive and follows the established append-only structure (`bible.md:3`, `bible.md:113-122`).

## Cross-cutting findings
- [MEDIUM] The supplied chapter context says “12 H2 subheadings,” but `ch-08.md` contains 10 H2 headings (`ch-08.md:5`, `:13`, `:26`, `:34`, `:40`, `:136`, `:142`, `:208`, `:216`, `:228`). Either the context metric is stale or two planned navigational sections are absent. The existing headings satisfy the ≤7-word/action-fragment constraint.
- The chapter's HTML self-critique comment claims all review points are satisfied, but it is not evidence and should not substitute for the fresh checks above (`ch-08.md:238-244`).

## Out-of-scope observations (informational only)
- The task metadata still describes older 18-chapter phase counts and an earlier ch-08 smolagents dispatch in its historical log (`tasks/T-2026-08-01-001-book-ai-agents-with-python.md:26-31`, `:113-117`). This review did not edit task metadata because it is outside the requested chapter-review boundary.
- No existing ch-09 chapter file is present in the current workspace snapshot, so the forward pointer was checked against the outline rather than a drafted next chapter.

## Honest assessment
The chapter's core teaching move is sound: the plain-Python loop, deterministic stub, `done` termination, and `max_steps` safety path all work under fresh venv verification. It is not ready to ship because the closing action violates the explicit contract, two runnable lines are not PEP 8 clean, and the DIY framework comparison is not fully cited inline. These are small, targeted fixes, not a plan failure.

## Self-critique
- **Did I do my job?** Yes. I read the chapter, style guide, bible, outline, research entries, ledger, task metadata, and coder-resource directory; then ran fresh targeted runtime and encoding checks.
- **What might I have missed?** No repository-wide book line-edit or copy-edit pass was run; no live provider call was attempted because the chapter's live path requires credentials and the requested verification uses mocked requests.
- **What did I assume without evidence?** The 12-H2 figure was treated as a stated target because it was supplied in the dispatch; the PEP 8 finding uses the canonical 79-character line-length rule and a direct static scan because no formatter/linter is installed.
- **Boundary note:** No source, book-state, task, memory, trace, warning-register, or other share file was written; only the requested review report artifact was written.
