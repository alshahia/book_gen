---
name: mavis-team
description: >
  Coordinate a Mavis multi-agent team plan. Use only when the user explicitly
  invokes /mavis-team or /team, or 100% unambiguously asks to use an agent team
  / multi-agent team. Do not infer team use from complexity, deep research,
  long-running work, parallelism, specialist value, or verification risk.
---

# Mavis Team

Use this skill to coordinate multiple agents toward one final deliverable, but
only after an explicit slash invocation or a 100% unambiguous user request to
use the agent team. The owner keeps responsibility for planning, launch,
intervention, final decisions, CI/CR waiting, merge, and cleanup. Workers
produce bounded deliverables and exit.

## Hard rules

- User-facing text follows the user's language: `plan.name`, task `title`,
  decision `message_to_user`, and prose in `prompt` / `verify_prompt`.
  Technical tokens, file paths, schema fields, and commands can stay literal.
- Before launching or monitoring a team plan, read exactly one platform command
  reference: `references/commands-windows-powershell.md` for `win32`, or
  `references/commands-macos-linux.md` for `darwin` / `linux`. If platform is
  unknown, do a tiny preflight first. Do not translate shell recipes from
  memory.
- A team plan must choose a validation closure: independent verification, a
  final PASS/FAIL gate, or a concrete low-risk skip reason.
- Do not create new agents for an implicit need without explicit user consent.
- Do not use this skill merely because the task is complex, research-heavy,
  long-running, parallelizable, or risky. Those are planning considerations only
  after the explicit team trigger has already been met.

## When not to use a full team

If this skill loaded without an explicit `/mavis-team`, `/team`, or 100%
unambiguous agent-team request, stop and continue in the owner session. Do not
launch a team plan.

When the explicit trigger is present, still use the smallest sufficient plan.
Prefer one owner plus a light verifier when that satisfies the user's explicit
team request; use broader parallel deliverables only when they genuinely reduce
time or risk.

## Plan preflight

Before writing YAML, answer these in your head:

1. What is the final deliverable?
2. Why is a team better than one owner plus a light verifier?
3. Which deliverables can run independently, and which dependencies are real?
4. Which agents, tools, sources, and files does each track need?
5. What evidence closes the plan: per-task verifier, final gate, or skip reason?

For software engineering tasks, read `references/software-engineering.md` when
the work spans components, requires worktree/run-location choices, or needs
code-specific verification strategy.

## Split the work

Split by verifiable deliverable, not by activity. A good task can be completed
by a fresh worker with its prompt, the auto-injected retry context, and the
repository.

For large, long-running, or complex work, split like a human engineering team:
parallel owners deliver bounded slices, review/test at handoffs, then use final
E2E/integration as the closing signal.

Maximize useful parallelism: run independent deliverables in parallel when they
have distinct outputs, tool surfaces, or verification boundaries. Use
`depends_on` only for real output consumption, shared contracts, integration, or
shared mutable runtime.

For serious recommendations that depend on separable evidence streams, split the
streams first, then synthesize. For example, revenue impact, churn risk, support
cost, source audit, and final recommendation can be separate bounded
deliverables when each can be checked independently.

Avoid two bad splits: do not split one coherent task into ritual steps such as
"research", "implement", "format"; and do not serialize independent tracks
merely because their outputs later meet in one MR, report, or release.

If tracks feel coupled, first write the shared contract into prompts or create
one contract task, then fan out. Serialize only the part that truly shares
state.

## Pick or design agents

Before writing `assigned_to` or `verified_by`, discover the active roster from
`<agent-context>` or the selected platform reference's list-agents/list-peers
recipe. Use exact available agent names. Prefer project-specific agents, use
`general` for one-off work with no specialist, and remember that the same agent
can handle multiple tasks in separate sessions.

When a needed role is missing:

- Do not treat a missing named specialist as a blocker by itself. For one-off
  serious work, prefer an existing agent plus explicit evidence, calculations,
  and verification when that can produce a reliable result.
- If the gap is discovered during planning, do not create an agent silently.
  State the blocked task, the closest existing agent, and a sufficient but not
  excessive set of candidate agents, each with name, scope, and stop condition.
  Propose only roles that are reusable beyond the current task; keep the set
  small and wait for user approval.
- If the user explicitly asked to add agents, define sufficient but not
  excessive agent specs and load `create-agent`; ask only when name, scope, or
  stop condition is unclear.

This skill decides whether a roster gap exists and what handoff is needed;
`create-agent` writes the agent files.

Size the roster to real independent work. Do not add a PM/orchestrator agent,
clone roles, use seniority names, or pad the team "just in case".

## Validation closure

Choose the smallest closure that gives trust:

- Use `verified_by` for serious/risky `produce` tasks: when an error would be
  hard to notice, expensive to recover from, or likely to mislead downstream
  work or external users.
- `depends_on` alone does not require `verified_by`; it describes execution and
  data flow. For low-risk `produce` output, omit `verified_by` with a concrete
  planner-written `verify_skip_reason` when downstream checks, the final
  closure, or owner/user direct review are enough.
- `role: verify-as-task` means the task deliverable is the verdict: E2E report,
  smoke check, audit verdict, cross-check report, or integration gate result. It
  omits `verified_by` by default, even when consumed downstream.

Write `verify_prompt` as independent checks against primary evidence, not as a
request to grade the producer's summary. Ask the verifier to run relevant
commands, inspect original sources, recalculate key numbers, compare critical
dates/quotes, or test the boundary that carries the risk.

Do not add a final `verify-as-task` merely because the plan has multiple tasks
or ends with a recommendation. If the final producer already has an independent
verifier, add a final gate only when it checks a distinct end-to-end boundary.

For large multi-phase code work, verify each meaningful phase or contract
boundary before downstream work builds on it. Do not rely only on a final
integration gate; late defects are harder to isolate, retry, and merge.

## YAML template

Use only fields the plan needs. Values wrapped in `<...>` are variable
placeholders; replace them with concrete values before launch. Translate
user-facing strings before launch.

​```yaml
version: 1
plan:
  name: '<user-language plan name>'
  max_concurrency: 10
  max_consecutive_failures: 2
  max_cycles: 10
  auto_reject_retries: 1
  verifier_config:
    default_verifiers: [verifier]
    audit_sample_rate: 0.0
tasks:
  # Serious/risky produce task: verify independently.
  - id: '<task-id>'
    title: '<user-language title>'
    prompt: '<self-contained producer spec, expected files/output, stop condition>'
    assigned_to: '<exact-agent-name>'
    verified_by: verifier
    verify_prompt: '<independent re-derivation steps and PASS/FAIL standard>'
    max_retries: 2

  # Low-risk produce task: skip verifier with a concrete reason.
  - id: '<low-risk-task-id>'
    title: '<user-language title>'
    prompt: '<self-contained producer spec, expected files/output, stop condition>'
    assigned_to: '<exact-agent-name>'
    verify_skip_reason: '<why downstream checks, final closure, or direct review are enough>'
    max_retries: 1

  # Optional final verification gate: use when the real trust anchor is a verdict.
  - id: '<final-gate-id>'
    title: '<user-language title>'
    role: verify-as-task
    prompt: '<run the E2E/integration/audit check and report PASS/FAIL>'
    assigned_to: '<tester-or-verifier-agent>'
    depends_on: ['<upstream-task-id>']
    max_retries: 1
​​