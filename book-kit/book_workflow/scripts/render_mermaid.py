"""render_mermaid.py -- mermaid figure renderer for book-kit (P11).

Scans ``<book>/chapters/*.md`` for fenced ``mermaid`` blocks. For each block:

1. Writes the block source to ``figures/<slug>-ch-NN-mermaid-<idx>.mmd``.
2. Runs ``mmdc -i <mmd> -o figures/<slug>-ch-NN-mermaid-<idx>.png
   -b transparent`` (array-form subprocess, never ``shell=True``).
3. Replaces the block with ``![<caption>](figures/....png)`` in a mirrored
   copy under ``chapters-rendered/``. The source chapter is NEVER mutated.

Emits ``figures/mermaid-manifest.json``: a list of
``{chapter, index, source_hash, png_path}`` records, sorted by
``(chapter, index)`` so re-runs are byte-stable.

EXTERNAL DEPENDENCY -- mermaid-cli must be installed:

    npm install -g @mermaid-js/mermaid-cli

``mmdc`` is resolved via ``shutil.which`` before any rendering. If it is
missing AND at least one mermaid block was found, the script prints an
actionable install hint to stderr and exits 3 (nothing is written). If it
is missing and NO block was found, the script writes an empty manifest and
exits 0 -- a book with no diagrams must not break the pre-PDF pipeline.

Caption resolution, first match wins:
1. ``%% caption: <text>`` directive on any line inside the mermaid block.
2. The nearest preceding markdown heading in the chapter.
3. ``Figure <idx>``.

CLI:
    render_mermaid.py --book <book-root> [--slug <slug>] [--figures-dir <rel>]
                      [--out <rel>] [--manifest <rel>] [--chapter <ch-NN.md>]

``--figures-dir``, ``--out`` and ``--manifest`` are resolved relative to
``--book`` and are refused if they escape the book root (absolute paths
outside the root, or any ``..`` traversal) -- the P4 #14 / P6 compensating
control applied to this script's three writable paths.

Exit: 0 on success, 2 on input error (missing book, malformed block,
bad path), 3 when ``mmdc`` is required but not installed.

Stdlib-only. No new Python dependencies.
"""
from __future__ import annotations

import argparse
import hashlib
import io
import json
import re
import shutil
import subprocess
import sys
from pathlib import Path


def _force_utf8_stdio():
    """Keep argparse help and rendered markdown portable on Windows."""
    for stream in (sys.stdout, sys.stderr):
        try:
            stream.reconfigure(encoding="utf-8")
        except (AttributeError, io.UnsupportedOperation):
            pass


_force_utf8_stdio()

INSTALL_HINT = "npm install -g @mermaid-js/mermaid-cli"

# Opening fence for a mermaid block: 3+ backticks, optional space, "mermaid",
# optional trailing attributes, end of line.
_OPEN_RE = re.compile(r"^(\s*)(`{3,})\s*mermaid\s*$", re.IGNORECASE)
_CAPTION_RE = re.compile(r"^\s*%%\s*caption:\s*(.+?)\s*$", re.IGNORECASE)
_HEADING_RE = re.compile(r"^#{1,6}\s+(.+?)\s*$")


class MermaidError(Exception):
    """Raised for malformed input that should end the run with exit 2."""


# ---------------------------------------------------------------------------
# Parsing
# ---------------------------------------------------------------------------

def find_mermaid_blocks(text):
    """Return a list of block dicts found in one chapter's markdown text.

    Each dict carries ``index`` (1-based), ``source`` (block body without the
    fences), ``caption``, ``start`` and ``end`` (0-based inclusive line span
    of the whole fenced block).

    Raises ``MermaidError`` when an opening fence has no matching close.
    """
    lines = text.splitlines()
    blocks = []
    i = 0
    idx = 0
    while i < len(lines):
        m = _OPEN_RE.match(lines[i])
        if not m:
            i += 1
            continue
        indent, ticks = m.group(1), m.group(2)
        close_re = re.compile(r"^\s*`{%d,}\s*$" % len(ticks))
        end = None
        for j in range(i + 1, len(lines)):
            if close_re.match(lines[j]):
                end = j
                break
        if end is None:
            raise MermaidError(
                "unterminated mermaid block opened at line %d" % (i + 1)
            )
        idx += 1
        body = lines[i + 1:end]
        blocks.append(
            {
                "index": idx,
                "source": "\n".join(body).strip() + "\n",
                "caption": _caption_for(body, lines, i, idx),
                "start": i,
                "end": end,
                "indent": indent,
            }
        )
        i = end + 1
    return blocks


