"""Check every piece of an episode's edit has its spare frames (14 Nov 2026, the owner's note "Its pause and black screen" on
the review page: a piece starting at a swipe had too few frames before it, so the Remotion Player stalled on black).
A piece that starts at a swipe needs from >= 3 frames; every clip must reach the piece's end (+3 frames at a swipe).
Usage: python check_joins.py <episode or its edit folder>      exit code 1 if any piece has a problem."""
import json, os, subprocess, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import sfconfig  # noqa: F401  (ffprobe on PATH)

ed = os.path.abspath(sys.argv[1]); ed = ed if os.path.isdir(os.path.join(ed, 'src')) else os.path.join(ed, 'edit')
c = json.load(open(os.path.join(ed, 'src', 'cut.json'), encoding='utf-8'))
sw, PAD, FPS = c.get('swipes', []), 3 / 30, 30
bad = 0
for g in c['segs']:
    at_sw = any(abs(s - g['at']) < 1e-3 for s in sw); to_sw = any(abs(s - g['to']) < 1e-3 for s in sw)
    a = g['at'] - (PAD if at_sw else 0); b = g['to'] + (PAD if to_sw else 0)
    if g.get('img'):
        ok = os.path.exists(os.path.join(ed, 'public', g['img']))
        print(f"{g['at']:6.2f}-{g['to']:6.2f} still {g['img']:30} {'OK' if ok else 'MISSING'}"); bad += not ok; continue
    trim = round((g.get('from', 0) - (g['at'] - a)) * FPS)
    need = g.get('from', 0) + (b - g['at'])
    path = os.path.join(ed, 'public', g['clip'])
    dur = float(subprocess.run(['ffprobe', '-v', 'error', '-show_entries', 'format=duration', '-of', 'csv=p=0', path],
                               capture_output=True, text=True).stdout or 0)
    ok = trim >= 0 and need <= dur + 1 / FPS
    bad += not ok
    print(f"{g['at']:6.2f}-{g['to']:6.2f} {g['clip']:30} start trim {trim:4d}  needs {need:6.3f} of {dur:6.3f} s  {'OK' if ok else 'PROBLEM'}")
print('all joins OK' if not bad else f'{bad} PROBLEM piece(s)')
sys.exit(1 if bad else 0)
