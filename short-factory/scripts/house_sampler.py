"""House sampler: Claude composes, real instruments play it (15 Nov 2026).
Plays note lists with the house instrument recordings (assets/house_sound/instruments, CC0, see SOURCES.md) and writes a
finished stereo WAV. Pure numpy on the processor (no graphics card, nothing installed). Pieces:
  * Instrument   - one recorded instrument: picks the nearest recorded note and loudness layer, shifts the pitch a little,
                   shapes the note (attack, hold, release; long held notes loop smoothly).
  * theory       - chord symbols ('D', 'Bm7', 'G/B', 'Asus4'), smooth voicings, scales.
  * Cue          - a piece of music for one stretch of video: segments (tempo, key, chord progression, layers), each
                   starting at a second (usually a spoken word), snapped to the bar grid unless told not to.
  * layers       - piano arpeggios, block chords, bass, string pads, plucked ostinatos, sparkles, harp rolls, shaker,
                   melodies. Each turns one bar + chord into notes.
  * render       - notes -> audio, room reverb (overlap-add convolution), loudness match, 16-bit WAV.
Used by masterclass-video/tools/mc_score.py. Run with: py -3.13 -P -X utf8 <script>  (the recordings are data only).
"""
from __future__ import annotations

import glob, json, math, os, re, struct, wave
from dataclasses import dataclass, field

import numpy as np

SR = 48000
ROOT = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'assets', 'house_sound', 'instruments'))

# ----------------------------------------------------------------------------------------------------------------- WAV
def read_wav(path: str) -> tuple[np.ndarray, int]:
    """Any PCM 8/16/24/32-bit or float WAV -> float32 (n, 2) and its sample rate."""
    with open(path, 'rb') as f:
        data = f.read()
    if data[:4] != b'RIFF' or data[8:12] != b'WAVE':
        raise ValueError(f'not a WAV: {path}')
    pos, tag, ch, sr, bits, raw = 12, None, 1, SR, 16, None
    while pos + 8 <= len(data):
        cid = data[pos:pos + 4]
        size = int.from_bytes(data[pos + 4:pos + 8], 'little')
        body = data[pos + 8:pos + 8 + size]
        if cid == b'fmt ':
            tag, ch, sr, _, _, bits = struct.unpack('<HHIIHH', body[:16])
            if tag == 0xFFFE and len(body) >= 26:
                tag = int.from_bytes(body[24:26], 'little')
        elif cid == b'data':
            raw = body
        pos += 8 + size + (size & 1)
    if raw is None or tag is None:
        raise ValueError(f'no audio in {path}')
    bps = bits // 8
    raw = raw[: len(raw) - len(raw) % (bps * ch)]
    if tag == 1:
        if bits == 16:
            x = np.frombuffer(raw, '<i2').astype(np.float32) / 32768.0
        elif bits == 24:
            b = np.frombuffer(raw, np.uint8).reshape(-1, 3).astype(np.int32)
            v = b[:, 0] | (b[:, 1] << 8) | (b[:, 2] << 16)
            v = np.where(v >= 1 << 23, v - (1 << 24), v)
            x = v.astype(np.float32) / 8388608.0
        elif bits == 32:
            x = np.frombuffer(raw, '<i4').astype(np.float32) / 2147483648.0
        elif bits == 8:
            x = (np.frombuffer(raw, np.uint8).astype(np.float32) - 128) / 128.0
        else:
            raise ValueError(f'{bits}-bit PCM in {path}')
    elif tag == 3:
        x = np.frombuffer(raw, '<f4' if bits == 32 else '<f8').astype(np.float32)
    else:
        raise ValueError(f'format {tag} in {path}')
    x = x.reshape(-1, ch)
    x = np.repeat(x, 2, axis=1) if ch == 1 else x[:, :2]
    return np.ascontiguousarray(x), sr


def write_wav(path: str, x: np.ndarray, sr: int = SR) -> None:
    y = np.clip(x, -1, 1)
    y = (y * 32767).astype('<i2')
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with wave.open(path, 'wb') as w:
        w.setnchannels(2); w.setsampwidth(2); w.setframerate(sr)
        w.writeframes(y.tobytes())


# ------------------------------------------------------------------------------------------------------------- pitches
PC = {'C': 0, 'C#': 1, 'Db': 1, 'D': 2, 'D#': 3, 'Eb': 3, 'E': 4, 'F': 5, 'F#': 6, 'Gb': 6, 'G': 7, 'G#': 8, 'Ab': 8,
      'A': 9, 'A#': 10, 'Bb': 10, 'B': 11, 'Cb': 11, 'E#': 5, 'Fb': 4, 'B#': 0}
NOTE_RE = re.compile(r'(?<![A-Za-z])([A-G])([#b]?)(-?\d)(?![0-9])')


def name_to_midi(name: str) -> int | None:
    """'A#3' / 'Bb3' / 'C-1' -> midi (C4 = 60). Returns the LAST note-like token in the name."""
    hits = NOTE_RE.findall(name)
    if not hits:
        return None
    l, acc, octv = hits[-1]
    return 12 * (int(octv) + 1) + PC[l + acc]


