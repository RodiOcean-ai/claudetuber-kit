"""Scene table -> blocky 3D scene. A Short is written as a markdown table; this builds the places, the cast, their moves,
faces and lip flaps, the camera (a bank of framings joined by quick flights), runs the checks and renders.

Run: blender -b --factory-startup --python scene.py -- <scene.md> <out_dir>
     env MODE = check (checks only) | preview (half size, fast) | stills (STILLS=1,40,...) | full (default)
         SHOTS=3,5 re-renders only those shots (camera rows; check mode lists each shot's frames) into the same folder.
         RANGE=1-180 renders only that stretch of frames; scripts/render_parallel.py splits a scene into stretches and renders
         them at the same time (12 Nov 2026: one Blender uses a fraction of the graphics card, so several run side by side).
         SAMPLES=n, RT=0|1 override the full-quality settings (for speed tests).
         LOOK=premium switches on the high-end look (premium.py; a look test, 12 Nov 2026): Cycles on the graphics card, glossy
         toy plastic, real metal and glass, a reflective floor and a gradient backdrop in the void, key / rim / fill light and
         depth of field that follows the shot. LOOK=chess is its bolder second round (the chess Short's recipe): glossy
         navy-and-white marble tiles, a dusk sky in the void, a low warm key and a strong cool rim, AgX 'Punchy'.
         Without LOOK nothing changes.
     Use absolute paths: Blender treats a relative output folder as relative to the drive root.

The underwater lab (RodiOcean, 10 Nov 2026): place 'lab' with 'light: underwater' and 'screen: <picture or video file>' (what the
huge screen behind the cast shows; spots left, centre, right, presenter, screen_left; NO radar there, owner's rule).
The lab's things and the channel's name on them (lab_dressing.py): 'dress: crates, buoy, sub' (default; also tank, hose) and
'logo: buoy' (which ONE carries the name; owner: one per Short; without the line each scene file picks its own; floor,
pedestal; none). Ginger's bump gags: where 'bump crates' (or buoy,
tank, hose) on her run row: she runs in from her side, hits the thing and falls (moves bonk, smack, trip), the thing reacts.
The void (12 Nov 2026): place 'void' is an endless floor and backdrop in one flat colour ('void: #9ad8f5' changes it; write
'light: day'; it brings its own soft light), centred on 0 0, spots left, centre, right, far_left, far_right (1.35 apart in a
shallow V, the middle in front), back_left, back_mid, back_right (3 behind left, centre, right); made to be the only place of a
scene (never together with the street).
The file: optional lines 'length: 15', 'light: day|golden|night|underwater', 'screen: <file>', 'void: #hex' and 'hero: {"top": "#1d1d24", ...}' (this episode's restyle
of the hero, as JSON overrides of its cast.json recipe), then one table:
| at | who | do | face | where | says |
- at: seconds from the start.
- who: 'place' (do = street | classroom | bedroom | kitchen | office | shop | lab | void; where 'no chairs; no bowl' clears the kitchen table), 'camera' (do = a framing, where = who to frame),
  or a cast name (hero, mayor, teacher, kid, inspector, mom, pip, grandpa, grandma, scientist, guard, chef, boss, fan; animals: dog,
  cat, rabbit, squirrel, pigeon). A character in another place is a separate copy of them. Copies 'fan#2', 'dog#2' ... take the recipe's
  next 'variant' (another outfit or coat), so a crowd or two dogs never look the same.
- do: a move from the moves bank ('walk', 'stand+wave', 'sit+cry', ...; 13 Nov 2026 also sprint, slide, dive (options 'speed N',
  'land H' = a table top), scoop); blank keeps the current move (a new face or words). Camera framings: wide, medium, close, two_shot,
  ots (over the shoulder of the first at the second), low, push_in, top (13 Nov 2026: straight down from above, a dollhouse
  view; the picture's long side runs along x, so a 12-wide room fits; the room's ceiling is hidden for it; frame a 'mark' prop
  with 'size N': the camera sits 7 x N above the floor, size 1.3 shows most of a room, 0.6 one corner).
- face: an expression from the face bank (calm, happy, angry, ...). Blank keeps the last one.
- where: tokens separated by ';' - a spot of the place (left, seat_0_0 ...), 'from X Y', 'to <spot>' (walk or run there),
  'turn N', 'face <who>', 'seat N'.
- The mystery hero: a 'reveal' in the hero's do (e.g. 'reveal+wave') shows the hero as the mystery figure (shadow, glowing '?')
  until that moment, then he pops out in a burst of sparks. 'mystery: yes' with no reveal keeps him hidden all scene.
- says: the words the character says from 'at' (mouth flaps; with a real voice the word times come from the voice file).
- More 'where' tokens for people: 'at X Y Z' (an exact spot, e.g. on a table or inside a toaster), 'to X Y', 'only A-B' (shown only
  from A to B seconds), 'away A-B' (hidden from A to B; works on the mystery hero too). Two copies of one cast member: 'tinychef#2'.
- Props (props.py): who = '@name'. Its first row's do is the kind (toaster, bread, toast, cloche, pasta, ice, card, frames,
  bulb, spatula, mark = an invisible camera target) with where 'at X Y Z; turn N', or 'size N' (framing scale), or 'hold <who>; until T; tilt N; left' to sit in someone's hand. Later rows
  do an action: toaster pop | take (slot N) | empty | glow (off T) | load; cloche lift; card rise; bulb on; frames grow;
  any prop hide | show. A camera row can frame a prop by its '@name' (close, medium, low, push_in).
- Story props (props_story.py, 12 Nov 2026; nothing on them is written, they are all shapes):
  satellite: glow | dim | squash | float (up N) | flash.     cash: slide (to X Y Z).     maze, cage (tall N; radius N): static.
  shark: circle (around X Y; radius R; height Z; for S; speed REVS; back = the other way round).
  bubble (first row: icon squirrel | shark | scammer | satellite): orbit (around X Y Z; radius R; speed REVS_PER_S; phase DEG) |
  stop | flare | fade.     magnifier: 'hold <who>' like toast (with the move 'show' and 'tilt 125', or 'carry' and 'tilt 55').
  Every option of an action row reaches the prop as numbers, e.g. '| 4.0 | @cash | slide | | to 1.5 0 2.0 | |'.
- Ginger's signature fall (our running gag, owner 5 Nov 2026): '| 3.0 | ginger | splat | shocked | | |' - a ginger cat that never
  lands on its feet: a pounce, chin first into the ground, topples onto its side, stars circling. Always the same 1.6 s.
  People can do 'splat' too (a stumble and a faceplant). Animals: walk, run, jump, sit, fall,
  talk (bark), wave (a paw), laugh (happy bounce), cry (sad); a pigeon also 'fly' (takes off and away) and 'jump' (a startled flutter)."""
import json, math, os, random, re, sys
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path[:0] = [HERE, os.path.dirname(HERE)]
import bpy
from mathutils import Vector
from common import reset, camera, render, hexrgb, FPS
from sf_world import box, empty
from blocky_kit import CAST, HEAD_Z, M, build, hero, face_track, mystery, MARK, RIM
from moves import animate, ss, BLEND, GAG_HIT, GAG_LAND
from lab_dressing import REACH
from places import place, light, portal, ROOM_DOOR
import props as PR
import props_room, props_story
PR.BUILD.update(props_room.BUILDERS)   # tanks, calendars, phone, sign
PR.BUILD.update(props_story.BUILDERS)  # satellite, cash, maze, cage, shark, bubble, magnifier
KW_ALL = dict(props_story.KW)            # first-row keywords a table may pass to a builder, from every prop module
import importlib
for _m in ('props_cleaning', 'props_ice', 'props_light'):   # the weekend-test props (13 Nov 2026), each module optional
    try:
        _mod = importlib.import_module(_m)
    except ModuleNotFoundError as e:
        if e.name != _m:
            raise
        continue
    PR.BUILD.update(_mod.BUILDERS); KW_ALL.update(getattr(_mod, 'KW', {}))

