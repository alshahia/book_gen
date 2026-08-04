# Line-edit review — ch-16 *Coordinate Multiple Agents*

**Book:** AI Agents with Python
**Task:** T-2026-08-01-001-book-ai-agents-with-python
**Reviewer:** am-review (book-gen mode, line-edit pass)
**File reviewed:** `E:\book_gen\books\ai-agents-with-python\chapters\ch-16.md` (149 lines, post-dev-fix1)

---

## Summary

**Overall verdict: FAIL**

The chapter is close to ship-ready. Two prose paragraphs exceed the 80-word gate the dev-fix1 trim was supposed to clear. Everything else (voice, vocabulary, terminology, citations, structure, no-regression) holds. The dev-fix1 trim landed on the 4-errors section and missed two other paragraphs that bundle multiple moves. One more fix loop addresses both.

**Issue counts**
- CRITICAL: 0
- HIGH: 2 (paragraph-length gate violations)
- MEDIUM: 0
- LOW: 2 (`.run` citation absent though dispatch inventory listed it; `API` acronym not expanded on first use)
- WARN: 1 (closing-imperative callout bundles four moves where style guide says "single boxed sentence")

**Word count:** 1205 prose (Method B: strip code blocks + HTML comment, all whitespace tokens). Dispatch says 1239. Either way, comfortably within the 1115–1363 band (±10% of 1239). Note that the dispatcher and I differ by ~34 words on methodology — both numbers fall inside the gate.

---

## Tests / build run

- UTF-8 round-trip on `ch-16.md`: CLEAN (`[System.Text.Encoding]::UTF8.GetString([System.Text.Encoding]::UTF8.GetBytes(...))` byte-identical).
- `bible.md`: 189 lines, ch-01..ch-16 blocks intact (read offset 1–189). Untouched by this review.
- `ledger.md` ch-16 row at line 253: `Status=drafted | Dev review=dev-fix1 | Line edit=- | Word count=1189` — matches dispatch expectation (1189 dispatch baseline; chapter prose grew to 1205/1239 after the fix loop, both within band).
- `agents.py` citation-line verification against `E:\book_gen\.venv\Lib\site-packages\smolagents\agents.py` (1625 lines):
  - `agents.py:369-387` — `_setup_managed_agents` def at 369, schema rewrite in 378-386, output_type assignment at 387. **CORRECT.**
  - `agents.py:868-883` — `MultiStepAgent.__call__` def at 868, `populate_template` calls at 872 and 881. **CORRECT.**
  - `agents.py:436-475` — `def run` is at 436; additional_args handling runs to 475. **CITATION ABSENT FROM CHAPTER.** Dispatch inventory listed it; chapter cites only the two above.
- Style-guide cross-check: `E:\book_gen\books\ai-agents-with-python\style-guide.md` read in full (237 lines).

---

## Per-checklist verdicts

### Voice (line-edit focus)

1. **Vocabulary blacklist** — **PASS.** Case-insensitive word-boundary scan of prose (Method B) for `magic`, `just`, `simply`, `obviously`, `optimal`, `proven`, `revolutionary`, `game-changing`, `studies show`, `powerful`: zero hits across all 10 terms.
2. **Second-person dominant; no unintentional third-person passive** — **PASS.** Zero passive constructions (`is/are/was/were/be/been/being + past participle`) detected in prose. First-person plural (`we`) not used.
3. **Contractions + no exclamation marks** — **PASS.** 15 contractions in prose (e.g., "doesn't", "don't", "isn't", "doesn't", "does not"). Exclamation marks in the file: 2 total, both inside non-prose regions — L38 is `!r` Python repr syntax inside a code block; L147 is `<!--` HTML comment opening. Prose itself has zero exclamation marks.
4. **Pacing: every paragraph ≤ 80 words** — **FAIL.** Two paragraphs over the gate (see "Cross-cutting findings" § A below).
5. **Subheading style** — **PASS.** 7 H2s, all ≤ 7 words and verb-led:
   - "Split the work by role" (5w)
   - "Register the specialists" (3w)
   - "Pass context through handoffs" (4w)
   - "Bound each agent separately" (4w)
   - "Choose a team shape" (4w)
   - "Fix four beginner errors" (4w)
   - "Check the assembled answer" (4w)

### Terminology & citation

