"""Run the picture helper's prompt lists (assets_work/p25/gen1.sh, assets_work/collage/gen1.sh) through make-picture.py,
without needing bash on the PATH (the traffic light runs commands through cmd.exe).
Usage (inside one traffic-light turn): py -3.13 assets_work/gen_rest.py [p25] [collage]"""
import os, re, shlex, subprocess, sys, time

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MP = os.environ.get('MAKE_PICTURE', r'<your-picture-maker>/make-picture.py')   # your local picture script
os.chdir(ROOT)
which = sys.argv[1:] or ['p25', 'collage']
for name in which:
    if not re.fullmatch(r'[a-z0-9][a-z0-9_-]{0,63}', name):      # a folder name inside assets_work, nothing else
        sys.exit(f'refused batch name {name!r}: use a folder name like p25 or collage')
    path = f'assets_work/{name}/gen1.sh'
    var = {}
    t0 = time.time()
    for line in open(path, encoding='utf-8'):
        line = line.strip()
        if not line or line.startswith('#'):
            continue
        m = re.match(r'^([A-Z]+)=(.*)$', line)
        if m:  # NAME="value" or NAME=value
            v = m.group(2)
            v = shlex.split(v)[0] if v.startswith('"') else v
            for k, val in var.items():
                v = v.replace('$' + k, val)
            var[m.group(1)] = v
            continue
        if line.startswith('$MP'):
            for k in sorted(var, key=len, reverse=True):
                if k != 'MP':
                    line = line.replace('$' + k, var[k])
            args = shlex.split(line[len('$MP'):])
            print(f"{time.strftime('%H:%M:%S')} {args[1]}", flush=True)
            subprocess.run([sys.executable, MP, *args], check=False)
    print(f'{name} done in {time.time() - t0:.0f} s', flush=True)
