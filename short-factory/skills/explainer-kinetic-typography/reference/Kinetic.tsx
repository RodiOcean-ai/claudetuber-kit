// Style 1: KINETIC TYPOGRAPHY. Every word lands on its spoken word; the words act out their meaning (SLICES splits, KNIFE
// slides in like a blade, SPREAD stretches, EDGES flies to the edges, PRESS squashes, CUT is cut). A camera glides from one
// word group to the next across a big page; at the end it pulls back, the whole page becomes a slice of bread and is cut
// corner to corner into two triangles.
import React from 'react';
import { AbsoluteFill, Easing, interpolate, useCurrentFrame } from 'remotion';
import { Soundtrack, Sfx } from '../../shared/Soundtrack';
import { ensureFonts } from '../../shared/fonts';
import { WORDS, K, at } from '../../shared/timing';
import { backOut, clamp, easeOut, mix, pop, prog } from '../../shared/anim';

ensureFonts('Rubik', 'Anton', 'Instrument Serif');

const BG = '#FFF3DC';
const INK = '#2A1A0E';
const CRUST = '#D3922F';
const CRUMB = '#F9E3AE';
const PB = '#9A521E';
const BLUE = '#0A84C6';
const HEAVY = 'Rubik';
const SERIF = 'Instrument Serif';

// ---------- the page: where each word group sits (page pixels) and the camera path ----------
type Cam = { f: number; x: number; y: number; s: number; r: number };
const G = {
  c1: { x: 0, y: 0, r: 0 },
  c2: { x: 2050, y: 0, r: -6 },
  c3: { x: 2050, y: 1250, r: 0 },
  c4: { x: 0, y: 1250, r: 5 },
  c5: { x: 0, y: 2500, r: 0 },
  c6: { x: 2050, y: 2500, r: -4 },
};
const MAP = { x: 1025, y: 1230, s: 0.232 }; // the whole page in view at the end
const CAM: Cam[] = [
  { f: 0, x: 0, y: 40, s: 1.22, r: 2 },
  { f: 64, ...G.c1, s: 1.0 },
  { f: 77, ...G.c2, s: 1.0 },
  { f: 127, ...G.c2, y: 20, s: 0.95, r: -7 },
  { f: 140, ...G.c3, s: 1.0 },
  { f: 203, ...G.c3, y: 1270, s: 0.9, r: 0 },
  { f: 216, ...G.c4, s: 1.0 },
  { f: 266, ...G.c4, y: 1270, s: 0.95, r: 6 },
  { f: 279, ...G.c5, s: 1.0 },
  { f: 322, ...G.c5, y: 2520, s: 0.95, r: 0 },
  { f: 335, ...G.c6, s: 1.0 },
  { f: 380, ...G.c6, y: 2520, s: 0.92, r: -5 },
  { f: 404, x: MAP.x, y: MAP.y, s: MAP.s, r: 0 },
  { f: 450, x: MAP.x, y: MAP.y, s: MAP.s * 0.97, r: 0 },
];
const WHIP = Easing.bezier(0.75, 0, 0.25, 1);
const camAt = (f: number) => {
  let i = 0;
  while (i < CAM.length - 2 && f >= CAM[i + 1].f) i++;
  const a = CAM[i], b = CAM[i + 1];
  // short gaps between keys are camera moves (whips); long ones are slow drifts
  const move = b.f - a.f <= 26;
  const t = interpolate(f, [a.f, b.f], [0, 1], { extrapolateLeft: 'clamp', extrapolateRight: 'clamp', easing: move ? WHIP : (x) => x });
  // scale changes multiplicatively so zooms feel even
  const s = Math.exp(mix(t, Math.log(a.s), Math.log(b.s)));
  return { x: mix(t, a.x, b.x), y: mix(t, a.y, b.y), s, r: mix(t, a.r, b.r) };
};
const pageTransform = (c: { x: number; y: number; s: number; r: number }) =>
  `translate(960px, 540px) scale(${c.s}) rotate(${-c.r}deg) translate(${-c.x}px, ${-c.y}px)`;

// ---------- words ----------
type Kind = 'pop' | 'rise' | 'drop' | 'blade' | 'gloop' | 'stretch' | 'edges' | 'squash' | 'sliced' | 'cut' | 'tri' | 'big';
type WProps = { k: number; text?: string; size: number; font?: string; color?: string; kind?: Kind; italic?: boolean; style?: React.CSSProperties };

