"""Tests for align_srt.py -- ASR-to-chunk alignment + SRT emission.

Verifies:
  * A high-overlap fixture produces an SRT with at least one cue.
  * A heavily word-dropped fixture exits 4 (drift > 30%, below
    ``DRIFT_RATIO_FLOOR``); the test documents the drift-floor
    contract rather than expecting cues to land in the file.
"""
import json
from pathlib import Path

import pytest

import align_srt as align_mod


# ---------------------------------------------------------------------------
# Helpers -- build a complete book tree under tmp_path so run_align
# has everything it expects.
# ---------------------------------------------------------------------------


def _book_with_alignment_fixture(
    tmp_path,
    *,
    slug,
    chapter_id,
    locale,
    chapter_text,
    words,
    chunk_duration_ms,
):
    """Create a book root that run_align can consume end-to-end.

    Layout:
        <tmp_path>/<slug>/
            chapters/<chapter_id>.md
            chapters/<chapter_id>-<locale>-words.json
            figures/media-tts-manifest.json
    """
    book_dir = tmp_path / slug
    (book_dir / "chapters").mkdir(parents=True)
    (book_dir / "figures").mkdir(parents=True)

    # Chapter text (canonical -- will be chunked by _chunk_by_h2).
    (book_dir / "chapters" / ("%s.md" % chapter_id)).write_text(
        chapter_text, encoding="utf-8",
    )

    # Words JSON (faster-whisper sidecar shape).
    (book_dir / "chapters" / ("%s-%s-words.json" % (chapter_id, locale))).write_text(
        json.dumps({"words": words}, indent=2, sort_keys=True),
        encoding="utf-8",
    )

    # Media TTS manifest entry for this (chapter, locale).
    manifest = {
        "chunks": [
            {
                "chapter": chapter_id,
                "locale": locale,
                "chunks": [
                    {"duration_ms": chunk_duration_ms, "index": 1},
                ],
            }
        ]
    }
    (book_dir / "figures" / "media-tts-manifest.json").write_text(
        json.dumps(manifest, indent=2, sort_keys=True), encoding="utf-8",
    )

    return book_dir


# ---------------------------------------------------------------------------
# 1) High-overlap fixture: cues are emitted, exit 0
# ---------------------------------------------------------------------------


def test_align_chunks_returns_srt_with_cues(monkeypatch, tmp_path):
    """When ASR words cover the chunk, an SRT with at least one cue is written."""
    chapter_text = "Hello world today."
    words = [
        {"word": "hello", "start": 0.10, "end": 0.50, "prob": 0.99},
        {"word": "world", "start": 0.60, "end": 1.10, "prob": 0.98},
        {"word": "today", "start": 1.20, "end": 1.80, "prob": 0.97},
    ]
    book_dir = _book_with_alignment_fixture(
        tmp_path,
        slug="book_a",
        chapter_id="ch-01",
        locale="ar",
        chapter_text=chapter_text,
        words=words,
        chunk_duration_ms=2000,
    )

    # Patch REPO_ROOT so the book dir under tmp_path passes the path guard.
    monkeypatch.setattr(align_mod, "REPO_ROOT", tmp_path)

    rc = align_mod.main([
        "--book", str(book_dir),
        "--chapter", "ch-01",
        "--locale", "ar",
    ])
    assert rc == 0, "expected exit 0 on a high-overlap fixture"

    srt_path = book_dir / "chapters" / "ch-01-ar.srt"
    assert srt_path.exists(), "SRT must be written on success"
    srt_text = srt_path.read_text(encoding="utf-8")

    # At least one cue block: an index line + a time-range line.
    assert "\n" in srt_text
    assert "-->" in srt_text, "SRT must contain at least one cue time-range"
    # SRT timestamps are HH:MM:SS,mmm; assert at least one such range.
    import re
    assert re.search(r"\d{2}:\d{2}:\d{2},\d{3}\s*-->\s*\d{2}:\d{2}:\d{2},\d{3}", srt_text), (
        "expected at least one SRT timestamp pair"
    )


# ---------------------------------------------------------------------------
# 2) Drift floor: 80% word-drop -> exit 4 (drift > 30%)
# ---------------------------------------------------------------------------


