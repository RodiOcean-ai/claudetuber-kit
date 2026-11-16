"""The in-house voice for a Short (14 Nov 2026): replaces the ElevenLabs takes. Owner, after five blind listening rounds:
"Lets use voice 1 method - its not perfect but it usable".
The method: Chatterbox reads each sentence copying the LIVELY sample (energy, emphasis; exaggeration 0.75, cfg 0.4), the
sentences are joined with short pauses, the whole read is voice-swapped (Chatterbox VC) to the CALM sample so it sounds like
the original speaker, and ClearerVoice rebuilds the highs at 48 kHz. Free and local. Never time-stretched.

Every graphics-card step goes through an optional turn-taking script (config voice_inhouse.gpu_turn; without one the steps
run directly, one at a time); the clean-up and the word check run on the processor (-CpuOnly). Writes <episode>/voice/inhouse/take<N>.wav (44.1 kHz mono, peak -1 dB) + take<N>.words.json, prints a
word check per take. With --use N it becomes voice/final_voice.wav (+ .words.json); an existing final voice is kept as
final_voice_before.wav first.

Text: the episode's voice_script.txt (sound-spellings like "Kahbee Lahmeh" are kept), mood tags like [calm] dropped, and
cut right after the locked script's last word, so there are no read-on words to trim (the loop word ends the read).
Usage: python -I -X utf8 voice_make.py <episode_dir> [--takes 2] [--use N] [--dry]"""
import argparse, difflib, json, os, re, shutil, subprocess, sys, wave

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import sfconfig
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
V = sfconfig.CFG['voice_inhouse']
FF = os.path.join(sfconfig.FFMPEG_DIR, 'ffmpeg')
norm = lambda w: re.sub(r"[^a-z0-9']", '', w.lower())


def read_text(ep):
    lock = open(os.path.join(ep, 'script_LOCKED.txt'), encoding='utf-8').read().strip()
    vs = os.path.join(ep, 'voice_script.txt')
    text = lock
    if os.path.exists(vs):
        m = re.search(r'^B01:\s*(.+)$', open(vs, encoding='utf-8').read(), re.M)
        if m:
            text = m.group(1)
    text = re.sub(r'\[[^\]]*\]\s*', '', text).strip()
    # stop at the locked script's last words (the voice script reads on into the first line for the loop)
    tail = [norm(w) for w in lock.split()[-3:]]
    words = text.split(); nw = [norm(w) for w in words]
    for i in range(len(nw) - len(tail), -1, -1):
        if nw[i:i + len(tail)] == tail:
            words = words[:i + len(tail)]
            break
    text = ' '.join(words).rstrip(',;')
    return re.split(r'(?<=[.!?])\s+', text), lock


def turn(name, cmd_lines, cpu=False, need=7):
    cmd = os.path.join(os.environ.get('TEMP', HERE), f'voice_make_{re.sub(r"[^a-z0-9]", "_", name.lower())}.cmd')
    with open(cmd, 'w', encoding='utf-8') as f:
        f.write('@echo off\r\n' + f'set "PATH={sfconfig.FFMPEG_DIR};%PATH%"\r\n' + '\r\n'.join(cmd_lines) + '\r\n')
    if not os.path.isfile(V.get('gpu_turn') or ''):      # no turn-taking script set: run the step directly
        r = subprocess.run(['cmd', '/c', cmd])
        if r.returncode:
            sys.exit(f'{name} failed (exit {r.returncode})')
        return
    args = ['powershell', '-NoProfile', '-ExecutionPolicy', 'Bypass', '-File', V['gpu_turn'], '-Name', name]
    args += ['-CpuOnly'] if cpu else ['-NeedGB', str(need)]
    r = subprocess.run(args + ['-Run', cmd])
    if r.returncode == 75:
        sys.exit('no turn on the graphics card after 30 minutes: tell the owner, or try again later')
    if r.returncode:
        sys.exit(f'{name} failed (exit {r.returncode})')


def load(p, sr=44100):
    raw = subprocess.run([FF, '-v', 'error', '-i', p, '-ac', '1', '-af', 'aresample=resampler=soxr', '-ar', str(sr), '-f', 'f32le', '-'],
                         capture_output=True, check=True).stdout
    return np.frombuffer(raw, np.float32).astype(np.float64)


def finish(src, dst, sr=44100):
    """Lead silence 0.03 s, tail 0.15 s, one fixed gain to a -1 dB peak (no compressor, no loudness change of the delivery)."""
    x = load(src, sr); n = int(0.01 * sr)
    e = np.array([np.sqrt((x[i:i + n] ** 2).mean()) for i in range(0, len(x) - n, n)])
    on = np.where(e > e.max() * 10 ** (-40 / 20))[0]
    a = max(0, on[0] * n - int(0.03 * sr)); b = min(len(x), (on[-1] + 1) * n + int(0.15 * sr))
    y = x[a:b] / max(1e-9, np.abs(x[a:b]).max()) * 10 ** (-1 / 20)
    with wave.open(dst, 'wb') as w:
        w.setnchannels(1); w.setsampwidth(2); w.setframerate(sr); w.writeframes((y * 32767).astype(np.int16).tobytes())
    return len(y) / sr


