# Visa Digital Card Art Requirements Reference

*Source: Visa Digital Card Brand Standards (September 2025)*

---

## Technical Specifications

| Spec | Required Value |
|------|---------------|
| Dimensions | 1536 × 969 pixels |
| Aspect ratio | ISO ID-1 card proportional |
| File format | PNG |
| Color mode | RGB |
| Resolution | 72 DPI |
| Orientation for review submission | Horizontal (landscape) only |

---

## Required Elements

- **Visa Brand Mark**: Must be present, legible, and not distorted
  - Positioned in upper-left or upper-right corner
  - Must be at least 56px from all edges
- **Issuer logo**: Must be present
- **Last 4 digits indicator** (area for PAN display — not actual PAN values)

---

## Prohibited Elements

The following must NOT appear on digital card art:

| Prohibited Element | Reason |
|-------------------|--------|
| Cardholder name | Security |
| Full PAN / card number | Security |
| Expiry date | Security |
| EMV chip contacts / chip graphic | Physical-only element |
| Hologram imagery (static pictures of holograms) | Physical-only dynamic element |
| 3D shading / embossed effects making it look physical | Digital art must be flat |
| Physical card photographs or highly detailed card illustrations | No physical representations |
| Labels describing embossed attributes | Physical-only element |

---

## Orientation Rules

- **Preferred**: Landscape (horizontal) orientation
- **Allowed**: Portrait (vertical) on devices supporting vertical orientation
- **For Visa review submission**: Always submit in horizontal orientation
- **Brand Mark placement when stacked**: Upper-left or upper-right

---

## Fallback RGB Color Values (Required from Issuer)

These are submitted separately from the card art image — they are used as fallbacks when the card image cannot render (low bandwidth, connectivity issues):

| Color Field | Purpose | Example |
|-------------|---------|---------|
| `background_color` | Shown when card image can't render | Dominant card background color |
| `foreground_color` | For variable values: last 4 PAN digits | Usually light or dark text color |
| `label_color` | For labels on the card (e.g., "Debit", "Credit") | Usually matches foreground or brand color |

---

## Display Rules

- Must appear in full color on color-capable screens
- Partial card image is acceptable only after user has already seen full card image
- Contactless Indicator (⟳) may be included even if physical card isn't contactless
- Do not alter position of card elements from approved layout

---

## What "Digital" Means (vs. Physical)

Digital card art is NOT required to match the physical card. Key differences:
- No chip graphic
- No hologram graphic
- No 3D/embossed effects
- No physical card photography
- Flat design appropriate for screen display
