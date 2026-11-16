// Style 11: STOP MOTION (the faked look). A felt-and-cardboard miniature set on a gingham tablecloth, built with
// @remotion/three: felt bread with stitched edges, a brown felt peanut-butter piece that grows in replacement steps,
// a kraft-paper jar with a felt lid, a card-and-stick craft knife. Everything moves at 12 poses a second (each held for
// 2-3 frames), every pose has its own tiny hand-placed wobble, the light flickers a hair and the background is soft
// like a real tabletop set shot with a close lens.
import React, { useLayoutEffect, useMemo } from 'react';
import * as THREE from 'three';
import { ThreeCanvas } from '@remotion/three';
import { useThree } from '@react-three/fiber';
import { AbsoluteFill, useCurrentFrame } from 'remotion';
import { Soundtrack, Sfx } from '../../shared/Soundtrack';
import { K, STEPS, at } from '../../shared/timing';
import { clamp, mix, rand } from '../../shared/anim';
import { V2, clipHalf, flatSolid, polyShape, shapePolygon, sliceShape } from '../../shared/three/shapes';

type V3 = [number, number, number];
const T = 0.06; // top of the cardboard board
const A: V3 = [-0.8, T, 0.2], B: V3 = [0.8, T, 0.2], JAR: V3 = [1.7, 0, -1.55]; // behind the board (it ends at z -1.05)
const W = 1.25, TH = 0.16, BEV = 0.03, PBH = 0.05;
const POSE = 2.5; // 30 fps / 12 poses a second

