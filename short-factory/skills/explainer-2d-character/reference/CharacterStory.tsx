// Style 9: 2D CHARACTERS WITH A STORY. A little penguin chef (a puppet built from parts: body, belly, apron, eyes that
// look and blink, beak that chomps, chef's hat, two flippers that reach for things) makes the sandwich behind a kitchen
// counter and acts every step: pulls bread from the bag, twists the lid off, digs, spreads with its tongue-out focus,
// flips and presses, slashes corner to corner, then bites a triangle and melts with happiness. Flat cartoon shapes,
// squash and stretch, a real sound for every action.
import React from 'react';
import { AbsoluteFill, Easing, interpolate, useCurrentFrame } from 'remotion';
import { Soundtrack, Sfx } from '../../shared/Soundtrack';
import { K, at } from '../../shared/timing';
import { clamp, easeInOut, easeOut, mix, pop, prog, rand } from '../../shared/anim';

const NAVY = '#13294B', BELLY = '#FFFFFF', BEAK = '#F59E0B', BEAK_D = '#D97706', BLUSH = '#FF8FA3', APRON = '#7CC8EE', APRON_D = '#4AA8DA';
const WALL = '#D3ECF8', TILE = '#E8F6FC', WOOD = '#B9783F', WOOD_L = '#CF9157', COUNTER = '#F5E7D4', COUNTER_D = '#E5D1B6';
const CRUMB = '#F8DFA6', CRUST = '#D68C38', PB = '#9C561F', PB_L = '#BB733A', STEEL = '#DCE4EC', STEEL_D = '#9CB0C4', JAR = '#E4F4FB';

type Pt = [number, number];
type Key<T> = [number, T];
const track = (f: number, keys: Key<number>[], ease = easeInOut) => {
  if (f <= keys[0][0]) return keys[0][1];
  for (let i = 0; i < keys.length - 1; i++) {
    const [a, va] = keys[i], [b, vb] = keys[i + 1];
    if (f <= b) return mix(ease(clamp((f - a) / Math.max(1, b - a))), va, vb);
  }
  return keys[keys.length - 1][1];
};
const trackPt = (f: number, keys: Key<Pt>[], ease = easeInOut): Pt => [
  track(f, keys.map(([t, p]) => [t, p[0]] as Key<number>), ease), track(f, keys.map(([t, p]) => [t, p[1]] as Key<number>), ease)];

// ---------- the stage ----------
const BASE: Pt = [960, 770];              // the penguin stands here (its feet are behind the counter)
const SHOULDER_L: Pt = [-132, -262], SHOULDER_R: Pt = [132, -262];
const BAG: Pt = [430, 650], JAR_AT: Pt = [1450, 690], KNIFE_REST: Pt = [1250, 772];
const SPOT_A: Pt = [850, 768], SPOT_B: Pt = [1075, 768];
const FLAT = 0.42; // slices lying on the board are drawn squashed (cartoon perspective)

