// Style 6 made with THREE.JS instead of the picture maker (a test for the owner, 14 Nov 2026). The same comic page,
// camera, narration boxes and sound words as the approved comic, but every panel is a live 3D scene drawn in a comic look:
// flat toon colours, black ink outlines and halftone dots in the shadows. Each panel freezes on its own moment, so the
// pulled-back page at the end reads as a real comic strip. One 3D canvas draws all six panels (each clipped to its
// panel shape), so the whole page costs one graphics context.
import React, { useMemo } from 'react';
import * as THREE from 'three';
import { ThreeCanvas } from '@remotion/three';
import { useFrame } from '@react-three/fiber';
import { AbsoluteFill, Easing, interpolate, useCurrentFrame } from 'remotion';
import { Soundtrack, Sfx } from '../../shared/Soundtrack';
import { ensureFonts } from '../../shared/fonts';
import { WORDS, K, STEPS, at } from '../../shared/timing';
import { clamp, easeInOut, mix, pop, prog } from '../../shared/anim';
import { HT_U, INK_U, ink, toonMat } from '../../shared/three/toon';
import { SWG, cutFaceTex, sandwichGeo } from '../../shared/three/sandwichGeo';

ensureFonts('Bangers', 'Comic Neue');
const INKC = '#111111', PAPER = '#FBF5E6', CAPTION = '#FFE45C';
type V3 = [number, number, number];
type Pt = [number, number];

// ---------- the page (page px), as in the approved comic ----------
type Panel = { x: number; y: number; w: number; h: number; poly: Pt[]; words: [number, number]; sfx: string; sfxAt: number;
  sfxPos: [number, number]; sfxRot: number; sfxColor: string; win: [number, number] };
const rect = (x: number, y: number, w: number, h: number): Pt[] => [[x, y], [x + w, y], [x + w, y + h], [x, y + h]];
const PANELS: Panel[] = [
  { x: 40, y: 40, w: 640, h: 700, poly: rect(40, 40, 640, 700), words: [0, 4], sfx: 'FLOP!', sfxAt: at(K.slices) - 2, sfxPos: [470, 590], sfxRot: -12, sfxColor: '#FF5A36', win: [0, STEPS.bread.to] },
  { x: 710, y: 40, w: 640, h: 700, poly: rect(710, 40, 640, 700), words: [5, 12], sfx: 'SHLUK!', sfxAt: at(K.into) - 2, sfxPos: [170, 590], sfxRot: 10, sfxColor: '#FFB020', win: [STEPS.knife.from, STEPS.knife.to] },
  { x: 1380, y: 40, w: 980, h: 700, poly: rect(1380, 40, 980, 700), words: [13, 19], sfx: 'SWOOSH!', sfxAt: at(K.spread) - 2, sfxPos: [760, 590], sfxRot: -8, sfxColor: '#36B5FF', win: [STEPS.spread.from, at(K.edges) + 6] },
  { x: 40, y: 770, w: 640, h: 700, poly: rect(40, 770, 640, 700), words: [20, 25], sfx: 'SMOOSH!', sfxAt: at(K.top) - 2, sfxPos: [330, 610], sfxRot: 8, sfxColor: '#FF5A36', win: [STEPS.press.from, STEPS.press.to] },
  { x: 710, y: 770, w: 760, h: 700, poly: [[710, 770], [1470, 770], [710 + 0.92 * 760, 1470], [710, 1470]], words: [26, 31], sfx: 'SHHNK!', sfxAt: at(K.corner2) - 2,
    sfxPos: [560, 610], sfxRot: -14, sfxColor: '#FFB020', win: [STEPS.cut.from, STEPS.cut.to] },
  { x: 1440, y: 770, w: 920, h: 700, poly: [[1440 + 0.07 * 920, 770], [2360, 770], [2360, 1470], [1440, 1470]], words: [32, 35], sfx: 'YUM!', sfxAt: at(K.better),
    sfxPos: [760, 610], sfxRot: -10, sfxColor: '#FF3D7F', win: [STEPS.payoff.from, 450] },
];
const PAGE = { w: 2400, h: 1510 };
const BORDER = 7;
const inner = (p: Panel) => ({ x: p.x + BORDER, y: p.y + BORDER, w: p.w - 2 * BORDER, h: p.h - 2 * BORDER });

