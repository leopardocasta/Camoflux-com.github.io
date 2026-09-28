#!/usr/bin/env python3
"""Camoflux site builder.

  python3 export_images.py   # once, or after adding source images
  python3 build.py           # regenerates site/ and lints it

Markup is composed from small component functions. All styling lives in
assets/site.css (tokens first). No inline styles are emitted.
"""
import html
import json
import re
import shutil
import sys
import zipfile
from datetime import date
from pathlib import Path

ROOT = Path(__file__).parent
sys.path.insert(0, str(ROOT))
from content import (SITE, NAV, IMAGES, WORLD, FEATURES, PRESS_FEATURED, PRESS_SHORT,
                     RECOGNITION, EXHIBITIONS, DEVLOG, STUDIO, MERCH, MERCH_NOTE, SOCIAL,
                     ARTWORK, PAINTINGS, SKETCHBOOK, GAMEPLAY, COVERAGE)
ALL_IMAGES = {**IMAGES, **ARTWORK}
GAME_IMAGES = {k: v for k, v in IMAGES.items() if v.get('kind') == 'game'}
import json as _json

IMG_DIR = ROOT / "images"
OUT = ROOT / "site"
ERRORS = []

def e(s):
    return html.escape(str(s), quote=True)

def fmt_date(iso):
    d = date.fromisoformat(iso)
    return f"{d.strftime('%B')} {d.day}, {d.year}"

def fmt_size(n):
    return f"{n/1024/1024:.1f} MB" if n > 1024 * 1024 else f"{n/1024:.0f} KB"

MANIFEST = json.loads((IMG_DIR / "manifest.json").read_text()) if (IMG_DIR / "manifest.json").exists() else {}
LOGO_RATIO = MANIFEST.get("logo", {}).get("ratio", 17.12)

# ---------------------------------------------------------------- icons
# Sized in CSS at 1em so they scale with the text beside them.
ICON = {
    "play": '<svg class="icon" viewBox="0 0 24 24" aria-hidden="true"><path d="M7 4.5v15l13-7.5z" fill="currentColor"/></svg>',
    "menu": '<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M3 7h18M3 12h18M3 17h18" stroke="currentColor" stroke-width="1.5"/></svg>',
    "prev": '<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M15 5l-7 7 7 7" fill="none" stroke="currentColor" stroke-width="1.5"/></svg>',
    "next": '<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M9 5l7 7-7 7" fill="none" stroke="currentColor" stroke-width="1.5"/></svg>',
}

# ---------------------------------------------------------------- primitives

def link(url, label, cls="link", download=False):
    """Rules: no URL, no link. External links open in a new tab and carry ↗."""
    if not url:
        return ""
    external = url.startswith("http")
    attrs = f' class="{cls}"' if cls else ""
    if external:
        attrs += ' target="_blank" rel="noopener"'
    if download:
        attrs += " download"
    arrow = ' <span class="ext" aria-hidden="true">↗</span><span class="sr-only"> (opens in a new tab)</span>' if external else ""
    return f'<a href="{e(url)}"{attrs}>{e(label)}{arrow}</a>'

def btn(url, label, variant="primary", size="", download=False):
    cls = f"btn btn--{variant}" + (f" btn--{size}" if size else "")
    return link(url, label, cls=cls, download=download)

def acc(html_text):
    """AB-24h draws no accented letters; mark them so CSS can set them in the display face."""
    return re.sub(r"([À-ÿ])", r'<span class="acc">\1</span>', html_text)

def meta(text, tag="span", cls=""):
    return f'<{tag} class="t-meta{(" " + cls) if cls else ""}">{acc(e(text))}</{tag}>'

def img_path(key, size="sm"):
    suffix = {"sm": "-sm", "main": "", "master": "-master"}[size]
    return f"images/{key}{suffix}.jpg"

def check_image(key):
    if key not in ALL_IMAGES:
        ERRORS.append(f"image key '{key}' missing from IMAGES or ARTWORK in content.py")
    if not (IMG_DIR / f"{key}.jpg").exists():
        ERRORS.append(f"images/{key}.jpg not found; run export_images.py")

def media(key, ar="16x9", size="sm", badge="", badge_right="", src=None, alt=None, fallback=None):
    """Skeleton placeholder until the image loads (site.js), then fades in."""
    if src is None:
        check_image(key)
        src = img_path(key, size)
        alt = ALL_IMAGES.get(key, {}).get("alt", "")
    b = f'<span class="badge t-meta">{e(badge)}</span>' if badge else ""
    br = f'<span class="badge badge--right t-meta">{e(badge_right)}</span>' if badge_right else ""
    fb = f' data-fallback="{e(fallback)}"' if fallback else ""
    full = ""
    if key and key in ALL_IMAGES:   # click to open large (site.js lightbox)
        cap = ALL_IMAGES[key].get("caption", ""); cr = ALL_IMAGES[key].get("credit", "")
        full = f' data-full="{e(img_path(key, "main"))}" data-caption="{e(cap + (". " + cr if cr else ""))}"'
    return (f'<div class="media ar-{ar}" data-src="{e(src)}"{fb}{full}>{b}{br}'
            f'<div class="media__img" role="img" aria-label="{e(alt)}"></div>'
            f'<div class="media__status">{meta("Image unavailable")}</div>'
            f'<noscript><img src="{e(src)}" alt="{e(alt)}"></noscript></div>')

def frame():
    return '<div class="frame" aria-hidden="true"><i></i><i></i><i></i><i></i></div>'

def section(inner, id_="", alt=False, cls="", panel=True):
    """Every section's content sits on a black panel over the ink ground."""
    attrs = f' id="{id_}"' if id_ else ""
    classes = "section" + (" section--alt" if alt else "") + (f" {cls}" if cls else "")
    body = f'<div class="panel">{inner}</div>' if panel else inner
    return f'<section{attrs} class="{classes}"><div class="wrap">{body}</div></section>'

def split(label, inner):
    return f'<div class="split">{meta(label, "p")}<div>{inner}</div></div>'

def row_head(title, right=""):
    return f'<div class="row-head"><h2 class="t-h2">{e(title)}</h2>{right}</div>'

def prose(paragraphs):
    return '<div class="prose">' + "".join(f"<p>{p}</p>" for p in paragraphs) + "</div>"

