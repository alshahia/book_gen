# Web search strategy (v0.17.0+)

am-research's landscape scan runs in your lane. This doc is the standing playbook: query patterns, license filter, quality signals, skip conditions, result-size budget.

## Query patterns

For a domain scan, batch these patterns in a single turn (3–7 queries, adaptive):

| Pattern | Purpose |
|---------|---------|
| `"<problem> library <year>"` | recent options |
| `"<problem> vs <competitor>"` | pairwise comparison |
| `"<problem> open source alternative to <famous SaaS>"` | find OSS replacements |
| `"<problem> site:github.com language:<lang>"` | concrete candidates |
| `"<problem> benchmark <year>"` | performance / quality data |
| `"<problem> production usage"` | who's shipping with this |

For a deep-dive on a known candidate, single fetch is fine:

- `<canonical-doc-url>` — official docs
- `<github-repo>/blob/main/README.md` — readme of a known candidate

## Skip conditions

These come from `research/SKILL.md` `## Landscape scan`. If **any** is true, skip the scan and write the reason in `## Existing solutions`:

- User gave exact URL / known tool
- User said "from scratch"
- Trivial task (rename, typo, single-file refactor)
- Pure research, no code implication
- Well-trodden domain (e.g. "TODO app in React")

## Quality signals per recommendation

| Signal | Good | Bad | Why |
|--------|------|-----|-----|
| Last commit | <6 months | >1 year | Active maintenance |
| Open vs closed issues | close rate >70% | pile of stale | Responsive maintainers |
| License | MIT/BSD/Apache | AGPL, unlicensed | Compatibility, legal safety |
| Stars / downloads | context-dependent | sole signal | Vanity; can mislead |
| Releases | regular cadence | 1.0 in 2021, nothing since | Not a maintained product |
| Bus factor | >1 maintainer | single maintainer, no co-maintainers | Risk if maintainer disappears |

## License filter

| License | Flag in scan output? | Why |
|---------|---------------------|-----|
| MIT, BSD, Apache 2.0 | No | Permissive, no copyleft, no patent surprise |
| LGPL | Flag with "weak copyleft, dynamic linking OK" | Usually fine for libs, careful with static linking |
| MPL 2.0 | Flag with "file-level copyleft" | Modifications to MPL files must be shared |
| GPL (any) | Flag if project is proprietary or unknown | Strong copyleft, contaminates the work |
| AGPL (any) | **Always flag with "network copyleft"** | Even SaaS use triggers source disclosure |
| Unlicensed | Flag with "verify license before use" | No grant = no legal right to use |
| Unknown (no LICENSE file) | Flag with "verify license before use" | Same as unlicensed until proven otherwise |

## Result-size budget

- Default 30KB total raw result per turn.
- If a single result >20KB, summarize the relevant sections, do not paste full.
- If total >30KB, prioritize top 2–3, skim the rest on demand.

## Rabbit-hole follow-up

If the first round reveals an unexpected angle, do **one** follow-up turn with 2–3 deeper queries — not a full second scan. The follow-up queries should be tightly scoped to the angle, not a re-broadcast of the original 3–7.

## See also

- `research/SKILL.md` — `## Landscape scan` section, output template
- `research/rules.md` — rules 13, 14, 15
- `docs/TRACE.md` — audit trail for the scan's actions
