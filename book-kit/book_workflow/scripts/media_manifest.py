"""media_manifest.py -- book2media media-locale-manifest validator + generator.

Validates `books/<slug>/media-locale-manifest.json` against the embedded
schema and scaffolds a stub manifest from a book's `chapters/` directory
plus `providers.yaml` defaults.

CLI:
    py -3 -m book_workflow.scripts.media_manifest validate <manifest-path>
    py -3 -m book_workflow.scripts.media_manifest generate --book <slug-dir>
        [--providers <providers.yaml>]
        [--out <manifest-path>]
        [--source-locale <en|ar>]

EXIT CODES
    validate
      0  schema-valid (printed as one PASS line)
      2  schema error (per-field path printed to stderr)
      3  missing dependency (jsonschema absent; install hint)
      4  input error (missing file, bad path)
    generate
      0  manifest written (idempotent on re-run)
      2  input error (book slug missing, chapters absent, path escapes root)
      3  missing dependency (jsonschema absent; install hint)
      4  providers.yaml malformed

PATH VALIDATION (P4 #14 / P6 inheritance)
    Every `--book`, `--out`, `--providers`, and positional `manifest-path`
    is resolved against the repo root (the parent of `book-kit/`) and
    rejected with a clear error if the path contains `..` or escapes the
    root. The script never writes outside the configured root.

IDEMPOTENT
    Re-running `generate` with the same inputs produces a byte-identical
    manifest: keys are sorted, trailing newline is single-LF, fields are
    emitted in a stable order. `validate` is read-only so trivially
    idempotent.

JSON SCHEMA
    The schema is embedded as a Python dict below (`SCHEMA`). It is
    deliberately the same shape the orchestrator documents in
    `agents_manager/book2media-orchestrator/SKILL.md` so the two stay in
    sync. The script does NOT import from an external `.json` file
    because the controller's chub-gate rule says "embed or it drifts".

JS-DEPENDENCY
    `jsonschema` (BSD, installed in `E:\book_gen\.venv` at v4.26.0) is
    used when present. When missing, the script degrades to a pure-stdlib
    schema check that covers the canonical required-field + type
    assertions. The fallback is documented in the project TRAC register
    as a known-degraded path; the script exits 3 with an install hint
    when the user opts out of the fallback.
"""
from __future__ import annotations

import argparse
import io
import json
import os
import re
import sys
from pathlib import Path

# ---------------------------------------------------------------------------
# UTF-8 stdio force (P4 #15 / P5 #22 inheritance)
# ---------------------------------------------------------------------------

def _force_utf8_stdio():
    """Reconfigure stdout/stderr to UTF-8 on Windows consoles.

    Must run BEFORE argparse, so help + error text never crash on
    cp1256 / cp1252 hosts.
    """
    for stream in (sys.stdout, sys.stderr):
        try:
            stream.reconfigure(encoding="utf-8")
        except (AttributeError, OSError, io.UnsupportedOperation):
            pass


_force_utf8_stdio()

# ---------------------------------------------------------------------------
# jsonschema optional import (degrades to stdlib when absent)
# ---------------------------------------------------------------------------

try:
    import jsonschema  # type: ignore
    _HAS_JSONSCHEMA = True
except ImportError:
    jsonschema = None  # type: ignore
    _HAS_JSONSCHEMA = False


# ---------------------------------------------------------------------------
# JSON Schema (embedded, intentionally not imported from .json)
# ---------------------------------------------------------------------------

SCHEMA = {
    "type": "object",
    "required": ["source_locale", "target_locales", "products"],
    "properties": {
        "source_locale": {"type": "string", "minLength": 1},
        "target_locales": {
            "type": "array",
            "minItems": 1,
            "items": {"type": "string", "minLength": 1},
        },
        "products": {
            "type": "array",
            "minItems": 1,
            "items": {
                "type": "object",
                "required": [
                    "id",
                    "locale",
                    "format",
                    "tts_provider",
                    "voice",
                    "skip",
                ],
                "properties": {
                    "id": {"type": "string", "pattern": "^[a-z0-9][a-z0-9-]*$"},
                    "locale": {"type": "string", "minLength": 1},
                    "format": {"type": "string", "minLength": 1},
                    "tts_provider": {"type": "string", "minLength": 1},
                    "voice": {"type": "string"},
                    "skip": {"type": "boolean"},
                    "translation_required": {"type": "boolean"},
                    "retention": {
                        "type": "object",
                        "properties": {
                            "keep_until": {"type": "string"},
                            "auto_delete": {"type": "boolean"},
                        },
                        "additionalProperties": False,
                    },
                    "cover_image": {"type": "string"},
                },
                "additionalProperties": False,
            },
        },
    },
    "additionalProperties": False,
}

