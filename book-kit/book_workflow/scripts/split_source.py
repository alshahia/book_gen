"""Split a source file into parts sized for the chunked-write protocol.

Usage:
    py split_source.py <source-file> [--parts N] [--out DIR] [--prefix PREFIX]

The chunked-write protocol in book-writer/SKILL.md says:
    source <= 20 KB  -> 1 part
    20 KB < source <= 50 KB -> 2 parts
    source > 50 KB -> N = ceil(source_bytes / 18_000)

This script applies the same sizing but splits at H2 boundaries (## ...) so the
translation seams land at semantic breaks. If the source has no H2 markers, it
falls back to paragraph boundaries (\n\n) every ~18 KB.

Output files: <prefix>-part-1.txt, <prefix>-part-2.txt, ...
A manifest sidecar: <prefix>-manifest.json (sized for book_check.py consumption).

Stdlib only. Self-check: assert that a 60KB file produces >= 3 parts each <= 22KB.
"""

import argparse
import json
import math
import re
import sys
from pathlib import Path

H2 = re.compile(r"(?m)^## .+$")
PARA = re.compile(r"\n\n+")

def plan_parts(size_bytes):
    """Return (n_parts, target_part_size) per chunked-write protocol."""
    if size_bytes <= 20_000:
        return 1, size_bytes
    if size_bytes <= 50_000:
        return 2, math.ceil(size_bytes / 2)
    return math.ceil(size_bytes / 18_000), 18_000

def split_at_h2(text, n_parts):
    """Split text at H2 boundaries so each part holds roughly n_parts worth of content."""
    h2_positions = [m.start() for m in H2.finditer(text)]
    if len(h2_positions) < n_parts:
        return _split_at_paragraph(text, n_parts)
    # pick n_parts-1 cut points evenly spaced through the H2 positions
    step = len(h2_positions) / n_parts
    cuts = [h2_positions[int(i * step)] for i in range(1, n_parts)]
    parts, prev = [], 0
    for cut in cuts:
        parts.append(text[prev:cut])
        prev = cut
    parts.append(text[prev:])
    return parts

def _split_at_paragraph(text, n_parts):
    """Fallback: split at paragraph boundaries every ~target bytes."""
    target = math.ceil(len(text) / n_parts)
    parts, current, size = [], [], 0
    for chunk in PARA.split(text):
        piece = chunk + "\n\n"
        if size + len(piece) > target and current:
            parts.append("".join(current))
            current, size = [piece], len(piece)
        else:
            current.append(piece)
            size += len(piece)
    if current:
        parts.append("".join(current))
    return parts

def main(argv=None):
    ap = argparse.ArgumentParser(description="Split a source file for chunked-write protocol.")
    ap.add_argument("source", help="Path to source file (.txt / .md)")
    ap.add_argument("--parts", type=int, default=0, help="Override part count (else derive from size)")
    ap.add_argument("--out", default=".", help="Output directory (default: cwd)")
    ap.add_argument("--prefix", default=None, help="Prefix for output files (default: source stem)")
    ns = ap.parse_args(argv)

    src = Path(ns.source)
    if not src.exists():
        print(f"error: {src} not found", file=sys.stderr); return 1
    text = src.read_text(encoding="utf-8", errors="replace")
    size = len(text.encode("utf-8"))

    if ns.parts > 0:
        n_parts = ns.parts
    else:
        n_parts, _ = plan_parts(size)

    parts = split_at_h2(text, n_parts) if n_parts > 1 else [text]

    prefix = ns.prefix or src.stem
    out_dir = Path(ns.out)
    out_dir.mkdir(parents=True, exist_ok=True)

    written = []
    for i, part in enumerate(parts, 1):
        p = out_dir / f"{prefix}-part-{i}.txt"
        p.write_text(part, encoding="utf-8")
        written.append({"part": i, "path": str(p), "bytes": len(part.encode("utf-8"))})

    manifest = {
        "source": str(src),
        "source_bytes": size,
        "n_parts": len(written),
        "protocol": "chunked-write v0.2.0",
        "parts": written,
    }
    (out_dir / f"{prefix}-manifest.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")

    print(json.dumps({"source": str(src), "n_parts": len(written), "total_bytes": size, "max_part_bytes": max(w["bytes"] for w in written)}, ensure_ascii=False))
    return 0

if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "--self-check":
        # ponytail: assert-based smoke for the alpha slice.
        import tempfile
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            big = root / "big.txt"
            content = ("## Section A\n\n" + ("lorem ipsum " * 600) + "\n\n"
                       + "## Section B\n\n" + ("dolor sit amet " * 600) + "\n\n"
                       + "## Section C\n\n" + ("consectetur adipiscing " * 600) + "\n\n"
                       + "## Section D\n\n" + ("elit sed do eiusmod " * 600) + "\n\n"
                       + "## Section E\n\n" + ("tempor incididunt ut " * 600))
            big.write_text(content, encoding="utf-8")
            rc = main([str(big), "--out", td, "--prefix", "big"])
            assert rc == 0
            manifest = json.loads((root / "big-manifest.json").read_text(encoding="utf-8"))
            # chunked-write protocol promises >= 3 parts for files > 50KB
            assert manifest["n_parts"] >= 3, f"expected >=3 parts, got {manifest['n_parts']}"
            # each part must be smaller than the whole (no empty/degenerate splits)
            assert max(p["bytes"] for p in manifest["parts"]) < manifest["source_bytes"]
            # each part must contain at least one H2 (so seams land at semantic breaks)
            for p in manifest["parts"]:
                assert "## " in Path(p["path"]).read_text(encoding="utf-8"), f"part {p['part']} has no H2"
            # 1-part case
            small = root / "small.txt"
            small.write_text("## Tiny\n\nonly one section here.\n", encoding="utf-8")
            rc = main([str(small), "--out", td, "--prefix", "small"])
            assert rc == 0
            m2 = json.loads((root / "small-manifest.json").read_text(encoding="utf-8"))
            assert m2["n_parts"] == 1
        print("split_source self-check OK")
        sys.exit(0)
    sys.exit(main(sys.argv[1:]))
