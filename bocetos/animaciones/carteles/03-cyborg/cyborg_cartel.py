"""Cartel 03 "CYBORG": la mascota cyber de Barullo en cromo negro líquido, ojos rojos y la medalla «o»
de plata joya con rubí colgada al pecho. Fondo transparente: la alfombra LED se compone en Remotion.

Reutiliza remotion/blender/barullo_cyber.py (cabeza, pelo, trenzas, piercings, cables, cascos y la
animación de 8 s en bucle a 120 BPM) y cambia materiales, luces, cámara y añade el colgante.

  blender.exe -b --factory-startup --python cyborg_cartel.py -- --lib <human_base_meshes_bundle.blend>
      --tex <logo-alfombra/tex/medal> --out C:/.../frames/ --view story|feed [--frames 1-240[:step]] [--res 50]
"""
import argparse
import math
import os
import sys

import bpy
from mathutils import Matrix, Vector

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.normpath(os.path.join(HERE, '..', '..', '..', '..'))
sys.path.insert(0, os.path.join(REPO, 'remotion', 'blender'))
sys.path.insert(0, os.path.join(HERE, '..', 'comun'))
import barullo_cyber as base  # noqa: E402
from medalla_lib import Medal  # noqa: E402

hex_lin = base.hex_lin
RED = '#FF2A36'


def materials():
    M = base.materials()
    # Cromo negro líquido (refs 16 y 17): metal oscuro casi espejo con barniz.
    M['skin'] = base.principled('M_black_chrome', hex_lin('#1C1C22'), metal=1.0, rough=0.07, coat=1.0, coat_rough=0.02)
    M['sclera'] = base.principled('M_eye_red', hex_lin('#FF5A64'), rough=0.1, emit=hex_lin(RED), emit_strength=6.0)
    M['iris'] = base.principled('M_iris_hot', hex_lin('#FFFFFF'), rough=0.1, emit=hex_lin('#FFD9DC'), emit_strength=16.0)
    M['lash'] = base.principled('M_lash_red', hex_lin('#5A0A12'), rough=0.3, emit=hex_lin(RED), emit_strength=0.4)
    M['chrome'] = base.principled('M_chrome', hex_lin('#F2F3F7'), metal=1.0, rough=0.06)
    return M


_neon = base.neon_material


def red_neon():
    m, wave = _neon()
    em = next(n for n in m.node_tree.nodes if n.type == 'EMISSION')
    em.inputs['Color'].default_value = hex_lin('#FF4250')
    return m, wave


def chain(points, parent, mat, link_len=0.0042, wire=0.0007):
    """Cadena de eslabones (toroides alternos) a lo largo de una polilínea."""
    path = [Vector(p) for p in points]
    seg = [(path[i], path[i + 1]) for i in range(len(path) - 1)]
    total = sum((b - a).length for a, b in seg)
    n = int(total / link_len)
    proto = base.torus_obj('LINK-proto', mat, link_len * 0.42, wire, None, seg=16, ts=6)
    proto.scale = (1, 0.62, 1)
    objs = []
    d = 0.0
    for i in range(n):
        # punto a distancia d
        acc = 0.0
        for a, b in seg:
            L = (b - a).length
            if acc + L >= d:
                p = a + (b - a) * ((d - acc) / L)
                tan = (b - a).normalized()
                break
            acc += L
        o = proto.copy()
        bpy.context.scene.collection.objects.link(o)
        q = tan.to_track_quat('Y', 'Z')
        o.rotation_mode = 'QUATERNION'
        o.rotation_quaternion = q @ Matrix.Rotation(math.pi / 2 * (i % 2), 4, 'Y').to_quaternion()
        o.location = p
        o.parent = parent
        o.matrix_parent_inverse = parent.matrix_world.inverted()
        objs.append(o)
        d += link_len
    bpy.data.objects.remove(proto)
    return objs


def pendant(head, eye_z, tex, M):
    """Medalla al pecho colgando de una cadena que sale de detrás de los cascos."""
    zc = eye_z - 0.2
    c, r = base.slice_center(head, zc)
    # punto del esternón: raycast frontal bajo la nuez
    S = base.Surface(head)
    zs = 0.047  # el busto acaba en z=0: placa del pecho bajo el neón del cuello
    hit = S.front(0.0, zs)
    chest = hit[0] if hit else Vector((0, -0.07, zs))
    nrm = hit[1] if hit else Vector((0, -1, 0))
    print('LANDMARK chest', tuple(round(v, 4) for v in chest), tuple(round(v, 3) for v in nrm))
    md = Medal(tex, size=0.095)
    holder = bpy.data.objects.new('PENDANT', None)
    base.link(holder, head)
    holder.location = chest + nrm * 0.016
    # cara al frente, levemente inclinada hacia arriba como apoyada en el pecho
    holder.rotation_mode = 'XYZ'
    holder.rotation_euler = (math.radians(97), 0, 0)  # cara un poco hacia abajo: refleja el suelo oscuro, no la tira blanca
    bpy.context.view_layer.update()
    # EEVEE no refracta bien el rubí transmisivo: gema opaca de barniz con brillo interno rojo
    ruby_mat = Medal.plain('rubi_eevee', Base_Color=(0.3, 0.0, 0.012), Roughness=0.02, Coat_Weight=1.0,
                           Emission_Color=(1.0, 0.02, 0.06), Emission_Strength=0.35)
    star, ruby, gem_r = md.build(two_sided=False, ruby_mat=ruby_mat)
    star.parent = holder
    star.matrix_parent_inverse = Matrix.Identity(4)
    # anilla en la punta superior
    top = 0.095 / 2 * 0.97
    ring = base.torus_obj('GEO-bail', M['chrome'], 0.0055, 0.0016, holder)
    ring.matrix_parent_inverse = Matrix.Identity(4)
    ring.location = (0, top + 0.0045, 0)
    ring.rotation_euler = (0, math.radians(90), 0)
    bpy.context.view_layer.update()
    bail = ring.matrix_world.translation.copy() + Vector((0, 0, 0.005))
    # cadena: de la anilla sube por el pecho hasta el cuello, por los dos lados
    for s in (-1, 1):
        pts = [bail]
        for k in range(1, 13):
            u = k / 12
            z = bail.z + (eye_z - 0.125 - bail.z) * u ** 0.9
            a = math.radians(-90 + s * (8 + 70 * u ** 0.8))
            d = Vector((math.cos(a), math.sin(a), 0))
            cc, rr = base.slice_center(head, z)
            pts.append(Vector((cc.x, cc.y, z)) + d * (rr + 0.004 + 0.012 * (1 - u) ** 3))
        chain(pts, head, M['chrome'])
    return holder, ruby