def rail(track_cls, items_html, label):
    n = items_html.count('class="quote') or 1
    return (f'<div class="rail" role="region" aria-label="{e(label)}">'
            f'<div class="rail__track {track_cls}">{items_html}</div>'
            f'<div class="rail__controls">{meta("01 / " + str(n).zfill(2), cls="rail__count")}'
            f'<div class="rail__btns"><button class="rail__btn" data-dir="-1" aria-label="Previous">{ICON["prev"]}</button>'
            f'<button class="rail__btn" data-dir="1" aria-label="Next">{ICON["next"]}</button></div></div></div>')

# ---------------------------------------------------------------- shared chrome

def nav_href(item, page):
    if "anchor" in item:
        return f"#{item['anchor']}" if page == "index" else f"index.html#{item['anchor']}"
    return item["page"]

def header(page):
    items = ""
    for it in NAV:
        current = ' aria-current="page"' if it.get("page") == f"{page}.html" else ""
        items += f'<a href="{nav_href(it, page)}"{current}>{e(it["label"])}</a>'
    items += btn(SITE["steam_url"], "Wishlist on Steam", size="sm")
    return f'''<a class="skip" href="#main">Skip to content</a>
<header class="site-header" data-open="false">
  <div class="brand">
    <a href="index.html"><img src="images/logo-header.png" alt="{e(SITE["title"])}, home" width="{round(14*LOGO_RATIO)}" height="14"></a>
  </div>
  <nav class="nav" aria-label="Main">{items}</nav>
  <div class="header-cta">{btn(SITE["steam_url"], "Wishlist on Steam", size="sm")}</div>
  <button class="menu-toggle" aria-expanded="false" aria-label="Open menu">{ICON["menu"]}</button>
</header>'''

def footer_signup():
    mc = SITE.get("mailchimp")
    if not mc or not mc.get("action"):
        return ""
    return f'''<div class="footer-signup">
    <p class="t-meta">Studio updates by email</p>
    <form class="newsletter newsletter--sm" action="{e(mc["action"])}" method="post" target="_blank" novalidate data-mailchimp>
      <label class="sr-only" for="mce-EMAIL">Email address</label>
      <input id="mce-EMAIL" type="email" name="EMAIL" required placeholder="Email address" autocomplete="email">
      <input type="hidden" name="tags" value="{e(mc["tags"])}">
      <div class="sr-only" aria-hidden="true"><input type="text" name="{e(mc["honeypot"])}" tabindex="-1" value=""></div>
      <button class="btn btn--primary btn--sm" type="submit">Subscribe</button>
    </form>
    <p class="form-msg t-small" role="status" aria-live="polite"></p>
  </div>'''

def footer():
    follow = "".join(f"<li>{link(s['url'], s['label'], cls='')}</li>" for s in SOCIAL if s.get("url"))
    contact = "".join(f"<li>{link('mailto:' + m, m, cls='')}</li>" for m in (SITE.get("press_email"), SITE.get("biz_email")) if m)
    year = date.today().year
    return f'''<footer class="site-footer"><div class="wrap cols">
  <div>
    <img src="images/logo-header.png" alt="{e(SITE["title"])}" width="{round(14*LOGO_RATIO)}" height="14">
    <p class="t-small">A game by {e(STUDIO["name"])}. Published by {e(SITE["publisher"])}.</p>
    <p class="t-small">© {year} Levels and Bosses LLC</p>
    {footer_signup()}
  </div>
  <div>{meta("Play", "p")}<ul>
    <li>{link(SITE["steam_url"], "Steam", cls="")}</li>
    <li><a href="presskit.html">Press kit</a></li>
    <li>{link("https://www.youtube.com/watch?v=" + SITE["youtube_id"], "Trailer", cls="")}</li>
  </ul></div>
  <div>{meta("Explore", "p")}<ul>
    <li><a href="exhibitions.html">Exhibitions and playtesting</a></li>
    <li><a href="devlog.html">Devlog</a></li>
    <li><a href="merch.html">Merch</a></li>
  </ul></div>
  <div>{meta("Follow", "p")}<ul>{follow}</ul>
    {meta("Contact", "p") if contact else ""}<ul>{contact}</ul></div>
</div></footer>'''

def trailer_modal():
    return f'''<div class="modal" id="trailer-modal" data-video="{e(SITE["youtube_id"])}" data-open="false" role="dialog" aria-modal="true" aria-label="Camoflux trailer">
  <div class="modal__frame">
    <button class="modal__close btn btn--ghost btn--sm">Close</button>
    <div class="modal__loading">{meta("Loading trailer")}</div>
    <iframe title="Camoflux trailer" allow="autoplay; encrypted-media; picture-in-picture" allowfullscreen></iframe>
  </div>
</div>'''

def trailer_tile():
    thumb = f"https://img.youtube.com/vi/{SITE['youtube_id']}/maxresdefault.jpg"
    return (f'<button class="trailer-tile" data-trailer aria-label="Play the Camoflux trailer">'
            f'{media(None, src=thumb, alt="Camoflux trailer thumbnail", fallback=img_path("level-one", "main"))}'
            f'<span class="play" aria-hidden="true">{ICON["play"]}</span></button>')

def newsletter():
    """Mailchimp signup band. Identical on every page, directly above the footer.
    With JS: submits via Mailchimp's JSON endpoint and shows submitting / success / error in place.
    Without JS: a normal POST to Mailchimp in a new tab."""
    mc = SITE.get("mailchimp")
    if not mc or not mc.get("action"):
        return ""
    return f'''<section class="signup" aria-labelledby="signup-title"><div class="wrap signup__inner">
  <div class="stack">
    <h2 class="t-h2" id="signup-title">Studio updates by email</h2>
    <p class="t-body">News on Camoflux, exhibitions, and new work from Levels & Bosses.</p>
  </div>
  <div>
    <form class="newsletter" action="{e(mc["action"])}" method="post" target="_blank" novalidate data-mailchimp>
      <label class="sr-only" for="mce-EMAIL">Email address</label>
      <input id="mce-EMAIL" type="email" name="EMAIL" required placeholder="Email address" autocomplete="email">
      <input type="hidden" name="tags" value="{e(mc["tags"])}">
      <div class="sr-only" aria-hidden="true"><input type="text" name="{e(mc["honeypot"])}" tabindex="-1" value=""></div>
      <button class="btn btn--primary" type="submit">Subscribe</button>
    </form>
    <p class="form-msg t-small" role="status" aria-live="polite"></p>
  </div>
</div></section>'''

