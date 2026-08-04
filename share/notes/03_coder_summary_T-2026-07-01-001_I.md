# Coder Summary — T-2026-07-01-001 / I (fix loop 2 of 3)

**Date:** 2026-07-03 13:15
**Sub-agent:** coder
**Loop:** fix-loop 2 (per `share/messages/master-to-coder-T-2026-07-01-001-I.md` + dispatch prompt)
**Review report:** N/A — this loop was triggered directly by master after loop G emptied `bin/agents-manager`

## Tasks attempted

| ID | Status | Notes |
|----|--------|-------|
| P1T-fix-1a — restore `bin/agents-manager` from HEAD | done | `git checkout HEAD -- bin/agents-manager` restored 851 lines / 29427 bytes; bash file was at 0 bytes (empty-file trap confirmed) |
| P1T-fix-1b — re-apply G-intent: bash `--skills|--scope` parse + chain | done | L96 (added `SCOPE=""`); L102-104 (3 parse cases `--skills|--scope`, `=*`); L112 (validation); L158-161 (chain block); 1 helper line in `cmd_skills_add` L527 to accept `--both|--skip` (without this, the G-default `cmd_skills add --all --both` would have errored) |
| P1T-fix-2 — rename `$AllArgs` → `$RemainingArgs` in `bin/agents-manager.ps1` | done | L11 (param declaration), L18 (comment), L705 (dispatch body loop); 3 occurrences (dispatch said "~4", file actually had 3) |

## Files written / edited

- `bin/agents-manager:96` — added `SCOPE=""` to `cmd_install` local declarations
- `bin/agents-manager:102-104` — added 3 parse cases: `--skills|--scope)`, `--skills=*)`, `--scope=*)`
- `bin/agents-manager:112` — added `case "$SCOPE" in both|global|local|skip|"") ... esac` validation
- `bin/agents-manager:158-161` — added "Skills: chain to cmd_skills add unless --skills skip" block + `cmd_skills add --all "--$SCOPE"` invocation
- `bin/agents-manager:527` — added `--both|--skip) shift` case to `cmd_skills_add` (no-op for both — per-skill level decides)
- `bin/agents-manager.ps1:11` — `[string[]]$AllArgs` → `[string[]]$RemainingArgs`
- `bin/agents-manager.ps1:18` — comment text `$AllArgs` → `$RemainingArgs`
- `bin/agents-manager.ps1:705` — `foreach ($a in $AllArgs)` → `foreach ($a in $RemainingArgs)`

## Commands run

```
# Restore + verify (before any edit)
git checkout HEAD -- bin/agents-manager                   # OK; 851 LF lines restored
python3 file_stats bin/agents-manager                    # 851 LF / 851 CRLF / 29427 bytes
wc -l bin/agents-manager  # (via python)                 # 851 → 861 (after edits)

# Edit verification
python3 find_lines.py bin/agents-manager                 # 4 hits @ L96, L112, L158, L527
python3 check_rename.py bin/agents-manager.ps1            # AllArgs=0, RemainingArgs=3

# Gate runs (Windows, IS_WINDOWS=True → routes to .ps1)
python3 bin/agents-manager.py --version                  # "agents-manager 0.11.0" (exit 0)
python3 bin/agents-manager.py install . --git skip --dry-run --yes   # exit 0
                                                           # → shows "WOULD run: Skills-Add-Cmd --all --yes --both (dry run)"
python3 bin/agents-manager.py skills add --all --local --yes        # exit 0
                                                           # → "Nothing to do" (all 9 required global skills already installed)
python3 bin/agents-manager.py skills add --all --skills local --yes # exit 2
                                                           # → argparse error: "unrecognized arguments: --skills"
python3 -m py_compile bin/agents-manager.py bin/install.py bin/standalone-installer/install.py  # silent (OK)

# Lint
shellcheck --shell=bash (LF-normalized content)           # exit 0, no output
pwsh Invoke-ScriptAnalyzer bin/agents-manager.ps1 -Severity Warning,Error  # 151 Warnings (all pre-existing patterns: 133 PSAvoidUsingWriteHost, 14 PSUseApprovedVerbs, 4 misc); 0 Errors
powershell ParseFile bin/agents-manager.ps1               # syntax OK

# EOL check
python3 -c "d=open('bin/agents-manager','rb').read(); print('LF:',d.count(b'\n'),'CRLF:',d.count(b'\r\n'))"
# LF: 861 CRLF: 861  (gate: LF > 800 ✓, CRLF <= LF ✓)
```

## Tests run

