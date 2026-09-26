/* Camoflux 3D hero, v3.
   Needs THREE (r147 UMD), THREE.GLTFLoader and MeshoptDecoder, and window.CAMOFLUX_HERO.
   Asset sources may be URLs (site) or data URIs (single-file previews).

   Interactions, each tied to a mechanic of the game:
     Move       Sensing. A pale sensor light follows the pointer across the ground, reading the land.
     Stay still Camouflage. After a moment of stillness the model sinks into the painted ground;
                fast movement reveals it again.
     Scroll     Source to sea. Scrolling lowers the camera toward the water and speeds its flow.
     Click      Vibration. Clicking the ground sends a ripple through it and the model answers.
                Clicking the model shifts to the next being; clicking the footage opens it large.
     Hold       Channel energy. Press and hold to charge light into the model; release to let it out.
   Reciprocity runs through all of them: the scene answers gently when approached gently,
   and harder when approached fast.

   Markup: #hero, canvas#scene, #progress, #status, #footage, #hint, #shotbox, [data-hero-next], [data-hero-shot] */
(() => {
  const C = window.CAMOFLUX_HERO;
  const $ = (id) => document.getElementById(id);
  const hero = $('hero'), canvas = $('scene');
  if (!C || !hero || !canvas) return;
  const statusEl = $('status'), progress = $('progress'), footEl = $('footage');
  const setText = (el, t) => { if (el) el.textContent = t; };
  // Reduced motion: no automatic movement, but the scene stays live and still answers the visitor.
  const reduced = matchMedia('(prefers-reduced-motion: reduce)').matches;
  const auto = reduced ? 0 : 1;
  const fail = (msg) => { setText(statusEl, msg); if (progress) progress.style.opacity = 0; hero.classList.add('is-still'); };

  if (!window.THREE || !THREE.GLTFLoader) return fail('3D could not load; showing a still');
  let renderer;
  try { renderer = new THREE.WebGLRenderer({ canvas, antialias: true, powerPreference: 'high-performance' }); }
  catch (e) { return fail('3D is not available on this device; showing a still'); }
  renderer.setPixelRatio(Math.min(window.devicePixelRatio || 1, 1.75));
  renderer.outputEncoding = THREE.sRGBEncoding;
  renderer.toneMapping = THREE.ACESFilmicToneMapping;
  renderer.toneMappingExposure = 1.05;

  const scene = new THREE.Scene();
  scene.background = new THREE.Color(0x000000);
  scene.fog = new THREE.FogExp2(0x000000, 0.06);
  const camera = new THREE.PerspectiveCamera(34, 1, 0.1, 200);
  const camBase = new THREE.Vector3(0, 1.1, 7.6);
  camera.position.copy(camBase);

  scene.add(new THREE.HemisphereLight(0xa9bccc, 0x050505, 0.5));
  const key = new THREE.DirectionalLight(0xffffff, 1.5); key.position.set(-5, 7, -2); scene.add(key);
  const rim = new THREE.DirectionalLight(0xc9d6e6, 0.5); rim.position.set(0, 3, -8); scene.add(rim);
  const screenLight = new THREE.DirectionalLight(0x3a6f55, 0.9); screenLight.position.set(0, 2, -6); scene.add(screenLight);
  const fill = new THREE.DirectionalLight(0x6fa8a0, 0.3); fill.position.set(3, 1, 6); scene.add(fill);
  const energyLight = new THREE.PointLight(0xff6a1a, 0, 7, 1.3); scene.add(energyLight);      // channelled energy
  const sensor = new THREE.PointLight(0xd9ecff, 0, 4.5, 1.6); scene.add(sensor);                // sensing light

  // ---- loading ----
  const texKeys = Object.keys(C.tex);
  const total = texKeys.length + C.frames.length + 1;
  let loaded = 0;
  const tick = () => { loaded++; if (progress) progress.style.width = Math.round(loaded / total * 100) + '%'; };
  const tl = new THREE.TextureLoader();
  const T = {};
  texKeys.forEach((k) => {
    T[k] = tl.load(C.tex[k], tick, undefined, tick);
    T[k].wrapS = T[k].wrapT = THREE.RepeatWrapping;
    T[k].anisotropy = Math.min(8, renderer.capabilities.getMaxAnisotropy());
    T[k].encoding = k.endsWith('N') ? THREE.LinearEncoding : THREE.sRGBEncoding;
  });

  // ---- model surface ----
  const makeMat = (repeat) => {
    const map = T.void.clone(); map.needsUpdate = true; map.repeat.set(repeat, repeat);
    const nrm = T.voidN.clone(); nrm.needsUpdate = true; nrm.repeat.set(repeat, repeat);
    const m = new THREE.MeshStandardMaterial({ map, normalMap: nrm, normalScale: new THREE.Vector2(1.2, 1.2), color: 0xbdbdbd,
      roughness: 0.55, metalness: 0.2, side: THREE.DoubleSide, transparent: true });
    m.userData.base = m.color.clone();
    return m;
  };

  // ---- ground: the hand-painted greenish oil pattern with its normal map ----
  const groundMap = T.ground; groundMap.repeat.set(7, 7);
  const groundN = T.groundN; groundN.repeat.set(7, 7);
  const ground = new THREE.Mesh(new THREE.PlaneGeometry(80, 80),
    new THREE.MeshStandardMaterial({ map: groundMap, normalMap: groundN, normalScale: new THREE.Vector2(1.4, 1.4), color: 0x6c7771, roughness: 0.62, metalness: 0.06 }));
  ground.rotation.x = -Math.PI / 2; ground.position.y = -1.35; scene.add(ground);
  const groundTint = new THREE.Color(0x0b1a15);   // what the model blends toward when camouflaged

  // ---- footage screen behind the model (stills and looping clips) ----
  const pickClip = (f) => (f.webm && document.createElement('video').canPlayType('video/webm; codecs="vp9"') ? f.webm : f.video);
  const toBlobUrl = (u) => {   // data: videos become blob: URLs, which more pages allow as media sources
    if (!u || !u.startsWith('data:')) return u;
    const [head, b64] = u.split(','); const bin = atob(b64); const a = new Uint8Array(bin.length);
    for (let i = 0; i < bin.length; i++) a[i] = bin.charCodeAt(i);
    return URL.createObjectURL(new Blob([a], { type: head.slice(5).split(';')[0] }));
  };
  const frameTex = C.frames.map((f) => {
    const still = tl.load(f.src, tick, undefined, tick); still.encoding = THREE.sRGBEncoding;
    if (!f.video) return still;
    const v = document.createElement('video');
    Object.assign(v, { muted: true, loop: true, playsInline: true, preload: 'auto' });
    v.setAttribute('muted', ''); v.setAttribute('playsinline', '');
    v.src = toBlobUrl(pickClip(f));
    const vt = new THREE.VideoTexture(v); vt.encoding = THREE.sRGBEncoding; vt.userData.video = v; vt.userData.still = still;
    v.addEventListener('error', () => { vt.userData.failed = true; });   // falls back to the still
    return vt;
  });
  const texFor = (i) => { const t = frameTex[i]; return t.userData.video && (t.userData.failed || t.userData.video.readyState < 2) ? t.userData.still : t; };
  const playFrame = (i) => frameTex.forEach((t, j) => { const v = t.userData.video; if (!v) return; if (j === i || j === (i + 1) % frameTex.length) v.play().catch(() => {}); else v.pause(); });

  const screenMat = new THREE.ShaderMaterial({
    uniforms: { a: { value: frameTex[0] }, b: { value: frameTex[1 % frameTex.length] }, mixv: { value: 0 }, zoom: { value: 0 }, dim: { value: 0.95 } },
    vertexShader: 'varying vec2 vUv; void main(){ vUv = uv; gl_Position = projectionMatrix * modelViewMatrix * vec4(position,1.0); }',
    fragmentShader: `uniform sampler2D a; uniform sampler2D b; uniform float mixv; uniform float zoom; uniform float dim; varying vec2 vUv;
      void main(){ vec2 uv = (vec2(1.0 - vUv.x, vUv.y) - 0.5) * (1.0 - zoom * 0.06) + 0.5;
        vec3 c = mix(texture2D(a, uv).rgb, texture2D(b, uv).rgb, smoothstep(0.0, 1.0, mixv));
        float edge = smoothstep(0.0, 0.03, vUv.x) * smoothstep(0.0, 0.03, 1.0 - vUv.x) * smoothstep(0.0, 0.04, vUv.y) * smoothstep(0.0, 0.04, 1.0 - vUv.y);
        gl_FragColor = vec4(c * dim * edge, 1.0);
        #include <encodings_fragment>
      }`,
    toneMapped: false, side: THREE.DoubleSide, fog: false,
  });
  const screen = new THREE.Mesh(new THREE.CylinderGeometry(14, 14, 3.78, 32, 1, true, Math.PI - 0.27, 0.54)   /* 2:1, matching the gameplay clips */, screenMat);
  screen.position.set(0, 1.55, 7.2); scene.add(screen);

  let frameIdx = 0, frameT = 0, fading = false;
  const colorOf = (i) => new THREE.Color(C.frames[i].color || '#3a6f55');
  const showFrameCaption = (i) => setText(footEl, C.frames[i].caption);
  function advanceFrames(dt) {
    screenMat.uniforms.a.value = fading ? screenMat.uniforms.a.value : texFor(frameIdx);
    if (frameTex.length < 2 || reduced) return;
    frameT += dt; screenMat.uniforms.zoom.value = Math.min(1, frameT / 7);
    if (!fading && frameT > 6) { fading = true; screenMat.uniforms.b.value = texFor((frameIdx + 1) % frameTex.length); playFrame(frameIdx); }
    if (fading) {
      screenMat.uniforms.mixv.value = Math.min(1, screenMat.uniforms.mixv.value + dt / 1.4);
      screenLight.color.lerpColors(colorOf(frameIdx), colorOf((frameIdx + 1) % frameTex.length), screenMat.uniforms.mixv.value);
      if (screenMat.uniforms.mixv.value >= 1) {
        frameIdx = (frameIdx + 1) % frameTex.length; screenMat.uniforms.a.value = texFor(frameIdx);
        screenMat.uniforms.mixv.value = 0; frameT = 0; fading = false; showFrameCaption(frameIdx); playFrame(frameIdx);
      }
    }
  }

  // ---- models ----
  const loader = new THREE.GLTFLoader();
  if (window.MeshoptDecoder) loader.setMeshoptDecoder(window.MeshoptDecoder);
  const cache = {};
  const b64ToBuf = (s) => { const bin = atob(s.slice(s.indexOf(',') + 1)); const u = new Uint8Array(bin.length); for (let i = 0; i < bin.length; i++) u[i] = bin.charCodeAt(i); return u.buffer; };
  const loadSrc = (src) => new Promise((res, rej) => {
    if (src.startsWith('data:')) loader.parse(b64ToBuf(src), '', res, rej); else loader.load(src, res, undefined, rej);
  });
  // Compressed (meshopt) files need WebAssembly; where a page blocks it, fall back to the quantized copy.
  const load = (name) => {
    if (cache[name]) return Promise.resolve(cache[name]);
    const m = C.models[name];
    return loadSrc(m.src).catch((err) => (m.fallback ? loadSrc(m.fallback) : Promise.reject(err))).then((g) => (cache[name] = g));
  };
  const order = C.order || Object.keys(C.models);
  let modelName = C.initialModel || order[0];
  let current = null, morphs = [], drones = [], bones = {}, mats = [];

  const fit = (obj, height) => {
    obj.updateMatrixWorld(true);
    const box = new THREE.Box3().setFromObject(obj); const size = box.getSize(new THREE.Vector3()); const c = box.getCenter(new THREE.Vector3());
    const s = height / Math.max(size.x, size.y, size.z); obj.scale.setScalar(s); obj.position.sub(c.multiplyScalar(s));
  };
  async function show(name) {
    const cfg = C.models[name]; const gltf = await load(name);
    if (current) scene.remove(current);
    morphs = []; drones = []; bones = {}; mats = [];
    const group = new THREE.Group(); const mat = makeMat(cfg.repeat || 2); mats.push(mat);
    if (cfg.flock) {
      for (let i = 0; i < 9; i++) {
        const d = gltf.scene.clone(true); const holder = new THREE.Group(); holder.add(d); fit(d, 0.55 + (i % 3) * 0.12);
        d.traverse((m) => { if (m.isMesh) m.material = mat; });
        holder.userData = { r: 1.2 + (i % 4) * 0.45, speed: 0.18 + (i % 5) * 0.04, phase: i * 0.7, y: -0.4 + (i % 3) * 0.55 };
        group.add(holder); drones.push(holder);
      }
    } else {
      const m = cfg.skinned ? gltf.scene : gltf.scene.clone(true);
      const wrap = new THREE.Group(); wrap.add(m);
      if (cfg.skinned) { wrap.scale.setScalar(cfg.scale || 1); wrap.position.y = cfg.floor ?? -1.35; } else fit(wrap, cfg.height || 3.2);
      group.add(wrap);
      m.traverse((o) => {
        if (o.isMesh && /^U(CX|BX|SP|CP)_/.test(o.name)) { o.visible = false; return; }
        if (o.isMesh) { o.material = mat; o.frustumCulled = false; if (o.morphTargetInfluences && o.morphTargetInfluences.length) morphs.push(o); }
        if (o.isBone) { bones[o.name.replace(/^.*_/, '')] = { bone: o, rest: o.quaternion.clone() }; }
      });
    }
    group.userData.name = name; current = group; scene.add(group); modelName = name;
    layout();
  }

  const q = new THREE.Quaternion(), eul = new THREE.Euler();
  const sway = (n, x, y, z) => { const b = bones[n]; if (!b) return; eul.set(x, y, z); q.setFromEuler(eul); b.bone.quaternion.copy(b.rest).multiply(q); };
  function idleRig(t, k) {
    sway('Spine', Math.sin(t * 0.8) * 0.03 * k, 0, 0); sway('Spine1', Math.sin(t * 0.8 + 0.4) * 0.03 * k, Math.sin(t * 0.3) * 0.05 * k, 0);
    sway('Neck', 0, Math.sin(t * 0.35) * 0.12 * k, 0); sway('Head', Math.sin(t * 0.5) * 0.06 * k, Math.sin(t * 0.35 + 0.6) * 0.18 * k, 0);
  }

  // ---- layout ----
  function layout() {
    const w = canvas.clientWidth, h = canvas.clientHeight; if (!w || !h) return;
    renderer.setSize(w, h, false); camera.aspect = w / h; camera.updateProjectionMatrix();
    const wide = w > 900;
    if (current) current.position.set(wide ? 2.3 : 0, wide ? 0.15 : 0.9, 0);
    screen.position.x = wide ? 2.2 : 0;
  }
  addEventListener('resize', layout);

  // ---- input state ----
  const pointer = new THREE.Vector2(), ndc = new THREE.Vector2(-0.7, -0.3), ray = new THREE.Raycaster();
  const groundPlane = new THREE.Plane(new THREE.Vector3(0, 1, 0), 1.35), groundHit = new THREE.Vector3();
  let speed = 0, lastMove = 0, lastX = 0, lastY = 0, stillFor = 0, camo = 0;
  let holding = false, holdStart = 0, energy = 0, heldLong = false, scrollP = 0, surge = 0, near = 0;
  const panVel = new THREE.Vector2(), modelScreen = new THREE.Vector3();
  const onMove = (ev) => {
    const now = performance.now(), dtm = Math.max(16, now - lastMove);
    speed = speed * 0.7 + (Math.hypot(ev.clientX - lastX, ev.clientY - lastY) / dtm) * 0.3;   // px per ms, smoothed
    lastX = ev.clientX; lastY = ev.clientY; lastMove = now; stillFor = 0;
    pointer.set(ev.clientX / innerWidth - 0.5, ev.clientY / innerHeight - 0.5);
    const r = canvas.getBoundingClientRect(); ndc.set(((ev.clientX - r.left) / r.width) * 2 - 1, -((ev.clientY - r.top) / r.height) * 2 + 1);
  };
  addEventListener('pointermove', onMove, { passive: true });
  const updateScroll = () => { const r = hero.getBoundingClientRect(); scrollP = Math.min(1, Math.max(0, -r.top / Math.max(1, r.height))); };
  addEventListener('scroll', updateScroll, { passive: true });

  // ---- ripples: vibration through the painted ground ----
  const ripples = [];
  const ringGeo = new THREE.RingGeometry(0.96, 1, 96);
  function ripple(at, strength) {
    const m = new THREE.Mesh(ringGeo, new THREE.MeshBasicMaterial({ color: 0xe8e6df, transparent: true, opacity: 0.55 * strength, depthWrite: false, fog: true }));
    m.rotation.x = -Math.PI / 2; m.position.set(at.x, -1.33, at.z); m.scale.setScalar(0.2);
    m.userData = { age: 0, life: 1.6 + strength, grow: 3 + strength * 5 }; scene.add(m); ripples.push(m);
    surge = Math.min(1.5, surge + 0.5 * strength);
  }

  // ---- loop ----
  const clock = new THREE.Clock();
  let visible = true, running = false;
  function frame() {
    if (!running) return;
    const dt = Math.min(clock.getDelta(), 0.05), t = clock.elapsedTime;
    stillFor += dt; speed *= Math.pow(0.1, dt);

    // Camouflage: stillness hides the model in the ground; fast movement reveals it.
    const target = stillFor > 1.2 && !holding ? 1 : 0;
    camo += (target - camo) * Math.min(1, dt * (target ? 0.6 : 2.5 + speed * 10));
    mats.forEach((m) => { m.color.copy(m.userData.base).lerp(groundTint, camo * 0.85); m.opacity = 1 - camo * 0.55; });

    // Hold: channel energy into the model; release lets it out as a large ripple.
    if (holding && performance.now() - holdStart > 260) heldLong = true;
    energy += ((holding && heldLong ? 1 : 0) - energy) * Math.min(1, dt * (holding ? 0.7 : 1.8));
    energyLight.intensity = energy * 9; if (current) energyLight.position.set(current.position.x, current.position.y + 0.4, 0.2);
    screenMat.uniforms.dim.value = 0.95 + energy * 0.35;

    // Sensing: the sensor light follows the pointer across the ground.
    ray.setFromCamera(ndc, camera);
    if (ray.ray.intersectPlane(groundPlane, groundHit)) { sensor.position.set(groundHit.x, -0.7, groundHit.z); sensor.intensity += ((1.4 + Math.min(2, speed * 3)) - sensor.intensity) * Math.min(1, dt * 4); }

    // Model motion: automatic parts scale with `auto`; responses to the visitor always run.
    surge *= Math.pow(0.25, dt);
    const react = surge + energy;
    if (current) {
      if (drones.length) drones.forEach((d) => { const u = d.userData, a = t * u.speed * (auto + react * 2) + u.phase; d.position.set(Math.cos(a) * u.r * (1 + energy * 0.4), u.y + Math.sin(t * 0.6 + u.phase) * 0.15 * auto, Math.sin(a) * u.r * (1 + energy * 0.4)); d.rotation.y = -a; });
      else current.rotation.y += dt * ((C.models[modelName].spin ?? 0.08) * auto + react * 0.9);
      // Breathing: slow, and deeper while camouflaged. Ground vibrations touch the shape keys only lightly.
      const breathe = 0.24 * (1 - camo * 0.35), keyReact = surge * 0.1 + energy;
      morphs.forEach((m) => m.morphTargetInfluences.forEach((_, i) => { const osc = (Math.sin(t * (breathe - i * 0.05) * (1 + keyReact * 3) + i * 1.7) + 1) * 0.5; m.morphTargetInfluences[i] = Math.min(1, osc * ((0.84 - i * 0.12) * (auto + camo * 0.6) + keyReact * 0.8)); }));
      if (Object.keys(bones).length) idleRig(t, auto + react);
      const s = 1 + Math.sin(t * 22) * 0.012 * surge; current.scale.setScalar(s);
      modelScreen.copy(current.position).project(camera);
      const d = Math.hypot(modelScreen.x - ndc.x, (modelScreen.y + 0.1) - ndc.y);
      near += (Math.max(0, 1 - d / 0.7) - near) * Math.min(1, dt * 2);
      current.position.z = near * 2.2;   // comes up to 2.2 units closer
    }

    // Scroll: descend toward the water; the ground flows faster, the fog thickens.
    panVel.multiplyScalar(Math.pow(0.35, dt));
    groundMap.offset.x += panVel.x * dt; groundMap.offset.y += panVel.y * dt - dt * (0.004 * auto + 0.02 * scrollP + energy * 0.01);
    groundN.offset.copy(groundMap.offset);
    scene.fog.density = 0.06 + scrollP * 0.05;

    ripples.forEach((r) => { r.userData.age += dt; const k = r.userData.age / r.userData.life; r.scale.setScalar(0.2 + k * r.userData.grow); r.material.opacity = Math.max(0, (1 - k)) * 0.55; });
    for (let i = ripples.length - 1; i >= 0; i--) if (ripples[i].userData.age > ripples[i].userData.life) { scene.remove(ripples[i]); ripples[i].material.dispose(); ripples.splice(i, 1); }

    advanceFrames(dt);

    // Camera: pointer parallax plus the scroll descent.
    const tgt = camBase.clone().add(new THREE.Vector3(pointer.x * 2.59, -pointer.y * 1.3 - scrollP * 0.9, -scrollP * 1.6));
    camera.position.lerp(tgt, 0.05);
    camera.lookAt((current ? current.position.x * 0.55 : 0) + pointer.x * 0.65, 0.3 - pointer.y * 0.32 - scrollP * 0.5, 0);
    renderer.render(scene, camera);
    requestAnimationFrame(frame);
  }
  const setRunning = () => {
    const want = visible && !document.hidden;
    if (want) playFrame(frameIdx); else frameTex.forEach((t) => t.userData.video && t.userData.video.pause());
    if (want && !running) { running = true; clock.getDelta(); requestAnimationFrame(frame); } else if (!want) running = false;
  };
  new IntersectionObserver((es) => { visible = es[0].isIntersecting; setRunning(); }).observe(hero);
  document.addEventListener('visibilitychange', setRunning);

  // ---- clicks and holds ----
  let swapping = false;
  async function nextModel() {
    if (swapping) return; swapping = true; hero.setAttribute('aria-busy', 'true');
    const i = (order.indexOf(modelName) + 1) % order.length;
    try { await show(order[i]); load(order[(i + 1) % order.length]).catch(() => {}); } catch (err) { console.error(err); }
    hero.removeAttribute('aria-busy'); swapping = false;
  }
  const box = $('shotbox');
  function openShot() {
    if (!box) return;
    const f = C.frames[frameIdx], stage = box.querySelector('.shotbox__stage'); stage.innerHTML = '';
    const el = f.video ? Object.assign(document.createElement('video'), { src: toBlobUrl(pickClip(f)), autoplay: true, loop: true, muted: true, playsInline: true, controls: true })
                       : Object.assign(document.createElement('img'), { src: f.src, alt: f.caption });
    stage.appendChild(el); setText(box.querySelector('.shotbox__cap'), f.caption);
    box.dataset.open = 'true'; box.querySelector('button').focus();
  }
  const closeShot = () => { if (box) { box.dataset.open = 'false'; box.querySelector('.shotbox__stage').innerHTML = ''; } };
  if (box) { box.addEventListener('click', (ev) => { if (ev.target === box || ev.target.closest('button')) closeShot(); }); document.addEventListener('keydown', (ev) => { if (ev.key === 'Escape') closeShot(); }); }

  const hitTest = () => {
    ray.setFromCamera(ndc, camera);
    if (current && ray.intersectObject(current, true).length) return 'model';
    if (ray.intersectObject(screen).length) return 'screen';
    return 'ground';
  };
  const ignore = (ev) => ev.target.closest('a,button,input,form');
  hero.addEventListener('pointerdown', (ev) => { if (ignore(ev)) return; onMove(ev); holding = true; heldLong = false; holdStart = performance.now(); });
  const release = () => {
    if (!holding) return; holding = false;
    if (heldLong && energy > 0.15 && current) ripple(current.position.clone().setY(-1.35), 1 + energy * 1.5);
  };
  addEventListener('pointerup', release); addEventListener('pointercancel', release);
  hero.addEventListener('pointermove', (ev) => { if (ignore(ev)) { hero.style.cursor = ''; return; } const h = hitTest(); hero.style.cursor = h === 'ground' ? 'crosshair' : 'pointer'; });
  hero.addEventListener('click', (ev) => {
    if (ignore(ev) || heldLong) return;
    const h = hitTest();
    if (h === 'model') nextModel();
    else if (h === 'screen') openShot();
    else if (ray.ray.intersectPlane(groundPlane, groundHit)) {
      ripple(groundHit.clone(), Math.min(1.2, 0.5 + speed * 2));
      panVel.x += -groundHit.x * 0.012; panVel.y += groundHit.z * 0.012;   // the painted ground slides away from the click
    }
  });
  hero.addEventListener('contextmenu', (ev) => { if (!ignore(ev)) ev.preventDefault(); });
  document.querySelectorAll('[data-hero-next]').forEach((b) => b.addEventListener('click', nextModel));
  document.querySelectorAll('[data-hero-shot]').forEach((b) => b.addEventListener('click', openShot));

  // ---- start ----
  const texReady = new Promise((r) => { const check = () => (loaded >= texKeys.length + C.frames.length ? r() : setTimeout(check, 30)); check(); });
  texReady.then(() => show(modelName)).then(() => {
    tick(); layout(); updateScroll(); showFrameCaption(0); screenLight.color.copy(colorOf(0));
    load(order[(order.indexOf(modelName) + 1) % order.length]).catch(() => {});
    hero.classList.add('is-live'); setTimeout(() => { if (progress) progress.style.opacity = 0; }, 400);
    setRunning();
  }).catch((err) => { console.error(err); fail('The 3D scene failed to load; showing a still'); });
})();
