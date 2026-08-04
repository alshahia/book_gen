#!/usr/bin/env bash
# release-zip-all.sh — build agents-manager-vX.Y.Z.zip for every local tag
# Usage: bin/release-zip-all.sh [--out <dir>]
#
# Builds ZIPs into <out> (default: ./dist/) for all tags matching 'v*'.
# Prints a summary table. Safe to re-run (overwrites). Does NOT push to GitHub
# Releases — pair with a `gh release create` loop for that.
set -euo pipefail

OUT_DIR="./dist"
while [[ $# -gt 0 ]]; do
  case "$1" in
    --out) OUT_DIR="${2:-}"; shift 2 ;;
    --out=*) OUT_DIR="${1#--out=}"; shift ;;
    -h|--help)
      echo "Usage: $0 [--out <dir>]"
      echo ""
      echo "  --out <dir>   output directory (default: ./dist/)"
      exit 0
      ;;
    *) echo "ERROR: unknown arg: $1" >&2; exit 1 ;;
  esac
done

mkdir -p "$OUT_DIR"

TAGS=$(git tag -l 'v*' --sort=v:refname)
if [[ -z "$TAGS" ]]; then
  echo "ERROR: no tags matching 'v*' found locally." >&2
  exit 1
fi

echo "Building ZIPs into ${OUT_DIR}/"
echo ""

BUILT=0
FAILED=0
for tag in $TAGS; do
  if bin/release-zip.sh "$tag" --out "${OUT_DIR}/agents-manager-${tag}.zip" 2>&1 | sed 's/^/    /'; then
    BUILT=$((BUILT + 1))
  else
    echo "  FAIL ${tag}"
    FAILED=$((FAILED + 1))
  fi
done

echo ""
echo "Done. Built: ${BUILT}, Failed: ${FAILED}"
echo "Output: ${OUT_DIR}/"

if [[ $FAILED -gt 0 ]]; then
  exit 1
fi