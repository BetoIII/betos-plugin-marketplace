---
name: card-art-checker
description: >
  Use this skill whenever a user submits, uploads, or shares a card art image for review — virtual card designs,
  digital card art, card submissions, or any image being checked for Visa compliance. Trigger on phrases like
  "check this card art", "review my card design", "does this pass", "card submission review", "validate card art",
  "check the card image", "is this compliant", or when a user uploads an image and mentions cards, Visa, brand
  guidelines, or card design. Also use when the user asks for the RGB fallback colors for a card submission.
  This skill checks both technical specs (dimensions, format, DPI, color mode) and visual design compliance
  against Visa Digital Card Brand Standards.
---

# Card Art Checker

This skill reviews digital/virtual card art submissions against Visa Digital Card Brand Standards
and Rain's internal requirements. It produces a structured compliance report and extracts the
RGB fallback color values the issuer needs to provide.

---

## Your job

When a user shares a card art image (or multiple images), you will:

1. **Locate or download the image file** so you can run technical checks on it
2. **Run the technical spec checker** (Python script — fast, objective)
3. **Visually inspect the image** using your vision capabilities
4. **Produce a structured compliance report** with a clear pass/fail for every check
5. **Extract and confirm RGB fallback colors** (background, foreground, label)

Do this even if the user says "quick check" or seems to want a brief review — the full checklist
is important and shouldn't be skipped. A card that fails compliance can delay an issuer's launch.

---

## Step 1: Get the image file

The image can arrive in three ways. Handle each one:

### A) Image attached directly in the conversation
Check common upload locations — `~/uploads/`, `/tmp/uploads/`, or any path the user mentions.
If the file is present, use that path with the spec checker script.

If the uploads folder is empty, the image is only available visually in the conversation context.
In that case, **skip the Python spec checker and proceed to visual-only mode** (see note at end of
this step). You can still run a meaningful review — just flag which technical checks couldn't be
verified programmatically.

### B) URL provided (e.g., a Slack link, Google Drive link, or direct image URL)
Try to download the image using Python:

```python
import requests, os, re
url = "<the URL>"
# Try to infer filename from URL
filename = re.split(r'[/?#]', url)[-1] or "card_art_image"
if '.' not in filename:
    filename += ".jpg"  # fallback extension
out_path = f"/tmp/{filename}"
r = requests.get(url, timeout=15)
r.raise_for_status()
with open(out_path, 'wb') as f:
    f.write(r.content)
print(f"Downloaded to {out_path}")
```

If the URL is behind authentication (e.g., Slack, Google Drive) and the download fails or returns
HTML instead of image bytes, **fall back to visual-only mode**. Note the URL source in the report.

### C) File path provided explicitly
Use the path directly with the spec checker script.

---

**Visual-only mode** (when no file is accessible on disk): Skip the Python script. Do the full
visual checklist in Step 3, and in the Technical Specs section of the report, mark dimensions,
color mode, and DPI as ⚠️ Unverified with a note explaining why. You can still confirm file
format from the filename/URL extension or Slack metadata if available.

---

## Step 2: Run the technical spec checker

Once you have a file path, run:

```bash
python3 "${CLAUDE_PLUGIN_ROOT}/skills/card-art-checker/scripts/check_technical_specs.py" <path-to-image>
```

This outputs JSON with:
- Pass/fail for: dimensions, file format, color mode, DPI
- Dominant colors and suggested fallback RGB values

Save the JSON output — you'll use it in the report.

If Pillow isn't installed, the script installs it automatically.

---

## Step 3: Visual inspection checklist

With the image in front of you, check each of the following visually. Be thorough — some of these
are easy to miss:

### ✅ Required elements (must be present)
- [ ] **Visa Brand Mark**: clearly visible, legible, not distorted or stretched
- [ ] **Visa Brand Mark position**: in the upper-left or upper-right corner of the card
- [ ] **Visa Brand Mark margin**: appears to be ~56px (≈3.6% of card width) from nearest edges
- [ ] **Issuer logo**: clearly present
- [ ] **Last 4 digit area**: space or placeholder for displaying last 4 digits of PAN

### 🚫 Prohibited elements (must NOT be present)
- [ ] **EMV chip graphic**: no chip contact image or chip artwork
- [ ] **Hologram imagery**: no static hologram pictures, foil-style graphics, or dove hologram
- [ ] **Cardholder name**: no name on the card
- [ ] **Full PAN / card number**: no card number digits (last 4 placeholder is OK)
- [ ] **Expiry date**: no expiry date
- [ ] **3D / embossed effects**: the design should look flat and digital, not like a photograph of a card
- [ ] **Physical card photography**: no photograph or highly detailed realistic illustration of a physical card
- [ ] **Embossed attribute labels**: no text labels describing embossed-only features

