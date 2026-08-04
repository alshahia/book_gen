# Full Outline — AI Agents with Python

Status: DRAFT (structural change since 2026-08-01 — pending user re-confirmation)

This outline is the last user-checkpoint before writing starts. It is complete enough that, combined with the book bible and style guide, a writer can draft any chapter from this file alone. Research-log entries are referenced by ID (`entry-NNN`); no findings are paraphrased beyond what the chapter summary itself needs.

## depends_on summary (vs. skeleton)

The skeleton's dependency graph is preserved unchanged. Each later chapter's concrete moves depend on the prior chapter's installed elements:

- ch-01 (independent) installs the beginner mental model of Python, language models, and AI agents that every later chapter rests on.
- ch-02 (depends on ch-01) prepares Python 3.10+, a `.venv` with smolagents and JupyterLab, a `.gitignore` excluding `.venv` and `.env`, and a `.env.example` template that ch-03 onward can rely on without re-teaching setup.
- ch-03 (depends on ch-02) installs values, variables, `print()`, `input()`, f-strings, and the four beginner error categories that ch-04's control flow depends on.
- ch-04 (depends on ch-03) installs `if`/`elif`/`else`, `while` and `for`, `range()`, and the four named control-flow errors that ch-05's collections and I/O depend on.
- ch-05 (depends on ch-04) installs `list`, `tuple`, `set`, `dict`, `open()` with `encoding="utf-8"`, and `csv`/`json` so ch-06 onward can store and load data.
- ch-06 (depends on ch-05) installs the next-token-prediction loop, the context window, the system/user/assistant role convention, and the two beginner safety flags that ch-08's API calls depend on.
- ch-07 (depends on ch-06) installs stdlib HTTP, `requests`, env-var secrets handling, retries with backoff, and the four-bucket error taxonomy that ch-08's toy agent and ch-09's first smolagents agent both inherit.
- ch-08 (depends on ch-07) installs the agent-loop anatomy and the 30-line plain-Python toy agent (prompt model -> parse action -> run tool -> feed result back -> loop until final answer) that ch-09 compares against smolagents.
- ch-09 (depends on ch-08) opens with a short 'Why Use a Framework' intro that compares the ch-08 toy agent to smolagents, then installs smolagents==1.26.0's `CodeAgent` + `InferenceClientModel`, the `@tool` decorator contract, the `final_answer` loop terminator, and the offline stub-model demo that ch-10 and later chapters build on.
- ch-10 (depends on ch-09) installs the docstring-as-contract tool pattern and the verified no-auto-coercion tool-return behavior that ch-11's instructions and ch-12's workflows depend on.
- ch-11 (depends on ch-10) installs the `instructions`, `planning_interval`, `max_steps`, `reset=`, `return_full_result=` knobs that ch-12, ch-13, and ch-14 reuse.
- ch-12 (depends on ch-11) installs the `managed_agents`, `step_callbacks`, `final_answer_checks`, and the six-class exception hierarchy that ch-13, ch-14, and ch-15 build on.
- ch-13 (depends on ch-12) installs the three observability pillars (`step_callbacks`, `final_answer_checks`, `RunResult`) that ch-14 tests assert against.
- ch-14 (depends on ch-13) installs the stub-model pattern (subclass `Model`, override `generate`), pytest fixtures, and gold-answer tests that ch-18 and ch-19 reuse.
- ch-15 (depends on ch-14) installs the safety scaffolding (`executor_type`, `authorized_imports`, `final_answer_checks`, secrets redaction) that ch-16, ch-18, and ch-19 hard-code at scale.
- ch-16 (depends on ch-15) installs the manager + `managed_agents` pattern, the per-agent scope rule, the verified Jinja handoff contract, and the sequential-only invocation rule that ch-17, ch-18, and ch-19 build on.
- ch-17 (depends on ch-13, ch-15) installs the fourteen-name model surface, the `LiteLLMModel` Anthropic path, the `*ServerModel` family, the two-level `Model` / `ApiModel` hierarchy, and the backend factory that ch-18 and ch-19 pick from per agent.
- ch-18 (depends on ch-14, ch-15, ch-17) installs the research-and-briefing capstone shape (single `CodeAgent`, three web tools, four-knob safety, three-layer test suite) that ch-19 extends.
- ch-19 (depends on ch-16, ch-17, ch-18) installs the four-agent capstone (manager + researcher + writer + reviewer, per-agent models, per-agent JSONL logs, three-layer tests) that closes the book.

No reordering or dependency change is recommended. Reasoning: every later chapter's *concrete move* would be unsupported if the earlier chapter's move had not been installed; reversing any edge would force the writer to introduce a concept before it had been justified.

---

## ch-01 — Meet Python and AI Agents

Outcome: by the end of the reading, the reader can describe in plain language what Python is, what a large language model is, what an AI agent is, and why agent output must be treated as a draft before being acted on.

Summary: By the end of this chapter the reader has a beginner-friendly mental model of Python, language models, and AI agents that the rest of the book rests on, without having written or run any code. The chapter stands alone — it assumes no prior Python, LLM, or agent experience — but it plants every conceptual seed the later chapters need: Python's general-purpose, batteries-included posture and its suitability as the agent base (entry-001, entry-002, entry-003); the next-token-prediction model and the hallucination / bias / compute caveats that agent authors must respect (entry-004, entry-005); the smolagents "agency as a spectrum" definition and the tool-as-typed-function contract that beginners will write in ch-09 (entry-006, entry-008); and the Anthropic "workflows vs agents" distinction with its built-in stop conditions (entry-007). Entry-061 is referenced once here as a forward-pointer to ch-09's one-time sidebar so the writer knows the class-rename corrective belongs to ch-09's prose and not ch-01's. The chapter closes the conceptual half of the book before ch-02 opens the setup half.

