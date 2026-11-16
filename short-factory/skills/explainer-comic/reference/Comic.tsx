// Style 6: COMIC. One comic page, six panels (made on the free local picture maker in one consistent ink-and-halftone
// look, hands only). The camera reads the page panel by panel with quick comic-style moves; each panel has a yellow
// narration box typed word by word with the voice, and a big sound-effect word (FLOP! SHLUK! SWOOSH! SMOOSH! SHHNK! YUM!).
// At the end the camera pulls back to show the whole page.
import React from 'react';
import { AbsoluteFill, Easing, Img, interpolate, staticFile, useCurrentFrame } from 'remotion';
import { Soundtrack, Sfx } from '../../shared/Soundtrack';
import { ensureFonts } from '../../shared/fonts';
import { WORDS, K, at } from '../../shared/timing';
import { clamp, mix, pop, prog } from '../../shared/anim';

ensureFonts('Bangers', 'Comic Neue');
const INK = '#111111', PAPER = '#FBF5E6', CAPTION = '#FFE45C';

// ---------- the page (page px) ----------
type Panel = { img: string; custom?: 'cut' | 'tri'; x: number; y: number; w: number; h: number; clip?: string; words: [number, number]; sfx: string; sfxAt: number;
  sfxPos: [number, number]; sfxRot: number; sfxColor: string; fx?: number; fy?: number };
const PANELS: Panel[] = [
  { img: 'cm_1_bread', x: 40, y: 40, w: 640, h: 700, words: [0, 4], sfx: 'FLOP!', sfxAt: at(K.slices) - 2, sfxPos: [470, 560], sfxRot: -12, sfxColor: '#FF5A36' },
  { img: 'cm_2_knife', x: 710, y: 40, w: 640, h: 700, words: [5, 12], sfx: 'SHLUK!', sfxAt: at(K.into) - 2, sfxPos: [150, 540], sfxRot: 10, sfxColor: '#FFB020' },
  { img: 'cm_3_spread', x: 1380, y: 40, w: 980, h: 700, words: [13, 19], sfx: 'SWOOSH!', sfxAt: at(K.spread) - 2, sfxPos: [720, 560], sfxRot: -8, sfxColor: '#36B5FF', fx: 0.5 },
  { img: 'cm_4_press', x: 40, y: 770, w: 640, h: 700, words: [20, 25], sfx: 'SMOOSH!', sfxAt: at(K.top) - 2, sfxPos: [330, 610], sfxRot: 8, sfxColor: '#FF5A36' },
  { img: 'cm_7_topdown', custom: 'cut', x: 710, y: 770, w: 760, h: 700, clip: 'polygon(0 0, 100% 0, 92% 100%, 0 100%)', words: [26, 31], sfx: 'SHHNK!', sfxAt: at(K.corner2) - 2,
    sfxPos: [560, 600], sfxRot: -14, sfxColor: '#FFB020' },
  { img: 'cm_7_topdown', custom: 'tri', x: 1440, y: 770, w: 920, h: 700, clip: 'polygon(7% 0, 100% 0, 100% 100%, 0 100%)', words: [32, 35], sfx: 'YUM!', sfxAt: at(K.better),
    sfxPos: [760, 600], sfxRot: -10, sfxColor: '#FF3D7F' },
];
const PAGE = { w: 2400, h: 1510 };

