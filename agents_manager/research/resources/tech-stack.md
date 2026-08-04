# Tech Stack — agents_manager

**Last verified:** 2026-07-04

Pinned versions and rationale for the runtime/host stack that am-research's findings, plans, and code reviews depend on.

## Language + runtime

- **Python 3.11+** — controller scripts (`bin/agents-manager.py`, `bin/standalone-installer/install.py`). Stdlib only; deliberately no `pip install` requirement so a fresh clone runs without bootstrap.
- **bash 4+** / **zsh** — dispatcher scripts in `bin/agents-manager`, `scripts/*.sh`. CRLF-stripped on Windows working tree via `.gitattributes` (`*.sh text eol=lf`).
- **PowerShell 7+ (pwsh)** — `bin/agents-manager.ps1`. CRLF preserved on commit (`*.ps1 text eol=crlf`).
- **Node.js 20+** — only for `npx --yes shellcheck` linting and `python3 scripts/validate-frontmatter.py`; not part of the runtime.
- **Markdown (CommonMark + GFM)** — every memory entry, plan, research note, and review report. Linted for frontmatter by `scripts/validate-frontmatter.py`.

## Controller layer

- **agents_manager v0.14.0** (promoting to v0.14.1 with this task) — OpenCode multi-agent orchestration. 6 specialists defined in `opencode.jsonc`. Soft-wall lane enforcement (v0.5.0+); prose defines who writes what, the OpenCode permission layer is `permission: "allow"` for all.
- **opencode.jsonc** (71 L) — agent definitions + per-agent prompt. Frontmatter-style JSONC with comments.

## Memory + memory schema

- **agents_manager/memory/** (v0.13.0+) — three-scope memory tree: `global/`, `projects/<slug>/`, `<role>/notes/{semantic,episodic}/`. Canonical schema at `agents_manager/memory/README.md`. Required frontmatter: `scope`, `topic`, `status`, `created`, `last_verified`. ≤20 L per entry.

## Lint + verification

- **shellcheck** — bash scripts (via `npx --yes shellcheck`).
- **PowerShell PSScriptAnalyzer** — `bin/agents-manager.ps1` (manual smoke only on Windows; CI runs on `ubuntu-latest`).
- **`python3 -m py_compile`** — Python scripts.
- **`scripts/validate-frontmatter.py`** — frontmatter linter for controller files.

## Why this matters for research

When researching a library or pattern, default to versions on this list. If the user's task references a different version, flag the drift in the **What we know** section and recommend a version-pin. Don't recommend adding a new dependency when an already-installed one (or the stdlib) covers it — that's the lazy-first reflex from `rules.md` rule 8 (stay-in-scope) extended to dependency choices.

## Source-of-truth pointers

- `AGENTS.md` — top-level conventions, dispatcher install paths, lint commands.
- `.gitattributes` — EOL normalization map.
- `agents_manager/CHANGELOG.md` — version history (start at the latest entry for current contract).

---

last-verified: 2026-07-04