def page_shell(page, title, body, description=None, preload=None, modal=False):
    desc = e(description or SITE["lead"])
    base = (SITE.get("base_url") or "").rstrip("/")
    og = f"{base}/images/og.jpg" if base else "images/og.jpg"
    pre = f'<link rel="preload" as="image" href="{preload}" fetchpriority="high">' if preload else ""
    return f'''<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{e(title)}</title>
<meta name="description" content="{desc}">
<meta name="theme-color" content="#000000">
<link rel="icon" type="image/png" sizes="32x32" href="images/favicon-32.png">
<link rel="icon" type="image/png" sizes="16x16" href="images/favicon-16.png">
<link rel="apple-touch-icon" sizes="180x180" href="images/favicon-180.png">
<meta property="og:type" content="website">
<meta property="og:title" content="{e(title)}">
<meta property="og:description" content="{desc}">
<meta property="og:image" content="{og}">
<meta name="twitter:card" content="summary_large_image">
{pre}
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Inter:ital,wght@0,400;0,500;1,400&family=Share+Tech+Mono&display=swap" rel="stylesheet">
{adobe_fonts()}
<link rel="stylesheet" href="assets/site.css">
</head>
<body{' class="has-ab24"' if SITE["fonts"].get("adobe_kit_id") else ""}>
{header(page)}
<main id="main">
{body}
</main>
{footer()}
<div class="shotbox" id="lightbox" data-open="false" role="dialog" aria-modal="true" aria-label="Image">
  <div class="shotbox__frame"><button class="shotbox__close btn btn--ghost btn--sm">Close</button><div class="shotbox__stage"></div><p class="shotbox__cap t-meta"></p></div>
</div>
{trailer_modal() if modal else ""}
<script src="assets/site.js" defer></script>
{hero3d_scripts() if page == "index" else ""}
</body>
</html>'''

def adobe_fonts():
    kit = SITE["fonts"].get("adobe_kit_id")
    if not kit:
        return ""
    fam = SITE["fonts"]["adobe_meta_family"]
    return f'<link rel="stylesheet" href="https://use.typekit.net/{e(kit)}.css"><style>:root {{ --f-mono: "{e(fam)}", "Share Tech Mono", ui-monospace, monospace; }}</style>'

# Footage on the screen behind the model. "clip:" entries are looping MP4s made from the gameplay GIFs.
HERO_FRAMES = [("clip:amazon", "Amazon, in-game render"), ("clip:first-boss", "The First-Boss, Level One"),
               ("clip:level-one", "Level One"), ("clip:paramo", "Patterned Páramo")]

def hero3d_scripts():
    """Loads three.js and the hero only after the page is up, and only where it makes sense."""
    h = SITE.get("hero3d") or {}
    if not h.get("enabled"):
        return ""
    colors = _json.loads((ROOT / "assets/3d/frames/colors.json").read_text())
    def frame(k, c):
        if k.startswith("clip:"):
            n = k[5:]
            d = {"src": f"assets/3d/clips/{n}.jpg", "video": f"assets/3d/clips/{n}.mp4", "caption": c, "color": colors.get("clip-" + n, colors.get(n, "#1f4a33"))}
            if (ROOT / f"assets/3d/clips/{n}.webm").exists():
                d["webm"] = f"assets/3d/clips/{n}.webm"
            return d
        return {"src": f"assets/3d/frames/{k}.jpg", "caption": c, "color": colors[k]}
    def model(m):
        d = {k: v for k, v in m.items() if k not in ("id", "file")}
        d["src"] = f"assets/3d/{m['file']}"
        q = m["file"].replace(".glb", ".q.glb")
        if (ROOT / "assets/3d" / q).exists():
            d["fallback"] = f"assets/3d/{q}"
        return d
    models = {m["id"]: model(m) for m in h["models"]}
    # Homepage hero: floating level icons (hover for each level's 360, hold to look around),
    # particles that open into screenshots, The Other cycling its shape keys. See assets/hero3d-levels.js.
    lv = SITE["hero_levels"]
    cfg = {
        "icons": [{"id": x["id"], "label": x["label"], "src": f"assets/3d/{x['model']}", "height": x["height"],
                   "pano": f"assets/3d/pano/{x['pano']}.mp4", "panoPoster": f"assets/3d/pano/{x['pano']}.jpg"} for x in lv["icons"]],
        "figure": {"label": "The Other", "src": f"assets/3d/{lv['figure']}", "scale": 1.25, "lie": False,
                   **({"video": f"assets/3d/clips/{lv['figure_video']}.mp4", "poster": f"assets/3d/clips/{lv['figure_video']}.jpg",
                       "videoCaption": lv.get("figure_video_caption", "Gameplay")} if lv.get("figure_video") else {})},
        "tex": {"void": "assets/3d/void.jpg", "voidN": "assets/3d/void-n.jpg", "ground": "assets/3d/ground.jpg", "groundN": "assets/3d/ground-n.jpg"},
        "shots": [{"src": img_path(k, "sm"), "caption": IMAGES[k]["caption"]} for k in lv["shots"]],
    }
    for f in [*(x["src"] for x in cfg["icons"]), *(x["pano"] for x in cfg["icons"]), *(x["panoPoster"] for x in cfg["icons"]), cfg["figure"]["src"], *([cfg["figure"]["video"], cfg["figure"]["poster"]] if cfg["figure"].get("video") else []), *cfg["tex"].values()]:
        if not (ROOT / f).exists():
            ERRORS.append(f"3D hero asset missing: {f}")
    libs = ["https://cdn.jsdelivr.net/npm/three@0.147.0/build/three.min.js",
            "https://cdn.jsdelivr.net/npm/three@0.147.0/examples/js/loaders/GLTFLoader.js",
            "https://cdn.jsdelivr.net/npm/three@0.147.0/examples/js/libs/meshopt_decoder.js",
            "assets/hero3d-levels.js"]
    return f'''<script>window.CAMOFLUX_LEVELS = {_json.dumps(cfg, ensure_ascii=False)};
(function () {{
  var hero = document.getElementById('hero');
  var saveData = navigator.connection && navigator.connection.saveData;
  var gl = (function () {{ try {{ var c = document.createElement('canvas'); return !!(c.getContext('webgl2') || c.getContext('webgl')); }} catch (e) {{ return false; }} }})();
  if (!hero || saveData || !gl) {{ if (hero) hero.classList.add('is-still'); return; }}
  var libs = {_json.dumps(libs)};
  var next = function (i) {{ if (i >= libs.length) return; var s = document.createElement('script');
    var inline = libs[i].indexOf('inline:') === 0 && document.getElementById(libs[i].slice(7));
    if (inline) {{ s.textContent = inline.textContent; document.body.appendChild(s); return next(i + 1); }}
    s.src = libs[i];
    s.onload = function () {{ next(i + 1); }}; s.onerror = function () {{ hero.classList.add('is-still'); }}; document.body.appendChild(s); }};
  window.addEventListener('load', function () {{ next(0); }});
}})();
</script>'''

