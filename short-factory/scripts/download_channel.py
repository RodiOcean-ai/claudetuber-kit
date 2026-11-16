"""List a channel's Shorts and long videos, pick the most-viewed ones and download them for study_channel.py.
Usage: python -I download_channel.py <@handle | channel url> [--key name] [--top-shorts 10] [--top-longs 10] [--list-only]
Writes into the study folder (config studies_root/<key>, or a legacy study folder):
  shorts.json, videos.json   full flat lists (id, title, views, duration)
  picks.json                 the chosen top N + N, every title (for title patterns), counts
  videos/<id>.mp4 + .info.json + .en.vtt + .jpg   (720p at most), download.log (the exact command)
Ids already analysed (tracker) are skipped. --list-only stops after picks.json (no downloads)."""
import argparse, json, os, re, subprocess, sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import sfconfig  # noqa: E402
import tracker  # noqa: E402


def flat(url):
    r = subprocess.run([sys.executable, '-m', 'yt_dlp', '--flat-playlist', '-J', '--no-warnings', url],
                       capture_output=True, text=True, encoding='utf-8', errors='replace')
    if r.returncode or not r.stdout.strip():
        return {'entries': []}
    return json.loads(r.stdout)


def main():
    ap = argparse.ArgumentParser(); ap.add_argument('channel'); ap.add_argument('--key')
    ap.add_argument('--top-shorts', type=int, default=sfconfig.CFG['study']['top_shorts'])
    ap.add_argument('--top-longs', type=int, default=sfconfig.CFG['study']['top_longs']); ap.add_argument('--list-only', action='store_true')
    a = ap.parse_args()
    ch = a.channel.strip()
    base = ch if ch.startswith('http') else f'https://www.youtube.com/{ch if ch.startswith("@") else "@" + ch}'
    base = re.sub(r'/(shorts|videos|featured)/?$', '', base)
    key = (a.key or re.sub(r'[^a-z0-9-]', '', base.rsplit('/', 1)[-1].lower().lstrip('@'))) or 'channel'
    study = sfconfig.study_dir(key); os.makedirs(os.path.join(study, 'videos'), exist_ok=True)
    print('study folder:', study)
    sh, lo = flat(base + '/shorts'), flat(base + '/videos')
    json.dump(sh, open(os.path.join(study, 'shorts.json'), 'w', encoding='utf-8'))
    json.dump(lo, open(os.path.join(study, 'videos.json'), 'w', encoding='utf-8'))
    S = [e for e in sh.get('entries', []) if e and e.get('view_count') is not None]
    L = [e for e in lo.get('entries', []) if e and e.get('view_count') is not None]
    print(f'found {len(S)} Shorts and {len(L)} long videos')
    done = tracker.analysed_ids(key)
    top = []
    for kind, lst, n in (('short', S, a.top_shorts), ('long', L, a.top_longs)):
        for rank, e in enumerate(sorted(lst, key=lambda e: -e['view_count'])[:n], 1):
            top.append({'id': e['id'], 'kind': kind, 'rank': rank, 'title': e.get('title', ''), 'views': e['view_count'],
                        'duration': e.get('duration'), 'already_analysed': e['id'] in done})
    picks = {'handle': base.rsplit('/', 1)[-1], 'url': base, 'subscribers': sh.get('channel_follower_count') or lo.get('channel_follower_count'),
             'n_shorts': len(S), 'n_longs': len(L), 'top': top,
             'all_titles': [{'kind': 'short', 'title': e.get('title', ''), 'views': e['view_count']} for e in S] +
                           [{'kind': 'long', 'title': e.get('title', ''), 'views': e['view_count']} for e in L]}
    json.dump(picks, open(os.path.join(study, 'picks.json'), 'w', encoding='utf-8'), indent=1, ensure_ascii=False)
    for p in top:
        print(f'  {p["kind"]:5} #{p["rank"]:<2} {p["views"] / 1e6:8.1f}M  {p["title"][:70]}' + ('  (already analysed)' if p['already_analysed'] else ''))
    if a.list_only:
        return
    want = [p for p in top if not p['already_analysed'] and not os.path.exists(os.path.join(study, 'videos', p['id'] + '.mp4'))]
    if not want:
        print('nothing new to download'); return
    lst = os.path.join(study, 'to_download.txt')
    open(lst, 'w').write('\n'.join(f'https://www.youtube.com/watch?v={p["id"]}' for p in want))
    h = sfconfig.CFG['study']['max_height']
    cmd = [sys.executable, '-m', 'yt_dlp', '-a', lst, '-f', f'bv*[height<={h}][ext=mp4]+ba[ext=m4a]/b[height<={h}][ext=mp4]/b',
           '--merge-output-format', 'mp4', '-o', os.path.join(study, 'videos', '%(id)s.%(ext)s'), '--write-info-json',
           '--write-subs', '--write-auto-subs', '--sub-langs', 'en', '--sub-format', 'vtt', '--write-thumbnail', '--convert-thumbnails', 'jpg',
           '--no-overwrites', '--ignore-errors']
    with open(os.path.join(study, 'download.log'), 'a', encoding='utf-8') as log:
        log.write(' '.join(f'"{c}"' if ' ' in c else c for c in cmd) + '\n')
        r = subprocess.run(cmd, stdout=log, stderr=subprocess.STDOUT)
    got = [p for p in want if os.path.exists(os.path.join(study, 'videos', p['id'] + '.mp4'))]
    print(f'downloaded {len(got)} of {len(want)}' + ('' if len(got) == len(want) else ' - see download.log (blocked videos: use the browser-only light study)'))


if __name__ == '__main__':
    main()
