// Style 5 made with THREE.JS instead of the picture maker (a test for the owner, 14 Nov 2026). The same board, camera,
// labels, arrows and timing as the approved whiteboard, but every drawing comes from 3D models: the pen strokes are worked
// out from the models' outlines and edges as the camera sees them (hidden lines removed), the colour fills are three.js
// renders of the same models in flat marker colours, and the drawing hand is a 3D cartoon hand holding a marker.
// Everything is made in the browser when the video opens; no picture files are used.
import React, { useMemo } from 'react';
import * as THREE from 'three';
import { AbsoluteFill, Easing, Img, interpolate, useCurrentFrame } from 'remotion';
import { Soundtrack, Sfx } from '../../shared/Soundtrack';
import { ensureFonts } from '../../shared/fonts';
import { clamp, easeInOut, mix, prog, rand } from '../../shared/anim';
import { HT_U, INK_U, capsule, ink, toonMat } from '../../shared/three/toon';
import { LineArt, LineObj, lineArt, projector } from '../../shared/three/lineart';
import { SWG, cutFaceTex, sandwichGeo } from '../../shared/three/sandwichGeo';

ensureFonts('Permanent Marker');
const INKC = '#1C1C1E', BLUE = '#1E5BB8', RED = '#D62F2F';
const MARKER = 'Permanent Marker';
type Pt = [number, number];
type V3 = [number, number, number];

// ---------- the board: six cells in a snake (1 2 3 / 6 5 4), as in the approved whiteboard ----------
const SIZE = 560;
const CELLS: Pt[] = [[400, 380], [1200, 380], [2000, 380], [2000, 1110], [1200, 1110], [400, 1110]];
const DRAW = [
  { name: 'bread', draw: [12, 48], color: [48, 58], label: '2 slices', write: [50, 62] },
  { name: 'jar', draw: [68, 108], color: [108, 116], label: 'dig in!', write: [110, 122] },
  { name: 'spread', draw: [128, 166], color: [168, 180], label: 'to the edges!', write: [176, 192] },
  { name: 'stack', draw: [206, 240], color: [240, 248], label: 'press it down', write: [244, 258] },
  { name: 'cut', draw: [268, 294], color: [296, 304], label: 'corner to corner', write: [300, 316] },
  { name: 'halves', draw: [330, 354], color: [354, 362], label: 'triangles taste better!', write: [356, 376] },
] as const;

// ---------- the six drawings as 3D scenes ----------
const COL = { crumb: '#F7DD98', crust: '#DE9A52', pb: '#C47A30', glass: '#D6ECF4', red: '#E64B4B', steel: '#C9D1D8', handle: '#5E5650' };

type Built = { art: LineArt[]; color: string[]; cut: [Pt, Pt]; hand: { url: string; w: number; h: number; tip: Pt; sleeve: { a: Pt; b: Pt; r: number; ink: number } } };

