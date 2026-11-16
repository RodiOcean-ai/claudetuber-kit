// Style 4: ISOMETRIC. A small diorama (a kitchen counter block with a cutting board, a mug and a plant) seen from a locked
// true-isometric orthographic camera, built with @remotion/three (no Blender). Flat colours, soft key light from the
// upper left so the top / left / right faces read as three tones, soft shadows for lift. The camera only zooms and pans
// (the angle never changes); small callout labels with leader lines point at each step.
import React, { useLayoutEffect, useMemo } from 'react';
import * as THREE from 'three';
import { ThreeCanvas } from '@remotion/three';
import { useThree } from '@react-three/fiber';
import { AbsoluteFill, Easing, interpolate, useCurrentFrame } from 'remotion';
import { Soundtrack, Sfx } from '../../shared/Soundtrack';
import { ensureFonts } from '../../shared/fonts';
import { K, STEPS, at } from '../../shared/timing';
import { clamp, easeInOut, easeOut, mix, pop, prog } from '../../shared/anim';
import { V2, clipHalf, cutSegment, flatSolid, polyShape, shapePolygon, sliceShape } from '../../shared/three/shapes';

ensureFonts('Inter');
const INK = '#0B2540';
const C = {
  counterTop: '#FBF4EA', counterSide: '#F1E4D2', board: '#E3AF72', crumb: '#F8E2AE', crust: '#D58F3A', pb: '#A55E27',
  glass: '#CDEBF8', label: '#0A84C6', lid: '#E5484D', blade: '#E6ECF2', handle: '#12324F', mug: '#0A84C6', pot: '#E07A4F', leaf: '#3FA66B',
};

// ---------- layout (world units; y is up; the table top of the board is y = 0.16) ----------
const T = 0.16;
const A: [number, number, number] = [-0.95, T, 0.45];
const B: [number, number, number] = [0.95, T, 0.45];
const JAR: [number, number, number] = [1.45, T, -0.85];
const W = 1.4, Hs = 1.4, TH = 0.18, BEV = 0.02, PBH = 0.045;

// ---------- camera: [frame, zoom (px per unit), target x, y, z]; the angle is locked ----------
const CAM: [number, number, number, number, number][] = [
  [0, 112, 0, -0.2, 0], [60, 126, 0, 0, 0.1], [74, 150, 0.4, 0.3, -0.3], [126, 150, 0.4, 0.3, -0.3],
  [140, 215, A[0], 0.35, A[2]], [200, 215, A[0], 0.35, A[2]], [214, 175, -0.1, 0.6, 0.45], [266, 175, -0.4, 0.5, 0.45],
  [278, 225, A[0], 0.45, A[2]], [322, 225, A[0], 0.45, A[2]], [336, 185, A[0], 0.45, A[2] - 0.1], [450, 165, A[0] + 0.2, 0.4, A[2] - 0.1],
];
type Cam = { zoom: number; x: number; y: number; z: number };
const camAt = (f: number): Cam => {
  let i = 0;
  while (i < CAM.length - 2 && f >= CAM[i + 1][0]) i++;
  const a = CAM[i], b = CAM[i + 1];
  const t = interpolate(f, [a[0], b[0]], [0, 1], { extrapolateLeft: 'clamp', extrapolateRight: 'clamp', easing: b[0] - a[0] <= 16 ? Easing.bezier(0.65, 0, 0.35, 1) : (x) => x });
  return { zoom: mix(t, a[1], b[1]), x: mix(t, a[2], b[2]), y: mix(t, a[3], b[3]), z: mix(t, a[4], b[4]) };
};
// world point -> screen pixel for the true-iso camera (camera at target + (10,10,10))
const proj = (p: [number, number, number], c: Cam): [number, number] => {
  const dx = p[0] - c.x, dy = p[1] - c.y, dz = p[2] - c.z;
  return [960 + ((dx - dz) / Math.SQRT2) * c.zoom, 540 - ((-dx + 2 * dy - dz) / Math.sqrt(6)) * c.zoom];
};

const Rig: React.FC<{ c: Cam }> = ({ c }) => {
  const { camera } = useThree();
  useLayoutEffect(() => {
    camera.position.set(c.x + 10, c.y + 10, c.z + 10);
    camera.up.set(0, 1, 0);
    camera.lookAt(c.x, c.y, c.z);
    (camera as THREE.OrthographicCamera).zoom = c.zoom;
    camera.updateProjectionMatrix();
  }, [camera, c.x, c.y, c.z, c.zoom]);
  return null;
};

