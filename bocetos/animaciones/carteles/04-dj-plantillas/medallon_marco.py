"""DJ · plantilla A «medallón»: la medalla «o» de frente, SIN gema, con el hueco central abierto
(transparente) para meter dentro la foto del/de la DJ en Remotion.

Mismos materiales y estilos que bocetos/disenos/logo/estilos (comun/medalla_lib.py). Renderiza N variantes de luz
(la luz principal da una vuelta alrededor de la cara: variante i = i/N de vuelta). En Remotion se funden
en bucle, así el brillo del oro se mueve sin tener que renderizar 240 frames (Cycles CPU, unos minutos).

Escribe l_<i>.png (RGBA) y marco.json con el polígono del hueco y las 8 puntas en coordenadas 0..1 de la imagen.

  blender.exe -b --factory-startup --python medallon_marco.py -- <logo-alfombra dir> <estilo> <out dir> [N=4] [samples=48] [res=2048]
"""
import bpy, json, math, os, sys
from mathutils import Vector
from bpy_extras.object_utils import world_to_camera_view

_A = sys.argv[sys.argv.index('--') + 1:]
D, STYLE, OUTD = _A[0], _A[1], _A[2]
N = int(_A[3]) if len(_A) > 3 else 4
HOLE = float(os.environ.get('HOLE', '1.3'))  # escala del hueco (1 = el de la medalla original): ventana más grande para la foto
SAMPLES = int(_A[4]) if len(_A) > 4 else 48
RES = int(_A[5]) if len(_A) > 5 else 2048
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, '..', 'comun'))
from medalla_lib import Medal, estilo, EXTRUDE  # noqa: E402

sc = bpy.context.scene
for o in list(bpy.data.objects):
    bpy.data.objects.remove(o)
sc.render.engine = 'CYCLES'; sc.cycles.samples = SAMPLES; sc.cycles.use_denoising = True; sc.cycles.device = 'CPU'
sc.cycles.use_adaptive_sampling = True; sc.cycles.adaptive_threshold = 0.02
sc.cycles.max_bounces = 6; sc.cycles.glossy_bounces = 4
sc.render.resolution_x = sc.render.resolution_y = RES
sc.render.film_transparent = True
sc.render.image_settings.color_mode = 'RGBA'
sc.view_settings.view_transform = 'AgX'; sc.view_settings.look = 'AgX - Punchy'

# mundo: HDRI de estudio (reflejos del oro)
w = bpy.data.worlds.new('w'); sc.world = w; w.use_nodes = True
nt = w.node_tree; [nt.nodes.remove(n) for n in list(nt.nodes)]
tc = nt.nodes.new('ShaderNodeTexCoord'); mp = nt.nodes.new('ShaderNodeMapping')
env = nt.nodes.new('ShaderNodeTexEnvironment'); env.image = bpy.data.images.load(os.path.join(D, 'hdri', 'studio_small_09.hdr'))
bg = nt.nodes.new('ShaderNodeBackground'); bg.inputs[1].default_value = 0.8
out = nt.nodes.new('ShaderNodeOutputWorld')
nt.links.new(tc.outputs['Generated'], mp.inputs['Vector']); nt.links.new(mp.outputs['Vector'], env.inputs['Vector'])
nt.links.new(env.outputs['Color'], bg.inputs['Color']); nt.links.new(bg.outputs[0], out.inputs[0])


def area(name, loc, size, energy, color=(1, 1, 1)):
    l = bpy.data.lights.new(name, 'AREA'); l.size = size; l.energy = energy; l.color = color
    o = bpy.data.objects.new(name, l); sc.collection.objects.link(o); o.location = loc
    o.rotation_euler = (Vector((0, 0, 0)) - Vector(loc)).to_track_quat('-Z', 'Y').to_euler()
    return o


def softbox(loc, size, strength, color=(1, 1, 1)):
    bpy.ops.mesh.primitive_plane_add(size=1, location=loc)
    o = bpy.context.object; o.scale = (*size, 1)
    o.rotation_euler = (Vector((0, 0, 0)) - Vector(loc)).to_track_quat('Z', 'Y').to_euler()
    m = bpy.data.materials.new('sb'); m.use_nodes = True; t = m.node_tree
    [t.nodes.remove(n) for n in list(t.nodes)]
    em = t.nodes.new('ShaderNodeEmission'); em.inputs[0].default_value = (*color, 1); em.inputs[1].default_value = strength
    o2 = t.nodes.new('ShaderNodeOutputMaterial'); t.links.new(em.outputs[0], o2.inputs[0])
    o.data.materials.append(m); o.visible_camera = False; o.visible_shadow = False
    return o