// ---------- the acting: where each flipper tip goes ----------
const restL: Pt = [800, 680], restR: Pt = [1120, 680];
const ARM_L: Key<Pt>[] = [
  [0, restL], [18, restL], [26, [BAG[0] + 20, BAG[1] - 10]], [30, [BAG[0] + 20, BAG[1] - 10]], [40, [SPOT_A[0], SPOT_A[1] - 14]],
  [44, [680, 640]], [48, [BAG[0] + 20, BAG[1] - 10]], [58, [SPOT_B[0], SPOT_B[1] - 14]], [66, restL],
  [240, restL], [248, [800, 728]], [262, [800, 734]], [270, restL], [450, restL],
];
const KR: Pt = [KNIFE_REST[0] - 40, KNIFE_REST[1] - 6];
const ARM_R: Key<Pt>[] = [
  [0, restR], [70, restR], [76, [1452, 586]], [84, [1452, 586]], [88, [1350, 520]], [92, KR], [94, KR], [99, [1446, 520]], [104, [1446, 626]],
  [110, [1446, 616]], [118, [1446, 500]], [128, [1180, 600]], [138, [980, 715]],
  // owner, note 2: "He spread it with the handle": the flipper holds the handle, so it now stays to the RIGHT of the
  // slice and the blade (pointing left and a little down) lies across the bread while it sweeps
  [143, [1075, 723]], [148, [970, 727]], [153, [1075, 733]], [158, [970, 737]], [163, [1075, 741]], [168, [970, 745]], [174, [1070, 735]],
  [182, [1100, 665]], [196, KR], [204, restR], [210, restR], [216, [SPOT_B[0], SPOT_B[1] - 14]], [218, [SPOT_B[0], SPOT_B[1] - 14]],
  [230, [1020, 560]], [244, [SPOT_A[0] + 10, SPOT_A[1] - 40]], [248, [900, 728]], [262, [900, 734]], [270, restR], [276, KR], [281, KR],
  [292, [1080, 400]], [296, [1060, 410]], [302, [740, 840]], [308, [690, 860]], [318, KR], [328, restR], [332, restR],
  [338, [930, 760]], [341, [930, 760]], [350, [1012, 476]], [372, [1040, 500]], [450, [1060, 512]],
];
const LEAN: Key<number>[] = [
  [0, 0], [18, 0], [26, -11], [32, -4], [46, -11], [56, -2], [66, 0], [80, 6], [96, 13], [112, 6], [124, 0], [138, -7], [176, -7], [196, 5],
  [210, 0], [232, 2], [250, -3], [266, 0], [290, 6], [298, -12], [312, 0], [340, 3], [350, 5], [450, 2],
];

// ---------- parts ----------
const slicePath = (w = 300, h = 300) => {
  const X = (u: number) => -w / 2 + u * w, Y = (v: number) => -h / 2 + v * h;
  return `M ${X(0.08)} ${Y(1)} L ${X(0.92)} ${Y(1)} Q ${X(1)} ${Y(1)} ${X(1)} ${Y(0.92)} L ${X(1)} ${Y(0.32)} ` +
    `C ${X(1.08)} ${Y(0.2)} ${X(1.05)} ${Y(0.01)} ${X(0.8)} ${Y(0.02)} C ${X(0.66)} ${Y(-0.04)} ${X(0.34)} ${Y(-0.04)} ${X(0.2)} ${Y(0.02)} ` +
    `C ${X(-0.05)} ${Y(0.01)} ${X(-0.08)} ${Y(0.2)} ${X(0)} ${Y(0.32)} L ${X(0)} ${Y(0.92)} Q ${X(0)} ${Y(1)} ${X(0.08)} ${Y(1)} Z`;
};
const SL_OUT = slicePath(), SL_IN = slicePath(256, 250), SL_PB = slicePath(240, 232);
const OL = { stroke: NAVY, strokeWidth: 7, strokeLinejoin: 'round' as const };

const Slice: React.FC<{ pb?: number; id?: string }> = ({ pb = 0, id = 's' }) => (
  <g>
    <path d={SL_OUT} fill={CRUST} {...OL} />
    <path d={SL_IN} fill={CRUMB} transform="translate(0 8)" />
    {[[-60, -10, 8], [50, 40, 7], [-10, 70, 6], [70, -40, 6]].map(([x, y, r], i) => <circle key={i} cx={x} cy={y} r={r} fill="#EBC77F" />)}
    {pb > 0 ? (
      <g>
        <clipPath id={`pbc-${id}`}><circle cx={0} cy={0} r={pb * 220} /></clipPath>
        <g clipPath={`url(#pbc-${id})`}>
          <path d={SL_PB} fill={PB} transform="translate(0 10)" />
          <path d="M -80 -30 C -30 -60 40 -50 85 -20 M -85 40 C -30 15 40 20 80 50" stroke={PB_L} strokeWidth={12} fill="none" strokeLinecap="round" />
        </g>
      </g>
    ) : null}
  </g>
);

