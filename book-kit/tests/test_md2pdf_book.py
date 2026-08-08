"""pytest tests for md2pdf.py --book mode (P12).

Chrome is not installed in this environment, so the PDF path is exercised
through a mocked subprocess and the acceptance criteria are verified against
the assembled HTML (cover first, preface, chapters in toc.md order,
back-matter, ToC links, head metadata, counter(page) CSS, paper size, fonts).

All docstrings and assertions here are ASCII-only. Arabic body text lives in
the generated fixture chapters, which is where it belongs.
"""
import subprocess
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).parent.parent / "book_workflow" / "scripts"))
import md2pdf  # noqa: E402


STYLE_GUIDE = """---
paper_size: B5
fonts: {body: Cairo, display: Amiri}
cover_text: |
  Fixture Book
  A three-chapter smoke test
title: Fixture Book
author: Fixture Author
---

# Style Guide

Body rules live below the frontmatter.
"""

TOC = """# Table of Contents

1. [Part 1](chapters/ch-01.md)
2. [Part 2](chapters/ch-02.md)
3. [Part 3](chapters/ch-03.md)
"""


def make_book(root, chapters=3, style_guide=STYLE_GUIDE, toc=TOC,
              preface=True, backmatter=True):
    """Plant a minimal book tree and return its root Path."""
    root = Path(root)
    (root / "chapters").mkdir(parents=True, exist_ok=True)
    if toc is not None:
        (root / "toc.md").write_text(toc, encoding="utf-8")
    if style_guide is not None:
        (root / "style-guide.md").write_text(style_guide, encoding="utf-8")
    for n in range(1, chapters + 1):
        body = (
            "# \u0627\u0644\u0641\u0635\u0644 %d\n\n"
            "MARKER-CH-%02d\n\n"
            "\u0646\u0635 \u0639\u0631\u0628\u064a \u0642\u0635\u064a\u0631 "
            "\u0644\u0644\u0627\u062e\u062a\u0628\u0627\u0631.\n" % (n, n)
        )
        (root / "chapters" / ("ch-%02d.md" % n)).write_text(body, encoding="utf-8")
    if preface:
        (root / "preface.html").write_text(
            "<p>MARKER-PREFACE</p>\n", encoding="utf-8")
    if backmatter:
        (root / "back-matter.html").write_text(
            "<p>MARKER-BACKMATTER</p>\n", encoding="utf-8")
    return root


def test_three_chapter_book_assembles_in_order(tmp_path):
    """Cover, preface, ToC, 3 chapters in toc order, back-matter, all present."""
    root = make_book(tmp_path / "book-mini")
    document, entries, meta = md2pdf.assemble_book_html(root)

    assert len(entries) == 3
    assert [e["href"] for e in entries] == [
        "chapters/ch-01.md", "chapters/ch-02.md", "chapters/ch-03.md"]

    positions = [
        document.index('id="cover"'),
        document.index("MARKER-PREFACE"),
        document.index('id="toc"'),
        document.index("MARKER-CH-01"),
        document.index("MARKER-CH-02"),
        document.index("MARKER-CH-03"),
        document.index("MARKER-BACKMATTER"),
    ]
    assert positions == sorted(positions), "sections out of order: %r" % positions

    # Cover must be the first section in the body.
    assert document.index('id="cover"') < document.index("<body>") + 200


def test_assembled_html_carries_toc_links_and_section_ids(tmp_path):
    """The auto-generated ToC links to every chapter's section id."""
    root = make_book(tmp_path / "book-mini")
    document, entries, _ = md2pdf.assemble_book_html(root)
    for entry in entries:
        assert '<a href="#%s">' % entry["id"] in document
        assert 'id="%s"' % entry["id"] in document
    assert entries[0]["id"] == "ch-01"


def test_assembled_html_has_page_counter_paper_size_and_fonts(tmp_path):
    """counter(page) in @page, B5 dimensions, and both frontmatter fonts."""
    root = make_book(tmp_path / "book-mini")
    document, _, meta = md2pdf.assemble_book_html(root)
    assert "counter(page)" in document
    assert "@bottom-right" in document
    assert "@page :first" in document
    assert meta["paper_size"] == "B5"
    assert "176mm 250mm" in document
    assert meta["fonts"] == {"body": "Cairo", "display": "Amiri"}
    assert "Cairo" in document and "Amiri" in document


