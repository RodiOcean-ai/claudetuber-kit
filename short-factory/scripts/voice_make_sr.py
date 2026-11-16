"""Processor half of voice_make.py (runs in the ClearerVoice venv, through the traffic light with -CpuOnly). 14 Nov 2026.
ClearerVoice MossFormer2_SR_48K rebuilds the highs the 24 kHz voice lacks. On the processor it is slow (about 90 s for 33 s
of voice) but safe: on a busy graphics card it once froze the card for over an hour.
Usage: python voice_make_sr.py <in.wav> <out.wav> [<in.wav> <out.wav> ...]"""
import os, sys, time
a = sys.argv[1:]
from clearvoice import ClearVoice
os.chdir(os.environ.get('CLEARVOICE_HOME', os.getcwd()))      # its models live in <home>/checkpoints
cv = ClearVoice(task='speech_super_resolution', model_names=['MossFormer2_SR_48K'])
for src, dst in zip(a[::2], a[1::2]):
    t = time.time(); y = cv(input_path=src, online_write=False); cv.write(y, output_path=dst)
    print(f'{os.path.basename(src)} -> 48 kHz in {time.time() - t:.0f} s', flush=True)