const build = (): Built => {
  const G = sandwichGeo(0, 0);
  const { TH, PBH } = SWG;
  const TOTAL = 2 * TH + PBH;
  const M = {
    crumb: toonMat(COL.crumb), crust: toonMat(COL.crust), pb: toonMat(COL.pb), red: toonMat(COL.red, { side: THREE.DoubleSide }),
    steel: toonMat(COL.steel), handle: toonMat(COL.handle),
  };
  const jarTex = (() => {
    const c = document.createElement('canvas'); c.width = 4; c.height = 128;
    const g = c.getContext('2d')!;
    g.fillStyle = COL.glass; g.fillRect(0, 0, 4, 128);
    g.fillStyle = COL.pb; g.fillRect(0, 38, 4, 90);
    const t = new THREE.CanvasTexture(c); t.colorSpace = THREE.SRGBColorSpace; t.magFilter = THREE.NearestFilter;
    return t;
  })();
  const jarMat = toonMat('#FFFFFF', { map: jarTex, side: THREE.DoubleSide });
  const faceMat = toonMat('#FFFFFF', { map: cutFaceTex(COL.crumb, COL.pb, COL.crust), side: THREE.DoubleSide });
  const bread = (parent: THREE.Object3D) => { const m = new THREE.Mesh(G.slice, [M.crumb, M.crust]); parent.add(m); return m; };
  const add = (geo: THREE.BufferGeometry, mat: THREE.Material | THREE.Material[], parent: THREE.Object3D) => { const m = new THREE.Mesh(geo, mat); parent.add(m); return m; };
  const lit = () => {
    const s = new THREE.Scene();
    s.add(new THREE.HemisphereLight('#FFFFFF', '#E9DDC9', 1.25));
    const d = new THREE.DirectionalLight('#FFFFFF', 2.0); d.position.set(-2, 5, 3);
    s.add(d, d.target);
    return s;
  };
  const camera = (pos: V3, target: V3, fov: number) => {
    const c = new THREE.PerspectiveCamera(fov, 1, 0.05, 50);
    c.position.set(...pos); c.lookAt(...target); c.updateMatrixWorld(); c.updateProjectionMatrix();
    return c;
  };
  const knifeGroup = (parent: THREE.Object3D) => {
    const k = new THREE.Group(); parent.add(k);
    const blade = add(G.knife, M.steel, k);
    const handle = add(new THREE.BoxGeometry(0.14, 0.55, 0.08), M.handle, k);
    handle.position.set(0.005, 1.27, 0);
    return { k, blade, handle };
  };
  // detail lines that lie on the bread top (in the slice's own space): the inner crust line and a few crumb holes
  const crustLine = (y: number, k = 0.86) => { const p = G.outline.map(([x, z]) => new THREE.Vector3(x * k, y, -z * k)); p.push(p[0].clone()); return p; };
  const crumbs = (seed: number, y: number, n = 7) => Array.from({ length: n }, (_, i) => {
    const cx = (rand(seed + i * 3) - 0.5) * 0.78, cz = (rand(seed + i * 3 + 1) - 0.5) * 0.7, r = 0.022 + rand(seed + i * 3 + 2) * 0.022, a0 = rand(seed + i * 5) * 6;
    return Array.from({ length: 9 }, (_, j) => { const a = a0 + (j / 8) * 4.3; return new THREE.Vector3(cx + Math.cos(a) * r, y, cz + Math.sin(a) * r * 0.85); });
  });
  const swirl = (y: number) => [[-0.18, 0.06, 0.24, 0.4, 3.3], [0.16, -0.12, 0.2, 3.6, 6.4], [0.02, 0.2, 0.13, 1.2, 3.9]].map(([cx, cz, r, a0, a1]) =>
    Array.from({ length: 16 }, (_, j) => { const a = a0 + ((a1 - a0) * j) / 15; return new THREE.Vector3(cx + Math.cos(a) * r, y, cz + Math.sin(a) * r * 0.8); }));

  const scenes: { scene: THREE.Scene; cam: THREE.PerspectiveCamera; objs: LineObj[] }[] = [];
  // 1 bread: two slices
  {
    const s = lit();
    const a = bread(s); a.position.set(-0.8, 0, 0.05); a.rotation.y = 0.12;
    const b = bread(s); b.position.set(0.8, 0, -0.05); b.rotation.y = -0.1;
    scenes.push({ scene: s, cam: camera([0, 3.0, 2.7], [0, 0, 0.02], 41), objs: [
      { mesh: a, order: 0, details: [crustLine(TH + 0.003), ...crumbs(11, TH + 0.003)] },
      { mesh: b, order: 1, details: [crustLine(TH + 0.003), ...crumbs(41, TH + 0.003)] },
    ] });
  }
  // 2 jar: open jar of peanut butter, the knife dug in, the lid beside it
  {
    const s = lit();
    const outer = add(new THREE.CylinderGeometry(0.4, 0.4, 1.06, 48, 1, true), jarMat, s); outer.position.y = 0.53;
    const label = add(new THREE.CylinderGeometry(0.407, 0.407, 0.34, 48, 1, true), M.red, s); label.position.y = 0.4;
    const pbTop = add(new THREE.CircleGeometry(0.392, 48), M.pb, s); pbTop.rotation.x = -Math.PI / 2; pbTop.position.y = 0.74;
    const { k, blade, handle } = knifeGroup(s);
    k.position.set(0.05, 0.6, 0.02); k.rotation.set(0.12, 0.6, -0.3);
    const lid = add(new THREE.CylinderGeometry(0.43, 0.43, 0.14, 48), M.red, s); lid.position.set(-1.0, 0.07, 0.5);
    // two short shine marks on the glass (the outer wall's own space: centre at half height)
    const shine = (th: number, y0: number, y1: number) => [y0, y1].map((y) => new THREE.Vector3(Math.sin(th) * 0.402, y, Math.cos(th) * 0.402));
    scenes.push({ scene: s, cam: camera([0.25, 2.3, 3.4], [-0.15, 0.75, 0.05], 38), objs: [
      { mesh: outer, order: 0, details: [shine(-0.62, 0.27, 0.46), shine(-0.47, 0.31, 0.4)] }, { mesh: label, order: 1 }, { mesh: pbTop, order: 2, details: swirl(0.002).map((l) => l.map((p) => new THREE.Vector3(p.x * 1.2, p.z * -1.2, 0.002))) },
      { mesh: blade, order: 3 }, { mesh: handle, order: 4 }, { mesh: lid, order: 5 },
    ] });
  }
  // 3 spread: the slice covered in peanut butter, the knife lying on it
  {
    const s = lit();
    const a = bread(s);
    const p = add(G.pb, M.pb, s); p.position.y = TH;
    const { k, blade, handle } = knifeGroup(s);
    k.position.set(-0.14, TH + PBH + 0.009, 0.14); k.rotation.set(-Math.PI / 2, 0, -1.04);
    scenes.push({ scene: s, cam: camera([0, 2.85, 2.25], [0.12, 0.1, 0], 37), objs: [
      { mesh: a, order: 0 }, { mesh: p, order: 1, details: swirl(PBH + 0.003) }, { mesh: blade, order: 2 }, { mesh: handle, order: 3 },
    ] });
  }
  // 4 stack: the sandwich, peanut butter squeezing out between the slices
  {
    const s = lit();
    const g = new THREE.Group(); g.rotation.y = 0.42; s.add(g);
    const a = bread(g);
    const p = add(G.pb, M.pb, g); p.position.y = TH; p.scale.set(1.07, 1, 1.07);
    const b = bread(g); b.position.y = TH + PBH;
    scenes.push({ scene: s, cam: camera([1.1, 1.65, 2.5], [0, 0.17, 0], 36), objs: [
      { mesh: a, order: 0 }, { mesh: p, order: 1 }, { mesh: b, order: 2, details: [crustLine(TH + 0.003), ...crumbs(77, TH + 0.003)] },
    ] });
  }
  // 5 cut: seen from straight above, the big knife lying on the corner-to-corner line
  const [S0, S1] = G.seg;
  {
    const s = lit();
    const a = bread(s);
    const p = add(G.pb, M.pb, s); p.position.y = TH;
    const b = bread(s); b.position.y = TH + PBH;
    const u = new THREE.Vector3(S1[0] - S0[0], 0, -(S1[1] - S0[1])).normalize();
    const n = new THREE.Vector3(-u.z, 0, u.x);
    const chef = new THREE.Group(); s.add(chef);
    const cb = add(G.chef, M.steel, chef); cb.position.set(-0.8, 0, 0);
    const ch = add(new THREE.BoxGeometry(0.5, 0.13, 0.07), M.handle, chef); ch.position.set(-1.05, 0.2, 0);
    chef.matrixAutoUpdate = false;
    chef.matrix.makeBasis(u, n, new THREE.Vector3().crossVectors(u, n)).setPosition(0, TOTAL + 0.012, 0);
    chef.updateMatrixWorld(true);
    scenes.push({ scene: s, cam: camera([0, 3.55, 0.2], [0, 0, 0], 35), objs: [
      { mesh: b, order: 0, details: [crustLine(TH + 0.003), ...crumbs(91, TH + 0.003, 6)] }, { mesh: a, order: 1 }, { mesh: p, order: 1 },
      { mesh: cb, order: 2 }, { mesh: ch, order: 3 },
    ] });
  }
  // 6 halves: the two triangles, a little apart, the layers showing on the cut
  {
    const s = lit();
    const nrm = new THREE.Vector3(-(S1[1] - S0[1]), 0, -(S1[0] - S0[0])).normalize();
    const objs: LineObj[] = [];
    G.halves.forEach((h, i) => {
      const g = new THREE.Group(); s.add(g);
      const dir = i === 0 ? 1 : -1;
      // side by side from this camera, each turned so its cut (the three layers) faces us a little
      g.position.copy(nrm).multiplyScalar(0.34 * dir);
      g.rotateY(dir * 0.55);
      const bot = add(h.slice, [M.crumb, M.crust], g);
      const pb = add(h.pb, M.pb, g); pb.position.y = TH;
      const top = add(h.slice, [M.crumb, M.crust], g); top.position.y = TH + PBH;
      // the cut face in colour: crumb / peanut butter / crumb (colour only, it adds no pen lines)
      const segLen = Math.hypot(S1[0] - S0[0], S1[1] - S0[1]);
      const face = add(new THREE.PlaneGeometry(segLen * 0.995, TOTAL), faceMat, g);
      face.position.set((S0[0] + S1[0]) / 2 - nrm.x * 0.003 * dir, TOTAL / 2, -(S0[1] + S1[1]) / 2 - nrm.z * 0.003 * dir);
      face.rotation.y = Math.atan2(-dir * nrm.x, -dir * nrm.z);
      objs.push({ mesh: top, order: i * 3 }, { mesh: pb, order: i * 3 + 1 }, { mesh: bot, order: i * 3 + 2 });
    });
    scenes.push({ scene: s, cam: camera([1.6, 2.0, 1.95], [0, 0.12, 0], 37), objs });
  }

  // frame every drawing the same way: the models fill 84 % of the drawing square, centred
  scenes.forEach((sc) => {
    sc.cam.clearViewOffset();
    const P0 = projector(sc.cam, SIZE);
    let x0 = Infinity, y0 = Infinity, x1 = -Infinity, y1 = -Infinity;
    sc.objs.forEach((o) => {
      o.mesh.updateWorldMatrix(true, false);
      const pos = o.mesh.geometry.getAttribute('position');
      for (let i = 0; i < pos.count; i++) {
        const q = P0(new THREE.Vector3().fromBufferAttribute(pos, i).applyMatrix4(o.mesh.matrixWorld));
        x0 = Math.min(x0, q.x); x1 = Math.max(x1, q.x); y0 = Math.min(y0, q.y); y1 = Math.max(y1, q.y);
      }
    });
    const win = Math.max(x1 - x0, y1 - y0) / 0.84;
    sc.cam.setViewOffset(SIZE, SIZE, (x0 + x1) / 2 - win / 2, (y0 + y1) / 2 - win / 2, win, win);
    sc.cam.updateMatrixWorld();
  });
  // the pen strokes from the 3D models
  const art = scenes.map((sc) => lineArt(sc.objs, sc.cam, SIZE));
  // the corner-to-corner line of drawing 5, on the drawing
  const P5 = projector(scenes[4].cam, SIZE);
  const c0 = P5(new THREE.Vector3(S0[0], TOTAL, -S0[1])), c1 = P5(new THREE.Vector3(S1[0], TOTAL, -S1[1]));
  const cut: [Pt, Pt] = [[c0.x, c0.y], [c1.x, c1.y]];

  // colour fills and the hand: three.js renders, made once, kept as pictures
  const canvas = document.createElement('canvas');
  const r = new THREE.WebGLRenderer({ canvas, alpha: true, antialias: true, preserveDrawingBuffer: true });
  r.setPixelRatio(1);
  r.setClearColor(0x000000, 0);
  HT_U.strength.value = 0;
  r.setSize(SIZE * 2, SIZE * 2, false);
  const color = scenes.map((sc) => { r.clear(); r.render(sc.scene, sc.cam); return canvas.toDataURL('image/png'); });
  const hand = buildHand(r, canvas);
  r.dispose();
  r.forceContextLoss();
  return { art, color, cut, hand };
};

