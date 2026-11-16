/* The editor-style timeline under the review player ("like editing software: I can see where things are at the bottom
   and put notes there, especially about the voice, so I understand better what I'm hearing").
   Rows: picture (the chapters, or the tab itself), clips, voice (every sentence, and every word when zoomed in, over its
   waveform), music (each section over its waveform), sound effects, notes. A red line follows the player; click to jump,
   Ctrl + mouse wheel to zoom, double-click any row to leave a note on that exact sound.
   Data: review/timeline.json (written by review/make_timeline.py from the project's manifest) plus the sound effects,
   clips and other sounds the page reads from the composition itself while it plays (scanSounds below; saved by the
   server in review/sounds.json, one list per tab). */
import React, { useCallback, useEffect, useLayoutEffect, useMemo, useRef, useState } from 'react';
import { Sequence } from 'remotion';

export type Sound = { f: number; e: number; src: string; vol: number | null; kind: 'sfx' | 'clip' | 'voice' | 'music' };
export type Chapter = { id: string; title: string; style?: string; start: number; frames: number };
export type TL = {
  fps: number; total: number; pps: number;
  chapters: Chapter[];
  voice: { f: number; e: number; text: string }[];
  words: { f: number; e: number; w: string }[];
  music: { f: number; e: number; name: string; bpm?: number | null; chords?: string; inst?: string[] }[];
  voicePeaks: string; musicPeaks: string;
  voiceFiles: string[]; musicFiles: string[];   // files in public/ whose exact data is above (not read from the composition)
  sounds: Record<string, { items: Sound[]; at: string; code?: number }>;
  silent: string[];                             // files in public/ to leave off the timeline (made silent, placeholders)
};
export type TrackId = 'picture' | 'clips' | 'voice' | 'music' | 'sfx';
export const TRACK_NAME: Record<TrackId, string> = { picture: 'Picture', clips: 'Clips', voice: 'Voice', music: 'Music', sfx: 'Sound effects' };
export type TLNote = { id: string; n: number; frame: number | null; status: 'open' | 'done'; track?: string | null; text: string };

/** timeline.json may be missing or partial (no manifest): fill in what is not there */
export const normTl = (x: Partial<TL> | null | undefined, fps: number): TL => ({
  fps: x?.fps || fps, total: x?.total || 0, pps: x?.pps || 10,
  chapters: x?.chapters ?? [], voice: x?.voice ?? [], words: x?.words ?? [], music: x?.music ?? [],
  voicePeaks: x?.voicePeaks ?? '', musicPeaks: x?.musicPeaks ?? '',
  voiceFiles: x?.voiceFiles ?? [], musicFiles: x?.musicFiles ?? [], sounds: x?.sounds ?? {}, silent: x?.silent ?? [],
});

const ROWS: { id: TrackId | 'ruler' | 'notes'; h: number; name: string }[] = [
  { id: 'ruler', h: 20, name: '' },
  { id: 'picture', h: 30, name: 'V1 Picture' },
  { id: 'clips', h: 24, name: 'V2 Clips' },
  { id: 'voice', h: 46, name: 'A1 Voice' },
  { id: 'music', h: 40, name: 'A2 Music' },
  { id: 'sfx', h: 36, name: 'A3 Sound effects' },
  { id: 'notes', h: 24, name: 'Notes' },
];
const TOP: Record<string, number> = {};
const RH: Record<string, number> = {};
{ let y = 0; for (const r of ROWS) { TOP[r.id] = y; RH[r.id] = r.h; y += r.h; } }
const HEIGHT = ROWS.reduce((a, r) => a + r.h, 0);
const CH_COLORS = ['#3d6fb6', '#7a4fb0', '#2f8f83', '#b5832a', '#b2503f', '#4f7f3a', '#8a5a2b', '#356f9e', '#7b3f8c',
  '#2e7d6b', '#9a6a1c', '#a1453a', '#4a6aa8'];
/** a media src as a path inside public/ ("/audio/voice.wav?x" -> "audio/voice.wav") */
export const cleanSrc = (src: string) => {
  let p = src.split('?')[0];
  try { p = decodeURIComponent(p); } catch { /* keep as is */ }
  return p.replace(/^\/+/, '');
};
const base = (src: string) => (cleanSrc(src).split('/').pop() || src).replace(/\.(wav|mp3|m4a|aac|ogg|mp4|webm|mov)$/i, '');
const fmtAt = (f: number, fps: number) => { const s = f / fps, m = Math.floor(s / 60); return `${m}:${(s - m * 60).toFixed(1).padStart(4, '0')}`; };

