"""Barullo hero loop: chest in a ribbed tank top wearing a silver Barullo medallion.

Run headless (Windows Blender 5.2):
  blender.exe -b --factory-startup --python colgante.py -- key=value ...
Keys:
  out=<path prefix>      render output (frame number is appended)
  frames=a-b | frame=n   what to render (loop is frames 0-209, 30 fps, 7 s)
  res=<pct>              resolution percentage of 2520x1080 (default 100)
  samples=<n>            Cycles max samples (default 128)
  save=<path.blend>      save the built scene
The square deliverable is the centred 1080x1080 crop of the wide frame.
"""
import bpy, bmesh, math, sys, os
import numpy as np
from mathutils import Vector, Matrix, Euler
from mathutils.bvhtree import BVHTree

ROOT = "C:/Users/Veintiuno/barullo-render/colgante/"
HBM = "C:/Users/Veintiuno/barullo-render/assets/hbm/human-base-meshes-bundle-v1.4.1/human_base_meshes_bundle.blend"
ARGS = dict(a.split("=", 1) for a in (sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []))

T = 210          # loop length (frames)
STRIDE = 70      # one gait cycle (two steps)
STEP = 35
BREATH = 105
R = 0.025        # medal radius (m)
MEDAL_Z = 1.235  # medal centre height on the sternum
CHEST = Vector((0, -0.02, 1.25))

sc = bpy.context.scene
for o in list(bpy.data.objects):
    bpy.data.objects.remove(o)


def smooth(t):
    t = np.clip(t, 0, 1)
    return t * t * (3 - 2 * t)


def mesh_np(me):
    co = np.empty(len(me.vertices) * 3, np.float32)
    me.vertices.foreach_get("co", co)
    return co.reshape(-1, 3)


def set_co(me, co):
    me.vertices.foreach_set("co", co.astype(np.float32).ravel())
    me.update()


def normals_np(me):
    n = np.empty(len(me.vertices) * 3, np.float32)
    me.vertices.foreach_get("normal", n)
    return n.reshape(-1, 3)


def vgroup(ob, name, w):
    g = ob.vertex_groups.new(name=name)
    idx = np.nonzero(w > 1e-4)[0]
    for i in idx:
        g.add([int(i)], float(w[i]), "REPLACE")
    return g


def drv(ob, path, idx, expr):
    fc = ob.driver_add(path, idx) if idx is not None else ob.driver_add(path)
    fc.driver.type = "SCRIPTED"
    fc.driver.expression = expr
    return fc


# ---------------------------------------------------------------- body
with bpy.data.libraries.load(HBM) as (src, dst):
    dst.objects = ["GEO-body_male_realistic"]
body = dst.objects[0]
sc.collection.objects.link(body)
body.location = (0, 0, 0)
mr = body.modifiers[0]
mr.levels = int(ARGS.get("mr", mr.render_levels))
with bpy.context.temp_override(object=body, active_object=body, selected_objects=[body]):
    bpy.ops.object.modifier_apply(modifier=mr.name)

bm = bmesh.new()
bm.from_mesh(body.data)
bmesh.ops.delete(bm, geom=[v for v in bm.verts if v.co.z < 0.9 or v.co.z > 1.58], context="VERTS")
bm.to_mesh(body.data)
bm.free()
body.data.update()

co0 = mesh_np(body.data)
x, y, z = co0[:, 0], co0[:, 1], co0[:, 2]
ax = np.abs(x)

# arm weight: outside the line armpit -> hand of the A pose, and away from the straps
A = np.array([0.168, 1.245])
d = np.array([0.23, -0.59]); d /= np.linalg.norm(d)
nrm = np.array([-d[1], d[0]])  # points out/up
s = (ax - A[0]) * nrm[0] + (z - A[1]) * nrm[1]
W_ARM = smooth((s + 0.01) / 0.03) * smooth((ax - 0.13) / 0.03)


def bend(co, w):
    """Lower the A-pose arms ~12 deg around the shoulder joints (angle blended by weight)."""
    out = co.copy()
    for side in (1, -1):
        m = (np.sign(co[:, 0]) == side) & (w > 0)
        px, pz = 0.19 * side, 1.36
        th = np.radians(12) * side * w[m]
        dx, dz = co[m, 0] - px, co[m, 2] - pz
        out[m, 0] = px + dx * np.cos(th) + dz * np.sin(th)
        out[m, 2] = pz - dx * np.sin(th) + dz * np.cos(th)
    return out


set_co(body.data, bend(co0, W_ARM))


def flatten_nipples(me):
    """Relax the nipples so the tight fabric over them reads as cotton, not latex."""
    co = mesh_np(me)
    e = np.empty(len(me.edges) * 2, np.int32)
    me.edges.foreach_get("vertices", e)
    e = e.reshape(-1, 2)
    for side in (1, -1):
        # nipple sits at ~(0.125, 1.212) on this mesh (measured on renders)
        cand = np.nonzero((np.hypot(co[:, 0] - 0.125 * side, co[:, 2] - 1.212) < 0.012) & (co[:, 1] < -0.05))[0]
        c = co[cand].mean(0)
        c[1] = co[cand, 1].min()
        dd = np.linalg.norm(co - c, axis=1)
        w = 1 - smooth((dd - 0.022) / 0.02)
        sel = w > 0
        for _ in range(120):
            acc = np.zeros_like(co)
            np.add.at(acc, e[:, 0], co[e[:, 1]])
            np.add.at(acc, e[:, 1], co[e[:, 0]])
            deg_ = np.bincount(e.ravel(), minlength=len(co))[:, None]
            avg = acc / np.maximum(deg_, 1)
            co[sel] += (avg[sel] - co[sel]) * (0.8 * w[sel])[:, None]
        print("nipple", side, c)
    set_co(me, co)


flatten_nipples(body.data)

# ---------------------------------------------------------------- tank top boundary
def top_front(a):
    neck = 1.30 + 0.13 * (np.minimum(a, 0.065) / 0.065) ** 2.5
    arm = 1.45 - 0.31 * smooth((a - 0.105) / 0.065)
    return np.where(a < 0.065, neck, np.where(a < 0.105, 9.0, arm))


