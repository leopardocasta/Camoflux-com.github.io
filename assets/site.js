/* Camoflux site behaviors. Each block is independent and no-ops if its markup is absent. */
(() => {
  const $$ = (sel, root = document) => Array.from(root.querySelectorAll(sel));

  /* ---- Lazy media with skeleton → loaded / error states ---- */
  const loadMedia = (el) => {
    const map = window.__IMG || {};                 // filled only in standalone preview files
    const src = map[el.dataset.src] || el.dataset.src;
    if (!src || el.dataset.state) return;
    el.dataset.state = 'loading';
    const img = new Image();
    img.onload = () => {
      el.querySelector('.media__img').style.backgroundImage = `url("${img.src}")`;
      el.classList.add('is-loaded');
      el.dataset.state = 'loaded';
    };
    img.onerror = () => {
      const fb = (window.__IMG || {})[el.dataset.fallback] || el.dataset.fallback;
      if (fb && img.src !== fb && !img.dataset.triedFallback) { img.dataset.triedFallback = '1'; img.src = fb; return; }   // e.g. YouTube thumbnail blocked
      el.classList.add('is-error'); el.dataset.state = 'error';
    };
    img.src = src;
  };
  const media = $$('.media[data-src]');
  if ('IntersectionObserver' in window) {
    const io = new IntersectionObserver((entries) => {
      entries.forEach((e) => { if (e.isIntersecting) { loadMedia(e.target); io.unobserve(e.target); } });
    }, { rootMargin: '300px 0px' });
    media.forEach((el) => io.observe(el));
  } else {
    media.forEach(loadMedia);
  }

  /* ---- Lightbox: every image opens large on click (or Enter), except inside links ---- */
  const lb = document.getElementById('lightbox');
  if (lb) {
    const stage = lb.querySelector('.shotbox__stage'), capEl = lb.querySelector('.shotbox__cap'), closeBtn = lb.querySelector('button');
    let lastFocus = null;
    const open = (src, cap, alt) => {
      lastFocus = document.activeElement; stage.innerHTML = '';
      stage.appendChild(Object.assign(document.createElement('img'), { src, alt: alt || cap || '' }));
      capEl.textContent = cap || ''; lb.dataset.open = 'true'; document.body.style.overflow = 'hidden'; closeBtn.focus();
    };
    const close = () => { lb.dataset.open = 'false'; stage.innerHTML = ''; document.body.style.overflow = ''; if (lastFocus) lastFocus.focus(); };
    const zoomables = $$('[data-full]').filter((el) => !el.closest('a'));
    zoomables.forEach((el) => {
      el.classList.add('is-zoomable'); el.setAttribute('tabindex', '0'); el.setAttribute('role', 'button');
      el.setAttribute('aria-label', 'Open image: ' + (el.dataset.caption || el.getAttribute('alt') || ''));
      const go = () => { const img = el.querySelector('.media__img'); open((window.__IMG && window.__IMG[el.dataset.full]) || el.dataset.full, el.dataset.caption, img ? img.getAttribute('aria-label') : el.getAttribute('alt')); };
      el.addEventListener('click', go);
      el.addEventListener('keydown', (ev) => { if (ev.key === 'Enter' || ev.key === ' ') { ev.preventDefault(); go(); } });
    });
    lb.addEventListener('click', (ev) => { if (ev.target === lb || ev.target.closest('button')) close(); });
    document.addEventListener('keydown', (ev) => { if (ev.key === 'Escape' && lb.dataset.open === 'true') close(); });
  }

  /* ---- Gameplay clips: play only while on screen ---- */
  const clips = $$('video.clip');
  clips.forEach((v) => $$('source', v).forEach((s) => {   // embedded clips in previews play from blob: URLs
    const u = s.getAttribute('src');
    if (u && u.startsWith('data:')) { const [h, b] = u.split(','); const bin = atob(b); const a = new Uint8Array(bin.length); for (let i = 0; i < bin.length; i++) a[i] = bin.charCodeAt(i); s.src = URL.createObjectURL(new Blob([a], { type: h.slice(5).split(';')[0] })); }
  }));
  if ('IntersectionObserver' in window && clips.length) {
    const cio = new IntersectionObserver((es) => es.forEach((en) => { const v = en.target; if (en.isIntersecting) { if (v.preload === 'none') { v.preload = 'auto'; v.load(); } v.play().catch(() => {}); } else v.pause(); }), { threshold: 0.25 });
    clips.forEach((v) => cio.observe(v));
  }

  /* ---- Mobile menu ---- */
  const header = document.querySelector('.site-header');
  const toggle = document.querySelector('.menu-toggle');
  if (header && toggle) {
    const setOpen = (open) => {
      header.dataset.open = String(open);
      toggle.setAttribute('aria-expanded', String(open));
      toggle.setAttribute('aria-label', open ? 'Close menu' : 'Open menu');
    };
    toggle.addEventListener('click', () => setOpen(header.dataset.open !== 'true'));
    $$('.nav a', header).forEach((a) => a.addEventListener('click', () => setOpen(false)));
    document.addEventListener('keydown', (e) => { if (e.key === 'Escape') setOpen(false); });
  }

  /* ---- Trailer modal: button shows progress until the player has loaded ---- */
  const modal = document.getElementById('trailer-modal');
  if (modal) {
    const frame = modal.querySelector('.modal__frame');
    const iframe = modal.querySelector('iframe');
    const closeBtn = modal.querySelector('.modal__close');
    let opener = null;

    const close = () => {
      modal.dataset.open = 'false';
      frame.classList.remove('is-ready');
      iframe.removeAttribute('src');
      document.body.style.overflow = '';
      if (opener) { opener.removeAttribute('aria-busy'); opener.focus(); }
    };
    const open = (btn) => {
      opener = btn;
      btn.setAttribute('aria-busy', 'true');
      modal.dataset.open = 'true';
      document.body.style.overflow = 'hidden';
      iframe.onload = () => { frame.classList.add('is-ready'); btn.removeAttribute('aria-busy'); };
      iframe.src = `https://www.youtube-nocookie.com/embed/${modal.dataset.video}?autoplay=1&rel=0`;
      closeBtn.focus();
    };
    $$('[data-trailer]').forEach((btn) => btn.addEventListener('click', (e) => { e.preventDefault(); open(btn); }));
    closeBtn.addEventListener('click', close);
    modal.addEventListener('click', (e) => { if (e.target === modal) close(); });
    document.addEventListener('keydown', (e) => { if (e.key === 'Escape' && modal.dataset.open === 'true') close(); });
  }

  /* ---- Rails: snap carousel on small screens with working prev/next + counter ---- */
  $$('.rail').forEach((rail) => {
    const track = rail.querySelector('.rail__track');
    const prev = rail.querySelector('[data-dir="-1"]');
    const next = rail.querySelector('[data-dir="1"]');
    const count = rail.querySelector('.rail__count');
    const items = Array.from(track.children);
    if (!prev || !next || !items.length) return;
    const pad = (n) => String(n).padStart(2, '0');
    const step = () => (items[1] ? items[1].offsetLeft - items[0].offsetLeft : track.clientWidth) || 1;
    const current = () => {
      if (track.scrollLeft + track.clientWidth >= track.scrollWidth - 2) return items.length - 1;
      return Math.min(items.length - 1, Math.round(track.scrollLeft / step()));
    };
    const update = () => {
      const i = current();
      count.textContent = `${pad(i + 1)} / ${pad(items.length)}`;
      prev.disabled = i === 0;
      next.disabled = i === items.length - 1;
    };
    const go = (dir) => {
      const i = Math.min(items.length - 1, Math.max(0, current() + dir));
      track.scrollTo({ left: items[i].offsetLeft - items[0].offsetLeft, behavior: 'smooth' });
    };
    prev.addEventListener('click', () => go(-1));
    next.addEventListener('click', () => go(1));
    let t;
    track.addEventListener('scroll', () => { clearTimeout(t); t = setTimeout(update, 60); }, { passive: true });
    window.addEventListener('resize', update);
    update();
  });

  /* ---- Mailchimp signup: idle → submitting → success / error, shown in place ----
     Uses Mailchimp's JSONP endpoint (post-json) so the real response message can be shown. */
  $$('form[data-mailchimp]').forEach((form) => {
    const btn = form.querySelector('button');
    const email = form.querySelector('input[type="email"]');
    const msg = form.parentElement.querySelector('.form-msg');
    const label = btn.textContent;
    const say = (state, text) => { msg.dataset.state = state; msg.textContent = text; };
    const clean = (s) => String(s || '').replace(/<[^>]*>/g, '').replace(/^\d+\s*-\s*/, '').replace(/\s*Click here.*$/i, '').trim();
    const setBusy = (busy) => {
      btn.disabled = busy;
      if (busy) { btn.setAttribute('aria-busy', 'true'); btn.textContent = 'Subscribing'; }
      else { btn.removeAttribute('aria-busy'); btn.textContent = label; }
    };

    form.addEventListener('submit', (e) => {
      e.preventDefault();
      if (!email.value || !email.checkValidity()) { say('error', 'Enter a valid email address.'); email.focus(); return; }
      setBusy(true); say('', '');
      const cb = 'mc_cb_' + Date.now();
      const params = new URLSearchParams(new FormData(form));
      params.set('c', cb);
      const url = form.action.replace('/post?', '/post-json?') + '&' + params.toString();
      const tag = document.createElement('script');
      const done = () => { clearTimeout(timer); delete window[cb]; tag.remove(); setBusy(false); };
      const timer = setTimeout(() => { done(); say('error', 'The mailing list did not respond. Check your connection and try again.'); }, 12000);
      window[cb] = (res) => {
        done();
        if (res && res.result === 'success') { say('success', clean(res.msg) || 'Check your inbox to confirm your subscription.'); form.reset(); }
        else { say('error', clean(res && res.msg) || 'Subscription failed. Try again.'); }
      };
      tag.onerror = () => { done(); say('error', 'The mailing list could not be reached. Try again in a moment.'); };
      tag.src = url;
      document.body.appendChild(tag);
    });
  });
})();
