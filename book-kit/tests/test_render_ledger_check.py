"""Tests for render_ledger_check.py — gate-checklist block generator + ledger writer.

Stdlib-only fixtures. The tests target the two pure functions directly:

* ``build_gate_block`` — produces the 8-row markdown table from
  hand-crafted payload dicts that mimic ``check_chapter.py --json`` and
  ``book_check.py --json`` output. This is the heart of the module and
  the only piece that requires nontrivial branching logic.
* ``write_into_ledger`` — anchors on the ``## Gate checklist`` header
  in a fixture ``ledger.md`` and replaces the block between that
  header and the next ``## …`` section, so re-runs never duplicate.

The script's subprocess wrappers (``_load_check_chapter_json`` /
``_load_book_check_json``) are intentionally not exercised here — the
script-level smoke test is documented in the coder summary and the
upstream review note (the daily-focus manual run).
"""
import sys
from pathlib import Path

# conftest.py already prepends book-kit/book_workflow/scripts to sys.path.
import render_ledger_check as rlc

KIT_ROOT = Path(__file__).resolve().parents[1]
SCRIPT = KIT_ROOT / "book_workflow" / "scripts" / "render_ledger_check.py"


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _write_chapter(root, name="ch-03.md", text="# Chapter\n\nBody text here.\n"):
    p = root / "chapters" / name
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(text, encoding="utf-8")
    return p


def _seed_frozen_lines(root, chapter_filename, lines):
    """Write ``frozen-lines.json`` with the given line numbers and a fixed hash."""
    import hashlib
    fp = root / "frozen-lines.json"
    items = []
    for n in lines:
        # The 0xdeadbeef hash never matches; we use this only to count
        # the manifest entries, not to verify them.
        items.append({"line_number": n, "sha256": hashlib.sha256(b"x").hexdigest()})
    payload = {"chapters": {chapter_filename: {"frozen_lines": items}}}
    fp.write_text(__import__("json").dumps(payload), encoding="utf-8")


def _base_ledger() -> str:
    """A minimal ledger.md template containing only the canonical sections.

    ``## Gate checklist`` is intentionally omitted — ``write_into_ledger``
    appends it when absent.
    """
    return (
        "# Chapter Ledger\n"
        "\n"
        "Status values, in order: `planned` → `drafted` → `approved`.\n"
        "\n"
        "## Mechanical gates\n"
        "\n"
        "- `book_check.py` — gate\n"
        "- `check_chapter.py` — gate\n"
        "\n"
        "## Open questions\n"
        "\n"
        "1. Where do we want this to land?\n"
        "\n"
    )


# ---------------------------------------------------------------------------
# 1) Builds an 8-row table from a realistic check_chapter payload
# ---------------------------------------------------------------------------


def test_renders_eight_rows_from_check_chapter_json(tmp_path):
    """A representative check_chapter payload → exactly 8 rows in spec order.

    The 4 rules served by check_chapter (``Word window``,
    ``Countdown ≥1``, ``Closing hook ≤8``, ``Banned-pattern scan``) all
    return ``PASS``; the 4 book_check-backed rows return ``n/a`` because
    the payload is omitted here.
    """
    check_chapter_payload = {
        "chapter": "ch-03",
        "checks": [
            {"name": "word_count_per_beat", "status": "PASS",
             "evidence": "window=600-750; beats=4; …"},
            {"name": "countdown", "status": "PASS",
             "evidence": "ch-03 has 2 countdown token(s)"},
            {"name": "closing_hook", "status": "PASS",
             "evidence": "closing hook is 6 words (≤ 8)"},
            {"name": "banned_patterns", "status": "PASS",
             "evidence": "scanned 3 pattern(s); no matches"},
        ],
    }

    block = rlc.build_gate_block(
        "ch-03.md",
        check_chapter_payload=check_chapter_payload,
    )

    lines = [ln for ln in block.splitlines() if ln.startswith("|") and ln.count("|") >= 3]
    # 1 header + 1 separator + 8 data rows = 10 lines
    assert len(lines) == 10, (
        f"expected header+separator+8 rows (=10 lines), got {len(lines)}:\n{block}"
    )

    # Verify the 8 rule labels appear in the spec order
    rule_rows = [ln for ln in lines if ln.startswith("| Word window")
                 or ln.startswith("| Countdown")
                 or ln.startswith("| Closing hook")
                 or ln.startswith("| Frozen lines")
                 or ln.startswith("| Banned-pattern")
                 or ln.startswith("| Cross-ref")
                 or ln.startswith("| Source ratio")
                 or ln.startswith("| Tashkeel ratio")]
    assert len(rule_rows) == 8, f"expected 8 data rows; got {len(rule_rows)}: {rule_rows}"

    expected_order = [
        "Word window", "Countdown", "Closing hook", "Frozen lines",
        "Banned-pattern", "Cross-ref", "Source ratio", "Tashkeel ratio",
    ]
    actual_order = [r.split("|")[1].strip().split(" ")[0] + ""
                    if r.split("|")[1].strip().split(" ")[0] not in ("Source", "Tashkeel")
                    else r.split("|")[1].strip().split(" ")[0]
                    for r in rule_rows]
    # Just verify the row-start strings appear in order; "Word window" vs
    # "Source ratio" both start with unique tokens so a positional slice
    # is unambiguous.
    starts = [r.split("|")[1].strip() for r in rule_rows]
    for label, start in zip(expected_order, starts):
        assert start.startswith(label), (
            f"order drift at row {label!r}: got {start!r}"
        )


