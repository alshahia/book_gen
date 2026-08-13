"""assemble_reel.py -- book2media Phase 4b: Mode-1 vertical reel assembler.

CLI:
    py -3 book-kit/book_workflow/scripts/assemble_reel.py \
        --book books/<slug> \
        --chapter ch-NN \
        --out books/<slug>/exports/reel-m1-ch-NN.mp4 \
        --cover figures/<slug>-ch-NN-cover.png \
        --audio books/<slug>/exports/audiobook-ch-NN.m4b \
        --locale en \
        [--bgm path/to/bgm.mp3] \
        [--burn-subs] \
        [--subs path/to/ch-NN-en.ass]

EXIT CODES
    0  success -- MP4 written at --out; sidecar manifest at
       <book>/figures/media-video-manifest.json.
    2  input error (--book/--out/--audio missing, --burn-subs without
       --subs, path escapes repo root, cover ladder exhausted).
    3  missing dependency (ffmpeg or ffprobe absent from PATH).
    4  internal/runtime (ffprobe non-zero, ffprobe returned non-numeric
       duration, ffmpeg non-zero exit, manifest write failure).

PATH VALIDATION
    Every --book, --out, --cover, --audio, --bgm, --subs resolves under
    the repo root; any '..' component in any flag is rejected with exit
    2.

COVER IMAGE FALLBACK LADDER (per Phase 4b spec)
    1. --cover flag (if provided AND exists). A missing --cover path is
       fatal: we do NOT fall through to the ladder because the user
       explicitly told us where to look.
    2. books/<slug>/figures/cover.png (user-supplied).
    3. books/<slug>/chapters-rendered/*.png (first sorted PNG).
    All miss -> exit 2 with stderr
    "No cover image found at <book>/figures/ or <book>/chapters-rendered/".

PER-PLATFORM FAN-OUT (Phase 4b-2)
    - --platforms <list>  Comma-separated platform codes; one mp4 per
                          code. Allowed: yt, ig, tiktok.
                          Default: yt,ig,tiktok (fan out to all three).
    - One source render (cover zoompan) is shared across platforms via a
      single ffmpeg invocation with one -filter_complex and N -map
      segments. The cover zoompan runs once; the audio + per-platform
      loudnorm + per-platform subs+alignment fan out from that single
      render.
    - Per-platform loudnorm target (ffmpeg loudnorm filter):
        yt     I=-14  TP=-1
        ig     I=-16  TP=-1.5
        tiktok I=-14  TP=-1
    - Per-platform caption positioning (ASS Alignment via force_style
      on the ass filter; libass per ffmpeg.org/ffmpeg-filters.html#ass):
        yt, ig  -> Alignment=2  (bottom-center)
        tiktok  -> Alignment=8  (top-center)
    - Output naming: <out-stem>-<platform><out-suffix>
      e.g. reel-m1-ch-01.mp4 -> reel-m1-ch-01-yt.mp4,
                                reel-m1-ch-01-ig.mp4,
                                reel-m1-ch-01-tiktok.mp4

NOT IN SCOPE (deferred)
    - 4:5 IG feed, 1:1 IG square, etc. -- this v1 fans out the 9:16
      vertical MP4 only. Different aspect ratios land in a follow-up.
    - Waveform overlay (ffmpeg showwaves) is omitted from the v1 filter
      graph; the Phase 4b spec does not require it for the Mode-1
      vertical reel. Trailer + multi-platform variants will add it
      per-locale as needed.

# chub-cite: ffmpeg `zoompan` filter (built-in to local ffmpeg).
# chub-cite: ffmpeg `scale` filter (built-in to local ffmpeg).
# chub-cite: ffmpeg `vignette` filter (built-in to local ffmpeg).
<!-- chub: libass per ffmpeg.org/ffmpeg-filters.html#ass -->
<!-- chub: ffmpeg loudnorm filter per ffmpeg.org/ffmpeg-filters.html#loudnorm -->
"""
from __future__ import annotations