def page_head(label, title, lead="", actions=""):
    return (f'<section class="page-head"><div class="wrap"><div class="panel">{meta(label)}'
            f'<h1 class="t-h1">{e(title)}</h1>'
            + (f'<p class="t-lead">{e(lead)}</p>' if lead else "")
            + (f'<div class="actions page-head__actions">{actions}</div>' if actions else "")
            + '</div></div></section>')

# ---------------------------------------------------------------- blocks

def quote_card(q, small=False):
    who = ", ".join(x for x in (q["source"], q.get("author"), q.get("date")) if x)
    return (f'<a class="quote{" quote--sm" if small else ""}" href="{e(q["url"])}" target="_blank" rel="noopener">'
            f'<p class="t-quote">“{e(q["quote"])}”</p>'
            f'<footer>{meta(who, "p")}{meta("Read ↗", cls="ext-label")}</footer>'
            f'<span class="sr-only"> (opens in a new tab)</span></a>')

def coverage_block(groups=None):
    out = ""
    for title, items in COVERAGE.items():
        if groups and title not in groups:
            continue
        links = "".join(f'<li>{link(u, n, cls="")}</li>' for n, u in items)
        out += f'<div class="coverage">{meta(title, "p")}<ul class="coverage__list">{links}</ul></div>'
    return out

def press_block():
    top = rail("quotes quotes--2", "".join(quote_card(q) for q in PRESS_FEATURED), "Featured press")
    rest = rail("quotes quotes--3", "".join(quote_card(q, small=True) for q in PRESS_SHORT), "More press")
    return f'<div class="stack-lg">{top}{rest}</div>'

def clip_media(n, label, ar="2x1"):
    return (f'<div class="media ar-{ar} clip-wrap"><video class="clip" muted loop playsinline preload="none" poster="assets/3d/clips/{n}.jpg" aria-label="{e(label)}">'
            + (f'<source src="assets/3d/clips/{n}.webm" type="video/webm">' if (ROOT / f"assets/3d/clips/{n}.webm").exists() else "")
            + f'<source src="assets/3d/clips/{n}.mp4" type="video/mp4"></video></div>')

def feature_card(f):
    m = clip_media(f["clip"], f["title"]) if f.get("clip") else media(f["image"], ar="2x1")
    return (f'<article class="card">{m}'
            f'{meta(f["category"])}<h3 class="t-h3">{e(f["title"])}</h3>'
            f'<p class="t-small">{e(f["body"])}</p></article>')

def biome_card(i, b):
    head = f'{meta(f"{i:02d}", cls="accent")}<h3 class="t-h3">{e(b["name"])}</h3><p class="t-small">{e(b["body"])}</p>'
    if b.get("image"):
        return f'<article class="card card--step">{media(b["image"], ar="4x3")}{head}</article>'
    return f'<article class="card card--text card--step">{head}</article>'

def facts_bar():
    items = [("Status", SITE["status"]), ("Platform", SITE["platform"]), ("Engine", SITE["engine"]), ("Release", SITE["release"])]
    cells = "".join(f'<div><dt class="t-meta">{e(k)}</dt><dd>{e(v)}</dd></div>' for k, v in items)
    return f'<div class="wrap"><dl class="facts">{cells}</dl></div>'

def exhibition_rows():
    rows = ""
    for x in EXHIBITIONS["upcoming"][:3]:
        rows += (f'<a class="row" href="exhibitions.html#upcoming"><div>{meta("Upcoming")}'
                 f'<h3 class="t-h3">{e(x["title"])}</h3><p class="t-small">{e(x["venue"])}</p></div>{meta(x["dates"])}</a>')
    f = EXHIBITIONS["featured"]
    rows += (f'<a class="row" href="exhibitions.html#whitney"><div>{meta("Exhibited")}'
             f'<h3 class="t-h3">{e(f["title"])}</h3><p class="t-small">{e(f["venue"])}</p></div>{meta("2026")}</a>')
    return f'<div class="rows">{rows}</div>'

def merch_card(m):
    available = m["status"] == "available" and m.get("url")
    badge = "Available" if available else "In production"
    buy = btn(m["url"], f"Buy {m['price']}" if m.get("price") else "Buy", size="sm") if available else ""
    details = f'<p class="t-small">{e(m["details"])}</p>' if m.get("details") else ""
    return (f'<article class="card">{media(m["image"], ar="1x1", badge=badge)}'
            f'{meta(m["category"])}<h3 class="t-h3">{e(m["name"])}</h3>{details}{buy}</article>')

def devlog_card(p):
    head = (f'<time class="t-meta" datetime="{p["date"]}">{fmt_date(p["date"])}</time>'
            f'<h3 class="t-h3">{e(p["title"])}</h3><p class="t-small">{e(p["excerpt"])}</p>')
    if p.get("image"):
        return f'<a class="card" href="devlog-{p["id"]}.html">{media(p["image"], badge=p["category"])}{head}</a>'
    return f'<a class="card card--text" href="devlog-{p["id"]}.html">{meta(p["category"])}{head}</a>'

# ---------------------------------------------------------------- pages

