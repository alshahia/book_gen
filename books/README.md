# Books — Book-Gen Projects

This folder holds **one folder per book**. Each `books/<slug>/` is a self-contained book project: its own intake, skeleton, research log, outline, style guide, writing plan, bible, ledger, decisions log, source map (translation-mode only), and chapters.

## Layout

```
books/
├── README.md                            ← this file
├── <slug>/                              ← one folder per book
│   ├── intake.md                        ← Phase 0: 15-field confirmed intake (§10 translation-mode toggle)
│   ├── source-map.md                    ← Phase 0: translation-mode only (chapter → source binding)
│   ├── skeleton.md                      ← Phase 1: chapter list + depends_on tags
│   ├── research-log.md                  ← Phase 2: per-source structured entries
│   ├── outline.md                       ← Phase 3: full chapter summaries
│   ├── style-guide.md                   ← Phase 4: presentation + voice
│   ├── writing-plan.md                  ← Phase 5: linear / parallel / mixed
│   ├── frozen-lines.json                ← Phase 4 close: SHA256 manifest of frozen lines
│   ├── .translate-progress.json         ← Phase 6: translation-mode resume ledger (chunked-write + resume)
│   ├── bible.md                         ← cumulative, append-only state
│   ├── ledger.md                        ← one row per chapter status
│   ├── decisions-log.md                 ← append-only why-changed record
│   └── chapters/
│       ├── ch-01.md                     ← the prose itself, one file per chapter
│       ├── ch-02.md
│       └── ...
└── ...
```

Templates for every file above live at `book_workflow/book-agents/templates/` (18 markdown + 1 JSON schema). The orchestrator skill at `agents_manager/book-gen-orchestrator/SKILL.md` knows where to find them.

## How a book gets here

The user says "write a book about X" (or any book-gen trigger phrase). The master:

1. Loads `agents_manager/book-gen-orchestrator/SKILL.md`.
2. Runs the 7-phase pipeline (intake → skeleton → research → outline → style → writing plan → chapter writes → review passes).
3. **Translation-mode only:** when intake §10 `Is translation? = yes`, master also copies `source-map.md` template and runs `book_workflow/scripts/build_source_map.py` before Phase 3.
4. **Phase 7 dispatch selection:** translation-mode + `source-map.md` present → loads `agents_manager/book-reviewer/SKILL.md` (2-pass accuracy + consistency); otherwise the default 3-pass dev/line/copy.
5. Writes each book's state files into a `books/<slug>/` folder under here.

## Slug policy

- Lowercase, hyphen-separated, ASCII only.
- Derived from the working title (e.g. "Daily Focus" → `daily-focus`).
- On collision: suffix `-v2`, `-v3`, etc. Never overwrite.

## State files are master-owned

- Master writes `intake.md`, `source-map.md` (translation-mode), `writing-plan.md`, `decisions-log.md`, `frozen-lines.json` directly.
- `am-planning` writes `skeleton.md` and `outline.md`.
- `am-research` writes `research-log.md`.
- `am-design` writes `style-guide.md`.
- `am-coder` (in book-writer mode) writes `chapters/*.md` + appends to `bible.md` + updates `ledger.md` to `drafted` + appends to `.translate-progress.json` (translation-mode).
- `am-review` writes review reports under `share/reports/04_book-review_<task-id>_ch-<NN>_<pass>.md`; **Branch A (translation):** `04_book-review_<task-id>_ch-<NN>_accuracy.md` + `04_book-review_<task-id>_ch-<NN>_consistency.md`; **Branch B (native):** `04_book-review_<task-id>_ch-<NN>_dev.md` + `04_book-review_<task-id>_ch-<NN>_lineedit.md` + `04_book-review_<task-id>_ch-<NN>_copy.md`. Master updates `ledger.md` status from `drafted` → pass-specific status → `approved` based on review verdicts.
- `bible.md` is append-only — never rewrite existing entries.
- `ledger.md` rows are updated in place; history is captured in `decisions-log.md`.

## Smoke test

If you ran a smoke test, the book lives at `books/daily-focus/` (or whichever slug was used). Inspect:

- `intake.md` — what the smoke test filled in
- `skeleton.md` — chapter list
- `outline.md` — chapter summaries
- `chapters/ch-01.md` — the prose
- `share/reports/04_book-review_*.md` — the review passes (Branch B: dev + line; Branch A: accuracy + consistency)