// camera per panel: centre + zoom so the panel fills the frame
const camFor = (p: Panel) => ({ x: p.x + p.w / 2, y: p.y + p.h / 2, z: Math.min(1920 / (p.w + 70), 1080 / (p.h + 70)), r: 0 });
const KEYS: { f: number; c: { x: number; y: number; z: number; r: number } }[] = [
  { f: 0, c: { ...camFor(PANELS[0]), z: camFor(PANELS[0]).z * 1.12 } }, { f: 64, c: camFor(PANELS[0]) },
  { f: 74, c: { ...camFor(PANELS[1]), r: 1.5 } }, { f: 126, c: { ...camFor(PANELS[1]), r: 0, z: camFor(PANELS[1]).z * 1.04 } },
  { f: 136, c: { ...camFor(PANELS[2]), r: -1.5 } }, { f: 204, c: { ...camFor(PANELS[2]), r: 0, z: camFor(PANELS[2]).z * 1.05 } },
  { f: 216, c: { ...camFor(PANELS[3]), r: 2 } }, { f: 266, c: { ...camFor(PANELS[3]), r: 0, z: camFor(PANELS[3]).z * 1.05 } },
  { f: 276, c: { ...camFor(PANELS[4]), r: -2 } }, { f: 324, c: { ...camFor(PANELS[4]), r: 0, z: camFor(PANELS[4]).z * 1.06 } },
  { f: 334, c: { ...camFor(PANELS[5]), r: 1.5 } }, { f: 384, c: { ...camFor(PANELS[5]), r: 0, z: camFor(PANELS[5]).z * 1.05 } },
  { f: 408, c: { x: PAGE.w / 2, y: PAGE.h / 2, z: Math.min(1920 / (PAGE.w + 60), 1080 / (PAGE.h + 60)), r: 0 } },
  { f: 450, c: { x: PAGE.w / 2, y: PAGE.h / 2, z: Math.min(1920 / (PAGE.w + 60), 1080 / (PAGE.h + 60)) * 0.98, r: 0 } },
];
const camAt = (f: number) => {
  let i = 0;
  while (i < KEYS.length - 2 && f >= KEYS[i + 1].f) i++;
  const a = KEYS[i], b = KEYS[i + 1];
  const move = b.f - a.f <= 26;
  const t = interpolate(f, [a.f, b.f], [0, 1], { extrapolateLeft: 'clamp', extrapolateRight: 'clamp', easing: move ? Easing.bezier(0.8, 0, 0.2, 1) : (x) => x });
  const z = Math.exp(mix(t, Math.log(a.c.z), Math.log(b.c.z)));
  // never look past the edge of the page: tall panels sit to one side and the next panel peeks in
  const hw = 960 / z, hh = 540 / z, m = 24;
  const cx = PAGE.w + 2 * m > 2 * hw ? clamp(mix(t, a.c.x, b.c.x), hw - m, PAGE.w - hw + m) : PAGE.w / 2;
  const cy = PAGE.h + 2 * m > 2 * hh ? clamp(mix(t, a.c.y, b.c.y), hh - m, PAGE.h - hh + m) : PAGE.h / 2;
  return { x: cx, y: cy, z, r: mix(t, a.c.r, b.c.r) };
};

// ---------- the top-down sandwich (cm_7) and its cut-out (cm_7_sandwich, cut from the same picture) ----------
// sandwich corners in the 1328 px picture (top-left and bottom-right of the whole sandwich, crust included)
const SW = { x0: 190, y0: 130, x1: 1160, y1: 1160 };
// the cut-out was cropped from the picture at (162, 110) and is 1021 x 1078
const CUT = { x: 162, y: 110, w: 1021, h: 1078 };
// the cut runs from the sandwich's top-left corner to its bottom-right corner; in the cut-out's own pixels:
const P1 = [SW.x0 - CUT.x, SW.y0 - CUT.y], P2 = [SW.x1 - CUT.x, SW.y1 - CUT.y];
const D = [P2[0] - P1[0], P2[1] - P1[1]];
const pct = (x: number, y: number) => `${(x / CUT.w) * 100}% ${(y / CUT.h) * 100}%`;
const HALF_UR = `polygon(${pct(P1[0] - D[0], P1[1] - D[1])}, ${pct(P2[0] + D[0], P2[1] + D[1])}, ${pct(4000, -4000)})`;
const HALF_LL = `polygon(${pct(P1[0] - D[0], P1[1] - D[1])}, ${pct(P2[0] + D[0], P2[1] + D[1])}, ${pct(-4000, 4000)})`;
const NORMAL = (() => { const l = Math.hypot(D[0], D[1]); return [D[1] / l, -D[0] / l]; })(); // points to the upper-right half

// the picture laid out in a panel like objectFit: cover (inner size w x h)
const coverOf = (w: number, h: number) => { const k = Math.max(w / 1328, h / 1328); return { k, ox: (w - 1328 * k) / 2, oy: (h - 1328 * k) / 2 }; };

