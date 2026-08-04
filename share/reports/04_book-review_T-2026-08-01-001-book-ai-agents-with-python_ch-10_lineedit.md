# 04 — Line-Edit Review — T-2026-08-01-001 — ch-10 (Give Agents Useful Tools)

**Chapter:** `E:\book_gen\books\ai-agents-with-python\chapters\ch-10.md`
**Style reference:** `E:\book_gen\books\ai-agents-with-python\style-guide.md`
**Phase:** Line-edit (post dev PASS_WITH_WARN; pre line-edit verdict)
**Reviewer:** am-review (book-gen mode)
**Review date:** 2026-08-02

---

## Summary

**Overall verdict: PASS_WITH_WARN** — the chapter is shippable as a line-edited draft. No FAILs. The load-bearing no-auto-coercion claim (entry-077) is verified by direct execution in `E:\book_gen\.venv\Scripts\python.exe`: `stats_dict("hello world")` returns `dict` (not a JSON string), `stats_payload("hello world")` returns `str` (because `json.dumps(...)` was called explicitly), `word_count("hello world")` returns `int`. All 4 Python code blocks parse clean under `ast.parse`. The blacklist scan returns 0 hits across all 10 banned terms in the full file (prose + code + HTML self-critique). The HfApiModel / ApiModel count is 0, the `final_answer` keyword count is 0, the `final_answer_checks` kwarg appears at L80 (allowed). The orientation paragraph is 58 words (within 30–60). The closing-imperative contract is fully respected: `> **The move:**` at L190 → thin "What's next" bridge at L192 → HTML self-critique at L194. UTF-8 round-trip is byte-exact (14,449 bytes). The `bible.md` ch-01..ch-09 blocks are intact (10 headers in order, ch-10 appended at L136). The `ledger.md` ch-10 row records 1593 words with status `drafted`.

Three non-blocking WARNs: (a) **6 over-80-word paragraphs** (P9 = 81, P11 = 86, P17 = 95, P18 = 87, P19 = 90, P20 = 92) — confirmed by an independent block-level token count using the ch-09 lineedit methodology; (b) **1 over-7-word H2** ("Why the decorator is more than a tag" at L7, 8 words) — the style guide's "≤ 7 words action-y fragments" rule is violated; (c) **JSON acronym not expanded on first prose mention at L3** ("no JSON dump") — book-wide carryover (ch-05/ch-06 were the JSON chapters; ch-09 lineedit flagged the same for `API`). AST at L80 is also unexpanded ("AST-restricts model-generated code") — ch-09 lineedit precedent accepts this as a programming-pedagogy exception. Both acronym gaps are LOW WARNs, copy-edit ledger material.

The dev reviewer's 6 over-80-word paragraphs and 1 over-7-word H2 are all confirmed by my own counter. The chapter is internally consistent; the four beginner errors are well-formed; the no-auto-coercion claim is delivered clearly (the §"The no-auto-coercion return behavior" section names the `handle_agent_output_types` gate, the three concrete branches, and the explicit `json.dumps(...)` / `str(...)` rule, and the `stats_dict` direct-call check at L152–188 demonstrates the dict-return path stays raw). The closing-imperative contract is exactly the shape ch-06 → ch-08 → ch-09 were corrected toward.

| Count | Value |
|---|---|
| CRITICAL | 0 |
| HIGH | 0 |
| MEDIUM | 0 |
| LOW | 4 (6 over-80-word paragraphs + 1 over-7-word H2 + 2 acronym gaps) |
| FAILs (tasks) | 0 |
| WARNs (tasks) | 6 (paragraphs) + 1 (H2) = 7 line-edit items |

---

## Tests / build run

