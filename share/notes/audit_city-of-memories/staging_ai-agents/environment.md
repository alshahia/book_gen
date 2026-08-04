# Environment — AI Agents with Python

This file records the actual versions installed in the local virtual environment used to test the book's example code. Update this file whenever packages are upgraded or a new chapter's examples are validated.

## Virtual environment

- **Path:** `E:\book_gen\.venv`
- **Prompt:** `ai-agents-book`
- **Python:** `C:\Python313\python.exe` (CPython 3.13.7)
- **Created with:** `uv 0.7.18` (https://github.com/astral-sh/uv)
- **Created on:** 2026-08-01
- **Book context:** workspace-local per user instruction (one venv shared across `E:\book_gen\books\*`).
- **Activation:**
  - Windows PowerShell: `& "E:\book_gen\.venv\Scripts\Activate.ps1"`
  - Windows cmd: `E:\book_gen\.venv\Scripts\activate.bat`
  - macOS/Linux (from `E:\book_gen`): `source .venv/bin/activate`
- **Direct python:** `& "E:\book_gen\.venv\Scripts\python.exe"` (no activation needed for one-off scripts)
- **Install packages:** `uv pip install --python "E:\book_gen\.venv\Scripts\python.exe" <package>`
- **List packages:** `& "E:\book_gen\.venv\Scripts\python.exe" -m pip list`

## Installed package versions (snapshot 2026-08-01)

Installed via `uv pip install` from PyPI:

| Package | Version | Used in chapters | Chub-validated? | Notes |
|---|---|---|---|---|
| `smolagents` | `1.26.0` | ch-08, ch-09, ch-10, ch-11, ch-12, ch-13, ch-14, ch-15, ch-16, ch-17, ch-18 | Yes (but see Version drift below) | API surface differs from 1.24.0 cited in research-log |
| `python-dotenv` | `1.2.2` | ch-02, ch-07 | Yes (research-log ch-02 entry-017, ch-07 entry-052) | Matches research-log exactly |
| `requests` | `2.34.2` | ch-07 | Yes (research-log ch-07 entry-051) | Matches research-log exactly |
| `openai` | `2.52.0` | ch-07, ch-16 | Yes, but research-log cites 2.38.0 | Newer than research-log |
| `anthropic` | `0.120.2` | ch-07, ch-16 | Yes, but research-log cites 0.105.2 | Newer than research-log |
| `huggingface_hub` | `1.26.0` | ch-16 | N/A (forward reference) | For HF Inference API |
| `duckduckgo-search` | `8.1.1` | ch-09 (default smolagents web tool), ch-17, ch-18 | N/A (forward reference) | Default search tool |
| `pytest` | `9.1.1` | ch-13 | N/A (forward reference) | |
| `pytest-asyncio` | `1.4.0` | ch-13 | N/A (forward reference) | For async agent tests |
| `jupyterlab` | `4.6.2` | notebooks (intake) | N/A | Per intake decision (scripts + notebooks) |
| `ipykernel` | `7.3.0` | jupyterlab dep | N/A | |
| `pydantic` | `2.13.4` | transitive (smolagents, openai) | N/A | Pulled in by smolagents + openai |
| `httpx` | `0.28.1` | transitive (smolagents) | N/A | smolagents uses httpx for HTTP |

Total of ~80 transitive packages installed. See `pip list` output for the full set.

## Version drift — smolagents 1.24.0 → 1.26.0

**This is the single most important version note in this file.** The research log cited smolagents `1.24.0` documentation via chub (see ch-01 entry-006). The installed version is `1.26.0`. The following API name changes were detected on import-test (2026-08-01):

### Renamed

- **`HfApiModel` → `ApiModel`** (smolagents 1.26.0). Importing `from smolagents import HfApiModel` raises `ImportError: cannot import name 'HfApiModel' from 'smolagents'. Did you mean: 'ApiModel'?`
  - **Impact:** any chapter example that imports `HfApiModel` (including the ch-08 "first agent" code path) must use `ApiModel` instead.
  - **Action for Phase 6 (chapter writing):** every smolagents model-import example must be regenerated against `1.26.0` before being written into manuscript.
  - **Action for Phase 2 (research):** research-log entry-006 is supplemented by entry-061 (see research-log.md).

### Still present in 1.26.0 (verified 2026-08-01)

Model classes: `ApiModel` (renamed from `HfApiModel`), `InferenceClientModel`, `OpenAIModel`, `AzureOpenAIModel`, `AmazonBedrockModel`, `LiteLLMModel`, `TransformersModel`, `VLLMModel`, `MLXModel`, `OpenAIServerModel`, `AzureOpenAIServerModel`, `AmazonBedrockServerModel`, `LiteLLMRouterModel`.

Agent classes: `CodeAgent`, `ToolCallingAgent`, `MultiStepAgent` — all still present, with expanded constructor parameters (notably `instructions=`, `add_base_tools=`, `managed_agents=`, `planning_interval=`, `provide_run_summary=`, `return_full_result=` on `MultiStepAgent`).

Tools (smolagents built-in): `DuckDuckGoSearchTool`, `GoogleSearchTool`, `VisitWebpageTool`, `WikipediaSearchTool`, `WebSearchTool`, `SpeechToTextTool`, `PythonInterpreterTool`, `FinalAnswerTool`, `UserInputTool`, `ApiWebSearchTool` (new in 1.26.0), `ToolCollection`, `load_tool`.

Helpers: `tool` decorator, `load_dotenv` (re-exported from python-dotenv), `Monitor`, `GradioUI`, `launch_gradio_demo`, `create_agent_gradio_app_template`.

### New constructors relevant to chapters

- `MultiStepAgent(tools, model, ..., instructions=None, max_steps=20, add_base_tools=False, ..., managed_agents=None, ..., planning_interval=None, name=None, description=None, provide_run_summary=False, final_answer_checks=None, return_full_result=False)` — ch-10 (instructions/memory), ch-11 (workflows), ch-15 (multi-agent) will use these.
- `CodeAgent(tools, model, ..., executor_type='local' | 'blaxel' | 'e2b' | 'modal' | 'docker', executor_kwargs=None, ..., use_structured_outputs_internally=False)` — ch-14 (safety) will likely discuss `executor_type='docker'`.

### Other installed-but-newer-than-research-log packages

- `openai` installed `2.52.0`; research-log ch-07 entry-058 cites chub `2.38.0`. Newer minor; API surface for `chat.completions.create` is stable across these versions for beginner use.
- `anthropic` installed `0.120.2`; research-log ch-07 entry-058 cites chub `0.105.2`. Newer minor; `messages.create` API is stable.
- These are noted but not blocking — examples should run unchanged.

## Open issues to flag for the user

1. **`HfApiModel` rename** (above). Phase 6 chapter writer must use `ApiModel` in ch-08 example.
2. **`python` command is broken on this Windows host.** Running `python --version` opens the Microsoft Store. Use `py` or the venv's `Scripts\python.exe` directly. The book examples should not assume `python` is on PATH.
3. **No API keys configured.** The venv is installed and ready, but `OPENAI_API_KEY`, `ANTHROPIC_API_KEY`, `HF_TOKEN` are not set. ch-07's credential-loading examples will load `None` until the user provides keys via `.env`. This is a Phase 6 testing concern; the book should document `.env.example` placeholders rather than real keys.

## Chapter validation status

| Chapter | Examples tested? | Versions used | Last tested |
|---|---|---|---|
| ch-07 | Yes (2026-08-02) | requests 2.34.2, python-dotenv 1.2.2, urllib (stdlib) | 2026-08-02 |
| ch-08 | Pending Phase 6 | smolagents 1.26.0, ApiModel | — |
| (subsequent chapters) | Pending Phase 6 | — | — |

Phase 6 chapter-writing protocol: when a chapter's examples are written, install any new packages into this venv (`uv pip install --python E:\book_gen\.venv\Scripts\python.exe <new-pkg>`), run the example scripts and notebooks inside this venv, and update this file's chapter-validation table with `Yes` + the date + versions used. If anything fails, add a row to "Open issues to flag for the user" rather than silently patching the example.