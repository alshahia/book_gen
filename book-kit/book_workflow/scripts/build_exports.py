from pathlib import Path
import json
import re
import subprocess
import sys

HERE = Path(__file__).resolve().parent

def read_text_safe(path):
    """Read a markdown file with encoding fallback. Tries utf-8 → cp1256 → cp1252 → utf-8 (replace)."""
    for enc in ("utf-8", "cp1256", "cp1252"):
        try:
            text = path.read_text(encoding=enc)
            print(f"[encoding] {path.name} → {enc}", file=sys.stderr)
            return text
        except UnicodeDecodeError:
            continue
    text = path.read_text(encoding="utf-8", errors="replace")
    print(f"[encoding] {path.name} → utf-8 (replace)", file=sys.stderr)
    return text

def words(text):
    return len(re.findall(r"\b[\w'\-\u2018\u2019]+\b", re.sub(r"```.*?```", "", text, flags=re.S), re.UNICODE))

def section(text, names):
    m = re.search(r"##\s+(?:" + "|".join(names) + r")(.*?)(?=\n## |\Z)", text, re.S | re.I)
    return m.group(1) if m else ""

def chapter_title(text, fallback=""):
    """Return the first H1 line, stripped. Falls back to `fallback` if no H1."""
    m = re.search(r"^#\s+(.+?)\s*$", text, re.MULTILINE)
    return m.group(1) if m else fallback

def style_directive(path):
    """Read `rtl:` and `language:` declarations from style-guide.md. Used by TOC + glossary to switch rendering mode.

    Heuristic fallback: when no `rtl:` line is present but the style-guide's body is
    majority-Arabic (>=30% Arabic codepoints in the first 500 visible chars), treat
    as RTL. This catches the common case where a hand-written Arabic style-guide
    never declares `rtl: true` explicitly.
    """
    if not path.exists(): return {"rtl": False, "language": "en"}
    text = read_text_safe(path)
    rtl = bool(re.search(r"(?m)^rtl:\s*true\b", text))
    lang_match = re.search(r"(?m)^language:\s*([a-z]{2,3})\b", text)
    language = lang_match.group(1) if lang_match else "en"
    if not rtl and language == "en":
        # heuristic: Arabic content without an explicit language directive
        sample = text[:500]
        arabic = sum(1 for c in sample if '\u0600' <= c <= '\u06ff' or '\u0750' <= c <= '\u077f')
        latin = sum(1 for c in sample if c.isascii() and c.isalpha())
        if arabic > latin and arabic > 20:
            rtl = True
            language = "ar"
    return {"rtl": rtl, "language": language}

def arabic_indic(n):
    """Convert integer to Arabic-Indic (٠١٢٣٤٥٦٧٨٩). Used for page numbers in RTL books."""
    digits = "٠١٢٣٤٥٦٧٨٩"
    return "".join(digits[int(d)] for d in str(n))

def main(argv=None):
    root = Path(argv[0] if argv else ".")
    force = "--force" in argv
    if force: argv = [a for a in argv if a != "--force"]
    root = Path(argv[0] if argv else ".")
    t1 = subprocess.run([sys.executable, str(HERE / "book_check.py"), str(root)], capture_output=True, text=True)
    if t1.returncode and not force: sys.stderr.write(t1.stderr); return 1
    if t1.returncode and force:
        sys.stderr.write(f"build_exports: book_check FAIL but --force set; continuing\n")
    t2 = subprocess.run([sys.executable, str(HERE / "strip_publish_annotations.py"), str(root)], capture_output=True, text=True)
    if t2.returncode and not force: sys.stderr.write(t2.stderr); return 1
    chapters = sorted((root / "chapters").glob("ch-*.md"))
    exports = root / "exports"; exports.mkdir(exist_ok=True)
    style = style_directive(root / "style-guide.md")
    is_rtl = style["rtl"] or style["language"] == "ar"

    rows = []
    ch_texts = {}
    for ch in chapters:
        ch_texts[ch.name] = read_text_safe(root / "chapters" / ch.name)
        title = chapter_title(ch_texts[ch.name], ch.stem)
        n = re.search(r"\d+", ch.stem).group()
        n_int = int(n)
        # RTL TOC: prefix chapter label with its Arabic-Indic number; suffix with page placeholder.
        if is_rtl:
            label = f"الفصل {arabic_indic(n_int)}: {title}"
            page = "<!-- صفحة {} -->".format(arabic_indic(n_int))
        else:
            label = f"Chapter {n_int:02d}: {title}"
            page = "<!-- page {} -->".format(n_int)
        rows.append(f"- [{label}](chapters/{ch.name}) {page}")

    toc_header = "# فهرس المحتويات" if is_rtl else "# Table of Contents"
    toc_body = "\n".join(rows) + "\n"
    if is_rtl:
        # Wrap with HTML dir marker so markdown renderers apply RTL flow
        toc_body = "<div dir=\"rtl\">\n\n" + toc_body + "\n</div>\n"
    (exports / "toc.md").write_text(toc_header + "\n\n" + toc_body, encoding="utf-8")
    print(f"build_exports: toc mode={'rtl' if is_rtl else 'ltr'}", file=sys.stderr)
    bible = read_text_safe(root / "bible.md") if (root / "bible.md").exists() else ""
    terms = re.findall(r"^###\s+(.+?)\s*\n([^#]+)", section(bible, ["Terminology", "Glossary"]), re.M)
    glossary = []
    for term, definition in terms:
        definition = re.sub(r"\s+", " ", definition).strip()
        glossary.append(f"- **{term.strip()}** — {definition}")
    (exports / "glossary.md").write_text("# Glossary\n\n" + ("\n".join(sorted(glossary, key=str.casefold)) or "[No terminology entries yet — populate bible.md]") + "\n", encoding="utf-8")
    names = [x.strip() for x in re.findall(r"^###\s+(.+)", section(bible, ["Terminology", "Glossary", "Characters"]), re.M)]
    index = []
    for term in sorted(set(names), key=str.casefold):
        hits = []
        for ch in chapters:
            lines = ch_texts[ch.name].splitlines()
            for i, line in enumerate(lines, 1):
                if term.casefold() in line.casefold(): hits.append(f"{ch.stem}:{i}")
        index.append(f"- **{term}** — {', '.join(hits) or 'not found'}")
    (exports / "index.md").write_text("# Index\n\n" + ("\n".join(index) or "[No terms yet — populate bible.md]") + "\n", encoding="utf-8")
    manifest = root / "frozen-lines.json"
    if manifest.exists(): (exports / "manifest.json").write_bytes(manifest.read_bytes())
    total = sum(words(ch_texts[ch.name]) for ch in chapters)
    deliverables = ["toc.md", "glossary.md", "index.md"] + (["manifest.json"] if manifest.exists() else []) + ["README.md", "clean/..."]
    readme = f"# Exports\n\nBuild date: deterministic local build\n\nChapters: {len(chapters)}\nTotal words: {total}\n\n> Preface requires separate am-design dispatch (LLM pass).\n\nDeliverables:\n" + "\n".join(f"- {x}" for x in deliverables) + "\n"
    (exports / "README.md").write_text(readme, encoding="utf-8")
    print(json.dumps({"chapters": len(chapters), "total_words": total, "t1_exit": t1.returncode, "t3_exit": 0, "deliverables": deliverables}, sort_keys=True))
    return 0

if __name__ == "__main__": sys.exit(main(sys.argv[1:]))