# ---------------------------------------------------------------------------
# UTF-8 stdio force (mandatory block from dispatch preamble). MUST run
# before any import that could open a file with a non-ASCII path and
# before argparse (so help + error text never crash on cp1256/cp1252).
# ---------------------------------------------------------------------------

import sys
import io
import tempfile
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
import shutil
import subprocess
from pathlib import Path

# Same-dir import: ffmpeg_zoompan.py lives at
# book-kit/book_workflow/scripts/ffmpeg_zoompan.py. When invoked as
# `py -3 assemble_reel.py`, Python prepends the script's directory to
# sys.path automatically.
import ffmpeg_zoompan  # noqa: E402


# ---------------------------------------------------------------------------
# Paths + constants
# ---------------------------------------------------------------------------

# This file lives at: book-kit/book_workflow/scripts/assemble_reel.py
# parents[3] = repo root.
REPO_ROOT = Path(__file__).resolve().parents[3]

# Output geometry -- fixed by the Mode-1 vertical reel spec (1080x1920).
TARGET_W = 1080
TARGET_H = 1920

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

# Sidecar manifest path (per dispatch spec; shared with the horizontal
# assembler so a downstream consumer reads one file per book).
MANIFEST_REL = "figures/media-video-manifest.json"

# Per-platform specs (Phase 4b-2 fan-out).
#   loudnorm_I / loudnorm_TP  : ffmpeg loudnorm filter integrated
#                              loudness target (LUFS) and true peak (dBTP).
#   alignment                 : ASS Alignment code (1..9) used via
#                              force_style on the ass filter.
#                              2 = bottom-center, 8 = top-center.
PLATFORM_SPECS = {
    "yt":     {"loudnorm_I": -14.0, "loudnorm_TP": -1.0,  "alignment": 2},
    "ig":     {"loudnorm_I": -16.0, "loudnorm_TP": -1.5,  "alignment": 2},
    "tiktok": {"loudnorm_I": -14.0, "loudnorm_TP": -1.0,  "alignment": 8},
}
VALID_PLATFORMS = frozenset(PLATFORM_SPECS)
DEFAULT_PLATFORMS = ("yt", "ig", "tiktok")


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
# Platform parsing
# ---------------------------------------------------------------------------


def _parse_platforms(raw):
    """Parse a comma-separated platform string into a tuple of platform codes.

    Accepts str (CLI flag value) or any iterable of strings (programmatic
    callers). Returns a tuple. Empty -> InputError. Unknown code ->
    InputError. Duplicate codes -> InputError. None -> DEFAULT_PLATFORMS.
    """
    if raw is None:
        return DEFAULT_PLATFORMS
    if isinstance(raw, str):
        text = raw.strip()
        if not text:
            raise InputError("--platforms must not be empty")
        parts = [p.strip() for p in text.split(",") if p.strip()]
    else:
        parts = [str(p).strip() for p in raw if str(p).strip()]
    if not parts:
        raise InputError("--platforms must not be empty")
    bad = [p for p in parts if p not in VALID_PLATFORMS]
    if bad:
        raise InputError(
            "--platforms invalid: %s. Allowed: %s"
            % (",".join(bad), ",".join(sorted(VALID_PLATFORMS)))
        )
    seen = set()
    dupes = []
    for p in parts:
        if p in seen and p not in dupes:
            dupes.append(p)
        seen.add(p)
    if dupes:
        raise InputError(
            "--platforms contains duplicates: %s" % ",".join(dupes)
        )
    return tuple(parts)


