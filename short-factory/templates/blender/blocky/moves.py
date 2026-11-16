"""Moves bank for blocky characters: each move is a function of time that returns only the joints it controls; animate()
plays a timeline of moves on a character, blends each change over BLEND seconds, walks the body along its facing,
keeps the feet on the ground (unless the move flies or lies down) and keys every frame.
Timeline: [(start_s, 'walk', {'turn': 90, 'speed': 2.2}), (2.4, 'stand+wave', {'turn': 60}), ...]
'a+b' layers move b's arms and head over move a's legs (e.g. 'sit+cry', 'walk+talk').
Joints: shLf/shLs, shRf/shRs (shoulder forward/sideways, deg), hipL/hipR (forward, deg), headX (nod), headY (tilt), headZ (look),
twist (torso), lean (body, + forward), roll (body onto its side), lift (extra height), tail / tailup (wag, raise; animals),
air (True: don't pin feet to the ground).
Animals (animals.py) have their own banks: QUAD (dog, cat, rabbit) and BIRD (pigeon); a move they lack falls back to 'stand'."""
import math
import bpy
from common import FPS

BLEND = 0.25
LEG, TOE = 1.0, 0.27                      # hip height and half the shoe length (scale 1)
REST = dict(shLf=0, shLs=4, shRf=0, shRs=4, hipL=0, hipR=0, headX=0, headY=0, headZ=0, twist=0, lean=0, roll=0, lift=0, tail=0, tailup=0,
            solve=0, floor=0)                     # solve: an airborne move that still keeps every body part above the ground;
                                                  # floor: ... but the ground may only push it up, never pull it down
W = lambda hz, t, ph=0: math.sin(2 * math.pi * hz * t + ph)
ss = lambda u: 0 if u <= 0 else 1 if u >= 1 else u * u * (3 - 2 * u)
ARMS_HEAD = ('shLf', 'shLs', 'shRf', 'shRs', 'headX', 'headY', 'headZ', 'twist', 'tail', 'tailup')


def stand(t, o):
    return dict(shLs=4 + 1.5 * W(0.3, t), shRs=4 + 1.5 * W(0.3, t), headX=1.5 * W(0.31, t, 1), lift=0.008 * W(0.3, t))


def walk(t, o):
    a = o.get('stride', 30); p = W(o.get('hz', 1.1), t)
    return dict(hipL=a * p, hipR=-a * p, shLf=-a * p, shRf=a * p, shLs=5, shRs=5, headX=1.2 * W(2.2, t), speed=o.get('speed', 2.2))


def run(t, o):
    a = o.get('stride', 45); p = W(o.get('hz', 1.7), t)
    return dict(hipL=a * p, hipR=-a * p, shLf=-55 * p, shRf=55 * p, shLs=8, shRs=8, lean=10, headX=-4,
                lift=0.1 * abs(W(o.get('hz', 1.7), t, math.pi / 2)), speed=o.get('speed', 5.0))


def wave(t, o):
    return dict(shRf=8, shRs=150 + 14 * W(2.2, t), headY=-6 * W(1.1, t), headZ=4)


def point(t, o):
    return dict(shRf=88, shRs=2, lean=-3, headX=-3)


def talk(t, o):
    return dict(shRf=22 + 14 * W(0.9, t), shRs=10, shLf=12 + 10 * W(0.7, t, 1), shLs=8, headX=4 * W(1.3, t), headZ=5 * W(0.4, t))


def shrug(t, o):
    k = ss(t / 0.25)
    return dict(shLf=35 * k, shLs=40 * k, shRf=35 * k, shRs=40 * k, headY=10 * k, headX=-4 * k)


def jump(t, o):
    """Jump in shock: a quick hop with both arms flung up."""
    u = min(t / o.get('dur', 0.55), 1.0); k = ss(t / 0.12)
    return dict(lift=o.get('height', 0.6) * 4 * u * (1 - u), shLs=125 * k, shRs=125 * k, shLf=15 * k, shRf=15 * k, headX=-8 * k,
                hipL=10 * k * (1 - u), hipR=-6 * k * (1 - u), air=True)


