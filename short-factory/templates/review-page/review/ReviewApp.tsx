/* The review page (free kit template). One tab per item in review/contract.json: the whole video, each chapter, a
   cover, one style... Plays the selected item LIVE with the Remotion Player (nothing is rendered). The person pauses
   anywhere and clicks the spot they mean (N), comments on the whole tab (C), or double-clicks a track on the editor-style
   timeline under the player (picture, clips, voice, music, sound effects) to note one exact sound. Notes are saved with
   the tab, second, frame, spot and track to review/notes.json; Claude's replies show under each note; each tab has an
   approve button. The notes list scrolls on its own and follows the moment (and chapter) that is playing.
   Bundled by review/serve.py with esbuild. The tabs come from review/items.gen.tsx (written by review/make_items.py). */
import React, { useCallback, useEffect, useMemo, useRef, useState } from 'react';
import { createRoot } from 'react-dom/client';
import { Player, PlayerRef } from '@remotion/player';
import { FPS, ITEMS, TITLE } from './items.gen';
import { Sound, TL, Timeline, TrackId, TRACK_NAME, cleanSrc, mediaSeconds, normTl, scanSounds } from './Timeline';

const FILL = { width: '100%', height: '100%' };
// frame null = a comment on the whole tab (key C); track = a note on one track of the timeline (voice, music...)
// (the field is called `style` for the tab id: the first page had one tab per animation style)
type Note = { id: string; style: string; t: number | null; frame: number | null; x: number | null; y: number | null; text: string; created: string;
  status: 'open' | 'done'; reply?: string; build?: string; track?: TrackId | null; item?: string | null };
type Build = { label?: string; changes?: string[]; standins?: string[] };
type Approval = { style: string; build: string; at: string };
type State = { builds: Record<string, Build>; notes: Note[]; approvals: Approval[]; code?: number };
type Draft = { frame: number | null; x: number | null; y: number | null; track?: TrackId; item?: string };
const fr = (n: { frame: number | null }) => n.frame ?? -1;   // whole-tab comments first (same order as serve.py)

const fmt = (f: number) => {
  const s = f / FPS, m = Math.floor(s / 60);
  return `${m}:${(s - m * 60).toFixed(2).padStart(5, '0')}`;
};
// serve.py puts a new random token into the page on every start; every write sends it back (other web pages can't read it)
const TOKEN = document.querySelector('meta[name="review-token"]')?.getAttribute('content') ?? '';
const api = async (path: string, body?: unknown) => {
  const r = await fetch(path, body === undefined ? undefined : {
    method: 'POST', headers: { 'Content-Type': 'application/json', 'X-Review-Token': TOKEN }, body: JSON.stringify(body) });
  if (!r.ok) throw new Error(await r.text());
  return r.json();
};
const typing = (e: KeyboardEvent) => {
  const el = e.target as HTMLElement | null;
  return !!el && (el.tagName === 'INPUT' || el.tagName === 'TEXTAREA' || el.isContentEditable);
};
const firstItem = () => {
  const h = decodeURIComponent(window.location.hash.slice(1));
  return ITEMS.find((s) => s.id === h)?.id ?? ITEMS[0].id;
};

// ?clean: only the video, filling the window (for Claude's own frame checks: no tabs, no notes)
const CLEAN = new URLSearchParams(window.location.search).has('clean');

