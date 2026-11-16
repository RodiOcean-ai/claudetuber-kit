// Style 2: MOTION GRAPHICS. Flat vector shapes on the RodiOcean "Clean ocean" board (white dotted paper, ink #0B2540,
// one blue accent, Inter + JetBrains Mono), everything lands on its word: a step title with a highlighter sweep, step chips
// that fill, a counter that rolls (x2), a coverage meter that rolls to 100 % on "edges", a dashed corner-to-corner cut
// line, and a star-rating card for the payoff ("triangles taste better").
import React from 'react';
import { AbsoluteFill, Easing, interpolate, useCurrentFrame } from 'remotion';
import { Soundtrack, Sfx } from '../../shared/Soundtrack';
import { ensureFonts } from '../../shared/fonts';
import { K, STEPS, at } from '../../shared/timing';
import { backOut, clamp, easeInOut, easeOut, mix, pop, prog } from '../../shared/anim';

ensureFonts('Inter', 'JetBrains Mono', 'Instrument Serif');

const INK = '#0B2540', G2 = '#4A6C8A', DOT = '#C9E6F5', LINE = '#C9E6F5', WASH = '#ECF7FD', HI = '#CFF3FF';
const BLUE = '#0A84C6', BLUE_L = '#E6F7FF', CORAL = '#E11D48', MINT = '#059669';
const CRUMB = '#F6DFA4', CRUMB_D = '#EAC77F', CRUST = '#D9963F', CRUST_D = '#B8772A', PB = '#A65F2A', PB_L = '#C27A3E';
const STEEL = '#D6E0EA', STEEL_D = '#9FB3C8', HANDLE = '#0B2540';
const SANS = 'Inter', MONO = 'JetBrains Mono';

// ---------- shapes (drawn in a 300 x 300 box centred on 0,0) ----------
const slicePath = (w = 300, h = 300) => {
  const X = (u: number) => -w / 2 + u * w, Y = (v: number) => -h / 2 + v * h;
  return `M ${X(0.08)} ${Y(1)} L ${X(0.92)} ${Y(1)} Q ${X(1)} ${Y(1)} ${X(1)} ${Y(0.92)} L ${X(1)} ${Y(0.32)} ` +
    `C ${X(1.08)} ${Y(0.2)} ${X(1.05)} ${Y(0.01)} ${X(0.8)} ${Y(0.02)} C ${X(0.66)} ${Y(-0.04)} ${X(0.34)} ${Y(-0.04)} ${X(0.2)} ${Y(0.02)} ` +
    `C ${X(-0.05)} ${Y(0.01)} ${X(-0.08)} ${Y(0.2)} ${X(0)} ${Y(0.32)} L ${X(0)} ${Y(0.92)} Q ${X(0)} ${Y(1)} ${X(0.08)} ${Y(1)} Z`;
};
const OUTER = slicePath(300, 300), INNER = slicePath(258, 256), PBP = slicePath(244, 240);

const Slice: React.FC<{ id: string; pb?: number; pbCx?: number; pbCy?: number }> = ({ id, pb = 0, pbCx = 0, pbCy = 0 }) => (
  <g>
    <path d={OUTER} fill={CRUST} />
    <path d={OUTER} fill="none" stroke={CRUST_D} strokeWidth={4} opacity={0.5} />
    <path d={INNER} fill={CRUMB} transform="translate(0 6)" />
    {[[-60, -20, 9], [40, 30, 7], [-20, 60, 6], [70, -50, 5], [-80, 70, 5], [10, -70, 6]].map(([x, y, r], i) => (
      <ellipse key={i} cx={x} cy={y} rx={r} ry={r * 0.7} fill={CRUMB_D} opacity={0.8} />
    ))}
    {pb > 0 ? (
      <>
        <defs>
          <clipPath id={`pbclip-${id}`}><circle cx={pbCx} cy={pbCy} r={pb * 230} /></clipPath>
        </defs>
        <g clipPath={`url(#pbclip-${id})`} transform="translate(0 8)">
          <path d={PBP} fill={PB} />
          <path d="M -80 -40 C -30 -70 40 -60 80 -30 M -90 20 C -40 -5 30 0 85 30 M -70 75 C -20 55 40 60 75 85" fill="none" stroke={PB_L} strokeWidth={10} strokeLinecap="round" opacity={0.85} />
        </g>
      </>
    ) : null}
  </g>
);

