#!/usr/bin/env python3
"""install.py - agents-manager standalone bootstrap installer.

Downloads the latest (or pinned) agents-manager release from GitHub
Releases, extracts it to a temp directory, dispatches to the bundled
bin/install.py against the user's chosen target, then cleans up.

Standalone installer for agents-manager - safe to re-run.

Usage:
    python3 install.py [options]
    install.sh install . --version v0.10.1 --yes
    install.cmd install . --skills local --yes
"""

import argparse
import json
import os
import platform
import shutil
import ssl
import subprocess
import sys
import tempfile
import urllib.error
import urllib.request
import zipfile
from pathlib import Path

VERSION = "0.11.0"
DEFAULT_REPO = "ahmadmhmdsy/agents-manager"
GITHUB_API = "https://api.github.com"
IS_WINDOWS = platform.system() == "Windows"

BANNER = """
================================================
  agents-manager standalone installer
================================================

This installer will:
  1. Download agents-manager {version} from GitHub Releases
     (~50 KB)
  2. Extract it to a temporary folder
  3. Run the bundled installer against your chosen target
  4. Clean up the temporary folder

You can re-run this anytime - it's safe.
""".strip()


# ────────────────────────── preflight ──────────────────────────


def check_python_version() -> None:
    """Fail fast if Python is too old. Prints one actionable recipe."""
    if sys.version_info < (3, 7):
        sys.stderr.write(
            f"ERROR: Python 3.7+ is required (you have "
            f"{sys.version_info.major}.{sys.version_info.minor}).\n"
            "  Install: https://www.python.org/downloads/\n"
        )
        sys.exit(1)


def check_network() -> None:
    """HEAD api.github.com. One actionable recipe on failure."""
    try:
        ctx = ssl.create_default_context()
        req = urllib.request.Request(
            f"{GITHUB_API}", method="HEAD",
            headers={"User-Agent": "agents-manager-installer"},
        )
        with urllib.request.urlopen(req, timeout=10, context=ctx) as r:
            r.read()
    except (urllib.error.URLError, TimeoutError, OSError) as e:
        sys.stderr.write(
            f"ERROR: Cannot reach {GITHUB_API}: {e}\n"
            "  Check your internet connection.\n"
            "  If behind a corporate proxy, set HTTPS_PROXY and try again.\n"
        )
        sys.exit(1)


def check_target_writable(target: str) -> None:
    """The chosen TARGET must exist (as dir) or have a writable parent."""
    p = Path(target).expanduser().resolve()
    if p.exists():
        if not p.is_dir():
            sys.stderr.write(
                f"ERROR: Target exists and is not a directory: {p}\n"
                "  Pick a folder, not a file. Example: --target C:\\Users\\you\\myproj\n"
            )
            sys.exit(1)
        if not os.access(str(p), os.W_OK):
            sys.stderr.write(
                f"ERROR: Target directory not writable: {p}\n"
                "  Pick a different folder. Try: --target C:\\Users\\you\\my-project\n"
            )
            sys.exit(1)
        return
    parent = p.parent
    if not parent.exists() or not os.access(str(parent), os.W_OK):
        sys.stderr.write(
            f"ERROR: Cannot create target - parent not writable: {parent}\n"
            "  Pick a different parent folder.\n"
        )
        sys.exit(1)


def warn_optional_tools(skills_scope: str) -> None:
    """Warn (don't fail) if optional tools are missing."""
    if shutil.which("git") is None:
        sys.stderr.write(
            "WARN: git not found on PATH.\n"
            "  Install: https://git-scm.com/downloads\n"
            "  Install will skip 'git init' step.\n"
        )
    if skills_scope in ("global", "both") and shutil.which("npx") is None:
        sys.stderr.write(
            "WARN: npx not found on PATH.\n"
            "  Install Node.js: https://nodejs.org/\n"
            "  Global skill install will be skipped.\n"
        )


# ────────────────────────── GitHub Releases ──────────────────────────


