"""Comp several AI-voice takes into one natural narration (the natural-ai-voice method, stages 5-6).
Usage:
  python -I voice_comp.py <takes_dir> <voice_script.txt>                 propose a comp and render voice/comp_draft.wav
  python -I voice_comp.py <takes_dir> <voice_script.txt> --use comp.json  re-render after the owner changed choices
  python -I voice_comp.py <takes_dir> <voice_script.txt> --finish [--speed 1.04] [--hold 1.1]   tighten + clean-up chain -> voice/final_voice.wav
  python -I voice_comp.py <takes_dir> <voice_script.txt> --batches <out_dir>  one comped file per batch (B03.wav ...)
voice_script.txt: one batch per line, "B03: text of 2-4 sentences". Tags [..] and <break .../> are ignored for matching.
A "||" after a sentence marks a deliberate pause (kept at 0.8 s); every other join is tightened to 0.12 s.
Takes: <takes_dir>/B03_t1.mp3, B03_t2.wav ... Whisper transcripts are cached next to each take (.words.json)."""
import difflib, glob, json, os, re, subprocess, sys
import numpy as np, librosa, soundfile as sf

TAKES, SCRIPT = sys.argv[1], sys.argv[2]
USE = sys.argv[sys.argv.index('--use') + 1] if '--use' in sys.argv else None
FINISH = '--finish' in sys.argv
SPEED = float(sys.argv[sys.argv.index('--speed') + 1]) if '--speed' in sys.argv else 1.0
OUT = os.path.join(os.path.dirname(os.path.abspath(TAKES)), 'voice') if os.path.basename(os.path.normpath(TAKES)) == 'takes' else os.path.join(TAKES, 'voice')
os.makedirs(OUT, exist_ok=True)
SR = 44100
JOIN, HOLD, PAD = 0.12, (float(sys.argv[sys.argv.index('--hold') + 1]) if '--hold' in sys.argv else 0.8), 0.03   # --hold 1.1: longer deliberate pauses
norm = lambda w: re.sub(r"[^a-z0-9']", '', w.lower())
ONES = 'zero one two three four five six seven eight nine ten eleven twelve thirteen fourteen fifteen sixteen seventeen eighteen nineteen'.split()
TENS = 'x x twenty thirty forty fifty sixty seventy eighty ninety'.split()


