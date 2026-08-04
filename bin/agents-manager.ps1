# agents-manager.ps1 — unified CLI for the agents-manager controller (PowerShell)
# Mirror of bin/agents-manager. v0.10.0+
#
# Usage: .\agents-manager.ps1 [<subcommand>] [args]
#   No args = interactive wizard.
[CmdletBinding()]
param(
    # Captures all subcommand + arg tokens. The per-subcommand parse loops
    # below split it into subcommand-specific flags.
    [Parameter(ValueFromRemainingArguments = $true)]
    [string[]]$RemainingArgs
)

# We intentionally do NOT declare switch parameters for -Yes, -Skills, etc.
# Those flags are matched by the per-subcommand parse loops below. Declaring
# them here would require PowerShell-style casing (e.g. -Skills not --skills)
# and would fail the bind when invoked with bash-style --skills / -All / etc.
# The single positional [string[]]$RemainingArgs accepts any combination of
# args and routes them to the parse loop.

$ScriptVersion = "v0.11.0"
$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$Src = (Resolve-Path (Join-Path $ScriptDir "..")).Path
$ManifestPath = Join-Path $ScriptDir "skills-manifest.json"

$USE_COLOR = $Host.UI.SupportsVirtualTerminal -and -not $env:NO_COLOR
if ($USE_COLOR) {
    $RED = "`e[31m"; $GREEN = "`e[32m"; $YELLOW = "`e[33m"
    $BLUE = "`e[34m"; $BOLD = "`e[1m"; $DIM = "`e[2m"; $RESET = "`e[0m"
} else {
    $RED = ''; $GREEN = ''; $YELLOW = ''; $BLUE = ''; $BOLD = ''; $DIM = ''; $RESET = ''
}

$YES = $false

function err  { Write-Host "${RED}ERROR:${RESET} $args" -ForegroundColor Red }
function warn { Write-Host "${YELLOW}WARN:${RESET}  $args" -ForegroundColor Yellow }
function ok   { Write-Host "${GREEN}OK${RESET}    $args" }
function info { Write-Host "${BLUE}..${RESET}    $args" }
function dim  { Write-Host "${DIM}$args${RESET}" }

$manifest = $null
function Load-Manifest {
    if ($null -eq $manifest) {
        $script:manifest = Get-Content $ManifestPath -Raw | ConvertFrom-Json
    }
}

function Get-ManifestField {
    param([string]$Id, [string]$Field)
    Load-Manifest
    $skill = $manifest.skills | Where-Object { $_.id -eq $Id } | Select-Object -First 1
    if ($null -eq $skill) { return "" }
    $val = $skill.$Field
    if ($null -eq $val) { return "" }
    if ($val -is [bool]) { return "$val".ToLower() }
    return "$val"
}

function Test-SkillInstalled {
    param([string]$Id, [string]$Level, [string]$ProjectRoot = ".")
    $path = if ($Level -eq "global") {
        Join-Path $HOME ".agents/skills/$Id/SKILL.md"
    } else {
        Join-Path $ProjectRoot ".agents/skills/$Id/SKILL.md"
    }
    Test-Path $path
}

# Copy a controller-shipped skill from the source checkout to the target project.
# Returns the destination path on success (whether newly copied or already present);
# returns $null if the skill is not bundled with the controller.
function Install-Skill-Locally {
    param([string]$Id, [string]$Source, [string]$Target)
    if ($Source -ne "controller") { return $null }
    $src = Join-Path $Src ".agents/skills/$Id"
    if (-not (Test-Path $src)) { return $null }
    $dest = Join-Path $Target ".agents/skills/$Id"
    if (Test-Path $dest) { return $dest }
    New-Item -Path (Split-Path -Parent $dest) -ItemType Directory -Force | Out-Null
    Copy-Item -Path $src -Destination $dest -Recurse -Force
    return $dest
}

function Resolve-Target {
    param([string]$Path)
    if (-not (Test-Path $Path)) { throw "target '$Path' does not exist" }
    (Resolve-Path $Path).Path
}

# Install chub (context-hub) globally via npm. Called during install (v0.21.0+).
# Idempotent: skips if already on PATH. Warns and continues on failure; agents
# fall back to the on-demand install path in agents_manager/SKILL.md.
function Install-Chub {
    param([bool]$DryRun)
    if (Get-Command chub -ErrorAction SilentlyContinue) {
        Write-Host "  OK   chub (already on PATH)"
        return
    }
    if (-not (Get-Command npm -ErrorAction SilentlyContinue)) {
        warn "npm not on PATH - chub not installed. agents will fall back to on-demand install per master SKILL.md."
        return
    }
    if ($DryRun) {
        Write-Host "  WOULD run: npm install -g @aisuite/chub (dry run)"
        return
    }
    Write-Host "  ..   npm install -g @aisuite/chub"
    $output = & npm install -g @aisuite/chub 2>&1
    if ($LASTEXITCODE -eq 0) {
        ok "chub installed"
    } else {
        warn "chub install failed. agents will try on-demand install per master SKILL.md."
    }
}