def main():
    ap = argparse.ArgumentParser(); ap.add_argument('episode'); ap.add_argument('--takes', type=int, default=2)
    ap.add_argument('--use', type=int); ap.add_argument('--dry', action='store_true')
    ap.add_argument('--lively', help='the sample to copy the delivery from (default: config voice_inhouse.lively)')
    ap.add_argument('--swap', action='store_true', help='voice-swap to the calm sample (owner heard it as a weird echo)')
    ap.add_argument('--finish', choices=['polish', 'sr'], default='polish',
                    help='polish = tone matched to the ElevenLabs takes (dry); sr = ClearerVoice highs (left a haze, heard as echo)')
    ap.add_argument('--name', default='inhouse', help='sub-folder of voice/ for these takes')
    ap.add_argument('--cfg', type=float, help='lower = slower, more deliberate read (default config)')
    ap.add_argument('--exaggeration', type=float, help='delivery strength (default config)')
    ap.add_argument('--pause', type=float, help='seconds between sentences (default config)')
    a = ap.parse_args()
    ep = os.path.abspath(a.episode); slug = os.path.basename(ep); out = os.path.join(ep, 'voice', a.name)
    if a.use:
        src = os.path.join(out, f'take{a.use}.wav'); fin = os.path.join(ep, 'voice', 'final_voice.wav')
        if os.path.exists(fin) and not os.path.exists(os.path.join(ep, 'voice', 'final_voice_before.wav')):
            shutil.copyfile(fin, os.path.join(ep, 'voice', 'final_voice_before.wav'))
            wj = os.path.join(ep, 'voice', 'final_voice.words.json')
            if os.path.exists(wj):
                shutil.copyfile(wj, os.path.join(ep, 'voice', 'final_voice_before.words.json'))
        shutil.copyfile(src, fin); shutil.copyfile(os.path.splitext(src)[0] + '.words.json', os.path.join(ep, 'voice', 'final_voice.words.json'))
        print(f'take {a.use} is now voice/final_voice.wav'); return
    sentences, lock = read_text(ep)
    print(f'{len(sentences)} sentences:'); [print('  ' + s) for s in sentences]
    if a.dry:
        return
    os.makedirs(out, exist_ok=True)
    job = {'sentences': sentences, 'lively': a.lively or V['lively'], 'calm': V['calm'], 'exaggeration': a.exaggeration if a.exaggeration is not None else V['exaggeration'],
           'cfg': a.cfg if a.cfg is not None else V['cfg'], 'pause': a.pause if a.pause is not None else V['pause'], 'takes': a.takes, 'swap': a.swap, 'out': out.replace('\\', '/')}
    jp = os.path.join(out, 'job.json'); json.dump(job, open(jp, 'w', encoding='utf-8'), indent=1, ensure_ascii=False)
    # 1. graphics card: the read (+ the voice swap only with --swap)
    turn(f'voice {slug}', [f'"{V["chatterbox_python"]}" "{HERE}\\voice_make_gpu.py" "{jp}"'])
    # 2. processor: the finish
    if a.finish == 'sr':
        pairs = ' '.join(f'"{out}\\take{k}_raw.wav" "{out}\\take{k}_sr48.wav"' for k in range(1, a.takes + 1))
        turn(f'voice clean-up {slug}', [f'set "CLEARVOICE_HOME={V["clearvoice_home"]}"', f'cd /d "{V["clearvoice_home"]}"',
                                        f'"{V["clearvoice_python"]}" "{HERE}\\voice_make_sr.py" {pairs}'], cpu=True)
        mid = 'sr48'
    else:                                                          # voice_polish.py: tone matched to the ElevenLabs takes
        pol = V.get('polish') or sys.exit('set voice_inhouse.polish in config.json to your voice-polish script, or use --finish sr')
        turn(f'voice polish {slug}', [f'"{sfconfig.CFG["python"]}" "{pol}" "{out}\\take{k}_raw.wav" "{out}\\take{k}_polish.wav"'
                                      for k in range(1, a.takes + 1)], cpu=True)
        mid = 'polish'
    # 3. finish each take
    takes = []
    for k in range(1, a.takes + 1):
        d = finish(os.path.join(out, f'take{k}_{mid}.wav'), os.path.join(out, f'take{k}.wav')); takes.append((k, d))
    # 4. processor: word times + check against the locked script
    turn(f'voice words {slug}', [f'"{sfconfig.CFG["python"]}" -X utf8 "{HERE}\\voice_make_words.py" '
                                 + ' '.join(f'"{out}\\take{k}.wav"' for k, _ in takes)], cpu=True)
    want = [norm(w) for w in ' '.join(sentences).split() if norm(w)]
    for k, d in takes:
        got = [norm(x['w']) for x in json.load(open(os.path.join(out, f'take{k}.words.json'), encoding='utf-8')) if norm(x['w'])]
        ratio = difflib.SequenceMatcher(None, want, got).ratio()
        last = got[-1] if got else ''
        print(f'take {k}: {d:.1f} s, {len(got) / d:.2f} words/s, words match {ratio * 100:.0f} %, last word "{last}"'
              + ('' if last == want[-1] else f'  << the script ends on "{want[-1]}"'))
    print(f'\nListen, then: python voice_make.py "{ep}" --use <take>')


if __name__ == '__main__':
    main()