def n2w(n):
    """850 -> 'eight hundred and fifty', so Whisper's digits match a script written in words."""
    if n < 20: return ONES[n]
    if n < 100: return TENS[n // 10] + ('' if n % 10 == 0 else ' ' + ONES[n % 10])
    if n < 1000: return ONES[n // 100] + ' hundred' + ('' if n % 100 == 0 else ' and ' + n2w(n % 100))
    if n < 1_000_000: return n2w(n // 1000) + ' thousand' + ('' if n % 1000 == 0 else ' ' + n2w(n % 1000))
    return n2w(n // 1_000_000) + ' million' + ('' if n % 1_000_000 == 0 else ' ' + n2w(n % 1_000_000))


def spelled(ws):
    """Whisper writes '300'; the script says 'three hundred'. Expand digits into words (each keeps the number's timing);
    years like 2024 stay as they are."""
    out = []
    for w in ws:
        m = re.fullmatch(r'[$]?(\d[\d,]*?)[.,!?;:]*', w['w'].replace(' ', ''))
        n = int(m.group(1).replace(',', '')) if m else None
        if n is None or (1900 < n < 2100 and ',' not in m.group(1)):
            out.append(w)
        else:
            spoken = re.sub(r'^one (hundred|thousand|million)', r'a \1', n2w(n))   # scripts say "a thousand", not "one thousand"
            if w['w'].lstrip().startswith('$'):
                spoken += ' dollars'                                            # "$1,000" is said "a thousand dollars"
            out += [{'w': t, 's': w['s'], 'e': w['e']} for t in spoken.split()]
    return out


def parse_script():
    batches = {}
    for line in open(SCRIPT, encoding='utf-8-sig'):
        m = re.match(r'\s*(B\d+)\s*:\s*(.+)', line)
        if not m:
            continue
        t = re.sub(r'<[^>]+>|\[[^\]]*\]', ' ', m.group(2))
        sents = []
        for s in re.split(r'(?<![DM]r\.)(?<=[.!?…])\s+(?!\|\|)|(?<=\|\|)\s*', t):
            hold = '||' in s
            s = s.replace('||', '').strip()
            if re.search(r'[A-Za-z0-9]', s):
                sents.append({'text': s, 'hold': hold, 'words': [norm(w) for w in s.replace('-', ' ').split() if norm(w)]})
        batches[m.group(1)] = sents
    return batches


_model = None
def join_numbers(ws):
    """Whisper sometimes splits a number ("231", ",000"); glue such pieces back onto the word before."""
    out = []
    for w in ws:
        if out and re.match(r'^[,.]\d', w['w']) and re.search(r'\d$', out[-1]['w']):
            out[-1] = {'w': out[-1]['w'].strip() + w['w'].strip(), 's': out[-1]['s'], 'e': w['e']}
        else:
            out.append(w)
    return out


def words_of(path):
    cache = os.path.splitext(path)[0] + '.words.json'
    if os.path.exists(cache):
        return join_numbers(json.load(open(cache, encoding='utf-8')))
    global _model
    if _model is None:
        import whisper
        _model = whisper.load_model('large-v3-turbo')
    r = _model.transcribe(path, language='en', word_timestamps=True, condition_on_previous_text=False,
                          initial_prompt='Um, so, uh... I mean, okay. Wait, what?')
    ws = [{'w': w['word'].strip(), 's': w['start'], 'e': w['end']} for seg in r['segments'] for w in seg.get('words', [])]
    json.dump(ws, open(cache, 'w', encoding='utf-8'), indent=0)
    return join_numbers(ws)


def life(y, sr):
    """How alive a stretch sounds: pitch movement + loudness movement (both in their own units, added)."""
    if len(y) < sr * 0.3:
        return 0.0
    f0 = librosa.yin(y, fmin=65, fmax=400, sr=sr, frame_length=2048, hop_length=512)
    rms = librosa.feature.rms(y=y, hop_length=512)[0]
    v = rms > np.percentile(rms, 40)
    p = 12 * np.log2(f0[v[:len(f0)]] / 100.0) if v.any() else np.array([0.0])
    return float(np.std(p) + 0.15 * np.std(20 * np.log10(rms[v] + 1e-9)))


def segments(batches):
    """For every take, find each script sentence (and its two halves) inside the take."""
    out = {}
    for path in sorted(glob.glob(os.path.join(TAKES, 'B*_t*.*'))):
        if path.endswith('.json'):
            continue
        b = re.match(r'(B\d+)_t(\d+)', os.path.basename(path))
        if not b or b.group(1) not in batches:
            continue
        ws = spelled(words_of(path))
        y, _ = librosa.load(path, sr=SR, mono=True)
        toks = [norm(w['w']) for w in ws]
        for si, s in enumerate(batches[b.group(1)]):
            sm = difflib.SequenceMatcher(None, toks, s['words'], autojunk=False)
            blocks = [m for m in sm.get_matching_blocks() if m.size]
            if not blocks:
                continue
            i0, i1 = blocks[0].a, blocks[-1].a + blocks[-1].size - 1
            got = toks[i0:i1 + 1]
            acc = difflib.SequenceMatcher(None, got, s['words']).ratio()
            st, en = ws[i0]['s'], ws[i1]['e']
            seg = y[int(st * SR):int(en * SR)]
            key = (b.group(1), si)
            row = {'take': os.path.basename(path), 'path': path, 's': round(st, 3), 'e': round(en, 3), 'accuracy': round(acc, 2),
                   'life': round(life(seg, SR), 3), 'wps': round(len(got) / max(en - st, 0.1), 2)}
            # halves: split at the longest word gap inside the sentence (only for 10+ word sentences)
            if i1 - i0 >= 9:
                gaps = [(ws[k + 1]['s'] - ws[k]['e'], k) for k in range(i0 + 3, i1 - 3)]
                if gaps:
                    g, k = max(gaps)
                    mid = (ws[k]['e'] + ws[k + 1]['s']) / 2
                    row['split_word'] = ws[k]['w']
                    row['half_life'] = [round(life(y[int(st * SR):int(mid * SR)], SR), 3), round(life(y[int(mid * SR):int(en * SR)], SR), 3)]
                    row['mid'] = round(mid, 3)
            out.setdefault(key, []).append(row)
    return out


def propose(batches, segs):
    comp = []
    for b, sents in batches.items():
        for si, s in enumerate(sents):
            cands = [r for r in segs.get((b, si), []) if r['accuracy'] >= 0.9]
            if not cands:
                comp.append({'batch': b, 'sentence': si, 'text': s['text'], 'hold': s['hold'], 'pick': None,
                             'note': 'NO CLEAN TAKE: regenerate this batch'})
                continue
            best = max(cands, key=lambda r: r['life'])
            pick = [{'take': best['take'], 's': best['s'], 'e': best['e']}]
            note = f"{best['take']} (life {best['life']})"
            halves = [r for r in cands if 'mid' in r]
            if len(halves) >= 2:                      # best first half from one take, best second half from another
                a = max(halves, key=lambda r: r['half_life'][0]); c = max(halves, key=lambda r: r['half_life'][1])
                base = sum(best['half_life']) if 'half_life' in best else 2 * best['life']
                if a['take'] != c['take'] and norm(a['split_word']) == norm(c['split_word']) and a['half_life'][0] + c['half_life'][1] > 1.1 * base:
                    pick = [{'take': a['take'], 's': a['s'], 'e': a['mid']}, {'take': c['take'], 's': c['mid'], 'e': c['e']}]
                    note = f"{a['take']} up to '{a['split_word']}', then {c['take']}"
            comp.append({'batch': b, 'sentence': si, 'text': s['text'], 'hold': s['hold'], 'pick': pick, 'note': note})
    return comp


FR = int(0.01 * SR)  # 10 ms frames for finding the quiet gap


def snap(y, t, direction, reach):
    """Whisper word times are often early at the end of a word. Move a cut to where the voice has really gone quiet:
    the first 50 ms run 35 dB below the take's average, searched forward (ends) or backward (starts); else the quietest frame."""
    ref = 20 * np.log10(np.sqrt(np.mean(y ** 2)) + 1e-9)
    i0 = int(t * SR)
    idx = range(i0, min(i0 + int(reach * SR), len(y) - FR), FR) if direction > 0 else range(i0 - FR, max(i0 - int(reach * SR), 0), -FR)
    lv = [(i, 20 * np.log10(np.sqrt(np.mean(y[i:i + FR] ** 2)) + 1e-9) - ref) for i in idx]
    if not lv:
        return t
    for k in range(len(lv) - 4):
        if all(v < -35 for _, v in lv[k:k + 5]):
            i = lv[k][0] + (2 * FR if direction > 0 else FR - 1)  # a little into the silence
            return i / SR
    return min(lv, key=lambda r: r[1])[0] / SR


def quietest(y, g0, g1):
    """The quietest 10 ms point between two word times (the real breath gap between two words)."""
    a, b = int(g0 * SR), int(g1 * SR)
    if b - a < 2 * FR:
        return (g0 + g1) / 2
    lv = [(i, np.mean(y[i:i + FR] ** 2)) for i in range(a, b - FR, FR // 2)]
    return (min(lv, key=lambda r: r[1])[0] + FR // 2) / SR


def render_clean(comp, path, segs):
    """Joins without glitches. Sentences that follow each other in the same take stay as one continuous piece of audio
    (no cut); a take changes only where BOTH takes have a real gap between the two sentences, and the cut sits at the
    quietest point of that gap, so no word loses or repeats its first or last sound. Holds cut in the gap too."""
    rows = {}                                              # (batch, sentence, take) -> timing row
    for k, rs in segs.items():
        for r in rs:
            if r['accuracy'] >= 0.9:
                rows[(k[0], k[1], r['take'])] = r
    cache = {}
    def audio(take):
        f = os.path.join(TAKES, take)
        if f not in cache:
            cache[f] = librosa.load(f, sr=SR, mono=True)[0]
        return cache[f]
    gap = lambda b, i, t: (rows[(b, i, t)]['e'], rows[(b, i + 1, t)]['s']) if (b, i, t) in rows and (b, i + 1, t) in rows else None
    parts, switched, kept = [], 0, 0
    by_batch = {}
    for c in comp:
        by_batch.setdefault(c['batch'], []).append(c)
    for b, cs in by_batch.items():
        cs = [c for c in cs if c['pick']]
        takes = [c['pick'][0]['take'] for c in cs]          # whole sentences only: no mid-sentence swaps
        for i in range(1, len(cs)):                         # keep the take going where a switch has no clean gap
            if takes[i] != takes[i - 1]:
                ga, gb = gap(b, cs[i - 1]['sentence'], takes[i - 1]), gap(b, cs[i - 1]['sentence'], takes[i])
                if ga and gb and ga[1] - ga[0] >= 0.06 and gb[1] - gb[0] >= 0.06 and (b, cs[i]['sentence'], takes[i]) in rows:
                    switched += 1
                elif (b, cs[i]['sentence'], takes[i - 1]) in rows:
                    takes[i] = takes[i - 1]; kept += 1
        start = None
        for i, c in enumerate(cs):
            t, si = takes[i], c['sentence']
            y = audio(t)
            if start is None:                               # run start: the gap before this sentence, or a short reach back
                g = gap(b, si - 1, t)
                start = quietest(y, *g) if g else snap(y, rows[(b, si, t)]['s'] if (b, si, t) in rows else c['pick'][0]['s'], -1, 0.15)
            last = i == len(cs) - 1
            nxt_same = not last and takes[i + 1] == t
            if nxt_same and not c['hold']:
                continue                                    # same take continues: no cut here
            g = gap(b, si, t)
            end = quietest(y, *g) if g else snap(y, rows[(b, si, t)]['e'] if (b, si, t) in rows else c['pick'][-1]['e'], +1, 0.6)
            seg = y[int(start * SR):int(end * SR)].copy()
            n = min(int(0.005 * SR), len(seg) // 2)
            seg[:n] *= np.linspace(0, 1, n); seg[-n:] *= np.linspace(1, 0, n)
            parts.append(seg)
            h = c['hold']
            if h:
                parts.append(np.zeros(int((h if type(h) in (int, float) else HOLD) * SR)))
            elif last:
                parts.append(np.zeros(int(0.35 * SR)))       # between paragraphs
            start = None if (last or not nxt_same) else end
            if nxt_same and c['hold']:
                start = end                                 # same take continues after the hold
    sf.write(path, np.concatenate(parts) if parts else np.zeros(SR), SR)
    print(f'clean joins: {switched} take switches at real gaps, {kept} switches skipped (no clean gap)')


def render(comp, path):
    cache, parts = {}, []
    for c in comp:
        if not c['pick']:
            parts.append(np.zeros(int(0.5 * SR))); continue
        for p in c['pick']:
            f = os.path.join(TAKES, p['take'])
            if f not in cache:
                cache[f] = librosa.load(f, sr=SR, mono=True)[0]
            s, e = snap(cache[f], p['s'], -1, 0.25), snap(cache[f], p['e'], +1, 0.6)
            y = cache[f][int(s * SR):int(e * SR)].copy()
            n = min(int(0.01 * SR), len(y) // 2)
            y[:n] *= np.linspace(0, 1, n); y[-n:] *= np.linspace(1, 0, n)
            parts.append(y)
        h = c['hold']   # true = the standard hold; a number = a hold of exactly that many seconds (set by hand in comp.json)
        parts.append(np.zeros(int((h if type(h) in (int, float) else HOLD if h else JOIN) * SR)))
    sf.write(path, np.concatenate(parts) if parts else np.zeros(SR), SR)


def render_batches(comp, outdir):
    """One file per batch (B03.wav ...), for editors that time scenes per batch (build_timeline.py). Holds inside a
    batch are kept; the gap after the batch is left to the editor. Single takes like S01.mp3 are copied as they are."""
    os.makedirs(outdir, exist_ok=True)
    groups = {}
    for c in comp:
        groups.setdefault(c['batch'], []).append(c)
    for b, cs in groups.items():
        tmp = os.path.join(outdir, '_tmp.wav')
        last = dict(cs[-1]); last['hold'] = False
        render(cs[:-1] + [last], tmp)
        y, _ = librosa.load(tmp, sr=SR, mono=True)
        sf.write(os.path.join(outdir, b + '.wav'), np.trim_zeros(y, 'b'), SR)
        os.remove(tmp)
    for f in glob.glob(os.path.join(TAKES, 'S*.*')):
        if not f.endswith('.json'):
            y, _ = librosa.load(f, sr=SR, mono=True)
            sf.write(os.path.join(outdir, os.path.splitext(os.path.basename(f))[0] + '.wav'), y, SR)
    print('batches written to', outdir)


batches = parse_script()
if '--batches' in sys.argv:              # voice_comp.py <takes> <script> --batches <out_dir> [--use comp.json]
    comp = json.load(open(USE or os.path.join(OUT, 'comp.json'), encoding='utf-8'))
    render_batches(comp, sys.argv[sys.argv.index('--batches') + 1])
    sys.exit()
if FINISH:
    src = os.path.join(OUT, 'comp_draft.wav')
    chain = (f'atempo={SPEED},' if abs(SPEED - 1) > 0.001 else '') + \
        'highpass=f=80,equalizer=f=350:t=q:w=1.2:g=-3,equalizer=f=4000:t=q:w=1:g=2,deesser=i=0.4,' \
        'acompressor=threshold=-20dB:ratio=3:attack=5:release=80,loudnorm=I=-14:TP=-1.5:LRA=7'
    dst = os.path.join(OUT, 'final_voice.wav')
    r = subprocess.run(['ffmpeg', '-v', 'error', '-y', '-i', src, '-af', chain, '-ar', '48000', dst], capture_output=True, text=True)
    print(r.stderr or f'saved {dst}  (speed {SPEED}, EQ, de-ess, compressor, -14 LUFS)')
    sys.exit()
segs = segments(batches)
if USE:
    comp = json.load(open(USE, encoding='utf-8'))
else:
    comp = propose(batches, segs)
    json.dump(comp, open(os.path.join(OUT, 'comp.json'), 'w', encoding='utf-8'), indent=1, ensure_ascii=False)
render_clean(comp, os.path.join(OUT, 'comp_draft.wav'), segs)   # (render() is the old cut-everywhere join, kept for --batches)
with open(os.path.join(OUT, 'comp_list.md'), 'w', encoding='utf-8') as f:
    f.write('# Comp list (edit comp.json to change a choice, then run with --use comp.json)\n\n')
    for c in comp:
        f.write(f"- {c['batch']}.{c['sentence'] + 1}{' [HOLD]' if c['hold'] else ''}: {c['note']}  —  \"{c['text'][:70]}\"\n")
print(open(os.path.join(OUT, 'comp_list.md'), encoding='utf-8').read())
print('draft:', os.path.join(OUT, 'comp_draft.wav'))