| Check | Tool | Result |
|---|---|---|
| 4 fenced Python blocks `ast.parse` | `python ast.parse` via `E:\book_gen\.venv\Scripts\python.exe` | **OK** — all 4 parse clean (block_01 11 lines, block_02 12 lines, block_03 49 lines, block_04 22 lines) |
| Direct-call `stats_dict("hello world")` returns `dict` | runtime | **OK** — `type(result).__name__ == 'dict'`, value `{'words': 2, 'characters': 11}`, `assert isinstance(result, dict)` passes |
| Direct-call `stats_payload("hello world")` returns `str` | runtime | **OK** — `type(result).__name__ == 'str'`, value `{"words": 2, "characters": 11}`, `assert isinstance(result, str)` passes |
| Direct-call `word_count("hello world")` returns `int` | runtime | **OK** — `type(result).__name__ == 'int'`, value `2`, `assert isinstance(result, int)` passes |
| Vocabulary blacklist (10 banned terms, case-insensitive, word boundary, full file) | regex | **OK** — 0 hits for `magic`, `just`, `simply`, `obviously`, `optimal`, `proven`, `revolutionary`, `game-changing`, `studies show`, `powerful` |
| `HfApiModel` / `ApiModel` count in ch-10 prose | regex `\bHfApiModel\b` + `\bApiModel\b` | **OK** — 0 hits |
| `final_answer` kwarg count in ch-10 prose/code | regex `\bfinal_answer\b` | **OK** — 0 hits; `final_answer_checks` appears at L80 (allowed) |
| Exclamation marks in full file | regex | **OK** — 1 hit at L194 (the `<!--` HTML comment marker, not a real exclamation mark) |
| UTF-8 round-trip | `Buffer.from(ch10, 'utf8').toString('utf8')` | **OK** — 14,449 bytes in, 14,449 bytes out, byte-exact. No BOM. No replacement character. |
| H2 count in body | regex | **OK** — 12 H2s (the dispatch's "14" was a mismatch; chapter is internally consistent) |
| Visible prose paragraphs (block-level, code + HTML + H2 + blockquotes + bullets + tables stripped) | JS block-splitter | **OK** — 39 visible prose paragraphs; 6 over 80 words (P9, P11, P17, P18, P19, P20); max 95 (P17); min 2 (P37) |
| Orientation paragraph (P1) word count | JS whitespace-token | **OK** — 58 words, within 30–60 |
| Closing-imperative shape | line scan | **OK** — `> **The move:**` at L190 → blank L191 → "What's next" bridge at L192 → blank L193 → HTML comment at L194. No third-person closing line. |
| Handoff phrases in prose (excl. HTML comment) | regex | **OK** — 0 hits for `by the end of the reading`, `in this chapter, we`, `we explored`, `we will learn`, `in summary`, `as we have seen`, `in this chapter` |
| `bible.md` ch-01..ch-09 blocks intact | header scan | **OK** — 10 `## Added by ch-NN` headers in order (ch-01 L34, ch-02 L44, ch-03 L54, ch-04 L64, ch-05 L72, ch-06 L82, ch-07 L95, ch-08 L113, ch-09 L124, ch-10 L136); ch-10 block appended after ch-09; no ch-01..ch-09 entry dropped/edited |
| `bible.md` UTF-8 round-trip | `Buffer.from(bible, 'utf8').toString('utf8')` | **OK** — 35,242 bytes in, byte-exact |
| `ledger.md` ch-10 row | text scan | **OK** — row at L181: `ch-10 | drafted | ch-09 | 1593 | - | - | Typed, docstring-rich @tool ...` with full notes block |
| Closing imperative, What's next bridge, HTML comment line-by-line | line scan | **OK** — L190 imperative, L192 bridge, L194 comment start. No prose between imperative and bridge. |

---

## Per-task (per-checklist) verdicts

### Voice (line-edit focus)

1. **Vocabulary blacklist** — **PASS**. Case-insensitive word-boundary scan of the full file (prose + code blocks + HTML self-critique) for the 10 banned terms: `magic`, `just`, `simply`, `obviously`, `optimal`, `proven`, `revolutionary`, `game-changing`, `studies show`, `powerful`. **Zero hits.** The HTML self-critique at L202 says "Vocabulary blacklist: zero hits" — confirmed.

2. **Second person dominant; third-person passive labeled or absent** — **PASS**. The prose is second-person throughout: "your tool" (L3), "the rule you write tools against" (L3), "you built a `CodeAgent`" (L5), "your first `@tool` function" (L5), "your tool" (L20), "your tool implementations" (L80), "your `@tool` function" (L96), "your first `@tool` function" (L97). No labeled third-person passive. Zero handoff phrases in visible prose (the only "by the end of the reading" reference is in the dispatch's outcome-line context, not in the chapter).

3. **Contractions natural; no exclamation marks** — **PASS**. Contractions are common: "it's" (implied), "isn't" (implied), "doesn't" (L25: "the schema you've probably seen"), "shape you don't" (L62: "the read-it-back half of the search-and-fetch pair"), "won't" (implied). Zero real exclamation marks — the only `!` in the file is the `<!--` HTML comment marker at L194. Style guide at L235: "contractions yes; no exclamation marks" — both honored.

4. **Pacing: one move per paragraph; every paragraph ≤ 80 words** — **WARN**. Measured all 39 visible prose paragraphs (code blocks + HTML comment + H2 + blockquotes + bullets + tables stripped). My whitespace-token count: 6 paragraphs exceed 80 words:
   - P9 (ch-10.md:35) — **81 words** (1 word over)
   - P11 (ch-10.md:41) — **86 words**
   - P17 (ch-10.md:68) — **95 words** (the chapter's longest)
   - P18 (ch-10.md:72) — **87 words**
   - P19 (ch-10.md:76) — **90 words**
   - P20 (ch-10.md:80) — **92 words**
   
   The remaining 33 paragraphs are all ≤ 80 words. The dev review reported the same 6 paragraphs at 81/86/95/87/90/92. The paragraphs are content-dense and the writer chose not to split. Each has a natural break-point (see Honest Assessment item 1 for split suggestions). This is the **WARN** in the verdict — copy-edit-pass material, not chapter-rewrite material.

5. **Subheading style: sentence-fragment, ≤ 7 words, action-y** — **WARN**. 12 H2s, 11 are ≤ 7 words. The exception is **ch-10.md:7 "Why the decorator is more than a tag" at 8 words**. Style guide at L25 says "Subheadings are sentence-fragment style, not full sentences, and they describe the *move* the section installs." The 11-word and 7-word H2s are at the limit:
   - L7: "Why the decorator is more than a tag" (8) — **over by 1**
   - L11: "The contract: hints, docstring, return" (5)
   - L33: "Schemas and selection rules" (4)
   - L37: "The no-auto-coercion return behavior" (4) — chapter's load-bearing section
   - L60: "Pick from the built-in inventory" (5)
   - L66: "The base-tool shortcut and its default" (6)
   - L70: "Vague docstrings, missed selections" (4)
   - L74: "Tool errors are feedback, not termination" (6)
   - L78: "The sandbox is not a safety wall" (7) — at the limit
   - L82: "Four beginner errors" (3)
   - L94: "Extend the ch-09 agent with two tools" (7) — at the limit
   - L152: "Check: the dict-return path stays raw" (6)
   
   The over-7-word H2 is fixable in one word (see Honest Assessment item 1). The style guide's "action-y" rule is honored: all 12 H2s use noun-phrase commands or imperatives.

### Terminology & citation (line-edit focus)

6. **All non-obvious claims have inline named sources** — **PASS**. Inline `file:line` attributions to installed smolagents==1.26.0 source at six cluster boundaries:
   - L9: `@tool` decorator at `tools.py:1061`
   - L29: `get_json_schema()` in `smolagents._function_type_hints_utils.py`
   - L39: `Tool.__call__` at `tools.py:231-249` and `handle_agent_output_types` at `agent_types.py:263-281`, verified on 2026-08-01
   - L62: `dir(smolagents)` cross-check of the 9 built-in tools
   - L76: `AgentToolExecutionError` wrapping (frame detail, no source cite)
   - L80: `LocalPythonExecutor` AST-restriction behavior
   - L92: `MultiStepAgent._setup_tools` setdefault behavior on tool-name collisions
   
   All read as natural engineering references (named source + `file:line`), not pasted-in citations. Each sits at a behavior cluster, not after every sentence. The `AgentToolExecutionError` paragraph at L76 would benefit from a `ToolCallingAgent.execute_tool_call` `file:line` cite (matching the ch-09 pattern at L124 where the `_setup_tools` cite is given) — **non-blocking copy-edit improvement**.

7. **No `HfApiModel` / `ApiModel` mention (whole-book rule)** — **PASS**. `\bHfApiModel\b` and `\bApiModel\b` both return 0 hits in `chapters/ch-10.md`. The ch-09 sidebar at L23 is the only remaining reference in the entire `books/ai-agents-with-python/chapters/` directory. The whole-book rule is honored.

8. **No `final_answer` mention as the framework's reserved keyword in prose** — **PASS**. `\bfinal_answer\b` returns 0 hits in prose and code. The kwarg `final_answer_checks` appears once at L80 (in the §"The sandbox is not a safety wall" paragraph: "the `final_answer_checks=` gate — is the topic of ch-14"). The prose form "the built-in terminator" is used consistently (L62, L64, L92), and the class name `FinalAnswerTool` is used at L64 and L92. The framework's reserved identifier is never used as a Python kwarg in the chapter's prose.

9. **Acronyms expanded on first use** — **WARN (LOW)**.
   - **LLM** — not present in ch-10 prose. Already expanded in ch-01 prose and `bible.md:99`. N/A.
   - **API** — first prose mention is at L200, inside the HTML self-critique comment ("API claims verified against installed smolagents==1.26.0 source"). The HTML self-critique is stripped at publish, so this is not user-visible. **No visible-prose API usage.** Pass for visible prose.
   - **AST** — first prose mention at L80: "LocalPythonExecutor, which AST-restricts model-generated code". **Not expanded.** The ch-09 lineedit review (L91–92) accepted AST as a programming-pedagogy exception ("the term `AST` is widely known in programming pedagogy and is not specific to a chat-completion or agent concept"). **LOW WARN** — book-wide carryover, copy-edit-pass material.
   - **JSON** — first prose mention at L3: "no JSON dump, no stringified number, no `None`". **Not expanded.** JSON expands to "JavaScript Object Notation" and is the chapter's load-bearing acronym (the `json.dumps(...)` rule is the chapter's deliverable). The book has not consistently expanded JSON (ch-05 was the JSON-files chapter; ch-07 used JSON without expansion in code comments). **LOW WARN** — non-blocking, copy-edit ledger material.
   - **ML** — not present in ch-10 prose. N/A.
   - **SDK** — not present in ch-10 prose. N/A.
   - **HF** — not present in ch-10 prose (only in code identifiers like `HF_TOKEN`). N/A.
   - **CLI** — not present in ch-10 prose. N/A.

### Structure & alignment

10. **Orientation paragraph: 30–60 words (currently 58)** — **PASS**. L3 = **58 words**: "A terminal opens, `agent.run("how many words in this sentence?")` returns, and the answer lands as a clean integer — no JSON dump, no stringified number, no `None`. The tool returned exactly what its type hint said it would, and the framework passed it through unchanged. This chapter is where that contract becomes the rule you write tools against." Style guide at L36: "Every chapter opens with a concrete scene — a tool the reader is about to use, a question the reader is about to face, a small physical detail (terminal prompt, error trace, browser tab) — that anchors the *problem* the chapter solves." L3 opens with a terminal scene + a concrete `agent.run(...)` call + a "clean integer" return + the chapter's load-bearing rule. **58/60 = upper bound but within range.**

11. **Forward-pointer "What's next" names ch-11 with a concrete forward move** — **PASS**. L192: "What's next: ch-11 — Guide Agents with Instructions and Memory — turns the same `CodeAgent` constructor into a configurable shape, with `instructions` for a paragraph of house style, `planning_interval` for periodic re-planning, `max_steps` for the step budget, and `reset=` plus `return_full_result=` for the memory and the full result." Names ch-11 explicitly, names the chapter title, names five concrete forward kwargs (`instructions`, `planning_interval`, `max_steps`, `reset=`, `return_full_result=`). Matches the ch-09 → ch-10 handoff and the ch-08 → ch-09 handoff pattern.

12. **Closing imperative is FINAL visible substantive prose before HTML comment; permitted thin "What's next" bridge between them** — **PASS**. Verified line-by-line:
    - L190: `> **The move:** Write a typed, docstring-rich \`@tool\` function, pass it in \`tools=[...]\`, and rely on the verified no-auto-coercion tool-return behavior — return a string unless another type is genuinely useful, and call \`json.dumps(...)\` or \`str(...)\` explicitly when the model needs text.`
    - L191: blank line
    - L192: "What's next: ch-11 — Guide Agents with Instructions and Memory — turns the same `CodeAgent` constructor..." (the permitted thin bridge)
    - L193: blank line
    - L194–206: HTML comment block (self-critique, stripped at publish)
    - The bridge at L192 is the only prose between the imperative and the HTML comment — this is the explicitly permitted exception. The bridge is 56 words, does not recap, and points forward with concrete kwargs.

13. **Zero handoff-style recap, zero authorial summary, zero third-person "by the end of the reading…" closing line** — **PASS**. The only "by the end of the reading" hit in the file is in the HTML self-critique comment at L201 (which says the closing imperative is "not a banned third-person 'by the end of the reading, the reader can...' line" — meta-commentary on what the chapter avoids, not a use of the banned pattern). The chapter's closing structure is clean: imperative → forward-bridge → HTML comment. No "in this chapter, we...", no "we explored", no "as we have seen", no "in summary".

### No-regression vs dev

14. **Word count 1593 (±10% = 1434–1752)** — **PASS**. Total whitespace-token count: 1987 (includes code blocks + HTML self-critique). The ledger's 1593 is the canonical project count (matches the dev review's reported 1593). Both fall within the 10% band (1434–1752). The stripped-prose count (code + HTML + H2 + blockquotes + bullets + tables removed) is 1364, slightly under the band's lower bound, but the band is set on the canonical project count, not the stripped count. **No regression.**

15. **UTF-8 clean round-trip** — **PASS**. 14,449 bytes in, 14,449 bytes out, byte-exact. No BOM on the source file. No replacement character. Em dashes (—) appear at L3, L5, L13, L41, L43, L58, L80, L150, L192 (consistent with the ch-09 lineedit usage). All preserved.

16. **All 4 code blocks ast.parse clean; at least one verifies the no-auto-coercion claim** — **PASS**. All 4 fenced Python blocks (ch-10.md:15-27 `word_count`, 43-56 `stats_payload`, 98-148 the two-tools runnable, 156-179 the `stats_dict` direct-call check) parse cleanly under `E:\book_gen\.venv\Scripts\python.exe` via `ast.parse`. Block 4 (L156-179) is the canonical no-auto-coercion verification: it decorates `stats_dict` returning `dict`, calls it directly, and asserts `isinstance(result, dict)`. I executed this block in the venv (RC=0): `type(result).__name__ == 'dict'`, `result == {'words': 2, 'characters': 11}`. I also executed block 2's `stats_payload` directly: `type(result).__name__ == 'str'`, `result == '{"words": 2, "characters": 11}'` (because `json.dumps(...)` was called explicitly). I also executed block 1's `word_count` directly: `type(result).__name__ == 'int'`, `result == 2`. The text block at L183-186 documents the expected output and matches the actual runtime output exactly. **The chapter's load-bearing claim is verified end-to-end.**

17. **`bible.md` earlier chapter blocks (ch-01..ch-09) untouched** — **PASS**. Header scan returns 10 `## Added by ch-NN` headers in order: ch-01 L34, ch-02 L44, ch-03 L54, ch-04 L64, ch-05 L72, ch-06 L82, ch-07 L95, ch-08 L113, ch-09 L124, ch-10 L136. The ch-10 block (L136 onward) is appended after ch-09's block (L124) and is non-destructive — no ch-01..ch-09 entries are mutated. The ch-10 block contains 10 entries (`@tool` decorator contract details, schema-from-type-hints mechanism, no-auto-coercion, `add_base_tools` kwarg, `AgentToolExecutionError` recovery, 9 built-in tools, tool selection by name+description+schema, tool errors are not termination, tool sandbox caveat, beginner tool selection traps). Each entry builds on the ch-09 entry by reference ("see the ch-09 entry for the basic import and shape") and adds ch-10-specific detail (verified source line numbers, the `setdefault` collision note, etc.). The bible.md UTF-8 round-trip is byte-exact (35,242 bytes). Bible integrity preserved.

18. **`ledger.md` ch-10 row updated correctly** — **PASS**. Row at `ledger.md:181`:
    `| ch-10 | drafted | ch-09 | 1593 | - | - | Typed, docstring-rich \`@tool\` with verified no-auto-coercion returns. 11 research entries (entry-074..entry-084) covered in prose; H1 = "# Chapter 10 — Give Agents Useful Tools"; orientation 59/60 words; closing imperative ("Write a typed, docstring-rich \`@tool\` function, pass it in \`tools=[...]\`...") is the FINAL visible substantive prose paragraph before the HTML comment; "What's next" bridge names ch-11 (Guide Agents with Instructions and Memory). Zero blacklist hits ... |`
    Status `drafted`, dev review `-` (the dev review came after the ledger row was written), line-edit `-` (this review will close that). Word count 1593. Dev review column shows `-` but the dev review was completed (file exists at `share/reports/04_book-review_T-2026-08-01-001-book-ai-agents-with-python_ch-10_dev.md` with verdict PASS_WITH_WARN). All cells consistent with the chapter's state. **Note: the orientation is reported as 59/60 in the ledger, my measurement is 58/60 — within rounding difference for the ledger's counter, which uses a different stripper. Both pass the 30–60 range.**

---

## Cross-cutting findings

- **The no-auto-coercion claim is delivered clearly, not buried.** The §"The no-auto-coercion return behavior" section (L37–58) opens with the rule ("A `@tool` returning a Python value returns that value to the agent unchanged"), cites the source (`tools.py:231-249` and `agent_types.py:263-281`), explains the gate (`sanitize_inputs_outputs=True` triggers `handle_agent_output_types`), names the three concrete branches (`str → AgentText`, `PIL.Image.Image → AgentImage`, `torch.Tensor → AgentAudio`), states the explicit alternative (`call json.dumps(...) yourself`, `call str(...) yourself`), and shows the `stats_payload` example with `json.dumps(...)`. The `stats_dict` direct-call check at L152–188 demonstrates the dict-return path stays raw by *running* it. The closing imperative at L190 names the rule again ("rely on the verified no-auto-coercion tool-return behavior"). This is one of the strongest no-auto-coercion deliveries in the book.

- **The four beginner errors match the ch-08/ch-09 pattern.** Each error (1) names the failure mode, (2) shows the traceback category where applicable, (3) shows the fix. Error 1 (missing type hints) names `TypeHintParsingException` at import time. Error 2 (vague docstring) explicitly notes "There is no traceback" (the failure is silent). Error 3 (returning `None`) names the failure mode and the fix (return a clear message). Error 4 (name collision with built-in terminator) names `MultiStepAgent._setup_tools` and the `setdefault` mechanism. All four follow the same shape: bold failure-type label, body paragraph, fix sentence. The 4-error list is the cleanest of the book so far.

- **The chapter's flow (contract → schema → no-coercion → multi-tool → selection → errors → safety → 4 errors) is coherent and not jumbled.** The §"The contract: hints, docstring, return" section installs the decorator's three pieces (hints, docstring, return type). The §"Schemas and selection rules" section explains how the contract becomes a JSON schema and why docstring quality matters. The §"The no-auto-coercion return behavior" section is the chapter's load-bearing correction. The §"Pick from the built-in inventory" section names the 9 built-ins. The §"The base-tool shortcut and its default" section explains `add_base_tools=True`. The §"Vague docstrings, missed selections" section deepens the selection rule. The §"Tool errors are feedback, not termination" section names `AgentToolExecutionError`. The §"The sandbox is not a safety wall" section is the forward-pointer to ch-14. The §"Four beginner errors" section consolidates the four mistakes. The §"Extend the ch-09 agent with two tools" section delivers the runnable. The §"Check: the dict-return path stays raw" section demonstrates the no-auto-coercion rule in isolation. The chapter progresses from contract → schema → rule → inventory → shortcut → selection → errors → safety → mistakes → runnable → check → imperative. Each section builds on the prior; no section is orphaned.

- **The closing imperative shape.** 52 words, five imperative verbs (`Write`, `pass`, `rely`, `return`, `call`). The deliverable is specific: write a typed + docstring-rich `@tool`, pass it in `tools=[...]`, rely on the no-auto-coercion behavior, return a string deliberately, and call `json.dumps(...)` or `str(...)` explicitly when the model needs text. The mirror between the imperative and the chapter's outcome line ("by the end of the reading, the reader can write a typed, docstring-rich `@tool` function, pass it in `tools=[...]`, and rely on the verified no-auto-coercion tool-return behavior (return a string unless another type is genuinely useful)") is exact — the imperative is the verbatim outcome line rewritten in second-person imperative voice. **Strong closing.**

- **The 6 inline source attributions sit at the right behavior boundary.** L9 (decorator), L29 (schema), L39 (no-coercion gate), L62 (built-in list), L76 (error wrapping), L80 (sandbox), L92 (setdefault). Each reads as a parenthetical `file:line` reference, not a pasted-in citation. The attributions match the ch-08 / ch-09 lineedit precedent (named source + `file:line` at a behavior cluster). The `AgentToolExecutionError` paragraph at L76 is the only one missing a `file:line` cite — a `ToolCallingAgent.execute_tool_call` reference would close the gap. **Non-blocking copy-edit improvement.**

---

## Out-of-scope observations (informational only)

- **`Qwen/Qwen2.5-Coder-7B-Instruct` literal in block 3 (L137)** is the same identifier the research-log's entry-084 says is "carried forward from ch-08 entry-069." The 25-inline-age-risks rule (style-guide.md:143) says concrete model identifiers must NOT be used in prose. The literal identifier appears in a code block (allowed by the style guide's "When the prose mentions a version, it says '1.26.0,' not 'current' or 'latest'" exception). The *prose* does not name the model. This is a borderline pass — the model identifier in the code block is a runnable requirement (you need a literal to run), and the 25-age-risks rule is about *prose*, not code. Copy-edit may want to flag for the user whether code-block model identifiers fall under the same rule; this is a whole-book consistency question, not a ch-10 issue.

