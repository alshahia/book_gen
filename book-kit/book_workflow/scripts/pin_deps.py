"""pin_deps.py -- pin chapter code dependencies via `uv pip compile` (P14).

Walks ``<book>/chapters/code/ch-NN/`` looking for ``requirements.txt`` or
``pyproject.toml``. For each chapter that has an input file, runs
``uv pip compile <input> -o <output>/uv.lock`` and copies the generated
``uv.lock`` next to the input. Emits
``<book>/chapters/code/CH-DEP-STATUS.md`` with a per-chapter row
``{chapter, packages, lock_status}``.

CLI:
    pin_deps.py --book <book-root> [--code-dir REL]

EXIT CODES
    0  status table written
    2  input error (book root missing, --code-dir escapes --book)

LOCK FORMAT
    `uv pip compile` writes a requirements.txt-style ``uv.lock`` by
    default (one ``name==version`` line per package). The parser in
    :func:`_load_lock_packages` matches that shape directly. PEP 751
    ``[[package]]`` blocks are ignored -- the script tolerates them
    by simply not matching them, so a future uv that switches defaults
    degrades to "no packages detected" without crashing (the status row
    will read ``packages=0 lock_status=pinned`` which a future patch can
    address; for now uv 0.7.x always writes the requirements.txt form).

PATH VALIDATION (P4 #14 / P6 / P11 / P13 inheritance)
    ``--code-dir`` is resolved relative to ``--book``. Any value
    containing a ``..`` component, or any absolute path that does not
    resolve under the book root, is refused before a single subprocess
    is spawned.
"""
from __future__ import annotations

import argparse
import re
import shutil
import subprocess
import sys
from pathlib import Path


CODE_DIR_DEFAULT = "chapters/code"
STATUS_FILENAME = "CH-DEP-STATUS.md"
COMPILE_TIMEOUT = 120

# uv pip compile's default output format is one `name==version` line per
# resolved package; the header lines start with `#` and are skipped.
_LOCK_LINE_RE = re.compile(r"^([A-Za-z0-9_.\-]+)==([^\s]+)\s*$")


def _force_utf8_stdio():
    """Reconfigure stdout/stderr to UTF-8 on Windows consoles (P4 #15 / P5 #22)."""
    for stream in (sys.stdout, sys.stderr):
        try:
            stream.reconfigure(encoding="utf-8")
        except (AttributeError, OSError):
            pass


_force_utf8_stdio()


class PinDepsError(Exception):
    """Raised for input errors that should end the run with exit 2."""


def resolve_under(root, candidate, label):
    """Resolve ``candidate`` relative to ``root``, refusing escapes.

    Rejects any path containing a ``..`` component and any absolute path
    that does not live under ``root``. Returns the resolved ``Path``.
    """
    raw = Path(candidate)
    if ".." in raw.parts:
        raise PinDepsError(
            "%s must not contain '..': %s" % (label, candidate)
        )
    target = raw if raw.is_absolute() else (root / raw)
    target = target.resolve()
    root = root.resolve()
    if target != root and root not in target.parents:
        raise PinDepsError(
            "%s must resolve under %s: %s" % (label, root, candidate)
        )
    return target


def _find_input(chapter_dir):
    """Find the dependency input file in ``chapter_dir``.

    Preference order: ``pyproject.toml`` wins over ``requirements.txt``
    when both are present (pyproject is the more expressive declaration
    and matches the project's own metadata conventions).

    Returns the input ``Path`` or ``None`` when neither file exists.
    """
    pp = chapter_dir / "pyproject.toml"
    if pp.exists():
        return pp
    req = chapter_dir / "requirements.txt"
    if req.exists():
        return req
    return None


