"""
Mascota de Barullo v4: cabeza estilizada de porcelana (cráneo grande, rasgos
pequeños), ojos violetas a media asta con pestañas-cuchilla, grillz, cigarro con
brasa roja, corona de pinchos cromados, cascos de DJ y tatuaje "BARULLO".
Animación actuada (8 s, bucle): calada, mira a un lado, parpadea, suelta el humo
abriendo la boca, mira al otro lado, parpadea y vuelve.

Base: "head_stylized" del pack oficial Human Base Meshes de Blender (CC0).

  blender.exe -b --factory-startup --python barullo_v4.py -- \
      --lib C:/.../human_base_meshes_bundle.blend --out C:/ruta/frames/ \
      --variant square|wide [--frames 1-240] [--save escena.blend]
"""

import argparse
import math
import os
import random
import sys

import bmesh
import bpy
from mathutils import Matrix, Quaternion, Vector

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import barullo_cyber as base  # noqa: E402  (utilidades compartidas con la v3)

HEAD = 'GEO-head_stylized'
base.HEAD = HEAD  # link() aplica la inversa de padre a lo que cuelga de esta cabeza
FPS, FRAMES, SECONDS = 30, 240, 8.0
BPM = 120
MOUTH_Z = 0.129  # comisura (medida con raycast sobre la malla base)
hex_lin = base.hex_lin
link = base.link


# ---------------------------------------------------------------- utilidades

def smooth(a, b, x):
    if b == a:
        return 1.0 if x >= b else 0.0
    u = max(0.0, min(1.0, (x - a) / (b - a)))
    return u * u * (3 - 2 * u)


def track(keys, sec):
    """Curva por poses clave [(segundo, valor)] con ease-in-out entre poses."""
    for (t0, v0), (t1, v1) in zip(keys, keys[1:]):
        if t0 <= sec <= t1:
            return v0 + (v1 - v0) * smooth(t0, t1, sec)
    return keys[-1][1]


def new_mesh_obj(name, bm, mat, parent=None, smooth_shade=True):
    me = bpy.data.meshes.new(name)
    bm.to_mesh(me)
    bm.free()
    if smooth_shade:
        me.shade_smooth()
    if mat is not None:
        me.materials.append(mat)
    return link(bpy.data.objects.new(name, me), parent)


def empty(name, parent=None, loc=(0, 0, 0), rot=None):
    o = bpy.data.objects.new(name, None)
    o.empty_display_size = 0.02
    link(o, parent)
    o.location = loc
    if rot is not None:
        o.rotation_mode = 'QUATERNION'
        o.rotation_quaternion = rot
    return o


def cone(name, mat, length, radius, parent, seg=32):
    bm = bmesh.new()
    bmesh.ops.create_cone(bm, cap_ends=True, cap_tris=False, segments=seg, radius1=radius, radius2=0.0, depth=length)
    bmesh.ops.translate(bm, verts=bm.verts, vec=(0, 0, length / 2))
    return new_mesh_obj(name, bm, mat, parent)


def cylinder(name, mat, r, depth, parent, seg=48, bevel=0.0):
    bm = bmesh.new()
    bmesh.ops.create_cone(bm, cap_ends=True, cap_tris=False, segments=seg, radius1=r, radius2=r, depth=depth)
    o = new_mesh_obj(name, bm, mat, parent)
    if bevel:
        b = o.modifiers.new('bevel', 'BEVEL')
        b.width = bevel
        b.segments = 4
    return o


def along(d):
    return Vector(d).normalized().to_track_quat('Z', 'Y')


# ---------------------------------------------------------------- materiales

def emission_mix(name, col_center, col_edge, strength):
    """Brillo que va de blanco caliente en el centro a violeta en el canto."""
    m = bpy.data.materials.new(name)
    m.use_nodes = True
    nt = m.node_tree
    N, L = nt.nodes, nt.links
    N.clear()
    out = N.new('ShaderNodeOutputMaterial')
    lw = N.new('ShaderNodeLayerWeight')
    lw.inputs['Blend'].default_value = 0.35
    mix = N.new('ShaderNodeMix')
    mix.data_type = 'RGBA'
    mix.inputs[6].default_value = col_center
    mix.inputs[7].default_value = col_edge
    L.new(lw.outputs['Facing'], mix.inputs['Factor'])
    em = N.new('ShaderNodeEmission')
    em.name = 'EMIT'
    em.inputs['Strength'].default_value = strength
    L.new(mix.outputs[2], em.inputs['Color'])
    L.new(em.outputs[0], out.inputs['Surface'])
    return m


