# Cinematic Landing — Review Checklist

`am-review` reads this BEFORE reviewing any cinematic-landing task. It codifies the
quality bar from `templates/cinematic-landing/memory/09-quality-bar.md`.

## P0 — Hard rules (any failure = FAIL)

- [ ] No `video.currentTime = …` assignment in any file (grep, exclude comments)
- [ ] No `<video>` tag in markup (allowed only when branch = B per manifest)
- [ ] No `mix-blend-mode` on GSAP-transformed elements (read CSS + JS transform handlers)
- [ ] `.fallback-host.is-missing` exists, wired with image `error` listener
- [ ] `prefers-reduced-motion: reduce` honored (CSS media query + JS matchMedia + mid-session listener)

## P1 — Asset integrity

- [ ] All asset URLs HEAD-200
- [ ] `assets/MANIFEST.json` matches the URLs in the HTML
- [ ] Branch declared in `assets/MANIFEST.json` matches the implementation chosen
- [ ] If branch = A: `frames[]` present + non-empty
- [ ] If branch = B: `video_url` present + HEAD-200
- [ ] If branch = C: `still_urls[]` length 5–6
- [ ] If branch = D: `ask_list` present + concrete (specific, attainable, time-bounded)

## P1 — Structure & DNA

- [ ] 8 sections present (`<header>`, hero, film, reveal, ritual, cta, editions, footer)
- [ ] Header hide/show on scroll direction (search for header + scroll handler)
- [ ] Lenis + GSAP single ticker (one `gsap.ticker.add`, no extra RAFs)
- [ ] Per-section `data-ambient` attribute (or documented exception)

## P2 — Brand voice

- [ ] No marketing clichés (`grep` for luxurious | premium | artisanal | curated returns zero hits in the deliverable)
- [ ] Tagline consistent across hero, header, footer
- [ ] Copy is sensory, second-person, concrete

## P3 — Documented deviations

- [ ] Branch C crossfade implemented as specified (Path C in memory/02)
- [ ] Branch B video ambient implemented as specified (Path B in memory/02)
- [ ] 3-frame CTA click-advance implemented as specified (memory/08)

## P4 — Code quality

- [ ] No console errors at parse time (run `node --check` on extracted JS)
- [ ] No dead code, no commented-out blocks of unrelated work
- [ ] No `eval`, no `Function()`, no unsafe patterns
- [ ] CSS specificity not exploding (no `!important` chains beyond the reduced-motion block)
- [ ] Inline JS uses `const`/`let`, not `var`

## P1 — Locale

- [ ] `<html lang dir>` attributes set per template's `04-locale-handoff.md`
- [ ] No hardcoded English-only strings (or documented why)
- [ ] RTL layout works (if `dir="rtl"`, visual spot-check)

## Verdict

- **PASS** — all P0 + P1 pass, P3 deviations implemented as specified
- **PASS-WITH-NOTES** — all P0 + P1 pass, P2/P3/P4 have minor non-blocking issues
- **FAIL** — any P0 fails, P1 has uncovered 404, P3 deviations silently dropped