# Built-in defaults (resolution order: per-book > global > built-in).
# See agents_manager/book2media-orchestrator/providers.yaml for the
# canonical global yaml; the values here are the LAST-resort fallback.
BUILTIN_PROVIDERS = {
    "tts": {
        "en": {"provider": "kokoro", "voice": "af_heart", "grade": "A"},
        "ar": {"provider": "edge-tts", "voice": "ar-SA-HamedNeural", "grade": "native"},
    }
}

# Per-locale voice defaults (resolved at generate time).
BUILTIN_VOICES = {
    "en": "af_heart",
    "ar": "ar-SA-HamedNeural",
}

# Per-locale TTS provider defaults (resolved at generate time).
BUILTIN_PROVIDER_NAME = {
    "en": "kokoro",
    "ar": "edge-tts",
}

# Locked product matrix from T-2026-08-10-001 plan § Phase 1 architecture.
# id-prefix -> (format, file_suffix). The runtime appends `_<locale>` to the
# id and `<locale>` to the file suffix.
PRODUCT_TYPES = [
    ("audiobook", "audio/m4b", "m4b"),
    ("video-horizontal-m1", "video/mp4", "mp4"),
    ("video-vertical-trailer", "video/mp4", "mp4"),
    ("video-vertical-reel", "video/mp4", "mp4"),
]

# Cover-image fallback ladder (T-2026-08-10-001 plan + design review F4):
# 1. Flux-generated (Mode 2 era; future)
# 2. User-supplied at books/<slug>/assets/cover.png
# 3. Auto-pick from books/<slug>/chapters-rendered/ (first PNG)
# 4. Empty string (assembler will fail loudly)
COVER_IMAGE_FALLBACK_ORDER = [
    "books/<slug>/assets/cover.png",
    "books/<slug>/chapters-rendered/cover.png",
]

REPO_ROOT = Path(__file__).resolve().parents[3]
CHAPTER_GLOB = "ch-*.md"


# ---------------------------------------------------------------------------
# Errors
# ---------------------------------------------------------------------------

class MediaManifestError(Exception):
    """Raised for input errors that should exit 2 with a one-line hint."""


class MissingDependencyError(Exception):
    """Raised when an optional dep is missing and the user opted out of fallback."""


# ---------------------------------------------------------------------------
# Path validation
# ---------------------------------------------------------------------------

def _resolve_under(root, candidate, label):
    """Resolve `candidate` under `root`, refusing escapes.

    Rejects any path containing a `..` component and any absolute path
    that does not live under `root`. Returns the resolved `Path`.
    """
    raw = Path(candidate)
    if ".." in raw.parts:
        raise MediaManifestError(
            "%s must not contain '..': %s" % (label, candidate)
        )
    if raw.is_absolute():
        target = raw.resolve()
    else:
        target = (root / raw).resolve()
    root = root.resolve()
    if target != root and root not in target.parents:
        raise MediaManifestError(
            "%s must resolve under %s: %s" % (label, root, candidate)
        )
    return target


def _resolve_repo_path(candidate, label):
    """Resolve a path against the repo root with the same strict rules."""
    return _resolve_under(REPO_ROOT, candidate, label)


# ---------------------------------------------------------------------------
# Pure-stdlib schema fallback (no jsonschema)
# ---------------------------------------------------------------------------

def _validate_required(data, required_keys, path):
    """Walk the required-keys list and yield (path, message) errors."""
    for key in required_keys:
        if key not in data:
            yield ("%s.%s" % (path, key), "missing required field")


