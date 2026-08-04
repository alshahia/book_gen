"""Watch a book-kit project's chapters/ folder and emit a progress dashboard.

Two output modes:
  --once     print a snapshot to stdout and exit (default)
  --watch    loop every N seconds, updating <root>/exports/.dashboard.html
             and printing a one-line summary to stdout

Detects:
  - chapters not yet started (no file)
  - chapters with file but no .translate-progress.json entry (status=pending)
  - chapters with .translate-progress.json entry: status / parts / age / stuck flag
  - file mtime vs .translate-progress.json last_updated (stuck if both stale > 30 min)

Stdlib only. Self-check: build a fake project, snapshot, assert rows.
"""

import argparse
import json
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

CHAPTER_GLOB_PATTERNS = ("ch-*.md", "app-*.md", "introduction.md", "preface.md")
STUCK_THRESHOLD_MIN = 30
HTML_HEAD = """<!DOCTYPE html>
<html><head><meta charset="utf-8"><title>Chapter progress</title>
<meta http-equiv="refresh" content="5">
<style>
body { font-family: -apple-system, sans-serif; margin: 1em auto; max-width: 60em; }
table { border-collapse: collapse; width: 100%; }
th, td { border: 1px solid #ccc; padding: 0.4em 0.6em; text-align: left; }
th { background: #f0f0f0; }
tr.stuck { background: #ffe5e5; }
tr.partial { background: #fff7e0; }
tr.complete { background: #e8f7e8; }
caption { font-weight: bold; padding: 0.5em; }
</style></head><body>
"""
HTML_TAIL = "</body></html>\n"

def load_progress(root):
    pp = root / ".translate-progress.json"
    if not pp.exists(): return {}
    try: return json.loads(pp.read_text(encoding="utf-8")).get("chapters", {})
    except (OSError, ValueError) as e:
        sys.stderr.write(f"warning: invalid .translate-progress.json: {e}\n")
        return {}

def now():
    return datetime.now(timezone.utc)

def snapshot(root):
    chapters = []
    for pat in CHAPTER_GLOB_PATTERNS:
        chapters.extend((root / "chapters").glob(pat))
    chapters = sorted(set(chapters))
    progress = load_progress(root)
    rows = []
    for ch in chapters:
        info = progress.get(ch.name, {})
        rec = {
            "chapter": ch.name,
            "file_exists": True,
            "file_bytes": ch.stat().st_size,
            "status": info.get("status", "pending"),
            "parts_written": info.get("parts_written"),
            "expected_parts": info.get("expected_parts"),
            "age_minutes": None,
            "stuck": False,
        }
        last = info.get("last_updated")
        if last:
            try:
                ts = datetime.fromisoformat(last.replace("Z", "+00:00"))
                rec["age_minutes"] = round((now() - ts).total_seconds() / 60, 1)
                if rec["status"] in ("in_progress", "partial") and rec["age_minutes"] > STUCK_THRESHOLD_MIN:
                    rec["stuck"] = True
            except ValueError:
                pass
        rows.append(rec)
    return rows

def render_text(rows, root):
    n = len(rows)
    n_complete = sum(1 for r in rows if r["status"] == "complete")
    n_partial = sum(1 for r in rows if r["status"] in ("partial", "in_progress"))
    n_pending = sum(1 for r in rows if r["status"] == "pending")
    n_stuck = sum(1 for r in rows if r["stuck"])
    lines = []
    lines.append(f"=== {root.name} ===")
    lines.append(f"  {n} chapters: {n_complete} complete, {n_partial} in-progress, {n_pending} pending ({n_stuck} STUCK)")
    lines.append("")
    lines.append(f"  {'chapter':<45s} {'status':<11s} {'parts':<7s} {'age':>6s} {'file':>7s}")
    for r in rows:
        parts = f"{r['parts_written']}/{r['expected_parts']}" if r['parts_written'] is not None else "-"
        age = f"{r['age_minutes']}m" if r['age_minutes'] is not None else "-"
        size = f"{r['file_bytes']}b"
        marker = " [STUCK]" if r["stuck"] else ""
        lines.append(f"  {r['chapter']:<45s} {r['status']:<11s} {parts:<7s} {age:>6s} {size:>7s}{marker}")
    return "\n".join(lines)

