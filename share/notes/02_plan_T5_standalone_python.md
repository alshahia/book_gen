# Plan: Standalone installer (Track T5 — REVISED for Option C)

**Task**: T-2026-07-01-001.C
**Track**: T5 of T-2026-07-01-001 (revised: Python instead of ps1/sh/cmd trio)
**Decision**: Option C — Python UX

## Goal

A self-contained bootstrapper that:
1. Downloads the latest (or pinned) agents-manager release from GitHub API.
2. Extracts to a temp directory.
3. Runs the bundled `install.py` against the user's chosen target.
4. Cleans up temp.

One Python file handles Windows + macOS + Linux. Three thin shims (5 LOC each) make it double-clickable from Explorer.

## Files to create

| File | LOC | Purpose |
|---|---|---|
| `bin/standalone-installer/install.py` | ~250 | Python bootstrap (cross-platform) |
| `bin/standalone-installer/install.sh` | 5 | Unix shim → `python3 install.py "$@"` |
| `bin/standalone-installer/install.cmd` | 5 | Windows shim → `python install.py %*` |
| `bin/standalone-installer/README.md` | ~80 | Documents the trio + flags |

Total: ~340 LOC.

## Files NOT to edit (this track)

- `bin/agents-manager.py`, `bin/install.py` (T2 / Python UX)
- `bin/agents-manager` (T1 done)
- `bin/agents-manager.ps1` (T1 done)
- `README.md`, `bin/README.md`, `docs/INSTALL.md` (Track T3)
- `.gitattributes`, release workflow, CHANGELOG, version bump (Track T4)

## Architecture

```
User runs:  bin/standalone-installer/install.sh   (or .cmd shim)
            ↓
        install.py starts:
          Phase 0  Banner ("about to do X, Y, Z")
          Phase 1  Preflight:
                    - Python 3.6+ ?
                    - Network reachable (api.github.com)?
                    - Target dir writable?
                    - Optional: git, node (warn only)
          Phase 2  Ask / parse flags
          Phase 3  GitHub Releases API:
                    GET https://api.github.com/repos/.../releases/latest
                    Find asset matching agents-manager-vX.Y.Z.zip
          Phase 4  Download ZIP → temp dir
          Phase 5  Extract ZIP → temp/agents-manager-<ver>/
          Phase 6  Run extracted/bin/install.py install <target> ...
          Phase 7  Cleanup temp
          Phase 8  Print "Done!" + next-step hints
```

## `install.py` design (~250 LOC)

