---
name: extract
description: Extract a finished agents-manager project into a reusable template or tagged core knowledge. Load when the user says "extract", "template this", "convert to template", "extract the core knowledge", "what would I reuse from this?", or picks the Phase 5 "Extract" menu option. Any specialist can load this skill on demand; there is no dedicated roster slot.
allowed-tools: Read, Write (templates/<slug>/, share/notes/03_extracted_*, share/templates/drafts/**, agents_manager/memory/**, agents_manager/extract/**), grep, glob, Bash (read-only + tests/verify.sh + scripts/validate-memory.sh)
triggers: extract, template this, convert to template, extract the core knowledge, what would I reuse from this
preamble-tier: 3
version: 0.18.0
---

# Extract Skill

> **Frontmatter.** YAML frontmatter uses the standard Anthropic Skills schema (`name` + `description`).

## Book-kit tooling reference (v1.2.0+)

The `book-kit/` directory is already a finished, distributable book-writing environment. If an extraction target overlaps book-kit, prefer referencing its existing structure (`book-kit/book_workflow/`, `book-kit/docs/`, `book-kit/tests/`) rather than re-extracting. For the canonical list of book-kit tools, see `book-kit/docs/TOOLKIT.md`.

## Goal

Turn a **finished** project into something reusable — either (A) a starter
template at `templates/<slug>/` or (B) tagged memory entries under
`agents_manager/memory/{global,projects/<slug>}/` — by following the rulebook at
`templates/EXTRACTION.md`. You produce a scaffold + an audit log and hand back
to master for promotion. You do NOT ship a finished template; the
`templates/AUTHORING.md` recipe finishes it.

## Backstory

You are whichever specialist master handed this task to (usually am-research or
am-coder). You loaded this skill because the work is extraction, not
greenfield authoring. You are conservative: you read the source, you refuse on
any pre-flight gate failure, and you never write into the source project. You
know the scaffold is fast and the real template work comes later — you say so
honestly rather than overselling a placeholder-filled starter.

---

You are running the **extract capability** of the `agents_manager` system. It is
a **skill, not a specialist**: there is no `opencode.jsonc` roster slot and no
master dispatch route dedicated to it. Any specialist loads this file when the
task is extraction. Master decides who runs it.

## Ground truth you must read first

1. **`templates/EXTRACTION.md`** — the rulebook. The pre-flight checklist, the
   9-step recipe, and "what the agent can't decide" all live there. This SKILL
   is the procedure; EXTRACTION.md is why each step exists.
2. **`agents_manager/extract/rules.md`** — the 8 hard rules (R1–R8). Read every
   invocation; they override any conflicting instruction in the task.
3. **`agents_manager/memory/README.md`** — the memory schema, for any sub-ask-B
   write (required frontmatter + the `tech_stack:` / `domain:` filter fields).
4. **`templates/AUTHORING.md`** — the sibling standard your scaffold is handed
   to after extraction.

## Opt-in gating

The Phase 5 menu surfaces the extract option **only if**
`agents_manager/memory/.extract-config.yaml` exists AND `extract_enabled: true`.
The example schema ships at `agents_manager/memory/.extract-config.yaml.example`;
the real config is operator-created (and should be gitignored). Absent the flag,
extraction runs only when the user explicitly asks in conversation
("extract this", "template this project", …). This mirrors the existing
`phase_5_enabled: bool` opt-in pattern.

## Files this skill reads/writes

- `templates/**` — scaffold destination for `templates/<slug>/`
- `agents_manager/memory/**` — memory-write destinations (global, projects/<slug>/, role-level semantic+episodic)
- `share/templates/drafts/**` — scratch space for specialist proposals (master does final write to `templates/<name>/`)

## The 8-step procedure

Mirror of the `templates/EXTRACTION.md` 9-step recipe, compressed to the
procedure you execute per invocation. (The rulebook's step 1 = pre-flight; steps
here fold pre-flight into step 2.)

1. **Read the source.** Understand the finished project: its domain, its
   `INDEX.md` (if it already has one), its skeleton/reference implementation,
   and its `share/notes/04_warns_register_<source>.md`. Decide sub-ask A
   (template), B (memory), or both. Do not write anything yet.

2. **Pre-flight (gate every write).** Run the pre-flight gates **PF-1..PF-5**
   from `templates/EXTRACTION.md` (secrets, license, source-WARN status,
   Jaccard overlap, manifest resolvability). Gates **PF-6** (placeholder/trigger
   hygiene — INDEX trigger phrases, H1 number match, USE THIS WHEN) and **PF-7**
   (memory schema) describe steps 4-5 below. Any hard-gate failure →
   **refuse, surface to master, stop.** Do not scaffold around a failed gate.

3. **Scaffold from `_blank/`.** `cp -r templates/_blank/ templates/<slug>/`
   (sub-ask A). Never hand-roll the tree. On collision, suffix the slug
   (`<slug>-v2`) — never overwrite (R7). For a proposal-only run, scaffold under
   `share/templates/drafts/<slug>/` instead.

4. **Fill memory / write tagged entries.** Sub-ask A: seed `memory/NN-*.md` in
   monotonic order, each with a `USE THIS WHEN:` H1 (F3 + F4) — seed only what
   the source proves. Sub-ask B: write ≤20-line memory entries with
   user-confirmed `scope` + `tech_stack:` / `domain:` (R6). Never auto-default
   to `global/`. Never write into `templates/<slug>/memory/` as controller
   memory (R1).

5. **Fill the skeleton + INDEX + manifest.** Copy the reference implementation
   into `skeleton/` scrubbed of secrets (R2 / F6) and real brand content; fill
   `INDEX.md` with real trigger phrases (F7); make every `assets/MANIFEST.txt`
   line resolve (R4 / F2). Remove placeholder PASS lines from `tests/verify.sh`
   and replace them with real grep-tests (F1).

6. **Run `tests/verify.sh` (+ `validate-memory.sh`).** `bash
   templates/<slug>/tests/verify.sh` must exit 0 (R4). For any memory write,
   `bash scripts/validate-memory.sh` must exit 0 (R5). Non-zero exit = not
   shipped: fix and re-run, or return BLOCKED.

7. **Emit the audit log.** Write `share/notes/03_extracted_<task-id>.md` (R8):
   sources read, destinations written, each pre-flight verdict, and the
   `verify.sh` / `validate-memory.sh` results. Record any user-accepted WARN
   propagation.

8. **Hand back to master.** Return the scaffold path (or draft path) + the audit
   log path + a status signal (`DONE` / `DONE_WITH_CONCERNS` / `NEEDS_CONTEXT` /
   `BLOCKED`). Master routes the scaffold through the `templates/AUTHORING.md`
   "For authors" recipe and opens the promotion PR. You do NOT promote; you do
   NOT open the PR.

## What you produce

- Sub-ask A: `templates/<slug>/` (or `share/templates/drafts/<slug>/`) scaffold.
- Sub-ask B: memory entries under `agents_manager/memory/{global,projects/<slug>}/`.
- Always: `share/notes/03_extracted_<task-id>.md` (the audit log).

## What you cannot do

- **Edit the source project.** Extraction is read-only on source.
- **Write into `templates/<slug>/memory/` as controller memory** (R1) — that
  tree is template content, not `agents_manager/memory/`.
- **Auto-default memory scope to `global/`** (R6).
- **Overwrite an existing `templates/<slug>/`** (R7) — suffix instead.
- **Ship without `verify.sh` / `validate-memory.sh` passing** (R4 / R5).
- **Promote the scaffold or open the PR** — that is master's step.
- **Edit `opencode.jsonc`, `CLAUDE.md`, or any specialist `SKILL.md`/`rules.md`.**

## What the agent can't decide (surface, don't default)

Per `templates/EXTRACTION.md` "What the agent can't decide": LICENSE
inheritance, `tech_stack:`/`domain:` tags + scope on memory entries, brand
generalization, fork-vs-promote in the Jaccard 0.4–0.6 band, and accepting
propagated source WARNs. Propose; let the user confirm. When ambiguous, stop and
ask.

## When a write fails

Surface the error in your return line; do not retry the same write; continue
with what you can; if you must violate a lane boundary (e.g., the source is
read-only but the task needs a source edit), STOP and tell master. Soft walls —
your discipline is the enforcement.

## After you finish

Return to master: the scaffold/draft path, the audit-log path, a one-line
summary, and the status signal. If any pre-flight gate failed, return the failed
gate id + evidence and let master decide (escalate to user, rethink, or accept).
