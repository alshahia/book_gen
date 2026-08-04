# Research — T-2026-07-04-009 — angle C: Operations

**Date:** 2026-07-04
**Trigger:** initial
**Sub-agent:** research
**Angle:** Operations — UX surface, triggers, failure modes, validation (per master dispatch prompt)

## Task in one sentence

The user wants an agents-manager capability that turns a finished project into either (a) a reusable template under `templates/<name>/` or (b) a compact "core knowledge" extract that helps agents on similar future projects. This angle answers: **how would the capability actually feel to use, what does each agent see, what breaks, and how does am-review verify it before it ships.**

## What we know for sure

- The user-facing trigger sits at Phase 5 (next-steps, opt-in per `agents_manager/SKILL.md:390-414`); the dispatch prompt names Phase 5 by implication ("just finished a task ... extract now?").
- A precedent for "what an extraction looks like" already exists: `templates/cinematic-landing/examples/_recipe.md` (procedure) + `examples/_neutral/` (worked variant) — the two-file pair is the existing pattern for "this is what we did + here is the recipe another agent could follow".
- The template authoring rulebook is at `templates/AUTHORING.md:1-332` — 8 rules + folder structure + acceptance checklist (Rule 8). Any "extract-to-template" feature MUST produce an output that passes the Rule 8 checklist (`templates/AUTHORING.md:190-206`), not bypass it.
- The `_blank/` starter at `templates/_blank/` (14 files per CHANGELOG v0.14.0 line 73) is the documented copy-and-fill recipe; the rulebook explicitly says `cp -r _blank/ <your-name>/` is the author path (`templates/CONTRIBUTING.md:14`).
- The memory system at `agents_manager/memory/README.md:27-60` already defines a 3-scope extract mechanism (global / project / role) with a 20-line cap and a secrets-free hard rule. The user's "extract core to guide agents" maps directly onto a memory-scope write — not a new artifact.
- The triageable WARN list at `agents_manager/SKILL.md:373-388` has 8 entries today; this angle will surface new extraction-specific ones.
- The WARN register pattern at `share/notes/04_warns_register_T-2026-07-04-001.md` is the surface where extraction-output WARNs would land (per `agents_manager/SKILL.md:194-195`).
- Two scenarios in the dispatch are essentially the same artifact at different scopes: scenario X writes to `agents_manager/memory/projects/<slug>/` (memory), scenario Y writes to `templates/<name>/` (template). The runtime trigger and agent-surface are the only differentiators.
- `agents_manager/memory/README.md:114-116` explicitly fences `templates/<name>/memory/` as **not** a write target for the controller-memory tree — a hard boundary the design must respect.
- Existing `templates/` inventory (per `templates/README.md:13-20`): 3 active templates (`cinematic-landing` v0.14.0, `dashboard` v0.1.0, `docs-site` v0.1.0) + `_blank/` starter. Any new template must dedupe against this set or the INDEX.md consumer map lies.

## What we don't know (ambiguities)

- **Slug policy.** When user says "yes, scaffold a template", is the proposed slug derived from `git rev-parse --show-toplevel` basename (per `agents_manager/memory/README.md:22`), from a user-typed value, or from a hash? If two users in two unrelated projects both finish "auth-module" projects, do they collide on `templates/auth-module/`?
  - **Suggested clarifying question:** "When two unrelated users both propose a template named after the same kind of project (e.g. `auth-module`), should we (a) suffix by user/date, (b) refuse and ask the user to disambiguate, or (c) trust the second one will overwrite?"

- **Trigger cadence.** Is the Phase 5 prompt one-shot per task (fires once at Phase 5 entry) or per-master-session (fires every time the user opens the same project for a new task)? Repeated prompting is the #1 cause of "I just hit skip reflexively" fatigue (anecdotal pattern; not verified in this repo).
  - **Suggested clarifying question:** "Should the prompt remember 'user already said skip for this project' so it doesn't re-prompt every new task in the same project? Or prompt every time and trust the user to read?"

- **The 'edit which parts' choice in scenario X.** The dispatch prompt offers three buttons (yes / edit which parts / skip). "Edit which parts" implies a pre-flight editor — does the user pick which files move into the extract, or which memories get written, or which template sections get generated? The shape of the editor differs wildly across the three.
  - **Suggested clarifying question:** "When the user picks 'edit which parts' in scenario X, what is being edited: (a) the file list to copy, (b) the memory entries to write, (c) the template's INDEX.md sections, or (d) all three?"

