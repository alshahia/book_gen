"""Convert Arabic Markdown chapters to RTL PDF via HTML + Chrome headless.

Usage:
    py md2pdf.py <md-file> [<md-file> ...] [--out DIR] [--css FILE] [--figures-manifest FILE]

When --figures-manifest is provided, scans each chapter for italic figure placeholders
(`> **الشكل N:** caption`) and prepends an `<img>` from the manifest in order of appearance.
Without the flag, the italic placeholders render as-is (the v0.2.0-alpha default).

Manifest format (produced by `extract_figures.py`):
    {"pdf": "...", "slug": "...", "figures": [{"page": N, "num": N, "path": "figures/X-N-N.png", ...}]}

BOOK MODE (P12):
    py md2pdf.py --book <book-root> [--out REL] [--html-only]
                 [--toc REL] [--style-guide REL]
                 [--title T] [--author A] [--isbn I] [--build-date D]

Reads `<book>/toc.md` for the chapter order and assembles ONE document in
this order: cover -> preface -> auto-linked table of contents -> chapters
(in toc.md order) -> back-matter. Paper size and fonts come from the
`style-guide.md` YAML frontmatter (`paper_size: B5`,
`fonts: {body: Cairo, display: Amiri}`); `cover_text` supplies the cover
lines. Page numbers are emitted through
`@page { @bottom-right { content: counter(page); } }` and suppressed on the
cover via `@page :first`. Book metadata (title, author, isbn, build date)
is written into the `<head>` so Chrome carries it into the PDF.

`--out` is resolved relative to the book root and is refused when it
escapes that root (`..` components or absolute paths elsewhere). When
Chrome/Edge is absent the book build exits 3 (deferred rendering); pass
`--html-only` to stop after the assembled HTML, which needs no browser.

Book-mode exit codes: 0 success, 2 input error, 3 browser missing.

Requires: markdown-it-py (pip), Chrome/Edge installed (not for --html-only).
"""
import argparse
import html as html_lib
import io
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path


def _force_utf8_stdio():
    """Keep argparse help and assembled markup portable on Windows consoles."""
    for stream in (sys.stdout, sys.stderr):
        try:
            stream.reconfigure(encoding="utf-8")
        except (AttributeError, io.UnsupportedOperation):
            pass


_force_utf8_stdio()

try:
    from markdown_it import MarkdownIt
except ImportError:
    print("markdown-it-py is required: py -m pip install markdown-it-py", file=sys.stderr)
    sys.exit(1)

FIGURE_PLACEHOLDER = re.compile(r"^>\s*\*\*الشكل\s+(\d+):\*\*", re.M)

CHROME_CANDIDATES = [
    os.environ.get("CHROME_PATH", ""),
    r"C:\Program Files\Google\Chrome\Application\chrome.exe",
    r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe",
    r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe",
    r"C:\Program Files\Microsoft\Edge\Application\msedge.exe",
]

# PATH names probed by find_chrome_optional() after the explicit paths above.
CHROME_PATH_NAMES = [
    "chrome",
    "chrome.exe",
    "chromium",
    "chromium-browser",
    "google-chrome",
    "google-chrome-stable",
    "msedge",
    "msedge.exe",
]

