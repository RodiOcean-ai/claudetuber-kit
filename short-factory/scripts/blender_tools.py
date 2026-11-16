"""Run an episode's Blender world (blender/world.py built on sf_world) without typing Blender commands by hand.
Usage: python -I blender_tools.py check  <world.py>                          overlap pass: every CHECK pair must say "clear"
       python -I blender_tools.py stills <world.py> <f1,f2,...> [--outline] stills + one contact sheet (render/stills_<time>/)
       python -I blender_tools.py render <world.py> <vN> [--outline] [--parts 3]
              full render to blender/render/<vN>/, encoded to blender/render/world_<vN>.mp4 and copied to edit/public/clips/world.mp4;
              then the loop seam and the whips (edit/src/swishes.json) are done automatically
       python -I blender_tools.py seam   <frames_dir>                        last vs first frame, compared with a normal frame step
       python -I blender_tools.py whips  <render.log> [--top 5]              camera whips -> edit/src/swishes.json"""
import argparse, datetime as dt, glob, json, os, re, shutil, subprocess, sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import sfconfig  # noqa: E402


def episode_of(world):
    return os.path.dirname(os.path.dirname(os.path.abspath(world)))


def blender(world, out, env_extra=None, still=None, log=None):
    env = dict(os.environ, **(env_extra or {}))
    cmd = [sfconfig.CFG['blender'], '-b', '--factory-startup', '--python-exit-code', '1', '--python', os.path.abspath(world), '--', out]
    if still is not None:
        cmd += ['--still', str(still)]
    r = subprocess.run(cmd, env=env, capture_output=True, text=True, encoding='utf-8', errors='replace', cwd=os.path.dirname(os.path.abspath(world)))
    text = r.stdout + r.stderr
    if log:
        open(log, 'a', encoding='utf-8').write(text)
    if r.returncode and 'CHECK' not in (env_extra or {}):
        sys.stdout.write(text[-3000:]); sys.exit(f'Blender failed (exit {r.returncode})')
    return text


def info_lines(text):
    return [l for l in text.splitlines() if l.startswith(('world:', 'physics:', 'CHECK', 'WHIPS_JSON')) or 'Error' in l or 'Traceback' in l]


def cmd_check(a):
    text = blender(a.world, os.path.join(episode_of(a.world), 'blender', 'render', 'check_'), {'CHECK': '1'})
    lines = [l for l in text.splitlines() if l.startswith('CHECK') or 'Error' in l]
    print('\n'.join(lines) or text[-2000:])
    bad = [l for l in lines if l.startswith('CHECK') and not l.endswith('clear')]
    print('RESULT:', 'all clear' if not bad and lines else f'{len(bad)} pair(s) pass through each other - fix before rendering')


