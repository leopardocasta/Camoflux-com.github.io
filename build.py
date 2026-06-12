#!/usr/bin/env python3
"""Camoflux site builder.

Reads content.py and emits all pages into ../output/.
Run: python3 build.py
"""
import base64
import os
import sys
from pathlib import Path

# Allow importing content.py from same dir
sys.path.insert(0, str(Path(__file__).parent))
from content import (
    SITE, NAV, FEATURES, PRESS_FEATURED, PRESS_SHORT, AWARDS,
    DOWNLOADS, DEVLOG, EXHIBITION, STUDIO, SOCIAL, MERCH,
)

ROOT = Path(__file__).parent
OUT = ROOT / "site"
OUT.mkdir(parents=True, exist_ok=True)

# ---- Image references ----
# Images live in ./images/ relative to each HTML page.
# Each key has a 'main' (1920w) and 'small' (960w) variant.
# Use main for hero/full-bleed contexts, small for cards & mobile.

def img(name, size='main'):
    """Return a relative URL to an image file.
    Sizes: 'main' (1920w), 'small' (960w, suffix -sm), 'master' (high-quality, suffix -master)
    """
    if size == 'small':
        return f'images/{name}-sm.jpg'
    elif size == 'master':
        return f'images/{name}-master.jpg'
    return f'images/{name}.jpg'

# Convenience map for legacy code that just wants a default
IMAGES = {
    "cavern": img("cavern"),
    "igapo": img("igapo"),
    "mangrove": img("mangrove"),
}
IMAGES_SM = {
    "cavern": img("cavern", "small"),
    "igapo": img("igapo", "small"),
    "mangrove": img("mangrove", "small"),
}
YT_THUMB = f"https://img.youtube.com/vi/{SITE['youtube_id']}/maxresdefault.jpg"
# Local fallback if YouTube CDN is blocked/slow:
YT_THUMB_LOCAL = "images/trailer-thumb.jpg"

def img_or_placeholder(key):
    if key and key in IMAGES:
        return f"background:url({IMAGES[key]}) center/cover no-repeat;"
    return "background:linear-gradient(135deg,#1a1d20,#2c2f33);"

# ---- Shared CSS ----
SHARED_CSS = """
*{margin:0;padding:0;box-sizing:border-box}
html{scroll-behavior:smooth}
html,body{background:#0a0b0d;color:#e8e6df;font-family:'Inter',system-ui,sans-serif;-webkit-font-smoothing:antialiased}
body{min-width:1280px;overflow-x:hidden}
.mono{font-family:'JetBrains Mono',ui-monospace,monospace}
.serif-italic{font-family:Georgia,serif;font-style:italic}
.corner{position:absolute;width:14px;height:14px;pointer-events:none}
.accent{color:#d8ff3a}
.section-label{font-family:'JetBrains Mono',monospace;font-size:10px;letter-spacing:0.22em;color:rgba(232,230,223,0.45)}
a{color:inherit;text-decoration:none}
em{font-family:Georgia,serif;font-style:italic;font-weight:400}
strong{font-weight:500}

.btn-primary{background:#d8ff3a;color:#0a0b0d;padding:13px 24px;font-size:12px;letter-spacing:0.08em;font-weight:500;display:inline-flex;align-items:center;gap:10px;cursor:pointer;border:none;transition:transform 0.2s ease, box-shadow 0.2s ease;font-family:'Inter',sans-serif}
.btn-primary:hover{transform:translateY(-2px);box-shadow:0 12px 24px -8px rgba(216,255,58,0.35)}
.btn-secondary{border:0.5px solid rgba(232,230,223,0.5);background:rgba(232,230,223,0.06);padding:13px 24px;font-size:12px;letter-spacing:0.08em;display:inline-flex;align-items:center;gap:10px;cursor:pointer;color:#e8e6df;transition:background 0.25s ease, color 0.25s ease, box-shadow 0.25s ease, border-color 0.25s ease, transform 0.2s ease;font-family:'Inter',sans-serif}
.btn-secondary:hover{background:#e8e6df;color:#0a0b0d;border-color:#e8e6df;transform:translateY(-2px);box-shadow:0 0 32px rgba(232,230,223,0.45), 0 0 64px rgba(232,230,223,0.2)}
.btn-secondary:hover .play-arrow{border-left-color:#0a0b0d}
.play-arrow{transition:border-left-color 0.25s ease}

@keyframes pulse-dot{0%,100%{opacity:1;transform:scale(1)}50%{opacity:0.4;transform:scale(0.85)}}
.rec-dot{display:inline-block;animation:pulse-dot 1.6s ease-in-out infinite}
@keyframes pulse-status{0%,100%{opacity:1}50%{opacity:0.5}}
.status-live{animation:pulse-status 2s ease-in-out infinite}
@keyframes ken-burns{0%{transform:scale(1.0) translate(0,0)}50%{transform:scale(1.08) translate(-1%,-1%)}100%{transform:scale(1.0) translate(0,0)}}
.hero-bg{position:absolute;inset:-2%;animation:ken-burns 24s ease-in-out infinite;will-change:transform}
@keyframes marquee{0%{transform:translateX(0)}100%{transform:translateX(-50%)}}
.marquee{display:flex;gap:48px;animation:marquee 40s linear infinite;width:max-content}
.marquee-wrap{overflow:hidden;mask:linear-gradient(90deg,transparent,#000 6%,#000 94%,transparent)}

.reveal{opacity:0;transform:translateY(24px);transition:opacity 0.9s cubic-bezier(0.2,0.6,0.2,1), transform 0.9s cubic-bezier(0.2,0.6,0.2,1)}
.reveal.in{opacity:1;transform:translateY(0)}

nav .nav-link{position:relative;cursor:pointer;transition:color 0.2s ease}
nav .nav-link:hover{color:#e8e6df}
nav .nav-link::after{content:'';position:absolute;bottom:-4px;left:0;width:0;height:1px;background:#d8ff3a;transition:width 0.3s ease}
nav .nav-link:hover::after{width:100%}
nav .nav-link.active{color:#e8e6df}
nav .nav-link.active::after{width:100%}

@media (prefers-reduced-motion: reduce){
  *,*::before,*::after{animation-duration:0.01ms !important;animation-iteration-count:1 !important;transition-duration:0.01ms !important}
  .hero-bg{animation:none}
  .reveal{opacity:1;transform:none}
}
"""

# ---- Reusable fragments ----
def fonts():
    return """<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500&family=JetBrains+Mono:wght@400;500&display=swap" rel="stylesheet">"""


def header(active=None):
    """Sticky header. `active` = page name to mark active in nav."""
    nav_html = ""
    for item in NAV:
        is_active = "active" if (active and item["label"].lower() == active.lower()) else ""
        nav_html += f'<a href="{item["href"]}" class="nav-link {is_active}"><span>{item["label"]}</span></a>'

    return f"""<header style="position:sticky;top:0;z-index:50;display:flex;justify-content:space-between;align-items:center;padding:18px 48px;border-bottom:0.5px solid rgba(232,230,223,0.12);background:rgba(10,11,13,0.85);backdrop-filter:blur(12px);" class="mono">
  <div style="display:flex;align-items:center;gap:24px;">
    <div style="display:flex;align-items:center;gap:10px;">
      <div class="rec-dot" style="width:7px;height:7px;background:#d8ff3a;border-radius:50%;"></div>
      <a href="index.html" style="letter-spacing:0.05em;font-weight:500;font-size:11px;">{SITE['title'].upper()} <span style="color:rgba(232,230,223,0.45);">/ {SITE['subtitle'].upper()}</span></a>
    </div>
    <div style="color:rgba(232,230,223,0.4);font-size:10px;letter-spacing:0.18em;">[ PART ONE ]</div>
  </div>
  <nav style="display:flex;gap:28px;color:rgba(232,230,223,0.65);letter-spacing:0.08em;font-size:11px;">
    {nav_html}
  </nav>
  <a href="{SITE['steam_url']}" target="_blank" class="btn-primary" style="padding:8px 18px;font-size:11px;">WISHLIST →</a>
</header>"""


def status_bar():
    return f"""<section style="padding:14px 48px;background:#14171a;display:flex;justify-content:space-between;align-items:center;font-size:10px;letter-spacing:0.15em;color:rgba(232,230,223,0.55);border-bottom:0.5px solid rgba(232,230,223,0.08);" class="mono">
  <div style="display:flex;gap:36px;">
    <span>STATUS: <span class="accent">{SITE['status']}</span></span>
    <span>EPISODE 0{SITE['episode_current']} / {'I' * SITE['episode_total']}</span>
    <span>{SITE['engine']} · {SITE['platforms']}</span>
  </div>
  <div style="display:flex;gap:8px;align-items:center;">
    <span style="color:rgba(232,230,223,0.4);">SHIPPING</span>
    <span>{SITE['release']}</span>
  </div>
</section>"""


def footer():
    return f"""<footer style="padding:48px;background:#0a0b0d;border-top:0.5px solid rgba(232,230,223,0.1);display:grid;grid-template-columns:2fr 1fr 1fr 1fr;gap:36px;" class="mono">
  <div>
    <div style="display:flex;align-items:center;gap:8px;margin-bottom:12px;">
      <div class="rec-dot" style="width:6px;height:6px;background:#d8ff3a;border-radius:50%;"></div>
      <div style="font-size:12px;font-weight:500;letter-spacing:0.05em;">{SITE['title'].upper()} <span style="color:rgba(232,230,223,0.4);">/ {SITE['subtitle'].upper()}</span></div>
    </div>
    <div style="color:rgba(232,230,223,0.45);font-size:10px;line-height:1.7;letter-spacing:0.05em;">© {STUDIO['name'].upper()} · {STUDIO['publisher'].upper()}<br/>NEWSLETTER SIGNUP →</div>
  </div>
  <div>
    <div style="font-size:10px;letter-spacing:0.18em;color:rgba(232,230,223,0.4);margin-bottom:14px;">[ PLAY ]</div>
    <div style="font-size:11px;line-height:2;color:rgba(232,230,223,0.75);letter-spacing:0.05em;">
      <a href="{SITE['steam_url']}" target="_blank">STEAM</a><br/>
      <a href="presskit.html">PRESS KIT</a><br/>
      <a href="exhibition.html">EXHIBITION</a>
    </div>
  </div>
  <div>
    <div style="font-size:10px;letter-spacing:0.18em;color:rgba(232,230,223,0.4);margin-bottom:14px;">[ FOLLOW ]</div>
    <div style="font-size:11px;line-height:2;color:rgba(232,230,223,0.75);letter-spacing:0.05em;">
      <a href="{SOCIAL['youtube']}" target="_blank">YOUTUBE</a><br/>
      <a href="{SOCIAL['instagram']}" target="_blank">INSTAGRAM</a><br/>
      <a href="{SOCIAL['x']}" target="_blank">X / THREADS</a><br/>
      <a href="{SOCIAL['tiktok']}" target="_blank">TIKTOK</a>
    </div>
  </div>
  <div>
    <div style="font-size:10px;letter-spacing:0.18em;color:rgba(232,230,223,0.4);margin-bottom:14px;">[ CONTACT ]</div>
    <div style="font-size:11px;line-height:2;color:rgba(232,230,223,0.75);letter-spacing:0.05em;"><a href="mailto:{SITE['press_email']}">{SITE['press_email'].upper()}</a></div>
  </div>
</footer>"""


def reveal_script():
    return """<script>
const reveals = document.querySelectorAll('.reveal');
const io = new IntersectionObserver((entries) => {
  entries.forEach(e => {
    if (e.isIntersecting) {
      e.target.classList.add('in');
      io.unobserve(e.target);
    }
  });
}, { threshold: 0.15, rootMargin: '0px 0px -10% 0px' });
reveals.forEach(el => io.observe(el));
</script>"""


