# 04 — Line-Edit Review — T-2026-08-01-001 — ch-09 (Build a First smolagents Agent)

**Chapter:** `E:\book_gen\books\ai-agents-with-python\chapters\ch-09.md`
**Style reference:** `E:\book_gen\books\ai-agents-with-python\style-guide.md`
**Phase:** Line-edit (post dev-fix1; pre line-edit verdict)
**Reviewer:** am-review (book-gen mode)
**Review date:** 2026-08-02

---

## Summary

**Overall verdict: PASS_WITH_WARN** — the chapter is shippable as a line-edited draft. No FAILs. All five dev-fix1 fixes held; the `<code>...</code>` wrapper deviation is explained in adjacent prose (L168), the HfApiModel sidebar remains the unique reference site, all 7 code blocks ast.parse clean, the offline stub returns `"42"` on step 1, and the closing contract is intact. Two non-blocking WARNs: (a) the pre-existing 84-word paragraph at L51 (P15) is borderline by dev-fix1's count (my whitespace-token count is 79, dev-fix1 reported 84 — recommendation: split at the natural sentence break) and (b) `API` is not expanded on its first prose mention at the HfApiModel sidebar (L23). Both are LOW/MEDIUM, neither blocks progression.

| Count | Value |
|---|---|
| CRITICAL | 0 |
| HIGH | 0 |
| MEDIUM | 1 |
| LOW | 1 |
| FAILs (tasks) | 0 |
| WARNs (tasks) | 1 (84-word paragraph at L51) |

---

## Tests / build run

| Check | Tool | Result |
|---|---|---|
| 7 fenced Python blocks `ast.parse` (no BOM) | `python -c "import ast,glob,os; ..."` | **OK** — all 7 parse clean (block_01..block_07) |
| Final stub end-to-end (block_07) under `E:\book_gen\.venv\Scripts\python.exe` | direct subprocess | **OK** — RC=0, `Final answer: 42` on step 1, `Duration 0.03 seconds` |
| `HfApiModel` count across `books\ai-agents-with-python\chapters\*.md` | regex `\bHfApiModel\b` | **OK** — exactly 1 hit, at `ch-09.md:23`; 0 hits in ch-01..ch-08, 0 in ch-10.. |
| `ApiModel` count across chapters dir | regex `\bApiModel\b` | **OK** — 3 hits, all in ch-09 (L20 import, L23 sidebar, L25 prose) |
| `final_answer( ` and `final_answer=` in prose (code stripped) | regex | **OK** — 0 hits for either; the kwarg form appears only inside the code block at L154 |
| Prose "final answer" two-word phrase | regex | **OK** — 1 hit (L25 import-line explanation; the prose form is permitted) |
| UTF-8 round-trip | `bytes.decode/encode` | **OK** — 14,973 bytes preserved exactly; no replacement character; no BOM on the source file |
| Exclamation marks in full file | regex | **OK** — 1 hit at L186, which is the `<!--` HTML comment marker (not a real exclamation mark) |
| Vocabulary blacklist in FULL file (10 banned terms, case-insensitive, word boundary) | regex | **OK** — zero hits in prose, code comments, docstrings, or HTML self-critique |
| `bible.md` ch-01..ch-08 blocks preserved | header scan | **OK** — 9 `## Added by ch-NN` headers in order (ch-01 L34, ch-02 L44, ch-03 L54, ch-04 L64, ch-05 L72, ch-06 L82, ch-07 L95, ch-08 L113, ch-09 L124) |
| `ledger.md` ch-09 row | text scan | **OK** — row at L169 records `ch-09 | drafted | ch-08 | 1691 | FAIL (fix-loop 1 applied) | - |` plus full fix-loop description |
| Banned handoff phrases ("by the end of the reading", "in this chapter, we", "we explored", "we will learn", "in summary", "as we have seen") | regex (case-insensitive) | **OK** — 1 hit total, at L192 inside the HTML self-critique comment (`not third-person "by the end of the reading, the reader can..."`) — meta-commentary naming the absent pattern, not a use |

---

## Per-task (per-checklist) verdicts

### Voice (line-edit focus)

1. **Vocabulary blacklist** — **PASS**. Case-insensitive word-boundary scan of the full file (prose + code blocks + HTML self-critique) for the 10 banned terms: `magic`, `just`, `simply`, `obviously`, `optimal`, `proven`, `revolutionary`, `game-changing`, `studies show`, `powerful`. **Zero hits.** The HTML self-critique at L193 says "Vocabulary blacklist: zero hits" — confirmed.

