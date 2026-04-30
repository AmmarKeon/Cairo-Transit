# FINAL_DESIGN.md

## Unified Design System Specification

### Design Philosophy

This design system fuses the semantic precision and interactive behavior of Notion with Clay's vibrant, diverse color palette and component architecture. The result is a warm, tactile interface that feels hand-crafted yet functions with absolute precision — cream-tinted canvas with dark-navy CTAs, saturated accent cards, multi-layered depth, and thoughtful whitespace.

---

## 1. Visual Themes & Atmosphere

### Light Theme (Default)

The light theme anchors on Clay's cream-tinted white canvas (`#fffaf0`) — warm, approachable, and differentiated from sterile cool-gray competitor interfaces. Text uses not pure black but near-black (`#0a0a0a`) that carries subtle warmth.

| Element | Token | Value |
|---------|------|-------|
| Page Canvas | `{clay.colors.canvas}` | `#fffaf0` |
| Card Surface | `{clay.colors.surface-card}` | `#f5f0e0` |
| Section Tint | `{clay.colors.surface-soft}` | `#faf5e8` |
| Heading Text | `{clay.colors.ink}` | `#0a0a0a` |
| Body Text | `{clay.colors.body}` | `#3a3a3a` |
| Muted Text | `{clay.colors.muted}` | `#6a6a6a` |

### Dark Theme

The dark theme draws from Notion's restraint — not inverted but deepened. Near-black canvas with warm undertones, high-contrast text, and subtle depth layers that create ambient occlusion without heavy shadows.

| Element | Token | Value |
|---------|------|-------|
| Dark Canvas | — | `#0d0d0d` |
| Dark Surface | — | `#1a1a1a` |
| Dark Elevated | — | `#262626` |
| Heading Text | — | `#fafafa` |
| Body Text | — | `#e5e5e5` |
| Muted Text | — | `#9a9a9a` |

**Key Characteristics:**
- Light theme: Cream canvas (`#fffaf0`) anchored — Never cool gray
- Dark theme: Near-black deepened surface with warm undertones
- Primary CTA: Dark navy (`#0a0a0a`) — Clay's button identity
- Section rhythm: 96px between major bands — Clay's generous pacing
- Depth: Multi-layer shadow stacks from Notion (max 0.05 opacity) — felt not seen
- Badges: Pill-shaped (9999px) — Notion's status indicators
- 12px border radius for content cards — friendly, not sterile

---

## 2. Color Palette & Roles

### Clay Colors (Primary — No Notion Colors)

The system uses Clay's diverse 6-color palette exclusively. Notion's singular blue accent is rejected in favor of vibrant, saturated feature cards.

| Token | Value | Use |
|-------|-------|-----|
| `{clay.colors.primary}` | `#0a0a0a` | Primary CTAs, heading text |
| `{clay.colors.brand-pink}` | `#ff4d8b` | Feature card — outbound, sequencer |
| `{clay.colors.brand-teal}` | `#1a3a3a` | Featured tier, dark card |
| `{clay.colors.brand-lavender}` | `#b8a4ed` | Feature card — AI agent |
| `{clay.colors.brand-peach}` | `#ffb084` | Feature card — general warmth |
| `{clay.colors.brand-ochre}` | `#e8b94a` | Feature card — community |
| `{clay.colors.brand-mint}` | `#a4d4c5` | Accent, illustrations |
| `{clay.colors.brand-coral}` | `#ff6b5a` | Highlight accent |
| `{clay.colors.success}` | `#22c55e` | Success states |
| `{clay.colors.warning}` | `#f59e0b` | Warning states |
| `{clay.colors.error}` | `#ef4444` | Error validation |

### Surface Colors (Clay)

| Token | Value | Use |
|-------|-------|-----|
| `{clay.colors.canvas}` | `#fffaf0` | Page background (light) |
| `{clay.colors.surface-soft}` | `#faf5e8` | Section backgrounds |
| `{clay.colors.surface-card}` | `#f5f0e0` | Card surfaces |
| `{clay.colors.surface-strong}` | `#ebe6d6` | Emphasized bands |
| `{clay.colors.hairline}` | `#e5e5e5` | 1px borders |