def midi_name(m: int) -> str:
    return ['C', 'C#', 'D', 'Eb', 'E', 'F', 'F#', 'G', 'Ab', 'A', 'Bb', 'B'][m % 12] + str(m // 12 - 1)


def detect_midi(x: np.ndarray, sr: int, at: float = 0.12) -> float | None:
    """Rough pitch of a recorded note (autocorrelation), as a fractional midi number; None if unclear."""
    a = int(at * sr)
    seg = x[a:a + 8192, 0].astype(np.float64)
    if len(seg) < 4096 or np.max(np.abs(seg)) < 1e-4:
        return None
    seg = seg - seg.mean()
    seg *= np.hanning(len(seg))
    n = 1 << (len(seg) * 2 - 1).bit_length()
    f = np.fft.rfft(seg, n)
    ac = np.fft.irfft(f * np.conj(f))[: len(seg)]
    lo, hi = int(sr / 2000), int(sr / 25)
    if hi >= len(ac):
        hi = len(ac) - 1
    k = lo + int(np.argmax(ac[lo:hi]))
    if ac[k] < 0.25 * ac[0]:
        return None
    # parabolic refine
    if 1 <= k < len(ac) - 1:
        y0, y1, y2 = ac[k - 1], ac[k], ac[k + 1]
        d = 0.5 * (y0 - y2) / (y0 - 2 * y1 + y2) if (y0 - 2 * y1 + y2) != 0 else 0
        k = k + float(np.clip(d, -1, 1))
    if k <= 0:
        return None
    f0 = sr / k
    return 69 + 12 * math.log2(f0 / 440.0)


# ------------------------------------------------------------------------------------------------------------ samples
@dataclass
class Sample:
    path: str
    midi: int
    layer: int          # loudness layer, 0 = softest
    rr: int = 0         # round robin take
    _x: np.ndarray | None = None
    _sr: int = SR
    _on: int = 0

    def load(self) -> tuple[np.ndarray, int, int]:
        if self._x is None:
            x, sr = read_wav(self.path)
            pk = float(np.max(np.abs(x))) or 1.0
            env = np.max(np.abs(x), axis=1)
            idx = np.nonzero(env > pk * 0.01)[0]       # first sound above -40 dB of the peak, minus 3 ms
            on = max(0, int(idx[0]) - int(0.003 * sr)) if len(idx) else 0
            self._x, self._sr, self._on = x, sr, on
        return self._x, self._sr, self._on


def cubic(x: np.ndarray, pos: np.ndarray) -> np.ndarray:
    """4-point cubic (Catmull-Rom) read of x (n, 2) at fractional positions."""
    n = len(x)
    i = np.floor(pos).astype(np.int64)
    t = (pos - i).astype(np.float32)[:, None]
    i1 = np.clip(i, 0, n - 1); i0 = np.clip(i - 1, 0, n - 1); i2 = np.clip(i + 1, 0, n - 1); i3 = np.clip(i + 2, 0, n - 1)
    xm, x0, x1, x2 = x[i0], x[i1], x[i2], x[i3]
    c1 = 0.5 * (x1 - xm)
    c2 = xm - 2.5 * x0 + 2 * x1 - 0.5 * x2
    c3 = 0.5 * (x2 - xm) + 1.5 * (x0 - x1)
    return ((c3 * t + c2) * t + c1) * t + x0


@dataclass
class Instrument:
    name: str
    samples: list[Sample]
    kind: str = 'oneshot'      # 'oneshot' (rings out: piano, harp, mallets, plucks) or 'sustain' (bowed, blown: loops)
    gain: float = 1.0
    release: float = 0.3       # seconds of fade after the note ends (oneshot: damper; sustain: bow lift)
    max_ring: float = 6.0      # oneshot: longest a note may ring after it ends
    attack: float = 0.0        # extra fade-in (sustain swells)
    pan: float = 0.0           # -1 left .. +1 right
    send: float = 0.2          # how much goes to the room
    vel_curve: float = 1.6     # loudness = vel ** curve
    pitched: bool = True
    lo: int = 0
    hi: int = 127
    _rr: dict = field(default_factory=dict)

    def __post_init__(self):
        self.samples.sort(key=lambda s: (s.midi, s.layer, s.rr))
        self.layers = sorted({s.layer for s in self.samples})
        mids = [s.midi for s in self.samples]
        self.lo, self.hi = min(mids) - 3, max(mids) + 3

    def pick(self, midi: int, vel: float) -> Sample:
        nl = len(self.layers)
        want = self.layers[min(nl - 1, int(vel * nl))] if nl > 1 else self.layers[0]
        cands = [s for s in self.samples if s.layer == want] or self.samples
        if self.pitched:
            best = min(abs(s.midi - midi) for s in cands)
            # prefer recordings at or a little below the note (shifting up sounds more natural than down)
            near = [s for s in cands if abs(s.midi - midi) == best]
        else:
            near = cands
        key = (want, near[0].midi)
        k = self._rr.get(key, 0)
        self._rr[key] = k + 1
        return near[k % len(near)]

    def note(self, midi: int, vel: float, dur: float) -> np.ndarray:
        s = self.pick(midi, vel)
        x, sr, on = s.load()
        fine = 0.0 if self.name == 'piano' else TUNING.get(os.path.relpath(s.path, ROOT), 0.0)   # pianos keep their own stretch
        semis = (midi - s.midi - (fine if abs(fine) <= 60 else 0.0) / 100) if self.pitched else 0
        ratio = (sr / SR) * (2 ** (semis / 12))
        avail = (len(x) - on) / ratio / SR                         # seconds of recording after the onset
        if self.kind == 'sustain':
            total = dur + self.release
        else:
            total = min(avail, dur + self.max_ring)
        n = int(total * SR)
        if self.kind == 'sustain' and total > avail - 0.05:
            y = self._looped(x[on:], ratio, n)
        else:
            pos = on + np.arange(n) * ratio
            y = cubic(x, pos)
        g = self.gain * (max(0.02, vel) ** self.vel_curve)
        env = np.ones(n, np.float32)
        if self.attack > 0:
            a = min(n, int(self.attack * SR))
            env[:a] = np.linspace(0, 1, a, dtype=np.float32) ** 1.5
        else:
            a = min(n, int(0.002 * SR))
            env[:a] = np.linspace(0, 1, a, dtype=np.float32)
        d = int(dur * SR)
        if self.kind == 'sustain' or d < n:
            r = max(1, int(self.release * SR)) if self.kind == 'sustain' else max(1, int(max(self.release, 0.05) * SR))
            if d < n:
                tail = np.exp(-np.arange(n - d) / (r / 4.6)).astype(np.float32)   # -40 dB at `release`
                env[d:] *= tail
        f = min(n, int(0.01 * SR))                                   # tiny fade at the very end: no clicks
        env[n - f:] *= np.linspace(1, 0, f, dtype=np.float32)
        y = y * (env * g)[:, None]
        if self.pan:
            ang = (self.pan + 1) * math.pi / 4
            y = y * np.array([math.cos(ang), math.sin(ang)], np.float32) * math.sqrt(2)
        return y.astype(np.float32)

    @staticmethod
    def _looped(x: np.ndarray, ratio: float, n: int) -> np.ndarray:
        """A held note longer than its recording: play it, then keep repeating its middle with 0.35 s cross-fades."""
        L = len(x)
        a, b = int(L * 0.35), int(L * 0.85)
        xf = int(0.35 * SR * ratio)
        if b - a < 2 * xf:
            xf = max(1, (b - a) // 3)
        body = x[:b].copy()
        loop = x[a:b]
        out = [body]
        cur = len(body)
        need = int(n * ratio) + 4
        w = np.linspace(0, 1, xf, dtype=np.float32)[:, None]
        while cur < need:
            prev = out[-1]
            seam = prev[-xf:] * np.sqrt(1 - w) + loop[:xf] * np.sqrt(w)
            out[-1] = prev[:-xf]
            out.append(np.concatenate([seam, loop[xf:]]))
            cur += len(loop) - xf
        y = np.concatenate(out)
        return cubic(y, np.arange(n) * ratio)


# ------------------------------------------------------------------------------------------------ instrument registry
# gains: measured 15 Nov so every instrument is equally loud at the same note strength (about -36 dB RMS at vel 0.6;
# shaker -44 dB). Balance in a piece comes from the score's velocities, not from here.
def _files(sub: str) -> list[str]:
    return sorted(glob.glob(os.path.join(ROOT, sub, '**', '*.wav'), recursive=True))


LAYER_WORDS = {'pp': 0, 'p': 1, 'mp': 2, 'mf': 3, 'f': 4, 'ff': 5, 'soft': 0, 'quiet': 0, 'medium': 2, 'loud': 4, 'hard': 5}


def _layer_of(name: str) -> int:
    m = re.search(r'(?:^|[_ \-])(?:v|dyn|vl|vel)(\d+)(?=[_ \-.]|$)', name, re.I)
    if m:
        return int(m.group(1))
    for tok in re.split(r'[_ \-.]', name.lower()):
        if tok in LAYER_WORDS:
            return LAYER_WORDS[tok]
    return 0


def _rr_of(name: str) -> int:
    m = re.search(r'(?:rr|RR)(\d+)', name)
    if m:
        return int(m.group(1))
    m = re.search(r'_(\d{1,2})\.wav$', name)
    return int(m.group(1)) if m else 0


def _by_name(sub: str, octave_shift: int = 0, skip: str | None = None) -> list[Sample]:
    out = []
    for p in _files(sub):
        n = os.path.basename(p)
        if skip and re.search(skip, n, re.I):
            continue
        m = name_to_midi(n)
        if m is None:
            continue
        out.append(Sample(p, m + 12 * octave_shift, _layer_of(n), _rr_of(n)))
    # renumber layers 0..k-1
    lay = sorted({s.layer for s in out})
    for s in out:
        s.layer = lay.index(s.layer)
    return out


def _upright_piano() -> list[Sample]:
    """VSCO2 'Upright Piano': Player_dyn<L>_rr1_<NNN>.wav, NNN = steps of 2 semitones; MappingChart.txt gives the note."""
    sub = os.path.join(ROOT, 'vsco2ce', 'Keys', 'Upright Piano')
    chart = {}
    mp = os.path.join(sub, 'MappingChart.txt')
    if os.path.exists(mp):
        for line in open(mp, encoding='utf-8', errors='replace'):
            m = re.match(r'\s*(\d{3})\s*=\s*(\d+)\s*$', line)          # "000=21" (KeyNumber notation = midi)
            if m:
                chart[m.group(1)] = int(m.group(2))
    out = []
    for p in _files(os.path.join('vsco2ce', 'Keys', 'Upright Piano')):
        n = os.path.basename(p)
        m = re.search(r'dyn(\d)_rr(\d)_(\d{3})', n)
        if not m:
            continue
        num = m.group(3)
        midi = chart.get(num)
        if midi is None:
            midi = PIANO_BASE + int(num)          # fallback, verified by detect in check()
        out.append(Sample(p, midi, int(m.group(1)) - 1, int(m.group(2))))
    return out


PIANO_BASE = 21   # fallback only (A0 + number); check() verifies the real pitch
_CACHE: dict[str, Instrument] = {}
OCTAVE_FIX: dict[str, int] = {}   # set after check(): octave correction per instrument (in octaves)
_FIX_FILE = os.path.join(ROOT, 'octave_fix.json')
if os.path.exists(_FIX_FILE):
    OCTAVE_FIX.update(json.load(open(_FIX_FILE, encoding='utf-8')))


_TUNE_FILE = os.path.join(ROOT, 'tuning.json')
TUNING: dict[str, float] = json.load(open(_TUNE_FILE, encoding='utf-8')) if os.path.exists(_TUNE_FILE) else {}


def measure_cents(s: Sample) -> float | None:
    """How far (in cents) the recording is from its named pitch: spectrum peak at a harmonic above 200 Hz."""
    x, sr, on = s.load()
    seg = x[on + int(0.05 * sr): on + int(0.05 * sr) + 16384, 0].astype(np.float64)
    if len(seg) < 8192:
        return None
    f_exp = 440 * 2 ** ((s.midi - 69) / 12)
    h = max(1, math.ceil(200 / f_exp))
    N = 1 << 17
    F = np.abs(np.fft.rfft(seg * np.hanning(len(seg)), N))
    f = np.fft.rfftfreq(N, 1 / sr)
    lo, hi = f_exp * h * 2 ** (-0.7 / 12), f_exp * h * 2 ** (0.7 / 12)
    idx = np.nonzero((f >= lo) & (f <= hi))[0]
    if len(idx) < 3:
        return None
    k = idx[np.argmax(F[idx])]
    if F[k] < 0.05 * F.max() or k in (idx[0], idx[-1]):
        return None
    y0, y1, y2 = np.log(F[k - 1] + 1e-12), np.log(F[k] + 1e-12), np.log(F[k + 1] + 1e-12)
    d = 0.5 * (y0 - y2) / (y0 - 2 * y1 + y2) if (y0 - 2 * y1 + y2) != 0 else 0
    fk = (k + float(np.clip(d, -1, 1))) * (f[1] - f[0])
    return 1200 * math.log2(fk / (f_exp * h))


def tune_all() -> None:
    out = {}
    for name in ALL:
        if name == 'shaker':
            continue
        I = _make(name)
        cs = []
        for s in I.samples:
            c = measure_cents(s)
            if c is not None and abs(c) < 60:
                out[os.path.relpath(s.path, ROOT)] = round(c, 1); cs.append(c)
        print(f'{name:9s} tuned {len(cs)}/{len(I.samples)}  median {np.median(cs) if cs else 0:+.0f} cents  spread {np.ptp(cs) if cs else 0:.0f}')
    json.dump(out, open(_TUNE_FILE, 'w', encoding='utf-8'), indent=0)
    TUNING.clear(); TUNING.update(out)


def _make(name: str) -> Instrument:
    sh = OCTAVE_FIX.get(name, 0)
    V, C = 'vsco2ce', 'vcsl'
    if name == 'piano':
        s = _upright_piano()
        for x in s:
            x.midi += 12 * sh
        return Instrument('piano', s, 'oneshot', gain=2.16, release=0.35, max_ring=5.0, send=0.22, pan=0.0)
    table = {
        'violins':  (f'{V}/Strings/Violin Section/susVib', dict(kind='sustain', gain=1.21, release=0.6, attack=0.25, send=0.32, pan=-0.35)),
        'violas':   (f'{V}/Strings/Viola Section/susvib', dict(kind='sustain', gain=0.375, release=0.6, attack=0.25, send=0.32, pan=0.1)),
        'cellos':   (f'{V}/Strings/Cello Section/susvib', dict(kind='sustain', gain=0.28, release=0.6, attack=0.25, send=0.3, pan=0.35)),
        'vln_pizz': (f'{V}/Strings/Violin Section/Pizz', dict(kind='oneshot', gain=0.89, release=0.15, max_ring=0.8, send=0.25, pan=-0.3)),
        'vc_pizz':  (f'{V}/Strings/Cello Section/pizzT', dict(kind='oneshot', gain=1.01, release=0.2, max_ring=1.2, send=0.22, pan=0.3)),
        'harp':     (f'{V}/Strings/Harp', dict(kind='oneshot', gain=2.04, release=1.2, max_ring=4.0, send=0.3, pan=-0.2)),
        'flute':    (f'{V}/Woodwinds/Flute/susvib', dict(kind='sustain', gain=0.877, release=0.35, attack=0.08, send=0.3, pan=0.2)),
        'horn':     (f'{V}/Brass/F Horn/sus', dict(kind='sustain', gain=0.713, release=0.5, attack=0.3, send=0.35, pan=0.25)),
        'glock':    (f'{V}/Percussion/Glock', dict(kind='oneshot', gain=9.0, release=1.5, max_ring=3.0, send=0.3, pan=0.25)),
        'marimba':  (f'{V}/Percussion/Marimba', dict(kind='oneshot', gain=2.54, release=0.4, max_ring=1.5, send=0.2, pan=-0.15)),
        'vibes':    (f'{C}/Idiophones/Struck Idiophones/Vibraphone/Soft Mallets', dict(kind='oneshot', gain=0.766, release=1.0, max_ring=3.5, send=0.3, pan=0.15)),
        'kalimba':  (f'{C}/Idiophones/Plucked Idiophones/Kalimba, Kenya', dict(kind='oneshot', gain=2.16, release=0.6, max_ring=2.0, send=0.25, pan=-0.1)),
    }
    if name == 'shaker':
        s = [Sample(p, 0, i % 2, i) for i, p in enumerate(_files(f'{C}/Idiophones/Struck Idiophones/Shaker, Small'))]
        return Instrument('shaker', s, 'oneshot', gain=4.9, release=0.1, max_ring=0.4, send=0.12, pitched=False, pan=0.3)
    sub, kw = table[name]
    s = _by_name(sub)
    for x in s:
        x.midi += 12 * sh
    if not s:
        raise FileNotFoundError(f'no recordings for {name} in {sub}')
    return Instrument(name, s, **kw)


def inst(name: str) -> Instrument:
    if name not in _CACHE:
        _CACHE[name] = _make(name)
    return _CACHE[name]


ALL = ['piano', 'violins', 'violas', 'cellos', 'vln_pizz', 'vc_pizz', 'harp', 'flute', 'horn', 'glock', 'marimba',
       'vibes', 'kalimba', 'shaker']


def check(write_fix: bool = True) -> None:
    """Compare each instrument's file-name notes with the pitch actually heard; store octave corrections."""
    fix = {}
    for name in ALL:
        if name == 'shaker':
            continue
        try:
            I = _make(name) if name not in OCTAVE_FIX else _make(name)
        except Exception as e:  # noqa: BLE001
            print(f'{name:9s} MISSING: {e}'); continue
        diffs = []
        picks = I.samples[:: max(1, len(I.samples) // 8)][:8]
        for s in picks:
            x, sr, on = s.load()
            d = detect_midi(x[on:], sr)
            if d is not None:
                diffs.append(d - s.midi)
        oct_ = [round(d / 12) for d in diffs]
        best = max(set(oct_), key=oct_.count) if oct_ else 0
        fix[name] = OCTAVE_FIX.get(name, 0) + 0  # current
        cents = [round((d - 12 * best) * 100) for d in diffs]
        print(f'{name:9s} {len(I.samples):3d} notes {midi_name(min(s.midi for s in I.samples))}-{midi_name(max(s.midi for s in I.samples))}'
              f' layers {len(I.layers)}  heard-vs-name octaves {oct_}  cents {cents}')
        if best != 0:
            fix[name] = OCTAVE_FIX.get(name, 0) + best
    fix['glock'] = 1          # autocorrelation can't read a glockenspiel (bell overtones); spectrum check: +1 octave
    if write_fix:
        json.dump({k: v for k, v in fix.items() if v}, open(_FIX_FILE, 'w', encoding='utf-8'), indent=1)
        print('octave fixes:', {k: v for k, v in fix.items() if v})


# -------------------------------------------------------------------------------------------------------------- theory
QUAL = {
    '': [0, 4, 7], 'm': [0, 3, 7], '7': [0, 4, 7, 10], 'maj7': [0, 4, 7, 11], 'm7': [0, 3, 7, 10], 'sus4': [0, 5, 7],
    'sus2': [0, 2, 7], 'add9': [0, 4, 7, 14], 'madd9': [0, 3, 7, 14], '6': [0, 4, 7, 9], 'm6': [0, 3, 7, 9],
    'dim': [0, 3, 6], 'm7b5': [0, 3, 6, 10], '9': [0, 4, 7, 10, 14], 'maj9': [0, 4, 7, 11, 14], 'm9': [0, 3, 7, 10, 14],
    '7sus4': [0, 5, 7, 10], '5': [0, 7],
}
CH_RE = re.compile(r'^([A-G][#b]?)(maj9|maj7|madd9|m7b5|m9|m7|m6|7sus4|sus4|sus2|add9|dim|m|7|6|9|5)?(?:/([A-G][#b]?))?$')


@dataclass
class Chord:
    sym: str
    root: int          # pitch class
    tones: list[int]   # pitch classes, root first
    bass: int          # pitch class in the bass

    @staticmethod
    def of(sym: str) -> 'Chord':
        m = CH_RE.match(sym)
        if not m:
            raise ValueError(f'chord {sym!r}')
        r = PC[m.group(1)]
        iv = QUAL[m.group(2) or '']
        tones = [(r + i) % 12 for i in iv]
        b = PC[m.group(3)] if m.group(3) else r
        return Chord(sym, r, tones, b)


def pitches_in(pcs: list[int], lo: int, hi: int) -> list[int]:
    return [m for m in range(lo, hi + 1) if m % 12 in pcs]


def voice(ch: Chord, lo: int, hi: int, n: int = 3, prev: list[int] | None = None, top: int | None = None) -> list[int]:
    """Choose n notes of the chord within [lo, hi], moving as little as possible from `prev`."""
    pcs = list(dict.fromkeys(ch.tones))
    # which chord tones: always 3rd and 7th/colour; root and 5th as space allows
    want = pcs[:]
    if len(want) > n:
        drop = [t for t in want if (t - ch.root) % 12 == 7]           # drop the 5th first
        for d in drop:
            if len(want) > n:
                want.remove(d)
        while len(want) > n:
            want.pop(0 if want[0] != ch.root else -1)
    while len(want) < n:
        want.append(ch.root if ch.root not in want[-1:] else (ch.root + 7) % 12)
    import itertools
    opts = [pitches_in([pc], lo, hi) for pc in want]
    best, bc = None, 1e9
    target = prev if prev else None
    mid = (lo + hi) / 2
    for combo in itertools.product(*opts):
        v = sorted(combo)
        if len(set(v)) < len(v):
            continue
        gaps = [b - a for a, b in zip(v, v[1:])]
        if any(g > 9 for g in gaps):
            continue
        cost = 0.0
        if target and len(target) == len(v):
            cost += sum(abs(a - b) for a, b in zip(v, sorted(target)))
        else:
            cost += abs(sum(v) / len(v) - mid) * 1.5
        cost += sum(0.8 for g in gaps if g == 1) + sum(0.3 for g in gaps if g == 2)
        if top is not None:
            cost += abs(v[-1] - top) * 0.7
        if cost < bc:
            best, bc = v, cost
    if best is None:
        best = sorted(pitches_in(want, lo, hi)[:n])
    return best


def bass_note(ch: Chord, lo: int, hi: int, prev: int | None = None) -> int:
    opts = pitches_in([ch.bass], lo, hi)
    if not opts:
        opts = pitches_in([ch.bass], lo - 12, hi + 12)
    if prev is None:
        return opts[len(opts) // 2] if len(opts) > 1 else opts[0]
    return min(opts, key=lambda m: (abs(m - prev), m))


MAJOR = [0, 2, 4, 5, 7, 9, 11]
MINOR = [0, 2, 3, 5, 7, 8, 10]


# ---------------------------------------------------------------------------------------------------------- cue/score
@dataclass
class Note:
    t: float
    inst: str
    midi: int
    vel: float
    dur: float


@dataclass
class Bar:
    t0: float          # seconds from cue start
    beat: float        # seconds per beat
    beats: int         # beats per bar
    chord: Chord       # chord at the bar's start
    chords: list[tuple[float, Chord]]   # (beat offset, chord) changes inside the bar
    i: int             # bar number inside the segment
    n: int             # bars in the segment
    seg: 'Segment'
    final: bool = False
    span: float = 0.0  # seconds until the next bar (the final bar: until the end of the cue)

    def at(self, b: float) -> float:
        return self.t0 + b * self.beat

    def chord_at(self, b: float) -> Chord:
        c = self.chords[0][1]
        for off, ch in self.chords:
            if off <= b + 1e-6:
                c = ch
        return c


@dataclass
class Segment:
    start: float
    bpm: float
    prog: list[str]
    layers: list
    beats: int = 4
    chord_beats: float = 4
    snap: bool = True
    end: float = 0.0
    name: str = ''
    rest: bool = False


class Cue:
    """One piece of music, `length` seconds long. Add segments in time order; render() returns the notes."""

    def __init__(self, name: str, length: float, seed: int = 1):
        self.name, self.length, self.segs = name, length, []
        self.rng = np.random.default_rng(seed)
        self.end_chord: str | None = None
        self.end_layers: list = []
        self.extra: list[Note] = []

    def seg(self, start: float, bpm: float, prog: list[str], layers: list, beats: int = 4, chord_beats: float = 4,
            snap: bool = True, name: str = '', rest: bool = False) -> 'Cue':
        self.segs.append(Segment(start, bpm, prog, layers, beats, chord_beats, snap, name=name, rest=rest))
        return self

    def ending(self, chord: str, layers: list) -> 'Cue':
        """The last bar: one held chord (the cadence) instead of the pattern."""
        self.end_chord, self.end_layers = chord, layers
        return self

    def plan(self) -> list[Bar]:
        bars: list[Bar] = []
        segs = self.segs
        # 1) snap segment starts to the running bar grid; 2) stretch the last segment's tempo (max ~5%) so the cue's
        # end lands on a bar line.
        for k, s in enumerate(segs):
            if k == 0:
                s.start = 0.0 if s.start < 0.5 else s.start
                continue
            p = segs[k - 1]
            if s.snap and not p.rest:
                bl = p.beats * 60 / p.bpm
                nb = max(1, round((s.start - p.start) / bl))
                s.start = p.start + nb * bl
        for k, s in enumerate(segs):
            s.end = segs[k + 1].start if k + 1 < len(segs) else self.length
        # No tempo stretching: the last segment fills whole bars and its final bar holds until the cue ends.
        for k, s in enumerate(segs):
            if s.rest:
                continue
            bl = s.beats * 60 / s.bpm
            beat = 60 / s.bpm
            span = s.end - s.start
            is_last = k == len(segs) - 1
            nxt_hard = k + 1 < len(segs) and (not segs[k + 1].snap or segs[k + 1].rest)
            if is_last:
                n = max(1, int(span / bl + 0.02))
            elif nxt_hard:
                n = max(1, math.ceil(span / bl - 0.02))        # notes past a hard start get cut there
            else:
                n = max(1, int(round(span / bl)))
            for i in range(n):
                t0 = s.start + i * bl
                chords = []
                for b in np.arange(0, s.beats, min(s.chord_beats, s.beats)):
                    gb = i * s.beats + b                         # global beat in the segment
                    idx = int(gb // s.chord_beats) % len(s.prog)
                    chords.append((float(b), Chord.of(s.prog[idx])))
                bar = Bar(t0, beat, s.beats, chords[0][1], chords, i, n, s, span=bl)
                if is_last and i == n - 1:
                    bar.span = self.length - t0
                bars.append(bar)
        if bars:
            bars[-1].span = self.length - bars[-1].t0
        if self.end_chord and bars:
            b = bars[-1]
            b.final = True
            b.chord = Chord.of(self.end_chord)
            b.chords = [(0.0, b.chord)]
        return bars

    def notes(self) -> list[Note]:
        out: list[Note] = []
        bars = self.plan()
        state: dict = {}
        for b in bars:
            layers = self.end_layers if b.final else b.seg.layers
            for L in layers:
                out += L(b, state, self.rng)
        out += self.extra
        # notes may not cross a hard segment start (a stop): cut them there
        hard = [s.start for s in self.segs if not s.snap or s.rest]
        res = []
        for nt in out:
            if nt.t >= self.length - 0.02:
                continue
            for h in hard:
                if nt.t < h - 0.01 < nt.t + nt.dur:
                    nt.dur = max(0.05, h - nt.t)
            res.append(nt)
        return res


# --------------------------------------------------------------------------------------------------------------- layers
def _h(rng, t, vel, tj=0.006, vj=0.05):
    return t + float(rng.normal(0, tj)), float(np.clip(vel + rng.normal(0, vj), 0.05, 1.0))


def arp(name='piano', pattern=(0, 1, 2, 3, 2, 1, 2, 3), step=0.5, lo=50, hi=74, vel=0.4, pedal=True, n=3, bass=True,
        accent=0.08, every=1):
    """Broken chord: pattern indexes [bass, voicing low..high]; one note every `step` beats."""
    def L(b: Bar, st, rng):
        if b.i % every:
            return []
        out = []
        steps = int(round(b.beats / step))
        for k in range(steps):
            off = k * step
            ch = b.chord_at(off)
            key = (name, 'arp', ch.sym)
            pv = st.get((name, 'arpv'))
            v = voice(ch, lo + 7, hi, n, pv)
            st[(name, 'arpv')] = v
            bn = bass_note(ch, lo - 12, lo + 4, st.get((name, 'arpb')))
            st[(name, 'arpb')] = bn
            pool = ([bn] if bass else []) + v
            m = pool[pattern[k % len(pattern)] % len(pool)]
            # pedal: hold until the chord changes or the bar ends
            if pedal:
                nxt = [o for o, _ in b.chords if o > off + 1e-6]
                d = (nxt[0] * b.beat if nxt else b.span) - off * b.beat
            else:
                d = step * b.beat * 0.9
            t, vv = _h(rng, b.at(off), vel + (accent if off % 2 == 0 else 0))
            out.append(Note(t, name, m, vv, d))
        return out
    return L


def block(name='piano', hits=((0, 4),), lo=55, hi=76, vel=0.35, n=3, roll=0.0, top=None):
    """Chords on given beats: hits = ((beat, length_in_beats), ...)."""
    def L(b: Bar, st, rng):
        out = []
        for off, ln in hits:
            ch = b.chord_at(off)
            v = voice(ch, lo, hi, n, st.get((name, 'blk')), top)
            st[(name, 'blk')] = v
            for j, m in enumerate(v):
                t, vv = _h(rng, b.at(off) + j * roll, vel)
                out.append(Note(t, name, m, vv, ln * b.beat))
        return out
    return L


def bass(name='vc_pizz', hits=((0, 1), (2, 1)), lo=36, hi=50, vel=0.5, fifth_on=()):
    """Bass line: chord root (or slash bass) on given beats; beats listed in fifth_on play the fifth."""
    def L(b: Bar, st, rng):
        out = []
        for off, ln in hits:
            ch = b.chord_at(off)
            bn = bass_note(ch, lo, hi, st.get((name, 'bass')))
            st[(name, 'bass')] = bn
            m = bn
            if off in fifth_on:
                m = bn + 7 if bn + 7 <= hi + 5 else bn - 5
            t, vv = _h(rng, b.at(off), vel)
            out.append(Note(t, name, m, vv, ln * b.beat))
        return out
    return L


def pad(name='violas', lo=55, hi=72, vel=0.35, n=3, top=None, every=1):
    """Held chord for each chord change (legato). `every`: re-voice only every N bars (longer held notes)."""
    def L(b: Bar, st, rng):
        out = []
        if b.i % every and not b.final:
            return []
        for j, (off, ch) in enumerate(b.chords):
            if j + 1 < len(b.chords):
                d = (b.chords[j + 1][0] - off) * b.beat
            else:
                d = (b.span if (every == 1 or b.final) else every * b.beats * b.beat) - off * b.beat
            v = voice(ch, lo, hi, n, st.get((name, 'pad')), top)
            st[(name, 'pad')] = v
            for m in v:
                t, vv = _h(rng, b.at(off), vel, tj=0.015, vj=0.03)
                out.append(Note(t, name, m, vv, d + 0.12))
        return out
    return L


def held_bass(name='cellos', lo=36, hi=50, vel=0.35, every=1):
    def L(b: Bar, st, rng):
        if b.i % every and not b.final:
            return []
        out = []
        for j, (off, ch) in enumerate(b.chords):
            if j + 1 < len(b.chords):
                d = (b.chords[j + 1][0] - off) * b.beat
            else:
                d = (b.span if (every == 1 or b.final) else every * b.beats * b.beat) - off * b.beat
            bn = bass_note(ch, lo, hi, st.get((name, 'hb')))
            st[(name, 'hb')] = bn
            t, vv = _h(rng, b.at(off), vel, tj=0.01, vj=0.03)
            out.append(Note(t, name, bn, vv, d + 0.12))
        return out
    return L


def ostinato(name='marimba', pattern=(0, 2, 1, 2), step=0.5, lo=60, hi=79, vel=0.35, n=3, dur=0.9, accent=0.1,
             skip=()):
    """Repeating plucked/struck figure on chord tones (no bass): pattern indexes the voicing low..high."""
    def L(b: Bar, st, rng):
        out = []
        steps = int(round(b.beats / step))
        for k in range(steps):
            if k in skip:
                continue
            off = k * step
            ch = b.chord_at(off)
            v = voice(ch, lo, hi, n, st.get((name, 'ost')))
            st[(name, 'ost')] = v
            m = v[pattern[k % len(pattern)] % len(v)]
            t, vv = _h(rng, b.at(off), vel + (accent if abs(off - round(off)) < 1e-6 else 0))
            out.append(Note(t, name, m, vv, step * b.beat * dur))
        return out
    return L


def sparkle(name='glock', beats=(0,), every=2, lo=79, hi=96, vel=0.3, phase=0):
    """A single high chord tone on given beats, every N bars."""
    def L(b: Bar, st, rng):
        if (b.i + phase) % every:
            return []
        out = []
        for off in beats:
            ch = b.chord_at(off)
            opts = pitches_in(ch.tones, lo, hi)
            prev = st.get((name, 'sp'), opts[len(opts) // 2])
            m = min(opts, key=lambda x: (abs(x - prev) if abs(x - prev) > 0 else 99))
            st[(name, 'sp')] = m
            t, vv = _h(rng, b.at(off), vel)
            out.append(Note(t, name, m, vv, 1.0))
        return out
    return L


def roll(name='harp', lo=48, hi=84, step=0.07, vel=0.35, every=1, on=(0,), down=False):
    """Harp-style rolled chord: chord tones upward through the range, fast."""
    def L(b: Bar, st, rng):
        if b.i % every and not b.final:
            return []
        out = []
        for off in on:
            ch = b.chord_at(off)
            ps = pitches_in(list(dict.fromkeys(ch.tones)), lo, hi)
            if down:
                ps = ps[::-1]
            for j, m in enumerate(ps):
                t, vv = _h(rng, b.at(off) + j * step, vel - 0.1 * j / max(1, len(ps)), tj=0.004)
                out.append(Note(t, name, m, vv, 2.5))
        return out
    return L


def shaker(pattern='x.x.x.x.x.x.x.x.', vel=0.3, accent='x...x...x...x...', every=1):
    """16th-note shaker; 'x' = hit; accent pattern makes the beats a bit louder."""
    def L(b: Bar, st, rng):
        if b.i % every:
            return []
        out = []
        steps = len(pattern)
        for k, c in enumerate(pattern):
            if c != 'x':
                continue
            off = k * b.beats / steps
            a = accent[k % len(accent)] == 'x'
            t, vv = _h(rng, b.at(off), vel + (0.12 if a else -0.05), tj=0.004)
            out.append(Note(t, 'shaker', 60, vv, 0.2))
        return out
    return L


def melody(name, tonic: int, notes, bars: int, vel=0.4, start_bar=0, once=True, legato=1.0):
    """A tune: notes = [(bar, beat, semitones from tonic, length in beats, optional vel)], over `bars` bars.
    Plays from the segment's bar `start_bar` (repeats every `bars` bars unless once)."""
    def L(b: Bar, st, rng):
        k = b.i - start_bar
        if k < 0 or (once and k >= bars):
            return []
        k %= bars
        out = []
        for nt in notes:
            bar_i, beat, semi, ln = nt[:4]
            v = nt[4] if len(nt) > 4 else vel
            if bar_i != k:
                continue
            t, vv = _h(rng, b.at(beat), v, tj=0.008, vj=0.04)
            out.append(Note(t, name, tonic + semi, vv, ln * b.beat * legato))
        return out
    return L


def hold(name='piano', lo=50, hi=74, n=4, vel=0.35, roll=0.0, with_bass=True, blo=36, bhi=50, top=None, beat=0.0):
    """The final chord: held from `beat` until the end of the cue (rolled upward if roll > 0)."""
    def L(b: Bar, st, rng):
        ch = b.chord_at(beat)
        v = voice(ch, lo, hi, n, st.get((name, 'hold')), top)
        ps = ([bass_note(ch, blo, bhi)] if with_bass else []) + v
        d = b.span - beat * b.beat + 0.3
        out = []
        for j, m in enumerate(ps):
            t, vv = _h(rng, b.at(beat) + j * roll, vel, tj=0.004, vj=0.02)
            out.append(Note(t, name, m, vv, d))
        return out
    return L


def single(name, midi, beat=0.0, beats=None, vel=0.35):
    """One note at `beat` of the bar; beats=None holds it to the end of the bar (final bar: to the end of the cue)."""
    def L(b: Bar, st, rng):
        d = (beats * b.beat) if beats else (b.span - beat * b.beat + 0.3)
        t, vv = _h(rng, b.at(beat), vel, tj=0.004, vj=0.02)
        return [Note(t, name, midi, vv, d)]
    return L


def after(t: float, layer):
    """Use `layer` only in bars starting at or after second t (of the cue)."""
    def L(b: Bar, st, rng):
        return layer(b, st, rng) if b.t0 >= t - 0.35 else []
    return L


def before(t: float, layer):
    def L(b: Bar, st, rng):
        return layer(b, st, rng) if b.t0 < t - 0.35 else []
    return L


def only_bars(sel, layer):
    """Use `layer` only in the segment's bars where sel(i, n) is true (e.g. lambda i, n: i >= 4)."""
    def L(b: Bar, st, rng):
        return layer(b, st, rng) if sel(b.i, b.n) else []
    return L


def louder(f, layer):
    def L(b: Bar, st, rng):
        out = layer(b, st, rng)
        for x in out:
            x.vel = float(np.clip(x.vel * f, 0.03, 1))
        return out
    return L


def swell(layer, a=0.6, z=1.0):
    """Velocity ramps from a to z across the segment (crescendo / decrescendo)."""
    def L(b: Bar, st, rng):
        out = layer(b, st, rng)
        f = a + (z - a) * (b.i / max(1, b.n - 1))
        for x in out:
            x.vel = float(np.clip(x.vel * f, 0.03, 1))
        return out
    return L


# --------------------------------------------------------------------------------------------------------------- render
def impulse(rt60=2.0, pre=0.018, seed=7, damp=5500.0) -> np.ndarray:
    """A synthetic room: decaying stereo noise (different left/right), darker as it decays, plus early reflections."""
    rng = np.random.default_rng(seed)
    n = int((rt60 + 0.3) * SR)
    t = np.arange(n) / SR
    out = np.zeros((n, 2), np.float32)
    for c in range(2):
        x = rng.standard_normal(n).astype(np.float32)
        x *= np.exp(-6.9 * t / rt60).astype(np.float32)
        # darker tail: low-pass in the frequency domain, cutoff falling with time (two bands blended)
        X = np.fft.rfft(x)
        f = np.fft.rfftfreq(n, 1 / SR)
        lp = 1 / (1 + (f / damp) ** 2)
        dark = np.fft.irfft(X * lp, n).astype(np.float32)
        darker = np.fft.irfft(X * (1 / (1 + (f / (damp / 3)) ** 2)), n).astype(np.float32)
        w = np.clip(t / rt60, 0, 1).astype(np.float32)
        y = dark * (1 - w) + darker * w
        y[: int(pre * SR)] = 0
        for d, g in ((0.011, 0.5), (0.019, 0.35), (0.027, 0.3), (0.041, 0.22)):
            k = int((d + 0.002 * c) * SR)
            y[k] += g * (1 if (c + int(d * 1000)) % 2 else -1) * 3
        out[:, c] = y
    out /= np.sqrt(np.sum(out ** 2) / 2)
    return out


def convolve(x: np.ndarray, ir: np.ndarray, block: int = 1 << 17) -> np.ndarray:
    n, m = len(x), len(ir)
    N = 1 << (block + m - 1).bit_length()
    H = np.fft.rfft(ir, N, axis=0)
    y = np.zeros((n + m, 2), np.float32)
    for s in range(0, n, block):
        seg = x[s:s + block]
        Y = np.fft.irfft(np.fft.rfft(seg, N, axis=0) * H, N, axis=0)[: len(seg) + m - 1]
        y[s:s + len(Y)] += Y.astype(np.float32)
    return y[:n]


def loudness(x: np.ndarray) -> float:
    """Rough loudness in dB: RMS over 400 ms blocks, gated (ignores near-silence), with a gentle low cut weighting."""
    b = int(0.4 * SR)
    if len(x) < b:
        return -99.0
    k = len(x) // b
    blk = x[: k * b].reshape(k, b, 2)
    r = np.sqrt(np.mean(blk ** 2, axis=(1, 2)) + 1e-12)
    db = 20 * np.log10(r)
    g = db[db > db.max() - 20]
    return float(10 * np.log10(np.mean(10 ** (g / 10))))


def render(notes: list[Note], length: float, tail: float = 2.0, rt60: float = 2.0, target_db: float | None = -20.0,
           fade_out: float = 1.5) -> np.ndarray:
    n = int((length + tail) * SR)
    dry = np.zeros((n, 2), np.float32)
    wet = np.zeros((n, 2), np.float32)
    for nt in sorted(notes, key=lambda z: z.t):
        I = inst(nt.inst)
        if I.pitched and not (I.lo <= nt.midi <= I.hi):
            # out of the recorded range: move by octaves into it
            m = nt.midi
            while m < I.lo:
                m += 12
            while m > I.hi:
                m -= 12
            nt.midi = m
        y = I.note(nt.midi, nt.vel, nt.dur)
        s = max(0, int(nt.t * SR))
        e = min(n, s + len(y))
        if e <= s:
            continue
        dry[s:e] += y[: e - s]
        wet[s:e] += y[: e - s] * I.send
    room = convolve(wet, impulse(rt60))
    mix = dry + room * 0.9
    # end: fade over the last `fade_out` seconds of the tail
    if fade_out > 0:
        f = int(fade_out * SR)
        mix[n - f:] *= np.linspace(1, 0, f, dtype=np.float32)[:, None] ** 2
    if target_db is not None:
        mix *= 10 ** ((target_db - loudness(mix)) / 20)
    pk = float(np.max(np.abs(mix)))
    if pk > 0.89:                     # soft ceiling at about -1 dB
        over = np.abs(mix) > 0.7
        mix = np.where(over, np.sign(mix) * (0.7 + 0.19 * np.tanh((np.abs(mix) - 0.7) / 0.19)), mix)
    return mix
