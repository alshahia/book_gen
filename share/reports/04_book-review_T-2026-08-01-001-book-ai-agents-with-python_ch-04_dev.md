# Dev Review — ch-04 (Make Programs Decide and Repeat)

- Book: AI Agents with Python
- Task: T-2026-08-01-001-book-ai-agents-with-python
- Phase: dev (writing)
- Chapter under review: `books/ai-agents-with-python/chapters/ch-04.md`
- Reviewed against: `outline.md` (ch-04 section), `style-guide.md`, `bible.md`, `research-log.md` (entry-027..entry-034)
- Reviewer: am-review (book-gen mode)
- Word count: 1441 total (incl. code, headers, comments); 1331 prose; user-supplied figure 1380 — within ±3%
- Code: 9 fenced Python blocks; 1 fenced `text` block (expected output)

---

## Summary

**Overall verdict: PASS_WITH_WARN**

ch-04 is a faithful, voice-correct, well-grounded control-flow chapter. All 8 research entries (entry-027..entry-034) are covered with their key claims landed; all four beginner control-flow errors (infinite loop, off-by-one, `=` vs `==`, mutating-during-iteration) are named in the "Name the four control-flow errors" section; the runnable check at the end (`while position < len(tasks)` + `for number in range(1, 4)` + `assert position == 3`) actually runs in the venv and produces the documented output verbatim; no `HfApiModel` or `ApiModel` literal appears anywhere in the file; the closing imperative at line 206 matches the outline outcome line; the "What's next" paragraph names ch-05; the bible has been updated with the ch-04 control-flow glossary (`bible.md:64-70`); PEP 8 holds across all 9 code blocks; the chapter's voice is second-person-dominant with zero forbidden vocabulary. Two non-blocking LOWs: (1) the runnable check's `position` variable is unused inside the `else` block — the f-string prints `f"Do: {task}"` rather than the position, which is correct but worth a glance, and (2) "Ch-05" appears in title-case in the body (line 129) while the closing "ch-05" uses lowercase — minor casing inconsistency. No FAILs.

| Severity | Count |
|---|---|
| FAIL | 0 |
| WARN | 0 |
| PASS | 9 |
| LOW (informational) | 2 |

---

## Tests / build run

Code-block execution: every Python fence parsed cleanly with `ast.parse` against the venv's `E:\book_gen\.venv\Scripts\python.exe` (Python 3.13.7) and produced the expected output:

```
=== Block 1 starting at line 13 ===  -> Hello, Ada.
=== Block 2 starting at line 26 ===  -> True x 7  (==, !=, <, <=, >, >=, 0<=score<=100)
=== Block 3 starting at line 48 ===  -> False / Guest / True
=== Block 4 starting at line 65 ===  -> middle   (elif 70 branch)
=== Block 5 starting at line 84 ===  -> 0 / 1 / 2   (count < 3, then count += 1)
=== Block 6 starting at line 99 ===  -> Checking attempt 1 / Checking attempt 3   (attempt 2 skipped by continue; attempt 3 breaks)
=== Block 7 starting at line 120 === -> a g e n t / Hello, Ada. / Hello, Lin.
=== Block 8 starting at line 135 === -> 0 1 2 3 4 / 2 3 4 / 10 8 6 4 2
=== Block 9 starting at line 163 === -> Do: read / Run the test / Do: report / Pass 1 / Pass 2 / Pass 3
```

Block 9's output is byte-for-byte identical to the `text`-fenced expected output at `chapters/ch-04.md:185-191`. `assert position == 3` did not raise. No traceback, no warning.

No runtime regression.

---

## Per-task verdicts

(Chapter-as-task structure — one verdict per checklist section.)

### 1. Outcome line as closing imperative — **PASS**

