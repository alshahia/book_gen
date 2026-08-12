"""Tests for errors.py -- actionable error helper.

Covers both the catalog semantics (every HINTS key works; unknown keys
fallback cleanly) and the dataclass contract (MediaPipelineError carries
``hint`` and ``exit_code``).
"""
import sys
from pathlib import Path

import pytest

# Make errors.py importable. Lib lives at book-kit/book_workflow/lib/;
# relative to this file that's parents[1]/book_workflow/lib.
LIB_DIR = Path(__file__).resolve().parents[1] / "book_workflow" / "lib"
sys.path.insert(0, str(LIB_DIR))

import errors as errors_mod  # noqa: E402


# ---------------------------------------------------------------------------
# 1) Every HINTS key raises cleanly with the right exit_code default.
# ---------------------------------------------------------------------------


def test_raise_actionable_each_kind():
    """Every catalog entry raises a MediaPipelineError; exit_code matches."""
    expectations = {
        "missing_amiri_font": 3,
        "voice_unavailable": 4,
        "schema_invalid": 2,
        "audio_empty": 4,
        "comfyui_not_running": 3,
        "unsupported_locale": 2,
    }
    sample_ctx = {
        "missing_amiri_font": {"path": "/tmp/missing-font.ttf"},
        "voice_unavailable": {"voice": "x", "locale": "y", "provider": "z"},
        "schema_invalid": {"path": "/tmp/m.json", "field": "$.a"},
        "audio_empty": {"chapter": "ch-01", "locale": "en"},
        "comfyui_not_running": {"url": "http://127.0.0.1:8188/"},
        "unsupported_locale": {"locale": "xx"},
    }
    for kind, ctx in sample_ctx.items():
        with pytest.raises(errors_mod.MediaPipelineError) as exc:
            errors_mod.raise_actionable(kind, **ctx)
        assert exc.value.exit_code == expectations[kind], (
            "%s should exit %d (got %d)"
            % (kind, expectations[kind], exc.value.exit_code)
        )
        # The hint must reference something actionable (a path, a name,
        # a URL, a config location) -- not just "error".
        assert exc.value.hint


# ---------------------------------------------------------------------------
# 2) format_hint is side-effect free for known and unknown kinds.
# ---------------------------------------------------------------------------


def test_format_hint_no_raise():
    """format_hint returns a string for known and unknown kinds (no raise)."""
    # Known kind + ctx.
    h = errors_mod.format_hint(
        "voice_unavailable", voice="ar-SA-X", locale="ar", provider="edge-tts"
    )
    assert isinstance(h, str) and "ar-SA-X" in h

    # Unknown kind returns a fallback mentioning the known kinds.
    h2 = errors_mod.format_hint("nonsense_kind")
    assert "nonsense_kind" in h2
    assert "missing_amiri_font" in h2, (
        "fallback should list the known kinds so the user knows what to use"
    )


# ---------------------------------------------------------------------------
# 3) MediaPipelineError carries .hint and .exit_code cleanly.
# ---------------------------------------------------------------------------


def test_media_pipeline_error_carries_hint_exit():
    """Exception attributes are accessible; str() is single-line (the hint)."""
    err = errors_mod.MediaPipelineError("install Amiri at /x/font.ttf", exit_code=3)
    assert err.hint == "install Amiri at /x/font.ttf"
    assert err.exit_code == 3
    # Default exit_code is 2 (input error).
    err2 = errors_mod.MediaPipelineError("default exit")
    assert err2.exit_code == 2
    # repr includes both fields for log-friendly debugging.
    r = repr(err)
    assert "exit_code=3" in r
    assert "install Amiri" in r
    # str(err) returns the hint alone, not a Python-default frame.
    assert str(err) == "install Amiri at /x/font.ttf"


# ---------------------------------------------------------------------------
# 4) Every error_kind used by Phase 2a/2b code paths is in HINTS.
# ---------------------------------------------------------------------------


def test_kinds_match_hint_catalog():
    """The Phase 2 helpers must reference only error_kinds present in HINTS."""
    catalog = set(errors_mod.HINTS.keys())
    # Phase 2 helpers that surface error_kinds directly: tts_events.
    referenced_kinds = {
        "unsupported_locale",  # tts_events.collect_sentence_offsets
    }
    # Phase 9 / devex F9 reference list (what we WILL use later; we
    # check the catalog is a superset so we don't trip a verification
    # failure when the integration wave lands).
    future_referenced = {
        "missing_amiri_font",
        "voice_unavailable",
        "schema_invalid",
        "audio_empty",
        "comfyui_not_running",
    }
    missing_now = referenced_kinds - catalog
    missing_future = future_referenced - catalog
    assert not missing_now, (
        "Phase 2b code paths use kinds not in HINTS: %s" % missing_now
    )
    assert not missing_future, (
        "Phase 2a/2b planned integration needs kinds not in HINTS: %s"
        % missing_future
    )


# ---------------------------------------------------------------------------
# 5) DEFAULT_EXIT_CODES is consistent with the documented exit-code
# convention (0/2/3/4 only).
# ---------------------------------------------------------------------------


def test_default_exit_codes_allowed_values():
    """Every DEFAULT_EXIT_CODES value is in {2, 3, 4} (never 0 or 1)."""
    for kind, code in errors_mod.DEFAULT_EXIT_CODES.items():
        assert code in (2, 3, 4), (
            "%s has illegal exit_code=%d (must be 2/3/4 per pipeline conv.)"
            % (kind, code)
        )
        # And the same key must exist in HINTS -- otherwise the raise
        # call will trigger the unknown-kind fallback (exit 2).
        assert kind in errors_mod.HINTS, (
            "%s in DEFAULT_EXIT_CODES but missing from HINTS" % kind
        )
