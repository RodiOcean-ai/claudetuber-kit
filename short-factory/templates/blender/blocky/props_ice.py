"""Clear-ice props for the blocky world (built 13 Nov 2026 for the nilered-ice episode: cloudy freezer ice vs one perfectly
clear block, frozen from the top down). Nothing carries a word, a letter, a number or a logo: every mark on them is a shape.
Each builder returns (P, objects) like the builders in props.py; P['setup'] runs once the prop has its root, P['actions'] maps
an action name to f(P, t, opt). scene.py registers BUILDERS and hands the builder the first row's keywords listed in KW; an
action row's options arrive as lists of numbers ('to 1 2 3' -> opt['to'] == [1.0, 2.0, 3.0]; a bare word -> True).
Every prop stands on its own origin (its bottom on z = 'at' Z: 0 on the floor, 1.15 on a table top), front toward -y.

Kinds, their actions and options (table rows: '| 0.0 | @name | kind | | at X Y Z; turn N | |', then '| t | @name | action | | options | |'):
- cube (one freezer ice cube, 0.30 across: a clear rounded shell, a soft milky cloud in the middle, trapped bubble dots, a faint
  crack): drop ('to X Y Z' = where its bottom lands, default 0.3 in front of it on the floor; or 'into @cup' = it floats in that
  glass, its top just above the water, with a splash; 'for S' flight time, default 0.35; 'splash' = a splash where it lands even
  without a cup): a small toss up, down, a 35-degree spin, a tiny bounce. In a hand: 'hold <who>; tilt 125' on its first row and
  the holder's move 'stand+show': it sits up on the fingertips beside the face (it takes the holder's size: the kid's is 78 %).
  A held cube that drops leaves the hand from exactly where the hand is at that moment (a free copy takes over, the held one hides).
  Camera: 'close @cube' fills about two-thirds of the picture's width. Held, the camera bank only knows where the hand is when a
  drop row follows (the drop fills that in); otherwise frame the holder. A camera row aims at where the prop is in the middle of
  that row, so a close-up over a drop is aimed at the landing spot: keep drops in a close-up short (about 0.3 sideways).
- tray (a white plastic ice-cube tray, 0.9 x 0.4, 2 x 6 cloudy cubes): static. In a hand: 'hold <who>; tilt 75' with 'stand+carry'
  (resting on the right hand in front of the chest, tipped toward the camera so the cubes show; 'tilt 55' is dead flat and seen
  edge-on). For 'close @tray' while held, give its first row 'at' about (holder x + 0.4, holder y - 0.85, 1.65) for a grown-up.
- cup (a drinking-glass tumbler, 0.42 across, 0.52 high, water to 0.36): static. P['inside'] = (0, 0, 0.10): the local point where a
  full-size cube's bottom lands (its top 4 cm above the water). Simplest: drop the cube with 'into @cup'.
- block (a big, perfectly clear ice block, 1.1 wide x 0.7 deep x 0.85 high, on a dark slate plinth; first row 'stand H' = plinth
  height, default 0.9, so the block's top is at 1.75, a grown-up's chest; 'stand 0' = no plinth; 'hidden' = it starts at scale
  0.001, and 'rise' on its own also hides it until the rise): rise (the block and plinth grow from nothing with a small overshoot,
  0.35 s) | sparkle (three star glints pop one after another on the top-left corner, the right edge and the top edge, 0.6 s).
- cooler (a cutaway 'freeze it from the top' cooler, 1.2 wide x 0.8 deep x 1.0 high on a stand whose top is at 0.6; blue insulated
  walls with the cut foam showing on the front edges, a clear glass front, light-blue water to 1.5, no lid): freeze ('for S',
  default 3.0): a layer of clear ice (pale, with glass shine streaks and a white front line) grows from the water's top surface
  DOWN to 80 % of the depth, quickly at first and slowing; the white air bubbles in the water are pushed down ahead of the front
  and gather at the bottom, where a milky white layer builds; a few cold mist puffs rise off the top at the start.
- pot (a steel cooking pot, 0.7 across, rim at 1.7, on a single gas burner on its own stand, top at 1.1): boil (from t 'until T',
  default the scene's end): blue flames lick out round the pot's base and light it blue, the burner ring glows, bubbles swell
  and pop on the water, white steam puffs rise and fade above the pot | pour ('into @cooler; for S', added 13 Nov 2026 so the
  boiling test reads as "boil the water, then freeze it"): the pot lifts, slides over the cooler's near wall, tips and pours a
  stream into it, then goes back on the burner. End the boil with 'until' at the pour. Put the cooler 1.2-1.5 away.
- cooler, more (13 Nov 2026): first row 'empty' = no water and no air bubbles until 'fill' ('for S', default 0.6: the water
  rises to its line); 'freeze' may follow the fill.
Framing (focus_z / size for '| t | camera | close | | @name | |'): cube 0.15 / 0.26, tray 0.07 / 0.42 (looks down on it), cup
0.27 / 0.34 (slightly from above), block stand + 0.38 / 0.82, cooler 1.12 / 0.86, pot 1.55 / 0.62 (from above, into the pot).
'medium' is about twice as wide as 'close'. Any first row may also say 'size N' to frame wider or tighter.

Looks: every ice, water and glass material here is built without a Principled BSDF (see-through body + glossy skin + glowing
cool edge), so it reads the same in the EEVEE previews and in LOOK=premium / chess; premium.py leaves such materials as built
(13 Nov 2026: no change to premium.py was needed).
Weak spots (13 Nov 2026): inside the cup's water the cube reads mostly by its cloudy middle, its edges are faint; EEVEE sorts
see-through things per object, so a cube in the cup's water can draw just in front of or behind the water as the camera moves;
'show' tilts a held cube 8 degrees and 'carry' tilts the tray 6 degrees sideways (the moves' arm swing); the cube's grip is made for
'show' only (with 'carry' it sits in the fist); 'hidden' and 'into @cup' are read from scene.py's build_props while it runs
('hidden 1' also works through KW)."""
import math, random, sys
import bpy
from mathutils import Vector, Euler
from common import FPS, hexrgb
from sf_world import box, cyl, empty, parent
from blocky_kit import M
from props import _keys, _sphere, visible, F

ss = lambda u: 0 if u <= 0 else 1 if u >= 1 else u * u * (3 - 2 * u)
KW = {'block': {'stand': float, 'hidden': float}}       # first-row keywords a table may pass to a builder


