---
title: Novel-Abstraction Seed List (chunk-size protocol, v0.7.0+)
extends: ../../rules.md § Complexity estimation
maintained_by: anyone who encounters a new pattern that feels novel to a reviewer
---

# Novel-Abstraction Seed List

When the planner fills `novel_abstractions` in a phase's `### Complexity` block, the entries should be drawn from this list — **extended by the planner when they encounter a pattern that's clearly novel but not yet catalogued**.

## Curated entries (8 — the obvious ones)

These cover patterns that typically feel like "learning on the job" for a full-stack engineer reviewing unfamiliar code:

- **Lazy-loaded heavy editors** (Monaco / CodeMirror / Slate) — reviewer has no prior pattern to anchor against
- **Sandboxed iframe with custom origin / CSP** — new plugin / middleware pattern
- **Sub-application with independent build pipeline** — whole new build subgraph
- **Runtime external API integration** (not just type-imported) — actual network/IO at runtime, not compile-time stubs
- **WebSocket persistent connection** — bidirectional state, reconnect logic, message protocol
- **WebRTC peer connection** — signaling, ICE candidates, media tracks
- **WASM / background workers / service workers** — off-main-thread compute, complex lifecycle
- **Custom build tools / plugin authoring** — extending the build system itself

## Patterns that look novel but are NOT (don't enumerate these)

- Custom Tailwind classes (theme tokens — trivial)
- CSS animations / Framer Motion (well-known libraries)
- React context providers (well-known pattern)
- A new shadcn/ui component (existing library)
- Standard fetch with retries (well-known)

These should NOT trigger `novel_abstractions` unless something genuinely unprecedented is happening.

## How to extend this list

If you encounter a pattern that:
1. Is genuinely novel (not in the "NOT" section above), AND
2. Would make a reviewer uncomfortable without domain experience,

Then:
1. Name it inline in your Complexity block (don't skip the entry just because it's not on the list)
2. Flag it in your plan's "Why this design" summary
3. Open a PR to add it here with a one-line description of why it's novel

The owner reviews additions quarterly.