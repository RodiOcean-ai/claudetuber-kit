"""Shared settings for every short-factory script: read config.json once, expose paths, put ffmpeg on PATH."""
import json, os, re, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CFG = json.load(open(os.path.join(ROOT, 'config.json'), encoding='utf-8'))
if os.path.isdir(CFG.get('home', '')) and os.path.normcase(os.path.abspath(CFG['home'])) != os.path.normcase(ROOT):
    ROOT = CFG['home']                     # running from Claude's installed copy: read and write the master folder (tracker, reference)
    CFG = json.load(open(os.path.join(ROOT, 'config.json'), encoding='utf-8'))
FFMPEG_DIR = CFG['ffmpeg_dir']
if os.path.isdir(FFMPEG_DIR) and FFMPEG_DIR not in os.environ.get('PATH', ''):
    os.environ['PATH'] = FFMPEG_DIR + os.pathsep + os.environ.get('PATH', '')
if os.path.isdir(CFG.get('pylib', '')) and CFG['pylib'] not in sys.path:
    sys.path.append(CFG['pylib'])          # transformers / openpyxl live here, not in the venv
FONTS = CFG['fonts']
TRACKER = os.path.join(ROOT, CFG['tracker'])
ASSETS = os.path.join(ROOT, 'assets')
TEMPLATES = os.path.join(ROOT, 'templates')
REFERENCE = os.path.join(ROOT, 'reference')


SAFE_NAME = re.compile(r'^[a-z0-9][a-z0-9_-]{0,63}$')     # episode slugs, channel keys, folder names typed on the command line
VIDEO_ID = re.compile(r'^[A-Za-z0-9_-]{6,20}$')            # a YouTube video id (used as a file name)


def safe_name(value, what='name'):
    """Allow only a short plain name (lowercase letters, digits, "-" and "_"; 1-64 characters, starting with a letter or
    digit), so a typed name can never climb out of its folder or carry shell characters. Stops with a clear message."""
    v = '' if value is None else str(value)
    if not SAFE_NAME.match(v):
        sys.exit(f'refused {what} {v!r}: use 1-64 characters - lowercase letters, digits, "-" or "_" - starting with a '
                 f'letter or digit (for example: space-facts or ep_07)')
    return v


def inside(root, *parts):
    """root joined with parts, resolved (links and "..") and checked to stay inside root; stops otherwise."""
    base = os.path.realpath(root)
    full = os.path.realpath(os.path.join(base, *parts))
    try:
        ok = os.path.normcase(os.path.commonpath([base, full])) == os.path.normcase(base) and full != base
    except ValueError:                                     # another drive
        ok = False
    if not ok:
        sys.exit(f'refused: {os.path.join(*parts) if parts else full!r} would land outside {base}')
    return full


def study_dir(channel):
    """Folder of a channel study: a legacy folder if we have one, else studies_root/<channel>."""
    key = safe_name(str(channel).strip().lower().lstrip('@'), 'channel key')
    if key in CFG.get('legacy_studies', {}):
        return CFG['legacy_studies'][key]
    return inside(CFG['studies_root'], key)