// camera per panel: centre + zoom so the panel fills the frame (same moves as the approved comic)
const camFor = (p: Panel) => ({ x: p.x + p.w / 2, y: p.y + p.h / 2, z: Math.min(1920 / (p.w + 70), 1080 / (p.h + 70)), r: 0 });
const KEYS: { f: number; c: { x: number; y: number; z: number; r: number } }[] = [
  { f: 0, c: { ...camFor(PANELS[0]), z: camFor(PANELS[0]).z * 1.12 } }, { f: 64, c: camFor(PANELS[0]) },
  { f: 74, c: { ...camFor(PANELS[1]), r: 1.5 } }, { f: 126, c: { ...camFor(PANELS[1]), r: 0, z: camFor(PANELS[1]).z * 1.04 } },
  { f: 136, c: { ...camFor(PANELS[2]), r: -1.5 } }, { f: 204, c: { ...camFor(PANELS[2]), r: 0, z: camFor(PANELS[2]).z * 1.05 } },
  { f: 216, c: { ...camFor(PANELS[3]), r: 2 } }, { f: 266, c: { ...camFor(PANELS[3]), r: 0, z: camFor(PANELS[3]).z * 1.05 } },
  { f: 276, c: { ...camFor(PANELS[4]), r: -2 } }, { f: 324, c: { ...camFor(PANELS[4]), r: 0, z: camFor(PANELS[4]).z * 1.06 } },
  { f: 334, c: { ...camFor(PANELS[5]), r: 1.5 } }, { f: 384, c: { ...camFor(PANELS[5]), r: 0, z: camFor(PANELS[5]).z * 1.05 } },
  { f: 408, c: { x: PAGE.w / 2, y: PAGE.h / 2, z: Math.min(1920 / (PAGE.w + 60), 1080 / (PAGE.h + 60)), r: 0 } },
  { f: 450, c: { x: PAGE.w / 2, y: PAGE.h / 2, z: Math.min(1920 / (PAGE.w + 60), 1080 / (PAGE.h + 60)) * 0.98, r: 0 } },
];
const camAt = (f: number) => {
  let i = 0;
  while (i < KEYS.length - 2 && f >= KEYS[i + 1].f) i++;
  const a = KEYS[i], b = KEYS[i + 1];
  const move = b.f - a.f <= 26;
  const t = interpolate(f, [a.f, b.f], [0, 1], { extrapolateLeft: 'clamp', extrapolateRight: 'clamp', easing: move ? Easing.bezier(0.8, 0, 0.2, 1) : (x) => x });
  const z = Math.exp(mix(t, Math.log(a.c.z), Math.log(b.c.z)));
  const hw = 960 / z, hh = 540 / z, m = 24;
  const cx = PAGE.w + 2 * m > 2 * hw ? clamp(mix(t, a.c.x, b.c.x), hw - m, PAGE.w - hw + m) : PAGE.w / 2;
  const cy = PAGE.h + 2 * m > 2 * hh ? clamp(mix(t, a.c.y, b.c.y), hh - m, PAGE.h - hh + m) : PAGE.h / 2;
  return { x: cx, y: cy, z, r: mix(t, a.c.r, b.c.r) };
};

// ---------- the 3D world (same layout and sizes as the approved 3D style) ----------
const BOARD_TOP = 0.1;
const A: V3 = [-0.85, BOARD_TOP, 0.25], B: V3 = [0.85, BOARD_TOP, 0.25], JAR: V3 = [1.75, 0, -1.6];
const { TH, PBH } = SWG;
const TOTAL = 2 * TH + PBH;
const COL = { crumb: '#F8E4B2', crust: '#D3893A', pb: '#B96C26', board: '#DDA367', counter: '#F3E6CF', wall: '#BFE2EC', red: '#E2363F',
  glass: '#E6F4F8', steel: '#D9E0E6', handle: '#2B2522', room: '#BFE2EC' };

/** each panel's 3D camera at its local progress u (0..1 through its moment) */
const PCAM: { p0: V3; p1: V3; t0: V3; t1: V3; fov: number }[] = [
  { p0: [0.25, 4.3, 4.7], p1: [0.1, 3.8, 4.1], t0: [0, 0.35, 0.2], t1: [0, 0.3, 0.2], fov: 42 },
  { p0: [2.85, 2.25, 0.75], p1: [2.65, 2.05, 0.45], t0: [1.72, 0.95, -1.55], t1: [1.72, 0.9, -1.55], fov: 40 },
  { p0: [-0.95, 2.75, 2.4], p1: [-0.9, 2.45, 2.05], t0: [-0.85, 0.2, 0.15], t1: [-0.85, 0.2, 0.2], fov: 38 },
  { p0: [0.35, 2.05, 3.7], p1: [0.25, 1.85, 3.35], t0: [0.0, 0.45, 0.25], t1: [-0.1, 0.4, 0.25], fov: 46 },
  { p0: [A[0] + 0.05, 4.45, A[2] + 1.3], p1: [A[0], 4.15, A[2] + 1.2], t0: [A[0], 0.15, A[2] - 0.3], t1: [A[0], 0.15, A[2] - 0.28], fov: 40 },
  { p0: [0, 1.75, 4.7], p1: [0, 1.6, 4.35], t0: [0, 0.22, 0], t1: [0, 0.2, 0], fov: 36 },
];
const localT = (i: number, f: number) => clamp(f, PANELS[i].win[0], PANELS[i].win[1]);
const camSetup = (cam: THREE.PerspectiveCamera, i: number, f: number) => {
  const p = PANELS[i], c = PCAM[i], r = inner(p);
  const u = (localT(i, f) - p.win[0]) / Math.max(1, p.win[1] - p.win[0]);
  const e = easeInOut(u);
  cam.fov = c.fov; cam.aspect = r.w / r.h; cam.near = 0.05; cam.far = 120;
  cam.position.set(mix(e, c.p0[0], c.p1[0]), mix(e, c.p0[1], c.p1[1]), mix(e, c.p0[2], c.p1[2]));
  cam.lookAt(mix(e, c.t0[0], c.t1[0]), mix(e, c.t0[1], c.t1[1]), mix(e, c.t0[2], c.t1[2]));
  cam.updateProjectionMatrix();
  cam.updateMatrixWorld();
  return cam;
};