Draws on: entry-001, entry-002, entry-003, entry-004, entry-005, entry-006, entry-007, entry-008, entry-061 (corrective, referenced as ch-09 sidebar trigger)

depends_on: independent

Contradiction framing needed: none

---

## ch-02 — Set Up a Cross-Platform Workspace

Outcome: by the end of the reading, the reader has a working Python 3.10+ interpreter, a `.venv` virtual environment with smolagents and JupyterLab installed, a `.gitignore` that excludes `.venv` and `.env`, and a `.env.example` template ready for the API keys ch-08 onward will need.

Summary: By the end of this chapter the reader has a cross-platform Python workspace ready for every later example. The chapter depends on ch-01 because the "what kind of tool is Python" framing is reused in the install walkthrough. It draws on entry-009 for the version floor (smolagents requires Python ≥3.10; the chapter picks the latest bugfix release as the durable default), entry-010 for the Windows Python Install Manager story (with the explicit "this section may age quickly" flag), entry-011 for the macOS python.org universal2 installer, entry-012 for the Linux distribution-and-pyenv story, entry-013 for `python -m venv .venv` and per-OS activation, entry-014 for `python -m pip install` and pinning, entry-015 for JupyterLab placement in the same `.venv` as the kernel, entry-016 for the `python -m <module>` vs `python script.py` rule, entry-017 for the python-dotenv + `load_dotenv()` baseline and the "production wins over `.env`" default, and entry-018 for the project-folder convention with the canonical Python `.gitignore` lines.

Draws on: entry-009, entry-010, entry-011, entry-012, entry-013, entry-014, entry-015, entry-016, entry-017, entry-018

depends_on: ch-01

Contradiction framing needed: none

---

## ch-03 — Write Your First Python Programs

Outcome: by the end of the reading, the reader can write, save, and run a short Python script that uses values, variables, `input()`, `print()`, f-strings, and the four beginner error categories.

Summary: By the end of this chapter the reader can write, save, and run a short Python script that prints and reads text, names and reassigns variables, and uses the four beginner error categories as navigation. The chapter depends on ch-02 because the same `.venv` and `python -m` interpreter carry the script; the reader runs the script with the project's Python launcher and sees the same output a notebook cell would show. It draws on entry-019 for the variables-and-dynamic-typing mental model (a name is a label, the object has the type), entry-020 for the integer / float / string literal set and the operators, entry-021 for the canonical `print("Hello, world!")` first program, entry-022 for f-strings (PEP 498, available throughout the book's 3.10+ floor), entry-023 for `input()` plus the explicit `int()` / `float()` conversion, entry-024 for reading tracebacks from the bottom up across the four named errors (`SyntaxError`, `IndentationError`, `NameError`, `TypeError`), entry-025 for the `.py`-vs-notebook execution model and the "restart kernel and run from top" reproducibility check, and entry-026 for the small PEP 8 subset (four-space indent, snake_case names, one space around operators).

Draws on: entry-019, entry-020, entry-021, entry-022, entry-023, entry-024, entry-025, entry-026

depends_on: ch-02

Contradiction framing needed: none

---

## ch-04 — Make Programs Decide and Repeat

Outcome: by the end of the reading, the reader can write programs that use `if`/`elif`/`else`, `while` and `for` loops, `range()`, and `break`/`continue`, and can name the four beginner control-flow errors (infinite loop, off-by-one, `=` vs `==`, mutating-during-iteration).

Summary: By the end of this chapter the reader can build programs that respond to changing input and repeat work — the conditional and loop building blocks that ch-05's collections and ch-09's agent loop reuse. The chapter depends on ch-03 because every example still uses values, variables, `print()`, and f-strings; the new ingredient is control flow. It draws on entry-027 for the `bool` type and the truthiness rule (the enumerated false values and the `if name:` shortcut), entry-028 for the six beginner comparison operators and chained comparisons, entry-029 for `and`/`or`/`not` short-circuit (and the trap that `or`/`and` return one of their operands), entry-030 for the `if`/`elif`/`else` syntax with its three indentation rules, entry-031 for `while`, `break`, `continue`, and the safe `while True: ... break` pattern, entry-032 for `for` over strings and lists with a warning against mutating during iteration, entry-033 for the three `range()` forms and the half-open-interval rule that drives off-by-one errors, and entry-034 for the four named beginner errors and their one-line fixes.

Draws on: entry-027, entry-028, entry-029, entry-030, entry-031, entry-032, entry-033, entry-034

depends_on: ch-03

Contradiction framing needed: none

---

## ch-05 — Work with Data and Files

Outcome: by the end of the reading, the reader can store collections in lists, tuples, sets, and dicts; read and write text files using `with` and `encoding="utf-8"`; and read/write CSV and JSON with the standard library.

