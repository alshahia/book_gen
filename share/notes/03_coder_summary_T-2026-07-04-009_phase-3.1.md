# Coder Summary — T-2026-07-04-009 / Phase 3.1

**Date:** 2026-07-04
**Sub-agent:** coder (am-coder)
**Loop:** initial

## Tasks attempted
| ID | Status | Notes |
|----|--------|-------|
| P3T1 | done | Authored `templates/EXTRACTION.md` (644 lines) — rulebook mirroring `AUTHORING.md`; pre-flight encodes F1–F8. |
| P3T2 | done | Authored `extract/SKILL.md` + `extract/rules.md` (8 rules) + `.extract-config.yaml.example`; added CONTRIBUTING.md "via extract" subsection. |

## Files written / edited
- `templates/EXTRACTION.md` — created — extraction rulebook: TL;DR 8 rules, Rule details, "What extraction produces", pre-flight checklist (PF-1…PF-7 encoding F1–F8), 9-step recipe, worked example (cinematic-landing inline), refusals/WARN table, "what the agent can't decide", consumers + research-vs-authoring, companion cross-refs, versioning (v1.0.0), audit-log template.
- `agents_manager/extract/SKILL.md` — created — YAML frontmatter (`name`/`description`/`paths`); 8-step procedure; opt-in gating; lanes; non-standard `paths:` documented.
- `agents_manager/extract/rules.md` — created — 8 hard rules R1–R8 verbatim from synthesis v2; each cites the FAIL condition it gates.
- `agents_manager/memory/.extract-config.yaml.example` — created — `extract_enabled: false` + comments.
- `templates/CONTRIBUTING.md` — edited (+22 lines) — new `### I want to extract a finished project into a template` subsection between "add a new template" and "fix a bug"; references skill + rulebook; contrasts extraction (additive) vs manual authoring (full write).

## Commands run
- `python scripts/validate-frontmatter.py agents_manager/extract/SKILL.md` — exit 0 (`OK ... lenient`).
- `python -c "import yaml..."` (SKILL frontmatter + config) — both PASS. NOTE: env `python3` lacks PyYAML; `python` has it. The stdlib validator runs under either.
- Gate greps (anchors 34, rules 8, extract_enabled 2, CONTRIBUTING extract 9) — all ≥ threshold.
- `git diff --name-only` + `git ls-files --others` forbidden-zone check — **0 violations**.

## Tests run
- No unit tests in scope (docs/skill authoring). `verify.sh`/`validate-memory.sh` are invoked by FUTURE extraction runs (encoded in the rulebook), not by this build. Frontmatter validator: 1 file PASS.

## FAIL-condition encoding (F1–F8) — pointers in EXTRACTION.md pre-flight
- **F1** placeholder PASS lines → `templates/EXTRACTION.md` §Pre-flight PF-6 (rules.md R4)
- **F2** manifest resolvability → §Pre-flight PF-5 (R4)
- **F3** memory `USE THIS WHEN:` → §Pre-flight PF-6 (R4)
- **F4** H1 = filename prefix → §Pre-flight PF-6 (R4)
- **F5** LICENSE + attribution → §Pre-flight PF-1 (R3)
- **F6** secrets denylist → §Pre-flight PF-2 (R2)
- **F7** INDEX trigger phrases → §Pre-flight PF-6 (R4)
- **F8** source WARN register 0 OPEN → §Pre-flight PF-4 (R8)
- Consolidated in the "Pre-flight FAIL-condition coverage map" table + "Refusals and WARNs at a glance" table.

## Merged-risk coverage (R1–R12 from synthesis v2)
- R1 soft-wall erosion → skill lives only in new `agents_manager/extract/`; no specialist SKILL touched.
- R2/R9 IP/license → rules.md R3 + EXTRACTION PF-1; "can't decide" = human LICENSE call.
- R3 secrets → rules.md R2 + EXTRACTION PF-2 (denylist verbatim).
- R4 authoring drift → EXTRACTION sibling framing + rules.md R4 (verify.sh); Rule 8 unchanged.
- R5 UX framing → rules.md R7 + EXTRACTION Rule details 7 ("scaffold ~30s, not finished").
- R6 source open WARNs → rules.md R8 + EXTRACTION PF-4 (F8).
- R7 memory cross-pollination → rules.md R6 + `tech_stack:`/`domain:` tags (schema change is 3.2).
- R8 duplicate templates → EXTRACTION PF-3 (Jaccard >0.6 refuse / 0.4–0.6 WARN).
- R10 staleness → documented as deferred (controller_compat not shipped this build).
- R11 skip fatigue → `W-extract-skip-fatigue` in refusals table; auto-disable deferred.
- R12 over/under-generalization → EXTRACTION "What the agent can't decide" (brand generalization).

