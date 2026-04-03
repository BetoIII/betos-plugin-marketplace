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

> **⚠️ #1 REJECTION REASON — 56px Visa Brand Mark Margin**
>
> The most common reason Visa rejects card art is the **Visa Brand Mark (including "VISA" text
> and the product identifier like "Signature", "Platinum", etc.) being too close to the card
> edges**. The mark must be at least 56px from the nearest edges — even 1px under is a rejection.
> The Python script now includes a **two-pass Visa Brand Mark distance measurement** that:
> 1. Locates the mark using brightness + density filtering (separates text from decoration)
> 2. Measures exact pixel distance from the mark to the top/bottom and right card edges
> 3. Reports **FAIL** if distance < 56px, **WARN** if 56-58px (borderline)
>
> Borderline placements (56-58px) have been rejected by Visa in practice — treat WARN as a
> strong signal to adjust. Always visually verify with extreme scrutiny. When in doubt, **fail
> the card** — it is better to send back a card for adjustment than to let a borderline case
> through to Visa and get rejected.

---

## Your job

When a user shares a card art image (or multiple images), you will:

1. **Locate or download the image file** so you can run technical checks on it
2. **Run the technical spec checker** (Python script — fast, objective)
3. **Visually inspect the image** using your vision capabilities
4. **Review the suggested RGB fallback colors** (background, foreground, label)
5. **Generate the Card Art Checker Results image** — a single-page PNG with the card art,
   numbered location markers for warnings/failures, overall status, tech spec table, and
   visual design compliance table — output as a single-page PDF
