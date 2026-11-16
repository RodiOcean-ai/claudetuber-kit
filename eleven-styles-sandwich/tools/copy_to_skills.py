"""Copy the reusable code of this project into the short-factory skills (reference files), so the skills (and the free kit
built from them) carry working examples. Run after the owner approves a style; re-run when a style changes.
Usage: py -3.13 tools/copy_to_skills.py [style-skill ...]      (no argument = the base skill + every approved style)"""
import json, os, shutil, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SKILLS = os.path.join(os.path.dirname(ROOT), 'short-factory', 'skills')
BASE = {
    'shared/timing.ts': 'src/shared/timing.ts', 'shared/anim.ts': 'src/shared/anim.ts', 'shared/Soundtrack.tsx': 'src/shared/Soundtrack.tsx',
    'shared/fonts.ts': 'src/shared/fonts.ts', 'shared/three-shapes.ts': 'src/shared/three/shapes.ts', 'shared/styles.tsx': 'src/styles.tsx',
    'shared/Root.tsx': 'src/Root.tsx', 'review/serve.py': 'review/serve.py', 'review/ReviewApp.tsx': 'review/ReviewApp.tsx',
    'review/index.html': 'review/index.html', 'tools/make_voice3.py': 'tools/make_voice3.py', 'tools/clearvoice_sr.py': 'tools/clearvoice_sr.py',
    'tools/words.py': 'tools/words.py', 'tools/assemble_voice.py': 'tools/assemble_voice.py', 'tools/timing.py': 'tools/timing.py',
    'tools/sfx.py': 'tools/sfx.py', 'tools/render.py': 'tools/render.py', 'tools/srt.py': 'tools/srt.py', 'tools/contact.py': 'tools/contact.py',
    'tools/grab_cut.py': 'tools/grab_cut.py', 'tools/key_cutout.py': 'tools/key_cutout.py', 'tools/paper_border.py': 'tools/paper_border.py',
    'tools/wb_trace.py': 'tools/wb_trace.py', 'tools/wb_fill.py': 'tools/wb_fill.py', 'package.json': 'package.json', 'remotion.config.ts': 'remotion.config.ts',
}
STYLES = {
    'S01-KineticTypography': ('explainer-kinetic-typography', 'src/styles/s01_kinetic/Kinetic.tsx'),
    'S02-MotionGraphics': ('explainer-motion-graphics', 'src/styles/s02_motion/MotionGraphics.tsx'),
    'S03-Screencast': ('explainer-screencast', 'src/styles/s03_screencast/Screencast.tsx'),
    'S04-Isometric': ('explainer-isometric', 'src/styles/s04_isometric/Isometric.tsx'),
    'S05-Whiteboard': ('explainer-whiteboard', 'src/styles/s05_whiteboard/Whiteboard.tsx'),
    'S06-Comic': ('explainer-comic', 'src/styles/s06_comic/Comic.tsx'),
    'S07-TwoPointFiveD': ('explainer-2-5d', 'src/styles/s07_25d/TwoPointFiveD.tsx'),
    'S08-Collage': ('explainer-collage', 'src/styles/s08_collage/Collage.tsx'),
    'S09-CharacterStory': ('explainer-2d-character', 'src/styles/s09_character/CharacterStory.tsx'),
    'S10-ThreeD': ('explainer-3d-animation', 'src/styles/s10_3d/ThreeD.tsx'),
    'S11-StopMotion': ('explainer-stop-motion', 'src/styles/s11_stopmotion/StopMotion.tsx'),
}
# the three.js tests of 14 Nov 2026 (no picture maker): copied into the same style's skill once approved
VARIANTS = {
    'T05-WhiteboardThreeJS': ('explainer-whiteboard', {'Whiteboard3D.tsx': 'src/styles/t05_whiteboard3d/Whiteboard3D.tsx',
        'three-lineart.ts': 'src/shared/three/lineart.ts', 'three-toon.ts': 'src/shared/three/toon.ts', 'three-sandwichGeo.ts': 'src/shared/three/sandwichGeo.ts'}),
    'T06-ComicThreeJS': ('explainer-comic', {'Comic3D.tsx': 'src/styles/t06_comic3d/Comic3D.tsx',
        'three-toon.ts': 'src/shared/three/toon.ts', 'three-sandwichGeo.ts': 'src/shared/three/sandwichGeo.ts'}),
}


def copy(dst_dir, mapping):
    for rel, src in mapping.items():
        d = os.path.join(dst_dir, 'reference', rel)
        os.makedirs(os.path.dirname(d), exist_ok=True)
        shutil.copyfile(os.path.join(ROOT, src), d)


def approved():
    notes = json.load(open(os.path.join(ROOT, 'review', 'notes.json'), encoding='utf-8'))
    builds = json.load(open(os.path.join(ROOT, 'review', 'builds.json'), encoding='utf-8'))
    return [s for s in list(STYLES) + list(VARIANTS) if any(a['style'] == s and a['build'] == builds.get(s, {}).get('label') for a in notes['approvals'])]


if __name__ == '__main__':
    want = sys.argv[1:]
    copy(os.path.join(SKILLS, 'explainer-styles'), BASE)
    print('explainer-styles: base reference copied')
    for s in approved():
        if s in VARIANTS:
            name, files = VARIANTS[s]
        else:
            name, src = STYLES[s]
            files = {os.path.basename(src): src}
        if want and name not in want:
            continue
        copy(os.path.join(SKILLS, name), files)
        print(f'{name}: {", ".join(files)} copied')
