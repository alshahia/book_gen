CREATE TABLE IF NOT EXISTS books (
    id              INTEGER PRIMARY KEY,
    slug            TEXT UNIQUE NOT NULL,
    title           TEXT,
    root_path       TEXT NOT NULL,
    indexed_at      TEXT DEFAULT CURRENT_TIMESTAMP,
    parser_version  TEXT
);

CREATE TABLE IF NOT EXISTS chapters (
    id              INTEGER PRIMARY KEY,
    book_id         INTEGER NOT NULL REFERENCES books(id) ON DELETE CASCADE,
    chapter_num     INTEGER NOT NULL,
    file_path       TEXT NOT NULL,
    title           TEXT,
    word_count      INTEGER,
    hash            TEXT,
    indexed_at      TEXT DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(book_id, chapter_num)
);

CREATE TABLE IF NOT EXISTS beats (
    id              INTEGER PRIMARY KEY,
    chapter_id      INTEGER NOT NULL REFERENCES chapters(id) ON DELETE CASCADE,
    beat_num        INTEGER NOT NULL,
    level           INTEGER NOT NULL,
    heading         TEXT NOT NULL,
    start_line      INTEGER,
    end_line        INTEGER,
    word_count      INTEGER,
    UNIQUE(chapter_id, beat_num)
);

CREATE TABLE IF NOT EXISTS frozen_lines (
    id                      INTEGER PRIMARY KEY,
    book_id                 INTEGER NOT NULL REFERENCES books(id) ON DELETE CASCADE,
    line_id                 TEXT NOT NULL,
    quote                   TEXT NOT NULL,
    sha256                  TEXT NOT NULL,
    first_seen_chapter_num  INTEGER,
    note                    TEXT,
    UNIQUE(book_id, line_id)
);

CREATE TABLE IF NOT EXISTS frozen_line_occurrences (
    id              INTEGER PRIMARY KEY,
    frozen_line_id  INTEGER NOT NULL REFERENCES frozen_lines(id) ON DELETE CASCADE,
    chapter_id      INTEGER NOT NULL REFERENCES chapters(id) ON DELETE CASCADE,
    beat_id         INTEGER REFERENCES beats(id),
    line_number     INTEGER,
    context         TEXT,
    UNIQUE(frozen_line_id, chapter_id, line_number)
);

CREATE TABLE IF NOT EXISTS motifs (
    id                      INTEGER PRIMARY KEY,
    book_id                 INTEGER NOT NULL REFERENCES books(id) ON DELETE CASCADE,
    name                    TEXT NOT NULL,
    description             TEXT,
    UNIQUE(book_id, name)
);

CREATE TABLE IF NOT EXISTS motif_mentions (
    id              INTEGER PRIMARY KEY,
    motif_id        INTEGER NOT NULL REFERENCES motifs(id) ON DELETE CASCADE,
    chapter_id      INTEGER NOT NULL REFERENCES chapters(id) ON DELETE CASCADE,
    beat_id         INTEGER REFERENCES beats(id),
    line_number     INTEGER,
    context         TEXT
);

CREATE TABLE IF NOT EXISTS characters (
    id              INTEGER PRIMARY KEY,
    book_id         INTEGER NOT NULL REFERENCES books(id) ON DELETE CASCADE,
    name            TEXT NOT NULL,
    description     TEXT,
    UNIQUE(book_id, name)
);

CREATE TABLE IF NOT EXISTS character_mentions (
    id              INTEGER PRIMARY KEY,
    character_id    INTEGER NOT NULL REFERENCES characters(id) ON DELETE CASCADE,
    chapter_id      INTEGER NOT NULL REFERENCES chapters(id) ON DELETE CASCADE,
    beat_id         INTEGER REFERENCES beats(id),
    line_number     INTEGER,
    context         TEXT
);

CREATE TABLE IF NOT EXISTS continuity_anchors (
    id                      INTEGER PRIMARY KEY,
    book_id                 INTEGER NOT NULL REFERENCES books(id) ON DELETE CASCADE,
    keyword                 TEXT NOT NULL,
    quote                   TEXT,
    scope_start_chapter     INTEGER,
    scope_end_chapter       INTEGER,
    expected_state          TEXT,
    actual_state_summary    TEXT,
    UNIQUE(book_id, keyword, scope_start_chapter, scope_end_chapter)
);

CREATE TABLE IF NOT EXISTS chapter_refs (
    id                      INTEGER PRIMARY KEY,
    from_chapter_id         INTEGER NOT NULL REFERENCES chapters(id) ON DELETE CASCADE,
    to_chapter_id           INTEGER NOT NULL REFERENCES chapters(id) ON DELETE CASCADE,
    ref_type                TEXT,
    line_number             INTEGER,
    context                 TEXT
);

CREATE TABLE IF NOT EXISTS chapter_deps (
    id                      INTEGER PRIMARY KEY,
    chapter_id              INTEGER NOT NULL REFERENCES chapters(id) ON DELETE CASCADE,
    depends_on_chapter_id   INTEGER NOT NULL REFERENCES chapters(id) ON DELETE CASCADE,
    dep_type                TEXT
);

CREATE TABLE IF NOT EXISTS index_runs (
    id                      INTEGER PRIMARY KEY,
    book_id                 INTEGER NOT NULL REFERENCES books(id) ON DELETE CASCADE,
    started_at              TEXT NOT NULL,
    finished_at             TEXT,
    files_seen              INTEGER,
    error                   TEXT
);

CREATE VIRTUAL TABLE IF NOT EXISTS search_index USING fts5(
    content,
    source_type UNINDEXED,
    source_id UNINDEXED,
    book_id UNINDEXED,
    tokenize='unicode61 remove_diacritics 2'
);

CREATE TABLE IF NOT EXISTS schema_version (
    version     INTEGER PRIMARY KEY,
    applied_at  TEXT DEFAULT CURRENT_TIMESTAMP
);
