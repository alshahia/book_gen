"""Tests for index_reports.py report index generation."""
from pathlib import Path

import index_reports as ir


def _write_report(reports_dir: Path, name: str, body: str) -> Path:
    path = reports_dir / name
    path.write_text(body, encoding="utf-8")
    return path


def test_index_good(tmp_path):
    _write_report(
        tmp_path,
        "02_plan_T-2026-08-03-001.md",
        "# Plan\n\nNo status marker.\n",
    )
    _write_report(
        tmp_path,
        "04_review_T-2026-08-02-001.md",
        "# Review\n\n```verdict\nPASS\n```\n",
    )
    _write_report(
        tmp_path,
        "04_review_T-2026-08-01-001.md",
        "# Review\n\n[auto-accepted triageable]\n",
    )
    _write_report(
        tmp_path,
        "05_ship_release.md",
        "# Ship\n\nDate: 2026-07-31\nVerdict: APPROVED\n",
    )
    _write_report(
        tmp_path,
        "06_health_undated.md",
        "| Check | Status |\n|---|---|\n| suite | FAIL |\n",
    )

    expected = (
        "| Phase | File | Date | Status |\n"
        "|---|---|---|---|\n"
        "| 02 plan | 02_plan_T-2026-08-03-001.md | 2026-08-03 | — |\n"
        "| 04 review | 04_review_T-2026-08-02-001.md | 2026-08-02 | PASS |\n"
        "| 04 review | 04_review_T-2026-08-01-001.md | 2026-08-01 | PASS_WITH_WARN |\n"
        "| 05 ship | 05_ship_release.md | 2026-07-31 | APPROVED |\n"
        "| 06 health | 06_health_undated.md | — | FAIL |\n"
    )
    assert ir.render_index(tmp_path) == expected


def test_index_missing(tmp_path):
    assert ir.render_index(tmp_path) == (
        "| Phase | File | Date | Status |\n"
        "|---|---|---|---|\n"
        "No reports found\n"
    )


def test_index_malformed(tmp_path):
    _write_report(
        tmp_path,
        "04_review_T-2026-08-04-001.md",
        "Verdict: PASS\n",
    )
    _write_report(tmp_path, "review_bad.md", "Verdict: FAIL\n")

    index = ir.render_index(tmp_path)
    assert "04_review_T-2026-08-04-001.md" in index
    assert "review_bad.md" not in index


def test_index_regen_idempotent(tmp_path):
    _write_report(
        tmp_path,
        "04_review_T-2026-08-05-001.md",
        "```verdict\nREADY_FOR_REVIEW\n```\n",
    )

    assert ir.main(["--regen", "--reports-dir", str(tmp_path)]) == 0
    first = (tmp_path / "INDEX.md").read_bytes()
    assert ir.main(["--regen", "--reports-dir", str(tmp_path)]) == 0
    second = (tmp_path / "INDEX.md").read_bytes()

    assert second.splitlines()[:50] == first.splitlines()[:50]