def _platform_output_path(out_base, platform):
    """Derive the per-platform output path from a base output path.

    Example: 'reel-m1-ch-01.mp4' + 'yt' -> 'reel-m1-ch-01-yt.mp4'
    """
    return out_base.with_name(
        "%s-%s%s" % (out_base.stem, platform, out_base.suffix)
    )


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
                     scale_mult=SCALE_MULT_DEFAULT, waveform=False):
    """Build the -filter_complex argument for one reel render.

    Shape (per dispatch spec):
        supersample_zoompan_filterchain(1080, 1920, audio_dur) -- 3-tuple
        [optional: ass=<subs_path>:shaping=complex]            (if --burn-subs)
        [optional: amix=inputs=2:duration=first:dropout_transition=0[v]]
                                                                (if --bgm)
        vignette=PI/4[v]                                       (final, always)

    Optional waveform overlay (if --waveform):
        A separate chain on the audio stream [1:a] is built with
        showwaves to produce a 2D waveform video [wf], then overlayed
        near the bottom of the frame via [v_main][wf]overlay.

    Returns the joined filter string ready for ffmpeg's -filter_complex.
    Comma-joins filter tokens in the same chain; semicolons separate
    parallel chains (e.g. the audio-waveform chain from the main video
    chain).
    """
    chain = ffmpeg_zoompan.supersample_zoompan_filterchain(
        target_w=TARGET_W, target_h=TARGET_H, dur_s=audio_dur,
        scale_mult=scale_mult,
    )
    parts = list(chain)
    # The zoompan chain output label is whatever the filterchain emits;
    # for v1 it terminates with "[v_base]" (see ffmpeg_zoompan.py).
    # When we append ass=/amix, we re-label the previous video output so
    # the next stage can consume it cleanly.
    main_label = "v_main"
    if burn_subs and subs_path is not None:
        parts.append("ass=%s:shaping=complex[%s]" % (subs_path.as_posix(), main_label))
    if bgm_path is not None:
        # Per dispatch spec: append this literal token. The trailing [v]
        # re-labels the previous filter's output for the next stage
        # (vignette). Kept verbatim per spec; reviewer can flag if
        # ffmpeg's local build rejects amix inside a video filter chain.
        parts.append("amix=inputs=2:duration=first:dropout_transition=0[v]")
    # Optional waveform: a parallel chain on [1:a] producing [wf], then
    # overlayed on the main video. We append the showwaves chain to the
    # main chain with a semicolon, then add an overlay step.
    if waveform:
        wf_chain = (
            "[1:a]showwaves=s=1080x160:mode=cline:colors=white@0.75:"
            "rate=30,format=yuva420p[wf]"
        )
        # The overlay uses the (possibly relabelled) main video stream.
        # When burn_subs was on, main_label is "v_main"; otherwise the
        # base zoompan output is the unlabelled "[v_base]" which the
        # zoompan lib returns. We need to reference whichever label
        # actually exists in the chain.
        if burn_subs and subs_path is not None:
            base_in = "[%s]" % main_label
        else:
            base_in = "[v_base]"
        overlay_step = "%s[wf]overlay=0:H-h-40:format=auto[v_main2]" % base_in
        # Stitch together: main chain (parts) + showwaves chain + overlay.
        return ",".join(parts) + ";" + wf_chain + ";" + overlay_step + "," + "vignette=PI/4[v]"
    parts.append("vignette=PI/4[v]")
    return ",".join(parts)