### Text Colors (Clay)

| Token | Value | Use |
|-------|-------|-----|
| `{clay.colors.ink}` | `#0a0a0a` | Headings |
| `{clay.colors.body-strong}` | `#1a1a1a` | Lead paragraphs |
| `{clay.colors.body}` | `#3a3a3a` | Running text |
| `{clay.colors.muted}` | `#6a6a6a` | Sub-headings |
| `{clay.colors.muted-soft}` | `#9a9a9a` | Captions |
| `{clay.colors.on-primary}` | `#ffffff` | Text on dark buttons |
| `{clay.colors.on-dark}` | `#ffffff` | Text on teal cards |

### Badge Colors (Notion Badges + Clay Tints)

| Token | Value | Use |
|-------|-------|-----|
| Badge Background | `#f5f0e0` | Cream-tinted pill background |
| Badge Text | `#0a0a0a` | Dark ink for readability |
| Status New | `{clay.colors.brand-pink}` | "New" feature badges |
| Status Featured | `{clay.colors.brand-teal}` | "Pro" tier badges |

---

## 3. Typography Rules

### Font Family

The system uses Clay's font stack — Plain Black for display headlines and Inter for body text, navigation, and UI.

| Token | Font | Fallback |
|-------|------|----------|
| Display | Plain Black | Inter, 500 weight |
| Body/UI | Inter | `-apple-system, BlinkMacSystemFont, "Segoe UI", Roboto` |

**Note:** If Plain Black is unavailable, Inter at weight 500 with -0.05em letter-spacing is the closest approximation.

### Typography Hierarchy (Clay Token System)

| Token | Font | Size | Weight | Line Height | Letter Spacing | Use |
|-------|------|------|--------|-------------|----------------|-----|
| `{clay.typography.display-xl}` | Plain Black | 72px | 500 | 1.0 | -2.5px | Hero h1 |
| `{clay.typography.display-lg}` | Plain Black | 56px | 500 | 1.05 | -2px | Section heads |
| `{clay.typography.display-md}` | Plain Black | 40px | 500 | 1.1 | -1px | Sub-section heads |
| `{clay.typography.display-sm}` | Plain Black | 32px | 500 | 1.15 | -0.5px | CTA heads |
| `{clay.typography.title-lg}` | Inter | 24px | 600 | 1.3 | -0.3px | Card titles, pricing |
| `{clay.typography.title-md}` | Inter | 18px | 600 | 1.4 | 0 | Feature card titles |
| `{clay.typography.title-sm}` | Inter | 16px | 600 | 1.4 | 0 | Small card titles |
| `{clay.typography.body-md}` | Inter | 16px | 400 | 1.55 | 0 | Running text |
| `{clay.typography.body-sm}` | Inter | 14px | 400 | 1.55 | 0 | Fine print |
| `{clay.typography.caption}` | Inter | 13px | 500 | 1.4 | 0 | Badge labels |
| `{clay.typography.caption-uppercase}` | Inter | 12px | 600 | 1.4 | 1.5px | Section labels |
| `{clay.typography.button}` | Inter | 14px | 600 | 1.0 | 0 | Button labels |
| `{clay.typography.nav-link}` | Inter | 14px | 500 | 1.4 | 0 | Navigation |

### Typography Principles

1. **Display compression:** Plain Black at display sizes uses -1 to -2.5px letter-spacing — this is the brand voice
2. **Weight restraint:** Display stays at 500 — the rounded character adds warmth without bolder weight
3. **Body vs. display split:** Plain Black for headlines, Inter for everything else — never mix
4. **Warm scaling:** Line height tightens as size increases — 1.55 at body, 1.3-1.4 at titles, 1.0 at display

---

## 4. Component Stylings

### Buttons (Clay)

Use Clay's button styling — rounded, tactile, with solid color fills.