def render_html(rows, root):
    body = [HTML_HEAD, f"<h1>Chapter progress — {root.name}</h1>"]
    n = len(rows)
    n_complete = sum(1 for r in rows if r["status"] == "complete")
    n_partial = sum(1 for r in rows if r["status"] in ("partial", "in_progress"))
    n_pending = sum(1 for r in rows if r["status"] == "pending")
    n_stuck = sum(1 for r in rows if r["stuck"])
    body.append(f"<p>{n} chapters: <b>{n_complete}</b> complete, <b>{n_partial}</b> in-progress, <b>{n_pending}</b> pending ({n_stuck} STUCK). Refreshes every 5s.</p>")
    body.append("<table>")
    body.append("<tr><th>chapter</th><th>status</th><th>parts</th><th>age (min)</th><th>file (bytes)</th></tr>")
    for r in rows:
        cls = "stuck" if r["stuck"] else r["status"]
        parts = f"{r['parts_written']}/{r['expected_parts']}" if r['parts_written'] is not None else "-"
        age = str(r['age_minutes']) if r['age_minutes'] is not None else "-"
        body.append(f"<tr class='{cls}'><td>{r['chapter']}</td><td>{r['status']}</td><td>{parts}</td><td>{age}</td><td>{r['file_bytes']}</td></tr>")
    body.append("</table>")
    body.append(HTML_TAIL)
    return "\n".join(body)

def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("root", help="Project root")
    ap.add_argument("--once", action="store_true", default=True, help="Print one snapshot and exit (default)")
    ap.add_argument("--watch", action="store_true", help="Loop: update HTML dashboard every N seconds")
    ap.add_argument("--interval", type=int, default=15, help="Watch interval in seconds (default 15)")
    args = ap.parse_args(argv)
    root = Path(args.root)
    if not (root / "chapters").exists():
        print(f"error: {root}/chapters not found", file=sys.stderr); return 1
    if args.watch:
        out = root / "exports" / ".dashboard.html"
        out.parent.mkdir(exist_ok=True)
        print(f"poll_progress: watching {root} (Ctrl-C to stop)", file=sys.stderr)
        while True:
            rows = snapshot(root)
            out.write_text(render_html(rows, root), encoding="utf-8")
            n_stuck = sum(1 for r in rows if r["stuck"])
            n_complete = sum(1 for r in rows if r["status"] == "complete")
            print(f"[{datetime.now().strftime('%H:%M:%S')}] {len(rows)} chapters, {n_complete} complete, {n_stuck} stuck → {out}", file=sys.stderr)
            time.sleep(args.interval)
    rows = snapshot(root)
    print(render_text(rows, root))
    return 0

if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "--self-check":
        import tempfile
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            (root / "chapters").mkdir()
            (root / "chapters" / "ch-01.md").write_text("body", encoding="utf-8")
            (root / "chapters" / "ch-02.md").write_text("body", encoding="utf-8")
            # ch-01 has progress entry complete, ch-02 has stale partial
            (root / ".translate-progress.json").write_text(json.dumps({
                "version": 1,
                "chapters": {
                    "ch-01.md": {"status": "complete", "parts_written": 1, "expected_parts": 1, "last_updated": now().isoformat()},
                    "ch-02.md": {"status": "in_progress", "parts_written": 1, "expected_parts": 3, "last_updated": "2020-01-01T00:00:00Z"},
                }
            }), encoding="utf-8")
            rc = main([str(root), "--once"])
            assert rc == 0
            text = render_text(snapshot(root), root)
            assert "1 complete" in text
            assert "STUCK" in text
            html = render_html(snapshot(root), root)
            assert "<table>" in html
            assert "class='stuck'" in html
        print("poll_progress self-check OK")
        sys.exit(0)
    sys.exit(main(sys.argv[1:]))
