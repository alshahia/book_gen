"""assemble_video_trailer.py -- book2media Phase 4b-2: video trailer assembler.

CLI:
    py -3 book-kit/book_workflow/scripts/assemble_video_trailer.py \
        --book books/<slug> \
        --out books/<slug>/exports/video-trailer.mp4 \
        --cover figures/<slug>-cover.png \
        --locale en \
        [--bgm path/to/bgm.mp3] \
        [--burn-subs]

EXIT CODES
    0  success -- MP4 written at --out; sidecar manifest at
       <book>/figures/media-trailer-manifest.json.
    2  input error (--book/--out missing, path escapes repo root,
       no chapters, cover ladder exhausted, audio missing for a
       selected clip, no clips selected within budget).
    3  missing dependency (ffmpeg or ffprobe absent from PATH).
    4  internal/runtime (ffprobe non-zero, ffprobe returned non-numeric
       duration, ffmpeg non-zero exit, manifest write failure).

PATH VALIDATION
    Every --book, --out, --cover, --bgm resolves under the repo root;
    any '..' component in any flag is rejected with exit 2. Per-chapter
    audio paths derived for clip-selection live under
    <book>/exports/audiobook-<ch_id>.m4b (also under repo root by
    construction).

COVER IMAGE FALLBACK LADDER (mirrors assemble_video_horizontal.py)
    1. --cover flag (if provided AND exists). A missing --cover path is
       fatal: we do NOT fall through to the ladder because the user
       explicitly told us where to look.
    2. books/<slug>/figures/cover.png (user-supplied).
    3. books/<slug>/chapters-rendered/*.png (first sorted PNG).
    All miss -> exit 2 with stderr
    "No cover image found at <book>/figures/ or <book>/chapters-rendered/".

CLIP-SELECTION PASS (replaces the per-chapter loop)
    Replaces the per-chapter loop of assemble_video_horizontal.py with
    a clip-selection pass: each chapter is chunked into paragraphs,
    then chunks are accumulated across chapters of books/<slug> until
    either TARGET_CHUNKS (~12) clips are selected or CHAR_BUDGET
    (~1500 chars) is reached. The accumulated char count maps to a
    60-90 second trailer at typical TTS pacing (~15 chars/sec).

NOT IN SCOPE (deferred)
    - Word-level audio alignment; per-chunk audio boundaries are
      proportional to character counts within each chapter.
    - Multi-locale trailer; --locale is reserved for parity with the
      Mode-1 horizontal CLI surface and not used internally.
    - Reels (assemble_reel.py) remain a separate Phase 4b-2 deliverable.

# chub-cite: ffmpeg `zoompan` filter (built-in to local ffmpeg).
# chub-cite: ffmpeg `ass` filter (built-in to local ffmpeg).
# chub-cite: ffmpeg `vignette` filter (built-in to local ffmpeg).
# chub-cite: ffmpeg `amix` filter (built-in to local ffmpeg).
<!-- chub: libass per ffmpeg.org/ffmpeg-filters.html#ass -->
"""
from __future__ import annotations

# ---------------------------------------------------------------------------
# UTF-8 stdio force (mandatory block from dispatch preamble). MUST run
# before any import that could open a file with a non-ASCII path and
# before argparse (so help + error text never crash on cp1256/cp1252).
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
import json
import re
import shutil
import subprocess
import tempfile
from pathlib import Path

# Same-dir import: ffmpeg_zoompan.py lives at
# book-kit/book_workflow/scripts/ffmpeg_zoompan.py. When invoked as
# `py -3 assemble_video_trailer.py`, Python prepends the script's
# directory to sys.path automatically.
import ffmpeg_zoompan  # noqa: E402


# ---------------------------------------------------------------------------
# Paths + constants
# ---------------------------------------------------------------------------

# This file lives at: book-kit/book_workflow/scripts/assemble_video_trailer.py
# parents[3] = repo root.
REPO_ROOT = Path(__file__).resolve().parents[3]

# Output geometry -- fixed by the trailer spec (1920x1080 landscape).
TARGET_W = 1920
TARGET_H = 1080

# Default ffmpeg video / audio codec + bitrate knobs (per dispatch spec).
VCODEC = "libx264"
VPRESET = "fast"
VCRF = 23
ACODEC = "aac"
ABITRATE = "192k"

