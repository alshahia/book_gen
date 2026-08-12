"""ffmpeg_zoompan.py -- shared zoompan filter-chain helpers for book2media.

Public API:
    ZOOM_DEFAULT_30S_NATURAL  -- canonical "slow gentle push-in" tuple
                                (zoom_start=1.0, zoom_end=1.08,
                                 pan_x="0", pan_y="ih/2-ih/(2*zoom)").
    WIDE_GENTLE               -- alias of ZOOM_DEFAULT_30S_NATURAL,
                                 used by assemble_video_horizontal.py
                                 and (Phase 4b-2) assemble_video_trailer.py.
    compute_zoompan_filter    -- returns the ffmpeg
                                 ``zoompan=z='...':d=...:x='...':y='...':s=WxH:fps=N``
                                 filter string.
    supersample_zoompan_filterchain -- returns a 3-tuple
                                 ``(scale=<W>:-1, zoompan=..., scale=<W>:<H>)``
                                 implementing the 4x supersample trick that
                                 kills zoompan judder (per Phase 4 research F8).

USAGE
    Import-clean: ``import ffmpeg_zoompan`` and
    ``importlib.import_module('ffmpeg_zoompan')`` both succeed. No CLI,
    no ``__main__`` block -- this is a library consumed by the video
    assemblers (assemble_video_horizontal.py, and Phase 4b-2's
    assemble_video_trailer.py / assemble_video_reels.py).

PATH VALIDATION
    This module performs no path validation -- it has no file inputs.
    Callers (assemble_video_horizontal.py) are responsible for resolving
    paths under the repo root before invoking ffmpeg.

# chub-cite: ffmpeg `zoompan` filter (built-in to local ffmpeg).
# chub-cite: ffmpeg `scale` filter (built-in to local ffmpeg).

ASCII-ONLY: every byte is ASCII per the P1-P18 hardening rules.
"""
from __future__ import annotations

# ---------------------------------------------------------------------------
# UTF-8 stdio force (mandatory block from dispatch preamble).
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


# ---------------------------------------------------------------------------
# Public constants
# ---------------------------------------------------------------------------


# Canonical "slow gentle push-in" -- the motion recipe shared by the
# horizontal video assembler (this phase) and the trailer assembler
# (Phase 4b-2). 30-second natural motion: 1.0x at frame 0 -> 1.08x at
# the final frame, vertically centred (no horizontal pan). The
# `ih/2 - ih/(2*zoom)` expression keeps the centre of frame stable while
# the zoom factor grows -- the standard Ken Burns "stay centred" recipe.
ZOOM_DEFAULT_30S_NATURAL = (1.0, 1.08, "0", "ih/2-ih/(2*zoom)")

# Aliases for callers that prefer the descriptive name. Same tuple value
# so identity checks (`is`) and equality checks (`==`) both hold.
WIDE_GENTLE = ZOOM_DEFAULT_30S_NATURAL


# ---------------------------------------------------------------------------
# Public API: compute_zoompan_filter
# ---------------------------------------------------------------------------


def compute_zoompan_filter(
    target_w, target_h, dur_s, fps=30,
    zoom_start=1.0, zoom_end=1.05,
    pan_x="0", pan_y="ih/2-ih/(2*zoom)",
):
    """Return the ffmpeg `zoompan` filter chain string.

    Shape:
        zoompan=z='<expr>':d=<N>:x='<x>':y='<y>':s=<W>x<H>:fps=<F>

    The `z` expression linearly interpolates from `zoom_start` at
    frame 0 to `zoom_end` at frame (d-1), producing the classic Ken
    Burns push-in. ffmpeg's zoompan `z` is an expr, so we emit
    ``<start> + (end - start) * on / (N - 1)``; when d <= 1 we emit
    the static `zoom_start` (avoid div-by-zero in the expression).

    Args:
        target_w, target_h: output frame size in pixels.
        dur_s: scene duration in seconds (drives `d`).
        fps: output frame rate (drives `d` and `fps`).
        zoom_start, zoom_end: zoom factor at frame 0 and frame (d-1).
        pan_x, pan_y: pan expressions (ffmpeg zoompan syntax).

    Returns:
        The full filter string ready for ffmpeg's `-vf` / `-filter_complex`.
    """
    w = int(target_w)
    h = int(target_h)
    f = int(fps)
    # Round to nearest integer frame count so `d` matches the actual
    # number of output frames ffmpeg will produce.
    d_frames = max(1, int(round(float(dur_s) * f)))
    if d_frames <= 1 or float(zoom_end) == float(zoom_start):
        # Static zoom: avoid div-by-zero in the linear interp.
        z_expr = "%g" % float(zoom_start)
    else:
        # Linear interp: zoom at frame `on` is start + (end-start)*on/(d-1).
        z_expr = "%g+(%g)*on/%d" % (
            float(zoom_start),
            (float(zoom_end) - float(zoom_start)) / (d_frames - 1),
            d_frames - 1,
        )
    return (
        "zoompan=z='%s':d=%d:x='%s':y='%s':s=%dx%d:fps=%d"
        % (z_expr, d_frames, pan_x, pan_y, w, h, f)
    )


# ---------------------------------------------------------------------------
# Public API: supersample_zoompan_filterchain
# ---------------------------------------------------------------------------


# Base width used to compute the supersample dimension: 2000px * scale_mult.
# At the default scale_mult=4 the leading filter is `scale=8000:-1` -- the
# literal value documented in Phase 4 research F8 as the canonical "4x
# supersample of a 2000px source" trick that kills zoompan judder.
_SUPERSAMPLE_BASE_WIDTH = 2000


def supersample_zoompan_filterchain(target_w, target_h, dur_s, scale_mult=4):
    """Return the 3-tuple ``(scale=W:-1, zoompan=..., scale=W:H)``.

    The leading `scale=<W>:-1` is the critical supersample trick: it
    inflates the source image to ``2000 * scale_mult`` pixels wide
    (default 8000 = 4x of a 2000px source) BEFORE zoompan sees it.
    Without this, zoompan operates on the source resolution and the
    output is blocky / blurry (Phase 4 research F8).

    The trailing `scale=W:H` normalises back to the target dimensions
    so the consumer always sees the requested size regardless of the
    upstream image aspect ratio.

    Args:
        target_w, target_h: output frame size in pixels.
        dur_s: scene duration in seconds.
        scale_mult: supersample multiplier; default 4 -> 8000px wide.
            Pass 2 for memory-constrained hosts; 8 for higher quality.

    Returns:
        A 3-tuple of ffmpeg filter strings, ready to be joined with
        ``","`` for `-vf` or `-filter_complex`.
    """
    mult = int(scale_mult)
    if mult < 1:
        mult = 1
    supersample_w = _SUPERSAMPLE_BASE_WIDTH * mult
    zp = compute_zoompan_filter(
        target_w=int(target_w),
        target_h=int(target_h),
        dur_s=float(dur_s),
    )
    return (
        "scale=%d:-1" % supersample_w,
        zp,
        "scale=%d:%d" % (int(target_w), int(target_h)),
    )


# ---------------------------------------------------------------------------
# Library boundary -- NO __main__ block (per dispatch: library, not CLI).
# ---------------------------------------------------------------------------