DEFAULT_CSS = """
@page {
    size: A4;
    margin: 2cm 2.2cm;
}
* { box-sizing: border-box; }
body {
    direction: rtl;
    text-align: right;
    font-family: 'Cairo', 'Sakkal Majalla', 'Segoe UI', Tahoma, Arial, sans-serif;
    font-size: 11.5pt;
    line-height: 1.9;
    color: #1a1a1a;
    margin: 0;
}
h1 {
    font-size: 22pt;
    color: #0b3d66;
    border-bottom: 3px solid #0b3d66;
    padding-bottom: 0.3em;
    margin: 0 0 1.2em 0;
}
h2 {
    font-size: 16pt;
    color: #0b3d66;
    margin: 1.6em 0 0.7em 0;
    padding-right: 0.4em;
    border-right: 4px solid #2f7fb5;
}
h3 { font-size: 13pt; color: #14507e; margin: 1.3em 0 0.5em 0; }
p { margin: 0.7em 0; }
ul, ol { padding-right: 1.6em; padding-left: 0; margin: 0.6em 0; }
li { margin: 0.25em 0; }
strong { color: #0b3d66; }
blockquote {
    border-right: 4px solid #2f7fb5;
    margin: 1em 0;
    padding: 0.6em 1em;
    background: #f0f6fb;
    color: #333;
}
code {
    font-family: 'Cascadia Code', Consolas, 'Courier New', monospace;
    font-size: 9.5pt;
    direction: ltr;
    unicode-bidi: embed;
    background: #f2f2f2;
    padding: 0.1em 0.3em;
    border-radius: 3px;
}
pre {
    direction: ltr;
    text-align: left;
    background: #f7f7f7;
    border: 1px solid #e0e0e0;
    border-radius: 6px;
    padding: 0.9em 1em;
    margin: 1em 0;
    overflow-x: auto;
    white-space: pre-wrap;
    word-wrap: break-word;
}
pre code { background: none; padding: 0; }
a { color: #14507e; text-decoration: none; }
hr { border: none; border-top: 1px solid #ccc; margin: 1.5em 0; }
table { border-collapse: collapse; width: 100%; margin: 1em 0; }
th, td { border: 1px solid #ccc; padding: 0.4em 0.6em; text-align: right; }
th { background: #e8f0f7; }
img { max-width: 100%; height: auto; display: block; margin: 1.2em auto; border: 1px solid #ccc; border-radius: 4px; }
"""


def find_chrome() -> str:
    for candidate in CHROME_CANDIDATES:
        if candidate and Path(candidate).exists():
            return candidate
    raise SystemExit("Chrome/Edge not found. Set CHROME_PATH.")


def find_chrome_optional():
    """Return a Chrome/Edge executable path, or None when none is installed.

    Checks the explicit ``CHROME_CANDIDATES`` install paths first (so
    ``CHROME_PATH`` still wins), then falls back to ``shutil.which`` for the
    common PATH names used on Linux/macOS/Windows.
    """
    for candidate in CHROME_CANDIDATES:
        if candidate and Path(candidate).exists():
            return candidate
    for name in CHROME_PATH_NAMES:
        found = shutil.which(name)
        if found:
            return found
    return None


def md_to_html(md_text: str, title: str, css: str, figures: list = None, chapter_dir: Path = None) -> str:
    md = MarkdownIt("commonmark", {"html": True, "linkify": True}).enable("table")
    if figures:
        md_text = _insert_figures(md_text, figures, chapter_dir)
    body = md.render(md_text)
    return f"""<!DOCTYPE html>
<html lang="ar" dir="rtl">
<head>
<meta charset="utf-8">
<title>{title}</title>
<style>{css}</style>
</head>
<body>
{body}
</body>
</html>"""

def _insert_figures(md_text: str, figures: list, chapter_dir: Path) -> str:
    """Replace each `> **الشكل N:** caption` placeholder with an `<img>` block followed by the original blockquote.

    Sequential — figure index in the chapter (in order of appearance) maps to figures[0], figures[1], ...
    Skipped indices (chapter mentions more figures than the manifest has) keep the original blockquote.
    """
    figure_iter = iter(figures)
    def replace(match):
        try:
            fig = next(figure_iter)
        except StopIteration:
            return match.group(0)
        path = fig["path"]
        # If chapter_dir given, embed as file:// URI (Chrome needs absolute paths or http URIs)
        abs_path = (chapter_dir / path).resolve() if chapter_dir else Path(path).resolve()
        img_uri = abs_path.as_uri()
        return f"![الشكل]({img_uri})\n\n" + match.group(0)
    return FIGURE_PLACEHOLDER.sub(replace, md_text)


