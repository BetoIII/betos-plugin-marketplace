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
Run the following Python to find the uploads folder and any image files in it — the session name
changes every session, so never hardcode it:

```python
import glob, os

# Dynamically find the uploads folder (session name varies every run)
sessions = sorted(glob.glob('/sessions/*/mnt/uploads/'))
uploads_dir = sessions[0] if sessions else None

image_extensions = ['*.png', '*.jpg', '*.jpeg', '*.webp',
                    '*.PNG', '*.JPG', '*.JPEG', '*.WEBP']
image_files = []
if uploads_dir:
    for ext in image_extensions:
        image_files.extend(glob.glob(os.path.join(uploads_dir, ext)))

if image_files:
    print(f"Found: {image_files}")
else:
    print(f"No image files found in: {uploads_dir}")
```

Use the first image found as the source file for Step 2. If multiple images are present, ask the
user which one to check.

**If no image file is found in uploads** (i.e. the image was pasted inline rather than uploaded
via the file picker), do NOT fall back to visual-only mode — instead proceed to **inline
reconstruction** (Step 1B below) to create a working file so the spec checker can run.

### A2) Inline reconstruction (when no file is found on disk)

Cowork does not write inline-pasted images to disk — they only exist as base64 in the
conversation context. To work around this, reconstruct a working PNG file using PIL based on
what you can observe visually. This is not pixel-perfect, but it allows the spec checker to run
and eliminates ⚠️ Unverified results wherever possible.

Before writing the reconstruction code, visually inspect the image and determine:

1. **Background color** — the dominant solid fill color (as R, G, B integers)
2. **Color mode** — is it RGB (solid, no transparency) or RGBA (has transparent areas)?
3. **Approximate dimensions** — estimate width × height in pixels:
   - Standard digital card art is **1536 × 969**. If the image looks like a standard landscape
     card and there's no reason to think otherwise, use these dimensions.
   - If the image is clearly a different size or aspect ratio, estimate accordingly.
4. **Filename** — derive a sensible filename from the card name/context (e.g.
   `visa_platinum_white.png`)

Then run this Python, substituting in your observations:

```python
from PIL import Image
import os

# --- Fill these in based on visual inspection ---
bg_color     = (R, G, B)           # e.g. (255, 255, 255) for white
color_mode   = "RGB"               # "RGB" or "RGBA"
width        = 1536                # estimated width in pixels
height       = 969                 # estimated height in pixels
filename     = "card_art_inline.png"
# ------------------------------------------------

out_path = f"/tmp/{filename}"
img = Image.new(color_mode, (width, height), bg_color)
img.save(out_path, "PNG", dpi=(72, 72))
print(f"Saved reconstruction to: {out_path} ({width}x{height}, {color_mode})")
```

Use `out_path` as the source file for Step 2. In the final report, mark the Dimensions row as
`⚠️ Estimated` (not ✅ Pass or ❌ Fail) and add a note: *"Inline paste — dimensions estimated
visually. Upload via file picker for pixel-accurate verification."* All other checks (color mode,
format, DPI, visual checklist) can be reported normally.

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
HTML instead of image bytes, **use inline reconstruction (Step A2 above)**. Note the URL source
in the report and mark Dimensions as ⚠️ Estimated.

### C) File path provided explicitly
Use the path directly with the spec checker script.

---

## Step 2: Run the technical spec checker

Once you have a file path, locate and run the spec checker script. The script is extracted alongside
the skill — find it dynamically (session name changes every run):

```python
import glob, subprocess, sys

# Find the spec checker script — never hardcode the session name
scripts = glob.glob('/sessions/*/card-art-checker/scripts/check_technical_specs.py')
if not scripts:
    # Also check the extracted skill folder name variations
    scripts = glob.glob('/sessions/*/card-art-checker-extracted/card-art-checker/scripts/check_technical_specs.py')

if scripts:
    script_path = scripts[0]
    result = subprocess.run([sys.executable, script_path, "<path-to-image>"],
                            capture_output=True, text=True)
    print(result.stdout)
else:
    print("Script not found — will need to extract from skill zip first")
```

If the script isn't found, extract the skill zip first:
```bash
# Find and extract the skill zip
SKILL_ZIP=$(find /sessions/*/mnt/uploads/ -name "card-art-checker.skill" 2>/dev/null | head -1)
SESSION_DIR=$(echo "$SKILL_ZIP" | grep -oP '/sessions/[^/]+')
unzip -o "$SKILL_ZIP" -d "${SESSION_DIR}/card-art-checker/"
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
