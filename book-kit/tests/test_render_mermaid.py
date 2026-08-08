"""Tests for render_mermaid.py mermaid figure rendering.

The mmdc binary is not installed in CI, so every rendering test patches
``render_mermaid.run_mmdc`` (or ``subprocess.run``) to write a stub PNG.
That keeps the suite green on hosts without mermaid-cli while still
exercising the manifest, the chapters-rendered mirror and the path guards.
"""
from pathlib import Path

import json

import pytest

import render_mermaid as rm


TWO_BLOCK_CHAPTER = """# Chapter One

## Flow

```mermaid
graph TD
  A --> B
```

Some prose between the diagrams.

## Sequence

```mermaid
%% caption: Login handshake
sequenceDiagram
  A->>B: hello
```

Closing prose.
"""


def _book(tmp_path, chapters):
    """Create a book root with the given {name: text} chapters."""
    root = tmp_path / "mybook"
    (root / "chapters").mkdir(parents=True)
    for name, text in chapters.items():
        (root / "chapters" / name).write_text(text, encoding="utf-8")
    return root


@pytest.fixture
def fake_mmdc(monkeypatch):
    """Patch run_mmdc to write a stub PNG and record every invocation."""
    calls = []

    def _fake(mmdc_path, mmd_path, png_path):
        calls.append((mmdc_path, Path(mmd_path), Path(png_path)))
        Path(png_path).write_bytes(b"\x89PNG stub")

    monkeypatch.setattr(rm, "run_mmdc", _fake)
    return calls


def test_two_blocks_produce_two_pngs_and_manifest(tmp_path, fake_mmdc):
    """Spec case: 1 fixture chapter with 2 mermaid blocks -> 2 PNGs + manifest."""
    root = _book(tmp_path, {"ch-01.md": TWO_BLOCK_CHAPTER})

    records = rm.render_book(root, mmdc_path="mmdc")

    assert len(records) == 2
    assert len(fake_mmdc) == 2

    pngs = sorted((root / "figures").glob("*.png"))
    assert [p.name for p in pngs] == [
        "mybook-ch-01-mermaid-1.png",
        "mybook-ch-01-mermaid-2.png",
    ]
    mmds = sorted((root / "figures").glob("*.mmd"))
    assert len(mmds) == 2
    assert "graph TD" in mmds[0].read_text(encoding="utf-8")

    manifest = json.loads(
        (root / "figures" / "mermaid-manifest.json").read_text(encoding="utf-8")
    )
    assert [r["chapter"] for r in manifest] == ["ch-01.md", "ch-01.md"]
    assert [r["index"] for r in manifest] == [1, 2]
    assert manifest[0]["png_path"] == "figures/mybook-ch-01-mermaid-1.png"
    assert all(len(r["source_hash"]) == 64 for r in manifest)
    assert manifest[0]["source_hash"] != manifest[1]["source_hash"]

    mirrored = (root / "chapters-rendered" / "ch-01.md").read_text(
        encoding="utf-8"
    )
    assert "```mermaid" not in mirrored
    assert "![Flow](../figures/mybook-ch-01-mermaid-1.png)" in mirrored
    assert (
        "![Login handshake](../figures/mybook-ch-01-mermaid-2.png)" in mirrored
    )
    assert "Some prose between the diagrams." in mirrored

    # The source chapter is never mutated.
    assert (root / "chapters" / "ch-01.md").read_text(
        encoding="utf-8"
    ) == TWO_BLOCK_CHAPTER


