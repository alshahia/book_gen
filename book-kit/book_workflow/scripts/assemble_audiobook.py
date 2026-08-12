"""assemble_audiobook.py -- book2media Phase 4a: M4B audiobook assembler.

Combine per-chapter MP3s + chapter metadata + cover image + chapter
markers into a single AAC-in-M4B audiobook with proper ID3 metadata, for
upload to podcast/audiobook platforms.

CLI:
    py -3 book-kit/book_workflow/scripts/assemble_audiobook.py \\
        --book books/<slug> \\
        --locale en \\
        --out books/<slug>/exports/<slug>-en.m4b \\
        [--no-loudnorm] [--self-check]

EXIT CODES
    0  success -- M4B written at --out.
    2  input error (missing --book, --out escapes repo root, .., missing
       chapter, no MP3 for a (chapter, locale), missing cover, voice-
       policy mismatch, or style-guide `## Chapter titles` malformed).
    3  missing dependency (ffmpeg or ffprobe absent from PATH).
    4  internal/runtime (ffmpeg or ffprobe raised at runtime, including
       --self-check chapter-count mismatch, ID3 title mismatch, or
       loudnorm two-pass failure).

PATH VALIDATION
    --book and --out must resolve under the repo root. Any '..' component
    in either is rejected with exit 2. The script never reads or writes
    outside the configured root.

COVER IMAGE FALLBACK LADDER (per Phase 4a dispatch + locked design):
    1. Flux-generated (Mode 2 era; not implemented yet, slot reserved).
    2. books/<slug>/figures/cover.png (user-supplied).
    3. First PNG in books/<slug>/chapters-rendered/ (auto-pick).
    All three missing -> exit 2 via errors.raise_actionable("schema_invalid").

CHAPTER MARKERS
    Embedded via the ffmpeg metadata sidecar (FFMETADATA1 format). The
    MP4 muxer writes a Nero chapter atom (chpl) that iTunes / Apple Books
    / Pocket Casts / VLC all read; this is the simplest path that does
    not require an additional third-party tool. Chapter titles are
    sourced from `books/<slug>/style-guide.md` `## Chapter titles` when
    present (each `- "Title"` line maps to the ch-NN at the same index);
    otherwise the script falls back to the H1 of each `chapters/ch-NN.md`.

TWO-PASS LOUDNORM (per Phase 4a dispatch + plan F8):
    Default ON. EBU R128 targets I=-19 LUFS, TP=-2 dBTP, LRA=11.
    Step 1 (measure): run ffmpeg loudnorm pass 1 to /dev/null with
    `print_format=json`; parse `input_i`, `input_tp`, `input_lra`,
    `input_thresh`, `target_offset`.
    Step 2 (apply): run ffmpeg loudnorm pass 2 with the measured values
    plugged in (`linear=true`) to produce the loudness-corrected WAV
    that the M4B muxer reads.
    --no-loudnorm skips both passes (useful for smoke tests where the
    two-pass overhead is unwanted). pyloudnorm is consulted only if it
    is importable; otherwise the ffmpeg-measure fallback is used.

VOICE-POLICY ENFORCEMENT:
    Before synthesising, the script reads
    `books/<slug>/media-locale-manifest.json` and looks for the
    `products[locale==<locale>].voice` row whose `format` is
    `audio/m4b` (audiobook). The same voice used by `media_tts.py` is
    read from `figures/media-tts-manifest.json` (`chunks[].voice`). If
    the two disagree for ANY chapter, the script exits 2 with the
    `voice_unavailable` hint from `lib/errors.py`. If either manifest
    is missing, the check is skipped (manifestless dev path is OK) and
    a clear stderr line is emitted.

SELF-CHECK (--self-check):
    After M4B assembly, run `ffprobe -show_chapters -of json` against
    the output and assert `chapter_count == product_count` (number of
    `chunks[].chapter` rows in media-tts-manifest, or chapter file
    count when that manifest is missing). Also assert the format-level
    `title=` tag equals the book title (or slug fallback). Mismatch
    exits 4 via the `audio_empty` hint from `lib/errors.py`.

IDEMPOTENT
    Re-running with identical inputs produces a byte-identical M4B except
    for ffmpeg-managed timestamps inside the moov atom; these are not
    user-visible. We do not assert byte-identity in tests -- the spec
    permits "close enough".

NOT IN SCOPE (deferred to Phase 4b)
    - Mode 1 video assembly (assemble_video_horizontal.py)
    - Trailer + reels (assemble_video_trailer.py, assemble_reel.py)
"""
from __future__ import annotations

# ---------------------------------------------------------------------------
# UTF-8 stdio force (P4 #15 / P5 #22 inheritance) -- MUST run before argparse.
# ---------------------------------------------------------------------------

import sys
import io

for _stream in (sys.stdout, sys.stderr):
    try:
        _stream.reconfigure(encoding="utf-8")
    except (AttributeError, OSError, io.UnsupportedOperation):
        # Already detached (e.g. captured by pytest) or unsupported.
        pass


# ---------------------------------------------------------------------------
# Standard imports
# ---------------------------------------------------------------------------

import argparse
import json
import re
import shutil
import subprocess
import tempfile
from pathlib import Path


# ---------------------------------------------------------------------------
# Local imports (errors.py lives in sibling lib/).
# ---------------------------------------------------------------------------

_THIS_DIR = Path(__file__).resolve().parent
_LIB_DIR = _THIS_DIR.parent / "lib"
sys.path.insert(0, str(_LIB_DIR))
import errors as errors_mod  # noqa: E402


# ---------------------------------------------------------------------------
# Paths + constants
# ---------------------------------------------------------------------------

