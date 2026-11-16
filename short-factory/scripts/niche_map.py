"""Map a niche on YouTube the depth-first way (the 'demand map' from a public YouTube training, Sep 2026; notes in reference/methods/youtube-training-notes.md).
Seed searches -> videos that beat the rest -> their channels -> each channel's standout videos, one branch at a time,
using a stack (a to-do pile: the newest find is explored first, then we step back to the next one).
Usage: python -I niche_map.py <name> --seeds seeds.txt [--per-search 20] [--per-seed-channels 3] [--max-channels 30]
                              [--min-views 100000] [--x 3] [--topic "youtube,channel,viral,..."]
  Only on-topic results are followed (title shares a word with its search line or the topic words), and each search
  line opens at most --per-seed-channels new channels, so every line gets explored. Channel lists are cached per day.
  seeds.txt: one search line per line (the 10 common searches of the niche; # starts a comment).
Writes into studies_root/niche_<name>/<YYYY-MM-DD>/:
  raw/search_*.json, raw/channel_*.json   what YouTube returned (flat lists: title, views, length)
  niche_map.xlsx   Searches, Videos, Channels, Standouts, Stack (every step in the order it was explored)
  NICHE_MAP.md     plain-English summary: channels ranked, the top standouts, what to open by hand next
Recommendations ("up next") are not in yt-dlp's flat lists: the summary lists the standouts to open in the browser."""
import argparse, datetime as dt, json, os, re, statistics, subprocess, sys, time, urllib.parse

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import sfconfig  # noqa: E402
from openpyxl import Workbook  # noqa: E402
from openpyxl.styles import Font  # noqa: E402

SHORTS_FILTER = 'EgIYAQ%253D%253D'   # YouTube search filter "under 4 minutes"
TOPIC = 'youtube,youtuber,youtubers,channel,channels,viral,subscribers,subs,algorithm,creator,creators,thumbnail,thumbnails,hook,hooks,grew,grow,famous,strategy,mrbeast,blew'
STOP = set('a an the and or of to in on for how why what this that is are was got get did do my your his her it with from you i'.split())


def words(t):
    t = re.sub(r'#\w+', ' ', (t or '').lower())                 # hashtags (#viralshort, #shorts) say nothing about the topic
    return {w for w in re.findall(r"[a-z0-9']+", t) if w not in STOP and len(w) > 2}


def flat(url, end=None):
    cmd = [sys.executable, '-m', 'yt_dlp', '--flat-playlist', '-J', '--no-warnings']
    if end:
        cmd += ['--playlist-end', str(end)]
    r = subprocess.run(cmd + [url], capture_output=True, text=True, encoding='utf-8', errors='replace')
    time.sleep(1.5)                   # be gentle: YouTube answers 429 (too many requests) when pushed
    if r.returncode or not r.stdout.strip():
        return {'entries': []}
    return json.loads(r.stdout)


def entries(d):
    return [e for e in d.get('entries', []) if e and e.get('view_count') is not None]


def kind(e):
    return 'Short' if (e.get('duration') or 0) <= 180 or '/shorts/' in (e.get('url') or '') else 'Long'


def med(xs):
    return statistics.median(xs) if xs else 0