# ---------------------------------------------------------------- helpers
def _num(o, key, default, i=0):
    v = o.get(key)
    return v[i] if isinstance(v, list) and len(v) > i and isinstance(v[i], float) else default


def _from_table(name):
    """A value from scene.py's build_props while it builds the props: 'opt' (the row's options as read) or 'props' (every
    prop built so far). A bare first-row word ('hidden') never reaches a builder through KW (scene.py only passes words with a
    value), and an action cannot see the other props; both are read here."""
    f = sys._getframe(1)
    while f is not None:
        if f.f_code.co_name == 'build_props' and isinstance(f.f_locals.get(name), dict):
            return f.f_locals[name]
        f = f.f_back
    return {}


def _row_words():
    return _from_table('opt')


def _group(name, objs, loc=(0, 0, 0)):
    g = empty(name, loc); parent(objs, g)
    return g


def _stay(P, t):
    if 'track' in P:
        for f in range(F(t), max(P['track']) + 1):
            P['track'][f] = (*P['loc'], P['turn'])


def _socket_keys(sock, pts):
    for t, v in pts:
        sock.default_value = v; sock.keyframe_insert('default_value', frame=F(t))


def _tube(loc, r, depth, m, wall, verts=64):
    """An open-ended round wall (a glass, a pot): a cylinder without caps, thickened inward."""
    bpy.ops.mesh.primitive_cylinder_add(radius=r, depth=depth, location=loc, vertices=verts, end_fill_type='NOTHING')
    o = bpy.context.object; o.data.materials.append(m); bpy.ops.object.shade_smooth()
    s = o.modifiers.new('wall', 'SOLIDIFY'); s.thickness = wall; s.offset = -1.0; s.use_even_offset = True
    return o


def _torus(loc, R, r, m, segs=64):
    bpy.ops.mesh.primitive_torus_add(major_radius=R, minor_radius=r, location=loc, major_segments=segs, minor_segments=12)
    o = bpy.context.object; o.data.materials.append(m); bpy.ops.object.shade_smooth()
    return o


def _cone(loc, r1, r2, depth, m, rot=(0, 0, 0), verts=16):
    bpy.ops.mesh.primitive_cone_add(radius1=r1, radius2=r2, depth=depth, location=loc, vertices=verts, rotation=tuple(math.radians(a) for a in rot))
    o = bpy.context.object; o.data.materials.append(m); bpy.ops.object.shade_smooth()
    return o


# ---------------------------------------------------------------- materials
# None of these has a Principled BSDF, so premium.py (LOOK=premium / chess) leaves them exactly as built: they read the same in
# the EEVEE previews and in Cycles.
def _node(nt, kind, **inputs):
    n = nt.nodes.new(kind)
    for k, v in inputs.items():
        n.inputs[k.replace('_', ' ')].default_value = v
    return n


def _mix(nt, fac, a, b):
    mx = nt.nodes.new('ShaderNodeMixShader')
    if isinstance(fac, (int, float)):
        mx.inputs[0].default_value = fac
    else:
        nt.links.new(fac, mx.inputs[0])
    nt.links.new(a, mx.inputs[1]); nt.links.new(b, mx.inputs[2])
    return mx.outputs[0]


def _math(nt, op, a, b, clamp=True):
    n = nt.nodes.new('ShaderNodeMath'); n.operation = op; n.use_clamp = clamp
    for i, v in enumerate((a, b)):
        if isinstance(v, (int, float)):
            n.inputs[i].default_value = v
        else:
            nt.links.new(v, n.inputs[i])
    return n.outputs[0]


_MATS = {}


def _clear(name, tint='#eef9ff', milk=0.05, milk_col='#ffffff', rim_col='#bfeaff', rim=1.6, rim_pow=2.2, gloss=0.6, blend=0.3):
    """See-through ice, glass or water: a tinted clear body (plus 'milk', a little white haze), a glossy skin at grazing angles
    and a glowing cool edge (the bevels and the outline light up, so it reads as ice against any background)."""
    if name in _MATS:
        return _MATS[name]
    m = bpy.data.materials.new(name); m.use_nodes = True; nt = m.node_tree; nt.nodes.clear()
    out = nt.nodes.new('ShaderNodeOutputMaterial')
    tr = _node(nt, 'ShaderNodeBsdfTransparent', Color=(*hexrgb(tint), 1))
    df = _node(nt, 'ShaderNodeBsdfDiffuse', Color=(*hexrgb(milk_col), 1))
    gl = _node(nt, 'ShaderNodeBsdfGlossy', Roughness=0.04)
    em = _node(nt, 'ShaderNodeEmission', Color=(*hexrgb(rim_col), 1), Strength=rim); em.name = 'Rim'
    lw = _node(nt, 'ShaderNodeLayerWeight', Blend=blend)
    body = _mix(nt, milk, tr.outputs[0], df.outputs[0])
    skin = _mix(nt, _math(nt, 'MULTIPLY', lw.outputs['Fresnel'], gloss), body, gl.outputs[0])
    edge = _mix(nt, _math(nt, 'POWER', lw.outputs['Facing'], rim_pow), skin, em.outputs[0])
    nt.links.new(edge, out.inputs['Surface'])
    m.surface_render_method = 'BLENDED'; m.use_backface_culling = False
    for k, v in (('use_transparency_overlap', True), ('use_transparent_shadow', True)):
        try:
            setattr(m, k, v)
        except Exception:
            pass
    _MATS[name] = m
    return m


def _cloud(name, col='#ffffff', soft=1.0, emit=0.3, blended=False):
    """Milky white with soft edges: solid in the middle, fading at the outline (the cloudy core, steam, cold mist).
    Inside a clear shell it is drawn with the solid things (dithered), so the shell lies over it in EEVEE."""
    if name in _MATS:
        return _MATS[name]
    m = bpy.data.materials.new(name); m.use_nodes = True; nt = m.node_tree; nt.nodes.clear()
    out = nt.nodes.new('ShaderNodeOutputMaterial')
    tr = _node(nt, 'ShaderNodeBsdfTransparent', Color=(1, 1, 1, 1))
    df = _node(nt, 'ShaderNodeBsdfDiffuse', Color=(*hexrgb(col), 1))
    em = _node(nt, 'ShaderNodeEmission', Color=(*hexrgb(col), 1), Strength=emit)
    add = nt.nodes.new('ShaderNodeAddShader'); nt.links.new(df.outputs[0], add.inputs[0]); nt.links.new(em.outputs[0], add.inputs[1])
    lw = _node(nt, 'ShaderNodeLayerWeight', Blend=0.5)
    solid = _math(nt, 'POWER', _math(nt, 'SUBTRACT', 1.0, lw.outputs['Facing']), soft)
    nt.links.new(_mix(nt, solid, tr.outputs[0], add.outputs[0]), out.inputs['Surface'])
    m.surface_render_method = 'BLENDED' if blended else 'DITHERED'; m.use_backface_culling = True
    _MATS[name] = m
    return m


