// Style 3: SCREENCAST. A screen recording of a (made-up) app, "Sandwich Studio": the cursor drags bread from the ingredient
// list onto the board, drops the jar, picks the knife tool and scoops, paints the peanut butter on with the mouse until
// the coverage reads 100 %, drags the second slice on top and holds to press, draws the cut corner to corner, then clicks
// "Serve". The camera auto-zooms on whatever the cursor is doing (the Screen Studio look), with real click sounds.
import React from 'react';
import { AbsoluteFill, Easing, interpolate, useCurrentFrame } from 'remotion';
import { Soundtrack, Sfx } from '../../shared/Soundtrack';
import { ensureFonts } from '../../shared/fonts';
import { K, at } from '../../shared/timing';
import { clamp, easeInOut, easeOut, mix, pop, prog, rand } from '../../shared/anim';

ensureFonts('Inter', 'JetBrains Mono');
const SANS = 'Inter';
const INK = '#0B2540', MUTED = '#5B6B7C', LINE = '#E3E8EF', PANEL = '#F7F9FC', BLUE = '#0A84C6', BLUE_L = '#E6F4FC', GREEN = '#16A34A';
const CRUMB = '#F6DFA4', CRUST = '#D9963F', PB = '#A65F2A', PB_L = '#C27A3E', WOOD = '#E2B47C', WOOD_D = '#C99459';

// ---------- the screen layout (screen pixels at zoom 1) ----------
const WIN = { x: 150, y: 76, w: 1620, h: 940 };
const SIDE_X = WIN.x, SIDE_W = 300, CANVAS_X = WIN.x + SIDE_W, CANVAS_W = 1020, STEPS_X = CANVAS_X + CANVAS_W;
const TOOLBAR_Y = WIN.y + 52, BODY_Y = WIN.y + 116;
const ITEM_Y = { bread: 344, jar: 420, jelly: 496, banana: 572 };
const TOOL = { select: { x: 520, y: TOOLBAR_Y + 32 }, knife: { x: 580, y: TOOLBAR_Y + 32 }, cut: { x: 640, y: TOOLBAR_Y + 32 } };
const A = { x: 760, y: 640 }, B = { x: 1030, y: 640 }, JAR = { x: 1270, y: 610 };
const SL = 250; // slice size on the board

// ---------- the cursor's path: [frame, x, y] (moves ease between keys) ----------
type P = [number, number, number];
const PATH: P[] = [
  [0, 1180, 760], [16, 1180, 760],
  [26, 215, ITEM_Y.bread], [28, 215, ITEM_Y.bread], [40, A.x, A.y], [43, A.x, A.y], // drag slice 1
  [50, 215, ITEM_Y.bread], [52, 215, ITEM_Y.bread], [64, B.x, B.y], [68, B.x, B.y], // drag slice 2
  [78, 215, ITEM_Y.jar], [80, 215, ITEM_Y.jar], [94, JAR.x, JAR.y], [96, JAR.x, JAR.y], // drag the jar
  [104, TOOL.knife.x, TOOL.knife.y], [106, TOOL.knife.x, TOOL.knife.y], // knife tool
  [114, JAR.x - 4, JAR.y - 40], [124, JAR.x - 4, JAR.y - 40], // scoop
  [134, A.x - 92, A.y - 88], // to the slice
  // paint the peanut butter on, row by row
  [140, A.x + 90, A.y - 84], [146, A.x - 92, A.y - 40], [152, A.x + 92, A.y - 30], [158, A.x - 92, A.y + 16], [163, A.x + 92, A.y + 30],
  [168, A.x - 92, A.y + 70], [173, A.x + 90, A.y + 88], [178, A.x, A.y + 10], [186, A.x, A.y + 10],
  [196, TOOL.select.x, TOOL.select.y], [200, TOOL.select.x, TOOL.select.y], // back to the arrow
  [212, B.x, B.y], [216, B.x, B.y], [244, A.x, A.y - 8], [248, A.x, A.y - 8], // drag slice 2 onto slice 1
  [250, A.x + 10, A.y + 6], [264, A.x + 10, A.y + 6], // hold to press
  [278, TOOL.cut.x, TOOL.cut.y], [281, TOOL.cut.x, TOOL.cut.y], // cut tool
  [288, A.x - SL / 2 - 6, A.y - SL / 2 - 6], [290, A.x - SL / 2 - 6, A.y - SL / 2 - 6], [302, A.x + SL / 2 + 6, A.y + SL / 2 + 6], [306, A.x + SL / 2 + 6, A.y + SL / 2 + 6],
  [346, 1362, 336], [362, 1362, 336], // "Serve" button on the toast
  [390, 1300, 640], [450, 1260, 700],
];
const cursorAt = (f: number) => {
  let i = 0;
  while (i < PATH.length - 2 && f >= PATH[i + 1][0]) i++;
  const [f0, x0, y0] = PATH[i], [f1, x1, y1] = PATH[i + 1];
  const painting = f0 >= 134 && f1 <= 178;
  const t = interpolate(f, [f0, f1], [0, 1], { extrapolateLeft: 'clamp', extrapolateRight: 'clamp', easing: painting ? (x) => x : Easing.bezier(0.45, 0, 0.25, 1) });
  // a slight arc, like a real hand on a mouse
  const arc = painting ? 0 : Math.sin(t * Math.PI) * Math.min(40, Math.hypot(x1 - x0, y1 - y0) * 0.06);
  return { x: mix(t, x0, x1), y: mix(t, y0, y1) - arc };
};
const CLICKS = [28, 43, 52, 68, 80, 96, 106, 116, 200, 216, 248, 281, 290, 306, 362];
const DOWN: [number, number][] = [[28, 43], [52, 68], [80, 96], [116, 124], [136, 178], [216, 248], [250, 264], [290, 306]];
const isDown = (f: number) => DOWN.some(([a, b]) => f >= a && f <= b);