FLIGHT = 0.45                                   # quick flight between framings (owner: quick flights, not snap whips)
APPROACH, EMERGE = 0.5, 0.6                     # a change of place: fly into a door (s), come out of the matching one (s)
DOOR_D, DOOR_Z, DOOR_LENS = 2.0, 1.7, 28        # the door picture: 2 units in front of the door, at its middle, 28 mm
PAST, DOOR_OPEN = 1.0, 100                      # a room's portal door stands 1 unit behind the first framing; opens 100 degrees
QUALITY = dict(samples=24, raytracing=True)     # speed A/B 5 Nov 2026: 24 samples look the same as 48, 13% faster; no ray tracing flattens floors
WORD = 0.38                                     # seconds per spoken word when there is no voice file yet
SPEED = {'walk': 2.2, 'run': 5.0, 'sprint': 8.5}


def cycles_look(sc):
    """ENGINE=cycles: the chess Short's renderer (path tracing on the graphics card, denoised): real reflections, soft shadows
    and bounce light instead of the quick EEVEE look. A look test only so far (12 Nov 2026): materials and lights were tuned for EEVEE."""
    sc.render.engine = 'CYCLES'
    prefs = bpy.context.preferences.addons['cycles'].preferences
    for dev in ('OPTIX', 'CUDA'):
        try:
            prefs.compute_device_type = dev; prefs.get_devices()
            for d in prefs.devices:
                d.use = d.type != 'CPU'
            break
        except Exception:
            pass
    cy = sc.cycles
    for k, v in (('device', 'GPU'), ('samples', int(os.environ.get('SAMPLES', '96'))), ('use_adaptive_sampling', True), ('adaptive_threshold', 0.02),
                 ('use_denoising', True), ('denoiser', 'OPTIX'), ('max_bounces', 8), ('glossy_bounces', 4), ('transmission_bounces', 8),
                 ('transparent_max_bounces', 8), ('sample_clamp_indirect', 8.0)):
        try:
            setattr(cy, k, v)
        except Exception:
            pass
    sc.render.use_persistent_data = True


def parse(path):
    meta, rows = {}, []
    for line in open(path, encoding='utf-8'):
        line = line.strip()
        m = re.match(r'^(length|light|hero|mystery|screen|dress|logo|void)\s*:\s*(.+)', line)
        if m:
            meta[m.group(1)] = m.group(2).strip()
        elif line.startswith('|') and not re.match(r'^\|\s*-', line) and not re.match(r'^\|\s*at\s*\|', line):
            c = [x.strip() for x in line.strip('|').split('|')] + [''] * 6
            rows.append(dict(at=float(c[0]), who=c[1].lower(), do=c[2].lower(), face=c[3].lower(), where=c[4], says=c[5]))
    rows.sort(key=lambda r: r['at'])
    return meta, rows


