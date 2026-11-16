"""Blocky animals (owner, 5 Nov 2026): the same can-shaped head and face stickers as the people, on a four-legged body
(dog, cat, rabbit) or a bird body (pigeon). blocky_kit.build() hands any cast.json recipe with "kind": "quad" or "bird" here.
build_animal(recipe, loc) returns the same R dict as a person (root, torso, shL/shR, hipL/hipR, neck, head, feet), so the moves,
faces, checks and camera all work, plus:
  kind  'quad' (front legs on shL/shR, back legs on hipL/hipR) or 'bird' (wings on shL/shR, legs on hipL/hipR);
  tail  a pivot the moves wag (or None); leg, toe and contacts for the ground solve; head_z (head height) for the camera.
Recipe keys: fur (body), face (head colour, default fur), belly, paw, ear, nose, eye, ears (flop | point | long | round), tail (stub |
long | puff | bushy = a squirrel's big tail curling up over its back; tail_tip = its lighter tip), muzzle (colour: a painted patch
round the nose and mouth), nose_size (1 = the dog's), teeth (true: two front teeth), stripes, collar (colour: a collar with a
gold bell), leg (leg length), length (body), scale;
birds: wing, bar, band, beak, legs."""
import math
import bpy, bmesh
from common import hexrgb
from blocky_kit import HEAD_R, HEAD_H, M, head_material, set_face, _pivot, _sphere
from sf_world import box, cyl, empty, parent


def prism(pts, depth, loc, m, rot=(0, 0, 0), bevel=0.02):
    """A flat shape (points in x-z) with thickness along y: ears, wing tips, stars."""
    me = bpy.data.meshes.new('prism'); bm = bmesh.new(); n = len(pts)
    vs = [bm.verts.new((px, sy * depth / 2, pz)) for sy in (-1, 1) for px, pz in pts]
    bm.faces.new(vs[:n]); bm.faces.new(vs[n:])
    for i in range(n):
        j = (i + 1) % n; bm.faces.new((vs[i], vs[j], vs[n + j], vs[n + i]))
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces); bm.to_mesh(me); bm.free()
    o = bpy.data.objects.new('prism', me); bpy.context.collection.objects.link(o)
    o.location = loc; o.rotation_euler = tuple(math.radians(a) for a in rot); o.data.materials.append(m)
    if bevel:
        bv = o.modifiers.new('bev', 'BEVEL'); bv.width = bevel; bv.segments = 2
    return o


_MUZZLES = {}


def _muzzle_material(skin, eye, layers, muzzle):
    """The head material with a painted oval patch (a lighter muzzle) under the eyes; the face stickers draw on top of it."""
    key = (skin, eye, tuple(layers), muzzle)
    if key in _MUZZLES:
        return _MUZZLES[key]
    m = head_material(skin, eye, layers).copy(); m.name = 'Head_' + skin + '_muzzle'; nt = m.node_tree; L = nt.links
    first = next(n for n in nt.nodes if n.bl_idname == 'ShaderNodeMix' and n.data_type == 'RGBA' and not n.inputs['A'].is_linked
                 and n.inputs['B'].is_linked)                    # the first sticker layer: it mixes over the plain head colour

    def op(kind, a, c):
        n = nt.nodes.new('ShaderNodeMath'); n.operation = kind
        for i, v in enumerate((a, c)):
            if isinstance(v, (int, float)):
                n.inputs[i].default_value = v
            else:
                L.new(v, n.inputs[i])
        return n.outputs[0]
    tc = nt.nodes.new('ShaderNodeTexCoord'); sep = nt.nodes.new('ShaderNodeSeparateXYZ'); L.new(tc.outputs['Object'], sep.inputs[0])
    dx = op('DIVIDE', sep.outputs['X'], 0.24); dz = op('DIVIDE', op('ADD', sep.outputs['Z'], 0.155), 0.17)    # an oval round the nose and mouth
    inside = op('MULTIPLY', op('LESS_THAN', op('ADD', op('MULTIPLY', dx, dx), op('MULTIPLY', dz, dz)), 1.0), op('LESS_THAN', sep.outputs['Y'], 0.0))
    mix = nt.nodes.new('ShaderNodeMix'); mix.data_type = 'RGBA'
    mix.inputs['A'].default_value = first.inputs['A'].default_value[:]; mix.inputs['B'].default_value = (*hexrgb(muzzle), 1)
    L.new(inside, mix.inputs['Factor']); L.new(mix.outputs['Result'], first.inputs['A'])
    _MUZZLES[key] = m
    return m


