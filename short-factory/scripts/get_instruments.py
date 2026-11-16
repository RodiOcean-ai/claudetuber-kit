"""Download the house instrument recordings (real instruments, note by note) for Claude-composed music.
Owner OK: 15 Nov 2026 ("Yes, download"), about 740 MB. Both collections are by Versilian Studios, licence CC0 (public
domain: free for any use, also a paid channel, no credit needed). Audio and text files only, nothing to install.
  py -3.13 -P -X utf8 get_instruments.py        (re-run safe: skips files that are already complete)
Lands in ../assets/house_sound/instruments/<collection>/<the collection's own folder path>."""
import json, os, sys, time, urllib.parse, urllib.request
from concurrent.futures import ThreadPoolExecutor

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.normpath(os.path.join(HERE, '..', 'assets', 'house_sound', 'instruments'))
REPOS = {
    'vsco2ce': ('sgossner/VSCO-2-CE', 'master', [
        'Keys/Upright Piano/', 'Strings/Violin Section/susVib/', 'Strings/Viola Section/susvib/',
        'Strings/Cello Section/susvib/', 'Strings/Violin Section/Pizz/', 'Strings/Cello Section/pizzT/',
        'Strings/Harp/', 'Woodwinds/Flute/susvib/', 'Brass/F Horn/sus/', 'Percussion/Glock/', 'Percussion/Marimba/',
        'LICENSE', 'Readme.txt', 'README.md']),
    'vcsl': ('sgossner/VCSL', 'master', [
        'Idiophones/Struck Idiophones/Vibraphone/', 'Idiophones/Plucked Idiophones/Kalimba, Kenya/',
        'Idiophones/Struck Idiophones/Shaker, Small/', 'LICENSE', 'README.md']),
}
OK_EXT = ('.wav', '.txt', '.md', '')          # audio and text only; anything else is skipped


def get(url, tries=4):
    for k in range(tries):
        try:
            req = urllib.request.Request(url, headers={'User-Agent': 'house-instruments-fetch'})
            with urllib.request.urlopen(req, timeout=120) as r:
                return r.read()
        except Exception as e:  # noqa: BLE001
            if k == tries - 1:
                raise
            time.sleep(2 + 3 * k)


jobs = []
for coll, (repo, branch, prefixes) in REPOS.items():
    tree = json.loads(get(f'https://api.github.com/repos/{repo}/git/trees/{branch}?recursive=1'))
    for t in tree['tree']:
        p = t['path']
        if t['type'] != 'blob' or not any(p == x or p.startswith(x) for x in prefixes):
            continue
        if os.path.splitext(p)[1].lower() not in OK_EXT:
            print('skip (not audio/text):', p); continue
        dst = os.path.join(OUT, coll, *p.split('/'))
        url = f'https://raw.githubusercontent.com/{repo}/{branch}/' + urllib.parse.quote(p)
        jobs.append((url, dst, t['size']))

total = sum(s for _, _, s in jobs)
print(f'{len(jobs)} files, {total / 1e6:.0f} MB -> {OUT}', flush=True)
done = [0, 0]


def fetch(job):
    url, dst, size = job
    if os.path.exists(dst) and os.path.getsize(dst) == size:
        done[0] += size; return None
    os.makedirs(os.path.dirname(dst), exist_ok=True)
    data = get(url)
    if len(data) != size:
        return f'size mismatch {dst}: {len(data)} != {size}'
    with open(dst + '.part', 'wb') as f:
        f.write(data)
    os.replace(dst + '.part', dst)
    done[0] += size; done[1] += 1
    if done[1] % 25 == 0:
        print(f'  {done[0] / 1e6:.0f} / {total / 1e6:.0f} MB', flush=True)
    return None


with ThreadPoolExecutor(8) as ex:
    errs = [e for e in ex.map(fetch, jobs) if e]
for e in errs:
    print('ERROR', e)
with open(os.path.join(OUT, 'SOURCES.md'), 'w', encoding='utf-8') as f:
    f.write('# House instruments (real instruments, recorded note by note)\n\nDownloaded 15 Nov 2026 with the owner\'s OK.\n'
            'Licence of both collections: CC0 1.0 (public domain). Free for any use, including a monetised channel; no credit needed.\n\n'
            '- vsco2ce/: Versilian Studios Chamber Orchestra 2, Community Edition (github.com/sgossner/VSCO-2-CE): upright piano, '
            'violin/viola/cello sections (held notes, plucked), harp, flute, French horn, glockenspiel, marimba.\n'
            '- vcsl/: Versilian Community Sample Library (github.com/sgossner/VCSL): vibraphone, kalimba (Kenya), small shaker.\n\n'
            'Played by short-factory/scripts/house_sampler.py (Claude\'s own note player; runs on the processor).\n')
print('DONE' if not errs else f'DONE with {len(errs)} errors', f'{done[0] / 1e6:.0f} MB')
