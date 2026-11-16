// Shared 3D shapes for the 3D styles (isometric, 3D animation, stop motion): the bread-slice outline, and the two halves
// of any outline cut corner to corner (so the cut pieces are real closed solids, not hollow shells).
import * as THREE from 'three';

export type V2 = [number, number];

/** The classic slice outline (width w, height h, centred on 0,0; the dome points to +y). */
export const sliceShape = (w: number, h: number) => {
  const X = (u: number) => -w / 2 + u * w, Y = (v: number) => h / 2 - v * h; // v measured from the top
  const s = new THREE.Shape();
  s.moveTo(X(0.08), Y(1));
  s.lineTo(X(0.92), Y(1));
  s.quadraticCurveTo(X(1), Y(1), X(1), Y(0.92));
  s.lineTo(X(1), Y(0.32));
  s.bezierCurveTo(X(1.08), Y(0.2), X(1.05), Y(0.01), X(0.8), Y(0.02));
  s.bezierCurveTo(X(0.66), Y(-0.04), X(0.34), Y(-0.04), X(0.2), Y(0.02));
  s.bezierCurveTo(X(-0.05), Y(0.01), X(-0.08), Y(0.2), X(0), Y(0.32));
  s.lineTo(X(0), Y(0.92));
  s.quadraticCurveTo(X(0), Y(1), X(0.08), Y(1));
  return s;
};

/** Outline as a polygon (points in order). */
export const shapePolygon = (shape: THREE.Shape, n = 80): V2[] => shape.getSpacedPoints(n).slice(0, -1).map((p) => [p.x, p.y]);

/** Keep the part of a polygon on one side of the line a->b (Sutherland-Hodgman with one edge). side=+1 left, -1 right. */
export const clipHalf = (poly: V2[], a: V2, b: V2, side: 1 | -1): V2[] => {
  const d = (p: V2) => side * ((b[0] - a[0]) * (p[1] - a[1]) - (b[1] - a[1]) * (p[0] - a[0]));
  const out: V2[] = [];
  for (let i = 0; i < poly.length; i++) {
    const p = poly[i], q = poly[(i + 1) % poly.length];
    const dp = d(p), dq = d(q);
    if (dp >= 0) out.push(p);
    if ((dp >= 0) !== (dq >= 0)) {
      const t = dp / (dp - dq);
      out.push([p[0] + (q[0] - p[0]) * t, p[1] + (q[1] - p[1]) * t]);
    }
  }
  return out;
};

export const polyShape = (poly: V2[]) => {
  const s = new THREE.Shape();
  poly.forEach(([x, y], i) => (i === 0 ? s.moveTo(x, y) : s.lineTo(x, y)));
  s.closePath();
  return s;
};

/** Where the cut line crosses the outline: the two end points of the cut face. */
export const cutSegment = (poly: V2[], a: V2, b: V2): [V2, V2] => {
  const hits: { t: number; p: V2 }[] = [];
  const dir: V2 = [b[0] - a[0], b[1] - a[1]];
  for (let i = 0; i < poly.length; i++) {
    const p = poly[i], q = poly[(i + 1) % poly.length];
    const e: V2 = [q[0] - p[0], q[1] - p[1]];
    const den = dir[0] * e[1] - dir[1] * e[0];
    if (Math.abs(den) < 1e-9) continue;
    const t = ((p[0] - a[0]) * e[1] - (p[1] - a[1]) * e[0]) / den;
    const u = ((p[0] - a[0]) * dir[1] - (p[1] - a[1]) * dir[0]) / den;
    if (u >= 0 && u <= 1) hits.push({ t, p: [a[0] + dir[0] * t, a[1] + dir[1] * t] });
  }
  hits.sort((x, y) => x.t - y.t);
  return [hits[0].p, hits[hits.length - 1].p];
};

/** Extrude an outline into a flat solid lying on the table: thickness along +y, the outline's +y pointing to world -z. */
export const flatSolid = (shape: THREE.Shape, depth: number, bevel = 0.02, curveSegments = 24) => {
  const g = new THREE.ExtrudeGeometry(shape, {
    depth, bevelEnabled: bevel > 0, bevelThickness: bevel, bevelSize: bevel, bevelSegments: 3, curveSegments,
  });
  g.rotateX(-Math.PI / 2); // extrusion now points up (+y); outline +y now points to -z
  g.computeVertexNormals();
  return g;
};
