# agents-manager

[![CI](https://github.com/ahmadmhmdsy/agents-manager/actions/workflows/ci.yml/badge.svg)](https://github.com/ahmadmhmdsy/agents-manager/actions/workflows/ci.yml)
[![Release v0.16.0](https://img.shields.io/badge/release-v0.16.0-blue)](https://github.com/ahmadmhmdsy/agents-manager/releases/tag/v0.16.0)
[![License MIT](https://img.shields.io/badge/license-MIT-green)](LICENSE)
[![Upstream patch contributions](https://img.shields.io/badge/upstream-2%20patches-purple)](docs/UPSTREAM-CONTRIB.md)

> **Status:** v0.16.0 — soft walls + adaptive orchestration (pipeline is default shape, not absolute rule). API may change between minor versions until v1.0.0.

A multi-agent task orchestration system built on [OpenCode](https://opencode.ai)'s agent system. One **master agent** routes work through **six specialist agents** (research → planning → design → assets → coder → review), each with its own context window and a dedicated role.

## Book Kit

Want the **7-phase book-writing pipeline** on another laptop without the full controller? `book-kit/` is a portable ZIP that ships only what book-gen needs. See `book-kit/README.md` and the artifact at `dist/book-kit-0.1.0.zip`.

## Quick install

The fastest way to bootstrap agents-manager into any project. One command per platform:

| OS | Command |
|---|---|
| Windows (PowerShell) | `iwr -useb https://raw.githubusercontent.com/ahmadmhmdsy/agents-manager/main/bin/standalone-installer/install.cmd -OutFile install.cmd; .\install.cmd` |
| Windows (cmd / double-click) | Save <https://raw.githubusercontent.com/ahmadmhmdsy/agents-manager/main/bin/standalone-installer/install.cmd> → right-click → "Save Link As" → double-click the saved `install.cmd` |
| macOS / Linux | `curl -fsSL https://raw.githubusercontent.com/ahmadmhmdsy/agents-manager/main/bin/standalone-installer/install.sh \| bash` |

See [`bin/standalone-installer/README.md`](bin/standalone-installer/README.md) for the full flag set (`--target`, `--version`, `--skills`, `--git`, `--dry-run`). For alternative install paths (git subtree, release ZIP, manual copy), see [Quick start](#quick-start) below.

## Table of contents

- [Why](#why)
- [At a glance](#at-a-glance)
- [Optional flags](#optional-flags)
- [What's new in v0.16.0](#whats-new-in-v0160)
- [What's new in v0.15.0](#whats-new-in-v0150)
- [What's new in v0.14.1](#whats-new-in-v0141)
- [What's new in v0.14.0](#whats-new-in-v0140)
- [What's new in v0.13.0](#whats-new-in-v0130)
- [What's new in v0.12.1](#whats-new-in-v0121)
- [What's new in v0.12.0](#whats-new-in-v0120)
- [What's new in v0.11.0](#whats-new-in-v0110)
- [What's new in v0.10.0](#whats-new-in-v0100)
- [What's new in v0.9.0](#whats-new-in-v090)
- [What's new in v0.7.0](#whats-new-in-v070)
- [What's new in v0.6.0](#whats-new-in-v060)
- [Pipeline](#pipeline)
- [The seven agents](#the-seven-agents)
- [Permissions model](#permissions-model-v050--soft-walls)
- [Operational characteristics](#operational-characteristics-v051)
- [Quick start](#quick-start)
- [Examples](#examples)
- [Required user-level skills](#required-user-level-skills)
- [Usage](#usage)
- [Repo layout](#repo-layout)
- [FAQ](#faq)
- [Contributing](CONTRIBUTING.md)
- [Releases](#releases)
- [License](#license)
- [Status](#status)

## Why

Generic AI assistants collapse too many roles into a single chat: research, planning, coding, and review share context and bleed into each other. **agents-manager** enforces role separation through **separate context windows** + **soft walls declared in each agent's `SKILL.md`**. Each specialist:

- Runs in a fresh context window (no cross-contamination).
- Reads its `SKILL.md` boundaries (and the inline prompt's Can/Can't list) to decide what to do.
- Returns a file artifact (no out-of-band chat).
- Self-critiques before returning.

The master enforces `max_fix_loops = 3` and pauses for user confirmation between planning and build. In v0.5.0+, walls are soft contracts (prose + LLM discipline) rather than OpenCode permission-layer enforcement. See [`docs/PERMISSIONS.md`](docs/PERMISSIONS.md) for the rationale.

## At a glance

```
            ┌──────────────────┐
            │  master (orch.)  │
            │  routes + gates   │
            └────────┬─────────┘
                     │ task(subagent_type=…)
        ┌────────────┼────────────┬─────────────┐
        ▼            ▼            ▼             ▼
   ┌─────────┐  ┌──────────┐  ┌─────────┐  ┌──────────┐
   │research │  │ planning │  │  coder  │  │  review  │
   │ (R)     │  │ (P)      │  │ (C)     │  │ (R)      │
   └────┬────┘  └─────┬────┘  └────┬────┘  └────┬─────┘
        │            │            │            │
        ▼            ▼            ▼            ▼
   share/notes/01_   …02_      …03_         share/reports/04_
              ▲                                 │
              └────────── tasks/<id>.md ───────┘
                       (canonical task tracker)
```

**Bus:** `share/notes/`, `share/handoffs/`, `share/reports/`, `share/messages/` — inter-agent communication.

**Flags** (set in `tasks/<id>.md` header, see [Optional flags](#optional-flags)): `auto_accept_warns`, `git_initialized`, `phase_5_enabled`, `run_smoke_at_close`.

## Optional flags

Set in the `## Optional flags` block of `tasks/<task-id>.md`. Master sets these at Phase 0 Ingest; sub-agents read-only.

| Flag | Default | Set when | Effect |
|---|---|---|---|
| `auto_accept_warns: bool` | `false` | User says "I trust the triageable list" | Master auto-appends matching WARNs to register with `[auto-accepted triageable]` tag, no user prompt |
| `git_initialized: bool` | `false` | User accepts Phase 0 git-init prompt | Records whether master initialized git in this task |
| `phase_5_enabled: bool` | `false` | User wants next-steps prompt at task close | Master enters Phase 5 (auto-detects git vs non-git menu) |
| `run_smoke_at_close: bool` | `true` (when API key provided) | API key given in Phase 0 | Master runs `npm run smoke` in its own session at Phase 4 review time |

All flags default to safe values. Users opt in to enable features. Schema documented in [`tasks/README.md`](tasks/README.md) § Optional flags.

## What's new in v0.16.0

**Adaptive orchestration.** Pipeline reframed as a default shape, not an absolute rule. Five authority levers for the master: (1) **complexity triage** — trivial / one-step / standard / complex maps to direct / single-dispatch / pipeline / pipeline+adapt; (2) **re-dispatch any specialist any number of times** — phase boundaries are not single-use gates; (3) **run specialists in parallel** — research + explorer + designer co-existing is the norm for complex work; (4) **apply review to any artifact** — plan, brief, design, not just code; (5) **propose better solutions proactively** — surface alternatives with full reasoning before acting. Every specialist now self-validates, proposes better, and surfaces cross-lane. See [`share/notes/99_decisions.md`](share/notes/99_decisions.md) for the 5 decisions logged on 2026-07-05.

## What's new in v0.15.0

**`agents_manager/extract/` specialist.** Extract-to-template recipe moved into its own specialist at `agents_manager/extract/`. Closes the WARN-9 fix-loop from [`share/reports/04_review_T-2026-07-03-003.md`](share/reports/04_review_T-2026-07-03-003.md). See commit `d71305d`.

## What's new in v0.14.1

**`am-research` enhancements (additive).** No breaking changes. Populates `agents_manager/research/resources/` with 6 starter files, seeds `notes/episodic/` with 3 backfilled entries, and adds 2 protocol sections + 2 rules (confidence scoring + wrong-specialist handoff) to `am-research`. Ships `scripts/backfill-research-metrics.sh` (stdlib-only, idempotent). Closes the 8 gap categories surfaced by `T-2026-07-04-004`. Full entry in [`agents_manager/CHANGELOG.md`](agents_manager/CHANGELOG.md).

## What's new in v0.14.0

**`cinematic-landing` template promoted to PASS + `templates/AUTHORING.md` v1.0.0.** The 9 review-driven fixes from `share/templates/cinematic-landing-fixes.md` all landed. Ships a `templates/_blank/` starter, `templates/CONTRIBUTING.md`, per-template `INDEX.md` (3-step consumer walkthrough), and per-template `tests/verify.sh` (8 grep-oracle tests). All 14 `memory/*.md` carry `USE THIS WHEN:` trigger-line coverage. Full entry in [`agents_manager/CHANGELOG.md`](agents_manager/CHANGELOG.md).

## What's new in v0.13.0

**Three-scope memory system (`agents_manager/memory/`).** Global + project + role scopes; single canonical schema at `agents_manager/memory/README.md`; read-on-entry (`≤200 L/scope`); write-on-exit (≤20 L/entry + durable-insight filter); ships `scripts/validate-memory.sh` as a release blocker. 90-day sweep flag at Phase 5 close. 6 specialist SKILL.md updates. Full entry in [`agents_manager/CHANGELOG.md`](agents_manager/CHANGELOG.md).

## What's new in v0.12.1

**v2-axis memory files integrated + source `PROPOSED_PATCH.md` §F sync.** 4 source memory files (canvas-a11y, reduced-motion-listener, keyboard-nav, dark-theme) moved into `templates/cinematic-landing/memory/` as files 11-14. Skeleton extended ~286 LOC to absorb v2 axes (FOUC + dark theme + DPR + JS controller + a11y). `cinematic-landing-kit-demo/` copied to repo root for traceability. Full entry in [`agents_manager/CHANGELOG.md`](agents_manager/CHANGELOG.md).

## What's new in v0.12.0

**`cinematic-landing` task template + `am-assets` specialist.** Ships `templates/cinematic-landing/` (17 files: 9 memory + 1 skeleton + 3 prompts + decisions + assets schema + MANIFEST). Adds **6th specialist** — `am-assets` asset gatekeeper, sits at Phase 3a between Planning and Build, runs the 4-branch runtime decision tree (video pipeline / video file / stills only / nothing). Multi-LLM neutral by design (works with Midjourney / DALL-E / Sora / Runway / Veo / Stable Diffusion / Replicate / Higgsfield / local models). 5 hard rules for cinematic-landing builds ship in [`agents_manager/assets/resources/landing-review-checklist.md`](agents_manager/assets/resources/landing-review-checklist.md).

## What's new in v0.11.0

**Python UX + standalone installer + skills scope override.** `bin/agents-manager.py` (stdlib only, ~380 LOC) wraps the existing bash + PowerShell dispatchers with an interactive wizard. Zero-dependency standalone installer at `bin/standalone-installer/install.{py,sh,cmd}` lets users bootstrap agents-manager into any project from a single URL. `--global/--local/--both/--skip` flags on `agents-manager skills add` (was implicit-only before).

## What's new in v0.10.0

**Unified dispatcher (`agents-manager` CLI).** Three install paths now share a single dispatcher contract: `bin/agents-manager` (bash), `bin/agents-manager.ps1` (PowerShell), `bin/agents-manager.py` (Python UX). One entry point per platform covers `install` / `check` / `update` / `lint` / `version` / `release` / `skills list|add|which|update`. CI `chmod +x` discipline added; `.cmd`/`.bat` shim layer kept. Pre-commit dispatcher-lint hook enforced.

## What's new in v0.9.0

Three new features from the Part 2 upstream-contribution patch (chunk-size protocol, builds on v0.6.0):

- **Per-phase complexity estimation (planner)** — every phase in `02_plan_phases_<task-id>.md` gets a `### Complexity` block: novel abstractions, LOC/files estimates, review-difficulty word, split recommendation + reason. Hard triggers (LOC > 1200 OR files > 15 OR ≥2 novel abstractions) force `split_recommended: true`.
- **Master re-ask protocol at dispatch** — before dispatching am-coder, master reads the Complexity block; can re-ask planner ≤ 2× with concrete feedback; has final say. Each dispatch decision lands in `## Loop history` (appended to `tasks/<task-id>.md`) for auditability.
- **Phase productivity metric** — `tasks/README.md` Phase timings table gets `LOC written` + `WARNs` columns; new `## Phase productivity` block at close with LOC/WARN ratio as a sanity check, not a score.

Seed list for novel abstractions lives in [`agents_manager/planning/resources/novel-abstractions-seed-list.md`](agents_manager/planning/resources/novel-abstractions-seed-list.md) — extend it as you encounter new patterns (it lists 8 curated + a "NOT" list of patterns that look novel but aren't).

## What's new in v0.6.0

Six new features from an upstream-contribution patch ([`docs/UPSTREAM-CONTRIB.md`](docs/UPSTREAM-CONTRIB.md)), all opt-in by default:

- **WARN register** — `share/notes/04_warns_register_<task-id>.md` consolidates per-phase WARNs into one file, so the user is asked once at task close instead of once per phase.
- **Git-status + API-key preflight at Phase 0** — master asks about `git init` (default no) and external API keys (stored in gitignored `share/notes/02_secrets_*.md`).
- **Per-phase fix-loop counter** — `Fix-loops by phase: {P1: 0, P2: 0, ...}` + total in tasks/README.md.
- **Phase 5 non-git menu** — auto-detects git vs non-git at task close; sandbox projects get a 4-option menu (run smoke / polish WARNs / build follow-up / close out) instead of dead-branching on merge/PR.
- **Browser visual preflight** (opt-in when browser tools are available) — master takes screenshots before review for UI phases.
- **Optional flags** ([see table above](#optional-flags)) — `auto_accept_warns`, `git_initialized`, `phase_5_enabled`, `run_smoke_at_close`.

## Pipeline

```
USER TASK
   │
   ▼
[0] INGEST       ← master captures the task verbatim
   │
   ▼
[1] RESEARCH     ← am-research: analyze, doubt, surface unknowns
   │              ↓ may ask user clarifying questions
   ▼
[2] PLANNING     ← am-planning: phased plan + Complexity block per phase (v0.7.0+)
   │              ↓ master presents to user, waits for confirmation
   ▼
[3] BUILD        ← am-coder: implement assigned tasks, write summary
   │              ↓ master re-asks planner if Complexity triggers fire (v0.7.0+)
   │              ↓ browser visual preflight for UI phases (v0.6.0+)
   ▼
[4] REVIEW       ← am-review: per-task verdicts (PASS / WARN / FAIL)
   │
   ├── FAIL → loop to [3] with fix list (max 3 fix-loops)
   ├── plan-change-needed → loop to [2]
   ├── research-gap → loop to [1]
   └── all PASS → DONE
   │
   ▼
[5] NEXT-STEPS (optional)  ← v0.6.0+: auto-detects git vs non-git menu
                              v0.6.0+: optionally runs smoke test if API key provided
```

## The seven agents

| Agent | Type | What it does | Hard wall (v0.5.0+ soft) |
|---|---|---|---|
| **master** | orchestrator | Routes work, gates on user confirmation, enforces `max_fix_loops = 3`. Adaptive mode (v0.16.0+): pipeline is default shape, not rule. | Cannot implement, plan, design, code, or review; only edits its own `agents_manager/SKILL.md` |
| **am-research** | specialist | Brainstorm, analyze, surface unknowns | Read-only — cannot write code or configs |
| **am-planning** | specialist | Phased plan + Complexity block + task table | No bash, no code edits |
| **am-design** (v0.9.0+) | specialist | 12-mode design: mockups, tokens, brand, audit, copy, locale, audit | Never writes `src/**`; never edits other specialists' folders |
| **am-assets** (v0.12.0+) | specialist | Asset gatekeeper at Phase 3a; 4-branch runtime decision tree (video pipeline / video file / stills / nothing) | Never writes `src/**`; never edits templates; never touches other specialists' folders |
| **am-coder** | specialist | Implement assigned tasks | Cannot edit other specialists' folders or controller config; only its own `agents_manager/coder/**` |
| **am-review** | specialist | Per-task verdicts with evidence | Cannot edit source code; tests only |

Walls are soft — enforced by each agent reading its `SKILL.md` boundaries + the inline prompt's Can/Can't list, not by OpenCode's permission layer. See [`docs/PERMISSIONS.md`](docs/PERMISSIONS.md) for the v0.5.0 architectural change rationale.

## Permissions model (v0.5.0+ — soft walls)

All 7 agents have `permission: "allow"` in `opencode.jsonc`. OpenCode's permission layer is **not used** to enforce walls. Each agent's `SKILL.md` declares its boundaries as a soft contract — the LLM is expected to honor them.

| Agent | Reads | Writes | Dispatches | Bash |
|---|---|---|---|---|
| **master** | anything | anything (own orchestration doc by convention) | all 6 specialists | read-only by convention |
| **am-research** | anything | anything (own folder by convention) | — | read-only by convention |
| **am-planning** | anything | anything (own folder by convention) | — | read-only by convention |
| **am-design** | anything | anything (own folder by convention) | — | read-only by convention |
| **am-assets** | anything | `assets/MANIFEST.json`, `share/notes/03a_*`, `share/handoffs/03a_*`, own folder | — | read-only by convention |
| **am-coder** | anything | anything (own folder by convention) | — | allow (full) |
| **am-review** | anything | anything (own folder by convention) | — | test commands by convention |

**Cross-agent coordination** goes through `share/messages/<from>-to-<to>-<topic>.md` (a free-form folder; the naming convention makes intent obvious — e.g. `research-to-planning-T-001-clarify.md`).

**Why soft walls?** The v0.4.0 → v0.4.1 era exposed several OpenCode permission-layer edge cases (write/edit dual-allow requirement, bash exact-match, silent task cancellation). Hard walls required continuous patching. v0.5.0 trades mechanical enforcement for simpler config and LLM-disciplined boundaries. If a downstream project finds soft walls insufficient, the architecture supports opt-in hard walls per agent — see [`docs/PERMISSIONS.md`](docs/PERMISSIONS.md).

For the v0.4.0 → v0.4.1 hard-wall era (now retired) and the discovered OpenCode behavior, see [`docs/PERMISSIONS.md`](docs/PERMISSIONS.md).

## Operational characteristics (v0.5.1+)

Each agent in `agents_manager/` follows two efficiency rules: **batch parallel reads when you know what to read, batch parallel edits when independent.** Only sequence when later edits depend on earlier or when discovery (grep/glob) is needed first. These rules apply to **this LLM** too — see [`CLAUDE.md`](CLAUDE.md). Full text + caveats (oldString uniqueness, context-window limit, discovery-then-read pattern) is in each agent's `SKILL.md` "Tool usage efficiency" section.

## Quick start

> **Unified CLI (v0.10.0+).** After installing, use `agents-manager` (bash) or `agents-manager.ps1` (PowerShell) for everything: `install`, `check`, `doctor`, `update`, `skills list|add|which|update`, `release`, `lint`, `version`. Run with no args to launch the interactive wizard, or `agents-manager help` for the full surface.

Windows? Use `bin\install.cmd` for an interactive wizard. macOS/Linux? Use `bin/install.sh`. Both launch the Python UX layer (`bin/agents-manager.py`), which dispatches to the bash or PowerShell dispatcher under the hood. For zero-dependency remote bootstrap, see [Quick install](#quick-install) above.

### Option A — git subtree (recommended for downstream projects with their own git history)

```bash
# In your target project's repo root:
git subtree add --prefix=agents-manager-src https://github.com/ahmadmhmdsy/agents-manager.git main --squash
# Then run the installer pointing at this dir:
./agents-manager-src/bin/install.sh .
```

### Option B — download a release ZIP

1. Go to <https://github.com/ahmadmhmdsy/agents-manager/releases/latest>
2. Download the latest release ZIP (e.g. `agents-manager-v0.9.1.zip`)
3. Extract the controller files into your project root
4. Run `bash bin/install.sh .` from inside the extracted folder, OR manually copy `opencode.jsonc`, `CLAUDE.md`, `agents_manager/`, `share/`, `tasks/`, `.agents/skills/mavis-team/` into your project root.

### Option C — manual install

See [`docs/INSTALL.md`](docs/INSTALL.md) for the full procedure (PowerShell + Unix). If you already have a local checkout, the Python UX wrapper gives you a single entry point: `python3 bin/agents-manager.py install . --yes`. The Python layer wraps the bash / PowerShell dispatcher and adds an interactive 5-option menu; the dispatcher logic is unchanged.

## Examples

Eight worked examples live in [`examples/`](examples/):

**Code pipeline:**
- **`examples/node-markdown-linter/`** — full pipeline trace for "add a no-consecutive-h1 rule" task. Includes `original/` (starting state), `user-task.md`, full `share/` artifacts (00–04), `tasks/T-2026-06-28-001.md`, and `expected-output/` (rule + 5 new tests). **Canonical demonstration** of the agents-manager code pipeline end-to-end.
- **`examples/python-csv-summarizer/`** — compact example for "add a `mean` aggregation alongside `sum` and `count`". Demonstrates the Python/pytest loop.
- **`examples/docs-restructure/`** — pure-markdown example (no source code). Demonstrates Phases 1+2+4 without Phase 3 (no code to write).
- **`cinematic-landing-kit-demo/`** (repo-root demo) — the v0.12.0 worked example for a cinematic / scroll-driven landing page: 1133-L single-file HTML rendering all 5 cinematic-landing hard rules. Lives at repo root (not under `examples/`) because it doubles as the runtime exemplar + source-of-truth for `templates/cinematic-landing/skeleton/`.

**Design pipeline (v0.9.0+):**
- **`examples/design-onboarding/`** — fitness app, 2-screen mobile onboarding (carried from am-design v1).
- **`examples/design-brand-identity/`** — Atlas coffee roastery, full brand system + copy deck.
- **`examples/design-responsive-web/`** — Lumio habit tracker, 3 breakpoints (mobile/tablet/desktop).
- **`examples/design-audit/`** — Stride fitness app, 20 findings + severity matrix + remediation plan.
- **`examples/design-casestudy-quran/`** — retrospective on a real multi-theme, multi-locale Quran app design system built before am-design was formalized.

Plus a docs-site template worked-example pair under [`templates/docs-site/examples/`](templates/docs-site/examples/) and a blank recipe starter at [`templates/_blank/`](templates/_blank/).

See [`examples/README.md`](examples/README.md) for the index + how to replay.

## Required user-level skills

After installing the controller, install these skills on your machine (user-level, not project):

```bash
npx --yes skills add https://github.com/obra/superpowers --skill dispatching-parallel-agents -g -y
npx --yes skills add https://github.com/obra/superpowers --skill subagent-driven-development -g -y
npx --yes skills add https://github.com/obra/superpowers --skill verification-before-completion -g -y
npx --yes skills add https://github.com/obra/superpowers --skill systematic-debugging -g -y
npx --yes skills add https://github.com/obra/superpowers --skill test-driven-development -g -y
npx --yes skills add https://github.com/obra/superpowers --skill requesting-code-review -g -y
npx --yes skills add https://github.com/obra/superpowers --skill writing-plans -g -y
npx --yes skills add https://github.com/obra/superpowers --skill executing-plans -g -y
npx --yes skills add https://github.com/obra/superpowers --skill brainstorming -g -y
```

Verify your install: `bash bin/check.sh .`

**Upgrading:** `bash bin/update.sh --check` (dry run) or `bash bin/update.sh` (apply). The master agent also prompts once per day if a newer release is available. PowerShell parity via `.\bin\update.ps1 -Check`.

The install scripts support `--dry-run` (preview without writing) and `--uninstall` (remove the controller). For full script documentation, see [`bin/README.md`](bin/README.md). PowerShell parity via `.\bin\install.ps1 -Target <path>`.

**Zero-knowledge git handling (v0.9.1+):** the installer defaults to `--git auto` — if your target folder is not a git repo, it runs `git init` + initial commit for you. Use `--git prompt` to be asked first, or `--git skip` to leave git alone. See [`docs/INSTALL.md`](docs/INSTALL.md) § Git initialization.

## Usage

Once installed, open your project in OpenCode and describe your task. The `master` agent auto-routes to specialists based on your request. See [`agents_manager/SKILL.md`](agents_manager/SKILL.md) for the full orchestration protocol and [`agents_manager/README.md`](agents_manager/README.md) for the system overview.

## Repo layout

```
agents-manager/
├── README.md                       ← this file (GitHub landing)
├── CONTRIBUTING.md                 ← v1.0.0 contributor guide (2026-07-04)
├── LICENSE                         ← MIT
├── opencode.jsonc                  ← 7 agents + permission blocks (master + 6 specialists)
├── CLAUDE.md                       ← auto-routing rule
├── AGENTS.md                       ← project-orientation doc
├── agents_manager/                 ← controller (master + 6 specialists: research, planning, design, assets, coder, review)
│   ├── master/SKILL.md             ← master's orchestration protocol (adaptive mode in v0.16.0+)
│   ├── memory/                     ← 3-scope memory tree (v0.13.0+): global/ + projects/ + per-role notes/
│   └── upstream-contrib/           ← MiniMax-M3 contribution patches (v0.6.0 + v0.7.0 + cinematic-landing)
├── share/                          ← inter-agent bus (handoffs / notes / reports / design/ / messages/)
├── tasks/                          ← task tracker (T-YYYY-MM-DD-NNN.md per task)
├── examples/                       ← 8 worked pipeline traces (3 code + 5 design; v0.12.0+ demos)
├── templates/                      ← visual task templates (v0.12.0+)
│   ├── cinematic-landing/          ← first shipped template (memory/ + skeleton/ + prompts/ + decisions/ + assets/)
│   ├── docs-site/                  ← docs-site template
│   ├── _blank/                     ← recipe starter (cp -r to author a new template)
│   └── AUTHORING.md                ← v1.0.0 template-authoring rulebook
├── cinematic-landing-kit-demo/     ← repo-root worked example for cinematic-landing (1133 L single-file HTML)
├── .agents/skills/mavis-team/      ← OpenCode-discoverable skill
├── .github/ISSUE_TEMPLATE/         ← bug_report + feature_request templates (2026-07-04)
├── bin/                            ← install + check + update + release scripts (bash / PowerShell / Python UX / standalone)
├── docs/                           ← installation, permissions, attribution, design docs-site content
└── scripts/                        ← stdlib-only repo scripts (e.g. validate-frontmatter, validate-memory, backfill-research-metrics)
```

## FAQ

### Why soft walls instead of hard permission-layer walls?

The v0.4.0 → v0.4.1 era exposed three OpenCode permission-layer edge cases (write/edit dual-allow requirement, bash exact-match, silent task cancellation). Hard walls required continuous patching as OpenCode evolved. v0.5.0 trades mechanical enforcement for simpler config and LLM-disciplined boundaries. If a downstream project needs hard walls, see [`docs/PERMISSIONS.md`](docs/PERMISSIONS.md) for the opt-in procedure.

### Can I install agents-manager into a nested directory (e.g., `tools/agents-manager/`)?

No — not in v0.7.0. The OpenCode permission-layer globs in `opencode.jsonc` are root-relative (e.g., `share/**`, `tasks/**`). They resolve against the project root, not the install directory. Nesting breaks the path resolution. **Root-level install only** is supported.

### How do I add an 8th agent? (or: how was `am-design` added in v0.9.0, `am-assets` in v0.12.0?)

The v0.9.0 + v0.12.0 PRs each added a worked example. Same recipe applies to any future agent:

1. Add the agent block to `opencode.jsonc` (use any existing agent as a template; match the inline prompt structure: `## Before acting` / `## Output` / `## Boundaries` / `## Return` / `## Tool usage (v0.5.1+)`). Add the v0.16.0+ `## Adaptive mode` reflex block.
2. Create `agents_manager/<role>/SKILL.md` + `rules.md` + `notes/{episodic,semantic}/.gitkeep` + `resources/`.
3. Reference the agent in `agents_manager/SKILL.md` master prompt:
   - `## Spawning a specialist` dispatch contract (the `task(subagent_type=...)` example)
   - `## Your responsibilities` ("Never do a sub-agent's job. ... Design → design agent. Assets → assets agent. ...")
   - `## What you cannot do` (the master never dispatches non-specialist agents)
4. Add the agent row to the CLAUDE.md agents table + update project-structure count.
5. Update this README's "The seven agents" table + FAQ + Releases.

`am-assets` is a good model for "specialist with a structured artifact surface" — owns `agents_manager/assets/`, writes to `assets/MANIFEST.json` + `share/notes/03a_assets_<task-id>.md` + `share/handoffs/03a_assets-to-coder-<task-id>.md`, runs a deterministic 4-branch decision tree (no creative work — pure gating). `am-design` is a good model for "specialist with its own subtree" — owns `agents_manager/design/`, writes `share/design/<task-id>/**`, strict-separation only.

### How do I migrate from a hard-wall install (v0.4.x) to soft-wall (v0.5.0+)?

The permission block shape changed. v0.4.x used `{ edit: {...}, write: {...}, bash: {...}, task: {...}, ... }`; v0.5.0+ uses `"permission": "allow"`. To upgrade:
1. Replace each agent's `permission` block with `"permission": "allow"`.
2. Move the per-path restrictions from JSON into prose in each `SKILL.md` "Boundaries" section.
3. Run `bin/check.sh .` to verify.

The `agents_manager/SKILL.md` + `docs/PERMISSIONS.md` document the new architecture. Hard walls can be opted back in per agent.

### What's the difference between `share/notes/`, `share/messages/`, and `share/handoffs/`?

| Folder | Convention | Used by |
|---|---|---|
| `share/notes/01_research_<task-id>.md` | Phase 1 research output | am-research |
| `share/notes/02_plan_high_<task-id>.md`, `02_plan_phases_<task-id>.md` | Phase 2 plan output | am-planning |
| `share/notes/03_coder_summary_<task-id>_<phase>.md` | Phase 3 coder output | am-coder |
| `share/notes/04_warns_register_<task-id>.md` (v0.6.0+) | Consolidated WARN log | master + am-review |
| `share/notes/99_progress_<task-id>.md` | Master recovery ledger | master |
| `share/messages/<from>-to-<to>-<topic>.md` | Cross-agent notes (free-form) | any agent |
| `share/handoffs/00_user_task.md` | Captured user task | master (Phase 0 Ingest) |
| `share/reports/04_review_<task-id>_<phase>.md` | Phase 4 review output | am-review |

### Can I use agents-manager in a non-git project (sandbox / exploration)?

Yes — v0.6.0+ detects git vs non-git at Phase 5 and offers a 4-option menu for non-git projects (run smoke / polish WARNs / build follow-up / close out). Phase 0 also asks before `git init`-ing (default no).

### What if my downstream project finds soft walls insufficient?

Per-agent opt-in: set one agent's `permission` back to a hard-wall block (copy from `agents_manager/upstream-contrib/PROPOSED_PATCH_v0.5.x_2026-06-29.md` historical pattern). The architecture supports mixed soft + hard per agent. See [`docs/PERMISSIONS.md`](docs/PERMISSIONS.md) § When to opt back into hard walls.

## Releases

| Version | Date | Theme | Highlights |
|---|---|---|---|
| **v0.16.0** | 2026-07-05 | Adaptive orchestration | Pipeline reframed as default shape (not absolute rule); 5 authority levers (complexity triage, re-dispatch, parallel, review-any, propose-better); adaptive-mode reflex added to all 7 agents |
| **v0.15.0** | 2026-07-04 | Extract-to-template | `agents_manager/extract/` specialist + extract-skill-as-non-roster-soft-skill recipe; closes WARN-9 from `04_review_T-2026-07-03-003` |
| **v0.14.1** | 2026-07-04 | am-research enhancements | Populated `research/resources/` (6 files) + seeded `notes/episodic/` (3 backfilled); 2 new protocol sections + 2 rules (confidence scoring + handoff); `scripts/backfill-research-metrics.sh` ships |
| **v0.14.0** | 2026-07-04 | cinematic-landing PASS + `templates/AUTHORING.md` v1.0.0 | 9 review fixes land; `templates/_blank/` recipe starter; per-template `INDEX.md` + `tests/verify.sh` (8 grep oracles); 14/14 `memory/*.md` carry `USE THIS WHEN:` trigger lines |
| **v0.13.0** | 2026-07-03 | Three-scope memory | `agents_manager/memory/{global,projects}/` + per-role `notes/`; canonical schema in `memory/README.md`; `scripts/validate-memory.sh` ships as release blocker; 90-day sweep hook |
| **v0.12.1** | 2026-07-03 | v2-axis integration | 4 source memory files (canvas-a11y, reduced-motion, keyboard-nav, dark-theme) moved into `templates/cinematic-landing/memory/` as files 11-14; skeleton extended ~286 LOC; `cinematic-landing-kit-demo/` copied to repo root |
| **v0.12.0** | 2026-07-03 | cinematic-landing template + am-assets | 6th specialist (`am-assets`, asset gatekeeper at Phase 3a); 4-branch runtime decision tree; `templates/cinematic-landing/` (17 files); 5 hard rules for cinematic builds |
| **v0.11.0** | 2026-07-01 | Python UX + standalone installer | `bin/agents-manager.py` (stdlib only, ~380 LOC) wraps bash + PowerShell dispatchers with wizard; `bin/standalone-installer/install.{py,sh,cmd}`; `--global/--local/--both/--skip` skills flag |
| **v0.10.0** | 2026-06-30 | Unified dispatcher | `bin/agents-manager` (bash), `bin/agents-manager.ps1` (PowerShell), `bin/agents-manager.py` (Python UX) — one entry point per platform; CI chmod + dispatcher-lint hooks |
| **v0.9.x** | 2026-07-20 | `am-design` v2.0: 12-mode design specialist | 5th agent (design), 6 mockup templates, 5 new design examples + 1 case study, audience-aware handoff, strict-separation only |
| **v0.9.0** | 2026-07-20 | Auto-updater | `bin/update.sh` / `update.ps1` with version compare + backup + zip-apply; master once-per-day prompt |
| **v0.8.0** | 2026-06-29 | WARN register + preflights | WARN consolidation, git/API preflight, Phase 5 non-git menu, browser preflight |
| **v0.7.x** | 2026-06-29 | Chunk-size protocol | Per-phase complexity estimation + master re-ask + Phase productivity metric (v0.7.0); install guide + scripts polish (v0.7.1 + v0.7.2) |
| **v0.6.0** | 2026-06-29 | README + LICENSE + install/check | First public release + addendum recipes |
| **v0.5.1** | 2026-06-28 | Tool usage efficiency | Batch parallel reads + edits rules (applies to this LLM too) |
| **v0.5.0** | 2026-06-28 | Soft-wall architecture | All agents `permission: "allow"`; boundaries become soft contracts |
| **v0.4.x** | 2026-06-28 | Permission rewrite | Permission-layer fixes (v0.4.1); broader share + own-folder writes (v0.4.0) |
| **v0.3.0** | 2026-06-28 | Examples + maintenance | 3 worked examples + obra-sync workflow |
| **v0.2.0** | 2026-06-28 | Tier 3 skills | Brainstorming, executing-plans, finishing-a-development-branch |
| **v0.1.0** | 2026-06-28 | First public release | README, LICENSE, install/check scripts, INSTALL.md |

Five of these releases (v0.6.0 + v0.7.0 + v0.11.0 + v0.14.0 templates + v0.16.0 design-pattern) were upstream-contribution patches from downstream consumers. See [`docs/UPSTREAM-CONTRIB.md`](docs/UPSTREAM-CONTRIB.md) for attribution + decision log, and [`agents_manager/upstream-contrib/`](agents_manager/upstream-contrib/) for the full patch text.

## License

MIT — see [`LICENSE`](LICENSE).

## Status

**v0.16.0** is the latest release. The controller is functional and tested on 3 downstream projects (2 with full end-to-end runs) plus 7 internal task runs (`T-2026-07-03-001` through `T-2026-07-04-009`). Known scope:

- API may change between minor versions until v1.0.0.
- Soft walls rely on LLM discipline; opt back into hard walls per agent if your project requires mechanical enforcement.
- `git subtree`, manual ZIP install paths, and the zero-dependency standalone installer are all battle-tested.
- Window-specific path assumptions (root-relative globs) require a **root-level install** — nesting under `tools/` etc. is not supported.
- Memory system (v0.13.0+) is opt-in: empty scaffold ships; first task on each clone writes content as it earns its keep. 90-day sweep runs at master's Phase 5 close when `phase_5_enabled: true`.
- Visual templates (v0.12.0+) are opt-in: master dispatches `am-assets` only when the task uses a template that declares assets in its frontmatter AND no `MANIFEST.json` exists yet.
- Adaptive orchestration (v0.16.0+) softens pipeline-as-rule to pipeline-as-default; the complexity triage table in `agents_manager/SKILL.md` decides the dispatch shape per task.

See [`agents_manager/CHANGELOG.md`](agents_manager/CHANGELOG.md) for full change history and [`share/notes/99_decisions.md`](share/notes/99_decisions.md) for append-only architectural decisions logged since v0.13.0.