def _head(R, recipe, hc, layers=('brows', 'eyes', 'mouths')):
    name = recipe['name']; skin = recipe.get('face', recipe['fur'])
    hm = _muzzle_material(skin, recipe.get('eye'), layers, recipe['muzzle']) if recipe.get('muzzle') else head_material(skin, recipe.get('eye'), layers)
    head = cyl(hc, HEAD_R, HEAD_H, hm, verts=64)
    head.name = name + '_head'
    bv = head.modifiers.new('bev', 'BEVEL'); bv.width = 0.13; bv.segments = 8; bv.limit_method = 'ANGLE'; bv.angle_limit = math.radians(40)
    R['head'] = head
    return head


def _ears(kind, hc, recipe):
    x, y, z = hc; fur = M(recipe.get('ear', recipe.get('face', recipe['fur'])), 0.8); pink = M('#f4a3b4', 0.7); top = z + HEAD_H / 2
    parts = []
    for sx in (-1, 1):
        if kind == 'flop':                                         # dog: soft flaps hanging down the sides of the head
            parts.append(box((x + sx * (HEAD_R + 0.05), y + 0.02, z + 0.04), (0.11, 0.34, 0.5), fur, rot=(0, sx * 10, 0), bevel=0.04))
        elif kind == 'point':                                      # cat: triangles on top, pink inside
            parts += [prism([(-0.17, 0), (0.17, 0), (0.02 * sx, 0.32)], 0.08, (x + sx * 0.2, y + 0.02, top - 0.06), fur, rot=(0, -sx * 12, 0)),
                      prism([(-0.09, 0), (0.09, 0), (0.015 * sx, 0.19)], 0.03, (x + sx * 0.2, y - 0.03, top - 0.03), pink, rot=(0, -sx * 12, 0), bevel=0.01)]
        elif kind == 'long':                                       # rabbit: tall rounded ears, pink inside
            parts += [box((x + sx * 0.15, y + 0.02, top + 0.3), (0.17, 0.09, 0.66), fur, rot=(0, -sx * 8, 0), bevel=0.07),
                      box((x + sx * 0.15 - sx * 0.005, y - 0.03, top + 0.3), (0.09, 0.02, 0.5), pink, rot=(0, -sx * 8, 0), bevel=0.02)]
        elif kind == 'round':                                      # squirrel: small round ears on top, pink inside
            for r, d, yy, m in ((0.1, 0.09, 0.04, fur), (0.055, 0.02, -0.01, pink)):       # (a little taller than wide, standing up)
                e = cyl((x + sx * 0.19, y + yy, top + 0.08), r, d, m, rot=(90, 0, -sx * 12)); e.scale = (1.0, 1.35, 1.0); parts.append(e)
    return parts


def _nose(hc, recipe):
    x, y, z = hc; fy = y - HEAD_R - 0.02; k = recipe.get('nose_size', 1.0)
    parts = [box((x, fy, z - 0.065), (0.14 * k, 0.07, 0.075 * k), M(recipe.get('nose', '#222228'), 0.25, coat=0.6), bevel=0.03 * k)]
    if recipe.get('teeth'):                                        # a rodent's two front teeth, on the upper lip of the mouth sticker
        parts += [box((x + sx * 0.034, fy + 0.012, z - 0.14), (0.058, 0.03, 0.075), M('#ffffff', 0.35), bevel=0.012) for sx in (-1, 1)]
    if recipe.get('whiskers'):
        for sx in (-1, 1):
            for dz, a in ((-0.05, 8), (-0.09, -6)):
                parts.append(box((x + sx * 0.3, fy + 0.01, z + dz), (0.26, 0.012, 0.012), M('#f4f4f6', 0.5), rot=(0, sx * a, 0), bevel=0))
    return parts


