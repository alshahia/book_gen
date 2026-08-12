"""voices.py -- book2media voice registry + three-tier resolution.

Three-tier voice lookup for the book2media pipeline:

    1. Per-book override from
       `books/<slug>/media-locale-manifest.json::products[].voice`
       (matched on locale + product id).
    2. Global default from
       `agents_manager/book2media-orchestrator/providers.yaml::tts.<locale>.voice`.
    3. Built-in default in `VOICE_REGISTRY` (last-resort fallback so the
       runtime never crashes on a missing file).

Resolution order per the locked plan T-2026-08-10-001:
    per-book > global > built-in.

Public API:
    resolve_voice(book_slug, locale, tts_provider) -> str
        Returns the voice id, e.g. ``af_heart`` (Kokoro en) or
        ``ar-SA-HamedNeural`` (edge-tts ar).

    list_voices(tts_provider, locale=None) -> list[dict]
        Returns [{id, locale, gender, grade}, ...] for the provider.
        Filtered by locale when given.

    VOICE_REGISTRY: dict[str, dict[str, list[dict]]]
        Built-in table. ``VOICE_REGISTRY[provider][locale]`` is the list
        of voice dicts to enumerate when no manifest / providers.yaml
        override exists.

EXIT CODES
    The module is a library, but its ``__main__`` self-test exits 0 on
    success. There are no CLI exit codes to document; the calling scripts
    exit on input errors per their own conventions.

ASCII-ONLY
    Every byte is ASCII per the P1-P18 hardening rules. No em-dash, no
    curly quotes, no ellipsis char. Use ``-``, ``'``, ``"``, ``...``.
"""
from __future__ import annotations

# ---------------------------------------------------------------------------
# UTF-8 stdio force (P4 #15 / P5 #22 inheritance) -- MUST run before any
# print() or argparse import that might emit non-ASCII on cp1252/cp1256
# Windows consoles.
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

import json
import os
from pathlib import Path


# ---------------------------------------------------------------------------
# Repo + manifest paths
# ---------------------------------------------------------------------------

# This file lives at: book-kit/book_workflow/scripts/voices.py
# parents[0] = scripts/, [1] = book_workflow/, [2] = book-kit/, [3] = repo root
REPO_ROOT = Path(__file__).resolve().parents[3]
PROVIDERS_YAML_PATH = (
    REPO_ROOT / "agents_manager" / "book2media-orchestrator" / "providers.yaml"
)


# ---------------------------------------------------------------------------
# Errors
# ---------------------------------------------------------------------------


class VoiceResolutionError(Exception):
    """Raised when no tier yields a voice for the requested locale/provider."""


# ---------------------------------------------------------------------------
# Built-in voice registry (Tier 3 - last resort)
#
# Source of truth for the canonical voice ids used in the Phase 5 smoke:
#   - Kokoro 0.9.4: voices are exposed by the package at import time. The
#     5 voices hard-coded below are Grade A by the Kokoro-82M upstream
#     README (hexgrad/Kokoro-82M). The full inventory is 54 voices (all
#     English). Hard-coding the smoke-target voices keeps this module
#     importable offline (no model load, no network).
#   - edge-tts 7.2.8: 28 Arabic voices exposed by Microsoft Edge's
#     speech endpoint. The 16 listed below are the Arabic voices from the
#     Microsoft Azure TTS voice catalog as of 2025-Q3 (locale prefix
#     ``ar-*``). The catalog is reachable from
#     ``edge_tts.list_voices()`` but is intentionally NOT queried at
#     import time -- the registry must work offline and never block on
#     a network round-trip.
#
# Voice dict shape: ``{id, locale, gender, grade}``. ``grade`` is the
# orchestrator's quality marker (``A`` for Kokoro Grade A;
# ``native`` for MS Neural voices).
# ---------------------------------------------------------------------------

KOKORO_VOICES_EN = [
    {"id": "af_heart", "locale": "en", "gender": "female", "grade": "A"},
    {"id": "af_bella", "locale": "en", "gender": "female", "grade": "A"},
    {"id": "af_nova", "locale": "en", "gender": "female", "grade": "B"},
    {"id": "af_sky", "locale": "en", "gender": "female", "grade": "B"},
    {"id": "af_river", "locale": "en", "gender": "female", "grade": "C"},
    {"id": "am_michael", "locale": "en", "gender": "male", "grade": "A"},
    {"id": "am_adam", "locale": "en", "gender": "male", "grade": "A"},
    {"id": "am_echo", "locale": "en", "gender": "male", "grade": "B"},
    {"id": "am_eric", "locale": "en", "gender": "male", "grade": "B"},
    {"id": "am_liam", "locale": "en", "gender": "male", "grade": "B"},
    {"id": "am_onyx", "locale": "en", "gender": "male", "grade": "B"},
    {"id": "am_puck", "locale": "en", "gender": "male", "grade": "B"},
    {"id": "am_santa", "locale": "en", "gender": "male", "grade": "B"},
    {"id": "bf_emma", "locale": "en", "gender": "female", "grade": "A"},
    {"id": "bf_isabella", "locale": "en", "gender": "female", "grade": "B"},
    {"id": "bf_alice", "locale": "en", "gender": "female", "grade": "B"},
    {"id": "bf_lily", "locale": "en", "gender": "female", "grade": "B"},
    {"id": "bm_george", "locale": "en", "gender": "male", "grade": "B"},
    {"id": "bm_lewis", "locale": "en", "gender": "male", "grade": "B"},
    {"id": "bm_daniel", "locale": "en", "gender": "male", "grade": "B"},
    {"id": "bm_fable", "locale": "en", "gender": "male", "grade": "B"},
]