const appear = (k: number) => at(k) - 2; // a word lands two frames before it is heard

const Word: React.FC<WProps> = ({ k, text, size, font = HEAVY, color = INK, kind = 'pop', italic, style }) => {
  const f = useCurrentFrame();
  const a = appear(k);
  const t = f - a;
  const label = text ?? WORDS[k].w.replace(/[,.]/g, '').toUpperCase();
  const base: React.CSSProperties = {
    fontFamily: font, fontSize: size, color, fontWeight: font === HEAVY ? 900 : 400, fontStyle: italic ? 'italic' : 'normal',
    lineHeight: 0.92, display: 'inline-block', whiteSpace: 'nowrap', letterSpacing: font === HEAVY ? '-0.02em' : 0, ...style,
  };
  if (t < 0) return <span style={{ ...base, opacity: 0 }}>{label}</span>;
  const o = clamp(t / 3);
  if (kind === 'rise') {
    const y = interpolate(t, [0, 7], [105, 0], { extrapolateRight: 'clamp', easing: easeOut });
    return (
      <span style={{ display: 'inline-block', overflow: 'hidden', paddingBottom: size * 0.12, marginBottom: -size * 0.12 }}>
        <span style={{ ...base, transform: `translateY(${y}%)` }}>{label}</span>
      </span>
    );
  }
  if (kind === 'drop') {
    const p = pop(f, a, { damping: 9, stiffness: 220, mass: 0.7 });
    return <span style={{ ...base, opacity: o, transform: `translateY(${(1 - p) * -420}px) scaleY(${1 + (1 - p) * 0.25})` }}>{label}</span>;
  }
  if (kind === 'blade') {
    const p = interpolate(t, [0, 6], [0, 1], { extrapolateRight: 'clamp', easing: easeOut });
    const gleam = interpolate(t, [5, 16], [-30, 130], { extrapolateLeft: 'clamp', extrapolateRight: 'clamp' });
    return (
      <span style={{ ...base, opacity: o, transform: `translateX(${(1 - p) * 900}px) skewX(${(1 - p) * -25}deg)`, position: 'relative' }}>
        {label}
        <span style={{ position: 'absolute', inset: 0, background: `linear-gradient(100deg, transparent ${gleam - 12}%, rgba(255,255,255,0.85) ${gleam}%, transparent ${gleam + 12}%)`,
          WebkitBackgroundClip: 'text', backgroundClip: 'text', color: 'transparent' }}>{label}</span>
      </span>
    );
  }
  if (kind === 'gloop' || kind === 'edges' || kind === 'tri') {
    const letters = label.split('');
    const spread = kind === 'edges' ? interpolate(t, [0, 20], [0, 0.62], { extrapolateRight: 'clamp', easing: Easing.out(Easing.exp) }) : 0;
    return (
      <span style={{ ...base, letterSpacing: `${spread - 0.02}em`, marginRight: `${-spread}em` }}>
        {letters.map((ch, i) => {
          const d = kind === 'gloop' ? i * 1.2 : kind === 'tri' ? i * 1.4 : 0;
          const p = pop(f, a + d, kind === 'gloop' ? { damping: 7, stiffness: 160 } : { damping: 11, stiffness: 200 });
          const wob = kind === 'gloop' ? Math.sin((t - d) * 0.6) * Math.exp(-(t - d) / 10) * 22 : 0;
          const rot = kind === 'tri' ? (1 - p) * (i % 2 ? 50 : -50) : 0;
          return (
            <span key={i} style={{ display: 'inline-block', opacity: clamp((t - d) / 3), transform: `translateY(${(1 - p) * 120 + wob}px) rotate(${rot}deg) scale(${0.4 + 0.6 * p})` }}>
              {ch}
            </span>
          );
        })}
      </span>
    );
  }
  if (kind === 'stretch') {
    // SPREAD stretches across the line while it is said
    const sx = interpolate(t, [0, 16], [0.3, 1.25], { extrapolateRight: 'clamp', easing: Easing.out(Easing.quad) });
    return (
      <span style={{ display: 'inline-flex', justifyContent: 'center', width: 1100 }}>
        <span style={{ ...base, opacity: o, transform: `scaleX(${sx})`, transformOrigin: '50% 50%' }}>{label}</span>
      </span>
    );
  }
  if (kind === 'squash') {
    const p = pop(f, a, { damping: 10, stiffness: 260 });
    const hit = pop(f, a + 6, { damping: 8, stiffness: 300 });
    const sy = (0.4 + 0.6 * p) * (1 - 0.32 * Math.sin(clamp(hit) * Math.PI));
    return <span style={{ ...base, opacity: o, transform: `scaleY(${sy}) scaleX(${1 + (1 - sy) * 0.5})`, transformOrigin: '50% 100%' }}>{label}</span>;
  }
  if (kind === 'sliced' || kind === 'cut') {
    // the word splits in two along a line (flat for SLICES, corner to corner for CUT)
    const p = pop(f, a, { damping: 12, stiffness: 200 });
    const s = prog(f, a + (kind === 'cut' ? 6 : 8), a + (kind === 'cut' ? 14 : 16), easeOut);
    const up = kind === 'cut' ? 'polygon(0 0, 100% 0, 100% 8%, 0 92%)' : 'polygon(0 0, 100% 0, 100% 52%, 0 52%)';
    const down = kind === 'cut' ? 'polygon(0 92%, 100% 8%, 100% 100%, 0 100%)' : 'polygon(0 52%, 100% 52%, 100% 100%, 0 100%)';
    // halves part across the cut line (for CUT the line climbs left to right, so the top half goes up, the bottom half down)
    const dx = kind === 'cut' ? 10 * s : 0, dy = kind === 'cut' ? 34 * s : 14 * s;
    const line = kind === 'cut' ? prog(f, a + 2, a + 7, easeOut) : 0;
    const lineFade = kind === 'cut' ? 1 - prog(f, a + 16, a + 24) : 0;
    return (
      <span style={{ position: 'relative', display: 'inline-block', opacity: o, transform: `scale(${0.5 + 0.5 * p})` }}>
        <span style={{ ...base, clipPath: up, transform: `translate(${dx}px, ${-dy}px) rotate(${kind === 'cut' ? -3 * s : 0}deg)` }}>{label}</span>
        <span style={{ ...base, clipPath: down, position: 'absolute', left: 0, top: 0, transform: `translate(${-dx}px, ${dy}px) rotate(${kind === 'cut' ? 2 * s : 0}deg)` }}>{label}</span>
        {kind === 'cut' ? (
          <svg style={{ position: 'absolute', left: '-6%', top: '-10%', width: '112%', height: '120%', overflow: 'visible' }} viewBox="0 0 100 100" preserveAspectRatio="none">
            <line x1={-2} y1={93} x2={-2 + 104 * line} y2={93 - 88 * line} stroke={BLUE} vectorEffect="non-scaling-stroke"
              style={{ strokeWidth: 12, opacity: lineFade }} strokeLinecap="round" />
          </svg>
        ) : null}
      </span>
    );
  }
  // pop / big
  const p = pop(f, a, kind === 'big' ? { damping: 10, stiffness: 180 } : { damping: 13, stiffness: 210 });
  return <span style={{ ...base, opacity: o, transform: `translateY(${(1 - p) * 40}px) scale(${0.55 + 0.45 * p})` }}>{label}</span>;
};

