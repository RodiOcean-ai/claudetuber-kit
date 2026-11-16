// Turn three.js models into pen strokes for the whiteboard (test without the picture maker, 14 Nov 2026).
// The drawing is worked out from the 3D shapes themselves: the outline of every object as the camera sees it, its sharp
// edges, and extra detail lines (crumbs, swirls) that lie on its surfaces. Hidden lines are removed with a depth picture
// of the scene, so a line behind something stops where a real artist's line would stop. The result is a list of pen
// strokes in drawing order, in the same format as the traced whiteboard drawings.
import * as THREE from 'three';

export type LineObj = {
  mesh: THREE.Mesh; // world position already set
  order: number; // objects are drawn in this order
  width?: number; // outline pen width (drawing px)
  crease?: number; // edges sharper than this (degrees) are drawn
  details?: THREE.Vector3[][]; // extra lines in the mesh's own space (on its surfaces)
  detailWidth?: number;
};
export type LineArt = { w: number; h: number; strokeWidth: number; strokes: number[][]; widths: number[] };
type P2 = [number, number];
type Run = { pts: P2[]; order: number; width: number; kind: 0 | 1 };

export const projector = (cam: THREE.PerspectiveCamera, size: number) => {
  cam.updateMatrixWorld();
  cam.updateProjectionMatrix();
  const vp = new THREE.Matrix4().multiplyMatrices(cam.projectionMatrix, cam.matrixWorldInverse);
  const t = new THREE.Vector4();
  return (v: THREE.Vector3) => {
    t.set(v.x, v.y, v.z, 1).applyMatrix4(vp);
    const iw = 1 / t.w;
    return { x: ((t.x * iw + 1) / 2) * size, y: ((1 - t.y * iw) / 2) * size, iw };
  };
};

const simplify = (pts: P2[], eps: number): P2[] => {
  if (pts.length < 3) return pts;
  const keep = new Uint8Array(pts.length);
  keep[0] = keep[pts.length - 1] = 1;
  const stack: [number, number][] = [[0, pts.length - 1]];
  while (stack.length) {
    const [a, b] = stack.pop()!;
    const [ax, ay] = pts[a], [bx, by] = pts[b];
    const dx = bx - ax, dy = by - ay, L = Math.hypot(dx, dy);
    let best = -1, bi = -1;
    for (let i = a + 1; i < b; i++) {
      // a closed loop (start = end) has no line to measure from: use the distance from the start point instead
      const d = L < 1e-6 ? Math.hypot(pts[i][0] - ax, pts[i][1] - ay) : Math.abs((pts[i][0] - ax) * dy - (pts[i][1] - ay) * dx) / L;
      if (d > best) { best = d; bi = i; }
    }
    if (best > eps) { keep[bi] = 1; stack.push([a, bi], [bi, b]); }
  }
  return pts.filter((_, i) => keep[i]);
};

const lengthOf = (pts: P2[]) => { let s = 0; for (let i = 1; i < pts.length; i++) s += Math.hypot(pts[i][0] - pts[i - 1][0], pts[i][1] - pts[i - 1][1]); return s; };

/** a small hand wobble along the stroke (none at the two ends, so joins stay joined) */
const wobble = (pts: P2[], seed: number, amp: number): P2[] => {
  const L = lengthOf(pts);
  if (L < 6) return pts;
  const out: P2[] = [];
  const step = 3;
  let acc = 0, j = 1;
  const at = (s: number): P2 => {
    while (j < pts.length - 1 && acc + Math.hypot(pts[j][0] - pts[j - 1][0], pts[j][1] - pts[j - 1][1]) < s) {
      acc += Math.hypot(pts[j][0] - pts[j - 1][0], pts[j][1] - pts[j - 1][1]); j++;
    }
    const seg = Math.hypot(pts[j][0] - pts[j - 1][0], pts[j][1] - pts[j - 1][1]) || 1e-9;
    const u = Math.min(1, Math.max(0, (s - acc) / seg));
    return [pts[j - 1][0] + (pts[j][0] - pts[j - 1][0]) * u, pts[j - 1][1] + (pts[j][1] - pts[j - 1][1]) * u];
  };
  const n = Math.max(2, Math.ceil(L / step));
  const ph1 = seed * 1.7, ph2 = seed * 3.1;
  const raw: P2[] = [];
  for (let i = 0; i <= n; i++) raw.push(at((i / n) * L));
  for (let i = 0; i <= n; i++) {
    const s = (i / n) * L;
    const p = raw[i], q = raw[Math.min(n, i + 1)], r = raw[Math.max(0, i - 1)];
    const tx = q[0] - r[0], ty = q[1] - r[1], tl = Math.hypot(tx, ty) || 1e-9;
    const taper = Math.min(1, s / 10, (L - s) / 10);
    const o = amp * taper * (Math.sin(s / 29 + ph1) * 0.65 + Math.sin(s / 9.5 + ph2) * 0.35);
    out.push([p[0] - (ty / tl) * o, p[1] + (tx / tl) * o]);
  }
  return out;
};

