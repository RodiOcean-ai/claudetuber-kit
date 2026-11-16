// Style 5: WHITEBOARD. Six marker drawings (made on the free local picture maker, then traced into pen strokes) are drawn
// stroke by stroke by a real-looking hand on a big whiteboard, coloured in with a marker sweep, and labelled in blue
// marker handwriting. The camera moves from drawing to drawing along the board; at the end it pulls back to show the
// whole recipe board, arrows join the steps, and a red circle lands on the triangles.
import React from 'react';
import { AbsoluteFill, Easing, Img, interpolate, staticFile, useCurrentFrame } from 'remotion';
import { Soundtrack, Sfx } from '../../shared/Soundtrack';
import { ensureFonts } from '../../shared/fonts';
import { clamp, easeInOut, mix, prog } from '../../shared/anim';
import breadS from '../../../public/img/wb/wb_bread.strokes.json';
import jarS from '../../../public/img/wb/wb_jar.strokes.json';
import spreadS from '../../../public/img/wb/wb_spread.strokes.json';
import stackS from '../../../public/img/wb/wb_stack.strokes.json';
import cutS from '../../../public/img/wb/wb_cut.strokes.json';
import halvesS from '../../../public/img/wb/wb_halves.strokes.json';

ensureFonts('Permanent Marker');
const INKC = '#1C1C1E', BLUE = '#1E5BB8', RED = '#D62F2F';
const MARKER = 'Permanent Marker';

type Strokes = { w: number; h: number; strokeWidth: number; strokes: number[][]; widths?: number[] };
type Pt = [number, number];

// ---------- the board: six cells in a snake (1 2 3 / 6 5 4) ----------
const SIZE = 560; // drawing size on the board (board px)
const CELLS: Pt[] = [[400, 380], [1200, 380], [2000, 380], [2000, 1110], [1200, 1110], [400, 1110]];
type D = { name: string; s: Strokes; draw: [number, number]; color: [number, number]; label: string; write: [number, number] };
const DRAW: D[] = [
  { name: 'bread', s: breadS as Strokes, draw: [12, 48], color: [48, 58], label: '2 slices', write: [50, 62] },
  { name: 'jar', s: jarS as Strokes, draw: [68, 108], color: [108, 116], label: 'dig in!', write: [110, 122] },
  { name: 'spread', s: spreadS as Strokes, draw: [128, 166], color: [168, 180], label: 'to the edges!', write: [176, 192] },
  { name: 'stack', s: stackS as Strokes, draw: [206, 240], color: [240, 248], label: 'press it down', write: [244, 258] },
  { name: 'cut', s: cutS as Strokes, draw: [268, 294], color: [296, 304], label: 'corner to corner', write: [300, 316] },
  { name: 'halves', s: halvesS as Strokes, draw: [330, 354], color: [354, 362], label: 'triangles taste better!', write: [356, 376] },
];

// a drawing as one path for the pen: strokes in order, with pen-up travel between them (so the hand never teleports)
type Seg = { pts: Pt[]; len: number; draw: boolean; width: number; cum: number[] };
const prep = (s: Strokes) => {
  const k = SIZE / s.w;
  const segs: Seg[] = [];
  let last: Pt | null = null;
  s.strokes.forEach((arr, i) => {
    const pts: Pt[] = [];
    for (let j = 0; j < arr.length; j += 2) pts.push([arr[j] * k, arr[j + 1] * k]);
    if (last) {
      const d = Math.hypot(pts[0][0] - last[0], pts[0][1] - last[1]);
      segs.push({ pts: [last, pts[0]], len: d * 0.35, draw: false, width: 0, cum: [0, d * 0.35] });
    }
    const cum = [0];
    for (let j = 1; j < pts.length; j++) cum.push(cum[j - 1] + Math.hypot(pts[j][0] - pts[j - 1][0], pts[j][1] - pts[j - 1][1]));
    segs.push({ pts, len: cum[cum.length - 1], draw: true, width: Math.max(2.2, (s.widths?.[i] ?? s.strokeWidth) * k), cum });
    last = pts[pts.length - 1];
  });
  const total = segs.reduce((a, x) => a + x.len, 0);
  return { segs, total };
};
const PREP = DRAW.map((d) => prep(d.s));
const pointAt = (seg: Seg, l: number): Pt => {
  if (seg.pts.length < 2) return seg.pts[0];
  if (!seg.draw) { const t = seg.len > 0 ? l / seg.len : 1; return [mix(t, seg.pts[0][0], seg.pts[1][0]), mix(t, seg.pts[0][1], seg.pts[1][1])]; }
  let j = 1;
  while (j < seg.cum.length - 1 && seg.cum[j] < l) j++;
  const a = seg.cum[j - 1], b = seg.cum[j];
  const t = b > a ? (l - a) / (b - a) : 0;
  return [mix(t, seg.pts[j - 1][0], seg.pts[j][0]), mix(t, seg.pts[j - 1][1], seg.pts[j][1])];
};

