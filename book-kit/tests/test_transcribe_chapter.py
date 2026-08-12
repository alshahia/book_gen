"""Tests for transcribe_chapter.py -- ASR path validation + dep probe.

Verifies:
  * ``main`` exits 3 when faster-whisper is missing.
  * ``main`` exits 2 when ``--book`` resolves outside the repo root
    (path-escape guard via ``_resolve_under_root``).
  * ``main`` exits 2 when ``--book`` contains a ``..`` segment.
  * ``main`` exits 2 for an unsupported locale.

Tests that need a real book directory under the repo root monkeypatch
``tc_mod.REPO_ROOT`` to ``tmp_path``; this keeps every write inside the
pytest temp area while satisfying the path-escape guard.
"""
import sys
import importlib.util

import pytest

import transcribe_chapter as tc_mod


# ---------------------------------------------------------------------------
# Module-level dep probe (defined for completeness; tests in this file
# do NOT require faster-whisper to be installed -- they validate the
# dep-missing path).
# ---------------------------------------------------------------------------

HAS_FASTER_WHISPER = importlib.util.find_spec("faster_whisper") is not None


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _find_spec_fake_factory(missing_names, real_find_spec):
    """find_spec replacement that returns None for `missing_names`."""
    missing = set(missing_names)

    def fake(name, *args, **kwargs):
        if name in missing:
            return None
        return real_find_spec(name, *args, **kwargs)

    return fake


def _book_dir_under(tmp_path):
    """Build a minimal book dir and patch REPO_ROOT so path guard accepts it."""
    book_dir = tmp_path / "book_a"
    (book_dir / "chapters").mkdir(parents=True)
    return book_dir


# ---------------------------------------------------------------------------
# 1) Faster-whisper missing -> exit 3
# ---------------------------------------------------------------------------


def test_exits_3_when_faster_whisper_missing(monkeypatch, tmp_path, capsys):
    """When faster-whisper is not importable, main returns exit 3.

    We pass a valid book + MP3 so path validation succeeds, then the
    dep probe at the end of ``run_transcribe`` short-circuits with 3.
    """
    book_dir = _book_dir_under(tmp_path)
    fake_mp3 = book_dir / "ch-01-en.mp3"
    fake_mp3.write_bytes(b"")  # presence check; never decoded

    # Patch REPO_ROOT so the book dir resolves under the (patched) root.
    monkeypatch.setattr(tc_mod, "REPO_ROOT", tmp_path)

    # Patch find_spec to make faster_whisper look absent.
    real_find_spec = importlib.util.find_spec
    monkeypatch.setattr(
        importlib.util,
        "find_spec",
        _find_spec_fake_factory(("faster_whisper",), real_find_spec),
    )

    rc = tc_mod.main([
        "--book", str(book_dir),
        "--chapter", "ch-01",
        "--locale", "en",
        "--mp3", str(fake_mp3),
    ])
    captured = capsys.readouterr()
    assert rc == 3, "expected exit 3 when faster-whisper is missing"
    assert "faster-whisper" in captured.err


# ---------------------------------------------------------------------------
# 2) Path-escape rejection
# ---------------------------------------------------------------------------


def test_path_validation_rejects_outside_book_root(capsys):
    """``--book C:\\Windows`` must exit 2 (resolves outside repo root)."""
    if not sys.platform.startswith("win"):
        pytest.skip("C:\\Windows path is Windows-specific")
    rc = tc_mod.main([
        "--book", "C:\\Windows",
        "--chapter", "ch-01",
        "--locale", "en",
    ])
    captured = capsys.readouterr()
    assert rc == 2, "path-escape via --book must exit 2"
    assert "--book" in captured.err


def test_path_validation_rejects_dotdot_in_book(capsys):
    """A ``..`` segment in ``--book`` is rejected (exit 2) before any FS touch."""
    rc = tc_mod.main([
        "--book", "books/../etc",
        "--chapter", "ch-01",
        "--locale", "en",
    ])
    captured = capsys.readouterr()
    assert rc == 2
    assert ".." in captured.err


# ---------------------------------------------------------------------------
# 3) Unknown locale -> exit 2 (path validation passed via patched REPO_ROOT)
# ---------------------------------------------------------------------------


def test_unknown_locale_exits_2(monkeypatch, tmp_path, capsys):
    """An unsupported locale is rejected (exit 2) after path validation passes."""
    book_dir = _book_dir_under(tmp_path)
    monkeypatch.setattr(tc_mod, "REPO_ROOT", tmp_path)

    rc = tc_mod.main([
        "--book", str(book_dir),
        "--chapter", "ch-01",
        "--locale", "fr",
    ])
    captured = capsys.readouterr()
    assert rc == 2
    assert "locale" in captured.err
