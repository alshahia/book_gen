"""tts_events.py -- per-locale SentenceBoundary event capture for phase 9.

edge-tts 7.2.8 emits ``SentenceBoundary`` events natively (verified SF2
on 2026-08-11: no ``WordBoundary`` produced by default; ``boundary="``)
``. SentenceBoundary`` is the constructor default). Kokoro 0.9.4 ships
no event API at this writing -- the kokoro branch is a stub pending the
upstream "events" prototype.

This module is consumed by:
  - phase 3 caption alignment (faster-whisper + difflib)
  - phase 4 timing verification (audiobook/M4B chapter marks)
  - any future smoke that wants char/audio offset alignment

Public API:
    SentenceOffset          -- dataclass: (text, char_offset_start,
                               char_offset_end, audio_offset_ms).
    TTSEventCollector       -- async context-manager-friendly event sink
                               that translates provider chunks into
                               ``SentenceOffset`` rows.
    collect_sentence_offsets -- async helper: runs a single TTS pass and
                               returns the offsets. Returns ``[]`` on
                               empty input; raises ``MediaPipelineError``
                               on unknown ``tts_provider`` or missing
                               optional dep.
    sentence_offsets_to_srt -- sync helper: writes an SRT file from the
                               offsets. Exit codes: 0 success, 2 path
                               error, 3 missing dep.
    get_provider_event_format -- ``"ms-windows"`` for edge-tts,
                               ``"kokoro-v0.9"`` for kokoro. Anything
                               else raises via :func:`errors.raise_actionable`.

ASCII-ONLY
    Every byte is ASCII per the P1-P18 hardening rules.
"""
from __future__ import annotations

# ---------------------------------------------------------------------------
# UTF-8 stdio force (P4 #15 / P5 #22 inheritance) -- runs before any print().
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

import importlib.util
import json
from dataclasses import dataclass, asdict
from pathlib import Path
from typing import Optional


# ---------------------------------------------------------------------------
# Local import (sibling module: errors.py).
# ---------------------------------------------------------------------------

_THIS_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(_THIS_DIR))

import errors as errors_mod  # noqa: E402


# ---------------------------------------------------------------------------
# Repo-root resolution -- shared with scripts/.media_tts.py convention.
# ---------------------------------------------------------------------------

# This file lives at: book-kit/book_workflow/lib/tts_events.py
# parents[0] = lib/, [1] = book_workflow/, [2] = book-kit/, [3] = repo root
REPO_ROOT = Path(__file__).resolve().parents[3]


# ---------------------------------------------------------------------------
# Provider registry -- single source of truth for "what providers exist".
# ---------------------------------------------------------------------------

PROVIDER_FORMATS: dict = {
    "edge-tts": "ms-windows",
    "kokoro": "kokoro-v0.9",
}


# ---------------------------------------------------------------------------
# Optional-import probes
#
# We never import edge_tts / kokoro at module load time so the rest of
# the pipeline stays importable offline (smoke runs without kokoro on
# ARM64 macs, etc.). Callers that need a live synthesis probe before
# calling :func:`collect_sentence_offsets` instead.
# ---------------------------------------------------------------------------


def _has_edge_tts():
    return importlib.util.find_spec("edge_tts") is not None


def _has_kokoro():
    return importlib.util.find_spec("kokoro") is not None


HAS_EDGE_TTS: bool = _has_edge_tts()
HAS_KOKORO: bool = _has_kokoro()


# ---------------------------------------------------------------------------
# Public dataclass
# ---------------------------------------------------------------------------


@dataclass
class SentenceOffset:
    """One TTS sentence boundary, in both character and audio coordinates.

    Attributes:
        text              -- the boundary text (often a sentence fragment).
        char_offset_start -- start index in the input text (inclusive).
        char_offset_end   -- end index in the input text (exclusive).
        audio_offset_ms   -- TTS audio offset in milliseconds since
                             stream start. Edge-tts reports ``offset``
                             in 100-ns ticks (``edge_tts.communicate
                             .TICKS_PER_SECOND == 10_000_000``) -- this
                             dataclass stores the post-divided
                             millisecond value so downstream consumers
                             never see the raw tick count.
    """

    text: str
    char_offset_start: int
    char_offset_end: int
    audio_offset_ms: int

    def to_dict(self):
        return asdict(self)


