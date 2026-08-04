# Style Guide — AI Agents with Python

Status: DRAFT

This style guide governs Phase 5 (writing) for *AI Agents with Python*. Every chapter must follow both Presentation and Voice below. It is bound by the confirmed intake, the confirmed outline (19 chapters, structural change since 2026-08-01), the bible, and the research-log. It is the writer's primary reference for tone, code conventions, and the corrected technical claims the verified 1.26.0 runtime requires.

---

## Presentation

### Chapter length and rhythm

The book is **19 chapters × ~17–22 pages each** (~300+ pages total). The skeleton now installs a toy-agent chapter (new ch-08) before the framework introduction, and the chapter rhythm respects the dependency chain in `outline.md` exactly.

- **~17–22 pages per chapter** is intentional. Long enough to install one concrete move with its evidence and tradeoffs; short enough that a beginner can read a chapter in one sitting and execute the move the same day. A chapter that lands under ~12 pages is doing less than the outline asks of it; one that runs over ~28 pages is probably trying to install two moves.
- **Chapter 1 is independent.** It can be read first and requires no prior chapter. Its move (the mental model of Python, language models, and AI agents) is the foundation every later chapter rests on.
- **Chapters 2–7 form a linear chain** (workspace → Python fundamentals → language models → API calls). Each later chapter's concrete move depends on the prior chapter's installed element.
- **Chapter 8 is structural.** It is the new "How Agents Work: A Toy Agent from Scratch" chapter — a 30-line plain-Python agent loop that the framework introduction in ch-09 lands on. **ch-08 is plain Python only. No smolagents, no `@tool`, no `CodeAgent`, no `final_answer`** — these are introduced in ch-09.
- **Chapter 9 opens with a "Why Use a Framework" intro.** This intro compares the ch-08 toy agent to smolagents before the framework code appears. The intro must name the **four things smolagents automates** (the action parser, the dispatch table, the step loop, the final-answer termination) and the **three things it adds** (typed schemas, retry-able step errors, agent-aware tool errors). The intro lands on a concrete mental model rather than abstract magic.
- **Chapters 9–19 form the framework chain.** Each later chapter's concrete move depends on one or two prior chapters' installed elements, per the outline's `depends_on` field.
- **Internal rhythm.** Each chapter alternates between explanation and concrete moves at roughly 2:1 prose-to-instruction. No chapter is a pure recitation of evidence, and no chapter is a pure checklist. The closing 10–15% of every chapter is dedicated to the reader-facing action (see "Outcome lines → reader-facing actions" below).

### Structural devices

**Subheadings.** Frequent. A chapter should be scannable in 30 seconds. Subheadings carry the navigational load; the reader should always be able to answer "what is this paragraph about?" by reading the subheading two lines up. Subheadings are sentence-fragment style, not full sentences, and they describe the *move* the section installs, not the topic being discussed ("Parse the action, dispatch the tool" not "Tool dispatch").

**Lists.** Sparingly. Lists are for items the reader is expected to *do* in sequence or to enumerate as a discrete set (the four beginner error categories in ch-03, the four-step agent loop in ch-08, the four-knob safety hardening in ch-18). Bulleted prose — paragraphs that have been converted into bullets because the author lost the patience to write them — is not.

**Callouts.** Yes, but only one kind per chapter, and used at most twice per chapter. Two recurring callout types:

1. **"The move"** — a single boxed sentence stating the chapter's concrete action in imperative form. Appears once, near the end of the chapter, immediately before the closing.
2. **"Verified behavior vs. assumption"** — a short boxed distinction used when the chapter is documenting a behavior that *looks like* an assumption but was verified against installed smolagents==1.26.0 source. This callout names the assumption the writer might be tempted to make, names what the verified source actually does, and tells the reader the source is canonical. See the three brief-corrections and the eighteen brief-corrections noted in the outline.

No other callout types. No "pro tip" boxes. No "war story" boxes. No "common mistakes" boxes. If the writer wants to break the rule, escalate to master first.

**Chapter-opening convention.** Every chapter opens with a concrete scene — a tool the reader is about to use, a question the reader is about to face, a small physical detail (terminal prompt, error trace, browser tab) — that anchors the *problem* the chapter solves. Not a thesis statement. Not a chapter summary. A scene.

