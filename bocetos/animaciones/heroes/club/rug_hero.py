"""Barullo flying carpet: woven-logo rug with inextensible travelling waves and simulated fringes.

blender -b --factory-startup --python rug_fly.py -- <tex_dir> <out_dir> <view> <frames> [engine] [samples] [scale%]
  view    wide | square
  frames  "poster" | "12" | "0-179" | "0-179:2" (step)
  engine  eevee | cycles
Frames are written as <out_dir>/<view>_####.png. The loop is LOOP frames long and periodic.
"""
import bpy, bmesh, math, os, sys
import numpy as np
from mathutils import Vector

argv = sys.argv[sys.argv.index('--') + 1:]
TEX, OUT, VIEW, FR = argv[:4]
ENGINE = argv[4] if len(argv) > 4 else 'eevee'
SAMPLES = int(argv[5]) if len(argv) > 5 else 64
SCALE = int(argv[6]) if len(argv) > 6 else 100
os.makedirs(OUT, exist_ok=True)

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, '..', '..', 'alfombra', 'rug'))
from rug_motion import *  # noqa: F401,F403  (LOOP, FPS, rug_points, simulate, NB, PER, NS, KNOT, ...)

# ---------------------------------------------------------------- scene
sc = bpy.context.scene
for o in list(bpy.data.objects):
    bpy.data.objects.remove(o)
sc.render.fps = FPS
if ENGINE == 'cycles':
    sc.render.engine = 'CYCLES'; sc.cycles.samples = SAMPLES; sc.cycles.use_denoising = True
    sc.cycles.device = 'CPU'
    sc.cycles.max_bounces = 6
else:
    for eng in ('BLENDER_EEVEE', 'BLENDER_EEVEE_NEXT'):
        try:
            sc.render.engine = eng; break
        except TypeError:
            pass
    ee = sc.eevee
    for attr, val in (('use_raytracing', True), ('taa_render_samples', SAMPLES), ('use_shadows', True),
                      ('shadow_ray_count', 2), ('shadow_step_count', 8), ('use_volumetric_shadows', True),
                      ('fast_gi_method', 'GLOBAL_ILLUMINATION')):
        if hasattr(ee, attr):
            try:
                setattr(ee, attr, val)
            except Exception:
                pass
    if hasattr(ee, 'ray_tracing_options'):
        ee.ray_tracing_options.resolution_scale = '1'
if VIEW == 'square':
    sc.render.resolution_x = sc.render.resolution_y = 1080
elif VIEW == 'narrow':                       # hero móvil, 9:16
    sc.render.resolution_x, sc.render.resolution_y = 1080, 1920
else:
    sc.render.resolution_x, sc.render.resolution_y = 1920, 1080
sc.render.resolution_percentage = SCALE
for vt in ('Khronos PBR Neutral', 'AgX', 'Filmic'):
    try:
        sc.view_settings.view_transform = vt; break
    except TypeError:
        pass
print('view transform', sc.view_settings.view_transform)

w = bpy.data.worlds.new('w'); sc.world = w; w.use_nodes = True
bg = next(n for n in w.node_tree.nodes if n.type == 'BACKGROUND')
bg.inputs[0].default_value = (0.006, 0.0045, 0.005, 1); bg.inputs[1].default_value = 1.0

def img(name, colorspace='sRGB'):
    im = bpy.data.images.load(os.path.join(TEX, name))
    im.colorspace_settings.name = colorspace
    return im