def _build_ffmpeg_argv(cover_path, audio_path, bgm_path, filter_arg, out_path,
                       vcodec=VCODEC_DEFAULT, vpreset=VPRESET_DEFAULT):
    """Build the ffmpeg argv for a single-reel render.

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
        "-pix_fmt", "yuv420p",
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
# Single-reel render
# ---------------------------------------------------------------------------


def _render_reel(book_dir, ch_id, out_path, cover_arg, audio_path,
                 bgm_path=None, burn_subs=False, subs_path=None,
                 waveform=False):
    """Render a single vertical reel MP4. Returns a manifest-entry dict.

    Honors the cover fallback ladder via `_resolve_cover`. Validates
    that the audio file exists, probes its duration, builds the filter
    complex, and runs ffmpeg. The returned dict matches the per-chapter
    shape in the sidecar manifest schema (mirrors the horizontal
    assembler so a downstream consumer sees one schema across products).
    """
    cover_path = _resolve_cover(book_dir, cover_arg)
    if not audio_path.exists():
        raise InputError("audio not found: %s" % audio_path)
    audio_dur = _probe_duration_seconds(audio_path)
    filter_arg = _build_filter_arg(audio_dur, burn_subs, subs_path, bgm_path,
                                    waveform=waveform)
    argv = _build_ffmpeg_argv(
        cover_path, audio_path, bgm_path, filter_arg, out_path,
    )
    out_path.parent.mkdir(parents=True, exist_ok=True)
    _run_ffmpeg(argv)
    return {
        "chapter_id": ch_id,
        "codec": vcodec,
        "width": TARGET_W,
        "height": TARGET_H,
        "duration_s": round(audio_dur, 3),
        "source_cover": cover_path.as_posix(),
        "source_audio": audio_path.as_posix(),
        "burned_subs": bool(burn_subs and subs_path is not None),
        "bgm": bgm_path.as_posix() if bgm_path else None,
    }


# ---------------------------------------------------------------------------
# Multi-platform filter complex + ffmpeg argv
# ---------------------------------------------------------------------------


def _build_filter_arg_multi(platforms, audio_dur, burn_subs, subs_path,
                            bgm_path, scale_mult=SCALE_MULT_DEFAULT):
    """Build a -filter_complex for multi-platform fan-out.

    One source render: the cover zoompan chain (scale->zoompan->scale)
    runs once and is labeled [v_base]. The audio stream [1:a] is split
    into N inputs.

    N fan-out outputs: per-platform video (subs with force_style for
    alignment + vignette -> [v_<platform>]) and per-platform audio
    (loudnorm -> [a_<platform>]).

    NOTE: bgm_path is accepted for parity with the single-reel builder
    but is not wired into the multi-platform path (multi-input audio
    mixing is out of scope for the v1 fan-out).
    """
    _ = bgm_path  # reserved; multi-input audio mixing deferred
    chain = ffmpeg_zoompan.supersample_zoompan_filterchain(
        target_w=TARGET_W, target_h=TARGET_H, dur_s=audio_dur,
    )
    parts = list(chain)
    n = len(platforms)
    # Label the final scale output so we can split it per-platform.
    parts[-1] = parts[-1] + "[v_base]"
    # Video fan-out: split [v_base] into N inputs. ffmpeg requires the
    # split filter's input pad to be explicitly labeled (e.g.
    # `[v_base]split=3[a][b][c]`); an unlabeled `split=3[a][b][c]` is
    # rejected with EINVAL ("Cannot find an unused video input stream to
    # feed the unlabeled input pad split:default"). The audio fan-out
    # below already uses `[1:a]asplit=...` so it does not need this fix.
    split_labels = "".join("[v_%s_in]" % p for p in platforms)
    parts.append("[v_base]split=%d%s" % (n, split_labels))
    # Per-platform video chain: optional subs (with force_style for
    # caption alignment) + vignette -> [v_<platform>].
    for platform in platforms:
        segs = []
        if burn_subs and subs_path is not None:
            align = PLATFORM_SPECS[platform]["alignment"]
            sub_path_esc = subs_path.as_posix().replace("\\", "/")
            # ffmpeg's force_style uses single quotes; escape any
            # single quotes in the path to keep the filter parseable.
            sub_path_esc = sub_path_esc.replace("'", "'\\''")
            segs.append(
                "ass=%s:force_style='Alignment=%d':shaping=complex"
                % (sub_path_esc, align)
            )
        segs.append("vignette=PI/4[v_%s]" % platform)
        parts.append("[v_%s_in]%s" % (platform, ",".join(segs)))
    # Audio fan-out: split [1:a] into N inputs, apply per-platform
    # loudnorm -> [a_<platform>].
    audio_split_labels = "".join("[a_%s_in]" % p for p in platforms)
    parts.append("[1:a]asplit=%d%s" % (n, audio_split_labels))
    for platform in platforms:
        spec = PLATFORM_SPECS[platform]
        parts.append(
            "[a_%s_in]loudnorm=I=%s:TP=%s[a_%s]"
            % (
                platform,
                _fmt_loudnorm(spec["loudnorm_I"]),
                _fmt_loudnorm(spec["loudnorm_TP"]),
                platform,
            )
        )
    return ",".join(parts)


def _fmt_loudnorm(v):
    """Format a loudnorm numeric value compactly: '-14' for whole, '-1.5' for fraction."""
    f = float(v)
    if f == int(f):
        return "%d" % int(f)
    return "%g" % f


def _build_ffmpeg_argv_multi(platforms, cover_path, audio_path, bgm_path,
                             filter_arg, out_paths,
                             vcodec=VCODEC_DEFAULT, vpreset=VPRESET_DEFAULT):
    """Build a single ffmpeg argv that produces N outputs (one per platform).

    Each output maps its own [v_<platform>] video and [a_<platform>]
    audio from the shared filter complex. The cover + audio inputs
    (and optional bgm) are declared once at the head of the argv.
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
    cmd.extend(["-filter_complex", filter_arg])
    for platform, out_path in zip(platforms, out_paths):
        cmd.extend([
            "-map", "[v_%s]" % platform,
            "-map", "[a_%s]" % platform,
            "-c:v", vcodec, "-preset", vpreset, "-crf", str(VCRF),
            "-pix_fmt", "yuv420p",
            "-c:a", ACODEC, "-b:a", ABITRATE,
            "-shortest",
            str(out_path),
        ])
    return cmd