**Chapter-closing convention.** Every chapter closes with **one concrete action the reader takes the same day they finish reading**. The action is the chapter's outcome line from the outline, surfaced verbatim or near-verbatim as the final imperative line. No "in this chapter we explored..." closings. No "tomorrow, try this..." closings that defer the action.

**Reading aids.** A short end-of-chapter "What's next" note (one or two sentences) is permitted in chapters 2–18 to bridge to the next chapter's dependency. Chapter 1 has no such note (it is independent). Chapter 19 has no "What's next" (it closes the book).

### Code blocks

Every code snippet must satisfy **all four rules** below. A reviewer will fail any chapter whose code blocks violate them.

1. **Runnable in the venv.** Every snippet must run in `E:\book_gen\.venv\Scripts\python.exe` on Windows or the platform-equivalent `python` from the book's `.venv` on macOS/Linux. The book instructs the reader to invoke the venv's interpreter explicitly; the prose never relies on a bare `python` being on `PATH`. Cross-platform activation lines from ch-02 are reused.
2. **PEP 8.** Four-space indent. `snake_case` for functions and variables. `PascalCase` for classes. One space around operators. One blank line between top-level definitions. The beginner subset is taught in ch-03 and held through ch-19.
3. **`if __name__ == "__main__":` for project scripts.** Every runnable project (ch-17, ch-18, ch-19) wraps its top-level code in this guard. Notebooks in early chapters use top-level cells and do not require the guard.
4. **Test before writing.** The writer must run every snippet in the venv before committing the chapter prose. A broken example is a chapter-killer; the reviewer will fail the chapter and the writer rewrites until the snippet runs.

Code blocks are fenced with triple backticks and carry a language tag (`python`, `bash`, `text`, `dotenv`). Inline code is fenced with single backticks. Imports are grouped (stdlib, third-party, local) and separated by blank lines.

### Runnable checks

Each chapter (except ch-01, which is conceptual-only and pre-runtime) installs at least one **runnable check** — a 5–20 line snippet the reader copies, runs, and observes the expected output from. The check is the smallest concrete demonstration of the chapter's move.

- **Chapter rhythm with checks.** The check appears at the end of the first half of the chapter, after the move has been explained and before the closing action. The check uses real files (not print-only output where avoidable) so the reader builds muscle memory with the venv.
- **Check style.** Short header naming the check (e.g., "Check: a tool returns its input"). The body is the snippet. The expected output is shown in a fenced block immediately below. No `assert`-free style; the check must fail loudly if the snippet is wrong.
- **Capstone checks.** ch-17, ch-18, ch-19 replace the inline check with a full project walkthrough whose end-state is a working `src/` directory plus a passing `pytest` run.

### Outcome lines → reader-facing actions

The outline gives each chapter an outcome line. The style guide treats those outcome lines as the binding contract for what the chapter's closing action must be. The writer may not substitute a "richer" action, a "more interesting" action, or a "deeper" action in place of the outcome line. The action is the point.