def test_align_handles_drift_floor(monkeypatch, tmp_path):
    """With 80% of words dropped, drift exceeds the 30% floor -> exit 4.

    7-word canonical vs 1-word ASR slice -> SequenceMatcher ratio is
    well below 0.70, so run_align returns 4. The SRT is NOT written in
    that case (the script returns before the write step).

    locale="en" -- if we used "ar", the auto-detect would see mostly-Latin
    canonical text and downgrade the floor to 0.0, masking the case this
    test exercises (genuine drift, not translation mismatch).
    """
    chapter_text = "Hello world today is a beautiful bright morning."
    # 1 word in the slice out of 7 canonical -> ~85% word-drop, ~70-85% drift.
    words = [
        {"word": "hello", "start": 0.10, "end": 0.50, "prob": 0.99},
    ]
    book_dir = _book_with_alignment_fixture(
        tmp_path,
        slug="book_b",
        chapter_id="ch-02",
        locale="en",
        chapter_text=chapter_text,
        words=words,
        chunk_duration_ms=5000,
    )

    # Patch REPO_ROOT so the book dir under tmp_path passes the path guard.
    monkeypatch.setattr(align_mod, "REPO_ROOT", tmp_path)

    rc = align_mod.main([
        "--book", str(book_dir),
        "--chapter", "ch-02",
        "--locale", "en",
    ])
    assert rc == 4, "expected exit 4 when drift exceeds the 30% floor"

    srt_path = book_dir / "chapters" / "ch-02-en.srt"
    # Exit 4 means the script returned before writing the SRT.
    assert not srt_path.exists(), "SRT must NOT be written on a drift-floor exit"


# ---------------------------------------------------------------------------
# 3) Bad inputs
# ---------------------------------------------------------------------------


def test_path_validation_rejects_escape(capsys):
    """An absolute --book path outside the repo root exits 2."""
    import sys
    if not sys.platform.startswith("win"):
        pytest.skip("C:\\Windows is Windows-specific")
    rc = align_mod.main([
        "--book", "C:\\Windows",
        "--chapter", "ch-01",
        "--locale", "ar",
    ])
    captured = capsys.readouterr()
    assert rc == 2
    assert "--book" in captured.err


def test_missing_words_json_exits_2(tmp_path, capsys):
    """A book with no words JSON exits 2 (input error)."""
    book_dir = tmp_path / "book_no_words"
    (book_dir / "chapters").mkdir(parents=True)
    (book_dir / "chapters" / "ch-01.md").write_text("Hello world.", encoding="utf-8")
    (book_dir / "figures").mkdir(parents=True)
    (book_dir / "figures" / "media-tts-manifest.json").write_text(
        json.dumps({"chunks": [
            {"chapter": "ch-01", "locale": "ar",
             "chunks": [{"duration_ms": 1000, "index": 1}]}
        ]}),
        encoding="utf-8",
    )
    rc = align_mod.main([
        "--book", str(book_dir),
        "--chapter", "ch-01",
        "--locale", "ar",
    ])
    captured = capsys.readouterr()
    assert rc == 2
    assert "words" in captured.err.lower()


# ---------------------------------------------------------------------------
# 4) --drift-floor CLI flag overrides the default 0.70 floor
# ---------------------------------------------------------------------------


def test_drift_floor_cli_flag_overrides_default(monkeypatch, tmp_path):
    """--drift-floor accepts a float and changes the pass/fail threshold.

    Fixture canonical / ASR pair have a SequenceMatcher ratio around 0.43,
    well below 0.70 (default floor -> exit 4) but above 0.40
    (--drift-floor 0.4 -> exit 0). Two book trees under tmp_path so the
    patch and the floor-setting variants do not collide on disk paths.
    """
    chapter_text = "hello there bright day morning"  # 32 chars
    # Engineered so the only matching block is "hello there " (12 chars).
    # ratio = 2 * 12 / (32 + 24) ~= 0.43.
    words = [
        {"word": "hello", "start": 0.10, "end": 0.40, "prob": 0.99},
        {"word": "there", "start": 0.50, "end": 0.80, "prob": 0.98},
        {"word": "fizzle", "start": 0.90, "end": 1.30, "prob": 0.97},
        {"word": "gizmo",  "start": 1.40, "end": 1.70, "prob": 0.96},
    ]

    # Variant A: default 0.70 floor -> exit 4.
    book_a = _book_with_alignment_fixture(
        tmp_path, slug="book_default", chapter_id="ch-03",
        locale="en", chapter_text=chapter_text, words=words,
        chunk_duration_ms=2000,
    )
    monkeypatch.setattr(align_mod, "REPO_ROOT", tmp_path)
    rc_default = align_mod.main([
        "--book", str(book_a), "--chapter", "ch-03", "--locale", "en",
    ])
    assert rc_default == 4, (
        "expected exit 4 on default floor (ratio~0.43 < 0.70), got %d"
        % rc_default
    )

    # Variant B: --drift-floor 0.4 -> exit 0.
    book_b = _book_with_alignment_fixture(
        tmp_path / "b", slug="book_low", chapter_id="ch-03",
        locale="en", chapter_text=chapter_text, words=words,
        chunk_duration_ms=2000,
    )
    rc_low = align_mod.main([
        "--book", str(book_b), "--chapter", "ch-03", "--locale", "en",
        "--drift-floor", "0.4",
    ])
    assert rc_low == 0, (
        "expected exit 0 with --drift-floor 0.4 (ratio~0.43 >= 0.4), got %d"
        % rc_low
    )
    srt_path = book_b / "chapters" / "ch-03-en.srt"
    assert srt_path.exists(), "SRT must be written when --drift-floor accepts"


