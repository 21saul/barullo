"""Pulseras de tela de Barullo flotando (héroe de /entradas).

Tres cintas jacquard (band_tex.py) cerradas con un engarce de plata, con su
cola suelta, girando despacio en el aire entre brasas. Todos los giros y
balanceos usan frecuencias enteras del bucle: el fotograma LOOP es el 0.

blender -b --factory-startup --python bands.py -- <tex> <out> <view> <frames> [samples] [scale%]
Variables: CAM / TGT ("x,y,z"), LENS.
"""
import bpy, bmesh, math, os, sys
import numpy as np
from mathutils import Vector, Euler, Matrix

argv = sys.argv[sys.argv.index('--') + 1:]
TEX, OUT, VIEW, FR = argv[:4]
SAMPLES = int(argv[4]) if len(argv) > 4 else 64
SCALE = int(argv[5]) if len(argv) > 5 else 100
os.makedirs(OUT, exist_ok=True)
FPS, LOOP = 30, 300
TAU = 2 * math.pi
W0 = TAU / LOOP

# ---------------------------------------------------------------- escena
sc = bpy.context.scene
for o in list(bpy.data.objects):
    bpy.data.objects.remove(o)
sc.render.fps = FPS
for eng in ('BLENDER_EEVEE', 'BLENDER_EEVEE_NEXT'):
    try:
        sc.render.engine = eng; break
    except TypeError:
        pass
ee = sc.eevee
for attr, val in (('use_raytracing', True), ('taa_render_samples', SAMPLES), ('use_shadows', True),
                  ('shadow_ray_count', 2), ('shadow_step_count', 8), ('fast_gi_method', 'GLOBAL_ILLUMINATION')):
    if hasattr(ee, attr):
        try:
            setattr(ee, attr, val)
        except Exception:
            pass
if hasattr(ee, 'ray_tracing_options'):
    ee.ray_tracing_options.resolution_scale = '1'
if VIEW == 'narrow':
    sc.render.resolution_x, sc.render.resolution_y = 1080, 1920
else:
    sc.render.resolution_x, sc.render.resolution_y = 1920, 1080
sc.render.resolution_percentage = SCALE
for vt in ('Khronos PBR Neutral', 'AgX', 'Filmic'):
    try:
        sc.view_settings.view_transform = vt; break
    except TypeError:
        pass

# mundo: casi negro, con un degradado cálido que dé algo que reflejar al metal
w = bpy.data.worlds.new('w'); sc.world = w; w.use_nodes = True
wn = w.node_tree
bg = next(n for n in wn.nodes if n.type == 'BACKGROUND')
tc = wn.nodes.new('ShaderNodeTexCoord'); sep = wn.nodes.new('ShaderNodeSeparateXYZ')
ramp = wn.nodes.new('ShaderNodeValToRGB')
ramp.color_ramp.elements[0].position = 0.45; ramp.color_ramp.elements[0].color = (0.004, 0.003, 0.003, 1)
ramp.color_ramp.elements[1].position = 1.0; ramp.color_ramp.elements[1].color = (0.09, 0.03, 0.025, 1)
wn.links.new(tc.outputs['Generated'], sep.inputs[0]); wn.links.new(sep.outputs['Z'], ramp.inputs['Fac'])
wn.links.new(ramp.outputs['Color'], bg.inputs['Color']); bg.inputs[1].default_value = 1.0
# la cámara no ve el degradado del mundo: fondo negro limpio
try:
    w.visibility.camera = False
except Exception:
    pass

def img(name, colorspace='sRGB'):
    im = bpy.data.images.load(os.path.join(TEX, name))
    im.colorspace_settings.name = colorspace
    return im

NORMAL = img('band_normal.png', 'Non-Color'); ROUGH = img('band_rough.png', 'Non-Color')

