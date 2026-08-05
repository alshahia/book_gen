# Workflow — the 7-phase book-gen pipeline

This is the operational guide for running the book-gen pipeline. See
`QUICKSTART.md` for the install path. See `TRANSLATION_MODE.md` for the
translation-specific extensions.

```
master → research → planning → design → master (writing-plan) → coder (per chapter) → review (whole book)
                                ↑                                       ↑
                                |                                       |
                                +─ bible.md append ─── ledger.md update ─┘
```

The orchestrator (`agents_manager/book-gen-orchestrator/SKILL.md`) drives
this flow. Specialists never spawn each other — only master dispatches.

---

## Phase 0 — Intake

**Output:** `books/<slug>/intake.md` (filled)

The orchestrator prompts the user for **9 fields** (native) or **16 fields**
(translation adds §10 with 7 more).

| # | Field | Notes |
|---|---|---|
| 1 | Title | Working title (can be revised in Phase 4) |
| 2 | Audience | "new managers", "ML researchers", "intermediate Python devs" |
| 3 | Length target | Approximate word count or chapter count |
| 4 | Tone | "casual / academic / journalistic / technical-reference" |
| 5 | POV / tense | "second-person present" / "third-person past" / etc. |
| 6 | Language | ISO 639-1 (`en`, `ar`, `fr`, …) |
| 7 | Renders RTL? | `true` for Arabic/Hebrew, `false` otherwise |
| 8 | Front matter | "preface + introduction" / "preface + introduction + foreword" |
| 9 | Back matter | "glossary + index + bibliography" / "none" |
| 10–16 | Translation-only (§10) | See TRANSLATION_MODE.md |

**Gate:** every field needs explicit user confirmation.

---

## Phase 1 — Skeleton

**Output:** `books/<slug>/skeleton.md` (filled)

Master dispatches `am-planning`. Skeleton contains:

- Chapter list (one row per chapter)
- Title + 1-sentence description per chapter
- Dependency tags (which chapters depend on which)
- Rough word target per chapter

No user gate — master writes and moves on.

---

## Phase 2 — Research

**Output:** `books/<slug>/research-log.md` (filled)

Master dispatches `am-research` per chapter. Research notes cover:

- Key concepts the chapter must explain
- External sources to cite
- Cross-references to other chapters
- Open questions for the writer

Chapters with no inter-dependencies run research in parallel.

No user gate.

---

## Phase 3 — Outline

**Output:** `books/<slug>/outline.md` (filled)

Master dispatches `am-planning`. Outline has:

- Per-chapter: H1 / H2 structure, key beats, target word count
- Cross-chapter: dependency graph, vocabulary consistency notes
- Translation-mode: source-map binding per chapter (REFUSES to advance
  if §10 `Is translation? = yes` but `source-map.md` is missing)

**Gate:** user reviews outline. Confirm to advance.

---

## Phase 4 — Style / voice

**Output:** `books/<slug>/style-guide.md` (filled)

Master dispatches `am-design`. Style guide covers:

- Voice (sentence length, formality, humor)
- Terminology (canonical names for key concepts)
- Structure (H2 conventions, code block treatment, list usage)
- Translation tolerances (tashkeel ratio, source-ratio, etc.)

**Gate:** user reviews style. Confirm to advance.

---

## Phase 5 — Writing plan

**Output:** `books/<slug>/writing-plan.md` (filled)

Master decides dispatch order:

- **LINEAR** — write chapters one at a time, in order
- **PARALLEL** — write all chapters in parallel (only for short books with no shared lore)
- **MIXED** — group chapters by dependency cluster, write each cluster in order, clusters in parallel (most common for medium-length books)

Also writes the dispatch prompts the coder will receive.

**Gate:** user reviews plan. Confirm to advance.

---

## Phase 6 — Writing

**Output:** `books/<slug>/chapters/ch-NN-*.md` (one per chapter)

Master dispatches `am-coder` per chapter. The coder loads
`agents_manager/book-writer/SKILL.md` which sets prose-writing posture.

Per chapter:

1. Read `outline.md` for that chapter's structure
2. Read `bible.md` for terminology consistency
3. Draft the chapter
4. Append terminology entries to `bible.md`
5. Update `ledger.md` row (status: in_progress → drafted → approved)
6. Append architectural decisions to `decisions-log.md` if any

Translation-mode chapters use **chunked-write**: `split_source.py` splits
the source at H2 boundaries, the coder writes one chunk at a time, and
`.translate-progress.json` tracks which parts are done so a session can
resume mid-chapter after a crash.

User gate only on chapter add/remove (mid-stream scope changes).

---

## Phase 7 — Review

**Output:** `share/reports/04_review_*.md` per chapter

Master dispatches `am-review` per chapter. Review mode is selected based
on `intake.md §10`:

| Trigger | Branch | What runs |
|---|---|---|
| §10 `Is translation? = no` (default) | **Branch B** | 3-pass: dev (structural) → line (sentence-level) → copy (typos/punctuation) |
| §10 `Is translation? = yes` AND `source-map.md` present | **Branch A** | 2-pass via `book-reviewer/SKILL.md`: Pass 1 (accuracy vs source) + Pass 2 (cross-chapter glossary consistency) — never combined |
| §10 `Is translation? = yes` but `source-map.md` missing | **REFUSE** | Orchestrator refuses to dispatch review until source-map is filled |

`book-reviewer` outputs go to `share/reports/04_book-review_ch-NN_pass1.md`
and `04_book-review_ch-NN_pass2.md`. Native `am-review` outputs go to
`share/reports/04_review_ch-NN_dev.md` etc.

Copy-edit (Branch B, third pass) only runs when ALL chapters are
`approved` — skipped on partial runs.

`max_fix_loops = 3` per chapter. After 3 fix loops without approval,
master surfaces to the user.

---

## Output paths

| File | Owner | Purpose |
|---|---|---|
| `books/<slug>/intake.md` | master | Phase 0 |
| `books/<slug>/skeleton.md` | am-planning | Phase 1 |
| `books/<slug>/research-log.md` | am-research | Phase 2 |
| `books/<slug>/outline.md` | am-planning | Phase 3 |
| `books/<slug>/style-guide.md` | am-design | Phase 4 |
| `books/<slug>/writing-plan.md` | master | Phase 5 |
| `books/<slug>/chapters/ch-NN-*.md` | am-coder | Phase 6 |
| `books/<slug>/bible.md` | am-coder (append) | Phase 6 |
| `books/<slug>/ledger.md` | am-coder (update) | Phase 6 |
| `books/<slug>/decisions-log.md` | any (append) | ongoing |
| `books/<slug>/source-map.md` | am-research (translation) | Phase 0/3 |
| `books/<slug>/.translate-progress.json` | am-coder (translation) | Phase 6 |
| `share/reports/04_review_*.md` | am-review / book-reviewer | Phase 7 |
| `share/handoffs/` | inter-agent | handoff notes |
| `share/notes/99_progress_<task-id>.md` | master | progress log |

User content (`books/`, `tasks/`, `share/`) survives kit upgrades. Engine
content (`opencode.jsonc`, `CLAUDE.md`, `agents_manager/`,
`book_workflow/`) gets refreshed on `python install.py --upgrade`.