def _glow(name, col='#ffffff', strength=8.0):
    if name in _MATS:
        return _MATS[name]
    m = bpy.data.materials.new(name); m.use_nodes = True; nt = m.node_tree; nt.nodes.clear()
    out = nt.nodes.new('ShaderNodeOutputMaterial'); em = _node(nt, 'ShaderNodeEmission', Color=(*hexrgb(col), 1), Strength=strength)
    nt.links.new(em.outputs[0], out.inputs['Surface']); _MATS[name] = m
    return m


def _shine(name='IceShine', strength=1.5, alpha=0.38):
    """A cartoon glass shine: a pale see-through streak (two of them on a face say 'solid and clear')."""
    if name in _MATS:
        return _MATS[name]
    m = bpy.data.materials.new(name); m.use_nodes = True; nt = m.node_tree; nt.nodes.clear()
    out = nt.nodes.new('ShaderNodeOutputMaterial')
    tr = _node(nt, 'ShaderNodeBsdfTransparent', Color=(1, 1, 1, 1)); em = _node(nt, 'ShaderNodeEmission', Color=(1, 1, 1, 1), Strength=strength)
    nt.links.new(_mix(nt, alpha, tr.outputs[0], em.outputs[0]), out.inputs['Surface'])
    m.surface_render_method = 'BLENDED'; m.use_backface_culling = False; _MATS[name] = m
    return m


def _streaks(x, y, z, L, k=1.0, ang=38):
    """Two parallel diagonal shine streaks on a face that looks toward -y, centred near (x, z)."""
    out = []
    for dx, w in ((0.0, 0.07 * k), (0.11 * k, 0.025 * k)):
        o = box((x + dx, y, z), (w, 0.003, L), _shine(), rot=(0, ang, 0), bevel=0); o.visible_shadow = False; out.append(o)
    return out


def ice_shell():
    return _clear('IceShell', tint='#e2f5ff', milk=0.17, milk_col='#eef9ff', rim_col='#e2f6ff', rim=2.7, rim_pow=1.35, gloss=0.7)


def ice_clear():
    return _clear('IceClear', tint='#e6f6ff', milk=0.05, milk_col='#d4f0ff', rim_col='#a9e4ff', rim=2.4, rim_pow=2.4, gloss=0.8, blend=0.25)


def ice_core():
    return _cloud('IceCore', '#f4f9fc', soft=1.3, emit=0.4)


# ---------------------------------------------------------------- the freezer cube
CUBE = 0.30                                              # across (fits a 'cup' with room to spare)
GRIP_SHOW = (0.0, -0.06, 0.92)                           # in the hand with 'show' and 'tilt 125': up on the fingertips


def _cloudy_cube(s=CUBE, seed=3, detail=True, z0=0.0, xy=(0.0, 0.0)):
    """A freezer ice cube standing on z0 around (x, y): a clear rounded shell, a soft milky cloud in the middle, a sprinkle of
    trapped bubble dots in the cloud and a faint crack line near one corner."""
    rnd = random.Random(seed); x0, y0 = xy; c = (x0, y0, z0 + s / 2)
    shell = box(c, (s, s, s), ice_shell(), bevel=s * 0.2); shell.modifiers['bev'].segments = 4
    core = _sphere(c, s * 0.33, ice_core(), segs=32); core.scale = (1.08, 0.9, 1.0); core.visible_shadow = False
    parts = [shell, core]
    if detail:
        inner = _sphere(c, s * 0.2, _cloud('IceCoreDense', '#ffffff', soft=0.6, emit=0.5), segs=24); inner.visible_shadow = False
        parts.append(inner)                                             # denser in the very middle
        dot = M('#ffffff', 0.3, emit=hexrgb('#ffffff'), emit_strength=0.6)
        for k in range(14):                                            # trapped bubbles, mostly on the cloud's front
            a = rnd.uniform(0, 2 * math.pi); r = rnd.uniform(0.08, 0.36) * s
            d = _sphere((c[0] + r * math.cos(a), c[1] - rnd.uniform(0.18, 0.34) * s, c[2] + r * math.sin(a)), s * rnd.uniform(0.016, 0.03), dot, segs=10)
            d.visible_shadow = False; parts.append(d)
        cr = box((c[0] - s * 0.27, c[1] - s * 0.38, c[2] + s * 0.26), (s * 0.22, 0.002, s * 0.012), _shine('IceCrack', 1.2, 0.6), rot=(0, 28, 0), bevel=0)
        cr.visible_shadow = False; parts.append(cr)                     # a faint crack near the top-left corner
    return parts


