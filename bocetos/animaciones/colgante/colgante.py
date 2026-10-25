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
import bpy, bmesh, math, sys, os, re, time
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
CHEST = Vector((0, -0.02, 1.25))
SWAY, BOB, TWIST = 0.008, 0.0055, 0.028   # lateral weight shift, vertical bob, shoulder counter-rotation

sc = bpy.context.scene
for o in list(bpy.data.objects):
    bpy.data.objects.remove(o)


def smooth(t):
    t = np.clip(t, 0, 1)
    return t * t * (3 - 2 * t)


def smoother(t):
    """C2 smoothstep: no curvature kink at the ends, so deformation weights leave no visible crease."""
    t = np.clip(t, 0, 1)
    return t * t * t * (t * (6 * t - 15) + 10)


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
LAP = 4 ** max(mr.levels - 2, 0)   # Laplacian steps scale with mesh density
with bpy.context.temp_override(object=body, active_object=body, selected_objects=[body]):
    bpy.ops.object.modifier_apply(modifier=mr.name)

bm = bmesh.new()
bm.from_mesh(body.data)
bmesh.ops.delete(bm, geom=[v for v in bm.verts if v.co.z < 0.9 or v.co.z > 1.58], context="VERTS")
# the base mesh is split along the centre line and the arm joins: weld it, or Cycles shows the seams as lines
nv = len(bm.verts)
bmesh.ops.remove_doubles(bm, verts=bm.verts[:], dist=float(ARGS.get("weld", 0.00005)))
print("welded", nv - len(bm.verts), "verts")
for e_ in bm.edges:
    e_.smooth = True
for f_ in bm.faces:
    f_.smooth = True
bm.to_mesh(body.data)
bm.free()
print("body attrs", [a.name for a in body.data.attributes], "custom normals", body.data.has_custom_normals)
for nm_ in ("sharp_edge", "sharp_face"):
    if nm_ in body.data.attributes:
        body.data.attributes.remove(body.data.attributes[nm_])
if body.data.has_custom_normals:
    with bpy.context.temp_override(object=body, active_object=body, selected_objects=[body]):
        bpy.ops.mesh.customdata_custom_splitnormals_clear()
body.data.update()

co0 = mesh_np(body.data)
x, y, z = co0[:, 0], co0[:, 1], co0[:, 2]
ax = np.abs(x)

# arm weight: outside the line armpit -> hand of the A pose, and away from the straps
A = np.array([0.168, 1.245])
d = np.array([0.23, -0.59]); d /= np.linalg.norm(d)
nrm = np.array([-d[1], d[0]])  # points out/up
s = (ax - A[0]) * nrm[0] + (z - A[1]) * nrm[1]
W_ARM = smoother((s + 0.03) / 0.08) * smoother((ax - 0.12) / 0.07)   # soft: no crease where the arm bends
W_CUT = smooth((s + 0.01) / 0.03) * smooth((ax - 0.13) / 0.03)    # tight: where the shirt stops


def bend(co, w):
    """Lower the A-pose arms ~12 deg around the shoulder joints (angle blended by weight)."""
    out = co.copy()
    for side in (1, -1):
        m = (np.sign(co[:, 0]) == side) & (w > 0)
        px, pz = 0.19 * side, 1.36
        th = np.radians(float(ARGS.get("bend", 9))) * side * w[m]
        dx, dz = co[m, 0] - px, co[m, 2] - pz
        out[m, 0] = px + dx * np.cos(th) + dz * np.sin(th)
        out[m, 2] = pz - dx * np.sin(th) + dz * np.cos(th)
    return out


set_co(body.data, bend(co0, W_ARM))


def relax_shoulder_seam(me):
    """The arm/chest transition (and the base mesh's delto-pectoral groove) renders as a hard seam in
    Cycles; relax the skin there so it reads as one continuous surface."""
    co = mesh_np(me)
    e = np.empty(len(me.edges) * 2, np.int32)
    me.edges.foreach_get("vertices", e)
    e = e.reshape(-1, 2)
    a_, z_ = np.abs(co[:, 0]), co[:, 2]
    w = np.exp(-((a_ - 0.14) / 0.035) ** 2) * smooth((z_ - 1.12) / 0.05) * (1 - smooth((z_ - 1.42) / 0.04)) * (co[:, 1] < 0.03)
    sel = w > 0.02
    deg_ = np.bincount(e.ravel(), minlength=len(co))[:, None]
    for _ in range(int(ARGS.get("seam_iters", 25))):
        acc = np.zeros_like(co)
        np.add.at(acc, e[:, 0], co[e[:, 1]])
        np.add.at(acc, e[:, 1], co[e[:, 0]])
        avg = acc / np.maximum(deg_, 1)
        co[sel] += (avg[sel] - co[sel]) * (0.6 * w[sel])[:, None]
    set_co(me, co)


relax_shoulder_seam(body.data)


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
        w = 1 - smooth((dd - 0.03) / 0.025)
        sel = w > 0
        for _ in range(120 * LAP):
            acc = np.zeros_like(co)
            np.add.at(acc, e[:, 0], co[e[:, 1]])
            np.add.at(acc, e[:, 1], co[e[:, 0]])
            deg_ = np.bincount(e.ravel(), minlength=len(co))[:, None]
            avg = acc / np.maximum(deg_, 1)
            co[sel] += (avg[sel] - co[sel]) * (0.8 * w[sel])[:, None]
        print("nipple", side, c)
    set_co(me, co)


flatten_nipples(body.data)


def define_muscles(me):
    """Masculine chest: fuller upper (clavicular) pecs, less droop at the lower outer pec, a sternum
    groove and a firmer lower pec line, so the shape under the knit reads athletic, not soft."""
    co, n = mesh_np(me), normals_np(me)
    ax_, z_ = np.abs(co[:, 0]), co[:, 2]
    front_ = np.clip(-n[:, 1] * 2.0, 0, 1)
    g = lambda cx, cz, sx, sz: np.exp(-(((ax_ - cx) / sx) ** 2 + ((z_ - cz) / sz) ** 2))
    d = (0.003 * g(0.07, 1.27, 0.055, 0.035)
         - 0.0055 * g(0.115, 1.165, 0.06, 0.035)
         - float(ARGS.get("pec_tip", 0.0045)) * g(0.12, 1.2, 0.045, 0.04)   # round off the pec apex so the knit doesn't tent into a point
         - 0.0012 * np.exp(-((co[:, 0] / 0.02) ** 2 + ((z_ - 1.22) / 0.065) ** 2)))
    # no carved pit or line under the pecs: the knit dipped into them and drew two points
    set_co(me, co + n * (d * front_)[:, None])


define_muscles(body.data)

# ---------------------------------------------------------------- tank top boundary
NECK_XF = float(ARGS.get("neck_xf", 0.045))   # half-width of the flat bottom of the square neck
NECK_R = float(ARGS.get("neck_r", 0.012))     # corner radius
NECK_Z = float(ARGS.get("neck_z", 1.29))     # lowest point of the neckline


def square_neck(a):
    """Square neckline: flat across the chest, rounded corners, straight sides up to the straps."""
    a = np.minimum(a, 0.065)
    u = np.clip(a - NECK_XF, 0, NECK_R)
    corner = NECK_R - np.sqrt(np.maximum(NECK_R ** 2 - u ** 2, 0))
    side = np.maximum(a - NECK_XF - NECK_R, 0) * 60
    return np.minimum(NECK_Z + corner + side, 1.45)


# classic ribbed A-shirt (reference: Abanderado): wide U scoop, narrow straps set out towards the
# shoulders, very deep armholes
STRAP_IN = float(ARGS.get("strap_in", 0.088))
STRAP_OUT = float(ARGS.get("strap_out", 0.116))


def u_neck(a):
    return NECK_Z + (1.43 - NECK_Z) * (np.minimum(a, STRAP_IN) / STRAP_IN) ** float(ARGS.get("neck_pow", 4.0))


def top_front(a):
    neck = square_neck(a) if ARGS.get("neck") == "square" else u_neck(a)
    arm = 1.45 - 0.36 * smooth((a - STRAP_OUT) / 0.05)
    return np.where(a < STRAP_IN, neck, np.where(a < STRAP_OUT, 9.0, arm))


