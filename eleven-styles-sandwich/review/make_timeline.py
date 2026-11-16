"""Writes review/timeline.json, the tracks under the review player, from the manifest named in review/contract.json
(free kit template). Only standard Python (3.9+); uses FFmpeg when it is installed (any sound format, faster) and numpy
when it is installed (faster), neither is required for WAV files.
  python review/make_timeline.py        (run again after the voice, the chapters or the music change)

Without a manifest it still writes a small timeline.json: the page then shows the sound effects, clips, voice and music
it reads from the compositions themselves, and the notes.

The manifest (JSON; any key may be left out; keys that start with "_" are comments):
  fps          frames a second (default: the contract's)
  total        the whole video's length in frames (default: the end of the last chapter, word, section or sound file)
  chapters     [{"id", "title", "style" (optional), "start", "frames",
                 "words" (optional: a list, or the path of a JSON file with the list, counted from the chapter's start),
                 "voice" (optional: this chapter's voice file in public/), "lead" (frames before that file starts)}]
  words        a list, or the path (from the project folder) of a JSON file with the list, counted from frame 0:
               [{"w": "Take", "fs": 18, "fe": 24}]  (fs/fe = first/last frame; or "s"/"e" in seconds when there are no
               frames). Sentences are made from the words (they end at . ? ! or at a pause longer than a second).
  voiceFiles   [{"file": "audio/voice.wav", "at": 0}]   voice files in public/ and the frame where each starts playing
  music        [{"name": "Intro bed", "fs": 0, "fe": 450, "bpm": 96, "chords": "C G Am F", "inst": ["piano"]}]
               the music's sections (fs/fe frames, or s/e seconds); without sections each music file is one block
  musicFiles   [{"file": "audio/music.wav", "at": 0}]   music files in public/ and the frame where each starts playing
  silent       ["sfx/old_whoosh.wav"]   sound files in public/ to leave off the timeline (muted ones, placeholders)
A file listed in voiceFiles or musicFiles (or a chapter's "voice") is drawn as a waveform and is not listed again from
the compositions."""
import array, json, math, os, re, shutil, subprocess, sys, wave

RV = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(RV)
PUB = os.path.join(ROOT, 'public')
PPS = 10        # loudness values a second
try:
    import numpy as np
except ImportError:      # fine: slower, same result
    np = None


def fail(msg):
    sys.exit(f'make_timeline: {msg}')


def strip(d):
    if isinstance(d, dict):
        return {k: strip(v) for k, v in d.items() if not k.startswith('_')}
    if isinstance(d, list):
        return [strip(v) for v in d]
    return d


def load_json(p, what):
    try:
        return strip(json.load(open(p, encoding='utf-8')))
    except FileNotFoundError:
        fail(f'{what} not found: {p}')
    except ValueError as e:
        fail(f'{what} is not valid JSON ({p}): {e}')


def listed(x, what):
    """a list given inline, or the path of a JSON file that holds it"""
    if isinstance(x, str):
        return load_json(os.path.join(ROOT, x), what)
    return x or []


def span(d, fps, off=0):
    """(first, last) frame of a word or section: fs/fe frames, f/e frames, or s/e seconds; `off` = where 0 is"""
    if 'fs' in d:
        return off + int(round(d['fs'])), off + int(round(d.get('fe', d['fs'])))
    if 'f' in d:
        return off + int(round(d['f'])), off + int(round(d.get('e', d['f'])))
    if 's' in d:
        return off + int(round(d['s'] * fps)), off + int(round(d.get('e', d['s']) * fps))
    raise ValueError(f'no fs/fe, f/e or s/e times in {d}')


def files(lst):
    out = []
    for x in lst or []:
        if isinstance(x, str):
            x = {'file': x, 'at': 0}
        out.append({'file': x['file'].replace('\\', '/').lstrip('/'), 'at': int(x.get('at', 0))})
    return out


