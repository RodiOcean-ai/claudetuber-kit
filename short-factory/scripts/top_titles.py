"""The most viral course / masterclass videos of one month on YouTube (free: yt-dlp searches, no credits). 15 Nov 2026.
Owner: "give me the top 50 most viral master class titles from October and we check it together" + "top 16 thumbnails 4x4".
  py -3.13 -P -X utf8 top_titles.py <out_dir> [--month 2026-10] [--per 40] [--min-views 100000]
1) Each search line + YouTube's own date range (after:/before:), sorted by views, videos only.
2) Keep teaching videos: a course word in the title (masterclass, course, tutorial, guide...), 8+ minutes, Latin script,
   no sports/trailer/podcast-clip words.
3) Full details for the strongest candidates (upload date, channel subscribers), keep the month only.
4) Viral score = views / channel subscribers (how far the video beat its own audience). Top 50 by score (min views).
Writes top50.md, top50.json, all.json and grid16.jpg (the top 16 thumbnails, numbered, 4 x 4).
Checks added after the first run: the ORIGINAL title (search shows titles auto-translated), language, YouTube category,
subscribers from the channel page when the video page has none, and our audience's topics only (AI, tech, creators,
business, online income); --reuse skips the searches and re-checks all.json."""
import argparse, calendar, json, os, re, subprocess, sys, time, urllib.parse, urllib.request
from concurrent.futures import ThreadPoolExecutor

TOPICS = ['AI', 'ChatGPT', 'Claude', 'Claude Code', 'AI agents', 'n8n', 'vibe coding', 'YouTube', 'faceless YouTube',
          'YouTube automation', 'content creation', 'video editing', 'AI video', 'AI animation', 'Canva', 'marketing',
          'sales', 'business', 'make money online', 'personal brand', 'copywriting', 'Excel', 'coding', 'Blender',
          'Instagram', 'TikTok', 'prompt engineering', 'Gemini', 'productivity', 'Notion']
GENERIC = ['masterclass', 'full course', 'complete course', 'crash course', 'full tutorial for beginners',
           'step by step guide', 'everything you need to know', 'ultimate guide', 'free course', 'full workflow']
COURSE = re.compile(r'master\s?class|course|tutorial|guide|class\b|lesson|how to|learn|beginner|step[- ]by[- ]step|bootcamp|'
                    r'workshop|training|full workflow|a to z|from scratch|zero to|explained|blueprint|playbook', re.I)
NOISE = re.compile(r'\bvs\.?\b|highlights|full fight|trailer|\bgoal|match\b|\bnba\b|\bnfl\b|\bufc\b|football|soccer|'
                   r'cricket|boxing|episode|reaction|live stream|livestream|music video|official video|lyrics|sermon|church|'
                   r'prayer|retreat', re.I)


def run(args, timeout=180):
    try:
        r = subprocess.run([sys.executable, '-m', 'yt_dlp', '--no-warnings'] + args, capture_output=True, text=True,
                           encoding='utf-8', errors='replace', timeout=timeout)
        return r.stdout if r.returncode == 0 else ''
    except subprocess.TimeoutExpired:
        return ''


def search(q, a, b, per):
    url = 'https://www.youtube.com/results?search_query=' + urllib.parse.quote_plus(f'{q} after:{a} before:{b}') + '&sp=CAMSAhAB'
    out = run(['--flat-playlist', '-J', '--playlist-end', str(per), url])
    time.sleep(1.2)                                   # gentle: YouTube answers 429 when pushed
    try:
        return [e for e in json.loads(out).get('entries', []) if e]
    except ValueError:
        return []


def details(vid):
    out = run(['-J', '--skip-download', f'https://www.youtube.com/watch?v={vid}'], timeout=90)
    try:
        d = json.loads(out)
    except ValueError:
        return None
    return {k: d.get(k) for k in ('id', 'title', 'upload_date', 'view_count', 'like_count', 'comment_count', 'duration',
                                  'channel', 'channel_id', 'channel_follower_count', 'webpage_url', 'language', 'categories')}