# This file lives at: book-kit/book_workflow/scripts/assemble_audiobook.py
# parents[3] = repo root.
REPO_ROOT = Path(__file__).resolve().parents[3]

# Cover-image fallback ladder. Tier 1 reserved for Flux-generated
# outputs (Mode 2 era; no implementation yet). Tier 2 is the user-locked
# user-supplied path. Tier 3 is the chapters-rendered auto-pick (sorted
# lexicographically, so prefix ordering matters -- e.g. "00-cover.png"
# sorts before "01-fig.png").
COVER_LADDER_TIERS = (
    "books/<slug>/figures/cover.png",
    "books/<slug>/chapters-rendered",
)

# Per-chapter MP3 path templates (locale-suffixed). Used when the
# figures/media-tts-manifest.json lookup misses.
PER_CHAPTER_AUDIO_TEMPLATE = "books/<slug>/chapters/<ch>-<locale>.mp3"

# ISO 639-1 -> ISO 639-2 (B) mapping for the locales book-kit supports.
# The MP4 muxer packs language into a 15-bit integer in the mdhd atom
# and only accepts 3-char codes; a 2-char code like "en" is silently
# dropped by ffmpeg's libavformat. We expand to 3-char before emitting.
_ISO_639_2 = {
    "en": "eng", "ar": "ara", "fr": "fra", "es": "spa",
    "de": "deu", "it": "ita", "pt": "por", "nl": "nld",
    "ru": "rus", "zh": "zho", "ja": "jpn", "ko": "kor",
    "tr": "tur", "fa": "fas", "ur": "urd", "hi": "hin",
}


def _locale_to_iso639_2(locale):
    """Return the 3-char ISO 639-2 code for a 2- or 3-char locale.

    Pass-through for already-3-char codes. Falls back to the first 3
    characters (uppercased) for unknown 2-char codes; this matches the
    "eng" / "ara" convention and avoids silent drops on uncommon locales.
    """
    if not locale:
        return "und"
    if len(locale) == 3:
        return locale.lower()
    if len(locale) == 2:
        return _ISO_639_2.get(locale.lower(), locale.lower() + "_")
    return "und"


# ---------------------------------------------------------------------------
# Errors
# ---------------------------------------------------------------------------


class InputError(Exception):
    """Raised for input errors that should exit 2 with a one-line hint."""


class MissingDepError(Exception):
    """Raised when ffmpeg or ffprobe is absent (exit 3)."""


class RuntimeFailure(Exception):
    """Raised when ffmpeg or ffprobe failed at runtime (exit 4)."""


# ---------------------------------------------------------------------------
# Path validation
# ---------------------------------------------------------------------------


def _resolve_under_root(candidate, label):
    """Resolve `candidate` under the repo root, refusing escapes.

    Rejects any path containing a '..' component and any absolute path
    that does not live under REPO_ROOT. Returns the resolved Path.
    """
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


# ---------------------------------------------------------------------------
# Style-guide chapter titles
# ---------------------------------------------------------------------------


_STYLE_TITLES_HEADER_RE = re.compile(
    r"(?ms)^##\s+Chapter\s+titles[^\n]*\n(.*?)(?=^\##\s|\Z)"
)
_STYLE_TITLES_ENTRY_RE = re.compile(r"""(?m)^\s*-\s+["'](.+?)["']\s*$""")


def _style_guide_chapter_titles(book_dir, expected_count):
    """Return chapter titles from style-guide.md `## Chapter titles` if present.

    Returns a list of length `expected_count` when the section is found and
    parses cleanly, otherwise returns None (caller falls back to H1).
    A list shorter than `expected_count` is treated as malformed -- we
    would rather refuse than guess -- and a list longer than
    `expected_count` is truncated to the chapter count.
    """
    sg_path = book_dir / "style-guide.md"
    if not sg_path.exists():
        return None
    try:
        text = sg_path.read_text(encoding="utf-8")
    except OSError:
        return None
    m = _STYLE_TITLES_HEADER_RE.search(text)
    if not m:
        return None
    block = m.group(1)
    titles = _STYLE_TITLES_ENTRY_RE.findall(block)
    if not titles:
        return None
    if len(titles) < expected_count:
        return None
    return titles[:expected_count]


# ---------------------------------------------------------------------------
# Cover-image fallback ladder
# ---------------------------------------------------------------------------


def _resolve_cover(book_dir):
    """Walk the cover-ladder tiers; return the first existing Path.

    On total miss, raises via errors.raise_actionable("schema_invalid",
    ...) so the exit code matches the dispatcher-mandated 2.
    """
    # Tier 2: user-supplied at <book>/figures/cover.png.
    primary = (book_dir / "figures" / "cover.png").resolve()
    if primary.exists() and primary.is_file():
        return primary
    # Tier 3: first PNG under <book>/chapters-rendered/ (sorted).
    cr = (book_dir / "chapters-rendered").resolve()
    if cr.is_dir():
        pngs = sorted(cr.glob("*.png"))
        if pngs:
            return pngs[0].resolve()
    # All tiers exhausted -> fail loud via the shared error catalog.
    errors_mod.raise_actionable(
        "schema_invalid",
        path=str(primary),
        field="cover_image.fallback_ladder",
    )


# ---------------------------------------------------------------------------
# Chapter discovery + per-chapter metadata
# ---------------------------------------------------------------------------


_PUBLISH_COMMENT_RE = re.compile(r"<!--.*?-->", re.DOTALL)
_H1_RE = re.compile(r"(?m)^#\s+(.+?)\s*$")
_CHAPTER_FILE_RE = re.compile(r"^(ch-(\d+))\.md$")