const App: React.FC = () => {
  const player = useRef<PlayerRef>(null);
  const box = useRef<HTMLDivElement>(null);
  const textBox = useRef<HTMLTextAreaElement>(null);
  const target = useRef<number | null>(null);
  const queued = useRef(false);
  const [itemId, setItemId] = useState(firstItem);
  const item = ITEMS.find((s) => s.id === itemId) ?? ITEMS[0];
  const [frame, setFrame] = useState(0);
  const [state, setState] = useState<State>({ builds: {}, notes: [], approvals: [] });
  const [pointing, setPointing] = useState(false);
  const [draft, setDraft] = useState<Draft | null>(null);
  const [text, setText] = useState('');
  const [error, setError] = useState('');
  const [saving, setSaving] = useState(false);
  const [asking, setAsking] = useState<string | null>(null);   // 'approve' or a note id
  const [tl, setTl] = useState<TL | null>(null);
  const [playing, setPlaying] = useState(false);
  const loadTl = useCallback(() => api('/api/timeline').then((x) => setTl(normTl(x, FPS))).catch(() => undefined), []);
  useEffect(() => { loadTl(); }, [loadTl]);
  useEffect(() => { document.title = `${TITLE}: review before rendering`; }, []);

  const code0 = useRef<number | undefined>(undefined);
  const [stale, setStale] = useState(false);
  const load = useCallback(() => api('/api/state').then((s: State) => {
    setState(s); setError('');
    if (code0.current === undefined) code0.current = s.code; else if (s.code !== code0.current) setStale(true);
  }).catch(() => setError('Lost contact with the review server. Is it still running?')), []);
  useEffect(() => { load(); const k = setInterval(load, 4000); return () => clearInterval(k); }, [load]);

  const pick = (id: string) => {
    player.current?.pause(); setDraft(null); setPointing(false); setText(''); setAsking(null); setFrame(0);
    setItemId(id); window.location.hash = id;
  };

  useEffect(() => {
    const p = player.current; if (!p) return;
    (window as unknown as { reviewPlayer: PlayerRef }).reviewPlayer = p;   // for Claude's own checks (seek and read errors)
    const on = (e: { detail: { frame: number } }) => setFrame(e.detail.frame);
    const pl = () => setPlaying(true), pa = () => setPlaying(false);
    p.addEventListener('frameupdate', on); p.addEventListener('seeked', on);
    p.addEventListener('play', pl); p.addEventListener('pause', pa); p.addEventListener('ended', pa);
    return () => {
      p.removeEventListener('frameupdate', on); p.removeEventListener('seeked', on);
      p.removeEventListener('play', pl); p.removeEventListener('pause', pa); p.removeEventListener('ended', pa);
    };
  }, [itemId]);

  // Chapters: a chapter tab shows its own stretch of the timeline; a tab that plays several chapters (the whole video)
  // knows which chapter is on screen, so the notes list can follow it.
  const hasTl = item.timeline;
  const chaps = tl?.chapters ?? [];
  const absFrame = item.start + frame;
  const ownChap = item.chapter ? chaps.find((c) => c.id === item.chapter) : undefined;
  const curChap = ownChap ?? (hasTl ? chaps.find((c) => c.start <= absFrame && absFrame < c.start + c.frames) : undefined);
  const spans = !item.chapter && !!curChap;

  // Sound effects, clips and other sounds for the timeline: read from the composition on screen every 2 s while it plays
  // (things that only appear at some moments are found as the video plays) and saved on the server per tab
  // (review/sounds.json). A new build (the project's code changed) starts the tab's list afresh.
  const tlRef = useRef<TL | null>(null); tlRef.current = tl;
  useEffect(() => {
    if (!hasTl) return;
    const code = state.code ?? 0, key = item.id, a = item.start, b = item.start + item.frames;
    let alive = true, busy = false;
    const run = async () => {
      const el = box.current, t = tlRef.current;
      if (!alive || busy || !el || !t) return;
      busy = true;
      try {
        const skip = new Set([...t.voiceFiles, ...t.musicFiles].map(cleanSrc));
        const raw = scanSounds(el, a, skip).filter((x) => x.f >= a && x.f < b);
        const stored = t.sounds[key];
        const same = !!stored && stored.code === code;
        if (!raw.length && same) return;
        const keep = same ? stored.items : [];
        const have = new Set(keep.map((o) => `${o.f}|${o.src}`));
        const fresh = raw.filter((x) => !have.has(`${x.f}|${x.src}`));
        if (!fresh.length && same) return;
        const add: Sound[] = await Promise.all(fresh.map(async (x) => {
          const sec = await mediaSeconds(x.src);
          const len = Math.min(x.dur ?? 1e9, Math.max(1, Math.round(sec * FPS)));
          return { f: x.f, e: Math.min(b, x.f + len), src: x.src, vol: x.vol, kind: x.kind };
        }));
        if (!alive) return;
        await api('/api/sounds', { key, code, items: keep.concat(add) });
        await loadTl();
      } catch { /* try again on the next tick */ } finally { busy = false; }
    };
    const k0 = setTimeout(run, 700), k = setInterval(run, 2000);
    return () => { alive = false; clearTimeout(k0); clearInterval(k); };
  }, [hasTl, item.id, item.start, item.frames, state.code, loadTl]);

  const startNote = useCallback(() => { player.current?.pause(); setDraft(null); setPointing(true); }, []);
  const general = useCallback(() => {
    player.current?.pause(); setPointing(false); setDraft({ frame: null, x: null, y: null });
    setTimeout(() => textBox.current?.focus(), 30);
  }, []);
  const trackNote = (track: TrackId, f: number, what: string) => {
    player.current?.pause(); player.current?.seekTo(f); setPointing(false);
    setDraft({ frame: f, x: null, y: null, track, item: what || undefined });
    setTimeout(() => textBox.current?.focus(), 30);
  };
  const cancel = useCallback(() => { setPointing(false); setDraft(null); setText(''); }, []);
  const seek = (f: number) => { player.current?.pause(); player.current?.seekTo(f); };

  useEffect(() => {
    const key = (e: KeyboardEvent) => {
      if (e.key === 'Escape') { cancel(); return; }
      if (typing(e)) return;
      const p = player.current; if (!p) return;
      if (e.code === 'Space') { e.preventDefault(); p.isPlaying() ? p.pause() : p.play(); }
      else if (e.key === 'ArrowLeft' || e.key === 'ArrowRight') {
        e.preventDefault(); p.pause();
        // one seek per animation frame however fast the key repeats (a burst of seeks can overload React)
        target.current = Math.min(item.frames - 1, Math.max(0, (target.current ?? p.getCurrentFrame()) + (e.key === 'ArrowLeft' ? -1 : 1) * (e.shiftKey ? 10 : 1)));
        if (!queued.current) {
          queued.current = true;
          requestAnimationFrame(() => { queued.current = false; if (target.current !== null) p.seekTo(target.current); target.current = null; });
        }
      } else if (e.key === 'n' || e.key === 'N') { e.preventDefault(); startNote(); }
      else if (e.key === 'c' || e.key === 'C') { e.preventDefault(); general(); }
    };
    window.addEventListener('keydown', key);
    return () => window.removeEventListener('keydown', key);
  }, [cancel, startNote, general, item.frames]);

  const place = (e: React.MouseEvent) => {
    const r = box.current!.getBoundingClientRect();
    const f = player.current?.getCurrentFrame() ?? frame;
    setDraft({ frame: f, x: (e.clientX - r.left) / r.width, y: (e.clientY - r.top) / r.height });
    setPointing(false);
    setTimeout(() => textBox.current?.focus(), 30);
  };
  const wholeFrame = () => {
    setDraft({ frame: player.current?.getCurrentFrame() ?? frame, x: null, y: null });
    setPointing(false);
    setTimeout(() => textBox.current?.focus(), 30);
  };
  const save = async () => {
    if (!draft || !text.trim()) return;
    setSaving(true);
    try {
      await api('/api/notes', { style: itemId, frame: draft.frame, t: draft.frame === null ? null : draft.frame / FPS, x: draft.x, y: draft.y,
        track: draft.track ?? null, item: draft.item ?? null, text: text.trim() });
      setDraft(null); setText(''); await load();
    } catch (err) { setError(`Couldn't save the note: ${err}`); }
    setSaving(false);
  };
  // confirmations happen on the page itself: some browser panes silently block window.confirm()
  const remove = async (n: Note) => {
    if (asking !== n.id) { setAsking(n.id); return; }
    setAsking(null);
    try { await api(`/api/notes/${n.id}/delete`, {}); load(); } catch (err) { setError(`Couldn't delete the note: ${err}`); }
  };

  const build = state.builds[itemId] ?? {};
  const ready = !!state.builds[itemId];
  const label = build.label || 'this build';
  const approvedOf = (id: string) => {
    const l = state.builds[id]?.label;
    return l ? state.approvals.find((a) => a.style === id && a.build === l) : undefined;
  };
  const approved = approvedOf(itemId);
  const notes = useMemo(() => state.notes.filter((n) => n.style === itemId).sort((a, b) => fr(a) - fr(b)), [state.notes, itemId]);
  const open = notes.filter((n) => n.status === 'open');
  const approve = async () => {
    setAsking(null);
    try { await api('/api/approve', { style: itemId, build: label }); load(); } catch (err) { setError(`Couldn't send the approval: ${err}`); }
  };
  const num = (n: Note) => notes.indexOf(n) + 1;
  const shown = notes.filter((n) => n.x !== null && n.frame !== null && Math.abs(n.frame - frame) <= 12);

  // The notes list follows the video: notes near the moment playing now (or in the chapter playing now) are marked, the
  // latest note at or just before this moment is highlighted and scrolled to the top of the list. Scrolling the list by
  // hand pauses that for 8 s; the "Following the video" button switches it off.
  const [follow, setFollow] = useState(true);
  const listBox = useRef<HTMLDivElement>(null);
  const itemEls = useRef<Record<string, HTMLLIElement | null>>({});
  const handUntil = useRef(0);
  const sec = spans && curChap
    ? { a: curChap.start - item.start, b: curChap.start + curChap.frames - item.start }
    : { a: frame - 5 * FPS, b: frame + 5 * FPS };
  const isHere = (n: Note) => n.frame !== null && n.frame >= sec.a && n.frame < sec.b;
  const hereCount = notes.filter(isHere).length;
  const nowNote = useMemo(() => {
    let best: Note | null = null;
    for (const n of notes) if (n.frame !== null && n.frame <= frame + 15 && n.frame >= sec.a - 1) best = n;
    return best;
  }, [notes, frame, sec.a]);
  useEffect(() => {
    if (!follow || !nowNote || Date.now() < handUntil.current) return;
    const el = itemEls.current[nowNote.id], lb = listBox.current;
    if (el && lb) lb.scrollTo({ top: Math.max(0, el.offsetTop - 6), behavior: 'smooth' });
  }, [nowNote?.id, follow]);
  const byHand = () => { handUntil.current = Date.now() + 8000; };

  // the video box keeps the item's own shape (wide, square or upright), leaving room for the timeline under it
  const ratio = item.w / item.h;
  const frameStyle: React.CSSProperties = {
    aspectRatio: `${item.w} / ${item.h}`,
    maxWidth: `max(${Math.round(315 * ratio)}px, calc((100vh - ${hasTl ? 610 : 190}px) * ${ratio.toFixed(4)}))`,
  };
  const chapIdx = ownChap ? chaps.indexOf(ownChap) : -1;
  const eyebrow = chapIdx >= 0 ? `Chapter ${chapIdx + 1} of ${chaps.length}` : TITLE;

  if (CLEAN) {
    return (
      <div style={{ position: 'fixed', inset: 0, background: '#000' }}>
        <Player key={itemId} ref={player} component={item.comp} durationInFrames={item.frames} fps={FPS} compositionWidth={item.w} compositionHeight={item.h}
          style={FILL} controls={false} clickToPlay={false} numberOfSharedAudioTags={0} acknowledgeRemotionLicense />
      </div>
    );
  }
  return (
    <>
      <nav className="tabs">
        {ITEMS.map((s) => {
          const isReady = !!state.builds[s.id];
          const openCount = state.notes.filter((n) => n.style === s.id && n.status === 'open').length;
          return (
            <button key={s.id} className={`tab${s.id === itemId ? ' on' : ''}${isReady ? '' : ' todo'}`} onClick={() => pick(s.id)}
              title={isReady ? (approvedOf(s.id) ? 'Approved' : 'Ready for your review') : 'Not built yet'}>
              <span className={`num${approvedOf(s.id) ? ' ok' : isReady ? ' ready' : ''}`}>{s.n}</span>
              {s.name}
              {openCount ? <span className="dot">{openCount}</span> : null}
            </button>
          );
        })}
      </nav>
      <div className="page">
        <section className="stage">
          <div className="frame" ref={box} style={frameStyle}>
            <Player key={itemId} ref={player} component={item.comp} durationInFrames={item.frames} fps={FPS} compositionWidth={item.w} compositionHeight={item.h}
              style={FILL} controls clickToPlay={false} doubleClickToFullscreen={false} numberOfSharedAudioTags={0}
              spaceKeyToPlayOrPause={false} showVolumeControls allowFullscreen={false} acknowledgeRemotionLicense />
            {shown.map((n) => (
              <button key={n.id} className={`pin ${n.status}`} style={{ left: `${n.x! * 100}%`, top: `${n.y! * 100}%` }}
                title={n.text} onClick={() => seek(n.frame!)}>{num(n)}</button>
            ))}
            {draft && draft.x !== null ? <div className="pin draft" style={{ left: `${draft.x * 100}%`, top: `${draft.y! * 100}%` }}>+</div> : null}
            {pointing ? (
              <div className="catcher" onClick={place}>
                <div className="hint">Click the spot you mean<span>Esc to cancel</span></div>
              </div>
            ) : null}
          </div>
          <div className="bar">
            <span className="now">{fmt(frame)} <small>frame {frame}</small></span>
            {pointing
              ? <><button className="ghost" onClick={wholeFrame}>No spot, just this moment</button><button className="ghost" onClick={cancel}>Cancel</button></>
              : <><button className="primary" onClick={startNote}>Add a note here <kbd>N</kbd></button>
                  <button className="ghost" onClick={general}>Comment on the whole video <kbd>C</kbd></button></>}
          </div>
          <p className="keys">Space play/pause · ← → one frame (Shift: ten) · N note on the picture · C comment on the whole video{hasTl ? ' · double-click a track below: note on that sound' : ''}</p>
          {hasTl && tl ? (
            <Timeline tl={tl} sounds={tl.sounds[item.id]?.items ?? []} name={item.name} start={item.start} frames={item.frames} frame={frame}
              playing={playing} musicHeard={item.music}
              notes={notes.map((n) => ({ id: n.id, n: num(n), frame: n.frame, status: n.status, track: n.track, text: n.text }))}
              onSeek={seek} onTrackNote={trackNote} />
          ) : null}
        </section>

        <aside className="side">
          <header>
            <p className="eyebrow">{eyebrow} · review before rendering</p>
            <h1>{item.name}</h1>
            <p className="label">{ready ? label : 'Not built yet'}</p>
          </header>
          {error ? <p className="error">{error}</p> : null}
          {stale ? (
            <button className="primary" onClick={() => window.location.reload()}>Claude changed the videos: reload to see the new build</button>
          ) : null}

          {draft ? (
            <div className="draft-box">
              <p className="draft-head">{draft.frame === null
                ? <>New comment on <strong>{item.name}</strong> as a whole (not tied to one moment)</>
                : draft.track
                  ? <>New note on the <strong>{TRACK_NAME[draft.track]}</strong> track at <strong>{fmt(draft.frame)}</strong>{draft.item ? <><br /><span className="item">{draft.item}</span></> : null}</>
                  : <>New note on <strong>{item.name}</strong> at <strong>{fmt(draft.frame)}</strong>{draft.x === null ? ' (whole frame)' : ''}</>}</p>
              <textarea ref={textBox} autoFocus value={text} onChange={(e) => setText(e.target.value)} rows={3}
                placeholder="What's wrong here, or what should change?"
                onKeyDown={(e) => { if (e.key === 'Enter' && (e.ctrlKey || e.metaKey)) save(); }} />
              <div className="row">
                <button className="primary" disabled={!text.trim() || saving} onClick={save}>{saving ? 'Saving…' : 'Save note'}</button>
                <button className="ghost" onClick={cancel}>Cancel</button>
              </div>
            </div>
          ) : null}

          {build.changes?.length ? (
            <div className="block">
              <h2>What's in this build</h2>
              <ul>{build.changes.map((c, i) => <li key={i}>{c}</li>)}</ul>
            </div>
          ) : null}
          {build.standins?.length ? (
            <div className="block warn">
              <h2>Placeholders (not final)</h2>
              <ul>{build.standins.map((c, i) => <li key={i}>{c}</li>)}</ul>
            </div>
          ) : null}

          <div className="block">
            <h2 className="notes-head">Your notes <span className="count">{open.length} open</span>
              <button className={`follow${follow ? ' on' : ''}`} onClick={() => { setFollow(!follow); handUntil.current = 0; }}
                title="Keep the list on the notes for the moment that's playing">{follow ? '● Following the video' : '○ Follow the video'}</button>
            </h2>
            {notes.length ? <p className="here-line">{spans && curChap
              ? <>Now in <strong>{curChap.title}</strong>: {hereCount ? `${hereCount} note${hereCount > 1 ? 's' : ''} (marked)` : 'no notes here yet'}</>
              : <>Notes near this moment are marked</>}</p> : null}
            {notes.length === 0 ? <p className="empty">No notes yet. Pause where something is off and press "Add a note here".</p> : null}
            <div className="notes-scroll" ref={listBox} onWheel={byHand} onTouchMove={byHand} onMouseDown={byHand}>
            <ol className="notes">
              {notes.map((n) => (
                <li key={n.id} ref={(el) => { itemEls.current[n.id] = el; }}
                  className={`${n.status}${isHere(n) ? ' here' : ''}${nowNote?.id === n.id ? ' now' : ''}`}>
                  <div className="note-top">
                    <span className="badge">{num(n)}</span>
                    {n.frame === null
                      ? <span className="whole">Whole video</span>
                      : <button className="time" onClick={() => seek(n.frame!)}>{fmt(n.frame)}</button>}
                    {n.track ? <span className={`trk ${n.track}`}>{TRACK_NAME[n.track] ?? n.track}</span> : null}
                    <span className={`status ${n.status}`}>{n.status === 'done' ? 'Fixed' : 'Open'}</span>
                    {n.status === 'open'
                      ? (asking === n.id
                        ? <span className="link-row"><button className="link danger" onClick={() => remove(n)}>Yes, delete</button>
                            <button className="link" onClick={() => setAsking(null)}>Keep</button></span>
                        : <button className="link" onClick={() => remove(n)}>Delete</button>)
                      : null}
                  </div>
                  {n.item ? <p className="item">{n.item}</p> : null}
                  <p className="text">{n.text}</p>
                  {n.reply ? <p className="reply"><strong>Claude:</strong> {n.reply}</p> : null}
                </li>
              ))}
            </ol>
            </div>
          </div>

          {ready ? (
            <div className="block approve">
              {approved
                ? <p className="ok">Approved for rendering · {new Date(approved.at).toLocaleString()}</p>
                : asking === 'approve'
                  ? (
                    <div className="confirm">
                      <p>{open.length
                        ? `You still have ${open.length} open note${open.length > 1 ? 's' : ''}. Approve "${item.name}" anyway?`
                        : `Approve "${item.name}" (${label})? Claude will then render it.`}</p>
                      <div className="row">
                        <button className="approve-btn" onClick={approve}>Yes, approve</button>
                        <button className="ghost" onClick={() => setAsking(null)}>Cancel</button>
                      </div>
                    </div>
                  )
                  : <button className="approve-btn" onClick={() => setAsking('approve')}>Approve this for rendering</button>}
              <p className="small">Nothing is rendered until you approve here or tell Claude in the chat.</p>
            </div>
          ) : <p className="small">This one is still being built. Claude marks it ready when it is.</p>}
        </aside>
      </div>
    </>
  );
};

createRoot(document.getElementById('root')!).render(<App />);
