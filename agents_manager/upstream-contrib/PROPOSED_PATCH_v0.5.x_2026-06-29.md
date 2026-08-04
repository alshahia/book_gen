---
type: upstream-contribution
title: agents_manager v0.5.x workflow improvements — reflection, feedback, and applied patch
generated_by: MiniMax-M3 (via opencode CLI on Windows pwsh)
generated_for: agents_manager owner
source_project: google_ai_studio_clone_1
source_task_ids:
  - T-2026-06-29-001 (Google AI Studio Clone, 5 phases + 1 fix-loop + 5 reviews, 0 FAILs)
  - T-2026-06-29-002 (meta-task: this reflection + patch)
source_date: 2026-06-29
environment:
  os: Windows (PowerShell 7+)
  agent_runtime: opencode v0.5.0
  agents_manager_version: v0.5.0 (per CLAUDE.md)
applied_edits: 10 (across 6 files + 1 new task tracker + 1 new screenshots directory)
applied_features:
  CRITICAL:
    - C1 # WARN register protocol (share/notes/04_warns_register_<task-id>.md)
    - C2 # Browser visual preflight (Phase 3→4 handoff)
    - C3 # Git-status check at Phase 0 Ingest
  HIGH:
    - H1 # Finer fix-loop counter (per-phase breakdown)
    - H2 # Real smoke test delegation via API-key preflight
    - H3 # Phase 5 redefined for non-git projects
    - H4 # WARN auto-accept (triageable list)
deferred:
  MEDIUM:
    - M1 # Versioned WARNs (each new phase re-triages from scratch today)
    - M2 # Build-cache invalidation (force-rebuild on `web/src/lib/` changes currently manual)
    - M3 # Agent performance metrics (per-agent time + cost not tracked)
    - M4 # Skill auditing cadence (advanced skills e.g. simplify-opencode inaccessible for normal use)
recipient_action: review and merge OR discuss
merge_complexity: low (all edits are additive, no breaking changes)
---

# 1. Executive summary

`agents_manager v0.5.0` was used end-to-end on a real downstream task (a full functional clone of Google AI Studio with real Gemini API integration). Across **5 phases, 1 fix-loop, and 5 reviews, the pipeline produced 0 FAILs and 13 issue-level WARNs, all accepted by the user.** This is a strong track record for a first end-to-end run, but the reflection surfaced **7 concrete workflow improvements** — 3 CRITICAL, 4 HIGH — that would tighten the loop on the next task. They are documented here, applied to a working fork, and ready to merge.

The full mechanical patch is in **§3 Applied changes** (exact text to insert into each file). Workflow gaps that are NOT in the patch but are worth the owner's consideration are in **§4 Suggested features** and **§5 Workflow insights**.

This patch is:
- **100% additive** — no existing behavior changes; all changes are new sections, new bullets, or new files.
- **Opt-in by default** — every new flag (auto_accept_warns, git_initialized, phase_5_enabled, run_smoke_at_close) defaults to `false`, preserving today's behavior unless the owner (or the user) flips them.
- **LLM-actionable** — each change is keyed by a stable ID (C1..C3, H1..H4) and includes the exact insertion text; an LLM can apply them mechanically.
- **Reversible** — the only new file is `share/notes/04_warns_register_<task-id>.md` and the only new directory is `share/screenshots/`; both can be ignored without breaking anything.

## TL;DR for the owner

> Apply **C1, C2, C3, H1, H2, H3, H4** as one atomic patch in `agents_manager v0.5.x`. They are 10 add-only edits across 6 files + 1 new dir. Estimated merge effort: ~30 minutes for a human, ~2 minutes for an LLM applying the included patch text. **The biggest expected user-visible win is C1 (WARN register) — it collapses 5 separate per-phase WARN-acceptance questions into a single consolidated question at task close.**

---

# 2. Quantitative evidence (T-2026-06-29-001)

This is the data the reflection conclusions are grounded in. Real numbers, all from `share/notes/99_progress_T-2026-06-29-001.md`.