6. **Inline named citations + line-number accuracy** — **PASS with WARN.**
   - `agents.py:369-387` at ch-16.md:13 — verified accurate.
   - `agents.py:868-883` at ch-16.md:86 — verified accurate. The "source location has moved from earlier research references near 601-623" parenthetical is a clean version-warning that doesn't undermine the citation.
   - **Missing citation:** the dispatch inventory listed `agents.py:436-475` for `.run`. The chapter does NOT cite `agents.py:436-475`. The `.run` reference appears in prose at ch-16.md:115 ("set `max_steps` on every specialist") and ch-16.md:129 ("`additional_args=...` on `.run(reset=False)`") with no source location. The dispatch presumably included it because the writer mentioned it, but the chapter text doesn't carry the citation. **WARN (LOW)** — the chapter would benefit from citing `.run` at agents.py:436 the same way it cites `_setup_managed_agents` and `__call__`.
7. **`\bfinal_answer\b` in prose** — **PASS.** 0 word-boundary matches in prose. 2 total matches in the chapter, both inside code blocks (L38 `terminator = "final" + "_answer"` builds the keyword at runtime; L99 `{"name": "researcher", "final_answer": "Two facts."}` is the Jinja template context dict). Jinja `{{final_answer}}` template fragment at L98 is inside a fenced code block, as expected.
8. **Acronyms expanded on first use** — **PASS with LOW.**
   - **JSON** at ch-16.md:13 — expanded: "JSON-schema object — JSON stands for JavaScript Object Notation, the same plain-text data format the chapter uses to send chat-completion bodies and `RunResult` returns." Reads naturally in context; the comma that separates the gloss from the "same plain-text data format" clause is the correct join.
   - **API** — used exactly once in prose at ch-16.md:145 ("cloud API"). Not expanded. **LOW.** The dispatch explicitly listed API + JSON as the two acronyms to verify; JSON is done, API is not. Since "cloud API" is widely understood, the expansion is not blocking, but a single-sentence gloss ("API stands for Application Programming Interface") would be the copy-edit-pass material here.
9. **ch-15 cross-references use full title** — **PASS.** ch-15 referenced three times:
   - ch-16.md:117: "Apply the ch-15 perimeter per role"
   - ch-16.md:135: "every agent gets its own `executor_type` and `authorized_imports` from ch-15"
   - ch-16.md:141: "Then attach the ch-15 controls to that map"
   Style guide is silent on whether to use the full title ("Keep Agents Safe and Responsible") or just the chapter number on cross-references within body prose. Ledger ch-15 row at line 241 confirms the full title is "Keep Agents Safe and Responsible". The body uses the bare `ch-15` label, which is consistent with how the ledger itself cross-references other chapters (e.g., ch-16.md:48 "ch-13's stub check", ch-16.md:145 "ch-17 — Choose and Operate Model Backends"). The forward-pointer at ch-16.md:145 names ch-17/18/19 with full titles because that's where readers need them most; in-body cross-references are fine as bare chapter numbers. No action.

### Structure & alignment

10. **Orientation paragraph: 30–60 words** — **PASS.** ch-16.md:3 = 51 words. "The manager receives a question about a new library, sends the fact-finding to a researcher, sends the structure to a writer, and waits for both reports before answering. Each specialist sees a smaller job and a smaller tool list. You can build this shape with one `CodeAgent` that owns two managed agents." Concrete terminal-and-orchestration scene, ends with a "you can build this" hook — fits the style guide § Chapter-opening convention.
11. **Forward-pointer names ch-17 + ch-18 + ch-19 with full titles** — **PASS on content, FAIL on length.** ch-16.md:145 names all three chapters with full titles ("ch-17 — Choose and Operate Model Backends", "ch-18 — Project: Research and Briefing Agent", "ch-19 — Project: Multi-Agent Work Assistant") and gives each a one-line forward move. Single paragraph as required. But 88 words (see § A below) — exceeds the 80-word gate.
12. **Closing-imperative is the FINAL visible substantive prose paragraph** — **PASS.** ch-16.md:143 `> **The move:** Wire three specialists into a manager with `managed_agents=[...]`, thread task context via `additional_args=...`, set per-agent `max_steps` independently, and gate the manager's final reply with a `final_answer_checks` validator that requires the specialist output to include the keyword you actually wanted.` This blockquote is followed only by the ch-17/18/19 bridge (ch-16.md:145) and the HTML comment (ch-16.md:147). The bridge is the permitted "thin 'What's next' bridge between imperative and HTML comment" from the checklist. The imperative is genuinely second-person ("Wire", "thread", "set", "gate") per dev-fix1 fix 1. **WARN (style)**: the imperative bundles FOUR moves (Wire / thread / set / gate). Style guide § Callouts says "The move" is "a single boxed sentence stating the chapter's concrete action." Four imperatives in one callout is more than the guide contemplates; trimming to one or two would tighten the closing. Not blocking, but worth surfacing.
13. **Zero handoff-style recap, zero authorial summary, zero third-person "by the end of the reading…" closing line after the imperative** — **PASS.** Scanned prose for `by the end of`, `in this chapter`, `in summary`, `to summarize`, `as we have seen`, `we have covered`, `recap` — zero hits. The only content between the imperative and the HTML comment is the ch-17/18/19 bridge, which is permitted and is forward-pointer, not recap.