def smoke_material(name, two_layer=True):
    """
    Humo volumétrico: ruido 3D recortado por un perfil (más ancho y tenue arriba).
    Dos capas de ruido que se desplazan y se funden: el bucle cierra sin salto.
    Nodos animables: 'OFF_A', 'OFF_B' (Mapping) y 'XFADE' (mezcla), 'DENS' (densidad).
    """
    m = bpy.data.materials.new(name)
    m.use_nodes = True
    nt = m.node_tree
    N, L = nt.nodes, nt.links
    N.clear()
    out = N.new('ShaderNodeOutputMaterial')
    vol = N.new('ShaderNodeVolumePrincipled')
    vol.inputs['Color'].default_value = hex_lin('#D9D3E6')
    vol.inputs['Anisotropy'].default_value = 0.3
    coord = N.new('ShaderNodeTexCoord')

    def layer(tag):
        mp = N.new('ShaderNodeMapping')
        mp.name = tag
        L.new(coord.outputs['Object'], mp.inputs['Vector'])
        nz = N.new('ShaderNodeTexNoise')
        nz.inputs['Scale'].default_value = 2.2
        nz.inputs['Detail'].default_value = 6.0
        nz.inputs['Roughness'].default_value = 0.6
        nz.inputs['Distortion'].default_value = 0.6
        L.new(mp.outputs[0], nz.inputs['Vector'])
        return nz.outputs['Fac']

    a = layer('OFF_A')
    b = layer('OFF_B')
    xf = N.new('ShaderNodeMix')
    xf.name = 'XFADE'
    xf.data_type = 'FLOAT'
    L.new(a, xf.inputs[2])
    L.new(b, xf.inputs[3])
    xf.inputs['Factor'].default_value = 0.0
    shape = N.new('ShaderNodeMapRange')
    shape.interpolation_type = 'SMOOTHSTEP'
    shape.inputs['From Min'].default_value = 0.48
    shape.inputs['From Max'].default_value = 0.72
    L.new(xf.outputs[0], shape.inputs['Value'])

    # Perfil: z local -1..1 → abre hacia arriba y se desvanece; radio xy limitado.
    sep = N.new('ShaderNodeSeparateXYZ')
    L.new(coord.outputs['Object'], sep.inputs[0])
    up = N.new('ShaderNodeMapRange')
    up.inputs['From Min'].default_value = -1.0
    up.inputs['From Max'].default_value = 1.0
    L.new(sep.outputs['Z'], up.inputs['Value'])  # 0 abajo → 1 arriba
    xy = N.new('ShaderNodeCombineXYZ')
    L.new(sep.outputs['X'], xy.inputs['X'])
    L.new(sep.outputs['Y'], xy.inputs['Y'])
    rlen = N.new('ShaderNodeVectorMath')
    rlen.operation = 'LENGTH'
    L.new(xy.outputs[0], rlen.inputs[0])
    width = N.new('ShaderNodeMath')
    width.operation = 'MULTIPLY_ADD'
    L.new(up.outputs['Result'], width.inputs[0])
    width.inputs[1].default_value = 0.75
    width.inputs[2].default_value = 0.25
    rel = N.new('ShaderNodeMath')
    rel.operation = 'DIVIDE'
    L.new(rlen.outputs['Value'], rel.inputs[0])
    L.new(width.outputs[0], rel.inputs[1])
    radial = N.new('ShaderNodeMapRange')
    radial.interpolation_type = 'SMOOTHSTEP'
    radial.inputs['From Min'].default_value = 1.0
    radial.inputs['From Max'].default_value = 0.2
    L.new(rel.outputs[0], radial.inputs['Value'])
    fade = N.new('ShaderNodeMapRange')
    fade.interpolation_type = 'SMOOTHSTEP'
    fade.inputs['From Min'].default_value = 1.0
    fade.inputs['From Max'].default_value = 0.35
    L.new(up.outputs['Result'], fade.inputs['Value'])

    m1 = N.new('ShaderNodeMath')
    m1.operation = 'MULTIPLY'
    L.new(shape.outputs['Result'], m1.inputs[0])
    L.new(radial.outputs['Result'], m1.inputs[1])
    m2 = N.new('ShaderNodeMath')
    m2.operation = 'MULTIPLY'
    L.new(m1.outputs[0], m2.inputs[0])
    L.new(fade.outputs['Result'], m2.inputs[1])
    dens = N.new('ShaderNodeMath')
    dens.name = 'DENS'
    dens.operation = 'MULTIPLY'
    dens.inputs[1].default_value = 40.0
    L.new(m2.outputs[0], dens.inputs[0])
    L.new(dens.outputs[0], vol.inputs['Density'])
    L.new(vol.outputs[0], out.inputs['Volume'])
    return m