# Parse a flag-style arg list: returns a hashtable with Target, DryRun, GitMode, Skills (or whatever flags).
# Accepts both bash-style (--dry-run, --git=M, --skills=local) and PowerShell PascalCase (-DryRun, -Git M, -Skills local)
# on every documented install flag. This makes the install subcommand accept the same args from both wrappers.
function Parse-InstallFlags {
    param([string[]]$Rest)
    $Target = "."
    $DryRun = $false
    $GitMode = "auto"
    $Skills = "both"
    $ChubGlobal = $false
    for ($i = 0; $i -lt $Rest.Count; $i++) {
        $a = $Rest[$i]
        switch -Regex ($a) {
            '^-{1,2}(dry-?run|DryRun)$'      { $DryRun = $true; continue }
            '^-{1,2}(yes|Y)$'                { continue }
            '^-{1,2}[gG]it=(.+)$'            { $GitMode = $Matches[1]; continue }
            '^-{1,2}[gG]it$'                 {
                if ($i + 1 -lt $Rest.Count) { $GitMode = $Rest[$i + 1]; $i++ }
                continue
            }
            '^-{1,2}(skills|scope)=(.*)$'    { $Skills = $Matches[2].ToLower(); continue }
            '^-{1,2}(skills|scope)$'         {
                if ($i + 1 -lt $Rest.Count) { $Skills = $Rest[$i + 1].ToLower(); $i++ }
                continue
            }
            '^-{1,2}(chub-?global|ChubGlobal)(?:=(true|false))?$' {
                if ($Matches.Count -gt 2 -and $Matches[2]) { $ChubGlobal = $Matches[2].ToLower() -eq 'true' }
                else { $ChubGlobal = $true }
                continue
            }
            '^-'                 { err "unknown flag: $a"; return $null }
            default              { $Target = $a }
        }
    }
    return @{ Target = $Target; DryRun = $DryRun; GitMode = $GitMode; Skills = $Skills; ChubGlobal = $ChubGlobal }
}