// the jar: glass body, peanut butter inside (level can drop), a blue label, a lid that can fly off
const Jar: React.FC<{ level: number; lid: number }> = ({ level, lid }) => {
  const top = mix(level, 70, -60);
  return (
    <g>
      <rect x={-110} y={-120} width={220} height={250} rx={34} fill={BLUE_L} stroke={INK} strokeWidth={6} />
      <path d={`M -100 ${top} Q 0 ${top - 18} 100 ${top} L 100 96 Q 100 122 74 122 L -74 122 Q -100 122 -100 96 Z`} fill={PB} />
      <path d={`M -86 ${top + 10} Q -10 ${top - 6} 60 ${top + 8}`} stroke={PB_L} strokeWidth={8} fill="none" strokeLinecap="round" opacity={0.8} />
      <rect x={-110} y={-6} width={220} height={74} fill={BLUE} />
      <text x={0} y={42} textAnchor="middle" fontFamily={MONO} fontWeight={700} fontSize={30} fill="#fff" letterSpacing={2}>PEANUT</text>
      <rect x={-84} y={-136} width={168} height={22} rx={6} fill={INK} />
      <g transform={`translate(${lid * 230} ${-150 - lid * 140 + lid * lid * 160}) rotate(${lid * 210})`}>
        <rect x={-96} y={-30} width={192} height={44} rx={10} fill={CORAL} />
        {[-60, -30, 0, 30, 60].map((x) => <rect key={x} x={x - 3} y={-24} width={6} height={32} rx={3} fill="#fff" opacity={0.35} />)}
      </g>
    </g>
  );
};

// the knife: blade pointing down (0,0 = tip)
const Knife: React.FC<{ blob?: number }> = ({ blob = 0 }) => (
  <g>
    <path d="M -22 -230 L 22 -230 L 22 -40 Q 22 0 0 6 Q -22 0 -22 -40 Z" fill={STEEL} stroke={STEEL_D} strokeWidth={4} />
    <path d="M -8 -220 L -8 -40" stroke="#fff" strokeWidth={6} strokeLinecap="round" opacity={0.7} />
    <rect x={-28} y={-400} width={56} height={176} rx={22} fill={HANDLE} />
    <circle cx={0} cy={-370} r={7} fill={STEEL_D} /><circle cx={0} cy={-260} r={7} fill={STEEL_D} />
    {blob > 0 ? <ellipse cx={0} cy={-36} rx={30 * blob} ry={36 * blob} fill={PB} /> : null}
  </g>
);

const Star: React.FC<{ x: number; on: number; fill: string }> = ({ x, on, fill }) => {
  const p = clamp(on);
  return (
    <g transform={`translate(${x} 0)`}>
      <path d="M 0 -26 L 7.6 -8.4 L 26 -8 L 12 4 L 16.4 23 L 0 13 L -16.4 23 L -12 4 L -26 -8 L -7.6 -8.4 Z" fill="#D5DEE7" />
      <path transform={`scale(${p})`} opacity={p > 0 ? 1 : 0}
        d="M 0 -26 L 7.6 -8.4 L 26 -8 L 12 4 L 16.4 23 L 0 13 L -16.4 23 L -12 4 L -26 -8 L -7.6 -8.4 Z" fill={fill} />
    </g>
  );
};

// ---------- step text ----------
const TITLES: [number, string][] = [
  [at(K.take) - 2, 'Take 2 slices of bread'],
  [at(K.then) - 2, 'Dig a knife into the peanut butter'],
  [at(K.and1) - 2, 'Spread it right to the edges'],
  [at(K.press) - 2, 'Press the second slice on top'],
  [at(K.and2) - 2, 'Cut it corner to corner'],
  [at(K.because) - 2, 'Triangles taste better'],
];
const CHIPS = ['Bread', 'Knife', 'Spread', 'Press', 'Cut'];
const CHIP_AT = [STEPS.bread.from + 16, STEPS.knife.from, STEPS.spread.from, STEPS.press.from, STEPS.cut.from, STEPS.payoff.from];