def top_back(a):
    neck = 1.40 + 0.03 * (np.minimum(a, STRAP_IN) / STRAP_IN) ** 2
    arm = 1.45 - 0.36 * smooth((a - STRAP_OUT) / 0.05)
    return np.where(a < STRAP_IN, neck, np.where(a < STRAP_OUT, 9.0, arm))


def boundary_poly(topf):
    a1 = np.linspace(0, STRAP_IN, 400)
    a2 = np.linspace(STRAP_OUT, 0.30, 120)
    p = [np.stack([a1, topf(a1)], 1), None, None, np.stack([a2, topf(a2)], 1)]
    return [np.array(p[0]), np.array([[STRAP_IN, topf(np.array([STRAP_IN - 0.001]))[0]], [STRAP_IN, 1.6]]),
            np.array([[STRAP_OUT, 1.6], [STRAP_OUT, 1.45]]), np.array(p[3])]


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
inside = (z < top) & (z < 1.5) & (W_CUT < 0.02)

bm = bmesh.new()
bm.from_mesh(body.data)
bm.verts.ensure_lookup_table()
keep = {f.index for f in bm.faces if all(inside[v.index] for v in f.verts)}
bm.faces.ensure_lookup_table()
for _ in range(4):
    # drop ragged peninsulas: faces held by fewer than two kept neighbours
    drop = {fi for fi in keep if sum(1 for e in bm.faces[fi].edges for lf in e.link_faces
                                     if lf.index != fi and lf.index in keep) < 2}
    if not drop:
        break
    keep -= drop
keep_faces = [bm.faces[fi] for fi in sorted(keep)]
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
# the arm cut leaves a stair-stepped border where no snap applies: relax it along the border loop,
# then put it back on the skin
bedges = np.array([[e.verts[0].index, e.verts[1].index] for e in sbm.edges if e.is_boundary])
loose = border & ~snap
body_bvh = BVHTree.FromBMesh(bm)
dg_ = np.bincount(bedges.ravel(), minlength=len(sco))[:, None]
for rnd in range(4):
    for _ in range(25):
        acc = np.zeros_like(sco)
        np.add.at(acc, bedges[:, 0], sco[bedges[:, 1]])
        np.add.at(acc, bedges[:, 1], sco[bedges[:, 0]])
        avg = acc / np.maximum(dg_, 1)
        sco[border] += (avg[border] - sco[border]) * np.where(loose[border], 0.5, 0.25)[:, None]
    for i in np.nonzero(border)[0]:
        h_ = body_bvh.find_nearest(Vector(sco[i]))
        if h_[0] is not None:
            sco[i] = h_[0][:]
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
for _ in range(int(ARGS.get("bridge_it", 110)) * LAP):
    acc = np.zeros_like(sm)
    np.add.at(acc, edges[:, 0], sm[edges[:, 1]])
    np.add.at(acc, edges[:, 1], sm[edges[:, 0]])
    nxt = acc / np.maximum(deg, 1)[:, None]
    nxt[border] = sco[border]
    sm = 0.5 * sm + 0.5 * nxt
_bd = ((sm - sco) * sn).sum(1)
bridge = 0.5 * (_bd + np.sqrt(_bd ** 2 + 0.0012 ** 2)) - 0.0006   # soft max(0, d): a hard kink drew a crease under the pecs
s_ax = np.abs(sco[:, 0])
P = np.stack([s_ax, sco[:, 2]], 1)
edge_d = np.where(s_front, dist_to_polys(P, boundary_poly(top_front)), dist_to_polys(P, boundary_poly(top_back)))
band = 1 - smooth((edge_d - 0.008) / 0.002)        # binding band at neckline/armholes
# knit stretched over the chest: a parabolic "closing" of the front surface. The fabric rests on the
# high points (pecs) and spans the hollows below them like taut cloth instead of dipping into them.
def drape_envelope(P, k):
    """Lower envelope of upward parabolas k*d^2 over a depth map (separable, exact)."""
    gx = np.arange(-0.20, 0.2001, 0.002)
    gz = np.arange(0.95, 1.4501, 0.002)
    D = np.full((len(gz), len(gx)), np.inf)
    ix = np.clip(np.round((P[:, 0] - gx[0]) / 0.002).astype(int), 0, len(gx) - 1)
    iz = np.clip(np.round((P[:, 2] - gz[0]) / 0.002).astype(int), 0, len(gz) - 1)
    np.minimum.at(D, (iz, ix), P[:, 1])
    big = 1.0
    D = np.where(np.isinf(D), big, D)
    dx = (gx[:, None] - gx[None, :]) ** 2 * k
    E = np.min(D[:, None, :] + dx[None, :, :], axis=2)
    dz = (gz[:, None] - gz[None, :]) ** 2 * k
    E = np.min(E.T[:, None, :] + dz[None, :, :], axis=2).T
    return E[iz, ix]


front_face = s_front & (sn[:, 1] < -0.35)
env = drape_envelope(np.where(front_face[:, None], sco, [0, 9.0, 0]), float(ARGS.get("drape_k", 16.0)))
env_push = np.where(front_face, np.maximum(sco[:, 1] - env, 0), 0) * np.clip(-sn[:, 1], 0, 1)
# only below the pecs' crest: higher up (collarbones, straps) the knit lies on the skin
env_push *= 1 - smooth((sco[:, 2] - 1.2) / 0.05)
env_push = np.minimum(env_push, 0.007)
bridge = np.maximum(bridge, env_push)
push = 0.0011 + bridge + 0.0005 * band
# drag lines: the armholes pull the knit diagonally towards the sternum; soft bunching under the pecs
fold = np.zeros(len(sco))
xs_, zs_ = sco[:, 0], sco[:, 2]
for side in (1, -1):
    a0 = np.array([0.15 * side, 1.20])
    dv = np.array([-0.13 * side, -0.075]); dv /= np.linalg.norm(dv)
    rel = np.stack([xs_ - a0[0], zs_ - a0[1]], 1)
    along, across = rel @ dv, rel @ np.array([-dv[1], dv[0]])
    m_ = smooth(along / 0.015) * (1 - smooth((along - 0.03) / 0.09)) * np.exp(-(across / 0.035) ** 2) * s_front
    fold += float(ARGS.get("drag", 0.0)) * m_ * (0.5 + 0.5 * np.cos(2 * np.pi * across / 0.019 + 0.8 * side))
under = np.exp(-((np.abs(xs_) - 0.09) / 0.06) ** 2) * np.exp(-((zs_ - 1.16) / 0.03) ** 2) * s_front
drape = np.exp(-((np.abs(xs_) - 0.075) / 0.06) ** 2) * smooth((1.165 - zs_) / 0.05) * s_front
fold += float(ARGS.get("drape", 0.0007)) * drape * (0.5 + 0.5 * np.cos(2 * np.pi * (np.abs(xs_) - 0.075) / 0.032 + 4 * (1.17 - zs_)))
fold *= 1 - band
set_co(shirt_me, sco + sn * (push + fold)[:, None])
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


SKIN_TEX = ROOT + "tex/2K-human_skin_1_"   # ShareTextures «Human Skin 1» (CC0), scanned skin patch


def box_tex(nt, oc, name, tile, noncolor=True):
    """Scanned skin patch box-projected on the body (no UVs needed), tile = metres per repeat."""
    it = nt.nodes.new("ShaderNodeTexImage")
    it.image = bpy.data.images.load(SKIN_TEX + name + ".jpg", check_existing=True)
    if noncolor:
        it.image.colorspace_settings.name = "Non-Color"
    it.projection = "BOX"
    it.projection_blend = 0.3
    mp = nt.nodes.new("ShaderNodeMapping")
    mp.inputs["Scale"].default_value = (1 / tile, 1 / tile, 1 / tile)
    nt.links.new(oc, mp.inputs["Vector"])
    nt.links.new(mp.outputs["Vector"], it.inputs["Vector"])
    return it.outputs["Color"]


