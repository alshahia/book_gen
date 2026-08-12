"""Tests for check_whisper_deps.py -- faster-whisper dep probe + model picker.

Verifies:
  * Per-locale model auto-pick (large-v3 for Arabic, small for English).
  * ``main --self-check`` exits 3 when faster-whisper / ctranslate2 is
    not importable, regardless of whether the venv actually has them.
"""
import sys
import importlib.util

import pytest

import check_whisper_deps as cwd_mod


# ---------------------------------------------------------------------------
# Probe at import time (used by future skipif markers; not required today).
# ---------------------------------------------------------------------------

HAS_FASTER_WHISPER = importlib.util.find_spec("faster_whisper") is not None
HAS_CTRANSLATE2 = importlib.util.find_spec("ctranslate2") is not None


# ---------------------------------------------------------------------------
# 1) Locale -> model auto-pick
# ---------------------------------------------------------------------------


def test_picks_large_v3_for_arabic():
    """Arabic (ar) must resolve to large-v3 (per research F10)."""
    assert cwd_mod.pick_model_for_locale("ar") == "large-v3"


def test_picks_small_for_english():
    """English (en) must resolve to small (faster, sufficient for en)."""
    assert cwd_mod.pick_model_for_locale("en") == "small"


def test_unknown_locale_raises():
    """An unsupported locale raises WhisperDepsError (exits 2 from main)."""
    with pytest.raises(cwd_mod.WhisperDepsError):
        cwd_mod.pick_model_for_locale("fr")


# ---------------------------------------------------------------------------
# 2) main() exits 3 when faster_whisper / ctranslate2 missing
# ---------------------------------------------------------------------------


def _find_spec_fake_factory(missing_names, real_find_spec):
    """Build a find_spec replacement that returns None for `missing_names`."""
    missing = set(missing_names)

    def fake(name, *args, **kwargs):
        if name in missing:
            return None
        return real_find_spec(name, *args, **kwargs)

    return fake


def test_exits_3_when_faster_whisper_missing(monkeypatch, capsys):
    """main() with --self-check must return 3 when faster_whisper is absent."""
    real_find_spec = importlib.util.find_spec
    monkeypatch.setattr(
        importlib.util,
        "find_spec",
        _find_spec_fake_factory(
            ("faster_whisper", "ctranslate2"),
            real_find_spec,
        ),
    )
    rc = cwd_mod.main(["--language", "en", "--self-check"])
    captured = capsys.readouterr()
    assert rc == 3, "expected exit 3 when faster-whisper is missing"
    assert "missing" in captured.err.lower()


def test_exits_3_from_plain_dep_check_when_missing(monkeypatch, capsys):
    """main() WITHOUT --self-check still exits 3 when the dep is absent."""
    real_find_spec = importlib.util.find_spec
    monkeypatch.setattr(
        importlib.util,
        "find_spec",
        _find_spec_fake_factory(
            ("faster_whisper",),
            real_find_spec,
        ),
    )
    rc = cwd_mod.main(["--language", "ar"])
    assert rc == 3


def test_exits_2_on_unsupported_locale_via_picker(capsys):
    """``pick_model_for_locale`` raises WhisperDepsError for unsupported codes.

    argparse's ``choices=[...]`` already rejects bad --language at the
    CLI layer, so the test exercises the underlying helper directly.
    """
    with pytest.raises(cwd_mod.WhisperDepsError):
        cwd_mod.pick_model_for_locale("fr")
