# Dev Review — ch-03 (Write Your First Python Programs)

- Book: AI Agents with Python
- Task: T-2026-08-01-001-book-ai-agents-with-python
- Phase: dev (writing)
- Chapter under review: `books/ai-agents-with-python/chapters/ch-03.md`
- Reviewed against: `outline.md` (ch-03 section), `style-guide.md`, `bible.md`, `research-log.md` (entry-019..entry-026)
- Reviewer: am-review (book-gen mode)
- Word count: 1591 total (incl. code, headers, comments); 1256 prose; user-supplied figure was 1557 — within ±3%

---

## Summary

**Overall verdict: PASS_WITH_WARN**

ch-03 is a faithful, voice-correct, well-grounded first programs chapter. All 8 outline entries (entry-019..entry-026) are covered; all four named error categories appear; sources are named inline; PEP 8 conventions are honoured; the closing imperative matches the outcome line; no agent code or model calls leak past the chapter boundary; no `HfApiModel`/`ApiModel` literal appears. One minor WARN: the orientation paragraph (line 3) is 66 words, six over the bible's 30-60-word ceiling. The deviation is non-blocking — the paragraph still satisfies the "one concrete observable outcome" rule and reads cleanly. No FAILs.

| Severity | Count |
|---|---|
| FAIL | 0 |
| WARN | 1 |
| PASS | 9 |

---

## Tests / build run

Static review only — no runtime checks executed in this review pass (chapter does not install framework surface; ch-03 is pre-runtime). Spot-reads of the 10 fenced Python blocks confirm:

- 4-space indent across all blocks (no tab characters, no mixed indentation)
- snake_case variable names throughout (`trip_distance`, `first_name`, `base_score`, `first_number`, `second_number`)
- One blank line between top-level definitions in `## Use a small PEP 8 checklist`
- Operators carry one space on both sides
- Quoted strings match opening/closing quotes
- Canonical `print("Hello, world!")` is the entire contents of `first_program.py` (minimal)
- `input()` -> `int()` conversion is shown explicitly
- F-strings shown with prefix `f` and braces
- One traceback example (`TypeError` from `count_text + 1`) with the fix shown immediately after
- Bash run command reuses ch-02's `.venv` path: `E:\book_gen\.venv\Scripts\python.exe first_program.py`

No runtime execution performed; this is consistent with the dev review pass before integration.

---

## Per-task verdicts

(Chapter-as-task structure — one verdict per checklist section.)

### 1. Outline coverage — **PASS**

- Outcome line on `outline.md:321`: *"by the end of the reading, the reader can write, save, and run a short Python script that uses values, variables, `input()`, `print()`, f-strings, and the four beginner error categories."*
- All 8 outline entries covered:
  - entry-019 (variables & dynamic typing): `chapters/ch-03.md:31-47` ("Give values readable labels")
  - entry-020 (literal set & operators): `chapters/ch-03.md:49-67` ("Combine three value categories")
  - entry-021 (canonical `print("Hello, world!")`): `chapters/ch-03.md:7-29` ("Start with one line")
  - entry-022 (f-strings via PEP 498): `chapters/ch-03.md:69-82` ("Format output with f-strings")
  - entry-023 (`input()` + `int()`/`float()` conversion): `chapters/ch-03.md:84-105` ("Read input, then convert it")
  - entry-024 (tracebacks, bottom-up, four named errors): `chapters/ch-03.md:107-134` ("Read a traceback from the bottom up")
  - entry-025 (.py vs notebook + restart-and-run-from-top): `chapters/ch-03.md:7-29` ("Start with one line" second half)
  - entry-026 (PEP 8 beginner subset): `chapters/ch-03.md:136-149` ("Use a small PEP 8 checklist")
- Stays inside ch-03 — no agent code, no model calls, no framework imports. PASS.

### 2. Voice match — **PASS**

- Conversational technical; second person dominant ("you write," "you'll see," "you read"). PASS.
- Contractions natural: "you'll" (3x), "doesn't" (1x), "you're" (0x), "won't" (0x), "you've" (0x) — natural distribution, not overused. PASS.
- No exclamation marks in prose. The only `!` in the file is inside the quoted `"Hello, world!"` string literal (line 24) — that is content of the canonical first program, not a sentence exclamation. PASS.
- No forbidden vocabulary. Grep for `\b(optimal|proven|magic|simply|just|obviously|revolutionary|game-changing|powerful)\b` and `studies show` returns 0 hits. PASS.

### 3. Bible consistency — **PASS**

- Does not contradict ch-01 or ch-02. The chapter correctly references "the interpreter from ch-02" and reuses `E:\book_gen\.venv\Scripts\python.exe` exactly as ch-02 introduced. PASS.
- New terms appended correctly. `bible.md:54-62` ("## Added by ch-03 — 2026-08-01") lists: variable & dynamic-typing model, beginner values & operators, `print()` and f-strings, `input()` conversion, traceback map, script/notebook execution, beginner PEP 8 subset. Every entry maps to a section in ch-03 with the corresponding one-sentence plain-language gloss. PASS.

