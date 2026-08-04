# Book-Review (developmental) — ch-10 *Give Agents Useful Tools*

**Task:** T-2026-08-01-001-book-ai-agents-with-python
**Chapter:** ch-10 — *Give Agents Useful Tools*
**Pass:** dev (developmental)
**Book:** *AI Agents with Python* (`books/ai-agents-with-python/`)
**Reviewer:** am-review (book-gen mode)
**Date:** 2026-08-02
**Status:** Complete

---

## Summary

**Overall verdict: PASS_WITH_WARN**

The chapter is technically correct and load-bearing claim (no-auto-coercion, entry-077) is verified against installed smolagents 1.26.0 source. All 11 research entries (entry-074..entry-084) are addressed in prose. All four code blocks parse clean in `E:\book_gen\.venv\Scripts\python.exe` and the canonical no-auto-coercion checks reproduce the documented behavior: `stats_dict` returns a raw `dict` (not a JSON string); `stats_payload` returns a raw `str`; `word_count` returns a raw `int`. The closing-imperative contract is fully respected (the `> **The move:**` callout is the final visible substantive prose, followed only by a thin "What's next" bridge and the HTML self-critique comment).

Two non-blocking style issues: six paragraphs exceed the 80-word ceiling from style-guide.md (one at 81 words, the rest 86–95), and one H2 subheading ("Why the decorator is more than a tag") is 8 words where the style guide's "≤ 7 words" rule applies. Both are copy-edit-pass material, not chapter-killers. No FAILs.

| Severity | Count |
|---|---|
| CRITICAL | 0 |
| HIGH | 0 |
| MEDIUM | 0 |
| LOW / WARN | 4 (6 over-80-word paragraphs + 1 over-7-word H2 + 1 dispatch-mismatch note on H2 count) |
| FAIL | 0 |

---

## Tests / build run

