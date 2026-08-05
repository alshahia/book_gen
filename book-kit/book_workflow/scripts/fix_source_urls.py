"""Fix pdftotext artifacts in source/*.txt files.

`pdftotext -layout` introduces several artifacts at PDF column boundaries:
1. Pure-digit lines (PDF page numbers, e.g. "28") appearing on their own line
   after a URL-bearing reference line.
2. Page numbers glued to the end of a URL on the same line (e.g.
   `https://example.com/path/6` where 6 is the page number).
3. Truncated URLs split across consecutive lines
   (e.g. `https://...very/long/path\n...continued`).
4. Doubled last segment from pdftotext concatenating two adjacent lines
   (e.g. `https://x/langgraph\nlanggraph` -> `langgraphlanggraph`).
5. Trailing `..` (line-wrap artifact).
6. Trailing `/#` (empty fragment artifact).

The chapter (translator's read of the actual PDF) preserves the canonical
full URL without page-number artifacts. This script repairs the source
text so bilingual_smoke.py does not flag false positives.

Detection rules (applied in order, idempotent):
- (1) Pure-digit standalone line immediately after a URL-bearing line: drop
      the pure-digit line entirely.
- (2) URL ending in `/N` (1-3 digits): strip the trailing `/N`.
- (3) Line ending with `https?://...`, next non-blank line is pure URL-fragment
      chars (no spaces): join them.
- (4) URL last segment is doubled word (>=3 chars): strip the second copy.
- (5) URL ending with `..`: trim to single `.`.
- (6) URL ending with `/#`: strip the trailing `#`, keep the `/`.

Known limitations (NOT auto-fixed; requires manual review):
- Page number glued directly to URL body without `/` separator
  (e.g. `https://arxiv.org/abs/1707.0634712` -> `1707.06347`).
  Risk of false positives on legitimate IDs.
- Doubled segments not at the END of URL
  (e.g. `https://x/adk-docs/mcp/databases/databases`).
- Two URLs concatenated when they should be on separate lines
  (e.g. `https://arxiv.org/pdf/2504.15228https://github.com/...`).
- Concatenated path + path on adjacent lines
  (e.g. `https://openrouter.ai/rankings` + `api/v1/chat/completions`
  -> `https://openrouter.ai/rankingsapi/v1/chat/completions`).

Stdlib only. Self-check covers cases 1-3, 4, 5, 6, and a regression for
case 4 false-positive (`whitepaper-foo` must NOT be stripped).

Typical usage:
    python fix_source_urls.py <source_dir>             # apply all fixes
    python fix_source_urls.py <source_dir> --dry-run  # report only, no writes
    python fix_source_urls.py --self-check             # verify regex behavior
"""
import argparse
import re
import sys
from pathlib import Path

# (1) and (3): URL prefix at end of current line
URL_OPEN_RE = re.compile(r"https?://[^\s)\]<>\"']+$")
# (3): URL-fragment chars on the next line
URL_CONT_RE = re.compile(r"^[A-Za-z0-9._~:/?#\[\]@!$&'()*+,;=%-]+$")
# (1): pure-digit line = PDF page number
PURE_DIGIT_RE = re.compile(r"^\d+$")
# (2): trailing page-number glued to URL — `/N` where N is 1-3 digits,
# optionally followed by end-of-line / closing bracket. Greedy match on the
# URL body consumes up to the LAST `/` so multi-segment URLs (e.g.
# `https://example.com/a/b/c/14`) strip only the trailing page number.
URL_TRAILING_PAGENUM_RE = re.compile(r"(https?://[^\s)\]<>\"']*)/(\d{1,3})(?=$|[\s)\]<>\"',;])")
# (4): doubled last segment — pdftotext concatenates two adjacent lines into
# the URL (e.g. `langgraph\nlanggraph` -> `langgraphlanggraph`). Strip the
# second occurrence of the trailing word. Require `\2` to be >=3 chars and
# start with a letter so single-char / digit-suffix collisions (e.g.
# `whitepaper-foo` -> `whitepaper-f`) are rejected.
URL_DOUBLED_SEG_RE = re.compile(r"(https?://[^\s)\]<>\"'/]+/)([A-Za-z][A-Za-z0-9_-]{2,})\2(?=$|[\s)\]<>\"',;])")
# (5): trailing `..` — pdftotext line-wrap artifact. Trim to single `.`.
URL_TRAILING_DOTDOT_RE = re.compile(r"(https?://[^\s)\]<>\"']*?)\.\.(?=$|[\s)\]<>\"',;])")
# (6): truncated fragment — URL ending with `/#` has an empty fragment
# artifact. Strip the trailing `#` but KEEP the trailing `/`.
URL_TRAILING_HASH_RE = re.compile(r"(https?://\S*?)(/)#$")