const G = sandwichGeo(0, 0);
const [S0, S1] = G.seg;
const SEG_LEN = Math.hypot(S1[0] - S0[0], S1[1] - S0[1]);
const SEG_MID: V3 = [(S0[0] + S1[0]) / 2, 0, -(S0[1] + S1[1]) / 2];
const SEG_ANG = Math.atan2(-(S1[1] - S0[1]), S1[0] - S0[0]);
const NORMAL: [number, number] = [-(S1[1] - S0[1]) / SEG_LEN, -(S1[0] - S0[0]) / SEG_LEN]; // world x, z; points to half 0

const buildWorld = () => {
  const scene = new THREE.Scene();
  const M = {
    crumb: toonMat(COL.crumb), crust: toonMat(COL.crust), pb: toonMat(COL.pb), board: toonMat(COL.board), counter: toonMat(COL.counter),
    wall: toonMat(COL.wall), red: toonMat(COL.red), steel: toonMat(COL.steel), handle: toonMat(COL.handle), glassRim: toonMat('#CFE3EA'),
    face: toonMat('#FFFFFF', { map: cutFaceTex(COL.crumb, COL.pb, COL.crust) }),
  };
  // the jar body: glass at the top, peanut butter seen through the glass below
  const jarTex = (() => {
    const c = document.createElement('canvas'); c.width = 4; c.height = 128;
    const g = c.getContext('2d')!;
    g.fillStyle = COL.glass; g.fillRect(0, 0, 4, 128);
    g.fillStyle = COL.pb; g.fillRect(0, 38, 4, 90);
    const t = new THREE.CanvasTexture(c); t.colorSpace = THREE.SRGBColorSpace; t.magFilter = THREE.NearestFilter;
    return t;
  })();
  const jarMat = toonMat('#FFFFFF', { map: jarTex });
  const jarIn = toonMat(COL.glass, { side: THREE.BackSide });

  const hemi = new THREE.HemisphereLight('#FFFFFF', '#D8C7AA', 1.0);
  const sun = new THREE.DirectionalLight('#FFF4E2', 2.35);
  sun.position.set(-3.2, 6.5, 4.2);
  sun.castShadow = true;
  sun.shadow.mapSize.set(2048, 2048);
  Object.assign(sun.shadow.camera, { left: -5, right: 5, top: 5, bottom: -5, near: 0.5, far: 20 });
  sun.shadow.bias = -0.0006;
  scene.add(hemi, sun, sun.target);

  const mesh = (geo: THREE.BufferGeometry, mat: THREE.Material | THREE.Material[], outline = true, cast = true) => {
    const m = new THREE.Mesh(geo, mat);
    m.castShadow = cast; m.receiveShadow = true;
    return ink(m, outline);
  };
  const room = new THREE.Mesh(new THREE.SphereGeometry(60, 24, 12), new THREE.MeshBasicMaterial({ color: COL.room, side: THREE.BackSide }));
  const floor = mesh(new THREE.PlaneGeometry(60, 60), M.counter, false, false);
  floor.rotation.x = -Math.PI / 2;
  const wall = mesh(new THREE.PlaneGeometry(60, 16), M.wall, false, false);
  wall.position.set(0, 8, -5);
  const board = mesh(new THREE.BoxGeometry(4.1, BOARD_TOP, 2.5), M.board);
  board.position.set(0, BOARD_TOP / 2, 0.15);
  scene.add(room, floor, wall, board);

  // jar: outer wall, inner wall, rim, peanut-butter surface, label; and the lid
  const jar = new THREE.Group();
  jar.position.set(...JAR);
  const outer = mesh(new THREE.CylinderGeometry(0.4, 0.4, 1.06, 48, 1, true), jarMat);
  outer.position.y = 0.53;
  const innerW = mesh(new THREE.CylinderGeometry(0.382, 0.382, 1.04, 48, 1, true), jarIn, false, false);
  innerW.position.y = 0.53;
  const rim = mesh(new THREE.TorusGeometry(0.391, 0.024, 10, 48), M.glassRim);
  rim.rotation.x = Math.PI / 2; rim.position.y = 1.06;
  const pbTop = mesh(new THREE.CircleGeometry(0.383, 48), M.pb, false, false);
  pbTop.rotation.x = -Math.PI / 2; pbTop.position.y = 0.74;
  const label = mesh(new THREE.CylinderGeometry(0.408, 0.408, 0.34, 48, 1, true), M.red);
  label.position.y = 0.4;
  jar.add(outer, innerW, rim, pbTop, label);
  const lid = mesh(new THREE.CylinderGeometry(0.43, 0.43, 0.14, 48), M.red);
  const lidG = new THREE.Group();
  lidG.add(lid);
  jar.add(lidG);
  scene.add(jar);

  // slices
  const bread = (geo: THREE.BufferGeometry) => mesh(geo, [M.crumb, M.crust]);
  const aG = new THREE.Group();
  const aBread = bread(G.slice);
  const aPb = mesh(G.pb, M.pb);
  aG.add(aBread, aPb);
  const bG = new THREE.Group();
  const bBread = bread(G.slice);
  bBread.position.y = -TH / 2;
  bG.add(bBread);
  scene.add(aG, bG);

  // the two halves after the cut: outer group (moves, turns) > inner group (puts the half's centre at the origin)
  const halves = G.halves.map((h, i) => {
    const outerG = new THREE.Group(), innerG = new THREE.Group();
    const c: V3 = [h.centroid[0], 0, -h.centroid[1]];
    innerG.position.set(-c[0], 0, -c[2]);
    const bot = bread(h.slice); bot.position.y = 0;
    const pbm = mesh(h.pb, M.pb); pbm.position.y = TH;
    const top = bread(h.slice); top.position.y = TH + PBH;
    const dir = i === 0 ? 1 : -1; // the cut face looks towards -dir * NORMAL
    const face = new THREE.Mesh(new THREE.PlaneGeometry(SEG_LEN * 0.995, TOTAL), M.face);
    face.position.set(SEG_MID[0] - NORMAL[0] * 0.003 * dir, TOTAL / 2, SEG_MID[2] - NORMAL[1] * 0.003 * dir);
    face.rotation.y = Math.atan2(-dir * NORMAL[0], -dir * NORMAL[1]);
    innerG.add(bot, pbm, top, face);
    outerG.add(innerG);
    scene.add(outerG);
    return { outer: outerG, inner: innerG, c, faceDir: [-dir * NORMAL[0], -dir * NORMAL[1]] as [number, number] };
  });

  // the butter knife (tip at the origin, blade up, handle on top) and the chef's knife
  const knife = new THREE.Group();
  const blade = mesh(G.knife, M.steel);
  const handle = mesh(new THREE.BoxGeometry(0.14, 0.55, 0.08), M.handle);
  handle.position.set(0.005, 1.27, 0);
  const blob = mesh(new THREE.SphereGeometry(0.12, 24, 16), M.pb);
  blob.position.set(0.005, 0.17, 0);
  knife.add(blade, handle, blob);
  const chef = new THREE.Group();
  const cBlade = mesh(G.chef, M.steel);
  cBlade.position.set(-0.8, 0, 0);
  const cHandle = mesh(new THREE.BoxGeometry(0.5, 0.13, 0.07), M.handle);
  cHandle.position.set(-1.05, 0.2, 0);
  chef.add(cBlade, cHandle);
  scene.add(knife, chef);

  // every material only draws inside the current panel's shape (stencil = 1)
  scene.traverse((o) => {
    const mm = (o as THREE.Mesh).material;
    if (!mm) return;
    (Array.isArray(mm) ? mm : [mm]).forEach((m) => {
      m.stencilWrite = true; m.stencilRef = 1; m.stencilFunc = THREE.EqualStencilFunc;
      m.stencilFail = THREE.KeepStencilOp; m.stencilZFail = THREE.KeepStencilOp; m.stencilZPass = THREE.KeepStencilOp;
    });
  });
  return { scene, room, floor, wall, board, jar, lidG, aG, aBread, aPb, bG, halves, knife, blob, chef };
};
type World = ReturnType<typeof buildWorld>;

