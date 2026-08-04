---
scope: role
topic: template-memory-vs-agents_manager-memory
status: active
created: 2026-07-03
last_verified: 2026-07-03
---

## TL;DR

When copying source `memory/*.md` files into an agents_manager v0.13.0+ project, they go into `templates/<name>/memory/` (template-author lane, no frontmatter required), NOT into `agents_manager/memory/{global,projects}/` (controller-internal lane, requires frontmatter per `agents_manager/memory/README.md`).

## Context

T-2026-07-03-003: copy source's `cinematic-landing-kit-demo/memory/{09-canvas-a11y,10-reduced-motion-listener,12-keyboard-nav,13-dark-theme}.md` into our project. Initially ambiguous because v0.13.0 memory system has frontmatter requirements that the source files lack.

## Insight

The discriminator is the `no-write-into-templates` fence at `agents_manager/memory/README.md:113-116`: "Do NOT write into `templates/<name>/memory/`. That's the template author's lane." Source memory files are runtime-task playbook content (about template section implementation patterns) — they belong in `templates/<name>/memory/`, which has NO frontmatter requirement. The v0.13.0 schema (frontmatter `scope, topic, status, created, last_verified`) applies ONLY to `agents_manager/memory/{global,projects}/` and `agents_manager/<role>/notes/{semantic,episodic}/`. Verified: all 10 of our existing `templates/cinematic-landing/memory/*.md` files have zero frontmatter.

## Source

`share/notes/01_research_T-2026-07-03-003.md` §E (v0.13.0 constraints) + §K (template file numbering) + R2 (frontmatter non-application)

## Verification

`Get-ChildItem E:\context_gen\templates\cinematic-landing\memory -Filter *.md | %{$_.FullName}` — all 10 files have no frontmatter (`Get-Content ... -Head 3` returns just `# 0N · ...`). Confirm at future re-entry.