function Install-Cmd {
    param([string[]]$Rest)
    $p = Parse-InstallFlags $Rest
    if ($null -eq $p) { return 1 }
    if ($p.GitMode -notin @("auto", "prompt", "skip")) {
        err "--git must be auto|prompt|skip (got '$($p.GitMode)')"; return 1
    }
    if ($p.Skills -notin @("both", "global", "local", "skip")) {
        err "-Skills must be both|global|local|skip (got '$($p.Skills)')"; return 1
    }
    if (-not (Test-Path $Src/opencode.jsonc)) {
        err "$Src does not look like an agents-manager checkout"; return 1
    }
    $T = Resolve-Target $p.Target

    Write-Host "${BOLD}agents-manager installer $ScriptVersion${RESET}"
    Write-Host "  Source: $Src"
    Write-Host "  Target: $T"
    if ($p.DryRun) { Write-Host "  Mode:   DRY RUN (no changes will be written)" }
    Write-Host ""

    function Copy-Safe([string]$Rel) {
        $dest = Join-Path $T $Rel
        if (Test-Path $dest) { Write-Host "  SKIP $Rel (already exists)" }
        elseif ($p.DryRun) { Write-Host "  COPY $Rel (dry run)" }
        else {
            Copy-Item -Path (Join-Path $Src $Rel) -Destination $dest -Recurse -Force
            Write-Host "  OK   $Rel"
        }
    }

    # Install chub-gate opencode plugin + chub-validate skill (v0.22.0+).
    # Project-local by default; with -Global also copies to ~/.config/opencode/.
    function Install-ChubAssets {
        param([bool]$DryRun, [bool]$Global)
        $pluginSrc = Join-Path $Src "agents_manager/chub-gate/chub-gate.ts"
        $skillSrc  = Join-Path $Src "agents_manager/chub-validate/SKILL.md"
        if (-not (Test-Path $pluginSrc) -or -not (Test-Path $skillSrc)) {
            warn "chub-gate source not found at $pluginSrc or $skillSrc - skipping."
            return
        }
        $pluginDst = Join-Path $T ".opencode/plugins/chub-gate.ts"
        $skillDir  = Join-Path $T ".opencode/skills/chub-validate"
        $skillDst  = Join-Path $skillDir "SKILL.md"
        if (Test-Path $pluginDst) { Write-Host "  SKIP .opencode/plugins/chub-gate.ts (already exists)" }
        elseif ($DryRun) { Write-Host "  COPY .opencode/plugins/chub-gate.ts (dry run)" }
        else {
            New-Item -Path (Split-Path $pluginDst) -ItemType Directory -Force | Out-Null
            Copy-Item -Path $pluginSrc -Destination $pluginDst -Force
            Write-Host "  OK   .opencode/plugins/chub-gate.ts"
        }
        if (Test-Path $skillDst) { Write-Host "  SKIP .opencode/skills/chub-validate/SKILL.md (already exists)" }
        elseif ($DryRun) { Write-Host "  COPY .opencode/skills/chub-validate/SKILL.md (dry run)" }
        else {
            New-Item -Path $skillDir -ItemType Directory -Force | Out-Null
            Copy-Item -Path $skillSrc -Destination $skillDst -Force
            Write-Host "  OK   .opencode/skills/chub-validate/SKILL.md"
        }
        if (-not $Global) { return }
        $gPluginDir = Join-Path $HOME ".config/opencode/plugins"
        $gSkillDir  = Join-Path $HOME ".config/opencode/skills/chub-validate"
        $gPluginDst = Join-Path $gPluginDir "chub-gate.ts"
        $gSkillDst  = Join-Path $gSkillDir "SKILL.md"
        if (Test-Path $gPluginDst) { Write-Host "  SKIP ~/.config/opencode/plugins/chub-gate.ts (already exists)" }
        elseif ($DryRun) { Write-Host "  COPY ~/.config/opencode/plugins/chub-gate.ts (dry run)" }
        else {
            New-Item -Path $gPluginDir -ItemType Directory -Force | Out-Null
            Copy-Item -Path $pluginSrc -Destination $gPluginDst -Force
            Write-Host "  OK   ~/.config/opencode/plugins/chub-gate.ts"
        }
        if (Test-Path $gSkillDst) { Write-Host "  SKIP ~/.config/opencode/skills/chub-validate/SKILL.md (already exists)" }
        elseif ($DryRun) { Write-Host "  COPY ~/.config/opencode/skills/chub-validate/SKILL.md (dry run)" }
        else {
            New-Item -Path $gSkillDir -ItemType Directory -Force | Out-Null
            Copy-Item -Path $skillSrc -Destination $gSkillDst -Force
            Write-Host "  OK   ~/.config/opencode/skills/chub-validate/SKILL.md"
        }
    }

    Write-Host "${BOLD}Files:${RESET}"
    Copy-Safe "opencode.jsonc"
    Copy-Safe "CLAUDE.md"
    Write-Host ""
    Write-Host "${BOLD}Directories:${RESET}"
    Copy-Safe "agents_manager"
    Copy-Safe "share"
    Copy-Safe "tasks"
    if ($p.DryRun) { Write-Host "  MKDIR .agents/skills (dry run)" }
    else { New-Item -Path (Join-Path $T ".agents/skills") -ItemType Directory -Force | Out-Null }
    Copy-Safe ".agents/skills/mavis-team"
    Write-Host ""
    Write-Host "${BOLD}Gitignore:${RESET}"
    $marker = "# agents-manager $ScriptVersion"
    $gi = Join-Path $T ".gitignore"
    if (-not (Test-Path $gi)) {
        if ($p.DryRun) { Write-Host "  CREATE .gitignore (dry run)" }
        else {
            @"
$marker
# agents-manager runtime artifacts
share/notes/02_secrets_*.md
share/screenshots/
share/notes/99_progress_*.md
"@ | Out-File -FilePath $gi -Encoding utf8
            Write-Host "  OK   .gitignore (created)"
        }
    } elseif (-not (Select-String -Path $gi -Pattern ([regex]::Escape($marker)) -Quiet)) {
        if ($p.DryRun) { Write-Host "  APPEND .gitignore (dry run)" }
        else {
            @"

$marker
share/notes/02_secrets_*.md
share/screenshots/
share/notes/99_progress_*.md
"@ | Out-File -FilePath $gi -Append -Encoding utf8
            Write-Host "  OK   .gitignore (appended)"
        }
    } else {
        Write-Host "  SKIP .gitignore (already has agents-manager entries)"
    }
    Write-Host ""
    Write-Host "${BOLD}Git:${RESET}"
    if (Test-Path (Join-Path $T ".git")) {
        Write-Host "  SKIP .git (already initialized)"
    } elseif ($p.GitMode -eq "skip") {
        Write-Host "  SKIP git init (-Git skip)"
    } elseif (-not (Get-Command git -ErrorAction SilentlyContinue)) {
        warn "git CLI not on PATH - skipping git init (install continues)."
    } else {
        if ($p.GitMode -eq "prompt" -and -not $YES -and -not $p.DryRun) {
            $choices = @(
                [System.Management.Automation.Host.ChoiceDescription]::new("&Yes", "Run git init + initial commit now."),
                [System.Management.Automation.Host.ChoiceDescription]::new("&No", "Skip git init.")
            )
            $pick = $Host.UI.PromptForChoice("Git init", "Initialize git in $T?", $choices, 0)
            if ($pick -ne 0) { Write-Host "  SKIP git init (declined)"; return }
        }
        if ($p.DryRun) { Write-Host "  GIT init + add + commit (dry run)" }
        else {
            & git -C $T init -q -b "main" *>$null
            if ($LASTEXITCODE -ne 0) { & git -C $T init -q *>$null }
            & git -C $T add -A *>$null
            & git -C $T diff --cached --quiet *>$null
            if ($LASTEXITCODE -eq 0) {
                Write-Host "  OK   .git (initialized, nothing to commit)"
            } else {
                & git -C $T -c "user.email=agents-manager@local" -c "user.name=agents-manager" commit -q -m "Initial commit" *>$null
                Write-Host "  OK   .git (initialized + initial commit)"
            }
        }
    }
    Write-Host ""
    Write-Host "${BOLD}Permissions:${RESET}"
    Write-Host "  (PowerShell scripts require no special permission. Bash scripts in bin/ are chmod +x'd by the bash installer.)"

    # Skills chain (after controller files copy). Default = both (matches v0.10.0
    # implicit behavior); -Skills skip disables; -DryRun prints what would happen.
    # NOTE: Skills-Add-Cmd only accepts --all (lowercase) for the all flag; it accepts
    # PascalCase -Global/-Local/-Both/-Skip for scope. We pass the long-form --all and
    # --yes, and PascalCase --skills-equivalent for scope.
    Write-Host ""
    Write-Host "${BOLD}Skills:${RESET}"
    if ($p.Skills -eq "skip") {
        Write-Host "  SKIP skills install (-Skills skip)"
    } elseif ($p.DryRun) {
        Write-Host "  WOULD run: Skills-Add-Cmd --all --yes --$($p.Skills) (dry run)"
    } else {
        Skills-Add-Cmd @("--all", "--yes", "--$($p.Skills)")
    }

    # chub (v0.21.0+): install by default so downstream agents don't skip on miss.
    Write-Host ""
    Write-Host "${BOLD}Chub (context-hub):${RESET}"
    Install-Chub -DryRun $p.DryRun

    # chub-gate plugin + chub-validate skill (v0.22.0+). Project-local by default;
    # --chub-global also copies to ~/.config/opencode/.
    Write-Host ""
    Write-Host "${BOLD}Chub-gate (plugin + skill):${RESET}"
    Install-ChubAssets -DryRun $p.DryRun -Global $p.ChubGlobal

    if ($p.DryRun) { Write-Host ""; Write-Host "DRY RUN complete - no changes were written."; return }

    Write-Host ""; ok "Done."
    Write-Host ""
    Write-Host "${BOLD}NEXT STEPS:${RESET}"
    Write-Host "  1. cd $T"
    Write-Host "  2. Run:  .\agents-manager.ps1 check ."
    Write-Host "  3. Run:  .\agents-manager.ps1 skills add --all --yes"
    Write-Host "  4. Run:  .\agents-manager.ps1 doctor ."
    Write-Host "  5. Open in OpenCode - the master agent is auto-routed"
    Write-Host ""
}

