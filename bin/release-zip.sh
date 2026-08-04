#!/usr/bin/env bash
# release-zip.sh — build agents-manager-vX.Y.Z.zip from a git tag's tree
# Usage: bin/release-zip.sh <tag> [--out <path>]
#   tag:  e.g. v0.9.1 (leading 'v' optional)
#   --out <path>:  output path (default: ./agents-manager-<version>.zip in cwd)
#
# Includes only the 7 controller paths (NOT bin/ — bin/ stays in the source repo
# for the maintainer; users download ZIPs and run install.sh from inside them).
# Validates that each expected path was actually included before declaring success.
set -euo pipefail

# NOTE: This script is invoked directly (must have +x) OR via `bash release-zip.sh`
# from agents-manager. The dispatcher uses the `bash explicit` form so the +x bit
# is not required.

if [[ $# -lt 1 ]] || [[ "$1" == "--help" ]] || [[ "$1" == "-h" ]]; then
  echo "Usage: $0 <tag> [--out <path>]"
  echo ""
  echo "  tag          git tag to archive (e.g. v0.9.1, leading v optional)"
  echo "  --out <path> output zip path (default: ./agents-manager-v<X.Y.Z>.zip)"
  exit 0
fi

RAW_TAG="$1"
shift

OUT_PATH=""
while [[ $# -gt 0 ]]; do
  case "$1" in
    --out) OUT_PATH="${2:-}"; shift 2 ;;
    --out=*) OUT_PATH="${1#--out=}"; shift ;;
    *) echo "ERROR: unknown arg: $1" >&2; exit 1 ;;
  esac
done

# Normalize tag
TAG="${RAW_TAG}"
[[ "$TAG" != v* ]] && TAG="v${TAG}"
VERSION="${TAG#v}"

# Validate tag exists locally
if ! git rev-parse --verify --quiet "refs/tags/${TAG}" >/dev/null; then
  echo "ERROR: tag '${TAG}' does not exist locally." >&2
  echo "       Available tags: $(git tag -l | tr '\n' ' ')" >&2
  exit 1
fi

if [[ -z "$OUT_PATH" ]]; then
  OUT_PATH="agents-manager-v${VERSION}.zip"
fi

# Resolve to absolute path.
# Accept POSIX absolute (starts with /), Windows-style (X:/... or X:\...),
# or fall back to CWD-relative.
case "$OUT_PATH" in
  /*|[A-Za-z]:[\\/]*) ;;   # already absolute
  *)  OUT_PATH="${PWD}/${OUT_PATH}" ;;
esac

# Path allowlist — what goes into the release ZIP.
#
# Includes the 6 controller paths (what install.sh copies INTO the target
# project) PLUS the bin/ directory (so Option B / "download a ZIP" users can
# actually RUN the installer from the extracted folder).
PATHS=(
  "opencode.jsonc"
  "CLAUDE.md"
  "agents_manager"
  "share"
  "tasks"
  ".agents/skills/mavis-team"
  "bin"
)

echo "Building ${OUT_PATH} from tag ${TAG}..."

# git archive writes to stdout in zip format; redirect to OUT_PATH.
# --prefix=agents-manager/ creates the top-level directory in the zip.
git archive \
  --format=zip \
  --prefix="agents-manager/" \
  --output="${OUT_PATH}.tmp" \
  "${TAG}" \
  "${PATHS[@]}"

# Validate the resulting zip contains all expected top-level entries.
# `unzip -Z1` lists one entry per line. We check that each expected path
# appears either as a directory entry (with trailing /) or as a file
# inside a directory of the same name.
EXPECTED_PREFIX="agents-manager/"
if ! command -v unzip >/dev/null 2>&1; then
  echo "WARN: unzip not on PATH — skipping ZIP content validation."
  echo "      Install unzip (apt: unzip, brew: unzip, choco: unzip) to enable verification."
else
  LISTING=$(unzip -Z1 "${OUT_PATH}.tmp")
  MISSING=()
  for p in "${PATHS[@]}"; do
    # Allow the dir entry itself (with trailing /) or any file inside it.
    if ! printf '%s\n' "$LISTING" | grep -qE "^${EXPECTED_PREFIX}${p}(/|\$)"; then
      MISSING+=("$p")
    fi
  done
  if [[ ${#MISSING[@]} -gt 0 ]]; then
    echo "ERROR: ZIP is missing expected paths:" >&2
    printf '  - %s\n' "${MISSING[@]}" >&2
    rm -f "${OUT_PATH}.tmp"
    exit 2
  fi
  # Extra check: Option B users invoke the installer from the extracted folder,
  # so the bin/ scripts must be present. (Otherwise we'd pass the per-PATH
  # check above but Option B would still be broken.)
  for must in "bin/install.sh" "bin/install.ps1"; do
    if ! printf '%s\n' "$LISTING" | grep -qE "^${EXPECTED_PREFIX}${must}\$"; then
      MISSING+=("$must")
    fi
  done
  if [[ ${#MISSING[@]} -gt 0 ]]; then
    echo "ERROR: ZIP is missing required installer scripts (Option B would break):" >&2
    printf '  - %s\n' "${MISSING[@]}" >&2
    rm -f "${OUT_PATH}.tmp"
    exit 2
  fi
fi

mv "${OUT_PATH}.tmp" "${OUT_PATH}"

# Print summary
SIZE=$(stat -c %s "${OUT_PATH}" 2>/dev/null || stat -f %z "${OUT_PATH}" 2>/dev/null || echo "?")
ENTRIES=$(unzip -Z1 "${OUT_PATH}" 2>/dev/null | wc -l | tr -d ' ')
echo "  OK   ${OUT_PATH}"
echo "       size: ${SIZE} bytes, entries: ${ENTRIES}"
echo "       tag:  ${TAG} -> $(git rev-parse --short "${TAG}")"