// a cartoon hand holding a whiteboard marker, drawn in the same toon-and-ink look; the marker tip is at the origin
const buildHand = (r: THREE.WebGLRenderer, canvas: HTMLCanvasElement) => {
  const s = new THREE.Scene();
  s.add(new THREE.HemisphereLight('#FFFFFF', '#D6C8B2', 1.2));
  const d = new THREE.DirectionalLight('#FFFFFF', 2.3); d.position.set(-2, 3, 5);
  s.add(d, d.target);
  const skin = toonMat('#F2C29A'), white = toonMat('#F2F2EF'), blue = toonMat('#2F6FD6'), black = toonMat('#1B1B1B');
  const SLEEVE = '#41618F';
  const sleeveMat = new THREE.MeshBasicMaterial({ color: SLEEVE });
  const dir = new THREE.Vector3(1, 0.42, 0.24).normalize();
  const side = new THREE.Vector3(dir.y, -dir.x, 0).normalize(); // below the marker, in the picture plane
  const Z = new THREE.Vector3(0, 0, 1);
  const P = (along: number, sd: number, z: number) => dir.clone().multiplyScalar(along).addScaledVector(side, sd).addScaledVector(Z, z);
  const Y = new THREE.Vector3(0, 1, 0);
  const cyl = (s0: number, s1: number, r0: number, r1: number, mat: THREE.Material) => {
    const m = new THREE.Mesh(new THREE.CylinderGeometry(r1, r0, s1 - s0, 36), mat);
    m.position.copy(dir.clone().multiplyScalar((s0 + s1) / 2));
    m.quaternion.setFromUnitVectors(Y, dir);
    s.add(ink(m));
  };
  // the marker
  cyl(0, 0.09, 0.028, 0.042, black);
  cyl(0.09, 0.33, 0.05, 0.115, white);
  cyl(0.33, 0.43, 0.12, 0.12, blue);
  cyl(0.43, 1.6, 0.12, 0.12, white);
  cyl(1.6, 1.98, 0.13, 0.13, blue);
  // the hand: back of the hand, fingers wrapped round the marker, the thumb in front, the wrist
  const palm = new THREE.Mesh(new THREE.SphereGeometry(1, 32, 24), skin);
  palm.position.copy(P(1.2, -0.03, -0.04));
  palm.quaternion.setFromUnitVectors(Y, dir);
  palm.scale.set(0.3, 0.38, 0.24);
  s.add(ink(palm));
  const finger = (a: THREE.Vector3, b: THREE.Vector3, rad: number) => s.add(ink(capsule(a, b, rad, skin)));
  finger(P(1.0, -0.24, 0.02), P(0.64, -0.19, 0.03), 0.072); // index, resting on top of the marker
  finger(P(1.04, 0.13, 0.2), P(0.72, 0.07, 0.17), 0.078); // thumb, in front
  finger(P(1.1, 0.24, 0.0), P(0.8, 0.2, -0.02), 0.07); // middle, under the marker
  finger(P(1.2, 0.3, -0.04), P(1.0, 0.28, -0.06), 0.066); // ring, curled
  finger(P(1.29, 0.32, -0.06), P(1.13, 0.31, -0.08), 0.06); // little finger, curled
  const arm = side.clone().multiplyScalar(0.85).addScaledVector(dir, 0.45).addScaledVector(Z, 0.05).normalize();
  const w0 = P(1.32, 0.08, -0.05);
  finger(P(1.2, 0.0, -0.04), w0.clone().addScaledVector(arm, 0.3), 0.17); // wrist
  const sa = w0.clone().addScaledVector(arm, 0.28), sb = w0.clone().addScaledVector(arm, 3.2);
  const sleeve = new THREE.Mesh(new THREE.CylinderGeometry(0.24, 0.24, sa.distanceTo(sb), 36), sleeveMat);
  sleeve.position.copy(sa).lerp(sb, 0.5);
  sleeve.quaternion.setFromUnitVectors(Y, arm);
  s.add(ink(sleeve));
  // frame: from a little left of the tip to past the hand; the sleeve runs out of the picture (an SVG band continues it)
  const k = 360; // px per unit
  const L = -0.22, R = 2.25, T = 1.15, B = -1.15;
  const cam = new THREE.OrthographicCamera(L, R, T, B, -20, 20);
  cam.position.set(0, 0, 10); cam.lookAt(0, 0, 0); cam.updateMatrixWorld();
  const w = Math.round((R - L) * k), h = Math.round((T - B) * k);
  r.setSize(w, h, false);
  INK_U.resolution.value.set(w, h);
  INK_U.thickness.value = 4.5;
  HT_U.strength.value = 0;
  r.clear();
  r.render(s, cam);
  const url = canvas.toDataURL('image/png');
  const px = (v: THREE.Vector3): Pt => [(v.x - L) * k, (T - v.y) * k];
  return { url, w, h, tip: px(new THREE.Vector3(0, 0, 0)), sleeve: { a: px(sa), b: px(sb), r: 0.24 * k, ink: 4.5 } };
};

