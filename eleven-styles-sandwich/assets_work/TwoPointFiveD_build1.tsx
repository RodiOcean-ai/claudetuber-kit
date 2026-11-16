// Style 7: 2.5D. Flat photo layers (made on the free local picture maker: a kitchen plate and cut-out objects) placed at
// different depths in a 3D space and filmed with a slowly moving camera, so near things slide past far things
// (parallax). The far kitchen is soft, a herb plant drifts past in the blurred foreground, the objects on the board
// move with soft shadows, and the camera pushes in for the payoff.
import React from 'react';
import { AbsoluteFill, Easing, Img, staticFile, useCurrentFrame } from 'remotion';
import { Soundtrack, Sfx } from '../../shared/Soundtrack';
import { K, STEPS, at } from '../../shared/timing';
import { clamp, easeInOut, mix, pop, prog } from '../../shared/anim';

const img = (n: string) => staticFile(`img/p25/${n}.png`);
const P = 1500;                 // perspective (px)
const Z_BG = -1100, Z_IT = -500, Z_FG = 520;
const BG_W = 3600, BG_H = (3600 * 928) / 1664;
// the empty cutting board in the kitchen picture (picture px of 1664 x 928): its centre and size, measured by eye
const BOARD = { x: 840, y: 606, w: 1180 }; // bg-2 of 3
// board centre in item-layer world px (so items at Z_IT sit on the board when the camera is at rest)
const onBoard = (dx: number, dy: number) => {
  const k = (P - Z_IT) / (P - Z_BG);
  return { x: ((BOARD.x / 1664 - 0.5) * BG_W) * k + dx, y: ((BOARD.y / 928 - 0.5) * BG_H) * k + dy };
};
const SIZE = 420; // item size in world px at the item layer

type Item = { src: string; x: number; y: number; z?: number; s?: number; r?: number; o?: number; rx?: number; mask?: string; shadow?: number };
const Layer: React.FC<{ it: Item }> = ({ it }) => (
  <div style={{ position: 'absolute', left: 0, top: 0, transformStyle: 'preserve-3d',
    transform: `translate3d(${it.x}px, ${it.y}px, ${it.z ?? Z_IT}px) rotateX(${it.rx ?? 0}deg) rotateZ(${it.r ?? 0}deg) scale(${it.s ?? 1})`, opacity: it.o ?? 1 }}>
    {it.shadow ? (
      <div style={{ position: 'absolute', left: -SIZE * 0.42, top: SIZE * 0.18, width: SIZE * 0.84, height: SIZE * 0.22, borderRadius: '50%',
        background: 'rgba(60,35,15,0.38)', filter: 'blur(14px)', opacity: it.shadow, transform: 'translateZ(-1px)' }} />
    ) : null}
    <Img src={img(it.src)} style={{ position: 'absolute', left: -SIZE / 2, top: -SIZE / 2, width: SIZE, height: SIZE, objectFit: 'contain',
      WebkitMaskImage: it.mask, maskImage: it.mask }} />
  </div>
);