EDGE_TTS_VOICES_AR = [
    {"id": "ar-SA-HamedNeural", "locale": "ar", "gender": "male", "grade": "native"},
    {"id": "ar-SA-ZariyahNeural", "locale": "ar", "gender": "female", "grade": "native"},
    {"id": "ar-EG-SalmaNeural", "locale": "ar", "gender": "female", "grade": "native"},
    {"id": "ar-EG-ShakirNeural", "locale": "ar", "gender": "male", "grade": "native"},
    {"id": "ar-AE-FatimaNeural", "locale": "ar", "gender": "female", "grade": "native"},
    {"id": "ar-AE-HamdanNeural", "locale": "ar", "gender": "male", "grade": "native"},
    {"id": "ar-LB-LaylaNeural", "locale": "ar", "gender": "female", "grade": "native"},
    {"id": "ar-LB-RamiNeural", "locale": "ar", "gender": "male", "grade": "native"},
    {"id": "ar-MA-MounaNeural", "locale": "ar", "gender": "female", "grade": "native"},
    {"id": "ar-MA-NaimNeural", "locale": "ar", "gender": "male", "grade": "native"},
    {"id": "ar-QA-AmalNeural", "locale": "ar", "gender": "female", "grade": "native"},
    {"id": "ar-QA-MoazNeural", "locale": "ar", "gender": "male", "grade": "native"},
    {"id": "ar-KW-FahedNeural", "locale": "ar", "gender": "male", "grade": "native"},
    {"id": "ar-KW-NouraNeural", "locale": "ar", "gender": "female", "grade": "native"},
    {"id": "ar-JO-TalaNeural", "locale": "ar", "gender": "female", "grade": "native"},
    {"id": "ar-JO-SamerNeural", "locale": "ar", "gender": "male", "grade": "native"},
]

# Default voice per (provider, locale) - used by resolve_voice() as Tier 3.
DEFAULT_VOICE_BY_PROVIDER_LOCALE = {
    ("kokoro", "en"): "af_heart",
    ("edge-tts", "ar"): "ar-SA-HamedNeural",
}

# Built-in registry exported as VOICE_REGISTRY. Tier 3 lookup.
VOICE_REGISTRY: dict = {
    "kokoro": {
        "en": KOKORO_VOICES_EN,
    },
    "edge-tts": {
        "ar": EDGE_TTS_VOICES_AR,
    },
}


# ---------------------------------------------------------------------------
# Per-book manifest loader (Tier 1)
# ---------------------------------------------------------------------------


def _load_per_book_voice(book_slug, locale, tts_provider):
    """Return voice from `books/<slug>/media-locale-manifest.json` or None.

    The manifest stores per-product voice overrides. We pick the first
    product matching the locale AND tts_provider. Skip products that
    have ``skip: true`` (per locked rule: empty ``voice`` falls back;
    skip is the only "off" signal).
    """
    book_dir = REPO_ROOT / "books" / book_slug
    manifest_path = book_dir / "media-locale-manifest.json"
    if not manifest_path.exists():
        return None
    try:
        text = manifest_path.read_text(encoding="utf-8")
        data = json.loads(text)
    except (OSError, json.JSONDecodeError):
        return None
    products = data.get("products", [])
    for prod in products:
        if not isinstance(prod, dict):
            continue
        if prod.get("locale") != locale:
            continue
        if prod.get("tts_provider") != tts_provider:
            continue
        if prod.get("skip") is True:
            continue
        voice = prod.get("voice")
        if isinstance(voice, str) and voice and voice.strip():
            return voice.strip()
    return None


# ---------------------------------------------------------------------------
# Global providers.yaml loader (Tier 2)
# ---------------------------------------------------------------------------