def fall(t, o):
    """Slip and fall flat on the back; a small bounce, arms flung out."""
    u = min(t / 0.45, 1.0); g = u * u
    bounce = 6 * math.exp(-9 * max(t - 0.45, 0)) * math.sin(14 * max(t - 0.45, 0))
    return dict(lean=-(88 * g) + bounce, lift=0.3 * ss((t - 0.25) / 0.2), shLf=150 * ss(t / 0.3), shRf=150 * ss(t / 0.3),
                shLs=30, shRs=30, hipL=25 * ss(t / 0.3), hipR=10 * ss(t / 0.3), headX=-10, air=True)


def cry(t, o):
    sob = 0.012 * W(3.0, t)
    return dict(shLf=125, shLs=-12, shRf=125, shRs=-12, headX=14 + 3 * W(3.0, t), lift=sob)


def sit(t, o):
    """Sit on a seat of height o['seat'] (0 = the ground): legs straight forward."""
    return dict(hipL=88, hipR=88, shLf=20, shRf=20, shLs=6, shRs=6, lift=-(LEG - 0.25 - o.get('seat', 0.0)), air=True)


def laugh(t, o):
    return dict(lean=-6 + 3 * W(4.0, t), headX=-10 + 4 * W(4.0, t), shLf=30, shRf=30, shLs=-10, shRs=-10)


def show(t, o):
    """Hold something up beside the face with the right hand (toast, bread): the arm rises and stays.
    'rise 0' starts with the arm already up (14 Nov 2026: a Short's first frame must match its last for the loop; the
    cleaning kid's arm rose over the first 0.25 s, so the loop jumped from shirt-up to arms-down. Owner: "This is not the
    first frame of the video")."""
    r = o.get('rise', 0.25)
    k = 1.0 if r <= 0 else ss(t / r)
    return dict(shRf=125 * k, shRs=8, headY=-4 * k, headZ=4 * k)


def carry(t, o):
    """Hold something in front of the chest with the right hand."""
    k = ss(t / 0.2)
    return dict(shRf=55 * k, shRs=6)


def yell(t, o):
    """Both arms thrown up and shaking, head forward: a telling-off."""
    k = ss(t / 0.15)
    return dict(shLs=135 * k + 8 * W(5.0, t), shRs=135 * k + 8 * W(5.0, t, 1), shLf=15 * k, shRf=15 * k, headX=8 * k + 3 * W(5.0, t), lean=4 * k)


def press(t, o):
    """Reach forward with the left hand and push something down (a toaster lever): reach for 0.4 s, press, stay."""
    reach = ss(t / 0.35); down = ss((t - 0.4) / 0.18)
    return dict(shLf=62 * reach - 18 * down, shLs=-6 * reach, headX=10 * reach, lean=6 * reach)


def duel(t, o):
    """A spatula duel: the right arm slashes up and down fast, the body bobs."""
    return dict(shRf=75 + 45 * W(2.6, t, o.get('ph', 0)), shRs=10, shLf=20, shLs=20, lean=4 * W(2.6, t, o.get('ph', 0)), headX=-4)


def splat(t, o):
    """Pip's signature fall (owner, 5 Nov 2026: our running gag, like a recurring character who always falls). Always the same
    1.6 s so viewers learn it: a stumble with windmilling arms, a flat faceplant with a slide, both legs kick up behind,
    then the head lifts, dazed (the scene adds circling stars). Starts from a walk or from standing."""
    trip = ss(t / 0.3); u = ss((t - 0.25) / 0.3); hit = max(t - 0.55, 0.0)
    spin = 2 * math.pi * 2.6 * t
    arms = 1 - ss((t - 0.25) / 0.25)                                         # windmill, then both arms flung forward
    bounce = 7 * math.exp(-10 * hit) * math.sin(16 * hit) if t > 0.55 else 0
    kick = ss((t - 0.6) / 0.18) * (1 - ss((t - 1.05) / 0.3))
    daze = ss((t - 1.05) / 0.3)
    return dict(lean=18 * trip + 72 * u * u + bounce, lift=0.12 * math.sin(math.pi * min(t / 0.3, 1.0)) * (1 - u) + 0.37 * u,
                shLf=(90 + 80 * math.sin(spin)) * arms + 170 * (1 - arms), shRf=(90 - 80 * math.sin(spin)) * arms + 170 * (1 - arms),
                shLs=30 * arms + 14, shRs=30 * arms + 14,
                hipL=20 * trip * (1 - u) - 70 * kick - 8 * daze, hipR=-35 * trip * (1 - u) - 50 * kick - 4 * daze,
                headX=-8 * trip - 28 * daze, headY=9 * daze * W(1.6, t), speed=o.get('speed', 2.2) * (1 - ss(t / 0.75)), air=True)


