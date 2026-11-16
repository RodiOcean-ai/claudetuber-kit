"""Word times for voice takes with faster-whisper (large-v3-turbo if cached, else medium.en).
Usage: py -3.13 words.py <wav> [<wav> ...]   -> writes <wav>.words.json next to each, prints text, speech span and pace."""
import sys, json, os, subprocess
import numpy as np
from faster_whisper import WhisperModel
m = None
for name in ('large-v3-turbo', 'deepdml/faster-whisper-large-v3-turbo-ct2', 'large-v3', 'medium.en', 'small.en'):
    try:
        m = WhisperModel(name, device='cpu', compute_type='int8'); print('model', name); break
    except Exception as e:
        print('no', name, str(e)[:80])
for p in sys.argv[1:]:
    pcm = np.frombuffer(subprocess.run(['ffmpeg','-v','error','-i',p,'-ac','1','-ar','16000','-f','f32le','-'],capture_output=True,check=True).stdout, np.float32)
    segs, _ = m.transcribe(pcm, language='en', word_timestamps=True, condition_on_previous_text=False, beam_size=5)
    ws = [{'w': w.word.strip(), 's': round(w.start, 3), 'e': round(w.end, 3)} for s in segs for w in (s.words or [])]
    json.dump(ws, open(os.path.splitext(p)[0] + '.words.json', 'w', encoding='utf-8'), indent=0)
    span = ws[-1]['e'] - ws[0]['s']
    print(f"{os.path.basename(p)}: {ws[0]['s']:.2f}-{ws[-1]['e']:.2f} s, {len(ws)} words, {len(ws)/span:.2f} w/s | {' '.join(w['w'] for w in ws)}")
