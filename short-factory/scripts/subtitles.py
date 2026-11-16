"""Subtitles file for every video (owner's rule, 10 Nov 2026): a timed .srt next to the final video, named the way
Facebook demands (name.[language]_[country].srt), which YouTube accepts too.
Usage: python -I subtitles.py <episode_dir> [--lang en_US] [--script script_LOCKED.txt] [--out <file.srt>]
Reads edit/src/words.json (else voice/final_voice.words.json): the final voice's word times. Spelling and capitals come from
the locked script where the words match; numbers stay as digits. One cue per sentence or clause, at most about 42 letters,
never overlapping. Writes post/<slug>.<lang>.srt. Upload it in YouTube Studio (Subtitles > Add language > Upload file >
With timing) and on Facebook (Captions > Upload)."""
import argparse, difflib, json, os, re

norm = lambda w: re.sub(r"[^a-z0-9']", '', w.lower())


def load_words(ep):
    for rel in (os.path.join('edit', 'src', 'words.json'), os.path.join('voice', 'final_voice.words.json')):
        p = os.path.join(ep, rel)
        if os.path.exists(p):
            return json.load(open(p, encoding='utf-8'))
    raise SystemExit('no word times found: run captions.py first')


def glue_numbers(words):
    """The voice-to-text splits numbers ("3" + ",000."): glue them back."""
    out = []
    for w in words:
        if out and re.match(r'^,\d', w['w']) and re.search(r'\d$', out[-1]['w']):
            out[-1] = {'w': out[-1]['w'] + w['w'], 's': out[-1]['s'], 'e': w['e']}
        else:
            out.append(dict(w))
    return out


def script_spelling(words, script):
    sw = script.split()
    a, b = [norm(w['w']) for w in words], [norm(x) for x in sw]
    for op, i1, i2, j1, j2 in difflib.SequenceMatcher(a=a, b=b, autojunk=False).get_opcodes():
        if op == 'equal':
            for k in range(i2 - i1):
                words[i1 + k]['w'] = sw[j1 + k]
    return words


JOINERS = {'and', 'or', 'but', 'so', 'because', 'that', 'which', 'when', 'if', 'then', 'while'}
length = lambda ws: len(' '.join(x['w'] for x in ws))


def split_long(ws, limit):
    """A clause longer than the limit is cut once near its middle, before a joining word when one is close."""
    if length(ws) <= limit or len(ws) < 4:
        return [ws]
    mid = length(ws) / 2
    best, score = None, None
    for i in range(2, len(ws) - 1):
        d = abs(length(ws[:i]) - mid) - (mid * 0.6 if norm(ws[i]['w']) in JOINERS else 0)
        if score is None or d < score:
            best, score = i, d
    return split_long(ws[:best], limit) + split_long(ws[best:], limit)


def cues(words, limit=50):
    out, cur = [], []
    for w in words:
        cur.append(w)
        if re.search(r'[.!?]$', w['w']) or (re.search(r',$', w['w']) and len(cur) >= 4):
            out += split_long(cur, limit)
            cur = []
    if cur:
        out += split_long(cur, limit)
    return out


def stamp(t):
    ms = int(round(t * 1000))
    return f'{ms // 3600000:02d}:{ms // 60000 % 60:02d}:{ms // 1000 % 60:02d},{ms % 1000:03d}'


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('episode'); ap.add_argument('--lang', default='en_US'); ap.add_argument('--script', default='script_LOCKED.txt'); ap.add_argument('--out')
    a = ap.parse_args()
    ep = os.path.abspath(a.episode)
    words = glue_numbers(load_words(ep))
    sp = os.path.join(ep, a.script)
    if os.path.exists(sp):
        words = script_spelling(words, open(sp, encoding='utf-8').read())
    cs = cues(words)
    lines = []
    for i, c in enumerate(cs):
        start = c[0]['s']
        nxt = cs[i + 1][0]['s'] if i + 1 < len(cs) else None
        end = max(c[-1]['e'] + 0.12, start + 0.7)
        if nxt is not None:
            end = min(end, nxt - 0.02)
        text = ' '.join(x['w'] for x in c)
        text = text[0].upper() + text[1:] if i == 0 or re.search(r'[.!?]$', cs[i - 1][-1]['w']) else text
        lines += [str(i + 1), f'{stamp(start)} --> {stamp(end)}', text, '']
    out = a.out or os.path.join(ep, 'post', f'{os.path.basename(ep)}.{a.lang}.srt')
    os.makedirs(os.path.dirname(out), exist_ok=True)
    open(out, 'w', encoding='utf-8').write('\n'.join(lines))
    print(f'{len(cs)} cues -> {out}')


if __name__ == '__main__':
    main()
