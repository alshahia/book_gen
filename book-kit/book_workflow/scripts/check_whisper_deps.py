"""check_whisper_deps.py -- book2media Phase 3 P5T1: faster-whisper dep check + self-check.

Verifies that the ``faster_whisper`` and ``ctranslate2`` packages are
installed (exits 3 if not), auto-picks a model size for the requested
locale (``large-v3`` for Arabic, ``small`` for English), and (with
``--self-check``) downloads the model once into the cache and runs
inference on a 30s synthetic sample. The self-check prints a real-time
ratio ``audio_seconds / inference_seconds`` so the user knows whether
ASR will fit the Phase 5 smoke-test wall-clock budget on this hardware.

CLI:
    py -3 book-kit/book_workflow/scripts/check_whisper_deps.py \\
        --language ar --self-check

EXIT CODES
    0  success -- model resolved (or self-check completed).
    2  input error (unknown locale, bad flag, no language given).
    3  missing dependency (faster_whisper or ctranslate2 not in venv).
    4  internal/runtime (model load failed or inference raised).

PATH VALIDATION
    This script does not write to disk beyond the faster-whisper cache
    (default: ``$HF_HOME`` / ``~/.cache/huggingface``). It has no
    ``--book`` / ``--out`` flags. The cache dir is overridable via
    ``--cache-dir``; we accept any absolute path so the user can pin it
    inside the repo for offline runs.

IDEMPOTENT
    Re-running with ``--self-check`` on a warm cache skips the download
    (faster-whisper's own cache logic) and re-runs inference on the
    synthetic 30s sample.

NOT IN SCOPE
    - Auto-installing faster-whisper / ctranslate2. Per the dispatch
      preamble the venv ships without these; we surface a one-line
      ``pip install`` hint instead.
    - Benchmarking on real chapter audio -- the Phase 5 smoke run does
      that. This self-check only validates "the library loads and the
      model runs end-to-end on synthetic audio".

# chub-cite: SYSTRAN/faster-whisper
"""
from __future__ import annotations

# ---------------------------------------------------------------------------
# UTF-8 stdio force (P4 #15 / P5 #22 inheritance) -- MUST run before argparse.
# ---------------------------------------------------------------------------

import sys
import io

for _stream in (sys.stdout, sys.stderr):
    try:
        _stream.reconfigure(encoding="utf-8")
    except (AttributeError, OSError, io.UnsupportedOperation):
        pass


# ---------------------------------------------------------------------------
# Standard imports
# ---------------------------------------------------------------------------

import argparse
import importlib.util
import time
from pathlib import Path


# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

# Per-locale model auto-pick. Arabic needs large-v3 for reasonable
# diacritic + tashkeel recognition (per research F10); English gets by
# with the smaller, faster `small` model.
MODEL_FOR_LOCALE = {
    "ar": "large-v3",
    "en": "small",
}

# Self-check sample: 30 seconds of 440 Hz mono sine at 16 kHz. Generated
# in-memory by ``_synth_sample``; no fixture file required.
SELF_CHECK_DURATION_S = 30
SELF_CHECK_SAMPLE_RATE_HZ = 16000
SELF_CHECK_TONE_HZ = 440.0

# Self-check real-time ratio target. RTX 4000 (8 GB) should land well
# below 1.0x; we report the observed ratio either way. If the ratio
# exceeds 5.0x, the self-check returns exit 4 so the user can decide
# whether to switch locales or upgrade hardware before running the full
# 2,465-word `daily-focus` chapter.
SELF_CHECK_RATIO_CEILING = 5.0


# ---------------------------------------------------------------------------
# Errors
# ---------------------------------------------------------------------------


class WhisperDepsError(Exception):
    """Raised for input errors that should exit 2 with a one-line hint."""


class WhisperMissingDependency(Exception):
    """Raised when faster_whisper / ctranslate2 is not in the venv."""


class WhisperRuntimeFailure(Exception):
    """Raised when the model loads but inference fails."""


# ---------------------------------------------------------------------------
# Optional-import probe (no silent pip install).
# ---------------------------------------------------------------------------


def _check_deps():
    """Return (has_faster_whisper, has_ctranslate2). Raise if both missing."""
    has_fw = importlib.util.find_spec("faster_whisper") is not None
    has_ct = importlib.util.find_spec("ctranslate2") is not None
    if not has_fw or not has_ct:
        missing = []
        if not has_fw:
            missing.append("faster-whisper")
        if not has_ct:
            missing.append("ctranslate2")
        raise WhisperMissingDependency(
            "missing Python dep(s): %s; install with "
            "`pip install faster-whisper==1.1.1` (pulls ctranslate2 ~50 MB)"
            % ", ".join(missing)
        )
    return has_fw, has_ct


def pick_model_for_locale(locale):
    """Return the canonical Whisper model id for ``locale``."""
    model = MODEL_FOR_LOCALE.get(locale)
    if model is None:
        raise WhisperDepsError(
            "unsupported locale=%r; supported: %s"
            % (locale, sorted(MODEL_FOR_LOCALE.keys()))
        )
    return model


# ---------------------------------------------------------------------------
# Synthetic 30s sample (numpy already installed per environment note).
# ---------------------------------------------------------------------------


