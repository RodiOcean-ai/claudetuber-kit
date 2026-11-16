/* The owner's review page for the 11 styles (adapted from short-factory/templates/review, 14 Nov 2026).
   One tab per style. Plays the selected style LIVE with the Remotion Player (nothing is rendered), lets the owner pause
   anywhere, click the spot he means and type a note (saved with the style, second, frame and spot to review/notes.json),
   shows Claude's replies under each note, and has an "Approve this build" button per style. Bundled by review/serve.py. */
import React, { useCallback, useEffect, useMemo, useRef, useState } from 'react';
import { createRoot } from 'react-dom/client';
import { Player, PlayerRef } from '@remotion/player';
import { STYLES } from '../src/styles';
import { DURATION as FRAMES, FPS, H, W } from '../src/shared/timing';

const FILL = { width: '100%', height: '100%' };
type Note = { id: string; style: string; t: number; frame: number; x: number | null; y: number | null; text: string; created: string;
  status: 'open' | 'done'; reply?: string; build?: string };
type Build = { label?: string; changes?: string[]; standins?: string[] };
type Approval = { style: string; build: string; at: string };
type State = { builds: Record<string, Build>; notes: Note[]; approvals: Approval[]; code?: number };
type Draft = { frame: number; x: number | null; y: number | null };

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
const firstStyle = () => {
  const h = decodeURIComponent(window.location.hash.slice(1));
  return STYLES.find((s) => s.id === h)?.id ?? (STYLES.find((s) => s.built) ?? STYLES[0]).id;
};

// ?clean: only the video, filling the window (for Claude's frame checks: no tabs, no notes)
const CLEAN = new URLSearchParams(window.location.search).has('clean');