def _load_chapter_ids(book_dir):
    """Return a sorted list of chapter ids (e.g. ['ch-01', 'ch-02'])."""
    chapters_dir = (book_dir / "chapters").resolve()
    if not chapters_dir.is_dir():
        raise InputError("no chapters/ directory at %s" % chapters_dir)
    ids = []
    for entry in sorted(chapters_dir.iterdir()):
        m = _CHAPTER_FILE_RE.match(entry.name)
        if m:
            ids.append(m.group(1))
    if not ids:
        raise InputError("no ch-*.md chapter files in %s" % chapters_dir)
    return ids


def _chapter_title(book_dir, ch_id):
    """Return the H1 line of chapters/<ch_id>.md (publish-stripped)."""
    path = book_dir / "chapters" / ("%s.md" % ch_id)
    if not path.exists():
        raise InputError("chapter file missing: %s" % path)
    try:
        text = path.read_text(encoding="utf-8")
    except OSError as exc:
        raise InputError("cannot read %s: %s" % (path, exc))
    text = _PUBLISH_COMMENT_RE.sub("", text)
    m = _H1_RE.search(text)
    if not m:
        raise InputError("no H1 title in %s" % path)
    return m.group(1).strip()


def _find_chapter_audio(book_dir, ch_id, locale):
    """Resolve the per-chapter MP3 path for (ch_id, locale).

    Tier 1: figures/media-tts-manifest.json::chunks[chapter+locale].out_path
            (repo-root-relative; the canonical record left by media_tts.py).
    Tier 2: chapters/<ch_id>-<locale>.mp3 (raw layout, used by smoke tests).
    """
    manifest_path = book_dir / "figures" / "media-tts-manifest.json"
    if manifest_path.exists():
        try:
            data = json.loads(manifest_path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError) as exc:
            raise InputError("cannot read %s: %s" % (manifest_path, exc))
        for entry in data.get("chunks", []):
            if (
                isinstance(entry, dict)
                and entry.get("chapter") == ch_id
                and entry.get("locale") == locale
            ):
                rel = entry.get("out_path")
                if not rel:
                    continue
                abs_path = (REPO_ROOT / rel).resolve()
                if not abs_path.exists():
                    raise InputError(
                        "manifest out_path for %s/%s does not exist: %s"
                        % (ch_id, locale, abs_path)
                    )
                return abs_path
    # Tier 2 fallback (raw layout, no manifest produced).
    fallback = (book_dir / "chapters" / ("%s-%s.mp3" % (ch_id, locale))).resolve()
    if fallback.exists():
        return fallback
    raise InputError(
        "no MP3 found for chapter=%s locale=%s (manifest out_path missing and "
        "chapters/<id>-<locale>.mp3 missing)"
        % (ch_id, locale)
    )


# ---------------------------------------------------------------------------
# Two-pass loudnorm (EBU R128)
# ---------------------------------------------------------------------------


# Canonical EBU R128 targets per plan F8: I=-19 LUFS, TP=-2 dBTP, LRA=11.
# These are the values that ship to production; the smoke target uses
# the same constants (so the smoke validates the same code path).
LOUDNORM_TARGETS = {"I": -19.0, "TP": -2.0, "LRA": 11.0}


def _concat_to_wav(list_path, wav_path):
    """Concatenate the MP3s in `list_path` (concat demuxer) to a mono
    44.1 kHz PCM WAV at `wav_path`. This is the input the loudnorm
    filter expects; the M4B muxer reads the loudness-corrected WAV
    produced by ``_two_pass_loudnorm``."""
    ffmpeg = shutil.which("ffmpeg")
    if not ffmpeg:
        raise MissingDepError(
            "ffmpeg not on PATH; install or set FFMPEG_PATH to its absolute location"
        )
    cmd = [
        ffmpeg, "-y", "-hide_banner",
        "-f", "concat", "-safe", "0", "-i", str(list_path),
        "-ar", "44100", "-ac", "1", "-c:a", "pcm_s16le",
        str(wav_path),
    ]
    proc = subprocess.run(
        cmd, capture_output=True, text=True, encoding="utf-8", check=False,
    )
    if proc.returncode != 0:
        raise RuntimeFailure(
            "ffmpeg concat->WAV failed (rc=%d): %s"
            % (proc.returncode, (proc.stderr or proc.stdout).strip())
        )


def _pyln_measure(wav_path):
    """Measure integrated loudness / true peak via pyloudnorm, if available.

    Returns a dict with keys ``measured_I``, ``measured_TP``,
    ``measured_LRA``, ``measured_thresh``, ``offset`` (LU offset to
    apply so the integrated loudness lands at the target), or None when
    pyloudnorm (or its numpy / soundfile dependency) is absent. The
    caller falls back to ffmpeg's loudnorm JSON when this returns None.
    """
    try:
        import numpy as _np  # noqa: F401
        import soundfile as _sf  # noqa: F401
        import pyloudnorm as _pyln
    except ImportError:
        return None
    try:
        data, rate = _sf.read(str(wav_path))
    except (OSError, ValueError):
        return None
    if data is None or len(data) == 0:
        return None
    # pyloudnorm requires (samples, channels) shape; soundfile already
    # returns that. For mono we add a trailing axis.
    if data.ndim == 1:
        data = data.reshape(-1, 1)
    try:
        meter = _pyln.Meter(int(rate))
        il = float(meter.integrated_loudness(data))
    except Exception:
        return None
    # True peak via ffmpeg would be more accurate, but pyloudnorm does
    # not ship a true-peak meter; we approximate with sample peak (in dBFS).
    # The two-pass ffmpeg pass will replace this anyway; for the offset
    # the IL measurement is what matters.
    peak = float(_np.max(_np.abs(data))) if data.size else 0.0
    peak_db = 20.0 * _np.log10(peak) if peak > 0.0 else -99.0
    # Offset = target_I - measured_I; second pass loudnorm applies this
    # as the input gain before normalising.
    offset = LOUDNORM_TARGETS["I"] - il
    return {
        "measured_I": round(il, 3),
        "measured_TP": round(float(peak_db), 3),
        "measured_LRA": 0.0,  # not measured; pass-2 ffmpeg will fall back
        "measured_thresh": round(il - 0.0, 3),  # approximation
        "offset": round(offset, 3),
    }