```python
#!/usr/bin/env python3
"""agents-manager standalone installer.

Downloads the latest (or pinned) agents-manager release from GitHub,
extracts it, and runs the bundled installer against the user's target.

Usage:
    python3 install.py [options]
    install.cmd install . --version v0.10.1 --skills local --yes
"""
import argparse
import json
import os
import shutil
import ssl
import subprocess
import sys
import tempfile
import urllib.request
import zipfile
from pathlib import Path

VERSION = "0.11.0"
DEFAULT_REPO = "ahmadmhmdsy/agents-manager"
GITHUB_API = "https://api.github.com"

BANNER = """
================================================
  agents-manager bootstrap installer v{ver}
================================================

This installer will:
  1. Download agents-manager {{version}} from GitHub Releases
     (~50 KB)
  2. Extract it to a temporary folder
  3. Run the bundled installer against your chosen target
  4. Clean up the temporary folder

You can re-run this anytime — it's safe.
"""

# ────────────────────────── preflight ──────────────────────────

def check_python_version():
    if sys.version_info < (3, 6):
        sys.stderr.write(
            f"ERROR: Python 3.6+ required (you have {sys.version_info.major}."
            f"{sys.version_info.minor}).\n"
            "Install: https://www.python.org/downloads/\n"
        )
        sys.exit(1)

def check_network():
    ctx = ssl.create_default_context()
    try:
        req = urllib.request.Request(
            f"{GITHUB_API}", method="HEAD",
            headers={"User-Agent": "agents-manager-installer"})
        with urllib.request.urlopen(req, timeout=10, context=ctx) as r:
            r.read()
    except (urllib.error.URLError, TimeoutError, OSError) as e:
        sys.stderr.write(
            f"ERROR: Cannot reach {GITHUB_API}: {e}\n"
            "Check your internet connection. If behind a corporate proxy,\n"
            "set HTTPS_PROXY environment variable and try again.\n"
        )
        sys.exit(1)

def check_target_writable(target):
    p = Path(target).expanduser().resolve()
    if p.exists():
        if not p.is_dir():
            sys.stderr.write(f"ERROR: Target exists and is not a directory: {p}\n")
            sys.exit(1)
        if not os.access(str(p), os.W_OK):
            sys.stderr.write(
                f"ERROR: Target directory not writable: {p}\n"
                "Pick a different folder. Try: --target C:\\Users\\you\\my-project\n"
            )
            sys.exit(1)
    else:
        parent = p.parent
        if not os.access(str(parent), os.W_OK):
            sys.stderr.write(
                f"ERROR: Cannot create target — parent not writable: {parent}\n"
                "Pick a different folder.\n"
            )
            sys.exit(1)

def warn_optional_tools(scope):
    """Warn if git or node are missing (don't fail)."""
    if shutil.which("git") is None:
        sys.stderr.write(
            "WARN: git not found on PATH.\n"
            "  Install: https://git-scm.com/downloads\n"
            "  Install will skip 'git init' step.\n"
        )
    if scope in ("global", "both") and shutil.which("npx") is None:
        sys.stderr.write(
            "WARN: npx not found on PATH.\n"
            "  Install Node.js: https://nodejs.org/\n"
            "  Global skill install will be skipped.\n"
        )

# ────────────────────────── GitHub API ──────────────────────────

def fetch_release_url(repo, version):
    """Returns (tag, download_url) for the requested release."""
    if version == "latest":
        url = f"{GITHUB_API}/repos/{repo}/releases/latest"
    else:
        url = f"{GITHUB_API}/repos/{repo}/releases/tags/{version}"
    try:
        req = urllib.request.Request(
            url, headers={
                "Accept": "application/vnd.github+json",
                "User-Agent": "agents-manager-installer",
            })
        with urllib.request.urlopen(req, timeout=20) as r:
            data = json.loads(r.read())
    except urllib.error.HTTPError as e:
        if e.code == 404:
            sys.stderr.write(
                f"ERROR: Release '{version}' not found at "
                f"https://github.com/{repo}/releases\n"
                "Check version string or omit --version for latest.\n"
            )
        else:
            sys.stderr.write(
                f"ERROR: GitHub API returned {e.code}. "
                "Try again or pin --version vX.Y.Z.\n"
            )
        sys.exit(1)
    except (urllib.error.URLError, TimeoutError, OSError) as e:
        sys.stderr.write(
            f"ERROR: Cannot fetch release info: {e}\n"
            "Try again or pin --version vX.Y.Z.\n"
        )
        sys.exit(1)

    tag = data["tag_name"]
    assets = data.get("assets", [])
    zip_asset = next(
        (a for a in assets
         if a["name"].startswith("agents-manager-v") and a["name"].endswith(".zip")),
        None)
    if zip_asset is None:
        sys.stderr.write(
            f"ERROR: Release {tag} has no agents-manager-v*.zip asset.\n"
            "The release workflow may have failed. "
            f"File an issue: https://github.com/{repo}/issues\n"
        )
        sys.exit(1)
    return tag, zip_asset["browser_download_url"]

# ────────────────────────── download + extract ──────────────────────────

def download_zip(url, dest):
    sys.stdout.write(f"Downloading {url}\n  → {dest}\n")
    try:
        ctx = ssl.create_default_context()
        with urllib.request.urlopen(url, timeout=60, context=ctx) as r:
            with open(dest, "wb") as f:
                shutil.copyfileobj(r, f)
    except (urllib.error.URLError, TimeoutError, OSError) as e:
        sys.stderr.write(
            f"ERROR: Download failed: {e}\n"
            "Try --version vX.Y.Z (specific version, smaller delta).\n"
        )
        sys.exit(1)

def extract_zip(zip_path, dest_dir):
    try:
        with zipfile.ZipFile(zip_path) as z:
            z.extractall(dest_dir)
    except (zipfile.BadZipFile, OSError) as e:
        sys.stderr.write(f"ERROR: Cannot extract ZIP: {e}\n")
        sys.exit(1)

# ────────────────────────── dispatch ──────────────────────────

def run_bundled(extracted_dir, args):
    installer = Path(extracted_dir) / "bin" / "install.py"
    if not installer.exists():
        sys.stderr.write(
            f"ERROR: Extracted ZIP missing bin/install.py.\n"
            "The release is broken. "
            "File an issue: https://github.com/ahmadmhmdsy/agents-manager/issues\n"
        )
        sys.exit(1)
    cmd = [sys.executable, str(installer)] + args
    sys.stdout.write(f"$ {' '.join(cmd)}\n")
    return subprocess.call(cmd)

# ────────────────────────── argparse ──────────────────────────

def build_parser():
    p = argparse.ArgumentParser(
        prog="install.py",
        description="agents-manager standalone installer (downloads release + runs it)")
    p.add_argument("--version", default="latest",
                   help="release tag to install (default: latest)")
    p.add_argument("--repo", default=DEFAULT_REPO,
                   help=f"GitHub repo (default: {DEFAULT_REPO})")
    p.add_argument("--target", default=".",
                   help="installation target (default: CWD)")
    p.add_argument("--git", choices=["auto", "skip", "prompt"], default="auto")
    p.add_argument("--skills", choices=["global", "local", "both", "skip"],
                   default="both")
    p.add_argument("--dry-run", action="store_true")
    p.add_argument("--yes", "-y", action="store_true",
                   help="skip confirmation prompts")
    return p

# ────────────────────────── main ──────────────────────────

def main():
    check_python_version()
    parser = build_parser()
    args = parser.parse_args()

    print(BANNER.format(ver=VERSION))
    print(f"Repo:    {args.repo}")
    print(f"Version: {args.version}")
    print(f"Target:  {os.path.abspath(args.target)}")
    print(f"Git:     {args.git}")
    print(f"Skills:  {args.skills}")
    if args.dry_run:
        print(f"Dry-run: yes (no actual changes)")
    print()

    check_network()
    check_target_writable(args.target)
    warn_optional_tools(args.skills)

    if not args.yes:
        if not confirm("Proceed?"):
            print("Cancelled.")
            return 0

    tag, zip_url = fetch_release_url(args.repo, args.version)
    print(f"Found release: {tag}")

    tmpdir = Path(tempfile.mkdtemp(prefix="agents-manager-"))
    try:
        zip_path = tmpdir / "install.zip"
        download_zip(zip_url, str(zip_path))
        extracted = tmpdir / "extracted"
        extracted.mkdir()
        extract_zip(str(zip_path), str(extracted))
        # The ZIP contains a top-level agents-manager/ folder.
        extracted_root = extracted / "agents-manager"
        if not extracted_root.exists():
            # Some archives flatten — fallback to first subdir
            children = list(extracted.iterdir())
            extracted_root = children[0] if children else extracted
        run_args = ["install", args.target,
                    "--git", args.git,
                    "--skills", args.skills]
        if args.dry_run:
            run_args.append("--dry-run")
        run_args.append("--yes")
        rc = run_bundled(extracted_root, run_args)
        return rc
    finally:
        shutil.rmtree(tmpdir, ignore_errors=True)

def confirm(message, default=True):
    suffix = " [Y/n]" if default else " [y/N]"
    while True:
        sys.stdout.write(f"{message}{suffix}: ")
        sys.stdout.flush()
        try:
            line = input().strip().lower()
        except (EOFError, KeyboardInterrupt):
            print()
            print("Cancelled.")
            sys.exit(130)
        if not line:
            return default
        if line in ("y", "yes"):
            return True
        if line in ("n", "no"):
            return False

if __name__ == "__main__":
    sys.exit(main() or 0)
```