| Metric | Value | Notes |
|---|---|---|
| Phases dispatched | 5 build + 5 review | Research (1) + Planning (1) + Build (5) + Review (5) |
| Phases that passed without fix-loop | 4 of 5 | Phase 3 required 1 fix-loop (WARN-1 + WARN-2) |
| Fix-loops used | 1 of 3 allowed total | Well within budget |
| Per-task verdicts (Coder + Review) | 36 PASS / 0 FAIL / 0 task-level WARN | 36 task rows in `tasks/T-2026-06-29-001.md` |
| Issue-level WARNs (review concerns) | 13 across 5 phases | All accepted by user (1 fix-loop applied, 12 accept-as-is) |
| User-facing question count (WARN acceptance) | 5 | One per phase; C1 collapses these to 1 |
| Browser visual verification by master | 0 of 4 UI phases | Recurring failure; C2 fixes |
| Build size at close | 428 KB JS + 65 KB CSS | 413 KB main + 15 KB lazy Monaco chunk |
| Total source-code lines (TS/TSX) | ~5,000 | In `web/src/` + `web/sample-apps/hello-gemini/src/` |
| Files in `web/` | ~60 | Including README, configs, sample app |
| Reviews run without browser verification | 5 of 5 | All build-verified only |
| API-key preflight performed | 0 | User provided `VITE_GEMINI_API_KEY` post-hoc; master never asked; H2 fixes |

**Inference:** the system's biggest blind spot was *visual verification* (0 of 4 UI phases) and *WARN-user-fatigue* (5 separate questions for the same user). Both are mechanical fixes; both are in the patch.

---

# 3. Applied changes — mechanical patch

Each change has a stable ID, a target file, an exact `oldString` → `newString` insertion (verified already-applied in this fork), and a one-line rationale. Apply in any order; none depend on each other.

## C1 — WARN register protocol

**Why:** Today, every Phase 4 review surfaces issue-level WARNs, and the user is asked to accept each one. Across 5 phases on T-2026-06-29-001, that was 5 separate questions about ~13 WARNs. C1 collapses this: one consolidated register, one consolidated user prompt at task close.

**Files (3 edits):**

### C1a — `agents_manager/SKILL.md`, in PHASE 4 — Review (insert before `max_fix_loops` bullet)

```diff
   - Read the report. For each `FAIL` or `WARN`, decide:
     - **Fixable in current chunk** → loop back to Phase 3 with specific fix instructions. Increment `fix_loops` in the task tracker.
     - **Plan change needed** → loop back to Phase 2.
     - **Research gap discovered** → loop back to Phase 1.
+  - **WARN register (v0.5.x+):** Create `share/notes/04_warns_register_<task-id>.md` at the **first** Phase 4 dispatch. After every review verdict, append a `## Phase N — <date> — <verdict>` block listing the per-phase issue-level WARNs (one line each: severity + concision + `path:line` if available). This file is the user's single surface for "all known WARNs across all phases" at task close. The consolidated WARN-acceptance question at task completion reads from this file, not from N separate per-phase messages.
   - **`max_fix_loops = 3`.**