def main():
    ap = argparse.ArgumentParser(); ap.add_argument('name'); ap.add_argument('--seeds', required=True)
    ap.add_argument('--per-search', type=int, default=20); ap.add_argument('--max-channels', type=int, default=30)
    ap.add_argument('--min-views', type=int, default=100_000); ap.add_argument('--x', type=float, default=3.0)
    ap.add_argument('--per-seed-channels', type=int, default=3); ap.add_argument('--topic', default=TOPIC)
    a = ap.parse_args()
    seeds = [s.strip() for s in open(a.seeds, encoding='utf-8') if s.strip() and not s.strip().startswith('#')]
    name = sfconfig.safe_name(a.name, 'niche map name')
    out = sfconfig.inside(sfconfig.CFG['studies_root'], 'niche_' + name, dt.date.today().isoformat())
    os.makedirs(os.path.join(out, 'raw'), exist_ok=True)
    print('niche map folder:', out)

    videos, channels, stack_log = [], {}, []
    stack = [('seed', s, None) for s in reversed(seeds)]      # first seed on top
    seen_ch, per_seed = set(), {}
    topic = {w.strip().lower() for w in a.topic.split(',') if w.strip()}
    while stack:
        node, val, via = stack.pop()
        if node == 'seed':
            q = urllib.parse.quote_plus(val)
            found = []
            for fmt, url in (('Short', f'https://www.youtube.com/results?search_query={q}&sp={SHORTS_FILTER}'),
                             ('Any', f'ytsearch{a.per_search}:{val}')):
                d = flat(url, a.per_search)
                json.dump(d, open(os.path.join(out, 'raw', f'search_{re.sub(r"[^a-z0-9]+", "_", val.lower())}_{fmt}.json'), 'w', encoding='utf-8'))
                for e in entries(d):
                    v = dict(seed=val, title=e.get('title'), channel=e.get('channel') or e.get('uploader'),
                             channel_id=e.get('channel_id'), views=e['view_count'], duration=e.get('duration'),
                             kind=kind(e), url=e.get('url') or f'https://www.youtube.com/watch?v={e["id"]}')
                    videos.append(v); found.append(v)
            stack_log.append(('search', val, f'{len(found)} videos'))
            keys = words(val) | topic
            for v in found:
                v['on_topic'] = bool(words(v['title']) & keys)
            hits = sorted([v for v in found if v['views'] >= a.min_views and v['channel_id'] and v['on_topic']], key=lambda v: v['views'])
            for v in hits:                                    # biggest ends on top of the stack
                stack.append(('video', v, val))
        elif node == 'video':
            cid = val['channel_id']
            if cid in seen_ch:
                continue                                       # branch already explored: step back
            if per_seed.get(via, 0) >= a.per_seed_channels:
                continue                                       # this search line has had its share
            if len(seen_ch) >= a.max_channels:
                stack_log.append(('skip', val['channel'], 'channel limit reached')); continue
            seen_ch.add(cid); per_seed[via] = per_seed.get(via, 0) + 1
            base = f'https://www.youtube.com/channel/{cid}'
            cache = os.path.join(out, 'raw', f'channel_{cid}.json')
            if os.path.exists(cache):
                c = json.load(open(cache, encoding='utf-8')); sh, lo = c['shorts'], c['videos']
            else:
                sh, lo = flat(base + '/shorts', 200), flat(base + '/videos', 200)
                json.dump({'shorts': sh, 'videos': lo}, open(cache, 'w', encoding='utf-8'))
            S, L = entries(sh), entries(lo)
            ms, ml = med([e['view_count'] for e in S]), med([e['view_count'] for e in L])
            subs = sh.get('channel_follower_count') or lo.get('channel_follower_count')
            stand = []
            for fmt, E, m in (('Short', S, ms), ('Long', L, ml)):
                for e in E:
                    if m and e['view_count'] >= a.x * m and e['view_count'] >= a.min_views:
                        stand.append(dict(channel=val['channel'], kind=fmt, title=e.get('title'), views=e['view_count'],
                                          x=round(e['view_count'] / m, 1), url=e.get('url') or f'https://www.youtube.com/watch?v={e["id"]}'))
            stand.sort(key=lambda s: -s['x'])
            channels[cid] = dict(channel=val['channel'], subs=subs, shorts=len(S), shorts_median=int(ms), longs=len(L),
                                 longs_median=int(ml), standouts=stand, found_via=val['seed'], first_hit=val['title'],
                                 url=base)
            stack_log.append(('channel', val['channel'], f'{len(S)} Shorts (median {int(ms):,}), {len(L)} long (median {int(ml):,}), {len(stand)} standouts'))

    # outlier score for every search result: views vs its own channel's median for that format
    for v in videos:
        c = channels.get(v['channel_id'])
        m = c and (c['shorts_median'] if v['kind'] == 'Short' else c['longs_median'])
        v['x'] = round(v['views'] / m, 1) if m else None

    wb = Workbook(); bold = Font(bold=True)

    def sheet(title, head, rows, first=False):
        ws = wb.active if first else wb.create_sheet()
        ws.title = title; ws.append(head)
        for c in ws[1]:
            c.font = bold
        for r in rows:
            ws.append(r)
        ws.freeze_panes = 'A2'

    sheet('Searches', ['Search line', 'Results', 'Over min views', 'Best views', 'Best title'],
          [[s, len(vs), sum(v['views'] >= a.min_views for v in vs), max((v['views'] for v in vs), default=0),
            max(vs, key=lambda v: v['views'])['title'] if vs else '']
           for s in seeds for vs in [[v for v in videos if v['seed'] == s]]], first=True)
    sheet('Videos', ['Search line', 'Title', 'Channel', 'Views', 'x channel median', 'Format', 'Seconds', 'On topic', 'URL'],
          [[v['seed'], v['title'], v['channel'], v['views'], v['x'], v['kind'], v['duration'], v['on_topic'], v['url']]
           for v in sorted(videos, key=lambda v: -v['views'])])
    sheet('Channels', ['Channel', 'Subscribers', 'Shorts', 'Shorts median', 'Long videos', 'Long median', 'Standouts', 'Found via', 'URL'],
          [[c['channel'], c['subs'], c['shorts'], c['shorts_median'], c['longs'], c['longs_median'], len(c['standouts']), c['found_via'], c['url']]
           for c in sorted(channels.values(), key=lambda c: -(c['subs'] or 0))])
    allst = sorted([s for c in channels.values() for s in c['standouts']], key=lambda s: -s['views'])   # real reach first; x shows how far above normal
    sheet('Standouts', ['Channel', 'Format', 'Title', 'Views', 'x channel median', 'URL'],
          [[s['channel'], s['kind'], s['title'], s['views'], s['x'], s['url']] for s in allst])
    sheet('Stack', ['Step', 'Action', 'Node', 'Result'], [[i + 1, *r] for i, r in enumerate(stack_log)])
    wb.save(os.path.join(out, 'niche_map.xlsx'))

    md = [f'# Niche map: {a.name} ({dt.date.today().isoformat()})', '',
          f'{len(seeds)} search lines, {len(videos)} results, {len(channels)} channels opened. '
          f'A standout is a video with at least {a.x:g}x its own channel\'s median views for that format and {a.min_views:,}+ views.', '',
          '## Channels (most subscribers first)', '', '| Channel | Subs | Shorts (median) | Long (median) | Standouts | Found via |', '|---|---|---|---|---|---|']
    for c in sorted(channels.values(), key=lambda c: -(c['subs'] or 0)):
        md.append(f"| {c['channel']} | {c['subs'] or '?':,} | {c['shorts']} ({c['shorts_median']:,}) | {c['longs']} ({c['longs_median']:,}) | {len(c['standouts'])} | {c['found_via']} |"
                  if c['subs'] else f"| {c['channel']} | ? | {c['shorts']} ({c['shorts_median']:,}) | {c['longs']} ({c['longs_median']:,}) | {len(c['standouts'])} | {c['found_via']} |")
    md += ['', '## Top 30 standouts (most views first)', '', '| x median | Views | Format | Channel | Title |', '|---|---|---|---|---|']
    md += [f"| {s['x']} | {s['views']:,} | {s['kind']} | {s['channel']} | {s['title']} |" for s in allst[:30]]
    md += ['', '## Open by hand next (recommendations are not in the flat lists)', '']
    md += [f"- {s['channel']}: {s['title']} ({s['url']})" for s in allst[:8]]
    open(os.path.join(out, 'NICHE_MAP.md'), 'w', encoding='utf-8').write('\n'.join(md) + '\n')
    print(f'{len(videos)} videos, {len(channels)} channels, {len(allst)} standouts -> {out}')


if __name__ == '__main__':
    main()
