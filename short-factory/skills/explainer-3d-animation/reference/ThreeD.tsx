// Style 10: 3D ANIMATION. A tabletop "food commercial" built with @remotion/three (no Blender): a marble counter, a wooden
// board, bread with crumb and crust, a glass jar of peanut butter, a steel knife; physically based materials lit by a
// warm key light with soft shadows and a studio reflection map; a cinematic camera that never stops moving. The knife
// really cuts the sandwich corner to corner and the halves part to show the layers.
import React, { useLayoutEffect, useMemo } from 'react';
import * as THREE from 'three';
import { RoomEnvironment } from 'three/examples/jsm/environments/RoomEnvironment.js';
import { ThreeCanvas } from '@remotion/three';
import { useThree } from '@react-three/fiber';
import { AbsoluteFill, Easing, useCurrentFrame } from 'remotion';
import { Soundtrack, Sfx } from '../../shared/Soundtrack';
import { K, STEPS, at } from '../../shared/timing';
import { clamp, easeInOut, mix, pop, prog, rand } from '../../shared/anim';
import { V2, clipHalf, cutSegment, flatSolid, polyShape, shapePolygon, sliceShape } from '../../shared/three/shapes';

type V3 = [number, number, number];
const BOARD_TOP = 0.1;
const A: V3 = [-0.85, BOARD_TOP, 0.25], B: V3 = [0.85, BOARD_TOP, 0.25], JAR: V3 = [1.75, 0, -1.6]; // behind the board (it ends at z -1.1)
const W = 1.3, TH = 0.17, BEV = 0.025, PBH = 0.065;

// ---------- procedural textures (drawn once) ----------
const canvasTex = (w: number, h: number, draw: (g: CanvasRenderingContext2D) => void, repeat: [number, number] = [1, 1]) => {
  const c = document.createElement('canvas'); c.width = w; c.height = h;
  draw(c.getContext('2d')!);
  const t = new THREE.CanvasTexture(c);
  t.colorSpace = THREE.SRGBColorSpace; t.wrapS = t.wrapT = THREE.RepeatWrapping; t.repeat.set(repeat[0], repeat[1]); t.anisotropy = 8;
  return t;
};
const crumbTex = () => canvasTex(512, 512, (g) => {
  g.fillStyle = '#F1DBA8'; g.fillRect(0, 0, 512, 512);
  for (let i = 0; i < 900; i++) {
    const x = rand(i) * 512, y = rand(i + 77) * 512, r = 1 + rand(i + 5) * 5;
    g.fillStyle = rand(i + 3) > 0.5 ? 'rgba(196,150,88,0.45)' : 'rgba(255,248,226,0.55)';
    g.beginPath(); g.ellipse(x, y, r, r * (0.5 + rand(i + 9) * 0.6), rand(i + 11) * 3, 0, Math.PI * 2); g.fill();
  }
}, [1 / W, 1 / W]);
const crustTex = () => canvasTex(256, 64, (g) => {
  const gr = g.createLinearGradient(0, 0, 0, 64); gr.addColorStop(0, '#B8702A'); gr.addColorStop(0.5, '#C98638'); gr.addColorStop(1, '#A9621F');
  g.fillStyle = gr; g.fillRect(0, 0, 256, 64);
  for (let i = 0; i < 200; i++) { g.fillStyle = `rgba(90,45,10,${0.08 + rand(i) * 0.12})`; g.fillRect(rand(i + 1) * 256, rand(i + 2) * 64, 2 + rand(i + 3) * 6, 1 + rand(i + 4) * 2); }
}, [3, 3]);
const woodTex = () => canvasTex(1024, 256, (g) => {
  g.fillStyle = '#B98352'; g.fillRect(0, 0, 1024, 256);
  for (let i = 0; i < 70; i++) {
    const y = rand(i) * 256, a = 4 + rand(i + 1) * 10;
    g.strokeStyle = `rgba(${rand(i + 2) > 0.5 ? '120,74,38' : '214,170,120'},${0.18 + rand(i + 3) * 0.25})`; g.lineWidth = 1 + rand(i + 4) * 3;
    g.beginPath(); for (let x = 0; x <= 1024; x += 16) g.lineTo(x, y + Math.sin(x / (60 + rand(i + 5) * 80) + i) * a); g.stroke();
  }
}, [1, 1]);
const marbleTex = () => canvasTex(1024, 1024, (g) => {
  g.fillStyle = '#ECEAE6'; g.fillRect(0, 0, 1024, 1024);
  for (let i = 0; i < 18; i++) {
    g.strokeStyle = `rgba(150,150,155,${0.08 + rand(i) * 0.14})`; g.lineWidth = 1 + rand(i + 1) * 3;
    g.beginPath(); let x = rand(i + 2) * 1024, y = 0;
    g.moveTo(x, y); while (y < 1024) { x += (rand(x + y) - 0.5) * 60; y += 30; g.lineTo(x, y); } g.stroke();
  }
}, [2, 2]);
const pbTex = () => canvasTex(512, 512, (g) => {
  g.fillStyle = '#B9762F'; g.fillRect(0, 0, 512, 512);
  g.filter = 'blur(10px)';
  for (let i = 0; i < 40; i++) {
    const x = rand(i + 2) * 512, y = rand(i + 3) * 512, r = 40 + rand(i + 4) * 110;
    g.fillStyle = rand(i) > 0.5 ? 'rgba(214,150,80,0.35)' : 'rgba(150,86,30,0.35)';
    g.beginPath(); g.ellipse(x, y, r, r * 0.6, rand(i + 5) * 3, 0, Math.PI * 2); g.fill();
  }
  g.filter = 'blur(3px)';
  for (let i = 0; i < 14; i++) {
    g.strokeStyle = 'rgba(232,178,110,0.45)'; g.lineWidth = 5 + rand(i + 7) * 7;
    g.beginPath(); g.arc(rand(i + 8) * 512, rand(i + 9) * 512, 60 + rand(i + 10) * 120, rand(i + 11) * 6, rand(i + 11) * 6 + 0.8 + rand(i + 12)); g.stroke();
  }
  g.filter = 'none';
}, [1 / W, 1 / W]);