function Check-Cmd {
    param([string[]]$Rest)
    $Target = if ($Rest.Count -gt 0) { $Rest[0] } else { "." }
    $T = Resolve-Target $Target

    Write-Host "${BOLD}agents-manager check $ScriptVersion${RESET}"
    Write-Host "  Target: $T"
    Write-Host ""
    Write-Host "${BOLD}Controller files in $T${RESET}"
    $missing = @()
    foreach ($p in @("opencode.jsonc", "CLAUDE.md", "agents_manager", "share", "tasks", ".agents/skills/mavis-team")) {
        if (Test-Path (Join-Path $T $p)) { Write-Host "  OK    $p" }
        else { Write-Host "  MISS  $p"; $missing += $p }
    }
    Write-Host ""
    Write-Host "${BOLD}Required skills (manifest):${RESET}"
    Load-Manifest
    $total = 0; $installed = 0; $skillMiss = 0
    foreach ($s in $manifest.skills) {
        $total++
        $level = if ($s.level) { $s.level } else { "global" }
        if (Test-SkillInstalled -Id $s.id -Level $level -ProjectRoot $T) {
            Write-Host "  OK    $($s.id) ($level)"; $installed++
        } else {
            Write-Host "  MISS  $($s.id) ($level)"; $skillMiss++
        }
    }
    Write-Host ""
    Write-Host "Result: PASS=$installed  FAIL=$skillMiss  TOTAL=$total"
    if ($skillMiss -gt 0 -or $missing.Count -gt 0) { return 1 }
    return 0
}

