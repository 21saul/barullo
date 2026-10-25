"""
El diablillo de Barullo: la mascota. Bola de cromo iridiscente con cuernos,
pinchos, ojos verdes de enfadado, piercings, un halo de cadena con espinas y
la cola en bucle con punta de flecha. Referencias en esta carpeta (ref-*.png).

Todo es procedural y depende de una fase t∈[0,1): cada fotograma se monta y se
renderiza por separado, así el bucle cierra perfecto y se puede reanudar.

  blender.exe -b --factory-startup -t 6 --python diablillo.py -- \
      frames=0-119 res=900 samples=96 out=C:/Users/Veintiuno/barullo-render/diablillo/f_

Argumentos: frames=a-b (o un número), res, samples, out, device=CPU|GPU,
total=120 (fotogramas del bucle), cam=front|three, bg=0|1 (fondo negro opaco
en vez de transparente), blend=ruta.blend (guarda la escena del primer frame).
"""
import bpy, bmesh, math, sys, os, time
from mathutils import Vector, Matrix, Euler, noise

ARGS = dict(a.split("=", 1) for a in (sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []))
TOTAL = int(ARGS.get("total", 120))
RES = int(ARGS.get("res", 900))
SAMPLES = int(ARGS.get("samples", 96))
OUT = ARGS.get("out", "C:/Users/Veintiuno/barullo-render/diablillo/test_")
DEVICE = ARGS.get("device", "CPU")
BG = ARGS.get("bg", "0") == "1"
CAM = ARGS.get("cam", "front")
fr = ARGS.get("frames", "0")
FRAMES = list(range(int(fr.split("-")[0]), int(fr.split("-")[1]) + 1)) if "-" in fr else [int(fr)]

TAU = math.tau

# ---------------------------------------------------------------- escena base
bpy.ops.wm.read_factory_settings(use_empty=True)
scn = bpy.context.scene
scn.render.engine = "CYCLES"
cy = scn.cycles
cy.device = DEVICE
if DEVICE == "GPU":
    prefs = bpy.context.preferences.addons["cycles"].preferences
    for kind in ("HIP", "ONEAPI", "CUDA", "OPTIX"):
        try:
            prefs.compute_device_type = kind
            prefs.get_devices()
            if any(d.type == kind for d in prefs.devices):
                for d in prefs.devices:
                    d.use = d.type == kind
                break
        except TypeError:
            pass
cy.samples = SAMPLES
cy.use_adaptive_sampling = True
cy.adaptive_threshold = 0.01
cy.use_denoising = True
cy.denoiser = "OPENIMAGEDENOISE"
cy.max_bounces = 12
cy.glossy_bounces = 10
cy.transmission_bounces = 8
cy.caustics_reflective = False
cy.caustics_refractive = False
cy.blur_glossy = 0.5
scn.render.resolution_x = scn.render.resolution_y = RES
scn.render.film_transparent = not BG
scn.render.image_settings.file_format = "PNG"
scn.render.image_settings.color_mode = "RGBA"
scn.render.image_settings.color_depth = "16"
vs = scn.view_settings
vs.view_transform = "AgX"
for look in ("AgX - Punchy", "Punchy", "AgX - Medium High Contrast", "Medium High Contrast"):
    try:
        vs.look = look
        break
    except TypeError:
        pass
vs.exposure = float(ARGS.get("exposure", 0.0))

world = bpy.data.worlds.new("w")
scn.world = world
world.use_nodes = True
wbg = world.node_tree.nodes["Background"]
wbg.inputs[0].default_value = (0.004, 0.004, 0.006, 1)
wbg.inputs[1].default_value = 1.0


# ------------------------------------------------------------- materiales
# Acabado. «satin» (por defecto desde el 22/10): la pieza tiene color propio,
# opaco y perlado, con un barniz brillante encima; el espejo puro («mirror»,
# la primera versión) deslumbraba y costaba leer la forma.
SATIN = ARGS.get("finish", "satin") == "satin"


