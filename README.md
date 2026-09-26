# Camoflux site

Static site for Camoflux: Levels & Bosses. Content lives in one file, styling in one design system, and the build checks its own output.

## Workflow

```bash
python3 export_images.py   # after adding or changing anything in images_src/
python3 build.py           # after any content change; regenerates site/ and lints it
```

Deploy the contents of `site/` to any static host.

`build.py` also writes `preview/`: the same pages with the stylesheet, script, and images embedded, so each file opens correctly on its own (in a chat preview, an email attachment, or double-clicked from a download). They are 1 to 4 MB each, so use them for review only. Pages in `site/` load their styles and images from the folders beside them; opened alone, they render as a plain white page.

## Folder structure

```
content.py          all copy, links, images, devlog, exhibitions, merch
build.py            page templates built from small components, plus lint
export_images.py    images_src/ to images/ (3 sizes, logo variants, OG card, favicons)
assets/site.css     design system: tokens first, then components
assets/site.js      lazy images with skeletons, trailer modal, menu, carousels, form states
images_src/         original files, keep for re-export
images/             generated
site/               generated, deploy this
```

## Design system (assets/site.css)

Every value in the stylesheet references a token defined at the top.

| Token group | Values |
| --- | --- |
| Color | bg, surface, surface-2, line, line-strong, text (3 levels), accent #d8ff3a |
| Type scale | 11 meta, 13 small, 16 body, 20 lead, 22 h3, 28 to 40 h2, 36 to 56 h1, 40 to 80 display (hero only) |
| Weights | 400 and 500 only |
| Line height | 1.05 headings, 1.35 h3 and quotes, 1.6 all running text |
| Spacing | 4px base: 4, 8, 12, 16, 24, 32, 48, 64, 96, 128 |
| Radius | 0 (surfaces, media, buttons), 2px (badges, inputs), round (dots, circular controls) |
| Motion | ease-out cubic-bezier(0.2, 0.6, 0.2, 1), 160 / 280 / 700ms, 90ms stagger, 3px max lift |

Rules:

- Chartreuse is the only accent. It marks actions and current state, nothing decorative.
- Motion: one entrance sequence on the homepage hero. Everything else animates only in response to the visitor (hover, open, load).
- Links that leave the site open in a new tab and carry ↗. Internal links carry no arrow.
- Numbered markers appear only on real sequences (the water arc: páramo, igapó, mangrove).

## What the build enforces

`build.py` fails if any page has an em dash, an empty or `#` link, an image without alt text, a missing image or asset, a link to a page that does not exist, or an inline style outside the allowed set. A link whose URL is `None` in content.py is simply not rendered, so placeholders never ship as dead buttons.

## Common edits

- **Release date:** `SITE["release"]`
- **Hero video loop:** put an MP4 in `site/video/` (or add a copy step) and set `SITE["hero_video"]`
- **Mailchimp signup:** configured in `SITE["mailchimp"]` from your embed code. It appears above the footer on every page and submits in place, showing submitting, success, and error states with Mailchimp's own message. Without JavaScript it falls back to a normal Mailchimp form in a new tab.
- **Devlog post:** add a dict to the top of `DEVLOG`; `"draft": True` keeps it out of the build
- **Merch item for sale:** set `status` to `"available"`, plus `price` and `url`; available items also appear on the homepage
- **New image:** drop the file in `images_src/`, run `export_images.py`, add a caption and alt text to `IMAGES`

Search content.py for `# CONFIRM` to find every placeholder or unverified value.

## Void Signal (current direction)

- **Ground:** the inverted 2012 Void Construction ink drawing tiles behind every page (`assets/ui/ground-ink.jpg`); all content sits on black panels. Every overlay is pure black.
- **Type:** Technical Standard VP for headings (self-hosted from `assets/fonts/`; needs a web license), Inter for reading, Inter Italic for press quotes, AB-24h for metadata. AB-24h comes from Adobe Fonts: set `SITE["fonts"]["adobe_kit_id"]` to your web project's kit ID. Until then Share Tech Mono stands in. The build marks accented letters so AB-24h's missing á, ó, í are set in Technical Standard at matching height.
- **3D hero:** `assets/hero3d.js` renders the model named in `SITE["hero3d"]` in front of a curved screen of in-game frames (`assets/3d/frames/`). Set `SITE["hero_video"]` to an MP4 gameplay clip to play video on that screen instead. three.js loads after the page, from jsDelivr, and is skipped with reduced motion, data saver, or no WebGL; the poster `images/hero-3d-still.jpg` shows instead.
- **Swapping the hero model:** convert FBX with FBX2glTF, compress with `gltf-transform meshopt`, drop the `.glb` in `assets/3d/`, and set `SITE["hero3d"]["model"]`.
- **Artwork:** paintings, drawings, and installation photos live in `ARTWORK` in content.py (with photo credits) and appear on `studio.html`, the homepage sketchbook, and the Exhibitions page. They are not part of the press kit screenshots.
