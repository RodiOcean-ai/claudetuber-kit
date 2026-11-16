// Style 8: COLLAGE. Vintage magazine photos (made on the free local picture maker) cut out with a white paper border,
// on brown kraft paper. Everything moves in jerky paper-animation steps (12 a second, a little wobble each step), pieces
// are held down with masking tape, each step gets a ransom-note headline glued on a torn paper strip, the peanut butter
// is a torn brown paper shape that grows, and the scissors cut along a dashed "cut here" line from corner to corner.
import React from 'react';
import { AbsoluteFill, Img, staticFile, useCurrentFrame } from 'remotion';
import { Soundtrack, Sfx } from '../../shared/Soundtrack';
import { ensureFonts } from '../../shared/fonts';
import { K, STEPS, at } from '../../shared/timing';
import { clamp, mix, rand } from '../../shared/anim';

ensureFonts('Anton', 'Bebas Neue', 'Abril Fatface', 'Courier Prime', 'Bangers', 'Permanent Marker', 'Rubik', 'Instrument Serif');

const STEP = 2.5; // 12 poses a second
const img = (n: string) => staticFile(`img/collage/${n}.png`);

// ---------- ransom-note letters ----------
const FONTS = ['Anton', 'Bebas Neue', 'Abril Fatface', 'Courier Prime', 'Bangers', 'Rubik', 'Instrument Serif', 'Permanent Marker'];
const PAPERS = [['#FFFFFF', '#111111'], ['#111111', '#FFFFFF'], ['#F2D64B', '#111111'], ['#D9382F', '#FFFFFF'], ['#EFE6D2', '#3A2A1A'], ['#2E6FB5', '#FFFFFF'], ['#FFFFFF', '#D9382F']];
const Ransom: React.FC<{ text: string; size: number; seed: number; wide?: number }> = ({ text, size, seed, wide = 9 }) => (
  <div style={{ display: 'flex', flexWrap: 'wrap', justifyContent: 'center', gap: size * 0.08, rowGap: size * 0.12, maxWidth: size * wide }}>
    {text.split(' ').map((word, wi) => (
      <div key={wi} style={{ display: 'flex', gap: size * 0.04, marginRight: size * 0.42 }}>
        {word.split('').map((ch, i) => {
          const r = (k: number) => rand(seed * 97 + wi * 31 + i * 7 + k);
          const [bg, fg] = PAPERS[Math.floor(r(1) * PAPERS.length)];
          const font = FONTS[Math.floor(r(2) * FONTS.length)];
          return (
            <span key={i} style={{ display: 'inline-block', fontFamily: font, fontSize: size * (0.85 + r(3) * 0.35), lineHeight: 1, color: fg, background: bg,
              padding: `${size * 0.06}px ${size * 0.1}px`, transform: `rotate(${(r(4) - 0.5) * 14}deg) translateY(${(r(5) - 0.5) * size * 0.15}px)`,
              boxShadow: '2px 3px 0 rgba(0,0,0,0.25)', fontWeight: font === 'Rubik' ? 900 : 400, textTransform: 'uppercase' }}>{ch}</span>
          );
        })}
      </div>
    ))}
  </div>
);

// one headline per step, glued on a torn white strip, slapped on and later torn away
const HEADLINES: [number, number, string][] = [
  [at(K.two) - 4, STEPS.knife.from, 'two slices'], [at(K.dig) - 4, STEPS.spread.from, 'dig in'], [at(K.spread) - 2, STEPS.press.from, 'to the edges'],
  [at(K.press) - 2, STEPS.cut.from, 'press'], [at(K.corner1) - 4, STEPS.payoff.from, 'corner to corner'], [at(K.triangles) - 4, 999, 'triangles taste better'],
];

// a torn-paper outline (jagged polygon) for the peanut butter
const tornBlob = (r: number, seed: number, n = 46) => Array.from({ length: n }).map((_, i) => {
  const a = (i / n) * Math.PI * 2, j = 1 + (rand(seed + i * 1.7) - 0.5) * 0.12;
  return `${Math.cos(a) * r * 1.05 * j},${Math.sin(a) * r * 0.95 * j}`;
}).join(' ');

