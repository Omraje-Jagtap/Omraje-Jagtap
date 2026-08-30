#!/usr/bin/env python3
"""animate_photo.py — embed a real photo in a circular frame with an
animated rotating ring, as a single self-contained SVG for a GitHub README.

Unlike dotify.py, this does NOT stylize the photo — the actual image is
embedded as-is (center-cropped to a square, clipped to a circle). Only the
decorative ring around it is animated, using SVG's native SMIL animation
(the same mechanism behind animated "typing" banners), so it plays
correctly wherever GitHub renders the README.

Usage:
    python animate_photo.py <input_photo> -o <output_svg> [--size 320]
        [--ring-color '#39D353'] [--ring-color-2 '#1F6FEB'] [--duration 4]
"""
import argparse
import base64
import io
from PIL import Image


def build_svg(photo: Image.Image, size: int, ring_color: str, ring_color_2: str, duration: float) -> str:
    photo = photo.convert("RGB")
    w, h = photo.size
    side = min(w, h)
    # Center-crop to a square, biased toward the top third (typical
    # headshot framing keeps the face there rather than dead-center).
    left = (w - side) // 2
    top = max(0, (h - side) // 3)
    photo = photo.crop((left, top, left + side, top + side))
    photo = photo.resize((640, 640), Image.Resampling.LANCZOS)

    buf = io.BytesIO()
    photo.save(buf, format="JPEG", quality=90)
    b64 = base64.b64encode(buf.getvalue()).decode("ascii")

    c = size / 2
    photo_r = size * 0.42
    ring_r = size * 0.47

    return f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {size} {size}" width="{size}" height="{size}">
  <defs>
    <clipPath id="photoClip">
      <circle cx="{c}" cy="{c}" r="{photo_r}"/>
    </clipPath>
  </defs>

  <!-- static outer track -->
  <circle cx="{c}" cy="{c}" r="{ring_r}" fill="none" stroke="currentColor" stroke-opacity="0.15" stroke-width="3"/>

  <!-- animated sweeping arc -->
  <g>
    <circle cx="{c}" cy="{c}" r="{ring_r}" fill="none"
            stroke="{ring_color}" stroke-width="3.5" stroke-linecap="round"
            stroke-dasharray="{2 * 3.14159 * ring_r * 0.22} {2 * 3.14159 * ring_r}">
      <animateTransform attributeName="transform" type="rotate"
                         from="0 {c} {c}" to="360 {c} {c}"
                         dur="{duration}s" repeatCount="indefinite"/>
      <animate attributeName="stroke" values="{ring_color};{ring_color_2};{ring_color}"
               dur="{duration * 2}s" repeatCount="indefinite"/>
    </circle>
  </g>

  <!-- the actual photo, unmodified, clipped to a circle -->
  <image href="data:image/jpeg;base64,{b64}" x="{c - photo_r}" y="{c - photo_r}"
         width="{photo_r * 2}" height="{photo_r * 2}" clip-path="url(#photoClip)"
         preserveAspectRatio="xMidYMid slice"/>
</svg>'''


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("input", help="source photo (jpg/png)")
    ap.add_argument("-o", "--output", required=True, help="output .svg path")
    ap.add_argument("--size", type=int, default=320, help="SVG canvas size in px (default: 320)")
    ap.add_argument("--ring-color", default="#39D353", help="primary ring color (default: GitHub green)")
    ap.add_argument("--ring-color-2", default="#1F6FEB", help="secondary ring color it cycles to")
    ap.add_argument("--duration", type=float, default=4.0, help="seconds per full ring rotation")
    args = ap.parse_args()

    photo = Image.open(args.input)
    svg = build_svg(photo, args.size, args.ring_color, args.ring_color_2, args.duration)

    with open(args.output, "w") as f:
        f.write(svg)
    print(f"wrote {args.output}")


if __name__ == "__main__":
    main()