def _validate_type(value, expected_type, path):
    """Yield a type-mismatch error when `value` does not match `expected_type`.

    `expected_type` is one of `string`, `integer`, `number`, `boolean`,
    `array`, `object`.
    """
    py = {
        "string": str,
        "integer": int,
        "number": (int, float),
        "boolean": bool,
        "array": list,
        "object": dict,
    }.get(expected_type)
    if py is None:
        return  # unknown type -> skip
    # bool is a subclass of int in Python; guard against integer-accepting bools.
    if expected_type == "integer" and isinstance(value, bool):
        yield (path, "expected integer, got boolean")
    elif expected_type == "string" and not isinstance(value, str):
        yield (path, "expected string, got %s" % type(value).__name__)
    elif not isinstance(value, py):
        yield (path, "expected %s, got %s" % (expected_type, type(value).__name__))


def _validate_schema_stdlib(data):
    """Pure-stdlib validator. Returns a list of (path, message) errors.

    Covers the same `required` + `type` constraints as the embedded jsonschema
    schema. Pattern + minLength + items are NOT enforced in the fallback; the
    fallback is documented as degraded in the module docstring.
    """
    errors = []
    for path, msg in _validate_required(data, SCHEMA["required"], ""):
        errors.append((path, msg))
    if not errors:
        # Nested: products
        products = data.get("products", [])
        if not isinstance(products, list):
            errors.append(("products", "expected array, got %s" % type(products).__name__))
        else:
            for i, prod in enumerate(products):
                base = "products[%d]" % i
                if not isinstance(prod, dict):
                    errors.append((base, "expected object, got %s" % type(prod).__name__))
                    continue
                for path, msg in _validate_required(
                    prod, SCHEMA["properties"]["products"]["items"]["required"], base
                ):
                    errors.append((path, msg))
                # Type checks for the canonical fields
                for fname, ftype in (
                    ("id", "string"),
                    ("locale", "string"),
                    ("format", "string"),
                    ("tts_provider", "string"),
                    ("skip", "boolean"),
                ):
                    if fname in prod:
                        for path, msg in _validate_type(prod[fname], ftype, "%s.%s" % (base, fname)):
                            errors.append((path, msg))
    return errors


def _format_errors(errors):
    """Render a list of (path, message) errors as one-line readable strings."""
    return ["%s: %s" % (path, msg) for path, msg in errors]


# ---------------------------------------------------------------------------
# jsonschema adapter (when available)
# ---------------------------------------------------------------------------

def _validate_schema_jsonschema(data):
    """Run the embedded schema via jsonschema. Returns a list of (path, msg)."""
    validator = jsonschema.Draft7Validator(SCHEMA)
    errors = []
    for err in sorted(validator.iter_errors(data), key=lambda e: list(e.absolute_path)):
        # Minimal-path variant: "/products/0/id" -> "products[0].id"
        path_parts = []
        for token in err.absolute_path:
            if isinstance(token, int):
                if path_parts:
                    path_parts[-1] = path_parts[-1] + "[%d]" % token
                else:
                    path_parts.append("[%d]" % token)
            else:
                path_parts.append(str(token))
        path = ".".join(path_parts) if path_parts else "(root)"
        errors.append((path, err.message))
    return errors


# ---------------------------------------------------------------------------
# validate subcommand
# ---------------------------------------------------------------------------

def run_validate(manifest_path_arg, allow_fallback, strict):
    """Validate a manifest file. Returns the exit code."""
    try:
        manifest_path = _resolve_repo_path(manifest_path_arg, "manifest-path")
    except MediaManifestError as exc:
        print("media_manifest: %s" % exc, file=sys.stderr)
        return 2

    if not manifest_path.exists():
        print("media_manifest: manifest not found: %s" % manifest_path, file=sys.stderr)
        return 2

    # Read manifest as UTF-8 (with cp1256 fallback for legacy Arabic books).
    try:
        text = manifest_path.read_text(encoding="utf-8")
    except UnicodeDecodeError:
        try:
            text = manifest_path.read_text(encoding="cp1256")
        except UnicodeDecodeError:
            print(
                "media_manifest: cannot decode %s as UTF-8 or cp1256"
                % manifest_path,
                file=sys.stderr,
            )
            return 2

    try:
        data = json.loads(text)
    except json.JSONDecodeError as exc:
        print(
            "media_manifest: invalid JSON in %s: %s" % (manifest_path, exc),
            file=sys.stderr,
        )
        return 2

    if _HAS_JSONSCHEMA:
        errors = _validate_schema_jsonschema(data)
    else:
        if strict:
            print(
                "media_manifest: jsonschema is not installed; cannot run strict "
                "validation. Install with `pip install jsonschema`.",
                file=sys.stderr,
            )
            return 3
        if not allow_fallback:
            print(
                "media_manifest: jsonschema is not installed; pass --allow-stdlib-fallback "
                "to run the degraded validator, or install jsonschema.",
                file=sys.stderr,
            )
            return 3
        errors = _validate_schema_stdlib(data)

    if errors:
        print("media_manifest: FAIL: %d schema error(s) in %s" % (len(errors), manifest_path),
              file=sys.stderr)
        for line in _format_errors(errors):
            print("  %s" % line, file=sys.stderr)
        return 2

    print("media_manifest: PASS: %s" % manifest_path)
    return 0


