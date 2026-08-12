"""align_srt.py -- book2media Phase 3 P5T3: ASR->canonical chunk alignment + SRT.

Reads the per-chunk TTS manifest from media_tts.py, re-chunks the
chapter text using the same H2-driven logic, slices the faster-whisper
word JSON by chunk time-windows, and emits a cue-aligned SRT via
difflib.SequenceMatcher. The downstream srt_to_ass.py consumes this SRT.

CLI:
    py -3 book-kit/book_workflow/scripts/align_srt.py \\
        --book books/<slug> --chapter ch-01 --locale ar \\
        [--drift-floor 0.55] [--locale-mismatch-ratio 0.50]

EXIT CODES
    0  success -- SRT written.
    2  input error (missing book, manifest entry, words JSON, bad chapter id).
    4  internal/runtime (alignment drift exceeds --drift-floor, chunk-count
       mismatch, no words in a chunk window).

PATH VALIDATION
    --book, --words-json, --out must resolve under repo root.

IDEMPOTENT
    Re-running with identical inputs produces a byte-identical SRT.

LOCALE TUNING
    Arabic chapters (and other non-English scripts) go through
    normalize_arabic() before the difflib comparison: diacritics are
    stripped, tatweel removed, and alef / yaa form variants collapsed.
    English chapters are unaffected.
    When the canonical text is mostly Latin but --locale is non-English
    (i.e. the chapter has not been translated yet), the drift floor is
    auto-dropped to 0.0 and a warning is printed to stderr -- the SRT
    is still written, possibly with zero cues, so the smoke pipeline
    does not fail spuriously on translation-pending chapters.

# chub-cite: pysubs2
"""
from __future__ import annotations

# ---------------------------------------------------------------------------
# UTF-8 stdio force (mandatory block from dispatch preamble).
# ---------------------------------------------------------------------------

import sys
for _stream in (sys.stdout, sys.stderr):
    try: _stream.reconfigure(encoding="utf-8")
    except Exception: pass


# ---------------------------------------------------------------------------
# Standard imports
# ---------------------------------------------------------------------------

import argparse
import difflib
import json
import re
import unicodedata
from pathlib import Path


# ---------------------------------------------------------------------------
# Paths + constants
# ---------------------------------------------------------------------------

# This file lives at: book-kit/book_workflow/scripts/align_srt.py
# parents[3] = repo root.
REPO_ROOT = Path(__file__).resolve().parents[3]

# Sibling-script + lib imports. media_tts provides the canonical
# chunker so the per-chunk text stays byte-identical to what TTS
# synthesized; lib/errors provides the audio_empty hint.
_THIS_DIR = Path(__file__).resolve().parent
_LIB_DIR = _THIS_DIR.parent / "lib"

sys.path.insert(0, str(_THIS_DIR))
sys.path.insert(0, str(_LIB_DIR))

import media_tts as media_tts_mod  # noqa: E402
try:
    import errors as errors_mod  # noqa: E402
except ImportError:  # pragma: no cover -- lib/ ships with the package
    errors_mod = None

# Standard chapter-id pattern (matches transcribe_chapter.py).
_CHAPTER_RE = re.compile(r"^[A-Za-z0-9_.-]+$")

# Drift floor: weighted average SequenceMatcher.ratio() below this is
# considered mis-aligned. 0.70 == 30% drift. Locale-specific tuning is
# exposed via the --drift-floor CLI flag.
DRIFT_RATIO_FLOOR = 0.70

# Tolerance (seconds) when slicing words by chunk time-window. Without
# this the first/last words of each chunk vanish into the gap between
# adjacent windows (faster-whisper frequently straddles chunk boundaries).
WINDOW_TOLERANCE_S = 0.05

# Latin-script ratio threshold above which we treat a chunk as "the
# caller sent English text into a non-English TTS pipeline." Above this,
# align_srt.py downgrades the drift floor to 0.0 so a translation-pending
# chapter does not fail. Mirrored in media_tts.py::_check_locale_match.
LOCALE_MISMATCH_RATIO = 0.30


