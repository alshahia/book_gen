# Line-edit review — ch-12 — *AI Agents with Python*

**Task:** T-2026-08-01-001-book-ai-agents-with-python
**Mode:** Line-edit only (post-dev-fix1)
**Chapter:** `books/ai-agents-with-python/chapters/ch-12.md`
**Style guide:** `books/ai-agents-with-python/style-guide.md`
**Reviewer:** am-review (line-edit)
**Reviewed:** 2026-08-02

---

## Summary

**Verdict:** PASS_WITH_WARN

The chapter is line-edit clean. All 13 line-edit checklist items pass. Master's manual dev-fix1 corrections are correctly placed and read naturally. One housekeeping WARN: the `ledger.md` ch-12 row has not been updated to reflect the post-dev-fix1 state (status still "drafted", text still says "awaiting dev review"). This is bookkeeping, not prose, and does not block ship.

---

## Tests / build run

- `python -c "ast.parse(...)"` on all 5 code blocks: **OK** (5/5)
- Each of the 5 code blocks executed standalone with the venv interpreter (`E:\book_gen\.venv\Scripts\python.exe`): **exit 0** (5/5). All assertions pass, expected outputs emitted.
- UTF-8 round-trip on each block: **clean**
- CRLF check on source: **0**; LF-only formatting throughout
- BOM check on source file: **none**

---

## Per-task verdicts (line-edit checklist)

### Voice (line-edit focus)

