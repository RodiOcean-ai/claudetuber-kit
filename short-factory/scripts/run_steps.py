"""Run a list of program steps one after another, each as an argument list (no shell, so nothing inside a path or a
name is ever treated as a command). Used by voice_make.py, directly or inside one turn of a turn-taking script.
Usage: python -I run_steps.py <job.json>
job.json: {"path": "<folder put first on PATH, e.g. ffmpeg>", "steps": [{"args": [...], "cwd": "...", "env": {...}}, ...]}
Stops at the first step that fails and exits with its code. Standard library only."""
import json, os, subprocess, sys


def run(job):
    env = dict(os.environ)
    if job.get('path'):
        env['PATH'] = job['path'] + os.pathsep + env.get('PATH', '')
    for step in job['steps']:
        args = step['args']
        if not isinstance(args, list) or not all(isinstance(x, str) for x in args):
            print('run_steps: a step must be a list of strings', file=sys.stderr)
            return 2
        r = subprocess.run(args, cwd=step.get('cwd') or None, env={**env, **step.get('env', {})})
        if r.returncode:
            return r.returncode
    return 0


if __name__ == '__main__':
    if len(sys.argv) != 2:
        sys.exit(__doc__)
    sys.exit(run(json.load(open(sys.argv[1], encoding='utf-8'))))