// the finished sandwich (bottom slice with peanut butter, a peanut-butter band, the top slice), optionally one half of it
const Sandwich: React.FC<{ half?: 'a' | 'b'; ooze?: number; bite?: number }> = ({ half, ooze = 0, bite = 0 }) => {
  const clip = half === 'a' ? 'M -400 -400 L 400 -400 L -400 400 Z' : half === 'b' ? 'M 400 -400 L 400 400 L -400 400 Z' : null;
  const id = `sw-${half ?? 'w'}`;
  return (
    <g>
      <defs>
        {clip ? <clipPath id={`${id}-c`}><path d={clip} /></clipPath> : null}
        {clip ? <clipPath id={`${id}-o`}><path d={SL_OUT} /></clipPath> : null}
        {bite > 0 ? (
          <mask id={`${id}-m`} maskUnits="userSpaceOnUse" x={-400} y={-400} width={800} height={800}>
            <rect x={-400} y={-400} width={800} height={800} fill="#fff" />
            {[[150, -120], [112, -150], [160, -78]].map(([x, y], i) => <circle key={i} cx={x} cy={y} r={46 * bite} fill="#000" />)}
          </mask>
        ) : null}
      </defs>
      <g clipPath={clip ? `url(#${id}-c)` : undefined} mask={bite > 0 ? `url(#${id}-m)` : undefined}>
        <g transform="translate(0 26)"><Slice /></g>
        <path d={SL_OUT} fill={PB} transform="translate(0 12) scale(1.02)" />
        {ooze > 0 ? [[-150, 40], [150, 70], [-120, 140], [100, 150]].map(([x, y], i) => (
          <ellipse key={i} cx={x} cy={y} rx={18 * ooze} ry={13 * ooze} fill={PB} />
        )) : null}
        <Slice />
        {half ? <g clipPath={`url(#${id}-o)`}><line x1={300} y1={-300} x2={-300} y2={300} stroke={PB} strokeWidth={22} /></g> : null}
      </g>
    </g>
  );
};

const KnifeArt: React.FC<{ glob?: number }> = ({ glob = 0 }) => (
  // pointing along +x from the handle (0,0) to the tip (260,0)
  <g>
    <rect x={-10} y={-17} width={96} height={34} rx={14} fill={NAVY} />
    <circle cx={22} cy={0} r={5} fill={STEEL_D} /><circle cx={60} cy={0} r={5} fill={STEEL_D} />
    <path d="M 84 -15 L 230 -15 Q 268 -12 262 6 Q 240 16 84 15 Z" fill={STEEL} stroke={STEEL_D} strokeWidth={4} />
    {glob > 0 ? <ellipse cx={226} cy={-2} rx={30 * glob} ry={22 * glob} fill={PB} stroke={NAVY} strokeWidth={4} /> : null}
  </g>
);

const Flipper: React.FC<{ shoulder: Pt; tip: Pt }> = ({ shoulder, tip }) => {
  const dx = tip[0] - shoulder[0], dy = tip[1] - shoulder[1];
  const L = Math.max(120, Math.hypot(dx, dy));
  const ang = (Math.atan2(dy, dx) * 180) / Math.PI;
  return (
    <g transform={`translate(${shoulder[0]} ${shoulder[1]}) rotate(${ang})`}>
      <path d={`M -10 -30 Q ${L * 0.45} -44 ${L} -4 Q ${L + 10} 8 ${L - 8} 18 Q ${L * 0.45} 40 -10 30 Z`} fill={NAVY} />
    </g>
  );
};

