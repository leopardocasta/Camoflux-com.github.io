# Camoflux site — production bundle

## Folder structure

```
camoflux-site/
├── README.md
├── content.py           ← single source of truth for all content
├── build.py             ← run this to regenerate HTML
├── export_images.py     ← run this to (re-)generate image variants
├── images_src/          ← original PNGs (not deployed; keep for re-export)
│   ├── cavern.png       ← 1920×1080 source
│   ├── igapo.png
│   └── mangrove.png
├── images/              ← exported JPG variants + favicons + OG
│   ├── cavern.jpg          ← 1920w main hero/feature
│   ├── cavern-sm.jpg       ← 960w for cards & mobile
│   ├── cavern-master.jpg   ← 1920w q92, press kit downloads
│   ├── igapo.jpg / -sm / -master
│   ├── mangrove.jpg / -sm / -master
│   ├── og.jpg              ← 1200×630 social sharing
│   ├── trailer-thumb.jpg   ← 1280×720 local trailer fallback
│   └── favicon-{16,32,180,512}.png
└── site/                ← deploy this folder
    ├── index.html
    ├── presskit.html
    ├── exhibition.html
    ├── devlog.html
    ├── devlog-*.html
    ├── merch.html
    ├── mobile.html
    └── images/          ← auto-copied by build.py from ../images/
```

## Workflow

```bash
# First-time setup or after adding new source images:
python3 export_images.py    # exports PNGs → JPG variants + favicons + OG

# Any content change:
python3 build.py            # regenerates site/ HTML + syncs images
```

## File size breakdown

```
HTML total:            ~210 KB  (10 pages combined)
Images dir total:      ~2.3 MB
  cavern.jpg            290 KB  main hero
  cavern-sm.jpg          84 KB  card variant
  cavern-master.jpg     400 KB  press kit master
  (igapo, mangrove similar)
  og.jpg                 78 KB  social sharing card
  trailer-thumb.jpg     150 KB  local trailer fallback
  favicons             total < 10 KB
```

Compared to the inlined-base64 previews (1–2 MB per HTML file), this is **~100× lighter per page**, and the browser only loads images visible to the user.

## How images are wired in

Each image has three variants:

| Variant | Width | Quality | Use case | Approx size |
| --- | --- | --- | --- | --- |
| `name.jpg` | 1920 | 85 | Hero, full-bleed, exhibition page | 200-350 KB |
| `name-sm.jpg` | 960 | 82 | Feature cards, devlog index, merch grid, mobile | 65-95 KB |
| `name-master.jpg` | 1920 | 92 | Press kit downloads (high quality) | 280-500 KB |

In `build.py`:

```python
img("cavern")            # → "images/cavern.jpg"
img("cavern", "small")   # → "images/cavern-sm.jpg"
img("cavern", "master")  # → "images/cavern-master.jpg"

IMAGES['cavern']         # main version (shorthand)
IMAGES_SM['cavern']      # small version (shorthand)
```

Hero contexts use `IMAGES[…]`. Card/grid contexts use `IMAGES_SM[…]`.

## Adding a new image

1. Drop the source PNG into `images_src/` (e.g. `images_src/cavern2.png`)
2. Re-run the image-export step (see `export_images.py` below — or run the snippet manually)
3. Reference it in `content.py`: `"image": "cavern2"`
4. Run `python3 build.py`

## Image export snippet

```python
from PIL import Image
import os

configs = {
    'main':   {'width': 1920, 'quality': 85, 'suffix': ''},
    'small':  {'width': 960,  'quality': 82, 'suffix': '-sm'},
    'master': {'width': 1920, 'quality': 92, 'suffix': '-master'},
}
for name in ['cavern', 'igapo', 'mangrove']:  # add new keys here
    src = Image.open(f'images_src/{name}.png').convert('RGB')
    sw, sh = src.size
    for cfg in configs.values():
        w = cfg['width']
        h = int(sh * w / sw)
        img = src.resize((w, h), Image.LANCZOS) if w != sw else src
        out = f'images/{name}{cfg["suffix"]}.jpg'
        img.save(out, 'JPEG', quality=cfg['quality'], optimize=True, progressive=True)
```

## Deploying

1. Run `python3 build.py`
2. Copy `images/` into `site/images/` (or symlink during dev)
3. Upload the contents of `site/` to your web host

Works on any static host — Netlify, Vercel, Cloudflare Pages, GitHub Pages, S3, plain Apache/nginx. No build step required server-side.

## Further optimization (when ready)

- **WebP**: emit `.webp` alongside `.jpg`, use `<picture>` tags. ~30% smaller for equivalent quality. Browser support is now universal.
- **AVIF**: even better compression than WebP, ~95% browser support. Worth adding as a third format.
- **Lazy load**: convert CSS `background-image` to `<img loading="lazy">` for non-hero images. Major bandwidth savings on long-scroll pages like the press kit screenshot grid.
- **CDN**: serve images through Cloudflare or similar. Free tier handles this site comfortably.
- **Preconnect**: already added for fonts.googleapis.com; consider adding for img.youtube.com if you keep the trailer thumbnail remote.

## Content updates

See workflow in earlier README — edit `content.py`, run `python3 build.py`. The image references and file sizes all stay consistent automatically.