/** put every object where it is at time t (as in the 3D style); panel 5 (index 5) is the hero shot of the two triangles */
const pose = (w: World, t: number, panel: number) => {
  const hero = panel === 5;
  [w.room, w.floor, w.wall, w.board, w.jar, w.aG, w.bG, w.knife, w.chef].forEach((o) => (o.visible = !hero));
  const dropAraw = pop(t, at(K.two) - 6, { damping: 11, stiffness: 120 }), dropBraw = pop(t, at(K.slices) - 6, { damping: 11, stiffness: 120 });
  const dropA = Math.min(1, dropAraw), dropB = Math.min(1, dropBraw);
  const landA = 1 - 0.6 * Math.max(0, dropAraw - 1), landB = 1 - 0.6 * Math.max(0, dropBraw - 1);
  const lid = prog(t, at(K.then) - 4, at(K.dig) + 8, easeInOut);
  const kIn = prog(t, at(K.knife) - 6, at(K.into) + 4, Easing.out(Easing.cubic));
  const dip = prog(t, at(K.into), at(K.peanut) + 4, easeInOut);
  const kOut = prog(t, at(K.butter) - 2, at(K.butter) + 14, easeInOut);
  const go = prog(t, STEPS.spread.from - 8, at(K.spread) + 2, easeInOut);
  const sT = prog(t, at(K.spread), at(K.edges) + 6, (x) => x);
  const pb = prog(t, at(K.spread), at(K.edges) + 6, Easing.inOut(Easing.quad));
  const kAway = prog(t, at(K.edges) + 8, at(K.edges) + 24, Easing.in(Easing.cubic));
  const up = prog(t, at(K.press) - 2, at(K.second) + 6, easeInOut);
  const over = prog(t, at(K.second) - 2, at(K.on) + 2, easeInOut);
  const down = prog(t, at(K.on) - 2, at(K.top) - 1, Easing.in(Easing.quad));
  const squash = t >= at(K.top) - 1 ? Math.sin(clamp((t - at(K.top) + 1) / 10) * Math.PI) * Math.exp(-(t - at(K.top) + 1) / 14) : 0;
  const cutIn = prog(t, at(K.cut) - 6, at(K.corner1), easeInOut);
  const sl = prog(t, at(K.corner1), at(K.corner2) + 4, easeInOut);
  const cutOut = prog(t, at(K.corner2) + 6, at(K.corner2) + 20, Easing.in(Easing.cubic));
  const cut = t >= at(K.corner2) + 4;
  const part = prog(t, at(K.corner2) + 4, at(K.corner2) + 20, Easing.out(Easing.back(1.3)));

  // lid
  w.lidG.position.set(mix(lid, 0, 0.95), 1.16 + Math.sin(lid * Math.PI) * 0.7 - lid * 1.07, mix(lid, 0, -0.45));
  w.lidG.rotation.set(lid * 0.2, lid * Math.PI * 2, lid * Math.PI * 0.95);
  // slice A + peanut butter
  w.aG.visible = !hero && !cut;
  w.aG.position.set(A[0], 0, A[2]);
  w.aG.scale.set(1 + 0.04 * squash, 1 - 0.1 * squash, 1 + 0.04 * squash);
  w.aBread.position.set(0, BOARD_TOP + (1 - dropA) * 3, 0);
  w.aBread.rotation.set(0, (1 - dropA) * 0.5, 0);
  w.aBread.scale.set(1, landA, 1);
  w.aPb.visible = pb > 0;
  w.aPb.position.set(0, BOARD_TOP + TH, 0);
  w.aPb.scale.set(0.12 + 0.88 * pb, 1, 0.12 + 0.88 * pb);
  // slice B: lifts, turns over and lands on A
  w.bG.visible = !hero && !cut && dropB > 0.01;
  w.bG.position.set(mix(over, B[0], A[0]), BOARD_TOP + TH / 2 + up * (1 - down) + down * (TH + PBH) + (1 - dropB) * 3, mix(over, B[2], A[2]));
  w.bG.rotation.set(0, (1 - dropB) * -0.4, over * Math.PI);
  w.bG.scale.set(1 + 0.04 * squash * down, (1 - 0.1 * squash * down) * landB, 1 + 0.04 * squash * down);
  // the halves
  w.halves.forEach((h, i) => {
    h.outer.visible = cut || hero;
    if (hero) {
      // stand each triangle with its cut face (the layers) towards the camera, slightly turned and bobbing
      const inn = pop(t, at(K.because) - 6, { damping: 12, stiffness: 160 });
      const s = 0.7 + 0.3 * inn;
      // the triangle's long side (the cut, with the layers) faces the camera; tipped back so the triangle itself shows
      const yaw = -Math.atan2(h.faceDir[0], h.faceDir[1]) + (i === 0 ? 0.3 : -0.3) + Math.sin((t - 331) / 26 + i * 2) * 0.1;
      h.inner.position.set(-h.c[0], -TOTAL / 2, -h.c[2]);
      h.outer.position.set(i === 0 ? 0.66 : -0.66, 0.16 + Math.sin((t - 331) / 18 + i * 1.7) * 0.04, 0);
      h.outer.rotation.set(0.55, yaw, 0);
      h.outer.scale.setScalar(s * 0.94);
    } else {
      h.inner.position.set(-h.c[0], 0, -h.c[2]);
      const dir = i === 0 ? 1 : -1;
      const off = 0.22 * part;
      h.outer.position.set(A[0] + h.c[0] + NORMAL[0] * off * dir, BOARD_TOP, A[2] + h.c[2] + NORMAL[1] * off * dir);
      h.outer.rotation.set(0, 0, 0);
      h.outer.scale.setScalar(1);
    }
  });
  // butter knife (steps 2-3)
  let kp: V3 = [JAR[0], mix(kIn, 3.2, 1.25) - dip * 0.42 + kOut * 0.85, JAR[2]];
  w.knife.quaternion.identity();
  const blob = t < STEPS.spread.from ? clamp(kOut * 2.5) : 1 - pb;
  if (t >= STEPS.spread.from - 8) {
    // spreading with the flat of the blade: tip on the bread, blade lying to the right, handle raised a little
    const zig = Math.sin(sT * Math.PI * 5);
    kp = [mix(go, JAR[0], A[0] - 0.3 + zig * 0.22) + kAway * 2.4, mix(go, 2.1, A[1] + TH + PBH * pb + 0.012) + kAway * 1.4, mix(go, JAR[2], A[2] + mix(sT, -0.32, 0.32)) - kAway * 1.4];
    const flat = new THREE.Quaternion().setFromEuler(new THREE.Euler(-Math.PI / 2, 0, -Math.PI / 2, 'XYZ'));
    const tilt = new THREE.Quaternion().setFromAxisAngle(new THREE.Vector3(0, 0, 1), 0.2 + zig * 0.04);
    const yaw = new THREE.Quaternion().setFromAxisAngle(new THREE.Vector3(0, 1, 0), 0.32 + zig * 0.12);
    w.knife.quaternion.slerp(yaw.multiply(tilt).multiply(flat), go);
  }
  w.knife.visible = !hero && t >= at(K.knife) - 6 && kAway < 1;
  w.knife.position.set(...kp);
  w.blob.visible = blob > 0.01;
  w.blob.scale.set(blob, blob * 1.25, blob);
  // chef's knife (step 5): upright in the plane of the cut, edge down, slicing along the diagonal
  w.chef.visible = !hero && cutIn > 0 && cutOut < 1;
  const along = mix(sl, -0.4, 0.4) * SEG_LEN;
  const ux = Math.cos(SEG_ANG), uz = Math.sin(SEG_ANG);
  w.chef.position.set(A[0] + SEG_MID[0] + along * ux, mix(cutIn, 1.5, BOARD_TOP + TOTAL + 0.06) - sl * (TOTAL + 0.04) + cutOut * 1.5, A[2] + SEG_MID[2] + along * uz);
  w.chef.rotation.set(0, -SEG_ANG, 0);
};

