"""Barullo logo prototypes in the carpet style. Run: blender -b --factory-startup --python logo3d.py -- <dir> <variant>"""
import bpy, bmesh, json, math, os, sys, random
from mathutils import Vector

D, VAR = sys.argv[sys.argv.index('--') + 1:][:2]
TEX = os.path.join(D, 'tex')
data = json.load(open(os.path.join(D, 'wordmark.json')))
IW, IH = data['w'], data['h']
WIDTH = 8.0
S = WIDTH / IW
HEIGHT = IH * S

sc = bpy.context.scene
for o in list(bpy.data.objects):
    bpy.data.objects.remove(o)
for eng in ('BLENDER_EEVEE_NEXT', 'BLENDER_EEVEE'):
    try:
        sc.render.engine = eng; break
    except TypeError:
        pass
ee = sc.eevee
for attr, val in (('use_raytracing', True), ('taa_render_samples', 96), ('use_shadows', True)):
    if hasattr(ee, attr):
        setattr(ee, attr, val)
if hasattr(ee, 'ray_tracing_options'):
    ee.ray_tracing_options.resolution_scale = '1'
sc.render.resolution_x, sc.render.resolution_y = 1600, 1000
sc.render.film_transparent = False
sc.view_settings.view_transform = 'AgX' if 'AgX' in [i.identifier for i in bpy.types.ColorManagedViewSettings.bl_rna.properties['view_transform'].enum_items] else 'Filmic'
try:
    sc.view_settings.look = 'AgX - Punchy'
except TypeError:
    pass

def world(col=(0.01, 0.01, 0.012), strength=1.0):
    w = bpy.data.worlds.new('w'); sc.world = w; w.use_nodes = True
    bg = next(n for n in w.node_tree.nodes if n.type == 'BACKGROUND')
    bg.inputs[0].default_value = (*col, 1); bg.inputs[1].default_value = strength

def mat(name, base=(0.8, 0.05, 0.03), metal=0.0, rough=0.3, coat=0.0, img=None, emit=None, emit_strength=0.0, attr=None):
    m = bpy.data.materials.new(name); m.use_nodes = True
    nt = m.node_tree
    p = next(n for n in nt.nodes if n.type == 'BSDF_PRINCIPLED')
    p.inputs['Base Color'].default_value = (*base, 1)
    p.inputs['Metallic'].default_value = metal
    p.inputs['Roughness'].default_value = rough
    if 'Coat Weight' in p.inputs:
        p.inputs['Coat Weight'].default_value = coat
        p.inputs['Coat Roughness'].default_value = 0.03
    if img:
        tx = nt.nodes.new('ShaderNodeTexImage')
        tx.image = bpy.data.images.load(img); tx.interpolation = 'Closest'
        tc = nt.nodes.new('ShaderNodeTexCoord')
        if img.endswith('letters-riso.png'):
            mp = nt.nodes.new('ShaderNodeMapping')
            mp.inputs['Scale'].default_value = (1 / WIDTH, 1 / HEIGHT, 1)
            mp.inputs['Location'].default_value = (0.5, 0.5, 0)
            nt.links.new(tc.outputs['Object'], mp.inputs['Vector'])
            nt.links.new(mp.outputs['Vector'], tx.inputs['Vector'])
        else:
            nt.links.new(tc.outputs['UV'], tx.inputs['Vector'])
        nt.links.new(tx.outputs['Color'], p.inputs['Base Color'])
        if emit_strength:
            nt.links.new(tx.outputs['Color'], p.inputs['Emission Color'])
            p.inputs['Emission Strength'].default_value = emit_strength
    if attr:
        at = nt.nodes.new('ShaderNodeAttribute'); at.attribute_name = attr
        nt.links.new(at.outputs['Color'], p.inputs['Base Color'])
        if emit_strength:
            nt.links.new(at.outputs['Color'], p.inputs['Emission Color'])
            p.inputs['Emission Strength'].default_value = emit_strength
    return m

def wordmark(extrude=0.18, bevel=0.06, offset=-0.05, res=5):
    cu = bpy.data.curves.new('wm', 'CURVE'); cu.dimensions = '2D'; cu.fill_mode = 'BOTH'
    for poly in data['polys']:
        sp = cu.splines.new('POLY'); sp.points.add(len(poly) - 2)
        for i, (x, y) in enumerate(poly[:-1]):
            sp.points[i].co = ((x - IW / 2) * S, -(y - IH / 2) * S, 0, 1)
        sp.use_cyclic_u = True
    cu.extrude = extrude; cu.bevel_depth = bevel; cu.bevel_resolution = res; cu.offset = offset
    ob = bpy.data.objects.new('wordmark', cu); sc.collection.objects.link(ob)
    bpy.context.view_layer.objects.active = ob; ob.select_set(True)
    bpy.ops.object.convert(target='MESH')
    ob = bpy.context.view_layer.objects.active
    for poly in ob.data.polygons:
        poly.use_smooth = True
    return ob

