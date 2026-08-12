"""Tests for install_amiri.py -- Amiri font download + install.

Verifies:
  * Idempotent skip when the target dir already has a TTF/OTF.
  * Network failure (urlopen URLError) surfaces as exit 3.
"""
import sys
from pathlib import Path
from urllib.error import URLError

import pytest

import install_amiri as ia_mod


# ---------------------------------------------------------------------------
# 1) Idempotent skip when target dir already has Amiri
# ---------------------------------------------------------------------------


def test_idempotent_skip_when_target_dir_has_amiri(tmp_path, capsys):
    """When --target-dir already has a .ttf and --force is absent,
    run_install prints 'already installed' and exits 0.
    """
    target = tmp_path / "amiri_target"
    target.mkdir(parents=True)
    (target / "Amiri-Regular.ttf").write_bytes(b"FAKE-Ttf")

    rc = ia_mod.run_install(
        force=False,
        verify_only=False,
        target_arg=str(target),
    )
    captured = capsys.readouterr()
    assert rc == 0, "expected exit 0 when font is already installed"
    assert "already installed" in captured.out


def test_idempotent_skip_with_force_proceeds_to_network(
    tmp_path, monkeypatch, capsys
):
    """With --force, the script does NOT short-circuit on the existing
    font and instead proceeds to the network step. We patch the network
    call to raise so the test stays offline.
    """
    target = tmp_path / "amiri_target"
    target.mkdir(parents=True)
    (target / "Amiri-Regular.ttf").write_bytes(b"FAKE-Ttf")

    def boom(*args, **kwargs):
        raise URLError("simulated network failure")

    monkeypatch.setattr(ia_mod, "urlopen", boom)

    rc = ia_mod.run_install(
        force=True,
        verify_only=False,
        target_arg=str(target),
    )
    captured = capsys.readouterr()
    assert rc == 3, "expected exit 3 on simulated network failure"
    assert "network" in captured.err.lower() or "cannot" in captured.err.lower()


# ---------------------------------------------------------------------------
# 2) Network failure -> exit 3
# ---------------------------------------------------------------------------


def test_exits_3_on_network_failure(monkeypatch, capsys):
    """Patch urlopen to raise URLError; the script must exit 3."""
    def boom(*args, **kwargs):
        raise URLError("simulated network failure")

    monkeypatch.setattr(ia_mod, "urlopen", boom)

    rc = ia_mod.run_install(
        force=True,
        verify_only=False,
        target_arg=None,  # use default; we never get past the API call
    )
    captured = capsys.readouterr()
    assert rc == 3
    assert "cannot" in captured.err.lower() or "network" in captured.err.lower()


def test_exits_3_when_github_api_returns_404(monkeypatch, capsys):
    """HTTPError also maps to exit 3."""
    from urllib.error import HTTPError
    def boom(*args, **kwargs):
        raise HTTPError(
            "https://api.github.com/...", 404, "Not Found", {}, None,
        )

    monkeypatch.setattr(ia_mod, "urlopen", boom)

    rc = ia_mod.run_install(
        force=True,
        verify_only=False,
        target_arg=None,
    )
    captured = capsys.readouterr()
    assert rc == 3
    assert "cannot" in captured.err.lower() or "github" in captured.err.lower()


# ---------------------------------------------------------------------------
# 3) --verify path
# ---------------------------------------------------------------------------


def test_verify_exits_0_when_installed(tmp_path, capsys):
    """--verify exits 0 when the target dir has Amiri."""
    target = tmp_path / "amiri_verify"
    target.mkdir(parents=True)
    (target / "Amiri-Bold.ttf").write_bytes(b"FAKE")

    rc = ia_mod.run_install(
        force=False,
        verify_only=True,
        target_arg=str(target),
    )
    captured = capsys.readouterr()
    assert rc == 0
    assert "installed" in captured.out
