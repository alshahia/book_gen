# Extract Skill — Standing Rules

These 8 hard rules apply **every** time the extract skill is loaded. They
override any conflicting guidance in the user task. They are the enforceable
core of `templates/EXTRACTION.md`; the rulebook explains *why*, this file states
*what you must never do*.

Each rule notes which am-review FAIL condition (`F1`–`F8`, from
`share/notes/01_research_T-2026-07-04-009_angle-operations.md:178-185`) it gates,
where applicable.

## R1: Never write controller memory into `templates/<name>/memory/`.

- `templates/<name>/memory/` is the **template author's** lane (runtime playbook
  content shipped with the template). The `agents_manager/memory/` tree is
  controller-internal specialist knowledge. They are distinct trees.
- Sub-ask A may **seed** `templates/<slug>/memory/` as *template content* per the
  AUTHORING recipe, but never as an `agents_manager/memory/` entry.
- Sub-ask B writes ONLY to `agents_manager/memory/{global,projects/<slug>}/`.
- Rationale: mixing the two lanes contaminates the controller memory read budget
  and breaks the `agents_manager/memory/README.md` fence.

## R2: Never write secrets. Refuse and surface on a pre-flight hit. (→ F6)

- Scan every candidate file before writing it. Denylist:
  - **Paths:** `.env*`, `*.pem`, `*.key`, `id_rsa*`, `02_secrets_*`
  - **Content:** `sk-[A-Za-z0-9]{20,}`,
    `-----BEGIN [A-Z ]*PRIVATE KEY-----`
- Any hit → refuse the file, surface the path + matched pattern to master.
- A confirmed false positive (e.g. a test fixture `sk-test...`) is a
  `W-extract-secrets-near-miss` WARN, acceptable only with explicit user
  confirmation recorded in the audit log.
- Never reference a `share/notes/02_secrets_*` path in any written artifact
  (same rule as memory entries and CHANGELOG).

## R3: Never copy a LICENSE without attribution. Refuse if unattributed. (→ F5)

- `templates/<slug>/LICENSE` must exist, carry an attribution line naming the
  source, and be on the whitelist:
  **MIT, Apache-2.0, BSD-2-Clause, BSD-3-Clause, ISC, CC0, CC-BY, or a
  user-declared-equivalent.**
- Unknown, copyleft-incompatible, or unattributed license → **refuse**; LICENSE
  inheritance is a human call (see EXTRACTION.md "What the agent can't decide").
- Never silently omit the LICENSE to dodge the check — a missing LICENSE also
  fails F5.

## R4: Always invoke `tests/verify.sh` after scaffolding. Non-zero exit = FAIL. (→ F1, F2, F3, F4, F7)

- Run `bash templates/<slug>/tests/verify.sh` after the scaffold is filled.
- It gates: manifest resolvability (F2), memory `USE THIS WHEN:` triggers (F3),
  H1-number-matches-filename (F4), no-placeholder-PASS-lines (F1). Confirm the
  INDEX real-trigger-phrase check (F7) separately if verify.sh does not cover it.
- Non-zero exit means the artifact is **not shipped**. Fix and re-run, or return
  BLOCKED. Never mark done with a red verify.sh.

## R5: Always run `scripts/validate-memory.sh` after writing memory entries.

- For any sub-ask-B write, run `bash scripts/validate-memory.sh` and require
  exit 0.
- It lints required frontmatter (`scope`, `topic`, `status`, `created`,
  `last_verified`), scope/status enums, and date parsing per
  `agents_manager/memory/README.md`.
- The new `tech_stack:` / `domain:` fields are additive; they do not replace any
  required key.

## R6: Never auto-default memory scope to `global/`. Require user-confirmed scope per entry.

- Every extracted memory entry's `scope` (`global` | `project`) is a
  **user-confirmed** choice, per entry. `global/` is never the silent default.
- `tech_stack:` and/or `domain:` tags are likewise proposed by the agent and
  confirmed by the user (they are the read-side filter words).
- Rationale: an over-eager `global/` write cross-pollinates unrelated projects
  (locked-design R6 / merged-risk R7).

## R7: Never overwrite an existing template. Suffix on collision.

- If `templates/<slug>/` already exists, scaffold `templates/<slug>-v2/` (then
  `-v3`, …). Never `cp -r` over an existing tree.
- If a memory `topic:` already exists, **supersede** it per the
  `agents_manager/memory/README.md` lifecycle (`status: superseded` +
  `superseded_by:`), never clobber the body.
- Suggested suffix format: `<slug>-v2`, `<slug>-v3`.

## R8: Always emit an audit log at `share/notes/03_extracted_<task-id>.md`. (→ F8)

- Every run writes the audit log recording: sources read, destinations written,
  each pre-flight verdict (PF-1…PF-7), and the `verify.sh` /
  `validate-memory.sh` results.
- The log MUST record the PF-4 source WARN-register check
  (`share/notes/04_warns_register_<source>.md` had 0 OPEN entries, or the
  user-accepted exception). This is the F8 receipt.
- The audit log is the extraction's proof of gate compliance; a run without it
  is incomplete.
