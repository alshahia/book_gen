# 99 — Architectural decisions

Append-only. Each entry = one decision with rationale, scope, and reversibility.

## 2026-07-05 — Protocol response to T-minimax2.7 (Kotlin Quran) reflection

**Source:** user pasted `agent_reflect_minimax2.7_kotlin.txt` (Downloads) documenting a Quran-app run that shipped technically correct but culturally empty output.

**Decision:** apply 5 minimal protocol changes to `agents_manager/SKILL.md`. Each addresses one reflection recommendation. All within master's lane (master's own SKILL.md only).

**Changes applied:**

| # | Reflection rec | Protocol change | Location |
|---|---|---|---|
| A | Design as first-class phase | New "Design preflight" — dispatch `am-design` before Phase 2 when cultural/visual triggers fire; brief is required input to plan + review | SKILL.md between Phase 1 and Phase 2 |
| B | Document auto-approve defaults | Mandatory `share/handoffs/auto-answers_<task-id>.md` when `fill_defaults: true`; no silent absorption | Phase 0 Ingest |
| C | Review validates user intent | New "user-intent alignment check" in Phase 4 — PASS-on-spec / FAIL-on-intent = FAIL | Phase 4 Review |
| D | Self-score gates progression | Strengthened planning gate: any dimension <5 → "what would raise this to 5?" before advancing | Programmatic gates table |
| E | Split auto-approve signal | Two orthogonal flags: `fill_defaults` (silence defaults) vs `skip_gates` (silence user waits) | Phase 0 Ingest (same bullet as B) |

**Out of lane (flagged for a dedicated maintenance phase, NOT applied here):**

- `am-design/SKILL.md` — master can now dispatch am-design more aggressively, but am-design's contract for what the brief MUST contain is owned by am-design's author.
- `am-review/SKILL.md` — master now requires intent-alignment prompts, but am-review's contract for what it MUST validate beyond spec is owned by am-review's author.
- `am-research/SKILL.md` — master now requires auto-answers to be written, but am-research's contract for HOW it answers defaults is owned by am-research's author.

**Reversibility:** trivial. Each change is one bullet / row / section in SKILL.md. Rollback = revert the 4 edits.

**Ponytail note:** reflection named 5 problems. I added the minimum protocol surface to address each one. Did NOT add: new agents, new mandatory phases, new files beyond `share/handoffs/auto-answers_*.md`, new gates beyond the strengthened self-score rule, or new reviewer checks beyond the intent-alignment prompt requirement.

## 2026-07-05 — Adaptive orchestration (pipeline as default, not rule)

**Source:** user directive on master behavior. Existing protocol framed the pipeline as the dominant paradigm; specialists were exceptions within it. User wants the inverse: specialists as a toolkit, pipeline as a default shape, master adapts to project complexity.

**Decision:** insert new "Adaptive orchestration (v0.16.0+)" section BEFORE "The mandatory pipeline". Soften the pipeline's mandatory language to "default shape". No structural pipeline changes — only framing.

**Four authority levers the user called out:**

1. **Complexity triage** — trivial / one-step / standard / complex maps to direct / single-dispatch / pipeline / pipeline+adapt.
2. **Re-dispatch any specialist any number of times** — phase boundaries are not single-use gates.
3. **Run specialists in parallel** — research + explorer + designer co-existing is the norm for complex work, not the exception.
4. **Apply review to any artifact** — plan, brief, design can all be reviewed, not just code.
5. **Propose better solutions proactively** — surface alternatives with full reasoning before acting; user decides.

**Inform-the-user rules:** every significant action gets a "what + why + pros/cons" message; every fork gets options; never silently pick; never silently substitute user's intent with master's preference.

**Audit-trail rules (unchanged but reinforced):** progress ledger + WARN register + handoffs + task tracker Loop history. Reconstruction must be possible.

**Reversibility:** trivial. Revert = delete the new section, restore "Every user task flows through these phases. Do not skip a phase. Do not reorder."

**Out of lane (not addressed):** specialist SKILL.md files (`am-design`, `am-review`, `am-research`, `am-planning`, `am-coder`). Master can now use them more flexibly, but their contracts are owned by their authors. A separate maintenance phase would update those.

## 2026-07-05 — Maintenance phase: adaptive-mode propagated to all 7 agents

**Source:** user follow-up. Asked for: (a) maintenance-phase plan to update specialist SKILL.md files (option b), AND (b) base instructions in `opencode.jsonc` updated for each agent so adaptive-mode is internalised, not just referenced from master's doc.

**Soft-wall override:** master normally CANNOT edit `opencode.jsonc` or other agents' `agents_manager/<role>/SKILL.md`. The v0.5.0+ soft-wall override clause permits this with explicit surface — declared at the top of the work and applied with user consent.

**Changes (13 edits):**

- `opencode.jsonc` — added `## Adaptive mode (v0.16.0+)` block to all 7 agent prompts. Master gets the full orchestration framing (complexity triage, inform-the-user, propose-better). 6 specialists get the abbreviated reflex (self-validate, propose better, surface cross-lane) with a link to the full protocol.
- 6 specialist `SKILL.md` files (research / planning / design / coder / review / assets) — added ~8-line `## Adaptive mode (v0.16.0+)` section right after the role statement. Five-reflex block: (1) re-dispatch is normal, read latest state; (2) parallel work expected, coordinate via `share/messages/`; (3) self-validate before returning, cite `path:line`; (4) propose better solutions proactively; (5) cross-lane work returns to master.

**Why both files?** `opencode.jsonc` prompts are injected at every agent invocation as the base instruction. Specialist `SKILL.md` files are loaded once per session as standing rules. Updating both means: short-term memory (each call) + long-term memory (each session) both carry the new contract.

