# Coder Summary — T-2026-07-01-001 / G (fix loop 1 of 3)

**Date:** 2026-07-03 12:45
**Sub-agent:** coder
**Loop:** fix-loop 1 (per `share/notes/02_plan_T-2026-07-01-001_G_fix_loop.md`)
**Review report:** `share/reports/04_review_T-2026-07-01-001.md` (FAIL — 2 CRITICAL, 2 HIGH, 3 MEDIUM, 5 LOW)

## Tasks attempted

| ID | Status | Notes |
|----|--------|-------|
| P1T1 — bash dispatcher install parse + chain | done | `cmd_install` L113-129 accepts `--skills|--scope` + `=*`; L261-271 chains `cmd_skills add --all --$SKILL_SCOPE` after copy |
| P1T2 — PowerShell dispatcher install parse + chain | done | `Parse-InstallFlags` L94-120 + `Install-Cmd` L129-130 (validation), L230-240 (chain) |
| P1T3 — PascalCase flag parity in PowerShell | done | `-Yes`, `-DryRun`, `-Git M`, `-Skills S`, `-Scope S` now accepted (was silent docs/behavior drift) |
| P1T4 — `.gitignore` cleanup | done | `__pycache__/` + `*.pyc` appended at end |
| P1T5 — `bin/__pycache__/` deletion | done | both `bin/__pycache__/` and `bin/standalone-installer/__pycache__/` removed |
| P1T6 — Python floor 3.6→3.7 | done | `bin/agents-manager.py:27-29` |
| P1T7 — em-dash → ASCII `--` | done | `bin/agents-manager.py:242` |
| P1T8 — CHANGELOG review-driven fixes section | done | 5 bullets under v0.11.0 entry |

## Files written / edited

- `bin/agents-manager:114-129` — added `SKILL_SCOPE` local + `--skills|--scope[=*]` parse cases + validation
- `bin/agents-manager:261-271` — new `Skills:` block; calls `cmd_skills add --all --$SKILL_SCOPE` (or prints SKIP/WOULD)
- `bin/agents-manager:765-790` — install help text expanded with `--skills/--scope` flag doc
- `bin/agents-manager.ps1:91-120` — `Parse-InstallFlags` accepts PascalCase (`-DryRun`, `-Yes`, `-Git M`, `-Skills S`, `-Scope S`); `Skills = "both"` default added
- `bin/agents-manager.ps1:129-131` — `-Skills must be both|global|local|skip` validation
- `bin/agents-manager.ps1:230-240` — `Skills:` block; calls `Skills-Add-Cmd @("--all", "--yes", "--$($p.Skills)")`
- `bin/agents-manager.ps1:619` — install help line updated with `-Skills S`
- `.gitignore:44-47` — appended `__pycache__/` + `*.pyc`
- `bin/agents-manager.py:27-29` — Python floor 3.6 → 3.7
- `bin/agents-manager.py:242` — em-dash → `--`
- `agents_manager/CHANGELOG.md:5-15` — new `### Review-driven fixes (2026-07-03)` subsection
- Deleted: `bin/__pycache__/` (4 files), `bin/standalone-installer/__pycache__/` (1 file)

## Commands run

| # | Command | Exit | Note |
|---|---|---|---|
| 1 | `python3 -m py_compile bin/agents-manager.py bin/install.py bin/standalone-installer/install.py` | 0 | clean |
| 2 | `python3 bin/agents-manager.py --version` | 0 | `agents-manager 0.11.0` |
| 3 | `python3 -c "import sys; sys.exit(0 if sys.version_info >= (3,7) else 1)"` | 0 | floor matches |
| 4 | `python3 bin/agents-manager.py install C:\temp\fixture --git skip --skills skip --dry-run --yes` | 0 | **headline bug fixed** |
| 5 | `python3 bin/agents-manager.py install C:\temp\fixture2 --git skip --skills local --dry-run --yes` | 0 | shows `WOULD run: cmd_skills add --all --local` |
| 6 | `python3 bin/agents-manager.py install . --git skip --dry-run --yes` | 0 | default scope `both`, shows `Skills:` block |
| 7 | `bash bin/agents-manager install . --git skip --skills skip --dry-run --yes` | 0 | bash path works (after LF normalization — see Deviations) |
| 8 | `pwsh -NoProfile -Command "& 'bin\agents-manager.ps1' install . -Git skip -Skills skip -DryRun -Yes"` | 0 | PascalCase accepted |
| 9 | `pwsh -NoProfile -Command "& 'bin\agents-manager.ps1' install . -Yes"` | 0 | minimal `-Yes` form works |
| 10 | `npx --yes shellcheck <LF-normalized bash>` | 0 | no findings |
| 11 | `Select-String -Path .gitignore -Pattern "__pycache__"` | match | `__pycache__/` present |
| 12 | `pwsh -NoProfile -Command "Invoke-ScriptAnalyzer -Path bin/agents-manager.ps1 -Severity Warning,Error \| Measure-Object"` | 0 | **count=151** (vs expected 147; see Deviations) |
| 13 | invalid `--skills bogus` (bash) | 1 | validation works: `--skills must be both\|global\|local\|skip (got 'bogus')` |
| 14 | invalid `-Skills bogus` (PowerShell) | 1 | validation works |