| Component | Token | Value |
|-----------|------|-------|
| Primary | `{clay.component.button-primary}` | See below |
| Secondary | `{clay.component.button-secondary}` | See below |
| Ghost | `{clay.component.button-text-link}` | See below |
| On Color | `{clay.component.button-on-color}` | White button over saturated cards |

**button-primary:**
- Background: `{clay.colors.primary}` (`#0a0a0a`)
- Text: `{clay.colors.on-primary}` (`#ffffff`)
- Padding: 12px 20px
- Height: 44px
- Radius: `{clay.rounded.md}` (12px)
- Typography: `{clay.typography.button}`
- Hover: background darkens to `#1f1f1f`
- Active: scale(0.98)
- Focus: 2px outline `{clay.colors.primary}`

**button-secondary:**
- Background: `{clay.colors.canvas}` (`#fffaf0`)
- Text: `{clay.colors.ink}` (`#0a0a0a`)
- Border: 1px `{clay.colors.hairline}`
- Padding: 12px 20px
- Height: 44px
- Radius: `{clay.rounded.md}` (12px)

**button-text-link:**
- Background: transparent
- Text: `{clay.colors.ink}`
- Underline on hover
- Typography: `{clay.typography.button}`

### Badges (Notion Style)

Use Notion's pill-shaped badges with Clay's cream-tinted backgrounds.

| Component | Token | Value |
|-----------|------|-------|
| Badge Pill | `{clay.component.badge-pill}` | See below |
| Category Tab | `{clay.component.category-tab}` | See below |
| Status Badge | Custom | Active state indicator |

**badge-pill:**
- Background: `{clay.colors.surface-card}` (`#f5f0e0`)
- Text: `{clay.colors.ink}` (`#0a0a0a`)
- Typography: `{clay.typography.caption}` (13px / 500)
- Radius: `{clay.rounded.pill}` (9999px)
- Padding: 4px 12px

**badge-status:**
- Background: Varies by status
  - New: `{clay.colors.brand-pink}` + white text
  - Pro: `{clay.colors.brand-teal}` + white text
  - Featured: `{clay.colors.brand-ochre}` + dark text
- Radius: 9999px (pill)
- Typography: `{clay.typography.caption-uppercase}` (12px / 600, uppercase, 1.5px spacing)

### Cards (Notion Style)

Use Notion's card architecture — white/cream surfaces with whisper borders and Notion's multi-layer shadows.

| Component | Token | Value |
|-----------|------|-------|
| Card Standard | White + whisper border | See below |
| Card Feature | Saturated colors | Clay.feature-card-* |
| Card Testimonial | Cream surface | Clay testimonial |
| Card Pricing | Cream + tier indicator | Clay pricing |
| Card Product Mockup | White + hairline | Clay product-mockup |

**card-standard:**
- Background: `#ffffff` (light theme) / `#1a1a1a` (dark theme)
- Border: `1px solid rgba(0,0,0,0.08)` (Notion whisper)
- Radius: 12px
- Shadow: Notion 4-layer stack
  ```
  rgba(0,0,0,0.04) 0px 4px 18px,
  rgba(0,0,0,0.027) 0px 2.025px 7.84688px,
  rgba(0,0,0,0.02) 0px 0.8px 2.925px,
  rgba(0,0,0,0.01) 0px 0.175px 1.04062px
  ```
- Padding: 24px

**feature-card-* (Clay saturated cards):**
- Background: `{clay.colors.brand-*}` (pink/teal/lavender/peach/ochre)
- Radius: `{clay.rounded.xl}` (24px)
- Padding: 32px
- Text: White on pink/teal; dark ink on lavender/peach/ochre
- Contains: Title + description + product UI fragment

**product-mockup-card:**
- Background: `{clay.colors.canvas}`
- Border: 1px `{clay.colors.hairline}`
- Radius: `{clay.rounded.lg}` (16px)
- Padding: 24px
- Contains: Product UI screenshot/fragment

**testimonial-card:**
- Background: `{clay.colors.surface-card}` (cream)
- Radius: `{clay.rounded.lg}` (16px)
- Padding: 24px
- Contains: Avatar + name + role + quote

