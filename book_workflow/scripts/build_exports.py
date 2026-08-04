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

def main(argv=None):
    root = Path(argv[0] if argv else ".")
    t1 = subprocess.run([sys.executable, str(HERE / "book_check.py"), str(root)], capture_output=True, text=True)
    if t1.returncode: sys.stderr.write(t1.stderr); return 1
    t2 = subprocess.run([sys.executable, str(HERE / "strip_publish_annotations.py"), str(root)], capture_output=True, text=True)
    if t2.returncode: sys.stderr.write(t2.stderr); return 1
    chapters = sorted((root / "chapters").glob("ch-*.md"))
    exports = root / "exports"; exports.mkdir(exist_ok=True)
    outline = read_text_safe(root / "outline.md") if (root / "outline.md").exists() else ""
    rows = []
    ch_texts = {}
    for ch in chapters:
        ch_texts[ch.name] = read_text_safe(root / "chapters" / ch.name)
        title = chapter_title(ch_texts[ch.name], ch.stem)
        n = re.search(r"\d+", ch.stem).group()
        rows.append(f"- [Chapter {int(n):02d}: {title}](chapters/{ch.name})")
    (exports / "toc.md").write_text("# Table of Contents\n\n" + "\n".join(rows) + "\n", encoding="utf-8")
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