def wool_material():
    m = bpy.data.materials.new('wool'); m.use_nodes = True
    nt = m.node_tree
    p = next(n for n in nt.nodes if n.type == 'BSDF_PRINCIPLED')
    uv = nt.nodes.new('ShaderNodeTexCoord')
    ta = nt.nodes.new('ShaderNodeTexImage'); ta.image = img('albedo.png'); ta.interpolation = 'Cubic'
    tn = nt.nodes.new('ShaderNodeTexImage'); tn.image = img('normal.png', 'Non-Color')
    tr = nt.nodes.new('ShaderNodeTexImage'); tr.image = img('rough.png', 'Non-Color')
    for t in (ta, tn, tr):
        nt.links.new(uv.outputs['UV'], t.inputs['Vector'])
    nm = nt.nodes.new('ShaderNodeNormalMap'); nm.inputs['Strength'].default_value = 1.2
    nt.links.new(tn.outputs['Color'], nm.inputs['Color'])
    # underside: the back of the knots, flatter and duller than the pile
    geo = nt.nodes.new('ShaderNodeNewGeometry')
    back = nt.nodes.new('ShaderNodeMix'); back.data_type = 'RGBA'; back.blend_type = 'MULTIPLY'
    back.inputs['B'].default_value = (0.62, 0.58, 0.56, 1)
    nt.links.new(geo.outputs['Backfacing'], back.inputs['Factor'])
    nt.links.new(ta.outputs['Color'], back.inputs['A'])
    nt.links.new(back.outputs['Result'], p.inputs['Base Color'])
    nt.links.new(tr.outputs['Color'], p.inputs['Roughness'])
    nt.links.new(nm.outputs['Normal'], p.inputs['Normal'])
    for k, v in (('Sheen Weight', 0.5), ('Sheen Roughness', 0.45), ('Specular IOR Level', 0.12),
                 ('Subsurface Weight', 0.08), ('Subsurface Scale', 0.01)):
        if k in p.inputs:
            p.inputs[k].default_value = v
    if 'Sheen Tint' in p.inputs:
        nt.links.new(ta.outputs['Color'], p.inputs['Sheen Tint'])
    if 'Subsurface Radius' in p.inputs:
        p.inputs['Subsurface Radius'].default_value = (1.0, 0.3, 0.2)
    return m

def plain(name, col, rough=0.8, sheen=0.6):
    m = bpy.data.materials.new(name); m.use_nodes = True
    p = next(n for n in m.node_tree.nodes if n.type == 'BSDF_PRINCIPLED')
    p.inputs['Base Color'].default_value = (*col, 1); p.inputs['Roughness'].default_value = rough
    if 'Sheen Weight' in p.inputs:
        p.inputs['Sheen Weight'].default_value = sheen
    return m

# rug mesh
me = bpy.data.meshes.new('rug')
verts = [(0, 0, 0)] * ((NX + 1) * (NY + 1))
faces = [(j * (NX + 1) + i, j * (NX + 1) + i + 1, (j + 1) * (NX + 1) + i + 1, (j + 1) * (NX + 1) + i)
         for j in range(NY) for i in range(NX)]
me.from_pydata(verts, [], faces)
uvl = me.uv_layers.new(name='UV')
uvs = []
for poly in me.polygons:
    for li in poly.loop_indices:
        vi = me.loops[li].vertex_index
        i, j = vi % (NX + 1), vi // (NX + 1)
        uvs.extend((i / NX, j / NY))
uvl.data.foreach_set('uv', uvs)
me.polygons.foreach_set('use_smooth', [True] * len(me.polygons))
rug = bpy.data.objects.new('rug', me); sc.collection.objects.link(rug)
rug.data.materials.append(wool_material())
rug.data.materials.append(plain('binding', (0.12, 0.012, 0.008), 0.75, 0.8))
so = rug.modifiers.new('thick', 'SOLIDIFY'); so.thickness = 0.014; so.offset = -1
so.material_offset_rim = 1; so.use_even_offset = True
sub = rug.modifiers.new('sub', 'SUBSURF'); sub.levels = sub.render_levels = 1

def set_rug(P):
    # image row 0 is the top of the texture -> v = +WD/2 maps to uv 1
    me.vertices.foreach_set('co', P.reshape(-1))
    me.update()