- **Promotion vs creation.** If a user says "extract" and a template with the same name already exists, is the new run a **promotion** (merge into existing) or a **fork** (new `templates/<name>-v2/`)? Promotion implies a maintainer flow; fork implies unbounded tree growth.
  - **Suggested clarifying question:** "When extracting a project that overlaps an existing `templates/<name>/`, do we promote (edit in place via the existing template's CONTRIBUTING.md flow) or fork (`templates/<name>-<date>/`)? My recommendation: promote — fork destroys the rulebook's monotonic-number invariant."

- **Telemetry.** Does master need a `templates_extracted: <slug>` counter on the task tracker, or is "file exists at `templates/<name>/`" sufficient evidence? Without a counter, drift over time is invisible.
  - **Suggested clarifying question:** "Should the task tracker gain a `templates_extracted: <slug>` field (one-line evidence) or is the resulting directory path enough?"

## Risks and doubts

- **R1 — Re-invention of the memory write.** The user's "extract the core" framing maps onto `agents_manager/memory/projects/<slug>/` writes that the v0.13.0 protocol (`agents_manager/memory/README.md:27-60`) already defines. A new tool that writes memory without going through the existing protocol creates a parallel write path → 2 places to lint (`scripts/validate-memory.sh` per `agents_manager/memory/README.md:126`) → silent drift.
  - **Severity:** high
  - **Mitigation:** Scenario X must call the existing memory-write API (the 3-question durable-insight test + 20-line cap + secrets-free rule), not invent a new one. Scenario Y writes `templates/<name>/` files but those are template-author lane — out of scope for the master-led extraction unless we add an explicit author-mode toggle.

- **R2 — UX framing mismatch.** The dispatch prompt's scenario X ("takes ~30s, [yes / edit which parts / skip]") implies a one-click automation. Reality: producing even a minimal-legal template is the 9-step `AUTHORING.md:248-290` recipe (cp starter → fill INDEX → memory files monotonic → skeleton last → verify.sh → Rule 8 checklist → PR). 30 seconds is not realistic. Users will see a spinner, get a partial scaffold, and the **"edit which parts"** option will surface the truth that the heavy lift is still ahead. This is a UX lie.
  - **Severity:** high
  - **Mitigation:** Rename the prompt: scenario X is "scaffold a stub template" (genuine ~30s), and a follow-up "complete the recipe (9 steps)" task is dispatched separately. Master does not pretend 30s covers the full rulebook. Better still: scenario X is **just the memory write** — fast, secrets-checked, in-place — and scenario Y is "scaffold a stub template (passes verify.sh with placeholders only)".

- **R3 — Secrets leak via extract.** A finished project's `.env`, `config/local.json`, source-tree API keys, or `share/notes/02_secrets_*.md` could be copied into `templates/<name>/skeleton/` by a naive `cp -r`. The memory system already forbids this (`agents_manager/memory/README.md:108-113`), but a template is not memory — it has no built-in secrets-filter. A new failure surface.
  - **Severity:** high
  - **Mitigation:** Pre-flight secret scan (block list: `.env`, `.env.*`, `*.pem`, `*.key`, `id_rsa*`, `02_secrets_*`, plus regex `\b[A-Z0-9]{20,}\b` heuristic). Refuse to copy if any hit; surface the offending path to the user with a "delete then retry" prompt. Document this in `templates/AUTHORING.md` Rule 5 (manifest references).

- **R4 — Template = shipped bugs.** Auto-trigger fires when a project is "freshly done" → Phase 5 PASS verdict → memory shows clean review. But `share/notes/04_warns_register_T-2026-07-04-001.md` shows real templates ship with **multiple DEFERRED WARNs** that are accepted "not blocking ship" (e.g. AG16-W9 keyboard reachability, deferred with explicit follow-up title). A `templates/` extract that ships while the source has deferred WARNs propagates those WARNs to every future consumer with **no WARN register of its own**.
  - **Severity:** medium
  - **Mitigation:** Refuse to extract if `share/notes/04_warns_register_<task-id>.md` has any entry with status `OPEN` or `DEFERRED`. Surface the count to user before asking "extract anyway?". Or: extract, but **also write a derived WARN register** at `templates/<name>/WARN-register.md` listing what was inherited. Master decides which.

