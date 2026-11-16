"""EPISODE world: ONE bright Blender world and ONE continuous camera, timed to the approved voice (short-factory template).

Edit the four marked parts and nothing else first:
  1. CUES      word times from the voice (T.at('but'), T.at('but', after=40) for a later one)
  2. SET       stations along x (camera looks toward +y); faceless toy figures only, never a real person's likeness
  3. SHOTS     the shot table: (start, end, cam_from, cam_to, look_from, look_to, lift of the whip INTO this hold)
               every hold <= 4 s; the camera settles back into frame one after the last hold (the loop)
  4. CHECKS    the check list: pairs that must never pass through each other

Switches (environment variables): CHECK=1 overlap pass only | STILLS=1,120,300 several stills | OUTLINE=1 cartoon outline
| FRAME_START/FRAME_END part render.  Run through blender_tools.py (check / stills / render), not by hand.
A full worked example is reference/creators/light-study/world_example.py (8 trick shots, physics, reveal, loop)."""
import math, os, sys
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.append(HERE)
import bpy
from common import *
from sf_world import *

T = timing(os.path.join(HERE, '..', 'voice', 'final_voice.words.json'))

# ---------------------------------------------------------------- 1. CUES
T_BUT = T.at('but')                      # the "But..." twist: the first big whip lands here
T_END = T.end

OUT, STILL = args()
sc = reset(T.frames)
world(top='#5aa8ff', horizon='#eaf5ff', strength=1.3)
floor(color='#dcecff')
sun()

# ---------------------------------------------------------------- 2. SET (station A at x=0, station B at x=14)
WOOD = mat('Wood', hexrgb('#c98a4b'), rough=0.5)
TOY = mat('Toy', hexrgb('#ffb020'), rough=0.35, coat=0.6)
BALL = mat('Ball', hexrgb('#ff3b4f'), rough=0.3, coat=1.0)

table = box((0, 0, 0.375), (1.6, 0.9, 0.75), WOOD)
bottle = make_bottle('Bottle', (0, 0, 0.75))
flip(bottle, (0, 0, 0.75), -0.3)                      # already mid-flip on frame one ...
flip(bottle, (0, 0, 0.75), T.loop - 0.3)              # ... and the same flip again, so the last frame flows into frame one

kid = figure('Kid', (14, 0.4, 0), 1.2, TOY, arm_up=True)
ball = sphere((15.0, 0.2, 2.2), 0.12, BALL)
ball.keyframe_insert('location', frame=1)            # held by its keys until released, then physics takes over
bake_physics(dynamic=[(ball, T_BUT + 0.3, 'SPHERE', 0.6, 300)], passive=[(bpy.data.objects['Floor'], 'BOX', 0.5)], frames=T.frames)

# ---------------------------------------------------------------- 3. SHOTS (drifting holds joined by whips)
SHOTS = [                                # demo: 2 holds only; a real episode covers the whole voice with holds of 4 s or less
    (0.0, T_BUT - 0.35, (0.0, -3.2, 1.35), (0.0, -2.6, 1.25), (0, 0, 0.95), (0, 0, 0.95), 0.0),
    (T_BUT, min(T_BUT + 3.6, T_END - 1.2), (14, -4.2, 1.6), (14, -3.6, 1.4), (14, 0.3, 1.1), (14, 0.3, 1.0), 1.2),
]
cam, target, whips = camera_rig(SHOTS, T.frames, T.loop)

# ---------------------------------------------------------------- 4. CHECKS
CHECKS = [('ball vs kid', [ball], kids(kid)), ('bottle vs table', kids(bottle), [table])]

if os.environ.get('OUTLINE'):
    add_outline()
finish(OUT, STILL, T, whips, checks=CHECKS, per_frame=lambda scene, *a: pose_bottles((scene.frame_current - 1) / FPS))
