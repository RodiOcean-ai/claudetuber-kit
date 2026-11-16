import React from 'react';
import { AbsoluteFill, spring, useCurrentFrame } from 'remotion';
import { FPS } from './kit';

/* Captions: 1-3 words, a new chunk after punctuation or when a chunk would pass 1 s. */
export type Word = { w: string; s: number; e: number };
export const chunks = (words: Word[], starts?: number[]) => {
  if (starts) {                                  // hand-set phrase breaks (word numbers where each caption starts)
    return starts.map((st, k) => {
      const ws = words.slice(st, starts[k + 1] ?? words.length);
      return { text: ws.map((x) => x.w).join(' ').replace(/(\d) ,(\d)/g, '$1,$2'), s: ws[0].s, e: ws[ws.length - 1].e };
    });
  }
  const CHUNKS: { text: string; s: number; e: number }[] = [];
  let cur: Word[] = [];
  const joined: Word[] = [];                     // the voice-to-text splits numbers ("231" + ",000"): glue them back
  for (const w of words) {
    const prev = joined[joined.length - 1];
    if (prev && /^,\d/.test(w.w) && /\d$/.test(prev.w)) joined[joined.length - 1] = { w: prev.w + w.w, s: prev.s, e: w.e };
    else joined.push(w);
  }
  const flush = () => { if (cur.length) CHUNKS.push({ text: cur.map((x) => x.w).join(' '), s: cur[0].s, e: cur[cur.length - 1].e }); cur = []; };
  for (const w of joined) {
    if (cur.length && (cur.length >= 3 || w.e - cur[0].s > 1.0)) flush();
    cur.push(w);
    if (/[.,?!]$/.test(w.w)) flush();
  }
  flush();
  return CHUNKS;
};

export const Captions: React.FC<{ words: Word[]; starts?: number[] }> = ({ words, starts }) => {
  const CHUNKS = React.useMemo(() => chunks(words, starts), [words, starts]);
  const f = useCurrentFrame();
  const t = f / FPS;
  const i = CHUNKS.findIndex((c, k) => t >= c.s - 0.03 && t < (CHUNKS[k + 1]?.s ?? c.e + 0.4) - 0.03 && t < c.e + 0.6);
  if (i < 0) return null;
  const c = CHUNKS[i];
  const k = spring({ frame: f - Math.round(c.s * FPS), fps: FPS, config: { damping: 14, stiffness: 220 } });
  return (
    <AbsoluteFill style={{ alignItems: 'center', top: 1120, height: 200, justifyContent: 'center' }}>
      <div style={{
        fontFamily: "'Arial Black', 'Segoe UI', sans-serif", fontWeight: 900, fontSize: 86, color: '#ffffff',
        WebkitTextStroke: '7px #000000', paintOrder: 'stroke fill', textAlign: 'center', padding: '0 60px',
        transform: `scale(${0.85 + 0.15 * k})`, lineHeight: 1.05,
      }}>{c.text.replace(/[,.]$/, '')}</div>
    </AbsoluteFill>
  );
};

