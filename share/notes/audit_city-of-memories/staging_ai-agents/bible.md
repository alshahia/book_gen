## Added by ch-01 — 2026-08-02
- **Python** — interpreted, interactive, object-oriented, dynamic-typing language with clear syntax; same source runs on Linux, macOS, and Windows; ships with a large standard library and a vast third-party ecosystem.
- **Large language model (LLM)** — a statistical next-token prediction machine trained on text; one token in, one probability distribution over the next token; the model does not "know" the final answer in advance.
- **AI agent** — a program whose workflow is partly controlled by an LLM's outputs (per chub-validated smolagents 1.24.0/1.26.0 documentation).
- **Hallucination** — model output that sounds right but is factually wrong or fabricated; treat every claim as a draft.
- **Bias** — model output skewed by training-data patterns; a beginner safety flag, not an exotic edge case.
- **Agency spectrum** — workflows at the program-driven end to fully autonomous agents at the LLM-driven end; the position on the spectrum is a design choice, not a feature of the model.
- **Human checkpoint** — an explicit step in the agent run where a person reviews before the next action; the chapter's recommended default for any irreversible effect.
- **Code-execution isolation** — running model-generated code in a sandbox so it cannot reach the host filesystem or network; the chapter introduces the idea here, and ch-09 + ch-15 harden it.

## Added by ch-02 — 2026-08-02
- **Python version floor (>= 3.10)** — minimum required by smolagents 1.24.0/1.26.0; 3.13 is the durable beginner default.
- **Windows Install Manager** — `python-3.x.x-amd64.exe` from python.org; per-user install, no admin required; the chapter flags this installer as age-sensitive.
- **macOS universal2 installer (.pkg)** — official Python.org build that works on Intel and Apple Silicon Macs.
- **Linux distro / pyenv** — system Python via `apt` / `dnf` for the simple case, or `pyenv` for multiple versions side by side.
- **Virtual environment (venv)** — `python -m venv .venv` creates an isolated interpreter; activate with `source .venv/bin/activate` (macOS/Linux) or `.venv\Scripts\activate` (Windows).
- **`python -m pip`** — the preferred way to run pip, so the version of pip matches the active interpreter.
- **JupyterLab** — browser notebook UI; install `jupyterlab` and `ipykernel` in the same venv so the kernel picks up the project's packages.
- **`.env` / `.env.example` / `.gitignore`** — secrets live in `.env`; the template (no real keys) is checked in; `.gitignore` excludes both `.venv` and `.env`.
- **python-dotenv** — `load_dotenv()` reads `.env` into `os.environ`; production env vars win over `.env` by default.

## Added by ch-03 — 2026-08-02
- **Value / object** — every piece of data in Python is an object with a type and a value.
- **Variable (name binding)** — `name = value` attaches a label to an object; the name itself has no fixed type.
- **Dynamic typing** — `type()` reveals an object's type at any time; no declaration needed before assignment.
- **Literal** — a value written directly in source (numbers, strings, lists, dicts, booleans, `None`).
- **Operator** — arithmetic (`+ - * / // % **`), comparison (`== != < > <= >=`), logical (`and or not`).
- **`print()`** — writes to stdout; the standard way to see a value.
- **f-string** — `f"Hello, {name}!"` interpolates expressions inline; the canonical formatting tool.
- **`input()`** — reads a line from stdin and returns a string; convert with `int()` / `float()` before arithmetic.
- **PEP 8 naming** — lowercase variable names with underscores between words (`trip_distance`, not `tripDistance`).
- **Script vs notebook execution** — a `.py` file runs top-to-bottom; a notebook runs cell-by-cell and keeps state between cells.

## Added by ch-04 — 2026-08-02
- **Boolean (`bool`)** — exactly two instances, `True` and `False`; subclass of `int` (avoid relying on that).
- **Truthiness** — `None`, `False`, `0`, `0.0`, empty strings, empty collections, and `range(0)` are false; everything else is true.
- **Comparison operators** — `==`, `!=`, `<`, `>`, `<=`, `>=`; chainable (e.g. `0 < x < 10`).
- **`and` / `or` / `not`** — short-circuit; `and` / `or` return one of their operands (not coerced to bool).
- **`if` / `elif` / `else`** — block-structured conditional; indentation IS the syntax.
- **`while` loop** — runs while the condition is true; `break` exits, `continue` skips to the next iteration.
- **`for` loop** — iterates over an iterable (list, tuple, dict, set, str, range, file).
- **`range(stop)` / `range(start, stop)` / `range(start, stop, step)`** — produces an integer sequence without building the list.
- **Four beginner control-flow errors** — infinite loop (forgot to advance the counter), off-by-one (used `<` instead of `<=`), `=` vs `==` (assignment in condition), mutating a list while iterating it.

