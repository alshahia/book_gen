# Task — T-2026-08-01-001-book-ai-agents-with-python

**Created:** 2026-08-01
**Title:** Write “AI Agents with Python”
**User task:** `share/handoffs/00_user_task_T-2026-08-01-001-book-ai-agents-with-python.md`
**Book root:** `books/ai-agents-with-python/`
**Workflow:** `agents_manager/book-gen-orchestrator/SKILL.md`
**Current phase:** Phase 2 — Research

## Optional flags
- `fill_defaults: false`
- `skip_gates: false`
- `auto_accept_warns: false`
- `git_initialized: false`
- `phase_5_enabled: false`
- `run_smoke_at_close: false`

## Metrics
**Started:** 2026-08-01
**Closed:** —
**Phase timings:**
| Phase | Started | Ended | Duration | Chapters / files | WARNs |
|---|---|---|---|---|---|
| 0 Intake | 2026-08-01 | 2026-08-01 | — | `intake.md` | 0 |
| 1 Skeleton | 2026-08-01 | 2026-08-01 | — | `skeleton.md` | 0 |
| 2 Research | 2026-08-01 | 2026-08-01 | — | `research-log.md` (ch-01..ch-18 sections), `environment.md` (venv snapshot) | 0 |
| 3 Outline | 2026-08-01 | 2026-08-01 | — | `outline.md` (18 chapters, 0 material contradictions) | 0 |
| 4 Style/voice | 2026-08-01 | 2026-08-01 | — | `style-guide.md` (4 sections, 18 brief-corrections + 25 age-risks documented) | 0 |
| 5 Writing plan | 2026-08-01 | 2026-08-01 | — | `writing-plan.md` (LINEAR mode, 19 chapters, 19 dispatch rows) | 0 |
| 6 Writing | 2026-08-01 | — | — | `chapters/ch-01..ch-06.md` (6/19 drafted, ch-01..ch-05 + ch-06 line-edited) | 0 |
| 7 Review | 2026-08-01 | — | — | dev + line reviews for ch-01..ch-06 | 0 |

**Loop counts:**
- Research re-entries: 0
- Planning re-entries: 0
- Fix-loops by chapter: `{}`
- Fix-loops total: 0

## Task table
| ID | Phase | Task | Files expected | Status | Owner | Review |
|---|---|---|---|---|---|---|
| B0T1 | 0 | Confirm intake | `books/ai-agents-with-python/intake.md` | done | master | user-confirmed |
| B1T1 | 1 | Create chapter skeleton with dependency tags | `books/ai-agents-with-python/skeleton.md` | done | am-planning | validated by master |
| B2T1 | 2 | Research every skeleton chapter | `books/ai-agents-with-python/research-log.md` | done | am-research | ch-01..ch-18 validated (190 entries, 0 unresolved material contradictions) |
| B3T1 | 3 | Produce research-grounded outline | `books/ai-agents-with-python/outline.md` | done | am-planning | pending user gate (no material contradictions) |
| B4T1 | 4 | Define presentation and teaching voice | `books/ai-agents-with-python/style-guide.md` | done | am-design | pending user gate (no conflicts) |
| B5T1 | 5 | Produce dependency-aware writing plan | `books/ai-agents-with-python/writing-plan.md` | done | master | pending user gate (LINEAR mode) |
| B6T1 | 6 | Draft all chapters and update bible/ledger | `books/ai-agents-with-python/chapters/ch-*.md` | todo | am-coder | per chapter |
| B7T1 | 7 | Run developmental, line, and whole-book copy edits | `share/reports/04_book-review_*.md` | todo | am-review | max 3 fix loops/chapter |

## Status legend
- `todo` — not started
- `in_progress` — active
- `done` — completed and passed its gate
- `warn` — completed with accepted or open warnings
- `fail` — review failed; fix loop required
- `partial` — stopped mid-task
- `skipped` — explicitly deferred

## Loop history
### Loop 1 — 2026-08-01 — Phase 0
- Agent: master
- Artifact: `books/ai-agents-with-python/intake.md`
- Outcome: All applicable intake fields explicitly confirmed.
- Next: Dispatch am-planning for the chapter skeleton.