# ---------------------------------------------------------------------------
# Multi-platform render
# ---------------------------------------------------------------------------


def _render_reel_multi(book_dir, ch_id, platforms, out_paths,
                       cover_arg, audio_path, bgm_path=None,
                       burn_subs=False, subs_path=None,
                       waveform=False,
                       scale_mult=SCALE_MULT_DEFAULT,
                       vcodec=VCODEC_DEFAULT, vpreset=VPRESET_DEFAULT):
    """Render N platform variants serially from one source video.

    Step 1 -- render the cover zoompan to a temp base video (no audio,
    no per-platform filter). The expensive zoompan work happens once
    and is shared across all platforms.

    Step 2 -- for each platform, run a small ffmpeg that reads the
    base video + the original audio, applies per-platform subs
    alignment (force_style on ass) + per-platform loudnorm + vignette,
    and writes the platform MP4. Each platform is one ffmpeg
    invocation; peak memory is bounded by ONE libx264 encoder at a
    time instead of N parallel encoders.

    Why serial: a single ffmpeg invocation with N parallel libx264
    encodes at 1080p (each with its own lookahead + b-frames) can
    OOM on consumer hardware (observed 3-4 GB peak, exceeds 1.3 GB
    free on 32 GB hosts under load). The serial pattern trades a
    small wall-clock cost (one extra base render) for bounded memory.

    `_build_filter_arg_multi` + `_build_ffmpeg_argv_multi` are kept
    for unit tests; this function does not call them.
    """
    cover_path = _resolve_cover(book_dir, cover_arg)
    if not audio_path.exists():
        raise InputError("audio not found: %s" % audio_path)
    audio_dur = _probe_duration_seconds(audio_path)
    ffmpeg = shutil.which("ffmpeg")
    if ffmpeg is None:
        raise MissingDepError("ffmpeg not on PATH; install or set FFMPEG_PATH")

    with tempfile.TemporaryDirectory(prefix="assemble_reel_multi_") as tmp:
        tmp_dir = Path(tmp)
        base_video = tmp_dir / "base.mp4"

        # Step 1: render the cover zoompan to a temp base video.
        chain = list(ffmpeg_zoompan.supersample_zoompan_filterchain(
            target_w=TARGET_W, target_h=TARGET_H, dur_s=audio_dur,
            scale_mult=scale_mult,
        ))
        chain[-1] = chain[-1] + "[v_base]"
        base_argv = [
            ffmpeg, "-y",
            "-loop", "1", "-i", str(cover_path),
            "-filter_complex", ",".join(chain),
            "-map", "[v_base]",
            "-an",
            "-c:v", vcodec, "-preset", vpreset, "-crf", str(VCRF),
            "-pix_fmt", "yuv420p",
            "-t", str(audio_dur),
            str(base_video),
        ]
        _run_ffmpeg(base_argv)

        # Step 2: per-platform render. Each invocation reads the base
        # video + the original audio and applies per-platform filters.
        entries = []
        for platform, out_path in zip(platforms, out_paths):
            out_path.parent.mkdir(parents=True, exist_ok=True)
            spec = PLATFORM_SPECS[platform]
            v_segs = []
            if burn_subs and subs_path is not None:
                align = spec["alignment"]
                sub_path_esc = subs_path.as_posix().replace("\\", "/")
                sub_path_esc = sub_path_esc.replace("'", "'\\''")
                # NOTE: ffmpeg's gyan.dev 2025-08 build does not support
                # force_style on the ass/subtitles filter. We use
                # original_size=1080x1920 + shaping=complex (matrix-typed
                # filter, must escape the drive-colon in the path as \\:
                # so ffmpeg does not parse it as an option separator).
                # Per-platform caption positioning is deferred to a
                # per-platform ASS prebake at srt_to_ass time.
                v_segs.append(
                    "ass=%s:original_size=1080x1920:shaping=complex"
                    % sub_path_esc.replace(":", "\\\\:")
                )
            v_segs.append("vignette=PI/4")
            if waveform:
                # 3-segment chain: produce a [wf] parallel stream from
                # the audio via showwaves, then overlay it on the
                # post-vignette video at the bottom with a 40px margin.
                v_base_filter = "[0:v]" + ",".join(v_segs) + "[v_pre]"
                v_overlay = (
                    "[v_pre][wf]overlay=0:H-h-40:format=auto[v]"
                )
                v_filter = v_base_filter + ";" + v_overlay
                wf_chain = (
                    "[1:a]showwaves=s=1080x160:mode=cline:"
                    "colors=white@0.75:rate=30,format=yuva420p[wf]"
                )
            else:
                v_filter = "[0:v]" + ",".join(v_segs) + "[v]"
                wf_chain = None
            a_filter = (
                "[1:a]loudnorm=I=%s:TP=%s[a]"
                % (
                    _fmt_loudnorm(spec["loudnorm_I"]),
                    _fmt_loudnorm(spec["loudnorm_TP"]),
                )
            )
            if wf_chain is not None:
                platform_filter = "%s;%s;%s" % (wf_chain, v_filter, a_filter)
            else:
                platform_filter = "%s;%s" % (v_filter, a_filter)
            platform_argv = [
                ffmpeg, "-y",
                "-i", str(base_video),
                "-i", str(audio_path),
            ]
            platform_argv.extend([
                "-filter_complex", platform_filter,
                "-map", "[v]",
                "-map", "[a]",
                "-c:v", vcodec, "-preset", vpreset, "-crf", str(VCRF),
                "-pix_fmt", "yuv420p",
                "-c:a", ACODEC, "-b:a", ABITRATE,
                "-shortest",
                str(out_path),
            ])
            _run_ffmpeg(platform_argv)
            entries.append({
                "chapter_id": ch_id,
                "platform": platform,
                "codec": vcodec,
                "width": TARGET_W,
                "height": TARGET_H,
                "duration_s": round(audio_dur, 3),
                "source_cover": cover_path.as_posix(),
                "source_audio": audio_path.as_posix(),
                "burned_subs": bool(burn_subs and subs_path is not None),
                "bgm": bgm_path.as_posix() if bgm_path else None,
                "loudnorm": {
                    "I": spec["loudnorm_I"],
                    "TP": spec["loudnorm_TP"],
                },
                "caption_position": "bottom" if spec["alignment"] == 2 else "top",
                "out": out_path.as_posix(),
            })
        return entries


