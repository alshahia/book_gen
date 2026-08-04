# Coder summary — T-2026-07-01-001.A (T1 dispatcher scope override)

**Status**: complete
**Master task**: T-2026-07-01-001 (track T1)
**Plan**: `share/notes/02_plan_T1_dispatcher_scope.md`
**am-coder dispatch**: cancelled mid-run; code on disk, summary written by master from on-disk diffs

## Tasks attempted

| ID | Title | Status |
|---|---|---|
| A.1 | bash `cmd_skills_add` parse `--global/--local/--both/--skip` | done |
| A.2 | bash `install_skill_locally` helper | done |
| A.3 | bash per-skill loop: scope branching (skip / local / global / both) | done |
| A.4 | bash wizard prompt for scope before `cmd_skills add --all` | done |
| A.5 | bash help text updated (`skills add` line + `cmd_skills_list` tip) | done |
| A.6 | PowerShell `Skills-Add-Cmd` parse `--global/--local/--both/--skip` | done |
| A.7 | PowerShell `Install-Skill-Locally` function | done |
| A.8 | PowerShell per-skill loop: scope branching | done |
| A.9 | PowerShell wizard prompt for scope | done |
| A.10 | PowerShell help text updated | done |

## Files written/edited

- `bin/agents-manager` — added `install_skill_locally` helper at L94-L107; refactored `cmd_skills_add` L518-L630; updated wizard L850-L865; updated help at L508, L799
- `bin/agents-manager.ps1` — added `Install-Skill-Locally` at L70-L82; refactored `Skills-Add-Cmd` L412-L490; updated wizard L647-L660; updated help at L386, L604

## Commands / tests run

| Command | Result |
|---|---|
| `shellcheck bin/agents-manager` (via `npx --yes shellcheck` v0.11.0 + `python3` CRLF→LF) | exit 0 |
| `pwsh -NoProfile -Command "Invoke-ScriptAnalyzer -Path bin/agents-manager.ps1 -Severity Warning,Error"` | 141 warnings — same as pre-change baseline (all PSAvoidUsingWriteHost from existing style, no new issues) |

## Deviations from plan

- **Default scope**: plan said `both`; implementation uses `both`. Match.
- **PowerShell flag casing**: plan said PascalCase `-Skills`; code accepts BOTH `--skills` and `-Skills` (the `-xxx` form is normalized via `.ToLower()`). More forgiving than the plan strictly required; no functional impact.
- **Help-text style**: plan said to mirror existing format; PowerShell tip line updated to show both `-Global|-Local|-Both|-Skip`, bash tip line updated to show `--global|--local|--both|--skip`. Both follow existing style.

## Known issues / TODOs

- bash file is CRLF on Windows working tree (due to `core.autocrlf=true`); .gitattributes stores as LF; CI runs LF. No action needed.
- PowerShell file's pre-existing 141 PSAvoidUsingWriteHost warnings are out of scope; project convention keeps Write-Host for interactive CLI output.

## Suggested review focus

- Confirm the `scope=both` default behavior matches today's implicit behavior (mavis-team local + obra global).
- Confirm `scope=local` produces a friendly warn (not a hard error) when the skill isn't bundled.
- Confirm the wizard's scope prompt default = `1) both` matches user expectation.
- Confirm `--global` is gracefully rejected for `source=controller` skills (mavis-team).

## Self-critique

- **yes** — implementation matches plan, gates pass, no new lint regressions, defaults are conservative (mirror today's behavior).

## Master actions taken

- am-coder cancelled mid-write; no `share/notes/03_*` produced by subagent.
- Master wrote this summary from `git diff` output + gate logs.
- All code is committed-ready (no commit performed per project convention).
- T1 ready for review; advance to T2 (in-repo `.cmd` files).