def build_index():
    hero_img = img_path(SITE["hero_image"], "main")
    check_image(SITE["hero_image"])
    hero = f'''<section class="hero hero--3d" id="hero" aria-label="{e(SITE["full_title"])}">
  <div class="hero__poster" role="img" aria-label="{e(IMAGES[SITE["hero_image"]]["alt"])}" style="background-image:url({hero_img})"></div>
  <canvas id="scene" aria-hidden="true"></canvas>
  <div class="hero__progress" id="progress"></div>
  <p class="sr-only" id="status" role="status"></p>
  <p class="level-label t-meta" id="level-label" data-show="false" aria-hidden="true"></p>
  <div class="hero__keys"><button class="btn btn--ghost btn--sm" data-hero-next>Show the next model</button><button class="btn btn--ghost btn--sm" data-hero-shot>View the footage larger</button></div>
  <div class="hero__body seq">
    <h1 style="--i:0"><img class="hero__logo" src="images/logo.png" alt="{e(SITE["full_title"])}" width="880" height="{round(880/LOGO_RATIO)}"></h1>
    <p class="t-lead" style="--i:1">{e(SITE["lead"])}</p>
    <div class="actions" style="--i:2">
      {btn(SITE["steam_url"], "Wishlist on Steam")}
      <button class="btn btn--ghost" data-trailer>{ICON["play"]}Watch trailer</button>
    </div>
  </div>
</section>
<div class="shotbox" id="shotbox" data-open="false" role="dialog" aria-modal="true" aria-label="Game footage">
  <div class="shotbox__frame"><button class="shotbox__close btn btn--ghost btn--sm">Close</button><div class="shotbox__stage"></div><p class="shotbox__cap t-meta"></p></div>
</div>'''

    biomes = "".join(biome_card(i + 1, b) for i, b in enumerate(WORLD["biomes"]))
    world = section(split("World", f'<div class="stack-lg"><h2 class="t-h2">{e(WORLD["heading"])}</h2>{prose(WORLD["body"])}'
                                   f'<div class="grid grid--2">{biomes}</div></div>'), id_="world")
    features = section(row_head("Features") + f'<div class="grid grid--{3 if len(FEATURES) == 3 else 2}">' + "".join(feature_card(f) for f in FEATURES) + "</div>", id_="features")
    sketch = "".join(f'<figure class="sketch">{media(k, ar="4x3", size="main")}<figcaption class="t-meta">{acc(e(ARTWORK[k]["caption"]))}</figcaption></figure>' for k in SKETCHBOOK[:3])
    def clip(n, cap):
        return (f'<figure class="clip-fig"><div class="media ar-2x1 clip-wrap"><video class="clip" muted loop playsinline preload="none" poster="assets/3d/clips/{n}.jpg" aria-label="{e(cap)}">'
                + (f'<source src="assets/3d/clips/{n}.webm" type="video/webm">' if (ROOT / f"assets/3d/clips/{n}.webm").exists() else "")
                + f'<source src="assets/3d/clips/{n}.mp4" type="video/mp4"></video></div><figcaption class="t-meta">{acc(e(cap))}</figcaption></figure>')
    wide = GAMEPLAY.get("wide")
    inplay = section(row_head("In play", meta("Captured in the game")) + '<div class="grid grid--2">' + "".join(clip(n, c) for n, c in GAMEPLAY["clips"]) + "</div>"
                     + (f'<figure class="wide-fig">{media(wide, ar="wide", size="main")}<figcaption class="t-meta">{acc(e(IMAGES[wide]["caption"]))}</figcaption></figure>' if wide else ""), id_="gameplay")
    sketchbook = section(row_head("From the sketchbook", meta("Drawings behind the game")) + f'<div class="grid grid--3">{sketch}</div>', id_="sketchbook")
    trailer = section(row_head("Trailer", link("https://www.youtube.com/watch?v=" + SITE["youtube_id"], "YouTube")) + trailer_tile(), id_="trailer")
    exhibitions = section(split("Exhibitions and playtesting", exhibition_rows() + '<p class="rows-more"><a class="link" href="exhibitions.html">All exhibitions and playtesting</a></p>'))
    press = section(row_head("Press", '<a class="link" href="presskit.html">Press kit</a>') + press_block() + coverage_block(["Whitney Biennial 2026", "Interviews"]), id_="press", alt=True)
    studio = section(split("Studio", f'<div class="stack"><h2 class="t-h2">{e(STUDIO["name"])}</h2>{prose([STUDIO["short"]])}'
                                     f'<div class="actions"><a class="link" href="studio.html">Paintings and studio</a>{link(STUDIO["site"], "Leo Castañeda")}</div></div>'), id_="studio")
    available = [m for m in MERCH if m["status"] == "available" and m.get("url")]
    merch = section(row_head("Merch", '<a class="link" href="merch.html">All merch</a>') +
                    '<div class="grid grid--3">' + "".join(merch_card(m) for m in available[:3]) + "</div>") if available else ""
    cta_img = img_path(SITE["cta_image"], "main")
    cta = f'''<section class="cta"><div class="cta__media" style="background-image:url({cta_img})"></div>{frame()}
  <div class="cta__body wrap"><h2 class="t-h1">Wishlist Camoflux on Steam</h2>
  <p class="t-body">Steam will notify you when Camoflux is released.</p>
  {btn(SITE["steam_url"], "Wishlist on Steam")}</div></section>'''

    body = hero + facts_bar() + world + features + inplay + sketchbook + trailer + exhibitions + press + studio + merch + cta
    return page_shell("index", SITE["full_title"], body, preload=hero_img, modal=True)


