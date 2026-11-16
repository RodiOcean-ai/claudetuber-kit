"""Measure how human a narration sounds: tone swings, speed changes, pauses, stressed words, fillers.
Usage: python -I voice_style.py <voice.wav> <out.json> [<transcript.json>]
<voice.wav> should be the voice alone (a Demucs vocals stem, or a raw TTS take). Without a transcript, Whisper runs first
(with a prompt that keeps "um", "uh" and other fillers, which Whisper otherwise drops).
Used on the 9 videos of the faceless-channel study (29 Oct 2026) and by voice_check.py on our own takes."""
import json, os, re, sys
import numpy as np, librosa

WAV, OUT = sys.argv[1], sys.argv[2]
TR = sys.argv[3] if len(sys.argv) > 3 else None
FILLERS = ['um', 'uh', 'hmm', 'huh', 'like', 'so', 'well', 'okay', 'ok', 'right', 'yeah', 'anyways', 'anyway', 'actually',
           'basically', 'dude', 'man', 'i mean', 'you know', 'kind of', 'kinda', 'look', 'wait']


def words_from(path):
    if path and os.path.exists(path):
        return json.load(open(path, encoding='utf-8'))['words']
    import whisper
    m = whisper.load_model('large-v3-turbo')
    r = m.transcribe(WAV, language='en', word_timestamps=True, condition_on_previous_text=False,
                     initial_prompt='Um, so, uh... I mean, like, you know, it was, hmm, kind of weird. Wait, what?')
    return [{'w': w['word'].strip(), 's': round(w['start'], 2), 'e': round(w['end'], 2)} for seg in r['segments'] for w in seg.get('words', [])]


def semis(f):
    return 12 * np.log2(f / 100.0)


y, sr = librosa.load(WAV, sr=16000, mono=True)
dur = len(y) / sr
words = words_from(TR)
hop = 256
f0 = librosa.yin(y, fmin=65, fmax=400, sr=sr, frame_length=1024, hop_length=hop)
rms = librosa.feature.rms(y=y, frame_length=1024, hop_length=hop)[0]
db = 20 * np.log10(rms + 1e-9)
voiced = db > (np.percentile(db, 95) - 30)
t_frame = np.arange(len(f0)) * hop / sr
from scipy.ndimage import median_filter
f0 = median_filter(f0, size=7)
pitch = np.where(voiced[:len(f0)], f0, np.nan)
ps = semis(pitch[~np.isnan(pitch)])

# phrases: words separated by gaps of 0.25 s or more
phrases, cur = [], []
for a, b in zip(words, words[1:] + [None]):
    cur.append(a)
    if b is None or b['s'] - a['e'] >= 0.25:
        phrases.append(cur); cur = []
ph_rate, ph_pitch, ph_loud = [], [], []
for p in phrases:
    s, e = p[0]['s'], p[-1]['e']
    if e - s < 0.6:
        continue
    ph_rate.append(len(p) / (e - s))
    m = (t_frame >= s) & (t_frame <= e) & ~np.isnan(pitch)
    if m.sum() > 5:
        ph_pitch.append(float(np.median(semis(pitch[m]))))
    ml = (t_frame >= s) & (t_frame <= e)
    ph_loud.append(float(np.mean(db[ml])) if ml.any() else np.nan)

# stressed words: a word noticeably louder AND higher than its own phrase
stressed = []
for p in phrases:
    s, e = p[0]['s'], p[-1]['e']
    pm = (t_frame >= s) & (t_frame <= e)
    if pm.sum() < 10:
        continue
    pv = pm & ~np.isnan(pitch)
    pl, pp = np.mean(db[pm]), (float(np.median(semis(pitch[pv]))) if pv.any() else None)
    for w in p:
        wm = (t_frame >= w['s']) & (t_frame <= w['e'])
        if wm.sum() < 3 or pp is None:
            continue
        wl = np.mean(db[wm])
        wp = pitch[wm & ~np.isnan(pitch)]
        if len(wp) and wl > pl + 3 and np.median(semis(wp)) > pp + 2:
            stressed.append({'w': w['w'], 's': w['s']})

gaps = [round(b['s'] - a['e'], 2) for a, b in zip(words, words[1:])]
g = np.array(gaps) if gaps else np.array([0.0])
spoken_min = max((words[-1]['e'] - words[0]['s']) / 60, 0.01) if words else 0.01
text = ' '.join(w['w'] for w in words).lower()
toks = re.findall(r"[a-z']+", text)
joined = ' ' + ' '.join(toks) + ' '
fill = {f: joined.count(' ' + f + ' ') for f in FILLERS}
fill = {k: v for k, v in sorted(fill.items(), key=lambda x: -x[1]) if v}
sent = [s for s in re.split(r'[.!?]+', ' '.join(w['w'] for w in words)) if s.strip()]
slen = [len(s.split()) for s in sent]
punct = ' '.join(w['w'] for w in words)

res = {
    'file': os.path.basename(WAV), 'duration_s': round(dur, 1), 'words': len(words),
    'pitch': {'median_hz': round(float(np.nanmedian(pitch)), 1) if ps.size else None,
              'range_semitones_10_90': round(float(np.percentile(ps, 90) - np.percentile(ps, 10)), 1) if ps.size else None,
              'phrase_to_phrase_swing_semitones': round(float(np.std(ph_pitch)), 2) if len(ph_pitch) > 2 else None},
    'speed': {'words_per_sec_mean': round(float(np.mean(ph_rate)), 2) if ph_rate else None,
              'phrase_speed_variation_pct': round(float(np.std(ph_rate) / np.mean(ph_rate) * 100), 1) if len(ph_rate) > 2 else None,
              'slowest_phrase_wps': round(float(np.percentile(ph_rate, 10)), 2) if ph_rate else None,
              'fastest_phrase_wps': round(float(np.percentile(ph_rate, 90)), 2) if ph_rate else None},
    'loudness': {'phrase_loudness_swing_db': round(float(np.nanstd(ph_loud)), 2) if len(ph_loud) > 2 else None},
    'pauses': {'per_min_0.25_0.5s': round(float(((g >= 0.25) & (g < 0.5)).sum() / spoken_min), 1),
               'per_min_0.5_1s': round(float(((g >= 0.5) & (g < 1.0)).sum() / spoken_min), 1),
               'per_min_over_1s': round(float((g >= 1.0).sum() / spoken_min), 1),
               'longest_s': round(float(g.max()), 2), 'phrases_per_min': round(len(phrases) / spoken_min, 1)},
    'stressed_words_per_min': round(len(stressed) / spoken_min, 1), 'stressed_examples': [s['w'] for s in stressed[:40]],
    'fillers_per_min': round(sum(fill.values()) / spoken_min, 1), 'fillers': fill,
    'sentences': {'count': len(slen), 'mean_words': round(float(np.mean(slen)), 1) if slen else None,
                  'length_spread_words': round(float(np.std(slen)), 1) if slen else None,
                  'shortest': min(slen) if slen else None, 'longest': max(slen) if slen else None,
                  'questions_per_min': round(punct.count('?') / spoken_min, 1), 'exclamations_per_min': round(punct.count('!') / spoken_min, 1)},
}
json.dump(res, open(OUT, 'w', encoding='utf-8'), indent=1, default=lambda o: o.item())
print(json.dumps({k: res[k] for k in ('file', 'pitch', 'speed', 'pauses', 'stressed_words_per_min', 'fillers_per_min')}, default=lambda o: o.item()))