def _tail(kind, base, recipe):
    """Tail parts for a pivot at base, pointing back (+y) and up."""
    x, y, z = base; m = M(recipe.get('tail_color', recipe['fur']), 0.8)
    if kind == 'stub':
        return [box((x, y + 0.14, z + 0.14), (0.15, 0.15, 0.42), m, rot=(-40, 0, 0), bevel=0.05)]
    if kind == 'long':
        parts = [box((x, y + 0.2, z + 0.08), (0.13, 0.42, 0.13), m, rot=(25, 0, 0), bevel=0.05),
                 box((x, y + 0.42, z + 0.42), (0.13, 0.13, 0.5), m, rot=(-10, 0, 0), bevel=0.05)]
        if recipe.get('stripes'):                                  # tabby rings and a dark tip
            st = M(recipe['stripes'], 0.8)
            parts += [box((x, y + 0.22, z + 0.09), (0.145, 0.07, 0.145), st, rot=(25, 0, 0), bevel=0.02)]
            parts += [box((x, y + 0.42 + 0.17 * dz, z + 0.42 + dz), (0.145, 0.145, h), st, rot=(-10, 0, 0), bevel=0.02)
                      for dz, h in ((-0.1, 0.07), (0.07, 0.07), (0.21, 0.09))]
        return parts
    if kind == 'puff':
        return [_sphere((x, y + 0.08, z + 0.02), 0.17, M(recipe.get('tail_color', '#ffffff'), 0.9))]
    if kind == 'bushy':                                            # squirrel: thick, rising behind the back and curling forward at the top
        tip = M(recipe.get('tail_tip', recipe.get('tail_color', recipe['fur'])), 0.8)   # (it leans back, so the wag never pushes it into the head)
        return [box((x, y + 0.14, z + 0.12), (0.3, 0.32, 0.42), m, rot=(-35, 0, 0), bevel=0.1),
                box((x, y + 0.37, z + 0.5), (0.64, 0.52, 0.72), m, rot=(-20, 0, 0), bevel=0.23),
                box((x, y + 0.45, z + 0.97), (0.7, 0.54, 0.66), m, rot=(0, 0, 0), bevel=0.25),
                box((x, y + 0.25, z + 1.31), (0.62, 0.62, 0.44), m, rot=(30, 0, 0), bevel=0.2),
                box((x, y - 0.07, z + 1.3), (0.44, 0.36, 0.34), tip, rot=(65, 0, 0), bevel=0.15)]
    return []


