import React from 'react';
import { AbsoluteFill, Audio, Easing, interpolate, Sequence, staticFile, useCurrentFrame } from 'remotion';
import { clamp, FPS } from './kit';
import brand from './brand.json';

/* RodiOcean brand (assets/brand/BRAND.md; owner's picks, 10 Nov 2026), switched per episode in brand.json:
   - NO ping at the start (owner, 12 Nov 2026: "remove the ping at the start, don't do it anymore also in future video").
   - readouts: [{at, value, label?, y?, hold?}] the proof readout ("x42 NORMAL") the moment the voice says the measured
     number, with the echo ping. Yellow means "measured": nothing else in the edit is lemon yellow. One per video.
   - waves: [seconds] the sea transition: a band of water sweeps the picture from RIGHT to LEFT at one constant speed, 0.4 s
     in all (owner, 12 Nov 2026: the old wave crash was too slow; "from right to left, double the pace, no mid slowdown").
     The picture is fully covered WAVE_COVER frames after the wave starts: place the change of picture exactly there. */
export const WAVE_COVER = 6;
const WAVE_FRAMES = 12;
type Readout = { at: number; value: string; label?: string; y?: number; hold?: number };
type BrandCfg = { readouts?: Readout[]; waves?: number[] };
const B = brand as BrandCfg;

const CYAN = '#02D2F9', YELLOW = '#FEF401', ORANGE = '#FF8A1F';

const ReadoutPill: React.FC<{ value: string; label: string; y: number; dur: number }> = ({ value, label, y, dur }) => {
  const f = useCurrentFrame();
  const pop = interpolate(f, [0, 7], [0.55, 1], { ...clamp, easing: Easing.out(Easing.back(2.2)) });
  const op = interpolate(f, [0, 4, dur - 6, dur], [0, 1, 1, 0], clamp);
  const ring = interpolate(f, [0, 18], [0, 1], clamp);
  return (
    <AbsoluteFill style={{ alignItems: 'center', justifyContent: 'flex-start', paddingTop: y }}>
      <div style={{ transform: `scale(${pop})`, opacity: op, display: 'flex', alignItems: 'center', gap: 22,
        padding: '16px 44px 16px 22px', borderRadius: 999, background: 'rgba(3,11,22,0.88)',
        border: `6px solid ${CYAN}`, boxShadow: '0 0 34px rgba(2,210,249,0.45)' }}>
        <svg width={88} height={88} viewBox="0 0 88 88">
          <circle cx={44} cy={44} r={38} fill="none" stroke={CYAN} strokeWidth={5} />
          <circle cx={44} cy={44} r={22} fill="none" stroke="rgba(2,210,249,0.6)" strokeWidth={4} />
          <circle cx={63} cy={25} r={9 + 14 * ring} fill="none" stroke={YELLOW} strokeWidth={3} opacity={1 - ring} />
          <circle cx={63} cy={25} r={16} fill="rgba(254,244,1,0.35)" style={{ filter: 'blur(6px)' }} />
          <circle cx={63} cy={25} r={9} fill={YELLOW} />
        </svg>
        <span style={{ fontFamily: "'Montserrat', 'Arial Black', sans-serif", fontWeight: 900, fontSize: 100, lineHeight: 1,
          color: YELLOW, textShadow: `0 0 18px ${ORANGE}, 0 0 6px ${ORANGE}` }}>{value}</span>
        <span style={{ fontFamily: "'Montserrat', 'Segoe UI', sans-serif", fontWeight: 600, fontSize: 48, lineHeight: 1,
          color: '#F0FBFF', marginTop: 16 }}>{label}</span>
      </div>
    </AbsoluteFill>
  );
};

/** The sea transition: a band of water wider than the picture crosses it right to left at one constant speed. */
const WaveWipe: React.FC = () => {
  const f = useCurrentFrame();
  const BAND = 1620, AMP = 46, SPEED = (1080 + 200 + BAND) / WAVE_FRAMES;       // px a frame, never eased
  const lead = 1080 + 100 - SPEED * (f + 0.5), trail = lead + BAND;
  const edge = (x0: number, ph: number) => Array.from({ length: 49 }, (_, k) => {
    const y = (k / 48) * 1920;
    return [x0 + AMP * Math.sin((y / 1920) * Math.PI * 6 + ph + f * 0.9) + 18 * Math.sin((y / 1920) * Math.PI * 17 + ph * 2), y] as const;
  });
  const pts = (E: readonly (readonly [number, number])[], dx = 0) => E.map(([x, y]) => `${(x + dx).toFixed(1)} ${y.toFixed(1)}`).join(' L ');
  const L = edge(lead, 0), R = edge(trail, 1.7);
  const band = (dx: number) => `M ${pts(L, dx)} L ${pts([...R].reverse())} Z`;
  return (
    <AbsoluteFill>
      <svg width={1080} height={1920} viewBox="0 0 1080 1920">
        <defs>
          <linearGradient id="seaWipe" x1="0" x2="1" y1="0" y2="0.25">
            <stop offset="0" stopColor="#bff1ff" /><stop offset="0.18" stopColor="#35c3ee" /><stop offset="0.6" stopColor="#0a86c9" /><stop offset="1" stopColor="#0b5fa8" />
          </linearGradient>
        </defs>
        <path d={band(-34)} fill="#ffffff" opacity={0.92} />
        <path d={band(0)} fill="url(#seaWipe)" />
        {[0.22, 0.47, 0.71].map((u, k) => (
          <path key={k} d={`M ${pts(edge(lead + BAND * u, k * 2.1))}`} fill="none" stroke="#e9fbff" strokeWidth={10 - k * 2} opacity={0.35} />
        ))}
        {Array.from({ length: 14 }, (_, k) => (
          <circle key={k} cx={lead - 20 + 30 * Math.sin(k * 3.1)} cy={(k + 0.5) * 137} r={10 + 7 * Math.sin(k * 1.7 + f)} fill="#ffffff" opacity={0.85} />
        ))}
      </svg>
    </AbsoluteFill>
  );
};

/** Put this ABOVE the picture and BELOW the captions, so the words stay readable even under the wave. */
export const BrandLayer: React.FC = () => (
  <>
    {(B.readouts ?? []).map((r, i) => {
      const dur = Math.round((r.hold ?? 2.4) * FPS);
      return (
        <Sequence key={`r${i}`} from={Math.round(r.at * FPS)} durationInFrames={dur}>
          <ReadoutPill value={r.value.replace(/^x/, '×')} label={r.label ?? 'NORMAL'} y={r.y ?? 330} dur={dur} />
          <Audio src={staticFile('brand/sonar_ping_echo.wav')} volume={0.32} />
        </Sequence>
      );
    })}
    {(B.waves ?? []).map((t, i) => (
      <Sequence key={`w${i}`} from={Math.max(0, Math.round(t * FPS) - WAVE_COVER)} durationInFrames={WAVE_FRAMES}>
        <WaveWipe />
        <Audio src={staticFile('brand/sea_wave.wav')} volume={0.45} playbackRate={2} />
      </Sequence>
    ))}
  </>
);
