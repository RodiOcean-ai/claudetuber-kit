"""Blocky world kit (look approved 5 Nov 2026, <projects>/short-factory-lookdev/blocky_hero v2): adult blocky figures on hinges with a can-shaped head.
- build(recipe, loc): a character from a cast.json recipe (colours, scale, accessories). Returns R, a dict of pivots for posing.
- The face is three sticker layers (brows, eyes, mouths) from the face bank atlases (faces_bank.py). The head carries three
  numbers (face_brow, face_eye, face_mouth) that pick a cell per layer; they can be keyframed, so faces change, blink and talk.
- set_face(R, 'angry') for a still; face_track(R, cues, words) keys a whole performance (expressions, auto blinks, lip flaps).
- pose(R, ...) hinges: shoulders (forward, sideways), hips, neck, turn, lean, lift.
Use: sys.path has templates/blender and templates/blender/blocky;  from blocky_kit import *"""
import json, math, os, random
import bpy, bmesh
from common import FPS, mat, hexrgb
from sf_world import box, cyl, empty, parent, text

KIT = os.path.dirname(os.path.abspath(__file__))
ASSETS = os.path.normpath(os.path.join(KIT, '..', '..', '..', 'assets', 'blocky'))
FB = json.load(open(os.path.join(ASSETS, 'faces.json'), encoding='utf-8'))
CAST = json.load(open(os.path.join(KIT, 'cast.json'), encoding='utf-8'))
HEAD_R, HEAD_H, FACE_W = 0.37, 0.7, 1.0           # can-shaped head; FACE_W = width one face cell covers on the head
HEAD_Z = 2.0 + HEAD_H / 2 + 0.02                   # head centre above the feet (scale 1)
EYE = (0.161, 0.07)                                # eye centre on the head: x from the middle, z above the head centre
_MATS, _IMGS = {}, {}


def M(hx, rough=0.6, **k):
    key = (hx, rough, tuple(sorted(k.items())))
    if key not in _MATS:
        _MATS[key] = mat(f'C_{hx}_{rough}', hexrgb(hx), rough=rough, **k)
    return _MATS[key]


def atlas(layer):
    if layer not in _IMGS:
        _IMGS[layer] = bpy.data.images.load(os.path.join(ASSETS, layer + '.png'))
    return _IMGS[layer]


