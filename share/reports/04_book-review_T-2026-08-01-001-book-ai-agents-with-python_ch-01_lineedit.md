# Line-Edit Review — ch-01 — AI Agents with Python

Date: 2026-08-01
Reviewer: am-review
Chapter: 407 words at `books/ai-agents-with-python/chapters/ch-01.md`
Previous pass: dev-review PASS_WITH_WARN (1 LOW)
Style guide: `books/ai-agents-with-python/style-guide.md`

## Verdict: PASS_WITH_WARN

Voice is clean, citations are inline, outcome line is near-verbatim, no regressions vs. dev pass; one LOW terminology nit (the LLM acronym is used in the body without an inline expansion; the subheading primes "language model" but the first body mention is the bare acronym), and the dev-review CodeAgent advisory is unaddressed but the dev review explicitly judged it "not required."

## Checklist

### 1. Voice consistency: PASS
- Conversational technical, scene-setter opener: "Before you open a terminal, picture explaining an AI agent to a new coder." (line 3).
- Second person dominant: "you'll have plain-language definitions", "you can describe", "your own words", "you must review". No first-person plural anywhere in the chapter.
- Contractions present ("you'll", "isn't", "aren't"), no exclamation marks, no cheerleading.

### 2. Vocabulary blacklist: PASS
- Scanned the chapter for the full blacklist ("magic", "magical", "just", "simply", "obviously", "optimal", "proven", "revolutionary", "game-changing", "powerful", "studies show"): zero hits.
- The phrase "model output is a draft" (which could read as a hand-wave) is rescued by the rest of the chapter — IBM hallucination warning, isolated-execution caveat, the move callout all anchor it.

### 3. Citation hygiene: PASS
- Every claim is sourced inline: "Python's official FAQ" (line 9), "The official Python tutorial" (line 9), "IBM defines an LLM as" (line 13), "IBM's *Evaluating LLMs* section" (line 15), "The Hugging Face smolagents guide" (line 19), "Anthropic's *Building effective agents*" (line 21), "The smolagents package guide" (line 25). No hanging claims.
- Zero hits for the banned forward-pointers ("as we will see", "in the next chapter", "as the title says").
- The one short direct quote ("AI Agents are programs where LLM outputs control the workflow", line 19) is properly attributed to the Hugging Face smolagents guide and is the single permitted direct quote per the dev review.

### 4. Pacing and rhythm: PASS
- Short load-bearing sentence: "Check the draft before it influences an action." (line 15) — exactly the rhythm the style guide asks for.
- Longer explanatory sentences for evidence (the IBM and Anthropic paraphrases, lines 13–21) — rhythm opens up for the evidence-nut paragraphs.
- Opener (scene) → definitions (evidence) → move callout (imperative) → closing imperative. The chapter breathes at the seams. For a 407-word definitional chapter the rhythm is appropriate; the style guide's "one move per paragraph, then its evidence-nut" applies to the opener (one move = the four definitions) and the rest of the chapter is the evidence-nut.

### 5. Forward-pointer hygiene: PASS
- No "What's next" paragraph in the chapter. The dispatch checklist item 5 anticipates one, but the binding style guide (line 40) explicitly exempts ch-01: "Chapter 1 has no such note (it is independent)." This is the same reconciliation the dev review surfaced (line 62 of the dev report); style guide wins.
- No forward pointer to ch-02 by name. The closing is the outcome line, which is correct per the style guide for ch-01.

### 6. LOW-issue resolution: PASS_WITH_WARN
- The dev review's LOW advisory (line 25: "Its `CodeAgent` can execute model-generated Python") is **unaddressed in prose** — no parenthetical gloss was added between dev and line-edit. The file mtime (15:21:43) predates the dev review (15:25:36), so the chapter was not modified.
- The dev review explicitly judged this issue **"not required"**: "Context implies the role ('can execute model-generated Python'), so this is inferable; flagged as advisory only for the line-edit pass to consider." The line-editor concurs — for a true beginner, "CodeAgent" is something that "can execute model-generated Python" (the role is carried by the action description), and the surrounding "isolated execution when prompts or retrieved content aren't fully trusted" anchors the safety reason. A parenthetical like "(the smolagents class that runs model-written Python)" would be a polish, not a fix.
- WARN, not FAIL, because the dev review's "not required" call stands; the line-editor has not judged the seam too abrupt for the reader.