// the stencil masks: one flat shape per panel in page px
const buildMasks = () => {
  const scene = new THREE.Scene();
  const cam = new THREE.OrthographicCamera(0, PAGE.w, 0, -PAGE.h, -1, 1);
  const mat = new THREE.MeshBasicMaterial({ colorWrite: false, depthWrite: false, depthTest: false, stencilWrite: true, stencilRef: 1,
    stencilFunc: THREE.AlwaysStencilFunc, stencilZPass: THREE.ReplaceStencilOp, stencilFail: THREE.ReplaceStencilOp, stencilZFail: THREE.ReplaceStencilOp });
  const meshes = PANELS.map((p) => {
    // the panel shape, shrunk by the ink border
    const cx = p.x + p.w / 2, cy = p.y + p.h / 2;
    const pts = p.poly.map(([x, y]) => new THREE.Vector2(x + Math.sign(cx - x) * BORDER, -(y + Math.sign(cy - y) * BORDER)));
    const m = new THREE.Mesh(new THREE.ShapeGeometry(new THREE.Shape(pts)), mat);
    scene.add(m);
    return m;
  });
  return { scene, cam, meshes };
};

const DPR = 1.5;
const Renderer: React.FC<{ f: number }> = ({ f }) => {
  const world = useMemo(buildWorld, []);
  const masks = useMemo(buildMasks, []);
  const cams = useMemo(() => PANELS.map(() => new THREE.PerspectiveCamera()), []);
  const view = camAt(f);
  useFrame(({ gl }) => {
    gl.autoClear = false;
    gl.setScissorTest(false);
    gl.setViewport(0, 0, PAGE.w, PAGE.h);
    gl.setClearColor(0x000000, 0);
    gl.clear(true, true, true);
    // only the panels the page camera can see
    const hw = 960 / view.z + 160, hh = 540 / view.z + 160;
    PANELS.forEach((p, i) => {
      if (p.x > view.x + hw || p.x + p.w < view.x - hw || p.y > view.y + hh || p.y + p.h < view.y - hh) return;
      const r = inner(p);
      gl.setScissorTest(false);
      gl.setViewport(0, 0, PAGE.w, PAGE.h);
      gl.clear(false, false, true);
      masks.meshes.forEach((m, k) => (m.visible = k === i));
      gl.render(masks.scene, masks.cam);
      const y = PAGE.h - r.y - r.h;
      gl.setViewport(r.x, y, r.w, r.h);
      gl.setScissor(r.x, y, r.w, r.h);
      gl.setScissorTest(true);
      gl.clear(false, true, false);
      INK_U.thickness.value = 3.0;
      INK_U.resolution.value.set(r.w, r.h);
      HT_U.cell.value = 10;
      HT_U.strength.value = 0.42;
      pose(world, localT(i, f), i);
      gl.render(world.scene, camSetup(cams[i], i, f));
    });
    gl.setScissorTest(false);
  }, 1);
  return null;
};