// ---------- camera keys: [frame, zoom, centre x, centre y] ----------
const CAM: [number, number, number, number][] = [
  [0, 1, 960, 540], [12, 1, 960, 540], [24, 1.42, 640, 470], [66, 1.42, 700, 480], [76, 1.25, 820, 430], [124, 1.25, 820, 450],
  [136, 1.75, A.x, A.y - 10], [184, 1.75, A.x, A.y - 10], [198, 1.3, 760, 470], [210, 1.35, 880, 610], [266, 1.35, 840, 610],
  [278, 1.45, 700, 500], [318, 1.45, 720, 560], [334, 1.25, 1020, 520], [372, 1.25, 1020, 520], [396, 1, 960, 540], [450, 1, 960, 540],
];
const camAt = (f: number) => {
  let i = 0;
  while (i < CAM.length - 2 && f >= CAM[i + 1][0]) i++;
  const a = CAM[i], b = CAM[i + 1];
  const t = interpolate(f, [a[0], b[0]], [0, 1], { extrapolateLeft: 'clamp', extrapolateRight: 'clamp', easing: Easing.bezier(0.65, 0, 0.35, 1) });
  return { z: mix(t, a[1], b[1]), x: mix(t, a[2], b[2]), y: mix(t, a[3], b[3]) };
};