const Row: React.FC<{ children: React.ReactNode; gap?: number; style?: React.CSSProperties }> = ({ children, gap = 34, style }) => (
  <div style={{ display: 'flex', alignItems: 'baseline', justifyContent: 'center', gap, ...style }}>{children}</div>
);
const Group: React.FC<{ g: { x: number; y: number; r: number }; children: React.ReactNode; gap?: number }> = ({ g, children, gap = 10 }) => (
  <div style={{ position: 'absolute', left: g.x, top: g.y, transform: `translate(-50%, -50%) rotate(${g.r}deg)`, display: 'flex',
    flexDirection: 'column', alignItems: 'center', gap }}>{children}</div>
);
const serif = (k: number, size = 120, text?: string) => <Word k={k} text={text ?? WORDS[k].w.replace(/[,.]/g, '')} size={size} font={SERIF} italic kind="rise" />;

// a hand-drawn-ish underline that spreads to both sides (for "right to the edges")
const SpreadBar: React.FC = () => {
  const f = useCurrentFrame();
  const p = prog(f, appear(K.edges), appear(K.edges) + 20, Easing.out(Easing.exp));
  return <div style={{ height: 34, width: mix(p, 60, 1500), borderRadius: 17, background: PB, opacity: p > 0 ? 1 : 0, marginTop: 8 }} />;
};

