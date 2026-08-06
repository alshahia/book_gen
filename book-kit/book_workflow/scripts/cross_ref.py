"""cross_ref.py — cross-reference resolver for book-kit.

Scans chapter files for cross-reference patterns (English + Arabic) and
verifies each reference resolves to an existing file and/or anchor.

CLI:
    cross_ref.py <files...> [--json] [--report-dir <path>] [--task <task-id>]
    cross_ref.py --book <books/<slug>/>

Patterns scanned:
  English:
    - ``[ch-0X]``       (square-bracket form, e.g. ``[ch-03]``)
    - ``(ch-NN.md#anchor)``  (explicit anchor)
    - ``(ch-NN)``       (parenthetical form)
    - ``chapter N`` / ``ch. N`` / ``Ch. N``  (free-text chapter)
    - ``the Foo section`` / ``the Foo chapter``  (intra-chapter section)
  Arabic:
    - ``الفصل ٠٣`` / ``الفصل 03``  (explicit "chapter N")
    - ``الفصل التاسع``  (ordinal word → chapter number)
    - ``في الفصل N``   ("in chapter N")
    - ``الفصل السابق``  (previous chapter)
    - ``الفصل التالي``  (next chapter)

Resolution:
  - ``ch-NN``          → file ``chapters/ch-NN.md`` exists
  - ``#anchor``        → slugified H2/H3 anchor in target file
  - ``chapter N`` / ``الفصل N``  → H2 in target containing "Chapter N" /
                         "الفصل N" (Arabic-aware substring match)
  - ``الفصل السابق``   → ``chapter_num - 1`` (file must exist)
  - ``الفصل التالي``   → ``chapter_num + 1`` (file must exist)
  - Arabic-Indic digits (٠-٩) → ASCII (0-9) BEFORE lookup
  - ``the Foo section`` → scan target chapter H2/H3 headings
                         case-insensitive for any containing word ``Foo``;
                         first match wins; none → BROKEN.

Output:
  --json: emit JSON to stdout, exit 0/1.
  default: write ``<report-dir>/<task-id>/cross_ref.md`` (or
           ``<report-dir>/cross_ref.md`` when no task-id) with rows:

    ## Broken: ch-03.md line 142 → ch-05.md#causes: no such anchor
    ## Broken: ch-07.md line 88 → الفصل التاسع: no such file
    ## Resolved: 16/18 references

Stdlib-only. No new dependencies.
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from dataclasses import dataclass
from pathlib import Path


# ---------------------------------------------------------------------------
# Constants — Arabic ordinal mapping + slug helper
# ---------------------------------------------------------------------------

# Arabic-Indic digits ٠-٩ → ASCII 0-9 (single translation table)
_ARABIC_DIGITS = str.maketrans("٠١٢٣٤٥٦٧٨٩", "0123456789")

# Arabic ordinal words → chapter number. Extensible beyond 10 if needed
# (the spec only mentions الأول-الخامس explicitly but the table is canonical
# Arabic ordinal morphology for the first ten).
ARABIC_ORDINALS: dict[str, int] = {
    "الأول": 1,
    "الثاني": 2,
    "الثالث": 3,
    "الرابع": 4,
    "الخامس": 5,
    "السادس": 6,
    "السابع": 7,
    "الثامن": 8,
    "التاسع": 9,
    "العاشر": 10,
}

# Combined arabic-indic + ASCII digit class. Used by regexes that capture
# chapter numbers written in either script.
DIGIT_CLASS = r"[\u0660-\u0669\d]+"


def normalize_digits(text: str) -> str:
    """Convert Arabic-Indic digits (٠-٩) to ASCII so int() can parse them."""
    return text.translate(_ARABIC_DIGITS)


def slugify(text: str) -> str:
    """Slugify a heading for anchor matching.

    Rules:
      - lowercase ASCII (Arabic has no case)
      - replace runs of whitespace with ``-``
      - strip punctuation except word chars, Arabic letters, and existing
        hyphens
      - trim leading/trailing hyphens

    Matches the convention book-kit uses elsewhere (e.g. md2pdf ToC links).
    """
    s = text.lower().strip()
    s = re.sub(r"\s+", "-", s)
    s = re.sub(r"[^\w\u0600-\u06ff-]", "", s)
    return s.strip("-")


# ---------------------------------------------------------------------------
# Reference extraction — one Reference per match.
# ---------------------------------------------------------------------------

@dataclass
class Reference:
    """One cross-reference found inside a chapter."""
    from_file: str                 # e.g. "ch-03.md"
    line: int                      # 1-indexed line number
    ref_text: str                  # original matched substring
    kind: str                      # see KINDS
    target_chapter: int | None = None   # numeric chapter target, None = intra-chapter
    target_anchor: str | None = None    # explicit anchor from ``(ch-NN.md#anchor)``


# kinds — used for branch selection in resolve_references
KINDS = (
    "bracket_ch",        # [ch-NN]
    "paren_ch",          # (ch-NN)
    "anchor_ch",         # (ch-NN.md#anchor)
    "english_chapter",   # chapter N / Ch. N / ch. N
    "arabic_chapter",    # الفصل N
    "arabic_ordinal",    # الفصل التاسع
    "previous",          # الفصل السابق
    "next",              # الفصل التالي
    "fi_alfasl",         # في الفصل N
    "the_section",       # the Foo section / chapter
)

# Patterns — compiled once. Each pattern is independent; an overlap check
# confirms that ``(ch-03)`` and ``(ch-03.md#anchor)`` do not both match the
# same span (digit-tail + ') ' vs '.md#...') so dedupe is unnecessary.

RE_BRACKET = re.compile(r"\[\s*ch-(\d+)\s*\]")
RE_PAREN_CH = re.compile(r"\(\s*ch-(\d+)\s*\)")
RE_ANCHOR = re.compile(r"\(\s*(ch-(\d+))\.md#([\w\u0600-\u06ff-]+)\s*\)")
RE_ENG_CHAPTER = re.compile(r"\b(?:[Cc]hapter|[Cc]h\.)\s+(\d+)\b")
RE_THE_SECTION = re.compile(r"\b[Tt]he\s+([A-Z][a-z]+)\s+(?:section|chapter)\b")
RE_AR_CHAPTER = re.compile(r"الفصل\s+(" + DIGIT_CLASS + r")")
_AR_ORDINAL_ALT = "|".join(re.escape(w) for w in ARABIC_ORDINALS)
RE_AR_ORDINAL = re.compile(r"الفصل\s+(" + _AR_ORDINAL_ALT + r")")
RE_AR_PREV = re.compile(r"الفصل\s+السابق")
RE_AR_NEXT = re.compile(r"الفصل\s+التالي")
RE_FI_ALFASL = re.compile(r"في\s+الفصل\s*(" + DIGIT_CLASS + r")")


def _read_md(path):
    """UTF-8 with cp1256/cp1252/latin-1 fallback (matches check_chapter.py)."""
    p = Path(path)
    try:
        return p.read_text(encoding="utf-8")
    except UnicodeDecodeError:
        for enc in ("cp1256", "cp1252"):
            try:
                return p.read_text(encoding=enc)
            except UnicodeDecodeError:
                continue
        return p.read_text(encoding="latin-1")


def _strip_code_fences(text):
    """Replace fenced code blocks with equivalent blank lines.

    Cross-references inside code blocks should not be flagged — they're
    either documentation of the reference syntax itself, or syntax examples
    in a technical book. Mirrors the `outside()` helper in check_chapter.py
    / book_check.py.
    """
    fence = re.compile(r"```.*?```", re.DOTALL)
    return fence.sub(lambda m: "\n" * m.group(0).count("\n"), text)


def _is_in_url(line, match_start):
    """Return True if the match starts inside a URL (``http://``/``https://``).

    Catches the false-positive case where ``ch-03`` appears inside a
    URL path like ``https://example.com/ch-03``. Cheap heuristic — just
    looks for ``https?://`` before the match on the same line.
    """
    prefix = line[:match_start]
    return bool(re.search(r"https?://\S*$", prefix))


def _extract_refs_from_line(line, line_no, filename):
    """Find every cross-reference in `line` (one chapter line).

    Returns a list of `Reference` objects. Multiple matches on the same
    line are allowed — each span is its own Reference.
    """
    refs = []

    # Bracket-wrapped ch-NN
    for m in RE_BRACKET.finditer(line):
        if _is_in_url(line, m.start()):
            continue
        n = int(m.group(1))
        refs.append(Reference(filename, line_no, m.group(0),
                              kind="bracket_ch", target_chapter=n))

    # Parenthetical ch-NN (no anchor) — kept separate from RE_ANCHOR so
    # the two never conflict (anchor form requires '.md#').
    for m in RE_PAREN_CH.finditer(line):
        if _is_in_url(line, m.start()):
            continue
        n = int(m.group(1))
        refs.append(Reference(filename, line_no, m.group(0),
                              kind="paren_ch", target_chapter=n))

    # Explicit anchor — (ch-NN.md#anchor)
    for m in RE_ANCHOR.finditer(line):
        if _is_in_url(line, m.start()):
            continue
        n = int(m.group(2))
        refs.append(Reference(filename, line_no, m.group(0),
                              kind="anchor_ch", target_chapter=n,
                              target_anchor=m.group(3)))

    # English "chapter N" / "Ch. N" / "ch. N"
    for m in RE_ENG_CHAPTER.finditer(line):
        if _is_in_url(line, m.start()):
            continue
        n = int(m.group(1))
        refs.append(Reference(filename, line_no, m.group(0),
                              kind="english_chapter", target_chapter=n))

    # "the Foo section" / "the Foo chapter" — intra-chapter section ref
    for m in RE_THE_SECTION.finditer(line):
        refs.append(Reference(filename, line_no, m.group(0),
                              kind="the_section"))

    # Arabic الفصل N (Arabic-Indic + ASCII digits normalized before int())
    for m in RE_AR_CHAPTER.finditer(line):
        n = int(normalize_digits(m.group(1)))
        refs.append(Reference(filename, line_no, m.group(0),
                              kind="arabic_chapter", target_chapter=n))

    # Arabic ordinal الفصل التاسع (and similar)
    for m in RE_AR_ORDINAL.finditer(line):
        n = ARABIC_ORDINALS[m.group(1)]
        refs.append(Reference(filename, line_no, m.group(0),
                              kind="arabic_ordinal", target_chapter=n))

    # الفصل السابق (previous chapter)
    for m in RE_AR_PREV.finditer(line):
        refs.append(Reference(filename, line_no, m.group(0),
                              kind="previous"))

    # الفصل التالي (next chapter)
    for m in RE_AR_NEXT.finditer(line):
        refs.append(Reference(filename, line_no, m.group(0),
                              kind="next"))

    # في الفصل N (in chapter N)
    for m in RE_FI_ALFASL.finditer(line):
        n = int(normalize_digits(m.group(1)))
        refs.append(Reference(filename, line_no, m.group(0),
                              kind="fi_alfasl", target_chapter=n))

    return refs


def extract_references(text, filename):
    """Extract all cross-references from a chapter's text."""
    cleaned = _strip_code_fences(text)
    refs = []
    for line_no, line in enumerate(cleaned.splitlines(), start=1):
        refs.extend(_extract_refs_from_line(line, line_no, filename))
    return refs


# ---------------------------------------------------------------------------
# Resolution
# ---------------------------------------------------------------------------

@dataclass
class BrokenRef:
    """A reference that failed to resolve."""
    from_file: str          # e.g. "ch-03.md"
    line: int               # 1-indexed line number
    ref_text: str           # original substring
    expected_target: str    # canonical target (file or "file#anchor")
    reason: str             # human-readable explanation


def _chapter_anchors(text):
    """Return set of slugified H2/H3 anchors present in the chapter."""
    anchors = set()
    for line in text.splitlines():
        m = re.match(r"^#{2,3}\s+(.+?)\s*$", line)
        if m:
            anchors.add(slugify(m.group(1)))
    return anchors


def _chapter_headings(text):
    """Return list of (level, heading_text) tuples for H2/H3 in the chapter."""
    out = []
    for line in text.splitlines():
        m = re.match(r"^(#{2,3})\s+(.+?)\s*$", line)
        if m:
            out.append((len(m.group(1)), m.group(2)))
    return out


def _anchor_for_word(text, word):
    """Find first H2/H3 heading containing ``word`` (case-insensitive).

    Returns the slug of the matching heading, or None if no heading matches.
    Multiple matches: first wins (spec rule).
    """
    for line in text.splitlines():
        m = re.match(r"^#{2,3}\s+(.+?)\s*$", line)
        if m and re.search(r"\b" + re.escape(word) + r"\b", m.group(1), re.I):
            return slugify(m.group(1))
    return None


def _current_chapter_number(filename):
    """Extract leading integer from a chapter filename, or None.

    Accepts ``ch-03.md``, ``ch-03-prompt.md``, etc. (matches the
    ``CHAPTER`` regex in book_check.py).
    """
    m = re.search(r"ch-(\d+)", Path(filename).name)
    return int(m.group(1)) if m else None


def _chapter_label(n):
    """Format chapter number as ``ch-NN`` (zero-padded two digits)."""
    return f"ch-{n:02d}"


def resolve_references(refs, book_root):
    """Resolve each reference. Returns ``(broken_list, resolved_count)``.

    `book_root` is the parent containing ``chapters/``. The function
    pre-loads every chapter file once and caches its anchors + headings so
    resolution is O(refs * chapters) worst-case.
    """
    broken: list[BrokenRef] = []
    resolved = 0
    chapters_dir = Path(book_root) / "chapters"

    # Pre-load all chapter files (numeric only — ch-NN.md).
    chapter_files: dict[int, dict] = {}
    for f in sorted(chapters_dir.glob("ch-*.md")):
        m = re.match(r"^ch-(\d+)\.md$", f.name)
        if not m:
            continue
        n = int(m.group(1))
        text = _read_md(f)
        chapter_files[n] = {
            "name": f.name,
            "text": text,
            "anchors": _chapter_anchors(text),
            "headings": _chapter_headings(text),
        }

    for ref in refs:
        current_ch = _current_chapter_number(ref.from_file)

        # ---- previous / next chapter (current_ch required) ----
        if ref.kind == "previous":
            if current_ch is None:
                broken.append(BrokenRef(ref.from_file, ref.line, ref.ref_text,
                                        ref.ref_text,
                                        "no chapter number in source file"))
                continue
            target_ch = current_ch - 1
            if target_ch < 1 or target_ch not in chapter_files:
                broken.append(BrokenRef(ref.from_file, ref.line, ref.ref_text,
                                        ref.ref_text,
                                        f"no such chapter {_chapter_label(target_ch)} (الفصل السابق)"))
                continue
            resolved += 1
            continue

        if ref.kind == "next":
            if current_ch is None:
                broken.append(BrokenRef(ref.from_file, ref.line, ref.ref_text,
                                        ref.ref_text,
                                        "no chapter number in source file"))
                continue
            target_ch = current_ch + 1
            if target_ch not in chapter_files:
                broken.append(BrokenRef(ref.from_file, ref.line, ref.ref_text,
                                        ref.ref_text,
                                        f"no such chapter {_chapter_label(target_ch)} (الفصل التالي)"))
                continue
            resolved += 1
            continue

        # ---- the Foo section (intra-chapter, requires current_ch) ----
        if ref.kind == "the_section":
            if current_ch is None or current_ch not in chapter_files:
                broken.append(BrokenRef(ref.from_file, ref.line, ref.ref_text,
                                        ref.ref_text,
                                        "no chapter context for 'the X section'"))
                continue
            m = RE_THE_SECTION.search(ref.ref_text)
            word = m.group(1) if m else None
            if not word:
                broken.append(BrokenRef(ref.from_file, ref.line, ref.ref_text,
                                        ref.ref_text,
                                        "could not extract section name"))
                continue
            ch = chapter_files[current_ch]
            anchor = _anchor_for_word(ch["text"], word)
            if anchor is None:
                broken.append(BrokenRef(ref.from_file, ref.line, ref.ref_text,
                                        ref.ref_text,
                                        f"no matching heading for section '{word}'"))
                continue
            resolved += 1
            continue

        # ---- all other kinds need a target chapter ----
        target_ch = ref.target_chapter
        if target_ch is None or target_ch not in chapter_files:
            label = _chapter_label(target_ch) if target_ch is not None else "?"
            broken.append(BrokenRef(ref.from_file, ref.line, ref.ref_text,
                                    ref.ref_text,
                                    f"no such file {label}.md"))
            continue

        ch = chapter_files[target_ch]

        # Explicit anchor — must match a slug in target chapter
        if ref.target_anchor is not None:
            slug = slugify(ref.target_anchor)
            if slug not in ch["anchors"]:
                broken.append(BrokenRef(ref.from_file, ref.line, ref.ref_text,
                                        f"{ch['name']}#{ref.target_anchor}",
                                        f"no such anchor {ref.target_anchor!r}"))
                continue
            resolved += 1
            continue

        # English "chapter N" — find an H2 containing "chapter N"
        if ref.kind == "english_chapter":
            wanted = f"chapter {target_ch}"
            if not any(re.search(r"\b" + re.escape(wanted) + r"\b", h, re.I)
                       for _, h in ch["headings"]):
                broken.append(BrokenRef(ref.from_file, ref.line, ref.ref_text,
                                        ref.ref_text,
                                        f"no matching heading for 'chapter {target_ch}' in {ch['name']}"))
                continue
            resolved += 1
            continue

        # Arabic "الفصل N" / "في الفصل N" — find an H2 containing "الفصل N"
        if ref.kind in ("arabic_chapter", "fi_alfasl"):
            wanted = f"الفصل {target_ch}"
            if not any(wanted in h for _, h in ch["headings"]):
                broken.append(BrokenRef(ref.from_file, ref.line, ref.ref_text,
                                        ref.ref_text,
                                        f"no matching heading for {wanted!r} in {ch['name']}"))
                continue
            resolved += 1
            continue

        # Arabic ordinal "الفصل التاسع" — find an H2 containing that exact phrase
        if ref.kind == "arabic_ordinal":
            ordinal_word = next(w for w, n in ARABIC_ORDINALS.items() if n == target_ch)
            wanted = f"الفصل {ordinal_word}"
            if not any(wanted in h for _, h in ch["headings"]):
                broken.append(BrokenRef(ref.from_file, ref.line, ref.ref_text,
                                        ref.ref_text,
                                        f"no matching heading for {wanted!r} in {ch['name']}"))
                continue
            resolved += 1
            continue

        # bracket_ch / paren_ch — file exists, that's sufficient
        if ref.kind in ("bracket_ch", "paren_ch"):
            resolved += 1
            continue

        # Fallback (shouldn't reach) — count as resolved.
        resolved += 1

    return broken, resolved


# ---------------------------------------------------------------------------
# Orchestration
# ---------------------------------------------------------------------------

def run_cross_ref(chapter_paths, book_root=None):
    """Run the cross-ref checker across all chapter files.

    `chapter_paths` is an iterable of Path objects pointing at chapter files.
    `book_root` is the parent containing `chapters/`. If None, inferred from
    `chapter_paths[0]` (parent.parent when grandparent is "chapters").

    Returns a dict:

        {
            "broken":   [{"from_file": ..., "line": ..., "ref_text": ...,
                          "expected_target": ..., "reason": ...}, ...],
            "resolved": int,
            "total":    int,
        }
    """
    # Infer book_root if missing
    if book_root is None:
        chapter_paths = list(chapter_paths)
        if chapter_paths:
            parent = Path(chapter_paths[0]).parent
            book_root = parent.parent if parent.name == "chapters" else parent
        else:
            book_root = Path(".")

    refs = []
    for cp in chapter_paths:
        cp = Path(cp)
        if not cp.exists():
            continue
        text = _read_md(cp)
        refs.extend(extract_references(text, cp.name))

    broken, resolved = resolve_references(refs, book_root)
    return {
        "broken": [
            {
                "from_file": b.from_file,
                "line": b.line,
                "ref_text": b.ref_text,
                "expected_target": b.expected_target,
                "reason": b.reason,
            }
            for b in broken
        ],
        "resolved": resolved,
        "total": resolved + len(broken),
    }


def render_markdown_report(result, task_id):
    """Format the broken-ref rows + summary as a markdown document."""
    lines = [f"# cross_ref — {task_id}", ""]
    for b in result["broken"]:
        lines.append(
            f"## Broken: {b['from_file']} line {b['line']} "
            f"→ {b['expected_target']}: {b['reason']}"
        )
        lines.append("")
    lines.append(f"## Resolved: {result['resolved']}/{result['total']} references")
    lines.append("")
    return "\n".join(lines)


def _force_utf8_stdio():
    """Force UTF-8 on stdout/stderr (Windows compat for Arabic glyphs)."""
    for stream in (sys.stdout, sys.stderr):
        reconfigure = getattr(stream, "reconfigure", None)
        if reconfigure is not None:
            try:
                reconfigure(encoding="utf-8")
            except (ValueError, OSError):
                pass


def main(argv=None):
    p = argparse.ArgumentParser(
        description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    p.add_argument("files", nargs="*", type=Path,
                   help="chapter files to scan (positional globs or paths)")
    p.add_argument("--book", type=Path, default=None,
                   help="path to books/<slug>/ (auto-globs chapters/*.md)")
    p.add_argument("--json", action="store_true",
                   help="emit JSON to stdout instead of writing a markdown report")
    p.add_argument("--report-dir", type=Path, default=Path("reports"),
                   help="directory prefix for markdown report (default: ./reports)")
    p.add_argument("--task", type=str, default="unknown",
                   help="task id used in the report filename + metadata (default: 'unknown')")
    args = p.parse_args(argv)
    _force_utf8_stdio()

    # Resolve the chapter file list
    chapter_paths = []
    book_root = None
    if args.book is not None:
        book_root = Path(args.book)
        chapters_dir = book_root / "chapters"
        if chapters_dir.exists():
            chapter_paths = sorted(chapters_dir.glob("*.md"))
    elif args.files:
        for f in args.files:
            f_str = str(f)
            if any(c in f_str for c in "*?["):
                chapter_paths.extend(Path(".").glob(f_str))
            else:
                chapter_paths.append(Path(f_str))

    if not chapter_paths:
        print("cross_ref: no chapter files provided", file=sys.stderr)
        return 2

    result = run_cross_ref(chapter_paths, book_root=book_root)

    if args.json:
        json.dump(result, sys.stdout, ensure_ascii=False)
        sys.stdout.write("\n")
    else:
        target_dir = args.report_dir
        if args.task and args.task != "unknown":
            target_dir = target_dir / args.task
        target_dir.mkdir(parents=True, exist_ok=True)
        target = target_dir / "cross_ref.md"
        target.write_text(render_markdown_report(result, args.task), encoding="utf-8")
        n_broken = len(result["broken"])
        print(f"cross_ref: wrote {target} ({n_broken} broken / {result['resolved']} resolved)",
              file=sys.stderr)

    return 1 if result["broken"] else 0


if __name__ == "__main__":
    sys.exit(main())