const Drawing: React.FC<{ i: number; f: number }> = ({ i, f }) => {
  const d = DRAW[i], { segs, total } = PREP[i];
  const p = prog(f, d.draw[0], d.draw[1], (t) => t);
  const col = prog(f, d.color[0], d.color[1], easeInOut);
  if (p <= 0) return null;
  let left = p * total;
  return (
    <>
      {/* the coloured version (lines included) sweeps in when the drawing is done */}
      {col > 0 ? (
        <Img src={staticFile(`img/wb/wb_${d.name}_color.png`)} style={{ position: 'absolute', left: 0, top: 0, width: SIZE, height: SIZE, mixBlendMode: 'multiply',
          WebkitMaskImage: `linear-gradient(110deg, #000 ${col * 130 - 30}%, transparent ${col * 130}%)`, maskImage: `linear-gradient(110deg, #000 ${col * 130 - 30}%, transparent ${col * 130}%)` }} />
      ) : null}
      <svg width={SIZE} height={SIZE} style={{ position: 'absolute', left: 0, top: 0, overflow: 'visible', opacity: 1 - col }}>
        {segs.map((s, k) => {
          if (!s.draw) { left -= s.len; return null; }
          const vis = Math.max(0, Math.min(s.len, left));
          left -= s.len;
          if (vis <= 0) return null;
          return (
            <polyline key={k} points={s.pts.map((q) => q.join(',')).join(' ')} fill="none" stroke={INKC} strokeWidth={s.width}
              strokeLinecap="round" strokeLinejoin="round" strokeDasharray={`${s.len + 1} ${s.len + 1}`} strokeDashoffset={s.len - vis} />
          );
        })}
      </svg>
    </>
  );
};

// where the pen is (board px) at a frame, and whether it is touching the board
const penAt = (f: number): { p: Pt; down: boolean } | null => {
  for (let i = 0; i < DRAW.length; i++) {
    const d = DRAW[i], c = CELLS[i];
    const o: Pt = [c[0] - SIZE / 2, c[1] - SIZE / 2 - 40];
    if (f >= d.draw[0] && f <= d.draw[1]) {
      const { segs, total } = PREP[i];
      let l = prog(f, d.draw[0], d.draw[1], (t) => t) * total;
      for (const s of segs) {
        if (l <= s.len) { const q = pointAt(s, l); return { p: [o[0] + q[0], o[1] + q[1]], down: s.draw }; }
        l -= s.len;
      }
    }
    if (f >= d.write[0] && f <= d.write[1]) {
      const t = prog(f, d.write[0], d.write[1], (x) => x);
      const w = d.label.length * 34;
      return { p: [c[0] - w / 2 + t * w, c[1] + 312 + Math.sin(t * 40) * 8], down: true };
    }
  }
  return null;
};

// camera: [frame, centre x, centre y, zoom] (board px)
const CAM: [number, number, number, number][] = [
  [0, CELLS[0][0], CELLS[0][1] + 70, 1.32], [62, CELLS[0][0] + 20, CELLS[0][1] + 70, 1.28], [72, CELLS[1][0], CELLS[1][1] + 70, 1.3],
  [124, CELLS[1][0] + 20, CELLS[1][1] + 70, 1.27], [134, CELLS[2][0], CELLS[2][1] + 70, 1.3], [198, CELLS[2][0], CELLS[2][1] + 80, 1.26],
  [212, CELLS[3][0], CELLS[3][1] + 70, 1.3], [264, CELLS[3][0] - 20, CELLS[3][1] + 70, 1.27], [274, CELLS[4][0], CELLS[4][1] + 70, 1.3],
  [324, CELLS[4][0] - 20, CELLS[4][1] + 70, 1.27], [334, CELLS[5][0], CELLS[5][1] + 70, 1.3], [380, CELLS[5][0] + 20, CELLS[5][1] + 70, 1.26],
  [408, 1200, 760, 0.66], [450, 1200, 760, 0.64],
];
const camAt = (f: number) => {
  let i = 0;
  while (i < CAM.length - 2 && f >= CAM[i + 1][0]) i++;
  const a = CAM[i], b = CAM[i + 1];
  const move = b[0] - a[0] <= 30;
  const t = interpolate(f, [a[0], b[0]], [0, 1], { extrapolateLeft: 'clamp', extrapolateRight: 'clamp', easing: move ? Easing.bezier(0.6, 0, 0.3, 1) : (x) => x });
  return { x: mix(t, a[1], b[1]), y: mix(t, a[2], b[2]), z: mix(t, a[3], b[3]) };
};