# ---------------------------------------------------------------------------
# Arabic text normalisation (Phase 5 P5T2 follow-up; genuine-Arabic
# chapters only -- a no-op on English / Latin-only text).
#
# Arabic text from a chapter rarely matches its faster-whisper transcript
# byte-for-byte: the chapter may carry tashkil / diacritics that edge-tts
# silently strips, while the model may emit alef / yaa in a different form
# than the chapter source. We normalise both sides before difflib so a
# genuine-Arabic chapter crosses the 0.70 floor without flagging spurious
# drift. We deliberately do NOT normalise away script differences: if the
# caller fed English text into an Arabic TTS pipeline, the chapter is in
# English and the ASR is in Arabic-script -- no amount of diacritic
# normalisation will bridge the script gap; that case is handled by the
# locale-mismatch detector below.
# ---------------------------------------------------------------------------


_AR_DIACRITICS_RE = re.compile(
    "["
    "\u0610-\u061A"        # Arabic signs (U+0610..U+061A)
    "\u064B-\u065F"        # standard tashkil (U+064B..U+065F)
    "\u0670"               # superscript alef
    "\u06D6-\u06DC"        # end-of-ayah / small high marks (U+06D6..U+06DC)
    "\u06DF-\u06E4"        # more Quranic marks (U+06DF..U+06E4)
    "\u06E7\u06E8"         # small high meem / low noon / jeem
    "\u06EA-\u06ED"        # more marks (U+06EA..U+06ED)
    "]"
)
_AR_TATWEEL = "\u0640"
# Alef forms -> bare alef; alef maksura -> yaa. Hamza-on-alef variants
# (U+0623 / U+0625 / U+0622 / U+0671) collapse to bare alef (U+0627).
_AR_FORM_TABLE = str.maketrans({
    "\u0623": "\u0627",
    "\u0625": "\u0627",
    "\u0622": "\u0627",
    "\u0671": "\u0627",
    "\u0649": "\u064A",
})
_AR_PUNCT_RE = re.compile(
    r"["
    r"\u060C\u061B\u061F\u066A\u066B\u066C"   # Arabic comma, semicolon, question mark, percent, decimal sep
    r"\u066D\u066E\u066F"                      # Arabic asterisk, dot-above, dot-below
    r".,;:!?()\[\]{}"
    r"\u2014"                                  # em-dash (English sentence break)
    r"]"
)


def normalize_arabic(text):
    """Strip Arabic diacritics + tatweel + normalise alef / yaa forms.

    Lowercases ASCII letters (preserves Arabic letter shapes). Collapses
    runs of whitespace into a single space. Returns a plain ASCII-or-
    Arabic string ready for difflib.

    No-op when `text` contains no Arabic letters -- safe to call on
    English chapter text.
    """
    if not text:
        return ""
    # Canonical compatibility decomposition first as a defense-in-depth
    # step for any other punctuation-likes; cheap and stdlib-only.
    text = unicodedata.normalize("NFKC", text)
    text = _AR_DIACRITICS_RE.sub("", text)
    text = text.replace(_AR_TATWEEL, "")
    text = text.translate(_AR_FORM_TABLE)
    text = _AR_PUNCT_RE.sub(" ", text)
    # lowercase only the ASCII letters; Arabic letters are case-invariant
    # but lower-casing them still ensures any stray Latin letters match.
    text = "".join(c.lower() if c.isascii() and c.isalpha() else c for c in text)
    text = re.sub(r"\s+", " ", text).strip()
    return text


def _latin_ratio(text):
    """Return fraction of alphabetic chars that are Latin-script.

    Mirrors media_tts.py::_latin_ratio; duplicated rather than imported
    to keep each script's path-validation contract self-contained.
    """
    letters = [c for c in text if c.isalpha()]
    if not letters:
        return 0.0
    latin = sum(1 for c in letters if c.isascii())
    return latin / len(letters)