def top_back(a):
    neck = 1.40 + 0.03 * (np.minimum(a, 0.065) / 0.065) ** 2
    arm = 1.45 - 0.31 * smooth((a - 0.105) / 0.065)
    return np.where(a < 0.065, neck, np.where(a < 0.105, 9.0, arm))


def boundary_poly(topf):
    a1 = np.linspace(0, 0.065, 60)
    a2 = np.linspace(0.105, 0.30, 120)
    p = [np.stack([a1, topf(a1)], 1), [[0.065, 1.6]], [[0.105, 1.6]], np.stack([a2, topf(a2)], 1)]
    return [np.array(p[0]), np.array([[0.065, topf(np.array([0.064]))[0]], [0.065, 1.6]]),
            np.array([[0.105, 1.6], [0.105, 1.45]]), np.array(p[3])]


def nearest_on_polys(P, polys):
    best = np.full(len(P), 9.0)
    near = P.copy()
    for poly in polys:
        for i in range(len(poly) - 1):
            a, b = poly[i], poly[i + 1]
            ab = b - a
            t = np.clip(((P - a) @ ab) / max(ab @ ab, 1e-12), 0, 1)
            q = a + t[:, None] * ab
            dd = np.linalg.norm(P - q, axis=1)
            m = dd < best
            best[m] = dd[m]
            near[m] = q[m]
    return best, near


def dist_to_polys(P, polys):
    return nearest_on_polys(P, polys)[0]


nb = normals_np(body.data)
front = nb[:, 1] < 0
top = np.where(front, top_front(ax), top_back(ax))
inside = (z < top) & (z < 1.5) & (W_ARM < 0.3)

bm = bmesh.new()
bm.from_mesh(body.data)
bm.verts.ensure_lookup_table()
keep_faces = [f for f in bm.faces if all(inside[v.index] for v in f.verts)]
shirt_me = bpy.data.meshes.new("tanktop")
sbm = bmesh.new()
vmap = {}
for f in keep_faces:
    for v in f.verts:
        if v.index not in vmap:
            vmap[v.index] = sbm.verts.new(v.co)
for f in keep_faces:
    sbm.faces.new([vmap[v.index] for v in f.verts])
sbm.verts.ensure_lookup_table()
src_index = np.array(list(vmap.keys()))
sbm.verts.index_update()
# snap the border onto the cut curve so neckline and armholes are clean
sco = np.array([v.co[:] for v in sbm.verts])
border = np.array([v.is_boundary for v in sbm.verts])
s_front = front[src_index]
s_top = np.where(s_front, top_front(np.abs(sco[:, 0])), top_back(np.abs(sco[:, 0])))
# project border verts onto the cut curve in the (|x|, z) plane
Pb = np.stack([np.abs(sco[:, 0]), sco[:, 2]], 1)
dF, qF = nearest_on_polys(Pb, boundary_poly(top_front))
dB, qB = nearest_on_polys(Pb, boundary_poly(top_back))
dN = np.where(s_front, dF, dB)
qN = np.where(s_front[:, None], qF, qB)
snap = border & (dN < 0.011) & (sco[:, 2] > 0.95)
sco[snap, 0] = np.sign(sco[snap, 0]) * qN[snap, 0]
sco[snap, 2] = qN[snap, 1]
edges = np.array([[e.verts[0].index, e.verts[1].index] for e in sbm.edges])
sbm.to_mesh(shirt_me)
sbm.free()
bm.free()
shirt = bpy.data.objects.new("tanktop", shirt_me)
sc.collection.objects.link(shirt)
set_co(shirt_me, sco)

# fabric bridges concave valleys (sternum, under the pecs): heavy Laplacian smooth, push out where it is outside
sn = normals_np(shirt_me)
deg = np.bincount(edges.ravel(), minlength=len(sco)).astype(np.float32)
sm = sco.copy()
for _ in range(90):
    acc = np.zeros_like(sm)
    np.add.at(acc, edges[:, 0], sm[edges[:, 1]])
    np.add.at(acc, edges[:, 1], sm[edges[:, 0]])
    nxt = acc / np.maximum(deg, 1)[:, None]
    nxt[border] = sco[border]
    sm = 0.5 * sm + 0.5 * nxt
bridge = np.maximum(((sm - sco) * sn).sum(1), 0) * 0.9
s_ax = np.abs(sco[:, 0])
P = np.stack([s_ax, sco[:, 2]], 1)
edge_d = np.where(s_front, dist_to_polys(P, boundary_poly(top_front)), dist_to_polys(P, boundary_poly(top_back)))
band = 1 - smooth((edge_d - 0.008) / 0.002)        # binding band at neckline/armholes
push = 0.0011 + bridge + 0.0005 * band
set_co(shirt_me, sco + sn * push[:, None])
att = shirt_me.attributes.new("edge_d", "FLOAT", "POINT")
att.data.foreach_set("value", edge_d.astype(np.float32))
for p in shirt_me.polygons:
    p.use_smooth = True
for p in body.data.polygons:
    p.use_smooth = True

# shared deformation groups (computed from the rest A-pose positions so body and shirt match)
co_b = mesh_np(body.data)
w_arm_shirt = W_ARM[src_index]


def breath_w(co, nrm_):
    return np.exp(-((co[:, 0] / 0.14) ** 2 + ((co[:, 2] - 1.22) / 0.12) ** 2)) * np.clip(-nrm_[:, 1] * 1.6, 0, 1)


for ob, w_arm, co_, n_ in ((body, W_ARM, co_b, normals_np(body.data)), (shirt, w_arm_shirt, mesh_np(shirt_me), normals_np(shirt_me))):
    vgroup(ob, "arm.L", np.where(co_[:, 0] > 0, w_arm, 0))
    vgroup(ob, "arm.R", np.where(co_[:, 0] < 0, w_arm, 0))
    vgroup(ob, "breath", breath_w(co_, n_))

# ---------------------------------------------------------------- materials
def principled(mat):
    mat.use_nodes = True
    nt = mat.node_tree
    return nt, next(n for n in nt.nodes if n.type == "BSDF_PRINCIPLED")


def inp(node, *names):
    for n in names:
        if n in node.inputs:
            return node.inputs[n]
    raise KeyError(names)