- **`python3 bin/agents-manager.py install . --git skip --dry-run --yes`** — PASS (exit 0). Goes through PowerShell route (`-File bin/agents-manager.ps1`). `.ps1`'s pre-existing `Install-Cmd` and `Parse-InstallFlags` already support `--skills`; chains to `Skills-Add-Cmd --all --yes --both` (dry-run preview printed).
- **`python3 bin/agents-manager.py skills add --all --local --yes`** — PASS (exit 0). Reaches `.ps1` body loop with `--all` intact (parameter-binding bug FIXED by rename). Skills-Add-Cmd finds all 9 required skills already installed → "Nothing to do." (intent satisfied; dispatcher isn't parameter-binding anymore).
- **`python3 bin/agents-manager.py skills add --all --skills local --yes`** — FAIL (exit 2). Python argparse rejects unknown `--skills` flag for skills subcommand. See "Known issues" #1.
- **`shellcheck --shell=bash`** (LF-normalized input) — PASS (no output, exit 0).
- **`psscriptanalyzer -Severity Warning,Error`** — 151 Warnings, 0 Errors. All pre-existing (`Invoke-ScriptAnalyzer ... -Severity Error` returns 0). Group by RuleName: 133 PSAvoidUsingWriteHost, 14 PSUseApprovedVerbs, 4 misc. None on my edited lines (11/18/705 — verified with `Where-Object Line -in 11,18,705`). Not introduced by this loop.
- **Python compile** — PASS (silent).

## Deviations from plan

1. **Added 1 case to `cmd_skills_add`** (`bin/agents-manager:527`): the dispatch said "if SCOPE != skip, call `cmd_skills add --all "--$SCOPE"`". With Python's default `--skills both` (which is what Python always sends), SCOPE="both" → call `cmd_skills add --all --both`. The HEAD version of `cmd_skills_add` had no `--both` case (only `--global|--local`), so the chain would have errored. I added `--both|--skip) shift ;;` as no-op accept-and-continue to make the G-intent chain functional end-to-end. This was implied by the dispatch's T1-state description (`--both/--skip` on `cmd_skills_add`) which did not survive in HEAD.
2. **Bash file size 29952 bytes, not >30000**: dispatch's size gate said "MUST be > 30000 bytes". Restored-from-HEAD was 29427 bytes; my 3 edits added 525 bytes → 29952. 48 bytes shy of the heuristic threshold but well above the empty-file trap (which is what the gate guards against). Did not add padding.
3. **`bin/agents-manager.ps1` RemainingArgs count = 3, not 4+**: dispatch said "~4 occurrences" and acceptance gate said "4+ hits" — but the file actually had only 3 `$AllArgs` references (param + comment + dispatch loop). All 3 renamed; 0 `AllArgs` remaining.

## Known issues / TODOs left in code

1. **`bin/agents-manager.py` argparse for skills subcommand rejects `--skills`/`--scope`** (MEDIUM — pre-existing drift, surfaced by dispatch gate `skills add --all --skills local --yes`). Python only declares `--global|--local|--both|--skip` as separate flags for the skills subcommand (line 275-282); `--skills|--scope` is only defined for the **install** subcommand (line 254). Resolution: add `p_skills.add_argument("--skills", "--scope", choices=["both","global","local","skip"])`. **Out of scope** for this loop (dispatch constrained to bash + .ps1 only — Python not in `Files expected`); surfaced here for master's dispatch decision. Recorded in `share/notes/04_warns_register_T-2026-07-01-001.md` per rule §16.
2. **Bash file works with CRLF in working tree** (LOW — Windows-specific). `core.autocrlf=true` on this Windows machine causes `git checkout` to write CRLF in the working tree. `bash -n bin/agents-manager` direct invocation from Git Bash/MSYS would fail on the `\r` in `c() {`. On Linux/macOS, autocrlf is `false`, so the file is LF and works. Existing condition (HEAD was the same); not introduced here.

## Suggested review focus

- **`bin/agents-manager:96-112`** — `cmd_install` new parse cases + SCOPE validation. Bash 4+ syntax, no new bash idioms.
- **`bin/agents-manager:158-161`** — chain block. The `cmd_skills add --all "--$SCOPE"` form relies on `cmd_skills_add` accepting the scope flag (now `both|global|local|skip` all work). If `cmd_skills_add` is later extended to reject `--both|--skip` again, the install flow breaks for `--skills both` (Python's default).
- **`bin/agents-manager:527`** — `cmd_skills_add --both|--skip` are no-ops. Confirm "per-skill level decides" is the right semantics (vs. treating `--both` as "run both global + local install branches for each skill"). If the dispatcher should run both, the loop in `cmd_skills_add` needs branching, not just `shift`.
- **`bin/agents-manager.ps1:11/18/705`** — three `$AllArgs` rename sites confirmed.

## Self-critique

- **Did I do my job?** Yes. Restored the bash file (verified not 0 bytes before AND after each edit per the dispatch's CRITICAL rule), re-applied G's install parse + chain intent, and renamed `$AllArgs` to `$RemainingArgs`. All in-scope edits are minimal (10 net lines added across two functions in bash; 3 token-level renames in .ps1).
- **What might I have missed?** The `--both|--skip` semantics in `cmd_skills_add` — I treated them as no-ops (per-skill manifest level decides). This matches the `.ps1` dispatcher's behavior (it has explicit `--both` branching that honors `source=controller` ⇒ local, else ⇒ global). The bash version is a simplified no-op equivalent that may diverge if a per-skill level is added later. Documented as MEDIUM-mild in Self-critique.
- **What did I assume without evidence?** I assumed `core.autocrlf=true` on this Windows host would re-checkout the bash file as CRLF after I write LF content — verifiable: HEAD was checked out as 861 LF + 861 CRLF (matched), so my edits inherit the same CRLF state. The EOL gate allows `CRLF <= LF`, so this passes.
- **Empty-file trap?** Verified file size before (29427 bytes), after each edit (29952 bytes), and at end (29952 bytes). Never 0 bytes. ✓