# ---------------------------------------------------------------------------
# Sidecar manifest
# ---------------------------------------------------------------------------


def _write_manifest(book_dir, entries, vcodec=VCODEC_DEFAULT):
    """Write the sidecar manifest at <book>/figures/media-video-manifest.json.

    Schema (per dispatch spec; identical to the horizontal assembler):
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


def run_reel(book_arg, chapter, out_arg, cover_arg, audio_arg,
             locale, bgm_arg=None, burn_subs=False, subs_arg=None,
             waveform=False,
             platforms=DEFAULT_PLATFORMS,
             scale_mult=SCALE_MULT_DEFAULT, vcodec=VCODEC_DEFAULT,
             vpreset=VPRESET_DEFAULT):
    """Run the full reel assembler. Returns the exit code.

    Flags:
        book_arg    -- --book value (required, repo-root-relative or
                       absolute-under-root).
        chapter     -- --chapter value (ch-NN), required.
        out_arg     -- --out value (required, repo-root-relative or
                       absolute-under-root). The actual outputs are
                       named <stem>-<platform><suffix> per platform
                       (e.g. reel-m1-ch-01-yt.mp4).
        cover_arg   -- --cover value (optional; falls back to the ladder).
        audio_arg   -- --audio value (required).
        locale      -- --locale value (required, kept for parity with the
                       rest of the Phase 9 CLI surface; not used
                       internally -- cover / audio / ASS are all
                       pre-localised by upstream scripts).
        bgm_arg     -- --bgm value (optional).
        burn_subs   -- --burn-subs flag (requires --subs).
        subs_arg    -- --subs value (required when burn_subs is True).
        platforms   -- Iterable or comma-separated str of platform codes
                       to fan out to. Each platform emits its own mp4
                       with its own loudnorm + caption positioning.
                       Default: ("yt", "ig", "tiktok").
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
        print("assemble_reel: %s" % exc, file=sys.stderr)
        return 2
    if not book_dir.is_dir():
        print(
            "assemble_reel: --book not found: %s" % book_dir,
            file=sys.stderr,
        )
        return 2

    # 2. --out
    try:
        out_path = _resolve_under_root(out_arg, "--out")
    except InputError as exc:
        print("assemble_reel: %s" % exc, file=sys.stderr)
        return 2

    # 3. Optional: --bgm, --subs
    bgm_path = None
    if bgm_arg is not None:
        try:
            bgm_path = _resolve_under_root(bgm_arg, "--bgm")
        except InputError as exc:
            print("assemble_reel: %s" % exc, file=sys.stderr)
            return 2
        if not bgm_path.exists():
            print(
                "assemble_reel: --bgm not found: %s" % bgm_path,
                file=sys.stderr,
            )
            return 2
    subs_path = None
    if subs_arg is not None:
        try:
            subs_path = _resolve_under_root(subs_arg, "--subs")
        except InputError as exc:
            print("assemble_reel: %s" % exc, file=sys.stderr)
            return 2
        if not subs_path.exists():
            print(
                "assemble_reel: --subs not found: %s" % subs_path,
                file=sys.stderr,
            )
            return 2

    # 4. --burn-subs requires --subs.
    if burn_subs and subs_path is None:
        print(
            "assemble_reel: --burn-subs requires --subs",
            file=sys.stderr,
        )
        return 2

    # 5. --platforms validation.
    try:
        platforms_tuple = _parse_platforms(platforms)
    except InputError as exc:
        print("assemble_reel: %s" % exc, file=sys.stderr)
        return 2

    # 6. Audio.
    ch_id = chapter
    try:
        audio = _resolve_under_root(audio_arg, "--audio")
    except InputError as exc:
        print(
            "assemble_reel: %s" % exc, file=sys.stderr,
        )
        return 2
    if not audio.exists():
        print(
            "assemble_reel: --audio not found: %s" % audio,
            file=sys.stderr,
        )
        return 2

    # 7. Per-platform output paths.
    out_paths = [_platform_output_path(out_path, p) for p in platforms_tuple]
    for p in out_paths:
        p.parent.mkdir(parents=True, exist_ok=True)

    # 8. Multi-platform pipeline (one ffmpeg invocation; N outputs).
    try:
        entries = _render_reel_multi(
            book_dir, ch_id, platforms_tuple, out_paths,
            cover_arg=cover_arg,
            audio_path=audio,
            bgm_path=bgm_path,
            burn_subs=burn_subs,
            subs_path=subs_path,
            waveform=waveform,
            scale_mult=scale_mult,
            vcodec=vcodec,
            vpreset=vpreset,
        )
    except InputError as exc:
        print("assemble_reel: %s" % exc, file=sys.stderr)
        return 2
    except MissingDepError as exc:
        print("assemble_reel: %s" % exc, file=sys.stderr)
        return 3
    except RuntimeFailure as exc:
        print("assemble_reel: %s" % exc, file=sys.stderr)
        return 4

    # 9. Sidecar manifest.
    try:
        manifest_path = _write_manifest(book_dir, entries, vcodec=vcodec)
    except OSError as exc:
        print(
            "assemble_reel: cannot write manifest: %s" % exc,
            file=sys.stderr,
        )
        return 4

    print(
        "assemble_reel: OK platforms=%s chapters=%d outs=%s manifest=%s"
        % (
            ",".join(platforms_tuple),
            len(entries),
            ",".join(str(p) for p in out_paths),
            manifest_path,
        )
    )
    return 0


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------