def _caption_for(body, lines, open_line, idx):
    """Resolve a block caption: %% caption -> nearest heading -> Figure N."""
    for line in body:
        m = _CAPTION_RE.match(line)
        if m:
            return m.group(1)
    for k in range(open_line - 1, -1, -1):
        m = _HEADING_RE.match(lines[k])
        if m:
            return m.group(1)
    return "Figure %d" % idx


def chapter_stem(chapter_path):
    """Return the ``ch-NN``-style stem used in figure filenames."""
    return Path(chapter_path).stem


def figure_basename(slug, chapter_path, index):
    """Build ``<slug>-<chapter-stem>-mermaid-<idx>`` (no extension)."""
    return "%s-%s-mermaid-%d" % (slug, chapter_stem(chapter_path), index)


def source_hash(source):
    """sha256 of the mermaid block source (stable across re-runs)."""
    return hashlib.sha256(source.encode("utf-8")).hexdigest()


def render_chapter_text(text, blocks, png_rel_paths):
    """Return the mirrored chapter text with each block replaced by an image.

    ``png_rel_paths`` is a list parallel to ``blocks`` holding the markdown
    link target for each figure (POSIX-style, relative to the chapter).
    """
    lines = text.splitlines()
    out = []
    cursor = 0
    for block, rel in zip(blocks, png_rel_paths):
        out.extend(lines[cursor:block["start"]])
        out.append(
            "%s![%s](%s)" % (block["indent"], block["caption"], rel)
        )
        cursor = block["end"] + 1
    out.extend(lines[cursor:])
    return "\n".join(out) + ("\n" if text.endswith("\n") else "")


# ---------------------------------------------------------------------------
# Path validation (P4 #14 / P6 compensating control)
# ---------------------------------------------------------------------------

def resolve_under(book_root, candidate, label):
    """Resolve ``candidate`` relative to ``book_root``, refusing escapes.

    Rejects any path containing a ``..`` component and any absolute path that
    does not live under ``book_root``. Returns the resolved ``Path``.
    """
    raw = Path(candidate)
    if ".." in raw.parts:
        raise MermaidError(
            "%s must not contain '..': %s" % (label, candidate)
        )
    target = raw if raw.is_absolute() else (book_root / raw)
    target = target.resolve()
    root = book_root.resolve()
    if target != root and root not in target.parents:
        raise MermaidError(
            "%s must resolve under the book root %s: %s"
            % (label, root, candidate)
        )
    return target


# ---------------------------------------------------------------------------
# Rendering
# ---------------------------------------------------------------------------

def run_mmdc(mmdc_path, mmd_path, png_path):
    """Invoke mermaid-cli for one diagram. Raises MermaidError on failure."""
    cmd = [
        mmdc_path,
        "-i",
        str(mmd_path),
        "-o",
        str(png_path),
        "-b",
        "transparent",
    ]
    try:
        subprocess.run(cmd, check=True, capture_output=True)
    except subprocess.CalledProcessError as exc:
        stderr = (exc.stderr or b"")
        if isinstance(stderr, bytes):
            stderr = stderr.decode("utf-8", "replace")
        raise MermaidError(
            "mmdc failed for %s: %s" % (mmd_path.name, stderr.strip())
        )
    except OSError as exc:
        raise MermaidError("cannot execute mmdc: %s" % exc)


