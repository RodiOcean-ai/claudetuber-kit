"""Render a blocky scene table several stretches at a time (owner, 12 Nov 2026: renders must be 2-4 times faster).
One Blender uses only part of the graphics card and one processor core for the scene work, so N Blenders side by side finish
close to N times sooner. Same pictures as a normal full render (same settings, same frame numbers).
Usage: python -I render_parallel.py <abs scene.md> <abs out_dir> [workers=6] [frames=from the table's length line | first-last]
('first-last', e.g. 911-983, renders only that stretch: a table whose middle is not used, 13 Nov 2026.)
Writes 0001.png ... into out_dir, logs in out_dir/_logs, and prints the seconds it took."""
import os, re, subprocess, sys, time
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import sfconfig

table, out = sys.argv[1], sys.argv[2].replace(chr(92), '/').rstrip('/') + '/'
N = int(sys.argv[3]) if len(sys.argv) > 3 else 6
m = re.search(r'^length:\s*([0-9.]+)', open(table, encoding='utf-8').read(), re.M)
spec = sys.argv[4] if len(sys.argv) > 4 else ''
f0, f1 = (map(int, spec.split('-'))) if '-' in spec else (1, int(spec) if spec else round(float(m.group(1)) * 30))
frames = f1 - f0 + 1
scene = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'templates', 'blender', 'blocky', 'scene.py')
blender = sfconfig.CFG.get('blender') or 'C:/Program Files/Blender Foundation/Blender 5.2/blender.exe'
os.makedirs(out + '_logs', exist_ok=True)
step = -(-frames // N)
t0 = time.time()
procs = []
for k in range(N):
    a, b = f0 + k * step, min(f1, f0 + (k + 1) * step - 1)
    if a > b:
        break
    env = dict(os.environ, MODE='full', RANGE=f'{a}-{b}')
    log = open(f'{out}_logs/part_{k + 1}.log', 'w')
    procs.append(subprocess.Popen([blender, '-b', '--factory-startup', '--python', scene, '--', table, out], env=env,
                                  stdout=log, stderr=subprocess.STDOUT))
codes = [p.wait() for p in procs]
done = len([f for f in os.listdir(out) if re.fullmatch(r'\d{4}\.png', f) and f0 <= int(f[:4]) <= f1])
print(f'{done} of {frames} frames in {time.time() - t0:.0f} s with {len(procs)} workers; exit codes {codes}')
sys.exit(0 if done >= frames and not any(codes) else 1)