def fabric(variant):
    m = bpy.data.materials.new(f'cinta_{variant}'); m.use_nodes = True
    nt = m.node_tree; p = next(n for n in nt.nodes if n.type == 'BSDF_PRINCIPLED')
    uv = nt.nodes.new('ShaderNodeTexCoord')
    ta = nt.nodes.new('ShaderNodeTexImage'); ta.image = img(f'band_{variant}.png'); ta.interpolation = 'Cubic'
    tn = nt.nodes.new('ShaderNodeTexImage'); tn.image = NORMAL
    tr = nt.nodes.new('ShaderNodeTexImage'); tr.image = ROUGH
    for t in (ta, tn, tr):
        t.extension = 'REPEAT'; nt.links.new(uv.outputs['UV'], t.inputs['Vector'])
    nm = nt.nodes.new('ShaderNodeNormalMap'); nm.inputs['Strength'].default_value = 0.9
    nt.links.new(tn.outputs['Color'], nm.inputs['Color'])
    nt.links.new(ta.outputs['Color'], p.inputs['Base Color'])
    nt.links.new(tr.outputs['Color'], p.inputs['Roughness'])
    nt.links.new(nm.outputs['Normal'], p.inputs['Normal'])
    for k, v in (('Sheen Weight', 0.0), ('Sheen Roughness', 0.5), ('Specular IOR Level', 0.15)):
        if k in p.inputs:
            p.inputs[k].default_value = v
    if 'Sheen Tint' in p.inputs:
        nt.links.new(ta.outputs['Color'], p.inputs['Sheen Tint'])
    return m

silver = bpy.data.materials.new('plata'); silver.use_nodes = True
sp = next(n for n in silver.node_tree.nodes if n.type == 'BSDF_PRINCIPLED')
sp.inputs['Base Color'].default_value = (0.92, 0.92, 0.95, 1)
sp.inputs['Metallic'].default_value = 1.0; sp.inputs['Roughness'].default_value = 0.18

# ---------------------------------------------------------------- pulsera
CIRC = 0.205                 # largo del lazo (m)
BW = CIRC * 288 / 4096       # ancho de la cinta según la textura (~14 mm)
TH = 0.0009
TAIL = 0.05

def ribbon(name, pts, side, u0, u1, mat):
    """Malla de cinta: `pts` (n,3) eje, `side` (n,3) dirección del ancho."""
    n = len(pts)
    me = bpy.data.meshes.new(name)
    v = np.concatenate([pts - side * BW / 2, pts + side * BW / 2])
    faces = [(i, i + 1, n + i + 1, n + i) for i in range(n - 1)]
    me.from_pydata([tuple(p) for p in v], [], faces)
    me.polygons.foreach_set('use_smooth', [True] * len(me.polygons))
    uvl = me.uv_layers.new(name='UV')
    u = np.linspace(u0, u1, n)
    uv = []
    for poly in me.polygons:
        for li in poly.loop_indices:
            vi = me.loops[li].vertex_index
            uv.extend((u[vi % n], 0.0 if vi < n else 1.0))
    uvl.data.foreach_set('uv', uv)
    ob = bpy.data.objects.new(name, me); sc.collection.objects.link(ob)
    ob.data.materials.append(mat)
    so = ob.modifiers.new('grosor', 'SOLIDIFY'); so.thickness = TH; so.offset = 0
    sub = ob.modifiers.new('sub', 'SUBSURF'); sub.levels = sub.render_levels = 1
    return ob

def bracelet(name, variant, seed):
    rs = np.random.default_rng(seed)
    root = bpy.data.objects.new(name, None); sc.collection.objects.link(root)
    mat = fabric(variant)
    # lazo: elipse algo irregular en el plano XY, el ancho en Z
    R = CIRC / TAU
    t = np.linspace(0, TAU, 241)
    rr = R * (1 + 0.06 * np.cos(2 * t + rs.uniform(0, TAU)) + 0.02 * np.cos(3 * t + rs.uniform(0, TAU)))
    pts = np.column_stack([rr * np.cos(t), rr * np.sin(t), 0.0015 * np.sin(2 * t)])
    side = np.tile([0, 0, 1.0], (len(t), 1))
    # una leve torsión: la cinta no queda perfectamente cilíndrica
    tw = 0.12 * np.sin(t)
    rad = np.column_stack([np.cos(t), np.sin(t), np.zeros_like(t)])
    side = side * np.cos(tw)[:, None] + rad * np.sin(tw)[:, None]
    lo = ribbon(name + '_lazo', pts, side, 0.0, CIRC / CIRC, mat); lo.parent = root
    # cola: sale del engarce por fuera, con una curva suave hacia afuera
    s = np.linspace(0, TAIL, 40)
    curl = 0.9 * (s / TAIL) ** 1.6
    x = R + 0.0022 + np.sin(curl) * s * 0.35
    y = s * np.cos(curl * 0.5) - 0.006
    tp = np.column_stack([x, y, np.zeros_like(s)])
    ts = np.tile([0, 0, 1.0], (len(s), 1))
    ta = ribbon(name + '_cola', tp, ts, 0.13, 0.13 + TAIL / CIRC, mat); ta.parent = root
    # engarce de plata, con biselado
    bm = bmesh.new(); bmesh.ops.create_cube(bm, size=1.0)
    mc = bpy.data.meshes.new(name + '_engarce'); bm.to_mesh(mc); bm.free()
    cr = bpy.data.objects.new(name + '_engarce', mc); sc.collection.objects.link(cr)
    cr.scale = (0.006, 0.011, BW + 0.004); cr.location = (R + 0.0012, 0.0, 0.0); cr.parent = root
    bv = cr.modifiers.new('bisel', 'BEVEL'); bv.width = 0.0016; bv.segments = 4; bv.limit_method = 'NONE'
    bv.affect = 'EDGES'
    cr.data.materials.append(silver)
    cr.data.polygons.foreach_set('use_smooth', [True] * len(cr.data.polygons))
    return root

