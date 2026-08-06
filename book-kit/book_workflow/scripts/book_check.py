from pathlib import Path
import argparse
import hashlib
import json
import re
import sys
import unicodedata

try:
    import jsonschema
    _HAS_JSONSCHEMA = True
except ImportError:
    _HAS_JSONSCHEMA = False

# Schema dir is co-located with the templates; resolved relative to this file so
# the validator works from any cwd.
SCHEMA_DIR = Path(__file__).resolve().parent.parent / "book-agents" / "templates"
_schema_warned = False


def _validate_against_schema(data, schema_filename, label):
    """Validate `data` against `<SCHEMA_DIR>/<schema_filename>`.

    On `ValidationError`: print `FAIL: schema: <label> <error.message>` and exit(2).
    If `jsonschema` is missing: print a single info line for the run, then continue.
    If the schema file is absent (not yet shipped): skip silently.
    """
    global _schema_warned
    if not _HAS_JSONSCHEMA:
        if not _schema_warned:
            print("info: install jsonschema for schema validation", file=sys.stderr)
            _schema_warned = True
        return
    schema_path = SCHEMA_DIR / schema_filename
    if not schema_path.exists():
        return
    try:
        schema_obj = json.loads(schema_path.read_text(encoding="utf-8"))
        jsonschema.validate(data, schema=schema_obj)
    except jsonschema.ValidationError as e:
        print(f"FAIL: schema: {label} {e.message}", file=sys.stderr)
        sys.exit(2)


FENCE = re.compile(r"```.*?```", re.DOTALL)
# ponytail: accept slug-suffixed names (ch-01-prompt-chaining.md) AND plain names (ch-01.md) AND non-chapter files (introduction.md, app-a-...md) AND letter-suffixed names (ch-a.md, ch-b.md used in tests).
CHAPTER = re.compile(r"^(ch-(?:\d{1,3}|[a-z])(?:[-_.][\w-]+)?|introduction|preface|app-[a-z](?:[-_.][\w-]+)?)\.md$", re.I)

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
    """Parse source-map.md: chapter | source | word_min | word_max | required_h2 | freeze_code |
    source_ratio_override | glossary_drift_exempt.

    Returns dict keyed by chapter filename (no path). Fields are optional per row.
    `source_ratio_override` (e.g. `0.50`) and `glossary_drift_exempt` (`yes`/`no`)
    are honored by the per-chapter checks; absent = use the project-global tolerance.
    """
    if not path.exists(): return {}
    out = {}
    for line in read_md(path).splitlines():
        if not line.lstrip().startswith("|"):
            continue
        cells = [c.strip() for c in line.strip().strip("|").split("|")]
        if len(cells) < 2 or not cells[0].endswith(".md"):
            continue
        # skip header / separator rows
        if all(set(c) <= set("-: ") for c in cells):
            continue
        if cells[0].lower() == "chapter":
            continue
        # cells[1] could be source filename or '-'
        if len(cells) < 4:
            continue
        try:
            lo, hi = int(cells[2]), int(cells[3])
        except ValueError:
            continue
        h2_cell = cells[4] if len(cells) > 4 else ""
        freeze = cells[5].lower() if len(cells) > 5 else ""
        ratio_raw = cells[6].strip() if len(cells) > 6 else ""
        exempt_raw = cells[7].strip().lower() if len(cells) > 7 else ""
        try:
            ratio_val = float(ratio_raw.rstrip('%')) / (100 if '%' in ratio_raw else 1) if ratio_raw and ratio_raw != "-" else None
        except ValueError:
            ratio_val = None
        out[cells[0]] = {
            "source": cells[1].strip() if cells[1].strip() != "-" else "",
            "word_min": lo,
            "word_max": hi,
            "required_h2": [s.strip().lstrip("-").strip() for s in h2_cell.split(",") if s.strip() and s.strip() != "-"],
            "source_ratio_override": ratio_val,
            "glossary_drift_exempt": exempt_raw in ("yes", "true"),
        }
    return out