# ===========================================================================
# BOOK MODE (P12)
# ===========================================================================

DEFAULT_PAPER = "A4"
DEFAULT_FONTS = {"body": "Cairo", "display": "Cairo"}

# Named paper sizes accepted in style-guide frontmatter. An unrecognised value
# is passed through verbatim so a raw CSS size ("210mm 297mm") still works.
PAPER_SIZES = {
    "A4": "210mm 297mm",
    "A5": "148mm 210mm",
    "A6": "105mm 148mm",
    "B5": "176mm 250mm",
    "B6": "125mm 176mm",
    "LETTER": "8.5in 11in",
    "US-LETTER": "8.5in 11in",
    "LEGAL": "8.5in 14in",
    "CROWN-QUARTO": "189mm 246mm",
    "ROYAL": "156mm 234mm",
}

PREFACE_NAMES = ["preface.html", "preface.md", "front-matter.html", "front-matter.md"]
BACKMATTER_NAMES = ["back-matter.html", "back-matter.md", "backmatter.html", "backmatter.md"]

_FRONTMATTER_RE = re.compile(r"\A\ufeff?---[ \t]*\r?\n(.*?)\r?\n---[ \t]*(?:\r?\n|\Z)", re.S)
_TOC_LINK_RE = re.compile(r"\[([^\]\n]*)\]\(([^)\s]+\.md)\)")
_TOC_BARE_RE = re.compile(r"([A-Za-z0-9_./-]*ch-\d+[A-Za-z0-9_-]*\.md)")
_SLUG_STRIP_RE = re.compile(r"[^a-z0-9]+")


class BookError(Exception):
    """Raised for book-mode input errors that should end the run with exit 2."""


# ---------------------------------------------------------------------------
# Path validation (inherits the P4 #14 / P6 / P11 compensating control)
# ---------------------------------------------------------------------------

def resolve_under(book_root, candidate, label):
    """Resolve ``candidate`` relative to ``book_root``, refusing escapes.

    Rejects any path containing a ``..`` component and any absolute path that
    does not live under ``book_root``. Returns the resolved ``Path``.
    """
    raw = Path(candidate)
    if ".." in raw.parts:
        raise BookError("%s must not contain '..': %s" % (label, candidate))
    target = raw if raw.is_absolute() else (book_root / raw)
    target = target.resolve()
    root = book_root.resolve()
    if target != root and root not in target.parents:
        raise BookError(
            "%s must resolve under the book root %s: %s" % (label, root, candidate)
        )
    return target


# ---------------------------------------------------------------------------
# Minimal YAML frontmatter subset
# ---------------------------------------------------------------------------

def _strip_quotes(value):
    value = value.strip()
    if len(value) >= 2 and value[0] == value[-1] and value[0] in "'\"":
        return value[1:-1]
    return value


def _dedent_block(lines):
    body = [ln for ln in lines]
    indents = [len(ln) - len(ln.lstrip()) for ln in body if ln.strip()]
    pad = min(indents) if indents else 0
    return "\n".join(ln[pad:] if ln.strip() else "" for ln in body).strip("\n")


def _parse_flow_map(value):
    inner = value.strip()[1:-1]
    out = {}
    for part in inner.split(","):
        if ":" not in part:
            continue
        key, _, val = part.partition(":")
        key = _strip_quotes(key)
        if key:
            out[key] = _strip_quotes(val)
    return out


