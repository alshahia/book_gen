# cinematic-landing — concrete fixes (v0.12.0 → v0.13.0)

The exemplar currently passes with notes; this file lists the notes in
priority order. Each item is a small diff; together they are < 60 lines.

Companion to `share/templates/AUTHORING.md`. Apply in order, run
`tests/verify.sh` after each batch.

---

## Fix 1 — Reconcile `--ink-faint` and `--gold-bright` with contrast audit

**Severity:** CRITICAL — skeleton ships values its own memory marks as failing.

**Where:**
- `templates/cinematic-landing/skeleton/index.html` line 74
  (`--ink-faint:#9A8975;` — the value memory/05 says fails)
- `templates/cinematic-landing/skeleton/index.html` ~line 321
  (`color:var(--gold-bright);` for `.idx` — `--gold-bright:#CC9A4A` is 2.35:1
  on `#FBF6EE` per memory/14's own table, fails AA body)

**Change:**

```diff
- --ink-faint:#9A8975;
+ --ink-faint:#7A6855;
```

And in `memory/14-dark-theme.md`, add a light-mode contrast footnote:

> Light-mode body text uses `--ink:#3A2E1F` (PASS 12.6:1) and
> `--ink-soft:#5C4D3A` (PASS 7.4:1) on `--paper:#FBF6EE`. Index markers
> (`.idx`) use `--gold-deep:#8B5E22` (PASS 6.8:1) — never `--gold-bright`
> on light, which fails AA body at 2.35:1.

Then update the skeleton's `.idx` rule:

```diff
- color:var(--gold-bright);
+ color:var(--gold-deep);
```

**Verify:** re-run `tests/verify.sh` after edit; visual contrast check via
WebAIM on light + dark.

---

## Fix 2 — Fix the `data-section="hero"` grep claim

**Severity:** CRITICAL — README tells the user to grep for an attribute the
skeleton does not have.

**Where:**
- `templates/cinematic-landing/00-readme-first.md` line 26
- `templates/cinematic-landing/skeleton/index.html` (sections use `id` +
  `data-ambient`, no `data-section` attribute)

**Two options, pick one:**

**Option A — add `data-section` to the skeleton** (recommended; makes the
section-name attribute a real, queryable contract):

```bash
# In skeleton/index.html, for each <section>:
-<section id="hero" data-ambient="...">
+<section id="hero" data-section="hero" data-ambient="...">
```

Apply to all 8 sections: hero, film, reveal, ritual, cta, editions, plus
`header` and `footer` (if they use `<section>`; otherwise keep as-is).

**Option B — change the README grep** to match the actual attribute:

```diff
- "Find sections with: `data-section=\"hero\"`"
+ "Find sections with: `id=\"hero\"` and `data-ambient=\"...\"`"
```

Option A is preferred because the `data-section` attribute is independently
useful (gating, analytics, future runtime decisions) and keeps the README
honest.

---

## Fix 3 — Renumber memory files and align H1s

**Severity:** HIGH — discovery is muddled; two `04-` files collide; H1s in
11/12/13/14 don't match filename prefix.

**Where:**
- `templates/cinematic-landing/memory/04-locale-handoff.md` (collides with
  `04-cinematic-hero.md`)
- `templates/cinematic-landing/memory/11-canvas-a11y.md` (H1 says "09 ·")
- `templates/cinematic-landing/memory/12-reduced-motion-listener.md`
  (H1 says "10 ·")
- `templates/cinematic-landing/memory/13-keyboard-nav.md` (H1 says "12 ·")
- `templates/cinematic-landing/memory/14-dark-theme.md` (H1 says "13 ·")

**Change:** move `04-locale-handoff.md` → `10-locale-handoff.md` and renumber
the additions to fill the gap (so locale-handoff becomes 10; the existing
11/12/13/14 shift down if needed for monotonic order — but the cleaner call
is to renumber the H1s in 11/12/13/14 to match their existing filenames, since
locale-handoff is the *new* arrival and gets the new number).

Concrete diff:

```bash
git mv templates/cinematic-landing/memory/04-locale-handoff.md \
       templates/cinematic-landing/memory/10-locale-handoff.md
```

Then in each file, fix H1:

```diff
# 11-canvas-a11y.md
- # 09 · Canvas a11y
+ # 11 · Canvas a11y — USE THIS WHEN: shipping a `<canvas>` that conveys
+   meaning and needs a screen-reader fallback

# 12-reduced-motion-listener.md
- # 10 · Reduced-motion listener
+ # 12 · Reduced-motion listener — USE THIS WHEN: implementing the
+   mid-session prefers-reduced-motion toggle

# 13-keyboard-nav.md
- # 12 · Keyboard navigation
+ # 13 · Keyboard navigation — USE THIS WHEN: shipping focus-visible,
+   Tab order, or scroll-snap keyboard handling

# 14-dark-theme.md
- # 13 · Dark theme
+ # 14 · Dark theme — USE THIS WHEN: defining or auditing dark-mode tokens
```

Each H1 now includes a `USE THIS WHEN:` line (Rule 6 in `AUTHORING.md`).

---

## Fix 4 — Reconcile memory/05 dark block with memory/14

**Severity:** HIGH — two sources of truth for dark tokens; an LLM cannot
tell which is canonical.

**Where:**
- `templates/cinematic-landing/memory/05-theming.md` (placeholder dark block
  with weak token values)
- `templates/cinematic-landing/memory/14-dark-theme.md` (canonical,
  WebAIM-audited)

**Change:** in `memory/05-theming.md`, replace the placeholder `[data-theme="dark"]`
block with a one-line reference:

```diff
- [data-theme="dark"] {
-   --paper:#0E0B07;
-   --ink:#F5EBD7;
-   ...placeholder values...
- }
+ /* Dark theme tokens: see memory/14-dark-theme.md (canonical, WebAIM-audited). */
```

Add the same canonical-pointer at the top of `memory/05`:

```diff
+ > Dark mode is documented in `memory/14-dark-theme.md`. This file
+ > covers light-mode mechanics and the `[data-theme]` selector.
```

**Verify:** grep for token values across `memory/` — only one file per token
should define it.

---

## Fix 5 — Fix section count and numbering in memory/01

**Severity:** MEDIUM — internal inconsistency in the build-flow doc.

**Where:** `templates/cinematic-landing/memory/01-builder-flow.md` stage 3.

**Change:** rewrite the numbered list to match the skeleton's 8 sections:

```diff
- 1. <section data-section="header">
- 2. <section data-section="hero">
- 3. <section data-section="film">
- 4. <section data-section="reveal">
- 5. section data-section="ritual">     <!-- missing backtick -->
- 6. <section data-section="cta">
+ 1. <header data-section="header">
+ 2. <section id="hero" data-section="hero" data-ambient="...">
+ 3. <section id="film" data-section="film" data-ambient="...">
+ 4. <section id="reveal" data-section="reveal" data-ambient="...">
+ 5. <section id="ritual" data-section="ritual" data-ambient="...">
+ 6. <section id="cta" data-section="cta" data-ambient="...">
+ 7. <section id="editions" data-section="editions" data-ambient="...">
+ 8. <footer data-section="footer">
```

Fix 2's Option A (`data-section` on every element) makes this list
accurate; without it, this list is fiction.

---

## Fix 6 — Update stale line counts

**Severity:** MEDIUM — three different numbers for the same file.

**Where:**
- `templates/cinematic-landing/00-readme-first.md` line 16: "700-line
  reference implementation"
- `agents_manager/upstream-contrib/PROPOSED_PATCH_v0.5.x_*.md` line 217:
  "885 lines"
- Actual `templates/cinematic-landing/skeleton/index.html`: **1097 lines**

**Change:** update both docs to match reality, or trim the skeleton to a
target number. Trimming 200 lines is plausible (the manifest/comment density
is high). Otherwise:

```diff
# 00-readme-first.md
- "700-line reference implementation"
+ "reference implementation (~1100 lines)"

# PROPOSED_PATCH
- "885 lines"
+ "1097 lines (grown post-merge; see cinematic-landing-fixes.md fix #6)"
```

---

## Fix 7 — Skeleton violates memory/04 hard rule #1

**Severity:** HIGH — skeleton uses the same image for aura + cutout.

**Where:**
- `templates/cinematic-landing/skeleton/index.html` line 208 (aura:
  `6195171`)
- `templates/cinematic-landing/skeleton/index.html` line 490 (cutout:
  `4046718`)
- `templates/cinematic-landing/memory/04-cinematic-hero.md` hard rule 1:
  *"NEVER use the same image with `filter: blur()` applied"*

**Change:** pick a different image for the cutout. Suggested candidates
(any Pexels photo with a strong subject on a neutral background):

```diff
- <img class="cutout" src="https://images.pexels.com/photos/4046718/...">
+ <img class="cutout" src="https://images.pexels.com/photos/<NEW-ID>/...">
```

Or, if no second image is available, soften the rule:

```diff
# memory/04-cinematic-hero.md, hard rule 1
- NEVER use the same image with `filter: blur()` applied.
+ PREFER two distinct images for aura + cutout. If only one image is
+ available, accept the parallax coupling and document the trade-off in
+ decision-log.md.
```

Document the trade-off in `decision-log.md` with a `P<n>` reference.

---

## Fix 8 — Trim `assets/MANIFEST.txt` to existing files

**Severity:** HIGH — manifest references a non-existent subtree.

**Where:**
- `templates/cinematic-landing/assets/MANIFEST.txt` lists 28 files
  including `agents_manager/assets/SKILL.md`,
  `agents_manager/assets/notes/branch-decisions.md`,
  `agents_manager/assets/resources/landing-review-checklist.md`
- The `agents_manager/assets/` subtree does **not** exist in the working
  tree. The `am-assets` 6th specialist (PROPOSED_PATCH F2) never landed.

**Change:** trim the manifest to existing files only:

```diff
- agents_manager/assets/SKILL.md
- agents_manager/assets/notes/branch-decisions.md
- agents_manager/assets/resources/landing-review-checklist.md
+ # (removed — am-assets specialist not yet landed; see
+ #  decision-log.md entry D-2026-07-04-am-assets-deferred)
```

Add a decision-log entry:

```markdown
## D-2026-07-04-am-assets-deferred

**Status:** deferred
**Context:** PROPOSED_PATCH v0.5.x proposed `am-assets` as a 6th
  specialist to own asset curation, rotation, and manifest auditing.
**Decision:** template ships without it. Asset work is staged inside
  `am-coder`'s build flow until usage justifies a dedicated specialist.
**Reopen when:** >2 templates need shared asset curation, or a single
  template's manifest exceeds 50 entries.
```

**Verify:** `tests/verify.sh` should add a `test_manifest_resolves` that
runs `awk '{print $1}' MANIFEST.txt | xargs -I{} test -e {}` (or
PowerShell equivalent on Windows).

---

## Fix 9 — Fix `output-skeleton.md` typo

**Severity:** LOW — one-character rot in the canonical folder tree.

**Where:** `agents_manager/design/resources/output-skeleton.md` line 106.

**Change:**

```diff
- share/hrief.md
+ share/handoff.md
```

---

## After all fixes

Run:

```bash
# from repo root
bash templates/cinematic-landing/tests/verify.sh
```

Expected: all greppable claims pass, no duplicates across memory files,
monotonic numbering, all manifest entries resolve.

Then tick every box in `AUTHORING.md` Rule 8 acceptance checklist.

The exemplar is then ready to graduate from PASS-WITH-NOTES to PASS, and
to be cited as the model other templates should clone from.