def materials():
    P = base.principled
    return {
        # Porcelana blanca-lila muy brillante (refs cabeza blanca y chica cyber).
        'skin': P('M_porcelain', hex_lin('#CFC5E6'), rough=0.26, coat=1.0, coat_rough=0.03,
                  **{'Subsurface Weight': 0.2, 'Subsurface Scale': 0.003,
                     'Subsurface Radius': Vector((1.0, 0.6, 0.8)),
                     'Thin Film Thickness': 380.0, 'Thin Film IOR': 1.35}),
        'lips': P('M_lips', hex_lin('#C9B8D9'), rough=0.12, coat=1.0, coat_rough=0.01),
        'sclera': emission_mix('M_eye_glow', hex_lin('#8C6CFF'), hex_lin('#3A1FD9'), 0.9),
        'iris': emission_mix('M_iris_glow', hex_lin('#FFFFFF'), hex_lin('#E2D6FF'), 6.0),
        'lash': P('M_lash_blade', hex_lin('#050507'), metal=0.5, rough=0.12, coat=1.0),
        'chrome': P('M_chrome', hex_lin('#F2F3F7'), metal=1.0, rough=0.12),
        'stud_dark': P('M_stud_dark', hex_lin('#0B0B10'), metal=0.6, rough=0.1, coat=1.0),
        'red': P('M_red_lacquer', hex_lin('#C40A22'), rough=0.2, coat=1.0, coat_rough=0.02),
        'white_lacquer': P('M_white_lacquer', hex_lin('#ECEAF2'), rough=0.18, coat=1.0, coat_rough=0.02),
        'cushion': P('M_cushion', hex_lin('#111116'), rough=0.5, coat=0.3),
        'mouth': P('M_mouth', hex_lin('#140308'), rough=0.4),
        'tattoo': P('M_tattoo', hex_lin('#3A3550'), rough=0.3, coat=1.0, coat_rough=0.03),
        'paper': P('M_paper', hex_lin('#F3F1EC'), rough=0.6),
        'filter': P('M_filter', hex_lin('#D8A56A'), rough=0.55),
        'ash': P('M_ash', hex_lin('#5B5862'), rough=0.9),
        'ember': emission_mix('M_ember', hex_lin('#FFD08A'), hex_lin('#FF2A10'), 4.0),
        'glass': P('M_droplet', hex_lin('#FFFFFF'), rough=0.0, **{'Transmission Weight': 1.0, 'IOR': 1.33}),
        'wisp': smoke_material('M_smoke_wisp'),
        'puff': smoke_material('M_smoke_puff'),
    }


# ---------------------------------------------------------------- cabeza

def load_head(lib):
    with bpy.data.libraries.load(lib, link=False) as (src, dst):
        dst.objects = [n for n in src.objects if n.startswith(HEAD)]
    for o in dst.objects:
        bpy.context.scene.collection.objects.link(o)
        o.hide_render = False
        o.hide_viewport = False
    head = bpy.data.objects[HEAD]
    bpy.context.view_layer.update()
    bb = [head.matrix_world @ Vector(c) for c in head.bound_box]
    cx = (min(v.x for v in bb) + max(v.x for v in bb)) / 2
    cy = (min(v.y for v in bb) + max(v.y for v in bb)) / 2
    shift = Matrix.Translation(-Vector((cx, cy, min(v.z for v in bb))))
    kids = [(c, c.matrix_world.copy()) for c in head.children]
    head.data.transform(shift @ head.matrix_world)
    head.matrix_world = Matrix.Identity(4)
    for c, cw in kids:
        c.matrix_parent_inverse = Matrix.Identity(4)
        c.matrix_world = shift @ cw
    bpy.context.view_layer.update()
    eyes = sorted((o for o in dst.objects if '.eye.' in o.name), key=lambda o: o.matrix_world.translation.x)
    return head, eyes


def stylize(head):
    """Cráneo más grande y redondo (refs poiandkeely): se infla todo lo que queda por encima de los ojos."""
    c = Vector((0.0, 0.0, 0.2))
    for v in head.data.vertices:
        w = smooth(0.2, 0.33, v.co.z)
        if w > 0:
            d = v.co - c
            v.co = c + d * (1.0 + 0.16 * w) + Vector((0, 0.01 * w, 0.012 * w))
    head.data.update()


def add_jaw_key(head):
    """Shape key 'jaw': gira la mandíbula y el labio inferior hacia abajo."""
    me = head.data
    if not me.shape_keys:
        head.shape_key_add(name='Basis')
    key = head.shape_key_add(name='jaw', from_mix=False)
    pivot = Vector((0.0, 0.0, 0.165))
    ang = 0.2
    for i, v in enumerate(me.vertices):
        co = v.co
        if co.y > -0.02 or co.z > MOUTH_Z:
            continue
        w = smooth(MOUTH_Z, MOUTH_Z - 0.008, co.z)  # el labio inferior se separa del superior
        w *= 1.0 - smooth(0.05, 0.09, abs(co.x))
        w *= 1.0 - smooth(0.02, 0.05, MOUTH_Z - 0.065 - co.z) if co.z < MOUTH_Z - 0.065 else 1.0
        if w <= 0:
            continue
        R = Matrix.Rotation(ang * w, 3, 'X')
        key.data[i].co = pivot + R @ (co - pivot)
    moved = sum(1 for i, v in enumerate(me.vertices) if (key.data[i].co - v.co).length > 1e-6)
    print('DEBUG jaw verts moved', moved)
    return key