**pricing-tier-card:**
- Background: `{clay.colors.canvas}`
- Border: 1px `{clay.colors.hairline}`
- Radius: `{clay.rounded.lg}` (16px)
- Padding: 32px

**pricing-tier-card-featured:**
- Background: `{clay.colors.brand-teal}`
- Text: `{clay.colors.on-dark}` (white)
- Radius: `{clay.rounded.lg}` (16px)
- Padding: 32px

### Inputs & Forms (Clay)

Use Clay's form styling — cream-tinted inputs with clear focus states.

| Component | Token | Value |
|-----------|------|-------|
| Text Input | `{clay.component.text-input}` | See below |
| Text Input Focused | — | Border thickens |
| Select | — | Same as text input |
| Checkbox/Radio | — | Custom styled |

**text-input:**
- Background: `{clay.colors.canvas}` (`#fffaf0`)
- Text: `{clay.colors.ink}` (`#0a0a0a`)
- Typography: `{clay.typography.body-md}`
- Border: 1px `{clay.colors.hairline}`
- Radius: `{clay.rounded.md}` (12px)
- Padding: 12px 16px
- Height: 44px
- Placeholder: `{clay.colors.muted-soft}`
- Focus: Border becomes `{clay.colors.ink}`, 2px outline

### Navigation (Clay)

| Component | Token | Value |
|-----------|------|-------|
| Top Nav | `{clay.component.top-nav}` | See below |
| Nav Link | `{clay.component.nav-link}` | See below |
| Mobile Menu | — | Hamburger collapse |

**top-nav:**
- Background: `{clay.colors.canvas}`
- Height: 64px
- Logo: Left-aligned
- Links: Center-aligned horizontal menu
- CTA: Right-aligned primary button

**nav-link:**
- Typography: `{clay.typography.nav-link}`
- Text: `{clay.colors.ink}`
- Hover: Underline or color shift

---

## 5. Layout Principles

### Spacing System (Clay Base + Notion Scale)

| Token | Value | Use |
|-------|-------|-----|
| `{clay.spacing.xxs}` | 4px | Micro spacing |
| `{clay.spacing.xs}` | 8px | Tight spacing |
| `{clay.spacing.sm}` | 12px | Small gaps |
| `{clay.spacing.md}` | 16px | Default gap |
| `{clay.spacing.lg}` | 24px | Section components |
| `{clay.spacing.xl}` | 32px | Card padding |
| `{clay.spacing.xxl}` | 48px | Large gaps |
| `{clay.spacing.section}` | 96px | Between major bands |

### Grid & Container

| Property | Value |
|----------|-------|
| Max content width | ~1280px centered |
| Light theme base | Cream (`#fffaf0`) |
| Section alternation | Cream surface (`#faf5e8`) |
| Grid columns | 12-column editorial |
| Hero split | 7/5 (content/illustration) |
| Feature grid | 3-up desktop → 2-up tablet → 1-up mobile |

### Whitespace Philosophy

1. **Generous vertical rhythm:** 96px between major sections — Clay's editorial pacing
2. **Content-first density:** Compact body text (line-height 1.55) surrounded by ample margins
3. **Warm alternation:** Cream sections alternate with cream-tinted sections — Notion's rhythm without the cool grays

---

## 6. Elevation & Depth (Notion System)

### Depth Levels

| Level | Treatment | Use |
|-------|-----------|-----|
| Flat (0) | No shadow, no border | Page background |
| Whisper (1) | `1px solid rgba(0,0,0,0.08)` | Card outlines, dividers |
| Soft Card (2) | 4-layer shadow stack (max 0.04 opacity) | Content cards |
| Deep Card (3) | 5-layer shadow stack (max 0.05 opacity, 52px blur) | Modals, featured panels |
| Focus | `2px solid var(--focus-color)` | Keyboard focus |

### Shadow Philosophy (Notion)

Notion's shadow system uses multiple layers with extremely low individual opacity (0.01 to 0.05) that accumulate into soft, natural elevation. The 4-layer card shadow spans from 1.04px to 18px blur — a gradient of depth rather than a single hard shadow.