def _parse_providers_yaml_simple(text):
    """Tiny YAML subset reader for `providers.yaml` (no PyYAML dep).

    Parses only:
      - `tts:` block with 2-space indent: locale -> provider/voice/grade
    Other sections (render, reels_targets) are ignored here -- we only
    need the per-locale voice.
    """
    out = {}
    in_tts = False
    current_locale = None
    for raw_line in text.splitlines():
        line = raw_line.rstrip()
        stripped = line.strip()
        if not stripped or stripped.startswith("#"):
            continue
        # Top-level key detection
        if not line.startswith(" ") and stripped.endswith(":"):
            key = stripped[:-1]
            in_tts = (key == "tts")
            current_locale = None
            continue
        if not in_tts:
            continue
        # 2-space locale block opener (e.g. "  en:")
        if line.startswith("  ") and not line.startswith("    ") and stripped.endswith(":"):
            current_locale = stripped[:-1]
            out[current_locale] = {}
            continue
        # 4-space key: value
        if line.startswith("    ") and current_locale is not None and ":" in stripped:
            k, _, v = stripped.partition(":")
            out[current_locale][k.strip()] = v.strip()
    return out


def _load_global_voice(locale, tts_provider):
    """Return voice from providers.yaml or None.

    Tier 2: a global default that the per-book manifest may override.
    The provider check is loose (case-insensitive contains) so a
    providers.yaml ``provider: kokoro`` matches a ``tts_provider``
    passed as ``Kokoro`` or ``kokoro-82m``.
    """
    if not PROVIDERS_YAML_PATH.exists():
        return None
    try:
        text = PROVIDERS_YAML_PATH.read_text(encoding="utf-8")
        tts_map = _parse_providers_yaml_simple(text)
    except OSError:
        return None
    entry = tts_map.get(locale)
    if not entry:
        return None
    if tts_provider and entry.get("provider"):
        if tts_provider.lower() not in entry["provider"].lower():
            return None
    voice = entry.get("voice")
    if isinstance(voice, str) and voice and voice.strip():
        return voice.strip()
    return None


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------


def resolve_voice(book_slug, locale, tts_provider):
    """Return the voice id for ``(book_slug, locale, tts_provider)``.

    Three-tier resolution: per-book manifest > providers.yaml >
    built-in default. Raises ``VoiceResolutionError`` only when every
    tier is exhausted (locale/provider pair has no built-in default
    AND no override file).
    """
    # Tier 1: per-book manifest
    if book_slug:
        v = _load_per_book_voice(book_slug, locale, tts_provider)
        if v:
            return v
    # Tier 2: global providers.yaml
    v = _load_global_voice(locale, tts_provider)
    if v:
        return v
    # Tier 3: built-in default
    key = (tts_provider, locale)
    if key in DEFAULT_VOICE_BY_PROVIDER_LOCALE:
        return DEFAULT_VOICE_BY_PROVIDER_LOCALE[key]
    raise VoiceResolutionError(
        "no voice for provider=%r locale=%r (built-in defaults: %s)"
        % (tts_provider, locale, sorted(DEFAULT_VOICE_BY_PROVIDER_LOCALE.keys()))
    )


def list_voices(tts_provider, locale=None):
    """Return the built-in voice list for a provider (optionally filtered).

    Each entry: ``{id, locale, gender, grade}``. When ``locale`` is None
    the list covers every locale the registry knows about for that
    provider; when set, only that locale's voices are returned.
    """
    provider_map = VOICE_REGISTRY.get(tts_provider, {})
    if locale is None:
        out = []
        for loc_voices in provider_map.values():
            out.extend(loc_voices)
        return out
    return list(provider_map.get(locale, []))


# ---------------------------------------------------------------------------
# Self-test (run with: py -3 voices.py)
# ---------------------------------------------------------------------------


def _selftest():
    """Print the canonical smoke resolutions. Exits 0 on success."""
    out_en = resolve_voice("test-slug", "en", "kokoro")
    print("voices.py: resolve_voice('test-slug', 'en', 'kokoro') -> %s" % out_en)
    out_ar = resolve_voice("test-slug", "ar", "edge-tts")
    print("voices.py: resolve_voice('test-slug', 'ar', 'edge-tts') -> %s" % out_ar)
    kokoro_count = len(list_voices("kokoro", "en"))
    edge_ar_count = len(list_voices("edge-tts", "ar"))
    print("voices.py: list_voices('kokoro', 'en') -> %d voices" % kokoro_count)
    print("voices.py: list_voices('edge-tts', 'ar') -> %d voices" % edge_ar_count)
    assert out_en == "af_heart", "expected af_heart; got %r" % out_en
    assert out_ar == "ar-SA-HamedNeural", (
        "expected ar-SA-HamedNeural; got %r" % out_ar
    )


if __name__ == "__main__":
    try:
        _selftest()
    except (AssertionError, VoiceResolutionError) as exc:
        print("voices.py: SELFTEST FAIL: %s" % exc, file=sys.stderr)
        sys.exit(2)
    sys.exit(0)