# ---------------------------------------------------------------- brasas
NEMB = 45
rs = np.random.default_rng(11)
EB = np.column_stack([rs.uniform(-0.12, 0.5, NEMB), rs.uniform(-0.1, 0.6, NEMB), rs.uniform(-0.12, 0.35, NEMB)])
EA = rs.uniform(0.004, 0.03, (NEMB, 3)); EK = rs.integers(1, 3, (NEMB, 3)); EP = rs.uniform(0, TAU, (NEMB, 3))
ER = rs.uniform(0.0004, 0.0011, NEMB)
eb_ = bmesh.new(); bmesh.ops.create_icosphere(eb_, subdivisions=3, radius=1.0)
ev = np.array([v.co[:] for v in eb_.verts]); ef = [[v.index for v in f.verts] for f in eb_.faces]; eb_.free()
EV = len(ev); groups = []
for gi, col in enumerate(((1.0, 0.42, 0.12), (1.0, 0.18, 0.35), (1.0, 0.85, 0.6))):
    idx = np.arange(NEMB)[np.arange(NEMB) % 3 == gi]
    m_ = bpy.data.meshes.new(f'emb{gi}')
    m_.from_pydata([(0, 0, 0)] * (EV * len(idx)), [], [[i + n * EV for i in f] for n in range(len(idx)) for f in ef])
    o_ = bpy.data.objects.new(f'emb{gi}', m_); sc.collection.objects.link(o_)
    mt = bpy.data.materials.new(f'emb{gi}'); mt.use_nodes = True
    pn = next(n for n in mt.node_tree.nodes if n.type == 'BSDF_PRINCIPLED')
    pn.inputs['Base Color'].default_value = (*col, 1)
    pn.inputs['Emission Color'].default_value = (*col, 1); pn.inputs['Emission Strength'].default_value = 3.0
    m_.materials.append(mt); groups.append((m_, idx))

def set_embers(f):
    t = f * W0
    P = EB + EA * np.sin(EK * t + EP)
    for m_, idx in groups:
        co = ev[None] * ER[idx, None, None] + P[idx, None]
        m_.vertices.foreach_set('co', co.reshape(-1)); m_.update()

# ---------------------------------------------------------------- composición
# La roja va delante, nítida y con el «barullo» de cara: el aro con el eje
# vertical enseña su cara exterior a la cámara y el engarce queda detrás
# (giro z de 90°). Sólo se balancea, no da la vuelta, para que el logo se lea
# siempre. Las otras dos, detrás y desenfocadas, sí giran.
# (nombre, variante, posición, giro base en grados)
if VIEW == 'narrow':
    LAYOUT = [('b1', 'roja', (0.0, -0.1, 0.035), (28, 0, 90)),
              ('b2', 'negra', (0.06, 0.2, 0.1), (25, 60, -30)),
              ('b3', 'hueso', (0.05, 0.4, -0.07), (-40, -20, 60))]
