# Master synthesis v2 — T-2026-07-04-009 (post-user-clarification)

**Date:** 2026-07-04
**Author:** master (orchestrator)
**Supersedes:** `share/notes/01_master_synthesis_T-2026-07-04-009.md` (v1)
**Status:** DONE_WITH_CONCERNS — synthesis updated; awaiting user sign-off before Phase 2 planning dispatch
**Task tracker:** `tasks/T-2026-07-04-009.md`

---

## User answers (resolved gating questions)

| # | Gating Q | User's answer | Implication |
|---|---|---|---|
| 1 | Ship location | **No standalone tool. Use the same agents-manager, guided.** Agents read a guide/instruction/rules. Triggered by (a) a separate command the agents recognize OR (b) user explicitly tells the agent in conversation. | The "extraction" is an agent-led activity using the existing pipeline, not a CLI script. |
| 2 | Sub-ask B scope | **Mostly tech stack OR domain. Add filter words.** | Memory entries get `tech_stack:` and `domain:` frontmatter fields; specialists filter on read. |
| 3 | Generation mode | **LLM-assisted generation is acceptable.** Agents can tune for different tech stack/domain. | The agents do the template generation (read the source project, produce the template artifacts), guided by the rulebook. |
| 4 | Slug policy + trigger cadence | **Suffix-on-collision + per-project opt-out after 3 skips.** | Stable, predictable naming; respects user attention. |
| 5 | Promotion vs fork | **Promote (edit in place).** | Single source of truth; CONTRIBUTING.md flow governs. |

---

## What changed vs v1 synthesis

v1 recommended a `bin/agents-manager-extract-template.{py,sh,cmd}` CLI script. **The user explicitly rejected that shape.** v1 also defaulted memory writes to `agents_manager/memory/global/` after per-entry user confirmation. **The user wants tech_stack/domain filter words**, not just global-vs-project routing.

The v2 shape:

| Concern | v1 (superseded) | v2 (current) |
|---|---|---|
| Extraction mechanism | CLI script (deterministic) | Agent-led, LLM-assisted, guided by rulebook |
| Storage for extracted knowledge | `agents_manager/memory/global/` (default) | `agents_manager/memory/global/` with `tech_stack:` + `domain:` frontmatter; filtered on read |
| Trigger | Phase 5 menu entry only | Phase 5 menu entry **AND** explicit user invocation ("extract this to a template") |
| The "thinking work" | Script logic | Specialist agent (am-research or am-design) reads the guide, produces analysis + draft |
| The "writing work" | Script does it | Master does it (controller owner) |
| What the user explicitly invoked | CLI command | Conversation instruction OR Phase 5 menu pick |

This is **closer to the gstack user-installed skills pattern + Anthropic Skills convention** than to a CLI tool. The agents-manager becomes self-extending: the guide IS the new capability, and the existing agents do the work.

---

## Updated recommendation — v0.15.0 additive

### Core (the guide + skill — minimum that delivers value)