def area(name, loc, size, energy, color=(1, 1, 1), target=(0, 0, 0)):
    l = bpy.data.lights.new(name, 'AREA'); l.size = size; l.energy = energy; l.color = color
    o = bpy.data.objects.new(name, l); sc.collection.objects.link(o); o.location = loc
    d = Vector(target) - Vector(loc); o.rotation_euler = d.to_track_quat('-Z', 'Y').to_euler()
    return o

def panel(loc, size, strength, color=(1, 1, 1), target=(0, 0, 0)):
    bpy.ops.mesh.primitive_plane_add(size=1, location=loc)
    o = bpy.context.object; o.scale = (*size, 1)
    d = Vector(target) - Vector(loc); o.rotation_euler = d.to_track_quat('Z', 'Y').to_euler()
    m = bpy.data.materials.new('softbox'); m.use_nodes = True
    nt = m.node_tree; [nt.nodes.remove(n) for n in list(nt.nodes)]
    em = nt.nodes.new('ShaderNodeEmission'); em.inputs[0].default_value = (*color, 1); em.inputs[1].default_value = strength
    out = nt.nodes.new('ShaderNodeOutputMaterial'); nt.links.new(em.outputs[0], out.inputs[0])
    o.data.materials.append(m); o.visible_camera = False
    return o

def camera(loc, target, lens=50, dof=None):
    c = bpy.data.cameras.new('cam'); c.lens = lens
    o = bpy.data.objects.new('cam', c); sc.collection.objects.link(o); o.location = loc
    d = Vector(target) - Vector(loc); o.rotation_euler = d.to_track_quat('-Z', 'Y').to_euler()
    sc.camera = o
    if dof:
        c.dof.use_dof = True; c.dof.aperture_fstop = dof
        c.dof.focus_distance = d.length
    return o

def sparkles(n, spread, z, seed=1, scale=0.06):
    random.seed(seed)
    m = mat('spark', base=(1, 1, 1), metal=1, rough=0.05)
    for i in range(n):
        bpy.ops.mesh.primitive_uv_sphere_add(radius=scale * random.uniform(0.5, 1.4), location=(random.uniform(-spread[0], spread[0]), random.uniform(-spread[1], spread[1]), z + random.uniform(-0.2, 0.4)))
        o = bpy.context.object; o.data.materials.append(m); bpy.ops.object.shade_smooth()

def carpet_wall(loc, size, strength, target):
    bpy.ops.mesh.primitive_plane_add(size=1, location=loc)
    o = bpy.context.object; o.scale = (*size, 1)
    d = Vector(target) - Vector(loc); o.rotation_euler = d.to_track_quat('Z', 'Y').to_euler()
    m = mat('wall', img=os.path.join(TEX, 'carpet-riso.jpg'), emit_strength=strength)
    o.data.materials.append(m); o.visible_camera = False
    return o

RED = (0.75, 0.03, 0.02)

if VAR == 'hinchable':
    world((0.004, 0.004, 0.006))
    ob = wordmark(extrude=0.16, bevel=0.085, offset=-0.075, res=8)
    ob.data.materials.append(mat('carpet-plastic', rough=0.32, coat=1.0, img=os.path.join(TEX, 'letters-riso.png')))
    ob.rotation_euler = (math.radians(97), 0, math.radians(-12))
    camera((0, -12.5, 0.8), (0, 0, 0), lens=55)
    area('key', (-3, -7, 4), 6, 2600)
    area('fill', (5, -6, 0), 5, 900, (1, 0.8, 0.7))
    area('rimP', (5, 4, 2), 3, 2200, (1, 0.25, 0.6))
    area('rimO', (-5, 4, -1), 3, 1500, (1, 0.55, 0.15))
    panel((0, -7, 4.5), (10, 2.2), 7)
    panel((-6, -5, 0), (1.5, 6), 4, (1, 0.5, 0.75))

elif VAR == 'cromo':
    sc.render.engine = 'CYCLES'; sc.cycles.samples = 96; sc.cycles.use_denoising = True; sc.cycles.device = 'CPU'
    world((0.01, 0.006, 0.006))
    ob = wordmark(extrude=0.22, bevel=0.035, offset=-0.03, res=4)
    ob.data.materials.append(mat('chrome', base=(0.95, 0.95, 0.97), metal=1.0, rough=0.06))
    ob.rotation_euler = (math.radians(90), 0, 0)
    ob.location = (0, 0, HEIGHT / 2 + 0.02)
    bpy.ops.mesh.primitive_plane_add(size=1, location=(0, 1.2, 0))
    fl = bpy.context.object; fl.scale = (11, 11 * 1176 / 840, 1)
    fl.data.materials.append(mat('rug', rough=0.85, img=os.path.join(D, 'tex', 'carpet-riso.jpg')))
    camera((2.4, -11.5, 1.4), (0, 0, 1.3), lens=45, dof=4.0)
    area('key', (-3, -5, 6), 4, 900)
    area('rim', (3, 5, 3), 4, 1800, (1, 0.35, 0.5))
    carpet_wall((0, -15, 2.5), (22, 30.8), 1.2, (0, 0, 1.3))
    panel((0, -6, 5.5), (10, 1.2), 8)
    panel((-7, -2, 2), (1.2, 6), 4, (1, 0.6, 0.3))