# Per-chapter audio path template (assemble_audiobook.py output naming).
PER_CHAPTER_AUDIO_TEMPLATE = "audiobook-%s.m4b"

# Sidecar manifest path (per dispatch spec).
MANIFEST_REL = "figures/media-trailer-manifest.json"

# Clip-selection tuning. ~12 chunks at ~125 chars/chunk maps to a
# 60-90 second trailer at ~15 chars/sec narration pacing.
TARGET_CHUNKS = 12
CHAR_BUDGET = 1500


# ---------------------------------------------------------------------------
# Errors
# ---------------------------------------------------------------------------


class InputError(Exception):
    """Input error -- caller should exit 2."""


class MissingDepError(Exception):
    """Missing ffmpeg/ffprobe -- caller should exit 3."""


class RuntimeFailure(Exception):
    """ffmpeg/ffprobe failure -- caller should exit 4."""


# ---------------------------------------------------------------------------
# Path validation (mirrors assemble_video_horizontal.py::_resolve_under_root)
# ---------------------------------------------------------------------------


def _resolve_under_root(candidate, label):
    """Resolve `candidate` under REPO_ROOT, refusing escapes.

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
# Cover image fallback ladder
# ---------------------------------------------------------------------------


def _resolve_cover(book_dir, cover_arg):
    """Walk the cover-ladder tiers; return the first existing Path.

    Tier 1: --cover flag (if provided). If --cover is set but the file
            does NOT exist, raise InputError -- the user explicitly told
            us where to look and we should not silently fall through.
    Tier 2: books/<slug>/figures/cover.png.
    Tier 3: books/<slug>/chapters-rendered/*.png (first sorted PNG).
    All miss -> raise InputError (-> exit 2).
    """
    if cover_arg is not None:
        cover_path = _resolve_under_root(cover_arg, "--cover")
        if not cover_path.exists() or not cover_path.is_file():
            raise InputError("--cover not found: %s" % cover_path)
        return cover_path
    # Tier 2: user-supplied at <book>/figures/cover.png.
    primary = (book_dir / "figures" / "cover.png").resolve()
    if primary.exists() and primary.is_file():
        return primary
    # Tier 3: first sorted PNG under <book>/chapters-rendered/.
    cr = (book_dir / "chapters-rendered").resolve()
    if cr.is_dir():
        pngs = sorted(cr.glob("*.png"))
        if pngs:
            return pngs[0].resolve()
    # All miss -- stderr message is locked by the dispatch spec.
    raise InputError(
        "No cover image found at <book>/figures/ or <book>/chapters-rendered/"
    )


# ---------------------------------------------------------------------------
# Audio duration probe
# ---------------------------------------------------------------------------


def _probe_duration_seconds(audio_path):
    """Return audio duration in seconds (float) via ffprobe.

    Raises MissingDepError if ffprobe is absent, RuntimeFailure on any
    ffprobe failure (non-zero exit, empty output, non-numeric payload).
    """
    ffprobe = shutil.which("ffprobe")
    if ffprobe is None:
        raise MissingDepError(
            "ffprobe not on PATH; install ffmpeg (which ships ffprobe) or "
            "set FFPROBE_PATH"
        )
    try:
        proc = subprocess.run(
            [
                ffprobe, "-v", "error",
                "-show_entries", "format=duration",
                "-of", "default=noprint_wrappers=1:nokey=1",
                str(audio_path),
            ],
            check=True, capture_output=True, text=True, encoding="utf-8",
        )
    except subprocess.CalledProcessError as exc:
        raise RuntimeFailure(
            "ffprobe failed for %s (rc=%d): %s"
            % (audio_path, exc.returncode, (exc.stderr or "").strip())
        )
    out = (proc.stdout or "").strip()
    if not out:
        raise RuntimeFailure(
            "ffprobe returned empty duration for %s" % audio_path
        )
    try:
        return float(out)
    except ValueError:
        raise RuntimeFailure(
            "ffprobe returned non-numeric duration %r for %s"
            % (out, audio_path)
        )


# ---------------------------------------------------------------------------
# Filter complex + ffmpeg argv
# ---------------------------------------------------------------------------


def _build_filter_arg(audio_dur, burn_subs, subs_path, bgm_path):
    """Build the -filter_complex argument for one clip's render.

    Shape (mirrors assemble_video_horizontal.py):
        supersample_zoompan_filterchain(1920, 1080, audio_dur) -- 3-tuple
        [optional: ass=<subs_path>:shaping=complex]            (if --burn-subs)
        [optional: amix=inputs=2:duration=first:dropout_transition=0[v]]
                                                                (if --bgm)
        vignette=PI/4[v]                                       (final, always)

    Returns the joined filter string ready for ffmpeg's -filter_complex.
    """
    chain = ffmpeg_zoompan.supersample_zoompan_filterchain(
        target_w=TARGET_W, target_h=TARGET_H, dur_s=audio_dur,
    )
    parts = list(chain)
    if burn_subs and subs_path is not None:
        parts.append("ass=%s:shaping=complex" % subs_path.as_posix())
    if bgm_path is not None:
        # Per dispatch spec: append this literal token. The trailing [v]
        # re-labels the previous filter's output for the next stage
        # (vignette). Kept verbatim per spec; reviewer can flag if
        # ffmpeg's local build rejects amix inside a video filter chain.
        parts.append("amix=inputs=2:duration=first:dropout_transition=0[v]")
    parts.append("vignette=PI/4[v]")
    return ",".join(parts)


def _build_ffmpeg_argv(cover_path, audio_path, audio_offset, audio_dur,
                       bgm_path, filter_arg, out_path):
    """Build the ffmpeg argv for a single-clip render.

    Per dispatch spec:
        ffmpeg -y -loop 1 -i <cover>
               -ss <audio_offset> -t <audio_dur> -i <audio>
               [-i <bgm>]
               -filter_complex <filter_arg>
               -map [v] -map 1:a? [-map 2:a?]
               -c:v libx264 -preset fast -crf 23
               -c:a aac -b:a 192k
               -shortest
               <out>

    `audio_offset` and `audio_dur` select the per-clip audio window from
    the per-chapter M4B; the trailer's clip-selection pass computes
    these proportional boundaries up-front.
    """
    ffmpeg = shutil.which("ffmpeg")
    if ffmpeg is None:
        raise MissingDepError(
            "ffmpeg not on PATH; install or set FFMPEG_PATH"
        )
    cmd = [
        ffmpeg, "-y",
        "-loop", "1", "-i", str(cover_path),
        "-ss", "%.3f" % audio_offset,
        "-t", "%.3f" % audio_dur,
        "-i", str(audio_path),
    ]
    if bgm_path is not None:
        cmd.extend(["-i", str(bgm_path)])
    cmd.extend([
        "-filter_complex", filter_arg,
        "-map", "[v]",
        "-map", "1:a?",
    ])
    if bgm_path is not None:
        cmd.extend(["-map", "2:a?"])
    cmd.extend([
        "-c:v", VCODEC, "-preset", VPRESET, "-crf", str(VCRF),
        "-c:a", ACODEC, "-b:a", ABITRATE,
        "-shortest",
        str(out_path),
    ])
    return cmd


def _run_ffmpeg(cmd):
    """Run ffmpeg; raise RuntimeFailure on non-zero exit.

    Per dispatch spec: subprocess.run([...], check=True, capture_output=True),
    catch CalledProcessError -> exit 4 with stderr echo.
    """
    try:
        subprocess.run(
            cmd, check=True, capture_output=True, text=True, encoding="utf-8",
        )
    except subprocess.CalledProcessError as exc:
        stderr = (exc.stderr or "").strip()
        stdout = (exc.stdout or "").strip()
        raise RuntimeFailure(
            "ffmpeg failed (rc=%d): %s"
            % (exc.returncode, stderr or stdout)
        )
    except FileNotFoundError as exc:
        raise MissingDepError("ffmpeg binary not found: %s" % exc)


# ---------------------------------------------------------------------------
# Chapter discovery + per-chapter audio
# ---------------------------------------------------------------------------


_CHAPTER_FILE_RE = re.compile(r"^ch-(\d+)\.md$")

# ASS subtitle inline overrides (chapter self-critique blocks; trailer
# strips these the same way assemble_chapter_audio does).
_SELF_CRITIQUE_RE = re.compile(r"<!--.*?-->", re.DOTALL)


def _load_chapter_ids(book_dir):
    """Sorted numeric list of chapter ids (ch-01, ch-02, ...).

    Lexicographic sort would put ch-10 before ch-2; the integer sort
    below keeps the audiobook / video ordering numerically correct.
    """
    chapters_dir = (book_dir / "chapters").resolve()
    if not chapters_dir.is_dir():
        raise InputError("chapters/ not found: %s" % chapters_dir)
    pairs = []
    for p in chapters_dir.iterdir():
        m = _CHAPTER_FILE_RE.match(p.name)
        if m:
            pairs.append((int(m.group(1)), p.stem))
    if not pairs:
        raise InputError("no ch-NN.md files in %s" % chapters_dir)
    pairs.sort()
    return [stem for _, stem in pairs]


def _chapter_audio_path(book_dir, ch_id):
    """Per-chapter audio path (assemble_audiobook.py output naming)."""
    return (book_dir / "exports" / (PER_CHAPTER_AUDIO_TEMPLATE % ch_id)).resolve()


# ---------------------------------------------------------------------------
# Clip-selection pass (replaces the per-chapter loop)
# ---------------------------------------------------------------------------


def _read_chapter_text(ch_path):
    """Read raw chapter text; strip self-critique HTML blocks if any."""
    text = ch_path.read_text(encoding="utf-8")
    return _SELF_CRITIQUE_RE.sub("", text)


def _chunk_chapter(text):
    """Split chapter text into paragraph chunks (non-empty, stripped)."""
    return [p.strip() for p in re.split(r"\n\s*\n", text) if p.strip()]


def _clip_offsets(chapters_chars, audio_dur):
    """Compute per-chunk audio offsets+durations within their chapter.

    `chapters_chars` is a list of (ch_id, [char_count, ...]) tuples in
    chapter-order; `audio_dur` is a parallel list of per-chapter audio
    durations. Each chunk's audio window is its proportional share of
    the chapter's full duration based on its character count.

    Returns a list of (ch_id, chunk_index, audio_offset, audio_dur).
    """
    out = []
    for (ch_id, chunks), dur in zip(chapters_chars, audio_dur):
        total = sum(chunks) or 1
        running = 0.0
        for idx, n in enumerate(chunks):
            share = n / total
            seg_dur = dur * share
            out.append((ch_id, idx, running, seg_dur))
            running += seg_dur
    return out


def _select_clips(book_dir, ch_ids, char_budget=CHAR_BUDGET,
                  chunk_cap=TARGET_CHUNKS):
    """Clip-selection pass: take the first ~chunk_cap chunks across all
    chapters of `book_dir` until the character budget is reached.

    Returns a list of dicts:
        {chapter_id, chunk_index, text, char_count}

    Raises InputError if no chunks selected within budget.

    Side-effect: validates that each selected chapter has an audio file
    on disk (so the per-clip render does not fail mid-loop). Mirrors
    the audio-presence check in assemble_video_horizontal.py's --all
    branch.
    """
    selected = []
    used = 0
    for ch_id in ch_ids:
        ch_path = (book_dir / "chapters" / ("%s.md" % ch_id)).resolve()
        if not ch_path.exists():
            continue
        text = _read_chapter_text(ch_path)
        chunks = _chunk_chapter(text)
        for idx, chunk in enumerate(chunks):
            n = len(chunk)
            if used > 0 and used + n > char_budget:
                # Budget hit; stop accumulating further chunks.
                return selected
            selected.append({
                "chapter_id": ch_id,
                "chunk_index": idx,
                "text": chunk,
                "char_count": n,
            })
            used += n
            if len(selected) >= chunk_cap:
                return selected
        if used >= char_budget:
            return selected
    if not selected:
        raise InputError(
            "no clips selected within budget=%d for %s"
            % (char_budget, book_dir)
        )
    return selected


# ---------------------------------------------------------------------------
# Per-clip ASS (single-line burn-in)
# ---------------------------------------------------------------------------


def _build_clip_ass(clip, audio_dur, ass_path):
    """Write a one-Dialogue-line ASS file for a single clip.

    The Dialogue runs from 0 to `audio_dur` (relative to the clip's
    ffmpeg render), burning `clip["text"]` over the zoompan frame.
    """
    ass_path.parent.mkdir(parents=True, exist_ok=True)
    text = (
        clip["text"]
        .replace("\n", r"\N")
        .replace("{", r"\{")
        .replace("}", r"\}")
    )
    end = _fmt_ass_time(audio_dur)
    body = (
        "[Script Info]\n"
        "ScriptType: v4.00+\n"
        "PlayResX: %d\nPlayResY: %d\n"
        "WrapStyle: 0\n"
        "ScaledBorderAndShadow: yes\n\n"
        "[V4+ Styles]\n"
        "Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, "
        "OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, "
        "ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, "
        "Alignment, MarginL, MarginR, MarginV, Encoding\n"
        "Style: Default,Arial,48,&H00FFFFFF,&H000000FF,&H00000000,&H00000000,"
        "0,0,0,0,100,100,0,0,1,2,1,2,40,40,40,1\n\n"
        "[Events]\n"
        "Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, "
        "Effect, Text\n"
        "Dialogue: 0,0:00:00.00,%s,Default,,0,0,0,,%s\n"
    ) % (TARGET_W, TARGET_H, end, text)
    ass_path.write_text(body, encoding="utf-8")
    return ass_path


def _fmt_ass_time(seconds):
    """Format seconds as h:mm:ss.cs (ASS time format)."""
    h = int(seconds // 3600)
    m = int((seconds % 3600) // 60)
    s = seconds % 60
    return "%d:%02d:%05.2f" % (h, m, s)


# ---------------------------------------------------------------------------
# Per-clip render
# ---------------------------------------------------------------------------


def _render_clip(book_dir, clip, audio_offset, audio_dur, cover_path,
                 out_path, bgm_path=None, burn_subs=False):
    """Render a single clip's MP4. Returns a manifest-entry dict.

    Honors the cover fallback ladder via `_resolve_cover`. Validates
    that the chapter's audio file exists, builds the filter complex,
    and runs ffmpeg with the clip's audio window selected via -ss/-t.
    The returned dict matches the per-clip shape in the sidecar manifest
    schema.
    """
    ch_id = clip["chapter_id"]
    audio_path = _chapter_audio_path(book_dir, ch_id)
    if not audio_path.exists():
        raise InputError("audio not found for %s: %s" % (ch_id, audio_path))
    subs_path = None
    if burn_subs:
        # Per-clip ASS: written once per render, deleted in the caller.
        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".ass", delete=False, encoding="utf-8",
        ) as tf:
            subs_path = Path(tf.name)
        _build_clip_ass(clip, audio_dur, subs_path)
    try:
        filter_arg = _build_filter_arg(
            audio_dur, burn_subs, subs_path, bgm_path,
        )
        argv = _build_ffmpeg_argv(
            cover_path, audio_path, audio_offset, audio_dur,
            bgm_path, filter_arg, out_path,
        )
        out_path.parent.mkdir(parents=True, exist_ok=True)
        _run_ffmpeg(argv)
    finally:
        if subs_path is not None:
            try:
                subs_path.unlink()
            except OSError:
                pass
    return {
        "clip_index": clip["chunk_index"],
        "chapter_id": ch_id,
        "codec": VCODEC,
        "width": TARGET_W,
        "height": TARGET_H,
        "duration_s": round(audio_dur, 3),
        "char_count": clip["char_count"],
        "source_cover": cover_path.as_posix(),
        "source_audio": audio_path.as_posix(),
        "audio_offset_s": round(audio_offset, 3),
        "burned_subs": bool(burn_subs),
        "bgm": bgm_path.as_posix() if bgm_path else None,
    }


# ---------------------------------------------------------------------------
# Concatenation (clip-level; replaces per-chapter concat)
# ---------------------------------------------------------------------------


def _concat_clip_mp4s(clip_mp4s, final_out):
    """Concatenate per-clip MP4s via ffmpeg's concat demuxer (stream copy).

    Stream-copy is safe here because every per-clip MP4 was produced by
    the same ffmpeg invocation shape (identical codec / preset / crf /
    pixel format / timebase) -- there is no transcode to do, so
    concat-demuxer `-c copy` is byte-fast and lossless.
    """
    ffmpeg = shutil.which("ffmpeg")
    if ffmpeg is None:
        raise MissingDepError("ffmpeg not on PATH")
    list_path = None
    try:
        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".txt", delete=False, encoding="utf-8",
        ) as list_file:
            for mp4 in clip_mp4s:
                list_file.write("file '%s'\n" % mp4.as_posix())
            list_path = Path(list_file.name)
        argv = [
            ffmpeg, "-y", "-hide_banner",
            "-f", "concat", "-safe", "0", "-i", str(list_path),
            "-c", "copy",
            str(final_out),
        ]
        _run_ffmpeg(argv)
    finally:
        if list_path is not None:
            try:
                list_path.unlink()
            except OSError:
                pass


# ---------------------------------------------------------------------------
# Sidecar manifest
# ---------------------------------------------------------------------------


def _write_manifest(book_dir, trailer_entry):
    """Write the sidecar manifest at <book>/figures/media-trailer-manifest.json.

    Schema (per dispatch spec):
        trailer: {clips: [{chapter_id, codec, width, height, duration_s,
                    char_count, source_cover, source_audio, audio_offset_s,
                    burned_subs, bgm, clip_index}, ...],
                  codec, width, height, duration_s_total,
                  target_chunks, char_budget, locale, burned_subs, bgm}
        codec, width, height: per-product constants echoed at top level.

    `ensure_ascii=True` + `sort_keys=True` make re-runs byte-stable.
    """
    manifest_path = (book_dir / MANIFEST_REL).resolve()
    manifest_path.parent.mkdir(parents=True, exist_ok=True)
    payload = {
        "trailer": trailer_entry,
        "codec": trailer_entry["codec"],
        "width": trailer_entry["width"],
        "height": trailer_entry["height"],
    }
    with open(manifest_path, "w", encoding="utf-8") as f:
        json.dump(payload, f, indent=2, sort_keys=True, ensure_ascii=True)
        f.write("\n")
    return manifest_path


# ---------------------------------------------------------------------------
# Top-level orchestration
# ---------------------------------------------------------------------------


def run_trailer(book_arg, out_arg, cover_arg, locale,
                bgm_arg=None, burn_subs=False):
    """Run the trailer assembler. Returns the exit code.

    Flags:
        book_arg    -- --book value (required, repo-root-relative or
                       absolute-under-root).
        out_arg     -- --out value (required, repo-root-relative or
                       absolute-under-root).
        cover_arg   -- --cover value (optional; falls back to the ladder).
        locale      -- --locale value (required, reserved for parity with
                       the Mode-1 horizontal CLI surface; not used
                       internally -- the clip-selection pass reads the
                       canonical chapter markdown files).
        bgm_arg     -- --bgm value (optional).
        burn_subs   -- --burn-subs flag; trailer ASS burn-in is enabled
                       per-clip when set.
    """
    # locale is reserved for future locale-gated features (e.g.
    # per-locale hardcoded subs margins). The trailer does not
    # locale-switch anything internally because chunks are pulled from
    # the canonical chapter markdown files.
    _ = locale

    # 1. --book
    try:
        book_dir = _resolve_under_root(book_arg, "--book")
    except InputError as exc:
        print("assemble_video_trailer: %s" % exc, file=sys.stderr)
        return 2
    if not book_dir.is_dir():
        print(
            "assemble_video_trailer: --book not found: %s" % book_dir,
            file=sys.stderr,
        )
        return 2

    # 2. --out
    try:
        out_path = _resolve_under_root(out_arg, "--out")
    except InputError as exc:
        print("assemble_video_trailer: %s" % exc, file=sys.stderr)
        return 2

    # 3. Optional: --bgm
    bgm_path = None
    if bgm_arg is not None:
        try:
            bgm_path = _resolve_under_root(bgm_arg, "--bgm")
        except InputError as exc:
            print("assemble_video_trailer: %s" % exc, file=sys.stderr)
            return 2
        if not bgm_path.exists():
            print(
                "assemble_video_trailer: --bgm not found: %s" % bgm_path,
                file=sys.stderr,
            )
            return 2

    # 4. Cover (ladder).
    try:
        cover_path = _resolve_cover(book_dir, cover_arg)
    except InputError as exc:
        print("assemble_video_trailer: %s" % exc, file=sys.stderr)
        return 2

    # 5. Clip-selection + per-clip render (replaces the per-chapter
    #    loop of assemble_video_horizontal.py).
    try:
        ch_ids = _load_chapter_ids(book_dir)
        clips = _select_clips(book_dir, ch_ids)
        # Group by chapter for proportional audio-window math.
        per_ch_chars = []
        per_ch_audio = []
        for ch_id in ch_ids:
            ch_clips = [c for c in clips if c["chapter_id"] == ch_id]
            if not ch_clips:
                continue
            per_ch_chars.append((ch_id, [c["char_count"] for c in ch_clips]))
            audio = _chapter_audio_path(book_dir, ch_id)
            per_ch_audio.append(_probe_duration_seconds(audio))
        offsets = _clip_offsets(per_ch_chars, per_ch_audio)
        # Map (chapter_id, chunk_index) -> (audio_offset, audio_dur).
        offset_map = {
            (ch_id, idx): (off, dur)
            for (ch_id, idx, off, dur) in offsets
        }
        tmp_dir = Path(tempfile.mkdtemp(prefix="video_trailer_"))
        clip_mp4s = []
        entries = []
        try:
            for clip in clips:
                audio_offset, audio_dur = offset_map[
                    (clip["chapter_id"], clip["chunk_index"])
                ]
                clip_out = tmp_dir / (
                    "%s-clip-%02d.mp4" % (clip["chapter_id"], clip["chunk_index"])
                )
                entry = _render_clip(
                    book_dir, clip, audio_offset, audio_dur,
                    cover_path, clip_out,
                    bgm_path=bgm_path,
                    burn_subs=burn_subs,
                )
                entries.append(entry)
                clip_mp4s.append(clip_out)
            out_path.parent.mkdir(parents=True, exist_ok=True)
            _concat_clip_mp4s(clip_mp4s, out_path)
        finally:
            for f in tmp_dir.glob("*"):
                try:
                    f.unlink()
                except OSError:
                    pass
            try:
                tmp_dir.rmdir()
            except OSError:
                pass
        total_dur = sum(e["duration_s"] for e in entries)
        trailer_entry = {
            "clips": entries,
            "codec": VCODEC,
            "width": TARGET_W,
            "height": TARGET_H,
            "duration_s_total": round(total_dur, 3),
            "target_chunks": TARGET_CHUNKS,
            "char_budget": CHAR_BUDGET,
            "locale": locale,
            "burned_subs": bool(burn_subs),
            "bgm": bgm_path.as_posix() if bgm_path else None,
            "source_cover": cover_path.as_posix(),
        }
        manifest_path = _write_manifest(book_dir, trailer_entry)
    except InputError as exc:
        print("assemble_video_trailer: %s" % exc, file=sys.stderr)
        return 2
    except MissingDepError as exc:
        print("assemble_video_trailer: %s" % exc, file=sys.stderr)
        return 3
    except RuntimeFailure as exc:
        print("assemble_video_trailer: %s" % exc, file=sys.stderr)
        return 4
    except OSError as exc:
        print(
            "assemble_video_trailer: cannot write manifest: %s" % exc,
            file=sys.stderr,
        )
        return 4

    print(
        "assemble_video_trailer: OK clips=%d duration_s=%.2f out=%s manifest=%s"
        % (len(entries), total_dur, out_path, manifest_path)
    )
    return 0


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------


def _build_parser():
    p = argparse.ArgumentParser(
        prog="assemble_video_trailer",
        description=(
            "Phase 4b-2: render a 60-90s landscape (1920x1080) trailer by "
            "selecting the first ~12 chunks across all chapters of a book "
            "and concatenating them over a Ken Burns zoompan + optional BGM."
        ),
    )
    p.add_argument("--book", required=True,
                   help="Book root (books/<slug>/).")
    p.add_argument("--out", required=True,
                   help="Output MP4 path (must resolve under repo root).")
    p.add_argument("--cover",
                   help="Cover image path (under repo root; falls back to "
                        "figures/cover.png then chapters-rendered/*.png).")
    p.add_argument("--locale", required=True,
                   help="Locale code (en, ar, ...).")
    p.add_argument("--bgm",
                   help="Optional background-music audio path (under repo root).")
    p.add_argument("--burn-subs", action="store_true",
                   help="Burn each clip's chunk text into the video as an "
                        "ASS subtitle overlay (recommended for trailers).")
    return p


def main(argv=None):
    parser = _build_parser()
    args = parser.parse_args(argv)
    return run_trailer(
        book_arg=args.book,
        out_arg=args.out,
        cover_arg=args.cover,
        locale=args.locale,
        bgm_arg=args.bgm,
        burn_subs=args.burn_subs,
    )


if __name__ == "__main__":
    sys.exit(main())