def principled(name, color, metallic=1.0, rough=0.06, coat=0.0, film=0.0, film_ior=1.45,
               emission=None, estr=0.0, spec_tint=None, micro=0.0, micro_scale=60.0, trans=0.0, ior=1.5):
    m = bpy.data.materials.new(name)
    m.use_nodes = True
    nt = m.node_tree
    p = nt.nodes["Principled BSDF"]
    p.inputs["Base Color"].default_value = (*color, 1)
    p.inputs["Metallic"].default_value = metallic
    p.inputs["Roughness"].default_value = rough
    p.inputs["IOR"].default_value = ior
    if trans:
        p.inputs["Transmission Weight"].default_value = trans
    if coat:
        p.inputs["Coat Weight"].default_value = coat
        p.inputs["Coat Roughness"].default_value = 0.02
    if film and "Thin Film Thickness" in p.inputs:
        p.inputs["Thin Film Thickness"].default_value = film
        p.inputs["Thin Film IOR"].default_value = film_ior
    if spec_tint is not None:
        p.inputs["Specular Tint"].default_value = (*spec_tint, 1)
    if emission is not None:
        p.inputs["Emission Color"].default_value = (*emission, 1)
        p.inputs["Emission Strength"].default_value = estr
    if micro:
        # Superficie de objeto real: manchas de roce que cambian la rugosidad
        # y una piel de naranja finísima en el relieve.
        tc = nt.nodes.new("ShaderNodeTexCoord")
        n1 = nt.nodes.new("ShaderNodeTexNoise")
        n1.inputs["Scale"].default_value = micro_scale * 0.12
        n1.inputs["Detail"].default_value = 6
        n1.inputs["Roughness"].default_value = 0.6
        nt.links.new(tc.outputs["Object"], n1.inputs["Vector"])
        ramp = nt.nodes.new("ShaderNodeMapRange")
        ramp.inputs["From Min"].default_value = 0.45
        ramp.inputs["From Max"].default_value = 0.75
        ramp.inputs["To Min"].default_value = rough
        ramp.inputs["To Max"].default_value = rough + micro
        nt.links.new(n1.outputs["Fac"], ramp.inputs["Value"])
        # arañazos: ruido estirado en una dirección, umbral fino
        mp = nt.nodes.new("ShaderNodeMapping")
        mp.inputs["Scale"].default_value = (1.0, 1.0, 38.0)
        mp.inputs["Rotation"].default_value = (0.4, 0.9, 0.2)
        nt.links.new(tc.outputs["Object"], mp.inputs["Vector"])
        n2 = nt.nodes.new("ShaderNodeTexNoise")
        n2.inputs["Scale"].default_value = micro_scale * 0.5
        n2.inputs["Detail"].default_value = 2
        nt.links.new(mp.outputs["Vector"], n2.inputs["Vector"])
        sc = nt.nodes.new("ShaderNodeMapRange")
        sc.inputs["From Min"].default_value = 0.70
        sc.inputs["From Max"].default_value = 0.74
        sc.inputs["To Min"].default_value = 0.0
        sc.inputs["To Max"].default_value = micro * 0.9
        nt.links.new(n2.outputs["Fac"], sc.inputs["Value"])
        add = nt.nodes.new("ShaderNodeMath")
        add.operation = "ADD"
        add.use_clamp = True
        nt.links.new(ramp.outputs["Result"], add.inputs[0])
        nt.links.new(sc.outputs["Result"], add.inputs[1])
        nt.links.new(add.outputs[0], p.inputs["Roughness"])
        n3 = nt.nodes.new("ShaderNodeTexNoise")
        n3.inputs["Scale"].default_value = micro_scale * 4
        n3.inputs["Detail"].default_value = 3
        nt.links.new(tc.outputs["Object"], n3.inputs["Vector"])
        bump = nt.nodes.new("ShaderNodeBump")
        bump.inputs["Strength"].default_value = 0.035
        bump.inputs["Distance"].default_value = 0.002
        nt.links.new(n3.outputs["Fac"], bump.inputs["Height"])
        nt.links.new(bump.outputs["Normal"], p.inputs["Normal"])
    return m


def mat_head():
    """Cromo con película fina: rosa-rojo arriba, plata al centro y verdoso por
    debajo, como en la referencia. El color base va por la altura del objeto."""
    if SATIN:
        m = principled("chrome_head", (0.95, 0.75, 0.8), metallic=float(ARGS.get("hmetal", 0.75)),
                       rough=float(ARGS.get("hrough", 0.16)), coat=1.0,
                       film=float(ARGS.get("film", 300)), film_ior=1.5, micro=0.06)
    else:
        m = principled("chrome_head", (0.95, 0.75, 0.8), rough=0.045, film=float(ARGS.get("film", 380)),
                       film_ior=1.6, micro=0.07)
    nt = m.node_tree
    p = nt.nodes["Principled BSDF"]
    tc = nt.nodes.new("ShaderNodeTexCoord")
    sep = nt.nodes.new("ShaderNodeSeparateXYZ")
    nt.links.new(tc.outputs["Object"], sep.inputs[0])
    ramp = nt.nodes.new("ShaderNodeValToRGB")
    cr = ramp.color_ramp
    cr.interpolation = "EASE"
    cr.elements[0].position = 0.0
    cr.elements[0].color = (0.95, 0.97, 0.97, 1)   # base casi plata
    cr.elements[1].position = 0.5
    cr.elements[1].color = (0.97, 0.95, 0.96, 1)   # plata
    e = cr.elements.new(0.85)
    e.color = (1.0, 0.32, 0.45, 1)                  # rosa-rojo de la coronilla
    mr = nt.nodes.new("ShaderNodeMapRange")
    mr.inputs["From Min"].default_value = -1.0
    mr.inputs["From Max"].default_value = 1.0
    nt.links.new(sep.outputs["Z"], mr.inputs["Value"])
    nt.links.new(mr.outputs["Result"], ramp.inputs["Fac"])
    nt.links.new(ramp.outputs["Color"], p.inputs["Base Color"])
    return m


MAT = {}