def test_assembled_html_has_metadata_in_head(tmp_path):
    """CLI metadata lands in <head> and beats the style-guide frontmatter."""
    root = make_book(tmp_path / "book-mini")
    document, _, _ = md2pdf.assemble_book_html(
        root,
        metadata={
            "title": "CLI Title",
            "author": "CLI Author",
            "isbn": "978-0-00-000000-0",
            "build_date": "2026-08-08",
        },
    )
    head = document.split("</head>")[0]
    assert "<title>CLI Title</title>" in head
    assert 'name="author" content="CLI Author"' in head
    assert 'name="isbn" content="978-0-00-000000-0"' in head
    assert 'name="dcterms.created" content="2026-08-08"' in head
    assert 'urn:isbn:978-0-00-000000-0' in head


def test_metadata_falls_back_to_style_guide_frontmatter(tmp_path):
    """With no CLI metadata, title/author come from the style guide."""
    root = make_book(tmp_path / "book-mini")
    document, _, _ = md2pdf.assemble_book_html(root)
    head = document.split("</head>")[0]
    assert "<title>Fixture Book</title>" in head
    assert 'content="Fixture Author"' in head


def test_empty_book_is_rejected(tmp_path):
    """A toc.md that lists no chapters must not produce a document."""
    root = make_book(tmp_path / "book-empty", chapters=0,
                     toc="# Table of Contents\n\n(nothing yet)\n")
    with pytest.raises(md2pdf.BookError) as exc:
        md2pdf.assemble_book_html(root)
    assert "no chapters" in str(exc.value)


def test_missing_toc_is_a_graceful_error(tmp_path):
    """A book root without toc.md raises BookError, not a traceback."""
    root = make_book(tmp_path / "book-no-toc", toc=None)
    with pytest.raises(md2pdf.BookError) as exc:
        md2pdf.assemble_book_html(root)
    assert "toc.md not found" in str(exc.value)


def test_missing_chapter_file_is_a_graceful_error(tmp_path):
    """A toc entry pointing at a nonexistent chapter raises BookError."""
    root = make_book(tmp_path / "book-gap", chapters=2)
    with pytest.raises(md2pdf.BookError) as exc:
        md2pdf.assemble_book_html(root)
    assert "ch-03" in str(exc.value)


def test_missing_style_guide_falls_back_to_defaults(tmp_path):
    """Without style-guide.md the bundled defaults still produce a document."""
    root = make_book(tmp_path / "book-plain", style_guide=None)
    document, entries, meta = md2pdf.assemble_book_html(root)
    assert len(entries) == 3
    assert meta["paper_size"] == md2pdf.DEFAULT_PAPER
    assert meta["fonts"] == md2pdf.DEFAULT_FONTS
    assert "210mm 297mm" in document          # A4 default
    assert "direction: rtl" in document       # DEFAULT_CSS still bundled
    assert "counter(page)" in document
    # No cover_text -> cover falls back to the book directory name.
    assert 'id="cover"' in document


def test_book_without_preface_or_backmatter_still_assembles(tmp_path):
    """Optional front/back matter is genuinely optional."""
    root = make_book(tmp_path / "book-bare", preface=False, backmatter=False)
    document, entries, _ = md2pdf.assemble_book_html(root)
    assert len(entries) == 3
    assert "MARKER-PREFACE" not in document
    assert "MARKER-BACKMATTER" not in document
    assert 'id="cover"' in document and 'id="toc"' in document


def test_html_only_writes_file_and_exits_zero(tmp_path, monkeypatch):
    """--html-only needs no browser and writes the assembled document."""
    root = make_book(tmp_path / "book-mini")
    monkeypatch.setattr(md2pdf, "find_chrome_optional", lambda: None)
    rc = _run_main(monkeypatch, [
        "--book", str(root), "--html-only", "--out", "exports/book.html"])
    assert rc == 0
    out = root / "exports" / "book.html"
    assert out.is_file()
    text = out.read_text(encoding="utf-8")
    assert "counter(page)" in text
    assert "MARKER-CH-03" in text


def test_chrome_absent_exits_three(tmp_path, monkeypatch):
    """Book mode without --html-only and without a browser exits 3."""
    root = make_book(tmp_path / "book-mini")
    monkeypatch.setattr(md2pdf, "find_chrome_optional", lambda: None)
    rc = _run_main(monkeypatch, ["--book", str(root)])
    assert rc == 3