# ---------------------------------------------------------------------------
# 2) Status inference — PASS / FAIL / WARN / n/a
# ---------------------------------------------------------------------------


def test_status_inference_pass_fail_warn_na(tmp_path):
    """Status cell values match the spec verbatim (PASS/FAIL/WARN/n/a)."""
    check_chapter_payload = {
        "chapter": "ch-04",
        "checks": [
            # Word window = WARN, Countdown = PASS, Closing hook = FAIL,
            # Banned-patterns = WARN.
            {"name": "word_count_per_beat", "status": "WARN",
             "evidence": "window=600-750; beats=4; …"},
            {"name": "countdown", "status": "PASS",
             "evidence": "1 token"},
            {"name": "closing_hook", "status": "FAIL",
             "evidence": "closing hook is 14 words (max 8)"},
            {"name": "banned_patterns", "status": "WARN",
             "evidence": "scanned 1 pattern(s); no matches"},
        ],
    }
    book_check_payload = {
        "chapters": {
            "ch-04.md": {
                "source_ratio": 0.85,
                "source_ratio_tolerance": 0.40,
                "tashkeel_ratio": 0.12,
            }
        },
        "cross_ref": {"resolved": 12, "total": 14, "broken": [{"x": 1}]},
    }

    block = rlc.build_gate_block(
        "ch-04.md",
        check_chapter_payload=check_chapter_payload,
        book_check_payload=book_check_payload,
    )

    # Pull Status cell from each row.
    def _status(row_label: str) -> str:
        for line in block.splitlines():
            if line.startswith(f"| {row_label} "):
                cells = [c.strip() for c in line.strip().strip("|").split("|")]
                return cells[1]
        raise AssertionError(f"row {row_label!r} not found in:\n{block}")

    assert _status("Word window") == "WARN"
    assert _status("Countdown ≥1") == "PASS"
    assert _status("Closing hook ≤8") == "FAIL"
    assert _status("Banned-pattern scan") == "WARN"

    # Cross-ref integrity → FAIL because broken list is non-empty
    assert _status("Cross-ref integrity") == "FAIL", (
        f"expected FAIL because broken list non-empty; got {_status('Cross-ref integrity')!r}"
    )
    # Source ratio 0.85 in (1-0.40, 1+0.40) = (0.60, 1.40) → PASS
    assert _status("Source ratio") == "PASS"
    # Tashkeel 0.12 > 0 → PASS (per spec, tashkeel is just > 0)
    assert _status("Tashkeel ratio") == "PASS"

    # Now verify n/a propagation: omit book_check → cross-ref/source/tashkeel
    # rows + frozen-lines row default to n/a.
    block_na = rlc.build_gate_block(
        "ch-04.md",
        check_chapter_payload=check_chapter_payload,
        book_check_payload=None,
    )
    assert "Frozen lines intact | n/a" in block_na, (
        f"expected frozen-lines row to be n/a; got block:\n{block_na}"
    )
    assert "Cross-ref integrity | n/a" in block_na
    assert "Source ratio | n/a" in block_na
    assert "Tashkeel ratio | n/a" in block_na


# ---------------------------------------------------------------------------
# 3) Cross-ref evidence format — "N/total resolved"
# ---------------------------------------------------------------------------


