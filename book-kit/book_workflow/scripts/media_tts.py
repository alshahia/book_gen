"""media_tts.py -- book2media TTS dispatcher (Phase 2a).

Chunk a chapter, dispatch to the per-locale TTS provider (Kokoro or
edge-tts), concatenate the per-chunk WAV into one MP3, and write a
sidecar JSON manifest under ``books/<slug>/figures/``.

CLI:
    py -3 book-kit/book_workflow/scripts/media_tts.py \\
        --book books/<slug> \\
        --chapter ch-NN \\
        --locale en \\
        --out shares/audio/<slug>/ch-NN-en.mp3

EXIT CODES
    0  success -- MP3 written, manifest updated.
    2  input error (missing chapter, missing --book, path escapes root).
    3  missing dependency (kokoro / edge-tts / ffmpeg absent when needed).
    4  internal/runtime error (provider raised, ffmpeg failed, audio was empty).

PATH VALIDATION
    --book must resolve under the repo root. --out, when given, must
    resolve under the repo root too (any subdir is fine; the script
    never writes outside the configured root).

CHUNKING
    H2-driven, with the same P17 review-chunker shape used by the
    orchestrator's Phase 7. Each H2 (## ...) starts a new chunk;
    paragraphs and oversized H2s are split via the same paragraph ->
    word-window fallback chain.

IDEMPOTENT
    Re-running with the same chapter + locale + voice produces a
    byte-identical MP3 only if the input text is byte-identical; chunk
    boundaries depend on the H2 sequence so a chapter edit re-chunks.
    The manifest is keyed by ``sha256`` of the per-chunk WAVs so two
    runs with identical chunks produce identical manifests.

NOT IN SCOPE (deferred to Phase 2b / 3 / 4)
    - faster-whisper word alignment (Phase 3)
    - Caption generation (Phase 3)
    - Multi-locale batch (Phase 2b)
    - Reel / audiobook / video assembly (Phase 4)
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
        pass


# ---------------------------------------------------------------------------
# Standard imports
# ---------------------------------------------------------------------------

import argparse
import hashlib
import json
import os
import re
import shutil
import struct
import subprocess
import tempfile
import wave
from pathlib import Path


# ---------------------------------------------------------------------------
# Local imports (sibling script: voices.py).
# ---------------------------------------------------------------------------

_THIS_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(_THIS_DIR))

import voices as voices_mod  # noqa: E402


# ---------------------------------------------------------------------------
# Paths + constants
# ---------------------------------------------------------------------------

# This file lives at: book-kit/book_workflow/scripts/media_tts.py
# parents[3] = repo root.
REPO_ROOT = Path(__file__).resolve().parents[3]

# Kokoro 0.9.4 emits audio at 24 kHz mono PCM. Verified empirically by
# inspecting `result.audio.shape` (a ~10s passage is ~240000 samples).
KOKORO_SAMPLE_RATE_HZ = 24000
KOKORO_SAMPLE_WIDTH_BYTES = 2  # 16-bit signed PCM after int16 conversion

# MP3 encode via ffmpeg. Lame at 128k mono is the audiobook-target
# bitrate; matches Phase 4's AAC target within rounding.
FFMPEG_MP3_CODEC_ARGS = ["-codec:a", "libmp3lame", "-b:a", "128k"]

# Edge-tts ships an asyncio entry point. To stay synchronous from the
# CLI we shell out to ``python -m edge_tts --write-media``. The module
# writes a single MP3 file with no further work on our side.
EDGE_TTS_CLI = [sys.executable, "-m", "edge_tts"]


# ---------------------------------------------------------------------------
# Errors
# ---------------------------------------------------------------------------


class MediaTtsError(Exception):
    """Raised for input errors that should exit 2 with a one-line hint."""


class MissingDependencyError(Exception):
    """Raised when an optional dep is missing (kokoro / edge-tts / ffmpeg)."""


class RuntimeFailure(Exception):
    """Raised when a provider raised or ffmpeg failed at runtime."""


# ---------------------------------------------------------------------------
# Path validation
# ---------------------------------------------------------------------------


def _resolve_under_root(candidate, label):
    """Resolve `candidate` under the repo root, refusing escapes."""
    raw = Path(candidate)
    if ".." in raw.parts:
        raise MediaTtsError("%s must not contain '..': %s" % (label, candidate))
    if raw.is_absolute():
        target = raw.resolve()
    else:
        target = (REPO_ROOT / raw).resolve()
    root = REPO_ROOT.resolve()
    if target != root and root not in target.parents:
        raise MediaTtsError(
            "%s must resolve under %s: %s" % (label, root, candidate)
        )
    return target


# ---------------------------------------------------------------------------
# Chapter chunker (P17 H2-driven, max ~400 words per chunk for TTS context)
# ---------------------------------------------------------------------------

_WORD_RE = re.compile(r"\b[\w'\u2018\u2019-]+\b", re.UNICODE)
_H2_BREAK = re.compile(r"(?m)(?=^## )")
_TTS_MAX_WORDS_PER_CHUNK = 400


def _chunk_by_h2(text, max_words=_TTS_MAX_WORDS_PER_CHUNK):
    """Split chapter text into H2-bounded chunks of <= max_words.

    Mirrors the orchestrator's P17 review chunker but with an H2 split
    boundary (review used H3; TTS uses H2 because audiobook chapters
    don't always have nested H3 sections). Falls back to paragraph
    splitting for oversized H2 sections, then to a word-window last
    resort.
    """
    words = _count_words(text)
    if words <= max_words:
        return [text] if text.strip() else []
    sections = _H2_BREAK.split(text)
    sections = [s for s in sections if s.strip()]
    if len(sections) <= 1:
        return _chunk_by_paragraphs(text, max_words)
    chunks = []
    current = ""
    current_words = 0
    for section in sections:
        sec_words = _count_words(section)
        if sec_words > max_words:
            if current:
                chunks.append(current)
                current = ""
                current_words = 0
            chunks.extend(_chunk_by_paragraphs(section, max_words))
            continue
        if current and current_words + sec_words > max_words:
            chunks.append(current)
            current = section
            current_words = sec_words
            continue
        current += section
        current_words += sec_words
    if current:
        chunks.append(current)
    return chunks


def _chunk_by_paragraphs(text, max_words):
    """Paragraph-level fallback when no H2 boundaries are available."""
    paragraphs = re.split(r"\n\s*\n", text)
    paragraphs = [p for p in paragraphs if p.strip()]
    if len(paragraphs) <= 1:
        return _chunk_by_words(text, max_words)
    chunks = []
    current = ""
    current_words = 0
    for p in paragraphs:
        pw = _count_words(p)
        if pw > max_words:
            if current:
                chunks.append(current)
                current = ""
                current_words = 0
            chunks.extend(_chunk_by_words(p, max_words))
            continue
        if current and current_words + pw > max_words:
            chunks.append(current)
            current = p
            current_words = pw
            continue
        if current:
            current += "\n\n" + p
        else:
            current = p
        current_words += pw
    if current:
        chunks.append(current)
    return chunks


def _chunk_by_words(text, max_words):
    """Word-window last resort when even a single paragraph exceeds budget."""
    words = text.split()
    if not words:
        return []
    return [" ".join(words[i:i + max_words]) for i in range(0, len(words), max_words)]


def _count_words(text):
    return len(_WORD_RE.findall(text))


def _latin_ratio(text):
    """Return fraction of alphabetic chars that are Latin-script.

    Used to detect a chunk whose source is English while the caller asked
    for a non-English locale (e.g., feeding English chapter text to an
    Arabic TTS voice). Result is in [0.0, 1.0]; 0.0 when no letters at all.
    """
    letters = [c for c in text if c.isalpha()]
    if not letters:
        return 0.0
    latin = sum(1 for c in letters if c.isascii())
    return latin / len(letters)


def _check_locale_match(chunks, locale):
    """Warn on stderr when chunk text looks English but locale is not 'en'.

    Edge-TTS (and most other TTS providers) will faithfully transliterate
    the English source into the target locale's script, producing audio
    whose ASR transcript does not match the canonical text. Subsequent
    align_srt.py runs will fail the drift check; the user needs to know
    the smoke test result is expected.
    """
    if locale == "en":
        return
    if not chunks:
        return
    max_ratio = max(_latin_ratio(c) for c in chunks)
    if max_ratio > 0.30:
        # ponytail: threshold chosen so a quote of English mid-paragraph
        # does not trip the warning; a whole chunk that's mostly English
        # almost always means the chapter has not been translated.
        print(
            "media_tts: WARNING chapter text appears mostly English "
            "(max latin_ratio=%.2f) but locale=%r; TTS will transliterate "
            "rather than translate. align_srt.py will accept the low "
            "drift as expected for a translation-pending chapter."
            % (max_ratio, locale),
            file=sys.stderr,
        )


# ---------------------------------------------------------------------------
# Manifest + chapter loading
# ---------------------------------------------------------------------------


def _load_chapter_text(book_dir, chapter_id):
    """Return the chapter text (stripped of leading HTML-comment self-critique)."""
    chapter_path = (book_dir / "chapters" / ("%s.md" % chapter_id)).resolve()
    if not chapter_path.exists():
        raise MediaTtsError(
            "chapter file not found: %s" % chapter_path
        )
    try:
        text = chapter_path.read_text(encoding="utf-8")
    except OSError as exc:
        raise MediaTtsError("cannot read %s: %s" % (chapter_path, exc))
    return _strip_publish_comments(text)


_PUBLISH_COMMENT_RE = re.compile(r"<!--.*?-->", re.DOTALL)


def _strip_publish_comments(text):
    """Remove the `<!-- Self-critique ... -->` block from chapter text.

    The book-writer skill appends a self-critique block at the end of
    each drafted chapter; that block is orchestrator/reviewer-facing
    metadata that must not be synthesized aloud.
    """
    return _PUBLISH_COMMENT_RE.sub("", text)


# ---------------------------------------------------------------------------
# Kokoro dispatch
# ---------------------------------------------------------------------------


def _check_kokoro_available():
    try:
        import kokoro  # noqa: F401
    except ImportError:
        raise MissingDependencyError(
            "kokoro not installed; `pip install kokoro==0.9.4` in the venv"
        )


def _synth_kokoro(text, voice_id, sample_rate_hz):
    """Synthesize via Kokoro; return (int16_pcm_bytes, duration_ms).

    Kokoro's ``pipeline(text, voice=...)`` is a generator yielding
    ``Result`` namedtuples with a ``.audio`` torch.Tensor at the
    package's native sample rate. We concatenate every yielded tensor
    along the time axis, normalize to int16 PCM, and let the caller
    wrap the result in a WAV header.
    """
    _check_kokoro_available()
    from kokoro import KPipeline  # noqa: F401  (after dep check)

    # Lang code: 'a' (American English) for locale=en, 'b' (British)
    # not currently used by any Phase 5 smoke target. Kokoro 0.9.4
    # supports only English; Arabic goes through edge-tts.
    lang_code = "a"
    try:
        pipeline = KPipeline(lang_code=lang_code)
    except Exception as exc:
        raise RuntimeFailure("KPipeline init failed: %s" % exc)

    chunks = []
    try:
        for result in pipeline(text, voice=voice_id):
            audio = getattr(result, "audio", None)
            if audio is None:
                continue
            # Convert torch.Tensor -> numpy ndarray -> int16 list.
            try:
                import torch  # local import: keeps module importable
                # without torch when kokoro absent
            except ImportError:
                raise MissingDependencyError(
                    "torch not installed; kokoro requires `pip install torch`"
                )
            arr = audio.detach().cpu().numpy() if hasattr(audio, "detach") else audio
            chunks.append(arr)
    except Exception as exc:
        raise RuntimeFailure("Kokoro synthesis raised: %s" % exc)

    if not chunks:
        raise RuntimeFailure(
            "Kokoro produced no audio chunks for voice=%r" % voice_id
        )

    import numpy as np  # local import; numpy ships with kokoro/torch anyway

    full = np.concatenate(chunks).astype("float32")
    # Clip + scale to int16 range. Kokoro emits values in roughly
    # [-0.5, 0.5] per the upstream README; we multiply by ~3.0 to
    # fill the int16 range without clipping, then clip defensively.
    pcm = np.clip(full * 32767.0 * 3.0, -32768.0, 32767.0).astype("<i2")
    duration_ms = int(round(1000.0 * pcm.shape[0] / sample_rate_hz))
    return pcm.tobytes(), duration_ms


# ---------------------------------------------------------------------------
# edge-tts dispatch (sync via subprocess)
# ---------------------------------------------------------------------------


def _check_edge_tts_available():
    try:
        import edge_tts  # noqa: F401
    except ImportError:
        raise MissingDependencyError(
            "edge-tts not installed; `pip install edge-tts==7.2.8` in the venv"
        )


def _synth_edge_tts(text, voice_id, out_path):
    """Synthesize via edge-tts (sync wrapper around the asyncio CLI).

    edge-tts is asyncio-native; the cleanest way to call it from a
    synchronous entry point is to shell out to its CLI (``python -m
    edge_tts --write-media``). The CLI writes a single MP3 with no
    intermediate WAV.
    """
    _check_edge_tts_available()
    out_path = Path(out_path)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    cmd = EDGE_TTS_CLI + [
        "--voice", voice_id,
        "--text", text,
        "--write-media", str(out_path),
    ]
    try:
        proc = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            encoding="utf-8",
            timeout=180,
            check=False,
        )
    except subprocess.TimeoutExpired as exc:
        raise RuntimeFailure("edge-tts timed out after 180s")
    except OSError as exc:
        raise MissingDependencyError("cannot launch edge-tts: %s" % exc)
    if proc.returncode != 0:
        raise RuntimeFailure(
            "edge-tts failed (rc=%d): %s" % (proc.returncode, proc.stderr.strip())
        )
    if not out_path.exists() or out_path.stat().st_size == 0:
        raise RuntimeFailure("edge-tts produced no output at %s" % out_path)
    return out_path


# ---------------------------------------------------------------------------
# WAV assembly (Kokoro -> single WAV -> MP3)
# ---------------------------------------------------------------------------


def _write_wav_int16(wav_path, pcm_bytes, sample_rate_hz):
    """Write a 16-bit PCM mono WAV file. Replaces any existing file."""
    wav_path = Path(wav_path)
    wav_path.parent.mkdir(parents=True, exist_ok=True)
    with wave.open(str(wav_path), "wb") as w:
        w.setnchannels(1)
        w.setsampwidth(KOKORO_SAMPLE_WIDTH_BYTES)
        w.setframerate(sample_rate_hz)
        w.writeframes(pcm_bytes)


def _ffmpeg_to_mp3(wav_path, mp3_path):
    """Convert WAV to MP3 via ffmpeg (libmp3lame). Replaces any existing file."""
    ffmpeg = shutil.which("ffmpeg")
    if not ffmpeg:
        raise MissingDependencyError(
            "ffmpeg not on PATH; install or set FFMPEG_PATH"
        )
    mp3_path = Path(mp3_path)
    mp3_path.parent.mkdir(parents=True, exist_ok=True)
    cmd = [
        ffmpeg, "-y", "-loglevel", "error",
        "-i", str(wav_path),
    ] + FFMPEG_MP3_CODEC_ARGS + [str(mp3_path)]
    proc = subprocess.run(
        cmd, capture_output=True, text=True, encoding="utf-8", check=False,
    )
    if proc.returncode != 0:
        raise RuntimeFailure(
            "ffmpeg failed (rc=%d): %s" % (proc.returncode, proc.stderr.strip())
        )
    if not mp3_path.exists() or mp3_path.stat().st_size == 0:
        raise RuntimeFailure("ffmpeg produced no MP3 at %s" % mp3_path)


# ---------------------------------------------------------------------------
# Manifest writer
# ---------------------------------------------------------------------------


def _stable_dump(data):
    """Canonical JSON: sorted keys + trailing single LF."""
    return json.dumps(data, indent=2, sort_keys=True, ensure_ascii=False) + "\n"


def _merge_manifest(manifest_path, entry):
    """Append/upsert `entry` into the per-book manifest list, keyed by chapter+locale."""
    if manifest_path.exists():
        try:
            data = json.loads(manifest_path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            data = {"chunks": []}
    else:
        data = {"chunks": []}
    chunks = data.get("chunks", [])
    # Drop any prior entry for the same (chapter, locale, voice).
    kept = [
        c for c in chunks
        if not (
            c.get("chapter") == entry["chapter"]
            and c.get("locale") == entry["locale"]
            and c.get("voice") == entry["voice"]
        )
    ]
    kept.append(entry)
    data["chunks"] = kept
    manifest_path.parent.mkdir(parents=True, exist_ok=True)
    manifest_path.write_text(_stable_dump(data), encoding="utf-8")


# ---------------------------------------------------------------------------
# Main run
# ---------------------------------------------------------------------------


def _chapter_baseline_text(book_dir, chapter_id):
    """Read the chapter text for chunking (publish-stripped)."""
    return _load_chapter_text(book_dir, chapter_id)


def run_synthesize(book_arg, chapter_id, locale, out_arg, tts_provider):
    """Synthesize one (chapter, locale) into an MP3. Returns the exit code."""
    try:
        book_dir = _resolve_under_root(book_arg, "--book")
    except MediaTtsError as exc:
        print("media_tts: %s" % exc, file=sys.stderr)
        return 2
    if not book_dir.is_dir():
        print("media_tts: --book not found: %s" % book_dir, file=sys.stderr)
        return 2

    # Resolve --out under repo root (or default to shares/audio/<slug>/ch-NN-<locale>.mp3).
    if out_arg:
        try:
            out_path = _resolve_under_root(out_arg, "--out")
        except MediaTtsError as exc:
            print("media_tts: %s" % exc, file=sys.stderr)
            return 2
    else:
        slug = book_dir.name
        out_path = (REPO_ROOT / "shares" / "audio" / slug / ("%s-%s.mp3" % (chapter_id, locale))).resolve()

    # Provider fallback: try manifest product entry; else resolve via voices.py defaults.
    if not tts_provider:
        try:
            tts_provider = _detect_tts_provider(book_dir, locale)
        except MediaTtsError:
            tts_provider = "kokoro" if locale == "en" else "edge-tts"

    try:
        voice_id = voices_mod.resolve_voice(book_dir.name, locale, tts_provider)
    except voices_mod.VoiceResolutionError as exc:
        print("media_tts: %s" % exc, file=sys.stderr)
        return 2

    text = _chapter_baseline_text(book_dir, chapter_id)
    chunks = _chunk_by_h2(text)
    if not chunks:
        print("media_tts: chapter %s yielded no chunks" % chapter_id, file=sys.stderr)
        return 2

    # Locale-mismatch detection: warn if English text is heading to a
    # non-English TTS voice. Best done at synthesis time so the user sees
    # the warning alongside the manifest write.
    _check_locale_match(chunks, locale)

    chunk_records = []
    sample_rate_hz = KOKORO_SAMPLE_RATE_HZ

    if tts_provider == "kokoro":
        with tempfile.TemporaryDirectory(prefix="media_tts_") as tmp:
            tmp_dir = Path(tmp)
            full_pcm = bytearray()
            for idx, chunk_text in enumerate(chunks, start=1):
                pcm_bytes, dur_ms = _synth_kokoro(chunk_text, voice_id, sample_rate_hz)
                sha = hashlib.sha256(pcm_bytes).hexdigest()
                chunk_records.append({
                    "index": idx,
                    "bytes": len(pcm_bytes),
                    "duration_ms": dur_ms,
                    "sha256": sha,
                })
                full_pcm.extend(pcm_bytes)
            total_ms = int(round(1000.0 * len(full_pcm) / (sample_rate_hz * KOKORO_SAMPLE_WIDTH_BYTES)))
            wav_path = tmp_dir / "concat.wav"
            _write_wav_int16(wav_path, bytes(full_pcm), sample_rate_hz)
            _ffmpeg_to_mp3(wav_path, out_path)
    elif tts_provider == "edge-tts":
        with tempfile.TemporaryDirectory(prefix="media_tts_") as tmp:
            tmp_dir = Path(tmp)
            total_ms = 0
            for idx, chunk_text in enumerate(chunks, start=1):
                chunk_mp3 = tmp_dir / ("chunk-%02d.mp3" % idx)
                _synth_edge_tts(chunk_text, voice_id, chunk_mp3)
                chunk_bytes = chunk_mp3.read_bytes()
                sha = hashlib.sha256(chunk_bytes).hexdigest()
                dur_ms = _mp3_duration_ms_estimate(chunk_bytes)
                total_ms += dur_ms
                chunk_records.append({
                    "index": idx,
                    "bytes": len(chunk_bytes),
                    "duration_ms": dur_ms,
                    "sha256": sha,
                })
            # Concat chunks via ffmpeg concat demuxer; preserves MP3 timing.
            list_path = tmp_dir / "list.txt"
            list_path.write_text(
                "\n".join(
                    "file '%s'" % ("chunk-%02d.mp3" % i)
                    for i in range(1, len(chunks) + 1)
                ),
                encoding="utf-8",
            )
            cmd = [
                shutil.which("ffmpeg") or "ffmpeg",
                "-y", "-loglevel", "error",
                "-f", "concat", "-safe", "0",
                "-i", str(list_path),
                "-c", "copy",
                str(out_path),
            ]
            proc = subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8", check=False)
            if proc.returncode != 0:
                raise RuntimeFailure(
                    "ffmpeg concat failed (rc=%d): %s" % (proc.returncode, proc.stderr.strip())
                )
    else:
        print(
            "media_tts: unknown tts_provider=%r (use kokoro or edge-tts)" % tts_provider,
            file=sys.stderr,
        )
        return 2

    # Sidecar manifest.
    figures_dir = book_dir / "figures"
    manifest_path = figures_dir / "media-tts-manifest.json"
    sha_manifest = hashlib.sha256(
        json.dumps(chunk_records, sort_keys=True).encode("utf-8")
    ).hexdigest()
    entry = {
        "chapter": chapter_id,
        "locale": locale,
        "voice": voice_id,
        "tts_provider": tts_provider,
        "chunk_count": len(chunk_records),
        "chunks": chunk_records,
        "duration_ms": total_ms,
        "sha256_manifest": sha_manifest,
        "out_path": str(out_path.relative_to(REPO_ROOT)),
        "mp3_bytes": out_path.stat().st_size,
    }
    try:
        _merge_manifest(manifest_path, entry)
    except OSError as exc:
        print("media_tts: cannot write manifest: %s" % exc, file=sys.stderr)
        return 4

    print(
        "media_tts: OK dur=%dms bytes=%d chunks=%d out=%s"
        % (total_ms, out_path.stat().st_size, len(chunk_records), out_path)
    )
    return 0


def _mp3_duration_ms_estimate(mp3_bytes):
    """Estimate MP3 duration from the frame header (CBR / VBR first frame).

    This is an estimate only -- for the smoke it is more than enough.
    The Phase 3 transcription step is the authoritative duration source.
    """
    # Skip ID3v2 tag if present.
    offset = 0
    if mp3_bytes[:3] == b"ID3":
        # ID3v2 size is 4 bytes; the high bit of each is zero.
        size_bytes = mp3_bytes[6:10]
        try:
            tag_size = (size_bytes[0] << 21) | (size_bytes[1] << 14) | (size_bytes[2] << 7) | size_bytes[3]
            offset = 10 + tag_size
        except Exception:
            offset = 0
    # Scan first frame header (sync = 0xFFE0..0xFFFF).
    for i in range(offset, min(offset + 4096, len(mp3_bytes) - 4)):
        if mp3_bytes[i] == 0xFF and (mp3_bytes[i + 1] & 0xE0) == 0xE0:
            # Parse MPEG audio frame header.
            h1, h2, h3, h4 = mp3_bytes[i], mp3_bytes[i + 1], mp3_bytes[i + 2], mp3_bytes[i + 3]
            version = (h2 >> 3) & 0x03  # 00=2.5, 01=reserved, 10=2, 11=1
            layer = (h2 >> 1) & 0x03    # 01=III, 10=II, 11=I
            bitrate_idx = (h3 >> 4) & 0x0F
            sr_idx = (h3 >> 2) & 0x03
            if bitrate_idx == 0 or bitrate_idx == 0x0F or sr_idx == 0x03:
                continue
            # Bitrate table (MPEG1 Layer III, kbps).
            br_table_v1_l3 = [
                0, 32, 40, 48, 56, 64, 80, 96, 112, 128, 160, 192, 224, 256, 320, 0,
            ]
            sr_table_v1 = [44100, 48000, 32000, 0]
            br = br_table_v1_l3[bitrate_idx] * 1000
            sr = sr_table_v1[sr_idx]
            if br and sr:
                # Frame size = 144 * bitrate / sample_rate + padding.
                padding = (h3 >> 1) & 0x01
                frame_bytes = (144 * br // sr) + padding
                frames = (len(mp3_bytes) - i) // max(frame_bytes, 1)
                duration_s = frames * 0.026  # 1152 samples / 44100 Hz
                return int(round(duration_s * 1000))
            break
    return 0


def _detect_tts_provider(book_dir, locale):
    """Inspect the per-book manifest for the audiobook product's tts_provider."""
    manifest_path = book_dir / "media-locale-manifest.json"
    if not manifest_path.exists():
        raise MediaTtsError("no manifest; cannot detect provider")
    try:
        data = json.loads(manifest_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise MediaTtsError("cannot read manifest: %s" % exc)
    for prod in data.get("products", []):
        if (
            isinstance(prod, dict)
            and prod.get("locale") == locale
            and prod.get("skip") is not True
            and prod.get("tts_provider")
        ):
            return prod["tts_provider"]
    raise MediaTtsError("no audiobook product for locale=%r" % locale)


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------


def _build_parser():
    p = argparse.ArgumentParser(
        prog="media_tts",
        description="Synthesize one (chapter, locale) into an MP3 via Kokoro or edge-tts.",
    )
    p.add_argument(
        "--book", required=True,
        help="Book root (books/<slug>/).",
    )
    p.add_argument(
        "--chapter", required=True,
        help="Chapter id, e.g. ch-01.",
    )
    p.add_argument(
        "--locale", required=True,
        help="Locale code: en, ar, etc.",
    )
    p.add_argument(
        "--out",
        help="Output MP3 path (must resolve under repo root). Default: shares/audio/<slug>/<chapter>-<locale>.mp3.",
    )
    p.add_argument(
        "--tts-provider",
        choices=["kokoro", "edge-tts"],
        help="TTS provider override. Default: read from per-book manifest, "
             "else kokoro for en / edge-tts for ar.",
    )
    return p


def main(argv=None):
    parser = _build_parser()
    args = parser.parse_args(argv)
    try:
        return run_synthesize(
            args.book, args.chapter, args.locale, args.out, args.tts_provider
        )
    except MediaTtsError as exc:
        print("media_tts: %s" % exc, file=sys.stderr)
        return 2
    except MissingDependencyError as exc:
        print("media_tts: %s" % exc, file=sys.stderr)
        return 3
    except RuntimeFailure as exc:
        print("media_tts: %s" % exc, file=sys.stderr)
        return 4


if __name__ == "__main__":
    sys.exit(main())
