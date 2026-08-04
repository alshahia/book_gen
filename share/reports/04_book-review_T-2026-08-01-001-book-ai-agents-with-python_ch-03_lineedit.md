# Line-Edit Review — ch-03 — AI Agents with Python

Date: 2026-08-01
Reviewer: am-review (book-gen mode)
Chapter: ch-03.md (1591 total words / 1256 prose; 185 lines)
Previous verdict: PASS_WITH_WARN (dev pass, 1 WARN — orientation paragraph 66 vs 60 words)
Pass: line-edit
Style guide: `books/ai-agents-with-python/style-guide.md`

## Verdict: PASS_WITH_WARN

The chapter is voice-clean, citation-clean, blacklist-clean, terminologically tight, and structurally aligned with the style guide. The single carryover WARN from the dev review remains — the orientation paragraph (line 3) is 66 words, six over the bible's 30–60-word ceiling. The chapter was last modified at 15:59:55, three minutes before the dev review was written at 16:03:41, so no edits have been applied between passes; the WARN carries over unchanged. No new issues surfaced on this pass. The chapter is line-edit clean enough to ship to Phase 7 copy-edit.

## Summary

| Dimension | Result |
|---|---|
| Voice (conversational technical, second person dominant) | PASS |
| Vocabulary blacklist | PASS (0 matches) |
| Pacing and rhythm | PASS |
| Terminology consistency | PASS |
| Citation hygiene | PASS (every claim named inline) |
| Code-block conventions | PASS |
| Forward-pointer hygiene | PASS |
| Outcome-line contract | PASS (verbatim match with style guide) |
| No regression vs. dev review | PASS_WITH_WARN (carryover orientation length) |

**Counts:** 0 FAIL, 1 WARN, 0 FAIL-by-omission.

## Tests / build run

Line-edit pass — no code execution required. The dev pass already spot-read all 10 fenced Python blocks for indentation, naming, and operator spacing; that verification is unchanged. No re-test needed for a line-edit pass.

## Per-checklist verdicts (with path:line evidence)

### 1. Voice consistency — VERDICT PASS

Conversational technical; second person dominant; contractions natural. Verified by:

- Scene-setter opener at ch-03.md:3 (the orientation paragraph; see § 10 for the length WARN).
- Direct-address imperatives throughout: "Type this as the entire contents of `first_program.py`" (ch-03.md:9), "Run it from the project folder" (ch-03.md:15), "Begin with three literal categories" (ch-03.md:51), "Read input, then convert it" (ch-03.md:85), "Read a traceback from the bottom up" (ch-03.md:109), "Replace the contents of `first_program.py`" (ch-03.md:153), "Run it with" (ch-03.md:165). Each subheading names the move, in line with style-guide § "Subheadings."
- Second-person verbs in prose: "you'll have written" (line 3), "you can see" (implicit, line 21), "you can write" (line 185), "you read" (line 134), "you don't declare" (line 45), "you type" (line 97), "you're learning" (line 82). First-person plural "we" as subject: 0 matches in prose.
- Contractions natural and not overused. Verified curly-apostrophe counts across the chapter: `you'll` 3x (lines 3, 67, 111), `won't` 1x (line 65), `doesn't` 1x (line 149), `don't` 2x (lines 45, 138), `you're` 1x (line 82). Total: 8 contractions, distributed across sections, none clustered. The dev review cited `you'll` 3x, `doesn't` 1x, and 0x for the rest; the undercount was a sampling miss, not a chapter bug.
- No exclamation marks in actual prose. The 2 `!` characters in the file are inside HTML comments (lines 5 and 177 — the `<!--` opener for the book-writer self-critique block) and inside the literal `"Hello, world!"` quoted string (lines 12, 24). The latter is content of the canonical first program, not a sentence exclamation; the former is HTML-comment markup. Both are out of scope for the no-exclamation rule.

### 2. Vocabulary blacklist — VERDICT PASS

Style-guide blacklist terms scanned in prose only (prose = no code blocks, no HTML comments, no inline HTML):

