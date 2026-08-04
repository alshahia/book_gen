#!/usr/bin/env bash
# Validator for the three-scope memory system. Walks every *.md under:
#   agents_manager/memory/{global,projects}/ + agents_manager/<role>/notes/{semantic,episodic}/
# Checks: frontmatter opens+closes, required keys (scope|topic|status|created|last_verified),
# scope/status enum, YYYY-MM-DD parse for created+last_verified, superseded_by present
# when status=superseded. Exit 0 = clean, 1 = >=1 FAIL.
#
# Note: agents_manager/memory/README.md uses scope=canonical-schema, but that file is
# NOT in the walk list (we only scan global/ + projects/), so the strict 3-value enum
# check below is correct.

set -u
ROOT="agents_manager"
ROLES=(research planning design coder review assets)
DATE_RE='^[0-9]{4}-[0-9]{2}-[0-9]{2}$'

dirs=( "$ROOT/memory/global" "$ROOT/memory/projects" )
for r in "${ROLES[@]}"; do
  dirs+=( "$ROOT/$r/notes/semantic" "$ROOT/$r/notes/episodic" )
done

files=()
for d in "${dirs[@]}"; do
  [ -d "$d" ] || continue
  while IFS= read -r f; do files+=( "$f" ); done < <(find "$d" -type f -name '*.md')
done

fail=0
for f in "${files[@]}"; do
  mapfile -t lines < <(tr -d '\r' < "$f")
  if [ "${#lines[@]}" -lt 1 ] || [ "${lines[0]}" != "---" ]; then
    echo "FAIL : $f : missing opening --- on line 1" >&2; fail=1; continue
  fi
  end=-1
  for ((i=1; i<${#lines[@]}; i++)); do [ "${lines[$i]}" = "---" ] && end=$i && break; done
  if [ "$end" -le 0 ]; then
    echo "FAIL : $f : frontmatter not closed with ---" >&2; fail=1; continue
  fi
  declare -A fm=()
  for ((i=1; i<end; i++)); do
    line="${lines[$i]}"
    [[ "$line" =~ ^[[:space:]]*(#|$) ]] && continue
    [[ "$line" =~ ^([A-Za-z_][A-Za-z0-9_-]*):[[:space:]]*(.*)$ ]] && \
      fm["${BASH_REMATCH[1],,}"]="${BASH_REMATCH[2]}"
  done
  for k in scope topic status created last_verified; do
    [ -n "${fm[$k]+x}" ] || { echo "FAIL : $f : missing required key '$k'" >&2; fail=1; }
  done
  case "${fm[scope]:-}" in
    global|project|role) ;;
    *) echo "FAIL : $f : scope '${fm[scope]:-}' not in {global,project,role}" >&2; fail=1 ;;
  esac
  case "${fm[status]:-}" in
    active|superseded) ;;
    *) echo "FAIL : $f : status '${fm[status]:-}' not in {active,superseded}" >&2; fail=1 ;;
  esac
  for k in created last_verified; do
    v="${fm[$k]:-}"
    [[ "$v" =~ $DATE_RE ]] && date -d "$v" +%Y-%m-%d >/dev/null 2>&1 || {
      echo "FAIL : $f : '$k' '$v' not a valid YYYY-MM-DD" >&2; fail=1
    }
  done
  if [ "${fm[status]:-}" = "superseded" ] && [ -z "${fm[superseded_by]+x}" ]; then
    echo "FAIL : $f : status=superseded but missing 'superseded_by'" >&2; fail=1
  fi
done

echo "OK: ${#files[@]} entries validated"
[ "$fail" -eq 0 ]