def build_materials():
    MAT["head"] = mat_head()
    if SATIN:
        MAT["horn"] = principled("chrome_red", (0.9, 0.08, 0.12), metallic=0.75, rough=0.16, coat=1.0, micro=0.05)
        MAT["chrome"] = principled("chrome", (0.9, 0.88, 0.9), rough=0.16, film=200, micro=0.06)
        MAT["pink"] = principled("chrome_pink", (1.0, 0.45, 0.58), metallic=0.4, rough=0.25, coat=1.0, micro=0.05)
    else:
        MAT["horn"] = principled("chrome_red", (1.0, 0.16, 0.2), rough=0.05, film=260, film_ior=1.5, micro=0.05)
        MAT["chrome"] = principled("chrome", (0.95, 0.93, 0.95), rough=0.035, film=300, micro=0.05)
        MAT["pink"] = principled("chrome_pink", (1.0, 0.5, 0.62), rough=0.06, film=320, micro=0.05)
    MAT["gold"] = principled("gold_rose", (1.0, 0.62, 0.42), rough=0.08, micro=0.04)
    MAT["orange"] = principled("ring_orange", (1.0, 0.35, 0.05), rough=0.1, coat=1.0)
    # cadena del halo: rojo caramelo sobre oro, como la ref de la cadena
    MAT["chain"] = principled("chain_candy", (1.0, 0.18, 0.04), rough=0.12, coat=1.0, film=500, micro=0.08,
                              micro_scale=30)
    MAT["thorn"] = principled("thorn", (1.0, 0.42, 0.12), rough=0.15, coat=1.0)
    # ojo: canica verde de cristal con iris interior
    MAT["eye"] = mat_eye()
    MAT["mouth"] = principled("mouth", (0.02, 0.0, 0.005), metallic=0.0, rough=0.35)
    MAT["tongue"] = principled("tongue", (0.5, 0.02, 0.06), metallic=0.0, rough=0.2, coat=1.0)
    MAT["fang"] = principled("fang", (0.95, 0.93, 0.88), metallic=0.0, rough=0.12, coat=1.0)


def mat_eye():
    m = bpy.data.materials.new("eye")
    m.use_nodes = True
    nt = m.node_tree
    p = nt.nodes["Principled BSDF"]
    p.inputs["Metallic"].default_value = 0.0
    p.inputs["Roughness"].default_value = 0.08
    p.inputs["Coat Weight"].default_value = 1.0
    p.inputs["Coat Roughness"].default_value = 0.0
    p.inputs["Coat IOR"].default_value = 1.6
    # el ojo mira por su eje -Y local: distancia radial en XZ → iris/pupila
    tc = nt.nodes.new("ShaderNodeTexCoord")
    sep = nt.nodes.new("ShaderNodeSeparateXYZ")
    nt.links.new(tc.outputs["Object"], sep.inputs[0])
    sx = nt.nodes.new("ShaderNodeMath"); sx.operation = "MULTIPLY"
    sz = nt.nodes.new("ShaderNodeMath"); sz.operation = "MULTIPLY"
    nt.links.new(sep.outputs["X"], sx.inputs[0]); nt.links.new(sep.outputs["X"], sx.inputs[1])
    nt.links.new(sep.outputs["Z"], sz.inputs[0]); nt.links.new(sep.outputs["Z"], sz.inputs[1])
    ad = nt.nodes.new("ShaderNodeMath"); ad.operation = "ADD"
    nt.links.new(sx.outputs[0], ad.inputs[0]); nt.links.new(sz.outputs[0], ad.inputs[1])
    sq = nt.nodes.new("ShaderNodeMath"); sq.operation = "SQRT"
    nt.links.new(ad.outputs[0], sq.inputs[0])
    # textura radial del iris
    nz = nt.nodes.new("ShaderNodeTexNoise")
    nz.inputs["Scale"].default_value = 30
    nz.inputs["Detail"].default_value = 4
    nt.links.new(tc.outputs["Object"], nz.inputs["Vector"])
    mix_r = nt.nodes.new("ShaderNodeMath"); mix_r.operation = "MULTIPLY_ADD"
    nt.links.new(nz.outputs["Fac"], mix_r.inputs[0])
    mix_r.inputs[1].default_value = 0.025
    nt.links.new(sq.outputs[0], mix_r.inputs[2])
    ramp = nt.nodes.new("ShaderNodeValToRGB")
    cr = ramp.color_ramp
    cr.interpolation = "EASE"
    cr.elements[0].position = 0.0
    cr.elements[0].color = (0.005, 0.03, 0.005, 1)   # pupila
    cr.elements[1].position = 0.2
    cr.elements[1].color = (0.01, 0.12, 0.01, 1)
    for pos, col in ((0.27, (0.08, 0.6, 0.03, 1)), (0.45, (0.3, 1.0, 0.06, 1)), (0.6, (0.12, 0.6, 0.03, 1)),
                     (0.66, (0.02, 0.15, 0.01, 1)), (0.71, (0.95, 0.95, 0.82, 1)), (1.0, (1.0, 0.93, 0.72, 1))):
        e = cr.elements.new(pos); e.color = col
    mr = nt.nodes.new("ShaderNodeMapRange")
    mr.inputs["From Min"].default_value = 0.0
    mr.inputs["From Max"].default_value = 0.33
    nt.links.new(mix_r.outputs[0], mr.inputs["Value"])
    nt.links.new(mr.outputs["Result"], ramp.inputs["Fac"])
    nt.links.new(ramp.outputs["Color"], p.inputs["Base Color"])
    # brillo propio leve del verde (los ojos de la ref casi emiten)
    p.inputs["Emission Color"].default_value = (0.1, 0.9, 0.05, 1)
    em = nt.nodes.new("ShaderNodeMath"); em.operation = "LESS_THAN"
    em.inputs[1].default_value = 0.19
    nt.links.new(mix_r.outputs[0], em.inputs[0])
    emk = nt.nodes.new("ShaderNodeMath"); emk.operation = "MULTIPLY"
    emk.inputs[1].default_value = float(ARGS.get("eyeglow", 0.35))
    nt.links.new(em.outputs[0], emk.inputs[0])
    nt.links.new(emk.outputs[0], p.inputs["Emission Strength"])
    return m


# ------------------------------------------------------------- geometría
COL = None


def link(obj):
    COL.objects.link(obj)
    return obj