# ---------------------------------------------------------------- the head shader: skin + three atlas layers
def head_material(skin, eye=None, layers=('brows', 'eyes', 'mouths')):
    """eye: an optional eye colour; the dark ink of the eye stickers takes it (the white shine stays white).
    layers: which sticker layers to draw (a bird has a beak, so no mouth)."""
    key = ('head', skin, eye, tuple(layers))
    if key in _MATS:
        return _MATS[key]
    m = mat('Head_' + skin + ('_' + eye if eye else ''), hexrgb(skin), rough=0.5); nt = m.node_tree; b = nt.nodes['Principled BSDF']; L = nt.links

    def op(kind, a, c):
        n = nt.nodes.new('ShaderNodeMath'); n.operation = kind
        for i, v in enumerate((a, c)):
            if isinstance(v, (int, float)):
                n.inputs[i].default_value = v
            else:
                L.new(v, n.inputs[i])
        return n.outputs[0]
    tc = nt.nodes.new('ShaderNodeTexCoord'); sep = nt.nodes.new('ShaderNodeSeparateXYZ'); L.new(tc.outputs['Object'], sep.inputs[0])
    u = op('ADD', op('DIVIDE', sep.outputs['X'], FACE_W), 0.5); v = op('ADD', op('DIVIDE', sep.outputs['Z'], FACE_W), 0.5)
    inside = op('MULTIPLY', op('MULTIPLY', op('GREATER_THAN', u, 0.0), op('LESS_THAN', u, 1.0)),
                op('MULTIPLY', op('MULTIPLY', op('GREATER_THAN', v, 0.0), op('LESS_THAN', v, 1.0)), op('LESS_THAN', sep.outputs['Y'], 0.0)))
    n = FB['grid']; color = b.inputs['Base Color'].default_value[:]
    prev = None
    for layer in layers:
        at = nt.nodes.new('ShaderNodeAttribute'); at.attribute_type = 'OBJECT'; at.attribute_name = 'face_' + layer
        idx = op('ROUND', at.outputs['Fac'], 0.0)              # a cell number, never a blend of two cells
        col = op('MODULO', idx, n); row = op('FLOOR', op('DIVIDE', idx, n), 0.0)
        cu = op('DIVIDE', op('ADD', u, col), n); cv = op('DIVIDE', op('ADD', v, op('SUBTRACT', n - 1, row)), n)
        uv = nt.nodes.new('ShaderNodeCombineXYZ'); L.new(cu, uv.inputs['X']); L.new(cv, uv.inputs['Y'])
        tex = nt.nodes.new('ShaderNodeTexImage'); tex.image = atlas(layer); tex.extension = 'CLIP'; L.new(uv.outputs[0], tex.inputs[0])
        ink = tex.outputs['Color']
        if eye and layer == 'eyes':                            # dark pixels -> the eye colour, light ones (the shine) stay
            bw = nt.nodes.new('ShaderNodeRGBToBW'); L.new(ink, bw.inputs[0])
            tint = nt.nodes.new('ShaderNodeMix'); tint.data_type = 'RGBA'; tint.inputs['B'].default_value = (*hexrgb(eye), 1)
            L.new(ink, tint.inputs['A']); L.new(op('LESS_THAN', bw.outputs[0], 0.35), tint.inputs['Factor']); ink = tint.outputs['Result']
        mix = nt.nodes.new('ShaderNodeMix'); mix.data_type = 'RGBA'
        if prev is None:
            mix.inputs['A'].default_value = color
        else:
            L.new(prev, mix.inputs['A'])
        L.new(op('MULTIPLY', tex.outputs['Alpha'], inside), mix.inputs['Factor']); L.new(ink, mix.inputs['B'])
        prev = mix.outputs['Result']
    L.new(prev, b.inputs['Base Color'])
    _MATS[key] = m
    return m


# ---------------------------------------------------------------- accessories: f(hc, opt) -> objects; hc = head centre
def _ring_top(major, minor, loc, m):
    bpy.ops.mesh.primitive_torus_add(major_radius=major, minor_radius=minor, location=loc, rotation=(math.radians(90), 0, 0),
                                     major_segments=64, minor_segments=16)
    o = bpy.context.object; o.data.materials.append(m); bpy.ops.object.shade_smooth()
    bm = bmesh.new(); bm.from_mesh(o.data)
    bmesh.ops.delete(bm, geom=[v for v in bm.verts if v.co.y < -0.02], context='VERTS'); bm.to_mesh(o.data); bm.free()
    return o


def headphones(hc, color='#ff7a1a'):
    x, y, z = hc; org, pad = M(color, 0.3, coat=0.6), M('#20222c', 0.8)
    parts = [_ring_top(0.47, 0.05, (x, y + 0.03, z + 0.04), org)]
    for sx in (-1, 1):
        parts += [cyl((x + sx * 0.44, y + 0.03, z - 0.02), 0.18, 0.13, org, rot=(0, 90, 0)),
                  cyl((x + sx * 0.374, y + 0.03, z - 0.02), 0.145, 0.03, pad, rot=(0, 90, 0))]
    return parts


def _round_cap(loc, r, h, m, bevel=0.06):
    o = cyl(loc, r, h, m, verts=64)
    bv = o.modifiers.new('bev', 'BEVEL'); bv.width = bevel; bv.segments = 5; bv.limit_method = 'ANGLE'; bv.angle_limit = math.radians(40)
    return o


def bucket_hat(hc, color='#ffd23a'):
    x, y, z = hc; m = M(color)
    return [cyl((x, y, z + HEAD_H / 2 + 0.02), 0.56, 0.04, m), _round_cap((x, y, z + HEAD_H / 2 + 0.13), 0.39, 0.22, m)]