// ---------- geometry built once ----------
const useKit = () => useMemo(() => {
  const slice = sliceShape(W, Hs);
  const pbShape = sliceShape(W * 0.84, Hs * 0.82);
  const slicePoly = shapePolygon(slice, 96), pbPoly = shapePolygon(pbShape, 96);
  // the cut runs from the outline's bottom-left corner to its top-right corner (left to right on screen)
  const ca: V2 = [-W / 2 - 0.1, -Hs / 2 - 0.1], cb: V2 = [W / 2 + 0.1, Hs / 2 + 0.1];
  const half = (poly: V2[], side: 1 | -1) => polyShape(clipHalf(poly, ca, cb, side));
  const seg = cutSegment(slicePoly, ca, cb);
  // the cut face: a vertical card along the cut showing bread / peanut butter / bread
  const cv = document.createElement('canvas'); cv.width = 64; cv.height = 256;
  const g = cv.getContext('2d')!;
  const band = (y0: number, y1: number, col: string) => { g.fillStyle = col; g.fillRect(0, 256 * (1 - y1), 64, 256 * (y1 - y0)); };
  const total = TH + 2 * BEV + PBH + TH + 2 * BEV;
  const a1 = (TH + 2 * BEV) / total, p1 = (TH + 2 * BEV + PBH) / total;
  band(0, a1, C.crumb); band(a1, p1, C.pb); band(p1, 1, C.crumb);
  band(0, 0.03, C.crust); band(0.97, 1, C.crust);
  const tex = new THREE.CanvasTexture(cv); tex.colorSpace = THREE.SRGBColorSpace;
  return {
    slice: flatSolid(slice, TH, BEV), pb: flatSolid(pbShape, PBH, 0.012),
    halves: ([1, -1] as const).map((side) => ({
      slice: flatSolid(half(slicePoly, side), TH, BEV, 2), pb: flatSolid(half(pbPoly, side), PBH, 0.012, 2),
    })),
    seg, total, faceTex: tex,
    knifeBlade: (() => {
      const s = new THREE.Shape();
      s.moveTo(0, 0); s.quadraticCurveTo(0.09, 0.02, 0.09, 0.2); s.lineTo(0.09, 0.95); s.lineTo(-0.07, 0.95); s.lineTo(-0.07, 0.25); s.quadraticCurveTo(-0.06, 0.05, 0, 0);
      return new THREE.ExtrudeGeometry(s, { depth: 0.022, bevelEnabled: false });
    })(),
  };
}, []);

const mat = (color: string, extra: Partial<THREE.MeshLambertMaterialParameters> = {}) => <meshLambertMaterial color={color} {...extra} />;
// two materials on one extruded solid: [0] the flat faces (crumb), [1] the sides (crust)
const bread = () => [<meshLambertMaterial key="0" attach="material-0" color={C.crumb} />, <meshLambertMaterial key="1" attach="material-1" color={C.crust} />];

const Knife: React.FC<{ kit: ReturnType<typeof useKit>; blob: number }> = ({ kit, blob }) => (
  <group>
    <mesh geometry={kit.knifeBlade} position={[0, 0, -0.011]} castShadow>{mat(C.blade)}</mesh>
    <mesh position={[0.01, 1.22, 0]} castShadow><boxGeometry args={[0.15, 0.55, 0.09]} />{mat(C.handle)}</mesh>
    {blob > 0 ? <mesh position={[0.01, 0.16, 0]} scale={[blob, blob * 1.2, blob]} castShadow><sphereGeometry args={[0.1, 20, 16]} />{mat(C.pb)}</mesh> : null}
  </group>
);