Summary: By the end of this chapter the reader can store collections of values, walk and mutate them, and persist them as text, CSV, or JSON files — the storage layer that ch-06 onward will reuse when prompts and tool results need to be saved. The chapter depends on ch-04 because every collection example loops over items, and `with open(...)` uses the `for line in f:` form from ch-04. It draws on entry-035 for `list` and its beginner methods (`append`, `remove`, `pop`, `len`, `in`), entry-036 for `tuple` and tuple unpacking (with the `TypeError` from item assignment), entry-037 for `set` and the four set algebra operators (with the empty-set `set()` vs `{}` pitfall), entry-038 for `dict` and the safe `.get(key, default)` form (with the 3.7+ insertion-order guarantee), entry-039 for the strings-behave-like-lists shortcut (zero-based indexing, slicing, `in` for substring), entry-040 for `open()` with `encoding="utf-8"` and the required `with` statement, entry-041 for `csv.reader` / `csv.writer` / `csv.DictReader` / `csv.DictWriter` (with `newline=""` for Windows), entry-042 for `json.dump` / `json.load` with `ensure_ascii=False, indent=2`, and entry-043 for the supported-types cheat sheet and the `tuple → list` / `set-rejected` warnings.

Draws on: entry-035, entry-036, entry-037, entry-038, entry-039, entry-040, entry-041, entry-042, entry-043

depends_on: ch-04

Contradiction framing needed: none

---

## ch-06 — Understand Language Models

Outcome: by the end of the reading, the reader can explain the next-token-prediction loop, the context window, the system/user/assistant role convention, and the two beginner safety flags (untrusted output, jailbreaking via context).

Summary: By the end of this chapter the reader can explain, in plain language, how an LLM works, what a token is, what a context window is, and why model output must be treated as a draft before any agent action runs on it. The chapter depends on ch-05 only loosely — every "file" example in ch-06 is a small text snippet held in a Python string. It draws on entry-044 for the next-token-prediction loop as the chapter's centerpiece, entry-045 for tokens as sub-words and the "tokens are the model's alphabet" framing (with the rough 1.5-tokens-per-word estimator noted but deferred), entry-046 for the training-vs-inference split and "every `model.generate(prompt)` is online inference", entry-047 for the context window and the "lost in the middle" effect (with specific model sizes kept directional), entry-048 for temperature and `top_p` sampling (with `top_k` and friends deferred), entry-049 for the system / user / assistant role convention (with a one-line note that OpenAI renamed "system" to "developer" and that the chapter teaches the pattern, not the exact name), and entry-050 for the two beginner safety flags carried into ch-15 (untrusted output; context-window jailbreaking).

Draws on: entry-044, entry-045, entry-046, entry-047, entry-048, entry-049, entry-050

depends_on: ch-05

Contradiction framing needed: none

---

## ch-07 — Call Models Safely from Python

Outcome: by the end of the reading, the reader can post a chat-completion request to a provider API from a notebook or script, with `HF_TOKEN` or `OPENAI_API_KEY` loaded from `.env`, an explicit timeout, a retry-with-backoff loop on 429 and 5xx, and a clear catch on auth / bad-request errors.

Summary: By the end of this chapter the reader can post a chat-completion request to a provider API from a notebook or script with secrets loaded from `.env`, an explicit timeout, and a small retry-with-backoff loop. The chapter depends on ch-06 because the request body uses the system / user / assistant role convention established there. It draws on entry-051 for the stdlib `urllib.request` POST-JSON path and the `http.HTTPStatus` enum, entry-052 for the `requests` 2.34.2 package and the verified `timeout=` rule, entry-053 for the `load_dotenv()` + `os.getenv()` baseline and the explicit missing-key check, entry-054 for the request / response shape (with the age-risk note that base URLs, field names, and model identifiers change every API version), entry-055 for the always-pass-timeout rule across stdlib, requests, and the openai SDK, entry-056 for the stdlib retry-with-backoff recipe (with `tenacity` mentioned as the upgrade path), entry-057 for HTTP 429 and the `Retry-After` header, entry-058 for the four-bucket error taxonomy (network / auth / bad-request / server), entry-059 for the three-rule API-key security baseline (never in source, never in git, always read from env at runtime), and entry-060 for the minimal conversation loop that ch-09's first agent inherits.

Draws on: entry-051, entry-052, entry-053, entry-054, entry-055, entry-056, entry-057, entry-058, entry-059, entry-060

depends_on: ch-06

Contradiction framing needed: none

---

## ch-08 — How Agents Work: A Toy Agent from Scratch

Outcome: by the end of the reading, the reader can write a 30-line agent loop in plain Python that prompts the model, parses a chosen action, runs a tool, feeds the result back, and loops until the model says "done" — and can name, in plain language, what smolagents will automate for them in the next chapter.

Summary: By the end of this chapter the reader has built a minimal agent from scratch — no smolagents, no framework — so the next chapter's smolagents introduction lands on a concrete mental model rather than abstract magic. The chapter depends on ch-07 because the same provider API call (the `requests.post(...)` with `HF_TOKEN` from `.env`) provides the only model interaction the toy agent needs; everything else is a plain-Python loop the reader already has the building blocks for. It draws on entries to be produced by the post-skeleton-change research dispatch for the agent-loop anatomy (the prompt, the action parser, the tool-call dispatch, the result-feed loop, the implicit termination), the four-step mental model (observe → decide → act → observe), the comparison to the ch-07 minimal conversation loop (one call vs many), the two cost-of-diy costs (no parallel tool calls, no schema-aware retries), the four beginner errors (infinite loop without a `max_steps` guard, model returning prose instead of structured action, action name mismatch, tool exception unwitnessed), the offline stub-model demo (the model-less loop where the parser is fed canned actions), the forward-pointer to the smolagents chapter that "automates this loop for you," and the explicit framing that the chapter is about understanding, not adoption. The chapter deliberately does NOT use smolagents, the `@tool` decorator, `CodeAgent`, `final_answer`, or any of the framework surface — the framework is introduced in the very next chapter. The `Draws on:` field is updated once the new research entries are produced.