def cap(hc, color='#e63946', backwards=False):
    x, y, z = hc; m = M(color, 0.5); s = 1 if backwards else -1
    return [_round_cap((x, y, z + HEAD_H / 2 + 0.03), 0.39, 0.16, m), box((x, y + s * 0.5, z + HEAD_H / 2 - 0.02), (0.5, 0.34, 0.035), m, bevel=0.015),
            cyl((x, y, z + HEAD_H / 2 + 0.12), 0.05, 0.03, m)]


def chef_hat(hc, color='#fbfbf8'):
    """A tall chef's toque: a straight band on the head and a puffed top that leans out wider than the band."""
    x, y, z = hc; m = M(color, 0.85); top = z + HEAD_H / 2
    return [cyl((x, y, top + 0.1), 0.385, 0.2, m, verts=64), _round_cap((x, y, top + 0.5), 0.46, 0.62, m, bevel=0.22)]


def flat_cap(hc, color='#4a4552'):
    x, y, z = hc; m = M(color, 0.8)
    crown = _round_cap((x, y + 0.02, z + HEAD_H / 2 + 0.03), 0.41, 0.11, m, bevel=0.05); crown.rotation_euler = (math.radians(-7), 0, 0)
    return [crown, box((x, y - 0.42, z + HEAD_H / 2 - 0.0), (0.56, 0.2, 0.035), m, rot=(-12, 0, 0), bevel=0.015)]


def hair(hc, color='#3b2416', bun=False):
    """Top disc plus a shell over the back and sides of the head (front left open for the face)."""
    x, y, z = hc; m = M(color, 0.75)
    parts = [_round_cap((x, y + 0.01, z + HEAD_H / 2 - 0.02), 0.395, 0.14, m, bevel=0.06)]
    bpy.ops.mesh.primitive_cylinder_add(radius=0.39, depth=0.5, location=(x, y + 0.01, z + 0.1), vertices=64, end_fill_type='NOTHING')
    sh = bpy.context.object; sh.data.materials.append(m); bpy.ops.object.shade_smooth()
    bm = bmesh.new(); bm.from_mesh(sh.data)
    bmesh.ops.delete(bm, geom=[v for v in bm.verts if v.co.y < -0.16], context='VERTS'); bm.to_mesh(sh.data); bm.free()
    so = sh.modifiers.new('thick', 'SOLIDIFY'); so.thickness = 0.03
    parts.append(sh)
    if bun:
        parts.append(_sphere((x, y + 0.12, z + HEAD_H / 2 + 0.16), 0.17, m))
    return parts


def _sphere(loc, r, m):
    bpy.ops.mesh.primitive_uv_sphere_add(radius=r, location=loc, segments=48, ring_count=24); o = bpy.context.object
    o.data.materials.append(m); bpy.ops.object.shade_smooth()
    return o


def glasses(hc, color='#20222c', shape='round'):
    x, y, z = hc; m = M(color, 0.3); ex, ez = EYE; fy = y - HEAD_R - 0.01
    parts = [box((x, fy + 0.005, z + ez + 0.02), (0.1, 0.025, 0.025), m, bevel=0.008)]
    for sx in (-1, 1):
        cx = x + sx * ex
        if shape == 'round':
            bpy.ops.mesh.primitive_torus_add(major_radius=0.115, minor_radius=0.017, location=(cx, fy + abs(sx) * 0.0, z + ez),
                                             rotation=(math.radians(90), 0, 0), major_segments=48, minor_segments=10)
            o = bpy.context.object; o.data.materials.append(m); bpy.ops.object.shade_smooth(); parts.append(o)
        else:
            for dz, w, h in ((0.1, 0.26, 0.03), (-0.1, 0.26, 0.03)):
                parts.append(box((cx, fy, z + ez + dz), (w, 0.03, h), m, bevel=0.008))
            for dx in (-0.13, 0.13):
                parts.append(box((cx + dx, fy, z + ez), (0.03, 0.03, 0.23), m, bevel=0.008))
        parts.append(box((x + sx * (HEAD_R + 0.005), y - 0.12, z + ez + 0.02), (0.02, 0.36, 0.025), m, bevel=0.005))
    return _no_shadow(parts)


def _no_shadow(parts):
    """Frames sit just in front of the face sticker: their shadows would draw dark stripes over the eyes."""
    for o in parts:
        o.visible_shadow = False
    return parts