def page_shell(title, body, extra_css="", extra_js="", description=None, preload_hero=True):
    desc = description or SITE['description_short'].replace('"', '&quot;')
    preload_tag = '<link rel="preload" as="image" href="images/cavern.jpg" fetchpriority="high">' if preload_hero else ''
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=1280, initial-scale=1">
<title>{title}</title>
<meta name="description" content="{desc}">
<link rel="icon" type="image/png" sizes="32x32" href="images/favicon-32.png">
<link rel="icon" type="image/png" sizes="16x16" href="images/favicon-16.png">
<link rel="apple-touch-icon" sizes="180x180" href="images/favicon-180.png">
<meta property="og:title" content="{title}">
<meta property="og:description" content="{desc}">
<meta property="og:image" content="images/og.jpg">
<meta property="og:type" content="website">
<meta name="twitter:card" content="summary_large_image">
<meta name="twitter:title" content="{title}">
<meta name="twitter:description" content="{desc}">
<meta name="twitter:image" content="images/og.jpg">
{preload_tag}
{fonts()}
<style>{SHARED_CSS}{extra_css}</style>
</head>
<body>
{body}
{reveal_script()}
{extra_js}
</body>
</html>"""


# ---- Page builders ----

def build_homepage():
    """The main page. With anchor IDs and working nav scroll."""
    yt_id = SITE['youtube_id']
    cavern = IMAGES['cavern']

    # Marquee with terms repeated for seamless loop
    marquee_html = ""
    for _ in range(2):
        for term in SITE['marquee_terms']:
            marquee_html += f'<span>{term}</span><span class="accent">●</span>'

    # Features grid
    features_html = ""
    for i, f in enumerate(FEATURES):
        delay = "transition-delay:0.1s;" if i % 2 == 1 else ""
        if f['image']:
            img_inner = f'<div class="img-inner" style="position:absolute;inset:0;background:url({IMAGES_SM[f["image"]]}) center/cover no-repeat;transition:transform 0.8s cubic-bezier(0.2,0.6,0.2,1);"></div>'
            placeholder = ""
        else:
            img_inner = ""
            placeholder = '<div class="mono" style="font-size:11px;letter-spacing:0.15em;color:rgba(232,230,223,0.5);">[ PROCESS DOCUMENTATION ]</div>'

        bg_style = "" if f['image'] else "background:linear-gradient(135deg,#1a1d20,#2c2f33);"
        flex_center = "display:flex;align-items:center;justify-content:center;" if not f['image'] else ""

        features_html += f"""
    <article class="feature-card reveal" style="{delay}">
      <div class="img-wrap" style="aspect-ratio:16/9;margin-bottom:20px;position:relative;overflow:hidden;{bg_style}{flex_center}">
        {img_inner}
        <div class="mono accent" style="position:absolute;top:14px;left:14px;font-size:9px;letter-spacing:0.2em;background:rgba(10,11,13,0.7);padding:5px 9px;z-index:2;">{f['tag']}</div>
        {placeholder}
      </div>
      <div class="mono" style="font-size:10px;letter-spacing:0.18em;color:rgba(232,230,223,0.5);margin-bottom:10px;">{f['category']}</div>
      <h3 style="font-size:26px;letter-spacing:-0.025em;margin-bottom:10px;font-weight:500;">{f['title']}</h3>
      <p style="font-size:15px;color:rgba(232,230,223,0.65);line-height:1.6;">{f['body']}</p>
    </article>"""

    # Merch teaser — show first 3 items with images
    merch_with_images = [m for m in MERCH if m.get('image')][:3]
    merch_teaser_html = ""
    for i, m in enumerate(merch_with_images):
        delay = f"transition-delay:{i*0.05}s;" if i > 0 else ""
        img_url = IMAGES_SM[m['image']]
        merch_teaser_html += f"""
    <a href="merch.html" class="merch-card reveal" style="display:block;{delay}">
      <div class="img-wrap" style="aspect-ratio:1/1;background:url({img_url}) center/cover no-repeat;position:relative;overflow:hidden;margin-bottom:16px;">
        <div class="img-inner" style="position:absolute;inset:0;background:url({img_url}) center/cover no-repeat;transition:transform 0.8s cubic-bezier(0.2,0.6,0.2,1);"></div>
        <div class="mono accent" style="position:absolute;top:12px;left:12px;font-size:9px;letter-spacing:0.2em;background:rgba(10,11,13,0.7);padding:5px 9px;z-index:2;">{m['category']}</div>
        <div class="mono" style="position:absolute;bottom:12px;right:12px;font-size:9px;letter-spacing:0.15em;color:rgba(232,230,223,0.85);background:rgba(10,11,13,0.7);padding:5px 9px;z-index:2;">{m['edition']}</div>
      </div>
      <div style="display:flex;justify-content:space-between;align-items:baseline;margin-bottom:6px;">
        <h3 style="font-size:18px;letter-spacing:-0.015em;font-weight:500;">{m['name']}</h3>
        <div class="mono" style="font-size:13px;letter-spacing:0.05em;color:rgba(232,230,223,0.85);">{m['price']}</div>
      </div>
      <div class="mono" style="font-size:10px;letter-spacing:0.12em;color:rgba(232,230,223,0.5);">{m['format']}</div>
    </a>"""

    # Press blocks
    press_top = ""
    for i, p in enumerate(PRESS_FEATURED):
        delay = "transition-delay:0.1s;" if i > 0 else ""
        press_top += f"""
    <a href="{p['url']}" target="_blank" class="press-quote reveal" style="display:block;background:#14171a;padding:44px 36px;{delay}">
      <p class="serif-italic" style="font-size:24px;letter-spacing:-0.015em;line-height:1.4;margin-bottom:28px;">"{p['quote']}"</p>
      <div style="display:flex;justify-content:space-between;align-items:center;padding-top:20px;border-top:0.5px solid rgba(232,230,223,0.15);" class="mono">
        <span style="font-size:11px;letter-spacing:0.12em;">{p['source']}</span>
        <span style="font-size:10px;color:rgba(232,230,223,0.5);" class="press-meta">{p['date']} · READ →</span>
      </div>
    </a>"""

    press_short = ""
    for i, p in enumerate(PRESS_SHORT):
        delay = f"transition-delay:{i*0.05+0.05}s;" if i > 0 else ""
        press_short += f"""
    <a href="{p['url']}" target="_blank" class="press-quote reveal" style="display:block;background:#14171a;padding:32px 36px;{delay}">
      <p class="serif-italic" style="font-size:17px;letter-spacing:-0.01em;line-height:1.45;margin-bottom:18px;">"{p['quote']}"</p>
      <div class="mono" style="font-size:10px;letter-spacing:0.12em;padding-top:14px;border-top:0.5px solid rgba(232,230,223,0.15);display:flex;justify-content:space-between;">
        <span>{p['source']}</span>
        <span class="press-meta" style="color:rgba(232,230,223,0.5);">READ →</span>
      </div>
    </a>"""

    extra_css = """