def type_(t, o):
    """Typing like mad: both forearms forward over a desk, hands hammering in turn, head down at the screen."""
    return dict(shLf=52 + 9 * W(6.0, t), shRf=52 + 9 * W(6.0, t, math.pi), shLs=8, shRs=8, headX=10 + 2 * W(3.0, t), lean=5)


# ---- athletic moves for the cleaning race (13 Nov 2026, owner: like the real speed-cleaning Short: slides, dives, a flat-out sprint)
def sprint(t, o):
    """Flat out: long fast strides, a deep forward lean, arms pumping hard (8.5 units a second, run is 5)."""
    a = o.get('stride', 62); hz = o.get('hz', 2.6); p = W(hz, t)
    return dict(hipL=a * p, hipR=-a * p, shLf=-80 * p, shRf=80 * p, shLs=10, shRs=10, lean=20, headX=-8,
                lift=0.14 * abs(W(hz, t, math.pi / 2)), speed=o.get('speed', 8.5))


def slide(t, o):
    """A feet-first slide (like a baseball slide): drops onto the backside, legs out in front, arms flung up and out, and skids
    forward along its facing, slowing to a stop over 0.75 s ('speed' at the start, default 7)."""
    k = ss(t / 0.15); stop = ss(t / 0.75)
    return dict(hipL=84 * k, hipR=74 * k, lean=-12 * k, lift=-(LEG - 0.3) * k, shLs=70 * k, shRs=100 * k, shLf=35 * k, shRf=-5 * k,
                headX=-12 * k, headY=6 * k, speed=o.get('speed', 7.0) * (1 - stop), air=True)


def dive(t, o):
    """A superman dive: a spring forward, flat in the air with both arms reaching ahead, a belly landing on 'land' (the height of
    the floor or a table top, default 0) and a skid that stops over 0.9 s ('speed', default 6)."""
    fly = min(t / 0.42, 1.0); flat = ss(t / 0.22); land = o.get('land', 0.0); hit = max(t - 0.42, 0.0)
    arc = (0.55 + land) * math.sin(math.pi * fly * 0.5) if t < 0.42 else land + 0.05 * math.exp(-9 * hit) * math.sin(18 * hit)
    return dict(lean=86 * flat, lift=0.37 * flat + arc, shLf=172 * flat, shRf=168 * flat, shLs=12, shRs=12, hipL=-8 * flat,
                hipR=-14 * flat, headX=-35 * flat, speed=o.get('speed', 6.0) * (1 - ss(hit / 0.9)), air=True)


def scoop(t, o):
    """Grabbing things at top speed: bent over, both arms sweeping forward and back in turn, head down at the job."""
    return dict(lean=36, shLf=95 + 50 * W(4.2, t), shRf=95 + 50 * W(4.2, t, math.pi), shLs=12, shRs=12, headX=18, hipL=-8, hipR=8)


MOVES = dict(stand=stand, walk=walk, run=run, wave=wave, point=point, talk=talk, shrug=shrug, jump=jump, fall=fall, cry=cry, sit=sit,
             laugh=laugh, show=show, carry=carry, yell=yell, press=press, duel=duel, splat=splat, type=type_,
             sprint=sprint, slide=slide, dive=dive, scoop=scoop,
             bonk=fall, smack=fall, trip=splat)          # people who bump into something just fall


# ---------------------------------------------------------------- animals (owner, 5 Nov 2026)
# Four legs: the front legs swing like arms (shLf/shRf), the back legs like hips; a walk is a trot (diagonal pairs together).
def q_stand(t, o):
    return dict(tail=14 * W(1.3, t), tailup=12, headX=2 * W(0.4, t), headY=3 * W(0.23, t), lift=0.005 * W(0.6, t))


def q_walk(t, o):
    a = o.get('stride', 28); p = W(o.get('hz', 2.4), t)
    return dict(hipL=a * p, hipR=-a * p, shLf=-a * p, shRf=a * p, tail=20 * W(2.4, t), tailup=18, headX=2.5 * W(4.8, t), speed=o.get('speed', 2.2))