// "corner to corner": laid out on the diagonal with a dashed guide drawn from corner to corner
const CornerToCorner: React.FC = () => {
  const f = useCurrentFrame();
  const line = prog(f, appear(K.corner1), appear(K.corner2) + 8, Easing.inOut(Easing.quad));
  return (
    <div style={{ position: 'relative', width: 1700, height: 600 }}>
      <svg width={1700} height={600} style={{ position: 'absolute', left: 0, top: 0, overflow: 'visible' }}>
        <line x1={40} y1={30} x2={40 + 1620 * line} y2={30 + 530 * line} stroke={BLUE} strokeWidth={14} strokeLinecap="round" strokeDasharray="1 34" />
        <circle cx={40} cy={30} r={line > 0 ? 18 : 0} fill={BLUE} />
        <circle cx={1660} cy={560} r={line > 0.98 ? 18 : 0} fill={BLUE} />
      </svg>
      <div style={{ position: 'absolute', left: 90, top: 56, transform: 'rotate(18deg)', transformOrigin: '0 0' }}><Word k={K.corner1} size={150} /></div>
      <div style={{ position: 'absolute', left: 790, top: 250 }}>{serif(K.to2, 130)}</div>
      <div style={{ position: 'absolute', right: 70, bottom: 36, transform: 'rotate(18deg)', transformOrigin: '100% 100%' }}><Word k={K.corner2} size={150} color={CRUST} /></div>
    </div>
  );
};

// the triangle drawn round TRIANGLES
const TriangleMark: React.FC = () => {
  const f = useCurrentFrame();
  const p = prog(f, appear(K.triangles) + 2, appear(K.triangles) + 22, Easing.inOut(Easing.cubic));
  const fill = prog(f, appear(K.triangles) + 10, appear(K.triangles) + 26);
  const len = 4700;
  return (
    <svg width={2000} height={1000} style={{ position: 'absolute', left: '50%', top: '50%', transform: 'translate(-50%, -50%)', overflow: 'visible', pointerEvents: 'none' }}>
      <path d="M 1000 10 L 1990 990 L 10 990 Z" fill={BLUE} opacity={0.12 * fill} />
      <path d="M 1000 10 L 1990 990 L 10 990 Z" fill="none" stroke={BLUE} strokeWidth={14} strokeLinejoin="round" strokeLinecap="round"
        strokeDasharray={len} strokeDashoffset={len * (1 - p)} opacity={p > 0 ? 1 : 0} />
    </svg>
  );
};

const Page: React.FC = () => (
  <div style={{ position: 'absolute', left: 0, top: 0, width: 0, height: 0 }}>
    <Group g={G.c1}>
      <Row><Word k={K.take} size={130} style={{ fontWeight: 800 }} /></Row>
      <Row><Word k={K.two} size={240} color={CRUST} kind="big" /><Word k={K.slices} size={240} kind="sliced" /></Row>
      <Row>{serif(3, 150)}<Word k={K.bread} size={290} color={CRUST} kind="big" style={{ WebkitTextStroke: `10px ${INK}`, paintOrder: 'stroke fill' }} /></Row>
    </Group>
    <Group g={G.c2}>
      <Row>{serif(K.then, 130)}<Word k={K.dig} size={230} kind="drop" />{serif(7, 130)}</Row>
      <Row><Word k={K.knife} size={270} font="Anton" kind="blade" style={{ letterSpacing: '0.16em', fontWeight: 400 }} /></Row>
      <Row>{serif(K.into, 120)}{serif(10, 120)}</Row>
      <Row gap={40}><Word k={K.peanut} size={200} color={PB} kind="gloop" /><Word k={K.butter} size={200} color={PB} kind="gloop" /></Row>
    </Group>
    <Group g={G.c3} gap={6}>
      <Row>{serif(K.and1, 130)}<Word k={K.spread} size={210} color={PB} kind="stretch" />{serif(K.it1, 130)}</Row>
      <Row>{serif(K.right, 130)}{serif(17, 130)}{serif(18, 130)}</Row>
      <Row><Word k={K.edges} size={250} kind="edges" /></Row>
      <SpreadBar />
    </Group>
    <Group g={G.c4} gap={4}>
      <Row><Word k={K.top} size={230} color={CRUST} kind="drop" /></Row>
      <Row><Word k={K.press} size={300} kind="squash" /></Row>
      <Row>{serif(21, 120)}<Word k={K.second} size={180} color={CRUST} /><Word k={K.slice} size={180} color={CRUST} />{serif(K.on, 120)}</Row>
    </Group>
    <Group g={G.c5} gap={0}>
      <Row>{serif(K.and2, 130)}<Word k={K.cut} size={330} kind="cut" />{serif(28, 130)}</Row>
      <CornerToCorner />
    </Group>
    <Group g={G.c6} gap={14}>
      <TriangleMark />
      <Row style={{ marginTop: 120 }}>{serif(K.because, 140)}</Row>
      <Row><Word k={K.triangles} size={200} color={BLUE} kind="tri" /></Row>
      <Row><Word k={K.taste} size={230} color={PB} kind="big" /><Word k={K.better} size={230} kind="big" /></Row>
    </Group>
  </div>
);