def shades(hc, color='#0d0d10'):
    x, y, z = hc; m = M(color, 0.15, coat=1.0); ex, ez = EYE; fy = y - HEAD_R + 0.01
    parts = [box((x, fy - 0.02, z + ez + 0.04), (0.6, 0.04, 0.05), m, bevel=0.01)]
    for sx in (-1, 1):
        parts.append(box((x + sx * ex, fy - 0.025, z + ez - 0.01), (0.25, 0.04, 0.16), m, bevel=0.03))
        parts.append(box((x + sx * (HEAD_R + 0.005), y - 0.12, z + ez + 0.04), (0.02, 0.36, 0.03), m, bevel=0.005))
    return _no_shadow(parts)


def tie(tc, color='#c8303a'):
    x, y, z = tc; m = M(color, 0.5)
    return [box((x, y - 0.262, z + 0.88), (0.15, 0.03, 0.1), m, bevel=0.01), box((x, y - 0.262, z + 0.55), (0.13, 0.025, 0.58), m, bevel=0.01)]


def sash(tc, color='#f2c230'):
    x, y, z = tc; m = M(color, 0.35, metal=0.3)
    return [box((x, y - 0.262, z + 0.5), (1.18, 0.03, 0.15), m, rot=(0, 38, 0), bevel=0.01)]


def backpack(tc, color='#ff8a3d'):
    x, y, z = tc; m = M(color, 0.6); st = M('#3a3a46', 0.7)
    parts = [box((x, y + 0.42, z + 0.48), (0.72, 0.32, 0.78), m, bevel=0.06), box((x, y + 0.6, z + 0.36), (0.5, 0.06, 0.32), m, bevel=0.04)]
    for sx in (-1, 1):
        parts.append(box((x + sx * 0.28, y - 0.258, z + 0.62), (0.1, 0.025, 0.66), st, bevel=0.008))
    return parts


def mustache(hc, color='#e9e9ec'):
    """A bushy block just above the mouth sticker (the mouth still shows and talks below it)."""
    x, y, z = hc; m = M(color, 0.85)
    return [box((x, y - HEAD_R - 0.015, z - 0.085), (0.36, 0.07, 0.075), m, bevel=0.03)]


def peaked_cap(hc, color='#1f2a44', band='#15151b', badge='#f2c230'):
    """A guard's or officer's cap: band, wide flat crown, shiny visor and a gold badge."""
    x, y, z = hc; top = z + HEAD_H / 2
    return [cyl((x, y, top + 0.04), 0.39, 0.1, M(band, 0.4)), _round_cap((x, y + 0.03, top + 0.15), 0.45, 0.13, M(color, 0.5), bevel=0.05),
            box((x, y - 0.43, top + 0.01), (0.5, 0.22, 0.03), M(band, 0.15, coat=1.0), rot=(-10, 0, 0), bevel=0.012),
            box((x, y - 0.405, top + 0.14), (0.12, 0.03, 0.1), M(badge, 0.3, metal=0.7), bevel=0.012)]


def souwester(hc, color='#ffd23a'):
    """A rain hat (sou'wester): round crown and a brim that slopes down at the back."""
    x, y, z = hc; m = M(color, 0.3, coat=0.6); top = z + HEAD_H / 2
    return [cyl((x, y + 0.1, top - 0.0), 0.6, 0.04, m, rot=(-12, 0, 0)), _round_cap((x, y, top + 0.12), 0.41, 0.26, m, bevel=0.1)]


def beanie(hc, color='#7b4dd6'):
    x, y, z = hc; m = M(color, 0.9); top = z + HEAD_H / 2
    return [cyl((x, y, top - 0.02), 0.395, 0.14, m), _round_cap((x, y, top + 0.1), 0.38, 0.24, m, bevel=0.11),
            _sphere((x, y, top + 0.27), 0.08, m)]


def apron(tc, color='#fbfbf8'):
    """A chef's apron: a bib on the chest and a skirt down the front of the legs."""
    x, y, z = tc; m = M(color, 0.85)
    return [box((x, y - 0.262, z + 0.62), (0.56, 0.02, 0.5), m, bevel=0.01), box((x, y - 0.27, z + 0.12), (0.92, 0.025, 0.7), m, bevel=0.01),
            box((x, y - 0.258, z + 0.36), (1.02, 0.02, 0.06), m, bevel=0.005)]


