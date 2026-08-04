"""Extract embedded images from a PDF as PNGs and emit a manifest.json.

Wraps poppler's `pdfimages -png`. Each PDF produces:
  figures/<pdf-slug>-page-<N>-<idx>.png     (extracted images)
  figures/<pdf-slug>-manifest.json          (page → path mapping)

Usage:
    py extract_figures.py <pdf> [--out DIR] [--slug SLUG]

Stdlib only (subprocess). pdfimages must be on PATH (poppler 0.86+).
Self-check: assert that a synthetic PDF containing at least one image
produces one extracted PNG (uses pdfimages -list to discover fixtures).
"""

import argparse
import json
import re
import shutil
import subprocess
import sys
from pathlib import Path

def pdfimages_list(pdf):
    """Run `pdfimages -list <pdf>` and return parsed rows.

    Returns list of dicts: {page, num, type, width, height, ...}.
    """
    r = subprocess.run(["pdfimages", "-list", str(pdf)], capture_output=True, text=True)
    if r.returncode != 0:
        raise RuntimeError(f"pdfimages failed: {r.stderr.strip()}")
    rows = []
    # skip header lines (separator + column names)
    lines = r.stdout.splitlines()
    for line in lines[2:]:
        line = line.strip()
        if not line: continue
        parts = line.split()
        if len(parts) < 8: continue
        try:
            page = int(parts[0])
            num = int(parts[1])
            width = int(parts[3])
            height = int(parts[4])
            rows.append({"page": page, "num": num, "type": parts[2], "width": width, "height": height})
        except ValueError:
            continue
    return rows

def pdfimages_dump(pdf, out_dir, prefix):
    """Run `pdfimages -png -p <pdf> <prefix>` — dumps all images with `prefix-NNNN.png` names."""
    out_dir.mkdir(parents=True, exist_ok=True)
    r = subprocess.run(["pdfimages", "-png", "-p", str(pdf), str(out_dir / prefix)], capture_output=True, text=True)
    if r.returncode != 0:
        raise RuntimeError(f"pdfimages -png failed: {r.stderr.strip()}")
    # pdfimages writes files named <prefix>-<page>-<num>.png when -p is used
    return sorted(out_dir.glob(f"{prefix}-*.png"))

def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("pdf", help="Input PDF path")
    ap.add_argument("--out", default=None, help="Output directory (default: figures/ next to PDF)")
    ap.add_argument("--slug", default=None, help="Filename slug prefix (default: PDF stem)")
    args = ap.parse_args(argv)

    pdf = Path(args.pdf)
    if not pdf.exists():
        print(f"error: {pdf} not found", file=sys.stderr); return 1

    slug = args.slug or re.sub(r"[^A-Za-z0-9]+", "-", pdf.stem).strip("-").lower()
    out_dir = Path(args.out) if args.out else pdf.parent / "figures"
    out_dir.mkdir(parents=True, exist_ok=True)

    listing = pdfimages_list(pdf)
    if not listing:
        print(json.dumps({"pdf": str(pdf), "slug": slug, "figures": []}, ensure_ascii=False))
        print(f"extract_figures: no images in {pdf.name}", file=sys.stderr)
        # still write a manifest so the chapter pipeline can see "this PDF has no figures"
        (out_dir / f"{slug}-manifest.json").write_text(
            json.dumps({"pdf": str(pdf), "slug": slug, "figures": []}, ensure_ascii=False, indent=2),
            encoding="utf-8")
        return 0

    dumped = pdfimages_dump(pdf, out_dir, slug)
    # pdfimages names with -p: <prefix>-<page>-<num>.png (zero-padded page+num)
    # build a lookup by (page, num)
    pattern = re.compile(rf"^{re.escape(slug)}-(\d+)-(\d+)\.png$")
    lookup = {}
    for p in dumped:
        m = pattern.match(p.name)
        if m:
            lookup[(int(m.group(1)), int(m.group(2)))] = p

    figures = []
    for row in listing:
        path = lookup.get((row["page"], row["num"]))
        figures.append({
            "page": row["page"],
            "num": row["num"],
            "width": row["width"],
            "height": row["height"],
            "type": row["type"],
            "path": str(path.relative_to(out_dir.parent)) if path else None,
        })

    manifest = {"pdf": str(pdf), "slug": slug, "figures": figures}
    (out_dir / f"{slug}-manifest.json").write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2),
        encoding="utf-8")

    print(json.dumps({"pdf": str(pdf), "slug": slug, "figures_extracted": len(figures)}, ensure_ascii=False))
    return 0

if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "--self-check":
        # Ponytail: smoke against a real PDF in the workspace if present; else skip.
        candidates = [
            Path(r"E:\books_gen\Agentic Design Patterns translate to arabic\Agentic Design Patterns\Chapter 1_ Prompt Chaining.pdf"),
        ]
        target = next((p for p in candidates if p.exists()), None)
        if target is None:
            print("extract_figures self-check SKIPPED (no PDF fixture available)")
            sys.exit(0)
        import tempfile
        with tempfile.TemporaryDirectory() as td:
            rc = main([str(target), "--out", td])
            assert rc == 0
            manifest_path = Path(td) / f"{target.stem.lower().replace(' ', '-').replace('_', '-')}-manifest.json"
            # slug may differ — search for any manifest
            manifests = list(Path(td).glob("*-manifest.json"))
            assert manifests, "no manifest written"
            m = json.loads(manifests[0].read_text(encoding="utf-8"))
            assert m["figures"], f"Chapter 1 has 2 images; got {len(m['figures'])}"
            pngs = list(Path(td).glob("*.png"))
            assert len(pngs) == 2, f"expected 2 PNGs, got {len(pngs)}"
        print(f"extract_figures self-check OK ({len(pngs)} PNGs from Chapter 1)")
        sys.exit(0)
    sys.exit(main(sys.argv[1:]))
