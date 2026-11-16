"""Measure every downloaded top video of a channel and record it, so nothing is analysed twice.
Usage: python -I study_channel.py <channel_key> [--skip-sounds] [--keep-media] [--only <id> ...]
Reads <study>/picks.json (written by download_channel.py). Per video: analyze.py (cuts, shot lengths, loudness, Demucs
voice/background split, Whisper words, hook/shot/timeline sheets), sounds.py (music share, sound effects), voice_style.py
(narration character) and a loop check (last frame vs first). Then: "<key> - all data.xlsx" (Top shorts, Top longs,
All titles, Title patterns, Averages), thumbs_sheet.jpg and hooks_sheet.jpg, tracker rows. Big media (mp4, mix.wav, stems)
is deleted afterwards unless --keep-media; the numbers, transcripts and frame sheets stay."""
import argparse, glob, json, os, re, shutil, statistics as st, subprocess, sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import sfconfig  # noqa: E402
import tracker  # noqa: E402

EMOJI = re.compile('[\U0001F300-\U0001FAFF☀-➿]')


def run(args):
    return subprocess.run(args, capture_output=True, text=True, encoding='utf-8', errors='replace')


def loop_score(mp4, dur):
    """Mean pixel difference (0-255) between the first and the last frame; under ~12 reads as a loop."""
    from PIL import Image, ImageChops, ImageStat
    tmp = []
    for k, t in enumerate((0.04, max(0.0, dur - 0.08))):
        f = os.path.join(os.path.dirname(mp4), f'_loop{k}.png')
        run(['ffmpeg', '-y', '-v', 'error', '-ss', str(t), '-i', mp4, '-frames:v', '1', '-vf', 'scale=180:-2', f]); tmp.append(f)
    try:
        a, b = (Image.open(x).convert('RGB') for x in tmp)
        return round(sum(ImageStat.Stat(ImageChops.difference(a, b)).mean) / 3, 1)
    except Exception:
        return None
    finally:
        for x in tmp:
            if os.path.exists(x):
                os.remove(x)


def video_row(channel, vid, kind, rank, title, views, adir, loop=None):
    """One tracker/workbook row from an analysis folder (metrics.json + sounds.json)."""
    m = json.load(open(os.path.join(adir, 'metrics.json'), encoding='utf-8'))
    s = json.load(open(os.path.join(adir, 'sounds.json'), encoding='utf-8')) if os.path.exists(os.path.join(adir, 'sounds.json')) else {}
    sp = m.get('speech', {})
    return {'channel': channel, 'id': vid, 'kind': kind, 'rank': rank, 'title': title, 'views': views, 'duration_s': m.get('duration_s'),
            'words': sp.get('word_count'), 'words_per_s': sp.get('words_per_sec'), 'cuts_per_min': m.get('cuts_per_min'),
            'avg_shot_s': m.get('avg_shot_s'), 'voice_minus_bg_lu': m.get('voice_minus_background_lu'), 'lufs': (m.get('mix') or {}).get('integrated_lufs'),
            'music_share': s.get('music_share'), 'sfx_per_min': s.get('sfx_per_min'), 'loop': loop, 'first_words': sp.get('words_in_first_3s')}


def title_stats(t):
    w = t.split()
    return {'opening': (w[0].lower().strip('"\'') if w else ''), 'question': '?' in t, 'emoji': bool(EMOJI.search(t)), 'words': len(w),
            'number': bool(re.search(r'\d', t)), 'caps_word': bool(re.search(r'\b[A-Z]{3,}\b', t))}


