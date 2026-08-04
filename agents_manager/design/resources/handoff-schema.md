# Handoff Schema — `share/messages/design-to-coder-<task-id>-handoff.md`

The wire format that bridges `am-design` → `am-coder`. `am-coder` reads this file as the **first input** after the task id and dispatch prompt.

## File template

```markdown
# Handoff: design → coder

**Task id:** T-YYYY-MM-DD-NNN
**Modes executed:** {CONCEIVE, SYSTEMIZE, MOCK, EXTEND, AUDIT}
**Scope tier:** small | medium | full
**Status:** DONE | DONE_WITH_CONCERNS | NEEDS_CONTEXT | BLOCKED
**Date:** YYYY-MM-DD

## Artifacts (paths `am-coder` must read)

- `share/design/<task-id>/00_brief.md` — restated user task (for context)
- `share/design/<task-id>/99_handoff.md` — pointer + token wiring snippet
- `share/design/<task-id>/01_directions/<n>/SPEC.md` — visual direction (if multi-direction)
- `share/design/<task-id>/01_directions/<n>/mockup.html` — visual reference
- `share/design/<task-id>/02_system/tokens/base.json` — token map (if scope=full)
- `share/design/<task-id>/02_system/tokens/tokens.css` — compiled CSS vars (if scope=full)
- `share/design/<task-id>/02_system/components/components.json` — component catalog (if scope=full)
- `share/design/<task-id>/02_system/pages/<name>.json` — per-screen spec (if scope=full)

## How to wire tokens into your framework

A 2-paragraph copy-paste-able snippet. Example:

> 1. Copy `02_system/tokens/base.json` into your project as `src/design/tokens.json`.
> 2. Compile to CSS vars, Tailwind config, or ThemeData at build time. Theme switching = swap `[data-theme="..."]` on `<html>` or pass a `theme` prop to your provider. Do NOT branch component code per theme.

If the framework is known (e.g. user said "React Native"):

> 1. Copy `02_system/tokens/base.json` into `src/design/tokens.json`.
> 2. Build a `<ThemeProvider value={tokens}>` from it; wrap your app root.
> 3. Components consume `theme.color.bg`, `theme.space[4]`, etc. — never raw values.
> 4. Theme switching = call `setTheme("01-traditional-illuminated")` from your settings screen.

## Top 3 things `am-coder` MUST NOT do

1. **Do not invent new token names.** If you need a color/spacing/radius not in `base.json`, ask master to dispatch `am-design` to extend the schema. Don't hardcode.
2. **Do not branch component code per theme.** One component, semantic tokens, theme attribute. This is the whole point.
3. **Do not write RTL CSS with physical properties.** `margin-inline-start` only. Verify RTL on at least one screen per theme before declaring done.

## Top 3 open questions

1. <specific UX or visual question that needs user input — `am-coder` cannot decide>
2. <one>
3. <one>

If empty, write "None — proceed with implementation."

## Self-critique (filled by `am-design`)

- Did every screen in every mockup use `var(--xxx)` tokens? yes / partial / no — explain
- Do .md and .json specs match? yes / partial / no — explain
- Did you open every `mockup.html` in a browser and verify? yes / no — N/A if no browser tool
- Contrast checked for `accent-on-bg`, `ink-on-bg`, `line-on-bg` in each theme? yes / partial / no
- RTL verified on ≥2 sample screens per theme? yes / partial / no / N/A

## Visual verification (if browser available)

- `share/screenshots/<task-id>_<direction>_<screen>.png` — one per shipped mockup
- ✓/✗/⚠ per visible element vs SPEC.md

## STATUS: <signal>

DONE | DONE_WITH_CONCERNS | NEEDS_CONTEXT | BLOCKED
```

## What `am-coder` does with this file

1. Reads `## Artifacts` paths and pulls them all into context.
2. Follows `## How to wire tokens` to set up the framework integration.
3. Obeys `## Top 3 things MUST NOT do` (these are hard constraints, not suggestions).
4. Surfaces `## Top 3 open questions` to master before implementing them — does NOT guess.
5. Checks `## STATUS` — if not DONE, asks master before proceeding.

## What the master does with this file

- Logs the path in `share/notes/99_progress_<task-id>.md`.
- Routes any `## Top 3 open questions` to the user before dispatching `am-coder`.
- If `STATUS: BLOCKED` or `STATUS: NEEDS_CONTEXT`, pauses the pipeline.