def mesh_obj(name, bm, mat, smooth=True, subsurf=0, parent=None):
    me = bpy.data.meshes.new(name)
    bm.to_mesh(me)
    bm.free()
    if smooth:
        for poly in me.polygons:
            poly.use_smooth = True
    ob = bpy.data.objects.new(name, me)
    link(ob)
    me.materials.append(mat)
    if subsurf:
        md = ob.modifiers.new("ss", "SUBSURF")
        md.levels = md.render_levels = subsurf
    if parent:
        ob.parent = parent
    return ob


def uv_sphere(name, mat, radius=1.0, seg=64, rings=32, scale=(1, 1, 1), loc=(0, 0, 0), parent=None, subsurf=0):
    bm = bmesh.new()
    bmesh.ops.create_uvsphere(bm, u_segments=seg, v_segments=rings, radius=radius)
    ob = mesh_obj(name, bm, mat, subsurf=subsurf, parent=parent)
    ob.scale = scale
    ob.location = loc
    return ob


def torus_bm(R, r, seg=48, rs=16, sx=1.0):
    bm = bmesh.new()
    verts = []
    for i in range(seg):
        a = TAU * i / seg
        c = Vector((math.cos(a) * sx, math.sin(a), 0))
        row = []
        for j in range(rs):
            b = TAU * j / rs
            n = Vector((math.cos(a) * math.cos(b), math.sin(a) * math.cos(b), math.sin(b)))
            p = Vector((math.cos(a) * (R * sx) , math.sin(a) * R, 0)) + n * r
            row.append(bm.verts.new(p))
        verts.append(row)
    for i in range(seg):
        for j in range(rs):
            bm.faces.new((verts[i][j], verts[(i + 1) % seg][j], verts[(i + 1) % seg][(j + 1) % rs], verts[i][(j + 1) % rs]))
    return bm


def tube_bm(pts, radii, rs=20, cap_start=True, cap_end=True):
    """Tubo a lo largo de una polilínea con transporte paralelo del marco.
    Radio 0 al final = punta cerrada en un vértice."""
    bm = bmesh.new()
    n = len(pts)
    tangents = []
    for i in range(n):
        a = pts[max(i - 1, 0)]
        b = pts[min(i + 1, n - 1)]
        tangents.append((b - a).normalized())
    t0 = tangents[0]
    ref = Vector((0, 0, 1)) if abs(t0.z) < 0.9 else Vector((1, 0, 0))
    u = t0.cross(ref).normalized()
    rings = []
    tip = None
    for i in range(n):
        t = tangents[i]
        if i:
            u = (u - t * u.dot(t)).normalized()
        v = t.cross(u)
        if radii[i] <= 1e-5:
            tip = bm.verts.new(pts[i])
            break
        ring = [bm.verts.new(pts[i] + (u * math.cos(TAU * j / rs) + v * math.sin(TAU * j / rs)) * radii[i])
                for j in range(rs)]
        rings.append(ring)
    for a, b in zip(rings, rings[1:]):
        for j in range(rs):
            bm.faces.new((a[j], a[(j + 1) % rs], b[(j + 1) % rs], b[j]))
    if tip is not None:
        last = rings[-1]
        for j in range(rs):
            bm.faces.new((last[j], last[(j + 1) % rs], tip))
    elif cap_end:
        c = bm.verts.new(pts[len(rings) - 1])
        last = rings[-1]
        for j in range(rs):
            bm.faces.new((last[j], last[(j + 1) % rs], c))
    if cap_start:
        c = bm.verts.new(pts[0])
        first = rings[0]
        for j in range(rs):
            bm.faces.new((first[(j + 1) % rs], first[j], c))
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    return bm


def bezier(p0, p1, p2, p3, n):
    out = []
    for i in range(n):
        s = i / (n - 1)
        out.append(p0 * (1 - s) ** 3 + p1 * 3 * (1 - s) ** 2 * s + p2 * 3 * (1 - s) * s ** 2 + p3 * s ** 3)
    return out


def catmull(ctrl, per=16, closed=False):
    pts = []
    m = len(ctrl)
    rng = range(m) if closed else range(m - 1)
    for i in rng:
        p0 = ctrl[(i - 1) % m] if closed else ctrl[max(i - 1, 0)]
        p1 = ctrl[i % m]
        p2 = ctrl[(i + 1) % m] if closed else ctrl[min(i + 1, m - 1)]
        p3 = ctrl[(i + 2) % m] if closed else ctrl[min(i + 2, m - 1)]
        for k in range(per):
            s = k / per
            s2, s3 = s * s, s * s * s
            pts.append(0.5 * ((2 * p1) + (-p0 + p2) * s + (2 * p0 - 5 * p1 + 4 * p2 - p3) * s2 + (-p0 + 3 * p1 - 3 * p2 + p3) * s3))
    if not closed:
        pts.append(ctrl[-1].copy())
    return pts


def on_head(theta_deg, phi_deg, r=1.0):
    """Punto de la esfera: theta = azimut desde el frente (-Y) hacia +X,
    phi = elevación."""
    th, ph = math.radians(theta_deg), math.radians(phi_deg)
    return Vector((math.sin(th) * math.cos(ph), -math.cos(th) * math.cos(ph), math.sin(ph))) * r


def look_rot(direction, up=Vector((0, 0, 1))):
    """Rotación que lleva -Y local a `direction` (los objetos «miran» por -Y)."""
    d = direction.normalized()
    return (-d).to_track_quat("Y", "Z").to_euler()


