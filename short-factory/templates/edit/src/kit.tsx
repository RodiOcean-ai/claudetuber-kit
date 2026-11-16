import React from 'react';
import { AbsoluteFill, Easing, interpolate, useCurrentFrame } from 'remotion';

export const FPS = 30;
export const W = 1080;
export const H = 1920;
export const clamp = { extrapolateLeft: 'clamp', extrapolateRight: 'clamp' } as const;
export const ease = Easing.bezier(0.33, 1, 0.68, 1);
export const lerp = (f: number, a: number, b: number, from: number, to: number, e = ease) =>
  interpolate(f, [a, b], [from, to], { ...clamp, easing: e });

/** Pale-blue explainer world: sky gradient with a soft floor glow. */
export const Sky: React.FC<{ top?: string; bottom?: string; children?: React.ReactNode }> = ({ top = '#bfe0ff', bottom = '#f2f9ff', children }) => (
  <AbsoluteFill style={{ background: `linear-gradient(180deg, ${top} 0%, ${bottom} 75%)` }}>
    <div style={{ position: 'absolute', left: 140, right: 140, top: 1180, height: 220, borderRadius: '50%', background: 'radial-gradient(closest-side, rgba(255,255,255,0.9), rgba(255,255,255,0))' }} />
    {children}
  </AbsoluteFill>
);

/** Full-frame SVG in frame coordinates. */
export const Svg: React.FC<{ children: React.ReactNode; style?: React.CSSProperties }> = ({ children, style }) => (
  <svg viewBox={`0 0 ${W} ${H}`} width={W} height={H} style={{ position: 'absolute', inset: 0, ...style }}>{children}</svg>
);

/** Soft contact shadow under an object. */
export const Shadow: React.FC<{ x: number; y: number; w: number; o?: number }> = ({ x, y, w, o = 0.18 }) => (
  <ellipse cx={x} cy={y} rx={w / 2} ry={w / 10} fill={`rgba(30,60,110,${o})`} style={{ filter: 'blur(8px)' }} />
);

export type Dir = 'left' | 'right' | 'up' | 'down';
const vec = (d: Dir) => ({ left: [-1, 0], right: [1, 0], up: [0, -1], down: [0, 1] }[d]);

/**
 * The camera never stops: a slow push over the whole scene, a blurred whip in from `enter`
 * over the first 4 frames and a blurred whip out toward `exit` over the last 4 (the join is hidden in the blur).
 */
export const Cam: React.FC<{ dur: number; enter?: Dir; exit?: Dir; push?: [number, number]; children: React.ReactNode }> = ({ dur, enter, exit, push = [1, 1.07], children }) => {
  const f = useCurrentFrame();
  const s = interpolate(f, [0, dur], push, clamp);
  let dx = 0, dy = 0, blur = 0;
  if (enter && f < 4) {
    const k = interpolate(f, [0, 4], [1, 0], { ...clamp, easing: Easing.out(Easing.quad) });
    const [vx, vy] = vec(enter);
    dx = -vx * k * 900; dy = -vy * k * 1500; blur = k * 40;
  }
  if (exit && f > dur - 5) {
    const k = interpolate(f, [dur - 5, dur - 1], [0, 1], { ...clamp, easing: Easing.in(Easing.quad) });
    const [vx, vy] = vec(exit);
    dx = vx * k * 900; dy = vy * k * 1500; blur = k * 40;
  }
  const bx = Math.abs(dx) > 0 ? blur : blur * 0.25, by = Math.abs(dy) > 0 ? blur : blur * 0.25;
  return (
    <AbsoluteFill style={{ overflow: 'hidden', background: '#05070c' }}>
      <AbsoluteFill style={{ transform: `translate(${dx}px, ${dy}px) scale(${s})`, filter: blur > 0.5 ? `blur(${Math.max(bx, by)}px)` : undefined }}>
        {children}
      </AbsoluteFill>
    </AbsoluteFill>
  );
};

/** A simple phone: dark body, glowing screen, content slot. */
export const Phone: React.FC<{ x: number; y: number; w: number; h: number; rot?: number; children?: React.ReactNode }> = ({ x, y, w, h, rot = 0, children }) => (
  <g transform={`translate(${x} ${y}) rotate(${rot})`}>
    <rect x={-w / 2 + 10} y={-h / 2 + 18} width={w} height={h} rx={w * 0.14} fill="rgba(20,40,80,0.18)" style={{ filter: 'blur(14px)' }} />
    <rect x={-w / 2} y={-h / 2} width={w} height={h} rx={w * 0.14} fill="url(#phoneBody)" />
    <rect x={-w / 2 + w * 0.05} y={-h / 2 + w * 0.05} width={w * 0.9} height={h - w * 0.1} rx={w * 0.1} fill="url(#phoneScreen)" />
    <rect x={-w * 0.12} y={-h / 2 + w * 0.08} width={w * 0.24} height={w * 0.05} rx={w * 0.025} fill="#0c1424" />
    {children}
  </g>
);

export const Defs: React.FC = () => (
  <defs>
    <linearGradient id="phoneBody" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stopColor="#3a4660" /><stop offset="1" stopColor="#141b2b" /></linearGradient>
    <linearGradient id="phoneScreen" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stopColor="#5fb4ff" /><stop offset="1" stopColor="#2a6fe0" /></linearGradient>
    <linearGradient id="metal" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stopColor="#f4f7fb" /><stop offset="0.45" stopColor="#a9b6c8" /><stop offset="1" stopColor="#5d6b80" /></linearGradient>
    <linearGradient id="gold" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stopColor="#ffe38a" /><stop offset="0.5" stopColor="#f2b632" /><stop offset="1" stopColor="#b97a12" /></linearGradient>
    <linearGradient id="brass" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stopColor="#ffd98a" /><stop offset="1" stopColor="#c0841f" /></linearGradient>
    <linearGradient id="skin" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stopColor="#ffd2b8" /><stop offset="1" stopColor="#f0a98a" /></linearGradient>
    <radialGradient id="glow"><stop offset="0" stopColor="#fff7c2" stopOpacity="1" /><stop offset="1" stopColor="#fff7c2" stopOpacity="0" /></radialGradient>
  </defs>
);

/** Rounded label text with an outline, for words that live inside the picture. */
export const Label: React.FC<{ x: number; y: number; size: number; fill?: string; children: React.ReactNode; anchor?: 'start' | 'middle' | 'end'; weight?: number }> = ({ x, y, size, fill = '#ffffff', children, anchor = 'middle', weight = 900 }) => (
  <text x={x} y={y} fontSize={size} fontFamily="'Arial Black', 'Segoe UI', sans-serif" fontWeight={weight} fill={fill} textAnchor={anchor} dominantBaseline="middle">{children}</text>
);
