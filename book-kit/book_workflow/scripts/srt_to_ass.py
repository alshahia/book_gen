"""srt_to_ass.py -- book2media Phase 3 P5T4: SRT -> ASS via pysubs2.

Local ffmpeg gyan-dev build lacks `shaping=` flag in `subtitles=` filter
(predates upstream commit b08c9c5); we route everything through the
`ass=` filter with HarfBuzz enabled via `shaping=complex`. pysubs2 writes
ASS, ffmpeg renders ASS, HarfBuzz does the shaping.

CLI:
    py -3 book-kit/book_workflow/scripts/srt_to_ass.py \\
        --in chapters/ch-01-ar.srt --out chapters/ch-01-ar.ass \\
        --locale ar --font-size 24

EXIT CODES
    0  success -- ASS written.
    2  input error (missing --in, --locale not en|ar, bad path).
    3  missing dep (pysubs2 not installed; for ar, Amiri font absent).
    4  internal/runtime (pysubs2.load failed, write failed).

PATH VALIDATION
    --in and --out must resolve under repo root.

IDEMPOTENT
    Re-running with identical inputs produces a byte-identical ASS.

# chub-cite: pysubs2
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
import importlib.util
import subprocess
from pathlib import Path


# ---------------------------------------------------------------------------
# Paths + imports
# ---------------------------------------------------------------------------

# This file lives at: book-kit/book_workflow/scripts/srt_to_ass.py
# parents[3] = repo root.
REPO_ROOT = Path(__file__).resolve().parents[3]

_THIS_DIR = Path(__file__).resolve().parent
_LIB_DIR = _THIS_DIR.parent / "lib"

sys.path.insert(0, str(_LIB_DIR))
try:
    import errors as errors_mod  # noqa: E402
except ImportError:  # pragma: no cover -- lib/ ships with the package
    errors_mod = None


# ---------------------------------------------------------------------------
# Errors
# ---------------------------------------------------------------------------


class InputError(Exception):
    """Input error -- caller should exit 2."""


class MissingDepError(Exception):
    """Missing Python dep or font -- caller should exit 3."""


class RuntimeFailure(Exception):
    """Provider / runtime failure -- caller should exit 4."""


# ---------------------------------------------------------------------------
# Path validation (mirrors media_tts.py::_resolve_under_root).
# ---------------------------------------------------------------------------


def _resolve_under_root(candidate, label):
    """Resolve `candidate` under the repo root, refusing escapes."""
    raw = Path(candidate)
    if ".." in raw.parts:
        raise InputError("%s must not contain '..': %s" % (label, candidate))
    if raw.is_absolute():
        target = raw.resolve()
    else:
        target = (REPO_ROOT / raw).resolve()
    root = REPO_ROOT.resolve()
    if target != root and root not in target.parents:
        raise InputError(
            "%s must resolve under %s: %s" % (label, root, candidate)
        )
    return target


# ---------------------------------------------------------------------------
# Optional-dep + font probes.
# ---------------------------------------------------------------------------


def _check_pysubs2():
    if importlib.util.find_spec("pysubs2") is None:
        raise MissingDepError(
            "pysubs2 not installed; `pip install pysubs2` in the venv"
        )


def _default_amiri_target():
    """Mirror install_amiri.py's default install dirs."""
    import os
    if sys.platform.startswith("win"):
        base = os.environ.get("LOCALAPPDATA") or str(
            Path.home() / "AppData" / "Local"
        )
        return Path(base) / "fonts" / "Amiri"
    if sys.platform == "darwin":
        return Path.home() / "Library" / "Fonts" / "Amiri"
    return Path.home() / ".local" / "share" / "fonts" / "Amiri"


def _check_amiri_installed():
    """True if Amiri is discoverable by the OS or present in the user font dir."""
    target = _default_amiri_target()
    if target.is_dir():
        for pat in ("*.ttf", "*.otf"):
            if any(target.glob(pat)):
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
# Main run
# ---------------------------------------------------------------------------