med = Medal(os.path.join(D, 'tex', 'medal'))
st = estilo(STYLE, os.path.join(D, 'estilos.json'))
_f = med.fr
_f['hole'] = [(_f['cx'] + (x - _f['cx']) * HOLE, _f['cy'] + (y - _f['cy']) * HOLE) for x, y in _f['hole']]
s = med.star(bevel=0.04)
s.data.materials.append(med.engraved('st', st['metal'], st['rough'], st['pat'], st['enamel'], st['linecol'], st['line_metal']))
# filete de oro pulido alrededor del hueco (marco de la foto)
k = med.SIZE / 3
ztop = EXTRUDE * k
fr = med.fr
hole = [((x - fr['cx']) * med.S2, -(y - fr['cy']) * med.S2) for x, y in fr['hole'][:-1]]
cu = bpy.data.curves.new('rim', 'CURVE'); cu.dimensions = '3D'; cu.bevel_depth = 0.022 * k; cu.bevel_resolution = 6
sp = cu.splines.new('POLY'); sp.points.add(len(hole) - 1)
for i, (x, y) in enumerate(hole):
    sp.points[i].co = (x * 1.0, y * 1.0, ztop + 0.01 * k, 1)
sp.use_cyclic_u = True
rim = bpy.data.objects.new('rim', cu); sc.collection.objects.link(rim)
rim.data.materials.append(Medal.plain('rimgold', Base_Color=st['metal'], Metallic=1.0, Roughness=0.06))
# leve inclinación: el oro refleja el softbox de arriba y se ve el canto
root = bpy.data.objects.new('root', None); sc.collection.objects.link(root)
root.rotation_euler = (math.radians(-9), math.radians(7), 0)
s.parent = root; rim.parent = root

# cámara de frente, tele largo (casi ortográfica, deja ver un poco el bisel)
DIST = 14.0
c = bpy.data.cameras.new('cam'); c.sensor_fit = 'HORIZONTAL'; c.sensor_width = 36
VIEW = med.SIZE * 1.06
c.lens = 36 * DIST / VIEW
cam = bpy.data.objects.new('cam', c); sc.collection.objects.link(cam); cam.location = (0, 0, DIST); sc.camera = cam

softbox((0, 6, 9), (12, 3.0), 2.6)
softbox((0, -7, 7), (12, 1.4), 1.2, (1, 0.85, 0.75))
softbox((-7, 0, 6), (1.2, 10), 1.4, (1, 0.7, 0.35))
area('rimA', (6, 2, 3), 3, 900, (0.2, 0.9, 0.85))
area('rimB', (-6, -2, 3), 3, 700, (1.0, 0.55, 0.2))
key = area('key', (0, 0, 8), 3.5, 900)

# puntas (destellos) y hueco, en coordenadas de imagen
tips = {}
for (x, y) in fr['outer'][:-1]:
    px, py = (x - fr['cx']) * med.S2, -(y - fr['cy']) * med.S2
    kk = int(((math.atan2(py, px) + math.pi / 8) % (2 * math.pi)) // (math.pi / 4))
    if kk not in tips or px * px + py * py > tips[kk][0] ** 2 + tips[kk][1] ** 2:
        tips[kk] = (px, py)
bpy.context.view_layer.update()


def scr(x, y, z):
    p = world_to_camera_view(sc, cam, root.matrix_world @ Vector((x, y, z)))
    return [round(p.x, 5), round(1 - p.y, 5)]


os.makedirs(OUTD, exist_ok=True)
json.dump(dict(style=STYLE, n=N, res=RES,
               hole=[scr(x, y, ztop) for x, y in hole],
               tips=[scr(*tips[kk], ztop) for kk in sorted(tips)]),
          open(os.path.join(OUTD, 'marco.json'), 'w'))

for i in range(N):
    a = 2 * math.pi * i / N + 0.6
    key.location = (5.5 * math.cos(a), 5.5 * math.sin(a), 6.5)
    key.rotation_euler = (Vector((0, 0, 0)) - key.location).to_track_quat('-Z', 'Y').to_euler()
    mp.inputs['Rotation'].default_value = (0, 0, a * 0.5)
    sc.render.filepath = os.path.join(OUTD, f'l_{i}.png')
    if not os.path.exists(sc.render.filepath):
        bpy.ops.render.render(write_still=True)
    print('variante', i, flush=True)
print('DONE')