def build(lib, M):
    rnd = random.Random(16)
    head, eyes = load_head(lib)
    stylize(head)
    head.data.materials.clear()
    head.data.materials.append(M['skin'])
    jaw_key = add_jaw_key(head)
    jaw_key.value = 0.0  # al crearla vale 1: con la boca abierta los raycasts se colarían por la ranura
    head.data.shade_smooth()
    sub = head.modifiers.new('subsurf', 'SUBSURF')
    sub.levels = sub.render_levels = 2
    S = base.Surface(head)

    eye_r = eyes[0].dimensions.x / 2
    eye_c = [e.matrix_world.translation.copy() for e in eyes]
    rig = {'head': head, 'jaw_key': jaw_key, 'eyes': [], 'lids': [], 'spikes': [], 'cups': [], 'teeth': []}

    # --- Ojos: globo violeta con iris blanco caliente; párpados de porcelana que giran.
    for s, e in zip((-1, 1), eyes):
        e.data.materials.clear()
        e.data.materials.append(M['sclera'])
        e.data.shade_smooth()
        ec = e.matrix_world.translation.copy()
        pivot = empty(f'EYEPIV-{s}', head, loc=ec)
        # El globo cuelga del pivote en su centro (coordenadas locales, sin inversa).
        e.parent = pivot
        e.matrix_parent_inverse = Matrix.Identity(4)
        e.location = (0, 0, 0)
        e.rotation_euler = (0, 0, 0)
        bm = bmesh.new()
        bmesh.ops.create_uvsphere(bm, u_segments=32, v_segments=16, radius=1)
        iris = new_mesh_obj(f'GEO-iris-{s}', bm, M['iris'], pivot)
        iris.location = (0, -eye_r * 0.9, 0)
        iris.scale = (eye_r * 0.42, eye_r * 0.14, eye_r * 0.42)
        rig['eyes'].append(pivot)

        lids = []
        for kind in ('up', 'low'):
            bm = bmesh.new()
            bmesh.ops.create_uvsphere(bm, u_segments=64, v_segments=32, radius=eye_r * 1.08)
            kill = [v for v in bm.verts if (v.co.z < -1e-5 if kind == 'up' else v.co.z > 1e-5)]
            bmesh.ops.delete(bm, geom=kill, context='VERTS')
            lid_e = empty(f'LID-{kind}-{s}', head, loc=ec)
            lid_e.rotation_mode = 'XYZ'
            lid = new_mesh_obj(f'GEO-lid-{kind}-{s}', bm, M['skin'], lid_e)
            sol = lid.modifiers.new('solid', 'SOLIDIFY')
            sol.thickness = eye_r * 0.06
            sol.offset = -1
            lids.append(lid_e)
            if kind == 'up':
                # Pestañas-cuchilla negras en el canto delantero; más largas hacia fuera.
                for j in range(6):
                    u = j / 5
                    outer = u  # 0 = lagrimal, 1 = rabillo
                    phi = math.radians(-90 - s * (-60 + 135 * u))
                    p = Vector((math.cos(phi), math.sin(phi), 0)) * eye_r * 1.1
                    d = Vector((math.cos(phi) * 0.8 + s * 0.6 * outer, math.sin(phi) * 0.5, 0.75 + 0.3 * outer))
                    lash_e = empty(f'LASH-{s}-{j}', lid_e, loc=p, rot=along(d))
                    c = cone(f'GEO-lash-{s}-{j}', M['lash'], eye_r * (0.6 + 1.3 * outer ** 1.5), eye_r * 0.13, lash_e, seg=16)
                    c.scale = (1.0, 0.28, 1.0)
        rig['lids'].append(lids)

    # --- Boca: interior oscuro y grillz cromado que asoman al abrir la mandíbula.
    # En la comisura hay una ranura real: se mide en los labios, justo encima y debajo.
    lips = [S.front(0.0, MOUTH_Z + dz) for dz in (0.004, -0.004)]
    seam_y = max(h[0].y for h in lips if h) + 0.003 if all(lips) else -0.119
    mouth = empty('MOUTH', head, loc=(0, seam_y - 0.0012, MOUTH_Z - 0.001))
    bm = bmesh.new()
    bmesh.ops.create_uvsphere(bm, u_segments=48, v_segments=16, radius=1)
    cav = new_mesh_obj('GEO-mouth_cavity', bm, M['mouth'], mouth)
    cav.scale = (0.021, 0.0015, 0.001)
    rig['cavity'] = cav
    teeth = empty('TEETH', mouth, loc=(0, -0.0006, -0.0004))
    for k in range(6):
        x = -0.0125 + 0.025 * k / 5
        bm = bmesh.new()
        bmesh.ops.create_cube(bm, size=1)
        t = new_mesh_obj(f'GEO-tooth-{k}', bm, M['chrome'], teeth)
        t.location = (x, 0, -0.0026)
        t.scale = (0.0042, 0.0016, 0.005)
        bv = t.modifiers.new('bevel', 'BEVEL')
        bv.width = 0.18
        bv.segments = 3
    rig['teeth_root'] = teeth

    # --- Cigarro en la comisura derecha (de su lado izquierdo en pantalla), brasa animada.
    cig = empty('CIG', head, loc=(0.019, seam_y - 0.001, MOUTH_Z - 0.0015), rot=along((0.55, -0.72, -0.3)))
    cig.rotation_mode = 'XYZ'
    r = 0.0032
    parts = (('filter', 0.0, 0.016), ('paper', 0.016, 0.046))
    for kind, z0, ln in parts:
        c = cylinder(f'GEO-cig-{kind}', M[kind], r, ln, cig, seg=24)
        c.location = (0, 0, z0 + ln / 2 - 0.004)
    bm = bmesh.new()
    bmesh.ops.create_uvsphere(bm, u_segments=24, v_segments=12, radius=1)
    ember = new_mesh_obj('GEO-ember', bm, M['ember'], cig)
    ember.location = (0, 0, 0.0585)  # punta: justo al final del papel
    ember.scale = (r * 0.98, r * 0.98, 0.0034)
    rig['cig'] = cig
    bpy.context.view_layer.update()
    print('DEBUG cig', tuple(round(c, 4) for c in cig.matrix_world.translation), 'seam_y', round(seam_y, 4),
          [ (c.name, tuple(round(x, 4) for x in c.matrix_world.translation)) for c in cig.children][:2])
    rig['cig_rest'] = cig.rotation_euler.copy()

    # Humo: hilo continuo desde la brasa y bocanada que sale de la boca.
    bpy.context.view_layer.update()
    tip = cig.matrix_world @ Vector((0, 0, 0.06))
    bm = bmesh.new()
    bmesh.ops.create_cube(bm, size=2)
    wisp = new_mesh_obj('VOL-wisp', bm, M['wisp'], head, smooth_shade=False)
    wisp.rotation_mode = 'XYZ'
    wisp.rotation_euler = (0.15, 0.75, 0)  # arriba y hacia fuera: se ve contra el negro
    wisp.location = tip + Vector((0.075, -0.012, 0.085))
    wisp.scale = (0.04, 0.04, 0.12)
    bm = bmesh.new()
    bmesh.ops.create_cube(bm, size=2)
    puff = new_mesh_obj('VOL-puff', bm, M['puff'], head, smooth_shade=False)
    puff.rotation_mode = 'XYZ'
    rig['puff'] = puff
    rig['puff_from'] = Vector((0.004, seam_y - 0.012, MOUTH_Z + 0.004))

    # --- Corona de pinchos cromados (ref leopardo) sobre el cráneo inflado.
    C = Vector((0, 0.005, 0.215))
    for i in range(9):
        u = i / 8
        a = math.radians(-78 + 156 * u)
        d = Vector((math.sin(a), -0.18, math.cos(a))).normalized()
        h = S.toward(C, d, 0.5)
        if not h:
            continue
        p, n = h
        mid = 1 - abs(2 * u - 1)
        piv = empty(f'SPK-{i}', head, loc=p - n * 0.004, rot=along(d))
        cone(f'GEO-spike-{i}', M['chrome'], 0.07 + 0.08 * mid, 0.012 + 0.004 * mid, piv)
        rig['spikes'].append((piv, u))

    # --- Cascos de DJ blancos lacados con aro rojo, diadema por detrás de la corona.
    phones = empty('PHONES', head, loc=(0, 0.035, 0.19))
    band = base.torus_obj('GEO-phones_band', M['white_lacquer'], 0.168, 0.009, phones, arc=math.pi)
    band.rotation_euler = (math.pi / 2, 0, 0)
    for s in (-1, 1):
        cup = empty(f'CUP-{s}', phones, loc=(0.158 * s, 0, -0.01), rot=along((s, 0, 0)))
        cylinder(f'GEO-cup-{s}', M['white_lacquer'], 0.05, 0.034, cup, bevel=0.008)
        cush = cylinder(f'GEO-cushion-{s}', M['cushion'], 0.044, 0.014, cup, bevel=0.005)
        cush.location = (0, 0, -0.02)
        ring = base.torus_obj(f'GEO-cup_ring-{s}', M['red'], 0.03, 0.0035, cup)
        ring.location = (0, 0, 0.0175)
        rig['cups'].append(cup)

    # --- Tatuaje vertical "BARULLO" en la sien (como el "CHAOS" de la ref).
    h = S.toward(Vector((0, 0, 0.215)), Vector((0.93, -0.25, 0.28)), 0.5)
    if h:
        p, n = h
        cu = bpy.data.curves.new('TXT-barullo', 'FONT')
        cu.body = 'BARULLO'
        cu.size = 0.017
        cu.align_x = 'CENTER'
        cu.align_y = 'CENTER'
        cu.extrude = 0.0
        tobj = bpy.data.objects.new('TXT-barullo', cu)
        bpy.context.scene.collection.objects.link(tobj)
        bpy.context.view_layer.update()
        tme = bpy.data.meshes.new_from_object(tobj.evaluated_get(bpy.context.evaluated_depsgraph_get()))
        bpy.data.objects.remove(tobj)
        bm = bmesh.new()
        bm.from_mesh(tme)
        bmesh.ops.triangulate(bm, faces=bm.faces)
        bmesh.ops.subdivide_edges(bm, edges=bm.edges, cuts=3, use_grid_fill=True)
        # Texto en XY → vertical sobre la sien: X del texto hacia arriba, normal = n.
        up = Vector((0, 0, 1))
        xaxis = (up - n * up.dot(n)).normalized()
        yaxis = n.cross(xaxis).normalized()
        R = Matrix((xaxis, yaxis, n)).transposed().to_4x4()
        bm.transform(Matrix.Translation(p + n * 0.0006) @ R)
        tat = new_mesh_obj('GEO-tattoo', bm, M['tattoo'], head, smooth_shade=True)
        sw = tat.modifiers.new('wrap', 'SHRINKWRAP')
        sw.target = head
        sw.wrap_method = 'NEAREST_SURFACEPOINT'
        sw.offset = 0.0004

    # --- Micro-piercings en arco bajo los ojos y gotas de cristal.
    k = 0
    for s, ec in zip((-1, 1), eye_c):
        for j in range(7):
            u = j / 6
            x = ec.x + s * eye_r * (0.1 + 1.0 * u)  # solo hacia la sien, sin cruzar la nariz
            z = ec.z - eye_r * (1.15 - 0.55 * u * u)
            hit = S.front(x, z)
            if not hit or rnd.random() < 0.2:
                continue
            p, n = hit
            rr = rnd.choice((0.0009, 0.0012, 0.0016))
            o = base.sphere_obj(f'GEO-stud-{k}', M['chrome'] if rnd.random() < 0.75 else M['stud_dark'], p + n * rr * 0.4, rr, head)
            k += 1
    return rig