def test_cross_ref_evidence_format(tmp_path):
    """When cross_ref block is present, evidence cell reads ``N/total resolved``."""
    book_check_payload = {
        "chapters": {"ch-05.md": {"frozen_intact": True}},
        "cross_ref": {"resolved": 17, "total": 18, "broken": []},
    }

    block = rlc.build_gate_block(
        "ch-05.md",
        check_chapter_payload=None,
        book_check_payload=book_check_payload,
    )

    cross_ref_row = None
    for line in block.splitlines():
        if line.startswith("| Cross-ref integrity"):
            cross_ref_row = line
            break
    assert cross_ref_row is not None, (
        f"Cross-ref integrity row missing in:\n{block}"
    )
    cells = [c.strip() for c in cross_ref_row.strip().strip("|").split("|")]
    # Status = PASS (no broken refs)
    assert cells[1] == "PASS"
    # Evidence ends with "17/18 resolved" exactly
    assert cells[2] == "17/18 resolved", (
        f"evidence cell must read 'N/total resolved'; got {cells[2]!r}"
    )


# ---------------------------------------------------------------------------
# 4) --out mode replaces the existing gate-checklist block (no duplication)
# ---------------------------------------------------------------------------


def test_out_mode_writes_block_back_to_ledger(tmp_path):
    """``write_into_ledger`` replaces the existing block in-place when
    present; re-running it does NOT duplicate.

    Two passes are made: first with a chunk that swaps a representative
    cell value, then again with the original chunk. After both passes,
    the file must contain *exactly one* ``## Gate checklist`` header and
    a single 8-row table — no duplicate header, no duplicate rows.
    """
    ledger = tmp_path / "ledger.md"
    ledger.write_text(_base_ledger(), encoding="utf-8")

    block_v1 = rlc.build_gate_block(
        "ch-09.md",
        check_chapter_payload={
            "checks": [
                {"name": "word_count_per_beat", "status": "PASS",
                 "evidence": "first-pass evidence token (e1)"},
                {"name": "countdown", "status": "WARN",
                 "evidence": "second-rule evidence (e2)"},
                {"name": "closing_hook", "status": "FAIL",
                 "evidence": "third-rule evidence (e3)"},
                {"name": "banned_patterns", "status": "WARN",
                 "evidence": "fourth-rule evidence (e4)"},
            ]
        },
    )

    rc1 = rlc.write_into_ledger(ledger, block_v1)
    assert rc1 == 0, f"first call: expected header-appended (rc=0); got {rc1}"
    text1 = ledger.read_text(encoding="utf-8")
    assert text1.count("## Gate checklist") == 1, "exactly one header after first pass"
    assert text1.count("first-pass evidence token") == 1
    assert text1.count("| Word window ") == 1, "exactly one Word-window data row"
    assert text1.count("| Countdown ≥1 ") == 1

    # Now write an updated block with different evidence — must replace,
    # not append.
    block_v2 = rlc.build_gate_block(
        "ch-09.md",
        check_chapter_payload={
            "checks": [
                {"name": "word_count_per_beat", "status": "PASS",
                 "evidence": "second-pass evidence token (e1v2)"},
                {"name": "countdown", "status": "PASS",
                 "evidence": "second-rule evidence (e2v2)"},
                {"name": "closing_hook", "status": "PASS",
                 "evidence": "third-rule evidence (e3v2)"},
                {"name": "banned_patterns", "status": "PASS",
                 "evidence": "fourth-rule evidence (e4v2)"},
            ]
        },
    )

    rc2 = rlc.write_into_ledger(ledger, block_v2)
    assert rc2 == 1, f"second call: expected in-place replace (rc=1); got {rc2}"
    text2 = ledger.read_text(encoding="utf-8")

    # Re-running must not duplicate headers or rows.
    assert text2.count("## Gate checklist") == 1, "header must not duplicate"
    assert text2.count("| Word window ") == 1, "Word-window row must not duplicate"
    assert text2.count("| Countdown ≥1 ") == 1
    assert text2.count("| Closing hook ≤8 ") == 1
    assert text2.count("| Frozen lines intact ") == 1
    assert text2.count("| Banned-pattern scan ") == 1
    assert text2.count("| Cross-ref integrity ") == 1
    assert text2.count("| Source ratio ") == 1
    assert text2.count("| Tashkeel ratio ") == 1

    # v1 evidence must be gone entirely (replaced, not kept).
    assert "first-pass evidence token" not in text2
    # v2 evidence must be present in the table.
    assert "second-pass evidence token (e1v2)" in text2

    # The "Mechanical gates" section that follows must be preserved.
    assert "## Mechanical gates" in text2, "subsequent sections must be preserved"
    assert "## Open questions" in text2