function Doctor-Cmd {
    param([string[]]$Rest)
    $Target = "."; $Fix = $false
    foreach ($a in $Rest) {
        if ($a -eq "--fix") { $Fix = $true } else { $Target = $a }
    }
    if (-not (Test-Path $Target)) { err "target '$Target' does not exist"; return 1 }
    $T = Resolve-Target $Target

    Write-Host "${BOLD}agents-manager doctor $ScriptVersion${RESET}"
    Write-Host "  Target: $T"
    Write-Host ""
    $script:pass = 0; $script:warnN = 0; $script:fail = 0

    Write-Host "${BOLD}Controller files:${RESET}"
    foreach ($p in @("opencode.jsonc", "CLAUDE.md", "agents_manager", "share", "tasks")) {
        if (Test-Path (Join-Path $T $p)) { Write-Host "  ${GREEN}PASS${RESET}  $p"; $script:pass++ } else { Write-Host "  ${RED}FAIL${RESET}  missing $p"; $script:fail++ }
    }
    Write-Host ""; Write-Host "${BOLD}Required skills:${RESET}"
    $skillMiss = @()
    Load-Manifest
    foreach ($s in $manifest.skills) {
        $req = if ($s.required) { $s.required } else { $false }
        if (-not $req) { continue }
        $level = if ($s.level) { $s.level } else { "global" }
        if (Test-SkillInstalled -Id $s.id -Level $level -ProjectRoot $T) {
            Write-Host "  ${GREEN}PASS${RESET}  $($s.id) ($level)"; $script:pass++
        } else {
            Write-Host "  ${RED}FAIL${RESET}  missing $($s.id) ($level)"; $script:fail++
            $skillMiss += $s.id
        }
    }
    Write-Host ""; Write-Host "${BOLD}Tooling:${RESET}"
    if (Get-Command git -ErrorAction SilentlyContinue) {
        $gv = & git --version 2>$null
        Write-Host "  ${GREEN}PASS${RESET}  git CLI on PATH ($gv)"
        $script:pass++
    } else { Write-Host "  ${RED}FAIL${RESET}  git CLI not on PATH"; $script:fail++ }
    if (Get-Command opencode -ErrorAction SilentlyContinue) {
        Write-Host "  ${GREEN}PASS${RESET}  opencode CLI on PATH"; $script:pass++
    } else { Write-Host "  ${YELLOW}WARN${RESET}  opencode CLI not on PATH"; $script:warnN++ }
    if (Get-Command npx -ErrorAction SilentlyContinue) {
        Write-Host "  ${GREEN}PASS${RESET}  npx on PATH"; $script:pass++
    } else { Write-Host "  ${YELLOW}WARN${RESET}  npx not on PATH (Node.js required for global skills)"; $script:warnN++ }
    Write-Host ""; Write-Host "${BOLD}Target git state:${RESET}"
    if (Test-Path (Join-Path $T ".git")) { Write-Host "  ${GREEN}PASS${RESET}  target is a git repo"; $script:pass++ }
    else { Write-Host "  ${YELLOW}WARN${RESET}  target is not a git repo"; $script:warnN++ }
    Write-Host ""; Write-Host "Doctor: PASS=$script:pass WARN=$script:warnN FAIL=$script:fail"
    if ($script:fail -gt 0) { return 1 }
    return 0
}

function Uninstall-Cmd {
    param([string[]]$Rest)
    $Target = "."; $YesLocal = $false
    foreach ($a in $Rest) {
        switch ($a) {
            { $_ -in @("--yes", "-y") } { $YesLocal = $true }
            { $_ -like "-*" } {}
            default { $Target = $_ }
        }
    }
    $T = Resolve-Target $Target
    Write-Host "${BOLD}Uninstall from $T${RESET}"
    $paths = @("opencode.jsonc", "CLAUDE.md", "agents_manager", "share", "tasks", ".agents/skills/mavis-team")
    foreach ($p in $paths) { if (Test-Path (Join-Path $T $p)) { Write-Host "  will remove: $p" } }
    if (-not ($YesLocal -or $YES)) {
        $ans = Read-Host "  Proceed? Type 'yes' to confirm"
        if ($ans -ne "yes") { Write-Host "Aborted."; return 3 }
    }
    foreach ($p in $paths) {
        $full = Join-Path $T $p
        if (Test-Path $full) { Remove-Item -LiteralPath $full -Recurse -Force; Write-Host "  REMOVED $p" }
    }
    Write-Host ""; ok "Uninstall complete."
}

function Skills-Cmd {
    param([string[]]$Rest)
    $action = if ($Rest.Count -gt 0) { $Rest[0] } else { "list" }
    $tail = if ($Rest.Count -gt 1) { $Rest[1..($Rest.Count - 1)] } else { @() }
    switch ($action) {
        "list"   { Skills-List-Cmd $tail }
        "add"    { Skills-Add-Cmd $tail }
        "remove" { Skills-Remove-Cmd $tail }
        "which"  { Skills-Which-Cmd $tail }
        "update" { Skills-Update-Cmd $tail }
        default  { err "unknown skills subcommand: $action"; return 1 }
    }
}