def build_presskit():
    kit = OUT / "downloads" / "camoflux-press-kit.zip"
    facts = [
        ("Title", e(SITE["full_title"])), ("Developer", f"{e(STUDIO['name'])} ({e(STUDIO['lead'])})"),
        ("Publisher", e(SITE["publisher"])), ("Genre", e(SITE["genre"])), ("Status", e(SITE["status"])),
        ("Release", e(SITE["release"])), ("Platform", e(SITE["platform"])), ("Engine", e(SITE["engine"])),
        ("Languages", e(SITE["languages"])), ("Steam", link(SITE["steam_url"], "Store page", cls="")),
        ("Trailer", link("https://www.youtube.com/watch?v=" + SITE["youtube_id"], "YouTube", cls="")),
        ("Press contact", link("mailto:" + SITE["press_email"], SITE["press_email"], cls="") if SITE.get("press_email") else "See contact below"),
    ]
    fact_list = '<dl class="fact-list">' + "".join(f'<div><dt class="t-meta">{k}</dt><dd>{v}</dd></div>' for k, v in facts) + "</dl>"

    rows = (f'<a class="row" href="downloads/{kit.name}" download><div><h3 class="t-h3">Complete press kit</h3>'
            f'<p class="t-small">Screenshots at full resolution, logos, and fact sheet</p></div>{meta("ZIP, " + fmt_size(kit.stat().st_size))}</a>')
    for name, label, note in (("logo-white.png", "Logo, white", "For dark backgrounds"), ("logo-black.png", "Logo, black", "For light backgrounds")):
        f = IMG_DIR / name
        rows += (f'<a class="row" href="images/{name}" download><div><h3 class="t-h3">{label}</h3><p class="t-small">{note}</p></div>'
                 f'{meta(f"PNG, {MANIFEST["logo"]["width"]}×{MANIFEST["logo"]["height"]}, {fmt_size(f.stat().st_size)}")}</a>')
    downloads = f'<div class="rows">{rows}</div>'

    shots = ""
    for key, info in GAME_IMAGES.items():
        m = MANIFEST.get(key, {})
        f = IMG_DIR / f"{key}-master.jpg"
        spec = f"{m.get('master_width')}×{m.get('master_height')}, {fmt_size(f.stat().st_size)}"
        shots += (f'<a class="card" href="{img_path(key, "master")}" download>{media(key, badge_right="JPG")}'
                  f'{meta(spec)}<h3 class="t-h3">{e(info["caption"])}</h3></a>')

    recog = "".join(f'<div><div><h3 class="t-h3">{e(r["title"])}</h3><p class="t-small">{e(r["detail"])}</p></div>{meta(r["year"])}</div>' for r in RECOGNITION)
    contacts = "".join(f'<div class="stack">{meta(lbl, "p")}{link("mailto:" + SITE[k], SITE[k], cls="t-h3")}<p class="t-small">{note}</p></div>'
                       for lbl, k, note in (("Press", "press_email", "Interviews, review access, and coverage."),
                                            ("Business and exhibitions", "biz_email", "Partnerships, exhibitions, and acquisitions.")) if SITE.get(k))

    body = (page_head("Press kit", SITE["full_title"], SITE["description_50"],
                      btn(f"downloads/{kit.name}", f"Download press kit, {fmt_size(kit.stat().st_size)}", download=True) +
                      (btn("mailto:" + SITE["press_email"], "Email press contact", "ghost") if SITE.get("press_email") else ""))
            + section(split("Fact sheet", fact_list))
            + section(split("Description", f'<div class="stack-lg"><div class="stack"><h2 class="t-h3">Short</h2>{prose([SITE["description_50"]])}</div>'
                                           f'<div class="stack"><h2 class="t-h3">Long</h2>{prose(SITE["description_150"])}</div></div>'))
            + section(split("Downloads", downloads), alt=True)
            + section(row_head("Screenshots", meta("Select an image to download it at full resolution")) +
                      '<div class="grid grid--2">' + shots + "</div>", id_="screenshots")
            + section(row_head("Trailer") + trailer_tile())
            + section(split("Recognition", f'<div class="rows">{recog}</div>'), alt=True)
            + section(row_head("Press") + press_block() + coverage_block(), alt=True)
            + section(split("Studio", f'<div class="stack"><h2 class="t-h2">{e(STUDIO["name"])}</h2>{prose(STUDIO["long"])}{link(STUDIO["site"], "leonardocastaneda.com")}</div>'), id_="studio")
            + (section(split("Contact", f'<div class="grid grid--2">{contacts}</div>'), alt=True) if contacts else ""))
    return page_shell("presskit", f"Press kit, {SITE['full_title']}", body, description=SITE["description_50"], modal=True)


def build_exhibitions():
    up = ""
    for x in EXHIBITIONS["upcoming"]:
        up += (f'<div class="stack"><h2 class="t-h2">{e(x["title"])}</h2>{meta(x["type"] + ", " + x["venue"] + ", " + x["dates"], "p")}'
               f'{prose([e(x["body"])])}{link(x.get("url"), "Exhibition page")}</div>')
    f = EXHIBITIONS["featured"]
    works = ""
    for w in f["works"]:
        text = (f'<div class="stack">{meta(w["year"], "p")}<h3 class="t-h2">{e(w["title"])}</h3>'
                f'{meta(w["media"], "p")}{prose([e(w["body"])])}'
                + (f'<p class="t-small">{e(w["credits"])}</p>' if w.get("credits") else "") + "</div>")
        if w.get("image"):
            works += f'<article class="work">{media(w["image"], size="main")}{text}</article>'
        else:
            works += f'<article class="work work--text"><div class="card--text">{text}</div></article>'
    ph = f.get("photos", [])
    def photo(k, ar):
        a = ARTWORK[k]
        return f'<figure>{media(k, ar=ar, size="main")}<figcaption class="t-meta">{acc(e(a["caption"]))}. {e(a["credit"])}</figcaption></figure>'
    photos = ""
    if ph:
        photos = f'<div class="photos">{photo(ph[0], "16x9")}<div class="grid grid--2">{"".join(photo(k, "4x3") for k in ph[1:])}</div></div>'
    featured = (f'<div class="stack-lg">{photos}<div class="stack"><h2 class="t-h1">{e(f["title"])}</h2>{link(f.get("url"), "whitney.org")}'
                f'{meta(f["venue"] + ", " + f["dates"], "p")}{meta("Curated by " + f["curators"], "p")}{prose([e(f["intro"])])}</div>'
                f'<div>{works}</div><div class="quotes quote-single">{quote_card(f["quote"])}</div></div>')
    def past_row(p):
        inner = f'<div><h3 class="t-h3">{e(p["title"])}{" <span class=\"ext\" aria-hidden=\"true\">↗</span>" if p.get("url") else ""}</h3><p class="t-small">{e(p["venue"])}</p></div>{meta(p["year"])}'
        return f'<a class="row" href="{e(p["url"])}" target="_blank" rel="noopener">{inner}<span class="sr-only"> (opens in a new tab)</span></a>' if p.get("url") else f'<div>{inner}</div>'
    past = "".join(past_row(p) for p in EXHIBITIONS["past"])

    body = (page_head("Exhibitions and playtesting", "Exhibitions and playtesting", "Where Camoflux has been shown and played: installations, sculpture, commissions, and public playtests.")
            + section(split("Upcoming", up), id_="upcoming")
            + section(split("2026", featured), id_="whitney", alt=True)
            + section(split("History", f'<div class="stack-lg"><div class="rows">{past}</div>'
                            f'<figure class="history-photo">{media("supercon-performance", ar="16x9", size="main")}<figcaption class="t-meta">{acc(e(ARTWORK["supercon-performance"]["caption"]))}{(". " + e(ARTWORK["supercon-performance"]["credit"])) if ARTWORK["supercon-performance"].get("credit") else ""}</figcaption></figure></div>')))
    return page_shell("exhibitions", f"Exhibitions and playtesting, {SITE['full_title']}", body)


def published():
    return [p for p in DEVLOG if not p.get("draft")]

def build_devlog_index():
    posts = published()
    body = (page_head("Devlog", "Notes from the studio", "News, process, and exhibition reports from Levels & Bosses.")
            + section('<div class="grid grid--3">' + "".join(devlog_card(p) for p in posts) + "</div>"))
    return page_shell("devlog", f"Devlog, {SITE['full_title']}", body)

