# Novel Abstractions — Seed List (v2)

Two lists. Use freely the accepted (T) patterns; refuse the refused (R) patterns unless a fresh decision says otherwise.

When a new pattern emerges in real work, append to T or R with rationale. Never delete — mark superseded.

---

## Accepted (use freely)

### T1 — Token-only palette in mockups

Every color in every mockup comes from a CSS custom property (`var(--xxx)`) declared in `:root` (light) or a `[data-theme="..."]` block (themed). Inline hex is rejected by the lint gate.

**Why**: Theme switching becomes a single attribute swap. Designers don't redo work per theme.

### T2 — W3C Design Tokens (W3C spec format)

Tokens serialized as `{ $type, $value }` JSON, with $type from the W3C Design Tokens spec (color, dimension, fontFamily, fontWeight, duration, cubicBezier, etc.).

**Why**: Machine-parseable by Style Dictionary, Theo, and any modern token compiler. Survives framework changes.

### T3 — Dual `.md` + `.json` for every spec

Every spec ships in two files with identical content: `.md` (prose, human-readable) and `.json` (machine-readable). Both are required; lint rejects specs with only one.

**Why**: LLMs and humans read .md; agents and tools read .json. One source, two consumers.

### T4 — Locked dimensions per medium

Every mockup template has hardcoded dimensions that match the platform's spec:
- Mobile: 390×844 (iPhone X-class)
- Tablet: 1024×768 (iPad-class)
- Desktop: 1440×900 (laptop-class)
- Email: 600px (email-safe width)
- Print: A4 (210×297mm) or US Letter (8.5×11in)

**Why**: Designers don't second-guess canvas size. Reviews happen against a known frame.

### T5 — RTL via logical CSS properties

For RTL layouts (Arabic, Hebrew, Persian, Urdu), use `margin-inline-start`, `padding-inline-end`, `border-inline-start`, `text-align: start`. Never `margin-left`, `padding-right`, etc. for layout.

**Why**: Single CSS file works for LTR and RTL. Mirroring becomes automatic.

### T6 — Authentic content over lorem ipsum

For Quran app work: real Surah names, real ayahs, real reciters, real Hijri dates. For other apps: real product names, real user names, real copy. Never "Acme Corp" or "Lorem ipsum dolor sit amet."

**Why**: Lorem ipsum hides design problems. Real content exposes them.

### T7 — Status signal at the end of every dispatch

Every dispatch's `99_handoff.md` ends with `STATUS: DONE` / `DONE_WITH_CONCERNS` / `NEEDS_CONTEXT` / `BLOCKED`. Matches master's subagent dispatch contract.

**Why**: Master and humans can parse handoff state without reading the whole file.

### T8 — Scope-tiered output schema

The output tree branches by scope: small (one screen), medium (3-10 screens, one direction), full (system + multiple directions). Folders are created only when needed.

**Why**: Designers don't produce empty folders. The artifact set matches the actual task.

### T9 — Audience-aware handoff

`99_handoff.md` declares the next consumer (am-coder, human designer, PM, stakeholder, marketing, external agency, accessibility reviewer, localizer) and includes the right artifacts for each.

**Why**: A stakeholder doesn't want token JSON. A coder doesn't want executive summary. Audience-aware routing.

### T10 — Discovery before production

Before producing anything, am-design asks 7 questions (medium, audience, constraints, artifact set, mode set, scope tier, success criteria). No production without answered discovery.

**Why**: Prevents the "design assumed wrong medium" failure mode. Cheap to ask, expensive to redo.

### T11 — Self-critique before STATUS

Every dispatch ends with a self-critique against core + medium-specific + theme + locale + separation items. STATUS is only valid after self-critique passes or surfaces concerns explicitly.

**Why**: Catches the "looks done, isn't done" pattern. Self-critique is a gate, not a formality.

---

## Refused (don't use without a fresh decision)

### R1 — "Per-component theme file"

Don't create `Button.light.css`, `Button.dark.css`, etc. Theme is one attribute (`[data-theme="..."]`), one token map.

**Why it was refused**: Multiplies files. Branching in component code is the alternative — and that defeats the token layer.

### R2 — "Pixel-perfect to a raster mockup"

Don't accept mockups as PNG and try to recreate them pixel-for-pixel. Mockups are *visual reference*, not the spec.

**Why it was refused**: Loses responsive behavior, accessibility, and theming. Mockup is for alignment, not pixel source.

### R3 — "Emoji as ornaments or icons"

Don't use emoji (🌙 📖 ✨) as decorative UI elements. Use proper icons (SVG) or typography ornaments.

**Why it was refused**: Emoji render inconsistently across OS, can be mistaken for content, fail accessibility checks (most screen readers read emoji).

### R4 — "Auto-extract tokens from Figma / Sketch export"

Don't write a script to parse Figma JSON and generate tokens. Define tokens in W3C format, then import into Figma if needed.

**Why it was refused**: Round-trips lose information. Figma's token model ≠ W3C. The agent loses control of the schema.

### R5 — "Visual fidelity without browser verification"

Don't claim a mockup is visually correct without opening it in a browser (or browser tool) and screenshotting.

**Why it was refused**: CSS computes differently across browsers. Inline styles, font fallback, RTL math — all differ. Without verification, you're shipping assumptions.

### R6 — "Mobile-only design for projects that need responsive"

Don't deliver a 390px mockup for a project whose brief says "responsive web." Lock the canvas to the medium.

**Why it was refused**: Designers redo work. Mobile and responsive are different design problems (touch vs pointer, scroll vs paginate, viewport variability).

### R7 — "Static mockup when interactive prototype was requested"

If the brief says "prototype" or "click-through," produce HTML/CSS/JS that navigates between screens. A static mockup set is not a prototype.

**Why it was refused**: Stakeholders can't experience flow from static screens. Motion, transitions, and state changes need runtime to be evaluated.

### R8 — "Brand work without audience definition"

Don't design a brand identity without a defined audience. Color, type, voice all depend on who the brand speaks to.

**Why it was refused**: Brand is communication. Without audience, communication is guesswork.

### R9 — "Accessibility claim without WCAG verification"

Don't claim "WCAG 2.2 AA compliant" without running axe-core / Lighthouse / WAVE / manual checks. Document the test result.

**Why it was refused**: Compliance claims without evidence are legal risk. Verify, then claim with evidence.

### R10 — "Mixing scripts as decoration"

Don't use Arabic glyphs as decorative borders on a non-Arabic project, or Latin glyphs on an Arabic project. Glyphs are content, not ornament.

**Why it was refused**: Reads as cultural misappropriation. Triggers accessibility flags (screen reader announces the glyph).

### R11 — "Reinventing wheels"

Don't design a new component pattern (settings group, list row, modal) without checking what conventions exist for the medium (Apple HIG, Material 3, Fluent, Polaris, etc.).

**Why it was refused**: Users carry expectations from every app they've used. Custom patterns add cognitive load.

### R12 — "Skipping the audit step on existing products"

If the brief is "redesign X," first audit X. Don't redesign blind.

**Why it was refused**: Existing products have constraints (legacy data, accessibility certifications, user habits) the brief doesn't mention. Audit surfaces them.

---

## How to extend this list

Add to T or R with:
- One-line name
- One-paragraph pattern description
- One-paragraph rationale ("why accepted" or "why refused")
- Optional: example code or counter-example

Mark superseded entries with `~~strikethrough~~` and a one-line reason; never delete.

If a pattern changes status (accepted → refused or vice versa), add a new entry referencing the old one.