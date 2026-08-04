# Build-Exports Spec

> Canonical reference for the Phase 5b export pipeline in book-gen. Read by master (Phase 5b dispatch) and by am-design (preface LLM pass).

## What problem this solves

Before this protocol, books shipped as raw chapter markdown: no TOC, no glossary, no preface, no index. Readers got a folder of prose files. Two completed books (`books/ai-agents-with-python/`, `books_from_other_projects/city-of-memories/`) shipped without these; feedback flagged it as a load-bearing gap.

Phase 5b builds the front-matter and back-matter that turn prose into a book.

## Pipeline

```
build_exports.py books/<slug>/
|
+-- Step 1: book_check.py books/<slug>/
|         Exit 0 required; abort on failure
|
+-- Step 2: strip_publish_annotations.py books/<slug>/
|         Writes exports/clean/ch-NN.md (HTML-comment-stripped)
|
+-- Step 3: deterministic generation (no LLM)
|   +-- exports/toc.md     <- outline.md + chapter H2 scan
|   +-- exports/glossary.md <- bible.md §Terminology projection
|   +-- exports/index.md    <- chapter term-frequency lookup
|   +-- exports/manifest.json <- copy of frozen-lines.json
|
+-- Step 4: LLM pass (separate am-design dispatch)
|   +-- exports/preface.md  <- intake + outline + bible; 350-500 words
|
+-- Step 5: exports/README.md (T10 template)
```

## Two-track generation (deterministic + LLM)

| Deliverable | Method | Why |
|---|---|---|
| `clean/ch-NN.md` | `strip_publish_annotations.py` (T3) | Pure regex strip; deterministic. |
| `toc.md` | **Deterministic** - outline + first H2 of each chapter | TOC is structural; LLM would invent page numbers and miss terms. |
| `glossary.md` | **Deterministic** - `bible.md` `## Terminology` projection, A-Z sorted, with `introduced in ch-NN` anchors | Glossary = bible projection; no prose. |
| `index.md` | **Deterministic** - chapter-term-occurrence scan | Index = term-frequency lookup. |
| `preface.md` | **LLM pass** - master dispatches am-design with intake + outline + bible | Preface has voice; needs the same style-guide lens as chapters. |
| `exports/README.md` | **Deterministic** - T10 template + build metadata | README is metadata. |

## Why LLM only for preface

Preface is the only deliverable that requires voice — it's the part the reader reads first, and where the author's stance has to land. TOC, glossary, index are mechanical lookups; an LLM would hallucinate page numbers and miss terms.

Splitting deterministic-vs-LLM this way makes the script testable: `book_check.py` can verify a deterministic TOC by re-running it and comparing.

## Failure modes

| Failure | Detection | Handling |
|---|---|---|
| `book_check.py` fails (exit != 0) | exit code | Abort `build_exports.py` before any file is written |
| `strip_publish_annotations.py` finds nothing to strip | (chapters already clean) | Log "no-op"; still considered pass |
| am-design preface fails `book_check.py` | exit code != 0 | Re-dispatch am-design once with the failure report; on second failure surface to user |
| `frozen-lines.json` missing | `book_check.py` already failed on this | Abort at step 1 |
| `outline.md` missing chapters | regex scan returns empty | Log warning, write empty TOC section, surface to user |

## Idempotence

`build_exports.py` is re-runnable. It overwrites `exports/` contents in place.

- TOC / glossary / index outputs are deterministic — re-runs produce identical bytes.
- Preface is LLM-generated — re-runs may produce different prose. Acceptable for a preface (revisions are expected).

## Output schema

```
books/<slug>/
+-- exports/
    +-- README.md          <- build metadata, deliverables list
    +-- manifest.json      <- frozen-lines archive
    +-- toc.md             <- Table of Contents (page numbers TBD)
    +-- preface.md         <- Author's preface (LLM pass)
    +-- glossary.md        <- Bible terminology projection
    +-- index.md           <- Term/character occurrence index
    +-- clean/
        +-- ch-01.md       <- Annotation-stripped
        +-- ch-02.md
        +-- ...
```

## Open questions

- Should `build_exports.py` also produce PDF / ePub via the `make-pdf` skill? -> opt-in, off by default. Add `--with-pdf` flag.
- Should TOC include page numbers? -> yes, but as `<!-- PAGE TBD -->` placeholders. PDF build (if invoked) replaces placeholders with actual numbers.
- Is there a maximum chapter count for glossary projection? -> no, the script streams.