// one triangle half of the cut-out, placed at (x, y) with scale k (cut-out px -> panel px)
const Half: React.FC<{ which: 'ur' | 'll'; x: number; y: number; k: number; dx: number; dy: number; rot?: number; shadow?: boolean }> = ({ which, x, y, k, dx, dy, rot = 0, shadow }) => (
  <div style={{ position: 'absolute', left: x + dx, top: y + dy, width: CUT.w * k, height: CUT.h * k, transform: `rotate(${rot}deg)`,
    transformOrigin: `${((P1[0] + P2[0]) / 2 / CUT.w) * 100}% ${((P1[1] + P2[1]) / 2 / CUT.h) * 100}%`,
    filter: shadow ? 'drop-shadow(10px 12px 0 rgba(17,17,17,.85))' : undefined }}>
    <Img src={staticFile('img/comic/cm_7_sandwich.png')} style={{ width: '100%', height: '100%', clipPath: which === 'ur' ? HALF_UR : HALF_LL }} />
    {/* the peanut butter shows along the cut edge */}
    <svg width={CUT.w * k} height={CUT.h * k} viewBox={`0 0 ${CUT.w} ${CUT.h}`} style={{ position: 'absolute', left: 0, top: 0, overflow: 'visible', clipPath: which === 'ur' ? HALF_UR : HALF_LL }}>
      <line x1={P1[0] + D[0] * 0.05} y1={P1[1] + D[1] * 0.05} x2={P1[0] + D[0] * 0.95} y2={P1[1] + D[1] * 0.95} stroke={INK} strokeWidth={34} strokeLinecap="round" />
      <line x1={P1[0] + D[0] * 0.05} y1={P1[1] + D[1] * 0.05} x2={P1[0] + D[0] * 0.95} y2={P1[1] + D[1] * 0.95} stroke="#D08A35" strokeWidth={22} strokeLinecap="round" />
    </svg>
  </div>
);

// panel 5: the knife slash goes corner to corner across the sandwich, which then splits on the board
const CutPanel: React.FC<{ p: Panel; f: number }> = ({ p, f }) => {
  const w = p.w - 14, h = p.h - 14, c = coverOf(w, h);
  const slash = prog(f, at(K.corner1) - 2, at(K.corner2) + 2, Easing.out(Easing.quad));
  const fade = prog(f, at(K.corner2) + 4, at(K.corner2) + 14);
  const part = prog(f, at(K.corner2) + 2, at(K.corner2) + 12, Easing.out(Easing.back(1.6)));
  const a = [c.ox + SW.x0 * c.k, c.oy + SW.y0 * c.k], b = [c.ox + SW.x1 * c.k, c.oy + SW.y1 * c.k];
  const cx = c.ox + CUT.x * c.k, cy = c.oy + CUT.y * c.k, ck = c.k;
  const sep = 16 * part;
  return (
    <>
      <Img src={staticFile('img/comic/cm_7_topdown.png')} style={{ position: 'absolute', left: c.ox, top: c.oy, width: 1328 * c.k, height: 1328 * c.k }} />
      {part > 0 ? (
        <>
          {/* the uncut sandwich is covered by its own dark silhouette, so the gap between the halves reads as shadow on the board */}
          <Img src={staticFile('img/comic/cm_7_sandwich.png')} style={{ position: 'absolute', left: cx, top: cy, width: CUT.w * ck, height: CUT.h * ck, filter: 'brightness(0.22) sepia(0.6)' }} />
          <Half which="ll" x={cx} y={cy} k={ck} dx={-NORMAL[0] * sep} dy={-NORMAL[1] * sep} rot={-2 * part} />
          <Half which="ur" x={cx} y={cy} k={ck} dx={NORMAL[0] * sep} dy={NORMAL[1] * sep} rot={2 * part} />
        </>
      ) : null}
      {slash > 0 && fade < 1 ? (
        <svg width={w} height={h} style={{ position: 'absolute', left: 0, top: 0, overflow: 'visible', opacity: 1 - fade }}>
          {/* speed lines along the cut */}
          {[-36, -18, 18, 36].map((o, i) => (
            <line key={i} x1={a[0] - 60 + NORMAL[0] * o} y1={a[1] - 60 + NORMAL[1] * o} x2={mix(slash, a[0], b[0]) + NORMAL[0] * o} y2={mix(slash, a[1], b[1]) + NORMAL[1] * o}
              stroke={INK} strokeWidth={3} opacity={0.6} />
          ))}
          <line x1={a[0] - 40} y1={a[1] - 40} x2={mix(slash, a[0], b[0] + 30)} y2={mix(slash, a[1], b[1] + 30)} stroke={INK} strokeWidth={26} strokeLinecap="round" />
          <line x1={a[0] - 40} y1={a[1] - 40} x2={mix(slash, a[0], b[0] + 30)} y2={mix(slash, a[1], b[1] + 30)} stroke="#FFFFFF" strokeWidth={14} strokeLinecap="round" />
          <line x1={a[0] - 40} y1={a[1] - 40} x2={mix(slash, a[0], b[0] + 30)} y2={mix(slash, a[1], b[1] + 30)} stroke="#9BE3FF" strokeWidth={5} strokeLinecap="round" />
        </svg>
      ) : null}
    </>
  );
};