def q_run(t, o):
    """A bounding run: front legs together, back legs together, the body rocking."""
    hz = o.get('hz', 3.2); p = W(hz, t)
    return dict(shLf=40 * p, shRf=36 * p, hipL=-40 * p, hipR=-36 * p, lean=6 * W(hz, t, math.pi / 2), lift=0.1 * abs(W(hz, t)),
                tail=8 * W(hz, t), tailup=32, headX=-4, speed=o.get('speed', 5.0))


def q_jump(t, o):
    u = min(t / o.get('dur', 0.5), 1.0); k = ss(t / 0.1)
    return dict(lift=o.get('height', 0.7) * 4 * u * (1 - u), shLf=45 * k * (1 - u), shRf=45 * k * (1 - u), hipL=-40 * k * (1 - u),
                hipR=-40 * k * (1 - u), tailup=40 * k, headX=-10 * k, air=True)


def q_sit(t, o):
    k = ss(t / 0.3)
    return dict(lean=-18 * k, hipL=78 * k, hipR=78 * k, shLf=-18 * k, shRf=-18 * k, headX=14 * k, tail=10 * W(1.0, t), tailup=-25 * k)


def q_fall(t, o):
    """Flops over onto its side, legs out, and twitches."""
    k = ss(t / 0.35); tw = 10 * math.exp(-2.5 * max(t - 0.35, 0)) * W(7, t)
    return dict(roll=90 * k, lift=0.42 * k, shLf=12 * k + tw, shRf=-8 * k - tw, hipL=-10 * k - tw, hipR=10 * k + tw, headX=-8 * k,
                tail=0, tailup=-20 * k, air=True)


def q_splat(t, o):
    """Ginger's signature fall (owner, 5 Nov 2026: our running gag is a ginger cat that never lands on its feet). Always the
    same 1.6 s: a butt-wiggle, a proud pounce, chin first into the ground with the back end up and the tail swishing, then it
    topples onto its side, legs stiff, and the scene adds the circling stars."""
    u = min(max((t - 0.2) / 0.42, 0.0), 1.0); fly = 0.2 < t < 0.62
    land = ss((t - 0.62) / 0.1); top = ss((t - 0.95) / 0.3); tw = 9 * math.exp(-3 * max(t - 1.25, 0)) * W(8, t) * top
    if t <= 0.2:                                                             # the wiggle before the pounce
        lean, legs, hips, twist = 0, 0, 0, 7 * W(6, t) * ss(t / 0.06)
    elif fly:                                                                # the pounce: nose up, then down; legs stretched
        g = ss(u / 0.25); lean, legs, hips, twist = (-15 + 75 * u) * g, 75 * g, -55 * g, 0
    else:                                                                    # chin first, back end up, then over onto its side
        lean, legs, hips, twist = 60 * (1 - top), (-25 + 100 * (1 - land)) * (1 - top), (15 - 70 * (1 - land)) * (1 - top), 0
    return dict(lean=lean, roll=90 * top, twist=twist, lift=(1.3 * 4 * u * (1 - u) if fly else 0) + 0.42 * top,
                shLf=legs + 12 * top + tw, shRf=legs - 8 * top - tw, hipL=hips - 10 * top - tw, hipR=hips + 10 * top + tw,
                headX=10 * (1 - u) - 12 * top, tail=30 * W(4, t) * (t > 0.62) * (1 - top), tailup=60 * (1 - top) - 20 * top,
                speed=o.get('speed', 4.0) * (1 if fly else (1 - ss((t - 0.62) / 0.3)) if t >= 0.62 else 0),
                solve=1 - top, floor=1 if fly else 0, air=True)     # in the air the ground only pushes up (no paw through the street)


# Ginger's bump-and-fall gags (owner, 10 Nov 2026: "I want the cat to bump something and then fall", like the format benchmark's girl on the
# bicycle). The scene's 'bump <thing>' starts them at the moment she reaches the thing. Her middle's height c is planned and the
# lift worked out from it, so she tumbles round her own middle instead of round her feet: lift = c - CZ cos(lean) cos(roll).
CZ, SIDE = 0.78, 0.42                    # a cat's middle above the ground standing, and lying on its side (scale 1)


def _mid(c, lean, roll):
    return c - CZ * math.cos(math.radians(lean)) * math.cos(math.radians(roll))