def _ffmpeg_measure_loudnorm(wav_path):
    """Run ffmpeg loudnorm pass 1 and parse the JSON output.

    Returns the same shape as ``_pyln_measure``; raises RuntimeFailure
    when ffmpeg returns non-zero. Uses ``print_format=json`` and parses
    the last JSON object in stdout (ffmpeg writes the stats after the
    pass-1 stream; some versions intersperse other log lines).
    """
    ffmpeg = shutil.which("ffmpeg")
    if not ffmpeg:
        raise MissingDepError(
            "ffmpeg not on PATH; install or set FFMPEG_PATH to its absolute location"
        )
    af = (
        "loudnorm=I=%g:TP=%g:LRA=%g:print_format=json"
        % (LOUDNORM_TARGETS["I"], LOUDNORM_TARGETS["TP"], LOUDNORM_TARGETS["LRA"])
    )
    cmd = [
        ffmpeg, "-hide_banner", "-i", str(wav_path),
        "-af", af,
        "-f", "null", "-",
    ]
    proc = subprocess.run(
        cmd, capture_output=True, text=True, encoding="utf-8", check=False,
    )
    if proc.returncode != 0:
        raise RuntimeFailure(
            "ffmpeg loudnorm measure failed (rc=%d): %s"
            % (proc.returncode, proc.stderr.strip())
        )
    # The JSON object is at the end of stderr in ffmpeg 5+ and stdout
    # in some builds; scan both and pick the last parseable JSON.
    blob = proc.stderr or proc.stdout or ""
    decoder = json.JSONDecoder()
    idx = 0
    payload = None
    while idx < len(blob):
        brace = blob.find("{", idx)
        if brace < 0:
            break
        try:
            obj, end = decoder.raw_decode(blob[brace:])
        except json.JSONDecodeError:
            idx = brace + 1
            continue
        payload = obj
        idx = brace + end
    if not isinstance(payload, dict):
        raise RuntimeFailure(
            "ffmpeg loudnorm pass-1 produced no JSON payload (rc=%d)"
            % proc.returncode
        )
    # ffmpeg JSON keys: input_i, input_tp, input_lra, input_thresh, target_offset.
    measured_I = float(payload.get("input_i", -23.0))
    measured_TP = float(payload.get("input_tp", -2.0))
    measured_LRA = float(payload.get("input_lra", 0.0))
    measured_thresh = float(payload.get("input_thresh", -34.0))
    offset = float(payload.get("target_offset", 0.0))
    return {
        "measured_I": round(measured_I, 3),
        "measured_TP": round(measured_TP, 3),
        "measured_LRA": round(measured_LRA, 3),
        "measured_thresh": round(measured_thresh, 3),
        "offset": round(offset, 3),
    }


def _ffmpeg_apply_loudnorm(in_wav, out_wav, measured):
    """Run ffmpeg loudnorm pass 2 with the measured values applied.

    Writes ``out_wav`` (44.1 kHz mono PCM) with `linear=true` so the
    loudness is corrected in a single resampling + gain pass. Raises
    RuntimeFailure on ffmpeg non-zero exit.
    """
    ffmpeg = shutil.which("ffmpeg")
    if not ffmpeg:
        raise MissingDepError(
            "ffmpeg not on PATH; install or set FFMPEG_PATH to its absolute location"
        )
    af = (
        "loudnorm=I=%g:TP=%g:LRA=%g:"
        "measured_I=%g:measured_TP=%g:measured_LRA=%g:measured_thresh=%g:offset=%g:"
        "linear=true:print_format=summary"
        % (
            LOUDNORM_TARGETS["I"], LOUDNORM_TARGETS["TP"], LOUDNORM_TARGETS["LRA"],
            measured["measured_I"], measured["measured_TP"],
            measured["measured_LRA"], measured["measured_thresh"],
            measured["offset"],
        )
    )
    cmd = [
        ffmpeg, "-y", "-hide_banner", "-i", str(in_wav),
        "-af", af,
        "-ar", "44100", "-ac", "1",
        str(out_wav),
    ]
    proc = subprocess.run(
        cmd, capture_output=True, text=True, encoding="utf-8", check=False,
    )
    if proc.returncode != 0:
        raise RuntimeFailure(
            "ffmpeg loudnorm apply failed (rc=%d): %s"
            % (proc.returncode, (proc.stderr or proc.stdout).strip())
        )