def sheet(pngs, out, cols=4, w=270):
    from PIL import Image, ImageDraw
    ims = [Image.open(p).convert('RGB') for p in pngs]
    h = round(w * ims[0].height / ims[0].width); rows = (len(ims) + cols - 1) // cols
    S = Image.new('RGB', (cols * w, rows * (h + 22)), 'white'); d = ImageDraw.Draw(S)
    for i, (p, im) in enumerate(zip(pngs, ims)):
        x, y = (i % cols) * w, (i // cols) * (h + 22)
        S.paste(im.resize((w, h)), (x, y + 22)); f = int(os.path.splitext(os.path.basename(p))[0])
        d.text((x + 6, y + 4), f'frame {f}  ({(f - 1) / 30:.2f} s)', fill='black')
    S.save(out, quality=90); return out


def cmd_stills(a):
    out = os.path.join(episode_of(a.world), 'blender', 'render', 'stills_' + dt.datetime.now().strftime('%H%M%S'))
    os.makedirs(out, exist_ok=True)
    env = {'STILLS': a.frames}
    if a.outline:
        env['OUTLINE'] = '1'
    text = blender(a.world, out, env, log=os.path.join(out, 'render.log'))
    print('\n'.join(l for l in info_lines(text) if not l.startswith('WHIPS_JSON')))
    pngs = sorted(glob.glob(os.path.join(out, '*.png')))
    print('contact sheet:', sheet(pngs, os.path.join(out, 'sheet.jpg')), f'({len(pngs)} stills)')


def frames_total(world, env):
    text = blender(world, os.devnull, dict(env, CHECK='1', SF_COUNT='1'))
    m = re.search(r'world: frames (\d+)', text)
    return int(m.group(1)) if m else None


def cmd_render(a):
    ep = episode_of(a.world); out = os.path.join(ep, 'blender', 'render', a.version); os.makedirs(out, exist_ok=True)
    log = os.path.join(out, 'render.log'); env = {'OUTLINE': '1'} if a.outline else {}
    if a.parts > 1:
        n = frames_total(a.world, env) or sys.exit('could not read the frame count')
        step = -(-n // a.parts); procs = []
        for k in range(a.parts):
            e = dict(os.environ, **env, FRAME_START=str(1 + k * step), FRAME_END=str(min(n, (k + 1) * step)))
            procs.append(subprocess.Popen([sfconfig.CFG['blender'], '-b', '--factory-startup', '--python', os.path.abspath(a.world), '--', out + os.sep],
                                          env=e, cwd=os.path.dirname(os.path.abspath(a.world)), stdout=open(log + f'.{k}', 'w'), stderr=subprocess.STDOUT))
        for p in procs:
            p.wait()
        for k in range(a.parts):
            open(log, 'a', encoding='utf-8').write(open(log + f'.{k}', encoding='utf-8', errors='replace').read()); os.remove(log + f'.{k}')
    else:
        blender(a.world, out + os.sep, env, log=log)
    text = open(log, encoding='utf-8', errors='replace').read()
    print('\n'.join(dict.fromkeys(l for l in info_lines(text) if not l.startswith('WHIPS_JSON'))))
    pngs = sorted(glob.glob(os.path.join(out, '[0-9]*.png')))
    if not pngs:
        sys.exit('no frames rendered - see ' + log)
    mp4 = os.path.join(ep, 'blender', 'render', f'world_{a.version}.mp4')
    subprocess.run(['ffmpeg', '-y', '-loglevel', 'error', '-framerate', '30', '-start_number', os.path.basename(pngs[0])[:4].lstrip('0') or '0',
                    '-i', os.path.join(out, '%04d.png'), '-c:v', 'libx264', '-crf', '16', '-preset', 'slow', '-pix_fmt', 'yuv420p', mp4], check=True)
    clips = os.path.join(ep, 'edit', 'public', 'clips'); os.makedirs(clips, exist_ok=True)
    shutil.copy(mp4, os.path.join(clips, 'world.mp4'))
    print(f'video: {mp4} ({len(pngs)} frames, {len(pngs) / 30:.2f} s) -> copied to the edit as clips/world.mp4')
    seam(out); whips(log, ep, 5)


def seam(frames_dir):
    import numpy as np
    from PIL import Image
    pngs = sorted(glob.glob(os.path.join(frames_dir, '[0-9]*.png')))
    load = lambda p: np.asarray(Image.open(p).convert('L').resize((270, 480)), dtype=np.float32)
    steps = [float(np.abs(load(pngs[i]) - load(pngs[i + 1])).mean()) for i in range(0, len(pngs) - 1, max(1, len(pngs) // 40))]
    normal = float(np.median(steps)); s = float(np.abs(load(pngs[-1]) - load(pngs[0])).mean())
    ok = s <= max(normal * 1.5, 2.0)
    print(f'loop seam: last->first {s:.2f} vs a normal frame step {normal:.2f} -> {"SMOOTH" if ok else "JUMPS: fix the ending pose in world.py"}')
    return s, normal


def whips(log, ep, top):
    text = open(log, encoding='utf-8', errors='replace').read()
    m = re.findall(r'WHIPS_JSON (\[.*\])', text)
    if not m:
        print('no whips in the log'); return []
    w = json.loads(m[-1])
    pick = sorted(sorted(w, key=lambda x: -x[1])[:top]) if any(x[1] for x in w) else w[:top]
    times = [round(x[0], 2) for x in pick]
    dst = os.path.join(ep, 'edit', 'src', 'swishes.json')
    if os.path.isdir(os.path.dirname(dst)):
        json.dump(times, open(dst, 'w'))
    print('swishes at', times, '->', dst)
    return times


def main():
    ap = argparse.ArgumentParser(); sp = ap.add_subparsers(dest='cmd', required=True)
    p = sp.add_parser('check'); p.add_argument('world')
    p = sp.add_parser('stills'); p.add_argument('world'); p.add_argument('frames'); p.add_argument('--outline', action='store_true')
    p = sp.add_parser('render'); p.add_argument('world'); p.add_argument('version'); p.add_argument('--outline', action='store_true')
    p.add_argument('--parts', type=int, default=1)
    p = sp.add_parser('seam'); p.add_argument('frames_dir')
    p = sp.add_parser('whips'); p.add_argument('log'); p.add_argument('--top', type=int, default=5)
    a = ap.parse_args()
    if a.cmd == 'check':
        cmd_check(a)
    elif a.cmd == 'stills':
        cmd_stills(a)
    elif a.cmd == 'render':
        cmd_render(a)
    elif a.cmd == 'seam':
        seam(a.frames_dir)
    else:
        ep = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(a.log))))
        whips(a.log, ep, a.top)


if __name__ == '__main__':
    main()
