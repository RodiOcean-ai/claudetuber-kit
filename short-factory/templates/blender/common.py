"""short-factory shared look: bright pale-blue studio world, soft daylight, vertical 9:16, shallow focus (bright toy look).
world.py imports this, builds its set, and renders: blender -b --factory-startup --python world.py -- <out> [--still FRAME]"""
import math, os, sys, random
import bpy

FPS = 30
DARK = False       # bright toy-look world (pale-blue sky, soft daylight)
LIGHT = 0.15 if DARK else 1.0
GOLD, CYAN, RED = '#ffb020', '#28d7ff', '#ff3b4f'


def args():
    a = sys.argv[sys.argv.index('--') + 1:] if '--' in sys.argv else []
    out = a[0] if a else '//render/'
    still = int(a[a.index('--still') + 1]) if '--still' in a else None
    return out, still


def reset(frames):
    bpy.ops.wm.read_factory_settings(use_empty=True)
    sc = bpy.context.scene
    # vertical Short by default; WIDE=1 renders 16:9 for long videos (the survival long video, 7 Nov 2026)
    sc.render.resolution_x, sc.render.resolution_y = (1920, 1080) if os.environ.get('WIDE') == '1' else (1080, 1920)
    sc.render.fps = FPS
    sc.frame_start, sc.frame_end = 1, frames
    for eng in ('BLENDER_EEVEE', 'BLENDER_EEVEE_NEXT'):
        try:
            sc.render.engine = eng
            break
        except TypeError:
            continue
    ee = sc.eevee
    for k, v in (('use_raytracing', True), ('taa_render_samples', 48), ('use_shadows', True), ('shadow_ray_count', 2), ('use_fast_gi', True)):
        if hasattr(ee, k):
            setattr(ee, k, v)
    sc.view_settings.view_transform = 'AgX'
    looks = [i.identifier for i in sc.view_settings.bl_rna.properties['look'].enum_items]
    for lk in ('AgX - Punchy', 'Punchy', 'AgX - Medium High Contrast'):
        if lk in looks:
            sc.view_settings.look = lk
            break
    sc.render.film_transparent = False
    if DARK:
        sc.view_settings.view_transform = 'Standard'   # keeps glows saturated (AgX washes them pastel)
        sc.view_settings.look = 'None'
        bloom(sc)
    return sc


def bloom(sc):
    """Soft glow around bright, emissive things (compositor glare). Works on old and new (5.x) compositor APIs."""
    if hasattr(sc, 'compositing_node_group'):
        ng = bpy.data.node_groups.new('Bloom', 'CompositorNodeTree')
        sc.compositing_node_group = ng
        gi = ng.nodes.new('NodeGroupInput'); go = ng.nodes.new('NodeGroupOutput')
        ng.interface.new_socket('Image', in_out='INPUT', socket_type='NodeSocketColor')
        ng.interface.new_socket('Image', in_out='OUTPUT', socket_type='NodeSocketColor')
        rl = ng.nodes.new('CompositorNodeRLayers')
        out_node, src = go, rl.outputs['Image']
    else:
        sc.use_nodes = True
        ng = sc.node_tree
        ng.nodes.clear()
        rl = ng.nodes.new('CompositorNodeRLayers')
        out_node = ng.nodes.new('CompositorNodeComposite')
        src = rl.outputs['Image']
    g = ng.nodes.new('CompositorNodeGlare')
    for attr, val in (('glare_type', 'BLOOM'), ('quality', 'HIGH'), ('threshold', 0.8), ('size', 7), ('mix', 0.0)):
        try:
            setattr(g, attr, val)
        except Exception:
            pass
    for name, val in (('Type', 'Bloom'), ('Threshold', 0.8), ('Strength', 0.9), ('Size', 0.6), ('Quality', 'High')):
        if name in g.inputs:
            try:
                g.inputs[name].default_value = val
            except Exception:
                pass
    ng.links.new(src, g.inputs['Image'])
    ng.links.new(g.outputs['Image'], out_node.inputs[0])


def mat(name, rgb, rough=0.4, metal=0.0, emit=None, emit_strength=0.0, coat=0.0):
    m = bpy.data.materials.new(name)
    m.use_nodes = True
    b = m.node_tree.nodes['Principled BSDF']
    b.inputs['Base Color'].default_value = (*rgb, 1)
    b.inputs['Roughness'].default_value = rough
    b.inputs['Metallic'].default_value = metal
    if coat and 'Coat Weight' in b.inputs:
        b.inputs['Coat Weight'].default_value = coat
    if emit:
        b.inputs['Emission Color'].default_value = (*emit, 1)
        b.inputs['Emission Strength'].default_value = emit_strength
    return m


def hexrgb(h):
    h = h.lstrip('#')
    lin = lambda c: (c / 255) / 12.92 if c / 255 <= 0.04045 else (((c / 255) + 0.055) / 1.055) ** 2.4
    return tuple(lin(int(h[i:i + 2], 16)) for i in (0, 2, 4))