# ----------------------------------------------------------------- montaje
def build():
    global COL
    COL = scn.collection
    build_materials()
    rig = bpy.data.objects.new("head_rig", None)
    link(rig)

    head = uv_sphere("head", MAT["head"], seg=96, rings=48, parent=rig)

    # cuernos: cono curvo que sale del lateral alto, abre y vuelve hacia dentro
    for side in (-1, 1):
        base = on_head(side * 62, 30, 0.82)
        p0 = base
        p1 = base + Vector((side * 0.40, 0.05, 0.22))
        p2 = base + Vector((side * 0.46, 0.08, 0.72))
        p3 = base + Vector((side * 0.16, 0.12, 1.02))
        pts = bezier(p0, p1, p2, p3, 40)
        radii = [0.38 * (1 - i / 39) ** 1.25 for i in range(40)]
        radii[-1] = 0
        mesh_obj(f"horn_{side}", tube_bm(pts, radii, rs=32, cap_end=False), MAT["horn"], subsurf=1, parent=rig)

    # pinchos de la coronilla: dos pares hacia el frente
    for th, ph, h in ((-28, 52, 0.30), (-12, 66, 0.24), (12, 66, 0.24), (28, 52, 0.30)):
        base = on_head(th, ph, 0.95)
        nrm = base.normalized()
        pts = [base + nrm * (h * i / 16) for i in range(17)]
        radii = [0.085 * (1 - i / 16) ** 1.3 for i in range(17)]
        radii[-1] = 0
        mesh_obj("spike", tube_bm(pts, radii, rs=24, cap_end=False), MAT["chrome"], subsurf=1, parent=rig)

    # ojos: canica + párpado de cromo cortado en diagonal (cejo fruncido)
    eyes = []
    for side in (-1, 1):
        c = on_head(side * 30, -10, 0.79)
        eye_rig = bpy.data.objects.new(f"eye_rig_{side}", None)
        link(eye_rig)
        eye_rig.parent = rig
        eye_rig.location = c
        eye_rig.rotation_euler = look_rot(c.normalized() * 0.55 + Vector((0, -0.45, 0)))
        ball = uv_sphere(f"eye_{side}", MAT["eye"], radius=0.33, seg=64, rings=32, parent=eye_rig)
        ball.scale = (1.0, 0.9, 0.86)
        # párpado: casquete de esfera algo mayor que la canica, cortado por un plano inclinado
        bm = bmesh.new()
        bmesh.ops.create_uvsphere(bm, u_segments=64, v_segments=32, radius=0.357)
        ang = math.radians(side * 26)  # ceño: el lado de la nariz más bajo
        nrm = Vector((math.sin(ang), 0.0, -math.cos(ang)))
        res = bmesh.ops.bisect_plane(bm, geom=bm.verts[:] + bm.edges[:] + bm.faces[:], dist=1e-5,
                                     plane_co=Vector((0, 0, 0.1)), plane_no=nrm, clear_outer=True)
        lid = mesh_obj(f"lid_{side}", bm, MAT["head"], parent=eye_rig)
        lid.scale = (1.06, 0.95, 0.92)
        sol = lid.modifiers.new("sol", "SOLIDIFY")
        sol.thickness = 0.05
        sol.offset = 1
        md = lid.modifiers.new("ss", "SUBSURF")
        md.levels = md.render_levels = 2
        # párpado inferior pequeño, recto
        bm = bmesh.new()
        bmesh.ops.create_uvsphere(bm, u_segments=64, v_segments=32, radius=0.354)
        bmesh.ops.bisect_plane(bm, geom=bm.verts[:] + bm.edges[:] + bm.faces[:], dist=1e-5,
                               plane_co=Vector((0, 0, -0.22)), plane_no=Vector((0, 0, 1)), clear_outer=True)
        low = mesh_obj(f"lowlid_{side}", bm, MAT["head"], parent=eye_rig)
        low.scale = (1.05, 0.95, 0.92)
        sol = low.modifiers.new("sol", "SOLIDIFY")
        sol.thickness = 0.022
        sol.offset = 1
        md = low.modifiers.new("ss", "SUBSURF")
        md.levels = md.render_levels = 2
        eyes.append((side, eye_rig, ball, lid))

    # nariz: botoncito con argolla
    nose = on_head(0, -16, 0.99)
    uv_sphere("nose", MAT["head"], radius=0.065, loc=nose, parent=rig, scale=(1.1, 0.8, 0.9))
    ring = mesh_obj("nose_ring", torus_bm(0.045, 0.009, 32, 12), MAT["chrome"], parent=rig)
    ring.location = nose + Vector((0, -0.045, -0.04))
    ring.rotation_euler = (math.radians(70), 0, 0)

    # boca: «o» abierta con labio de cromo, lengua y un colmillo
    mc = on_head(0, -30, 0.95)
    mouth = uv_sphere("mouth", MAT["mouth"], radius=0.15, loc=mc, parent=rig, scale=(1.0, 0.5, 0.62))
    mouth.rotation_euler = (math.radians(-30), 0, 0)
    uv_sphere("tongue", MAT["tongue"], radius=0.08, loc=mc + Vector((0.0, -0.02, -0.045)), parent=rig,
              scale=(1.0, 0.6, 0.45))
    lip = mesh_obj("lip", torus_bm(0.145, 0.032, 64, 20, sx=1.0), MAT["head"], parent=rig)
    lip.location = mc + Vector((0, -0.035, 0))
    lip.rotation_euler = (math.radians(90 - 30), 0, 0)
    lip.scale = (1.0, 0.66, 1.0)
    fang_base = mc + Vector((0.055, -0.07, 0.065))
    pts = [fang_base + Vector((0.0, -0.01 * i / 10, -0.11 * i / 10)) for i in range(11)]
    rad = [0.032 * (1 - i / 10) ** 0.9 for i in range(11)]
    rad[-1] = 0
    mesh_obj("fang", tube_bm(pts, rad, rs=16, cap_start=True, cap_end=False), MAT["fang"], subsurf=1, parent=rig)

    # piercings de la ceja derecha: argolla + tres bolitas
    for i, (th, ph) in enumerate(((38, 16), (42, 8), (45, 0))):
        uv_sphere(f"stud_{i}", MAT["gold"], radius=0.028, loc=on_head(th, ph, 1.005), parent=rig)
    br = on_head(30, 22, 0.98)
    ring2 = mesh_obj("brow_ring", torus_bm(0.07, 0.013, 40, 14), MAT["chrome"], parent=rig)
    ring2.location = br + br.normalized() * 0.02
    ring2.rotation_euler = look_rot(Vector((0.6, 0.0, 0.8)))
    uv_sphere("brow_bead", MAT["pink"], radius=0.024, loc=ring2.location + Vector((0.0, -0.05, -0.05)), parent=rig)

    # halo de cadena con espinas
    halo = bpy.data.objects.new("halo", None)
    link(halo)
    N = 30
    R = 0.62
    link_bm = torus_bm(0.064, 0.027, 40, 14, sx=1.7)
    me = bpy.data.meshes.new("chainlink")
    link_bm.to_mesh(me)
    link_bm.free()
    for poly in me.polygons:
        poly.use_smooth = True
    me.materials.append(MAT["chain"])
    thorn_bm = tube_bm([Vector((0, 0, z * 0.011)) for z in range(11)],
                       [0.017 * (1 - i / 10) ** 1.2 for i in range(10)] + [0], rs=12, cap_end=False)
    th_me = bpy.data.meshes.new("thorn")
    thorn_bm.to_mesh(th_me)
    thorn_bm.free()
    for poly in th_me.polygons:
        poly.use_smooth = True
    th_me.materials.append(MAT["thorn"])
    for i in range(N):
        a = TAU * i / N
        ob = bpy.data.objects.new(f"link_{i}", me)
        link(ob)
        ob.parent = halo
        ob.location = (R * math.cos(a), R * math.sin(a), 0)
        # eslabón tangente al aro; uno sí, uno no girado 90° sobre su eje
        ob.rotation_euler = Euler((math.pi / 2 if i % 2 else 0.0, 0, a + math.pi / 2), "ZYX")
        ob.rotation_mode = "ZYX"
        ob.rotation_euler = (math.pi / 2 if i % 2 else 0.0, 0, a + math.pi / 2)
        # espinas hacia fuera, arriba y abajo según el eslabón
        dirs = [Vector((math.cos(a), math.sin(a), 0.25)), Vector((0.2 * math.cos(a), 0.2 * math.sin(a), 1))] if i % 2 \
            else [Vector((math.cos(a + 0.1), math.sin(a + 0.1), -0.35)), Vector((-math.cos(a), -math.sin(a), 0.5))]
        for d in dirs:
            t = bpy.data.objects.new("thorn", th_me)
            link(t)
            t.parent = halo
            d = d.normalized()
            t.location = Vector(ob.location) + d * 0.045
            t.rotation_euler = d.to_track_quat("Z", "Y").to_euler()
    # cola
    tail = {"obj": None}
    return dict(rig=rig, eyes=eyes, halo=halo, tail=tail)