def parse_frontmatter(text):
    """Parse a leading ``---`` YAML block into a dict.

    Supports the subset book-kit style guides actually use: scalar
    ``key: value`` pairs, inline flow mappings (``fonts: {body: X}``), one
    level of indented nested mappings, and ``|`` / ``>`` block scalars.
    Returns ``{}`` when the text has no frontmatter.
    """
    match = _FRONTMATTER_RE.match(text)
    if not match:
        return {}
    lines = match.group(1).splitlines()
    data = {}
    i = 0
    while i < len(lines):
        raw = lines[i]
        i += 1
        if not raw.strip() or raw.lstrip().startswith("#"):
            continue
        if raw[:1] in (" ", "\t"):
            continue
        if ":" not in raw:
            continue
        key, _, val = raw.partition(":")
        key = key.strip()
        val = val.strip()
        if val in ("|", "|-", "|+", ">", ">-", ">+"):
            buf = []
            while i < len(lines) and (not lines[i].strip() or lines[i][:1] in (" ", "\t")):
                buf.append(lines[i])
                i += 1
            data[key] = _dedent_block(buf)
        elif val.startswith("{") and val.endswith("}"):
            data[key] = _parse_flow_map(val)
        elif val == "":
            nested = {}
            while i < len(lines) and lines[i].strip() and lines[i][:1] in (" ", "\t"):
                nkey, _, nval = lines[i].strip().partition(":")
                nkey = nkey.strip()
                if nkey:
                    nested[nkey] = _strip_quotes(nval)
                i += 1
            data[key] = nested if nested else ""
        else:
            data[key] = _strip_quotes(val)
    return data


def load_style_meta(path):
    """Read paper size, fonts, cover text and metadata from a style guide.

    A missing file, or one without frontmatter, yields the defaults so the
    bundled DEFAULT_CSS stays authoritative.
    """
    meta = {
        "paper_size": DEFAULT_PAPER,
        "fonts": dict(DEFAULT_FONTS),
        "cover_text": "",
    }
    if path is None:
        return meta
    p = Path(path)
    if not p.exists() or not p.is_file():
        return meta
    front = parse_frontmatter(p.read_text(encoding="utf-8"))
    paper = front.get("paper_size")
    if isinstance(paper, str) and paper.strip():
        meta["paper_size"] = paper.strip()
    fonts = front.get("fonts")
    if isinstance(fonts, dict):
        for slot in ("body", "display"):
            value = fonts.get(slot)
            if isinstance(value, str) and value.strip():
                meta["fonts"][slot] = value.strip()
    cover = front.get("cover_text")
    if isinstance(cover, str) and cover.strip():
        meta["cover_text"] = cover.strip()
    for key in ("title", "author", "isbn", "build_date", "language", "direction"):
        value = front.get(key)
        if isinstance(value, str) and value.strip():
            meta[key] = value.strip()
    return meta


# ---------------------------------------------------------------------------
# toc.md parsing
# ---------------------------------------------------------------------------

def slug_id(value):
    """ASCII-safe HTML id derived from a chapter file name."""
    stem = Path(str(value)).stem.lower()
    slug = _SLUG_STRIP_RE.sub("-", stem).strip("-")
    return slug or "section"


def parse_toc(text):
    """Return ordered ``[{"title", "href"}]`` entries from a toc.md body.

    Markdown links whose target ends in ``.md`` win. Lines with no link fall
    back to a bare ``ch-NN.md`` token so a plain list still works.
    """
    entries = []
    for line in text.splitlines():
        links = _TOC_LINK_RE.findall(line)
        if links:
            for title, href in links:
                href = href.strip()
                entries.append({
                    "title": title.strip() or Path(href).stem,
                    "href": href,
                })
            continue
        bare = _TOC_BARE_RE.search(line)
        if bare:
            href = bare.group(1)
            title = line.replace(href, "").strip(" \t-*#.|0123456789)")
            entries.append({"title": title or Path(href).stem, "href": href})
    return entries


def resolve_chapter(book_root, href):
    """Locate a toc entry's chapter file inside the book root.

    Prefers the P11 ``chapters-rendered/`` mirror when it exists so rendered
    mermaid figures reach the PDF instead of raw fences.
    """
    name = Path(href).name
    for rel in (
        Path("chapters-rendered") / name,
        Path(href),
        Path("chapters") / name,
        Path(name),
    ):
        candidate = resolve_under(book_root, rel, "chapter path")
        if candidate.is_file():
            return candidate
    raise BookError("chapter listed in toc.md not found: %s" % href)


