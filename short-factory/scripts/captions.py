"""Caption data for the Remotion edit: word times corrected against the locked script, and 1-3 word phrase starts.
Usage: python -I captions.py <episode_dir> [--script script_LOCKED.txt] [--words voice/final_voice.words.json]
Writes edit/src/words.json (Whisper's timing, the script's spelling: e.g. "turn" -> "turned") and edit/src/captions.json
(the word numbers where each caption starts). Rules: a caption never crosses a comma or full stop, holds 1-3 words,
keeps a number with its unit ("13 billion views", "8 trick shots") and avoids a lone word unless the clause is one word."""
import argparse, difflib, json, os, re

NUM = re.compile(r"^\d[\d,.]*$|^(one|two|three|four|five|six|seven|eight|nine|ten|eleven|twelve|thirteen|twenty|thirty|hundred)$", re.I)
norm = lambda w: re.sub(r"[^a-z0-9']", '', w.lower())


def correct(words, script):
    sw = script.split()
    a, b = [norm(w['w']) for w in words], [norm(x) for x in sw]
    out = [dict(w) for w in words]
    for op, i1, i2, j1, j2 in difflib.SequenceMatcher(a=a, b=b, autojunk=False).get_opcodes():
        if op == 'replace' and (i2 - i1) == (j2 - j1):
            for k in range(i2 - i1):
                if re.match(r'^\d', a[i1 + k]):                 # keep Whisper's digits: captions show "13", the script says "thirteen"
                    continue
                tail = re.search(r'[,.!?]+$', out[i1 + k]['w'])
                out[i1 + k]['w'] = re.sub(r'[,.!?]+$', '', sw[j1 + k]) + (tail.group(0) if tail else re.search(r'[,.!?]*$', sw[j1 + k]).group(0))
    return out


def starts(words):
    clauses, cur = [], []
    for i, w in enumerate(words):
        cur.append(i)
        if re.search(r'[,.!?]$', w['w']):
            clauses.append(cur); cur = []
    if cur:
        clauses.append(cur)
    res = []
    for cl in clauses:                                        # best split of each clause into 1-3 word captions (cheapest total cost)
        n = len(cl); best = [0.0] + [1e9] * n; prev = [0] * (n + 1)
        for j in range(1, n + 1):
            for s in (1, 2, 3):
                if s <= j and best[j - s] + group_cost(words, cl[j - s:j], j == n, n) < best[j]:
                    best[j] = best[j - s] + group_cost(words, cl[j - s:j], j == n, n); prev[j] = j - s
        cuts, j = [], n
        while j > 0:
            cuts.append(prev[j]); j = prev[j]
        res += [cl[c] for c in reversed(cuts)]
    return res


WEAK = {'a', 'an', 'the', 'to', 'of', 'into', 'from', 'like', 'and', 'but', 'so', 'your', 'their', 'its', 'with', 'for', 'in', 'on', 'at',
        'as', 'if', 'where', 'that', 'over', 'my', 'our', 'his', 'her', 'this', 'these', 'those', 'by'}


def group_cost(words, g, clause_end, clause_len):
    """Each caption costs 1; a lone word, a caption ending on "a"/"from"/"your", or a number cut off from its unit costs more."""
    last = norm(words[g[-1]]['w']); c = 1.0 + (0.3 if len(g) == 3 else 0)
    if len(g) == 1 and clause_len > 1:
        c += 2.5
    if last in WEAK and not clause_end:
        c += 3
    if NUM.match(last) and not clause_end:                    # keep "13 billion views" and "8 trick shots" together
        c += 5
    return c


def main():
    ap = argparse.ArgumentParser(); ap.add_argument('episode'); ap.add_argument('--script', default='script_LOCKED.txt')
    ap.add_argument('--words', default=os.path.join('voice', 'final_voice.words.json'))
    a = ap.parse_args(); ep = os.path.abspath(a.episode)
    words = json.load(open(os.path.join(ep, a.words), encoding='utf-8'))
    sp = os.path.join(ep, a.script)
    if os.path.exists(sp):
        fixed = correct(words, open(sp, encoding='utf-8').read())
        for x, y in zip(words, fixed):
            if x['w'] != y['w']:
                print(f'  corrected "{x["w"]}" -> "{y["w"]}" at {x["s"]:.2f} s')
        words = fixed
    st = starts(words)
    os.makedirs(os.path.join(ep, 'edit', 'src'), exist_ok=True)
    json.dump(words, open(os.path.join(ep, 'edit', 'src', 'words.json'), 'w', encoding='utf-8'), indent=0, ensure_ascii=False)
    json.dump(st, open(os.path.join(ep, 'edit', 'src', 'captions.json'), 'w'))
    caps = [' '.join(w['w'] for w in words[s:(st[k + 1] if k + 1 < len(st) else len(words))]) for k, s in enumerate(st)]
    print(f'{len(st)} captions:', ' | '.join(caps))


if __name__ == '__main__':
    main()
