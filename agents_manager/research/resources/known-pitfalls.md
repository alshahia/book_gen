# Known Pitfalls — research reports

**Last verified:** 2026-07-04

Five traps am-research has either hit or watched peers hit. Read once at dispatch-start; revisit in self-critique.

## 1. The "uncited finding" trap

A bullet under **Technical findings** that names a tool, function, or behavior without a `path:line` or doc URL.

**Why it happens:** the agent infers from context and writes it down as if confirmed.
**Why it's a bug:** the planner then builds on an unverified assumption; the coder implements against a phantom API.
**Fix:** rule 3 (cite-everything) is absolute. If you can't cite, mark "Unknown — needs verification" and move it to **What we don't know**.

## 2. The "padded report" trap

A long, confident-sounding **Feasibility verdict** with no concrete driver behind the claim.

**Why it happens:** the agent wants to look decisive; "yes" feels safer than "partial" or "no".
**Why it's a bug:** the master advances the pipeline on false confidence; downstream costs surface only at review.
**Fix:** rule 2 (honesty is non-negotiable) + v0.14.1 calibrated feasibility verdict (`confidence: HIGH|MEDIUM|LOW` with the driver in one short paragraph). When the answer is "partial", say partial.

## 3. The "scope-creep via tangential discoveries" trap

A **Side observation** that quietly grows into a primary finding, then into a recommendation, then into a second task.

**Why it happens:** the agent found something interesting and didn't want to lose it.
**Why it's a bug:** the planner now plans two tasks; the budget doubles; the user only asked for one.
**Fix:** rule 8 (stay-in-scope). Tangential observations are bullets, not sections. If it deserves a section, it deserves a separate task — surface the conflict, don't absorb it.

## 4. The "missing self-critique" trap

Returning to master without filling the `## Self-critique` block, or filling it with "yes, did my job" and nothing else.

**Why it happens:** the agent is rushed or thinks the gate is ceremonial.
**Why it's a bug:** the master will not advance without the gate met (SKILL.md L131-133). Worse, without an honest self-critique, the same blind spot repeats on the next task.
**Fix:** the block is mandatory. Required content: did I do my job, what might I have missed, what did I assume without evidence. Three bullets minimum, one sentence each, no padding.

## 5. The "missing NEEDS_USER_INPUT" trap

Returning `NEEDS_USER_INPUT: false` when **What we don't know** still has open questions, because the questions "felt obvious".

**Why it happens:** the agent picked a default and forgot the user has veto power.
**Why it's a bug:** the master advances; the user discovers at review that their preference was overridden silently.
**Fix:** rule 5 (clarifying questions must be actionable). If a question meets all three criteria (changes plan, one-sentence answer, not already answered) AND you picked a default instead of asking, set `NEEDS_USER_INPUT: true` and surface the question.

## Bonus: the "implicit decisions" trap

A research note that quietly commits the team to a library, architecture, or file layout without a finding backing it up.

**Why it's a separate trap:** rule 1 says "you investigate, you do not decide." A research file is not the place to lock choices.
**Fix:** any choice-shaped recommendation belongs in `## Recommendations for the planning agent` as a suggestion, not a fact. The planner decides; the coder implements; the review gates.

---

last-verified: 2026-07-04