# ---------------------------------------------------------------------------
# YAML provider loader (stdlib only -- no PyYAML)
# ---------------------------------------------------------------------------

def _parse_simple_yaml(text):
    """Parse the providers.yaml shape used by book2media.

    We support only the subset required by this script:
      - 2-space indented mappings
      - top-level keys: `version`, `tts`, `render`, `reels_targets`
      - list of mappings under `reels_targets` (each `- key: value` block)
      - inline flow-style `{top: 250, bottom: 250, left: 0, right: 0}` for the
        `caption_safe_zone` mapping (no quoting, all values scalars).

    The file is hand-written by the orchestrator owner; we read it line by
    line and accept the documented shape. Anything fancier is a v2 concern.
    """
    out = {"version": None, "tts": {}, "render": {}, "reels_targets": []}
    lines = text.splitlines()
    i = 0
    section = None
    section_indent = 0
    while i < len(lines):
        line = lines[i]
        stripped = line.strip()
        if not stripped or stripped.startswith("#"):
            i += 1
            continue
        indent = len(line) - len(line.lstrip())
        if indent == 0:
            if ":" not in stripped:
                raise MediaManifestError(
                    "providers.yaml: expected `key: value` at line %d: %r" % (i + 1, line)
                )
            k, _, v = stripped.partition(":")
            k = k.strip()
            v = v.strip()
            if k == "version":
                try:
                    out["version"] = int(v)
                except ValueError:
                    out["version"] = v
                section = None
            elif k in ("tts", "render"):
                section = k
                section_indent = 0
                if v:
                    # single-line value (rare for these sections)
                    raise MediaManifestError(
                        "providers.yaml: section %r expects a block, not a scalar (line %d)"
                        % (k, i + 1)
                    )
            elif k == "reels_targets":
                section = "reels_targets"
                section_indent = 0
            else:
                # Unknown top-level key -- ignore (forward compat).
                section = None
            i += 1
            continue
        # Indented: depends on section
        if section == "tts":
            # 2 spaces: locale; 4 spaces: provider/voice/grade
            if indent == 2 and stripped.endswith(":"):
                locale = stripped[:-1].strip()
                out["tts"][locale] = {}
                current_locale = locale
                i += 1
                continue
            if indent == 4 and ":" in stripped:
                k, _, v = stripped.partition(":")
                out["tts"][current_locale][k.strip()] = v.strip()
                i += 1
                continue
            raise MediaManifestError(
                "providers.yaml: unexpected indent in tts section at line %d: %r"
                % (i + 1, line)
            )
        if section == "render":
            if indent == 2 and ":" in stripped:
                k, _, v = stripped.partition(":")
                out["render"][k.strip()] = v.strip()
                i += 1
                continue
            raise MediaManifestError(
                "providers.yaml: unexpected indent in render section at line %d: %r"
                % (i + 1, line)
            )
        if section == "reels_targets":
            if indent == 2 and stripped.startswith("- "):
                # List entry: parse inline `key: value` pairs.
                item = {}
                rest = stripped[2:].strip()
                if ":" in rest:
                    k, _, v = rest.partition(":")
                    item[k.strip()] = v.strip()
                # Look ahead for the indented nested mapping.
                j = i + 1
                while j < len(lines):
                    l2 = lines[j]
                    s2 = l2.strip()
                    if not s2 or s2.startswith("#"):
                        j += 1
                        continue
                    ind2 = len(l2) - len(l2.lstrip())
                    if ind2 <= 2:
                        break
                    if ":" in s2:
                        k, _, v = s2.partition(":")
                        k = k.strip()
                        v = v.strip()
                        if v.startswith("{") and v.endswith("}"):
                            # Inline flow-style mapping.
                            inner = v[1:-1].strip()
                            sub = {}
                            for pair in inner.split(","):
                                if ":" not in pair:
                                    continue
                                pk, _, pv = pair.partition(":")
                                sub[pk.strip()] = _coerce(pv.strip())
                            item[k] = sub
                        else:
                            item[k] = _coerce(v)
                    j += 1
                out["reels_targets"].append(item)
                i = j
                continue
            raise MediaManifestError(
                "providers.yaml: unexpected indent in reels_targets at line %d: %r"
                % (i + 1, line)
            )
        # Unknown section content -- skip.
        i += 1
    return out