// panel 6: the two triangles on a comic sunburst
const TriPanel: React.FC<{ p: Panel; f: number }> = ({ p, f }) => {
  const w = p.w - 14, h = p.h - 14;
  const k = (h * 0.6) / CUT.h;
  const x = (w - CUT.w * k) / 2 + 20, y = (h - CUT.h * k) / 2 + 40;
  const inn = pop(f, at(K.because) - 6, { damping: 12, stiffness: 160 });
  const spin = (f - at(K.because)) * 0.25;
  return (
    <>
      <svg width={w} height={h} style={{ position: 'absolute', left: 0, top: 0 }}>
        <rect width={w} height={h} fill="#FFC93C" />
        {Array.from({ length: 18 }).map((_, i) => {
          const a0 = ((i / 18) * 360 + spin) * Math.PI / 180, a1 = (((i + 0.5) / 18) * 360 + spin) * Math.PI / 180, R = 1200;
          return <path key={i} d={`M ${w / 2} ${h / 2} L ${w / 2 + Math.cos(a0) * R} ${h / 2 + Math.sin(a0) * R} L ${w / 2 + Math.cos(a1) * R} ${h / 2 + Math.sin(a1) * R} Z`} fill="#FF8A1F" opacity={0.85} />;
        })}
        <circle cx={w / 2} cy={h / 2} r={180} fill="#FFE27A" opacity={0.9} />
      </svg>
      <div style={{ position: 'absolute', inset: 0, backgroundImage: 'radial-gradient(rgba(150,60,0,.25) 2px, transparent 2.6px)', backgroundSize: '12px 12px' }} />
      <Half which="ll" x={x} y={y} k={k * (0.7 + 0.3 * inn)} dx={-NORMAL[0] * 70} dy={-NORMAL[1] * 70} rot={-11} shadow />
      <Half which="ur" x={x} y={y} k={k * (0.7 + 0.3 * inn)} dx={NORMAL[0] * 70} dy={NORMAL[1] * 70} rot={9} shadow />
      {[[0.16, 0.2], [0.86, 0.22], [0.12, 0.78], [0.9, 0.7]].map(([sx, sy], i) => {
        const t = ((f + i * 9) % 36) / 36;
        return <svg key={i} width={70} height={70} viewBox="-35 -35 70 70" style={{ position: 'absolute', left: sx * w - 35, top: sy * h - 35, transform: `scale(${Math.sin(t * Math.PI)})` }}>
          <path d="M 0 -32 L 7 -7 L 32 0 L 7 7 L 0 32 L -7 7 L -32 0 L -7 -7 Z" fill="#FFFFFF" stroke={INK} strokeWidth={4} />
        </svg>;
      })}
    </>
  );
};

// the narration box: the panel's words, typed in as they are spoken
const Caption: React.FC<{ p: Panel; f: number }> = ({ p, f }) => {
  const [w0, w1] = p.words;
  const shown = WORDS.slice(w0, w1 + 1).filter((w) => f >= w.fs - 2).map((w) => w.w.toUpperCase());
  if (!shown.length) return null;
  const lead = w0 > 0 && p.words[0] !== 20 ? '…' : ''; // the second sentence starts at word 20
  const box = pop(f, WORDS[w0].fs - 4, { damping: 14, stiffness: 220 });
  return (
    <div style={{ position: 'absolute', left: 22, top: 22, maxWidth: p.w * 0.72, background: CAPTION, border: `5px solid ${INK}`, padding: '12px 18px',
      fontFamily: 'Comic Neue', fontWeight: 700, fontSize: 40, lineHeight: 1.12, color: INK, letterSpacing: '0.02em', boxShadow: '6px 6px 0 rgba(0,0,0,.85)',
      transform: `scale(${0.85 + 0.15 * box})`, transformOrigin: '0 0', opacity: clamp(box * 2) }}>
      {lead}{shown.join(' ')}
    </div>
  );
};

const SfxWord: React.FC<{ p: Panel; f: number }> = ({ p, f }) => {
  const t = f - p.sfxAt;
  if (t < 0) return null;
  const s = pop(f, p.sfxAt, { damping: 7, stiffness: 260, mass: 0.6 });
  const shake = t < 10 ? Math.sin(t * 2.6) * (10 - t) * 0.6 : 0;
  return (
    <div style={{ position: 'absolute', left: p.sfxPos[0], top: p.sfxPos[1], transform: `translate(-50%, -50%) rotate(${p.sfxRot + shake}deg) scale(${s})`,
      fontFamily: 'Bangers', fontSize: p.sfx.length > 5 ? 120 : 140, color: p.sfxColor, letterSpacing: '0.04em', whiteSpace: 'nowrap',
      WebkitTextStroke: `10px ${INK}`, paintOrder: 'stroke fill', textShadow: `8px 8px 0 ${INK}` }}>{p.sfx}</div>
  );
};

