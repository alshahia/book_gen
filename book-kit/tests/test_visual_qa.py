"""Tests for visual_qa.py -- P13 PyMuPDF page diagnostics.

Fixture PDFs are built programmatically in ``tmp_path`` using PyMuPDF
itself, so no binary fixtures live in the repo. Each helper below writes
a deterministic PDF, then the test invokes ``run`` (the library entry
point) and asserts on the emitted ``visual-qa.md`` markdown.
"""
import pymupdf
import pytest

from visual_qa import run, main, EMPTY_CELL


def make_clean_pdf(tmp_path, pages=3, body_text=None, y=400):
    """N-page A4 PDF, one ``insert_text`` line per page at y.

    Default y=400 lands the line in the middle of an A4 page so the
    widow/orphan heuristic sees no top- or bottom-region block and the
    counters come out as 0/0 for every page.
    """
    if body_text is None:
        body_text = "Lorem ipsum dolor sit amet consectetur"
    pdf = tmp_path / "clean.pdf"
    doc = pymupdf.open()
    for i in range(pages):
        page = doc.new_page(width=595, height=842)  # A4
        page.insert_text((50, y), body_text)
    doc.save(str(pdf))
    doc.close()
    return pdf


def make_widow_pdf(tmp_path):
    """1-page A4 PDF with a short text inserted at the very top.

    Yields widow=1 because the inserted block's last line lands in the
    top 20 percent of the page AND its width is well under one third of
    the page width.
    """
    pdf = tmp_path / "widow.pdf"
    doc = pymupdf.open()
    page = doc.new_page(width=595, height=842)
    page.insert_text((50, 50), "Tiny")
    doc.save(str(pdf))
    doc.close()
    return pdf


def make_orphan_pdf(tmp_path):
    """1-page A4 PDF with a short text inserted at the very bottom.

    Yields orphan=1 because the inserted block's first line lands in the
    bottom 20 percent of the page.
    """
    pdf = tmp_path / "orphan.pdf"
    doc = pymupdf.open()
    page = doc.new_page(width=595, height=842)
    page.insert_text((50, 800), "Tiny")
    doc.save(str(pdf))
    doc.close()
    return pdf


def _data_rows(md_text):
    """Return the data rows (excluding header + separator) of the markdown table."""
    return [
        line for line in md_text.splitlines()
        if line.startswith("| ") and "---" not in line and "Page" not in line
    ]


def _cells(row):
    """Split a markdown row into stripped cells, dropping the outer empties."""
    return [c.strip() for c in row.split("|")][1:-1]


def test_three_pages_emit_three_rows(tmp_path):
    """A 3-page fixture emits exactly 3 data rows + 3 zero-padded PNGs."""
    pdf = make_clean_pdf(tmp_path, pages=3)
    figs = tmp_path / "figures"
    out = figs / "visual-qa.md"
    rc = run(str(pdf), out_path=str(out), figures_dir=str(figs))
    assert rc == 0
    body = out.read_text(encoding="utf-8")
    assert len(_data_rows(body)) == 3
    assert (figs / "clean-page-01.png").exists()
    assert (figs / "clean-page-02.png").exists()
    assert (figs / "clean-page-03.png").exists()


def test_no_markers_yields_dash(tmp_path):
    """When --markers is omitted, every row's Markers cell is EMPTY_CELL."""
    pdf = make_clean_pdf(tmp_path, pages=2)
    figs = tmp_path / "figures"
    out = figs / "visual-qa.md"
    rc = run(str(pdf), out_path=str(out), figures_dir=str(figs))
    assert rc == 0
    body = out.read_text(encoding="utf-8")
    rows = _data_rows(body)
    assert len(rows) == 2
    for row in rows:
        cells = _cells(row)
        # Layout: | Page | Chapter | Markers | Widows | Orphans |
        assert cells[2] == EMPTY_CELL


def test_marker_indexed_on_each_page(tmp_path):
    """A marker present on every page shows up in the Markers column for each."""
    pdf = make_clean_pdf(tmp_path, pages=3, body_text="UNIQUE TOKEN")
    markers = tmp_path / "markers.txt"
    markers.write_text("UNIQUE TOKEN\n", encoding="utf-8")
    figs = tmp_path / "figures"
    out = figs / "visual-qa.md"
    rc = run(str(pdf), markers_path=str(markers),
             out_path=str(out), figures_dir=str(figs))
    assert rc == 0
    body = out.read_text(encoding="utf-8")
    rows = _data_rows(body)
    assert len(rows) == 3
    for row in rows:
        cells = _cells(row)
        assert "UNIQUE TOKEN" in cells[2]


def test_marker_not_found_yields_dash(tmp_path):
    """A marker absent from every page yields EMPTY_CELL in every Markers cell."""
    pdf = make_clean_pdf(tmp_path, pages=2, body_text="Hello world")
    markers = tmp_path / "markers.txt"
    markers.write_text("This String Does Not Exist Anywhere\n", encoding="utf-8")
    figs = tmp_path / "figures"
    out = figs / "visual-qa.md"
    rc = run(str(pdf), markers_path=str(markers),
             out_path=str(out), figures_dir=str(figs))
    assert rc == 0
    body = out.read_text(encoding="utf-8")
    rows = _data_rows(body)
    assert len(rows) == 2
    for row in rows:
        cells = _cells(row)
        assert cells[2] == EMPTY_CELL