# ---------------------------------------------------------------------------
# CSS + HTML assembly
# ---------------------------------------------------------------------------

BOOK_CSS = """
@page {
    size: __SIZE__;
    margin: 18mm 16mm 20mm 16mm;
    @bottom-right {
        content: counter(page);
        font-family: '__BODY_FONT__', sans-serif;
        font-size: 9pt;
        color: #555555;
    }
}
@page :first {
    @bottom-right { content: ""; }
}
body {
    font-family: '__BODY_FONT__', 'Cairo', 'Sakkal Majalla', 'Segoe UI', Tahoma, Arial, sans-serif;
}
h1, h2, h3, .cover-line {
    font-family: '__DISPLAY_FONT__', '__BODY_FONT__', 'Cairo', serif;
}
.book-cover {
    text-align: center;
    padding-top: 28%;
    page-break-after: always;
    break-after: page;
}
.book-cover .cover-line {
    font-size: 20pt;
    line-height: 1.7;
    margin: 0.35em 0;
    color: #0b3d66;
}
.book-cover .cover-meta {
    margin-top: 3em;
    font-size: 11pt;
    color: #555555;
}
.book-toc,
.book-preface,
.book-backmatter,
.book-chapter {
    page-break-before: always;
    break-before: page;
}
.book-toc ol { padding-right: 1.4em; }
.book-toc li { margin: 0.45em 0; font-size: 12pt; }
.book-toc a { color: #14507e; text-decoration: none; }
"""


def build_page_css(paper_size, fonts):
    """Render the book CSS bundle for a paper size + font pair."""
    key = str(paper_size or DEFAULT_PAPER).strip()
    size = PAPER_SIZES.get(key.upper(), key) or PAPER_SIZES[DEFAULT_PAPER]
    body = (fonts or {}).get("body") or DEFAULT_FONTS["body"]
    display = (fonts or {}).get("display") or DEFAULT_FONTS["display"]
    return (
        BOOK_CSS
        .replace("__SIZE__", size)
        .replace("__BODY_FONT__", body)
        .replace("__DISPLAY_FONT__", display)
    )


def render_cover(cover_text, metadata):
    """Cover section: one ``.cover-line`` per line of ``cover_text``."""
    lines = [ln.strip() for ln in (cover_text or "").splitlines() if ln.strip()]
    if not lines:
        fallback = metadata.get("title") or "Untitled"
        lines = [fallback]
    parts = ['<section class="book-cover" id="cover">']
    for line in lines:
        parts.append('<div class="cover-line">%s</div>' % html_lib.escape(line))
    tail = []
    if metadata.get("author"):
        tail.append(html_lib.escape(metadata["author"]))
    if metadata.get("build_date"):
        tail.append(html_lib.escape(metadata["build_date"]))
    if metadata.get("isbn"):
        tail.append("ISBN " + html_lib.escape(metadata["isbn"]))
    if tail:
        parts.append('<div class="cover-meta">%s</div>' % "<br>".join(tail))
    parts.append("</section>")
    return "\n".join(parts)


def render_toc(entries, heading="Contents"):
    """Auto-linked table of contents pointing at each chapter section id."""
    parts = ['<nav class="book-toc" id="toc">', "<h1>%s</h1>" % html_lib.escape(heading), "<ol>"]
    for entry in entries:
        parts.append(
            '<li><a href="#%s">%s</a></li>'
            % (entry["id"], html_lib.escape(entry["title"]))
        )
    parts.append("</ol>")
    parts.append("</nav>")
    return "\n".join(parts)


def _render_part(path, md):
    """Render a preface/back-matter file: HTML passes through, markdown converts."""
    text = path.read_text(encoding="utf-8")
    if path.suffix.lower() in (".html", ".htm"):
        return text
    return md.render(text)


