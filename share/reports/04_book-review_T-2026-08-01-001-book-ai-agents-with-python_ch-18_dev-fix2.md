# Book Developmental Re-review — T-2026-08-01-001-book-ai-agents-with-python / ch-18 / dev-fix2

**Date:** 2026-08-03
**Sub-agent:** am-review
**Loop:** developmental fix-loop 2
**Scope:** Re-review of the 3 surgical fixes remaining after dev-fix1

## Summary

- **Overall verdict:** PASS
- **Fixes reviewed:** 3
- **Pass / Warn / Fail:** 3 / 0 / 0
- **Open issue counts:** 0 CRITICAL / 0 HIGH / 0 MEDIUM / 0 LOW
- **Block line-edit?** no
- **One-line summary:** The CLI now accepts and forwards the logger correctly, the supported `step_callbacks` path emits a real `step >= 1` JSONL record during a stub-model run, and the exact no-key CLI path reaches the expected OpenAI missing-credentials error instead of `TypeError`; all requested no-regression gates pass.

## Tests / build run

All executable checks used a disposable project extracted from the chapter's fenced blocks; the disposable tree was removed at command completion.

- `E:\book_gen\.venv\Scripts\python.exe -B -m research_briefing.cli "solar panels Spain"` with `OPENAI_API_KEY` and `HF_TOKEN` unset — **exit 1 as expected**; final exception was `openai.OpenAIError: Missing credentials...`; `TypeError` was absent.
- `E:\book_gen\.venv\Scripts\python.exe -B -m research_briefing.cli --help` — **exit 0**; argparse usage text was present.
- Runtime `build_agent(logger=logger)` wiring probe with only the provider/tool constructors replaced by inert fakes — **exit 0**; captured constructor state was `logger_identity=true`, `callback_count=1`, `callback_self=true`, `callback_name="on_step"`, `max_steps=15`.
- One stub-model `CodeAgent.run()` using the chapter's `JsonlLogger` and callback wiring — **exit 0**; answer `stub result`; JSONL contained 8 total logger/event records and exactly 1 dedicated per-step record: `{"step": 1, "type": "ActionStep", ...}`. This proves the step count is no longer stuck at zero.
- `E:\book_gen\.venv\Scripts\python.exe -B -m pytest tests/test_smoke.py tests/test_gold.py -v -p no:cacheprovider` — **exit 0; 13 passed in 0.95s**.
- `E:\book_gen\.venv\Scripts\python.exe -B -m pytest tests/test_live.py -v -p no:cacheprovider` with both provider keys unset — **exit 0; 4 skipped in 0.54s**.
- `ast.parse` over the extracted Python fences — **10/10 PASS**.
- UTF-8 encode/decode round-trip — **PASS**; current chapter SHA-256 `d0c72f5cce06428bd6d126f657a34ea32bf05cb71a060603d17f52e3fd5b59b2`.
- Prose word count after stripping fenced blocks, the HTML handoff comment, inline-code spans, and Markdown markers — **2,229 words**, a +1 delta from the 2,228 ledger baseline and within the required 1,616–2,461 band.
- Visible-prose scan — **0** `HfApiModel`; **0** bare `final_answer`; **0** hits for all blacklist entries in `style-guide.md:186-193`.
- `bible.md` invariant — **189 lines**, SHA-256 `db2a516b708a27bf6d0a5595e0c24f23282a9f830db34f08c6650df84c0b4ecb`; mtime remains `2026-08-03 09:12:51 +03:00`, matching the timestamp recorded by dev-fix1.

## Per-task verdicts

### Fix 1 — [CRITICAL] `cli.py` → `build_agent` wiring

- **Verdict:** PASS
- **Spec match:** `build_agent` is now keyword-only and accepts both `model_name` and `logger` at `books/ai-agents-with-python/chapters/ch-18.md:119-123`. It derives the callback from that logger at `:135-136` and forwards both `logger=logger` and `step_callbacks=step_callbacks` into `CodeAgent` at `:138-146`.
- **Correctness:** The CLI creates `JsonlLogger` and calls `build_agent(logger=logger)` at `books/ai-agents-with-python/chapters/ch-18.md:307-314`. A runtime constructor-capture probe confirmed the identical logger object and its bound `on_step` callback reach `CodeAgent`.
- **Tests:** The exact no-key CLI command reaches `openai.OpenAIError: Missing credentials` and contains no `TypeError`.
- **Evidence:** `books/ai-agents-with-python/chapters/ch-18.md:119-147,307-319`; installed `smolagents/agents.py:294-312` confirms `CodeAgent`/`MultiStepAgent` accepts both `step_callbacks` and `logger`.
- **Issues:** none.
- **Suggested fix:** no fix needed.

### Fix 2 — [CRITICAL] JSONL per-step records through `step_callbacks`

