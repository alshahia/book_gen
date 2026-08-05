"""Tests for split_source.py — chunked-write protocol part sizer."""
from pathlib import Path

from split_source import main, plan_parts, split_at_h2


def test_self_check_passes():
    import subprocess
    import sys
    r = subprocess.run(
        [sys.executable, str(Path(__file__).parent.parent / "book_workflow" / "scripts" / "split_source.py"), "--self-check"],
        capture_output=True, text=True, timeout=30,
    )
    assert r.returncode == 0, r.stderr
    assert "self-check OK" in r.stdout


def test_plan_parts_small():
    n, target = plan_parts(10_000)
    assert n == 1


def test_plan_parts_medium():
    n, target = plan_parts(35_000)
    assert n == 2


def test_plan_parts_large():
    n, target = plan_parts(60_000)
    assert n >= 3
    assert target == 18_000


def test_split_at_h2_basic():
    text = "## A\n\naaa\n\n## B\n\nbbb\n\n## C\n\nccc\n\n## D\n\nddd\n"
    parts = split_at_h2(text, 2)
    assert len(parts) == 2
    assert "## A" in parts[0]
    assert "## D" in parts[1]


def test_split_at_h2_falls_back_to_paragraph_when_too_few_h2():
    text = "intro paragraph one\n\nsecond paragraph\n\nthird\n"
    parts = split_at_h2(text, 3)
    assert len(parts) >= 1


def test_main_writes_manifest(tmp_path):
    src = tmp_path / "big.txt"
    content = "## Section A\n\n" + ("lorem ipsum " * 1500) + "\n\n## Section B\n\n" + ("dolor sit " * 1500)
    src.write_text(content, encoding="utf-8")
    rc = main([str(src), "--out", str(tmp_path), "--prefix", "big"])
    assert rc == 0
    manifest = tmp_path / "big-manifest.json"
    assert manifest.exists()
    import json
    data = json.loads(manifest.read_text(encoding="utf-8"))
    assert data["n_parts"] >= 2
    assert any("big-part-1.txt" in p["path"] for p in data["parts"])
