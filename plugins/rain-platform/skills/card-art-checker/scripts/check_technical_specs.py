#!/usr/bin/env python3
"""
Technical spec checker for Visa digital card art.
Checks dimensions, format, color mode, and DPI.
Also extracts dominant background, foreground, and label colors.

Usage:
    python3 check_technical_specs.py <image_path>

Outputs JSON with technical check results and extracted colors.
"""

import sys
import json
import os

try:
    from PIL import Image
    import numpy as np
except ImportError:
    import subprocess
    subprocess.check_call([sys.executable, "-m", "pip", "install", "Pillow", "numpy", "--break-system-packages", "-q"])
    from PIL import Image
    import numpy as np


REQUIRED_WIDTH = 1536
REQUIRED_HEIGHT = 969
REQUIRED_FORMAT = "PNG"
REQUIRED_MODE = "RGB"
REQUIRED_DPI = 72
VISA_MARK_EDGE_MARGIN = 56  # pixels


def check_image(image_path: str) -> dict:
    results = {
        "file": os.path.basename(image_path),
        "checks": {},
        "colors": {},
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

    # --- Color Mode ---
    mode = img.mode
    # RGBA is technically not RGB - flag it but note it
    mode_ok = mode == REQUIRED_MODE
    results["checks"]["color_mode"] = {
        "passed": mode_ok,
        "actual": mode,
        "required": REQUIRED_MODE,
        "note": "" if mode_ok else f"Color mode is {mode}, expected {REQUIRED_MODE}. If RGBA, ensure transparency is intentional."
    }

    # --- DPI ---
    dpi_info = img.info.get("dpi", None)
    if dpi_info:
        dpi_x, dpi_y = dpi_info
        dpi_ok = (abs(dpi_x - REQUIRED_DPI) <= 1) and (abs(dpi_y - REQUIRED_DPI) <= 1)
        results["checks"]["dpi"] = {
            "passed": dpi_ok,
            "actual": f"{dpi_x:.0f}x{dpi_y:.0f}",
            "required": str(REQUIRED_DPI),
            "note": "" if dpi_ok else f"DPI is {dpi_x:.0f}x{dpi_y:.0f}, expected {REQUIRED_DPI}"
        }
    else:
        results["checks"]["dpi"] = {
            "passed": None,
            "actual": "not embedded",
            "required": str(REQUIRED_DPI),
            "note": "DPI metadata not embedded in file. Verify DPI is set to 72 in your design tool before exporting."
        }

    # --- Color Extraction ---
    # Convert to RGB for analysis if needed
    try:
        rgb_img = img.convert("RGB")
        arr = np.array(rgb_img)

        # Background color: sample corners (avoid logo areas)
        corner_size = 40
        corners = [
            arr[:corner_size, :corner_size],          # top-left
            arr[:corner_size, -corner_size:],          # top-right
            arr[-corner_size:, :corner_size],          # bottom-left
            arr[-corner_size:, -corner_size:],         # bottom-right
        ]
        corner_pixels = np.concatenate([c.reshape(-1, 3) for c in corners], axis=0)
        bg_color = corner_pixels.mean(axis=0).astype(int).tolist()

        # Get unique colors across the entire image using k-means approximation (top N colors)
        # Simplified: sample a grid of pixels
        sample = arr[::8, ::8].reshape(-1, 3)

        # Most dominant color (roughly the background)
        from collections import Counter
        # Quantize to reduce colors
        quantized = (sample // 16) * 16
        counts = Counter(map(tuple, quantized.tolist()))
        most_common = counts.most_common(5)

        dominant_colors = [{"rgb": list(color), "hex": "#{:02X}{:02X}{:02X}".format(*color), "count": cnt}
                           for color, cnt in most_common]

        results["colors"]["background"] = {
            "rgb": bg_color,
            "hex": "#{:02X}{:02X}{:02X}".format(*bg_color),
            "description": "Sampled from image corners — used when card image cannot render",
            "note": "Verify this matches your intended card background color"
        }

        results["colors"]["dominant_colors"] = dominant_colors

        # Foreground/label color suggestion: use contrasting color to background
        bg_luminance = 0.299 * bg_color[0] + 0.587 * bg_color[1] + 0.114 * bg_color[2]
        if bg_luminance > 128:
            suggested_fg = [30, 30, 30]    # dark text on light background
        else:
            suggested_fg = [255, 255, 255] # white text on dark background

        results["colors"]["foreground_suggestion"] = {
            "rgb": suggested_fg,
            "hex": "#{:02X}{:02X}{:02X}".format(*suggested_fg),
            "description": "Suggested foreground color for last 4 PAN digits and variable values",
            "note": "Auto-suggested based on background luminance. Override with your design's actual text color."
        }

        results["colors"]["label_suggestion"] = {
            "rgb": suggested_fg,
            "hex": "#{:02X}{:02X}{:02X}".format(*suggested_fg),
            "description": "Suggested label color for card labels",
            "note": "Auto-suggested — override with your design's actual label color."
        }

    except Exception as e:
        results["errors"].append(f"Color extraction failed: {e}")

    return results


def main():
    if len(sys.argv) < 2:
        print("Usage: python3 check_technical_specs.py <image_path>")
        sys.exit(1)

    image_path = sys.argv[1]
    result = check_image(image_path)
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
