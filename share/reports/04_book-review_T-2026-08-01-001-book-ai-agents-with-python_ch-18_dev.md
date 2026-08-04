# Book Developmental Review — T-2026-08-01-001-book-ai-agents-with-python / ch-18

**Date:** 2026-08-03
**Sub-agent:** am-review
**Pass:** developmental

## Summary

- **Overall verdict:** FAIL
- **Chapter reviewed:** ch-18 — *Project: Research and Briefing Agent*
- **Issue counts:** 6 CRITICAL / 3 HIGH / 2 MEDIUM / 0 LOW
- **Block progression?** yes
- **One-line summary:** The offline smoke/gold tests are genuinely reproducible, but the reader-facing project is not runnable: required tool dependencies and the CLI/package surface are missing, the configured “2-second” search limit is actually 0.5 seconds, and several core outcome guarantees are not implemented.

## Outcome verification

Required outcome:

> by the end of the reading, the reader has a runnable `src/research_briefing/` project that takes a topic string and returns a 200-400 word briefing with 3-5 cited source URLs, gated by `max_steps=15`, two `final_answer_checks` (max length, must contain `Sources:`), a 2.0-second web-tool rate limit, and a 10000-character page-fetch cap; the test suite has three layers (smoke, gold, live) and a per-run JSONL trace.

**Result: FAIL.** The closing callout preserves the requested numerical/content targets at `books/ai-agents-with-python/chapters/ch-18.md:374`, but the implementation does not deliver a runnable command, a 2.0-second request interval, the production dependencies, reliable 200–400-word/3–5-URL enforcement, or a per-step/per-run trace.

## Tests / build run

- `E:\book_gen\.venv\Scripts\python.exe -c "from smolagents import DuckDuckGoSearchTool; print('ok')"` — **exit 0**, printed `ok`. Importing the class succeeds because `ddgs` is loaded lazily in the constructor.
- `DuckDuckGoSearchTool()` instantiation — **exit 1**: `ModuleNotFoundError: No module named 'ddgs'`, re-raised as `ImportError: You must install package ddgs`. Installed source confirms `from ddgs import DDGS` at `E:\book_gen\.venv\Lib\site-packages\smolagents\default_tools.py:133`.
- Dependency probe — `ddgs_spec=None`; `duckduckgo_search` is installed. Installed versions are `smolagents==1.26.0`, `pytest==9.1.1`, and `duckduckgo-search==8.1.1`, matching `books/ai-agents-with-python/environment.md:27,33-35`.
- `WikipediaSearchTool()` instantiation — **exit 1**: `ModuleNotFoundError: No module named 'wikipediaapi'`, re-raised with guidance to install `wikipedia-api`; the lazy import is at `E:\book_gen\.venv\Lib\site-packages\smolagents\default_tools.py:596`.
- Extracted all eight Python fences and ran `ast.parse` with the pinned venv — **8/8 PASS**.
- Extracted the eight project/test fences into a disposable temporary `src/` project, set `PYTHONPATH=src`, and ran `pytest tests/test_smoke.py tests/test_gold.py -v` — **exit 0, 10 passed in 0.71s**.
- In the same fresh temporary project, with `OPENAI_API_KEY` and `HF_TOKEN` empty, ran `pytest tests/test_live.py -v` — **exit 0, 2 skipped in 0.58s**, with the `live` marker registered.
- UTF-8 encode/decode round-trip — **PASS**.
- Structural metrics over visible prose — orientation 48 words; longest paragraph 76 words; 12 H2s, each 3–6 words and verb-led.

## Per-task verdicts

### ch-18 — Project: Research and Briefing Agent

- **Verdict:** FAIL
- **Spec match:** The prose covers the planned topics and the offline tests run, but the copy-pasted project cannot execute its documented production path.
- **Correctness:** Multiple runtime and API-semantics defects block the outcome.
- **Style:** Voice, blacklist, heading, paragraph-length, and UTF-8 gates pass; closing order and acronym gates fail.
- **Tests:** Eight code blocks parse; smoke/gold are 10/10 green; live skips without keys. These tests avoid the broken production tool path and therefore do not establish that the project is runnable.
- **Evidence:** `books/ai-agents-with-python/chapters/ch-18.md:3-17,29-55,69-117,121-176,178-216,218-350,352-376`; installed 1.26.0 source cited below.

## Required checklist