6. **Show the results image** to the user
7. **Produce a structured compliance report** with a clear pass/fail for every check

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
- **Bleed zone analysis**: programmatic detection of content in the 56px Visa Brand Mark margin
  zone — if this check fails, the brand mark is almost certainly extending past the boundary and
  the card should be flagged as ❌ Fail for the margin check in Step 3
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
- [ ] **Visa Brand Mark position**: in the **upper-left or upper-right** corner only — no lower-edge placement allowed
- [ ] **Visa Brand Mark margin (CRITICAL — #1 rejection reason)**: Every part of the Visa Brand
      Mark — including the outermost edges of letters like the tips of the "A" in "VISA" and
      every character in the product identifier ("Signature", "Platinum", "Infinite", "Debit") —
      must be **fully inside** the 56px boundary on ALL sides (top, bottom, left, right edges of
      the card). **Zero tolerance**: if ANY pixel of the brand mark text touches or crosses the
      red dashed 56px boundary line shown in the review image, this is ❌ **FAIL**. Do NOT use
      approximate language ("looks about right", "appears close enough"). Zoom in on the boundary
      edges near the brand mark and check each edge explicitly. The script also runs a programmatic
      bleed zone analysis — if it flags content in the margin zone, treat that as strong evidence
      of failure. **This margin requirement applies ONLY to the Visa Brand Mark**, not to other
      logos or design elements
- [ ] **Visa Brand Mark size**: must match one of the two allowed size options (see below)
- [ ] **Issuer logo**: clearly present (may bleed to edge — no margin requirement)

#### Visa Brand Mark Size Options

Only two size options are permitted. Check which one is used and verify it matches:

**Option One — Visa Brand Mark with Debit Identifier** (for Debit cards):
| Measurement | Value | Description |
|---|---|---|
| C | 109 px | Height of Visa Brand Mark |
| D | 56 px | Distance from nearest card edge to Visa Brand Mark |
| E | 56 px | Distance from baseline of debit identifier to top of Visa Brand Mark |
| F | 50 px | Minimum height of debit identifier |

**Option Two — Visa Brand Mark (standalone or with Product Identifier)** (for Signature, Platinum, Infinite, etc.):
| Measurement | Value | Description |
|---|---|---|
| C | 142 px | Height of Visa Brand Mark |
| D | 220 px | Distance from top of Visa Brand Mark to baseline of product identifier (when present) |
| E | 56 px | Distance from nearest card edge to Visa Brand Mark |

When visually inspecting, estimate whether the Visa Brand Mark height appears to be approximately
109px (Option One) or 142px (Option Two) relative to the card dimensions. The mark should be
roughly **11.2%** (Option One) or **14.7%** (Option Two) of the card height (969px). If it looks
significantly smaller or larger than either option, flag it as ❌ Fail.

### 🚫 Prohibited elements (must NOT be present)
- [ ] **EMV chip graphic**: no chip contact image or chip artwork
- [ ] **Hologram imagery**: no static hologram pictures, foil-style graphics, or dove hologram
- [ ] **Magnetic stripe graphic**: no magnetic stripe imagery
- [ ] **Cardholder name**: no name on the card
- [ ] **Full PAN / card number**: no card number digits
- [ ] **Expiry date**: no expiry date
- [ ] **Physical card photography**: no photograph or highly detailed realistic illustration of a physical card
- [ ] **Embossed attribute labels**: no text labels describing embossed-only features
- [ ] **Lower-left area clear**: the lower-left area of the card is reserved for card personalization (last 4 PAN digits overlay) and **must not contain any marks or graphics** — this includes issuer logos, brand names, icons, design elements, or any other visual content. If anything other than the card background/pattern is in the lower-left, flag as ❌ Fail. Example: an issuer logo placed in the bottom-left corner would fail this check.
- [ ] **Design elements clear of product identifier**: no artwork, logos, or design elements obscuring or touching the Visa product identifier text (Signature, Platinum, Infinite, etc.)

### 📐 Layout & orientation
- [ ] **Orientation**: horizontal (landscape) — **required** for Visa review submissions
- [ ] **Aspect ratio**: looks proportional to a standard credit card (roughly 1.586:1 width:height)

### 🎨 Design quality
- [ ] **Color**: appears to be full-color (not grayscale or monochrome)
- [ ] **Legibility**: Visa Brand Mark and any text elements are legible at card size
- [ ] **Visa Brand Mark contrast**: the Visa Brand Mark (including the product identifier text —
      Signature, Platinum, Infinite, Debit, etc.) must have strong color contrast against the card's
      background. Both the "VISA" wordmark AND the product identifier must be clearly readable.
      Check that neither blends into or is hard to distinguish from the background color. Common
      issues: gray/silver text on light backgrounds, dark text on dark backgrounds, or a product
      identifier in a different color than the Visa wordmark that lacks sufficient contrast.
      If the Visa Brand Mark or product identifier is hard to read against the card background,
      flag as ❌ Fail and recommend using white or a higher-contrast color.

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

## Step 5: Generate the Card Art Checker Results image

After completing the visual inspection (Step 3) and reviewing the colors (Step 4), generate the
full results image. This combines everything — the card art with location markers, overall status,
tech spec table, and visual design compliance table — into a single-page PDF.

### 5a) Construct the visual results JSON

Build a JSON object from your visual inspection findings. The structure is:

```json
{
  "overall_status": "APPROVED | REQUIRES CHANGES | APPROVED WITH NOTES",
  "overall_description": "1-2 sentence summary of findings and what needs fixing",
  "visual_checks": [
    {
      "name": "Check name (from Step 3 checklist)",
      "result": "pass | fail | warning",
      "notes": "Brief explanation (optional for passes)"
    }
  ]
}
```

**Location-based markers**: For any failure or warning where a **specific location on the card**
caused the issue, add `marker_x` and `marker_y` fields (floats from 0.0 to 1.0) to place a
numbered marker on the card art. These fields are **only for location-specific issues** — not
every failure gets a marker.

- `marker_x`: 0.0 = left edge, 1.0 = right edge of card
- `marker_y`: 0.0 = top edge, 1.0 = bottom edge of card
- Place the marker at the approximate center of where the issue occurs

Examples of checks that **should** get markers:
- Visa Brand Mark contrast → marker at the Visa logo position
- Visa Brand Mark margin → marker at the edge where margin is insufficient
- Lower-left area not clear → marker at the offending element in the lower-left
- Design elements near product identifier → marker where elements encroach

Examples of checks that should **NOT** get markers:
- Landscape orientation (global, not location-specific)
- Full color / grayscale (global)
- No cardholder name (absence check — nowhere specific to point)
- File format / dimensions / DPI (technical, not visual location)

```json
{
  "name": "Visa Brand Mark contrast",
  "result": "fail",
  "notes": "Silver text on pink background — low contrast",
  "marker_x": 0.75,
  "marker_y": 0.12
}
```

Each marker gets an auto-assigned number (1, 2, 3, ...) that appears both on the card and in
the Ref column of the Visual Design Compliance table, creating a visual legend.

### 5b) Save the JSON and call the script

Save the visual results JSON to a temp file, then call the script with `--visual-results-file`:

```python
import json, glob, subprocess, sys

visual_results = {
    "overall_status": "...",       # from your assessment
    "overall_description": "...",  # from your assessment
    "visual_checks": [ ... ]       # from your Step 3 inspection
}

# Save to temp file
results_json_path = "/tmp/visual_results.json"
with open(results_json_path, "w") as f:
    json.dump(visual_results, f)

# Find the script
scripts = glob.glob('/sessions/*/virtual-card-art-checker/scripts/check_technical_specs.py')
if not scripts:
    scripts = glob.glob('/sessions/*/virtual-card-art-checker-extracted/virtual-card-art-checker/scripts/check_technical_specs.py')

if scripts:
    script_path = scripts[0]
    result = subprocess.run(
        [sys.executable, script_path, "<path-to-image>",
         "--visual-results-file", results_json_path],
        capture_output=True, text=True
    )
    print(result.stdout)
    if result.stderr:
        print(result.stderr)
```

This generates `<filename>_card_art_checker_results.pdf` in the same directory as the input image.

---

## Step 6: Show the results image

The script generates a **Card Art Checker Results** image (`<filename>_card_art_checker_results.pdf`).
**Always show this image to the user** using the Read tool. The single-page PNG contains:

1. **Card Art Review Pane** (top) — the card art with:
   - The 56px bleed border (red dashed line)
   - Sample "•••• 6789" PAN in the suggested foreground color
   - **Numbered markers** (colored circles) at exact locations where warnings/failures occur
   - RGB fallback color values displayed to the right with swatches

2. **Overall Status** — colored badge (green/red/orange) with summary description

3. **Technical Specifications** table — dimensions, format, DPI with pass/fail status

4. **Visual Design Compliance** table — all visual checks with:
   - **Ref column**: numbered markers matching those on the card art above
   - Check name, result (colored PASS/FAIL/WARN), and notes
   - Legend note linking the Ref numbers to the card markers

This gives the issuer a complete, self-contained compliance document.

After presenting the results, **always offer to open the PDF** for the user:
> "Would you like me to open the results PDF?"

If the user accepts, open it with: `open -a Preview "<path_to_results.pdf>"`

---

## Step 7: Produce the compliance report

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
| 56px Margin Zone (Visa Brand Mark) | ✅ Pass / ⚠️ Warn / ❌ Fail | Distance measurement from Visa Brand Mark to card edges. FAIL < 56px, WARN 56-58px (borderline) |

---

#### Visual Design Compliance

| Check | Result | Notes |
|-------|--------|-------|
| Visa Brand Mark present | ✅ / ❌ | |
| Visa Brand Mark position (upper-left or upper-right only) | ✅ / ❌ | No lower-edge placement allowed |
| Visa Brand Mark size (Option One: 109px / Option Two: 142px height) | ✅ / ❌ / ⚠️ | Must match one of the two allowed size options |
| Visa Brand Mark margin (56px from edges — **#1 rejection reason**) | ✅ / ❌ | Zero tolerance — any brand mark content past the 56px boundary is a hard fail. Cross-reference with bleed zone analysis. |
| Visa Brand Mark contrast against background | ✅ / ❌ | Both "VISA" and product identifier must be clearly readable |
| Issuer logo present | ✅ / ❌ | May bleed to edge — no margin requirement |
| No EMV chip graphic | ✅ / ❌ | |
| No hologram imagery | ✅ / ❌ | |
| No magnetic stripe graphic | ✅ / ❌ | |
| No cardholder name | ✅ / ❌ | |
| No PAN / card number | ✅ / ❌ | |
| No expiry date | ✅ / ❌ | |
| No physical card photography | ✅ / ❌ | |
| Lower-left area clear (no marks/graphics) | ✅ / ❌ | Reserved for card personalization — must be completely empty |
| Design elements clear of product identifier | ✅ / ❌ | No artwork touching Signature/Platinum/Infinite text |
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

**Results image**: `[path to _card_art_checker_results.pdf]` — full results with markers, tables, and status.

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
- **Contactless Indicator (⟳ / )))**: Allowed per Visa standards, even if the physical card is not contactless enabled. Do NOT flag as a failure.
- **Portrait orientation**: Only flag if this is being submitted for Visa review. Portrait display
  in-app is permitted; portrait submission is not.