// panel 5's cut line on screen: the sandwich's corner-to-corner line seen through the panel's own 3D camera
const cutLineOnScreen = (f: number) => {
  const cam = camSetup(new THREE.PerspectiveCamera(), 4, f);
  const r = inner(PANELS[4]);
  const P = (s: [number, number]) => {
    const v = new THREE.Vector3(A[0] + s[0], BOARD_TOP + TOTAL, A[2] - s[1]).project(cam);
    return [(v.x + 1) / 2 * r.w, (1 - v.y) / 2 * r.h] as Pt;
  };
  return [P(S0), P(S1)] as const;
};

const Slash: React.FC<{ f: number }> = ({ f }) => {
  const slash = prog(f, at(K.corner1) - 2, at(K.corner2) + 2, Easing.out(Easing.quad));
  const fade = prog(f, at(K.corner2) + 4, at(K.corner2) + 14);
  if (slash <= 0 || fade >= 1) return null;
  const [a0, b0] = cutLineOnScreen(f);
  const d: Pt = [b0[0] - a0[0], b0[1] - a0[1]];
  const L = Math.hypot(d[0], d[1]);
  const n: Pt = [d[1] / L, -d[0] / L];
  const a: Pt = [a0[0] - d[0] * 0.12, a0[1] - d[1] * 0.12], b: Pt = [b0[0] + d[0] * 0.1, b0[1] + d[1] * 0.1];
  const x = mix(slash, a[0], b[0]), y = mix(slash, a[1], b[1]);
  const r = inner(PANELS[4]);
  return (
    <svg width={r.w} height={r.h} style={{ position: 'absolute', left: 0, top: 0, overflow: 'visible', opacity: 1 - fade }}>
      {[-36, -18, 18, 36].map((o, i) => (
        <line key={i} x1={a[0] - d[0] * 0.08 + n[0] * o} y1={a[1] - d[1] * 0.08 + n[1] * o} x2={x + n[0] * o} y2={y + n[1] * o} stroke={INKC} strokeWidth={3} opacity={0.6} />
      ))}
      <line x1={a[0]} y1={a[1]} x2={x} y2={y} stroke={INKC} strokeWidth={26} strokeLinecap="round" />
      <line x1={a[0]} y1={a[1]} x2={x} y2={y} stroke="#FFFFFF" strokeWidth={14} strokeLinecap="round" />
      <line x1={a[0]} y1={a[1]} x2={x} y2={y} stroke="#9BE3FF" strokeWidth={5} strokeLinecap="round" />
    </svg>
  );
};