- **Verdict:** PASS
- **Spec match:** The dead `log_steps` method is gone. `JsonlLogger.on_step(step)` increments `current_step` and writes a typed/timed JSON record at `books/ai-agents-with-python/chapters/ch-18.md:271-282`; the explanatory prose accurately describes registration through `step_callbacks=[logger.on_step]` at `:288-292`.
- **Correctness:** Installed smolagents 1.26.0 documents and accepts callbacks at `agents.py:282,304`; list callbacks are registered for `ActionStep` at `agents.py:416-434`; finalized steps invoke the callback registry at `agents.py:620-623`. `CallbackRegistry.callback` preserves one-argument callback compatibility at `memory.py:300-316`, so the bound `on_step(self, step)` signature is valid.
- **Tests:** One stub-model `agent.run()` generated one `ActionStep` callback record with `step=1`; ordinary logger events were also present, as designed. The mechanism therefore produces one dedicated record per action step rather than zero step-numbered records.
- **Evidence:** `books/ai-agents-with-python/chapters/ch-18.md:223-292`; `E:/book_gen/.venv/Lib/site-packages/smolagents/agents.py:282,304,416-434,620-623`; `E:/book_gen/.venv/Lib/site-packages/smolagents/memory.py:300-316`.
- **Issues:** none.
- **Suggested fix:** no fix needed.

### Fix 3 — [HIGH] CLI end-to-end behavior

- **Verdict:** PASS
- **Spec match:** `cli.main()` defines the positional topic and `--log-dir`, creates the logger, builds the agent with that logger, and runs the topic at `books/ai-agents-with-python/chapters/ch-18.md:307-319`.
- **Correctness:** `--help` exits 0. With no API keys, execution advances through the repaired CLI/factory interface and stops at the expected provider trust boundary with `openai.OpenAIError: Missing credentials`; the prior invalid-kwarg failure is gone.
- **Tests:** Both CLI commands were run fresh from the extracted chapter project. Smoke/gold remain 13/13 green and live remains 4/4 cleanly skipped.
- **Evidence:** `books/ai-agents-with-python/chapters/ch-18.md:294-334,384-392,400-547`.
- **Issues:** none.
- **Suggested fix:** no fix needed.

## No-regression checks

| Check | Verdict | Evidence |
|---|---|---|
| Word-count delta | PASS | 2,229 under the established prose-with-inline-code-stripped methodology; +1 from 2,228 and inside 1,616–2,461. |
| UTF-8 round-trip | PASS | Byte decode/encode round-trip clean. |
| Python syntax | PASS | 10/10 fenced Python blocks pass `ast.parse`. |
| Smoke + gold tests | PASS | 13/13 passed. |
| Live-test no-key behavior | PASS | 4/4 skipped, exit 0. |
| `HfApiModel` discipline | PASS | Zero visible-prose matches. |
| Bare `final_answer` discipline | PASS | Zero visible-prose matches; `final_answer_checks` remains allowed. |
| Vocabulary blacklist | PASS | Zero matches for `optimal`, `proven`, `studies show`, `magic`/`magical`, `just`, `simply`, `obviously`, `revolutionary`, `game-changing`, and `powerful`. |
| `bible.md` invariant | PASS | 189 lines; prior-review mtime unchanged. |

## Cross-cutting findings

- Static code, installed-framework source, and runtime behavior now agree. The previous failures came from interface mismatch and an invented callback name; both are replaced by the framework-supported API.
- The JSONL file contains ordinary logger-event records in addition to the dedicated callback record. That does not weaken the per-step guarantee: the stub run produced exactly one typed step record for its one `ActionStep`.
- No new issue was introduced by the three surgical changes.

## Out-of-scope observations

- A live provider success path was not run because no API keys were available. This is expected; the requested missing-credentials path and all offline tests were verified.
- This workspace has no Git history or prior bible hash to prove byte-for-byte non-edit provenance. The current 189-line count and file mtime match the baselines recorded in earlier review material.

## Honest assessment

The writer correctly fixed the `cli.py` → `build_agent` wiring: the factory's keyword-only signature accepts `logger`, and runtime capture proves that the same logger and its bound `on_step` callback reach `CodeAgent`. The per-step JSONL mechanism is now correct for the requested behavior: a one-step stub-model run produced one `ActionStep` record with `step=1`, not a file whose step values remain zero. I found no new issue introduced by these changes. Chapter 18 is ready for line-edit.

## Self-critique

- **Did I do my job?** yes; I read the current chapter and prior dev-fix1 report, checked the installed callback implementation, ran the exact CLI help/no-key paths, captured `build_agent` constructor wiring at runtime, ran a real stub-model callback cycle, and reran every requested no-regression check.
- **What might I have missed?** I did not call OpenAI or Hugging Face with real credentials, and the requested one-step probe does not exercise a long multi-step run. The callback registry and increment logic are nevertheless directly verified for the first action step.
- **What did I assume without evidence?** I treated the established 2,228 ledger count as the pre-fix baseline. I cannot prove `bible.md` byte identity against an earlier snapshot because no prior hash or VCS history exists; I verified its 189-line count and unchanged recorded mtime instead.
