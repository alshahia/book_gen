#!/usr/bin/env bash
# check-search-keys.sh - print masked status of search-provider API keys.
#
# Usage:
#   bash book-kit/bin/check-search-keys.sh
#
# Searches for `.env.local` starting from the script's own directory and
# walking up. Sources the file silently if found. Prints one line per key
# (`FIRECRAWL_API_KEY`, `EXA_API_KEY`) showing whether the key is set
# and, when set, the last 4 characters. Exits 0 when no required key is
# missing; exits 1 when FIRECRAWL_API_KEY is unset or empty. EXA_API_KEY
# is optional and does not affect the exit code.
#
# Stdlib-only. No new dependencies. Forces UTF-8 stdout so the masked
# status line renders cleanly on Windows-cp1256 terminals (P4 #15 / P5
# #22 inheritance).

set -u

# Force UTF-8 stdout when supported (no-op on Windows-cp1256 cmd shells).
if command -v locale >/dev/null 2>&1; then
    LC_ALL="${LC_ALL:-C.UTF-8}"
    LANG="${LANG:-C.UTF-8}"
    export LC_ALL LANG
fi

# Locate .env.local: walk up from the script's directory to the workspace
# root. We check each ancestor in order, taking the first match.
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd 2>/dev/null || pwd)"
ENV_LOCAL=""
search_dir="${SCRIPT_DIR}"
for _ in 1 2 3 4 5; do
    candidate="${search_dir}/.env.local"
    if [ -f "${candidate}" ]; then
        ENV_LOCAL="${candidate}"
        break
    fi
    parent="$(dirname "${search_dir}")"
    if [ "${parent}" = "${search_dir}" ]; then
        break
    fi
    search_dir="${parent}"
done

if [ -n "${ENV_LOCAL}" ]; then
    # shellcheck disable=SC1090
    . "${ENV_LOCAL}" 2>/dev/null || true
    ENV_SOURCE="${ENV_LOCAL}"
else
    ENV_SOURCE="(not found; searched from ${SCRIPT_DIR} upward)"
fi

# Mask helper: print "set (last 4: XXXX)" when value is non-empty, else
# "missing (last 4: —)". Never echoes the full key.
mask_status() {
    local key_name="$1"
    local required="$2"
    local value="${!key_name:-}"
    if [ -z "${value}" ]; then
        if [ "${required}" = "1" ]; then
            printf '%s: missing (last 4: —)\n' "${key_name}"
        else
            printf '%s: missing (last 4: —) [optional]\n' "${key_name}"
        fi
        return 1
    fi
    local tail
    tail="$(printf '%s' "${value}" | tail -c 5 || true)"
    printf '%s: set (last 4: %s)\n' "${key_name}" "${tail}"
    return 0
}

required_missing=0

echo "env source: ${ENV_SOURCE}"

mask_status FIRECRAWL_API_KEY 1 || required_missing=1
mask_status EXA_API_KEY 0 || true

if [ "${required_missing}" -ne 0 ]; then
    exit 1
fi
exit 0