## Shim files

### `bin/standalone-installer/install.sh` (5 LOC, LF)

```bash
#!/usr/bin/env bash
# agents-manager standalone installer shim (Unix)
exec python3 "$(dirname "${BASH_SOURCE[0]}")/install.py" "$@"
```

### `bin/standalone-installer/install.cmd` (5 LOC, CRLF)

```bat
@echo off
REM agents-manager standalone installer shim (Windows)
python "%~dp0install.py" %*
exit /b %errorlevel%
```

## Acceptance criteria (this track)

1. `python3 install.py --version v0.10.1 --target C:\\temp\\fixture --yes` → downloads v0.10.1 ZIP, extracts, runs install, cleans up, exits with dispatcher's exit code.
2. `python3 install.py --help` → prints usage.
3. No Python 3.6 → friendly error + install recipe.
4. No network → friendly error + proxy recipe.
5. `--version notavalidtag` → friendly 404 error.
6. `install.cmd` (Windows, double-click) → menu/banner appears.
7. `curl -fsSL https://raw.githubusercontent.com/ahmadmhmdsy/agents-manager/main/bin/standalone-installer/install.sh | bash` → end-to-end install works.
8. `python -m py_compile bin/standalone-installer/install.py` → exits 0.
9. T2 files (`bin/agents-manager.py`, `bin/install.py`) coexist; both `bin/install.py install` and `bin/standalone-installer/install.py` work independently.

## Quality gates

```bash
python3 -m py_compile bin/standalone-installer/install.py
# Manual smoke test on real Windows + macOS/Linux for end-to-end
```

## Output (am-coder must produce)

1. The 4 new files written.
2. `share/notes/03_coder_summary_T-2026-07-01-001_C.md` with:
   - Tasks attempted table (C.1-C.4)
   - Files written (path + LOC)
   - py_compile output + smoke test results
   - Deviations from plan
   - Self-critique

## Reference (read before editing)

- T2 plan file (`share/notes/02_plan_T2_python_ux.md`) — install.py shape that this script downloads
- T1 changes — dispatcher `--scope` already wired
- `bin/agents-manager` and `bin/agents-manager.ps1` — what runs after extraction