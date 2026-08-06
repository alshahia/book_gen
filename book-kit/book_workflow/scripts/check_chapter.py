"""check_chapter.py — per-chapter prose enforcer for book-kit.

Runs eight rule-based checks against a single chapter file (one of
``chapters/ch-NN.md``, ``introduction.md``, ``preface.md``, ``app-*.md``).
Each check returns a ``CheckResult(name, status, evidence)`` so the caller
can render JSON or a markdown report.

Tokenization helpers (``word_count``, ``read_md``, ``outside``, ``FENCE``) are
copied verbatim from ``book_check.py`` rather than imported across script
boundaries — both scripts must stay runnable standalone, and a shared-import
coupling would make future refactors slower.

CLI:
    check_chapter.py <chapter.md> [--beat] [--json] [--config <style-guide.md|book-root>]
                         [--task <task-id>] [--report-dir <root>]

``--config`` accepts either a path to ``style-guide.md`` (P2-era behavior)
or a book-root directory containing both ``style-guide.md`` and ``bible.md``
(P5 — bible's ``## Rule applicability`` table gates the ``Countdown ≥1``
rule's ``applies_from``).

Exit: 0 if no FAIL, 1 if any FAIL, 2 if input is missing.

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
# CheckResult dataclass
# ---------------------------------------------------------------------------

@dataclass
class CheckResult:
    """One rule verdict: rule name + status + human-readable evidence."""
    name: str
    status: str  # 'PASS' | 'WARN' | 'FAIL'
    evidence: str


# ---------------------------------------------------------------------------
# Tokenization helpers — local copies from book_check.py (independence contract)
# ---------------------------------------------------------------------------

FENCE = re.compile(r"```.*?```", re.DOTALL)


def read_md(path):
    """Read a markdown file with UTF-8 + Arabic / cp1256 / cp1252 fallback."""
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


def outside(text):
    """Replace fenced code blocks with equivalent empty lines (line numbers preserved)."""
    return FENCE.sub(lambda m: "\n" * m.group(0).count("\n"), text)


def word_count(text):
    """Count word tokens (Latin + Arabic), apostrophes and Unicode quotes."""
    return len(re.findall(r"\b[\w'\-\u2018\u2019]+\b", text, re.UNICODE))


# ---------------------------------------------------------------------------
# Style-guide parser (YAML frontmatter + section fallback)
# ---------------------------------------------------------------------------

DEFAULT_WINDOW = (600, 750)
DEFAULT_FORBIDDEN: list[str] = []
DEFAULT_COUNTDOWN_TOKENS = ["بقي", "لم يبق"]


def _read_yaml_scalar(text, key):
    """Extract a top-level scalar `key: value` from a minimal frontmatter block.

    Supports the subset used by book-kit's style-guide: ``key: value`` lines
    where value is one line of plain text (or a comma-separated list). Returns
    None if the key is absent or no frontmatter block exists.
    """
    if not text.startswith("---"):
        return None
    end = text.find("\n---", 3)
    if end < 0:
        return None
    block = text[3:end]
    for line in block.splitlines():
        m = re.match(rf"^\s*{re.escape(key)}\s*:\s*(.+?)\s*$", line)
        if m:
            return m.group(1).strip()
    return None


def _parse_list_value(raw, sep=r"[,،]"):
    if not raw:
        return []
    return [t.strip() for t in re.split(sep, raw) if t.strip()]


def read_style_guide(path):
    """Pull the three configurable knobs from ``style-guide.md``.

    Priority order:
      1. YAML frontmatter ``Beat window:``, ``Forbidden patterns:``,
         ``Countdown tokens:`` (per task spec — frontmatter is canonical).
      2. ``## Forbidden patterns`` code-block (preserved contract with
         ``book_check.py`` so the same style guide feeds both scripts).

    Missing fields keep their defaults. An absent file yields all defaults.
    """
    out = {
        "window": DEFAULT_WINDOW,
        "forbidden": list(DEFAULT_FORBIDDEN),
        "countdown_tokens": list(DEFAULT_COUNTDOWN_TOKENS),
    }
    if path is None or not Path(path).exists():
        return out
    text = read_md(Path(path))

    # Frontmatter overrides take precedence.
    raw_window = _read_yaml_scalar(text, "Beat window")
    if raw_window:
        m = re.match(r"^\s*(\d+)\s*[-–]\s*(\d+)\s*$", raw_window)
        if m:
            lo, hi = int(m.group(1)), int(m.group(2))
            if 0 < lo < hi:
                out["window"] = (lo, hi)
    raw_forbidden = _read_yaml_scalar(text, "Forbidden patterns")
    if raw_forbidden:
        out["forbidden"] = _parse_list_value(raw_forbidden)
    raw_countdown = _read_yaml_scalar(text, "Countdown tokens")
    if raw_countdown:
        out["countdown_tokens"] = _parse_list_value(raw_countdown)

    # Section fallback for Forbidden patterns only — used when frontmatter
    # is absent (e.g. older book kits). Preserves compatibility with
    # ``book_check.py`` which reads from this same section.
    if not out["forbidden"]:
        m = re.search(r"## Forbidden patterns(.*?)(?=\n## |\Z)", text, re.S | re.I)
        if m:
            blocks = re.findall(r"```(?:[^\n]*)\n(.*?)```", m.group(1), re.S)
            section = [x.strip() for b in blocks for x in b.splitlines()
                       if x.strip() and not x.lstrip().startswith("#")]
            if section:
                out["forbidden"] = section
    return out


# ---------------------------------------------------------------------------
# bible.md parser — `## Rule applicability` table (P5)
# ---------------------------------------------------------------------------

def _resolve_config_paths(config_arg):
    """Decide which files ``--config`` refers to.

    Returns a ``(style_guide_path, bible_path)`` tuple. Either may be ``None``
    when the file is absent — both parser functions handle that gracefully.

    Three cases (P5 contract):
      - ``None`` / non-existent path — ``args.config`` was not supplied, or
        the supplied path doesn't exist on disk. Both parsers fall through
        to defaults; behavior matches the P2-era ``check_chapter.py``.
      - File path — caller pointed at ``style-guide.md`` directly (the
        P2-era invocation). ``bible.md`` is not consulted; the applicability
        table is empty, so ``countdown`` falls back to ``applies_from=3``
        (preserved back-compat default).
      - Directory path — caller pointed at a book root. We look inside for
        both ``style-guide.md`` and ``bible.md`` and parse whichever exist.
        This is the new P5 dispatch hook.
    """
    if config_arg is None:
        return None, None
    p = Path(config_arg)
    if not p.exists():
        return None, None
    if p.is_file():
        return p, None
    if p.is_dir():
        sg = p / "style-guide.md"
        bb = p / "bible.md"
        return (
            sg if sg.exists() else None,
            bb if bb.exists() else None,
        )
    return None, None


def parse_rule_applicability(path):
    """Read the ``## Rule applicability`` table from ``bible.md``.

    Returns ``dict[rule_name, applies_from_chapter_number]`` mirroring the
    ``Applies from`` column. Example::

        { "Countdown ≥1": 3, "Speaker tags": 5 }

    Returns ``{}`` when the path is ``None``, the file is absent, or the
    table section is missing. Defensive default mirrors ``render_ledger_check`` —
    if the bible doesn't carry the table, the rule runs as if the row were
    never written.
    """
    out: dict[str, int] = {}
    if path is None or not Path(path).exists():
        return out
    text = read_md(Path(path))
    m = re.search(r"## Rule applicability(.*?)(?=\n## |\Z)", text, re.S | re.I)
    if not m:
        return out
    # Match `| <Rule Name> | ch-NN | ... |`. The header row (`| Rule |` …)
    # and separator row (`| --- |` …) carry no `ch-NN` cell and so are skipped
    # by this regex naturally; we explicitly strip whitespace + a stray HTML
    # comment that the template carries between the table and the next section.
    for rule_name, ch_str in re.findall(
        r"\|\s*([^|\n]+?)\s*\|\s*ch-(\d+)\s*\|",
        m.group(1),
    ):
        rule_name = rule_name.strip()
        if not rule_name or rule_name.lower() == "rule":
            continue
        out[rule_name] = int(ch_str)
    return out


# ---------------------------------------------------------------------------
# Beat splitter (used by word_count_per_beat)
# ---------------------------------------------------------------------------

def _split_beats(text):
    """Split chapter text at H2/H3 boundaries → list of ``(heading, body)``.

    The first beat has ``heading=None`` and contains everything above the first
    H2/H3 (i.e. the chapter title + scene-setting paragraph). Empty input
    yields an empty list.
    """
    lines = text.splitlines()
    beats: list[tuple[str | None, list[str]]] = []
    heading = None
    buf: list[str] = []
    for line in lines:
        if re.match(r"^#{2,3}\s+", line):
            if heading is not None or buf:
                beats.append((heading, buf))
            heading = line.strip()
            buf = []
        else:
            buf.append(line)
    if heading is not None or buf:
        beats.append((heading, buf))
    return [(h, "\n".join(b)) for h, b in beats]


# ---------------------------------------------------------------------------
# The eight rule implementations
# ---------------------------------------------------------------------------

def word_count_per_beat(chapter_md, window=DEFAULT_WINDOW):
    """PASS when each H2/H3 beat is in ``[lo, hi]``.

    WARN when any beat is in ``[0.5*lo, lo) ∪ (hi, 1.5*hi]``.
    FAIL when any beat is outside ``[0.5*lo, 1.5*hi]`` (i.e. egregious).
    """
    lo, hi = window
    beats = _split_beats(chapter_md)
    if not beats:
        return [CheckResult("word_count_per_beat", "PASS",
                            "no H2/H3 beats detected (empty chapter)")]
    counts = [(heading or "(preamble)", word_count(outside(body))) for heading, body in beats]
    worst = "PASS"
    tags = []
    for heading, n in counts:
        if n > 1.5 * hi or n < 0.5 * lo:
            tags.append(f"FAIL({n})")
            worst = "FAIL"
        elif n < lo or n > hi:
            tags.append(f"WARN({n})")
            if worst != "FAIL":
                worst = "WARN"
        else:
            tags.append(f"PASS({n})")
    summary = " ".join(f"[{(h or '(preamble)')[:30]}:{t}]" for (h, _), t in zip(counts, tags))
    return [CheckResult("word_count_per_beat", worst,
                        f"window={lo}-{hi}; beats={len(counts)}; {summary}")]


def banned_patterns(chapter_md, patterns):
    if not patterns:
        return [CheckResult("banned_patterns", "PASS",
                            "no forbidden patterns configured")]
    clean = outside(chapter_md)
    hits = []
    for pattern in patterns:
        try:
            for match in re.finditer(pattern, clean):
                line_no = clean.count("\n", 0, match.start()) + 1
                hits.append(f"L{line_no}: {match.group(0)!r}")
        except re.error as e:
            hits.append(f"INVALID REGEX {pattern!r}: {e}")
    if hits:
        return [CheckResult("banned_patterns", "FAIL",
                            f"{len(hits)} match(es): {'; '.join(hits[:5])}")]
    return [CheckResult("banned_patterns", "PASS",
                        f"scanned {len(patterns)} pattern(s); no matches")]


def quote_pair_balance(chapter_md):
    """« vs » parity. FAIL if imbalanced; WARN if any single paragraph nests both."""
    opn = chapter_md.count("«")
    cls = chapter_md.count("»")
    if opn != cls:
        return [CheckResult("quote_pair_balance", "FAIL",
                            f"«={opn} vs »={cls} (imbalanced — every « needs a »)")]
    nested = []
    for raw in re.split(r"\n\s*\n", chapter_md):
        clean_p = FENCE.sub("", raw)
        if clean_p.count("«") > 1 and clean_p.count("»") > 1:
            nested.append(raw[:60].replace("\n", " ").strip())
    if nested:
        return [CheckResult("quote_pair_balance", "WARN",
                            f"balanced overall ({opn}/{cls}); {len(nested)} paragraph(s) "
                            f"contain multiple quoted pairs (likely nested dialogue): "
                            f"{' / '.join(nested[:2])}…")]
    return [CheckResult("quote_pair_balance", "PASS",
                        f"«={opn} »={cls}; single-pair per paragraph confirmed")]


def dialogue_own_line(chapter_md):
    """WARN when a paragraph mixes narration with ``«…»`` on the same line."""
    bad = []
    for raw in re.split(r"\n\s*\n", chapter_md):
        clean_p = FENCE.sub("", raw)
        if "«" not in clean_p:
            continue
        for line in clean_p.splitlines():
            if "«" not in line or "»" not in line:
                continue
            outside_quote = re.sub(r"«[^»]*»", "", line).strip(" \t\r\n.!?،؟,;:")
            if outside_quote:
                bad.append(line[:80].strip())
                break
    if bad:
        return [CheckResult("dialogue_own_line", "WARN",
                            f"{len(bad)} paragraph(s) mix narration + dialogue on the same line: "
                            f"{' / '.join(bad[:2])}…")]
    return [CheckResult("dialogue_own_line", "PASS",
                        "all dialogue paragraphs keep quoted text on its own line")]


def _strip_html_comments(text):
    """Remove ``<!-- … -->`` blocks (book-kit's self-critique convention)."""
    return re.sub(r"<!--.*?-->", "", text, flags=re.DOTALL)


def _last_paragraph(text):
    """Last non-empty paragraph (block separated by blank lines)."""
    paras = [p for p in re.split(r"\n\s*\n", text) if p.strip()]
    return paras[-1] if paras else ""


def closing_hook(chapter_md, max_words=8):
    """Find the last prose paragraph.

    Resolution order:
      1. If ``<!-- end-of-chapter -->`` marker is present → the last
         paragraph in the segment BEFORE the marker (HTML comments in
         that segment are stripped first, so a stray comment can't shift
         the paragraph boundary).
      2. Otherwise → the last paragraph of the file (after stripping HTML
         comments so the book-writer ``Self-critique`` annotation block
         never masquerades as the closing hook).
    """
    marker = "<!-- end-of-chapter -->"
    if marker in chapter_md:
        para = _last_paragraph(_strip_html_comments(chapter_md.split(marker, 1)[0]))
    else:
        para = _last_paragraph(_strip_html_comments(chapter_md))
    n = word_count(para)
    preview = para[:80].replace("\n", " ").strip()
    if n > max_words:
        return [CheckResult("closing_hook", "FAIL",
                            f"closing hook is {n} words (max {max_words}): {preview!r}")]
    return [CheckResult("closing_hook", "PASS",
                        f"closing hook is {n} words (≤ {max_words}): {preview!r}")]


def _chapter_number_from_path(path):
    """Extract the leading integer from a chapter filename, or None."""
    m = re.search(r"ch-(\d+)", Path(path).name)
    return int(m.group(1)) if m else None


def countdown(chapter_md, chapter_path=None, min_occurrences=1, applies_from=3, tokens=None):
    """Only run when ``ch-NN`` chapter number ≥ ``applies_from``.

    The default ``applies_from=3`` is preserved as a back-compat backstop for
    direct callers (e.g. the test helper ``_results_for``). When invoked via
    ``run_all_checks()`` / the CLI ``--config`` path, ``applies_from`` is
    resolved from the ``## Rule applicability`` table in ``bible.md`` —
    see ``parse_rule_applicability()`` and the P5 dispatch.
    """
    if tokens is None:
        tokens = DEFAULT_COUNTDOWN_TOKENS
    n = _chapter_number_from_path(chapter_path) if chapter_path is not None else None
    if n is None:
        return [CheckResult("countdown", "PASS",
                            "no chapter number in filename; rule skipped (skip ch-XX-pattern files)")]
    if n < applies_from:
        return [CheckResult("countdown", "PASS",
                            f"chapter ch-{n:02d} < applies_from={applies_from}; countdown rule skipped")]
    clean = outside(chapter_md)
    counts = {tok: clean.count(tok) for tok in tokens}
    total = sum(counts.values())
    if total < min_occurrences:
        return [CheckResult("countdown", "FAIL",
                            f"ch-{n:02d} requires ≥{min_occurrences} countdown token(s); "
                            f"found {total}; per-token counts={counts}")]
    return [CheckResult("countdown", "PASS",
                        f"ch-{n:02d} has {total} countdown token(s); per-token counts={counts}")]


def arabic_punctuation(chapter_md):
    """FAIL when Arabic-prose lines contain Latin ``, ; ? !`` (period excluded — too common).

    URL lines + fenced-code lines + blank lines are skipped. The rule only
    flags lines that contain Arabic characters, so English-only chapters
    are unaffected.
    """
    bad_lines = []
    clean = outside(chapter_md)
    for ln_idx, line in enumerate(clean.splitlines(), start=1):
        if not re.search(r"[\u0600-\u06ff\u0660-\u0669\u06f0-\u06f9]", line):
            continue
        if re.search(r"https?://\S+", line):
            continue
        bad = re.findall(r"[,;\?!]", line)
        if bad:
            bad_lines.append((ln_idx, "".join(bad), line.strip()[:60]))
    if bad_lines:
        ev = "; ".join(f"L{ln}: {b!r} in {t!r}" for ln, b, t in bad_lines[:3])
        return [CheckResult("arabic_punctuation", "FAIL",
                            f"{len(bad_lines)} line(s) with Latin punctuation in Arabic context: {ev}")]
    return [CheckResult("arabic_punctuation", "PASS",
                        "no Latin punctuation found in Arabic prose lines")]


def sentence_length(chapter_md, target_median=22):
    """WARN when median sentence length (in words) exceeds ``target_median``.

    Sentence split is regex-based: split after ``. ! ? ؟ ،`` followed by
    whitespace + an opening-of-sentence cue (capital, Arabic letter,
    opening bracket / quote). Markdown emphasis + heading lines are
    filtered out before length is measured.
    """
    clean = outside(chapter_md)
    sents = re.split(
        r"(?<=[.!?\u061f\u060c])\s+(?=[\u0600-\u06ffA-Z\u2018\u2019\"'(\[])",
        clean,
    )
    sents = [s.strip(" \t\r\n*_>#-") for s in sents if s.strip()]
    sents = [s for s in sents
             if (any(c.isalpha() or "\u0600" <= c <= "\u06ff" for c in s)) and len(s) > 5]
    if len(sents) < 3:
        return [CheckResult("sentence_length", "PASS",
                            f"only {len(sents)} sentence(s) detected; median skipped")]
    lengths = sorted(word_count(s) for s in sents)
    median = lengths[len(lengths) // 2]
    if median > target_median:
        return [CheckResult("sentence_length", "WARN",
                            f"median sentence is {median} words (target ≤ {target_median}); "
                            f"{len(sents)} sentence(s) sampled")]
    return [CheckResult("sentence_length", "PASS",
                        f"median sentence is {median} words (target ≤ {target_median}); "
                        f"{len(sents)} sentence(s) sampled")]


# ---------------------------------------------------------------------------
# Orchestration
# ---------------------------------------------------------------------------

def run_all_checks(chapter_path, config, applicability=None):
    """Run all eight checks against the chapter file at ``chapter_path``.

    ``config`` is the dict produced by ``read_style_guide``.
    ``applicability`` is the dict produced by ``parse_rule_applicability`` —
    empty when ``bible.md`` is absent or has no ``## Rule applicability``
    section. The ``Countdown ≥1`` row's chapter number overrides the
    runtime ``applies_from`` default (3) when present; when absent,
    the default is preserved so a book whose ``bible.md`` doesn't carry
    the table still gets the P2-era behavior.
    """
    text = read_md(chapter_path)
    if applicability is None:
        applicability = {}
    applies_from = applicability.get("Countdown ≥1", 3)
    results: list[CheckResult] = []
    results.extend(word_count_per_beat(text, config["window"]))
    results.extend(banned_patterns(text, config["forbidden"]))
    results.extend(quote_pair_balance(text))
    results.extend(dialogue_own_line(text))
    results.extend(closing_hook(text))
    results.extend(countdown(text, chapter_path=chapter_path,
                              tokens=config["countdown_tokens"],
                              applies_from=applies_from))
    results.extend(arabic_punctuation(text))
    results.extend(sentence_length(text))
    return results


def render_markdown(results, chapter_name, task_id):
    lines = [
        f"# check_chapter — {chapter_name}",
        "",
        f"_task: {task_id}_",
        "",
    ]
    for r in results:
        lines.append(f"## Check: {r.name} | {r.status}")
        lines.append("")
        lines.append(r.evidence)
        lines.append("")
    return "\n".join(lines)


def _chapter_label(chapter_path):
    """Stable chapter label for reports / JSON output (e.g. ``ch-03``)."""
    return Path(chapter_path).stem


def _force_utf8_stdio():
    """Reconfigure stdout/stderr to UTF-8 on Windows.

    Python's `json.dump` flushes via `sys.stdout.encoding`. On Windows,
    that's often cp1256 or cp1252, which can't encode `≤`, `«», or
    many Arabic glyphs. The script never emits binary to stdout, so
    forcing UTF-8 is safe and produces a parseable JSON payload in
    every locale.
    """
    for stream in (sys.stdout, sys.stderr):
        reconfigure = getattr(stream, "reconfigure", None)
        if reconfigure is not None:
            try:
                reconfigure(encoding="utf-8")
            except (ValueError, OSError):
                pass


def main(argv=None):
    p = argparse.ArgumentParser(description=__doc__,
                                formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("chapter", type=Path, help="path to ch-NN.md (or other chapter file)")
    p.add_argument("--config", type=Path, default=None,
                   help="path to style-guide.md (or a book-root containing both style-guide.md and bible.md)")
    p.add_argument("--json", action="store_true",
                   help="emit JSON to stdout instead of writing a markdown report")
    p.add_argument("--task", type=str, default="unknown",
                   help="task id used in the report filename + metadata (default: 'unknown')")
    p.add_argument("--report-dir", type=Path, default=Path("reports"),
                   help="directory prefix for the markdown report (default: ./reports)")
    args = p.parse_args(argv)
    _force_utf8_stdio()

    if not args.chapter.exists():
        print(f"check_chapter: not a file: {args.chapter}", file=sys.stderr)
        return 2

    style_guide_path, bible_path = _resolve_config_paths(args.config)
    config = read_style_guide(style_guide_path)
    applicability = parse_rule_applicability(bible_path)
    results = run_all_checks(args.chapter, config, applicability)
    chapter_label = _chapter_label(args.chapter)

    if args.json:
        payload = {"chapter": chapter_label,
                   "checks": [{"name": r.name, "status": r.status, "evidence": r.evidence}
                              for r in results]}
        json.dump(payload, sys.stdout, ensure_ascii=False)
        sys.stdout.write("\n")
    else:
        report_root = args.report_dir / args.task
        report_root.mkdir(parents=True, exist_ok=True)
        target = report_root / f"check_chapter_{chapter_label}.md"
        target.write_text(render_markdown(results, chapter_label, args.task), encoding="utf-8")
        fail = sum(r.status == "FAIL" for r in results)
        warn = sum(r.status == "WARN" for r in results)
        print(f"check_chapter: wrote {target} ({fail} FAIL / {warn} WARN)", file=sys.stderr)

    return 1 if any(r.status == "FAIL" for r in results) else 0


if __name__ == "__main__":
    sys.exit(main())