# ---------------------------------------------------------------- animación

# Poses clave (segundos). Todas empiezan y acaban igual: el bucle cierra.
# Párpado superior: + baja el canto delantero. -0.05 = media asta; 0.5 = cerrado contra el inferior.
LID_UP = [(0, 0.12), (1.0, 0.12), (1.9, 0.26), (2.4, 0.12), (3.3, 0.12), (3.38, 0.55), (3.48, 0.55), (3.7, 0.12),
          (4.4, -0.08), (5.4, 0.12), (6.35, 0.12), (6.43, 0.55), (6.5, 0.55), (6.76, 0.12), (8, 0.12)]
EYE_YAW = [(0, 0.0), (2.42, 0.0), (2.52, 0.45), (4.05, 0.45), (4.18, 0.0), (5.5, 0.0), (5.6, -0.45),
           (7.0, -0.45), (7.14, 0.0), (8, 0.0)]
HEAD_YAW = [(0, 0.0), (2.45, -0.025), (3.1, 0.24), (4.1, 0.22), (4.7, 0.03), (5.55, 0.0), (6.2, -0.22),
            (7.1, -0.2), (7.75, 0.0), (8, 0.0)]
HEAD_PITCH = [(0, 0.0), (1.0, 0.0), (1.9, -0.06), (2.5, -0.03), (4.0, -0.03), (4.6, -0.11), (5.5, -0.02), (8, 0.0)]
JAW = [(0, 0.06), (3.95, 0.06), (4.2, 1.0), (4.85, 0.8), (5.35, 0.06), (8, 0.06)]
EMBER = [(0, 5.0), (1.0, 5.0), (1.8, 32.0), (2.25, 12.0), (3.2, 6.0), (8, 5.0)]
CIG_TILT = [(0, 0.0), (1.0, 0.0), (1.8, -0.14), (2.4, -0.03), (4.1, 0.1), (5.3, 0.0), (8, 0.0)]


