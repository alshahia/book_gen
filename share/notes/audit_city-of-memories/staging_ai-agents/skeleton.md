# Skeleton — AI Agents with Python

Status: DRAFT (no user confirmation required at this stage)

| Chapter ID | Working title | One-line purpose | depends_on |
|---|---|---|---|
| ch-01 | Meet Python and AI Agents | Build a beginner-friendly mental model of Python, language models, tools, and agents before writing code. | independent |
| ch-02 | Set Up a Cross-Platform Workspace | Prepare Python, notebooks, scripts, virtual environments, and safe environment-variable handling on Windows, macOS, and Linux. | ch-01 |
| ch-03 | Write Your First Python Programs | Learn values, variables, input, output, types, and basic expressions through small runnable exercises. | ch-02 |
| ch-04 | Make Programs Decide and Repeat | Use conditions, loops, functions, and simple debugging habits to create programs that respond to changing input. | ch-03 |
| ch-05 | Work with Data and Files | Organize information with core collections, read and write files, and handle common failures without losing data. | ch-04 |
| ch-06 | Understand Language Models | Learn how prompts, context, tokens, responses, uncertainty, and model access fit into an agent application. | ch-05 |
| ch-07 | Call Models Safely from Python | Connect a notebook and script to provider-flexible cloud, Hugging Face-hosted, and local model paths while keeping credentials out of code. | ch-06 |
| ch-08 | How Agents Work: A Toy Agent from Scratch | Build a minimal agent loop in plain Python (model picks action → tool runs → result fed back → loop until final answer) before introducing smolagents, so the reader sees exactly what the framework automates. | ch-07 |
| ch-09 | Build a First smolagents Agent | Open with a short "Why Use a Framework" intro that compares the toy agent from ch-08 to smolagents, then assemble a minimal `CodeAgent`, run a simple task, and inspect how the model chooses and uses capabilities. | ch-08 |
| ch-10 | Give Agents Useful Tools | Turn focused Python functions into tools and design clear inputs, outputs, and failure behavior for reliable use. | ch-09 |
| ch-11 | Guide Agents with Instructions and Memory | Shape agent behavior with explicit goals, constraints, context, and deliberately bounded working memory. | ch-10 |
| ch-12 | Create Structured Agent Workflows | Break larger goals into validated steps, pass structured results between them, and recover when a step fails. | ch-11 |
| ch-13 | Observe, Debug, and Evaluate Runs | Trace decisions, record useful events, measure task outcomes, and diagnose why an apparently successful run is wrong. | ch-12 |
| ch-14 | Test Agents Without Guessing | Build repeatable tests for tools, workflows, model-dependent behavior, and regressions using controlled inputs and clear success criteria. | ch-13 |
| ch-15 | Keep Agents Safe and Responsible | Add trust boundaries, permission limits, input validation, secret protection, human approval, and defenses against unsafe instructions. | ch-14 |
| ch-16 | Coordinate Multiple Agents | Divide a substantial task among specialized agents, define handoffs, prevent duplicated work, and resolve conflicting results. | ch-15 |
| ch-17 | Choose and Operate Model Backends | Compare provider-flexible cloud APIs, Hugging Face options, and local models by capability, privacy, latency, cost, and operational effort. | ch-13, ch-15 |
| ch-18 | Project: Research and Briefing Agent | Build an evidence-aware agent that gathers information, tracks sources, checks gaps, and produces a structured briefing for human review. | ch-14, ch-15, ch-17 |
| ch-19 | Project: Multi-Agent Work Assistant | Combine tools, structured workflows, observability, safety controls, multiple agents, and interchangeable model backends into a substantial end-to-end application. | ch-16, ch-17, ch-18 |

Notes: this is intentionally shallow — no summaries, no research citations yet. Its only job is to give am-research something to aim at.
