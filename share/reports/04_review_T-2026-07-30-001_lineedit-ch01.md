# Line Edit — ch-01 (Daily Focus)

**Pass:** 2 (line edit)
**Verdict:** PASS
**Date:** 2026-07-30
**Reviewer lens:** prose quality + voice consistency vs style-guide.md

## Voice match (per style-guide.md § Voice)

- **Newport traits (calm, evidence-cited, anti-hustle, specific commitments):** PASS — named citation + book title at `chapters/ch-01.md:11` (Newport + *Deep Work*); Wood cited with journal + year at line 21 (`Annual Review of Psychology* in 2016`); Lally cited with journal + year + numbers at line 63 (`European Journal of Social Psychology* ... median of 66 days ... 95th-percentile range ... 18 days to 254 days`); Maltz myth-bust at line 63. Anti-hustle posture confirmed at line 7 ("The fix isn't willpower"). Specific commitments at lines 37-44 (five named moves) and line 81 (cue template).
- **Pragmatic Programmer traits (direct address, no filler, concrete closing):** PASS — second person dominant (lines 5, 7, 13, 19, 31, 32, 37-44, 45, 47, 65, 67, 71, 73, 81). Closing at line 85 is a concrete imperative that names the action (write tomorrow's first task + cue) and the surface (card or task tool). No detected filler sentences in chapter body.
- **Clear traits (concrete habit-installation language; four-laws NOT used as primary frame):** PASS — uses *cue-routine architecture* (line 21), *cognitive scaffolding* (line 13), *cue* (lines 21, 23, 25, 67, 81), *routine* (many), *environmental signal* (line 21), *environmental cue* (decision-002 required vocabulary). No four-laws vocabulary anywhere in body. Clear not invoked in ch-01 at all (consistent with decision-003 ch-05 constraint; Clear is ch-05 territory).
- **Formality (conversational professional, contractions yes, no exclamations, no cheerleading, no academic hedging):** PASS — contractions present and consistent: "It's" line 5, "you've" line 5, "isn't" line 7, "doesn't" line 19, "you'll" lines 31, 32, "don't" line 45, "isn't" line 23, "doesn't" line 67. Zero exclamation marks in chapter body. No cheerleading ("you've got this", etc.). No academic hedging clichés ("it could be argued," "some scholars suggest").
- **Person (second person dominant; first-person plural only for shared problem framing):** PASS — second person dominant throughout. Single first-person-plural usage at line 15 ("the way the rest of us have to keep re-learning") is shared-problem framing per style-guide § Person — appropriate, used sparingly, not as substitute for you.
- **Pacing (short for key claims, longer for evidence, mixed rhythm, one move + one evidence-nut per paragraph):** PASS — line 7 (rhetorical short pair + longer explanation), line 19 (chiasmus: "run on the days you don't need it / skip on the days you do"), line 23 (short-contrast pair of mood vs cue in quotes), line 47 (longer evidence sentence + short directives), line 65 (six-sentence rhythm), line 83 (three short declaratives). Mixed rhythm confirmed; no monotone staccato.

## Issues

No issues at CRITICAL, HIGH, or MEDIUM severity. The chapter clears the bar for prose quality and voice consistency at every binding dimension. Three LOW-level tightening notes are listed under Out-of-scope observations; none are blocking.

## Dev-pass-deferred concerns (addressed)

1. **ch-01.md:25 — internal cross-reference.** VERDICT: TIGHT AS WRITTEN. The 5-sentence block does necessary visibility work per the dev-pass binding decision (cue-routine architecture must be visible to the reader, not just implied). Breakdown:
   - S1: bridge sentence (load-bearing concept claim) — necessary.
   - S2: enumerates downstream chapters (2/3/4/5) attached to the cue — necessary per visibility requirement.
   - S3: anchors the trunk/branch metaphor.
   - S4-S5: deliberate if/only-if parallel structure. On re-read these are not redundant; S4 names what *robust* gives the system (a foundation), S5 names what *fragile* propagates (downstream cue fragility). Different emphases, parallel form — a load-bearing move, not filler.
   - No change recommended.

2. **ch-01.md:81 — cue template scope (cue-only vs cue+first-step).** VERDICT: SCOPE IS CORRECT. Template reads: `"My cue is [specific signal]. Tomorrow at that cue, I will do [first concrete step]."` The template includes *what their cue is* (satisfying the outline development criterion) and the first concrete step (satisfying the outcome-line contract at line 85, which instructs writing BOTH first task AND cue). The cue-routine pair is installed as one committed unit, matching the chapter's central architecture claim and the closing imperative. No issue.

3. **ch-01.md:7 — rhetorical opener voice check.** VERDICT: DEFENSIBLE. "Most days don't fail at 2 PM. They fail at 8:55 AM, when reactive work has already taken the calendar and the important thing has nowhere to go." is mildly rhetorical (X is not Y; X is Z) but is anchored by a specific time (8:55 AM, not "morning"), is set up by the scene at line 5 (the 7:42 AM kitchen), and is followed immediately by anti-hustle: "The fix isn't willpower. The fix is a thirty-minute structured start..." The 8:55 AM claim is consistent with Newport's evidence-cited counterexample posture. No voice issue.

## Outcome-line closing check (re-verify after surgical fix)

- **Outline outcome** (`outline.md:24`): "by the end of the reading, the reader writes tomorrow's first task and its cue on a card (or in their task tool) before doing anything else tomorrow morning."
- **Chapter closing** (`chapters/ch-01.md:85`): "Write tomorrow's first task and its cue on a card (or in your task tool) before doing anything else tomorrow morning."

MATCH: Verbatim, with descriptive→imperative conversion ("by the end of the reading, the reader writes" → "Write") per `style-guide.md:36`. Surgical fix at line 59 (sentence replacement, net −11 words) did not shift the closing line — verified at line 85 unchanged from pre-fix position. PASS.

## Vocabulary blacklist (re-check)

Style-guide.md § Vocabulary blacklist re-checked against `chapters/ch-01.md` chapter body (lines 1-86; the HTML comment block at lines 87-94 is meta-content and not rendered to the reader):

| Blacklist item | Body hits | Note |
|---|---|---|
| "Decision fatigue" | 0 | — |
| "Ego depletion" / "willpower depletion" | 0 | — |
| "Optimal" without citation | 1 | `chapters/ch-01.md:47` — "not an empirically optimal length" (negation, permitted per style-guide) |
| "Proven" / "scientifically proven" | 0 | — |
| "Studies show" | 0 | — |
| "We all know" / "everyone knows" | 0 | — |
| "Make it obvious / attractive / easy / satisfying" as primary frame | 0 | N/A in ch-01; ch-05 territory |

PASS — zero violations.

## Out-of-scope observations

- **(LOW) `chapters/ch-01.md:33`** — Trailing sentence "The morning routine then runs the receiving end" essentially restates the prior sentence "The morning routine is the receiving end of that pipeline" (the only difference is "is" → "runs"). Could be cut without losing content. Not blocking; personal-call tightening.
- **(LOW) `chapters/ch-01.md:47`** — "There is evidence that *a structured start* correlates with perceived productivity — surveys of how people who feel productive begin their days tend to find that they begin them with structure —" is a hedge-pattern evidence claim without a named source. Not on the formal blacklist (which names "studies show"), but matches the same anti-pattern. The "Evidence vs. convention" callout at line 49 partially addresses the convention-vs-evidence distinction. Not blocking; would tighten if a named citation exists.
- **(LOW, file-hygiene) `chapters/ch-01.md:87-94`** — HTML comment block containing writer's self-critique, open questions, and post-dev-fix notes. Not rendered to the reader but is in the file. Pre-publish cleanup item, not a line-edit concern. Should be stripped before final ship (defer to am-ship / master).

## Self-critique

**Confidence:** High on voice match (each dimension verified by direct file reads with path:line evidence), vocabulary blacklist (grep'd against body, line 90 hit confirmed inside the HTML comment not the rendered prose), and outcome-line closing check (string match against outline.md:24, line 85 unchanged after surgical fix). High on the three dev-deferred concerns — each got a separate verdict with evidence. **What I could not verify:** whether the chapter's word count (2,030 words in chapter body, ~2,465 per ledger if HTML comment is included) maps to the style-guide's "~25 pages per chapter" target at the book-gen pipeline's actual formatting convention; the chapter is plausibly within range but I did not cross-check against rendered output. Whether ch-02 through ch-05 writers (not yet drafted) will be able to re-cite the cue-routine architecture cleanly from the line 21 definition — I judged the three-sentence block compact, but did not simulate downstream needs. **Likely needs a second line-edit pass:** No. The chapter clears every binding dimension with margin; the three LOWs are personal-call tightening notes that the writer could address or not at their discretion without changing the chapter's pass status. If am-coder does take a second pass on the LOWs, the existing prose is already close enough that a third pass would not be productive.