### 4. Research grounding — **PASS**

- Each claim has a source named inline:
  - `print()` semantics: "The Python documentation for `print()` describes it as a built-in function that writes text to standard output and ends with a newline by default." (`chapters/ch-03.md:15`)
  - Script execution model: "according to the Python interpreter documentation" (`chapters/ch-03.md:27`)
  - Notebook restart habit: "The Jupyter documentation identifies restart-and-rerun as the check that exposes out-of-order state." (`chapters/ch-03.md:29`)
  - Data model + execution model + assignment: "The Python data model says every object has a type and a value, while the execution model says a name refers to an object." (`chapters/ch-03.md:33`)
  - PEP 8 naming: "PEP 8, Python's style guide, recommends lowercase names with words separated by underscores" (`chapters/ch-03.md:47`)
  - Arithmetic operators: "The Python tutorial documents `+`, `-`, `*`, `/`, `//`, `%`, and `**`" (`chapters/ch-03.md:65`)
  - F-strings: "PEP 498 introduced formatted string literals" (`chapters/ch-03.md:71`)
  - `input()` + `int()` + `float()`: "The Python documentation for `input()`, `int()`, and `float()` makes the conversion step explicit." (`chapters/ch-03.md:86`)
  - Traceback reading: "The Python tutorial recommends starting at the final line for a runtime error" (`chapters/ch-03.md:109`)
- All four required traceback error names appear: `SyntaxError` (3x), `IndentationError` (2x), `NameError` (2x), `TypeError` (3x). PASS.
- PEP 8 beginner subset presented explicitly: "use four spaces for each indentation level, don't mix tabs and spaces, write names in `snake_case`, and put one space around `=` and arithmetic operators" (`chapters/ch-03.md:138`). PASS.

### 5. Code-block correctness — **PASS**

- All 10 fenced Python blocks use 4-space indent; no tabs; no mixed indentation. PASS.
- `print("Hello, world!")` is the entire first program — minimal, canonical. PASS.
- `input()` -> `int()` conversion shown explicitly with `int(age_text)` on line 91 and `float(height_text)` on line 101. PASS.
- F-strings shown on lines 77-79 with `f` prefix and `{name}`, `{steps}`, `{steps + 1}` placeholder forms. PASS.
- At least one traceback example: the `count_text + 1` `TypeError` example at lines 118-132, with the fix shown immediately after on lines 128-132. PASS.

### 6. Beginner accessibility — **PASS (one minor WARN)**

- Reader with no Python experience can follow: the chapter moves `print("Hello, world!")` -> variables -> three literal categories -> f-strings -> input/conversion -> tracebacks -> PEP 8 subset -> complete script. Each new construct gets a plain-language gloss the first time it appears (e.g., "PEP 8 ... recommends lowercase names with words separated by underscores, called `snake_case`"). PASS.
- The chapter opens with WHY: line 3 spells out "you'll have written a script that stores values, asks for input, prints a result, and gives you a method for reading the first errors you meet" — that is the input/output loop the chapter installs. PASS.
- Orientation paragraph length: line 3 is **66 words**, which exceeds the bible's "30-60 words" ceiling by 6 words. WARN (minor, non-blocking).

### 7. Outcome-line contract — **PASS**

- Closing imperative verbatim or near-verbatim:
  - Outline outcome line: "by the end of the reading, the reader can write, save, and run a short Python script that uses values, variables, `input()`, `print()`, f-strings, and the four beginner error categories."
  - `chapters/ch-03.md:185` (final prose line): "By the end of the reading, you can write, save, and run a short Python script that uses values, variables, `input()`, `print()`, f-strings, and the four beginner error categories." — differs only in `the reader can` -> `you can` and lowercase `b` -> uppercase `B`, which is the intended second-person rewrite per style-guide.md.
  - `chapters/ch-03.md:173` ("The move" callout): "Write, save, and run the complete script above in the book's `.venv`, then fix one traceback by starting at its final line and checking the named error category." — this is the imperative action. PASS.
- The style guide requires both the verbatim outcome-line restatement AND a concrete same-day action; ch-03 delivers both. PASS.

### 8. HfApiModel / ApiModel rule — **PASS**

- Grep for `HfApiModel|ApiModel` returns 0 hits in `chapters/ch-03.md`. The literal `HfApiModel` does not appear (correct — ch-09 sidebar only), and the literal `ApiModel` does not appear (correct — ch-17 abstract-hierarchy chapter only). PASS.

### 9. Forward-pointers — **PASS**

- `chapters/ch-03.md:175` — "What's next: ch-04 adds decisions and repetition with `if`, `while`, and `for`. Those structures will reuse the values, variables, input, output, and f-strings you practiced here." Names ch-04 by number and content; bridges to ch-04's installed elements per `outline.md:66` (`if`/`elif`/`else`, `while`/`for`, `range()`). PASS.