def _coerce(v):
    """Parse a scalar string into int / float / bool / str."""
    if v == "":
        return ""
    if v.lower() in ("true", "yes"):
        return True
    if v.lower() in ("false", "no"):
        return False
    try:
        return int(v)
    except ValueError:
        pass
    try:
        return float(v)
    except ValueError:
        pass
    return v


# ---------------------------------------------------------------------------
# generate subcommand
# ---------------------------------------------------------------------------

def _discover_chapters(book_dir):
    """Return a sorted list of chapter IDs (e.g. ['ch-01', 'ch-02'])."""
    chapters_dir = book_dir / "chapters"
    if not chapters_dir.is_dir():
        return []
    ids = []
    for entry in sorted(chapters_dir.iterdir()):
        if entry.is_file():
            m = re.match(r"^(ch-(\d+))\.md$", entry.name)
            if m:
                ids.append(m.group(1))
    return ids


def _voice_for(locale, providers):
    """Resolve the voice for a locale using the 3-tier rule."""
    tts = providers.get("tts", {}) if providers else {}
    entry = tts.get(locale)
    if entry and entry.get("voice"):
        return entry["voice"]
    if locale in BUILTIN_VOICES:
        return BUILTIN_VOICES[locale]
    raise MediaManifestError(
        "providers.yaml: no TTS entry for locale %r; add a block or pass --source-locale" % locale
    )


def _provider_for(locale, providers):
    """Resolve the TTS provider name for a locale."""
    tts = providers.get("tts", {}) if providers else {}
    entry = tts.get(locale)
    if entry and entry.get("provider"):
        return entry["provider"]
    if locale in BUILTIN_PROVIDER_NAME:
        return BUILTIN_PROVIDER_NAME[locale]
    return "unknown"


def _translation_required(locale, source_locale):
    """Whether the target locale needs translation, NOT just TTS."""
    return locale != source_locale


def _retention_field():
    """Per-design-review F3: include a retention policy object."""
    return {"keep_until": "shipped", "auto_delete": True}


def _cover_image_field(book_dir):
    """Per-design-review F4: cover-image fallback ladder.

    Returns the first-resolved path from the ladder, or an empty string
    when nothing resolves. The assembler will fail loudly if the path
    is empty at use time -- documented in plan § Phase 1.
    """
    for relpath in COVER_IMAGE_FALLBACK_ORDER:
        # First replace `<slug>` with the actual book directory name.
        rel = relpath.replace("<slug>", book_dir.name)
        candidate = (book_dir / rel).resolve()
        if candidate.exists():
            return rel
    return ""


def _build_products(book_dir, source_locale, target_locales, providers):
    """Build the canonical 5-product matrix per locale."""
    products = []
    cover_image = _cover_image_field(book_dir)
    retention = _retention_field()
    for locale in target_locales:
        voice = _voice_for(locale, providers)
        provider = _provider_for(locale, providers)
        translation_required = _translation_required(locale, source_locale)
        for type_id, fmt, _suffix in PRODUCT_TYPES:
            product = {
                "id": "%s-%s" % (type_id, locale),
                "locale": locale,
                "format": fmt,
                "tts_provider": provider,
                "voice": voice,
                "skip": False,
            }
            if translation_required:
                product["translation_required"] = True
            product["retention"] = retention
            if cover_image:
                product["cover_image"] = cover_image
            products.append(product)
    return products


def _stable_dump(data):
    """Serialize to a canonical JSON string with sorted keys + stable indent."""
    return json.dumps(data, indent=2, sort_keys=True, ensure_ascii=False) + "\n"


