"""Measure our own finished video against the Shorts format authority (the shorts-format study's measured ranges, 29 Oct 2026).
Usage: python -I format_check.py <video.mp4> short|long
Runs analyze.py + sounds.py on the file (results in <video folder>/format_check/, cleared first so no old transcript is
reused), then prints a pass/fail table and writes format_check/report.md. Look at hook.jpg and timeline.jpg afterwards."""
import json, os, shutil, subprocess, sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import sfconfig  # noqa: E402  (ffmpeg on PATH)

VIDEO, KIND = os.path.abspath(sys.argv[1]), sys.argv[2]
STUDY = HERE
OUT = os.path.join(os.path.dirname(VIDEO), 'format_check')
shutil.rmtree(OUT, ignore_errors=True)
VID = os.path.splitext(os.path.basename(VIDEO))[0].replace(' ', '_')
PY = sys.executable
os.makedirs(OUT, exist_ok=True)
subprocess.run([PY, '-I', os.path.join(HERE, 'analyze.py'), STUDY, VID, VIDEO, OUT], check=True)
bed = os.path.join(OUT, 'stems', 'htdemucs', VID, 'no_vocals.wav')
subprocess.run([PY, '-I', os.path.join(HERE, 'sounds.py'), STUDY, '--file', bed, OUT], check=True)
m = json.load(open(os.path.join(OUT, 'metrics.json')))
s = json.load(open(os.path.join(OUT, 'sounds.json'))) if os.path.exists(os.path.join(OUT, 'sounds.json')) else {}
sp = m.get('speech', {})
gap = m.get('voice_minus_background_lu')
# (label, our value, test, his typical value)
if KIND == 'short':
    rows = [
        ('Length 23-40 s', m['duration_s'], 23 <= m['duration_s'] <= 40, 'about 30 s'),
        ('Voice starts by 0.5 s', sp.get('first_word_at_s'), (sp.get('first_word_at_s') if sp.get('first_word_at_s') is not None else 9) <= 0.5, 'within 0.5 s in all 10'),
        ('Words 70-115', sp.get('word_count'), 70 <= (sp.get('word_count') or 0) <= 115, 'about 85'),
        ('Speaking speed 2.4-3.2 words/s', sp.get('words_per_sec'), 2.4 <= (sp.get('words_per_sec') or 0) <= 3.2, 'about 2.8'),
        ('No pause longer than 0.5 s (0-1 allowed)', sp.get('pauses_over_0.5s'), (sp.get('pauses_over_0.5s') or 0) <= 1, '0 in 9 of 10'),
        ('Hard cuts per minute 0-4', m['cuts_per_min'], m['cuts_per_min'] <= 4, '0 in 7 of 10 (blurred swipes instead)'),
        ('Voice above background 12-20 LU', gap, gap is not None and 12 <= gap <= 20, 'about 16 (his range 9-22)'),
        ('Music under the voice 60-100 %', s.get('music_share'), (s.get('music_share') or 0) >= 0.6, 'about 90 %'),
        ('Sound effects 0-12 a minute', s.get('sfx_per_min'), (s.get('sfx_per_min') or 0) <= 12, 'a few small whooshes'),
    ]
else:
    rows = [
        ('Length 3-13 min', round(m['duration_s'] / 60, 1), 180 <= m['duration_s'] <= 780, '3:05-12:13 (top ones 5-6 min)'),
        ('Voice starts by 0.5 s', sp.get('first_word_at_s'), (sp.get('first_word_at_s') if sp.get('first_word_at_s') is not None else 9) <= 0.5, 'within 0.5 s in all 10'),
        ('Speaking speed 2.3-2.8 words/s', sp.get('words_per_sec'), 2.3 <= (sp.get('words_per_sec') or 0) <= 2.8, 'about 2.55'),
        ('Voice covers 85 %+ of the time', sp.get('voice_covers_share'), (sp.get('voice_covers_share') or 0) >= 0.85, '88-92 %'),
        ('Cuts per minute 6-14', m['cuts_per_min'], 6 <= m['cuts_per_min'] <= 14, '6-14 (3D ones change picture every ~1.5 s)'),
        ('Voice above background 8-15 LU', gap, gap is not None and 8 <= gap <= 15, 'about 12'),
        ('Music under the voice 70 %+', s.get('music_share'), (s.get('music_share') or 0) >= 0.7, '75-94 %'),
    ]
rows.append(('Final loudness -9 to -14 LUFS', m['mix']['integrated_lufs'], -14.5 <= m['mix']['integrated_lufs'] <= -9, 'about -10 to -12'))
rows.append(('True peak at or below -1 dBTP', m['mix']['true_peak_dbtp'], m['mix']['true_peak_dbtp'] <= -1.0, '(he clips; we should not)'))
lines = ['| Check | Ours | Pass | Benchmark typical |', '|---|---|---|---|']
lines += [f"| {a} | {b} | {'yes' if c else 'NO'} | {d} |" for a, b, c, d in rows]
lines.append(f"\nFirst words: \"{sp.get('words_in_first_3s', '')}\"  - must name the subject in the first 3 words.")
rep = '\n'.join(lines)
open(os.path.join(OUT, 'report.md'), 'w', encoding='utf-8').write(rep + '\n')
print(rep)
print(f"\n{sum(r[2] for r in rows)}/{len(rows)} checks pass. Frames to eyeball: {os.path.join(OUT, 'hook.jpg')} and timeline.jpg")
