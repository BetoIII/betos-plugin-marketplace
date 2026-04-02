#!/usr/bin/env python3
"""
Technical spec checker for Visa virtual/digital card art.
Checks dimensions, format, and DPI (calculated from image resolution).
Extracts dominant colors and suggests background, foreground, and label RGB values.
Generates an output image showing the 56px bleed border, suggested RGB values,
and a sample last-4 PAN overlay.

DPI is calculated as: pixel_width / CARD_WIDTH_INCHES
where CARD_WIDTH_INCHES = 3.375 (ISO ID-1 standard credit card width).
For Visa digital card display, a minimum of 72 DPI is required.
At the standard 1536px width, calculated DPI is ~455, well above the minimum.

Usage:
    python3 check_technical_specs.py <image_path> [--output-dir /path/to/dir]

Outputs JSON with technical check results and extracted colors.
Also saves an output image to the same directory as the input (or --output-dir).
"""

import sys
import json
import os
import argparse

try:
    from PIL import Image, ImageDraw, ImageFont
    import numpy as np
except ImportError:
    import subprocess
    subprocess.check_call([sys.executable, "-m", "pip", "install", "Pillow", "numpy", "-q"])
    from PIL import Image, ImageDraw, ImageFont
    import numpy as np


REQUIRED_WIDTH = 1536
REQUIRED_HEIGHT = 969
REQUIRED_FORMAT = "PNG"
CARD_WIDTH_INCHES = 3.375   # ISO ID-1 standard credit card width
MIN_DPI_DIGITAL = 72        # Visa minimum DPI for digital card display
VISA_MARK_EDGE_MARGIN = 56  # pixels — applies ONLY to the Visa Brand Mark