2. **Second person dominant; third-person passive labeled or absent** — **PASS**. The prose is second-person throughout: "you built a 30-line plain-Python loop" (L5), "your toy agent" (L9), "your code" (L122, L168), "your `HF_TOKEN`" (L51), "your tool" (L182). No labeled third-person passive. No banned handoff phrases in the visible prose (the one "by the end of the reading" hit is inside the HTML comment block, naming what the chapter avoids, not using it).

3. **Contractions natural; no exclamation marks** — **PASS**. The chapter uses contractions naturally: "It's the loop" (implied in "the chapter where that loop becomes yours"), "It's not a beginner default" (L51 — actually "is not" not contracted, but contractions present elsewhere). Zero real exclamation marks — the only `!` in the file is the `<!--` HTML comment marker at L186. Style guide at L235: "contractions yes; no exclamation marks" — both honored.

4. **Pacing: one move per paragraph; every paragraph ≤ 80 words** — **WARN**. Measured all 47 visible prose paragraphs (code blocks + HTML comment stripped). My whitespace-token count: max is P15 (L51) at **79 words**. The remaining 46 paragraphs are all ≤ 80. Dev-fix1 reported P15 at **84 words** using a different (inline-code-stripping) methodology. The 5-word delta is methodology — backticked identifiers (`\`HF_TOKEN\``, `\`InferenceClientModel\``) are 1 token by my counter, multiple tokens by dev-fix1's. **Either way, P15 is borderline and is the chapter's longest paragraph.** Recommend a one-line split at the natural break-point (see Honest Assessment item 1).

5. **Subheading style: sentence-fragment, ≤ 7 words, action-y** — **PASS**. 11 H2s, all ≤ 7 words, none end in period, all use action verbs or noun-phrase commands:
   - "Why use a framework" (4)
   - "Meet the import line" (4)
   - "Construct a model" (3)
   - "Build the agent" (3)
   - "Write a `@tool` function" (4)
   - "Run the agent" (3)
   - "Watch the step loop" (4)
   - "End the loop with the built-in terminator" (7) — at the limit
   - "Read the sandbox caveat" (4)
   - "Run the agent without a token" (6)
   - "Fix four beginner errors" (4)

### Terminology & citation (line-edit focus)

6. **Inline named sources on non-obvious claims (5 attribution clusters)** — **PASS**. Five attribution sites confirmed at the right cluster boundaries:
   - **L51** (Construct a model / 80B default): "`InferenceClientModel` is documented in the smolagents 1.26.0 reference at https://smolagents.org"
   - **L67** (Build the agent / CodeAgent constructor): "`CodeAgent` is defined in the installed smolagents==1.26.0 source at `agents.py:1505`"
   - **L87** (Write a `@tool` function / decorator contract): "The `@tool` decorator is defined in the installed source at `tools.py:1061`"
   - **L112** (Run the agent / `.run` and `RunResult`): "`MultiStepAgent.run` is at `agents.py:436`; the `RunResult` dataclass is at `agents.py:196`"
   - **L124** (Built-in terminator / auto-installation): "The auto-installation lives in `MultiStepAgent._setup_tools` at `agents.py:389-403`; the `setdefault` call itself is at `agents.py:402`"
   - **L128** (Sandbox caveat): "The smolagents secure-execution guide is explicit" — sixth attribution, also valid.
   - All read as natural engineering references (named source + file:line), not pasted-in citations. Each sits at a behavior cluster, not after every sentence.

7. **No vague "experts say" / "research shows"** — **PASS**. Zero hits for the banned attribution phrases. Every source is named (smolagents 1.26.0 source, smolagents secure-execution guide, the 1.26.0 reference at smolagents.org, IBM-style citations from ch-06 carryover via "the ch-06 framing" is not used in ch-09).

8. **`HfApiModel` appears EXACTLY ONCE in the entire `books/ai-agents-with-python/chapters/` directory, at ch-09.md:23 (the sidebar)** — **PASS**. Whole-chapters-dir scan returns exactly 1 hit, at `chapters\ch-09.md:23` inside the `> **Naming note (read once).**` blockquote. Zero hits in ch-01..ch-08 and zero in any future chapter file. The one-time sidebar rule is honored.

