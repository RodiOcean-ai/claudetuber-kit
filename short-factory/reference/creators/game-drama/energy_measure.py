import json, os, re, glob, statistics as st, sys
R = '<projects>'
def syl(w):
    w = re.sub(r'[^a-z]', '', w.lower())
    if not w: return 0
    if len(w) <= 3: return 1
    w = re.sub(r'(?:[^laeiouy]es|ed|[^laeiouy]e)$', '', w)
    w = re.sub(r'^y', '', w)
    return max(1, len(re.findall(r'[aeiouy]{1,2}', w)))
def read(d):
    out = {}
    t = os.path.join(d, 'transcript.json')
    if os.path.exists(t):
        ws = [x['w'] for x in json.load(open(t, encoding='utf8')).get('words', [])]
        text = ' '.join(ws)
        sents = [s for s in re.split(r'[.!?]+', text) if re.search(r'[A-Za-z]', s)]
        words = [w for w in re.findall(r"[A-Za-z][A-Za-z'\-]*", text)]
        if len(words) >= 10 and sents:
            sy = [syl(w) for w in words]
            out['fk_grade'] = 0.39 * len(words) / len(sents) + 11.8 * sum(sy) / len(words) - 15.59
            out['sent_words'] = len(words) / len(sents)
            out['syl_per_word'] = sum(sy) / len(words)
            out['pct_3syl'] = 100 * sum(1 for s in sy if s >= 3) / len(words)
            out['n_words'] = len(words)
    v = os.path.join(d, 'voice_style.json')
    if os.path.exists(v):
        j = json.load(open(v, encoding='utf8'))
        out['wps'] = j['speed']['words_per_sec_mean']
        out['pitch_range_st'] = j['pitch']['range_semitones_10_90']
        out['stress_per_min'] = j['stressed_words_per_min']
        out['loud_swing_db'] = j['loudness']['phrase_loudness_swing_db']
        out['pauses_over_1s_min'] = j['pauses']['per_min_over_1s']
    m = os.path.join(d, 'metrics.json')
    if os.path.exists(m):
        j = json.load(open(m, encoding='utf8'))
        out['voice_lufs'] = (j.get('voice') or {}).get('integrated_lufs')
        out['voice_over_music'] = j.get('voice_minus_background_lu')
        out['voice_range_lu'] = (j.get('voice') or {}).get('range_lu')
    return out
def group(name, dirs):
    rows = [read(d) for d in dirs]
    keys = ['wps','pitch_range_st','stress_per_min','loud_swing_db','pauses_over_1s_min','voice_lufs','voice_over_music','voice_range_lu','fk_grade','sent_words','syl_per_word','pct_3syl']
    print(f'== {name} (n={len(dirs)})')
    for k in keys:
        vals = [r[k] for r in rows if r.get(k) is not None]
        if vals: print(f'  {k:20s} median {st.median(vals):7.2f}   range {min(vals):.2f}-{max(vals):.2f}  n={len(vals)}')
    return rows
def picks(study, kind):
    p = json.load(open(f'{R}/studies/{study}/picks.json', encoding='utf8'))
    return [f'{R}/studies/{study}/analysis/{x["id"]}' for x in p['top'] if x['kind'] == kind]
g = group('GothamChess top 10 Shorts', picks('gothamchess', 'short'))
group('GothamChess 3 weaker Shorts', glob.glob(f'{R}/studies/gothamchess/contrast/analysis/*'))
group('GothamChess top 10 long videos', picks('gothamchess', 'long'))
group('MrBeast top 10 Shorts', picks('mrbeast', 'short'))
group('Zack top 10 Shorts', sorted(glob.glob(f'{R}/studies/shorts-format/analysis/S*')))
print('\nper-video GothamChess Shorts:')
for d in picks('gothamchess','short'):
    r = read(d); print(' ', os.path.basename(d), {k: round(v,1) for k,v in r.items() if isinstance(v,(int,float)) and k in ('fk_grade','wps','stress_per_min','pitch_range_st','n_words')})
