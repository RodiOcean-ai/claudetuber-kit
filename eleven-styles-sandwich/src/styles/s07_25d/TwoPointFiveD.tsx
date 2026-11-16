// Style 7: 2.5D, Build 2 (owner's notes on Build 1: "the bread doesn't look like it is on the board, maybe try a top view",
// "not sure what's happening with the knife and the PB", "spread with the edge of the knife, not the handle", "not corner
// to corner"). A TOP-DOWN set: flat photo layers (made on the free local picture maker, cut out) stacked at different
// heights above a cutting board and filmed by a camera that drifts, turns and pushes in, so higher things slide over lower
// things (parallax) and cast soft shadows that move with their height. Slices drop onto the board, the lid lifts off the
// open jar, the knife dips into the peanut butter and comes out loaded, the blade lies on the bread while the real peanut
// butter appears under it, the second slice flips over onto the first, and the knife cuts the sandwich corner to corner.
// (Build 1, the side view, is kept in assets_work/TwoPointFiveD_build1.tsx.)
import React from 'react';
import { AbsoluteFill, Easing, Img, interpolate, staticFile, useCurrentFrame } from 'remotion';
import { Soundtrack, Sfx } from '../../shared/Soundtrack';
import { K, STEPS, at } from '../../shared/timing';
import { clamp, easeInOut, mix, pop, prog } from '../../shared/anim';

const img = (n: string) => staticFile(`img/p25top/${n}.png`);
const P = 1600;
const Z_TABLE = -900, Z_OBJ = -880, Z_HELD = -760, Z_FG = 360;
// the board picture (1664 x 928) shown 3750 wide; its board is centred near picture px (845, 472)
const BG_W = 3750, BG_H = (3750 * 928) / 1664;
const BOARD_C = { x: (845 / 1664 - 0.5) * BG_W, y: (472 / 928 - 0.5) * BG_H };
// layout on the board (world units, the board centre is 0,0)
const A = { x: -480, y: 70 }, B = { x: 250, y: 70 }, JAR = { x: 840, y: -330 }, LID_SPOT = { x: 880, y: 360 };
const SLICE_W = 620;                     // bread width in world units
const SW_W = (SLICE_W * 831) / 732;      // the top-down sandwich picture (831 x 889) has peanut butter peeking out
const JAR_W = 440, LID_W = 370, KNIFE_W = 720;
// knife pictures: tip at the left end; the blade is the left ~45 %
const KNIFE = { w: 1216, h: 153, tip: [10, 52] }, KNIFE_PB = { w: 1304, h: 277, tip: [12, 118] };
// sandwich picture corners (px of 831 x 889) for the cut, and the jar opening (px of 880 x 913)
const SW_TL = [105, 96], SW_BR = [768, 823], JAR_OPEN = { cx: 442, cy: 452, r: 318 };

type L = { x: number; y: number; z: number; w: number; src: string; ar: number; r?: number; ry?: number; s?: number; o?: number; clip?: string; shadow?: boolean };
// a flat picture lying at height z, with its soft shadow on the table (light from the top left)
const Layer: React.FC<{ l: L; children?: React.ReactNode }> = ({ l, children }) => {
  const h = l.w / l.ar, lift = l.z - Z_TABLE;
  return (
    <>
      {l.shadow !== false ? (
        <div style={{ position: 'absolute', left: 0, top: 0, transformStyle: 'preserve-3d',
          transform: `translate3d(${l.x + 10 + lift * 0.09}px, ${l.y + 14 + lift * 0.11}px, ${Z_TABLE + 1}px) rotateZ(${l.r ?? 0}deg) scale(${l.s ?? 1})` }}>
          <Img src={img(l.src)} style={{ position: 'absolute', left: -l.w / 2, top: -h / 2, width: l.w, height: h, clipPath: l.clip,
            filter: `brightness(0) blur(${8 + lift * 0.05}px)`, opacity: (l.o ?? 1) * clamp(0.42 - lift * 0.0005, 0.12, 0.42) }} />
        </div>
      ) : null}
      <div style={{ position: 'absolute', left: 0, top: 0, transformStyle: 'preserve-3d',
        transform: `translate3d(${l.x}px, ${l.y}px, ${l.z}px) rotateZ(${l.r ?? 0}deg) rotateY(${l.ry ?? 0}deg) scale(${l.s ?? 1})`, opacity: l.o ?? 1 }}>
        <div style={{ position: 'absolute', left: -l.w / 2, top: -h / 2, width: l.w, height: h, clipPath: l.clip }}>
          {children ?? <Img src={img(l.src)} style={{ width: '100%', height: '100%' }} />}
        </div>
      </div>
    </>
  );
};