def cube():
    """One freezer ice cube (0.30 across, its bottom on z=0)."""
    P = {'focus_z': CUBE / 2, 'size': 0.26, 'grip': GRIP_SHOW, 'actions': {}}

    def drop(P, t, o):
        dur = max(0.15, _num(o, 'for', 0.35)); sc = bpy.context.scene; held = P.get('held')
        if held and held[1] <= t < held[2]:
            R, t0, t1 = held; now = sc.frame_current; marks = {}
            for f in sorted(set(range(max(1, F(t0)), F(t), 3)) | {F(t)}):   # where it rides in the hand: the camera bank finds it
                sc.frame_set(f); marks[f] = P['root'].matrix_world.copy()
            sc.frame_set(now)
            fs = sorted(marks)
            for a, b in zip(fs, fs[1:] + [fs[-1]]):
                pa, pb = marks[a].translation, marks[b].translation
                for f in range(a, b + 1):
                    u = (f - a) / max(1, b - a); P['track'][f] = (*(pa + (pb - pa) * u), P['turn'])
            loc0, q0, s0 = marks[F(t)].decompose()
            node = _group(P['name'] + '_free', _cloudy_cube(), (0, 0, 0))
            turn0 = math.degrees(q0.to_euler('XYZ').z); e0 = q0.to_euler('XYZ', Euler((0, 0, math.radians(turn0))))
            node.location = loc0; node.rotation_euler = e0; node.scale = s0; k = s0.x
            visible([P['root']], [(t, False)]); visible([node], [(0, False), (t, True)])
        else:
            node = P['root']; loc0 = Vector(P['loc']); turn0 = P['turn']; e0 = Euler((0, 0, math.radians(turn0))); k = 1.0
        into = o.get('into'); cupP = None
        if isinstance(into, list) and into:                              # 'into @cup': floats in that glass, top just above the water
            cupP = _from_table('props').get(str(into[0]).lower())
        if cupP is not None and 'inside' in cupP:
            c = Vector(cupP['loc']); to = c + Vector((0, 0, CUP_WATER + 0.04 - CUBE * k))
        else:
            to = Vector(o['to'][:3]) if isinstance(o.get('to'), list) and len(o['to']) >= 3 else Vector((loc0.x, loc0.y - 0.3, 0.0))
        if cupP is not None or o.get('splash'):                          # water jumps out over the rim
            wz = (Vector(cupP['loc']).z + CUP_WATER) if cupP is not None else to.z; c = Vector(cupP['loc']) if cupP is not None else to
            sm = _clear('WaterSplash', tint='#bfe9ff', milk=0.5, milk_col='#9fdcff', rim_col='#ffffff', rim=1.2, rim_pow=1.5, gloss=0.6)
            tl = t + dur; rr = random.Random(F(t))
            for i in range(9):
                a = 2 * math.pi * i / 9 + rr.uniform(-0.2, 0.2); ca, sa = math.cos(a), math.sin(a); up = rr.uniform(0.16, 0.3)
                d = _sphere((0, 0, 0), rr.uniform(0.014, 0.022), sm, segs=16); d.visible_shadow = False
                _keys(d, 'location', [(tl - 0.04, (c.x + 0.1 * ca, c.y + 0.1 * sa, wz)), (tl + 0.16, (c.x + 0.2 * ca, c.y + 0.2 * sa, wz + up)),
                                      (tl + 0.4, (c.x + 0.29 * ca, c.y + 0.29 * sa, wz - 0.12))], 'LINEAR')
                _keys(d, 'scale', [(tl - 0.08, (0.001,) * 3), (tl + 0.02, (1, 1, 1)), (tl + 0.33, (1, 1, 1)), (tl + 0.42, (0.001,) * 3)], 'LINEAR')
        h = 0.1 + 0.15 * min(1.0, (to - loc0).length)                       # a small toss, then down
        t_end = 35.0 + turn0
        locs, rots = [], []
        for f in range(F(t), F(t + dur + 0.3) + 1):
            tt = (f - 1) / FPS; u = min(1.0, (tt - t) / dur); d = tt - t - dur
            p = loc0 + (to - loc0) * u + Vector((0, 0, 4 * h * u * (1 - u)))
            if d > 0:                                                    # a tiny bounce on landing
                p = Vector(to) + Vector((0, 0, k * (0.045 * abs(math.sin(math.pi * d / 0.16)) if d < 0.16 else 0.012 * abs(math.sin(math.pi * (d - 0.16) / 0.1)) if d < 0.26 else 0.0)))
            e = ss(u); rz = math.radians(turn0 + (t_end - turn0) * e)
            locs.append((tt, tuple(p))); rots.append((tt, (e0.x * (1 - e), e0.y * (1 - e), rz)))
            if 'track' in P:
                P['track'][f] = (*p, turn0 + (t_end - turn0) * e)
        _keys(node, 'location', locs, 'LINEAR'); _keys(node, 'rotation_euler', rots, 'LINEAR')
        P['loc'] = tuple(to); P['turn'] = t_end; _stay(P, t + dur + 0.31)
    P['actions']['drop'] = drop
    return P, _cloudy_cube()


# ---------------------------------------------------------------- the ice-cube tray
GRIP_CARRY = (-0.35, -0.24, 1.05)                        # with 'carry' and 'tilt 55': flat on the hand, in front of the chest


def tray():
    """A white plastic tray (0.9 x 0.4, 0.09 deep) of 2 x 6 cloudy cubes, its bottom on z=0."""
    white, wall = M('#f6f8fb', 0.35), 0.022
    W, D, H, nx, ny = 0.9, 0.4, 0.09, 6, 2
    parts = [box((0, 0, 0.012), (W, D, 0.024), white, bevel=0.008)]
    for sy in (-1, 1):
        parts.append(box((0, sy * (D / 2 - wall / 2), H / 2), (W, wall, H), white, bevel=0.008))
    for sx in (-1, 1):
        parts.append(box((sx * (W / 2 - wall / 2), 0, H / 2), (wall, D, H), white, bevel=0.008))
        parts.append(box((sx * (W / 2 + 0.03), 0, H - 0.01), (0.07, D * 0.7, 0.018), white, bevel=0.006))   # the end tabs
    cw, cd = (W - wall) / nx, (D - wall) / ny
    for i in range(1, nx):
        parts.append(box((-W / 2 + wall / 2 + i * cw, 0, H * 0.42), (0.014, D - wall, H * 0.84), white, bevel=0.004))
    parts.append(box((0, 0, H * 0.42), (W - wall, 0.014, H * 0.84), white, bevel=0.004))
    s = 0.11
    for i in range(nx):
        for j in range(ny):
            parts += _cloudy_cube(s, seed=i * 2 + j, detail=False, z0=0.024, xy=(-W / 2 + wall / 2 + (i + 0.5) * cw, -D / 2 + wall / 2 + (j + 0.5) * cd))
    return {'focus_z': 0.07, 'size': 0.42, 'grip': GRIP_CARRY, 'view_up': 0.45}, parts


# ---------------------------------------------------------------- the drinking glass
CUP_R, CUP_H, CUP_WATER = 0.21, 0.52, 0.36


def cup():
    """A drinking-glass tumbler (0.42 across, 0.52 high) two-thirds full of water; P['inside'] is the local point where a
    dropped cube's bottom lands (it floats with its top just above the water)."""
    glass = _clear('IceCupGlass', tint='#f4fbff', milk=0.03, rim_col='#ffffff', rim=1.1, rim_pow=2.4, gloss=0.9)
    water = _clear('WaterCup', tint='#a6e0ff', milk=0.07, milk_col='#6cc4f5', rim_col='#d8f3ff', rim=0.8, rim_pow=2.0, gloss=0.5)
    base, wall = 0.05, 0.016
    parts = [_tube((0, 0, base + (CUP_H - base) / 2), CUP_R, CUP_H - base, glass, wall), cyl((0, 0, base / 2), CUP_R, base, glass, verts=64),
             _torus((0, 0, CUP_H), CUP_R - wall / 2, wall / 2 + 0.002, glass),
             cyl((0, 0, (base + CUP_WATER) / 2 + 0.001), CUP_R - wall - 0.004, CUP_WATER - base, water, verts=64)]
    for o in parts:
        o.visible_shadow = False
    return {'focus_z': 0.27, 'size': 0.34, 'view_up': 0.3, 'inside': (0.0, 0.0, CUP_WATER + 0.04 - CUBE)}, parts