def skin_material():
    mat = bpy.data.materials.new("skin")
    nt, p = principled(mat)
    oc = obj_coords(nt)
    # tone: deep warm brown with mottling; redder and warmer over the shoulders, deeper in the creases
    mott = noise(nt, oc, 18, 6, 0.6)
    tone0 = ramp(nt, mott, [(0.3, (0.118, 0.054, 0.029, 1)), (0.7, (0.148, 0.07, 0.039, 1))])
    sepo = nt.nodes.new("ShaderNodeSeparateXYZ")
    nt.links.new(oc, sepo.inputs[0])
    warm_f = math_node(nt, "MULTIPLY", math_node(nt, "SUBTRACT", math_node(nt, "ABSOLUTE", sepo.outputs["X"]), 0.07), 7.0, True)
    warm = nt.nodes.new("ShaderNodeMix")
    warm.data_type = "RGBA"
    nt.links.new(warm_f, sock(warm.inputs, "Factor_Float"))
    nt.links.new(tone0, sock(warm.inputs, "A_Color"))
    sock(warm.inputs, "B_Color").default_value = (0.175, 0.07, 0.035, 1)
    ao = nt.nodes.new("ShaderNodeAmbientOcclusion")
    ao.inputs["Distance"].default_value = 0.035
    crease = nt.nodes.new("ShaderNodeMix")
    crease.data_type = "RGBA"
    crease.blend_type = "MULTIPLY"
    nt.links.new(math_node(nt, "MULTIPLY", math_node(nt, "SUBTRACT", 1.0, ao.outputs["AO"]), 1.3, True), sock(crease.inputs, "Factor_Float"))
    nt.links.new(sock(warm.outputs, "Result_Color"), sock(crease.inputs, "A_Color"))
    sock(crease.inputs, "B_Color").default_value = (0.42, 0.3, 0.27, 1)
    tone = sock(crease.outputs, "Result_Color")
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
    sock(mix2.inputs, "B_Color").default_value = (0.7, 0.6, 0.56, 1)
    # blotchy mid-scale variation (sun, blood flow) and fine follicle dots so the albedo never reads as paint
    blot = noise(nt, oc, 55, 5, 0.65)
    mix3 = nt.nodes.new("ShaderNodeMix")
    mix3.data_type = "RGBA"
    mix3.blend_type = "MULTIPLY"
    nt.links.new(math_node(nt, "MULTIPLY", math_node(nt, "ABSOLUTE", math_node(nt, "SUBTRACT", blot, 0.5)), 1.4, True), sock(mix3.inputs, "Factor_Float"))
    nt.links.new(sock(mix2.outputs, "Result_Color"), sock(mix3.inputs, "A_Color"))
    sock(mix3.inputs, "B_Color").default_value = (0.82, 0.74, 0.72, 1)
    foll = nt.nodes.new("ShaderNodeTexVoronoi")
    foll.inputs["Scale"].default_value = 520
    foll.inputs["Randomness"].default_value = 1.0
    nt.links.new(oc, foll.inputs["Vector"])
    dots = math_node(nt, "LESS_THAN", foll.outputs["Distance"], 0.09)
    mix4 = nt.nodes.new("ShaderNodeMix")
    mix4.data_type = "RGBA"
    mix4.blend_type = "MULTIPLY"
    nt.links.new(math_node(nt, "MULTIPLY", dots, 0.18), sock(mix4.inputs, "Factor_Float"))
    nt.links.new(sock(mix3.outputs, "Result_Color"), sock(mix4.inputs, "A_Color"))
    sock(mix4.inputs, "B_Color").default_value = (0.55, 0.45, 0.42, 1)
    # real skin micro-colour from the scan, normalised by its mean so it only adds variation
    TILE = float(ARGS.get("skin_tile", 0.06))
    alb = box_tex(nt, oc, "diffuseOriginal", TILE, noncolor=False)
    norm_ = nt.nodes.new("ShaderNodeMix")
    norm_.data_type = "RGBA"
    norm_.blend_type = "MULTIPLY"
    sock(norm_.inputs, "Factor_Float").default_value = 1.0
    nt.links.new(alb, sock(norm_.inputs, "A_Color"))
    sock(norm_.inputs, "B_Color").default_value = (1 / 0.4483, 1 / 0.1924, 1 / 0.0752, 1)
    mix5 = nt.nodes.new("ShaderNodeMix")
    mix5.data_type = "RGBA"
    mix5.blend_type = "MULTIPLY"
    sock(mix5.inputs, "Factor_Float").default_value = float(ARGS.get("skin_detail", 0.7))
    nt.links.new(sock(mix4.outputs, "Result_Color"), sock(mix5.inputs, "A_Color"))
    nt.links.new(sock(norm_.outputs, "Result_Color"), sock(mix5.inputs, "B_Color"))
    nt.links.new(sock(mix5.outputs, "Result_Color"), inp(p, "Base Color"))
    inp(p, "Subsurface Weight").default_value = 1.0
    inp(p, "Subsurface Radius").default_value = (1.0, 0.42, 0.24)
    inp(p, "Subsurface Scale").default_value = 0.006
    try:
        p.subsurface_method = ARGS.get("sss", "RANDOM_WALK_SKIN")
    except TypeError:
        pass
    # roughness: oilier on the sternum, varied elsewhere
    # no clear coat (that is what made it read as plastic): broken-up roughness, oilier patches, rougher pores
    rn = noise(nt, oc, 40, 3)
    oil = math_node(nt, "GREATER_THAN", noise(nt, oc, 12, 3, 0.5), 0.55)
    rough_ = math_node(nt, "ADD", math_node(nt, "MULTIPLY", rn, 0.18), 0.40)
    rough_ = math_node(nt, "SUBTRACT", rough_, math_node(nt, "MULTIPLY", oil, 0.08))
    sm_ = nt.nodes.new("ShaderNodeSeparateColor")
    nt.links.new(box_tex(nt, oc, "smoothness", float(ARGS.get("skin_tile", 0.06))), sm_.inputs[0])
    rough_ = math_node(nt, "ADD", rough_, math_node(nt, "MULTIPLY", math_node(nt, "SUBTRACT", 0.226, sm_.outputs[0]), 5.0))
    nt.links.new(rough_, inp(p, "Roughness"))
    inp(p, "Specular IOR Level").default_value = 0.5
    inp(p, "Coat Weight").default_value = 0.0
    inp(p, "Coat Roughness").default_value = 0.28
    inp(p, "Sheen Weight").default_value = 0.08
    inp(p, "Sheen Roughness").default_value = 0.45
    inp(p, "Sheen Tint").default_value = (1, 0.82, 0.7, 1)
    # micro surface: pores, fine crosshatch wrinkles, broad unevenness
    vor = nt.nodes.new("ShaderNodeTexVoronoi")
    vor.inputs["Scale"].default_value = 820
    vor.inputs["Randomness"].default_value = 0.9
    nt.links.new(oc, vor.inputs["Vector"])
    pores = math_node(nt, "SMOOTH_MAX" if False else "POWER", math_node(nt, "MINIMUM", math_node(nt, "MULTIPLY", vor.outputs["Distance"], 2.2), 1.0), 0.5)
    hs_ = nt.nodes.new("ShaderNodeSeparateColor")
    nt.links.new(box_tex(nt, oc, "height", float(ARGS.get("skin_tile", 0.06))), hs_.inputs[0])
    scan_h = math_node(nt, "MULTIPLY", math_node(nt, "SUBTRACT", hs_.outputs[0], 0.5), float(ARGS.get("skin_h", 60.0)))
    n0 = bump(nt, scan_h, 0.6, 0.0002)
    n1 = bump(nt, pores, 0.2, 0.00022, n0)
    fine = noise(nt, oc, 2600, 3, 0.7)
    n2 = bump(nt, fine, 0.12, 0.0002, n1)
    # skin cell lines: two stretched wave patterns crossing at ~60 deg
    cells = None
    for rot_ in (0.5, -0.55):
        mpn = nt.nodes.new("ShaderNodeMapping")
        mpn.inputs["Rotation"].default_value = (0.3, 0.2, rot_)
        mpn.inputs["Scale"].default_value = (1, 6, 1)
        nt.links.new(oc, mpn.inputs["Vector"])
        wv = nt.nodes.new("ShaderNodeTexWave")
        wv.inputs["Scale"].default_value = 380
        wv.inputs["Distortion"].default_value = 6
        wv.inputs["Detail"].default_value = 3
        nt.links.new(mpn.outputs["Vector"], wv.inputs["Vector"])
        cells = wv.outputs["Fac"] if cells is None else math_node(nt, "MINIMUM", cells, wv.outputs["Fac"])
    n2b = bump(nt, cells, 0.22, 0.0002, n2)
    broad = noise(nt, oc, 90, 4, 0.6)
    n3 = bump(nt, broad, 0.1, 0.002, n2b)
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
    rib = math_node(nt, "SINE", math_node(nt, "MULTIPLY", sep.outputs["X"], 2 * math.pi / 0.0024))
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
    n1 = bump(nt, h, 1.0, 0.0006)
    wr = noise(nt, oc, 22, 3, 0.5)
    n2 = bump(nt, wr, 0.08, 0.003, n1)
    nt.links.new(n2, inp(p, "Normal"))
    col = ramp(nt, fiber, [(0.3, (0.40, 0.395, 0.38, 1)), (0.7, (0.47, 0.46, 0.445, 1))])
    # knit reads as knit: the valleys between cords are a touch darker, the sewn binding slightly greyer
    knit = nt.nodes.new("ShaderNodeMix")
    knit.data_type = "RGBA"
    knit.blend_type = "MULTIPLY"
    nt.links.new(math_node(nt, "MULTIPLY", math_node(nt, "SUBTRACT", 1.0, ribmix.outputs[0]), 0.35), sock(knit.inputs, "Factor_Float"))
    nt.links.new(col, sock(knit.inputs, "A_Color"))
    sock(knit.inputs, "B_Color").default_value = (0.55, 0.55, 0.56, 1)
    nt.links.new(sock(knit.outputs, "Result_Color"), inp(p, "Base Color"))
    inp(p, "Roughness").default_value = 0.92
    # cotton jersey is slightly translucent: light softens into it instead of bouncing off a white shell
    inp(p, "Subsurface Weight").default_value = 0.35
    inp(p, "Subsurface Radius").default_value = (1.0, 0.95, 0.9)
    inp(p, "Subsurface Scale").default_value = 0.0015
    inp(p, "Sheen Weight").default_value = 0.7
    inp(p, "Sheen Roughness").default_value = 0.35
    inp(p, "Specular IOR Level").default_value = 0.3
    return mat


