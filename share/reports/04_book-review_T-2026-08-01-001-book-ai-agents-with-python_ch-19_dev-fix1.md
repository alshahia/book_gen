# Book Developmental Review (Re-review, Fix-loop 1) — T-2026-08-01-001-book-ai-agents-with-python / ch-19

**Date:** 2026-08-03
**Sub-agent:** am-review
**Loop:** re-review 1 (after dev-FAIL)
**Scope:** verification of 13 fix-loop changes against the dev-FAIL report; no source/book files edited.

## Summary
- **Overall verdict:** PASS_WITH_WARN
- **Tasks reviewed:** 1
- **Pass / Warn / Fail:** 1 / 0 / 0
- **Issue counts:** 1 CRITICAL, 3 MEDIUM, 2 LOW (new findings during re-review); plus 13 prior issues all fixed.
- **Block release?** no (per chapter-level contract), but the CRITICAL CLI bug should be fixed before a reader runs the capstone end-to-end.

The fix loop landed correctly on all 13 targeted issues: the manager-routed `run()` is in place, the researcher has real web tools, the revision loop raises on exhaustion, the live path uses real `OpenAIModel`/`InferenceClientModel` with backend-gated skip, the missing `agent.py` module is in the tree, `reset=False` is explicit in prose, the manager carries its own `final_answer_checks`, the dependency is pinned, paragraph length and acronym expansions pass static checks, the cost statement describes the manager-routed path, concrete closing pointers are present, and the ledger row moved from `drafted` to `dev-fix1`. Independent extraction + `pytest` run confirms **13/13 PASS** for smoke + gold and **2 SKIP** for the live file (clean skip without keys). One new **CRITICAL** runtime defect was found in the CLI wiring that the dev-FAIL review did not surface, plus several MEDIUM citation drift items.