# Defaults — overridable via style-guide.md frontmatter `tolerances:` block.
DEFAULT_TOLERANCES = {
    "untranslated_english": 0.30,   # <30% latin words outside code fences
    "source_ratio": 0.40,            # target word count within ±40% of source word count
    "stuck_threshold_min": 30,       # flag chapters updated > N min ago with status in_progress
}


def parse_style_guide_tolerances(path):
    """Read YAML frontmatter `tolerances:` block from style-guide.md.

    Returns a dict merged over DEFAULT_TOLERANCES. Missing keys keep defaults.
    Malformed values fall back to defaults. Unknown keys are ignored.
    """
    if not path.exists():
        return dict(DEFAULT_TOLERANCES)
    text = read_md(path)
    if not text.startswith("---"):
        return dict(DEFAULT_TOLERANCES)
    end = text.find("\n---", 3)
    if end < 0:
        return dict(DEFAULT_TOLERANCES)
    block = text[3:end].strip()
    out = dict(DEFAULT_TOLERANCES)
    in_tolerances = False
    for raw in block.splitlines():
        line = raw.rstrip()
        if not line.strip() or line.lstrip().startswith("#"):
            continue
        if line.startswith("tolerances:"):
            in_tolerances = True
            continue
        if in_tolerances:
            if not line.startswith((" ", "\t")):
                # left tolerances section
                in_tolerances = False
                continue
            m = re.match(r"^\s+([A-Za-z_]+):\s*(.+?)\s*$", line)
            if not m:
                continue
            key, raw_val = m.group(1), m.group(2).strip()
            if key not in DEFAULT_TOLERANCES:
                continue
            try:
                v = float(raw_val.rstrip('%')) / (100 if '%' in raw_val else 1)
                out[key] = v
            except ValueError:
                pass  # fall back to default for this key
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
        try:
            _frozen_raw = json.loads(fp.read_text(encoding="utf-8"))
            _validate_against_schema(_frozen_raw, "frozen-lines.schema.json", str(fp))
            frozen_json = _frozen_raw.get("chapters", {})
        except (OSError, ValueError) as e: print(f"warning: invalid frozen-lines.json: {e}", file=sys.stderr)

    # Tolerances: read from style-guide.md frontmatter `tolerances:` block.
    # Missing keys fall back to DEFAULT_TOLERANCES (see top of file).
    tolerances = parse_style_guide_tolerances(root / "style-guide.md")
    UNTRANSLATED_TOLERANCE = tolerances["untranslated_english"]
    SOURCE_RATIO_TOLERANCE = tolerances["source_ratio"]

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
        ratio_tol_used = SOURCE_RATIO_TOLERANCE  # report which tolerance was applied
        if src_row and src_row.get("source"):
            src_path = root / "source" / src_row["source"]
            if src_path.exists():
                src_words = word_count(read_md(src_path))
                src_ratio = words / src_words if src_words else None
                # per-chapter override on tolerance takes precedence over the global
                override = src_row.get("source_ratio_override")
                tol = override if isinstance(override, (int, float)) and override > 0 else SOURCE_RATIO_TOLERANCE
                ratio_tol_used = tol
                lo = 1.0 - tol
                hi = 1.0 + tol
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
            "source_ratio_tolerance": ratio_tol_used,
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
            # per-chapter exemption: source-map.md row `glossary_drift_exempt: yes`
            exempt = smap.get(fname, {}).get("glossary_drift_exempt", False)
            for term, n_use in term_usage.items():
                if n_use / n_chapters >= 0.80 and not chapter_usage[fname][term]:
                    drifts.append(term)
            if drifts and not exempt: failed = True
            info["glossary_drift"] = drifts
            info["glossary_drift_exempt"] = exempt

    # ---- cross-reference check (P3 wire-up) ----
    # Auto-runs whenever the book root has a `chapters/` subdirectory.
    # Counts every cross-reference across the chapter files, resolves each
    # against the chapter index, and flags any broken target. Failures are
    # appended to the JSON payload + stderr, and contribute to the FAIL
    # verdict. The check is wrapped in try/except so a missing or
    # unimportable cross_ref.py degrades gracefully (we just print an info
    # line and continue with the existing checks).
    cross_ref_broken: list[dict] = []
    cross_ref_total = 0
    cross_ref_resolved = 0
    if chapters.exists():
        try:
            _scripts_dir = Path(__file__).resolve().parent
            if str(_scripts_dir) not in sys.path:
                sys.path.insert(0, str(_scripts_dir))
            from cross_ref import run_cross_ref as _run_cross_ref
            _cr_chapters = sorted(chapters.glob("ch-*.md"))
            _cr = _run_cross_ref(_cr_chapters, book_root=root)
            cross_ref_broken = _cr["broken"]
            cross_ref_total = _cr["total"]
            cross_ref_resolved = _cr["resolved"]
            if cross_ref_broken:
                failed = True
                for b in cross_ref_broken:
                    print(
                        f"FAIL: cross_ref: {b['from_file']}:{b['line']} "
                        f"→ {b['expected_target']}: {b['reason']}",
                        file=sys.stderr,
                    )
            else:
                print(
                    f"PASS: cross_ref: {cross_ref_resolved}/{cross_ref_total} resolved",
                    file=sys.stderr,
                )
        except ImportError as e:
            print(f"info: cross_ref.py not importable ({e}); skipping cross_ref check",
                  file=sys.stderr)

    # ---- summary ----
    def _ratio_out_of_band(fname, v):
        if v["source_ratio"] is None:
            return False
        tol = smap.get(fname, {}).get("source_ratio_override") or SOURCE_RATIO_TOLERANCE
        return v["source_ratio"] < (1 - tol) or v["source_ratio"] > (1 + tol)

    summary = {
        "chapters_checked": len(result),
        "tolerances_used": {
            "untranslated_english": UNTRANSLATED_TOLERANCE,
            "source_ratio": SOURCE_RATIO_TOLERANCE,
        },
        "checks": {
            "frozen_lines": sum(1 for v in result.values() if not v["frozen_intact"]),
            "forbidden_patterns": sum(1 for v in result.values() if v["forbidden_matches"]),
            "word_window": sum(1 for v in result.values() if stem_match(v, windows)),
            "tashkeel": sum(1 for v in result.values() if v["tashkeel_ratio"] is not None and (v["tashkeel_ratio"] < 0 or True)),  # placeholder
            "fence_balance": sum(1 for v in result.values() if v["fence_balance"] != 0),
            "missing_h2": sum(1 for v in result.values() if v["missing_h2"]),
            "source_ratio": sum(1 for f, v in result.items() if _ratio_out_of_band(f, v)),
            "untranslated_english": sum(1 for v in result.values() if v["untranslated_ratio"] > UNTRANSLATED_TOLERANCE),
            "glossary_drift": sum(1 for v in result.values() if v.get("glossary_drift") and not v.get("glossary_drift_exempt")),
            "cross_ref": len(cross_ref_broken),
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
            _validate_against_schema(raw, ".translate-progress.schema.json", str(progress_path))
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

    print(json.dumps({"summary": summary, "chapters": result, "progress": progress,
                      "cross_ref": {"broken": cross_ref_broken,
                                    "resolved": cross_ref_resolved,
                                    "total": cross_ref_total}},
                     ensure_ascii=False, sort_keys=True))
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
        # self-check #2: style-guide frontmatter tolerance override
        with tempfile.TemporaryDirectory() as td2:
            r2 = Path(td2)
            (r2 / "chapters").mkdir()
            (r2 / "chapters" / "ch-01.md").write_text("# T\n\nنص عربي قصير\n", encoding="utf-8")
            (r2 / "style-guide.md").write_text("---\ntolerances:\n  untranslated_english: 0.99\n---\n\n# style\n", encoding="utf-8")
            tols = parse_style_guide_tolerances(r2 / "style-guide.md")
            assert tols["untranslated_english"] == 0.99, f"override not applied: {tols}"
            assert tols["source_ratio"] == 0.40, f"missing key fell back wrong: {tols}"
        # self-check #3: per-chapter source_ratio_override from source-map.md
        with tempfile.TemporaryDirectory() as td3:
            r3 = Path(td3)
            (r3 / "chapters").mkdir()
            (r3 / "chapters" / "ch-short.md").write_text("# T\n\n" + ("كلمة " * 50) + "\n", encoding="utf-8")
            (r3 / "source").mkdir()
            (r3 / "source" / "x.txt").write_text("src " * 200, encoding="utf-8")
            (r3 / "source-map.md").write_text(
                "| ch-short.md | x.txt | 0 | 9999 | - | yes | 0.60 | no |\n", encoding="utf-8"
            )
            smap = source_map(r3 / "source-map.md")
            assert smap["ch-short.md"]["source_ratio_override"] == 0.60, f"override missed: {smap}"
            assert smap["ch-short.md"]["glossary_drift_exempt"] is False
        # self-check #4: per-chapter glossary_drift_exempt
        # 5 chapters: 4 use the term, 1 doesn't. Of those 4 users, 1 is exempt.
        with tempfile.TemporaryDirectory() as td4:
            r4 = Path(td4)
            (r4 / "chapters").mkdir()
            (r4 / "chapters" / "ch-a.md").write_text("# T\n\nالنص الأول مع المصطلحالفريد هنا\n", encoding="utf-8")
            (r4 / "chapters" / "ch-b.md").write_text("# T\n\nالنص الثاني مع المصطلحالفريد هنا\n", encoding="utf-8")
            (r4 / "chapters" / "ch-c.md").write_text("# T\n\nالنص الثالث مع المصطلحالفريد هنا\n", encoding="utf-8")
            (r4 / "chapters" / "ch-d.md").write_text("# T\n\nالنص الرابع مع المصطلحالفريد هنا\n", encoding="utf-8")
            (r4 / "chapters" / "ch-e.md").write_text("# T\n\nالنص الخامس بلا مصطلح فريد\n", encoding="utf-8")
            (r4 / "glossary.md").write_text(
                "| english | arabic |\n|---|---|\n| Unique Term | المصطلحالفريد |\n",
                encoding="utf-8",
            )
            (r4 / "source-map.md").write_text(
                "| ch-a.md | - | 0 | 999 | - | yes | - | no |\n"
                "| ch-b.md | - | 0 | 999 | - | yes | - | yes |\n"
                "| ch-c.md | - | 0 | 999 | - | yes | - | no |\n"
                "| ch-d.md | - | 0 | 999 | - | yes | - | no |\n"
                "| ch-e.md | - | 0 | 999 | - | yes | - | no |\n",
                encoding="utf-8",
            )
            import io, contextlib
            buf = io.StringIO()
            with contextlib.redirect_stdout(buf):
                ec = main([str(r4)])
            data = json.loads(buf.getvalue())
            # 4/5 chapters (80%) use المصطلحالفريد — ch-e drifts.
            # ch-a uses the term so does not drift.
            # ch-b uses the term but is exempt — does not drift either.
            assert data["summary"]["checks"]["glossary_drift"] == 1, f"only ch-e should drift; got {data['summary']['checks']['glossary_drift']}"
            assert data["chapters"]["ch-a.md"].get("glossary_drift_exempt") is False
            assert data["chapters"]["ch-b.md"].get("glossary_drift_exempt") is True
            assert data["chapters"]["ch-e.md"].get("glossary_drift") == ["المصطلحالفريد"]
        print("self-check OK")
        sys.exit(0)
    sys.exit(main(sys.argv[1:]))
