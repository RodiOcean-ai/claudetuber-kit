"""Free local narration with Chatterbox (MIT licence, its own built-in voice: no cloning sample, no ElevenLabs output used).
Usage: <chatterbox venv python> make_voice.py <script.txt> <out_dir> [n_takes]
Writes take_<k>.wav (24 kHz) with different expressiveness settings and seeds; pick by ear/measurement, then polish."""
import sys, os, torch, torchaudio as ta
from chatterbox.tts import ChatterboxTTS
text = open(sys.argv[1], encoding='utf-8').read().strip()
out = sys.argv[2]; os.makedirs(out, exist_ok=True)
n = int(sys.argv[3]) if len(sys.argv) > 3 else 6
m = ChatterboxTTS.from_pretrained(device='cuda')
settings = [(0.5, 0.5), (0.4, 0.5), (0.6, 0.4), (0.45, 0.35), (0.5, 0.3), (0.35, 0.45), (0.55, 0.5), (0.4, 0.3)]
for k in range(n):
    ex, cfg = settings[k % len(settings)]
    torch.manual_seed(100 + k)
    wav = m.generate(text, exaggeration=ex, cfg_weight=cfg)
    p = os.path.join(out, f'take_{k + 1}.wav')
    ta.save(p, wav, m.sr)
    print(f'take_{k + 1}: exaggeration {ex} cfg {cfg}  {wav.shape[-1] / m.sr:.2f} s', flush=True)
