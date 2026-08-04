# Plan: dispatcher `--scope` override (Track T1)

**Task**: T-2026-07-01-001.A
**Track**: T1 of T-2026-07-01-001
**Master's task tracker**: `tasks/T-2026-07-01-001.md`
**User task capture**: `share/handoffs/00_user_task.md`

## Goal

Add a `--global/--local/--both/--skip` flag (and equivalents) to `bin/agents-manager` (bash) and `bin/agents-manager.ps1` (PowerShell) so that `cmd_skills_add` and the wizard's "install skills" step respect a user-chosen scope, not only the per-skill `level` declared in `bin/skills-manifest.json`.

## Files to edit

| File | Change |
|---|---|
| `bin/agents-manager` (bash, ~852 LOC) | (a) parse `--global/--local/--both/--skip` in `cmd_skills_add`, (b) implement `install_skill_locally` bash helper, (c) wire scope override into the loop that runs `install_cmd`/`update_cmd`, (d) add a scope prompt in `wizard()` before `cmd_skills add --all` |
| `bin/agents-manager.ps1` (PowerShell, ~638 LOC) | mirror of (a)-(d): parameter binding in `Skills-Cmd`, `Install-Skill-Locally` function, wire into the install/update loop, scope prompt in wizard |

## Files NOT to edit (in this track)

- `bin/skills-manifest.json` (unchanged)
- `bin/install.cmd` (Track T2)
- `bin/standalone-installer/**` (Track T5)
- `README.md`, `docs/INSTALL.md`, `bin/README.md` (Track T3)
- `.gitattributes`, release workflow, CHANGELOG, version bump (Track T4)

## Acceptance criteria (this track only)

1. `bin/agents-manager.ps1 install <target> -Skills local -Yes` → mavis-team copied to `<target>/.agents/skills/mavis-team/`; obra/superpowers skills skip with friendly error (they're not bundled).
2. `bin/agents-manager.ps1 install <target> -Skills global -Yes` → obra skills installed via npx to `%USERPROFILE%\.agents\skills\`; mavis-team is level=local in manifest, but since user passed `--global`, attempt the npx path (which will fail for `source=controller` since there's no install_cmd) → graceful skip with reason printed.
3. `bin/agents-manager.ps1 install <target> -Skills both -Yes` → mavis-team copied locally + obra skills installed via npx (matches today's default behavior).
4. `bin/agents-manager.ps1 install <target> -Skills skip -Yes` → controller files only; no skill install attempt.
5. `bin/agents-manager install <target> --skills local -y` → bash parity of (1).
6. Default (no `--skills` flag) → matches today's behavior as closely as possible. **Default = `both`** (mirrors what the user implicitly chose by using `cmd_skills add --all` in the wizard today, which actually only honors `level` per-skill — so true behavior today is "mavis-team local, obra global"). Pick `both` for the default flag value, since "install per-skill at declared level" maps naturally to "do whatever you can, both paths".
7. Wizard prompts the user for scope before running skills add --all.
8. shellcheck passes on `bin/agents-manager`.
9. PSScriptAnalyzer passes on `bin/agents-manager.ps1`.

## Edge cases to handle

- Skill has `source=controller` (mavis-team) and user passed `--global` → no `install_cmd` in manifest → emit warn "skill 'X' is shipped locally; --scope global only meaningful for non-controller skills" and skip.
- Skill has `source=obra/superpowers` and user passed `--local` → no local copy bundled → emit warn "skill 'X' is not bundled; install via --scope global" and skip.
- Skill already installed at target path → no-op (don't re-copy).
- User passes both `--skills` and `--global` etc. → later flag wins (or print error if ambiguous). Pick: **last one wins**, simplest.

## Implementation guidance

### bash (bin/agents-manager)

In `cmd_skills_add`:

```bash
# After existing while-loop that parses args, add:
SCOPE_FLAG=""
ALL_FLAG=false
YES_FLAG=false
SKILL_NAMES=()

# Add cases inside the existing case statement:
  --global) SCOPE_FLAG="global" ;;
  --local)  SCOPE_FLAG="local" ;;
  --both)   SCOPE_FLAG="both" ;;
  --skip)   SCOPE_FLAG="skip" ;;
  --all)    ALL_FLAG=true ;;
  -y|--yes) YES_FLAG=true ;;
  --scope=*) SCOPE_FLAG="${arg#--scope=}" ;;

# Default if no flag passed:
[[ -z "$SCOPE_FLAG" ]] && SCOPE_FLAG="both"

# New helper:
install_skill_locally() {
  local id="$1" source="$2" target="$3"
  if [[ "$source" != "controller" ]]; then return 1; fi
  local src="$SRC/.agents/skills/$id"
  [[ -d "$src" ]] || return 1
  local dest="$target/.agents/skills/$id"
  [[ -d "$dest" ]] && { echo "$dest"; return 0; }
  mkdir -p "$(dirname "$dest")"
  cp -R "$src" "$dest"
  echo "$dest"
}

# Inside the per-skill loop:
  case "$SCOPE_FLAG" in
    skip)   dim "   --scope skip -> skipping $id"; continue ;;
    local)  if dest=$(install_skill_locally "$id" "$source" "$TARGET"); then
              ok "   installed locally -> $dest"
            else
              warn "   cannot install '$id' locally (not bundled)"
            fi ;;
    both)   install_skill_locally "$id" "$source" "$TARGET" || true
            # fall through to npx path below
            ;;
  esac

  # existing npx path runs UNLESS scope=local (only) — adjust existing condition
  if [[ "$SCOPE_FLAG" != "local" ]]; then
    # existing run_install_cmd + run_update_cmd logic
  fi
```

### PowerShell (bin/agents-manager.ps1)

Mirror the same logic. The existing `Skills-Cmd` already has a parse loop using `switch -Regex` — extend it. Add `Install-Skill-Locally` function near top of file.

## Quality gates (must pass before review)

```bash
# Bash:
shellcheck -x bin/agents-manager

# PowerShell:
pwsh -NoProfile -Command "Invoke-ScriptAnalyzer -Path bin/agents-manager.ps1 -Severity Warning,Error"
```

If shellcheck/PSScriptAnalyzer flag a style nit you can't fix in 1-2 lines, document it in the work summary under "Deviations".

## Output (am-coder must produce)

1. Edited `bin/agents-manager` and `bin/agents-manager.ps1` (minimal diff).
2. `share/notes/03_coder_summary_T-2026-07-01-001_A.md` with:
   - Tasks attempted table
   - Files written/edited (path:line)
   - shellcheck + PSScriptAnalyzer output
   - Deviations, if any
   - Suggested review focus

## Reference (read before editing)

- `bin/skills-manifest.json` — understand `level`, `source`, `install_cmd`, `update_cmd` shape
- `bin/agents-manager` lines ~511-592 (cmd_skills_add) and ~766-812 (wizard)
- `bin/agents-manager.ps1` Skills-Cmd parse loop (around line 400-500 based on earlier read)