def obj_coords(nt):
    tc = nt.nodes.new("ShaderNodeTexCoord")
    return tc.outputs["Object"]


def math_node(nt, op, a, b=None, clamp=False):
    m = nt.nodes.new("ShaderNodeMath")
    m.operation = op
    m.use_clamp = clamp
    for i, v in enumerate((a, b)):
        if v is None:
            continue
        if isinstance(v, (int, float)):
            m.inputs[i].default_value = v
        else:
            nt.links.new(v, m.inputs[i])
    return m.outputs[0]


def noise(nt, vec, scale, detail=4, rough=0.55):
    n = nt.nodes.new("ShaderNodeTexNoise")
    n.inputs["Scale"].default_value = scale
    n.inputs["Detail"].default_value = detail
    n.inputs["Roughness"].default_value = rough
    nt.links.new(vec, n.inputs["Vector"])
    return n.outputs["Fac"]


def bump(nt, height, strength, distance, normal=None):
    b = nt.nodes.new("ShaderNodeBump")
    b.inputs["Strength"].default_value = strength
    b.inputs["Distance"].default_value = distance
    nt.links.new(height, b.inputs["Height"])
    if normal is not None:
        nt.links.new(normal, b.inputs["Normal"])
    return b.outputs["Normal"]


def sock(coll, ident):
    return next(s for s in coll if s.identifier == ident)


def ramp(nt, fac, stops):
    r = nt.nodes.new("ShaderNodeValToRGB")
    els = r.color_ramp.elements
    for i, (pos, col) in enumerate(stops):
        e = els[i] if i < 2 else els.new(pos)
        e.position = pos
        e.color = col
    nt.links.new(fac, r.inputs["Fac"])
    return r.outputs["Color"]


def skin_material():
    mat = bpy.data.materials.new("skin")
    nt, p = principled(mat)
    oc = obj_coords(nt)
    # tone: warm mediterranean skin with mottling and flushed areas
    mott = noise(nt, oc, 18, 6, 0.6)
    tone = ramp(nt, mott, [(0.3, (0.42, 0.215, 0.13, 1)), (0.7, (0.50, 0.26, 0.155, 1))])
    flush = noise(nt, oc, 4, 3, 0.5)
    mix = nt.nodes.new("ShaderNodeMix")
    mix.data_type = "RGBA"
    mix.blend_type = "MULTIPLY"
    nt.links.new(math_node(nt, "MULTIPLY", math_node(nt, "SUBTRACT", flush, 0.45, True), 1.5), sock(mix.inputs, "Factor_Float"))
    nt.links.new(tone, sock(mix.inputs, "A_Color"))
    sock(mix.inputs, "B_Color").default_value = (1.0, 0.9, 0.86, 1)
    freck = nt.nodes.new("ShaderNodeTexVoronoi")
    freck.inputs["Scale"].default_value = 260
    nt.links.new(oc, freck.inputs["Vector"])
    fr = math_node(nt, "LESS_THAN", freck.outputs["Distance"], 0.12)
    fr = math_node(nt, "MULTIPLY", fr, math_node(nt, "GREATER_THAN", noise(nt, oc, 30, 2), 0.56))
    mix2 = nt.nodes.new("ShaderNodeMix")
    mix2.data_type = "RGBA"
    mix2.blend_type = "MULTIPLY"
    nt.links.new(math_node(nt, "MULTIPLY", fr, 0.35), sock(mix2.inputs, "Factor_Float"))
    nt.links.new(sock(mix.outputs, "Result_Color"), sock(mix2.inputs, "A_Color"))
    sock(mix2.inputs, "B_Color").default_value = (0.75, 0.55, 0.45, 1)
    nt.links.new(sock(mix2.outputs, "Result_Color"), inp(p, "Base Color"))
    inp(p, "Subsurface Weight").default_value = 1.0
    inp(p, "Subsurface Radius").default_value = (1.0, 0.38, 0.2)
    inp(p, "Subsurface Scale").default_value = 0.0045
    try:
        p.subsurface_method = ARGS.get("sss", "RANDOM_WALK_SKIN")
    except TypeError:
        pass
    # roughness: oilier on the sternum, varied elsewhere
    rn = noise(nt, oc, 40, 3)
    nt.links.new(math_node(nt, "ADD", math_node(nt, "MULTIPLY", rn, 0.18), 0.33), inp(p, "Roughness"))
    inp(p, "Specular IOR Level").default_value = 0.55
    inp(p, "Coat Weight").default_value = 0.08
    inp(p, "Coat Roughness").default_value = 0.35
    inp(p, "Sheen Weight").default_value = 0.12
    inp(p, "Sheen Roughness").default_value = 0.45
    inp(p, "Sheen Tint").default_value = (1, 0.9, 0.85, 1)
    # micro surface: pores, fine crosshatch wrinkles, broad unevenness
    vor = nt.nodes.new("ShaderNodeTexVoronoi")
    vor.inputs["Scale"].default_value = 820
    vor.inputs["Randomness"].default_value = 0.9
    nt.links.new(oc, vor.inputs["Vector"])
    pores = math_node(nt, "SMOOTH_MAX" if False else "POWER", math_node(nt, "MINIMUM", math_node(nt, "MULTIPLY", vor.outputs["Distance"], 2.2), 1.0), 0.5)
    n1 = bump(nt, pores, 0.32, 0.00018)
    fine = noise(nt, oc, 2600, 3, 0.7)
    n2 = bump(nt, fine, 0.12, 0.0002, n1)
    broad = noise(nt, oc, 90, 4, 0.6)
    n3 = bump(nt, broad, 0.05, 0.002, n2)
    nt.links.new(n3, inp(p, "Normal"))
    return mat


