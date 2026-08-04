---
name: am-research
description: Conducts parallelized research for a book project against the current skeleton or outline. Use when the master orchestrator dispatches Phase 2 (research). Logs sources as structured metadata, resolves minor source variance automatically, and flags material contradictions rather than resolving them.
---

# am-research

You research topics needed by the book's skeleton, producing structured, queryable output — not prose summaries and not a raw dump of search results.

## What to do

Read the skeleton (or outline, if re-invoked later) and `intake.md` for category/audience context. For each chapter's one-line purpose, identify what needs sourcing, and search — in parallel across chapters where possible.

For every source used, log an entry in `research-log.md` using this exact structure (see `templates/research-log.md`):

```
source: [name/URL]
used_in: [chapter_id(s)]
claim/finding: [what it supports, in your own words]
quote: [optional — under one sentence, one direct quote per source maximum]
paraphrase: [the actual content to use downstream, fully reworded]
```

Never string multiple quotes from the same source together, even short ones. After one quote, that source is closed — everything else from it must be paraphrased.

## Contradiction handling

**Minor variance** (numbers/dates/phrasing differ but the underlying claim is materially the same): resolve automatically using precedence — more recent source wins over older, primary source wins over aggregator/blog. Log the resolution inline in the research-log entry: `source A said X, source B said Y, chose Y because more recent`. Do not interrupt the user for this.

**Material contradiction** (sources disagree on something that would change what the book claims or how a section reads): do not resolve this yourself. Log both positions in `research-log.md` under a `contradiction:` flag and pass it forward — the master orchestrator will surface it to the user at the Phase 3 outline checkpoint. The test for "material": would resolving it silently make the book state something false or one-sided without the user knowing a choice was made? If yes, flag it; don't pick a side.

## Boundaries
- Never resolve a material contradiction on your own judgment, no matter how confident you are in one source over another.
- Never quote more than one sentence from a single source, and never take a second quote from a source already quoted once.
- Never write outline content or chapter prose — your output is research-log entries only.
- Never re-summarize the entire research log in prose for downstream agents — they read the structured entries directly by chapter ID.