def fetch_release_url(repo: str, version: str):
    """Resolve (tag, zip_download_url) for the requested release.

    Returns (tag, url) tuple. Exits with code 1 + recipe on any failure.
    """
    if version == "latest":
        url = f"{GITHUB_API}/repos/{repo}/releases/latest"
    else:
        url = f"{GITHUB_API}/repos/{repo}/releases/tags/{version}"
    try:
        req = urllib.request.Request(
            url,
            headers={
                "Accept": "application/vnd.github+json",
                "User-Agent": "agents-manager-installer",
            },
        )
        with urllib.request.urlopen(req, timeout=20) as r:
            data = json.loads(r.read())
    except urllib.error.HTTPError as e:
        if e.code == 404:
            sys.stderr.write(
                f"ERROR: Release '{version}' not found at "
                f"https://github.com/{repo}/releases\n"
                "  Check version string or omit --version for latest.\n"
                "  List tags: https://github.com/"
                f"{repo}/releases/tag/{version}\n"
            )
        elif e.code == 403:
            sys.stderr.write(
                f"ERROR: GitHub API rate limit hit ({e.code}).\n"
                "  Wait a few minutes, or pin --version vX.Y.Z.\n"
            )
        else:
            sys.stderr.write(
                f"ERROR: GitHub API returned {e.code}.\n"
                "  Try again or pin --version vX.Y.Z.\n"
            )
        sys.exit(1)
    except (urllib.error.URLError, TimeoutError, OSError) as e:
        sys.stderr.write(
            f"ERROR: Cannot fetch release info: {e}\n"
            "  Try again or pin --version vX.Y.Z.\n"
        )
        sys.exit(1)

    tag = data.get("tag_name", "unknown")
    assets = data.get("assets", []) or []
    zip_asset = next(
        (
            a for a in assets
            if a.get("name", "").startswith("agents-manager-v")
            and a.get("name", "").endswith(".zip")
        ),
        None,
    )
    if zip_asset is None:
        sys.stderr.write(
            f"ERROR: Release {tag} has no agents-manager-v*.zip asset.\n"
            "  The release workflow may have failed.\n"
            f"  File an issue: https://github.com/{repo}/issues\n"
        )
        sys.exit(1)
    return tag, zip_asset["browser_download_url"]


# ────────────────────────── download + extract ──────────────────────────


def download_zip(url: str, dest: Path) -> None:
    """Stream the ZIP to disk. Exit with recipe on failure."""
    sys.stdout.write(f"Downloading {url}\n  -> {dest}\n")
    try:
        ctx = ssl.create_default_context()
        with urllib.request.urlopen(url, timeout=60, context=ctx) as r:
            with open(dest, "wb") as f:
                shutil.copyfileobj(r, f)
    except (urllib.error.URLError, TimeoutError, OSError) as e:
        sys.stderr.write(
            f"ERROR: Download failed: {e}\n"
            "  Try --version vX.Y.Z (specific version, smaller delta).\n"
        )
        sys.exit(1)


def extract_zip(zip_path: Path, dest_dir: Path) -> None:
    """Unzip into dest_dir. Exit with recipe on failure."""
    try:
        with zipfile.ZipFile(zip_path) as z:
            z.extractall(dest_dir)
    except (zipfile.BadZipFile, OSError) as e:
        sys.stderr.write(
            f"ERROR: Cannot extract ZIP: {e}\n"
            "  The release asset may be corrupted. "
            f"File an issue: https://github.com/{DEFAULT_REPO}/issues\n"
        )
        sys.exit(1)


# ────────────────────────── dispatch ──────────────────────────


def run_bundled(extracted_dir: Path, args: list) -> int:
    """Invoke the bundled bin/install.py with `args`. Returns its exit code."""
    # Pick the right dispatcher shim for this OS.
    if IS_WINDOWS:
        dispatcher = extracted_dir / "bin" / "install.cmd"
        # .cmd shim - invoke via cmd.exe so %errorlevel% propagates.
        cmd = ["cmd.exe", "/c", str(dispatcher)] + args
    else:
        dispatcher = extracted_dir / "bin" / "install.sh"
        cmd = ["bash", str(dispatcher)] + args
    if not dispatcher.exists():
        # Fallback: some zips flatten directories.
        for candidate_name in ("install.cmd", "install.sh", "install.py"):
            alt = extracted_dir / "bin" / candidate_name
            if alt.exists():
                dispatcher = alt
                if candidate_name == "install.py":
                    cmd = [sys.executable, str(alt)] + args
                elif candidate_name == "install.cmd":
                    cmd = ["cmd.exe", "/c", str(alt)] + args
                else:
                    cmd = ["bash", str(alt)] + args
                break
        else:
            sys.stderr.write(
                f"ERROR: Extracted bundle missing bin/install.{{cmd,sh,py}}.\n"
                f"  Looked in: {extracted_dir / 'bin'}\n"
                f"  File an issue: https://github.com/{DEFAULT_REPO}/issues\n"
            )
            sys.exit(1)
    sys.stdout.write(f"$ {' '.join(cmd)}\n")
    sys.stdout.flush()
    return subprocess.call(cmd)


