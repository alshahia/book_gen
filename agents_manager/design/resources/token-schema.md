# Token Schema — W3C Design Tokens

We ship tokens as a **subset of the W3C Design Tokens spec**, constrained for portability across web, native, and design tools. The full spec lives at https://www.designtokens.org/ — we intentionally use a smaller surface area.

## Mandatory top-level groups

Every `02_system/tokens/base.json` MUST contain these groups. Sub-keys within a group are the agent's call, but the group names are locked.

```json
{
  "color": {
    "bg":       { "$type": "color", "$value": "#FAFAF7" },
    "surface":  { "$type": "color", "$value": "#FFFFFF" },
    "ink":      { "$type": "color", "$value": "#1A1A1A" },
    "ink-2":    { "$type": "color", "$value": "#4A4A4A" },
    "ink-3":    { "$type": "color", "$value": "#8A8A8A" },
    "line":     { "$type": "color", "$value": "#E8E8E2" },
    "accent":   { "$type": "color", "$value": "#5B7A6B" },
    "highlight":{ "$type": "color", "$value": "#B8935A" }
  },
  "typography": {
    "family-ui":   { "$type": "fontFamily", "$value": "Inter, system-ui, sans-serif" },
    "family-quran":{ "$type": "fontFamily", "$value": "Amiri Quran, serif" },
    "fs-12": { "$type": "dimension", "$value": "12px" },
    "fs-14": { "$type": "dimension", "$value": "14px" },
    "fs-17": { "$type": "dimension", "$value": "17px" },
    "fs-24": { "$type": "dimension", "$value": "24px" },
    "fs-32": { "$type": "dimension", "$value": "32px" },
    "lh-tight":   { "$type": "number", "$value": 1.2 },
    "lh-relaxed": { "$type": "number", "$value": 1.8 }
  },
  "spacing": {
    "1": { "$type": "dimension", "$value": "4px" },
    "2": { "$type": "dimension", "$value": "8px" },
    "3": { "$type": "dimension", "$value": "12px" },
    "4": { "$type": "dimension", "$value": "16px" },
    "6": { "$type": "dimension", "$value": "24px" },
    "8": { "$type": "dimension", "$value": "32px" }
  },
  "radius": {
    "sm":   { "$type": "dimension", "$value": "8px" },
    "md":   { "$type": "dimension", "$value": "14px" },
    "lg":   { "$type": "dimension", "$value": "22px" },
    "pill": { "$type": "dimension", "$value": "999px" }
  },
  "size": {
    "touch-target": { "$type": "dimension", "$value": "44px" },
    "icon":         { "$type": "dimension", "$value": "24px" },
    "avatar":       { "$type": "dimension", "$value": "40px" }
  },
  "motion": {
    "duration-fast":   { "$type": "duration", "$value": "150ms" },
    "duration-normal": { "$type": "duration", "$value": "250ms" },
    "duration-slow":   { "$type": "duration", "$value": "400ms" },
    "ease-standard":   { "$type": "cubicBezier", "$value": [0.4, 0, 0.2, 1] }
  }
}
```

## Themes

Each theme is a **token map override**, not a new spec. Themes live in `themes/<n>/tokens.json` and override only the keys that change.

```json
{
  "theme": "01-traditional-illuminated",
  "color": {
    "bg":       { "$value": "#F5EBD3" },
    "ink":      { "$value": "#2A1F18" },
    "accent":   { "$value": "#0B3D2E" },
    "highlight":{ "$value": "#C9A24A" }
  }
}
```

Compile to CSS:

```css
:root { /* base */ }
[data-theme="01-traditional-illuminated"] { /* overrides */ }
```

## Semantic aliases (optional but recommended)

Add a `semantic` group if you want role-based token names that themes can re-map:

```json
{
  "semantic": {
    "bg":        { "$type": "color", "$value": "{color.bg}" },
    "text-body": { "$type": "color", "$value": "{color.ink}" },
    "primary":   { "$type": "color", "$value": "{color.accent}" }
  }
}
```

`am-coder` should consume semantic tokens, not raw color tokens. This is what makes theme switching a one-attribute change.

## What we do NOT ship

- Shadow values as tokens (use CSS variables per theme, or platform-native).
- Animation curves beyond `ease-standard` (let the platform decide the rest).
- Gradient stops (too theme-specific to tokenize meaningfully).