# ---------------------------------------------------------------------------
# Errors
# ---------------------------------------------------------------------------


class InputError(Exception):
    """Input error -- caller should exit 2."""


class AlignmentDrift(Exception):
    """Drift exceeded threshold -- caller should exit 4."""


# ---------------------------------------------------------------------------
# Path validation (mirrors media_tts.py::_resolve_under_root).
# ---------------------------------------------------------------------------


def _resolve_under_root(candidate, label):
    """Resolve `candidate` under the repo root, refusing escapes."""
    raw = Path(candidate)
    if ".." in raw.parts:
        raise InputError("%s must not contain '..': %s" % (label, candidate))
    if raw.is_absolute():
        target = raw.resolve()
    else:
        target = (REPO_ROOT / raw).resolve()
    root = REPO_ROOT.resolve()
    if target != root and root not in target.parents:
        raise InputError(
            "%s must resolve under %s: %s" % (label, root, candidate)
        )
    return target


def _validate_chapter(chapter_id):
    if not _CHAPTER_RE.match(chapter_id):
        raise InputError(
            "--chapter must match [A-Za-z0-9_.-]+ (got %r)" % chapter_id
        )


# ---------------------------------------------------------------------------
# Manifest + words JSON loaders
# ---------------------------------------------------------------------------


