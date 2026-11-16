"""short-factory Blender kit: the reusable half of our "one world, one camera" Shorts (our first two episodes).
Use in an episode's world.py:   from common import *;  from sf_world import *;  T = timing('../voice/final_voice.words.json')
What is here: word timing, primitive helpers, toy figures and bottles, pop-ins, wobble/arc/ease, a camera rig of drifting holds
joined by whips that settles back into frame one (loop), Bullet physics baked to keys, the cartoon outline (OUTLINE=1),
the overlap CHECK (CHECK=1) and the finish step (STILLS=..., FRAME_START/FRAME_END, full render)."""
import json, math, os, sys
import bpy
from common import FPS, mat, hexrgb, camera, render

S = {'fr': lambda t: 1 + round(t * FPS), 'font': None}
lerp3 = lambda a, b, u: tuple(x + (y - x) * u for x, y in zip(a, b))
add = lambda a, b, k=1.0: tuple(x + k * y for x, y in zip(a, b))


class Timing:
    """Word times of the approved voice: T.at('but') is the start of the first "but"; T.at('but', after=40) a later one."""
    def __init__(self, path, tail=0.5):
        self.words = json.load(open(path, encoding='utf-8'))
        self.end = self.words[-1]['e'] + tail
        self.frames = round(self.end * FPS)
        self.loop = self.frames / FPS                      # the frame after the last one = frame one again

    def index(self, word, after=0):
        return next(i for i, w in enumerate(self.words) if i >= after and w['w'].lower().strip('.,?!') == word)

    def at(self, word, after=0):
        return self.words[self.index(word, after)]['s']


def timing(path, tail=0.5):
    return Timing(path, tail)


fr = lambda t: S['fr'](t)


def font(path='C:/Windows/Fonts/Montserrat-Black.ttf'):
    if S['font'] is None:
        S['font'] = bpy.data.fonts.load(path)
    return S['font']


# ---------------------------------------------------------------- primitives
def box(loc, size, m, rot=(0, 0, 0), bevel=0.02):
    bpy.ops.mesh.primitive_cube_add(size=1, location=loc, rotation=tuple(math.radians(r) for r in rot)); o = bpy.context.object
    o.scale = size; bpy.ops.object.transform_apply(scale=True)
    if bevel:
        b = o.modifiers.new('bev', 'BEVEL'); b.width = bevel; b.segments = 3
    o.data.materials.append(m)
    return o


def cyl(loc, r, depth, m, rot=(0, 0, 0), smooth=True, verts=48):
    bpy.ops.mesh.primitive_cylinder_add(radius=r, depth=depth, location=loc, vertices=verts, rotation=tuple(math.radians(a) for a in rot))
    o = bpy.context.object; o.data.materials.append(m)
    if smooth:
        bpy.ops.object.shade_smooth()
    return o


def cone(loc, r1, r2, depth, m, rot=(0, 0, 0)):
    bpy.ops.mesh.primitive_cone_add(radius1=r1, radius2=r2, depth=depth, location=loc, vertices=48, rotation=tuple(math.radians(a) for a in rot))
    o = bpy.context.object; o.data.materials.append(m); bpy.ops.object.shade_smooth()
    return o


def sphere(loc, r, m, scale=(1, 1, 1)):
    bpy.ops.mesh.primitive_uv_sphere_add(radius=r, location=loc, segments=48, ring_count=24); o = bpy.context.object
    o.scale = scale; o.data.materials.append(m); bpy.ops.object.shade_smooth()
    return o


def torus(loc, R, r, m, rot=(0, 0, 0)):
    bpy.ops.mesh.primitive_torus_add(major_radius=R, minor_radius=r, location=loc, rotation=tuple(math.radians(a) for a in rot), major_segments=64, minor_segments=16)
    o = bpy.context.object; o.data.materials.append(m); bpy.ops.object.shade_smooth()
    return o


def empty(name, loc=(0, 0, 0)):
    e = bpy.data.objects.new(name, None); bpy.context.collection.objects.link(e); e.location = loc
    return e


def parent(objs, root):
    bpy.context.view_layer.update()
    for o in objs:
        o.parent = root; o.matrix_parent_inverse = root.matrix_world.inverted()