// camera keys: [frame, x, y, push toward the board, turn (deg)]
const CAM: [number, number, number, number, number][] = [
  [0, 0, 60, -160, -3], [64, -120, 50, 0, -2], [78, 360, -170, 160, 0], [126, 380, -160, 210, 1], [140, -360, 50, 300, 2],
  [206, -330, 50, 340, 3], [216, -170, 50, 220, 1], [270, -250, 60, 260, 0], [282, -400, 70, 360, -1], [328, -400, 70, 380, -2],
  [450, -420, 70, 560, 5],
];
const camAt = (f: number) => {
  let i = 0;
  while (i < CAM.length - 2 && f >= CAM[i + 1][0]) i++;
  const a = CAM[i], b = CAM[i + 1];
  const t = interpolate(f, [a[0], b[0]], [0, 1], { extrapolateLeft: 'clamp', extrapolateRight: 'clamp', easing: b[0] - a[0] <= 16 ? Easing.bezier(0.6, 0, 0.3, 1) : (x) => x });
  return { x: mix(t, a[1], b[1]), y: mix(t, a[2], b[2]), z: mix(t, a[3], b[3]), r: mix(t, a[4], b[4]) };
};

// where the knife picture's centre goes so that its TIP sits at (tx, ty), pointing along angle (deg; 180 = tip to the left)
const knifeAt = (tx: number, ty: number, ang: number, k: typeof KNIFE) => {
  const w = KNIFE_W, h = (KNIFE_W * k.h) / k.w;
  const off = { x: (k.tip[0] / k.w) * w - w / 2, y: (k.tip[1] / k.h) * h - h / 2 }; // tip relative to the picture centre (tip left)
  const a = ((ang - 180) * Math.PI) / 180;               // rotation applied to the picture
  const rx = off.x * Math.cos(a) - off.y * Math.sin(a), ry = off.x * Math.sin(a) + off.y * Math.cos(a);
  return { x: tx - rx, y: ty - ry, r: ang - 180, ar: k.w / k.h };
};

// the spreading path (relative to slice A's centre): 6 passes down the slice, the tip moving left-right a little
const PASSES = 6;
const spreadAt = (t: number) => {
  const tt = t * PASSES, row = Math.floor(Math.min(tt, PASSES - 0.001)), w = tt - row, dir = row % 2 === 0 ? 1 : -1;
  return { x: -250 + (dir > 0 ? w : 1 - w) * 165, y: -300 + (row + w) * (600 / PASSES), wob: Math.sin(tt * Math.PI) };
};

