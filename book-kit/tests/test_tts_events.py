"""Tests for tts_events.py -- per-locale SentenceBoundary capture.

Only the offline-by-default tests run in CI. The live edge-tts test is
gated behind ``HAS_EDGE_TTS`` so an offline machine / a stripped venv
still gets a green run. The live test is a smoke -- it does not
guarantee provider behaviour beyond "SentenKBoundary events arrive in
the order edge-tts promises them".

Path layout: ``sentence_offsets_to_srt`` rejects paths outside the
repo root (the same gate ``media_tts.py --out`` enforces). Tests that
need to write an SRT must use a tmp dir under the repo root; the
``srt_tmp_path`` fixture below builds one under ``book-kit/``.
"""
import asyncio
import importlib.util
import os
import sys
from pathlib import Path

import pytest

# repo-root-relative paths
LIB_DIR = (
    Path(__file__).resolve().parents[1] / "book_workflow" / "lib"
)
sys.path.insert(0, str(LIB_DIR))

import errors as errors_mod  # noqa: E402
import tts_events as tts_events_mod  # noqa: E402


# ---------------------------------------------------------------------------
# Optional-import probe -- mirrors the module-level HAS_EDGE_TTS check.
# ---------------------------------------------------------------------------


HAS_EDGE_TTS = importlib.util.find_spec("edge_tts") is not None
HAS_KOKORO = importlib.util.find_spec("kokoro") is not None


# ---------------------------------------------------------------------------
# Fixture: a tmp dir under the repo root, so path-validation accepts it.
# ---------------------------------------------------------------------------


@pytest.fixture
def srt_tmp_path(tmp_path_factory):
    """A temporary directory under book-kit/ that the path validator accepts.

    pytest's stock ``tmp_path`` lives in ``%TEMP%/pytest-of-...`` which
    is OUTSIDE the repo root; ``sentence_offsets_to_srt`` would reject
    it as a path escape. This fixture builds the tmp dir under
    ``book-kit/.tmp_test_tts_events_<pid>/`` and self-cleans.
    """
    base = Path(__file__).resolve().parents[1] / ".tmp_test_tts_events"
    base.mkdir(exist_ok=True)
    sub = base / ("%d_%d" % (os.getpid(), id(object())))
    sub.mkdir(exist_ok=True)
    try:
        yield sub
    finally:
        # Best-effort cleanup; Windows file-locks sometimes block.
        try:
            for p in sub.iterdir():
                try:
                    p.unlink()
                except OSError:
                    pass
            sub.rmdir()
            if not any(base.iterdir()):
                base.rmdir()
        except OSError:
            pass


# ---------------------------------------------------------------------------
# 1) Empty input short-circuits to [] (no provider call, no event loop).
# ---------------------------------------------------------------------------


def test_collect_sentence_offsets_empty():
    """Empty string returns [] -- no Network calls, no exceptions."""
    result = asyncio.run(
        tts_events_mod.collect_sentence_offsets(
            "", "edge-tts", "ar-SA-HamedNeural", "ar"
        )
    )
    assert result == []
    # whitespace-only is also empty
    result2 = asyncio.run(
        tts_events_mod.collect_sentence_offsets(
            "   \n\n\t  ", "edge-tts", "ar-SA-HamedNeural", "ar"
        )
    )
    assert result2 == []


# ---------------------------------------------------------------------------
# 2) get_provider_event_format: known + unknown.
# ---------------------------------------------------------------------------


def test_get_provider_event_format_known_unknown():
    """Known providers map to canonical format strings; unknown raises."""
    assert tts_events_mod.get_provider_event_format("edge-tts") == "ms-windows"
    assert tts_events_mod.get_provider_event_format("kokoro") == "kokoro-v0.9"
    # Unknown provider -> MediaPipelineError(exit_code=2) + hint.
    with pytest.raises(errors_mod.MediaPipelineError) as exc:
        tts_events_mod.get_provider_event_format("not-a-real-provider")
    assert exc.value.exit_code == 2
    assert "not-a-real-provider" in exc.value.hint


# ---------------------------------------------------------------------------
# 3) sentence_offsets_to_srt: invalid path rejects with exit 2.
# ---------------------------------------------------------------------------


def test_sentence_offsets_to_srt_invalid_path(srt_tmp_path):
    """Path containing '..' or escaping the repo root exits 2."""
    rc = tts_events_mod.sentence_offsets_to_srt(
        [], str(srt_tmp_path / ".." / "outside.srt")
    )
    assert rc == 2
    # Absolute path outside the repo root also fails.
    rc2 = tts_events_mod.sentence_offsets_to_srt(
        [], "C:\\Windows\\Temp\\escape.srt"
    )
    assert rc2 == 2


# ---------------------------------------------------------------------------
# 4) sentence_offsets_to_srt happy path: empty + populated.
# ---------------------------------------------------------------------------


