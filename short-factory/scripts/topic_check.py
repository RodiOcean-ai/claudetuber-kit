"""Check a topic or title idea against a studied channel's titles: did they already make it, and how did similar titles do?
Usage: python -I topic_check.py [--channel shorts-format] "Could You Survive Inside A Whale?" ["another idea" ...]
Titles come from reference/creators/<channel>/shorts.json (yt-dlp flat dump) or shorts.txt (id|views|title).
Prints the 5 most similar titles with their views and a verdict (TOO CLOSE = already made; pick another angle)."""
import json, os, re, sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import sfconfig  # noqa: E402

sys.stdout.reconfigure(encoding='utf-8')
args = sys.argv[1:]
CH = 'shorts-format'
if args and args[0] == '--channel':
    CH, args = args[1], args[2:]
D = os.path.join(sfconfig.REFERENCE, 'creators', CH)
E = []
if os.path.exists(os.path.join(D, 'shorts.json')):
    d = json.load(open(os.path.join(D, 'shorts.json'), encoding='utf-8-sig'))
    E = [{'title': x['title'], 'view_count': x['view_count']} for x in d['entries'] if x and x.get('view_count')]
elif os.path.exists(os.path.join(D, 'shorts.txt')):
    for ln in open(os.path.join(D, 'shorts.txt'), encoding='utf-8', errors='replace'):
        p = ln.rstrip('\n').split('|', 2)
        if len(p) == 3 and p[1].isdigit():
            E.append({'title': p[2], 'view_count': int(p[1])})
if not E:
    sys.exit(f'no titles found for {CH} in {D}')
STOP = set('a an the of to in on is are was were be do does did can could would will if what why how you your it its this that and or for with from at by into as i my me we he she they them his her their whats happens happen really'.split())


def words(t):
    return {w for w in re.findall(r"[a-z0-9']+", t.lower()) if w not in STOP and len(w) > 2}


print(f'checked against {len(E)} titles of {CH}')
for idea in args:
    iw = words(idea)
    scored = sorted(((len(iw & words(x['title'])) / max(1, len(iw)), x) for x in E), key=lambda s: (-s[0], -s[1]['view_count']))[:5]
    top = scored[0][0] if scored else 0
    verdict = ('TOO CLOSE - already made; change the angle' if top >= 0.75 else
               'LOOK CLOSELY - read the top match; if it is the same question, change the angle' if top >= 0.6 else
               'related videos exist - fine if the angle is new' if top >= 0.4 else 'fresh')
    print(f'\nIDEA: {idea}\n  verdict: {verdict}')
    for sc, x in scored:
        if sc > 0:
            print(f"  {sc:.0%}  {x['view_count'] / 1e6:6.1f}M  {x['title']}")
