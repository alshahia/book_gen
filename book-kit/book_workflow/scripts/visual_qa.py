"""visual_qa.py -- PyMuPDF page diagnostics for book-kit (P13).

Scans a rendered book PDF and emits per-page diagnostics:

1. A PNG render of every page (dpi=150), named
   ``<figures-dir>/<slug>-page-NN.png`` (NN zero-padded to a stable width).
2. Widow/orphan counts derived from the text-layout blocks (rough
   page-level heuristic; see WIDOW/ORPHAN HEURISTIC below).
3. A page-number table of marker-string matches (e.g. chapter titles
   supplied via ``--markers``).

CLI:
    visual_qa.py <book.pdf> [--markers FILE]
                  [--out PATH] [--figures-dir DIR] [--slug NAME]

``--markers`` is a UTF-8 text file with one marker per line. Blank lines
and lines starting with ``#`` are ignored. When the flag is omitted, no
marker scan is performed and the Markers column is ``--`` for every page.

EXIT CODES
    0  diagnostics written
    2  input error (PDF not found, malformed --markers, --out/--figures-dir
       outside the PDF's parent directory, PyMuPDF cannot open the PDF)

EXTERNAL DEPENDENCY -- PyMuPDF:
    pip install pymupdf
The script imports the package as ``pymupdf as fitz`` so it works on
PyMuPDF >= 1.28 where the top-level ``fitz`` module is deprecated and
emits ``DeprecationWarning`` on import. Older PyMuPDF releases (where
``import fitz`` was canonical) are also covered by the alias because
both expose the same ``Document`` / ``Page`` surface used here.

WIDOW/ORPHAN HEURISTIC
    widow  -- the last line of a text block that lands in the top
              20 percent of the page AND whose line width is strictly
              less than one-third of the page width. Rough proxy for a
              paragraph ending whose tail-line was orphaned to the next
              page.
    orphan -- the first line of a text block that lands in the bottom
              20 percent of the page. Rough proxy for a paragraph
              starting whose head-line was left behind on the previous
              page.
These are page-level heuristics, not typesetting-perfect detectors.
A future P13.x can swap in a paragraph-reconstruction algorithm when
the project needs higher fidelity.

PATH VALIDATION (P4 #14 / P6 / P11 inheritance)
    ``--out`` and ``--figures-dir`` are resolved relative to the PDF's
    parent directory. Any value containing a ``..`` component, or any
    absolute path that does not resolve under the PDF parent, is refused
    before a single byte is written.
"""
from __future__ import annotations

import argparse
import io
import sys
from pathlib import Path


def _force_utf8_stdio():
    """Keep argparse help + emitted markdown portable on Windows consoles."""
    for stream in (sys.stdout, sys.stderr):
        try:
            stream.reconfigure(encoding="utf-8")
        except (AttributeError, io.UnsupportedOperation):
            pass


_force_utf8_stdio()

try:
    import pymupdf as fitz  # PyMuPDF >= 1.28 (top-level 'fitz' is deprecated)
except ImportError as exc:  # pragma: no cover - import guard
    print(
        "visual_qa: PyMuPDF is required. Install with: pip install pymupdf",
        file=sys.stderr,
    )
    raise SystemExit(2) from exc


class VisualQAError(Exception):
    """Raised for input errors that should end the run with exit 2."""


# Page-region thresholds (top/bottom 20%) for the widow/orphan heuristic.
_TOP_FRACTION = 0.20
_BOTTOM_FRACTION = 0.20
# Widow width ceiling: a "last line" is flagged when its width is
# strictly below this fraction of the page width.
_WIDOW_WIDTH_FRACTION = 1.0 / 3.0

# Empty-cell sentinel for the markdown table (ASCII per the P13 gate;
# no U+2014 / em-dash).
EMPTY_CELL = "--"


def resolve_under(root, candidate, label):
    """Resolve ``candidate`` relative to ``root``, refusing escapes.

    Rejects any path containing a ``..`` component and any absolute path
    that does not live under ``root``. Returns the resolved ``Path``.
    """
    raw = Path(candidate)
    if ".." in raw.parts:
        raise VisualQAError(
            "%s must not contain '..': %s" % (label, candidate)
        )
    target = raw if raw.is_absolute() else (root / raw)
    target = target.resolve()
    root = root.resolve()
    if target != root and root not in target.parents:
        raise VisualQAError(
            "%s must resolve under %s: %s" % (label, root, candidate)
        )
    return target


def load_markers(path):
    """Read the markers file: one marker per line, blanks + # ignored."""
    p = Path(path)
    if not p.is_file():
        raise VisualQAError("markers file not found: %s" % p)
    markers = []
    for line in p.read_text(encoding="utf-8").splitlines():
        s = line.strip()
        if not s or s.startswith("#"):
            continue
        markers.append(s)
    return markers


def page_widows_orphans(page):
    """Return ``(widow_count, orphan_count)`` for a PyMuPDF Page.

    Iterates ``page.get_text("dict")`` blocks. Image blocks (type 1)
    have no lines and are skipped. For each text block:
      - widow candidate: last line whose y0 is in the top 20 percent of
        the page AND whose width is strictly below one third of the
        page width.
      - orphan candidate: first line whose y0 is in the bottom 20 percent
        of the page.
    """
    width = page.rect.width
    height = page.rect.height
    top_threshold = height * _TOP_FRACTION
    bottom_threshold = height * (1.0 - _BOTTOM_FRACTION)
    widow_width_ceiling = width * _WIDOW_WIDTH_FRACTION

    data = page.get_text("dict")
    blocks = data.get("blocks", [])
    widows = 0
    orphans = 0
    for block in blocks:
        if block.get("type", 0) != 0:
            continue
        lines = block.get("lines", [])
        if not lines:
            continue
        last = lines[-1]
        last_bbox = last.get("bbox")
        if last_bbox:
            y0 = last_bbox[1]
            line_width = last_bbox[2] - last_bbox[0]
            if y0 < top_threshold and line_width < widow_width_ceiling:
                widows += 1
        first = lines[0]
        first_bbox = first.get("bbox")
        if first_bbox and first_bbox[1] > bottom_threshold:
            orphans += 1
    return widows, orphans