1. **`templates/EXTRACTION.md`** — the extraction rulebook. ~400-600 LOC. Mirrors `templates/AUTHORING.md` style. Contents:
   - Pre-flight checklist (license, secrets scan, Jaccard overlap check, source WARN register status)
   - 9-step extraction recipe (parallel to AUTHORING.md's 9-step authoring recipe)
   - Worked example (extracting `templates/cinematic-landing/` from a real finished project, retroactively)
   - "What the agent can't decide" (trigger phrases on memory files, brand generalization choices, the recipe calls that are inherently human)
   - Cross-references: `templates/AUTHORING.md`, `templates/CONTRIBUTING.md`, `agents_manager/memory/README.md`, `share/templates/cinematic-landing-fixes.md`

2. **`agents_manager/extract/SKILL.md`** — the skill file with YAML trigger frontmatter (per Anthropic Skills convention). ~200 LOC + frontmatter. Tells any specialist that picks it up:
   - **description:** "Extract a finished agents-manager project into a reusable template or core knowledge. Use when the user says 'extract', 'template this', 'convert to template', or picks the Phase 5 'Extract' menu option."
   - **paths:** `templates/**`, `agents_manager/memory/**`, `share/templates/drafts/**`
   - Body: the procedure the agent follows (read source → pre-flight → scaffold → fill memory → skeleton → verify.sh → emit audit log → hand back to master for promotion)

3. **`agents_manager/extract/rules.md`** — extraction-specific rules. ~100 LOC. Hard rules (mirror the existing per-role rules.md pattern):
   - R1: NEVER write to `templates/<name>/memory/` from this lane; the template author owns that after promotion.
   - R2: NEVER write secrets; refuse and surface if pre-flight scan hits.
   - R3: NEVER copy source LICENSE without attribution; refuse if `templates/<name>/LICENSE` would be unattributed.
   - R4: ALWAYS invoke `tests/verify.sh` after scaffolding; non-zero exit = FAIL.
   - R5: ALWAYS run `scripts/validate-memory.sh` after writing memory entries.
   - R6: NEVER auto-default to `global/`; require explicit user-confirmed scope per entry.
   - R7: NEVER overwrite an existing `templates/<name>/`; suffix the slug on collision (R-collision).
   - R8: ALWAYS emit an audit log at `share/notes/03_extracted_<task-id>.md` documenting sources, destinations, and verdicts.

### Trigger integration

4. **Phase 5 menu enhancement** in `agents_manager/SKILL.md:406-412` — add option 5: "Extract this project to a template / core knowledge." Gated on opt-in flag at `agents_manager/memory/.extract-config.yaml` (gitignored, default false). Master invokes the specialist (am-research or am-design, master's choice based on the project shape) with the extraction SKILL loaded.

5. **Conversation trigger** — Master's pause-and-ask hook (`agents_manager/SKILL.md:228-238`) recognizes user phrases: "extract this", "template this project", "convert to a template", "extract the core knowledge", "what would I reuse from this?" → routes to the extraction specialist.

### Memory schema extension

6. **`agents_manager/memory/README.md` schema extension** — add `tech_stack:` and `domain:` fields to the required frontmatter (line 62). These are comma-separated lists. Used for read-side filtering.

7. **Read-side filter subroutine** — extend `agents_manager/memory/README.md:75-83` read-on-entry protocol with a filter step: "If your current task has `tech_stack: react,nextjs` and `domain: ecommerce`, grep memory entries for matching tags before applying." This is a soft filter (specialist chooses), not a hard gate.

### Polish (defer to v0.15.x patches after usage feedback)

8. **`scripts/validate-template.sh`** — new enforcement script for `templates/AUTHORING.md` Rules 1-8. ~80 LOC. The extraction skill runs this on its output as a self-check.

9. **5 new triageable WARNs** in `agents_manager/SKILL.md:373-388` (W-extract-secrets-near-miss, W-extract-license-unattributed, W-extract-overlap-with-existing, W-extract-source-has-open-warn, W-extract-skip-fatigue).

10. **2 new Rule 8 acceptance items** in `templates/AUTHORING.md:190-206` (LICENSE check + secrets scan).

11. **`share/templates/cinematic-landing-fixes.md` worked-example trace** — document a retroactive extraction to validate the recipe against a known exemplar. Demonstrates the procedure is real, not aspirational.

---

## What v2 deliberately does NOT do

- Does NOT add a new specialist (`am-extract`). The extraction is a **skill** that any specialist picks up; routing is master's call.
- Does NOT modify `opencode.jsonc`. Controller fence stays clean.
- Does NOT add a CLI script (`bin/agents-manager-extract-*`). The user said no standalone tool; extraction is agent-led.
- Does NOT modify any existing `agents_manager/<role>/SKILL.md` or `rules.md`. Specialists read `agents_manager/extract/SKILL.md` ad-hoc; their own SKILL stays clean.
- Does NOT modify `templates/_blank/`. The `_blank/` is the source-of-truth starter; extraction does not modify it.
- Does NOT auto-trigger at Phase 5. Opt-in via the config flag (matches v1 R11 mitigation).

---

## Estimated scope (updated)

- **Core (items 1-5):** 4 new files (`templates/EXTRACTION.md`, `agents_manager/extract/SKILL.md`, `agents_manager/extract/rules.md`, `agents_manager/memory/.extract-config.yaml.example`), 3 modified (`agents_manager/SKILL.md` Phase 5 menu, `agents_manager/memory/README.md` schema + read protocol, `templates/CONTRIBUTING.md` cross-ref). ~1200-1500 LOC + tests. **Confidence HIGH.**
- **Core + memory schema (items 1-7):** + 0 new files, 1 more modified (`agents_manager/memory/README.md`). ~1500-1700 LOC. **Confidence HIGH.**
- **Full (items 1-11):** + 1 new file (`scripts/validate-template.sh`), + 2 modified (`templates/AUTHORING.md`, `share/templates/cinematic-landing-fixes.md`). ~2000-2500 LOC. **Confidence MEDIUM-HIGH**; the polish items are additive and low-risk individually.

The **single-phase trigger threshold** (`agents_manager/SKILL.md:130-145` — LOC > 1200 OR files > 15 OR novel_abstractions ≥ 2): the "Full" version would trip this; am-planning should split into 2 sub-phases if you go full. "Core + memory schema" is under the threshold and ships as one phase.

---

## Per-role bias-check (what each specialist would say)

- **am-research voice:** "Yes, the guide is a research artifact as much as a template. `templates/EXTRACTION.md` should be readable as research output too — meta-circular." → Recommendation: add a section "When extraction is research" linking to `agents_manager/research/SKILL.md` patterns.
- **am-planning voice:** "Where in the pipeline does this fit? Phase 5 opt-in menu + conversation trigger. Two trigger surfaces, one skill. Master handles routing. No new pipeline phase." → Matches v2 design.
- **am-design voice:** "The user-facing UX is two prompts: (a) Phase 5 menu pick, (b) any time the user says 'extract/template/convert'. The first prompt needs to show a preview card (proposed slug, Jaccard score, secrets-scan verdict, proposed destination paths). The second trigger needs a one-question confirmation: 'I'll extract this to a template. Confirm?'" → Add this to am-design's Phase 2 deliverables.
- **am-coder voice:** "LLM-assisted generation means the specialist reads source files and PROPOSES template content. The specialist does NOT write `templates/<name>/memory/` directly — that's template author lane. The specialist writes a PROPOSAL to `share/templates/drafts/<name>/`, and a human (or am-review in promote-mode) promotes." → Matches v2 design (master does the final write, not the specialist).
- **am-review voice:** "Validate against Rules 1-8 of `templates/AUTHORING.md` before allowing promotion from `share/templates/drafts/` to `templates/<name>/`. Specifically the 8 FAIL conditions from `share/notes/01_research_T-2026-07-04-009_angle-operations.md` F1-F8." → Matches v2 design.

---

## Honest pushbacks on the user's answers

1. **"Use the same agents-manager"** is correct, but the agents doing the extraction need their own skill file. Putting the procedure in `agents_manager/SKILL.md` (master's lane) is wrong — that's the orchestrator's doc, not a worker's procedure. Putting it in `agents_manager/extract/SKILL.md` as a new skill file is the right shape. The user implicitly endorsed this by saying "agents will use the guide/instruction/rules."

2. **"LLM-assisted generation is acceptable"** opens up quality variance. The rulebook needs explicit acceptance criteria (the Rule 8 checklist + the 8 am-review FAIL conditions from operations angle F1-F8) so the specialist's output is gated, not free-form. This is captured in items 1+9.

3. **"Tech stack or domain filter words"** is a clean answer but introduces a new failure mode: what if a project's tech_stack changes over its lifetime? `react` → `nextjs` → `react-native`. The schema needs to handle multi-tag entries (comma-separated lists) and the read-side filter needs to be a soft match (any tag matches = candidate). Captured in item 6+7.

4. **"Promote (edit in place)"** means extraction is bounded to ONE pass per project. If the source project changes after extraction, the template goes stale. Mitigated by the `controller_compat: >=v0.x.y` frontmatter pattern (R10 from operations angle) — but only if we actually ship it. Captured in item 10 (Rule 8 addition).

---

## What happens next

Once you sign off on v2, I dispatch `am-planning` with the v2 recommendation. The plan will:
- Confirm the scope you pick (Core, Core+memory, or Full)
- Produce phased chunks respecting the single-phase trigger threshold
- Include complexity blocks for each phase
- Surface any sub-phase splits if Full is chosen

**Recommend scope: "Core + memory schema" (items 1-7).** It's under the single-phase threshold, ships the user's literal ask, and includes the schema extension that makes sub-ask B useful.

**Sign-off options:**
- **(A)** Approve v2 as-is → I dispatch am-planning with Core+memory scope.
- **(B)** Approve v2 but scope down to Core-only (items 1-5) → skip the memory schema extension for v0.15.0; ship it as a v0.15.x patch.
- **(C)** Approve v2 but scope up to Full (items 1-11) → am-planning will split into 2 sub-phases.
- **(D)** Refine further → tell me what to change.

**Standing by.**

---

## Files updated this turn

- `share/notes/01_master_synthesis_T-2026-07-04-009.md` → superseded by v2 (this file)
- `share/notes/99_progress_T-2026-07-04-009.md` → appended Phase 1.5 entry
- `tasks/T-2026-07-04-009.md` → status of P1M = done; P2T1 = gated awaiting user scope pick

---

## Metrics

- findings: 10 (unchanged from v1 — merged research still holds)
- risks_HIGH: 5 (unchanged)
- risks_MEDIUM: 4 (unchanged)
- risks_LOW: 3 (unchanged)
- clarifying_Qs: 5 → 0 (all resolved by user this turn)
- user_scope_pick: pending (A / B / C / D)

## Status signal

**DONE_WITH_CONCERNS** — synthesis updated; 5 Qs resolved; waiting for user scope pick (A/B/C/D) before Phase 2 planning dispatch.

NEEDS_USER_INPUT: **true** — pick scope (A/B/C/D) and any refinements.