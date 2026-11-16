"""Owner's voice recipe (14 Nov 2026, "use Chatterbox + ClearerVoice"): Chatterbox cloned from the channel voice sample
(your own voice sample, the same sample as his "Chatterbox try 2"), no time-stretching afterwards.
Usage: <chatterbox venv python> make_voice3.py <out_dir> [cpu|cuda]
Writes <key>_e<ex>_c<cfg>_s<seed>.wav (24 kHz). ClearerVoice SR 48K runs afterwards (tools/clearvoice venv)."""
import sys, os, torch, torchaudio as ta
from chatterbox.tts import ChatterboxTTS

out = sys.argv[1]; os.makedirs(out, exist_ok=True)
dev = sys.argv[2] if len(sys.argv) > 2 else 'cuda'
REF = r'<your-voice-sample.wav>'
texts = {
    # same words as the locked script; the punctuation only shapes the natural pauses between steps
    'q': "Take two slices of bread... then dig a knife into the peanut butter, and spread it, right to the edges. Press the second slice on top... and cut it corner to corner, because triangles taste better.",
    'p': "Take two slices of bread. Then dig a knife into the peanut butter, and spread it right to the edges. Press the second slice on top, and cut it corner to corner... because triangles taste better.",
}
m = ChatterboxTTS.from_pretrained(device=dev)
for key, text in texts.items():
    for ex, cfg in [(0.4, 0.3), (0.5, 0.5)]:
        for seed in (1, 2):
            torch.manual_seed(seed)
            wav = m.generate(text, audio_prompt_path=REF, exaggeration=ex, cfg_weight=cfg)
            p = os.path.join(out, f'{key}_e{ex}_c{cfg}_s{seed}.wav')
            ta.save(p, wav, m.sr)
            print(f'{os.path.basename(p)} {wav.shape[-1] / m.sr:.2f} s', flush=True)
