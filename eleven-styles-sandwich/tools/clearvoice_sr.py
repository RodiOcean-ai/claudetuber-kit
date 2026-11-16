"""ClearerVoice MossFormer2_SR_48K on one file: rebuild real highs of a 24 kHz free voice at 48 kHz (owner's pick, 14 Nov 2026).
Usage: <tools/clearvoice venv python> clearvoice_sr.py <in.wav> <out.wav>"""
import sys, time
from clearvoice import ClearVoice
t = time.time()
cv = ClearVoice(task='speech_super_resolution', model_names=['MossFormer2_SR_48K'])
y = cv(input_path=sys.argv[1], online_write=False)
cv.write(y, output_path=sys.argv[2])
print(f'{sys.argv[1]} -> {sys.argv[2]} in {time.time() - t:.1f} s')
