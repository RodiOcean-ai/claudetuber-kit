"""Graphics-card half of voice_make.py (runs in the Chatterbox venv, ONLY through the traffic light). 14 Nov 2026.
Reads a job file (JSON): sentences, lively sample, calm sample, exaggeration, cfg, pause, takes, out folder.
For each take: every sentence read by Chatterbox copying the LIVELY sample (energy and emphasis), joined with short pauses,
then the whole read voice-swapped (Chatterbox VC) to the CALM sample (the original speaker). Writes <out>/take<N>_raw.wav (24 kHz)."""
import json, sys
import torch, torchaudio as ta
from chatterbox.tts import ChatterboxTTS
from chatterbox.vc import ChatterboxVC

job = json.load(open(sys.argv[1], encoding='utf-8'))
out = job['out']
tts = ChatterboxTTS.from_pretrained(device='cuda')
reads = []
for k in range(1, job['takes'] + 1):
    torch.manual_seed(1000 + k)
    parts = []
    for s in job['sentences']:
        parts += [tts.generate(s, audio_prompt_path=job['lively'], exaggeration=job['exaggeration'], cfg_weight=job['cfg']),
                  torch.zeros(1, int(job['pause'] * tts.sr))]
    read = torch.cat(parts[:-1], dim=1)
    path = f'{out}/take{k}_tts.wav'; ta.save(path, read, tts.sr); reads.append(path)
    print(f'take {k}: read {read.shape[-1] / tts.sr:.1f} s', flush=True)
del tts; torch.cuda.empty_cache()
if not job.get('swap', True):                                  # no voice swap: it made a "weird echo" (owner, 14 Nov 2026)
    import shutil
    for k, path in enumerate(reads, 1):
        shutil.copyfile(path, f'{out}/take{k}_raw.wav')
    sys.exit(0)
vc = ChatterboxVC.from_pretrained('cuda')
for k, path in enumerate(reads, 1):
    wav = vc.generate(audio=path, target_voice_path=job['calm'])
    ta.save(f'{out}/take{k}_raw.wav', wav, vc.sr)
    print(f'take {k}: voice swapped, {wav.shape[-1] / vc.sr:.1f} s', flush=True)