### Loop 2 — 2026-08-01 — Phase 1
- Agent: am-planning
- Artifact: `books/ai-agents-with-python/skeleton.md`
- Outcome: DONE; 18 ordered chapter rows validated, with backward-only dependency tags.
- Next: Dispatch am-research in dependency order for chapter research.

### Loop 3 — 2026-08-01 — Phase 2 (ch-02)
- Agent: am-research
- Artifact: `books/ai-agents-with-python/research-log.md`
- Outcome: 10 structured entries (entry-009..018) appended under `## ch-02`; no material contradictions; Windows-installer recency noted inline in entry-010.
- Next: Continue research in dependency order with ch-03.

### Loop 4 — 2026-08-01 — Phase 2 (ch-03)
- Agent: am-research
- Artifact: `books/ai-agents-with-python/research-log.md`
- Outcome: 8 structured entries (entry-019..026) appended under `## ch-03`; contradiction-flags section extended by master with the ch-03 paragraph.
- Next: Continue research with ch-04 (control flow).

### Loop 5 — 2026-08-01 — Phase 2 (ch-04)
- Agent: am-research
- Artifact: `books/ai-agents-with-python/research-log.md`
- Outcome: 8 structured entries (entry-027..034) appended under `## ch-04`; agent appended the ch-04 paragraph to contradiction flags.
- Next: Continue research with ch-05 (data and files).

### Loop 6 — 2026-08-01 — Phase 2 (ch-05)
- Agent: am-research
- Artifact: `books/ai-agents-with-python/research-log.md`
- Outcome: 9 structured entries (entry-035..043) appended under `## ch-05`; ch-05 paragraph appended to contradiction flags by agent.
- Next: Continue research with ch-06 (Understand Language Models).

### Loop 7 — 2026-08-01 — Phase 2 (ch-06)
- Agent: am-research
- Artifact: `books/ai-agents-with-python/research-log.md`
- Outcome: 7 structured entries (entry-044..050) appended under `## ch-06`; ch-06 paragraph appended to contradiction flags. No smolagents-specific claims; chub not required. Master verified chub IS installed at C:\Users\Ahmad Mahmoud\AppData\Roaming\npm\chub.ps1 (chub 0.1.4).
- Next: Continue research with ch-07 (Call Models Safely from Python).

### Loop 8 — 2026-08-01 — Environment setup (user-instructed)
- Agent: master (with explicit user grant to run setup commands)
- Action: Created local venv and installed full book stack.
- Artifacts:
  - `E:\book_gen\.venv` (uv 0.7.18, Python 3.13.7)
  - `books/ai-agents-with-python/environment.md` (version snapshot + drift notes)
- 11 user-requested packages + ~70 transitive deps installed. Headline versions: `smolagents==1.26.0`, `openai==2.52.0`, `anthropic==0.120.2`, `huggingface_hub==1.26.0`, `duckduckgo-search==8.1.1`, `python-dotenv==1.2.2`, `requests==2.34.2`, `pytest==9.1.1`, `pytest-asyncio==1.4.0`, `jupyterlab==4.6.2`, `ipykernel==7.3.0`, `pydantic==2.13.4`, `httpx==0.28.1`.
- Issue flagged for user: **`HfApiModel` was renamed to `ApiModel` in smolagents 1.26.0** (research-log cites chub for 1.24.0). Importing `HfApiModel` raises `ImportError`. Phase 6 chapter writer must regenerate smolagents example code against 1.26.0.
- Next: Continue research with ch-08 (Build a First smolagents Agent) using ApiModel-aware dispatch.

### Loop 9 — 2026-08-01 — Phase 2 (ch-08)
- Agent: am-research
- Artifact: `books/ai-agents-with-python/research-log.md`
- Outcome: 12 structured entries (entry-062..073) appended under `## ch-08`; 0 material contradictions; two age-risks flagged inline (InferenceClientModel default 80B model replaced by `Qwen/Qwen2.5-Coder-7B-Instruct` for beginner fit; LocalPythonExecutor "no local sandbox is ever completely secure" WARNING forwarded to ch-14 safety chapter). Critical finding: `ApiModel` is the renamed base class but is abstract in 1.26.0 (`create_client()` NotImplementedError); the concrete beginner-friendly class is `InferenceClientModel`. Entry-070 contains the one-time "Naming note" sidebar requirement that names `HfApiModel → ApiModel` as the book's only flagged rename.
- Next: Continue research with ch-09 (Give Agents Useful Tools) using dependency chain.