function Skills-List-Cmd {
    param([string[]]$Rest)
    $filter = "all"
    foreach ($a in $Rest) {
        switch ($a) {
            "--required-only"  { $filter = "required" }
            "--installed-only" { $filter = "installed" }
            "--missing-only"   { $filter = "missing" }
            default {}
        }
    }
    Write-Host "${BOLD}Required skills:${RESET}"
    Write-Host ""
    Write-Host ("  {0,-30}  {1,-7}  {2,-10}  {3}" -f "SKILL", "LEVEL", "STATUS", "SOURCE")
    Write-Host ("  {0,-30}  {1,-7}  {2,-10}  {3}" -f "------------------------------", "-------", "----------", "-------------------------")
    Load-Manifest
    foreach ($s in $manifest.skills) {
        $level = if ($s.level) { $s.level } else { "global" }
        $req = if ($s.required) { $s.required } else { $false }
        $src = if ($s.source) { $s.source } else { "" }
        $status = if (Test-SkillInstalled -Id $s.id -Level $level) { "installed" } else { "missing" }
        switch ($filter) {
            "required"  { if (-not $req) { continue } }
            "installed" { if ($status -ne "installed") { continue } }
            "missing"   { if ($status -ne "missing") { continue } }
        }
        $color = if ($status -eq "installed") { $GREEN } else { $RED }
        Write-Host ("  {0,-30}  {1,-7}  {2}{3,-10}{4}  {5}" -f $s.id, $level, $color, $status, $RESET, $src)
    }
    Write-Host ""
    Write-Host "Tip:  .\agents-manager.ps1 skills add <name>...|--all [-Global|-Local|-Both|-Skip] [-Yes]"
}

function Skills-Which-Cmd {
    param([string[]]$Rest)
    $id = $Rest[0]
    if (-not $id) { err "usage: skills which <name>"; return 1 }
    Load-Manifest
    $level = Get-ManifestField -Id $id -Field "level"
    if (-not $level) { err "unknown skill: $id"; return 1 }
    $path = if ($level -eq "global") {
        Join-Path $HOME ".agents/skills/$id/SKILL.md"
    } else { Join-Path (Get-Location) ".agents/skills/$id/SKILL.md" }
    if (Test-Path $path) {
        Write-Host "${GREEN}installed${RESET}  $id ($level)"
        Write-Host "         $path"
    } else {
        Write-Host "${RED}missing${RESET}    $id ($level)"
        Write-Host "         expected at: $path"
        $ic = Get-ManifestField -Id $id -Field "install_cmd"
        if ($ic) { Write-Host "         install: $ic" }
        return 1
    }
}

function Skills-Add-Cmd {
    param([string[]]$Rest)
    $names = @(); $all = $false; $scope = "both"
    foreach ($a in $Rest) {
        switch ($a) {
            '--all'                        { $all = $true; continue }
            { $_ -in @('--global', '--local', '--both', '--skip') } {
                $scope = $_.Substring(2); continue
            }
            { $_ -in @('-Global', '-Local', '-Both', '-Skip') } {
                $scope = $_.Substring(1).ToLower(); continue
            }
            { $_ -in @('--yes', '-y') }   { continue }
            default                       { $names += $a }
        }
    }
    Load-Manifest
    if ($all) {
        foreach ($s in $manifest.skills) {
            $req = if ($s.required) { $s.required } else { $false }
            if (-not $req) { continue }
            $level = if ($s.level) { $s.level } else { "global" }
            if (Test-SkillInstalled -Id $s.id -Level $level) { continue }
            $names += $s.id
        }
    }
    if ($names.Count -eq 0) { dim "Nothing to do."; return 0 }
    $okCount = 0; $failCount = 0
    $projectRoot = (Get-Location).Path
    foreach ($id in $names) {
        $level = Get-ManifestField -Id $id -Field "level"
        $source = Get-ManifestField -Id $id -Field "source"
        $ic = Get-ManifestField -Id $id -Field "install_cmd"
        Write-Host ""; Write-Host "${BOLD}-> $id${RESET} (level=$level source=$source)"

        if ($scope -eq "skip") {
            dim "   --scope skip -> skipping $id"
            continue
        }

        # Determine which paths to attempt. Scope=both honors per-skill source
        # so the default output matches today's behavior.
        $doLocal = $false; $doGlobal = $false
        switch ($scope) {
            "local"  { $doLocal = $true }
            "global" { $doGlobal = $true }
            "both" {
                if ($source -eq "controller") { $doLocal = $true } else { $doGlobal = $true }
            }
        }

        # Local-install branch
        if ($doLocal) {
            $wasPresent = Test-Path (Join-Path $projectRoot ".agents/skills/$id")
            $localDest = Install-Skill-Locally -Id $id -Source $source -Target $projectRoot
            if ($localDest) {
                if ($wasPresent) { ok "   already installed at $localDest" }
                else { ok "   installed locally -> $localDest" }
                $okCount++
            } else {
                warn "   '$id' is not bundled; install via -Scope global"; $failCount++
            }
        }

        # Global-install branch (npx)
        if ($doGlobal) {
            if (-not $ic) {
                warn "   '$id' is shipped locally; -Scope global only meaningful for non-controller skills"; $failCount++
                continue
            }
            if (-not $YES -and -not $all) {
                $ans = Read-Host "   Run: $ic  [Y/n]"
                if (-not $ans) { $ans = "Y" }
                if ($ans -notmatch "^[Yy]") { dim "   skipped"; continue }
            }
            info "   running: $ic"
            & bash -c "$ic"
            if ($LASTEXITCODE -eq 0) { ok "   installed"; $okCount++ } else { err "   install failed"; $failCount++ }
        }
    }
    Write-Host ""; Write-Host "Skills: ok=$okCount fail=$failCount"
    if ($failCount -gt 0) { return 1 }
    return 0
}