def silver(name, rough, wave=False, tilt=None, chrome=False):
    mat = bpy.data.materials.new(name)
    nt, p = principled(mat)
    inp(p, "Metallic").default_value = 1.0
    # chrome faces: dim the true (Cycles) mirror so the flat letter faces don't just mirror the big key
    # light / white knit as one flat white; the reflection-vector bands then carry the light-dark contrast
    b_ = float(ARGS.get("chrome_base", 0.3)) if chrome else 0.96
    inp(p, "Base Color").default_value = (b_, b_ * 0.995, b_ * 0.98, 1)
    try:
        inp(p, "Specular Tint").default_value = (0.99, 0.98, 0.96, 1)
    except KeyError:
        pass
    oc = obj_coords(nt)
    smudge = noise(nt, oc, 160, 4, 0.6)
    nt.links.new(math_node(nt, "ADD", math_node(nt, "MULTIPLY", smudge, 0.05), rough - 0.02), inp(p, "Roughness"))
    if wave:
        nt.links.new(bump(nt, noise(nt, oc, 45, 2, 0.5), 0.04, 0.0004), inp(p, "Normal"))
    if chrome:
        chrome_bands(nt, p, oc)
    else:
        studio_reflect(nt, p, 1.0, tilt)
    return mat, nt, p


STUDIO = None


def chrome_bands(nt, p, oc):
    """Product-shot chrome for big flat faces: soft light/dark bands looked up by the reflection vector,
    skewed across the piece so the faces never read as one flat grey; the bands sweep as the plate moves."""
    tc = nt.nodes.new("ShaderNodeTexCoord")
    rv = nt.nodes.new("ShaderNodeSeparateXYZ")
    nt.links.new(tc.outputs["Reflection"], rv.inputs[0])
    ov = nt.nodes.new("ShaderNodeSeparateXYZ")
    nt.links.new(oc, ov.inputs[0])
    k = float(ARGS.get("band_k", 3.2))
    c = math_node(nt, "ADD", math_node(nt, "MULTIPLY", rv.outputs["Z"], k), math_node(nt, "MULTIPLY", rv.outputs["X"], 1.4))
    c = math_node(nt, "ADD", c, math_node(nt, "MULTIPLY", ov.outputs["X"], 9.0))
    c = math_node(nt, "ADD", c, math_node(nt, "MULTIPLY", ov.outputs["Y"], -14.0))
    c = math_node(nt, "ADD", c, math_node(nt, "MULTIPLY", noise(nt, oc, 30, 2, 0.5), 0.25))
    c = math_node(nt, "FRACT", math_node(nt, "ADD", c, float(ARGS.get("band_off", 0.66))))
    col = ramp(nt, c, [(0.0, (0.03, 0.03, 0.032, 1)), (0.18, (0.6, 0.6, 0.61, 1)), (0.3, (1.0, 1.0, 1.0, 1)),
                       (0.42, (0.12, 0.12, 0.125, 1)), (0.62, (0.05, 0.05, 0.052, 1)), (0.8, (0.36, 0.36, 0.37, 1)),
                       (1.0, (0.03, 0.03, 0.032, 1))])
    nt.links.new(col, inp(p, "Emission Color"))
    inp(p, "Emission Strength").default_value = float(ARGS.get("chrome_gain", 1.6))


def studio_reflect(nt, p, strength, tilt=None):
    """Mirror a studio HDRI by the reflection vector into emission: EEVEE cannot see off-screen
    softboxes, so the chrome gets its product-shot reflections from here."""
    global STUDIO
    if STUDIO is None:
        STUDIO = bpy.data.images.load(ROOT + "studio_small_09.hdr")
    tc = nt.nodes.new("ShaderNodeTexCoord")
    mp = nt.nodes.new("ShaderNodeMapping")
    mp.inputs["Rotation"].default_value = (math.radians(float(ARGS.get("envtilt", 0)) if tilt is None else tilt), 0, math.radians(float(ARGS.get("envrot", 45))))
    nt.links.new(tc.outputs["Reflection"], mp.inputs["Vector"])
    env = nt.nodes.new("ShaderNodeTexEnvironment")
    env.image = STUDIO
    nt.links.new(mp.outputs["Vector"], env.inputs["Vector"])
    nt.links.new(env.outputs["Color"], inp(p, "Emission Color"))
    if isinstance(strength, (int, float)):
        inp(p, "Emission Strength").default_value = strength * float(ARGS.get("envgain", 0.6))
    else:
        nt.links.new(math_node(nt, "MULTIPLY", strength, float(ARGS.get("envgain", 0.6))), inp(p, "Emission Strength"))


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
    if ARGS.get("arms", "keys") != "armature":
        continue
    am = ob.modifiers.new("arms", "ARMATURE")
    am.object = arm
    am.use_deform_preserve_volume = ARGS.get("dq", "0") == "1"
sol = shirt.modifiers.new("thickness", "SOLIDIFY")
sol.thickness = 0.0007
sol.offset = -1
sol.use_even_offset = True

for nm, sgn in (("arm.L", 1), ("arm.R", -1)):
    pb = arm.pose.bones[nm]
    pb.rotation_mode = "XYZ"
    drv(pb, "rotation_euler", 0, f"{0.075 * sgn}*sin(2*pi*frame/{STRIDE}+1.2)")

ARM_SWING = 0.075


def arm_swing_keys(ob, w_arm):
    """Arm swing as shape keys (rotation about each shoulder, blended by the arm weight). The Armature
    modifier left a visible crease along the weight falloff in Cycles; these keys deform smoothly."""
    co = mesh_np(ob.data)
    ob.shape_key_add(name="Basis")
    for side, sgn in ((1, 1), (-1, -1)):
        piv = np.array([0.19 * side, -0.03, 1.36])
        th = ARM_SWING * np.where(np.sign(co[:, 0]) == side, w_arm, 0.0)
        d = co - piv
        c_, s_ = np.cos(th), np.sin(th)
        out = co.copy()
        out[:, 1] = piv[1] + d[:, 1] * c_ - d[:, 2] * s_
        out[:, 2] = piv[2] + d[:, 1] * s_ + d[:, 2] * c_
        kb = ob.shape_key_add(name=f"swing_{side}")
        kb.slider_min = -1.0
        kb.data.foreach_set("co", out.astype(np.float32).ravel())
        drv(kb, "value", None, f"{sgn}*sin(2*pi*frame/{STRIDE}+1.2)")