def fix_pure_digit_lines(lines):
    """Drop pure-digit lines that immediately follow a URL-bearing line."""
    out = []
    i = 0
    dropped = 0
    while i < len(lines):
        line = lines[i]
        if (PURE_DIGIT_RE.match(line.strip())
                and out
                and URL_OPEN_RE.search(out[-1])):
            dropped += 1
            i += 1
            continue
        out.append(line)
        i += 1
    return out, dropped

def fix_trailing_page_numbers(lines):
    """Strip trailing /N page numbers from URLs on any line.

    PDFs in reference sections often append a page number directly to the
    URL (e.g. `https://example.com/path/6`). The 1-3-digit trailing segment
    after a final `/` is a strong page-number signal: real URLs ending in
    `/N` where N is 1-3 digits are rare in practice (and where they exist,
    the `/N` is usually pagination that the chapter does not preserve
    anyway).
    """
    fixed_lines = []
    fixed = 0
    for line in lines:
        def _strip(m):
            nonlocal fixed
            fixed += 1
            return m.group(1)
        new_line = URL_TRAILING_PAGENUM_RE.sub(_strip, line)
        fixed_lines.append(new_line)
    return fixed_lines, fixed

def fix_doubled_segments(lines):
    """Strip doubled last segment from URLs (e.g. `langgraphlanggraph` -> `langgraph`).

    pdftotext occasionally concatenates two lines that should be separate
    reference entries, producing URLs like `langgraphlanggraph`,
    `databases/databases`, or `rankingsrankings`.
    """
    fixed_lines = []
    fixed = 0
    for line in lines:
        def _strip(m):
            nonlocal fixed
            fixed += 1
            return m.group(1) + m.group(2)
        new_line = URL_DOUBLED_SEG_RE.sub(_strip, line)
        fixed_lines.append(new_line)
    return fixed_lines, fixed

def fix_trailing_dotdot(lines):
    """Trim trailing `..` from URLs (line-wrap artifact)."""
    fixed_lines = []
    fixed = 0
    for line in lines:
        def _strip(m):
            nonlocal fixed
            fixed += 1
            return m.group(1) + "."
        new_line = URL_TRAILING_DOTDOT_RE.sub(_strip, line)
        fixed_lines.append(new_line)
    return fixed_lines, fixed

def fix_trailing_hash(lines):
    """Strip trailing empty fragment `/#` from URLs, keep the trailing `/`."""
    fixed_lines = []
    fixed = 0
    for line in lines:
        def _strip(m):
            nonlocal fixed
            fixed += 1
            return m.group(1) + m.group(2)
        new_line = URL_TRAILING_HASH_RE.sub(_strip, line)
        fixed_lines.append(new_line)
    return fixed_lines, fixed

def fix_truncated_urls(lines):
    """Join URLs that pdftotext split across 2 lines (excluding pure-digit next-line)."""
    out = []
    i = 0
    joins = 0
    while i < len(lines):
        line = lines[i]
        m_open = URL_OPEN_RE.search(line)
        if m_open and i + 1 < len(lines):
            j = i + 1
            while j < len(lines) and lines[j].strip() == "":
                j += 1
            if j < len(lines):
                cont = lines[j].strip()
                if not PURE_DIGIT_RE.match(cont) and URL_CONT_RE.match(cont):
                    out.append(line + cont)
                    i = j + 1
                    joins += 1
                    continue
        out.append(line)
        i += 1
    return out, joins

def fix_all(text):
    """Apply all fixes. Returns (new_text, dict_of_counts)."""
    lines = text.splitlines(keepends=False)
    counts = {"dropped_digit_lines": 0, "stripped_trailing_page_nums": 0,
              "stripped_doubled_segments": 0, "trimmed_trailing_dotdot": 0,
              "stripped_trailing_hash": 0, "joined_lines": 0}

    lines, dropped = fix_pure_digit_lines(lines)
    counts["dropped_digit_lines"] += dropped

    lines, stripped = fix_trailing_page_numbers(lines)
    counts["stripped_trailing_page_nums"] += stripped

    lines, doubled = fix_doubled_segments(lines)
    counts["stripped_doubled_segments"] += doubled

    lines, dotdot = fix_trailing_dotdot(lines)
    counts["trimmed_trailing_dotdot"] += dotdot

    lines, hashcount = fix_trailing_hash(lines)
    counts["stripped_trailing_hash"] += hashcount

    lines, joined = fix_truncated_urls(lines)
    counts["joined_lines"] += joined

    new_text = "\n".join(lines) + ("\n" if text.endswith("\n") else "")
    return new_text, counts

