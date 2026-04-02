---
name: virtual-card-art-checker
description: >
  Use this skill whenever a user submits, uploads, or shares a card art image for review
  of a **virtual or digital card** design — checking against Visa Digital Card Brand Standards
  and Rain's internal requirements. Trigger on phrases like "check this card art", "review my
  virtual card design", "does this pass", "card submission review", "validate card art",
  "check the digital card image", "is this compliant", or when a user uploads an image and
  mentions virtual cards, digital cards, Visa brand guidelines, or card art for digital use.
  Also use when the user asks for the RGB fallback colors for a virtual card submission.
  This skill checks technical specs (dimensions, format, DPI calculated from resolution)
  and visual design compliance against Visa Digital Card Brand Standards (September 2025),
  including landscape orientation. It always generates an output review image showing the
  56px Visa Brand Mark bleed border, suggested RGB fallback colors, and a sample PAN overlay.
---

# Virtual Card Art Checker

This skill reviews virtual/digital card art submissions against Visa Digital Card Brand Standards
(September 2025) and Rain's internal requirements. It produces a structured compliance report,
suggests RGB fallback color values, and generates a visual output image for review.

---

## Your job

When a user shares a card art image (or multiple images), you will:

1. **Locate or download the image file** so you can run technical checks on it
2. **Run the technical spec checker** (Python script — fast, objective)
3. **Visually inspect the image** using your vision capabilities
4. **Produce a structured compliance report** with a clear pass/fail for every check
5. **Show the generated output image** to the user — it includes the 56px bleed border,
   suggested RGB fallback colors, and a sample last-4 PAN overlay
6. **Present the suggested RGB fallback colors** (background, foreground, label)

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
   - Standard virtual card art is **1536 × 969**. If the image looks like a standard landscape
     card and there's no reason to think otherwise, use these dimensions.
   - If the image is clearly a different size or aspect ratio, estimate accordingly.