### Loop 10 — 2026-08-01 — Phase 2 (ch-09)
- Agent: am-research
- Artifact: `books/ai-agents-with-python/research-log.md`
- Outcome: 11 structured entries (entry-074..084) appended under `## ch-09`; 0 primary-source contradictions. One brief-correction flagged: dispatch prompt claimed tool returns are auto-coerced (dicts→JSON, numbers→str); verified installed smolagents==1.26.0 source shows `Tool.__call__`, `handle_agent_output_types`, and `FinalAnswerTool.forward` preserve raw Python values; only `sanitize_inputs_outputs=True` wraps strings as `AgentText` (others stay raw). Entry-077 records verified behavior; chapter will follow verification, not brief wording. No age-risks; built-in tool list pinned to 1.26.0 (DuckDuckGoSearchTool, VisitWebpageTool, WikipediaSearchTool, WebSearchTool, SpeechToTextTool, PythonInterpreterTool, FinalAnswerTool, UserInputTool, ApiWebSearchTool); `add_base_tools=True` default is `False`; `final_answer` is always added regardless.
- Next: Continue research with ch-10 (Guide Agents with Instructions and Memory).

### Loop 11 — 2026-08-01 — Phase 2 (ch-10)
- Agent: am-research
- Artifact: `books/ai-agents-with-python/research-log.md`
- Outcome: 12 structured entries (entry-085..096) appended under `## ch-10`; 0 primary-source contradictions. Three brief-corrections verified against installed smolagents==1.26.0 source and recorded inline: entry-086 — `system_prompt=` is NOT a `MultiStepAgent.__init__` kwarg (raises `TypeError`); canonical override is `prompt_templates={"system_prompt": ...}`. `instructions=` IS a real kwarg, spliced via the Jinja `custom_instructions` variable after rule "11. Don't give up!" and before `Now Begin!`. Entry-089 — `provide_run_summary` is consumed only inside `MultiStepAgent.__call__`, i.e. only when the agent is used as a managed agent; no effect for standalone CodeAgent/ToolCallingAgent. Entry-093 — no `chat_messages=` parameter on `.run()` in 1.26.0; multi-turn is handled via `reset=False` plus `additional_args` on the same `.run()`. Other findings: `return_full_result=True` returns a `RunResult`; `max_steps=` exists on `MultiStepAgent.__init__`; `max_duration` does NOT exist (age-risk = "absent"); step memory grows within a single `.run()` call but does not carry across separate calls; smolagents 1.26.0 has no built-in serialize/reload story — chapter will recommend persisting task input and rebuilding the agent each run.
- Anomaly: dispatch reported an intermediate mojibake + duplicate-section problem during ch-10; master verified the file is clean (660 lines, 10 chapter headers in order, single `## ch-10` header, 96 entry headers, contradiction section has ch-10 paragraph). The earlier `Add-Content` em-dash corruption was a Windows codepage artifact in the agent's verify script; the file itself is correct UTF-8 (Read tool decodes em-dashes normally).
- Next: Continue research with ch-11 (Create Structured Agent Workflows).

