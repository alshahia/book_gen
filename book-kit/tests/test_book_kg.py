"""Tests for the SQLite book knowledge graph."""
import importlib.util
import json
import os
import sqlite3
from pathlib import Path

import pytest

KIT_ROOT = Path(__file__).resolve().parents[1]
MCP_ROOT = KIT_ROOT / "mcp" / "book-kg"
FIXTURE = KIT_ROOT / "tests" / "fixtures" / "kg-3ch-book"

spec = importlib.util.spec_from_file_location("book_kg_indexer", MCP_ROOT / "indexer.py")
indexer = importlib.util.module_from_spec(spec)
spec.loader.exec_module(indexer)
qspec = importlib.util.spec_from_file_location("book_kg_query", MCP_ROOT / "query.py")
query = importlib.util.module_from_spec(qspec)
qspec.loader.exec_module(query)


def db_for(tmp_path):
    db = tmp_path / "book-kg.db"
    indexer.index_book(FIXTURE, db)
    return db


def test_expected_edge_counts(tmp_path):
    db = db_for(tmp_path)
    conn = sqlite3.connect(db)
    assert conn.execute("SELECT count(*) FROM chapters").fetchone()[0] == 3
    assert conn.execute("SELECT count(*) FROM motif_mentions").fetchone()[0] == 6
    assert conn.execute("SELECT count(*) FROM character_mentions").fetchone()[0] == 3
    assert conn.execute("SELECT count(*) FROM frozen_line_occurrences").fetchone()[0] == 1


def test_trace_path_returns_chronological_three_nodes(tmp_path):
    db = db_for(tmp_path)
    rows = query.trace_path("coin", db_path=db)
    assert [row["chapter"] for row in rows] == ["ch-01", "ch-02", "ch-03"]


def test_motifs_in_chapter(tmp_path):
    assert query.motifs_in_chapter("ch-02", db_for(tmp_path)) == ["coin", "door"]


def test_contradicts_returns_empty_without_expected_state(tmp_path):
    assert query.contradicts("frozen-12", db_for(tmp_path)) == []


def test_references_targets_chapter(tmp_path):
    db = db_for(tmp_path)
    rows = query.references("ch-03", db)
    assert len(rows) == 1
    assert rows[0]["from_id"] == "ch-02"


def test_idempotent_reindex_has_no_duplicates(tmp_path):
    db = db_for(tmp_path)
    indexer.index_book(FIXTURE, db)
    conn = sqlite3.connect(db)
    assert conn.execute("SELECT count(*) FROM motif_mentions").fetchone()[0] == 6
    assert conn.execute("SELECT count(*) FROM character_mentions").fetchone()[0] == 3
    assert conn.execute("SELECT count(*) FROM chapters").fetchone()[0] == 3
    assert conn.execute("SELECT count(*) FROM schema_version").fetchone()[0] == 1
    assert conn.execute("SELECT count(*) FROM frozen_line_occurrences").fetchone()[0] == 1
    assert conn.execute("SELECT count(*) FROM continuity_anchors").fetchone()[0] == 1
    assert conn.execute("SELECT count(*) FROM chapter_deps").fetchone()[0] == 2


def test_outline_md_creates_chapter_deps(tmp_path):
    db = db_for(tmp_path)
    conn = sqlite3.connect(db)
    rows = conn.execute("""
        SELECT fc.chapter_num AS from_ch, tc.chapter_num AS to_ch, cd.dep_type
        FROM chapter_deps cd
        JOIN chapters fc ON fc.id=cd.chapter_id
        JOIN chapters tc ON tc.id=cd.depends_on_chapter_id
        ORDER BY fc.chapter_num, tc.chapter_num
    """).fetchall()
    assert len(rows) == 2
    pairs = {(r[0], r[1]) for r in rows}
    assert pairs == {(2, 1), (3, 2)}
    assert {r[2] for r in rows} == {"narrative"}


def test_fts5_search(tmp_path):
    db = db_for(tmp_path)
    assert query.fts_search("coin", db)