def _find_part(book_root, names):
    for name in names:
        candidate = book_root / name
        if candidate.is_file():
            return candidate
    return None


def assemble_book_html(book_root, toc_rel="toc.md", style_rel="style-guide.md",
                       metadata=None, extra_css=""):
    """Assemble the whole book into one HTML document.

    Order: cover -> preface -> auto-linked ToC -> chapters (toc.md order)
    -> back-matter. Raises ``BookError`` on a missing/empty toc.md, a missing
    chapter file, or a path that escapes the book root.
    """
    root = Path(book_root)
    if not root.is_dir():
        raise BookError("book root is not a directory: %s" % book_root)

    toc_path = resolve_under(root, toc_rel, "--toc")
    if not toc_path.is_file():
        raise BookError("toc.md not found: %s" % toc_path)

    entries = parse_toc(toc_path.read_text(encoding="utf-8"))
    if not entries:
        raise BookError(
            "toc.md lists no chapters: %s (an empty book cannot be typeset)" % toc_path
        )

    style_path = resolve_under(root, style_rel, "--style-guide")
    meta = load_style_meta(style_path)

    metadata = dict(metadata or {})
    for key in ("title", "author", "isbn", "build_date"):
        if not metadata.get(key) and meta.get(key):
            metadata[key] = meta[key]

    md = MarkdownIt("commonmark", {"html": True, "linkify": True}).enable("table")

    seen = {}
    for entry in entries:
        base = slug_id(entry["href"])
        seen[base] = seen.get(base, 0) + 1
        entry["id"] = base if seen[base] == 1 else "%s-%d" % (base, seen[base])
        entry["path"] = resolve_chapter(root, entry["href"])

    body_parts = [render_cover(meta.get("cover_text", ""), metadata)]

    preface = _find_part(root, PREFACE_NAMES)
    if preface is not None:
        body_parts.append(
            '<section class="book-preface" id="preface">\n%s\n</section>'
            % _render_part(preface, md)
        )

    body_parts.append(render_toc(entries))

    for entry in entries:
        chapter_html = md.render(entry["path"].read_text(encoding="utf-8"))
        body_parts.append(
            '<section class="book-chapter" id="%s">\n%s\n</section>'
            % (entry["id"], chapter_html)
        )

    backmatter = _find_part(root, BACKMATTER_NAMES)
    if backmatter is not None:
        body_parts.append(
            '<section class="book-backmatter" id="back-matter">\n%s\n</section>'
            % _render_part(backmatter, md)
        )

    css = DEFAULT_CSS + "\n" + build_page_css(meta["paper_size"], meta["fonts"])
    if extra_css:
        css = css + "\n" + extra_css

    title = metadata.get("title") or root.name
    lang = meta.get("language", "ar")
    direction = meta.get("direction", "rtl")

    head = [
        '<meta charset="utf-8">',
        "<title>%s</title>" % html_lib.escape(title),
        '<meta name="generator" content="book-kit md2pdf --book">',
    ]
    if metadata.get("author"):
        head.append('<meta name="author" content="%s">' % html_lib.escape(metadata["author"]))
    if metadata.get("isbn"):
        head.append('<meta name="isbn" content="%s">' % html_lib.escape(metadata["isbn"]))
        head.append(
            '<meta name="identifier" content="urn:isbn:%s">'
            % html_lib.escape(metadata["isbn"])
        )
    if metadata.get("build_date"):
        head.append(
            '<meta name="dcterms.created" content="%s">'
            % html_lib.escape(metadata["build_date"])
        )
    head.append('<meta name="paper-size" content="%s">' % html_lib.escape(meta["paper_size"]))
    head.append("<style>%s</style>" % css)

    document = """<!DOCTYPE html>
<html lang="%s" dir="%s">
<head>
%s
</head>
<body>
%s
</body>
</html>""" % (
        html_lib.escape(lang),
        html_lib.escape(direction),
        "\n".join(head),
        "\n\n".join(body_parts),
    )
    return document, entries, meta