def text(body, loc, size, m, rot=(90, 0, 0), extrude=0.03, align='CENTER'):
    cu = bpy.data.curves.new('T_' + body[:8], 'FONT'); cu.body = body; cu.font = font()
    cu.align_x = align; cu.align_y = 'CENTER'; cu.size = size; cu.extrude = extrude
    o = bpy.data.objects.new('T_' + body[:8], cu); bpy.context.collection.objects.link(o)
    o.location = loc; o.rotation_euler = tuple(math.radians(r) for r in rot); o.data.materials.append(m)
    return o


def pop(root, t_in, t_out=None, grow=0.25):
    """Scale 0 -> 1 with a small overshoot at t_in; back to 0 at t_out (so nothing shows where it shouldn't)."""
    keys = [(0, 0.0), (t_in - 0.01, 0.0), (t_in + grow * 0.7, 1.12), (t_in + grow, 1.0)]
    if t_out:
        keys += [(t_out, 1.0), (t_out + 0.2, 0.0)]
    for t, s in keys:
        root.scale = (s, s, s); root.keyframe_insert('scale', frame=max(1, fr(t)))


# ---------------------------------------------------------------- motion helpers
def ease(u, k=7.0):
    """Whip easing: almost still at both ends, very fast in the middle."""
    return (math.tanh(k * (u - 0.5)) / math.tanh(k / 2) + 1) / 2


def hermite(p0, m0, p1, m1, T, u):
    h00, h10, h01, h11 = 2 * u ** 3 - 3 * u ** 2 + 1, u ** 3 - 2 * u ** 2 + u, -2 * u ** 3 + 3 * u ** 2, u ** 3 - u ** 2
    return tuple(h00 * a + h10 * T * b + h01 * c + h11 * T * d for a, b, c, d in zip(p0, m0, p1, m1))


def arc(p0, p1, h, u):
    """A throw: straight line from p0 to p1 plus a parabola of height h."""
    return (p0[0] + (p1[0] - p0[0]) * u, p0[1] + (p1[1] - p0[1]) * u, p0[2] + (p1[2] - p0[2]) * u + 4 * h * u * (1 - u))


def wobble(t, hits, amp=9.0, freq=3.2, decay=5.5):
    """Damped rock on the base after each landing (radians): it lands, rocks, settles."""
    for h in hits:
        d = t - h
        if 0 <= d < 1.2:
            return math.radians(amp) * math.exp(-decay * d) * math.sin(2 * math.pi * freq * d)
    return 0.0


# ---------------------------------------------------------------- props
def bottle_materials():
    return {'plastic': mat('Bottle', hexrgb('#bfe6ff'), rough=0.05, coat=1.0),
            'water': mat('Water', hexrgb('#3fa9ff'), rough=0.1, emit=hexrgb('#3fa9ff'), emit_strength=0.3),
            'label': mat('Label', hexrgb('#ff4a5a'), rough=0.4), 'cap': mat('Cap', hexrgb('#1f6fff'), rough=0.3)}


def make_bottle(name, loc, M=None):
    M = M or S.setdefault('bottle_mats', bottle_materials())
    root = empty(name, loc)
    parts = [cyl((loc[0], loc[1], loc[2] + 0.11), 0.045, 0.22, M['plastic']), cyl((loc[0], loc[1], loc[2] + 0.07), 0.046, 0.12, M['water']),
             cyl((loc[0], loc[1], loc[2] + 0.12), 0.0465, 0.06, M['label']), cone((loc[0], loc[1], loc[2] + 0.245), 0.045, 0.018, 0.05, M['plastic']),
             cyl((loc[0], loc[1], loc[2] + 0.28), 0.02, 0.025, M['cap'])]
    parent(parts, root)
    return root


BOTTLES = []                                         # (root, base, launch times, duration, height): posed every frame by pose_bottles(t)


def flip(root, base, launch, dur=0.95, height=0.55):
    for b in BOTTLES:
        if b[0] is root:
            b[2].append(launch); return
    BOTTLES.append((root, base, [launch], dur, height))


def bottle_pose(base, launches, dur, height, t):
    """Up in a parabola and one full turn; rocks and settles after landing."""
    for l in launches:
        u = (t - l) / dur
        if 0 <= u <= 1:
            return (base[0], base[1], base[2] + 4 * height * u * (1 - u)), 2 * math.pi * (1 - (1 - u) ** 1.6)
    return base, wobble(t, [l + dur for l in launches])