def test_widow_detected(tmp_path):
    """A page with a short line at the top flags widow=1."""
    pdf = make_widow_pdf(tmp_path)
    figs = tmp_path / "figures"
    out = figs / "visual-qa.md"
    rc = run(str(pdf), out_path=str(out), figures_dir=str(figs))
    assert rc == 0
    body = out.read_text(encoding="utf-8")
    rows = _data_rows(body)
    assert len(rows) == 1
    cells = _cells(rows[0])
    assert int(cells[3]) >= 1


def test_orphan_detected(tmp_path):
    """A page with a short line at the bottom flags orphan=1."""
    pdf = make_orphan_pdf(tmp_path)
    figs = tmp_path / "figures"
    out = figs / "visual-qa.md"
    rc = run(str(pdf), out_path=str(out), figures_dir=str(figs))
    assert rc == 0
    body = out.read_text(encoding="utf-8")
    rows = _data_rows(body)
    assert len(rows) == 1
    cells = _cells(rows[0])
    assert int(cells[4]) >= 1


def test_clean_fixture_zero_widow_zero_orphan(tmp_path):
    """A 3-page fixture with mid-page text yields widows=orphans=0 per row."""
    pdf = make_clean_pdf(tmp_path, pages=3)
    figs = tmp_path / "figures"
    out = figs / "visual-qa.md"
    rc = run(str(pdf), out_path=str(out), figures_dir=str(figs))
    assert rc == 0
    body = out.read_text(encoding="utf-8")
    rows = _data_rows(body)
    assert len(rows) == 3
    for row in rows:
        cells = _cells(row)
        assert int(cells[3]) == 0
        assert int(cells[4]) == 0


def test_out_outside_pdf_parent_rejected(tmp_path):
    """--out pointing outside the PDF parent directory is refused (exit 2)."""
    pdf = make_clean_pdf(tmp_path, pages=1)
    rc = run(
        str(pdf),
        out_path="/tmp/external/report.md",
        figures_dir=str(tmp_path / "figures"),
    )
    assert rc == 2


def test_figures_dir_outside_pdf_parent_rejected(tmp_path):
    """--figures-dir pointing outside the PDF parent directory is refused (exit 2)."""
    pdf = make_clean_pdf(tmp_path, pages=1)
    rc = run(
        str(pdf),
        out_path=str(tmp_path / "out.md"),
        figures_dir="/tmp/external",
    )
    assert rc == 2


def test_out_with_dotdot_rejected(tmp_path):
    """A ``..`` component in --out is refused before any byte is written."""
    pdf = make_clean_pdf(tmp_path, pages=1)
    rc = run(
        str(pdf),
        out_path=str(tmp_path / "figures" / ".." / "evil.md"),
        figures_dir=str(tmp_path / "figures"),
    )
    assert rc == 2


def test_missing_pdf_argument_rejected():
    """argparse rejects the missing positional with SystemExit(2)."""
    with pytest.raises(SystemExit) as exc_info:
        main([])
    assert exc_info.value.code == 2


def test_pdf_not_found_rejected(tmp_path):
    """run() refuses a non-existent PDF with exit 2 and writes no files."""
    rc = run(
        str(tmp_path / "no-such.pdf"),
        out_path=str(tmp_path / "out.md"),
        figures_dir=str(tmp_path / "figures"),
    )
    assert rc == 2
    assert not (tmp_path / "out.md").exists()


def test_chapter_label_cover_for_page_one(tmp_path):
    """Page 1 without marker matches is labelled 'cover' (plan spec verbatim)."""
    pdf = make_clean_pdf(tmp_path, pages=2)
    figs = tmp_path / "figures"
    out = figs / "visual-qa.md"
    rc = run(str(pdf), out_path=str(out), figures_dir=str(figs))
    assert rc == 0
    body = out.read_text(encoding="utf-8")
    rows = _data_rows(body)
    cells_page1 = _cells(rows[0])
    cells_page2 = _cells(rows[1])
    assert cells_page1[1] == "cover"
    assert cells_page2[1] == EMPTY_CELL


def test_markers_file_comments_and_blanks_skipped(tmp_path):
    """Blank lines and # comments in the markers file are ignored."""
    pdf = make_clean_pdf(tmp_path, pages=1, body_text="Hello")
    markers = tmp_path / "markers.txt"
    markers.write_text(
        "# a comment\n\n  \nHELLO\n# another\n",
        encoding="utf-8",
    )
    figs = tmp_path / "figures"
    out = figs / "visual-qa.md"
    rc = run(str(pdf), markers_path=str(markers),
             out_path=str(out), figures_dir=str(figs))
    assert rc == 0
    body = out.read_text(encoding="utf-8")
    assert "HELLO" in body
    # The comment lines themselves never reach the markdown
    assert "a comment" not in body
    assert "another" not in body
