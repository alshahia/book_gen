# Writing Plan — AI Agents with Python

Mode: LINEAR
Reasoning: The outline's dependency graph is a strictly forward chain (ch-01 → ch-02 → ... → ch-19) with two off-chain branches (ch-17 depends on ch-13 + ch-15; ch-18 depends on ch-14 + ch-15 + ch-17; ch-19 depends on ch-16 + ch-17 + ch-18). These branches do not form parallel-safe groups because every later chapter depends on something that has not been written yet. Even where multiple chapters appear to be independent of each other within the same dep layer, the linear-chain property means each chapter's prose assumes the prior chapter's installed elements are already on the page. Per the orchestrator skill ("one chapter at a time per writer invocation. Even parallel groups are dispatched one group at a time"), LINEAR is the cleanest mode. The user did not request parallel in intake.

## Execution order

1. **ch-01** — Meet Python and AI Agents (independent)
2. **ch-02** — Set Up a Cross-Platform Workspace (depends on ch-01)
3. **ch-03** — Write Your First Python Programs (depends on ch-02)
4. **ch-04** — Make Programs Decide and Repeat (depends on ch-03)
5. **ch-05** — Work with Data and Files (depends on ch-04)
6. **ch-06** — Understand Language Models (depends on ch-05)
7. **ch-07** — Call Models Safely from Python (depends on ch-06)
8. **ch-08** — How Agents Work: A Toy Agent from Scratch (depends on ch-07) — PLAIN PYTHON ONLY
9. **ch-09** — Build a First smolagents Agent (depends on ch-08) — opens with "Why Use a Framework" intro
10. **ch-10** — Give Agents Useful Tools (depends on ch-09)
11. **ch-11** — Guide Agents with Instructions and Memory (depends on ch-10)
12. **ch-12** — Create Structured Agent Workflows (depends on ch-11)
13. **ch-13** — Observe, Debug, and Evaluate Runs (depends on ch-12)
14. **ch-14** — Test Agents Without Guessing (depends on ch-13)
15. **ch-15** — Keep Agents Safe and Responsible (depends on ch-14)
16. **ch-16** — Coordinate Multiple Agents (depends on ch-15)
17. **ch-17** — Choose and Operate Model Backends (depends on ch-13, ch-15) — first off-chain branch
18. **ch-18** — Project: Research and Briefing Agent (depends on ch-14, ch-15, ch-17)
19. **ch-19** — Project: Multi-Agent Work Assistant (depends on ch-16, ch-17, ch-18) — capstone

Each chapter is dispatched to `am-coder` one at a time. The writer must finish and save the chapter before the next dispatch. Maximum three fix loops per chapter's review cycle (per `max_fix_loops=3` from the controller's standing rules).

## Per-chapter dispatch reference

Each dispatch gives the writer:
- The chapter's outline entry (Outcome, Summary, Draws on, depends_on, Contradiction framing)
- The chapter-specific research entries from `books/ai-agents-with-python/research-log.md` only (not the full log)
- `books/ai-agents-with-python/style-guide.md` (binding)
- `books/ai-agents-with-python/bible.md` (cumulative, append-only)
- Instruction to load the `book-writer` skill (prose-writing posture)

| Chapter | Outline entry | Research entries | Status |
|---|---|---|---|
| ch-01 | outline.md#ch-01 | entry-001..entry-008, entry-061 (corrective) | planned |
| ch-02 | outline.md#ch-02 | entry-009..entry-018 | planned |
| ch-03 | outline.md#ch-03 | entry-019..entry-026 | planned |
| ch-04 | outline.md#ch-04 | entry-027..entry-034 | planned |
| ch-05 | outline.md#ch-05 | entry-035..entry-043 | planned |
| ch-06 | outline.md#ch-06 | entry-044..entry-050 | planned |
| ch-07 | outline.md#ch-07 | entry-051..entry-060 | planned |
| ch-08 | outline.md#ch-08 | entry-191..entry-202 (toy agent) | planned |
| ch-09 | outline.md#ch-09 | entry-061..entry-073 (smolagents first agent) | planned |
| ch-10 | outline.md#ch-10 | entry-074..entry-084 | planned |
| ch-11 | outline.md#ch-11 | entry-085..entry-096 | planned |
| ch-12 | outline.md#ch-12 | entry-097..entry-108 | planned |
| ch-13 | outline.md#ch-13 | entry-109..entry-120 | planned |
| ch-14 | outline.md#ch-14 | entry-121..entry-132 | planned |
| ch-15 | outline.md#ch-15 | entry-133..entry-142 | planned |
| ch-16 | outline.md#ch-16 | entry-143..entry-154 | planned |
| ch-17 | outline.md#ch-17 | entry-155..entry-166 | planned |
| ch-18 | outline.md#ch-18 | entry-167..entry-178 | planned |
| ch-19 | outline.md#ch-19 | entry-179..entry-190 | planned |

