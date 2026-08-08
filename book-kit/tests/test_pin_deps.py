"""Tests for pin_deps.py -- P14 dependency pinner.

The ``uv`` binary IS available in this dev env (0.7.18 verified), so the
end-to-end tests invoke the real subprocess call against a tiny
``requirements.txt`` / ``pyproject.toml`` fixture. The fixture deps
(`pyyaml`, `requests`) are small + widely cached + pinned in the
generated ``uv.lock``, which is the only artifact we assert on. When uv
is missing or the network is offline, the script degrades to
``uv_missing`` status and :func:`test_uv_missing_path` covers that.

The tests follow the project convention: file-based fixtures under
``tmp_path``, library entry-point calls (``run_pin``), and assertions on
the produced files + status row.
"""
from pathlib import Path

import pytest

import pin_deps as pd


def _book(tmp_path):
    """Create a minimal book root with ``chapters/code/`` pre-created."""
    root = tmp_path / "mybook"
    (root / "chapters" / "code").mkdir(parents=True)
    return root


# ---------------------------------------------------------------------------
# 1) requirements.txt chapter -> uv.lock + status row
# ---------------------------------------------------------------------------

def test_requirements_txt_chapter_pins(tmp_path):
    """A chapter with ``requirements.txt`` produces ``uv.lock`` and a
    ``pinned`` row in the status file. The status file's basename
    matches the spec (``CH-DEP-STATUS.md``).
    """
    root = _book(tmp_path)
    ch_dir = root / "chapters" / "code" / "ch-07"
    ch_dir.mkdir(parents=True)
    (ch_dir / "requirements.txt").write_text("pyyaml\n", encoding="utf-8")

    rc = pd.run_pin(root, "chapters/code")
    assert rc == 0, "run_pin must exit 0 on a successful pin"

    assert (ch_dir / "uv.lock").exists(), "uv.lock must land next to the input"
    text = (root / "chapters" / "code" / "CH-DEP-STATUS.md").read_text(
        encoding="utf-8")
    assert "ch-07" in text, "chapter label missing from status file"
    assert "pinned" in text, "status row should report lock_status=pinned"


# ---------------------------------------------------------------------------
# 2) pyproject.toml chapter -> uv.lock + status row
# ---------------------------------------------------------------------------

def test_pyproject_toml_chapter_pins(tmp_path):
    """A chapter with ``pyproject.toml`` produces ``uv.lock`` and a
    ``pinned`` row. The dependency count must be > 0 (pyyaml pulls
    itself in for a single-deps project).
    """
    root = _book(tmp_path)
    ch_dir = root / "chapters" / "code" / "ch-03"
    ch_dir.mkdir(parents=True)
    (ch_dir / "pyproject.toml").write_text(
        '[project]\nname = "x"\nversion = "0.1"\n'
        'dependencies = ["pyyaml"]\n',
        encoding="utf-8",
    )

    rc = pd.run_pin(root, "chapters/code")
    assert rc == 0

    assert (ch_dir / "uv.lock").exists()
    lock_text = (ch_dir / "uv.lock").read_text(encoding="utf-8")
    assert "pyyaml==" in lock_text, "uv.lock should pin pyyaml"

    text = (root / "chapters" / "code" / "CH-DEP-STATUS.md").read_text(
        encoding="utf-8")
    assert "ch-03" in text
    assert "pinned" in text


# ---------------------------------------------------------------------------
# 3) pyproject.toml wins over requirements.txt when both are present
# ---------------------------------------------------------------------------

def test_pyproject_wins_over_requirements(tmp_path):
    """When both inputs exist, ``pyproject.toml`` wins. The lock file
    produced must reflect pyproject's dependency (``pyyaml``) and not
    the requirements.txt's distinct dependency (``requests``).

    Verifies the precedence rule documented in :func:`_find_input`.
    """
    root = _book(tmp_path)
    ch_dir = root / "chapters" / "code" / "ch-05"
    ch_dir.mkdir(parents=True)
    (ch_dir / "pyproject.toml").write_text(
        '[project]\nname = "y"\nversion = "0.1"\n'
        'dependencies = ["pyyaml"]\n',
        encoding="utf-8",
    )
    (ch_dir / "requirements.txt").write_text("requests\n", encoding="utf-8")

    rc = pd.run_pin(root, "chapters/code")
    assert rc == 0

    lock_text = (ch_dir / "uv.lock").read_text(encoding="utf-8")
    assert "pyyaml==" in lock_text, "pyproject dep must appear in lock"
    # requests WOULD show up transitively if requests were the root
    # (it pulls urllib3, idna, etc.) -- but with pyyaml as the only root
    # the lock lists pyyaml and nothing else.
    assert "requests==" not in lock_text, (
        "requirements.txt dep must NOT appear when pyproject.toml wins"
    )