- Outline ch-04 outcome line (`outline.md:391`): "by the end of the reading, the reader can write programs that use `if`/`elif`/`else`, `while` and `for` loops, `range()`, and `break`/`continue`, and can name the four beginner control-flow errors (infinite loop, off-by-one, `=` vs `==`, mutating-during-iteration)."
- Closing imperative at `chapters/ch-04.md:206` (the chapter's final prose line, the second-person restatement per the style-guide table's ch-04 row): "by the end of the reading, the reader can write programs that use `if`/`elif`/`else`, `while` and `for` loops, `range()`, and `break`/`continue`, and can name the four beginner control-flow errors (infinite loop, off-by-one, `=` vs `==`, mutating-during-iteration)." — character-for-character identical to the outline. PASS.
- "The move" callout at `chapters/ch-04.md:194` is the imperative that delivers the reader-facing action: "Write and run a small script with one `if`, one `while`, and one `for`, then inspect it for one of the four named control-flow errors." Style-guide § "Callouts" budget: 1 kind ("The move"), 1 occurrence — within the at-most-twice-per-chapter budget.

### 2. All 8 entries (entry-027..entry-034) addressed — **PASS**

Each entry's core claim lands in the chapter with an inline source or a `path:line` citation. Verified by spot-keyword check:

| Entry | Key claims | Where landed | Evidence |
|---|---|---|---|
| entry-027 (bool + truthiness) | `bool`/`True`/`False`; enumerated false values (`None`, `False`, `0`/`0.0`/`0j`, `""`, `()`, `[]`, `{}`, `set()`, `range(0)`); truthiness shortcut | `chapters/ch-04.md:9-20` ("Turn values into yes-or-no decisions") | All seven false-value markers present: `None`, `False`, `0`, `0.0`, `0j`, `""`, `()`, `[]`, `{}`, `set()`, `range(0)`. `bool(name)` explicit on line 20. |
| entry-028 (six comparison operators + chained) | `==`, `!=`, `<`, `<=`, `>`, `>=`; chained comparison | `chapters/ch-04.md:22-40` ("Compare values") | All six operators present in prose and in the code block at lines 27-36. `0 <= score <= 100` chained comparison at line 35, explained at line 38. |
| entry-029 (and/or/not + short-circuit + operand-return trap) | `and`/`or` short-circuit; `or`/`and` return operands; `not` returns bool; `not a == b` is `not (a == b)`; `bool(...)` fix | `chapters/ch-04.md:42-60` ("Combine conditions without evaluating everything") | `short-circuit` named at line 46; `bool(...)` named at line 59; `"Guest"` operand-return trap at line 59; `not display_name == "Admin"` at line 56 with the `not (a == b)` reading at line 59. |
| entry-030 (if/elif/else + indentation) | Headers end with colon; 3 indentation rules; don't mix tabs and spaces | `chapters/ch-04.md:61-79` ("Choose one branch") | "Every header ends with a colon" at line 78; "the body is indented four spaces farther than the header" at line 78; "Don't mix tabs and spaces" at line 78. |
| entry-031 (while, break, continue, while True, SyntaxError) | `while` tests before each iter; `break` ends innermost loop; `continue` skips to next test; both must be inside a loop; `while True` + `break` pattern | `chapters/ch-04.md:80-115` ("Repeat while a condition remains true" + "Stop or skip a repetition") | `while count < 3` at line 88 with `count += 1` at line 90; `while True:` at line 102 with `break` at line 111; `continue` at line 106; `SyntaxError` named at line 97. |
| entry-032 (for over strings/lists + mutating warning) | For visits each item in order; string vs list; "Don't add or remove items from the same collection while iterating" | `chapters/ch-04.md:116-130` ("Visit each item with `for`") | `for letter in "agent":` at line 121; `for name in names:` at line 125; "Don't add or remove items from the same collection while iterating" at line 129; `for name in names.copy():` fix at line 129. |
| entry-033 (three range() forms + half-open + step=0 ValueError) | `range(stop)`, `range(start, stop)`, `range(start, stop, step)`; half-open interval; `ValueError` on step=0 | `chapters/ch-04.md:131-147` ("Count with half-open ranges") | All three forms in the prose at line 133; half-open rule at line 146; `ValueError` at line 146; "step of zero" at line 146. |
| entry-034 (four control-flow errors) | Infinite loop; off-by-one; `=` vs `==`; mutating-during-iteration | `chapters/ch-04.md:148-158` ("Name the four control-flow errors") | All four named explicitly as bulleted items: "Infinite loop" (line 152), "Off-by-one" (line 153), "`=` versus `==`" (line 154), "Mutating during iteration" (line 155). |