def animate(rig):
    head = rig['head']
    head.rotation_mode = 'XYZ'
    em_ember = bpy.data.materials['M_ember'].node_tree.nodes['EMIT'].inputs['Strength']
    wisp = bpy.data.materials['M_smoke_wisp'].node_tree.nodes
    puff_nodes = bpy.data.materials['M_smoke_puff'].node_tree.nodes
    puff = rig['puff']
    for f in range(1, FRAMES + 1):
        t = (f - 1) / FRAMES
        sec = t * SECONDS
        beat = (t * SECONDS * BPM / 60) % 1.0
        nod = base.kick(beat, 0.08, 0.12)

        head.rotation_euler = (-track(HEAD_PITCH, sec) + 0.012 * nod, 0.015 * math.sin(2 * math.pi * t),
                               track(HEAD_YAW, sec))
        head.keyframe_insert('rotation_euler', frame=f)

        yaw = track(EYE_YAW, sec)
        for pivot in rig['eyes']:
            pivot.rotation_mode = 'XYZ'
            pivot.rotation_euler = (0.05, 0, yaw)
            pivot.keyframe_insert('rotation_euler', frame=f)
        up = track(LID_UP, sec)
        for lid_up, lid_low in rig['lids']:
            lid_up.rotation_euler = (up, 0, 0)
            lid_up.keyframe_insert('rotation_euler', frame=f)
            # Inferior: + baja su canto delantero (-24°); al parpadear sube un poco a buscar al superior.
            lid_low.rotation_euler = (0.42 - 0.12 * smooth(0.35, 0.55, up), 0, 0)
            lid_low.keyframe_insert('rotation_euler', frame=f)

        jaw = track(JAW, sec)
        rig['jaw_key'].value = jaw
        rig['jaw_key'].keyframe_insert('value', frame=f)
        open_h = 0.0005 + 0.0055 * jaw
        rig['cavity'].scale = (0.019 + 0.003 * jaw, 0.0015, open_h)
        rig['cavity'].location = (0, 0, -open_h * 0.8)
        rig['cavity'].keyframe_insert('scale', frame=f)
        rig['cavity'].keyframe_insert('location', frame=f)
        rig['teeth_root'].scale = (1, 1, max(0.01, smooth(0.15, 0.8, jaw)))
        rig['teeth_root'].keyframe_insert('scale', frame=f)

        cig = rig['cig']
        r0 = rig['cig_rest']
        cig.rotation_euler = (r0.x + track(CIG_TILT, sec), r0.y, r0.z)
        cig.keyframe_insert('rotation_euler', frame=f)
        em_ember.default_value = track(EMBER, sec) * (1 + 0.08 * math.sin(2 * math.pi * 6 * t))
        em_ember.keyframe_insert('default_value', frame=f)

        # Hilo de humo: dos capas que suben y se funden (cierra en el bucle).
        rise = 1.6
        wisp['OFF_A'].inputs['Location'].default_value = (0, 0, -rise * t)
        wisp['OFF_B'].inputs['Location'].default_value = (0, 0, -rise * (t - 1))
        wisp['XFADE'].inputs['Factor'].default_value = t
        wisp['DENS'].inputs[1].default_value = 140.0 + 120.0 * smooth(1.6, 2.4, sec) * (1 - smooth(2.4, 4.0, sec))
        for node, inp in ((wisp['OFF_A'], 'Location'), (wisp['OFF_B'], 'Location')):
            node.inputs[inp].keyframe_insert('default_value', frame=f)
        wisp['XFADE'].inputs['Factor'].keyframe_insert('default_value', frame=f)
        wisp['DENS'].inputs[1].keyframe_insert('default_value', frame=f)

        # Bocanada: sale con la boca abierta, sube hacia su derecha y se abre.
        pt = max(0.0, min(1.0, (sec - 4.1) / 2.9))
        grow = 1 - (1 - pt) ** 2
        puff.location = rig['puff_from'] + Vector((0.14 * grow, -0.07 * grow, 0.06 * grow + 0.05 * pt * pt))
        sz = 0.014 + 0.075 * grow
        puff.scale = (sz * 1.2, sz, sz * 1.1)
        puff.rotation_euler = (0, 0.5 * grow, 0.3)
        puff.keyframe_insert('location', frame=f)
        puff.keyframe_insert('scale', frame=f)
        puff.keyframe_insert('rotation_euler', frame=f)
        env = smooth(0.0, 0.12, pt) * (1 - smooth(0.45, 1.0, pt)) if 0 < pt < 1 else 0.0
        puff_nodes['DENS'].inputs[1].default_value = 320.0 * env
        puff_nodes['DENS'].inputs[1].keyframe_insert('default_value', frame=f)
        puff_nodes['OFF_A'].inputs['Location'].default_value = (0.4 * pt, 0, -0.8 * pt)
        puff_nodes['OFF_A'].inputs['Location'].keyframe_insert('default_value', frame=f)

        # Capa secundaria: la corona ondula en cada compás, los cascos laten con el bombo.
        bar = (t * SECONDS * BPM / 60 / 4) % 1.0
        for piv, u in rig['spikes']:
            kk = base.kick(bar, 0.04 + u * 0.08, 0.05)
            piv.scale = (1 - 0.06 * kk, 1 - 0.06 * kk, 1 + 0.16 * kk)
            piv.keyframe_insert('scale', frame=f)
        for cup in rig['cups']:
            p = 1 + 0.05 * base.kick(beat, 0.03, 0.08)
            cup.scale = (p, p, 1 + 0.08 * base.kick(beat, 0.03, 0.08))
            cup.keyframe_insert('scale', frame=f)
    bpy.context.scene.frame_set(1)


