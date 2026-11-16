import sys, glob, os, numpy as np, librosa
for p in sorted(glob.glob(r'<your-sound-library>/music/*.mp3')):
    y, sr = librosa.load(p, sr=22050, mono=True)
    tempo, beats = librosa.beat.beat_track(y=y, sr=sr, units='time')
    rms = librosa.feature.rms(y=y, hop_length=sr // 2)[0]
    db = 20 * np.log10(rms / rms.max() + 1e-9)
    env = ' '.join(f'{d:.0f}' for d in db[::2])   # one value per second
    cen = librosa.feature.spectral_centroid(y=y, sr=sr).mean()
    print(f"{os.path.basename(p)}: {len(y)/sr:.1f} s, tempo {float(np.atleast_1d(tempo)[0]):.0f}, beats {len(beats)}, first beat {beats[0] if len(beats) else -1:.2f}, centroid {cen:.0f} Hz")
    print('   dB per s:', env)
