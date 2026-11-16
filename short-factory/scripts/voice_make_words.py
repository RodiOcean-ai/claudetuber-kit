"""Processor half of voice_make.py: word times for each take with Whisper (the project's whisper, large-v3-turbo, CPU only,
through the traffic light with -CpuOnly). Writes <take>.words.json as a list of {w, s, e}. 14 Nov 2026.
Usage: python voice_make_words.py <take.wav> [...]"""
import json, os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import sfconfig  # noqa: F401  (ffmpeg on PATH)
import whisper
m = whisper.load_model('large-v3-turbo', device='cpu')
for p in sys.argv[1:]:
    r = m.transcribe(p, language='en', word_timestamps=True, condition_on_previous_text=False, fp16=False)
    words = [{'w': w['word'].strip(), 's': round(w['start'], 2), 'e': round(w['end'], 2)} for s in r['segments'] for w in s['words']]
    json.dump(words, open(os.path.splitext(p)[0] + '.words.json', 'w', encoding='utf-8'), indent=1, ensure_ascii=False)
    print(f'{os.path.basename(p)}: {len(words)} words | {r["text"].strip()}', flush=True)