function Skills-Remove-Cmd {
    param([string[]]$Rest)
    $id = $Rest[0]
    if (-not $id) { err "usage: skills remove <name>"; return 1 }
    Load-Manifest
    $level = Get-ManifestField -Id $id -Field "level"
    if ($level -ne "global") { err "skills remove only supports global skills"; return 1 }
    $cmd = "npx --yes skills remove https://github.com/obra/superpowers --skill $id -g -y"
    Write-Host "  $cmd"
    & bash -c "$cmd"
    if ($LASTEXITCODE -eq 0) { ok "removed $id" } else { err "remove failed"; return 1 }
}

function Skills-Update-Cmd {
    param([string[]]$Rest)
    $names = @(); $all = $false
    foreach ($a in $Rest) {
        switch ($a) {
            "--all" { $all = $true }
            { $_ -in @("--yes", "-y") } {}
            default { $names += $_ }
        }
    }
    Load-Manifest
    if ($all) {
        foreach ($s in $manifest.skills) {
            $level = if ($s.level) { $s.level } else { "global" }
            if ($level -eq "global") { $names += $s.id }
        }
    }
    foreach ($id in $names) {
        $uc = Get-ManifestField -Id $id -Field "update_cmd"
        if (-not $uc) { dim "  $id : no update_cmd in manifest"; continue }
        info "  $id : $uc"
        & bash -c "$uc"
    }
}

function Update-Cmd {
    param([string[]]$Rest)
    $u = Join-Path $ScriptDir "update.ps1"
    if (Test-Path $u) { info "Delegating to $u (v0.8 update logic)..."; & $u @Rest; return $LASTEXITCODE }
    err "update.ps1 not found at $u"; return 1
}

function Release-Cmd {
    param([string[]]$Rest)
    $sub = if ($Rest.Count -gt 0) { $Rest[0] } else { "zip" }
    $tail = if ($Rest.Count -gt 1) { $Rest[1..($Rest.Count - 1)] } else { @() }
    switch ($sub) {
        "zip" { & (Join-Path $ScriptDir "release-zip.ps1") @tail }
        "all" { & bash (Join-Path $ScriptDir "release-zip-all.sh") @tail }
        default { err "release subcommand: zip|all"; return 1 }
    }
}

function Lint-Cmd {
    param([string[]]$Rest)
    & bash (Join-Path $ScriptDir "lint-design.sh") @Rest
}

function Version-Cmd {
    Write-Host "agents-manager $ScriptVersion"
    Write-Host "  manifest: $ManifestPath"
    if (Test-Path $ManifestPath) {
        Load-Manifest
        Write-Host "  manifest skills: $($manifest.skills.Count) entries"
    }
}

