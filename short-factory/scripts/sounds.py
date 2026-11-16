"""Name the sounds under the voice: run an AudioSet sound classifier over the background stem (music + effects).
Usage: python -I sounds.py <study_dir> <video_id> [<video_id> ...]
Writes analysis/<id>/sounds.json: per-window top labels, the music share and a list of sound-effect events."""
import json, os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import sfconfig  # adds the pylib folder (transformers) after the venv's own packages
import numpy as np, librosa, torch
from transformers import ASTFeatureExtractor, ASTForAudioClassification

STUDY = sys.argv[1]
NAME = 'MIT/ast-finetuned-audioset-10-10-0.4593'
fe = ASTFeatureExtractor.from_pretrained(NAME)
model = ASTForAudioClassification.from_pretrained(NAME).eval().to('cuda' if torch.cuda.is_available() else 'cpu')
labels = model.config.id2label
MUSIC = {'Music', 'Musical instrument', 'Background music', 'Soundtrack music', 'Theme music', 'Electronic music', 'Ambient music',
         'Synthesizer', 'Piano', 'Keyboard (musical)', 'Drum', 'Drum kit', 'Percussion', 'Bass drum', 'Snare drum', 'Hi-hat',
         'Cymbal', 'Electronic dance music', 'Techno', 'House music', 'Pop music', 'Hip hop music', 'Orchestra', 'String section',
         'Bowed string instrument', 'Violin, fiddle', 'Cello', 'Guitar', 'Electric guitar', 'Bass guitar', 'Plucked string instrument',
         'Scary music', 'Tender music', 'Happy music', 'Sad music', 'Exciting music', 'Angry music', 'Funny music', 'Video game music',
         'Electronica', 'Dubstep', 'Drum and bass', 'Trance music', 'Rock music', 'Classical music', 'Middle Eastern music', 'Brass instrument',
         'Mallet percussion', 'Marimba, xylophone', 'Glockenspiel', 'Vibraphone', 'Timpani', 'Tabla', 'Wind instrument, woodwind instrument',
         'Synthetic singing', 'Christmas music', 'Music for children', 'Lullaby', 'Wedding music', 'New-age music', 'Jingle (music)',
         'Beat', 'Chime', 'Bell', 'Harp', 'Organ', 'Electronic organ', 'Hammond organ', 'Flute', 'Choir', 'Singing', 'Chant', 'Humming'}
QUIET = {'Silence', 'Speech', 'Narration, monologue', 'Male speech, man speaking', 'Female speech, woman speaking', 'Conversation',
         'Inside, small room', 'Inside, large room or hall', 'Outside, rural or natural', 'Outside, urban or manmade', 'Sound effect', 'Noise',
         'Static', 'Hum', 'Mains hum', 'White noise', 'Pink noise', 'Environmental noise', 'Child speech, kid speaking', 'Speech synthesizer'}
WIN, HOP = 1.0, 0.5

if sys.argv[2] == '--file':          # sounds.py <study> --file <no_vocals.wav> <out_dir>  (used by format_check.py)
    JOBS = [('check', sys.argv[3], sys.argv[4])]
else:
    JOBS = [(v, os.path.join(STUDY, 'analysis', v, 'stems', 'htdemucs', v, 'no_vocals.wav'), os.path.join(STUDY, 'analysis', v))
            for v in sys.argv[2:]]
for vid, bed, out in JOBS:
    y, sr = librosa.load(bed, sr=16000, mono=True)
    starts = np.arange(0, max(len(y) / sr - WIN, 0) + 1e-6, HOP)
    rows = []
    for b in range(0, len(starts), 32):
        chunk = [y[int(s * sr): int((s + WIN) * sr)] for s in starts[b:b + 32]]
        inp = fe(chunk, sampling_rate=sr, return_tensors='pt').to('cuda')
        with torch.no_grad():
            p = torch.sigmoid(model(**inp).logits).cpu().numpy()
        for s, row, c in zip(starts[b:b + 32], p, chunk):
            rms = float(np.sqrt(np.mean(c ** 2)) + 1e-9)
            top = [(labels[i], round(float(row[i]), 2)) for i in np.argsort(row)[::-1][:5]]
            rows.append({'t': round(float(s), 1), 'db': round(20 * np.log10(rms), 1), 'top': top,
                         'music': round(float(max(row[i] for i in range(len(row)) if labels[i] in MUSIC)), 2)})
    events, last = [], {}
    for r in rows:
        if r['db'] < -45:
            continue
        for lab, pr in r['top']:
            if lab in MUSIC or lab in QUIET or pr < 0.2:
                continue
            if r['t'] - last.get(lab, -9) > 1.0:
                events.append({'t': r['t'], 'sound': lab, 'p': pr})
            last[lab] = r['t']
    counts = {}
    for e in events:
        counts[e['sound']] = counts.get(e['sound'], 0) + 1
    dur = len(y) / sr
    res = {'id': vid, 'music_share': round(float(np.mean([r['music'] > 0.3 for r in rows])), 2),
           'silent_bed_share': round(float(np.mean([r['db'] < -45 for r in rows])), 2),
           'sfx_events': len(events), 'sfx_per_min': round(len(events) / dur * 60, 1),
           'sfx_kinds': dict(sorted(counts.items(), key=lambda x: -x[1])[:25]), 'events': events, 'windows': rows}
    json.dump(res, open(os.path.join(out, 'sounds.json'), 'w', encoding='utf-8'), indent=0)
    print(vid, res['music_share'], res['sfx_per_min'], list(res['sfx_kinds'].items())[:8], flush=True)