// ---------- the pen (as in the approved whiteboard) ----------
type Seg = { pts: Pt[]; len: number; draw: boolean; width: number; cum: number[] };
const prep = (s: LineArt) => {
  const k = SIZE / s.w;
  const segs: Seg[] = [];
  let last: Pt | null = null;
  s.strokes.forEach((arr, i) => {
    const pts: Pt[] = [];
    for (let j = 0; j < arr.length; j += 2) pts.push([arr[j] * k, arr[j + 1] * k]);
    if (last) {
      const d = Math.hypot(pts[0][0] - last[0], pts[0][1] - last[1]);
      segs.push({ pts: [last, pts[0]], len: d * 0.35, draw: false, width: 0, cum: [0, d * 0.35] });
    }
    const cum = [0];
    for (let j = 1; j < pts.length; j++) cum.push(cum[j - 1] + Math.hypot(pts[j][0] - pts[j - 1][0], pts[j][1] - pts[j - 1][1]));
    segs.push({ pts, len: cum[cum.length - 1], draw: true, width: Math.max(2.2, (s.widths?.[i] ?? s.strokeWidth) * k), cum });
    last = pts[pts.length - 1];
  });
  const total = segs.reduce((a, x) => a + x.len, 0);
  return { segs, total };
};
type Prep = ReturnType<typeof prep>;
const pointAt = (seg: Seg, l: number): Pt => {
  if (seg.pts.length < 2) return seg.pts[0];
  if (!seg.draw) { const t = seg.len > 0 ? l / seg.len : 1; return [mix(t, seg.pts[0][0], seg.pts[1][0]), mix(t, seg.pts[0][1], seg.pts[1][1])]; }
  let j = 1;
  while (j < seg.cum.length - 1 && seg.cum[j] < l) j++;
  const a = seg.cum[j - 1], b = seg.cum[j];
  const t = b > a ? (l - a) / (b - a) : 0;
  return [mix(t, seg.pts[j - 1][0], seg.pts[j][0]), mix(t, seg.pts[j - 1][1], seg.pts[j][1])];
};