# ---------------------------------------------------------------- render

def setup_render(variant, out):
    sc = bpy.context.scene
    sc.render.engine = 'BLENDER_EEVEE'
    sc.render.fps = FPS
    sc.frame_start, sc.frame_end = 1, FRAMES
    sc.render.resolution_x, sc.render.resolution_y = (1920, 824) if variant == 'wide' else (1080, 1080)
    sc.render.resolution_percentage = 100
    sc.render.film_transparent = False
    sc.render.dither_intensity = 0.0
    sc.render.image_settings.file_format = 'PNG'
    sc.render.image_settings.color_mode = 'RGB'
    sc.render.filepath = out
    sc.view_settings.view_transform = 'Standard'
    sc.view_settings.look = 'None'
    ee = sc.eevee
    for attr, val in (('taa_render_samples', 48), ('use_raytracing', True), ('use_shadows', True),
                      ('fast_gi_method', 'GLOBAL_ILLUMINATION'), ('volumetric_tile_size', '2'),
                      ('volumetric_samples', 64), ('volumetric_start', 0.5), ('volumetric_end', 3.0),
                      ('use_volumetric_shadows', True)):
        if hasattr(ee, attr):
            try:
                setattr(ee, attr, val)
            except Exception as e:  # noqa: BLE001
                print('eevee', attr, e)

    cam_d = bpy.data.cameras.new('CAM-hero')
    cam_d.lens = 70
    cam_d.sensor_fit = 'VERTICAL'
    cam_d.sensor_height = 24
    cam = link(bpy.data.objects.new('CAM-hero', cam_d))
    target = Vector((0.006, 0, 0.235))
    yaw, elev, dist = math.radians(14), math.radians(7), 1.42
    cam.location = target + Vector((math.sin(yaw) * math.cos(elev), -math.cos(yaw) * math.cos(elev), math.sin(elev))) * dist
    cam.rotation_mode = 'QUATERNION'
    cam.rotation_quaternion = (cam.location - target).to_track_quat('Z', 'Y')
    sc.camera = cam

    L = base.light
    L('LGT-key', 'AREA', (-0.5, -1.0, 0.95), (0, 0, 0.24), 16, '#FFFFFF', size=0.9, spec=0.7)
    L('LGT-fill', 'AREA', (0.8, -0.7, 0.2), (0, 0, 0.22), 4, '#EEF0FF', size=1.2, spec=0.3)
    L('LGT-rim_violet', 'AREA', (-0.7, 0.8, 0.5), (0, 0, 0.25), 26, '#8B5CFF', size=0.5)
    L('LGT-rim_red', 'AREA', (0.75, 0.75, 0.35), (0, 0, 0.22), 22, '#FF2140', size=0.5)
    L('LGT-eye_bounce', 'POINT', (0, -0.3, 0.215), (0, 0, 0.215), 0.5, '#B49BFF', size=0.05, spec=0.0)