// the hand image: 1085 x 1062, marker tip at (13, 466)
const HAND = { w: 1085, h: 1062, tip: [13, 466] as Pt, s: 0.5 };

// an arrow head at the end of a cubic path "M x y C x1 y1 x2 y2 x3 y3"
const head = (d: string) => {
  const n = d.replace(/[MC]/g, ' ').trim().split(/\s+/).map(Number);
  const [x2, y2, x3, y3] = n.slice(4);
  const a = Math.atan2(y3 - y2, x3 - x2), L = 34;
  const p = (da: number) => `${x3 - L * Math.cos(a + da)} ${y3 - L * Math.sin(a + da)}`;
  return `M ${p(0.55)} L ${x3} ${y3} L ${p(-0.55)}`;
};
// hand-drawn arrows joining the steps (board px)
const ARROWS = [
  'M 700 360 C 760 330 860 330 900 360', 'M 1500 360 C 1560 330 1660 330 1700 360', 'M 2330 560 C 2380 650 2380 760 2330 840',
  'M 1700 1090 C 1640 1060 1540 1060 1500 1090', 'M 900 1090 C 840 1060 740 1060 700 1090',
];

export const Whiteboard: React.FC = () => {
  const f = useCurrentFrame();
  const cam = camAt(f);
  const pen = penAt(f);
  // the hand: follows the pen; between drawings it rests off to the lower right of what the camera sees
  const restP: Pt = [cam.x + 1100 / cam.z, cam.y + 700 / cam.z];
  let handP: Pt = pen ? pen.p : restP;
  if (!pen) {
    // glide between the last and next pen positions instead of jumping
    let prev: Pt | null = null, next: Pt | null = null, tp = 0, tn = 0;
    for (let k = 1; k <= 14; k++) { const q = penAt(f - k); if (q) { prev = q.p; tp = k; break; } }
    for (let k = 1; k <= 14; k++) { const q = penAt(f + k); if (q) { next = q.p; tn = k; break; } }
    if (prev && next) handP = [mix(tp / (tp + tn), prev[0], next[0]), mix(tp / (tp + tn), prev[1], next[1])];
    else if (prev) handP = [mix(easeInOut(clamp(tp / 12)), prev[0], restP[0]), mix(easeInOut(clamp(tp / 12)), prev[1], restP[1])];
    else if (next) handP = [mix(easeInOut(clamp(tn / 12)), next[0], restP[0]), mix(easeInOut(clamp(tn / 12)), next[1], restP[1])];
  }
  const lift = pen && !pen.down ? 6 : 0;
  const arrows = prog(f, 386, 412, easeInOut);
  const ring = prog(f, 414, 430, Easing.out(Easing.quad));

  return (
    <AbsoluteFill style={{ background: '#E9ECEE', overflow: 'hidden' }}>
      <AbsoluteFill style={{ transform: `translate(${960 - cam.x * cam.z}px, ${540 - cam.y * cam.z}px) scale(${cam.z})`, transformOrigin: '0 0' }}>
        {/* the whiteboard */}
        <div style={{ position: 'absolute', left: -600, top: -500, width: 3600, height: 2600, background: 'radial-gradient(ellipse at 50% 40%, #FFFFFF 0%, #FAFBFA 55%, #F0F2F1 100%)' }} />
        {/* faint ghosts of old marker */}
        <svg width={2400} height={1500} style={{ position: 'absolute', left: 0, top: 0, opacity: 0.05 }}>
          <path d="M 150 900 C 400 860 600 980 820 920 M 1500 120 C 1700 90 1900 160 2100 110 M 900 1380 C 1100 1340 1300 1420 1500 1370" stroke="#555" strokeWidth={26} fill="none" strokeLinecap="round" />
        </svg>
        {DRAW.map((d, i) => (
          <div key={d.name} style={{ position: 'absolute', left: CELLS[i][0] - SIZE / 2, top: CELLS[i][1] - SIZE / 2 - 40, width: SIZE, height: SIZE }}>
            <Drawing i={i} f={f} />
          </div>
        ))}
        {/* labels, written left to right */}
        {DRAW.map((d, i) => {
          const t = prog(f, d.write[0], d.write[1], (x) => x);
          if (t <= 0) return null;
          return (
            <div key={d.name + 'l'} style={{ position: 'absolute', left: CELLS[i][0], top: CELLS[i][1] + 312, transform: 'translate(-50%, -50%) rotate(-2deg)',
              fontFamily: MARKER, fontSize: 64, color: i === 5 ? RED : BLUE, whiteSpace: 'nowrap', clipPath: `inset(-20% ${100 - t * 100}% -20% -5%)` }}>{d.label}</div>
          );
        })}
        {/* corner-to-corner dashed line on the cut drawing */}
        {f >= 284 ? (
          <svg width={SIZE} height={SIZE} style={{ position: 'absolute', left: CELLS[4][0] - SIZE / 2, top: CELLS[4][1] - SIZE / 2 - 40, overflow: 'visible' }}>
            <line x1={150} y1={110} x2={mix(prog(f, 284, 296, easeInOut), 150, 470)} y2={mix(prog(f, 284, 296, easeInOut), 110, 450)} stroke={RED} strokeWidth={9} strokeDasharray="22 16" strokeLinecap="round" />
          </svg>
        ) : null}
        {/* the overview: arrows and a red ring on the triangles */}
        {arrows > 0 ? (
          <svg width={2400} height={1500} style={{ position: 'absolute', left: 0, top: 0, overflow: 'visible' }}>
            {ARROWS.map((d, i) => {
              const t = clamp(arrows * 5 - i);
              return (
                <g key={i}>
                  <path d={d} stroke={BLUE} strokeWidth={12} fill="none" strokeLinecap="round" pathLength={1} strokeDasharray="1 1" strokeDashoffset={1 - t} />
                  {t >= 1 ? <path d={head(d)} stroke={BLUE} strokeWidth={12} fill="none" strokeLinecap="round" strokeLinejoin="round" /> : null}
                </g>
              );
            })}
            {ring > 0 ? (
              <ellipse cx={CELLS[5][0]} cy={CELLS[5][1] + 20} rx={370} ry={360} stroke={RED} strokeWidth={14} fill="none" pathLength={1} strokeDasharray="1 1"
                strokeDashoffset={1 - ring} transform={`rotate(-8 ${CELLS[5][0]} ${CELLS[5][1] + 20})`} strokeLinecap="round" />
            ) : null}
          </svg>
        ) : null}
        {/* the sleeve carries on past the picture's edge, off screen */}
        <svg width={HAND.w * HAND.s} height={HAND.h * HAND.s} viewBox={`0 0 ${HAND.w} ${HAND.h}`} style={{ position: 'absolute', overflow: 'visible',
          left: handP[0] - HAND.tip[0] * HAND.s + lift, top: handP[1] - HAND.tip[1] * HAND.s - lift, filter: 'drop-shadow(18px 22px 16px rgba(0,0,0,.22))' }}>
          <defs><linearGradient id="sleeve" x1="0" y1="0" x2="1" y2="0.2"><stop offset="0" stopColor="#5A6164" /><stop offset="0.5" stopColor="#474E51" /><stop offset="1" stopColor="#3A4043" /></linearGradient></defs>
          <polygon points="752,1040 1080,786 2000,1950 1660,2230" fill="url(#sleeve)" />
        </svg>
        {/* the hand */}
        <Img src={staticFile('img/wb/hand_marker.png')} style={{ position: 'absolute', width: HAND.w * HAND.s, height: HAND.h * HAND.s,
          left: handP[0] - HAND.tip[0] * HAND.s + lift, top: handP[1] - HAND.tip[1] * HAND.s - lift, filter: 'drop-shadow(18px 22px 16px rgba(0,0,0,.22))' }} />
      </AbsoluteFill>
      <Soundtrack sfx={SFX} />
    </AbsoluteFill>
  );
};

// a marker squeak roughly every half second while drawing or writing; a page swish on each camera move
const drawingSfx: Sfx[] = [];
DRAW.forEach((d) => {
  for (let t = d.draw[0]; t < d.draw[1] - 4; t += 13) drawingSfx.push({ at: t, file: 'stroke.wav', vol: 0.32, dur: 16 });
  drawingSfx.push({ at: d.write[0], file: 'stroke.wav', vol: 0.3, dur: 16 });
});
const SFX: Sfx[] = [
  ...drawingSfx,
  ...[64, 126, 200, 266, 326].map((t) => ({ at: t, file: 'page.wav', vol: 0.3 })),
  { at: 384, file: 'whoosh.wav', vol: 0.3 }, { at: 392, file: 'stroke.wav', vol: 0.3 }, { at: 414, file: 'circle.wav', vol: 0.4 },
];
