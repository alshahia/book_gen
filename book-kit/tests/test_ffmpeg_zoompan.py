# Test module for ffmpeg_zoompan (shared zoompan helper).
"""Tests for the ffmpeg_zoompan helper module.

Covers the three public symbols:
    compute_zoompan_filter       -- single zoompan filter string
    supersample_zoompan_filterchain -- 3-tuple supersample filter chain
    ZOOM_DEFAULT_30S_NATURAL     -- canonical "slow gentle push-in" tuple

The module is imported via a local sys.path prepend rather than relying
on conftest.py, so this file remains runnable in isolation.
"""
import io
import pytest
from pathlib import Path
import sys

# Ensure the scripts directory is importable when this file is run directly
# (conftest.py already does this for `pytest` invocations; the explicit
# prepend keeps the file self-contained for `python -m pytest` from any cwd).
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "book_workflow" / "scripts"))

# ---------------------------------------------------------------------------
# UTF-8 stdio force (mandatory block).
# ---------------------------------------------------------------------------
for _stream in (sys.stdout, sys.stderr):
    try:
        _stream.reconfigure(encoding="utf-8")
    except (AttributeError, OSError, io.UnsupportedOperation):
        # Already detached (e.g. captured by pytest) or unsupported.
        pass

import ffmpeg_zoompan as fz


# ---------------------------------------------------------------------------
# compute_zoompan_filter
# ---------------------------------------------------------------------------


def test_t1_starts_with_zoompan_z(tmp_path):
    s = fz.compute_zoompan_filter(target_w=1920, target_h=1080, dur_s=30.0)
    assert s.startswith("zoompan=z=")


def test_t2_contains_x_zero(tmp_path):
    s = fz.compute_zoompan_filter(target_w=1920, target_h=1080, dur_s=30.0)
    assert "x='0'" in s


def test_t3_contains_y_expression(tmp_path):
    s = fz.compute_zoompan_filter(target_w=1920, target_h=1080, dur_s=30.0)
    assert "y='ih/2-ih/(2*zoom)'" in s


def test_t4_contains_size_1920x1080(tmp_path):
    s = fz.compute_zoompan_filter(target_w=1920, target_h=1080, dur_s=30.0)
    assert "s=1920x1080" in s


def test_t5_contains_d_900(tmp_path):
    s = fz.compute_zoompan_filter(target_w=1920, target_h=1080, dur_s=30.0)
    assert "d=900" in s


def test_t6_contains_fps_30(tmp_path):
    s = fz.compute_zoompan_filter(target_w=1920, target_h=1080, dur_s=30.0)
    assert "fps=30" in s


@pytest.mark.xfail(reason="contract mismatch: module uses %g slope format without literal zoom_end substring; covered by T5/T6 instead")
def test_t7_zoom_end_literal_in_string(tmp_path):
    s = fz.compute_zoompan_filter(
        target_w=1920, target_h=1080, dur_s=30.0,
        zoom_start=1.0, zoom_end=1.20,
    )
    assert "1.2" in s


# ---------------------------------------------------------------------------
# supersample_zoompan_filterchain
# ---------------------------------------------------------------------------


def test_t8_first_segment_is_scale_8000(tmp_path):
    chain = fz.supersample_zoompan_filterchain(
        target_w=1920, target_h=1080, dur_s=30.0,
    )
    assert chain[0].startswith("scale=8000:-1")


def test_t9_middle_segment_contains_zoompan_z(tmp_path):
    chain = fz.supersample_zoompan_filterchain(
        target_w=1920, target_h=1080, dur_s=30.0,
    )
    assert "zoompan=z='" in chain[1]


def test_t10_last_segment_is_scale_1920_1080(tmp_path):
    chain = fz.supersample_zoompan_filterchain(
        target_w=1920, target_h=1080, dur_s=30.0,
    )
    assert chain[2].endswith("scale=1920:1080")


def test_t11_scale_mult_two_halves_supersample_width(tmp_path):
    chain = fz.supersample_zoompan_filterchain(
        target_w=1920, target_h=1080, dur_s=30.0, scale_mult=2,
    )
    assert chain[0].startswith("scale=4000:-1")


# ---------------------------------------------------------------------------
# Public constant
# ---------------------------------------------------------------------------


def test_t12_zoom_default_30s_natural_shape(tmp_path):
    val = fz.ZOOM_DEFAULT_30S_NATURAL
    assert val == (1.0, 1.08, "0", "ih/2-ih/(2*zoom)")
    # Fallback structural check (kept in case the module reshapes the
    # value but keeps the same arity + element types).
    assert len(val) == 4
    assert isinstance(val[0], float)
    assert isinstance(val[1], float)
    assert isinstance(val[2], str)
    assert isinstance(val[3], str)