def test_sentence_offsets_to_srt_happy_path(srt_tmp_path):
    """Empty offsets -> empty SRT body; populated offsets -> SRT file."""
    target = srt_tmp_path / "out.srt"
    rc = tts_events_mod.sentence_offsets_to_srt([], str(target))
    assert rc == 0
    assert target.exists()
    # Empty offsets -> valid empty file (no cue rows).
    assert target.read_text(encoding="utf-8") == ""

    # Populated path
    target2 = srt_tmp_path / "populated.srt"
    offsets = [
        tts_events_mod.SentenceOffset(
            text="First sentence.",
            char_offset_start=0,
            char_offset_end=16,
            audio_offset_ms=0,
        ),
        tts_events_mod.SentenceOffset(
            text="Second sentence.",
            char_offset_start=16,
            char_offset_end=32,
            audio_offset_ms=2000,
        ),
    ]
    rc2 = tts_events_mod.sentence_offsets_to_srt(offsets, str(target2))
    assert rc2 == 0
    body = target2.read_text(encoding="utf-8")
    # SRT cue shape: index line, time-range line, text line, blank line.
    assert "00:00:00,000 --> 00:00:02,000" in body
    assert "First sentence." in body
    assert "00:00:02,000 --> 00:00:03,000" in body
    assert "Second sentence." in body


# ---------------------------------------------------------------------------
# 5) TTSEventCollector push() shape -- the unit-test of the collector alone.
# ---------------------------------------------------------------------------


def test_collector_push_skips_audio_and_wordboundary():
    """Non-SentenceBoundary events (audio + WordBoundary) are dropped."""
    coll = tts_events_mod.TTSEventCollector("hello world")
    # Audio chunks: ignored.
    coll.push({"type": "audio", "data": b"\x00\x01"})
    # WordBoundary chunks: ignored (sentence-only contract).
    coll.push({"type": "WordBoundary", "text": "hello", "offset_ms": 100})
    # SentenceBoundary chunk: ingested. Public contract: offset_ms.
    coll.push(
        {
            "type": "SentenceBoundary",
            "text": "hello world",
            "offset_ms": 500,
            "duration_ms": 200,
        }
    )
    offsets = coll.offsets()
    assert len(offsets) == 1
    assert offsets[0].text == "hello world"
    assert offsets[0].audio_offset_ms == 500
    assert offsets[0].char_offset_start == 0
    assert offsets[0].char_offset_end == 11


def test_collector_push_unsourced_text_records_minus_one():
    """When the boundary text is not in the source we record (-1, -1)."""
    coll = tts_events_mod.TTSEventCollector("plain text")
    coll.push(
        {
            "type": "SentenceBoundary",
            "text": "this-was-normalised-away-by-ssml",
            "offset_ms": 1250,
        }
    )
    offsets = coll.offsets()
    assert len(offsets) == 1
    assert offsets[0].char_offset_start == -1
    assert offsets[0].char_offset_end == -1
    assert offsets[0].audio_offset_ms == 1250


# ---------------------------------------------------------------------------
# 6) Live edge-tts synthesis: 2 sentences -> 2 offsets.
#    Skipped when edge-tts is not installed.
# ---------------------------------------------------------------------------


@pytest.mark.skipif(
    not HAS_EDGE_TTS, reason="edge-tts python package is not installed"
)
def test_collect_sentence_offsets_en():
    """Two English sentences produce at least two SentenceOffset rows.

    edge-tts is permitted to round boundaries at the clause level --
    a 2-sentence input can yield >=2 rows (one per real SentenceBoundary).
    The exact count depends on edge-tts's internal segmentation; we
    assert >=2 and trust the audio offset is below a sane ceiling.
    """
    text = "Hello world. This is a second sentence."
    offsets = asyncio.run(
        tts_events_mod.collect_sentence_offsets(
            text, "edge-tts", "en-US-EmmaMultilingualNeural", "en"
        )
    )
    assert len(offsets) >= 2
    for off in offsets:
        assert isinstance(off, tts_events_mod.SentenceOffset)
        # Sanity ceiling: 1 hour of audio == 3_600_000 ms. Real output
        # for two short sentences is ~1-3 seconds.
        assert 0 <= off.audio_offset_ms < 3_600_000
    # Boundaries arrive in monotonic order.
    audio_offsets = [off.audio_offset_ms for off in offsets]
    assert audio_offsets == sorted(audio_offsets)


# ---------------------------------------------------------------------------
# 7) Known and actual code paths agree -- the API is exported.
# ---------------------------------------------------------------------------


def test_public_api_exports():
    """Public names from the dispatch contract are present on the module."""
    required = [
        "SentenceOffset",
        "TTSEventCollector",
        "collect_sentence_offsets",
        "sentence_offsets_to_srt",
        "get_provider_event_format",
    ]
    for name in required:
        assert hasattr(tts_events_mod, name), (
            "tts_events module must export %r per P4T5 dispatch" % name
        )