// panel 6 background: the comic sunburst (under the 3D canvas, which is see-through in that panel)
const Sunburst: React.FC<{ f: number }> = ({ f }) => {
  const r = inner(PANELS[5]);
  const spin = (f - at(K.because)) * 0.25;
  return (
    <svg width={r.w} height={r.h} style={{ position: 'absolute', left: r.x, top: r.y }}>
      <rect width={r.w} height={r.h} fill="#FFC93C" />
      {Array.from({ length: 18 }).map((_, i) => {
        const a0 = ((i / 18) * 360 + spin) * Math.PI / 180, a1 = (((i + 0.5) / 18) * 360 + spin) * Math.PI / 180, R = 1200;
        return <path key={i} d={`M ${r.w / 2} ${r.h / 2} L ${r.w / 2 + Math.cos(a0) * R} ${r.h / 2 + Math.sin(a0) * R} L ${r.w / 2 + Math.cos(a1) * R} ${r.h / 2 + Math.sin(a1) * R} Z`} fill="#FF8A1F" opacity={0.85} />;
      })}
      <circle cx={r.w / 2} cy={r.h / 2} r={180} fill="#FFE27A" opacity={0.9} />
    </svg>
  );
};

const Stars: React.FC<{ f: number }> = ({ f }) => {
  const r = inner(PANELS[5]);
  if (f < STEPS.payoff.from) return null;
  return (
    <>
      {[[0.16, 0.2], [0.86, 0.22], [0.12, 0.78], [0.9, 0.7]].map(([sx, sy], i) => {
        const t = ((f + i * 9) % 36) / 36;
        return <svg key={i} width={70} height={70} viewBox="-35 -35 70 70" style={{ position: 'absolute', left: sx * r.w - 35, top: sy * r.h - 35, transform: `scale(${Math.sin(t * Math.PI)})` }}>
          <path d="M 0 -32 L 7 -7 L 32 0 L 7 7 L 0 32 L -7 7 L -32 0 L -7 -7 Z" fill="#FFFFFF" stroke={INKC} strokeWidth={4} />
        </svg>;
      })}
    </>
  );
};

// the narration box: the panel's words, typed in as they are spoken
const Caption: React.FC<{ p: Panel; f: number }> = ({ p, f }) => {
  const [w0, w1] = p.words;
  const shown = WORDS.slice(w0, w1 + 1).filter((w) => f >= w.fs - 2).map((w) => w.w.toUpperCase());
  if (!shown.length) return null;
  const lead = w0 > 0 && p.words[0] !== 20 ? '…' : '';
  const box = pop(f, WORDS[w0].fs - 4, { damping: 14, stiffness: 220 });
  return (
    <div style={{ position: 'absolute', left: 22, top: 22, maxWidth: p.w * 0.72, background: CAPTION, border: `5px solid ${INKC}`, padding: '12px 18px',
      fontFamily: 'Comic Neue', fontWeight: 700, fontSize: 40, lineHeight: 1.12, color: INKC, letterSpacing: '0.02em', boxShadow: '6px 6px 0 rgba(0,0,0,.85)',
      transform: `scale(${0.85 + 0.15 * box})`, transformOrigin: '0 0', opacity: clamp(box * 2) }}>
      {lead}{shown.join(' ')}
    </div>
  );
};