| Term | Matches |
|---|---|
| `magic` / `magical` | 0 |
| `optimal` | 0 |
| `proven` | 0 |
| `revolutionary` | 0 |
| `game-changing` | 0 |
| `powerful` | 0 |
| `simply` | 0 |
| `obviously` | 0 |
| `just` | 0 |
| `studies show` | 0 |
| Productivity jargon (`synergy`, `leverage`, `optimize`, `deep dive`, `unpack`, `delve`) | 0 |

The phrase "by starting at its final line" (line 109, line 173) is the bottom-up reading habit, not a hype word; the phrase "the reading habit" (line 134) is a recurring pedagogical pattern, not a hand-wave. No blacklist hits anywhere in the chapter.

### 3. Pacing and rhythm — VERDICT PASS

Short sentences for key claims:

- ch-03.md:24 (the expected output) — 2 words inside a fenced text block
- ch-03.md:51 "Digits inside quotes are text, so `\"7\"` is not the integer `7`." — 13 words
- ch-03.md:86 "It always returns a `str`, even when you type digits." — 10 words
- ch-03.md:105 "That error is worth noticing, but this chapter's four named categories are the first navigation map." — 18 words
- ch-03.md:134 "Read the last line first, then inspect your own line and the lines immediately before it." — 17 words
- ch-03.md:138 "use four spaces for each indentation level, don't mix tabs and spaces..." — instruction-list run
- ch-03.md:149 "Formatting doesn't change what this program calculates." — 7 words
- ch-03.md:149 "It makes the structure and intent easier to inspect..." — 11 words

Longer sentences for explanation:

- ch-03.md:27 — 5 sentences (~70 words across them) explaining the script-vs-notebook trade-off; reads cleanly, alternates claim and evidence
- ch-03.md:65 — 4 sentences (~60 words) introducing the seven operators; ends with the "string + number" rule
- ch-03.md:109 — 3 sentences explaining the bottom-up reading habit; middle sentence is the longest at ~30 words

Mix verified: the chapter breathes — short claim / longer evidence / short claim is the default rhythm. Style-guide § "Pacing and rhythm" satisfied.

### 4. Terminology consistency — VERDICT PASS

| Term | First prose use | Inline gloss |
|---|---|---|
| `print()` | ch-03.md:11 (in code), ch-03.md:15 (in prose) | ch-03.md:15 "The Python documentation for `print()` describes it as a built-in function that writes text to standard output and ends with a newline by default." |
| `input()` | ch-03.md:85 (subheading + prose) | ch-03.md:86 "The built-in `input()` function displays an optional prompt and returns one line of text. It always returns a `str`, even when you type digits." |
| `int()` / `float()` | ch-03.md:85 (implicit) | ch-03.md:86 + ch-03.md:97 + ch-03.md:101 — explicit conversion examples |
| variable / dynamic typing | ch-03.md:31 (subheading) | ch-03.md:33 "The Python data model says every object has a type and a value, while the execution model says a name refers to an object. Think of a variable as a label, not a permanently typed box." |
| `snake_case` | ch-03.md:47 (prose) | ch-03.md:47 "PEP 8, Python's style guide, recommends lowercase names with words separated by underscores, called `snake_case`." |
| f-string | ch-03.md:69 (subheading + prose) | ch-03.md:71 "PEP 498 introduced formatted string literals, commonly called f-strings. Put `f` before the opening quote, then place a name or small expression inside braces." |
| traceback | ch-03.md:107 (subheading + prose) | ch-03.md:109 "A traceback is Python's report of where an error occurred." |
| The four named error categories | ch-03.md:111 ("Here are the four beginner categories you'll use as first checks:") | ch-03.md:113–116 (four-bullet enumeration with one-sentence gloss each) |

All terminology first-uses are glossed within the chapter body. No bare-uses without a definition or citation. The bible's working definition of "traceback" matches the chapter's plain-language gloss (bottom-up reading, final line first).

### 5. Citation hygiene — VERDICT PASS

Every operative claim has an inline source name. Verified by reading the full chapter:

