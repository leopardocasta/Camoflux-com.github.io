#!/usr/bin/env python3
"""Camoflux image exporter.

Reads sources from images_src/ and writes web-ready files to images/.

  Screenshots (any .png / .jpg except logo.png) get three variants:
    <name>.jpg          1920 wide, q85   hero and full-width use
    <name>-sm.jpg        960 wide, q82   cards, grids, mobile
    <name>-master.jpg   native width, q92 press kit downloads

  logo.png (white wordmark on transparency) becomes:
    logo.png            1760 wide, trimmed   hero use (2x of 880px display)
    logo-header.png       28 px tall, trimmed  header/footer (2x of 14px display)
    logo-white.png      native, trimmed      press kit download (for dark backgrounds)
    logo-black.png      native, trimmed      press kit download (for light backgrounds)

  Derived: og.jpg (1200x630 share card), favicon-{16,32,180,512}.png

Usage: python3 export_images.py
"""
from pathlib import Path
from PIL import Image, ImageDraw, ImageOps
import json

ROOT = Path(__file__).parent
SRC = ROOT / "images_src"
OUT = ROOT / "images"
OUT.mkdir(exist_ok=True)

OG_SOURCE = "hero-3d-still"   # which screenshot backs the social share card
BG = (10, 11, 13)               # --c-bg
ACCENT = (216, 255, 58)         # --c-accent

VARIANTS = [
    ("", 1920, 85),
    ("-sm", 960, 82),
    ("-master", None, 92),       # None = keep native width
]


def save_jpg(img, path, q):
    img.save(path, "JPEG", quality=q, optimize=True, progressive=True)


def resize_w(img, w):
    if w is None or img.width <= w:
        return img
    return img.resize((w, round(img.height * w / img.width)), Image.LANCZOS)


manifest = {}

# ---- Screenshots ----
for src in sorted([*SRC.glob("*.png"), *SRC.glob("*.jpg"), *SRC.glob("*.jpeg")]):
    if src.stem in ("logo", "favicon-source"):
        continue
    img = Image.open(src).convert("RGB")
    entry = {"width": img.width, "height": img.height}
    print(f"{src.name}  {img.width}x{img.height}")
    # Press kit masters are only needed for game screenshots; artwork and photos get web sizes only.
    web_only = src.stem.startswith(("paint-", "draw-", "whitney-", "hero-", "supercon-"))
    for suffix, w, q in VARIANTS:
        if web_only and suffix == "-master":
            continue
        out = OUT / f"{src.stem}{suffix}.jpg"
        v = resize_w(img, w)
        save_jpg(v, out, q)
        print(f"  {out.name:32s} {v.width}x{v.height}  {out.stat().st_size/1024:.0f} KB")
    if not web_only:
        master = Image.open(OUT / f"{src.stem}-master.jpg")
        entry["master_width"], entry["master_height"] = master.size
    manifest[src.stem] = entry

# ---- Logo ----
logo_src = SRC / "logo.png"
if logo_src.exists():
    logo = Image.open(logo_src).convert("RGBA")
    logo = logo.crop(logo.getchannel("A").getbbox())
    logo.save(OUT / "logo-white.png", optimize=True)
    black = Image.new("RGBA", logo.size, (0, 0, 0, 255))
    black.putalpha(logo.getchannel("A"))
    black.save(OUT / "logo-black.png", optimize=True)
    resize_w(logo, 1760).save(OUT / "logo.png", optimize=True)
    h = 28
    logo.resize((round(logo.width * h / logo.height), h), Image.LANCZOS).save(OUT / "logo-header.png", optimize=True)
    manifest["logo"] = {"width": logo.width, "height": logo.height, "ratio": logo.width / logo.height}
    print(f"logo.png  trimmed to {logo.width}x{logo.height}, ratio {logo.width/logo.height:.2f}")

# ---- OG share card: screenshot + gradient + logo ----
og_src = next(SRC.glob(f"{OG_SOURCE}.*"), None)
if og_src:
    base = ImageOps.fit(Image.open(og_src).convert("RGB"), (1200, 630), Image.LANCZOS)
    shade = Image.new("RGBA", (1200, 630))
    d = ImageDraw.Draw(shade)
    for y in range(630):
        d.line([(0, y), (1200, y)], fill=(*BG, int(90 + 140 * (y / 630) ** 1.4)))
    og = Image.alpha_composite(base.convert("RGBA"), shade)
    if logo_src.exists():
        lw = 840
        lg = logo.resize((lw, round(logo.height * lw / logo.width)), Image.LANCZOS)
        og.alpha_composite(lg, ((1200 - lw) // 2, 630 - lg.height - 96))
    save_jpg(og.convert("RGB"), OUT / "og.jpg", 88)
    print("og.jpg  1200x630")

# ---- Favicons: the game's joystick plate icon on black (falls back to an accent dot) ----
fav_src = SRC / "favicon-source.png"
if fav_src.exists():
    icon = Image.open(fav_src).convert("RGBA")
    fav = Image.new("RGBA", (512, 512), (0, 0, 0, 255))
    icon = icon.resize((472, 472), Image.LANCZOS); fav.alpha_composite(icon, (20, 20))
else:
    fav = Image.new("RGBA", (512, 512), (*BG, 255))
    ImageDraw.Draw(fav).ellipse([116, 116, 396, 396], fill=(*ACCENT, 255))
for s in (512, 180, 32, 16):
    fav.resize((s, s), Image.LANCZOS).save(OUT / f"favicon-{s}.png", optimize=True)
print("favicons 16/32/180/512")

(OUT / "manifest.json").write_text(json.dumps(manifest, indent=2))
total = sum(f.stat().st_size for f in OUT.iterdir())
print(f"\nimages/ = {total/1024/1024:.2f} MB")