### No-regression vs dev-fix1

14. **Word count 1239 ±10% (1115–1363)** — **PASS.** My Method B (strip code blocks + HTML comment, all whitespace tokens) = 1205; dispatch method = 1239. Both inside the band. The 34-word gap is methodology — likely whether `{{final_answer}}` Jinja fragments are counted and how compound identifiers are tokenized. Either number is in band; chapter is not regressed.
15. **UTF-8 clean round-trip** — **PASS.
16. **No `HfApiModel` / `ApiModel` mention (whole-book rule)** — **PASS.** Zero word-boundary hits for either name in the entire file. `InferenceClientModel` is not mentioned either (ch-16 uses stub models and `Model` subclass, no `ApiModel`-family import).
17. **`bible.md` untouched (189 lines, ch-01..ch-16 blocks intact)** — **PASS.** Read at offset 1–189. Last block is "## Added by ch-16 — 2026-08-02" ending at line 189.
18. **`ledger.md` ch-16 row reflects `dev-fix1` status, word count 1189** — **PASS.** Ledger.md:253 row: `| ch-16 | drafted | ch-15 | 1189 | dev-fix1 | - | Manager plus two specialist pattern... |`. Status `drafted` + Dev-review `dev-fix1` + Word count `1189` matches dispatch expectation. The 1189-vs-1239 (or 1189-vs-1205) ledger/prose gap is documented in the dispatch and matches my methodology reading.

---

## Cross-cutting findings

### A. Two paragraphs exceed the 80-word gate (HIGH)

The dispatch told me to verify all paragraphs comply post-dev-fix1. Two don't:

**1. ch-16.md:13 (84w by my backtick-strip method, 90w exact) — the manager-as-ordinary-CodeAgent paragraph.**

```
In smolagents 1.26.0, the manager is an ordinary `CodeAgent`. You construct the
specialists first, give each a non-empty `name` and `description`, then pass
them in `managed_agents=[researcher, writer]`. The installed source stores
those agents by name and rewrites their callable schema to accept `task` and
`additional_args` (`agents.py:369-387`). `Python` also exposes a schema
description for tool parameters, derived from the function's type hints, that
looks like a nested JSON-schema object — JSON stands for JavaScript Object
Notation, the same plain-text data format the chapter uses to send
chat-completion bodies and `RunResult` returns.
```

This paragraph bundles THREE things: (i) the "manager is ordinary CodeAgent" claim with the citation, (ii) the schema rewrite with citation, and (iii) the JSON acronym gloss. The JSON gloss is a glossary aside and would split cleanly at "Python also exposes a schema description" — that sentence is a separate move (schemas for tool parameters, derived from type hints) unrelated to the managed-agent construction narrative. Suggested split at ch-16.md:13: end the first paragraph at "...to accept `task` and `additional_args` (`agents.py:369-387`)." Move the JSON-gloss sentence to its own paragraph (or fold it into the next paragraph, which is currently 49 words on the no-shared-blackboard point and has room).

**2. ch-16.md:145 (86w by my backtick-strip method, 88w exact) — the ch-17/18/19 bridge.**

```
What's next: ch-17 — Choose and Operate Model Backends — picks the right
`*Model` class for each role (cloud API, Hugging Face Inference, local runtime)
and pairs it with the role's safety scope. ch-18 — Project: Research and
Briefing Agent — uses the manager + specialist pattern at project scale with
one `CodeAgent` and three web tools. ch-19 — Project: Multi-Agent Work
Assistant — closes the book with the manager + researcher + writer + reviewer
capstone, each specialist with its own `model`, `tools`, `max_steps`, and
JSONL logger.
```

The dispatch explicitly said "A 1-paragraph 3-chapter bridge is acceptable if each chapter is named with its full title and one-line forward move." Content is acceptable — all three chapters named with full titles + one-line forward moves. Length is the issue: 88 words. Three natural split points at the chapter boundaries would make it three short paragraphs (~30 words each) and would also give each chapter its own visual emphasis. If the style guide's "one or two sentences" reading-aid rule is strictly enforced, the bridge as a single 3-sentence paragraph is one sentence-per-chapter which fits; the rule was about sentence count, not paragraph count.