// ---------- small drawings ----------
const slicePath = (w: number, h: number) => {
  const X = (u: number) => -w / 2 + u * w, Y = (v: number) => -h / 2 + v * h;
  return `M ${X(0.08)} ${Y(1)} L ${X(0.92)} ${Y(1)} Q ${X(1)} ${Y(1)} ${X(1)} ${Y(0.92)} L ${X(1)} ${Y(0.32)} ` +
    `C ${X(1.08)} ${Y(0.2)} ${X(1.05)} ${Y(0.01)} ${X(0.8)} ${Y(0.02)} C ${X(0.66)} ${Y(-0.04)} ${X(0.34)} ${Y(-0.04)} ${X(0.2)} ${Y(0.02)} ` +
    `C ${X(-0.05)} ${Y(0.01)} ${X(-0.08)} ${Y(0.2)} ${X(0)} ${Y(0.32)} L ${X(0)} ${Y(0.92)} Q ${X(0)} ${Y(1)} ${X(0.08)} ${Y(1)} Z`;
};
const OUT = slicePath(SL, SL), INN = slicePath(SL * 0.86, SL * 0.85);
const SliceArt: React.FC<{ sel?: boolean }> = ({ sel }) => (
  <g>
    <path d={OUT} fill="#fff" stroke="#fff" strokeWidth={14} strokeLinejoin="round" />
    <path d={OUT} fill={CRUST} />
    <path d={INN} fill={CRUMB} transform="translate(0 6)" />
    {sel ? <rect x={-SL / 2 - 14} y={-SL / 2 - 14} width={SL + 28} height={SL + 28} fill="none" stroke={BLUE} strokeWidth={3} strokeDasharray="10 6" /> : null}
  </g>
);
const JarArt: React.FC<{ scale?: number; dent?: number }> = ({ scale = 1, dent = 0 }) => (
  <g transform={`scale(${scale})`}>
    <rect x={-70} y={-86} width={140} height={176} rx={26} fill="#fff" />
    <rect x={-64} y={-80} width={128} height={164} rx={22} fill="#EAF6FC" stroke="#9EC9DE" strokeWidth={4} />
    <path d={`M -58 ${-34 + dent * 14} Q 0 ${-46 + dent * 30} 58 ${-34 + dent * 14} L 58 66 Q 58 80 44 80 L -44 80 Q -58 80 -58 66 Z`} fill={PB} />
    <rect x={-64} y={2} width={128} height={46} fill={BLUE} />
    <rect x={-52} y={-100} width={104} height={20} rx={6} fill="#E11D48" />
  </g>
);
const KnifeIcon: React.FC<{ size?: number; color?: string }> = ({ size = 1, color = INK }) => (
  <g transform={`scale(${size}) rotate(45)`}>
    <path d="M -5 -16 L 5 -16 L 5 6 Q 5 12 0 14 Q -5 12 -5 6 Z" fill="none" stroke={color} strokeWidth={2.6} />
    <rect x={-4.5} y={-30} width={9} height={14} rx={3} fill={color} />
  </g>
);
const CutIcon: React.FC<{ color?: string }> = ({ color = INK }) => (
  <g>
    <line x1={-12} y1={-12} x2={12} y2={12} stroke={color} strokeWidth={3} strokeDasharray="4 4" strokeLinecap="round" />
    <circle cx={-12} cy={-12} r={4} fill={color} /><circle cx={12} cy={12} r={4} fill={color} />
  </g>
);
const ArrowIcon: React.FC<{ color?: string }> = ({ color = INK }) => <path d="M -7 -12 L -7 10 L -1 4 L 4 14 L 8 12 L 3 2 L 11 2 Z" fill={color} />;

const Cursor: React.FC<{ kind: 'arrow' | 'knife' | 'cut' | 'grab'; pressed: boolean; blob: number }> = ({ kind, pressed, blob }) => {
  const s = pressed ? 0.88 : 1;
  if (kind === 'knife') {
    return (
      <g transform={`scale(${s})`} style={{ filter: 'drop-shadow(0 4px 6px rgba(0,0,0,.35))' }}>
        <g transform="rotate(-35)">
          <path d="M -9 -86 L 9 -86 L 9 -18 Q 9 -2 0 2 Q -9 -2 -9 -18 Z" fill="#E9EEF3" stroke="#8FA3B7" strokeWidth={3} />
          <rect x={-11} y={-150} width={22} height={66} rx={9} fill={INK} />
          {blob > 0 ? <ellipse cx={0} cy={-14} rx={13 * blob} ry={16 * blob} fill={PB} /> : null}
        </g>
      </g>
    );
  }
  if (kind === 'cut') {
    return (
      <g transform={`scale(${s})`} style={{ filter: 'drop-shadow(0 3px 4px rgba(0,0,0,.35))' }}>
        <line x1={-16} y1={0} x2={16} y2={0} stroke="#fff" strokeWidth={7} /><line x1={0} y1={-16} x2={0} y2={16} stroke="#fff" strokeWidth={7} />
        <line x1={-16} y1={0} x2={16} y2={0} stroke={INK} strokeWidth={3} /><line x1={0} y1={-16} x2={0} y2={16} stroke={INK} strokeWidth={3} />
      </g>
    );
  }
  // macOS-style arrow, tip at 0,0
  return (
    <g transform={`scale(${s * 1.25})`} style={{ filter: 'drop-shadow(0 3px 4px rgba(0,0,0,.35))' }}>
      <path d="M 0 0 L 0 26 L 6.5 20 L 11 30 L 15.5 28 L 11 18.5 L 19.5 18.5 Z" fill="#000" stroke="#fff" strokeWidth={2.2} strokeLinejoin="round" />
    </g>
  );
};

const STEP_LABELS = ['Take 2 slices of bread', 'Dig the knife into the peanut butter', 'Spread it to the edges', 'Press the second slice on top', 'Cut it corner to corner'];
const STEP_DONE = [60, 124, 186, 266, 320];