def _load_manifest_entry(book_dir, chapter_id, locale):
    manifest_path = book_dir / "figures" / "media-tts-manifest.json"
    if not manifest_path.exists():
        raise InputError(
            "manifest not found: %s; run media_tts.py first" % manifest_path
        )
    try:
        data = json.loads(manifest_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise InputError("cannot read manifest: %s" % exc)
    for entry in data.get("chunks", []):
        if (
            entry.get("chapter") == chapter_id
            and entry.get("locale") == locale
        ):
            inner = entry.get("chunks", [])
            if not inner:
                raise InputError(
                    "manifest entry for %s/%s has no chunks"
                    % (chapter_id, locale)
                )
            return inner
    raise InputError(
        "no manifest entry for chapter=%r locale=%r in %s"
        % (chapter_id, locale, manifest_path)
    )


def _load_words(path):
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except OSError as exc:
        raise InputError("cannot read %s: %s" % (path, exc))
    except json.JSONDecodeError as exc:
        raise InputError("words JSON malformed at %s: %s" % (path, exc))
    words = data.get("words")
    if not isinstance(words, list):
        raise InputError("words JSON missing 'words' array: %s" % path)
    return words


def _chunk_windows(chunk_records):
    """Return [(start_s, end_s), ...] cumulative from duration_ms."""
    windows = []
    cum_ms = 0
    for rec in chunk_records:
        dur_ms = int(rec.get("duration_ms") or 0)
        start_s = cum_ms / 1000.0
        cum_ms += dur_ms
        end_s = cum_ms / 1000.0
        windows.append((start_s, end_s))
    return windows


def _slice_words(words, start_s, end_s):
    """Return words whose [start,end] intersects the window (with tolerance)."""
    lo = start_s - WINDOW_TOLERANCE_S
    hi = end_s + WINDOW_TOLERANCE_S
    out = []
    for w in words:
        s = float(w.get("start", 0.0) or 0.0)
        e = float(w.get("end", 0.0) or 0.0)
        if e >= lo and s <= hi:
            out.append(w)
    return out


def _token_positions(text):
    """Return [(start_char, end_char), ...] for whitespace-separated tokens."""
    out = []
    i = 0
    n = len(text)
    while i < n:
        while i < n and text[i].isspace():
            i += 1
        if i >= n:
            break
        start = i
        while i < n and not text[i].isspace():
            i += 1
        out.append((start, i))
    return out


def _srt_ts(t_seconds):
    """Format seconds as SRT timestamp HH:MM:SS,mmm (rounded, sub-second)."""
    if t_seconds < 0:
        t_seconds = 0.0
    total_ms = int(round(t_seconds * 1000.0))
    h, rem = divmod(total_ms, 3600 * 1000)
    m, rem = divmod(rem, 60 * 1000)
    s, ms = divmod(rem, 1000)
    return "%02d:%02d:%02d,%03d" % (h, m, s, ms)


# ---------------------------------------------------------------------------
# Chapter text loading + canonical chunking
# ---------------------------------------------------------------------------


def _load_chapter_canonical(book_dir, chapter_id):
    """Return the chapter split into canonical chunks (same logic as media_tts)."""
    chapter_path = book_dir / "chapters" / ("%s.md" % chapter_id)
    if not chapter_path.exists():
        raise InputError("chapter file not found: %s" % chapter_path)
    try:
        text = chapter_path.read_text(encoding="utf-8")
    except OSError as exc:
        raise InputError("cannot read chapter %s: %s" % (chapter_path, exc))
    # Mirror media_tts.py's publish-strip; the canonical chunk text
    # must match what TTS actually synthesized.
    text = re.sub(r"<!--.*?-->", "", text, flags=re.DOTALL)
    return media_tts_mod._chunk_by_h2(text)


# ---------------------------------------------------------------------------
# Main run
# ---------------------------------------------------------------------------


def run_align(book_arg, chapter_id, locale, words_arg, out_arg, drift_floor=None, locale_mismatch_ratio=None):
    # 1. --book
    try:
        book_dir = _resolve_under_root(book_arg, "--book")
    except InputError as exc:
        print("align_srt: %s" % exc, file=sys.stderr)
        return 2
    if not book_dir.is_dir():
        print("align_srt: --book not a directory: %s" % book_dir,
              file=sys.stderr)
        return 2

    # 2. --chapter id
    try:
        _validate_chapter(chapter_id)
    except InputError as exc:
        print("align_srt: %s" % exc, file=sys.stderr)
        return 2

    # 3. --words-json (default <book>/chapters/<chapter>-<locale>-words.json)
    if words_arg:
        try:
            words_path = _resolve_under_root(words_arg, "--words-json")
        except InputError as exc:
            print("align_srt: %s" % exc, file=sys.stderr)
            return 2
    else:
        words_path = (book_dir / "chapters" /
                      ("%s-%s-words.json" % (chapter_id, locale))).resolve()
    if not words_path.exists():
        print(
            "align_srt: words JSON not found: %s; run transcribe_chapter.py first"
            % words_path,
            file=sys.stderr,
        )
        return 2

    # 4. --out (default <book>/chapters/<chapter>-<locale>.srt)
    if out_arg:
        try:
            out_path = _resolve_under_root(out_arg, "--out")
        except InputError as exc:
            print("align_srt: %s" % exc, file=sys.stderr)
            return 2
    else:
        out_path = (book_dir / "chapters" /
                    ("%s-%s.srt" % (chapter_id, locale))).resolve()

    # 5. Load manifest + words + canonical chunks.
    try:
        chunk_records = _load_manifest_entry(book_dir, chapter_id, locale)
        words = _load_words(words_path)
        canonical_chunks = _load_chapter_canonical(book_dir, chapter_id)
    except InputError as exc:
        print("align_srt: %s" % exc, file=sys.stderr)
        return 2

    if not canonical_chunks:
        print("align_srt: chapter %s yielded no chunks" % chapter_id,
              file=sys.stderr)
        return 2
    if len(canonical_chunks) != len(chunk_records):
        print(
            "align_srt: chunk count mismatch (manifest=%d canonical=%d); "
            "re-run media_tts.py to refresh the manifest"
            % (len(chunk_records), len(canonical_chunks)),
            file=sys.stderr,
        )
        return 4

    # 5b. Locale-mismatch auto-downgrade. When the chapter text is mostly
    # Latin but the locale is non-English, ASR will not align with the
    # canonical text no matter how clean either side is -- the chapter
    # hasn't been translated yet. Drop the floor to 0.0 so the smoke
    # test still produces an SRT (with whatever cues the matching finds,
    # possibly zero) rather than failing on a guaranteed drift.
    if drift_floor is None:
        drift_floor = DRIFT_RATIO_FLOOR
    effective_floor = drift_floor
    if locale != "en":
        max_latin = max((_latin_ratio(c) for c in canonical_chunks), default=0.0)
        ratio_threshold = (
            LOCALE_MISMATCH_RATIO
            if locale_mismatch_ratio is None
            else locale_mismatch_ratio
        )
        if max_latin > ratio_threshold:
            print(
                "align_srt: locale=%r but canonical text is mostly Latin "
                "(ratio=%.2f); chapter appears translation-pending. "
                "Drift floor dropped to 0.0; SRT will be emitted with "
                "whatever cues difflib finds."
                % (locale, max_latin),
                file=sys.stderr,
            )
            effective_floor = 0.0
    apply_arabic_norm = locale != "en"

    # 6. Walk chunks, slice words, align via difflib, emit cues.
    windows = _chunk_windows(chunk_records)
    cues = []
    drift_num = 0.0
    drift_den = 0
    cue_idx = 0
    for idx, ((start_s, end_s), canonical) in enumerate(
        zip(windows, canonical_chunks), start=1,
    ):
        slice_ = _slice_words(words, start_s, end_s)
        if not slice_:
            if errors_mod is not None:
                print(
                    "align_srt: %s"
                    % errors_mod.format_hint(
                        "audio_empty", chapter=chapter_id, locale=locale
                    ),
                    file=sys.stderr,
                )
            else:
                print(
                    "align_srt: no words in chunk window %d "
                    "(chapter=%s locale=%s); check transcribe_chapter output"
                    % (idx, chapter_id, locale),
                    file=sys.stderr,
                )
            return 4
        # Build asr_text so that empty / all-punctuation tokens do NOT
        # appear in the joined string -- otherwise normalize_arabic drops
        # them while slice_ keeps them, leaving positions out of sync
        # with the underlying word list. We track the surviving slice_
        # entries in slice_kept so first_ti / last_ti stay valid indices.
        slice_kept = []
        slice_words = []
        for w in slice_:
            tok = str(w.get("word", ""))
            if apply_arabic_norm:
                tok = normalize_arabic(tok)
            if not tok:
                continue
            slice_kept.append(w)
            slice_words.append(tok)
        if not slice_words:
            # Whole chunk reduced to empty by normalize -> no cues possible.
            continue
        asr_text = " ".join(slice_words)
        canonical_norm = re.sub(r"\s+", " ", canonical).strip()
        if apply_arabic_norm:
            # Strip diacritics + normalize alef/yaa on BOTH sides so a
            # genuine-Arabic chapter whose source carries tashkil but
            # whose ASR doesn't crosses the 0.70 floor without flagging
            # spurious drift. No-op when `text` is all-Latin.
            canonical_norm = normalize_arabic(canonical_norm)
        sm = difflib.SequenceMatcher(
            a=canonical_norm, b=asr_text, autojunk=False,
        )
        positions = _token_positions(asr_text)
        for block in sm.get_matching_blocks():
            if block.size <= 0:
                continue
            cue_text = canonical_norm[block.a:block.a + block.size].strip()
            if not cue_text:
                continue
            # Map the b-side char range to the underlying slice words.
            first_ti = None
            for ti, (ts, te) in enumerate(positions):
                if te > block.b:
                    first_ti = ti
                    break
            last_ti = None
            for ti in range(len(positions) - 1, -1, -1):
                ts, te = positions[ti]
                if ts < block.b + block.size:
                    last_ti = ti
                    break
            if first_ti is None or last_ti is None or last_ti < first_ti:
                continue
            cue_start = float(slice_kept[first_ti].get("start", start_s) or start_s)
            cue_end = float(slice_kept[last_ti].get("end", end_s) or end_s)
            # Clamp to chunk window -- guards against ASR timestamp drift.
            cue_start = max(cue_start, start_s)
            cue_end = min(cue_end, end_s)
            if cue_end <= cue_start:
                continue
            cue_idx += 1
            cues.append((cue_idx, cue_start, cue_end, cue_text))
        # Weighted by canonical length so a short chunk cannot mask a
        # long chunk that drifted badly.
        weight = max(len(canonical_norm), 1)
        drift_num += weight * sm.ratio()
        drift_den += weight

    avg_ratio = drift_num / max(drift_den, 1)
    if avg_ratio < effective_floor:
        print(
            "align_srt: alignment drift %.0f%% exceeds threshold "
            "(ratio=%.3f < %.2f); check ASR/chunker mismatch"
            % ((1.0 - avg_ratio) * 100.0, avg_ratio, effective_floor),
            file=sys.stderr,
        )
        return 4

    # 7. Write SRT. LF line endings; portable enough for ffmpeg + pysubs2.
    out_path.parent.mkdir(parents=True, exist_ok=True)
    parts = []
    for idx, start_s, end_s, text in cues:
        parts.append(str(idx))
        parts.append("%s --> %s" % (_srt_ts(start_s), _srt_ts(end_s)))
        parts.append(text)
        parts.append("")
    out_path.write_text("\n".join(parts), encoding="utf-8")
    print(
        "align_srt: OK cues=%d ratio=%.3f out=%s"
        % (cue_idx, avg_ratio, out_path)
    )
    return 0


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------


def _build_parser():
    p = argparse.ArgumentParser(
        prog="align_srt",
        description=(
            "Align per-chunk TTS text against faster-whisper word JSON "
            "via difflib.SequenceMatcher; emit cue-timed SRT."
        ),
    )
    p.add_argument("--book", required=True,
                   help="Book root (books/<slug>/).")
    p.add_argument("--chapter", required=True,
                   help="Chapter id, e.g. ch-01.")
    p.add_argument("--locale", required=True,
                   help="Locale code (en, ar).")
    p.add_argument(
        "--words-json",
        help="Words JSON path. Default: <book>/chapters/<chapter>-<locale>-words.json.",
    )
    p.add_argument(
        "--out",
        help="Output SRT path. Default: <book>/chapters/<chapter>-<locale>.srt.",
    )
    p.add_argument(
        "--drift-floor",
        type=float,
        default=None,
        help=(
            "Minimum acceptable weighted-average difflib.SequenceMatcher.ratio() "
            "(0.0-1.0). Default: 0.70. Lower for noisier locales or "
            "translation-pending chapters (set 0.0 to accept any drift)."
        ),
    )
    p.add_argument(
        "--locale-mismatch-ratio",
        type=float,
        default=None,
        help=(
            "Latin-script ratio threshold (0.0-1.0) above which a non-English "
            "locale is treated as translation-pending and the drift floor is "
            "dropped to 0.0. Default: 0.30. Raise to 0.50 for genuine-Arabic "
            "chapters that contain occasional English tech terms; lower to 0.10 "
            "for chapters that mix English transliterations."
        ),
    )
    return p


def main(argv=None):
    parser = _build_parser()
    args = parser.parse_args(argv)
    return run_align(
        book_arg=args.book,
        chapter_id=args.chapter,
        locale=args.locale,
        words_arg=args.words_json,
        out_arg=args.out,
        drift_floor=args.drift_floor,
        locale_mismatch_ratio=args.locale_mismatch_ratio,
    )


if __name__ == "__main__":
    sys.exit(main())
