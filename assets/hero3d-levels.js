/* Camoflux 3D hero, "levels" test.
   - One floating 3D icon per level, bobbing and breathing over the painted ground.
   - Hovering an icon (tapping, on touch screens) surrounds the viewer with that level's 360 video.
   - Press and hold an icon to look around inside its 360 video; release to return.
   - Drifting particles; clicking one opens into a floating in-game screenshot with dissolving edges, like a memory.
     Clicking that screenshot opens it large.
   - Clicking the ground slides the painted texture and sends a ripple; a sensing light follows the pointer.
   - Optional figure (The Other) cycles through its shape keys.
   Needs THREE r147 UMD + GLTFLoader, and window.CAMOFLUX_LEVELS:
     { icons: [{ id, label, src, height, pano, panoPoster }], tex: { void, voidN, ground, groundN }, shots: [{ src, caption }] }  */
(() => {
  const C = window.CAMOFLUX_LEVELS;
  const $ = (id) => document.getElementById(id);
  const hero = $('hero'), canvas = $('scene');
  if (!C || !hero || !canvas) return;
  const progress = $('progress'), label = $('level-label');
  const reduced = matchMedia('(prefers-reduced-motion: reduce)').matches, auto = reduced ? 0 : 1;
  const fail = () => { if (progress) progress.style.opacity = 0; hero.classList.add('is-still'); };
  if (!window.THREE || !THREE.GLTFLoader) return fail();
  let renderer;
  try { renderer = new THREE.WebGLRenderer({ canvas, antialias: true }); } catch (e) { return fail(); }
  renderer.setPixelRatio(Math.min(devicePixelRatio || 1, 1.75));
  renderer.outputEncoding = THREE.sRGBEncoding;
  renderer.toneMapping = THREE.ACESFilmicToneMapping;

  const scene = new THREE.Scene();
  scene.background = new THREE.Color(0x000000);
  scene.fog = new THREE.FogExp2(0x000000, 0.06);
  const camera = new THREE.PerspectiveCamera(38, 1, 0.1, 200);
  const camBase = new THREE.Vector3(0, 1.1, 8.2);
  camera.position.copy(camBase);
  scene.add(new THREE.HemisphereLight(0xa9bccc, 0x050505, 0.55));
  const key = new THREE.DirectionalLight(0xffffff, 1.5); key.position.set(-5, 7, -2); scene.add(key);
  const rim = new THREE.DirectionalLight(0xc9d6e6, 0.5); rim.position.set(0, 3, -8); scene.add(rim);
  const fill = new THREE.DirectionalLight(0x6fa8a0, 0.35); fill.position.set(3, 1, 6); scene.add(fill);

  // ---- loading ----
  const total = Object.keys(C.tex).length + C.icons.length + C.shots.length;
  let loaded = 0;
  const tick = () => { loaded++; if (progress) progress.style.width = Math.round(loaded / total * 100) + '%'; };
  const tl = new THREE.TextureLoader();
  const T = {};
  Object.keys(C.tex).forEach((k) => {
    T[k] = tl.load(C.tex[k], tick, undefined, tick);
    T[k].wrapS = T[k].wrapT = THREE.RepeatWrapping;
    T[k].encoding = k.endsWith('N') ? THREE.LinearEncoding : THREE.sRGBEncoding;
  });
  const shotTex = C.shots.map((s) => { const t = tl.load(s.src, tick, undefined, tick); t.encoding = THREE.sRGBEncoding; return t; });

  // ---- ground ----
  T.ground.repeat.set(7, 7); T.groundN.repeat.set(7, 7);
  const groundMat = new THREE.MeshStandardMaterial({ map: T.ground, normalMap: T.groundN, normalScale: new THREE.Vector2(1.4, 1.4), color: 0x6c7771, roughness: 0.62, metalness: 0.06, transparent: true });
  const ground = new THREE.Mesh(new THREE.PlaneGeometry(80, 80), groundMat);
  ground.rotation.x = -Math.PI / 2; ground.position.y = -1.35; scene.add(ground);
  const sensor = new THREE.PointLight(0xd9ecff, 0, 4.5, 1.6); scene.add(sensor);
  const panVel = new THREE.Vector2(), ripples = [], ringGeo = new THREE.RingGeometry(0.96, 1, 96);
  const groundPlane = new THREE.Plane(new THREE.Vector3(0, 1, 0), 1.35), groundHit = new THREE.Vector3();
  function ripple(at) {
    const m = new THREE.Mesh(ringGeo, new THREE.MeshBasicMaterial({ color: 0xe8e6df, transparent: true, opacity: 0.45, depthWrite: false }));
    m.rotation.x = -Math.PI / 2; m.position.set(at.x, -1.33, at.z); m.scale.setScalar(0.2); m.userData = { age: 0 }; scene.add(m); ripples.push(m);
  }

  // ---- 360 videos: one inside-out sphere, its texture swapped per level ----
  const toBlob = (u) => { if (!u || !u.startsWith('data:')) return u; const [h, b] = u.split(','); const bin = atob(b); const a = new Uint8Array(bin.length); for (let i = 0; i < bin.length; i++) a[i] = bin.charCodeAt(i); return URL.createObjectURL(new Blob([a], { type: h.slice(5).split(';')[0] })); };
  const panos = C.icons.map((ic) => {
    const v = document.createElement('video');
    Object.assign(v, { muted: true, loop: true, playsInline: true, preload: 'none', src: toBlob(ic.pano) });   // fetched on first hover
    v.setAttribute('muted', ''); v.setAttribute('playsinline', '');
    const t = new THREE.VideoTexture(v); t.encoding = THREE.sRGBEncoding;
    const poster = tl.load(ic.panoPoster); poster.encoding = THREE.sRGBEncoding;
    return { v, t, poster };
  });
  const sphereMat = new THREE.MeshBasicMaterial({ transparent: true, opacity: 0, depthWrite: false, fog: false, side: THREE.BackSide, toneMapped: false });
  const sphere = new THREE.Mesh(new THREE.SphereGeometry(40, 64, 32), sphereMat);
  sphere.renderOrder = -1; scene.add(sphere);
  let panoIdx = -1, panoAmt = 0;

  // The Other: hovering plays gameplay footage on a curved screen in front of the camera; clicking opens it large with sound.
  let figVideo = null, figTex = null, figPoster = null, figScreen = null, figAmt = 0, figHover = false;
  if (C.figure && C.figure.video) {
    figVideo = document.createElement('video');
    Object.assign(figVideo, { muted: true, loop: true, playsInline: true, preload: 'none', src: toBlob(C.figure.video) });
    figVideo.setAttribute('muted', ''); figVideo.setAttribute('playsinline', '');
    figTex = new THREE.VideoTexture(figVideo); figTex.encoding = THREE.sRGBEncoding;
    figPoster = C.figure.poster ? tl.load(C.figure.poster) : null; if (figPoster) figPoster.encoding = THREE.sRGBEncoding;
    [figTex, figPoster].forEach((t) => { if (t) { t.center.set(0.5, 0.5); t.repeat.set(-1, 1); } });   // seen from inside the arc
    const arc = 0.9, R = 12, hgt = (R * arc) * 9 / 16;
    figScreen = new THREE.Mesh(new THREE.CylinderGeometry(R, R, hgt, 48, 1, true, Math.PI - arc / 2, arc),
      new THREE.MeshBasicMaterial({ map: figPoster || figTex, transparent: true, opacity: 0, side: THREE.DoubleSide, fog: false, toneMapped: false, depthWrite: false }));
    figScreen.renderOrder = -1; figScreen.visible = false; scene.add(figScreen);
  }

  // ---- icons ----
  const loader = new THREE.GLTFLoader();
  if (window.MeshoptDecoder) loader.setMeshoptDecoder(window.MeshoptDecoder);
  const b64 = (s) => { const bin = atob(s.slice(s.indexOf(',') + 1)); const u = new Uint8Array(bin.length); for (let i = 0; i < bin.length; i++) u[i] = bin.charCodeAt(i); return u.buffer; };
  const loadGLB = (src) => new Promise((res, rej) => (src.startsWith('data:') ? loader.parse(b64(src), '', res, rej) : loader.load(src, res, undefined, rej)));
  const fit = (obj, h) => { obj.updateMatrixWorld(true); const box = new THREE.Box3().setFromObject(obj); const s = h / Math.max(...box.getSize(new THREE.Vector3()).toArray()); obj.scale.setScalar(s); obj.position.sub(box.getCenter(new THREE.Vector3()).multiplyScalar(s)); };
  const icons = [];
  const makeMat = () => {
    const map = T.void.clone(); map.needsUpdate = true; map.repeat.set(2, 2);
    const nrm = T.voidN.clone(); nrm.needsUpdate = true; nrm.repeat.set(2, 2);
    return new THREE.MeshStandardMaterial({ map, normalMap: nrm, color: 0xbdbdbd, roughness: 0.55, metalness: 0.2, side: THREE.DoubleSide, emissive: 0x000000 });
  };
  let figure = null, figMorphs = [], figHit = null;
  async function buildFigure() {
    if (!C.figure) return;
    const g = await loadGLB(C.figure.src); const m = g.scene;
    const wrap = new THREE.Group(); wrap.add(m); wrap.scale.setScalar(C.figure.scale || 1.2);
    // Lying on the floor, face down, head toward the camera and legs stretching away from it.
    if (C.figure.lie) wrap.rotation.x = Math.PI / 2;
    const mat = makeMat();
    m.traverse((o) => { if (o.isMesh) { o.material = mat; o.frustumCulled = false; if (o.morphTargetInfluences && o.morphTargetInfluences.length) figMorphs.push(o); } });
    figure = new THREE.Group(); figure.add(wrap);
    figHit = new THREE.Mesh(new THREE.CylinderGeometry(0.45, 0.45, 2.4, 8), new THREE.MeshBasicMaterial({ visible: false }));
    if (C.figure.lie) { figHit.rotation.x = Math.PI / 2; figHit.position.set(0, 0.2, 1.2); } else figHit.position.y = 1.2;
    figure.add(figHit);
    scene.add(figure); layout();
  }
  async function buildIcons() {
    const n = C.icons.length;
    for (let i = 0; i < n; i++) {
      const ic = C.icons[i];
      const g = await loadGLB(ic.fallback || ic.src).catch(() => loadGLB(ic.src)); tick();
      const m = g.scene; const wrap = new THREE.Group(); wrap.add(m); fit(wrap, ic.height || 1.6);
      const mat = makeMat(); const morphs = [];
      m.traverse((o) => { if (o.isMesh && /^U(CX|BX|SP|CP)_/.test(o.name)) { o.visible = false; return; } if (o.isMesh) { o.material = mat; if (o.morphTargetInfluences && o.morphTargetInfluences.length) morphs.push(o); } });
      const holder = new THREE.Group(); holder.add(wrap);
      const hit = new THREE.Mesh(new THREE.SphereGeometry((ic.height || 1.6) * 0.55, 12, 8), new THREE.MeshBasicMaterial({ visible: false }));
      holder.add(hit);
      holder.userData = { i, mat, morphs, hit, phase: i * 1.9, hover: 0, base: new THREE.Vector3() };
      scene.add(holder); icons.push(holder);
    }
    layout();
  }

  // ---- particles and screenshots ----
  const PCOUNT = 36;
  const pGeo = new THREE.SphereGeometry(0.035, 8, 6), pHitGeo = new THREE.SphereGeometry(0.2, 6, 4);
  // Particles rest a soft grey-green and turn pure white under the pointer.
  const pBase = new THREE.Color(0x9fa894), pWhite = new THREE.Color(0xffffff);
  const particles = [];
  let hoverParticle = null;
  const rand = (a, b) => a + Math.random() * (b - a);
  const place = (p, fromBelow) => { p.position.set(rand(-4, 6), fromBelow ? -1.2 : rand(-1, 3.2), rand(-4, 3)); p.userData.v = rand(0.08, 0.22); p.userData.ph = rand(0, 6.28); };
  for (let i = 0; i < PCOUNT; i++) {
    const p = new THREE.Mesh(pGeo, new THREE.MeshBasicMaterial({ color: pBase.clone(), transparent: true, opacity: 0.8, fog: true, toneMapped: false })); const h = new THREE.Mesh(pHitGeo, new THREE.MeshBasicMaterial({ visible: false }));
    p.add(h); p.userData.hit = h; p.userData.glow = 0; place(p, false); scene.add(p); particles.push(p);
  }
  // Screenshots appear as memories: irregular, dissolving edges that breathe slowly, slightly faded colour.
  const memoryMat = (t) => new THREE.ShaderMaterial({
    uniforms: { map: { value: t }, opacity: { value: 0 }, time: { value: 0 }, seed: { value: Math.random() * 10 } },
    vertexShader: 'varying vec2 vUv; void main(){ vUv = uv; gl_Position = projectionMatrix * modelViewMatrix * vec4(position,1.0); }',
    fragmentShader: `uniform sampler2D map; uniform float opacity; uniform float time; uniform float seed; varying vec2 vUv;
      float h(vec2 p){ return fract(sin(dot(p, vec2(127.1, 311.7))) * 43758.5453); }
      float n(vec2 p){ vec2 i = floor(p), f = fract(p); f = f * f * (3.0 - 2.0 * f);
        return mix(mix(h(i), h(i + vec2(1, 0)), f.x), mix(h(i + vec2(0, 1)), h(i + vec2(1, 1)), f.x), f.y); }
      float fbm(vec2 p){ float v = 0.0, a = 0.5; for (int k = 0; k < 4; k++) { v += a * n(p); p *= 2.1; a *= 0.5; } return v; }
      void main(){
        vec2 c = vUv - 0.5;
        float edge = 1.0 - max(abs(c.x) * 2.0, abs(c.y) * 2.0);           // 0 at the border, 1 at the centre
        float r = 1.0 - length(c * vec2(1.6, 1.9));                         // soft oval
        float wob = fbm(vUv * 5.0 + seed + time * 0.06) - 0.5;              // irregular, slowly shifting border
        float mask = smoothstep(0.0, 0.42, min(edge, r) + wob * 0.35);
        vec3 col = texture2D(map, vUv + (fbm(vUv * 3.0 + time * 0.05) - 0.5) * 0.006).rgb;
        col = mix(col, vec3(dot(col, vec3(0.299, 0.587, 0.114))), 0.22);  // slightly faded, like recall
        gl_FragColor = vec4(col, mask * opacity);
        #include <encodings_fragment>
      }`,
    transparent: true, depthWrite: false, side: THREE.DoubleSide, toneMapped: false,
  });
  const shots = [];
  let shotIdx = 0;
  function openShotAt(pos) {
    const t = shotTex[shotIdx % shotTex.length]; const cap = C.shots[shotIdx % C.shots.length]; shotIdx++;
    const img = t.image; const aspect = img && img.width ? img.width / img.height : 16 / 9;
    const w = Math.min(2.4, 1.3 * aspect), h = w / aspect;
    const mesh = new THREE.Mesh(new THREE.PlaneGeometry(w, h), memoryMat(t));
    mesh.position.copy(pos); mesh.scale.setScalar(0.05);
    mesh.userData = { age: 0, life: 9, cap }; scene.add(mesh); shots.push(mesh);
    if (shots.length > 3) shots[0].userData.age = Math.max(shots[0].userData.age, shots[0].userData.life - 0.6);
  }

  // ---- layout ----
  function layout() {
    const w = canvas.clientWidth, h = canvas.clientHeight; if (!w || !h) return;
    renderer.setSize(w, h, false); camera.aspect = w / h; camera.updateProjectionMatrix();
    const wide = w > 900, n = icons.length;
    if (figure) { if (C.figure.lie) figure.position.set(wide ? 2.4 : 0.2, -1.25, -2.6); else figure.position.set(wide ? 4.7 : 2.0, -1.4, wide ? 0.4 : 0.3); }
    icons.forEach((ic, i) => {
      const k = n > 1 ? i / (n - 1) : 0.5;
      ic.userData.base.set(wide ? 0.6 + k * 4.2 : -1.6 + k * 3.2, wide ? 0.5 + Math.sin(k * Math.PI) * 0.6 : 1.4, wide ? -1.2 + Math.sin(k * Math.PI) * 1.4 : 0);
    });
  }
  addEventListener('resize', layout);

  // ---- input ----
  const ndc = new THREE.Vector2(-0.7, -0.3), pointer = new THREE.Vector2(), ray = new THREE.Raycaster();
  let hovered = -1, holding = -1, holdStart = null, yaw = 0, pitch = 0, lookW = 0, yaw0 = 0, pitch0 = 0;
  const onMove = (ev) => { const r = canvas.getBoundingClientRect(); ndc.set(((ev.clientX - r.left) / r.width) * 2 - 1, -((ev.clientY - r.top) / r.height) * 2 + 1); pointer.set(ev.clientX / innerWidth - 0.5, ev.clientY / innerHeight - 0.5); if (label) { label.style.left = ev.clientX - r.left + 18 + 'px'; label.style.top = ev.clientY - r.top + 12 + 'px'; } };
  addEventListener('pointermove', onMove, { passive: true });
  const ignore = (ev) => ev.target.closest('a,button,input,form');
  const pick = () => {
    ray.setFromCamera(ndc, camera);
    const s = ray.intersectObjects(shots, false); if (s.length) return { kind: 'shot', obj: s[0].object };
    const ic = ray.intersectObjects(icons.map((x) => x.userData.hit), false); if (ic.length) return { kind: 'icon', i: icons.findIndex((x) => x.userData.hit === ic[0].object) };
    const p = ray.intersectObjects(particles.map((x) => x.userData.hit), false); if (p.length) return { kind: 'particle', obj: p[0].object.parent };
    if (figHit && ray.intersectObject(figHit).length) return { kind: 'figure' };
    if (ray.ray.intersectPlane(groundPlane, groundHit)) return { kind: 'ground', at: groundHit.clone() };
    return null;
  };
  const setHover = (i) => {
    if (i === hovered) return; hovered = i;
    panos.forEach((p, j) => { if (j === i) { p.v.play().catch(() => {}); } else p.v.pause(); });
    if (i >= 0) { panoIdx = i; if (label) { label.textContent = C.icons[i].label; label.dataset.show = 'true'; } } else if (label) label.dataset.show = 'false';
  };
  let touchPinned = false;
  hero.addEventListener('pointermove', (ev) => {
    if (holding >= 0) {   // looking around inside the 360: a drag across the screen turns about one and a half circles
      const r = canvas.getBoundingClientRect();
      yaw = yaw0 - (ev.clientX - holdStart.x) / r.width * Math.PI * 3;
      pitch = Math.max(-1.2, Math.min(1.2, pitch0 + (ev.clientY - holdStart.y) / r.height * Math.PI));
      return;
    }
    if (ignore(ev) || touchPinned) return;
    const h = pick(); hero.style.cursor = h && h.kind !== 'ground' ? 'pointer' : (h ? 'crosshair' : '');
    setHover(h && h.kind === 'icon' ? h.i : -1);
    hoverParticle = h && h.kind === 'particle' ? h.obj : null;
    figHover = !!(h && h.kind === 'figure');
    if (figVideo) { if (figHover) figVideo.play().catch(() => {}); else if (figAmt < 0.05) figVideo.pause(); }
    if (label) { if (h && h.kind === 'figure') { label.textContent = C.figure.label; label.dataset.show = 'true'; } else if (!(h && h.kind === 'icon')) label.dataset.show = 'false'; }
  });
  hero.addEventListener('pointerleave', () => { if (!touchPinned && holding < 0) setHover(-1); });
  hero.addEventListener('pointerdown', (ev) => {
    if (ignore(ev)) return; onMove(ev); const h = pick();
    if (h && h.kind === 'icon') {
      holding = h.i; setHover(h.i); holdStart = { x: ev.clientX, y: ev.clientY, time: performance.now() };
      yaw0 = yaw; pitch0 = pitch; hero.classList.add('is-looking'); hero.setPointerCapture && hero.setPointerCapture(ev.pointerId);
    }
  });
  const endHold = () => { if (holding < 0) return; holding = -1; hero.classList.remove('is-looking'); if (!touchPinned) setHover(-1); };
  addEventListener('pointerup', endHold); addEventListener('pointercancel', endHold);
  const box = $('shotbox');
  const openVideo = (src, cap) => { if (!box) return; const st = box.querySelector('.shotbox__stage'); st.innerHTML = '';
    const v = Object.assign(document.createElement('video'), { src: toBlob(src), controls: true, autoplay: true, playsInline: true }); st.appendChild(v);
    box.querySelector('.shotbox__cap').textContent = cap; box.dataset.open = 'true'; box.querySelector('button').focus(); };
  const openLarge = (shot) => { if (!box) return; const st = box.querySelector('.shotbox__stage'); st.innerHTML = ''; st.appendChild(Object.assign(document.createElement('img'), { src: shot.userData.cap.src, alt: shot.userData.cap.caption })); box.querySelector('.shotbox__cap').textContent = shot.userData.cap.caption; box.dataset.open = 'true'; box.querySelector('button').focus(); };
  if (box) { box.addEventListener('click', (ev) => { if (ev.target === box || ev.target.closest('button')) { box.dataset.open = 'false'; box.querySelector('.shotbox__stage').innerHTML = ''; } }); document.addEventListener('keydown', (ev) => { if (ev.key === 'Escape') box.dataset.open = 'false'; }); }
  hero.addEventListener('click', (ev) => {
    if (ignore(ev)) return; onMove(ev); const h = pick();
    if (!h) { if (touchPinned) { touchPinned = false; setHover(-1); } return; }
    if (h.kind === 'shot') openLarge(h.obj);
    if (h.kind === 'particle') { openShotAt(h.obj.position.clone()); place(h.obj, true); }
    if (h.kind === 'figure' && C.figure.video) openVideo(C.figure.video, C.figure.videoCaption || 'Gameplay');
    if (h.kind === 'ground') { ripple(h.at); panVel.x += -h.at.x * 0.012; panVel.y += h.at.z * 0.012; }
    if (h.kind === 'icon' && ev.pointerType === 'touch') { touchPinned = hovered !== h.i || !touchPinned; setHover(touchPinned ? h.i : -1); }
  });

  // ---- loop ----
  const clock = new THREE.Clock();
  let visible = true, running = false;
  const q = new THREE.Vector3();
  function frame() {
    if (!running) return;
    const dt = Math.min(clock.getDelta(), 0.05), t = clock.elapsedTime;

    // 360: fade in around the viewer while an icon is hovered; the painted world recedes.
    panoAmt += ((hovered >= 0 ? 1 : 0) - panoAmt) * Math.min(1, dt * 3);
    lookW += ((holding >= 0 ? 1 : 0) - lookW) * Math.min(1, dt * (holding >= 0 ? 5 : 2.5));
    if (holding < 0 && lookW < 0.02) { yaw *= 0.9; pitch *= 0.9; }
    if (panoIdx >= 0) { const p = panos[panoIdx]; sphereMat.map = p.v.readyState >= 2 ? p.t : p.poster; sphereMat.needsUpdate = true; }
    sphereMat.opacity = panoAmt; sphere.visible = panoAmt > 0.01;
    if (figScreen) {
      figAmt += ((figHover ? 1 : 0) - figAmt) * Math.min(1, dt * 3);
      figScreen.visible = figAmt > 0.01; figScreen.position.copy(camera.position);
      figScreen.material.opacity = figAmt * 0.95;
      const live = figVideo.readyState >= 2 ? figTex : (figPoster || figTex);
      if (figScreen.material.map !== live) { figScreen.material.map = live; figScreen.material.needsUpdate = true; }
      if (!figHover && figAmt < 0.02 && !figVideo.paused) figVideo.pause();
    }
    const fov = 38 + panoAmt * 29 + lookW * 8;   // widened view inside a 360, a third less than the first test
    if (Math.abs(camera.fov - fov) > 0.05) { camera.fov = fov; camera.updateProjectionMatrix(); }
    sphere.position.copy(camera.position);   // the 360 wraps the camera, so it projects correctly
    sphere.rotation.y = pointer.x * 0.6 * (1 - lookW) + t * 0.01 * auto;
    groundMat.opacity = 1 - Math.max(panoAmt * 0.85, figAmt * 0.7); scene.fog.density = 0.06 * (1 - panoAmt * 0.8);

    icons.forEach((ic, i) => {
      const u = ic.userData, on = hovered === i ? 1 : 0;
      u.hover += (on - u.hover) * Math.min(1, dt * 4);
      ic.position.set(u.base.x, u.base.y + Math.sin(t * 0.6 + u.phase) * 0.18 * auto, u.base.z + u.hover * 0.9);
      ic.rotation.y += dt * (0.12 * auto + u.hover * 0.5);
      ic.scale.setScalar(1 + u.hover * 0.18);
      u.mat.emissive.setScalar(u.hover * 0.12);
      u.morphs.forEach((m) => m.morphTargetInfluences.forEach((_, j) => { m.morphTargetInfluences[j] = (Math.sin(t * (0.24 - j * 0.05) + j * 1.7 + u.phase) + 1) * 0.5 * (0.8 - j * 0.1) * (auto + u.hover); }));
    });

    ray.setFromCamera(ndc, camera);
    if (ray.ray.intersectPlane(groundPlane, groundHit)) { sensor.position.set(groundHit.x, -0.7, groundHit.z); sensor.intensity += ((holding >= 0 ? 0 : 1.6) - sensor.intensity) * Math.min(1, dt * 4); }
    panVel.multiplyScalar(Math.pow(0.35, dt));
    T.ground.offset.x += panVel.x * dt; T.ground.offset.y += panVel.y * dt - dt * 0.004 * auto; T.groundN.offset.copy(T.ground.offset);
    for (let i = ripples.length - 1; i >= 0; i--) { const r = ripples[i]; r.userData.age += dt; const k = r.userData.age / 2; r.scale.setScalar(0.2 + k * 5); r.material.opacity = Math.max(0, 1 - k) * 0.45; if (k >= 1) { scene.remove(r); r.material.dispose(); ripples.splice(i, 1); } }
    // The Other cycles through its shape keys one after another, each easing in and out.
    if (figure) {
      figure.rotation.y = C.figure.lie ? Math.sin(t * 0.15) * 0.04 * auto : -0.5 + Math.sin(t * 0.2) * 0.25 * auto;
      figMorphs.forEach((m) => { const n = m.morphTargetInfluences.length, c = (t * 0.35) % n;
        for (let j = 0; j < n; j++) { const d = Math.min(Math.abs(c - j), n - Math.abs(c - j)); m.morphTargetInfluences[j] = Math.max(0, 1 - d) ** 2 * (reduced ? 0.4 : 1); } });
    }
    particles.forEach((p) => { const u = p.userData; u.glow += ((p === hoverParticle ? 1 : 0) - u.glow) * Math.min(1, dt * 8); p.material.color.lerpColors(pBase, pWhite, u.glow); p.material.opacity = 0.8 + u.glow * 0.2; { const f = u.glow < 0.05; if (p.material.fog !== f) { p.material.fog = f; p.material.needsUpdate = true; } }   /* fog would grey out the white */ p.position.y += p.userData.v * dt * (auto || 0.2) * (1 - u.glow * 0.9); p.position.x += Math.sin(t * 0.4 + p.userData.ph) * 0.002 * auto; if (p.position.y > 3.6) place(p, true); p.scale.setScalar((1 + Math.sin(t * 2 + p.userData.ph) * 0.25) * (1 + u.glow * 0.3)); });

    for (let i = shots.length - 1; i >= 0; i--) {
      const s = shots[i], u = s.userData; u.age += dt;
      const inA = Math.min(1, u.age / 0.5), outA = Math.min(1, Math.max(0, (u.life - u.age) / 0.6));
      s.material.uniforms.opacity.value = Math.min(inA, outA); s.material.uniforms.time.value = t; s.scale.setScalar(0.05 + 0.95 * (1 - Math.pow(1 - inA, 3)));
      s.position.y += dt * 0.05; s.quaternion.copy(camera.quaternion);
      if (u.age > u.life) { scene.remove(s); s.geometry.dispose(); s.material.dispose(); shots.splice(i, 1); }
    }

    const tgt = camBase.clone().add(q.set(pointer.x * 2.59 * (1 - lookW), -pointer.y * 1.3 * (1 - lookW), 0));
    camera.position.lerp(tgt, 0.05);
    const normal = new THREE.Vector3(1.2 + pointer.x * 0.65, 0.5 - pointer.y * 0.32, 0);
    const dir = new THREE.Vector3(Math.sin(yaw) * Math.cos(pitch), Math.sin(pitch), -Math.cos(yaw) * Math.cos(pitch));
    const look = camera.position.clone().add(dir.multiplyScalar(10));
    camera.lookAt(normal.lerp(look, lookW));
    renderer.render(scene, camera);
    requestAnimationFrame(frame);
  }
  const setRunning = () => { const want = visible && !document.hidden; if (!want) panos.forEach((p) => p.v.pause()); else if (hovered >= 0) panos[hovered].v.play().catch(() => {}); if (want && !running) { running = true; clock.getDelta(); requestAnimationFrame(frame); } else if (!want) running = false; };
  new IntersectionObserver((es) => { visible = es[0].isIntersecting; setRunning(); }).observe(hero);
  document.addEventListener('visibilitychange', setRunning);

  const ready = new Promise((r) => { const c = () => (loaded >= Object.keys(C.tex).length + C.shots.length ? r() : setTimeout(c, 30)); c(); });
  ready.then(buildIcons).then(buildFigure).then(() => { layout(); hero.classList.add('is-live'); setTimeout(() => { if (progress) progress.style.opacity = 0; }, 400); setRunning(); })
    .catch((err) => { console.error(err); fail(); });

})();