def world(top=None, horizon=None, strength=None):
    top = top or ('#04060d' if DARK else '#6fb6ff'); horizon = horizon or ('#071028' if DARK else '#e6f3ff')
    strength = strength if strength is not None else (1.0 if DARK else 1.25)
    """Sky gradient: brighter near the horizon, bluer above (camera-facing gradient)."""
    w = bpy.data.worlds.new('World')
    bpy.context.scene.world = w
    w.use_nodes = True
    nt = w.node_tree
    nt.nodes.clear()
    out = nt.nodes.new('ShaderNodeOutputWorld')
    bg = nt.nodes.new('ShaderNodeBackground')
    tc = nt.nodes.new('ShaderNodeTexCoord')
    sep = nt.nodes.new('ShaderNodeSeparateXYZ')
    ramp = nt.nodes.new('ShaderNodeValToRGB')
    ramp.color_ramp.elements[0].position = 0.0
    ramp.color_ramp.elements[0].color = (*hexrgb(horizon), 1)
    ramp.color_ramp.elements[1].position = 0.45
    ramp.color_ramp.elements[1].color = (*hexrgb(top), 1)
    nt.links.new(tc.outputs['Generated'], sep.inputs[0])
    nt.links.new(sep.outputs['Z'], ramp.inputs['Fac'])
    nt.links.new(ramp.outputs['Color'], bg.inputs['Color'])
    bg.inputs['Strength'].default_value = strength
    nt.links.new(bg.outputs[0], out.inputs[0])
    # Generated Z for the world runs 0..1 from down to up; shift so the horizon sits at 0
    mapn = nt.nodes.new('ShaderNodeMapping')
    nt.links.new(tc.outputs['Generated'], mapn.inputs['Vector'])
    mapn.inputs['Location'].default_value[2] = -0.5
    mapn.inputs['Scale'].default_value[2] = 2.0
    nt.links.new(mapn.outputs['Vector'], sep.inputs[0])
    return w


def floor(color=None, size=400):
    color = color or ('#030408' if DARK else '#cfe6ff')
    bpy.ops.mesh.primitive_plane_add(size=size, location=(0, 0, 0))
    f = bpy.context.object
    f.name = 'Floor'
    f.data.materials.append(mat('Floor', hexrgb(color), rough=0.28 if DARK else 0.92))
    return f


def sun(energy=3.5, angle_deg=12, rot=(52, 0, 35), color='#fff6ea'):
    d = bpy.data.lights.new('Sun', 'SUN')
    d.energy = energy * LIGHT
    d.angle = math.radians(angle_deg)
    d.color = hexrgb(color)
    o = bpy.data.objects.new('Sun', d)
    bpy.context.collection.objects.link(o)
    o.rotation_euler = tuple(math.radians(r) for r in rot)
    return o


def area(loc, rot, size=4, energy=400, color='#ffffff'):
    d = bpy.data.lights.new('Fill', 'AREA')
    d.size = size
    d.energy = energy * LIGHT
    d.color = hexrgb(color)
    o = bpy.data.objects.new('Fill', d)
    bpy.context.collection.objects.link(o)
    o.location = loc
    o.rotation_euler = tuple(math.radians(r) for r in rot)
    return o


def rim(loc, rot, color=None, energy=900, size=3):
    """A coloured back light that outlines objects against the dark (no-op in the bright look)."""
    if not DARK:
        return None
    return area(loc, rot, size=size, energy=energy / LIGHT, color=color or CYAN)


def camera(lens=32, focus_obj=None, fstop=2.8):
    c = bpy.data.cameras.new('Cam')
    c.lens = lens
    c.sensor_fit = 'VERTICAL'
    c.sensor_height = 36
    if focus_obj is not None:
        c.dof.use_dof = True
        c.dof.focus_object = focus_obj
        c.dof.aperture_fstop = fstop
    o = bpy.data.objects.new('Cam', c)
    bpy.context.collection.objects.link(o)
    bpy.context.scene.camera = o
    return o


def look_at(obj, target):
    from mathutils import Vector
    d = Vector(target) - obj.location
    obj.rotation_euler = d.to_track_quat('-Z', 'Y').to_euler()


def key_cam(cam, frame, loc, target):
    cam.location = loc
    look_at(cam, target)
    cam.keyframe_insert('location', frame=frame)
    cam.keyframe_insert('rotation_euler', frame=frame)


def smooth_all():
    for o in bpy.data.objects:
        if o.animation_data and o.animation_data.action:
            act = o.animation_data.action
            curves = getattr(act, 'fcurves', None)
            if curves is None:   # Blender 5 layered actions
                curves = [fc for l in act.layers for s in l.strips for cb in s.channelbags for fc in cb.fcurves]
            for fc in curves:
                for k in fc.keyframe_points:
                    k.interpolation = 'BEZIER'
                    k.easing = 'AUTO'


def render(out, still):
    sc = bpy.context.scene
    if still is not None:
        sc.frame_set(still)
        sc.render.filepath = out
        sc.render.image_settings.file_format = 'PNG'
        bpy.ops.render.render(write_still=True)
    else:
        sc.render.filepath = out
        sc.render.image_settings.file_format = 'PNG'
        bpy.ops.render.render(animation=True)