def build_scene(path):
    meta, rows = parse(path)
    HERO = json.loads(meta['hero']) if 'hero' in meta else None      # this episode's restyle of the hero (owner rule)
    reveals = [r['at'] for r in rows if r['who'] == 'hero' and 'reveal' in r['do'].split('+')]
    MYST = bool(reveals) or meta.get('mystery', 'no').lower() in ('yes', 'true', '1')   # the hero hides as the mystery figure
    REVEAL = reveals[0] if reveals else None                          # ... until this time (None: never revealed)
    for r in rows:
        if 'reveal' in r['do'].split('+'):
            r['do'] = '+'.join(x for x in r['do'].split('+') if x != 'reveal') or 'stand'
    T_END = float(meta.get('length', max(r['at'] for r in rows) + 2.0))
    places, place_at, cur = {}, [], None
    for r in rows:
        if r['who'] == 'place':
            if r['do'] not in places:
                opts = {t.split()[1]: False for t in r['where'].split(';') if t.strip().startswith('no ')}   # 'no chairs; no bowl'
                if r['do'] == 'lab':
                    if meta.get('screen'):
                        opts['screen'] = meta['screen'].strip().strip('"')                                # the huge screen's content
                    lst = lambda v: [x.strip().lower() for x in v.split(',') if x.strip() and x.strip().lower() != 'none']
                    if meta.get('dress'):
                        opts['dress'] = lst(meta['dress'])                                           # which things stand in the lab
                    if meta.get('logo'):
                        opts['brand'] = lst(meta['logo'])                                            # which of them carry the name
                    opts['t_end'] = T_END
                    opts['seed'] = sum(map(ord, os.path.abspath(path).lower()))   # each episode's file: its own hidden name spot
                if r['do'] == 'void' and meta.get('void'):
                    opts['color'] = meta['void'].split()[0]                                           # 'void: #ffd9a0'
                places[r['do']] = place(r['do'], **opts)
            place_at.append((r['at'], r['do']))
    where_is = lambda t: next((p for tt, p in reversed(place_at) if tt <= t), place_at[0][1])
    chars, plans, pos, only, away = {}, {}, {}, {}, {}

    def spot(pl, name):
        return places[pl]['spots'].get(name)

    def turn_to(a, b):
        return math.degrees(math.atan2(b[0] - a[0], -(b[1] - a[1])))

    for r in rows:
        if r['who'] in ('place', 'camera') or r['who'].startswith('@'):
            continue
        pl = where_is(r['at']); key = (r['who'], pl)
        toks = [t.strip() for t in r['where'].split(';') if t.strip()]
        o, start, dest, bump = {}, None, None, None
        for tk in toks:
            w = tk.split()
            if w[0] == 'from':
                start = (float(w[1]), float(w[2]), places[pl]['spots'].get('centre', (0, 0, 0, 0))[2] if pl == 'street' else 0.0, None)
            elif w[0] == 'to':
                dest = spot(pl, w[1]) if len(w) == 2 else (float(w[1]), float(w[2]), 0.0, None)
            elif w[0] == 'bump':                      # run into a thing in the place and fall (Ginger's bump gags)
                bump = places[pl].get('bumps', {}).get(w[1])
                if bump is None:
                    raise SystemExit(f"bump {w[1]}: there is no '{w[1]}' to run into in the {pl} (see 'dress:')")
                dest = bump['spot']
            elif w[0] == 'turn':
                o['turn'] = float(w[1])
            elif w[0] == 'face':
                o['face_who'] = w[1]
            elif w[0] == 'seat':
                o['seat'] = float(w[1])
            elif w[0] in ('speed', 'land', 'height', 'stride', 'hz', 'rise'):   # a move's own option (dive: 'land 1.21; speed 5')
                o[w[0]] = float(w[1])
            elif w[0] == 'at':
                start = (float(w[1]), float(w[2]), float(w[3]), None)
            elif w[0] == 'only':
                a, b = w[1].split('-'); only[key] = (float(a), float(b))
            elif w[0] == 'away':
                a, b = w[1].split('-'); away[key] = (float(a), float(b))
            elif spot(pl, w[0]):
                start = spot(pl, w[0])
        if bump and start is None and key not in chars:
            start = spot(pl, bump['start'])           # she comes from her side of the lane unless told otherwise
        if key not in chars:
            s0 = start or (0, 0, 0, 0)
            cast, _, n = r['who'].partition('#')
            rec = {**CAST[cast], 'name': CAST[cast]['name'] + n}
            if n and CAST[cast].get('variants') and int(n) > 1:               # fan#2, dog#3: the next outfit or coat
                rec.update(CAST[cast]['variants'][(int(n) - 2) % len(CAST[cast]['variants'])])
            chars[key] = hero(HERO, s0[:3]) if cast == 'hero' else build(rec, s0[:3])
            if r['who'] == 'hero' and MYST:
                chars[key]['twin'] = mystery(hero(HERO, s0[:3]))   # same moves; shown until the reveal
            plans[key] = dict(tl=[], cues=[], words=[]); pos[key] = s0
            if s0[3] is not None and 'turn' not in o:
                o['turn'] = s0[3]
        elif start and 'turn' not in o and start[3] is not None:
            o['turn'] = start[3]
        if 'face_who' in o:
            other = pos.get((o.pop('face_who'), pl))
            if other:
                o['turn'] = turn_to(pos[key], other)
        if 'sit' in r['do'] and 'seat' not in o:
            o['seat'] = places[pl].get('seat', 0.75)
        P = plans[key]
        base = r['do'].split('+')[0]
        if dest and bump and base in SPEED:
            # run at the thing and hit it: the run starts at 'at' (standing still before), the gag starts on arrival
            d = math.hypot(dest[0] - pos[key][0], dest[1] - pos[key][1]); th = turn_to(pos[key], dest)
            sp = SPEED[base]; dur = d / (sp * chars[key]['scale']) + BLEND / 2 - 0.02
            if not P['tl']:
                P['tl'].append((-1.0, 'stand', {'turn': th}))
            P['tl'].append((r['at'], r['do'], {'turn': th, 'speed': sp, 'turn_time': 0.2}))
            P['tl'].append((r['at'] + dur, bump['move'], {'turn': th, 'blend': 0.04, 'reach': REACH}))
            P['cues'].append((r['at'] + dur + GAG_HIT.get(bump['move'], 0.0), 'shocked'))
            P.setdefault('gags', []).append((r['at'] + dur, bump)); pos[key] = dest
        elif dest and base in SPEED:
            d = math.hypot(dest[0] - pos[key][0], dest[1] - pos[key][1]); th = turn_to(pos[key], dest)
            sp = SPEED[base]; dur = d / (sp * chars[key]['scale']) + 0.12     # small people and animals cover less ground a second
            extra = {'dest': (dest[0], dest[1])} if base == 'sprint' else {}   # a sprint steers onto its spot exactly (13 Nov 2026)
            P['tl'].append((r['at'], r['do'], {'turn': th, 'speed': sp, 'turn_time': 0.3, **extra}))
            P['tl'].append((r['at'] + dur, 'stand', {'turn': dest[3] if dest[3] is not None else th, 'turn_time': 0.35, 'auto': r['at']}))
            pos[key] = dest
        elif not r['do'] and P['tl'] and 'turn' not in o:
            pass                                      # a blank move keeps the current one (only a new face or words)
        else:
            if 'turn' in o:
                o.setdefault('turn_time', 0.35)
            sat = not P['tl'] and r['at'] == 0 and 'sit' in r['do'].split('+')     # already sitting when the scene opens
            P['tl'].append((-0.5 if sat else r['at'], r['do'] or 'stand', o))
        if r['face']:
            P['cues'].append((r['at'], r['face']))
        for i, w in enumerate(r['says'].split()):
            P['words'].append({'w': w.strip('.,!?"\''), 's': r['at'] + i * WORD, 'e': r['at'] + i * WORD + WORD * 0.85})
    for key, R in chars.items():
        P = plans[key]
        # the stop added at the end of a walk or run 'to' a spot is dropped when the table's next move for that character
        # already started before the arrival (13 Nov 2026: a sprint into a slide stopped dead and the slide never showed)
        P['tl'] = [e for e in P['tl'] if 'auto' not in e[2] or not any('auto' not in o and e[2]['auto'] < t0 < e[0] for t0, _, o in P['tl'])]
        animate(R, P['tl'], T_END)
        face_track(R, sorted(P['cues'], key=lambda c: c[0]) or [(0.0, 'calm')], P['words'], t_end=T_END, seed=sum(map(ord, key[0] + key[1])) % 97)   # same blinks every run
        R['place'] = key[1]; R['who'] = key[0]
        if 'twin' in R:
            animate(R['twin'], P['tl'], T_END); reveal_fx(R, REVEAL)
        for t0, name, _ in P['tl']:
            if 'splat' in name.split('+') and R.get('kind') != 'bird':
                dizzy_stars(R, t0)
        for t_arr, bump in P.get('gags', []):          # the hit: a squash, a burst, the thing rocks; then the stars
            mv = bump['move']; t_hit = t_arr + GAG_HIT.get(mv, 0.0)
            if mv != 'trip':
                squash(R, t_hit)
            impact_fx(R, bump, t_hit)
            bump['react'](t_hit)
            dizzy_stars(R, t_arr + GAG_LAND.get(mv, 0.7) - 0.7)
        if key in only:
            a, b = only[key]; fa_, fb_ = (1 + round(a * FPS) if a > 0 else None), 1 + round(b * FPS)
            if 'twin' in R:                           # (14 Nov 2026) the window holds for the mystery figure too, and the real
                fr = None if REVEAL is None else 1 + round(REVEAL * FPS)   # hero still only shows from the reveal on
                _show(R['twin'], on_from=fa_, off_from=fb_ if fr is None else min(fb_, fr))
                if fr is not None and fr < fb_:
                    _show(R, on_from=max(fa_ or 0, fr), off_from=fb_)
            else:
                _show(R, on_from=fa_, off_from=fb_)
        if key in away:                               # out of sight for a while (e.g. so a wide shot of others is clean)
            a, b = away[key]; fa, fb = 1 + round(a * FPS), 1 + round(b * FPS)
            # who comes back after the gap: the real hero only if there is no mystery figure or he has been revealed by then;
            # the mystery figure if he is never revealed or not yet (13 Nov 2026: 'mystery: yes' + 'away' brought the real face back)
            # (14 Nov 2026) keep whatever showed before the gap: without a key just before it, Blender holds the first key's
            # 'hidden' back to frame 0, so someone stepping out for a while was gone from the very start (the ice fan, the kid)
            sc_ = bpy.context.scene; now_ = sc_.frame_current; sc_.frame_set(max(0, fa - 1))
            before = {o: o.hide_render for X in (R, R.get('twin')) if X for o in X['root'].children_recursive if o.type in ('MESH', 'FONT')}
            sc_.frame_set(now_)
            for X, back in ((R, 'twin' not in R or (REVEAL is not None and b >= REVEAL)), (R.get('twin'), REVEAL is None or b < REVEAL)):
                if X is None:
                    continue
                for o in X['root'].children_recursive:
                    if o.type in ('MESH', 'FONT'):
                        if fa > 1:
                            o.hide_render = o.hide_viewport = before[o]
                            o.keyframe_insert('hide_render', frame=fa - 1); o.keyframe_insert('hide_viewport', frame=fa - 1)
                        for f, hide in ((fa, True), (fb, not back)):
                            o.hide_render = o.hide_viewport = hide
                            o.keyframe_insert('hide_render', frame=f); o.keyframe_insert('hide_viewport', frame=f)
    props = build_props(rows, chars, where_is, T_END)
    cams = [r for r in rows if r['who'] == 'camera']
    return meta, T_END, places, chars, cams, where_is, props


def build_props(rows, chars, where_is, T_END):
    """Props from '@name' rows: the first row builds (do = kind), later rows animate (do = action)."""
    props = {}
    for r in rows:
        if not r['who'].startswith('@'):
            continue
        name, pl = r['who'], where_is(r['at'])
        toks = [t.strip().split() for t in r['where'].split(';') if t.strip()]
        opt = {w[0]: (w[1:] if len(w) > 1 else True) for w in toks}
        if name not in props:
            loc = tuple(float(v) for v in opt['at']) if 'at' in opt else (0, 0, 0)
            kw = {}
            if r['do'] == 'card':                     # the number card with our own words: label 43M; sub VIEWS; scale 0.4
                kw = {k2: (' '.join(opt[k2]) if k2 != 's' else float(opt[k2][0])) for k2 in ('label', 'sub', 's') if k2 in opt}
            for k2, cast_to in KW_ALL.get(r['do'], {}).items():   # bubble: icon squirrel; cage: tall 3.2; radius 1.4
                if k2 in opt and opt[k2] is not True:          # 'text': the words as written ('labels 340M, 1.7B')
                    kw[k2] = ' '.join(opt[k2]) if cast_to == 'text' else cast_to(opt[k2][0].lower())
            P = PR.make(r['do'], name, loc, float(opt['turn'][0]) if 'turn' in opt else 0.0, **kw)
            P.update(place=pl, who=name, name=name, t_end=T_END)
            P['track'] = {f: (*loc, P['turn']) for f in range(1, round(T_END * FPS) + 3)}
            props[name] = P
            if 'size' in opt:
                P['size'] = float(opt['size'][0])
            if 'hold' in opt:
                R = chars[(opt['hold'][0], pl)]
                PR.hold(P, R, r['at'], float(opt['until'][0]) if 'until' in opt else T_END + 1,
                        side='L' if 'left' in opt else 'R', tilt=(float(opt['tilt'][0]) if 'tilt' in opt else 0, 0, 0))
            continue
        a = {'slot': int(opt['slot'][0])} if 'slot' in opt else {}
        if 'off' in opt:
            a['off'] = float(opt['off'][0])
        for k2, v in opt.items():                     # every other option as numbers: to X Y Z; up N; around X Y; radius R; for S ...
            if k2 not in ('slot', 'off'):
                try:
                    a[k2] = v if v is True else [float(x) for x in v]
                except ValueError:
                    a[k2] = v
        PR.act(props[name], r['do'], r['at'], a)
    return props


