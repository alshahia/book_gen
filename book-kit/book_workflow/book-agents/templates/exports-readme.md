---
template: exports-readme
purpose: Document deterministic export contents, regeneration, and provenance.
phase: back-matter
consumers: [build_exports.py, readers, am-review]
---

# Exports

Build date: <deterministic local build>

Chapters: <count>

Total words: <count>

> Preface requires separate am-design dispatch (LLM pass).

## Deliverables

- `book.md` — assembled Markdown manuscript.
- `toc.md` — deterministic navigation and section index.
- `glossary.md` — terminology projected from the book bible.
- `README.md` — build inventory and provenance.

## Regeneration

```sh
python3 build_exports.py books/<slug>/
```

## Provenance

- Chapter source path: `books/<slug>/chapters/`
- `frozen-lines.json` SHA256: `<sha256>`

## Open questions

1. Which additional export formats are enabled?
2. Is the preface approved and available for assembly?
3. Which local build identifier should replace the deterministic placeholder?