// ---------- handmade textures ----------
const tex = (w: number, h: number, draw: (g: CanvasRenderingContext2D) => void, rep: [number, number] = [1, 1], offset: [number, number] = [0, 0]) => {
  const c = document.createElement('canvas'); c.width = w; c.height = h; draw(c.getContext('2d')!);
  const t = new THREE.CanvasTexture(c); t.colorSpace = THREE.SRGBColorSpace; t.wrapS = t.wrapT = THREE.RepeatWrapping;
  t.repeat.set(rep[0], rep[1]); t.offset.set(offset[0], offset[1]); t.anisotropy = 8; return t;
};
const fibres = (g: CanvasRenderingContext2D, w: number, h: number, base: string, light: string, dark: string, n = 2600) => {
  g.fillStyle = base; g.fillRect(0, 0, w, h);
  for (let i = 0; i < n; i++) {
    const x = rand(i * 1.3) * w, y = rand(i * 2.1 + 5) * h, a = rand(i * 3.7) * Math.PI, l = 3 + rand(i * 4.3) * 9;
    g.strokeStyle = rand(i * 5.1) > 0.5 ? light : dark; g.lineWidth = 0.6 + rand(i * 6.7) * 1.1;
    g.beginPath(); g.moveTo(x, y); g.lineTo(x + Math.cos(a) * l, y + Math.sin(a) * l); g.stroke();
  }
};
// the slice outline drawn on a canvas (same curve as sliceShape), for the stitches
const sliceOnCanvas = (g: CanvasRenderingContext2D, S: number, inset: number) => {
  const k = 1 - 2 * inset, o = S * inset;
  const X = (u: number) => o + u * S * k, Y = (v: number) => o + v * S * k;
  g.beginPath(); g.moveTo(X(0.08), Y(1)); g.lineTo(X(0.92), Y(1)); g.quadraticCurveTo(X(1), Y(1), X(1), Y(0.92)); g.lineTo(X(1), Y(0.32));
  g.bezierCurveTo(X(1.08), Y(0.2), X(1.05), Y(0.01), X(0.8), Y(0.02)); g.bezierCurveTo(X(0.66), Y(-0.04), X(0.34), Y(-0.04), X(0.2), Y(0.02));
  g.bezierCurveTo(X(-0.05), Y(0.01), X(-0.08), Y(0.2), X(0), Y(0.32)); g.lineTo(X(0), Y(0.92)); g.quadraticCurveTo(X(0), Y(1), X(0.08), Y(1)); g.closePath();
};
const breadTop = () => tex(512, 512, (g) => {
  fibres(g, 512, 512, '#F3E2BC', 'rgba(255,250,235,0.55)', 'rgba(190,160,110,0.35)');
  g.setLineDash([14, 11]); g.lineWidth = 5; g.strokeStyle = 'rgba(150,95,40,0.9)'; sliceOnCanvas(g, 512, 0.085); g.stroke();
}, [1 / W, 1 / W], [0.5, 0.5]);
const crustFelt = () => tex(256, 256, (g) => fibres(g, 256, 256, '#C88A45', 'rgba(230,180,110,0.5)', 'rgba(120,70,25,0.45)', 1500), [3, 3]);
const pbFelt = () => tex(512, 512, (g) => {
  fibres(g, 512, 512, '#8E4E1F', 'rgba(190,120,60,0.5)', 'rgba(70,35,10,0.5)');
  g.setLineDash([12, 10]); g.lineWidth = 4; g.strokeStyle = 'rgba(240,200,150,0.75)'; sliceOnCanvas(g, 512, 0.06); g.stroke();
}, [1 / (W * 0.99), 1 / (W * 0.99)], [0.5, 0.5]);
const gingham = () => tex(512, 512, (g) => {
  g.fillStyle = '#F7F1E6'; g.fillRect(0, 0, 512, 512);
  for (let i = 0; i < 8; i++) { g.fillStyle = 'rgba(214,64,64,0.55)'; g.fillRect(i * 64, 0, 32, 512); g.fillRect(0, i * 64, 512, 32); }
  for (let i = 0; i < 3000; i++) { g.fillStyle = `rgba(0,0,0,${rand(i) * 0.05})`; g.fillRect(rand(i + 1) * 512, rand(i + 2) * 512, 2, 2); }
}, [2.4, 1.2]);
const cardboard = () => tex(512, 512, (g) => {
  g.fillStyle = '#C79B62'; g.fillRect(0, 0, 512, 512);
  for (let i = 0; i < 40; i++) { g.fillStyle = `rgba(120,80,40,${0.06 + rand(i) * 0.06})`; g.fillRect(0, i * 13 + rand(i) * 4, 512, 3); }
  for (let i = 0; i < 1500; i++) { g.fillStyle = `rgba(80,50,20,${rand(i + 3) * 0.12})`; g.fillRect(rand(i + 4) * 512, rand(i + 5) * 512, 1 + rand(i) * 3, 1); }
}, [2, 1.3]);
const kraftJar = () => tex(1024, 256, (g) => {
  g.fillStyle = '#B98A55'; g.fillRect(0, 0, 1024, 256);
  for (let i = 0; i < 2000; i++) { g.fillStyle = `rgba(90,60,30,${rand(i) * 0.12})`; g.fillRect(rand(i + 1) * 1024, rand(i + 2) * 256, 2, 2); }
  g.fillStyle = '#FFF8EA'; g.fillRect(310, 70, 400, 120);
  g.strokeStyle = '#3A2A1A'; g.lineWidth = 6; g.setLineDash([]); g.strokeRect(318, 78, 384, 104);
  g.fillStyle = '#5A3418'; g.font = 'bold 76px "Comic Sans MS", "Patrick Hand", cursive'; g.textAlign = 'center'; g.fillText('P.B.', 512, 160);
}, [1, 1], [0.5, 0]);
const stick = () => tex(256, 64, (g) => {
  g.fillStyle = '#E3C79A'; g.fillRect(0, 0, 256, 64);
  for (let i = 0; i < 30; i++) { g.strokeStyle = `rgba(150,110,60,${0.2 + rand(i) * 0.3})`; g.lineWidth = 1 + rand(i + 1) * 2; g.beginPath(); g.moveTo(0, rand(i + 2) * 64); g.lineTo(256, rand(i + 3) * 64); g.stroke(); }
});
// silver-painted card for the blade
const silverCard = () => tex(256, 256, (g) => fibres(g, 256, 256, '#C9CFD6', 'rgba(255,255,255,0.45)', 'rgba(120,128,138,0.35)', 1200));
const knifeBlade = () => {
  const s2 = new THREE.Shape(); // tip at 0,0; the blade runs up +y to the handle; flat edge on the left
  s2.moveTo(0.02, 0); s2.quadraticCurveTo(0.12, 0.04, 0.12, 0.22); s2.lineTo(0.1, 0.86); s2.lineTo(-0.07, 0.86); s2.lineTo(-0.07, 0.12); s2.quadraticCurveTo(-0.06, 0.01, 0.02, 0);
  const g = new THREE.ExtrudeGeometry(s2, { depth: 0.028, bevelEnabled: true, bevelThickness: 0.01, bevelSize: 0.01, bevelSegments: 2 });
  g.translate(0, 0, -0.014); return g;
};
const redFelt = () => tex(256, 256, (g) => fibres(g, 256, 256, '#C0392B', 'rgba(240,120,110,0.5)', 'rgba(110,20,15,0.5)', 1500), [2, 2]);