export const Collage: React.FC = () => {
  const frame = useCurrentFrame();
  const pose = Math.floor(frame / STEP);
  const f = pose * STEP; // everything moves in steps
  const jig = (seed: number, amt = 1) => ({ x: (rand(pose * 3.1 + seed) - 0.5) * 6 * amt, y: (rand(pose * 5.7 + seed) - 0.5) * 6 * amt, r: (rand(pose * 7.3 + seed) - 0.5) * 1.6 * amt });
  const p = (a: number, b: number) => clamp((f - a) / (b - a)); // stepped progress, no easing

  // positions (screen px)
  const A = { x: 760, y: 640 }, B = { x: 1170, y: 640 };
  const inA = p(at(K.two) - 8, at(K.two) + 4), inB = p(at(K.slices) - 8, at(K.slices) + 4);
  const jarIn = p(at(K.dig) - 6, at(K.dig) + 4), jarOut = p(STEPS.spread.from + 6, STEPS.spread.from + 16);
  const handIn = p(at(K.knife) - 6, at(K.knife) + 4);
  const dig = p(at(K.into), at(K.peanut) + 2), lift = p(at(K.butter), at(K.butter) + 8);
  const toA = p(STEPS.spread.from - 4, at(K.spread) + 2);
  const spread = p(at(K.spread), at(K.edges) + 4);
  const handOut = p(at(K.edges) + 6, at(K.edges) + 16);
  const pbSize = [0, 0.3, 0.45, 0.6, 0.75, 0.88, 1][Math.min(6, Math.floor(spread * 6.99))];
  const up = p(at(K.press) - 2, at(K.second) + 4), flip = p(at(K.second), at(K.on) + 2), down = p(at(K.on) + 2, at(K.top));
  const squash = f >= at(K.top) && f < at(K.top) + 6 ? 0.9 : 1;
  const tape = f >= at(K.top) + 2;
  const cutLine = p(at(K.corner1) - 2, at(K.corner2) + 4);
  const split = p(at(K.corner2) + 6, at(K.corner2) + 16);
  const pay = p(STEPS.payoff.from, STEPS.payoff.from + 16);

  // the hand (cut from a vintage photo; it reaches in from the left) is placed by its knife tip and turned about it
  const J = { x: 330, y: 430 };            // the jar's mouth
  const zig = Math.sin(Math.floor(spread * 10) / 10 * Math.PI * 5);
  const tip = {
    x: mix(handOut, mix(toA, mix(handIn, -420, J.x + 10), A.x - 60 + zig * 90), -700),
    y: mix(handOut, mix(toA, mix(handIn, 160, J.y + 70) + dig * 120 - lift * 150, A.y - 20), 120),
    r: mix(toA, 96, 62 + zig * 6),
  };
  const showHand = f >= at(K.knife) - 6 && handOut < 1;
  const digging = f >= at(K.knife) - 6 && f < at(K.butter) + 6;
  const glob = f >= at(K.butter) && spread < 0.5;
  const HAND = { w: 1141, h: 810, tx: 1106, ty: 34, s: 0.6 };

  // the sandwich group (A + peanut butter + B + tape), later split into two triangles
  const BOX = 430;
  const bx = mix(down, mix(up, B.x, 980), A.x + 10), by = mix(down, mix(up, B.y, 420), A.y - 14);
  const bFlipX = flip < 0.5 ? 1 - flip * 2 : (flip - 0.5) * 2; // 1 -> 0 -> 1 (the paper turns over)
  // the top-down sandwich picture (998 x 1011, contained in the BOX): its true corners for the corner-to-corner cut
  const SWK = BOX / 1011, SWX = (BOX - 998 * SWK) / 2;
  const TL = { x: SWX + 132 * SWK, y: 128 * SWK }, BR = { x: SWX + 907 * SWK, y: 941 * SWK };
  const pc = (x: number, y: number) => `${(x / BOX) * 100}% ${(y / BOX) * 100}%`;
  const DX = BR.x - TL.x, DY = BR.y - TL.y;
  const HALF_UR = `polygon(${pc(TL.x - DX, TL.y - DY)}, ${pc(BR.x + DX, BR.y + DY)}, ${pc(BOX * 4, -BOX * 4)})`;
  const HALF_LL = `polygon(${pc(TL.x - DX, TL.y - DY)}, ${pc(BR.x + DX, BR.y + DY)}, ${pc(-BOX * 4, BOX * 4)})`;
  const NRM = (() => { const l = Math.hypot(DX, DY); return { x: DY / l, y: -DX / l }; })(); // towards the upper-right half
  const landedOnA = f >= at(K.on) + 2;
  const Sandwich: React.FC<{ part?: 'ur' | 'll' }> = ({ part }) => (
    <div style={{ position: 'absolute', left: -BOX / 2, top: -BOX / 2, width: BOX, height: BOX, clipPath: part === 'ur' ? HALF_UR : part === 'll' ? HALF_LL : undefined }}>
      {!landedOnA ? (
        <>
          <Img src={img('vt_bread_a_border')} style={{ position: 'absolute', inset: 0, width: '100%', height: '100%', objectFit: 'contain' }} />
          {pbSize > 0 ? (
            <svg width={BOX} height={BOX} viewBox={`${-BOX / 2} ${-BOX / 2} ${BOX} ${BOX}`} style={{ position: 'absolute', inset: 0 }}>
              <defs><clipPath id="pbtorn"><polygon points={tornBlob(205 * pbSize, Math.floor(pbSize * 10))} transform="translate(0 14)" /></clipPath></defs>
              <image href={img('vt_pb_layer')} x={-150} y={-160} width={300} height={346} clipPath="url(#pbtorn)" />
              <polygon points={tornBlob(205 * pbSize, Math.floor(pbSize * 10))} transform="translate(0 14)" fill="none" stroke="#FFF8EA" strokeWidth={pbSize < 1 ? 5 : 0} />
            </svg>
          ) : null}
        </>
      ) : (
        <Img src={img('vt_sandwich_border')} style={{ position: 'absolute', inset: 0, width: '100%', height: '100%', objectFit: 'contain', transform: `scale(1, ${squash})` }} />
      )}
      {part ? (
        <svg width={BOX} height={BOX} style={{ position: 'absolute', inset: 0 }}>
          <line x1={TL.x + DX * 0.04} y1={TL.y + DY * 0.04} x2={BR.x - DX * 0.04} y2={BR.y - DY * 0.04} stroke="#B06F2D" strokeWidth={22} />
        </svg>
      ) : null}
      {tape && !part ? (
        <>
          <Img src={img('tape_1')} style={{ position: 'absolute', left: -30, top: 150, width: 150, transform: 'rotate(-12deg)' }} />
          <Img src={img('tape_2')} style={{ position: 'absolute', right: -30, top: 170, width: 150, transform: 'rotate(10deg)' }} />
        </>
      ) : null}
    </div>
  );

  const jA = jig(1), jB = jig(2), jJ = jig(3), jH = jig(4, 1.4), jS = jig(5);
  const sep = 46 * split + 20 * pay;

  return (
    <AbsoluteFill style={{ overflow: 'hidden', background: '#B98A55' }}>
      <Img src={img('kraft')} style={{ position: 'absolute', inset: 0, width: '100%', height: '100%', objectFit: 'cover' }} />
      {/* a few scraps already glued on the page */}
      <Img src={img('paper_white')} style={{ position: 'absolute', left: -120, top: 860, width: 760, transform: 'rotate(-6deg)', opacity: 0.95 }} />
      <Img src={img('paper_white')} style={{ position: 'absolute', right: -160, top: 40, width: 640, transform: 'rotate(7deg) scaleX(-1)', opacity: 0.95 }} />

      {/* the plate for the payoff */}
      {f >= STEPS.payoff.from ? (
        <Img src={img('v_plate_border')} style={{ position: 'absolute', left: A.x + 10 - 340, top: A.y - 340, width: 680, transform: `translate(${mix(pay, 1300, 0)}px, 0) rotate(${-4 + jS.r}deg)`, zIndex: 1 }} />
      ) : null}

      {/* slice A (and the sandwich built on it) */}
      {f >= at(K.two) - 8 ? (
        split <= 0 ? (
          <div style={{ position: 'absolute', left: mix(inA, -400, A.x) + jA.x, top: A.y + jA.y, transform: `rotate(${mix(inA, -30, -4) + jA.r}deg)` }}><Sandwich /></div>
        ) : (
          <>
            <div style={{ position: 'absolute', left: A.x + 10 - NRM.x * sep + jA.x, top: A.y - NRM.y * sep + jA.y, transform: `rotate(${-4 - 6 * split + jA.r}deg)`, zIndex: 4 }}><Sandwich part="ll" /></div>
            <div style={{ position: 'absolute', left: A.x + 10 + NRM.x * sep + jB.x, top: A.y + NRM.y * sep + jB.y, transform: `rotate(${-4 + 6 * split + jB.r}deg)`, zIndex: 4 }}><Sandwich part="ur" /></div>
          </>
        )
      ) : null}
      {/* slice B until it lands on A */}
      {f >= at(K.slices) - 8 && f < at(K.on) + 2 ? (
        <div style={{ position: 'absolute', left: mix(inB, 2300, bx) + jB.x, top: by + jB.y, transform: `rotate(${mix(inB, 25, 5) + jB.r}deg) scaleX(${Math.max(0.05, bFlipX)})` }}>
          <Img src={img('vt_bread_b_border')} style={{ position: 'absolute', left: -BOX / 2, top: -BOX / 2, width: BOX, height: BOX, objectFit: 'contain' }} />
        </div>
      ) : null}
      {/* the jar */}
      {f >= at(K.dig) - 6 && jarOut < 1 ? (
        <Img src={img('v_jar_border')} style={{ position: 'absolute', left: mix(jarOut, mix(jarIn, -500, J.x), -600) + jJ.x - 190, top: J.y - 34 + jJ.y, width: 380,
          transform: `rotate(${-4 + jJ.r}deg)`, zIndex: 3 }} />
      ) : null}
      {/* the jar's front (below the peanut-butter surface) drawn over the hand while it digs: the blade goes INTO the jar */}
      {digging && jarOut < 1 ? (
        <Img src={img('v_jar_border')} style={{ position: 'absolute', left: mix(jarIn, -500, J.x) + jJ.x - 190, top: J.y - 34 + jJ.y, width: 380,
          transform: `rotate(${-4 + jJ.r}deg)`, zIndex: 6, clipPath: 'inset(36% 0 0 0)' }} />
      ) : null}
      {/* the hand with the knife, placed by its tip */}
      {showHand ? (
        <Img src={img('v_hand_border')} style={{ position: 'absolute', left: tip.x - HAND.tx * HAND.s + jH.x, top: tip.y - HAND.ty * HAND.s + jH.y,
          width: HAND.w * HAND.s, transformOrigin: `${HAND.tx * HAND.s}px ${HAND.ty * HAND.s}px`, transform: `rotate(${tip.r + jH.r}deg)`, zIndex: 5 }} />
      ) : null}
      {showHand && glob ? (
        <svg width={110} height={90} viewBox="-55 -45 110 90" style={{ position: 'absolute', left: tip.x - 55 + jH.x, top: tip.y - 45 + jH.y, zIndex: 7 }}>
          <defs><clipPath id="dollop"><polygon points={tornBlob(34, 5, 24)} /></clipPath></defs>
          <image href={img('vt_pb_layer')} x={-60} y={-60} width={120} height={140} preserveAspectRatio="xMidYMid slice" clipPath="url(#dollop)" />
          <polygon points={tornBlob(34, 5, 24)} fill="none" stroke="#FFF8EA" strokeWidth={5} />
        </svg>
      ) : null}
      {/* "cut here": a dashed line corner to corner with the scissors travelling along it */}
      {cutLine > 0 && split < 1 ? (() => {
        const ox = A.x + 10 - BOX / 2, oy = A.y - BOX / 2;
        const x0 = ox + TL.x - DX * 0.08, y0 = oy + TL.y - DY * 0.08, x1 = ox + BR.x + DX * 0.06, y1 = oy + BR.y + DY * 0.06;
        const t = cutLine;
        return (
          <svg width={1920} height={1080} style={{ position: 'absolute', inset: 0, overflow: 'visible' }}>
            <line x1={x0} y1={y0} x2={x1} y2={y1} stroke="#111" strokeWidth={6} strokeDasharray="18 14" opacity={1 - split} />
            <g transform={`translate(${mix(t, x0, x1)} ${mix(t, y0, y1)}) rotate(${45 + (pose % 2) * 14}) scale(2)`} opacity={1 - split}>
              <circle cx={-34} cy={-16} r={16} fill="none" stroke="#D9382F" strokeWidth={9} /><circle cx={-34} cy={16} r={16} fill="none" stroke="#D9382F" strokeWidth={9} />
              <path d="M -20 -10 L 40 6 M -20 10 L 40 -6" stroke="#C9CFD6" strokeWidth={10} strokeLinecap="round" />
              <circle cx={-4} cy={0} r={4} fill="#333" />
            </g>
          </svg>
        );
      })() : null}
      {/* the headline strip for the current step */}
      {HEADLINES.map(([a, b, text], i) => {
        if (f < a || f >= b + 6) return null;
        const slap = f < a + 5 ? 1.12 : 1;
        const tear = f >= b ? (f - b) / 6 : 0;
        return (
          <div key={i} style={{ position: 'absolute', left: 960, top: (i === 5 ? 170 : 150) - tear * 260, transform: `translate(-50%, -50%) rotate(${(rand(i * 13) - 0.5) * 6 + jig(9 + i).r}deg) scale(${slap})` }}>
            <div style={{ position: 'relative', padding: '26px 54px', background: '#FBF7EE', boxShadow: '4px 6px 0 rgba(0,0,0,0.25)',
              clipPath: 'polygon(0 6%, 4% 0, 12% 5%, 20% 0, 30% 4%, 41% 0, 52% 5%, 63% 0, 74% 4%, 85% 0, 94% 5%, 100% 1%, 99% 94%, 92% 100%, 81% 95%, 70% 100%, 59% 96%, 47% 100%, 36% 95%, 25% 100%, 14% 96%, 4% 100%, 0 94%)' }}>
              <Ransom text={text} size={i === 5 ? 66 : 84} seed={i + 1} wide={i === 5 ? 15 : 9} />
            </div>
          </div>
        );
      })}
      {/* sticker stars at the end */}
      {f >= at(K.better) ? [[420, 360], [1500, 420], [1340, 820]].map(([x, y], i) => (
        f >= at(K.better) + i * 5 ? (
          <svg key={i} width={140} height={140} viewBox="-70 -70 140 140" style={{ position: 'absolute', left: x - 70, top: y - 70, transform: `rotate(${(rand(i + 40) - 0.5) * 40}deg)` }}>
            <path d="M 0 -60 L 16 -18 L 60 -18 L 24 8 L 38 52 L 0 26 L -38 52 L -24 8 L -60 -18 L -16 -18 Z" fill="#F2D64B" stroke="#FFFFFF" strokeWidth={8} />
          </svg>
        ) : null
      )) : null}
      {/* paper grain over everything */}
      <AbsoluteFill style={{ backgroundImage: 'radial-gradient(rgba(60,35,10,.10) 1px, transparent 1.4px)', backgroundSize: '6px 6px', mixBlendMode: 'multiply', pointerEvents: 'none' }} />
      <Soundtrack sfx={SFX} />
    </AbsoluteFill>
  );
};

const SFX: Sfx[] = [
  ...HEADLINES.map(([a]) => ({ at: a, file: 'paper.wav', vol: 0.3, dur: 18 })),
  { at: at(K.two), file: 'card.wav', vol: 0.3 }, { at: at(K.slices), file: 'card2.wav', vol: 0.3 },
  { at: at(K.dig) - 2, file: 'page.wav', vol: 0.3 }, { at: at(K.knife), file: 'swish2.wav', vol: 0.3 }, { at: at(K.into) + 2, file: 'smack.wav', vol: 0.25 },
  { at: at(K.spread), file: 'paper.wav', vol: 0.3, dur: 40 }, { at: at(K.second), file: 'page.wav', vol: 0.3 }, { at: at(K.top), file: 'thud.wav', vol: 0.35 },
  { at: at(K.top) + 2, file: 'zip2.wav', vol: 0.3 }, { at: at(K.corner1) - 2, file: 'zip1.wav', vol: 0.3 }, { at: at(K.corner2) + 6, file: 'crack.wav', vol: 0.3 },
  { at: STEPS.payoff.from, file: 'card.wav', vol: 0.25 }, { at: at(K.better), file: 'sparkle.wav', vol: 0.2 },
];