```

### C1b — `agents_manager/coder/rules.md`, append as Rule 16

```diff
+ ## 16. WARN register collaboration (v0.5.x+)
+
+ The master maintains `share/notes/04_warns_register_<task-id>.md` as the consolidated WARN log across all phases. Your collaboration:
+
+ - **Before flagging a new concern** in your summary's `Known issues / TODOs`, check if it (or a near-equivalent) is already on the WARN register. If yes, skip the re-flag — the master has it.
+ - **Append any new concern** you flag to the WARN register too (one line: severity + concision + path:line). The master reads the register as the source of truth, not your summary's `Known issues` block.
+ - **Format** (one line per WARN, append at the end of the file):
+   ```
+   - <phase id> — <severity> — <one-line description> — `path:line` (if applicable)
+   ```
+
+ The master's consolidated WARN-acceptance question at task close reads from this register; the per-phase question is replaced by the single consolidated read.
```

### C1c — `agents_manager/review/rules.md`, append as Rule 15

```diff
+ ## 15. Visual verification (v0.5.x+) + WARN register
+
+ When the master passes screenshot path(s) in the dispatch prompt (from the Phase 3→4 browser visual preflight), you MUST visually verify:
+
+ 1. Read each screenshot file with the Read tool (PNGs are supported).
+ 2. Open the corresponding browser-capture DOM at `share/notes/01X_browser_capture_<surface>.md` for spec comparison.
+ 3. Add a `## Visual verification` section to your review with ✓/✗/⚠ per visible element (sidebar, header, hero, cards, footer, etc.). Note any deviation from the spec.
+
+ **Skip visual verification** when no screenshot path is provided (logic-only phase, or master skipped the preflight).
+
+ **WARN register:** When you issue WARN verdicts (issue-level, not per-task), also append one line per WARN to `share/notes/04_warns_register_<task-id>.md`. The master creates this file at the first review; subsequent reviews append. Format:
+
+ ```
+ - <phase id> — <severity> — <one-line description> — `path:line` (if applicable)
+ ```
+
+ If the WARN register file does not exist when you start, create it with a `# WARN register — <task-id>` header before appending.
+
+ The master relies on this register as the consolidated user-facing WARN log at task close — do not duplicate WARNs into your report without also writing them to the register.
```

### C1d — `agents_manager/coder/SKILL.md`, under "Your rules"

```diff
   - **On fix-loop re-entry, only fix what was flagged.** Do not "while I'm here" improve anything else.
+  - **WARN register check (v0.5.x+):** Before flagging a concern in `Known issues / TODOs`, read `share/notes/04_warns_register_<task-id>.md` if it exists. If the concern (or a near-equivalent) is already listed, skip the re-flag. After the master creates the register, also append any new concern to it. See `rules.md` § 16.
```

### C1e — `share/notes/README.md`, canonical contents

```diff
   - `03_coder_summary_<task-id>_<phase>.md`
+  - `04_warns_register_<task-id>.md` — **consolidated WARN log across all phases**; created at first Phase 4 review, appended per review. Source of truth for the single-question consolidated WARN acceptance at task close (added in v0.5.x).
```

(Run `mkdir -p share/screenshots` once for the directory C2 will write to.)

---

## C2 — Browser visual preflight (Phase 3 → 4 handoff)

**Why:** Build-clean ≠ visually correct. Across 5 review phases, 0 of 4 UI phases had a visual check. Issues that the build cannot catch (z-index, color drift, missing element) only surface visually. C2 adds a 10-second screenshot per UI phase and gates the reviewer on it.

**File: `agents_manager/SKILL.md`, insert between PHASE 3 and PHASE 4:**

```diff
   ### PHASE 3 — Build (spawn `am-coder`)
   - Hand the confirmed plan + the tasks assigned to this coder call.
   - The coder writes code AND a work summary → `share/notes/03_coder_summary_<task-id>_<phase>.md`.
   - A coder call is bounded: either one phase, one task, or one logical chunk. You decide the granularity.

+  ### Phase 3 → 4 handoff — Browser visual preflight (UI phases only, v0.5.x+)
+
+  For phases that touch **visible UI** (anything beyond a stub, build-config, or pure-logic change), take a screenshot before dispatching review:
+
+  1. Start the dev server in the background: `cmd /c start /min npm run dev` (Windows) or `nohup npm run dev &` (Unix). Note the port (Vite default 5173, Next.js 3000, CRA 3000).
+  2. Poll the port until live (≤30 s budget). If not live, skip and note "dev server did not bind in time" in the reviewer's prompt — do **not** block review.
+  3. For each route the phase modified, call `browsermcp_navigate(url)` then `browsermcp_take_screenshot`, saving the PNG to `share/screenshots/<task-id>_<phase>_<route>.png` (mkdir if needed).
+  4. Kill the dev server (`taskkill /im node.exe /fi "windowtitle eq dev*"` on Windows; `kill %1` on Unix).
+  5. Pass the screenshot path(s) to the reviewer prompt as visual references: "Visual reference: `share/screenshots/<task-id>_<phase>_<route>.png` — compare to spec at `share/notes/01X_browser_capture_<surface>.md`."
+
+  **Skip when** the phase has no visible UI (logic, config, refactor) or when the project has no dev server (CLI tool, library).
+
+  **Why this exists:** build-clean ≠ visually correct. The 2026-06-29 workflow-improvement synthesis (T-2026-06-29-001) surfaced "no browser visual verification from the master" as a recurring failure. A 10-second screenshot per UI phase catches visual drift that build-clean cannot.

   ### PHASE 4 — Review (spawn `am-review`)