def setup(view, out, eye_z, res):
    sc = bpy.context.scene
    base.setup_render('square', out, eye_z)
    sc.render.resolution_x, sc.render.resolution_y = (2160, 3840) if view == 'story' else (2160, 2700)
    sc.render.resolution_percentage = res
    sc.render.film_transparent = True
    sc.render.image_settings.color_mode = 'RGBA'
    sc.view_settings.view_transform = 'AgX'
    sc.view_settings.look = 'AgX - Punchy'
    cam = sc.camera
    cam.data.lens = 70
    # el busto (z 0..0.37) ocupa del 8 % al 56 % del alto en story y del 8 % al 70 % en feed,
    # desplazado a la derecha para dejar la columna de la fecha y el logo a la izquierda
    if view == 'story':
        tgt, dist, cam.data.shift_x = Vector((0, 0, 0.046)), 2.25, -0.05
    else:
        tgt, dist, cam.data.shift_x = Vector((0, 0, 0.119)), 1.74, -0.17
    cam.location = tgt + Vector((0.0, -dist, 0.06))
    cam.rotation_quaternion = (cam.location - tgt).to_track_quat('Z', 'Y')
    # luces: blanco duro arriba para las vetas del cromo, rojo de marca en los contornos
    for n in ('LGT-rim_violet', 'LGT-eye_bounce'):
        o = bpy.data.objects[n]
        o.data.color = hex_lin(RED)[:3]
    bpy.data.objects['LGT-rim_violet'].data.energy = 45
    bpy.data.objects['LGT-eye_bounce'].data.energy = 1.2
    bpy.data.objects['LGT-key'].data.energy = 22
    base.light('LGT-strip_top', 'AREA', (0.0, -0.9, eye_z + 0.7), (0, 0, eye_z), 18, '#FFFFFF', size=1.4, spec=1.0)
    base.light('LGT-red_low', 'AREA', (0.5, -0.8, eye_z - 0.6), (0, 0, eye_z - 0.3), 20, RED, size=0.8, spec=1.0)


def recolor_world():
    """El estudio de barullo_cyber tiene una tira violeta: pasa a rojo para los reflejos del cromo."""
    for n in bpy.context.scene.world.node_tree.nodes:
        if n.type == 'VECT_MATH' and n.operation == 'SCALE':
            v = n.inputs[0].default_value
            if v[2] > v[0] * 1.3:  # la violeta (#9B7BFF)
                n.inputs[0].default_value = tuple(x * 5.0 for x in hex_lin('#FF2A36')[:3])


def main():
    argv = sys.argv[sys.argv.index('--') + 1:]
    ap = argparse.ArgumentParser()
    ap.add_argument('--lib', required=True)
    ap.add_argument('--tex', required=True)
    ap.add_argument('--out', required=True)
    ap.add_argument('--view', default='story')
    ap.add_argument('--frames', default='')
    ap.add_argument('--res', type=int, default=100)
    ap.add_argument('--samples', type=int, default=64)
    a = ap.parse_args(argv)

    bpy.ops.wm.read_factory_settings(use_empty=True)
    M = materials()
    base.materials = lambda: M
    base.neon_material = red_neon
    base.build_world()
    recolor_world()
    head, eyes, pulse = base.build(a.lib, M)
    eye_z = eyes[0].matrix_world.translation.z
    holder, ruby = pendant(head, eye_z, a.tex, M)
    base.animate(head, eyes, pulse)
    setup(a.view, a.out, eye_z, a.res)
    bpy.context.scene.eevee.taa_render_samples = a.samples
    base.setup_glare()
    sc = bpy.context.scene
    rng, _, step = a.frames.partition(':')
    if rng:
        import json
        from bpy_extras.object_utils import world_to_camera_view
        f0, _, f1 = rng.partition('-')
        gems = {}
        for f in range(int(f0), int(f1 or f0) + 1, int(step or 1)):
            sc.frame_set(f)
            p = world_to_camera_view(sc, sc.camera, ruby.matrix_world.translation)
            gems[f] = dict(x=round(p.x, 4), y=round(1 - p.y, 4), vis=1.0)
            if os.environ.get('NORENDER'):
                continue
            sc.render.filepath = f'{a.out}{a.view}_{f:04d}'
            bpy.ops.render.render(write_still=True)
            print('frame', f, flush=True)
        json.dump(gems, open(f'{a.out}gem_{a.view}_{f0}-{f1 or f0}.json', 'w'))


main()