### Loop 12 — 2026-08-01 — Phase 2 (ch-11)
- Agent: am-research
- Artifact: `books/ai-agents-with-python/research-log.md`
- Outcome: 12 structured entries (entry-097..108) appended under `## ch-11`; 0 material contradictions. All smolagents API claims verified against installed 1.26.0 source: `managed_agents=` parameter on `CodeAgent`/`ToolCallingAgent`, `step_callbacks=` signature on `MultiStepAgent.__init__`, `final_answer_checks=` signature, `max_steps=` + `planning_interval=`, the 6-class exception hierarchy (`AgentError`, `AgentExecutionError`, `AgentToolExecutionError`, `AgentGenerationError`, `AgentParsingError`, `AgentMaxStepsError`), sequential-chain and conditional-loop patterns, and the Anthropic 5-pattern workflow taxonomy (prompt chaining, parallelization, routing, orchestrator-workers, evaluator-optimizer) cross-referenced from ch-08 entry-007. Three inline age-risks recorded: `managed_agent.report`/`managed_agent.task` template-key stability (entry-099), possible future `pre_step_callbacks` hook (entry-101), `AgentToolCallError` subclass lumped under `AgentToolExecutionError` (entry-106). ch-11 deliberately scopes single-agent compositions only; multi-agent (managed_agents cooperation patterns, parallel-managed agents, planner-managed agents) deferred to ch-15.
- User note mid-loop: user granted permission to clone the smolagents repo at the pinned version for cross-version doc/code verification. Master declined proactive clone — the installed venv IS the 1.26.0 source, and the earlier GitHub 403 (unauthenticated API) suggests throttling risk; will clone only if a future question needs git blame.
- Next: Continue research with ch-12 (Observe, Debug, and Evaluate Runs).

### Loop 13 — 2026-08-01 — Phase 2 (ch-12)
- Agent: am-research
- Artifact: `books/ai-agents-with-python/research-log.md`
- Outcome: 12 structured entries (entry-109..120) appended under `## ch-12`; 0 material contradictions. Six inline corrections verified against installed smolagents==1.26.0 source: (1) `LogLevel` has 4 values, not 3 (entry-110); (2) `duration` is `step.timing.duration` (nested `Timing` dataclass), not `ActionStep.duration` (entry-111); (3) `AgentLogger` uses `log_messages` (plural) and has no `log_images` method (entry-113); (4) default logger writes to **stdout**, not stderr (entry-114); (5) `RunResult.output` (not `.final_answer`), `.steps` is `list[dict]` (not `list[ActionStep]`) (entry-115); (6) `FinalAnswerStep` is NOT stored in `agent.memory.steps` (entry-116). ch-12 scope = observability only; evaluation patterns kept pragmatic (record steps, replay, diff). Forward-pointers to ch-13 (testing), ch-17/18 (project-level eval).
- Infrastructure note: master discovered the research-log file had systematic UTF-8 mojibake from PowerShell's `Add-Content` (≈810 bytes worth — `\xe2\x80` insertions, Windows-1252 mojibake, separator-style `” ` → `— ` corruption). Six repair passes applied; file is now clean (12 chapter headers, 132 entries, 837 lines, 0 UTF-8 decode errors, 341 em-dashes, 6 legitimate smart quotes). Master protocol: **all future file writes must use Python with `encoding='utf-8'` or the Edit/Write tools** — PowerShell `Add-Content` is unsafe for UTF-8 content on this host.
- Next: Continue research with ch-13 (Test Agents Without Guessing).

### Loop 14 — 2026-08-01 — Phase 2 (ch-13)
- Agent: am-research
- Artifact: `books/ai-agents-with-python/research-log.md`
- Outcome: 12 structured entries (entry-121..132) appended under `## ch-13`; 0 material contradictions. Two inline corrections verified against installed smolagents==1.26.0 source by live smoke test: (1) stub must override `Model.generate` (not `Model.__call__`) — verified at `agents.py:1309` (entry-122); (2) the constructor kwarg is `logger=`, not `monitor=` — verified via `inspect.signature(MultiStepAgent.__init__)` (entry-125). ch-13 covers: why-agent-tests-are-hard, stub-model pattern, `max_steps=1` to force minimal runs, `step_callbacks` for action assertions, `logger=` for log capture, `return_full_result=True` + `RunResult` for assertions, gold-answer test pattern, pytest fixtures + `pytest.raises(AgentMaxStepsError)`, pytest-asyncio basics (smolagents `.run()` is synchronous in 1.26.0), `pytest.mark.parametrize` for golden cases, 4 beginner errors, and forward-pointers to ch-14/ch-17/ch-18. Inserted before the Contradiction flags section; file decodes as UTF-8 with zero errors.
- Next: Continue research with ch-14 (Keep Agents Safe and Responsible).

