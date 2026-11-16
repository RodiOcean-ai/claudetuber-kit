"""Rank the saved month of course/masterclass videos (from top_titles.py) without asking YouTube again. 15 Nov 2026.
  py -3.13 -P -X utf8 rank_titles.py <out_dir> [--month 2026-10] [--src all_run1.json]
Fixes from the first run: a channel's subscriber count is sometimes read in a local number format (12 million -> "12"),
so each channel takes the LARGEST count seen on any of its videos, and a count under 2,000 on a 100K+ view video is
treated as unknown (left out). Topic and language filters as in top_titles.relevant(), plus transliterated Hindi, French,
exam-form and meditation titles. Writes top50.md, top50.json, grid16.jpg (top 16 thumbnails, numbered, 4 x 4)."""
import argparse, calendar, json, os, re, sys, urllib.request

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import top_titles as T  # noqa: E402

MORE_OFF = re.compile(r'kaise|banaye|banana|sikh|\bkare\b|\bse video\b|apply online|form fill|police|bpsc|\bbatch\b|'
                      r'meditation|\bserial\b|meesho|comment faire|complet\b|\bdu\b|\bpour\b|\bmit\b|\bund\b|\bfür\b|odia|'
                      r'tre \d|students🔥', re.I)


def fmt(n):
    return f'{n / 1e6:.1f}M' if n >= 1e6 else f'{n / 1e3:.0f}K'


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('out'); ap.add_argument('--month', default='2026-10'); ap.add_argument('--src', default='all_run1.json')
    a = ap.parse_args()
    y, m = map(int, a.month.split('-'))
    rows = json.load(open(os.path.join(a.out, a.src), encoding='utf-8'))
    best_subs = {}
    for r in rows:
        s = r.get('channel_follower_count') or 0
        best_subs[r['channel_id']] = max(best_subs.get(r['channel_id'], 0), s)
    keep, unknown = [], []
    for r in rows:
        s = best_subs.get(r['channel_id'], 0)
        if not T.relevant(r) or MORE_OFF.search(r['title']):
            continue
        if s < 2000:
            unknown.append(r); continue
        r['subs'] = s
        r['score'] = round(r['view_count'] / s, 2)
        keep.append(r)
    best = sorted(keep, key=lambda r: -r['score'])[:50]
    json.dump(best, open(os.path.join(a.out, 'top50.json'), 'w', encoding='utf-8'), indent=1, ensure_ascii=False)
    with open(os.path.join(a.out, 'top50.md'), 'w', encoding='utf-8') as f:
        f.write(f'# The 50 most viral course / masterclass videos of {calendar.month_name[m]} {y}\n\n'
                f'English teaching videos on AI, tech, creators, business and online income, 8+ minutes, 100K+ views, from 70 '
                f'YouTube searches (sorted by views, {calendar.month_name[m]} uploads only). **Viral = views / the channel\'s '
                f'subscribers** (1x = as many views as subscribers). {len(keep)} qualified; {len(unknown)} left out because '
                f'YouTube gave no usable channel size.\n\n| # | Title | Views | Channel subs | Viral | Length | Channel |\n|---|---|---|---|---|---|---|\n')
        for i, r in enumerate(best, 1):
            d = r['duration'] or 0
            ln = f'{d // 3600}h {d % 3600 // 60:02d}m' if d >= 3600 else f'{d // 60} min'
            f.write(f"| {i} | [{r['title'].replace('|', '/')}]({r['webpage_url']}) | {fmt(r['view_count'])} | {fmt(r['subs'])} | "
                    f"{r['score']}x | {ln} | {r['channel'].replace('|', '/')} |\n")
        if unknown:
            f.write('\n**Left out (channel size unreadable):** ' + '; '.join(f"{r['title']} ({fmt(r['view_count'])})" for r in unknown) + '\n')
    print(f'{len(keep)} ranked, {len(unknown)} unknown size; top50.md written', flush=True)
    from PIL import Image, ImageDraw, ImageFont
    tdir = os.path.join(a.out, 'thumbs'); os.makedirs(tdir, exist_ok=True)
    W, H, G = 480, 270, 12
    grid = Image.new('RGB', (4 * W + 5 * G, 4 * H + 5 * G), (15, 15, 15))
    font = ImageFont.truetype('C:/Windows/Fonts/arialbd.ttf', 34)
    for i, r in enumerate(best[:16]):
        p = os.path.join(tdir, f"{i + 1:02d}_{r['id']}.jpg")
        if not os.path.exists(p):
            for name in ('maxresdefault', 'hq720', 'sddefault', 'hqdefault'):
                try:
                    req = urllib.request.Request(f"https://i.ytimg.com/vi/{r['id']}/{name}.jpg", headers={'User-Agent': 'thumb-study'})
                    data = urllib.request.urlopen(req, timeout=30).read()
                    if len(data) > 3000:
                        open(p, 'wb').write(data); break
                except Exception:  # noqa: BLE001
                    continue
        if not os.path.exists(p):
            print('no thumbnail for', r['id']); continue
        im = Image.open(p).convert('RGB')
        sw, sh = im.size
        th = sw * 9 // 16
        im = im.crop((0, (sh - th) // 2, sw, (sh - th) // 2 + th)).resize((W, H), Image.LANCZOS)
        x, y0 = G + (i % 4) * (W + G), G + (i // 4) * (H + G)
        grid.paste(im, (x, y0))
        dr = ImageDraw.Draw(grid)
        dr.rounded_rectangle((x + 8, y0 + 8, x + 64, y0 + 52), 8, fill=(242, 35, 26))
        dr.text((x + 36, y0 + 30), str(i + 1), font=font, fill=(255, 255, 255), anchor='mm')
    grid.save(os.path.join(a.out, 'grid16.jpg'), quality=90)
    print('grid16.jpg written', flush=True)


if __name__ == '__main__':
    main()