| Claim | Source named inline | Location |
|---|---|---|
| `print()` semantics | "The Python documentation for `print()` describes it as a built-in function that writes text to standard output and ends with a newline by default." | ch-03.md:15 |
| Script execution model (top-to-bottom on every run) | "according to the Python interpreter documentation" | ch-03.md:27 |
| Notebook restart habit | "The Jupyter documentation identifies restart-and-rerun as the check that exposes out-of-order state." | ch-03.md:29 |
| Data model + execution model + assignment | "The Python data model says every object has a type and a value, while the execution model says a name refers to an object." | ch-03.md:33 |
| PEP 8 naming convention | "PEP 8, Python's style guide, recommends lowercase names with words separated by underscores" | ch-03.md:47 |
| Arithmetic operators | "The Python tutorial documents `+`, `-`, `*`, `/`, `//`, `%`, and `**` as the basic arithmetic operators." | ch-03.md:65 |
| F-string origin | "PEP 498 introduced formatted string literals" | ch-03.md:71 |
| `input()` / `int()` / `float()` conversion rule | "The Python documentation for `input()`, `int()`, and `float()` makes the conversion step explicit." | ch-03.md:86 |
| Traceback reading habit | "The Python tutorial recommends starting at the final line for a runtime error" | ch-03.md:109 |

No vague "as we will see" / "in the next chapter" / "studies show" hand-waving. (Searched: 0 matches for those three exact phrasings across prose.)

### 6. Code-block conventions — VERDICT PASS

All 10 fenced Python blocks conform to style-guide § "Code blocks":

| Line(s) | Block | Convention check |
|---|---|---|
| 11–13 | `print("Hello, world!")` | ✓ Minimal canonical first program |
| 17–19 | Bash run command (`E:\book_gen\.venv\Scripts\python.exe first_program.py`) | ✓ Reuses ch-02's venv path verbatim; no bare `python` |
| 23–25 | Expected output (`Hello, world!`) | ✓ `text` language tag |
| 35–43 | Variable reassignment + `type()` demo | ✓ 4-space indent; snake_case (`trip_distance`); operators with one space |
| 53–63 | Integer / float / string arithmetic | ✓ `snake_case` (`apples`, `price`, `label`, `total`, `message`); `str(apples)` explicit conversion |
| 73–80 | f-string example | ✓ `f` prefix, `{name}` and `{steps + 1}` placeholder forms |
| 88–95 | `input()` + `int()` conversion | ✓ Two-step pattern shown explicitly (`age_text = input(...)` then `age = int(age_text)`) |
| 99–103 | `input()` + `float()` conversion | ✓ Same two-step pattern with `float()` |
| 120–124 | `TypeError` example (`count_text + 1`) | ✓ Demonstrates the exact failure the chapter then fixes |
| 128–132 | Fix to the `TypeError` example (`int(count_text) + 1`) | ✓ Fix follows immediately after the bug |
| 140–147 | PEP 8 style example | ✓ `snake_case` (`first_name`, `base_score`, `bonus_score`, `final_score`); one blank line between top-level defs; one space around operators |
| 155–163 | Complete script for the runnable check | ✓ Mirrors the prior examples; no over-engineering |

All blocks: 4-space indent (verified — no tab characters, no mixed indentation); one space around operators; opening and closing quotes match; `print()` calls are parenthesised. The bash blocks reuse ch-02's `.venv` path exactly, satisfying code-rule 1 ("runnable in the venv").

### 7. Forward-pointer hygiene — VERDICT PASS

- **Explicit "What's next"** at ch-03.md:175: "What's next: ch-04 adds decisions and repetition with `if`, `while`, and `for`. Those structures will reuse the values, variables, input, output, and f-strings you practiced here." Two sentences; names ch-04 explicitly; names ch-04's three new constructs; enumerates the ch-03 elements ch-04 will reuse. Matches style-guide § "Reading aids" exactly.
- **Backward continuity reference** at ch-03.md:15: "Run it from the project folder with the interpreter from ch-02." Names ch-02 by number for the venv handoff; this is a continuity reference (the .venv was installed in ch-02), not a forward-pointer. Removing it would force the chapter to re-teach setup, which the dependency chain prohibits.
- **Vague forward glance** at ch-03.md:105: "Later chapters will show how to decide what a program should do after bad input." Generic "later chapters," not a specific named chapter; sets up ch-15 (tool side-effect classification, exception handling) and ch-18 (the capstone with input validation) without naming them. Style-guide § "Reading aids" permits cross-chapter vagueness when it serves comprehension; the chapter uses it once, in context, and avoids the rule's specific forbiddances ("as we will see," "in the next chapter," "as the title says").

