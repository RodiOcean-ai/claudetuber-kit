"""Second pass: same words, extra punctuation for natural pauses, calmer settings. Usage: <venv python> make_voice2.py <out_dir>"""
import sys, os, torch, torchaudio as ta
from chatterbox.tts import ChatterboxTTS
out = sys.argv[1]; os.makedirs(out, exist_ok=True)
texts = {
 'p': "Take two slices of bread. Then dig a knife into the peanut butter, and spread it right to the edges. Press the second slice on top, and cut it corner to corner... because triangles taste better.",
 'q': "Take two slices of bread... then dig a knife into the peanut butter, and spread it, right to the edges. Press the second slice on top... and cut it corner to corner, because triangles taste better.",
}
m = ChatterboxTTS.from_pretrained(device='cuda')
k = 0
for key, text in texts.items():
    for ex, cfg in [(0.3, 0.2), (0.35, 0.3), (0.4, 0.25)]:
        for seed in (1, 2):
            torch.manual_seed(seed); k += 1
            wav = m.generate(text, exaggeration=ex, cfg_weight=cfg)
            p = os.path.join(out, f'{key}_e{ex}_c{cfg}_s{seed}.wav'); ta.save(p, wav, m.sr)
            print(f'{os.path.basename(p)} {wav.shape[-1] / m.sr:.2f} s', flush=True)