def quad(recipe, loc):
    name = recipe['name']; x0, y0, z0 = loc; P = lambda x, y, z: (x0 + x, y0 + y, z0 + z)
    fur = M(recipe['fur'], 0.8); paw = M(recipe.get('paw', recipe['fur']), 0.75)
    L = recipe.get('leg', 0.5); W, D, H = 0.84, recipe.get('length', 1.5), 0.72      # leg length, body width, length, height
    fy, by = -D / 2 + 0.25, D / 2 - 0.25                                 # front and back legs
    root = empty(name, loc); top = L + H
    R = {'root': root, 'name': name, 'base': tuple(loc), 'kind': 'quad', 'feet': [],
         'contacts': dict(front=fy, back=by, hip=L + 0.1, leg=L + 0.1, toe=(-0.22, 0.14), body=[(-D / 2, L), (D / 2, L)] +
                          [(-D / 2 + 0.05 + dy, top + 0.2 + dz) for dy, dz in ((-0.37, 0), (-0.3, -0.25), (0, -0.35), (-0.3, 0.25), (0, 0.4))])}
    torso = _pivot(name + '_torso', P(0, 0, L + 0.1), root); R['torso'] = torso
    tparts = [box(P(0, 0, L + H / 2), (W, D, H), fur, bevel=0.07)]
    if recipe.get('belly'):                                              # a lighter chest patch
        tparts.append(box(P(0, -D / 2 - 0.006, L + H / 2 - 0.06), (W * 0.56, 0.02, H * 0.62), M(recipe['belly'], 0.85), bevel=0.01))
    if recipe.get('stripes'):                                            # tabby stripes across the back
        for yy in (-0.35, 0.0, 0.35):
            tparts.append(box(P(0, yy, top - 0.01), (W + 0.02, 0.11, 0.04), M(recipe['stripes'], 0.8), bevel=0.01))
            for sx in (-1, 1):
                tparts.append(box(P(sx * (W / 2 + 0.005), yy, top - 0.16), (0.02, 0.11, 0.3), M(recipe['stripes'], 0.8), bevel=0.005))
    for px, py, key, par in ((-0.25, fy, 'shL', torso), (0.25, fy, 'shR', torso), (-0.25, by, 'hipL', root), (0.25, by, 'hipR', root)):
        pv = _pivot(f'{name}_{key}', P(px, py, L + 0.1), par)
        foot = box(P(px, py - 0.04, 0.06), (0.3, 0.36, 0.12), paw, bevel=0.035)
        parent([box(P(px, py, (L + 0.22) / 2), (0.26, 0.28, L + 0.02), fur, bevel=0.035), foot], pv)
        R[key] = pv; R['feet'].append(foot)
    neck = _pivot(name + '_neck', P(0, -D / 2 + 0.15, top - 0.1), torso); R['neck'] = neck
    hc = P(0, -D / 2 + 0.05, top + 0.2); R['head_z'] = top + 0.2
    hparts = [_head(R, recipe, hc)] + _ears(recipe.get('ears', 'flop'), hc, recipe) + _nose(hc, recipe)
    if recipe.get('stripes'):                                            # tabby stripes over the top of the head and on the cheeks
        st = M(recipe['stripes'], 0.8); x, y, z = hc
        hparts += [box((x + dx, y + 0.06, z + HEAD_H / 2 + 0.004), (0.06, 0.42, 0.03), st, bevel=0.01) for dx in (-0.12, 0.0, 0.12)]
        hparts += [box((x + sx * (HEAD_R - 0.004), y - 0.02, z + dz), (0.03, 0.2, 0.045), st, bevel=0.01) for sx in (-1, 1) for dz in (-0.04, 0.07)]
    if recipe.get('collar'):                                             # Ginger's red collar and gold bell (our gag cat)
        x, y, z = hc; cz = z - HEAD_H / 2 + 0.07
        hparts += [cyl((x, y, cz), HEAD_R + 0.025, 0.09, M(recipe['collar'], 0.45), verts=64),
                   _sphere((x, y - HEAD_R - 0.06, cz - 0.07), 0.075, M('#f2c230', 0.2, metal=0.9))]
    tb = P(0, D / 2 - 0.05, top - 0.12)
    tail = _pivot(name + '_tail', tb, torso); R['tail'] = tail
    parent(_tail(recipe.get('tail', 'stub'), tb, recipe), tail)
    parent(tparts, torso); parent(hparts, neck)
    R['ground_parts'] = R['feet'] + tparts[:1]                           # a sitting animal rests on its body, not only its paws
    return R


