# Plan: T3 (docs) + T4 (release plumbing) for T-2026-07-01-001

**Task**: T-2026-07-01-001.D
**Tracks**: T3 (docs) + T4 (release plumbing) — combined into one am-coder dispatch since they're tightly coupled
**Master tracker**: `tasks/T-2026-07-01-001.md`
**Source**: `share/handoffs/00_user_task.md`

## State going in
- T1 done: `bin/agents-manager` (bash) and `bin/agents-manager.ps1` (PowerShell) have `--global/--local/--both/--skip` flag
- T2 done: `bin/agents-manager.py`, `bin/install.py`, `bin/agents-manager.{sh,cmd}`, `bin/install.{sh,cmd}` exist
- T5 done: `bin/standalone-installer/install.{py,sh,cmd}` + `README.md` exist
- `bin/agents-manager.py` already says version `0.11.0`; bash + PowerShell dispatchers still say `v0.10.0` (need bump in T4)
- T1+T2 changes are uncommitted (per project convention "Don't commit unless explicitly asked")

## Files to edit / create (in this dispatch)

### Track T3 — Docs

#### 1. `README.md` (top-level, ~120 lines currently)
- Add a new section near the top, right after the title/badges, titled "Quick install"
- Three one-liners (one per row of a markdown table):
  - Windows PowerShell: `iwr -useb https://raw.githubusercontent.com/ahmadmhmdsy/agents-manager/main/bin/standalone-installer/install.cmd -OutFile install.cmd; .\install.cmd`
  - Windows cmd: link to `https://raw.githubusercontent.com/ahmadmhmdsy/agents-manager/main/bin/standalone-installer/install.cmd` with "right-click → Save Link As, then double-click"
  - macOS/Linux: `curl -fsSL https://raw.githubusercontent.com/ahmadmhmdsy/agents-manager/main/bin/standalone-installer/install.sh | bash`
- In the "Quick start" section, add one paragraph: "Windows? Use `bin\install.cmd` for a wizard. macOS/Linux? Use `bin/install.sh`."
- Update the existing "Manual install" or "Get started" section to mention the new Python UX: `python3 bin/agents-manager.py install . --yes`

#### 2. `bin/README.md` (~215 lines currently)
- Add a new section "Python UX (v0.11.0+)" documenting:
  - `bin/agents-manager.py` (full dispatcher)
  - `bin/install.py` (wizard launcher)
  - The four shims: `bin/agents-manager.{sh,cmd}` and `bin/install.{sh,cmd}`
- Update the dispatcher flag table to include the new `--global/--local/--both/--skip` flag on `skills add`
- Add a new section "Standalone installer" pointing to `bin/standalone-installer/README.md`
- Update the dispatcher table at the top to include Python

#### 3. `docs/INSTALL.md` (~368 lines currently)
- Add a NEW top-level section "Option D — Use the standalone installer" (BEFORE Option A)
- Show all three one-liners (PowerShell / cmd / curl|bash) with a flags table
- Add a "Skill installation scope (v0.11.0+)" subsection under "Install required user-level skills":
  - Default: `both` (matches v0.10.0 implicit behavior)
  - `--skills global`: only npx-installed to $HOME/.agents/skills/
  - `--skills local`: only locally to <target>/.agents/skills/
  - `--skills skip`: controller only
- Update the existing "Shell coverage table" to add: Windows cmd, Python UX

### Track T4 — Release plumbing

#### 4. `.gitattributes`
- Add two lines: `*.cmd text eol=crlf` and `*.bat text eol=crlf`
- (existing `*.ps1 text eol=crlf` and `*.sh text eol=lf` stay)

#### 5. `.github/workflows/release.yml`
- In the ZIP validation block, add 4 new `grep -q` lines:
  - `bin/agents-manager.py`
  - `bin/install.py`
  - `bin/standalone-installer/install.py`
  - `bin/standalone-installer/install.cmd`
- (existing checks for `bin/install.sh` and `bin/install.ps1` stay)

#### 6. `bin/release-zip.ps1`
- Mirror the same 4 additions in PowerShell

#### 7. `agents_manager/CHANGELOG.md`
- Add new top section `## v0.11.0 — Python UX + standalone installer + skills scope override`
- Bullets:
  - New: Python UX layer (`bin/agents-manager.py`, `bin/install.py`, four shims)
  - New: Standalone installer (`bin/standalone-installer/`)
  - Changed: `bin/agents-manager` and `bin/agents-manager.ps1` accept `--global/--local/--both/--skip` on `skills add`
  - Changed: wizard prompts for scope before `cmd_skills add --all`
  - Compatibility: no breaking changes; default scope `both` matches prior implicit behavior

#### 8. Version bump
- `bin/agents-manager` line 5: `VERSION="v0.10.0"` → `VERSION="v0.11.0"`
- `bin/agents-manager.ps1` line 17 (after recent T1 changes): `$ScriptVersion = "v0.10.0"` → `$ScriptVersion = "v0.11.0"`
- (Python `bin/agents-manager.py` already says `0.11.0` from T2 — no change)

## Files NOT to edit (in this track)

- `bin/agents-manager` lines other than line 5 (the T1 --scope work is preserved)
- `bin/agents-manager.ps1` lines other than line 17
- Any T2/T5 files
- `agents_manager/` controller internals
- `opencode.jsonc`
- `CLAUDE.md`

## Acceptance gates (run BEFORE writing summary)

```bash
cd E:\context_gen

# Lint regression check (T1 work must still pass)
shellcheck bin/agents-manager   # via python3 CRLF->LF + npx shellcheck
pwsh -NoProfile -Command "Invoke-ScriptAnalyzer -Path bin/agents-manager.ps1 -Severity Warning,Error" | Select-String -Pattern "^[^\s]" | Measure-Object

# Python compile regression
python3 -m py_compile bin/agents-manager.py bin/install.py bin/standalone-installer/install.py

# Markdown sanity
Test-Path README.md
Test-Path bin/README.md
Test-Path docs/INSTALL.md
Test-Path agents_manager/CHANGELOG.md
Test-Path .gitattributes
Test-Path .github/workflows/release.yml
Test-Path bin/release-zip.ps1

# Version bump visible
Select-String -Path bin/agents-manager,bin/agents-manager.ps1 -Pattern "v0.11.0"
```

Expected:
- shellcheck: 0 new issues
- PSScriptAnalyzer: count same as T1 baseline (141)
- py_compile: exit 0
- All Test-Path: True
- Select-String: 2 matches (one per file)

## Output (mandatory)

`share/notes/03_coder_summary_T-2026-07-01-001_D.md` with template:
- Tasks attempted table
- Files written/edited
- Commands run + their results
- Deviations (if any)
- Known issues / TODOs
- Self-critique

Keep under 120 lines.

## Constraints

- Docs must render cleanly on GitHub (use fenced code blocks, not indented)
- CHANGELOG voice: terse, technical, present tense
- `.gitattributes` change: don't break existing rules; add as new lines
- Do NOT commit. Do NOT touch T1/T2/T5 files except the two `VERSION=` lines.
- If a tool fails, partial summary OK.