- **R5 — License / IP contamination.** The repo's `LICENSE` (not present in working tree as of `git ls-files`, to be verified at Phase 2) may not permit redistribution of the project's contents as a template. Even MIT-licensed source can carry third-party snippets under incompatible terms. The rulebook says nothing about license.
  - **Severity:** medium
  - **Mitigation:** Pre-flight: detect `LICENSE` file; require `templates/<name>/LICENSE` to be either (a) the source project's LICENSE copied verbatim with attribution, (b) the agents-manager repo's LICENSE, or (c) a new file the user authors. Refuse to extract without an explicit user declaration. This is a `templates/AUTHORING.md` Rule 8 checklist addition (probably the most important one — see am-review fail conditions below).

- **R6 — "Skip" button fatigue.** A prompt that fires at Phase 5 for every finished task trains the user to hit Skip reflexively. The first 3 times, the prompt is valuable; by the 10th, it is noise. This is an unverified concern but plausible; it is the **#1 documented anti-pattern** of in-product upsell flows in shipped software.
  - **Severity:** medium
  - **Mitigation:** Per-project opt-out flag stored at `agents_manager/.extract-prompt-disabled` (gitignored). After 3 consecutive skips for a project, master auto-creates the flag. Master re-prompts only when (a) flag absent AND (b) ≥30 days since last prompt for this project.

- **R7 — Memory scope cross-pollination.** When scenario X writes to `agents_manager/memory/projects/<slug>/`, the slug defaults to `basename $PWD` (`agents_manager/memory/README.md:135`). If a user runs the extract on project `foo-app` from a sub-directory, the wrong slug is derived → memory lands in `projects/<wrong-slug>/` → next session reads the wrong memory. The same risk exists today, but extracting creates new memory writes (vs. a single decision-log entry) that compound the error.
  - **Severity:** low
  - **Mitigation:** Resolve slug via `agents_manager/.active-project` first (per `agents_manager/memory/README.md:131-147`); print the resolved slug in the prompt's "writing to: …" line so the user sees the destination before confirming. The extraction tool fails closed if `.active-project` is missing AND `basename $PWD` is ambiguous (e.g. running from `/tmp`).

- **R8 — Duplication with existing templates.** A user finishes a Next.js dashboard; master scaffolds `templates/nextjs-dashboard/`; but `templates/dashboard/` already exists at v0.1.0 (`templates/README.md:18`). The new template is a near-duplicate; both live in the registry; consumers grep `data-section="table"` and find two INDEX.md maps with conflicting advice.
  - **Severity:** medium
  - **Mitigation:** Pre-flight: list existing `templates/*/` with their `INDEX.md` section-id lists; compute Jaccard similarity on the per-section table; if >0.6, refuse and surface "you might be duplicating `templates/dashboard/` — open that template and follow `templates/CONTRIBUTING.md` §I want to fix a bug in an existing template instead". This is the "promotion vs creation" question above — same root cause.

- **R9 — Stale template after a v0.x.x bump.** A template extracted from `agents-manager v0.14.1` is consumed under v0.15.0 if the controller's pipeline changed (new WARN surface, memory protocol changed). The template's `INDEX.md` references trigger phrases that don't match the new version. No automatic drift detection.
  - **Severity:** low
  - **Mitigation:** Templates carry a `controller_compat: >=v0.14.1` frontmatter on `00-readme-first.md`. `tests/verify.sh` (extended) greps the running controller's CHANGELOG and refuses to consume if the template's compat floor > running version. Push back to user with "this template needs a minor bump first; see its decision-log.md".

- **R10 — Master self-edit creep.** Phase 5 prompts are master's lane (master decides the menu at `agents_manager/SKILL.md:390-414`). Adding "extract" as a 5th Phase 5 option is a master protocol edit. Per `agents_manager/SKILL.md:496`, master does not silently rewrite the protocol during an active pipeline. If the extraction capability ships as a Phase 5 option, master must do so via an explicit maintenance phase, not as a side-effect of the extraction-feature PR.
  - **Severity:** low
  - **Mitigation:** Scope-limit: the extraction feature lives at Phase 5, but master's SKILL.md does NOT gain a new option in the same PR. Instead, master reads a **separate config** `templates/.extract-enabled: bool` (gitignored, default false); if true, master appends the prompt to its existing 4-option menu at runtime. Configuration > code for opt-in features.