Draws on: entry-191, entry-192, entry-193, entry-194, entry-195, entry-196, entry-197, entry-198, entry-199, entry-200, entry-201, entry-202 (entries produced by the post-skeleton-change research dispatch verified 2026-08-01)

depends_on: ch-07

Contradiction framing needed: none

---

## ch-09 — Build a First smolagents Agent

Outcome: by the end of the reading, the reader can construct a `CodeAgent` with one or two small `@tool`-decorated functions, run `.run(task)`, and inspect the returned answer and (optionally) the `RunResult`.

Summary: By the end of this chapter the reader can build a first smolagents==1.26.0 agent that solves a small task, prints the final answer, and (optionally) inspects the `RunResult`. The chapter depends on ch-08 because the framework automates the loop the toy agent already proves works, and the same `InferenceClientModel` + `HF_TOKEN` setup is reused. The chapter opens with a short "Why Use a Framework" intro that compares the ch-08 toy agent to smolagents so the framework introduction lands on a concrete mental model rather than abstract magic — the intro names the four things smolagents automates (the action parser, the dispatch table, the step loop, the final-answer termination) and the three things it adds (typed schemas, retry-able step errors, agent-aware tool errors), then moves to the smolagents code. It draws on entry-062 for the canonical import line (`CodeAgent`, `ApiModel`, `tool`, plus `InferenceClientModel` as the concrete class the quickstart actually instantiates), entry-063 for the two-knob model construction (`model_id` plus `token` with the `HF_TOKEN` fallback), entry-064 for `CodeAgent(tools=[], model=...)` as the minimum construction (with `executor_type` and `managed_agents` deferred to ch-15 and ch-12), entry-065 for the `@tool` decorator contract (typed parameters, typed return, docstring with `Args:`), entry-066 for `.run(task)` and the final-answer-vs-`RunResult` distinction, entry-067 for the step-loop mental model (one iteration = one `step()`), entry-068 for `final_answer` as the implicit loop terminator, entry-069 for the `Qwen/Qwen2.5-Coder-7B-Instruct` beginner default and the missing-token pre-check, entry-070 for the one-time naming-note sidebar (entry-061 corrective), entry-071 for the `LocalPythonExecutor` "not a sandbox" caveat, entry-072 for the four first-run errors (missing `HF_TOKEN`, wrong repo id, vague docstring, missing `import`), and entry-073 for the offline stub-model demo.

Draws on: entry-061 (operative, sidebar trigger), entry-062, entry-063, entry-064, entry-065, entry-066, entry-067, entry-068, entry-069, entry-070, entry-071, entry-072, entry-073

depends_on: ch-08

Contradiction framing needed: the one-time naming-note sidebar about the `HfApiModel` → `ApiModel` rename (research-log entry-061 records the corrective; entry-070 records the sidebar requirement). The literal `HfApiModel` string must appear in the ch-09 prose exactly once, in this sidebar, and must not appear anywhere else in the book. This is the only place in the outline where the literal `HfApiModel` string is permitted.

---

## ch-10 — Give Agents Useful Tools

Outcome: by the end of the reading, the reader can write a typed, docstring-rich `@tool` function, pass it in `tools=[...]`, and rely on the verified no-auto-coercion tool-return behavior (return a string unless another type is genuinely useful).

Summary: By the end of this chapter the reader can write a typed, docstring-rich Python function, decorate it with `@tool`, and pass it in `tools=[...]` so the agent can call it by name with a clear contract. The chapter depends on ch-09 because the same `CodeAgent(tools=[...], model=...)` constructor receives the new tools. It draws on entry-074 for the decorator's auto-inspection contract, entry-075 for the type-hint requirement, entry-076 for the Google / NumPy docstring style and the "use this when…" selection rule, entry-077 for the verified no-auto-coercion return behavior (the chapter teaches explicit `json.dumps()` / `str()` rather than the dispatch's "dict becomes JSON" wording), entry-078 for how the agent selects tools (by name + description + inputs schema, not by reading the body), entry-079 for the built-in tool inventory, entry-080 for the `add_base_tools=False` default, entry-081 for the `AgentToolExecutionError` recovery path, entry-082 for the "tool is a capability boundary, not a safety boundary" caveat (deferred to ch-15), entry-083 for the four first-tool traps (missing hints, vague docstring, accidental `None`, `final_answer` name shadowing), and entry-084 for the smallest runnable.

Draws on: entry-074, entry-075, entry-076, entry-077, entry-078, entry-079, entry-080, entry-081, entry-082, entry-083, entry-084

depends_on: ch-09

Contradiction framing needed: none (the no-auto-coercion brief-correction in entry-077 is a behavioral fact the writer will follow; verified 1.26.0 source does not silently coerce dicts to JSON or numbers to strings at the tool boundary).

---

## ch-11 — Guide Agents with Instructions and Memory

