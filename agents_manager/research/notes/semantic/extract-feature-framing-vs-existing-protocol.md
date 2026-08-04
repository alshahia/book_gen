---
scope: role
topic: extract-feature-framing-vs-existing-protocol
status: active
created: 2026-07-04
last_verified: 2026-07-04
---

## TL;DR

When a user asks for an "extract-to-template" / "extract-the-core" feature, before proposing a new tool, map the ask onto (a) the v0.13.0 memory-write protocol for "core knowledge" and (b) `templates/_blank/` + `templates/AUTHORING.md` 9-step recipe for "template scaffold". The user is almost always reinventing an existing protocol.

## Context

T-2026-07-04-009 angle C: user wants meta-tooling that turns a finished project into either a reusable template or a compact "core knowledge" extract. Operations analysis surfaced that both surfaces already exist (memory protocol + rulebook recipe), and the user's "~30s" framing for the full scenario contradicts the rulebook's 9-step recipe (which takes hours-to-days for a contributor).

## Insight

The two scenarios in the dispatch map cleanly:
- **Scenario X (lightweight / "core knowledge"):** a memory write to `agents_manager/memory/projects/<slug>/` via the existing protocol (`agents_manager/memory/README.md:27-60`). 20-line cap, secrets-free, append-only, 3-question durable-insight gate. Tool = thin wrapper around existing writer.
- **Scenario Y (full template):** a `cp -r _blank/ templates/<name>/` plus `tests/verify.sh` plus the 9-step recipe (`templates/AUTHORING.md:248-290`) plus Rule 8 acceptance checklist (12 items). Tool = starter-scaffold only; the rest is human-driven.

The non-obvious part: the dispatch prompt's "30s" framing for scenario Y is a UX lie. Scaffold is fast (~30s). Completing the rulebook is not. Honest framing: "Scaffold a starter (~30s, placeholders only); complete the 9-step recipe afterwards."

## Source

`share/notes/01_research_T-2026-07-04-009_angle-operations.md` §F1-F14 + R1-R3.

## Verification

At future re-entry on any "extract-to-template" or "extract knowledge" user task, before writing the research file, run `ls agents_manager/memory/ && ls templates/` — if both exist, this note applies and the new task is a wrapper around the existing protocol, not a new tool.