# ---------------------------------------------------------------- the perfectly clear block
BLOCK = (1.1, 0.7, 0.85)


def _star(loc, k=1.0):
    """A four-pointed glint in the x-z plane (seen from the front)."""
    w = _glow('IceGlint', '#ffffff', 12.0)
    a = _sphere((0, 0, 0), 1.0, w, segs=12); a.scale = (0.15 * k, 0.006, 0.016 * k)
    b = _sphere((0, 0, 0), 1.0, w, segs=12); b.scale = (0.016 * k, 0.006, 0.15 * k)
    c = _sphere((0, 0, 0), 0.03 * k, w, segs=12)
    for o in (a, b, c):
        o.visible_shadow = False
    g = _group('IceGlint', [a, b, c], (0, 0, 0)); g.location = loc; g.scale = (0.001,) * 3
    return g


def block(stand=0.9, hidden=0.0):
    """A big, perfectly clear ice block (1.1 x 0.7 x 0.85) on a dark slate plinth 'stand' high."""
    hidden = hidden or 'hidden' in _row_words()
    W, D, H = BLOCK; slate, edge = M('#343b48', 0.5), M('#454e5e', 0.4)
    parts = [box((0, 0, 0.03), (1.34, 0.94, 0.06), M('#262b35', 0.55), bevel=0.015)] if stand > 0.12 else []
    if stand > 0:
        parts += [box((0, 0, stand / 2), (1.28, 0.88, stand), slate, bevel=0.03), box((0, 0, stand - 0.02), (1.34, 0.94, 0.04), edge, bevel=0.012)]
    blk = box((0, 0, stand + H / 2 + 0.001), (W, D, H), ice_clear(), bevel=0.05); blk.modifiers['bev'].segments = 2
    parts += [blk] + _streaks(-0.22, -D / 2 - 0.004, stand + H * 0.58, 0.62)
    stars = [_star((-W / 2 + 0.02, -D / 2 - 0.01, stand + H - 0.03), 1.0), _star((W / 2 - 0.01, -D / 2 - 0.01, stand + 0.3), 0.8),
             _star((0.18, -D / 2 - 0.01, stand + H + 0.005), 0.7)]
    P = {'focus_z': stand + 0.38, 'size': 0.82, 'stars': stars, 'actions': {}}
    if hidden:
        P['setup'] = lambda P: setattr(P['root'], 'scale', (0.001,) * 3)

    def rise(P, t, o):
        _keys(P['root'], 'scale', [(t, (0.001,) * 3), (t + 0.22, (1.12,) * 3), (t + 0.35, (1.0,) * 3)])

    def sparkle(P, t, o):
        for i, g in enumerate(P['stars']):
            t0 = t + 0.16 * i
            _keys(g, 'scale', [(t0 - 0.01, (0.001,) * 3), (t0 + 0.09, (1.25,) * 3), (t0 + 0.16, (1.0,) * 3), (t0 + 0.28, (0.001,) * 3)])
            _keys(g, 'rotation_euler', [(t0, (0, 0, 0)), (t0 + 0.28, (0, math.radians(40), 0))], 'LINEAR')
    P['actions'].update(rise=rise, sparkle=sparkle)
    return P, parts + stars


# ---------------------------------------------------------------- the freeze-it-from-the-top cooler
CZ0, CW, CD, CH, CT = 0.6, 1.2, 0.8, 1.0, 0.1            # stand top, cooler width, depth, height, wall
WATER_TOP, WATER_DEPTH, ICE_FRAC, MILK_H = CZ0 + CT + 0.8, 0.8, 0.8, 0.11