Outcome: by the end of the reading, the reader can shape an agent's behavior with the `instructions` parameter, set a `planning_interval` for periodic re-plan steps, cap the step budget with `max_steps`, and control multi-turn memory with `reset=False` and `additional_args`.

Summary: By the end of this chapter the reader can shape an agent's behavior with a short `instructions` paragraph, give it a re-plan cadence via `planning_interval`, cap the step budget with `max_steps`, and control multi-turn memory with `reset=False` and `additional_args`. The chapter depends on ch-10 because every knob here sits on the same `CodeAgent` / `ToolCallingAgent` constructor that ch-10 built. It draws on entry-085 for the `instructions` contract (a paragraph appended via the `{{custom_instructions}}` block), entry-086 for the verified "no `system_prompt` kwarg in 1.26.0" brief-correction, entry-087 for the three named prompt-template pieces, entry-088 for the `planning_interval` trigger logic, entry-089 for the verified "`provide_run_summary` fires only inside `MultiStepAgent.__call__`" brief-correction, entry-090 for the `RunResult` shape (`output`, `state`, `steps`, `token_usage`, `timing`), entry-091 for the `max_steps=20` default and the absence of a wall-clock cap, entry-092 for `agent.memory.steps` and the `reset=True` default, entry-093 for the verified "no `chat_messages=` parameter" brief-correction, entry-094 for the `to_dict` / `save` template-shipping surface (runtime state is not persisted), entry-095 for the four beginner errors, and entry-096 for the forward-pointers to ch-12 / ch-13 / ch-14.

Draws on: entry-085, entry-086, entry-087, entry-088, entry-089, entry-090, entry-091, entry-092, entry-093, entry-094, entry-095, entry-096

depends_on: ch-10

Contradiction framing needed: none (three brief-corrections to the verified 1.26.0 surface — no `system_prompt` kwarg, `provide_run_summary` is managed-only, no `chat_messages` parameter — are recorded as verified behavior the writer will follow).

---

## ch-12 — Create Structured Agent Workflows

Outcome: by the end of the reading, the reader can design a single-agent workflow that uses `managed_agents` to call a specialist, `step_callbacks` to observe, `final_answer_checks` to gate the final answer, and plain Python `while` / `for` around `.run(reset=False)` for evaluator-optimizer loops.

Summary: By the end of this chapter the reader can design a single-agent workflow that uses `managed_agents` to call a specialist by name, `step_callbacks` to observe each step, `final_answer_checks` to gate the final answer, and a plain Python `while` / `for` around `.run(reset=False)` for evaluator-optimizer loops. The chapter depends on ch-11 because every knob (`instructions`, `planning_interval`, `max_steps`, `reset=`) is reused. It draws on entry-097 for the single-agent scope statement (ch-12 stays inside one agent; ch-16 is the multi-agent chapter), entry-098 for the Anthropic five-pattern taxonomy (the chapter names all five and implements two), entry-099 for the `managed_agents=` rewrite, entry-100 for the inverse `@tool`-wrapped-agent pattern, entry-101 for `step_callbacks` list vs dict, entry-102 for `final_answer_checks` (truthy accept / falsy reject / `AgentError`), entry-103 for per-agent `max_steps` / `planning_interval`, entry-104 for plain-Python chaining via two `.run()` calls and an f-string interpolation, entry-105 for the `while` + `reset=False` evaluator loop, entry-106 for the six-class exception hierarchy, entry-107 for the four beginner errors, and entry-108 for the runnable two-agent demo.

Draws on: entry-097, entry-098, entry-099, entry-100, entry-101, entry-102, entry-103, entry-104, entry-105, entry-106, entry-107, entry-108

depends_on: ch-11

Contradiction framing needed: none

---

## ch-13 — Observe, Debug, and Evaluate Runs

Outcome: by the end of the reading, the reader can attach a `step_callbacks` callback to capture per-step data, read `agent.memory.steps` and `RunResult` after the run, classify errors via the six-class exception hierarchy, and run a small `(task, expected_answer)` evaluator loop.

Summary: By the end of this chapter the reader can observe what an agent did (`step_callbacks`), debug why it failed (correlate `step.tool_calls`, `step.observations`, `step.error`), and evaluate how good the answer was (`RunResult.output`, `state`, `token_usage`, `timing`). The chapter depends on ch-12 because every observability hook sits on the same `MultiStepAgent`. It draws on entry-109 for the three pillars (observation, debugging, evaluation), entry-110 for the four-value `LogLevel` enum (`OFF`, `ERROR`, `INFO`, `DEBUG`), entry-111 for the `ActionStep` fields the callback receives (`duration` lives at `step.timing.duration`, not as a direct attribute), entry-112 for `final_answer_checks` read-only semantics, entry-113 for `AgentLogger` / `Monitor` (default writes to stdout; canonical method is `log_messages` plural), entry-114 for the `RunResult` shape, entry-115 for the three typed step classes in `agent.memory.steps` (`FinalAnswerStep` is yielded but not appended; read the final answer from `RunResult.output` instead), entry-116 for `step.timing.duration` as a `step.timing` property, entry-117 for the six-class exception taxonomy with retry / replan / fail rules, entry-118 for the `(task, expected_answer)` evaluator pattern, entry-119 for the four beginner errors, and entry-120 for the runnable three-case evaluator demo.

Draws on: entry-109, entry-110, entry-111, entry-112, entry-113, entry-114, entry-115, entry-116, entry-117, entry-118, entry-119, entry-120