export const TwoPointFiveD: React.FC = () => {
  const f = useCurrentFrame();
  const cam = camAt(f);

  // step 1: the slices drop onto the board (never below it: the overshoot becomes a squash)
  const dA = pop(f, at(K.two) - 8, { damping: 12, stiffness: 120 }), dB = pop(f, at(K.slices) - 8, { damping: 12, stiffness: 120 });
  const hA = (1 - Math.min(1, dA)) * 900, hB = (1 - Math.min(1, dB)) * 900;
  const sqA = 1 + 0.24 * Math.max(0, dA - 1), sqB = 1 + 0.24 * Math.max(0, dB - 1);
  // step 2: the lid lifts off and lands on the board; the knife dips into the jar and comes out loaded
  const lid = prog(f, at(K.then) - 2, at(K.dig) + 10, easeInOut);
  const kIn = prog(f, at(K.knife) - 8, at(K.into) - 2, Easing.out(Easing.cubic));
  const dip = prog(f, at(K.into) - 2, at(K.peanut), easeInOut);
  const kUp = prog(f, at(K.butter) - 4, at(K.butter) + 8, easeInOut);
  // step 3: spreading with the blade flat on the bread
  const toA = prog(f, STEPS.spread.from - 8, at(K.spread) + 2, easeInOut);
  const sT = prog(f, at(K.spread), at(K.edges) + 4, (t) => t);
  const kAway = prog(f, at(K.edges) + 6, at(K.edges) + 20, Easing.in(Easing.cubic));
  // step 4: slice B lifts, flips over, lands on A
  const up = prog(f, at(K.press) - 4, at(K.second) + 6, easeInOut);
  const over = prog(f, at(K.second) - 2, at(K.on) + 2, easeInOut);
  const down = prog(f, at(K.on), at(K.top) - 1, Easing.in(Easing.quad));
  const landed = f >= at(K.top) - 1;
  const squash = landed ? Math.sin(clamp((f - at(K.top) + 1) / 9) * Math.PI) * Math.exp(-(f - at(K.top) + 1) / 12) : 0;
  // step 5: the cut, corner to corner, then the halves part
  const cutK = prog(f, at(K.cut) - 2, at(K.corner2) + 6, easeInOut);
  const cut = f >= at(K.corner2) + 6;
  const part = prog(f, at(K.corner2) + 6, at(K.corner2) + 20, Easing.out(Easing.back(1.4)));
  const sep = 46 * part + 26 * prog(f, STEPS.payoff.from, 420, easeInOut);

  // the sandwich's corners in world units
  const swH = (SW_W * 889) / 831, kSW = SW_W / 831;
  const tl = { x: A.x - SW_W / 2 + SW_TL[0] * kSW, y: A.y - swH / 2 + SW_TL[1] * kSW }, br = { x: A.x - SW_W / 2 + SW_BR[0] * kSW, y: A.y - swH / 2 + SW_BR[1] * kSW };

  // ----- the knife -----
  let knife = { tx: 0, ty: 0, ang: 180, z: Z_HELD, pb: false, show: false };
  if (f >= at(K.knife) - 8 && f < STEPS.spread.from - 8) {
    // in from the right, tip over the jar's opening, down into the peanut butter, up again with a dollop
    knife = { tx: mix(kIn, JAR.x + 900, JAR.x + 40), ty: mix(kIn, JAR.y - 120, JAR.y + 10), ang: 200, z: mix(dip, Z_HELD, Z_OBJ + 18) + kUp * 110,
      pb: f >= at(K.butter), show: true };
  } else if (f >= STEPS.spread.from - 8 && kAway < 1) {
    // to slice A; then the blade lies on the bread (tip to the left, handle off the slice to the right) and sweeps it
    const s = spreadAt(sT);
    knife = { tx: mix(toA, JAR.x + 40, A.x + s.x) + kAway * 1200, ty: mix(toA, JAR.y + 10, A.y + s.y) - kAway * 300, ang: 180 + 6 * s.wob,
      z: mix(toA, Z_HELD, Z_OBJ + 26), pb: sT < 0.35, show: true };
  } else if (cutK > 0 && !cut) {
    // the cut: tip first along the sandwich's diagonal, from beyond its top-left corner to beyond its bottom-right corner
    const ang = (Math.atan2(br.y - tl.y, br.x - tl.x) * 180) / Math.PI;
    knife = { tx: mix(cutK, tl.x - 0.15 * (br.x - tl.x), br.x + 0.12 * (br.x - tl.x)), ty: mix(cutK, tl.y - 0.15 * (br.y - tl.y), br.y + 0.12 * (br.y - tl.y)),
      ang, z: Z_OBJ + 40, pb: false, show: true };
  }
  const kk = knifeAt(knife.tx, knife.ty, knife.ang, knife.pb ? KNIFE_PB : KNIFE);

  // ----- the peanut butter appears under the blade (a mask of every place the blade has passed) -----
  const pbLayerW = SLICE_W * 0.9, pbLayerH = (pbLayerW * 807) / 721;
  const passesDone: { y: number; x0: number; x1: number }[] = [];
  if (f >= at(K.spread)) {
    const steps = Math.round(sT * 60);
    for (let i = 0; i <= steps; i++) {
      const s = spreadAt(i / 60);
      passesDone.push({ y: s.y, x0: s.x - 40, x1: s.x + 330 });          // the blade covers ~330 units right of its tip (knife 720 wide)
    }
  }
  const fullPB = f >= at(K.edges) + 6;
  const sliceH = (SLICE_W * 865) / 732;

  // the sandwich halves (clip paths in % of the sandwich picture)
  const pc = (x: number, y: number) => `${(x / 831) * 100}% ${(y / 889) * 100}%`;
  const D = [SW_BR[0] - SW_TL[0], SW_BR[1] - SW_TL[1]];
  const L1 = [SW_TL[0] - D[0], SW_TL[1] - D[1]], L2 = [SW_BR[0] + D[0], SW_BR[1] + D[1]];
  const HALF_UR = `polygon(${pc(L1[0], L1[1])}, ${pc(L2[0], L2[1])}, ${pc(3000, -3000)})`, HALF_LL = `polygon(${pc(L1[0], L1[1])}, ${pc(L2[0], L2[1])}, ${pc(-3000, 3000)})`;
  const nrm = (() => { const l = Math.hypot(D[0], D[1]); return [D[1] / l, -D[0] / l]; })();   // points to the upper-right half
  const cutEdge = (
    <svg width="100%" height="100%" viewBox="0 0 831 889" style={{ position: 'absolute', inset: 0 }}>
      <line x1={SW_TL[0] + D[0] * 0.03} y1={SW_TL[1] + D[1] * 0.03} x2={SW_BR[0] - D[0] * 0.03} y2={SW_BR[1] - D[1] * 0.03} stroke="#A8662A" strokeWidth={44} />
    </svg>
  );

  return (
    <AbsoluteFill style={{ background: '#2A2420', overflow: 'hidden', perspective: P, perspectiveOrigin: '50% 50%' }}>
      <div style={{ position: 'absolute', left: 960, top: 540, transformStyle: 'preserve-3d',
        transform: `translate3d(0px, 0px, ${cam.z}px) rotateZ(${cam.r}deg) translate3d(${-cam.x}px, ${-cam.y}px, 0px)` }}>
        {/* the counter and the board */}
        <div style={{ position: 'absolute', left: 0, top: 0, transform: `translate3d(${-BG_W / 2 - BOARD_C.x}px, ${-BG_H / 2 - BOARD_C.y}px, ${Z_TABLE}px)` }}>
          <Img src={img('board')} style={{ width: BG_W, height: BG_H }} />
        </div>
        {/* the jar (open) and its lid */}
        <Layer l={{ x: JAR.x, y: JAR.y, z: Z_OBJ, w: JAR_W, src: 'jar', ar: 880 / 913 }} />
        <Layer l={{ x: mix(lid, JAR.x, LID_SPOT.x), y: mix(lid, JAR.y, LID_SPOT.y), z: Z_OBJ + 12 + Math.sin(lid * Math.PI) * 420, w: LID_W, src: 'lid', ar: 648 / 656, r: lid * 160 }} />
        {/* slice A with the peanut butter appearing under the blade */}
        {!landed && f >= at(K.two) - 8 ? (
          <Layer l={{ x: A.x, y: A.y, z: Z_OBJ + hA, w: SLICE_W, src: 'bread_a', ar: 732 / 865, s: sqA, r: (1 - Math.min(1, dA)) * -18 }}>
            <svg width="100%" height="100%" viewBox={`${-SLICE_W / 2} ${-sliceH / 2} ${SLICE_W} ${sliceH}`} style={{ position: 'absolute', inset: 0, overflow: 'visible' }}>
              <defs>
                <filter id="pbsoft" x="-20%" y="-20%" width="140%" height="140%"><feGaussianBlur stdDeviation="9" /></filter>
                <mask id="pbmask" maskUnits="userSpaceOnUse" x={-400} y={-400} width={800} height={800}>
                  {fullPB ? <rect x={-400} y={-400} width={800} height={800} fill="#fff" /> : (
                    <g filter="url(#pbsoft)">{passesDone.map((p, i) => <rect key={i} x={p.x0} y={p.y - 62} width={p.x1 - p.x0} height={124} rx={60} fill="#fff" />)}</g>
                  )}
                </mask>
              </defs>
              <image href={img('bread_a')} x={-SLICE_W / 2} y={-sliceH / 2} width={SLICE_W} height={sliceH} />
              {f >= at(K.spread) ? (
                <image href={img('pb_layer')} x={-pbLayerW / 2} y={-pbLayerH / 2 + 22} width={pbLayerW} height={pbLayerH} mask="url(#pbmask)" />
              ) : null}
            </svg>
          </Layer>
        ) : null}
        {/* slice B: drops, then lifts, flips over and lands on A */}
        {!landed && f >= at(K.slices) - 8 ? (
          <Layer l={{ x: mix(over, B.x, A.x), y: mix(over, B.y, A.y), z: Z_OBJ + hB + up * 420 * (1 - down) + down * 26, w: SLICE_W, src: 'bread_b', ar: 736 / 892,
            s: sqB, r: (1 - Math.min(1, dB)) * 16, ry: over * 180 }} />
        ) : null}
        {/* the sandwich, then its two halves */}
        {landed && !cut ? <Layer l={{ x: A.x, y: A.y, z: Z_OBJ + 26, w: SW_W, src: 'sandwich', ar: 831 / 889, s: 1 + 0.03 * squash }} /> : null}
        {cut ? (
          <>
            <Layer l={{ x: A.x - nrm[0] * sep, y: A.y - nrm[1] * sep, z: Z_OBJ + 26, w: SW_W, src: 'sandwich', ar: 831 / 889, clip: HALF_LL, r: -3 * part }}>
              <Img src={img('sandwich')} style={{ width: '100%', height: '100%' }} />{cutEdge}
            </Layer>
            <Layer l={{ x: A.x + nrm[0] * sep, y: A.y + nrm[1] * sep, z: Z_OBJ + 26, w: SW_W, src: 'sandwich', ar: 831 / 889, clip: HALF_UR, r: 3 * part }}>
              <Img src={img('sandwich')} style={{ width: '100%', height: '100%' }} />{cutEdge}
            </Layer>
          </>
        ) : null}
        {/* the cut line appears behind the knife as it slices */}
        {cutK > 0 && !cut ? (
          <div style={{ position: 'absolute', left: 0, top: 0, transform: `translate3d(0px, 0px, ${Z_OBJ + 30}px)` }}>
            <svg width={2} height={2} style={{ overflow: 'visible' }}>
              <line x1={tl.x} y1={tl.y} x2={mix(clamp((cutK - 0.1) / 0.8), tl.x, br.x)} y2={mix(clamp((cutK - 0.1) / 0.8), tl.y, br.y)}
                stroke="#6E3A12" strokeWidth={7} strokeLinecap="round" opacity={0.85} />
            </svg>
          </div>
        ) : null}
        {/* the knife */}
        {knife.show ? <Layer l={{ x: kk.x, y: kk.y, z: knife.z, w: KNIFE_W, src: knife.pb ? 'knife_pb' : 'knife', ar: kk.ar, r: kk.r }} /> : null}
        {/* the open jar's peanut butter covers the blade while it is down in the jar */}
        {f >= at(K.knife) - 8 && f < at(K.butter) + 8 ? (
          <div style={{ position: 'absolute', left: 0, top: 0, transform: `translate3d(${JAR.x}px, ${JAR.y}px, ${Z_OBJ + 22}px)` }}>
            <Img src={img('jar')} style={{ position: 'absolute', left: -JAR_W / 2, top: -(JAR_W * 913) / 880 / 2, width: JAR_W, height: (JAR_W * 913) / 880,
              clipPath: `circle(${(JAR_OPEN.r / 880) * 100}% at ${(JAR_OPEN.cx / 880) * 100}% ${(JAR_OPEN.cy / 913) * 100}%)` }} />
          </div>
        ) : null}
        {/* basil sprigs close to the camera, soft, sliding past */}
        {[{ x: -1250, y: -560, r: 30, s: 1.0 }, { x: 1150, y: 520, r: -140, s: 1.15 }].map((b, i) => (
          <div key={i} style={{ position: 'absolute', left: 0, top: 0, transform: `translate3d(${b.x + cam.x * 0.6}px, ${b.y + cam.y * 0.6}px, ${Z_FG}px) rotateZ(${b.r}deg) scale(${b.s})` }}>
            <Img src={img('basil')} style={{ position: 'absolute', left: -440, top: -330, width: 880, filter: 'blur(9px)', opacity: 0.95 }} />
          </div>
        ))}
      </div>
      {/* warm morning light and a soft vignette */}
      <AbsoluteFill style={{ background: 'radial-gradient(ellipse at 22% 18%, rgba(255,220,160,0.20), rgba(255,220,160,0) 55%)', mixBlendMode: 'screen' }} />
      <AbsoluteFill style={{ background: 'radial-gradient(ellipse at 50% 50%, rgba(0,0,0,0) 60%, rgba(25,15,5,0.42) 100%)' }} />
      <Soundtrack sfx={SFX} />
    </AbsoluteFill>
  );
};