if ARGS.get("arms", "keys") == "keys":
    arm_swing_keys(body, W_ARM)
    arm_swing_keys(shirt, w_arm_shirt)

# walk cycle: weight shift once per stride (dwelling over each foot), bob twice per stride (sharper dip at
# heel strike), forward pitch per step, lateral lean, shoulders counter-rotating; breathing on top.
# The same expressions drive the rig and feed the pendant simulation (rig_pose).
W1, W2, W3 = f"2*pi*frame/{STRIDE}", f"2*pi*frame/{STEP}", f"2*pi*frame/{BREATH}"
RIG_EXPR = {
    ("location", 0): f"{SWAY}*(sin({W1})+0.14*sin(3*({W1})))",
    ("location", 1): f"{CHEST.y}+0.0018*sin({W2}+1.0)",
    ("location", 2): f"{CHEST.z}+{BOB}*(cos({W2})-0.22*cos(2*({W2})))+0.0016*sin({W3})",
    ("rotation_euler", 0): f"0.009*sin({W2}+0.5)-0.006*sin({W3})",
    ("rotation_euler", 1): f"0.018*sin({W1}+0.4)",
    ("rotation_euler", 2): f"{TWIST}*(sin({W1}+1.2)+0.1*sin(3*({W1})+1.2))",
}
for (pth, i), ex in RIG_EXPR.items():
    drv(rig, pth, i, ex)

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


# ---------------------------------------------------------------- nameplate (kufi wordmark, Jäger style)
SVG_S = float(ARGS.get("plate_w", 0.112)) / 2906   # metres per svg unit (wordmark is 2906 wide)
LUG_V = 360.0                                     # svg y of the two side lugs (hinge line)
LUG_U = (-38.0, 2872.0)                           # svg x of the lug holes (left of «b», right of the star)
U0 = sum(LUG_U) / 2
THICK = 0.0034                                    # letter depth
BEVEL = 0.00035
LUG_R, LUG_HOLE = 78.0, 36.0
RING_MAJ, RING_MIN = 0.0024, 0.0006


def svg_polys(path):
    d = re.search(r'd="([^"]+)"', open(path).read()).group(1)
    return [np.array(p, float) for p in (re.findall(r"([\d.]+) ([\d.]+)", sp) for sp in d.split("Z")) if len(p) >= 3]


def area2(p):
    return 0.5 * (p[:, 0] * np.roll(p[:, 1], -1) - np.roll(p[:, 0], -1) * p[:, 1]).sum()


def to_plate(p):
    """svg units -> plate local metres: x right, y up, hinge (lug) line at y=0."""
    return np.stack([(p[:, 0] - U0) * SVG_S, (LUG_V - p[:, 1]) * SVG_S], 1)


def span_at(poly, y):
    xs = []
    for a, b in zip(poly, np.roll(poly, -1, 0)):
        if (a[1] - y) * (b[1] - y) < 0:
            xs.append(a[0] + (y - a[1]) * (b[0] - a[0]) / (b[1] - a[1]))
    return (min(xs), max(xs)) if xs else None


def bar(p, q, w):
    """Quad of width w from p to q (svg units), overshooting both ends a little."""
    p, q = np.array(p, float), np.array(q, float)
    d = (q - p) / np.linalg.norm(q - p)
    n = np.array([-d[1], d[0]]) * w / 2
    p, q = p - d * 22, q + d * 22
    return np.array([p + n, q + n, q - n, p - n])


def circle(c, r, n=40):
    a = np.linspace(0, 2 * math.pi, n, endpoint=False)
    return np.stack([c[0] + r * np.cos(a), c[1] + r * np.sin(a)], 1)


polys = svg_polys(ROOT + "wordmark-kufi.svg")
outer = [p for p in polys if area2(p) > 0]
letters = sorted([p for p in outer if area2(p) > 60000], key=lambda p: p[:, 0].min())
dots = [p for p in outer if area2(p) <= 60000]
# connectors: a short bar across every gap between neighbouring letters, low in the x-height
links_svg = []
for a_, b_ in zip(letters[:-1], letters[1:]):
    sa, sb = span_at(a_, 650.0), span_at(b_, 650.0)
    if sa and sb and sb[0] > sa[1] - 5:
        links_svg.append(bar((sa[1], 650.0), (sb[0], 650.0), 46))
# floating dots hang from the nearest letter
for dp in dots:
    best = None
    for lp in letters:
        for v in dp:
            for a_, b_ in zip(lp, np.roll(lp, -1, 0)):
                ab = b_ - a_
                t_ = np.clip((v - a_) @ ab / (ab @ ab), 0, 1)
                q_ = a_ + t_ * ab
                dd = np.linalg.norm(v - q_)
                if best is None or dd < best[0]:
                    best = (dd, v, q_)
    links_svg.append(bar(best[1], best[2], 40))
lugs_svg = []
for u in LUG_U:
    lugs_svg += [circle((u, LUG_V), LUG_R), circle((u, LUG_V), LUG_HOLE, 28)]


def extruded(name, polys_svg, depth, z_off, bevel, mat):
    cu = bpy.data.curves.new(name, "CURVE")
    cu.dimensions = "2D"
    cu.fill_mode = "BOTH"
    cu.extrude = max(depth / 2 - bevel, 1e-5)
    cu.bevel_depth = bevel
    cu.bevel_resolution = 4
    cu.offset = -bevel
    for p in polys_svg:
        q = to_plate(p)
        sp_ = cu.splines.new("POLY")
        sp_.points.add(len(q) - 1)
        for pt, (x_, y_) in zip(sp_.points, q):
            pt.co = (x_, y_, 0, 1)
        sp_.use_cyclic_u = True
    tmp = bpy.data.objects.new(name + "_cu", cu)
    sc.collection.objects.link(tmp)
    bpy.context.view_layer.update()
    me_ = bpy.data.meshes.new_from_object(tmp.evaluated_get(bpy.context.evaluated_depsgraph_get()))
    bpy.data.objects.remove(tmp)
    me_.name = name
    try:
        me_.shade_smooth()
        me_.set_sharp_from_angle(angle=math.radians(32))
    except AttributeError:
        for p_ in me_.polygons:
            p_.use_smooth = True
    ob = bpy.data.objects.new(name, me_)
    sc.collection.objects.link(ob)
    ob.location = (0, 0, z_off)
    ob.data.materials.append(mat)
    return ob


m_polish, _, _ = silver("silver_polished", 0.05, wave=True, chrome=True)
plate = extruded("plate_letters", polys, THICK, 0.0, BEVEL, m_polish)
plate_links = extruded("plate_links", links_svg, 0.0016, -THICK / 2 + 0.0009, 0.0002, m_polish)
plate_lugs = extruded("plate_lugs", lugs_svg, 0.0016, 0.0, 0.0003, m_polish)

# rest placement: average chest normal over the footprint, then lift until the back clears skin and fabric
HINGE_Z = float(ARGS.get("hinge_z", 1.255))   # below the bottom of the scoop: the plate rests on the knit
ns = []
for xx_ in np.linspace(-0.04, 0.04, 9):
    for zz_ in np.linspace(HINGE_Z - 0.016, HINGE_Z + 0.004, 5):
        h_ = surf((xx_, -1, zz_), (0, 1, 0))
        if h_:
            ns.append(-h_[1] if h_[1].y > 0 else h_[1])
