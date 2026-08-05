"""pytest tests for md2pdf.py — RTL Arabic PDF builder.

Covers: --self-check, figure-insertion edge cases (already in self-check),
plus additional negative cases (empty manifest, manifest < placeholders, etc.).
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "book_workflow" / "scripts"))
import md2pdf  # noqa: E402


def test_self_check_passes():
    """The script's --self-check entrypoint must exit cleanly."""
    import subprocess
    r = subprocess.run(
        [sys.executable, str(Path(md2pdf.__file__)), "--self-check"],
        capture_output=True, text=True,
    )
    assert r.returncode == 0, f"self-check failed: {r.stderr}"
    assert "md2pdf self-check OK" in r.stdout


def test_insert_figures_basic():
    """Two placeholders, two figures → both embedded."""
    sample = "# T\n\n> **الشكل 1:** A\n\n> **الشكل 2:** B\n\nend.\n"
    figs = [{"path": "f1.png"}, {"path": "f2.png"}]
    out = md2pdf._insert_figures(sample, figs, Path("."))
    assert "f1.png" in out
    assert "f2.png" in out
    assert out.count("![") == 2


def test_insert_figures_underflow():
    """More placeholders than figures → remaining placeholders kept verbatim."""
    sample = "# T\n\n> **الشكل 1:** A\n\n> **الشكل 2:** B\n\n> **الشكل 3:** C\n"
    figs = [{"path": "f1.png"}]
    out = md2pdf._insert_figures(sample, figs, Path("."))
    assert out.count("![") == 1
    assert "**الشكل 2:**" in out
    assert "**الشكل 3:**" in out


def test_insert_figures_overflow():
    """More figures than placeholders → extras ignored (no exception)."""
    sample = "# T\n\n> **الشكل 1:** A\n"
    figs = [{"path": "f1.png"}, {"path": "f2.png"}, {"path": "f3.png"}]
    out = md2pdf._insert_figures(sample, figs, Path("."))
    assert out.count("![") == 1
    assert "f1.png" in out
    assert "f2.png" not in out  # extras dropped


def test_insert_figures_empty():
    """No placeholders → unchanged."""
    sample = "# T\n\nno figures here\n"
    figs = [{"path": "f1.png"}]
    out = md2pdf._insert_figures(sample, figs, Path("."))
    assert out == sample
    assert out.count("![") == 0


def test_figure_placeholder_regex():
    """The regex matches `> **الشكل N:**` at line start."""
    import re
    rx = md2pdf.FIGURE_PLACEHOLDER
    assert rx.search("> **الشكل 1:** caption")
    assert rx.search("> **الشكل 99:** caption")
    assert not rx.search("**الشكل 1:** caption")  # missing `>` marker
    assert not rx.search("> الشكل 1: caption")    # missing `**`


def test_default_css_has_rtl():
    """The bundled default CSS must declare `direction: rtl` for body."""
    css = md2pdf.DEFAULT_CSS
    assert "direction: rtl" in css
    assert "html dir=" not in css  # direction lives on body, not html (html is set in template)


def test_chrome_finder_handles_empty_env(tmp_path, monkeypatch):
    """When CHROME_PATH is empty and no candidate exists, raise SystemExit(1)."""
    monkeypatch.setattr(md2pdf, "CHROME_CANDIDATES", ["", ""])  # both empty
    # The function raises SystemExit on missing chrome
    import pytest
    with pytest.raises(SystemExit):
        md2pdf.find_chrome()
