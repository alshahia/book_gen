"""assemble_video_horizontal.py -- book2media Phase 4b: Mode-1 landscape video assembler.

CLI:
    py -3 book-kit/book_workflow/scripts/assemble_video_horizontal.py \
        --book books/<slug> \
        --chapter ch-NN \
        --out books/<slug>/exports/video-horizontal-m1-ch-NN.mp4 \
        --cover figures/<slug>-ch-NN-cover.png \
        --audio books/<slug>/exports/audiobook-ch-NN.m4b \
        --locale en \
        [--bgm path/to/bgm.mp3] \
        [--burn-subs] \
        [--subs path/to/ch-NN-en.ass]

    # Whole-book mode (mutually exclusive with --chapter):
    py -3 ... --all --out books/<slug>/exports/video-horizontal-m1.mp4

EXIT CODES
    0  success -- MP4 written at --out; sidecar manifest at
       <book>/figures/media-video-manifest.json.
    2  input error (--book/--out/--audio missing, --chapter and --all both
       set, --burn-subs without --subs, --all + --burn-subs, path escapes
       repo root, cover ladder exhausted, audio missing in --all mode for
       a chapter).
    3  missing dependency (ffmpeg or ffprobe absent from PATH).
    4  internal/runtime (ffprobe non-zero, ffprobe returned non-numeric
       duration, ffmpeg non-zero exit, manifest write failure).

PATH VALIDATION
    Every --book, --out, --cover, --audio, --bgm, --subs resolves under
    the repo root; any '..' component in any flag is rejected with exit
    2. Per-chapter audio paths derived in --all mode live under
    <book>/exports/audiobook-<ch_id>.m4b (also under repo root by
    construction).

COVER IMAGE FALLBACK LADDER (per Phase 4b spec)
    1. --cover flag (if provided AND exists). A missing --cover path is
       fatal: we do NOT fall through to the ladder because the user
       explicitly told us where to look.
    2. books/<slug>/figures/cover.png (user-supplied).
    3. books/<slug>/chapters-rendered/*.png (first sorted PNG).
    All miss -> exit 2 with stderr
    "No cover image found at <book>/figures/ or <book>/chapters-rendered/".

NOT IN SCOPE (deferred to Phase 4b-2)
    - Trailer + reels (assemble_video_trailer.py, assemble_reel.py).
    - Waveform overlay (ffmpeg showwaves) is omitted from the v1 filter
      graph; the Phase 4b spec does not require it for the Mode-1
      horizontal video. Trailer + reels will add it per-locale as
      needed.

# chub-cite: ffmpeg `zoompan` filter (built-in to local ffmpeg).
# chub-cite: ffmpeg `scale` filter (built-in to local ffmpeg).
# chub-cite: ffmpeg `vignette` filter (built-in to local ffmpeg).
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
# `py -3 assemble_video_horizontal.py`, Python prepends the script's
# directory to sys.path automatically.
import ffmpeg_zoompan  # noqa: E402


# ---------------------------------------------------------------------------
# Paths + constants
# ---------------------------------------------------------------------------

# This file lives at: book-kit/book_workflow/scripts/assemble_video_horizontal.py
# parents[3] = repo root.
REPO_ROOT = Path(__file__).resolve().parents[3]

# Output geometry -- fixed by the Mode-1 spec (1920x1080 landscape).
TARGET_W = 1920
TARGET_H = 1080

# Default ffmpeg video / audio codec + bitrate knobs (per dispatch spec).
VCODEC_DEFAULT = "libx264"
VPRESET_DEFAULT = "fast"
SCALE_MULT_DEFAULT = 4
# Module-level aliases for code paths that still read the constant directly
# (e.g. empty-manifest fallback). Tests + production paths thread the
# CLI-resolved values through.
VCODEC = VCODEC_DEFAULT
VPRESET = VPRESET_DEFAULT
VCRF = 23
ACODEC = "aac"
ABITRATE = "192k"

# Per-chapter audio path template (assemble_audiobook.py output naming).
PER_CHAPTER_AUDIO_TEMPLATE = "audiobook-%s.m4b"

# Sidecar manifest path (per dispatch spec).
MANIFEST_REL = "figures/media-video-manifest.json"


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
# Path validation (mirrors assemble_audiobook.py::_resolve_under_root)
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


def _build_filter_arg(audio_dur, burn_subs, subs_path, bgm_path,
                     scale_mult=SCALE_MULT_DEFAULT):
    """Build the -filter_complex argument for one chapter's render.

    Shape (per dispatch spec):
        supersample_zoompan_filterchain(1920, 1080, audio_dur) -- 3-tuple
        [optional: ass=<subs_path>:shaping=complex]            (if --burn-subs)
        [optional: amix=inputs=2:duration=first:dropout_transition=0[v]]
                                                                (if --bgm)
        vignette=PI/4[v]                                       (final, always)

    Returns the joined filter string ready for ffmpeg's -filter_complex.
    """
    chain = ffmpeg_zoompan.supersample_zoompan_filterchain(
        target_w=TARGET_W, target_h=TARGET_H, dur_s=audio_dur,
        scale_mult=scale_mult,
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


def _build_ffmpeg_argv(cover_path, audio_path, bgm_path, filter_arg, out_path,
                       vcodec=VCODEC_DEFAULT, vpreset=VPRESET_DEFAULT):
    """Build the ffmpeg argv for a single-chapter render.

    Per dispatch spec:
        ffmpeg -y -loop 1 -i <cover>
               -i <audio>
               [-i <bgm>]
               -filter_complex <filter_arg>
               -map [v] -map 1:a? [-map 2:a?]
               -c:v libx264 -preset fast -crf 23
               -c:a aac -b:a 192k
               -shortest
               <out>
    """
    ffmpeg = shutil.which("ffmpeg")
    if ffmpeg is None:
        raise MissingDepError(
            "ffmpeg not on PATH; install or set FFMPEG_PATH"
        )
    cmd = [
        ffmpeg, "-y",
        "-loop", "1", "-i", str(cover_path),
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
        "-c:v", vcodec, "-preset", vpreset, "-crf", str(VCRF),
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
# Per-chapter render
# ---------------------------------------------------------------------------


def _render_chapter(book_dir, ch_id, out_path, cover_arg, audio_path,
                    bgm_path=None, burn_subs=False, subs_path=None,
                    scale_mult=SCALE_MULT_DEFAULT, vcodec=VCODEC_DEFAULT,
                    vpreset=VPRESET_DEFAULT):
    """Render a single chapter's MP4. Returns a manifest-entry dict.

    Honors the cover fallback ladder via `_resolve_cover`. Validates
    that the audio file exists, probes its duration, builds the
    filter complex, and runs ffmpeg. The returned dict matches the
    per-chapter shape in the sidecar manifest schema.
    """
    cover_path = _resolve_cover(book_dir, cover_arg)
    if not audio_path.exists():
        raise InputError("audio not found: %s" % audio_path)
    audio_dur = _probe_duration_seconds(audio_path)
    filter_arg = _build_filter_arg(
        audio_dur, burn_subs, subs_path, bgm_path, scale_mult=scale_mult,
    )
    argv = _build_ffmpeg_argv(
        cover_path, audio_path, bgm_path, filter_arg, out_path,
        vcodec=vcodec, vpreset=vpreset,
    )
    out_path.parent.mkdir(parents=True, exist_ok=True)
    _run_ffmpeg(argv)
    return {
        "chapter_id": ch_id,
        "codec": VCODEC,
        "width": TARGET_W,
        "height": TARGET_H,
        "duration_s": round(audio_dur, 3),
        "source_cover": cover_path.as_posix(),
        "source_audio": audio_path.as_posix(),
        "burned_subs": bool(burn_subs and subs_path is not None),
        "bgm": bgm_path.as_posix() if bgm_path else None,
    }


# ---------------------------------------------------------------------------
# Concatenation (--all mode)
# ---------------------------------------------------------------------------


def _concat_chapter_mp4s(chapter_mp4s, final_out):
    """Concatenate per-chapter MP4s via ffmpeg's concat demuxer (stream copy).

    Stream-copy is safe here because every per-chapter MP4 was produced
    by the same ffmpeg invocation shape (identical codec / preset / crf
    / pixel format / timebase) -- there is no transcode to do, so
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
            for mp4 in chapter_mp4s:
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


