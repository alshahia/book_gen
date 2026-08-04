# Copy Template (`06_copy/`)

Two artifacts: `microcopy.md` + `content-strategy.md`.

## `microcopy.md`

```markdown
# Microcopy — <Product / Screen>

**Voice reference**: <link to 02_brand/voice-and-tone.md>
**Locale(s)**: <ar-SA, en-US, ...>

## Buttons
| Action | Primary | Destructive |
|---|---|---|
| Save | حفظ | — |
| Delete | حذف | حذف نهائياً |
| Cancel | إلغاء | — |
| Confirm | تأكيد | — |

## Empty states
### <Screen> when no data
- Headline: <short, invitational>
- Body: <explains what will appear, invites action>
- Primary CTA: <action verb>

(repeat per screen)

## Error messages
### <Error class>
- Title: <what happened, plainly>
- Body: <what user can do>
- CTA: <next action>

### Validation
- Required field missing: "<Field> مطلوب"
- Invalid format: "<Field> غير صالح"

## Success messages
### <Action>
- <brief, satisfied tone>
- <avoid exclamation unless brand voice allows>

## Loading states
| Context | Copy |
|---|---|
| Initial load | "جارٍ التحميل..." |
| Long operation (>2s) | "يستغرق لحظة..." |
| Streaming / infinite | (no copy — use skeleton) |

## Numbers, dates, units
- Numbers: <Latin Arabic / Eastern Arabic / with thousand separators?>
- Dates: <Hijri / Gregorian / both?>
- Currency: <display in user's locale>

## Bilingual rules (ar + en in same UI)
- Lead with user's locale setting, fall back to brand language.
- If both shown, primary on top (or per design direction).
- Don't mix Arabic numerals in Latin-numeral contexts unless intended.
```

## `content-strategy.md`

```markdown
# Content Strategy — <Product>

## Goals
- ...

## Audience segments
- ...

## Voice in practice
| Touchpoint | Tone |
|---|---|
| Onboarding | Warm, encouraging |
| First-time experience | Patient, exploratory |
| Daily use | Concise, respectful |
| Error / edge case | Direct, helpful, never blaming |
| Power user | Efficient, no hand-holding |

## Information hierarchy
- Primary: ...
- Secondary: ...
- Tertiary: ...

## Localization strategy
- Source locale: ...
- Translation pipeline: ...
- RTL handling: ...
- Bidirectional text: ...

## Editorial standards
- Sentence case vs Title Case: ...
- Punctuation: ...
- Acronyms: ...
- Inclusive language: ...

## Don'ts
- Don't anthropomorphize the system ("RAUM. thinks you might like...") unless brand voice explicitly allows.
- Don't use "we" unless the brand is a person/team the user knows.
- Don't use exclamation unless brand voice explicitly allows.
```

## Tone quick-reference

| Avoid | Prefer |
|---|---|
| "Oops!" | "We couldn't..." |
| "Awesome!" | "Done." |
| "Just" (as filler) | remove the word |
| "Simply" / "just" / "easy" | describe what to do |
| "Sorry for the inconvenience" | solve the problem or offer an action |
| "Click here" | describe destination |
| Second person "you" repeated | vary; consider imperative |