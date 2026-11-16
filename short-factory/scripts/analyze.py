"""Measure one downloaded video: cuts, loudness, voice vs background, speech, sound-effect hits, frames.
Usage: python -I analyze.py <study_dir> <video_id> [<video_path> <out_dir>]
Writes <study_dir>/analysis/<id>/ (or <out_dir>): metrics.json, transcript.json, shots.jpg (one frame per shot), hook.jpg (first 3 s),
timeline.jpg. The optional path/out_dir form measures any video, e.g. our own finished ad (format_check.py does this)."""
import json, os, re, subprocess, sys
import numpy as np
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import sfconfig  # puts ffmpeg on PATH

STUDY, VID = sys.argv[1], sys.argv[2]
SRC = sys.argv[3] if len(sys.argv) > 3 else os.path.join(STUDY, 'videos', VID + '.mp4')
OUT = sys.argv[4] if len(sys.argv) > 4 else os.path.join(STUDY, 'analysis', VID)
os.makedirs(OUT, exist_ok=True)
FONT = sfconfig.FONTS['bold'].replace(':', '\\:', 1)


def run(cmd):
    return subprocess.run(cmd, capture_output=True, text=True, encoding='utf-8', errors='replace')


def probe():
    r = run(['ffprobe', '-v', 'error', '-show_entries', 'format=duration:stream=codec_type,width,height,r_frame_rate',
             '-of', 'json', SRC])
    j = json.loads(r.stdout)
    v = [s for s in j['streams'] if s['codec_type'] == 'video'][0]
    n, d = v['r_frame_rate'].split('/')
    return float(j['format']['duration']), v['width'], v['height'], float(n) / float(d)


def cuts(dur):
    r = run(['ffmpeg', '-hide_banner', '-i', SRC, '-vf', "select='gt(scene,0.28)',showinfo", '-an', '-f', 'null', '-'])
    t = [float(m) for m in re.findall(r'pts_time:([\d.]+)', r.stderr)]
    t = [x for i, x in enumerate(t) if x > 0.15 and (i == 0 or x - t[i - 1] > 0.12)]
    bounds = [0.0] + t + [dur]
    shots = [round(b - a, 2) for a, b in zip(bounds, bounds[1:])]
    return t, shots


def loud(path):
    r = run(['ffmpeg', '-hide_banner', '-nostats', '-v', 'verbose', '-i', path, '-af', 'ebur128=peak=true:framelog=verbose', '-f', 'null', '-'])
    s = r.stderr
    def last(pat):
        m = re.findall(pat, s)
        return float(m[-1]) if m else None
    mom = [(float(a), float(b)) for a, b in re.findall(r't:\s*([\d.]+)\s+TARGET.*?M:\s*(-?[\d.]+|-inf)', s) if b != '-inf' and float(a) >= 0.4]
    return {'integrated_lufs': last(r'I:\s+(-?[\d.]+) LUFS'), 'range_lu': last(r'LRA:\s+(-?[\d.]+) LU'),
            'true_peak_dbtp': last(r'Peak:\s+(-?[\d.]+) dBFS')}, mom


def stems():
    sd = os.path.join(OUT, 'stems')
    voc = os.path.join(sd, 'htdemucs', VID, 'vocals.wav')
    if not os.path.exists(voc):
        wav = os.path.join(OUT, 'mix.wav')
        run(['ffmpeg', '-v', 'error', '-y', '-i', SRC, '-ac', '2', '-ar', '44100', wav])
        r = run([sys.executable, '-I', '-m', 'demucs', '--two-stems', 'vocals', '-n', 'htdemucs', '-o', sd, wav])
        os.replace(os.path.join(sd, 'htdemucs', 'mix'), os.path.join(sd, 'htdemucs', VID)) if os.path.isdir(os.path.join(sd, 'htdemucs', 'mix')) else None
        if not os.path.exists(voc):
            raise RuntimeError(r.stderr[-2000:])
    return voc, os.path.join(sd, 'htdemucs', VID, 'no_vocals.wav')


def bed_stats(path, dur):
    import librosa
    y, sr = librosa.load(path, sr=22050, mono=True)
    rms = librosa.feature.rms(y=y, frame_length=2048, hop_length=512)[0]
    db = 20 * np.log10(rms + 1e-9)
    present = float((db > -45).mean())        # share of time something (music/sfx) is audible under the voice
    on = librosa.onset.onset_detect(y=y, sr=sr, units='time', backtrack=False, delta=0.25)
    # loud hits = sound effects / accents: the background jumps 6+ dB above its own level of the previous 1.5 s
    hop_s = 512 / sr
    win = int(1.5 / hop_s)
    strong, last = [], -9
    for i in range(win, len(db)):
        base = np.median(db[i - win:i])
        if db[i] > base + 6 and db[i] > -40 and i * hop_s - last > 0.4:
            strong.append(i * hop_s); last = i * hop_s
    tempo = librosa.beat.beat_track(y=y, sr=sr)[0]
    return {'bed_audible_share': round(present, 2), 'onsets_per_min': round(len(on) / dur * 60, 1),
            'strong_hits_per_min': round(len(strong) / dur * 60, 1), 'strong_hit_times': [round(float(x), 2) for x in strong][:400],
            'bed_tempo_bpm': round(float(np.atleast_1d(tempo)[0]), 1)}