def fabric_material():
    mat = bpy.data.materials.new("ribbed_cotton")
    nt, p = principled(mat)
    oc = obj_coords(nt)
    sep = nt.nodes.new("ShaderNodeSeparateXYZ")
    nt.links.new(oc, sep.inputs[0])
    # 1x1 rib: vertical cords every 1.9 mm, finer in the binding band
    attr = nt.nodes.new("ShaderNodeAttribute")
    attr.attribute_name = "edge_d"
    in_band = math_node(nt, "LESS_THAN", attr.outputs["Fac"], 0.008)
    rib = math_node(nt, "SINE", math_node(nt, "MULTIPLY", sep.outputs["X"], 2 * math.pi / 0.0019))
    rib = math_node(nt, "POWER", math_node(nt, "ABSOLUTE", rib), 0.6)
    # binding: cords run along the edge, approximated by horizontal-ish fine ribs
    rib_b = math_node(nt, "ABSOLUTE", math_node(nt, "SINE", math_node(nt, "MULTIPLY", attr.outputs["Fac"], 2 * math.pi / 0.0013)))
    ribmix = nt.nodes.new("ShaderNodeMix")
    nt.links.new(in_band, ribmix.inputs["Factor"])
    nt.links.new(rib, ribmix.inputs["A"])
    nt.links.new(rib_b, ribmix.inputs["B"])
    # stitched fold line where the binding is sewn
    seam = math_node(nt, "MULTIPLY", math_node(nt, "SUBTRACT", 1.0, math_node(nt, "MINIMUM", math_node(nt, "MULTIPLY", math_node(nt, "ABSOLUTE", math_node(nt, "SUBTRACT", attr.outputs["Fac"], 0.0085)), 900), 1.0)), -0.6)
    fiber = noise(nt, oc, 1800, 5, 0.75)
    h = math_node(nt, "ADD", math_node(nt, "ADD", ribmix.outputs[0], seam), math_node(nt, "MULTIPLY", fiber, 0.35))
    n1 = bump(nt, h, 0.55, 0.0004)
    wr = noise(nt, oc, 22, 3, 0.5)
    n2 = bump(nt, wr, 0.08, 0.003, n1)
    nt.links.new(n2, inp(p, "Normal"))
    col = ramp(nt, fiber, [(0.3, (0.55, 0.54, 0.52, 1)), (0.7, (0.63, 0.62, 0.60, 1))])
    nt.links.new(col, inp(p, "Base Color"))
    inp(p, "Roughness").default_value = 0.92
    inp(p, "Sheen Weight").default_value = 0.7
    inp(p, "Sheen Roughness").default_value = 0.35
    inp(p, "Specular IOR Level").default_value = 0.3
    return mat


def silver(name, rough, aniso=0.0, rough_tex=None):
    mat = bpy.data.materials.new(name)
    nt, p = principled(mat)
    inp(p, "Metallic").default_value = 1.0
    inp(p, "Base Color").default_value = (0.96, 0.955, 0.94, 1)
    try:
        inp(p, "Specular Tint").default_value = (0.99, 0.98, 0.96, 1)
    except KeyError:
        pass
    oc = obj_coords(nt)
    smudge = noise(nt, oc, 160, 4, 0.6)
    nt.links.new(math_node(nt, "ADD", math_node(nt, "MULTIPLY", smudge, 0.05), rough - 0.02), inp(p, "Roughness"))
    studio_reflect(nt, p, 1.0)
    return mat, nt, p


STUDIO = None


def studio_reflect(nt, p, strength):
    """Mirror a studio HDRI by the reflection vector into emission: EEVEE cannot see off-screen
    softboxes, so the chrome gets its product-shot reflections from here."""
    global STUDIO
    if STUDIO is None:
        STUDIO = bpy.data.images.load(ROOT + "studio_small_09.hdr")
    tc = nt.nodes.new("ShaderNodeTexCoord")
    mp = nt.nodes.new("ShaderNodeMapping")
    mp.inputs["Rotation"].default_value = (math.radians(float(ARGS.get("envtilt", 0))), 0, math.radians(float(ARGS.get("envrot", 45))))
    nt.links.new(tc.outputs["Reflection"], mp.inputs["Vector"])
    env = nt.nodes.new("ShaderNodeTexEnvironment")
    env.image = STUDIO
    nt.links.new(mp.outputs["Vector"], env.inputs["Vector"])
    nt.links.new(env.outputs["Color"], inp(p, "Emission Color"))
    if isinstance(strength, (int, float)):
        inp(p, "Emission Strength").default_value = strength * float(ARGS.get("envgain", 0.9))
    else:
        nt.links.new(math_node(nt, "MULTIPLY", strength, float(ARGS.get("envgain", 0.9))), inp(p, "Emission Strength"))


body.data.materials.append(skin_material())
shirt.data.materials.append(fabric_material())

# ---------------------------------------------------------------- rig + armature
rig = bpy.data.objects.new("rig", None)
sc.collection.objects.link(rig)
rig.location = CHEST

arm_data = bpy.data.armatures.new("arms")
arm = bpy.data.objects.new("arms", arm_data)
sc.collection.objects.link(arm)
bpy.context.view_layer.objects.active = arm
bpy.ops.object.mode_set(mode="EDIT")
for side, nm in ((1, "arm.L"), (-1, "arm.R")):
    b = arm_data.edit_bones.new(nm)
    b.head = (0.19 * side, -0.03, 1.36)
    b.tail = (0.19 * side, -0.03, 1.46)
    b.roll = 0
bpy.ops.object.mode_set(mode="OBJECT")

for ob in (body, shirt, arm):
    ob.parent = rig
    ob.matrix_parent_inverse = rig.matrix_world.inverted()

for ob in (body, shirt):
    br = ob.modifiers.new("breath", "DISPLACE")
    br.direction = "NORMAL"
    br.mid_level = 0
    br.vertex_group = "breath"
    drv(br, "strength", None, f"0.0035*(0.5-0.5*cos(2*pi*frame/{BREATH}))")
    am = ob.modifiers.new("arms", "ARMATURE")
    am.object = arm
    am.use_deform_preserve_volume = True
sol = shirt.modifiers.new("thickness", "SOLIDIFY")
sol.thickness = 0.0012
sol.offset = -1
sol.use_even_offset = True

for nm, sgn in (("arm.L", 1), ("arm.R", -1)):
    pb = arm.pose.bones[nm]
    pb.rotation_mode = "XYZ"
    drv(pb, "rotation_euler", 0, f"{0.075 * sgn}*sin(2*pi*frame/{STRIDE}+1.2)")