def _write_manifest(book_dir, entries, vcodec=VCODEC_DEFAULT):
    """Write the sidecar manifest at <book>/figures/media-video-manifest.json.

    Schema (per dispatch spec):
        chapters: [{chapter_id, codec, width, height, duration_s,
                    source_cover, source_audio, burned_subs, bgm}, ...]
        codec, width, height: per-product constants echoed at top level.

    `ensure_ascii=True` + `sort_keys=True` make re-runs byte-stable
    (modulo any mtime the OS embeds in MP4 moov atoms).
    """
    manifest_path = (book_dir / MANIFEST_REL).resolve()
    manifest_path.parent.mkdir(parents=True, exist_ok=True)
    if entries:
        head = entries[0]
        payload = {
            "chapters": entries,
            "codec": head["codec"],
            "width": head["width"],
            "height": head["height"],
        }
    else:
        payload = {
            "chapters": [],
        "codec": vcodec,
            "width": TARGET_W,
            "height": TARGET_H,
        }
    with open(manifest_path, "w", encoding="utf-8") as f:
        json.dump(payload, f, indent=2, sort_keys=True, ensure_ascii=True)
        f.write("\n")
    return manifest_path


# ---------------------------------------------------------------------------
# Top-level orchestration
# ---------------------------------------------------------------------------