// ---------------------------------------------------------------------------------------------- reading the sounds
type Fiber = { elementType: unknown; type: unknown; memoizedProps: Record<string, unknown> | null; child: Fiber | null; sibling: Fiber | null };
const MEDIA = /\.(wav|mp3|m4a|aac|ogg|mp4|webm|mov)(\?|$)/i;
const kindOf = (src: string, skip: Set<string>): Sound['kind'] | null => {
  const p = cleanSrc(src);
  if (skip.has(p)) return null;                                    // exact data comes from timeline.json
  if (/\.(mp4|webm|mov)$/i.test(p)) return 'clip';
  const low = p.toLowerCase();
  if (/voice|narrat/.test(low)) return 'voice';
  if (/music/.test(low)) return 'music';
  return 'sfx';
};
export type Found = { f: number; src: string; vol: number | null; dur: number | null; kind: Sound['kind'] };

/** Walk the live React tree under `el` and list every sound and clip with its frame on the timeline (`offset` = where the
 *  tab's frame 0 sits). Sequences that aren't playing right now still carry their children as props, so most of the
 *  composition is found at once; the rest is added while it plays. */
export const scanSounds = (el: HTMLElement, offset: number, skip: Set<string> = new Set()): Found[] => {
  const key = Object.keys(el).find((k) => k.startsWith('__reactFiber$'));
  if (!key) return [];
  const root = (el as unknown as Record<string, Fiber>)[key];
  const out = new Map<string, Found>();
  const add = (f: number, props: Record<string, unknown>, dur: number | null) => {
    const src = props.src;
    if (typeof src !== 'string' || !MEDIA.test(src)) return;
    const kind = kindOf(src, skip); if (!kind) return;
    const k = `${Math.round(f)}|${src}`;
    if (!out.has(k)) out.set(k, { f: Math.round(f), src, vol: typeof props.volume === 'number' ? props.volume : null, dur, kind });
  };
  const walkEl = (node: unknown, off: number, dur: number | null, depth: number): void => {
    if (depth > 40 || node == null || typeof node !== 'object') return;
    if (Array.isArray(node)) { node.forEach((n) => walkEl(n, off, dur, depth + 1)); return; }
    const e = node as { type?: unknown; props?: Record<string, unknown> };
    if (!e.props) return;
    let o = off, d = dur;
    if (e.type === Sequence) {
      o = off + (Number(e.props.from) || 0);
      const df = Number(e.props.durationInFrames); d = Number.isFinite(df) ? df : dur;
    }
    if (typeof e.type !== 'string') add(o, e.props, d);
    walkEl(e.props.children, o, d, depth + 1);
  };
  // Every Remotion sequence (a plain <Sequence> and each part of a <Series>) renders one inner component named
  // SequenceRefForwardingFunction that carries `from`: add the offset there, exactly once per sequence.
  const isSeq = (t: unknown) => {
    const x = t as { name?: string; displayName?: string; render?: { name?: string } } | null;
    return !!x && x.displayName !== 'Sequence' && (x.name === 'SequenceRefForwardingFunction' || x.render?.name === 'SequenceRefForwardingFunction');
  };
  const stack: [Fiber, number, number | null][] = [[root, offset, null]];
  let guard = 0;
  while (stack.length && guard++ < 200000) {
    const [fb, off, dur] = stack.pop()!;
    let o = off, d = dur;
    const p = fb.memoizedProps;
    if (p && isSeq(fb.elementType)) {
      o = off + (Number(p.from) || 0);
      const df = Number(p.durationInFrames); d = Number.isFinite(df) ? df : dur;
      walkEl(p.children, o, d, 0);      // what it plays, also when it isn't playing now (duplicates merge by frame + file)
    }
    if (p && typeof fb.type !== 'string') add(o, p, d);
    if (fb.sibling) stack.push([fb.sibling, off, dur]);
    if (fb.child) stack.push([fb.child, o, d]);
  }
  return [...out.values()];
};