const Title: React.FC<{ f: number }> = ({ f }) => {
  let i = -1;
  TITLES.forEach(([t], k) => { if (f >= t) i = k; });
  if (i < 0) return null;
  const t0 = TITLES[i][0];
  const inn = prog(f, t0, t0 + 10, easeOut);
  const sweep = prog(f, t0 + 4, t0 + 16, easeInOut);
  const next = TITLES[i + 1]?.[0];
  const out = next ? prog(f, next - 6, next, Easing.in(Easing.cubic)) : 0;
  return (
    <div style={{ position: 'absolute', left: 120, top: 128, fontFamily: SANS, fontWeight: 700, fontSize: 76, letterSpacing: '-0.035em', color: INK,
      whiteSpace: 'nowrap', opacity: inn * (1 - out), transform: `translateY(${(1 - inn) * 30 - out * 20}px)` }}>
      <span style={{ background: `linear-gradient(178deg, transparent 0 52%, ${HI} 52% 93%, transparent 93%) no-repeat 0 0 / ${sweep * 100}% 100%`, padding: '0 10px' }}>
        {TITLES[i][1]}
      </span>
    </div>
  );
};

export const MotionGraphics: React.FC = () => {
  const f = useCurrentFrame();
  const board = prog(f, 0, 12, easeOut);

  // --- slice A (gets the peanut butter) and slice B (goes on top) ---
  const popA = pop(f, at(K.two) - 2), popB = pop(f, at(K.slices) - 2);
  const toStep2 = prog(f, STEPS.knife.from - 4, STEPS.knife.from + 12, easeInOut);
  const toStep3 = prog(f, STEPS.spread.from - 4, STEPS.spread.from + 12, easeInOut);
  const toStep4 = prog(f, STEPS.press.from, STEPS.press.from + 14, easeInOut);
  const lift = prog(f, at(K.press) + 2, at(K.second) + 6, easeInOut);
  const flip = prog(f, at(K.second) + 2, at(K.slice) + 8, easeInOut);
  const land = prog(f, at(K.slice) + 6, at(K.top) - 1, Easing.in(Easing.quad));
  const squash = f >= at(K.top) - 1 ? Math.sin(clamp((f - at(K.top) + 1) / 9) * Math.PI) * Math.exp(-(f - at(K.top) + 1) / 12) : 0;
  const toCut = prog(f, STEPS.cut.from - 6, STEPS.cut.from + 8, easeInOut);
  const toPay = prog(f, STEPS.payoff.from - 2, STEPS.payoff.from + 16, easeInOut);

  // positions per step (centre x, y, scale)
  const ax = mix(toStep4, mix(toStep3, mix(toStep2, 760, 520), 700), 900);
  const ay = mix(toStep3, mix(toStep2, 575, 600), 610);
  const as = mix(toStep3, mix(toStep2, 1, 0.82), 1.2) * mix(toStep4, 1, 1.05);
  const bxRest = mix(toStep3, mix(toStep2, 1160, 860), 1200);
  const byRest = mix(toStep3, mix(toStep2, 575, 600), 650);
  const bsRest = mix(toStep3, mix(toStep2, 1, 0.82), 0.8);
  const bx = mix(land, mix(lift, bxRest, mix(0.5, bxRest, ax)), ax);
  const by = mix(land, mix(lift, byRest, 430), ay - 14);
  const bs = mix(land, mix(lift, bsRest, 1.05), as);
  const flipX = Math.cos(flip * Math.PI); // 1 -> -1: the slice turns over
  // the whole sandwich moves to centre for the cut, then left for the payoff
  const sx = mix(toPay, mix(toCut, 0, 960 - ax), 600 - ax);
  const sy = mix(toPay, mix(toCut, 0, 600 - ay), 600 - ay);
  const ss = mix(toPay, mix(toCut, 1, 1.1), 0.92);

  // --- peanut butter spreading (step 3) ---
  const pb = prog(f, at(K.spread), at(K.edges) + 4, Easing.inOut(Easing.quad));
  const coverage = Math.round(pb * 100);

  // --- jar and knife (steps 2 and 3) ---
  const jarIn = pop(f, at(K.dig) - 4, { damping: 14, stiffness: 150 });
  const jarOut = prog(f, STEPS.spread.from + 2, STEPS.spread.from + 16, Easing.in(Easing.cubic));
  const lid = prog(f, at(K.dig) + 2, at(K.knife) + 4, Easing.out(Easing.quad));
  const jarX = 1360 + (1 - jarIn) * 700 + jarOut * 800, jarY = 600;
  const knifeIn = prog(f, at(K.knife) - 4, at(K.into) + 2, Easing.out(Easing.back(1.2)));
  const dip = prog(f, at(K.into), at(K.peanut) + 2, easeInOut);
  const out = prog(f, at(K.butter) - 2, at(K.butter) + 12, easeInOut);
  const level = 1 - 0.18 * dip;
  // knife path: above jar -> into jar -> lifted with a blob -> over slice A spreading in a zigzag -> away
  let kx = jarX, ky = mix(knifeIn, -200, jarY - 40) + dip * 90 - out * 210, kr = 0, kOn = knifeIn;
  const spreadT = prog(f, at(K.spread) - 2, at(K.edges) + 4, (t) => t);
  if (f >= STEPS.spread.from - 4) {
    const go = prog(f, STEPS.spread.from - 4, at(K.spread), easeInOut);
    const zig = Math.sin(spreadT * Math.PI * 5);
    kx = mix(go, jarX, ax + zig * 95 * as);
    ky = mix(go, jarY - 250, ay + mix(spreadT, -60, 70) * as + 10);
    kr = mix(go, 0, -62 + zig * 10);
  }
  const kAway = prog(f, at(K.edges) + 6, at(K.edges) + 20, Easing.in(Easing.cubic));
  kx += kAway * 900; ky -= kAway * 200; kOn *= 1 - kAway;
  const blob = f < STEPS.spread.from ? out : 1 - pb;

  // --- the cut (step 5) ---
  const guide = prog(f, at(K.corner1) - 2, at(K.corner2) + 4, easeInOut);
  const split = prog(f, at(K.corner2) + 6, at(K.corner2) + 18, Easing.out(Easing.back(1.4)));
  const cutKnife = prog(f, at(K.cut) - 2, at(K.corner2) + 6, easeInOut);

  // --- payoff card ---
  const card = pop(f, at(K.triangles) - 4, { damping: 15, stiffness: 140 });
  const starsSq = [0, 1, 2].map((i) => prog(f, at(K.taste) - 4 + i * 3, at(K.taste) + 2 + i * 3, backOut));
  const starsTri = [0, 1, 2, 3, 4].map((i) => prog(f, at(K.better) - 4 + i * 3, at(K.better) + 2 + i * 3, backOut));
  const crown = pop(f, at(K.better) + 14, { damping: 9, stiffness: 200 });

  // gentle camera: always moving a little, a small push on each step
  const cam = 1 + 0.02 * Math.sin(f / 70) + 0.025 * (toStep2 + toStep3 + toStep4 + toCut + toPay) / 5 + prog(f, 380, 450) * 0.03;

  const sandwichOrigin = `translate(${ax + sx} ${ay + sy}) scale(${ss})`;
  const local = (x: number, y: number) => `translate(${(x - ax) * 1} ${(y - ay) * 1})`;

  return (
    <AbsoluteFill style={{ background: '#fff', overflow: 'hidden' }}>
      <AbsoluteFill style={{ backgroundImage: `radial-gradient(${DOT} 1.5px, transparent 1.5px)`, backgroundSize: '40px 40px', opacity: board }} />
      <AbsoluteFill style={{ transform: `scale(${cam})` }}>
        {/* header */}
        <div style={{ position: 'absolute', left: 126, top: 84, fontFamily: MONO, fontWeight: 500, fontSize: 24, letterSpacing: '0.07em',
          color: G2, textTransform: 'uppercase', opacity: board }}>How to make · a peanut-butter sandwich</div>
        <Title f={f} />

        <svg width={1920} height={1080} style={{ position: 'absolute', inset: 0, overflow: 'visible' }}>
          {/* jar */}
          {f >= at(K.dig) - 6 && jarOut < 1 ? (
            <g transform={`translate(${jarX} ${jarY}) scale(${0.6 + 0.4 * jarIn})`}><Jar level={level} lid={lid} /></g>
          ) : null}
          {/* slice B waiting (before it lands it is drawn under the knife, above slice A) */}
          {/* the sandwich group: slice A, then slice B when it lands */}
          <g transform={sandwichOrigin}>
            {[0, 1].map((half) => {
              // during and after the cut the sandwich is drawn twice, clipped to the two triangles
              const cutting = split > 0;
              if (!cutting && half === 1) return null;
              const d = 34 * split;
              const tr = !cutting ? '' : half === 0 ? `translate(${d * 0.7} ${-d * 0.7})` : `translate(${-d * 0.7} ${d * 0.7})`;
              return (
                <g key={half} transform={tr} clipPath={cutting ? `url(#tri-${half})` : undefined}>
                  <g transform={`scale(${as * (1 - 0.06 * squash)} ${as * (1 + 0.04 * squash)})`}>
                    <g opacity={clamp(popA * 2)} transform={`scale(${popA})`}><Slice id="a" pb={pb} pbCx={-40} pbCy={-20} /></g>
                    {land >= 1 ? (
                      <g transform={`scale(${1 + 0.05 * squash} ${1 - 0.1 * squash})`}>
                        <path d={OUTER} fill={PB} transform="translate(-7 -13)" />
                        <g transform="translate(-14 -28)"><Slice id="b2" /></g>
                      </g>
                    ) : null}
                    {cutting ? <line x1={-260} y1={-260} x2={260} y2={260} stroke={PB} strokeWidth={30} clipPath="url(#slice-clip)" /> : null}
                  </g>
                </g>
              );
            })}
            <defs>
              <clipPath id="tri-0"><path d="M -400 -400 L 400 -400 L 400 400 Z" /></clipPath>
              <clipPath id="tri-1"><path d="M -400 -400 L 400 400 L -400 400 Z" /></clipPath>
              <clipPath id="slice-clip"><path d={OUTER} transform="translate(0 -12)" /></clipPath>
            </defs>
            {/* corner-to-corner guide */}
            {guide > 0 && split < 1 ? (
              <line x1={-180 * as} y1={-180 * as} x2={mix(guide, -180, 180) * as} y2={mix(guide, -180, 180) * as} stroke={BLUE} strokeWidth={8}
                strokeDasharray="4 18" strokeLinecap="round" opacity={1 - split} />
            ) : null}
            {guide > 0 && split < 1 ? <circle cx={-180 * as} cy={-180 * as} r={12} fill={BLUE} opacity={1 - split} /> : null}
            {guide >= 1 && split < 1 ? <circle cx={180 * as} cy={180 * as} r={12} fill={BLUE} opacity={1 - split} /> : null}
          </g>
          {/* slice B before it lands */}
          {land < 1 ? (
            <g transform={`translate(${bx + sx * land} ${by + sy * land}) scale(${bs * flipX * clamp(popB) } ${bs * clamp(popB)})`} opacity={clamp(popB * 2)}>
              {flipX < 0 ? <path d={OUTER} fill={CRUST} /> : null}
              <Slice id="b" />
            </g>
          ) : null}
          {/* knife for steps 2-3 */}
          {kOn > 0.01 ? <g transform={`translate(${kx} ${ky}) rotate(${kr})`} opacity={clamp(kOn * 1.5)}><Knife blob={blob} /></g> : null}
          {/* knife for the cut, travelling along the diagonal */}
          {cutKnife > 0 && split < 0.6 ? (
            <g transform={`${sandwichOrigin} translate(${mix(cutKnife, -200, 200) * as} ${mix(cutKnife, -200, 200) * as}) rotate(-45)`} opacity={1 - split * 1.6}>
              <Knife />
            </g>
          ) : null}
          {/* "x2" counter */}
          {f >= at(K.bread) - 4 && toStep2 < 1 ? (
            <g transform={`translate(960 ${790 - 30 * (1 - pop(f, at(K.bread) - 4))})`} opacity={clamp(pop(f, at(K.bread) - 4)) * (1 - toStep2)}>
              <rect x={-90} y={-46} width={180} height={92} rx={46} fill={INK} />
              <text x={0} y={22} textAnchor="middle" fontFamily={MONO} fontWeight={700} fontSize={56} fill="#fff">×2</text>
            </g>
          ) : null}
          {/* edges arrows */}
          {f >= at(K.edges) - 4 && f < STEPS.press.from + 6 ? (
            <g transform={`translate(${ax} ${ay + 8})`} opacity={1 - prog(f, STEPS.press.from - 8, STEPS.press.from + 4)}>
              {[[0, -1, 0], [1, 0, 90], [0, 1, 180], [-1, 0, 270]].map(([dx, dy, r], i) => {
                const p = pop(f, at(K.edges) - 4 + i * 2, { damping: 10, stiffness: 220 });
                const d = 150 * as + 40 * p;
                return (
                  <g key={i} transform={`translate(${dx * d} ${dy * d}) rotate(${r}) scale(${p})`}>
                    <path d="M 0 -34 L 26 6 L 9 6 L 9 30 L -9 30 L -9 6 L -26 6 Z" fill={BLUE} />
                  </g>
                );
              })}
            </g>
          ) : null}
          {/* press arrow */}
          {f >= at(K.press) - 4 && f < at(K.top) + 20 ? (
            <g transform={`translate(${ax} ${ay - 260 + 70 * land})`} opacity={clamp(pop(f, at(K.press) - 4)) * (1 - prog(f, at(K.top) + 8, at(K.top) + 20))}>
              <path d="M 0 40 L 40 -10 L 16 -10 L 16 -60 L -16 -60 L -16 -10 L -40 -10 Z" fill={CORAL} />
            </g>
          ) : null}
        </svg>

        {/* coverage meter (step 3) */}
        {f >= STEPS.spread.from && f < STEPS.press.from + 14 ? (() => {
          const inn = pop(f, STEPS.spread.from + 2, { damping: 15, stiffness: 160 });
          const gone = prog(f, STEPS.press.from - 2, STEPS.press.from + 12, Easing.in(Easing.cubic));
          const done = coverage >= 100;
          return (
            <div style={{ position: 'absolute', left: 1330, top: 360, width: 440, padding: '28px 32px', background: '#fff', border: `1.5px solid ${LINE}`,
              borderRadius: 22, boxShadow: '0 10px 30px rgba(7,26,46,.10)', fontFamily: SANS, color: INK,
              opacity: clamp(inn) * (1 - gone), transform: `translateY(${(1 - inn) * 40 + gone * 40}px)` }}>
              <div style={{ fontFamily: MONO, fontWeight: 500, fontSize: 24, letterSpacing: '0.07em', color: G2, textTransform: 'uppercase' }}>Coverage</div>
              <div style={{ fontSize: 120, fontWeight: 800, letterSpacing: '-0.04em', lineHeight: 1.05, fontVariantNumeric: 'tabular-nums', color: done ? MINT : INK }}>
                {coverage}<span style={{ fontSize: 64 }}>%</span>
              </div>
              <div style={{ height: 22, borderRadius: 11, background: WASH, overflow: 'hidden', marginTop: 8 }}>
                <div style={{ height: '100%', width: `${coverage}%`, background: done ? MINT : PB, borderRadius: 11 }} />
              </div>
              <div style={{ fontFamily: MONO, fontSize: 24, marginTop: 14, color: done ? MINT : G2, opacity: done ? 1 : 0.0 }}>✓ right to the edges</div>
            </div>
          );
        })() : null}

        {/* payoff: star ratings */}
        {f >= at(K.triangles) - 4 ? (
          <div style={{ position: 'absolute', left: 1060, top: 330, width: 700, opacity: clamp(card * 1.5), transform: `translateX(${(1 - card) * 80}px)` }}>
            <div style={{ fontFamily: MONO, fontWeight: 500, fontSize: 26, letterSpacing: '0.07em', color: G2, textTransform: 'uppercase', marginBottom: 18 }}>Taste rating</div>
            {[{ label: 'Square', stars: starsSq, n: 5, tri: false }, { label: 'Triangles', stars: starsTri, n: 5, tri: true }].map((row, r) => (
              <div key={r} style={{ display: 'flex', alignItems: 'center', gap: 26, padding: '22px 28px', marginBottom: 20, borderRadius: 22,
                background: row.tri ? BLUE_L : '#fff', border: `1.5px solid ${row.tri ? BLUE : LINE}`, boxShadow: '0 10px 30px rgba(7,26,46,.10)', position: 'relative' }}>
                <svg width={70} height={70} viewBox="-35 -35 70 70">
                  {row.tri ? <path d="M -28 28 L 28 28 L -28 -28 Z" fill={CRUST} stroke={PB} strokeWidth={5} /> : <rect x={-28} y={-28} width={56} height={56} rx={6} fill={CRUST} stroke={PB} strokeWidth={5} />}
                </svg>
                <div style={{ fontFamily: SANS, fontWeight: 700, fontSize: 52, color: INK, width: 250, letterSpacing: '-0.03em' }}>{row.label}</div>
                <svg width={300} height={60} viewBox="-30 -30 300 60">
                  {Array.from({ length: row.n }).map((_, i) => <Star key={i} x={i * 60} on={row.stars[i] ?? 0} fill={row.tri ? '#F5B301' : '#F5B301'} />)}
                </svg>
                {row.tri ? (
                  <div style={{ position: 'absolute', right: -26, top: -30, transform: `scale(${crown}) rotate(12deg)`, background: CORAL, color: '#fff',
                    fontFamily: MONO, fontWeight: 700, fontSize: 26, padding: '8px 16px', borderRadius: 999 }}>WINNER</div>
                ) : null}
              </div>
            ))}
          </div>
        ) : null}

        {/* step chips */}
        <div style={{ position: 'absolute', left: 0, right: 0, top: 952, display: 'flex', justifyContent: 'center', gap: 22, opacity: board }}>
          {CHIPS.map((c, i) => {
            const on = f >= CHIP_AT[i] - 2;
            const done = f >= CHIP_AT[i + 1] - 2;
            const p = pop(f, CHIP_AT[i] - 2, { damping: 12, stiffness: 220 });
            return (
              <div key={c} style={{ display: 'flex', alignItems: 'center', gap: 12, padding: '12px 24px 12px 14px', borderRadius: 999,
                fontFamily: SANS, fontWeight: 700, fontSize: 30, letterSpacing: '-0.02em',
                background: done ? INK : on ? BLUE : '#fff', color: on || done ? '#fff' : G2, border: `1.5px solid ${on || done ? 'transparent' : LINE}`,
                transform: `scale(${on && !done ? 1 + 0.08 * p : 1})`, boxShadow: on && !done ? '0 10px 24px rgba(10,132,198,.35)' : 'none' }}>
                <span style={{ width: 42, height: 42, borderRadius: 21, display: 'grid', placeItems: 'center', fontFamily: MONO, fontSize: 24,
                  background: on || done ? 'rgba(255,255,255,.18)' : WASH, color: on || done ? '#fff' : G2 }}>{done ? '✓' : i + 1}</span>
                {c}
              </div>
            );
          })}
        </div>
      </AbsoluteFill>
      <Soundtrack sfx={SFX} />
    </AbsoluteFill>
  );
};