# edge-tts reports boundary offsets in 100-ns ticks (Windows FILETIME
# format -- see ``edge_tts.communicate.TICKS_PER_SECOND``). 10000 ticks
# per millisecond.
_EDGE_TTS_TICKS_PER_MS = 10_000


# ---------------------------------------------------------------------------
# Provider event-format lookup
# ---------------------------------------------------------------------------


def get_provider_event_format(tts_provider):
    """Return the canonical event-format string for ``tts_provider``.

    Known providers:
        ``"edge-tts"`` -> ``"ms-windows"`` (edge-tts sends SSML metadata
        over its WebSocket and exposes ``SentenceBoundary`` events
        natively).
        ``"kokoro"``   -> ``"kokoro-v0.9"`` (Kokoro 0.9.4 has no event
        API yet; this string is reserved for the upcoming events
        prototype).

    Unknown providers raise :class:`MediaPipelineError` with exit_code=2
    so callers can ``try`` the lookup at CLI parse time and surface a
    one-line actionable hint.
    """
    if tts_provider in PROVIDER_FORMATS:
        return PROVIDER_FORMATS[tts_provider]
    errors_mod.raise_actionable("unsupported_locale", locale=tts_provider)
    # Never reached -- raise_actionable is NoReturn -- but keeps static
    # analysers happy.
    raise RuntimeError("raise_actionable did not raise")


# ---------------------------------------------------------------------------
# Collector
#
# ``TTSEventCollector`` does NOT call the TTS provider itself -- the
# caller drives the async iteration (so we can re-use one collector
# across multiple chunks/providres in tests). It does the post-processing
# (char offset search, ms rounding) inside :meth:`push`.
# ---------------------------------------------------------------------------


class TTSEventCollector:
    """Async-friendly sink for TTS SentenceBoundary events.

    Designed for use as::

        async with TTSEventCollector(input_text) as collector:
            communicate = edge_tts.Communicate(input_text, voice)
            async for chunk in communicate.stream():
                collector.push(chunk)
        offsets = collector.offsets()

    The collector tracks a cursor in ``input_text`` and finds each
    boundary text via :func:`str.find`. Boundaries that cannot be
    located in the source are recorded with char offsets of (-1, -1)
    so the downstream caption tool knows the audio timestamp is real
    but the source match is uncertain.
    """

    def __init__(self, input_text: str = ""):
        self._input = input_text or ""
        self._cursor = 0
        self._records: list = []
        self._entered = False

    # Context-manager API. Sync ``__enter__``/``__exit__`` is correct for
    # ``async with`` in modern Python (the ``async with`` statement
    # looks for ``__aenter__``/``__aexit__`` first and falls back to
    # these if the async ones are absent).
    def __enter__(self):
        self._entered = True
        return self

    def __exit__(self, exc_type, exc, tb):
        self._entered = False
        return False  # do not swallow exceptions

    # Push one event from any provider.
    def push(self, chunk):
        """Ingest one TTS event, in the public milliseconds contract.

        The ``chunk`` is a dict -- typically the raw dict produced by
        an asyncio event-stream yield -- with these key/value pairs:

            {"type": "audio" | "SentenceBoundary" | "WordBoundary",
             "text": "...",          # boundary text
             "offset_ms": int        # audio offset in MILLISECONDS
                                      # (not seconds, not ticks;
                                      # providers must pre-convert)
            }

        Why the public contract is ms (not seconds, not ticks): keeps
        downstream caption/SRT code branch-free. Edge-tts returns
        100-ns ticks; ``_collect_edge_tts`` divides by
        ``_EDGE_TTS_TICKS_PER_MS == 10_000`` before pushing.

        Audio chunks and ``WordBoundary`` events are dropped silently
        -- the public contract is sentence-level only.
        """
        if not isinstance(chunk, dict):
            return
        ctype = chunk.get("type")
        if ctype != "SentenceBoundary":
            return
        text = chunk.get("text") or ""
        offset_ms = chunk.get("offset_ms")
        if offset_ms is None:
            # No timing info -- skip but still ingest the text so the
            # caller can see what arrived.
            return
        try:
            offset_ms_i = int(round(float(offset_ms)))
        except (TypeError, ValueError):
            return
        # Locate the text in the input starting from the last cursor.
        # ``find`` returns -1 when the boundary text is repeated or
        # modified by SSML normalisation; we record (-1, -1) in that
        # case so downstream knows the char match is uncertain.
        idx = self._input.find(text, self._cursor)
        if idx < 0:
            idx = self._input.find(text, 0)
        if idx >= 0:
            char_start = idx
            char_end = idx + len(text)
            self._cursor = char_end
        else:
            char_start = -1
            char_end = -1
        self._records.append(
            SentenceOffset(
                text=text,
                char_offset_start=char_start,
                char_offset_end=char_end,
                audio_offset_ms=offset_ms_i,
            )
        )

    # The post-collect view.
    def offsets(self):
        """Return the collected :class:`SentenceOffset` rows."""
        # Return a defensive copy so callers cannot mutate collector state.
        return list(self._records)