N0 = Vector(np.mean(ns, 0)).normalized()
P0 = surf((0, -1, HINGE_Z), (0, 1, 0))[0]
up = (Vector((0, 0, 1)) - N0 * N0.z).normalized()
xax = up.cross(N0).normalized()
frame_m = Matrix((xax, up, N0)).transposed()   # columns: x, y(up), z(normal)
foot = np.concatenate([to_plate(p) for p in polys] + [to_plate(p) for p in links_svg])
lift = 0.0
for x_, y_ in foot[::2]:
    p_ = P0 + frame_m @ Vector((x_, y_, -THICK / 2))
    h_ = surf(p_ - N0 * 0.03, N0)
    if h_:
        lift = max(lift, (h_[0] - p_).dot(N0))
hinge = P0 + N0 * (lift + 0.0004)
plate_c = hinge + frame_m @ Vector((0, -0.0035, THICK / 2))
print("plate normal", N0, "lift", lift)

piv_base = bpy.data.objects.new("pendant_base", None)
sc.collection.objects.link(piv_base)
piv_base.parent = rig
piv_base.matrix_parent_inverse = Matrix.Identity(4)
piv_base.matrix_basis = Matrix.Translation(hinge - CHEST) @ frame_m.to_4x4()
swing = bpy.data.objects.new("pendant_swing", None)
sc.collection.objects.link(swing)
swing.parent = piv_base
swing.rotation_mode = "XYZ"


def torus(name, major, minor, seg=48, mseg=14, mat=None):
    verts = []
    for i in range(seg):
        a = 2 * math.pi * i / seg
        for k in range(mseg):
            b = 2 * math.pi * k / mseg
            rr2 = major + minor * math.cos(b)
            verts.append((rr2 * math.cos(a), rr2 * math.sin(a), minor * math.sin(b)))
    faces = [(i * mseg + k, ((i + 1) % seg) * mseg + k, ((i + 1) % seg) * mseg + (k + 1) % mseg, i * mseg + (k + 1) % mseg)
             for i in range(seg) for k in range(mseg)]
    me_ = bpy.data.meshes.new(name)
    me_.from_pydata(verts, [], faces)
    for p_ in me_.polygons:
        p_.use_smooth = True
    ob = bpy.data.objects.new(name, me_)
    sc.collection.objects.link(ob)
    if mat:
        ob.data.materials.append(mat)
    return ob


# jump rings stand through the lug holes, in the plane of the plate normal and "up"
ring_top_plate = {}
for side, u in ((-1, LUG_U[0]), (1, LUG_U[1])):
    lx = (u - U0) * SVG_S
    jr = torus(f"jump_ring_{side}", RING_MAJ, RING_MIN, mat=m_polish)
    jr.rotation_euler = (0, math.pi / 2, 0)
    jr.location = (lx, RING_MAJ - LUG_HOLE * SVG_S * 0.5, 0)
    ring_top_plate[side] = Vector((lx, 2 * RING_MAJ - LUG_HOLE * SVG_S * 0.5, 0))
    jr.parent = swing
    jr.matrix_parent_inverse = Matrix.Identity(4)
for ob in (plate, plate_links, plate_lugs):
    ob.parent = swing
    ob.matrix_parent_inverse = Matrix.Identity(4)

# ---------------------------------------------------------------- pendant dynamics (simulated, then baked)
# The plate hangs from two strands: sideways it behaves like a pendulum of length LP; it can also hinge
# out from the chest about its lug line. The chest motion is the rig motion below plus a jolt at every
# heel strike. Integrated for several loops so the last one is the periodic steady state.
LP = 0.085
KPS = 3 / (4 * 0.013)
HS = STEP / 2                        # heel strike: lowest point of the bob


RIG_CODE = {k: compile(v, "rig", "eval") for k, v in RIG_EXPR.items()}


def rig_pose(f):
    env = {"frame": f, "sin": math.sin, "cos": math.cos, "pi": math.pi}
    v = {k: eval(c, env) for k, c in RIG_CODE.items()}
    loc = Vector([v[("location", i)] for i in range(3)])
    rot = Euler([v[("rotation_euler", i)] for i in range(3)], "XYZ").to_matrix()
    return loc, rot


SUB = 20
DT = 1 / (30 * SUB)
hinge_l = hinge - CHEST
gx0, gy0, gn0, pulse, foot_side = (np.zeros(T * SUB) for _ in range(5))


def pivot_world(f):
    loc, rot = rig_pose(f)
    return loc + rot @ hinge_l


for i in range(T * SUB):
    f = i / SUB
    h = 1 / SUB
    acc = (pivot_world(f + h) - 2 * pivot_world(f) + pivot_world(f - h)) / DT ** 2
    F = rig_pose(f)[1] @ frame_m
    g = F.transposed() @ (Vector((0, 0, -9.81)) - acc)
    gx0[i], gy0[i], gn0[i] = g
    d = (f - HS + STEP / 2) % STEP - STEP / 2
    pulse[i] = math.exp(-0.5 * (d / 1.3) ** 2)
    foot_side[i] = 1 if round((f - HS) / STEP) % 2 == 0 else -1