export const Screencast: React.FC = () => {
  const f = useCurrentFrame();
  const cam = camAt(f);
  const cur = cursorAt(f);
  const pressed = isDown(f);

  // tool state and cursor look
  const tool: 'arrow' | 'knife' | 'cut' = f >= 281 && f < 320 ? 'cut' : f >= 106 && f < 200 ? 'knife' : 'arrow';
  const blob = f >= 116 && f < 136 ? clamp((f - 116) / 6) : f >= 136 && f < 178 ? 1 - (f - 136) / 42 : 0;

  // slices and jar on the board
  const sliceA = f >= 43 ? 1 : 0, sliceB = f >= 68 ? 1 : 0;
  const dragA = f >= 28 && f < 43, dragB = f >= 52 && f < 68, dragJar = f >= 80 && f < 96;
  const landA = pop(f, 43, { damping: 11, stiffness: 260 }), landB = pop(f, 68, { damping: 11, stiffness: 260 }), landJar = pop(f, 96, { damping: 11, stiffness: 260 });
  const scoop = prog(f, 116, 124, easeOut);
  const jarGone = prog(f, 186, 198, Easing.in(Easing.cubic));
  // slice B dragged onto A
  const dragBTop = f >= 216 && f < 248;
  const onTop = f >= 248;
  const hold = prog(f, 250, 264, (t) => t);
  const squash = f >= 264 ? Math.sin(clamp((f - 264) / 8) * Math.PI) * Math.exp(-(f - 264) / 10) : 0;
  // the cut
  const cutting = f >= 290 && f <= 306;
  const split = prog(f, 306, 318, Easing.out(Easing.back(1.5)));
  // painting: every cursor position from 136 on leaves peanut butter
  const strokes: { x: number; y: number }[] = [];
  for (let k = 136; k <= Math.min(f, 178); k++) strokes.push(cursorAt(k));
  const coverage = Math.min(100, Math.round(prog(f, 136, 172, (t) => 1 - Math.pow(1 - t, 1.3)) * 100));
  // the toast
  const toast = pop(f, at(K.because) - 2, { damping: 14, stiffness: 170 });
  const served = f >= 362;
  const confetti = f - 362;

  const steps = STEP_DONE.map((d) => f >= d);
  const stepPop = STEP_DONE.map((d) => pop(f, d, { damping: 10, stiffness: 260 }));

  // the sandwich on the board (slice A + B), drawn as two halves after the cut
  const Sandwich: React.FC<{ half?: 0 | 1 }> = ({ half }) => (
    <g clipPath={half === undefined ? undefined : `url(#half-${half})`}>
      <g transform={`scale(${1 + 0.04 * squash} ${1 - 0.08 * squash})`}>
        <SliceArt />
        <g mask="url(#paint)">
          <path d={INN} fill={PB} transform="translate(0 6)" />
          <path d="M -70 -40 C -30 -60 30 -55 70 -30 M -75 20 C -35 0 25 5 72 28" stroke={PB_L} strokeWidth={8} fill="none" strokeLinecap="round" opacity={0.8} />
        </g>
        {onTop ? (
          <g transform="translate(-8 -16)">
            <path d={OUT} fill={PB} transform="translate(4 8)" />
            <SliceArt />
          </g>
        ) : null}
      </g>
      {half !== undefined ? <line x1={-SL} y1={-SL} x2={SL} y2={SL} stroke={PB} strokeWidth={18} clipPath="url(#slice-in)" /> : null}
    </g>
  );

  return (
    <AbsoluteFill style={{ background: '#0B2540', overflow: 'hidden', fontFamily: SANS }}>
      <AbsoluteFill style={{ transform: `translate(${960 - cam.x * cam.z}px, ${540 - cam.y * cam.z}px) scale(${cam.z})`, transformOrigin: '0 0' }}>
        {/* wallpaper */}
        <div style={{ position: 'absolute', left: 0, top: 0, width: 1920, height: 1080, background: 'linear-gradient(135deg, #BFE6F8 0%, #7FC4EA 45%, #3E8FC4 100%)' }}>
          <div style={{ position: 'absolute', left: -200, top: 620, width: 1200, height: 700, borderRadius: '50%', background: 'rgba(255,255,255,0.18)', filter: 'blur(60px)' }} />
          <div style={{ position: 'absolute', left: 1100, top: -200, width: 900, height: 600, borderRadius: '50%', background: 'rgba(255,255,255,0.22)', filter: 'blur(70px)' }} />
        </div>
        {/* menu bar */}
        <div style={{ position: 'absolute', left: 0, top: 0, width: 1920, height: 34, background: 'rgba(255,255,255,0.62)',
          display: 'flex', alignItems: 'center', gap: 28, padding: '0 22px', fontSize: 17, color: INK }}>
          <span style={{ fontWeight: 800 }}>Sandwich Studio</span><span>File</span><span>Edit</span><span>View</span><span>Help</span>
          <span style={{ marginLeft: 'auto', fontVariantNumeric: 'tabular-nums' }}>Sat 12:30</span>
        </div>
        {/* the app window */}
        <div style={{ position: 'absolute', left: WIN.x, top: WIN.y, width: WIN.w, height: WIN.h, borderRadius: 18, background: '#fff', overflow: 'hidden',
          boxShadow: '0 40px 90px rgba(7,26,46,.45), 0 0 0 1px rgba(7,26,46,.08)' }}>
          {/* title bar */}
          <div style={{ height: 52, background: PANEL, borderBottom: `1px solid ${LINE}`, display: 'flex', alignItems: 'center', padding: '0 20px', position: 'relative' }}>
            {['#FF5F57', '#FEBC2E', '#28C840'].map((c) => <span key={c} style={{ width: 15, height: 15, borderRadius: 8, background: c, marginRight: 9 }} />)}
            <div style={{ position: 'absolute', left: 0, right: 0, textAlign: 'center', fontSize: 18, fontWeight: 600, color: MUTED }}>
              Sandwich Studio — {served ? 'lunch.sandwich · Saved' : 'Untitled.sandwich'}
            </div>
          </div>
          {/* toolbar */}
          <div style={{ height: 64, borderBottom: `1px solid ${LINE}`, display: 'flex', alignItems: 'center', paddingLeft: SIDE_W + 20 - 26, gap: 14 }}>
            {([['select', <ArrowIcon key="a" />], ['knife', <KnifeIcon key="k" size={1.1} />], ['cut', <CutIcon key="c" />]] as const).map(([name, icon]) => {
              const on = (name === 'select' && tool === 'arrow') || name === tool;
              return (
                <svg key={name} width={46} height={46} viewBox="-23 -23 46 46" style={{ borderRadius: 10, background: on ? BLUE_L : 'transparent', outline: on ? `2px solid ${BLUE}` : 'none' }}>
                  {icon}
                </svg>
              );
            })}
            <div style={{ width: 1, height: 30, background: LINE, margin: '0 10px' }} />
            <span style={{ fontSize: 17, color: MUTED }}>{tool === 'knife' ? 'Knife: click a jar to scoop, drag to spread' : tool === 'cut' ? 'Cut: drag a line across' : 'Select'}</span>
            <div style={{ marginLeft: 'auto', marginRight: 20, padding: '10px 22px', borderRadius: 10, background: BLUE, color: '#fff', fontWeight: 700, fontSize: 18 }}>Share</div>
          </div>
          {/* sidebar */}
          <div style={{ position: 'absolute', left: 0, top: 116, width: SIDE_W, bottom: 0, background: PANEL, borderRight: `1px solid ${LINE}`, padding: '22px 18px' }}>
            <div style={{ fontSize: 14, fontWeight: 700, letterSpacing: '0.08em', color: MUTED }}>INGREDIENTS</div>
            <div style={{ marginTop: 14, padding: '10px 14px', borderRadius: 10, border: `1px solid ${LINE}`, background: '#fff', color: '#9AA8B6', fontSize: 17 }}>Search…</div>
            {([['bread', 'Bread', 'x2'], ['jar', 'Peanut butter', ''], ['jelly', 'Jelly', 'not today'], ['banana', 'Banana', 'not today']] as const).map(([k, label, note]) => {
              const hot = (k === 'bread' && f >= 20 && f < 66) || (k === 'jar' && f >= 72 && f < 96);
              return (
                <div key={k} style={{ position: 'absolute', left: 14, right: 14, top: ITEM_Y[k] - WIN.y - 116 - 30, height: 62, borderRadius: 12, display: 'flex', alignItems: 'center',
                  gap: 14, padding: '0 12px', background: hot ? BLUE_L : 'transparent', opacity: note === 'not today' ? 0.45 : 1 }}>
                  <svg width={44} height={44} viewBox="-22 -22 44 44">
                    {k === 'bread' ? <g transform="scale(0.15)"><path d={OUT} fill={CRUST} /><path d={INN} fill={CRUMB} /></g> : null}
                    {k === 'jar' ? <JarArt scale={0.2} /> : null}
                    {k === 'jelly' ? <g transform="scale(0.2)"><rect x={-64} y={-80} width={128} height={164} rx={22} fill="#C2185B" /></g> : null}
                    {k === 'banana' ? <path d="M -16 8 Q 0 20 18 -12 Q 4 6 -16 2 Z" fill="#F4C430" /> : null}
                  </svg>
                  <span style={{ fontSize: 19, fontWeight: 600, color: INK }}>{label}</span>
                  <span style={{ marginLeft: 'auto', fontSize: 14, color: MUTED }}>{note}</span>
                </div>
              );
            })}
          </div>
          {/* steps panel */}
          <div style={{ position: 'absolute', left: STEPS_X - WIN.x, top: 116, right: 0, bottom: 0, borderLeft: `1px solid ${LINE}`, padding: '22px 20px', background: '#fff' }}>
            <div style={{ fontSize: 14, fontWeight: 700, letterSpacing: '0.08em', color: MUTED }}>STEPS</div>
            {STEP_LABELS.map((l, i) => (
              <div key={l} style={{ display: 'flex', alignItems: 'center', gap: 12, marginTop: 18, fontSize: 18, fontWeight: 600, color: steps[i] ? INK : MUTED }}>
                <span style={{ width: 28, height: 28, borderRadius: 8, display: 'grid', placeItems: 'center', flex: '0 0 28px',
                  background: steps[i] ? GREEN : '#fff', border: steps[i] ? 'none' : `2px solid ${LINE}`, color: '#fff', fontSize: 18, transform: `scale(${steps[i] ? 0.7 + 0.3 * stepPop[i] : 1})` }}>
                  {steps[i] ? '✓' : ''}
                </span>
                <span style={{ textDecoration: steps[i] ? 'line-through' : 'none', textDecorationColor: 'rgba(11,37,64,.35)' }}>{l}</span>
              </div>
            ))}
            <div style={{ marginTop: 28, padding: 16, borderRadius: 12, background: PANEL, border: `1px solid ${LINE}` }}>
              <div style={{ fontSize: 14, fontWeight: 700, letterSpacing: '0.08em', color: MUTED }}>COVERAGE</div>
              <div style={{ fontSize: 44, fontWeight: 800, color: coverage >= 100 ? GREEN : INK, fontVariantNumeric: 'tabular-nums' }}>{coverage}%</div>
              <div style={{ height: 10, borderRadius: 5, background: LINE }}><div style={{ height: '100%', width: `${coverage}%`, borderRadius: 5, background: coverage >= 100 ? GREEN : PB }} /></div>
            </div>
          </div>
          {/* canvas */}
          <div style={{ position: 'absolute', left: SIDE_W, top: 116, width: CANVAS_W, bottom: 0, backgroundColor: '#FBFCFE',
            backgroundImage: 'radial-gradient(#DCE5EE 1.4px, transparent 1.4px)', backgroundSize: '28px 28px' }} />
        </div>

        {/* board, jar, slices: drawn in screen pixels */}
        <svg width={1920} height={1080} style={{ position: 'absolute', left: 0, top: 0, overflow: 'visible' }}>
          <defs>
            <mask id="paint" maskUnits="userSpaceOnUse" x={-400} y={-400} width={800} height={800}>
              {strokes.map((p, i) => <circle key={i} cx={p.x - A.x} cy={p.y - A.y} r={58} fill="#fff" />)}
            </mask>
            <clipPath id="half-0"><path d="M -400 -400 L 400 -400 L 400 400 Z" /></clipPath>
            <clipPath id="half-1"><path d="M -400 -400 L 400 400 L -400 400 Z" /></clipPath>
            <clipPath id="slice-in"><path d={OUT} transform="translate(-4 -8)" /></clipPath>
          </defs>
          <rect x={CANVAS_X + 90} y={BODY_Y + 210} width={CANVAS_W - 180} height={540} rx={34} fill={WOOD} />
          <rect x={CANVAS_X + 90} y={BODY_Y + 210} width={CANVAS_W - 180} height={540} rx={34} fill="none" stroke={WOOD_D} strokeWidth={6} />
          {[0, 1, 2, 3, 4].map((i) => <path key={i} d={`M ${CANVAS_X + 130} ${BODY_Y + 280 + i * 100} Q ${CANVAS_X + 510} ${BODY_Y + 260 + i * 100 + (i % 2 ? 24 : -18)} ${CANVAS_X + CANVAS_W - 130} ${BODY_Y + 286 + i * 100}`}
            stroke={WOOD_D} strokeWidth={3} fill="none" opacity={0.35} />)}
          {/* jar */}
          {f >= 96 && jarGone < 1 ? (
            <g transform={`translate(${JAR.x} ${JAR.y}) scale(${(0.7 + 0.3 * landJar) * (1 - jarGone)})`}><JarArt dent={scoop} /></g>
          ) : null}
          {/* slice A, painted, then the whole sandwich */}
          {sliceA ? (
            <g transform={`translate(${A.x} ${A.y}) scale(${0.85 + 0.15 * landA})`}>
              {split <= 0 ? <Sandwich /> : (
                <>
                  <g transform={`translate(${-26 * split} ${26 * split})`}><Sandwich half={1} /></g>
                  <g transform={`translate(${26 * split} ${-26 * split})`}><Sandwich half={0} /></g>
                </>
              )}
            </g>
          ) : null}
          {/* slice B waiting, then dragged on top */}
          {sliceB && !onTop && !dragBTop ? <g transform={`translate(${B.x} ${B.y}) scale(${0.85 + 0.15 * landB})`}><SliceArt sel={f >= 212 && f < 216} /></g> : null}
          {/* cut line while dragging */}
          {cutting || (f > 306 && split < 0.3) ? (
            <line x1={A.x - SL / 2 - 6} y1={A.y - SL / 2 - 6} x2={cutting ? cur.x : A.x + SL / 2 + 6} y2={cutting ? cur.y : A.y + SL / 2 + 6}
              stroke={BLUE} strokeWidth={4} strokeDasharray="10 8" />
          ) : null}
          {/* hold-to-press ring */}
          {f >= 250 && f < 270 ? (
            <g transform={`translate(${cur.x} ${cur.y})`} opacity={1 - prog(f, 264, 270)}>
              <circle r={44} fill="none" stroke="rgba(10,132,198,.25)" strokeWidth={8} />
              <circle r={44} fill="none" stroke={BLUE} strokeWidth={8} strokeDasharray={2 * Math.PI * 44} strokeDashoffset={2 * Math.PI * 44 * (1 - hold)} transform="rotate(-90)" strokeLinecap="round" />
            </g>
          ) : null}
          {/* things being dragged follow the cursor */}
          {dragA || dragB ? <g transform={`translate(${cur.x} ${cur.y}) rotate(-4) scale(0.9)`} opacity={0.92}><SliceArt /></g> : null}
          {dragJar ? <g transform={`translate(${cur.x} ${cur.y}) rotate(-4) scale(0.9)`} opacity={0.92}><JarArt /></g> : null}
          {dragBTop ? <g transform={`translate(${cur.x - 8} ${cur.y - 8}) rotate(-3)`}><SliceArt sel /></g> : null}
          {dragBTop && f > 236 ? (
            <g opacity={0.9}>
              <line x1={A.x} y1={A.y - 200} x2={A.x} y2={A.y + 200} stroke="#E11D48" strokeWidth={2} />
              <line x1={A.x - 200} y1={A.y} x2={A.x + 200} y2={A.y} stroke="#E11D48" strokeWidth={2} />
            </g>
          ) : null}
          {/* tooltip after the scoop */}
          {f >= 118 && f < 140 ? (
            <g transform={`translate(${JAR.x + 60} ${JAR.y - 150})`} opacity={clamp(pop(f, 118)) * (1 - prog(f, 134, 140))}>
              <rect x={0} y={-24} width={170} height={48} rx={10} fill={INK} />
              <text x={85} y={8} textAnchor="middle" fontFamily={SANS} fontWeight={700} fontSize={20} fill="#fff">1 scoop ✓</text>
            </g>
          ) : null}
          {/* coverage chip at the slice when it hits 100 % */}
          {f >= at(K.edges) && f < 200 ? (
            <g transform={`translate(${A.x} ${A.y + SL / 2 + 46}) scale(${pop(f, at(K.edges))})`} opacity={1 - prog(f, 190, 200)}>
              <rect x={-120} y={-24} width={240} height={48} rx={24} fill={GREEN} />
              <text x={0} y={8} textAnchor="middle" fontFamily={SANS} fontWeight={800} fontSize={21} fill="#fff">100% · to the edges</text>
            </g>
          ) : null}
        </svg>

        {/* the toast */}
        {f >= at(K.because) - 2 ? (
          <div style={{ position: 'absolute', left: 1000, top: 230, width: 440, padding: '20px 22px', borderRadius: 16, background: '#fff', boxShadow: '0 24px 60px rgba(7,26,46,.30)',
            border: `1px solid ${LINE}`, transform: `translateY(${(1 - toast) * -40}px)`, opacity: clamp(toast * 1.4) }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: 12 }}>
              <svg width={42} height={42} viewBox="-21 -21 42 42"><path d="M -16 16 L 16 16 L -16 -16 Z" fill={CRUST} stroke={PB} strokeWidth={3} /></svg>
              <div>
                <div style={{ fontSize: 22, fontWeight: 800, color: INK }}>2 triangles ready</div>
                <div style={{ fontSize: 17, color: MUTED, marginTop: 2 }}>Taste: <span style={{ color: GREEN, fontWeight: 700 }}>{f >= at(K.taste) - 2 ? 'better ↑' : '…'}</span></div>
              </div>
            </div>
            <div style={{ display: 'flex', justifyContent: 'flex-end', marginTop: 14 }}>
              <div style={{ padding: '10px 26px', borderRadius: 10, background: served ? GREEN : BLUE, color: '#fff', fontWeight: 700, fontSize: 19,
                transform: `scale(${f >= 360 && f < 366 ? 0.94 : 1})` }}>{served ? 'Served ✓' : 'Serve'}</div>
            </div>
          </div>
        ) : null}

        {/* confetti from the Serve button */}
        {served ? (
          <svg width={1920} height={1080} style={{ position: 'absolute', left: 0, top: 0, overflow: 'visible', pointerEvents: 'none' }}>
            {Array.from({ length: 46 }).map((_, i) => {
              const a = rand(i) * Math.PI * 2, v = 9 + rand(i + 50) * 13, t = confetti;
              const x = 1362 + Math.cos(a) * v * t, y = 336 + Math.sin(a) * v * t + 0.32 * t * t;
              const c = [BLUE, '#E11D48', '#F5B301', GREEN, PB][i % 5];
              return <rect key={i} x={x} y={y} width={12} height={7} rx={2} fill={c} transform={`rotate(${t * 12 + i * 37} ${x} ${y})`} opacity={1 - clamp((t - 40) / 30)} />;
            })}
          </svg>
        ) : null}

        {/* click ripples and the cursor */}
        <svg width={1920} height={1080} style={{ position: 'absolute', left: 0, top: 0, overflow: 'visible', pointerEvents: 'none' }}>
          {CLICKS.filter((c) => f >= c && f < c + 12).map((c) => {
            const p = cursorAt(c), t = (f - c) / 12;
            return <circle key={c} cx={p.x} cy={p.y} r={10 + 34 * easeOut(t)} fill="none" stroke={BLUE} strokeWidth={5 * (1 - t)} opacity={1 - t} />;
          })}
          <g transform={`translate(${cur.x} ${cur.y})`}><Cursor kind={tool === 'arrow' ? 'arrow' : tool} pressed={pressed} blob={blob} /></g>
        </svg>
      </AbsoluteFill>
      <Soundtrack sfx={SFX} />
    </AbsoluteFill>
  );
};

const SFX: Sfx[] = [
  ...CLICKS.map((c) => ({ at: c - 1, file: 'mclick.wav', vol: 0.45 })),
  { at: 43, file: 'card.wav', vol: 0.25 }, { at: 68, file: 'card.wav', vol: 0.25 }, { at: 96, file: 'card2.wav', vol: 0.25 },
  { at: 116, file: 'pop2.wav', vol: 0.25 },
  { at: 138, file: 'paper.wav', vol: 0.25, dur: 40 },
  { at: at(K.edges), file: 'confirm.wav', vol: 0.3 },
  ...[60, 124, 186, 266, 320].map((d) => ({ at: d, file: 'tick.wav', vol: 0.3 })),
  { at: 248, file: 'card2.wav', vol: 0.3 }, { at: 264, file: 'thud.wav', vol: 0.35 },
  { at: 304, file: 'whip.wav', vol: 0.3 },
  { at: at(K.because) - 2, file: 'blip.wav', vol: 0.3 },
  { at: 362, file: 'sparkle.wav', vol: 0.25 },
  { at: 22, file: 'swipe2.wav', vol: 0.12 }, { at: 134, file: 'swipe2.wav', vol: 0.12 }, { at: 390, file: 'swipe1.wav', vol: 0.15 },
];