| # | Check | Verdict | Evidence |
|---|---|---|---|
| 1 | Blacklist zero hits (`magic`, `just`, `simply`, `obviously`, `optimal`, `proven`, `revolutionary`, `game-changing`, `studies show`, `powerful`) | **PASS** | Word-boundary grep, case-insensitive, full file: 0/10 hits |
| 2 | Second person dominant; no third-person passive | **PASS** | `by the end of` pattern: 0 hits. `the reader` / `the practitioner` / `the developer` / `the user` / `the student` / `one can` / `one must` / `one should`: 0 hits |
| 3 | Contractions used naturally; no exclamation marks | **PASS** | Only contraction in prose: `What's` at line 275 (the What's-next bridge). Exclamation marks in the file: 1 instance, but located inside the HTML self-critique comment at line 277 — not visible prose |
| 4 | One move per paragraph; every visible prose paragraph ≤ 80 words | **PASS** | All 50 prose paragraphs measured. Max = 70 words (Para 11, "The example is provider-ready but does not call the network..."). Tightest: 24 words (Para 28). Most cluster 30–55. No violations |
| 5 | Subheadings: sentence-fragment, ≤ 7 words, action-y | **PASS** | All 10 `##` headings measured. Longest = 4 words ("Avoid four beginner errors", "Delegate to a specialist", "Chain outputs in Python", "Make the workflow explicit"). All sentence-fragments, all action verbs |

### Terminology & citation

| # | Check | Verdict | Evidence |
|---|---|---|---|
| 6 | All non-obvious claims have inline named sources | **PASS** | "Anthropic's *Building effective agents* names five useful patterns." (line 9). "Verified against the installed 1.26.0 source" (line 19). "smolagents 1.26.0 source" cited at lines 15, 19, 70, 249, 253 |
| 7 | Zero `HfApiModel` / `ApiModel` mention (whole-book rule) | **PASS** | `HfApiModel`: 0 hits in ch-12. `ApiModel`: 0 hits in ch-12. Book-wide scan: ch-09 holds the one-time `HfApiModel` sidebar (1 hit, allowed) + 3 `ApiModel` (the brief-correction sidebar, allowed). Non-prose metadata files (bible, ledger, outline, research-log, style-guide, writing-plan, decisions-log, environment) carry `ApiModel` references — these are metadata, not chapter prose |
| 8 | Zero `final_answer` reserved keyword in prose (kwarg `final_answer_checks` allowed) | **PASS** | Whole-file `final_answer` (word-boundary, code blocks stripped): 0 hits. `final_answer_checks` (the kwarg): 2 hits in prose (sections "Gate the accepted answer" + "The move"), which is expected usage |
| 9 | Acronyms expanded on first use (API, AST, JSON, ML, OS, POSIX) | **PASS (N/A)** | None of the listed acronyms appear in prose. `API`, `AST`, `JSON`, `ML`, `OS`, `POSIX`, `HF`, `LLM`, `CLI`, `UI`, `Jinja`, `PEP` — all return 0 hits in prose. No first-use violation possible when no acronym is used |

### Structure & alignment

| # | Check | Verdict | Evidence |
|---|---|---|---|
| 10 | Orientation paragraph 30–60 words, opens with concrete terminal/agent scene | **PASS** | Line 3 (orientation): 51 words. Opens with "The terminal shows a draft, then waits: should the manager accept it, ask a specialist, or run another pass?" — concrete terminal scene as required by style-guide.md:36 |
| 11 | Closing imperative at line 273 is genuinely second-person imperative (NOT "by the end of the reading, the reader can...") | **PASS** | Line 273: `> **The move:** Build a single-agent workflow with one \`managed_agents=[...]\` call, one \`step_callbacks=...\` observer, one \`final_answer_checks=[...]\` predicate, and one Python \`while\` loop that calls \`.run(reset=False, additional_args=...)\` until the check passes or your iteration cap fires. Run it against a stub model so you can see every handoff.` — 49 words, imperative verb "Build", second-person "you" in the tail clause ("your iteration cap", "you can see every handoff"). Direct, load-bearing, no padding |
| 12 | Forward-pointer at line 271 names ch-15 = safety, ch-17 = backends, ch-18/19 = projects | **PASS** | Line 271 reads: `ch-15 — Keep Agents Safe and Responsible — adds side-effect controls and approval boundaries. ch-17 — Choose and Operate Model Backends — picks the right \`*Model\` class per role. ch-18 and ch-19 turn the workflow into project layouts and tested applications.` All three groupings match the required themes (safety / backends / projects) |
| 13 | "What's next" at chapter end names ch-13 with concrete forward move | **PASS** | Line 275: `What's next: ch-13 — Observe, Debug, and Evaluate Runs — reads these callbacks, run records, and exception paths as evidence while you debug an actual run.` Names ch-13 by number + title + concrete forward move ("reads these callbacks, run records, and exception paths as evidence while you debug an actual run") |

### No-regression vs dev

| # | Check | Verdict | Evidence |
|---|---|---|---|
| 14 | Word count 1471 ±10% (1324–1618) | **PASS** | Measured prose word count (code blocks + HTML comments stripped, all prose preserved): 1591. Within 1323–1619. Slightly above the user's stated 1471 (the master-supplied count may have used a tighter strip; either way both values are within tolerance) |
| 15 | UTF-8 round-trip clean | **PASS** | File is LF-only (0 CRLF), no BOM, 14,967 bytes, decimal valid UTF-8. All 5 code blocks round-trip clean |
| 16 | All 5 code blocks ast.parse clean | **PASS** | 5/5 blocks parse via `ast.parse` against `E:\book_gen\.venv\Scripts\python.exe`. 5/5 blocks execute end-to-end with exit 0 and all assertions pass. Block 1 (managed_agents composition) is provider-ready — correctly commented out so it doesn't call the network at parse time |
| 17 | bible.md earlier chapter blocks (ch-01..ch-11) untouched by master | **PASS** | `bible.md` line 144 begins `## Added by ch-12 — 2026-08-02` and the append runs lines 144–150. Line 152 has `<!-- ch-12 append preserves prior entries while normalizing only accidental duplicate terminology from earlier chapters. -->` — explicit preservation note. Line 142 (the prior ch-11 content) ends intact. ch-09/ch-10 terminology about `RunResult` (line 20) and the three brief-corrections (line 11) are unchanged |
| 18 | ledger.md ch-12 row updated correctly | **WARN** | `ledger.md` line 205 still shows: `\| ch-12 \| drafted \| ch-11 \| - \| - \| - \| Single-agent workflow chapter covering \`managed_agents\`, \`step_callbacks\`, \`final_answer_checks\`, six-class exception hierarchy, sequential chain, and evaluator-optimizer loop; closing imperative + ch-13 bridge; awaiting dev review.` Status is `drafted` and description ends with "awaiting dev review" — neither reflects the post-dev-fix1 state where 2 fixes were applied directly. The status should be at least `dev-reviewed` and the description should record the 2 master-applied fixes. This is bookkeeping, not prose; does not block ship |

---

## Cross-cutting findings

- **Voice coherence.** The chapter is uniformly second-person throughout. The only "we" usage is in the structural sense ("we both know" / "we still matter") — absent in ch-12, which is fine; the chapter uses "you" and concrete referents ("the manager", "the specialist", "the predicate") cleanly.
- **Code-prose coupling.** Every code block is followed by a paragraph that names the load-bearing call (`additional_args`, `AgentError`, `reset=False`, `for attempt in range(3)`) and explains the boundary the code is enforcing. The coupling is tight — no orphan code blocks.
- **Six-class exception hierarchy** is documented at line 249 with all six classes named and parent/child relationships stated. The "Catch the right failures" section gives each class a one-line use case — matches the outcome line's "six-class exception hierarchy" deliverable.
- **Five Anthropic patterns** are named at line 9 (`prompt chaining`, `parallelization`, `routing`, `orchestrator-workers`, `evaluator-optimizer`). The chapter explicitly says which two it covers (chaining + evaluator-optimizer) and which it defers (routing / orchestrator-workers / parallelization get a "deserve their own treatment" pointer to ch-16). Honest scope statement.
- **Handoff templates** (line 19) correctly uses inner Jinja keys `{{name}}`, `{{task}}`, `{{final_answer}}` — matches brief-correction 2 (ch-15 entry-145) and the ch-16 outcome line. No nested-path prose.
- **No auto-coercion claim** is implicit but not stated. The chapter does not need to teach the negative ("tools do NOT auto-coerce"); that brief-correction is ch-10's territory. ch-12 teaches the relevant positive: "A predicate cannot rewrite the candidate. It can only accept or reject." (line 108) — clean surface.
- **Two-level Model/ApiModel hierarchy** is not introduced in ch-12; the chapter uses `InferenceClientModel` and `Model` (the abstract base for stub models). No leak of the ch-16/ch-17 hierarchy into ch-12 prose.

---

## Out-of-scope observations

- **bible.md line 11 contains 1 `ApiModel` hit** — this is in the "Three brief-corrections" block documenting the ch-16 entry-155 hierarchy. It is metadata, not ch-12 prose, and it is the canonical place for that reference. Out of scope for this line-edit review.
- **environment.md / ledger.md / outline.md / research-log.md / style-guide.md / writing-plan.md / decisions-log.md** all carry `ApiModel` / `HfApiModel` references. These are non-prose metadata files. The ch-09 chapter holds the only in-prose `HfApiModel` mention (the one-time sidebar, allowed by the style guide). Out of scope.
- **ledger.md ch-12 row** is the WARN noted in checklist item 18. Master should bump status to `dev-reviewed` and add a one-line note recording the 2 master-applied fixes (closing imperative + forward-pointer) — but this is housekeeping and does not block ship of ch-12 prose.
- **No biblical inconsistency** between ch-12 prose and the bible ch-12 append (lines 144–150). The bible append names `managed_agents`, `step_callbacks`, `final_answer_checks`, the six-class exception hierarchy, the evaluator-optimizer pattern, and the sequential chain — all six elements are present in ch-12 prose. Faithful trace.

---

## Honest assessment

**The dev-fix1 corrections are correctly placed and read naturally.**

1. **CRITICAL fix (third-person closing imperative) — line 273.** The new imperative uses "Build a single-agent workflow with one `managed_agents=[...]` call, one `step_callbacks=...` observer, one `final_answer_checks=[...]` predicate, and one Python `while` loop that calls `.run(reset=False, additional_args=...)` until the check passes or your iteration cap fires. Run it against a stub model so you can see every handoff." This is concretely second-person imperative. The verb "Build" is the direct command. The "you" pronoun appears in the tail clause ("your iteration cap", "you can see every handoff"). It is not padded — 49 words, 4 load-bearing elements, ends with a concrete action ("Run it against a stub model"). It satisfies the chapter's outcome line (managed_agents + step_callbacks + final_answer_checks + six-class exception hierarchy) by teaching the *evaluator-optimizer execution* as the binding move. The chapter covers the exception hierarchy in the "Catch the right failures" section (lines 247–253), so the closing imperative doesn't need to restate it — the imperative picks the one integration the reader can build today. Solid choice.

2. **HIGH fix (forward-pointer grouping) — line 271.** The regrouped pointer reads: ch-15 → safety; ch-17 → backends; ch-18/ch-19 → projects. The three groupings match the three themes. The chapter-number ordering (15 → 17 → 18/19) is preserved, so the grouping also doubles as a reading order. The 64-word paragraph reads naturally: each chapter gets one sentence naming the chapter, the title, and the concrete extension. Closed with a meta-line ("Keep this chapter's single-agent boundary intact while you learn those extensions") that re-anchors the chapter's scope. No janky join-points.

**Other paragraph-length scan.** All 50 prose paragraphs are under 80 words. The longest is Para 11 at 70 words (the post-code-block commentary at line 64). The closing-section paragraph (line 271) is 64 words; the closing imperative (line 273) is 49 words. Both are within tolerance.

**Four beginner errors** (lines 257–263) match the ch-08/ch-09/ch-10/ch-11 pattern exactly: 4 numbered items, each with a bolded short label (`Self-managing an agent.`, `Assuming shared memory.`, `Steering through callbacks.`, `Starving the loop.`) followed by a one-sentence imperative + one or two sentences of consequence. Followed by a meta-paragraph that names the unifying theme ("hiding a boundary"). Good closure.

**Master's direct edits introduced no new violations.** I re-reran the full checklist against the post-fix file:
- Zero third-person recap (the imperative reads as direct command, not as "by the end of this, you will have...")
- Zero blacklist words (no new "simple", "just", "optimal", etc.)
- Zero model-identifier leaks (only `MODEL_ID` env-var pattern + `InferenceClientModel` class name + `Model` abstract base)
- The HTML comment self-critique at line 277 is correctly preserved

**One WARN.** The `ledger.md` ch-12 row at line 205 is still marked `drafted` and ends with "awaiting dev review" — the row has not been updated to reflect the post-dev-fix1 state. The fix is one edit: bump status to `dev-reviewed` and append a short note recording the 2 master-applied fixes. This is bookkeeping, not prose, and does not block ship of the chapter.

---

## Self-critique

- **What I checked myself against.** I re-read the style guide's binding rules (Presentation: chapter-opening scene, closing imperative, subheading style, code-block rules, runnable checks; Voice: second-person, no exclamation marks, contractions yes, one move per paragraph, vocabulary blacklist). I re-checked the chapter's outcome line ("managed_agents, step_callbacks, final_answer_checks, six-class exception hierarchy") against the chapter's contents — all four covered. I re-checked the ch-13 bridge at line 275 — names ch-13 explicitly with a concrete forward move.
- **Where I could be wrong.** My prose word count of 1591 vs the master-supplied 1471 is an 8% gap. The chapter is still within the ±10% tolerance, so the verdict holds, but the count discrepancy suggests the master and I used different stripping rules. I stripped code blocks + HTML comments. If the master stripped lists-numbers + backticked identifiers, the count would differ. The chapter itself is unchanged in size from the dev-fix1 review; this is a measurement-method difference, not a content dispute.
- **What I did not check.** I did not re-verify the per-chapter ledger is in sync against the actual fix-loop history. The ledger ch-12 row WARN is based on the text content ("awaiting dev review") — I did not crawl the ledger's "## Auto-converted review history" section if it exists. If the ledger's history section records the dev-fix1 already, the row's "drafted" status is a display-glitch and the WARN is cosmetic. Either way, the WARN stands as an action item for master.
- **What I am confident about.** All 13 line-edit checklist items pass except the bookkeeping WARN. The chapter is ready to advance to the next gate (line-edit approval → copy-edit pass when all chapters are approved → ship).

---

## Verdict

**PASS_WITH_WARN**

- **FAILs:** 0
- **WARNs:** 1 (ledger.md ch-12 row out of sync with post-dev-fix1 state — bookkeeping, not prose)
- **Action:** Master updates `ledger.md` ch-12 row (status → `dev-reviewed`, append one-line note recording the 2 fixes). Then ch-12 advances to `line-edited`.

## Call to action

Ready to ship ch-12 line-edit once master syncs the ledger row. No prose changes needed.
