# Research Template (`01_research/`)

Three optional artifacts, each with `.md` + `.json` mirror.

## `competitive-analysis.md`

**Purpose**: Position the new design against existing products. Identify what to copy, improve, avoid.

```markdown
# Competitive Analysis — <Project Name>

**Audience for this doc**: PM, stakeholders, design team
**Date**: YYYY-MM-DD
**Analyst**: am-design

## TL;DR
<3-5 bullets. What did we learn? What's our wedge?>

## Comparators
| Product | What they do well | What they do poorly | Visual signature |
|---|---|---|---|
| <Name> | ... | ... | <1-line description> |

## Patterns we should adopt
- ...

## Patterns we should explicitly avoid
- ...

## White space (no one does this)
- ...

## Open questions
- ...
```

**`.json` mirror** of the same content. Use machine-readable fields where possible (e.g. an array of comparator objects).

## `user-research.md`

**Purpose**: Synthesize existing user research into design-relevant signals.

```markdown
# User Research Synthesis — <Project Name>

## Personas
### <Persona name>
- Demographics: ...
- Goals: ...
- Frustrations: ...
- Quote: "<verbatim from research>"

## Jobs to be done
- When <situation>, <persona> wants to <motivation>, so they can <expected outcome>.

## Pain points
1. ...
2. ...

## Behavioral signals
- <what users actually do, not what they say>

## What this means for design
- <3-5 design implications derived from above>
```

## `design-audit-input.md`

**Purpose**: When the dispatch is `mode=AUDIT` or `EVALUATE`, this is the input to the audit (NOT the output — the output goes to `05_audit/`).

```markdown
# Audit Input

## Subject
<What's being audited: existing app, marketing site, brand assets>

## Audit scope
- Medium(s): ...
- Screen count: ...
- Locale(s): ...
- Accessibility level claimed: <WCAG 2.2 AA / AAA / none>

## Reference standards
- WCAG 2.2 (web)
- Apple HIG (iOS)
- Material Design 3 (Android)
- W3C Design Tokens
- Brand book <link if exists>

## What's in scope
- ...

## What's out of scope
- ...

## Known issues
- ...

## Audit criteria
1. Contrast (4.5:1 AA / 7:1 AAA)
2. ...
```

## Always

- Cite sources (interview transcript, survey ID, paper, article).
- Distinguish observed behavior from self-reported.
- Flag any finding that contradicts the brief.