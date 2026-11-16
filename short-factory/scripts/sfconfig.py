"""Shared settings for every short-factory script: read config.json once, expose paths, put ffmpeg on PATH."""
import json, os, sys

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


def study_dir(channel):
    """Folder of a channel study: a legacy folder if we have one, else studies_root/<channel>."""
    key = channel.lower().lstrip('@')
    if key in CFG.get('legacy_studies', {}):
        return CFG['legacy_studies'][key]
    return os.path.join(CFG['studies_root'], key)