# ---------------------------------------------------------------- the reveal
def _show(R, on_from=None, off_from=None):
    """Key a character's visibility: hidden before on_from and from off_from (frames; None = no limit)."""
    for o in R['root'].children_recursive:
        if o.type not in ('MESH', 'FONT'):
            continue
        for f, hide in ((0, on_from is not None), (on_from, False), (off_from, True)):
            if f is not None:
                o.hide_render = o.hide_viewport = hide
                o.keyframe_insert('hide_render', frame=f); o.keyframe_insert('hide_viewport', frame=f)


def reveal_fx(R, t):
    """The mystery figure (R['twin']) is shown until t, then the real hero pops out of a burst of sparks."""
    X = R['twin']; X['name'] = R['name'] + '_mystery'
    if t is None:                                     # never revealed: only the mystery figure
        _show(R, off_from=0); return
    f = 1 + round(t * FPS); _show(X, off_from=f); _show(R, on_from=f)
    s = R['scale']
    for df, k in ((-1, 1.0), (0, 0.7), (4, 1.06), (8, 1.0)):   # a squash-and-pop as the hero appears
        R['root'].scale = (s * k,) * 3; R['root'].keyframe_insert('scale', frame=max(1, f + df))
    x, y, z, _ = R['track'][f]; rnd = random.Random(7); n = 30
    for i in range(n):                                # a ring of sparks in the mystery colours bursts out and shrinks away
        a = 2 * math.pi * i / n + rnd.uniform(-0.1, 0.1); d = rnd.uniform(1.3, 2.2) * s
        c = (x, y - 0.3 * s, z + 1.5 * s); end = (x + d * math.cos(a), y - 0.3 * s - rnd.uniform(0, 0.6) * s, c[2] + d * math.sin(a) * 1.1)
        sz = rnd.uniform(0.16, 0.3) * s; col = (MARK, RIM, '#ffffff')[i % 3]
        b = box((0, 0, 0), (sz, sz, sz), M(col, 0.4, emit=hexrgb(col), emit_strength=4.0), rot=(rnd.uniform(0, 90),) * 3, bevel=0)   # box() bakes its location into the mesh
        for df, loc, k in ((-1, c, 0.0), (0, c, 1.0), (round(0.18 * FPS), lerp3(c, end, 0.75), 1.0), (round(0.5 * FPS), end, 0.0)):
            b.location = loc; b.scale = (k,) * 3
            b.keyframe_insert('location', frame=max(1, f + df)); b.keyframe_insert('scale', frame=max(1, f + df))


def dizzy_stars(R, t0):
    """Pip's splat ends with three yellow stars circling above the dazed head (from 0.7 s to 2.3 s after the trip)."""
    from animals import prism
    s = max(R['scale'], 0.6); sc = bpy.context.scene; f0, f1 = 1 + round((t0 + 0.7) * FPS), 1 + round((t0 + 2.3) * FPS)
    pts = [((0.16 if i % 2 == 0 else 0.07) * math.sin(math.pi * i / 5), (0.16 if i % 2 == 0 else 0.07) * math.cos(math.pi * i / 5)) for i in range(10)]
    stars = [prism(pts, 0.05, (0, 0, 0), M(MARK, 0.35, emit=hexrgb(MARK), emit_strength=2.5), bevel=0.012) for _ in range(3)]
    heads = {}
    for f in range(f0 - 1, f1 + 2, 2):                # the head's place per frame (it lies on the ground, then lifts)
        sc.frame_set(f); heads[f] = R['head'].matrix_world.translation.copy()
    for i, st in enumerate(stars):
        for f, h in heads.items():
            t = (f - f0) / FPS; a = 2 * math.pi * (1.4 * t + i / 3)
            k = ss(t / 0.2) * (1 - ss((t - 1.4) / 0.2))
            st.location = (h.x + 0.48 * s * math.cos(a), h.y + 0.48 * s * math.sin(a), h.z + (0.55 + 0.06 * math.sin(3 * a)) * s)
            st.rotation_euler = (0, 0, a * 2); st.scale = (max(k, 0.0) * s * 1.2,) * 3
            for path in ('location', 'rotation_euler', 'scale'):
                st.keyframe_insert(path, frame=f)
    sc.frame_set(1)


def squash(R, t):
    """A cartoon squash at a hit: flattened along the way she was going, then a small rebound."""
    s = R['scale']; f = 1 + round(t * FPS)
    for df, k in ((-1, (1, 1, 1)), (1, (1.18, 0.64, 1.12)), (4, (0.93, 1.1, 0.97)), (7, (1, 1, 1))):
        R['root'].scale = tuple(s * v for v in k); R['root'].keyframe_insert('scale', frame=max(1, f + df))


def impact_fx(R, bump, t):
    """A small white burst where she hits the thing (eight short streaks flying out for 0.2 s), so the bump reads even small
    in the background."""
    f = 1 + round(t * FPS); bpy.context.scene.frame_set(f); h = R['head'].matrix_world.translation.copy()
    cx, cy = bump['contact']; d = bump['dir']
    c = (cx if bump['move'] != 'trip' else h.x, cy - 0.15, h.z if bump['move'] != 'trip' else 0.25)
    m = M('#ffffff', 0.4, emit=hexrgb('#ffffff'), emit_strength=3.0); s = max(R['scale'], 0.5)
    for i in range(8):
        a = 2 * math.pi * (i + 0.5) / 8
        st = box((0, 0, 0), (0.05 * s, 0.05 * s, 0.3 * s), m, rot=(0, -math.degrees(a) + 90, 0), bevel=0)
        for df, r0, k in ((-1, 0.2, 0.0), (0, 0.25, 1.0), (round(0.12 * FPS), 0.55, 1.0), (round(0.22 * FPS), 0.75, 0.0)):
            st.location = (c[0] + r0 * s * 2 * math.cos(a), c[1], c[2] + r0 * s * 2 * math.sin(a)); st.scale = (k,) * 3
            st.keyframe_insert('location', frame=max(1, f + df)); st.keyframe_insert('scale', frame=max(1, f + df))
    bpy.context.scene.frame_set(1)


def lerp3(a, b, u):
    return tuple(p + (q - p) * u for p, q in zip(a, b))


# ---------------------------------------------------------------- camera bank
def live(R):
    """The figure really on screen at the current frame: the mystery twin while the hero is still hidden. A hidden object is
    not evaluated, so the hidden hero's head keeps a stale place; reading it aimed the camera, the move tests and the checks
    at the wrong spot (found 13 Nov 2026, weekend Shorts)."""
    return R['twin'] if 'twin' in R and R['head'].hide_viewport and not R['twin']['head'].hide_viewport else R


def head_at(R, f):
    """Where R's head really is at frame f (lying down, sitting, an animal's head ahead of its body)."""
    bpy.context.scene.frame_set(f)
    return live(R)['head'].matrix_world.translation.copy()