**Reversibility:** trivial. Each insertion is one block. Rollback = delete the inserted block in each of 13 files.

**Ponytail note:** user wanted "agents not to forget it". Minimum visible-surface = one high-visibility section per file (~8 lines), not a separate shared doc agents might skip reading. Each section reads as part of the file, not a stub.

**`am-assets/SKILL.md` was also updated** even though the original "option b" referenced only 5 specialists. Including it keeps the 6th specialist from drifting out of the contract.

## 2026-07-05 - Adaptive-mode smoke test + 1-sentence rationale add

**Source:** user picked option (b) on m0023 - run a smoke test dispatching one specialist through the new protocol and read its first turn.

**Smoke test:** dispatched m-research with a question about how OpenCode's 	ask tool handles 	ask_id reuse. Task was deliberately chosen to exercise all 5 adaptive reflexes (self-validate, propose-better, stay-in-lane, re-dispatch awareness, parallel coordination).

**Result:** PASSED. am-research returned a thorough response that:
- Cited path:line on every claim (e.g. 	ask.ts:87-89, 	ask.ts:113-119, gents_manager/SKILL.md:377)
- Dropped confidence HIGH -> MEDIUM-HIGH when two claims became inferred-not-proven
- Stayed in lane (no writes to share/notes//share/design//share/reports//	asks/)
- Grepped prior research before answering (confirmed no prior session covered this)
- Proposed 2 concrete workarounds + explicitly declined the obvious-but-wrong fix (enabling 	ask_id reuse without deliberation)
- Bonus catch: flagged that OpenCode public docs do NOT list the 	ask tool (contract lives only in embedded 	ask.txt source - real maintenance risk)

**Follow-up edit applied:** added 1 sentence to gents_manager/SKILL.md line 377 making the rationale for fresh-context-per-dispatch explicit:

> 	ask() calls in this protocol always create a fresh specialist context; we deliberately do NOT pass OpenCode's 	ask_id between dispatches even when one is returned, because state carries through share/notes/ + 	asks/<id>.md instead.

This pre-empts the next person who notices the 	ask_id field exists in the tool output and tries to use it for context continuity (which would silently subvert the v0.13.0 context-isolation walls).

**Reversibility:** trivial. Delete the appended sentence at line 377.

**Not addressed (out of smoke-test scope):** the bonus catch about OpenCode public docs not listing the 	ask tool. That's a real concern but requires a separate maintenance phase (either pin the OpenCode version or move the 	ask contract into our own docs).


## 2026-07-05 - OpenCode 	ask tool contract documented in SKILL.md

**Source:** user picked option (b) on m0030 - address the OpenCode-docs gap that am-research flagged during the smoke test. Two fixes proposed: (1) pin OpenCode version, (2) move the 	ask contract into our own docs.

**Pick:** option 2. Ponytail reasoning:
- Option 1 (version pin) is heavier machinery (CI / pinning cadence / risk of breaking user's opencode CLI install). Wrong rung for the actual risk.
- Option 2 (documentation) captures our usage contract regardless of what Anomaly does upstream, is reversible in 30 seconds, and pre-empts the next reader who wonders where the contract comes from.

**Change applied:** added ### Runtime contract: OpenCode \	ask\ tool subsection at the end of ## Subagent dispatch contract in gents_manager/SKILL.md (between "Override: no per-task model selection" and "## Progress ledger").

**Content (8 lines):** name the contract surface we depend on (subagent_type, prompt, description, 	ask_id, returned 	ask_id), note that public OpenCode docs do NOT list the 	ask tool (contract lives only in embedded 	ask.txt source), and instruct to re-verify against the source if any dispatch behavior looks unexpected.

**Reversibility:** delete the new ### Runtime contract subsection. ~30 seconds.

**Not done:** the version pin (option 1). Stays available if a real breakage happens.
## 2026-08-05 — Book-Kit Tool Roadmap (T-2026-08-05-001) — 18 phases approved

**Source:** User directive. Two recommendation lists from past agents (city-of-memories fiction + ai-agents-with-python technical) cross-referenced against `book-kit` v1.1.0 inventory; produced 18-phase roadmap with cumulative ~15-day effort.

**Decision:** Build 18 phases sequentially (lowest-risk first) rather than in parallel. Each phase must pass 6-gate (tests / manual run / lint / frontmatter / docs / commit) before the next starts.

**Phase 9 simplifications locked:**
- **Exa:** MCP primary + built-in `websearch: "allow"` (dual-wired, already in `~/.config/opencode/opencode.json` at `https://mcp.exa.ai/mcp`)
- **Firecrawl:** add to global config (remote OAuth URL `https://mcp.firecrawl.dev/v2/mcp-oauth`, key `fc-919e9ffa4d82483b90dbfa434ec4fa46` in `.env.local`)
- **Brave:** dropped (no free API key)
- **DuckDuckGo:** thin Python wrapper (`scripts/duckduckgo_search.py` over `webfetch`)
- **`.env.local` convention** adopted as kit standard

**Book-kg backing:** SQLite (FTS5). 5× faster to ship than Neo4j, identical query API surface, no infra cost.

**Reversibility:** trivial. Each phase is one commit; rollback = revert commit. Plan is at `share/notes/02_plan_T-2026-08-05-001_book-kit-roadmap.md`.

**Ponytail note:** 18 phases not 18 separate kits. Phases 1–8 are script/template changes (kit improvements). Phases 9–14 are external tool integrations (MCPs/CLIs). Phases 15–17 are workflow doc updates. Phase 18 is the only true new infrastructure piece (FastMCP + SQLite). Kept the big lift last so smaller phases establish patterns first.
