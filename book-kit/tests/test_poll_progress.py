"""Tests for poll_progress.py — snapshot, stuck detection, dashboard HTML."""
import json
import subprocess
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path

from poll_progress import (
    CHAPTER_GLOB_PATTERNS,
    STUCK_THRESHOLD_MIN,
    main,
    render_html,
    render_text,
    snapshot,
)


def test_self_check_passes():
    r = subprocess.run(
        [sys.executable, str(Path(__file__).parent.parent / "book_workflow" / "scripts" / "poll_progress.py"), "--self-check"],
        capture_output=True, text=True, timeout=30,
    )
    assert r.returncode == 0, r.stderr
    assert "self-check OK" in r.stdout


def test_snapshot_empty_chapters(tmp_project):
    rows = snapshot(tmp_project)
    assert rows == []


def test_snapshot_chapter_without_progress(tmp_project):
    (tmp_project / "chapters" / "ch-01.md").write_text("# T\n", encoding="utf-8")
    rows = snapshot(tmp_project)
    assert len(rows) == 1
    assert rows[0]["chapter"] == "ch-01.md"
    assert rows[0]["status"] == "pending"
    assert rows[0]["stuck"] is False


def test_snapshot_complete_chapter(tmp_project):
    (tmp_project / "chapters" / "ch-01.md").write_text("# T\n", encoding="utf-8")
    (tmp_project / ".translate-progress.json").write_text(
        json.dumps({"chapters": {"ch-01.md": {"status": "complete", "parts_written": 1, "expected_parts": 1,
                                               "last_updated": datetime.now(timezone.utc).isoformat()}}}),
        encoding="utf-8",
    )
    rows = snapshot(tmp_project)
    assert rows[0]["status"] == "complete"
    assert rows[0]["stuck"] is False


def test_snapshot_stuck_detection(tmp_project):
    """A chapter with status=in_progress and last_updated > 30 min ago must be flagged stuck."""
    (tmp_project / "chapters" / "ch-01.md").write_text("# T\n", encoding="utf-8")
    stale = (datetime.now(timezone.utc) - timedelta(minutes=STUCK_THRESHOLD_MIN + 5)).isoformat()
    (tmp_project / ".translate-progress.json").write_text(
        json.dumps({"chapters": {"ch-01.md": {"status": "in_progress", "parts_written": 1, "expected_parts": 3,
                                               "last_updated": stale}}}),
        encoding="utf-8",
    )
    rows = snapshot(tmp_project)
    assert rows[0]["stuck"] is True


def test_snapshot_recent_in_progress_not_stuck(tmp_project):
    """A chapter with status=in_progress and last_updated < 30 min ago must NOT be stuck."""
    (tmp_project / "chapters" / "ch-01.md").write_text("# T\n", encoding="utf-8")
    recent = (datetime.now(timezone.utc) - timedelta(minutes=5)).isoformat()
    (tmp_project / ".translate-progress.json").write_text(
        json.dumps({"chapters": {"ch-01.md": {"status": "in_progress", "parts_written": 1, "expected_parts": 3,
                                               "last_updated": recent}}}),
        encoding="utf-8",
    )
    rows = snapshot(tmp_project)
    assert rows[0]["stuck"] is False


def test_snapshot_covers_all_chapter_patterns(tmp_project):
    """Glob covers ch-*, app-*, introduction.md, preface.md."""
    for name in ("ch-01.md", "app-a.md", "introduction.md", "preface.md", "README.md"):
        (tmp_project / "chapters" / name).write_text("# T\n", encoding="utf-8")
    rows = snapshot(tmp_project)
    names = {r["chapter"] for r in rows}
    assert "ch-01.md" in names
    assert "app-a.md" in names
    assert "introduction.md" in names
    assert "preface.md" in names
    assert "README.md" not in names


def test_render_text_includes_summary(tmp_project):
    (tmp_project / "chapters" / "ch-01.md").write_text("# T\n", encoding="utf-8")
    rows = snapshot(tmp_project)
    text = render_text(rows, tmp_project)
    assert "1 chapters" in text
    assert "ch-01.md" in text


def test_render_html_contains_styling(tmp_project):
    (tmp_project / "chapters" / "ch-01.md").write_text("# T\n", encoding="utf-8")
    rows = snapshot(tmp_project)
    html = render_html(rows, tmp_project)
    assert "<table" in html
    assert "ch-01.md" in html


def test_main_once(tmp_project):
    (tmp_project / "chapters" / "ch-01.md").write_text("# T\n", encoding="utf-8")
    rc = main([str(tmp_project), "--once"])
    assert rc == 0