## Deviations from plan

1. **PSScriptAnalyzer count is 151, not 147.** The plan accepted +6 from T1's wizard scope-prompt (141→147). My `Skills:` block in `Install-Cmd` adds **+4 more** `PSAvoidUsingWriteHost` warnings (consistent with house style — every other Install-Cmd section uses `Write-Host`). Total 151. Documented in CHANGELOG. Net regression from 141→151 = +10; all 10 are the same `PSAvoidUsingWriteHost` rule already dominant in the file. If user wants the count back at 141, refactor wizard + my Skills: block to `Write-Output` (significant style break).
2. **Skills-Add-Cmd only accepts `--all` (lowercase) for the all-flag, not `-All`.** First call I wrote used `@("-All", "-Yes", "-Skills", $p.Skills)` — but `Skills-Add-Cmd` (L411-426) only has `'--all'` in its switch. The `-All` PascalCase is NOT accepted; it was treated as a positional skill name. Caught by Gate 9 (the `install . -Yes` minimal test). Fixed by switching the call to `@("--all", "--yes", "--$($p.Skills)")` (long-form `--all` + `--yes` are both accepted by `Skills-Add-Cmd`; scope `--both`/`--global`/etc. are accepted via `'--global', '--local', '--both', '--skip'` cases).

## Known issues / TODOs left in code

- **Pre-existing EOL drift on `bin/agents-manager`**: file was LF in git (HEAD = 852 LF lines, 0 CRLF) but the edit tool wrote it back as CRLF (935 CRLF, 0 LF). I normalized back to LF manually. This is a tooling artifact of the edit tool on this Windows env. If the next agent edits this file via the same tool, the cycle will repeat. **Mitigation**: ensure the file is committed as LF (git will store it that way given the file contents), then re-normalize working tree if needed before final commit. Not a code defect — just a workflow quirk.
- **`bin/agents-manager.cmd` and `bin/install.cmd`** are still showing as untracked in `git status` (from T2's Python UX work). Pre-existing — not my lane.
- The fix only addresses the **install** subcommand. `doctor --fix` (bash L420) still calls `cmd_skills add --all` without a scope argument; works fine since `cmd_skills_add` defaults to `both`, but if a user wanted `--scope local` doctor-fix, no flag exists. Out of scope for this fix loop.

## Suggested review focus

1. **`bin/agents-manager.ps1:230-240`** — verify the `Skills-Add-Cmd @("--all", "--yes", "--$($p.Skills)")` arg shape matches what `Skills-Add-Cmd` actually accepts. I tested it works, but the `-Skills`/`-Scope` flags in `Parse-InstallFlags` were added at the same time and the chain depends on them.
2. **`bin/agents-manager:114,129`** — verify `--skills`/`--scope` validation: bogus values reject with `unknown flag: --skills must be both|global|local|skip (got 'bogus')`. Tested with one bogus value; not tested with all 4 invalid values (e.g., `--skills bothX`).
3. **EOL on `bin/agents-manager`** — confirm working tree is LF (I normalized after the edit tool wrote CRLF). If master re-edits this file via the same tool, normalization may be needed again.
4. **PSScriptAnalyzer +4 from `Skills:` block** — confirm 151 is acceptable to the user. If 147 is the hard gate, refactor 4 `Write-Host` calls to `Write-Output` (style break) or `Write-Information` (PowerShell 5+ only).

## Self-critique

- **Did I do my job?** Yes. All 8 listed tasks implemented and verified by at least one acceptance gate. Headline bug (`--skills` rejected by dispatcher) fixed on every dispatch path (Python wrapper, bash direct, PowerShell direct, both PascalCase and lowercase flags).
- **What might I have missed?**
  - Did not test with `--skills=local` (the `=value` form). Tested both `--skills local` and `--scope both` separately. The `=*` case is in the parse loop and matches the same regex pattern as `--git=*`, which I verified works. Low risk.
  - Did not test the `cmd_skills add` non-`-all` path through install (e.g., what if a user wanted to install just one specific skill during install?). Out of scope — the install subcommand installs ALL skills per the plan.
  - Did not verify the PSScriptAnalyzer count from the committed HEAD's perspective (my tooling had escaping issues with `$tmp = New-TemporaryFile`). I confirmed working-tree count is 151 and manually diffed line ranges; that's sufficient evidence the +4 came from my Skills: block.
- **What did I assume without evidence?**
  - That `Skills-Add-Cmd @("--all", "--yes", "--$($p.Skills)")` is the right arg shape. Verified by Gate 9 actually calling it (it ran and printed "Nothing to do" — meaning all skills were already installed, but it parsed correctly).
  - That the git-HEAD `.gitignore` was LF (verified via `git show` byte scan: 43 LF, 0 CRLF — confirmed).

READY_FOR_REVIEW: true