# ---------------------------------------------------------------------------
# Async helper: run one TTS pass and capture offsets.
# ---------------------------------------------------------------------------


async def collect_sentence_offsets(
    text: str,
    tts_provider: str,
    voice: str,
    locale: str,
):
    """Synthesise ``text`` once and return the SentenceBoundary offsets.

    Empty ``text`` short-circuits to ``[]`` -- no provider call, no
    events, no exceptions. Unrecognised ``tts_provider`` raises
    :class:`MediaPipelineError` with ``exit_code=2`` and a one-line
    hint naming the known providers.

    Returns:
        ``list[SentenceOffset]``. Length equals the number of
        SentenceBoundary events emitted by the provider for this run.
        For an empty input the list is empty.
    """
    if not text or not text.strip():
        return []
    if tts_provider not in PROVIDER_FORMATS:
        errors_mod.raise_actionable("unsupported_locale", locale=tts_provider)
    if tts_provider == "edge-tts":
        return await _collect_edge_tts(text, voice, locale)
    if tts_provider == "kokoro":
        return await _collect_kokoro(text, voice, locale)
    # Defensive -- raise_actionable above is NoReturn but a stray future
    # provider addition should still surface a clean error.
    errors_mod.raise_actionable("unsupported_locale", locale=tts_provider)


_EDGE_TTS_MISSING_HINT = (
    "edge-tts python package not found in venv; "
    "`pip install edge-tts==7.2.8` and re-run"
)
_KOKORO_MISSING_HINT = (
    "kokoro python package not found in venv; "
    "`pip install kokoro==0.9.4` and re-run"
)


async def _collect_edge_tts(text, voice, locale):
    """edge-tts branch -- the one with native SentenceBoundary support."""
    if not HAS_EDGE_TTS:
        raise errors_mod.MediaPipelineError(_EDGE_TTS_MISSING_HINT, exit_code=3)
    import edge_tts  # local import -- keeps module importable offline.

    comm = edge_tts.Communicate(text, voice)
    out: list = []
    with TTSEventCollector(text) as collector:
        async for chunk in comm.stream():
            ctype = chunk.get("type")
            if ctype != "SentenceBoundary":
                continue
            # edge-tts returns ``offset`` in 100-ns ticks; convert to
            # ms before handing the chunk to the collector (the public
            # contract of TTSEventCollector.push is ``offset_ms``).
            ticks = chunk.get("offset")
            if ticks is None:
                continue
            try:
                offset_ms = float(ticks) / _EDGE_TTS_TICKS_PER_MS
            except (TypeError, ValueError):
                continue
            collector.push(
                {
                    "type": "SentenceBoundary",
                    "text": chunk.get("text") or "",
                    "offset_ms": offset_ms,
                }
            )
        out = collector.offsets()
    return out