const Label: React.FC<{ text: string; anchor: [number, number, number]; c: Cam; show: number; dx?: number; dy?: number; ok?: number }> = ({ text, anchor, c, show, dx = 120, dy = -120, ok = 0 }) => {
  if (show <= 0.001) return null;
  const [x, y] = proj(anchor, c);
  const lx = x + dx, ly = y + dy;
  return (
    <>
      <svg width={1920} height={1080} style={{ position: 'absolute', inset: 0, overflow: 'visible', opacity: show }}>
        <line x1={x} y1={y} x2={mix(show, x, lx)} y2={mix(show, y, ly)} stroke={INK} strokeWidth={3} />
        <circle cx={x} cy={y} r={7} fill="#fff" stroke={INK} strokeWidth={3} />
      </svg>
      <div style={{ position: 'absolute', left: lx, top: ly, transform: `translate(${dx > 0 ? '0' : '-100%'}, -50%) scale(${0.6 + 0.4 * show})`,
        transformOrigin: dx > 0 ? '0 50%' : '100% 50%', opacity: show, background: '#fff', color: INK, fontFamily: 'Inter', fontWeight: 700, fontSize: 34,
        padding: '12px 22px', borderRadius: 14, boxShadow: '0 10px 26px rgba(11,37,64,.18)', whiteSpace: 'nowrap', display: 'flex', alignItems: 'center', gap: 12 }}>
        {text}
        {ok > 0 ? <span style={{ display: 'inline-grid', placeItems: 'center', width: 36, height: 36, borderRadius: 18, background: '#16A34A', color: '#fff',
          fontSize: 24, transform: `scale(${ok})` }}>✓</span> : null}
      </div>
    </>
  );
};

