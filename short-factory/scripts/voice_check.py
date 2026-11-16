"""Pass/fail a finished narration against the measured targets (natural-ai-voice, stage 7).
Usage: python -I voice_check.py <final_voice.wav> natural|format|format-real|format-long [<transcript.json>]
Runs voice_style.py (Whisper first if no transcript) and prints YES/NO per check, plus <wav>_voicecheck.json.
Targets: natural = measured on the 9 videos of the faceless-channel study; format / format-long = the shorts-format study's
Shorts (with natural-level life) and long videos (studies of 29 Oct 2026); format-real = the real ranges of the format
benchmark's 10 top Shorts (11 Nov 2026): use it for every Short's voice from now on."""
import json, os, subprocess, sys

sys.stdout.reconfigure(encoding='utf-8')
WAV, MODE = sys.argv[1], sys.argv[2]
TR = sys.argv[3] if len(sys.argv) > 3 else None
HERE = os.path.dirname(os.path.abspath(__file__))
TARGETS = json.load(open(os.path.join(HERE, 'voice_targets.json'), encoding='utf-8'))[MODE]
out = os.path.splitext(WAV)[0] + '_voicestyle.json'
cmd = [sys.executable, '-I', os.path.join(HERE, 'voice_style.py'), WAV, out] + ([TR] if TR else [])
subprocess.run(cmd, check=True, capture_output=True)
m = json.load(open(out, encoding='utf-8'))
val = {
    'speed_wps': m['speed']['words_per_sec_mean'], 'phrase_speed_variation_pct': m['speed']['phrase_speed_variation_pct'],
    'tone_swing_semitones': m['pitch']['phrase_to_phrase_swing_semitones'], 'stressed_words_per_min': m['stressed_words_per_min'],
    'long_pauses_per_min': m['pauses']['per_min_over_1s'], 'mid_pauses_per_min': m['pauses']['per_min_0.5_1s'],
    'fillers_per_min': m['fillers_per_min'], 'loudness_swing_db': m['loudness']['phrase_loudness_swing_db'],
    'short_pauses_per_min': m['pauses']['per_min_0.25_0.5s'], 'stops_per_min': m['pauses']['phrases_per_min'],
}
rows, fails = [], 0
for k, (lo, hi, fix) in TARGETS.items():
    v = val.get(k)
    ok = v is not None and lo <= v <= hi
    fails += not ok
    rows.append((k, v, f'{lo}-{hi}', 'YES' if ok else 'NO', '' if ok else fix))
print(f'{"check":30} {"ours":>8}  {"target":>11}  pass')
for k, v, t, ok, fix in rows:
    print(f'{k:30} {str(v):>8}  {t:>11}  {ok}  {fix}')
print(f'\n{len(rows) - fails} of {len(rows)} checks passed ({MODE} mode).')
json.dump({'mode': MODE, 'values': val, 'rows': rows}, open(os.path.splitext(WAV)[0] + '_voicecheck.json', 'w', encoding='utf-8'), indent=1)