def build_devlog_post(p, posts):
    i = posts.index(p)
    newer = posts[i - 1] if i > 0 else None
    older = posts[i + 1] if i < len(posts) - 1 else None
    nav = '<nav class="post-nav" aria-label="More posts">'
    nav += f'<a href="devlog-{newer["id"]}.html">{meta("Newer")}<span class="t-h3">{e(newer["title"])}</span></a>' if newer else "<span></span>"
    nav += f'<a href="devlog-{older["id"]}.html">{meta("Older")}<span class="t-h3">{e(older["title"])}</span></a>' if older else "<span></span>"
    nav += "</nav>"
    figure = ""
    if p.get("image"):
        figure = (f'<figure class="stack">{media(p["image"], ar="21x9", size="main")}'
                  f'<figcaption class="t-small">{e(IMAGES[p["image"]]["caption"])}</figcaption></figure>')
    head = (f'<section class="page-head"><div class="wrap">'
            f'<p class="t-meta"><a href="devlog.html">Devlog</a>, <time datetime="{p["date"]}">{fmt_date(p["date"])}</time>, {e(p["category"])}</p>'
            f'<h1 class="t-h1">{e(p["title"])}</h1><p class="t-lead">{e(p["excerpt"])}</p></div></section>')
    body = head + section(f'<div class="stack-lg">{figure}<div class="split">{meta(p["category"], "p")}<div>{prose([e(x) for x in p["body"]])}{nav}</div></div></div>')
    return page_shell("devlog", f"{p['title']}, Devlog", body, description=p["excerpt"])


def build_merch():
    body = page_head("Merch", "Merch", MERCH_NOTE)
    if MERCH:
        body += section('<div class="grid grid--3">' + "".join(merch_card(m) for m in MERCH) + "</div>")
    return page_shell("merch", f"Merch, {SITE['full_title']}", body)


def build_studio():
    items = "".join(f'<figure class="painting"><img src="{img_path(k, "main")}" alt="{e(ARTWORK[k]["alt"])}" loading="lazy" data-full="{img_path(k, "main")}" data-caption="{e(ARTWORK[k]["caption"])}"><figcaption class="t-meta">{acc(e(ARTWORK[k]["caption"]))}</figcaption></figure>'
                    for k in PAINTINGS if check_image(k) is None)
    sketch = "".join(f'<figure class="painting sketch">{media(k, ar="4x3", size="main")}<figcaption class="t-meta">{acc(e(ARTWORK[k]["caption"]))}</figcaption></figure>' for k in SKETCHBOOK)
    body = (page_head("Studio", STUDIO["name"], STUDIO["short"])
            + section(split("Paintings", f'<div class="stack-lg">{prose([e(STUDIO["paintings_intro"])])}<div class="paintings">{items}</div></div>'), id_="paintings")
            + section(split("Drawings", f'<div class="grid grid--3">{sketch}</div>'), id_="drawings")
            + section(split("About", f'<div class="stack">{prose(STUDIO["long"])}{link(STUDIO["site"], "leonardocastaneda.com")}</div>'), id_="about")
            + section(split("Team", '<div class="rows">' + "".join(f'<div><div><h3 class="t-h3">{e(p["name"])}</h3></div>{meta(p["role"])}</div>' for p in STUDIO.get("team", [])) + '</div>'), id_="team"))
    return page_shell("studio", f"Studio, {SITE['full_title']}", body)


def build_hero_preview():
    """The homepage hero on its own, for sharing as a link. Not linked from the site."""
    idx = build_index()
    start = idx.index('<main id="main">') + len('<main id="main">')
    end = idx.index('</main>')
    body_html = idx[start:end]
    cut = body_html.index('<div class="wrap"><dl class="facts">')
    return idx[:start] + body_html[:cut] + facts_bar() + idx[end:]


def build_mobile_preview():
    """Design harness: shows the real, responsive index.html at phone size."""
    return '''<!DOCTYPE html><html lang="en"><head><meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1"><title>Camoflux, mobile preview</title>
<script>if (window.innerWidth < 600) location.replace('index.html');</script>
<link rel="stylesheet" href="assets/site.css">
<style>
body { min-height: 100vh; display: flex; flex-direction: column; align-items: center; gap: var(--s-4); padding: var(--s-6); background: var(--c-surface); }
.phone { width: 406px; height: 860px; border: 8px solid var(--c-surface-2); border-radius: 48px; overflow: hidden; background: var(--c-bg); }
.phone iframe { width: 390px; height: 844px; border: 0; display: block; }
</style></head><body>
<p class="t-meta">Mobile preview, 390 × 844. This frames the live index.html; there is no separate mobile build.</p>
<div class="phone"><iframe src="index.html" title="Mobile preview of the Camoflux homepage"></iframe></div>
</body></html>'''

# ---------------------------------------------------------------- press kit archive

def build_press_zip():
    dl = OUT / "downloads"
    dl.mkdir(parents=True, exist_ok=True)
    fact = [f"# {SITE['full_title']}", "", SITE["description_50"], "",
            f"Developer: {STUDIO['name']} ({STUDIO['lead']})", f"Publisher: {SITE['publisher']}",
            f"Genre: {SITE['genre']}", f"Status: {SITE['status']}", f"Release: {SITE['release']}",
            f"Platform: {SITE['platform']}", f"Engine: {SITE['engine']}", f"Steam: {SITE['steam_url']}",
            f"Trailer: https://www.youtube.com/watch?v={SITE['youtube_id']}",
            f"Press contact: {SITE.get('press_email') or 'n/a'}", "", "## Description", "", *SITE["description_150"], "",
            "## Studio", "", *[re.sub('<[^>]+>', '', p) for p in STUDIO["long"]], "", "## Image captions", "",
            *[f"{k}.jpg: {v['caption']}" for k, v in GAME_IMAGES.items()]]
    with zipfile.ZipFile(dl / "camoflux-press-kit.zip", "w", zipfile.ZIP_STORED) as z:
        z.writestr("camoflux-press-kit/fact-sheet.md", "\n".join(fact))
        for key in GAME_IMAGES:
            z.write(IMG_DIR / f"{key}-master.jpg", f"camoflux-press-kit/screenshots/{key}.jpg")
        for name in ("logo-white.png", "logo-black.png"):
            z.write(IMG_DIR / name, f"camoflux-press-kit/logo/{name}")

# ---------------------------------------------------------------- lint