def _pin_chapter(chapter_dir, uv_path):
    """Pin one chapter's deps via ``uv pip compile``.

    Returns ``(status, packages, error_msg)``. ``status`` is one of
    ``pinned``, ``no_deps``, ``uv_missing``, ``compile_failed``,
    ``missing_input``. ``packages`` is the count of resolved packages
    in the produced ``uv.lock`` (0 on failure paths).
    """
    input_file = _find_input(chapter_dir)
    if input_file is None:
        return ("missing_input", 0, "no requirements.txt or pyproject.toml")

    if uv_path is None:
        return ("uv_missing", 0, "uv not on PATH; install with `pip install uv`")

    out_lock = chapter_dir / "uv.lock"
    argv = [uv_path, "pip", "compile", str(input_file),
            "-o", str(out_lock), "--quiet"]
    try:
        proc = subprocess.run(argv, capture_output=True, text=True,
                              timeout=COMPILE_TIMEOUT)
    except subprocess.TimeoutExpired:
        return ("compile_failed", 0,
                "uv pip compile timed out after %ds" % COMPILE_TIMEOUT)
    except (OSError, FileNotFoundError) as exc:
        return ("compile_failed", 0, "uv pip compile failed: %s" % exc)

    if proc.returncode != 0:
        err = (proc.stderr or proc.stdout or "").strip()
        return ("compile_failed", 0, err[:500] or "uv pip compile failed")

    if not out_lock.exists():
        return ("compile_failed", 0, "uv.lock not produced")

    text = out_lock.read_text(encoding="utf-8")
    packages = sum(1 for line in text.splitlines() if _LOCK_LINE_RE.match(line))
    return ("pinned", packages, None)


def walk_chapters(code_dir):
    """Yield ``(chapter_label, chapter_dir)`` for every subdir of ``code_dir``.

    Sorted by basename so the status table is deterministic across runs.
    """
    if not code_dir.is_dir():
        return
    for sub in sorted(code_dir.iterdir()):
        if sub.is_dir():
            yield sub.name, sub


def render_status_table(rows):
    """Render the per-chapter status markdown table.

    ``rows`` is a list of ``(chapter, packages, lock_status)``. The table
    always carries a header row; an empty ``rows`` list renders a single
    placeholder data row with ``--`` cells so the file is non-empty.
    """
    lines = [
        "# Chapter dependency status",
        "",
        "| Chapter | Packages | Lock status |",
        "| --- | --- | --- |",
    ]
    if not rows:
        lines.append("| -- | -- | -- |")
    else:
        for chapter, packages, status in rows:
            lines.append("| %s | %d | %s |" % (chapter, packages, status))
    lines.append("")
    return "\n".join(lines)


def run_pin(book_root, code_dir_name=CODE_DIR_DEFAULT):
    """Top-level orchestrator. Returns the process exit code.

    The ``uv`` binary is resolved once via :func:`shutil.which`; if it
    is absent every chapter falls through to ``uv_missing`` status
    (no exception, no crash -- the script's job is to surface state,
    not to require uv on PATH).
    """
    root = Path(book_root)
    if not root.is_dir():
        print("pin_deps: book root not found: %s" % root, file=sys.stderr)
        return 2

    try:
        code_dir = resolve_under(root, code_dir_name, "--code-dir")
    except PinDepsError as exc:
        print("pin_deps: %s" % exc, file=sys.stderr)
        return 2

    code_dir.mkdir(parents=True, exist_ok=True)
    uv_path = shutil.which("uv")

    rows = []
    for chapter_label, chapter_dir in walk_chapters(code_dir):
        status, packages, err = _pin_chapter(chapter_dir, uv_path)
        if err:
            print("pin_deps: %s: %s: %s" % (chapter_label, status, err),
                  file=sys.stderr)
        rows.append((chapter_label, packages, status))

    status_file = code_dir / STATUS_FILENAME
    status_file.write_text(render_status_table(rows), encoding="utf-8")

    pinned = sum(1 for _, _, s in rows if s == "pinned")
    n = len(rows)
    print("pin_deps: %d/%d chapter(s) pinned -> %s" % (pinned, n, status_file),
          file=sys.stderr)
    return 0


def main(argv=None):
    p = argparse.ArgumentParser(
        description=(
            "Walk <book>/chapters/code/ch-NN/ for requirements.txt or "
            "pyproject.toml, pin via `uv pip compile`, emit "
            "CH-DEP-STATUS.md. Requires the `uv` CLI on PATH."
        ),
    )
    p.add_argument("--book", required=True,
                   help="Book root (books/<slug>/).")
    p.add_argument("--code-dir", default=CODE_DIR_DEFAULT,
                   help="Code directory relative to --book "
                        "(default: %s)." % CODE_DIR_DEFAULT)
    args = p.parse_args(argv)
    return run_pin(args.book, args.code_dir)


if __name__ == "__main__":
    sys.exit(main())