def run_convert(in_arg, out_arg, locale, font_size):
    # 1. --in
    try:
        in_path = _resolve_under_root(in_arg, "--in")
    except InputError as exc:
        print("srt_to_ass: %s" % exc, file=sys.stderr)
        return 2
    if not in_path.exists():
        print("srt_to_ass: --in not found: %s" % in_path, file=sys.stderr)
        return 2

    # 2. --out
    try:
        out_path = _resolve_under_root(out_arg, "--out")
    except InputError as exc:
        print("srt_to_ass: %s" % exc, file=sys.stderr)
        return 2

    # 3. --locale
    if locale not in ("en", "ar"):
        print("srt_to_ass: --locale must be en or ar (got %r)" % locale,
              file=sys.stderr)
        return 2

    # 4. pysubs2 dep.
    try:
        _check_pysubs2()
    except MissingDepError as exc:
        print("srt_to_ass: %s" % exc, file=sys.stderr)
        return 3

    # 5. Amiri font for Arabic -- surface lib/errors HINT when absent.
    if locale == "ar" and not _check_amiri_installed():
        if errors_mod is not None:
            print(
                "srt_to_ass: %s" % errors_mod.format_hint(
                    "missing_amiri_font", path=str(_default_amiri_target())
                ),
                file=sys.stderr,
            )
        else:
            print(
                "srt_to_ass: Amiri font not installed at %s; run "
                "book-kit/book_workflow/scripts/install_amiri.py"
                % _default_amiri_target(),
                file=sys.stderr,
            )
        return 3

    import pysubs2  # local import after dep check.

    try:
        subs = pysubs2.load(str(in_path))
    except Exception as exc:
        print("srt_to_ass: pysubs2.load failed: %s" % exc, file=sys.stderr)
        return 4

    if locale == "ar":
        # Patch Default style for Arabic.
        style = subs.styles.get("Default") or pysubs2.SSAStyle()
        style.fontname = "Amiri"
        style.fontsize = font_size
        style.outline = 1
        style.alignment = 2  # BOTTOM_CENTER
        subs.styles["Default"] = style
        # Force \\an2 on every line as belt-and-braces (HarfBuzz shaping
        # requires RTL-aware anchoring for Arabic ligatures).
        for line in subs:
            line.alignment = 2
        # WrapStyle=2: break long lines at the last whitespace. Critical
        # for Arabic because libass handles wrap differently for RTL.
        if hasattr(subs.info, "wrapstyle"):
            subs.info.wrapstyle = "2"
    # else (en): leave pysubs2 defaults; Default.Nudger = 0 is implicit.

    out_path.parent.mkdir(parents=True, exist_ok=True)
    try:
        subs.save(str(out_path))
    except OSError as exc:
        print("srt_to_ass: cannot write %s: %s" % (out_path, exc),
              file=sys.stderr)
        return 4

    print(
        "srt_to_ass: OK cues=%d locale=%s out=%s"
        % (len(subs), locale, out_path)
    )
    return 0


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------


def _build_parser():
    p = argparse.ArgumentParser(
        prog="srt_to_ass",
        description="Convert SRT to ASS via pysubs2 (Amiri for Arabic).",
    )
    p.add_argument("--in", dest="in_path", required=True,
                   help="Input SRT path (must resolve under repo root).")
    p.add_argument("--out", required=True,
                   help="Output ASS path (must resolve under repo root).")
    p.add_argument("--locale", required=True, choices=["en", "ar"],
                   help="Locale code (en: default sans; ar: Amiri + \\an2).")
    p.add_argument("--font-size", type=int, default=24,
                   help="Font size for Arabic (default 24).")
    return p


def main(argv=None):
    parser = _build_parser()
    args = parser.parse_args(argv)
    return run_convert(
        in_arg=args.in_path,
        out_arg=args.out,
        locale=args.locale,
        font_size=args.font_size,
    )


if __name__ == "__main__":
    sys.exit(main())
