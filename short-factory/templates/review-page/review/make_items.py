"""Writes the review page's tabs from review/contract.json (free kit template). Only standard Python (3.9+).
  review/items.gen.tsx   what the page plays: imports each tab's component from the project's code
  review/items.json      the tab ids, for serve.py
  python review/make_items.py          (run again whenever the contract or the manifest changes)

review/contract.json (keys that start with "_" are comments and are ignored):
  title     name shown on the page                               fps      frames a second (default 30)
  width     default width of every tab (default 1920)            height   default height (default 1080)
  manifest  optional: path (from the project folder) of the manifest with chapters, words and music; see
            make_timeline.py. Needed for "frames": "total" and for "chapter".
  items     one entry per tab, in the order of the tabs:
    id        short id without spaces (best: the composition id in Root.tsx); notes and approvals are filed under it
    name      what the tab says
    module    the file that exports the component, from the project folder, without .tsx (e.g. "src/Intro")
    export    the component's export name (or "default")
    props     optional: input props for the component, e.g. {"id": "ch01"}
    frames    its length in frames, or "total" (the manifest's whole length); not needed with "chapter"
    chapter   optional: a chapter id in the manifest; the tab gets that chapter's length and its stretch of the timeline
    start     optional: where the tab's frame 0 sits on the timeline (default: the chapter's start, else 0)
    width, height   optional: this tab's own size (a cover 1280x720, an upright Short 1080x1920)
    mark      optional: the short text in the tab's circle (default: its number)
    timeline  optional: false hides the timeline (default: shown for anything longer than one frame)
    music     optional: false greys out the music track (this tab plays without the music)"""
import datetime, json, os, re, sys

RV = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(RV)
EXTS = ['.tsx', '.ts', '.jsx', '.js']


def fail(msg):
    sys.exit(f'make_items: {msg}')


def strip(d):
    """drop "_comment" keys at every level"""
    if isinstance(d, dict):
        return {k: strip(v) for k, v in d.items() if not k.startswith('_')}
    if isinstance(d, list):
        return [strip(v) for v in d]
    return d


def load_json(p, what):
    try:
        return strip(json.load(open(p, encoding='utf-8')))
    except FileNotFoundError:
        fail(f'{what} not found: {p}')
    except ValueError as e:
        fail(f'{what} is not valid JSON ({p}): {e}')


def module_file(mod):
    base = os.path.join(ROOT, mod)
    for cand in [base] + [base + e for e in EXTS] + [os.path.join(base, 'index' + e) for e in EXTS]:
        if os.path.isfile(cand):
            return cand
    return None


def has_export(path, name):
    src = open(path, encoding='utf-8', errors='replace').read()
    if name == 'default':
        return re.search(r'export\s+default\b', src) is not None
    if re.search(rf'export\s+(const|let|var|function|class)\s+{re.escape(name)}\b', src):
        return True
    for block in re.findall(r'export\s*\{([^}]*)\}', src):     # export { A, B as C }
        for part in block.split(','):
            bits = part.strip().split()
            if bits and bits[-1] == name:
                return True
    return re.search(r'export\s*\*\s*from', src) is not None    # re-exports: cannot tell, assume yes


