from pathlib import Path
import argparse
import hashlib
import json
import re
import sys
import unicodedata

FENCE = re.compile(r"```.*?```", re.DOTALL)
CHAPTER = re.compile(r"^ch-\d+\.md$")

def read_md(path):
    """Read a markdown file with encoding fallback. Tries utf-8 → cp1256 → cp1252 → latin-1."""
    try:
        return path.read_text(encoding="utf-8")
    except UnicodeDecodeError:
        for enc in ("cp1256", "cp1252"):
            try:
                return path.read_text(encoding=enc)
            except UnicodeDecodeError:
                continue
        return path.read_text(encoding="latin-1")

def outside(text):
    return FENCE.sub(lambda m: "\n" * m.group(0).count("\n"), text)

def style_data(path):
    text = read_md(path) if path.exists() else ""
    windows, forbidden, frozen = {}, [], []
    m = re.search(r"## Word-count windows(.*?)(?=\n## |\Z)", text, re.S | re.I)
    if m:
        for ch, rng in re.findall(r"\|\s*(ch-\d+)\s*\|\s*(\d+)\s*-\s*(\d+)\s*\|", m.group(1)):
            windows[ch] = (int(rng[0]), int(rng[1]))
    m = re.search(r"## Forbidden patterns(.*?)(?=\n## |\Z)", text, re.S | re.I)
    if m:
        blocks = re.findall(r"```(?:[^\n]*)\n(.*?)```", m.group(1), re.S)
        forbidden = [x.strip() for b in blocks for x in b.splitlines() if x.strip() and not x.lstrip().startswith("#")]
    m = re.search(r"## Frozen lines(.*?)(?=\n## |\Z)", text, re.S | re.I)
    if m:
        frozen = re.findall(r"chapters/(ch-\d+\.md):(\d+)", m.group(1))
    return windows, forbidden, frozen

def policy(path):
    if not path.exists(): return {}
    m = re.search(r"## Per-chapter targets(.*?)(?=\n## |\Z)", read_md(path), re.S | re.I)
    return {ch: (float(t.rstrip('%')) / (100 if '%' in t else 1), float(tol.rstrip('%')) / (100 if '%' in tol else 1)) for ch,t,tol in re.findall(r"\|\s*(ch-\d+)\s*\|\s*([\d.]+%?)\s*\|\s*([\d.]+%?)\s*\|", m.group(1) if m else "")}

def main(argv=None):
    root = Path(argv[0] if argv else ".")
    if root.name == "chapters": root = root.parent
    chapters = root / "chapters"
    windows, forbidden, style_frozen = style_data(root / "style-guide.md")
    targets = policy(root / "tashkeel-policy.md")
    frozen_json = {}
    fp = root / "frozen-lines.json"
    if fp.exists():
        try: frozen_json = json.loads(fp.read_text(encoding="utf-8")).get("chapters", {})
        except (OSError, ValueError) as e: print(f"warning: invalid frozen-lines.json: {e}", file=sys.stderr)
    result, failed = {}, False
    for file in sorted(chapters.glob("ch-*.md")):
        if not CHAPTER.match(file.name): continue
        text = read_md(file)
        clean = outside(text)
        words = len(re.findall(r"\b[\w'\-\u2018\u2019]+\b", clean, re.UNICODE))
        drift, matches = [], []
        for item in frozen_json.get(file.name, {}).get("frozen_lines", []):
            n = int(item.get("line_number", 0)); lines = text.splitlines(); actual = lines[n-1].rstrip() if 0 < n <= len(lines) else ""
            got = hashlib.sha256(actual.encode()).hexdigest(); expected = item.get("sha256", "")
            if got != expected: drift.append({"line_number": n, "expected": expected, "actual": got}); failed = True
        for pattern in forbidden:
            try:
                for match in re.finditer(pattern, clean):
                    line = clean.count("\n", 0, match.start()) + 1; matches.append({"line": line, "match": match.group(0)})
            except re.error as e: print(f"warning: invalid forbidden regex {pattern!r}: {e}", file=sys.stderr)
        if matches: failed = True
        if file.stem in windows and not windows[file.stem][0] <= words <= windows[file.stem][1]: failed = True
        ratio = None
        if file.stem in targets:
            arabic = [c for c in clean if '\u0600' <= c <= '\u06ff' or '\u0750' <= c <= '\u077f' or '\u08a0' <= c <= '\u08ff']
            ratio = sum(unicodedata.category(c) == "Mn" for c in arabic) / len(arabic) if arabic else 0.0
            target, tol = targets[file.stem]
            if abs(ratio - target) > tol: failed = True
        result[file.stem] = {"word_count": words, "frozen_intact": not drift, "frozen_drift": drift, "forbidden_matches": matches, "tashkeel_ratio": ratio}
    print(json.dumps(result, ensure_ascii=False, sort_keys=True))
    print(f"book_check: {'FAIL' if failed else 'PASS'} ({len(result)} chapters)", file=sys.stderr)
    return 1 if failed else 0

if __name__ == "__main__": sys.exit(main(sys.argv[1:]))