def cooler():
    """A cutaway cooler on a stand: blue insulated walls (the cut foam shows on the front edges), a clear glass front, light-blue
    water inside, no lid."""
    blue, liner, foam, white = M('#2f7de0', 0.4), M('#f2f7fb', 0.5), M('#ffe9a8', 0.85), M('#ffffff', 0.4)
    cart, dark = M('#dde6ee', 0.45), M('#4b5566', 0.5)
    parts = [box((0, 0, 0.04), (1.24, 0.84, 0.08), dark, bevel=0.02), box((0, 0, 0.33), (1.3, 0.9, 0.5), cart, bevel=0.04),
             box((0, 0, CZ0 - 0.025), (1.36, 0.96, 0.05), dark, bevel=0.015)]                          # the stand, top at 0.6
    zc = CZ0 + CH / 2; iw = CW - 2 * CT
    parts += [box((0, 0, CZ0 + CT / 2), (CW, CD, CT), blue, bevel=0.03), box((0, CD / 2 - CT / 2, zc), (CW, CT, CH), blue, bevel=0.03)]
    for sx in (-1, 1):
        parts.append(box((sx * (CW / 2 - CT / 2), 0, zc), (CT, CD, CH), blue, bevel=0.03))
        parts.append(box((sx * (CW / 2 - CT / 2), -CD / 2 - 0.002, zc), (CT * 0.55, 0.006, CH - 0.05), foam, bevel=0))   # cut foam
        parts.append(box((sx * (CW / 2 + 0.03), 0.0, CZ0 + 0.72), (0.06, 0.34, 0.08), dark, bevel=0.025))                # handles
        parts.append(box((sx * (CW / 2 - CT / 2), 0, CZ0 + CH + 0.012), (CT + 0.02, CD + 0.02, 0.03), white, bevel=0.01))
        parts.append(box((sx * (iw / 2 - 0.004), 0.0, zc + CT / 2), (0.008, CD - CT - 0.05, CH - CT), liner, bevel=0))
    parts += [box((0, CD / 2 - CT / 2, CZ0 + CH + 0.012), (CW + 0.02, CT + 0.02, 0.03), white, bevel=0.01),
              box((0, -CD / 2 - 0.002, CZ0 + CT / 2), (CW - 0.05, 0.006, CT * 0.55), foam, bevel=0),
              box((0, CD / 2 - CT - 0.004, zc + CT / 2), (iw, 0.008, CH - CT), liner, bevel=0),
              box((0, 0, CZ0 + CT + 0.004), (iw, CD - CT - 0.05, 0.008), liner, bevel=0)]
    glass = _clear('IceCoolerGlass', tint='#f6fcff', milk=0.02, rim_col='#ffffff', rim=0.9, rim_pow=3.0, gloss=0.9)
    gy = -CD / 2 + 0.02
    pane = box((0, gy, zc + CT / 2), (iw + 0.01, 0.02, CH - CT), glass, bevel=0.004); pane.visible_shadow = False
    parts += [pane, box((0, gy, CZ0 + CH + 0.012), (iw + 0.02, 0.04, 0.03), white, bevel=0.01)]
    y_in0, y_in1 = gy + 0.012, CD / 2 - CT - 0.008; yc, dep = (y_in0 + y_in1) / 2, y_in1 - y_in0
    water = box((0, yc, WATER_DEPTH / 2), (iw - 0.02, dep, WATER_DEPTH), _clear('WaterCooler', tint='#62c2ff', milk=0.28, milk_col='#45b0f4',
                rim_col='#dff6ff', rim=0.6, rim_pow=2.5, gloss=0.4), bevel=0)
    water_g = _group('CoolerWater', [water], (0, 0, 0)); water_g.location = (0, 0, CZ0 + CT)
    ih = WATER_DEPTH * ICE_FRAC
    ice = box((0, yc, -ih / 2), (iw - 0.02, dep, ih), _clear('IceCooler', tint='#d8f3ff', milk=0.2, milk_col='#e9f9ff',
              rim_col='#ffffff', rim=1.6, rim_pow=1.6, gloss=0.8), bevel=0.03)
    ice_g = _group('CoolerIce', [ice] + _streaks(-0.24, y_in0 + 0.006, -ih * 0.45, ih * 0.9, k=1.1) + _streaks(0.26, y_in0 + 0.006, -ih * 0.6, ih * 0.6, k=0.7),
                   (0, 0, 0))
    ice_g.location = (0, 0, WATER_TOP); ice_g.scale = (1, 1, 0.001)
    line = box((0, y_in0 + 0.025, 0), (iw - 0.018, 0.04, 0.022), M('#ffffff', 0.3, emit=hexrgb('#e4f8ff'), emit_strength=1.4), bevel=0.006)
    line_g = _group('CoolerFront', [line], (0, 0, 0)); line_g.location = (0, 0, WATER_TOP); line_g.scale = (0.001,) * 3
    milk = box((0, yc, MILK_H / 2), (iw - 0.022, dep - 0.002, MILK_H), _cloud('IceMilk', '#f4f9fc', soft=0.15, emit=0.35), bevel=0.01)
    milk_g = _group('CoolerMilk', [milk], (0, 0, 0)); milk_g.location = (0, 0, CZ0 + CT); milk_g.scale = (1, 1, 0.001)
    rnd = random.Random(11); bub_m = M('#ffffff', 0.3, emit=hexrgb('#ffffff'), emit_strength=0.6); bubbles = []
    for k in range(30):
        r = rnd.uniform(0.016, 0.03); p = (rnd.uniform(-0.45, 0.45), rnd.uniform(y_in0 + 0.03, y_in0 + 0.22), rnd.uniform(CZ0 + CT + 0.12, WATER_TOP - 0.05))
        b = _sphere(p, r, bub_m, segs=12); b.visible_shadow = False; bubbles.append((b, p, r))
    mist_m = _cloud('IceMist', '#ffffff', soft=2.6, emit=0.5, blended=True); mist = []
    for k in range(7):
        m = _sphere((0, 0, 0), 0.12, mist_m, segs=16); m.visible_shadow = False; m.location = (rnd.uniform(-0.4, 0.4), rnd.uniform(-0.2, 0.2), CZ0 + CH)
        m.scale = (0.001,) * 3; mist.append(m)
    P = {'focus_z': 1.12, 'size': 0.86, 'ice': ice_g, 'water': water_g, 'line': line_g, 'milk': milk_g, 'bubbles': bubbles, 'mist': mist, 'actions': {}}
    if 'empty' in _row_words():                       # first row 'empty': no water (and no air bubbles) until 'fill'
        water_g.scale = (1, 1, 0.001)
        for b, _, _ in bubbles:
            b.scale = (0.001,) * 3

    def fill(P, t, o):                                # the water rises from the bottom to its line ('for S', default 0.6)
        S = max(0.1, _num(o, 'for', 0.6))
        _keys(P['water'], 'scale', [(t - 0.01, (1, 1, 0.001)), (t + S, (1, 1, 1))], 'LINEAR')
    P['actions']['fill'] = fill

    def freeze(P, t, o):
        S = max(0.5, _num(o, 'for', 3.0)); grow = WATER_DEPTH * ICE_FRAC
        prog = lambda tt: 1 - (1 - min(1.0, max(0.0, (tt - t) / S))) ** 1.5          # fast at first, slowing as it thickens
        front = lambda tt: WATER_TOP - grow * prog(tt)
        fr = list(range(F(t), F(t + S) + 1, 2)) + [F(t + S)]
        floor = CZ0 + CT
        milk_h = lambda tt: max(0.001, ss((tt - t - 0.35 * S) / (0.75 * S)))
        fm = fr + [F(t + 1.1 * S)]
        _keys(P['ice'], 'scale', [((f - 1) / FPS, (1, 1, max(0.001, prog((f - 1) / FPS)))) for f in fr], 'LINEAR')
        _keys(P['milk'], 'scale', [((f - 1) / FPS, (1, 1, milk_h((f - 1) / FPS))) for f in fm], 'LINEAR')
        # the water lies between the milky layer and the ice front (nothing blue in front of the milk)
        _keys(P['water'], 'location', [((f - 1) / FPS, (0, 0, floor + MILK_H * milk_h((f - 1) / FPS))) for f in fm], 'LINEAR')
        _keys(P['water'], 'scale', [((f - 1) / FPS, (1, 1, (front((f - 1) / FPS) - floor - MILK_H * milk_h((f - 1) / FPS)) / WATER_DEPTH)) for f in fm], 'LINEAR')
        _keys(P['line'], 'location', [((f - 1) / FPS, (0, 0, front((f - 1) / FPS))) for f in fr], 'LINEAR')
        _keys(P['line'], 'scale', [(t - 0.01, (0.001,) * 3), (t + 0.08, (1, 1, 1))], 'LINEAR')
        for k, (b, p, r) in enumerate(P['bubbles']):                     # pushed down ahead of the ice, gathering at the bottom
            rest = floor + MILK_H * 0.6 + r + (k % 4) * 0.014             # half sunk into the milky layer's top
            pts = []
            for f in range(F(t), F(t + 1.15 * S) + 1, 2):
                tt = (f - 1) / FPS; u = min(1.0, (tt - t) / S)
                z = min(p[2] - 0.08 * u, front(tt) - 0.03 - r)
                z = max(z, rest) if tt < t + S else rest + (max(min(p[2] - 0.08, front(t + S) - 0.03 - r), rest) - rest) * (1 - ss((tt - t - S) / (0.15 * S)))
                pts.append((tt, (p[0] + 0.012 * math.sin(3.0 * tt + k), p[1], z)))
            _keys(b, 'location', pts, 'LINEAR')
        for k, m in enumerate(P['mist']):                                # cold mist puffs off the top at the start
            t0 = t + 0.09 * k; x, y, _ = m.location
            _keys(m, 'location', [(t0, (x, y, CZ0 + CH - 0.02)), (t0 + 1.3, (x * 1.25, y - 0.1, CZ0 + CH + 0.55 + 0.05 * k))], 'LINEAR')
            _keys(m, 'scale', [(t0 - 0.01, (0.001,) * 3), (t0 + 0.15, (0.6, 0.6, 0.45)), (t0 + 0.75, (1.3, 1.3, 0.9)), (t0 + 1.3, (0.001,) * 3)])
    P['actions']['freeze'] = freeze
    return P, parts + [water_g, ice_g, line_g, milk_g] + [b for b, _, _ in bubbles] + mist