// ---------- camera: [frame, position, target] with smooth easing ----------
const CAM: [number, V3, V3][] = [
  [0, [0.2, 3.6, 6.2], [0, 0.2, 0]], [66, [0.1, 2.7, 4.4], [0, 0.25, 0.1]],
  [80, [2.9, 1.7, 1.9], [1.45, 0.55, -0.7]], [128, [2.6, 1.55, 1.6], [1.4, 0.55, -0.75]],
  [142, [-0.95, 2.35, 1.95], [-0.85, 0.18, 0.2]], [206, [-0.75, 2.15, 1.75], [-0.85, 0.2, 0.25]],
  [218, [0.9, 1.0, 2.6], [-0.45, 0.4, 0.2]], [268, [0.6, 0.95, 2.45], [-0.6, 0.35, 0.25]],
  [280, [-2.5, 1.25, 2.1], [-0.85, 0.3, 0.25]], [326, [-2.2, 1.05, 2.0], [-0.85, 0.3, 0.25]],
  [338, [1.0, 1.75, 3.3], [-0.85, 0.3, 0.25]], [450, [-2.3, 1.9, 3.0], [-0.85, 0.3, 0.25]],
];
const camAt = (f: number) => {
  let i = 0;
  while (i < CAM.length - 2 && f >= CAM[i + 1][0]) i++;
  const [f0, p0, t0] = CAM[i], [f1, p1, t1] = CAM[i + 1];
  const move = f1 - f0 <= 16;
  const t = clamp((f - f0) / (f1 - f0));
  const e = move ? Easing.bezier(0.6, 0, 0.3, 1)(t) : t;
  return { p: p0.map((v, k) => mix(e, v, p1[k])) as V3, t: t0.map((v, k) => mix(e, v, t1[k])) as V3 };
};

const Rig: React.FC<{ f: number }> = ({ f }) => {
  const { camera, gl, scene } = useThree();
  const c = camAt(f);
  useLayoutEffect(() => {
    camera.position.set(...c.p); camera.lookAt(...c.t); camera.updateProjectionMatrix();
  }, [camera, c.p, c.t]);
  useLayoutEffect(() => {
    // a studio reflection map built in code (no download): metal and glass get real-looking reflections
    const pm = new THREE.PMREMGenerator(gl);
    const env = pm.fromScene(new RoomEnvironment(), 0.04).texture;
    scene.environment = env;
    scene.environmentIntensity = 0.55;
    gl.toneMapping = THREE.ACESFilmicToneMapping; gl.toneMappingExposure = 1.05;
    return () => { env.dispose(); pm.dispose(); };
  }, [gl, scene]);
  return null;
};

