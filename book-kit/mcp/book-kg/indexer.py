"""SQLite book knowledge graph indexer."""
import hashlib
import json
import re
import sys
from datetime import datetime, timezone
from pathlib import Path

for stream in (sys.stdout, sys.stderr):
    reconfigure = getattr(stream, "reconfigure", None)
    if reconfigure:
        try:
            reconfigure(encoding="utf-8")
        except (ValueError, OSError):
            pass

import sqlite3

PACKAGE_ROOT = Path(__file__).resolve().parent
SCHEMA_PATH = PACKAGE_ROOT / "schema.sql"
SCHEMA_VERSION = 1
CHAPTER_RE = re.compile(r"^ch-(\d+)(?:[-_.].*)?\.md$", re.I)
CHAPTER_REF_RE = re.compile(r"\bch-(\d+)\b", re.I)


def read_text(path):
    return path.read_text(encoding="utf-8")


def resolve_under(path, root):
    root = Path(root).resolve()
    candidate = Path(path).resolve()
    if candidate != root and root not in candidate.parents:
        raise ValueError(f"path escapes book root: {path}")
    return candidate


def connect_db(db_path):
    db = sqlite3.connect(str(db_path))
    db.execute("PRAGMA foreign_keys = ON")
    db.row_factory = sqlite3.Row
    db.executescript(SCHEMA_PATH.read_text(encoding="utf-8"))
    db.execute("CREATE TABLE IF NOT EXISTS schema_version (version INTEGER PRIMARY KEY, applied_at TEXT DEFAULT CURRENT_TIMESTAMP)")
    if db.execute("SELECT 1 FROM schema_version WHERE version=?", (SCHEMA_VERSION,)).fetchone() is None:
        db.execute("INSERT INTO schema_version(version) VALUES (?)", (SCHEMA_VERSION,))
    db.commit()
    return db


def _heading_beats(text):
    headings = [(i, len(m.group(1)), m.group(2).strip()) for i, line in enumerate(text.splitlines(), 1) if (m := re.match(r"^(#{2,3})\s+(.+?)\s*$", line))]
    beats = []
    for index, (start, level, heading) in enumerate(headings, 1):
        end = headings[index][0] - 1 if index < len(headings) else len(text.splitlines())
        words = len(re.findall(r"\b\w+\b", "\n".join(text.splitlines()[start:end])))
        beats.append((index, level, heading, start, end, words))
    return beats


def _sections(text, title):
    match = re.search(rf"^##\s+{re.escape(title)}\s*:?(?:\s|$)(.*?)(?=^##\s+|\Z)", text, re.I | re.M | re.S)
    return match.group(1) if match else ""


def _table_rows(block):
    rows = []
    for line in block.splitlines():
        if not line.lstrip().startswith("|"):
            continue
        cells = [c.strip() for c in line.strip().strip("|").split("|")]
        if len(cells) >= 2 and not all(set(c) <= set("-: ") for c in cells):
            rows.append(cells)
    return rows[1:] if rows and rows[0][0].lower() in {"name", "keyword", "character", "motif"} else rows


def _upsert_named(db, table, book_id, name, description=None):
    db.execute(f"INSERT OR IGNORE INTO {table}(book_id,name,description) VALUES (?,?,?)", (book_id, name, description))
    return db.execute(f"SELECT id FROM {table} WHERE book_id=? AND name=?", (book_id, name)).fetchone()[0]