def subs_of(cid):
    out = run(['--flat-playlist', '-J', '--playlist-end', '1', f'https://www.youtube.com/channel/{cid}'], timeout=90)
    try:
        return json.loads(out).get('channel_follower_count')
    except ValueError:
        return None


TOPIC = re.compile(r'\bai\b|claude|chatgpt|gpt|gemini|grok|opus|fable|llm|agent|automat|n8n|prompt|youtube|faceless|'
                   r'content|creator|clipping|video|edit|animat|motion|brand|marketing|sales|business|startup|money|income|'
                   r'freelanc|side hustle|entrepreneur|coding|code|python|excel|notion|productiv|design|canva|blender|'
                   r'figma|playbook|d2c|ecommerce|e-commerce|dropshipping|trad(e|ing)|invest|finance|wealth|career|'
                   r'communication|leadership|learn anything|websites to learn|course creator|online', re.I)
OFF = re.compile(r'makeup|hair|crochet|necklace|drawing|recipe|workout|gym|anime|guide you need for|pve|deadlock|gta|'
                 r'roblox game(?!.*ai)|class \d|chapter \d|one shot|telugu|tamil|hindi|urdu|bangla|kannada|malayalam|'
                 r'marathi|glow up|parliament|spoiler', re.I)
OK_CAT = {'Education', 'Science & Technology', 'People & Blogs', 'Howto & Style', 'Film & Animation', 'Entertainment'}


def relevant(r):
    t = r.get('title') or ''
    cats = set(r.get('categories') or [])
    lang = (r.get('language') or 'en').lower()
    return (latin(t) and lang.startswith('en') and COURSE.search(t) and not NOISE.search(t) and not OFF.search(t)
            and (not cats or cats & OK_CAT) and (TOPIC.search(t) or 'Science & Technology' in cats))