# ---------------------------------------------------------------- the pot on a gas burner
POT_Z, POT_R, POT_H, POT_WATER = 1.28, 0.35, 0.42, 1.64


def pot():
    """A steel cooking pot (0.7 across) of water on a single gas burner, on its own stand (top at 1.1)."""
    body, top, dark, black = M('#e8edf2', 0.5), M('#3a4252', 0.45), M('#5b6677', 0.5), M('#202329', 0.5)
    steel = M('#b4bcc7', 0.38, metal=0.75)                 # brushed, so the bright lab does not mirror in it like glass
    parts = [box((0, 0, 0.04), (0.84, 0.74, 0.08), dark, bevel=0.02), box((0, 0, 0.57), (0.9, 0.8, 1.0), body, bevel=0.04),
             box((0, 0, 1.075), (0.96, 0.86, 0.05), top, bevel=0.015), box((0, -0.401, 0.6), (0.012, 0.006, 0.8), dark, bevel=0),
             box((0.09, -0.41, 0.85), (0.04, 0.02, 0.16), dark, bevel=0.008), box((-0.09, -0.41, 0.85), (0.04, 0.02, 0.16), dark, bevel=0.008)]
    parts += [box((0, 0, 1.15), (0.8, 0.8, 0.1), black, bevel=0.03), cyl((0, 0, 1.215), 0.12, 0.03, M('#121418', 0.4), verts=32),
              cyl((0.26, -0.41, 1.15), 0.045, 0.04, M('#e63946', 0.4), rot=(90, 0, 0), verts=24)]                      # burner, cap, knob
    for k in range(4):
        a = math.radians(45 + 90 * k)
        parts.append(box((0.24 * math.cos(a), 0.24 * math.sin(a), 1.245), (0.26, 0.03, 0.07), black, rot=(0, 0, math.degrees(a)), bevel=0.008))   # the grate
    glow = M('#2a3a66', 0.4, emit=hexrgb('#2f8dff'), emit_strength=0.0).copy(); glow.name = 'BurnerGlow'
    ring = _torus((0, 0, 1.232), 0.124, 0.014, glow, segs=48)
    flame_m = _glow('IceFlame', '#3d9bff', 6.0); flames = []
    for k in range(22):                                                   # on high: blue tongues lick out round the pot's base
        a = 2 * math.pi * (k + 0.5) / 22
        f = _cone((0.355 * math.cos(a), 0.355 * math.sin(a), 0.05), 0.026, 0.0, 0.12, flame_m)
        f.rotation_euler = (0, math.radians(18), a); f.visible_shadow = False; flames.append(f)
    flames_g = _group('Flames', flames, (0, 0, 0)); flames_g.location = (0, 0, 1.21); flames_g.scale = (0.001,) * 3
    ld = bpy.data.lights.new('BurnerLight', 'POINT'); ld.color = hexrgb('#4aa0ff'); ld.energy = 0.0; ld.shadow_soft_size = 0.2
    lamp = bpy.data.objects.new('BurnerLight', ld); bpy.context.collection.objects.link(lamp); lamp.location = (0, -0.3, 1.25)
    pz = POT_Z
    potp = [_tube((0, 0, pz + POT_H / 2), POT_R, POT_H, steel, 0.022), cyl((0, 0, pz + 0.0125), POT_R, 0.025, steel, verts=64),
            _torus((0, 0, pz + POT_H), POT_R - 0.011, 0.016, steel)]
    for sx in (-1, 1):
        potp += [box((sx * (POT_R + 0.06), 0, pz + POT_H - 0.07), (0.12, 0.2, 0.04), black, bevel=0.015),
                 box((sx * (POT_R + 0.01), 0, pz + POT_H - 0.07), (0.04, 0.08, 0.06), steel, bevel=0.01)]
    water = M('#5ec2ff', 0.12, emit=hexrgb('#5ec2ff'), emit_strength=0.12)
    pot_water = cyl((0, 0, (pz + 0.025 + POT_WATER) / 2), POT_R - 0.024, POT_WATER - pz - 0.025, water, verts=64)
    potp.append(pot_water)
    pot_g = _group('PotBody', potp, (0, 0, pz + POT_H / 2))      # pivots on the pot's middle, so 'pour' can lift and tip it
    pot_g.rotation_mode = 'AXIS_ANGLE'
    parts += [ring, pot_g]
    rnd = random.Random(5); bub_m = M('#e6f7ff', 0.15); bubbles = []
    for k in range(18):
        b = _sphere((0, 0, POT_WATER), 1.0, bub_m, segs=12); b.scale = (0.001,) * 3; b.visible_shadow = False; bubbles.append(b)
    steam_m = _cloud('IceSteam', '#ffffff', soft=2.4, emit=0.6, blended=True); steam = []
    for k in range(10):
        s = _sphere((0, 0, pz + POT_H), 0.13, steam_m, segs=16); s.scale = (0.001,) * 3; s.visible_shadow = False; steam.append(s)
    P = {'focus_z': 1.55, 'size': 0.62, 'view_up': 0.32, 'glow': glow, 'flames': flames_g, 'lamp': ld, 'bubbles': bubbles, 'steam': steam,
         'pot': pot_g, 'pot_water': pot_water, 'actions': {}}

    def pour(P, t, o):
        """'into @cooler; for S' (default 0.8): the pot lifts off the burner, slides over the cooler's near wall, tips 110 degrees
        toward it and a stream of water falls into it; then it goes back on the burner (0.3 s). Give the cooler its 'fill' row."""
        from mathutils import Matrix
        S = max(0.6, _num(o, 'for', 0.8)); into = o.get('into')
        T = _from_table('props').get(str(into[0]).lower()) if isinstance(into, list) and into else None
        if T is None:
            return
        Lp, Lc = Vector(P['loc']), Vector(T['loc'])
        v = Matrix.Rotation(-math.radians(P['turn']), 3, 'Z') @ (Lc - Lp)
        d = Vector((v.x, v.y, 0.0)); dist = d.length; d.normalize()
        c0 = Vector((0, 0, pz + POT_H / 2))
        c1 = d * max(0.0, dist - 0.5) + Vector((0, 0, Lc.z + CZ0 + CH + 0.72 - Lp.z))   # the tipped mouth's low lip about 0.3 above the rim
        k = Vector((-d.y, d.x, 0.0)); ang = math.radians(110)
        g = P['pot']; te = t + S
        _keys(g, 'location', [(t, tuple(c0)), (t + 0.3, tuple(c1)), (te, tuple(c1)), (te + 0.3, tuple(c0))])
        _keys(g, 'rotation_axis_angle', [(t + 0.25, (0.0, *k)), (t + 0.45, (ang, *k)), (te - 0.12, (ang, *k)), (te + 0.1, (0.0, *k))])
        _keys(P['pot_water'], 'scale', [(t + 0.38, (1, 1, 1)), (t + 0.5, (1, 1, 0.001)), (te + 0.3, (1, 1, 0.001)), (te + 0.32, (1, 1, 1))], 'LINEAR')
        lip = c1 + Matrix.Rotation(ang, 3, k) @ (d * POT_R + Vector((0, 0, POT_H / 2)))
        z_end = Lc.z + CZ0 + CT + 0.04 - Lp.z; L = max(0.2, lip.z - z_end)
        sm = M('#7fd3ff', 0.1, emit=hexrgb('#5ec2ff'), emit_strength=0.35)       # solid, so the stream reads at phone size
        col = cyl((0, 0, -L / 2), 0.055, L, sm, verts=24); col.visible_shadow = False
        st = _group(P['name'] + '_stream', [col], (0, 0, 0)); st.parent = P['root']
        st.location = (lip.x + d.x * 0.03, lip.y + d.y * 0.03, lip.z - 0.02); st.scale = (1, 1, 0.001)
        _keys(st, 'scale', [(t + 0.42, (1, 1, 0.001)), (t + 0.56, (1, 1, 1)), (te - 0.14, (1, 1, 1)), (te - 0.04, (0.001, 0.001, 0.001))], 'LINEAR')
        visible([st], [(0, False), (t + 0.42, True), (te, False)])
    P['actions']['pour'] = pour

    def boil(P, t, o):
        te = _num(o, 'until', P.get('t_end', t + 6.0) + 0.5)
        gs = P['glow'].node_tree.nodes['Principled BSDF'].inputs['Emission Strength']
        _socket_keys(gs, [(t, 0.0), (t + 0.25, 5.0), (te, 5.0), (te + 0.3, 0.0)])
        for tt, e in ((t, 0.0), (t + 0.25, 60.0), (te, 60.0), (te + 0.3, 0.0)):    # the blue glow lights the pot's base
            P['lamp'].energy = e; P['lamp'].keyframe_insert('energy', frame=F(tt))
        fl = [(t - 0.01, (0.001,) * 3), (t + 0.2, (1, 1, 1))]
        tt = t + 0.3
        while tt < te:                                                    # the flames flicker
            fl.append((tt, (1, 1, 0.8 + 0.4 * rnd.random()))); tt += 0.09
        fl += [(te, (1, 1, 1)), (te + 0.25, (0.001,) * 3)]
        _keys(P['flames'], 'scale', fl, 'LINEAR')
        for k, b in enumerate(P['bubbles']):                              # bubbles swell on the surface and pop
            sc, lc = [(t, (0.001,) * 3)], []; tt = t + 0.35 + rnd.uniform(0, 0.5)
            while tt < te:
                a, r = rnd.uniform(0, 2 * math.pi), (POT_R - 0.07) * math.sqrt(rnd.random()); big = rnd.uniform(0.026, 0.045)
                lc += [(tt - 0.02, (r * math.cos(a), r * math.sin(a), POT_WATER))]
                sc += [(tt - 0.01, (0.001,) * 3), (tt + rnd.uniform(0.12, 0.22), (big,) * 3), ]
                tp = sc[-1][0] + 0.04; sc.append((tp, (0.001,) * 3)); tt = tp + rnd.uniform(0.05, 0.3)
            if lc:
                _keys(b, 'location', lc, 'CONSTANT'); _keys(b, 'scale', sc, 'LINEAR')
        for k, s in enumerate(P['steam']):                               # steam puffs rise, swell and fade
            loc, sc = [], [(t, (0.001,) * 3)]; tt = t + 0.4 + 0.17 * k; life = 1.7
            while tt < te + 0.2:
                x, y = rnd.uniform(-0.18, 0.18), rnd.uniform(-0.12, 0.12)
                loc += [(tt, (x, y, POT_Z + POT_H - 0.05)), (tt + life, (x * 1.8 + rnd.uniform(-0.1, 0.1), y - 0.08, POT_Z + POT_H + 0.95))]
                sc += [(tt - 0.01, (0.001,) * 3), (tt + 0.25, (0.55,) * 3), (tt + 0.7 * life, (1.25,) * 3), (tt + life, (0.001,) * 3)]
                tt += life + 0.07                                         # it starts again from the pot, unseen
            if loc:
                _keys(s, 'location', loc, 'LINEAR'); _keys(s, 'scale', sc)
    P['actions']['boil'] = boil
    return P, parts + [flames_g, lamp] + bubbles + steam


BUILDERS = dict(cube=cube, tray=tray, cup=cup, block=block, cooler=cooler, pot=pot)