const SFX: Sfx[] = [
  { at: at(K.take) - 2, file: 'swipe1.wav', vol: 0.25 },
  { at: at(K.two) - 2, file: 'pop2.wav', vol: 0.35 },
  { at: at(K.slices) - 2, file: 'pop2.wav', vol: 0.3 },
  { at: at(K.bread) - 4, file: 'card.wav', vol: 0.3 },
  { at: STEPS.knife.from - 3, file: 'swipe2.wav', vol: 0.3 },
  { at: at(K.dig) - 4, file: 'card2.wav', vol: 0.3 },
  { at: at(K.dig) + 2, file: 'pop.wav', vol: 0.3 },
  { at: at(K.into), file: 'smack.wav', vol: 0.25 },
  { at: STEPS.spread.from - 3, file: 'swipe3.wav', vol: 0.3 },
  { at: at(K.spread), file: 'swish1.wav', vol: 0.2 },
  { at: at(K.edges) - 4, file: 'ding.wav', vol: 0.18 },
  { at: STEPS.press.from - 2, file: 'swipe1.wav', vol: 0.3 },
  { at: at(K.top) - 1, file: 'thud.wav', vol: 0.4 },
  { at: STEPS.cut.from - 4, file: 'swipe2.wav', vol: 0.3 },
  { at: at(K.corner1) - 2, file: 'stroke.wav', vol: 0.3 },
  { at: at(K.corner2) + 6, file: 'whip.wav', vol: 0.4 },
  { at: at(K.triangles) - 4, file: 'card.wav', vol: 0.3 },
  { at: at(K.taste) - 4, file: 'pop2.wav', vol: 0.2 },
  { at: at(K.better) - 4, file: 'pop2.wav', vol: 0.25 },
  { at: at(K.better) + 14, file: 'ding.wav', vol: 0.2 },
];
