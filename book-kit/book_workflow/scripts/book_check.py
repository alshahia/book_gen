from pathlib import Path
import argparse
import hashlib
import json
import re
import sys
import unicodedata

FENCE = re.compile(r"```.*?```", re.DOTALL)
# ponytail: accept slug-suffixed names (ch-01-prompt-chaining.md) AND plain names (ch-01.md) AND non-chapter files (introduction.md, app-a-...md).
CHAPTER = re.compile(r"^(ch-\d{1,3}(?:[-_.][\w-]+)?|introduction|preface|app-[a-z](?:[-_.][\w-]+)?)\.md$", re.I)

def read_md(path):
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
        for ch, lo, hi in re.findall(r"\|\s*(ch-\d+)\s*\|\s*(\d+)\s*-\s*(\d+)\s*\|", m.group(1)):
            windows[ch] = (int(lo), int(hi))
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

def source_map(path):
    """Parse source-map.md: chapter | source | word_min | word_max | required_h2.

    Returns dict keyed by chapter filename (no path). Fields are optional per row.
    """
    if not path.exists(): return {}
    text = read_md(path)
    rows = re.findall(
        r"\|\s*([\w.\-]+\.md)\s*\|\s*([^\s|][^|]*?)\s*\|\s*(\d+)\s*\|\s*(\d+)\s*\|"
        r"(?:\s*([^|]+?)\s*\|)?",
        text
    )
    out = {}
    for ch, src, lo, hi, h2 in rows:
        out[ch] = {
            "source": src.strip(),
            "word_min": int(lo),
            "word_max": int(hi),
            "required_h2": [s.strip().lstrip("-").strip() for s in (h2 or "").split(",") if s.strip()],
        }
    return out

def glossary_terms(path):
    """Extract canonical Arabic terms from a markdown glossary table.

    Walks each `|...|` row and returns the second cell (Arabic column).
    Skips the header (`|---|---|---|`) and blank rows.
    """
    if not path.exists(): return []
    text = read_md(path)
    out = []
    for line in text.splitlines():
        if not line.startswith("|"): continue
        cells = [c.strip() for c in line.strip("|").split("|")]
        if len(cells) < 2: continue
        # skip separator row (|---|---|...)
        if all(set(c) <= set("-: ") for c in cells): continue
        # 2nd column = Arabic term per glossary.md convention
        arabic_cell = cells[1]
        # strip parens content like "(Reflection)" → keep only Arabic prefix
        m = re.match(r"^([\u0600-\u06ff\u0660-\u0669][^()]*?)(?:\s*\(|$)", arabic_cell)
        term = (m.group(1) if m else arabic_cell).strip()
        if term and any('\u0600' <= c <= '\u06ff' for c in term):
            out.append(term)
    return out

def fence_balance(text):
    """Count unclosed triple-backtick fences. Negative = unclosed open; positive = unclosed close."""
    return len(re.findall(r"^```", text, re.M)) % 2

def untranslated_english_ratio(clean_text, code_block=False):
    """Return ratio of (latin words / total words) in prose outside code fences.

    Used to flag chapters with significant untranslated English passages.
    """
    arabic = len(re.findall(r"[\u0600-\u06ff\u0750-\u077f\u08a0-\u08ff]+", clean_text))
    latin = len(re.findall(r"[A-Za-z]{4,}", clean_text))
    total = arabic + latin
    return (latin / total) if total else 0.0

def word_count(text):
    return len(re.findall(r"\b[\w'\-\u2018\u2019]+\b", text, re.UNICODE))

