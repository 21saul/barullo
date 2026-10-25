"""Cartel 01 "LA MEDALLA": la «o» estrella de plata joya con rubí, girando en bucle.

Basado en bocetos/scripts/medal.py (mismos materiales, gemas y luces). Diferencias:
  - Las dos caras llevan grabado y rubí, y la trasera lee la textura con x invertida.
    Así, tras medio giro sobre su eje vertical, la imagen es idéntica a la del frame 0,
    y el bucle de 4 s se reproduce dos veces en los 8 s del cartel.
  - Fondo transparente: el fondo (alfombra LED) se compone en Remotion.
  - Escribe gem.json con la posición en pantalla del rubí por frame, para el destello.

  blender.exe -b --factory-startup --python medalla_anim.py -- <logo-alfombra dir> <out dir> <frames a-b> [samples] [res]
"""
import bpy, json, math, os, sys
from mathutils import Vector
from bpy_extras.object_utils import world_to_camera_view

_A = sys.argv[sys.argv.index('--') + 1:]
D, OUTD = _A[0], _A[1]
_fr = (_A[2] if len(_A) > 2 else '0-119').split(':')
F0, F1 = (int(x) for x in _fr[0].split('-'))
STEP = int(_fr[1]) if len(_fr) > 1 else 1
SAMPLES = int(_A[3]) if len(_A) > 3 else 48
RES = int(_A[4]) if len(_A) > 4 else 1800
LOOP = 120  # 4 s a 30 fps = medio giro
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'comun'))
from medalla_lib import Medal  # noqa: E402

sc = bpy.context.scene
for o in list(bpy.data.objects):
    bpy.data.objects.remove(o)
sc.render.engine = 'CYCLES'; sc.cycles.samples = SAMPLES; sc.cycles.use_denoising = True; sc.cycles.device = 'CPU'
sc.cycles.use_adaptive_sampling = True; sc.cycles.adaptive_threshold = 0.02
sc.cycles.max_bounces = 8; sc.cycles.transmission_bounces = 8; sc.cycles.glossy_bounces = 6
sc.render.resolution_x = sc.render.resolution_y = RES
sc.render.film_transparent = True
sc.render.image_settings.color_mode = 'RGBA'
sc.render.fps = 30
sc.view_settings.view_transform = 'AgX'; sc.view_settings.look = 'AgX - Punchy'


def world():
    w = bpy.data.worlds.new('w'); sc.world = w; w.use_nodes = True
    nt = w.node_tree; [nt.nodes.remove(n) for n in list(nt.nodes)]
    tc = nt.nodes.new('ShaderNodeTexCoord'); mp = nt.nodes.new('ShaderNodeMapping'); mp.inputs['Rotation'].default_value = (0, 0, 0.6)
    env = nt.nodes.new('ShaderNodeTexEnvironment'); env.image = bpy.data.images.load(os.path.join(D, 'hdri', 'studio_small_09.hdr'))
    b1 = nt.nodes.new('ShaderNodeBackground'); b1.inputs[1].default_value = 0.9
    out = nt.nodes.new('ShaderNodeOutputWorld')
    nt.links.new(tc.outputs['Generated'], mp.inputs['Vector']); nt.links.new(mp.outputs['Vector'], env.inputs['Vector'])
    nt.links.new(env.outputs['Color'], b1.inputs['Color']); nt.links.new(b1.outputs[0], out.inputs[0])


def area(name, loc, size, energy, color=(1, 1, 1), target=(0, 0, 0)):
    l = bpy.data.lights.new(name, 'AREA'); l.size = size; l.energy = energy; l.color = color
    o = bpy.data.objects.new(name, l); sc.collection.objects.link(o); o.location = loc
    o.rotation_euler = (Vector(target) - Vector(loc)).to_track_quat('-Z', 'Y').to_euler()
    return l