**Card Shadow (Level 2):**
```
rgba(0,0,0,0.04) 0px 4px 18px,
rgba(0,0,0,0.027) 0px 2.025px 7.84688px,
rgba(0,0,0,0.02) 0px 0.8px 2.925px,
rgba(0,0,0,0.01) 0px 0.175px 1.04062px
```

**Deep Shadow (Level 3):**
```
rgba(0,0,0,0.01) 0px 1px 3px,
rgba(0,0,0,0.02) 0px 3px 7px,
rgba(0,0,0,0.02) 0px 7px 15px,
rgba(0,0,0,0.04) 0px 14px 28px,
rgba(0,0,0,0.05) 0px 23px 52px
```

---

## 7. Responsive Behavior (Clay Breakpoints)

### Breakpoints

| Name | Width | Key Changes |
|------|-------|------------|
| Mobile | < 768px | Hamburger nav; h1 scales 72→36px; 1-up cards |
| Tablet | 768–1024px | 2-up feature cards |
| Desktop | 1024–1440px | Full layout, 3-up cards |
| Wide | > 1440px | Max content 1280px, centered |

### Collapsing Strategy (Clay)

1. **Navigation:** Horizontal → hamburger at < 768px
2. **Hero:** 7-5 grid → single column on mobile
3. **Feature cards:** 3 → 2 → 1 column
4. **Pricing:** 4 → 2 → 1 column
5. **Section spacing:** 96px → 48px on mobile

### Touch Targets

- Minimum button height: 44px (WCAG AAA compliance)
- Input height: 44px
- Tap targets: 44px × 44px minimum

---

## 8. Border Radius Scale (Clay)

| Token | Value | Use |
|-------|-------|-----|
| `{clay.rounded.xs}` | 6px | Small badges |
| `{clay.rounded.sm}` | 8px | Small buttons |
| `{clay.rounded.md}` | 12px | Standard buttons, inputs |
| `{clay.rounded.lg}` | 16px | Content cards |
| `{clay.rounded.xl}` | 24px | Feature cards |
| `{clay.rounded.pill}` | 9999px | Badges, pills |
| `{clay.rounded.full}` | 50% | Avatars |

---

## 9. Component Summary Table

### Buttons

| Component | Background | Text | Border | Radius | Height |
|----------|-----------|------|--------|--------|--------|
| Primary | `#0a0a0a` | `#ffffff` | none | 12px | 44px |
| Secondary | `#fffaf0` | `#0a0a0a` | 1px hairline | 12px | 44px |
| Ghost | transparent | `#0a0a0a` | none | — | auto |
| On Color | `#ffffff` | `#0a0a0a` | none | 12px | 44px |

### Cards

| Component | Background | Border | Radius | Padding | Shadow |
|----------|-----------|--------|--------|---------|--------|
| Standard | `#ffffff` | whisper | 12px | 24px | Level 2 |
| Feature Pink | `#ff4d8b` | none | 24px | 32px | none |
| Feature Teal | `#1a3a3a` | none | 24px | 32px | none |
| Feature Lavender | `#b8a4ed` | none | 24px | 32px | none |
| Feature Peach | `#ffb084` | none | 24px | 32px | none |
| Feature Ochre | `#e8b94a` | none | 24px | 32px | none |
| Product Mockup | `#fffaf0` | 1px hairline | 16px | 24px | none |
| Testimonial | `#f5f0e0` | none | 16px | 24px | none |
| Pricing Tier | `#fffaf0` | 1px hairline | 16px | 32px | none |
| Pricing Featured | `#1a3a3a` | none | 16px | 32px | none |

### Form Elements

| Component | Background | Border | Radius | Height | Focus |
|----------|-----------|--------|--------|--------|-------|
| Text Input | `#fffaf0` | 1px hairline | 12px | ink border |
| Select | `#fffaf0` | 1px hairline | 12px | ink border |
| Checkbox | custom | custom | 4px | ink ring |

### Badges