export const CharacterStory: React.FC = () => {
  const f = useCurrentFrame();

  // body: a hop at the start, breathing, lean and squash
  const hop = -Math.sin(clamp((f - 3) / 12) * Math.PI) * 34;
  const lean = track(f, LEAN);
  const squash =
    1 + 0.012 * Math.sin(f / 9) -
    0.07 * Math.exp(-Math.pow((f - 100) / 5, 2)) - 0.1 * Math.exp(-Math.pow((f - 252) / 6, 2)) - 0.06 * Math.exp(-Math.pow((f - 300) / 4, 2)) -
    0.06 * Math.exp(-Math.pow((f - 354) / 4, 2));
  const wiggle = f > 364 ? Math.sin((f - 364) / 4.5) * 4 * Math.min(1, (f - 364) / 12) : 0;
  const bodyRot = lean + wiggle;
  // where the shoulders are on screen after the lean
  const rot = (p: Pt): Pt => {
    const a = (bodyRot * Math.PI) / 180, sx = p[0], sy = p[1] * squash;
    return [BASE[0] + sx * Math.cos(a) - sy * Math.sin(a), BASE[1] + hop + sx * Math.sin(a) + sy * Math.cos(a)];
  };
  const shL = rot(SHOULDER_L), shR = rot(SHOULDER_R);
  const tipL = trackPt(f, ARM_L), tipR = trackPt(f, ARM_R);

  // eyes: where they look (-1..1), blinks, focus squint, happy
  const look: Pt = trackPt(f, [[0, [0, 0]], [16, [0, 0]], [22, [-1, 0.4]], [40, [-0.5, 1]], [50, [-1, 0.4]], [58, [0.2, 1]], [70, [0.2, 0.6]],
    [76, [1, -0.2]], [95, [1, 0.5]], [126, [0.4, 0.4]], [134, [-0.5, 1]], [196, [-0.5, 1]], [210, [0.4, 1]], [232, [0, -0.2]], [246, [-0.3, 1]],
    [276, [0.6, 1]], [290, [0, -0.6]], [298, [-0.6, 1]], [330, [0, 0]], [338, [0.5, 1]], [350, [0.6, 0.2]], [450, [0, 0]]]);
  const blink = [8, 64, 128, 206, 268, 326].some((b) => f >= b && f < b + 5) ? 0.1 : 1;
  const focus = (f >= 136 && f < 178) || (f >= 286 && f < 302) ? 0.55 : 1;
  const happy = f >= at(K.better) - 2;
  const chomp = f >= 350 && f < 362 ? Math.abs(Math.sin(((f - 350) / 12) * Math.PI * 2)) : 0;

  // objects
  const s1Held = f >= 28 && f < 40, s1Down = f >= 40;
  const s2Held = f >= 48 && f < 58, s2Down = f >= 58 && f < 216;
  const s2Lift = f >= 216 && f < 246;
  const onTop = f >= 246;
  const flipT = prog(f, 226, 240, easeInOut);
  const lidHeld = f >= 76 && f < 86;
  const lidFly = prog(f, 86, 102, (t) => t);
  const lidTwist = lidHeld ? Math.sin((f - 76) * 1.2) * 25 : 0;
  const knifeHeld = (f >= 92 && f < 198) || (f >= 281 && f < 318);
  const glob = f >= 112 && f < 136 ? clamp((f - 110) / 6) : f >= 136 && f < 176 ? 1 - (f - 136) / 40 : 0;
  const pb = prog(f, at(K.spread), at(K.edges) + 4, (t) => 1 - Math.pow(1 - t, 1.6));
  const ooze = f >= 250 ? pop(f, 250, { damping: 12, stiffness: 160 }) : 0;
  const pressSq = 1 - 0.14 * Math.exp(-Math.pow((f - 254) / 6, 2));
  const cut = f >= 302;
  const part = prog(f, 302, 314, Easing.out(Easing.back(1.6)));
  const halfBHeld = f >= 341;
  const bite = f >= 354 ? 1 : 0;

  // knife angle while held: plunge (down), spread (flat-ish), slash (along the swing)
  let knifeAng = 30;
  if (f >= 92 && f < 100) knifeAng = mix(prog(f, 92, 100), 0, 90);
  else if (f >= 100 && f < 112) knifeAng = 90;
  else if (f >= 112 && f < 136) knifeAng = mix(prog(f, 112, 132), 90, 160);
  else if (f >= 136 && f < 182) knifeAng = 168 + Math.sin(f * 0.9) * 8;
  else if (f >= 182 && f < 198) knifeAng = mix(prog(f, 182, 196), 168, 0);
  else if (f >= 281 && f < 296) knifeAng = mix(prog(f, 281, 292), 0, -110);
  else if (f >= 296 && f < 318) knifeAng = mix(prog(f, 296, 304), -110, 150);

  const shadow = (x: number, w: number) => <ellipse cx={x} cy={792} rx={w} ry={10} fill="rgba(19,41,75,.14)" />;

  return (
    <AbsoluteFill style={{ background: WALL, overflow: 'hidden' }}>
      <svg width={1920} height={1080} viewBox="0 0 1920 1080">
        <defs>
          <clipPath id="above-jar"><rect x={0} y={0} width={1920} height={JAR_AT[1] - 96} /></clipPath>
          <pattern id="tiles" width={120} height={120} patternUnits="userSpaceOnUse">
            <rect width={120} height={120} fill={WALL} /><path d="M 0 0 L 120 0 M 0 0 L 0 120" stroke={TILE} strokeWidth={6} />
          </pattern>
        </defs>
        <rect width={1920} height={800} fill="url(#tiles)" />
        {/* window */}
        <g transform="translate(150 120)">
          <rect width={430} height={330} rx={26} fill="#fff" />
          <rect x={22} y={22} width={386} height={286} rx={14} fill="#9FDAF7" />
          <ellipse cx={150 + Math.sin(f / 60) * 10} cy={120} rx={70} ry={30} fill="#fff" /><ellipse cx={200 + Math.sin(f / 60) * 10} cy={104} rx={50} ry={32} fill="#fff" />
          <ellipse cx={320} cy={210} rx={44} ry={18} fill="#fff" opacity={0.9} />
          <path d="M 215 22 L 215 308 M 22 165 L 408 165" stroke="#fff" strokeWidth={14} />
        </g>
        {/* shelf with jars */}
        <g transform="translate(1340 230)">
          <rect x={0} y={120} width={430} height={22} rx={6} fill={WOOD} />
          {[[30, '#F28B82', 70, 90], [120, '#FDD663', 60, 110], [200, '#81C995', 80, 80], [300, '#A7C7E7', 70, 100]].map(([x, c, w, h], i) => (
            <g key={i}><rect x={x as number} y={120 - (h as number)} width={w as number} height={h as number} rx={12} fill={c as string} stroke={NAVY} strokeWidth={5} />
              <rect x={(x as number) + 8} y={110 - (h as number)} width={(w as number) - 16} height={14} rx={4} fill={NAVY} /></g>
          ))}
        </g>

        {/* ---- the penguin (behind the counter) ---- */}
        <g transform={`translate(${BASE[0]} ${BASE[1] + hop}) rotate(${bodyRot}) scale(${1 / Math.sqrt(squash)} ${squash})`}>
          <ellipse cx={0} cy={-232} rx={158} ry={238} fill={NAVY} />
          <ellipse cx={0} cy={-200} rx={118} ry={196} fill={BELLY} />
          {/* apron */}
          <path d="M -98 -150 L 98 -150 L 112 40 L -112 40 Z" fill={APRON} />
          <rect x={-46} y={-96} width={92} height={56} rx={12} fill={APRON_D} />
          <path d="M -98 -150 Q -110 -230 -70 -300 M 98 -150 Q 110 -230 70 -300" stroke={APRON_D} strokeWidth={9} fill="none" />
          {/* face */}
          {[-1, 1].map((s) => (
            <g key={s} transform={`translate(${s * 48} -338)`}>
              {happy ? (
                <path d="M -26 6 Q 0 -22 26 6" stroke={NAVY} strokeWidth={9} fill="none" strokeLinecap="round" />
              ) : (
                <g transform={`scale(1 ${blink * focus})`}>
                  <ellipse rx={31} ry={37} fill="#fff" />
                  <circle cx={look[0] * 11} cy={look[1] * 13} r={16} fill={NAVY} />
                  <circle cx={look[0] * 11 + 6} cy={look[1] * 13 - 6} r={5.5} fill="#fff" />
                </g>
              )}
            </g>
          ))}
          <ellipse cx={-92} cy={-292} rx={20} ry={11} fill={BLUSH} opacity={happy ? 0.9 : 0.55} />
          <ellipse cx={92} cy={-292} rx={20} ry={11} fill={BLUSH} opacity={happy ? 0.9 : 0.55} />
          {/* beak (opens to chomp) */}
          <path d="M -30 -292 L 30 -292 L 0 -264 Z" fill={BEAK} stroke={BEAK_D} strokeWidth={4} strokeLinejoin="round" transform={`translate(0 ${chomp * 10})`} />
          <path d="M -32 -294 Q 0 -330 32 -294 Z" fill={BEAK} stroke={BEAK_D} strokeWidth={4} strokeLinejoin="round" transform={`translate(0 ${-chomp * 6})`} />
          {/* chef's hat */}
          <g transform={`translate(0 -455) rotate(${-bodyRot * 0.4 + Math.sin(f / 10) * 2})`}>
            <rect x={-76} y={-6} width={152} height={44} rx={10} fill="#fff" stroke={NAVY} strokeWidth={6} />
            <circle cx={-52} cy={-30} r={48} fill="#fff" stroke={NAVY} strokeWidth={6} />
            <circle cx={52} cy={-30} r={48} fill="#fff" stroke={NAVY} strokeWidth={6} />
            <circle cx={0} cy={-56} r={58} fill="#fff" stroke={NAVY} strokeWidth={6} />
            <rect x={-70} y={-4} width={140} height={20} fill="#fff" />
          </g>
        </g>

        {/* ---- the counter ---- */}
        <rect x={0} y={786} width={1920} height={294} fill={COUNTER} />
        <rect x={0} y={770} width={1920} height={26} fill={WOOD} />
        <rect x={0} y={770} width={1920} height={8} fill={WOOD_L} />
        {[200, 640, 1080, 1520].map((x) => <g key={x}><rect x={x} y={840} width={360} height={210} rx={14} fill="none" stroke={COUNTER_D} strokeWidth={6} />
          <rect x={x + 150} y={870} width={60} height={14} rx={7} fill={COUNTER_D} /></g>)}

        {/* the board */}
        {shadow(960, 300)}
        <rect x={690} y={758} width={540} height={34} rx={16} fill={WOOD_L} stroke={NAVY} strokeWidth={6} />
        {/* the bread bag */}
        {shadow(BAG[0], 110)}
        <g transform={`translate(${BAG[0]} ${BAG[1]}) rotate(${(f >= 26 && f < 34) || (f >= 46 && f < 54) ? Math.sin(f * 2) * 4 : 0})`}>
          <path d="M -90 140 L -100 -40 Q -60 -110 0 -112 Q 60 -110 100 -40 L 90 140 Z" fill="rgba(255,255,255,0.75)" stroke={NAVY} strokeWidth={6} />
          <rect x={-70} y={-30} width={140} height={160} rx={30} fill={CRUST} />
          <rect x={-56} y={-14} width={112} height={140} rx={22} fill={CRUMB} />
          <path d="M -26 -112 L 26 -112 L 14 -96 L -14 -96 Z" fill="#3B82F6" />
        </g>
        {/* the jar and its lid */}
        {shadow(JAR_AT[0], 95)}
        <g transform={`translate(${JAR_AT[0]} ${JAR_AT[1]}) rotate(${f >= 100 && f < 114 ? Math.sin(f * 1.6) * 5 : 0})`}>
          <rect x={-80} y={-92} width={160} height={190} rx={34} fill={JAR} stroke={NAVY} strokeWidth={6} />
          <rect x={-66} y={-54 + (f >= 112 ? 14 : 0)} width={132} height={140 - (f >= 112 ? 14 : 0)} rx={24} fill={PB} />
          <rect x={-80} y={-10} width={160} height={56} fill="#E5484D" />
          <circle cx={0} cy={18} r={18} fill="#fff" /><circle cx={0} cy={18} r={9} fill={PB} />
          <rect x={-62} y={-106} width={124} height={18} rx={6} fill="#C8E7F5" stroke={NAVY} strokeWidth={5} />
        </g>
        {(() => {
          let x = JAR_AT[0], y = JAR_AT[1] - 118, r = 0;
          if (lidHeld) { x = tipR[0]; y = tipR[1] + 8; r = lidTwist; }
          if (f >= 86) {
            x = mix(lidFly, 1452, 1650); y = mix(lidFly, 586, 760) - Math.sin(lidFly * Math.PI) * 140 - Math.abs(Math.sin(prog(f, 102, 114) * Math.PI)) * 30 * (f >= 102 ? 1 : 0);
            r = lidFly * 400;
          }
          return (
            <g transform={`translate(${x} ${y}) rotate(${r})`}>
              <rect x={-76} y={-22} width={152} height={44} rx={12} fill="#E5484D" stroke={NAVY} strokeWidth={6} />
              {[-48, -24, 0, 24, 48].map((dx) => <rect key={dx} x={dx - 3} y={-14} width={6} height={28} rx={3} fill="#fff" opacity={0.45} />)}
            </g>
          );
        })()}
        {/* the knife resting on the counter */}
        {!knifeHeld ? <g transform={`translate(${KNIFE_REST[0] - 120} ${KNIFE_REST[1] - 4})`}><KnifeArt /></g> : null}

        {/* slices on the board */}
        {s1Down && !onTop ? <g transform={`translate(${SPOT_A[0]} ${SPOT_A[1] - 4}) scale(0.78 ${0.78 * FLAT})`}><Slice pb={pb} id="a" /></g> : null}
        {s2Down ? <g transform={`translate(${SPOT_B[0]} ${SPOT_B[1] - 4}) scale(0.78 ${0.78 * FLAT})`}><Slice id="b" /></g> : null}
        {/* the sandwich, then its halves */}
        {onTop && !cut ? (
          <g transform={`translate(${SPOT_A[0]} ${SPOT_A[1] - 10}) scale(0.78 ${0.78 * FLAT * pressSq})`}><Sandwich ooze={ooze} /></g>
        ) : null}
        {cut ? (
          <>
            <g transform={`translate(${SPOT_A[0] - 22 * part} ${SPOT_A[1] - 10 + 4 * part}) scale(0.78 ${0.78 * FLAT})`}><Sandwich half="a" ooze={ooze} /></g>
            {!halfBHeld ? (
              <g transform={`translate(${SPOT_A[0] + 34 * part} ${SPOT_A[1] - 10 - 3 * part}) scale(0.78 ${0.78 * FLAT})`}><Sandwich half="b" ooze={ooze} /></g>
            ) : null}
          </>
        ) : null}
        {/* sparkles at the edges */}
        {f >= at(K.edges) && f < at(K.edges) + 24 ? [[-120, -10], [120, -10], [0, -60], [0, 40], [-95, 30], [95, 30]].map(([dx, dy], i) => {
          const t = (f - at(K.edges) - i) / 18;
          if (t < 0 || t > 1) return null;
          return <path key={i} transform={`translate(${SPOT_A[0] + dx * 1.15} ${SPOT_A[1] + dy}) scale(${Math.sin(t * Math.PI)}) rotate(${t * 90})`}
            d="M 0 -26 L 6 -6 L 26 0 L 6 6 L 0 26 L -6 6 L -26 0 L -6 -6 Z" fill="#FFD43B" stroke={NAVY} strokeWidth={4} />;
        }) : null}
        {/* press lines */}
        {f >= 248 && f < 266 ? [-1, 1].map((s) => (
          <g key={s} opacity={1 - prog(f, 256, 266)} transform={`translate(${SPOT_A[0] + s * 150} ${SPOT_A[1] - 40})`}>
            <path d={`M 0 0 L ${s * 34} -10 M 0 16 L ${s * 40} 16 M 0 32 L ${s * 34} 42`} stroke={NAVY} strokeWidth={7} strokeLinecap="round" />
          </g>
        )) : null}
        {/* the slash */}
        {f >= 297 && f < 312 ? (
          <path d="M 1010 690 Q 860 730 700 846" stroke="#fff" strokeWidth={mix(prog(f, 297, 302), 4, 30) * (1 - prog(f, 304, 312))} fill="none" strokeLinecap="round" opacity={0.95} />
        ) : null}

        {/* ---- flippers and what they hold (in front of the counter) ---- */}
        <Flipper shoulder={shL} tip={tipL} />
        <Flipper shoulder={shR} tip={tipR} />
        {s1Held ? <g transform={`translate(${tipL[0]} ${tipL[1]}) rotate(${-10 + (f - 28) * 2}) scale(${mix(prog(f, 28, 40), 0.55, 0.78)} ${mix(prog(f, 28, 40), 0.55, 0.78 * FLAT)})`}><Slice id="h1" /></g> : null}
        {s2Held ? <g transform={`translate(${tipL[0]} ${tipL[1]}) rotate(${10 - (f - 48) * 2}) scale(${mix(prog(f, 48, 58), 0.55, 0.78)} ${mix(prog(f, 48, 58), 0.55, 0.78 * FLAT)})`}><Slice id="h2" /></g> : null}
        {s2Lift ? (() => {
          // unflatten as it is lifted, turn over in the air (the slice shows its other face), flatten as it lands
          const yS = f < 226 ? mix(prog(f, 216, 226), FLAT, 1) : f < 240 ? Math.max(0.08, Math.abs(Math.cos(flipT * Math.PI))) : mix(prog(f, 240, 246), 1, FLAT);
          return <g transform={`translate(${tipR[0]} ${tipR[1] + 30}) scale(0.78 ${0.78 * yS})`}><Slice id="h3" /></g>;
        })() : null}
        {knifeHeld ? (
          // while it digs, the blade disappears into the jar (only what is above the jar's mouth shows)
          <g clipPath={f >= 99 && f < 119 ? 'url(#above-jar)' : undefined}>
            <g transform={`translate(${tipR[0]} ${tipR[1]}) rotate(${knifeAng}) translate(-40 0)`}><KnifeArt glob={glob} /></g>
          </g>
        ) : null}
        {halfBHeld ? (
          <g transform={`translate(${tipR[0] - 20} ${tipR[1] + 10}) rotate(${mix(prog(f, 341, 350), 0, -50)}) scale(${mix(prog(f, 341, 350), 0.78, 0.72)} ${mix(prog(f, 341, 350), 0.78 * FLAT, 0.72)})`}>
            <Sandwich half="b" bite={bite} />
          </g>
        ) : null}
        {/* crumbs from the bite */}
        {f >= 354 && f < 390 ? Array.from({ length: 12 }).map((_, i) => {
          const t = f - 354, a = -Math.PI / 2 + (rand(i) - 0.5) * 2.2, v = 5 + rand(i + 9) * 6;
          return <rect key={i} x={985 + Math.cos(a) * v * t} y={470 + Math.sin(a) * v * t + 0.5 * t * t} width={9} height={9} rx={2} fill={i % 2 ? CRUMB : CRUST} stroke={NAVY} strokeWidth={2} opacity={1 - t / 36} />;
        }) : null}
        {/* hearts */}
        {happy ? [0, 1, 2, 3].map((i) => {
          const t = f - (at(K.better) + i * 14);
          if (t < 0 || t > 60) return null;
          const x = 960 + (i % 2 ? 160 : -170) + Math.sin(t / 6) * 14, y = 330 - t * 4;
          return <path key={i} transform={`translate(${x} ${y}) scale(${Math.min(1, t / 8) * 1.2})`} opacity={1 - Math.max(0, (t - 40) / 20)}
            d="M 0 12 C -30 -10 -18 -34 0 -18 C 18 -34 30 -10 0 12 Z" fill="#FF5C7A" stroke={NAVY} strokeWidth={4} />;
        }) : null}
      </svg>
      <Soundtrack sfx={SFX} />
    </AbsoluteFill>
  );
};