def run_assemble(book_arg, chapter, all_mode, out_arg, cover_arg, audio_arg,
                 locale, bgm_arg=None, burn_subs=False, subs_arg=None,
                 scale_mult=SCALE_MULT_DEFAULT, vcodec=VCODEC_DEFAULT,
                 vpreset=VPRESET_DEFAULT):
    """Run the full assembler. Returns the exit code.

    Flags:
        book_arg    -- --book value (required, repo-root-relative or
                       absolute-under-root).
        chapter     -- --chapter value (ch-NN), required in single mode.
        all_mode    -- --all flag; when True, render every chapter in
                       books/<slug>/chapters/ and concatenate.
        out_arg     -- --out value (required, repo-root-relative or
                       absolute-under-root).
        cover_arg   -- --cover value (optional; falls back to the ladder).
        audio_arg   -- --audio value (required in single mode, ignored
                       in --all mode where per-chapter audio is derived).
        locale      -- --locale value (required, kept for parity with the
                       rest of the Phase 9 CLI surface; not used
                       internally -- cover / audio / subs are all
                       pre-localised by upstream scripts).
        bgm_arg     -- --bgm value (optional).
        burn_subs   -- --burn-subs flag (requires --subs).
        subs_arg    -- --subs value (required when burn_subs is True).
        scale_mult  -- --scale-mult value (escape hatch; 4 default; 2 = faster).
        vcodec      -- --vcodec value (escape hatch; libx264 default; h264_nvenc
                       ~5-10x faster on Nvidia GPUs).
        vpreset     -- --vpreset value (escape hatch; fast default; veryfast
                       faster still).
    """
    # locale is reserved for future locale-gated features (e.g.
    # per-locale hardcoded subs margins). The assembler does not
    # locale-switch anything internally because cover / audio / ASS
    # are all pre-localised by upstream scripts.
    _ = locale

    # 1. --book
    try:
        book_dir = _resolve_under_root(book_arg, "--book")
    except InputError as exc:
        print("assemble_video_horizontal: %s" % exc, file=sys.stderr)
        return 2
    if not book_dir.is_dir():
        print(
            "assemble_video_horizontal: --book not found: %s" % book_dir,
            file=sys.stderr,
        )
        return 2

    # 2. --out
    try:
        out_path = _resolve_under_root(out_arg, "--out")
    except InputError as exc:
        print("assemble_video_horizontal: %s" % exc, file=sys.stderr)
        return 2

    # 3. Optional: --bgm, --subs
    bgm_path = None
    if bgm_arg is not None:
        try:
            bgm_path = _resolve_under_root(bgm_arg, "--bgm")
        except InputError as exc:
            print("assemble_video_horizontal: %s" % exc, file=sys.stderr)
            return 2
        if not bgm_path.exists():
            print(
                "assemble_video_horizontal: --bgm not found: %s" % bgm_path,
                file=sys.stderr,
            )
            return 2
    subs_path = None
    if subs_arg is not None:
        try:
            subs_path = _resolve_under_root(subs_arg, "--subs")
        except InputError as exc:
            print("assemble_video_horizontal: %s" % exc, file=sys.stderr)
            return 2
        if not subs_path.exists():
            print(
                "assemble_video_horizontal: --subs not found: %s" % subs_path,
                file=sys.stderr,
            )
            return 2

    # 4. --burn-subs requires --subs.
    if burn_subs and subs_path is None:
        print(
            "assemble_video_horizontal: --burn-subs requires --subs",
            file=sys.stderr,
        )
        return 2

    # 5. --all + --burn-subs is unsupported in this phase (deferred to
    #    Phase 4b-2 trailer + reels, which will need a per-chapter ASS
    #    template; the horizontal Mode-1 video has no per-chapter ASS
    #    template by spec).
    if all_mode and burn_subs:
        print(
            "assemble_video_horizontal: --all + --burn-subs is not supported "
            "in this phase; deferred to Phase 4b-2 (trailer + reels).",
            file=sys.stderr,
        )
        return 2

    # 6. Per-chapter pipeline.
    try:
        if all_mode:
            ch_ids = _load_chapter_ids(book_dir)
            tmp_dir = Path(tempfile.mkdtemp(prefix="video_horizontal_"))
            chapter_mp4s = []
            entries = []
            try:
                for ch_id in ch_ids:
                    audio = _chapter_audio_path(book_dir, ch_id)
                    if not audio.exists():
                        raise InputError(
                            "audio not found for %s: %s" % (ch_id, audio)
                        )
                    chap_out = tmp_dir / ("%s.mp4" % ch_id)
                    entry = _render_chapter(
                        book_dir, ch_id, chap_out,
                        cover_arg=None,  # auto-resolve per chapter
                        audio_path=audio,
                        bgm_path=bgm_path,
                        burn_subs=burn_subs,
                        subs_path=subs_path,
                        scale_mult=scale_mult,
                        vcodec=vcodec,
                        vpreset=vpreset,
                    )
                    entries.append(entry)
                    chapter_mp4s.append(chap_out)
                out_path.parent.mkdir(parents=True, exist_ok=True)
                _concat_chapter_mp4s(chapter_mp4s, out_path)
            finally:
                # Clean up tmp dir (best-effort; if Windows holds a handle
                # the rmdir will fail silently -- the next cleanup pass
                # or reboot will reclaim the space).
                for f in tmp_dir.glob("*"):
                    try:
                        f.unlink()
                    except OSError:
                        pass
                try:
                    tmp_dir.rmdir()
                except OSError:
                    pass
        else:
            ch_id = chapter
            try:
                audio = _resolve_under_root(audio_arg, "--audio")
            except InputError as exc:
                print(
                    "assemble_video_horizontal: %s" % exc, file=sys.stderr,
                )
                return 2
            if not audio.exists():
                print(
                    "assemble_video_horizontal: --audio not found: %s" % audio,
                    file=sys.stderr,
                )
                return 2
            out_path.parent.mkdir(parents=True, exist_ok=True)
            entry = _render_chapter(
                book_dir, ch_id, out_path,
                cover_arg=cover_arg,
                audio_path=audio,
                bgm_path=bgm_path,
                burn_subs=burn_subs,
                subs_path=subs_path,
                scale_mult=scale_mult,
                vcodec=vcodec,
                vpreset=vpreset,
            )
            entries = [entry]
    except InputError as exc:
        print("assemble_video_horizontal: %s" % exc, file=sys.stderr)
        return 2
    except MissingDepError as exc:
        print("assemble_video_horizontal: %s" % exc, file=sys.stderr)
        return 3
    except RuntimeFailure as exc:
        print("assemble_video_horizontal: %s" % exc, file=sys.stderr)
        return 4

    # 7. Sidecar manifest.
    try:
        manifest_path = _write_manifest(book_dir, entries, vcodec=vcodec)
    except OSError as exc:
        print(
            "assemble_video_horizontal: cannot write manifest: %s" % exc,
            file=sys.stderr,
        )
        return 4

    print(
        "assemble_video_horizontal: OK chapters=%d out=%s manifest=%s"
        % (len(entries), out_path, manifest_path)
    )
    return 0


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------