export const lineArt = (objs: LineObj[], cam: THREE.PerspectiveCamera, size: number, opts: { crease?: number; eps?: number } = {}): LineArt => {
  const P = projector(cam, size);
  const Z = 2, R = size * Z;
  const zb = new Float32Array(R * R);
  const camPos = new THREE.Vector3().setFromMatrixPosition(cam.matrixWorld);
  const EPS = opts.eps ?? 0.008;

  // world triangles per object
  const world = objs.map((o) => {
    o.mesh.updateWorldMatrix(true, false);
    const g = o.mesh.geometry, pos = g.getAttribute('position'), idx = g.getIndex();
    const n = idx ? idx.count : pos.count;
    const v: THREE.Vector3[] = [];
    for (let i = 0; i < n; i++) v.push(new THREE.Vector3().fromBufferAttribute(pos, idx ? idx.getX(i) : i).applyMatrix4(o.mesh.matrixWorld));
    return v;
  });

  // 1) the depth picture (nearest surface per pixel, stored as 1/distance)
  for (const v of world) {
    for (let t = 0; t + 2 < v.length; t += 3) {
      const a = P(v[t]), b = P(v[t + 1]), c = P(v[t + 2]);
      if (a.iw <= 0 || b.iw <= 0 || c.iw <= 0) continue;
      const ax = a.x * Z, ay = a.y * Z, bx = b.x * Z, by = b.y * Z, cx = c.x * Z, cy = c.y * Z;
      const area = (bx - ax) * (cy - ay) - (by - ay) * (cx - ax);
      if (Math.abs(area) < 1e-7) continue;
      const x0 = Math.max(0, Math.floor(Math.min(ax, bx, cx))), x1 = Math.min(R - 1, Math.ceil(Math.max(ax, bx, cx)));
      const y0 = Math.max(0, Math.floor(Math.min(ay, by, cy))), y1 = Math.min(R - 1, Math.ceil(Math.max(ay, by, cy)));
      for (let y = y0; y <= y1; y++) {
        const py = y + 0.5;
        for (let x = x0; x <= x1; x++) {
          const px = x + 0.5;
          const w0 = ((bx - px) * (cy - py) - (by - py) * (cx - px)) / area;
          const w1 = ((cx - px) * (ay - py) - (cy - py) * (ax - px)) / area;
          const w2 = 1 - w0 - w1;
          if (w0 < -1e-4 || w1 < -1e-4 || w2 < -1e-4) continue;
          const iw = w0 * a.iw + w1 * b.iw + w2 * c.iw;
          const k = y * R + x;
          if (iw > zb[k]) zb[k] = iw;
        }
      }
    }
  }
  const visible = (s: { x: number; y: number; iw: number }) => {
    const x = Math.floor(s.x * Z), y = Math.floor(s.y * Z);
    if (x < 1 || y < 1 || x >= R - 1 || y >= R - 1) return false;
    let best = 0;
    for (let dy = -1; dy <= 1; dy++) for (let dx = -1; dx <= 1; dx++) best = Math.max(best, zb[(y + dy) * R + x + dx]);
    return best === 0 || s.iw >= best * (1 - EPS);
  };

  // 2) candidate edges: outlines (one face towards the camera, the other away), sharp edges, open borders
  const runs: Run[] = [];
  const sampleLine = (pts3: THREE.Vector3[], order: number, width: number, kind: 0 | 1) => {
    let run: P2[] = [];
    const flush = () => { if (run.length > 1) runs.push({ pts: run, order, width, kind }); run = []; };
    for (let i = 0; i + 1 < pts3.length; i++) {
      const a = pts3[i], b = pts3[i + 1];
      const sa = P(a), sb = P(b);
      const n = Math.max(1, Math.ceil(Math.hypot(sb.x - sa.x, sb.y - sa.y) / 1.25));
      for (let s = i === 0 ? 0 : 1; s <= n; s++) {
        const q = P(new THREE.Vector3().lerpVectors(a, b, s / n));
        if (visible(q)) run.push([q.x, q.y]); else flush();
      }
    }
    flush();
  };
  objs.forEach((o, oi) => {
    const v = world[oi];
    const cosCrease = Math.cos(((o.crease ?? opts.crease ?? 35) * Math.PI) / 180);
    const ids = new Map<string, number>();
    const pts: THREE.Vector3[] = [];
    const id = (p: THREE.Vector3) => {
      const k = `${Math.round(p.x * 2e4)},${Math.round(p.y * 2e4)},${Math.round(p.z * 2e4)}`;
      let i = ids.get(k);
      if (i === undefined) { i = pts.length; ids.set(k, i); pts.push(p); }
      return i;
    };
    const edges = new Map<number, THREE.Vector3[]>();
    const ab = new THREE.Vector3(), ac = new THREE.Vector3();
    for (let t = 0; t + 2 < v.length; t += 3) {
      const nrm = new THREE.Vector3().crossVectors(ab.subVectors(v[t + 1], v[t]), ac.subVectors(v[t + 2], v[t]));
      if (nrm.lengthSq() < 1e-14) continue;
      nrm.normalize();
      const i0 = id(v[t]), i1 = id(v[t + 1]), i2 = id(v[t + 2]);
      for (const [p, q] of [[i0, i1], [i1, i2], [i2, i0]]) {
        if (p === q) continue;
        const key = Math.min(p, q) * 2097152 + Math.max(p, q);
        const e = edges.get(key);
        if (e) e.push(nrm); else edges.set(key, [nrm]);
      }
    }
    const view = new THREE.Vector3();
    edges.forEach((ns, key) => {
      const a = pts[Math.floor(key / 2097152)], b = pts[key % 2097152];
      view.addVectors(a, b).multiplyScalar(0.5).sub(camPos).negate();
      const facing = ns.map((n) => n.dot(view));
      let draw = false;
      if (ns.length === 1) draw = true; // an open border
      else if (ns.length === 2) {
        if (facing[0] * facing[1] < 0) draw = true; // the outline as seen from here
        else if ((facing[0] > 0 || facing[1] > 0) && ns[0].dot(ns[1]) < cosCrease) draw = true; // a sharp edge
      } else draw = facing.some((f) => f > 0);
      if (draw) sampleLine([a, b], o.order, o.width ?? 4.4, 0);
    });
    (o.details ?? []).forEach((line) => sampleLine(line.map((p) => p.clone().applyMatrix4(o.mesh.matrixWorld)), o.order, o.detailWidth ?? 3, 1));
  });

  // 3) join the little pieces into long pen strokes (ends that meet, without sharp turns)
  const TOL = 1.3;
  const groups = new Map<string, Run[]>();
  runs.forEach((r) => { const k = `${r.order}:${r.kind}`; (groups.get(k) ?? groups.set(k, []).get(k)!).push(r); });
  const strokes: Run[] = [];
  groups.forEach((list) => {
    const used = new Uint8Array(list.length);
    const cell = 4;
    const grid = new Map<string, number[]>();
    const gk = (p: P2) => `${Math.floor(p[0] / cell)},${Math.floor(p[1] / cell)}`;
    list.forEach((r, i) => [r.pts[0], r.pts[r.pts.length - 1]].forEach((p) => { const k = gk(p); (grid.get(k) ?? grid.set(k, []).get(k)!).push(i); }));
    const dirAt = (pts: P2[]): P2 => {
      const e = pts[pts.length - 1];
      let k = pts.length - 2;
      while (k > 0 && Math.hypot(e[0] - pts[k][0], e[1] - pts[k][1]) < 4) k--;
      const d: P2 = [e[0] - pts[k][0], e[1] - pts[k][1]]; const l = Math.hypot(d[0], d[1]) || 1;
      return [d[0] / l, d[1] / l];
    };
    const extend = (pts: P2[]) => {
      for (;;) {
        const e = pts[pts.length - 1], d = dirAt(pts);
        let best = -1, bestRev = false, bestCos = Math.cos((68 * Math.PI) / 180);
        const cx = Math.floor(e[0] / cell), cy = Math.floor(e[1] / cell);
        for (let dy = -1; dy <= 1; dy++) for (let dx = -1; dx <= 1; dx++) {
          for (const j of grid.get(`${cx + dx},${cy + dy}`) ?? []) {
            if (used[j]) continue;
            const r = list[j].pts;
            for (const rev of [false, true]) {
              const s = rev ? r[r.length - 1] : r[0];
              if (Math.hypot(s[0] - e[0], s[1] - e[1]) > TOL) continue;
              const nx = rev ? r[Math.max(0, r.length - 4)] : r[Math.min(r.length - 1, 3)];
              const v: P2 = [nx[0] - s[0], nx[1] - s[1]]; const l = Math.hypot(v[0], v[1]) || 1;
              const c = (v[0] * d[0] + v[1] * d[1]) / l;
              if (c > bestCos) { bestCos = c; best = j; bestRev = rev; }
            }
          }
        }
        if (best < 0) return pts;
        used[best] = 1;
        const add = bestRev ? [...list[best].pts].reverse() : list[best].pts;
        pts = pts.concat(add.slice(1));
      }
    };
    const orderIdx = list.map((r, i) => [lengthOf(r.pts), i] as [number, number]).sort((x, y) => y[0] - x[0]).map(([, i]) => i);
    for (const i of orderIdx) {
      if (used[i]) continue;
      used[i] = 1;
      let pts = extend([...list[i].pts]);
      pts = extend(pts.reverse()).reverse();
      strokes.push({ ...list[i], pts });
    }
  });

  // 4) tidy, add the hand wobble, and put the strokes in drawing order (object by object, outline before details,
  //    each time the nearest next stroke so the pen does not jump around)
  const clean = strokes
    .map((s, i) => ({ ...s, pts: wobble(simplify(s.pts, 0.45), i + 1, s.kind ? 0.6 : 0.9) }))
    .filter((s) => lengthOf(s.pts) > (s.kind ? 2.5 : 5));
  const out: Run[] = [];
  let pen: P2 = [0, 0];
  const keys = [...new Set(clean.map((s) => s.order * 2 + s.kind))].sort((a, b) => a - b);
  for (const key of keys) {
    const left = clean.filter((s) => s.order * 2 + s.kind === key);
    if (!out.length && left.length) {
      left.sort((a, b) => lengthOf(b.pts) - lengthOf(a.pts));
      pen = left[0].pts[0];
    }
    while (left.length) {
      let bi = 0, brev = false, bd = Infinity;
      left.forEach((s, i) => {
        const d0 = Math.hypot(s.pts[0][0] - pen[0], s.pts[0][1] - pen[1]);
        const d1 = Math.hypot(s.pts[s.pts.length - 1][0] - pen[0], s.pts[s.pts.length - 1][1] - pen[1]);
        if (d0 < bd) { bd = d0; bi = i; brev = false; }
        if (d1 < bd) { bd = d1; bi = i; brev = true; }
      });
      const s = left.splice(bi, 1)[0];
      const pts = brev ? [...s.pts].reverse() : s.pts;
      out.push({ ...s, pts });
      pen = pts[pts.length - 1];
    }
  }
  return {
    w: size, h: size, strokeWidth: 4,
    strokes: out.map((s) => s.pts.flatMap(([x, y]) => [Math.round(x * 10) / 10, Math.round(y * 10) / 10])),
    widths: out.map((s) => s.width),
  };
};
