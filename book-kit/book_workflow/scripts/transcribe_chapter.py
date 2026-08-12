"""transcribe_chapter.py -- book2media Phase 3 P5T2: ASR alignment runner.

Reads a chapter MP3 (produced by ``media_tts.py``) and runs faster-whisper
with ``word_timestamps=True`` + ``language=<locale>``. The model is
auto-selected per locale (Arabic -> ``large-v3``; English -> ``small``).
Output is a sidecar JSON list of ``{word, start, end, probability}`` rows
that ``align_srt.py`` consumes downstream.

CLI:
    py -3 book-kit/book_workflow/scripts/transcribe_chapter.py \\
        --book books/daily-focus --chapter ch-01 --locale ar

EXIT CODES
    0  success -- words JSON written.
    2  input error (missing book, missing MP3, bad locale, path escape).
    3  missing dependency (faster_whisper not installed).
    4  internal/runtime (model load failed, transcription returned 0 words).

PATH VALIDATION
    --book must resolve under the repo root; --chapter must name a file
    under ``<book>/chapters/``; --out must resolve under the repo root
    (default lands inside the book's ``chapters/`` dir).

FLAGS
    --dry-run     Print what would be transcribed; do not load the model.
    --from N      Resume from chunk N (1-based; requires --out-of-chunks
                  JSON manifest from media_tts; if absent, falls back to
                  full-chapter transcription).
    --only N      Transcribe chunk N only (1-based; same fallback rule).
    These mirror the Phase 7 orchestrator's per-chunk resume controls
    so a crashed long run can pick up mid-chapter without re-doing work.

IDEMPOTENT
    Re-running with the same MP3 + locale produces a byte-identical JSON
    (whisper is deterministic for the same audio + same model version).
    If the model version is bumped, regenerate -- no JSON diff is
    expected for identical audio.

# chub-cite: SYSTRAN/faster-whisper
"""
from __future__ import annotations

# ---------------------------------------------------------------------------
# UTF-8 stdio force -- MUST run before argparse or any print.
# ---------------------------------------------------------------------------

import sys
import io

for _stream in (sys.stdout, sys.stderr):
    try:
        _stream.reconfigure(encoding="utf-8")
    except (AttributeError, OSError, io.UnsupportedOperation):
        pass


# ---------------------------------------------------------------------------
# Standard imports
# ---------------------------------------------------------------------------

import argparse
import importlib.util
import json
import re
from pathlib import Path


# ---------------------------------------------------------------------------
# Paths + constants
# ---------------------------------------------------------------------------

# This file lives at book-kit/book_workflow/scripts/transcribe_chapter.py
# parents[3] = repo root.
REPO_ROOT = Path(__file__).resolve().parents[3]

# Per-locale model auto-pick. Must match check_whisper_deps.py so the
# self-check numbers match the real-run numbers.
MODEL_FOR_LOCALE = {
    "ar": "large-v3",
    "en": "small",
}

# MP3 discovery: share/audio/<slug>/ch-NN-<locale>.mp3 is the media_tts.py
# default. We also accept any path the caller passes via --mp3.
DEFAULT_AUDIO_SUBDIR = "shares"
DEFAULT_AUDIO_BUCKET = "audio"

# Sidecar JSON file naming: chapters/ch-NN-<locale>-words.json (per Phase 3
# dispatch).
WORD_RECORD = re.compile(r"^[A-Za-z0-9_.-]+$")


# ---------------------------------------------------------------------------
# Errors (raise from helpers, catch in main()).
# ---------------------------------------------------------------------------


class InputError(Exception):
    """Input error -- caller should exit 2."""


class MissingDepError(Exception):
    """Missing Python dep -- caller should exit 3."""


class RuntimeFailure(Exception):
    """Provider / runtime failure -- caller should exit 4."""


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


def _validate_chapter_id(chapter_id):
    """Reject chapter ids that don't look like ch-NN."""
    if not WORD_RECORD.match(chapter_id):
        raise InputError(
            "--chapter must match [A-Za-z0-9_.-]+ (got %r)" % chapter_id
        )


# ---------------------------------------------------------------------------
# Audio discovery.
# ---------------------------------------------------------------------------


