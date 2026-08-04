# Dev Review — ch-01 — AI Agents with Python

Date: 2026-08-01
Reviewer: am-review
Chapter: 407 words at `books/ai-agents-with-python/chapters/ch-01.md`
Outline reference: ch-01 (Meet Python and AI Agents, independent)
Style guide: `books/ai-agents-with-python/style-guide.md`
Bible: `books/ai-agents-with-python/bible.md`

## Verdict: PASS_WITH_WARN

Chapter serves the outline, voice matches the style guide, and all four outcome-line promises are delivered with named inline citations; one LOW advisory about a forward-named smolagents term that may need a one-clause gloss at the line-edit pass.

## Checklist

### 1. Outline coverage: PASS
- Outcome line delivered near-verbatim at the close: "you can describe in plain language what Python is, what a large language model is, what an AI agent is, and why agent output must be treated as a draft before being acted on."
- All three promised definitions present: Python (entry-001/002/003), LLM (entry-004/005), agent (entry-006/007). "model output is a draft" rule stated three times — opener, IBM caveat paragraph, and the move callout.
- Draws-on coverage: entry-001/002/003 → "Python's official FAQ… interpreted, high-level, general-purpose… official Python tutorial says it skips a compile-and-link step"; entry-004 → "IBM defines an LLM as a deep-learning model"; entry-005 → "IBM's *Evaluating LLMs* section warns that plausible output can be false, a problem called hallucination"; entry-006 → "AI Agents are programs where LLM outputs control the workflow" + agency spectrum; entry-007 → "Anthropic's *Building effective agents* distinguishes a workflow… from an agent"; entry-008 → tool + `CodeAgent` sandbox-execution safety anchor.
- entry-061 handled correctly: ch-01 does not raise the `HfApiModel → ApiModel` renumber (it is the ch-09 sidebar per the outline).
- Boundary kept: no code blocks, no `@tool` usage, no framework import line, no `pip install` instructions. ch-01 stays conceptual as required.

### 2. Voice match: PASS
- Conversational technical: "Picture explaining an AI agent to a new coder" (scene-setting opener, per style guide).
- Second person dominant: "you'll have plain-language definitions", "you can describe", "you must review model output", "your own words". No first-person plural slipping in.
- Contractions present: "you'll", "isn't" (in the IBM paraphrase).
- No exclamation marks. No hype vocabulary — scanned for "optimal", "proven", "studies show", "magic", "just", "simply", "obviously", "revolutionary", "game-changing", "powerful"; none appear.
- Citations named inline as required: "Python's official FAQ", "The official Python tutorial", "IBM defines", "IBM's *Evaluating LLMs* section", "Hugging Face smolagents guide", "Anthropic's *Building effective agents*", "smolagents package guide".

### 3. Bible consistency: PASS
- Python version floor not violated (chapter makes no version pin claim).
- smolagents pinning not violated (chapter only mentions smolagents by name as the source of definitions, not as something the reader installs here).
- Three brief-corrections are not relevant to ch-01's scope.
- Bible append verified: `books/ai-agents-with-python/bible.md` lines 34–43 ("Added by ch-01 — 2026-08-01") carries Python, Large language model (LLM), Token, Hallucination and bias, Workflow, Agency spectrum, Draft-before-action rule, Code-executing agent safety — eight new terms, all consistent with the chapter prose. No seeded fact is contradicted.

### 4. Research grounding: PASS
- Every claim traces to a research-log entry (entry-001…entry-008) as enumerated in the outline's Draws-on field. No hanging claims.
- Anthropic "workflows vs agents" distinction (entry-007) is presented: "Anthropic's *Building effective agents* distinguishes a workflow, whose route is predefined in code, from an agent, whose model chooses the next step and tool… bounded by human goals, review checkpoints, and maximum step counts."
- Smolagents agency spectrum (entry-006) is presented with the one allowed short direct quote: "AI Agents are programs where LLM outputs control the workflow." (followed by the spectrum paraphrase "from showing model text to choosing tools, repeating steps, or starting another agent").
- CodeAgent / sandboxed-execution safety anchor (entry-008) is presented as a ch-01 caveat, not as a ch-01 payoff: "Its `CodeAgent` can execute model-generated Python, so the guide recommends isolated execution when prompts or retrieved content aren't fully trusted." The chapter does not teach sandboxing — it plants the seed.

### 5. Beginner accessibility: PASS
- All four headline concepts are defined inline on first use; no prior knowledge assumed.
- "Token" glossed inline: "a small unit of text". "Hallucination" glossed inline: "plausible output can be false". "Workflow" distinguished from "agent" by contrast.
- Draft-before-action rule stated in three forms (opener, IBM paragraph, the move callout) — reinforced, not buried.
- One minor nit flagged below for the line-edit pass.

### 6. Outcome-line contract: PASS
- Closing imperative is the outcome line near-verbatim (style guide allows "verbatim or near-verbatim"; the only change is "the reader can" → "you can", which is the prescribed second-person rewrite).
- Reader-facing action delivered by the "The move" callout: "Write one paragraph in your own words explaining what an AI agent is and why you must review model output before any action uses it." This matches the style-guide table's ch-01 row (the table scopes the move to agent + draft rule, not all four; the closing imperative carries the full outcome so the reader has both).
- "The move" callout appears once, near the end, boxed with `> **The move:**` — matches style guide exactly.

### 7. HfApiModel / ApiModel rule: PASS
- `HfApiModel`: grep over the chapter returns zero hits. ✓
- `ApiModel`: grep over the chapter returns zero hits. ✓
- Version-drift renumber concern not raised. ✓

### 8. End-of-chapter mechanics: PASS_WITH_WARN (style-guide reconciliation)
- "The move" callout present, boxed, single occurrence, near the close. ✓
- Closing imperative present and matches the outcome line. ✓
- Self-critique HTML comment preserved (lines 29–35 of `ch-01.md`). ✓ — explicitly per the dispatch: "it's for the reviewer's handoff, not the reader."
- "What's next" paragraph: NOT present, but the style guide explicitly exempts ch-01: "Chapter 1 has no such note (it is independent)." The dispatch checklist item 8 wording suggests one is expected; the binding document (style guide) wins here. No fix needed.
- Chapter-opening convention followed: opener is a concrete scene ("Before you open a terminal, picture explaining an AI agent to a new coder") rather than a thesis statement.

## Issues

| Severity | Issue | Location | Recommended fix |
|---|---|---|---|
| LOW | `CodeAgent` is named inline ("Its `CodeAgent` can execute model-generated Python") without an inline one-clause gloss for a reader who has never met smolagents. Context implies the role ("can execute model-generated Python"), so this is inferable; flagged as advisory only for the line-edit pass to consider adding a parenthetical like "(the smolagents class that runs model-written Python)" if the line editor judges the seam too abrupt for a true beginner. | ch-01.md line 25 ("Put tools inside boundaries" section) | Optional: append `(the smolagents class that runs model-written Python)` after the first `CodeAgent` mention. Not required. |

No MEDIUM, HIGH, or CRITICAL issues.

## Sign-off

Chapter is approved for line-edit. Ledger ch-01 row should move `drafted` → `dev-reviewed`. The LOW advisory is for the line-editor to consider, not a re-dispatch of am-coder.

---

**Notes on the style-guide / dispatch-checklist tension (item 8):** the dispatch checklist asks for a "What's next" paragraph; the binding style guide (line 40) explicitly exempts ch-01 because it is independent. Style guide wins; no fix required. Surfaced here so master sees the reconciliation if the line-edit dispatch repeats the same item.