def softbox(loc, size, strength, color=(1, 1, 1)):
    bpy.ops.mesh.primitive_plane_add(size=1, location=loc)
    o = bpy.context.object; o.scale = (*size, 1)
    o.rotation_euler = (Vector((0, 0, 0)) - Vector(loc)).to_track_quat('Z', 'Y').to_euler()
    m = bpy.data.materials.new('sb'); m.use_nodes = True; nt = m.node_tree
    [nt.nodes.remove(n) for n in list(nt.nodes)]
    em = nt.nodes.new('ShaderNodeEmission'); em.inputs[0].default_value = (*color, 1); em.inputs[1].default_value = strength
    out = nt.nodes.new('ShaderNodeOutputMaterial'); nt.links.new(em.outputs[0], out.inputs[0])
    o.data.materials.append(m); o.visible_camera = False; o.visible_shadow = False


world()
root = bpy.data.objects.new('root', None); sc.collection.objects.link(root)
root.rotation_euler = (math.radians(83), 0, math.radians(-14))
spin = bpy.data.objects.new('spin', None); sc.collection.objects.link(spin); spin.parent = root
s, ruby, gem_r = Medal(os.path.join(D, 'tex', 'medal')).build(spin)

c = bpy.data.cameras.new('cam'); c.lens = 100
cam = bpy.data.objects.new('cam', c); sc.collection.objects.link(cam); cam.location = (0.8, -9.5, 1.2)
cam.rotation_euler = (Vector((0, 0, 0)) - cam.location).to_track_quat('-Z', 'Y').to_euler(); sc.camera = cam

# luces de medal.py: barras blancas arriba/abajo, contraluces rosa y naranja
softbox((0, -9, 5), (12, 2.4), 2.4)
softbox((0, -9, -4), (12, 1.2), 1.0, (1, 0.75, 0.85))
softbox((-7, -5, 0.5), (1.0, 6), 1.6, (1, 0.6, 0.25))
area('key', (-3, -6, 5), 4, 700)
area('rimP', (4, 3, 2), 2.5, 1500, (1, 0.22, 0.55))
area('rimO', (-4, 3, -1), 2.5, 1000, (1, 0.5, 0.12))
# rojo de marca desde abajo a la derecha: tiñe el bisel durante el giro
area('rimR', (5, -3, -3), 3, 900, (1, 0.05, 0.08))


def ease(u):
    """quintic in-out"""
    return 16 * u ** 5 if u < 0.5 else 1 - (-2 * u + 2) ** 5 / 2


def pose(f):
    """Medio giro en LOOP frames: reposo de cara (con vaivén leve) y giro con aceleración suave."""
    t = (f % LOOP) / LOOP
    u = min(1.0, max(0.0, (t - 0.22) / 0.78))
    turn = math.pi * ease(u)
    sway = math.radians(5) * math.sin(2 * math.pi * t)      # periódico: cierra el bucle
    tilt = math.radians(3) * math.sin(2 * math.pi * t + 1.3)
    bob = 0.04 * math.sin(2 * math.pi * t + 0.4)
    return turn + sway, tilt, bob


gems = {}
os.makedirs(OUTD, exist_ok=True)
for f in range(F0, F1 + 1, STEP):
    turn, tilt, bob = pose(f)
    spin.rotation_euler = (tilt, turn, 0)
    root.location = (0, 0, bob)
    bpy.context.view_layer.update()
    # rubí visible: punto más alto de la gema frontal o trasera según qué cara mira a cámara
    n = (s.matrix_world.to_3x3() @ Vector((0, 0, 1))).normalized()
    to_cam = (cam.location - s.matrix_world.translation).normalized()
    facing = n.dot(to_cam)
    top = s.matrix_world @ Vector((0, 0, math.copysign(0.04 + gem_r * 0.62, facing)))
    p = world_to_camera_view(sc, cam, top)
    gems[f] = dict(x=round(p.x, 4), y=round(1 - p.y, 4), vis=round(abs(facing), 4))
    sc.render.filepath = os.path.join(OUTD, f'm_{f:04d}.png')
    if not os.environ.get('NORENDER'):
        bpy.ops.render.render(write_still=True)
    print('frame', f, flush=True)

gp = os.path.join(OUTD, f'gem_{F0:04d}-{F1:04d}.json')
json.dump(gems, open(gp, 'w'))
print('DONE', gp)