# walking: bob twice per stride, lateral sway, twist, roll; breathing lifts the chest
drv(rig, "location", 0, f"0.007*sin(2*pi*frame/{STRIDE})")
drv(rig, "location", 1, f"{CHEST.y}+0.002*sin(2*pi*frame/{STEP}+1.0)")
drv(rig, "location", 2, f"{CHEST.z}+0.005*cos(2*pi*frame/{STEP})+0.0015*sin(2*pi*frame/{BREATH})")
drv(rig, "rotation_euler", 0, f"0.010*sin(2*pi*frame/{STEP}+0.5)")
drv(rig, "rotation_euler", 1, f"0.020*sin(2*pi*frame/{STRIDE}+0.4)")
drv(rig, "rotation_euler", 2, f"0.035*sin(2*pi*frame/{STRIDE}+1.2)")

# ---------------------------------------------------------------- surface queries (rest pose, rig-local == world at rest)
sc.frame_set(0)
dg = bpy.context.evaluated_depsgraph_get()


def bvh(ob):
    ev = ob.evaluated_get(dg)
    me = ev.to_mesh()
    bm_ = bmesh.new()
    bm_.from_mesh(me)
    bm_.transform(ob.matrix_world)  # world at frame 0 (rig moved): undo below
    bm_.transform(rig.matrix_world.inverted())
    bm_.transform(Matrix.Translation(CHEST))
    t = BVHTree.FromBMesh(bm_)
    bm_.free()
    ev.to_mesh_clear()
    return t


T_SHIRT, T_BODY = bvh(shirt), bvh(body)


def surf(origin, direction):
    best = None
    for t in (T_SHIRT, T_BODY):
        hit = t.ray_cast(Vector(origin), Vector(direction).normalized())
        if hit[0] is not None and (best is None or hit[3] < best[3]):
            best = hit
    return best


# ---------------------------------------------------------------- medallion
hit = surf((0, -1, MEDAL_Z), (0, 1, 0))
P0, N0 = hit[0], hit[1]
up = (Vector((0, 0, 1)) - N0 * N0.z).normalized()
xax = up.cross(N0).normalized()
frame_m = Matrix((xax, up, N0)).transposed()   # columns: x, y(up), z(normal)
# clearance: lift until the back face clears the chest everywhere
lift = 0.0
for rr in np.linspace(0, R, 6):
    for a in np.linspace(0, 2 * math.pi, 24, endpoint=False):
        p = P0 + frame_m @ Vector((rr * math.cos(a), rr * math.sin(a), 0))
        h = surf(p - N0 * 0.03, N0)
        if h is None:
            continue
        lift = max(lift, (h[0] - p).dot(N0))
THICK = 0.0018
centre = P0 + N0 * (lift + THICK + 0.0004)
pivot_local = Vector((0, R + 0.0044, 0))  # chain passes through the jump ring here
pivot_world = centre + frame_m @ pivot_local

piv_base = bpy.data.objects.new("pendant_base", None)
sc.collection.objects.link(piv_base)
piv_base.parent = rig
piv_base.matrix_parent_inverse = Matrix.Identity(4)
piv_base.matrix_basis = Matrix.Translation(pivot_world - CHEST) @ frame_m.to_4x4()
swing = bpy.data.objects.new("pendant_swing", None)
sc.collection.objects.link(swing)
swing.parent = piv_base
swing.rotation_mode = "XYZ"
# lagging pendulum: sideways swing in the chest plane, lift off the chest on each step, twist only while lifted
LIFT = f"pow(max(0,sin(2*pi*(frame-4)/{STEP})),1.5)"
drv(swing, "rotation_euler", 2, f"0.11*sin(2*pi*(frame-10)/{STRIDE})")
drv(swing, "rotation_euler", 0, f"-0.09*{LIFT}")
drv(swing, "rotation_euler", 1, f"0.10*{LIFT}*sin(2*pi*frame/{STRIDE}+0.8)")
drv(swing, "location", 0, f"0.003*sin(2*pi*(frame-6)/{STRIDE})")
bw = float(np.exp(-((MEDAL_Z - 1.22) / 0.12) ** 2))
drv(swing, "location", 2, f"{0.0035 * bw}*(0.5-0.5*cos(2*pi*frame/{BREATH}))+0.0006*{LIFT}")


def lathe(name, prof, steps=256):
    """Revolve (r, z) profile around local Z."""
    verts, faces = [], []
    n = len(prof)
    for i in range(steps):
        a = 2 * math.pi * i / steps
        for r_, z_ in prof:
            verts.append((r_ * math.cos(a), r_ * math.sin(a), z_))
    for i in range(steps):
        j = (i + 1) % steps
        for k in range(n - 1):
            faces.append((i * n + k, j * n + k, j * n + k + 1, i * n + k + 1))
    me = bpy.data.meshes.new(name)
    me.from_pydata(verts, [], faces)
    me.validate()
    for p in me.polygons:
        p.use_smooth = True
    ob = bpy.data.objects.new(name, me)
    sc.collection.objects.link(ob)
    return ob


def rounded(r0, z0, rad, a0, a1, n=8):
    return [(r0 + rad * math.cos(a), z0 + rad * math.sin(a)) for a in np.linspace(a0, a1, n)]


# coin body: back face, rounded edge, raised polished rim, wall down to the field
prof = [(0.0, -THICK)] + [(R * f, -THICK) for f in (0.5, 0.85)]
prof += rounded(R - 0.0009, -THICK + 0.0009, 0.0009, -math.pi / 2, 0, 6)[1:]
prof += rounded(R - 0.0009, THICK - 0.0009, 0.0009, 0, math.pi / 2, 6)[1:]
prof += [(R - 0.0021, THICK), (R - 0.0026, THICK - 0.0002), (R - 0.0030, 0.0009), (R - 0.0034, 0.0004), (R * 0.5, 0.0004), (0.0, 0.0004)]
coin = lathe("medal_body", prof[::-1])
m_polish, _, _ = silver("silver_polished", 0.06)
coin.data.materials.append(m_polish)