def framing(kind, subj, pl, places, f):
    """-> (cam_start, cam_end, look_start, look_end, lens). Subjects are framed from their front (or the open side of a room)."""
    def head(R):
        x, y, z, t = R['track'][f]
        if R.get('prop'):
            return (x, y, z + R['focus_z']), t
        return tuple(head_at(R, f) - Vector((0, 0, 0.05))), t       # the real head: someone lying flat is filmed on the ground

    def front(t):
        """Where a single framing films from: the subject's front swung toward the open (-y) side, so someone facing another
        person side-on is filmed three-quarter on, never from where the other person stands (reveal test, 5 Nov 2026)."""
        F = (math.sin(math.radians(t)), -math.cos(math.radians(t)))
        if F[1] >= 0.35:
            return (0.0, -1.0)
        v = (F[0], F[1] - 1.0); L = math.hypot(*v); return (v[0] / L, v[1] / L)
    add = lambda a, b, k=1.0: tuple(x + k * y for x, y in zip(a, b))
    if not subj:                                      # a wide of the place itself
        c, l = places[pl]['cams'].get('wide') or places[pl]['cams']['from_door']
        return c, add(c, tuple(b - a for a, b in zip(c, l)), 0.05), l, l, 24 if pl != 'street' else 28
    (A, ta) = head(subj[0])
    if kind == 'top':                                 # from above: the long side of the picture along x, aimed at the floor below
        k = subj[0].get('size', 1.0) if subj[0].get('prop') else 1.0; h = 7.0 * k; z0 = subj[0]['track'][f][2]
        l = (A[0], A[1], z0); c = (A[0] - 0.16 * h, A[1], z0 + h)
        return c, c, l, l, 24
    if subj[0].get('prop') and len(subj) == 1:        # a prop: straight from its front, scaled to its size, no drift
        k = subj[0]['size']; Fp = (math.sin(math.radians(ta)), -math.cos(math.radians(ta)))
        if kind == 'push_in':
            c0 = (A[0] + Fp[0] * 5.2 * k, A[1] + Fp[1] * 5.2 * k, A[2] + 1.1 * k); c1 = (A[0] + Fp[0] * 2.4 * k, A[1] + Fp[1] * 2.4 * k, A[2] + 0.4 * k)
            return c0, c1, A, A, 32
        dist, dz, lens = dict(close=(2.9, 0.55, 35), medium=(5.2, 1.0, 30), low=(3.4, -0.25, 24), wide=(7.0, 1.6, 24)).get(kind, (5.2, 1.0, 30))
        if subj[0].get('view_up'):                   # small things on a plate: look down on them instead of along the plate
            dz = subj[0]['view_up'] * dist
        c = (A[0] + Fp[0] * dist * k, A[1] + Fp[1] * dist * k, A[2] + dz * k)
        return c, c, A, A, lens
    if kind in ('wide', 'two_shot') and (len(subj) > 1 or kind == 'wide'):
        hs = [head(R)[0] for R in subj]; lens = 24 if kind == 'wide' else 28
        for R in subj:                                    # a four-legged animal's body and tail stretch out behind its head
            if R.get('kind') == 'quad':
                x, y, z, t = R['track'][f]; k = R['scale']
                hs.append((x - math.sin(math.radians(t)) * 1.0 * k, y + math.cos(math.radians(t)) * 1.0 * k, z + 0.5 * k))
        tan_w = 18 / lens * 9 / 16                        # half-width of the 9:16 picture per unit of distance
        r = max(0.4, min(1.0, max(h[2] for h in hs) / (HEAD_Z + 0.01)))      # only animals or small people: lower and closer
        width = max(h[0] for h in hs) - min(h[0] for h in hs) + (3.6 if kind == 'wide' else 2.2) * r
        M = ((max(h[0] for h in hs) + min(h[0] for h in hs)) / 2, sum(h[1] for h in hs) / len(hs), 1.45 * r)
        dist = max(4.6 * r, width / (2 * tan_w)); c = (M[0], M[1] - dist, (2.0 + 0.04 * dist) * r)
        return c, add(c, (0, dist, 0), 0.05), M, M, lens
    if kind in ('two_shot', 'ots') and len(subj) > 1:
        (B, tb) = head(subj[1]); AB = (B[0] - A[0], B[1] - A[1]); L = math.hypot(*AB) or 1.0; n = (-AB[1] / L, AB[0] / L)
        if kind == 'ots':
            d = (AB[0] / L, AB[1] / L); c = (A[0] - d[0] * 2.6 + n[0] * 1.5, A[1] - d[1] * 2.6 + n[1] * 1.5, A[2] + 0.3)
            if c[1] > max(A[1], B[1]) + 0.5:          # never from behind a room's back wall
                c = (A[0] - d[0] * 2.6 - n[0] * 1.5, A[1] - d[1] * 2.6 - n[1] * 1.5, A[2] + 0.3)
            return c, add(c, (B[0] - c[0], B[1] - c[1], 0), 0.04), B, B, 32
        if n[1] > 0:
            n = (-n[0], -n[1])
        M = ((A[0] + B[0]) / 2, (A[1] + B[1]) / 2, (A[2] + B[2]) / 2 - 0.75); dist = max(5.0, L * 1.25 + 2.8)
        c = (M[0] + n[0] * dist, M[1] + n[1] * dist, 2.0)
        return c, add(c, (M[0] - c[0], M[1] - c[1], 0), 0.05), M, M, 28
    z0 = subj[0]['track'][f][2]
    if A[2] - z0 < 0.45 * subj[0].get('head_z', HEAD_Z) * subj[0]['scale']:    # lying flat (Pip's splat)
        # filmed from in front of the head and the open side, from above: the body runs away into the picture, so the
        # whole fall (face down, legs kicking up behind, the stars) fits the tall frame
        fd = (math.sin(math.radians(ta)), -math.cos(math.radians(ta))); k = subj[0]['scale']
        b, fwd = (-0.1, 2.2) if subj[0].get('kind') else (0.7, 0.8)          # an animal: keep its face in, film more from the front
        l = (A[0] - fd[0] * b * k, A[1] - fd[1] * b * k, A[2] + 0.2 * k)
        v = (fd[0] * fwd, fd[1] * fwd - 1.0); n = math.hypot(*v); v = (v[0] / n, v[1] / n)
        dist, up, lens = dict(close=(3.8, 1.7, 30), low=(3.8, 0.5, 24)).get(kind, (5.6, 2.6, 28))
        kz = max(0.45, k * subj[0].get('head_z', HEAD_Z) / HEAD_Z); dist, up = dist * kz, up * kz      # a lying cat: closer
        c = (l[0] + v[0] * dist, l[1] + v[1] * dist, A[2] + up)
        return c, add(c, (l[0] - c[0], l[1] - c[1], 0), 0.05), l, l, lens
    F = front(ta); side = (-F[1], F[0])
    q = max(0.3, min(1.0, (A[2] - z0) / (HEAD_Z - 0.05)))                  # small people and animals: everything closer and lower
    def at(dist, z, off=0.5):
        return (A[0] + F[0] * dist * q + side[0] * off * q, A[1] + F[1] * dist * q + side[1] * off * q, z0 + (z - z0) * q)
    if kind == 'close':
        c = at(2.9, A[2] + 0.15); l = (A[0], A[1], A[2] - 0.05 * q); return c, add(c, (l[0] - c[0], l[1] - c[1], 0), 0.06), l, l, 35
    if kind == 'low':
        c = at(3.6, z0 + 0.7, 0.3); l = (A[0], A[1], A[2] - 0.4 * q); return c, add(c, (l[0] - c[0], l[1] - c[1], 0), 0.05), l, l, 24
    if kind == 'push_in':
        c0 = at(5.2, z0 + 2.0); c1 = at(2.9, A[2] + 0.15); return c0, c1, (A[0], A[1], A[2] - 0.9 * q), (A[0], A[1], A[2] - 0.05 * q), 32
    c = at(5.2, z0 + 2.0); l = (A[0], A[1], A[2] - 0.9 * q)              # medium
    return c, add(c, (l[0] - c[0], l[1] - c[1], 0), 0.05), l, l, 30


def pick_moves(holds, cams, fits=lambda h, m: True):
    """One steady camera move per framing (owner, 13 Nov 2026: "most of [the format benchmark's] wins have nice camera movements across the
    whole video"). Measured on the format benchmark's top Shorts: its camera moves 95 % of the time and never rests longer than about 0.2 s;
    slow moves cross about 13 % of the picture width a second, push-ins about 6 % a second. Each framing gets the next move
    of MOVES whose family differs from the one before. The camera row's face column can force one ('arc_l', 'push', ...,
    or 'still' for the old creep). CAM=old switches the whole thing off (the camera before 13 Nov 2026), for comparisons."""
    out, prev, k = [], None, 0
    for h, r in zip(holds, cams):
        kind, subj = h[2], h[3]
        if os.environ.get('CAM') == 'old' or r.get('face') == 'still':
            m = 'old'
        elif kind == 'push_in':
            m = 'own'                                  # a push_in framing brings its own bigger push
        elif r.get('face') in MOVES:
            m = r['face']
        else:
            ok = [x for x in MOVES if not (x.startswith('arc') and (not subj or kind == 'ots')) and not (x.startswith('crane') and kind in ('low', 'top'))]   # no swing round a wide of a place; a low framing keeps its low angle
            order = [MOVES[(k + j) % len(MOVES)] for j in range(len(MOVES))]
            tries = [x for x in order if x in ok and FAMILY[x] != FAMILY.get(prev)] + [x for x in order if x in ok and FAMILY[x] == FAMILY.get(prev)]
            m = next((x for x in tries if fits(h, x)), 'push')      # every move is tried on the real scene first (faces in, nothing in the way)
            k = MOVES.index(m) + 1 if m in MOVES else k + 1
        out.append(m); prev = m
    return out