4. **Filename** — derive a sensible filename from the card name/context (e.g.
   `visa_platinum_virtual.png`)

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
visually. Upload via file picker for pixel-accurate verification."* All other checks (format,
DPI, visual checklist) can be reported normally.

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
scripts = glob.glob('/sessions/*/virtual-card-art-checker/scripts/check_technical_specs.py')
if not scripts:
    scripts = glob.glob('/sessions/*/virtual-card-art-checker-extracted/virtual-card-art-checker/scripts/check_technical_specs.py')

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
SKILL_ZIP=$(find /sessions/*/mnt/uploads/ -name "virtual-card-art-checker.skill" 2>/dev/null | head -1)
SESSION_DIR=$(echo "$SKILL_ZIP" | grep -oP '/sessions/[^/]+')
unzip -o "$SKILL_ZIP" -d "${SESSION_DIR}/virtual-card-art-checker/"
```

This outputs JSON with:
- Pass/fail for: dimensions, file format, DPI (calculated from image resolution)
- Suggested RGB fallback colors (background, foreground, label)
- Path to the generated output review image

Save the JSON output — you'll use it in the report.

If Pillow isn't installed, the script installs it automatically.

**Important**: The script always generates an output review image (`<filename>_review.png`) in
the same directory as the input image. This image shows the card art with the 56px bleed border,
a sample "•••• 6789" PAN in the suggested foreground color, and the three RGB color values
displayed to the right. **Always show this output image to the user.**

---

## Step 3: Visual inspection checklist

With the image in front of you, check each of the following visually. Be thorough — some of these
are easy to miss:

### ✅ Required elements (must be present)
- [ ] **Visa Brand Mark**: clearly visible, legible, not distorted or stretched
- [ ] **Visa Brand Mark position**: in the upper-left or upper-right corner of the card
- [ ] **Visa Brand Mark margin**: appears to be ~56px (≈3.6% of card width) from nearest edges —
      **this margin requirement applies ONLY to the Visa Brand Mark**, not to other logos or design elements
- [ ] **Issuer logo**: clearly present (may bleed to edge — no margin requirement)

### 🚫 Prohibited elements (must NOT be present)
- [ ] **EMV chip graphic**: no chip contact image or chip artwork
- [ ] **Hologram imagery**: no static hologram pictures, foil-style graphics, or dove hologram
- [ ] **Cardholder name**: no name on the card
- [ ] **Full PAN / card number**: no card number digits
- [ ] **Expiry date**: no expiry date
- [ ] **3D / embossed effects**: the design should look flat and digital, not like a photograph of a card
- [ ] **Physical card photography**: no photograph or highly detailed realistic illustration of a physical card
- [ ] **Embossed attribute labels**: no text labels describing embossed-only features

### 📐 Layout & orientation
- [ ] **Orientation**: horizontal (landscape) — **required** for Visa review submissions
- [ ] **Aspect ratio**: looks proportional to a standard credit card (roughly 1.586:1 width:height)

### 🎨 Design quality
- [ ] **Color**: appears to be full-color (not grayscale or monochrome)
- [ ] **Legibility**: Visa Brand Mark and any text elements are legible at card size

### ℹ️ Important: Bleed rules
- The **56px margin requirement applies ONLY to the Visa Brand Mark**
- Issuer logos, design elements, artwork, and other visuals **may extend to the card edge** (full bleed is allowed)
- Do NOT flag non-Visa elements for being too close to the edge

---

## Step 4: Suggested RGB fallback colors

The spec checker script extracts and suggests fallback colors automatically. These are YOUR
suggestions based on analyzing the card design — the issuer should confirm they match their
brand intent.

| Color | What it's used for | How to identify it |
|-------|-------------------|--------------------|
| **Background color** | Shown when the card image can't render (low-bandwidth fallback) | The dominant background/fill color of the card design |
| **Foreground color** | Variable values like last 4 PAN digits | A color with strong contrast against the background |
| **Label color** | Static labels on the card (e.g., "Debit", "Credit", account type) | A color readable against the background |

Review the script's suggestions against what you see in the design. If the card has a complex
gradient or pattern, note the most representative solid color. Override the script's suggestion
in the report if your visual judgment produces a better match.

---

## Step 5: Show the output image

The spec checker generates an output review image (`<filename>_review.png`). **Always show this
image to the user** using the Read tool. The image contains:

- The card art displayed with a visible **56px bleed border** around it
- A sample **"•••• 6789" PAN** overlaid in the bottom-left of the card using the suggested foreground color
- **Three RGB color values** (Background, Foreground, Label) displayed to the right of the card
  with color swatches

This gives the issuer a visual reference for how the fallback colors and PAN digits will look.

---

## Step 6: Produce the compliance report

Output a report in this exact format. Be direct — issuers need to know exactly what to fix.

---

### Virtual Card Art Compliance Report

**File**: `[filename]`
**Reviewed against**: Visa Digital Card Brand Standards (Sept 2025) + Rain requirements

---

#### Technical Specs

| Check | Result | Detail |
|-------|--------|--------|
| Dimensions (1536×969px) | ✅ Pass / ❌ Fail / ⚠️ Estimated | Actual: `[W×H]` or "Could not verify — file not on disk" |
| File format (PNG) | ✅ Pass / ❌ Fail / ⚠️ Unverified | Actual: `[format]` or inferred from filename/URL |
| DPI (≥72 for digital display) | ✅ Pass / ❌ Fail / ⚠️ Unverified | Calculated: `[value]` DPI (from pixel width ÷ 3.375″) |

---

#### Visual Design Compliance

| Check | Result | Notes |
|-------|--------|-------|
| Visa Brand Mark present | ✅ / ❌ | |
| Visa Brand Mark position (upper-left or upper-right) | ✅ / ❌ | |
| Visa Brand Mark margin (~56px from edges) | ✅ / ❌ / ⚠️ | This requirement applies ONLY to the Visa Brand Mark |
| Issuer logo present | ✅ / ❌ | May bleed to edge — no margin requirement |
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

#### Suggested RGB Fallback Colors

These values are suggested by the checker based on analyzing the card design. They serve as
fallbacks when the card image cannot render due to low bandwidth or connectivity issues.

| Color Field | RGB Value | Hex | Notes |
|------------|-----------|-----|-------|
| Background color | `rgb([R], [G], [B])` | `#RRGGBB` | [confirm or note if adjusted] |
| Foreground color | `rgb([R], [G], [B])` | `#RRGGBB` | For last 4 PAN digits + variable values |
| Label color | `rgb([R], [G], [B])` | `#RRGGBB` | For static labels on the card |

> ⚠️ These colors are suggested based on analyzing the card design. Please confirm with your
> designer that they match the intended brand colors before submitting.

**Output image**: `[path to _review.png]` — shows the bleed border, sample PAN, and color values.

---

#### Overall Status

**[✅ APPROVED / ❌ REQUIRES CHANGES / ⚠️ APPROVED WITH NOTES]**

[1-2 sentence summary. If there are failures, list what needs to be fixed. Be specific.]

---

## Notes on edge cases

- **RGBA images**: Flag as a warning rather than an outright failure — the issuer should confirm
  transparency is intentional. Recommend converting to RGB with a solid background.
- **DPI calculation**: DPI is calculated as `pixel_width ÷ 3.375` (ISO ID-1 card width in inches).
  For digital display, the Visa minimum is 72 DPI. At the standard 1536px width, this calculates
  to ~455 DPI which comfortably exceeds the minimum.
- **Missing DPI metadata**: Not relevant — DPI is always calculated from pixel dimensions, not
  read from file metadata.
- **Contactless indicator (⟳)**: Allowed even if the physical card isn't contactless — do not flag.
- **Portrait orientation**: Only flag if this is being submitted for Visa review. Portrait display
  in-app is permitted; portrait submission is not.
- **Partial card images**: Acceptable as long as the user confirms the full image is shown elsewhere
  in the flow.
- **Gradients**: Fine. Extract the most representative solid color for the fallback values.
- **Bleed to edge**: Only the Visa Brand Mark has a 56px margin requirement. All other logos,
  artwork, and design elements may extend to the card edge without restriction.

---

## Reference

Full requirements are in `references/visa-requirements.md`. Read it if you're unsure about a specific check.
