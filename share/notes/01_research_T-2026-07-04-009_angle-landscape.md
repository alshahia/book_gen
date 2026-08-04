# Research — T-2026-07-04-009 (angle A: Landscape — prior art, theory, definitions)

**Date:** 2026-07-04
**Trigger:** initial — parallel-research angle A, dispatched by master
**Sub-agent:** am-research
**Angle:** Landscape only. No plan. No code. No edits under `agents_manager/`, `templates/`, `share/`, or root configs.

---

## Task in one sentence

Survey the existing landscape OUTSIDE this repo for tools and conventions that do "project → template" (codebase-as-output to scaffold a new project) and "project → core knowledge" (codebase-as-wisdom to steer future agents), then map the user's two collapsed sub-asks against what `agents_manager` already ships, before any planning/design begins.

## What we know for sure

### What `agents_manager` ships today (confirmed by read)

- **Templates (`templates/`)** — 4 of them: `_blank/`, `cinematic-landing/` (~1100-line skeleton, 14 memory files), `dashboard/` (12 memory files + skeleton), `docs-site/` (v0.1.0 scaffolding). All conform to `templates/AUTHORING.md` v1 (8 rules, folder-shape contract: `00-readme-first.md` + `INDEX.md` + `memory/` + `skeleton/` + `prompts/` + `decisions/` + `assets/MANIFEST.txt` + `tests/verify.sh`). Rules include trigger-line format on memory files, monotonic filenames, MANIFEST-must-resolve, skeleton-must-obey-memory (verified via `share/templates/cinematic-landing-fixes.md:1-337`).
- **Controller memory (`agents_manager/memory/`)** — schema in `agents_manager/memory/README.md:1-157`. Three scopes: `global/` (cross-project), `projects/<slug>/` (per-project), `<role>/notes/{semantic,episodic}/` (per-role). Append-only lifecycle; ≤20 lines/entry; secrets-free; frontmatter required (the template-memory cp-fence at `agents_manager/research/notes/semantic/template-memory-cp-fence.md:19-20` confirms `templates/<name>/memory/` is a separate lane with NO frontmatter).
- **Memory is currently empty** — `agents_manager/memory/global/.gitkeep` only, `projects/.gitkeep` only, `episodic/T-2026-07-03-001/002/003.md` are 3 prior research outputs. The schema and read/write protocol exist; the population is thin.
- **Pipeline (`agents_manager/SKILL.md:239-260`)** — parallel-research mode is opt-in and standard. This dispatch IS one of three parallel research angles.
- **Templates produce finished artifacts (landing pages, dashboards, docs sites).** They are NOT project-evaporation machines — they are scaffolding for greenfield projects. The user is asking for the inverse direction: take a finished project and recover a reusable shape.

### What the user's ask collapses (verbatim from `share/handoffs/00_user_task_T-2026-07-04-009.md:8-21`)

The user wrote one run-on paragraph containing two related-but-distinct capabilities and one implicit third. Master has formalized them as **A** (project → template), **B** (project → core knowledge), **C** (project → skill / subagent). The exact wording matters: "extract/convert to template tool/instruction" and "extract the most need/common/core part to guide other agents."

### Prior art landscape (verified + training)

The landscape splits into four clusters; none of them solve A+B+C together — each solves one piece. URL-verified today: spec-kit (404 stars → 118k stars in 12 months — GitHub-trending-adjacent), gitingest (15k stars), POML (4.9k stars), agents.md (60k+ projects). Other items below from training-only; flagged as such.

## What we don't know (ambiguities)

- **Q1 — Does the user want templates authored in *this* repo (`templates/` lane) or per-project extracts dropped into `share/templates/` or `agents_manager/memory/projects/<slug>/`?**
  - **Suggested clarifying question:** "When you say 'convert the current project to a template,' do you mean (a) hoist it into `templates/<name>/` next to cinematic-landing/dashboard for anyone to clone (strong contract, 8 rules, verify.sh), or (b) capture a project-local extract at `share/templates/<name>/` or `<project-slug>/` for use by THIS project only (lighter, no contract)?"
  - **Why this matters:** the two paths differ 10x in overhead — option (a) costs a full AUTHORING.md compliance pass + verify.sh; option (b) is a markdown dump. Choosing wrong wastes a phase.