elif VAR == 'tapiz':
    world((0.006, 0.006, 0.008))
    bpy.ops.mesh.primitive_plane_add(size=1)
    rug = bpy.context.object; rug.scale = (7.2, 7.2 * 104 / 240, 1)
    bpy.ops.object.transform_apply(scale=True)
    bpy.ops.object.mode_set(mode='EDIT'); bpy.ops.mesh.subdivide(number_cuts=60); bpy.ops.object.mode_set(mode='OBJECT')
    for v in rug.data.vertices:
        x, y = v.co.x, v.co.y
        v.co.z = 0.18 * math.sin(x * 0.9 + 0.6) + 0.06 * math.sin(y * 2.3 + x * 0.4)
    so = rug.modifiers.new('s', 'SOLIDIFY'); so.thickness = 0.05
    rug.data.materials.append(mat('rug', rough=0.9, img=os.path.join(TEX, 'rug-riso.png')))
    bpy.ops.object.shade_smooth()
    # fringe
    random.seed(2); fm = mat('fringe', base=(0.95, 0.85, 0.75), rough=0.7)
    hw, hh = 3.6, 7.2 * 104 / 240 / 2
    for side in (-1, 1):
        for i in range(56):
            y = -hh + 0.1 + i * (2 * hh - 0.2) / 55
            ln = random.uniform(0.32, 0.46)
            x0 = side * (hw + ln / 2)
            z0 = 0.18 * math.sin(side * hw * 0.9 + 0.6)
            bpy.ops.mesh.primitive_cylinder_add(radius=0.012, depth=ln, location=(x0, y, z0 - 0.02), rotation=(0, math.radians(90 + side * random.uniform(-8, 8)), 0), vertices=6)
            bpy.context.object.data.materials.append(fm)
    rug.rotation_euler = (0, 0, math.radians(-6))
    bpy.ops.mesh.primitive_plane_add(size=60, location=(0, 0, -0.6))
    bpy.context.object.data.materials.append(mat('floor', base=(0.012, 0.012, 0.014), rough=0.6))
    camera((0, -7.4, 7.6), (0, 0.15, 0), lens=42)
    area('key', (-4, -3, 7), 6, 1500, (1, 0.95, 0.9))
    area('rim', (4, 5, 3), 4, 900, (1, 0.3, 0.55))

elif VAR == 'led':
    world((0.002, 0.002, 0.003))
    kn = json.load(open(os.path.join(TEX, 'knots.json')))
    cols, rows = kn['cols'], kn['rows']
    step = WIDTH / cols
    PAL = {0: (0.75, 0.03, 0.02), 1: (0.25, 0.01, 0.01), 2: (1.0, 0.38, 0.05), 3: (1.0, 0.1, 0.42), 4: (1.0, 0.9, 0.8)}
    bm = bmesh.new()
    lay = bm.loops.layers.color.new('knot') if hasattr(bm.loops.layers, 'color') else None
    random.seed(5)
    for r, c, ix in kn['knots']:
        x = (c - cols / 2) * step; y = -(r - rows / 2) * step
        h = step * (0.55 + 0.25 * random.random() + (0.35 if ix == 4 else 0))
        res = bmesh.ops.create_cube(bm, size=1)
        vs = res['verts']
        for v in vs:
            v.co.x = x + v.co.x * step * 0.8; v.co.y = y + v.co.y * step * 0.8; v.co.z = v.co.z * h + h / 2
        col = PAL[ix]
        for f in {f for v in vs for f in v.link_faces}:
            for l in f.loops:
                l[lay] = (*col, 1)
    me = bpy.data.meshes.new('knots'); bm.to_mesh(me)
    ob = bpy.data.objects.new('knots', me); sc.collection.objects.link(ob)
    bv = ob.modifiers.new('b', 'BEVEL'); bv.width = step * 0.18; bv.segments = 3
    ob.data.materials.append(mat('led', rough=0.25, coat=1.0, attr='knot', emit_strength=1.6))
    ob.rotation_euler = (math.radians(80), 0, math.radians(-6))
    bpy.ops.mesh.primitive_plane_add(size=60, location=(0, 0, -1.6))
    bpy.context.object.data.materials.append(mat('floor', base=(0.01, 0.01, 0.012), rough=0.35))
    camera((1.6, -12, 1.4), (0, 0, 0.6), lens=48, dof=2.2)
    area('key', (-3, -4, 6), 4, 250)
    area('rim', (4, 4, 4), 4, 900, (0.6, 0.6, 1.0))

sc.render.filepath = os.path.join(D, 'render', f'logo-{VAR}.png')
bpy.ops.render.render(write_still=True)
print('RENDERED', sc.render.filepath)
