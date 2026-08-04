# Multi-Agent Book Writing Workflow — Full Spec

Maps onto the existing `agents-manager` topology (master orchestrator + am-research, am-planning, am-design, am-coder-equivalent "writer", am-review). Default file format: Markdown, unless the user specifies otherwise.

---

## Phase 0 — Intake Survey (Agent: am-planning, orchestrated by master)

Single structured survey, multi-question, each with suggestions/examples. **User must approve each answer** — either by picking a suggestion, editing free-text, or rejecting/retrying. No downstream step starts until this phase is confirmed complete.

Required fields:

1. **Title / working title**
2. **Core idea / goal** — what the book is for, what it should leave the reader with
3. **Category** — agent infers a best guess from title/goal (e.g. "this sounds like nonfiction — a how-to guide") and presents it as a suggestion alongside alternatives: Fiction / Nonfiction / Hybrid (narrative nonfiction, memoir, etc.). User confirms or corrects. This answer sets downstream toggles rather than forking the whole workflow:
   - Fiction/hybrid → bible tracks characters, plot threads, POV, timeline; step 7 review includes continuity/plot checks
   - Nonfiction → bible tracks facts/terminology/claims; research is fact-verification-focused
4. **Audience** — who's reading this, what they already know
5. **Tone/voice reference points** — comparable books, adjectives (agent can suggest examples once category is known)
6. **Target length** — agent presents concrete options with chapter-count implications shown (e.g. "50–100 pages / ~5 chapters", "5 chapters × ~25 pages", "300+ pages / ~15–20 chapters"). Default bias toward the smaller end unless user picks otherwise.
7. **Definition of "done" / good enough** — exit criteria for review loops (e.g. "no unresolved developmental issues, max 2 line-edit passes per chapter")
8. **Exception-handling preferences**, decided up front so agents have a fallback instead of improvising mid-run:
   - What to do if research is thin or contradictory on a topic
   - What to do if the user is unresponsive at a checkpoint (proceed with best judgment and flag it, vs. hard-stop)
9. **Fiction-specific, if applicable** — agent searches genre conventions (structure, typical length, POV norms) relevant to stated genre and folds findings into suggestions here, same survey mechanism as above.

Output: a single confirmed `intake.md` — canonical answers, nothing implied or assumed.

---

## Phase 1 — Skeleton (Agent: am-planning)

Rough shape only, deliberately shallow — not the full outline:

- Working chapter/section list — **count + one-line purpose each**, no full summaries yet
- Rough dependency tags per chapter: `depends_on: [chapter_ids]` (or `independent`) — this is what step 5's linear/parallel decision will read

No user confirmation required yet — this is scaffolding for research, not a commitment.

---

## Phase 2 — Research (Agent: am-research, parallelized)

Research is driven by the skeleton, not by a finished outline — this avoids confirmation-bias research (searching only for things that support a plan already locked in).

Each resource logged as structured metadata, not prose dumps:

```
source: [name/URL]
used_in: [chapter_id(s)]
claim/finding: [what it supports]
quote: [optional, <1 sentence, one direct quote per source max]
paraphrase: [the actual content to use]
```

**Contradiction handling:**
- **Minor variance** (numbers/dates/phrasing differ but claim is materially the same) → agent auto-resolves using precedence: more recent > more authoritative (primary source > established publication > aggregator). Resolution logged in metadata (`source A said X, source B said Y, chose Y because more recent`). No user interrupt.
- **Material contradiction** (sources disagree on something that changes what the book claims) → agent does *not* silently pick a side. Surfaced to user at Phase 3 confirmation, not interrupting research: "sources disagree on X, here are both positions — which does the book take, or do we present it as open debate?" Heuristic for which bucket a contradiction falls in: *would resolving it silently make the book state something false or one-sided without the user knowing a choice was made?* If yes, it's material.

Output: `research-log.md`, structured and queryable by later agents (not re-read in full each time — saves tokens).

---

## Phase 3 — Full Outline (Agent: am-planning, merges old "outline validation")

Builds the real outline from skeleton + research: full chapter titles, summaries, what each chapter draws on and from where, dependency tags finalized.