# -------------------------------------------------------------- la cola
def tail_curve(t):
    """Puntos de control de la cola en la fase t. Sale por detrás a la derecha,
    rodea la cabeza por delante en un lazo bajo y cruza en diagonal hacia
    abajo a la izquierda, donde acaba en la flecha."""
    ctrl = [
        Vector((0.35, 0.75, -0.6)),
        Vector((1.0, 0.55, -0.66)),
        Vector((1.5, -0.05, -0.78)),
        Vector((1.3, -0.8, -0.98)),
        Vector((0.35, -1.15, -1.12)),
        Vector((-0.75, -1.05, -1.06)),
        Vector((-1.5, -0.5, -0.92)),
        Vector((-1.4, 0.3, -0.84)),
        Vector((-0.55, 0.35, -0.95)),
        Vector((0.35, -0.25, -1.18)),
        Vector((0.15, -1.15, -1.45)),
        Vector((-0.5, -1.25, -1.72)),
        Vector((-0.92, -1.05, -1.95)),
    ]
    n = len(ctrl)
    out = []
    for i, c in enumerate(ctrl):
        s = i / (n - 1)
        amp = 0.02 + 0.16 * s ** 1.4  # la raíz casi quieta, la punta latiguea
        ph = TAU * t - s * 3.4
        out.append(c + Vector((math.sin(ph) * amp, math.cos(ph * 1.0 + 0.6) * amp * 0.5, math.sin(ph + 1.1) * amp * 0.7)))
    return out