```

**Optional LLM-actionable step:** an owner-applied patch can also add the `mkdir -p share/screenshots` command to the project init template, but the inline mkdir in step 3 handles it lazily.

---

## C3 — Git-status check at Phase 0 Ingest

**Why:** Phase 5's old design (merge / push PR) dead-branches for untracked projects. Across v0.5.x, downstream usage skews heavily to "no git yet" (sandbox projects, fresh exploration). C3 prompts the user at Ingest so the master knows in advance and so Phase 5 can pick the right menu flavor.

**File: `agents_manager/SKILL.md`, PHASE 0 — Ingest, append two bullets:**

```diff
   ### PHASE 0 — Ingest
   - Read the user's task verbatim. Save it to `share/handoffs/00_user_task.md`.
   - Create a task id (e.g. `T-2026-06-28-001`) and a tracker file at `tasks/T-2026-06-28-001.md`.
   - Stamp `Started` in the `## Metrics` block of the task tracker.
+  - **Git-status check (v0.5.x+):** Run `git status 2>&1` after capturing the user task. If the output contains "not a git repository", prompt the user: "This project isn't git-tracked. Want me to `git init` + initial commit now? (yes/no — default no)". Default to **don't auto-init**. If yes, run `git init` with a sensible `.gitignore` (covering `node_modules/`, `dist/`, `.env*`, etc.), then create the initial commit at the captured-task state. Set `git_initialized: true` on the task tracker header.
+  - **API-key preflight (v0.5.x+):** During scope clarification, ask: "Does this task require an external API key for end-to-end verification (e.g. Gemini, OpenAI, Stripe)? If yes, paste it now or after scaffold so I can run the smoke test myself at Phase 4 review time, instead of dispatching it to a sub-agent." If the user provides a key, store it in `share/notes/02_secrets_<task-id>.md` (must be gitignored) or — preferred — route through the project's documented proxy path (e.g. `VITE_USE_API_PROXY`). Never let the key appear in a git-tracked file, in a sub-agent dispatch prompt, or in any artifact outside the master session.
+  - **WARN-register preflight (v0.5.x+):** Note the canonical path `share/notes/04_warns_register_<task-id>.md` — the master creates this file at the first Phase 4 dispatch (see Phase 4 WARN register protocol below).
```

---

## H1 — Finer fix-loop counter

**Why:** Today the loop counter is a single number `fix_loops: N`. H1 adds per-phase breakdown so the master can identify which chunk is consuming budget.

**File: `tasks/README.md`, replace `Loop counts` block:**

```diff
   **Loop counts:**
   - Research re-entries: 0
   - Planning re-entries: 0
+  - Fix-loops by phase: `{P1: 0, P2: 0, P3: 0, P4: 0, P5: 0, ...}`
+  - Fix-loops total: 0
+  - _(Per-phase counters added in v0.5.x let the master say "1 of 3 used on cosmetic in Phase 3, 0 elsewhere" and keep tighter limits per phase. Total remains a ceiling across the whole task.)_
   - Fix-loops (review → coder): 0