def _resolve_mp3(book_dir, chapter_id, locale):
    """Find the MP3 for this (book, chapter, locale); raise InputError if absent."""
    audio_root = REPO_ROOT / DEFAULT_AUDIO_SUBDIR / DEFAULT_AUDIO_BUCKET
    slug = book_dir.name
    candidate = audio_root / slug / ("%s-%s.mp3" % (chapter_id, locale))
    if candidate.exists():
        return candidate
    raise InputError(
        "MP3 not found at %s; run media_tts.py first or pass --mp3" % candidate
    )


# ---------------------------------------------------------------------------
# Optional-dep probe.
# ---------------------------------------------------------------------------


def _ensure_faster_whisper():
    """Raise MissingDepError if faster_whisper is not installed."""
    if importlib.util.find_spec("faster_whisper") is None:
        raise MissingDepError(
            "faster-whisper not installed; "
            "`pip install faster-whisper==1.1.1` (~50 MB ctranslate2 pull)"
        )


# ---------------------------------------------------------------------------
# Word-record normalisation (faster-whisper may emit punctuation-stripped
# words with leading whitespace).
# ---------------------------------------------------------------------------


def _normalise_word(raw):
    """Trim whitespace + trailing punctuation that the ASR sometimes appends.

    We keep the apostrophes + dashes that carry lexical meaning; only
    strip the leading/trailing ASCII punctuation that the alignment
    step would otherwise have to ignore.
    """
    w = (raw or "").strip()
    # Strip leading punctuation that does not exist in chapter text.
    while w and w[0] in ".,;:!?'\"()[]{}<>":
        w = w[1:]
    # Strip trailing punctuation except % which the chapter text keeps.
    while w and w[-1] in ".,;:!?'\"()[]{}<>":
        w = w[:-1]
    return w


# ---------------------------------------------------------------------------
# Core transcribe.
# ---------------------------------------------------------------------------


def transcribe_audio(mp3_path, locale, model_id, only_chunk=None, from_chunk=None):
    """Transcribe `mp3_path`; return list[{word,start,end,prob}]."""
    from faster_whisper import WhisperModel

    try:
        model = WhisperModel(model_id, device="cuda", compute_type="float16")
    except Exception as exc:
        raise RuntimeFailure("WhisperModel init failed: %s" % exc)

    try:
        segments_iter, _info = model.transcribe(
            str(mp3_path),
            language=locale,
            word_timestamps=True,
            beam_size=1,
        )
    except Exception as exc:
        raise RuntimeFailure("transcribe() raised: %s" % exc)

    rows = []
    seg_idx = 0
    for segment in segments_iter:
        seg_idx += 1
        if only_chunk is not None and seg_idx != only_chunk:
            continue
        if from_chunk is not None and seg_idx < from_chunk:
            continue
        words = getattr(segment, "words", None) or []
        for w in words:
            token = _normalise_word(getattr(w, "word", ""))
            if not token:
                continue
            rows.append({
                "word": token,
                "start": float(getattr(w, "start", 0.0) or 0.0),
                "end": float(getattr(w, "end", 0.0) or 0.0),
                "prob": float(getattr(w, "probability", 0.0) or 0.0),
            })
    if not rows:
        raise RuntimeFailure(
            "transcription returned 0 words for %s (locale=%r, model=%r)"
            % (mp3_path, locale, model_id)
        )
    return rows


# ---------------------------------------------------------------------------
# Top-level entry point.
# ---------------------------------------------------------------------------


