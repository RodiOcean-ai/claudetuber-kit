"""Pick this episode's music bed from the 3-track rotation and place it so its final hit lands on the last word.
Usage: python -I music_pick.py <episode_dir> [--track sprint|clocks|steps] [--word N] [--dry] [--no-tracker]
Reads edit/src/words.json (the voice word times). Frame one lands on a beat of the track (MUSIC_IN is a beat time), so the
loop restarts in rhythm. Writes edit/src/music.json {track, file, music_in, hit_at}, copies the wav into edit/public/audio/music.wav
and records the choice in the tracker's Music rotation sheet (unless --dry)."""
import argparse, datetime as dt, json, os, shutil, sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import sfconfig  # noqa: E402


def place(meta, words, word=None):
    w = words[word if word is not None else -1]
    end = words[-1]['e'] + 0.5
    target = w['s'] + 0.38                                  # just after the last word starts: the hit punctuates it
    best = None
    for b in meta['beats_s']:
        h = meta['final_hit_s'] - b                         # where the hit lands in the video if the track starts at beat b
        if w['s'] <= h <= end - 0.25 and b >= 0:
            if best is None or abs(h - target) < abs(best[1] - target):
                best = (b, h)
    if best is None:                                        # no beat fits: start exactly so the hit lands on target
        best = (max(0.0, meta['final_hit_s'] - target), target)
    return round(best[0], 3), round(best[1], 3)


def main():
    ap = argparse.ArgumentParser(); ap.add_argument('episode'); ap.add_argument('--track'); ap.add_argument('--word', type=int)
    ap.add_argument('--dry', action='store_true'); ap.add_argument('--no-tracker', action='store_true')
    a = ap.parse_args()
    ep = os.path.abspath(a.episode); slug = os.path.basename(ep)
    words = json.load(open(os.path.join(ep, 'edit', 'src', 'words.json'), encoding='utf-8'))
    if not a.track:
        import tracker
        a.track = tracker.music_next()
    meta = json.load(open(os.path.join(sfconfig.ASSETS, 'music', a.track + '.json'), encoding='utf-8'))
    music_in, hit_at = place(meta, words, a.word)
    out = {'track': a.track, 'file': 'audio/music.wav', 'music_in': music_in, 'hit_at': hit_at, 'bpm': meta['bpm']}
    print(json.dumps(out))
    if a.dry:
        return
    json.dump(out, open(os.path.join(ep, 'edit', 'src', 'music.json'), 'w'), indent=1)
    shutil.copy(os.path.join(sfconfig.ASSETS, 'music', a.track + '.wav'), os.path.join(ep, 'edit', 'public', 'audio', 'music.wav'))
    if a.no_tracker:
        return
    import tracker
    wb = tracker.book(); wb['Music rotation'].append([dt.date.today().isoformat(), slug, a.track, music_in])
    tracker.upsert(wb['Episodes'], ['slug'], {'slug': slug, 'music': a.track}); tracker.save(wb)


if __name__ == '__main__':
    main()