def sheet(paths, out, cols=5, w=320):
    from PIL import Image
    ims = [Image.open(p).convert('RGB') for p in paths if os.path.exists(p)]
    if not ims:
        return
    ims = [i.resize((w, int(i.height * w / i.width))) for i in ims]
    h = max(i.height for i in ims); rows = (len(ims) + cols - 1) // cols
    page = Image.new('RGB', (cols * w, rows * h), (16, 16, 16))
    for k, i in enumerate(ims):
        page.paste(i, ((k % cols) * w, (k // cols) * h))
    page.save(out, quality=88)


def workbook(key, study, recs, titles):
    from openpyxl import Workbook
    from openpyxl.styles import Font
    wb = Workbook(); ws = wb.active; ws.title = 'Read me'
    ws.append([f'{key}: measured top videos and all titles (short-factory study_channel.py)'])
    ws.append(['Numbers come from analyze.py / sounds.py; judgement notes live in the study notes and SECRET_SAUCE.md.'])
    cols = list(recs[0].keys()) if recs else []
    for kind in ('short', 'long'):
        sh = wb.create_sheet('Top shorts' if kind == 'short' else 'Top longs'); sh.append(cols)
        for r in [r for r in recs if r['kind'] == kind]:
            sh.append([r[c] for c in cols])
        sh['A1'].font = Font(bold=True)
    at = wb.create_sheet('All titles'); at.append(['kind', 'title', 'views', 'opening', 'question', 'emoji', 'words', 'number', 'CAPS word'])
    for t in titles:
        s = title_stats(t['title'])
        at.append([t['kind'], t['title'], t['views'], s['opening'], s['question'], s['emoji'], s['words'], s['number'], s['caps_word']])
    tp = wb.create_sheet('Title patterns'); tp.append(['kind', 'pattern', 'count', 'median views'])
    for kind in ('short', 'long'):
        T = [t for t in titles if t['kind'] == kind and t['views']]
        groups = {}
        for t in T:
            s = title_stats(t['title'])
            for k in (f'opens "{s["opening"]}"', 'has ?' if s['question'] else 'no ?', 'has emoji' if s['emoji'] else 'no emoji',
                      'has a number' if s['number'] else 'no number', f'{min(s["words"], 10)}{"+" if s["words"] >= 10 else ""} words'):
                groups.setdefault(k, []).append(t['views'])
        for k, v in sorted(groups.items(), key=lambda kv: -len(kv[1]))[:40]:
            tp.append([kind, k, len(v), int(st.median(v))])
    av = wb.create_sheet('Averages'); av.append(['kind', 'measure', 'median', 'min', 'max'])
    for kind in ('short', 'long'):
        R = [r for r in recs if r['kind'] == kind]
        for c in ('duration_s', 'words', 'words_per_s', 'cuts_per_min', 'avg_shot_s', 'voice_minus_bg_lu', 'lufs', 'music_share', 'sfx_per_min', 'loop'):
            v = [r[c] for r in R if isinstance(r.get(c), (int, float))]
            if v:
                av.append([kind, c, round(st.median(v), 2), round(min(v), 2), round(max(v), 2)])
    out = os.path.join(study, f'{key} - all data.xlsx'); wb.save(out); return out


def main():
    ap = argparse.ArgumentParser(); ap.add_argument('key'); ap.add_argument('--skip-sounds', action='store_true')
    ap.add_argument('--keep-media', action='store_true'); ap.add_argument('--only', nargs='*')
    a = ap.parse_args()
    a.key = sfconfig.safe_name(a.key.strip().lower().lstrip('@'), 'channel key')
    study = sfconfig.study_dir(a.key)
    picks = json.load(open(os.path.join(study, 'picks.json'), encoding='utf-8'))
    done = tracker.analysed_ids(a.key)
    py = sys.executable
    wb = tracker.book(); recs = []
    for p in picks['top']:
        vid = str(p['id'])
        if not sfconfig.VIDEO_ID.match(vid):                # ids become folder and file names
            print('skipped (not a video id):', repr(vid)); continue
        adir = os.path.join(study, 'analysis', vid); mp4 = os.path.join(study, 'videos', vid + '.mp4')
        if a.only and vid not in a.only:
            continue
        if vid in done and os.path.exists(os.path.join(adir, 'metrics.json')):
            print('skip (already analysed)', vid); recs.append(video_row(a.key, vid, p['kind'], p['rank'], p['title'], p['views'], adir)); continue
        if not os.path.exists(mp4):
            print('missing video, skipped:', vid); continue
        print(f'measuring {p["kind"]} #{p["rank"]}: {p["title"]}', flush=True)
        r = run([py, '-I', os.path.join(HERE, 'analyze.py'), study, vid])
        if r.returncode:
            print('analyze failed', vid, r.stderr[-400:]); continue
        if not a.skip_sounds:
            run([py, '-I', os.path.join(HERE, 'sounds.py'), study, vid])
        voc = os.path.join(adir, 'stems', 'htdemucs', vid, 'vocals.wav')
        if os.path.exists(voc):
            run([py, '-I', os.path.join(HERE, 'voice_style.py'), voc, os.path.join(adir, 'voice_style.json'), os.path.join(adir, 'transcript.json')])
        dur = json.load(open(os.path.join(adir, 'metrics.json'), encoding='utf-8'))['duration_s']
        rec = video_row(a.key, vid, p['kind'], p['rank'], p['title'], p['views'], adir, loop_score(mp4, dur))
        recs.append(rec); tracker.add_video(wb, rec); tracker.save(wb)
    titles = picks.get('all_titles', [])
    out = workbook(a.key, study, recs, titles) if recs else None
    sheet(sorted(glob.glob(os.path.join(study, 'videos', '*.jpg'))), os.path.join(study, 'thumbs_sheet.jpg'))
    sheet([os.path.join(study, 'analysis', p['id'], 'hook.jpg') for p in picks['top']], os.path.join(study, 'hooks_sheet.jpg'), cols=2, w=900)
    tracker.upsert(wb['Channels'], ['key'], {'key': a.key, 'handle': picks.get('handle'), 'study folder': study, 'subscribers': picks.get('subscribers'),
                                             'shorts': picks.get('n_shorts'), 'long videos': picks.get('n_longs'), 'studied on': tracker.today(), 'status': 'measured'})
    tracker.save(wb)
    if not a.keep_media:
        freed = 0
        for f in glob.glob(os.path.join(study, 'videos', '*.mp4')) + glob.glob(os.path.join(study, 'analysis', '*', 'mix.wav')):
            freed += os.path.getsize(f); os.remove(f)
        for d in glob.glob(os.path.join(study, 'analysis', '*', 'stems')):
            for root, _, fs in os.walk(d):
                freed += sum(os.path.getsize(os.path.join(root, x)) for x in fs)
            shutil.rmtree(d, ignore_errors=True)
        print(f'big media deleted: {freed / 1e9:.2f} GB freed')
    print('workbook:', out); print('measured', len(recs), 'videos')


if __name__ == '__main__':
    main()