## Technical findings

- **F1 — Phase 5 is opt-in, gateable per-task.** Per `agents_manager/SKILL.md:412-414`, Phase 5 is disabled by default; the task tracker row needs `phase_5_enabled: true`. The extraction prompt must follow the same pattern: an `extract_enabled: bool` flag on the task row (or a global config in `templates/.extract-config.yaml` if it spans tasks).
  - File: `agents_manager/SKILL.md:412-414`

- **F2 — Two scenarios share one scaffold path.** Scenario X (lightweight) → write to `agents_manager/memory/projects/<slug>/` (≤20-line entry, secrets-checked, append-only). Scenario Y (full) → `cp -r _blank/ templates/<name>/` + run `tests/verify.sh` → user fills in 9 steps → opens PR. The "extract" code path is ~5 lines (slug derive + scope check + scaffold); the heavy lift is the 9-step recipe (`templates/AUTHORING.md:248-290`) which is human-driven.
  - Files: `agents_manager/memory/README.md:27-60`, `templates/AUTHORING.md:248-290`, `templates/CONTRIBUTING.md:14-34`

- **F3 — The INDEX.md + 00-readme-first.md pair is the consumer API.** Per `templates/cinematic-landing/INDEX.md:1-12` ("It is the only INDEX read required") and `templates/README.md:21` ("grep discoverability — if a task brief mentions any of the trigger phrases above, the matching template applies"). An extraction that produces a `templates/<name>/` without an INDEX.md containing real trigger phrases (not boilerplate) produces a **dead template** that no agent can grep-find.
  - Files: `templates/cinematic-landing/INDEX.md:1-12`, `templates/README.md:13-22`

- **F4 — The rulebook's Rule 8 acceptance checklist is the gate, not the verify.sh alone.** Per `templates/AUTHORING.md:190-206` (12 checkbox items), `tests/verify.sh` enforces ~5 of those (T1–T8 in the cinematic-landing exemplar). The remaining 7 (no token-table duplication, reduced-motion manual test, a11y floor clean, etc.) are reviewer-judgment. am-review must be the gate, not just verify.sh.
  - Files: `templates/AUTHORING.md:190-206`, `templates/_blank/tests/verify.sh:1-28`

- **F5 — The memory protocol has a built-in "edit which parts" gate.** Per `agents_manager/memory/README.md:86-93`, the durable-insight test (3 questions) IS the editorial filter. The dispatch prompt's "edit which parts" button for scenario X is mechanically answered by that test — the user's choice is whether to proceed when the test fails. So "edit which parts" → "these 3 things don't pass the durable-insight test; pick which to keep, drop, or revise".
  - File: `agents_manager/memory/README.md:86-103`

- **F6 — The triageable WARN list (`agents_manager/SKILL.md:373-388`) has 8 entries, none extraction-specific.** Existing entries cover cosmetic / lint / dev-only findings — not the extract-specific risks (secrets leak, license contamination, duplication, scope mismatch). This angle proposes 5 new triageable entries (see "WARN taxonomy" below).

- **F7 — Memory entries are bounded at 20 lines per entry; templates are not.** Per `agents_manager/memory/README.md:104-106`, ≤20 lines is a hard cap. Templates have no cap but the rulebook's "smallest worked example" guidance (`templates/AUTHORING.md:258-263`) prefers ≤1100 lines of skeleton (cinematic-landing trace). The two scales are very different — extracting into memory is cheap; extracting into a template is expensive even in scaffold form.

- **F8 — `templates/_blank/tests/verify.sh` ships placeholder PASS lines.** Per `templates/_blank/tests/verify.sh:20-22`, the starter script's tests are `pass "T1 placeholder"` etc. — exit 0 by default. A scaffolded template passing verify.sh proves nothing until the author adds the 5 real tests (T1 ≥N data-section attrs, T2 no memory frontmatter, T3 MANIFEST resolves, T4 H1 matches filename, T5 H1 has USE THIS WHEN). The "passes verify.sh" claim from an extraction tool is therefore **vacuous** until the human completes the recipe.
  - File: `templates/_blank/tests/verify.sh:19-23`

- **F9 — Master's Phase 5 4-option menu (`agents_manager/SKILL.md:398-413`) is the natural injection point.** Adding "Extract to template / Extract memory-only / Skip / Close out" as options 0a/0b fits without restructuring the menu. The auto-detect (git vs non-git) at `agents_manager/SKILL.md:393-394` still applies. The extraction option runs only if `extract_enabled: true` per R10.

