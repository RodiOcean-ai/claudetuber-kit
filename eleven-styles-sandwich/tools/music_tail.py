import sys, numpy as np, librosa
for name in sys.argv[1:]:
    p = rf'<your-sound-library>/music/{name}'
    y, sr = librosa.load(p, sr=22050, mono=True)
    dur = len(y) / sr
    tempo, beats = librosa.beat.beat_track(y=y, sr=sr, units='time')
    onset = librosa.onset.onset_strength(y=y, sr=sr)
    t = librosa.times_like(onset, sr=sr)
    tail = t > dur - 20
    # strongest onsets in the last 20 s
    idx = np.argsort(onset[tail])[::-1][:12]
    strong = sorted(t[tail][idx])
    rms = librosa.feature.rms(y=y, hop_length=int(sr * 0.25))[0]; db = 20 * np.log10(rms / rms.max() + 1e-9)
    tt = np.arange(len(db)) * 0.25
    print(name, f'{dur:.2f} s, tempo {float(np.atleast_1d(tempo)[0]):.1f}')
    print('  beats in last 18 s:', ' '.join(f'{b:.2f}' for b in beats if b > dur - 18))
    print('  strong onsets:', ' '.join(f'{s:.2f}' for s in strong))
    print('  dB/0.25s last 8 s:', ' '.join(f'{d:.0f}' for d, x in zip(db, tt) if x > dur - 8))