# relief face: dense disc grid displaced by the emblem heightmap
G = int(ARGS.get("grid", 1100))
gx = np.linspace(-R, R, G + 1)
XX, YY = np.meshgrid(gx, gx)
rr_ = np.hypot(XX, YY)
keep = rr_ < R - 0.0029
idx = -np.ones(keep.shape, np.int64)
idx[keep] = np.arange(keep.sum())
q = (keep[:-1, :-1] & keep[1:, :-1] & keep[1:, 1:] & keep[:-1, 1:])
ii, jj = np.nonzero(q)
quads = np.stack([idx[ii, jj], idx[ii, jj + 1], idx[ii + 1, jj + 1], idx[ii + 1, jj]], 1)
vco = np.stack([XX[keep], YY[keep], np.full(keep.sum(), 0.0008)], 1)
me = bpy.data.meshes.new("medal_face")
me.vertices.add(len(vco))
me.vertices.foreach_set("co", vco.astype(np.float32).ravel())
me.loops.add(quads.size)
me.loops.foreach_set("vertex_index", quads.astype(np.int32).ravel())
me.polygons.add(len(quads))
me.polygons.foreach_set("loop_start", (np.arange(len(quads)) * 4).astype(np.int32))
me.polygons.foreach_set("loop_total", np.full(len(quads), 4, np.int32))
me.polygons.foreach_set("use_smooth", np.ones(len(quads), bool))
uv = me.uv_layers.new(name="UVMap")
lv = quads.ravel()
uvs = (vco[lv, :2] + R) / (2 * R)
uv.data.foreach_set("uv", uvs.astype(np.float32).ravel())
me.update()
me.validate()
face = bpy.data.objects.new("medal_face", me)
sc.collection.objects.link(face)
himg = bpy.data.images.load(ROOT + "tex/medal_height.png")
himg.colorspace_settings.name = "Non-Color"
htex = bpy.data.textures.new("medal_h", "IMAGE")
htex.image = himg
dm = face.modifiers.new("relief", "DISPLACE")
dm.texture = htex
dm.texture_coords = "UV"
dm.direction = "Z"
dm.space = "LOCAL"
dm.mid_level = 0
dm.strength = 0.00075

# face material: polished relief, sandblasted star interior, radially brushed outer field
mface = bpy.data.materials.new("silver_face")
nt, p = principled(mface)
inp(p, "Metallic").default_value = 1.0
inp(p, "Base Color").default_value = (0.96, 0.955, 0.94, 1)
mimg = bpy.data.images.load(ROOT + "tex/medal_mask.png")
mimg.colorspace_settings.name = "Non-Color"
it = nt.nodes.new("ShaderNodeTexImage")
it.image = mimg
sep = nt.nodes.new("ShaderNodeSeparateColor")
nt.links.new(it.outputs["Color"], sep.inputs[0])
oc = obj_coords(nt)
grain = noise(nt, oc, 3000, 2, 0.6)
r_rel = 0.05
r_sand = math_node(nt, "ADD", 0.55, math_node(nt, "MULTIPLY", grain, 0.15))
r_field = 0.2
rough = math_node(nt, "ADD", math_node(nt, "ADD", math_node(nt, "MULTIPLY", sep.outputs[0], r_rel), math_node(nt, "MULTIPLY", sep.outputs[1], r_sand)), math_node(nt, "MULTIPLY", sep.outputs[2], r_field))
nt.links.new(rough, inp(p, "Roughness"))
nt.links.new(sep.outputs[2], inp(p, "Anisotropic"))
# radial tangent for the brushed field
tan = nt.nodes.new("ShaderNodeTangent")
tan.direction_type = "RADIAL"
tan.axis = "Z"
nt.links.new(tan.outputs[0], inp(p, "Tangent"))
sand = bump(nt, math_node(nt, "MULTIPLY", grain, sep.outputs[1]), 0.25, 0.00004)
nt.links.new(sand, inp(p, "Normal"))
# antique finish: blackened sandblast inside the star, bright polish on the relief
dark = nt.nodes.new("ShaderNodeMix")
dark.data_type = "RGBA"
nt.links.new(sep.outputs[1], sock(dark.inputs, "Factor_Float"))
sock(dark.inputs, "A_Color").default_value = (0.96, 0.955, 0.94, 1)
sock(dark.inputs, "B_Color").default_value = (0.035, 0.033, 0.03, 1)
nt.links.new(sock(dark.outputs, "Result_Color"), inp(p, "Base Color"))
refl = math_node(nt, "ADD", math_node(nt, "ADD", sep.outputs[0], math_node(nt, "MULTIPLY", sep.outputs[2], 0.45)), math_node(nt, "MULTIPLY", sep.outputs[1], 0.0))
studio_reflect(nt, p, refl)
face.data.materials.append(mface)


def torus(name, major, minor, rot, loc, seg=48, mseg=16):
    bm_ = bmesh.new()
    for i in range(seg):
        a = 2 * math.pi * i / seg
        for k in range(mseg):
            b = 2 * math.pi * k / mseg
            rr2 = major + minor * math.cos(b)
            bm_.verts.new((rr2 * math.cos(a), rr2 * math.sin(a), minor * math.sin(b)))
    bm_.verts.ensure_lookup_table()
    for i in range(seg):
        for k in range(mseg):
            a_ = i * mseg + k
            b_ = ((i + 1) % seg) * mseg + k
            c_ = ((i + 1) % seg) * mseg + (k + 1) % mseg
            d_ = i * mseg + (k + 1) % mseg
            bm_.faces.new([bm_.verts[a_], bm_.verts[b_], bm_.verts[c_], bm_.verts[d_]])
    me_ = bpy.data.meshes.new(name)
    bm_.to_mesh(me_)
    bm_.free()
    for p_ in me_.polygons:
        p_.use_smooth = True
    ob = bpy.data.objects.new(name, me_)
    sc.collection.objects.link(ob)
    ob.rotation_euler = rot
    ob.location = loc
    ob.data.materials.append(m_polish)
    return ob


bail = torus("bail", 0.0026, 0.0009, (0, 0, 0), (0, R + 0.0018, 0))
ring = torus("jump_ring", 0.0021, 0.00055, (0, math.pi / 2, 0), (0, R + 0.0044, 0))
for ob in (coin, face, bail, ring):
    ob.parent = swing
    ob.matrix_parent_inverse = Matrix.Identity(4)
    ob.location = Vector(ob.location) - pivot_local