| # | Check | Verdict | Evidence |
|---|---|---|---|
| 1 | Outline coverage | PASS | Goal and acceptance tests `ch-18.md:5-11`; one `CodeAgent` and three tools `:13-19`; model factory `:21-27`; `src/` layout `:29-55`; four knobs `:121-168`; prompt injection `:170-176`; JSONL `:178-212`; three test layers `:214-350`; cost/latency `:352-356`; four errors `:358-366`; forward pointers `:368-376`. |
| 2 | Voice match | PASS | Conversational technical voice and direct address appear from `ch-18.md:3`; contractions occur at `:15,17,23,31,125`; no exclamation marks were found in visible prose. |
| 3 | Vocabulary blacklist | PASS | Fresh case-insensitive word-boundary scan of visible prose found zero hits for all ten forbidden terms. |
| 4 | Bible consistency / untouched | N/A | Current `bible.md` is 189 lines, but this workspace is not a Git repository and provides no edit history with which to prove that ch-18 did not touch it. Current block-count discrepancy is recorded under issue H3. |
| 5 | Research grounding | FAIL | Relevant claims cite installed 1.26.0 generally at `ch-18.md:15,25,125`, but the rate-limit interpretation is contradicted by installed source, and `VisitWebpageTool` behavior is misstated at `:362`. |
| 6 | Project structure | FAIL | The five requested modules and three test files are shown at `ch-18.md:35-53`, and the logger subclasses `AgentLogger` at `:188-210`; however, the promised `cli.py` is mentioned but omitted (`:33` versus `:35-42`), no runnable project script/main guard is supplied, and no complete package metadata/install surface is supplied. |
| 7 | Code-block correctness | FAIL | All eight Python fences parse and pytest fences execute, but production tool construction fails without `ddgs` and `wikipedia-api`; no reader-facing install guidance exists; rate-limit semantics are wrong. |
| 8 | Beginner accessibility | PASS | Orientation is 48 words; all H2s are verb-led and ≤7 words; longest visible prose paragraph is 76 words. |
| 9 | Closing-imperative contract | FAIL | `> **The move:**` is at `ch-18.md:374`, but `What's next` at `:376` is visible substantive prose after it. The callout is therefore not the final visible substantive paragraph before the HTML comment at `:378`. |
| 10 | Forward-pointer hygiene | PASS | `ch-18.md:368-376` explicitly names ch-19, *Project: Multi-Agent Work Assistant*, a `Critic` managed agent, revision behavior, and per-role backend selection. |
| 11 | `HfApiModel` mention rule | PASS | Fresh scan found zero occurrences in the visible ch-18 body. |
| 12 | `final_answer` discipline | PASS | Fresh prose scan found no bare `final_answer`; `final_answer_checks` is used as allowed. The test code constructs the terminator token at runtime at `ch-18.md:282-284`. |
| 13 | UTF-8 clean | PASS | Fresh UTF-8 round-trip completed with zero errors. |
| 14 | No-regression / edit provenance | N/A | No VCS or operation log exists to prove `Edit` rather than `Write`, or to compare earlier ledger rows byte-for-byte. Current `bible.md` has 189 lines but only 16 `## Added by ch-XX` headings (ch-01 through ch-16), not the required 17. |
| 15 | Acronyms | FAIL | JSONL is expanded at `ch-18.md:3`; CLI first appears unexpanded at `:119`, API first appears unexpanded at `:313`, and pytest first appears without a plain-language expansion at `:55`. |
| 16 | Test executability | PASS | Fresh extracted run: smoke + gold **10 passed**; live **2 skipped** without keys. See commands above. |

## Issues

### CRITICAL

1. **Production web tools cannot be constructed, and the chapter omits the required install guidance.** `build_web_tools()` immediately constructs `DuckDuckGoSearchTool` and `WikipediaSearchTool` at `ch-18.md:159-165`; the venv has neither `ddgs` nor `wikipedia-api`. The requested import-only command prints `ok`, but constructor execution fails because 1.26.0 imports `DDGS` lazily at `default_tools.py:133`. A full-file scan found no `pip install`, `ddgs`, or `duckduckgo-search` guidance. This directly blocks `build_agent()` at `ch-18.md:106` and the documented run at `:3`.

2. **`rate_limit=2.0` does not create a 2.0-second delay.** The chapter claims a 2.0-second pace at `ch-18.md:125,162,374`, but installed 1.26.0 computes `_min_interval = 1.0 / rate_limit` at `default_tools.py:130`; `2.0` permits two queries per second, a 0.5-second minimum interval. The configured value violates the outcome.

3. **The promised runnable project/CLI is absent.** The chapter says `cli.py` makes `python -m research_briefing.cli "..."` work at `ch-18.md:3,33,119`, but the package tree omits `cli.py` at `:35-42`, and no CLI code block, `__main__.py`, complete `pyproject.toml`, README, dependency list, or main guard is supplied. A beginner copying every block cannot run the opening command.

4. **The implementation does not enforce or test the core briefing contract.** The agent receives only `agent.run(topic)` (`ch-18.md:119`) with no instructions requiring 200–400 words, 3–5 URLs, source-per-claim citations, or non-fabricated URLs. The length validator permits anything up to 800 words (`:132-145`), and the source validator accepts any string containing `Sources:`. Smoke/gold tests at `:218-309` check validator mechanics and canned keywords, not the three acceptance tests stated at `:7-11`.