// ---------- a locked-off camera with tiny bumps; a slow stepped push ----------
const CamRig: React.FC<{ pose: number; sf: number }> = ({ pose, sf }) => {
  const { camera } = useThree();
  const push = clamp(sf / 450);
  const focus: V3 = sf < STEPS.knife.from ? [0, 0.2, 0.1] : sf < STEPS.spread.from ? [0.7, 0.35, -0.4] : sf < STEPS.press.from ? [-0.6, 0.25, 0.15] : [-0.65, 0.3, 0.2];
  const bump = 0.006;
  const px = mix(push, 0.4, -0.2) + (rand(pose * 3.1) - 0.5) * bump, py = mix(push, 3.4, 2.7) + (rand(pose * 5.3) - 0.5) * bump, pz = mix(push, 4.6, 3.9);
  useLayoutEffect(() => {
    camera.position.set(px, py, pz);
    camera.lookAt(focus[0] * 0.5, focus[1], focus[2] * 0.5);
    camera.updateProjectionMatrix();
  }, [camera, px, py, pz, focus]);
  return null;
};

const useKit = () => useMemo(() => {
  const slice = sliceShape(W, W), pbS = sliceShape(W * 0.99, W * 0.98);
  const sp = shapePolygon(slice, 100);
  const ca: V2 = [-W / 2 - 0.1, W / 2 + 0.1], cb: V2 = [W / 2 + 0.1, -W / 2 - 0.1];
  const pp = shapePolygon(pbS, 100);
  return {
    slice: flatSolid(slice, TH, BEV, 32), pb: flatSolid(pbS, PBH, 0.015, 32),
    halves: ([1, -1] as const).map((s) => ({ slice: flatSolid(polyShape(clipHalf(sp, ca, cb, s)), TH, BEV, 2), pb: flatSolid(polyShape(clipHalf(pp, ca, cb, s)), PBH, 0.015, 2) })),
    breadTop: breadTop(), crust: crustFelt(), pbT: pbFelt(), silver: silverCard(), blade: knifeBlade(), gingham: gingham(), cardboard: cardboard(), jar: kraftJar(), stick: stick(), red: redFelt(),
  };
}, []);

const Felt: React.FC<{ kit: ReturnType<typeof useKit>; geo: THREE.BufferGeometry }> = ({ kit, geo }) => (
  <mesh geometry={geo} castShadow receiveShadow>
    <meshStandardMaterial attach="material-0" map={kit.breadTop} roughness={1} bumpMap={kit.breadTop} bumpScale={0.6} />
    <meshStandardMaterial attach="material-1" map={kit.crust} roughness={1} bumpMap={kit.crust} bumpScale={0.6} />
  </mesh>
);

// a hand-placed wobble for each object in each pose
const jit = (pose: number, seed: number, amt = 1): { p: V3; r: V3 } => ({
  p: [(rand(pose * 7.1 + seed) - 0.5) * 0.008 * amt, 0, (rand(pose * 3.3 + seed * 2) - 0.5) * 0.008 * amt],
  r: [0, (rand(pose * 9.7 + seed * 3) - 0.5) * 0.012 * amt, 0],
});
const stepP = (sf: number, a: number, b: number) => clamp((sf - a) / (b - a)); // linear in poses: stop motion has no smooth easing