def simulate(kick, lat, loops=6):
    th = om = ps = vp = 0.0
    out = np.zeros((T, 2))
    for lp in range(loops):
        for i in range(T * SUB):
            gx = gx0[i] + lat * foot_side[i] * pulse[i]
            gn = gn0[i] + kick * pulse[i]
            gy = gy0[i]
            touching = ps < 0.004
            om += DT * ((gx * math.cos(th) + gy * math.sin(th)) / LP - (1.0 + 5.0 * touching) * om)
            th += DT * om
            vp += DT * (KPS * (gy * math.sin(ps) + gn * math.cos(ps)) - 2.5 * vp)
            ps += DT * vp
            if ps < 0:
                ps = 0.0
                vp = -0.3 * vp if vp < -0.4 else 0.0
            if lp == loops - 1 and i % SUB == 0:
                out[i // SUB] = th, ps
    return out


def solve(fn, target, lo, hi, it=16):
    for _ in range(it):
        mid = (lo + hi) / 2
        if fn(mid) < target:
            lo = mid
        else:
            hi = mid
    return (lo + hi) / 2


LIFT_T = float(ARGS.get("lift", 0.16))
SWAY_T = float(ARGS.get("sway", 0.0055))
kick = solve(lambda k: simulate(k, 0.0)[:, 1].max(), LIFT_T, 0.0, 80.0)
lat = solve(lambda l_: np.abs(LP * np.sin(simulate(kick, l_)[:, 0])).max(), SWAY_T, 0.0, 40.0)
sim = simulate(kick, lat)
sim2 = simulate(kick, lat, loops=7)
print(f"pendant sim kick={kick:.2f} lat={lat:.2f} max lift={sim[:, 1].max():.3f} sway={np.abs(LP * np.sin(sim[:, 0])).max() * 1000:.1f}mm"
      f" loop drift={np.abs(sim - sim2).max():.5f}")

bw = float(np.exp(-((hinge.x / 0.14) ** 2 + ((hinge.z - 1.22) / 0.12) ** 2)))
fr = np.arange(T)
breath_f = 0.5 - 0.5 * np.cos(2 * math.pi * fr / BREATH)
SW_LOC = np.stack([LP * np.sin(sim[:, 0]), LP * (1 - np.cos(sim[:, 0])), 0.0035 * bw * breath_f], 1)
SW_ROT = np.stack([-sim[:, 1], np.zeros(T), 0.35 * sim[:, 0]], 1)


def bake(ob, path, arr):
    ob.animation_data_create()
    if ob.animation_data.action is None:
        ob.animation_data.action = bpy.data.actions.new(ob.name + "_act")
    act = ob.animation_data.action
    for i in range(arr.shape[1]):
        try:
            fc = act.fcurve_ensure_for_datablock(ob, path, index=i)
        except AttributeError:
            fc = act.fcurves.new(path, index=i)
        fc.keyframe_points.add(T)
        fc.keyframe_points.foreach_set("co", np.stack([fr, arr[:, i]], 1).astype(np.float32).ravel())
        fc.update()


bake(swing, "location", SW_LOC)
bake(swing, "rotation_euler", SW_ROT)


def swing_mat(f):
    return (piv_base.matrix_basis @ Matrix.Translation(Vector(SW_LOC[f])) @
            Euler(tuple(SW_ROT[f]), "XYZ").to_matrix().to_4x4())


# ---------------------------------------------------------------- cuban curb chain
LINK_L, LINK_W, LINK_R, LINK_H = 0.0098, 0.0071, 0.00118, 0.001
PITCH = 0.0062
RZ = 0.8 * LINK_R
OFF = LINK_H + RZ + 0.0003


def curb_link(name, twist):
    """Oval link twisted into a saddle (so neighbours lie flat and interlock), then ground flat
    top and bottom like a diamond-cut curb."""
    a, b = LINK_L / 2 - LINK_R, LINK_W / 2 - LINK_R
    S, M = 72, 16
    zc = 0.62 * (LINK_H + RZ)
    verts = []
    for i in range(S):
        t = 2 * math.pi * i / S
        c = Vector((a * math.cos(t), b * math.sin(t), twist * LINK_H * math.sin(2 * t)))
        nn = Vector((b * math.cos(t), a * math.sin(t), 0)).normalized()
        for k in range(M):
            ph = 2 * math.pi * k / M
            v = c + nn * LINK_R * math.cos(ph) + Vector((0, 0, RZ * math.sin(ph)))
            v.z = max(-zc, min(zc, v.z))
            verts.append(v[:])
    faces = [(i * M + k, ((i + 1) % S) * M + k, ((i + 1) % S) * M + (k + 1) % M, i * M + (k + 1) % M)
             for i in range(S) for k in range(M)]
    me_ = bpy.data.meshes.new(name)
    me_.from_pydata(verts, [], faces)
    try:
        me_.shade_smooth()
        me_.set_sharp_from_angle(angle=math.radians(38))
    except AttributeError:
        for p_ in me_.polygons:
            p_.use_smooth = True
    return me_


m_chain, _, _ = silver("silver_chain", 0.07)
LINK_ME = (curb_link("curb_a", 1), curb_link("curb_b", -1))
for me_ in LINK_ME:
    me_.materials.append(m_chain)

nc = [v for v in mesh_np(body.data) if abs(v[0]) < 0.03 and abs(v[2] - 1.43) < 0.006]
ncy = float(np.mean([v[1] for v in nc])) if nc else -0.02


def onsurf(p, dirn):
    h_ = surf(Vector(p) - Vector(dirn) * 0.3, dirn)
    return Vector(p) if h_ is None else h_[0] + h_[1] * OFF


def strand_rest(side):
    """Rest path (world at rest) from the jump ring up the chest and round the neck to behind it."""
    ring = hinge + frame_m @ ring_top_plate[side]
    pts = [ring]
    # a loose chain: a soft V up the chest, then it lies on the base of the neck / trapezius
    # (dropped from above on a ring wider than the neck), never pulled tight against the neck
    NR = float(ARGS.get("chain_r", 0.074))
    a0 = 62.0
    top0 = Vector((NR * math.sin(math.radians(a0)) * side, ncy - NR * math.cos(math.radians(a0)), 1.47))
    h0 = surf(top0, Vector((0, 0, -1)))
    neck_side = h0[0] if h0 else Vector((top0.x, top0.y, 1.38))
    for t in np.linspace(0.2, 0.8, 5):
        e_ = t ** 1.5
        pts.append(onsurf((ring.x + (neck_side.x - ring.x) * e_, 0, ring.z + (neck_side.z - ring.z) * t), Vector((0, 1, 0))))
    for ang in np.radians(np.linspace(a0, 140, 8)):
        c = Vector((NR * math.sin(ang) * side, ncy - NR * math.cos(ang), 1.47))
        h_ = surf(c, Vector((0, 0, -1)))
        if h_ and h_[1].z > 0.2:
            pts.append(h_[0] + h_[1] * OFF)
    return np.array([p[:] for p in pts])


def chaikin(P, n=4):
    for _ in range(n):
        Q = [P[0]]
        for a, b in zip(P[:-1], P[1:]):
            Q += [0.75 * a + 0.25 * b, 0.25 * a + 0.75 * b]
        Q.append(P[-1])
        P = np.array(Q)
    return P


def nearest_surface(p):
    best = None
    for t in (T_SHIRT, T_BODY):
        h_ = t.find_nearest(Vector(p))
        if h_[0] is not None and (best is None or h_[3] < best[3]):
            best = h_
    return best


chain_obs = []
for side in (-1, 1):
    rest = strand_rest(side)
    arc = np.concatenate([[0], np.cumsum(np.linalg.norm(np.diff(rest, axis=0), axis=1))])
    w_end = 1 - smooth(arc / 0.075)
    ring0 = Vector(rest[0])
    n_links = int(arc[-1] / PITCH) - 1
    LOC = np.zeros((n_links, T, 3))
    ROT = np.zeros((n_links, T, 4))
    # the ring's motion travels up the strand with a small delay, so the links ripple instead of moving rigidly
    RD = np.array([np.array(swing_mat(f) @ ring_top_plate[side] + CHEST - ring0) for f in range(T)])

    def rd_at(ff):
        ff %= T
        i0 = int(ff)
        return RD[i0] + (RD[(i0 + 1) % T] - RD[i0]) * (ff - i0)

    for f in range(T):
        P = rest + w_end[:, None] * np.array([rd_at(f - a_ * 70) for a_ in arc])
        P[:, 1] -= 0.0035 * breath_f[f] * np.exp(-((P[:, 0] / 0.14) ** 2 + ((P[:, 2] - 1.22) / 0.12) ** 2))
        D = chaikin(P)
        s_ = np.concatenate([[0], np.cumsum(np.linalg.norm(np.diff(D, axis=0), axis=1))])
        for i in range(n_links):
            s = (i + 0.5) * PITCH
            j = min(np.searchsorted(s_, s), len(D) - 1)
            j0 = max(j - 1, 0)
            u = (s - s_[j0]) / max(s_[j] - s_[j0], 1e-9)
            pos = Vector(D[j0] + (D[j] - D[j0]) * u)
            tg = Vector(D[min(j + 1, len(D) - 1)] - D[max(j0 - 1, 0)]).normalized()
            hit = nearest_surface(pos)
            nrm = hit[1] if hit else Vector((0, -1, 0))
            if hit and s > 0.012:
                gap = (pos - hit[0]).dot(nrm)
                if gap < OFF:
                    pos += nrm * (OFF - gap)
            if nrm.dot(pos - Vector((0, ncy, pos.z))) < 0:
                nrm = -nrm
            zt = (nrm - tg * nrm.dot(tg)).normalized()
            m3 = Matrix((tg, zt.cross(tg), zt)).transposed()
            q = m3.to_quaternion()
            if f and Vector(ROT[i, f - 1]).dot(Vector(q)) < 0:
                q.negate()
            LOC[i, f] = pos - CHEST
            ROT[i, f] = q[:]
    for i in range(n_links):
        ob = bpy.data.objects.new(f"curb_{side}_{i:02d}", LINK_ME[i % 2])
        sc.collection.objects.link(ob)
        ob.parent = rig
        ob.matrix_parent_inverse = Matrix.Identity(4)
        ob.rotation_mode = "QUATERNION"
        bake(ob, "location", LOC[i])
        bake(ob, "rotation_quaternion", ROT[i])
        chain_obs.append(ob)
print("chain links", len(chain_obs))

# ---------------------------------------------------------------- body hair
def body_hair():
    """Short, sparse hair on the upper chest (only where the neckline leaves skin) and the upper arms.
    Perfectly hairless skin was a big part of the plastic, toy-like read."""
    co = mesh_np(body.data)
    nrm_ = normals_np(body.data)
    z_ = co[:, 2]
    front_ = np.clip(-nrm_[:, 1] * 1.5, 0, 1)
    # chest hair off by default: with the higher scoop little skin shows and the denoiser smeared the few strands into pale drips
    chest = float(ARGS.get("chest_hair", 0)) * np.exp(-((co[:, 0] / 0.075) ** 2 + ((z_ - 1.25) / 0.055) ** 2)) * front_
    arms = 0.45 * W_ARM * smooth((1.33 - z_) / 0.08)
    w = np.clip(chest + arms, 0, 1) * (~inside)
    vgroup(body, "hair", w)
    body.modifiers.new("hair", "PARTICLE_SYSTEM")
    psys = body.particle_systems[-1]
    st = psys.settings
    st.type = "HAIR"
    st.count = int(ARGS.get("hair_n", 7000))
    st.hair_length = float(ARGS.get("hair_len", 0.008))
    st.emit_from = "FACE"
    st.use_advanced_hair = True
    st.normal_factor = 0.18
    st.object_align_factor = (0.0, 0.0, -0.006)      # lies down along the skin, like real body hair
    st.child_type = "NONE"   # children ran the iGPU out of memory
    st.roughness_1 = 0.003
    st.roughness_2 = 0.002
    st.roughness_endpoint = 0.002
    st.radius_scale = 0.000035
    st.root_radius = 1.0
    st.tip_radius = 0.2
    st.render_step = 4
    st.display_step = 2
    psys.vertex_group_density = "hair"
    psys.vertex_group_length = "hair"
    hm = bpy.data.materials.new("body_hair")
    hm.use_nodes = True
    nt = hm.node_tree
    out_ = next(n for n in nt.nodes if n.type == "OUTPUT_MATERIAL")
    for n in [n for n in nt.nodes if n.type != "OUTPUT_MATERIAL"]:
        nt.nodes.remove(n)
    hb = nt.nodes.new("ShaderNodeBsdfHairPrincipled")
    for nm_, v_ in (("Melanin", 0.88), ("Roughness", 0.35), ("Radial Roughness", 0.4), ("Random Color", 0.15)):
        if nm_ in hb.inputs:
            hb.inputs[nm_].default_value = v_
    nt.links.new(hb.outputs[0], out_.inputs["Surface"])
    body.data.materials.append(hm)
    st.material_slot = "body_hair"


# off: with deformation blur off on the body (needed for speed) Cycles smears the hair into long streaks off the arms
if float(ARGS.get("hair", 0)) > 0:
    body_hair()

# ---------------------------------------------------------------- camera
cam = bpy.data.objects.new("cam", bpy.data.cameras.new("cam"))
sc.collection.objects.link(cam)
sc.camera = cam
# framing is fixed on the chest (the old plate height), so moving the plate does not move the shot
look = Vector((0, plate_c.y, float(ARGS.get("look_z", 1.302))))
cam.location = (0, look.y - 1.78, look.z + 0.05)
cam.rotation_euler = (look - Vector(cam.location)).to_track_quat("-Z", "Y").to_euler()
cam.data.lens = float(ARGS.get("lens", 110))
cam.data.sensor_fit = "HORIZONTAL"
cam.data.sensor_width = 36
cam.data.dof.use_dof = True
cam.data.dof.focus_distance = (plate_c - Vector(cam.location)).length
cam.data.dof.aperture_fstop = float(ARGS.get("fstop", 9.0))
if ARGS.get("cam") == "close":
    cam.location = plate_c + N0 * 0.45 + Vector((0, 0, 0.02))
    cam.rotation_euler = (plate_c - Vector(cam.location)).to_track_quat("-Z", "Y").to_euler()
    cam.data.dof.focus_distance = 0.45
    cam.data.dof.aperture_fstop = 11
else:
    # handheld-steady drift, whole periods in the loop
    drv(cam, "location", 0, "0.0022*sin(2*pi*frame/210)")
    drv(cam, "location", 2, f"{cam.location.z}+0.0012*sin(2*pi*frame/105+0.7)")

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
# rims kept low: at 160 the cold left rim left a milky band inside the arm contour
area("rim_l", (0.12, 1.1), (-0.8, 0.55, 1.35), (-0.12, 0, 1.25), float(ARGS.get("rim_l", 60)), (1.0, 0.93, 0.86))
area("rim_r", (0.12, 1.1), (0.8, 0.55, 1.35), (0.12, 0, 1.25), float(ARGS.get("rim_r", 140)), (0.79, 0.045, 0.027))
area("fill", (1.0, 1.0), (0.9, -1.4, 0.9), (0, -0.1, 1.25), 8, (1, 0.97, 0.95))
# product softbox: sits where the plate faces mirror the camera, specular only, so the polished faces read bright
_d = Vector((0, 1, 0))
_r = (_d - 2 * _d.dot(N0) * N0).normalized()
metal = bpy.data.collections.new("metal")
for ob_ in sc.objects:
    if ob_.type == "MESH" and ob_.name.startswith(("plate", "jump_ring", "curb")):
        metal.objects.link(ob_)
for nm_, off_, en_ in () if float(ARGS.get("softbox", 0)) <= 0 else (("softbox", Vector((float(ARGS.get("sbx", 0.33)), 0, 0)), float(ARGS.get("softbox", 4))), ("softbox_strip", Vector((-0.22, 0, 0.1)), float(ARGS.get("softbox", 70)) * 0.5)):
    sb_ = area(nm_, (0.7, 0.45) if nm_ == "softbox" else (0.08, 0.6), plate_c + _r * 1.1 + off_, plate_c, en_)
    sb_.data.diffuse_factor = 0.0
    try:
        sb_.light_linking.receiver_collection = metal
    except AttributeError as e:
        print("no light linking", e)
    try:
        sb_.data.volume_factor = 0.0
    except AttributeError:
        pass

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
if ARGS.get("device", "hip") == "hip":
    # the Radeon iGPU renders Cycles through HIP (much faster than the shared CPU)
    cp = bpy.context.preferences.addons["cycles"].preferences
    try:
        cp.compute_device_type = "HIP"
        cp.refresh_devices()
        for d in cp.devices:
            d.use = d.type == "HIP"
        if any(d.use for d in cp.devices):
            cy.device = "GPU"
    except (TypeError, AttributeError) as e:
        print("no HIP", e)
print("cycles device", cy.device)
cy.samples = int(ARGS.get("samples", 128))
cy.use_adaptive_sampling = True
cy.adaptive_threshold = float(ARGS.get("noise", 0.02))
cy.use_denoising = True
for attr_, val_ in (("denoising_prefilter", "ACCURATE"), ("denoising_quality", "HIGH"), ("denoising_input_passes", "RGB_ALBEDO_NORMAL")):
    try:
        setattr(cy, attr_, val_)
    except (AttributeError, TypeError) as e:
        print("denoise opt", attr_, e)
try:
    cy.denoiser = "OPENIMAGEDENOISE"
except TypeError:
    pass
cy.max_bounces = 6
cy.diffuse_bounces = 2
cy.glossy_bounces = 4
cy.transmission_bounces = 2
cy.transparent_max_bounces = 8
cy.volume_bounces = 0
cy.caustics_reflective = False
cy.caustics_refractive = False
cy.blur_glossy = 0.5
sc.render.use_persistent_data = True
if ARGS.get("blur", "1") == "1":
    sc.render.use_motion_blur = True
    sc.render.motion_blur_shutter = 0.35
    # deformation blur on the subdivided body/shirt costs a full extra sync per frame on the iGPU and is
    # invisible at walking speed; the pendant and links (object motion) keep their blur
    if ARGS.get("deform_blur", "0") != "1":
        for ob_ in (body, shirt):
            for host_ in (ob_, getattr(ob_, "cycles", None)):
                if host_ is not None and hasattr(host_, "use_deform_motion"):
                    host_.use_deform_motion = False
sc.render.resolution_x = 2520
sc.render.resolution_y = 1080
sc.render.resolution_percentage = int(ARGS.get("res", 100))
if ARGS.get("crop") == "square":
    sc.render.use_border = True
    sc.render.use_crop_to_border = True
    sc.render.border_min_x, sc.render.border_max_x = 720 / 2520, 1800 / 2520
    sc.render.border_min_y, sc.render.border_max_y = 0.0, 1.0
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
vs.exposure = float(ARGS.get("exposure", -0.35))
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
    if ARGS.get("blur", "1") == "1":
        sc.render.use_motion_blur = True
        sc.render.motion_blur_shutter = 0.35
        try:
            ee.motion_blur_steps = 1
        except AttributeError:
            pass
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

for nm_ in ARGS.get("hide", "").split(","):
    if nm_ in bpy.data.objects:
        bpy.data.objects[nm_].hide_render = True

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
        t0_ = time.time()
        bpy.ops.render.render(write_still=True)
        print("RENDERED", fp, f"{time.time() - t0_:.0f}s", flush=True)
print("DONE")