const Drawing: React.FC<{ i: number; f: number; pr: Prep; color: string }> = ({ i, f, pr, color }) => {
  const d = DRAW[i], { segs, total } = pr;
  const p = prog(f, d.draw[0], d.draw[1], (t) => t);
  const col = prog(f, d.color[0], d.color[1], easeInOut);
  if (p <= 0) return null;
  let left = p * total;
  return (
    <>
      {/* the marker colour (a three.js render of the same models) sweeps in under the lines when the drawing is done */}
      {col > 0 ? (
        <Img src={color} style={{ position: 'absolute', left: 0, top: 0, width: SIZE, height: SIZE, mixBlendMode: 'multiply', opacity: 0.92,
          WebkitMaskImage: `linear-gradient(110deg, #000 ${col * 130 - 30}%, transparent ${col * 130}%)`, maskImage: `linear-gradient(110deg, #000 ${col * 130 - 30}%, transparent ${col * 130}%)` }} />
      ) : null}
      <svg width={SIZE} height={SIZE} style={{ position: 'absolute', left: 0, top: 0, overflow: 'visible' }}>
        {segs.map((s, k) => {
          if (!s.draw) { left -= s.len; return null; }
          const vis = Math.max(0, Math.min(s.len, left));
          left -= s.len;
          if (vis <= 0) return null;
          return (
            <polyline key={k} points={s.pts.map((q) => q.join(',')).join(' ')} fill="none" stroke={INKC} strokeWidth={s.width}
              strokeLinecap="round" strokeLinejoin="round" strokeDasharray={`${s.len + 1} ${s.len + 1}`} strokeDashoffset={s.len - vis} />
          );
        })}
      </svg>
    </>
  );
};