else:
    LAYOUT = [('b1', 'roja', (0.035, -0.12, 0.02), (28, 0, 90)),
              ('b2', 'negra', (0.16, 0.22, 0.08), (25, 60, -30)),
              ('b3', 'hueso', (0.22, 0.45, -0.04), (-40, -20, 60))]
BR = []
for k, (nm_, var, pos, rot) in enumerate(LAYOUT):
    BR.append((bracelet(nm_, var, 5 + k), Vector(pos), Vector([math.radians(a) for a in rot]), k))
HERO_POS = Vector(LAYOUT[0][2])

def pose(f):
    t = f * W0
    for ob, pos, rot, k in BR:
        ph = 1.7 * k
        if k == 0:
            # balanceo suave: el logo nunca se va de cara
            ob.rotation_euler = Euler((rot.x + 0.12 * math.sin(t), rot.y + 0.08 * math.sin(2 * t + 0.4),
                                       rot.z + 0.38 * math.sin(t + 0.9)))
        else:
            spin = (1 if k % 2 == 0 else -1) * t
            ob.rotation_euler = Euler((rot.x + 0.35 * math.sin(t + ph), rot.y + 0.25 * math.sin(2 * t + ph), rot.z + spin))
        ob.location = pos + Vector((0.004 * math.sin(t + ph), 0.003 * math.cos(2 * t + ph), 0.006 * math.sin(t + ph + 0.6)))

# ---------------------------------------------------------------- luces y cámara
def area(name, loc, size, energy, color=(1, 1, 1), target=(0.06, 0.06, 0.02)):
    l = bpy.data.lights.new(name, 'AREA'); l.energy = energy; l.color = color; l.size = size
    o = bpy.data.objects.new(name, l); sc.collection.objects.link(o); o.location = loc
    d = Vector(target) - Vector(loc); o.rotation_euler = d.to_track_quat('-Z', 'Y').to_euler()
area('key', (-0.4, -0.6, 0.45), 1.0, 20, (1.0, 0.93, 0.86))
area('fill', (0.45, -0.5, 0.0), 0.8, 10, (1.0, 0.6, 0.5))
area('rimPink', (0.5, 0.5, 0.15), 0.4, 7, (1.0, 0.25, 0.55))
area('rimOrange', (-0.45, 0.45, -0.05), 0.35, 5, (1.0, 0.5, 0.15))
area('strip', (0.3, -0.35, 0.35), 0.06, 6, (1.0, 1.0, 1.0))   # brillo largo en la plata

cam_d = bpy.data.cameras.new('cam')
cam = bpy.data.objects.new('cam', cam_d); sc.collection.objects.link(cam); sc.camera = cam
if VIEW == 'narrow':
    loc, tgt, lens = Vector((0.0, -0.52, 0.12)), Vector((0.0, 0.05, 0.02)), 62
else:
    loc, tgt, lens = Vector((-0.12, -0.55, 0.1)), Vector((-0.02, 0.06, 0.01)), 56
vec = lambda k: Vector(tuple(map(float, os.environ[k].split(','))))
if 'CAM' in os.environ: loc = vec('CAM')
if 'TGT' in os.environ: tgt = vec('TGT')
if 'LENS' in os.environ: lens = float(os.environ['LENS'])
cam.location = loc; cam_d.lens = lens; cam_d.clip_start = 0.01
cam.rotation_euler = (tgt - loc).to_track_quat('-Z', 'Y').to_euler()
cam_d.dof.use_dof = True; cam_d.dof.focus_distance = (HERO_POS + Vector((0, -0.032, 0)) - loc).length   # la cara del aro
cam_d.dof.aperture_fstop = 9.0

# ---------------------------------------------------------------- fotogramas
if '-' in FR:
    rng_, _, step = FR.partition(':')
    a, b = map(int, rng_.split('-'))
    frames = list(range(a, b + 1, int(step or 1)))
else:
    frames = [int(FR)]
for f in frames:
    pose(f); set_embers(f)
    sc.frame_set(f)
    sc.render.filepath = os.path.join(OUT, f'{VIEW}_{f:04d}.png')
    if os.environ.get('SKIP') and os.path.exists(sc.render.filepath):
        continue   # reanudar: lo ya renderizado no se repite
    if os.environ.get('DRY'):
        print('DRY', f, flush=True); continue
    bpy.ops.render.render(write_still=True)
    print('FRAME', f, flush=True)