def render_book(
    book_root,
    slug=None,
    figures_dir="figures",
    out_dir="chapters-rendered",
    manifest="figures/mermaid-manifest.json",
    chapter=None,
    mmdc_path=None,
):
    """Render every mermaid block under ``<book>/chapters/``.

    Returns the manifest list. Raises ``MermaidError`` on input problems.
    """
    book_root = Path(book_root)
    if not book_root.is_dir():
        raise MermaidError("book root does not exist: %s" % book_root)
    chapters_dir = book_root / "chapters"
    if not chapters_dir.is_dir():
        raise MermaidError("no chapters/ directory under %s" % book_root)

    slug = slug or book_root.resolve().name
    figures_path = resolve_under(book_root, figures_dir, "--figures-dir")
    out_path = resolve_under(book_root, out_dir, "--out")
    manifest_path = resolve_under(book_root, manifest, "--manifest")

    if chapter:
        candidates = [chapters_dir / Path(chapter).name]
        if not candidates[0].is_file():
            raise MermaidError("no such chapter: %s" % candidates[0])
    else:
        candidates = sorted(chapters_dir.glob("*.md"))

    # Parse everything first so a malformed block fails before any write.
    parsed = []
    total_blocks = 0
    for path in candidates:
        text = path.read_text(encoding="utf-8")
        blocks = find_mermaid_blocks(text)
        total_blocks += len(blocks)
        parsed.append((path, text, blocks))

    if total_blocks and not mmdc_path:
        raise MermaidError(
            "mmdc not found on PATH but %d mermaid block(s) need rendering. "
            "Install mermaid-cli with: %s" % (total_blocks, INSTALL_HINT)
        )

    records = []
    figures_path.mkdir(parents=True, exist_ok=True)
    out_path.mkdir(parents=True, exist_ok=True)

    for path, text, blocks in parsed:
        rel_targets = []
        for block in blocks:
            base = figure_basename(slug, path, block["index"])
            mmd_file = figures_path / (base + ".mmd")
            png_file = figures_path / (base + ".png")
            mmd_file.write_text(block["source"], encoding="utf-8")
            run_mmdc(mmdc_path, mmd_file, png_file)
            rel = _relative_link(out_path, png_file)
            rel_targets.append(rel)
            records.append(
                {
                    "chapter": path.name,
                    "index": block["index"],
                    "source_hash": source_hash(block["source"]),
                    "png_path": _relative_link(book_root, png_file),
                }
            )
        mirrored = render_chapter_text(text, blocks, rel_targets)
        (out_path / path.name).write_text(mirrored, encoding="utf-8")

    records.sort(key=lambda r: (r["chapter"], r["index"]))
    manifest_path.parent.mkdir(parents=True, exist_ok=True)
    manifest_path.write_text(
        json.dumps(records, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )
    return records


def _relative_link(base, target):
    """POSIX-style relative path from ``base`` to ``target`` (best effort)."""
    base = Path(base).resolve()
    target = Path(target).resolve()
    try:
        return target.relative_to(base).as_posix()
    except ValueError:
        import os

        return Path(os.path.relpath(target, base)).as_posix()


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def main(argv=None):
    parser = argparse.ArgumentParser(
        description=(
            "Render fenced mermaid blocks in a book's chapters to PNG "
            "figures. Requires mermaid-cli: " + INSTALL_HINT
        )
    )
    parser.add_argument(
        "--book",
        required=True,
        type=Path,
        help="book root (the directory containing chapters/)",
    )
    parser.add_argument(
        "--slug",
        default=None,
        help="figure-name prefix (default: the book root directory name)",
    )
    parser.add_argument(
        "--figures-dir",
        default="figures",
        help="figure output dir, relative to --book (default: figures)",
    )
    parser.add_argument(
        "--out",
        default="chapters-rendered",
        help="mirrored chapter dir, relative to --book "
        "(default: chapters-rendered)",
    )
    parser.add_argument(
        "--manifest",
        default="figures/mermaid-manifest.json",
        help="manifest path, relative to --book "
        "(default: figures/mermaid-manifest.json)",
    )
    parser.add_argument(
        "--chapter",
        default=None,
        help="render a single chapter file name instead of all of them",
    )
    args = parser.parse_args(argv)

    mmdc_path = shutil.which("mmdc")
    if mmdc_path is None:
        print(
            "render_mermaid: mmdc not found on PATH. Install with: %s"
            % INSTALL_HINT,
            file=sys.stderr,
        )

    try:
        records = render_book(
            args.book,
            slug=args.slug,
            figures_dir=args.figures_dir,
            out_dir=args.out,
            manifest=args.manifest,
            chapter=args.chapter,
            mmdc_path=mmdc_path,
        )
    except MermaidError as exc:
        print("render_mermaid: %s" % exc, file=sys.stderr)
        return 3 if mmdc_path is None and "mmdc not found" in str(exc) else 2
    except OSError as exc:
        print("render_mermaid: %s" % exc, file=sys.stderr)
        return 2

    print("render_mermaid: %d figure(s) rendered" % len(records))
    return 0


if __name__ == "__main__":
    sys.exit(main())