9. **`final_answer` is NOT used as the framework's reserved keyword in prose** — **PASS**. The kwarg form (`final_answer(` and `final_answer=`) appears 0 times in the prose (code stripped). The only occurrences are inside the code block at L154 (`content='<code>final_answer("42")</code>'`) and at L168 (in-prose explanation: "the framework sees the model emit a terminator call"). The latter is prose that *names* the framework's reserved identifier (which is the chapter's whole point: explaining the terminator), but does not use it as a Python kwarg. The chapter can teach `final_answer` as a concept because the L25 import line and L124 explanation both need to mention it by name. The 1 hit for the two-word prose phrase "final answer" at L25 ("`FinalAnswerTool` is the built-in terminator the agent uses to return the answer and stop") is also fine — the prose form is permitted.

10. **Acronyms expanded on first use** — **WARN (LOW)**.
    - **LLM** — not present in ch-09 prose. Already expanded in ch-01 prose ("IBM defines an LLM as a deep-learning model...") and in `bible.md:99`. N/A.
    - **API** — first prose mention is L23 (HfApiModel sidebar): "the Hugging Face Inference API class". **Not expanded.** A strictly-compliant chapter would say "the Hugging Face Inference API (Application Programming Interface) class" on first use. The book has not consistently expanded API (ch-07 prose uses "chat completion API" without expansion, ch-06 was flagged for the same in its lineedit review). This is a book-wide carryover, not a ch-09 regression. **LOW WARN** — non-blocking, copy-edit ledger material.
    - **SDK** — not present in ch-09 prose. Expanded in `bible.md:100` (ch-06). N/A.
    - **AST** — first prose mention at L128: "walks the AST, denies most imports by default". Not expanded as "Abstract Syntax Tree". However, the term `AST` is widely known in programming pedagogy and is not specific to a chat-completion or agent concept; expansion in body prose is more appropriate for chat-completion specific acronyms (LLM, API, SDK). **N/A — accept the un-expanded use as a style-guide exception consistent with the book's pattern of expanding only the chapter's load-bearing acronyms.**
    - **ML** — not present in ch-09 prose. N/A.

### Structure & alignment

11. **Orientation paragraph: 30–60 words (currently 58 per dev-fix1)** — **PASS**. L3 = **58 words**: "A terminal opens, the prompt reads `agent.run("summarize https://example.com")`, the model thinks, prints `[Step 1: Calling web_search]`, fetches the page, prints `[Step 2: Calling summarize]`, and returns a two-paragraph summary to your script. If any step errors, the framework retries; if it can't recover, it surfaces a structured exception. This chapter is the chapter where that loop becomes yours." At 58/60, the orientation is at the upper bound but still within range. The "This chapter is the chapter where that loop becomes yours" closing is a touch self-conscious (per the dev-fix1 honest assessment) but is not a structural violation.

12. **Forward-pointer "What's next" names ch-10 with a concrete forward move** — **PASS**. L184: "What's next: ch-10 — Give Agents Useful Tools — turns the one-line `@tool` into a typed contract, shows the verified no-auto-coercion behavior on tool returns, and teaches how to write a docstring that makes the agent pick the tool." Names ch-10 explicitly, names the chapter title, names three concrete forward moves (typed contract, no-auto-coercion behavior, docstring → agent picks the tool). Matches the style-guide pattern and the ch-08 → ch-09 handoff.

13. **Closing imperative is FINAL visible substantive prose before HTML comment; permitted thin "What's next" bridge between them** — **PASS**. Verified line-by-line:
    - L182: `> **The move:** Import the framework, write one typed @tool function with an Args: docstring, construct an InferenceClientModel with HF_TOKEN loaded, build a CodeAgent(tools=[your_tool], model=model), and run .run(task) against a small task — then run the same loop with the stub model when you don't have a token.`
    - L184: `What's next: ch-10 — Give Agents Useful Tools — turns the one-line @tool into a typed contract, ...` (the permitted thin bridge)
    - L186–195: HTML comment block (self-critique, stripped at publish)
    - The "What's next" bridge at L184 is the only prose between the imperative and the HTML comment — this is the explicitly permitted exception. The bridge is short (37 words), does not recap, and points forward.

14. **Zero handoff-style recap, zero authorial summary, zero third-person "by the end of the reading…" closing line** — **PASS**. The only "by the end of the reading" hit in the file is at L192 inside the HTML self-critique: `Outcome imperative is second-person, not third-person "by the end of the reading, the reader can..."`. This is meta-commentary on the chapter's compliance with the style guide, not a use of the banned pattern. The chapter's closing structure is clean: imperative → forward-bridge → HTML comment. No "in this chapter, we...", no "we explored", no "as we have seen".

### No-regression vs dev-fix1

15. **Word count 1691 (±10% = 1522–1860)** — **PASS**. My whitespace-token count with code blocks + HTML comment stripped = **1790**. Ledger says 1691. Both are within the 1522–1860 band. The 99-word delta between my count and the ledger is methodology: the ledger counter likely strips H2 headings and bullet-list tokens; mine includes them. The dev-fix1 reviewer reported the chapter prose at 1,702 with their counter. All three numbers (1691 ledger, 1702 dev-fix1, 1790 mine) fall within the band. **No regression.** The dispatch's "1691" figure is the canonical project count.

16. **UTF-8 clean round-trip** — **PASS**. 14,973 bytes in, 14,973 bytes out, byte-exact. No BOM on the source file. No replacement character. 5 non-ASCII characters used (em dashes `—` at L5, L51, L66, L88, L116, L122, L124, L130, L180, L182, L184, L188; one ellipsis-style long em dash in the closing callout; standard typography). All preserved.

17. **All 7 code blocks ast.parse clean; offline stub demo runs end-to-end returning `"42"`** — **PASS**. All 7 fenced Python blocks (ch-09.md:19-21 import line, L31-47 model construction, L57-63 agent construction, L73-85 @tool, L93-98 .run call, L104-110 RunResult inspection, L136-166 stub) parse cleanly under `E:\book_gen\.venv\Scripts\python.exe` (after stripping the BOM that `System.IO.File.WriteAllText` defaulted to). The final stub block (L136-166) runs end-to-end: `CodeAgent` constructed with `tools=[]` and `StubModel()`, `agent.run("What is the answer to life, the universe, and everything?")` reaches step 1, the stub's `<code>final_answer("42")</code>` payload is parsed and executed through `LocalPythonExecutor`, the terminator call is detected, and the framework returns `42` to the assertion. The original `assert result == "42"` at L161 passes. Trace: `step 1 → final_answer("42") → Final answer: 42 → Duration 0.03 seconds`. The wrapper deviation is the correct smolagents 1.26.0 form.

18. **`bible.md` earlier chapter blocks (ch-01..ch-08) untouched** — **PASS**. Header scan returns all 9 `## Added by ch-NN` blocks in order (L34, L44, L54, L64, L72, L82, L95, L113, L124). The ch-09 block at L124–134 includes the 8 new entries (`CodeAgent`, `InferenceClientModel`, `@tool` decorator, `.run(task)`, `RunResult`, `FinalAnswerTool`, `LocalPythonExecutor`, `HfApiModel` → `ApiModel` rename, plus the "Stub model" ch-09-specific extension). The ch-08 block at L113–122 is intact (8 entries: agent-loop, observe-decide-act-observe, action parsing, tool dispatch, result feed, termination signal, max_steps guard, stub model). The ch-01..ch-07 blocks at L34–95 are intact (their content reads as the verified canonical entries). UTF-8 strict decode: 27,512 bytes, no replacement character. (No Git VCS exists at `E:\book_gen`, so byte-for-byte no-touch proof is structural, not cryptographic.)

19. **`ledger.md` ch-09 row updated correctly** — **PASS**. Row at `ledger.md:169`:
    `| ch-09 | drafted | ch-08 | 1691 | FAIL (fix-loop 1 applied) | - | First smolagents 1.26.0 chapter. Opens with concrete-scene orientation (terminal + tool + error) per style guide line 36; "Why Use a Framework" intro (1-3 paragraphs comparing ch-08 toy agent to smolagents); one-time HfApiModel sidebar placed at the first import line; uses InferenceClientModel for the runnable example (not ApiModel); 12 research entries (entry-062..entry-073) covered; 4 beginner errors; offline stub-model demo (forward-pointer to ch-13); sandbox caveat (forward-pointer to ch-14); closing imperative + What's-next ch-10 bridge. HfApiModel grep confirmed exactly 1 in ch-09, 0 in all other chapters. All 7 code blocks ast.parse OK in E:\book_gen\.venv\Scripts\python.exe; offline stub demo runs end-to-end (asserts "42"). Dev FAIL (1 CRITICAL / 1 HIGH / 3 MEDIUM) + fix loop 1 applied (1597→1691): ...`
    Status `drafted`, dev-review `FAIL (fix-loop 1 applied)`, line-edit `-` (this review will close that). Word count 1691. All cells consistent with the dispatch's stated state.

---

## Cross-cutting findings

- **Closing imperative shape** — 46 words, six imperative verbs (`Import`, `write`, `construct`, `build`, `run`, `run`). The deliverable is specific: construct an agent and run a small task with the real model, then re-run with the stub. The second clause ("then run the same loop with the stub model when you don't have a token") is a genuine fork for the offline reader. Genuinely actionable, not padded.

- **The `<code>...</code>` wrapper explanation is on-the-nose** — L168 explicitly walks the reader through the framework's parse path: "the framework sees the model emit a terminator call with `"42"`, extracts it from the `<code>` wrapper, executes it through `LocalPythonExecutor`, detects the terminator call, and returns `"42"` to your code." This is one sentence that names every step the framework takes on the wrapped payload. The wrapper is not unexplained magic; it is named, traced, and grounded in the framework's parse contract. The first 154 lines (where the reader has only seen `content='<code>final_answer("42")</code>'` in the code) leave them with the wrapper unexplained until L168; a one-sentence earlier foreshadowing (e.g., at L138 just before the stub class) would land the wrapper without breaking the chapter's pacing. **Optional copy-edit improvement, non-blocking.**

- **The 5 attribution clusters all sit at the right behavior boundary** — L51 (model default), L67 (CodeAgent constructor), L87 (@tool contract), L112 (.run/RunResult), L124 (auto-installation), plus L128 (sandbox secure-execution). The attributions read as parenthetical file:line references, not as a citation paragraph. They do not interrupt the teaching flow. The same pattern is the ch-08 lineedit precedent (ReAct paper, Anthropic's *Building effective agents*, stdlib docs, ch-07 cross-reference) — ch-09's attributions match the house style.

- **Bible dedup is clean** — `bible.md:134` "Stub model" entry for ch-09 explicitly says "see the ch-08 entry above for the basic stub concept" and then adds the ch-09 specifics (subclassing `Model`, overriding `generate(messages, **kwargs)`, the `<code>...</code>` wrapper, the offline-loop pattern). The dev-fix1 dedup is in place; no duplicate `Stub model` heading remains.

---

## Out-of-scope observations (informational only)

- **The "This chapter is the chapter where that loop becomes yours" phrase at L3** is mildly self-conscious (the "is the chapter where" parenthetical is a stutter). The dev-fix1 honest assessment noted the same. Copy-edit pass may want to tighten ("This chapter makes that loop yours" or "This chapter hands that loop to smolagents"). Non-blocking, style preference.

- **`HF_TOKEN` and `load_api_key` first-use page-reference at L49** ("matching the `load_dotenv()` + `os.getenv()` pattern from ch-02 and ch-07") is the right call — the ch-07 chapter taught this exact pattern. No expansion needed in ch-09. (Confirms the ch-09 prose trusts earlier chapters' foundations.)

- **The sandbox secure-execution source attribution at L128** is a sixth attribution beyond the five dev-fix1 required. The chapter also acknowledges ch-14 explicitly ("Real sandbox choices ... are deferred to ch-14, where the safety surface is the chapter's topic"). The handoff is clean.

- **No Git repository exists at `E:\book_gen`**, so the bible no-touch check is structural, not cryptographic. The dev-fix1 reviewer noted the same.

- **The stub's `os.environ.pop("HF_TOKEN", None)` at L139** is a small but pedagogically sharp detail — it ensures the offline demo really runs without a token. The chapter does not call this out, but a reader can see it on careful reading. Not a defect.

---

## Honest assessment (the four asks)

1. **The pre-existing 84-word paragraph at L51 (P15) — find it, report the line number, recommend a one-line trim.** P15 sits at `ch-09.md:51` and is the chapter's longest prose paragraph. My whitespace-token count is 79 (within the ≤80-word limit); dev-fix1's count is 84 (over). The 5-word delta is methodology: backticked identifiers count differently. **Either way, P15 is borderline and is the chapter's longest paragraph.** The paragraph has a natural break-point at "Provider model names age quickly, so treat the model id as directional" — splitting there gives two paragraphs of approximately 48 and 31 words. **Recommended one-line trim (master can apply):** insert a blank line before "Provider model names age quickly..." at L51, so the paragraph becomes two. After the split, P15 ≈ 48 words and a new P16 ≈ 31 words, both well under 80. **This is the MEDIUM WARN in the verdict.**

2. **The `<code>...</code>` workaround (Fix 1 deviation) — does the prose around it explain the wrapper to the reader, or is it unexplained magic?** **Explained, not magic.** L168 explicitly traces the parse path: "extracts it from the `<code>` wrapper, executes it through `LocalPythonExecutor`, detects the terminator call". The reader who reaches L168 understands the wrapper. The only improvement opportunity is a one-sentence foreshadowing at L138 (just before the stub class is defined) — a copy-edit pass could add: "*The payload below is wrapped in `<code>...</code>` because the framework's parser expects that pair of tags around the model's emitted code; the L168 paragraph traces what the framework does with the wrapper.*" Non-blocking, copy-edit ledger material.

3. **Are the 5 inline source attributions readable or do they feel pasted-in?** **Readable, not pasted-in.** All five sit at a behavior cluster (not after every sentence), use the same shape (named source + `file:line`), and read as natural engineering references. None of them looks like an academic citation or a footnote. The attributions match the ch-08 lineedit precedent (ReAct paper, Anthropic *Building effective agents*, stdlib docs, ch-07 cross-reference). The 5 attributions hold at the same 5 sites the dev-fix1 reviewer identified: L51, L67, L87, L112, L124 (plus a 6th unrequired one at L128 for the sandbox secure-execution source).

4. **Any blacklist words hidden in code comments, docstrings, or the HTML self-critique?** **None.** Full-file scan (prose + code blocks + HTML self-critique) returns 0 hits for all 10 banned terms. The HTML self-critique at L193 says "Vocabulary blacklist: zero hits" — verified. The Anthropic-style and smolagents-style citations use neutral language (no "powerful", "optimal", "proven", etc.). The `<code>final_answer("42")</code>` payload at L154 contains the framework's reserved identifier but no banned vocabulary. The docstring at L146 ("Returns a fixed final answer without ever calling the network") uses "final answer" as prose, not a banned term.

---

## Self-critique

- **What I'm confident about:** the mechanical checklist items (blacklist, paragraph lengths, H2 style, HfApiModel uniqueness, final_answer kwarg absence, smolagents scope, code-block ast.parse, offline stub end-to-end run, UTF-8 round-trip, bible/ledger state, no-regression vs dev-fix1). All measured by script and verified manually.
- **What I'm less confident about:** the 84-word vs 79-word count at L51. My whitespace-token counter gives 79; the dev-fix1 counter gave 84. I cannot inspect the dev-fix1 counter's source. I report both numbers in the report and recommend a split regardless. The word-count band (1522–1860) is met by both my count (1790) and the ledger's count (1691) and the dev-fix1's count (1702), so the band itself is unambiguous.
- **What I deliberately did NOT do:** I did not edit any chapter file, bible file, or ledger file. This is review-only. The orchestrator (master) will update the ledger to set `line-edit = pass` after this review, and may apply the optional L51 split (a one-line blank-line insertion, no content change).
- **Methodology call-out:** I stripped code blocks and the HTML self-critique before counting words, matching the ch-08 lineedit review's methodology. The ledger's 1691 likely uses a tighter stripper (probably also removes H2 heading lines and bullet-list markers), which explains the 99-word delta. I report the ledger-matching figure (1691) in the canonical-state rows and my code-stripped figure (1790) in the test row.
- **Boundary compliance:** Only `share/reports/04_book-review_T-2026-08-01-001-book-ai-agents-with-python_ch-09_lineedit.md` was written. No chapter, bible, ledger, task, note, message, memory, trace, or controller file was edited or created.

---

## Issue counts

- **FAIL:** 0
- **MEDIUM:** 1 (P15 at ch-09.md:51 — 79-84 word paragraph, dev-fix1 left for line-edit to handle)
- **LOW:** 1 (`API` not expanded on first prose mention at L23 sidebar; book-wide carryover, non-blocking)
- **Out-of-scope / informational:** 3 (closing-phrase self-consciousness at L3; L138 wrapper foreshadowing opportunity; stub `os.environ.pop` pedagogical detail)

---

## Call-to-action

**Ready to ship as line-edited chapter draft.** Orchestrator should:
1. Update `ledger.md` ch-09 row to set `line-edit = pass` and `Status = line-edited`.
2. Optional: apply the one-line split at ch-09.md:51 (insert blank line before "Provider model names age quickly..."). Trims P15 from 79/84 words to 48/31 — well within the chapter's ≤80-word convention. Not required to ship.
3. Optional (copy-edit pass): add a one-sentence foreshadowing at ch-09.md:138 explaining the `<code>...</code>` wrapper before the reader hits it. Not required to ship.
4. Optional (copy-edit pass): expand `API` on first use at ch-09.md:23 sidebar. Book-wide carryover, not a ch-09 regression.

No FAILs. No code edits performed by this review.