def _synth_sample(duration_s=SELF_CHECK_DURATION_S, sr=SELF_CHECK_SAMPLE_RATE_HZ):
    """Build a float32 mono numpy array of `duration_s` of 440 Hz tone."""
    import numpy as np  # local import: numpy ships in torch's dep tree

    t = np.linspace(0.0, duration_s, int(sr * duration_s), endpoint=False)
    tone = 0.2 * np.sin(2.0 * 3.141592653589793 * SELF_CHECK_TONE_HZ * t)
    return tone.astype("float32"), sr


# ---------------------------------------------------------------------------
# Self-check: download model (if cold cache), run inference on the sample.
# ---------------------------------------------------------------------------


def run_self_check(locale, cache_dir, device):
    """Run the 30s self-check; print ratio; return exit code."""
    model_id = pick_model_for_locale(locale)

    # Confirm deps are present before touching the model.
    try:
        _check_deps()
    except WhisperMissingDependency as exc:
        print("check_whisper_deps: %s" % exc, file=sys.stderr)
        return 3

    from faster_whisper import WhisperModel  # noqa: F401  (after dep check)

    # Default cache: repo-local .cache/faster-whisper to avoid leaking into
    # the user's HF_HOME (~/.cache/huggingface). Override with --cache-dir.
    if cache_dir:
        cache_arg = str(cache_dir)
    else:
        repo_cache = Path(__file__).resolve().parents[3] / ".cache" / "faster-whisper"
        cache_arg = str(repo_cache)
        print(
            "check_whisper_deps: --cache-dir not set; defaulting to repo-local %s"
            % cache_arg,
            file=sys.stderr,
        )
    print(
        "check_whisper_deps: loading model=%r device=%r cache=%s"
        % (model_id, device, cache_arg)
    )
    try:
        model = WhisperModel(
            model_id,
            device=device,
            compute_type="float16" if device == "cuda" else "int8",
            download_root=cache_arg,
        )
    except Exception as exc:
        print(
            "check_whisper_deps: WhisperModel init failed: %s" % exc,
            file=sys.stderr,
        )
        return 3

    sample, sr = _synth_sample()
    print(
        "check_whisper_deps: running inference on %ds sample @ %d Hz"
        % (SELF_CHECK_DURATION_S, sr)
    )
    t0 = time.perf_counter()
    try:
        segments, _info = model.transcribe(
            sample,
            language=locale,
            word_timestamps=False,
            beam_size=1,
        )
        # Force materialisation -- the generator is lazy.
        seg_count = 0
        for _ in segments:
            seg_count += 1
    except Exception as exc:
        print(
            "check_whisper_deps: inference raised: %s" % exc,
            file=sys.stderr,
        )
        return 4
    dt = time.perf_counter() - t0
    ratio = dt / SELF_CHECK_DURATION_S
    print(
        "check_whisper_deps: OK audio=%ds inference=%.2fs ratio=%.2fx "
        "(ceiling=%.2fx) segments=%d model=%r device=%r"
        % (
            SELF_CHECK_DURATION_S, dt, ratio,
            SELF_CHECK_RATIO_CEILING, seg_count, model_id, device,
        )
    )
    if ratio > SELF_CHECK_RATIO_CEILING:
        print(
            "check_whisper_deps: WARNING ratio exceeds ceiling; ASR will be "
            "slow on real chapters. Consider device=cpu or a smaller model.",
            file=sys.stderr,
        )
        return 4
    return 0


# ---------------------------------------------------------------------------
# Plain dep-check (no model download, no inference).
# ---------------------------------------------------------------------------


def run_dep_check(locale):
    """Just verify deps + resolve model id; print + return 0."""
    model_id = pick_model_for_locale(locale)
    try:
        _check_deps()
    except WhisperMissingDependency as exc:
        print("check_whisper_deps: %s" % exc, file=sys.stderr)
        return 3
    print(
        "check_whisper_deps: OK locale=%r model=%r deps=present"
        % (locale, model_id)
    )
    return 0


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------


def _build_parser():
    p = argparse.ArgumentParser(
        prog="check_whisper_deps",
        description=(
            "Verify faster-whisper deps + auto-pick a model for the locale. "
            "--self-check downloads the model + runs inference on a 30s "
            "synthetic sample and prints audio_seconds / inference_seconds."
        ),
    )
    p.add_argument(
        "--language", required=True, choices=sorted(MODEL_FOR_LOCALE.keys()),
        help="Locale code: en or ar (drives model auto-pick).",
    )
    p.add_argument(
        "--self-check", action="store_true",
        help="Download model + run inference on a 30s sample. Reports ratio.",
    )
    p.add_argument(
        "--cache-dir", default=None,
        help="Override the model download dir (default: <repo>/.cache/faster-whisper).",
    )
    p.add_argument(
        "--device", default="cuda", choices=["cuda", "cpu"],
        help="Compute device for faster-whisper (default cuda).",
    )
    return p


def main(argv=None):
    parser = _build_parser()
    args = parser.parse_args(argv)
    try:
        if args.self_check:
            return run_self_check(args.language, args.cache_dir, args.device)
        return run_dep_check(args.language)
    except WhisperDepsError as exc:
        print("check_whisper_deps: %s" % exc, file=sys.stderr)
        return 2
    except WhisperMissingDependency as exc:
        print("check_whisper_deps: %s" % exc, file=sys.stderr)
        return 3
    except WhisperRuntimeFailure as exc:
        print("check_whisper_deps: %s" % exc, file=sys.stderr)
        return 4


if __name__ == "__main__":
    sys.exit(main())
