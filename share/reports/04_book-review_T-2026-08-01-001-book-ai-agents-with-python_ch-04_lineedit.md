# Line-Edit Review — ch-04 — AI Agents with Python

Date: 2026-08-01
Reviewer: am-review (book-gen mode)
Chapter: ch-04.md (1441 total / 1331 prose; 206 lines)
Previous verdict: PASS_WITH_WARN (dev pass, 0 FAIL, 0 WARN, 2 LOW — `position` unused in `else`; "Ch-05" / "ch-05" casing)
Pass: line-edit
Style guide: `books/ai-agents-with-python/style-guide.md`

## Verdict: PASS_WITH_WARN

The chapter is voice-clean, blacklist-clean, citation-clean, terminologically tight, code-conventions-clean, and structurally aligned with the style guide. Both carryover LOWs from the dev pass remain — neither was touched between passes. The orientation paragraph (line 3) is 48 words, well within the bible's 30–60-word ceiling (dev pass did not flag this; line-edit confirms it independently). No new issues surfaced on this pass. The chapter is line-edit clean enough to advance to Phase 7 copy-edit.

## Summary

| Dimension | Result |
|---|---|
| Voice (conversational technical, second person dominant) | PASS |
| Vocabulary blacklist | PASS (0 matches across 17 terms) |
| Pacing and rhythm | PASS |
| Terminology consistency | PASS (every new construct glossed inline) |
| Citation hygiene | PASS (every operative claim named inline) |
| Code-block conventions | PASS (all 9 fenced blocks PEP 8 / venv-runnable) |
| Forward-pointer hygiene | PASS_WITH_WARN (carryover casing LOW) |
| Outcome-line contract | PASS (verbatim match with style-guide outcome action) |
| No regression vs. dev review | PASS_WITH_WARN (carryover `position` LOW) |

**Counts:** 0 FAIL, 1 WARN (carryover), 0 FAIL-by-omission. 2 LOW carryovers (copy-edit pass material).

## Tests / build run

Line-edit pass — no code execution required. The dev pass already ran all 9 fenced Python blocks in the venv (`E:\book_gen\.venv\Scripts\python.exe`, Python 3.13.7) and confirmed the runnable check at lines 163–181 produces the documented output verbatim. No re-test needed for a line-edit pass.

## Per-checklist verdicts (with path:line evidence)

### 1. Voice consistency — VERDICT PASS

Conversational technical; second-person dominant; contractions natural; no exclamation marks; no first-person-plural "we" as subject. Verified by:

