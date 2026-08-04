# Review Report — T-2026-08-01-001-book-ai-agents-with-python / ch-06_dev

**Date:** 2026-08-02
**Sub-agent:** review
**Loop:** initial

## Summary
- **Overall verdict:** FAIL
- **Tasks reviewed:** 1
- **Pass / Warn / Fail:** 0 / 1 / 1
- **Block release?** yes

## Tests / build run
- No documented test command — relying on LLM judgment only. This chapter is conceptual and contains no runnable code block or executable check.

## Per-task verdicts

### ch-06 — Understand Language Models
- **Verdict:** FAIL
- **Spec match:** The chapter covers the next-token loop, tokens, training/inference, context windows, sampling, roles, and safety flags, and its “What’s next” names ch-07 (`chapters/ch-06.md:7-65`). It does not satisfy the required closing-action contract: the outcome must be the closing imperative, but the chapter ends with metadata/self-critique text and a lowercase summary rather than the required reader action (`chapters/ch-06.md:67-74`; `style-guide.md:36-40,61-72`).
- **Correctness:** The explanation is broadly grounded and consistent with the bible: next-token prediction (`chapters/ch-06.md:9-13`), tokenization (`:17-21`), training versus inference (`:25-29`), context window and “Lost in the Middle” (`:33-37`), temperature/top_p (`:41-45`), roles (`:49-53`), and both safety flags (`:55-61`). One research requirement is omitted: entry-046 says batch inference should be mentioned in one sentence and set aside, but the chapter only discusses online inference (`research-log.md:313-317`; `chapters/ch-06.md:25-29`).
- **Style:** Voice is conversational technical, second-person, and beginner-oriented overall (`chapters/ch-06.md:1-65`; `style-guide.md:157-210`). The opening is an explanatory summary rather than the required concrete scene (`chapters/ch-06.md:1-5`; `style-guide.md:36`). The trailing HTML self-critique and lowercase afterword are not reader-facing chapter prose and prevent a clean book closing (`chapters/ch-06.md:67-74`).
- **Tests:** No runnable check is present. The style guide requires each chapter except ch-01 to install at least one runnable check (`style-guide.md:53-59`); because ch-06 is conceptual and the outline outcome is prose, this is at least a WARN rather than the primary FAIL.
- **Evidence:** `chapters/ch-06.md:1-74`; `outline.md:105-110`; `style-guide.md:36-40,53-72`; `bible.md:82-94`; `research-log.md:301-341`.
- **Issues:**
  - [CRITICAL] `chapters/ch-06.md:67-74` does not close with the outline outcome as an imperative. Remove production-visible self-critique/metadata and make the final line an imperative equivalent to: “Write a one-page plain-language explanation of what a context window is and why the model’s output is a draft, naming both safety flags.”
  - [HIGH] `chapters/ch-06.md:25-29` omits the batch-inference distinction required by research entry-046 (`research-log.md:313-317`). Add one beginner sentence defining batch inference and explicitly defer it.
  - [HIGH] `chapters/ch-06.md:1-5` opens with a thesis/chapter summary, not the concrete scene required by the style guide (`style-guide.md:36`). Recast the opening around an observable chat-box or terminal moment while retaining the orientation.
  - [MEDIUM] `chapters/ch-06.md:67-74` contains writer handoff artifacts (“Self-critique” and a lowercase capability note). These should not ship in reader-facing chapter text.
  - [MEDIUM] No runnable check appears, contrary to `style-guide.md:53-59`. Add the smallest copy-and-run demonstration if the chapter brief permits; otherwise explicitly resolve the exception with master rather than silently omitting it.
- **Suggested fix:** Rewrite the opening and closing, remove handoff artifacts, add the missing batch-inference sentence, and decide/document whether this conceptual chapter receives a runnable check.

## Cross-cutting findings
- Research grounding is strong across all seven entries except the batch-inference sub-requirement in entry-046; the chapter also correctly avoids forbidden `HfApiModel`/`ApiModel` mentions and keeps provider names and context sizes directional (`chapters/ch-06.md:17-65`; `bible.md:10,26-28`; `style-guide.md:139-153`).
- The chapter correctly points deeper safety defenses to ch-15, matching the book bible and outline, although the research-log paraphrase says ch-14; the canonical book-level sources support the chapter’s ch-15 pointer (`chapters/ch-06.md:61,65`; `bible.md:94`; `outline.md:109`).

## Out-of-scope observations (informational only)
- The chapter is substantially shorter than the style guide’s nominal 17–22-page target, but no page-rendering evidence was supplied; this review does not treat raw line count as a release blocker (`style-guide.md:11-15`).

## Honest assessment
The technical core is clear, accessible, and well aligned with the bible, and all seven research entries are visibly represented at the main-claim level. It is not shippable because the required reader action is not the closing line, handoff artifacts remain in the chapter, and entry-046’s batch-inference requirement is missing. Fix those concrete issues before approval.

## Self-critique
- **Did I do my job?** yes
- **What might I have missed?** I did not execute a prose linter or render the chapter; no documented test command or rendering command was available. I did not independently verify external source pages.
- **What did I assume without evidence?** I treated the outline/style-guide outcome contract as binding despite the chapter having no code; that is explicitly required by `style-guide.md:61-72`.