const Scene: React.FC<{ f: number }> = ({ f }) => {
  const kit = useKit();
  const pose = Math.floor(f / POSE);
  const sf = pose * POSE; // the frame of the current pose
  const flick = 1 + (rand(pose * 1.7) - 0.5) * 0.05;
  // step 1: slices hop in from the side in a few big moves
  const hopA = stepP(sf, at(K.two) - 10, at(K.two) + 4), hopB = stepP(sf, at(K.slices) - 8, at(K.slices) + 6);
  const arc = (t: number) => Math.sin(t * Math.PI * 3) * 0.25 * (1 - t);
  // step 2: lid twists off in steps, the stick dips in and comes out with a felt dollop
  const twist = stepP(sf, at(K.then) - 4, at(K.dig) + 6);
  const off = stepP(sf, at(K.dig) + 6, at(K.knife) + 2);
  const kIn = stepP(sf, at(K.knife) - 4, at(K.into) + 4);
  const dip = stepP(sf, at(K.into) + 4, at(K.peanut) + 4);
  const kOut = stepP(sf, at(K.butter) - 2, at(K.butter) + 12);
  // step 3: spreading; the felt piece grows in replacement sizes
  const go = stepP(sf, STEPS.spread.from - 6, at(K.spread) + 2);
  const sT = stepP(sf, at(K.spread), at(K.edges) + 6);
  const sizes = [0, 0.3, 0.45, 0.6, 0.72, 0.85, 1];
  const pbSize = sizes[Math.min(sizes.length - 1, Math.floor(sT * (sizes.length - 1) + (sT > 0 ? 1 : 0)))] ?? 0;
  const kAway = stepP(sf, at(K.edges) + 8, at(K.edges) + 22);
  // step 4: slice B up, over in 30-degree steps, down
  const up = stepP(sf, at(K.press) - 2, at(K.second) + 4);
  const over = Math.round(stepP(sf, at(K.second), at(K.on) + 2) * 6) / 6;
  const down = stepP(sf, at(K.on) + 2, at(K.top));
  const sq = sf >= at(K.top) && sf < at(K.top) + 8 ? 0.85 : 1; // a squashed replacement for two poses
  // step 5: the stick cuts in steps along the diagonal; then two half pieces
  const cutT = stepP(sf, at(K.cut) - 2, at(K.corner2) + 4);
  const cut = sf >= at(K.corner2) + 4;
  const part = stepP(sf, at(K.corner2) + 4, at(K.corner2) + 16);
  // step 6: the halves do a little alternating hop
  const dance = sf >= at(K.taste) ? Math.floor((sf - at(K.taste)) / (POSE * 2)) : -1;

  const jA = jit(pose, 1), jB = jit(pose, 2), jK = jit(pose, 3, 1.5), jJ = jit(pose, 4, 0.5);
  // stick knife path
  let kp: V3 = [JAR[0] + 0.05, mix(kIn, 2.6, 1.25) - dip * 0.45 + kOut * 0.9, JAR[2] + 0.05];
  let kr: V3 = [0, 0, 0.15];
  if (sf >= STEPS.spread.from - 6) {
    const zig = Math.sin(Math.floor(sT * 10) / 10 * Math.PI * 5);
    kp = [mix(go, JAR[0], A[0] + zig * 0.28) + kAway * 2.6, mix(go, 2.0, T + TH + 0.15) + kAway * 1.2, mix(go, JAR[2], A[2] + mix(sT, -0.25, 0.25)) - kAway * 1.4];
    kr = [mix(go, 0, -1.3), mix(go, 0, 1.0), mix(go, 0.15, -0.2)];
  }
  if (cutT > 0 && !cut) {
    const t = cutT;
    kp = [A[0] + mix(t, -0.95, 0.55), T + mix(t, 0.66, 0.12), A[2] + mix(t, -0.95, 0.55)];
    kr = [0, -Math.PI / 4, Math.PI / 2];
  }
  const showKnife = (sf >= at(K.knife) - 4 && kAway < 1) || (cutT > 0 && !cut);
  const blob = sf < STEPS.spread.from ? (kOut > 0 ? 1 : 0) : sT < 0.5 ? 1 - sT * 2 : 0;
  const bPos: V3 = [mix(hopB, 2.6, B[0]) + mix(up, 0, A[0] - B[0]) * clamp(over * 1.2), T + BEV + TH / 2 + arc(hopB) + up * 0.9 * (1 - down) + down * (TH + 2 * BEV + PBH), B[2]];

  return (
    <>
      <CamRig pose={pose} sf={sf} />
      <hemisphereLight args={['#FFF4E2', '#8A6E52', 0.7 * flick]} />
      <directionalLight position={[-3, 5.5, 3]} intensity={2.3 * flick} color="#FFE7C2" castShadow shadow-mapSize-width={2048} shadow-mapSize-height={2048}
        shadow-camera-left={-4} shadow-camera-right={4} shadow-camera-top={4} shadow-camera-bottom={-4} shadow-bias={-0.0004} shadow-radius={6} />
      <pointLight position={[3, 2.5, 2]} intensity={6 * flick} color="#FFD9A8" distance={9} />
      {/* tablecloth and cardboard board */}
      <mesh rotation={[-Math.PI / 2, 0, 0]} position={[0, -0.002, -0.3]} receiveShadow><planeGeometry args={[10, 4.6]} /><meshStandardMaterial map={kit.gingham} roughness={1} /></mesh>
      <mesh position={[0, T / 2, 0.1]} castShadow receiveShadow><boxGeometry args={[3.8, T, 2.3]} /><meshStandardMaterial map={kit.cardboard} roughness={1} /></mesh>
      {/* the kraft-paper jar with a felt lid */}
      <group position={[JAR[0] + jJ.p[0], 0, JAR[2] + jJ.p[2]]} rotation={jJ.r}>
        <mesh position={[0, 0.55, 0]} castShadow receiveShadow><cylinderGeometry args={[0.42, 0.44, 1.1, 40]} /><meshStandardMaterial map={kit.jar} roughness={1} /></mesh>
        <mesh position={[0, 1.105, 0]}><cylinderGeometry args={[0.36, 0.36, 0.01, 40]} /><meshStandardMaterial map={kit.pbT} roughness={1} /></mesh>
        <group position={[mix(off, 0, 0.9), 1.17 + (off > 0 && off < 1 ? 0.35 : 0) - off * 1.06, mix(off, 0, 0.4)]} rotation={[off * 0.3, Math.floor(twist * 5) / 5 * Math.PI, off * Math.PI]}>
          <mesh castShadow><cylinderGeometry args={[0.45, 0.45, 0.14, 40]} /><meshStandardMaterial map={kit.red} roughness={1} bumpMap={kit.red} bumpScale={0.5} /></mesh>
        </group>
      </group>
      {/* slice A + its felt peanut butter (until the cut) */}
      {!cut ? (
        <group position={[mix(hopA, -2.6, A[0]) + jA.p[0], arc(hopA), A[2] + jA.p[2]]} rotation={jA.r} scale={[1, sq, 1]}>
          <group position={[0, T + BEV, 0]}><Felt kit={kit} geo={kit.slice} /></group>
          {pbSize > 0 ? (
            <mesh geometry={kit.pb} position={[0, T + TH + 2 * BEV, 0.01]} scale={[pbSize, 1, pbSize]} castShadow receiveShadow>
              <meshStandardMaterial map={kit.pbT} roughness={1} bumpMap={kit.pbT} bumpScale={0.6} />
            </mesh>
          ) : null}
        </group>
      ) : null}
      {!cut && hopB > 0 ? (
        <group position={[bPos[0] + jB.p[0], bPos[1], bPos[2] + jB.p[2]]} rotation={[jB.r[0], jB.r[1], over * Math.PI]} scale={[1, sq, 1]}>
          <group position={[0, -TH / 2, 0]}><Felt kit={kit} geo={kit.slice} /></group>
        </group>
      ) : null}
      {/* after the cut: two half pieces, then a little dance */}
      {cut ? ([0, 1] as const).map((i) => {
        const h = kit.halves[i];
        const dir = i === 0 ? 1 : -1;
        const d = 0.34 * part;
        const hop = dance >= 0 && dance % 2 === i ? 0.14 : 0;
        const j = jit(pose, 10 + i);
        return (
          <group key={i} position={[A[0] + dir * d * 0.707 + j.p[0], hop, A[2] - dir * d * 0.707 + j.p[2]]} rotation={[0, j.r[1] + (hop ? dir * 0.12 : 0), 0]}>
            <group position={[0, T + BEV, 0]}><Felt kit={kit} geo={h.slice} /></group>
            <mesh geometry={h.pb} position={[0, T + TH + 2 * BEV, 0.01]} castShadow><meshStandardMaterial map={kit.pbT} roughness={1} /></mesh>
            <group position={[0, T + TH + 3 * BEV + PBH, 0]}><Felt kit={kit} geo={h.slice} /></group>
          </group>
        );
      }) : null}
      {/* the craft knife: card blade painted silver, felt collar, wooden handle */}
      {showKnife ? (
        <group position={[kp[0] + jK.p[0], kp[1], kp[2] + jK.p[2]]} rotation={kr}>
          <mesh geometry={kit.blade} castShadow><meshStandardMaterial map={kit.silver} roughness={0.55} metalness={0.35} /></mesh>
          <mesh position={[0.015, 0.89, 0]} castShadow><boxGeometry args={[0.2, 0.07, 0.07]} /><meshStandardMaterial map={kit.red} roughness={1} /></mesh>
          <mesh position={[0.015, 1.22, 0]} castShadow><boxGeometry args={[0.15, 0.6, 0.075]} /><meshStandardMaterial map={kit.stick} roughness={0.9} /></mesh>
          {blob > 0 ? <mesh position={[0, 0.12, 0.03]} castShadow><sphereGeometry args={[0.13, 14, 10]} /><meshStandardMaterial map={kit.pbT} roughness={1} /></mesh> : null}
        </group>
      ) : null}
    </>
  );
};