const useKit = () => useMemo(() => {
  const slice = sliceShape(W, W);
  const pbShape = sliceShape(W * 0.96, W * 0.95);
  const sp = shapePolygon(slice, 110), pp = shapePolygon(pbShape, 110);
  // corner to corner: from the outline's top-left corner to its bottom-right corner
  const ca: V2 = [-W / 2 - 0.1, W / 2 + 0.1], cb: V2 = [W / 2 + 0.1, -W / 2 - 0.1];
  const halves = ([1, -1] as const).map((side) => ({
    slice: flatSolid(polyShape(clipHalf(sp, ca, cb, side)), TH, BEV, 2),
    pb: flatSolid(polyShape(clipHalf(pp, ca, cb, side)), PBH, 0.01, 2),
  }));
  const knife = (() => {
    const s = new THREE.Shape();
    s.moveTo(0, 0); s.quadraticCurveTo(0.08, 0.03, 0.085, 0.22); s.lineTo(0.085, 1.0); s.lineTo(-0.075, 1.0); s.lineTo(-0.075, 0.3); s.quadraticCurveTo(-0.07, 0.06, 0, 0);
    return new THREE.ExtrudeGeometry(s, { depth: 0.014, bevelEnabled: true, bevelThickness: 0.004, bevelSize: 0.004, bevelSegments: 2 });
  })();
  const chef = (() => {
    const s = new THREE.Shape();
    s.moveTo(0, 0); s.lineTo(1.7, 0); s.quadraticCurveTo(1.68, 0.28, 1.4, 0.36); s.lineTo(0, 0.36); s.lineTo(0, 0);
    return new THREE.ExtrudeGeometry(s, { depth: 0.012, bevelEnabled: true, bevelThickness: 0.003, bevelSize: 0.003, bevelSegments: 2 });
  })();
  // the cut face (bread / peanut butter / bread) as a texture
  const face = canvasTex(64, 256, (g) => {
    const total = 2 * (TH + 2 * BEV) + PBH;
    const a1 = (TH + 2 * BEV) / total, p1 = (TH + 2 * BEV + PBH) / total;
    g.fillStyle = '#F1DBA8'; g.fillRect(0, 0, 64, 256);
    g.fillStyle = '#9A531C'; g.fillRect(0, 256 * (1 - p1), 64, 256 * (p1 - a1));
    g.fillStyle = '#B8702A'; g.fillRect(0, 0, 64, 8); g.fillRect(0, 248, 64, 8);
  });
  return {
    slice: flatSolid(slice, TH, BEV), pb: flatSolid(pbShape, PBH, 0.012), halves, seg: cutSegment(sp, ca, cb), knife, chef, face,
    crumb: crumbTex(), crust: crustTex(), wood: woodTex(), marble: marbleTex(), pbT: pbTex(),
  };
}, []);

const Bread: React.FC<{ kit: ReturnType<typeof useKit>; geo: THREE.BufferGeometry }> = ({ kit, geo }) => (
  <mesh geometry={geo} castShadow receiveShadow>
    <meshStandardMaterial attach="material-0" map={kit.crumb} roughness={0.92} />
    <meshStandardMaterial attach="material-1" map={kit.crust} roughness={0.8} />
  </mesh>
);