def pose_bottles(t):
    for root, base, launches, dur, height in BOTTLES:
        loc, a = bottle_pose(base, launches, dur, height, t)
        root.location = loc; root.rotation_euler = (0, a, 0)


def figure(name, loc, h, m, arm_up=False, rot_z=0, eyes=False):
    """A faceless toy figure (never a real person's likeness): rounded body, ball head, arms hinged at the shoulders.
    eyes=True adds two cartoon eyes looking forward (for our generic 'viewer', never for real people)."""
    x, y, z = loc
    root = empty(name, loc)
    parts = []
    for sx in (-1, 1):
        parts += [cyl((x + sx * 0.08 * h, y, z + 0.2 * h), 0.065 * h, 0.34 * h, m), sphere((x + sx * 0.08 * h, y, z + 0.035 * h), 0.07 * h, m, scale=(1, 1.3, 0.6))]
    parts += [sphere((x, y, z + 0.56 * h), 0.2 * h, m, scale=(1, 0.8, 1.35)), cyl((x, y, z + 0.84 * h), 0.05 * h, 0.08 * h, m),
              sphere((x, y, z + 1.02 * h), 0.19 * h, m)]
    L = 0.36 * h
    for sx, ang in ((-1, -14), (1, 160 if arm_up else 14)):
        sh = (x + sx * 0.19 * h, y, z + 0.74 * h)
        d = (math.sin(math.radians(ang)), 0, -math.cos(math.radians(ang)))
        parts.append(cyl(tuple(sh[i] + d[i] * L / 2 for i in range(3)), 0.048 * h, L, m, rot=(0, -ang, 0)))
        parts.append(sphere(tuple(sh[i] + d[i] * L for i in range(3)), 0.06 * h, m))
        parts.append(sphere(sh, 0.055 * h, m))
    if eyes:
        ew = mat('EyeWhite', (1, 1, 1), rough=0.2, coat=1.0); pu = mat('Pupil', hexrgb('#101420'), rough=0.2)
        for sx in (-1, 1):
            parts.append(sphere((x + sx * 0.065 * h, y - 0.16 * h, z + 1.05 * h), 0.052 * h, ew, scale=(1, 0.6, 1.2)))
            parts.append(sphere((x + sx * 0.065 * h, y - 0.196 * h, z + 1.03 * h), 0.024 * h, pu))
    parent(parts, root)
    root.rotation_euler = (0, 0, math.radians(rot_z))
    return root


# ---------------------------------------------------------------- camera: drifting holds joined by whips, settling into frame one
def camera_rig(shots, frames, t_loop, open_pose=None, t_open=None, lens=32, fstop=2.8):
    """shots: [(start, end, cam_from, cam_to, look_from, look_to, lift_of_the_whip_into_this_hold), ...].
    open_pose(t) -> (cam, look) optionally drives the first hold (e.g. a close-up that pulls back). After the last hold the
    camera eases (Hermite) into the exact frame-one position and speed, so the Short loops. Returns (cam, target, whips)."""
    target = empty('Target'); cam = camera(lens=lens, focus_obj=target, fstop=fstop)
    tc = cam.constraints.new('TRACK_TO'); tc.target = target; tc.track_axis = 'TRACK_NEGATIVE_Z'; tc.up_axis = 'UP_Y'
    t_open = t_open if t_open is not None else shots[0][1]
    first = open_pose or (lambda t: (lerp3(shots[0][2], shots[0][3], t / (shots[0][1] - shots[0][0])), lerp3(shots[0][4], shots[0][5], t / (shots[0][1] - shots[0][0]))))
    C0, T0 = first(0.0)
    V = tuple((a - b) * FPS for a, b in zip(first(1 / FPS)[0], C0)); VT = tuple((a - b) * FPS for a, b in zip(first(1 / FPS)[1], T0))
    t_settle = shots[-1][1]

    def pose(t):
        if t > t_settle:
            s = shots[-1]; T = t_loop - t_settle
            vc = tuple((b - a) / (s[1] - s[0]) for a, b in zip(s[2], s[3])); vg = tuple((b - a) / (s[1] - s[0]) for a, b in zip(s[4], s[5]))
            u = (t - t_settle) / T
            return hermite(s[3], vc, C0, V, T, u), hermite(s[5], vg, T0, VT, T, u)
        if t <= t_open:
            return first(t)
        for n, (t0, t1, c0, c1, g0, g1, lift) in enumerate(shots):
            if t <= t1 or n == len(shots) - 1:
                if t >= t0 or n == 0:
                    u = (t - t0) / (t1 - t0)
                    return lerp3(c0, c1, u), lerp3(g0, g1, u)
                p = shots[n - 1]; u = ease((t - p[1]) / (t0 - p[1]))
                c = lerp3(p[3], c0, u); g = lerp3(p[5], g0, u); h = lift * math.sin(math.pi * u)
                return (c[0], c[1], c[2] + h), (g[0], g[1] + 1.0 * h, g[2] + 0.4 * h)

    bpy.context.preferences.edit.keyframe_new_interpolation_type = 'LINEAR'
    for f in range(1, frames + 2):
        c, g = pose((f - 1) / FPS)
        cam.location = c; cam.keyframe_insert('location', frame=f); target.location = g; target.keyframe_insert('location', frame=f)
    sc = bpy.context.scene
    for owner, items in ((sc.render, (('use_motion_blur', True), ('motion_blur_shutter', 0.5))),
                         (sc.eevee, (('use_motion_blur', True), ('motion_blur_shutter', 0.5), ('motion_blur_steps', 1), ('motion_blur_max', 512)))):
        for k, v in items:
            if hasattr(owner, k):
                setattr(owner, k, v)
    whips = [(round(shots[n - 1][1], 2), shots[n][6]) for n in range(1, len(shots))]
    return cam, target, whips


