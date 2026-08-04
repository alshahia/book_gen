---
template: glossary
purpose: Define the deterministic glossary projection from the book bible.
phase: back-matter
consumers: [build_exports.py, am-review]
---

# Glossary

## Source

Project [bible.md](./bible.md) §Terminology.

## Format

- **term** — definition. (Introduced ch-NN.)

## Sort order

- Default: alphabetical by normalized term.
- Arabic: Arabic-aware order — ا ب ت ث ج ح خ د ذ ر ز س ش ص ض ط ظ ع غ ف ق ك ل م ن ه و ي.

## Generation rule

Deterministic projection from `bible.md`. If `## Terminology` is absent or empty, emit: `[No glossary terms recorded.]`

<!-- ponytail: definitions stay canonical in bible.md; this file only projects them. -->

## Open questions

1. Should English articles be ignored during sorting?
2. How should mixed Arabic–Latin terms be ordered?
3. Should aliases cross-reference the canonical term?