const durCache = new Map<string, Promise<number>>();
export const mediaSeconds = (src: string): Promise<number> => {
  if (!durCache.has(src)) {
    durCache.set(src, new Promise((res) => {
      const isVid = /\.(mp4|webm|mov)/i.test(src);
      const m = document.createElement(isVid ? 'video' : 'audio');
      m.preload = 'metadata'; m.muted = true;
      const done = () => { res(Number.isFinite(m.duration) ? m.duration : 1); m.removeAttribute('src'); m.load(); };
      m.onloadedmetadata = done; m.onerror = () => res(1);
      setTimeout(() => res(1), 8000);
      m.src = src;
    }));
  }
  return durCache.get(src)!;
};

// ------------------------------------------------------------------------------------------------------- timeline
type Props = {
  tl: TL; sounds: Sound[]; name: string; start: number; frames: number; frame: number; playing: boolean; notes: TLNote[];
  musicHeard: boolean; onSeek: (f: number) => void; onTrackNote: (track: TrackId, frame: number, item: string) => void;
};

type Block = { f: number; e: number; label: string; title: string; color?: string; lane?: number };

export const Timeline: React.FC<Props> = ({ tl, sounds: allSounds, name, start, frames, frame, playing, notes, musicHeard, onSeek, onTrackNote }) => {
  const FPS = tl.fps;
  const fmt = (f: number) => fmtAt(f, FPS);
  const scroller = useRef<HTMLDivElement>(null);
  const [viewW, setViewW] = useState(1000);
  const [zoom, setZoom] = useState(0);            // 0 = fit; otherwise pixels per frame
  const [scroll, setScroll] = useState(0);
  const [hover, setHover] = useState<{ x: number; y: number; text: string } | null>(null);
  const pending = useRef<number | null>(null);
  const fit = Math.max(0.0001, (viewW - 2) / frames);
  const ppf = zoom || fit;
  const W = Math.max(viewW, frames * ppf);
  const end = start + frames;
  const loc = (f: number) => (f - start) * ppf;

  useLayoutEffect(() => {
    const el = scroller.current; if (!el) return;
    const ro = new ResizeObserver(() => setViewW(el.clientWidth));
    ro.observe(el); setViewW(el.clientWidth);
    return () => ro.disconnect();
  }, []);
  useEffect(() => { setZoom(0); scroller.current?.scrollTo({ left: 0 }); }, [start, frames]);

  // keep the red line in view while playing
  useEffect(() => {
    const el = scroller.current; if (!el || !playing) return;
    const x = frame * ppf;
    if (x < el.scrollLeft || x > el.scrollLeft + el.clientWidth - 40) el.scrollLeft = Math.max(0, x - el.clientWidth * 0.1);
  }, [frame, playing, ppf]);

  const zoomTo = useCallback((z: number, anchorX?: number) => {
    const el = scroller.current; if (!el) return;
    const nz = Math.min(12, Math.max(fit, z));
    const headX = frame * ppf - el.scrollLeft;     // like an editor: zoom around the red line when it's in view
    const ax = anchorX ?? (headX >= 0 && headX <= el.clientWidth ? headX : el.clientWidth / 2);
    const fAt = (el.scrollLeft + ax) / ppf;
    const zz = nz <= fit * 1.001 ? 0 : nz;
    pending.current = Math.max(0, fAt * (zz || fit) - ax);   // applied once the wider timeline is laid out
    setZoom(zz);
  }, [fit, ppf, frame]);
  useLayoutEffect(() => {
    const el = scroller.current;
    if (el && pending.current !== null) { el.scrollLeft = pending.current; setScroll(el.scrollLeft); pending.current = null; }
  }, [ppf]);

  useEffect(() => {
    const el = scroller.current; if (!el) return;
    const wheel = (e: WheelEvent) => {
      if (!e.ctrlKey && !e.metaKey) return;
      e.preventDefault();
      zoomTo(ppf * (e.deltaY < 0 ? 1.25 : 0.8), e.clientX - el.getBoundingClientRect().left);
    };
    el.addEventListener('wheel', wheel, { passive: false });
    return () => el.removeEventListener('wheel', wheel);
  }, [ppf, zoomTo]);

  // visible window (frames of this tab), with a margin
  const v0 = Math.max(0, scroll / ppf - 60), v1 = Math.min(frames, (scroll + viewW) / ppf + 60);
  const inView = (f: number, e: number) => e - start >= v0 && f - start <= v1 && e > start && f < end;

  const sounds = useMemo(() => {
    const mute = new Set(tl.silent.map(cleanSrc));
    return allSounds.filter((x) => !mute.has(cleanSrc(x.src)));
  }, [allSounds, tl.silent]);
  const blocks = useMemo(() => {
    const b: Record<TrackId, Block[]> = { picture: [], clips: [], voice: [], music: [], sfx: [] };
    if (tl.chapters.length) {
      tl.chapters.forEach((c, i) => b.picture.push({ f: c.start, e: c.start + c.frames, label: `${i + 1}. ${c.title}${c.style ? ` · ${c.style}` : ''}`,
        title: `Chapter ${i + 1}: ${c.title}${c.style ? ` (${c.style})` : ''}`, color: CH_COLORS[i % CH_COLORS.length] }));
    } else {
      b.picture.push({ f: start, e: end, label: name, title: name, color: CH_COLORS[0] });
    }
    for (const s of sounds) {
      const t: TrackId = s.kind === 'clip' ? 'clips' : s.kind === 'voice' ? 'voice' : s.kind === 'music' ? 'music' : 'sfx';
      b[t].push({ f: s.f, e: Math.max(s.e, s.f + 6), label: base(s.src), title: `${base(s.src)}${s.vol != null ? ` · volume ${s.vol}` : ''} · ${fmt(s.f)}` });
    }
    for (const m of tl.music) {
      const inst = m.inst ?? [];
      b.music.push({ f: m.f, e: m.e, label: inst.length ? `${m.name} · ${inst.join(', ')}` : m.name,
        title: [m.name, inst.join(', '), m.bpm ? `${m.bpm} beats a minute` : '', m.chords ? `chords ${m.chords}` : ''].filter(Boolean).join('\n') });
    }
    // sound effects: two lanes so overlapping ones stay readable
    b.sfx.sort((a, c) => a.f - c.f);
    const laneEnd = [-1e9, -1e9];
    for (const s of b.sfx) {
      const px = (s.e - s.f) * ppf, need = Math.max(px, s.label.length * 6.2 + 8) / ppf;
      const l = laneEnd[0] <= s.f ? 0 : laneEnd[1] <= s.f ? 1 : (laneEnd[0] <= laneEnd[1] ? 0 : 1);
      s.lane = l; laneEnd[l] = s.f + need;
    }
    return b;
  }, [tl, sounds, ppf, start, end, name]);

  const wordsMode = ppf * FPS >= 45 && tl.words.length > 0;     // zoomed in far enough: show every word
  const voiceBlocks: Block[] = useMemo(() => wordsMode
    ? tl.words.map((w) => ({ f: w.f, e: w.e, label: w.w, title: w.w }))
    : tl.voice.map((s) => ({ f: s.f, e: s.e, label: s.text, title: s.text })), [tl, wordsMode]);

  // waveforms (drawn for the visible window only)
  const vCan = useRef<HTMLCanvasElement>(null), mCan = useRef<HTMLCanvasElement>(null);
  useEffect(() => {
    const draw = (cv: HTMLCanvasElement | null, peaks: string, color: string) => {
      if (!cv) return;
      const dpr = window.devicePixelRatio || 1, w = viewW, h = cv.clientHeight || 30;
      cv.width = Math.round(w * dpr); cv.height = Math.round(h * dpr);
      const g = cv.getContext('2d')!; g.scale(dpr, dpr); g.clearRect(0, 0, w, h);
      if (!peaks) return;
      g.fillStyle = color;
      const pps = tl.pps;
      for (let x = 0; x < w; x += 1) {
        const f0 = start + (scroll + x) / ppf, f1 = start + (scroll + x + 1) / ppf;
        if (f0 >= end) break;
        const k0 = Math.floor((f0 / FPS) * pps), k1 = Math.max(k0 + 1, Math.ceil((f1 / FPS) * pps));
        let v = 0;
        for (let k = k0; k < k1 && k < peaks.length; k++) v = Math.max(v, peaks.charCodeAt(k) - 48);
        const a = (v / 60) * (h / 2 - 1);
        if (a > 0.3) g.fillRect(x, h / 2 - a, 1, a * 2);
      }
    };
    draw(vCan.current, tl.voicePeaks, 'rgba(120, 220, 160, 0.55)');
    draw(mCan.current, tl.musicPeaks, 'rgba(120, 190, 255, 0.5)');
  }, [tl, viewW, scroll, ppf, start, end, FPS]);

  const pick = (e: React.MouseEvent): { f: number; y: number } => {
    const r = (e.currentTarget as HTMLElement).getBoundingClientRect();
    return { f: Math.max(0, Math.min(frames - 1, Math.round((e.clientX - r.left) / ppf))), y: e.clientY - r.top };
  };
  const rowAt = (y: number) => ROWS.find((r) => y >= TOP[r.id] && y < TOP[r.id] + r.h)?.id;
  const itemAt = (track: TrackId, absF: number, y: number): string => {
    const list = track === 'voice' ? voiceBlocks.concat(blocks.voice) : blocks[track];
    if (track === 'voice' && wordsMode) {
      const w = tl.words.find((x) => x.f <= absF && absF <= x.e);
      const s = tl.voice.find((x) => x.f <= absF && absF <= x.e);
      if (w && s) return `"${w.w}" in "${s.text}"`;
    }
    const lane = track === 'sfx' ? (y - TOP.sfx < RH.sfx / 2 ? 0 : 1) : undefined;
    const hit = list.filter((b) => b.f <= absF && absF <= b.e && (lane === undefined || b.lane === lane))
      .sort((a, b) => (a.e - a.f) - (b.e - b.f))[0];
    if (hit) return track === 'voice' && !wordsMode && voiceBlocks.includes(hit) ? `"${hit.label}"` : hit.label;
    return '';
  };

  const ticks = useMemo(() => {
    const secPx = ppf * FPS;
    const step = [1, 2, 5, 10, 15, 30, 60, 120, 300].find((s) => s * secPx >= 70) ?? 600;
    const out: number[] = [];
    for (let s = Math.ceil(v0 / FPS / step) * step; s * FPS <= v1; s += step) out.push(s);
    return out;
  }, [ppf, v0, v1, FPS]);

  const row = (list: Block[], cls: string, extra?: (b: Block) => React.CSSProperties) =>
    list.filter((b) => inView(b.f, b.e)).map((b, i) => {
      const x = loc(b.f), w = Math.max(2, (b.e - b.f) * ppf);
      return (
        <div key={`${cls}${i}${b.f}`} className={`tl-b ${cls}`} title={b.title}
          style={{ left: x, width: w, background: b.color, ...(extra ? extra(b) : {}) }}>
          {w > 18 ? <span>{b.label}</span> : null}
        </div>
      );
    });

  const absNow = start + frame;
  const now = useMemo(() => {
    const s = tl.voice.find((x) => x.f <= absNow && absNow <= x.e + 6);
    const w = tl.words.find((x) => x.f <= absNow && absNow <= x.e + 2);
    const m = tl.music.find((x) => x.f <= absNow && absNow < x.e);
    const live = (k: Sound['kind'][]) => sounds.filter((x) => k.includes(x.kind) && x.f <= absNow && absNow <= Math.max(x.e, x.f + 15)).map((x) => base(x.src));
    return { s, w, m, fx: live(['sfx', 'clip']), mf: live(['music']), vf: live(['voice']) };
  }, [tl, sounds, absNow]);

  const sentence = now.s ? (() => {
    const ws = tl.words.filter((x) => x.f >= now.s!.f && x.e <= now.s!.e + 1);
    return ws.length ? ws.map((x, i) => <span key={i} className={now.w && x.f === now.w.f ? 'on' : ''}>{x.w} </span>) : now.s.text;
  })() : null;
  const music = now.m
    ? <>{now.m.name}{now.m.inst?.length ? <em> · {now.m.inst.join(', ')}</em> : null}</>
    : now.mf.length ? <>{now.mf.join(', ')}</> : <em>(none)</em>;

  return (
    <div className="tl">
      <div className="tl-top">
        <div className="tl-zoom">
          <button onClick={() => zoomTo(ppf * 0.6)} title="Zoom out (Ctrl + mouse wheel)">−</button>
          <button onClick={() => zoomTo(fit)} className={zoom ? '' : 'on'}>Fit</button>
          <button onClick={() => zoomTo(ppf * 1.7)} title="Zoom in (Ctrl + mouse wheel)">+</button>
        </div>
        <span className="tl-hint">Click to jump · double-click any track to leave a note on that sound{tl.words.length ? ' · zoom in to see every spoken word' : ''}</span>
      </div>
      <div className="tl-body">
        <div className="tl-names" style={{ height: HEIGHT }}>
          {ROWS.map((r) => (
            <div key={r.id} style={{ height: r.h }} className={`tl-name ${r.id === 'music' && !musicHeard ? 'dim' : ''}`}>
              {r.id === 'music' && !musicHeard ? 'A2 Music (not in this tab)' : r.name}
            </div>
          ))}
        </div>
        <div className="tl-lanes" ref={scroller} onScroll={(e) => setScroll((e.target as HTMLDivElement).scrollLeft)}>
          <div className="tl-canvas" style={{ width: W, height: HEIGHT }}
            onClick={(e) => onSeek(pick(e).f)}
            onDoubleClick={(e) => {
              const { f, y } = pick(e); const r = rowAt(y);
              if (!r || r === 'ruler' || r === 'notes') return;
              onTrackNote(r as TrackId, f, itemAt(r as TrackId, start + f, y));
            }}
            onMouseMove={(e) => {
              const { f, y } = pick(e); const r = rowAt(y);
              if (!r || r === 'ruler' || r === 'notes') { setHover(null); return; }
              const it = itemAt(r as TrackId, start + f, y);
              const rect = (e.currentTarget as HTMLElement).getBoundingClientRect();
              setHover(it ? { x: e.clientX - rect.left, y, text: `${fmt(f)} · ${it}` } : null);
            }}
            onMouseLeave={() => setHover(null)}>
            {ROWS.slice(1).map((r) => <div key={r.id} className="tl-row" style={{ top: TOP[r.id], height: r.h }} />)}
            <div className="tl-ruler" style={{ height: RH.ruler }}>
              {ticks.map((s) => <span key={s} style={{ left: s * FPS * ppf }}>{Math.floor(s / 60)}:{String(s % 60).padStart(2, '0')}</span>)}
            </div>
            <div className="tl-track" style={{ top: TOP.picture, height: RH.picture }}>{row(blocks.picture, 'pic')}</div>
            <div className="tl-track" style={{ top: TOP.clips, height: RH.clips }}>{row(blocks.clips, 'clip')}</div>
            <div className="tl-track" style={{ top: TOP.voice, height: RH.voice }}>
              <canvas ref={vCan} className="tl-wave" style={{ left: scroll, width: viewW }} />
              {row(voiceBlocks, wordsMode ? 'voice word' : 'voice')}
              {row(blocks.voice, 'voice extra')}
            </div>
            <div className={`tl-track ${musicHeard ? '' : 'dim'}`} style={{ top: TOP.music, height: RH.music }}>
              <canvas ref={mCan} className="tl-wave" style={{ left: scroll, width: viewW }} />
              {row(blocks.music, 'music')}
            </div>
            <div className="tl-track" style={{ top: TOP.sfx, height: RH.sfx }}>
              {row(blocks.sfx, 'sfx', (b) => ({ top: b.lane ? RH.sfx / 2 : 1, height: RH.sfx / 2 - 2 }))}
            </div>
            <div className="tl-track" style={{ top: TOP.notes, height: RH.notes }}>
              {notes.filter((n) => n.frame !== null && n.frame >= 0 && n.frame < frames).map((n) => (
                <button key={n.id} className={`tl-pin ${n.status}`} style={{ left: n.frame! * ppf - 9 }}
                  title={`${n.n}. ${n.track ? `[${TRACK_NAME[n.track as TrackId] ?? n.track}] ` : ''}${n.text}`}
                  onClick={(e) => { e.stopPropagation(); onSeek(n.frame!); }}>{n.n}</button>
              ))}
            </div>
            {notes.filter((n) => n.track && n.frame !== null && n.frame >= 0 && n.frame < frames && TOP[n.track] !== undefined).map((n) => (
              <div key={`f${n.id}`} className={`tl-flag ${n.status}`} style={{ left: n.frame! * ppf, top: TOP[n.track!] }} />
            ))}
            <div className="tl-head" style={{ left: frame * ppf }} />
            {hover ? <div className="tl-tip" style={{ left: Math.min(hover.x + 12, W - 320), top: hover.y + 14 }}>{hover.text}</div> : null}
          </div>
        </div>
      </div>
      <div className="tl-now">
        <div><b>Voice</b> {sentence ?? (now.vf.length ? now.vf.join(', ') : <em>{tl.words.length ? '(silent)' : '(no word times given)'}</em>)}</div>
        <div><b>Music</b> {musicHeard ? music : <em>not in this tab</em>}</div>
        <div><b>Sounds</b> {now.fx.length ? now.fx.join(', ') : <em>(none right now)</em>}</div>
      </div>
    </div>
  );
};

// for Claude's own checks in the browser
(window as unknown as Record<string, unknown>).__scanSounds = scanSounds;
(window as unknown as Record<string, unknown>).__mediaSeconds = mediaSeconds;