def q_bonk(t, o):
    """Runs head first into something (a crate, a post): stops dead (the scene squashes her and shakes the thing), is thrown
    back with her front paws up, flips onto her side and lies there twitching (the scene adds the stars). t = 0 at the hit."""
    hit = ss(t / 0.08); u = min(max((t - 0.1) / 0.45, 0.0), 1.0); land = ss((t - 0.5) / 0.22)
    fly = ss((t - 0.05) / 0.1) * (1 - land); tw = 9 * math.exp(-3 * max(t - 0.75, 0)) * W(8, t) * land
    lean = (-14 * hit - 46 * ss((t - 0.1) / 0.3)) * (1 - land)
    roll = 90 * ss((t - 0.35) / 0.37)
    c = CZ + (SIDE - CZ) * ss((t - 0.4) / 0.3) + 0.7 * math.sin(math.pi * u) + 0.05 * math.exp(-8 * max(t - 0.72, 0)) * abs(math.sin(14 * max(t - 0.72, 0))) * (t > 0.72)
    return dict(lean=lean, roll=roll, lift=_mid(c, lean, roll),
                shLf=(70 + 25 * W(6, t)) * fly + 12 * land + tw, shRf=(70 - 25 * W(6, t, 1)) * fly - 8 * land - tw,
                hipL=-25 * fly - 10 * land - tw, hipR=-15 * fly + 10 * land + tw,
                headX=-22 * hit * (1 - land) - 12 * land, tail=0, tailup=55 * (1 - land) - 20 * land,
                speed=-3.4 * (t > 0.1) * (1 - ss((t - 0.1) / 0.6)), air=True)


def q_smack(t, o):
    """Pounces at a fish in a tank (t = 0 at the take-off): flies o['reach'] (scale 1) in 0.3 s, hits the glass, hangs there
    spread out for a beat, drops, lands on her side (the scene adds the stars)."""
    D = o.get('reach', 1.6); u = min(t / 0.3, 1.0); flying = t < 0.3; hang = 0.3 <= t < 0.6
    g = max(t - 0.6, 0.0) / 0.26; drop = min(g, 1.0); land = ss((t - 0.8) / 0.12)
    tw = 9 * math.exp(-3 * max(t - 0.95, 0)) * W(8, t) * land
    if flying:
        c = CZ + 0.8 * math.sin(math.pi / 2 * u); lean = -18 + 24 * u; legs, hips = 75 * ss(u / 0.3), -55 * ss(u / 0.3); head = 10 * (1 - u)
    elif hang:                                                            # stuck to the glass, paws spread, a small slide down
        c = CZ + 0.8 - 0.06 * (t - 0.3) / 0.3; lean = 6; legs, hips = 100 + 5 * W(11, t), -62; head = -14
    else:                                                                 # falls off the glass onto her side
        c = (CZ + 0.74) - (CZ + 0.74 - SIDE) * drop * drop + 0.05 * math.exp(-8 * max(t - 0.86, 0)) * abs(math.sin(14 * max(t - 0.86, 0))) * (t > 0.86)
        lean = 6 - 26 * ss(drop / 0.6) * (1 - land); legs, hips = (100 * (1 - land) + 12 * land), (-62 * (1 - land) - 10 * land); head = -12
    roll = 90 * ss((t - 0.68) / 0.22)
    return dict(lean=lean, roll=roll, lift=_mid(c, lean, roll), shLf=legs + tw, shRf=legs * (0.92 if hang else 1) - tw,
                hipL=hips - tw, hipR=hips + tw, headX=head, tail=30 * W(4, t) * (1 - land), tailup=40 * (1 - land) - 20 * land,
                speed=(D / 0.3) if flying else (-0.9 if t > 0.6 and t < 0.85 else 0.0), air=True)


def q_trip(t, o):
    """Her front paws catch on something low (a hose) mid-run (t = 0 there): she pitches over in a full somersault, lands on her
    side and lies there twitching (the scene adds the stars)."""
    snag = ss(t / 0.1); flip = ss((t - 0.06) / 0.5); land = ss((t - 0.5) / 0.18); v = min(max((t - 0.06) / 0.52, 0.0), 1.0)
    tw = 9 * math.exp(-3 * max(t - 0.75, 0)) * W(8, t) * land
    lean = 360 * flip + 20 * snag * (1 - flip)
    roll = 90 * ss((t - 0.42) / 0.26)
    c = CZ + (SIDE - CZ) * ss((t - 0.4) / 0.28) + 0.95 * math.sin(math.pi * v) + 0.05 * math.exp(-8 * max(t - 0.7, 0)) * abs(math.sin(14 * max(t - 0.7, 0))) * (t > 0.7)
    tuck = math.sin(math.pi * v)
    return dict(lean=lean, roll=roll, lift=_mid(c, lean, roll), shLf=-35 * snag * (1 - flip) + 70 * tuck + 12 * land + tw,
                shRf=-30 * snag * (1 - flip) + 60 * tuck - 8 * land - tw, hipL=-60 * tuck - 10 * land - tw, hipR=-50 * tuck + 10 * land + tw,
                headX=18 * tuck - 12 * land, tail=0, tailup=50 * tuck - 20 * land,
                speed=4.6 * (1 - ss(t / 0.62)), air=True)


