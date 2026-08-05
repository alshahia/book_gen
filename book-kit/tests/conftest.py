"""Pytest fixtures shared across book-kit tests."""
import sys
from pathlib import Path

import pytest

# Make the scripts importable.
KIT_ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = KIT_ROOT / "book_workflow" / "scripts"
sys.path.insert(0, str(SCRIPTS))


@pytest.fixture
def tmp_project(tmp_path):
    """A minimal book project layout: chapters/, source/, source-map.md."""
    (tmp_path / "chapters").mkdir()
    (tmp_path / "source").mkdir()
    (tmp_path / "source-map.md").write_text(
        "| ch-01.md | ch-01.txt | 100 | 1000 | no |\n",
        encoding="utf-8",
    )
    return tmp_path


@pytest.fixture
def chapter_with_url(tmp_project):
    """A chapter that has a single URL the source also has."""
    (tmp_project / "chapters" / "ch-01.md").write_text(
        "# Title\n\n## Overview\nbody text\n\n## Reference\n"
        "https://example.com/a\n",
        encoding="utf-8",
    )
    (tmp_project / "source" / "ch-01.txt").write_text(
        "## Overview\nbody text\n\n## Reference\nhttps://example.com/a\n",
        encoding="utf-8",
    )
    return tmp_project