const SFX: Sfx[] = [
  { at: 3, file: 'jump.wav', vol: 0.25 },
  { at: 26, file: 'paper.wav', vol: 0.3, dur: 20 }, { at: 40, file: 'card.wav', vol: 0.35 },
  { at: 46, file: 'paper.wav', vol: 0.3, dur: 20 }, { at: 58, file: 'card2.wav', vol: 0.35 },
  { at: 79, file: 'zip2.wav', vol: 0.3 }, { at: 86, file: 'zip1.wav', vol: 0.25 }, { at: 90, file: 'pop.wav', vol: 0.35 },
  { at: 106, file: 'bump2.wav', vol: 0.3 }, { at: 98, file: 'smack.wav', vol: 0.3 }, { at: 113, file: 'pop2.wav', vol: 0.35 },
  { at: 138, file: 'paper.wav', vol: 0.3, dur: 40 }, { at: at(K.edges), file: 'ding.wav', vol: 0.2 },
  { at: 226, file: 'whoosh.wav', vol: 0.3 }, { at: 250, file: 'thud.wav', vol: 0.45 }, { at: 252, file: 'gulp.wav', vol: 0.15 },
  { at: 288, file: 'riser.wav', vol: 0.12, dur: 14 }, { at: 297, file: 'whip.wav', vol: 0.5 }, { at: 304, file: 'card.wav', vol: 0.3 },
  { at: 352, file: 'crack.wav', vol: 0.45 }, { at: 356, file: 'crack.wav', vol: 0.3 },
  { at: at(K.better) - 2, file: 'sparkle.wav', vol: 0.25 },
];
