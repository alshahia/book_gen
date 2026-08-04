# External Docs — quick links

**Last verified:** 2026-07-04

Hand-picked doc URLs and one-line summaries for the things am-research's findings tend to reference. Reach for these before generic search results.

## OpenCode (the host runtime)

- **OpenCode task tool** — `task(subagent_type="<name>", prompt="...")` is the only sanctioned way for master to dispatch specialists. Per-agent prompt and `permission` are defined in `opencode.jsonc`. Specialists cannot dispatch subagents (no `task` tool exposed to them by default). Source: `opencode.jsonc` agent definitions + `agents_manager/SKILL.md` orchestration protocol.
- **agents_manager SKILL.md** — master orchestration protocol. Defines pipeline, phases, preflight, gates, fix-loop cap, and WARN register conventions. Read first; read latest CHANGELOG entry second.

## Memory system (v0.13.0+)

- **agents_manager/memory/README.md** — canonical schema, lifecycle, and read/write protocol for the three-scope memory tree. Required frontmatter keys (`scope`, `topic`, `status`, `created`, `last_verified`); ≤20 L per entry; 200-line per-scope read budget.
- **`scripts/validate-memory.sh`** — frontmatter linter for memory entries (planned/shipped in chunk 3 / P3.3). Exit 0 = clean; exit 1 = at least one issue. Run after every write batch.

## Task tracker

- **`tasks/README.md`** — schema for `tasks/<id>.md`: phase log, sub-task rows, status legend, `## Loop history` block. Required for any specialist that touches `tasks/<id>.md` (master's lane only).
- **`share/handoffs/00_user_task_<task-id>.md`** — user-task capture convention. Has a "Decisions" block for Phase-0 master-approved defaults.

## Dispatchers

- **`bin/agents-manager.py`** — Python UX, stdlib only. Recommended. Reads manifest via inline stdlib parsing.
- **`bin/agents-manager`** — bash dialect. Reads manifest via inline Python3. CRLF-stripped on commit.
- **`bin/agents-manager.ps1`** — PowerShell dialect. Reads manifest via `ConvertFrom-Json`. CRLF preserved.
- **`bin/standalone-installer/install.{py,sh,cmd}`** — downloads latest release from GitHub API, runs bundled installer, cleans up. Stdlib only.

## Lint / verify recipes

- **`scripts/validate-frontmatter.py`** — frontmatter linter for controller files. Run after every write batch.
- **shellcheck** — bash scripts via `npx --yes shellcheck`. Convert CRLF to LF before piping (Windows working tree).
- **PSScriptAnalyzer** — `bin/agents-manager.ps1`. Manual smoke on Windows; CI is `ubuntu-latest` so `.cmd` and `.ps1` cannot be CI-linted.
- **`python3 -m py_compile`** — Python scripts.

## EOL + line endings

- **`.gitattributes`** — `*.sh text eol=lf`, `*.ps1 text eol=crlf`, `*.cmd text eol=crlf`, `*.bat text eol=crlf`, `*.{json,yaml,md} text eol=lf`. Windows working tree may show CRLF due to `core.autocrlf=true`; git normalizes on commit.

## CHANGELOG + version history

- **`agents_manager/CHANGELOG.md`** — version history. Read the latest entry first when checking the current contract. Each entry documents what changed, why, and what to do at upgrade.

---

last-verified: 2026-07-04