def index_book(book_root, db_path=None):
    root = Path(book_root).resolve()
    if not root.is_dir():
        raise ValueError(f"book root is not a directory: {book_root}")
    db_path = Path(db_path or (root / ".book-kg.db")).resolve()
    # Explicit test or deployment paths may live outside the book root; only
    # reject a book root that itself is outside the resolved input boundary.
    db = connect_db(db_path)
    started = datetime.now(timezone.utc).isoformat()
    slug = root.name
    title = ""
    title_match = re.search(r"^#\s+(.+)$", read_text(root / "bible.md")) if (root / "bible.md").exists() else None
    if title_match:
        title = title_match.group(1).replace("Book Bible - ", "").strip()
    db.execute("INSERT OR IGNORE INTO books(slug,title,root_path,parser_version) VALUES (?,?,?,?)", (slug, title, str(root), "1"))
    book_id = db.execute("SELECT id FROM books WHERE slug=?", (slug,)).fetchone()[0]
    seen = 0
    try:
        bible = read_text(root / "bible.md") if (root / "bible.md").exists() else ""
        for row in _table_rows(_sections(bible, "Continuity anchor")):
            if len(row) >= 3 and re.search(r"ch-\d+", row[2], re.I):
                nums = [int(n) for n in re.findall(r"\d+", row[2])]
                db.execute("INSERT INTO continuity_anchors(book_id,keyword,quote,scope_start_chapter,scope_end_chapter) VALUES (?,?,?,?,?)", (book_id, row[0], row[1], nums[0], nums[-1]))
        for section, table in (("Motifs", "motifs"), ("Characters", "characters")):
            block = _sections(bible, section)
            for item in re.findall(r"^\s*[-*]\s+(.+?)\s*$", block, re.M):
                _upsert_named(db, table, book_id, item.strip(), "")
            for row in _table_rows(block):
                if row:
                    name = row[0].lstrip("-* ").strip()
                    if name.lower() not in {"motif", "character"}:
                        _upsert_named(db, table, book_id, name, row[1] if len(row) > 1 else "")

        chapters_dir = root / "chapters"
        chapters = []
        if chapters_dir.is_dir():
            for path in sorted(chapters_dir.glob("*.md")):
                match = CHAPTER_RE.match(path.name)
                if not match: continue
                chapters.append((int(match.group(1)), path))
        chapter_ids = {}
        db.execute("DELETE FROM chapter_refs WHERE from_chapter_id IN (SELECT id FROM chapters WHERE book_id=?) OR to_chapter_id IN (SELECT id FROM chapters WHERE book_id=?)", (book_id, book_id))
        # Pre-create all chapter rows so per-chapter ref insertion can target them.
        for number, path in chapters:
            text_pre = read_text(resolve_under(path, root))
            digest_pre = hashlib.sha256(text_pre.encode("utf-8")).hexdigest()
            words_pre = len(re.findall(r"\b\w+\b", text_pre))
            db.execute("INSERT OR IGNORE INTO chapters(book_id,chapter_num,file_path,title,word_count,hash) VALUES (?,?,?,?,?,?)", (book_id, number, str(path.relative_to(root)), text_pre.splitlines()[0].lstrip("# ") if text_pre else "", words_pre, digest_pre))
            chapter_id_pre = db.execute("SELECT id FROM chapters WHERE book_id=? AND chapter_num=?", (book_id, number)).fetchone()[0]
            chapter_ids[number] = chapter_id_pre
        for number, path in chapters:
            text = read_text(resolve_under(path, root))
            digest = hashlib.sha256(text.encode("utf-8")).hexdigest()
            words = len(re.findall(r"\b\w+\b", text))
            db.execute("INSERT OR IGNORE INTO chapters(book_id,chapter_num,file_path,title,word_count,hash) VALUES (?,?,?,?,?,?)", (book_id, number, str(path.relative_to(root)), text.splitlines()[0].lstrip("# ") if text else "", words, digest))
            db.execute("UPDATE chapters SET file_path=?,word_count=?,hash=?,indexed_at=CURRENT_TIMESTAMP WHERE book_id=? AND chapter_num=?", (str(path.relative_to(root)), words, digest, book_id, number))
            chapter_id = chapter_ids[number]
            db.execute("DELETE FROM motif_mentions WHERE chapter_id=?", (chapter_id,))
            db.execute("DELETE FROM character_mentions WHERE chapter_id=?", (chapter_id,))
            db.execute("DELETE FROM beats WHERE chapter_id=?", (chapter_id,))
            beats = _heading_beats(text)
            beat_ids = {}
            for beat_num, level, heading, start, end, beat_words in beats:
                db.execute("INSERT INTO beats(chapter_id,beat_num,level,heading,start_line,end_line,word_count) VALUES (?,?,?,?,?,?,?)", (chapter_id, beat_num, level, heading, start, end, beat_words))
                beat_ids[beat_num] = db.execute("SELECT id FROM beats WHERE chapter_id=? AND beat_num=?", (chapter_id, beat_num)).fetchone()[0]
            lines = text.splitlines()
            for row in db.execute("SELECT id,name FROM motifs WHERE book_id=?", (book_id,)).fetchall():
                for line_no, line in enumerate(lines, 1):
                    if row["name"].lower() in line.lower():
                        db.execute("INSERT INTO motif_mentions(motif_id,chapter_id,line_number,context) VALUES (?,?,?,?)", (row["id"], chapter_id, line_no, line.strip()))
            for row in db.execute("SELECT id,name FROM characters WHERE book_id=?", (book_id,)).fetchall():
                for line_no, line in enumerate(lines, 1):
                    if row["name"].lower() in line.lower():
                        db.execute("INSERT INTO character_mentions(character_id,chapter_id,line_number,context) VALUES (?,?,?,?)", (row["id"], chapter_id, line_no, line.strip()))
            for line_no, line in enumerate(lines, 1):
                for target in sorted(set(int(n) for n in CHAPTER_REF_RE.findall(line))):
                    if target in chapter_ids and target != number:
                        db.execute("INSERT OR IGNORE INTO chapter_refs(from_chapter_id,to_chapter_id,ref_type,line_number,context) VALUES (?,?,?,?,?)", (chapter_id, chapter_ids[target], "mention", line_no, line.strip()))
            db.execute("DELETE FROM search_index WHERE book_id=? AND source_type='chapter' AND source_id=?", (book_id, str(chapter_id)))
            db.execute("INSERT INTO search_index(content,source_type,source_id,book_id) VALUES (?,?,?,?)", (text, "chapter", str(chapter_id), str(book_id)))
            seen += 1

        frozen_path = root / "frozen-lines.json"
        if frozen_path.exists():
            data = json.loads(read_text(frozen_path))
            for chapter_name, payload in data.get("chapters", {}).items():
                chapter_match = CHAPTER_RE.match(chapter_name)
                if not chapter_match: continue
                chapter_id = chapter_ids.get(int(chapter_match.group(1)))
                if not chapter_id: continue
                for item in payload.get("frozen_lines", []):
                    line_id = item.get("id") or item.get("line_id") or f"frozen-{item.get('line_number')}"
                    quote = item.get("text") or item.get("quote") or ""
                    sha = item.get("sha256") or hashlib.sha256(quote.encode()).hexdigest()
                    db.execute("INSERT OR IGNORE INTO frozen_lines(book_id,line_id,quote,sha256,first_seen_chapter_num,note) VALUES (?,?,?,?,?,?)", (book_id, line_id, quote, sha, int(chapter_match.group(1)), item.get("note")))
                    frozen_id = db.execute("SELECT id FROM frozen_lines WHERE book_id=? AND line_id=?", (book_id, line_id)).fetchone()[0]
                    db.execute("INSERT OR IGNORE INTO frozen_line_occurrences(frozen_line_id,chapter_id,line_number,context) VALUES (?,?,?,?)", (frozen_id, chapter_id, item.get("line_number"), quote))
        finished = datetime.now(timezone.utc).isoformat()
        db.execute("INSERT INTO index_runs(book_id,started_at,finished_at,files_seen) VALUES (?,?,?,?)", (book_id, started, finished, seen))
        db.commit()
    except Exception as exc:
        db.execute("INSERT INTO index_runs(book_id,started_at,error) VALUES (?,?,?)", (book_id, started, str(exc)))
        db.commit()
        raise
    finally:
        db.close()
    return {"db_path": str(db_path), "book_id": book_id, "chapters": seen}


def main(argv=None):
    import argparse
    parser = argparse.ArgumentParser(description="Index a book into SQLite knowledge graph")
    parser.add_argument("book", type=Path)
    parser.add_argument("--db", type=Path)
    args = parser.parse_args(argv)
    print(json.dumps(index_book(args.book, args.db), ensure_ascii=False))

if __name__ == "__main__":
    main()