export const TwoPointFiveD: React.FC = () => {
  const f = useCurrentFrame();
  // camera: always moving (a slow dolly in with a sideways drift), a bigger push at the payoff
  const push = prog(f, 0, 450, (t) => t);
  const pay = prog(f, STEPS.payoff.from - 6, STEPS.payoff.from + 40, easeInOut);
  const camZ = mix(push, 0, 260) + pay * 260;
  // the payoff push centres the camera on the sandwich (A is defined below, so compute it here too)
  const Ac = onBoard(-175, 30);
  const camX = mix(pay, mix(push, -90, 70), Ac.x);
  const camY = mix(pay, mix(push, -20, 10), Ac.y - 40);
  const camRY = mix(push, 2.2, -1.6);

  const A = onBoard(-175, 30), B = onBoard(175, 30), J = onBoard(530, -165);
  // step 1: slices fall onto the board
  const dA = pop(f, at(K.two) - 6, { damping: 13, stiffness: 140 }), dB = pop(f, at(K.slices) - 6, { damping: 13, stiffness: 140 });
  const fallA = Math.min(1, dA), fallB = Math.min(1, dB);
  // step 2: jar slides in, lid comes off, knife dips in and comes out loaded
  const jarIn = prog(f, at(K.dig) - 8, at(K.dig) + 4, Easing.out(Easing.cubic));
  const jarOut = prog(f, STEPS.spread.from + 8, STEPS.spread.from + 22, Easing.in(Easing.cubic));
  const lid = prog(f, at(K.dig) + 2, at(K.knife) + 4, easeInOut);
  const kIn = prog(f, at(K.knife) - 6, at(K.into) + 2, Easing.out(Easing.cubic));
  const dip = prog(f, at(K.into), at(K.peanut) + 2, easeInOut);
  const kOut = prog(f, at(K.butter) - 2, at(K.butter) + 12, easeInOut);
  // step 3: spreading (the peanut-butter slice is revealed around the knife)
  const go = prog(f, STEPS.spread.from - 6, at(K.spread) + 2, easeInOut);
  const sT = prog(f, at(K.spread), at(K.edges) + 6, (t) => t);
  const pb = prog(f, at(K.spread), at(K.edges) + 6, Easing.inOut(Easing.quad));
  const kAway = prog(f, at(K.edges) + 8, at(K.edges) + 22, Easing.in(Easing.cubic));
  // step 4: the second slice lifts toward the camera, turns over and lands on the first
  const up = prog(f, at(K.press) - 2, at(K.second) + 6, easeInOut);
  const over = prog(f, at(K.second) - 2, at(K.on) + 2, easeInOut);
  const down = prog(f, at(K.on) - 2, at(K.top) - 1, Easing.in(Easing.quad));
  const landed = f >= at(K.top) - 1;
  const squash = landed ? Math.sin(clamp((f - at(K.top) + 1) / 9) * Math.PI) * Math.exp(-(f - at(K.top) + 1) / 12) : 0;
  // step 5: the knife slices corner to corner, then the halves part
  const cutK = prog(f, at(K.cut) - 4, at(K.corner2) + 4, easeInOut);
  const split = prog(f, at(K.corner2) + 6, at(K.corner2) + 20, Easing.out(Easing.back(1.3)));
  const cut = f >= at(K.corner2) + 6;

  // knife position (item-layer world px)
  let kx = J.x - 20, ky = J.y - mix(kIn, 560, 175) + dip * 85 - kOut * 175, kr = -45, kSrc = f >= at(K.butter) ? 'c_knife_pb' : 'c_knife';
  if (f >= STEPS.spread.from - 6) {
    const zig = Math.sin(sT * Math.PI * 6);
    kx = mix(go, J.x + 10, A.x + 40 + zig * 70) + kAway * 900;
    ky = mix(go, J.y - 160, A.y - 30 + mix(sT, -40, 40)) - kAway * 300;
    kr = mix(go, 0, -28 + zig * 10);
    kSrc = pb < 0.6 ? 'c_knife_pb' : 'c_knife';
  }
  if (cutK > 0 && !cut) {
    kSrc = 'c_knife';
    kx = A.x + mix(cutK, 330, -170); ky = A.y + mix(cutK, -300, 140); kr = 0;
  }
  const showKnife = (f >= at(K.knife) - 6 && kAway < 1) || (cutK > 0 && !cut);
  // mask that reveals the spread slice around where the knife has been
  const pbMask = `radial-gradient(circle at 50% 50%, #000 ${pb * 72}%, transparent ${pb * 72 + 8}%)`;
  const bx = mix(over, B.x, A.x), by = mix(over, B.y, A.y) - Math.sin(up * Math.PI * 0.5) * 120 * (1 - down);
  const bz = Z_IT + up * 260 * (1 - down);

  return (
    <AbsoluteFill style={{ background: '#2B1D12', overflow: 'hidden', perspective: P, perspectiveOrigin: '50% 45%' }}>
      <div style={{ position: 'absolute', left: 960, top: 540, transformStyle: 'preserve-3d',
        transform: `translate3d(${-camX}px, ${-camY}px, ${camZ}px) rotateY(${camRY}deg)` }}>
        {/* the kitchen, far and soft */}
        <div style={{ position: 'absolute', left: 0, top: 0, transform: `translate3d(${-BG_W / 2}px, ${-BG_H / 2}px, ${Z_BG}px)` }}>
          <Img src={img('bg_kitchen')} style={{ width: BG_W, height: BG_H, filter: 'blur(1.5px) saturate(1.05)' }} />
        </div>
        {/* the objects on the board */}
        {f >= at(K.two) - 6 && !landed ? <Layer it={{ src: pb > 0 ? 'c_bread' : 'c_bread', x: A.x, y: A.y - (1 - fallA) * 700, r: (1 - fallA) * -14, shadow: fallA }} /> : null}
        {pb > 0 && !landed ? <Layer it={{ src: 'c_slice_pb', x: A.x, y: A.y, mask: pbMask }} /> : null}
        {f >= at(K.slices) - 6 && !landed ? (
          <Layer it={{ src: 'c_bread2', x: bx, y: by - (1 - fallB) * 700, z: bz, r: (1 - fallB) * 12, rx: over * 180, shadow: fallB * (1 - up) }} />
        ) : null}
        {landed && !cut ? <Layer it={{ src: 'c_sandwich', x: A.x, y: A.y, s: 1 + 0.04 * squash, shadow: 1 }} /> : null}
        {cut ? <Layer it={{ src: 'c_halves', x: A.x, y: A.y - 6, s: 1.02 + 0.04 * split, o: clamp(split * 3), shadow: 1 }} /> : null}
        {f >= at(K.dig) - 8 && jarOut < 1 ? (
          <>
            <Layer it={{ src: 'c_jar', x: J.x + (1 - jarIn) * 900 + jarOut * 900, y: J.y, shadow: 1 }} />
            {lid < 1 || true ? <Layer it={{ src: 'c_lid', x: J.x + (1 - jarIn) * 900 + mix(lid, 0, 260) + jarOut * 900, y: J.y - mix(lid, 150, 40) - Math.sin(lid * Math.PI) * 160, z: Z_IT + 1, s: 0.55, r: lid * 200 }} /> : null}
          </>
        ) : null}
        {cutK > 0 && !cut ? (
          <div style={{ position: 'absolute', left: 0, top: 0, transform: `translate3d(${A.x}px, ${A.y}px, ${Z_IT + 1}px)` }}>
            <svg width={2} height={2} style={{ overflow: 'visible' }}>
              <line x1={150} y1={-118} x2={mix(cutK, 150, -150)} y2={mix(cutK, -118, 118)} stroke="#FFF6DD" strokeWidth={7} strokeLinecap="round" opacity={0.95} />
            </svg>
          </div>
        ) : null}
        {showKnife ? <Layer it={{ src: kSrc, x: kx, y: ky, z: Z_IT + 2, r: kr, s: 0.9,
          mask: f < STEPS.spread.from - 6 ? `linear-gradient(${-kr}deg, #000 0%, #000 ${mix(dip, 100, 62) - kOut * 40}%, transparent ${mix(dip, 100, 62) - kOut * 40 + 1}%)` : undefined }} /> : null}
        {/* a herb plant drifts past in the blurred foreground */}
        <div style={{ position: 'absolute', left: 0, top: 0, transform: `translate3d(${-1100 + push * 160}px, ${120}px, ${Z_FG}px)` }}>
          <Img src={img('fg_herb')} style={{ width: 760, filter: 'blur(9px)' }} />
        </div>
      </div>
      {/* warm light and a soft vignette */}
      <AbsoluteFill style={{ background: 'radial-gradient(ellipse at 30% 20%, rgba(255,214,150,0.22), rgba(255,214,150,0) 55%)', mixBlendMode: 'screen' }} />
      <AbsoluteFill style={{ background: 'radial-gradient(ellipse at 50% 50%, rgba(0,0,0,0) 58%, rgba(30,15,5,0.4) 100%)' }} />
      <Soundtrack sfx={SFX} />
    </AbsoluteFill>
  );
};

const SFX: Sfx[] = [
  { at: at(K.two) + 2, file: 'card.wav', vol: 0.35 }, { at: at(K.slices) + 2, file: 'card2.wav', vol: 0.35 },
  { at: at(K.dig) - 6, file: 'swipe1.wav', vol: 0.25 }, { at: at(K.dig) + 2, file: 'zip2.wav', vol: 0.25 },
  { at: at(K.into) + 2, file: 'smack.wav', vol: 0.25 }, { at: at(K.butter), file: 'pop2.wav', vol: 0.25 },
  { at: at(K.spread), file: 'paper.wav', vol: 0.3, dur: 40 }, { at: at(K.second) - 2, file: 'whoosh.wav', vol: 0.3 },
  { at: at(K.top) - 1, file: 'thud.wav', vol: 0.4 }, { at: at(K.corner1), file: 'zip1.wav', vol: 0.35 },
  { at: at(K.corner2) + 6, file: 'crack.wav', vol: 0.3 }, { at: STEPS.payoff.from, file: 'whoosh.wav', vol: 0.25 }, { at: at(K.better), file: 'sparkle.wav', vol: 0.2 },
];