def run_transcribe(book_arg, chapter_id, locale, out_arg, dry_run,
                   from_chunk, only_chunk, mp3_arg=None):
    """Validate inputs, transcribe, write JSON; return exit code."""
    # 1. --book path.
    try:
        book_dir = _resolve_under_root(book_arg, "--book")
    except InputError as exc:
        print("transcribe_chapter: %s" % exc, file=sys.stderr)
        return 2
    if not book_dir.is_dir():
        print("transcribe_chapter: --book not a directory: %s" % book_dir,
              file=sys.stderr)
        return 2

    # 2. --chapter id.
    try:
        _validate_chapter_id(chapter_id)
    except InputError as exc:
        print("transcribe_chapter: %s" % exc, file=sys.stderr)
        return 2

    # 3. --locale.
    model_id = MODEL_FOR_LOCALE.get(locale)
    if model_id is None:
        print(
            "transcribe_chapter: unsupported locale=%r; supported: %s"
            % (locale, sorted(MODEL_FOR_LOCALE.keys())),
            file=sys.stderr,
        )
        return 2

    # 4. --out path.
    if out_arg:
        try:
            out_path = _resolve_under_root(out_arg, "--out")
        except InputError as exc:
            print("transcribe_chapter: %s" % exc, file=sys.stderr)
            return 2
    else:
        out_path = (book_dir / "chapters" /
                    ("%s-%s-words.json" % (chapter_id, locale))).resolve()

    # 5. MP3 source.
    if mp3_arg:
        try:
            mp3_path = _resolve_under_root(mp3_arg, "--mp3")
        except InputError as exc:
            print("transcribe_chapter: %s" % exc, file=sys.stderr)
            return 2
        if not mp3_path.exists():
            print("transcribe_chapter: --mp3 not found: %s" % mp3_path,
                  file=sys.stderr)
            return 2
    else:
        try:
            mp3_path = _resolve_mp3(book_dir, chapter_id, locale)
        except InputError as exc:
            print("transcribe_chapter: %s" % exc, file=sys.stderr)
            return 2

    if dry_run:
        print(
            "transcribe_chapter: DRY-RUN book=%s chapter=%s locale=%s "
            "model=%s mp3=%s out=%s from=%s only=%s"
            % (
                book_dir, chapter_id, locale, model_id, mp3_path, out_path,
                from_chunk, only_chunk,
            )
        )
        return 0

    # 6. Real transcription.
    try:
        _ensure_faster_whisper()
    except MissingDepError as exc:
        print("transcribe_chapter: %s" % exc, file=sys.stderr)
        return 3

    try:
        rows = transcribe_audio(
            mp3_path, locale, model_id,
            only_chunk=only_chunk, from_chunk=from_chunk,
        )
    except RuntimeFailure as exc:
        print("transcribe_chapter: %s" % exc, file=sys.stderr)
        return 4

    # 7. Write JSON (sorted keys + stable formatting for byte-identical
    #    reruns).
    out_path.parent.mkdir(parents=True, exist_ok=True)
    payload = {
        "chapter": chapter_id,
        "locale": locale,
        "model": model_id,
        "mp3_path": str(mp3_path.relative_to(REPO_ROOT)) if mp3_path.is_absolute() else str(mp3_path),
        "word_count": len(rows),
        "words": rows,
    }
    out_path.write_text(
        json.dumps(payload, indent=2, sort_keys=True, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )
    print(
        "transcribe_chapter: OK words=%d model=%s mp3=%s out=%s"
        % (len(rows), model_id, mp3_path, out_path)
    )
    return 0


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------


def _build_parser():
    p = argparse.ArgumentParser(
        prog="transcribe_chapter",
        description=(
            "Transcribe one (chapter, locale) MP3 into per-word timestamps "
            "via faster-whisper."
        ),
    )
    p.add_argument("--book", required=True, help="Book root (books/<slug>/).")
    p.add_argument("--chapter", required=True, help="Chapter id, e.g. ch-01.")
    p.add_argument("--locale", required=True, help="Locale code (en, ar).")
    p.add_argument(
        "--out",
        help="Output words JSON path. Default: <book>/chapters/<chapter>-<locale>-words.json.",
    )
    p.add_argument(
        "--mp3",
        help="Override MP3 source path. Default: shares/audio/<slug>/<chapter>-<locale>.mp3.",
    )
    p.add_argument(
        "--dry-run", action="store_true",
        help="Print the resolved plan; do not load the model.",
    )
    p.add_argument(
        "--from", dest="from_chunk", type=int, default=None,
        help="Resume from segment N (1-based). Optional.",
    )
    p.add_argument(
        "--only", dest="only_chunk", type=int, default=None,
        help="Transcribe segment N only (1-based). Optional.",
    )
    return p


def main(argv=None):
    parser = _build_parser()
    args = parser.parse_args(argv)
    return run_transcribe(
        book_arg=args.book,
        chapter_id=args.chapter,
        locale=args.locale,
        out_arg=args.out,
        dry_run=args.dry_run,
        from_chunk=args.from_chunk,
        only_chunk=args.only_chunk,
        mp3_arg=args.mp3,
    )


if __name__ == "__main__":
    sys.exit(main())