## Pre-dispatch checks (writer must verify before saving)

1. All code snippets run in `E:\book_gen\.venv\Scripts\python.exe` (NOT the bare `python` command).
2. The literal `HfApiModel` string appears exactly once in the entire book (in ch-09's "Naming note" sidebar). No occurrences elsewhere.
3. The chapter's runnable check (5-20 line snippet) executes without error in the venv.
4. The chapter's outcome line from the outline is the chapter's closing imperative.
5. No `HfApiModel`, `Magic`, `Just`, `Simply`, `Obviously`, `Optimal`, `Proven`, `Studies show` (without study name), `Revolutionary`, `Game-changing`, `Powerful` without qualification.
6. Numbers and provider names are kept directional (per the 25 inline age-risks).
7. For ch-08: no smolagents, no `@tool`, no `CodeAgent`, no `final_answer` imports anywhere.
8. For ch-09: opens with the "Why Use a Framework" intro naming the four automations and three additions before the smolagents code.

## Post-dispatch checks (master must verify before next dispatch)

1. The chapter is saved at `books/ai-agents-with-python/chapters/ch-NN.md` (UTF-8, no mojibake).
2. The chapter is appended to `books/ai-agents-with-python/bible.md` (cumulative, append-only).
3. The chapter row in `books/ai-agents-with-python/ledger.md` is updated to `drafted`.
4. The chapter's review report (Phase 7) is in `share/reports/04_book-review_T-2026-08-01-001-book-ai-agents-with-python_ch-NN_dev.md` with verdict.
5. If the review requires fixes, the maximum is `max_fix_loops=3` per chapter; after 3 failed cycles, master surfaces to user.

## Phase 7 review cycles (per chapter)

Per the orchestrator skill, three separate review passes per chapter:

1. **Developmental** — does the chapter serve its outline? contradictions vs. bible? verdict against ledger exit criteria.
2. **Line edit** — prose quality + voice consistency against style-guide. Respect the revision-pass cap from intake's "definition of done".
3. **Copy edit** — single whole-book pass once **every** chapter is `approved`. Grammar, formatting, terminology consistency at book scale.

Each pass writes its findings to `share/reports/04_book-review_T-2026-08-01-001-book-ai-agents-with-python_ch-NN_<pass>.md`. Ledger is updated by master after each pass.

## State files touched during writing

- `books/ai-agents-with-python/chapters/ch-NN.md` — the prose itself (writer)
- `books/ai-agents-with-python/bible.md` — cumulative facts/voice/characters (writer appends)
- `books/ai-agents-with-python/ledger.md` — one row per chapter (writer writes status, master updates after review)
- `books/ai-agents-with-python/decisions-log.md` — append-only (any agent can append; mostly master for phase changes)
- `share/reports/04_book-review_T-2026-08-01-001-book-ai-agents-with-python_ch-NN_<pass>.md` — review outputs (reviewer)
- `share/notes/99_progress_T-2026-08-01-001-book-ai-agents-with-python.md` — master's recovery ledger (master updates)
- `share/notes/00_trace_T-2026-08-01-001-book-ai-agents-with-python.jsonl` — per-event trace (master appends)

---
Confirmation: user must confirm this plan before any writer agent is dispatched.