def lint():
    problems = list(ERRORS)
    for f in sorted(OUT.glob("*.html")):
        s = f.read_text()
        if "—" in s:
            problems.append(f"{f.name}: contains an em dash")
        for bad in re.findall(r'href="(#?)"', s):
            problems.append(f"{f.name}: empty or '#' link")
        for tag in re.findall(r"<img\b[^>]*>", s):
            if "alt=" not in tag:
                problems.append(f"{f.name}: <img> without alt")
        for ref in set(re.findall(r'(?:src|href|data-src)="((?:images|assets|downloads)/[^"]+)"', s)):
            if not (OUT / ref).exists():
                problems.append(f"{f.name}: missing file {ref}")
        for ref in set(re.findall(r'href="([a-z0-9-]+\.html)(?:#[^"]*)?"', s)):
            if not (OUT / ref).exists():
                problems.append(f"{f.name}: broken page link {ref}")
        if re.search(r'style="(?!--i:|background-image:url)', s):
            problems.append(f"{f.name}: inline style outside the allowed set")
    return problems

# ---------------------------------------------------------------- run

def main():
    if OUT.exists():
        shutil.rmtree(OUT)
    OUT.mkdir()
    shutil.copytree(IMG_DIR, OUT / "images", ignore=shutil.ignore_patterns("manifest.json"))
    shutil.copytree(ROOT / "assets", OUT / "assets")
    build_press_zip()

    pages = {
        "index.html": build_index(),
        "presskit.html": build_presskit(),
        "exhibitions.html": build_exhibitions(),
        "studio.html": build_studio(),
        "hero-preview.html": build_hero_preview(),
        "devlog.html": build_devlog_index(),
        "merch.html": build_merch(),
        "mobile.html": build_mobile_preview(),
    }
    posts = published()
    for p in posts:
        pages[f"devlog-{p['id']}.html"] = build_devlog_post(p, posts)
    for name, markup in pages.items():
        (OUT / name).write_text(markup)
        print(f"  {name:40s} {len(markup)/1024:5.0f} KB")

    problems = lint()
    total = sum(f.stat().st_size for f in OUT.rglob("*") if f.is_file())
    print(f"\n  site/ total {total/1024/1024:.1f} MB")
    if problems:
        print("\nLint problems:")
        for p in problems:
            print("  -", p)
        sys.exit(1)
    print("  lint: no em dashes, no dead links, all images present, all alt text set")

# ---------------------------------------------------------------- standalone previews
# Chat previews and email attachments open one HTML file on its own, without the
# assets/ and images/ folders beside it, which renders as an unstyled white page.
# These copies inline the stylesheet, script, and images so each file works alone.
# Deploy site/, not preview/.

import base64

def data_uri(path):
    mime = {".png": "image/png", ".jpg": "image/jpeg", ".glb": "model/gltf-binary", ".js": "text/javascript", ".mp4": "video/mp4", ".webm": "video/webm",
            ".otf": "font/otf", ".woff2": "font/woff2"}.get(path.suffix, "application/octet-stream")
    return f"data:{mime};base64," + base64.b64encode(path.read_bytes()).decode()

def build_previews():
    prev = ROOT / "preview"
    if prev.exists():
        shutil.rmtree(prev)
    prev.mkdir()
    css = (ROOT / "assets" / "site.css").read_text()
    # CSS urls are relative to assets/; embed them so the inlined stylesheet still resolves.
    for p in sorted(set(re.findall(r"url\(['\"]?((?:ui|fonts)/[^'\")]+)", css))):
        css = css.replace(p, data_uri(ROOT / "assets" / p))
    js = (ROOT / "assets" / "site.js").read_text()
    for f in sorted(OUT.glob("*.html")):
        s = f.read_text()
        s = s.replace('<link rel="stylesheet" href="assets/site.css">', f"<style>{css}</style>")
        # Lazy images resolve through one map, so each image is embedded once.
        lazy = sorted(set(re.findall(r'data-(?:src|fallback|full)="(images/[^"]+)"', s)))
        img_map = {p: data_uri(OUT / p) for p in lazy if (OUT / p).exists()}
        s = s.replace('<script src="assets/site.js" defer></script>',
                      f"<script>window.__IMG={json.dumps(img_map)};</script><script>{js}</script>")
        # Direct references (logo, hero, CTA) are inlined in place.
        for p in sorted(set(re.findall(r'(?:src="|url\()(images/[^")]+)', s))):
            if (OUT / p).exists():
                s = s.replace(f'src="{p}"', f'src="{data_uri(OUT / p)}"').replace(f"url({p})", f"url({data_uri(OUT / p)})")
        # 3D config: use the quantized models (they need no WebAssembly, which some hosts block),
        # drop the now-duplicate fallbacks, and keep only MP4 clips, to stay small.
        if "CAMOFLUX_HERO" in s:
            s = re.sub(r'"src": "assets/3d/([\w-]+)\.glb", "fallback": "assets/3d/\1\.q\.glb"', r'"src": "assets/3d/\1.q.glb"', s)
            s = re.sub(r', "webm": "assets/3d/clips/[\w-]+\.webm"', "", s)
            s = s.replace('"https://cdn.jsdelivr.net/npm/three@0.147.0/examples/js/libs/meshopt_decoder.js", ', '')
        # The engine goes in as an inline script body, since hosts often block data: scripts.
        eng_file = next((f for f in ("hero3d-levels.js", "hero3d.js") if f'"assets/{f}"' in s), None)
        if eng_file:
            eng = (ROOT / "assets" / eng_file).read_text().replace("</script", "<\\/script")
            s = s.replace(f'"assets/{eng_file}"', '"inline:hero3d-src"')
            s = s.replace("</body>", f'<script type="text/plain" id="hero3d-src">{eng}</script>\n</body>')
        # Screenshots named inside the 3D config (particles open into these) are embedded too.
        if "window.CAMOFLUX_LEVELS" in s:
            ci = s.index("window.CAMOFLUX_LEVELS"); ce = s.index("\n", ci)
            line = s[ci:ce]
            for p in sorted(set(re.findall(r'images/[\w.-]+\.jpg', line))):
                if (ROOT / p).exists():
                    line = line.replace(f'"{p}"', f'"{data_uri(ROOT / p)}"')
            s = s[:ci] + line + s[ce:]
        # 3D hero, HUD glyphs: every assets/ path the page names is embedded.
        for p in sorted(set(re.findall(r'assets/(?:3d|ui)/[\w./-]+', s)), key=len, reverse=True):
            if (ROOT / p).exists():
                s = s.replace(p, data_uri(ROOT / p))
        s = re.sub(r'<link rel="preload"[^>]*>', "", s)
        (prev / f.name).write_text(s)
        print(f"  preview/{f.name:32s} {len(s)/1024/1024:4.1f} MB")

if __name__ == "__main__":
    main()
    build_previews()