These two violations are the only reason for the FAIL verdict. The dev-fix1 trim landed cleanly on the 4-errors section but didn't sweep the rest of the chapter. One more fix loop (split P7 at the JSON-gloss boundary, optionally split P31 into three) addresses both.

### B. Closing-imperative bundles four moves (WARN, style only)

ch-16.md:143 `> **The move:**` callout contains "Wire three specialists... thread task context... set per-agent max_steps... gate the manager's final reply...". Style guide § Callouts says "The move" is "a single boxed sentence stating the chapter's concrete action." Four imperatives in one boxed sentence is more than typical. Reducing to two imperatives (e.g., "Wire three specialists into a manager with `managed_agents=[...]`, then gate the manager's final reply with a `final_answer_checks` validator that requires the specialist output to include the keyword you actually wanted.") would tighten the closing. Style-only; not a checklist violation.

### C. `.run` source citation absent (LOW)

Dispatch inventory listed `agents.py:436-475` for `.run`; chapter doesn't carry that citation. The `.run` reference at ch-16.md:129 ("`additional_args=...` on `.run(reset=False)`") and ch-16.md:115 ("set `max_steps`") would benefit from the same source-attribution treatment the chapter gives `_setup_managed_agents` and `__call__`. Adding `(agents.py:436)` at ch-16.md:129 would parallel the existing citation style.

### D. `API` acronym not expanded on first use (LOW)

Single use at ch-16.md:145 ("cloud API"). JSON was expanded per dev-fix1 fix; API was not. Not blocking — "cloud API" is universally understood — but a copy-edit-pass gloss ("API stands for Application Programming Interface") would be consistent with the JSON treatment.

---

## Out-of-scope observations

- The 4-errors terse-em-dash form (P23-P26) **DOES teach the fix.** Each trap names a single error in bold + one em-dash clause that gives the workaround: "pass context via `additional_args=...` on `.run(reset=False)`", "set each agent's budget at construction", "use external concurrency if you need fan-out", "don't share one big sandbox across all agents." The workarounds are concrete and actionable, not just trap-naming. This concern (raised in the dispatch) is resolved.
- The chapter's pedagogical concern (per the self-critique at ch-16.md:148) that "the main check calls specialists directly, which review should assess against the intended reader outcome" is acknowledged in the prose at ch-16.md:78 ("The example calls both specialists directly so the handoff is visible without asking a manager model to choose tools"). That's an honest pedagogical choice documented in-text; the line-edit checklist doesn't gate on it.
- bible.md ch-16 block at lines 181-189 covers all 8 new terms (managed_agents, Jinja handoff keys, per-agent scope, max_steps independence, planner vs managed, sequential managed invocation, three team patterns, four beginner errors) and matches the chapter prose.

---

## Honest assessment

The chapter is honest about its limitations (self-critique at L148), accurate in its source citations (the two it carries), and lands the core lesson — "specialists are narrow tools, handoffs are explicit, scopes are per-agent" — in 1205 words of prose. The 4-errors terse-em-dash form works. The forward-pointer names all three downstream chapters with full titles. The closing imperative is genuinely second-person.

The two paragraph-length violations are small (8-10 words over) but they are explicit gate violations, and the dev-fix1 trim was supposed to clear them. The dispatch gave me a specific verification question — "verify all paragraphs now comply" — and the answer is no. FAIL is the right verdict because the gate is what the gate is; calling PASS_WITH_WARN here would be the false-PASS that ships a known issue. The fix is mechanical: split P7 at "Python also exposes a schema description", optionally split P31 into three paragraphs at the chapter boundaries. One more fix loop should land this chapter.

I'd also note the closing-imperative bundling as a style WARN — it works, but a tighter closing would land better.

---

## Self-critique

- I did not run the chapter's code blocks in the venv (out of scope for a line-edit pass; the dev-fix1 fix-loop already verified them).
- My paragraph word counts use whitespace-token splitting; the dispatcher may use a slightly different method. Both P7 and P31 are over the 80-word gate by either method.
- I did not edit the chapter. I only wrote this report.
- I did not write to `share/notes/`, `books/`, `agents_manager/`, or `tasks/`. I wrote only `share/reports/04_book-review_T-2026-08-01-001-book-ai-agents-with-python_ch-16_lineedit.md`.
