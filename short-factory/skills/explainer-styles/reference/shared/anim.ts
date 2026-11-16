import { Easing, interpolate, spring } from 'remotion';
import { FPS } from './timing';

const C = { extrapolateLeft: 'clamp', extrapolateRight: 'clamp' } as const;
/** 0 -> 1 between frames a and b (clamped), with an optional easing. */
export const prog = (f: number, a: number, b: number, ease: (t: number) => number = Easing.inOut(Easing.cubic)) =>
  interpolate(f, [a, b], [0, 1], { ...C, easing: ease });
/** map 0..1 to [x, y] */
export const mix = (t: number, x: number, y: number) => x + (y - x) * t;
/** a spring that starts at frame `from` */
export const pop = (f: number, from: number, cfg: { damping?: number; stiffness?: number; mass?: number } = {}) =>
  spring({ frame: f - from, fps: FPS, config: { damping: 12, stiffness: 170, mass: 0.8, ...cfg } });
export const smooth = (f: number, from: number, dur = 18) => spring({ frame: f - from, fps: FPS, durationInFrames: dur, config: { damping: 200 } });
export const easeOut = Easing.out(Easing.cubic);
export const easeIn = Easing.in(Easing.cubic);
export const easeInOut = Easing.inOut(Easing.cubic);
export const backOut = Easing.out(Easing.back(1.6));
/** cheap deterministic pseudo-random in [0, 1) */
export const rand = (seed: number) => {
  const x = Math.sin(seed * 127.1 + 311.7) * 43758.5453;
  return x - Math.floor(x);
};
export const clamp = (v: number, a = 0, b = 1) => Math.min(b, Math.max(a, v));