def extract_colors(img):
    """Extract background, foreground, and label color suggestions from the image."""
    rgb_img = img.convert("RGB")
    arr = np.array(rgb_img)

    # Background color: sample corners (avoid logo areas)
    corner_size = 40
    corners = [
        arr[:corner_size, :corner_size],
        arr[:corner_size, -corner_size:],
        arr[-corner_size:, :corner_size],
        arr[-corner_size:, -corner_size:],
    ]
    corner_pixels = np.concatenate([c.reshape(-1, 3) for c in corners], axis=0)
    bg_color = corner_pixels.mean(axis=0).astype(int).tolist()

    # Dominant colors — sample a grid of pixels
    sample = arr[::8, ::8].reshape(-1, 3)

    from collections import Counter
    quantized = (sample // 16) * 16
    counts = Counter(map(tuple, quantized.tolist()))
    most_common = counts.most_common(10)

    dominant_colors = [
        {"rgb": list(color), "hex": "#{:02X}{:02X}{:02X}".format(*color), "count": cnt}
        for color, cnt in most_common
    ]

    # Background luminance for contrast decisions
    bg_luminance = 0.299 * bg_color[0] + 0.587 * bg_color[1] + 0.114 * bg_color[2]

    # Separate dominant colors into "background-like" and "accent" colors
    # Background-like = close in luminance to bg_color; accent = everything else with enough contrast
    accent_colors = []
    for dc in dominant_colors:
        c = dc["rgb"]
        lum = 0.299 * c[0] + 0.587 * c[1] + 0.114 * c[2]
        contrast = abs(lum - bg_luminance)
        # Check it's not just a shade of gray close to background
        is_chromatic = max(c) - min(c) > 20  # has some color saturation
        if contrast > 40:
            accent_colors.append({"rgb": c, "lum": lum, "contrast": contrast,
                                  "chromatic": is_chromatic, "count": dc["count"]})

    # Foreground color: prefer a chromatic accent color with good contrast, fall back to white/black
    suggested_fg = [255, 255, 255] if bg_luminance < 128 else [30, 30, 30]
    # First try chromatic accents (brand colors like gold, blue, etc.)
    for ac in accent_colors:
        if ac["chromatic"] and ac["contrast"] > 60:
            suggested_fg = ac["rgb"]
            break
    # If no chromatic accent found, use the highest-contrast dominant color
    if suggested_fg in ([255, 255, 255], [30, 30, 30]):
        for ac in sorted(accent_colors, key=lambda x: x["contrast"], reverse=True):
            if ac["contrast"] > 60:
                suggested_fg = ac["rgb"]
                break

    # Label color: prefer white or light color on dark bg, dark on light bg
    if bg_luminance < 128:
        suggested_label = [255, 255, 255]
        for ac in accent_colors:
            if ac["lum"] > 180:
                suggested_label = ac["rgb"]
                break
    else:
        suggested_label = [30, 30, 30]
        for ac in accent_colors:
            if ac["lum"] < 80:
                suggested_label = ac["rgb"]
                break

    return {
        "background": {
            "rgb": bg_color,
            "hex": "#{:02X}{:02X}{:02X}".format(*bg_color),
            "description": "Suggested background — shown when card image cannot render",
            "note": "Based on dominant card background color"
        },
        "foreground": {
            "rgb": suggested_fg,
            "hex": "#{:02X}{:02X}{:02X}".format(*suggested_fg),
            "description": "Suggested foreground — for last 4 PAN digits and variable values",
            "note": "Chosen for contrast against the background color"
        },
        "label": {
            "rgb": suggested_label,
            "hex": "#{:02X}{:02X}{:02X}".format(*suggested_label),
            "description": "Suggested label color — for static labels on the card",
            "note": "Chosen for readability against the background color"
        },
        "dominant_colors": dominant_colors,
    }


def _load_font(size, bold=False):
    """Try to load a system font at the given size. Returns ImageFont."""
    # Bold font paths (try these first when bold=True)
    bold_fonts = [
        "/System/Library/Fonts/Supplemental/Arial Bold.ttf",
        "/System/Library/Fonts/Helvetica Bold.ttc",
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
    ]
    regular_fonts = [
        "/System/Library/Fonts/Supplemental/Arial.ttf",
        "/System/Library/Fonts/Helvetica.ttc",
        "/System/Library/Fonts/SFNSText.ttf",
        "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
    ]
    candidates = (bold_fonts + regular_fonts) if bold else (regular_fonts + bold_fonts)
    for font_name in candidates:
        if os.path.exists(font_name):
            try:
                return ImageFont.truetype(font_name, size)
            except Exception:
                continue
    return ImageFont.load_default()


def _draw_dashed_rect(draw, rect, color, width=2, dash_len=16, gap_len=10):
    """Draw a dashed rectangle on an ImageDraw surface."""
    x0, y0, x1, y1 = rect
    # Draw four sides as dashed lines
    for start, end, horizontal in [
        ((x0, y0), (x1, y0), True),   # top
        ((x1, y0), (x1, y1), False),  # right
        ((x1, y1), (x0, y1), True),   # bottom
        ((x0, y1), (x0, y0), False),  # left
    ]:
        if horizontal:
            length = abs(end[0] - start[0])
            step = 1 if end[0] >= start[0] else -1
            pos = 0
            while pos < length:
                seg_end = min(pos + dash_len, length)
                sx = start[0] + pos * step
                ex = start[0] + seg_end * step
                draw.line([(sx, start[1]), (ex, start[1])], fill=color, width=width)
                pos += dash_len + gap_len
        else:
            length = abs(end[1] - start[1])
            step = 1 if end[1] >= start[1] else -1
            pos = 0
            while pos < length:
                seg_end = min(pos + dash_len, length)
                sy = start[1] + pos * step
                ey = start[1] + seg_end * step
                draw.line([(start[0], sy), (start[0], ey)], fill=color, width=width)
                pos += dash_len + gap_len


def generate_output_image(img, colors, output_path):
    """
    Generate an output image showing:
    - The card art with a red dashed 56px quiet zone drawn INSIDE the card
    - A sample last-4 PAN in the suggested foreground color
    - RGB color values displayed to the right of the card, each label colored
      to match the color it describes
    """
    card_w, card_h = img.size
    quiet_zone = VISA_MARK_EDGE_MARGIN  # 56px

    bg_rgb = tuple(colors["background"]["rgb"])
    fg_rgb = tuple(colors["foreground"]["rgb"])
    label_rgb = tuple(colors["label"]["rgb"])

    # Canvas layout — card on the left, color panel on the right
    padding = 50
    right_panel_w = 600
    canvas_w = padding + card_w + padding + right_panel_w + padding
    canvas_h = padding + card_h + padding

    # Canvas background: a soft tint of the card's background color
    bg_lum = 0.299 * bg_rgb[0] + 0.587 * bg_rgb[1] + 0.114 * bg_rgb[2]
    if bg_lum < 128:
        canvas_bg = tuple(min(255, c + 80) for c in bg_rgb)
    else:
        canvas_bg = tuple(max(0, c - 40) for c in bg_rgb)

    canvas = Image.new("RGB", (canvas_w, canvas_h), canvas_bg)
    draw = ImageDraw.Draw(canvas)

    # Paste the card art (no extra borders)
    card_x = padding
    card_y = padding
    card_rgb = img.convert("RGB")
    canvas.paste(card_rgb, (card_x, card_y))

    # Draw the 56px quiet zone as a red dashed rectangle INSIDE the card
    quiet_rect = [
        card_x + quiet_zone,
        card_y + quiet_zone,
        card_x + card_w - quiet_zone,
        card_y + card_h - quiet_zone,
    ]
    _draw_dashed_rect(draw, quiet_rect, color=(255, 0, 0), width=3, dash_len=18, gap_len=12)

    # Overlay sample PAN "•••• 6789" in the bottom-left of the card
    font_pan = _load_font(88, bold=True)
    pan_text = "•••• 6789"
    pan_x = card_x + quiet_zone + 10
    pan_y = card_y + card_h - quiet_zone - 110
    draw.text((pan_x, pan_y), pan_text, fill=fg_rgb, font=font_pan)

    # --- Right panel: color labels ---
    # Each line: "Background color:  [swatch]  R,G,B"
    # Text color matches the color being described
    font_panel = _load_font(36, bold=True)
    swatch_size = 40
    line_spacing = 90
    num_entries = 3
    total_panel_height = num_entries * line_spacing - (line_spacing - 40)  # height of all 3 rows
    panel_x = card_x + card_w + padding + 10
    panel_y = card_y + (card_h - total_panel_height) // 2  # vertically centered

    color_entries = [
        ("Background color:", bg_rgb),
        ("Foreground color:", fg_rgb),
        ("Label color:", label_rgb),
    ]

    for i, (label_text, rgb_val) in enumerate(color_entries):
        y = panel_y + i * line_spacing
        text_color = rgb_val  # label text matches the color it describes

        # Ensure the text is readable against the canvas background
        # If contrast is too low, add a slight outline effect
        text_lum = 0.299 * rgb_val[0] + 0.587 * rgb_val[1] + 0.114 * rgb_val[2]
        canvas_lum = 0.299 * canvas_bg[0] + 0.587 * canvas_bg[1] + 0.114 * canvas_bg[2]
        contrast = abs(text_lum - canvas_lum)
        if contrast < 50:
            # Low contrast — draw a subtle outline for readability
            outline_color = (0, 0, 0) if canvas_lum > 128 else (255, 255, 255)
            for dx, dy in [(-1, -1), (-1, 1), (1, -1), (1, 1)]:
                draw.text((panel_x + dx, y + dy), label_text, fill=outline_color, font=font_panel)

        # Draw label text
        draw.text((panel_x, y), label_text, fill=text_color, font=font_panel)

        # Measure label width to position swatch after it
        bbox = draw.textbbox((panel_x, y), label_text, font=font_panel)
        label_end_x = bbox[2] + 16

        # Draw color swatch
        swatch_y = y + 4
        draw.rectangle(
            [label_end_x, swatch_y, label_end_x + swatch_size, swatch_y + swatch_size],
            fill=rgb_val, outline=None
        )

        # Draw RGB value text
        rgb_text = f"  {rgb_val[0]},{rgb_val[1]},{rgb_val[2]}"
        value_x = label_end_x + swatch_size + 4
        if contrast < 50:
            for dx, dy in [(-1, -1), (-1, 1), (1, -1), (1, 1)]:
                draw.text((value_x + dx, y + dy), rgb_text, fill=outline_color, font=font_panel)
        draw.text((value_x, y), rgb_text, fill=text_color, font=font_panel)

    # Save
    canvas.save(output_path, "PNG")
    return output_path


def check_image(image_path: str, output_dir: str = None) -> dict:
    results = {
        "file": os.path.basename(image_path),
        "checks": {},
        "colors": {},
        "output_image": None,
        "errors": []
    }

    try:
        img = Image.open(image_path)
    except Exception as e:
        results["errors"].append(f"Could not open image: {e}")
        return results

    # --- Dimensions ---
    w, h = img.size
    results["checks"]["dimensions"] = {
        "passed": w == REQUIRED_WIDTH and h == REQUIRED_HEIGHT,
        "actual": f"{w}x{h}",
        "required": f"{REQUIRED_WIDTH}x{REQUIRED_HEIGHT}",
        "note": "" if (w == REQUIRED_WIDTH and h == REQUIRED_HEIGHT) else f"Image is {w}x{h}, expected {REQUIRED_WIDTH}x{REQUIRED_HEIGHT}"
    }

    # --- File Format ---
    fmt = img.format or os.path.splitext(image_path)[1].lstrip(".").upper()
    results["checks"]["file_format"] = {
        "passed": fmt == REQUIRED_FORMAT,
        "actual": fmt,
        "required": REQUIRED_FORMAT,
        "note": "" if fmt == REQUIRED_FORMAT else f"File format is {fmt}, expected {REQUIRED_FORMAT}"
    }

    # --- DPI (calculated from image resolution, not metadata) ---
    calculated_dpi = round(w / CARD_WIDTH_INCHES, 1)
    dpi_ok = calculated_dpi >= MIN_DPI_DIGITAL
    results["checks"]["dpi"] = {
        "passed": dpi_ok,
        "actual": f"{calculated_dpi} DPI (calculated)",
        "required": f">= {MIN_DPI_DIGITAL} DPI for digital display (Visa spec)",
        "note": (
            f"Calculated from image width: {w}px ÷ {CARD_WIDTH_INCHES}\" = {calculated_dpi} DPI. "
            + ("Meets Visa digital display requirement." if dpi_ok
               else f"Below Visa minimum of {MIN_DPI_DIGITAL} DPI. A wider source image is needed.")
        )
    }

    # --- Color Extraction ---
    try:
        colors = extract_colors(img)
        results["colors"] = colors
    except Exception as e:
        results["errors"].append(f"Color extraction failed: {e}")
        colors = None

    # --- Generate Output Image ---
    if colors:
        try:
            if output_dir:
                os.makedirs(output_dir, exist_ok=True)
                out_dir = output_dir
            else:
                out_dir = os.path.dirname(os.path.abspath(image_path))

            base_name = os.path.splitext(os.path.basename(image_path))[0]
            output_path = os.path.join(out_dir, f"{base_name}_review.png")
            generate_output_image(img, colors, output_path)
            results["output_image"] = output_path
        except Exception as e:
            results["errors"].append(f"Output image generation failed: {e}")

    return results


def main():
    parser = argparse.ArgumentParser(description="Check virtual card art technical specs")
    parser.add_argument("image_path", help="Path to the card art image")
    parser.add_argument("--output-dir", help="Directory to save the output review image", default=None)
    args = parser.parse_args()

    result = check_image(args.image_path, args.output_dir)
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
