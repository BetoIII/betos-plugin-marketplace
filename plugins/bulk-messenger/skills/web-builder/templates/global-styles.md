# Global Styles Reference

Used by: `sms-composer`, `preview`

---

## Fonts

- **Body / UI:** Instrument Sans (weights: 400, 500, 600)
- **Headings:** Fraunces (optical size: 9–144, weights: 400, 600)

Source: Google Fonts

---

## Color Variables

| Variable | Value | Usage |
|---|---|---|
| `--imessage-blue` | `#007AFF` | iMessage bubble color |
| `--background` | `#1A1A1A` | Page background |
| `--foreground` | `#FAF7F2` | Primary text |
| `--card` | `#2A2A2A` | Card backgrounds |
| `--card-border` | `#3A3A3A` | Card borders |
| `--primary` | `#D4573B` | Primary actions, active states |
| `--accent` | `#6B7A5A` | Accent elements, table headers |
| `--success` | `#2d9a5f` | Valid/success states |
| `--warning` | `#D4A13B` | Warning states |
| `--danger` | `#C05746` | Error/danger states |
| `--warm-gray` | `#6a6a6a` | Muted/secondary text |

---

## Layout

- `.container` — max-width: 1400px, centered
- `.layout-grid` — 2-column grid, 2rem gap; collapses to 1 column on screens ≤768px
- Body padding: 2rem (1rem on mobile)

---

## Typography

| Element | Font | Size | Weight | Notes |
|---|---|---|---|---|
| `h1` | Fraunces | 2.5rem | 700 | Page title |
| `.section-title` | Fraunces | 2rem | 600 | Section heading, 0.05em letter-spacing |
| `.subtitle` | Instrument Sans | 1.1rem | 400 | Muted warm-gray |
| `.form-label`, `label` | Instrument Sans | 1rem | 500 | Uppercase, 0.05em letter-spacing |

---

## Forms

- `.form-group` — flex column, 0.25rem gap
- `input[type="text/email/tel"]` — full width, `--background` fill, `--card-border` border, 6px radius; focus: `--primary` border
- `textarea` — full width, monospace (`Courier New`), min-height 150px, resizable vertically; focus: `--primary` border
- `.template-area` — extends textarea min-height to 180px

---

## Buttons

Base class: `.btn` — padding 0.75rem 1.5rem, 12px radius, 0.95rem font, weight 600, inline-flex centered

| Class | Background | Text | Hover |
|---|---|---|---|
| `.btn-primary` | `--primary` | white | `#E05F48`, lift -1px |
| `.btn-accent` | `--accent` | white | `#7A8B69`, lift -1px |
| `.btn-secondary` | `--card` | `--foreground` | `--card-border` |
| `.btn-danger` | `--danger` | white | `#D06755` |

Modifiers:
- `.btn-small` — smaller padding (0.4rem 0.8rem), 0.8rem font
- `.btn-full` — block, full width
- `.btn:disabled` — 50% opacity, not-allowed cursor
- `.btn-primary.copied` — background becomes `--success`

---

## Cards

- `.card` — `--card` background, 1.5rem padding, 6px radius, `--card-border` border
- `.card-header` — flex row, space-between, centered, 1rem bottom margin

---

## Badges

- `.badge` — `--accent` background, 0.5rem 1rem padding, 6px radius, weight 600, 0.875rem font

State modifiers:
- `.badge.valid`, `.badge.success` → `--success`
- `.badge.warning` → `--warning`
- `.badge.danger` → `--danger`

---

## Phone Preview

- `.phone-preview` — centered flex column, `--card` background, 6px radius, 2rem padding, min-height 500px
- `.phone-frame` — 320px wide, black, 32px radius, subtle shadow
- `.phone-notch` — 120×24px, centered at top of frame
- `.phone-screen` — 600px tall, dark gradient, 24px radius, scrollable, 40px top padding

### Message Bubble

- `.message-bubble` — iMessage blue, white text, 18px radius (4px bottom-right), max 85% width, right-aligned
- `.variable-highlight` — white 20% opacity background, for unfilled variables
- `.variable-filled` — white, weight 500
- `.missing-var` — danger-red 60% opacity background

### Contact Header

- `.contact-avatar` — 40×40px circle, blue (`#4A7CFF`), centered initials
- `.contact-name` — 16px, weight 600, white
- `.contact-status` — 12px, white 50% opacity

---

## Table

- Full width, collapsed borders
- `th` — `--accent` background, uppercase, 0.9rem, weight 600, 0.05em spacing
- `td` — 0.75rem padding, `#2A2A2A` bottom border
- `tr.valid` — 3px `--success` left border
- `tr.invalid` — 3px `--danger` left border, 70% opacity
- `tr.selected-row td` — iMessage blue 8% opacity background
- `tr:hover` — white 2% opacity background

---

## Code Output

- `.code-output` — monospace (`Courier New`), 0.9rem, `--background` fill, `--card-border` border, 8px radius, pre-wrap whitespace

---

## Output Label

- `.output-label` — uppercase, 0.75rem, weight 600, 0.1em spacing, `--warm-gray` color, flex with 0.5rem gap

---

## Edits Section

- `.edits-section` — `--card` background, 1.5rem padding, 16px radius, animated border/opacity
- `.edits-section.inactive` — 45% opacity, pointer-events disabled
- `.edits-section.active` — `--primary` border color
- Status dot — 8×8px circle; active state: `--primary` with glow shadow

---

## Empty State

- `.empty-state` — centered flex column, min-height 250px, `--warm-gray` text
- `.empty-state .icon` — 4rem, 50% opacity

---

## Utilities

- `.presets` — flex wrap, 0.5rem gap
- `.header-section` — centered text, 2rem bottom margin

---

## Scrollbar

Custom webkit scrollbar: 8px, `--background` track, `--card-border` thumb (4px radius), `--warm-gray` thumb on hover