const penAt = (f: number, PREP: Prep[]): { p: Pt; down: boolean } | null => {
  for (let i = 0; i < DRAW.length; i++) {
    const d = DRAW[i], c = CELLS[i];
    const o: Pt = [c[0] - SIZE / 2, c[1] - SIZE / 2 - 40];
    if (f >= d.draw[0] && f <= d.draw[1]) {
      const { segs, total } = PREP[i];
      let l = prog(f, d.draw[0], d.draw[1], (t) => t) * total;
      for (const s of segs) {
        if (l <= s.len) { const q = pointAt(s, l); return { p: [o[0] + q[0], o[1] + q[1]], down: s.draw }; }
        l -= s.len;
      }
    }
    if (f >= d.write[0] && f <= d.write[1]) {
      const t = prog(f, d.write[0], d.write[1], (x) => x);
      const w = d.label.length * 34;
      return { p: [c[0] - w / 2 + t * w, c[1] + 312 + Math.sin(t * 40) * 8], down: true };
    }
  }
  return null;
};

const CAM: [number, number, number, number][] = [
  [0, CELLS[0][0], CELLS[0][1] + 70, 1.32], [62, CELLS[0][0] + 20, CELLS[0][1] + 70, 1.28], [72, CELLS[1][0], CELLS[1][1] + 70, 1.3],
  [124, CELLS[1][0] + 20, CELLS[1][1] + 70, 1.27], [134, CELLS[2][0], CELLS[2][1] + 70, 1.3], [198, CELLS[2][0], CELLS[2][1] + 80, 1.26],
  [212, CELLS[3][0], CELLS[3][1] + 70, 1.3], [264, CELLS[3][0] - 20, CELLS[3][1] + 70, 1.27], [274, CELLS[4][0], CELLS[4][1] + 70, 1.3],
  [324, CELLS[4][0] - 20, CELLS[4][1] + 70, 1.27], [334, CELLS[5][0], CELLS[5][1] + 70, 1.3], [380, CELLS[5][0] + 20, CELLS[5][1] + 70, 1.26],
  [408, 1200, 760, 0.66], [450, 1200, 760, 0.64],
];
const camAt = (f: number) => {
  let i = 0;
  while (i < CAM.length - 2 && f >= CAM[i + 1][0]) i++;
  const a = CAM[i], b = CAM[i + 1];
  const move = b[0] - a[0] <= 30;
  const t = interpolate(f, [a[0], b[0]], [0, 1], { extrapolateLeft: 'clamp', extrapolateRight: 'clamp', easing: move ? Easing.bezier(0.6, 0, 0.3, 1) : (x) => x });
  return { x: mix(t, a[1], b[1]), y: mix(t, a[2], b[2]), z: mix(t, a[3], b[3]) };
};

const head = (d: string) => {
  const n = d.replace(/[MC]/g, ' ').trim().split(/\s+/).map(Number);
  const [x2, y2, x3, y3] = n.slice(4);
  const a = Math.atan2(y3 - y2, x3 - x2), L = 34;
  const p = (da: number) => `${x3 - L * Math.cos(a + da)} ${y3 - L * Math.sin(a + da)}`;
  return `M ${p(0.55)} L ${x3} ${y3} L ${p(-0.55)}`;
};
const ARROWS = [
  'M 700 360 C 760 330 860 330 900 360', 'M 1500 360 C 1560 330 1660 330 1700 360', 'M 2330 560 C 2380 650 2380 760 2330 840',
  'M 1700 1090 C 1640 1060 1540 1060 1500 1090', 'M 900 1090 C 840 1060 740 1060 700 1090',
];