# ---------------------------------------------------------------- physics: Bullet rigid bodies, simulated once and baked to keys
def bake_physics(dynamic, passive, frames, fps=FPS):
    """dynamic: [(obj, release_time, shape 'SPHERE'|'CONVEX_HULL'|'BOX', bounce, density)] - held by their animation until
    released; passive: [(obj, shape, bounce)] - colliders (floor, figures, props). Afterwards the rigid bodies are removed and the
    motion is plain keyframes, so stills, CHECK and renders are deterministic."""
    sc = bpy.context.scene
    with bpy.context.temp_override(scene=sc):
        bpy.ops.rigidbody.world_add()
    rbw = sc.rigidbody_world; rbw.collection = bpy.data.collections.new('RigidBodyWorld')
    rbw.point_cache.frame_start, rbw.point_cache.frame_end = 1, frames + 1
    rbw.substeps_per_frame, rbw.solver_iterations = 10, 10

    def rigid(ob, kind, shape, bounce, density=None, friction=0.6):
        with bpy.context.temp_override(object=ob, active_object=ob, selected_objects=[ob], selected_editable_objects=[ob]):
            bpy.ops.rigidbody.object_add(type=kind)
        rb = ob.rigid_body; rb.collision_shape = shape; rb.friction, rb.restitution = friction, bounce
        rb.use_margin, rb.collision_margin = True, 0.001
        if density:
            rb.mass = max(ob.dimensions.x * ob.dimensions.y * ob.dimensions.z * 0.52 * density, 0.01)

    for ob, shape, bounce in passive:
        rigid(ob, 'PASSIVE', shape, bounce, friction=0.8)
    for ob, rel, shape, bounce, density in dynamic:
        rigid(ob, 'ACTIVE', shape, bounce, density)
        for t, kin in ((0, True), (rel - 1 / fps, True), (rel, False)):
            ob.rigid_body.kinematic = kin; ob.rigid_body.keyframe_insert('kinematic', frame=max(1, fr(t)))
    samples = {d[0]: [] for d in dynamic}
    for f in range(1, frames + 2):
        sc.frame_set(f)
        for o in samples:
            samples[o].append((f, o.matrix_world.copy()))
    for o in [o for o in bpy.data.objects if o.rigid_body]:
        with bpy.context.temp_override(object=o, active_object=o, selected_objects=[o], selected_editable_objects=[o]):
            bpy.ops.rigidbody.object_remove()
    with bpy.context.temp_override(scene=sc):
        bpy.ops.rigidbody.world_remove()
    for o, smp in samples.items():
        o.rotation_mode = 'QUATERNION'
        for f, m in smp:
            o.matrix_world = m; o.keyframe_insert('location', frame=f); o.keyframe_insert('rotation_quaternion', frame=f)
    low = min((m.translation.z for smp in samples.values() for _, m in smp), default=0)
    print('physics: baked', len(samples), 'bodies, lowest centre z', round(low, 3))