- **Partial card images**: Acceptable as long as the user confirms the full image is shown elsewhere
  in the flow.
- **Gradients**: Fine. Extract the most representative solid color for the fallback values.
- **Bleed to edge**: Only the Visa Brand Mark has a 56px margin requirement. All other logos,
  artwork, and design elements may extend to the card edge without restriction.
- **Visa Brand Mark margin (most critical check)**: This is the #1 rejection reason from Visa.
  Even partial encroachment — a single letter tip crossing the 56px line — is a hard fail.
  The script measures exact pixel distance from the Visa Brand Mark to card edges — FAIL if < 56px,
  WARN if 56-58px (borderline). If the script flags a FAIL or WARN, visually confirm and fail the
  card. Do NOT pass a card where the brand mark is "close to" or "approximately at" the 56px boundary — if it's borderline,
  fail it. Visa will reject it.
- **Lower-left reserved zone**: The lower-left area of the card is reserved for card
  personalization (last 4 PAN digits). It must be completely free of marks or graphics —
  no issuer logos, brand names, icons, or design elements. Only the card's background color
  or pattern should be visible. This is a common mistake: issuers often place their logo in
  the bottom-left, which will be rejected.
- **Design elements near product identifier**: Artwork, logos, or large design elements must not
  obscure or touch the Visa product identifier text (Signature, Platinum, Infinite). Flag if
  elements encroach on the identifier text.

---

## Reference

Full requirements are in `references/visa-requirements.md`. Read it if you're unsure about a specific check.
