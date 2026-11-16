"""The master workbook (data/tracker.xlsx): every channel studied, every video analysed, every episode, music, posts, stats.
Nothing is analysed twice: download_channel.py and study_channel.py ask `analysed_ids()` first.

Usage: python -I tracker.py init                       create the workbook (keeps existing rows)
       python -I tracker.py status                     plain summary of channels, episodes, next music, next post slot
       python -I tracker.py analysed <channel_key>     ids already analysed for a channel
       python -I tracker.py add-channel <key> --handle @x --subs N --shorts N --longs N [--notes "..."]
       python -I tracker.py add-episode <slug> --title "..." --subject <key> [--music steps] [--status idea|script|voice|3d|edit|posted]
       python -I tracker.py set-status <slug> <status>
       python -I tracker.py music-next                 next track in the rotation
       python -I tracker.py log-post <slug> <platform> "YYYY-MM-DD HH:MM"
       python -I tracker.py log-stats <slug> <24|168> --views N [--stayed PCT] [--avg-pct PCT] [--subs N] [--platform YouTube]
       python -I tracker.py credits <slug> <amount> "<what>"
       python -I tracker.py add-pattern <channel_key> "<area>" "<pattern>" "<evidence>"
       python -I tracker.py add-sauce <channel_key> "<recipe line>" "<evidence>" [--copy yes|no]
       python -I tracker.py add-skill <channel_key> "<skill or agent name>" "<what it adds>"
"""
import argparse, datetime as dt, os, sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import sfconfig  # noqa: E402
from openpyxl import Workbook, load_workbook  # noqa: E402  (openpyxl comes from the pylib folder)
from openpyxl.styles import Font, PatternFill  # noqa: E402

SHEETS = {
    'Channels': ['key', 'handle', 'study folder', 'subscribers', 'shorts', 'long videos', 'studied on', 'status', 'notes'],
    'Videos analysed': ['channel', 'id', 'kind', 'rank', 'title', 'views', 'duration_s', 'words', 'words_per_s', 'cuts_per_min',
                        'avg_shot_s', 'voice_minus_bg_lu', 'lufs', 'music_share', 'sfx_per_min', 'loop', 'first_words', 'analysed on'],
    'Patterns': ['channel', 'area', 'pattern', 'evidence', 'added on'],
    'Secret sauce': ['channel', 'recipe line', 'evidence', 'we copy it?', 'added on'],
    'Skills & experts': ['channel', 'skill or agent', 'what it adds', 'added on'],
    'Episodes': ['slug', 'title', 'subject channel', 'music', 'status', 'folder', 'created', 'posted', 'notes'],
    'Music rotation': ['when', 'episode', 'track', 'music_in_s'],
    'Posting calendar': ['date', 'time', 'episode', 'platform', 'state'],
    'Performance': ['episode', 'platform', 'hours after post', 'views', 'stayed to watch %', 'avg % watched', 'subscribers', 'logged on'],
    'Credits': ['episode', 'amount', 'what', 'logged on'],
}
HEAD = PatternFill('solid', fgColor='1F2A44')


def today():
    return dt.date.today().isoformat()


def book():
    if os.path.exists(sfconfig.TRACKER):
        wb = load_workbook(sfconfig.TRACKER)
    else:
        os.makedirs(os.path.dirname(sfconfig.TRACKER), exist_ok=True)
        wb = Workbook(); wb.remove(wb.active)
    for name, cols in SHEETS.items():
        if name not in wb.sheetnames:
            ws = wb.create_sheet(name); ws.append(cols)
            for c in ws[1]:
                c.font = Font(bold=True, color='FFFFFF'); c.fill = HEAD
            ws.freeze_panes = 'A2'
    return wb


def save(wb):
    for ws in wb.worksheets:
        for col in ws.columns:
            w = max(len(str(c.value or '')) for c in col[:200])
            ws.column_dimensions[col[0].column_letter].width = min(60, max(10, w + 2))
    wb.save(sfconfig.TRACKER)


def rows(ws):
    hdr = [c.value for c in ws[1]]
    return [dict(zip(hdr, [c.value for c in r])) for r in ws.iter_rows(min_row=2) if any(c.value is not None for c in r)]


def upsert(ws, key_cols, rec):
    hdr = [c.value for c in ws[1]]
    for r in ws.iter_rows(min_row=2):
        if all(r[hdr.index(k)].value == rec.get(k) for k in key_cols):
            for k, v in rec.items():
                if v is not None:
                    r[hdr.index(k)].value = v
            return
    ws.append([rec.get(h) for h in hdr])


def analysed_ids(channel):
    wb = book()
    return {str(r['id']) for r in rows(wb['Videos analysed']) if r['channel'] == channel}


def add_video(wb, rec):
    rec.setdefault('analysed on', today())
    upsert(wb['Videos analysed'], ['channel', 'id'], rec)


def music_next(wb=None):
    wb = wb or book()
    order = sfconfig.CFG['music_rotation']
    used = [r['track'] for r in rows(wb['Music rotation']) if r['track'] in order]
    return order[(order.index(used[-1]) + 1) % len(order)] if used else order[0]


