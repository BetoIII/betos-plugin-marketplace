# Virtual / Digital Card Art Requirements Reference

*Source: Visa Digital Card Brand Standards (September 2025)*

---

## Technical Specifications

| Spec | Required Value |
|------|---------------|
| Dimensions | 1536 × 969 pixels |
| Aspect ratio | ISO ID-1 card proportional |
| File format | PNG |
| Resolution | ≥72 DPI (calculated from pixel width ÷ 3.375″) |
| Orientation for review submission | Horizontal (landscape) only |

> DPI is calculated from image resolution — not read from file metadata.
> Formula: `pixel_width ÷ 3.375` (ISO ID-1 card width in inches).
> At the standard 1536px width, calculated DPI is ~455, well above the 72 DPI minimum.

---

## Basic Graphic Elements (Required)

Per Visa Digital Card Brand Standards, these elements must appear on every digital card:

| Element | Requirement |
|---------|-------------|
| **A — Issuer logo** | Must be present and legible. May bleed to edge — no margin requirement. |
| **B — Issuer card art** | The card design itself. Design elements may extend to the card edge. |
| **C — Visa Brand Mark** | Must be present, legible, and not distorted |

---

## Visa Brand Mark Requirements

- Must be present and clearly legible
- Positioned in **upper-left or upper-right** corner only (landscape submission)
- Minimum margin of ~56px (≈3.6% of card width) from nearest edges — **this margin applies ONLY to the Visa Brand Mark**
- Must not be distorted or stretched
- When cards are stacked in a digital wallet, Brand Mark must be visible in upper-left or upper-right
- **Other logos and design elements have NO margin requirement** — they may bleed to the card edge

---

## Orientation Rules

- **Preferred display**: Landscape (horizontal)
- **Allowed in-app display**: Portrait (vertical) on devices that support it
- **For Visa review submission**: **Always submit in horizontal (landscape) orientation**
- When displayed vertically, the Brand Mark must still be in upper-left or upper-right

---

## Bleed Rules

- The **56px margin requirement applies ONLY to the Visa Brand Mark**
- Issuer logos, design elements, artwork, and other visuals **may extend to the card edge** (full bleed is allowed)
- Do NOT flag non-Visa elements for being too close to the edge

---

## Prohibited Elements

The following must NOT appear on digital card art:

| Prohibited Element | Reason |
|-------------------|--------|
| Cardholder name | Security |
| Full PAN / card number | Security |
| Expiry date | Security |
| EMV chip contacts / chip graphic | Physical-only element |
| Hologram imagery (static pictures of holograms, Visa Dove) | Physical-only dynamic element |
| 3D shading / embossed effects making it look physical | Digital art must be flat |
| Physical card photographs or highly detailed card illustrations | No physical representations |
| Labels describing embossed attributes | Physical-only element |

---

## Permitted Elements

- Contactless Indicator (⟳) — even if the physical card isn't contactless enabled
- Partial card image — acceptable only after the user has already seen the full digital card art
- Gradients and flat color designs

---

## Display Rules

- Must appear in full color on color-capable screens
- Do not alter the position of card elements from the approved layout
- Card art is NOT required to match the physical card design
- Card art must not include shading or three-dimensional elements attempting to look like a physical card

---

## Fallback RGB Color Values (Required from Issuer)

Submitted separately from the card art image. Used as fallbacks when the card image cannot render (low bandwidth, connectivity issues):

| Color Field | Purpose | How to Identify |
|-------------|---------|-----------------|
| `background_color` | Shown when card image can't render | Dominant card background color |
| `foreground_color` | For variable values: last 4 PAN digits | Color used for prominent text/numbers |
| `label_color` | For labels on the card (e.g., "Debit", "Credit") | Color used for descriptive labels |

---

## What "Digital" Means (vs. Physical)

Digital card art is NOT required to match the physical card. Key differences:
- No chip graphic
- No hologram graphic
- No 3D/embossed effects
- No physical card photography
- Flat design appropriate for screen display
- Must include last 4 PAN digit placeholder (physical cards do not require this in design artwork)