def transcribe(voc):
    import whisper
    m = whisper.load_model('large-v3-turbo')
    r = m.transcribe(voc, language='en', word_timestamps=True, condition_on_previous_text=False)
    words = [{'w': w['word'].strip(), 's': round(w['start'], 2), 'e': round(w['end'], 2)} for seg in r['segments'] for w in seg.get('words', [])]
    return r['text'].strip(), words


def speech_stats(words, dur):
    if not words:
        return {}
    first = words[0]['s']
    spoken = words[-1]['e'] - first
    gaps = [b['s'] - a['e'] for a, b in zip(words, words[1:])]
    first3 = ' '.join(w['w'] for w in words if w['s'] < 3.0)
    return {'word_count': len(words), 'first_word_at_s': first, 'words_per_sec': round(len(words) / max(spoken, 0.1), 2),
            'pauses_over_0.5s': sum(g > 0.5 for g in gaps), 'longest_pause_s': round(max(gaps), 2) if gaps else 0,
            'words_in_first_3s': first3, 'voice_covers_share': round(sum(w['e'] - w['s'] for w in words) / dur, 2)}


def sheet(times, name, cols, label):
    d = os.path.join(OUT, '_f_' + name)
    os.makedirs(d, exist_ok=True)
    for i, t in enumerate(times):
        run(['ffmpeg', '-v', 'error', '-y', '-ss', f'{t:.2f}', '-i', SRC, '-frames:v', '1', '-vf',
             f"scale=-2:300,drawtext=fontfile='{FONT}':text='{label(i, t)}':x=6:y=6:fontsize=22:fontcolor=yellow:box=1:boxcolor=black@0.7",
             os.path.join(d, f'{i:04d}.jpg')])
    rows = max(1, -(-len(times) // cols))
    run(['ffmpeg', '-v', 'error', '-y', '-i', os.path.join(d, '%04d.jpg'), '-frames:v', '1', '-vf', f'tile={cols}x{rows}:padding=4',
         '-q:v', '3', os.path.join(OUT, name + '.jpg')])
    for f in os.listdir(d):
        os.remove(os.path.join(d, f))
    os.rmdir(d)


dur, w, h, fps = probe()
cut_t, shots = cuts(dur)
mix_loud, mom = loud(SRC)
voc, bed = stems()
voc_loud, _ = loud(voc)
bed_loud, _ = loud(bed)
tf = os.path.join(OUT, 'transcript.json')
if os.path.exists(tf):
    tr = json.load(open(tf, encoding='utf-8'))
else:
    text, words = transcribe(voc)
    tr = {'text': text, 'words': words}
    json.dump(tr, open(tf, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
first3 = [s for t, s in mom if t <= 3.0]
rest = [s for t, s in mom if t > 3.0]
metrics = {
    'id': VID, 'duration_s': round(dur, 2), 'size': f'{w}x{h}', 'fps': round(fps, 2),
    'cuts': len(cut_t), 'cuts_per_min': round(len(cut_t) / dur * 60, 1), 'avg_shot_s': round(float(np.mean(shots)), 2),
    'median_shot_s': round(float(np.median(shots)), 2), 'longest_shot_s': max(shots), 'first_cut_at_s': round(cut_t[0], 2) if cut_t else None,
    'cut_times': [round(x, 2) for x in cut_t],
    'mix': mix_loud, 'voice': voc_loud, 'background': bed_loud,
    'voice_minus_background_lu': round(voc_loud['integrated_lufs'] - bed_loud['integrated_lufs'], 1)
    if voc_loud['integrated_lufs'] is not None and bed_loud['integrated_lufs'] is not None else None,
    'short_term_lufs_first3s': round(float(np.mean(first3)), 1) if first3 else None,
    'short_term_lufs_rest': round(float(np.mean(rest)), 1) if rest else None,
    'background_detail': bed_stats(bed, dur), 'speech': speech_stats(tr['words'], dur),
}
json.dump(metrics, open(os.path.join(OUT, 'metrics.json'), 'w', encoding='utf-8'), indent=1, default=lambda o: o.item())

# frames: middle of every shot (capped for long videos), and the hook
bounds = [0.0] + cut_t + [dur]
mids = [(a + b) / 2 for a, b in zip(bounds, bounds[1:])]
if len(mids) > 120:
    mids = [mids[int(i * len(mids) / 120)] for i in range(120)]
sheet(mids, 'shots', 8 if h > w else 6, lambda i, t: f'{i + 1}  {t:.1f}s')
step = 1.5 if dur < 120 else max(5.0, dur / 120)
sheet(list(np.arange(0.2, dur - 0.1, step)), 'timeline', 8 if h > w else 6, lambda i, t: f'{t:.1f}s')
sheet([0.0, 0.4, 0.8, 1.2, 1.6, 2.0, 2.5, 3.0], 'hook', 8 if h > w else 4, lambda i, t: f'{t:.1f}s')
print(json.dumps({k: metrics[k] for k in ('id', 'duration_s', 'cuts_per_min', 'avg_shot_s', 'voice_minus_background_lu')}, default=lambda o: o.item()))