## Deviations from plan
- **Did NOT edit `tasks/T-2026-07-04-009.md`.** Dispatch boundaries state coder CANNOT edit `tasks/<id>.md` (master's lane), which overrides the SKILL.md "update tracker" step. Rows P3T1/P3T2 status + Coder path are master's to set.
- **Gate command interpretation:** dispatch literally wrote `python3 scripts/validate-frontmatter.py` (no args → returns 2) and `import yaml` one-liners. Ran the validator against the one new file with frontmatter (`extract/SKILL.md`) per plan done-when #6, and used `python` (has PyYAML) instead of `python3` (lacks it) for the yaml gates. Substantively PASS.

## Known issues / TODOs left in code
- **[MEDIUM] Real `.extract-config.yaml` is not gitignored.** `agents_manager/memory/.gitignore` ignores `**/*.md` only; a real `.extract-config.yaml` (non-.md) would be tracked. Adding the ignore rule is OUT of this sub-phase's 5-file scope. Documented in the `.example` + SKILL body ("operator should gitignore"). Recommend master add `.extract-config.yaml` to `agents_manager/memory/.gitignore` in 3.2 or a patch.
- **[LOW] CI `validate-frontmatter` job does not list `agents_manager/extract/SKILL.md`.** `.github/workflows/ci.yml:49-56` is a fence file (not touched). Adding the new SKILL to the CI arg list is a v0.15.x follow-up / master's call.
- **[LOW] Env `python3` lacks PyYAML** (only `python` has it). Not a repo defect; the stdlib `validate-frontmatter.py` is unaffected. Surfaced so review uses `python` for the yaml one-liners.
- Pre-existing `validate-frontmatter.py` tuple-unpack crash on no-frontmatter files (already in prior WARN registers) — avoided by only passing the frontmatter-bearing SKILL.md.

## Suggested review focus
- `templates/EXTRACTION.md` §Pre-flight — confirm each of F1–F8 is genuinely encoded and the rule citations (R2/R3/R4/R8) are correct.
- `agents_manager/extract/rules.md` R1–R8 — verify verbatim match to synthesis v2 (esp. denylist in R2, whitelist in R3, suffix format in R7, audit path in R8).
- `agents_manager/extract/SKILL.md` frontmatter — confirm `paths:` extension is acceptable and lenient-mode validation is the right call (documented deviation per dispatch caveat 1).
- Forbidden-zone preservation — `git` name-only + untracked list shows 0 fence-file matches.

## Self-critique
- **Did I do my job?** yes — 5 deliverables authored; all Done-when gates pass; F1–F8 encoded with pointers; 0 forbidden-zone violations.
- **What might I have missed?** The `.extract-config.yaml` gitignore gap is real but out-of-scope — surfaced, not fixed. The retroactive cinematic-landing worked-example trace is deferred (per plan); EXTRACTION.md references the exemplar inline instead, which may read as lighter than a full trace to the reviewer.
- **What did I assume without evidence?** That the Anthropic Skills `paths:` extension is acceptable for a non-`/skills/` file (mirrored `research/SKILL.md` shape + documented the deviation per dispatch caveat 1). That `python` (not `python3`) is the intended yaml interpreter in this env.

## Status signal
**DONE_WITH_CONCERNS** — all assigned tasks done and all gates pass; concerns are the out-of-scope `.extract-config.yaml` gitignore gap (MEDIUM, master to resolve in 3.2/patch) and two LOW CI/env notes. None block review.

READY_FOR_REVIEW: true
Memory written: agents_manager/coder/notes/semantic/extract-skill-as-non-roster-soft-skill.md