const SFX: Sfx[] = [
  { at: at(K.two) + 2, file: 'card.wav', vol: 0.35 }, { at: at(K.slices) + 2, file: 'card2.wav', vol: 0.35 },
  { at: at(K.then), file: 'zip2.wav', vol: 0.25 }, { at: at(K.dig) + 10, file: 'bump2.wav', vol: 0.3 },
  { at: at(K.knife) - 8, file: 'swish2.wav', vol: 0.25 }, { at: at(K.into), file: 'smack.wav', vol: 0.3 }, { at: at(K.butter) - 2, file: 'pop2.wav', vol: 0.25 },
  { at: STEPS.spread.from - 6, file: 'swipe1.wav', vol: 0.2 }, { at: at(K.spread), file: 'paper.wav', vol: 0.3, dur: 40 },
  { at: at(K.press) - 2, file: 'whoosh.wav', vol: 0.3 }, { at: at(K.top) - 1, file: 'thud.wav', vol: 0.4 },
  { at: at(K.cut), file: 'zip1.wav', vol: 0.35 }, { at: at(K.corner2) + 6, file: 'crack.wav', vol: 0.3 },
  { at: STEPS.payoff.from, file: 'whoosh.wav', vol: 0.2 }, { at: at(K.better), file: 'sparkle.wav', vol: 0.2 },
];