def chrome_pdf_command(chrome, html_path, pdf_path):
    """Array-form Chrome headless command for the book PDF (never shell=True)."""
    return [
        chrome,
        "--headless=new",
        "--disable-gpu",
        "--no-sandbox",
        "--no-pdf-header-footer",
        "--print-to-pdf=%s" % pdf_path,
        Path(html_path).as_uri(),
    ]


def build_book(args):
    """Book-mode entrypoint. Returns a process exit code."""
    root = Path(args.book)
    try:
        extra_css = Path(args.css).read_text(encoding="utf-8") if args.css else ""
        metadata = {
            "title": args.title,
            "author": args.author,
            "isbn": args.isbn,
            "build_date": args.build_date,
        }
        document, entries, meta = assemble_book_html(
            root,
            toc_rel=args.toc,
            style_rel=args.style_guide,
            metadata={k: v for k, v in metadata.items() if v},
            extra_css=extra_css,
        )
        default_out = "exports/book.html" if args.html_only else "exports/book.pdf"
        out_path = resolve_under(root, args.out or default_out, "--out")
    except BookError as exc:
        print("FAIL: %s" % exc, file=sys.stderr)
        return 2
    except OSError as exc:
        print("FAIL: %s" % exc, file=sys.stderr)
        return 2

    out_path.parent.mkdir(parents=True, exist_ok=True)

    if args.html_only:
        out_path.write_text(document, encoding="utf-8")
        print("OK: %s (%d chapters, %s, %d bytes)" % (
            out_path, len(entries), meta["paper_size"], out_path.stat().st_size))
        return 0

    chrome = find_chrome_optional()
    if chrome is None:
        print(
            "DEFERRED: Chrome/Chromium/Edge not found; cannot render the book PDF.\n"
            "  Install Chrome (or set CHROME_PATH), or re-run with --html-only "
            "to emit the assembled HTML instead.",
            file=sys.stderr,
        )
        return 3

    with tempfile.TemporaryDirectory() as tmp:
        html_path = Path(tmp) / "book.html"
        html_path.write_text(document, encoding="utf-8")
        result = subprocess.run(
            chrome_pdf_command(chrome, html_path, out_path),
            capture_output=True,
        )
        if result.returncode != 0 or not out_path.exists():
            print("FAIL: Chrome exited %d building %s" % (result.returncode, out_path),
                  file=sys.stderr)
            return 2
        print("OK: %s (%d chapters, %s, %d bytes)" % (
            out_path, len(entries), meta["paper_size"], out_path.stat().st_size))
        if args.keep_html:
            kept = out_path.parent / "book.html"
            kept.write_text(document, encoding="utf-8")
            print("    HTML kept: %s" % kept)
    return 0