export const Comic: React.FC = () => {
  const f = useCurrentFrame();
  const cam = camAt(f);
  const prev = camAt(Math.max(0, f - 1));
  const speed = Math.hypot(cam.x - prev.x, cam.y - prev.y) * cam.z;
  const blur = f < 395 ? Math.min(6, speed / 40) : 0;
  const end = prog(f, 410, 426, Easing.out(Easing.back(1.8)));
  return (
    <AbsoluteFill style={{ background: '#1E1E1E', overflow: 'hidden' }}>
      <AbsoluteFill style={{ transform: `translate(960px, 540px) rotate(${cam.r}deg) scale(${cam.z}) translate(${-cam.x}px, ${-cam.y}px)`, transformOrigin: '0 0',
        filter: blur > 0.3 ? `blur(${blur}px)` : undefined }}>
        <div style={{ position: 'absolute', left: 0, top: 0, width: PAGE.w, height: PAGE.h, background: PAPER, boxShadow: '0 30px 80px rgba(0,0,0,.5)' }}>
          {/* paper grain dots */}
          <div style={{ position: 'absolute', inset: 0, backgroundImage: 'radial-gradient(rgba(120,90,40,.10) 1px, transparent 1.2px)', backgroundSize: '9px 9px' }} />
          {PANELS.map((p, i) => {
            const enter = prog(f, i === 0 ? 0 : KEYS[i * 2].f - 10, (i === 0 ? 0 : KEYS[i * 2].f - 10) + 60, (x) => x);
            return (
              <div key={p.img} style={{ position: 'absolute', left: p.x, top: p.y, width: p.w, height: p.h, clipPath: p.clip, background: INK, padding: 7 }}>
                <div style={{ position: 'relative', width: '100%', height: '100%', overflow: 'hidden', clipPath: p.clip }}>
                  {p.custom === 'cut' ? <CutPanel p={p} f={f} /> : p.custom === 'tri' ? <TriPanel p={p} f={f} /> : (
                    <Img src={staticFile(`img/comic/${p.img}.png`)} style={{ width: '100%', height: '100%', objectFit: 'cover', objectPosition: `${(p.fx ?? 0.5) * 100}% ${(p.fy ?? 0.5) * 100}%`,
                      transform: `scale(${1.04 + 0.06 * enter})` }} />
                  )}
                  {/* halftone dots over the panel for the printed look */}
                  <div style={{ position: 'absolute', inset: 0, backgroundImage: 'radial-gradient(rgba(0,0,0,.18) 1.2px, transparent 1.6px)', backgroundSize: '7px 7px', mixBlendMode: 'multiply' }} />
                  <Caption p={p} f={f} />
                  <SfxWord p={p} f={f} />
                </div>
              </div>
            );
          })}
          {/* the page title strip across the top gutter */}
          <div style={{ position: 'absolute', left: 0, right: 0, top: -10, textAlign: 'center', fontFamily: 'Bangers', fontSize: 34, color: INK, letterSpacing: '0.12em' }} />
        </div>
      </AbsoluteFill>
      {/* the ending stamp */}
      {f >= 408 ? (
        <div style={{ position: 'absolute', left: 960, top: 540, transform: `translate(-50%, -50%) rotate(-8deg) scale(${end})`, background: CAPTION,
          border: `8px solid ${INK}`, boxShadow: '12px 12px 0 #111', padding: '18px 44px', fontFamily: 'Bangers', fontSize: 96, letterSpacing: '0.05em', color: INK, whiteSpace: 'nowrap' }}>
          TRIANGLES TASTE BETTER!
        </div>
      ) : null}
      <Soundtrack sfx={SFX} />
    </AbsoluteFill>
  );
};

const SFX: Sfx[] = [
  ...[66, 128, 206, 268, 326].map((t) => ({ at: t, file: 'page.wav', vol: 0.35 })),
  { at: PANELS[0].sfxAt, file: 'card.wav', vol: 0.4 }, { at: PANELS[1].sfxAt, file: 'smack.wav', vol: 0.45 },
  { at: PANELS[2].sfxAt, file: 'swish1.wav', vol: 0.35 }, { at: PANELS[3].sfxAt, file: 'thud.wav', vol: 0.45 },
  { at: PANELS[4].sfxAt, file: 'whip.wav', vol: 0.5 }, { at: PANELS[5].sfxAt, file: 'sparkle.wav', vol: 0.3 },
  { at: 386, file: 'whoosh.wav', vol: 0.35 }, { at: 410, file: 'thud.wav', vol: 0.35 },
];