| Component | Background | Text | Radius | Padding |
|----------|-----------|------|--------|---------|
| Badge Pill | `#f5f0e0` | `#0a0a0a` | 9999px | 4px 12px |
| Badge New | `#ff4d8b` | `#ffffff` | 9999px | 4px 12px |
| Badge Pro | `#1a3a3a` | `#ffffff` | 9999px | 4px 12px |

---

## 10. Accessibility & States

### Interactive States (Notion + Clay)

| State | Treatment |
|-------|----------|
| Default | Standard appearance |
| Hover | Scale(1.02) on buttons, color shift on links |
| Active/Pressed | Scale(0.98) on buttons |
| Focus | 2px outline in brand color |
| Disabled | 50% opacity, no interactions |

### Color Contrast

- Heading on light: `#0a0a0a` on `#fffaf0` — ~18:1 (WCAG AAA)
- Body on light: `#3a3a3a` on `#fffaf0` — ~8:1 (WCAG AA)
- Muted on light: `#6a6a6a` on `#fffaf0` — ~5:1 (WCAG AA)
- White on dark: `#ffffff` on `#0a0a0a` — ~16:1 (WCAG AAA)

### Focus System

- All interactive elements receive visible focus indicators
- Focus ring: 2px solid outline in brand color
- Tab navigation supported throughout

---

## 11. Do's and Don'ts

### Do

- ✅ Anchor light theme on cream canvas (`#fffaf0`) — never cool gray
- ✅ Use Clay's saturated 6-color palette for feature cards
- ✅ Apply Plain Black at weight 500 with negative letter-spacing on display headlines
- ✅ Use Notion's 4-layer shadow for card elevation
- ✅ Keep section rhythm at 96px between major bands
- ✅ Use 12px radius for buttons and inputs, 24px for feature cards
- ✅ Ensure 44px minimum touch targets

### Don't

- ❌ Use Notion's cool gray palette — stick to Clay's warm tones
- ❌ Use more than 6 saturated brand colors — the palette is saturated enough
- ❌ Bold Plain Black beyond weight 500 — the rounded character adds warmth
- ❌ Use heavy shadows — depth comes from layered opacity, not hard shadows
- ❌ Repeat the same brand-color card twice in a row
- ❌ Use a dark footer in light theme — maintain cream-throughout
- ❌ Forget focus states on interactive elements

---

## 12. Quick Reference

### Light Theme Quick Color Map

| Token | Value |
|-------|-------|
| Canvas | `#fffaf0` |
| Surface | `#faf5e8` |
| Card | `#f5f0e0` |
| Ink | `#0a0a0a` |
| Body | `#3a3a3a` |
| Muted | `#6a6a6a` |
| Primary CTA | `#0a0a0a` |
| Brand Pink | `#ff4d8b` |
| Brand Teal | `#1a3a3a` |
| Brand Lavender | `#b8a4ed` |
| Brand Peach | `#ffb084` |
| Brand Ochre | `#e8b94a` |

### Quick Component Prompts

**Hero Section:**
"Hero on cream canvas. Headline at 72px Plain Black weight 500, line-height 1.0, letter-spacing -2.5px, color #0a0a0a. Subtitle at 18px Inter weight 400, line-height 1.4, color #3a3a3a. Primary CTA button (#0a0a0a bg, white text, 12px radius, 12px 20px padding, 44px height) and secondary button (cream bg, ink text, hairline border)."

**Feature Card:**
"Saturated feature card. Background #ff4d8b (pink). Title at 18px Inter weight 600, white text. Body at 16px Inter weight 400, white text. 24px radius, 32px padding. No shadow."

**Standard Card:**
"Card with whisper border. White background, 1px solid rgba(0,0,0,0.08) border, 12px radius. Notion 4-layer shadow. Title at 24px Inter weight 600. Body at 16px Inter weight 400, muted color."

**Pill Badge:**
"Pill badge badge. Cream background (#f5f0e0), ink text (#0a0a0a), 9999px radius, 4px 12px padding, 13px Inter weight 500."

**Form Input:**
"Text input on cream canvas. Background #fffaf0, 1px hairline border (#e5e5e5), 12px radius, 44px height. Placeholder in muted-soft. Focus state border becomes ink (#0a0a0a)."