### 7. Terminology consistency: PASS_WITH_WARN
- "Python" — used consistently throughout, no version pin, matches bible.
- "AI agent" / "agent" — used consistently. The bible's working definition ("A program that uses a language model to decide which actions to take") is reflected in the chapter's compact quote (line 19) plus the Anthropic contrast (line 21).
- "Tool" — used consistently; the chapter's working definition matches the bible ("a typed Python function decorated with `@tool`" — chapter says "a typed Python function with a clear docstring", line 25, with `@tool` deferred to ch-10 per the dependency chain).
- **LOW nit:** the LLM acronym is used without expansion on its first body occurrence. Line 11's subheading reads "Understand the language model," which primes the term, but line 13 says "IBM defines an LLM as a deep-learning model..." — the acronym is presented to a reader who has not yet met it in expanded form. The bible's canonical form is "Large language model (LLM)" (line 37 of bible.md). The style guide rule "define every new term" (line 210 of style-guide.md) applies. Recommended fix: rephrase line 13 to "IBM defines a large language model (LLM) as a deep-learning model..." and keep the rest of the chapter on "LLM" thereafter.
- "agent loop" — not used. This is correct: the loop is introduced in ch-08 (plain Python) per the bible and the style guide; ch-01 stays conceptual.

### 8. Outcome-line contract: PASS
- Outline outcome line: "Describe Python, LLMs, AI agents, and why agent output is a draft."
- Chapter closing imperative (line 37): "By the end of this chapter, you can describe in plain language what Python is, what a large language model is, what an AI agent is, and why agent output must be treated as a draft before being acted on."
- This is the outcome line near-verbatim with the prescribed second-person rewrite ("you can describe" instead of "the reader can describe"). The "The move" callout (line 27) carries the same action in imperative form for the reader-facing delivery. Both deliverables from the style-guide table's ch-01 row (line 67) are present.
- Reader can act after closing: the four concepts (Python, LLM, agent, draft rule) are all defined and named in the chapter; the reader can produce the one-paragraph explanation the move callout asks for.

### 9. Style-guide cross-cutting rules: PASS
- Orientation paragraph (line 3) is 52 words — within the 30–60 word window. Concrete scene ("Before you open a terminal, picture explaining an AI agent to a new coder"), not a thesis statement.
- Closing imperative is the outcome line near-verbatim.
- Self-critique HTML comment preserved (lines 29–35). Per the dispatch: "for the reviewer's handoff, not the reader"; strip at publish time per the daily-focus precedent.
- "The move" callout present, boxed with `> **The move:**`, single occurrence, near the close.
- No code blocks (correct — ch-01 is conceptual-only, per style guide line 55).
- Contractions yes, no exclamation marks, no hype vocabulary, no `HfApiModel` mention (grep returns zero hits), no `@tool` usage in ch-01 prose, no `final_answer` mention.

### 10. No regressions vs. dev review: PASS
- File mtime: `ch-01.md` LastWriteTime 2026-08-01 15:21:43; dev review LastWriteTime 2026-08-01 15:25:36. The chapter was last touched **before** the dev review was written. The dev review's recorded chapter size (2667 bytes) also matches the chapter's current Length (2667 bytes). No modifications between passes.

## Issues

| Severity | Issue | Location | Recommended fix |
|---|---|---|---|
| LOW | LLM acronym used without expansion on first body occurrence. Subheading "Understand the language model" primes the term, but the first body mention is the bare acronym ("IBM defines an LLM as a deep-learning model..."). A true beginner who reads only the body would see "LLM" before seeing the expansion. The bible's canonical form is "Large language model (LLM)" and the style guide requires every new term to be glossed. | ch-01.md line 13 | Rephrase to "IBM defines a large language model (LLM) as a deep-learning model..." — the chapter can then use "LLM" freely for the rest of the IBM and downstream paragraphs. |
| LOW (advisory, not required) | `CodeAgent` is named inline ("Its `CodeAgent` can execute model-generated Python") without a parenthetical one-clause gloss for a reader who has never met smolagents. The dev review (line 69 of the dev report) explicitly judged this "not required" because the role is inferable from the action description; the line-editor concurs. No fix needed unless a future reader comment flags the seam. | ch-01.md line 25 | Optional polish only: append "(the smolagents class that runs model-written Python)" after the first `CodeAgent` mention. Defer to next chapter's reader feedback. |

No MEDIUM, HIGH, or CRITICAL issues.

## Sign-off

Chapter is approved. Ledger ch-01 row should move `dev-reviewed` → `line-edited`. The two LOW issues are non-blocking: the LLM-expansion nit is a one-sentence edit the writer can make on a copy-edit pass, and the CodeAgent advisory was explicitly judged not required by both the dev and line-edit passes. Master may dispatch the line-edit sign-off back to the book-gen orchestrator for ledger bookkeeping; no re-dispatch of am-coder is required.