# ---------------------------------------------------------------------------
# 5) Arabic text normalization collapses diacritics + alef / yaa forms
# ---------------------------------------------------------------------------


def test_normalize_arabic_collapses_diacritics_and_forms():
    """normalize_arabic() strips tashkil, normalises alef/yaa, drops tatweel.

    Pure unit test of the normalization helper: no run_align needed.
    Verifies the four normalizations documented in the module-level
    docstring happen in one call.
    """
    norm = align_mod.normalize_arabic

    # 1) Standard tashkil (fatha, kasra, damma, sukun, etc.) is stripped.
    #    [ U+0627 U+0644 U+0633 U+0651 ... ] -> bare letters
    assert norm("\u0627\u0644\u0633\u0651\u0644\u0627\u0645\u064f "
                "\u0639\u0644\u064a\u0643\u064f\u0645\u0652") == (
        "\u0627\u0644\u0633\u0644\u0627\u0645 \u0639\u0644\u064a\u0643\u0645"
    )
    # ^^ both should normalize to "as-salaam alaykum" (Greeting upon you).

    # 2) Alef forms (hamza-above, hamza-below, madda, alef-wasla) collapse
    #    to bare alef.
    for form in ("\u0623\u0644\u0641", "\u0625\u0644\u0641",
                 "\u0622\u0644\u0641", "\u0671\u0644\u0641"):
        assert norm(form) == "\u0627\u0644\u0641"

    # 3) Alef maksura (\u0649) collapses to yaa (\u064A).
    assert norm("\u0631\u0645\u0649") == "\u0631\u0645\u064a"

    # 4) Tatweel (\u0640) is removed entirely.
    assert norm("\u0643\u062a\u0627\u0628\u0640\u0640\u0640") == (
        "\u0643\u062a\u0627\u0628"
    )

    # 5) No-op on ASCII text, with optional lowercasing.
    assert norm("Hello world.") == "hello world"
    assert norm("") == ""


def test_arabic_chapter_aligns_after_normalization(monkeypatch, tmp_path):
    """A chunk whose canonical carries tashkil aligns with stripped ASR.

    Genuine-Arabic fixture: chapter text has full tashkil; ASR words (as a
    real faster-whisper transcript often does) do not. Without
    normalize_arabic the difflib ratio would be ~0.5 due to the diacritics
    in canonical_norm. After normalization both sides become identical
    and ratio == 1.0, well above the default 0.70 floor.
    """
    chapter_text = (
        "\u0627\u0644\u0633\u0651\u0644\u0627\u0645\u064f "
        "\u0639\u0644\u064a\u0643\u064f\u0645\u0652"
    )
    words = [
        {"word": "\u0627\u0644\u0633\u0644\u0627\u0645",
         "start": 0.10, "end": 0.50, "prob": 0.99},
        {"word": "\u0639\u0644\u064a\u0643\u0645",
         "start": 0.60, "end": 1.10, "prob": 0.98},
    ]
    book_dir = _book_with_alignment_fixture(
        tmp_path,
        slug="book_ar",
        chapter_id="ch-04",
        locale="ar",
        chapter_text=chapter_text,
        words=words,
        chunk_duration_ms=2000,
    )
    monkeypatch.setattr(align_mod, "REPO_ROOT", tmp_path)

    rc = align_mod.main([
        "--book", str(book_dir),
        "--chapter", "ch-04",
        "--locale", "ar",
    ])
    assert rc == 0, (
        "Arabic chapter with tashkil must align after normalize_arabic"
    )
    srt_path = book_dir / "chapters" / "ch-04-ar.srt"
    assert srt_path.exists(), "SRT must be written on a successful align"
    srt_text = srt_path.read_text(encoding="utf-8")
    # The normalised Arabic phrase (as-salaam alaykum, U+0627 U+0644 U+0633
    # U+0644 U+0627 U+0645 ... ) must appear in the SRT cues.
    assert "\u0627\u0644\u0633\u0644\u0627\u0645 \u0639\u0644\u064a\u0643\u0645" in srt_text, (
        "expected normalised Arabic phrase in SRT cues, got: %r" % srt_text
    )
