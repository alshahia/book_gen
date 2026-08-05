"""Tests for bilingual_smoke.py — URL/bold/H2 diff between chapter and source."""
from pathlib import Path

from bilingual_smoke import (
    check_chapter,
    main,
    parse_source_map,
)


def test_self_check_passes():
    import subprocess
    import sys
    r = subprocess.run(
        [sys.executable, str(Path(__file__).parent.parent / "book_workflow" / "scripts" / "bilingual_smoke.py"), "--self-check"],
        capture_output=True, text=True, timeout=30,
    )
    assert r.returncode == 0, r.stderr
    assert "self-check OK" in r.stdout


def test_parse_source_map_basic(tmp_project):
    smap = parse_source_map(tmp_project / "source-map.md")
    assert smap == {"ch-01.md": "ch-01.txt"}


def test_parse_source_map_missing(tmp_project):
    (tmp_project / "source-map.md").unlink()
    smap = parse_source_map(tmp_project / "source-map.md")
    assert smap == {}


def test_check_chapter_urls_match(chapter_with_url):
    chap = chapter_with_url / "chapters" / "ch-01.md"
    src = chapter_with_url / "source" / "ch-01.txt"
    out = check_chapter(chap, src)
    assert out["urls"]["missing"] == []
    assert out["urls"]["rewritten"] == []
    assert out["urls"]["source_truncated"] == []


def test_check_chapter_missing_url(tmp_project):
    (tmp_project / "chapters" / "ch-01.md").write_text(
        "# Title\n\n## Reference\nno url here\n", encoding="utf-8",
    )
    (tmp_project / "source" / "ch-01.txt").write_text(
        "## Reference\nhttps://example.com/missing\n", encoding="utf-8",
    )
    out = check_chapter(tmp_project / "chapters" / "ch-01.md", tmp_project / "source" / "ch-01.txt")
    assert "https://example.com/missing" in out["urls"]["missing"]


def test_check_chapter_h2_diff(tmp_project):
    (tmp_project / "chapters" / "ch-01.md").write_text(
        "# Title\n\n## Overview\nbody\n\n## Reference\n\n## Extra\nbody\n",
        encoding="utf-8",
    )
    (tmp_project / "source" / "ch-01.txt").write_text(
        "## Overview\nbody\n\n## Reference\n\n## Method\nbody\n",
        encoding="utf-8",
    )
    out = check_chapter(tmp_project / "chapters" / "ch-01.md", tmp_project / "source" / "ch-01.txt")
    assert "Method" in out["h2"]["missing_in_chapter"]
    assert "Extra" in out["h2"]["extra_in_chapter"]


def test_main_writes_json(tmp_project):
    (tmp_project / "chapters" / "ch-01.md").write_text(
        "# Title\n\n## Reference\nhttps://example.com/a\n", encoding="utf-8",
    )
    (tmp_project / "source" / "ch-01.txt").write_text(
        "## Reference\nhttps://example.com/a\n", encoding="utf-8",
    )
    out_path = tmp_project / "report.json"
    rc = main([str(tmp_project), "--out", str(out_path)])
    assert rc == 0
    import json
    data = json.loads(out_path.read_text(encoding="utf-8"))
    assert data["summary"]["chapters_compared"] == 1
    assert data["summary"]["urls_missing"] == 0
