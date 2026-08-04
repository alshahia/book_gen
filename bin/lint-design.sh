#!/usr/bin/env bash
# bin/lint-design.sh — advisory lint for am-design mockups
#
# Flags inline hex colors and emoji outside :root / [data-theme] blocks in HTML files.
# Advisory only — does NOT fail CI. Run after bin/check.sh.
#
# Usage:
#   bash bin/lint-design.sh [path]
#
# Default path: examples/
#
# Exit codes:
#   0 — no violations found
#   1 — violations found (still passes CI; informational only)
#   2 — error (path not found, etc.)

set -euo pipefail

PATH_TO_CHECK="${1:-examples/}"

if [[ ! -d "$PATH_TO_CHECK" ]]; then
  echo "ERROR: path not found: $PATH_TO_CHECK" >&2
  exit 2
fi

# Find all .html files under the path
mapfile -t HTML_FILES < <(find "$PATH_TO_CHECK" -type f -name '*.html' 2>/dev/null || true)

if [[ ${#HTML_FILES[@]} -eq 0 ]]; then
  echo "No HTML files found under $PATH_TO_CHECK"
  exit 0
fi

VIOLATIONS=0

echo "Linting ${#HTML_FILES[@]} HTML files under $PATH_TO_CHECK ..."
echo

# Check 1: inline hex outside :root or [data-theme] blocks
# This is a heuristic — it flags raw #xxxxxx in style attributes that aren't var(--*)
# Excludes common safe cases: SVG fill/stroke="none", comments, etc.
for file in "${HTML_FILES[@]}"; do
  # Find style attributes with raw hex (not via var(--))
  # Pattern: # followed by 3 or 6 hex chars, not preceded by -- or word char
  HEX_HITS=$(grep -nE '#[0-9a-fA-F]{3,6}' "$file" 2>/dev/null \
    | grep -vE 'var\(--' \
    | grep -vE 'fill="none"|stroke="none"' \
    | grep -vE '<!--' \
    | grep -vE 'fill="currentColor"|stroke="currentColor"' \
    || true)

  # Also exclude lines that are inside a :root or [data-theme] block
  # (heuristic: if the surrounding context has --var declaration nearby)
  if [[ -n "$HEX_HITS" ]]; then
    while IFS= read -r hit; do
      line_num=$(echo "$hit" | cut -d: -f1)
      # Check 5 lines before — if any contain ":root" or "[data-theme", skip
      context=$(sed -n "$((line_num > 5 ? line_num - 5 : 1)),$((line_num - 1))p" "$file" 2>/dev/null || true)
      if echo "$context" | grep -qE ':root|\[data-theme'; then
        continue
      fi
      echo "  [HEX] $file:$line_num — inline hex outside token system"
      echo "         $hit"
      VIOLATIONS=$((VIOLATIONS + 1))
    done <<< "$HEX_HITS"
  fi
done

# Check 2: emoji in UI markup (decorative)
# Common emoji ranges; skip if inside text content (e.g., Arabic Quran text with ﷽)
EMOJI_PATTERN=$'\xF0\x9F[\x8C-\x9F][\x80-\xBF]|\xE2[\x98-\x9C][\x80-\xBF]'
for file in "${HTML_FILES[@]}"; do
  EMOJI_HITS=$(grep -nP "$EMOJI_PATTERN" "$file" 2>/dev/null \
    | grep -vE '<!--' \
    || true)
  if [[ -n "$EMOJI_HITS" ]]; then
    while IFS= read -r hit; do
      line_num=$(echo "$hit" | cut -d: -f1)
      # Skip if inside Arabic Quran content area (.ar-q class)
      context=$(sed -n "$line_num p" "$file" 2>/dev/null || true)
      if echo "$context" | grep -qE 'class="ar-q"|class="[^"]*ar-q'; then
        continue
      fi
      echo "  [EMOJI] $file:$line_num — emoji in UI (use SVG instead)"
      echo "           $hit"
      VIOLATIONS=$((VIOLATIONS + 1))
    done <<< "$EMOJI_HITS"
  fi
done

echo
if [[ $VIOLATIONS -eq 0 ]]; then
  echo "OK: ${#HTML_FILES[@]} HTML files passed lint."
  exit 0
else
  echo "FOUND: $VIOLATIONS violation(s) in ${#HTML_FILES[@]} files."
  echo "(Advisory only — does not fail CI. Review and decide per case.)"
  exit 1
fi