const Scene: React.FC<{ f: number }> = ({ f }) => {
  const kit = useKit();
  // step 1: slices fall onto the board
  // owner: "The breads disappear into the cutting board": the spring overshot below the board. Clamp the height; the
  // overshoot becomes a short squash.
  const dropAraw = pop(f, at(K.two) - 6, { damping: 11, stiffness: 120 }), dropBraw = pop(f, at(K.slices) - 6, { damping: 11, stiffness: 120 });
  const dropA = Math.min(1, dropAraw), dropB = Math.min(1, dropBraw);
  const landA = 1 - 0.6 * Math.max(0, dropAraw - 1), landB = 1 - 0.6 * Math.max(0, dropBraw - 1);
  // step 2: the lid lifts away, the knife dips in and comes out loaded
  const lid = prog(f, at(K.then) - 4, at(K.dig) + 8, easeInOut);
  const kIn = prog(f, at(K.knife) - 6, at(K.into) + 4, Easing.out(Easing.cubic));
  const dip = prog(f, at(K.into), at(K.peanut) + 4, easeInOut);
  const kOut = prog(f, at(K.butter) - 2, at(K.butter) + 14, easeInOut);
  // step 3: spreading
  const go = prog(f, STEPS.spread.from - 8, at(K.spread) + 2, easeInOut);
  const sT = prog(f, at(K.spread), at(K.edges) + 6, (t) => t);
  const pb = prog(f, at(K.spread), at(K.edges) + 6, Easing.inOut(Easing.quad));
  const kAway = prog(f, at(K.edges) + 8, at(K.edges) + 24, Easing.in(Easing.cubic));
  // step 4: the second slice turns over onto the first
  const up = prog(f, at(K.press) - 2, at(K.second) + 6, easeInOut);
  const over = prog(f, at(K.second) - 2, at(K.on) + 2, easeInOut);
  const down = prog(f, at(K.on) - 2, at(K.top) - 1, Easing.in(Easing.quad));
  const squash = f >= at(K.top) - 1 ? Math.sin(clamp((f - at(K.top) + 1) / 10) * Math.PI) * Math.exp(-(f - at(K.top) + 1) / 14) : 0;
  // step 5: the chef's knife slices down along the diagonal
  const cutIn = prog(f, at(K.cut) - 6, at(K.corner1), easeInOut);
  const slice = prog(f, at(K.corner1), at(K.corner2) + 4, easeInOut);
  const cutOut = prog(f, at(K.corner2) + 6, at(K.corner2) + 20, Easing.in(Easing.cubic));
  const cut = f >= at(K.corner2) + 4;
  const part = prog(f, at(K.corner2) + 4, at(K.corner2) + 20, Easing.out(Easing.back(1.3)));
  // step 6: the halves turn to show the layers
  const hero = prog(f, STEPS.payoff.from, STEPS.payoff.from + 40, easeInOut);

  // knife path (steps 2-3)
  let kp: V3 = [JAR[0], mix(kIn, 3.2, 1.25) - dip * 0.42 + kOut * 0.85, JAR[2]];
  let kr: V3 = [0, 0, 0];
  const blob = f < STEPS.spread.from ? clamp(kOut * 2.5) : 1 - pb;
  if (f >= STEPS.spread.from - 8) {
    const zig = Math.sin(sT * Math.PI * 5);
    kp = [mix(go, JAR[0], A[0] + zig * 0.3) + kAway * 2.4, mix(go, 2.1, A[1] + TH + 0.12) + kAway * 1.4, mix(go, JAR[2], A[2] + mix(sT, -0.3, 0.3)) - kAway * 1.4];
    kr = [mix(go, 0, -1.35), mix(go, 0, 1.1), mix(go, 0, -0.2 + zig * 0.25)];
  }
  const showKnife = f >= at(K.knife) - 6 && kAway < 1;

  // slice B
  const bPos: V3 = [mix(over, B[0], A[0]), BOARD_TOP + BEV + TH / 2 + mix(up, 0, 1.0) * (1 - down) + down * (TH + 2 * BEV + PBH) + (1 - dropB) * 3, mix(over, B[2], A[2])];
  const [s0, s1] = kit.seg;
  const segMid: V3 = [(s0[0] + s1[0]) / 2, 0, -(s0[1] + s1[1]) / 2];
  const segLen = Math.hypot(s1[0] - s0[0], s1[1] - s0[1]);
  const segAng = Math.atan2(-(s1[1] - s0[1]), s1[0] - s0[0]);
  const total = 2 * (TH + 2 * BEV) + PBH;

  return (
    <>
      <Rig f={f} />
      <hemisphereLight args={['#FFF6E8', '#C9B79C', 0.55]} />
      <directionalLight position={[-3.5, 6, 3.5]} intensity={2.6} color="#FFF1DC" castShadow shadow-mapSize-width={2048} shadow-mapSize-height={2048}
        shadow-camera-left={-4} shadow-camera-right={4} shadow-camera-top={4} shadow-camera-bottom={-4} shadow-bias={-0.0003} shadow-radius={4} />
      <directionalLight position={[4, 3, -4]} intensity={0.9} color="#CFE6FF" />
      {/* backdrop and counter */}
      <mesh position={[0, 3, -5]} receiveShadow><planeGeometry args={[30, 12]} /><meshStandardMaterial color="#E9DCC8" roughness={1} /></mesh>
      <mesh rotation={[-Math.PI / 2, 0, 0]} position={[0, -0.001, 0]} receiveShadow><planeGeometry args={[30, 30]} /><meshStandardMaterial map={kit.marble} roughness={0.35} /></mesh>
      {/* the board */}
      <mesh position={[0, BOARD_TOP / 2, 0.15]} castShadow receiveShadow>
        <boxGeometry args={[4.1, BOARD_TOP, 2.5]} /><meshStandardMaterial map={kit.wood} roughness={0.65} />
      </mesh>
      {/* the jar: glass, peanut butter inside, a lid that lifts away */}
      <group position={JAR}>
        <mesh position={[0, 0.36 - dip * 0.03, 0]} castShadow><cylinderGeometry args={[0.36, 0.36, 0.72, 48]} /><meshStandardMaterial map={kit.pbT} roughness={0.38} /></mesh>
        <mesh position={[0, 0.55, 0]} castShadow><cylinderGeometry args={[0.41, 0.41, 1.1, 48, 1, true]} />
          <meshPhysicalMaterial color="#E8F4FA" transparent opacity={0.28} roughness={0.05} metalness={0} clearcoat={1} side={THREE.DoubleSide} /></mesh>
        <mesh position={[0, 0.5, 0]}><cylinderGeometry args={[0.415, 0.415, 0.38, 48, 1, true]} /><meshStandardMaterial color="#C8202F" roughness={0.6} /></mesh>
        <group position={[mix(lid, 0, 0.95), 1.16 + Math.sin(lid * Math.PI) * 0.7 - lid * 1.07, mix(lid, 0, -0.45)]} rotation={[lid * 0.2, lid * Math.PI * 2, lid * Math.PI * 0.95]}>
          <mesh castShadow><cylinderGeometry args={[0.43, 0.43, 0.14, 48]} /><meshStandardMaterial color="#C8202F" roughness={0.45} metalness={0.1} /></mesh>
        </group>
      </group>
      {/* slice A + peanut butter (until the cut) */}
      {!cut ? (
        <group position={[A[0], 0, A[2]]} scale={[1 + 0.04 * squash, 1 - 0.1 * squash, 1 + 0.04 * squash]}>
          <group position={[0, BOARD_TOP + BEV + (1 - dropA) * 3, 0]} rotation={[0, (1 - dropA) * 0.5, 0]} scale={[1, landA, 1]}><Bread kit={kit} geo={kit.slice} /></group>
          {pb > 0 ? (
            <mesh geometry={kit.pb} position={[0, BOARD_TOP + TH + 2 * BEV, 0.01]} scale={[0.12 + 0.88 * pb, 1, 0.12 + 0.88 * pb]} castShadow receiveShadow>
              <meshStandardMaterial map={kit.pbT} roughness={0.32} />
            </mesh>
          ) : null}
        </group>
      ) : null}
      {!cut && dropB > 0.01 ? (
        <group position={bPos} rotation={[0, (1 - dropB) * -0.4, over * Math.PI]} scale={[1 + 0.04 * squash * down, (1 - 0.1 * squash * down) * landB, 1 + 0.04 * squash * down]}>
          <group position={[0, -TH / 2, 0]}><Bread kit={kit} geo={kit.slice} /></group>
        </group>
      ) : null}
      {/* after the cut: two halves, each bread / peanut butter / bread, with the cut face showing the layers */}
      {cut ? ([0, 1] as const).map((i) => {
        const h = kit.halves[i];
        const dir = i === 0 ? 1 : -1; // half 0 = left of the cut line (far side), half 1 = near side
        // part along the normal of the cut (outline coords -> world x, z = -y)
        const off = 0.22 * part + 0.06 * hero;
        const normal: [number, number] = [-(s1[1] - s0[1]) / segLen, -(s1[0] - s0[0]) / segLen];
        const turn = (i === 1 ? -1 : 1) * hero * 0.35;
        return (
          <group key={i} position={[A[0] + normal[0] * off * dir, 0, A[2] + normal[1] * off * dir]} rotation={[0, turn, 0]}>
            <group position={[0, BOARD_TOP + BEV, 0]}><Bread kit={kit} geo={h.slice} /></group>
            <mesh geometry={h.pb} position={[0, BOARD_TOP + TH + 2 * BEV, 0.01]} castShadow><meshStandardMaterial map={kit.pbT} roughness={0.32} /></mesh>
            <group position={[0, BOARD_TOP + TH + 3 * BEV + PBH, 0]}><Bread kit={kit} geo={h.slice} /></group>
            <mesh position={[segMid[0] + normal[0] * 0.034 * dir, BOARD_TOP + total / 2 + 0.005, segMid[2] + normal[1] * 0.034 * dir]} rotation={[0, -segAng + (i === 0 ? Math.PI : 0), 0]}>
              <planeGeometry args={[segLen * 0.99, total + 0.05]} /><meshStandardMaterial map={kit.face} roughness={0.85} side={THREE.DoubleSide} />
            </mesh>
          </group>
        );
      }) : null}
      {/* the butter knife (steps 2-3): tip at the origin, blade up, handle on top */}
      {showKnife ? (
        <group position={kp} rotation={kr}>
          <mesh geometry={kit.knife} position={[0, 0, -0.007]} castShadow><meshStandardMaterial color="#DDE3E8" metalness={1} roughness={0.22} /></mesh>
          <mesh position={[0.005, 1.27, 0]} castShadow><boxGeometry args={[0.14, 0.55, 0.08]} /><meshStandardMaterial color="#1D1A18" roughness={0.5} /></mesh>
          {blob > 0 ? <mesh position={[0.005, 0.17, 0]} scale={[blob, blob * 1.25, blob]} castShadow><sphereGeometry args={[0.12, 24, 18]} /><meshStandardMaterial map={kit.pbT} roughness={0.3} /></mesh> : null}
        </group>
      ) : null}
      {/* the chef's knife (step 5): edge down, slicing along the diagonal */}
      {cutIn > 0 && cutOut < 1 ? (() => {
        // the blade stands upright in the vertical plane of the cut line (its local x runs along the cut), edge down
        const along = mix(slice, -0.4, 0.4) * segLen;
        const ux = Math.cos(segAng), uz = Math.sin(segAng);
        const x = A[0] + segMid[0] + along * ux, z = A[2] + segMid[2] + along * uz;
        const y = mix(cutIn, 1.5, BOARD_TOP + total + 0.06) - slice * (total + 0.04) + cutOut * 1.5;
        return (
          <group position={[x, y, z]} rotation={[0, -segAng, 0]}>
            <mesh geometry={kit.chef} position={[-0.8, 0, -0.006]} castShadow><meshStandardMaterial color="#EEF2F5" metalness={0.75} roughness={0.28} /></mesh>
            <mesh position={[-1.05, 0.2, 0]} castShadow><boxGeometry args={[0.5, 0.13, 0.07]} /><meshStandardMaterial color="#1D1A18" roughness={0.5} /></mesh>
          </group>
        );
      })() : null}    </>
  );
};