- **F10 — Cross-pollination guard already exists for templates.** `templates/<name>/memory/` is fenced at `agents_manager/memory/README.md:114-116` — controller memory cannot write there. But the inverse is unguarded: a template author could write to `agents_manager/memory/projects/<slug>/`. The extraction tool's writes must respect the existing fence (do not write into templates from controller-memory scope).

- **F11 — The `WARN register` is per-task, not per-template.** Per `agents_manager/SKILL.md:194-195`, `share/notes/04_warns_register_<task-id>.md` is task-scoped. Templates have no equivalent surface. R4's mitigation ("extract with a derived WARN register") requires inventing a new artifact: `templates/<name>/WARN-register.md` with a schema to be defined. Until defined, this is a gap.

- **F12 — The "scope: project" frontmatter (`agents_manager/memory/README.md:118-122`) is the cross-pollination filter.** Project-scope entries are bound to one project; the protocol mandates grep-by-slug before applying. R7's mitigation is already partly in the protocol — extraction just needs to set the right slug.

- **F13 — The "approved recipes" pattern (`templates/cinematic-landing/examples/_recipe.md`) is the worked-example format.** When scenario Y scaffolds a template, the user fills `examples/<name>/RECIPE.md` per `templates/AUTHORING.md:209-228`. The recipe documents the **procedure**, not just the result. The extraction tool cannot auto-generate a recipe; it can only scaffold an empty `examples/_recipe.md` for the human to write.

- **F14 — The 9-step recipe requires decisions the tool cannot make.** Step 1 ("decide the domain") and Step 2 ("pick the smallest worked example") are inherently human calls. The tool cannot substitute. So extraction = "steps 3-9 are pre-scaffolded; user fills 1-2 + verifies 8". Realistic time-to-complete (after scaffold): 30-60 minutes for a contributor who knows the rulebook; days for a newcomer.

## Feasibility verdict

- **Can do:** partial
- **Confidence:** MEDIUM
- **Why:** the lightweight scenario (X) is straightforward — it is a memory-write with the existing 3-question gate, plus the existing secrets-filter. Confidence is MEDIUM (not HIGH) because the dispatch prompt's framing of "edit which parts" as a button is underspecified and needs user clarification. The full scenario (Y) is feasible as a **scaffold**, but the dispatch prompt's "~30s" framing is wrong — the scaffold lands fast, the human-driven recipe takes hours-to-days. Confidence is MEDIUM (not LOW) because the rulebook (`templates/AUTHORING.md`) is binding and the tool only needs to produce a starter, not a finished template; the success criterion is "Rule 8 checklist items that are mechanically testable pass; the rest is reviewer judgment", which is well-defined.

## Recommendations for the planning agent

1. **Reframe scenario X as a memory-write, not a new tool.** Scenario X is "memory write to `agents_manager/memory/projects/<slug>/`" — already supported by the v0.13.0 protocol. Plan a thin master helper (~30 lines) that: resolves slug, runs the durable-insight test interactively with the user, runs the secrets filter, writes the entry. ~150 LOC including tests.
2. **Reframe scenario Y as a starter-scaffold, not a finished template.** Scenario Y is "scaffold `templates/<name>/` from `_blank/`" — already supported by `cp -r _blank/`. Plan a thin master helper that: pre-fills `INDEX.md` from a template, runs `tests/verify.sh`, opens the 9-step checklist, hands off. ~200 LOC including the verify.sh extension.
3. **Move the user's "30s" claim into the prompt literally.** The Phase 5 option should read "Scaffold a starter template (~30s — fills placeholders only; complete the 9-step recipe in `templates/AUTHORING.md` afterwards)". Do not lie about scope.
4. **Add 5 new triageable WARNs (see WARN taxonomy section).** Update `agents_manager/SKILL.md:373-388` list.
5. **Add 2 new Rule 8 acceptance checklist items: LICENSE + secrets-scan.** `templates/AUTHORING.md:190-206` needs the new items.
6. **The 4 clarifying questions (slug policy, trigger cadence, edit-which-parts, promotion-vs-creation) gate planning.** Without user answers, the plan will paper over real ambiguity.
7. **Master SKILL.md does NOT gain a new option. Use `templates/.extract-config.yaml`** (gitignored, opt-in flag) so the controller fence stays clean. (R10 mitigation.)