def test_zero_blocks_yields_empty_manifest(tmp_path, fake_mmdc):
    """A chapter with no mermaid blocks renders nothing and still succeeds."""
    root = _book(
        tmp_path, {"ch-01.md": "# Plain\n\nNo diagrams here.\n\n```py\nx=1\n```\n"}
    )

    records = rm.render_book(root, mmdc_path="mmdc")

    assert records == []
    assert fake_mmdc == []
    assert list((root / "figures").glob("*.png")) == []
    manifest = json.loads(
        (root / "figures" / "mermaid-manifest.json").read_text(encoding="utf-8")
    )
    assert manifest == []
    # The mirror is still produced, byte-identical to the source.
    assert (root / "chapters-rendered" / "ch-01.md").read_text(
        encoding="utf-8"
    ) == (root / "chapters" / "ch-01.md").read_text(encoding="utf-8")


def test_malformed_block_errors_without_crashing(tmp_path, fake_mmdc):
    """An unterminated fence raises MermaidError, not an unhandled exception."""
    root = _book(
        tmp_path,
        {"ch-01.md": "# Broken\n\n```mermaid\ngraph TD\n  A --> B\n"},
    )

    with pytest.raises(rm.MermaidError) as excinfo:
        rm.render_book(root, mmdc_path="mmdc")

    assert "unterminated mermaid block" in str(excinfo.value)
    # Nothing was written: parsing fails before any figure or mirror lands.
    assert not (root / "figures").exists()
    assert not (root / "chapters-rendered").exists()


def test_cli_malformed_block_exits_2(tmp_path, monkeypatch, fake_mmdc):
    """The CLI turns a malformed block into exit 2 with a stderr message."""
    root = _book(
        tmp_path,
        {"ch-01.md": "# Broken\n\n```mermaid\ngraph TD\n"},
    )
    monkeypatch.setattr(rm.shutil, "which", lambda name: "mmdc")

    rc = rm.main(["--book", str(root)])

    assert rc == 2


def test_missing_mmdc_with_blocks_exits_3(tmp_path, monkeypatch):
    """No mmdc + work to do -> exit 3 and an actionable install hint."""
    root = _book(tmp_path, {"ch-01.md": TWO_BLOCK_CHAPTER})
    monkeypatch.setattr(rm.shutil, "which", lambda name: None)

    rc = rm.main(["--book", str(root)])

    assert rc == 3
    assert not (root / "figures").exists()


def test_missing_mmdc_without_blocks_exits_0(tmp_path, monkeypatch):
    """No mmdc but no diagrams either -> the pre-PDF step must not break."""
    root = _book(tmp_path, {"ch-01.md": "# Plain\n\nNo diagrams.\n"})
    monkeypatch.setattr(rm.shutil, "which", lambda name: None)

    rc = rm.main(["--book", str(root)])

    assert rc == 0
    manifest = json.loads(
        (root / "figures" / "mermaid-manifest.json").read_text(encoding="utf-8")
    )
    assert manifest == []


@pytest.mark.parametrize(
    "flag,value",
    [
        ("--figures-dir", "../escape"),
        ("--out", "../../elsewhere"),
        ("--manifest", "../manifest.json"),
    ],
)
def test_path_guard_rejects_traversal(tmp_path, monkeypatch, flag, value):
    """`..` traversal in any writable path is refused with exit 2."""
    root = _book(tmp_path, {"ch-01.md": TWO_BLOCK_CHAPTER})
    monkeypatch.setattr(rm.shutil, "which", lambda name: "mmdc")

    rc = rm.main(["--book", str(root), flag, value])

    assert rc == 2


def test_path_guard_rejects_absolute_outside_book(tmp_path):
    """An absolute path outside the book root is refused."""
    root = _book(tmp_path, {"ch-01.md": TWO_BLOCK_CHAPTER})
    outside = tmp_path / "outside"

    with pytest.raises(rm.MermaidError) as excinfo:
        rm.render_book(root, figures_dir=str(outside), mmdc_path="mmdc")

    assert "must resolve under the book root" in str(excinfo.value)


def test_path_guard_allows_absolute_inside_book(tmp_path, fake_mmdc):
    """An absolute path that stays under the book root is accepted."""
    root = _book(tmp_path, {"ch-01.md": TWO_BLOCK_CHAPTER})
    inside = root / "figures"

    records = rm.render_book(root, figures_dir=str(inside), mmdc_path="mmdc")

    assert len(records) == 2