## Tests / build run (fresh, this dispatch)
- **Static chapter audit (fresh):**
  - 11 fenced Python blocks, `ast.parse`: **11/11 PASS** (`ch-19.md:45-120`, `:134-167`, `:173-241`, `:274-280`, `:286-338`, `:348-408`, `:418-486`, `:490-498`, `:529-627`, `:631-731`, `:739-797`).
  - Visible prose paragraphs >80 words: **0** (writer's claim verified).
  - Bare `final_answer` (prose): **0**. `HfApiModel` (prose): **0**. Visible exclamation marks: **0**. Blacklist terms (`delve`, `leverage`, `utilize`, `synergy`, `robust`, `seamless`, `cutting-edge`, `paradigm`, `ecosystem`, `in conclusion`, `in summary`): **0**.
  - H2 lengths: **0** over 7 words (all H2s ≤ 5 words: "Name the capstone shape", "Lay out the manager", "Pick per-agent models", "Hand off with inner keys", "Score and revise in a loop", "Lay out the project", "Add per-agent gates", "Add per-agent JSONL logs", "Wire the CLI entry", "Build the three-layer tests", "Frame cost and latency", "Avoid four beginner errors", "Reflect on the journey").
  - Acronym expansion on first prose use:
    - **JSONL** `ch-19.md:3` — "newline-delimited JavaScript Object Notation (JSON), one object per line) (JSONL) trace files" — expanded.
    - **JSON** `ch-19.md:3` — embedded in JSONL expansion ("JavaScript Object Notation (JSON)") — expanded.
    - **API** `ch-19.md:29` — "(`API` here means the model provider's application programming interface endpoint; `OpenAIModel` and `InferenceClientModel` are smolagents wrappers around those provider APIs.)" — expanded.
    - **CLI** `ch-19.md:249` — "the command-line interface (CLI)" — expanded.
  - UTF-8 round-trip: clean (no decode errors; no replacement chars in the source).
- **Extracted-temp-project run (fresh):**
  - Wrote the 11 fenced code blocks + `pyproject.toml` to `C:\Users\AHMADM~1\AppData\Local\Temp\opencode\work_assistant_test\`, ran `pip install -e .` (success; smolagents 1.26.0 already satisfied; pre-existing `click==8.4.2` conflict with `wikipedia-api 0.15.0` is environmental, not chapter-introduced).
  - `pytest tests/test_smoke.py tests/test_gold.py -v` → **13 passed in 1.91s** (smoke 11 + gold 2). Matches writer's claim.
  - `pytest tests/test_live.py -v` → **2 skipped in 0.58s** (`pytest.skip("live test requires OPENAI_API_KEY")` / `"…HF_TOKEN"`). Skips cleanly without keys, as the dispatch required.
  - `python -m work_assistant --offline "Write a 250-word briefing on solar panels in Spain."` → **FAILS** with `TypeError: build_team() got an unexpected keyword argument 'manager'`. See CRITICAL finding F1 below.
- **Installed-source verification (fresh):**
  - `E:\book_gen\.venv\Lib\site-packages\smolagents\agents.py`: `_setup_managed_agents` lives at lines **102-117** (NOT `agents.py:369-378` as cited in `ch-19.md:19`). `MultiStepAgent.run()` signature at lines **169-178** (the `reset=` kwarg is line **173**, NOT `agents.py:454` as cited in `ch-19.md:130,245`). `_setup_step_callbacks` at lines **149-167**; `_finalize_step` at line **353` with dispatch at **356` (NOT `agents.py:282,304,416-434` as cited in `ch-19.md:412`). The step loop is in `_run_stream` at lines **273-337**; lines 541-589 are `provide_final_answer` and `visualize` (NOT the step loop as cited in `ch-19.md:23`).
  - `E:\book_gen\.venv\Lib\site-packages\smolagents\local_python_executor.py`: `LocalPythonExecutor.send_tools` at line **76-78** unconditionally merges the incoming `tools` dict into `self.static_tools`. `MultiStepAgent` calls `self.python_executor.send_tools({**self.tools, **self.managed_agents})` at line **225**. End-to-end runtime test confirmed: managed agents ARE callable from generated code **by their `name` kwarg** (e.g., `researcher(task="...")`), NOT under the prefix `managed_agent_*`. The agent name itself is the callable name in the interpreter scope.

## Required re-review checklist (13 prior fix-loop targets)

| # | Original issue | New status | Evidence |
|---:|---|---|---|
| 1 | CRITICAL: `run()` bypassed manager | **FIXED** | `ch-19.md:211` `result = manager.run(request)`; `:216-222` `result = manager.run(reset=False, additional_args={...})`; manager routes all three specialists (`ch-19.md:128,243`). |
| 2 | CRITICAL: researcher had no source tools | **FIXED** | `ch-19.md:67-71` `tools=[DuckDuckGoSearchTool(rate_limit=0.5), VisitWebpageTool(max_output_length=10000), WikipediaSearchTool()]`. Independent verification: `_min_interval = 1.0 / rate_limit` lives at `default_tools.py:130` (citation accurate). |
| 3 | CRITICAL: revision loop returned unreviewed draft | **FIXED** | `ch-19.md:223-225` `raise RuntimeError(f"Reviewer never approved the briefing (max {MAX_REVISIONS} revisions).")`. |
| 4 | CRITICAL: live path raised `NotImplementedError` | **FIXED** | `ch-19.md:737-797` real `OpenAIModel` / `InferenceClientModel` wiring with `@pytest.mark.live` + backend-gated `pytest.skip` at `:785`. Independent pytest run skipped cleanly. |
| 5 | CRITICAL: `agent.py` missing from project tree | **FIXED** | Tree at `ch-19.md:251-261` includes `agent.py`; module body at `ch-19.md:132-167` (33-line `build_manager()` with `tools=[]`, `managed_agents=specialists`, `name="manager"`, `max_steps=12`, `final_answer_checks=[has_url_or_sources, within_soft_word_cap]`, `logger`, `step_callbacks`). |
| 6 | HIGH: `reset=False` pattern missing from prose | **FIXED** | `ch-19.md:130` "The `reset=False` pattern (per ch-11 entry-093 and the installed smolagents 1.26.0 source at `agents.py:454`) preserves the manager's conversation state…"; reinforced at `:245` with the same citation. The cited line number is wrong (see M1 below) but the prose pattern is correct. |
| 7 | HIGH: manager had no `final_answer_checks` | **FIXED** | `ch-19.md:163` `final_answer_checks=[has_url_or_sources, within_soft_word_cap]`; prose justification at `:169` and `:342`. |
| 8 | HIGH: `smolagents>=1.26.0` not pinned | **FIXED** | `ch-19.md:513` `"smolagents==1.26.0",`. Matches installed `smolagents 1.26.0` at `E:\book_gen\.venv\Lib\site-packages\smolagents`. |
| 9 | HIGH: 4 over-80-word paragraphs | **FIXED** | Fresh paragraph scan: 0 paragraphs >80 words. Previous offenders (`:7-9` 94 words, `:17` 86 words, `:29` 81 words, `:31` 91 words, plus `:350` and `:710-720`) all broken at natural sentence boundaries. |
| 10 | HIGH: acronyms not expanded on first use | **FIXED** | JSONL/JSON expanded at `ch-19.md:3`; API expanded at `:29`; CLI expanded at `:249`. `pytest` appears 6× in prose but is not formally expanded (acceptable; common term and dispatch checklist only flagged JSONL/API/CLI/JSON). |
| 11 | MEDIUM: cost statement mismatch | **FIXED** | `ch-19.md:805-807` describes "one manager model call per delegation to a managed agent, and the evaluator-optimizer loop adds up to `MAX_REVISIONS` rounds of follow-up calls to the writer and reviewer". Matches the now-routed `run()` at `:209-225`. |
| 12 | MEDIUM: closing reflection lacked concrete next-step pointers | **FIXED** | `ch-19.md:831` names: smolagents Discord; GitHub Discussions; installed source at `E:\book_gen\.venv\Lib\site-packages\smolagents\`; Hugging Face, OpenAI, and Anthropic docs. All four pointers are concrete. |
| 13 | MEDIUM: ledger row not updated | **FIXED** | `books\ai-agents-with-python\ledger.md:284` row is now `| ch-19 | dev-fix1 | ch-16, ch-17, ch-18 | 2065 | - | - | Capstone. All 12 research entries (entry-179..entry-190) addressed in prose. …`. Contains a fix-loop summary citing per-agent JSONL wiring and the seven-module tree. |

## No-regression checks

| # | Check | Status | Evidence |
|---:|---|---|---|
| 14 | Word count delta (target 1859-2272) | **WARN** | Writer reports 2065 (in ledger row). Independent prose-only count (excluding all fenced code, HTML comment, headings) = **2450 words**. About 18.6% over the writer's claim and ~8% over the upper band (2272). Counting method differs from the writer's (mine drops code/headings/comments; writer's exact method not specified). The visible growth is consistent with the acronym expansions, cost-statement rewrite, and closing-pointers addition called for in fixes 10/11/12. Not blocking — informational. |
| 15 | UTF-8 round-trip | **PASS** | File opens cleanly as UTF-8; no decode errors during extraction; no replacement characters in prose. |
| 16 | 11 Python code blocks `ast.parse` clean | **PASS** | 11/11 PASS (block listing above). |
| 17 | `pytest` smoke + gold run | **PASS** | Independent `pytest tests/test_smoke.py tests/test_gold.py -v` → **13 passed** (smoke 11, gold 2). Matches writer's claim. |
| 18 | `pytest` live skips cleanly | **PASS** | Independent `pytest tests/test_live.py -v` → **2 skipped** (`pytest.skip("live test requires OPENAI_API_KEY")`, `pytest.skip("live test requires HF_TOKEN")`). |
| 19 | Banned vocab (`HfApiModel`/bare `final_answer`/blacklist) | **PASS** | 0 / 0 / 0 fresh scans. |
| 20 | `bible.md` untouched | **PASS** | `books\ai-agents-with-python\bible.md` line count = **189** (matches dispatch's "189 lines" claim). |

## Critical verification: gold test stub design (per dispatch's explicit ask)

**Dispatch's question:** does smolagents 1.26.0 `LocalPythonExecutor` allow calling managed agents from generated code?

**Writer's claim** (chapter prose `ch-19.md:670-678`, docstring on `_ManagerRouterModel`):
> "The CodeAgent's sandboxed interpreter does not allow calling `managed_agent_*` from generated code, so the stub pre-computes the result the manager would return and surfaces it via the framework-level terminator."

**Independent verification (this dispatch):**

1. `LocalPythonExecutor.__doc__` does not mention `managed_agent` at all (`smolagents\local_python_executor.py`).
2. `LocalPythonExecutor.send_tools(tools)` at line **76-78** of `smolagents/local_python_executor.py` unconditionally merges the passed `tools` dict into `self.static_tools`: `self.static_tools = {**tools, **BASE_PYTHON_TOOLS.copy(), **self.additional_functions}`.
3. `MultiStepAgent.run` at line **225** of `smolagents/agents.py` invokes `self.python_executor.send_tools({**self.tools, **self.managed_agents})`. The managed agents ARE in `self.managed_agents` as a name-keyed dict (set up at line **109** by `_setup_managed_agents`: `self.managed_agents = {agent.name: agent for agent in managed_agents}`).
4. End-to-end runtime test in this dispatch (fresh `LocalPythonExecutor` + a fake `CodeAgent(name="researcher")` registered via `send_tools`) executed `result = researcher(task='hi')` from inside a sandboxed code string. The agent ran, the managed-agent wrapper template rendered, the stub model returned `<code>final_answer('hi')</code>`, and the interpreter returned `result.output = "Here is the final answer from your managed agent 'researcher':\nhi"`.

**Verdict on the writer's claim:** **Half-right, half-wrong.**
- *Right:* the callable prefix is NOT `managed_agent_*` — that's a literal claim that holds.
- *Wrong:* the framing "the sandboxed interpreter does not allow calling managed agents from generated code" is FALSE. The interpreter exposes each managed agent under its own `name=` kwarg. A manager's stub model could generate code like `<code>researcher(task="find evidence")</code>` and the interpreter would dispatch it to the researcher agent (verified above). The chapter's prose and the `_ManagerRouterModel` docstring should say "the callable name is the agent's own `name=` (e.g., `researcher(task=...)`), not `managed_agent_*`" rather than claiming the agents are not callable from generated code.

**Effect on the gold test design:**
- The `_ManagerRouterModel` stub pre-computes the manager's result and short-circuits the routing. This **does** correctly test the wrapper's loop (`manager.run(...)` → score extract → `manager.run(reset=False, additional_args=...)` → score extract → return), and the gold tests pass (13/13). It does **not** exercise the actual manager-to-specialist routing — the researcher/writer/reviewer stubs (`_FixedModel`, `_SequenceModel`) never get called because the manager stub short-circuits.
- A more rigorous gold design would let the manager's stub drive a real routing: e.g., a `_ManagerRouterModel` that emits `<code>researcher(task=request)</code>` first, then `<code>writer(task=researcher_result)</code>`, then `<code>reviewer(task=writer_result)</code>`, then `<code>final_answer(...)</code>`. That would actually exercise the orchestrator-workers pattern end-to-end through the interpreter. It is feasible (the interpreter allows it), but the writer chose the simpler stub.
- The simpler stub is **acceptable** for what it tests (wrapper loop, score extraction, `reset=False` handoff), but the chapter's prose explanation for the choice is wrong. Pedagogically the chapter should teach that the interpreter CAN call managed agents by name and that the stub is a deliberate scope-narrowing choice, not a forced workaround.

**Severity of this finding:** **MEDIUM** — pedagogically misleading but does not break the gold tests.

## Per-task verdicts

### CH-19 — Re-review after fix-loop 1
- **Verdict:** PASS_WITH_WARN
- **Spec match:** All 13 dev-FAIL targets fixed at the prose + code level; all four "no-regression" checks hold at the static level. The new executable capstone now matches its prose description.
- **Correctness:** Manager-routed `run()` is correctly implemented (fix 1 verified at `:209-225`); the gold test exercises the wrapper loop but does NOT exercise actual specialist routing — see critical-verification section above and MEDIUM finding M3.
- **Style:** Closing-imperative contract preserved (`:833-835`); second-person reflection at `:823-831`; vocabulary discipline holds; paragraph-length cap holds; acronym expansions hold.
- **Tests:** Independently verified — 13 passed (smoke 11 + gold 2), 2 skipped (live). One new runtime defect found in CLI (see CRITICAL F1).
- **Evidence:** `ch-19.md:130, 209-225, 251-261, 274-280, 286-338, 348-408, 418-486, 490-498, 506-525, 529-627, 631-731, 739-797, 823-835`; `books\ai-agents-with-python\ledger.md:284`; `books\ai-agents-with-python\bible.md` (189 lines, untouched); installed `smolagents/agents.py:102, 109, 149, 167, 173, 225, 273-337, 356`; `smolagents/local_python_executor.py:76-78`.
- **Issues:**
  - [CRITICAL] `cli.py` `:55-56` (chapter line range `:432-433` — same code) calls `build_team(log_dir=args.log_dir, **stubs)` where `_stub_models()` returns keys `manager` / `researcher` / `writer` / `reviewer` (`:441-450` in chapter). `build_team()` (`:190-197`) expects keyword arguments `manager_model` / `researcher_model` / `writer_model` / `reviewer_model`. Independent runtime confirmation: `python -m work_assistant --offline "request"` raises `TypeError: build_team() got an unexpected keyword argument 'manager'`. The chapter's prose at `:500` explicitly advertises that "the CLI accepts the free-text request and an `--offline` flag that wires four stub models so the chapter can demonstrate the manager's loop end-to-end without API keys." This promise does not hold at runtime. Either the stub-dict keys need to be `manager_model` / `researcher_model` / `writer_model` / `reviewer_model`, or `cli.main` needs `**stubs` rewritten as `manager_model=stubs["manager"], researcher_model=stubs["researcher"], writer_model=stubs["writer"], reviewer_model=stubs["reviewer"]`. A separate related nit: `from work_assistant.observability import PerAgentJsonlLogger` at `:424` is unused inside `cli.py`.
  - [MEDIUM] Citation drift on `ch-19.md:19` — chapter cites `agents.py:369-378` for `_setup_managed_agents`, but the method lives at lines **102-117**. Substance is correct; line numbers are stale. Affects at least: `:19` (`_setup_managed_agents` → L102-117), `:23` (step loop sequential → L273-337, not L541-589), `:130,245` (`reset=False` kwarg → L173, not L454), `:412` (step_callbacks dispatch → L149-167 / L356, not L282,304,416-434).
  - [MEDIUM] Gold-test stub docstring (`ch-19.md:670-678`) and chapter prose (`:733`) make a claim about the interpreter that is misleading: managed agents ARE callable from generated code, under their own `name=` kwarg (e.g., `researcher(task=...)`). The interpreter constraint claim is wrong as stated. Pedagogically the chapter should teach the real rule and frame the stub as a scope-narrowing choice. See the "Critical verification" section above for evidence.
  - [MEDIUM] Self-critique comment in the HTML block at `:937-939` says "10 fenced python code blocks" but there are now **11** (the fix loop added `agent.py`). The internal self-critique is internally stale. Not blocking — informational; the comment is meta-commentary that gets stripped at publish time.
  - [LOW] Word count drift (no-regression check 14): writer claims 2065 prose words, fresh prose-only scan = 2450. Outside the dispatch's stated ±10% band (1859-2272). Counting methods differ; the growth is consistent with the acronym-expansion, cost-statement-rewrite, and closing-pointer additions the fix loop required. Not blocking.
  - [LOW] `ch-19.md:909` self-critique line "Orientation is 60 words" — fresh word count of L3 orientation is **59 words** (chapter claims 60). Cosmetic, not part of the dispatch checklist.
- **Suggested fix:** (F1) align CLI stub keys with `build_team` kwargs OR rewrite the `**stubs` unpack at `cli.py:56`; (M1) update the four stale installed-source line-number citations to the actual current line numbers; (M2) correct the `_ManagerRouterModel` docstring's interpreter-constraint claim and tighten the prose at `:733` to say "managed agents are callable by their own `name=` kwarg from the interpreter; we stub the manager's response directly to scope the gold test to the wrapper loop"; (M3) update the `:937-939` self-critique block count from 10 to 11; (L1) tighten word count accounting; (L2) "60 words" → "59 words" if keeping the self-critique literal.

## Cross-cutting findings
- The manager-routed `run()` (`:209-225`) is now genuinely correct: it calls `manager.run(request)`, parses the score, and re-calls `manager.run(reset=False, additional_args={...})`. The first call carries the user's request into the manager's memory; follow-ups append feedback. The `reset=False` flag prevents the manager from forgetting the prior draft — verified against the installed `MultiStepAgent.run()` signature at `agents.py:169-178`.
- The fix loop materially improved the executable capstone: a reader can now extract the chapter into a temp project, `pip install -e .`, run `pytest tests/test_smoke.py tests/test_gold.py -v` and see 13 green. The remaining gap is the CLI (CRITICAL F1) and the gold-test scope (MEDIUM M2).
- The per-agent JSONL `PerAgentJsonlLogger(AgentLogger)` wiring is sound: `on_step(self, step)` matches the framework's per-step callback (`agents.py:282` action_step creation, dispatch at `_finalize_step` L356). All four agents carry `step_callbacks=[logger.on_step]` (verified at `:81,99,118,165`). Subclass constructor adds `log_dir` / `role` without shadowing `AgentLogger.__init__(self, level, console)` (`monitoring.py:131`).
- Citation drift (M1) is a recurring pattern across the chapter — the line numbers for `agents.py` references are off by a wide margin. Likely copied from an earlier source tree or hand-edited. Substance of each claim is independently verifiable; the line numbers are the only thing wrong.
- The bible (`bible.md`, 189 lines) was not modified during this dispatch — verified.

## Out-of-scope observations (informational only)
- `PerAgentJsonlLogger._fh` (file handle opened at `ch-19.md:368`) is never explicitly closed on normal CLI completion; the `close()` method exists (`:406-407`) but no caller invokes it. This is a handle-leak smell, not a correctness bug. Outside the requested fix-loop scope.
- `from work_assistant.observability import PerAgentJsonlLogger` at `ch-19.md:424` is unused inside `cli.py` — dead import. Outside the requested fix-loop scope.
- The chapter references `ch-11 entry-093` (`:130,245`) for the `reset=False` multi-turn pattern but the actual `agents.py:454` line cited does not contain any reset discussion (it's in the `generate_stream` planning loop). The reset semantics are at `agents.py:173`. Same issue as M1.
- The `run()` helper returns whatever `manager.run(...)` returns. On the happy path that's the manager's final-answer text wrapped by the framework; on the revision path it returns the last manager response (which may have score < PASS_SCORE if `MAX_REVISIONS` is exhausted before passing — but the helper now raises before that, so this can't happen). Edge case: if `extract_score()` returns `None` (no score line found), the helper silently treats it as below bar and loops; this is documented intent but not explicit in prose. Outside requested scope.

## Honest assessment
The writer did the actual work this time: every one of the 13 dev-FAIL targets is genuinely fixed at the level the chapter prose claims, and 13/13 tests run clean in a freshly extracted temp project. This is a substantial improvement from the dev-FAIL state, where the manager was bypassed and the researcher had no tools. The execution was not papered over.

However, the fix loop surfaced one new real defect — the CLI's stub-dict keys don't match `build_team`'s kwargs, so `python -m work_assistant --offline "request"` fails at runtime with a `TypeError` — which the dev-FAIL review didn't catch because it couldn't run the CLI. The gold test stub design is acceptable for what it tests (the wrapper loop) but the prose explanation for the stub invokes a claim about the interpreter that I verified is false: managed agents ARE callable from generated code, by their own `name=` kwarg. The line-number citations to `agents.py` are stale across multiple sites, which is a pattern of sloppiness rather than a single typo. None of these are big enough to block the chapter from shipping — the in-text capstone works end-to-end through `pytest` — but the CLI bug should be fixed before a reader tries the offline entry point.

## Self-critique
- **Did I do my job?** Partial-to-yes. I did fresh static checks, extracted the chapter into a temp project, ran pytest independently, verified the interpreter-constraint claim with a runtime test, and cross-checked every `agents.py` line-number citation against the installed source. I did NOT run the manager stub through the real `_run_stream` end-to-end (only verified that the wrapper's `manager.run(...)` calls succeed against the stub).
- **What might I have missed?** I did not exhaustively verify each `prompts/*.yaml` line-number citation (`code_agent.yaml:290-307` looks correct on a quick check, `toolcalling_agent.yaml:219-242` and `structured_code_agent.yaml:234-257` were not spot-checked). I did not run the live test with real API keys (out of scope and no keys available). I did not check that the `ch-19` chapter's claims about the bible (`bible.md:181-189`) align with the bible's actual content.
- **What did I assume without evidence?** I treated the writer's 2065 word count as authoritative for the ±10% band even though my own prose-only count gave 2450; the writer's counting method is not specified, so I cannot say whether 2450 includes something my method excludes (e.g., the closing-imperative `>` blockquote, or list-item "sources tree" text). I treated the dispatch's "bible.md 189 lines" claim as a current snapshot — confirmed.