### 📐 Layout & orientation
- [ ] **Orientation**: horizontal (landscape) — this is required for Visa review submissions
- [ ] **Aspect ratio**: looks proportional to a standard credit card (roughly 1.586:1 width:height)

### 🎨 Design quality
- [ ] **Color**: appears to be full-color (not grayscale or monochrome)
- [ ] **Legibility**: Visa Brand Mark and any text elements are legible at card size

---

## Step 4: Extract RGB fallback colors

If you ran the spec checker, it will have suggested fallback colors — use those as a starting point.
In visual-only mode, estimate the colors directly from what you see. Review the image and determine:

| Color | What it's used for | How to identify it |
|-------|-------------------|--------------------|
| **Background color** | Shown when the card image can't render (low-bandwidth fallback) | The dominant background/fill color of the card design |
| **Foreground color** | Variable values like last 4 PAN digits | The color used for prominent text/numbers on the card |
| **Label color** | Static labels on the card (e.g., "Debit", "Credit", account type) | The color used for descriptive labels |

The script auto-suggests these from the image — confirm they look right based on the design.
If the card has a complex gradient or pattern, note the most representative solid color.

---

## Step 5: Produce the compliance report

Output a report in this exact format. Be direct — issuers need to know exactly what to fix.

---

### Card Art Compliance Report

**File**: `[filename]`
**Reviewed against**: Visa Digital Card Brand Standards (Sept 2025) + Rain requirements

---

#### Technical Specs

| Check | Result | Detail |
|-------|--------|--------|
| Dimensions (1536×969px) | ✅ Pass / ❌ Fail / ⚠️ Unverified | Actual: `[W×H]` or "Could not verify — file not on disk" |
| File format (PNG) | ✅ Pass / ❌ Fail / ⚠️ Unverified | Actual: `[format]` or inferred from filename/URL |
| Color mode (RGB) | ✅ Pass / ❌ Fail / ⚠️ Unverified | Actual: `[mode]` or "Could not verify — file not on disk" |
| DPI (72) | ✅ Pass / ❌ Fail / ⚠️ Unverified | `[note]` |

---

#### Visual Design Compliance

| Check | Result | Notes |
|-------|--------|-------|
| Visa Brand Mark present | ✅ / ❌ | |
| Visa Brand Mark position (upper-left or upper-right) | ✅ / ❌ | |
| Visa Brand Mark margin (~56px from edges) | ✅ / ❌ / ⚠️ | |
| Issuer logo present | ✅ / ❌ | |
| No EMV chip graphic | ✅ / ❌ | |
| No hologram imagery | ✅ / ❌ | |
| No cardholder name | ✅ / ❌ | |
| No PAN / card number | ✅ / ❌ | |
| No expiry date | ✅ / ❌ | |
| No 3D / embossed effects | ✅ / ❌ | |
| No physical card photography | ✅ / ❌ | |
| Landscape orientation | ✅ / ❌ | |
| Full color (not grayscale) | ✅ / ❌ | |

---

#### RGB Fallback Colors

These values are required when submitting card art to Rain. They serve as fallbacks when the
card image cannot render due to low bandwidth or connectivity issues.

| Color Field | RGB Value | Hex | Notes |
|------------|-----------|-----|-------|
| Background color | `rgb([R], [G], [B])` | `#RRGGBB` | [confirm or note if unsure] |
| Foreground color | `rgb([R], [G], [B])` | `#RRGGBB` | For last 4 PAN digits + variable values |
| Label color | `rgb([R], [G], [B])` | `#RRGGBB` | For static labels on the card |

> ⚠️ These colors are auto-extracted from the image. Please confirm with your designer that they
> match the intended brand colors before submitting.

---

#### Overall Status

**[✅ APPROVED / ❌ REQUIRES CHANGES / ⚠️ APPROVED WITH NOTES]**

[1-2 sentence summary. If there are failures, list what needs to be fixed. Be specific.]

---

## Notes on edge cases

- **RGBA images**: Flag as a warning rather than an outright failure — the issuer should confirm
  transparency is intentional. Recommend converting to RGB with a solid background.
- **Missing DPI metadata**: Not a blocker, but note it. Many design tools don't embed DPI in PNGs.
  Ask the issuer to confirm the export was set to 72 DPI.
- **Contactless indicator (⟳)**: This is allowed even if the physical card isn't contactless — do
  not flag it as an error.
- **Portrait orientation**: Only flag if this is being submitted for Visa review. Portrait display
  in-app is permitted; portrait submission is not.
- **Partial card images**: Acceptable as long as the user confirms the full image is shown elsewhere
  in the flow.
- **Gradients**: These are fine. Extract the most representative solid color for the fallback values.

---

## Reference

Full requirements are in `references/visa-requirements.md`. Read it if you're unsure about a specific check.
