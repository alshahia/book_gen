# release-zip.ps1 — build agents-manager-vX.Y.Z.zip from a git tag's tree
# Usage: .\bin\release-zip.ps1 -Tag <tag> [-Out <path>]
#
# Includes only the 6 controller paths (NOT bin/ — bin/ stays in the source repo
# for the maintainer; users download ZIPs and run install.sh from inside them).
# Validates that each expected path was actually included before declaring success.
[CmdletBinding()]
param(
    [Parameter(Mandatory = $true)]
    [string]$Tag,

    [string]$Out = ""
)

$ErrorActionPreference = "Stop"

# Normalize tag (allow either "0.9.1" or "v0.9.1")
if (-not $Tag.StartsWith("v")) { $Tag = "v$Tag" }
$Version = $Tag.Substring(1)

# Validate tag exists locally
$tagRev = git rev-parse --verify --quiet "refs/tags/$Tag" 2>$null
if (-not $tagRev) {
    Write-Host "ERROR: tag '${Tag}' does not exist locally." -ForegroundColor Red
    $existing = git tag -l
    Write-Host "       Available tags: $($existing -join ' ')" -ForegroundColor Red
    exit 1
}

if (-not $Out) {
    $Out = Join-Path (Get-Location) "agents-manager-v$Version.zip"
}

# Resolve to absolute path
$Out = [System.IO.Path]::GetFullPath($Out)
$TmpOut = "$Out.tmp"

# Path allowlist — what goes into the release ZIP.
#
# Includes the 6 controller paths (what install.ps1 copies INTO the target
# project) PLUS the bin/ directory (so Option B / "download a ZIP" users can
# actually RUN the installer from the extracted folder).
$Paths = @(
    "opencode.jsonc",
    "CLAUDE.md",
    "agents_manager",
    "share",
    "tasks",
    ".agents/skills/mavis-team",
    "bin"
)

Write-Host "Building ${Out} from tag ${Tag}..."

# Build the ZIP via [System.IO.Compression.ZipFile] (built into .NET).
# Strategy: use `git archive` to a tar stream, extract to a temp dir, then zip.
$TmpDir = New-Item -ItemType Directory -Path (Join-Path ([System.IO.Path]::GetTempPath()) ("agents-manager-build-" + [Guid]::NewGuid().ToString("N"))) -Force
try {
    $ExtractDir = Join-Path $TmpDir.FullName "agents-manager"
    New-Item -ItemType Directory -Path $ExtractDir -Force | Out-Null

    # git archive to stdout (tar), pipe through tar -x in bash
    $bashExe = $null
    if (Test-Path "C:\Program Files\Git\bin\bash.exe") {
        $bashExe = "C:\Program Files\Git\bin\bash.exe"
    } elseif (Get-Command bash -ErrorAction SilentlyContinue) {
        $bashExe = (Get-Command bash).Source
    }

    if ($bashExe) {
        # Path-mode archive: only the listed paths
        $pathArgs = $Paths -join ' '
        & git archive --format=tar "$Tag" -- $Paths | & $bashExe -c "tar -x -C '$($ExtractDir -replace '\\','/')'"
        if ($LASTEXITCODE -ne 0) { throw "git archive + tar extract failed (exit $LASTEXITCODE)" }
    } else {
        throw "No bash on PATH. PowerShell's tar.exe (Win10+ 1809+) can't extract git's POSIX tar reliably. Install Git for Windows or run bin/release-zip.sh instead."
    }

    # Verify each expected path was extracted
    $Missing = @()
    foreach ($p in $Paths) {
        $check = Join-Path $ExtractDir $p
        if (-not (Test-Path $check)) {
            $Missing += $p
        }
    }
    if ($Missing.Count -gt 0) {
        Write-Host "ERROR: extracted tree missing expected paths:" -ForegroundColor Red
        $Missing | ForEach-Object { Write-Host "  - $_" -ForegroundColor Red }
        exit 2
    }

    # Verify the new (v0.11.0+) Python UX + standalone installer scripts are present.
    # Without these, Option-D users (curl-pipe / iwr / double-click install.cmd)
    # cannot bootstrap from the release ZIP.
    $InstallerScripts = @(
        "bin\install.sh",
        "bin\install.ps1",
        "bin\agents-manager.py",
        "bin\install.py",
        "bin\standalone-installer\install.py",
        "bin\standalone-installer\install.cmd"
    )
    $MissingScripts = @()
    foreach ($s in $InstallerScripts) {
        $check = Join-Path $ExtractDir $s
        if (-not (Test-Path $check)) {
            $MissingScripts += $s
        }
    }
    if ($MissingScripts.Count -gt 0) {
        Write-Host "ERROR: extracted tree missing installer scripts:" -ForegroundColor Red
        $MissingScripts | ForEach-Object { Write-Host "  - $_" -ForegroundColor Red }
        exit 2
    }

    # Create the ZIP with [System.IO.Compression.ZipFile]
    Add-Type -AssemblyName System.IO.Compression.FileSystem
    if (Test-Path $TmpOut) { Remove-Item $TmpOut -Force }
    [System.IO.Compression.ZipFile]::CreateFromDirectory($TmpDir.FullName, $TmpOut)

    Move-Item -Path $TmpOut -Destination $Out -Force
} finally {
    Remove-Item -LiteralPath $TmpDir.FullName -Recurse -Force -ErrorAction SilentlyContinue
}

# Summary
$size = (Get-Item $Out).Length
$entryCount = [System.IO.Compression.ZipFile]::OpenRead($Out).Entries.Count
Write-Host "  OK   $Out"
Write-Host "       size: $size bytes, entries: $entryCount"
Write-Host "       tag:  $Tag -> $(git rev-parse --short $Tag)"