def page_markers(page, markers):
    """Return the list of marker strings found on this page."""
    if not markers:
        return []
    matched = []
    for marker in markers:
        hits = page.search_for(marker)
        if hits:
            matched.append(marker)
    return matched


def chapter_label(page_index, matched_markers):
    """Pick a chapter label for a page row.

    Strategy: first matching marker wins (the user lists markers in
    order, so the earliest listed title is most likely the chapter
    heading). If no marker matches and the page is page 1, use
    ``cover``. Otherwise leave the cell empty -- the page is interior
    matter (blank page, back-matter) without a chapter heading marker.
    """
    if matched_markers:
        return matched_markers[0]
    if page_index == 1:
        return "cover"
    return ""


def render_pages(pdf_path, figures_dir, slug):
    """Render every page of ``pdf_path`` to PNG at dpi=150.

    Returns ``(doc, pages)``. The caller closes ``doc`` once it is done
    walking ``pages``.
    """
    doc = fitz.open(str(pdf_path))
    figures_dir.mkdir(parents=True, exist_ok=True)
    n = doc.page_count
    pad = max(2, len(str(n)))
    pages = []
    for i, page in enumerate(doc, start=1):
        png_name = "%s-page-%s.png" % (slug, str(i).zfill(pad))
        png_path = figures_dir / png_name
        pix = page.get_pixmap(dpi=150)
        pix.save(str(png_path))
        pages.append(page)
    return doc, pages


def build_table(pages, markers):
    """Build the per-page row dicts for the markdown table."""
    rows = []
    for i, page in enumerate(pages, start=1):
        matched = page_markers(page, markers)
        widows, orphans = page_widows_orphans(page)
        chapter = chapter_label(i, matched)
        markers_cell = ", ".join(matched) if matched else EMPTY_CELL
        rows.append({
            "page": i,
            "chapter": chapter or EMPTY_CELL,
            "markers": markers_cell,
            "widows": widows,
            "orphans": orphans,
        })
    return rows


def render_md(rows):
    """Render the markdown report (header + table) from ``rows``."""
    lines = [
        "# Visual QA report",
        "",
        "| Page | Chapter | Markers | Widows | Orphans |",
        "| --- | --- | --- | --- | --- |",
    ]
    for r in rows:
        lines.append(
            "| %d | %s | %s | %d | %d |"
            % (r["page"], r["chapter"], r["markers"], r["widows"], r["orphans"])
        )
    lines.append("")
    return "\n".join(lines)


def run(pdf_path, markers_path=None, out_path=None, figures_dir=None, slug=None):
    """Top-level orchestrator. Returns the process exit code."""
    pdf = Path(pdf_path)
    if not pdf.is_file():
        print("visual_qa: PDF not found: %s" % pdf, file=sys.stderr)
        return 2
    root = pdf.parent
    if slug is None:
        slug = pdf.stem

    default_figures = root / "figures"
    default_out = root / "figures" / "visual-qa.md"

    try:
        figs = resolve_under(root, figures_dir or default_figures, "--figures-dir")
        out = resolve_under(root, out_path or default_out, "--out")
        markers = []
        if markers_path:
            markers = load_markers(markers_path)
    except VisualQAError as exc:
        print("visual_qa: %s" % exc, file=sys.stderr)
        return 2

    try:
        doc, pages = render_pages(pdf, figs, slug)
    except (RuntimeError, OSError, fitz.FileDataError, ValueError) as exc:
        # PyMuPDF raises RuntimeError / FileDataError / ValueError for bad PDFs.
        print(
            "visual_qa: cannot read PDF %s: %s" % (pdf, exc),
            file=sys.stderr,
        )
        return 2

    try:
        rows = build_table(pages, markers)
    finally:
        doc.close()

    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(render_md(rows), encoding="utf-8")
    print(
        "visual_qa: %d page(s), %d marker(s) -> %s"
        % (len(pages), len(markers), out)
    )
    return 0


def main(argv=None):
    parser = argparse.ArgumentParser(
        description=(
            "PyMuPDF page diagnostics for a rendered book PDF: "
            "per-page PNG + widow/orphan counts + marker-string index."
        ),
    )
    parser.add_argument("pdf", help="Path to the rendered book PDF.")
    parser.add_argument(
        "--markers",
        default=None,
        help="UTF-8 markers file, one marker per line (chapter titles). "
             "Omitted -> no marker scan; Markers column is -- for every page.",
    )
    parser.add_argument(
        "--out",
        default=None,
        help="Output markdown path, resolved under the PDF parent directory "
             "(default: <pdf-parent>/figures/visual-qa.md).",
    )
    parser.add_argument(
        "--figures-dir",
        default=None,
        help="PNG output directory, resolved under the PDF parent "
             "(default: <pdf-parent>/figures).",
    )
    parser.add_argument(
        "--slug",
        default=None,
        help="Prefix for rendered PNG filenames (default: <pdf-stem>).",
    )
    args = parser.parse_args(argv)
    return run(
        args.pdf,
        markers_path=args.markers,
        out_path=args.out,
        figures_dir=args.figures_dir,
        slug=args.slug,
    )


if __name__ == "__main__":
    sys.exit(main())
