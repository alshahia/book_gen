# Brand Template (`02_brand/`)

Brand identity deliverables. Each `.md` ships with a `.json` mirror.

## `color-palette.md` + `.json`

```markdown
# Color Palette — <Brand Name>

**Usage rule**: Always reference as tokens (`var(--color-primary)`), never inline hex.

## Primary
| Token | Hex | Use | Contrast on bg |
|---|---|---|---|
| `--color-primary` | #... | Brand surfaces, primary CTAs | 4.5:1 on bg ✓ |

## Secondary
| Token | Hex | Use | Contrast |
|---|---|---|---|
| `--color-secondary` | #... | Secondary actions, accents | ... |

## Neutral
| Token | Hex | Use |
|---|---|---|
| `--color-ink` | #... | Primary text |
| `--color-ink-2` | #... | Secondary text |
| `--color-ink-3` | #... | Tertiary text, captions |
| `--color-line` | #... | Borders, dividers |
| `--color-bg` | #... | Page background |
| `--color-surface` | #... | Card / elevated surface |

## Semantic
| Token | Hex | Use |
|---|---|---|
| `--color-success` | #... | Confirmations |
| `--color-warning` | #... | Cautions |
| `--color-danger` | #... | Errors, destructive |
| `--color-info` | #... | Informational |

## Don't
- Don't introduce a color not in this palette.
- Don't use `--color-*` tokens for non-color purposes (spacing, etc.).
- Don't override contrast ratios with custom values.
```

`.json` mirror uses W3C Design Tokens spec.

## `typography.md` + `.json`

```markdown
# Typography — <Brand Name>

## Families
| Token | Family | Weights | Use |
|---|---|---|---|
| `--font-display` | <name> | 700 | Hero, page titles |
| `--font-body` | <name> | 400, 500, 600 | Body, UI |
| `--font-mono` | <name> | 400 | Code, technical |

## Scale
| Token | Size / Line-height | Use |
|---|---|---|
| `--text-display` | 48 / 56 | Hero |
| `--text-h1` | 32 / 40 | Page title |
| `--text-h2` | 24 / 32 | Section title |
| `--text-h3` | 20 / 28 | Card title |
| `--text-body` | 16 / 24 | Body |
| `--text-small` | 14 / 20 | Caption |
| `--text-micro` | 12 / 16 | Legal, fine print |

## Rules
- Display family ONLY for display; body family for everything else.
- Body text must hit WCAG contrast on its background.
- Don't use weights outside the family.
- Arabic: pair Arabic-script display family with Latin display family; same for body.
```

## `voice-and-tone.md`

```markdown
# Voice and Tone — <Brand Name>

## Voice (constant)
We are <3 adjectives>. We sound like <reference person or character>.

## Tone (varies by context)
| Context | Tone |
|---|---|
| Onboarding | Warm, encouraging |
| Error message | Direct, helpful, never blaming |
| Marketing | Confident, specific, no hype |
| Empty state | Curious, inviting |
| Success | Brief, satisfied |

## Vocabulary
### Use
- ...

### Avoid
- ...

## Sample phrases
| Bad | Better |
|---|---|
| "Oops! Something went wrong!" | "We couldn't save your changes. Try again." |
```

## `brand-guidelines.md`

The executive summary. One document that a new team member reads first. Contains:

1. Logo usage rules (clear space, min size, backgrounds it does/doesn't work on)
2. Color (link to `color-palette.md`)
3. Typography (link to `typography.md`)
4. Voice and tone (link to `voice-and-tone.md`)
5. Photography / illustration style
6. Motion principles (link to `07_primitives/motion/motion-spec.md` when produced)
7. Don'ts (a tight list)

## `logo/logo-placeholder.svg`

A simple geometric placeholder so consumers can build before the real logo exists. Replace when the actual logo arrives.