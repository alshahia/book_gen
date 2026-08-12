"""install_amiri.py -- book2media Phase 3 P5T4: download + install Amiri font.

Downloads the Amiri font release zip from aliftype/amiri and extracts
to the platform-specific user font directory. Idempotent: re-running
without --force prints "already installed" and exits 0.

CLI:
    py -3 book-kit/book_workflow/scripts/install_amiri.py
    py -3 book-kit/book_workflow/scripts/install_amiri.py --verify
    py -3 book-kit/book_workflow/scripts/install_amiri.py --force

EXIT CODES
    0  success (or already installed).
    2  --verify found nothing; otherwise input error (bad --target-dir).
    3  network failure (GitHub API or zip download).
    4  extraction failure (zip invalid or font count below threshold).

PATH VALIDATION
    --target-dir is the user-overridden install location; we accept
    absolute paths because the default install dirs live outside the
    repo root by design (fonts belong in the OS user font dir).

IDEMPOTENT
    Re-running without --force skips download when Amiri is already
    discoverable via file presence or fc-list. --force bypasses.

# chub-cite: aliftype/amiri
"""
from __future__ import annotations

# ---------------------------------------------------------------------------
# UTF-8 stdio force (mandatory block from dispatch preamble).
# ---------------------------------------------------------------------------

import sys
for _stream in (sys.stdout, sys.stderr):
    try: _stream.reconfigure(encoding="utf-8")
    except Exception: pass


# ---------------------------------------------------------------------------
# Standard imports
# ---------------------------------------------------------------------------

import argparse
import json
import os
import shutil
import subprocess
import zipfile
from pathlib import Path
from urllib.request import Request, urlopen
from urllib.error import URLError, HTTPError


# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

# GitHub release endpoints (aliftype/amiri).
AMIRI_REPO = "aliftype/amiri"
GH_API_LATEST = "https://api.github.com/repos/%s/releases/latest" % AMIRI_REPO
GH_DOWNLOAD = "https://github.com/%s/releases/download" % AMIRI_REPO

# Amiri zip carries at least 5 TTF/OTF files (Regular, Bold, Italic,
# BoldSlanted, Quran, plus optional QuranColored). The threshold is a
# sanity check, not a strict equality -- some releases add variants.
EXPECTED_MIN_FONTS = 5

# Network timeout (seconds). GitHub API responds in <2s on a warm
# connection; the zip is ~3 MB and downloads in <10s on broadband.
NETWORK_TIMEOUT_S = 30

# User-Agent header. GitHub's API rejects requests without one.
USER_AGENT = "book-kit-amiri-installer/1.0"


# ---------------------------------------------------------------------------
# Errors
# ---------------------------------------------------------------------------


class InputError(Exception):
    """Input error -- caller should exit 2."""


class NetworkFailure(Exception):
    """Network problem -- caller should exit 3."""


class ExtractionFailure(Exception):
    """Zip / FS problem -- caller should exit 4."""


# ---------------------------------------------------------------------------
# Platform defaults + install detection
# ---------------------------------------------------------------------------


def _default_target_dir():
    if sys.platform.startswith("win"):
        base = os.environ.get("LOCALAPPDATA") or str(
            Path.home() / "AppData" / "Local"
        )
        return Path(base) / "fonts" / "Amiri"
    if sys.platform == "darwin":
        return Path.home() / "Library" / "Fonts" / "Amiri"
    return Path.home() / ".local" / "share" / "fonts" / "Amiri"


def _detect_installed(target_dir):
    """Return True if Amiri is discoverable by the OS or present in target_dir."""
    target_dir = Path(target_dir)
    if target_dir.is_dir():
        for pat in ("*.ttf", "*.otf"):
            if any(target_dir.glob(pat)):
                return True
    if not sys.platform.startswith("win"):
        try:
            proc = subprocess.run(
                ["fc-list"],
                capture_output=True, text=True, encoding="utf-8",
                check=False, timeout=5,
            )
            if proc.returncode == 0 and "Amiri" in proc.stdout:
                return True
        except (FileNotFoundError, subprocess.TimeoutExpired, OSError):
            pass
    return False


# ---------------------------------------------------------------------------
# Network + extraction
# ---------------------------------------------------------------------------