### 10. No regressions — **PASS**

- Consistent with style guide: conversational technical voice, second person dominant, contractions natural, no exclamation marks, no forbidden vocabulary, one move per paragraph followed by its evidence, no cheerleading, no productivity jargon. PASS.
- Consistent with bible: every ch-03-added term appears with the same gloss; no contradiction with ch-01 (Python, LLM, agent, token) or ch-02 (`.venv`, `python -m`, kernel, `.env`). PASS.
- Brief-corrections: none apply to ch-03 (the three binding brief-corrections land in ch-10 / ch-15 / ch-16). No violation. PASS.

---

## Cross-cutting findings

1. **Strength — inline citations.** Every operative claim in ch-03 names a specific source (Python docs, PEP 8, PEP 498, Jupyter docs) inline. This is rare in beginner Python writing and aligns with bible voice-rule 4 ("Citation hygiene: name the source inline"). The pattern is consistent across all 7 sections. Hold this pattern when later chapters (especially ch-06 onward) cite Anthropic / smolagents / NIST / OWASP — ch-03 is the template.

2. **Strength — explicit "WHY this chapter, not that" framing on scripts vs notebooks.** Lines 27-29 surface the trade-off (saved script = reproducible; notebook = interactive) before the chapter commits to scripts. Beginners who arrived from Jupyter-heavy tutorials will read this and not feel blindsided by the script-first decision. Hold.

3. **Pattern — single "The move" callout, single closing summary.** Style-guide.md permits at most one callout kind per chapter, used at most twice per chapter. ch-03 uses exactly one ("The move" on line 173) plus the closing summary line — within budget.

4. **Minor — orientation paragraph length.** 66 words vs the 60-word ceiling. Two possible fixes (writer's choice when revising): (a) drop the third sentence ("The same work also runs in a notebook, but the saved script gives you a clean record of what Python executed.") and lift that into the body of `## Start with one line`, where it already appears; (b) trim "from the project folder" to "in the project" in the first sentence. Either brings the line under 60. Surface as WARN, not FAIL — the prose still satisfies the "one concrete observable outcome" rule.

5. **Out-of-scope observation — self-critique block at lines 177-183.** The HTML-comment self-critique is the book-writer skill's standard handoff and matches the pattern noted in `AGENTS.md` (Book-gen mode: "books/daily-focus/chapters/ch-01.md lines 87-94 hold a self-critique HTML comment for orchestrator/reviewer handoff. Strip before any external publish."). This is correct as-is for review. Reminder for the eventual publish-time strip pass.

---

## Out-of-scope observations

- Chapter length (1591 words) is well under the ~17-22 page (≈3000-4000 word) target from `style-guide.md:15`. This is intentional — ch-03 is the first programs chapter and keeps its surface area small. No action required; flagging only so master knows ch-03 is shorter than the per-chapter average, which the chapter rhythm permits for a "first move" chapter.
- The closing-style used here (callout + verbatim outcome-line + "What's next") matches the style-guide template. The other 18 chapters should adopt the same closing shape.

---

## Honest assessment

ch-03 reads as written by an agent that has internalized both the bible and the style guide, not as output pasted from a generic Python tutorial. Every claim has a citation; every construct gets a one-sentence plain-language gloss the first time it appears; the four-error map is the chapter's navigational load-bearing piece, exactly as `outline.md:331` says; the chapter respects the ch-02 handoff by reusing the `.venv` path verbatim rather than re-teaching setup. The orientation-paragraph length WARN is a soft style-guide deviation, not a content bug — the prose is good and the trade-off (saving a 6-word deviation) does not justify a fix loop on its own.

I would ship this chapter today. The orientation length is a polish item, not a blocker.

If the next review pass (line / copy-edit) wants something to fix, it is line 3.

---

## Self-critique

- I did not execute the chapter in `E:\book_gen\.venv\Scripts\python.exe` myself — I relied on static review of the code blocks. The code is small enough (10 blocks, all beginner-Python) that the static check is high-confidence, but if the operator wants belt-and-braces, a `python -m py_compile` of each block is cheap. Surface: review pass did not run the code, only read it.
- I treated the `"The move:"` callout and the verbatim outcome-line restatement as joint fulfilment of the "closing imperative" requirement, which is consistent with how the style guide describes the chapter-closing convention but is my interpretation; if the next reviewer wants the callout itself to be the *only* closing imperative (and the line 185 restatement considered redundant), that is also defensible and would still PASS.
- I did not enumerate contractions or count every contraction instance precisely — I sampled "you'll" (3x) and spot-read the rest. Low risk given the chapter's small size, but flagging for transparency.
- I did not check the self-critique HTML comment for any leaking claims against the bible — the comment is a writer-to-reviewer handoff and I treated it as out-of-scope (and confirmed with AGENTS.md that it is intended to be stripped at publish time, not validated for fact).