# wool fuzz: short fibres scattered over the pile, coloured from the rug's UVs
def fuzz_object(density):
    ng = bpy.data.node_groups.new('fuzz', 'GeometryNodeTree')
    ng.interface.new_socket('Geometry', in_out='INPUT', socket_type='NodeSocketGeometry')
    ng.interface.new_socket('Geometry', in_out='OUTPUT', socket_type='NodeSocketGeometry')
    N = ng.nodes; Lk = ng.links.new
    gin = N.new('NodeGroupInput'); gout = N.new('NodeGroupOutput')
    oi = N.new('GeometryNodeObjectInfo'); oi.inputs['Object'].default_value = rug
    oi.transform_space = 'RELATIVE'
    dist = N.new('GeometryNodeDistributePointsOnFaces'); dist.inputs['Density'].default_value = density
    dist.inputs['Seed'].default_value = 3
    line = N.new('GeometryNodeCurvePrimitiveLine'); line.inputs['End'].default_value = (0, 0, 1)
    rnd = N.new('FunctionNodeRandomValue'); rnd.data_type = 'FLOAT'
    rnd.inputs['Min'].default_value = 0.0025; rnd.inputs['Max'].default_value = 0.0065
    tilt = N.new('FunctionNodeRandomValue'); tilt.data_type = 'FLOAT_VECTOR'
    tilt.inputs[0].default_value = (-0.6, -0.6, -3.14); tilt.inputs[1].default_value = (0.6, 0.6, 3.14)
    inst = N.new('GeometryNodeInstanceOnPoints')
    rot = N.new('GeometryNodeRotateInstances'); rot.inputs['Local Space'].default_value = True
    real = N.new('GeometryNodeRealizeInstances')
    rad = N.new('GeometryNodeSetCurveRadius'); rad.inputs['Radius'].default_value = float(os.environ.get('RUG_FUZZR', '0.0011'))
    smat = N.new('GeometryNodeSetMaterial')
    Lk(oi.outputs['Geometry'], dist.inputs['Mesh'])         # the 'UV' attribute rides along to each fibre
    Lk(dist.outputs['Points'], inst.inputs['Points'])
    Lk(line.outputs['Curve'], inst.inputs['Instance'])
    Lk(dist.outputs['Rotation'], inst.inputs['Rotation'])
    Lk(rnd.outputs[0], inst.inputs['Scale'])
    Lk(inst.outputs['Instances'], rot.inputs['Instances'])
    Lk(tilt.outputs[0], rot.inputs['Rotation'])
    Lk(rot.outputs['Instances'], real.inputs[0])
    Lk(real.outputs[0], rad.inputs['Curve'])
    Lk(rad.outputs['Curve'], smat.inputs['Geometry'])
    Lk(smat.outputs['Geometry'], gout.inputs[0])
    m = bpy.data.materials.new('fuzz'); m.use_nodes = True
    nt = m.node_tree; pb = next(n for n in nt.nodes if n.type == 'BSDF_PRINCIPLED')
    at = nt.nodes.new('ShaderNodeAttribute'); at.attribute_name = 'UV'
    tx = nt.nodes.new('ShaderNodeTexImage'); tx.image = bpy.data.images['albedo.png']
    nt.links.new(at.outputs['Vector'], tx.inputs['Vector'])
    br = nt.nodes.new('ShaderNodeHueSaturation'); br.inputs['Value'].default_value = 0.95
    nt.links.new(tx.outputs['Color'], br.inputs['Color']); nt.links.new(br.outputs['Color'], pb.inputs['Base Color'])
    pb.inputs['Roughness'].default_value = 0.9
    for k, v in (('Sheen Weight', 0.25), ('Specular IOR Level', 0.04)):
        if k in pb.inputs:
            pb.inputs[k].default_value = v
    if os.environ.get('RUG_FUZZDBG'):
        rgb = nt.nodes.new('ShaderNodeRGB'); rgb.outputs[0].default_value = (0, 1, 0, 1)
        nt.links.new(rgb.outputs[0], pb.inputs['Base Color'])
    smat.inputs['Material'].default_value = m
    hc = bpy.data.hair_curves.new('fuzz'); hc.materials.append(m)
    ob = bpy.data.objects.new('fuzz', hc); sc.collection.objects.link(ob)
    md = ob.modifiers.new('fuzz', 'NODES'); md.node_group = ng
    return ob

FUZZ = float(os.environ.get('RUG_FUZZ', '40000'))
fz = fuzz_object(FUZZ) if FUZZ > 0 else None

# fringes: one curve, a spline per thread
cu = bpy.data.curves.new('fringe', 'CURVE'); cu.dimensions = '3D'
cu.bevel_depth = 0.0042; cu.bevel_resolution = 2; cu.use_fill_caps = True
RES = 30
for end in (0, 1):
    for i in range(NS):
        sp = cu.splines.new('POLY'); sp.points.add(RES - 1)
