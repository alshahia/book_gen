# Multi-Locale Checklist

Every design that crosses a locale boundary must pass this checklist. A locale boundary is anywhere the script, direction, or cultural conventions change.

## 1. Script coverage

| Script | Direction | Locales | Notes |
|---|---|---|---|
| Latin | LTR | en, fr, de, es, pt, it, nl, … | Reference for layout |
| Cyrillic | LTR | ru, uk, bg, sr | Slavic languages |
| Greek | LTR | el | Diacritics common |
| Arabic | RTL | ar, fa, ur | Connected script; baseline shifts |
| Hebrew | RTL | he, yi | Square script |
| Devanagari | LTR | hi, mr, ne | Above-baseline marks |
| Bengali | LTR | bn | Above-baseline marks |
| Thai | LTR | th | No word spaces; line-break rules differ |
| CJK | LTR (vertical option) | zh, ja, ko | CJK can be vertical; line-break anywhere |
| Tibetan | LTR | bo | Above-baseline stacking |

## 2. Direction rules

```markdown
## RTL (Arabic, Hebrew, Persian, Urdu)
- Apply `dir="rtl"` at <html> or per-region.
- Use logical CSS properties only: `margin-inline-start`, never `margin-left`.
- Mirror: chevrons, breadcrumbs, progress bars, scrollbars (browser-handled), pagination arrows.
- Do NOT mirror: brand logos, audio waveforms, time numerals (12:34 stays 12:34), mathematical operators.
- Arabic numerals: Eastern Arabic (٠١٢٣٤٥٦٧٨٩) by default; switch to Western (0123456789) for technical content.

## LTR
- Default. Same rules as English/French.
- Watch for vertical text in CJK (rare; opt-in).

## Mixed (bilingual UI)
- Lead with user's chosen locale (per browser `Accept-Language` or user setting).
- Brand language as fallback.
- Numbers: match locale conventions (thousand separators, decimal marks).
- Dates: dual calendar support where relevant (Hijri + Gregorian for Muslim-majority markets).
```

## 3. Typography

```markdown
## Pairing
- Latin display ↔ Arabic display (e.g. Inter Bold ↔ Noto Naskh Arabic Bold)
- Latin body ↔ Arabic body
- NEVER pair: Latin display with Arabic body, or vice versa — it visually clashes.

## Sizing
- Arabic fonts render ~5-10% smaller at the same point size. Set body Arabic one notch up (16px → 17px or 18px).
- Diacritics (Arabic harakat, Hebrew niqqud) extend above the baseline; add line-height padding.

## Line-breaking
- Latin: break at word boundaries.
- Arabic / Hebrew: break anywhere appropriate (script handles it).
- CJK: break anywhere; hyphenation rare.
- Thai: break only at word boundaries (no spaces — needs a dictionary).

## Vertical
- CJK: optional vertical mode for headings and short labels. Set `writing-mode: vertical-rl`.
- Other scripts: vertical not standard.
```

## 4. Numbers, dates, units

```markdown
## Numerals
- Latin: Western (0123456789).
- Arabic: Eastern Arabic (٠١٢٣٤٥٦٧٨٩) by default; switch to Western for technical content.
- Persian / Urdu: Eastern Arabic with slight glyph differences (۴ vs ٤).
- CJK: full-width (０１２３) for parity with CJK characters; half-width for ASCII contexts.

## Dates
- Western: `MMM D, YYYY` (en-US) or `D MMM YYYY` (en-GB).
- Arabic: use Hijri or Gregorian per context. Both where relevant.
- Persian: Solar Hijri (e.g. 1403/04/15).
- Buddhist-era (Thailand): year is Gregorian + 543.

## Time
- 12-hour with AM/PM in en-US. 24-hour in most other locales.
- Arabic: 24-hour common.
- Display: keep numerals matched to locale.

## Currency
- Code + symbol per locale (USD $, EUR €, JPY ¥, AED د.إ).
- Position: before or after per locale convention.
- Don't hardcode; rely on `Intl.NumberFormat`.
```

## 5. RTL-specific UI patterns

```markdown
## Lists
- Numbered lists: visual order is mirrored (1. first → 1. first on the right).
- Bulleted lists: bullet position mirrors.

## Forms
- Labels above fields (universal).
- Required-field indicator: asterisk or "مطلوب" depending on locale.
- Error messages: place below field, aligned to start (right in RTL).

## Navigation
- Back chevron: points to start side (right in RTL).
- Breadcrumbs: separator mirrored (`›` becomes `‹`).
- Tabs: order mirrored.

## Charts / Data viz
- X-axis: numbers and labels mirrored.
- Time axis: still reads left-to-right in time, but visual placement of "earlier" depends on direction.
- Bar charts: positive direction flips in RTL.
- Pie charts: start angle flips.

## Progress
- Direction of progress flow flips.
- 0% on start side (right in RTL), 100% on end side (left in RTL).
```

## 6. Cultural considerations

```markdown
## Imagery
- Avoid hand gestures that read as offensive in target culture.
- Verify food, clothing, architecture fit locale.
- Avoid religious symbols unless the project explicitly is religious.

## Color
- Red ≠ danger in all cultures (positive in China).
- White ≠ purity in all cultures (mourning in parts of Asia).
- Green ≠ growth in all cultures (negative in some contexts).

## Iconography
- Mailbox shape (US vs EU).
- Toilet signs, transportation signs (don't reuse without locale check).
- Direction arrows (mirrored in RTL).
```

## 7. Testing protocol

```markdown
## Pre-ship verification per locale
- [ ] Native speaker review for copy
- [ ] RTL layout verified on at least 2 sample screens
- [ ] Bidi text (Arabic + English in same line) tested
- [ ] Dates / numbers / currency formatted per locale
- [ ] Typography pairing reads correctly
- [ ] Cultural imagery checked
- [ ] Color semantics checked
- [ ] Forms validation messages in user's language
- [ ] Audio / voice-over quality for TTS (if any)
- [ ] Screen reader tested in user's locale
```

## Don't

- Don't auto-translate with a generic translator and ship.
- Don't assume RTL is just mirroring LTR — it's a separate design problem.
- Don't reuse Western UI patterns for RTL markets (left sidebar → right sidebar isn't enough).
- Don't skip native-speaker review for marketing copy.
- Don't pick fonts without checking the full script range (some Latin fonts have broken Arabic fallbacks).