// The sandwich as 3D shapes for the three.js tests (comic and whiteboard without the picture maker, 14 Nov 2026):
// the same sizes as the approved 3D style, but with sharp edges (no bevel) so ink lines land on the real corners.
import * as THREE from 'three';
import { V2, clipHalf, cutSegment, flatSolid, polyShape, shapePolygon, sliceShape } from './shapes';

export const SWG = { W: 1.3, TH: 0.17, PBH: 0.065 };

export const sandwichGeo = (bevel = 0, pbBevel = 0) => {
  const { W, TH, PBH } = SWG;
  const slice = sliceShape(W, W);
  const pbShape = sliceShape(W * 0.94, W * 0.93);
  const sp = shapePolygon(slice, 110), pp = shapePolygon(pbShape, 110);
  // corner to corner: from the outline's top-left corner to its bottom-right corner
  const ca: V2 = [-W / 2 - 0.1, W / 2 + 0.1], cb: V2 = [W / 2 + 0.1, -W / 2 - 0.1];
  const halves = ([1, -1] as const).map((side) => {
    const poly = clipHalf(sp, ca, cb, side);
    const c = poly.reduce<V2>((a, p) => [a[0] + p[0] / poly.length, a[1] + p[1] / poly.length], [0, 0]);
    return {
      slice: flatSolid(polyShape(poly), TH, bevel, 2),
      pb: flatSolid(polyShape(clipHalf(pp, ca, cb, side)), PBH, pbBevel, 2),
      centroid: c,
    };
  });
  // the butter knife: tip at the origin, blade up (+y), 1.0 long
  const knife = (() => {
    const s = new THREE.Shape();
    s.moveTo(0, 0); s.quadraticCurveTo(0.08, 0.03, 0.085, 0.22); s.lineTo(0.085, 1.0); s.lineTo(-0.075, 1.0); s.lineTo(-0.075, 0.3); s.quadraticCurveTo(-0.07, 0.06, 0, 0);
    const g = new THREE.ExtrudeGeometry(s, { depth: 0.016, bevelEnabled: false, curveSegments: 10 });
    g.translate(0, 0, -0.008);
    return g;
  })();
  // the chef's knife: edge along +x from 0 to 1.7, spine at y 0.36
  const chef = (() => {
    const s = new THREE.Shape();
    s.moveTo(0, 0); s.lineTo(1.7, 0); s.quadraticCurveTo(1.68, 0.28, 1.4, 0.36); s.lineTo(0, 0.36); s.lineTo(0, 0);
    const g = new THREE.ExtrudeGeometry(s, { depth: 0.014, bevelEnabled: false, curveSegments: 10 });
    g.translate(0, 0, -0.007);
    return g;
  })();
  return {
    slice: flatSolid(slice, TH, bevel, 24),
    pb: flatSolid(pbShape, PBH, pbBevel, 24),
    halves, seg: cutSegment(sp, ca, cb), knife, chef, outline: sp,
  };
};
export type SandwichGeo = ReturnType<typeof sandwichGeo>;

/** The cut face (bread / peanut butter / bread) as a small texture, top row = top of the sandwich. */
export const cutFaceTex = (crumb: string, pb: string, crust: string) => {
  const c = document.createElement('canvas'); c.width = 64; c.height = 256;
  const g = c.getContext('2d')!;
  const { TH, PBH } = SWG;
  const total = 2 * TH + PBH;
  g.fillStyle = crumb; g.fillRect(0, 0, 64, 256);
  g.fillStyle = pb; g.fillRect(0, 256 * (TH / total), 64, 256 * (PBH / total));
  g.fillStyle = crust; g.fillRect(0, 0, 64, 10); g.fillRect(0, 246, 64, 10);
  const t = new THREE.CanvasTexture(c);
  t.colorSpace = THREE.SRGBColorSpace;
  return t;
};