# ---------------------------------------------------------------- cartoon outline (inverted hull), on when OUTLINE=1
def add_outline(color='#1a2033', skip=('Floor',)):
    ol = bpy.data.materials.new('Outline'); ol.use_backface_culling = True
    nt = ol.node_tree; nt.nodes.clear()               # dark ink for the camera, invisible to shadow rays (no dark shading inside)
    em = nt.nodes.new('ShaderNodeEmission'); em.inputs['Color'].default_value = (*hexrgb(color), 1); em.inputs['Strength'].default_value = 1.0
    tr = nt.nodes.new('ShaderNodeBsdfTransparent'); lp = nt.nodes.new('ShaderNodeLightPath'); mx = nt.nodes.new('ShaderNodeMixShader')
    nt.links.new(lp.outputs['Is Shadow Ray'], mx.inputs[0]); nt.links.new(em.outputs[0], mx.inputs[1]); nt.links.new(tr.outputs[0], mx.inputs[2])
    mo = nt.nodes.new('ShaderNodeOutputMaterial'); nt.links.new(mx.outputs[0], mo.inputs['Surface'])
    for o in [o for o in bpy.data.objects if o.type == 'MESH' and not o.name.startswith(skip)]:
        o.data.materials.append(ol)
        sol = o.modifiers.new('outline', 'SOLIDIFY')
        sol.thickness = -min(0.016, max(0.004, 0.03 * max(o.dimensions)))
        sol.use_flip_normals = True; sol.use_rim = False; sol.material_offset = len(o.data.materials) - 1


# ---------------------------------------------------------------- overlap CHECK: nothing may pass through anything
kids = lambda root: [root] + list(root.children_recursive)


def world_box(objs):
    from mathutils import Vector
    dg = bpy.context.evaluated_depsgraph_get(); lo = [1e9] * 3; hi = [-1e9] * 3
    for o in objs:
        if o.type != 'MESH' or o.hide_render:
            continue
        oe = o.evaluated_get(dg)
        for c in oe.bound_box:
            p = oe.matrix_world @ Vector(c)
            for i in range(3):
                lo[i] = min(lo[i], p[i]); hi[i] = max(hi[i], p[i])
    return lo, hi


def overlap(a, b, shrink=0.02):
    (al, ah), (bl, bh) = a, b
    return all(al[i] + shrink < bh[i] - shrink and bl[i] + shrink < ah[i] - shrink for i in range(3))


def run_check(checks, frames):
    """checks: [(name, [objects A], [objects B])]. Prints 'CHECK name : clear' or the overlapping frames, then exits."""
    sc = bpy.context.scene; hits = {}
    for f in range(1, frames + 1, 2):
        sc.frame_set(f)
        for name, A, B in checks:
            if A and B and overlap(world_box(A), world_box(B)):
                hits.setdefault(name, []).append(f)
    for name, *_ in checks:
        fs = hits.get(name, [])
        print('CHECK', name, ':', 'clear' if not fs else f'{len(fs)} frames overlap, first {fs[:6]}')
    sys.exit(0)


# ---------------------------------------------------------------- finish: CHECK / STILLS / partial or full render
def finish(out, still, T, whips, checks=(), per_frame=None):
    sc = bpy.context.scene
    if per_frame:
        bpy.app.handlers.frame_change_pre.append(per_frame)
    print('world: frames', T.frames, 'end', round(T.end, 2), 'whips at', [w[0] for w in whips])
    print('WHIPS_JSON', json.dumps(whips))
    if os.environ.get('SF_COUNT'):
        sys.exit(0)
    if os.environ.get('CHECK'):
        run_check(list(checks), T.frames)
    if os.environ.get('FRAME_START'):
        sc.frame_start, sc.frame_end = int(os.environ['FRAME_START']), int(os.environ['FRAME_END'])
    if os.environ.get('STILLS'):
        for f in map(int, os.environ['STILLS'].split(',')):
            render(os.path.join(out, f'{f:04d}.png'), f)
    else:
        render(out, still)