def q_talk(t, o):
    """Barking or meowing: quick head nods, wagging (the says column flaps the mouth)."""
    return dict(headX=-9 * abs(W(2.6, t)), tail=22 * W(3.0, t), tailup=25, lift=0.02 * abs(W(2.6, t)))


def q_wave(t, o):
    """A paw raised and shaken (shake hands / hello)."""
    k = ss(t / 0.2)
    return dict(shRf=(70 + 12 * W(2.4, t)) * k, lean=-6 * k, headY=-8 * k, tail=28 * W(3.2, t), tailup=30)


def q_happy(t, o):
    return dict(lift=0.1 * abs(W(2.4, t)), tail=32 * W(4.0, t), tailup=35, headX=-6, headY=6 * W(1.2, t), air=True)


def q_sad(t, o):
    k = ss(t / 0.3)
    return dict(headX=22 * k, tail=4 * W(0.6, t), tailup=-35 * k, lean=3 * k)


QUAD = dict(stand=q_stand, walk=q_walk, run=q_run, jump=q_jump, sit=q_sit, fall=q_fall, talk=q_talk, wave=q_wave, laugh=q_happy,
            cry=q_sad, yell=q_talk, splat=q_splat, bonk=q_bonk, smack=q_smack, trip=q_trip)
GAG_LAND = dict(bonk=0.72, smack=0.9, trip=0.68, splat=0.7)    # when each fall has landed (s after it starts): the stars begin
GAG_HIT = dict(bonk=0.0, smack=0.3, trip=0.0)                     # when it hits the thing (s after it starts)


# Birds stand on two legs like people; wings are the arms. A pigeon's walk pumps its head; 'fly' takes off and flaps.
def b_walk(t, o):
    a = o.get('stride', 34); hz = o.get('hz', 2.6); p = W(hz, t)
    return dict(hipL=a * p, hipR=-a * p, shLs=6, shRs=6, headX=14 * W(2 * hz, t), lean=4, tailup=5 * W(2 * hz, t), speed=o.get('speed', 2.2))


def b_flap(t, o):
    """A startled flutter: hops up flapping both wings."""
    u = min(t / o.get('dur', 0.7), 1.0); f = 65 + 60 * W(7, t)
    return dict(lift=o.get('height', 0.5) * 4 * u * (1 - u), shLs=f, shRs=f, headX=-6, tailup=20, air=True)


def b_fly(t, o):
    """Takes off and flies up and away (forward along its facing) for the rest of the scene."""
    f = 70 + 65 * W(6, t); k = ss(t / 0.4)
    return dict(lift=o.get('height', 4.0) * ss(t / 1.6) + 0.3 * k, shLs=f, shRs=f, lean=12 * k, hipL=-30 * k, hipR=-30 * k, tailup=15,
                speed=o.get('speed', 3.0) * k, air=True)


def b_sit(t, o):
    k = ss(t / 0.3)
    return dict(hipL=90 * k, hipR=90 * k, lift=-0.36 * k, headX=4 * W(0.4, t), air=True)


def b_wave(t, o):
    return dict(shRs=110 + 30 * W(5, t), headY=-6, tailup=10)


BIRD = dict(MOVES, walk=b_walk, run=b_walk, jump=b_flap, fly=b_fly, sit=b_sit, wave=b_wave, splat=b_flap)
BANKS = {'quad': QUAD, 'bird': BIRD}


