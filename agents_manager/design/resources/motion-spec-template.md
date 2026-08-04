# Motion Spec Template (`07_primitives/motion/motion-spec.md`)

Define motion the same way you define color or type: as tokens, with rules.

## Tokens

```markdown
## Duration
| Token | Value | Use |
|---|---|---|
| `--motion-instant` | 0ms | No animation (reduce-motion fallback) |
| `--motion-fast` | 120ms | Micro-interactions (toggle, hover) |
| `--motion-base` | 200ms | Standard UI transitions (fade, slide) |
| `--motion-slow` | 320ms | Page transitions, large movements |
| `--motion-slower` | 480ms | Onboarding, hero animations |
| `--motion-deliberate` | 720ms | Pacing for narrative sequences |

## Easing
| Token | Curve | Use |
|---|---|---|
| `--motion-ease-standard` | cubic-bezier(0.2, 0, 0, 1) | Default. Most UI. |
| `--motion-ease-emphasized` | cubic-bezier(0.2, 0, 0, 1) with overshoot | Primary actions, attention |
| `--motion-ease-decelerate` | cubic-bezier(0, 0, 0, 1) | Entering elements |
| `--motion-ease-accelerate` | cubic-bezier(0.3, 0, 1, 1) | Exiting elements |
| `--motion-ease-linear` | linear | Loops, progress indicators |
```

## Rules

```markdown
## Always
- Animate transform and opacity only (compositor-friendly).
- Honor `prefers-reduced-motion`: replace any animation with `--motion-instant`.
- Use `--motion-ease-standard` unless there's a reason.
- Pair duration with distance: short distance = short duration.

## Never
- Don't animate `width`, `height`, `top`, `left`. Reflow is expensive and janky.
- Don't chain more than 3 easings in one sequence.
- Don't loop animations more than 3 times unless user-initiated.
- Don't use `transition: all`. Name properties explicitly.

## Pacing examples
| Interaction | Duration | Easing | Property |
|---|---|---|---|
| Toggle on/off | fast | standard | opacity, transform |
| Modal open | base | decelerate | opacity, transform: scale(0.96→1) |
| Modal close | fast | accelerate | opacity, transform: scale(1→0.96) |
| Tab switch | base | standard | opacity, transform: translateX |
| Page enter | slow | decelerate | opacity, transform: translateY(8px→0) |
| Toast appear | base | emphasized | opacity, transform: translateY(16px→0) |
| Toast dismiss | fast | accelerate | opacity |
```

## Reduced motion

```markdown
## When prefers-reduced-motion: reduce

Override every duration to `--motion-instant`. Replace translate/scale with opacity-only.
```css
@media (prefers-reduced-motion: reduce) {
  *, *::before, *::after {
    animation-duration: var(--motion-instant) !important;
    transition-duration: var(--motion-instant) !important;
    animation-iteration-count: 1 !important;
  }
}
```

## Complex sequences

For orchestrated motion (onboarding, hero, narrative), use a timeline. Define:

```markdown
## Onboarding card stagger
1. Card 1 fades in + slides up (slow, decelerate, 0ms delay)
2. Card 2 fades in + slides up (slow, decelerate, 80ms delay)
3. Card 3 fades in + slides up (slow, decelerate, 160ms delay)
4. CTA fades in (slow, standard, 320ms delay)
```

Export the timeline as:
- Lottie JSON (for native rendering)
- CSS keyframes (for web)
- AE / Figma export (for hand-off)

## Handoff to `am-coder`

```markdown
## What am-coder needs
- Duration tokens → CSS variable per token
- Easing tokens → CSS variable per token
- Per-component rules → component file's `:hover`, `:focus`, transitions
- Reduced motion override → global stylesheet
- Complex sequences → Lottie JSON + integration snippet
```