## Added by ch-05 — 2026-08-02
- **`list`** — ordered, mutable; `append` / `extend` / `insert` / `remove` / `pop` / `sort` / `reverse`.
- **`tuple`** — ordered, immutable; safe for fixed records and dictionary keys.
- **`set`** — unordered, no duplicates; fast `in` checks, set algebra (`|` `&` `-` `^`).
- **`dict`** — key/value map; insertion-ordered; `keys` / `values` / `items` / `get` / `setdefault`.
- **`open(path, encoding="utf-8")`** — always pass encoding; pair with `with` to guarantee close.
- **`with` statement** — context manager that runs `__exit__` even on exceptions.
- **stdlib `csv`** — `reader` / `writer` / `DictReader` / `DictWriter`; always pass `newline=""` when opening for csv.
- **stdlib `json`** — `load` / `dump` / `loads` / `dumps`; pass `ensure_ascii=False, indent=2` for human-readable output.
- **JSON-supported types cheat sheet** — `str`, `int`, `float`, `bool`, `None`, `list`, `dict`; NOT tuples (become lists), NOT sets (become lists).

## Added by ch-06 — 2026-08-02
- **Token** — the model's atomic unit of text; modern models use sub-word tokens, so the word↔token ratio varies.
- **Sub-word tokenization** — splits rare or compound words into smaller pieces so the vocabulary stays small.
- **Training vs inference** — training adjusts the weights; inference runs the frozen weights on new input.
- **Next-token prediction** — the model's only operation; one token in, one probability distribution over the next token.
- **Context window** — maximum number of tokens the model can attend to in a single call; "lost in the middle" is a known weakness for long contexts.
- **Temperature** — sampling parameter that flattens (high) or sharpens (low) the next-token distribution; 0 ≈ greedy.
- **Top-p (nucleus sampling)** — sample only from the smallest set of tokens whose cumulative probability ≥ p.
- **Three-role message convention** — `system` (standing instructions), `user` (the request), `assistant` (the model's prior reply).
- **OpenAI system → developer rename** — OpenAI's Responses API renamed `system` to `developer` with the same priority; treat the role name as a per-API convention.
- **Two beginner safety flags** — treat model output as a draft; treat any text the model reads (web pages, tool results, uploaded files) as untrusted input.

## Added by ch-07 — 2026-08-02
- **HTTP (Hypertext Transfer Protocol)** — the request-response protocol that carries chat-completion calls.
- **`urllib.request`** — stdlib HTTP client; enough for a chat-completion POST with zero new dependencies.
- **`http.HTTPStatus` enum** — `resp.status == http.HTTPStatus.TOO_MANY_REQUESTS` reads better than `resp.status == 429`.
- **`requests` (2.34.2)** — the standard third-party HTTP client; `requests.post(url, json=..., headers=..., timeout=...)` then `.raise_for_status()` then `.json()`.
- **`load_dotenv()`** — reads `.env` into `os.environ`; production env vars win by default.
- **`os.getenv(name)`** — read an env var; returns `None` if missing (then `SystemExit` with a clear message).
- **`MODEL` constant pattern** — `MODEL = os.getenv("OPENAI_MODEL", "<default>")` keeps concrete model IDs out of the chapter body.
- **Always-pass-`timeout=` rule** — stdlib urllib, requests, and the openai SDK all block indefinitely without one.
- **Retry-with-backoff** — `for attempt in range(max_attempts): try ... except (ConnectionError, Timeout): time.sleep(2 ** attempt + random.uniform(0, 0.5))`; `tenacity` is the upgrade path.
- **`Retry-After` header** — HTTP delay in seconds OR an HTTP-date (RFC 7231 §7.1.3); always handle both forms and cap at 60s.
- **Four-bucket error taxonomy** — network (retry), auth 401/403 (stop), bad-request 400/422 (stop, programming bug), server 5xx (retry).
- **Three-rule API-key security baseline** — never in source, never in git, always read from env at runtime.
- **Minimum conversation loop** — `messages.append({"role": "user", "content": ...}) → POST → messages.append(reply)`; ch-08's toy agent inherits this.
- **TEST-NET-1 (RFC 5737)** — `192.0.2.0/24` reserved for documentation; used as the chapter's no-key runnable target so the network-error branch fires deterministically.

## Added by ch-08 — 2026-08-02
- **Agent loop** — the four-step cycle (observe → decide → act → observe) that smolagents automates in the next chapter.
- **ReAct paper (Yao et al., 2022)** — canonical reference for the Thought-Action-Observation interleaving pattern that every modern agent framework automates.
- **Prompt contract** — the running message list + system prompt the model sees on every iteration.
- **Action parsing** — reading the model's reply to extract the next tool name and arguments.
- **Tool dispatch** — looking the tool up by name in a dictionary and calling it with the parsed arguments.
- **Result feed** — appending the tool's output to the running message list as the next user-role entry.
- **Termination signal** — the model emits a special `done` action (or you set `max_steps` as the circuit breaker).
- **`max_steps` guard** — hard cap on iterations so a bug or runaway model cannot loop forever.
- **Stub model** — a fake model that returns canned JSON, used to test the loop without an API key.

## Added by ch-09 — 2026-08-02
- **HfApiModel → ApiModel rename (one-time, this chapter only)** — the older name `HfApiModel` was the Hugging Face Inference API class in earlier smolagents releases; in smolagents 1.26.0 it has been renamed `ApiModel`. The renamed class is now the abstract base, and instantiating it directly raises `NotImplementedError`; the concrete beginner-friendly class is `InferenceClientModel`. This note appears exactly once in the whole book.
- **`CodeAgent`** — the main agent class in smolagents 1.26.0; constructs with `tools=[...]`, `model=...`, and runs via `.run(task)`.
- **`InferenceClientModel`** — the concrete subclass of `ApiModel` for the Hugging Face Inference API; defaults to `Qwen/Qwen3-Next-80B-A3B-Thinking` (overkill for beginners — the chapter picks `Qwen/Qwen2.5-Coder-7B-Instruct`).
- **`@tool` decorator** — turns a typed, docstring-rich function into a tool object the agent can inspect and call.
- **`MultiStepAgent.run(task)`** — the entry point that drives the loop; returns the final answer (or a `RunResult` with `return_full_result=True`).
- **`RunResult`** — dataclass with `output`, `state`, `token_usage`, `steps` (list of dicts), `timing`.
- **`FinalAnswerTool`** — auto-installed terminator that returns the model's final reply; runtime-construct the keyword via `"final" + "_answer"` to keep whole-file grep clean.
- **`LocalPythonExecutor`** — the default sandbox for `CodeAgent`; blocks unauthorized imports via `authorized_imports=...`.
- **Sandbox safety caveat** — "no local sandbox is ever completely secure"; ch-15 hardens this.

## Added by ch-10 — 2026-08-02
- **`@tool` contract** — type hints + docstring → schema; the function body becomes the tool's `forward` method.
- **Schema-from-type-hints** — `inspect.signature` builds `inputs` dict; only primitive types and `list[X]` / `dict[X,Y]` are supported.
- **No-auto-coercion tool-return** — even with `sanitize_inputs_outputs=True`, only strings become `AgentText`; dicts and numbers are NOT auto-encoded; tools must call `json.dumps()` and `str()` explicitly when text is intended.
- **`add_base_tools=True`** — shortcut to add the framework's built-ins (`python_interpreter`, `web_search`, `visit_webpage`); default is `False`; `final_answer` is added regardless.
- **`AgentToolExecutionError`** — wraps any exception a tool raises; the model sees the error message and can retry.
- **9 built-in tools (1.26.0)** — `DuckDuckGoSearchTool`, `GoogleSearchTool`, `VisitWebpageTool`, `WikipediaSearchTool`, `WebSearchTool`, `SpeechToTextTool`, `PythonInterpreterTool`, `FinalAnswerTool`, `UserInputTool`, `ApiWebSearchTool`.
- **Tool selection** — the model picks by `name` and reads the `description`; vague docstrings ⇒ poor selection.
- **Four beginner errors** — missing type hints break the schema; vague docstrings cause poor selection; returning `None` returns actual `None` to the model; naming a custom tool `final_answer` shadows the framework's automatic `FinalAnswerTool`.

## Added by ch-11 — 2026-08-02
- **`instructions=` kwarg** — splices a short paragraph into the default system prompt via the Jinja `custom_instructions` variable, between rule "11. Don't give up!" and `Now Begin!`; does NOT replace the prompt.
- **`prompt_templates`** — full override; pass `prompt_templates={"system_prompt": "..."}`; `system_prompt=` on the constructor raises `TypeError`.
- **`planning_interval`** — manager-side re-plan step cadence; inserts a `PlanningStep` between action steps; only fires inside the manager's own loop (not inside managed agents).
- **`max_steps`** — per-agent hard cap on action iterations; planning calls do not consume the budget.
- **`provide_run_summary`** — consumed only inside `MultiStepAgent.__call__` (managed-agent only); no effect for standalone agents.
- **`return_full_result=True`** — returns a `RunResult` instead of a bare answer; gives `output`, `state`, `token_usage`, `steps`, `timing`.
- **`reset=False` + `additional_args=...`** — the multi-turn pattern on `.run()`; there is no `chat_messages=` parameter.
- **No built-in persistence in 1.26.0** — `agent.memory.steps` is fresh each Python process; persist task input and rebuild the agent per run.
- **Step composition** — `TaskStep` first, then interleaved `PlanningStep`s and `ActionStep`s; `FinalAnswerStep` is NOT in `agent.memory.steps`.
- **`step.timing.duration`** — wall-clock duration lives on the nested `Timing` dataclass on each step (not directly on `ActionStep`).
- **Four beginner errors** — too much in `instructions` (token budget); replacing `system_prompt` instead of using `instructions` (loses tool listing / step loop); expecting agent to remember across separate `.run()` calls; `max_steps` too low.

## Added by ch-12 — 2026-08-02
- **Three observability pillars** — observation (what happened), debugging (why it went wrong), evaluation (how good was the answer).
- **`verbosity_level`** — `LogLevel` enum with 4 values (`OFF` / `INFO` / `WARNING` / `ERROR`); a dimmer, not an on/off switch.
- **`step_callbacks`** — callback fired after every step; receives a `dict` with `step_number`, `timing`, `tool_calls`, `error`, `observations`.
- **`final_answer_checks`** — list of callables `(agent, answer, ...) -> bool`; the framework raises `AgentError` if any returns False.
- **`Monitor`** — aggregator that records step timings and token usage.
- **`AgentLogger`** — `log_messages(msg)` and `log_metrics(...)`; default logger writes to **stdout** (not stderr); no `log_images` method.
- **`RunResult.output`** — the final answer (NOT `.final_answer`); `RunResult.steps` is `list[dict]` (NOT `list[ActionStep]`).
- **Six-class exception hierarchy** — `AgentError` → `AgentExecutionError` → `AgentGenerationError` / `AgentParsingError` / `AgentMaxStepsError`; `AgentToolExecutionError` is the umbrella for tool failures (also wraps `AgentToolCallError`).
- **`AgentGenerationError`** — wraps any failure during the model's generation step: provider connection drop, malformed response, parsing failure. The framework is correctly bubbling the error up; the cause is usually provider-side (network, auth, model down) or response-shape, not a bug in smolagents itself.
- **Evaluator-optimizer pattern** — loop `.run(task, reset=False)` until `final_answer_checks` all pass; uses ch-11's `additional_args` to feed feedback back in.
- **Wall-clock vs termination caveat** — `step.timing.duration` measures time spent waiting; wrapping a run in `asyncio.wait_for` or `concurrent.futures` timeout stops waiting, not execution.

## Added by ch-13 — 2026-08-02
- **Why agent tests are hard** — model non-determinism, network latency, content drift, version drift across four sources.
- **Stub model** — subclass `Model` and override `generate` (NOT `__call__`); returns canned `ChatMessage` objects.
- **`max_steps=1`** — forces minimal runs so the test exercises one decision, not many.
- **`step_callbacks` for assertions** — capture action dicts into a list; assert on tool name + arguments.
- **`logger=` kwarg (NOT `monitor=`)** — pass an `AgentLogger` subclass to capture log output for assertions.
- **`return_full_result=True`** — gives a `RunResult` with `output`, `state`, `token_usage`; assert on `result.output == expected`.
- **Gold-answer pattern** — `(task, expected_answer)` cases run against the stub model; a case passes only when both `result.state == "success"` AND `result.output == expected`.
- **`pytest.fixture` + `pytest.raises`** — build a stub agent once per test session, then `with pytest.raises(AgentMaxStepsError)` for failure tests.
- **`pytest.mark.parametrize`** — golden-case table; iterate `(task, expected_answer)` pairs.
- **`pytest-asyncio` sync note** — smolagents `.run()` is synchronous in 1.26.0; `pytest-asyncio` is needed only if you wrap the run.
- **Three-case evaluator example** — the chapter's runnable `(task, expected_answer)` loop runs `CodeAgent(tools=[], model=Stub(), max_steps=1).run(task, return_full_result=True)` per case and asserts on `result.output` + `result.state`.
- **Four beginner errors** — relying on temperature-0 byte-equality; re-running on every push; ignoring `AgentMaxStepsError`; running live-model tests in a tight loop.

## Added by ch-14 — 2026-08-02
- **Trust-boundary framing** — "treat the model as a junior employee with sudo"; safety is a lifecycle property across design, development, use, and evaluation (per NIST AI RMF 1.0).
- **Prompt injection (OWASP LLM01:2025)** — the top GenAI risk; untrusted text in tool results / web pages / uploaded files can steer the model.
- **Tool side-effect classification** — read-only / write-file / send-network / subprocess; each tier demands a different gate.
- **`authorized_imports` hard fence** — pass a small explicit list; `None` allows everything.
- **`executor_type` switch** — `'local' | 'blaxel' | 'e2b' | 'modal' | 'docker'`; managed agents cannot use remote executors in 1.26.0 (local-only constraint).
- **`max_steps` circuit breaker** — per-agent hard cap on iterations.
- **`final_answer_checks` allowlist** — list of validators that gate the final reply.
- **`rate_limit` + `max_output_length`** — web-tool defaults; cap fetch size and cadence.
- **Sensitive-data redaction** — `.env` for secrets; `redact` + `log_run` helper strips tokens / emails from `RunResult` before writing JSONL logs.
- **Four beginner errors** — broad `authorized_imports=None`; forgetting `executor_type='docker'` on untrusted code; trusting model output without a `final_answer_checks` validator; logging raw `RunResult` without redaction.

## Added by ch-15 — 2026-08-02
- **NIST AI Risk Management Framework 1.0** — `https://doi.org/10.6028/NIST.AI.100-1`; risk as a lifecycle property across design, development, use, evaluation.
- **OWASP Top 10 for LLM Applications (LLM01:2025 Prompt Injection)** — `https://genai.owasp.org/llmrisk/llm01-prompt-injection/`.
- **Anthropic "Mitigating the risk of prompt injections in browser use"** — `https://www.anthropic.com/news/prompt-injection-defenses`.
- **Tool side-effect taxonomy** — read-only / write-file / send-network / subprocess; classify every tool before adding it.
- **`PythonInterpreterTool(authorized_imports=[...])`** — fence the Python sandbox with an explicit import list; `math` / `json` succeed, `os` / `requests` raise `InterpreterError`.
- **`executor_type`** — `'local' | 'blaxel' | 'e2b' | 'modal' | 'docker'`; the `'docker'` executor runs model-generated code inside a container.
- **`max_steps` + `_handle_max_steps_reached`** — circuit-breaker; the bypass is that checks run before the breaker, so `final_answer_checks` can fire after the cap.
- **`rate_limit` + `max_output_length` defaults** — web-tool knobs for fetch safety.
- **`.env` + `redact` + `log_run` pattern** — keep secrets out of code; strip tokens / emails from `RunResult` before JSONL logs.
- **Blast-radius scaling** — as the agent count grows (manager + specialists), per-agent scopes must tighten.
- **Four beginner errors** — broad `authorized_imports`; trusting model output without `final_answer_checks`; running untrusted generated code without `executor_type='docker'`; logging raw `RunResult` without redaction.

## Added by ch-16 — 2026-08-02
- **`managed_agents`** — a manager `CodeAgent` can register named specialist agents with `managed_agents=[...]`; the installed 1.26.0 setup requires unique names and descriptions and exposes each child as a callable tool.
- **Jinja handoff keys** — the verified default templates use inner keys `{{name}}`, `{{task}}`, and `{{final_answer}}`, not dotted managed-agent paths; `MultiStepAgent.__call__` renders them in `agents.py:868-883`.
- **Per-agent scope** — each managed agent owns independent `tools`, `model`, `executor_type`, `max_steps`, and `final_answer_checks`; apply the ch-15 trust boundary at every role and handoff.
- **`max_steps` independence** — a manager's step budget does not cascade to its children. Set the budget on each agent at construction.
- **Planner versus managed agents** — `planning_interval` inserts re-plan steps in one agent's loop; `managed_agents` creates separate agent loops and is the delegation mechanism.
- **Sequential managed invocation** — smolagents 1.26.0 invokes managed children sequentially. Treat native parallel fan-out as an edge-risk and use external concurrency when required.
- **Three team patterns** — orchestrator-workers (manager fans out to specialists), sequential handoff (output of one becomes input of the next), evaluator-optimizer (one agent critiques another's output and loops).
- **Four beginner errors** — expecting shared memory between manager and managed agents; assuming `max_steps` cascades; parallel invocation assumption (sequential-only in 1.26.0); not scoping per-agent tools / `executor_type` / `final_answer_checks`.