MOVES = ('push', 'arc_r', 'crane_up', 'truck_l', 'pull', 'arc_l', 'crane_down', 'truck_r')
FAMILY = dict(push='dolly', pull='dolly', arc_l='arc', arc_r='arc', crane_up='crane', crane_down='crane', truck_l='truck', truck_r='truck', own='dolly')
SIDE = float(os.environ.get('CAM_SIDE', '0.14'))   # swings, slides, cranes: the room behind slides this share of the picture width a second
PUSH = float(os.environ.get('CAM_PUSH', '0.08'))   # push / pull: this share of the camera's distance a second (the benchmark's push-ins: ~6 %/s zoom)
BEHIND = 6.8                                       # the room behind sits about this far behind the subject (fits the 13 Nov 2026 lab measurements)
CREEP = 0.025                                      # swings, cranes and slides also creep in a little, as the benchmark's do
CEILING = {'classroom': 4.5, 'bedroom': 4.5, 'kitchen': 4.5, 'office': 4.5, 'shop': 4.5}    # rooms are 5 high; lab, void, street are open


def moved(h, t):
    """Camera, aim point and lens of framing h at time t. Its move runs at one steady speed through the framing's middle
    (so the middle frame is the framing as planned and checked), and runs on through the flights either side, so the camera
    never comes to a stop between moves. A long framing moves slower rather than running out of room and stopping.
    Swings, slides and cranes keep the subject in the middle of the picture; the room behind it slides past."""
    m = h[10]
    if m in ('old', 'own'):
        u = min(max((t - h[0]) / max(h[1] - h[0], 1e-3), 0), 1)
        e = ss(u) if h[2] == 'push_in' else u
        return lerp3(h[5], h[6], e), lerp3(h[7], h[8], e), h[9]
    c, l, lens = h[5], h[7], h[9]
    dt = t - (h[0] + h[1]) / 2
    span = (h[1] - h[0]) / 2 + FLIGHT                          # furthest the move runs from the framing's middle
    fit = lambda rate, room: min(rate, room / span)
    v = tuple(a - b for a, b in zip(c, l)); d = math.sqrt(sum(x * x for x in v)) or 1.0
    tw = 18 / lens * 9 / 16                                    # half the picture width per unit of distance
    turn = SIDE * 2 * tw * (d + BEHIND) / BEHIND                  # how fast the view turns (radians a second) so the room behind slides SIDE
    sgn = -1 if m.endswith(('_l', 'down')) or m == 'pull' else 1
    if m in ('push', 'pull'):
        k = 1 - sgn * fit(PUSH, 0.4) * dt
        return tuple(a + x * k for a, x in zip(l, v)), l, lens
    k = 1 - fit(CREEP, 0.15) * dt; v = tuple(x * k for x in v); d *= k
    if m.startswith('arc'):
        a = sgn * fit(turn, 0.45) * dt
        ca, sa = math.cos(a), math.sin(a)
        return (l[0] + v[0] * ca - v[1] * sa, l[1] + v[0] * sa + v[1] * ca, l[2] + v[2]), l, lens
    if m.startswith('truck'):                                  # a straight slide sideways, still aimed at the subject
        hz = math.hypot(v[0], v[1]) or 1.0; right = (-v[1] / hz, v[0] / hz)
        s = sgn * fit(turn * d, 0.35 * d) * dt
        return (l[0] + v[0] + right[0] * s, l[1] + v[1] + right[1] * s, l[2] + v[2]), l, lens
    cz = l[2] + v[2]; zmax = CEILING.get(h[4], 9.0)            # crane: rise or sink, still aimed at the subject
    up, down = max(0.0, zmax - cz), max(0.0, cz - 0.35)
    half = min(fit(turn * d, 0.6 * d) * span, (up + down) / 2)
    mid = min(max(cz, 0.35 + half), zmax - half)               # near the floor or the ceiling: the move shifts to fit
    z = mid + sgn * (half / span) * dt
    return (l[0] + v[0], l[1] + v[1], z), l, lens


def move_fits(h, m, cam, target):
    """Try move m on framing h in the built scene: at the start, middle and end of the framing every framed face must stay in
    the picture, and nothing may stand between the camera and a face at two or more of those moments (the same tests as
    run_checks, which only looks at the middle)."""
    from bpy_extras.object_utils import world_to_camera_view
    sc = bpy.context.scene; hm = h[:10] + (m,); blocked = 0
    for te in (h[0] + 0.05, (h[0] + h[1]) / 2, max(h[0] + 0.05, h[1] - FLIGHT)):
        f = 1 + round(te * FPS); sc.frame_set(f)
        c, l, lens = moved(hm, te)
        cam.location = c; target.location = l; cam.data.lens = lens; bpy.context.view_layer.update()
        dg = bpy.context.evaluated_depsgraph_get(); o = cam.matrix_world.translation.copy()
        for R in (h[3][1:] if h[2] == 'ots' else h[3]):
            tr = R['track'].get(f) or R['track'][max(R['track'])]
            hd = Vector((tr[0], tr[1], tr[2] + R['focus_z'])) if R.get('prop') else live(R)['head'].matrix_world.translation.copy()
            v = world_to_camera_view(sc, cam, hd)
            if not (0.04 < v.x < 0.96 and 0.04 < v.y < 0.96 and v.z > 0):
                return False
            if R.get('kind') == 'mark':
                continue
            mine = set(R['root'].children_recursive) | (set(R['twin']['root'].children_recursive) if 'twin' in R else set())
            hit, _, _, _, ob, _ = sc.ray_cast(dg, o, (hd - o).normalized(), distance=(hd - o).length - 0.05)
            if hit and ob not in mine and ob.original not in mine:
                blocked += 1
    return blocked < 2