def sample(name, t, o, kind=None):
    """Pose for move 'a' or 'a+b' at time t since it started: REST, then a, then b's arms and head on top.
    kind: 'quad' or 'bird' picks that animal bank (a move it lacks becomes 'stand')."""
    p = dict(REST); air = False; speed = 0.0; bank = BANKS.get(kind, MOVES)
    for i, part in enumerate(name.split('+')):
        d = (bank.get(part) or bank['stand'] if kind else MOVES[part])(t, o)
        air = air or d.pop('air', False); speed = d.pop('speed', speed) if i == 0 else speed; d.pop('speed', None)
        p.update(d if i == 0 else {k: v for k, v in d.items() if k in ARMS_HEAD})
    return p, air, speed


def ground_lift(p, R=None):
    """Height to add so the lowest shoe corner touches the ground (legs swing on the hip). R: per-character leg length (birds)
    or, for four legs, the contact points (paws and the body's bottom corners, which a sitting dog rests on)."""
    if R and R.get('kind') == 'quad':
        return quad_ground(p, R['contacts'])
    leg, toe = (R.get('leg', LEG), R.get('toe', TOE)) if R else (LEG, TOE)
    low = max(leg * math.cos(math.radians(a)) + toe * abs(math.sin(math.radians(a))) for a in (p['hipL'], p['hipR']))
    return low - leg + toe * abs(math.sin(math.radians(p['lean'])))   # a lean tips the toes (or heels) down


def quad_ground(p, c):
    """Four legs: every paw's front and back bottom corner and the body's bottom corners, turned by the body's lean (in the
    side view, y forward-back, z up); returns how much to lift so the lowest touches the ground."""
    rad = math.radians; ln = rad(p['lean']); pts = list(c['body'])
    for py, a in ((c['front'], p['shLf']), (c['front'], p['shRf']), (c['back'], p['hipL']), (c['back'], p['hipR'])):
        a = rad(a); fy, fz = py - c['leg'] * math.sin(a), c['hip'] - c['leg'] * math.cos(a)
        pts += [(fy + d * math.cos(a), fz - d * math.sin(a)) for d in c['toe']]
    return -min(y * math.sin(ln) + z * math.cos(ln) for y, z in pts)