# ---------------------------------------------------------------------------
# 4) Empty chapters/code/ -> empty status table, exit 0
# ---------------------------------------------------------------------------

def test_empty_code_dir_writes_empty_status(tmp_path):
    """With no chapter subdirectories, the status file is written with
    a placeholder row and the script exits 0 (graceful fall-through).
    """
    root = _book(tmp_path)

    rc = pd.run_pin(root, "chapters/code")
    assert rc == 0, "empty code dir must not fail"

    status = root / "chapters" / "code" / "CH-DEP-STATUS.md"
    assert status.exists()
    text = status.read_text(encoding="utf-8")
    assert "Chapter dependency status" in text
    assert "| -- | -- | -- |" in text, (
        "empty state should render a single placeholder row"
    )


# ---------------------------------------------------------------------------
# 5) path validation: resolve_under refuses .. and absolute escapes
# ---------------------------------------------------------------------------

def test_resolve_under_rejects_parent_traversal(tmp_path):
    """resolve_under must reject any ``..`` component."""
    root = tmp_path / "book"
    with pytest.raises(pd.PinDepsError) as exc:
        pd.resolve_under(root, "../outside", "--code-dir")
    assert "must not contain '..'" in str(exc.value)


def test_resolve_under_rejects_absolute_escape(tmp_path):
    """An absolute path that does not live under ``root`` is refused."""
    root = tmp_path / "book"
    with pytest.raises(pd.PinDepsError) as exc:
        pd.resolve_under(root, tmp_path / "sibling", "--code-dir")
    assert "must resolve under" in str(exc.value)


def test_path_validation_via_run_pin(tmp_path):
    """End-to-end: ``--code-dir`` with ``..`` exits 2 (input error)."""
    root = _book(tmp_path)
    rc = pd.run_pin(root, "../sibling-code")
    assert rc == 2, "escaping code-dir must end with exit 2"


# ---------------------------------------------------------------------------
# 6) uv missing: chapters degrade to uv_missing status, no crash
# ---------------------------------------------------------------------------

def test_uv_missing_path(monkeypatch, tmp_path, capsys):
    """When ``uv`` is not on PATH, every chapter with a dep file gets
    ``uv_missing`` status. The script does NOT crash -- the surfaced
    state is the missing binary.
    """
    monkeypatch.setattr(pd.shutil, "which", lambda _: None)

    root = _book(tmp_path)
    ch_dir = root / "chapters" / "code" / "ch-09"
    ch_dir.mkdir(parents=True)
    (ch_dir / "requirements.txt").write_text("pyyaml\n", encoding="utf-8")

    rc = pd.run_pin(root, "chapters/code")
    assert rc == 0, "missing uv is a status, not a script error"

    text = (root / "chapters" / "code" / "CH-DEP-STATUS.md").read_text(
        encoding="utf-8")
    assert "ch-09" in text
    assert "uv_missing" in text, (
        "missing uv must surface as lock_status=uv_missing, not pinned"
    )
    # stderr should mention the install hint so a human can act on it.
    captured = capsys.readouterr()
    assert "uv not on PATH" in captured.err or "uv missing" in captured.err, (
        f"stderr must surface the uv-missing hint; got: {captured.err!r}"
    )


# ---------------------------------------------------------------------------
# 7) Status table format matches the spec's per-row shape
# ---------------------------------------------------------------------------

def test_status_table_row_format(tmp_path):
    """Rendered table header + a single row exercise the exact column
    shape: ``| Chapter | Packages | Lock status |`` and one data row.
    """
    rows = [("ch-07", 12, "pinned")]
    text = pd.render_status_table(rows)
    lines = text.splitlines()
    # Lines: 0 = "# Chapter dependency status", 1 = "", 2 = header,
    # 3 = separator, 4 = data row, 5 = "".
    assert lines[2] == "| Chapter | Packages | Lock status |"
    assert lines[3] == "| --- | --- | --- |"
    assert lines[4].startswith("| ch-07 | 12 | pinned |")