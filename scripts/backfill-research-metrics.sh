#!/usr/bin/env bash
# backfill-research-metrics.sh
# Append a `## Metrics` block to any share/notes/01_research_*.md missing it.
# Idempotent, append-only. Stdlib only (grep -E + awk; POSIX-reasonable). <10s on <=50 files.
#
# Usage: bash scripts/backfill-research-metrics.sh
# Exit:  0 = no work done (all files already had Metrics, or nothing to scan)
#        1 = at least one file was injected
#
# Discovery: a shell glob on the known naming convention. rg is not required
# (and often absent); grep -E does the content inference below. This is the
# laziest correct file-scan — no external dep, no `find`.
#
# Inferred counts are BEST-EFFORT heuristics. Ceilings are documented per-metric
# in infer_counts(). The backfilled block is stamped as inferred, not authored.

set -euo pipefail

# infer_counts <file> -> prints: "<findings> <risks_high> <risks_med> <risks_low> <clarifying_Qs>"
infer_counts() {
  local file="$1"
  local findings risks_h risks_m risks_l q_count

  # findings: top-level `- ` bullets INSIDE the `## Technical findings` section only
  #   (0 if the section is absent). Ceiling: counts top-level bullets only; nested
  #   detail bullets (indented) are intentionally not counted. Older notes (e.g.
  #   01_research_T-2026-07-03-001) use a different section name -> 0, by design.
  findings=$(awk '
    /^## Technical findings/ { infindings=1; next }
    /^## / { infindings=0 }
    infindings && /^- / { n++ }
    END { print n+0 }
  ' "$file")

  # risks_*: count of `**Severity:** <level>` lines. Ceiling: notes that record
  #   severity in a table (not `**Severity:**` prose) infer as 0 -> a known miss.
  #   `|| true` keeps grep's exit-1-on-zero-match from tripping `set -e`.
  risks_h=$(grep -cE '\*\*Severity:\*\* high' "$file" || true)
  risks_m=$(grep -cE '\*\*Severity:\*\* medium' "$file" || true)
  risks_l=$(grep -cE '\*\*Severity:\*\* low' "$file" || true)

  # clarifying_Qs: `**Suggested clarifying question:**` lines (any indentation).
  q_count=$(grep -cE '\*\*Suggested clarifying question:\*\*' "$file" || true)

  : "${findings:=0}"; : "${risks_h:=0}"; : "${risks_m:=0}"; : "${risks_l:=0}"; : "${q_count:=0}"
  echo "$findings $risks_h $risks_m $risks_l $q_count"
}

main() {
  local touched=0 file counts f rh rm rl q eol
  for file in share/notes/01_research_*.md; do
    [ -e "$file" ] || continue          # glob matched nothing -> skip literal pattern
    if grep -qE '^## Metrics' "$file"; then
      continue                          # already has Metrics -> never touch
    fi

    counts=$(infer_counts "$file")
    read -r f rh rm rl q <<<"$counts"

    # Match the file's existing line endings so we don't create mixed CRLF/LF.
    eol=$'\n'
    if grep -q $'\r' "$file"; then eol=$'\r\n'; fi

    # Close any unterminated final line so the appended heading starts on its
    # own line. Combined with the leading eol below, this guarantees exactly
    # one blank line before `## Metrics` (valid markdown) regardless of whether
    # the source file ended with a newline.
    if [ -n "$(tail -c1 "$file")" ]; then printf '%s' "$eol" >> "$file"; fi

    printf '%s## Metrics%s%sfindings: %s%srisks_HIGH: %s%srisks_MEDIUM: %s%srisks_LOW: %s%sclarifying_Qs: %s%s%s<!-- backfilled by scripts/backfill-research-metrics.sh on %s -- counts are inferred, not directly authored -->%s' \
      "$eol" "$eol" "$eol" \
      "$f" "$eol" "$rh" "$eol" "$rm" "$eol" "$rl" "$eol" "$q" "$eol" \
      "$eol" "$(date -u +%Y-%m-%d)" "$eol" >> "$file"

    echo "[backfill] $file  findings=$f risks(H/M/L)=$rh/$rm/$rl clarifying_Qs=$q (inferred)" >&2
    touched=$((touched + 1))
  done

  if [ "$touched" -gt 0 ]; then
    echo "[backfill] $touched file(s) updated" >&2
    exit 1
  fi
  echo "[backfill] no work needed" >&2
  exit 0
}

main "$@"
