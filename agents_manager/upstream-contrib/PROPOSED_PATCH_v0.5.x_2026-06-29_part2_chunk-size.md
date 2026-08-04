---
type: upstream-contribution
title: agents_manager v0.5.x+ chunk-size protocol — adaptive thresholds + planner/master shared decision
generated_by: MiniMax-M3 (via opencode CLI on Windows pwsh)
generated_for: agents_manager upstream owner
source_project: google_ai_studio_clone_1
source_task: T-2026-06-29-001 (Phase 4 oversized: 23 new files, ~1500 LOC, 3 novel abstractions, 6 issue-WARNs in one chunk)
source_date: 2026-06-29
part_of: [PROPOSED_PATCH_v0.5.x_2026-06-29.md (Patch-1)]
environment:
  os: Windows (PowerShell 7+)
  agent_runtime: opencode v0.5.0
  agents_manager_version: v0.5.0
proposed_features:
  - C1 # Per-phase complexity estimation (planner's new responsibility)
  - C2 # Master re-ask + dispatch-decision protocol
  - C3 # Per-phase LOC + WARN metric extension
adaptation: thresholds are per-phase (planner estimates), hard triggers are safety floor only
re_ask_limit: 2 per phase
novel_abstraction_seed_list:
  - Lazy-loaded heavy editors (Monaco / CodeMirror / Slate)
  - Sandboxed iframe with custom origin / CSP
  - Sub-application with independent build pipeline
  - Runtime external API integration (not just type-imported)
  - WebSocket persistent connection
  - WebRTC peer connection
  - WASM / background workers / service workers
  - Custom build tools / plugin authoring
hard_trigger_safety_floor:
  LOC: 1200
  files: 15
  novel_abstractions: 2
recipients:
  - agents_manager upstream owner
  - any LLM or agent applying the patch mechanically