**User confirmation required** for this phase before writing starts — this is the last checkpoint before content generation begins.

---

## Phase 4 — Style & Voice (Agent: am-design)

Separated into two parts:

- **Presentation** — formatting, chapter structure, how content is laid out (short punchy sections vs. long discursive chapters, etc.)
- **Voice** — how the narrator talks to the reader, informed by Phase 0's tone references

Output: `style-guide.md`. User confirms before writing begins.

---

## Phase 5 — Writing Plan (Agent: master orchestrator)

Determines linear vs. parallel execution:

- User explicitly says parallel → parallel
- User explicitly says linear → linear
- User doesn't specify:
  - Chapters tagged `independent` in the outline → parallel-safe
  - Chapters with `depends_on` links (shared characters/plot/callbacks) → linear

Regardless of mode: **one chapter at a time, finish and save before moving to the next.** This keeps each agent's working context small and achievable rather than holding a whole book in-flight — prevents context overflow and drift.

Plan output: `writing-plan.md` — ordered/grouped task list linking each chapter to its outline entry, its relevant research-log entries, and the style guide. Presented to user before writing starts.

---

## Phase 6 — Writing (Agent: writer role, per chapter)

Each chapter-writing agent reads before writing:
- The **book bible** (see State Mechanism below)
- Its outline entry + linked research
- The style guide

Writes the chapter, saves it, updates the bible and ledger (below) before the next chapter starts — even in parallel mode, bible updates should be appended in commit order to avoid two simultaneous chapters silently conflicting.

**Confirmation triggers during writing:**
- Chapter still in progress (not yet marked finished) → agent can freely revise/rework it without a user checkpoint, as long as it stays within what's already approved in the outline/bible
- Chapter marked finished, then needs to be **removed or reordered** → requires user confirmation
- **Adding** a new chapter → always requires user confirmation, regardless of state

---

## Phase 7 — Review (Agent: separate reviewer role/sub-agent — never the same agent that wrote the chapter)

Three distinct passes, not one generic "check":

1. **Developmental** — does the chapter serve the outline/goal; anything missing, contradicting the bible, or (for fiction) breaking continuity/timeline/POV. Runs immediately after each chapter is drafted, before it's marked "approved" in the ledger.
2. **Line edit** — prose quality, voice consistency against the style guide. Per chapter.
3. **Copy edit** — grammar, formatting, terminology consistency. Best run as a single full-book pass at the end rather than per-chapter, since some issues (repeated word overuse, inconsistent capitalization) only surface at whole-book scale.

Exit criteria pulled directly from Phase 0's "definition of done" — no open-ended revision loops.

---

## State & Memory Mechanism

Three lightweight, structured files, cheap for any agent to read — never re-parse prior full chapters for context:

1. **`bible.md`** — cumulative facts, established terminology, voice rules; for fiction/hybrid also characters, plot threads, timeline, POV. Updated after each chapter completes.
2. **`ledger.md`** — one row per chapter: status (`planned` / `drafted` / `dev-reviewed` / `line-edited` / `approved`), dependency tags, word count. Lets the orchestrator know what's done without re-reading content.
3. **`decisions-log.md`** — why the outline changed, what the user rejected and why, contradiction resolutions. Answers "why isn't X included" months later without re-deriving it.

---

## Agent Role Mapping (onto `agents-manager` topology)

| Phase | Role |
|---|---|
| 0 — Intake survey | am-planning |
| 1 — Skeleton | am-planning |
| 2 — Research | am-research (parallel) |
| 3 — Full outline | am-planning |
| 4 — Style/voice | am-design |
| 5 — Writing plan | master orchestrator |
| 6 — Writing | writer role (per chapter) |
| 7 — Review | am-review (separate invocation per pass, never the writer agent) |

---

## File/Output Structure

```
/book-project/
  intake.md
  research-log.md
  outline.md
  style-guide.md
  writing-plan.md
  bible.md
  ledger.md
  decisions-log.md
  /chapters/
    chapter-01.md
    chapter-02.md
    ...
```