# ────────────────────────── argparse ──────────────────────────


def build_parser() -> argparse.ArgumentParser:
    """Build the CLI parser. Help text doubles as the docs index."""
    p = argparse.ArgumentParser(
        prog="install.py",
        description=(
            "Standalone installer for agents-manager. "
            "Downloads the latest release from GitHub Releases, "
            "extracts it to a temp directory, runs the bundled "
            "bin/install.py against your target, then cleans up."
        ),
        epilog=BANNER
        + f"\n\nDefault repo: {DEFAULT_REPO}\n"
        "Default version: latest\n",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    p.add_argument(
        "--target",
        default=".",
        help="installation target directory (default: CWD)",
    )
    p.add_argument(
        "--version",
        default="latest",
        help="release tag to install, e.g. v0.10.1 (default: latest)",
    )
    p.add_argument(
        "--git",
        choices=["auto", "skip", "prompt"],
        default="auto",
        help="git init behavior (default: auto)",
    )
    p.add_argument(
        "--skills",
        choices=["global", "local", "both", "skip"],
        default="both",
        help="skill installation scope (default: both)",
    )
    p.add_argument(
        "--yes",
        "-y",
        action="store_true",
        help="skip confirmation prompts (assume yes)",
    )
    p.add_argument(
        "--dry-run",
        action="store_true",
        help="pass --dry-run through to the bundled installer",
    )
    p.add_argument(
        "--repo",
        default=DEFAULT_REPO,
        help=(
            "GitHub org/repo to pull from "
            f"(default: {DEFAULT_REPO})"
        ),
    )
    return p


# ────────────────────────── prompts ──────────────────────────


def confirm(message: str, default: bool = True) -> bool:
    """Y/n prompt. Ctrl+C / EOF exit 130."""
    suffix = " [Y/n]" if default else " [y/N]"
    while True:
        sys.stdout.write(f"{message}{suffix}: ")
        sys.stdout.flush()
        try:
            line = input().strip().lower()
        except (EOFError, KeyboardInterrupt):
            sys.stdout.write("\nCancelled.\n")
            sys.exit(130)
        if not line:
            return default
        if line in ("y", "yes"):
            return True
        if line in ("n", "no"):
            return False
        sys.stdout.write("  Please answer y or n.\n")


# ────────────────────────── main ──────────────────────────


def main() -> int:
    """Phase 0..7: banner, preflight, fetch, download, extract, run, cleanup."""
    check_python_version()
    parser = build_parser()
    args = parser.parse_args()

    target_abs = os.path.abspath(args.target)
    print(BANNER)
    print(f"  Repo:    {args.repo}")
    print(f"  Version: {args.version}")
    print(f"  Target:  {target_abs}")
    print(f"  Git:     {args.git}")
    print(f"  Skills:  {args.skills}")
    if args.dry_run:
        print(f"  Mode:    DRY RUN (no changes will be made)")
    print()

    check_network()
    check_target_writable(args.target)
    warn_optional_tools(args.skills)

    if not args.yes:
        if not confirm("Proceed?"):
            sys.stdout.write("Cancelled.\n")
            return 0

    tag, zip_url = fetch_release_url(args.repo, args.version)
    sys.stdout.write(f"  Found release: {tag}\n")

    tmpdir = Path(tempfile.mkdtemp(prefix="agents-manager-"))
    try:
        zip_path = tmpdir / "install.zip"
        download_zip(zip_url, zip_path)
        extracted = tmpdir / "extracted"
        extracted.mkdir()
        extract_zip(zip_path, extracted)
        # The ZIP contains a top-level agents-manager/ folder.
        extracted_root = extracted / "agents-manager"
        if not extracted_root.exists():
            # Fallback: flatten archives - pick the single child folder.
            children = [c for c in extracted.iterdir() if c.is_dir()]
            if len(children) == 1:
                extracted_root = children[0]
            else:
                extracted_root = extracted
        run_args = ["install", args.target,
                    "--git", args.git,
                    "--skills", args.skills]
        if args.dry_run:
            run_args.append("--dry-run")
        if args.yes:
            run_args.append("--yes")
        rc = run_bundled(extracted_root, run_args)
        if rc == 0:
            sys.stdout.write(
                "\nDone! Re-run this anytime to upgrade.\n"
                "  Next: cd into your project and run "
                "'agents-manager install .' to install the CLI.\n"
            )
        return rc
    finally:
        shutil.rmtree(tmpdir, ignore_errors=True)


if __name__ == "__main__":
    sys.exit(main())