def coat(tc, color='#f7f7f4', lapel='#d8dce4'):
    """An open long coat (a scientist's lab coat): front panels with a gap in the middle, down to the thighs."""
    x, y, z = tc; m = M(color, 0.8); parts = []
    for sx in (-1, 1):
        parts += [box((x + sx * 0.3, y - 0.27, z + 0.3), (0.42, 0.03, 1.32), m, bevel=0.01),
                  box((x + sx * 0.16, y - 0.29, z + 0.82), (0.12, 0.02, 0.3), M(lapel, 0.7), rot=(0, -sx * 18, 0), bevel=0.005)]
    parts.append(box((x, y + 0.27, z + 0.3), (1.02, 0.03, 1.32), m, bevel=0.01))
    return parts


def vest(tc, color='#c6f21a', stripe='#d9dde6'):
    """A hi-vis safety vest with a reflective stripe (guards, crew)."""
    x, y, z = tc
    return [box((x, y, z + 0.6), (1.03, 0.53, 0.78), M(color, 0.6), bevel=0.04),
            box((x, y, z + 0.42), (1.04, 0.54, 0.07), M(stripe, 0.2, metal=0.8), bevel=0.01)]


HEAD_ACC = {'headphones': headphones, 'bucket_hat': bucket_hat, 'cap': cap, 'chef_hat': chef_hat, 'flat_cap': flat_cap, 'hair': hair, 'glasses': glasses, 'shades': shades,
            'mustache': mustache, 'peaked_cap': peaked_cap, 'souwester': souwester, 'beanie': beanie}
BODY_ACC = {'tie': tie, 'sash': sash, 'backpack': backpack, 'apron': apron, 'coat': coat, 'vest': vest}


# ---------------------------------------------------------------- the character
def _pivot(name, loc, parent_to):
    p = empty(name, loc); parent([p], parent_to)
    return p


def build(recipe, loc=(0, 0, 0)):
    """recipe (cast.json): name, skin, top, bottom, shoe, optional pocket, sleeve, eye (colour), scale, accessories [[name, {options}], ...]."""
    if isinstance(recipe, str):
        recipe = CAST[recipe]
    if recipe.get('kind') in ('quad', 'bird'):                  # animals: same head and face, another body (animals.py)
        from animals import build_animal
        return build_animal(recipe, loc)
    name = recipe['name']; x0, y0, z0 = loc
    P = lambda x, y, z: (x0 + x, y0 + y, z0 + z)
    root = empty(name, loc); R = {'root': root, 'name': name, 'base': tuple(loc), 'head_z': HEAD_Z}
    top, bottom, shoe, skin = M(recipe['top'], 0.7), M(recipe['bottom'], 0.7), M(recipe['shoe'], 0.5), M(recipe['skin'], 0.5)
    R['feet'] = []
    for sx, side in ((-1, 'L'), (1, 'R')):                       # legs as long as the torso, side by side
        hip = _pivot(f'{name}_hip{side}', P(sx * 0.25, 0, 1.0), root)
        foot = box(P(sx * 0.25, -0.02, 0.08), (0.5, 0.54, 0.16), shoe, bevel=0.035)
        parent([box(P(sx * 0.25, 0, 0.58), (0.49, 0.5, 0.84), bottom, bevel=0.035), foot], hip)
        R['hip' + side] = hip; R['feet'].append(foot)
    torso = _pivot(name + '_torso', P(0, 0, 1.0), root); R['torso'] = torso
    tparts = [box(P(0, 0, 1.5), (1.0, 0.5, 1.0), top, bevel=0.04)]
    if recipe.get('pocket'):
        tparts.append(box(P(0, -0.255, 1.25), (0.56, 0.02, 0.24), M(recipe['pocket'], 0.7), bevel=0.01))
    for sx, side in ((-1, 'L'), (1, 'R')):                       # arms: sleeve plus a skin hand block, down to the hips
        sh = _pivot(f'{name}_sh{side}', P(sx * 0.745, 0, 1.92), torso)
        parent([box(P(sx * 0.745, 0, 1.63), (0.48, 0.48, 0.74), M(recipe.get('sleeve', recipe['top']), 0.7), bevel=0.035),
                box(P(sx * 0.745, 0, 1.13), (0.48, 0.48, 0.26), skin, bevel=0.035)], sh)
        R['sh' + side] = sh
    neck = _pivot(name + '_neck', P(0, 0, 2.0), torso); R['neck'] = neck
    hc = P(0, 0, HEAD_Z)
    head = cyl(hc, HEAD_R, HEAD_H, head_material(recipe['skin'], recipe.get('eye')), verts=64); head.name = name + '_head'
    bv = head.modifiers.new('bev', 'BEVEL'); bv.width = 0.13; bv.segments = 8; bv.limit_method = 'ANGLE'; bv.angle_limit = math.radians(40)
    R['head'] = head; hparts = [head]
    for acc in recipe.get('accessories', []):
        an, opt = (acc, {}) if isinstance(acc, str) else (acc[0], acc[1] if len(acc) > 1 else {})
        if an in HEAD_ACC:
            hparts += HEAD_ACC[an](hc, **opt)
        else:
            tparts += BODY_ACC[an](P(0, 0, 1.0), **opt)
    parent(tparts, torso); parent(hparts, neck)
    s = recipe.get('scale', 1.0); root.scale = (s, s, s); R['scale'] = s
    set_face(R, 'calm')
    return R


