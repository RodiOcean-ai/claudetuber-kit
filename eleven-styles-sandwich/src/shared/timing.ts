// The shared beat sheet: every style follows the same voice, words and steps, so only the style changes.
import words from './words.json';
import phrases from './phrases.json';

export const FPS = 30;
export const W = 1920;
export const H = 1080;
export const DURATION = 450; // 15.0 s

export type Word = { w: string; s: number; e: number; fs: number; fe: number };
export type Phrase = { text: string; s: number; e: number; fs: number; fe: number };
export const WORDS = words as Word[];
export const PHRASES = phrases as Phrase[];

// Word numbers (0-35) of the words the pictures act on.
export const K = {
  take: 0, two: 1, slices: 2, bread: 4, then: 5, dig: 6, knife: 8, into: 9, peanut: 11, butter: 12,
  and1: 13, spread: 14, it1: 15, right: 16, edges: 19, press: 20, second: 22, slice: 23, on: 24, top: 25,
  and2: 26, cut: 27, corner1: 29, to2: 30, corner2: 31, because: 32, triangles: 33, taste: 34, better: 35,
} as const;
export const at = (k: number) => WORDS[k].fs; // first frame of word k
export const end = (k: number) => WORDS[k].fe; // last frame of word k

// The five steps and the payoff (frames). Each step owns the screen from its first word until the next step starts.
export const STEPS = {
  bread: { from: 0, to: 71 }, //   "Take two slices of bread,"
  knife: { from: 71, to: 134 }, // "then dig a knife into the peanut butter,"
  spread: { from: 134, to: 212 }, // "and spread it, right to the edges."
  press: { from: 212, to: 274 }, // "Press the second slice on top"
  cut: { from: 274, to: 331 }, //   "and cut it corner to corner,"
  payoff: { from: 331, to: 450 }, // "because triangles taste better."
} as const;
export const VOICE_END = 376; // the last word ends here; 376-450 is the payoff hold