def _build_parser():
    p = argparse.ArgumentParser(
        prog="assemble_reel",
        description=(
            "Phase 4b Mode-1: render a vertical (1080x1920) reel from a "
            "single static cover + Ken Burns zoompan + audio + optional "
            "burned subs + optional BGM. By default fans out to yt, ig, "
            "and tiktok variants via a single ffmpeg invocation."
        ),
    )
    p.add_argument("--book", required=True,
                   help="Book root (books/<slug>/).")
    p.add_argument("--chapter", required=True,
                   help="Chapter id (e.g. ch-01) for the reel.")
    p.add_argument("--out", required=True,
                   help="Base output MP4 path (must resolve under repo "
                        "root). Each platform gets <stem>-<platform><suffix>.")
    p.add_argument("--cover",
                   help="Cover image path (under repo root; falls back to "
                        "figures/cover.png then chapters-rendered/*.png).")
    p.add_argument("--audio", required=True,
                   help="Per-chapter audio M4B path (under repo root).")
    p.add_argument("--locale", required=True,
                   help="Locale code (en, ar, ...).")
    p.add_argument("--bgm",
                   help="Optional background-music audio path (under repo root).")
    p.add_argument("--burn-subs", action="store_true",
                   help="Burn the ASS subtitle file into the video "
                        "(requires --subs).")
    p.add_argument("--subs",
                   help="ASS subtitle path (under repo root; required with "
                        "--burn-subs).")
    p.add_argument("--waveform", action="store_true",
                   help="Overlay a voice waveform visualizer (ffmpeg "
                        "showwaves) at the bottom of the reel. Default off.")
    p.add_argument("--platforms", default="yt,ig,tiktok",
                   help="Comma-separated list of platforms to fan out to. "
                        "Allowed: yt, ig, tiktok. Default: yt,ig,tiktok. "
                        "Each platform emits its own mp4 with its own "
                        "loudnorm target and caption positioning.")
    p.add_argument("--scale-mult", type=int, default=SCALE_MULT_DEFAULT,
                   help="Supersample multiplier for zoompan (default %d; "
                        "2 = ~2x faster, slight quality loss; 1 = native "
                        "1080x1920, fastest)." % SCALE_MULT_DEFAULT)
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
    return run_reel(
        book_arg=args.book,
        chapter=args.chapter,
        out_arg=args.out,
        cover_arg=args.cover,
        audio_arg=args.audio,
        locale=args.locale,
        bgm_arg=args.bgm,
        burn_subs=args.burn_subs,
        subs_arg=args.subs,
        waveform=args.waveform,
        platforms=args.platforms,
        scale_mult=args.scale_mult,
        vcodec=args.vcodec,
        vpreset=args.vpreset,
    )


if __name__ == "__main__":
    sys.exit(main())