# ------------------------------------------------------------------------------------------------ sound -> peaks
def levels(path):
    """(absolute sample levels 0..1 as an array, samples per second including channels) or None"""
    ff = shutil.which('ffmpeg')
    if ff:
        r = subprocess.run([ff, '-v', 'error', '-i', path, '-ac', '1', '-ar', '8000', '-f', 's16le', '-'], capture_output=True)
        if r.returncode == 0 and r.stdout:
            return pcm(r.stdout, 2), 8000
    try:
        with wave.open(path) as w:
            sr, ch, sw = w.getframerate(), w.getnchannels(), w.getsampwidth()
            raw = w.readframes(w.getnframes())
    except (wave.Error, EOFError, OSError) as e:
        print(f'  cannot read {os.path.relpath(path, ROOT)} ({e}); install FFmpeg to read this kind of file', file=sys.stderr)
        return None
    if sw == 3:                         # 24-bit: keep the top two bytes of each sample
        n = len(raw) // 3
        b2 = bytearray(2 * n); b2[0::2] = raw[1::3][:n]; b2[1::2] = raw[2::3][:n]
        raw, sw = bytes(b2), 2
    return pcm(raw, sw), sr * ch       # channels are interleaved: a block of sr*ch values is still one second


def pcm(raw, sw):
    if sw == 1:                         # 8-bit WAV is unsigned
        a = array.array('B', raw)
        return [abs(v - 128) / 128 for v in a] if np is None else np.abs(np.frombuffer(raw, np.uint8).astype(np.float32) - 128) / 128
    code, scale = {2: ('h', 32768.0), 4: ('i', 2147483648.0)}[sw]
    if np is not None:
        return np.abs(np.frombuffer(raw, '<i2' if sw == 2 else '<i4').astype(np.float32)) / scale
    a = array.array(code); a.frombytes(raw[: len(raw) // sw * sw])
    if sys.byteorder == 'big':
        a.byteswap()
    return [abs(v) / scale for v in a]


def peaks_into(arr, lv, rate, t0, t_max):
    """loudest level per 1/PPS s of a file that starts at second t0 of the video, cut at second t_max"""
    step = max(1, rate // PPS)
    n = min(len(lv) // step, int((t_max - t0) * PPS))
    k0 = int(round(t0 * PPS))
    for k in range(max(0, n)):
        if not 0 <= k0 + k < len(arr):
            continue
        blk = lv[k * step:(k + 1) * step]
        v = float(blk.max()) if np is not None else max(blk)
        if v > arr[k0 + k]:
            arr[k0 + k] = v


def pack(a):
    top = max(a) if a else 0
    return ''.join(chr(48 + int(math.sqrt(v / top) * 60)) for v in a) if top > 0 else ''   # '0'..'l', square root like an editor


# ------------------------------------------------------------------------------------------------------- main
def main():
    cp = os.path.join(RV, 'contract.json')
    c = load_json(cp, 'review/contract.json') if os.path.exists(cp) else {}
    man = load_json(os.path.join(ROOT, c['manifest']), 'the manifest') if c.get('manifest') else {}
    fps = int(man.get('fps') or c.get('fps') or 30)
    item_ends = [int(it.get('start', 0)) + it['frames'] for it in c.get('items', []) if isinstance(it.get('frames'), int)]

    chapters, words, voice, music, notes = [], [], [], [], []
    vfiles, mfiles = files(man.get('voiceFiles')), files(man.get('musicFiles'))
    for ch in man.get('chapters', []):
        st, fr = int(ch['start']), int(ch['frames'])
        chapters.append({'id': str(ch['id']), 'title': str(ch.get('title') or ch['id']), 'style': str(ch.get('style') or ''),
                         'start': st, 'frames': fr})
        for w in listed(ch.get('words'), f"chapter {ch['id']}'s words"):
            f, e = span(w, fps, st)
            words.append({'f': f, 'e': max(f, e), 'w': str(w['w']), 'cut': st + fr})
        if ch.get('voice'):
            vfiles.append({'file': ch['voice'].replace('\\', '/').lstrip('/'), 'at': st + int(ch.get('lead', 0)), 'end': st + fr})
    for w in listed(man.get('words'), 'the words'):
        f, e = span(w, fps)
        words.append({'f': f, 'e': max(f, e), 'w': str(w['w'])})
    words.sort(key=lambda x: x['f'])
    for m in man.get('music', []):
        f, e = span(m, fps)
        music.append({'f': f, 'e': e, 'name': str(m.get('name') or 'music'), 'bpm': m.get('bpm'),
                      'chords': str(m.get('chords') or ''), 'inst': [str(x) for x in m.get('inst', [])]})

    # sentences: end at . ? ! (also before a closing quote or bracket), at a chapter's end, or at a pause over a second
    cur = []
    for i, w in enumerate(words):
        cur.append(w)
        nxt = words[i + 1] if i + 1 < len(words) else None
        stop = (re.search(r'[.?!]["\')\]]*$', w['w']) or nxt is None or nxt['f'] - w['e'] > fps
                or ('cut' in w and nxt['f'] >= w['cut']))
        if stop:
            voice.append({'f': cur[0]['f'], 'e': cur[-1]['e'], 'text': ' '.join(x['w'] for x in cur)})
            cur = []
    for w in words:
        w.pop('cut', None)

    ends = [ch['start'] + ch['frames'] for ch in chapters] + [w['e'] for w in words] + [m['e'] for m in music]
    total = int(man.get('total') or 0)

    # loudness outlines (and each file's length, for files without sections)
    lens = {}
    for fl in vfiles + mfiles:
        p = os.path.join(PUB, fl['file'])
        if not os.path.isfile(p):
            print(f"  not found: public/{fl['file']} (its waveform stays empty until the file is there)", file=sys.stderr)
            continue
        got = levels(p)
        if got:
            lens[fl['file']] = got
            ends.append(fl['at'] + int(round(len(got[0]) / got[1] * fps)))
    total = total or max(ends + item_ends + [1])
    vpk = [0.0] * (int(total / fps * PPS) + 1)
    mpk = [0.0] * len(vpk)
    for arr, lst in ((vpk, vfiles), (mpk, mfiles)):
        for fl in lst:
            if fl['file'] in lens:
                lv, rate = lens[fl['file']]
                peaks_into(arr, lv, rate, fl['at'] / fps, min(total, fl.get('end', total)) / fps)

    # no sections or no words: one block per file, named after it
    def file_blocks(lst):
        out = []
        for fl in lst:
            if fl['file'] in lens:
                lv, rate = lens[fl['file']]
                e = min(total, fl.get('end', total), fl['at'] + int(round(len(lv) / rate * fps)))
                out.append((fl['at'], e, os.path.splitext(os.path.basename(fl['file']))[0]))
        return out
    if not music:
        music = [{'f': f, 'e': e, 'name': n, 'bpm': None, 'chords': '', 'inst': []} for f, e, n in file_blocks(mfiles)]
    if not voice and vfiles:
        voice = [{'f': f, 'e': e, 'text': n} for f, e, n in file_blocks(vfiles)]
        notes.append('no word times: the voice track shows one block per voice file')

    out = {'fps': fps, 'total': total, 'pps': PPS, 'silent': sorted({s.replace('\\', '/').lstrip('/') for s in man.get('silent', [])}),
           'chapters': chapters, 'voice': voice, 'words': words, 'music': music,
           'voicePeaks': pack(vpk), 'musicPeaks': pack(mpk),
           'voiceFiles': sorted({f['file'] for f in vfiles}), 'musicFiles': sorted({f['file'] for f in mfiles})}
    p = os.path.join(RV, 'timeline.json')
    with open(p + '.tmp', 'w', encoding='utf-8') as f:
        json.dump(out, f, ensure_ascii=False)
    os.replace(p + '.tmp', p)
    print(f'timeline.json: {total} frames, {len(chapters)} chapters, {len(voice)} voice lines, {len(words)} words, '
          f'{len(music)} music sections, waveforms for {len(lens)} of {len(vfiles) + len(mfiles)} sound files'
          + (' (no manifest)' if not man else '') + ''.join(f'\n  {n}' for n in notes))


if __name__ == '__main__':
    main()