def hero(overrides=None, loc=(0, 0, 0)):
    """The episode's hero: the cast's starting recipe restyled for the channel being reviewed. overrides replaces any field;
    its accessories list replaces the default headphones (e.g. [["cap", {"color": "#ff0033"}]]). Owner rule, 5 Nov 2026."""
    return build({**CAST['hero'], **(overrides or {})}, loc)


# ---------------------------------------------------------------- the mystery hero (owner, 5 Nov 2026)
# Until the reveal, the hero is a 'mystery figure': one inky shadow material over everything (body, hands, head, accessories,
# so only the outline gives anything away) with a violet glow around the edges, and a big glowing '?' for a face. It must read
# as a hidden shadow, never as a skin colour: the hands and head are the same ink as the clothes, and there is no face at all.
SHADOW, MARK, RIM = '#16121f', '#ffd23a', '#8a63ff'


def shadow_material():
    if 'shadow' in _MATS:
        return _MATS['shadow']
    m = mat('Mystery_shadow', hexrgb(SHADOW), rough=0.35); nt = m.node_tree; b = nt.nodes['Principled BSDF']
    lw = nt.nodes.new('ShaderNodeLayerWeight'); lw.inputs['Blend'].default_value = 0.35       # edges glow, the middle stays ink
    pw = nt.nodes.new('ShaderNodeMath'); pw.operation = 'POWER'; pw.inputs[1].default_value = 2.5
    k = nt.nodes.new('ShaderNodeMath'); k.operation = 'MULTIPLY'; k.inputs[1].default_value = 4.0
    nt.links.new(lw.outputs['Facing'], pw.inputs[0]); nt.links.new(pw.outputs[0], k.inputs[0]); nt.links.new(k.outputs[0], b.inputs['Emission Strength'])
    b.inputs['Emission Color'].default_value = (*hexrgb(RIM), 1)
    _MATS['shadow'] = m
    return m


def mystery(R):
    """Turn a built character into the mystery figure: every part in shadow, a glowing '?' on the face."""
    sm = shadow_material()
    for o in R['root'].children_recursive:
        if o.type == 'MESH':
            o.data = o.data.copy()                   # meshes may be shared; never repaint the real hero
            o.data.materials.clear(); o.data.materials.append(sm)
    s = R.get('scale', 1.0); bx, by, bz = R['base']
    hc = (bx, by - (HEAD_R + 0.025) * s, bz + (HEAD_Z - 0.03) * s)
    q = text('?', hc, 0.62 * s, M(MARK, 0.4, emit=hexrgb(MARK), emit_strength=3.0), extrude=0.035)
    q.data.bevel_depth = 0.012; parent([q], R['neck']); R['mark'] = q
    return R