def test_out_path_outside_book_root_is_rejected(tmp_path, monkeypatch):
    """--out pointing outside the book root exits 2 and writes nothing."""
    root = make_book(tmp_path / "book-mini")
    external = tmp_path / "external" / "book.html"
    rc = _run_main(monkeypatch, [
        "--book", str(root), "--html-only", "--out", str(external)])
    assert rc == 2
    assert not external.exists()

    rc = _run_main(monkeypatch, [
        "--book", str(root), "--html-only", "--out", "../escaped.html"])
    assert rc == 2


def test_toc_path_outside_book_root_is_rejected(tmp_path, monkeypatch):
    """--toc traversal is refused with the same guard as --out."""
    root = make_book(tmp_path / "book-mini")
    rc = _run_main(monkeypatch, [
        "--book", str(root), "--html-only", "--toc", "../toc.md"])
    assert rc == 2


def test_pdf_path_invokes_chrome_array_form(tmp_path, monkeypatch):
    """With a browser present, Chrome is invoked array-form (no shell=True)."""
    root = make_book(tmp_path / "book-mini")
    monkeypatch.setattr(md2pdf, "find_chrome_optional", lambda: "/usr/bin/chrome")
    seen = {}

    class FakeResult:
        returncode = 0

    def fake_run(cmd, **kwargs):
        seen["cmd"] = cmd
        seen["kwargs"] = kwargs
        target = [a for a in cmd if a.startswith("--print-to-pdf=")][0]
        Path(target.split("=", 1)[1]).write_bytes(b"%PDF-1.4 fake\n")
        return FakeResult()

    monkeypatch.setattr(md2pdf.subprocess, "run", fake_run)
    rc = _run_main(monkeypatch, ["--book", str(root), "--out", "exports/book.pdf"])
    assert rc == 0
    assert (root / "exports" / "book.pdf").is_file()
    assert isinstance(seen["cmd"], list)
    assert "shell" not in seen["kwargs"]
    assert seen["cmd"][0] == "/usr/bin/chrome"
    assert "--headless=new" in seen["cmd"]
    assert seen["cmd"][-1].startswith("file:")


def test_chrome_nonzero_exit_is_reported(tmp_path, monkeypatch):
    """A failing Chrome run exits 2 rather than claiming success."""
    root = make_book(tmp_path / "book-mini")
    monkeypatch.setattr(md2pdf, "find_chrome_optional", lambda: "/usr/bin/chrome")

    class FakeResult:
        returncode = 1

    monkeypatch.setattr(md2pdf.subprocess, "run", lambda cmd, **kw: FakeResult())
    rc = _run_main(monkeypatch, ["--book", str(root)])
    assert rc == 2


def test_parse_toc_accepts_bare_chapter_refs():
    """A plain list of ch-NN.md names parses in order."""
    entries = md2pdf.parse_toc("- ch-01.md\n- ch-02.md\n")
    assert [e["href"] for e in entries] == ["ch-01.md", "ch-02.md"]


def test_parse_frontmatter_handles_nested_and_block_forms():
    """Nested mapping and block scalar both parse."""
    front = md2pdf.parse_frontmatter(
        "---\nfonts:\n  body: Amiri\n  display: Lateef\n"
        "cover_text: |\n  Line A\n  Line B\npaper_size: A5\n---\nbody\n")
    assert front["fonts"] == {"body": "Amiri", "display": "Lateef"}
    assert front["cover_text"] == "Line A\nLine B"
    assert front["paper_size"] == "A5"
    assert md2pdf.parse_frontmatter("# no frontmatter\n") == {}


def test_build_page_css_passes_through_unknown_paper_size():
    """An unrecognised paper_size is emitted verbatim as a CSS size."""
    css = md2pdf.build_page_css("200mm 300mm", {"body": "X", "display": "Y"})
    assert "size: 200mm 300mm" in css
    assert "counter(page)" in css


def test_help_survives_cp1256_stdio():
    """--help must not crash on a Windows-cp1256 console (ASCII help text)."""
    import os
    env = dict(os.environ)
    env["PYTHONIOENCODING"] = "cp1256"
    r = subprocess.run(
        [sys.executable, str(Path(md2pdf.__file__)), "--help"],
        capture_output=True, text=True, env=env,
    )
    assert r.returncode == 0, r.stderr
    assert "--book" in r.stdout


def _run_main(monkeypatch, argv):
    """Call md2pdf.main(argv) and return the exit code it raised."""
    try:
        md2pdf.main(argv)
    except SystemExit as exc:
        code = exc.code
        return 0 if code is None else int(code)
    return 0