const Scene: React.FC<{ f: number; c: Cam }> = ({ f, c }) => {
  const kit = useKit();
  // step 1: slices drop in
  // owner, note 1: "The bread disappear": the spring went past the landing and sank the slice into the board.
  // Height never goes below the board now; the overshoot becomes a little squash instead.
  const dropAraw = pop(f, at(K.two) - 4, { damping: 10, stiffness: 150 }), dropBraw = pop(f, at(K.slices) - 4, { damping: 10, stiffness: 150 });
  const dropA = Math.min(1, dropAraw), dropB = Math.min(1, dropBraw);
  const landA = 1 - 0.6 * Math.max(0, dropAraw - 1), landB = 1 - 0.6 * Math.max(0, dropBraw - 1);
  // step 2: jar pops up, the lid twists off and lands on the board, the knife dips and scoops
  const jarIn = pop(f, at(K.dig) - 6, { damping: 11, stiffness: 170 });
  const lidT = prog(f, at(K.dig) + 2, at(K.knife) + 6, easeInOut);
  const knifeIn = prog(f, at(K.knife) - 6, at(K.into) + 2, Easing.out(Easing.cubic));
  const dip = prog(f, at(K.into), at(K.peanut) + 2, easeInOut);
  const lift = prog(f, at(K.butter) - 2, at(K.butter) + 12, easeInOut);
  const level = 1 - 0.12 * dip;
  // step 3: the knife spreads; the peanut butter grows from the middle to the edges
  const goSpread = prog(f, STEPS.spread.from - 6, at(K.spread), easeInOut);
  const spreadT = prog(f, at(K.spread), at(K.edges) + 4, (t) => t);
  const pb = prog(f, at(K.spread), at(K.edges) + 4, Easing.inOut(Easing.quad));
  const kAway = prog(f, at(K.edges) + 6, at(K.edges) + 20, Easing.in(Easing.cubic));
  const jarAway = prog(f, STEPS.spread.from + 10, STEPS.spread.from + 26, Easing.in(Easing.back(1.5)));
  // step 4: slice B lifts, turns over and lands on A with a squash
  const up = prog(f, at(K.press) - 2, at(K.second) + 4, easeInOut);
  const over = prog(f, at(K.second) - 2, at(K.on) + 2, easeInOut);
  const down = prog(f, at(K.on) - 2, at(K.top) - 1, Easing.in(Easing.quad));
  const squash = f >= at(K.top) - 1 ? Math.sin(clamp((f - at(K.top) + 1) / 9) * Math.PI) * Math.exp(-(f - at(K.top) + 1) / 12) : 0;
  // step 5: the cut
  const cutKnife = prog(f, at(K.cut) - 4, at(K.corner2) + 6, easeInOut);
  const split = prog(f, at(K.corner2) + 6, at(K.corner2) + 20, Easing.out(Easing.back(1.4)));
  const apart = 0.62 * split + 0.18 * prog(f, STEPS.payoff.from, 420, easeInOut);
  const cut = f >= at(K.corner2) + 6;

  // knife path
  let kp: [number, number, number] = [JAR[0], mix(knifeIn, 3.5, 1.45) - dip * 0.5 + lift * 0.9, JAR[2]];
  let kr: [number, number, number] = [0, 0, 0];
  const blob = f < STEPS.spread.from ? lift : 1 - pb;
  if (f >= STEPS.spread.from - 6) {
    const zig = Math.sin(spreadT * Math.PI * 6);
    const sx = A[0] + zig * 0.32, sz = A[2] + mix(spreadT, -0.35, 0.35);
    kp = [mix(goSpread, JAR[0], sx - 0.05) + kAway * 2.5, mix(goSpread, 2.3, T + TH + 0.12) + kAway * 1.5, mix(goSpread, JAR[2], sz) - kAway * 1.5];
    kr = [mix(goSpread, 0, -1.25), mix(goSpread, 0, 0.6), mix(goSpread, 0, -0.35 + zig * 0.18)];
  }
  const knifeShow = f >= at(K.knife) - 6 && kAway < 1;

  // slice B transform
  const bPos: [number, number, number] = [mix(over, B[0], A[0]), T + BEV + mix(up, 0, 1.2) * (1 - down) + down * (TH + 2 * BEV + PBH) + (1 - dropB) * 3, mix(over, B[2], A[2])];
  const bRot = over * Math.PI; // turn over (about z)
  const stackS = 1 - 0.1 * squash;

  return (
    <>
      <Rig c={c} />
      <ambientLight intensity={1.0} />
      <hemisphereLight args={['#ffffff', '#b9cfe0', 0.7]} />
      <directionalLight position={[-5, 10, 7]} intensity={2.4} castShadow shadow-mapSize-width={2048} shadow-mapSize-height={2048}
        shadow-camera-left={-6} shadow-camera-right={6} shadow-camera-top={6} shadow-camera-bottom={-6} shadow-bias={-0.0004} />
      {/* the counter block and the board */}
      <mesh position={[0, -0.45, 0]} receiveShadow><boxGeometry args={[6.2, 0.9, 4.4]} />{mat(C.counterSide)}</mesh>
      <mesh position={[0, -0.005, 0]} receiveShadow><boxGeometry args={[6.2, 0.01, 4.4]} />{mat(C.counterTop)}</mesh>
      <mesh position={[-0.1, 0.08, 0.15]} receiveShadow castShadow><boxGeometry args={[4.4, 0.16, 2.9]} />{mat(C.board)}</mesh>
      {[-0.9, 0, 0.9].map((z) => <mesh key={z} position={[-0.1, T + 0.001, 0.15 + z]} rotation={[-Math.PI / 2, 0, 0]}><planeGeometry args={[4.2, 0.02]} />{mat('#CF9A5D')}</mesh>)}
      {/* props: a mug and a little plant */}
      <group position={[-2.45, 0, -1.55]}>
        <mesh position={[0, 0.36, 0]} castShadow><cylinderGeometry args={[0.3, 0.27, 0.72, 32]} />{mat(C.mug)}</mesh>
        <mesh position={[0, 0.715, 0]}><cylinderGeometry args={[0.25, 0.25, 0.02, 32]} />{mat('#5B3A1E')}</mesh>
        <mesh position={[0.33, 0.38, 0]} rotation={[0, 0, Math.PI / 2]} castShadow><torusGeometry args={[0.15, 0.045, 12, 24]} />{mat(C.mug)}</mesh>
      </group>
      <group position={[2.55, 0, 1.6]}>
        <mesh position={[0, 0.22, 0]} castShadow><cylinderGeometry args={[0.28, 0.22, 0.44, 24]} />{mat(C.pot)}</mesh>
        {[[0, 0.62, 0, 0.3], [0.18, 0.52, 0.1, 0.22], [-0.16, 0.55, -0.08, 0.22]].map(([x, y, z, r], i) => (
          <mesh key={i} position={[x, y, z]} castShadow><icosahedronGeometry args={[r, 1]} />{mat(C.leaf, { flatShading: true })}</mesh>
        ))}
      </group>
      {/* the jar */}
      {jarIn > 0.01 && jarAway < 1 ? (
        <group position={[JAR[0] + jarAway * 2.2, 0, JAR[2] - jarAway * 1.2]} scale={jarIn * (1 - jarAway * 0.3)}>
          <mesh position={[0, T + 0.41 * level, 0]} scale={[1, level, 1]} castShadow><cylinderGeometry args={[0.38, 0.38, 0.82, 40]} />{mat(C.pb)}</mesh>
          <mesh position={[0, T + 0.5, 0]}><cylinderGeometry args={[0.42, 0.42, 1.0, 40, 1, true]} />{mat(C.glass, { transparent: true, opacity: 0.45, side: THREE.DoubleSide })}</mesh>
          <mesh position={[0, T + 0.5, 0]}><cylinderGeometry args={[0.425, 0.425, 0.34, 40, 1, true]} />{mat(C.label)}</mesh>
          <mesh position={[0, T + 1.0, 0]} rotation={[Math.PI / 2, 0, 0]}><torusGeometry args={[0.4, 0.035, 10, 48]} />{mat('#E9F4FA')}</mesh>
          <group position={[mix(lidT, 0, 1.1), T + 1.12 + Math.sin(lidT * Math.PI) * 0.9 - lidT * 1.0, mix(lidT, 0, 0.9)]} rotation={[lidT * 0.4, lidT * Math.PI * 2.5, lidT * Math.PI * 0.9]}>
            <mesh castShadow><cylinderGeometry args={[0.4, 0.4, 0.16, 40]} />{mat(C.lid)}</mesh>
          </group>
        </group>
      ) : null}
      {/* slice A (+ peanut butter) and slice B, until the cut */}
      {!cut ? (
        <group scale={[1 + 0.05 * squash, stackS, 1 + 0.05 * squash]} position={[A[0], 0, A[2]]}>
          <group position={[0, T + BEV + (1 - dropA) * 3, 0]} rotation={[0, (1 - dropA) * 0.6, 0]} scale={[1, landA, 1]}>
            <mesh geometry={kit.slice} castShadow receiveShadow>{bread()}</mesh>
          </group>
          {pb > 0 ? (
            <mesh geometry={kit.pb} position={[0, T + TH + 2 * BEV, 0.03]} scale={[0.15 + 0.85 * pb, 1, 0.15 + 0.85 * pb]} castShadow receiveShadow>{mat(C.pb)}</mesh>
          ) : null}
        </group>
      ) : null}
      {!cut && dropB > 0.01 ? (
        <group position={[bPos[0], bPos[1] + TH / 2, bPos[2]]} rotation={[0, (1 - dropB) * -0.5, bRot]} scale={[1 + 0.05 * squash * down, (1 - 0.1 * squash * down) * landB, 1 + 0.05 * squash * down]}>
          <mesh geometry={kit.slice} position={[0, -TH / 2, 0]} castShadow receiveShadow>{bread()}</mesh>
        </group>
      ) : null}
      {/* after the cut: two half stacks, each bread / peanut butter / bread, moving apart */}
      {cut ? ([0, 1] as const).map((i) => {
        const h = kit.halves[i];
        const dir = i === 0 ? -1 : 1; // half 0 is the far one (moves up-screen), half 1 the near one
        const d = apart * dir / Math.SQRT2;
        const [s0, s1] = kit.seg;
        // cut face card: along the cut segment (outline coords -> world: x, z = -y)
        const mx = (s0[0] + s1[0]) / 2, mz = -(s0[1] + s1[1]) / 2;
        const len = Math.hypot(s1[0] - s0[0], s1[1] - s0[1]);
        const ang = Math.atan2(-(s1[1] - s0[1]), s1[0] - s0[0]);
        return (
          <group key={i} position={[A[0] + d, 0, A[2] + d]} rotation={[0, dir * 0.12 * split, 0]}>
            <mesh geometry={h.slice} position={[0, T + BEV, 0]} castShadow receiveShadow>{bread()}</mesh>
            <mesh geometry={h.pb} position={[0, T + TH + 2 * BEV, 0.03]} castShadow>{mat(C.pb)}</mesh>
            <mesh geometry={h.slice} position={[0, T + TH + 3 * BEV + PBH, 0]} castShadow receiveShadow>{bread()}</mesh>
            {/* pushed a hair outward so it covers the extruded side wall along the cut */}
            <mesh position={[mx + (i === 0 ? 0.009 : -0.009), T + kit.total / 2, mz + (i === 0 ? 0.009 : -0.009)]} rotation={[0, -ang + (i === 1 ? Math.PI : 0), 0]}>
              <planeGeometry args={[len * 0.96, kit.total]} />
              <meshLambertMaterial map={kit.faceTex} side={THREE.DoubleSide} />
            </mesh>
          </group>
        );
      }) : null}
      {/* the knife (steps 2-3) */}
      {knifeShow ? <group position={kp} rotation={kr}><Knife kit={kit} blob={blob} /></group> : null}
      {/* the cutting knife: blade upright, slicing left to right along the cut */}
      {cutKnife > 0 && split < 0.5 ? (
        <group position={[A[0] + mix(cutKnife, -1.0, 1.0), T + 0.62 - Math.sin(cutKnife * Math.PI) * 0.3, A[2] - mix(cutKnife, -1.0, 1.0)]} rotation={[0, Math.PI / 4, Math.PI / 2]}>
          <group scale={1.3}><Knife kit={kit} blob={0} /></group>
        </group>
      ) : null}
    </>
  );
};