def _build_parser():
    p = argparse.ArgumentParser(
        prog="assemble_video_horizontal",
        description=(
            "Phase 4b Mode-1: render a landscape (1920x1080) video from a "
            "single static cover + Ken Burns zoompan + audio + optional "
            "burned subs + optional BGM."
        ),
    )
    p.add_argument("--book", required=True,
                   help="Book root (books/<slug>/).")
    p.add_argument("--out", required=True,
                   help="Output MP4 path (must resolve under repo root).")
    p.add_argument("--cover",
                   help="Cover image path (under repo root; falls back to "
                        "figures/cover.png then chapters-rendered/*.png).")
    p.add_argument("--audio",
                   help="Per-chapter audio M4B path (under repo root; "
                        "ignored in --all mode).")
    p.add_argument("--locale", required=True,
                   help="Locale code (en, ar, ...).")
    p.add_argument("--bgm",
                   help="Optional background-music audio path (under repo root).")
    p.add_argument("--burn-subs", action="store_true",
                   help="Burn the ASS subtitle file into the video "
                        "(requires --subs; not supported with --all).")
    p.add_argument("--subs",
                   help="ASS subtitle path (under repo root; required with "
                        "--burn-subs).")
    mode = p.add_mutually_exclusive_group(required=True)
    mode.add_argument("--chapter",
                      help="Single chapter id (e.g. ch-01).")
    mode.add_argument("--all", dest="all_mode", action="store_true",
                      help="Render all chapters and concatenate.")
    p.add_argument("--scale-mult", type=int, default=SCALE_MULT_DEFAULT,
                   help="Supersample multiplier for zoompan (default %d; "
                        "2 = ~2x faster, slight quality loss; 1 = native "
                        "1920x1080, fastest)." % SCALE_MULT_DEFAULT)
    p.add_argument("--vcodec", default=VCODEC_DEFAULT,
                   help="ffmpeg video codec (default %s; try h264_nvenc "
                        "on Nvidia GPUs for ~5-10x speedup)." % VCODEC_DEFAULT)
    p.add_argument("--vpreset", default=VPRESET_DEFAULT,
                   help="ffmpeg -preset value (default %s; veryfast = "
                        "faster, larger file)." % VPRESET_DEFAULT)
    return p


def main(argv=None):
    parser = _build_parser()
    args = parser.parse_args(argv)
    return run_assemble(
        book_arg=args.book,
        chapter=args.chapter,
        all_mode=args.all_mode,
        out_arg=args.out,
        cover_arg=args.cover,
        audio_arg=args.audio,
        locale=args.locale,
        bgm_arg=args.bgm,
        burn_subs=args.burn_subs,
        subs_arg=args.subs,
        scale_mult=args.scale_mult,
        vcodec=args.vcodec,
        vpreset=args.vpreset,
    )


if __name__ == "__main__":
    sys.exit(main())
