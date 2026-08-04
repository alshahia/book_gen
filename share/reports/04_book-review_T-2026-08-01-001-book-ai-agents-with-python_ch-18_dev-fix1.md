# Book Developmental Review — T-2026-08-01-001-book-ai-agents-with-python / ch-18

**Date:** 2026-08-03
**Sub-agent:** am-review
**Pass:** developmental fix-1 re-review
**Scope:** 11 fix items from dev (FAIL) → fix-1

## Summary

- **Overall verdict:** FAIL
- **Chapter reviewed:** ch-18 — *Project: Research and Briefing Agent* (post-fix)
- **Issue counts:** 2 CRITICAL / 1 HIGH / 0 MEDIUM / 0 LOW
- **Block progression?** yes (FAIL → FAIL; 9/11 fixes genuine, 1 partial, 1 introduced a new CRITICAL regression)
- **One-line summary:** 9 of the 11 fix items are honestly addressed (install guidance, rate_limit=0.5, project surface 4/4, briefing contract in both instructions and validators, closing-imperative order, live-test gating, model factory `resolve_backend`, two beginner-error corrections, three acronym expansions); but the very CLI the fix was supposed to deliver (CRITICAL #3) does not run — `cli.py` calls `build_agent(logger=logger)` and `build_agent` does not accept a `logger` kwarg, so `python -m research_briefing.cli "..."` raises `TypeError` before the model is invoked — and the JSONL per-step claim (CRITICAL #5) is also partial because `log_steps()` is never called by the framework.

## Tests / build run

- Fresh temp project tree built from the chapter's 10 Python fences + `pyproject.toml`. `tests/test_smoke.py tests/test_gold.py -v` → **13 passed in 1.18s** (8 smoke + 5 gold; matches the writer's reported 13/13).
- `tests/test_live.py -v` with no API keys → **4 skipped in 0.61s**; the parametrize matrix now expands to 4 cases (2 backends × 2 topics) and each one skips cleanly on its own env var.
- `ast.parse` over all 10 Python blocks → **10/10 PASS**.
- `tomllib.loads()` on the embedded `pyproject.toml` → **OK**; `project.dependencies = ['smolagents>=1.26.0', 'ddgs', 'wikipedia-api']`; `[tool.pytest.ini_options] markers = ['live: ...']` registered.
- `python -m research_briefing.cli --help` → **exit 0**; argparse surfaces the right help text. CLI module imports cleanly.
- `python -m research_briefing.cli "solar panels Spain"` (no API keys) → **exit 1, TypeError**: `build_agent() got an unexpected keyword argument 'logger'`. CLI cannot run end-to-end; see CRITICAL #3a below.
- Inspected installed smolagents 1.26.0 source: `DuckDuckGoSearchTool.__init__` computes `_min_interval = 1.0 / rate_limit`; `MultiStepAgent.__init__` accepts `instructions=`; `AgentLogger` exposes `log`/`log_rule`/`log_markdown`/`log_code`/`log_task`/`log_error`/`log_messages`/`visualize_agent_tree` — **there is no `log_steps` method, and the framework never calls one** (zero hits for `log_steps` across `site-packages/smolagents/`).
- Inspected `agents.py` for step-callback hook: `step_callbacks: list[Callable] | dict[Type[MemoryStep], ...]` (lines 282, 304, 416–434, 623) is the framework's official per-step hook. The writer did not use it.
- UTF-8 round-trip → **PASS**.
- Structural metrics: orientation 49 words; visible-prose word count 2387 (within the writer's claimed band 1616–2461 and inside my ±10% read of `1795 × 1.37 = 2459`); 17 H2 sections, all verb-led and ≤7 words; longest prose paragraph 76 words.

## Per-fix verdicts

### Fix 1 — Install guidance for missing deps → PASS
`pip install ddgs wikipedia-api` is at `ch-18.md:48-50`; the `duckduckgo-search` "different package, older API surface" caveat is at `:52`. The `pyproject.toml` block at `:331-335` also lists both packages as dependencies. Verdict: honest fix, beginner-visible, installable from the README. **PASS**.

### Fix 2 — `rate_limit=2.0` → `rate_limit=0.5` → PASS
Five `rate_limit=0.5` references (`ch-18.md:154,205,273-area prose,560`); zero `rate_limit=2.0` strings remain in code or prose; the prose at `:154` and the closing imperative at `:560` both call out "0.5 queries per second (2-second minimum interval)" and cite `default_tools.py` rate-limit semantics; I verified installed 1.26.0 source `_min_interval = 1.0 / rate_limit if rate_limit else 0.0`. Verdict: honest fix. **PASS**.

### Fix 3 — Complete project surface (cli.py / __main__.py / pyproject.toml / README.md) → FAIL
All four blocks are present (`ch-18.md:283-305,309-317,325-346,352-377`) and the `pyproject.toml` parses as valid TOML. **BUT** `cli.py:298` calls `build_agent(logger=logger)` and `build_agent`'s signature is `(model_name: str = 'openai', log_path: str | None = None) -> CodeAgent` — `logger` is not a kwarg. `python -m research_briefing.cli "solar panels Spain"` raises `TypeError: build_agent() got an unexpected keyword argument 'logger'` on the first call. The README command at `:371` (`python -m research_briefing.cli "solar panels in Spain"`) is the same broken path. The very promise of CRITICAL #3 ("a runnable project surface") is not delivered. The CLI exists, but it does not run. Verdict: **CRITICAL** regression.

### Fix 4 — Briefing contract enforcement → PASS
`BRIEFING_INSTRUCTIONS` at `ch-18.md:93-98` hard-codes 200–400 words, 3–5 URLs, the `Sources:` section, and "Do not fabricate URLs". `agent.py` passes `instructions=BRIEFING_INSTRUCTIONS` at `:141`. Validators tighten to `MIN_BRIEFING_WORDS = 200`, `MAX_BRIEFING_WORDS = 400`, `MIN_SOURCE_URLS = 3` with `_URL_PATTERN = re.compile(r"https?://\S+")` (`:163-167`); `has_sources_line` requires both the `Sources:` line and ≥3 URL matches (`:180-186`). Smoke tests at `:403-436` exercise the new threshold (e.g. `has_sources_line` rejects a 1-URL body). Verdict: contract enforced in both prompt and validators. **PASS**.

### Fix 5 — JSONL per-step logger → PARTIAL (HIGH)
The chapter adds `JsonlLogger.log_steps(self, step)` (`:257-267`) that increments `self.current_step` and writes `{ts, step, type: type(step).__name__, timing}` per call, with a sample line shown at `:275-277`. **However, smolagents 1.26.0 never calls `log_steps()`** — `grep -r log_steps E:\book_gen\.venv\Lib\site-packages\smolagents` returns zero hits, and the framework's `agents.py` calls `self.logger.log(...)`, `self.logger.log_rule(...)`, `self.logger.log_markdown(...)`, `self.logger.log_code(...)`, `self.logger.log_task(...)`, `self.logger.log_error(...)`, `self.logger.log_messages(...)`, `self.logger.visualize_agent_tree(...)` only (lines 482, 584, 740, 1314, 1386, 1402, 1579, 1684, 1743, 1746, 1762). The framework's official per-step hook is `step_callbacks: list[Callable] | dict[Type[MemoryStep], ...]` registered on the `ActionStep` class (lines 282, 304, 416–434, 623), which the writer did not use.

Practical effect: the `log()` override at `:247-255` *does* write one JSONL record per logger call (a real improvement over the original), with `ts`, `step`, and `event` fields, but `current_step` is never incremented, so every record's `step` reads `0`. The chapter's claim at `:273` ("the framework calls `log_steps()` once per step (smolagents 1.26.0 source at `agents.py` integrates the step logger alongside the existing `log()` event hooks)") is FALSE; the cited source does not back the claim. The per-step, per-run trace is structurally not delivered. The fix changes the JSON shape but not the per-step semantics. Verdict: **HIGH** partial.

### Fix 6 — Closing-imperative contract → PASS
Order is now `What's next` (`:558`) → `> **The move:**` (`:560`) → HTML comment (`:562`). The imperative is the final visible substantive paragraph before the orchestrator handoff comment. Verdict: honest fix. **PASS**.

### Fix 7 — Live-test backend gating → PASS
`tests/test_live.py:520-528` decorates with `@pytest.mark.live`, parametrize over `(backend, env_var) ∈ {("openai", "OPENAI_API_KEY"), ("hf", "HF_TOKEN")}` and `LIVE_CASES`, then `if not os.getenv(env_var): pytest.skip(...)`. Result: 4 tests, 4 skipped, no API keys; each test gates on its own backend's key. Verdict: honest fix. **PASS**.

### Fix 8 — Model factory consistency → PASS
`backend_for(name)` at `ch-18.md:101-107` and `resolve_backend(model_name)` at `:110-116`; `build_agent` at `:119-146` resolves `auto` → `hf` when `HF_TOKEN` is set and `OPENAI_API_KEY` is not, otherwise OpenAI; env-var defaults `OPENAI_MODEL="gpt-4o-mini"` and `HF_AGENT_MODEL="Qwen/Qwen2.5-Coder-7B-Instruct"`. Placeholders gone. Live test now selects `model_name=backend` directly. Verdict: honest fix. **PASS**.

### Fix 9 — Bible block-count discrepancy → N/A (master's lane; bible.md untouched)
`bible.md` mtime = 2026-08-03 09:12:51, `ch-18.md` mtime = 2026-08-03 10:59:29. Writer did not touch `bible.md`. The 16-vs-17 discrepancy is pre-existing and master's responsibility per the original review. Verdict: **N/A — unchanged**.

### Fix 10 — Two beginner errors → PASS
Line `:544` now reads "redundant rather than conflicting" for the transitive-`requests` claim; line `:546` now reads "The tool converts the page's HTML to Markdown, not to a plain-text dump (per the installed smolagents 1.26.0 source at `default_tools.py:531`, where `VisitWebpageTool.forward` runs an HTML-to-Markdown conversion)" — matches installed source. Verdict: honest fix. **PASS**.

### Fix 11 — Acronym expansions → PASS
`pytest` expanded at `ch-18.md:65` ("Python's standard testing framework"); `CLI` expanded at `:148` ("command-line interface (CLI) calls `build_agent(...)`"); `API` expanded at `:502` ("the application programming interface (API) key"). The earlier prose at `:52` mentions "API surface" as a phrase ("different package with an older API surface"), which is the common-English sense rather than an acronym introduction; the first standalone acronym introduction of `API` is correctly at `:502`. JSONL and OWASP were already expanded before the fix loop. Verdict: honest fix. **PASS**.

## No-regression verification

| # | Check | Verdict | Evidence |
|---|---|---|---|
| 12 | Word count delta | PASS | visible prose 2387 words (in band 1616–2461, Δ = +592 from 1795) |
| 13 | UTF-8 round-trip | PASS | `Buffer.toString('utf-8')` round-trip equals source byte-for-byte |
| 14 | `ast.parse` over 10 Python blocks | PASS | 10/10 |
| 15 | Smoke + gold pytest | PASS | 13/13 in 1.18s in a fresh temp project with `PYTHONPATH=src` |
| 16 | Live-test skip behaviour | PASS | 4/4 SKIPPED with no `OPENAI_API_KEY` / `HF_TOKEN` |
| 17 | Zero `HfApiModel` in prose | PASS | zero matches in visible prose |
| 18 | Zero bare `final_answer` in prose | PASS | zero matches in visible prose; `final_answer_checks` allowed and used |
| 19 | `bible.md` untouched | PASS | `bible.md` mtime precedes `ch-18.md` mtime; 16 blocks (ch-01..ch-16) intact, ch-17/ch-18 absent by master's-lane choice |

## Issues (this pass)

### CRITICAL

1. **`cli.py` calls `build_agent` with an invalid kwarg; the CLI does not run.** `cli.py:298` does `agent = build_agent(logger=logger)`. `build_agent`'s signature is `(model_name: str = 'openai', log_path: str | None = None) -> CodeAgent` (`agent.py:119-122`). There is no `logger` parameter. `python -m research_briefing.cli "..."` raises `TypeError: build_agent() got an unexpected keyword argument 'logger'` before any model is invoked. The README at `ch-18.md:371` documents the same broken command. Smoke and gold tests pass because they construct `CodeAgent` directly without going through the CLI; the live test uses `build_agent(model_name=backend)` and so does not hit the bug. **Effect:** the very outcome CRITICAL #3 was supposed to deliver — "a runnable `python -m research_briefing.cli "..."` command" — is not delivered. A beginner following the README cannot run the project. This is a regression introduced by the fix loop, not a paper-over.

2. **The JSONL per-step claim is not delivered; `log_steps()` is dead code.** `JsonlLogger.log_steps(self, step)` is defined at `ch-18.md:257-267` and looks correct in isolation, but smolagents 1.26.0 never calls it (zero hits for `log_steps` across `site-packages/smolagents/`). The framework's official per-step hook is `step_callbacks: list[Callable] | dict[Type[MemoryStep], ...]` (smolagents `agents.py:282, 304, 416-434, 623`), which `JsonlLogger` does not register. Practical consequence: the `log()` override at `:247-255` writes one JSONL record per `log()` call (an improvement over the original), but `self.current_step` is never incremented, so every record's `step` reads `0`, and records are not aligned to step boundaries. The chapter's claim at `:273` that "the framework calls `log_steps()` once per step" is FALSE; the cited source does not back the claim. Fix should have used `step_callbacks=[JsonlLogger.on_step]` in `CodeAgent.__init__` (or wired `current_step` to the step-callback registry).

### HIGH

(none new beyond CRITICAL #2)

### MEDIUM

(none)

## Cross-cutting findings

- **Code-quality regression in cli.py**: the closing of `cli.py`'s `JsonlLogger` is also missing — the logger's `close()` method is never called, so on Windows the JSONL file handle stays open until interpreter exit. With the broken `build_agent(logger=logger)` call already failing first, this is a secondary defect, but it would surface if the CLI were fixed.
- **No test exercises the CLI.** Smoke tests cover validators and `build_agent` import; gold tests build `CodeAgent` directly with a stub model; live tests use `build_agent(model_name=backend)`. None of them invoke `cli.main()`. If they did, the regression would have been caught.
- **Project surface (CRITICAL #3) is fixed in shape but broken in function.** The four required files are present and individually well-formed (CLI parses; `pyproject.toml` is valid TOML; README documents the run command), but they don't fit together. This is a common failure mode when a reviewer focuses on per-file shape rather than per-flow wiring.

## Out-of-scope observations

- `bible.md` still has 16 `## Added by ch-XX` blocks (ch-01..ch-16) — pre-existing, master's lane. The 17th block (for ch-17 or ch-18) is not the writer's job.
- `research-log.md` and the ch-17 chapter still carry the legacy "entry-167..entry-178" labels; ch-18 is correctly mapped to those entries in the chapter self-critique.

## Honest assessment

The writer did honest, well-cited work on 9 of the 11 fixes — install guidance, rate_limit units, the four-file project surface, the briefing contract, the closing-imperative order, live-test gating, model-factory resolution, two beginner-error corrections, and three acronym expansions. Each is verifiable against installed source and runs through pytest.

Two fixes are not honestly delivered. **Fix #5** is partial: the writer invented `log_steps()` without checking that the framework calls it, and the chapter claims a citation to `agents.py` that doesn't back the claim. **Fix #3** is worse — the CLI is broken. The writer added the right shapes but mismatched the interface between `cli.py` and `build_agent`, so `python -m research_briefing.cli "..."` raises `TypeError`. This is the exact outcome the dev FAIL flagged as missing ("a runnable command"), and the fix did not actually deliver it. The smoke + gold 13/13 result is real and reproducible, but it does not exercise the CLI, so it does not catch this regression.

Is the project walkthrough NOW COMPLETE? **No.** A beginner who follows the README will reach `python -m research_briefing.cli "solar panels in Spain"` and see `TypeError: build_agent() got an unexpected keyword argument 'logger'`. They will be more stuck than before the fix, because the README now confidently tells them to run a command that does not work. After `pip install ddgs wikipedia-api`, they still cannot run the project.

Are any original issues still partially present? Yes — CRITICAL #2 is genuinely fixed, CRITICAL #4 (briefing contract) is genuinely fixed in both prompt and validators, CRITICAL #6 (closing-imperative order) is genuinely fixed, but CRITICAL #1 (install guidance) and CRITICAL #3 (runnable project) have only been half-fixed: dependencies are listed, but the CLI that uses them does not run.

Any NEW issues introduced by the fixes? Yes — the CLI regression above, and the JSONL per-step dead-code claim. The bigger word count and new code blocks do not introduce structural issues.

## Self-critique

- **Did I do my job?** yes; I read the chapter line-by-line, extracted all 10 Python blocks + the pyproject.toml into a fresh temp project, ran pytest smoke/gold (13/13) and live (4/4 SKIPPED), invoked the CLI to discover the regression, and grep'd the installed smolagents 1.26.0 source for `log_steps` and step-callback support.
- **What might I have missed?** I did not install missing deps into the venv (review is report-only), so I could not exercise the `ddgs` and `wikipedia-api` tool construction paths. I did not run the gold tests against a real `Model` subclass beyond what smoke/gold already cover (smolagents' own gold test asserts on the canned `CodeAgent` path, which I did exercise). I did not delete `bible.md`'s missing ch-17/ch-18 blocks because that is master's lane.
- **What did I assume without evidence?** I assume the writer ran their reported 13/13 and 4/4-skip themselves; I independently reproduced both numbers. I did not assume `step_callbacks` is the only correct hook — but it is the framework-provided one, and `log_steps()` is not called by anything.
