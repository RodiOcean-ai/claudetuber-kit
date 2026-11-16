"""Word and phrase times for every style (the shared beat sheet). Whisper's word times on CPU run early by ~0.3 s, so each
phrase's first word starts at the phrase's exact start (found by sound level when the phrase was placed), the last word ends
at the phrase's exact end, and the words in between keep Whisper's times (clamped inside the phrase).
Usage: py -3.13 timing.py  -> src/shared/words.json, src/shared/phrases.json (seconds and frames at 30 fps)"""
import json, re
FPS = 30
# 14 Nov 2026: the voice is now Chatterbox (channel voice) + ClearerVoice, no stretching (owner's note on the old one)
ws = json.load(open('voice/voice_cv.words.json', encoding='utf-8'))
ph = json.load(open('voice/voice_cv_timed.phrases.json', encoding='utf-8'))
script = open('voice/script_LOCKED.txt', encoding='utf-8').read().split()
out, k = [], 0
for p in ph:
    n = len(p['text'].split()); grp = ws[k:k + n]; words = script[k:k + n]
    P0, P1 = p['start'], p['end']
    for i, (w, txt) in enumerate(zip(grp, words)):
        s = P0 if i == 0 else min(max(w['s'], P0), P1)
        e = P1 if i == n - 1 else min(max(w['e'], s + 0.05), P1)
        out.append({'w': txt, 's': round(s, 3), 'e': round(e, 3), 'fs': round(s * FPS), 'fe': round(e * FPS)})
    k += n
assert k == len(script) == len(ws), (k, len(script), len(ws))
phr = [{'text': p['text'], 's': p['start'], 'e': p['end'], 'fs': round(p['start'] * FPS), 'fe': round(p['end'] * FPS)} for p in ph]
json.dump(out, open('src/shared/words.json', 'w', encoding='utf-8'), indent=0)
json.dump(phr, open('src/shared/phrases.json', 'w', encoding='utf-8'), indent=1)
print(' '.join(f"{w['w']}@{w['fs']}" for w in out)); print([(p['fs'], p['fe']) for p in phr])
