"""Tests for extract_figures.py — pdfimages wrapper (with mocked subprocess)."""
from pathlib import Path
from unittest.mock import patch

from extract_figures import main, pdfimages_list


PDFIMAGES_LIST_OUTPUT = """page   num  type   width height color comp bpc  enc interp  object ID x-ppi y-ppi size ratio
--------------------------------------------------------------------------------------------
   1     0 image    640   480  rgb     3   8  jpeg   no       12  0   300   300  120K 6.7%
   2     0 image    800   600  rgb     3   8  jpeg   no       18  0   300   300  200K 6.7%
   3     0 image    320   240  rgb     3   8  jpeg   no       24  0   150   150   30K 6.7%
"""


def test_self_check_passes():
    import subprocess
    import sys
    r = subprocess.run(
        [sys.executable, str(Path(__file__).parent.parent / "book_workflow" / "scripts" / "extract_figures.py"), "--self-check"],
        capture_output=True, text=True, timeout=30,
    )
    assert r.returncode == 0, r.stderr
    assert "self-check OK" in r.stdout


def test_pdfimages_list_parses():
    fake = subprocess_completed(stdout=PDFIMAGES_LIST_OUTPUT, returncode=0, stderr="")
    with patch("extract_figures.subprocess.run", return_value=fake):
        rows = pdfimages_list(Path("dummy.pdf"))
    assert len(rows) == 3
    assert rows[0]["page"] == 1
    assert rows[0]["width"] == 640
    assert rows[0]["height"] == 480
    assert rows[2]["page"] == 3


def test_main_with_mocked_no_images(tmp_path):
    """No images → empty manifest is written (chapter pipeline can see 'no figures')."""
    fake = subprocess_completed(stdout=PDFIMAGES_LIST_OUTPUT.replace(PDFIMAGES_LIST_OUTPUT, ""), returncode=0, stderr="")
    pdf = tmp_path / "no_imgs.pdf"
    pdf.write_bytes(b"%PDF-1.4\n")
    with patch("extract_figures.subprocess.run", return_value=fake):
        rc = main([str(pdf), "--out", str(tmp_path), "--slug", "no-imgs"])
    assert rc == 0
    manifest = tmp_path / "no-imgs-manifest.json"
    assert manifest.exists()
    import json
    data = json.loads(manifest.read_text(encoding="utf-8"))
    assert data["figures"] == []


def test_main_with_mocked_images(tmp_path):
    """Images present → manifest entries reference PNG paths."""
    fake_list = subprocess_completed(stdout=PDFIMAGES_LIST_OUTPUT, returncode=0, stderr="")
    fake_dump = subprocess_completed(stdout="", returncode=0, stderr="")

    pdf = tmp_path / "ch.pdf"
    pdf.write_bytes(b"%PDF-1.4\n")

    def fake_run(cmd, **kwargs):
        if "-list" in cmd:
            return fake_list
        if "-png" in cmd:
            prefix = cmd[-1]
            # Create the PNG files pdfimages would have written
            for i in range(3):
                (tmp_path / f"{Path(prefix).name}-{i+1}-{0}.png").write_bytes(b"\x89PNG")
            return fake_dump
        return fake_list

    with patch("extract_figures.subprocess.run", side_effect=fake_run):
        rc = main([str(pdf), "--out", str(tmp_path), "--slug", "ch"])
    assert rc == 0
    import json
    manifest = json.loads((tmp_path / "ch-manifest.json").read_text(encoding="utf-8"))
    assert len(manifest["figures"]) == 3
    assert manifest["figures"][0]["page"] == 1


# ---- helpers ----

import subprocess as _subprocess
def subprocess_completed(*, stdout, returncode, stderr=""):
    """Build a fake CompletedProcess for monkey-patching."""
    return _subprocess.CompletedProcess(args=[], returncode=returncode, stdout=stdout, stderr=stderr)