const App: React.FC = () => {
  const player = useRef<PlayerRef>(null);
  const box = useRef<HTMLDivElement>(null);
  const textBox = useRef<HTMLTextAreaElement>(null);
  const target = useRef<number | null>(null);
  const queued = useRef(false);
  const [styleId, setStyleId] = useState(firstStyle);
  const style = STYLES.find((s) => s.id === styleId)!;
  const [frame, setFrame] = useState(0);
  const [state, setState] = useState<State>({ builds: {}, notes: [], approvals: [] });
  const [pointing, setPointing] = useState(false);
  const [draft, setDraft] = useState<Draft | null>(null);
  const [text, setText] = useState('');
  const [error, setError] = useState('');
  const [saving, setSaving] = useState(false);
  const [asking, setAsking] = useState<string | null>(null);   // 'approve' or a note id

  const code0 = useRef<number | undefined>(undefined);
  const [stale, setStale] = useState(false);
  const load = useCallback(() => api('/api/state').then((s: State) => {
    setState(s); setError('');
    if (code0.current === undefined) code0.current = s.code; else if (s.code !== code0.current) setStale(true);
  }).catch(() => setError('Lost contact with the review server. Is it still running?')), []);
  useEffect(() => { load(); const k = setInterval(load, 4000); return () => clearInterval(k); }, [load]);

  const pick = (id: string) => {
    player.current?.pause(); setDraft(null); setPointing(false); setText(''); setAsking(null); setFrame(0);
    setStyleId(id); window.location.hash = id;
  };

  useEffect(() => {
    const p = player.current; if (!p) return;
    (window as unknown as { reviewPlayer: PlayerRef }).reviewPlayer = p;   // for Claude's own checks (seek and read errors)
    const on = (e: { detail: { frame: number } }) => setFrame(e.detail.frame);
    p.addEventListener('frameupdate', on); p.addEventListener('seeked', on);
    return () => { p.removeEventListener('frameupdate', on); p.removeEventListener('seeked', on); };
  }, [styleId]);

  const startNote = useCallback(() => { player.current?.pause(); setDraft(null); setPointing(true); }, []);
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
        // one seek per animation frame however fast the key repeats (a burst of seeks overloaded React, 14 Nov 2026)
        target.current = Math.min(FRAMES - 1, Math.max(0, (target.current ?? p.getCurrentFrame()) + (e.key === 'ArrowLeft' ? -1 : 1) * (e.shiftKey ? 10 : 1)));
        if (!queued.current) {
          queued.current = true;
          requestAnimationFrame(() => { queued.current = false; if (target.current !== null) p.seekTo(target.current); target.current = null; });
        }
      } else if (e.key === 'n' || e.key === 'N') { e.preventDefault(); startNote(); }
    };
    window.addEventListener('keydown', key);
    return () => window.removeEventListener('keydown', key);
  }, [cancel, startNote]);

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
      await api('/api/notes', { style: styleId, frame: draft.frame, t: draft.frame / FPS, x: draft.x, y: draft.y, text: text.trim() });
      setDraft(null); setText(''); await load();
    } catch (err) { setError(`Couldn't save the note: ${err}`); }
    setSaving(false);
  };
  // confirmations happen on the page itself: the app's browser pane silently blocks window.confirm()
  const remove = async (n: Note) => {
    if (asking !== n.id) { setAsking(n.id); return; }
    setAsking(null);
    try { await api(`/api/notes/${n.id}/delete`, {}); load(); } catch (err) { setError(`Couldn't delete the note: ${err}`); }
  };

  const build = state.builds[styleId] ?? {};
  const ready = !!state.builds[styleId];
  const label = build.label || 'this build';
  const approvedOf = (id: string) => {
    const l = state.builds[id]?.label;
    return l ? state.approvals.find((a) => a.style === id && a.build === l) : undefined;
  };
  const approved = approvedOf(styleId);
  const notes = useMemo(() => state.notes.filter((n) => n.style === styleId).sort((a, b) => a.frame - b.frame), [state.notes, styleId]);
  const open = notes.filter((n) => n.status === 'open');
  const approve = async () => {
    setAsking(null);
    try { await api('/api/approve', { style: styleId, build: label }); load(); } catch (err) { setError(`Couldn't send the approval: ${err}`); }
  };
  const num = (n: Note) => notes.indexOf(n) + 1;
  const shown = notes.filter((n) => n.x !== null && Math.abs(n.frame - frame) <= 12);

  if (CLEAN) {
    return (
      <div style={{ position: 'fixed', inset: 0, background: '#000' }}>
        <Player key={styleId} ref={player} component={style.comp} durationInFrames={FRAMES} fps={FPS} compositionWidth={W} compositionHeight={H}
          style={FILL} controls={false} clickToPlay={false} numberOfSharedAudioTags={40} acknowledgeRemotionLicense />
      </div>
    );
  }
  return (
    <>
      <nav className="tabs">
        {STYLES.map((s) => {
          const isReady = !!state.builds[s.id];
          const openCount = state.notes.filter((n) => n.style === s.id && n.status === 'open').length;
          return (
            <button key={s.id} className={`tab${s.id === styleId ? ' on' : ''}${isReady ? '' : ' todo'}`} onClick={() => pick(s.id)}
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
          <div className="frame" ref={box}>
            <Player key={styleId} ref={player} component={style.comp} durationInFrames={FRAMES} fps={FPS} compositionWidth={W} compositionHeight={H}
              style={FILL} controls clickToPlay={false} doubleClickToFullscreen={false} numberOfSharedAudioTags={40}
              spaceKeyToPlayOrPause={false} showVolumeControls allowFullscreen={false} acknowledgeRemotionLicense />
            {shown.map((n) => (
              <button key={n.id} className={`pin ${n.status}`} style={{ left: `${n.x! * 100}%`, top: `${n.y! * 100}%` }}
                title={n.text} onClick={() => seek(n.frame)}>{num(n)}</button>
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
              : <button className="primary" onClick={startNote}>Add a note here <kbd>N</kbd></button>}
          </div>
          <p className="keys">Space play/pause · ← → one frame (Shift: ten) · N add a note</p>
        </section>

        <aside className="side">
          <header>
            <p className="eyebrow">Style {style.n} of 11 · review before rendering</p>
            <h1>{style.name}</h1>
            <p className="label">{ready ? label : 'Not built yet'}</p>
          </header>
          {error ? <p className="error">{error}</p> : null}
          {stale ? (
            <button className="primary" onClick={() => window.location.reload()}>Claude changed the videos: reload to see the new build</button>
          ) : null}

          {draft ? (
            <div className="draft-box">
              <p className="draft-head">New note on <strong>{style.name}</strong> at <strong>{fmt(draft.frame)}</strong>{draft.x === null ? ' (whole frame)' : ''}</p>
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
            <h2>Your notes <span className="count">{open.length} open</span></h2>
            {notes.length === 0 ? <p className="empty">No notes yet. Pause where something is off and press "Add a note here".</p> : null}
            <ol className="notes">
              {notes.map((n) => (
                <li key={n.id} className={n.status}>
                  <div className="note-top">
                    <span className="badge">{num(n)}</span>
                    <button className="time" onClick={() => seek(n.frame)}>{fmt(n.frame)}</button>
                    <span className={`status ${n.status}`}>{n.status === 'done' ? 'Fixed' : 'Open'}</span>
                    {n.status === 'open'
                      ? (asking === n.id
                        ? <span className="link-row"><button className="link danger" onClick={() => remove(n)}>Yes, delete</button>
                            <button className="link" onClick={() => setAsking(null)}>Keep</button></span>
                        : <button className="link" onClick={() => remove(n)}>Delete</button>)
                      : null}
                  </div>
                  <p className="text">{n.text}</p>
                  {n.reply ? <p className="reply"><strong>Claude:</strong> {n.reply}</p> : null}
                </li>
              ))}
            </ol>
          </div>

          {ready ? (
            <div className="block approve">
              {approved
                ? <p className="ok">Approved for rendering · {new Date(approved.at).toLocaleString()}</p>
                : asking === 'approve'
                  ? (
                    <div className="confirm">
                      <p>{open.length
                        ? `You still have ${open.length} open note${open.length > 1 ? 's' : ''}. Approve "${style.name}" anyway?`
                        : `Approve "${style.name}" (${label})? Claude will then render it.`}</p>
                      <div className="row">
                        <button className="approve-btn" onClick={approve}>Yes, approve</button>
                        <button className="ghost" onClick={() => setAsking(null)}>Cancel</button>
                      </div>
                    </div>
                  )
                  : <button className="approve-btn" onClick={() => setAsking('approve')}>Approve this style for rendering</button>}
              <p className="small">Nothing is rendered until you approve here or tell Claude in the chat.</p>
            </div>
          ) : <p className="small">This style is still being built. It shows a placeholder until it's ready.</p>}
        </aside>
      </div>
    </>
  );
};

createRoot(document.getElementById('root')!).render(<App />);