def _fetch_latest_tag():
    req = Request(GH_API_LATEST, headers={"User-Agent": USER_AGENT})
    try:
        with urlopen(req, timeout=NETWORK_TIMEOUT_S) as resp:
            payload = resp.read().decode("utf-8")
    except (URLError, HTTPError, TimeoutError, OSError) as exc:
        raise NetworkFailure("cannot reach %s: %s" % (GH_API_LATEST, exc))
    try:
        data = json.loads(payload)
    except json.JSONDecodeError as exc:
        raise NetworkFailure("GitHub API returned non-JSON: %s" % exc)
    tag = data.get("tag_name")
    if not tag:
        raise NetworkFailure("GitHub API response missing tag_name")
    return tag


def _download_zip(tag, out_path):
    url = "%s/%s/Amiri-%s.zip" % (GH_DOWNLOAD, tag, tag)
    req = Request(url, headers={"User-Agent": USER_AGENT})
    try:
        with urlopen(req, timeout=NETWORK_TIMEOUT_S) as resp:
            with open(out_path, "wb") as fh:
                shutil.copyfileobj(resp, fh)
    except (URLError, HTTPError, TimeoutError, OSError) as exc:
        raise NetworkFailure("cannot download %s: %s" % (url, exc))


def _extract_zip(zip_path, target_dir):
    target_dir = Path(target_dir)
    try:
        with zipfile.ZipFile(str(zip_path), "r") as zf:
            font_names = [
                n for n in zf.namelist()
                if n.lower().endswith((".ttf", ".otf"))
            ]
            if len(font_names) < EXPECTED_MIN_FONTS:
                raise ExtractionFailure(
                    "zip has %d font files (expected >= %d)"
                    % (len(font_names), EXPECTED_MIN_FONTS)
                )
            target_dir.mkdir(parents=True, exist_ok=True)
            zf.extractall(str(target_dir))
    except zipfile.BadZipFile as exc:
        raise ExtractionFailure("invalid zip %s: %s" % (zip_path, exc))
    except OSError as exc:
        raise ExtractionFailure("cannot extract to %s: %s" % (target_dir, exc))


# ---------------------------------------------------------------------------
# Main run
# ---------------------------------------------------------------------------


def run_install(force, verify_only, target_arg):
    target_dir = (
        Path(target_arg).resolve() if target_arg else _default_target_dir()
    )

    if verify_only:
        if _detect_installed(target_dir):
            print("install_amiri: installed at %s" % target_dir)
            return 0
        print("install_amiri: NOT installed (target=%s)" % target_dir)
        return 2

    if not force and _detect_installed(target_dir):
        print("install_amiri: already installed at %s" % target_dir)
        return 0

    # Resolve latest release tag.
    try:
        tag = _fetch_latest_tag()
    except NetworkFailure as exc:
        print("install_amiri: %s" % exc, file=sys.stderr)
        return 3

    print("install_amiri: latest tag=%s; downloading" % tag)

    # Download to a sibling tmp file (same dir so we never span mounts).
    tmp_zip = target_dir.parent / ("Amiri-%s.zip.tmp" % tag)
    try:
        tmp_zip.parent.mkdir(parents=True, exist_ok=True)
    except OSError as exc:
        print("install_amiri: cannot create %s: %s" % (tmp_zip.parent, exc),
              file=sys.stderr)
        return 4

    try:
        _download_zip(tag, tmp_zip)
    except NetworkFailure as exc:
        print("install_amiri: %s" % exc, file=sys.stderr)
        try:
            tmp_zip.unlink()
        except OSError:
            pass
        return 3

    try:
        _extract_zip(tmp_zip, target_dir)
    except ExtractionFailure as exc:
        print("install_amiri: %s" % exc, file=sys.stderr)
        try:
            tmp_zip.unlink()
        except OSError:
            pass
        return 4

    try:
        tmp_zip.unlink()
    except OSError:
        pass

    print("install_amiri: OK installed at %s (tag=%s)" % (target_dir, tag))
    return 0


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------


def _build_parser():
    p = argparse.ArgumentParser(
        prog="install_amiri",
        description="Download + install the Amiri font (idempotent).",
    )
    p.add_argument("--verify", action="store_true",
                   help="Print install status; do not download.")
    p.add_argument("--force", action="store_true",
                   help="Re-download even if Amiri is already installed.")
    p.add_argument("--target-dir", default=None,
                   help="Override install dir. Default: OS user font dir.")
    return p


def main(argv=None):
    parser = _build_parser()
    args = parser.parse_args(argv)
    return run_install(
        force=args.force,
        verify_only=args.verify,
        target_arg=args.target_dir,
    )


if __name__ == "__main__":
    sys.exit(main())
