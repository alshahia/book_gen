#!/usr/bin/env bash
# check-book-repo.sh - warn if a book directory is not a git repo.
#
# Usage:
#   bash book-kit/bin/check-book-repo.sh [BOOK_DIR]
#
# Exits 0 when BOOK_DIR/.git exists. Exits 1 with a clear stderr warning
# when it doesn't, so the orchestrator can surface the warning and skip
# beat-boundary git tags. Default BOOK_DIR is "." (cwd).
#
# Stdlib-only. POSIX-portable (uses `[ -d ]`, not `[[ -d ]]`).

set -e

# POSIX-portable single-line guard. Returns 0 when .git exists; returns
# 1 with a stderr warning when it doesn't.
[ -d "${1:-.}/.git" ] || { echo "WARNING: ${1:-.} is not a git repo; beat-boundary snapshots disabled. Run 'git init' to enable." >&2; exit 1; }
echo "${1:-.}: git repo OK"