depends_on: ch-12

Contradiction framing needed: none (five brief-corrections to the verified 1.26.0 API surface — `LogLevel` has four values including `OFF`, `duration` is `step.timing.duration` not `step.duration`, `AgentLogger` writes to stdout not stderr, `RunResult.output` not `final_answer`, `FinalAnswerStep` not in `agent.memory.steps` — are recorded as verified behavior the writer will follow).

---

## ch-14 — Test Agents Without Guessing

Outcome: by the end of the reading, the reader can write a pytest suite that stubs the model by subclassing `Model` and overriding `generate`, runs the agent with `max_steps=1` and `return_full_result=True`, captures logs by passing a `logger=` `AgentLogger` subclass, and asserts on `RunResult.output`, `RunResult.state`, and the steps recorded by a `step_callbacks` callback.

Summary: By the end of this chapter the reader can write a pytest suite that replaces the model with a stub (subclass `Model`, override `generate`, return a canned `ChatMessage`), runs the agent with `max_steps=1` and `return_full_result=True`, captures logs by passing a `logger=` `AgentLogger` subclass, and asserts on `RunResult.output`, `RunResult.state`, and the steps recorded by a `step_callbacks` callback. The chapter depends on ch-13 because every assertion surface (`RunResult`, `agent.memory.steps`, `AgentError`) was introduced there. It draws on entry-121 for the four sources of non-determinism and the "stub the model" mitigation, entry-122 for the verified stub pattern (override `generate`, not `__call__`, with a canned `ChatMessage`; `Model` has no `create_client` so it sidesteps `ApiModel.create_client`'s `NotImplementedError`), entry-123 for `max_steps=1` as the unit-test default, entry-124 for the `step_callbacks={ActionStep: record}` dict form, entry-125 for the verified `logger=` kwarg (the `monitor=` kwarg does not exist in 1.26.0) and the `ListLogger` subclass pattern, entry-126 for the per-call `return_full_result=True`, entry-127 for the gold-answer test pattern, entry-128 for `@pytest.fixture` and `pytest.raises`, entry-129 for the `pytest-asyncio` note (`MultiStepAgent.run` is sync), entry-130 for `pytest.mark.parametrize` with `ids=`, entry-131 for the four beginner errors, and entry-132 for the forward-pointers to ch-15 / ch-18 / ch-19.

Draws on: entry-121, entry-122, entry-123, entry-124, entry-125, entry-126, entry-127, entry-128, entry-129, entry-130, entry-131, entry-132

depends_on: ch-13

Contradiction framing needed: none (two brief-corrections to the verified 1.26.0 surface — stub overrides `generate` not `__call__`, log capture uses the `logger=` kwarg not `monitor=` — are recorded as verified behavior the writer will follow).

---

## ch-15 — Keep Agents Safe and Responsible

Outcome: by the end of the reading, the reader can classify tools by their strongest possible side effect, scope `PythonInterpreterTool(authorized_imports=...)` with a small explicit list, switch `executor_type` to `"docker"` (or a provider sandbox) for untrusted generated code, set `max_steps` and `final_answer_checks` as guards, and keep secrets in `.env` while redacting tokens from `RunResult` before logging.

Summary: By the end of this chapter the reader can classify tools by their strongest possible side effect, scope the import fence, switch `executor_type` for untrusted generated code, set `max_steps` as the loop circuit breaker, use `final_answer_checks` as a final-answer allowlist, and keep secrets in `.env` while redacting tokens from `RunResult`. The chapter depends on ch-14 because every safety control is testable with the same stub-model pattern ch-14 taught. It draws on entry-133 for the NIST / OWASP / Anthropic framing, entry-134 for prompt injection and the "label web / file content as data" rule, entry-135 for tool side-effect classification, entry-136 for the `authorized_imports` fence with the verified "None means base modules only" rule, entry-137 for `executor_type` choices and the verified "managed agents cannot use non-local executors in 1.26.0" restriction, entry-138 for `max_steps` as the circuit breaker (default 20; no wall-clock cap), entry-139 for `final_answer_checks` and the verified "post-`max_steps` final answer bypasses `_validate_final_answer`" caveat, entry-140 for the web-tool defaults (`rate_limit=1.0` queries per second; `max_output_length=40000`; plain HTTP, no JavaScript), entry-141 for the secrets / logging baseline, and entry-142 for the forward-pointers to ch-16 / ch-18 / ch-19.

Draws on: entry-133, entry-134, entry-135, entry-136, entry-137, entry-138, entry-139, entry-140, entry-141, entry-142

depends_on: ch-14

Contradiction framing needed: none (two brief-corrections to the verified 1.26.0 surface — `authorized_imports=None` means base modules only, and the final answer generated after `max_steps` is exhausted bypasses `_validate_final_answer` — are recorded as verified behavior the writer will follow).

---

## ch-16 — Coordinate Multiple Agents

Outcome: by the end of the reading, the reader can build a manager `CodeAgent` that routes work to two or three specialist managed agents via `managed_agents=[...]`, pass context explicitly via `additional_args` (because per-agent memory is private), and apply per-agent scopes (separate `tools`, `model`, `executor_type`, `max_steps`, `final_answer_checks`) from ch-15 to limit blast radius.

Summary: By the end of this chapter the reader can build a manager `CodeAgent` that routes work to two or three specialist managed agents via `managed_agents=[...]`, pass context explicitly through `additional_args`, and apply per-agent scopes from ch-15 to limit blast radius. The chapter depends on ch-15 because every multi-agent failure mode is a ch-15 boundary applied per agent. It draws on entry-143 for the "why split at all" motivation (shorter prompts, tighter tool lists, role specialization), entry-144 for the `managed_agents=` rewrite, entry-145 for the verified Jinja handoff contract — the keys are inner Jinja names `{{name}}`, `{{task}}` for the task prompt and `{{name}}`, `{{final_answer}}` for the report (NOT nested `{{managed_agent.task}}` / `{{managed_agent.report}}`), entry-146 for per-agent memory isolation (no shared blackboard), entry-147 for the verified "`max_steps` does not cascade" rule, entry-148 for the `planning_interval` (one agent re-plans) vs `managed_agents` (team of agents) distinction, entry-149 for the explicit-handoff pattern, entry-150 for the verified "managed agents run sequentially, not in parallel" 1.26.0 limitation, entry-151 for the per-agent scope controls, entry-152 for the three reusable shapes (orchestrator-workers, sequential handoff, evaluator-optimizer), entry-153 for the four beginner errors, and entry-154 for the forward-pointers to ch-17 / ch-18 / ch-19.

Draws on: entry-143, entry-144, entry-145, entry-146, entry-147, entry-148, entry-149, entry-150, entry-151, entry-152, entry-153, entry-154

depends_on: ch-15

Contradiction framing needed: none (the Jinja-key brief-correction — verified keys are `{{name}}`, `{{task}}`, `{{final_answer}}`, NOT the dispatch's nested-path form — is recorded as verified behavior the writer will follow).

---

## ch-17 — Choose and Operate Model Backends

Outcome: by the end of the reading, the reader can pick from the fourteen-name smolagents 1.26.0 model surface (`Model`, `ApiModel`, `InferenceClientModel`, `OpenAIModel`, `AzureOpenAIModel`, `AmazonBedrockModel`, `LiteLLMModel`, `LiteLLMRouterModel`, `TransformersModel`, `VLLMModel`, `MLXModel`, `OpenAIServerModel`, `AmazonBedrockServerModel`, `AzureOpenAIServerModel`), choose `OpenAIModel` for OpenAI's first-party API and `LiteLLMModel(model_id="anthropic/...")` for Anthropic (because no `AnthropicModel` exists in 1.26.0), point the `*ServerModel` family at any OpenAI-compatible endpoint, and write a small backend-selection factory function.

Summary: By the end of this chapter the reader can pick a model backend for any project, point the `*ServerModel` family at OpenAI-compatible endpoints, and write a small factory function that maps a config string to a model class. The chapter depends on ch-13 and ch-15 because every backend choice has a `RunResult` (ch-13) and a secrets / privacy (ch-15) consequence. It draws on entry-155 for the two-level hierarchy (`Model` is the root; `ApiModel` is the API-backed subclass; the three local-runtime classes extend `Model` directly because they do not own an HTTP client), entry-156 for the verified fourteen-name public surface, entry-157 for the `*ServerModel` family (still extends provider parents and uses the `openai` SDK for serialization), entry-158 for `InferenceClientModel` and the `HF_TOKEN` fallback, entry-159 for `OpenAIModel` and the verified `api_base=` kwarg (NOT `OPENAI_API_BASE`), entry-160 for `LiteLLMModel` as the Anthropic path (no `AnthropicModel` exists in 1.26.0), entry-161 for the three local-runtime backends (advanced / optional), entry-162 for `LiteLLMRouterModel` as the failover tool, entry-163 for the five-axis tradeoff table (directional only, no fabricated numbers), entry-164 for the backend factory pattern, entry-165 for the four beginner errors, and entry-166 for the forward-pointers to ch-18 / ch-19.

Draws on: entry-155, entry-156, entry-157, entry-158, entry-159, entry-160, entry-161, entry-162, entry-163, entry-164, entry-165, entry-166

depends_on: ch-13, ch-15

Contradiction framing needed: none (three brief-corrections to the verified 1.26.0 surface — two-level hierarchy `Model` → `ApiModel` with local classes extending `Model` directly, `*ServerModel` classes still extending their provider parent, and `api_base=` rather than `OPENAI_API_BASE` — are recorded as verified behavior the writer will follow). The older class name recorded in entry-061 is not exported in 1.26.0 and must not appear anywhere in ch-17's body.

---

## ch-18 — Project: Research and Briefing Agent

Outcome: by the end of the reading, the reader has a runnable `src/research_briefing/` project that takes a topic string and returns a 200-400 word briefing with 3-5 cited source URLs, gated by `max_steps=15`, two `final_answer_checks` (max length, must contain `Sources:`), a 2.0-second web-tool rate limit, and a 10000-character page-fetch cap; the test suite has three layers (smoke, gold, live) and a per-run JSONL trace.

Summary: By the end of this chapter the reader has a runnable research-and-briefing project with a single `CodeAgent`, three web tools, four safety knobs, and a three-layer test suite. The chapter depends on ch-14 (the stub-model test pattern reused at project scale), ch-15 (the four safety knobs hard-coded in code), and ch-17 (the project picks `OpenAIModel(model_id="gpt-4o-mini")` as primary with `InferenceClientModel` as fallback via a tiny factory). It draws on entry-167 for the project goal and the three acceptance tests (coherence, source-per-claim, no fabricated URLs), entry-168 for the single-`CodeAgent` shape with `add_base_tools=False`, entry-169 for the three tools (`DuckDuckGoSearchTool`, `VisitWebpageTool`, `WikipediaSearchTool`) and their verified `rate_limit` / `max_output_length` knobs, entry-170 for the primary / fallback factory, entry-171 for the `src` layout, entry-172 for the four-knob safety hardening (`max_steps=15`, two `final_answer_checks`, `rate_limit=2.0`, `max_output_length=10000`), entry-173 for the prompt-injection defense (the structural `Sources:` line), entry-174 for the three-layer test suite with the custom `live` marker, entry-175 for the JSONL observability, entry-176 for the directional cost / latency framing, entry-177 for the four beginner errors, and entry-178 for the forward-pointers to ch-19 / ch-15.

Draws on: entry-167, entry-168, entry-169, entry-170, entry-171, entry-172, entry-173, entry-174, entry-175, entry-176, entry-177, entry-178

depends_on: ch-14, ch-15, ch-17

Contradiction framing needed: none

---

## ch-19 — Project: Multi-Agent Work Assistant

Outcome: by the end of the reading, the reader has a runnable `src/work_assistant/` capstone project with a manager `CodeAgent` (no direct tools, three `managed_agents`) that routes a free-text request through a researcher (sources), a writer (prose), and a reviewer (numeric score + revision request), each with its own `model`, `tools`, `max_steps`, `final_answer_checks`, and JSONL logger; the reviewer runs an evaluator-optimizer loop with the writer until the score passes.

Summary: By the end of this chapter the reader has a runnable multi-agent capstone project with a manager that routes work to three specialists (researcher, writer, reviewer), each with its own model, tools, step budget, validator, and per-agent JSONL trace. The chapter depends on ch-16 (the `managed_agents=[...]` pattern is the wiring), ch-17 (each agent's `model=` is chosen from the fourteen-name surface, with a cheap manager and stronger specialists), and ch-18 (the project is the ch-18 single-agent shape extended with a `Critic` managed agent). It draws on entry-179 for the project acceptance (final deliverable, at least one reviewer flag, sources for every claim), entry-180 for the manager-plus-three-specialists shape, entry-181 for per-agent model selection (cheap manager, strong researcher, strong writer, strongest reviewer), entry-182 for the verified Jinja handoff contract, entry-183 for the reviewer-as-evaluator-optimizer (score 1-5, revise until ≥4), entry-184 for the `src` layout, entry-185 for per-agent `max_steps` and `final_answer_checks`, entry-186 for per-agent JSONL logs, entry-187 for the three-layer test suite, entry-188 for the directional cost / latency budget, entry-189 for the four beginner errors, and entry-190 for the next-step pointers.

Draws on: entry-179, entry-180, entry-181, entry-182, entry-183, entry-184, entry-185, entry-186, entry-187, entry-188, entry-189, entry-190

depends_on: ch-16, ch-17, ch-18

Contradiction framing needed: none

---

## Resolved decisions

No material contradictions surfaced in the research-log. No user-level decisions required at this gate.

The research-log explicitly records (in its `## Contradiction flags` sections for ch-01 through ch-19) that no chapter surfaces a material contradiction between primary sources. Every claim is verified against installed smolagents==1.26.0 source at `E:\book_gen\.venv\Lib\site-packages\smolagents\` on 2026-08-01, against the v1.26.0 official reference pages at `https://huggingface.co/docs/smolagents/v1.26.0/en/reference/...`, and against the Python 3.14.6 / pytest 9.1.1 / OWASP LLM01:2025 / NIST AI RMF 1.0 / Anthropic "Building effective agents" primary sources. Eighteen brief-corrections are recorded in the research-log as reconciliations between the chapter briefs and the verified 1.26.0 runtime — not as contradictions between two valid external sources — and the writer will follow the verified behavior in every case (entry-061, entry-077, entry-086, entry-089, entry-093, entry-110, entry-111, entry-113, entry-114, entry-115, entry-122, entry-125, entry-136, entry-139, entry-145, entry-155, entry-157, entry-159). Twenty-five inline age-risks (provider model names, API versions, rate-limit units, context-window sizes, executor-type names) are kept directional in the prose rather than committed to exact figures, per the ch-02 / ch-06 / ch-08 / ch-15 / ch-17 / ch-18 / ch-19 age-risk notes.

**Structural change since the previous outline (2026-08-01):** user requested one new chapter to be inserted before the smolagents introduction. The new ch-08 ("How Agents Work: A Toy Agent from Scratch") sits between ch-07 (Call Models Safely from Python) and the old ch-08 (Build a First smolagents Agent, now ch-09). Old ch-09..ch-18 renumber to ch-10..ch-19. The new ch-08 (toy agent) is structural-only — its research entries (entry-191..entry-202) will be added by a dedicated post-outline-confirmation dispatch; the chapter itself does not require any framework claims because everything is plain Python. The new ch-09 (formerly ch-08) now opens with a short "Why Use a Framework" intro that compares the toy agent to smolagents before the framework code appears.

---

Confirmation: user must explicitly confirm this outline before Phase 4 (style/voice) begins. Any structural change after confirmation (chapter added / removed / reordered, dependency edge changed, or any brief-correction listed above overridden by user direction) requires a fresh checkpoint.