def main(argv=None) -> None:
    parser = argparse.ArgumentParser(description="Arabic Markdown -> RTL PDF")
    parser.add_argument("files", nargs="*", help="Markdown chapter files (single-file mode)")
    parser.add_argument("--out", default=None, help="Output directory (single-file mode) or output file relative to the book root (--book mode)")
    parser.add_argument("--css", default=None, help="Extra CSS file")
    parser.add_argument("--keep-html", action="store_true", help="Keep intermediate HTML")
    parser.add_argument("--figures-manifest", default=None, help="Path to figures manifest.json (from extract_figures.py)")
    book = parser.add_argument_group("book mode")
    book.add_argument("--book", default=None, help="Book root directory; assemble cover + preface + ToC + chapters + back-matter into one document")
    book.add_argument("--toc", default="toc.md", help="Table-of-contents file, relative to the book root (default: toc.md)")
    book.add_argument("--style-guide", default="style-guide.md", help="Style guide supplying paper_size / fonts / cover_text frontmatter, relative to the book root (default: style-guide.md)")
    book.add_argument("--html-only", action="store_true", help="Book mode: write the assembled HTML and skip the Chrome PDF step (needs no browser)")
    book.add_argument("--title", default=None, help="Book title metadata")
    book.add_argument("--author", default=None, help="Book author metadata")
    book.add_argument("--isbn", default=None, help="Book ISBN metadata")
    book.add_argument("--build-date", default=None, help="Build date metadata (free-form, e.g. 2026-08-08)")
    args = parser.parse_args(argv)

    if args.book:
        raise SystemExit(build_book(args))

    if not args.files:
        parser.error("give one or more markdown files, or use --book <book-root>")

    chrome = find_chrome()
    extra_css = Path(args.css).read_text(encoding="utf-8") if args.css else ""
    css = DEFAULT_CSS + "\n" + extra_css
    out_dir = Path(args.out or "exports/pdf")
    out_dir.mkdir(parents=True, exist_ok=True)

    figures = []
    if args.figures_manifest:
        mp = Path(args.figures_manifest)
        if mp.exists():
            manifest = json.loads(mp.read_text(encoding="utf-8"))
            figures = manifest.get("figures", [])
            print(f"figures manifest: {len(figures)} figures from {mp.name}", file=sys.stderr)
        else:
            print(f"warning: figures manifest not found: {mp}", file=sys.stderr)

    for f in args.files:
        md_path = Path(f)
        if not md_path.exists():
            print(f"SKIP (missing): {md_path}", file=sys.stderr)
            continue
        text = md_path.read_text(encoding="utf-8")
        first_line = text.splitlines()[0].lstrip("# ").strip() if text.strip() else md_path.stem
        title = first_line or md_path.stem
        html = md_to_html(text, title, css, figures=figures, chapter_dir=md_path.parent)

        with tempfile.TemporaryDirectory() as tmp:
            html_path = Path(tmp) / f"{md_path.stem}.html"
            html_path.write_text(html, encoding="utf-8")
            pdf_path = out_dir / f"{md_path.stem}.pdf"
            subprocess.run(
                [
                    chrome,
                    "--headless=new",
                    "--disable-gpu",
                    "--no-sandbox",
                    "--no-pdf-header-footer",
                    f"--print-to-pdf={pdf_path}",
                    html_path.as_uri(),
                ],
                check=True,
                capture_output=True,
            )
            print(f"OK: {pdf_path} ({pdf_path.stat().st_size} bytes)")
            if args.keep_html:
                keep_dir = out_dir / "html"
                keep_dir.mkdir(parents=True, exist_ok=True)
                (keep_dir / html_path.name).write_text(html, encoding="utf-8")
                print(f"    HTML kept: {keep_dir / html_path.name}")


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "--self-check":
        # Ponytail: assert that _insert_figures wires the markdown correctly.
        sample = "# T\n\nintro paragraph.\n\n> **الشكل 1:** caption A\n\n> **الشكل 2:** caption B\n\nending.\n"
        figs = [{"path": "figures/x-9-0.png"}, {"path": "figures/x-12-1.png"}]
        out = _insert_figures(sample, figs, Path("."))
        assert "figures/x-9-0.png" in out, "first figure not embedded"
        assert "figures/x-12-1.png" in out, "second figure not embedded"
        assert "> **الشكل 1:**" in out, "original blockquote 1 lost"
        assert "> **الشكل 2:**" in out, "original blockquote 2 lost"
        # extra placeholders beyond manifest are preserved verbatim
        extra = _insert_figures("# T\n\n> **الشكل 1:** a\n\n> **الشكل 2:** b\n\n> **الشكل 3:** c\n", [{"path": "f.png"}], Path("."))
        assert "f.png" in extra, f"figure not embedded; got: {extra!r}"
        # only the first placeholder should have been replaced; the rest stay verbatim
        assert extra.count("![") == 1, f"expected exactly 1 img inserted; got {extra.count('![')}"
        assert extra.count("**الشكل 3:**") == 1, "third placeholder must remain"
        print("md2pdf self-check OK")
        sys.exit(0)
    main()
