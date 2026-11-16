"""Render approved styles to MP4 (ONLY after the owner's approval on the review page or in the chat; owner's rule).
Usage: py -3.13 tools/render.py S01 [S02 ...] [--force]
- refuses a style that has no approval for its current build label in review/notes.json (unless --force, which is only
  for an approval the owner gave in the chat; say so in the log);
- renders with the Remotion CLI (graphics card on for the 3D styles), then masters the sound to -12 LUFS / -1 dB true peak
  (house rule) without touching the picture, and writes out/<id>.mp4 plus out/<id>.render.json (seconds taken, sizes);
- appends one line per render to log/LOG.md."""
import json, os, subprocess, sys, time

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
IDS = ['S01-KineticTypography', 'S02-MotionGraphics', 'S03-Screencast', 'S04-Isometric', 'S05-Whiteboard', 'S06-Comic',
       'S07-TwoPointFiveD', 'S08-Collage', 'S09-CharacterStory', 'S10-ThreeD', 'S11-StopMotion',
       'T05-WhiteboardThreeJS', 'T06-ComicThreeJS']


def sid(s):
    m = [x for x in IDS if x.lower().startswith(s.lower())]
    if len(m) != 1:
        sys.exit(f'unknown style {s}')
    return m[0]


def approved(style):
    notes = json.load(open(os.path.join(ROOT, 'review', 'notes.json'), encoding='utf-8'))
    builds = json.load(open(os.path.join(ROOT, 'review', 'builds.json'), encoding='utf-8'))
    label = builds.get(style, {}).get('label')
    return label and any(a['style'] == style and a['build'] == label for a in notes['approvals']), label


def loudness(path):
    r = subprocess.run(['ffmpeg', '-hide_banner', '-nostats', '-i', path, '-af', 'loudnorm=I=-12:TP=-1:LRA=11:print_format=json', '-f', 'null', '-'],
                       capture_output=True, text=True)
    txt = r.stderr[r.stderr.rindex('{'):r.stderr.rindex('}') + 1]
    return json.loads(txt)


def main():
    args = [a for a in sys.argv[1:] if not a.startswith('--')]
    force = '--force' in sys.argv
    os.makedirs(os.path.join(ROOT, 'out'), exist_ok=True)
    for a in args:
        style = sid(a)
        ok, label = approved(style)
        if not ok and not force:
            print(f'SKIP {style}: {label} is not approved on the review page'); continue
        raw = os.path.join(ROOT, 'out', f'{style}.raw.mp4'); final = os.path.join(ROOT, 'out', f'{style}.mp4')
        t = time.time()
        cmd = ['npx', 'remotion', 'render', 'src/index.ts', style, raw, '--gl=angle', '--concurrency=6', '--codec=h264', '--crf=16',
               '--audio-codec=aac', '--audio-bitrate=320k', '--log=error']
        r = subprocess.run(cmd, cwd=ROOT, shell=(os.name == 'nt'))
        if r.returncode:
            sys.exit(f'render failed for {style}')
        took = time.time() - t
        m = loudness(raw)
        af = (f"loudnorm=I=-12:TP=-1:LRA=11:measured_I={m['input_i']}:measured_TP={m['input_tp']}:measured_LRA={m['input_lra']}:"
              f"measured_thresh={m['input_thresh']}:offset={m['target_offset']}:linear=true,aresample=48000")
        subprocess.run(['ffmpeg', '-v', 'error', '-y', '-i', raw, '-c:v', 'copy', '-af', af, '-c:a', 'aac', '-b:a', '320k', final], check=True)
        os.remove(raw)
        info = {'style': style, 'build': label, 'render_seconds': round(took, 1), 'mb': round(os.path.getsize(final) / 1e6, 1),
                'at': time.strftime('%Y-%m-%d %H:%M'), 'forced': force and not ok}
        json.dump(info, open(os.path.join(ROOT, 'out', f'{style}.render.json'), 'w'), indent=1)
        with open(os.path.join(ROOT, 'log', 'LOG.md'), 'a', encoding='utf-8') as f:
            f.write(f"- {info['at']}  {style}: rendered {label} in {info['render_seconds']} s ({info['mb']} MB)\n")
        print(f'{style}: {took:.1f} s -> {final}')


if __name__ == '__main__':
    main()