export const StopMotion: React.FC = () => {
  const f = useCurrentFrame();
  const pose = Math.floor(f / POSE);
  return (
    <AbsoluteFill style={{ overflow: 'hidden' }}>
      {/* the painted paper backdrop, soft like a close lens would make it */}
      <AbsoluteFill style={{ background: 'linear-gradient(180deg, #8EC9E8 0%, #BFE2F3 45%, #E8D6B8 46%, #E2CCAA 100%)', filter: 'blur(6px)', transform: 'scale(1.05)' }}>
        <div style={{ position: 'absolute', left: 260, top: 90, width: 360, height: 260, background: '#F7F2E7', borderRadius: 8 }}>
          <div style={{ position: 'absolute', inset: 18, background: '#A9DBF5' }} />
          <div style={{ position: 'absolute', left: 60, top: 70, width: 150, height: 54, background: '#fff', borderRadius: 30 }} />
        </div>
        <div style={{ position: 'absolute', left: 1240, top: 150, width: 420, height: 26, background: '#9B6B3D' }} />
        {[0, 1, 2].map((i) => <div key={i} style={{ position: 'absolute', left: 1280 + i * 120, top: 60, width: 80, height: 90, background: ['#E9806F', '#F2C14E', '#7FB77E'][i], borderRadius: 12 }} />)}
      </AbsoluteFill>
      <ThreeCanvas width={1920} height={1080} shadows gl={{ antialias: true, alpha: true }} camera={{ fov: 32, position: [0, 3, 4.6], near: 0.05, far: 50 }}
        style={{ position: 'absolute', inset: 0 }}>
        <Scene f={f} />
      </ThreeCanvas>
      {/* lens vignette and a hair of flicker over the whole picture */}
      <AbsoluteFill style={{ background: 'radial-gradient(ellipse at 50% 55%, rgba(0,0,0,0) 50%, rgba(30,15,0,0.35) 100%)', opacity: 0.9 + (rand(pose * 2.3) - 0.5) * 0.12 }} />
      <Soundtrack sfx={SFX} />
    </AbsoluteFill>
  );
};