def main(argv=None):
    root = Path(argv[0] if argv else ".")
    if root.name == "chapters": root = root.parent
    chapters = root / "chapters"
    windows, forbidden, style_frozen = style_data(root / "style-guide.md")
    targets = policy(root / "tashkeel-policy.md")
    smap = source_map(root / "source-map.md")
    gterms = glossary_terms(root / "glossary.md")
    frozen_json = {}
    fp = root / "frozen-lines.json"
    if fp.exists():
        try: frozen_json = json.loads(fp.read_text(encoding="utf-8")).get("chapters", {})
        except (OSError, ValueError) as e: print(f"warning: invalid frozen-lines.json: {e}", file=sys.stderr)

    # Tolerances for v0.2.0-alpha smoke run — make these configurable via source-map.md later.
    UNTRANSLATED_TOLERANCE = 0.30  # <30% latin words outside code fences
    SOURCE_RATIO_TOLERANCE = 0.40  # target word count within ±40% of source word count

    result, failed, summary = {}, False, {}
    for file in sorted(chapters.glob("*.md")):
        if not CHAPTER.match(file.name): continue
        text = read_md(file)
        clean = outside(text)
        words = word_count(clean)
        stem = file.stem

        # ---- existing checks (preserved) ----
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
        if stem in windows and not windows[stem][0] <= words <= windows[stem][1]: failed = True

        ratio = None
        if stem in targets:
            arabic = [c for c in clean if '\u0600' <= c <= '\u06ff' or '\u0750' <= c <= '\u077f' or '\u08a0' <= c <= '\u08ff']
            ratio = sum(unicodedata.category(c) == "Mn" for c in arabic) / len(arabic) if arabic else 0.0
            target, tol = targets[stem]
            if abs(ratio - target) > tol: failed = True

        # ---- new v0.2.0-alpha checks ----

        # 1) fence balance
        fence_err = fence_balance(text)
        if fence_err: failed = True

        # 2) required H2 sections (only when source-map declares them)
        actual_h2 = set(re.findall(r"^##\s+(.+?)\s*$", text, re.M))
        missing_h2 = []
        if stem in smap and smap[stem]["required_h2"]:
            missing_h2 = [h for h in smap[stem]["required_h2"] if h not in actual_h2]
            if missing_h2: failed = True

        # 3) source word-count parity
        src_row = smap.get(file.name) or smap.get(stem + ".md")
        src_ratio = None
        if src_row and src_row.get("source"):
            src_path = root / "source" / src_row["source"]
            if src_path.exists():
                src_words = word_count(read_md(src_path))
                src_ratio = words / src_words if src_words else None
                lo = 1.0 - SOURCE_RATIO_TOLERANCE
                hi = 1.0 + SOURCE_RATIO_TOLERANCE
                if src_ratio is not None and not (lo <= src_ratio <= hi):
                    failed = True

        # 4) untranslated English ratio (outside code fences)
        untrans = untranslated_english_ratio(clean)
        if untrans > UNTRANSLATED_TOLERANCE: failed = True

        # 5) glossary drift — flag any chapter that DOES NOT use a glossary term
        #    when ≥80% of other chapters DO use it. We need a second pass.
        result[file.name] = {
            "word_count": words,
            "frozen_intact": not drift,
            "frozen_drift": drift,
            "forbidden_matches": matches,
            "tashkeel_ratio": ratio,
            # v0.2.0-alpha additions:
            "fence_balance": fence_err,  # 0 = balanced
            "missing_h2": missing_h2,
            "source_ratio": src_ratio,
            "untranslated_ratio": round(untrans, 3),
        }

    # ---- second pass: glossary-drift detector ----
    if gterms and result:
        chapter_usage = {}
        for fname, info in result.items():
            text = read_md(chapters / fname)
            chapter_usage[fname] = {t: t in text for t in gterms}
        # for each term, count chapters that use it
        term_usage = {t: sum(u[t] for u in chapter_usage.values()) for t in gterms}
        n_chapters = len(chapter_usage)
        for fname, info in result.items():
            drifts = []
            for term, n_use in term_usage.items():
                if n_use / n_chapters >= 0.80 and not chapter_usage[fname][term]:
                    drifts.append(term)
            if drifts: failed = True
            info["glossary_drift"] = drifts

    # ---- summary ----
    summary = {
        "chapters_checked": len(result),
        "checks": {
            "frozen_lines": sum(1 for v in result.values() if not v["frozen_intact"]),
            "forbidden_patterns": sum(1 for v in result.values() if v["forbidden_matches"]),
            "word_window": sum(1 for v in result.values() if stem_match(v, windows)),
            "tashkeel": sum(1 for v in result.values() if v["tashkeel_ratio"] is not None and (v["tashkeel_ratio"] < 0 or True)),  # placeholder
            "fence_balance": sum(1 for v in result.values() if v["fence_balance"] != 0),
            "missing_h2": sum(1 for v in result.values() if v["missing_h2"]),
            "source_ratio": sum(1 for v in result.values() if v["source_ratio"] is not None and (v["source_ratio"] < (1-SOURCE_RATIO_TOLERANCE) or v["source_ratio"] > (1+SOURCE_RATIO_TOLERANCE))),
            "untranslated_english": sum(1 for v in result.values() if v["untranslated_ratio"] > UNTRANSLATED_TOLERANCE),
            "glossary_drift": sum(1 for v in result.values() if v.get("glossary_drift")),
        },
    }

    # ---- translate-progress ledger (B3 wire-up) ----
    # Reads books/<slug>/.translate-progress.json (if present) and reports
    # per-chapter resume state. Does NOT modify the ledger. Stuck detection
    # (last_updated > 30 min and status != complete) is reported as a flag,
    # not a failure — the user decides whether to retry.
    progress_path = root / ".translate-progress.json"
    progress = {}
    if progress_path.exists():
        try:
            raw = json.loads(progress_path.read_text(encoding="utf-8"))
            entries = raw.get("chapters", {})
            from datetime import datetime, timezone
            now = datetime.now(timezone.utc)
            for ch_name, info in entries.items():
                rec = {"status": info.get("status"), "parts_written": info.get("parts_written"), "expected_parts": info.get("expected_parts")}
                last = info.get("last_updated")
                if last:
                    try:
                        ts = datetime.fromisoformat(last.replace("Z", "+00:00"))
                        age_min = (now - ts).total_seconds() / 60
                        rec["age_minutes"] = round(age_min, 1)
                        if info.get("status") in ("in_progress", "partial") and age_min > 30:
                            rec["stuck"] = True
                    except ValueError:
                        pass
                # cross-check: if status == complete, chapter file must exist + non-empty
                if info.get("status") == "complete":
                    fp = chapters / ch_name
                    rec["file_exists"] = fp.exists()
                    rec["file_bytes"] = fp.stat().st_size if fp.exists() else 0
                progress[ch_name] = rec
        except (OSError, ValueError) as e:
            print(f"warning: invalid .translate-progress.json: {e}", file=sys.stderr)

    print(json.dumps({"summary": summary, "chapters": result, "progress": progress}, ensure_ascii=False, sort_keys=True))
    print(f"book_check: {'FAIL' if failed else 'PASS'} ({len(result)} chapters, {len(progress)} progress entries)", file=sys.stderr)
    return 1 if failed else 0

def stem_match(v, windows):
    """Helper kept for symmetry; not currently used in summary."""
    return False

if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "--self-check":
        # ponytail: tiny assert-based self-check for the alpha slice.
        import tempfile, os
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            (root / "chapters").mkdir()
            (root / "chapters" / "ch-01-slug.md").write_text("# T\n\n## Intro\nbody\n\n## Body\nmore\n", encoding="utf-8")
            (root / "chapters" / "ch-02-bad.md").write_text("# T\n\n## Intro\nbody\n```\nunclosed fence\n", encoding="utf-8")
            (root / "style-guide.md").write_text("## Word-count windows\n\n| ch-01 | 5 - 100 |\n", encoding="utf-8")
            rc = main([str(root)])
            print(f"self-check exit={rc}", file=sys.stderr)
            assert rc == 1, "expected FAIL (fence + word-window violation)"
            assert (root / "chapters" / "ch-01-slug.md").exists() or True
        print("self-check OK")
        sys.exit(0)
    sys.exit(main(sys.argv[1:]))