export const Isometric: React.FC = () => {
  const f = useCurrentFrame();
  const c = camAt(f);
  const lab = (from: number, to: number) => prog(f, from, from + 8, easeOut) * (1 - prog(f, to - 6, to));
  const pb = prog(f, at(K.spread), at(K.edges) + 4);
  return (
    <AbsoluteFill style={{ background: 'linear-gradient(160deg, #F2FAFE 0%, #DDF0FA 55%, #C7E5F5 100%)' }}>
      <ThreeCanvas orthographic flat width={1920} height={1080} shadows gl={{ antialias: true, alpha: true }} camera={{ position: [10, 10, 10], zoom: 112, near: 0.1, far: 100 }}
        style={{ position: 'absolute', inset: 0 }}>
        <Scene f={f} c={c} />
      </ThreeCanvas>
      <Label text="2 slices of bread" anchor={[0, T + 0.25, A[2] - 0.75]} c={c} show={lab(at(K.two), STEPS.knife.from + 4)} dx={140} dy={-150} />
      <Label text="Peanut butter" anchor={[JAR[0], T + 1.2, JAR[2]]} c={c} show={lab(at(K.peanut) - 2, STEPS.spread.from + 2)} dx={130} dy={-90} />
      <Label text="Right to the edges" anchor={[A[0] + 0.35, T + 0.3, A[2] - 0.4]} c={c} show={lab(at(K.right) - 2, STEPS.press.from + 2)} dx={150} dy={-150} ok={pop(f, at(K.edges) + 2) * (pb >= 1 ? 1 : 0)} />
      <Label text="Second slice on top" anchor={[A[0] + 0.3, T + 0.6, A[2] - 0.3]} c={c} show={lab(at(K.second) - 2, STEPS.cut.from + 2)} dx={160} dy={-160} />
      <Label text="Corner to corner" anchor={[A[0] + 0.75, T + 0.55, A[2] - 0.75]} c={c} show={lab(at(K.corner1) - 2, STEPS.payoff.from + 2)} dx={150} dy={-130} />
      <Label text="Triangles taste better" anchor={[A[0] + 0.3, T + 0.65, A[2] - 0.6]} c={c} show={lab(at(K.triangles) - 2, 999)} dx={170} dy={-170} />
      <Soundtrack sfx={SFX} />
    </AbsoluteFill>
  );
};