fr = bpy.data.objects.new('fringe', cu); sc.collection.objects.link(fr)
fr.data.materials.append(plain('cotton', (0.82, 0.76, 0.66), 0.7, 1.0))

# knots: little ellipsoids where each bundle is tied
tb = bmesh.new()
bmesh.ops.create_uvsphere(tb, u_segments=10, v_segments=7, radius=0.0115)
tv = np.array([v.co[:] for v in tb.verts]) * np.array([1.25, 1.0, 0.9])
tf = [[v.index for v in f.verts] for f in tb.faces]
tb.free()
KV = len(tv)
kme = bpy.data.meshes.new('knots')
kme.from_pydata([tuple(p) for p in np.tile(tv, (2 * NB, 1))], [],
                [[i + n * KV for i in f] for n in range(2 * NB) for f in tf])
kme.polygons.foreach_set('use_smooth', [True] * len(kme.polygons))
kn = bpy.data.objects.new('knots', kme); sc.collection.objects.link(kn)
kn.data.materials.append(fr.data.materials[0])
kbase = np.tile(tv, (2 * NB, 1)).reshape(2 * NB, KV, 3)

def catmull(p, n):
    """Resample a polyline (SEG+1, 3) to n points with Catmull-Rom."""
    m = len(p) - 1
    tt = np.linspace(0, m, n)
    i = np.clip(tt.astype(int), 0, m - 1); u = (tt - i)[:, None]
    P0 = p[np.clip(i - 1, 0, m)]; P1 = p[i]; P2 = p[i + 1]; P3 = p[np.clip(i + 2, 0, m)]
    return 0.5 * ((2 * P1) + (-P0 + P2) * u + (2 * P0 - 5 * P1 + 4 * P2 - P3) * u ** 2 + (-P0 + 3 * P1 - 3 * P2 + P3) * u ** 3)

def set_fringe(F):
    k = 0
    for end in (0, 1):
        for i in range(NS):
            q = catmull(F[end, i], RES)
            co = np.hstack([q, np.ones((RES, 1))])
            cu.splines[k].points.foreach_set('co', co.reshape(-1)); k += 1
            # taper towards the tips
        kc = F[end][:, KNOT].reshape(NB, PER, 3).mean(1)
        kbase_e = kbase[end * NB:(end + 1) * NB]
        if end == 0:
            allk = [kbase_e + kc[:, None]]
        else:
            allk.append(kbase_e + kc[:, None])
    kme.vertices.foreach_set('co', np.concatenate(allk).reshape(-1)); kme.update()

# taper radius along each thread
for sp in cu.splines:
    for n, pt in enumerate(sp.points):
        pt.radius = 1.0 - 0.45 * (n / (RES - 1)) ** 2

# ---------------------------------------------------------------- lights + camera
def area(name, loc, size, energy, color=(1, 1, 1), target=(0, 0, 0), shape='RECTANGLE', size_y=None):
    l = bpy.data.lights.new(name, 'AREA'); l.energy = energy; l.color = color
    l.shape = shape; l.size = size; l.size_y = size_y or size
    o = bpy.data.objects.new(name, l); sc.collection.objects.link(o); o.location = loc
    d = Vector(target) - Vector(loc); o.rotation_euler = d.to_track_quat('-Z', 'Y').to_euler()
    return o

area('key', (-2.5, -3.5, 5.5), 4.0, 650, (1.0, 0.94, 0.88), size_y=2.0)
area('rimPink', (3.5, 4.0, 1.6), 3.0, 600, (1.0, 0.25, 0.55))
area('rimOrange', (-4.5, 3.0, 1.0), 2.5, 420, (1.0, 0.5, 0.15))
area('under', (0.5, -1.0, -3.0), 4.0, 120, (1.0, 0.35, 0.25), target=(0, 0, 0))