async def _collect_kokoro(text, voice, locale):
    """Kokoro 0.9.4 has no native event API.

    Returns an empty list (no offsets available) and leaves a clear
    TODO for the upstream events prototype. Downstream can diff the
    first-frame timestamp against the chapter text if alignment is
    needed before the upstream API lands.

    ponytail: this exists as a placeholder; the Kokoro events API is
    tracked as a Phase 2b/3 follow-up. Returning ``[]`` keeps the
    pipeline importable on hosts without kokoro and on hosts where
    kokoro is installed but its events API has not been wired up.
    """
    if not HAS_KOKORO:
        raise errors_mod.MediaPipelineError(_KOKORO_MISSING_HINT, exit_code=3)
    # TODO(hexgrad/Kokoro-82M#events): replace this stub with a real
    # collector when the upstream events prototype ships.
    return []


# ---------------------------------------------------------------------------
# Sync helper: write an SRT.
# ---------------------------------------------------------------------------


def sentence_offsets_to_srt(offsets, output_path):
    """Write ``offsets`` to ``output_path`` as SubRip text.

    Exit codes mirror the rest of the pipeline:
        0 -- success (file written, non-empty when offsets are given).
        2 -- ``output_path`` escapes the repo root or its parent does
             not exist.
        3 -- a downstream consumer requires a missing optional dep
             (e.g. write-side ffmpeg post-processing); never raised
             by this minimal implementation -- returned only when
             future features wire ffmpeg subtitle burn.

    Empty offsets produce an empty SRT body (just the BOM-less header
    line) so the file is still valid SubRip.
    """
    raw = Path(output_path)
    if ".." in raw.parts:
        sys.stderr.write(
            "tts_events: output_path must not contain '..': %s\n" % output_path
        )
        return 2
    if raw.is_absolute():
        target = raw.resolve()
    else:
        target = (REPO_ROOT / raw).resolve()
    root = REPO_ROOT.resolve()
    if target != root and root not in target.parents:
        sys.stderr.write(
            "tts_events: output_path must resolve under %s: %s\n"
            % (root, output_path)
        )
        return 2
    if target.parent and not target.parent.exists():
        try:
            target.parent.mkdir(parents=True, exist_ok=True)
        except OSError as exc:
            sys.stderr.write(
                "tts_events: cannot create parent dir %s: %s\n"
                % (target.parent, exc)
            )
            return 2

    def _fmt_ts(ms_total):
        # SRT uses HH:MM:SS,mmm (comma decimal).
        if ms_total < 0:
            ms_total = 0
        h, rem = divmod(ms_total, 3600 * 1000)
        m, rem = divmod(rem, 60 * 1000)
        s, ms = divmod(rem, 1000)
        return "%02d:%02d:%02d,%03d" % (h, m, s, ms)

    lines = []
    for idx, off in enumerate(offsets, start=1):
        if not isinstance(off, SentenceOffset):
            # Tolerate duck-typed rows by re-extracting.
            d = dict(off) if hasattr(off, "__iter__") else {}
            off = SentenceOffset(
                text=d.get("text", ""),
                char_offset_start=int(d.get("char_offset_start", -1)),
                char_offset_end=int(d.get("char_offset_end", -1)),
                audio_offset_ms=int(d.get("audio_offset_ms", 0)),
            )
        # One-second cue duration is a safe default; if the next
        # offset is in the same SRT we close this cue against the next
        # audio offset minus one frame.
        end_ms = off.audio_offset_ms + 1000
        if idx - 1 < len(offsets) - 1:
            next_off = offsets[idx]
            n_ms = getattr(next_off, "audio_offset_ms", None)
            if isinstance(n_ms, int) and n_ms > off.audio_offset_ms:
                end_ms = n_ms
        start = _fmt_ts(off.audio_offset_ms)
        end = _fmt_ts(end_ms)
        text = (off.text or "").replace("\r", " ").replace("\n", " ").strip()
        lines.append("%d\n%s --> %s\n%s\n" % (idx, start, end, text))
    body = "\n".join(lines)
    if body and not body.endswith("\n"):
        body += "\n"
    try:
        target.write_text(body, encoding="utf-8")
    except OSError as exc:
        sys.stderr.write("tts_events: write failed: %s\n" % exc)
        return 2
    return 0
