---
name: chub-validate
description: Use this skill BEFORE writing any new external import. chub fetches canonical docs for libraries/SDKs/APIs and is faster than reading .d.ts files. Use when adding imports, choosing between libs, hitting API errors, or starting work on any unfamiliar package. Skip for project-internal code and well-known stable packages like lodash.get or date-fns.
license: MIT
compatibility: opencode
metadata:
  audience: any agent
  workflow: chub-cli
---

## What is chub
chub (context-hub) is the canonical doc source for external modules/libraries/frameworks/SDKs/APIs. Single source of truth — installs via `npm install -g @aisuite/chub` and lives on `~/.chub/`.

## Workflow (1-2-3)

1. **search** — `chub search "<pkg>"` returns the registry id (e.g. `chub search "hpcc-js wasm"` → id: `hpcc-js/wasm`).
2. **get** — `chub get <id> --lang <ts|js|py|...>` fetches the canonical doc. ~20s first call, sub-second cached on subsequent lookups.
3. **cite** — copy the worked example's import shape verbatim where possible; cite `chub get <id>` in the work summary's `Commands run` block.

## When MANDATORY

- Any new `import` of an external package (one not already cited this turn).
- Choosing between multiple candidate libraries.
- Verifying a non-trivial API surface or a runtime-behavior bug.
- After `npm install <pkg>` succeeds, before the first call against that package.

## When NOT to use

- Project-internal code (use `grep` / `read`).
- Stdlib and native platform features (`fs`, `path`, `<input type="date">`, CSS over JS).
- Trivially-stable packages (`lodash.get`, `date-fns`, `uuid`).

## Anti-patterns (NEVER)

- Reading `node_modules/<pkg>/types/*.d.ts` as the validation step. Type shape ≠ behavior. A method can exist with the right signature and still return the wrong thing at runtime (e.g. `mermaid.initialize()` is `void`, not `Promise<void>`).
- Trusting training-data recall for non-trivial APIs.
- Skipping chub "to save time" — the fix-loop cost (research → code → build → error → read `.d.ts` → fix → re-validate) is much higher than one chub call amortized via cache.

## Worked example — `@hpcc-js/wasm`

Real failure cited in `agents_manager/upstream-contrib/06_chub_enforcement_feedback.md`:

```bash
chub search "hpcc-js wasm"
# → id: hpcc-js/wasm
chub get hpcc-js/wasm --lang ts
```

The doc returns (paraphrased):

> `const graphviz = await Graphviz.load(); const svg = graphviz.layout("digraph { a }", "svg", "dot");`

Notes the doc surfaces that recall would miss:

- capital-G `Graphviz` (not `graphviz`)
- `await` on `.load()` — returns a promise, not a namespace
- three-arg `.layout(src, format, engine)` — order matters

None of this is obvious from `.d.ts` or training data. One chub call would have prevented ~3 fix-loop iterations.

## Install

If chub is not on PATH:

```bash
npm install -g @aisuite/chub
```

If `npm i -g` fails (permission, no npm), surface to user. Do not silently fall back to `.d.ts` reading — that is the failure mode this skill exists to prevent.

## Plumbed enforcement

This skill ships alongside the `chub-gate` opencode plugin (in the same install). The plugin re-injects a condensed chub reminder into context after every compaction, so the rule survives mid-session memory loss even if this skill is not actively loaded.