def camera_track(cams, chars, places, where_is, T_END, props=None):
    target = empty('Focus'); cam = camera(lens=28, focus_obj=target, fstop=8.0)
    import places as PLM
    wins = []                                         # a view from above ('top'): the rooms' ceilings are hidden meanwhile
    for i, r in enumerate(cams):
        if r['do'] == 'top':
            t0 = r['at'] - FLIGHT - 2 / FPS; t1 = (cams[i + 1]['at'] if i + 1 < len(cams) else T_END) + FLIGHT
            if wins and t0 <= wins[-1][1] + 1.0:      # views from above less than 1 s apart: one window, so the room's light
                wins[-1][1] = max(wins[-1][1], t1)    # does not jump during a short eye-level shot between them
            else:
                wins.append([t0, t1])
    for t0, t1 in wins:
        for ob in PLM.CEILS:
            for f, hide in ((max(1, 1 + round(t0 * FPS)), True), (1 + round(t1 * FPS), False)):
                ob.hide_render = ob.hide_viewport = hide
                ob.keyframe_insert('hide_render', frame=f); ob.keyframe_insert('hide_viewport', frame=f)
    for ob in PLM.CEILS:
        fc = ob.animation_data.action if ob.animation_data else None
        if fc is not None:
            ob.hide_render = ob.hide_viewport = False
            ob.keyframe_insert('hide_render', frame=0); ob.keyframe_insert('hide_viewport', frame=0)
            for c in (getattr(fc, 'fcurves', None) or [c for ly in fc.layers for st in ly.strips for cb in st.channelbags for c in cb.fcurves]):
                for kp in c.keyframe_points:
                    kp.interpolation = 'CONSTANT'
    tc = cam.constraints.new('TRACK_TO'); tc.target = target; tc.track_axis = 'TRACK_NEGATIVE_Z'; tc.up_axis = 'UP_Y'
    holds = []
    for i, r in enumerate(cams):
        t0 = r['at']; t1 = cams[i + 1]['at'] if i + 1 < len(cams) else T_END; pl = where_is(t0 + 0.01)
        subj = [props[w.strip()] if w.strip().startswith('@') else chars[(w.strip(), pl)] for w in r['where'].split(',')
                if (w.strip().startswith('@') and w.strip() in (props or {})) or (w.strip(), pl) in chars]
        mid = 1 + round((t0 + t1) / 2 * FPS)
        holds.append((t0, t1, r['do'], subj, pl) + framing(r['do'], subj, pl, places, min(mid, round(T_END * FPS))))
    holds = [h + (m,) for h, m in zip(holds, pick_moves(holds, cams, lambda h, m: move_fits(h, m, cam, target)))]
    bpy.context.scene.frame_set(1)
    for k, h in enumerate(holds, 1):
        print(f'MOVE {k}: {h[2]} -> {h[10]}')
    lerp = lambda a, b, u: tuple(x + (y - x) * u for x, y in zip(a, b))
    pose = moved

    def fly(a, b, u, e):
        """From pose a to pose b with a small rise in the middle; e eases the travel."""
        (c0, l0, n0), (c1, l1, n1) = a, b; rise = min(3.0, 0.12 * math.dist(c0, c1)) * math.sin(math.pi * u)
        c = lerp(c0, c1, e); return (c[0], c[1], c[2] + rise), lerp(l0, l1, ss(u)), n0 + (n1 - n0) * u

    def door_view(D, v):                              # the picture filled by a door: DOOR_D in front of its centre plane
        return (D[0] - v[0] * DOOR_D, D[1] - v[1] * DOOR_D, DOOR_Z), (D[0], D[1], DOOR_Z), DOOR_LENS

    def through(P, b, u):
        """From a portal's door view through the opening doorway to pose b (u 0..1): the camera rests at the door while it
        swings open, then moves through, staying at door height until it is past the doorway."""
        (c1, l1, n1) = b; c0, l0, n0 = door_view(P['D'], P['v']); e = ss(u)
        cross = DOOR_D / (DOOR_D + P['past'])
        xy = lerp(c0[:2], c1[:2], e); z = DOOR_Z + (c1[2] - DOOR_Z) * ss((e - cross) / (1 - cross))
        return (xy[0], xy[1], z), lerp(l0, l1, ss(u)), n0 + (n1 - n0) * u

    def make_portal(room, b):
        """An identical copy of the room's street door, standing PAST behind framing b, facing it."""
        c1, l1 = b[0], b[1]; v = (l1[0] - c1[0], l1[1] - c1[1]); L = math.hypot(*v) or 1.0; v = (v[0] / L, v[1] / L)
        D = (c1[0] - v[0] * PAST, c1[1] - v[1] * PAST)
        root, hinges, meshes = portal(ROOM_DOOR.get(room, 'house'), D, math.degrees(math.atan2(-v[0], v[1])))
        return dict(D=D, v=v, past=PAST, hinges=hinges, meshes=meshes, keys=[])

    def street_door(room):
        x, y = places['street']['doors'][ROOM_DOOR.get(room, 'house')]; return (x, y), (0.0, 1.0)

    # A change of place: fly into the street door of the building (or out through a room's portal), cut where the door
    # fills the picture, come out of the matching door on the other side.
    changes = []
    for i in range(len(holds) - 1):
        A, B = holds[i], holds[i + 1]
        if A[4] == B[4]:
            continue
        fs = 1 + round(B[0] * FPS); t_cut = (fs - 1.5) / FPS
        a_pose = pose(A, t_cut - APPROACH); b_pose = pose(B, t_cut + EMERGE)
        room = B[4] if B[4] != 'street' else A[4]
        if A[4] == 'street':
            dv = door_view(*street_door(room)); pa = None
            approach = lambda u, a_pose=a_pose, dv=dv: fly(a_pose, dv, u, ss(u))
        else:                                         # leave a room backwards through its portal, the doors closing
            pa = make_portal(room, a_pose)
            approach = lambda u, pa=pa, a_pose=a_pose: through(pa, a_pose, 1 - u)
        if B[4] == 'street':
            dv = door_view(*street_door(room)); pb = None
            emerge = lambda u, dv=dv, b_pose=b_pose: fly(dv, b_pose, u, ss(u))
        else:
            pb = make_portal(room, b_pose)
            emerge = lambda u, pb=pb, b_pose=b_pose: through(pb, b_pose, u)
        changes.append(dict(fs=fs, t_cut=t_cut, approach=approach, emerge=emerge, pa=pa, pb=pb))

    def at_time(t):
        """-> (camera, look, lens, portal in use or None, how far its doors are through opening 0..1)."""
        for ch in changes:
            if ch['t_cut'] - APPROACH <= t < ch['t_cut']:
                u = min(1.0, (t - (ch['t_cut'] - APPROACH)) / (APPROACH - 0.5 / FPS))   # at the door on the last frame before the cut
                return ch['approach'](u) + (ch['pa'], 1 - u)
            if ch['t_cut'] <= t < ch['t_cut'] + EMERGE:
                u = (t - ch['t_cut']) / EMERGE; return ch['emerge'](u) + (ch['pb'], u)
        i = max((k for k, h in enumerate(holds) if h[0] <= t), default=0)
        if i + 1 < len(holds) and holds[i + 1][4] == holds[i][4] and t > holds[i + 1][0] - FLIGHT:   # a quick flight in one place
            u = ss((t - (holds[i + 1][0] - FLIGHT)) / FLIGHT)
            if os.environ.get('CAM') == 'old':
                return fly(pose(holds[i], holds[i + 1][0] - FLIGHT), pose(holds[i + 1], holds[i + 1][0]), u, u) + (None, 0)
            # both framings keep moving during the flight (no dead stop at either end): from where this move is now
            # to where the next move is now
            return fly(pose(holds[i], t), pose(holds[i + 1], t), u, u) + (None, 0)
        return pose(holds[i], t) + (None, 0)

    def key(f, c, l, lens):
        cam.location = c; target.location = l; cam.data.lens = lens
        cam.keyframe_insert('location', frame=f); target.keyframe_insert('location', frame=f); cam.data.keyframe_insert('lens', frame=f)

    def key_portal(P, f, u, c):
        if P is not None:
            outside = (c[0] - P['D'][0]) * P['v'][0] + (c[1] - P['D'][1]) * P['v'][1] < 0
            P['keys'].append((f, outside, DOOR_OPEN * ss((u - 0.06) / 0.34)))   # still shut on the first frame after the cut

    prefs = bpy.context.preferences.edit; old = prefs.keyframe_new_interpolation_type; prefs.keyframe_new_interpolation_type = 'LINEAR'
    for f in range(1, round(T_END * FPS) + 2):
        c, l, lens, P, u = at_time((f - 1) / FPS); key(f, c, l, lens); key_portal(P, f, u, c)
    snaps = []
    for ch in changes:                                # the cut sits between two frames, outside both shutters: no smear
        c, l, lens = ch['approach'](1.0); key(ch['fs'] - 0.52, c, l, lens); key_portal(ch['pa'], ch['fs'] - 0.52, 0.0, c)
        snaps.append(ch['fs'] - 0.52)
        c, l, lens = ch['emerge'](0.0); key(ch['fs'] - 0.5, c, l, lens); key_portal(ch['pb'], ch['fs'] - 0.5, 0.0, c)
    for P in [p for ch in changes for p in (ch['pa'], ch['pb']) if p]:
        P['keys'].sort(); first, last = P['keys'][0][0], P['keys'][-1][0]
        for ob in P['meshes']:                        # shown only while the camera is outside it, during its change
            ob.hide_render = ob.hide_viewport = True
            for k in (0, first - 1, last + 1):
                ob.keyframe_insert('hide_render', frame=k); ob.keyframe_insert('hide_viewport', frame=k)
            for f, outside, _ in P['keys']:
                ob.hide_render = ob.hide_viewport = not outside
                ob.keyframe_insert('hide_render', frame=f); ob.keyframe_insert('hide_viewport', frame=f)
        for h, sign in P['hinges']:
            for f, _, ang in P['keys']:
                h.rotation_euler = (0, 0, math.radians(sign * ang)); h.keyframe_insert('rotation_euler', frame=f)
    prefs.keyframe_new_interpolation_type = old
    for ob in (cam, target, cam.data):                # hold the door picture until the cut
        act = ob.animation_data.action
        for fc in getattr(act, 'fcurves', None) or [fc for ly in act.layers for s in ly.strips for cb in s.channelbags for fc in cb.fcurves]:
            for k in fc.keyframe_points:
                if any(abs(k.co.x - sn) < 1e-3 for sn in snaps):
                    k.interpolation = 'CONSTANT'
    return cam, holds