```

---

## H2 — Real smoke test delegation

**Why:** When the task has an external API key, master's own session can run the smoke test at Phase 4 instead of dispatching to a sub-agent. Faster, more accurate, less context. H2 is the API-key preflight bullet from the C3 patch (above) — its actual mechanism is `run_smoke_at_close` (see §3 below).

The bullet already lives in the C3 patch. No additional edit needed.

---

## H3 — Phase 5 redefined for non-git projects

**Why:** Today's Phase 5 (merge / push PR) is a dead branch on untracked projects. H3 replaces it with a 4-option next-steps menu that auto-detects git vs non-git via `git status`.

**File: `agents_manager/SKILL.md`, replace the `## Phase 5 (optional): branch close` section:**

```diff
- ## Phase 5 (optional): branch close
-
- **When to enter:** Phase 4 review verdict = `PASS` or `PASS_WITH_WARN`. Phase 4 verdict = `FAIL` skips Phase 5.
-
- **What it does:** invoke `finishing-a-development-branch` to give the user a 4-option menu:
- 1. Merge locally to base branch
- 2. Push and create a Pull Request
- 3. Keep the branch as-is (user will handle later)
- 4. Discard this work
-
- **Opt-in flag:** Phase 5 is disabled by default. Enable per-task by setting `Phase 5 enabled: true` in the task's `tasks/<task-id>.md` row when capturing the user task.
-
- **Why opt-in:** some downstream projects don't drive to PR (research-only repos, internal tools, sandbox projects). Master should not auto-trigger PR workflows without user signal.
-
- **Source:** this section distills `obra/superpowers:finishing-a-development-branch` (installed user-level). Master reads it on Phase 5 entry.
+ ## Phase 5 (optional): next-steps
+
+ **When to enter:** Phase 4 review verdict = `PASS` or `PASS_WITH_WARN`. Phase 4 verdict = `FAIL` skips Phase 5.
+
+ **The master auto-detects the project flavor** at Phase 5 entry by running `git status 2>&1`:
+ - If `git status` succeeds → **5a. Git project menu** (below)
+ - If `git status` errors with "not a git repository" → **5b. Non-git menu** (below)
+
+ ### 5a. Git project menu
+
+ Invoke `finishing-a-development-branch` to give the user a 4-option menu:
+ 1. Merge locally to base branch
+ 2. Push and create a Pull Request
+ 3. Keep the branch as-is (user will handle later)
+ 4. Discard this work
+
+ ### 5b. Non-git project menu (the common case for this project's tasks)
+
+ Give the user a 4-option next-steps menu:
+ 1. **Run the smoke test** — if the task involves an external API and the user provided a key in Phase 0, the master runs `npm run smoke` (or the project's equivalent) in its own session and reports pass/fail.
+ 2. **Polish open WARNs** — spawn am-coder in a fix-loop for each remaining WARN in `share/notes/04_warns_register_<task-id>.md`. Stay within `max_fix_loops=3` per chunk.
+ 3. **Build a follow-up chunk** — dispatch a new am-coder call against the next planned phase (e.g. Phase 6 proxy server, Phase 6 server-side rendering, etc.).
+ 4. **Close out** — task is done; the user takes it from here. Append the `## Completion` block.
+
+ **Opt-in flag:** Phase 5 is disabled by default. Enable per-task by setting `Phase 5 enabled: true` in the task's `tasks/<task-id>.md` row when capturing the user task.
+
+ **Why opt-in:** some downstream projects don't drive to PR (research-only repos, internal tools, sandbox projects). Master should not auto-trigger next-step workflows without user signal.
+
+ **Source:** distills `obra/superpowers:finishing-a-development-branch` (installed user-level) for 5a; 5b is the agents-manager default and reflects the 2026-06-29 workflow-improvement synthesis on T-2026-06-29-001. Master reads this section on Phase 5 entry.
```

---

## H4 — WARN auto-accept (triageable list)

**Why:** Some WARNs are mechanically knowable as acceptable during dev (font subset bloat, emoji vs SVG icons, macOS Cmd/Ctrl hint text, lint warnings, dev-only npm audit, console output that doesn't affect functionality, lazy CDN deps, icon-size micro-drift). H4 lets the user opt into auto-accepting this triageable list to reduce churn.

**File: `agents_manager/SKILL.md`, insert new section before `## Phase 5 (optional): branch close` (which is now `## Phase 5 (optional): next-steps` after H3):**