def test_manifest_is_stable_across_reruns(tmp_path, fake_mmdc):
    """Re-running with unchanged input produces a byte-identical manifest."""
    root = _book(
        tmp_path,
        {"ch-02.md": TWO_BLOCK_CHAPTER, "ch-01.md": TWO_BLOCK_CHAPTER},
    )
    manifest_path = root / "figures" / "mermaid-manifest.json"

    rm.render_book(root, mmdc_path="mmdc")
    first = manifest_path.read_bytes()
    rm.render_book(root, mmdc_path="mmdc")
    second = manifest_path.read_bytes()

    assert first == second
    records = json.loads(first.decode("utf-8"))
    # Sorted by (chapter, index) regardless of filesystem iteration order.
    assert [(r["chapter"], r["index"]) for r in records] == [
        ("ch-01.md", 1),
        ("ch-01.md", 2),
        ("ch-02.md", 1),
        ("ch-02.md", 2),
    ]


def test_run_mmdc_uses_array_form_not_shell(tmp_path, monkeypatch):
    """The subprocess call is array-form with the spec'd flags, no shell=True."""
    seen = {}

    class _Completed:
        returncode = 0

    def _fake_run(cmd, **kwargs):
        seen["cmd"] = cmd
        seen["kwargs"] = kwargs
        return _Completed()

    monkeypatch.setattr(rm.subprocess, "run", _fake_run)

    rm.run_mmdc("mmdc", tmp_path / "a.mmd", tmp_path / "a.png")

    assert seen["cmd"][0] == "mmdc"
    assert seen["cmd"][1] == "-i"
    assert seen["cmd"][3] == "-o"
    assert seen["cmd"][5:] == ["-b", "transparent"]
    assert seen["kwargs"]["check"] is True
    assert seen["kwargs"]["capture_output"] is True
    assert "shell" not in seen["kwargs"]


def test_mmdc_failure_surfaces_stderr(tmp_path, monkeypatch):
    """A non-zero mmdc exit is reported with its captured stderr."""
    import subprocess as sp

    def _fake_run(cmd, **kwargs):
        raise sp.CalledProcessError(1, cmd, output=b"", stderr=b"bad syntax")

    monkeypatch.setattr(rm.subprocess, "run", _fake_run)

    with pytest.raises(rm.MermaidError) as excinfo:
        rm.run_mmdc("mmdc", tmp_path / "a.mmd", tmp_path / "a.png")

    assert "bad syntax" in str(excinfo.value)


def test_caption_falls_back_to_figure_number(tmp_path, fake_mmdc):
    """No caption directive and no preceding heading -> 'Figure N'."""
    root = _book(tmp_path, {"ch-01.md": "```mermaid\ngraph TD\n  A-->B\n```\n"})

    rm.render_book(root, mmdc_path="mmdc")

    mirrored = (root / "chapters-rendered" / "ch-01.md").read_text(
        encoding="utf-8"
    )
    assert "![Figure 1](../figures/mybook-ch-01-mermaid-1.png)" in mirrored


def test_slug_override_changes_figure_names(tmp_path, fake_mmdc):
    """--slug controls the figure filename prefix."""
    root = _book(tmp_path, {"ch-01.md": TWO_BLOCK_CHAPTER})

    records = rm.render_book(root, slug="daily-focus", mmdc_path="mmdc")

    assert records[0]["png_path"] == "figures/daily-focus-ch-01-mermaid-1.png"
    assert (root / "figures" / "daily-focus-ch-01-mermaid-1.png").is_file()


def test_missing_book_root_errors(tmp_path):
    """A nonexistent --book is an input error, not a traceback."""
    with pytest.raises(rm.MermaidError):
        rm.render_book(tmp_path / "nope", mmdc_path="mmdc")
