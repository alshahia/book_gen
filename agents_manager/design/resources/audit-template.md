# Audit Template (`05_audit/`)

Three artifacts, in order: `findings.md` → `severity-matrix.md` → `remediation-plan.md`.

## `findings.md`

```markdown
# Audit Findings — <Subject>

**Mode**: AUDIT (visual / UX review) | EVALUATE (accessibility / performance)
**Standard**: WCAG 2.2 AA | Apple HIG | Material 3 | W3C Design Tokens | <brand>
**Date**: YYYY-MM-DD
**Auditor**: am-design

## Summary
<TL;DR — 3-5 bullets. Most important takeaways.>

## Methodology
- What was reviewed (list of screens / pages / assets)
- Tools used (browser devtools, contrast checker, etc.)
- Time spent

## Findings
### F-001 — <Short title>
**Severity**: Critical | Major | Minor | Info
**Standard violated**: <WCAG SC / HIG guideline / brand rule>
**Affected**: <screen(s), component(s), asset(s)>
**Observed**: <what you saw, with screenshot path or quote>
**Expected**: <what the standard requires>
**Impact**: <who is affected and how>
**Fix**: <concrete remediation, with code snippet if applicable>
**Effort**: <XS / S / M / L>

(repeat F-002, F-003, …)

## Patterns observed
- <Recurring issues across the system — these are the leverage points>

## What's working
- <Don't only complain — call out wins so they survive refactors>
```

## `severity-matrix.md`

```markdown
# Severity Matrix — <Subject>

| Finding | Severity | Affected | Effort | Priority |
|---|---|---|---|---|
| F-001 | Critical | All screens | S | P0 |
| F-002 | Major | Reader screen | M | P1 |
| F-003 | Minor | Settings row | XS | P3 |
| ... |

## Critical (P0) — fix immediately
- F-001 ...

## Major (P1) — fix in current sprint
- F-002 ...

## Minor (P2) — backlog
- ...

## Info (P3) — nice to have
- ...
```

## `remediation-plan.md`

```markdown
# Remediation Plan — <Subject>

## Phased rollout
### Phase 1 (this sprint) — P0 critical fixes
- [ ] F-001: <action> — owner: <role>
- [ ] F-002: <action> — owner: <role>

### Phase 2 (next sprint) — P1 major
- [ ] ...

### Phase 3 (backlog) — P2/P3
- [ ] ...

## Verification
- [ ] Re-run axe-core / Lighthouse / WAVE
- [ ] Manual contrast check on every text/background pair
- [ ] Screen-reader walkthrough (VoiceOver / TalkBack / NVDA)
- [ ] Keyboard-only navigation

## Stop-the-line
- If a P0 fix introduces regression, revert and re-design.
- If a P0 fix is impossible in current architecture, escalate to master.
```

## Severity rubric

| Severity | Definition | Examples |
|---|---|---|
| **Critical** | Blocks core user task, fails legal requirement, visible to all users | Login broken, no contrast on body text, RTL flipped, screen reader inaccessible |
| **Major** | Degrades task success for some users, fails WCAG AA | Form has no error message, hover-only controls, motion without reduced-motion fallback |
| **Minor** | Polish issue, best-practice violation | Inconsistent spacing tokens, mixed Latin/Arabic number conventions |
| **Info** | Worth noting, no urgency | Icon could be more semantically clear, copy could be friendlier |