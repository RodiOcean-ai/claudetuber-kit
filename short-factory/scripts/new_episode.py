"""Scaffold a new episode folder from the plugin templates.
Usage: python -I new_episode.py <slug> [--title "..."] [--subject <channel key>] [--root <episodes_root>] [--no-tracker]
Makes <episodes_root>/<slug>/ with voice/, takes/, blender/ (common.py, sf_world.py, world.py), edit/ (Remotion template,
shared node_modules link, swish sounds, render.sh), post/, JOURNEY.md and facts.md, and adds the episode to the tracker.
Never overwrites: an existing folder is refused. The slug may hold only lowercase letters, digits, "-" and "_"."""
import argparse, datetime as dt, os, shutil, sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import sfconfig  # noqa: E402


def fill(src, dst, **kw):
    s = open(src, encoding='utf-8').read()
    for k, v in kw.items():
        s = s.replace('{' + k + '}', v or '')
    open(dst, 'w', encoding='utf-8').write(s)


def link_node_modules(edit):
    target = os.path.realpath(sfconfig.CFG['edit_node_modules']); link = os.path.join(edit, 'node_modules')
    if not os.path.isdir(target):
        print('  NOTE: shared node_modules not found; run "npm install" inside edit/'); return
    try:                                                   # plain Python, no shell: nothing in a path is ever run
        if os.name == 'nt':
            import _winapi                                 # a directory junction: no admin rights needed, no copy
            _winapi.CreateJunction(target, link)
        else:
            os.symlink(target, link, target_is_directory=True)
    except OSError as e:
        print('  NOTE: could not link node_modules:', str(e)[:200])


def main():
    ap = argparse.ArgumentParser(); ap.add_argument('slug'); ap.add_argument('--title', default=''); ap.add_argument('--subject', default='')
    ap.add_argument('--root', default=sfconfig.CFG['episodes_root']); ap.add_argument('--no-tracker', action='store_true')
    a = ap.parse_args()
    a.slug = sfconfig.safe_name(a.slug, 'episode slug')
    ep = sfconfig.inside(a.root, a.slug)                  # always a folder directly inside the episodes folder
    if os.path.exists(ep):
        sys.exit(f'refused: {ep} already exists')
    T = sfconfig.TEMPLATES; today = dt.date.today().isoformat()
    for d in ('voice', 'takes', 'blender/render', 'post', 'edit/out', 'edit/public/clips', 'edit/public/audio'):
        os.makedirs(os.path.join(ep, d), exist_ok=True)
    for f in ('common.py', 'sf_world.py', 'world.py'):
        shutil.copy(os.path.join(T, 'blender', f), os.path.join(ep, 'blender', f))
    shutil.copytree(os.path.join(T, 'edit'), os.path.join(ep, 'edit'), dirs_exist_ok=True,
                    ignore=shutil.ignore_patterns('node_modules', 'out'))     # node_modules is linked below, not copied
    for i in (1, 2, 3):
        shutil.copy(os.path.join(sfconfig.ASSETS, 'sfx', f'swish{i}.wav'), os.path.join(ep, 'edit', 'public', 'audio', f'swish{i}.wav'))
    link_node_modules(os.path.join(ep, 'edit'))
    kw = dict(SLUG=a.slug, TITLE=a.title or a.slug, SUBJECT=a.subject or '?', DATE=today)
    fill(os.path.join(T, 'episode', 'JOURNEY.md'), os.path.join(ep, 'JOURNEY.md'), **kw)
    fill(os.path.join(T, 'episode', 'facts.md'), os.path.join(ep, 'facts.md'), **kw)
    if not a.no_tracker:
        import tracker
        wb = tracker.book()
        tracker.upsert(wb['Episodes'], ['slug'], {'slug': a.slug, 'title': a.title, 'subject channel': a.subject, 'status': 'idea',
                                                  'folder': ep, 'created': today})
        tracker.save(wb)
    print('episode ready:', ep)
    print('  next: script_LOCKED.txt -> voice/final_voice.wav + .words.json -> blender/world.py -> captions.py -> music_pick.py')


if __name__ == '__main__':
    main()