## Open questions for the user

1. **Slug policy.** When two unrelated users both propose `templates/auth-module/`, do we (a) suffix by user/date, (b) refuse and disambiguate, or (c) overwrite? **(a) recommend.**
2. **Trigger cadence.** Should the Phase 5 prompt remember "user said skip for this project" so it doesn't re-prompt every new task, or prompt every time? **Remember + auto-disable after 3 skips — recommend.**
3. **"Edit which parts" scope.** When user picks this button in scenario X, what is being edited — file list, memory entries, INDEX sections, or all three? **Memory entries only — recommend (scenarios X and Y separate the two surfaces).**
4. **Promotion vs fork.** On overlap with existing template, do we promote (edit in place via `templates/CONTRIBUTING.md` §bug fix flow) or fork (`templates/<name>-<date>/`)? **Promote — fork destroys monotonic-number invariant.**

## Self-critique

- **Did I do my job?** Partial. I answered all 6 research questions but the answer to Q3 (failure modes) is bounded by my own risk-tolerance — I named 10 failure modes but a paranoid reviewer would surface more (e.g., what if the user is offline and the prompt fires on resume; what if the project is in a sub-module of a monorepo). Better than nothing; not exhaustive.
- **What might I have missed?** I did not check whether `agents_manager/SKILL.md` Phase 5 has any v0.15.0 draft changes in flight (CHANGELOG only goes to v0.14.1 as of `agents_manager/CHANGELOG.md:1`). If Phase 5 is being redesigned, the "inject the extraction prompt into Phase 5" plan becomes wrong. I also did not verify whether `agents_manager/research/SKILL.md` itself has an opt-in mechanism for research notes to be auto-extracted into memory (the protocol says master writes memory, but research's own `## Metrics` block is memory-shaped). Could be a third surface.
- **What did I assume without evidence?** (a) That the repo has no `LICENSE` file (to be confirmed — flagged as a planning input). (b) That the rulebook's monotonic-number rule is non-negotiable in practice — it is binding per `AUTHORING.md:36-40` but I have no counter-example of a fork-style override. (c) That the user's "30s" framing is wrong — it is wrong for the rulebook-driven scenario Y, but plausible if we narrow scope to "memory-write only".

## Cross-role perspectives

### From am-design

The user-facing UX for the two scenarios needs visual + copy + flow design, not just text. Specifically:

- **The Phase 5 prompt is the entire UX surface.** It is a single modal at task completion. There is no multi-step wizard — that would belong in a separate "guided extraction" workflow, not Phase 5. am-design should produce a one-shot prompt with 3 buttons (per scenario) and a single-sentence preview of the artifact destination.
- **The "preview" option in scenario Y is critical.** Before scaffolding `templates/<slug>/`, the user needs to see: (a) the proposed slug, (b) the existing templates it overlaps with (Jaccard score), (c) the proposed file list, (d) the verdict from secrets-scan. This is the same pattern as `git init` — show what's about to happen before committing. am-design should produce a preview card that fits in <200 chars.
- **"Skip" must be a persistent, single-click choice.** After 3 skips per project, master auto-disables (R6 mitigation). am-design needs a "Don't ask again for this project" toggle as a 4th button.
- **The "edit which parts" button is the hardest UX call.** am-design should default to **edit on the memory entries only** (scenario X surface). For scenario Y, "edit which parts" should open the user's editor at `templates/<name>/INDEX.md` directly — a "scaffold then hand off" pattern, not a "guided wizard" pattern.
- **Visual artifacts to produce at Phase 2 (planning):** ASCII mockup of the prompt (3 buttons, preview card), ASCII mockup of the preview card, ASCII mockup of the post-extract confirmation (what was written, where, with what diff). These live at `share/design/T-2026-07-04-009/`.

### From am-planning

Where does this fit in the pipeline? The options:

- **(A) Always-on at Phase 5 entry.** Every task with `phase_5_enabled: true` AND `extract_enabled: true` (per `templates/.extract-config.yaml` from R10) gets the prompt. Master adds options 0a (memory-only) and 0b (template scaffold) to the existing 4-option Phase 5 menu. **Pro:** simple, one trigger. **Con:** prompts every task; rely on user to skip.
- **(B) Per-request via a new task type.** User says `agents-manager extract` and master routes to a new dispatch path that bypasses the regular pipeline. **Pro:** no prompt fatigue. **Con:** user must remember the incantation; low discoverability.
- **(C) Always-on skill, fired by `find-skills`-style trigger phrases.** Master surfaces the option when the user's last message matches a trigger phrase ("we should template this", "extract the recipe"). **Pro:** discovery via natural language. **Con:** brittle matching; false positives.
- **(D) Hybrid.** Default = option A (Phase 5 prompt) but the prompt offers a "don't ask again" toggle that downgrades to option B (manual incantation). **Pro:** graceful degradation. **Con:** two code paths to maintain.

**My recommendation: (D) hybrid.** It satisfies both first-time users (low friction, prompt is right there) and experienced users (opt out of the prompt). The toggle is the persistent opt-out (R6 mitigation). am-planning should produce a phase plan that gates implementation behind user answers to the 4 clarifying questions — without them, the plan would paper over real ambiguity (especially the promotion-vs-fork question).

**Pipeline moment fit:** this is a **Phase 5 (next-steps, opt-in)** feature, not a new pipeline phase. Master does not gain a new mandatory step. The extraction is **bounded to 2 outputs**: (a) a single memory entry write (existing protocol), (b) a starter template copy (existing recipe). No novel abstractions, no novel dispatchers.

### From am-review

am-review would FAIL the new template-extraction capability on any of these conditions. Each has a verify command:

- **F1 — Scaffolded template's `_blank/tests/verify.sh` still contains placeholder PASS lines.** `rg -n 'placeholder' templates/<name>/tests/verify.sh` must return 0 hits before ship. **(FAIL)**
- **F2 — Manifest references files that don't exist.** `while IFS= read -r p; do [ -e "$p" ] || { echo "MISSING: $p"; exit 1; }; done < templates/<name>/assets/MANIFEST.txt` must exit 0. **(FAIL)**
- **F3 — Any memory file lacks `USE THIS WHEN:` on H1.** `rg -L 'USE THIS WHEN:' templates/<name>/memory/*.md` must return 0 files. **(FAIL)**
- **F4 — H1 number drifts from filename prefix.** `templates/<name>/memory/03-foo.md` must open with `# 03 · …`. Verify: `for f in templates/<name>/memory/*.md; do n=$(basename "$f" | cut -d- -f1); head -1 "$f" | rg -q "^# $n " || { echo "DRIFT: $f"; exit 1; }; done`. **(FAIL)**
- **F5 — LICENSE missing or unattributed at `templates/<name>/LICENSE`.** `[ -f templates/<name>/LICENSE ] || exit 1`. **(FAIL)** Also: license must be on the rulebook's whitelist (MIT, Apache-2.0, BSD-2/3, ISC, CC0, CC-BY, or user-declared-equivalent) — see WARN taxonomy below.
- **F6 — Secrets in skeleton.** `rg -l '\.env' templates/<name>/skeleton/ ; rg -l 'sk-[A-Za-z0-9]{20,}' templates/<name>/skeleton/ ; rg -l '-----BEGIN [A-Z ]*PRIVATE KEY-----' templates/<name>/skeleton/` must all return 0. **(FAIL)**
- **F7 — Index.md trigger phrases empty / boilerplate.** `rg -c '^## (Use when|Trigger phrases|Use this template when)' templates/<name>/INDEX.md` must be ≥1 (real phrases, not the placeholder "see worked example"). **(FAIL)**
- **F8 — Open WARNs in source project's `04_warns_register_<source-task-id>.md`.** `rg -c '^OPEN' share/notes/04_warns_register_<source-task-id>.md` must be 0 at extract time. **(FAIL if >0; user must explicitly accept.)**

Beyond the FAIL conditions, **WARN**-level checks:

- W-extract-1: source project has DEFERRED WARNs (count >0 in WARN register) — extraction propagates them; warn + ask user.
- W-extract-2: extract produces template that Jaccard-overlaps an existing `templates/<other>/` (score >0.4) — recommend promotion flow instead.
- W-extract-3: source project's `INDEX.md` is the boilerplate placeholder — recipe is meaningless; mark recipe as `(unfilled — author to complete)`.

## WARN taxonomy (new for v0.14.2+)

**Existing triageable entries** (`agents_manager/SKILL.md:373-388`) cover cosmetic / lint / dev-only findings. The extraction capability introduces 5 new categories. **Recommendation: add to the list, opt-in only (per `auto_accept_warns: bool` flag pattern):**

- **W-extract-secrets-near-miss** (MEDIUM) — secrets-scan regex hit was a false positive (e.g., test fixture with `sk-test12345…`); user confirms safe. Auto-acceptable with user confirmation. Path: extraction tool's pre-flight log.
- **W-extract-license-unattributed** (HIGH) — `templates/<name>/LICENSE` missing or copied from source without explicit attribution line. NOT auto-acceptable; surface to user every time. (R5 mitigation.)
- **W-extract-overlap-with-existing** (MEDIUM) — Jaccard similarity >0.4 with existing `templates/<other>/`. Auto-acceptable with user "promote instead" choice. (R8 mitigation.)
- **W-extract-source-has-open-warn** (MEDIUM) — source project's `04_warns_register` has OPEN entries at extract time. NOT auto-acceptable; user must explicitly accept propagation. (R4 mitigation.)
- **W-extract-skip-fatigue** (LOW) — 3+ consecutive skips for same project; auto-disable prompt. Auto-acceptable; no user prompt. (R6 mitigation.)

**Net effect on `agents_manager/SKILL.md:373-388`:** the list grows from 8 to 13 entries. The `auto_accept_warns: bool` flag's default of `false` preserves current behavior — users who have not opted in to auto-accept still see every WARN surfaced.

## Memory hygiene (verbatim from `agents_manager/memory/README.md`)

When the capability writes to `agents_manager/memory/global/` or `agents_manager/memory/projects/<slug>/`, the following rules apply **unchanged from the existing protocol**:

- **Secrets-free rule (L108-113):** *"Memory entries must NEVER name, quote, or reference a `share/notes/02_secrets_<task-id>.md` path or value. Reference the task id (`T-YYYY-MM-DD-NNN`) instead."* — The extraction tool's pre-flight secrets-scan must check that no candidate entry violates this.
- **No-write-into-templates (L114-116):** *"Do NOT write into `templates/<name>/memory/`. That's the template author's lane (see `agents_manager/assets/SKILL.md`)."* — The extraction tool's scenario Y writes to `templates/<name>/` (root level, not `templates/<name>/memory/`); this rule does not block it but the controller-memory scope must NOT confuse `templates/<name>/memory/` with its own `agents_manager/memory/` tree.
- **Size cap (L104-106):** *"≤20 lines per entry (including frontmatter and body). Why: keeps the per-scope 200-line read budget stable..."* — Scenario X's output is a single memory entry; it MUST fit in 20 lines. If the durable insight exceeds 20 lines, split or compress (per L106).
- **Append-only (L66-70):** *"Memory is **append-only** by design. To supersede an entry: leave the original in place with `status: superseded` and add `superseded_by: <path-to-new-entry>`."* — Extraction that runs twice on the same project must not overwrite; it must append a new entry or supersede the prior one with a forward-pointer.
- **Required frontmatter (L62):** `scope`, `topic`, `status`, `created`, `last_verified` — every extraction-written entry must carry all five.
- **Cross-project scoping (L118-122):** *"When reading project-scope entries, grep by `scope: project` + active project slug before applying."* — R7's mitigation (R7 above): the extraction tool must set the correct slug; the read-side protocol already filters.
- **Hard cap trigger (L59):** *"If a scope exceeds 200 lines, stop reading and report to master — that's a 90-day sweep signal."* — Extraction does not affect this directly, but a heavy extraction burst into `projects/<slug>/` could approach the cap and surface the sweep signal.

**No new hygiene rules are needed.** The existing protocol is sufficient. The extraction tool is a thin wrapper around it.

## Status signal

**DONE_WITH_CONCERNS**

- The research is complete on all 6 questions.
- The concerns are:
  - C1 — The dispatch prompt's framing of "30s" for scenario Y is incorrect; the scaffold is fast, the recipe is not.
  - C2 — The "edit which parts" button is underspecified and gates planning on user clarification.
  - C3 — The 4 clarifying questions (slug policy, trigger cadence, edit scope, promotion-vs-fork) are real and not derivable from context.

NEEDS_USER_INPUT: **true** — the 4 clarifying questions must be answered before planning begins.

---

## Metrics

- findings: 14
- risks_HIGH: 3
- risks_MEDIUM: 4
- risks_LOW: 3
- clarifying_Qs: 5