def _load_providers(providers_path):
    """Load and validate providers.yaml. Returns the parsed dict (or None)."""
    if providers_path is None:
        return None
    try:
        providers_path = _resolve_repo_path(providers_path, "--providers")
    except MediaManifestError as exc:
        print("media_manifest: %s" % exc, file=sys.stderr)
        raise SystemExit(2)
    if not providers_path.exists():
        print(
            "media_manifest: providers.yaml not found: %s" % providers_path,
            file=sys.stderr,
        )
        raise SystemExit(4)
    try:
        text = providers_path.read_text(encoding="utf-8")
        return _parse_simple_yaml(text)
    except (MediaManifestError, OSError) as exc:
        print("media_manifest: providers.yaml malformed: %s" % exc, file=sys.stderr)
        raise SystemExit(4)


def run_generate(book_arg, providers_arg, out_arg, source_locale):
    """Generate a stub manifest. Returns the exit code."""
    try:
        book_dir = _resolve_repo_path(book_arg, "--book")
    except MediaManifestError as exc:
        print("media_manifest: %s" % exc, file=sys.stderr)
        return 2
    if not book_dir.is_dir():
        print("media_manifest: --book not found: %s" % book_dir, file=sys.stderr)
        return 2
    chapters_dir = book_dir / "chapters"
    if not chapters_dir.is_dir():
        print(
            "media_manifest: --book has no chapters/ directory: %s" % book_dir,
            file=sys.stderr,
        )
        return 2

    providers = _load_providers(providers_arg)

    source_locale = source_locale or "en"
    # Per locked decision: target_locales = source + ar at minimum.
    target_locales = [source_locale]
    if "ar" not in target_locales:
        target_locales.append("ar")

    products = _build_products(book_dir, source_locale, target_locales, providers)

    manifest = {
        "source_locale": source_locale,
        "target_locales": target_locales,
        "products": products,
    }

    # Output path: --out or <book>/media-locale-manifest.json
    if out_arg:
        try:
            out_path = _resolve_repo_path(out_arg, "--out")
        except MediaManifestError as exc:
            print("media_manifest: %s" % exc, file=sys.stderr)
            return 2
    else:
        out_path = (book_dir / "media-locale-manifest.json").resolve()

    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(_stable_dump(manifest), encoding="utf-8")
    print(
        "media_manifest: wrote %d product(s) for %s -> %s"
        % (len(products), book_dir, out_path)
    )
    return 0


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def _build_parser():
    p = argparse.ArgumentParser(
        prog="media_manifest",
        description="Validate and generate books/<slug>/media-locale-manifest.json.",
    )
    sub = p.add_subparsers(dest="command", required=True)

    p_validate = sub.add_parser(
        "validate",
        help="Validate a media-locale-manifest.json against the embedded schema.",
    )
    p_validate.add_argument(
        "manifest_path",
        help="Path to a media-locale-manifest.json file (repo-root-relative).",
    )
    p_validate.add_argument(
        "--allow-stdlib-fallback",
        action="store_true",
        help="Run the degraded stdlib validator when jsonschema is missing.",
    )
    p_validate.add_argument(
        "--strict",
        action="store_true",
        help="Refuse to run when jsonschema is missing (default: warn and exit 3).",
    )

    p_generate = sub.add_parser(
        "generate",
        help="Scaffold a stub manifest from a book's chapters/ + providers.yaml.",
    )
    p_generate.add_argument(
        "--book", required=True,
        help="Book root (books/<slug>/).",
    )
    p_generate.add_argument(
        "--providers",
        help="Path to providers.yaml (repo-root-relative). "
             "Defaults to agents_manager/book2media-orchestrator/providers.yaml.",
    )
    p_generate.add_argument(
        "--out",
        help="Output manifest path (default: <book>/media-locale-manifest.json).",
    )
    p_generate.add_argument(
        "--source-locale",
        help="Source locale of the book (default: en).",
    )

    return p


def main(argv=None):
    parser = _build_parser()
    args = parser.parse_args(argv)

    if args.command == "validate":
        return run_validate(
            args.manifest_path,
            allow_fallback=args.allow_stdlib_fallback,
            strict=args.strict,
        )
    if args.command == "generate":
        return run_generate(
            args.book,
            args.providers,
            args.out,
            args.source_locale,
        )
    parser.error("unknown command: %s" % args.command)
    return 2


if __name__ == "__main__":
    sys.exit(main())
