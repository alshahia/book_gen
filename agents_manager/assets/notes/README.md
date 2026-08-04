---
title: Assets notes
scope: canonical-pointer
status: active
created: 2026-07-03
last_verified: 2026-07-03
---

# Assets notes

This folder has **two distinct trees** with different semantics. Do not conflate them.

## Memory tree (`semantic/`, `episodic/`)

Standard per-role memory tree for am-assets. Schema, lifecycle, and read/write protocol live in the canonical source-of-truth: [agents_manager/memory/README.md](../../memory/README.md).

## Runtime-task playbook (`branch-decisions.md`)

`branch-decisions.md` is a **different** artifact — it documents decisions about branches shipping downstream user-facing content (templates, releases). It is owned by am-assets but lives outside the memory protocol. See [agents_manager/assets/SKILL.md](../../assets/SKILL.md) for the full convention.

## Rule of thumb

- Writing **insight about am-assets's role** (what the specialist should know on re-entry) → `semantic/<topic>.md` or `episodic/<task-id>.md` per the canonical schema.
- Writing **decision about a runtime-task branch** (which template patch, which release line) → append to `branch-decisions.md`.