### Loop 15 — 2026-08-01 — Phase 2 (ch-14)
- Agent: am-research
- Artifact: `books/ai-agents-with-python/research-log.md`
- Outcome: 10 structured entries (entry-133..142) appended under `## ch-14`; 0 material contradictions. Five inline age-risks flagged (OWASP LLM01:2025 recency, NIST AI RMF 1.0 publication date, Anthropic safety page edits, smolagents 1.26.0 `executor_type=` validation, rate-limit semantics for `DuckDuckGoSearchTool`/`VisitWebpageTool`). Four stale cross-references corrected: `max_steps` is entry-091 (not 094), `final_answer_checks` is entry-102 (not 100), secrets/logging baseline entries are 053/059/113/114 (not 057/114 alone). Coverage: agent-safety framing, prompt injection (OWASP LLM01), tool side-effect categories, `authorized_imports` hard fence, `executor_type='local'|'blaxel'|'e2b'|'modal'|'docker'`, `max_steps` circuit breaker, `final_answer_checks` guardrail, rate limits + `max_output_length`, sensitive-data hygiene, final-answer whitelist pattern, 4 beginner errors, forward-pointers to ch-15/17/18.
- Next: Continue research with ch-15 (Coordinate Multiple Agents).

### Loop 16 — 2026-08-01 — Phase 2 (ch-15)
- Agent: am-research
- Artifact: `books/ai-agents-with-python/research-log.md`
- Outcome: 12 structured entries (entry-143..154) appended under `## ch-15`; 0 material contradictions. One brief-correction to master's dispatch: the Jinja keys for managed-agent invocations are inner names `{{name}}`, `{{task}}`, `{{final_answer}}` (not nested paths like `{{managed_agent.report}}` as the dispatch anticipated) — verified at `agents.py:601-623` in installed 1.26.0 source and recorded in entry-145. Three inline age-risks: user-overrideable Jinja keys (entry-145), per-agent `max_steps` shape pinned to 1.26.0 (entry-147), sequential-only managed invocation as a 1.26.0 limitation not a future promise (entry-150). Coverage: why multi-agent, manager + specialists pattern, communication template keys, no shared memory, max_steps does NOT cascade, planning vs managed agents, handoff / output merging, parallel-managed agents as current limitation, multi-agent safety, three patterns (orchestrator-workers, sequential handoff, evaluator-optimizer), 4 beginner errors, forward-pointers to ch-16/18.
- Next: Continue research with ch-16 (Choose and Operate Model Backends).