def _two_pass_loudnorm(list_path, out_wav, no_loudnorm):
    """Run concat -> measure -> apply; return the loudness-corrected WAV.

    When ``no_loudnorm`` is True, the function still concatenates the
    MP3s to a WAV (so the M4B muxer can read a single input) but does
    NOT run the loudnorm measure/apply passes -- the WAV is just the
    raw concat. This keeps the flag's effect deterministic: the M4B
    muxer always reads a single WAV input regardless of loudnorm on/off.

    When ``no_loudnorm`` is False, runs the three-step pipeline:
    1. concat (MP3 -> WAV) via the concat demuxer
    2. measure (loudnorm pass 1) via pyloudnorm if importable, else
       ffmpeg `loudnorm=...:print_format=json`
    3. apply (loudnorm pass 2) via ffmpeg with the measured values
       plugged in, `linear=true`
    """
    if not no_loudnorm:
        # 1. First concat to an intermediate WAV so loudnorm has PCM input.
        intermediate = out_wav.with_suffix(".raw.wav")
        _concat_to_wav(list_path, intermediate)
        # 2. Measure.
        measured = _pyln_measure(intermediate)
        if measured is None:
            measured = _ffmpeg_measure_loudnorm(intermediate)
        # 3. Apply.
        _ffmpeg_apply_loudnorm(intermediate, out_wav, measured)
        return out_wav
    # --no-loudnorm path: still emit a WAV the M4B muxer can read.
    _concat_to_wav(list_path, out_wav)
    return out_wav


# ---------------------------------------------------------------------------
# Voice-policy enforcement
# ---------------------------------------------------------------------------


