"""The posting calendar: one Short a day, between 16:00 and 22:00 local time (config.json "posting"). The owner uploads and
presses Schedule in YouTube Studio; this only plans the slot and reminds about the 24-hour and 7-day stat checks.
Usage: python -I calendar_plan.py next <slug> [--time 18:00] [--date YYYY-MM-DD] [--dry]   book the next free day
       python -I calendar_plan.py list                                                      the plan + stat checks that are due"""
import argparse, datetime as dt, os, sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import sfconfig  # noqa: E402
import tracker  # noqa: E402

P = sfconfig.CFG['posting']
hm = lambda s: dt.datetime.strptime(s, '%H:%M').time()


def when(r):
    try:
        return dt.datetime.combine(dt.date.fromisoformat(str(r['date'])[:10]), hm(str(r['time'] or '18:00')[:5]))
    except ValueError:
        return None


def next_slot(cal, t, start=None):
    busy = {str(r['date'])[:10] for r in cal if r['state'] in ('planned', 'posted')}
    now = dt.datetime.now(); d = start or now.date()
    if not start and now + dt.timedelta(hours=1) > dt.datetime.combine(d, t):
        d += dt.timedelta(days=1)                            # too late to schedule today: tomorrow
    while d.isoformat() in busy:
        d += dt.timedelta(days=1)
    return d


def main():
    ap = argparse.ArgumentParser(); sp = ap.add_subparsers(dest='cmd', required=True)
    p = sp.add_parser('next'); p.add_argument('slug'); p.add_argument('--time', default='18:00'); p.add_argument('--date'); p.add_argument('--dry', action='store_true')
    sp.add_parser('list')
    a = ap.parse_args(); wb = tracker.book(); cal = tracker.rows(wb['Posting calendar'])
    if a.cmd == 'next':
        t = hm(a.time)
        if not hm(P['window_start']) <= t <= hm(P['window_end']):
            sys.exit(f'{a.time} is outside the posting window {P["window_start"]}-{P["window_end"]}')
        mine = [r for r in cal if r['episode'] == a.slug and r['state'] in ('planned', 'posted')]
        if mine and not a.date:
            print(f'{a.slug} already has a slot: {mine[0]["date"]} {mine[0]["time"]} ({mine[0]["state"]})'); return
        d = dt.date.fromisoformat(a.date) if a.date else next_slot(cal, t)
        slot = dt.datetime.combine(d, t)
        print(f'slot for {a.slug}: {slot:%A %d %B %Y, %H:%M} (local time) on {", ".join(P["platforms"])}')
        print(f'  stats check 1: {slot + dt.timedelta(hours=24):%a %d %b %H:%M}   stats check 2: {slot + dt.timedelta(days=7):%a %d %b %H:%M}')
        if not a.dry:
            for pf in P['platforms']:
                tracker.upsert(wb['Posting calendar'], ['date', 'episode', 'platform'],
                               {'date': d.isoformat(), 'time': a.time, 'episode': a.slug, 'platform': pf, 'state': 'planned'})
            tracker.save(wb); print('  booked in the tracker (Posting calendar)')
        return
    now = dt.datetime.now(); perf = tracker.rows(wb['Performance'])
    latest = {}                                              # a later check (48 h) also covers an earlier one (24 h)
    for r in perf:
        latest[r['episode']] = max(latest.get(r['episode'], 0), float(r['hours after post'] or 0))
    seen = set()
    for r in sorted(cal, key=lambda r: (str(r['date']), str(r['time']))):
        k = (r['episode'], str(r['date'])[:10])
        if k in seen:
            continue
        seen.add(k); w = when(r)
        pfs = sorted({x['platform'] for x in cal if (x['episode'], str(x['date'])[:10]) == k})
        print(f'{str(r["date"])[:10]} {str(r["time"] or "--:--")[:5]}  {r["episode"]:<22} {r["state"]:<8} {", ".join(pfs)}')
        if w and r['state'] == 'posted':
            for h in (24, 168):
                if now >= w + dt.timedelta(hours=h) and latest.get(r['episode'], 0) < h:
                    print(f'      DUE: {h} h stats ({"1 day" if h == 24 else "7 days"} after posting)')
    ready = [e for e in tracker.rows(wb['Episodes']) if e['status'] not in ('posted', 'idea') and e['slug'] not in {c['episode'] for c in cal}]
    for e in ready:
        print(f'no slot yet: {e["slug"]} (status {e["status"]})')


if __name__ == '__main__':
    main()