.feature-card{transition:transform 0.4s cubic-bezier(0.2,0.6,0.2,1)}
.feature-card:hover{transform:translateY(-6px)}
.feature-card .img-wrap{transition:filter 0.4s ease}
.feature-card:hover .img-wrap{filter:brightness(1.08)}
.feature-card:hover .img-inner{transform:scale(1.05)}
.play-btn{transition:transform 0.3s ease, background 0.3s ease}
.trailer-link:hover .play-btn{transform:scale(1.1);background:rgba(216,255,58,0.2)}
.trailer-link .img-zoom{transition:transform 0.8s cubic-bezier(0.2,0.6,0.2,1)}
.trailer-link:hover .img-zoom{transform:scale(1.04)}
.press-quote{transition:background 0.3s ease, transform 0.3s ease}
.press-quote:hover{background:#1a1d20;transform:translateY(-3px)}
.press-quote:hover .press-meta{color:#d8ff3a}
.press-meta{transition:color 0.25s ease}
.merch-card{transition:transform 0.4s cubic-bezier(0.2,0.6,0.2,1)}
.merch-card:hover{transform:translateY(-6px)}
.merch-card .img-wrap{transition:filter 0.4s ease}
.merch-card:hover .img-wrap{filter:brightness(1.08)}
.merch-card:hover .img-inner{transform:scale(1.05)}
.modal-overlay{position:fixed;inset:0;background:rgba(10,11,13,0.92);display:none;align-items:center;justify-content:center;z-index:1000;opacity:0;transition:opacity 0.3s ease}
.modal-overlay.open{display:flex;opacity:1}
.modal-frame{width:80vw;max-width:1280px;aspect-ratio:16/9;position:relative}
.modal-close{position:absolute;top:-44px;right:0;color:#e8e6df;font-size:14px;letter-spacing:0.15em;cursor:pointer;font-family:'JetBrains Mono',monospace;background:none;border:none}
"""

    extra_js = f"""<script>
const modal = document.getElementById('trailer-modal');
const iframe = document.getElementById('trailer-iframe');
const openBtn = document.getElementById('open-trailer');
const trailerBlock = document.getElementById('trailer-block');
const closeBtn = document.getElementById('close-trailer');
function openTrailer(e){{
  if (e) e.preventDefault();
  iframe.src = 'https://www.youtube.com/embed/{yt_id}?autoplay=1&rel=0';
  modal.classList.add('open');
  document.body.style.overflow = 'hidden';
}}
function closeTrailer(){{
  iframe.src = '';
  modal.classList.remove('open');
  document.body.style.overflow = '';
}}
openBtn.addEventListener('click', openTrailer);
trailerBlock.addEventListener('click', openTrailer);
closeBtn.addEventListener('click', closeTrailer);
modal.addEventListener('click', (e) => {{ if (e.target === modal) closeTrailer(); }});
document.addEventListener('keydown', (e) => {{ if (e.key === 'Escape') closeTrailer(); }});
</script>"""

    body = f"""{header(active="world")}

<section id="world" style="position:relative;height:680px;overflow:hidden;">
  <div class="hero-bg" style="background:url({cavern}) center/cover no-repeat;"></div>
  <div style="position:absolute;inset:0;background:linear-gradient(180deg,rgba(10,11,13,0.55) 0%,rgba(10,11,13,0.15) 30%,rgba(10,11,13,0.45) 70%,rgba(10,11,13,0.95) 100%);"></div>
  <div style="position:absolute;top:32px;left:48px;right:48px;display:flex;justify-content:space-between;font-size:10px;letter-spacing:0.18em;color:rgba(232,230,223,0.65);" class="mono">
    <div>[ INCENDIO IGAPÓ // PART_01 ]</div>
    <div style="display:flex;gap:28px;">
      <span class="accent status-live">● REC</span>
    </div>
  </div>
  <div class="corner" style="top:24px;left:40px;border-left:1px solid rgba(232,230,223,0.5);border-top:1px solid rgba(232,230,223,0.5);"></div>
  <div class="corner" style="top:24px;right:40px;border-right:1px solid rgba(232,230,223,0.5);border-top:1px solid rgba(232,230,223,0.5);"></div>
  <div class="corner" style="bottom:24px;left:40px;border-left:1px solid rgba(232,230,223,0.5);border-bottom:1px solid rgba(232,230,223,0.5);"></div>
  <div class="corner" style="bottom:24px;right:40px;border-right:1px solid rgba(232,230,223,0.5);border-bottom:1px solid rgba(232,230,223,0.5);"></div>
  <div style="position:absolute;bottom:80px;left:48px;right:48px;">
    <div class="mono reveal" style="font-size:10px;letter-spacing:0.22em;color:rgba(232,230,223,0.6);margin-bottom:20px;">AN EPISODIC EXPLORATION GAME · {SITE['release'].split()[0]}</div>
    <h1 class="reveal" style="font-size:88px;line-height:0.95;letter-spacing:-0.04em;font-weight:500;max-width:1000px;margin-bottom:24px;transition-delay:0.1s;">{SITE['tagline']}</h1>
    <p class="reveal" style="font-size:16px;line-height:1.55;color:rgba(232,230,223,0.78);max-width:520px;margin-bottom:32px;transition-delay:0.2s;">{SITE['description_short']}</p>
    <div class="reveal" style="display:flex;gap:14px;align-items:center;transition-delay:0.3s;">
      <a href="{SITE['steam_url']}" target="_blank" class="btn-primary">WISHLIST ON STEAM →</a>
      <button class="btn-secondary" id="open-trailer">
        <div class="play-arrow" style="width:0;height:0;border-left:6px solid #e8e6df;border-top:4px solid transparent;border-bottom:4px solid transparent;"></div>
        WATCH TRAILER
      </button>
    </div>
  </div>
</section>

{status_bar()}

<section style="padding:32px 48px;background:#0f1012;border-bottom:0.5px solid rgba(232,230,223,0.08);display:grid;grid-template-columns:240px 1fr auto;gap:36px;align-items:center;">
  <div>
    <div class="section-label" style="margin-bottom:6px;">[ NOW SHOWING ]</div>
    <div style="font-size:18px;letter-spacing:-0.01em;font-weight:500;">{EXHIBITION['subtitle']}</div>
  </div>
  <div class="serif-italic" style="font-size:15px;color:rgba(232,230,223,0.75);line-height:1.55;">"{EXHIBITION['press_quote']}"</div>
  <a href="exhibition.html" class="mono" style="font-size:10px;letter-spacing:0.15em;color:rgba(232,230,223,0.5);text-align:right;">
    <div>{EXHIBITION['dates'].replace(', 2026','').upper()}</div>
    <div class="accent" style="margin-top:4px;">VISIT →</div>
  </a>
</section>

<section class="marquee-wrap" style="padding:20px 0;background:#0a0b0d;border-bottom:0.5px solid rgba(232,230,223,0.08);">
  <div class="marquee mono" style="font-size:13px;letter-spacing:0.15em;color:rgba(232,230,223,0.45);">
    {marquee_html}
  </div>
</section>

<section style="padding:120px 48px;">
  <div style="display:grid;grid-template-columns:240px 1fr;gap:64px;">
    <div class="section-label reveal" style="padding-top:14px;">[ PART_01 ]</div>
    <div>
      <h2 class="reveal" style="font-size:48px;letter-spacing:-0.03em;line-height:1.05;font-weight:500;margin-bottom:28px;max-width:780px;">You are <em>The Other</em>.</h2>
      <p class="reveal" style="font-size:17px;line-height:1.7;color:rgba(232,230,223,0.7);max-width:680px;transition-delay:0.1s;">A third-person ontology where landscapes, bodies, and technology fuse. Adapt to shifting conditions through vibrational terraforming, camouflage, and electromagnetic sensors. Solve environmental puzzles. Choose to destroy bosses — or engage with them.</p>
    </div>
  </div>
</section>

<section id="features" style="padding:0 48px 120px;scroll-margin-top:80px;">
  <div style="display:flex;justify-content:space-between;align-items:baseline;margin-bottom:36px;" class="mono">
    <div class="section-label">[ FEATURES ]</div>
    <div style="font-size:10px;letter-spacing:0.15em;color:rgba(232,230,223,0.4);">{len(FEATURES):02d} SYSTEMS</div>
  </div>
  <div style="display:grid;grid-template-columns:1fr 1fr;gap:32px;">
    {features_html}
  </div>
</section>

<section id="trailer" style="padding:0 48px 120px;scroll-margin-top:80px;">
  <div style="display:flex;justify-content:space-between;align-items:baseline;margin-bottom:28px;" class="mono">
    <div class="section-label">[ TRAILER ]</div>
    <div style="font-size:10px;letter-spacing:0.15em;color:rgba(232,230,223,0.4);">{SITE['trailer_duration']} · 4K</div>
  </div>
  <a href="https://www.youtube.com/watch?v={yt_id}" target="_blank" id="trailer-block" class="trailer-link reveal" style="position:relative;aspect-ratio:16/9;overflow:hidden;display:block;">
    <div class="img-zoom" style="position:absolute;inset:0;background:url({YT_THUMB}) center/cover no-repeat;"></div>
    <div style="position:absolute;inset:0;background:linear-gradient(180deg,transparent 50%,rgba(10,11,13,0.7) 100%);"></div>
    <div class="mono" style="position:absolute;top:18px;left:18px;right:18px;display:flex;justify-content:space-between;font-size:10px;letter-spacing:0.15em;color:rgba(232,230,223,0.7);">
      <span class="accent status-live">● LIVE FEED</span>
      <span>YT://{yt_id}</span>
    </div>
    <div class="play-btn" style="position:absolute;top:50%;left:50%;transform:translate(-50%,-50%);width:88px;height:88px;border:1px solid rgba(232,230,223,0.85);border-radius:50%;display:flex;align-items:center;justify-content:center;background:rgba(10,11,13,0.4);">
      <div style="width:0;height:0;border-left:22px solid #e8e6df;border-top:13px solid transparent;border-bottom:13px solid transparent;margin-left:6px;"></div>
    </div>
    <div class="mono" style="position:absolute;bottom:20px;left:18px;font-size:10px;letter-spacing:0.15em;color:rgba(232,230,223,0.7);">CAMOFLUX_TRAILER_2024.mp4</div>
  </a>
</section>

<section id="press" style="padding:120px 48px;background:#14171a;scroll-margin-top:80px;">
  <div style="display:grid;grid-template-columns:240px 1fr;gap:64px;margin-bottom:64px;">
    <div class="section-label reveal" style="padding-top:14px;">[ PRESS ]</div>
    <h2 class="reveal" style="font-size:34px;letter-spacing:-0.025em;line-height:1.2;max-width:760px;font-weight:400;">Critics on the practice — from gallery to game engine.</h2>
  </div>
  <div style="display:grid;grid-template-columns:1fr 1fr;gap:1px;background:rgba(232,230,223,0.1);margin-bottom:1px;">
    {press_top}
  </div>
  <div style="display:grid;grid-template-columns:1fr 1fr 1fr;gap:1px;background:rgba(232,230,223,0.1);">
    {press_short}
  </div>
  <div style="margin-top:32px;text-align:right;">
    <a href="presskit.html" class="mono" style="font-size:11px;letter-spacing:0.15em;color:#d8ff3a;">FULL PRESS KIT →</a>
  </div>
</section>

<section id="studio" style="padding:120px 48px;scroll-margin-top:80px;">
  <div style="display:grid;grid-template-columns:240px 1fr;gap:64px;">
    <div class="section-label reveal" style="padding-top:14px;">[ STUDIO ]</div>
    <div>
      <h2 class="reveal" style="font-size:38px;letter-spacing:-0.025em;line-height:1.1;font-weight:500;margin-bottom:22px;">{STUDIO['name']}</h2>
      <p class="reveal" style="font-size:16px;color:rgba(232,230,223,0.72);line-height:1.65;max-width:620px;margin-bottom:28px;transition-delay:0.1s;">{STUDIO['blurb_short']}</p>
      <a href="#" class="mono accent reveal" style="font-size:11px;letter-spacing:0.12em;display:inline-block;transition-delay:0.2s;">ABOUT THE STUDIO →</a>
    </div>
  </div>
</section>

<section style="padding:0 48px 120px;">
  <div style="display:flex;justify-content:space-between;align-items:baseline;margin-bottom:36px;" class="mono">
    <div class="section-label reveal">[ MERCH ]</div>
    <a href="merch.html" class="reveal" style="font-size:11px;letter-spacing:0.15em;color:#d8ff3a;">SHOP ALL →</a>
  </div>
  <div style="display:grid;grid-template-columns:1fr 1fr 1fr;gap:24px;">
    {merch_teaser_html}
  </div>
</section>

<section style="position:relative;padding:160px 48px;text-align:center;overflow:hidden;">
  <div class="hero-bg" style="background:url({cavern}) center/cover no-repeat;animation-duration:32s;"></div>
  <div style="position:absolute;inset:0;background:rgba(10,11,13,0.78);"></div>
  <div class="corner" style="top:32px;left:48px;border-left:1px solid rgba(232,230,223,0.5);border-top:1px solid rgba(232,230,223,0.5);"></div>
  <div class="corner" style="top:32px;right:48px;border-right:1px solid rgba(232,230,223,0.5);border-top:1px solid rgba(232,230,223,0.5);"></div>
  <div class="corner" style="bottom:32px;left:48px;border-left:1px solid rgba(232,230,223,0.5);border-bottom:1px solid rgba(232,230,223,0.5);"></div>
  <div class="corner" style="bottom:32px;right:48px;border-right:1px solid rgba(232,230,223,0.5);border-bottom:1px solid rgba(232,230,223,0.5);"></div>
  <div style="position:relative;">
    <div class="mono reveal" style="font-size:11px;letter-spacing:0.22em;color:rgba(232,230,223,0.55);margin-bottom:28px;">[ TRANSMISSION ENDS · {SITE['release'].split()[0]} ]</div>
    <h2 class="reveal" style="font-size:80px;letter-spacing:-0.035em;line-height:1;margin-bottom:28px;font-weight:500;transition-delay:0.1s;">Wishlist now.</h2>
    <p class="reveal" style="font-size:16px;color:rgba(232,230,223,0.7);margin-bottom:40px;max-width:520px;margin-left:auto;margin-right:auto;transition-delay:0.2s;">Get notified the moment Camoflux releases on Steam.</p>
    <a href="{SITE['steam_url']}" target="_blank" class="btn-primary reveal" style="padding:16px 34px;font-size:13px;transition-delay:0.3s;">WISHLIST ON STEAM →</a>
  </div>
</section>

{footer()}

<div class="modal-overlay" id="trailer-modal">
  <div class="modal-frame">
    <button class="modal-close" id="close-trailer">[ CLOSE × ]</button>
    <iframe id="trailer-iframe" width="100%" height="100%" src="" frameborder="0" allow="autoplay; encrypted-media; picture-in-picture" allowfullscreen></iframe>
  </div>
</div>"""

    return page_shell(f"{SITE['title']} — {SITE['subtitle']}", body, extra_css=extra_css, extra_js=extra_js)


def build_devlog_index():
    """Devlog list page."""
    posts_html = ""
    for i, post in enumerate(DEVLOG):
        delay = f"transition-delay:{(i % 3) * 0.05}s;"
        img_style = ""
        if post.get('image'):
            img_style = f"background:url({IMAGES_SM[post['image']]}) center/cover no-repeat;"
        else:
            img_style = "background:linear-gradient(135deg,#1a1d20,#2c2f33);"

        date_iso = post['date']
        date_display = date_iso.replace("-", ".")

        posts_html += f"""
    <a href="devlog-{post['id']}.html" class="devlog-card reveal" style="display:block;{delay}">
      <div class="img-wrap" style="aspect-ratio:16/9;{img_style}position:relative;overflow:hidden;margin-bottom:18px;">
        <div class="mono accent" style="position:absolute;top:14px;left:14px;font-size:9px;letter-spacing:0.2em;background:rgba(10,11,13,0.7);padding:5px 9px;z-index:2;">{post['category']}</div>
        <div class="img-inner" style="position:absolute;inset:0;{img_style}transition:transform 0.8s cubic-bezier(0.2,0.6,0.2,1);"></div>
      </div>
      <div class="mono" style="font-size:10px;letter-spacing:0.18em;color:rgba(232,230,223,0.5);margin-bottom:10px;">{date_display}</div>
      <h3 style="font-size:22px;letter-spacing:-0.02em;line-height:1.25;margin-bottom:10px;font-weight:500;">{post['title']}</h3>
      <p style="font-size:14px;color:rgba(232,230,223,0.65);line-height:1.55;margin-bottom:14px;">{post['excerpt']}</p>
      <span class="mono accent read-more" style="font-size:10px;letter-spacing:0.15em;">READ →</span>
    </a>"""

    extra_css = """
.devlog-card{transition:transform 0.4s cubic-bezier(0.2,0.6,0.2,1)}
.devlog-card:hover{transform:translateY(-4px)}
.devlog-card .img-wrap{transition:filter 0.4s ease}
.devlog-card:hover .img-wrap{filter:brightness(1.08)}
.devlog-card:hover .img-inner{transform:scale(1.05)}
.devlog-card:hover .read-more{color:#d8ff3a}
"""

    body = f"""{header(active="devlog")}

<section style="padding:80px 48px 40px;border-bottom:0.5px solid rgba(232,230,223,0.1);">
  <div class="mono reveal" style="font-size:10px;letter-spacing:0.22em;color:rgba(232,230,223,0.5);margin-bottom:18px;">[ DEVLOG · {len(DEVLOG):02d} ENTRIES ]</div>
  <h1 class="reveal" style="font-size:88px;line-height:0.95;letter-spacing:-0.04em;font-weight:500;margin-bottom:28px;max-width:1100px;transition-delay:0.1s;">Notes from the build.</h1>
  <p class="reveal" style="font-size:17px;line-height:1.6;color:rgba(232,230,223,0.7);max-width:680px;transition-delay:0.2s;">Process documentation, exhibition reports, and writing about the practice. New entries published as they happen.</p>
</section>

{status_bar()}

<section style="padding:96px 48px;">
  <div style="display:grid;grid-template-columns:repeat(3,1fr);gap:40px;">
    {posts_html}
  </div>
</section>

{footer()}"""

    return page_shell(f"Devlog — {SITE['title']}", body, extra_css=extra_css)


def build_devlog_post(post):
    """Individual devlog post page."""
    img_url = IMAGES[post['image']] if post.get('image') else None
    body_html = "".join(f'<p style="font-size:17px;line-height:1.75;color:rgba(232,230,223,0.85);margin-bottom:24px;">{para}</p>' for para in post['body'])

    # Find prev/next posts
    idx = next(i for i, p in enumerate(DEVLOG) if p['id'] == post['id'])
    prev_post = DEVLOG[idx - 1] if idx > 0 else None
    next_post = DEVLOG[idx + 1] if idx < len(DEVLOG) - 1 else None

    nav_html = '<div style="display:grid;grid-template-columns:1fr 1fr;gap:32px;margin-top:64px;padding-top:48px;border-top:0.5px solid rgba(232,230,223,0.15);">'
    if prev_post:
        nav_html += f'<a href="devlog-{prev_post["id"]}.html" style="display:block;"><div class="mono" style="font-size:10px;letter-spacing:0.18em;color:rgba(232,230,223,0.5);margin-bottom:8px;">← NEWER</div><div style="font-size:16px;letter-spacing:-0.01em;font-weight:500;">{prev_post["title"]}</div></a>'
    else:
        nav_html += '<div></div>'
    if next_post:
        nav_html += f'<a href="devlog-{next_post["id"]}.html" style="display:block;text-align:right;"><div class="mono" style="font-size:10px;letter-spacing:0.18em;color:rgba(232,230,223,0.5);margin-bottom:8px;">OLDER →</div><div style="font-size:16px;letter-spacing:-0.01em;font-weight:500;">{next_post["title"]}</div></a>'
    else:
        nav_html += '<div></div>'
    nav_html += '</div>'

    hero_img_html = ""
    if img_url:
        hero_img_html = f"""
<section style="padding:0 48px 48px;">
  <div style="aspect-ratio:21/9;background:url({img_url}) center/cover no-repeat;position:relative;">
    <div class="mono" style="position:absolute;bottom:16px;left:16px;font-size:10px;letter-spacing:0.15em;color:rgba(232,230,223,0.7);background:rgba(10,11,13,0.5);padding:6px 10px;">DEVLOG_{post['id'].upper()}_HERO.JPG</div>
  </div>
</section>"""

    date_display = post['date'].replace("-", ".")

    body = f"""{header(active="devlog")}

<section style="padding:80px 48px 48px;">
  <div class="mono reveal" style="display:flex;gap:24px;font-size:10px;letter-spacing:0.18em;color:rgba(232,230,223,0.5);margin-bottom:24px;">
    <span><a href="devlog.html" class="accent">← DEVLOG</a></span>
    <span>{date_display}</span>
    <span class="accent">{post['category']}</span>
  </div>
  <h1 class="reveal" style="font-size:64px;line-height:1.0;letter-spacing:-0.035em;font-weight:500;margin-bottom:24px;max-width:1000px;transition-delay:0.1s;">{post['title']}</h1>
  <p class="reveal" style="font-size:18px;line-height:1.55;color:rgba(232,230,223,0.7);max-width:720px;font-style:italic;font-family:Georgia,serif;transition-delay:0.2s;">{post['excerpt']}</p>
</section>

{hero_img_html}

<article style="padding:48px 48px 96px;max-width:780px;margin:0 auto;">
  {body_html}
  {nav_html}
</article>

{footer()}"""

    return page_shell(f"{post['title']} — Devlog", body)


def build_exhibition():
    """Whitney exhibition page."""
    works_html = ""
    for i, w in enumerate(EXHIBITION['works']):
        img_url = IMAGES.get(w['image']) if w.get('image') else None
        img_style = f"background:url({img_url}) center/cover no-repeat;" if img_url else "background:linear-gradient(135deg,#1a1d20,#2c2f33);"

        layout = "1fr 1.2fr" if i % 2 == 0 else "1.2fr 1fr"
        order_text = "" if i % 2 == 0 else "order:2;"
        order_img = "" if i % 2 == 0 else "order:1;"

        works_html += f"""
    <article class="reveal" style="display:grid;grid-template-columns:{layout};gap:48px;align-items:center;margin-bottom:96px;">
      <div style="{order_text}">
        <div class="mono accent" style="font-size:10px;letter-spacing:0.22em;margin-bottom:14px;">WORK_{i+1:02d}</div>
        <h3 style="font-size:32px;letter-spacing:-0.025em;line-height:1.1;font-weight:500;margin-bottom:8px;">{w['title']}</h3>
        <div class="mono" style="font-size:11px;letter-spacing:0.12em;color:rgba(232,230,223,0.5);margin-bottom:18px;">{w['year']} · {w['media']}</div>
        <p style="font-size:15px;color:rgba(232,230,223,0.72);line-height:1.65;">{w['description']}</p>
      </div>
      <div style="aspect-ratio:4/3;{img_style}position:relative;{order_img}">
        <div class="mono" style="position:absolute;bottom:14px;left:14px;font-size:10px;letter-spacing:0.15em;color:rgba(232,230,223,0.7);background:rgba(10,11,13,0.5);padding:6px 10px;">{w['title'].upper()[:40]}</div>
      </div>
    </article>"""

    cavern = IMAGES['cavern']

    body = f"""{header(active="world")}

<section style="position:relative;height:520px;overflow:hidden;">
  <div class="hero-bg" style="background:url({cavern}) center/cover no-repeat;"></div>
  <div style="position:absolute;inset:0;background:linear-gradient(180deg,rgba(10,11,13,0.55) 0%,rgba(10,11,13,0.25) 30%,rgba(10,11,13,0.5) 70%,rgba(10,11,13,0.95) 100%);"></div>
  <div style="position:absolute;top:32px;left:48px;right:48px;display:flex;justify-content:space-between;font-size:10px;letter-spacing:0.18em;color:rgba(232,230,223,0.65);" class="mono">
    <div>[ EXHIBITION // WHITNEY BIENNIAL 2026 ]</div>
    <div class="accent status-live">● ON VIEW</div>
  </div>
  <div class="corner" style="top:24px;left:40px;border-left:1px solid rgba(232,230,223,0.5);border-top:1px solid rgba(232,230,223,0.5);"></div>
  <div class="corner" style="top:24px;right:40px;border-right:1px solid rgba(232,230,223,0.5);border-top:1px solid rgba(232,230,223,0.5);"></div>
  <div class="corner" style="bottom:24px;left:40px;border-left:1px solid rgba(232,230,223,0.5);border-bottom:1px solid rgba(232,230,223,0.5);"></div>
  <div class="corner" style="bottom:24px;right:40px;border-right:1px solid rgba(232,230,223,0.5);border-bottom:1px solid rgba(232,230,223,0.5);"></div>
  <div style="position:absolute;bottom:64px;left:48px;right:48px;">
    <div class="mono reveal" style="font-size:10px;letter-spacing:0.22em;color:rgba(232,230,223,0.7);margin-bottom:18px;">{EXHIBITION['subtitle']} · {EXHIBITION['dates'].upper()}</div>
    <h1 class="reveal" style="font-size:80px;line-height:0.95;letter-spacing:-0.04em;font-weight:500;max-width:1000px;transition-delay:0.1s;">{EXHIBITION['title']}</h1>
  </div>
</section>

<section style="padding:18px 48px;background:#14171a;display:grid;grid-template-columns:repeat(4,1fr);gap:32px;font-size:10px;letter-spacing:0.15em;color:rgba(232,230,223,0.65);border-bottom:0.5px solid rgba(232,230,223,0.08);" class="mono">
  <div><span class="accent">VENUE</span><br/><span style="color:#e8e6df;font-size:11px;letter-spacing:0.05em;">{EXHIBITION['venue']}</span></div>
  <div><span class="accent">FLOOR</span><br/><span style="color:#e8e6df;font-size:11px;letter-spacing:0.05em;">{EXHIBITION['floor']}</span></div>
  <div><span class="accent">CURATORS</span><br/><span style="color:#e8e6df;font-size:11px;letter-spacing:0.05em;">{EXHIBITION['curators']}</span></div>
  <div><span class="accent">DATES</span><br/><span style="color:#e8e6df;font-size:11px;letter-spacing:0.05em;">{EXHIBITION['dates']}</span></div>
</section>

<section style="padding:96px 48px;">
  <div style="display:grid;grid-template-columns:240px 1fr;gap:64px;">
    <div class="section-label reveal" style="padding-top:14px;">[ ABOUT ]</div>
    <p class="reveal" style="font-size:21px;line-height:1.55;color:rgba(232,230,223,0.85);max-width:760px;font-weight:400;letter-spacing:-0.01em;transition-delay:0.1s;">{EXHIBITION['intro']}</p>
  </div>
</section>

<section style="padding:0 48px 96px;">
  <div style="display:grid;grid-template-columns:240px 1fr;gap:64px;margin-bottom:48px;">
    <div class="section-label reveal" style="padding-top:14px;">[ WORKS ON VIEW ]</div>
    <div class="mono reveal" style="font-size:11px;letter-spacing:0.12em;color:rgba(232,230,223,0.5);">03 INSTALLATIONS</div>
  </div>
  <div style="display:grid;grid-template-columns:240px 1fr;gap:64px;">
    <div></div>
    <div>
      {works_html}
    </div>
  </div>
</section>

<section style="padding:96px 48px;background:#14171a;">
  <div style="display:grid;grid-template-columns:240px 1fr;gap:64px;align-items:center;">
    <div class="section-label reveal">[ PRESS ]</div>
    <div>
      <blockquote class="reveal" style="margin:0;">
        <p class="serif-italic" style="font-size:32px;letter-spacing:-0.02em;line-height:1.35;margin-bottom:28px;">"{EXHIBITION['press_quote']}"</p>
        <footer style="display:flex;justify-content:space-between;align-items:center;padding-top:20px;border-top:0.5px solid rgba(232,230,223,0.15);" class="mono">
          <cite style="font-size:11px;letter-spacing:0.12em;font-style:normal;">{EXHIBITION['press_source'].upper()}</cite>
          <a href="{EXHIBITION['press_url']}" target="_blank" class="accent" style="font-size:11px;letter-spacing:0.12em;">READ FULL ARTICLE →</a>
        </footer>
      </blockquote>
    </div>
  </div>
</section>

<section style="padding:96px 48px;">
  <div style="display:grid;grid-template-columns:240px 1fr;gap:64px;">
    <div class="section-label reveal" style="padding-top:14px;">[ VISIT ]</div>
    <div style="max-width:760px;">
      <h2 class="reveal" style="font-size:38px;letter-spacing:-0.025em;line-height:1.1;font-weight:500;margin-bottom:32px;">Plan your visit.</h2>
      <div style="display:grid;grid-template-columns:1fr 1fr;gap:32px;margin-bottom:32px;">
        <div class="reveal">
          <div class="mono" style="font-size:10px;letter-spacing:0.18em;color:rgba(232,230,223,0.5);margin-bottom:10px;">ADDRESS</div>
          <div style="font-size:15px;line-height:1.6;color:rgba(232,230,223,0.85);">{EXHIBITION['venue']}<br/>{EXHIBITION['venue_address']}</div>
        </div>
        <div class="reveal" style="transition-delay:0.05s;">
          <div class="mono" style="font-size:10px;letter-spacing:0.18em;color:rgba(232,230,223,0.5);margin-bottom:10px;">HOURS</div>
          <div style="font-size:15px;line-height:1.6;color:rgba(232,230,223,0.85);">{EXHIBITION['hours']}</div>
        </div>
        <div class="reveal">
          <div class="mono" style="font-size:10px;letter-spacing:0.18em;color:rgba(232,230,223,0.5);margin-bottom:10px;">ADMISSION</div>
          <div style="font-size:15px;line-height:1.6;color:rgba(232,230,223,0.85);">{EXHIBITION['admission']}</div>
        </div>
        <div class="reveal" style="transition-delay:0.05s;">
          <div class="mono" style="font-size:10px;letter-spacing:0.18em;color:rgba(232,230,223,0.5);margin-bottom:10px;">DATES</div>
          <div style="font-size:15px;line-height:1.6;color:rgba(232,230,223,0.85);">{EXHIBITION['dates']}</div>
        </div>
      </div>
      <a href="{EXHIBITION['visit_url']}" target="_blank" class="btn-primary">VISIT WHITNEY.ORG →</a>
    </div>
  </div>
</section>

{footer()}"""

    return page_shell(f"{EXHIBITION['title']} — {SITE['title']}", body)


def build_presskit():
    """Press kit. Same as before but generated from data."""
    facts_html = ""
    facts = [
        ("TITLE", f"{SITE['title']}: {SITE['subtitle']}"),
        ("DEVELOPER", f"{STUDIO['name']} ({STUDIO['lead']})"),
        ("PUBLISHER", STUDIO['publisher']),
        ("RELEASE", f"{SITE['release']} (Episode 0{SITE['episode_current']} of {'I' * SITE['episode_total']})"),
        ("PLATFORMS", "PC (Steam) — Windows, macOS, Linux"),
        ("PRICE", "TBA"),
        ("ENGINE", "Unreal Engine 5"),
        ("LANGUAGES", "English, Spanish (interface)"),
        ("EXHIBITION", f"{EXHIBITION['subtitle']} · {EXHIBITION['dates']}"),
        ("PRESS CONTACT", f'<a href="mailto:{SITE["press_email"]}" class="accent">{SITE["press_email"]}</a>'),
    ]
    for k, v in facts:
        facts_html += f'<div class="fact-row"><div class="fact-key">{k}</div><div class="fact-val">{v}</div></div>'

    tags = ["Exploration", "Adventure", "Puzzle", "Stealth", "Atmospheric", "Surreal", "Philosophical"]
    tags_html = "".join(f'<span class="tag">{t}</span>' for t in tags)
    facts_html += f'<div class="fact-row"><div class="fact-key">GENRE</div><div class="fact-val">{tags_html}</div></div>'

    downloads_html = ""
    for i, d in enumerate(DOWNLOADS):
        delay = "transition-delay:0.05s;" if i % 2 == 1 else ""
        downloads_html += f"""
    <a href="{d['href']}" class="dl-card reveal" style="display:grid;grid-template-columns:auto 1fr auto;gap:24px;align-items:center;padding:26px 28px;border:0.5px solid rgba(232,230,223,0.18);background:rgba(10,11,13,0.4);{delay}">
      <div class="mono accent" style="font-size:10px;letter-spacing:0.15em;width:48px;">{d['type']}</div>
      <div>
        <div style="font-size:17px;letter-spacing:-0.01em;font-weight:500;margin-bottom:4px;">{d['title']}</div>
        <div class="mono" style="font-size:10px;letter-spacing:0.12em;color:rgba(232,230,223,0.5);">{d['meta']}</div>
      </div>
      <div class="dl-arrow mono" style="font-size:14px;color:rgba(232,230,223,0.6);">→</div>
    </a>"""

    awards_html = ""
    for a in AWARDS:
        awards_html += f"""
      <div style="display:flex;justify-content:space-between;align-items:flex-start;padding:14px 0;border-bottom:0.5px solid rgba(232,230,223,0.1);">
        <div>
          <div style="font-size:17px;letter-spacing:-0.01em;font-weight:500;margin-bottom:4px;">{a['title']}</div>
          <div style="font-size:13px;color:rgba(232,230,223,0.6);">{a['subtitle']}</div>
        </div>
        <div class="mono accent" style="font-size:10px;letter-spacing:0.12em;">{a['year']}</div>
      </div>"""

    press_top_html = ""
    for i, p in enumerate(PRESS_FEATURED):
        delay = "transition-delay:0.05s;" if i > 0 else ""
        press_top_html += f"""
    <a href="{p['url']}" target="_blank" class="press-quote reveal" style="display:block;background:#14171a;padding:36px 32px;{delay}">
      <p class="serif-italic" style="font-size:21px;letter-spacing:-0.015em;line-height:1.4;margin-bottom:24px;">"{p['quote']}"</p>
      <div style="display:flex;justify-content:space-between;align-items:center;padding-top:18px;border-top:0.5px solid rgba(232,230,223,0.15);" class="mono">
        <span style="font-size:11px;letter-spacing:0.12em;">{p['source']} · {p['author'].upper()}</span>
        <span style="font-size:10px;color:rgba(232,230,223,0.5);" class="press-meta">READ →</span>
      </div>
    </a>"""

    press_short_html = ""
    for i, p in enumerate(PRESS_SHORT):
        delay = f"transition-delay:{i*0.05}s;" if i > 0 else ""
        press_short_html += f"""
    <a href="{p['url']}" target="_blank" class="press-quote reveal" style="display:block;background:#14171a;padding:28px 32px;{delay}">
      <p class="serif-italic" style="font-size:16px;letter-spacing:-0.01em;line-height:1.45;margin-bottom:16px;">"{p['quote']}"</p>
      <div class="mono" style="font-size:10px;letter-spacing:0.12em;padding-top:14px;border-top:0.5px solid rgba(232,230,223,0.15);display:flex;justify-content:space-between;">
        <span>{p['source']}</span>
        <span class="press-meta" style="color:rgba(232,230,223,0.5);">READ →</span>
      </div>
    </a>"""

    desc_long_html = "".join(f'<p style="font-size:15px;line-height:1.7;color:rgba(232,230,223,0.75);margin-bottom:18px;">{p}</p>' for p in SITE['description_150'])

    extra_css = """
.dl-card{transition:border-color 0.2s ease, background 0.2s ease}
.dl-card:hover{border-color:rgba(216,255,58,0.5);background:rgba(216,255,58,0.04)}
.dl-card:hover .dl-arrow{color:#d8ff3a;transform:translateX(4px)}
.dl-arrow{transition:transform 0.2s ease, color 0.2s ease}
.shot{position:relative;overflow:hidden;cursor:pointer;aspect-ratio:16/9}
.shot-img{position:absolute;inset:0;transition:transform 0.6s cubic-bezier(0.2,0.6,0.2,1)}
.shot:hover .shot-img{transform:scale(1.04)}
.shot-overlay{position:absolute;inset:0;background:linear-gradient(0deg,rgba(10,11,13,0.85) 0%,transparent 50%);opacity:0;transition:opacity 0.3s ease;display:flex;flex-direction:column;justify-content:flex-end;padding:18px}
.shot:hover .shot-overlay{opacity:1}
.fact-row{display:grid;grid-template-columns:200px 1fr;gap:32px;padding:18px 0;border-bottom:0.5px solid rgba(232,230,223,0.1)}
.fact-row:last-child{border-bottom:none}
.fact-key{font-family:'JetBrains Mono',monospace;font-size:11px;letter-spacing:0.15em;color:rgba(232,230,223,0.5);padding-top:2px}
.fact-val{font-size:15px;color:rgba(232,230,223,0.92);line-height:1.6}
.tag{display:inline-block;padding:5px 11px;border:0.5px solid rgba(232,230,223,0.25);font-size:11px;letter-spacing:0.05em;color:rgba(232,230,223,0.75);margin:0 6px 6px 0;font-family:'JetBrains Mono',monospace}
.press-quote{transition:background 0.3s ease, transform 0.3s ease}
.press-quote:hover{background:#1a1d20;transform:translateY(-3px)}
.press-quote:hover .press-meta{color:#d8ff3a}
.press-meta{transition:color 0.25s ease}
"""

    body = f"""{header(active="press")}

<section style="padding:80px 48px 40px;border-bottom:0.5px solid rgba(232,230,223,0.1);">
  <div class="mono reveal" style="font-size:10px;letter-spacing:0.22em;color:rgba(232,230,223,0.5);margin-bottom:18px;">[ PRESS KIT · v{SITE['build_date']} ]</div>
  <h1 class="reveal" style="font-size:88px;line-height:0.95;letter-spacing:-0.04em;font-weight:500;margin-bottom:28px;max-width:1100px;transition-delay:0.1s;">Materials for the press.</h1>
  <p class="reveal" style="font-size:17px;line-height:1.6;color:rgba(232,230,223,0.7);max-width:680px;margin-bottom:36px;transition-delay:0.2s;">Logos, screenshots, key art, trailers, and a fact sheet for journalists, curators, and broadcasters covering Camoflux. All assets cleared for editorial use.</p>
  <div class="reveal" style="display:flex;gap:14px;align-items:center;transition-delay:0.3s;">
    <a href="#" class="btn-primary">DOWNLOAD ALL ASSETS<span style="font-size:10px;color:rgba(10,11,13,0.6);letter-spacing:0.1em;">.ZIP · 482 MB</span></a>
    <a href="mailto:{SITE['press_email']}" class="btn-secondary">PRESS ENQUIRIES →</a>
  </div>
</section>

{status_bar()}

<section style="padding:120px 48px;">
  <div style="display:grid;grid-template-columns:240px 1fr;gap:64px;">
    <div><div class="section-label reveal">[ 01 / FACT SHEET ]</div></div>
    <div class="reveal" style="max-width:880px;">{facts_html}</div>
  </div>
</section>

<section style="padding:0 48px 120px;">
  <div style="display:grid;grid-template-columns:240px 1fr;gap:64px;">
    <div><div class="section-label reveal">[ 02 / DESCRIPTION ]</div></div>
    <div style="max-width:760px;">
      <div class="reveal">
        <div class="mono" style="font-size:10px;letter-spacing:0.18em;color:rgba(232,230,223,0.5);margin-bottom:14px;">SHORT — 50 WORDS</div>
        <p style="font-size:17px;line-height:1.7;color:rgba(232,230,223,0.85);margin-bottom:48px;">{SITE['description_50']}</p>
      </div>
      <div class="reveal" style="transition-delay:0.1s;">
        <div class="mono" style="font-size:10px;letter-spacing:0.18em;color:rgba(232,230,223,0.5);margin-bottom:14px;">LONG — 150 WORDS</div>
        {desc_long_html}
      </div>
    </div>
  </div>
</section>

<section style="padding:120px 48px;background:#14171a;">
  <div style="display:grid;grid-template-columns:240px 1fr;gap:64px;margin-bottom:48px;">
    <div><div class="section-label reveal">[ 03 / DOWNLOADS ]</div></div>
    <h2 class="reveal" style="font-size:34px;letter-spacing:-0.025em;line-height:1.2;font-weight:400;">Asset packs.</h2>
  </div>
  <div style="display:grid;grid-template-columns:1fr 1fr;gap:14px;">{downloads_html}</div>
</section>

<section style="padding:120px 48px;">
  <div style="display:grid;grid-template-columns:240px 1fr;gap:64px;margin-bottom:48px;">
    <div><div class="section-label reveal">[ 04 / SCREENSHOTS ]</div></div>
    <div>
      <h2 class="reveal" style="font-size:34px;letter-spacing:-0.025em;line-height:1.2;font-weight:400;margin-bottom:14px;">Screen captures.</h2>
      <p class="reveal" style="font-size:14px;color:rgba(232,230,223,0.6);max-width:520px;line-height:1.6;transition-delay:0.1s;">Click any image to download in 4K. All captures rendered in-engine in Unreal Engine 5.</p>
    </div>
  </div>
  <div style="display:grid;grid-template-columns:2fr 1fr;gap:14px;margin-bottom:14px;">
    <div class="shot reveal" style="aspect-ratio:16/9;">
      <div class="shot-img" style="background:url({IMAGES['cavern']}) center/cover no-repeat;"></div>
      <div class="shot-overlay">
        <div class="mono" style="font-size:10px;letter-spacing:0.18em;color:rgba(232,230,223,0.7);margin-bottom:6px;">SS_001 · 3840×2160 · 24.4 MB</div>
        <div style="font-size:15px;letter-spacing:-0.01em;">Mangrove Village Teleporter — Level 01</div>
      </div>
    </div>
    <div style="display:grid;grid-template-rows:1fr 1fr;gap:14px;">
      <div class="shot reveal" style="transition-delay:0.05s;">
        <div class="shot-img" style="background:url({IMAGES['igapo']}) center/cover no-repeat;"></div>
        <div class="shot-overlay">
          <div class="mono" style="font-size:10px;letter-spacing:0.18em;color:rgba(232,230,223,0.7);margin-bottom:6px;">SS_002 · 3840×2160 · 18.1 MB</div>
          <div style="font-size:15px;letter-spacing:-0.01em;">Amazonian Igapó — Butterfly Drone</div>
        </div>
      </div>
      <div class="shot reveal" style="transition-delay:0.1s;">
        <div class="shot-img" style="background:url({IMAGES['mangrove']}) center/cover no-repeat;"></div>
        <div class="shot-overlay">
          <div class="mono" style="font-size:10px;letter-spacing:0.18em;color:rgba(232,230,223,0.7);margin-bottom:6px;">SS_003 · 3840×2160 · 21.7 MB</div>
          <div style="font-size:15px;letter-spacing:-0.01em;">Mangrove Boss — Incendio Igapó</div>
        </div>
      </div>
    </div>
  </div>
</section>

<section style="padding:0 48px 120px;">
  <div style="display:grid;grid-template-columns:240px 1fr;gap:64px;margin-bottom:32px;">
    <div><div class="section-label reveal">[ 05 / VIDEO ]</div></div>
    <h2 class="reveal" style="font-size:34px;letter-spacing:-0.025em;line-height:1.2;font-weight:400;">Official trailer.</h2>
  </div>
  <div class="reveal" style="position:relative;aspect-ratio:16/9;overflow:hidden;background:#000;">
    <iframe width="100%" height="100%" src="https://www.youtube.com/embed/{SITE['youtube_id']}?rel=0" frameborder="0" allow="autoplay; encrypted-media; picture-in-picture" allowfullscreen style="position:absolute;inset:0;"></iframe>
  </div>
</section>

<section style="padding:120px 48px;background:#14171a;">
  <div style="display:grid;grid-template-columns:240px 1fr;gap:64px;margin-bottom:48px;">
    <div><div class="section-label reveal">[ 06 / AWARDS &amp; PRESS ]</div></div>
    <h2 class="reveal" style="font-size:34px;letter-spacing:-0.025em;line-height:1.2;font-weight:400;">Recognition.</h2>
  </div>
  <div class="reveal" style="display:grid;grid-template-columns:240px 1fr;gap:64px;margin-bottom:48px;padding-bottom:36px;border-bottom:0.5px solid rgba(232,230,223,0.1);">
    <div class="mono" style="font-size:10px;letter-spacing:0.18em;color:rgba(232,230,223,0.5);padding-top:6px;">AWARDS</div>
    <div>{awards_html}</div>
  </div>
  <div style="display:grid;grid-template-columns:1fr 1fr;gap:1px;background:rgba(232,230,223,0.1);margin-bottom:1px;">
    {press_top_html}
  </div>
  <div style="display:grid;grid-template-columns:1fr 1fr 1fr;gap:1px;background:rgba(232,230,223,0.1);">
    {press_short_html}
  </div>
</section>

<section style="padding:120px 48px;">
  <div style="display:grid;grid-template-columns:240px 1fr;gap:64px;">
    <div><div class="section-label reveal">[ 07 / STUDIO ]</div></div>
    <div style="max-width:760px;">
      <h2 class="reveal" style="font-size:38px;letter-spacing:-0.025em;line-height:1.1;font-weight:500;margin-bottom:24px;">About {STUDIO['name']}</h2>
      {"".join(f'<p class="reveal" style="font-size:16px;line-height:1.7;color:rgba(232,230,223,0.78);margin-bottom:18px;transition-delay:{i*0.05}s;">{p}</p>' for i, p in enumerate(STUDIO['blurb_long']))}
    </div>
  </div>
</section>

<section style="padding:120px 48px;background:#14171a;">
  <div style="display:grid;grid-template-columns:240px 1fr;gap:64px;">
    <div><div class="section-label reveal">[ 08 / CONTACT ]</div></div>
    <div style="max-width:760px;">
      <h2 class="reveal" style="font-size:38px;letter-spacing:-0.025em;line-height:1.1;font-weight:500;margin-bottom:32px;">Get in touch.</h2>
      <div style="display:grid;grid-template-columns:1fr 1fr;gap:32px;">
        <div class="reveal">
          <div class="mono" style="font-size:10px;letter-spacing:0.18em;color:rgba(232,230,223,0.5);margin-bottom:10px;">PRESS &amp; MEDIA</div>
          <a href="mailto:{SITE['press_email']}" style="font-size:18px;letter-spacing:-0.01em;color:#e8e6df;">{SITE['press_email']}</a>
          <div style="font-size:13px;color:rgba(232,230,223,0.55);margin-top:8px;line-height:1.5;">For interviews, review codes, and editorial coverage.</div>
        </div>
        <div class="reveal" style="transition-delay:0.05s;">
          <div class="mono" style="font-size:10px;letter-spacing:0.18em;color:rgba(232,230,223,0.5);margin-bottom:10px;">BUSINESS &amp; CURATION</div>
          <a href="mailto:{SITE['biz_email']}" style="font-size:18px;letter-spacing:-0.01em;color:#e8e6df;">{SITE['biz_email']}</a>
          <div style="font-size:13px;color:rgba(232,230,223,0.55);margin-top:8px;line-height:1.5;">For partnerships, exhibitions, and acquisitions.</div>
        </div>
      </div>
    </div>
  </div>
</section>

{footer()}"""

    return page_shell(f"Press Kit — {SITE['title']}", body, extra_css=extra_css)


def build_merch():
    """Merch / shop page."""
    cavern = IMAGES['cavern']

    # Build merch grid — items with images get real photos; items without get a styled placeholder
    items_html = ""
    for i, m in enumerate(MERCH):
        delay_idx = i % 3
        delay = f"transition-delay:{delay_idx*0.05}s;" if delay_idx > 0 else ""

        if m.get('image'):
            img_url = IMAGES_SM[m['image']]
            img_block = f"""<div class="img-wrap" style="aspect-ratio:1/1;background:url({img_url}) center/cover no-repeat;position:relative;overflow:hidden;margin-bottom:18px;">
        <div class="img-inner" style="position:absolute;inset:0;background:url({img_url}) center/cover no-repeat;transition:transform 0.8s cubic-bezier(0.2,0.6,0.2,1);"></div>
        <div class="mono accent" style="position:absolute;top:14px;left:14px;font-size:9px;letter-spacing:0.2em;background:rgba(10,11,13,0.7);padding:5px 9px;z-index:2;">{m['category']}</div>
        <div class="mono" style="position:absolute;top:14px;right:14px;font-size:9px;letter-spacing:0.15em;background:rgba(10,11,13,0.7);padding:5px 9px;color:#e8e6df;z-index:2;">{m['status']}</div>
      </div>"""
        else:
            # Styled placeholder for artbook / vinyl / tshirt
            img_block = f"""<div class="img-wrap" style="aspect-ratio:1/1;background:linear-gradient(135deg,#1a1d20,#2c2f33);position:relative;overflow:hidden;margin-bottom:18px;display:flex;align-items:center;justify-content:center;">
        <div class="mono accent" style="position:absolute;top:14px;left:14px;font-size:9px;letter-spacing:0.2em;background:rgba(10,11,13,0.7);padding:5px 9px;z-index:2;">{m['category']}</div>
        <div class="mono" style="position:absolute;top:14px;right:14px;font-size:9px;letter-spacing:0.15em;background:rgba(10,11,13,0.7);padding:5px 9px;color:#e8e6df;z-index:2;">{m['status']}</div>
        <div class="mono" style="font-size:11px;letter-spacing:0.15em;color:rgba(232,230,223,0.4);">[ PRODUCT IMAGE ]</div>
      </div>"""

        # Status color
        status_color = "#d8ff3a" if m['status'] == "AVAILABLE" else ("#e8e6df" if m['status'] == "PRE-ORDER" else "rgba(232,230,223,0.6)")

        items_html += f"""
    <article class="merch-card reveal" style="{delay}">
      {img_block}
      <div style="display:flex;justify-content:space-between;align-items:baseline;margin-bottom:8px;">
        <h3 style="font-size:22px;letter-spacing:-0.02em;font-weight:500;">{m['name']}</h3>
        <div class="mono" style="font-size:15px;letter-spacing:0.05em;color:#e8e6df;">{m['price']}</div>
      </div>
      <div class="mono" style="font-size:10px;letter-spacing:0.15em;color:rgba(232,230,223,0.5);margin-bottom:12px;">{m['edition']} · {m['format']}</div>
      <p style="font-size:14px;color:rgba(232,230,223,0.7);line-height:1.55;margin-bottom:18px;">{m['description']}</p>
      <a href="{m['href']}" class="mono accent" style="font-size:11px;letter-spacing:0.12em;display:inline-block;">
        {'BUY NOW' if m['status'] == 'AVAILABLE' else 'PRE-ORDER' if m['status'] == 'PRE-ORDER' else 'NOTIFY ME'} →
      </a>
    </article>"""

    extra_css = """
.merch-card{transition:transform 0.4s cubic-bezier(0.2,0.6,0.2,1)}
.merch-card:hover{transform:translateY(-6px)}
.merch-card .img-wrap{transition:filter 0.4s ease}
.merch-card:hover .img-wrap{filter:brightness(1.08)}
.merch-card:hover .img-inner{transform:scale(1.05)}
"""

    body = f"""{header(active="merch")}

<section style="position:relative;height:420px;overflow:hidden;">
  <div class="hero-bg" style="background:url({cavern}) center/cover no-repeat;"></div>
  <div style="position:absolute;inset:0;background:linear-gradient(180deg,rgba(10,11,13,0.55) 0%,rgba(10,11,13,0.3) 50%,rgba(10,11,13,0.95) 100%);"></div>
  <div style="position:absolute;top:32px;left:48px;right:48px;display:flex;justify-content:space-between;font-size:10px;letter-spacing:0.18em;color:rgba(232,230,223,0.65);" class="mono">
    <div>[ MERCH // SHOP ]</div>
    <div class="accent status-live">● AVAILABLE</div>
  </div>
  <div class="corner" style="top:24px;left:40px;border-left:1px solid rgba(232,230,223,0.5);border-top:1px solid rgba(232,230,223,0.5);"></div>
  <div class="corner" style="top:24px;right:40px;border-right:1px solid rgba(232,230,223,0.5);border-top:1px solid rgba(232,230,223,0.5);"></div>
  <div class="corner" style="bottom:24px;left:40px;border-left:1px solid rgba(232,230,223,0.5);border-bottom:1px solid rgba(232,230,223,0.5);"></div>
  <div class="corner" style="bottom:24px;right:40px;border-right:1px solid rgba(232,230,223,0.5);border-bottom:1px solid rgba(232,230,223,0.5);"></div>
  <div style="position:absolute;bottom:64px;left:48px;right:48px;">
    <div class="mono reveal" style="font-size:10px;letter-spacing:0.22em;color:rgba(232,230,223,0.7);margin-bottom:18px;">[ PRINTS · APPAREL · BOOKS · VINYL ]</div>
    <h1 class="reveal" style="font-size:80px;line-height:0.95;letter-spacing:-0.04em;font-weight:500;max-width:1000px;transition-delay:0.1s;">Objects from the world.</h1>
  </div>
</section>

{status_bar()}

<section style="padding:80px 48px 48px;">
  <div style="display:grid;grid-template-columns:240px 1fr;gap:64px;">
    <div class="section-label reveal" style="padding-top:14px;">[ ABOUT ]</div>
    <p class="reveal" style="font-size:18px;line-height:1.65;color:rgba(232,230,223,0.8);max-width:760px;transition-delay:0.05s;">Limited-edition prints, soundtracks on vinyl, the making-of monograph, and apparel — all produced in small runs and shipped from Brooklyn. A portion of every sale supports the next episode.</p>
  </div>
</section>

<section style="padding:0 48px 96px;">
  <div style="display:flex;justify-content:space-between;align-items:baseline;margin-bottom:36px;" class="mono">
    <div class="section-label">[ PRODUCTS ]</div>
    <div style="font-size:10px;letter-spacing:0.15em;color:rgba(232,230,223,0.4);">{len(MERCH):02d} ITEMS</div>
  </div>
  <div style="display:grid;grid-template-columns:1fr 1fr 1fr;gap:36px;">
    {items_html}
  </div>
</section>

<section style="padding:96px 48px;background:#14171a;">
  <div style="display:grid;grid-template-columns:240px 1fr;gap:64px;align-items:start;">
    <div class="section-label reveal" style="padding-top:14px;">[ SHIPPING ]</div>
    <div style="max-width:760px;">
      <h2 class="reveal" style="font-size:32px;letter-spacing:-0.025em;line-height:1.15;font-weight:500;margin-bottom:24px;">Made small. Shipped slow.</h2>
      <div style="display:grid;grid-template-columns:1fr 1fr;gap:36px;">
        <div class="reveal">
          <div class="mono" style="font-size:10px;letter-spacing:0.18em;color:rgba(232,230,223,0.5);margin-bottom:8px;">FULFILLMENT</div>
          <p style="font-size:14px;color:rgba(232,230,223,0.78);line-height:1.6;">Prints ship in 5–10 days from Mast Editions in Brooklyn. Pre-orders ship when the run is complete; you'll get a tracked confirmation email.</p>
        </div>
        <div class="reveal" style="transition-delay:0.05s;">
          <div class="mono" style="font-size:10px;letter-spacing:0.18em;color:rgba(232,230,223,0.5);margin-bottom:8px;">INTERNATIONAL</div>
          <p style="font-size:14px;color:rgba(232,230,223,0.78);line-height:1.6;">We ship worldwide. International orders pay actual carrier rates calculated at checkout. Customs fees are buyer's responsibility.</p>
        </div>
      </div>
    </div>
  </div>
</section>

{footer()}"""

    return page_shell(f"Merch — {SITE['title']}", body, extra_css=extra_css)


def build_mobile():
    """Mobile homepage. Wrapped in a phone frame for desktop preview;
    auto-strips frame on actual mobile devices."""
    cavern = IMAGES['cavern']
    yt_id = SITE['youtube_id']
    yt_thumb = YT_THUMB

    # Marquee
    marquee_html = ""
    for _ in range(2):
        for term in SITE['marquee_terms'][:5]:
            marquee_html += f'<span>{term}</span><span class="accent">●</span>'

    # Features stacked
    features_html = ""
    for f in FEATURES:
        if f['image']:
            img_block = f'<div style="aspect-ratio:16/9;background:url({IMAGES_SM[f["image"]]}) center/cover no-repeat;position:relative;margin-bottom:14px;"><div class="mono accent" style="position:absolute;top:10px;left:10px;font-size:9px;letter-spacing:0.2em;background:rgba(10,11,13,0.7);padding:4px 8px;">{f["tag"]}</div></div>'
        else:
            img_block = f'<div style="aspect-ratio:16/9;background:linear-gradient(135deg,#1a1d20,#2c2f33);position:relative;margin-bottom:14px;display:flex;align-items:center;justify-content:center;"><div class="mono accent" style="position:absolute;top:10px;left:10px;font-size:9px;letter-spacing:0.2em;background:rgba(10,11,13,0.7);padding:4px 8px;">{f["tag"]}</div><div class="mono" style="font-size:10px;letter-spacing:0.15em;color:rgba(232,230,223,0.5);">[ PROCESS DOC ]</div></div>'

        features_html += f"""
    <article class="reveal">
      {img_block}
      <div class="mono" style="font-size:9px;letter-spacing:0.18em;color:rgba(232,230,223,0.5);margin-bottom:8px;">{f['category']}</div>
      <h3 style="font-size:22px;letter-spacing:-0.025em;margin-bottom:8px;font-weight:500;">{f['title']}</h3>
      <p style="font-size:14px;color:rgba(232,230,223,0.65);line-height:1.55;">{f['body']}</p>
    </article>"""

    # Press cards as horizontal scroll
    press_cards = ""
    for p in PRESS_FEATURED:
        press_cards += f"""
      <a href="{p['url']}" target="_blank" class="press-card-m" style="background:#0a0b0d;padding:22px;width:280px;flex-shrink:0;border:0.5px solid rgba(232,230,223,0.1);display:block;">
        <p class="serif-italic" style="font-size:16px;letter-spacing:-0.01em;line-height:1.4;margin-bottom:18px;">"{p['quote']}"</p>
        <div style="display:flex;justify-content:space-between;padding-top:14px;border-top:0.5px solid rgba(232,230,223,0.15);" class="mono">
          <span style="font-size:10px;letter-spacing:0.12em;">{p['source']}</span>
          <span style="font-size:9px;color:rgba(232,230,223,0.5);" class="press-meta">{p['date']} · READ →</span>
        </div>
      </a>"""

    for p in PRESS_SHORT:
        press_cards += f"""
      <a href="{p['url']}" target="_blank" class="press-card-m" style="background:#0a0b0d;padding:22px;width:240px;flex-shrink:0;border:0.5px solid rgba(232,230,223,0.1);display:block;">
        <p class="serif-italic" style="font-size:15px;letter-spacing:-0.01em;line-height:1.45;margin-bottom:16px;">"{p['quote']}"</p>
        <div class="mono" style="font-size:10px;letter-spacing:0.12em;padding-top:12px;border-top:0.5px solid rgba(232,230,223,0.15);display:flex;justify-content:space-between;">
          <span>{p['source']}</span>
          <span class="press-meta" style="color:rgba(232,230,223,0.5);">READ →</span>
        </div>
      </a>"""

    # Merch teaser - 3 items with images, horizontal scroll
    merch_with_images = [m for m in MERCH if m.get('image')][:3]
    merch_cards = ""
    for m in merch_with_images:
        img_url = IMAGES_SM[m['image']]
        merch_cards += f"""
      <a href="merch.html" class="merch-card-m" style="display:block;width:240px;flex-shrink:0;">
        <div style="aspect-ratio:1/1;background:url({img_url}) center/cover no-repeat;position:relative;margin-bottom:12px;">
          <div class="mono accent" style="position:absolute;top:10px;left:10px;font-size:9px;letter-spacing:0.2em;background:rgba(10,11,13,0.7);padding:4px 8px;">{m['category']}</div>
        </div>
        <div style="display:flex;justify-content:space-between;align-items:baseline;margin-bottom:4px;">
          <h3 style="font-size:15px;letter-spacing:-0.015em;font-weight:500;">{m['name']}</h3>
          <div class="mono" style="font-size:12px;letter-spacing:0.05em;">{m['price']}</div>
        </div>
        <div class="mono" style="font-size:9px;letter-spacing:0.12em;color:rgba(232,230,223,0.5);">{m['edition']}</div>
      </a>"""

    nav_html_mobile = ""
    for item in NAV:
        nav_html_mobile += f'<a href="{item["href"]}" style="font-size:32px;letter-spacing:-0.025em;font-weight:500;">{item["label"].title()}</a>'

    # Mobile-specific CSS — built fresh, doesn't share desktop minimum-width
    mobile_css = """
*{margin:0;padding:0;box-sizing:border-box}
html{scroll-behavior:smooth}
html,body{background:#0a0b0d;color:#e8e6df;font-family:'Inter',system-ui,sans-serif;-webkit-font-smoothing:antialiased}
body{overflow-x:hidden}
.mono{font-family:'JetBrains Mono',ui-monospace,monospace}
.serif-italic{font-family:Georgia,serif;font-style:italic}
.corner{position:absolute;width:10px;height:10px;pointer-events:none}
.accent{color:#d8ff3a}
.section-label{font-family:'JetBrains Mono',monospace;font-size:9px;letter-spacing:0.22em;color:rgba(232,230,223,0.45)}
a{color:inherit;text-decoration:none}
em{font-family:Georgia,serif;font-style:italic;font-weight:400}
.btn-primary{background:#d8ff3a;color:#0a0b0d;padding:14px 22px;font-size:12px;letter-spacing:0.08em;font-weight:500;display:inline-flex;align-items:center;justify-content:center;gap:8px;cursor:pointer;border:none;font-family:'Inter',sans-serif;width:100%;text-align:center}
.btn-secondary{border:0.5px solid rgba(232,230,223,0.5);background:rgba(232,230,223,0.06);padding:14px 22px;font-size:12px;letter-spacing:0.08em;display:inline-flex;align-items:center;justify-content:center;gap:8px;cursor:pointer;color:#e8e6df;font-family:'Inter',sans-serif;width:100%;text-align:center;transition:background 0.25s ease, color 0.25s ease, box-shadow 0.25s ease, border-color 0.25s ease}
.btn-secondary:active{background:#e8e6df;color:#0a0b0d;border-color:#e8e6df;box-shadow:0 0 32px rgba(232,230,223,0.45)}
.btn-secondary:active .play-arrow{border-left-color:#0a0b0d}
.play-arrow{transition:border-left-color 0.25s ease}
@keyframes pulse-dot{0%,100%{opacity:1;transform:scale(1)}50%{opacity:0.4;transform:scale(0.85)}}
.rec-dot{display:inline-block;animation:pulse-dot 1.6s ease-in-out infinite}
@keyframes pulse-status{0%,100%{opacity:1}50%{opacity:0.5}}
.status-live{animation:pulse-status 2s ease-in-out infinite}
@keyframes ken-burns{0%{transform:scale(1.0)}50%{transform:scale(1.1)}100%{transform:scale(1.0)}}
.hero-bg{position:absolute;inset:0;animation:ken-burns 24s ease-in-out infinite;will-change:transform}
@keyframes marquee{0%{transform:translateX(0)}100%{transform:translateX(-50%)}}
.marquee{display:flex;gap:32px;animation:marquee 30s linear infinite;width:max-content}
.marquee-wrap{overflow:hidden;mask:linear-gradient(90deg,transparent,#000 8%,#000 92%,transparent)}
.reveal{opacity:0;transform:translateY(16px);transition:opacity 0.7s cubic-bezier(0.2,0.6,0.2,1), transform 0.7s cubic-bezier(0.2,0.6,0.2,1)}
.reveal.in{opacity:1;transform:translateY(0)}
.menu-overlay{position:fixed;inset:0;background:rgba(10,11,13,0.97);backdrop-filter:blur(20px);z-index:100;display:flex;flex-direction:column;padding:80px 24px 24px;transform:translateX(100%);transition:transform 0.3s cubic-bezier(0.2,0.6,0.2,1);gap:24px}
.menu-overlay.open{transform:translateX(0)}
.hamburger{width:28px;height:18px;position:relative;cursor:pointer;background:none;border:none;padding:0}
.hamburger span{display:block;position:absolute;height:1.5px;width:100%;background:#e8e6df;left:0;transition:all 0.3s ease}
.hamburger span:nth-child(1){top:0}
.hamburger span:nth-child(2){top:50%;transform:translateY(-50%)}
.hamburger span:nth-child(3){bottom:0}
.hamburger.open{z-index:200}
.hamburger.open span:nth-child(1){top:50%;transform:translateY(-50%) rotate(45deg)}
.hamburger.open span:nth-child(2){opacity:0}
.hamburger.open span:nth-child(3){bottom:50%;transform:translateY(50%) rotate(-45deg)}
.phone-frame{max-width:430px;margin:24px auto;background:#0a0b0d;border:8px solid #1a1d20;border-radius:48px;overflow:hidden;box-shadow:0 40px 80px -20px rgba(0,0,0,0.6);position:relative}
.phone-frame::before{content:'';position:absolute;top:0;left:50%;transform:translateX(-50%);width:120px;height:28px;background:#1a1d20;border-radius:0 0 18px 18px;z-index:200}
.phone-content{height:920px;overflow-y:auto;overflow-x:hidden;-webkit-overflow-scrolling:touch}
.phone-content::-webkit-scrollbar{display:none}
.preview-wrapper{padding:24px;background:linear-gradient(135deg,#1a1d20,#2c2f33);min-height:100vh;display:flex;flex-direction:column;align-items:center;justify-content:flex-start}
.preview-label{color:rgba(232,230,223,0.6);font-family:'JetBrains Mono',monospace;font-size:11px;letter-spacing:0.18em;margin-bottom:8px;text-transform:uppercase}
.scroll-row{overflow-x:auto;-webkit-overflow-scrolling:touch;scrollbar-width:none}
.scroll-row::-webkit-scrollbar{display:none}
@media (max-width:480px){.preview-wrapper{padding:0;background:#0a0b0d}.preview-label{display:none}.phone-frame{margin:0;border:none;border-radius:0}.phone-frame::before{display:none}.phone-content{height:auto;overflow:visible}}
@media (prefers-reduced-motion:reduce){*,*::before,*::after{animation-duration:0.01ms !important;animation-iteration-count:1 !important;transition-duration:0.01ms !important}.hero-bg{animation:none}.reveal{opacity:1;transform:none}}
"""

    body_inner = f"""
<header style="position:sticky;top:0;z-index:60;display:flex;justify-content:space-between;align-items:center;padding:16px 20px;background:rgba(10,11,13,0.85);backdrop-filter:blur(12px);border-bottom:0.5px solid rgba(232,230,223,0.1);" class="mono">
  <div style="display:flex;align-items:center;gap:8px;">
    <div class="rec-dot" style="width:6px;height:6px;background:#d8ff3a;border-radius:50%;"></div>
    <a href="index.html" style="font-size:11px;font-weight:500;letter-spacing:0.05em;">CAMOFLUX</a>
    <span style="color:rgba(232,230,223,0.4);font-size:10px;letter-spacing:0.18em;margin-left:8px;">[ PART ONE ]</span>
  </div>
  <button class="hamburger" id="menu-btn" aria-label="Menu">
    <span></span><span></span><span></span>
  </button>
</header>

<div class="menu-overlay" id="menu">
  <div class="mono" style="font-size:9px;letter-spacing:0.22em;color:rgba(232,230,223,0.45);">[ NAVIGATION ]</div>
  <nav style="display:flex;flex-direction:column;gap:24px;flex:1;">
    {nav_html_mobile}
  </nav>
  <div style="border-top:0.5px solid rgba(232,230,223,0.15);padding-top:24px;">
    <div class="mono" style="font-size:9px;letter-spacing:0.22em;color:rgba(232,230,223,0.45);margin-bottom:14px;">[ FOLLOW ]</div>
    <div style="display:flex;gap:18px;font-family:'JetBrains Mono',monospace;font-size:10px;letter-spacing:0.12em;color:rgba(232,230,223,0.6);">
      <a href="{SOCIAL['youtube']}" target="_blank">YT</a>
      <a href="{SOCIAL['instagram']}" target="_blank">IG</a>
      <a href="{SOCIAL['x']}" target="_blank">X</a>
      <a href="{SOCIAL['tiktok']}" target="_blank">TT</a>
    </div>
  </div>
  <a href="{SITE['steam_url']}" target="_blank" class="btn-primary">WISHLIST ON STEAM →</a>
</div>

<section style="position:relative;height:560px;overflow:hidden;">
  <div class="hero-bg" style="background:url({cavern}) center/cover no-repeat;"></div>
  <div style="position:absolute;inset:0;background:linear-gradient(180deg,rgba(10,11,13,0.5) 0%,rgba(10,11,13,0.2) 30%,rgba(10,11,13,0.5) 65%,rgba(10,11,13,0.95) 100%);"></div>
  <div style="position:absolute;top:18px;left:20px;right:20px;display:flex;justify-content:space-between;font-size:9px;letter-spacing:0.18em;color:rgba(232,230,223,0.65);" class="mono">
    <div>[ PART_01 ]</div>
    <div class="accent status-live">● REC</div>
  </div>
  <div class="corner" style="top:14px;left:16px;border-left:1px solid rgba(232,230,223,0.5);border-top:1px solid rgba(232,230,223,0.5);"></div>
  <div class="corner" style="top:14px;right:16px;border-right:1px solid rgba(232,230,223,0.5);border-top:1px solid rgba(232,230,223,0.5);"></div>
  <div class="corner" style="bottom:14px;left:16px;border-left:1px solid rgba(232,230,223,0.5);border-bottom:1px solid rgba(232,230,223,0.5);"></div>
  <div class="corner" style="bottom:14px;right:16px;border-right:1px solid rgba(232,230,223,0.5);border-bottom:1px solid rgba(232,230,223,0.5);"></div>
  <div style="position:absolute;bottom:32px;left:24px;right:24px;">
    <div class="mono" style="font-size:9px;letter-spacing:0.22em;color:rgba(232,230,223,0.65);margin-bottom:14px;">EPISODIC EXPLORATION · 2026</div>
    <h1 style="font-size:42px;line-height:0.98;letter-spacing:-0.035em;font-weight:500;margin-bottom:16px;">{SITE['tagline']}</h1>
    <p style="font-size:13px;line-height:1.55;color:rgba(232,230,223,0.78);margin-bottom:18px;">{SITE['description_short']}</p>
    <div style="display:flex;flex-direction:column;gap:8px;">
      <a href="{SITE['steam_url']}" target="_blank" class="btn-primary">WISHLIST ON STEAM →</a>
      <a href="https://www.youtube.com/watch?v={yt_id}" target="_blank" class="btn-secondary">
        <div class="play-arrow" style="width:0;height:0;border-left:6px solid #e8e6df;border-top:4px solid transparent;border-bottom:4px solid transparent;"></div>
        WATCH TRAILER · {SITE['trailer_duration']}
      </a>
    </div>
  </div>
</section>

<section style="padding:14px 20px;background:#14171a;display:flex;justify-content:space-between;font-size:9px;letter-spacing:0.15em;color:rgba(232,230,223,0.55);border-bottom:0.5px solid rgba(232,230,223,0.08);" class="mono">
  <span>STATUS: <span class="accent">{SITE['status']}</span></span>
  <span>EP 0{SITE['episode_current']}/{'I' * SITE['episode_total']} · {SITE['engine']}</span>
</section>

<section style="padding:24px 20px;background:#0f1012;border-bottom:0.5px solid rgba(232,230,223,0.08);">
  <div class="section-label" style="margin-bottom:6px;">[ NOW SHOWING ]</div>
  <div style="font-size:16px;letter-spacing:-0.01em;font-weight:500;margin-bottom:10px;">{EXHIBITION['subtitle']}</div>
  <div class="serif-italic" style="font-size:13px;color:rgba(232,230,223,0.7);line-height:1.55;margin-bottom:14px;">"{EXHIBITION['press_quote']}"</div>
  <a href="exhibition.html" class="mono accent" style="font-size:10px;letter-spacing:0.15em;">VISIT · {EXHIBITION['dates'].upper()} →</a>
</section>

<section class="marquee-wrap" style="padding:14px 0;background:#0a0b0d;border-bottom:0.5px solid rgba(232,230,223,0.08);">
  <div class="marquee mono" style="font-size:11px;letter-spacing:0.15em;color:rgba(232,230,223,0.45);">
    {marquee_html}
  </div>
</section>

<section style="padding:56px 24px;">
  <div class="section-label reveal" style="margin-bottom:18px;">[ PART_01 ]</div>
  <h2 class="reveal" style="font-size:34px;letter-spacing:-0.03em;line-height:1.05;font-weight:500;margin-bottom:18px;">You are <em>The Other</em>.</h2>
  <p class="reveal" style="font-size:14px;line-height:1.65;color:rgba(232,230,223,0.7);">A third-person ontology where landscapes, bodies, and technology fuse. Adapt through vibrational terraforming, camouflage, and electromagnetic sensors. Choose to destroy bosses — or engage with them.</p>
</section>

<section style="padding:0 24px 56px;">
  <div style="display:flex;justify-content:space-between;align-items:baseline;margin-bottom:24px;" class="mono">
    <div class="section-label">[ FEATURES ]</div>
    <div style="font-size:9px;letter-spacing:0.15em;color:rgba(232,230,223,0.4);">{len(FEATURES):02d} SYSTEMS</div>
  </div>
  <div style="display:flex;flex-direction:column;gap:32px;">
    {features_html}
  </div>
</section>

<section style="padding:0 24px 56px;">
  <div style="display:flex;justify-content:space-between;align-items:baseline;margin-bottom:18px;" class="mono">
    <div class="section-label">[ TRAILER ]</div>
    <div style="font-size:9px;letter-spacing:0.15em;color:rgba(232,230,223,0.4);">{SITE['trailer_duration']} · 4K</div>
  </div>
  <a href="https://www.youtube.com/watch?v={yt_id}" target="_blank" style="position:relative;aspect-ratio:16/9;overflow:hidden;display:block;background:url({yt_thumb}) center/cover no-repeat;">
    <div style="position:absolute;inset:0;background:linear-gradient(180deg,transparent 50%,rgba(10,11,13,0.7) 100%);"></div>
    <div class="mono" style="position:absolute;top:12px;left:12px;right:12px;display:flex;justify-content:space-between;font-size:9px;letter-spacing:0.15em;color:rgba(232,230,223,0.7);">
      <span class="accent status-live">● LIVE FEED</span>
      <span>YT://{yt_id}</span>
    </div>
    <div style="position:absolute;top:50%;left:50%;transform:translate(-50%,-50%);width:60px;height:60px;border:1px solid rgba(232,230,223,0.85);border-radius:50%;display:flex;align-items:center;justify-content:center;background:rgba(10,11,13,0.4);">
      <div style="width:0;height:0;border-left:14px solid #e8e6df;border-top:9px solid transparent;border-bottom:9px solid transparent;margin-left:4px;"></div>
    </div>
  </a>
</section>

<section style="padding:56px 0;background:#14171a;">
  <div style="padding:0 24px;margin-bottom:20px;">
    <div class="section-label reveal" style="margin-bottom:14px;">[ PRESS ]</div>
    <h2 class="reveal" style="font-size:24px;letter-spacing:-0.025em;line-height:1.2;font-weight:400;">Critics on the practice.</h2>
  </div>
  <div class="scroll-row" style="padding:0 24px 8px;">
    <div style="display:flex;gap:14px;width:max-content;">
      {press_cards}
    </div>
  </div>
  <div style="padding:18px 24px 0;text-align:right;">
    <a href="presskit.html" class="mono accent" style="font-size:10px;letter-spacing:0.15em;">FULL PRESS KIT →</a>
  </div>
</section>

<section style="padding:56px 0;">
  <div style="padding:0 24px;margin-bottom:20px;display:flex;justify-content:space-between;align-items:baseline;" class="mono">
    <div class="section-label">[ MERCH ]</div>
    <a href="merch.html" class="accent" style="font-size:10px;letter-spacing:0.15em;">SHOP ALL →</a>
  </div>
  <div class="scroll-row" style="padding:0 24px 8px;">
    <div style="display:flex;gap:16px;width:max-content;">
      {merch_cards}
    </div>
  </div>
</section>

<section style="padding:56px 24px;">
  <div class="section-label reveal" style="margin-bottom:14px;">[ STUDIO ]</div>
  <h2 class="reveal" style="font-size:28px;letter-spacing:-0.025em;line-height:1.1;font-weight:500;margin-bottom:16px;">{STUDIO['name']}</h2>
  <p class="reveal" style="font-size:14px;color:rgba(232,230,223,0.7);line-height:1.65;margin-bottom:18px;">{STUDIO['blurb_short']}</p>
  <a href="#" class="mono accent" style="font-size:10px;letter-spacing:0.15em;">ABOUT THE STUDIO →</a>
</section>

<section style="position:relative;padding:72px 24px;text-align:center;overflow:hidden;">
  <div class="hero-bg" style="background:url({cavern}) center/cover no-repeat;animation-duration:32s;"></div>
  <div style="position:absolute;inset:0;background:rgba(10,11,13,0.78);"></div>
  <div class="corner" style="top:18px;left:20px;border-left:1px solid rgba(232,230,223,0.5);border-top:1px solid rgba(232,230,223,0.5);"></div>
  <div class="corner" style="top:18px;right:20px;border-right:1px solid rgba(232,230,223,0.5);border-top:1px solid rgba(232,230,223,0.5);"></div>
  <div class="corner" style="bottom:18px;left:20px;border-left:1px solid rgba(232,230,223,0.5);border-bottom:1px solid rgba(232,230,223,0.5);"></div>
  <div class="corner" style="bottom:18px;right:20px;border-right:1px solid rgba(232,230,223,0.5);border-bottom:1px solid rgba(232,230,223,0.5);"></div>
  <div style="position:relative;">
    <div class="mono" style="font-size:10px;letter-spacing:0.22em;color:rgba(232,230,223,0.55);margin-bottom:18px;">[ TRANSMISSION ENDS ]</div>
    <h2 style="font-size:44px;letter-spacing:-0.035em;line-height:1;margin-bottom:16px;font-weight:500;">Wishlist now.</h2>
    <p style="font-size:13px;color:rgba(232,230,223,0.7);margin-bottom:24px;">Get notified the moment Camoflux releases.</p>
    <a href="{SITE['steam_url']}" target="_blank" class="btn-primary">WISHLIST ON STEAM →</a>
  </div>
</section>

<footer style="padding:32px 24px;background:#0a0b0d;border-top:0.5px solid rgba(232,230,223,0.1);" class="mono">
  <div style="display:flex;align-items:center;gap:8px;margin-bottom:12px;">
    <div class="rec-dot" style="width:6px;height:6px;background:#d8ff3a;border-radius:50%;"></div>
    <div style="font-size:11px;font-weight:500;letter-spacing:0.05em;">CAMOFLUX <span style="color:rgba(232,230,223,0.4);">/ LEVELS &amp; BOSSES</span></div>
  </div>
  <div style="color:rgba(232,230,223,0.45);font-size:9px;line-height:1.7;letter-spacing:0.05em;margin-bottom:24px;">© LEVELS &amp; BOSSES · OTRO INVENTARIO</div>
  <div style="display:grid;grid-template-columns:1fr 1fr;gap:24px;">
    <div>
      <div style="font-size:9px;letter-spacing:0.18em;color:rgba(232,230,223,0.4);margin-bottom:10px;">[ FOLLOW ]</div>
      <div style="font-size:10px;line-height:1.9;color:rgba(232,230,223,0.7);letter-spacing:0.05em;">
        <a href="{SOCIAL['youtube']}" target="_blank">YOUTUBE</a><br/>
        <a href="{SOCIAL['instagram']}" target="_blank">INSTAGRAM</a><br/>
        <a href="{SOCIAL['x']}" target="_blank">X / THREADS</a><br/>
        <a href="{SOCIAL['tiktok']}" target="_blank">TIKTOK</a>
      </div>
    </div>
    <div>
      <div style="font-size:9px;letter-spacing:0.18em;color:rgba(232,230,223,0.4);margin-bottom:10px;">[ CONTACT ]</div>
      <div style="font-size:10px;line-height:1.9;color:rgba(232,230,223,0.7);letter-spacing:0.05em;">PRESS@<br/>LEVELSANDBOSSES<br/>.COM</div>
    </div>
  </div>
</footer>"""

    full_body = f"""<div class="preview-wrapper">
  <div class="preview-label">CAMOFLUX · MOBILE PREVIEW · 414 × 920</div>
  <div class="phone-frame">
    <div class="phone-content" id="content">
      {body_inner}
    </div>
  </div>
</div>

<script>
const reveals = document.querySelectorAll('.reveal');
const root = document.getElementById('content');
const io = new IntersectionObserver((entries) => {{
  entries.forEach(e => {{
    if (e.isIntersecting) {{
      e.target.classList.add('in');
      io.unobserve(e.target);
    }}
  }});
}}, {{ threshold: 0.1, rootMargin: '0px', root: root }});
reveals.forEach(el => io.observe(el));

const btn = document.getElementById('menu-btn');
const menu = document.getElementById('menu');
btn.addEventListener('click', () => {{
  btn.classList.toggle('open');
  menu.classList.toggle('open');
}});
menu.querySelectorAll('a').forEach(a => a.addEventListener('click', () => {{
  btn.classList.remove('open');
  menu.classList.remove('open');
}}));

if (window.innerWidth <= 480) {{
  document.body.classList.add('standalone-mobile');
}}
</script>"""

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1, maximum-scale=1">
<title>{SITE['title']} — Mobile</title>
<meta name="description" content="{SITE['description_short']}">
<link rel="icon" type="image/png" sizes="32x32" href="images/favicon-32.png">
<link rel="icon" type="image/png" sizes="16x16" href="images/favicon-16.png">
<link rel="apple-touch-icon" sizes="180x180" href="images/favicon-180.png">
<meta property="og:title" content="{SITE['title']} — {SITE['subtitle']}">
<meta property="og:description" content="{SITE['description_short']}">
<meta property="og:image" content="images/og.jpg">
<link rel="preload" as="image" href="images/cavern.jpg" fetchpriority="high">
{fonts()}
<style>{mobile_css}</style>
</head>
<body>
{full_body}
</body>
</html>"""


# ---- Run ----

def write(name, html):
    path = OUT / name
    with open(path, "w") as f:
        f.write(html)
    print(f"  ✓ {name}  ({len(html)/1024:.0f} kb)")
    return path

print(f"Building Camoflux site...")
print(f"  Output dir: {OUT}")
print()

write("index.html", build_homepage())
write("presskit.html", build_presskit())
write("exhibition.html", build_exhibition())
write("devlog.html", build_devlog_index())
write("merch.html", build_merch())
write("mobile.html", build_mobile())

print("  Devlog posts:")
for post in DEVLOG:
    write(f"devlog-{post['id']}.html", build_devlog_post(post))

# Sync images/ from project root into site/images/
import shutil
src_images = ROOT / 'images'
dst_images = OUT / 'images'
if src_images.exists():
    if dst_images.exists():
        shutil.rmtree(dst_images)
    shutil.copytree(src_images, dst_images)
    n_files = len(list(dst_images.iterdir()))
    total = sum(f.stat().st_size for f in dst_images.iterdir() if f.is_file())
    print(f"  ✓ images/  ({n_files} files, {total/1024/1024:.2f} MB)")
else:
    print(f"  ! images/ not found at {src_images} — run export_images.py first")

print()
print("Build complete.")