function Help-Cmd {
    param([string[]]$Rest)
    $topic = if ($Rest.Count -gt 0) { $Rest[0] } else { "" }
    if (-not $topic) {
        @"
${BOLD}agents-manager${RESET} $ScriptVersion - unified CLI for the agents-manager controller

${BOLD}Usage${RESET}
  .\agents-manager.ps1                                    Interactive wizard
  .\agents-manager.ps1 <subcommand> [options...]

${BOLD}Subcommands${RESET}
  install       Install the controller in a target directory
  update        Update an existing install to a newer version
  check         Verify the controller files + required skills
  doctor        Diagnose common issues (-Fix to auto-remediate)
  uninstall     Remove the controller from a target directory
  skills        Manage required skills - list / add / remove / which / update
  release       Build release ZIP(s) (subcommand: zip|all)
  lint          Run advisory design linter on HTML mockups
  version       Print version + manifest info
  help          Show this help

${BOLD}Global flags${RESET}
  -Yes                Skip all interactive prompts (use defaults)
  `$env:NO_COLOR = 1   Disable colored output

${BOLD}Examples${RESET}
  .\agents-manager.ps1 install . -Git auto -Yes
  .\agents-manager.ps1 doctor . -Fix
  .\agents-manager.ps1 skills list -MissingOnly
  .\agents-manager.ps1 skills add -All -Yes
  .\agents-manager.ps1 update -Check
  .\agents-manager.ps1 help install
"@
    } else {
        switch ($topic) {
            "install" { Write-Host "agents-manager install -Usage: install [TARGET] [-Git M] [-Skills S] [-Yes] [-DryRun]  (skills scope: both|global|local|skip; default both)" }
            "skills"  { Write-Host "agents-manager skills -Usage: skills list|add|remove|which|update ... add accepts -Global|-Local|-Both|-Skip" }
            default   { err "no detailed help for '$topic'"; return 1 }
        }
    }
}

function Wizard {
    if ($YES) { Help-Cmd @(); return 0 }
    Write-Host "${BOLD}agents-manager $ScriptVersion${RESET} - interactive setup"
    Write-Host ""
    Write-Host "What would you like to do?"
    Write-Host "  1) Install the controller in a project"
    Write-Host "  2) Update an existing install"
    Write-Host "  3) Check / verify an install"
    Write-Host "  4) Run doctor (diagnose issues)"
    Write-Host "  5) Manage skills (list/add/remove)"
    Write-Host "  6) Uninstall the controller"
    Write-Host "  7) Show full help"
    Write-Host "  q) Quit"
    $choice = Read-Host "  Enter number [1-7] or 'q'"
    switch ($choice) {
        "1" {
            $t = Read-Host "  Target directory [.]"
            if (-not $t) { $t = "." }
            $script:YES = $true
            Install-Cmd @($t)
        }
        "2" { Update-Cmd @("-Check") }
        "3" {
            $t = Read-Host "  Target directory [.]"
            if (-not $t) { $t = "." }
            Check-Cmd @($t)
        }
        "4" {
            $t = Read-Host "  Target directory [.]"
            if (-not $t) { $t = "." }
            Doctor-Cmd @($t)
        }
        "5" {
            Skills-List-Cmd @()
            $a = Read-Host "  Install missing required skills? [Y/n]"
            if (-not $a) { $a = "Y" }
            if ($a -match "^[Yy]") {
                Write-Host ""
                Write-Host "  Skill installation scope:"
                Write-Host "    1) both    (default - install per skill source: local controller, global obra)"
                Write-Host "    2) local   (force local install only - warn on skills not bundled)"
                Write-Host "    3) global  (force global install only - warn on controller-local skills)"
                Write-Host "    4) skip    (don't install any skills)"
                $scopeAns = Read-Host "  Scope [1-4, default=1]"
                if (-not $scopeAns) { $scopeAns = "1" }
                $scopeFlag = @("-Both")
                switch ($scopeAns) {
                    "2" { $scopeFlag = @("-Local") }
                    "3" { $scopeFlag = @("-Global") }
                    "4" { $scopeFlag = @("-Skip") }
                }
                $script:YES = $true
                Skills-Add-Cmd (@("-All", "-Yes") + $scopeFlag)
            }
        }
        "6" {
            $t = Read-Host "  Target directory [.]"
            if (-not $t) { $t = "." }
            $script:YES = $true
            Uninstall-Cmd @($t)
        }
        "7" { Help-Cmd @() }
        "q" { Write-Host "Bye." }
        default { Write-Host "  Invalid choice."; Wizard }
    }
}

# ───────────────────────────── dispatcher ─────────────────────────────
$rest = @()
foreach ($a in $RemainingArgs) {
    if ($a -in @("--yes", "-y")) { $script:YES = $true; continue }
    if ($a -eq "--no-color") { $env:NO_COLOR = "1"; continue }
    $rest += $a
}

if ($rest.Count -eq 0) { Wizard; return }

$sub = $rest[0]
$subArgs = if ($rest.Count -gt 1) { $rest[1..($rest.Count - 1)] } else { @() }

if ($env:NO_COLOR -eq "1") {
    $RED = ''; $GREEN = ''; $YELLOW = ''; $BLUE = ''; $BOLD = ''; $DIM = ''; $RESET = ''
}

switch ($sub) {
    "install"    { Install-Cmd $subArgs }
    "update"     { Update-Cmd $subArgs }
    "check"      { Check-Cmd $subArgs }
    "doctor"     { Doctor-Cmd $subArgs }
    "uninstall"  { Uninstall-Cmd $subArgs }
    "skills"     { Skills-Cmd $subArgs }
    "release"    { Release-Cmd $subArgs }
    "lint"       { Lint-Cmd $subArgs }
    "version"    { Version-Cmd }
    { $_ -in @("help", "-h", "--help") } { Help-Cmd $subArgs }
    default {
        err "unknown subcommand: $sub"
        Write-Host "Run '.\agents-manager.ps1 help' for usage."
        exit 1
    }
}