# ---------------------------------------------------------------- faces
def face_cells(expr, mouth=None, eyes=None):
    b, e, m = FB['expressions'][expr]
    return FB['brows'][b], FB['eyes'][eyes or e], FB['mouths'][mouth or m]


def set_face(R, expr, mouth=None, eyes=None):
    for layer, v in zip(('brows', 'eyes', 'mouths'), face_cells(expr, mouth, eyes)):
        R['head']['face_' + layer] = float(v)


def _talk_shape(word, k):
    """Mouth for chunk k of a word: vowels open the mouth (a wide, e/i half, o/u round), every other chunk closes a bit."""
    vow = [c for c in word.lower() if c in 'aeiouy']
    if k % 2:
        return 'talk_closed' if any(c in word.lower() for c in 'mbp') else 'talk_half'
    c = vow[(k // 2) % len(vow)] if vow else 'e'
    return {'a': 'talk_wide', 'o': 'talk_o', 'u': 'talk_o'}.get(c, 'talk_half')


def face_track(R, cues, words=(), t_end=None, seed=1, blink_every=(2.0, 4.0)):
    """cues: [(time, expression)]; words: [{'w', 's', 'e'}] this character says (lip flaps). Auto blinks. Keys only changes."""
    cues = sorted(cues); t_end = t_end or max([c[0] for c in cues] + [w['e'] for w in words]) + 1.0
    rnd = random.Random(seed); blinks, t = [], rnd.uniform(*blink_every) * 0.5
    while t < t_end:
        blinks.append(t); t += rnd.uniform(*blink_every)
    shut = {'happy', 'laugh', 'closed'}
    prefs = bpy.context.preferences.edit; old = prefs.keyframe_new_interpolation_type; prefs.keyframe_new_interpolation_type = 'CONSTANT'
    head, last = R['head'], None
    for f in range(1, round(t_end * FPS) + 2):
        t = (f - 1) / FPS
        expr = next((e for tc, e in reversed(cues) if tc <= t), cues[0][1])
        b, e, m = FB['expressions'][expr]
        w = next((w for w in words if w['s'] <= t < w['e']), None)
        if w:
            m = _talk_shape(w['w'], int((t - w['s']) / 0.1))
        if e not in shut and any(0 <= t - bt < 0.12 for bt in blinks):
            e = 'closed'
        cells = (FB['brows'][b], FB['eyes'][e], FB['mouths'][m])
        if cells != last:
            for layer, v in zip(('brows', 'eyes', 'mouths'), cells):
                head['face_' + layer] = float(v); head.keyframe_insert(f'["face_{layer}"]', frame=f)
            last = cells
    prefs.keyframe_new_interpolation_type = old
    act = head.animation_data.action                       # faces snap from key to key (Blender 5 layered actions)
    curves = getattr(act, 'fcurves', None) or [fc for l in act.layers for s in l.strips for cb in s.channelbags for fc in cb.fcurves]
    for fc in curves:
        if fc.data_path.startswith('["face_'):
            for k in fc.keyframe_points:
                k.interpolation = 'CONSTANT'
    return blinks


# ---------------------------------------------------------------- posing
def pose(R, shL=(0, 0), shR=(0, 0), hipL=0, hipR=0, head=(0, 0), turn=0, lean=0, lift=0, at=None):
    """Angles in degrees. sh = (forward swing, sideways raise); positive forward = toward the front. at = new base position."""
    rad = math.radians
    if at is not None:
        R['base'] = tuple(at)
    R['shL'].rotation_euler = (rad(-shL[0]), rad(shL[1]), 0)
    R['shR'].rotation_euler = (rad(-shR[0]), rad(-shR[1]), 0)
    R['hipL'].rotation_euler = (rad(-hipL), 0, 0); R['hipR'].rotation_euler = (rad(-hipR), 0, 0)
    R['neck'].rotation_euler = (rad(head[0]), 0, rad(head[1]))
    R['root'].rotation_euler = (rad(lean), 0, rad(turn))
    b = R['base']; R['root'].location = (b[0], b[1], b[2] + lift)