// ---------- the payoff: the page becomes a slice of bread, cut corner to corner ----------
// slice outline in screen pixels (centre 960, 540)
const SL = { x0: 960 - 470, y0: 540 - 470, w: 940, h: 940 };
const slicePath = () => {
  const { x0, y0, w, h } = SL;
  const X = (u: number) => x0 + u * w, Y = (v: number) => y0 + v * h;
  return `M ${X(0.07)} ${Y(1)} L ${X(0.93)} ${Y(1)} Q ${X(1)} ${Y(1)} ${X(1)} ${Y(0.93)} L ${X(1)} ${Y(0.3)} ` +
    `C ${X(1.07)} ${Y(0.2)} ${X(1.05)} ${Y(0.02)} ${X(0.82)} ${Y(0.02)} C ${X(0.68)} ${Y(-0.05)} ${X(0.32)} ${Y(-0.05)} ${X(0.18)} ${Y(0.02)} ` +
    `C ${X(-0.05)} ${Y(0.02)} ${X(-0.07)} ${Y(0.2)} ${X(0)} ${Y(0.3)} L ${X(0)} ${Y(0.93)} Q ${X(0)} ${Y(1)} ${X(0.07)} ${Y(1)} Z`;
};
const PATH = slicePath();
// the cut runs from the slice's top-left corner to its bottom-right corner
const C0 = { x: SL.x0 + SL.w + 30, y: SL.y0 - 10 }, C1 = { x: SL.x0 - 30, y: SL.y0 + SL.h + 10 }; // top-right -> bottom-left
const HALF_A = `polygon(${C0.x}px ${C0.y}px, ${C1.x}px ${C1.y}px, -400px ${C1.y + 400}px, -400px -400px, ${C0.x}px -400px)`; // upper left
const HALF_B = `polygon(${C0.x}px ${C0.y}px, ${C1.x}px ${C1.y}px, ${C1.x}px 1600px, 2400px 1600px, 2400px ${C0.y}px)`; // lower right

const SliceLayer: React.FC<{ cam: ReturnType<typeof camAt>; part: 'whole' | 'a' | 'b'; sliceOn: number; crust: number }> = ({ cam, part, sliceOn, crust }) => {
  const len = 3900;
  return (
    <AbsoluteFill style={{ clipPath: part === 'a' ? HALF_A : part === 'b' ? HALF_B : undefined }}>
      <svg width={1920} height={1080} style={{ position: 'absolute', inset: 0 }}>
        <path d={PATH} fill={CRUMB} opacity={sliceOn} />
      </svg>
      <AbsoluteFill style={{ clipPath: sliceOn > 0.5 ? `path('${PATH}')` : undefined }}>
        <div style={{ position: 'absolute', left: 0, top: 0, transform: pageTransform(cam), transformOrigin: '0 0' }}><Page /></div>
      </AbsoluteFill>
      {part !== 'whole' ? (
        <svg width={1920} height={1080} style={{ position: 'absolute', inset: 0, clipPath: `path('${PATH}')` }}>
          <line x1={C0.x} y1={C0.y} x2={C1.x} y2={C1.y} stroke={PB} strokeWidth={30} />
        </svg>
      ) : null}
      <svg width={1920} height={1080} style={{ position: 'absolute', inset: 0, overflow: 'visible' }}>
        <path d={PATH} fill="none" stroke={CRUST} strokeWidth={34} strokeLinejoin="round" strokeDasharray={len} strokeDashoffset={len * (1 - crust)} opacity={crust > 0 ? 1 : 0} />
        <path d={PATH} fill="none" stroke="#B97A22" strokeWidth={6} strokeLinejoin="round" strokeDasharray={len} strokeDashoffset={len * (1 - crust)} opacity={crust > 0 ? 0.8 : 0}
          transform={`translate(0 0)`} />
      </svg>
    </AbsoluteFill>
  );
};

