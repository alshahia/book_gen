"""Convert Arabic Markdown chapters to RTL PDF via HTML + Chrome headless.

Usage:
    py md2pdf.py <md-file> [<md-file> ...] [--out DIR] [--css FILE] [--figures-manifest FILE]

When --figures-manifest is provided, scans each chapter for italic figure placeholders
(`> **الشكل N:** caption`) and prepends an `<img>` from the manifest in order of appearance.
Without the flag, the italic placeholders render as-is (the v0.2.0-alpha default).

Manifest format (produced by `extract_figures.py`):
    {"pdf": "...", "slug": "...", "figures": [{"page": N, "num": N, "path": "figures/X-N-N.png", ...}]}

Requires: markdown-it-py (pip), Chrome/Edge installed.
"""
import argparse
import json
import os
import re
import subprocess
import sys
import tempfile
from pathlib import Path

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


def main() -> None:
    parser = argparse.ArgumentParser(description="Arabic Markdown -> RTL PDF")
    parser.add_argument("files", nargs="+", help="Markdown chapter files")
    parser.add_argument("--out", default="exports/pdf", help="Output directory")
    parser.add_argument("--css", default=None, help="Extra CSS file")
    parser.add_argument("--keep-html", action="store_true", help="Keep intermediate HTML")
    parser.add_argument("--figures-manifest", default=None, help="Path to figures manifest.json (from extract_figures.py)")
    args = parser.parse_args()

    chrome = find_chrome()
    extra_css = Path(args.css).read_text(encoding="utf-8") if args.css else ""
    css = DEFAULT_CSS + "\n" + extra_css
    out_dir = Path(args.out)
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