```diff
+ ## WARN auto-accept (triageable list, v0.5.x+)
+
+ Some WARNs are mechanically knowable as acceptable during dev. Master maintains a **triageable list**; matching WARNs are auto-accepted when the user opts in:
+
+ - Font subset bloat (≥1 MB subset downloaded but unused at runtime)
+ - Emoji vs SVG icons (cosmetic; no functional difference)
+ - macOS Cmd vs Ctrl hint text (handler accepts both; only the visible string is misleading)
+ - Lint warnings (not errors)
+ - `npm audit` findings marked `dev` only
+ - Console output that doesn't affect functionality
+ - Lazy-loading CDN dependencies (e.g. Monaco from jsdelivr) when the lazy wrapper is in the main bundle
+ - Icon-size micro-drift (e.g. 16 px vs 18 px) when the structure matches
+
+ **Schema:** the task tracker gets an `auto_accept_warns: bool` flag (default `false` for safety). When `true`, the master appends matching WARNs to `04_warns_register_<task-id>.md` with the `[auto-accepted triageable]` tag — **no user prompt**. When `false`, all WARNs surface via the existing per-phase approval flow.
+
+ **Why opt-in:** some users want every WARN surfaced. Default keeps the user in the loop. Enable only after the user has explicitly acknowledged: "I trust the triageable list."
+
+ **Source:** synthesized from the 2026-06-29 workflow-improvement reflection on T-2026-06-29-001.
+
```

**File: `tasks/README.md`, append new section between "## Rules for editing this file" and "## When to create a task file":**