**Navigation:**
"Top nav, 64px height, cream background. Logo left. Nav links centered, Inter 14px weight 500. Primary button right (#0a0a0a bg, white text, 12px radius)."

---

## 13. File Structure

```
styles/
├── tokens/
│   ├── colors.css          # Clay color tokens
│   ├── typography.css     # typography scale
���   ├── spacing.css      # spacing tokens
│   └── radius.css      # border radius tokens
├── components/
│   ├── buttons.css     # button variants
│   ├── cards.css     # card components
│   ├── badges.css    # badge/pill styles
│   ├── forms.css    # input/select styles
│   └── navigation.css # nav components
├── themes/
│   ├── light.css      # light theme overrides
│   └── dark.css     # dark theme overrides
└── style.css       # main import file
```

---

## 14. Design Tokens Summary

### Colors

```css
:root {
  /* Brand */
  --color-primary: #0a0a0a;
  --color-brand-pink: #ff4d8b;
  --color-brand-teal: #1a3a3a;
  --color-brand-lavender: #b8a4ed;
  --color-brand-peach: #ffb084;
  --color-brand-ochre: #e8b94a;

  /* Surface */
  --color-canvas: #fffaf0;
  --color-surface-soft: #faf5e8;
  --color-surface-card: #f5f0e0;
  --color-hairline: #e5e5e5;

  /* Text */
  --color-ink: #0a0a0a;
  --color-body: #3a3a3a;
  --color-muted: #6a6a6a;

  /* On Colors */
  --color-on-primary: #ffffff;
  --color-on-dark: #ffffff;

  /* Semantic */
  --color-success: #22c55e;
  --color-warning: #f59e0b;
  --color-error: #ef4444;
}
```

### Typography

```css
:root {
  --font-display-xl: 72px/1.0 -2.5px;
  --font-display-lg: 56px/1.05 -2px;
  --font-display-md: 40px/1.1 -1px;
  --font-display-sm: 32px/1.15 -0.5px;
  --font-title-lg: 24px/1.3 -0.3px;
  --font-title-md: 18px/1.4 0;
  --font-body-md: 16px/1.55 0;
  --font-body-sm: 14px/1.55 0;
  --font-caption: 13px/1.4 0;
  --font-button: 14px/1.0 0;
}
```

### Spacing

```css
:root {
  --space-xxs: 4px;
  --space-xs: 8px;
  --space-sm: 12px;
  --space-md: 16px;
  --space-lg: 24px;
  --space-xl: 32px;
  --space-xxl: 48px;
  --space-section: 96px;
}
```

### Radius

```css
:root {
  --radius-xs: 6px;
  --radius-sm: 8px;
  --radius-md: 12px;
  --radius-lg: 16px;
  --radius-xl: 24px;
  --radius-pill: 9999px;
}
```

---

## 15. Usage Guidelines

### When to Use Each Component

| Component | Use For |
|-----------|--------|
| Primary Button | CTAs, main actions |
| Secondary Button | Form submissions, secondary actions |
| Ghost Button | Inline links, tertiary actions |
| Badge Pill | Status indicators, feature labels |
| Feature Card | Product features, saturated emphasis |
| Testimonial Card | Customer quotes, reviews |
| Product Mockup Card | Product UI screenshots |
| Pricing Tier Card | Subscription plans |
| Text Input | Form fields, search |
| Top Nav | Site navigation |

### Theme Selection

| Theme | Use Case |
|-------|----------|
| Light | Default, marketing pages |
| Dark | In-app, dark mode preference |

### Accessibility Checklist

- [ ] All buttons have 44px minimum touch target
- [ ] Focus states visible on all interactive elements
- [ ] Color contrast meets WCAG AA (4.5:1 body, 3:1 large)
- [ ] Form inputs have associated labels
- [ ] Focus can be triggered via keyboard
- [ ] Disabled states clearly communicated

---

*Design System v1.0 — Merged from Notion semantics + Clay aesthetics*