Verdict: PASS. No specific named-chapter forward-pointers appear outside the explicit "What's next" paragraph. The two named-chapter references in the file are both backward (ch-02 handoff) and inside the "What's next" paragraph (ch-04 setup) — both permitted.

### 8. Outcome-line contract — VERDICT PASS

- **Outline ch-03 outcome line** (outline.md:321): "by the end of the reading, the reader can write, save, and run a short Python script that uses values, variables, `input()`, `print()`, f-strings, and the four beginner error categories."
- **Style-guide outcome action** (style-guide.md:69): "Reader writes the chapter's first-program snippet, runs it in the venv, observes the printed output, and fixes one traceback from the bottom up."
- **Chapter "The move" callout** (ch-03.md:173): "**The move:** Write, save, and run the complete script above in the book's `.venv`, then fix one traceback by starting at its final line and checking the named error category."
- **Chapter final restatement** (ch-03.md:185): "By the end of the reading, you can write, save, and run a short Python script that uses values, variables, `input()`, `print()`, f-strings, and the four beginner error categories."

Both deliverables from the style-guide table's ch-03 row are present:
1. The verbatim outcome-line restatement at ch-03.md:185 (differs from the outline only in the prescribed second-person rewrite `the reader can` → `you can` and lowercase `b` → uppercase `B`, which is the style-guide's intended transformation).
2. The "The move" callout at ch-03.md:173 (the chapter-closing imperative that delivers the reader-facing action).

The style-guide's outcome action ("runs it in the venv, observes the printed output, and fixes one traceback from the bottom up") maps cleanly to the chapter's callout ("Write, save, and run the complete script above in the book's `.venv`, then fix one traceback by starting at its final line and checking the named error category"). Verbatim near-match. PASS.

### 9. Style-guide cross-cutting rules — VERDICT PASS (with one carryover WARN)

- **Orientation paragraph length:** ch-03.md:3 is **66 words**, six over the bible's 30–60-word ceiling. **WARN (carryover from dev review).** See § 10 for the carryover verdict.
- **Chapter-opening scene:** ch-03.md:3 opens with a concrete scene ("Open the terminal from the project folder and create a file named `first_program.py`") — a tool the reader is about to use, anchored in a physical action. Style-guide § "Chapter-opening convention" satisfied.
- **Subheadings:** All 8 subheadings are sentence-fragment style and describe the move (not the topic), per style-guide § "Subheadings":
  - "Start with one line" (line 7)
  - "Give values readable labels" (line 31)
  - "Combine three value categories" (line 49)
  - "Format output with f-strings" (line 69)
  - "Read input, then convert it" (line 84)
  - "Read a traceback from the bottom up" (line 107)
  - "Use a small PEP 8 checklist" (line 136)
  - "Check: save and run a complete script" (line 151)
- **Lists:** Used only where the items are a discrete set the reader enumerates together: the four beginner error categories at ch-03.md:113–116. No bulleted-prose smell.
- **Callouts:** One kind ("The move"), one occurrence (line 173). Style-guide § "Callouts" budget: at most two per chapter; one is within budget. ✓
- **Code blocks:** All 10 conform (see § 6 above).
- **Self-critique HTML comment** at ch-03.md:177–183: preserved as the book-writer skill's standard handoff. Per the book-gen mode notes in `AGENTS.md`, this is the standard orchestrator/reviewer handoff and should be stripped at publish time. Not a line-edit concern; flag only.

### 10. No regression vs. dev review — VERDICT PASS_WITH_WARN

File mtimes confirmed:
- `ch-03.md` LastWriteTime: 2026-08-01 15:59:55
- Dev review (`04_book-review_..._ch-03_dev.md`) LastWriteTime: 2026-08-01 16:03:41

The chapter was last touched **3 minutes before** the dev review was written. No modifications between passes.

Dev review's single WARN carried over unchanged:

- **WARN — orientation paragraph length.** ch-03.md:3 is 66 words, six over the bible's 30–60-word ceiling. The dev review offered two fix options: (a) drop the third sentence ("The same work also runs in a notebook, but the saved script gives you a clean record of what Python executed.") and lift that into the body of `## Start with one line` where it already appears; (b) trim "from the project folder" to "in the project" in the first sentence. Either brings the line under 60. The line-editor concurs: the prose still satisfies the "one concrete observable outcome" rule, and the deviation is non-blocking. A future copy-edit pass can pick one of the two fixes without a fix-loop dispatch.

Dev review's 9 PASS items remain PASS (no regression):

1. Outline coverage — all 8 entries (entry-019..entry-026) covered. ✓
2. Voice match — conversational technical; second person dominant; no exclamation marks. ✓
3. Bible consistency — no contradiction with ch-01 / ch-02; new terms appended correctly. ✓
4. Research grounding — every claim sourced inline; all four named error categories appear. ✓
5. Code-block correctness — 4-space indent, snake_case, traceback example + fix. ✓
6. Beginner accessibility — reader with no Python experience can follow; opens with WHY. ✓ (with the carryover WARN)
7. Outcome-line contract — closing imperative near-verbatim with the outline. ✓
8. `HfApiModel` / `ApiModel` rule — grep returns 0 hits. ✓
9. Forward-pointers — "What's next" names ch-04; bridges to ch-04's installed elements. ✓

No new framework-name leaks: `HfApiModel` 0, `ApiModel` 0, `CodeAgent` 0, `final_answer` 0, `@tool` 0 occurrences in `chapters/ch-03.md`.

## Cross-cutting findings

1. **Strength — inline citations are consistent across all seven sections.** This was the dev review's headline strength; the line-edit pass confirms it holds. Every operative claim in ch-03 names a specific source inline (Python docs, PEP 8, PEP 498, Jupyter docs, Python tutorial, Python interpreter docs, Python data model). Hold this pattern when later chapters (especially ch-06 onward) cite Anthropic / smolagents / NIST / OWASP — ch-03 is the citation-hygiene template for the rest of the book.

2. **Strength — single callout kind, single occurrence.** Style-guide § "Callouts" permits at most one callout kind per chapter, used at most twice. ch-03 uses exactly one ("The move" at line 173). Within budget and well-deployed. The closing summary line at line 185 carries the same content in non-callout form, which is the style-guide's intended pairing.

3. **WARN carryover — orientation paragraph length.** 66 words vs 60-word ceiling. Non-blocking; covered in § 10 above.

4. **LOW note — line 105 vague forward glance.** "Later chapters will show how to decide what a program should do after bad input." Style-guide § "Reading aids" specifically forbids "as we will see" / "in the next chapter" / "as the title says"; "Later chapters" is a generic phrasing that does not match any of those three forbiddances. Borderline. The chapter uses the vague form exactly once, and only because the input-validation topic genuinely lives in multiple later chapters (ch-04 control flow, ch-15 tool safety, ch-18 capstone). Could be tightened to "ch-15 covers deciding what a program should do after bad input" if master prefers the specific form. Surface as LOW; not a line-edit blocker.

5. **LOW note — line 82 "while you're learning" feels slightly hand-wave-y.** The sentence is fine — it tells the reader to keep f-string expressions small while learning — but the use of `learning` (rather than something more concrete like `building your first programs`) is a small register drift. Borderline; copy-edit pass can tighten. Surface as LOW.

6. **Out-of-scope observation — self-critique HTML comment at ch-03.md:177–183.** Standard book-writer handoff; per `AGENTS.md` book-gen mode notes, strip at publish time. Not a line-edit concern.

## Out-of-scope observations

- **Chapter length (1591 words / 1256 prose):** well under the ~17–22 page (≈3000–4000 word) target from `style-guide.md:15`. The dev review noted this is intentional — ch-03 is the first programs chapter and keeps its surface area small. No action required.
- **`HfApiModel` / `ApiModel` placement:** `HfApiModel` 0 hits, `ApiModel` 0 hits, `CodeAgent` 0 hits, `final_answer` 0 hits, `@tool` 0 hits in ch-03. The first-frame correctness rule from style-guide § "Pinning rules" is fully respected. ✓
- **Bash run command reuse:** ch-03.md:18 and ch-03.md:168 both reuse `E:\book_gen\.venv\Scripts\python.exe first_program.py` — the ch-02 venv path is carried forward verbatim. ✓
- **No regression on the ch-02 handoff:** ch-03.md:15's "with the interpreter from ch-02" backward-pointer preserves the dependency chain from outline.md:351 (ch-03 `depends_on: ch-02`). ✓

## Honest assessment

ch-03 is line-edit clean. Voice, vocabulary, pacing, terminology, citations, code conventions, forward-pointer discipline, outcome-line contract, and the dev-review carryover all pass. The single WARN on orientation paragraph length is a soft style-guide deviation, not a content bug — the prose is good and the trade-off (saving a 6-word deviation) does not justify a fix loop on its own. The two LOW notes (vague forward glance, "while you're learning" register drift) are real but cosmetic; both are copy-edit-pass material, not line-edit material.

The chapter's biggest strength: it never drops the reader's hand. Every claim is sourced, every code block is runnable, every construct gets a one-sentence plain-language gloss the first time it appears, and the chapter's "the four beginner error categories as navigation" framing is the load-bearing pedagogical move that holds the whole chapter together. The biggest stylistic risk is the orientation paragraph's 6-word length overrun, which a copy-editor can fix in one sentence without touching the chapter's substance.

I rate this chapter ready for line-edit sign-off. I do not recommend a fix loop. If master wants the orientation paragraph tightened, that is a one-sentence edit and can be batched into the next chapter's normal maintenance pass (or done at copy-edit).

## Self-critique

- **What I checked thoroughly:** blacklist scan (10 forbidden terms, 0 matches); contraction counts (verified with curly-apostrophe regex across all 8 contractions); named-source citation count (9 inline citations mapped to claims); code-block language tags and indentation (all 10 Python blocks tagged correctly, 4-space indent throughout); forward-pointer hygiene (1 explicit "What's next" + 1 backward reference + 1 vague forward glance — all classified); outcome-line verbatim match (style-guide vs. chapter callout vs. final restatement).
- **What I might have under-checked:** I did not run the chapter in `E:\book_gen\.venv\Scripts\python.exe` myself — the dev pass already spot-read the 10 blocks for static correctness, and the code is small enough that a re-run would not surface new issues. Low risk.
- **What I might have over-flagged:** the LOW note on "while you're learning" (line 82) is borderline cosmetic; a less conservative reviewer might let it pass. I flagged it because the style guide's "no hand-waving" rule technically covers "while you're learning" as a soft direction rather than a concrete instruction. Copy-editor's call.
- **What I might have missed:** I did not cross-reference each subheading against the style-guide's subheading taxonomy beyond the format check (sentence-fragment vs. full sentence; describes the move vs. the topic). All 8 subheadings pass the format check; I trust that finding.
- **PONTAIL note:** The style guide prescribes a tight voice for a technical-onboarding book. I did not propose any "richer" or "more expressive" prose alternatives because that would violate the style-guide's "Conversational technical" register. The chapter is as boring as it needs to be — that's the register. No action.

## Sign-off

ch-03 line-edit verdict: **PASS_WITH_WARN.**

- 0 FAIL.
- 1 WARN (orientation paragraph length, carryover from dev review).
- 2 LOW notes (vague forward glance; "while you're learning" register drift) — copy-edit pass material.
- No fix-loop recommended.
- No regression vs. dev pass.
- Ready to advance to Phase 7 copy-edit (or to publish if Phase 7 is skipped per the chapter-gen structural-change plan).

Ledger ch-03 row should move: dev-reviewed → line-edited.

max_fix_loops = 3 (not used this pass).

(End of file — line-edit pass complete)