5. **The JSONL logger is not a per-step, per-run trace implementation.** `JsonlLogger.log()` writes one record per logger call at `ch-18.md:191-210`, not one record per agent step; smolagents calls several logging methods throughout a run (`agents.py:482,584,740,1314,1386,1402,1579,1684,1743-1762`). Records omit the promised step number and level, and no supplied CLI generates a unique run path or closes the logger. The claims at `ch-18.md:180,212,374` are not delivered.

6. **The closing imperative is not final.** The hard contract requires the callout to be the final visible substantive paragraph. `ch-18.md:376` places a `What's next` paragraph after the callout at `:374` and before the HTML comment at `:378`.

### HIGH

1. **The live-test key gate and selected backend disagree.** `ch-18.md:331-340` allows the test to run when either `OPENAI_API_KEY` or `HF_TOKEN` exists, but always calls `build_agent(model_name="openai")`. An HF-token-only reader does not skip and then attempts the OpenAI path.

2. **The model-factory prose and code disagree, and the defaults are non-runnable placeholders.** Prose says the factory reads which key is set at `ch-18.md:23-27`; code instead defaults to `model_name="openai"` and requires a caller-selected string at `:83-104`. Defaults `small-openai-model` and `small-huggingface-model` at `:97-98` are placeholders rather than usable pinned/directional configuration, so an otherwise configured reader reaches a provider with an invalid model identifier.

3. **The required 17-block bible snapshot is not present.** Current `books/ai-agents-with-python/bible.md` is exactly 189 lines, but its headings run only from ch-01 at `bible.md:1` through ch-16 at `:181`: 16 blocks, not 17. There is no VCS history to attribute this discrepancy to ch-18, so treat it as a blocking project-state discrepancy rather than a proven writer regression.

### MEDIUM

1. **Two beginner-error explanations are factually wrong.** Declaring a transitive dependency directly is redundant but does not inherently “create a version conflict” (`ch-18.md:360`). Installed `VisitWebpageTool.forward` converts HTML to Markdown (`default_tools.py:531`), contradicting “returns plain text” at `ch-18.md:362`.

2. **Three required acronym introductions are missing.** JSONL is expanded correctly at `ch-18.md:3`; CLI at `:119`, API at `:313`, and pytest at `:55` are not expanded on first prose use.

## Cross-cutting findings

- The test suite is real but strategically avoids production wiring: smoke imports `build_agent` without calling it (`ch-18.md:228-232`), while gold uses `tools=[]` (`:287-295`). Ten green tests therefore coexist with a production constructor that fails.
- The chapter repeatedly describes a full project while supplying selected modules only. Missing packaging, dependency, command-line, prompt-contract, and run-path pieces compound one another; adding one package alone will not make the walkthrough complete.
- Source-grounding language is present, but the review found several places where the installed 1.26.0 source contradicts the manuscript. The installed source, not the chapter’s self-critique, must remain canonical.

## Out-of-scope observations

- The research log labels the entry-167..178 section as ch-17 and points forward to old chapter numbers at `research-log.md:1115-1186`; the current outline and dispatch treat it as ch-18. This appears to be pre-existing renumbering drift.
- The style guide’s ch-18 command uses `python -m research_briefing --topic "..."` at `style-guide.md:84`, while the chapter promises `python -m research_briefing.cli "..."` at `ch-18.md:3`. The fix loop should choose one canonical interface.

## Honest assessment

The writer correctly identified the `ddgs` problem in the handoff/ledger context, but did not document the workaround in reader-visible chapter prose; `duckduckgo-search==8.1.1` does not satisfy smolagents 1.26.0’s `from ddgs import DDGS`, and `wikipedia-api` is also missing. The reported 10/10 pytest result is credible and independently reproducible, although no execution provenance can prove when the writer ran it. Subtle factual errors remain in the rate-limit units, webpage output format, model-factory description, live-test backend choice, and logger semantics. The walkthrough is not complete: a beginner cannot copy-paste it into a runnable research-and-briefing project.

## Self-critique

- **Did I do my job?** yes; I read the chapter, style guide, research entries, outline, ledger, bible, environment, installed 1.26.0 source, and ran fresh syntax/runtime/test checks.
- **What might I have missed?** I did not call external provider APIs because no keys are configured, and I did not install missing dependencies because review is report-only.
- **What did I assume without evidence?** I cannot prove whether `bible.md` or `ledger.md` was edited with Edit versus Write, whether earlier rows changed historically, or whether the writer personally ran the earlier temp suite; this workspace has no Git history or operation log.