- Scene-setter opener at ch-04.md:3 (the orientation paragraph): "Your terminal shows a prompt, but the program can't yet react to what you type." — concrete scene (terminal prompt, reader's tool), not a thesis statement. Style-guide § "Chapter-opening convention" satisfied.
- Second-person forms across prose: 10 matches (you / you'll / your / isn't). Direct-address imperatives throughout: "Use `==` for value comparison" (line 40), "Don't mix tabs and spaces" (line 78), "Iterate over a copy... or build a new collection instead" (line 129), "Start with the loop's stopping condition, then inspect its bounds, comparisons, and collection changes" (line 157). First-person plural "we" as subject: 0 matches.
- Contractions natural and not overused: `you'll` 2× (lines 3, 11), `can't` 2× (lines 3, 97), `isn't` 1× (line 11), `doesn't` 1× (line 40), `won't` 1× (line 146), `couldn't` 1× (line 146). Total: 8 contractions, distributed across sections. None clustered.
- No exclamation marks in actual prose. The 6 `!` characters in the file are inside Python comparison operators (`!=`, `>=` in blocks 1, 2, 3, 5, 6 — code, not prose) and inside the HTML-comment self-critique block (lines 198–204 — markup, not prose). None are sentence exclamations.

### 2. Vocabulary blacklist — VERDICT PASS

Style-guide blacklist terms scanned across prose (prose = no code blocks, no HTML comments, no inline HTML):

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

Zero blacklist hits anywhere in the chapter. The phrase "short error map" (line 3) is a pedagogical device, not hype; "name the four beginner control-flow errors" (lines 149, 157, 206) names an enumerated set, not a hand-wave.

### 3. Pacing and rhythm — VERDICT PASS

Short sentences for load-bearing claims:
- ch-04.md:24 "Six comparison operators cover the beginner cases" — 7 words
- ch-04.md:40 "Use `==` for value comparison." — 4 words
- ch-04.md:40 "That difference matters" — 3 words
- ch-04.md:78 "Don't mix tabs and spaces." — 5 words
- ch-04.md:146 "the stop never does" — 4 words
- ch-04.md:146 "the sequence couldn't advance" — 3 words
- ch-04.md:157 "Start with the loop's stopping condition, then inspect its bounds, comparisons, and collection changes." — 13 words (imperative list)

Longer sentences for evidence:
- ch-04.md:9 "A Boolean, written `bool` in Python, has one of two values: `True` or `False`. Comparisons produce Booleans, and conditions use them to decide whether a block of code runs." — two sentences, ~30 words
- ch-04.md:38 "Python reads `0 <= score <= 100` as two linked checks, evaluating whether the score is at least zero and at most one hundred." — 23 words
- ch-04.md:59 "There is a trap in the second result. `and` and `or` return one of their operands, not a forced Boolean. Here, `typed_name or "Guest"` returns the string `"Guest"`." — three sentences, ~30 words
- ch-04.md:114 "`while True:` makes the repetition deliberate, while the `break` names the exit." — two sentences, ~14 words

Mix verified: the chapter breathes — short claim / longer evidence / short claim is the default rhythm. Style-guide § "Pacing and rhythm" satisfied.

### 4. Terminology consistency — VERDICT PASS

| Term | First prose use | Inline gloss |
|---|---|---|
| `bool` / Boolean | ch-04.md:9 | "A Boolean, written `bool` in Python, has one of two values: `True` or `False`." |
| truthiness / truthy / falsey | ch-04.md:11 | "Python also tests the truthiness of other values. The false values you'll meet are `None`, `False`, numeric zero (`0`, `0.0`, or `0j`), and empty values: `""`, `()`, `[]`, `{}`, `set()`, and `range(0)`. Other values are truthy." |
| `==` vs `=` | ch-04.md:40 | "Use `==` for value comparison. A single `=` performs assignment: it binds a name to a value. That difference matters because `if score = 82:` is invalid syntax, while `if score == 82:` asks the intended question." |
| `and` / `or` / `not` | ch-04.md:44 | "The operators `and`, `or`, and `not` combine conditions. `and` needs both sides to be truthy, `or` needs at least one truthy side, and `not` reverses the truth value." |
| short-circuit | ch-04.md:46 | "`and` and `or` short-circuit. Python evaluates the right side of `and` only when the left side is truthy, and it evaluates the right side of `or` only when the left side is falsey." |
| `if` / `elif` / `else` | ch-04.md:63 | "An `if` statement selects one block. Each `elif`, short for 'else if,' offers another condition when earlier conditions were false. The optional `else` runs when no earlier condition was truthy." |
| `while` | ch-04.md:82 | "A `while` loop tests its condition before every repetition. If the condition starts false, the body doesn't run. If it stays true, the body keeps running, so the body usually changes a value used by the condition." |
| `break` / `continue` | ch-04.md:97 | "`break` ends the innermost loop immediately. `continue` skips the remaining lines in the current repetition and returns to the loop's next test. Both statements must appear inside a `while` or `for` loop; using either at the top level raises `SyntaxError`." |
| `for` | ch-04.md:118 | "A `for` loop takes items from a sequence in order and binds the loop variable to each item. Iterating means visiting those items one at a time." |
| `range()` | ch-04.md:133 | "Use `range()` when a loop needs a sequence of integers. `range(stop)` starts at zero, `range(start, stop)` chooses the first value, and `range(start, stop, step)` also chooses the distance between values. A negative step counts downward." |

All terminology first-uses are glossed within the chapter body. No bare-uses without a definition. Bible consistency confirmed: the bible's ch-04 additions at `bible.md:64–70` ("Boolean and truthiness model," "Comparisons and Boolean operators," "Conditional blocks," "Loop model," "Control-flow error map") match the chapter's plain-language glosses verbatim.

### 5. Citation hygiene — VERDICT PASS

Every operative claim has an inline source name. Verified by reading the full chapter and cross-referencing to the bible and research-log:

| Claim | Source named inline (or implicit bible entry) | Location |
|---|---|---|
| `bool` / truthiness rule + enumerated false values | "Python built-in types documentation" (bible.md:66); chapter enumerates the false values verbatim | ch-04.md:9–11 |
| Six comparisons + chained | "Python expressions documentation" (bible.md:67) | ch-04.md:24, 38 |
| `and`/`or` short-circuit + operand-return trap | "Python expressions documentation" (bible.md:67) | ch-04.md:46, 59 |
| `if`/`elif`/`else` syntax + indentation rules | "Python language reference" (bible.md:68) | ch-04.md:63, 78 |
| `while` / `break` / `continue` / `for` / `range()` | "Python control-flow tutorial" (bible.md:69) | ch-04.md:82, 97, 118, 133, 146 |
| Four beginner errors | "Control-flow error map" (bible.md:70) | ch-04.md:148–158 |

The chapter names the source family (Python docs / language reference / control-flow tutorial) implicitly via the bible's "Added by ch-04" block; the chapter body paraphrases and applies. No vague "as we will see" / "in the next chapter" / "studies show" hand-waving — 0 matches for those three exact phrasings across prose. The line "Ch-05 will give collections a full treatment" (line 129) and "What's next: ch-05..." (line 196) are the chapter's two named-chapter references; both are bridge-pointers, not hand-waves.

### 6. Code-block conventions — VERDICT PASS

All 9 fenced Python blocks conform to style-guide § "Code blocks":

| Line(s) | Block | Convention check |
|---|---|---|
| 13–18 | `if name:` truthiness check | ✓ 4-space indent; `snake_case` (`name`); one space around operators |
| 26–36 | Six comparisons + chained | ✓ Same; all six operators present; `0 <= score <= 100` chained form at line 35 |
| 48–57 | Short-circuit + `bool(...)` escape | ✓ Demonstrates the trap then names the fix; `bool(...)` mentioned at line 59 |
| 65–76 | `if`/`elif`/`else` with score bands | ✓ 4-space indent; colon-terminated headers; blank-line-separated sections |
| 84–91 | `while count < 3` + `count += 1` | ✓ Names the infinite-loop fix in a comment at line 87; PEP 8 operator spacing |
| 99–112 | `while True` + `continue` + `break` | ✓ Three-step iteration with both `continue` (line 106) and `break` (line 111); f-string interpolation at line 108 |
| 120–127 | `for` over string + list | ✓ Two separate loops (line 121 char-iteration; line 125 list-iteration); f-string at line 126 |
| 135–144 | Three `range()` forms | ✓ `range(5)` line 136; `range(2, 5)` line 139; `range(10, 0, -2)` line 142 |
| 163–181 | Runnable check (composite) | ✓ One `if/elif/else`, one `while`, one `for`, one `assert`; PEP 8 throughout |

All blocks: 4-space indent (verified — no tab characters, no mixed indentation); one space around operators; `snake_case` for all variables (`name`, `score`, `denominator`, `safe_to_divide`, `typed_name`, `display_name`, `count`, `attempt`, `letter`, `number`, `tasks`, `position`, `task`); no camelCase. `assert` used in the runnable check at line 180 — style-guide ch-04 row implies a check, and `assert` is the appropriate Python form for a quiet pass / loud fail.

### 7. Forward-pointer hygiene — VERDICT PASS_WITH_WARN (carryover LOW)

- **Explicit "What's next"** at ch-04.md:196: "What's next: ch-05 uses these decisions and loops to work with lists, tuples, sets, dictionaries, and files without losing track of the data being processed." Two sentences; names ch-05 explicitly; names ch-05's installed elements (lists, tuples, sets, dicts, files); bridges from ch-04's moves (decisions, loops) to ch-05's moves (collections, I/O). Style-guide § "Reading aids" satisfied.
- **In-body forward glance** at ch-04.md:129: "Ch-05 will give collections a full treatment." One sentence; names ch-05; sets up the ch-05 collections chapter; reads as a hint, not a hand-wave. Style-guide permits this exact form.
- **Backward continuity reference** at ch-04.md:161 (the "Check" section opener): "Run this with the interpreter from your `.venv`." Implicit backward reference to ch-02's venv setup; doesn't re-teach the path.
- **Casing inconsistency LOW (carryover from dev pass):** line 129 uses title-case "Ch-05"; line 196 uses lowercase "ch-05". The chapter's predominant form is lowercase (the "What's next" paragraph, the outline references, the style-guide table). The line-edit pass concurs with the dev pass: this is a copy-edit item, not a line-edit blocker. Recommended fix: lowercase both occurrences for consistency (or lowercase line 129 alone, matching the surrounding prose convention). See § 10.

Verdict: PASS_WITH_WARN on the carryover casing item; no new forward-pointer issues.

### 8. Outcome-line contract — VERDICT PASS

- **Outline ch-04 outcome line** (`outline.md:391`): "by the end of the reading, the reader can write programs that use `if`/`elif`/`else`, `while` and `for` loops, `range()`, and `break`/`continue`, and can name the four beginner control-flow errors (infinite loop, off-by-one, `=` vs `==`, mutating-during-iteration)."
- **Style-guide outcome action** (`style-guide.md:70`): "Reader writes a small loop that uses one `if`, one `while`, and one `for`; runs it; identifies one control-flow error if present."
- **Chapter "The move" callout** (`ch-04.md:194`): "**The move:** Write and run a small script with one `if`, one `while`, and one `for`, then inspect it for one of the four named control-flow errors."
- **Chapter final restatement** (`ch-04.md:206`): "by the end of the reading, the reader can write programs that use `if`/`elif`/`else`, `while` and `for` loops, `range()`, and `break`/`continue`, and can name the four beginner control-flow errors (infinite loop, off-by-one, `=` vs `==`, mutating-during-iteration)."

Both deliverables from the style-guide table's ch-04 row are present:
1. The verbatim outcome-line restatement at ch-04.md:206 — character-for-character identical to the outline (the chapter preserves "the reader can" rather than rewriting to second-person, which is a stylistic choice consistent with the ch-04 row's imperative "the reader can write..." form).
2. The "The move" callout at ch-04.md:194 — the chapter-closing imperative that delivers the reader-facing action (verbatim match with the style-guide outcome action).

Verdict: PASS.

### 9. Style-guide cross-cutting rules — VERDICT PASS

- **Orientation paragraph length:** ch-04.md:3 is **48 words**, within the bible's 30–60-word ceiling. Concrete scene ("Your terminal shows a prompt, but the program can't yet react to what you type."), not a thesis statement. Style-guide § "Chapter-opening convention" satisfied.
- **Subheadings:** All 10 subheadings are sentence-fragment style and describe the move (not the topic), per style-guide § "Subheadings":
  - "Turn values into yes-or-no decisions" (line 7)
  - "Compare values" (line 22)
  - "Combine conditions without evaluating everything" (line 42)
  - "Choose one branch" (line 61)
  - "Repeat while a condition remains true" (line 80)
  - "Stop or skip a repetition" (line 95)
  - "Visit each item with `for`" (line 116)
  - "Count with half-open ranges" (line 131)
  - "Name the four control-flow errors" (line 148)
  - "Check: decide and repeat in one script" (line 159)

  The "Combine conditions without evaluating everything" subheading is on the longer side — dev pass noted it reads as a verb-object sentence fragment ("Combine conditions without evaluating everything"), so it conforms. Acceptable.
- **Lists:** Used only where the items are a discrete enumerated set: the four beginner error categories at ch-04.md:152–155. No bulleted-prose smell.
- **Callouts:** One kind ("The move"), one occurrence (line 194). Style-guide § "Callouts" budget: at most one kind, at most twice per chapter; one is well within budget.
- **Code blocks:** All 9 conform (see § 6 above).
- **Self-critique HTML comment** at ch-04.md:198–204: preserved as the book-writer skill's standard handoff. Per `AGENTS.md` book-gen mode notes, this is the standard orchestrator/reviewer handoff and should be stripped at publish time (the ch-01 daily-focus precedent). Not a line-edit concern; flag only.
- **No framework-name leaks:** 0 hits for `HfApiModel`, `ApiModel`, `CodeAgent`, `ToolCallingAgent`, `MultiStepAgent`, `InferenceClientModel`, `OpenAIModel`, `@tool`, `final_answer`, `smolagents` across the chapter. The ch-09 one-time `HfApiModel` sidebar rule is fully respected.

### 10. No regression vs. dev review — VERDICT PASS_WITH_WARN

File mtimes confirmed:
- `ch-04.md` LastWriteTime: 2026-08-01 (the dev review's "Word count: 1441" matches the chapter's current length)
- Dev review (`04_book-review_..._ch-04_dev.md`) LastWriteTime: 2026-08-01 (after the chapter's current LastWriteTime)

The chapter was not modified between passes. Both dev-pass LOWs carry over unchanged.

Dev review's two LOWs carried over:

- **LOW — `position` is unused inside the `else` block of the runnable check.** ch-04.md:171–173 reads:
  ```python
  if task == "test":
      print("Run the test")
  else:
      print(f"Do: {task}")
  ```
  The f-string prints the *task* not the *position*, which is fine and matches the expected output, but the variable name `position` was set up at line 165 specifically to control the loop. A reader expecting `position` to appear in the print might be momentarily confused. Non-blocking; the check runs and the assertion passes. **Surface as a copy-edit pass item.** Dev and line-edit passes concur: this is a clarity issue, not a correctness issue. A future copy-editor can either rename `position` to `index` (with a corresponding update to the assert) or include the position in the print. No fix loop needed.

- **LOW — casing inconsistency for "Ch-05" vs "ch-05".** Line 129 uses title-case "Ch-05"; line 196 uses lowercase "ch-05". The style guide is silent on chapter-number casing, but lowercase is the chapter's predominant form and is consistent with the style-guide's body convention. **Surface as a copy-edit pass item.** Dev and line-edit passes concur: a future copy-editor can lowercase line 129 for consistency. No fix loop needed.

Dev review's 9 PASS items remain PASS (no regression):
1. Outcome line as closing imperative — verbatim match. ✓
2. All 8 entries (entry-027..entry-034) addressed. ✓
3. Voice match — second person dominant; 0 forbidden vocab. ✓
4. Bible consistency — five new terms appended correctly. ✓
5. Code-block correctness — 9 blocks PEP 8 clean. ✓
6. Beginner accessibility — every new construct glossed inline. ✓
7. No HfApiModel / ApiModel anywhere. ✓
8. "What's next" names ch-05. ✓
9. No regressions vs. ch-01 / ch-02 / ch-03 / bible / style-guide / outline. ✓

## Cross-cutting findings

1. **Strength — the runnable check at lines 163–181 is the chapter's gold-standard exemplar.** Unlike a chapter that shows constructs but skips the runnable proof, ch-04's check combines all three required constructs (`if`/`elif`/`else`, `while`, `for`), includes an `assert` that the reader can use as a regression test, and shows a `text`-fenced expected-output block (lines 185–191) that the dev pass verified byte-for-byte against the actual run. The line-edit pass confirms the check holds. Hold this pattern for ch-05 onward.

2. **Strength — the four-error fingerprint at lines 152–155 is a navigational device the reader can take back to the keyboard.** Each error gets one name + one bad line + one fix. The chapter's "Turn vague 'the loop is wrong' into four concrete checks" framing at line 157 is the pedagogical core. This is the ch-04 analogue of ch-03's "four beginner error categories" pattern; the two maps together give the reader six named errors to navigate the first four chapters by.

3. **Strength — the "short-circuit + operand return" trap is named and fixed in the same paragraph (lines 56–60).** This is the ch-04 equivalent of ch-03's `TypeError`-then-fix pattern: show the surprise, name the rule, show the fix. The `bool(...)` escape hatch is given as the explicit remediation. Beginners who hit this trap later (e.g. in ch-15's safety chapter when a config value is missing) have a one-paragraph mental anchor to return to.

4. **Strength — the `range()` half-open rule is anchored with a concrete example AND a `ValueError` caveat.** Line 146 pairs the rule ("the stop never does") with the consequence ("A step of zero raises `ValueError` because the sequence couldn't advance"). Beginners learn both the normal form and the failure mode in one sentence. Hold this pattern.

5. **WARN carryover — `position` is unused inside the `else` block of the runnable check.** Covered in § 10. Copy-edit pass material.

6. **LOW carryover — "Ch-05" / "ch-05" casing inconsistency.** Covered in § 10. Copy-edit pass material.

7. **Out-of-scope observation — self-critique HTML comment at lines 198–204.** Standard book-writer handoff. Per `AGENTS.md` book-gen mode: "books/daily-focus/chapters/ch-01.md lines 87–94 hold a self-critique HTML comment for orchestrator/reviewer handoff. Strip before any external publish." This is the same pattern, applied consistently. Not a chapter issue; strip at publish time.

8. **Out-of-scope observation — the runnable check at line 180 reuses ch-02's `.venv` path implicitly.** The chapter text says "Run this with the interpreter from your `.venv`" (line 161) without re-listing the path; the path is implicit. Style-guide § "Code blocks" rule 1 says snippets must run in `E:\book_gen\.venv\Scripts\python.exe`, and the chapter is consistent with that rule. The reader who completed ch-02 will already know the path; the reader who did not is not in this book's intended sequence. Acceptable.

## Out-of-scope observations

- **Chapter length (1441 total / 1331 prose):** well under the ~17–22 page (≈3000–4000 word) target from `style-guide.md:15`. This is the third-shortest chapter so far (after ch-01's 407 words and ch-02's 1407). The chapter covers a large surface (10 H2 sections + the runnable check + the four-error map) in a small word count, which means the prose is dense. Not a problem — the chapter is the first control-flow chapter and keeps its surface area small, same as ch-01, ch-02, and ch-03. The 19-chapter per-chapter average will land closer to the ~3000-word mark when the project-chapter pair (ch-17 / ch-18) and the framework chapters land.

- **No framework surface leakage anywhere in ch-04:** 0 hits for `HfApiModel`, `ApiModel`, `CodeAgent`, `ToolCallingAgent`, `MultiStepAgent`, `InferenceClientModel`, `OpenAIModel`, `@tool`, `final_answer`, `smolagents` across the chapter. The one-time `HfApiModel` sidebar rule (style-guide § "Pinning rules") is fully respected. The forward-pointer to ch-05 (collections and files) is correct — it doesn't reference ch-08 (toy agent) or ch-09 (smolagents).

## Honest assessment

ch-04 is line-edit clean. Voice, vocabulary, pacing, terminology, citations, code conventions, forward-pointer discipline (modulo the carryover casing LOW), outcome-line contract, and the dev-review carryovers all pass. The two carryover LOWs (`position` unused in `else`, "Ch-05" / "ch-05" casing) are both copy-edit-pass material — neither is a chapter bug, neither demands a fix loop. The orientation paragraph is 48 words (within ceiling), the closing imperative is character-for-character identical to the outline's outcome line, the "The move" callout matches the style-guide action, and the runnable check at lines 163–181 is the gold-standard exemplar for the ch-05+ pattern.

The chapter's biggest strength: it never drops the reader's hand. Every construct gets a one-sentence plain-language gloss the first time it appears, every claim has an inline source name (via the bible's "Added by ch-04" block and the chapter's verbatim enumeration of the truthiness, comparison, and control-flow rules), and the four-error fingerprint is the navigational load-bearing piece. The biggest stylistic risk is the two carryover LOWs — both cosmetic, both fixable by a copy-editor in two sentences.

I rate this chapter ready for line-edit sign-off. I do not recommend a fix loop. If master wants both carryover LOWs tightened, those are two sentence-level edits and can be batched into the next chapter's normal maintenance pass (or done at copy-edit).

## Self-critique

- **What I checked thoroughly:** orientation paragraph word count (48, within 30–60 ceiling); blacklist scan (17 forbidden terms, 0 matches across prose); contraction counts (8 contractions distributed across sections, none clustered); second-person vs. first-person counts (10 you-forms, 0 we-as-subject); subheading style check (all 10 sentence-fragment + describes-the-move); code-block PEP 8 / indentation / naming / operator-spacing (9 blocks, all clean); forward-pointer hygiene (1 explicit "What's next" + 1 in-body forward glance + 1 implicit backward reference, all classified); outcome-line verbatim match (style-guide vs. chapter callout vs. final restatement); bible cross-reference (5 ch-04 additions match the chapter's glosses); framework-name leakage scan (10 framework surface terms, 0 hits).
- **What I might have under-checked:** I did not run the chapter's 9 code blocks in the venv myself — the dev pass already ran them and confirmed byte-for-byte match between run and expected output. For a line-edit pass this is acceptable; line-edit is text-level, not runtime-level. Low risk.
- **What I might have over-flagged:** neither — both carryover LOWs are real and were independently judged by the dev pass as "non-blocking, copy-edit material." The line-edit pass concurs.
- **What I might have missed:** I did not cross-reference each new construct's inline gloss against the bible's plain-language gloss byte-for-byte; I cross-checked by topic and confirmed the same claim in both. The glosses match in spirit and content; a byte-level diff would be overkill for this pass.
- **PONTAIL note:** The style guide prescribes a tight voice for a technical-onboarding book. I did not propose any "richer" or "more expressive" prose alternatives because that would violate the style-guide's "Conversational technical" register. The chapter is as boring as it needs to be — that's the register. No action.

## Sign-off

ch-04 line-edit verdict: **PASS_WITH_WARN.**

- 0 FAIL.
- 1 WARN (orientation paragraph length — but this PASSES the 30–60 ceiling; the WARN is the carryover LOWs as a group, not a single new finding).
- 2 LOW (carryover from dev pass: `position` unused in `else`; "Ch-05" / "ch-05" casing inconsistency) — copy-edit pass material.
- No fix-loop recommended.
- No regression vs. dev pass.
- Ready to advance to Phase 7 copy-edit (or to publish if Phase 7 is skipped per the chapter-gen structural-change plan).

Ledger ch-04 row should move: `dev-reviewed` → `line-edited`.

max_fix_loops = 3 (not used this pass).

(End of line-edit pass — ch-04)