# ---------------------------------------------------------------- checks
def run_checks(chars, holds, cam, T_END):
    from mathutils import Vector
    from bpy_extras.object_utils import world_to_camera_view
    sc = bpy.context.scene; bad = []
    by_place = {}
    for R in chars.values():
        by_place.setdefault(R['place'], []).append(R)

    def bbox(R, dg):
        """Each body part's box (arms, legs, head, accessories), so a raised arm near someone is not counted as touching."""
        parts = []
        for o in live(R)['root'].children_recursive:
            if o.type != 'MESH':
                continue
            oe = o.evaluated_get(dg); ps = [oe.matrix_world @ Vector(c) for c in oe.bound_box]
            parts.append(([min(p[k] for p in ps) for k in range(3)], [max(p[k] for p in ps) for k in range(3)]))
        return parts
    feet, over = {}, {}
    for f in range(1, round(T_END * FPS) + 1, 3):
        sc.frame_set(f); dg = bpy.context.evaluated_depsgraph_get()
        for R in chars.values():
            if R['head'].hide_render and not ('twin' in R and not R['twin']['head'].hide_render):
                continue                              # hidden now ('only', 'away'): not evaluated, its feet are stale
            low = min((o.evaluated_get(dg).matrix_world @ Vector(c)).z for o in R.get('ground_parts', R['feet'])
                      for c in o.evaluated_get(dg).bound_box) - R['base'][2]
            if low < -0.04 or (not R['air'].get(f) and low > 0.06):
                feet.setdefault(R['name'] + '@' + R['place'], []).append(f)
        shown = lambda R: not R['head'].hide_render or ('twin' in R and not R['twin']['head'].hide_render)
        for pl, rs in by_place.items():           # people hidden at this moment ('only', before a reveal) can't touch anyone
            boxes = [(R, bbox(R, dg)) for R in rs if shown(R)]
            for a in range(len(boxes)):
                for b in range(a + 1, len(boxes)):
                    if any(all(la[k] + 0.03 < hb[k] - 0.03 and lb[k] + 0.03 < ha[k] - 0.03 for k in range(3))
                           for la, ha in boxes[a][1] for lb, hb in boxes[b][1]):
                        over.setdefault(f"{boxes[a][0]['name']} vs {boxes[b][0]['name']} @{pl}", []).append(f)
    for k, v in feet.items():
        bad.append(f'FEET {k}: {len(v)} frames off, first {v[:4]}')
    for k, v in over.items():
        bad.append(f'OVERLAP {k}: {len(v)} frames, first {v[:4]}')
    for t0, t1, kind, subj, pl, *_ in holds:              # every framed character in the picture and facing the camera
        f = 1 + round((t0 + t1) / 2 * FPS); sc.frame_set(f)
        for R in (subj[1:] if kind == 'ots' else subj):        # over the shoulder: only the face we look at must show
            hd = lambda R, fr: Vector((*R['track'][fr][:2], R['track'][fr][2] + R['focus_z'])) if R.get('prop') else head_at(R, fr)
            x, y, z, turn = R['track'][f]; h = hd(R, f)
            v = world_to_camera_view(sc, cam, h)
            if not (0.05 < v.x < 0.95 and 0.05 < v.y < 0.95 and v.z > 0):
                bad.append(f'FRAME {kind} at {t0:.1f}s: {R["name"]} head is out of the picture ({v.x:.2f}, {v.y:.2f})')
            for te in (t0 + 0.05, max(t0 + 0.05, t1 - FLIGHT)):  # the camera moves through the framing: both ends must hold the face too
                fe = 1 + round(te * FPS); sc.frame_set(fe); ve = world_to_camera_view(sc, cam, hd(R, fe))
                if not (0.03 < ve.x < 0.97 and 0.03 < ve.y < 0.97 and ve.z > 0):
                    bad.append(f'FRAME {kind} at {te:.1f}s (move end): {R["name"]} head is out of the picture ({ve.x:.2f}, {ve.y:.2f})')
            sc.frame_set(f)
            mine = set(R['root'].children_recursive) | (set(R['twin']['root'].children_recursive) if 'twin' in R else set())
            blocked = []                                  # nothing stays between the camera and the face (someone passing is fine)
            for u in (0.25, 0.5, 0.75):
                fu = 1 + round((t0 + (t1 - t0) * u) * FPS); sc.frame_set(fu); dg = bpy.context.evaluated_depsgraph_get()
                hu = hd(R, fu); dg = bpy.context.evaluated_depsgraph_get(); o = cam.matrix_world.translation
                hit, _, _, _, ob, _ = sc.ray_cast(dg, o, (hu - o).normalized(), distance=(hu - o).length - 0.05)
                if hit and ob not in mine and ob.original not in mine:
                    top = ob.original
                    while top.parent:
                        top = top.parent
                    blocked.append(top.name)
            if len(blocked) >= 2 and R.get('kind') != 'mark':     # a mark is only an aim point: things may stand in front of it
                bad.append(f'BLOCKED {kind} at {t0:.1f}s: {blocked[0]} is between the camera and {R["name"]}')
            sc.frame_set(f)
            F = Vector((math.sin(math.radians(turn)), -math.cos(math.radians(turn)), 0)); to_cam = (cam.matrix_world.translation - h); to_cam.z = 0
            if to_cam.length and math.degrees(F.angle(to_cam.normalized())) > 110 and kind != 'ots' and not R.get('prop'):
                bad.append(f'FACE {kind} at {t0:.1f}s: {R["name"]} has their back to the camera')
    print('CHECKS:', 'all clear' if not bad else f'{len(bad)} problems')
    for b in bad:
        print('  ', b)
    return bad


if __name__ == '__main__':
    args = sys.argv[sys.argv.index('--') + 1:]
    table, OUT = args[0], args[1]; MODE = os.environ.get('MODE', 'full')
    meta, _ = parse(table)
    T = float(meta.get('length', 15))
    sc = reset(round(T * FPS))
    sc.view_settings.view_transform = 'Standard'; sc.view_settings.look = 'None'
    meta, T_END, places, chars, cams, where_is, props = build_scene(table)
    light(meta.get('light', 'day'))
    cam, holds = camera_track(cams, chars, places, where_is, T_END, props)
    sc.frame_end = round(T_END * FPS)
    shots = []                                        # shot k = camera row k; its frames include the flight into it
    for k, (t0, t1, kind, subj, pl, *_) in enumerate(holds, 1):
        f0, f1 = max(1, 1 + round((t0 - 0.5) * FPS)), min(sc.frame_end, 1 + round(t1 * FPS))
        shots.append((f0, f1)); print(f'SHOT {k}: {t0:.1f}-{t1:.1f} s, frames {f0}-{f1}, {kind} {", ".join(R["who"] for R in subj) or pl}')
    if MODE == 'check':
        run_checks(chars, holds, cam, T_END); sys.exit(0)
    os.makedirs(OUT, exist_ok=True)
    if MODE == 'preview':
        sc.render.resolution_percentage = 50; sc.eevee.taa_render_samples = 8; sc.render.use_motion_blur = False
    else:
        sc.render.use_motion_blur = True; sc.render.motion_blur_shutter = 0.5
        sc.eevee.taa_render_samples = int(os.environ.get('SAMPLES', QUALITY['samples']))      # speed A/B, 5 Nov 2026
        sc.eevee.use_raytracing = os.environ.get('RT', '1' if QUALITY['raytracing'] else '0') == '1'
    if os.environ.get('ENGINE') == 'cycles':
        cycles_look(sc)
    if os.environ.get('LOOK') in ('premium', 'chess'):   # the optional high-end looks: a pass over everything built above
        import premium
        cycles_look(sc); premium.apply(sc, places, chars, props, cam, holds, T_END, FLIGHT, look=os.environ['LOOK'])
    if MODE == 'stills':
        for f in map(int, os.environ['STILLS'].split(',')):
            render(os.path.join(OUT, f'still_{f:04d}.png'), f)
    elif os.environ.get('RANGE'):                     # one stretch of frames (RANGE=1-180): scripts/render_parallel.py runs several at once
        sc.frame_start, sc.frame_end = map(int, os.environ['RANGE'].split('-')); render(os.path.join(OUT, ''), None)
    elif os.environ.get('SHOTS'):                     # re-render only these shots into the same folder (e.g. SHOTS=3,5)
        for k in map(int, os.environ['SHOTS'].split(',')):
            sc.frame_start, sc.frame_end = shots[k - 1]; render(os.path.join(OUT, ''), None)
    else:
        render(os.path.join(OUT, ''), None)
