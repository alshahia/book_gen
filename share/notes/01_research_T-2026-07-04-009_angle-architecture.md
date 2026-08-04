# Research — T-2026-07-04-009 — angle B: Architectural fit

**Date:** 2026-07-04
**Trigger:** initial
**Sub-agent:** research
**Angle:** Architecture — where the new capability lives inside `agents_manager`.
**User task:** `share/handoffs/00_user_task_T-2026-07-04-009.md`
**Master tracker:** `tasks/T-2026-07-04-009.md`
**Sibling angles:** A (landscape) + C (operations) — not consulted here.

---

## Task in one sentence

Map two user sub-asks — **(A) extract a finished project into a reusable template** and **(B) extract the recurring "core knowledge" from a finished project into reusable agent guidance** — onto the existing `agents_manager` controller tree, and answer six architectural questions (placement map, pipeline integration, trigger surface, specialist ownership, backward compatibility, reuse map) with concrete paths and tradeoffs.

## What we know for sure

- The user asked for two different shapes of meta-tooling on the controller itself, not on a downstream project. Both sub-asks operate on the *output* of a completed Phase-3 build (`agents_manager/SKILL.md:91-99`) and emit something into the controller's own surfaces.
- The controller's existing surface areas where new content can land are:
  - `templates/<name>/` — 4 ship today (`_blank/`, `cinematic-landing/`, `dashboard/`, `docs-site/`); folder shape governed by `templates/AUTHORING.md:54-72`; contribution flow governed by `templates/CONTRIBUTING.md:10-34`.
  - `agents_manager/memory/{global,projects/<slug>}/` — three-scope canonical schema in `agents_manager/memory/README.md:27-60`.
  - Per-role `agents_manager/<role>/notes/{semantic,episodic}/` — same memory umbrella, role-scoped.
  - `share/templates/` — staging area (`cinematic-landing-fixes.md` + `_archive/`) used for pre-promotion content.
  - `share/notes/`, `share/reports/`, `share/handoffs/`, `share/messages/` — bus, not state-bearing.
- Pipeline is locked at 6 phases (0 Ingest, 1 Research, 2 Planning, 3 Build, 4 Review, 5 Next-steps opt-in) per `agents_manager/SKILL.md:91-99`. Phase 3 has a 3a sub-phase for assets (line 84). Phase 5 is opt-in (line 414).
- Specialist count is fixed at 5 (research, planning, design, coder, review) per `agents_manager/SKILL.md:274-276` "we always use the 5-agent roster; we don't dynamically add or remove specialists per task. This is by design."
- `am-assets` (6th specialist) was added in v0.9.0 as a strict-separation exception (asset manifest only); it does NOT write into `templates/` content (`opencode.jsonc:67` "CANNOT: edit templates/** (those are owned by the template author / owner)").
- Every specialist's SKILL.md contains a hard rule "No writing into templates. `templates/<name>/memory/` is the template author's lane" (`agents_manager/research/SKILL.md:57`, mirrored in `agents_manager/memory/README.md:116`).
- The existing recipe for adding a template is `cp -r _blank/ <name>/` + 9-step `AUTHORING.md §For authors` (`templates/AUTHORING.md:246-289`); wholly manual, no automation today.
- A precedent for "shell-out to a controller operation" already exists: `bin/agents-manager` + `bin/standalone-installer/install.{py,sh,cmd}` (described in `AGENTS.md` lines 47-49). These are stdlib-only scripts that operate outside the agent pipeline.

## What we don't know (ambiguities)

- **Whether the user wants this to ship *inside* this repo, or to ship as an external tool the user runs against any project.** Phrase "when used agents-manager in other projects" (`share/handoffs/00_user_task_T-2026-07-04-009.md:7`) is ambiguous between (a) capability available whenever agents_manager is installed in a project (so lives inside the repo, like `bin/agents-manager`), and (b) a one-off script the user invokes manually (so lives alongside `bin/standalone-installer/`).
  - **Suggested clarifying question:** "For the extract-to-template tool: should it ship as a sub-command of agents-manager (run from any cloned project via `bin/agents-manager extract template`), or as a standalone install path (analogous to `bin/standalone-installer/`) that the user downloads and runs against a project they're trying to extract?"
- **What "core/most needed part" actually means in scope.** The user gave examples ("recurring pitfalls, design decisions, conventions, knowledge") that span at least three of the existing memory scopes (`global`, `project/<slug>`, per-role `notes/semantic`). The right scope depends on whether the knowledge is meant for *the same project, redone later* (= project scope), *any agent in this repo family* (= global), or *only one specialist role on similar projects* (= per-role `semantic/`).
  - **Suggested clarifying question:** "For sub-ask B: when an agent picks up a 'similar project', what does 'similar' mean — same tech stack, same domain, same company, or something else? The answer changes whether extracted knowledge goes to `agents_manager/memory/global/`, `agents_manager/memory/projects/<slug>/`, or a per-role `notes/semantic/` entry."
- **Whether extraction should be deterministic or LLM-assisted.** Authoring a template by hand requires 9 steps (`templates/AUTHORING.md:248-285`); having an LLM read a project and propose a template bundle (decisions, MANIFEST, skeleton, prompts) is a very different capability. The current rulebook is written assuming a human author; an LLM-assisted path would need rule changes or a new "`LLM-ASSISTED`" subtype.
  - **Suggested clarifying question:** "When extracting to a template, do you want the tool to *generate* the template files (skeleton, memory, prompts, decisions) by analyzing the project, or to *scaffold an empty template folder + checklist* the user then fills in?"
