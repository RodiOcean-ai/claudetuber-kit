"""Check a narration script for the things that make text sound AI-written (story-scripts, stage 5).
Usage: python -I script_check.py <script.txt> [--json]
Flags: even sentence rhythm, too few short sentences, repeated openers, stock phrases, "and then" chains, tidy triples,
em dashes. Bracketed edit notes [like this] are ignored. Targets come from the faceless-channel study's scripts (29 Oct 2026)."""
import json, re, statistics, sys

sys.stdout.reconfigure(encoding='utf-8')
STOCK = ["let's dive in", 'dive into', 'deep dive', 'game-changer', 'game changer', 'unlock', 'unleash', "in today's", 'fast-paced',
         'ever-evolving', 'in the world of', "whether you're", 'look no further', 'the power of', 'at the end of the day', 'elevate',
         'seamless', 'navigate the', 'embark', 'journey of', 'tapestry', 'testament to', 'in conclusion', 'moreover', 'furthermore',
         'additionally', "it's important to note", 'not only', 'but also', 'when it comes to', 'a world where', 'buckle up',
         "can't get out of your head", 'like never before', 'take it to the next level', 'without further ado', 'stay tuned',
         'harness', 'delve', 'crucial', 'pivotal', 'realm', 'landscape', 'robust', 'myriad', 'plethora', 'boasts']
text = open(sys.argv[1], encoding='utf-8-sig').read()
body = re.sub(r'\[[^\]]*\]', ' ', text)                     # edit notes and voice tags
body = re.sub(r'\s+', ' ', body).strip()
sents = [s.strip() for s in re.split(r'(?<=[.!?…])\s+', body) if re.search(r'[A-Za-z]', s)]
lens = [len(s.split()) for s in sents]
words = len(body.split())
low = body.lower()
openers = {}
for s in sents:
    o = ' '.join(s.lower().split()[:2])
    openers[o] = openers.get(o, 0) + 1
rep = {k: v for k, v in openers.items() if v >= 3}
stock = sorted({p for p in STOCK if p in low})
triples = re.findall(r'\b\w+(?: \w+)?, \w+(?: \w+)?,? and \w+', body)
res = {
    'words': words, 'sentences': len(sents),
    'mean_sentence_words': round(statistics.mean(lens), 1) if lens else 0,
    'sentence_length_spread': round(statistics.pstdev(lens), 1) if len(lens) > 1 else 0,
    'short_sentences_per_100_words': round(sum(l <= 3 for l in lens) / max(words, 1) * 100, 2),
    'longest_sentence': max(lens) if lens else 0,
    'and_then': len(re.findall(r'\band then\b', low)),
    'but_therefore_turns_per_100_words': round(len(re.findall(r'\b(but|so|therefore|which means|that\'s why|until)\b', low)) / max(words, 1) * 100, 1),
    'questions_per_100_words': round(body.count('?') / max(words, 1) * 100, 2),
    'em_dashes': body.count('—') + body.count(' - '),
    'repeated_openers': rep, 'stock_phrases': stock, 'triples': triples[:10],
}
flags = []
if res['sentence_length_spread'] < 6: flags.append('Rhythm too even: mix in very short and very long sentences (spread under 6 words; studied scripts 6.5-7.3).')
if res['short_sentences_per_100_words'] < 1: flags.append('Too few short punches: add a fragment or a 1-3 word sentence about every 100 words.')
if res['and_then']: flags.append(f'"and then" x{res["and_then"]}: rewrite as "but" (a turn) or "so/therefore" (a consequence).')
if rep: flags.append(f'Repeated sentence openers: {rep}.')
if stock: flags.append(f'Stock/AI phrases: {stock}.')
if len(triples) > max(1, words // 400): flags.append(f'Too many tidy triples ({len(triples)}): break some into two or four items.')
if res['em_dashes']: flags.append('Em dashes: replace with a full stop or "..." (the voice reads them oddly and detectors flag them).')
if res['questions_per_100_words'] < 0.5 and words > 150: flags.append('Almost no questions to the viewer: add one that makes them think.')
res['flags'] = flags
if '--json' in sys.argv:
    print(json.dumps(res, ensure_ascii=False, indent=1))
else:
    for k, v in res.items():
        if k != 'flags': print(f'{k}: {v}')
    print('\nFLAGS:' if flags else '\nNo flags. Reads human.')
    for f in flags: print(' -', f)