# make the bail sit in the coin plane (torus axis = coin normal) — rotate so its hole faces forward
bail.rotation_euler = (0, 0, 0)

# ---------------------------------------------------------------- ball chain
BALL = 0.00125
OFF = BALL + 0.0006


def onsurf(p, dirn):
    h = surf(Vector(p) - Vector(dirn) * 0.3, dirn)
    if h is None:
        return Vector(p)
    return h[0] + h[1] * OFF


J = pivot_world.copy()
neck_side = Vector((0.06, 0, 1.405))
pts_left = []
for t in np.linspace(0.12, 1.0, 9):
    px = J.x + (neck_side.x - J.x) * t
    pz = J.z + (neck_side.z - J.z) * t
    pts_left.append(onsurf((px, 0, pz), Vector((0, 1, 0))))
# around the neck base, from the front side to the back
nc = [v for v in mesh_np(body.data) if abs(v[0]) < 0.03 and abs(v[2] - 1.43) < 0.006]
ncy = float(np.mean([v[1] for v in nc])) if nc else -0.02
for k, ang in enumerate(np.radians(np.linspace(55, 180, 8))[1:]):
    zz = 1.405 + 0.03 * (k + 1) / 7
    dirn = Vector((math.sin(ang), -math.cos(ang), 0))  # outward
    c = Vector((0, ncy, zz))
    h = surf(c + dirn * 0.25, -dirn)
    pts_left.append(h[0] + h[1] * OFF if h else c + dirn * 0.06)
pts_right = [Vector((-p.x, p.y, p.z)) for p in pts_left]
chain_pts = [J] + pts_left + pts_right[::-1][1:]  # back centre shared once

cu = bpy.data.curves.new("chain_path", "CURVE")
cu.dimensions = "3D"
spl = cu.splines.new("NURBS")
spl.points.add(len(chain_pts) - 1)
for pt, v in zip(spl.points, chain_pts):
    pt.co = (v.x - CHEST.x, v.y - CHEST.y, v.z - CHEST.z, 1)
spl.use_cyclic_u = True
spl.order_u = 4
spl.resolution_u = 24
path = bpy.data.objects.new("chain_path", cu)
sc.collection.objects.link(path)
path.parent = rig
path.matrix_parent_inverse = Matrix.Identity(4)
bpy.context.view_layer.update()


def hook(ob, target, ids, centre_world, radius):
    hm = ob.modifiers.new("hook_" + target.name, "HOOK")
    hm.object = target
    hm.vertex_indices_set(ids)
    hm.center = centre_world - CHEST
    hm.falloff_type = "SMOOTH"
    hm.falloff_radius = radius
    hm.matrix_inverse = (ob.matrix_world.inverted() @ target.matrix_world).inverted()
    return hm


near = [i for i, v in enumerate(chain_pts) if (v - J).length < 0.09]
hook(path, swing, near, J, 0.09)
bhook = bpy.data.objects.new("breath_hook", None)
sc.collection.objects.link(bhook)
bhook.parent = rig
bhook.matrix_parent_inverse = Matrix.Identity(4)
bh0 = Vector((0, J.y, MEDAL_Z)) - CHEST
bhook.location = bh0
bpy.context.view_layer.update()
front_ids = [i for i, v in enumerate(chain_pts) if v.y < ncy - 0.02]
hook(path, bhook, front_ids, Vector((0, J.y, MEDAL_Z)), 0.17)
for i, axn in enumerate("xyz"):
    drv(bhook, "location", i, f"{bh0[i] + 0 * 1}+{-N0[i] * -0.0035}*(0.5-0.5*cos(2*pi*frame/{BREATH}))")

# one unit of #8 ball chain: ball + connector, arrayed along the path
bm_ = bmesh.new()
bmesh.ops.create_uvsphere(bm_, u_segments=18, v_segments=10, radius=BALL)
cyl = bmesh.ops.create_cone(bm_, segments=8, radius1=0.00033, radius2=0.00033, depth=0.0013, cap_ends=False)
for v in cyl["verts"]:
    v.co = Vector((v.co.z + 0.0017, v.co.x, v.co.y))
chain_me = bpy.data.meshes.new("ball_chain")
bm_.to_mesh(chain_me)
bm_.free()
for p_ in chain_me.polygons:
    p_.use_smooth = True
chain = bpy.data.objects.new("ball_chain", chain_me)
sc.collection.objects.link(chain)
chain.parent = rig
chain.matrix_parent_inverse = Matrix.Identity(4)
ar = chain.modifiers.new("links", "ARRAY")
ar.fit_type = "FIT_CURVE"
ar.curve = path
ar.use_relative_offset = False
ar.use_constant_offset = True
ar.constant_offset_displace = (0.0034, 0, 0)
cm = chain.modifiers.new("follow", "CURVE")
cm.object = path
cm.deform_axis = "POS_X"
m_chain, _, _ = silver("silver_chain", 0.1)
chain.data.materials.append(m_chain)

# ---------------------------------------------------------------- camera
cam = bpy.data.objects.new("cam", bpy.data.cameras.new("cam"))
sc.collection.objects.link(cam)
sc.camera = cam
FRAME_CZ = 1.255
look = Vector((0, centre.y, FRAME_CZ))
cam.location = (0, look.y - 1.78, 1.30)
cam.rotation_euler = (look - Vector(cam.location)).to_track_quat("-Z", "Y").to_euler()
cam.data.lens = 110
cam.data.sensor_fit = "HORIZONTAL"
cam.data.sensor_width = 36
cam.data.dof.use_dof = True
cam.data.dof.focus_distance = (centre - Vector(cam.location)).length
cam.data.dof.aperture_fstop = 3.2
if ARGS.get("cam") == "close":
    cam.location = centre + N0 * 0.35 + Vector((0, 0, 0.02))
    cam.rotation_euler = (centre - Vector(cam.location)).to_track_quat("-Z", "Y").to_euler()
    cam.data.lens = 120
    cam.data.dof.focus_distance = 0.35
    cam.data.dof.aperture_fstop = 11