def bird(recipe, loc):
    name = recipe['name']; x0, y0, z0 = loc; P = lambda x, y, z: (x0 + x, y0 + y, z0 + z)
    body = M(recipe['fur'], 0.75); wing = M(recipe.get('wing', recipe['fur']), 0.75); legs = M(recipe.get('legs', '#e0607a'), 0.6)
    L = recipe.get('leg', 0.42); root = empty(name, loc)
    R = {'root': root, 'name': name, 'base': tuple(loc), 'kind': 'bird', 'feet': [], 'leg': L, 'toe': 0.15}
    torso = _pivot(name + '_torso', P(0, 0, L), root); R['torso'] = torso
    tparts = [box(P(0, 0.12, L + 0.45), (0.9, 1.2, 0.86), body, rot=(-6, 0, 0), bevel=0.22)]
    if recipe.get('band'):                                               # the shiny neck feathers
        tparts.append(box(P(0, -0.1, L + 0.86), (0.93, 0.7, 0.16), M(recipe['band'], 0.25, metal=0.35), bevel=0.06))
    if recipe.get('belly'):
        tparts.append(box(P(0, -0.455, L + 0.38), (0.56, 0.02, 0.5), M(recipe['belly'], 0.8), bevel=0.01))
    for sx, side in ((-1, 'L'), (1, 'R')):
        sh = _pivot(f'{name}_sh{side}', P(sx * 0.47, 0.0, L + 0.78), torso)
        wp = [box(P(sx * 0.5, 0.12, L + 0.46), (0.1, 0.78, 0.62), wing, bevel=0.04)]
        for dz in (0.38, 0.24) if recipe.get('bar') else ():
            wp.append(box(P(sx * 0.556, 0.2, L + dz), (0.02, 0.5, 0.06), M(recipe['bar'], 0.7), bevel=0.005))
        parent(wp, sh); R['sh' + side] = sh
        hip = _pivot(f'{name}_hip{side}', P(sx * 0.2, 0, L + 0.04), root)
        foot = box(P(sx * 0.2, -0.06, 0.03), (0.24, 0.32, 0.06), legs, bevel=0.02)
        parent([box(P(sx * 0.2, 0, (L + 0.1) / 2), (0.09, 0.09, L + 0.1), legs, bevel=0.02), foot], hip)
        R['hip' + side] = hip; R['feet'].append(foot)
    neck = _pivot(name + '_neck', P(0, -0.1, L + 0.88), torso); R['neck'] = neck
    hc = P(0, -0.14, L + 0.88 + 0.33); R['head_z'] = L + 1.21
    x, y, z = hc; fy = y - HEAD_R
    beak = [box((x, fy - 0.1, z - 0.07), (0.1, 0.26, 0.07), M(recipe.get('beak', '#2b2b30'), 0.4), rot=(8, 0, 0), bevel=0.025),
            box((x, fy - 0.02, z - 0.03), (0.13, 0.07, 0.05), M('#ececf0', 0.6), bevel=0.02)]
    hparts = [_head(R, recipe, hc, layers=('brows', 'eyes'))] + beak
    tb = P(0, 0.62, L + 0.4)
    tail = _pivot(name + '_tail', tb, torso); R['tail'] = tail           # a fanned tail with a dark tip, sloping down behind
    parent([prism([(-0.16, 0), (0.16, 0), (0.3, -0.5), (-0.3, -0.5)], 0.07, (tb[0], tb[1] + 0.02, tb[2]), wing, rot=(62, 0, 0)),
            prism([(-0.3, -0.42), (0.3, -0.42), (0.31, -0.5), (-0.31, -0.5)], 0.075, (tb[0], tb[1] + 0.02, tb[2]), M(recipe.get('bar', '#3b4150'), 0.7), rot=(62, 0, 0), bevel=0.01)], tail)
    parent(tparts, torso); parent(hparts, neck)
    return R


def build_animal(recipe, loc=(0, 0, 0)):
    R = (quad if recipe['kind'] == 'quad' else bird)(recipe, loc)
    s = recipe.get('scale', 1.0); R['root'].scale = (s, s, s); R['scale'] = s
    set_face(R, 'calm')
    return R
