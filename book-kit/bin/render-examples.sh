#!/usr/bin/env bash
# render-examples.sh - re-render book-kit/examples/*.html to *.pdf.
#
# Usage:
#   bash book-kit/bin/render-examples.sh [--dry-run]
#
# Renders every .html in book-kit/examples/ to a sibling .pdf using Chrome
# headless, the same engine md2pdf.py uses. The committed .pdf files were
# produced by this script; re-run it after editing any sample's HTML or CSS
# so the committed PDFs stay in sync with their sources.
#
# --dry-run lists the files that would be rendered and exits 0 without
# launching Chrome. Use it to verify the sample set before rendering.
#
# Chrome discovery order:
#   1. $CHROME_PATH (explicit override)
#   2. chrome / google-chrome / chromium / msedge on PATH
#   3. the standard Windows/macOS/Linux install locations
#
# Exits 0 when every sample rendered, 1 when no sample HTML is found,
# 2 when Chrome is absent (set CHROME_PATH and re-run), 3 when one or
# more renders produced a missing or implausibly small PDF.
#
# Stdlib-only. POSIX-portable.

set -e

EXAMPLES_DIR="$(cd "$(dirname "$0")/../examples" && pwd)"

# A correctly rendered sample is ~80 KB. Chrome exits 0 even when it fails
# to load the input and prints its own error page instead, so size is the
# signal that separates a real render from a silent failure.
MIN_PDF_BYTES=20000

DRY_RUN=0
[ "${1:-}" = "--dry-run" ] && DRY_RUN=1

if [ "$DRY_RUN" -eq 1 ]; then
    count=0
    for html in "$EXAMPLES_DIR"/*.html; do
        [ -e "$html" ] || continue
        count=$((count + 1))
    done
    [ "$count" -gt 0 ] || { echo "ERROR: no .html samples in $EXAMPLES_DIR" >&2; exit 1; }
    echo "render-examples.sh --dry-run: $count sample(s) in $EXAMPLES_DIR"
    for html in "$EXAMPLES_DIR"/*.html; do
        [ -e "$html" ] || continue
        echo "  $(basename "$html") -> $(basename "${html%.html}.pdf")"
    done
    exit 0
fi

find_chrome() {
    if [ -n "${CHROME_PATH:-}" ] && [ -x "$CHROME_PATH" ]; then
        echo "$CHROME_PATH"
        return 0
    fi
    for name in chrome google-chrome chromium chromium-browser msedge; do
        found="$(command -v "$name" 2>/dev/null || true)"
        [ -n "$found" ] && { echo "$found"; return 0; }
    done
    for path in \
        "/c/Program Files/Google/Chrome/Application/chrome.exe" \
        "/c/Program Files (x86)/Google/Chrome/Application/chrome.exe" \
        "/c/Program Files (x86)/Microsoft/Edge/Application/msedge.exe" \
        "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome" \
        "/usr/bin/google-chrome" \
        "/usr/bin/chromium"; do
        [ -x "$path" ] && { echo "$path"; return 0; }
    done
    return 1
}

# Chrome is a native binary: under Git Bash / MSYS / Cygwin it cannot read
# the POSIX path this script sees ("/e/book_gen/..."), so hand it a native
# "file:///E:/book_gen/..." URI instead. Without this the browser silently
# renders its own "file not found" page and still exits 0.
to_file_uri() {
    if command -v cygpath >/dev/null 2>&1; then
        echo "file:///$(cygpath -m "$1")"
    else
        echo "file://$1"
    fi
}

CHROME="$(find_chrome || true)"
[ -n "$CHROME" ] || { echo "ERROR: Chrome/Edge not found. Set CHROME_PATH and re-run." >&2; exit 2; }

count=0
for html in "$EXAMPLES_DIR"/*.html; do
    [ -e "$html" ] || continue
    count=$((count + 1))
done
[ "$count" -gt 0 ] || { echo "ERROR: no .html samples in $EXAMPLES_DIR" >&2; exit 1; }

echo "render-examples.sh: rendering $count sample(s) with $CHROME"

failed=0
for html in "$EXAMPLES_DIR"/*.html; do
    [ -e "$html" ] || continue
    pdf="${html%.html}.pdf"
    rm -f "$pdf"
    "$CHROME" \
        --headless=new \
        --disable-gpu \
        --no-sandbox \
        --no-pdf-header-footer \
        --print-to-pdf="$pdf" \
        "$(to_file_uri "$html")" 2>/dev/null || true

    if [ ! -f "$pdf" ]; then
        echo "  FAIL $(basename "$html") -> no PDF produced" >&2
        failed=$((failed + 1))
        continue
    fi
    bytes="$(wc -c < "$pdf" | tr -d ' ')"
    if [ "$bytes" -lt "$MIN_PDF_BYTES" ]; then
        echo "  FAIL $(basename "$html") -> ${bytes}B (< ${MIN_PDF_BYTES}B; Chrome likely rendered an error page)" >&2
        failed=$((failed + 1))
        continue
    fi
    echo "  $(basename "$html") -> $(basename "$pdf") (${bytes}B)"
done

if [ "$failed" -gt 0 ]; then
    echo "render-examples.sh: $failed of $count sample(s) FAILED" >&2
    exit 3
fi

echo "render-examples.sh: done ($count rendered)"