- **Whether the new capability should be offered on *every* finished project or on opt-in only.** The current pipeline ends at Phase 4 PASS → Phase 5 opt-in menu; pushing extract there by default would be a surprise to users running single-shot tasks.
  - **Suggested clarifying question:** "Should the extract option appear automatically at Phase 5 close, or only when the user explicitly types `extract` after a task? (Default = opt-in, matches Phase 5's own opt-in pattern.)"

## Risks and doubts

- **R1 — Soft-wall erosion:** Every existing specialist's SKILL.md prohibits writing into `templates/<name>/memory/`. Adding an extract capability inside an existing specialist's lane (option A2 in § "Specialist ownership" below) requires loosening that rule with surgical exceptions ("am-research may write a NEW template folder but never modify an existing one"); risk of accidentally expanding the exception over time. **Severity: high.** Mitigation: prefer either a new specialist (cleanest), or a shell-out script that runs outside the agent pipeline (zero wall erosion).
- **R2 — Authoring-standard drift:** `templates/AUTHORING.md` is at version 1.0.0 with explicit rule numbering 1-8 (`templates/AUTHORING.md:29-50`). An extract tool that emits template content which violates any of these 8 rules creates a template that the maintainer's checklist will reject. The tool needs to enforce the same rules the human does, by construction. **Severity: high.** Mitigation: reuse the rules as test assertions, not as documentation; treat `tests/verify.sh` as the tool's compliance oracle.
- **R3 — Memory cross-contamination:** `agents_manager/memory/README.md:120` states "`scope: project` entries are bound to one project; cross-applying is a contamination risk." If sub-ask B writes "core knowledge" into `agents_manager/memory/projects/<slug>/` with the intent that other agents read it on similar projects, that's exactly the contamination the protocol forbids. The right destination is almost certainly `agents_manager/memory/global/`, but that scope has its own pitfall — global entries accumulate cross-repo cruft if the tool is run aggressively. **Severity: high.** Mitigation: require user-confirmed scoping question before each write; never auto-default to global.
- **R4 — Pipeline-shape surprise:** Phase 5 already exists as opt-in (`agents_manager/SKILL.md:414`). Adding a Phase 5d "extract" sub-option is a low-risk additive change. Adding a new Phase 6 (or re-skinning Phase 3 as "Build + Extract") is a surprise and would break existing task trackers. **Severity: medium.** Mitigation: keep extract OUT of the pipeline; treat as a parallel capability invoked explicitly or as a follow-up chunk.
- **R5 — Async-extraction orphan tasks:** If a user asks for extract at Phase 5 close and the system spawns a heavy extraction (multiple files, LLM-assisted), then walks away, the spawned task sits in `tasks/<id>.md` without a clean lifecycle. The protocol has no cleanup story for "task closed and then a follow-up spawned later" beyond new task ids. **Severity: medium.** Mitigation: a phase-5d extract that emits a new task id `T-<date>-010-extract` is fine, but the master must mark it as the post-close follow-up, not as a continuation of the prior task.
- **R6 — IP / license bleed:** Templates ship into other projects. If extraction blindly copies code, assets, LICENSE files, brand marks, or third-party assets from the source project into a new template, downstream users inherit the source's license + branding. This is invisible to a deterministic scraper; an LLM-assisted extract is even more likely to leak identifying references into skeleton comments. **Severity: medium.** Mitigation: extract tool must respect `LICENSE` / `NOTICE` / `PRIVACY.md` as first-class filters, not afterthoughts; explicitly strip project-specific brand tokens from skeleton before publish.
- **R7 — Reusing `share/templates/` is a layout question, not a placement solution.** `share/templates/` currently holds one staging file (`cinematic-landing-fixes.md`) and an `_archive/` (`E:\context_gen\share\templates\`). It is not a versioned controller surface; treating it as the "extracted templates live here" home would collide with the staging convention. **Severity: low.** Mitigation: don't repurpose; put extracted drafts through the same `share/templates/` staging path the manual workflow already uses, then promote to `templates/` per `templates/CONTRIBUTING.md:33-34`.

## Technical findings

- The templates folder is a **manually authored** asset tree governed by `templates/AUTHORING.md:11-20` ("A template is a reusable scaffold an agent clones to produce a complete artifact"). There is no programmatic template-construction script in the repo today.
- Folder shape is locked at `templates/AUTHORING.md:56-72`: `00-readme-first.md`, `INDEX.md`, `decision-log.md`, `memory/NN-<topic>-<role>.md`, `skeleton/`, `prompts/`, `assets/MANIFEST.txt` + `manifest.schema.json`, `tests/verify.sh`. An extract tool's output must conform.
- `_blank/` is a starter, not a slot template (`templates/_blank/README.md:1-15`): "Copy this folder to start a new template." Authored for human hand-copy. An extract tool could either (a) reuse `_blank/` as its initial state and mutate, or (b) produce its own scratch folder and let the user copy from `_blank/` after. (a) couples the tool to `_blank/`, which is currently decoupled.
- The memory protocol explicitly fences `templates/<name>/memory/` from the controller memory tree (`agents_manager/memory/README.md:116`). The fence is enforced by *every* specialist's SKILL.md hard rule (e.g. `agents_manager/research/SKILL.md:57`).
- `am-assets` is the only specialist that touches a template's contents today, and even then only by writing `MANIFEST.json` for an existing template (`agents_manager/assets/SKILL.md:60-61`, `opencode.jsonc:67`). It is forbidden from editing any other template file.
- `share/templates/` is used as a **promotion staging area** for the authoring standard (`share/templates/cinematic-landing-fixes.md` is the 9-item fix list `templates/cinematic-landing/` still owes; `share/templates/_archive/AUTHORING.md.pre-promotion` is the pre-promotion snapshot of `templates/AUTHORING.md`). Using this path for extract output is consistent with existing convention.
- `scripts/backfill-research-metrics.sh` is the canonical pattern for an idempotent, stdlib-only, append-only controller tool that operates on `share/notes/01_research_*.md` (`scripts/backfill-research-metrics.sh:1-13`). The same shell idiom (glob + per-file check + append with a marker) would translate directly to an extract script that scans a project and emits template/memory content.
- `bin/agents-manager` + `bin/standalone-installer/install.{py,sh,cmd}` are the canonical pattern for "user-installed tools that operate across projects" (`AGENTS.md:47-49`). They ship a CLI surface (`--global/--local/--both/--skip`) separate from the agent pipeline.
- The controller's spec for specialist count is explicit: "we always use the 5-agent roster; we don't dynamically add or remove specialists per task. This is by design" (`agents_manager/SKILL.md:274-276`). Adding a 7th specialist (`am-template`) is therefore a notable exception and would need a written rationale.

## Placement map — sub-ask A (project → template)

### Candidate A-1 — `templates/<new-name>/` (direct write into the canonical tree)

- **Path:** `templates/<new-name>/` populated against the rulebook in `templates/AUTHORING.md:54-72`.
- **Pros:** Single source of truth. The new template becomes discoverable by `am-planning`/`am-assets` the moment Phase 2 begins on the next downstream project (per `agents_manager/SKILL.md:80`). The 9-step manual recipe (`templates/AUTHORING.md:248-285`) is the same shape a tool would emit. Users discover it the same way they discover hand-authored ones.
- **Cons:** Requires loosening the hard rule "no writing into `templates/<name>/memory/`" (currently in every specialist SKILL and in `agents_manager/memory/README.md:116`). Bypasses the author-review gate (`templates/CONTRIBUTING.md:33-34` PR-per-template contract). Creates immediate need for `scripts/validate-template.sh` (doesn't exist today) to enforce rules 1-8 of `templates/AUTHORING.md` against emitted content.
- **Fits-with-existing-rules:** **conditional.** Only fits if the writing agent's SKILL.md is amended to permit it, OR if the writing happens via a non-agent shell script that doesn't carry an SKILL. Probable workable form: tool runs OUTSIDE the agent pipeline (analogue of `bin/standalone-installer/`); in-pipeline writes remain forbidden.

### Candidate A-2 — `share/templates/drafts/<new-name>/` (staging area, then promote)

- **Path:** Drop into `share/templates/drafts/<new-name>/` first; promote to `templates/<new-name>/` only after a review pass.
- **Pros:** Reuses the existing `share/templates/` convention (`share/templates/cinematic-landing-fixes.md`, `share/templates/_archive/`). Avoids touching the "no write into templates" rule during the heavy lift. Lets a human (or am-review) validate against `templates/AUTHORING.md` rules 1-8 before promotion. Mirrors the way `templates/AUTHORING.md` itself staged at `share/templates/AUTHORING.md.pre-promotion` before promotion.
- **Cons:** Adds one promotion hop to the workflow (more latency, more state to track). Doesn't solve the authorship-validation problem (same rules apply, just deferred).
- **Fits-with-existing-rules:** **yes.** Consistent with the staged-promotion precedent in `share/templates/_archive/` and `share/templates/cinematic-landing-fixes.md`.

### Candidate A-3 — Outside the repo entirely (in the *consumer* project's tree as a `.agents/templates/<name>/`)

- **Path:** Extract output lives at `<consumer-project>/.agents/templates/<new-name>/`, sibling to the consumer's own `agents_manager/` clone.
- **Pros:** Doesn't touch the controller repo at all — no rule conflict, no schema version drift. Each consumer project gets its own namespace. Avoids the licensing cross-pollination risk (R6) because the template never enters a shared repo.
- **Cons:** Templates can't be discovered by other projects using `am-planning` unless they explicitly `git clone` or copy. Doesn't match the existing "templates ship in the controller and are centrally versioned" model (`agents_manager/SKILL.md:68-84`). Massively reduces reusability — defeats the point of sub-ask A for users who run agents_manager across many projects.
- **Fits-with-existing-rules:** **no.** Contradicts `agents_manager/SKILL.md:80-84` ("New templates can be added by writing the 9 memory files + skeleton + prompts into `templates/<new-name>/`"). Only viable as a degraded mode.

## Placement map — sub-ask B (project → core knowledge / agent guidance)

### Candidate B-1 — `agents_manager/memory/global/<topic>.md`

- **Path:** One or more topically-scoped entries under the global scope (`agents_manager/memory/global/` is currently empty except for `.gitkeep` per `E:\context_gen\agents_manager\memory\global`).
- **Pros:** Existing cross-project destination; explicitly designed for "facts that apply across projects" (`agents_manager/memory/README.md:19-22` reads "Cross-project facts; first source on re-entry"). Schema is already documented (`agents_manager/memory/README.md:27-60`). Validated by `scripts/validate-memory.sh` (per line 126). Read automatically by every specialist on re-entry (`agents_manager/memory/README.md:75-79`). Perfect mechanism for "tips agents need on similar projects."
- **Cons:** Cross-project scope is also its hazard: a hasty extract clutters global with project-specific noise that other projects can't filter out (`agents_manager/memory/README.md:83` caps reads at 200 lines/scope; pollution eats the budget). Current memory protocol forbids "private URLs" / secrets in entries (line 110); easy to leak accidentally. Requires user-confirmation per entry because wrong-scope writes silently degrade the system.
- **Fits-with-existing-rules:** **conditional, with gating.** Writing is permitted (master is the global-scope owner per `agents_manager/memory/README.md:19-22`); tool must require user to confirm scope choice per entry, never auto-default to global.

### Candidate B-2 — `agents_manager/memory/projects/<slug>/<topic>.md`

- **Path:** Per-project memory under the active slug.
- **Pros:** Schema-conformant; validated by `scripts/validate-memory.sh`; existing protocol covers it.
- **Cons:** Explicitly forbidden for cross-project use by `agents_manager/memory/README.md:120`: "`scope: project` entries are bound to one project; cross-applying is a contamination risk." This is the wrong scope for "guidance for similar projects" *unless* the user actually means "the same project re-done later" (which the user's phrasing "similar projects" rules out).
- **Fits-with-existing-rules:** **no, for cross-project intent.** Use only if the user re-scopes sub-ask B to mean "resume guidance for THIS project."

### Candidate B-3 — Per-role `agents_manager/<role>/notes/semantic/<topic>.md`

- **Path:** Curated insights per specialist role.
- **Pros:** Right scope IF the extracted knowledge is purely "design expertise" or "planning patterns" or "coder conventions." Fits existing protocol (every specialist reads its semantic tree on re-entry per `agents_manager/memory/README.md:78`).
- **Cons:** Discriminator problem — "core knowledge" is usually *not* role-specific. A "we shipped a cinematic site and learned: cutout depth of 30px avoids eye-tracking friction" insight could go to design semantic OR planning semantic OR global, and the schema offers no tiebreaker. Risk: noise piles up in every role's semantic folder for every project, defeating the curated-curation purpose.
- **Fits-with-existing-rules:** **conditional.** Fits only for insights clearly tied to one role; questionable for the general "core knowledge" framing.

### Candidate B-4 — Brand-new tree: `agents_manager/playbooks/<slug>/` (or similar)

- **Path:** A new sibling tree to `agents_manager/memory/`, named distinctly (e.g., `agents_manager/playbooks/` or `agents_manager/knowledge/`).
- **Pros:** Clean separation from the schema-bound three-scope memory system. Avoids the cross-contamination risk (R3). Can evolve its own schema (provenance, comparable-project tags, freshness score).
- **Cons:** Introduces a fourth scope that every specialist would need to learn on re-entry — adds cognitive load; contradicts the canonical "three scopes" claim in `agents_manager/memory/README.md:14-15` ("The agents_manager memory system has three scopes"). Adds a new folder, requires validating scripts to extend, requires reading-order amendment in every specialist SKILL.
- **Fits-with-existing-rules:** **no, without a deliberate schema-level decision.** Only viable if the existing three-scope model is judged inadequate for the new content type, and the user explicitly approves the model expansion.

### Candidate B-5 — Reuse the template tree: drop the "core knowledge" as a `templates/_core-playbook_/` template

- **Path:** Treat "core knowledge" as a *meta-template* — a `templates/_core/` package whose `memory/` directory contains the extracted guidance, and whose `skeleton/` is an empty placeholder. Other templates would `references` it.
- **Pros:** Reuses existing authoring flow. Plays nicely with the per-role memory-format conventions in `templates/<name>/memory/`. Avoids inventing a new tree. Allows the "core" to evolve at the same cadence as templates.
- **Cons:** Conflates two concepts — "template" (a scaffold for *building a project*) and "playbook" (guidance for *thinking about a domain*). The two have different versioning concerns: a template ships with a project; a playbook evolves across projects. The consumer-discovery paths differ (`am-planning` greps for templates; nothing currently greps for playbooks).
- **Fits-with-existing-rules:** **no, semantically.** Conceptually wrong fit; only worth it if the user explicitly endorses the conflation.

## Pipeline integration — where the new capability fits

| Option | What | Tradeoffs |
|---|---|---|
| **(i) Explicit Phase 5d "Extract"** | Add a sub-option under Phase 5b menu: "Extract to template" + "Extract to knowledge." Fires at task close per opt-in pattern. | **Pro:** Lowest blast radius (matches existing 5b menu model, `agents_manager/SKILL.md:406-412`). **Pro:** Stays opt-in. **Con:** Requires a new sub-option in master's Phase 5 dispatch code; small but real master SKILL diff. **Con:** Per-project, not cross-project — user has to remember to do it every time. **Verdict:** Good fit for the *user-per-project* extraction path. Not enough alone for "guidance across similar projects." |
| **(ii) Skill / subcommand invoked by master ad-hoc** | Add a new master command — `bin/agents-manager extract template <project>` and `bin/agents-manager extract core <project>` — standing alongside `bin/standalone-installer/`. Master can dispatch it at Phase 5 close, or the user can run it directly. | **Pro:** Matches the existing controller-dispatcher precedent (`AGENTS.md:47-49`, `bin/agents-manager.{ps1,py}`). **Pro:** Operates *outside* the agent pipeline — no soft-wall erosion. **Pro:** Same command works against any project, in or out of this repo. **Pro:** New surface area can grow without touching `agents_manager/SKILL.md`. **Con:** Requires user (or master) to invoke it explicitly; no automatic discoverability. **Verdict:** Best fit for both sub-asks. Sub-ask A and B can share the script infrastructure; flags/args diverge them. |
| **(iii) An am-research or am-design responsibility at task close** | Add a "research-extract" or "design-extract" mode to existing specialists, dispatched automatically by master before Phase 5. | **Pro:** Fits the existing 6-specialist roster (no roster change). **Con:** Forces a soft-wall exception into am-research and/or am-design SKILL.md (R1 in § Risks). **Con:** am-research is forbidden from "writing into templates"; lifting the rule for one tool blurs the boundary. **Con:** Triggers *automatic* writes without confirmation — high user-surprise risk (R3, R4). **Verdict:** Reject unless user explicitly insists on a roster-locked solution. |
| **(iv) A separate specialist (`am-extract` / `am-template`)** | Add a 7th specialist whose lane is precisely "read a project, write a template or memory entry." | **Pro:** Cleanest ownership; no boundary erosion. **Pro:** Specialist can hold the soft rules in its OWN SKILL.md, sidestepping the "no writing into templates" fence (its SKILL can grant itself the right). **Con:** Violates the locked 5-roster design (`agents_manager/SKILL.md:274-276`) — needs a written rationale. **Con:** Two more artifacts to maintain: `agents_manager/extract/SKILL.md`, `agents_manager/extract/rules.md`, plus `opencode.jsonc` entry. **Con:** Specialists are dispatched via `task()` in the master pipeline; this specialist would also need ad-hoc invocation from the user, which isn't a current pattern. **Verdict:** Cleanest separation, highest cost. Justified only if the capability grows into a substantial recurring surface. |

**Recommendation by angle:** **Option (ii)** is the dominant choice. It is the only option that (a) avoids soft-wall erosion, (b) matches an existing precedent in the repo, (c) handles both sub-asks with shared infrastructure, and (d) is usable from either master (programmatic) or the user (manual). Options (i) and (ii) can coexist — (i) gives a Phase-5 menu entry that *invokes* the (ii) script. Option (iv) is overkill for v1.

## Trigger surface — when is the capability offered

- **(T1) Only on explicit user request.** User types `extract` (or runs the script directly). Defaults to all other cases. **Pros:** Zero surprise; lowest blast radius. **Cons:** Most users won't remember it exists. **Verdict:** Required floor; not the only trigger.
- **(T2) Auto-suggested at Phase 5 close based on heuristics.** Master polls the closed project's metadata — number of files, presence of `tests/verify.sh`, presence of `INDEX.md`, ≥3 phases completed — and surfaces the suggest text: "extract this to a template?" **Pros:** Recovers the "users won't remember" gap. Easy opt-out (just say no). **Cons:** Surfaces every time, even for throwaway tasks (R4). **Verdict:** Good if heuristics are conservative.
- **(T3) Auto-run at Phase 5 close (configurable).** Gated on the same heuristics as T2 but executes automatically and emits a draft to `share/templates/drafts/` for human review. **Pros:** No user friction. **Cons:** High blast radius (R6, R3). **Con:** Defeats the "core knowledge" ask — silently bulk-fills `agents_manager/memory/global/` with whatever the agent can mine from any project. **Verdict:** Reject without a written opt-in per project.
- **Recommendation:** T1 (always) + T2 (Phase 5 menu entry, gated on `tasks/<id>.md` showing ≥3 phases + `share/notes/03_coder_summary_*.md` existing). Defer T3 until v0.15+ after user feedback on T2.

## Specialist ownership — who owns each capability

The current boundary is a clean prohibition: every specialist SKILL.md + master SKILL.md says "no writing into `templates/<name>/memory/`" (audit: `agents_manager/SKILL.md` boundary sections, `agents_manager/research/SKILL.md:57`, mirrored across planning/design/coder/review/assets). The closest existing precedents for touching template content are:

- **`am-assets`** owns `assets/MANIFEST.json` writes for an existing template (`opencode.jsonc:67`) — narrow lane, writes one file, never edits skeleton/memory/prompts. Could be a model for "narrow-lane-permit" but the precedent is asset-scoped, not template-scoped.
- **Master** owns `agents_manager/SKILL.md` itself and `share/notes/99_decisions.md` (`opencode.jsonc:23`). Master can edit any `agents_manager/SKILL.md`. This is a precedent for "the orchestrator is the only one allowed to write into the controller's own surface," but templating is structurally different from SKILL maintenance.

**Ownership analysis for each candidate:**

| Owner | Sub-ask A | Sub-ask B | Pros | Cons |
|---|---|---|---|---|
| **master (in-pipeline)** | Yes if Phase 5d menu invokes it | Yes if Phase 5d menu invokes it | Reuses existing orchestration | Master becomes script-launcher; blurs the "orchestrator doesn't work, specialists work" boundary |
| **am-research** | No (soft-wall forbids templates) | Maybe (global memory is master-owned) | Cross-project brain already its focus | Soft-wall R1 |
| **am-planning** | No (soft-wall forbids templates) | No | n/a | Out of role |
| **am-design** | Conditionally (own scaffold area) | No | Design literacy | Strict-separation rule: design never writes `src/**`; analogously, never writes `templates/**`. Already at the edge of what it owns (`agents_manager/SKILL.md:84` `## Templates`). |
| **am-coder** | No (writes code, not scaffolds) | Maybe | Can write controller-side code (e.g., the extract script) | Not the right semantic owner |
| **am-review** | No (read-only by policy) | No (read-only) | n/a | n/a |
| **new specialist `am-template` / `am-extract`** | Yes | Yes | Clean lane | Violates 5-agent roster design (`agents_manager/SKILL.md:274-276`); needs user-rationale; two new artifacts |
| **user-only (no specialist)** | Via `bin/agents-manager extract template` | Via `bin/agents-manager extract core` | Zero soft-wall touches; matches `bin/standalone-installer/` precedent | Master can't dispatch it; no Phase 5 menu integration unless master's `bin/` invocation capability grows |

**Recommendation:** **Sub-ask A** ownership — **shell-out script under `bin/`** (the `bin/agents-manager-extract-template.{py,sh,cmd}` analogue of `bin/standalone-installer/`). Master invokes it from the Phase 5 menu (option (i)+(ii) combo); user can also invoke it directly.

**Recommendation for sub-ask B** — **also shell-out**, but reads/writes run **through master** as the canonical global-memory writer (`agents_manager/memory/README.md:19-22` says global is master-owned). Master can pre-fill the entries, then surface them to the user for confirmation before commit; this keeps the secret-safety and contamination controls intact.

## Backward compatibility — what this would break

- **`templates/AUTHORING.md` rulebook** would not break at v1.0.0 rules; the extract tool needs to *emit content that satisfies* rules 1-8 (`templates/AUTHORING.md:29-50`). However, adding a "how to extract" section IS a v1.x minor bump per the Versioning section (`templates/AUTHORING.md:325-330`). **Mitigation:** add `templates/EXTRACTION.md` as a sibling document (analogous to `templates/CONTRIBUTING.md`); keep `AUTHORING.md` unchanged.
- **`templates/CONTRIBUTING.md`** § "I want to add a new template" (`templates/CONTRIBUTING.md:10-34`) currently says the only entry point is `cp -r _blank/`. Extending it with a "via extract" path is additive and non-breaking. **Mitigation:** add a `### I want to extract a finished project into a template` subsection that points at the new script.
- **`templates/_blank/`** starter contract (`templates/_blank/README.md:1-15`) is untouched by this work — the extract tool writes into a fresh `<new-name>/`, not into `_blank/`. **Mitigation:** none needed; document the contract.
- **`agents_manager/memory/README.md`** three-scope claim (`agents_manager/memory/README.md:14-15`) could be strained if the extract tool writes frequently to `global`; it does not introduce a new scope. **Mitigation:** add a § "Write rate from automated extraction" subsection noting that auto-emitted global entries must include a `source:` field that points at the originating task id and include a `last_verified:` timestamp ≤ today.
- **Per-specialist SKILL.md "no writing into templates" hard rule** — the clean path (shell-out script) avoids triggering this; the unfortunate path (extract mode inside an existing specialist) requires amending SKILL.md. **Mitigation:** prefer the shell-out path; if a future design demands in-pipeline extraction, amend the rule with a precise exception ("the extract tool may write into a fresh `templates/<new-name>/` but never modify an existing `<existing-name>/`").
- **`scripts/validate-frontmatter.py` / `scripts/validate-memory.sh`** — both are manual (per `AGENTS.md:55-67`, "no tests for `bin/` scripts"). Adding an extract script doesn't touch these; the extract script should *invoke* them on its own output as a self-check.
- **`share/templates/cinematic-landing-fixes.md`** — unrelated; only mentioned because the same `share/templates/` directory is the natural home for extract drafts.

## Reuse map — what the new capability should leverage, not reinvent

- **`templates/_blank/`** (`templates/_blank/`) — use as the initial state of any extracted template (`cp -r _blank/ <draft>/`, then fill). The tool should treat the blank folder as the canonical "before" snapshot, just as a human author would.
- **`templates/AUTHORING.md`** (`templates/AUTHORING.md:1-333`) — the rulebook. The extract tool's compliance oracle. After populating a draft, the tool runs `tests/verify.sh` to enforce Rule 4 (`templates/AUTHORING.md:39-41`); a non-zero exit means the draft didn't satisfy rules 1-8.
- **`templates/CONTRIBUTING.md`** (`templates/CONTRIBUTING.md:1-101`) — surface the extract tool here as an alternate path; mirror the 9-step checklist (`templates/CONTRIBUTING.md:13-32`) as the tool's exit gate.
- **`agents_manager/memory/README.md`** (`agents_manager/memory/README.md:27-60`) — schema for sub-ask B output. Each emitted entry must have the canonical frontmatter and ≤20-line body (line 106). The tool must invoke `scripts/validate-memory.sh` on output.
- **`scripts/backfill-research-metrics.sh`** (`scripts/backfill-research-metrics.sh:1-87`) — exemplary pattern for "idempotent, stdlib-only, append-only controller tool." Read for the structural model before writing `bin/agents-manager-extract-*.py`:
  - Glob over the known input pattern (line 51).
  - Skip files that already match the output marker (line 53-55).
  - Append with a trailing marker line including a date (line 70-73).
  - Exit 0 if no work, 1 if work done (lines 78-83).
  - All in POSIX bash + grep + awk; no external deps.
- **`agents_manager/SKILL.md` Programmatic-gates pattern** (`agents_manager/SKILL.md:204-214`) — the extract tool's output should produce files that pass these gates. Specifically, the canonical 8-section am-research output template (`agents_manager/research/SKILL.md:87-129`) requires a `## Metrics` block with 5 integer fields (lines 264-273); the extract tool's emitted notes (e.g., draft template's `INDEX.md` summary) should also be machine-checkable.
- **`share/templates/`** (`share/templates/`) — staging area per existing convention; the tool writes drafts here, then a human (or am-review) promotes them to `templates/<name>/`.
- **`bin/agents-manager` + `bin/standalone-installer/`** (`AGENTS.md:47-49`) — direct precedent for "controller-side tool that operates on the user's projects." Match their install surface and stdlib-only discipline.
- **`opencode.jsonc`** (line 1-71) — only relevant if the team ends up adding a 7th specialist; shell-out path doesn't touch it.
- **Existing exemplar `templates/cinematic-landing/`** (`templates/cinematic-landing/INDEX.md`) — a concrete worked example of a complete template. The extract tool's smoke test could compare its emitted skeleton against this exemplar's shape to catch structural malformations.

## Cross-role perspectives

### From am-planning

**Pipeline integration, chunking, dispatch, triggers — primary voice for this angle.**

Sub-ask A is fundamentally a planning-shaped problem masquerading as an authoring one. Even if the extraction script itself runs in one shot, the *decisions* embedded in a successful extract (which skeleton's sections to keep, which memory files to write, which hard rules to encode, what the trade-log should say) are exactly the multi-step planning work that am-planning normally handles.

**Chunking:** If the capability ships as a Phase 5 menu item + shell-out script, the natural chunking is:

1. Phase 2-friendly: master pre-asks the user 1-3 scoping questions (target domain, level of fidelity, scope of memory extraction) when the extract menu is selected. Mirror the 7-question discovery pattern in `agents_manager/design/SKILL.md:80-90`.
2. Phase 3-shape: a single decision-body chunk that runs the script, validates output, surfaces drafts. Bounded at one chunk because the tool itself is deterministic.
3. Phase 4-shape: an am-review pass that runs `templates/<draft>/tests/verify.sh` and `scripts/validate-memory.sh` against the extracted content. Standard per-`tests/verify.sh` exit-code check.

**Dispatch:** For sub-ask A, master dispatches: (a) scoping question via pause-and-ask hook (`agents_manager/SKILL.md:228-238`); (b) runs the script inline (master has `bash` per `opencode.jsonc:23`); (c) optional am-review against the draft. No new specialist needed.

For sub-ask B, the dispatch is lighter: master prompts the user for per-entry scope confirmation, writes the entries via master itself (master is the global-memory owner per `agents_manager/memory/README.md:19-22`), then invokes `scripts/validate-memory.sh`. No new dispatch chain.

**Triggers:** A phase-5d menu entry that requires explicit user opt-in matches `agents_manager/SKILL.md:228-238` "pause-and-ask hook" semantics perfectly — the user has to *choose* the menu option, so no surprise.

### From am-research

**Inputs needed from research outputs; outputs research needs.**

Sub-ask A (template extraction) — research is a *consumer* of the resulting template more than a producer:
- **Input needed:** Nothing research-specific. The extract tool reads project files (skeleton, assets, conventions) directly; it does not need prior research notes.
- **Output to research:** The new template, when promoted, becomes a discoverable input for `am-research` on the next task via `am-planning`'s template-eligibility check (per `agents_manager/SKILL.md:80`). So research benefits indirectly — a future research call can read `templates/<new-name>/memory/01-*.md` and apply its findings.

Sub-ask B (core knowledge extraction) — research is a primary writer candidate:
- **Input from research outputs:** Prior `share/notes/01_research_<task-id>.md` files, especially the "what we know for sure" + "risks" sections, are the natural source of "recurring pitfalls" and "design decisions." The extract tool should *grep* the project's prior research notes, not invent knowledge from scratch.
- **Output to research:** The new memory entry becomes part of `agents_manager/memory/global/` (or the chosen scope). Research reads these on re-entry per `agents_manager/memory/README.md:75-79`. So the feedback loop is: research writes project findings → extract tool harvests them → future research reads them on a new but similar project.

**Concrete handoff:** the extract tool should require the user to point at one or more prior task ids (`T-YYYY-MM-DD-NNN`) whose `share/notes/01_research_*.md` + `share/notes/03_coder_summary_*.md` it'll mine. This makes the provenance auditable and avoids the LLM-hallucinated-pitfall risk.

### From am-design

**Agent-facing surface (CLI flag? skill? phase option? UX?).**

Three candidate surfaces exist in the codebase; each has a fit:

| Surface | Example | Fit for extract |
|---|---|---|
| CLI subcommand (`bin/agents-manager extract …`) | `bin/agents-manager` precedent | **Best fit.** Mirrors `bin/agents-manager` and `bin/standalone-installer/`; works outside OpenCode; user can invoke anytime. |
| Phase menu (`Phase 5b` opt-in) | `agents_manager/SKILL.md:406-412` | **Good fit for the within-pipeline path.** Master invokes the CLI subcommand on the user's behalf when they pick the menu option. |
| `task()` subagent dispatch | `opencode.jsonc:22-67` specialists | **Reject for v1.** Forces a specialist that we don't need; runs only inside OpenCode sessions. |
| Master SKILL menu (skill tool) | `brainstorming`, `gstack-*` user-installed skills | **Mis-fit.** Skills are general-purpose, not project-specific tools. |

**Recommended UX flow:**

1. User closes a task. Phase 5 menu shows: "1. Run smoke test / 2. Polish WARNs / 3. Build a follow-up / 4. Close out / **5. Extract to template** / **6. Extract to knowledge**."
2. Picking 5 or 6 triggers a pause-and-ask (`agents_manager/SKILL.md:228-238`) with 1-3 scoping questions (target template name / domain, source paths, desired scope for memory).
3. Master runs `bin/agents-manager-extract-{template,core}.py` with the answers as `--arg=value` flags.
4. Tool writes drafts to `share/templates/drafts/<name>/` (sub-ask A) or `agents_manager/memory/global/*.md` after user confirms per-entry (sub-ask B).
5. Master surfaces the draft paths and asks: "promote? yes / discard / defer."

**Why CLI is right:** `bin/agents-manager` already exposes a controller CLI; an `extract` subcommand slots in without any change to `opencode.jsonc`. The user can also run it manually from a sibling project, matching their literal phrasing "when used agents-manager in other projects" (`share/handoffs/00_user_task_T-2026-07-04-009.md:7`).

## Self-critique

- **Did I do my job?** Partial. The note answers the 6 questions master asked, but I did not run `bash scripts/validate-frontmatter.py` against the proposed paths (the paths I propose don't exist yet, so validation would not change answers). I did not produce a sketch of the recommended `bin/agents-manager-extract-template.py` shape — that's planning's lane, not mine.
- **What might I have missed?**
  - I didn't fully audit the per-specialist SKILL.md for ownership of `agents_manager/memory/global/` entries. I asserted master owns global based on `agents_manager/memory/README.md:19-22`, but I did not grep every role's SKILL for "global memory" mentions that might contradict. **Blind spot — open and verify before am-planning acts on the recommendation.**
  - I did not check `CHANGELOG.md` (haven't read it this turn). A new capability past v0.14.1 may have a per-version bump convention I am not respecting. **Blind spot.**
  - The reuse map mentions `templates/cinematic-landing/` as a smoke-test exemplar but I haven't compared its `tests/verify.sh` shape to other templates — they may differ in ways that affect the tool's compliance oracle. **Blind spot.**
  - I haven't read `share/notes/01_research_T-2026-07-04-004.md` (previous task) — that note may already contain partial analysis of "extract to template" from a prior task. **Blind spot.**
  - The note does not address the user's explicit ask "get all opinion so its biased to certain specialization/role" (`share/handoffs/00_user_task_T-2026-07-04-009.md:8`). I have only *my* perspective here; the master synthesis (P1M) is where the 5-role bias-check must happen. The `## Cross-role perspectives` section is my best read of each role's likely position based on their SKILL, not their *actual* position. **Known limitation.**
- **What did I assume without evidence?**
  - I assumed sub-ask A and B are independent enough to ship as two CLI subcommands sharing infra, rather than as a single mode. The user might want a single `extract` with mode flags (`--template` / `--core`). Worth re-asking in clarification.
  - I assumed the "core knowledge" is meant to live in `agents_manager/memory/global/` because that's the only scope that supports cross-project reuse. The user might have meant something more like a per-role `notes/semantic/` enhancement or even a wholly new tree. The clarifying question on "similar" is load-bearing.
  - I assumed the 5-roster design (`agents_manager/SKILL.md:274-276`) is hard enough that a 7th specialist needs user approval. The lock-in phrasing is strong ("This is by design"), but the contradiction between v0.9.0's actual 6th specialist (`am-assets`) and the prose roster claim suggests the design has already drifted once. A future v0.15+ drift for an `am-extract` is not impossible.

## Feasibility verdict

- **Can do:** yes
- **Confidence:** MEDIUM
- **Why:** Both sub-asks have at least one placement option (sub-ask A → `bin/` CLI + `share/templates/drafts/`; sub-ask B → `bin/` CLI + `agents_manager/memory/global/` after user confirmation) that fits all six architectural questions without violating the locked rules. Confidence is MEDIUM (not HIGH) because I have not verified that the proposed `bin/` shape is technically feasible against the existing `bin/agents-manager` script's runtime model (the precedent exists but the extract use case is heavier than `install`); and one placement decision for sub-ask B is load-bearing on a clarifying question I have not yet resolved with the user.

## Recommendations for the planning agent (will not pre-decide placement)

- Surface the 4 clarifying questions in § "What we don't know" to the user before planning. Sub-ask A's "ship-in-repo vs ship-as-tool" question and sub-ask B's "what does similar mean" question are both answers that change the plan materially.
- Default recommendation framework (master can adopt or override):
  - Sub-ask A: shell-out under `bin/`, drafts in `share/templates/drafts/`, promote via existing contributing flow. No specialist change. `opencode.jsonc` untouched.
  - Sub-ask B: shell-out under `bin/`, writes gated on user-confirmed scope choice per entry (default = `agents_manager/memory/global/` only after explicit approval). No specialist change. `opencode.jsonc` untouched.
- If the user insists on a 7th specialist, require an explicit design rationale amendment to `agents_manager/SKILL.md:274-276`.
- Add `## Cross-cutting finding` to master's eventual synthesis: the extract tool's output must invoke `scripts/validate-memory.sh` and `tests/verify.sh` to be self-checking, matching the existing tool discipline (`AGENTS.md:55-67`).
- Phase-5 menu change is the only SKILL.md-level touch required if the team adopts option (i)+(ii). Smallest possible controller diff.

## Open questions for the user

1. **Sub-ask A — ship location:** "For the extract-to-template tool: should it ship as a sub-command of agents-manager (run from any cloned project via `bin/agents-manager extract template`), or as a standalone install path analogous to `bin/standalone-installer/`?"
2. **Sub-ask B — 'similar projects' scope:** "For sub-ask B: when an agent picks up a 'similar project', what does 'similar' mean — same tech stack, same domain, same company, or something else? The answer changes whether extracted knowledge goes to `agents_manager/memory/global/`, `agents_manager/memory/projects/<slug>/`, or a per-role `notes/semantic/` entry."
3. **Generation mode:** "When extracting to a template, do you want the tool to *generate* the template files (skeleton, memory, prompts, decisions) by analyzing the project, or to *scaffold an empty template folder + checklist* the user then fills in?"
4. **Trigger posture:** "Should the extract option appear automatically at Phase 5 close, or only when the user explicitly types `extract` after a task? (Default = opt-in, matches Phase 5's own opt-in pattern.)"
5. **(Lower priority)** Should the extract tool emit an audit document recording what it harvested and from where, so the user can audit before any write commits?
  - **Suggested clarifying question:** "Should every extract run emit a `share/notes/03_extracted_<task-id>.md` log documenting the source project paths read, the scope chosen for each emitted file, and the draft location — so the user has a single audit trail?"

---

## Metrics

- findings: 9
- risks_HIGH: 3
- risks_MEDIUM: 3
- risks_LOW: 1
- clarifying_Qs: 5