# soft dark backdrop with a warm glow behind the rug
bpy.ops.mesh.primitive_plane_add(size=1, location=(0, 9, -1))
bd = bpy.context.object; bd.scale = (40, 24, 1); bd.rotation_euler = (math.radians(90), 0, 0)
bm_ = bpy.data.materials.new('backdrop'); bm_.use_nodes = True
nt = bm_.node_tree
[nt.nodes.remove(n) for n in list(nt.nodes)]
tc = nt.nodes.new('ShaderNodeTexCoord'); gr = nt.nodes.new('ShaderNodeTexGradient'); gr.gradient_type = 'SPHERICAL'
mp = nt.nodes.new('ShaderNodeMapping'); mp.inputs['Scale'].default_value = (2.2, 3.6, 1)
cr_ = nt.nodes.new('ShaderNodeValToRGB')
cr_.color_ramp.elements[0].color = (0.004, 0.003, 0.004, 1)
cr_.color_ramp.elements[1].color = (0.025, 0.005, 0.005, 1); cr_.color_ramp.elements[1].position = 0.95
em = nt.nodes.new('ShaderNodeEmission'); out = nt.nodes.new('ShaderNodeOutputMaterial')
nt.links.new(tc.outputs['Object'], mp.inputs['Vector']); nt.links.new(mp.outputs['Vector'], gr.inputs['Vector'])
nt.links.new(gr.outputs['Fac'], cr_.inputs['Fac']); nt.links.new(cr_.outputs['Color'], em.inputs['Color'])
nt.links.new(em.outputs['Emission'], out.inputs['Surface'])
bd.data.materials.append(bm_)

cam_d = bpy.data.cameras.new('cam')
cam = bpy.data.objects.new('cam', cam_d); sc.collection.objects.link(cam); sc.camera = cam
if VIEW == 'square':
    loc, tgt, lens = Vector((-2.2, -4.6, 4.3)), Vector((0.05, 0.05, -0.1)), 43
else:
    loc, tgt, lens = Vector((-1.5, -6.2, 2.75)), Vector((0.15, 0.1, -0.2)), 46
if os.environ.get('RUGCAM') == 'close':
    loc, tgt, lens = Vector((-1.2, -1.6, 0.75)), Vector((-0.75, -0.2, 0.0)), 60
# Héroe: la alfombra deja sitio al título (abajo a la izquierda en escritorio,
# abajo en móvil). Se puede afinar sin tocar el código con CAM/TGT/LENS/YAW.
if VIEW == 'wide':
    loc, tgt, lens = Vector((-0.6, -7.4, 2.4)), Vector((-1.2, 0.0, -0.65)), 37
if VIEW == 'narrow':
    loc, tgt, lens = Vector((-0.3, -4.6, 3.0)), Vector((-0.08, 0.3, -1.2)), 18.5
vec = lambda k: Vector(tuple(map(float, os.environ[k].split(','))))
if 'CAM' in os.environ: loc = vec('CAM')
if 'TGT' in os.environ: tgt = vec('TGT')
if 'LENS' in os.environ: lens = float(os.environ['LENS'])
cam.location = loc; cam_d.lens = lens
cam.rotation_euler = (tgt - loc).to_track_quat('-Z', 'Y').to_euler()
cam_d.dof.use_dof = True; cam_d.dof.focus_distance = (tgt - loc).length; cam_d.dof.aperture_fstop = 3.2   # brasas lejanas y cercanas en bokeh suave
# carpet sits at an angle to the camera for depth
for o in filter(None, (rug, fr, kn, fz)):
    o.rotation_euler = (0, 0, math.radians(float(os.environ.get('YAW', {'wide': -18, 'narrow': -12}.get(VIEW, -36)))))

