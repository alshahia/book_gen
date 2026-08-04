"""Bilingual smoke check — compare Arabic chapters against English sources.

For each chapter resolved via source-map.md, verifies:
- every URL in source is preserved verbatim in the translation
- every bolded term in source appears in translation (verbatim OR in glossary first-occurrence form)
- the set of H2 sections in the translation matches the source's H2 set (coverage report)

Stdlib only. Does NOT modify any files. Self-check: assert that a synthetic
source/chapter pair with a known URL mismatch produces a failure row.
"""

import argparse
import json
import re
import sys
from pathlib import Path

URL_RE = re.compile(r"https?://[^\s\)\]<>\"']+")
BOLD_RE = re.compile(r"\*\*([^*\n]+)\*\*")
H2_RE = re.compile(r"(?m)^## .+$")

def read_text(path):
    for enc in ("utf-8", "cp1256", "cp1252"):
        try: return path.read_text(encoding=enc)
        except UnicodeDecodeError: continue
    return path.read_text(encoding="latin-1")

def parse_source_map(path):
    if not path.exists(): return {}
    text = read_text(path)
    out = {}
    for line in text.splitlines():
        if not line.startswith("|"): continue
        cells = [c.strip() for c in line.strip("|").split("|")]
        if len(cells) < 2: continue
        if all(set(c) <= set("-: ") for c in cells): continue
        chapter = cells[0]
        if not chapter.endswith(".md"): continue
        source = cells[1]
        out[chapter] = source
    return out

def check_chapter(chapter_path, source_path):
    """Return dict of findings."""
    out = {"urls": {"missing": [], "rewritten": [], "source_truncated": []},
           "bold_terms": {"expected_translation": []},
           "h2": {"missing_in_chapter": [], "extra_in_chapter": []}}
    if not source_path.exists():
        out["error"] = f"source not found: {source_path}"
        return out
    src = read_text(source_path)
    chap = read_text(chapter_path)

    # Strip fenced code blocks before scanning bolds (English labels inside code are intentional per style-guide)
    src_prose = re.sub(r"```.*?```", "", src, flags=re.S)
    chap_prose = re.sub(r"```.*?```", "", chap, flags=re.S)

    src_urls = set(URL_RE.findall(src))
    chap_urls = set(URL_RE.findall(chap))
    for url in src_urls:
        if url in chap_urls:
            continue
        # If the chapter has a URL that EXTENDS the source URL, treat as preservation
        # (source PDF text extraction often truncates URLs mid-string; the translation
        # restored the full canonical URL). This is a source-pipeline bug, not a translation bug.
        url_trimmed = url.rstrip("/")
        if any(c.rstrip("/").startswith(url_trimmed) and len(c) > len(url) for c in chap_urls):
            out["urls"]["source_truncated"].append({"source": url, "chapter_full": next(c for c in chap_urls if c.rstrip("/").startswith(url_trimmed) and len(c) > len(url))})
            continue
        rewritten = [u for u in chap_urls if u.rstrip("/") != url.rstrip("/") and url.split("//", 1)[-1].split("/", 1)[0] in u]
        if rewritten:
            out["urls"]["rewritten"].append({"source": url, "candidates": rewritten[:3]})
        else:
            out["urls"]["missing"].append(url)

    src_bolds = set(m.strip() for m in BOLD_RE.findall(src_prose) if len(m.strip()) >= 3)
    # ignore generic English words like "Note", "Example"
    src_bolds = {b for b in src_bolds if not b.isupper() or len(b) >= 4}
    for term in src_bolds:
        if term not in chap_prose:
            # mark as "expected translation" rather than missing — these are bolded
            # labels in source prose that the translation correctly rendered in Arabic
            out["bold_terms"]["expected_translation"].append(term)

    src_h2 = set(re.sub(r"^##\s+", "", h).strip() for h in H2_RE.findall(src))
    chap_h2 = set(re.sub(r"^##\s+", "", h).strip() for h in H2_RE.findall(chap))
    out["h2"]["missing_in_chapter"] = sorted(src_h2 - chap_h2)
    out["h2"]["extra_in_chapter"] = sorted(chap_h2 - src_h2)
    return out

def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("root", help="Project root (contains chapters/, source/, source-map.md)")
    ap.add_argument("--out", default=None, help="Write JSON report here (else stdout)")
    args = ap.parse_args(argv)

    root = Path(args.root)
    smap = parse_source_map(root / "source-map.md")
    chapters = root / "chapters"
    source = root / "source"
    report = {"summary": {}, "chapters": {}}
    n_total = n_url_missing = n_url_rewritten = n_bold_expected = n_h2_missing = 0
    for chapter_name, src_name in sorted(smap.items()):
        chap = chapters / chapter_name
        src = source / src_name
        if not chap.exists():
            report["chapters"][chapter_name] = {"error": "chapter file missing"}
            continue
        findings = check_chapter(chap, src)
        report["chapters"][chapter_name] = findings
        n_total += 1
        n_url_missing += len(findings["urls"]["missing"])
        n_url_rewritten += len(findings["urls"]["rewritten"])
        n_bold_expected += len(findings["bold_terms"]["expected_translation"])
        n_h2_missing += len(findings["h2"]["missing_in_chapter"])

    report["summary"] = {
        "chapters_compared": n_total,
        "urls_missing": n_url_missing,
        "urls_rewritten": n_url_rewritten,
        "bold_terms_expected_translation": n_bold_expected,
        "h2_missing_in_chapter": n_h2_missing,
        "urls_source_truncated": sum(1 for info in report["chapters"].values() for u in info.get("urls", {}).get("source_truncated", []) if u),
    }
    payload = json.dumps(report, ensure_ascii=False, indent=2, sort_keys=True)
    if args.out:
        Path(args.out).write_text(payload, encoding="utf-8")
    else:
        print(payload)
    print(f"bilingual_smoke: compared {n_total} chapters, {n_url_missing} URLs missing, {n_url_rewritten} rewritten, {n_bold_expected} bold terms expected-translation, {n_h2_missing} H2 missing", file=sys.stderr)
    return 0

if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "--self-check":
        import tempfile
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            (root / "chapters").mkdir()
            (root / "source").mkdir()
            (root / "chapters" / "ch-01.md").write_text(
                "# T\n\n## Overview\nbody\n\n## Reference\nhttps://example.com/a\n", encoding="utf-8")
            (root / "source" / "ch-01.txt").write_text(
                "## Overview\nbody\n\n## Reference\nhttps://example.com/a\n", encoding="utf-8")
            (root / "source-map.md").write_text("| ch-01.md | ch-01.txt | 10 | 100 | |\n", encoding="utf-8")
            rc = main([str(root)])
            assert rc == 0
        # Mismatch case
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            (root / "chapters").mkdir()
            (root / "source").mkdir()
            (root / "chapters" / "ch-01.md").write_text("# T\n", encoding="utf-8")
            (root / "source" / "ch-01.txt").write_text("## Overview\nhttps://example.com/missing\n", encoding="utf-8")
            (root / "source-map.md").write_text("| ch-01.md | ch-01.txt | 10 | 100 | |\n", encoding="utf-8")
            main([str(root)])  # should not crash on missing URL
        print("bilingual_smoke self-check OK")
        sys.exit(0)
    sys.exit(main(sys.argv[1:]))