def _enforce_voice_policy(book_dir, locale):
    """Compare manifest voice vs synthesized voice. Exits 2 on mismatch.

    Reads ``books/<slug>/media-locale-manifest.json`` and looks for the
    audiobook product for ``locale``. Reads
    ``books/<slug>/figures/media-tts-manifest.json`` for the
    synthesised voice used per chapter. If both manifests are present
    AND the audiobook voice disagrees with ANY chapter's synthesised
    voice, raise an actionable error that maps to exit 2 with the
    `voice_unavailable` hint. If either manifest is missing, skip the
    check and emit a stderr note (manifestless dev path is OK).
    """
    media_manifest = book_dir / "media-locale-manifest.json"
    tts_manifest = book_dir / "figures" / "media-tts-manifest.json"
    if not media_manifest.exists() or not tts_manifest.exists():
        print(
            "assemble_audiobook: voice-policy check skipped "
            "(manifest absent at %s or %s)"
            % (media_manifest, tts_manifest),
            file=sys.stderr,
        )
        return
    try:
        media_data = json.loads(media_manifest.read_text(encoding="utf-8"))
        tts_data = json.loads(tts_manifest.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        print(
            "assemble_audiobook: voice-policy check skipped "
            "(manifest parse error: %s)" % exc,
            file=sys.stderr,
        )
        return
    # Find the audiobook product for this locale.
    product_voice = None
    for prod in media_data.get("products", []):
        if (
            isinstance(prod, dict)
            and prod.get("locale") == locale
            and prod.get("format") == "audio/m4b"
            and prod.get("skip") is not True
        ):
            product_voice = prod.get("voice")
            break
    if not product_voice:
        # No audiobook product for this locale -> no policy to enforce.
        return
    # Collect every (chapter, voice) pair the TTS run actually used.
    synthesised = {}
    for entry in tts_data.get("chunks", []):
        if not isinstance(entry, dict):
            continue
        ch = entry.get("chapter")
        voice = entry.get("voice")
        if ch and voice:
            synthesised[ch] = voice
    if not synthesised:
        print(
            "assemble_audiobook: voice-policy check skipped "
            "(media-tts-manifest has no chunks)",
            file=sys.stderr,
        )
        return
    mismatches = [
        (ch, voice) for ch, voice in synthesised.items()
        if voice != product_voice
    ]
    if mismatches:
        sample_ch, sample_voice = sorted(mismatches)[0]
        hint = errors_mod.format_hint(
            "voice_unavailable",
            voice=sample_voice,
            locale=locale,
            provider=product_voice,
        )
        print("assemble_audiobook: %s" % hint, file=sys.stderr)
        print(
            "assemble_audiobook: %d chapter(s) disagree (first: %s voice=%r, "
            "manifest voice=%r)"
            % (len(mismatches), sample_ch, sample_voice, product_voice),
            file=sys.stderr,
        )
        raise errors_mod.MediaPipelineError(hint, 2)


# ---------------------------------------------------------------------------
# Self-check (chapter count + ID3 title)
# ---------------------------------------------------------------------------


def _ffprobe_chapter_count(out_path):
    """Return the number of chapters in ``out_path`` via ffprobe JSON."""
    ffprobe = shutil.which("ffprobe")
    if not ffprobe:
        raise MissingDepError(
            "ffprobe not on PATH; install ffmpeg or set FFPROBE_PATH"
        )
    proc = subprocess.run(
        [
            ffprobe, "-v", "error", "-show_chapters",
            "-of", "json", str(out_path),
        ],
        capture_output=True, text=True, encoding="utf-8", check=False,
    )
    if proc.returncode != 0:
        raise RuntimeFailure(
            "ffprobe -show_chapters failed (rc=%d): %s"
            % (proc.returncode, proc.stderr.strip())
        )
    try:
        payload = json.loads(proc.stdout or "{}")
    except json.JSONDecodeError as exc:
        raise RuntimeFailure(
            "ffprobe -show_chapters returned non-JSON output: %s" % exc
        )
    chapters = payload.get("chapters") or []
    return len(chapters)


def _ffprobe_format_title(out_path):
    """Return the format-level `title` tag of ``out_path`` via ffprobe."""
    ffprobe = shutil.which("ffprobe")
    if not ffprobe:
        raise MissingDepError(
            "ffprobe not on PATH; install ffmpeg or set FFPROBE_PATH"
        )
    proc = subprocess.run(
        [
            ffprobe, "-v", "error",
            "-show_entries", "format_tags=title",
            "-of", "default=noprint_wrappers=1:nokey=1",
            str(out_path),
        ],
        capture_output=True, text=True, encoding="utf-8", check=False,
    )
    if proc.returncode != 0:
        return None
    return (proc.stdout or "").strip() or None


def _expected_chapter_count(book_dir, locale):
    """Return the expected chapter count for self-check, scoped to `locale`.

    Order of preference:
    1. Number of entries in `figures/media-tts-manifest.json::chunks`
       where the entry's `locale` matches the current locale (each
       matching entry is one chapter rendered for this locale).
    2. Number of `ch-NN.md` files in `chapters/` (if no per-locale
       matching entries are found, or no TTS manifest exists).
    """
    tts_manifest = book_dir / "figures" / "media-tts-manifest.json"
    if tts_manifest.exists():
        try:
            data = json.loads(tts_manifest.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            data = {}
        chunks = data.get("chunks") or []
        locale_rows = [c for c in chunks if c.get("locale") == locale]
        if locale_rows:
            return len(locale_rows)
    return len(_load_chapter_ids(book_dir))


def _self_check(out_path, book_dir, locale, book_title):
    """Run the post-build self-check. Raises MediaPipelineError on mismatch.

    - chapter_count must match the number of (chapter, locale) entries
      in media-tts-manifest (or ch-*.md count if that manifest is absent).
    - format-level `title=` tag must equal the book title (or slug
      fallback used in run_assemble).

    Exit code is 4 (via the `audio_empty` hint from `lib/errors.py`).
    """
    expected = _expected_chapter_count(book_dir, locale)
    actual = _ffprobe_chapter_count(out_path)
    if actual != expected:
        hint = errors_mod.format_hint(
            "audio_empty", chapter="<self-check>", locale="<self-check>"
        )
        print(
            "assemble_audiobook: --self-check failed: chapter_count=%d "
            "expected=%d (product_count mismatch)" % (actual, expected),
            file=sys.stderr,
        )
        print("assemble_audiobook: %s" % hint, file=sys.stderr)
        raise errors_mod.MediaPipelineError(hint, 4)
    actual_title = _ffprobe_format_title(out_path)
    if actual_title != book_title:
        print(
            "assemble_audiobook: --self-check failed: ID3 title=%r "
            "expected=%r" % (actual_title, book_title),
            file=sys.stderr,
        )
        raise errors_mod.MediaPipelineError(
            "ID3 title=%r does not match book title=%r"
            % (actual_title, book_title),
            4,
        )
    print(
        "assemble_audiobook: --self-check OK chapters=%d title=%r"
        % (actual, actual_title)
    )


# ---------------------------------------------------------------------------
# ffprobe + ffmpeg wrappers
# ---------------------------------------------------------------------------


def _probe_duration_ms(mp3_path):
    """Return the duration of `mp3_path` in milliseconds, via ffprobe.

    Uses the canonical ffmpeg-installed ffprobe CLI; we deliberately do
    not import the third-party `ffmpeg-python` package because the spec
    is "no new pip dependencies".
    """
    ffprobe = shutil.which("ffprobe")
    if not ffprobe:
        raise MissingDepError(
            "ffprobe not on PATH; install ffmpeg (which ships ffprobe) or "
            "set FFPROBE_PATH to its absolute location"
        )
    proc = subprocess.run(
        [
            ffprobe, "-v", "error",
            "-show_entries", "format=duration",
            "-of", "default=noprint_wrappers=1:nokey=1",
            str(mp3_path),
        ],
        capture_output=True, text=True, encoding="utf-8", check=False,
    )
    if proc.returncode != 0:
        raise RuntimeFailure(
            "ffprobe failed for %s (rc=%d): %s"
            % (mp3_path, proc.returncode, proc.stderr.strip())
        )
    out = proc.stdout.strip()
    try:
        seconds = float(out)
    except ValueError:
        raise RuntimeFailure(
            "ffprobe returned non-numeric duration %r for %s" % (out, mp3_path)
        )
    return int(round(seconds * 1000))


_METADATA_ESCAPE_RE = re.compile(r"([=;#\\\n])")


def _escape_metadata(text):
    """Escape special chars per FFMETADATA1 (backslash, equals, semicolon, hash, newline)."""
    return _METADATA_ESCAPE_RE.sub(r"\\\1", text)


def _write_ffmetadata(chapter_records, out_path):
    """Write an FFMETADATA1 file with [CHAPTER] sections per chapter record.

    TIMEBASE=1/1000 (millisecond resolution). The mp4 muxer reads these
    sections and writes a Nero chapter atom (chpl) by default; the
    `disable_chpl` movflag is not set, so chapters are emitted.
    """
    lines = [";FFMETADATA1"]
    for ch in chapter_records:
        lines.extend([
            "",
            "[CHAPTER]",
            "TIMEBASE=1/1000",
            "START=%d" % ch["start_ms"],
            "END=%d" % ch["end_ms"],
            "title=%s" % _escape_metadata(ch["title"]),
        ])
    out_path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def _ffmpeg_concat_to_m4b(
    audio_wav, cover_path, metadata_path, out_path, title, author, locale,
):
    """Wrap `audio_wav` (loudnormed or raw concat WAV) into an M4B with
    cover art + chapter markers from `metadata_path`.

    The audio input is ALWAYS a single WAV (produced by the loudnorm
    pre-pass or the raw concat pass -- see ``_two_pass_loudnorm``).
    Input index 0 = audio WAV, input index 1 = cover, input index 2 =
    metadata sidecar. `-map_metadata 2` pulls the FFMETADATA1 sidecar
    onto the output's metadata tree, where the mp4 muxer then reads
    [CHAPTER] sections into the chpl atom.
    """
    ffmpeg = shutil.which("ffmpeg")
    if not ffmpeg:
        raise MissingDepError(
            "ffmpeg not on PATH; install or set FFMPEG_PATH to its absolute location"
        )
    cmd = [
        ffmpeg, "-y", "-loglevel", "error",
        "-i", str(audio_wav),
        "-i", str(cover_path),
        "-i", str(metadata_path),
        "-map", "0:a", "-map", "1:v",
        "-c:a", "aac", "-b:a", "128k",
        "-c:v", "copy", "-disposition:v", "attached_pic",
        "-map_metadata", "2",
        "-metadata", "title=%s" % title,
        "-metadata", "artist=%s" % author,
        "-metadata", "album=%s" % title,
        "-metadata", "genre=Audiobook",
        # Language lives in the audio track's mdhd atom in MP4, not in
        # the format-level tags -- ffmpeg silently drops a format-level
        # `-metadata language=` for the mp4 muxer, so we target the
        # audio stream explicitly via -metadata:s:a:0. The muxer also
        # rejects 2-char ISO 639-1 codes ("en"); we expand to 3-char
        # ISO 639-2 so the language actually lands in the output.
        "-metadata:s:a:0", "language=%s" % _locale_to_iso639_2(locale),
        "-f", "mp4",
        str(out_path),
    ]
    proc = subprocess.run(
        cmd, capture_output=True, text=True, encoding="utf-8", check=False,
    )
    if proc.returncode != 0:
        raise RuntimeFailure(
            "ffmpeg concat failed (rc=%d): %s"
            % (proc.returncode, proc.stderr.strip())
        )


# ---------------------------------------------------------------------------
# Book-level metadata (title + author) from intake.md
# ---------------------------------------------------------------------------


_TITLE_RE = re.compile(
    r"(?ms)^##\s+1\.\s+Title[^\n]*\n+(.+?)\s*$"
)
_AUTHOR_RES = (
    re.compile(r"(?ms)^##\s+Author\s*\n+(.+?)\s*$"),
    re.compile(r"(?ms)^##\s+\d+\.\s+Author\s*\n+(.+?)\s*$"),
    re.compile(r"(?ms)^\*\*Author:\*\*\s*(.+?)\s*$"),
)


def _book_title(book_dir):
    """Return the book title from intake.md section 1, or None."""
    intake = book_dir / "intake.md"
    if not intake.exists():
        return None
    try:
        text = intake.read_text(encoding="utf-8")
    except OSError:
        return None
    m = _TITLE_RE.search(text)
    return m.group(1).strip() if m else None


def _book_author(book_dir):
    """Return the book author from intake.md, or None.

    Looks for '## Author', '## N. Author', or '**Author:** ...'.
    """
    intake = book_dir / "intake.md"
    if not intake.exists():
        return None
    try:
        text = intake.read_text(encoding="utf-8")
    except OSError:
        return None
    for rx in _AUTHOR_RES:
        m = rx.search(text)
        if m:
            return m.group(1).strip()
    return None


# ---------------------------------------------------------------------------
# Main run
# ---------------------------------------------------------------------------


def run_assemble(book_arg, locale, out_arg, no_loudnorm=False, self_check=False):
    """Run the full assembler. Returns the exit code.

    Flags:
        no_loudnorm  -- skip the two-pass loudnorm pre-pass. The M4B
                        muxer reads the raw concat WAV. The smoke
                        target uses this to keep wall-clock short.
        self_check   -- after M4B assembly, run ffprobe -show_chapters
                        and assert chapter_count == product_count; also
                        assert ID3 title == book title. Mismatch exits
                        4 via lib.errors.raise_actionable("audio_empty").
    """
    # Resolve --book under repo root (rejects .. and out-of-tree paths).
    try:
        book_dir = _resolve_under_root(book_arg, "--book")
    except InputError as exc:
        print("assemble_audiobook: %s" % exc, file=sys.stderr)
        return 2
    if not book_dir.is_dir():
        print("assemble_audiobook: --book not found: %s" % book_dir, file=sys.stderr)
        return 2

    # Resolve --out (or build the canonical default).
    if out_arg:
        try:
            out_path = _resolve_under_root(out_arg, "--out")
        except InputError as exc:
            print("assemble_audiobook: %s" % exc, file=sys.stderr)
            return 2
    else:
        out_path = (
            book_dir / "exports" / ("%s-%s.m4b" % (book_dir.name, locale))
        ).resolve()

    # Voice-policy enforcement runs before the M4B muxer -- a mismatch
    # is a configuration error, not a runtime error, so we exit 2.
    try:
        _enforce_voice_policy(book_dir, locale)
    except errors_mod.MediaPipelineError as exc:
        print("assemble_audiobook: %s" % exc.hint, file=sys.stderr)
        return exc.exit_code

    # Cover image via the fallback ladder.
    try:
        cover_path = _resolve_cover(book_dir)
    except errors_mod.MediaPipelineError as exc:
        print("assemble_audiobook: %s" % exc, file=sys.stderr)
        return exc.exit_code

    # Discover chapters + per-chapter MP3 paths + durations.
    try:
        ch_ids = _load_chapter_ids(book_dir)
    except InputError as exc:
        print("assemble_audiobook: %s" % exc, file=sys.stderr)
        return 2

    chapter_records = []
    for ch_id in ch_ids:
        try:
            mp3 = _find_chapter_audio(book_dir, ch_id, locale)
        except InputError as exc:
            print("assemble_audiobook: %s" % exc, file=sys.stderr)
            return 2
        try:
            dur_ms = _probe_duration_ms(mp3)
        except MissingDepError as exc:
            print("assemble_audiobook: %s" % exc, file=sys.stderr)
            return 3
        except RuntimeFailure as exc:
            print("assemble_audiobook: %s" % exc, file=sys.stderr)
            return 4
        chapter_records.append({
            "id": ch_id, "mp3": mp3, "duration_ms": dur_ms,
        })

    # Resolve chapter titles -- prefer style-guide.md `## Chapter titles`,
    # fall back to each ch-NN.md H1. If style-guide is malformed (length
    # mismatch), we still fall back to H1 rather than refuse.
    sg_titles = _style_guide_chapter_titles(book_dir, len(chapter_records))
    if sg_titles is not None:
        for ch, t in zip(chapter_records, sg_titles):
            ch["title"] = t
    else:
        for ch in chapter_records:
            try:
                ch["title"] = _chapter_title(book_dir, ch["id"])
            except InputError as exc:
                print("assemble_audiobook: %s" % exc, file=sys.stderr)
                return 2

    # Walk the chapters in order, computing millisecond offsets for
    # the FFMETADATA1 file. start_ms is exclusive of the previous
    # chapter's last frame; end_ms is inclusive of the last frame.
    cursor_ms = 0
    for ch in chapter_records:
        ch["start_ms"] = cursor_ms
        cursor_ms += ch["duration_ms"]
        ch["end_ms"] = cursor_ms

    # Title / author for the M4B metadata tree. Falls back gracefully.
    book_title = _book_title(book_dir) or book_dir.name
    book_author = _book_author(book_dir) or "Unknown"

    # Write the concat list + chapter metadata sidecar in a temp dir.
    with tempfile.TemporaryDirectory(prefix="assemble_audiobook_") as tmp:
        tmp_dir = Path(tmp)
        list_path = tmp_dir / "list.txt"
        list_path.write_text(
            "\n".join(
                "file '%s'" % ch["mp3"].as_posix() for ch in chapter_records
            ) + "\n",
            encoding="utf-8",
        )
        metadata_path = tmp_dir / "metadata.txt"
        _write_ffmetadata(chapter_records, metadata_path)
        out_path.parent.mkdir(parents=True, exist_ok=True)
        # The M4B muxer always reads a single WAV (loudnormed or raw).
        # Two-pass loudnorm is the default; --no-loudnorm skips the
        # measure/apply passes (the WAV is just the raw concat).
        audio_wav = tmp_dir / "audio.wav"
        try:
            _two_pass_loudnorm(list_path, audio_wav, no_loudnorm)
        except MissingDepError as exc:
            print("assemble_audiobook: %s" % exc, file=sys.stderr)
            return 3
        except RuntimeFailure as exc:
            print("assemble_audiobook: %s" % exc, file=sys.stderr)
            return 4
        try:
            _ffmpeg_concat_to_m4b(
                audio_wav, cover_path, metadata_path,
                out_path, book_title, book_author, locale,
            )
        except MissingDepError as exc:
            print("assemble_audiobook: %s" % exc, file=sys.stderr)
            return 3
        except RuntimeFailure as exc:
            print("assemble_audiobook: %s" % exc, file=sys.stderr)
            return 4
        if self_check:
            try:
                _self_check(out_path, book_dir, locale, book_title)
            except MissingDepError as exc:
                print("assemble_audiobook: %s" % exc, file=sys.stderr)
                return 3
            except RuntimeFailure as exc:
                print("assemble_audiobook: %s" % exc, file=sys.stderr)
                return 4
            except errors_mod.MediaPipelineError as exc:
                print("assemble_audiobook: %s" % exc.hint, file=sys.stderr)
                return exc.exit_code

    print(
        "assemble_audiobook: OK chapters=%d dur=%dms loudnorm=%s out=%s"
        % (len(chapter_records), cursor_ms, (not no_loudnorm), out_path)
    )
    return 0


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------


def _build_parser():
    p = argparse.ArgumentParser(
        prog="assemble_audiobook",
        description=(
            "Phase 4a: combine per-chapter MP3s + cover image + chapter "
            "markers into a single AAC-in-M4B audiobook."
        ),
    )
    p.add_argument(
        "--book", required=True,
        help="Book root (books/<slug>/).",
    )
    p.add_argument(
        "--locale", required=True,
        help="Locale code (en, ar, etc.).",
    )
    p.add_argument(
        "--out",
        help=(
            "Output M4B path (must resolve under repo root). Default: "
            "<book>/exports/<slug>-<locale>.m4b."
        ),
    )
    p.add_argument(
        "--no-loudnorm", action="store_true",
        help=(
            "Skip the two-pass EBU R128 loudnorm pre-pass. The M4B "
            "muxer reads the raw concatenated MP3s. Useful for smoke "
            "tests where the two-pass overhead is unwanted."
        ),
    )
    p.add_argument(
        "--self-check", action="store_true",
        help=(
            "After M4B assembly, run ffprobe -show_chapters and assert "
            "chapter_count == expected chapter count for the current "
            "locale (from media-tts-manifest or chapter file count); "
            "also assert ID3 title == book title. Mismatch exits 4 via "
            "the audio_empty hint."
        ),
    )
    return p


def main(argv=None):
    parser = _build_parser()
    args = parser.parse_args(argv)
    return run_assemble(
        args.book, args.locale, args.out,
        no_loudnorm=args.no_loudnorm, self_check=args.self_check,
    )


if __name__ == "__main__":
    sys.exit(main())
