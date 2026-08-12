"""errors.py -- shared actionable error helper for book2media scripts.

One-line hintecatalog + a tiny ``MediaPipelineError`` exception that
carries both a ``hint`` (actionable string for the user) and an
``exit_code`` (the convention 0/2/3/4 the Phase 9 CLIs honour).

Public API:
    MediaPipelineError -- the standard exception, with .hint and .exit_code.
    raise_actionable    -- raises MediaPipelineError(error_kind, **ctx).
    format_hint         -- returns the hint string without raising.
    HINTS               -- dict of error_kind -> template string.

EXIT CODES (kept in lock-step with media_tts.py / voices.py / phase 9 scripts)
    0  success
    2  input error (bad path, malformed manifest, unknown provider)
    3  missing dep (library absent from venv, font not installed)
    4  internal/runtime (provider raised, runtime failure)

ASCII-ONLY: every byte is ASCII per the P1-P18 hardening rules.
"""
from __future__ import annotations

# ---------------------------------------------------------------------------
# UTF-8 stdio force (P4 #15 / P5 #22 inheritance) -- runs before any print().
# ---------------------------------------------------------------------------

import sys
import io
from types import MappingProxyType

for _stream in (sys.stdout, sys.stderr):
    try:
        _stream.reconfigure(encoding="utf-8")
    except (AttributeError, OSError, io.UnsupportedOperation):
        # Already detached (e.g. captured by pytest) or unsupported.
        pass


# ---------------------------------------------------------------------------
# Hints catalog (error_kind -> format template)
#
# Templates use ``{ctx_key}`` placeholders resolved at raise-time via
# ``**ctx``. Unknown placeholders in the template raise a clear
# ``MediaPipelineError`` of their own rather than silently producing a
# broken message -- "fail loud at the configuration step" beats "wrong
# hint at the user step".
#
# Both HINTS and DEFAULT_EXIT_CODES are exposed as ``MappingProxyType``
# so importers can read but not mutate. The phase 9 review flagged a
# mutable-module-dict risk (Phase 2b WARN-1); the frozen view keeps
# backward compat with code that does ``HINTS[kind]`` lookups.
# ---------------------------------------------------------------------------

_HINTS_MUTABLE: dict = {
    "missing_amiri_font": (
        "Amiri font not found at {path}; install via "
        "book-kit/book_workflow/scripts/install_amiri.py or download from "
        "https://github.com/aliftype/amiri/releases and drop the .ttf into "
        "{path}"
    ),
    "voice_unavailable": (
        "voice {voice!r} not registered for locale={locale!r} via "
        "provider={provider!r}; check "
        "books/<slug>/media-locale-manifest.json::products[].voice and "
        "agents_manager/book2media-orchestrator/providers.yaml::"
        "tts.{locale}.voice"
    ),
    "schema_invalid": (
        "media-locale-manifest.json failed schema validation at "
        "{path}:{field}; run "
        "book-kit/book_workflow/scripts/validate_media_manifest.py validate "
        "<path> for the full error list"
    ),
    "audio_empty": (
        "synthesized audio was empty for chapter={chapter!r} "
        "locale={locale!r}; check TTS provider connectivity and chunker "
        "output length (see books/<slug>/figures/media-tts-manifest.json)"
    ),
    "comfyui_not_running": (
        "ComfyUI is not reachable at {url}; start ComfyUI Desktop or set "
        "COMFYUI_URL env var to your local instance"
    ),
    "unsupported_locale": (
        "locale={locale!r} is not registered in providers.yaml; add a row "
        "under agents_manager/book2media-orchestrator/providers.yaml::"
        "tts.<locale> with provider/voice/grade"
    ),
}
HINTS: MappingProxyType = MappingProxyType(_HINTS_MUTABLE)


# Default exit code per error_kind. Centralised so the CLIs and the
# tests cannot drift apart. Keys absent from this dict get exit_code=2
# (input error) as a conservative default.
_DEFAULT_EXIT_CODES_MUTABLE: dict = {
    "missing_amiri_font": 3,    # missing dep
    "voice_unavailable": 4,     # internal/runtime (provider said no)
    "schema_invalid": 2,        # input error
    "audio_empty": 4,           # internal/runtime
    "comfyui_not_running": 3,   # missing dep (server not up)
    "unsupported_locale": 2,    # input error
}
DEFAULT_EXIT_CODES: MappingProxyType = MappingProxyType(_DEFAULT_EXIT_CODES_MUTABLE)


# ---------------------------------------------------------------------------
# The standard exception
# ---------------------------------------------------------------------------


class MediaPipelineError(Exception):
    """Standard phase-9 error with both ``hint`` and ``exit_code`` attached.

    Catching code should ``print(err.hint, file=sys.stderr); sys.exit(
    err.exit_code)`` so the user sees the actionable message rather than
    a Python traceback.
    """

    def __init__(self, hint, exit_code=2):
        # Self.hint first so __str__ returns it (single-line, never traceback).
        self.hint = hint
        self.exit_code = int(exit_code)
        super().__init__(self.hint)

    def __repr__(self):
        return "%s(exit_code=%d, hint=%r)" % (
            type(self).__name__, self.exit_code, self.hint
        )


# ---------------------------------------------------------------------------
# Public helpers
# ---------------------------------------------------------------------------


def format_hint(error_kind, **ctx):
    """Return the hint string for ``error_kind``, parameterised by ``ctx``.

    Unknown ``error_kind`` returns a fallback string naming the known
    kinds rather than raising -- callers that want hard failure should
    use :func:`raise_actionable` instead.
    """
    template = HINTS.get(error_kind)
    if template is None:
        return (
            "errors.format_hint: unknown error_kind=%r; known=%s"
            % (error_kind, sorted(HINTS.keys()))
        )
    try:
        return template.format(**ctx)
    except KeyError as exc:
        return (
            "errors.format_hint: missing ctx key %r for kind=%r "
            "(hint expects: %s)"
            % (exc.args[0], error_kind, _ctx_keys(template))
        )


def raise_actionable(error_kind, **ctx):
    """Raise :class:`MediaPipelineError` with the canonical hint + exit code.

    Never returns (``NoReturn``); intended as ``raise raise_actionable(
    ...,)`` shorthand -- but the leading ``raise`` is redundant here,
    so call sites look like ``errors.raise_actionable(...)``.
    """
    exit_code = DEFAULT_EXIT_CODES.get(error_kind, 2)
    hint = format_hint(error_kind, **ctx)
    raise MediaPipelineError(hint, exit_code)


def _ctx_keys(template):
    """Best-effort extraction of ``{placeholder}`` names from a format string."""
    import string

    formatter = string.Formatter()
    return sorted({fname for _, fname, _, _ in formatter.parse(template) if fname})
