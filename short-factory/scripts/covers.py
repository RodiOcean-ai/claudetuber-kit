"""Cover frames for apps that only let you pick a frame (and a backup for the thumbnail).
Usage: python -I covers.py <video.mp4> [seconds ...]            candidates (default: 8 frames from 20-80 % of the video) + a sheet
       python -I covers.py <video.mp4> --main 8.4 --backup 15.3  saves post/COVER_main.jpg and post/COVER_backup.jpg
Frames go to <episode>/post/covers/ when the video sits in an episode, else next to the video."""
import argparse, os, subprocess, sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import sfconfig  # noqa: E402,F401  (puts ffmpeg on PATH)


def duration(v):
    return float(subprocess.run(['ffprobe', '-v', 'error', '-show_entries', 'format=duration', '-of', 'csv=p=0', v],
                                capture_output=True, text=True).stdout.strip())


def grab(v, t, out):
    subprocess.run(['ffmpeg', '-y', '-loglevel', 'error', '-ss', f'{t:.2f}', '-i', v, '-frames:v', '1', '-q:v', '2', out], check=True)
    return out


def post_dir(v):
    d = os.path.dirname(os.path.abspath(v))
    for _ in range(3):
        if os.path.exists(os.path.join(d, 'JOURNEY.md')):
            return os.path.join(d, 'post')
        d = os.path.dirname(d)
    return os.path.dirname(os.path.abspath(v))


def main():
    ap = argparse.ArgumentParser(); ap.add_argument('video'); ap.add_argument('times', nargs='*', type=float)
    ap.add_argument('--main', type=float); ap.add_argument('--backup', type=float)
    a = ap.parse_args(); post = post_dir(a.video); os.makedirs(post, exist_ok=True)
    if a.main is not None:
        print('saved', grab(a.video, a.main, os.path.join(post, 'COVER_main.jpg')))
        if a.backup is not None:
            print('saved', grab(a.video, a.backup, os.path.join(post, 'COVER_backup.jpg')))
        return
    d = duration(a.video); ts = a.times or [round(d * (0.2 + 0.6 * k / 7), 2) for k in range(8)]
    out = os.path.join(post, 'covers'); os.makedirs(out, exist_ok=True)
    files = [grab(a.video, t, os.path.join(out, f'cover_{t:05.2f}s.jpg')) for t in ts]
    from PIL import Image, ImageDraw
    w, h = 270, 480; S = Image.new('RGB', (4 * w, ((len(files) + 3) // 4) * (h + 24)), 'white'); dr = ImageDraw.Draw(S)
    for i, (f, t) in enumerate(zip(files, ts)):
        x, y = (i % 4) * w, (i // 4) * (h + 24)
        S.paste(Image.open(f).convert('RGB').resize((w, h)), (x, y + 24)); dr.text((x + 6, y + 6), f'{t:.2f} s', fill='black')
    S.save(os.path.join(out, 'sheet.jpg'), quality=90)
    print(f'{len(files)} candidates and a sheet in {out}; then: covers.py <video> --main <s> --backup <s>')


if __name__ == '__main__':
    main()