def main():
    argv = sys.argv[sys.argv.index('--') + 1:] if '--' in sys.argv else []
    ap = argparse.ArgumentParser()
    ap.add_argument('--lib', required=True)
    ap.add_argument('--out', default='//frames/')
    ap.add_argument('--variant', default='square', choices=('square', 'wide'))
    ap.add_argument('--frames', default='')
    ap.add_argument('--save', default='')
    args, _ = ap.parse_known_args(argv)

    bpy.ops.wm.read_factory_settings(use_empty=True)
    M = materials()
    base.build_world()
    rig = build(args.lib, M)
    animate(rig)
    if '--smoke-test' in sys.argv:
        for nm in ('M_smoke_wisp', 'M_smoke_puff'):
            d = bpy.data.materials[nm].node_tree.nodes['DENS'].inputs[1]
            if d.is_property_set('default_value') or True:
                fc = bpy.data.materials[nm].node_tree.animation_data
                if fc:
                    bpy.data.materials[nm].node_tree.animation_data_clear()
                d.default_value = 600.0
        print('DEBUG smoke test, eevee', {a: getattr(bpy.context.scene.eevee, a, 'NA') for a in ('volumetric_tile_size', 'volumetric_samples', 'volumetric_start', 'volumetric_end')})
    setup_render(args.variant, args.out)
    base.setup_glare()
    if args.save:
        bpy.ops.wm.save_as_mainfile(filepath=args.save)
        print('saved', args.save)
    if args.frames:
        sc = bpy.context.scene
        for part in args.frames.split(','):
            a, _, b = part.partition('-')
            for f in range(int(a), int(b or a) + 1):
                sc.frame_set(f)
                sc.render.filepath = f'{args.out}{f:04d}'
                bpy.ops.render.render(write_still=True)
                print('frame', f, flush=True)


if __name__ == '__main__':
    main()