def build_tail(state, t):
    for o in list(scn.objects):
        if o.name.startswith(("tail", "arrow", "washer", "oring")):
            bpy.data.objects.remove(o, do_unlink=True)
    pts = catmull(tail_curve(t), per=14)
    n = len(pts)
    radii = [0.085 - 0.025 * (i / (n - 1)) for i in range(n)]
    tail = mesh_obj("tail", tube_bm(pts, radii, rs=24), MAT["chrome"], subsurf=1)
    end = pts[-1]
    tang = (pts[-1] - pts[-4]).normalized()
    q = tang.to_track_quat("Z", "Y")
    # arandela y anilla naranja
    w = mesh_obj("washer", torus_bm(0.065, 0.03, 40, 14), MAT["pink"])
    w.location = end - tang * 0.18
    w.rotation_euler = q.to_euler()
    w.scale = (1, 1, 1.6)
    o = mesh_obj("oring", torus_bm(0.085, 0.012, 40, 12), MAT["orange"])
    o.location = end - tang * 0.03
    o.rotation_euler = (q @ Euler((0.5, 0.3, 0)).to_quaternion()).to_euler()
    # punta de flecha: pirámide aplanada de cuatro caras con la base escotada
    bm = bmesh.new()
    L, W, H = 0.72, 0.4, 0.09
    tip = bm.verts.new((0, 0, L))
    back = bm.verts.new((0, 0, 0.08))
    l = bm.verts.new((-W, 0, 0))
    r = bm.verts.new((W, 0, 0))
    up = bm.verts.new((0, H, 0.16))
    dn = bm.verts.new((0, -H, 0.16))
    for f in ((tip, l, up), (tip, up, r), (tip, r, dn), (tip, dn, l), (back, up, l), (back, r, up), (back, dn, r), (back, l, dn)):
        bm.faces.new(f)
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    a = mesh_obj("arrow", bm, MAT["horn"], smooth=False)
    bev = a.modifiers.new("bev", "BEVEL")
    bev.width = 0.02
    bev.segments = 4
    a.location = end - tang * 0.02
    a.rotation_euler = (q @ Euler((0, 0, math.radians(20) + 0.25 * math.sin(TAU * t))).to_quaternion()).to_euler()
    # La cola reflejada en la cara de cromo se leía como si se viera a través
    # de la cabeza (feedback 2026-10-22): fuera de los rayos de reflejo.
    for ob in (tail, w, o, a):
        ob.visible_glossy = False


# ------------------------------------------------------------- iluminación
def emitter(name, size, loc, color, strength, look_at=(0, 0, 0), soft=0.0):
    """Plano emisor invisible para la cámara. `soft` > 0 apaga los bordes con un
    degradado radial: en el cromo se lee como una mancha de luz, no un cuadro."""
    bpy.ops.mesh.primitive_plane_add(size=1)
    ob = bpy.context.active_object
    ob.name = name
    ob.scale = (size[0], size[1], 1)
    ob.location = loc
    d = Vector(look_at) - Vector(loc)
    ob.rotation_euler = d.to_track_quat("-Z", "Y").to_euler()
    m = bpy.data.materials.new(name)
    m.use_nodes = True
    nt = m.node_tree
    nt.nodes.remove(nt.nodes["Principled BSDF"])
    em = nt.nodes.new("ShaderNodeEmission")
    em.inputs[0].default_value = (*color, 1)
    em.inputs[1].default_value = strength
    if soft:
        tc = nt.nodes.new("ShaderNodeTexCoord")
        gr = nt.nodes.new("ShaderNodeTexGradient")
        gr.gradient_type = "SPHERICAL"
        mp = nt.nodes.new("ShaderNodeMapping")
        mp.inputs["Scale"].default_value = (2.0, 2.0, 1.0)
        nt.links.new(tc.outputs["Object"], mp.inputs["Vector"])
        nt.links.new(mp.outputs["Vector"], gr.inputs["Vector"])
        pw = nt.nodes.new("ShaderNodeMath"); pw.operation = "POWER"
        pw.inputs[1].default_value = soft
        nt.links.new(gr.outputs["Fac"], pw.inputs[0])
        mul = nt.nodes.new("ShaderNodeMath"); mul.operation = "MULTIPLY"
        mul.inputs[1].default_value = strength
        nt.links.new(pw.outputs[0], mul.inputs[0])
        nt.links.new(mul.outputs[0], em.inputs[1])
    nt.links.new(em.outputs[0], nt.nodes["Material Output"].inputs[0])
    ob.data.materials.append(m)
    ob.visible_camera = False
    ob.visible_shadow = False
    return ob


HDRI = "C:/Users/Veintiuno/barullo-render/diablillo/" + ARGS.get("hdri", "studio_small_09") + ".hdr"