def main():
    cp = os.path.join(RV, 'contract.json')
    if not os.path.exists(cp):
        fail('review/contract.json is missing: copy review/contract.example.json to review/contract.json and fill it in')
    c = load_json(cp, 'the contract')
    fps = int(c.get('fps') or 30)
    W, H = int(c.get('width') or 1920), int(c.get('height') or 1080)
    man = None
    if c.get('manifest'):
        man = load_json(os.path.join(ROOT, c['manifest']), 'the manifest')
    chapters = {ch['id']: ch for ch in (man or {}).get('chapters', [])}
    total = (man or {}).get('total') or (max((ch['start'] + ch['frames'] for ch in chapters.values()), default=0))
    items = c.get('items') or []
    if not items:
        fail('the contract has no items (one per tab)')

    imports, comps, rows, seen = {}, [], [], set()
    for i, it in enumerate(items, 1):
        iid = str(it.get('id') or '')
        if not re.fullmatch(r'[A-Za-z0-9][A-Za-z0-9._-]*', iid):
            fail(f'item {i}: "id" must be letters, digits, dots, dashes or underscores (got {iid!r})')
        if iid in seen:
            fail(f'two items have the id {iid!r}')
        seen.add(iid)
        mod, exp = it.get('module'), it.get('export')
        if not mod or not exp:
            fail(f'{iid}: needs "module" (the file, e.g. "src/Intro") and "export" (the component name)')
        mod = mod.replace('\\', '/')
        mod = re.sub(r'\.(tsx|ts|jsx|js)$', '', mod)
        path = module_file(mod)
        if not path:
            fail(f'{iid}: no file for module {mod!r} (looked for {mod}.tsx/.ts/.jsx/.js and {mod}/index.*)')
        if not has_export(path, exp):
            print(f'warning: {iid}: {os.path.relpath(path, ROOT)} does not seem to export {exp!r}', file=sys.stderr)
        ch = it.get('chapter')
        if ch is not None and ch not in chapters:
            fail(f'{iid}: chapter {ch!r} is not in the manifest' if man else f'{iid}: "chapter" needs a manifest in the contract')
        frames = it.get('frames')
        if frames == 'total':
            if not total:
                fail(f'{iid}: "frames": "total" needs a manifest with chapters or a "total"')
            frames = total
        if frames is None and ch is not None:
            frames = chapters[ch]['frames']
        if not isinstance(frames, int) or frames < 1:
            fail(f'{iid}: "frames" must be a whole number of frames (or "total", or give a "chapter")')
        start = it.get('start', chapters[ch]['start'] if ch is not None else 0)
        key = (mod, exp)
        if key not in imports:
            imports[key] = f'C{len(imports)}'
        comp = imports[key]
        if it.get('props'):
            comps.append(f'const P{i} = {json.dumps(it["props"], ensure_ascii=False)};')
            comp_expr = f'(() => <{comp} {{...P{i}}} />)'
        else:
            comp_expr = comp
        w, h = int(it.get('width') or W), int(it.get('height') or H)
        row = {'id': iid, 'n': str(it.get('mark', i)), 'name': str(it.get('name') or iid), 'frames': frames, 'w': w, 'h': h,
               'start': int(start), 'chapter': ch, 'timeline': bool(it.get('timeline', frames > 1)),
               'music': bool(it.get('music', True))}
        fields = ', '.join(f'{k}: {json.dumps(v, ensure_ascii=False)}' for k, v in row.items())
        rows.append(f'  {{ {fields}, comp: {comp_expr} }},')

    lines = [f'// Written by review/make_items.py from review/contract.json on {datetime.date.today()}.',
             '// Do not edit by hand: change the contract and run  python review/make_items.py  again.',
             "import React from 'react';"]
    for (mod, exp), name in imports.items():
        rel = '../' + mod
        lines.append(f"import {name} from '{rel}';" if exp == 'default' else f"import {{ {exp} as {name} }} from '{rel}';")
    lines += ['',
              f'export const TITLE = {json.dumps(str(c.get("title") or "Review"), ensure_ascii=False)};',
              f'export const FPS = {fps};',
              'export type ReviewItem = {',
              '  id: string; n: string; name: string; frames: number; w: number; h: number; start: number;',
              '  chapter: string | null; timeline: boolean; music: boolean;',
              '  // eslint-disable-next-line @typescript-eslint/no-explicit-any',
              '  comp: React.ComponentType<any>;',
              '};']
    lines += comps
    lines += ['export const ITEMS: ReviewItem[] = ['] + rows + ['];', '']
    open(os.path.join(RV, 'items.gen.tsx'), 'w', encoding='utf-8', newline='\n').write('\n'.join(lines))
    json.dump([it['id'] for it in items], open(os.path.join(RV, 'items.json'), 'w', encoding='utf-8'), ensure_ascii=False)
    print(f'items.gen.tsx and items.json: {len(items)} tabs, {len(imports)} components'
          + (f', manifest {len(chapters)} chapters, {total} frames' if man else ', no manifest'))


if __name__ == '__main__':
    main()
