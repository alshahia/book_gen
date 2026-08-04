---
template: preface
purpose: Define the LLM contract for generating book front-matter prose.
phase: front-matter
consumers: [am-design, book_check.py, build_exports.py]
---

## Inputs the LLM must consume

- [intake.md](./intake.md): audience, goal, category, and definition of done.
- [outline.md](./outline.md): chapter promise and progression.
- [bible.md](./bible.md): established terminology, facts, characters, and continuity.

## Output structure

# Preface

[Why this book exists and what journey it offers.]

## Who this is for

[Name the intended reader and useful prior knowledge.]

## How to read this book

[Explain sequence, selective reading, and exercises or conventions.]

## What this book is not

[Set concise scope and expectation boundaries.]

## Voice constraints

- Follow [style-guide.md](./style-guide.md) §Voice.
- Follow [style-guide.md](./style-guide.md) §Presentation.
- Do not introduce claims, terms, or characters absent from the inputs.

## Length target

350–500 words total.

## Gate

`book_check.py` must exit 0 against the produced preface before export.

## Open questions

1. Should the preface be signed or dated?
2. Is first-person author voice allowed?
3. Are spoilers or chapter-specific promises permitted?