def lights():
    k = float(ARGS.get("light", 0.8 if SATIN else 1.0))
    # Entorno: un estudio real (HDRI) teñido por altura —magenta-rojo arriba,
    # rosa pálido al centro, verde agua abajo—, que es lo que pinta la bola de
    # la ref. Fuera de cámara: el fondo sale transparente.
    nt = scn.world.node_tree
    tc = nt.nodes.new("ShaderNodeTexCoord")
    mp = nt.nodes.new("ShaderNodeMapping")
    mp.inputs["Rotation"].default_value = (0, 0, math.radians(float(ARGS.get("hrot", 140))))
    nt.links.new(tc.outputs["Generated"], mp.inputs["Vector"])
    env = nt.nodes.new("ShaderNodeTexEnvironment")
    env.image = bpy.data.images.load(HDRI)
    nt.links.new(mp.outputs["Vector"], env.inputs["Vector"])
    sep = nt.nodes.new("ShaderNodeSeparateXYZ")
    nt.links.new(tc.outputs["Generated"], sep.inputs[0])
    ramp = nt.nodes.new("ShaderNodeValToRGB")
    cr = ramp.color_ramp
    cr.interpolation = "EASE"
    cr.elements[0].position = 0.0
    cr.elements[0].color = (0.45, 0.95, 0.82, 1)
    cr.elements[1].position = 0.75
    cr.elements[1].color = (1.0, 0.12, 0.3, 1)
    e = cr.elements.new(0.3); e.color = (1.0, 0.92, 0.94, 1)
    zr = nt.nodes.new("ShaderNodeMapRange")
    zr.inputs["From Min"].default_value = -1.0
    nt.links.new(sep.outputs["Z"], zr.inputs["Value"])
    nt.links.new(zr.outputs["Result"], ramp.inputs["Fac"])
    mix = nt.nodes.new("ShaderNodeMix")
    mix.data_type = "RGBA"
    mix.blend_type = "MULTIPLY"
    mix.inputs["Factor"].default_value = 1.0
    nt.links.new(env.outputs["Color"], mix.inputs["A"])
    nt.links.new(ramp.outputs["Color"], mix.inputs["B"])
    bg = nt.nodes["Background"]
    nt.links.new(mix.outputs["Result"], bg.inputs[0])
    bg.inputs[1].default_value = float(ARGS.get("env", 1.4 if SATIN else 1.6))

    # mancha magenta-roja arriba a la izquierda por delante (coronilla y mejilla)
    emitter("key_magenta", (6.0, 6.0), (-3.2, -5.0, 3.4), (1.0, 0.04, 0.22), 4 * k, soft=1.4)
    # tira blanca de recorte, arriba
    emitter("strip_top", (5.0, 0.4), (0.8, -2.2, 4.4), (1.0, 0.95, 0.95), 22 * k)
    # tira blanca vertical a la derecha (el brillo largo del costado)
    emitter("strip_right", (0.4, 4.5), (3.8, -2.0, 0.4), (1.0, 0.97, 0.97), 16 * k, look_at=(0, 0, 0.2))
    # chispa cálida a la izquierda (el amarillo del ojo izquierdo)
    emitter("warm_left", (0.9, 0.9), (-3.6, -2.8, 0.3), (1.0, 0.65, 0.15), 14 * k, soft=1.5)
    # contraluces
    emitter("rim_back", (4.0, 1.0), (1.5, 4.0, 2.5), (0.7, 0.85, 1.0), 14 * k)
    emitter("rim_back_l", (3.0, 1.0), (-2.5, 4.0, -0.5), (1.0, 0.3, 0.4), 10 * k)


def camera():
    cam = bpy.data.cameras.new("cam")
    cam.lens = float(ARGS.get("lens", 85))
    cam.dof.use_dof = False
    ob = bpy.data.objects.new("cam", cam)
    link(ob)
    scn.camera = ob
    tgt = Vector((0.0, 0.0, float(ARGS.get("tz", -0.3))))
    if CAM == "face":
        tgt = Vector((0.0, 0.0, -0.1))
        pos = Vector((0.0, -11.5, 0.9))
        cam.lens = 200
    elif CAM == "three":
        pos = Vector((-4.5, -10.0, 1.6))
    elif CAM == "face":
        pass
    else:
        pos = Vector((0.0, -float(ARGS.get("dist", 11.5)), 0.9))
    ob.location = pos
    ob.rotation_euler = (tgt - pos).to_track_quat("-Z", "Y").to_euler()
    return ob


# ------------------------------------------------------------- animación
def ease_blink(t, at=0.62, dur=0.07):
    """0 abierto → 1 cerrado, un parpadeo rápido por bucle."""
    d = (t - at) / dur
    if 0 <= d <= 1:
        return math.sin(math.pi * d) ** 0.7
    return 0.0


def pose(state, t):
    ph = TAU * t
    rig = state["rig"]
    # flota y balancea: cabeceo y giro suaves, todo en múltiplos de la fase
    rig.location = (0.05 * math.sin(ph + 0.4), 0.0, 0.07 * math.sin(ph))
    rig.rotation_euler = (math.radians(4.0 * math.sin(ph - 0.9)),
                          math.radians(5.0 * math.sin(ph + 0.3)),
                          math.radians(11.0 * math.sin(ph)))
    blink = ease_blink(t)
    for side, eye_rig, ball, lid in state["eyes"]:
        # la mirada sigue un poco al giro y busca a la cámara
        ball.rotation_euler = (math.radians(6 * math.sin(ph - 0.5)), 0, math.radians(-9 * math.sin(ph) + side * 3))
        lid.rotation_euler = (math.radians(72 * blink), 0, 0)
    halo = state["halo"]
    # el halo va con retraso respecto a la cabeza y gira un par de eslabones por bucle
    halo.location = (0.05 * math.sin(ph + 0.4 - 0.5), 0.18, 1.3 + 0.07 * math.sin(ph - 0.7))
    halo.rotation_euler = (math.radians(-16 + 4 * math.sin(ph - 1.1)), math.radians(6 * math.sin(ph - 0.6)),
                           TAU * 2 / 30 * t)
    build_tail(state, t)


# ---------------------------------------------------------------- render
state = build()
lights()
camera()
if "blend" in ARGS:
    pose(state, 0.0)
    bpy.ops.wm.save_as_mainfile(filepath=ARGS["blend"])
for f in FRAMES:
    path = f"{OUT}{f:04d}.png"
    if ARGS.get("skip") == "1" and os.path.exists(path):
        continue
    t = (f % TOTAL) / TOTAL
    pose(state, t)
    scn.frame_current = f
    scn.render.filepath = path
    t0 = time.time()
    bpy.ops.render.render(write_still=True)
    print(f"FRAME {f} {time.time() - t0:.1f}s -> {path}", flush=True)