def animate(R, timeline, t_end, start=None):
    """Keys R's joints every frame from the timeline. start = (x, y) where the feet begin; turn (deg) in each step's options."""
    rad = math.radians; s = R.get('scale', 1.0)
    tl, last = [], 0.0
    for t0, name, o in sorted(timeline, key=lambda e: e[0]):  # each step keeps the facing of the one before unless it sets its own
        last = o.get('turn', last); tl.append((t0, name, {**o, 'turn': last}))
    x, y = start if start else R['base'][:2]
    prefs = bpy.context.preferences.edit; old = prefs.keyframe_new_interpolation_type; prefs.keyframe_new_interpolation_type = 'LINEAR'
    prev_turn = tl[0][2]['turn']
    frames = []
    for f in range(1, round(t_end * FPS) + 2):
        t = (f - 1) / FPS
        i = max(k for k, e in enumerate(tl) if e[0] <= t) if t >= tl[0][0] else 0
        t0, name, o = tl[i]
        p, air, speed = sample(name, t - t0, o, R.get('kind')); turn = o.get('turn', prev_turn); own = speed
        bl = o.get('blend', BLEND)                            # a bump stops dead: its move blends in almost at once
        if i > 0 and t - t0 < bl:                             # blend from the previous move into this one
            pt0, pname, po = tl[i - 1]; q, qair, qspeed = sample(pname, t - pt0, po, R.get('kind')); w = ss((t - t0) / bl)
            p = {k: q[k] + (p[k] - q[k]) * w for k in p}; speed = qspeed + (speed - qspeed) * w
            pturn = po.get('turn', turn); turn = pturn + (turn - pturn) * ss((t - t0) / o.get('turn_time', BLEND))
            air = air and qair
        elif i > 0 and 'turn_time' in o:
            pturn = tl[i - 1][2].get('turn', turn); turn = pturn + (turn - pturn) * ss((t - t0) / o['turn_time'])
        # a sprint 'to' a spot (o['dest']) steers straight at it and never overshoots, also while it blends into the next move
        # (13 Nov 2026: at 8.5 units a second the speed ramps threw each stop about a metre off and the errors piled up)
        if 'dest' in o:
            goal = o['dest']
        elif i > 0 and t - t0 < bl and 'dest' in tl[i - 1][2] and own == 0:   # a slide or dive after it keeps its momentum
            goal = tl[i - 1][2]['dest']
        else:
            goal = None
        if goal is not None:
            gx, gy = goal[0] - x, goal[1] - y; gd = math.hypot(gx, gy); step = min(speed * s / FPS, gd)
            if gd > 1e-4:
                if 'dest' in o and gd > 0.05:
                    turn = math.degrees(math.atan2(gx, -gy))
                x += gx / gd * step; y += gy / gd * step
        else:
            x += math.sin(rad(turn)) * speed * s / FPS; y += -math.cos(rad(turn)) * speed * s / FPS
        free = air and p['solve'] < 1e-3                       # a free jump or fall: no ground solve, and it must not lift its neighbours
        gl = None if free else ground_lift(p, R) * (1.0 if not air else p['solve'])
        frames.append((f, p, turn, x, y, max(gl, 0.0) if gl is not None and p['floor'] > 0.5 else gl))
        R.setdefault('air', {})[f] = air or p['lift'] > 0.02    # the feet check lets these frames leave the ground
    # Pinning the feet exactly makes the body shiver (it rises and drops ~3 cm four times a step). Smooth it instead:
    # a moving max (never lets a foot sink) then a shorter moving average (a gentle bob, still never below the max).
    g = [fr[5] for fr in frames]; n = len(g); rmax, ravg = (2, 2) if R.get('kind') else (5, 3)   # animals: a tighter window (sitting down and up)
    near = lambda arr, k, r: [v for v in arr[max(0, k - r):k + r + 1] if v is not None]
    gmax = [None if g[k] is None else max(near(g, k, rmax)) for k in range(n)]
    gs = [0.0 if g[k] is None else sum(near(gmax, k, ravg)) / len(near(gmax, k, ravg)) for k in range(n)]
    R['track'] = {}                                             # (x, y, z, turn) per frame, for the camera bank and the checks
    for (f, p, turn, x, y, _), ground in zip(frames, gs):
        lift = p['lift'] + ground
        R['track'][f] = (x, y, R['base'][2] + lift * s, turn)
        R['root'].location = (x, y, R['base'][2] + lift * s); R['root'].rotation_euler = (rad(p['lean']), rad(p['roll']), rad(turn))
        R['shL'].rotation_euler = (rad(-p['shLf']), rad(p['shLs']), 0); R['shR'].rotation_euler = (rad(-p['shRf']), rad(-p['shRs']), 0)
        R['hipL'].rotation_euler = (rad(-p['hipL']), 0, 0); R['hipR'].rotation_euler = (rad(-p['hipR']), 0, 0)
        R['neck'].rotation_euler = (rad(p['headX']), rad(p['headY']), rad(p['headZ'])); R['torso'].rotation_euler = (0, 0, rad(p['twist']))
        for ob, path in ((R['root'], 'location'), (R['root'], 'rotation_euler'), (R['shL'], 'rotation_euler'), (R['shR'], 'rotation_euler'),
                         (R['hipL'], 'rotation_euler'), (R['hipR'], 'rotation_euler'), (R['neck'], 'rotation_euler'), (R['torso'], 'rotation_euler')):
            ob.keyframe_insert(path, frame=f)
        if R.get('tail'):
            R['tail'].rotation_euler = (rad(p['tailup']), 0, rad(p['tail'])); R['tail'].keyframe_insert('rotation_euler', frame=f)
    prefs.keyframe_new_interpolation_type = old


def feet_check(chars, frames, grounded_only=True, tol=0.04):
    """The 'feet on the ground' check: lowest shoe point per frame. Reports frames below the ground (always wrong) and,
    for moves that should stand, frames floating above it. chars: [(R, [(t0, t1) windows where it may leave the ground])]."""
    from mathutils import Vector
    sc = bpy.context.scene; report = {}
    for f in range(1, frames + 1, 2):
        sc.frame_set(f); dg = bpy.context.evaluated_depsgraph_get(); t = (f - 1) / FPS
        for R, free in chars:
            low = min((o.evaluated_get(dg).matrix_world @ Vector(c)).z for o in R['feet'] for c in o.evaluated_get(dg).bound_box)
            airborne = any(a <= t <= b for a, b in free)
            if low < -tol or (not airborne and low > tol):
                report.setdefault(R['name'], []).append((f, round(low, 3)))
    for R, _ in chars:
        bad = report.get(R['name'], [])
        print('FEET', R['name'], ':', 'clear' if not bad else f'{len(bad)} frames off, first {bad[:5]}')
    return report