# ---------------------------------------------------------------- brasas
# Motas que flotan alrededor de la alfombra. Cada una sigue una órbita con
# frecuencias enteras del bucle, así que el fotograma LOOP es igual al 0.
NEMB = int(os.environ.get('EMBERS', '75'))
rs = np.random.default_rng(7)
EB = np.column_stack([rs.uniform(-4.5, 3.5, NEMB), rs.uniform(-4.5, 4.0, NEMB), rs.uniform(-1.6, 1.8, NEMB)])
EA = rs.uniform(0.05, 0.35, (NEMB, 3)); EK = rs.integers(1, 3, (NEMB, 3)); EP = rs.uniform(0, TAU, (NEMB, 3))
ER = rs.uniform(0.003, 0.016, NEMB) * rs.choice([1, 1, 1, 2.2], NEMB)
eb_ = bmesh.new(); bmesh.ops.create_icosphere(eb_, subdivisions=3, radius=1.0)   # redondas: con 1 salen hexágonos
ev = np.array([v.co[:] for v in eb_.verts]); ef = [[v.index for v in f.verts] for f in eb_.faces]; eb_.free()
EV = len(ev)
groups = []
for gi, col in enumerate(((1.0, 0.42, 0.12), (1.0, 0.18, 0.35), (1.0, 0.85, 0.6))):
    idx = np.arange(NEMB)[np.arange(NEMB) % 3 == gi]
    m_ = bpy.data.meshes.new(f'emb{gi}')
    m_.from_pydata([(0, 0, 0)] * (EV * len(idx)), [], [[i + n * EV for i in f] for n in range(len(idx)) for f in ef])
    o_ = bpy.data.objects.new(f'emb{gi}', m_); sc.collection.objects.link(o_)
    mt = bpy.data.materials.new(f'emb{gi}'); mt.use_nodes = True
    pn = next(n for n in mt.node_tree.nodes if n.type == 'BSDF_PRINCIPLED')
    pn.inputs['Base Color'].default_value = (*col, 1)
    pn.inputs['Emission Color'].default_value = (*col, 1); pn.inputs['Emission Strength'].default_value = 4.0
    m_.materials.append(mt)
    groups.append((m_, idx))

def set_embers(f):
    t = f * W0
    P = EB + EA * np.sin(EK * t + EP)
    P[:, 2] += 0.12 * np.sin(t + EP[:, 0])
    for m_, idx in groups:
        co = ev[None] * ER[idx, None, None] + P[idx, None]
        m_.vertices.foreach_set('co', co.reshape(-1)); m_.update()

# ---------------------------------------------------------------- frames
if FR == 'poster':
    frames = [LOOP // 4]
elif '-' in FR:
    rng_, _, step = FR.partition(':')
    a, b = map(int, rng_.split('-'))
    frames = list(range(a, b + 1, int(step or 1)))
else:
    frames = [int(FR)]

for nm in filter(None, os.environ.get('RUGHIDE', '').split(',')):
    sc.objects[nm].hide_render = True
cache = os.path.join(OUT, 'fringe_cache.npy')
if os.path.exists(cache):
    FRINGE = np.load(cache)
else:
    FRINGE = simulate(); np.save(cache, FRINGE)

for f in frames:
    sc.frame_set(f)
    set_rug(rug_points(f))
    set_fringe(FRINGE[f % LOOP])
    if NEMB: set_embers(f)
    if os.environ.get('RUGDBG'):
        for k, sp in enumerate(cu.splines):
            c = np.zeros(len(sp.points) * 4); sp.points.foreach_get('co', c); c = c.reshape(-1, 4)
            jump = np.linalg.norm(np.diff(c[:, :3], axis=0), axis=1).max()
            if jump > 0.05 or abs(c[:, 3] - 1).max() > 1e-3:
                print('BADSPLINE', k, jump, c[:3])
        kc = np.zeros(len(kme.vertices) * 3); kme.vertices.foreach_get('co', kc)
        print('KNOTS bbox', kc.reshape(-1, 3).min(0), kc.reshape(-1, 3).max(0))
        if fz:
            ev = fz.evaluated_get(bpy.context.evaluated_depsgraph_get())
            gs = ev.evaluated_geometry(); c = gs.curves
            print('FUZZ', len(c.points) if c else None, len(c.curves) if c else None, [a.name for a in c.attributes] if c else None, gs.mesh and len(gs.mesh.vertices), fz.hide_render, c and [m.name for m in c.materials])
        continue
    sc.render.filepath = os.path.join(OUT, f'{VIEW}_{f:04d}.png')
    if os.environ.get('SKIP') and os.path.exists(sc.render.filepath):
        continue   # reanudar: lo ya renderizado no se repite
    if os.environ.get('DRY'):
        print('DRY', f, flush=True); continue
    bpy.ops.render.render(write_still=True)
    print('FRAME', f, flush=True)