export const Kinetic: React.FC = () => {
  const f = useCurrentFrame();
  const cam = camAt(f);
  const prev = camAt(Math.max(0, f - 1));
  // motion blur while the camera whips between word groups
  const speed = Math.hypot((cam.x - prev.x) * cam.s, (cam.y - prev.y) * cam.s) + Math.abs(cam.r - prev.r) * 30;
  const blur = f < 400 ? Math.min(7, speed / 45) : 0;
  const sliceOn = prog(f, 392, 404, easeOut);
  const crust = prog(f, 394, 414, Easing.inOut(Easing.quad));
  const cut = prog(f, 416, 426, Easing.inOut(Easing.cubic));
  const apart = interpolate(f, [418, 436], [0, 1], { extrapolateLeft: 'clamp', extrapolateRight: 'clamp', easing: backOut });
  const nx = 0.7071 * 40 * apart, ny = 0.7071 * 40 * apart; // apart along the normal of the diagonal
  const cutLine = prog(f, 410, 418, easeOut);
  return (
    <AbsoluteFill style={{ background: BG, overflow: 'hidden' }}>
      <AbsoluteFill style={{ background: 'radial-gradient(ellipse at 50% 45%, rgba(255,255,255,0.65), rgba(255,255,255,0) 60%)' }} />
      <AbsoluteFill style={{ filter: blur > 0.3 ? `blur(${blur}px)` : undefined }}>
        {cut <= 0 ? (
          <SliceLayer cam={cam} part="whole" sliceOn={sliceOn} crust={crust} />
        ) : (
          <>
            <AbsoluteFill style={{ transform: `translate(${-nx}px, ${-ny}px)` }}><SliceLayer cam={cam} part="a" sliceOn={sliceOn} crust={crust} /></AbsoluteFill>
            <AbsoluteFill style={{ transform: `translate(${nx}px, ${ny}px)` }}><SliceLayer cam={cam} part="b" sliceOn={sliceOn} crust={crust} /></AbsoluteFill>
          </>
        )}
      </AbsoluteFill>
      {/* the knife line across the slice, corner to corner */}
      <svg width={1920} height={1080} style={{ position: 'absolute', inset: 0 }}>
        <line x1={C0.x} y1={C0.y} x2={mix(cutLine, C0.x, C1.x)} y2={mix(cutLine, C0.y, C1.y)} stroke={BLUE} strokeWidth={10} strokeLinecap="round"
          opacity={cutLine > 0 && cut < 1 ? 1 - cut : 0} />
      </svg>
      <Soundtrack sfx={SFX} />
    </AbsoluteFill>
  );
};

const SFX: Sfx[] = [
  { at: appear(K.two), file: 'pop2.wav', vol: 0.3 },
  { at: appear(K.slices) + 8, file: 'zip2.wav', vol: 0.25 },
  { at: appear(K.bread), file: 'card.wav', vol: 0.35 },
  { at: 66, file: 'swipe1.wav', vol: 0.4 },
  { at: appear(K.dig) + 3, file: 'smack.wav', vol: 0.35 },
  { at: appear(K.knife), file: 'zip1.wav', vol: 0.4 },
  { at: appear(K.peanut), file: 'pop.wav', vol: 0.25 },
  { at: 129, file: 'swipe2.wav', vol: 0.4 },
  { at: appear(K.spread), file: 'swish1.wav', vol: 0.25 },
  { at: appear(K.edges), file: 'whoosh.wav', vol: 0.35 },
  { at: 205, file: 'swipe3.wav', vol: 0.4 },
  { at: appear(K.press) + 6, file: 'thud.wav', vol: 0.45 },
  { at: appear(K.top) + 4, file: 'card2.wav', vol: 0.4 },
  { at: 268, file: 'swipe1.wav', vol: 0.4 },
  { at: appear(K.cut) + 3, file: 'whip.wav', vol: 0.45 },
  { at: appear(K.corner1), file: 'stroke.wav', vol: 0.3 },
  { at: 324, file: 'swipe2.wav', vol: 0.4 },
  { at: appear(K.triangles) + 4, file: 'circle.wav', vol: 0.25 },
  { at: appear(K.better), file: 'pop2.wav', vol: 0.3 },
  { at: 382, file: 'whoosh.wav', vol: 0.35 },
  { at: 410, file: 'whip.wav', vol: 0.4 },
  { at: 419, file: 'card.wav', vol: 0.3 },
];
