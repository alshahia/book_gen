"""Read-only queries over the book knowledge graph."""
import os
import re
import sys
from pathlib import Path

for stream in (sys.stdout, sys.stderr):
    reconfigure = getattr(stream, "reconfigure", None)
    if reconfigure:
        try:
            reconfigure(encoding="utf-8")
        except (ValueError, OSError):
            pass

import sqlite3

CHAPTER_ID = re.compile(r"^ch-(\d{1,4})$", re.I)


def _db_path(db_path=None):
    return Path(db_path or os.environ.get("BOOK_KG_DB", ".book-kg.db")).resolve()


def _connect(db_path=None):
    path = _db_path(db_path)
    if not path.is_file():
        raise ValueError(f"database does not exist: {path}")
    db = sqlite3.connect(str(path))
    db.row_factory = sqlite3.Row
    return db


def _chapter_number(chapter):
    match = CHAPTER_ID.fullmatch(chapter)
    if not match:
        raise ValueError("chapter must be ch-NN")
    return int(match.group(1))


def _book_id(db):
    row = db.execute("SELECT id FROM books ORDER BY id LIMIT 1").fetchone()
    if not row:
        raise ValueError("database contains no book")
    return row[0]


def trace_path(motif, ch_start=1, ch_end=9999, db_path=None):
    if not motif or ch_start < 1 or ch_end < ch_start:
        raise ValueError("invalid motif or chapter range")
    db = _connect(db_path)
    try:
        rows = db.execute("""
            SELECT c.chapter_num, 'ch-' || printf('%02d', c.chapter_num) AS chapter,
                   m.name AS motif, mm.line_number, mm.context
            FROM motif_mentions mm
            JOIN motifs m ON m.id=mm.motif_id
            JOIN chapters c ON c.id=mm.chapter_id
            WHERE m.book_id=? AND lower(m.name)=lower(?) AND c.chapter_num BETWEEN ? AND ?
            ORDER BY c.chapter_num, mm.line_number
        """, (_book_id(db), motif, ch_start, ch_end)).fetchall()
        return [dict(row) for row in rows]
    finally:
        db.close()


def motifs_in_chapter(chapter, db_path=None):
    number = _chapter_number(chapter)
    db = _connect(db_path)
    try:
        rows = db.execute("""
            SELECT DISTINCT m.name FROM motif_mentions mm
            JOIN motifs m ON m.id=mm.motif_id
            JOIN chapters c ON c.id=mm.chapter_id
            WHERE m.book_id=? AND c.chapter_num=? ORDER BY m.name
        """, (_book_id(db), number)).fetchall()
        return [row[0] for row in rows]
    finally:
        db.close()


def contradicts(line, db_path=None):
    db = _connect(db_path)
    try:
        rows = db.execute("""
            SELECT fl.line_id, flo.chapter_id, c.chapter_num, flo.line_number,
                   flo.context, ca.keyword, ca.expected_state
            FROM frozen_lines fl
            JOIN frozen_line_occurrences flo ON flo.frozen_line_id=fl.id
            JOIN chapters c ON c.id=flo.chapter_id
            LEFT JOIN continuity_anchors ca ON ca.book_id=fl.book_id
            WHERE fl.book_id=? AND fl.line_id=?
            ORDER BY c.chapter_num, flo.line_number
        """, (_book_id(db), line)).fetchall()
        return [dict(row) for row in rows if row["expected_state"] and row["context"] and row["expected_state"].lower() not in row["context"].lower()]
    finally:
        db.close()


def references(chapter, db_path=None):
    number = _chapter_number(chapter)
    db = _connect(db_path)
    try:
        rows = db.execute("""
            SELECT fc.chapter_num AS from_chapter, 'ch-' || printf('%02d', fc.chapter_num) AS from_id,
                   tc.chapter_num AS to_chapter, 'ch-' || printf('%02d', tc.chapter_num) AS to_id,
                   cr.ref_type, cr.line_number, cr.context
            FROM chapter_refs cr
            JOIN chapters fc ON fc.id=cr.from_chapter_id
            JOIN chapters tc ON tc.id=cr.to_chapter_id
            WHERE fc.book_id=? AND tc.chapter_num=?
            ORDER BY fc.chapter_num, cr.line_number
        """, (_book_id(db), number)).fetchall()
        return [dict(row) for row in rows]
    finally:
        db.close()


def fts_search(term, db_path=None):
    if not term or any(ch in term for ch in '"\x00'):
        raise ValueError("invalid FTS term")
    escaped = '"' + term.replace('"', '""') + '"'
    db = _connect(db_path)
    try:
        rows = db.execute("SELECT content,source_type,source_id,book_id FROM search_index WHERE search_index MATCH ?", (escaped,)).fetchall()
        return [dict(row) for row in rows]
    finally:
        db.close()