def latin(t):
    letters = [c for c in t if c.isalpha()]
    return letters and sum(c.isascii() for c in letters) / len(letters) > 0.9


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('out'); ap.add_argument('--month', default='2026-10'); ap.add_argument('--per', type=int, default=40)
    ap.add_argument('--min-views', type=int, default=100000); ap.add_argument('--detail-max', type=int, default=320)
    ap.add_argument('--reuse', action='store_true')
    a = ap.parse_args()
    os.makedirs(a.out, exist_ok=True)
    y, m = map(int, a.month.split('-'))
    last = calendar.monthrange(y, m)[1]
    after = f'{y}-{m - 1:02d}-{calendar.monthrange(y, m - 1)[1]:02d}' if m > 1 else f'{y - 1}-12-31'
    before = f'{y + (m == 12)}-{(m % 12) + 1:02d}-01'
    lines = GENERIC + [f'{t} masterclass' for t in TOPICS] + [f'{t} full course' for t in TOPICS]
    cand = {}
    if a.reuse:
        for r in json.load(open(os.path.join(a.out, 'all.json'), encoding='utf-8')):
            cand[r['id']] = {'id': r['id'], 'title': r['title'], 'views_search': r.get('view_count') or 0,
                             'duration': r.get('duration') or 0, 'queries': r.get('queries', [])}
        lines_run = []
    else:
        lines_run = lines
    for i, q in enumerate(lines_run, 1):
        got = search(q, after, before, a.per)
        keep = 0
        for e in got:
            t, d, v = e.get('title') or '', e.get('duration') or 0, e.get('view_count') or 0
            if d < 480 or v < a.min_views or not latin(t) or not COURSE.search(t) or NOISE.search(t):
                continue
            keep += 1
            c = cand.setdefault(e['id'], {'id': e['id'], 'title': t, 'views_search': v, 'duration': d, 'queries': []})
            c['queries'].append(q)
        print(f'[{i}/{len(lines)}] {q}: {len(got)} results, {keep} kept, {len(cand)} candidates', flush=True)
    top = sorted(cand.values(), key=lambda c: -c['views_search'])[: a.detail_max]
    print(f'details for {len(top)} candidates...', flush=True)
    with ThreadPoolExecutor(4) as ex:
        rows = [r for r in ex.map(lambda c: details(c['id']), top) if r]
    for r in rows:
        r['queries'] = cand[r['id']]['queries']
    month = [r for r in rows if (r.get('upload_date') or '').startswith(f'{y}{m:02d}') and (r.get('view_count') or 0) >= a.min_views]
    need = sorted({r['channel_id'] for r in month if not r.get('channel_follower_count') and r.get('channel_id')})
    print(f'subscribers from {len(need)} channel pages...', flush=True)
    with ThreadPoolExecutor(4) as ex:
        got = dict(zip(need, ex.map(subs_of, need)))
    for r in month:
        if not r.get('channel_follower_count'):
            r['channel_follower_count'] = got.get(r.get('channel_id'))
    json.dump(month, open(os.path.join(a.out, 'all.json'), 'w', encoding='utf-8'), indent=1, ensure_ascii=False)
    month = [r for r in month if r.get('channel_follower_count') and relevant(r)]
    for r in month:
        r['score'] = round((r['view_count'] or 0) / max(r['channel_follower_count'], 1000), 2)
    print(f'{len(month)} on our topics with known channel size', flush=True)
    best = sorted(month, key=lambda r: -r['score'])[:50]
    json.dump(best, open(os.path.join(a.out, 'top50.json'), 'w', encoding='utf-8'), indent=1, ensure_ascii=False)
    fmt = lambda n: f'{n / 1e6:.1f}M' if n >= 1e6 else f'{n / 1e3:.0f}K'
    with open(os.path.join(a.out, 'top50.md'), 'w', encoding='utf-8') as f:
        f.write(f'# Most viral course / masterclass videos, {calendar.month_name[m]} {y}\n\n'
                f'Viral score = views / channel subscribers. {len(month)} English teaching videos on AI, tech, creators, '
                f'business and online income, from {len(lines)} searches; only videos with {fmt(a.min_views)}+ views.\n\n| # | Title | Views | Subs | Score | Length | Date | Channel |\n|---|---|---|---|---|---|---|---|\n')
        for i, r in enumerate(best, 1):
            d = r['duration'] or 0
            f.write(f"| {i} | [{r['title']}]({r['webpage_url']}) | {fmt(r['view_count'])} | {fmt(r.get('channel_follower_count') or 0)} | "
                    f"{r['score']}x | {d // 3600}:{d % 3600 // 60:02d}:{d % 60:02d} | {r['upload_date'][6:]} {calendar.month_abbr[m]} | {r['channel']} |\n")
    print(f'{len(month)} from {calendar.month_name[m]}; top50.md written', flush=True)
    # the top 16 thumbnails, numbered, 4 x 4
    from PIL import Image, ImageDraw, ImageFont
    tdir = os.path.join(a.out, 'thumbs'); os.makedirs(tdir, exist_ok=True)
    W, H = 480, 270
    grid = Image.new('RGB', (4 * W + 5 * 12, 4 * H + 5 * 12), (15, 15, 15))
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
            continue
        im = Image.open(p).convert('RGB')
        sw, sh = im.size                              # crop to 16:9 (the sd/hq versions have black bars)
        th = sw * 9 // 16
        im = im.crop((0, (sh - th) // 2, sw, (sh - th) // 2 + th)).resize((W, H), Image.LANCZOS)
        x, y0 = 12 + (i % 4) * (W + 12), 12 + (i // 4) * (H + 12)
        grid.paste(im, (x, y0))
        dr = ImageDraw.Draw(grid)
        dr.rounded_rectangle((x + 8, y0 + 8, x + 64, y0 + 52), 8, fill=(242, 35, 26))
        dr.text((x + 36, y0 + 30), str(i + 1), font=font, fill=(255, 255, 255), anchor='mm')
    grid.save(os.path.join(a.out, 'grid16.jpg'), quality=90)
    print('grid16.jpg written', flush=True)


if __name__ == '__main__':
    main()
