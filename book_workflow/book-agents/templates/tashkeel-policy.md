---
template: tashkeel-policy
purpose: Lock Arabic-diacritic targets before chapter drafting and validation.
phase: policy
consumers: [book_check.py, book-writer, am-review, master]
---

# Tashkeel (تشكيل) Policy

## Per-chapter targets

| chapter | target-ratio | tolerance | rationale |
|---|---:|---:|---|
| ch-NN | [0.000–1.000] | [± ratio] | [why] |

## Measurement

`book_check.py` measures each chapter as:

`Arabic combining marks ÷ Arabic base characters`

- Numerator: Arabic combining marks recognized by the checker.
- Denominator: Arabic-script base characters recognized by the checker.
- Compare the measured ratio with the chapter target and tolerance above.

## Examples

Worked example: [city-of-memories](../../../../books/city-of-memories/) — chapter ratios `0.015`, `0.060`, `0.153`, `0.138`, `0.135`.

## Phase 3 decision

This template MUST be filled at Phase 3 (outline confirmation). Default: leave unvocalized unless user explicitly asks for partial/full vocalization. NO ACCIDENTAL SPLIT allowed.

## Refusal rule

If you discover mid-Phases 5-6 that some chapters are vocalized and others aren't, STOP and surface to master — this is a Phase-3 failure.

## Open questions

1. Does the user want unvocalized, partial, or full vocalization?
2. Should targets be uniform or chapter-specific?
3. What tolerance should `book_check.py` enforce?
