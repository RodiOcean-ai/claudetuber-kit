"""Write post/POST.md for an episode: title, description with the credit and "Not affiliated" line, hashtags, platform
settings (Made for kids No, AI label on) and the final video's facts (length, loudness, size), plus the slot if booked.
Usage: python -I post_kit.py <episode_dir> --title "..." --credit "Channel credit: @handle (YouTube)" [--description "..."]
       [--hashtags "#shorts #youtube"] [--video post/<slug>_FINAL.mp4]
The final video is post/*_FINAL.mp4, else the newest edit/out/<slug>_vN.mp4."""
import argparse, glob, json, os, re, subprocess, sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import sfconfig  # noqa: E402


def final_video(ep):
    c = glob.glob(os.path.join(ep, 'post', '*_FINAL.mp4'))
    if c:
        return c[0]
    c = [f for f in glob.glob(os.path.join(ep, 'edit', 'out', '*_v*.mp4')) if not re.search(r'(_phone|raw_)', os.path.basename(f))]
    return max(c, key=os.path.getmtime) if c else None


def facts(v):
    pr = json.loads(subprocess.run(['ffprobe', '-v', 'error', '-show_entries', 'format=duration:stream=width,height', '-of', 'json', v],
                                   capture_output=True, text=True).stdout)
    s = next(x for x in pr['streams'] if x.get('width'))
    e = subprocess.run(['ffmpeg', '-hide_banner', '-nostats', '-i', v, '-af', 'ebur128', '-f', 'null', '-'], capture_output=True, text=True).stderr
    lufs = re.findall(r'I:\s+(-?[\d.]+) LUFS', e)
    return dict(LENGTH=f'{float(pr["format"]["duration"]):.1f}', W=str(s['width']), H=str(s['height']),
                SIZE_MB=f'{os.path.getsize(v) / 1e6:.1f}', LUFS=lufs[-1] if lufs else '?')


def main():
    ap = argparse.ArgumentParser(); ap.add_argument('episode'); ap.add_argument('--title', required=True); ap.add_argument('--credit', required=True)
    ap.add_argument('--description', default=''); ap.add_argument('--hashtags', default='#shorts'); ap.add_argument('--video')
    a = ap.parse_args(); ep = os.path.abspath(a.episode); slug = os.path.basename(ep)
    v = a.video or final_video(ep) or sys.exit('no final video found (post/*_FINAL.mp4 or edit/out/<slug>_vN.mp4)')
    kw = facts(v); kw.update(SLUG=slug, VIDEO=os.path.relpath(v, ep).replace('\\', '/'), TITLE=a.title, DESCRIPTION=a.description,
                             CREDIT=a.credit, HASHTAGS=a.hashtags)
    m = os.path.join(ep, 'edit', 'src', 'music.json')
    kw['MUSIC'] = json.load(open(m))['track'] if os.path.exists(m) else '?'
    import tracker
    cal = [r for r in tracker.rows(tracker.book()['Posting calendar']) if r['episode'] == slug]
    kw['SLOT'] = (f'{str(cal[0]["date"])[:10]} {cal[0]["time"]} local time ({cal[0]["state"]})' if cal
                  else 'not booked yet: run calendar_plan.py next ' + slug)
    if len(a.title) > 70:
        print('  WARNING: the title is longer than 70 characters')
    s = open(os.path.join(sfconfig.TEMPLATES, 'episode', 'POST.md'), encoding='utf-8').read()
    for k, val in kw.items():
        s = s.replace('{' + k + '}', val)
    os.makedirs(os.path.join(ep, 'post'), exist_ok=True)
    out = os.path.join(ep, 'post', 'POST.md'); open(out, 'w', encoding='utf-8').write(s)
    print('saved', out, '|', kw['LENGTH'], 's,', kw['LUFS'], 'LUFS,', kw['SIZE_MB'], 'MB,', kw['W'] + 'x' + kw['H'])


if __name__ == '__main__':
    main()