const SFX: Sfx[] = [
  { at: at(K.two) + 2, file: 'card.wav', vol: 0.35 }, { at: at(K.slices) + 2, file: 'card2.wav', vol: 0.35 },
  { at: at(K.two), file: 'pop2.wav', vol: 0.2 },
  { at: 64, file: 'swipe1.wav', vol: 0.2 },
  { at: at(K.dig) - 6, file: 'pop.wav', vol: 0.3 },
  { at: at(K.dig) + 4, file: 'zip2.wav', vol: 0.25 },
  { at: at(K.knife) - 4, file: 'swish2.wav', vol: 0.3 },
  { at: at(K.into) + 2, file: 'smack.wav', vol: 0.25 },
  { at: at(K.peanut) - 2, file: 'pop2.wav', vol: 0.2 },
  { at: 130, file: 'swipe2.wav', vol: 0.2 },
  { at: at(K.spread), file: 'paper.wav', vol: 0.25, dur: 40 },
  { at: at(K.edges) + 2, file: 'ding.wav', vol: 0.15 },
  { at: at(K.press) - 2, file: 'whoosh.wav', vol: 0.3 },
  { at: at(K.top) - 1, file: 'thud.wav', vol: 0.4 },
  { at: 270, file: 'swipe3.wav', vol: 0.2 },
  { at: at(K.cut) - 2, file: 'zip1.wav', vol: 0.35 },
  { at: at(K.corner2) + 6, file: 'whip.wav', vol: 0.35 },
  { at: at(K.triangles) - 2, file: 'pop2.wav', vol: 0.25 },
  { at: at(K.better), file: 'sparkle.wav', vol: 0.2 },
];