| Check | Result | Evidence |
|---|---|---|
| `ast.parse` on the 4 Python code blocks | PASS | All 4 blocks parse clean in `E:\book_gen\.venv\Scripts\python.exe` (11 + 12 + 49 + 22 lines). See `check_ast.py` run. |
| `@tool` import path (`from smolagents import tool`) | PASS | `inspect.signature(smolagents.tool)` → `(tool_function: 'Callable') -> 'Tool'`. smolagents 1.26.0. |
| Decorated tool direct-call returns its native Python type | PASS | `stats_dict("hello world")` → `dict` (verified, type and value); `stats_payload("hello world")` → `str` (verified); `word_count("hello world")` → `int` 2. |
| `Tool.__call__` uses `sanitize_inputs_outputs` gate | PASS | Source confirms: `if sanitize_inputs_outputs: args, kwargs = handle_agent_input_types(...)` and `if sanitize_inputs_outputs: outputs = handle_agent_output_types(outputs, self.output_type)`. Default of the flag is `False`, so direct calls do not pass through `handle_agent_output_types`. |
| `handle_agent_output_types` only handles str / PIL.Image / torch.Tensor | PASS | Source scan: 3 explicit branches → `AgentText`, `AgentImage`, `AgentAudio`. Dicts/ints/floats/lists/None/custom dataclasses fall through unchanged. |
| All 9 chapter-claimed built-in tools present in 1.26.0 | PASS | `dir(smolagents)` scan: `DuckDuckGoSearchTool`, `VisitWebpageTool`, `WikipediaSearchTool`, `WebSearchTool`, `SpeechToTextTool`, `PythonInterpreterTool`, `FinalAnswerTool`, `UserInputTool`, `ApiWebSearchTool` — all 9 present. (`GoogleSearchTool` is *also* present in the installed lib but is not in the chapter's 9; the research-log entry-079 pins the 9-name list to 1.26.0 and notes re-check on upgrades, which is fine.) |
| `FinalAnswerTool.name` = `"final_answer"` | PASS | Confirmed: `'final_answer'`. This is the framework's reserved keyword; the chapter deliberately uses `FinalAnswerTool` (the class name) and "the built-in terminator" in prose, never the bare snake_case name. |
| `tools=[...]` kwarg on `CodeAgent` | PASS | `inspect.signature(CodeAgent)` accepts `tools=`; the chapter's runnable (block 3) passes `tools=[word_count, stats_payload]`. |
| `add_base_tools=False` default, kwarg inherited via `**kwargs` | PASS | bible.md ch-10 entry is the canonical attestation; not contradicted by source. |
| UTF-8 round-trip | PASS | `[System.Text.Encoding]::UTF8.GetString(bytes)` returns the file unchanged. |
| H2 count in body | 12 | Dispatch claimed 14; actual count is **12**. The chapter is consistent with itself; the dispatch's "14" is a minor mismatch, not a chapter issue. |

---

## Per-task verdicts

Each research-log entry is treated as a "task" for the per-task verdicts list. Every one is addressed in ch-10 prose.

| Entry | Topic | Verdict | Evidence |
|---|---|---|---|
| entry-074 | `@tool` contract (type hints + docstring + return) | PASS | "The contract: hints, docstring, return" (ch-10.md:11–32) + "Why the decorator is more than a tag" (ch-10.md:7–9). Decorator source cite at `tools.py:1061`. |
| entry-075 | schema generation from type hints | PASS | "Schemas and selection rules" (ch-10.md:33–35) + explicit `get_json_schema()` reference at ch-10.md:29 with the `_function_type_hints_utils.py` path. |
| entry-076 | multi-tool demo | PASS | "Extend the ch-09 agent with two tools" (ch-10.md:94–148): `word_count` and `stats_payload` both decorated, both passed in `tools=[...]`. |
| entry-077 | **the no-auto-coercion tool-return behavior** (load-bearing claim) | PASS | "The no-auto-coercion return behavior" (ch-10.md:37–58). Source cited at `tools.py:231-249` and `agent_types.py:263-281`. Verified by direct execution: `stats_dict` returns `dict` (not JSON string); `stats_payload` returns `str` (because the author called `json.dumps(...)` explicitly); `word_count` returns `int`. `Tool.__call__` source confirms `sanitize_inputs_outputs` is the gate. |
| entry-078 | the 9 built-in tools in 1.26.0 | PASS | "Pick from the built-in inventory" (ch-10.md:60–64) names all 9 with verified signatures; `dir(smolagents)` cross-check confirms each is present. |
| entry-079 | `add_base_tools=True` default `False`; split between `CodeAgent` (no python_interpreter) and `ToolCallingAgent` (adds it); `final_answer` always added | PASS | "The base-tool shortcut and its default" (ch-10.md:66–68) covers the default, the kwarg name, the three TOOL_MAPPING entries (`python_interpreter`, `web_search`, `visit_webpage`), the `CodeAgent`/`ToolCallingAgent` split, and the `final_answer` always-on behavior. |
| entry-080 | tool selection (docstring → description → model reads it) | PASS | "Schemas and selection rules" (ch-10.md:33–35) + "Vague docstrings, missed selections" (ch-10.md:70–72). Bad-vs-good description contrast included. |
| entry-081 | tool errors caught and wrapped as `AgentToolExecutionError`, fed back to the model | PASS | "Tool errors are feedback, not termination" (ch-10.md:74–76) names the exception, the wrapped payload (tool name, args, exception type/message, guidance), the model-retry path, and the beginner rule about catching expected network/file errors inside the tool. |
| entry-082 | sandbox safety carryover (LocalPythonExecutor with `authorized_imports` fence) — forward-pointer to ch-14 | PASS | "The sandbox is not a safety wall" (ch-10.md:78–80) names `LocalPythonExecutor` and the three ch-14 topics (`executor_type="docker"`, `authorized_imports=`, `final_answer_checks=`). The ch-14 forward-pointer is named explicitly. |
| entry-083 | 4 beginner errors | PASS | "Four beginner errors" (ch-10.md:82–92). All four: (1) missing type hints / `TypeHintParsingException`; (2) vague docstring / no traceback; (3) returning `None` returns actual `None`; (4) name collision with the built-in terminator via `setdefault`. Numbered list, one fix per error. |
| entry-084 | runnable demo extending ch-09 with 1-2 typed tools | PASS | "Extend the ch-09 agent with two tools" (ch-10.md:94–148) defines two typed tools, wires `CodeAgent(tools=[...], model=InferenceClientModel(...))`, calls `.run(...)`, and asserts `isinstance(answer, str)`. The same guard as ch-07/ch-09 (`load_api_key("HF_TOKEN")` short-circuit) is in place. |

---

## Required-checklist results (each PASS / FAIL / N/A)

1. **Outline coverage (entry-074..entry-084)** — **PASS**. All 11 entries addressed in prose. See per-task table above.
2. **Voice match** — **PASS**. Conversational technical, second-person dominant ("you write", "the decorator reads", "your tool"), contractions natural (don't, doesn't, you've, isn't), zero exclamation marks.
3. **Vocabulary blacklist** — **PASS**. `magic` 0, `just` 0, `simply` 0, `obviously` 0, `optimal` 0, `proven` 0, `revolutionary` 0, `game-changing` 0, `studies show` 0, `powerful` 0. (Case-insensitive, word-bounded, 10-term scan.)
4. **No HfApiModel / ApiModel mention (whole-book rule)** — **PASS**. `Select-String -Pattern "HfApiModel|ApiModel"` on `chapters/ch-10.md` returns 0 hits.
5. **No `final_answer` mention as the framework's reserved keyword** — **PASS**. `Select-String -Pattern "\bfinal_answer\b"` returns 0 hits. The kwarg `final_answer_checks` appears 2× (ch-10.md:80 in prose + ch-10.md:146 in the HTML self-critique) and is allowed per the dispatch.
6. **Bible consistency** — **PASS**. `bible.md:136-147` has `## Added by ch-10 — 2026-08-02` with all required terms: `@tool` decorator contract details, schema-from-type-hints mechanism, no-auto-coercion tool-return behavior, `add_base_tools` kwarg, `AgentToolExecutionError` recovery path, 9 built-in tools, tool selection by name + description + schema, tool errors are not termination, tool sandbox caveat, 4 beginner tool selection traps. Non-duplicative: each entry builds on the ch-09 entry by reference ("see the ch-09 entry for the basic import and shape") and adds the ch-10-specific detail (verified source line numbers, the `setdefault` collision note, etc.).
7. **Research grounding** — **PASS**. Inline attributions to installed smolagents 1.26.0 source: `tools.py:1061` (decorator), `tools.py:231-249` (`Tool.__call__` + sanitize gate), `agent_types.py:263-281` (`handle_agent_output_types`), `agents.py:402` (setdefault for `final_answer`). The 9 built-ins cite `dir(smolagents)` + `inspect.signature`. All citations match verified source.
8. **Code-block correctness** — **PASS**. 4 Python blocks, all `ast.parse` clean. `@tool` import path correct. Tool signatures use the type-hint-and-docstring pattern documented. `tools=[...]` kwarg on `CodeAgent` correct. The `stats_payload` example with `json.dumps(...)` correctly demonstrates the rule. The `stats_dict` direct-call check (block 4) shows what happens when you return a dict without coercion — verified at runtime, `type(result).__name__ == "dict"`, `result == {'words': 2, 'characters': 11}`.
9. **Beginner accessibility** — **PASS with one WARN**. Orientation paragraph 1 (ch-10.md:3) is 58 words, within the 30–60 range, opens with concrete terminal/tool/scene ("A terminal opens, `agent.run("how many words in this sentence?")` returns, and the answer lands as a clean integer…"). One move per paragraph, mostly. **WARN:** "Why the decorator is more than a tag" is 8 words where the style guide says subheadings ≤ 7. (See Cross-cutting findings.)
10. **Closing-imperative contract** — **PASS**. The `> **The move:**` callout (ch-10.md:190) is the final visible substantive prose paragraph. After it, only the thin "What's next" bridge (ch-10.md:192) and the HTML self-critique comment (ch-10.md:194–206). No third-person "by the end of the reading…" closing line, no "we've covered…" recap, no authorial summary after the imperative.
11. **Forward-pointer hygiene** — **PASS**. ch-10.md:192: "What's next: ch-11 — Guide Agents with Instructions and Memory — turns the same `CodeAgent` constructor into a configurable shape, with `instructions` for a paragraph of house style, `planning_interval` for periodic re-planning, `max_steps` for the step budget, and `reset=` plus `return_full_result=` for the memory and the full result." Names ch-11 explicitly, names concrete forward moves (the four new kwargs).
12. **Sandbox safety caveat (entry-082 enforcement)** — **PASS**. ch-10.md:80: "real isolation — the `executor_type="docker"` knob, the `authorized_imports=` whitelist, and the `final_answer_checks=` gate — is the topic of ch-14." Forward-pointer is present, named, and points to a specific later chapter.
13. **UTF-8 clean** — **PASS**. Round-trip with `bytes.decode('utf-8')` produces the same file with zero errors.
14. **No-regression vs prior chapters** — **PASS**. `ledger.md` ch-10 row (line 181) is populated: status `drafted`, word count `1593`, depends on `ch-09`, with a substantive notes block. `bible.md` ch-10 block (line 136 onward) is appended after ch-09's block (line 124) and is non-destructive — no ch-01..ch-09 entries are mutated. Append-only contract preserved.

---

## Cross-cutting findings

### WARN-1: Six paragraphs exceed the 80-word style-guide ceiling (style-guide.md Pacing and rhythm)

Style guide says "paragraphs ≤ 80 words." Word count per paragraph (after stripping code blocks, H1/H2, blockquotes, HTML comments):

| Para | File:line | Words | Note |
|---|---|---|---|
| 7 | ch-10.md:35 | 81 | "The agent never reads the function body…" — 1 word over. |
| 9 | ch-10.md:39–41 | 86 | "The `Tool.__call__` method runs the tool's `forward`…" — explains the `sanitize_inputs_outputs` gate. |
| 13 | ch-10.md:68 | 95 | "There is one shortcut for adding a small default set of built-ins: `add_base_tools=True`…" — names the default, the three TOOL_MAPPING entries, the CodeAgent/ToolCallingAgent split, and the `final_answer` always-on behavior. |
| 14 | ch-10.md:72 | 87 | "The model picks a tool by reading its name, description, and input schema…" — selection rule with the weak-vs-good contrast. |
| 15 | ch-10.md:76 | 90 | "A `ToolCallingAgent` invokes a tool as a normal Python call…" — entry-081 coverage. |
| 16 | ch-10.md:80 | 92 | "A `@tool` function is ordinary Python…" — entry-082 sandbox caveat with the ch-14 forward-pointer. |

These are not FAILs — the technical content is dense and the writer chose not to split. But the 80-word ceiling is explicit in the style guide. Two clean fixes per paragraph: split at the natural sentence boundary (e.g., the `add_base_tools` paragraph breaks naturally after "…regardless of the flag's value."), or pull the evidence into a follow-up paragraph. All copy-edit-pass material, no chapter rewrite required.

### WARN-2: One H2 subheading is 8 words (style-guide.md Structural devices)

Style guide line 25: "Subheadings are sentence-fragment style, not full sentences, and they describe the *move* the section installs." Style guide checklist (item 9) says "subheadings ≤ 7 words action-y fragments." The first H2, "Why the decorator is more than a tag," is 8 words. Easy fix in line-edit: "Why the decorator is a contract" (5 words) or "What the decorator actually does" (5 words). Copy-edit-pass material.

### NOTE-1: H2 count is 12, not 14

The dispatch's task brief said "14 H2 subheadings"; the actual file has 12. The 12 are all present and each is used as a section anchor. The chapter is internally consistent. This is a dispatch-side mismatch, not a chapter issue — no fix required.

### Note-2: `bible.md:147` ch-10 entry has a self-referential final clause

The `Beginner tool selection traps (4)` entry's final clause is "Duplicate names among explicitly supplied tools/managed agents raise `ValueError`, but a single collision with the built-in terminator's name is not rejected, making that collision especially dangerous." This is correctly conservative — it is sourced from the verified `_validate_tools_and_managed_agents` source, not a rephrase of the brief.

### Note-3: `GoogleSearchTool` is also in the installed 1.26.0 lib

`dir(smolagents)` lists 10 public Tool subclasses; the chapter names 9 of them (entry-079's list, pinned to 1.26.0). The 10th, `GoogleSearchTool`, is mentioned in research-log entry-079's `variance_resolution` as a re-check-on-upgrade item. The chapter does not promise "exactly 9" — it says "ships nine public built-in tools, verified by inspecting `dir(smolagents)` on 2026-08-01" (ch-10.md:62), which is correct as-of that date for the curated list. This is fine; copy-edit-pass can choose to add a one-line "as of 2026-08-01" qualifier if desired.

### Out-of-scope observations

- The chapter's three load-bearing claims (the `@tool` decorator location at `tools.py:1061`; the `Tool.__call__` gate at `tools.py:231-249`; the `handle_agent_output_types` branches at `agent_types.py:263-281`) are all verified against the installed 1.26.0 source. No research-log entry needs to be re-verified.
- The chapter's "Coming from ch-09" bridge (ch-10.md:5) preserves the "previous chapter's installed element" pattern from ch-07 and ch-08. Consistent.
- The runnable in block 3 uses `model_id="Qwen/Qwen2.5-Coder-7B-Instruct"` — this is the same identifier the research-log's entry-084 says is "carried forward from ch-08 entry-069." The 25-inline-age-risks rule (style-guide.md:143) says concrete model identifiers must NOT be used in prose. The literal identifier appears in a code block (which is allowed by the style guide's pinning exception: "When the prose mentions a version, it says '1.26.0,' not 'current' or 'latest'") but the *prose* does not name the model. This is a borderline pass — the model identifier in the code block is a runnable requirement (you need a literal to run), and the style guide's 25-age-risks rule is about the *prose*, not code. Copy-edit may want to flag for the user whether code-block model identifiers fall under the same rule; this is a whole-book consistency question, not a ch-10 issue.
- The 4 code blocks total 11 + 12 + 49 + 22 = 94 lines. The chapter's prose total is ~1500 words. The 2:1 prose-to-instruction ratio from style-guide.md:14 holds.

---

## Honest assessment

The chapter is the right shape and the right depth. The load-bearing claim (no-auto-coercion of tool returns) is the entire reason ch-10 exists — without it, beginners will write tools that silently return raw `dict`s and not understand why the model can't see the JSON they expected. The chapter teaches this correctly: explicit `json.dumps(...)` when the model needs text, explicit `str(...)` when it needs a stringified number, and the `stats_dict` direct-call check shows the rule in action by returning a `dict` unchanged.

The four beginner errors (missing hints, vague docstring, returning `None`, name collision with the built-in terminator via `setdefault`) are the right set and each gets a one-sentence fix. The ch-14 forward-pointer for sandbox isolation is present and named, which is the only place this side-correction is needed in the beginner path (the deeper `executor_type`/`authorized_imports`/`final_answer_checks` work is ch-14's job).

The closing-imperative contract is fully respected. The `> **The move:**` callout IS the final visible substantive prose paragraph, followed only by the thin "What's next" bridge and the HTML self-critique. This is the exact shape ch-06, ch-08, and ch-09 were all corrected toward in their fix loops.

What is not quite right: six paragraphs run over the 80-word ceiling, and one H2 is 8 words. Both are style-guide violations but neither is a content or correctness issue. They are copy-edit-pass material, not chapter-rewrite material. A line-edit pass can split each over-80 paragraph at a natural sentence boundary (most have one) and tighten the one H2 to 5–7 words.

Nothing in this chapter would mislead a beginner, nothing would crash their agent, nothing would make them write a tool that the framework handles differently from what the chapter describes.

---

## Self-critique

- I verified the no-auto-coercion claim by *running* it, not by reading the prose. The ch-10 claim is the chapter's load-bearing claim and "it sounds right" would not be sufficient. I ran the three direct-call examples (`stats_dict`, `stats_payload`, `word_count`) and confirmed each returns its declared native type, with no `handle_agent_output_types` in the path (because the default `sanitize_inputs_outputs=False` on `Tool.__call__` skips it). I also pulled the source of `Tool.__call__` and `handle_agent_output_types` to confirm the gate and the three concrete branches (`str → AgentText`, `PIL.Image → AgentImage`, `torch.Tensor → AgentAudio`). This is the chapter's correctness question; I am confident.
- I cross-checked the 9 built-in tools by scanning `dir(smolagents)` myself rather than trusting the chapter's list. All 9 are present; `GoogleSearchTool` is a 10th that the chapter does not name (intentional per research-log entry-079's pinning rule). I am confident in the list.
- I did NOT run the full runnable in block 3 end-to-end because it requires `HF_TOKEN`, which the chapter's `load_api_key` helper explicitly guards against. The chapter's prose correctly notes this ("full execution short-circuits on `load_api_key("HF_TOKEN")` until the reader has a token, the same guard ch-07 and ch-09 taught"). Running the full runnable would test the guard, not the chapter's correctness.
- I did NOT verify the `HfApiModel → ApiModel` rename claim itself — that's a ch-09 concern, and the chapter correctly avoids naming either class. The 0-hit grep on ch-10 is sufficient.
- I read all 12 H2 sections and the 4 code blocks; I did not re-read the HTML self-critique (line 194–206) as a verification target. The self-critique is a writer-to-reviewer handoff, not a published artifact.
- One blind spot: I assumed the `used_in: ch-09` tag on research-log entries 074–084 is a research-log-side mislabel and the dispatch's framing of "ch-10 entries 074..084" is the correct one. The chapter's content for these entries matches the entries' claims. If the master/orchestrator disagrees about the entry→chapter mapping, that is a meta-question outside this review.
- The dispatch said "14 H2 subheadings"; the chapter has 12. I did not let the dispatch's number override what the file actually contains. Reported as NOTE-1, not as a chapter defect.

---

## Files written

- This report: `share/reports/04_book-review_T-2026-08-01-001-book-ai-agents-with-python_ch-10_dev.md`

No other files written. No files edited. `chapters/ch-10.md`, `bible.md`, `ledger.md`, `research-log.md`, `outline.md`, `style-guide.md`, `environment.md` are all untouched.
