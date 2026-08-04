# Output Skeleton — `share/design/<task-id>/`

The canonical folder layout for any design dispatch. The tree is medium-aware and mode-aware: optional folders are created only when the corresponding mode is in the mode set.

```
share/design/<task-id>/
│
├── 00_brief.md                   ← ALWAYS. Restated task + medium + audience +
│                                   mode set + scope tier + success criteria
│                                   (answered during discovery).
│
├── 01_research/                  ← ONLY when mode includes RESEARCH
│   ├── competitive-analysis.md
│   ├── user-research.md
│   └── design-audit-input.md
│
├── 02_brand/                     ← ONLY when mode includes BRAND
│   ├── logo/
│   │   └── logo-placeholder.svg
│   ├── color-palette.md          ← + color-palette.json
│   ├── typography.md             ← + typography.json
│   ├── voice-and-tone.md
│   └── brand-guidelines.md
│
├── 03_system/                    ← ONLY when mode includes SYSTEMIZE or scope=full
│   ├── README.md
│   ├── tokens/
│   │   ├── base.json             ← W3C Design Tokens (theme-agnostic schema)
│   │   ├── tokens.css            ← compiled CSS vars (themes via [data-theme])
│   │   └── tailwind.config.example.js
│   ├── components/
│   │   ├── COMPONENTS.md         ← component catalog (prose)
│   │   └── components.json       ← machine-readable mirror
│   ├── patterns/
│   │   └── PATTERNS.md           ← recurring compositions
│   └── pages/                    ← per-page specs
│       ├── <screen-name>.md
│       └── <screen-name>.json
│
├── 04_mockups/                   ← ONLY when mode includes MOCK or PROTOTYPE
│   ├── <viewport>/               ← per medium — one folder each
│   │   │                           (mobile / tablet / desktop / web-responsive /
│   │   │                            email / brand)
│   │   ├── <screen-name>.html
│   │   └── index.html            ← all-in-one view of every screen in viewport
│   └── prototype.html            ← ONLY when mode=PROTOTYPE (interactive)
│
├── 05_audit/                     ← ONLY when mode includes AUDIT or EVALUATE
│   ├── findings.md               ← detailed findings
│   ├── severity-matrix.md        ← ranked by Critical / Major / Minor / Info
│   └── remediation-plan.md       ← concrete fixes per finding
│
├── 06_copy/                      ← ONLY when mode includes WRITE
│   ├── microcopy.md              ← strings, error messages, empty states
│   └── content-strategy.md       ← voice, tone, narrative arc
│
├── 07_primitives/                ← ONLY when mode includes ILLUSTRATE
│   ├── icons/
│   │   └── <icon-name>.svg
│   ├── illustrations/
│   └── motion/
│       └── motion-spec.md
│
├── 08_translations/              ← ONLY when mode includes TRANSLATE
│   └── <locale>/                 ← e.g. ar-SA, he-IL, fa-IR, ur-PK, en-US, zh-CN
│       ├── strings.md
│       ├── strings.json
│       └── locale-notes.md
│
└── 99_handoff.md                 ← ALWAYS. Audience-aware. Pointer file +
                                    "how to wire" + self-critique + STATUS signal.
```

## Per-mode decision tree (12 modes)

| Mode set includes… | Folders created |
|---|---|
| `RESEARCH` | `01_research/` |
| `CONCEIVE` | (extend `01_research/` with `01_research/concepts/<n>/SPEC.md`) |
| `BRAND` | `02_brand/` |
| `SYSTEMIZE` | `03_system/` |
| `MOCK` | `04_mockups/<viewport>/<screen>.html` + `index.html` |
| `PROTOTYPE` | `04_mockups/<viewport>/prototype.html` (interactive) |
| `EXTEND` | append to existing folder matching what is extended |
| `WRITE` | `06_copy/` |
| `AUDIT` | `05_audit/findings.md` + `severity-matrix.md` |
| `EVALUATE` | `05_audit/` (with accessibility focus) |
| `ILLUSTRATE` | `07_primitives/` |
| `TRANSLATE` | `08_translations/<locale>/` |

Every dispatch creates `00_brief.md` (overwrite or append on re-entry) and `99_handoff.md` (overwrite; version-bump if anything inside changes).

## Always present

- `00_brief.md` — overwrite or append on re-entry.
- `99_handoff.md` — overwrite on re-entry; version-bump if anything inside changes.

## What the **next agent** reads (audience-aware)

`99_handoff.md` declares the audience. The next consumer reads:

| Audience | Reads |
|---|---|
| `am-coder` | `99_handoff.md` → `03_system/tokens/*` → `03_system/components/components.json` → `03_system/pages/<name>.json` → `04_mockups/<viewport>/<screen>.html` |
| Human designer (Figma import) | `99_handoff.md` → `02_brand/*` → `04_mockups/<viewport>/index.html` → `07_primitives/icons/` |
| PM / Product owner | `99_handoff.md` → `04_mockups/<viewport>/index.html` → `01_research/competitive-analysis.md` |
| Stakeholder (executive) | `99_handoff.md` only (executive summary inside) |
| Marketing team | `99_handoff.md` → `02_brand/*` → `06_copy/*` |
| External agency | `99_handoff.md` → `02_brand/brand-guidelines.md` → `03_system/tokens/base.json` → `07_primitives/*` |
| Accessibility reviewer | `99_handoff.md` → `05_audit/` → `03_system/components/COMPONENTS.md` |
| Localizer | `99_handoff.md` → `08_translations/<locale>/strings.md` → `06_copy/microcopy.md` |

## Versioning

- Folder name is stable: `<task-id>` (e.g. `T-2026-07-15-001`).
- On re-entry, append new artifacts; do not silently overwrite history.
- When a token is renamed or removed, append a migration note to `99_handoff.md` (rule #7 in `rules.md`).

## What does NOT belong here

- Production source code (lives in `src/` or framework equivalent — `am-coder`'s lane).
- Test fixtures and CI configs (`am-coder` + `am-review` lane).
- API contracts / data shapes (`am-planning` + `am-coder` lane).
- Anything inside `agents_manager/` itself (controller files).