export const ThreeD: React.FC = () => {
  const f = useCurrentFrame();
  return (
    <AbsoluteFill style={{ background: '#E9DCC8' }}>
      <ThreeCanvas width={1920} height={1080} shadows gl={{ antialias: true }} camera={{ fov: 34, position: [0, 3, 6], near: 0.05, far: 60 }}
        style={{ position: 'absolute', inset: 0 }}>
        <Scene f={f} />
      </ThreeCanvas>
      {/* a soft vignette like a lens */}
      <AbsoluteFill style={{ background: 'radial-gradient(ellipse at 50% 50%, rgba(0,0,0,0) 55%, rgba(40,25,10,0.28) 100%)' }} />
      <Soundtrack sfx={SFX} />
    </AbsoluteFill>
  );
};

const SFX: Sfx[] = [
  { at: at(K.two) - 2, file: 'card.wav', vol: 0.4 }, { at: at(K.slices) - 2, file: 'card2.wav', vol: 0.4 },
  { at: 66, file: 'swipe1.wav', vol: 0.25 }, { at: at(K.then) - 2, file: 'zip2.wav', vol: 0.3 }, { at: at(K.dig) + 8, file: 'bump2.wav', vol: 0.3 },
  { at: at(K.into) + 2, file: 'smack.wav', vol: 0.3 }, { at: at(K.butter) - 2, file: 'pop2.wav', vol: 0.3 },
  { at: 132, file: 'swipe2.wav', vol: 0.25 }, { at: at(K.spread), file: 'paper.wav', vol: 0.3, dur: 40 },
  { at: 210, file: 'swipe3.wav', vol: 0.25 }, { at: at(K.second) - 2, file: 'whoosh.wav', vol: 0.3 }, { at: at(K.top) - 1, file: 'thud.wav', vol: 0.45 },
  { at: 272, file: 'swipe1.wav', vol: 0.25 }, { at: at(K.corner1), file: 'zip1.wav', vol: 0.4 }, { at: at(K.corner2) + 4, file: 'crack.wav', vol: 0.35 },
  { at: at(K.corner2) + 6, file: 'whip.wav', vol: 0.3 }, { at: at(K.better), file: 'sparkle.wav', vol: 0.2 },
];