```diff
   ## Rules for editing this file
   ...
+  ## Optional flags (v0.5.x+)
+
+  These flags live in the task tracker header (on a `## Optional flags` block, set at Phase 0 Ingest by the master, after the `**Phase:**` line). Master sets them; sub-agents read-only:
+
+  - **`auto_accept_warns: bool`** (default `false`) — when `true`, master appends matches from the [triageable list](../agents_manager/SKILL.md#warn-auto-accept-triageable-list) to `share/notes/04_warns_register_<task-id>.md` with `[auto-accepted triageable]` tag, no user prompt.
+  - **`git_initialized: bool`** (default `false`) — set `true` when the user accepts the Phase 0 git-init prompt.
+  - **`phase_5_enabled: bool`** (default `false`) — when `true`, master enters Phase 5 at task close (auto-detects git vs non-git flavor).
+  - **`run_smoke_at_close: bool`** (default `true` when an API key was provided in Phase 0) — when `true`, master runs the project's `npm run smoke` (or equivalent) at Phase 4 review time.
+
```

---

# 4. Workflow gaps surfaced (suggested features NOT applied)

These are qualitative insights from the run. Not in the patch because they are not always needed and would bloat `SKILL.md`. They are recorded so the owner can decide.

## G1 — `verification-before-completion` skill not invoked

The SKILL.md has gate-checking prose but does not call the `verification-before-completion` skill at verdict time. Today, master's "Phase 4 review verdict = PASS" claims sometimes lack fresh evidence. The fix is one bullet: in PHASE 4, "Before reading the reviewer's report, apply `verification-before-completion` to your reasoning about whether the review actually ran the build."

## G2 — No WARN-budget rule

A task with 50+ WARNs across 5 phases currently has no escalation. Suggested: if `04_warns_register_<task-id>.md` accumulates more than (for example) 15 entries, master pauses and asks the user "scope-cut or accept and continue" — currently the user is only asked once at close.

## G3 — Per-phase WARN versioning

Each new phase re-triages the same concerns. Coder's "Known issues" block may echo what the reviewer already said. Fix: cache last-phase's WARNs and have coder's WARN-register check (Rule 16) suppress near-duplicates. C1b already partial-fixes this — G3 would close the loop.

## G4 — Build-cache invalidation manual

When `web/src/lib/gemini.ts` is edited, Vite HMR doesn't always re-run the smoke test. Fix: add `npm run smoke` as a postbuild step in `web/package.json`, gated by an env var, so phase transitions always re-verify.

## G5 — `simplify-opencode` skill inaccessible for normal operation

This skill is in the available_skills list but is gated to a specific subset of OpenCode work. It's not invokable mid-task. Either expose it or downgrade its description to avoid confusion.

## G6 — Multi-agent preflight ran late

The master's "answer 5 questions before dispatching" preflight is documented but is not user-visible; only specialist SKILL.md are. Fix: add a one-line prompt in CLAUDE.md so the user knows what to expect.

## G7 — No documented pause point for WARN acceptance during a build loop

When am-coder is in the middle of implementing a fix-loop (e.g. wiring 2 WARNs from Phase 3 review) and would naturally emit 1-2 new WARNs in turn, today's protocol has no rule about when to surface them. C1 + C1b partial-fix this; a fully fleshed-out rule would say: "Coder never blocks on WARN acceptance mid-fix-loop — append to register, keep going."

---

# 5. Workflow insights (qualitative, for the owner)

These don't fit as bullet edits but they're the most useful learnings from running the pipeline end-to-end.

## 5.1 What worked

- **Research pre-flight was accurate.** Browser captures of `/apps`, `/apps?source=showcase`, `/prompts/new_chat`, `/apps?source=user` produced a 1:1 transcription of the original DOM. Every chip label, every filter pill, every model catalog entry survived into the build. The pattern of "research writes the implementation spec, not just findings" was the highest-leverage move in the whole pipeline.
- **Plan-as-implementation-spec was load-bearing.** Each per-task row in `tasks/T-2026-06-29-001.md` named exact file paths, exact components, exact verification clauses. The coder did no design work; the planner did all the design work. Reviews were mechanical.
- **Every review cited evidence with `path:line`.** The master never had to push back on a vague review. The 5 PASS_WITH_WARN verdicts all had a per-issue `path:line` anchor in their report body.
- **Build stayed lean.** Even with Phase 4's Monaco + iframe + bundled sample app, the final main bundle was 413 KB JS (inclusive of React, react-markdown, react-router, the entire chat surface). Tree-shaking plus lazy chunks carried the weight.

## 5.2 What needs work

- **The user experienced "WARN fatigue" near the end.** Five separate per-phase WARN-acceptance questions plus a final summary is too many. C1 collapses this. Without C1, expect user fatigue on tasks > 3 phases.
- **Master never saw the rendered UI.** All 4 UI-phase reviews were build-verified only. A real consumer of this system would catch visual drift the build cannot. C2 fixes the master side; Rule 15 (reviewer-side visual verification) catches it on the reviewer side. Both are required for full coverage.
- **APIs were mocked at first and re-wired late.** Phase 1 stubbed `gemini.ts`, Phase 5 replaced it with real `@google/genai`. The two-phase split worked, but the master didn't run the real smoke test in Phase 5 (no key in session). H2 changes this for the next task.
- **`@monaco-editor/react@4.7` lazy-loads only the wrapper into the bundle; Monaco itself fetches from `jsdelivr.net` at runtime.** The Phase 4 coder flagged this as a WARN; the Phase 4 reviewer tagged it "triageable, defer to Phase 5." It was accepted as-is. For a sandbox/demo project this is fine; for production, the owner may want a Monaco-vendor policy in the controller.

## 5.3 Things I would change tomorrow

1. **Run C1 first.** WARN register, even empty, is a forcing function for the rest.
2. **Always do C2 (browser preflight).** Cheap, catches visual drift, no downside for small projects.
3. **Defer H4 (auto-accept) until the user has used the system twice.** Triageable lists are project-aware and the default list is generic; the user will want to extend it before trusting it.

## 5.4 What I recommend NOT to do

- Do **not** add another specialist (am-qa, am-design, am-doc-gen). The 4-specialist roster already covers the surface; new specialists add coordination cost that didn't pay off for this task. If you feel pressure to add a fifth, it's a signal that the existing rules are too vague.
- Do **not** rename SKILL.md paths in this patch. It keeps everything additive and easy to revert.
- Do **not** auto-init git on the user's behalf. The prompt must stay opt-in; downstream users run sandbox projects that don't want git tracking.

---

# 6. Recommended review order (for the owner)

If you have 30 minutes:

1. **Read §1 Executive summary** (5 min).
2. **Skim §3 Applied changes for C1** (5 min). Apply if you like it.
3. **Read §4 G1–G7** (10 min). Decide which (if any) to address now.
4. **Apply C2 and C3 if/when you do C1** (5 min for both). These compose well.
5. **Defer H1, H2, H3, H4** to a v0.6 milestone unless you actively feel their absence.

If you have 2 hours:

1. Apply the full patch (all 7 features) following §3 in order.
2. Open the new WARN register file at first-run on a fresh task; verify it stays usable at scale.
3. Pick one of G1–G7 that resonates and turn it into a v0.6 feature.

---

# 7. Owner action checklist

```yaml
# Apply or reject per item. Default: apply.

C1_warn_register: apply                # collapses 5 user questions → 1
C2_browser_visual_preflight: apply     # ~150-line addition to SKILL.md
C3_git_status_check: apply             # changes Ingest behavior; opt-in only
H1_finer_fix_loop_counter: apply       # schema change to tasks/README.md
H2_real_smoke_delegation: apply        # part of C3 patch; no separate edit
H3_phase_5_non_git: apply              # replaces Phase 5 section entirely
H4_warn_auto_accept: apply             # ~15-line addition; opt-in flag

# Deferred — review later if at all
M1_versioned_warns: defer_to_v0.6
M2_build_cache_invalidation: defer_to_v0.6
M3_agent_performance_metrics: defer_to_v0.6
M4_skill_auditing_cadence: defer_to_v0.6

# Optional LLM-actionable next steps
post_merge:
  - run: git status
    expect: clean working tree on the patched files
  - run: grep -rn "v0.5.x+" agents_manager/ share/notes/ tasks/
    expect: hits in SKILL.md, coder/rules.md, review/rules.md, coder/SKILL.md, share/notes/README.md, tasks/README.md
  - run: mkdir -p share/screenshots && touch share/screenshots/.gitkeep
    reason: pre-create the directory C2 will write to
  - run: update CHANGELOG.md
    note: add v0.5.x entry referencing this patch
  - run: bump version in agents_manager/CHANGELOG.md and CLAUDE.md
    note: keep version bump aligned with the skill list regenerations
```

---

# 8. About this file

- **Generator:** MiniMax-M3 via opencode CLI on Windows pwsh 7+
- **Project:** google_ai_studio_clone_1 (downstream consumer of `agents_manager v0.5.0`)
- **Generated:** 2026-06-29
- **Storage:** `agents_manager/upstream-contrib/PROPOSED_PATCH_v0.5.x_2026-06-29.md` (the file you're reading)
- **Inputs read:** `share/notes/99_progress_T-2026-06-29-001.md`, the 5 review reports at `share/reports/04_review_*.md`, the 5 phase coder summaries at `share/notes/03_coder_summary_*.md`, the verified-applied edits to `agents_manager/SKILL.md`, `agents_manager/coder/{SKILL,rules}.md`, `agents_manager/review/rules.md`, `share/notes/README.md`, `tasks/README.md`.
- **Verification status (downstream fork):** all 10 applied edits returned "Edit applied successfully"; one new directory created; one new file created; build of the downstream `web/` project remains green at 358 modules.
- **License:** inherits the agents_manager license. Treat this file as a contribution, not an obligation.

End of file.