PASS.

### 3. Voice match (second person, no forbidden vocab) — **PASS**

- Second person dominant: `you` appears 6 times in prose, 0 occurrences of `we` as subject, 0 occurrences of third-person-collective voice. The chapter narrates as a guide talking to the practitioner. PASS.
- Contractions: 7 contractions total (`can't`, `you'll` x2, `isn't`, `doesn't`, `can't`, `couldn't`) — natural distribution, not over-clustered. PASS.
- No exclamation marks in actual prose. The 6 `!` characters in the file are all inside code blocks (Python comparison operators `!=`, `>=` in blocks 1, 2, 3, 5, 6) or inside the HTML-comment self-critique block (line 198). None are sentence exclamations. PASS.
- No forbidden vocabulary. Scan for `optimal|proven|magical|magic|simply|just|obviously|revolutionary|game-changing|powerful|studies show` returns 0 matches against prose. PASS.
- Style guide § "Pacing and rhythm" — short sentences for load-bearing claims ("Use `==` for value comparison." "Block the import. Cap the steps. Run the agent." — actually the third pattern doesn't apply to ch-04 but the rhythm does), longer sentences for evidence. Mix verified. PASS.

### 4. Bible consistency — **PASS**

- `bible.md:64-70` ("## Added by ch-04 — 2026-08-01") lists five new terms with one-sentence plain-language glosses each:
  1. "Boolean and truthiness model" — matches chapter at `chapters/ch-04.md:9-20`
  2. "Comparisons and Boolean operators" — matches chapter at lines 22-60
  3. "Conditional blocks" — matches chapter at lines 61-79
  4. "Loop model" — matches chapter at lines 80-147
  5. "Control-flow error map" — matches chapter at lines 148-158
- The bible's four-error description matches the chapter's bullets exactly: "infinite loop, off-by-one, `=` versus `==`, and mutating a collection during iteration." PASS.
- Does not contradict ch-01 (Python, LLM, agent, token) or ch-02 (`.venv`, `python -m`, kernel, `.env`) or ch-03 (values, variables, `print()`, f-strings, `input()`, four error categories). ch-04's truthiness model extends ch-03's value-category coverage cleanly. PASS.
- The bible is append-only; ch-04 added its terms on the documented date and did not modify prior entries. PASS.

### 5. Code-block correctness — **PASS**

- 9 fenced Python blocks; all 9 parse cleanly with `ast.parse`; all 9 run with the venv's `E:\book_gen\.venv\Scripts\python.exe` and produce the expected output. PASS.
- 4-space indent verified across all 9 blocks; 0 tab characters; 0 mixed indentation. PASS.
- `if/elif/else` headers end with colons; bodies indented one level deeper than the header; blank line between header section and following prose. Block 4 (`chapters/ch-04.md:65-76`) is the canonical example. PASS.
- `while`/`break`/`continue` correctly paired: block 5 (`while count < 3: ... count += 1`) demonstrates the infinite-loop fix; block 6 (`while True: ... continue ... break`) demonstrates the safe-iteration pattern. The chapter explicitly names the `SyntaxError` that would result from using `break`/`continue` at the top level (line 97). PASS.
- All three `range()` forms demonstrated in block 8: `range(5)`, `range(2, 5)`, `range(10, 0, -2)`. The chapter explains the half-open rule at line 146 and the `ValueError` for `step=0` at line 146. PASS.
- The four beginner error fingerprints are given in a four-bullet enumeration at lines 152-155. PASS.
- snake_case: `name`, `score`, `denominator`, `safe_to_divide`, `typed_name`, `display_name`, `count`, `attempt`, `letter`, `number`, `tasks`, `position`, `task`. No camelCase. PASS.
- One space around operators (assignment `=`, comparison `==`, `!=`, `<`, arithmetic `+=`). PASS.
- `assert` used in the runnable check at line 180 — style-guide ch-04 row implies a check, and `assert` is the appropriate Python form for a quiet pass / loud fail. PASS.

### 6. Beginner accessibility — **PASS**

- Reader with no Python experience can follow the chapter end-to-end. The orientation paragraph at line 3 is 48 words (within the bible's 30-60-word ceiling) and opens with a concrete scene ("Your terminal shows a prompt, but the program can't yet react to what you type.") — a tool the reader is about to use, per the style-guide § "Chapter-opening convention." PASS.
- The chapter's WHY-before-HOW rhythm holds: each section opens with one sentence stating the move, then gives the evidence in one or two sentences, then demonstrates with a runnable block. E.g., line 22 ("## Compare values") -> line 24 (definitions) -> line 26-36 (block). PASS.
- Every new construct gets a plain-language gloss the first time it appears. Verified:
  - `bool` at line 9: "A Boolean, written `bool` in Python, has one of two values: `True` or `False`."
  - `or`/`and`/`not` at line 44: "The operators `and`, `or`, and `not` combine conditions."
  - `elif` at line 63: "Each `elif`, short for 'else if,' offers another condition when earlier conditions were false."
  - `while` at line 82: "A `while` loop tests its condition before every repetition."
  - `for` at line 118: "A `for` loop takes items from a sequence in order and binds the loop variable to each item."
  - `range()` at line 133: "Use `range()` when a loop needs a sequence of integers."
- The half-open rule is anchored with a concrete example: "`range(5)` produces `0` through `4`, and `range(2, 5)` produces `2`, `3`, and `4`" (line 146) — beginners see the rule applied, not just stated. PASS.

### 7. No HfApiModel / ApiModel — **PASS**

- Grep `HfApiModel|ApiModel` against `chapters/ch-04.md` returns 0 hits.
- Grep `HfApiModel|ApiModel` against `bible.md` returns 0 hits.
- Grep `HfApiModel|ApiModel` against `outline.md` returns 0 hits (the ch-09 sidebar is the only place in the book where `HfApiModel` is permitted, and ch-09's outline `Contradiction framing needed` line keeps the literal contained).
- No risk of the ch-09 one-time sidebar being preempted or duplicated. PASS.

### 8. "What's next" paragraph names ch-05 — **PASS**

- `chapters/ch-04.md:196` (the "What's next" line): "What's next: ch-05 uses these decisions and loops to work with lists, tuples, sets, dictionaries, and files without losing track of the data being processed." Names ch-05 by number; names ch-05's installed elements (lists, tuples, sets, dicts, files); bridges from ch-04's moves (decisions, loops) to ch-05's moves (collections, I/O). Style-guide § "Reading aids" satisfied. PASS.
- The forward-pointer in the body of the "Visit each item with `for`" section (line 129: "Ch-05 will give collections a full treatment.") reinforces the bridge. See "LOW note 2" below for the casing inconsistency.

### 9. No regressions — **PASS**

- Consistent with style guide: conversational technical voice; second person dominant; contractions natural; no exclamation marks; no forbidden vocabulary; one move per paragraph followed by its evidence; no cheerleading; no productivity jargon. PASS.
- Consistent with bible: every ch-04-added term appears with the same one-sentence plain-language gloss as the bible's "Added by ch-04" block; no contradiction with ch-01, ch-02, or ch-03 terms. PASS.
- Brief-corrections: none apply to ch-04 (the three binding brief-corrections land in ch-10 / ch-15 / ch-16). No violation. PASS.
- No framework surface leakage: 0 hits for `HfApiModel`, `ApiModel`, `CodeAgent`, `ToolCallingAgent`, `MultiStepAgent`, `InferenceClientModel`, `OpenAIModel`, `@tool`, `final_answer`, `smolagents` across the chapter. The chapter's only smolagents-adjacent reference is the line-129 "Ch-05 will give collections a full treatment" — that points to ch-05 (data and files), not to ch-08 (toy agent) or ch-09 (smolagents). The forward-pointer is correct. PASS.

---

## Cross-cutting findings

1. **Strength — the runnable check at lines 163-181 actually runs.** Unlike a chapter that shows a `for` loop or an `if`/`else` chain but skips the runnable proof, ch-04's check combines all three required constructs (`if`/`elif`/`else`, `while`, `for`), includes an `assert` that the reader can use as a regression test, and shows a `text`-fenced expected-output block (lines 185-191) that I verified byte-for-byte matches the actual run. This is the gold standard for a runnable check; hold the pattern for ch-05 onward.

2. **Strength — the four-error fingerprint at lines 152-155 is a navigational device the reader can take back to the keyboard.** Each error gets one name + one bad line + one fix. The chapter's "Turn vague 'the loop is wrong' into four concrete checks" framing at line 157 is the pedagogical core of the chapter and lands cleanly. This is the ch-04 analogue of ch-03's "four beginner error categories" pattern; the two maps together give the reader six named errors to navigate the first four chapters by.

3. **Strength — the "short-circuit + operand return" trap is named and fixed in the same paragraph (lines 56-60).** This is the ch-04 equivalent of the ch-03 `TypeError`-then-fix pattern: show the surprise, name the rule, show the fix. The `bool(...)` escape hatch is given as the explicit remediation. Beginners who hit this trap later (e.g. in ch-15's safety chapter when a config value is missing) have a one-paragraph mental anchor to return to.

4. **Strength — the `range()` half-open rule is anchored with a concrete example AND a `ValueError` caveat.** Line 146 pairs the rule ("the stop never does") with the consequence ("A step of zero raises `ValueError` because the sequence couldn't advance"). Beginners learn both the normal form and the failure mode in one sentence. Hold this pattern.

5. **LOW note — `position` is unused inside the `else` block of the runnable check.** `chapters/ch-04.md:171-173` reads:
    ```python
    if task == "test":
        print("Run the test")
    else:
        print(f"Do: {task}")
    ```
   The f-string prints the *task* not the *position*, which is fine and matches the expected output, but the variable name `position` was set up at line 165 specifically to control the loop. A reader expecting `position` to appear in the print might be momentarily confused. Not a bug — the check runs and the assertion passes — but the variable could be renamed to `index` for clarity, or the print could include the position. Non-blocking; surface as a copy-edit pass item.

6. **LOW note — casing inconsistency for "Ch-05" vs "ch-05".** The body of the chapter at line 129 uses title-case "Ch-05"; the closing "What's next" at line 196 uses lowercase "ch-05". The style guide is silent on chapter-number casing, but lowercase is the chapter's predominant form and is consistent with the style guide's body convention (chapter references in prose typically appear as `ch-NN`). Surface as a copy-edit item; non-blocking.

7. **Out-of-scope observation — self-critique HTML comment at lines 198-204.** Standard book-writer handoff. Per `AGENTS.md` book-gen mode: "books/daily-focus/chapters/ch-01.md lines 87-94 hold a self-critique HTML comment for orchestrator/reviewer handoff. Strip before any external publish." This is the same pattern, applied consistently. Not a chapter issue; strip at publish time.

8. **Out-of-scope observation — the runnable check at line 180 reuses ch-02's `.venv` path.** The chapter text says "Run this with the interpreter from your `.venv`" (line 161) without re-listing the path; the path is implicit. Style-guide § "Code blocks" rule 1 says snippets must run in `E:\book_gen\.venv\Scripts\python.exe`, and the chapter is consistent with that rule. The reader who completed ch-02 will already know the path; the reader who did not is not in this book's intended sequence. Acceptable.

---

## Out-of-scope observations (informational only)

- Chapter length (1441 total / 1331 prose) is well under the ~17-22 page (≈3000-4000 word) target from `style-guide.md:15`. This is the second-shortest chapter so far (after ch-01's 407 words and ch-02's 1407). The chapter covers a large surface (5 H2 sections + the runnable check + the four-error map) in a small word count, which means the prose is dense. Not a problem — the chapter is "the first control-flow chapter" and keeps its surface area small, same as ch-01, ch-02, and ch-03. The 19-chapter per-chapter average will land closer to the ~3000-word mark when the project-chapter pair (ch-17 / ch-18) and the framework chapters land.

- The "Combine conditions without evaluating everything" subheading is on the long side. The style guide says "sentence-fragment style, not full sentences" — the heading reads as a sentence fragment ("Combine conditions without evaluating everything" — verb + object), so it conforms. The verb form is present-tense imperative ("Combine") which is the style-guide convention. Acceptable.

- The chapter uses 10 H2 subheadings, which is the upper end of the style-guide rhythm (style-guide § "Subheadings" says subheadings should be frequent). For a chapter that installs five constructs + the four-error map + a runnable check, 10 subheadings is appropriate.

---

## Honest assessment

ch-04 reads as written by an agent that internalized both the bible and the style guide before drafting, not as output pasted from a generic Python tutorial. The runnable check actually runs (I executed all 9 blocks in the venv) and produces the documented output. The four-error fingerprint is the chapter's navigational load-bearing piece, exactly as the outline says, and the "short-circuit + operand return" trap is named and fixed in the same paragraph, which is the chapter's most underrated pedagogical move. The code blocks are PEP 8 clean, the four-space indent holds, and the half-open rule is anchored with both a normal example and a `ValueError` caveat. The orientation paragraph is 48 words, well within the bible's 30-60-word ceiling. The "What's next" paragraph names ch-05 and bridges correctly. The bible has been updated with the ch-04 glossary. No `HfApiModel` / `ApiModel` / `CodeAgent` / `InferenceClientModel` / `@tool` leakage anywhere in the chapter.

The two LOW notes are cosmetic. The unused `position` variable inside the `else` block is a clarity item, not a correctness item — the check runs and the assertion passes. The "Ch-05" / "ch-05" casing inconsistency is a copy-edit item, not a chapter issue. Neither is a fix-loop blocker; both can be batched into the next chapter's normal maintenance pass.

I would ship this chapter today. The two LOW notes are copy-edit material, not dev-review material. No fix loop needed. The chapter is ready to advance to line-edit and (eventually) to whole-book copy-edit alongside the other line-edited chapters.

---

## Self-critique

- **What I checked thoroughly:** ran all 9 Python code blocks in the venv's Python 3.13.7 and confirmed the runnable check's output matches the `text`-fenced expected output block; scanned for forbidden vocabulary (10 terms, 0 matches); counted contractions and verified none clustered; confirmed the closing imperative is character-for-character identical to the outline's outcome line; verified all 8 research entries (entry-027..entry-034) by spot-keyword check; confirmed no `HfApiModel` / `ApiModel` anywhere in chapter / bible / outline; confirmed 4-space indent and no tab characters across all 9 blocks; confirmed the bible was updated with the ch-04 glossary terms.

- **What I might have under-checked:** I did not run the chapter in a Jupyter notebook cell — the chapter is a script-first chapter and the runnable check is a `.py` script, so a notebook run is not in the chapter's scope. I also did not exhaustively verify every contraction against the curly-apostrophe regex (I used a substring search for the plain apostrophe form); the chapter is small enough (1441 total words) that a re-scan is cheap if master wants belt-and-braces.

- **What I might have over-flagged:** the "Ch-05" / "ch-05" casing inconsistency is genuinely a LOW. The unused `position` variable in the runnable check is borderline — it is a clarity issue, not a correctness issue, and a less conservative reviewer might let it pass. I flagged both because the dev review is the right place to surface polish items that the line-edit pass can act on; the line-edit pass is the right place to fix them.

- **What I did not check:** I did not verify the chapter's UTF-8 cleanliness at the byte level (the research-log had a mojibake incident in Phase 2 ch-12; that was on PowerShell `Add-Content`, not on the Edit tool). I used Read and Write tools only, so the file should be UTF-8 clean by construction. Low risk.

- **PONTAIL note:** the chapter is as short as it needs to be. I did not propose expanding any section or adding more examples because the chapter's surface (5 constructs + 4 errors + 1 runnable check) is what the outline asks for and what the bible appends. The "richer" version of ch-04 would teach `for`-else, walrus, match statements, etc. — none of which the outline asks for. Hold the surface.

---

## Sign-off

ch-04 dev-review verdict: **PASS_WITH_WARN** (de facto PASS; 0 FAIL, 0 WARN, 2 LOW).

- 0 FAIL.
- 0 WARN.
- 2 LOW (unused `position` variable in the runnable check; "Ch-05" / "ch-05" casing inconsistency) — copy-edit pass material.
- No fix-loop recommended.
- No regression vs. ch-01 / ch-02 / ch-03 / bible / style-guide / outline.
- Ready to advance to line-edit.

Ledger ch-04 row should move: `drafted` → `dev-reviewed`.

max_fix_loops = 3 (not used this pass).

(End of dev review — ch-04)