| Chapter | Outcome line (from outline) | Reader-facing action the closing must deliver |
|---|---|---|
| ch-01 | Describe Python, LLMs, AI agents, and why agent output is a draft. | Reader writes a one-paragraph explanation in their own words of what an AI agent is and why the model's output must be reviewed before any action runs on it. |
| ch-02 | Working Python 3.10+ `.venv` with smolagents and JupyterLab, `.gitignore`, `.env.example`. | Reader runs the four cross-platform install steps in the book's `.venv` and confirms `python -c "import smolagents; print(smolagents.__version__)"` prints `1.26.0`. |
| ch-03 | Write, save, run a script with values, variables, `input()`, `print()`, f-strings, four error categories. | Reader writes the chapter's first-program snippet, runs it in the venv, observes the printed output, and fixes one traceback from the bottom up. |
| ch-04 | Programs with `if`/`elif`/`else`, `while`/`for`, `range()`, the four control-flow errors. | Reader writes a small loop that uses one `if`, one `while`, and one `for`; runs it; identifies one control-flow error if present. |
| ch-05 | Lists/tuples/sets/dicts; `open()` with `encoding="utf-8"`; CSV/JSON with stdlib. | Reader reads a small CSV and writes a JSON file from it using `with open(..., encoding="utf-8")`. |
| ch-06 | Next-token-prediction loop, context window, system/user/assistant role, two safety flags. | Reader writes a one-page plain-language explanation of what a context window is and why the model's output is a draft. |
| ch-07 | POST a chat-completion with `HF_TOKEN`/`OPENAI_API_KEY`, timeout, retries, four-bucket errors. | Reader runs the chapter's retry-with-backoff snippet against a real provider API; sees one 429 retry; sees one final success. |
| ch-08 | A 30-line plain-Python toy agent that prompts, parses, dispatches, feeds back, terminates. **Plain Python only. No smolagents, no `@tool`, no `CodeAgent`, no `final_answer`.** | Reader runs the toy agent with a stub model on a tiny task; observes the loop iterate and the termination message. |
| ch-09 | A `CodeAgent` with one or two `@tool` functions, `.run(task)`, optional `RunResult`. Opens with the **"Why Use a Framework" intro** naming the four automations and the three additions. Includes the **one-time `HfApiModel` → `ApiModel` naming sidebar** (literal `HfApiModel` appears here exactly once in the entire book). | Reader runs the offline stub-model demo and the chapter's first live `CodeAgent`; observes one tool call and the final answer. |
| ch-10 | Typed, docstring-rich `@tool` with verified no-auto-coercion returns. | Reader writes one `@tool` returning a string and one returning a dict (without `json.dumps`), observes that the dict is preserved as-is (no auto-coercion) and the string becomes `AgentText` under `sanitize_inputs_outputs=True`. |
| ch-11 | `instructions`, `planning_interval`, `max_steps`, `reset=`, `return_full_result=`. | Reader configures an agent with a custom `instructions` paragraph and `planning_interval=2`; runs a 3-step task; inspects `RunResult.steps`. |
| ch-12 | `managed_agents`, `step_callbacks`, `final_answer_checks`, six-class exception hierarchy. | Reader builds a manager-plus-one-specialist shape with `step_callbacks` capturing every step; runs one task; inspects the captured steps. |
| ch-13 | Observe (`step_callbacks`), debug (six-class exceptions), evaluate (`(task, expected_answer)`). | Reader runs the chapter's three-case evaluator over three stub tasks; inspects `RunResult.output` and `RunResult.token_usage`. |
| ch-14 | pytest with stub model (`Model` subclass, `generate` override), `max_steps=1`, `return_full_result=True`, `logger=` `AgentLogger`, gold-answer tests. | Reader runs `pytest` on the chapter's stub-model test suite; observes all green. |
| ch-15 | Tool side-effect classification, `authorized_imports=`, `executor_type=`, `max_steps=`, `final_answer_checks=`, secrets redaction. | Reader configures an agent with `executor_type="local"`, `authorized_imports=["requests"]`, two `final_answer_checks`; runs one task; observes the final answer pass both checks. |
| ch-16 | Manager `CodeAgent` with `managed_agents=[...]`, `additional_args` for explicit context, per-agent scopes, **Jinja handoff with inner keys `{{name}}`, `{{task}}`, `{{final_answer}}`** (NOT nested paths). | Reader runs the two-managed-agent handoff with the verified Jinja keys; observes the inner template render correctly. |
| ch-17 | Pick from the **fourteen-name** 1.26.0 model surface; **two-level hierarchy `Model` → `ApiModel`** (local classes extend `Model` directly); `*ServerModel` for OpenAI-compatible endpoints; factory function. | Reader writes a 10-line `pick_model(name: str)` factory that returns `OpenAIModel` / `InferenceClientModel` / `LiteLLMModel` based on a config string; calls it twice with different inputs. |
| ch-18 | `src/research_briefing/` project: topic → 200–400 word briefing, 3–5 cited URLs, `max_steps=15`, two `final_answer_checks`, `rate_limit=2.0`, `max_output_length=10000`, three-layer tests, JSONL trace. | Reader runs `python -m research_briefing --topic "..."` from the `src/` layout; observes a briefing with a `Sources:` line; runs `pytest -m smoke`, `pytest -m gold`, `pytest -m live`. |
| ch-19 | `src/work_assistant/` capstone: manager + researcher + writer + reviewer, per-agent `model`, per-agent JSONL logs, reviewer-as-evaluator-optimizer loop, three-layer tests. | Reader runs the capstone CLI with a free-text request; observes the four-agent trace in the JSONL logs; runs all three test layers green. |

The chapter does not need to *prove* the reader did the action — the book is not a quiz. But the closing must be specific enough that the reader could not confuse it with general advice.

### Special framing for new ch-08 and ch-09

**ch-08 (Toy Agent) — plain Python only.** This chapter is a deliberate digression from the framework. The chapter deliberately does NOT use:

- `import smolagents` (or any smolagents import)
- `@tool` (or any decorator)
- `CodeAgent` (or any agent class)
- `final_answer` (or any framework terminator)

Everything is stdlib + the `requests` library already installed in ch-07. The chapter builds the agent loop from scratch so the next chapter's framework introduction lands on a concrete mental model.

**ch-09 — opens with "Why Use a Framework".** Before any smolagents code appears, the chapter includes a 1–2 page intro that compares the ch-08 toy agent to smolagents. The intro names:

- **Four things smolagents automates** (already present in ch-08's loop, smolagents packages them):
  1. The action parser (extract the structured action from the model's text)
  2. The dispatch table (route the action to the right `@tool` by name)
  3. The step loop (iterate observe → decide → act → observe)
  4. The final-answer termination (stop when `final_answer` is called)
- **Three things it adds** (ch-08 did not have):
  1. Typed schemas (parameters and return types enforced at the tool boundary)
  2. Retry-able step errors (parse failures and tool errors surface as structured exceptions the agent can react to)
  3. Agent-aware tool errors (`AgentToolExecutionError` carries the failing call's metadata)

After this intro, the chapter moves to the canonical `CodeAgent` + `InferenceClientModel` construction.

### Pinning rules (smolagents==1.26.0 — verified 2026-08-01)

The book targets **smolagents==1.26.0** specifically, verified against installed source at `E:\book_gen\.venv\Lib\site-packages\smolagents\`. Writers must not assume a different version. When the prose mentions a version, it says "1.26.0," not "current" or "latest."

**One-time naming-note sidebar in ch-09.** Research-log entry-061 records the corrective: the older class name `HfApiModel` was renamed to `ApiModel` in current smolagents, and the literal `HfApiModel` string appears in the entire book **EXACTLY ONCE** — in the ch-09 sidebar that documents the rename. The sidebar exists so the writer can orient a reader who searched the web and saw the older name. It is the only place in the book where `HfApiModel` is permitted. If a writer finds themselves writing `HfApiModel` anywhere else, it is a bug.

**Beginner path uses `InferenceClientModel`, not `ApiModel`.** The quickstart code in ch-09 (and the beginner-chapter examples through ch-16) instantiates `InferenceClientModel(model_id="...", token=os.getenv("HF_TOKEN"))` — the concrete class. `ApiModel` is the abstract subclass introduced conceptually in ch-17's two-level hierarchy discussion. Beginners never need to subclass `ApiModel` directly.

### Three brief-corrections the writer must follow

These three corrections are binding. The reviewer will fail any chapter that violates them.

**Brief-correction 1 (ch-10, entry-077) — tools do NOT auto-coerce returns.** Verified 1.26.0 behavior: a `@tool` returning a `dict` returns a `dict` to the agent (no silent `json.dumps`). A `@tool` returning a `str` returns a string; under `sanitize_inputs_outputs=True`, the string is wrapped in `AgentText` for sanitization purposes, but the underlying type is preserved. The chapter teaches explicit `json.dumps(...)` when the agent needs a JSON string and explicit `str(...)` when the agent needs a stringified value. The chapter does NOT teach "the framework serializes your dict for you."

**Brief-correction 2 (ch-15, entry-145) — Jinja handoff keys are inner names, not nested paths.** Verified 1.26.0 behavior: the managed-agent task prompt template uses inner Jinja names `{{name}}` and `{{task}}`. The managed-agent report template uses `{{name}}` and `{{final_answer}}`. These are inner template variables; they are NOT nested paths like `{{managed_agent.task}}` or `{{managed_agent.report}}`. The chapter documents the verified form. Any prose that says "the framework exposes the managed agent's task as `{{managed_agent.task}}`" is wrong.

**Brief-correction 3 (ch-16, entry-155) — two-level `Model` / `ApiModel` hierarchy.** Verified 1.26.0 class structure:

- `Model` is the abstract base.
- `ApiModel` is the abstract API-backed subclass (inherits from `Model`).
- The three local-runtime classes (`TransformersModel`, `VLLMModel`, `MLXModel`) extend `Model` **directly**, because they do not own an HTTP client.
- All other public classes (`InferenceClientModel`, `OpenAIModel`, `AzureOpenAIModel`, `AmazonBedrockModel`, `LiteLLMModel`, `LiteLLMRouterModel`, `OpenAIServerModel`, `AmazonBedrockServerModel`, `AzureOpenAIServerModel`) extend `ApiModel`.

The chapter documents this hierarchy as a small ASCII tree. Any prose that says "local classes extend `ApiModel`" is wrong.

### 25 inline age-risks kept directional

The outline flags 25 inline items that age quickly. The writer must keep them **directional**, not commit to exact figures. The mapping below is binding — the prose must use the directional phrasing, not the literal identifier or version.

| Age-risk category | Concrete identifier the prose must NOT use | Directional phrasing the prose MUST use |
|---|---|---|
| OpenAI / Anthropic / Hugging Face model names | "gpt-4o-mini," "claude-3-5-sonnet," "Qwen/Qwen2.5-Coder-7B-Instruct" (specific identifiers) | "a small OpenAI model," "a small Anthropic model," "a small Hugging Face model" |
| API version numbers | "openai>=1.50," "anthropic>=0.30," "huggingface-hub>=0.20" (specific version pins) | "the current `openai` SDK," "the current `anthropic` SDK," "the current `huggingface-hub` package" |
| Rate-limit units | "10 requests per minute," "60 RPM" (specific numbers) | "the configured delay," "the provider's rate limit," "the rate-limit setting on the web tool" |
| Context-window sizes | "128k tokens," "200k context" (specific sizes) | "the model's context window," "a typical modern context window," "the configured context window" |
| Executor-type names | "executor_type='docker'", "executor_type='e2b'" (specific executor names beyond what's verified for 1.26.0) | "the supported execution backends," "the configured executor," "the sandbox executor you have access to" |
| Per-model defaults | "default temperature=0.7," "default top_p=0.9" (specific per-model defaults) | "the model's default sampling settings," "the default the provider picks," "a small Hugging Face model" |
| OS install paths | "brew install python," "choco install python," "apt install python3.10" (specific package-manager commands beyond ch-02's cross-platform baseline) | "the platform-specific installer," "your distribution's package manager," "the standard installer for your platform" |

This rule keeps the prose correct on re-read six months from now, when the identifiers and numbers above will have shifted. The book's value is the framework shape and the patterns, not the version pins.

---

## Voice

### Formality level

**Conversational technical.** Like a senior engineer teaching a junior — not a coach hyping a transformation, not an academic hedging a position. The reader is a complete beginner and the book talks to them as a peer who has not yet seen the material.

- Contractions yes ("you've," "don't," "isn't," "won't"). Feels human, not lecture-y.
- No exclamation marks. The book is not enthusiastic. The book is confident.
- No second-person cheerleading ("you've got this," "trust the process," "you're going to love this"). The reader is a peer, not a client.
- No academic hedging clichés ("it could be argued that," "some scholars suggest"). Either cite the scholar by name and the year, or don't cite.
- No productivity jargon from outside the technical register. Avoid: "synergy," "leverage" (as a verb), "optimize" (used generally), "deep dive," "unpack." Permit: "the agent," "the tool," "the model," "the step," "the run," "the framework," "the prompt."

### Person

**Second person, dominant.** Direct address to the reader as the practitioner. "You write a `@tool` function" — not "the practitioner writes a `@tool` function" or "we write a `@tool` function." First-person plural ("we") is rare and reserved for one use: describing the *shared problem* the reader and the book are looking at together ("we both know that the model can return prose when you wanted structured output"). Even there, sparingly, and never as a substitute for you.

The book is not narrated in first person. The author is not a character. The author is a careful guide.

### Pacing and rhythm

- **Short sentences for key claims and concrete moves.** "Block the import. Cap the steps. Run the agent." These are the load-bearing sentences of the book and they should read as load-bearing.
- **Longer sentences for explanation and evidence.** When the chapter is laying out the verified behavior, naming a tradeoff, or qualifying a claim, the sentence length opens up. The book is not a staccato of four-word declaratives.
- **Mix of rhythm, not monotone.** A paragraph of short moves followed by a paragraph of evidence followed by a paragraph of one mixed-length sentence doing the transition is the goal. The reader should feel the chapter breathing, not marching.
- **One move per paragraph, then its evidence-nut.** The default rhythm is: state the move in one or two sentences, then give the evidence or the trade-off in the next paragraph or two. Do not bundle two moves in one paragraph. Do not split one move across three paragraphs.

### Vocabulary constraints

These are binding. The writer must not violate them; the reviewer will fail chapters that do.

**Vocabulary blacklist (all chapters):**

- "Optimal" — without a citation to a named study.
- "Proven" / "scientifically proven" — without a citation to a named study.
- "Studies show" — without naming the study.
- "Magic" / "magical" — without naming what is actually happening (e.g., "the framework parses the action — that is, it does not feel like magic once you read the parser").
- "Just" / "simply" / "obviously" — hand-waving flags. Replace with the actual instruction.
- "Revolutionary" / "game-changing" / "powerful" — hype vocabulary. Replace with the specific capability.

**Vocabulary preferred:**

- "The model," "the agent," "the tool," "the prompt," "the step," "the run" — concrete referents.
- "You" direct address for the reader.
- "We" sparingly, only for shared problems.
- "Run," "execute," "observe," "inspect" — verbs of practice.
- "Returns," "raises," "prints" — verbs of behavior.
- "Verified against 1.26.0 source on 2026-08-01" — when documenting a behavior that could shift.

### Voice reference points from intake

The intake selected "Friendly tutor" with these traits: patient, conversational, encouraging without being vague, define every new term, use short steps, explain code line by line when first introduced, include frequent checks, avoid unexplained jargon.

- The style guide adopts the patient + define-every-term posture, not the encouraging-without-being-vague posture (the latter risks the cheerleading the voice explicitly forbids).
- "Explain code line by line" applies to the first introduction of a construct (the `@tool` decorator in ch-10, the `managed_agents` list in ch-16). It does not apply to code the reader has already seen twice.
- "Avoid unexplained jargon" is enforced by the runnable checks and the inline definition rule — every new term gets a one-sentence plain-language gloss the first time it appears.

---

## Conflict flags

**No conflicts surfaced.** The intake (nonfiction, beginner audience, friendly tutor, 300+ pages, all model access paths, cross-platform), the outline (19 chapters, structural change with new ch-08 toy agent + renumbered ch-09–ch-19), the research-log (no material contradictions between primary sources; eighteen brief-corrections recorded as reconciliations between chapter briefs and verified 1.26.0 runtime, not as conflicts), the bible (facts, terminology, technical claims, APIs, project decisions), and this style guide are mutually consistent.

The three brief-corrections in this guide (ch-10 entry-077, ch-15 entry-145, ch-16 entry-155) and the eighteen brief-corrections catalogued in the outline are all of the same form: a claim in a chapter brief that the verified 1.26.0 source requires the writer to override. There is no conflict between two valid external sources; the verified 1.26.0 runtime is canonical. The 25 inline age-risks are kept directional by design, not because of any conflict.

If the writer discovers a place where a stylistic choice would conflict with this style guide, the resolved brief-correction list, or the outline's `Draws on:` field, the writer must flag it back to master rather than silently picking a side.

---

## Confirmation

Status: DRAFT — pending user confirmation before Phase 5 (writing plan) begins.

The user must explicitly confirm this style guide before Phase 5 starts. The user-facing confirmation points are:

1. **Pinning rules.** smolagents==1.26.0 is the canonical target; the one-time `HfApiModel` → `ApiModel` sidebar lives in ch-09; beginners use `InferenceClientModel`.
2. **Three brief-corrections.** ch-10 entry-077 (no auto-coercion of tool returns), ch-15 entry-145 (Jinja keys are inner names), ch-16 entry-155 (two-level `Model` / `ApiModel` hierarchy with local classes extending `Model` directly).
3. **25 inline age-risks kept directional.** Provider model names, API versions, rate-limit units, context-window sizes, executor-type names, per-model defaults, OS install paths — all phrased directionally, not as exact figures.
4. **Special framing for new ch-08 and ch-09.** ch-08 is plain Python only (no smolagents, no `@tool`, no `CodeAgent`, no `final_answer`); ch-09 opens with the "Why Use a Framework" intro naming the four automations and the three additions.
5. **Code conventions.** Every snippet runnable in `E:\book_gen\.venv\Scripts\python.exe`; PEP 8; `if __name__ == "__main__":` for projects; test before writing.
6. **Voice.** Conversational technical; contractions yes; no exclamation marks; no cheerleading; no "studies show" without naming the study; second person; one move per paragraph, then its evidence-nut.

If any of these six points requires a change, the user names the change here, the style guide is revised, and Phase 5 begins after a second confirmation. If all six are accepted as written, Phase 5 begins with no further changes to the style guide.