let CACHE: Built | null = null;

export const Whiteboard3D: React.FC = () => {
  const f = useCurrentFrame();
  const B = useMemo(() => (CACHE ??= build()), []);
  const PREP = useMemo(() => B.art.map(prep), [B]);
  const HAND = { ...B.hand, s: 0.62 };
  const cam = camAt(f);
  const pen = penAt(f, PREP);
  const restP: Pt = [cam.x + 1100 / cam.z, cam.y + 700 / cam.z];
  let handP: Pt = pen ? pen.p : restP;
  if (!pen) {
    let prev: Pt | null = null, next: Pt | null = null, tp = 0, tn = 0;
    for (let k = 1; k <= 14; k++) { const q = penAt(f - k, PREP); if (q) { prev = q.p; tp = k; break; } }
    for (let k = 1; k <= 14; k++) { const q = penAt(f + k, PREP); if (q) { next = q.p; tn = k; break; } }
    if (prev && next) handP = [mix(tp / (tp + tn), prev[0], next[0]), mix(tp / (tp + tn), prev[1], next[1])];
    else if (prev) handP = [mix(easeInOut(clamp(tp / 12)), prev[0], restP[0]), mix(easeInOut(clamp(tp / 12)), prev[1], restP[1])];
    else if (next) handP = [mix(easeInOut(clamp(tn / 12)), next[0], restP[0]), mix(easeInOut(clamp(tn / 12)), next[1], restP[1])];
  }
  const lift = pen && !pen.down ? 6 : 0;
  const arrows = prog(f, 386, 412, easeInOut);
  const ring = prog(f, 414, 430, Easing.out(Easing.quad));
  const [ca, cb] = B.cut;
  const cd: Pt = [cb[0] - ca[0], cb[1] - ca[1]];
  const cutA: Pt = [ca[0] - cd[0] * 0.08, ca[1] - cd[1] * 0.08], cutB: Pt = [cb[0] + cd[0] * 0.06, cb[1] + cd[1] * 0.06];
  // the sleeve beyond the hand picture: a flat band with ink edges, continuing the 3D sleeve
  const sl = B.hand.sleeve;
  const ad: Pt = [sl.b[0] - sl.a[0], sl.b[1] - sl.a[1]], al = Math.hypot(ad[0], ad[1]);
  const au: Pt = [ad[0] / al, ad[1] / al], pn: Pt = [-au[1], au[0]];
  // the band starts where the sleeve leaves the hand picture (so the two shadows do not stack)
  const exitT = Math.min(...[au[0] > 1e-6 ? (HAND.w - sl.a[0]) / au[0] : Infinity, au[0] < -1e-6 ? -sl.a[0] / au[0] : Infinity,
    au[1] > 1e-6 ? (HAND.h - sl.a[1]) / au[1] : Infinity, au[1] < -1e-6 ? -sl.a[1] / au[1] : Infinity]);
  const st: Pt = [sl.a[0] + au[0] * Math.max(0, exitT - sl.r), sl.a[1] + au[1] * Math.max(0, exitT - sl.r)];
  const far: Pt = [sl.a[0] + au[0] * 9000, sl.a[1] + au[1] * 9000];
  const band = (rr: number) => [[st[0] + pn[0] * rr, st[1] + pn[1] * rr], [far[0] + pn[0] * rr, far[1] + pn[1] * rr], [far[0] - pn[0] * rr, far[1] - pn[1] * rr],
    [st[0] - pn[0] * rr, st[1] - pn[1] * rr]].map((q) => q.join(',')).join(' ');
  const handLeft = handP[0] - HAND.tip[0] * HAND.s + lift, handTop = handP[1] - HAND.tip[1] * HAND.s - lift;

  return (
    <AbsoluteFill style={{ background: '#E9ECEE', overflow: 'hidden' }}>
      <AbsoluteFill style={{ transform: `translate(${960 - cam.x * cam.z}px, ${540 - cam.y * cam.z}px) scale(${cam.z})`, transformOrigin: '0 0' }}>
        <div style={{ position: 'absolute', left: -600, top: -500, width: 3600, height: 2600, background: 'radial-gradient(ellipse at 50% 40%, #FFFFFF 0%, #FAFBFA 55%, #F0F2F1 100%)' }} />
        <svg width={2400} height={1500} style={{ position: 'absolute', left: 0, top: 0, opacity: 0.05 }}>
          <path d="M 150 900 C 400 860 600 980 820 920 M 1500 120 C 1700 90 1900 160 2100 110 M 900 1380 C 1100 1340 1300 1420 1500 1370" stroke="#555" strokeWidth={26} fill="none" strokeLinecap="round" />
        </svg>
        {DRAW.map((d, i) => (
          <div key={d.name} style={{ position: 'absolute', left: CELLS[i][0] - SIZE / 2, top: CELLS[i][1] - SIZE / 2 - 40, width: SIZE, height: SIZE }}>
            <Drawing i={i} f={f} pr={PREP[i]} color={B.color[i]} />
          </div>
        ))}
        {DRAW.map((d, i) => {
          const t = prog(f, d.write[0], d.write[1], (x) => x);
          if (t <= 0) return null;
          return (
            <div key={d.name + 'l'} style={{ position: 'absolute', left: CELLS[i][0], top: CELLS[i][1] + 312, transform: 'translate(-50%, -50%) rotate(-2deg)',
              fontFamily: MARKER, fontSize: 64, color: i === 5 ? RED : BLUE, whiteSpace: 'nowrap', clipPath: `inset(-20% ${100 - t * 100}% -20% -5%)` }}>{d.label}</div>
          );
        })}
        {/* the corner-to-corner line on the cut drawing, through the sandwich's real corners */}
        {f >= 284 ? (
          <svg width={SIZE} height={SIZE} style={{ position: 'absolute', left: CELLS[4][0] - SIZE / 2, top: CELLS[4][1] - SIZE / 2 - 40, overflow: 'visible' }}>
            <line x1={cutA[0]} y1={cutA[1]} x2={mix(prog(f, 284, 296, easeInOut), cutA[0], cutB[0])} y2={mix(prog(f, 284, 296, easeInOut), cutA[1], cutB[1])}
              stroke={RED} strokeWidth={9} strokeDasharray="22 16" strokeLinecap="round" />
          </svg>
        ) : null}
        {arrows > 0 ? (
          <svg width={2400} height={1500} style={{ position: 'absolute', left: 0, top: 0, overflow: 'visible' }}>
            {ARROWS.map((d, i) => {
              const t = clamp(arrows * 5 - i);
              return (
                <g key={i}>
                  <path d={d} stroke={BLUE} strokeWidth={12} fill="none" strokeLinecap="round" pathLength={1} strokeDasharray="1 1" strokeDashoffset={1 - t} />
                  {t >= 1 ? <path d={head(d)} stroke={BLUE} strokeWidth={12} fill="none" strokeLinecap="round" strokeLinejoin="round" /> : null}
                </g>
              );
            })}
            {ring > 0 ? (
              <ellipse cx={CELLS[5][0]} cy={CELLS[5][1] + 20} rx={370} ry={360} stroke={RED} strokeWidth={14} fill="none" pathLength={1} strokeDasharray="1 1"
                strokeDashoffset={1 - ring} transform={`rotate(-8 ${CELLS[5][0]} ${CELLS[5][1] + 20})`} strokeLinecap="round" />
            ) : null}
          </svg>
        ) : null}
        {/* the sleeve carries on past the picture's edge, off screen */}
        <svg width={HAND.w * HAND.s} height={HAND.h * HAND.s} viewBox={`0 0 ${HAND.w} ${HAND.h}`} style={{ position: 'absolute', overflow: 'visible',
          left: handLeft, top: handTop, filter: 'drop-shadow(18px 22px 16px rgba(0,0,0,.22))' }}>
          <polygon points={band(sl.r + sl.ink)} fill="#121212" />
          <polygon points={band(sl.r)} fill="#41618F" />
        </svg>
        <Img src={HAND.url} style={{ position: 'absolute', width: HAND.w * HAND.s, height: HAND.h * HAND.s, left: handLeft, top: handTop,
          filter: 'drop-shadow(18px 22px 16px rgba(0,0,0,.22))' }} />
      </AbsoluteFill>
      <Soundtrack sfx={SFX} />
    </AbsoluteFill>
  );
};

const drawingSfx: Sfx[] = [];
DRAW.forEach((d) => {
  for (let t = d.draw[0]; t < d.draw[1] - 4; t += 13) drawingSfx.push({ at: t, file: 'stroke.wav', vol: 0.32, dur: 16 });
  drawingSfx.push({ at: d.write[0], file: 'stroke.wav', vol: 0.3, dur: 16 });
});
const SFX: Sfx[] = [
  ...drawingSfx,
  ...[64, 126, 200, 266, 326].map((t) => ({ at: t, file: 'page.wav', vol: 0.3 })),
  { at: 384, file: 'whoosh.wav', vol: 0.3 }, { at: 392, file: 'stroke.wav', vol: 0.3 }, { at: 414, file: 'circle.wav', vol: 0.4 },
];