const SfxWord: React.FC<{ p: Panel; f: number }> = ({ p, f }) => {
  const t = f - p.sfxAt;
  if (t < 0) return null;
  const s = pop(f, p.sfxAt, { damping: 7, stiffness: 260, mass: 0.6 });
  const shake = t < 10 ? Math.sin(t * 2.6) * (10 - t) * 0.6 : 0;
  return (
    <div style={{ position: 'absolute', left: p.sfxPos[0], top: p.sfxPos[1], transform: `translate(-50%, -50%) rotate(${p.sfxRot + shake}deg) scale(${s})`,
      fontFamily: 'Bangers', fontSize: p.sfx.length > 5 ? 120 : 140, color: p.sfxColor, letterSpacing: '0.04em', whiteSpace: 'nowrap',
      WebkitTextStroke: `10px ${INKC}`, paintOrder: 'stroke fill', textShadow: `8px 8px 0 ${INKC}` }}>{p.sfx}</div>
  );
};

const clipOf = (p: Panel) => {
  const r = inner(p);
  return `polygon(${p.poly.map(([x, y]) => `${x - r.x}px ${y - r.y}px`).join(', ')})`;
};

export const Comic3D: React.FC = () => {
  const f = useCurrentFrame();
  const cam = camAt(f);
  const prev = camAt(Math.max(0, f - 1));
  const speed = Math.hypot(cam.x - prev.x, cam.y - prev.y) * cam.z;
  const blur = f < 395 ? Math.min(6, speed / 40) : 0;
  const end = prog(f, 410, 426, Easing.out(Easing.back(1.8)));
  return (
    <AbsoluteFill style={{ background: '#1E1E1E', overflow: 'hidden' }}>
      <AbsoluteFill style={{ transform: `translate(960px, 540px) rotate(${cam.r}deg) scale(${cam.z}) translate(${-cam.x}px, ${-cam.y}px)`, transformOrigin: '0 0',
        filter: blur > 0.3 ? `blur(${blur}px)` : undefined }}>
        <div style={{ position: 'absolute', left: 0, top: 0, width: PAGE.w, height: PAGE.h, background: PAPER, boxShadow: '0 30px 80px rgba(0,0,0,.5)' }}>
          <div style={{ position: 'absolute', inset: 0, backgroundImage: 'radial-gradient(rgba(120,90,40,.10) 1px, transparent 1.2px)', backgroundSize: '9px 9px' }} />
          <Sunburst f={f} />
          <ThreeCanvas width={PAGE.w} height={PAGE.h} dpr={DPR} flat shadows="percentage" gl={{ antialias: true, alpha: true, stencil: true }}
            style={{ position: 'absolute', left: 0, top: 0 }}>
            <Renderer f={f} />
          </ThreeCanvas>
          {/* inside each panel: printed-dot texture, narration box, sound word (and the cut slash / stars) */}
          {PANELS.map((p, i) => {
            const r = inner(p);
            return (
              <div key={i} style={{ position: 'absolute', left: r.x, top: r.y, width: r.w, height: r.h, clipPath: clipOf(p), overflow: 'hidden' }}>
                <div style={{ position: 'absolute', inset: 0, backgroundImage: 'radial-gradient(rgba(0,0,0,.10) 1.2px, transparent 1.6px)', backgroundSize: '7px 7px', mixBlendMode: 'multiply' }} />
                {i === 4 ? <Slash f={f} /> : null}
                {i === 5 ? <Stars f={f} /> : null}
                <Caption p={p} f={f} />
                <SfxWord p={p} f={f} />
              </div>
            );
          })}
          {/* the ink borders of the panels */}
          <svg width={PAGE.w} height={PAGE.h} style={{ position: 'absolute', left: 0, top: 0 }}>
            {PANELS.map((p, i) => (
              <polygon key={i} points={p.poly.map(([x, y]) => `${x},${y}`).join(' ')} fill="none" stroke={INKC} strokeWidth={BORDER * 2} strokeLinejoin="miter" />
            ))}
          </svg>
        </div>
      </AbsoluteFill>
      {f >= 408 ? (
        <div style={{ position: 'absolute', left: 960, top: 540, transform: `translate(-50%, -50%) rotate(-8deg) scale(${end})`, background: CAPTION,
          border: `8px solid ${INKC}`, boxShadow: '12px 12px 0 #111', padding: '18px 44px', fontFamily: 'Bangers', fontSize: 96, letterSpacing: '0.05em', color: INKC, whiteSpace: 'nowrap' }}>
          TRIANGLES TASTE BETTER!
        </div>
      ) : null}
      <Soundtrack sfx={SFX} />
    </AbsoluteFill>
  );
};

const SFX: Sfx[] = [
  ...[66, 128, 206, 268, 326].map((t) => ({ at: t, file: 'page.wav', vol: 0.35 })),
  { at: PANELS[0].sfxAt, file: 'card.wav', vol: 0.4 }, { at: PANELS[1].sfxAt, file: 'smack.wav', vol: 0.45 },
  { at: PANELS[2].sfxAt, file: 'swish1.wav', vol: 0.35 }, { at: PANELS[3].sfxAt, file: 'thud.wav', vol: 0.45 },
  { at: PANELS[4].sfxAt, file: 'whip.wav', vol: 0.5 }, { at: PANELS[5].sfxAt, file: 'sparkle.wav', vol: 0.3 },
  { at: 386, file: 'whoosh.wav', vol: 0.35 }, { at: 410, file: 'thud.wav', vol: 0.35 },
];
