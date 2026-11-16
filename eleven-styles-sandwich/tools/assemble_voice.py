"""Place one free-voice take on the 15 s timeline: slow it a touch (rubberband, pitch kept), split it ONLY in its own silent
gaps between phrases (found by sound level, never inside a word), and put each phrase at its planned start.
Usage: py -3.13 assemble_voice.py <take.wav> <out.wav> [--tempo 0.94] [--sr 24000] [--starts 0.6,2.38,...]
(14 Nov, owner: "the voice is shakey and robotic": use --tempo 1 (no stretching at all) on a ClearerVoice 48 kHz take, --sr 48000)
Prints where every phrase landed (these are the beats every style follows)."""
import sys, json, subprocess, numpy as np
src, out = sys.argv[1], sys.argv[2]
SR = int(sys.argv[sys.argv.index('--sr') + 1]) if '--sr' in sys.argv else 24000
tempo = float(sys.argv[sys.argv.index('--tempo') + 1]) if '--tempo' in sys.argv else 0.94
PHRASES = ['Take two slices of bread,', 'then dig a knife into the peanut butter,', 'and spread it,', 'right to the edges.',
           'Press the second slice on top', 'and cut it corner to corner,', 'because triangles taste better.']
STARTS = [0.60, 2.38, 4.45, 5.22, 7.08, 9.14, 11.02]      # planned speech onsets (s); total 15.0 s
if '--starts' in sys.argv:
    STARTS = [float(v) for v in sys.argv[sys.argv.index('--starts') + 1].split(',')]
TOTAL = 15.0
af = ['-af', f'rubberband=tempo={tempo}'] if abs(tempo - 1) > 1e-6 else []
x = np.frombuffer(subprocess.run(['ffmpeg', '-v', 'error', '-i', src, *af, '-ac', '1', '-ar', str(SR),
                                  '-f', 'f32le', '-'], capture_output=True, check=True).stdout, np.float32).copy()
fr = SR // 100; n = len(x) // fr
db = 20 * np.log10(np.sqrt((x[:n * fr].reshape(n, fr) ** 2).mean(1)) + 1e-9); db -= db.max()
loud = db > -38
on = np.argmax(loud); off = n - np.argmax(loud[::-1])
gaps = []; i = on
while i < off:
    if not loud[i]:
        j = i
        while j < off and not loud[j]: j += 1
        if j - i >= 8: gaps.append((i, j))
        i = j
    else: i += 1
print('gaps (s):', [(round(a / 100, 2), round((b - a) / 100, 2)) for a, b in gaps])
if len(gaps) != len(PHRASES) - 1:
    sys.exit(f'expected {len(PHRASES) - 1} gaps, found {len(gaps)}: pick another take or adjust the threshold')
bounds = [on] + [g for ab in gaps for g in ab] + [off]
segs = [(bounds[2 * k], bounds[2 * k + 1]) for k in range(len(PHRASES))]
y = np.zeros(int(TOTAL * SR), np.float32); PAD = 4; FADE = int(0.008 * SR)
beats = []
for (a, b), st, txt in zip(segs, STARTS, PHRASES):
    a2 = max(0, a - PAD); b2 = min(n, b + PAD)
    seg = x[a2 * fr:b2 * fr].copy()
    seg[:FADE] *= np.linspace(0, 1, FADE); seg[-FADE:] *= np.linspace(1, 0, FADE)
    pos = int((st - (a - a2) / 100) * SR)
    y[pos:pos + len(seg)] += seg
    beats.append({'text': txt, 'start': round(st, 3), 'end': round(st + (b - a) / 100, 3)})
    print(f'{st:6.2f} - {st + (b - a) / 100:6.2f}  {txt}')
subprocess.run(['ffmpeg', '-v', 'error', '-y', '-f', 'f32le', '-ar', str(SR), '-ac', '1', '-i', '-', out], input=y.tobytes(), check=True)
json.dump(beats, open(out.rsplit('.', 1)[0] + '.phrases.json', 'w', encoding='utf-8'), indent=1)