const SFX: Sfx[] = [
  { at: at(K.two) + 2, file: 'card.wav', vol: 0.35 }, { at: at(K.slices) + 4, file: 'card2.wav', vol: 0.35 },
  { at: at(K.then) - 2, file: 'zip2.wav', vol: 0.25 }, { at: at(K.dig) + 8, file: 'bump2.wav', vol: 0.3 },
  { at: at(K.into) + 4, file: 'smack.wav', vol: 0.25 }, { at: at(K.butter), file: 'pop2.wav', vol: 0.3 },
  { at: at(K.spread), file: 'paper.wav', vol: 0.3, dur: 40 }, { at: at(K.edges) + 4, file: 'ding.wav', vol: 0.15 },
  { at: at(K.second), file: 'whoosh.wav', vol: 0.25 }, { at: at(K.top), file: 'thud.wav', vol: 0.4 },
  { at: at(K.cut), file: 'zip1.wav', vol: 0.3 }, { at: at(K.corner2) + 4, file: 'crack.wav', vol: 0.3 },
  { at: at(K.taste), file: 'bump2.wav', vol: 0.25 }, { at: at(K.taste) + 5, file: 'bump2.wav', vol: 0.25 }, { at: at(K.taste) + 10, file: 'bump2.wav', vol: 0.25 },
  { at: at(K.better), file: 'sparkle.wav', vol: 0.2 },
];