def main():
    ap = argparse.ArgumentParser(); sp = ap.add_subparsers(dest='cmd', required=True)
    sp.add_parser('init'); sp.add_parser('status'); sp.add_parser('music-next')
    p = sp.add_parser('analysed'); p.add_argument('key')
    p = sp.add_parser('add-channel'); p.add_argument('key'); p.add_argument('--handle'); p.add_argument('--subs', type=int)
    p.add_argument('--shorts', type=int); p.add_argument('--longs', type=int); p.add_argument('--notes'); p.add_argument('--status', default='studied')
    p = sp.add_parser('add-episode'); p.add_argument('slug'); p.add_argument('--title'); p.add_argument('--subject'); p.add_argument('--music')
    p.add_argument('--status', default='idea'); p.add_argument('--notes')
    p = sp.add_parser('set-status'); p.add_argument('slug'); p.add_argument('status')
    p = sp.add_parser('log-post'); p.add_argument('slug'); p.add_argument('platform'); p.add_argument('when')
    p = sp.add_parser('log-stats'); p.add_argument('slug'); p.add_argument('hours', type=int); p.add_argument('--views', type=int, required=True)
    p.add_argument('--stayed', type=float); p.add_argument('--avg-pct', type=float); p.add_argument('--subs', type=int); p.add_argument('--platform', default='YouTube')
    p = sp.add_parser('credits'); p.add_argument('slug'); p.add_argument('amount', type=float); p.add_argument('what')
    for name, extra in (('add-pattern', ['area', 'pattern', 'evidence']), ('add-sauce', ['line', 'evidence']), ('add-skill', ['name', 'adds'])):
        p = sp.add_parser(name); p.add_argument('key')
        for e in extra:
            p.add_argument(e)
        if name == 'add-sauce':
            p.add_argument('--copy', default='yes')
    a = ap.parse_args()
    if getattr(a, 'key', None) is not None:                # channel keys and episode slugs name folders: plain names only
        a.key = sfconfig.safe_name(a.key.strip().lower().lstrip('@'), 'channel key')
    if getattr(a, 'slug', None) is not None:
        a.slug = sfconfig.safe_name(a.slug, 'episode slug')
    wb = book()
    if a.cmd == 'init':
        save(wb); print('tracker ready:', sfconfig.TRACKER)
    elif a.cmd == 'analysed':
        print('\n'.join(sorted(analysed_ids(a.key))) or '(none)')
    elif a.cmd == 'add-channel':
        upsert(wb['Channels'], ['key'], {'key': a.key, 'handle': a.handle, 'study folder': sfconfig.study_dir(a.key), 'subscribers': a.subs,
                                         'shorts': a.shorts, 'long videos': a.longs, 'studied on': today(), 'status': a.status, 'notes': a.notes})
        save(wb); print('channel saved', a.key)
    elif a.cmd == 'add-episode':
        upsert(wb['Episodes'], ['slug'], {'slug': a.slug, 'title': a.title, 'subject channel': a.subject, 'music': a.music, 'status': a.status,
                                          'folder': sfconfig.inside(sfconfig.CFG['episodes_root'], a.slug), 'created': today(), 'notes': a.notes})
        save(wb); print('episode saved', a.slug)
    elif a.cmd == 'set-status':
        upsert(wb['Episodes'], ['slug'], {'slug': a.slug, 'status': a.status}); save(wb); print(a.slug, '->', a.status)
    elif a.cmd == 'music-next':
        print(music_next(wb))
    elif a.cmd == 'log-post':
        d, t = (a.when.split(' ') + [''])[:2]
        upsert(wb['Posting calendar'], ['date', 'episode', 'platform'], {'date': d, 'time': t, 'episode': a.slug, 'platform': a.platform, 'state': 'posted'})
        upsert(wb['Episodes'], ['slug'], {'slug': a.slug, 'status': 'posted', 'posted': a.when})
        save(wb); print('post logged')
    elif a.cmd == 'log-stats':
        upsert(wb['Performance'], ['episode', 'platform', 'hours after post'], {'episode': a.slug, 'platform': a.platform, 'hours after post': a.hours,
               'views': a.views, 'stayed to watch %': a.stayed, 'avg % watched': a.avg_pct, 'subscribers': a.subs, 'logged on': today()})
        save(wb); print('stats logged')
    elif a.cmd == 'credits':
        wb['Credits'].append([a.slug, a.amount, a.what, today()]); save(wb); print('credits logged')
    elif a.cmd == 'add-pattern':
        wb['Patterns'].append([a.key, a.area, a.pattern, a.evidence, today()]); save(wb); print('pattern added')
    elif a.cmd == 'add-sauce':
        wb['Secret sauce'].append([a.key, a.line, a.evidence, a.copy, today()]); save(wb); print('sauce added')
    elif a.cmd == 'add-skill':
        wb['Skills & experts'].append([a.key, a.name, a.adds, today()]); save(wb); print('skill recorded')
    elif a.cmd == 'status':
        ch = rows(wb['Channels']); ep = rows(wb['Episodes']); va = rows(wb['Videos analysed']); perf = rows(wb['Performance'])
        cal = rows(wb['Posting calendar'])
        print(f'Channels studied: {len(ch)} ({", ".join(c["key"] for c in ch)})')
        print(f'Videos analysed: {len(va)}')
        print('Episodes:')
        for e in ep:
            print(f'  {e["slug"]}: {e["status"]}  "{e["title"] or ""}"  music={e["music"] or "-"}')
        print('Latest stats:')
        for p in perf[-5:]:
            print(f'  {p["episode"]} {p["platform"]} @{p["hours after post"]}h: {p["views"]} views, stayed {p["stayed to watch %"]}%')
        last = sorted([c for c in cal if c['date']], key=lambda c: c['date'])[-1:] if cal else []
        print('Last post:', f'{last[0]["date"]} {last[0]["time"]} {last[0]["episode"]}' if last else 'none logged')
        print('Next music track:', music_next(wb))


if __name__ == '__main__':
    main()