else:
    drv(cam, "location", 0, "0.0025*sin(2*pi*frame/210)")
    drv(cam, "location", 2, "1.30+0.0015*sin(2*pi*frame/105+0.7)")

# ---------------------------------------------------------------- light
def area(name, size, loc, target, energy, color=(1, 1, 1), shape="RECTANGLE"):
    ld = bpy.data.lights.new(name, "AREA")
    ld.shape = shape
    ld.size, ld.size_y = size
    ld.energy = energy
    ld.color = color
    ob = bpy.data.objects.new(name, ld)
    sc.collection.objects.link(ob)
    ob.location = loc
    ob.rotation_euler = (Vector(target) - Vector(loc)).to_track_quat("-Z", "Y").to_euler()
    return ob


area("key", (0.9, 0.6), (-1.0, -1.2, 2.05), (0, -0.1, 1.25), 120, (1, 0.96, 0.92))
area("glint", (0.9, 0.07), (0.35, -1.05, 1.95), (0, -0.12, 1.24), 90)
area("rim_l", (0.12, 1.1), (-0.8, 0.55, 1.35), (-0.12, 0, 1.25), 160, (0.9, 0.95, 1))
area("rim_r", (0.12, 1.1), (0.8, 0.55, 1.35), (0.12, 0, 1.25), 190, (0.79, 0.045, 0.027))
area("fill", (1.0, 1.0), (0.9, -1.4, 0.9), (0, -0.1, 1.25), 8, (1, 0.97, 0.95))

world = bpy.data.worlds.new("world")
sc.world = world
world.use_nodes = True
wn = world.node_tree
bg = next(n for n in wn.nodes if n.type == "BACKGROUND")
env = wn.nodes.new("ShaderNodeTexEnvironment")
env.image = bpy.data.images.load(ROOT + "studio_small_09.hdr")
wn.links.new(env.outputs["Color"], bg.inputs["Color"])
bg.inputs["Strength"].default_value = 0.22
lp = wn.nodes.new("ShaderNodeLightPath")
black = wn.nodes.new("ShaderNodeBackground")
black.inputs["Color"].default_value = (0.0034, 0.0034, 0.0034, 1)
mixs = wn.nodes.new("ShaderNodeMixShader")
out = next(n for n in wn.nodes if n.type == "OUTPUT_WORLD")
wn.links.new(lp.outputs["Is Camera Ray"], mixs.inputs[0])
wn.links.new(bg.outputs[0], mixs.inputs[1])
wn.links.new(black.outputs[0], mixs.inputs[2])
wn.links.new(mixs.outputs[0], out.inputs[0])

# ---------------------------------------------------------------- render settings
try:
    sc.render.engine = "CYCLES"
except TypeError as e:
    print(e)
cy = sc.cycles
cy.device = "CPU"
cy.samples = int(ARGS.get("samples", 128))
cy.use_adaptive_sampling = True
cy.adaptive_threshold = 0.015
cy.use_denoising = True
try:
    cy.denoiser = "OPENIMAGEDENOISE"
except TypeError:
    pass
cy.max_bounces = 8
cy.diffuse_bounces = 3
cy.glossy_bounces = 6
cy.transmission_bounces = 4
cy.transparent_max_bounces = 8
cy.volume_bounces = 0
cy.caustics_reflective = False
cy.caustics_refractive = False
cy.blur_glossy = 0.5
sc.render.use_persistent_data = True
sc.render.resolution_x = 2520
sc.render.resolution_y = 1080
sc.render.resolution_percentage = int(ARGS.get("res", 100))
sc.render.image_settings.file_format = "PNG"
sc.render.image_settings.color_depth = "8"
sc.render.film_transparent = False
vs = sc.view_settings
for vt in ("AgX", "Filmic"):
    try:
        vs.view_transform = vt
        break
    except TypeError:
        pass
for lk in ("AgX - Punchy", "Punchy", "Medium High Contrast"):
    try:
        vs.look = lk
        break
    except TypeError:
        pass
sc.frame_start, sc.frame_end = 0, T - 1
vs.exposure = float(ARGS.get("exposure", -0.6))
sc.render.fps = 30

if ARGS.get("engine", "cycles") == "eevee":
    for eng in ("BLENDER_EEVEE", "BLENDER_EEVEE_NEXT"):
        try:
            sc.render.engine = eng
            break
        except TypeError:
            pass
    ee = sc.eevee
    ee.taa_render_samples = int(ARGS.get("samples", 64))
    for attr, val in (("use_raytracing", True), ("use_shadows", True), ("shadow_ray_count", 2), ("shadow_step_count", 8),
                      ("use_fast_gi", True), ("fast_gi_method", "GLOBAL_ILLUMINATION")):
        try:
            setattr(ee, attr, val)
        except (AttributeError, TypeError) as e:
            print("eevee setting skipped", attr, e)
    try:
        ee.ray_tracing_options.resolution_scale = "1"
        ee.ray_tracing_options.use_denoise = True
    except (AttributeError, TypeError) as e:
        print("eevee rt opts", e)
    for ob in sc.objects:
        if ob.type == "LIGHT":
            ob.data.use_shadow = True
            try:
                ob.data.use_shadow_jitter = True
            except AttributeError:
                pass

if "save" in ARGS:
    bpy.ops.wm.save_as_mainfile(filepath=ARGS["save"])

out_prefix = ARGS.get("out", ROOT + "frames/f_")
if "frame" in ARGS:
    sc.frame_set(int(ARGS["frame"]))
    sc.render.filepath = out_prefix + f"{int(ARGS['frame']):04d}.png"
    import time
    t0 = time.time()
    bpy.ops.render.render(write_still=True)
    print("RENDER_SECONDS", round(time.time() - t0, 1))
elif "frames" in ARGS:
    a, b = map(int, ARGS["frames"].split("-"))
    for f in range(a, b + 1):
        fp = out_prefix + f"{f:04d}.png"
        if os.path.exists(fp) and os.path.getsize(fp) > 0:
            continue
        sc.frame_set(f)
        sc.render.filepath = fp
        bpy.ops.render.render(write_still=True)
        print("RENDERED", fp, flush=True)
print("DONE")
