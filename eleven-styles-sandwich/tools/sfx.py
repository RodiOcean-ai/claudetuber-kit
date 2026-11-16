"""Copy sound effects from the house library into public/sfx: lead silence trimmed, peak set to -6 dBFS, 44.1 kHz.
Usage: py -3.13 sfx.py name=relative/path/in/house_sound [name2=...]   (e.g. pop=sfx/S5_soft_pop_PICK.mp3)"""
import sys, os, subprocess, numpy as np
LIB = r'<your-sound-library>'
OUT = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'public', 'sfx')
os.makedirs(OUT, exist_ok=True)
for arg in sys.argv[1:]:
    name, rel = arg.split('=', 1)
    src = os.path.join(LIB, rel)
    x = np.frombuffer(subprocess.run(['ffmpeg', '-v', 'error', '-i', src, '-ac', '2', '-ar', '44100', '-f', 'f32le', '-'],
                                     capture_output=True, check=True).stdout, np.float32).reshape(-1, 2).copy()
    mono = np.abs(x).max(1); thr = mono.max() * 10 ** (-50 / 20)
    start = max(0, int(np.argmax(mono > thr)) - 44)
    x = x[start:]
    x *= 10 ** (-6 / 20) / max(1e-9, np.abs(x).max())
    dst = os.path.join(OUT, name + '.wav')
    subprocess.run(['ffmpeg', '-v', 'error', '-y', '-f', 'f32le', '-ar', '44100', '-ac', '2', '-i', '-', '-c:a', 'pcm_s16le', dst],
                   input=x.astype(np.float32).tobytes(), check=True)
    print(f'{name}.wav  {len(x) / 44100:.2f} s  <- {rel}')