recipient_action: review and merge after Patch-1
merge_complexity: low (additive on top of Patch-1; depends on H1's per-phase loop counter)
---

# 1. Executive summary

A real downstream run of `agents_manager v0.5.0` (5 phases + 1 fix-loop + 5 reviews, 0 FAILs, 13 issue-level WARNs) exposed a chunk-sizing failure that the plan agent's "tasks per phase ≤ 8" rule could not catch: **Phase 4 was 1500 LOC + 23 files + 3 novel abstractions in one chunk**, while Phases 1-3 and 5 averaged 650 LOC + 13 files + 0 novel abstractions. The reviewer handled it but at 6 issue-WARNs (vs 1-4 elsewhere) it was visibly past their comfort zone. The plan agent even self-rated Feasibility 4/5 with the comment "Phase 4 is the heaviest" — the warning was right there, but master downplayed it.

This patch is the structural fix.

**Three changes, ~60 net-additive lines, 3 files touched:**

| ID | File(s) | Lines | Purpose |
|---|---|---|---|
| **C1** | `agents_manager/planning/rules.md` + `agents_manager/planning/SKILL.md` | ~20 | Planner writes a per-phase `Complexity` block (novel abstractions + LOC + files + review-difficulty word + split recommendation + reason) |
| **C2** | `agents_manager/SKILL.md` (PHASE 3 sub-section) | ~25 | Master reads the estimate at dispatch time; may re-ask planner (≤2×) with concrete feedback; may brainstorm with am-review; master has final say |
| **C3** | `tasks/README.md` (extend Metrics table) | ~15 | Add `LOC written` + `WARNs` columns to per-phase timings; new `## Phase productivity` block at close |

**Why this is different from a global "LOC < 800" rule:**

A fixed global threshold would be wrong for two opposite reasons. It would be *too loose* on a phase with 800 LOC + 2 novel abstractions (Monaco + WebSocket — reviewer's eye glazes), and it would be *too tight* on a phase with 800 LOC + 0 novel abstractions (pure CRUD over known patterns — already comfortable). Adaptive per-phase estimation, with a small set of hard-trigger safety catches, gets it right.

**How it composes with Patch-1:**

| Patch-1 feature | Patch-2 dependency |
|---|---|
| H1: per-phase loop counter | C3 extends the same metrics table |
| WARN register (C1) | C3's `WARNs` column pulls from the same source |
| Browser visual preflight (C2) | C2's "brainstorm with am-review" runs at the same handoff |

Merge Patch-1 first, then Patch-2. Or merge them as one atomic release — they don't conflict.

## TL;DR for the owner

> Add three changes (C1+C2+C3 = ~60 lines) so the planner estimates per-phase complexity instead of relying on master judgment alone. Master still has the final say. The big payoff is that on the next "Phase 4 looks too big" the warning surfaces **at plan time** instead of **at review time** — when it's actionable rather than discoverable.

---

# 2. Quantitative evidence (Phase 4 oversized)

| Phase | Tasks | Files new | Files mod | LOC est. | Loc/file | Novel abstractions | Review WARNs |
|---|---|---|---|---|---|---|---|
| 1 — Scaffold + design system | 8 | 24 | 0 | ~700 | 30 | 0 (all known patterns) | 4 (all cosmetic) |
| 2 — Build home + Gallery | 7 | 8 | 3 | ~600 | 55 | 0 | 3 |
| 3 — Playground chat | 8 | 12 | 2 | ~800 | 57 | 0 | 4 |
| **4 — My apps + AppBuilder** | **7** | **19** | **4** | **~1500** | **65** | **3** | **6** |
| 5 — Real Gemini + smoke | 6 | 0 (replacement) | ~5 | ~400 | 80 | 0 (replaces existing module) | 1 |

What Phase 4 contained that the others didn't:
1. **Monaco lazy-loaded wrapper** (no prior code) — reviewer had no pattern to anchor against
2. **Sandboxed iframe with `allow-scripts allow-same-origin`** — new Vite plugin pattern
3. **Sub-application with independent Vite/React/TS build pipeline** + `copy-sample-app.mjs` script — whole new build subgraph

Each of those three things is independently "ask an LLM to write a tutorial on it." Combining them in one review is what produced the 6 issue-WARNs (vs ~3 elsewhere). Phase 4 split into 4a/4b/4c would have put each novel abstraction in its own chunk, and the reviewer would have hit a comfortable pattern for 4a (My apps, familiar table UI) and isolated the novel surface for review-only on 4b/4c.

The plan agent's own self-score (Feasibility: 4/5) included the note "Phase 4 (Monaco + iframe + sample app) is the heaviest surface — only Phase 4 is a 4 not a 5" — that warning was correct, and master missed the action it implied.

---

# 3. Proposed changes (mechanical patch)

Each change shows exact insertion text and where it lands. Apply in order C1 → C2 → C3; C3 composes on Patch-1's H1 (per-phase loop counter).

## C1 — Per-phase complexity estimation (planner's new responsibility)

### C1a — `agents_manager/planning/rules.md`

If the file does not have a "Complexity estimation" rule, append this block at the end:

```markdown
## N. Complexity estimation (v0.5.x+)

For every phase you propose, attach a `### Complexity` block to the phase section in `02_plan_phases_<task-id>.md`. The schema:

| Field | Type | Notes |
|---|---|---|
| `novel_abstractions` | array | Each entry MUST be drawn from the seed list below. If none apply, leave as `[]`. |
| `LOC_estimate` | integer (approx) | Tighter upper bound is better; round to nearest 100. |
| `files_estimate` | integer | New + modified. |
| `review_difficulty` | word ∈ {low, medium, high} | Your qualitative call based on the above. |
| `split_recommended` | bool | See trigger logic below. |
| `reason` | string | One sentence explaining the recommendation. |

**Novel-abstraction seed list (mechanical, not free-text):**
- Lazy-loaded heavy editors (Monaco / CodeMirror / Slate)
- Sandboxed iframe with custom origin / CSP
- Sub-application with independent build pipeline
- Runtime external API integration (not just type-imported)
- WebSocket persistent connection
- WebRTC peer connection
- WASM / background workers / service workers
- Custom build tools / plugin authoring

If a genuinely novel abstraction you encounter is not on this list, name it inline in the array + flag it in your plan's "Why this design" summary so the owner can add it.

**Trigger logic (safety floor — do not skip these):**

If ANY of the following is true, you MUST set `split_recommended: true`:
- `LOC_estimate > 1200`
- `files_estimate > 15`
- `length(novel_abstractions) ≥ 2`

You may set `split_recommended: true` for other reasons (e.g. cross-team dependencies, blocking tests not yet written) — explain in `reason`.

You may also set `split_recommended: false` while still tripping a trigger, IF you write a `reason` justifying it (e.g. "LOC=1300 but pure CRUD over known patterns; novel=[] — recommend NOT splitting"). Master will re-evaluate this in C2.

**Placement in the plan file:**
```markdown
### Phase N — <title>
[... existing phase description ...]

### Complexity
- novel_abstractions: [...]
- LOC_estimate: 1500
- files_estimate: 23
- review_difficulty: high
- split_recommended: true
- reason: "novel_count=3 (Monaco + iframe + sub-app), LOC > 1200, files > 15 — all 3 triggers fire"
```

**Discipline:** master reads this block at PHASE 3 dispatch. If `split_recommended: true` is false but a trigger condition is met, master pauses and re-asks you (this is in scope, not a violation). See C2.
```

### C1b — `agents_manager/planning/SKILL.md`

In the "What you must produce" section, add a bullet (or paragraph — match local style):

```markdown
- **Per-phase complexity block (v0.5.x+):** Every phase section in `02_plan_phases_<task-id>.md` includes a `### Complexity` block (novel abstractions, LOC estimate, files estimate, review difficulty word, split recommendation + reason). See `rules.md` for the schema and trigger logic. Master will not dispatch am-coder for a phase without this block.
```

---

## C2 — Master re-ask + dispatch-decision protocol

### C2a — `agents_manager/SKILL.md`

In the PHASE 3 — Build section, immediately after the existing bullets, add a new sub-section. **Match the existing format conventions (markdown headers, bullet style, code-fence style).**

```markdown
### Phase 3 dispatch — Complexity check + re-ask protocol (v0.5.x+)

Before dispatching am-coder, read the per-phase `### Complexity` block written by am-planning (see `agents_manager/planning/rules.md`).

**The complexity check is a forcing function, not a global rule.** Hard triggers (LOC > 1200 OR files > 15 OR novel_abstractions length ≥ 2) are a safety floor — if a trigger fires without `split_recommended: true`, the planner did not flag it and you should treat that as a planning gap, not a passthrough.

**Re-ask loop (≤ 2× per phase):**

If you disagree with the planner's estimate or with the split recommendation:
1. Dispatch `am-planning` with a refinement ask. Be specific:
   - "Phase 4 estimate is 1500 LOC + 23 files + 3 novel abstractions. Your `split_recommended: true` — propose a sub-phase boundary at the natural seam (Monaco vs. AppBuilder-shell vs. sample-app). Update `02_plan_phases_<task-id>.md` with the sub-phases and a Complexity block for each."
2. Re-read the updated Complexity blocks. Decide again.
3. If still disagreeing, dispatch one more refinement ask (≤ 2 total re-asks).
4. After 2 re-asks you MUST either:
   - **Accept the planner's recommendation** (and dispatch per it), OR
   - **Override with your own reasoning** (and document the override in `tasks/<task-id>.md` `## Loop history`).

**Brainstorming with am-review at dispatch time (optional but recommended for chunks tripping a trigger):**

If you're about to dispatch a chunk that hits a hard trigger even after split consideration, you may dispatch `am-review` FIRST with a pre-dispatch question: "How would you scope reviewing <this chunk>? What evidence patterns would convince you the work is right? What false-accept risks would you watch for?" Capture the response verbatim and pass it as additional guidance to the coder dispatch. Document in `## Loop history`.

**Documenting the dispatch decision:**

After every dispatch (split or whole), append one line to `tasks/<task-id>.md` `## Loop history`:

```
### Dispatch — <YYYY-MM-DD HH:MM> — Phase <N>
- Pl Complexity: <LOC> LOC / <files> files / <n> novel — `split_recommended: <bool>` (reason: <one line>)
- Re-asks performed: <0 | 1 | 2>
- Decision: <dispatch whole | dispatch sub-phase <X> | override: <reason>>
- Notes: <optional>
```

If `split_recommended: true` in the plan, dispatch the **first sub-phase** (do not dispatch all sub-phases at once — each gets its own review + complexity check).
```

**Optional companion:** if you want a hard dispatch gate, you may add (under "PHASE 3 — Build"):

```markdown
- **Dispatch gate:** Do not dispatch am-coder without a `### Complexity` block in the plan for the assigned phase. If absent, re-ask planner to add one (counts toward the 2× limit).
```

---

## C3 — Per-phase LOC + WARN metric extension

This composes with Patch-1's H1 (per-phase fix-loop counter). It extends the same metrics table.

### C3a — `tasks/README.md` — extend the Phase timings table

Find the existing `## Metrics > Phase timings` block (in the template under "**Phase timings:**"). Replace it with the extended version:

```diff
  **Phase timings:**
- | Phase | Started | Ended | Duration |
- |-------|---------|-------|----------|
- | 0 Ingest   | — | — | — |
- | 1 Research | — | — | — |
- | 2 Planning | — | — | — |
- | 3 Build    | — | — | — |
- | 4 Review   | — | — | — |
+ | Phase | Started | Ended | Duration | LOC written | WARNs |
+ |-------|---------|-------|----------|-------------|-------|
+ | 0 Ingest   | — | — | — | — | — |
+ | 1 Research | — | — | — | — | — |
+ | 2 Planning | — | — | — | — | — |
+ | 3 Build    | — | — | — | — | — |
+ | 4 Review   | — | — | — | — | — |
+ | 5 Next-steps (opt) | — | — | — | — | — |
```

WARNs column is for **issue-level** WARNs from Phase 4 reviews (NOT per-task WARNs, which are in the task table).

### C3b — `tasks/README.md` — extend the Completion block

Find the `## Completion` block in the template. Add the new section after the existing fields:

```diff
  ## Completion
  <!-- master fills when all rows are done or accepted -->
  **Closed:** YYYY-MM-DD
  **Final commit / branch:** ...
  **Last clean review:** share/reports/04_review_<task-id>_<phase>.md
  **Open WARNs accepted by user:** <list or "none">

+ ## Phase productivity (v0.5.x+)
+
+ <!-- master fills at task close with a one-line summary per phase -->
+ <!-- Example: "Phase 4: 18 min, 1500 LOC, 6 WARNs — 1.5× the project's median LOC/WARN ratio" -->
+
+ | Phase | Wall-clock min | LOC | WARNs | LOC/WARN | Notes |
+ |-------|---------------|-----|-------|-----------|-------|
+ | 0 Ingest   | | | | | — |
+ | 1 Research | | | | | — |
+ | 2 Planning | | | | | — |
+ | 3 Build    | | | | | — |
+ | 4 Review   | | | | | — |
+ | 5 Next-steps (opt) | | | | | — |
+
+ **Cross-phase signal:** if any single phase trips `(LOC/WARN > 2× project median) OR (LOC > 1200 AND WARNs > 4)` without a documented split decision in `## Loop history`, the user should review whether the chunk-size protocol (C1+C2) is working.
```

### C3c — `tasks/README.md` — add data-collection hint

In the "Rules for editing this file" section, append:

```markdown
- **Phase timings data is filled by the master at task close.** Sub-agents do not write `LOC written` or `WARNs` columns — master reads coder summaries + review reports + runs `find <scope> -name '*.ts*' -newer <phase_start_marker> | xargs wc -l` to count LOC. Mark `—` if data is unavailable.
```

---

# 4. Workflow insights

These don't fit as bullet edits but they are the substantive reasoning behind the patch.

## 4.1 Why "planner suggests, master decides" is the right separation

Three alternatives the user considered:

1. **Planner splits up front** — plan has Phase 4a/4b/4c from day 1. Pro: clean task rows. Con: planner is estimating blind; locked shape is hard to revise when actual data arrives at dispatch.

2. **Master re-splits at dispatch time** — master reads `Files written` estimate, decides. Pro: data-driven. Con: no architectural input; master and planner both lack each other's context.

3. **Planner suggests, master decides** (this patch). Pro: planner has the architectural seams at plan time; master has the actual files + LOC at dispatch. Both contribute. Con: requires the planner to write `novel_abstractions` mechanically.

The asymmetry was clear in the user's framing: "plan suggest, master brainstorm/discus with other agents and may re ask the plan agent multi time to create/reformat/update/change the plan, but the final say is to master agent." That's a "expert suggests, lead decides" pattern — the planner is the architect with the larger surface context at plan time; the master is the lead with the runtime + user signal context at dispatch time. Encoding it as a re-ask loop (≤2×) keeps the planner's expertise alive at dispatch time without giving the planner authority it shouldn't have.

## 4.2 Why complexity estimation beats tasks-per-phase

The current rule in `agents_manager` is "≤ 8 tasks per phase" (per `02_plan_phases_<task-id>.md` history). Two phases with 7 tasks each can have a 5× difference in code volume — that's a 200% spread the current rule can't see. Phase 4 of T-2026-06-29-001 had 7 tasks (within budget) but each task was 200 LOC where phases 1-3 averaged 100. The rule passed while the reality was expensive.

Replacing it with `novel_abstractions × 1000 + LOC × 1` as a fatigue proxy catches this: P1 = 0 + 700 = 700; P4 = 3000 + 1500 = 4500; threshold 2500 fires. But the owner shouldn't have to compute a score — encapsulating it as 3 simple triggers (LOC/files/novel) where ANY trigger fires is good enough. The planner + master re-ask loop handles the edge cases.

## 4.3 Why hard triggers are a floor, not a ceiling

The patch presents the LOC/files/novel triggers as a safety net, not a primary decision driver. The primary driver is the planner's `split_recommended: bool + reason`. The triggers fire when:
- The planner forgot to enumerate a novel abstraction
- The planner misestimated LOC by 50%
- The planner chose not to flag a risky chunk

In any of those cases, master should pause and re-ask, not auto-split. The trigger firing is the *symptom* — the underlying issue is planner/master disagreement on what makes a phase expensive. The re-ask loop is the fix; the trigger is just the early-warning.

## 4.4 What "novel abstraction" should NOT include

Some patterns look novel but are actually well-handled by existing tools:
- Custom Tailwind classes (theme tokens — trivial)
- CSS animations / Framer Motion (well-known libraries)
- React context providers (well-known pattern)
- A new shadcn/ui component (existing library)
- Standard fetch with retries (well-known)

These should NOT trigger `novel_abstractions` unless something genuinely unprecedented is happening. The seed list is the curated version of "what feels weird to a reviewer without experience in this domain." Add to it carefully.

## 4.5 What can go wrong

- **Planner dumps novel abstractions as a garden-variety list.** If every phase ends up with `novel_abstractions: [React component, Tailwind class, Vite plugin]`, the trigger becomes meaningless. The seed list is the gate; planner must stick to it.
- **Master accepts the planner's `split_recommended: true` without re-asking.** If the planner's split is wrong (e.g. they're splitting at a non-natural seam), the master should re-ask with concrete feedback. The re-ask limit prevents infinite loops but does not prevent lazy acceptance.
- **C3 metrics turn into a leaderboard.** Don't reward "fewer LOC" — reward "right-sized chunks." LOC/WARN ratio is a sanity check, not a quality metric.

---

# 5. Decision rationale (per change)

## 5.1 C1 over alternatives

**Why per-phase planner estimation, not a single LLM-judged difficulty word:**
- Mechanical triggers are testable; a difficulty word isn't.
- Per-phase LOC/files estimates are recoverable; "this phase felt heavy" isn't.
- Novel-abstraction enumeration from a seed list is auditable.

**Why 8 items in the seed list (not 4, not 16):**
- Fewer than 6 and you'd miss WebSocket / WebRTC.
- More than 10 and the list dilutes — every entry has to mean "the reviewer doesn't know this pattern cold."
- The 8 here cover the patterns that actually feel like learning-on-the-job for a typical full-stack engineer.

## 5.2 C2 over alternatives

**Why ≤ 2× re-ask limit:**
- Aligns with `max_fix_loops=3` philosophy — there's no point in a 3rd planning iteration when the master can just override with reasoning on the 2nd.
- Forces the planner to be sharper on first pass.
- Keeps the master override path documented so it doesn't feel like a workaround.

**Why am-review pre-dispatch brainstorm is optional, not mandatory:**
- Adds overhead; only worth it on chunks that are tripping a trigger.
- Owners who don't want the overhead can skip it; nothing in the protocol depends on it.

**Why document each dispatch decision in `## Loop history`:**
- Auditability. If a year from now the owner wants to know "why did Phase 4 ship in one chunk," the Loop history has the answer.
- Without this, the protocol degrades into "master trusts planner" — which is what we just demonstrated doesn't work.

## 5.3 C3 over alternatives

**Why extend the existing Phase timings table, not add a separate metrics file:**
- Composes with Patch-1's H1 (per-phase fix-loop counter) on the same row.
- Single source of truth.
- Less file proliferation.

**Why `LOC/WARN` ratio is a sanity check, not a quality score:**
- LOC is noisy (a phase of 50 LOC × 30 files = 1500 LOC is wildly different from 1500 LOC × 1 file).
- WARN is noisy (reviewer attention varies).
- The cross-phase signal is about *consistency*, not *quality*. A phase that has 2× the project's LOC/WARN median is worth looking at; it doesn't necessarily mean it's bad.

---

# 6. Recommended review order

If you have 30 minutes:
1. Read §1 Executive summary (3 min).
2. Skim §3 C1 (5 min). Apply if you agree.
3. Read §4.1–4.3 (5 min). Decide if the design holds.
4. Apply C2 and C3 (10 min). Skip the dispatcher-decision documenting if it's too much friction — it can be added later.
5. Done.

If you have 2 hours:
1. Apply full patch in order C1 → C2 → C3.
2. Pick the next task that hits the protocol and verify the planner's first estimate is reasonable.
3. Re-read §4.5 "What can go wrong" and decide how to harden against those cases.

If you'd rather defer:
- C1 is the only critical one. C2 and C3 are value-adds; the protocol can ship with just C1 + the existing patch (which already has C1 from the architecture side).

---

# 7. Owner action checklist

```yaml
# Apply or reject per item. Default: apply in order C1 → C2 → C3.

C1_complexity_estimation:
  apply: true
  file: agents_manager/planning/rules.md
  file_2: agents_manager/planning/SKILL.md
  lines_added: ~25
  rationale: |
    Without C1, master has nothing concrete to read at dispatch time.
    Planner's existing "≤ 8 tasks" rule cannot catch file-size variance.

C2_re_ask_protocol:
  apply: true
  file: agents_manager/SKILL.md (PHASE 3 sub-section)
  lines_added: ~30
  rationale: |
    Master's authority is preserved (final say).
    Planner's expertise is preserved (architectural seams).
    Re-ask loop keeps the conversation alive without infinite replanning.

C3_metrics_extension:
  apply: true
  file: tasks/README.md
  lines_added: ~25
  rationale: |
    Closes the loop with Patch-1 H1 by surfacing what was hidden.
    Owner gets a single metric per phase to spot future "Phase 4" cases.

# Optional companions — defer unless you actively feel their absence
D1_dispatch_gate: defer_to_v0.6      # hard-block dispatcher without complexity block
D2_overview_dashboard: defer_to_v0.6 # cross-task metric aggregation

# Verification after apply
post_apply:
  - run: grep -rn "Complexity" agents_manager/planning/
    expect: hits in both rules.md and SKILL.md
  - run: grep -n "Phase complexity re-ask" agents_manager/SKILL.md
    expect: hit
  - run: grep -n "Phase productivity" tasks/README.md
    expect: hit in the Completion block template
  - run: grep -n "LOC written" tasks/README.md
    expect: hit in the Phase timings table template
  - run: update CHANGELOG.md
    note: add v0.5.x+ entry referencing both Part 1 and Part 2 patches
```

---

# 8. About this file

- **Generator:** MiniMax-M3 via opencode CLI on Windows pwsh 7+
- **Project (consumer):** google_ai_studio_clone_1 (downstream consumer of `agents_manager v0.5.0`)
- **Generated:** 2026-06-29
- **Storage:** `agents_manager/upstream-contrib/PROPOSED_PATCH_v0.5.x_2026-06-29_part2_chunk-size.md` (this file)
- **Companion file:** `PROPOSED_PATCH_v0.5.x_2026-06-29.md` (Patch-1: WARN register, browser preflight, git-status check, finer fix-loop counter, smoke delegation, Phase 5 next-steps, WARN auto-accept)
- **Inputs read:** `share/notes/99_progress_T-2026-06-29-001.md`, the 5 review reports at `share/reports/04_review_*.md`, the 5 phase coder summaries at `share/notes/03_coder_summary_*.md`, the applied Patch-1 edits in `agents_manager/`.
- **Verification status (downstream fork):** Patch-1 has been applied end-to-end on a working fork of `agents_manager`. Patch-2 (this one) is in the file you are reading — not applied in fork yet.
- **License:** inherits the agents_manager license. Treat this as a contribution, not an obligation.

End of file.
