---
template: toc
purpose: Define the deterministic table-of-contents export.
phase: front-matter
consumers: [build_exports.py, am-review]
---

# Table of Contents

[Two or three lines describing the book once; do not repeat chapter summaries.]

## Chapters

- [Chapter NN: Title](chapters/ch-NN.md)
  - [First H2 section title]

## Front matter

- [Preface](preface.md)
- [How to read this book](preface.md#how-to-read-this-book)

## Back matter

- [Glossary](glossary.md)
- [Index](index.md)

## Generation rule

Deterministic. Re-running `build_exports.py` produces identical bytes. Page numbers are `<!-- PAGE TBD -->` placeholders filled at PDF-build time.

## Open questions

1. Should appendices appear under Back matter?
2. Should chapters without an H2 omit the nested item?
3. Which export formats require page placeholders?
