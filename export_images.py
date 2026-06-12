#!/usr/bin/env python3
"""Camoflux image exporter.

Reads source PNGs from images_src/, exports optimized JPGs to images/ at multiple sizes.
Re-run any time you add a new source image.

Usage: python3 export_images.py
"""
from PIL import Image, ImageDraw
from pathlib import Path
import os
import sys

ROOT = Path(__file__).parent
SRC = ROOT / 'images_src'
OUT = ROOT / 'images'
OUT.mkdir(exist_ok=True)

# Output configurations
CONFIGS = {
    'main':   {'width': 1920, 'quality': 85, 'suffix': ''},
    'small':  {'width': 960,  'quality': 82, 'suffix': '-sm'},
    'master': {'width': 1920, 'quality': 92, 'suffix': '-master'},
}

# Discover all PNGs in source
sources = sorted(SRC.glob('*.png'))
if not sources:
    print(f"No PNGs found in {SRC}. Drop source images there and re-run.")
    sys.exit(1)

print(f"Exporting {len(sources)} source image(s)...")
print()

for src_path in sources:
    name = src_path.stem
    src = Image.open(src_path).convert('RGB')
    sw, sh = src.size
    print(f"  {name}.png ({sw}×{sh})")
    for cfg_name, cfg in CONFIGS.items():
        w = cfg['width']
        h = int(sh * w / sw)
        img = src.resize((w, h), Image.LANCZOS) if w != sw else src
        out_path = OUT / f'{name}{cfg["suffix"]}.jpg'
        img.save(out_path, 'JPEG', quality=cfg['quality'], optimize=True, progressive=True)
        sz = os.path.getsize(out_path)
        print(f'    → {out_path.name}  ({img.size[0]}×{img.size[1]}, {sz/1024:.0f} KB)')
    print()

# --- Generate derived assets ---
# OG image: use the first source image, crop to 1200×630, add dark gradient
if sources:
    print("Building derived assets...")
    src = Image.open(sources[0]).convert('RGB')
    target_ratio = 1200 / 630
    sw, sh = src.size
    src_ratio = sw / sh
    if src_ratio > target_ratio:
        new_w = int(sh * target_ratio)
        left = (sw - new_w) // 2
        src = src.crop((left, 0, left + new_w, sh))
    else:
        new_h = int(sw / target_ratio)
        top = (sh - new_h) // 2
        src = src.crop((0, top, sw, top + new_h))
    og = src.resize((1200, 630), Image.LANCZOS)

    overlay = Image.new('RGBA', (1200, 630), (10, 11, 13, 0))
    draw = ImageDraw.Draw(overlay)
    for y in range(630):
        alpha = int(180 * (y / 630) ** 1.5) + 80
        draw.line([(0, y), (1200, y)], fill=(10, 11, 13, min(alpha, 230)))
    og_final = Image.alpha_composite(og.convert('RGBA'), overlay).convert('RGB')
    og_final.save(OUT / 'og.jpg', 'JPEG', quality=88, optimize=True, progressive=True)
    sz = os.path.getsize(OUT / 'og.jpg')
    print(f'  → og.jpg  (1200×630, {sz/1024:.0f} KB)')

# Favicon: chartreuse dot on near-black
fav = Image.new('RGBA', (512, 512), (10, 11, 13, 255))
draw = ImageDraw.Draw(fav)
cx, cy, r = 256, 256, 140
draw.ellipse([cx-r, cy-r, cx+r, cy+r], fill=(216, 255, 58, 255))
fav.save(OUT / 'favicon-512.png', 'PNG', optimize=True)
for s in [180, 32, 16]:
    f = fav.resize((s, s), Image.LANCZOS)
    f.save(OUT / f'favicon-{s}.png', 'PNG', optimize=True)
print(f'  → favicons (16, 32, 180, 512)')

# Trailer thumbnail fallback (uses first source image as stand-in)
if sources:
    yt = Image.open(sources[0]).convert('RGB')
    yt_resized = yt.resize((1280, 720), Image.LANCZOS)
    yt_resized.save(OUT / 'trailer-thumb.jpg', 'JPEG', quality=85, optimize=True, progressive=True)
    sz = os.path.getsize(OUT / 'trailer-thumb.jpg')
    print(f'  → trailer-thumb.jpg  (1280×720, {sz/1024:.0f} KB)')

print()
total = sum(f.stat().st_size for f in OUT.iterdir() if f.is_file())
print(f"Done. {OUT} = {total/1024/1024:.2f} MB total.")