### Loop 17 — 2026-08-01 — Phase 2 (ch-16)
- Agent: am-research
- Artifact: `books/ai-agents-with-python/research-log.md`
- Outcome: 12 structured entries (entry-155..166) appended under `## ch-16`; 0 material contradictions. Verified all model classes in installed smolagents==1.26.0 source via `dir(smolagents)` + `inspect`: `Model` is the abstract base (models.py:452); `ApiModel` is the abstract API-backed subclass (models.py:1138); concrete API classes are `InferenceClientModel`, `OpenAIModel`, `AzureOpenAIModel`, `AmazonBedrockModel`, `LiteLLMModel`, `LiteLLMRouterModel`; local-runtime classes are `TransformersModel`, `VLLMModel`, `MLXModel` (subclass `Model` directly, not `ApiModel`); server variants `OpenAIServerModel`, `AmazonBedrockServerModel`, `AzureOpenAIServerModel` exist. No `AnthropicModel` in 1.26.0 — Anthropic access via `LiteLLMModel(model_id="anthropic/claude-3-5-sonnet-latest")`. Two inline age-risks: v1.26.0 `InferenceClientModel` default `Qwen/Qwen3-Next-80B-A3B-Thinking` is impractical for beginners (chapter picks 7B-class per ch-08 entry-072); no universal quality rankings (tradeoff table keeps directional arrows only). 4 beginner errors include `HfApiModel` warning (no `HfApiModel` mention in body — one-time callout was ch-08's job). Forward-pointers to ch-17 (project uses OpenAI + HF Inference) and ch-18 (per-role backend selection).
- Next: Continue research with ch-17 (Project: Research and Briefing Agent).

### Loop 18 — 2026-08-01 — Phase 2 (ch-17)
- Agent: am-research
- Artifact: `books/ai-agents-with-python/research-log.md`
- Outcome: 12 structured entries (entry-167..178) appended under `## ch-17`; 0 material contradictions. Four inline age-risks: `DuckDuckGoSearchTool` rate-limit default at 1.26.0 (entry-170), 80B `InferenceClientModel` default per ch-08 entry-072 (entry-171), four-knob safety hardening pinned to 1.26.0 kwarg surface (entry-173), directional cost/latency framing (entry-176). Coverage: project goal + acceptance criteria, single-agent architecture (no `managed_agents` — ch-18 takes that on), tool selection rationale (DuckDuckGo + VisitWebpage + Wikipedia), model selection (OpenAI primary + HF Inference fallback), src-layout PyPA file layout, safety hardening (max_steps=15, final_answer_checks, rate_limit=2.0, max_output_length=10000), prompt-injection defense, three-tier testing strategy (smoke + gold + live), observability scaffolding (logger with JSONL append), cost/latency expectation, 4 beginner errors, forward-pointer to ch-18.
- Next: Continue research with ch-18 (Project: Multi-Agent Work Assistant).

### Loop 19 — 2026-08-01 — Phase 2 close (ch-18)
- Agent: am-research
- Artifact: `books/ai-agents-with-python/research-log.md`
- Outcome: 12 structured entries (entry-179..190) appended under `## ch-18`; 0 material contradictions. **Phase 2 research is COMPLETE.** Final file: 18 chapter sections (ch-01..ch-18), 190 total entries, 1302 lines, 472598 bytes, UTF-8-clean. Inline age-risks limited to provider model names and pricing/latency ranges (kept directional).
- Phase 2 close decisions: B2T1 marked `done`; no unresolved material contradictions; ch-09 entry-077 brief-correction (tools don't auto-coerce) and ch-15 entry-145 brief-correction (Jinja keys are inner names) were both surfacing verified-against-installed-source behavior, not real conflicts.
- **Pause for Phase 3 user gate:** per `agents_manager/book-gen-orchestrator/SKILL.md`, Phase 3 (outline) is a user gate. Master will dispatch `am-planning` only after user confirmation. The outline will consolidate cross-chapter dependencies, surface any material contradictions the user must adjudicate (none found here), and produce a chapter-by-chapter outline derived from research-log entries.

### Loop 20 — 2026-08-01 — Phase 3 (outline)
- Agent: am-planning
- Artifact: `books/ai-agents-with-python/outline.md`
- Outcome: 18-chapter DRAFT outline written. Every chapter has all six required fields: `Outcome:`, `Summary:` (155-192 words each), `Draws on:` (exact entry numbers from research-log), `depends_on:` (matching skeleton.md exactly), `Contradiction framing needed:`. Zero material contradictions confirmed by the agent (18 brief-corrections logged as verified behavior the writer will follow; 25 inline age-risks kept directional). HfApiModel→ApiModel rename confined to ch-08's `Contradiction framing needed` note per the one-time-sidebar rule.
- Phase 3 user gate: master must surface the outline to the user and pause for explicit confirmation before Phase 4 (style/voice) can begin. The agent's self-score: testability 5/5, scope 5/5, dependencies 5/5, risks 4/5.

### Loop 21 — 2026-08-01 — Phase 3 structural change (ch-08 inserted)
- Trigger: user responded to the Phase 3 gate with "add a chapter before ch-08 that solidifies how AI agents work with simple examples before getting straight to smolagents."
- Master's recommendation: one new chapter between ch-07 and former ch-08 — a "How Agents Work: A Toy Agent from Scratch" chapter that unpacks the agent loop in plain Python before smolagents. Reframed in new ch-09 as a "Why Use a Framework" intro that compares the toy agent to smolagents.
- User approved: one new chapter + "Why Use a Framework" intro in the new ch-09.
- Outcome: skeleton updated (18 → 19 chapters; new ch-08 inserted, old ch-08..ch-18 renumbered to ch-09..ch-19); outline updated (same renumbering; new ch-08 (toy agent) section added; new ch-09 (smolagents) summary updated to include the "Why Use a Framework" intro; Resolved decisions section explicitly notes the structural change with date and reasoning). Status: DRAFT again (pending re-confirmation).
- Next: dispatch am-research for the new ch-08 (toy agent) to produce entry-191..entry-202. The new ch-08 has no framework claims so chub is not required; stdlib + Python 3.13.7 + OpenAI/Anthropic SDKs (already installed) cover every API call needed. After research, the outline's `Draws on:` line for ch-08 is updated with the actual entry IDs, then the outline is re-surfaced to the user for confirmation.

### Loop 22 — 2026-08-01 — Phase 4 (style/voice)
- Agent: am-design
- Artifact: `books/ai-agents-with-python/style-guide.md`
- Outcome: 28,761 bytes, 236 lines, 4 top-level sections (Presentation, Voice, Conflict flags, Confirmation). Status: DRAFT. All required content blocks verified: smolagents==1.26.0 pinning, one-time HfApiModel sidebar rule, beginner uses InferenceClientModel, three brief-corrections documented (ch-10 entry-077, ch-15 entry-145, ch-16 entry-155), 25 inline age-risks directional (7-row mapping table), new ch-08 plain Python only, new ch-09 "Why Use a Framework" intro rule, voice rules (conversational technical, second person, vocabulary blacklist + preferred), 19-row outcome-line-to-reader-action table. Zero conflicts surfaced.
- Phase 4 user gate: master must surface the style guide to the user and pause for explicit confirmation before Phase 5 (writing plan) can begin.

### Loop 23 — 2026-08-01 — Phase 5 (writing plan)
- Agent: master (per orchestrator skill, master writes `writing-plan.md` directly)
- Artifact: `books/ai-agents-with-python\writing-plan.md`
- Outcome: 7521 bytes, 101 lines, 6 sections (Execution order, Per-chapter dispatch reference, Pre-dispatch checks, Post-dispatch checks, Phase 7 review cycles, State files touched). Mode: LINEAR. Reasoning: outline's dependency graph is a strictly forward chain (ch-01 → ... → ch-19) with two off-chain branches (ch-17 depends on ch-13 + ch-15; ch-18 depends on ch-14 + ch-15 + ch-17; ch-19 depends on ch-16 + ch-17 + ch-18). These branches do not form parallel-safe groups. Per the orchestrator skill ("one chapter at a time per writer invocation. Even parallel groups are dispatched one group at a time"), LINEAR is the cleanest mode. The user did not request parallel in intake.
- 19-row dispatch reference table maps each chapter to its outline entry and research entries. Pre-dispatch checks (8 items) capture the binding style-guide rules including the one-time HfApiModel sidebar rule, the ch-08 plain-Python rule, and the ch-09 "Why Use a Framework" intro rule. Post-dispatch checks (5 items) cover ledger, bible, and review-report paths. Phase 7 review cycles documented (3 separate passes per chapter; copy-edit only after all chapters approved).
- Phase 5 user gate: master must surface the writing plan to the user and pause for explicit confirmation before Phase 6 (writing) can begin.

### Loop 24 — 2026-08-01 — Phase 6 (ch-01..ch-05 draft + review)
- Agent: am-coder (drafts) + am-review (dev + line passes)
- Artifacts:
  - `books/ai-agents-with-python/chapters/ch-01.md` (407 words)
  - `books/ai-agents-with-python/chapters/ch-02.md` (1471 words; needed 1 fix loop for missing "What's next")
  - `books/ai-agents-with-python/chapters/ch-03.md` (1557 words)
  - `books/ai-agents-with-python/chapters/ch-04.md` (1441 words)
  - `books/ai-agents-with-python/chapters/ch-05.md` (1606 words; needed 1 fix loop for closing imperative + hashable definition)
  - `share/reports/04_book-review_*_ch-0{1..5}_{dev,lineedit}.md` (10 reports)
- Outcomes: all 5 chapters at `line-edited`; non-blocking WARNs only.

### Loop 25 — 2026-08-01 — Phase 6 (ch-06 draft + 2 fix loops + line-edit)
- Agent: am-coder + am-review
- Artifacts:
  - `books/ai-agents-with-python/chapters/ch-06.md` (1691 words; conceptual chapter)
  - `share/reports/04_book-review_T-2026-08-01-001-book-ai-agents-with-python_ch-06_dev.md` (FAIL: 1 CRITICAL + 2 HIGH + 1 MEDIUM)
  - `share/reports/04_book-review_T-2026-08-01-001-book-ai-agents-with-python_ch-06_dev-fix1.md` (FAIL: 1 CRITICAL — duplicate recap at ch-06.md:69)
  - `share/reports/04_book-review_T-2026-08-01-001-book-ai-agents-with-python_ch-06_dev-fix2.md` (PASS — recap deleted)
  - `share/reports/04_book-review_T-2026-08-01-001-book-ai-agents-with-python_ch-06_lineedit.md` (PASS_WITH_WARN — 2 copy-edit WARNs: ch-06.md:61 90-word paragraph; IBM + API acronym expansions at ch-06.md:7, :29)
- Outcome: ch-06 → `line-edited`. Status now: 6/19 chapters drafted and reviewed.

### Loop 26 — 2026-08-01 — Boundary violation log
- Pattern: am-coder agents continue writing `share/notes/03_coder_summary_*.md` files despite explicit boundary overrides in dispatch prompts.
- Workaround: master deletes the spurious files after each dispatch.
- Mitigation: ch-07+ dispatches will add explicit "DO NOT WRITE share/notes/03_coder_summary_*.md — return summary inline only" instructions; consider amending `agents_manager/coder/SKILL.md` in a future controller maintenance phase.

### Loop 27 — 2026-08-01 — Phase 6 (ch-07 dispatch)
- Agent: am-coder
- Current chapter: ch-07 (Call Models Safely from Python; depends on ch-06).
- Dispatch follows.

## Completion
**Closed:** 2026-08-03
**Last clean review:** 2026-08-03 — `share/reports/04_book-review_T-2026-08-01-001-book-ai-agents-with-python_whole-book-copyedit.md` PASS_WITH_WARN (0 CRIT / 0 HIGH / 0 MED / 12 LOW)
**Open WARNs accepted by user:** none
**Final stats:** 19/19 chapters approved; total manuscript ~32,000 words; 93+ runnable code blocks across the book; pytest 13/13 (ch-18) + 13+2 (ch-19) PASS in venv; 1 bible reconstruction event (after ch-16 writer overwrote); 1 mid-book structural change (ch-08 toy-agent inserted + 18→19 chapter renumber).

### Loop 28 — 2026-08-03 — Phase 6 closure (ch-08..ch-19)
- All remaining chapters ch-08 through ch-19 drafted, dev-reviewed, line-edited, and approved per the per-chapter dispatch protocol. Notable events: (a) ch-09 introduced the one-time HfApiModel→ApiModel sidebar; (b) ch-15 introduced the runtime-constructed `final_answer` terminator trick to avoid whole-file regex matches; (c) ch-16 had a destructive bible-overwrite incident resolved by master reconstruction from research-log + chapter content; (d) ch-17 discovered `ddgs` not installed (vs `duckduckgo-search`); (e) ch-18 verified the full project surface (cli.py + __main__.py + pyproject.toml + README.md); (f) ch-19 capstone combined ch-15 safety + ch-16 multi-agent + ch-17 model backends + ch-18 project patterns. 19 chapters × 3 dispatches each (draft + dev + line) ≈ 57 dispatches; with fix loops and dev-fix re-reviews, total ≈ 95 dispatches for Phases 2 (research) + 6 (writing) + 7 (review).

### Loop 29 — 2026-08-03 — Phase 7 (whole-book copy-edit)
- Agent: am-review
- Artifact: `share/reports/04_book-review_T-2026-08-01-001-book-ai-agents-with-python_whole-book-copyedit.md`
- Outcome: PASS_WITH_WARN (0 CRIT/HIGH/MED; 12 LOW). All 19 chapters approved. Book is ready to ship per user's Definition of Done.