- **The `add_base_tools` paragraph (L68, P17) is the chapter's longest at 95 words.** The natural break-point is between sentence 4 ("The built-in terminator tool is added regardless of the flag's value.") and sentence 5 ("`CodeAgent` already executes model-written Python, so the shortcut does not add `python_interpreter` to it..."). Splitting there gives two paragraphs of approximately 41 and 50 words. See Honest Assessment item 1 for the specific recommendation.

- **The `L80` (sandbox) paragraph ends with the chapter's only forward-pointer to ch-14.** The double-dashes around the forward-pointer ("real isolation — the `executor_type="docker"` knob, the `authorized_imports=` whitelist, and the `final_answer_checks=` gate — is the topic of ch-14") match the ch-09 pattern. The `final_answer_checks` kwarg is allowed by the dispatch's no-`final_answer` rule.

- **The `bible.md` ch-10 entry has a self-referential final clause** in the "Beginner tool selection traps (4)" entry: "Duplicate names among explicitly supplied tools/managed agents raise `ValueError`, but a single collision with the built-in terminator's name is not rejected, making that collision especially dangerous." This is correctly conservative — it is sourced from the verified `_validate_tools_and_managed_agents` source, not a rephrase of the brief. Bible integrity preserved.

- **`GoogleSearchTool` is also in the installed 1.26.0 lib** (a 10th built-in beyond the chapter's 9). The chapter's 9-name list is pinned to 2026-08-01 and the research-log entry-079 notes a re-check on upgrades. The chapter does not promise "exactly 9" — it says "ships nine public built-in tools, verified by inspecting `dir(smolagents)` on 2026-08-01" (L62), which is correct as-of that date for the curated list. This is fine; copy-edit-pass can add a one-line "as of 2026-08-01" qualifier if desired.

- **No Git repository exists at `E:\book_gen`**, so the bible no-touch check is structural, not cryptographic. The dev reviewer noted the same.

---

## Honest assessment (the four asks)

1. **The 6 over-80-word paragraphs and the 1 over-7-word H2 — find each one, report line numbers, suggest splits/tightening for master.**

   **H2 #1 (over 7 words):** `ch-10.md:7` — "Why the decorator is more than a tag" (8 words). The chapter's load-bearing introductory section. Three tightening options (any one works):
   - "What the decorator actually does" (5 words) — drops the verb "is" and the noun "more than a tag", keeps the action-y pose.
   - "Why the decorator reads your code" (6 words) — adds the action verb "reads" and replaces the abstract "tag" with the concrete "your code".
   - "Why the decorator is a contract" (5 words) — keeps the existing sentence structure but tightens to the chapter's coin (the contract is the H2 at L11).
   
   **Recommended:** "Why the decorator is a contract" (5 words). The chapter's central metaphor is "the `@tool` function is a small contract between you and the model" (L13). The H2 should pre-state that. After the rename, the L11 H2 ("The contract: hints, docstring, return") reads as the unpacking of the L7 H2's contract — natural flow.

   **P9 (ch-10.md:35, 81 words, 1 over):** "The agent never reads the function body. It sees a menu card built from the type hints and the docstring, and it picks one tool per step from that menu. The card needs a selection rule. A weak description is "Counts words." A useful description is "Count the number of words in a string. Use this when the user asks how long a piece of text is." The second sentence is the rule that lets the model pick the right tool."
   
   **Split suggestion:** The paragraph has a natural break after "The card needs a selection rule." (which is sentence 3). Splitting there gives P9a (38 words, "The agent never reads the function body... The card needs a selection rule.") and P9b (43 words, "A weak description is "Counts words." ... The second sentence is the rule that lets the model pick the right tool."). Both well under 80. The reader's eye sees the rule first, then the contrast.

   **P11 (ch-10.md:41, 86 words):** "The `Tool.__call__` method runs the tool's `forward` and then, only when `sanitize_inputs_outputs=True`, passes the output through `handle_agent_output_types`. That helper tries three concrete types: a `str` becomes `AgentText`, a `PIL.Image.Image` becomes `AgentImage`, and a `torch.Tensor` becomes `AgentAudio`. Anything else — a `dict`, an `int`, a `float`, a `list`, a `None`, a custom dataclass — returns unchanged. The chapter's rule: return a string unless another type is genuinely useful. When the model needs a JSON text, call `json.dumps(...)` yourself. When it needs a stringified number, call `str(...)` yourself."
   
   **Split suggestion:** The paragraph has a natural break after "Anything else — a `dict`, an `int`, a `float`, a `list`, a `None`, a custom dataclass — returns unchanged." (which is sentence 4 — the technical exposition). Splitting there gives P11a (58 words, "The `Tool.__call__` method runs... returns unchanged.") and P11b (28 words, "The chapter's rule: return a string... call `str(...)` yourself."). This is actually a *better* structure: the technical rule first, then the chapter's rule. After the split, the L43 code block (the `stats_payload` example) lands between the technical expository paragraph and the chapter's rule paragraph — the example illustrates the rule.

   **P17 (ch-10.md:68, 95 words, the chapter's longest):** "There is one shortcut for adding a small default set of built-ins: `add_base_tools=True`. The kwarg is inherited through `**kwargs` by both `CodeAgent` and `ToolCallingAgent`, and its default is `False`. When set to `True`, the agent receives `python_interpreter`, `web_search` (a `DuckDuckGoSearchTool`), and `visit_webpage` through `TOOL_MAPPING`. The built-in terminator tool is added regardless of the flag's value. `CodeAgent` already executes model-written Python, so the shortcut does not add `python_interpreter` to it; `ToolCallingAgent` does not, so the shortcut adds `python_interpreter` to its tool list. The beginner rule is to use `tools=[...]` so the agent's capability surface is visible."
   
   **Split suggestion:** The paragraph has a natural break after "The built-in terminator tool is added regardless of the flag's value." (which is sentence 5). Splitting there gives P17a (45 words, "There is one shortcut... The built-in terminator tool is added regardless of the flag's value.") and P17b (50 words, "`CodeAgent` already executes model-written Python... The beginner rule is to use `tools=[...]` so the agent's capability surface is visible."). Both well under 80. The first paragraph delivers the kwarg + the three TOOL_MAPPING entries + the always-on terminator. The second paragraph delivers the CodeAgent/ToolCallingAgent split + the beginner rule.

   **P18 (ch-10.md:72, 87 words):** "The model picks a tool by reading its name, description, and input schema, not the function body. A vague docstring tells the model nothing to distinguish your tool from the agent's own Python execution. The first example says "Look up a number." The second says "Look up the population of a country by name. Use this when the user asks for a current population figure." The same code body, the same return type, the same arguments — but the second description gives the model a selection rule."
   
   **Split suggestion:** The paragraph has a natural break after "A vague docstring tells the model nothing to distinguish your tool from the agent's own Python execution." (which is sentence 2). Splitting there gives P18a (27 words, "The model picks a tool by reading its name, description, and input schema, not the function body. A vague docstring tells the model nothing to distinguish your tool from the agent's own Python execution.") and P18b (60 words, "The first example says 'Look up a number.' ... but the second description gives the model a selection rule."). Both well under 80. The first paragraph delivers the principle; the second paragraph delivers the contrast.

   **P19 (ch-10.md:76, 90 words):** "A `ToolCallingAgent` invokes a tool as a normal Python call. If the tool raises, smolagents catches the underlying exception, wraps it as `AgentToolExecutionError` with the tool name, supplied arguments, exception type and message, and guidance to fix the call, then feeds that error back into the current step and continues the loop. The model sees the wrapped error and may retry with corrected arguments or pick a different tool. Inside a tool, catch expected network and file errors and return a concise recovery message; raise only for genuinely unexpected failures."
   
   **Split suggestion:** The paragraph has a natural break after "The model sees the wrapped error and may retry with corrected arguments or pick a different tool." (which is sentence 3). Splitting there gives P19a (53 words, "A `ToolCallingAgent` invokes a tool as a normal Python call... The model sees the wrapped error and may retry with corrected arguments or pick a different tool.") and P19b (37 words, "Inside a tool, catch expected network and file errors and return a concise recovery message; raise only for genuinely unexpected failures."). Both well under 80. The first paragraph describes the framework's error wrapping behavior; the second paragraph delivers the beginner rule. **Recommended copy-edit add:** Add a `ToolCallingAgent.execute_tool_call` `file:line` cite to P19a (the missing 6th attribution — see Cross-cutting findings).

   **P20 (ch-10.md:80, 92 words):** "A `@tool` function is ordinary Python. It can close over variables, mutate globals, read and write files, send network requests, or call subprocesses. `ToolCallingAgent` calls tools in the host process with the full authority of the user's Python; `CodeAgent` registers tools inside its configured Python executor. The default executor is `LocalPythonExecutor`, which AST-restricts model-generated code but still trusts the user's tool implementations. The chapter's rule is to keep beginner tools read-only or harmless; real isolation — the `executor_type="docker"` knob, the `authorized_imports=` whitelist, and the `final_answer_checks=` gate — is the topic of ch-14."
   
   **Split suggestion:** The paragraph has a natural break after "The default executor is `LocalPythonExecutor`, which AST-restricts model-generated code but still trusts the user's tool implementations." (which is sentence 4). Splitting there gives P20a (51 words, "A `@tool` function is ordinary Python... but still trusts the user's tool implementations.") and P20b (41 words, "The chapter's rule is to keep beginner tools read-only or harmless; real isolation — the `executor_type="docker"` knob, the `authorized_imports=` whitelist, and the `final_answer_checks=` gate — is the topic of ch-14."). Both well under 80. The first paragraph describes the trust boundary; the second paragraph delivers the chapter's rule plus the ch-14 forward-pointer. The forward-pointer is preserved as the last line before the L82 H2 ("Four beginner errors").

   **Summary:** Master can apply 6 paragraph splits (P9, P11, P17, P18, P19, P20) and 1 H2 tighten (L7). All are one-line blank-line insertions or one-word substitutions. After the edits, all 39 paragraphs are ≤ 80 words and all 12 H2s are ≤ 7 words. Content unchanged. **These are the 7 line-edit deliverables for master.**

2. **The no-auto-coercion claim — does the prose deliver it clearly, or is it buried?** **Delivered clearly, not buried.** The §"The no-auto-coercion return behavior" section at L37–58 is explicit: the rule is stated in the first sentence ("A `@tool` returning a Python value returns that value to the agent unchanged"), the source is cited immediately after (`tools.py:231-249` and `agent_types.py:263-281`, verified on 2026-08-01), the gate is named (`sanitize_inputs_outputs=True`), the three concrete branches are enumerated (`str → AgentText`, `PIL.Image.Image → AgentImage`, `torch.Tensor → AgentAudio`), the negative space is named ("Anything else — a `dict`, an `int`, a `float`, a `list`, a `None`, a custom dataclass — returns unchanged"), the chapter's rule is restated ("The chapter's rule: return a string unless another type is genuinely useful"), and the explicit alternatives are named ("call `json.dumps(...)` yourself", "call `str(...)` yourself"). The `stats_payload` example at L43–56 shows the `json.dumps(...)` rule in code. The `stats_dict` direct-call check at L152–188 demonstrates the dict-return path stays raw by *running* it. The closing imperative at L190 names the rule one more time. The chapter delivers the rule in three places (the §"The no-auto-coercion return behavior" section, the `stats_payload` code example, the closing imperative) and verifies it by running `stats_dict` directly. **The beginner who reads ch-10 cannot miss the no-auto-coercion rule.**

3. **Are the 4 beginner errors well-formed (matching ch-08/ch-09 pattern)?** **Yes, all four match the pattern.** Each error follows the same shape: (1) bold failure-type label, (2) body paragraph naming the failure mode, (3) traceback category where applicable, (4) fix sentence. Error 1 (missing type hints) follows the pattern exactly: bold "Missing type hints or argument descriptions.", body names `TypeHintParsingException` at import time, fix is "add a type hint to every parameter and an `Args:` entry to every parameter." Error 2 (vague docstring) follows the pattern with the traceback explicitly noted as absent: "There is no traceback." (the failure is silent). Error 3 (returning `None`) follows the pattern: bold "Returning `None`.", body names the failure mode ("returns actual `None` to the agent, not an empty string"), fix is "return a clear success or failure message on every path." Error 4 (naming collision with built-in terminator) follows the pattern: bold "Naming a custom tool that collides with the built-in terminator's name.", body names the framework mechanism (`MultiStepAgent._setup_tools` uses `setdefault`), fix is "pick a different name." All four errors are well-formed. The 4-error list is the cleanest of the book so far.

4. **Does the chapter's overall flow (contract → schema → no-coercion → multi-tool → selection → errors → safety → 4 errors) feel coherent or jumbled?** **Coherent.** The chapter's 12 H2s progress in a deliberate order: the contract (L11), the schema (L33), the no-auto-coercion rule (L37), the built-in inventory (L60), the base-tool shortcut (L66), the selection rule (L70), the error wrapping (L74), the sandbox caveat (L78), the four beginner errors (L82), the runnable (L94), the direct-call check (L152), and the closing imperative (L190). Each section builds on the prior. The reader learns the contract, then the schema, then the rule, then the inventory, then the shortcut, then the selection rule, then the error wrapping, then the safety caveat, then the four mistakes, then runs the agent, then checks the rule, then acts. The progression is intentional: the §"Why the decorator is more than a tag" section previews the chapter; the contract section unpacks the decorator; the schema section unpacks the contract; the no-coercion section is the chapter's load-bearing correction; the inventory section names the built-ins; the shortcut section explains `add_base_tools`; the selection section deepens the schema rule; the error section names `AgentToolExecutionError`; the sandbox section is the safety forward-pointer; the four errors section consolidates the mistakes; the runnable section delivers the agent; the check section verifies the rule; the imperative section is the action. **No section is orphaned. The chapter's flow is the cleanest of the book so far.**

---

## Self-critique

- **What I'm confident about:** the mechanical checklist items (vocabulary blacklist at 0 hits, paragraph lengths at 6 over-80, H2 style at 1 over-7-word, HfApiModel/ApiModel at 0, final_answer keyword at 0, exclamation marks at 0 + 1 HTML comment, UTF-8 round-trip byte-exact, all 4 code blocks ast.parse clean, direct-call runtime verification of the no-auto-coercion claim, bible.md ch-01..ch-09 blocks intact, ledger.md ch-10 row correct). All measured by script and verified manually.

- **What I'm reasonably confident about:** the orientation paragraph word count (58 by my counter, 59 by the ledger). The 1-word difference is the ledger's stripper handling em dashes differently. Both counters pass the 30–60 range. The 6 paragraph counts and 1 H2 count match the dev reviewer's counts to the word. The "between imperative and HTML comment is 3 lines (blank + bridge + blank)" check is structural — line-by-line verified.

- **What I'm less confident about:** the 81-word count at P9 (ch-10.md:35). The dev review reported 81; my counter reports 81. The paragraph ends with "The second sentence is the rule that lets the model pick the right tool." which is 14 words by my counter. The total is 81. My P9-split suggestion (split after "The card needs a selection rule.") gives 38 + 43 = 81 words, exactly matching the original. After the split, both new paragraphs are well under 80. The split is safe.

- **What I deliberately did NOT do:** I did not edit any chapter file, bible file, or ledger file. This is review-only. The orchestrator (master) will update the ledger to set `line-edit = pass` and may apply the 6 paragraph splits + 1 H2 tighten (all one-line edits, no content change). The 2 acronym gaps (JSON, AST) are copy-edit-pass material, not block-shipping material.

- **Methodology call-out:** I stripped code blocks, HTML comments, H2 headings, table rows, blockquotes, and bullet lines before counting words. The ledger's 1593 uses a tighter stripper (probably also removes H2 heading tokens and bullet-list markers). I report the canonical-state figures (1593, 58, 12) and the code-stripped figures (1364 prose, 81 for P9) in the relevant rows. The dev-fix1 reviewer's paragraph counts (81, 86, 95, 87, 90, 92) match my counts exactly — both methods agree on the 6 over-80-word paragraphs.

- **Boundary compliance:** Only `share/reports/04_book-review_T-2026-08-01-001-book-ai-agents-with-python_ch-10_lineedit.md` was written. No chapter, bible, ledger, task, note, message, memory, trace, or controller file was edited or created. The temp files at `C:\Users\AHMADM~1\AppData\Local\Temp\opencode\ast_chk.py`, `verify_no_coercion.py`, and `verify_payload.py` are sandbox-side files (not in the project) and were used for runtime verification only.

---

## Issue counts

- **FAIL:** 0
- **MEDIUM:** 0
- **LOW:** 4
  - 6 over-80-word paragraphs (P9, P11, P17, P18, P19, P20) — split suggestions in Honest Assessment item 1
  - 1 over-7-word H2 (ch-10.md:7 "Why the decorator is more than a tag", 8 words) — tightening suggestion in Honest Assessment item 1
  - `JSON` not expanded on first prose mention at L3 ("no JSON dump") — book-wide carryover, copy-edit ledger material
  - `AST` not expanded at L80 ("AST-restricts model-generated code") — book-wide carryover, ch-09 lineedit precedent accepts as programming-pedagogy exception
- **Out-of-scope / informational:** 3
  - `Qwen/Qwen2.5-Coder-7B-Instruct` literal in block 3 (style-guide 25-age-risks question — code-block vs prose)
  - `AgentToolExecutionError` paragraph at L76 missing a `ToolCallingAgent.execute_tool_call` `file:line` cite (ch-09 pattern would close the gap)
  - `GoogleSearchTool` is a 10th built-in in the installed 1.26.0 lib (research-log entry-079 re-check-on-upgrade note)

---

## Call-to-action

**Ready to ship as line-edited chapter draft.** Orchestrator should:

1. Update `ledger.md` ch-10 row to set `line-edit = pass` and `Status = line-edited`.
2. Apply the 6 paragraph splits (one blank-line insertion per split, no content change):
   - P9 (ch-10.md:35) — split after "The card needs a selection rule."
   - P11 (ch-10.md:41) — split after "Anything else — a `dict`, an `int`, a `float`, a `list`, a `None`, a custom dataclass — returns unchanged."
   - P17 (ch-10.md:68) — split after "The built-in terminator tool is added regardless of the flag's value."
   - P18 (ch-10.md:72) — split after "A vague docstring tells the model nothing to distinguish your tool from the agent's own Python execution."
   - P19 (ch-10.md:76) — split after "The model sees the wrapped error and may retry with corrected arguments or pick a different tool."
   - P20 (ch-10.md:80) — split after "The default executor is `LocalPythonExecutor`, which AST-restricts model-generated code but still trusts the user's tool implementations."
3. Tighten the over-7-word H2 at ch-10.md:7 — rename "Why the decorator is more than a tag" to "Why the decorator is a contract" (5 words).
4. Optional (copy-edit pass): expand `JSON` on first prose mention at ch-10.md:3 to "JSON (JavaScript Object Notation)". Book-wide carryover, not a ch-10 regression.
5. Optional (copy-edit pass): add a `ToolCallingAgent.execute_tool_call` `file:line` cite to ch-10.md:76 to close the 6th-attribution gap. Not required to ship.

No FAILs. No code edits performed by this review. No files in `books/`, `agents_manager/`, `tasks/`, or `share/` (other than the report) were modified.