- **Q2 — Is the "core knowledge to guide other agents" target agents-in-the-same-project (runtime memory) or agents-in-different-projects-but-same-domain (transferable knowledge)?**
  - **Suggested clarifying question:** "When you say 'guide other agents when used in another project to create a similar result,' do you mean (a) agents on project X benefit from notes captured during project Y (transferable across projects) or (b) agents in a fresh X-derived project get a starter pack specific to that domain (like a 'SaaS dashboard starter kit')?"
  - **Why this matters:** (a) is `agents_manager/memory/global/`; (b) is `templates/<name>/` minus the skeleton. Different ownership, different scopes.
- **Q3 — Is `share/templates/` (per-project extract) something the user knows exists already, or do they want a brand-new mechanism?**
  - **Suggested clarifying question:** "Are you aware `share/templates/cinematic-landing-fixes.md:1-337` already ships a per-project-extract pattern (template + fixes list), and you want that GENERALIZED, or is this a greenfield capability?"
  - **Why this matters:** if the answer is "generalize it," the work is one OPPORTUNITY-shaped addendum; if the answer is "fresh thing," scope is bigger.

## Risks and doubts

- **R1 — Capability-overlap with existing mechanisms.** `templates/_blank/` already gives a 0→1 scaffold, `templates/AUTHORING.md` already governs quality bar, `agents_manager/memory/{global,projects}/` already exists for cross-session memory, `share/templates/` already gives per-project artifacts, `share/notes/01_research_*` already captures per-task findings. A naive "extract to template" command risks duplicating all four without a clear discriminator. **Severity:** HIGH. **Mitigation:** the user's A vs B vs C distinction must be hardened; if it collapses back to "one tool that does it all," recommend the user reject and use existing mechanisms one-by-one instead.
- **R2 — IP / license contamination.** A "convert project → template" tool that grabs every source file risks carrying (a) vendor/NDA-encumbered code, (b) copyleft code (GPL/AGPL) into a template that downstream users would inherit, (c) accidentally copy dependencies' LICENSE files. The current `AUTHORING.md:139-160` MANIFEST rule only catches path resolution, not license cleanliness. **Severity:** HIGH. **Mitigation:** an extractor must run license-scan + dependency-graph + secret-scan before any file is promoted to `templates/<name>/skeleton/`; treat license-incompatible files as fails, not warnings.
- **R3 — Secrets exfiltration.** Many "extract" tools have shipped with accidental .env / .npmrc / *.pem / .ssh/id_rsa inclusions. The memory system explicitly forbids `share/notes/02_secrets_<task-id>.md` paths in memory entries (`agents_manager/memory/README.md:108-112`) — but a new extractor wouldn't be governed by that rule unless scoped under it. **Severity:** HIGH. **Mitigation:** declarative denylist (`.env`, `*.pem`, `*.key`, `id_rsa`, `credentials*`) before any output; secrets-detection regex sweep at verify-time.
- **R4 — Over-generalization (template too generic).** A button-press "extract" is statistically certain to produce a `templates/<name>/` so stripped of specifics that a downstream consumer can't ship a finished project from it. **Severity:** MEDIUM. **Mitigation:** the AUTHORING.md Rule 2 trigger-line format already requires specificity ("USE THIS WHEN: …") — borrow it; reject any auto-extracted memory file whose trigger-line is empty or contains only the topic noun.
- **R5 — Under-generalization (template so specific it's a clone).** Mirror image of R4 — the extractor keeps the project's brand colors, copy text, asset URLs, Pexels IDs (cinematic-landing-fixes.md Fix 7 is literally a "this skeleton uses the same image twice — replace one" ticket; see `share/templates/cinematic-landing-fixes.md:231-262`). **Severity:** MEDIUM. **Mitigation:** generalize-and-redact step (color tokens → neutral palette; brand strings → `{{brand_name}}`; Pexels IDs → image-role placeholders); ask user to confirm "the result should NOT visually match the source."
- **R6 — Template drift / staleness.** Every template ages. Extracted-into-template in 2026 will reference framework versions, asset CDNs, and patterns that age out. The current maintenance loop in `templates/AUTHORING.md:295-308` says "Update `INDEX.md` and `decision-log.md` in the same commit" but doesn't say WHO scans for drift or WHEN. **Severity:** MEDIUM. **Mitigation:** the existing `last_verified: YYYY-MM-DD` frontmatter + 90-day sweep (`agents_manager/memory/README.md:66-70`) is the right primitive; apply it to `templates/<name>/INDEX.md` too — but only if drift detection is something we explicitly want, otherwise add as a known-limitation.
- **R7 — User framing may be wrong.** The user said "extract to template tool/instruction" — but `templates/AUTHORING.md:11-12` calls a template "a reusable scaffold an agent clones to produce a complete artifact." If the source project IS itself already an instance of one of our templates (likely — am-planning uses templates for greenfield work), the "extract" is a degenerate operation: a clone-and-debrand of an existing template, and a new extract tool would just be a CLI around `cp -r templates/<src>/ templates/<new>/` plus a fill-the-blanks pass. The user's ask may collapse to "I want a CLI around template reuse." **Severity:** MEDIUM. **Mitigation:** Q1 above asks this directly; if confirmed, scope collapses 80%.

## Technical findings

### F1. Prior-art landscape — six clusters, no unified solution

A scan of the ecosystem turns up clusters A–F below. None of them solve A+B+C jointly; each cluster solves one piece. **The user's ask is novel in *combination*, not in any single leg.**

| Cluster | Tool / convention | What it does | URL | Verified |
|---|---|---|---|---|
| A. Template scaffolding (→ user's "A") | **GitHub spec-kit** | Spec-driven development CLI; `specify init` writes `.specify/memory/constitution.md` (governing principles) + `.specify/templates/{spec,plan,tasks}-template.md`; `/speckit.constitution` is the literal "extract principles from project, save them" command. Built-in `/speckit.tasks` and `/speckit.implement` execute downstream. 118k stars, MIT, current tag 0.12.4 (2026-07-02). Has *extensions / presets / bundles* layering. | https://github.com/github/spec-kit | VERIFIED |
| A. Template scaffolding | **cookiecutter** | Python template scaffolder; jinja2 substitution; `cookiecutter <repo-url>` produces a project. Strong prior art for "scaffold from a template," but solves only the OUTPUT side of the user's ask — it assumes the template already exists. | https://github.com/cookiecutter/cookiecutter (note: actual org is `cookiecutter/`, not `audreyfeldroy/`) | training-only |
| A. Template scaffolding | **giter8** | Scala/sbt-flavored template generator; templates hosted on GitHub under `g8<name>`. Same shape as cookiecutter; smaller ecosystem. | https://github.com/foundweekends/giter8 | training-only |
| A. Template scaffolding | **Yeoman generators** | The Node.js `generator-*` ecosystem. JS-flavored, npm-distributed. Same limitation as cookiecutter. | https://yeoman.io | training-only |
| B. Code-as-input to an LLM (→ upstream of both A and B) | **gitingest** | "Replace `hub` with `ingest` in any GitHub URL to get a prompt-friendly extract." Outputs a tree + concatenated file dump + token estimate; supports `--include-gitignored`. Closest prior art for "turn a project into LLM-ingestable text." Not a template; doesn't replace template authoring. | https://github.com/coderamp-labs/gitingest | VERIFIED |
| B. Code-as-input | **repomix** | The JavaScript equivalent of gitingest (NPM-published). Bundles a repo into one XML-tagged file for LLM context. | https://github.com/yamadashy/repomix | training-only |
| B. Code-as-input | **code2prompt** | Older code-to-prompt Rust tool, similar shape. | https://github.com/mufeedvh/code2prompt | training-only |
| C. Declarative agent instruction formats (→ user's "C" + adjacent to "A") | **AGENTS.md convention** | "A simple, open format for guiding coding agents." README-equivalent for AI agents; nearest-in-tree file wins. 60k+ OSS projects use it. Standardized via `agents.md` spec; now stewarded by Agentic AI Foundation (LF). | https://agents.md/ | VERIFIED |
| C. Declarative agent instruction formats | **Anthropic Skills (Claude Code)** | The SKILL.md convention. A skill is a folder with a `SKILL.md` trigger-frontmatter file (YAML `name` + `description`) that the agent activates when relevant; cascading skills via `paths:` glob. Closest prior art for the user's "C" — narrow, single-purpose, agent-loadable instruction. | https://github.com/anthropics/skills | training-only |
| C. Declarative agent instruction formats | **Cursor .cursorrules** | Single-file per-project instruction convention for Cursor IDE. Lightweight (one file, no schema). | https://docs.cursor.com/context/rules | training-only |
| C. Declarative agent instruction formats | **Microsoft POML** | "Prompt Orchestration Markup Language" — HTML-like markup (`<role>`, `<task>`, `<example>`, `<document>`, `<table>`, `<img>`) with CSS-like styling and a templating engine (`{{ }}`, `for`, `if`). Companion VS Code extension + Node/Python SDKs. 4.9k stars, MIT, v1 cited as arXiv:2508.13948. Solves structured *prompt authoring* — closer to (C) than to (A) or (B). | https://github.com/microsoft/poml | VERIFIED |
| D. Agent memory (→ user's "B") | **Letta / MemGPT** | Memory-augmented LLM agents; `memory_blocks` (in-context, always-loaded) + `archival_memory` (vector store) + `recall_memory` (conversation search). Closest prior art for "project → extracted wisdom = memory blocks"; but the *unit* is a per-agent scratchpad, not per-project. | https://github.com/letta-ai/letta | training-only |
| D. Agent memory | **mem0** | Production memory layer for LLM apps; "self-improving memory" that extracts facts from conversations. Closer to "episodic → semantic" distillation than to project templates. | https://github.com/mem0ai/mem0 | training-only |
| E. Spec / plan-artifact tooling (→ adjacent to "A") | **GitHub spec-kit** (above) plus ad-hoc competitors: TaskMaster, Kanban-md, Bmad-method. spec-kit is the canonical "spec → executable plan" pipeline; the closest competitor is `ddb` (data-driven-bug) for spec-as-test. | (see row 1) | (see row 1) | (see row 1) |
| F. Anthropic prompt caching / context engineering | Anthropic docs on prompt caching + the broader "context engineering" framing by Anthropic (long-context best practices). Tangential — establishes that *what you put in context matters as much as the model*. Reinforces why (B) matters: the right "core knowledge" turns the agent from guessing to using evidence. | https://docs.anthropic.com/en/docs/build-with-claude/prompt-caching | training-only |

**Synthesized relevance to the user's ask:**
- **(A) Project → Template** is closer to *spec-kit + cookiecutter* than to anything else. spec-kit's `/speckit.constitution` is the closest analog of "extract project principles → save → apply later." cookiecutter/giter8 are the *output* side; spec-kit also handles the *extraction* side via constitution/spec/plan/tasks.
- **(B) Project → Core knowledge** has no clean analog. Closest are Letta's memory blocks (but per-agent, not per-project) and mem0 (per-conversation, not per-project). `agents_manager/memory/projects/<slug>/` is already the closest existing analog — it just isn't populated yet.
- **(C) Project → Skill / Subagent** maps cleanly to **Anthropic Skills** (SKILL.md with YAML trigger frontmatter) and **AGENTS.md** (instruction convention) and **Cursor .cursorrules** (single-file). POML is the structured-prompt cousin.

### F2. Definitional refinement of the three collapsed concepts

Master split the user's ask into A/B/C. Each maps to different prior art and to different `agents_manager` mechanisms. The discriminators are **size, completeness, and lifecycle**:

| | (A) Project → Template | (B) Project → Core knowledge | (C) Project → Skill / Subagent |
|---|---|---|---|
| **Output unit** | A `templates/<name>/` folder (full contract) | A set of `agents_manager/memory/projects/<slug>/*.md` entries + optional `agents_manager/memory/global/*.md` | A folder with `SKILL.md` (frontmatter + body); possibly shippable to `agents_manager/<role>/skills/` |
| **Size budget** | Hundreds to ~2000 lines; tested by `verify.sh` | ≤20 lines/entry; memory-size-cap enforced | Tens to ~200 lines; trigger-line frontmatter required |
| **Lifecycle** | Versioned (v0.1.0 → v0.13.0+); `decision-log.md` append-only; 90-day `last_verified` sweep ideally | Append-only; `last_verified: YYYY-MM-DD`; superseded-by-pointer; sweep at >90 days | Append-only versioned folder; updated in place; discoverable via `description:` frontmatter |
| **Consumption path** | Specialist reads `INDEX.md`, follows `memory/01-builder-flow.md`, runs `verify.sh` | Specialist reads on re-entry per the read-on-entry protocol (`agents_manager/memory/README.md:75-83`) | Agent loads on demand when description matches context |
| **Closest prior art** | cookiecutter / spec-kit / giter8; AUTHORING.md | Letta memory blocks; mem0 facts | Anthropic Skills SKILL.md; AGENTS.md; Cursor .cursorrules |
| **Already in this repo?** | YES — `templates/{_blank,cinematic-landing,dashboard,docs-site}/`. The gap is *the extraction tool*, not the destination. | PARTIALLY — `agents_manager/memory/{global,projects}/` exists, schema finalized (memory/README.md), but **0 entries**. Mechanism exists; population is empty. | PARTIALLY — `agents_manager/<role>/SKILL.md` is the same shape as a Claude-Code skill (no frontmatter yet, but the convention is well-established). Sub-agent skills (the narrow, single-purpose kind) do NOT exist in this repo. |

### F3. The "where it lives" decision is partially already made

The `agents_manager/memory/README.md:115-116` fence explicitly says: **"Do NOT write into `templates/<name>/memory/`. That's the template author's lane."** This means there is *already* a discriminator between (A) and (B):
- Template memory is *runtime-task playbook content* (how to build a hero with aura + cutout): per-template, domain-specific, no controller-memory frontmatter.
- Controller memory is *cross-session, cross-task wisdom* (e.g., "test spritesheet `data-section` claim before shipping template"): frontmatter required, secrets-free, size-capped.

**Pull the user's (B) ask into `agents_manager/memory/projects/<slug>/`** and the schema + discipline are already there. **Pull (A) into `templates/<name>/`** and the AUTHORING.md contract is already there. The unsolved problem is *the EXTRACTION, not the STORAGE*.

### F4. Existing mechanisms the user's ask would overlap with — map

| Existing mechanism | Already covers for (A) | Already covers for (B) | Already covers for (C) |
|---|---|---|---|
| `templates/_blank/` + `templates/AUTHORING.md` | YES — the scaffold + the contract | NO (templates don't carry wisdom across projects) | NO |
| `agents_manager/memory/global/` + `agents_manager/memory/projects/<slug>/` | NO (memory doesn't carry scaffolding) | YES — schema is finalized, just empty. See `agents_manager/memory/README.md:1-157`. | NO (skill-folder shape is different from memory-file shape) |
| `agents_manager/research/notes/{episodic,semantic}/` | NO | PARTIAL — per-task research notes capture findings, but role-scoped, not project-scoped, and not designed for cross-task wisdom | PARTIAL — semantic notes ARE a kind of skill (curated expertise); the v0.14.0+ contract (`<role>/notes/semantic/*.md` with frontmatter) is skill-shaped |
| `share/templates/cinematic-landing-fixes.md` | YES — this is an extracted-from-project template-fixes doc in all but name. Demonstrates the pattern. | YES — also captures decisions/pitfalls | NO |
| `share/notes/01_research_*.md` | NO (research doesn't produce templates) | PARTIAL — captures per-task findings, partial duplication risk with `notes/episodic/` | PARTIAL — research SKILL is a Claude-Code skill by every other name |
| `share/notes/99_decisions_*.md` (decision log, append-only) | YES — a new template's `decision-log.md` IS a 99_decisions file under a new name | YES — captures project decisions across phases | NO |

**Bottom line:** for (B), the storage exists. For (A), the contract exists but requires manual AUTHORING.md walk. For (C), the shape exists informally (SKILL.md files in each role's folder) but lacks the Yaml frontmatter trigger convention that would make them discoverable as skills.

### F5. Theoretical grounding (SE / AI literature)

Honest read: I do NOT have off-the-top citations from SE/AI literature specifically on "project → template extraction" or "codebase → agent knowledge" as a named problem. The closest published framings I can point to with confidence are:

- **Knowledge transfer in software engineering** — classical SE literature treats cross-project knowledge transfer as a recognized problem (e.g., organizational learning, lessons-learned systems). Cited as "Boh et al. 2007 — Recomposition in Practice" and "Dingsøyr et al. 2009 — Knowledge management in software engineering" via training-only recollection. **Honest caveat:** I have not verified these citations and they may be wrong; treat as LOW confidence.
- **Case-based reasoning (CBR)** — AIPL/SE literature on CBR speaks to "adapt prior solutions to new problems," which is the structural ancestor of template-and-configure. The CBR framing is decades old; I have not pulled a specific 2024+ reference.
- **Code-as-corpus for LLMs** (training-data provenance, code licensing, dataset curation) — a current and well-discussed problem (e.g., the BigCode project, "The Stack" v2 papers, license contamination studies). Adjacent to F1's IP risk (R2) rather than to the construct directly.
- **Few-shot / in-context learning + retrieval-augmented generation** — the *theoretical* parent of "give an agent a memory of prior work." Standard references: Lewis et al. 2020 (RAG original); for structured retrieval, "Self-RAG" (Asai et al. 2023). These support (B)'s framing but do not address the codebase → memory operationalization.

**Honest status:** the prior art here is *practitioner literature* (blogs, GitHub READMEs, conference talks) rather than peer-reviewed papers. I have not done the academic-literature scan this question deserves; flag for review if the team wants peer-reviewed grounding.

### F6. Self-critique on the landscape angle

- What I did NOT verify: cookiecutter's exact org (recall mismatch — likely `cookiecutter/cookiecutter`); anthropic/skills exact repo contents (training-only); Letta/mem0 current state.
- What I should have checked but did not: existing `share/notes/02_plan_*` files for prior context-gen tasks that may have explored similar tooling (would have read at most 2 of them — based on the file listing there are 9 plans; I skimmed titles only).
- The angle is landscape-only. The other two angles (architecture / operations) will surface WHERE the tool would live and HOW it triggers. This angle does NOT need to answer those; defer.

## Feasibility verdict

- **Can do:** partial — the **mechanisms exist** (templates/ + memory/ + SKILL.md convention); the **extraction tool does not**, and the user's framing of "one tool that does extract-to-template AND extract-to-knowledge" risks overlapping with all three existing mechanisms without a discriminator.
- **Confidence:** MEDIUM. Verified by direct read of `templates/AUTHORING.md` (332 L), `agents_manager/memory/README.md` (157 L), `share/templates/cinematic-landing-fixes.md` (337 L), prior 4 research outputs (titles only). Unverified: how the user would actually invoke an extract tool, whether they're aware `share/templates/` already exists as a per-project-extract lane, and whether they'd accept a "no new tool, just use existing mechanisms in sequence" recommendation. Q1-Q3 above flip the answer.
- **Why:** The most-likely-honest answer based on the existing infrastructure is "the user is asking for a CONVENIENCE LAYER over mechanisms that already exist." A new tool/instruction risks becoming another BFG anti-pattern (browser-use favicon-thrower-stack) that does a worse job than the three existing mechanisms used one-by-one: `templates/<name>/` for greenfield scaffolds, `agents_manager/memory/projects/<slug>/` for cross-task wisdom, `agents_manager/<role>/skills/<name>/SKILL.md` for narrow single-purpose instructions. The right research question for the master is not "what should the extract tool look like?" but "does the user accept that the existing mechanisms are sufficient if surfaced as a 3-step recipe?"

## Recommendations for the planning agent

(Note: planning agent's lane. These are observations am-research is qualified to make; NOT a plan.)

1. **Hard-discriminate A/B/C before designing anything.** The user's two sub-asks collapse three products into one paragraph. Master must surface the distinction back to the user (Q1+Q2 above), and the plan should treat A, B, C as three independent deliverables each evaluated against existing mechanisms, before any new code is scoped. The current task tracker at `tasks/T-2026-07-04-009.md:21-25` lists only two research angles (architecture + operations) but the user's ask really has three (A/B/C) plus the synthesis — master may want a fourth research angle or split the existing ones along A/B/C lines.
2. **Consider the "no new tool" branch seriously.** If Q1 resolves to "yes, awareness of `share/templates/` is enough," the entire implementation is a README + a 4-line `agents-manager` subcommand recipe. This is the laziest path (Ponytail: rung 1 — does this need to exist at all?). Run that branch first.
3. **If a new tool IS warranted, position it as a meta-tool, not a destination.** The extract tool should *write into* `templates/<name>/` and `agents_manager/memory/projects/<slug>/` — it should NOT introduce a fourth storage location. (R1 mitigates.)
4. **Treat license + secrets as design-time gates, not review-time patches.** R2 + R3 are HIGH severity; both are categorically cheaper to design into the contract up front than to retrofit. (Ponytail: think first, lazy later.)
5. **Borrow the spec-kit structure literally.** `/speckit.constitution` + `.specify/memory/constitution.md` is the cleanest published prior-art of "principles extracted from a project, persisted as a discoverable file, applied on subsequent projects." Re-inventing this without acknowledging spec-kit is a missed opportunity.
6. **Drop the `references` to AGENTS.md / spec-kit / poml into a `## Companion tools` section of any new extract-tool docs.** Establishes upward-compatibility.

## Open questions for the user

1. **(Q1)** When you say "convert the current project to a template," do you mean (a) hoist it into `templates/<name>/` next to cinematic-landing/dashboard for ANYONE to clone (strong contract, 8 rules, `verify.sh`), or (b) capture a project-local extract at `share/templates/<name>/` or `<project-slug>/` for THIS project only (lighter, no contract)?
2. **(Q2)** When you say "guide other agents when used in another project to create a similar result," do you mean (a) agents on project X benefit from notes captured during project Y (transferable, → `agents_manager/memory/global/`), or (b) agents in a fresh X-derived project get a starter pack specific to that domain (→ `templates/<name>/` minus skeleton)?
3. **(Q3)** Are you aware `share/templates/cinematic-landing-fixes.md` already exists as a project-extract pattern (template + concrete fixes list), and you want that **generalized**, or do you want a brand-new capability that does NOT lean on that pattern?
4. **(Q4 — bonus, if you want to answer)** Is there any example of a real project you ran with agents-manager that you'd want to extract from? If yes, naming it lets the architecture and operations angles test their designs against a concrete case study instead of an abstract workflow.

## Cross-role perspectives

### From am-research

- The user's framing collapses three product concepts into one paragraph. **The first priority of this whole research effort is to disaggregate them** — every prior-art survey answers differently depending on whether (A), (B), or (C) is the real ask.
- The strongest *practitioner* references are spec-kit (closest analog of "extract project constitution then re-apply"), AGENTS.md (closest analog of "agent instruction convention"), and Anthropic Skills (closest analog of "narrow single-purpose skill"). None of these solve A+B+C jointly.
- The strongest *theoretical* support is structural (the schema for (B) is already designed, per `agents_manager/memory/README.md`; the discipline for (A) is already designed, per `templates/AUTHORING.md`), not academic literature. I have not pulled peer-reviewed citations; flag the gap (F5).
- **Pushback on the framing if needed:** a one-shot "extract" tool may be over-engineered. `templates/_blank/` is the lazy answer for greenfield, `agents_manager/memory/` is the lazy answer for cross-task wisdom, `SKILL.md` convention is the lazy answer for narrow instructions. If those three together cover the use case, no new tool is needed — only a recipe.

### From am-coder

(Lazy-senior voice.)

- **What's realistically extractable from source?** Reading from the existing exemplar is the right reference:
  - `templates/cinematic-landing/skeleton/` is **1097 lines of HTML/CSS/JS** with full GSAP/ScrollTrigger wiring — that's the kind of "starter skeleton" an extract tool would emit. Every line is contest-worthy; some honor pre-existing memory rules, some violate them (see `share/templates/cinematic-landing-fixes.md` Fix 7 — image collision at lines 208+490).
  - `templates/cinematic-landing/memory/*.md` is 14 prose contracts that codify decisions the source skeleton doesn't make on its own (e.g., "never `filter: blur()` and reuse the same image as a cutout"). **These memory files are not derivable from source code; they're derivable from the decisions log + reviewer findings.** An extractor that only reads code will miss them entirely.
  - Build/run commands: `templates/cinematic-landing/tests/verify.sh` is a 30-line grep-based self-check. **Trivially extractable.**
  - **The line where extraction becomes "fork the project":** as soon as the source has feature-specific tokens that no longer make sense (Apothecary Light's gold-deep hex vs. a neutral palette; "Maison Lumen" brand string vs. `{{brand_name}}`), the extractor MUST either generalize (replace with placeholders) or refuse (output a fork notice). R5 covers this.
- **What's NOT extractable without human review:** dependency manifests that pin versions (need a "supported version range" decision), LICENSE files of dependencies (need a license-clean scan — R2), secrets (denylist before any output — R3).
- **Realistic deliverable shape:** a `agents-manager extract` subcommand (or a one-shot `scripts/extract-template.sh`) that takes (source repo path, target template name, target destination) and emits a `templates/<name>/` skeleton AFTER passing through: license scan → secret scan → dependency clean → generalization pass → verify.sh dry-run on the output. This is **one round-trip with reviewable diffs**, not a magic button.
- **The "lazy" implementation:** three scripts wired in sequence. No abstractions. README + 30-line Makefile-replacement. Total new code: roughly 200–400 lines of bash + Python (license-scan can shell out to `reuse` or `scancode-toolkit`; secret-scan shells to `gitleaks` or `trufflehog`).

### From am-review

(Brutally-honest voice; review is the gate that catches what the other three miss.)

- **What I would validate before shipping an extracted template:**
  1. **MANIFEST resolves.** Every line of `assets/MANIFEST.txt` must point to a file that exists in the working tree. Currently fails on the cinematic exemplar (`share/templates/cinematic-landing-fixes.md` Fix 8 — the manifest references `agents_manager/assets/` subtree that doesn't exist).
  2. **`bash templates/<name>/tests/verify.sh` exits 0.** Same script, run as the acceptance gate. The extracted template must PASS the same checks as a manually-authored one.
  3. **Every memory file has a trigger line** matching AUTHORING.md Rule 6: `# NN · <topic> — USE THIS WHEN: <one-line>`. Any auto-extracted memory without a meaningful trigger line is rejected (R4).
  4. **`tools/license-scan` (reuse / scancode-toolkit) emits no HIGH or CRITICAL findings on the skeleton.** R2 — license contamination is a templating hard-stop, not a warn.
  5. **`gitleaks detect --no-banner` exits 0.** R3 — secrets are a templating hard-stop.
  6. **No brand-identifying strings in the skeleton.** Spot-grep for the source project's brand name; if found, either generalize (R5) or reject.
  7. **No monorepo-only manifests in the MANIFEST.** No `pnpm-workspace.yaml`, `lerna.json`, `nx.json`, `turbo.json`, etc. unless the extract target is explicitly another monorepo.
  8. **`INDEX.md` lists every convention the skeleton demonstrates.** Reverse-derive the INDEX from the skeleton, not from the source — if a convention exists in source but not in INDEX, it didn't survive the extract.
- **What I would reject on sight:** extracted templates that ship without a `tests/verify.sh` (means the author didn't trust their own output enough to test it); templates whose memory files are longer than the skeleton (means the wisdom was kept, the proof was discarded); templates that don't carry their `decision-log.md` (means the why-not-what is gone, and the next maintainer has no way to learn from the project's decisions).
- **The single most-likely failure mode:** the extractor ships a template that PASSES its own `verify.sh` but is unusable because the *trigger lines* on memory files are domain-noun-only ("cinematic-hero") without a USE-WHEN clause (R4 in disguise). Review must grep for `USE THIS WHEN:` and reject any memory file missing it.

## Self-critique

- **Did I do my job?** partial — I surveyed the landscape and surfaced the A/B/C distinction the user's framing collapsed. I did NOT deliver peer-reviewed academic citations (F5); I did NOT verify all prior-art URLs (spec-kit, gitingest, POML, agents.md verified; cookiecutter, Letta/mem0, Anthropic Skills from training only). I did NOT produce a definitive answer to the user's framing — I'm skeptical the user needs a new tool at all, and I named that skepticism as a push-back rather than scoring it.
- **What might I have missed?**
  - The existing 9 `share/notes/02_plan_*` files (I listed titles, did not read). One or more may have explored similar territory.
  - Real-world extracts done elsewhere (gstack, ad-hoc author shells, etc.) — there may be a corp-of-work I missed.
  - Anthropic's "Building effective agents" / "Context engineering for agents" essays — adjacent, possibly too recent to be confident about exact wording.
  - The user's actual project they want to extract FROM — without an example project I cannot critique the extraction against real failure modes.
- **What did I assume without evidence?**
  - That the user wants the tool because the existing mechanisms feel insufficient (assumption; they may just not know about the mechanisms).
  - That the existing `agents_manager/memory/` schema is the right destination for (B) (assumption; the user hasn't said they accept controller memory as the storage).
  - That author-of-extract is am-coder (the task tracker's P3T1+ rows are "TBD"; the role assignment hasn't been made).
  - That no academic literature specifically addresses this — I stated it as LOW confidence rather than proving the absence.

---

## Metrics

- findings: 6
- risks_HIGH: 3
- risks_MEDIUM: 4
- risks_LOW: 0
- clarifying_Qs: 4
