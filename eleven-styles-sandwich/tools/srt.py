"""Timed subtitles for the sandwich clips (house rule: every video gets a .srt next to it). All 11 styles share the voice,
so one subtitle file fits every clip; it is copied next to each rendered MP4 as <style>.en_US.srt.
Usage: py -3.13 tools/srt.py [out_dir]   (default out/)"""
import json, os, sys, shutil

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
out = sys.argv[1] if len(sys.argv) > 1 else os.path.join(ROOT, 'out')
os.makedirs(out, exist_ok=True)
ph = json.load(open(os.path.join(ROOT, 'src', 'shared', 'phrases.json'), encoding='utf-8'))
# join the two halves of "and spread it, right to the edges." into one line; every other phrase is one line
lines = []
for p in ph:
    if lines and lines[-1]['text'].endswith('spread it,'):
        lines[-1] = {'text': lines[-1]['text'] + ' ' + p['text'], 's': lines[-1]['s'], 'e': p['e']}
    else:
        lines.append({'text': p['text'], 's': p['s'], 'e': p['e']})
ts = lambda t: f"{int(t // 3600):02d}:{int(t % 3600 // 60):02d}:{int(t % 60):02d},{int(round((t % 1) * 1000)):03d}"
ends = [min(l['e'] + 0.25, (lines[k + 1]['s'] - 0.04) if k + 1 < len(lines) else 15.0) for k, l in enumerate(lines)]
srt = ''.join(f"{i}\n{ts(l['s'])} --> {ts(ends[i - 1])}\n{l['text'][0].upper() + l['text'][1:]}\n\n" for i, l in enumerate(lines, 1))
base = os.path.join(out, 'sandwich.en_US.srt')
open(base, 'w', encoding='utf-8').write(srt)
for f in os.listdir(out):
    if f.endswith('.mp4'):
        shutil.copyfile(base, os.path.join(out, f[:-4] + '.en_US.srt'))
print(srt)
