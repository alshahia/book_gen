Phase 0 (intake) — T-2026-08-01-001-book-ai-agents-with-python — DONE (artifact: books/ai-agents-with-python/intake.md; all applicable fields user-confirmed; future questions batched)
Phase 1 (skeleton) — T-2026-08-01-001-book-ai-agents-with-python — DONE (artifact: books/ai-agents-with-python/skeleton.md; 18 chapters; dependencies validated)
Phase 2 (research ch-01) — T-2026-08-01-001-book-ai-agents-with-python — DONE (8 entries entry-001..008; no material contradictions)
Phase 2 (research ch-02) — T-2026-08-01-001-book-ai-agents-with-python — DONE (10 entries entry-009..018; no material contradictions; Windows installer age-risk recorded inline in entry-010)
Phase 2 (research ch-03) — T-2026-08-01-001-book-ai-agents-with-python — DONE (8 entries entry-019..026; no material contradictions)
Phase 2 (research ch-04) — T-2026-08-01-001-book-ai-agents-with-python — DONE (8 entries entry-027..034; no material contradictions)
Phase 2 (research ch-05) — T-2026-08-01-001-book-ai-agents-with-python — DONE (9 entries entry-035..043; no material contradictions; stdlib-only: list/tuple/set/dict + open()/with + csv + json)
Phase 2 (research ch-06) — T-2026-08-01-001-book-ai-agents-with-python — DONE (7 entries entry-044..050; no material contradictions; conceptual LLM chapter with no smolagents claims; chub install confirmed by master post-dispatch)
Phase 2 (research ch-07) — T-2026-08-01-001-book-ai-agents-with-python — DONE (10 entries entry-051..060; 18 chub citations; no material contradictions; stdlib + requests + python-dotenv + openai + anthropic + tenacity)
Environment — T-2026-08-01-001-book-ai-agents-with-python — DONE (venv E:\book_gen\.venv with Python 3.13.7 + 11 user-requested packages; full snapshot in books/ai-agents-with-python/environment.md)
Issue — smolagents 1.24.0 (cited in research) → 1.26.0 (installed): HfApiModel renamed to ApiModel. Documented in environment.md and research-log entry-061.
Phase 2 (research ch-08) — T-2026-08-01-001-book-ai-agents-with-python — DONE (12 entries entry-062..073; 0 material contradictions; two age-risks flagged inline; one-time Naming-note sidebar requirement captured in entry-070; ApiModel is abstract base, InferenceClientModel is the concrete beginner-friendly class)
Phase 2 (research ch-09) — T-2026-08-01-001-book-ai-agents-with-python — DONE (11 entries entry-074..084; 0 primary-source contradictions; one brief-correction in entry-077 — dispatch prompt claimed dicts auto-JSON-encode and numbers auto-stringify at tool return; verified 1.26.0 source shows raw values preserved, only strings become AgentText under sanitize; chapter will follow verification)
Current chapter: ch-10 (Guide Agents with Instructions and Memory; depends_on ch-09)
- 2026-08-01 — Phase 2: ch-10 validated (entry-085..096, 12 entries); three brief-corrections recorded inline (entry-086 system_prompt kwarg absence, entry-089 provide_run_summary managed-only, entry-093 chat_messages absence).
- 2026-08-01 — Phase 2: ch-11 validated (entry-097..108, 12 entries); managed_agents / step_callbacks / final_answer_checks / 6-class exception hierarchy all verified against installed smolagents 1.26.0 source.
- 2026-08-01 — User granted permission to clone smolagents repo at pinned version for cross-version verification. Master deferred — installed venv IS the 1.26.0 source; will clone only if git blame or cross-version diff becomes necessary.
- 2026-08-01 — Current chapter: ch-12 (Observe, Debug, and Evaluate Runs).
Phase 2 (research ch-12) — T-2026-08-01-001-book-ai-agents-with-python — DONE (12 entries entry-109..120; 0 material contradictions; six inline corrections recorded: LogLevel 4 values, step.timing.duration, logger.log_messages plural + no log_images, stdout default, RunResult.output, FinalAnswerStep not in memory.steps)
Phase 2 (research ch-13) — T-2026-08-01-001-book-ai-agents-with-python — DONE (12 entries entry-121..132; 0 material contradictions; two inline corrections: stub must override Model.generate, not __call__; constructor kwarg is logger= not monitor=)
Protocol change — T-2026-08-01-001-book-ai-agents-with-python — APPLIED (PowerShell Add-Content is unsafe for UTF-8 on this host; all future file writes use Python with encoding=utf-8 or Edit/Write tools; mojibake repair was a one-time recovery).
Current chapter: ch-14 (Keep Agents Safe and Responsible; depends_on ch-13).
Phase 2 (research ch-14) — T-2026-08-01-001-book-ai-agents-with-python — DONE (10 entries entry-133..142; 0 material contradictions; covers prompt injection, authorized_imports, executor_type=, max_steps, final_answer_checks, rate limits, sensitive-data hygiene; 5 inline age-risks + 4 cross-ref corrections).
Current chapter: ch-15 (Coordinate Multiple Agents; depends_on ch-14).
Phase 2 (research ch-15) — T-2026-08-01-001-book-ai-agents-with-python — DONE (12 entries entry-143..154; 0 material contradictions; verified Jinja template keys {{name}}/{{task}}/{{final_answer}} against installed 1.26.0 source; 3 inline age-risks).
Current chapter: ch-16 (Choose and Operate Model Backends; depends_on ch-12, ch-14).
Phase 2 (research ch-16) — T-2026-08-01-001-book-ai-agents-with-python — DONE (12 entries entry-155..166; 0 material contradictions; verified model class hierarchy: Model is abstract base, ApiModel is abstract API subclass, 6 concrete API classes + 3 local classes + 4 server variants; no AnthropicModel class — use LiteLLMModel).
Current chapter: ch-17 (Project: Research and Briefing Agent; depends_on ch-13, ch-14, ch-16).
Phase 2 (research ch-17) — T-2026-08-01-001-book-ai-agents-with-python — DONE (12 entries entry-167..178; 0 material contradictions; project architecture: single CodeAgent with DuckDuckGo + VisitWebpage + Wikipedia, src layout, three-tier testing, JSONL logger).
Current chapter: ch-18 (Project: Multi-Agent Work Assistant; depends_on ch-15, ch-16, ch-17).
Phase 2 (research ch-18) — T-2026-08-01-001-book-ai-agents-with-python — DONE (12 entries entry-179..190; 0 material contradictions; capstone: manager + 3 specialists, per-agent backends, evaluator-optimizer loop, per-agent safety/observability, 4 beginner errors, what-next pointer).
Phase 2 — T-2026-08-01-001-book-ai-agents-with-python — CLOSED. 18 chapters, 190 entries, 0 unresolved material contradictions. File: 472598 bytes, 1302 lines, UTF-8 clean.
PAUSED at Phase 3 user gate (outline). Waiting for user confirmation to dispatch am-planning for the outline.
Phase 3 (outline) — T-2026-08-01-001-book-ai-agents-with-python — DONE (18 chapters, 0 material contradictions, status DRAFT pending user confirmation). Artifact: books/ai-agents-with-python/outline.md.
PAUSED at Phase 3 user gate (outline confirmation). User must confirm before Phase 4 (style/voice) can begin.
Phase 3 (structural change) - T-2026-08-01-001-book-ai-agents-with-python - DONE. User requested one new chapter before smolagents. New ch-08 (How Agents Work: A Toy Agent from Scratch) inserted; old ch-08..ch-18 renumbered to ch-09..ch-19. Skeleton and outline updated; status back to DRAFT pending re-confirmation. New ch-09 (formerly ch-08) summary updated to include a Why Use a Framework intro. Resolved decisions section explicitly notes the structural change. Dispatching am-research for new ch-08 (entry-191..202).
PAUSED at Phase 3 re-confirmation gate. Awaiting am-research for new ch-08, then outline update, then user re-confirmation.
Phase 2 (research addendum ch-08 toy agent) - T-2026-08-01-001-book-ai-agents-with-python - DONE. 12 entries entry-191..202 added. Plain Python only; no smolagents API claims. Outline updated to point at the actual entries. Ready for user re-confirmation of Phase 3 outline.
Phase 4 (style/voice) - T-2026-08-01-001-book-ai-agents-with-python - DONE. 28761 bytes, 4 sections, 18 brief-corrections + 25 age-risks documented. Status: DRAFT. Awaiting user confirmation before Phase 5.
Phase 5 (writing plan) - T-2026-08-01-001-book-ai-agents-with-python - DONE. LINEAR mode. 19 dispatch rows. Awaiting user confirmation before Phase 6.
Phase 6 (write ch-01) - T-2026-08-01-001-book-ai-agents-with-python - DONE. 407 words.
Phase 7 (ch-01 dev review) - T-2026-08-01-001-book-ai-agents-with-python - DONE. PASS_WITH_WARN (1 LOW).
Phase 7 (ch-01 line edit) - T-2026-08-01-001-book-ai-agents-with-python - DONE. PASS_WITH_WARN (2 LOW, non-blocking).
ch-01 status: line-edited. Awaiting whole-book copy-edit pass (after all 19 chapters). Next: ch-02.
Phase 6 (write ch-02) - DONE. 1407 words. Status: line-edited.
Phase 7 (ch-02 dev review) - DONE. FAIL (1 HIGH missing forward-pointer). Fix loop 1: added What's next paragraph. Dev re-review: PASS. Line-edit: PASS_WITH_WARN (4 LOW non-blocking).
ch-02 status: line-edited. ch-01 status: line-edited. Next: ch-03.
ch-03 status: line-edited. 3/19 chapters done. Continuing dispatch.