def process_file(path):
    text = path.read_text(encoding="utf-8")
    new_text, counts = fix_all(text)
    if any(counts.values()):
        path.write_text(new_text, encoding="utf-8")
    return counts

def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("source_dir", help="Directory of .txt source files")
    ap.add_argument("--dry-run", action="store_true", help="Report fixes without writing")
    args = ap.parse_args(argv)
    src_dir = Path(args.source_dir)
    if not src_dir.is_dir():
        print(f"not a directory: {src_dir}", file=sys.stderr)
        return 1
    totals = {"dropped_digit_lines": 0, "stripped_trailing_page_nums": 0,
              "stripped_doubled_segments": 0, "trimmed_trailing_dotdot": 0,
              "stripped_trailing_hash": 0, "joined_lines": 0}
    files_changed = 0
    for path in sorted(src_dir.glob("*.txt")):
        text = path.read_text(encoding="utf-8")
        new_text, counts = fix_all(text)
        if any(counts.values()):
            files_changed += 1
            for k, v in counts.items():
                totals[k] += v
            if not args.dry_run:
                path.write_text(new_text, encoding="utf-8")
            print(f"{path.name}: {counts}", file=sys.stderr)
    print(f"fix_source_urls: {totals} across {files_changed} file(s) (dry_run={args.dry_run})", file=sys.stderr)
    return 0

if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "--self-check":
        import tempfile
        with tempfile.TemporaryDirectory() as td:
            td = Path(td)

            # Case 1: page number on its own line after URL
            src = td / "ch-page.txt"
            src.write_text(
                "References\n"
                "1.\u200b Example, https://www.example.com/whitepaper-foo\n"
                "28\n"
                "\n"
                "2.\u200b Another, https://github.com/org/repo\n",
                encoding="utf-8",
            )
            new_text, counts = fix_all(src.read_text(encoding="utf-8"))
            assert counts["dropped_digit_lines"] == 1, counts
            assert "whitepaper-foo28" not in new_text
            assert "https://www.example.com/whitepaper-foo" in new_text
            assert "https://github.com/org/repo" in new_text

            # Case 2: page number glued to URL on same line
            src = td / "ch-glued.txt"
            src.write_text(
                "   1.\u200b Google Cloud Skills Boost, https://www.cloudskillsboost.google/6\n",
                encoding="utf-8",
            )
            new_text, counts = fix_all(src.read_text(encoding="utf-8"))
            assert counts["stripped_trailing_page_nums"] == 1, counts
            assert "https://www.cloudskillsboost.google" in new_text
            assert "/6" not in new_text

            # Case 3: truncated URL split across lines
            src = td / "ch-split.txt"
            src.write_text(
                "See:\n"
                "https://www.businesstoday.in/tech-today/news/story/30-of-microsofts-code-is-now-ai\n"
                "-generated-says-ceo-satya-nadella-474167-2025-04-30\n",
                encoding="utf-8",
            )
            new_text, counts = fix_all(src.read_text(encoding="utf-8"))
            assert counts["joined_lines"] == 1, counts
            assert "https://www.businesstoday.in/tech-today/news/story/30-of-microsofts-code-is-now-ai-generated-says-ceo-satya-nadella-474167-2025-04-30" in new_text

            # Case 4: arxiv URL with legitimate trailing digits must NOT be stripped
            src = td / "ch-arxiv.txt"
            src.write_text(
                "   1.\u200b Attention is all you need, https://arxiv.org/abs/1706.03762\n",
                encoding="utf-8",
            )
            new_text, counts = fix_all(src.read_text(encoding="utf-8"))
            assert counts["stripped_trailing_page_nums"] == 0, counts
            assert "https://arxiv.org/abs/1706.03762" in new_text

            # Case 6: truncated empty fragment `/#` must be stripped
            src = td / "ch-hash.txt"
            src.write_text(
                "   1.\u200b Profile, https://www.linkedin.com/in/marco-fago/#\n",
                encoding="utf-8",
            )
            new_text, counts = fix_all(src.read_text(encoding="utf-8"))
            assert counts["stripped_trailing_hash"] == 1, counts
            assert "https://www.linkedin.com/in/marco-fago/" in new_text
            assert "fago/#" not in new_text

            # Case 5: idempotent — running on already-fixed text produces no changes
            new_text2, counts2 = fix_all(new_text)
            assert all(v == 0 for v in counts2.values()), f"idempotency failed: {counts2}"

        print("fix_source_urls self-check OK")
        sys.exit(0)
    sys.exit(main(sys.argv[1:]))
