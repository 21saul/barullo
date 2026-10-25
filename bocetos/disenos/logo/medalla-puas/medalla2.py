"""Barullo medal v2 — "la o" redrawn as one fluid emblem: the 8-point star of the original medal,
its two upper tips curling into horns, a chrome face plate with a grin, spikes behind.
Everything is bezier paths + a few smooth gradients (no faceted pieces).

python3 medalla2.py <solo|solo_flat|lockup|lockup_red> <preview.png> [--connect] [--save C:/base/path/without/ext]
"""
import math, re, sys
from vc import VC

RED, RED_HI, RED_LO, BLACK, BONE, INK = "#E63B2E", "#FF6A4F", "#8E140C", "#0B0B0B", "#F2EFE8", "#0B0B0B"
C = 540.0  # medal geometry is authored in a 1080 box centred on (C, C)

# --- transform: medal space -> document space -------------------------------------------
T = {"cx": C, "cy": C, "k": 1.0}
def X(p):
    return (T["cx"] + (p[0] - C) * T["k"], T["cy"] + (p[1] - C) * T["k"])
def W(w):
    return w * T["k"]

def pol(r, a):
    a = math.radians(a - 90)  # 0deg = up, clockwise
    return (C + r * math.cos(a), C + r * math.sin(a))

def lerp(a, b, t):
    return (a[0] + (b[0] - a[0]) * t, a[1] + (b[1] - a[1]) * t)

def f(p):
    q = X(p); return f"{q[0]:.2f} {q[1]:.2f}"

class Path:
    """Tiny SVG path builder in medal space."""
    def __init__(self, p): self.s = [f"M{f(p)}"]; self.cur = p
    def L(self, p): self.s.append(f"L{f(p)}"); self.cur = p; return self
    def C(self, c1, c2, p): self.s.append(f"C{f(c1)} {f(c2)} {f(p)}"); self.cur = p; return self
    def Z(self): self.s.append("Z"); return self
    def d(self): return " ".join(self.s)

def grad(kind, stops, p0, p1):
    a, b = X(p0), X(p1)
    st = []
    for s in stops:
        o, c = s[0], s[1]
        e = {"offset": o, "color": c}
        if len(s) > 2: e["opacity"] = s[2]
        st.append(e)
    return {"gradient": {"kind": kind, "stops": st, "start": [round(a[0], 2), round(a[1], 2)], "end": [round(b[0], 2), round(b[1], 2)]}}

def path(ops, d, fill, stroke="none", sw=0):
    a = {"d": d, "fill": fill, "stroke": stroke}
    if stroke != "none": a["strokeWidth"] = W(sw)
    ops.append(("draw_path", a))

def bez(p0, c1, c2, p1, t):
    u = 1 - t
    return (u**3 * p0[0] + 3 * u * u * t * c1[0] + 3 * u * t * t * c2[0] + t**3 * p1[0],
            u**3 * p0[1] + 3 * u * u * t * c1[1] + 3 * u * t * t * c2[1] + t**3 * p1[1])

# --- geometry ------------------------------------------------------------------------------
R = 430.0                                              # star tip radius
RI = R * math.cos(math.radians(45)) / math.cos(math.radians(22.5))  # concave radius of two squares at 45deg

def horn_curves(side, s=1.0):
    """Outer and inner bezier of a horn growing from the star's upper-diagonal tip (side=-1 left, +1 right).
    Outer runs base->tip, inner runs tip->base. s<1 is the bevel inset: same tip, bases pulled in."""
    mx = (lambda p: p) if side == 1 else (lambda p: (2 * C - p[0], p[1]))
    b_out = pol(RI * s, 67.5); b_in = pol(RI * s, 22.5)
    tip = (858, 52)
    outer = (b_out, (b_out[0] + 125 * s, b_out[1] - 80), (948, 160), tip)
    inner = (tip, (842, 150), (b_in[0] + 110 * s, b_in[1] - 10), b_in)
    if s < 1:  # pull the inset curves inwards so the bevel is an even band
        outer = (outer[0], lerp(outer[1], (C, C), 1 - s), lerp(outer[2], (C, C), (1 - s) * 0.9), lerp(tip, (C, C), (1 - s) * 0.02))
        inner = (outer[3], lerp(inner[1], (C, C), (1 - s) * 0.6), lerp(inner[2], (C, C), 1 - s), inner[3])
    return tuple(mx(p) for p in outer), tuple(mx(p) for p in inner)

def silhouette(s=1.0, pinch=0.0):
    """Star outline (curved, slightly pinched edges so the tips read as spikes) with horns at +-45deg."""
    pts = []
    for i in range(16):
        a = i * 22.5
        pts.append((a, pol((R if i % 2 == 0 else RI) * s, a)))
    p = None
    # start at concave vertex 22.5 (right horn inner base) and walk clockwise
    order = [(i + 1) % 16 for i in range(16)]  # start at index 1 (22.5deg)
    start = pts[1][1]
    p = Path(start)
    i = 1
    while True:
        j = (i + 1) % 16
        a_j, pj = pts[j]
        if a_j in (45.0, 315.0):  # horn tip replaces this star tip
            side = 1 if a_j == 45.0 else -1
            outer, inner = horn_curves(side, s)
            if side == 1:   # walking clockwise: inner base (22.5) -> tip -> outer base (67.5)
                p.C(inner[2], inner[1], inner[0]).C(outer[2], outer[1], outer[0])
            else:           # left horn: outer base (292.5) -> tip -> inner base (337.5)
                p.C(outer[1], outer[2], outer[3]).C(inner[1], inner[2], inner[3])
            i = (j + 1) % 16
        else:
            pi = p.cur
            # pinch: pull both control points towards the centre a little
            c1 = lerp(lerp(pi, pj, 0.33), (C, C), pinch)
            c2 = lerp(lerp(pi, pj, 0.66), (C, C), pinch)
            p.C(c1, c2, pj)
            i = j
        if i == 1:
            break
    return p.Z().d()

def spike(ops, ang, r0, r1, half, warm=False):
    """One curved chrome spike: concave sides, gradient across its width so the ridge reads as a crisp edge."""
    bl, br, tip = pol(r0, ang - half), pol(r0, ang + half), pol(r1, ang)
    axis_mid = pol(r0 + (r1 - r0) * 0.45, ang)
    p = Path(bl).C(lerp(bl, axis_mid, 0.55), lerp(tip, axis_mid, 0.25), tip) \
               .C(lerp(tip, axis_mid, 0.25), lerp(br, axis_mid, 0.55), br).Z()
    dark = [(0.5, "#5A1410"), (0.56, "#B8261B"), (1, "#2A0705")] if warm else [(0.5, "#5B5F6C"), (0.56, "#3A3D47"), (1, "#0E0F13")]
    light = [(0, "#C9CDD6"), (0.3, "#FFFFFF"), (0.49, "#E9ECF1")]
    lit_left = math.sin(math.radians(ang)) > 0  # light from upper left
    stops = light + dark if lit_left else [(1 - o, c) for o, c in reversed(light + dark)]
    path(ops, p.d(), grad("linear", stops, pol(r0 + 60, ang - half), pol(r0 + 60, ang + half)), INK, 6)

def sparkle(ops, x, y, r):
    k = r * 0.16
    p = Path((x, y - r))
    for a, b in (((x + k, y - k), (x + r, y)), ((x + k, y + k), (x, y + r)), ((x - k, y + k), (x - r, y)), ((x - k, y - k), (x, y - r))):
        p.C(lerp(p.cur, a, 0.8), lerp(b, a, 0.8), b)
    path(ops, p.Z().d(), BONE)

# --- the medal -----------------------------------------------------------------------------
def medal(ops, flat=False, glow=True):
    # glow underneath
    if not flat and glow:
        ops.append(("draw_shape", {"shape": "ellipse", "x": X((C - 470, 0))[0], "y": X((0, C - 330))[1], "width": W(940), "height": W(900), "stroke": "none",
                                   "fill": {"gradient": {"kind": "radial", "start": list(X((C, C + 170))), "end": list(X((C + 470, C + 170))), "stops": [
                                       {"offset": 0, "color": "#B3200F", "opacity": 0.55}, {"offset": 0.5, "color": "#5A0E09", "opacity": 0.35}, {"offset": 1, "color": BLACK, "opacity": 0}]}}}))
    # spikes behind the star, poking out of the lower notches (top ones would fight the horns)
    spikes = [(a, RI * 0.8, R * 1.16, 12) for a in (112.5, 157.5, 202.5, 247.5)] + \
             [(a, R * 0.8, R * 1.3, 8.5) for a in (0, 90, 135, 180, 225, 270)]
    for a, r0, r1, h in spikes:
        if flat:
            bl, br, tip = pol(r0, a - h), pol(r0, a + h), pol(r1, a)
            m = pol(r0 + (r1 - r0) * 0.45, a)
            path(ops, Path(bl).C(lerp(bl, m, .55), lerp(tip, m, .25), tip).C(lerp(tip, m, .25), lerp(br, m, .55), br).Z().d(), RED)
        else:
            spike(ops, a, r0, r1, h, warm=(100 < a < 260))
    for a in (90 + 0, 270):  # side accents between the horizontal tips' neighbours
        pass

    # star body: rim (light top-left -> dark bottom-right), inset face with the opposite ramp = bevel
    outer = silhouette(1.0)
    if flat:
        path(ops, outer, RED)
    else:
        path(ops, outer, grad("linear", [(0, "#FF8A70"), (0.35, RED), (0.75, RED_LO), (1, "#3A0805")], (C - 300, C - 380), (C + 300, C + 380)), INK, 10)
        path(ops, silhouette(0.88), grad("radial", [(0, "#FF5A42"), (0.55, RED), (1, "#B3200F")], (C - 120, C - 160), (C + 420, C + 420)))
        # gloss: soft white veil over the upper-left half of the star
        path(ops, silhouette(0.88), grad("linear", [(0, "#FFFFFF", 0.45), (0.35, "#FFFFFF", 0.0), (1, "#FFFFFF", 0)], (C - 260, C - 330), (C + 60, C + 60)))
        # crisp specular streak on each horn
        for side in (-1, 1):
            o, inn = horn_curves(side, 0.93)
            p0, p1 = bez(*o, 0.25), bez(*o, 0.8)
            q0, q1 = bez(*inn, 0.25), bez(*inn, 0.72)
            m0, m1 = lerp(p0, q1, 0.3), lerp(p1, q0, 0.3)
            st = Path(m0).C(lerp(m0, m1, 0.3), lerp(m0, m1, 0.7), m1).C(lerp(m1, m0, 0.4), lerp(m1, m0, 0.8), lerp(m0, m1, 0.0))
            path(ops, Path(m0).C(lerp(m0, p1, .5), lerp(m1, p1, .2), m1).C(lerp(m1, q0, .3), lerp(m0, q0, .4), m0).Z().d(),
                 grad("linear", [(0, "#FFFFFF", 0.0), (0.5, "#FFFFFF", 0.85), (1, "#FFFFFF", 0.0)], m0, m1))
        # ribs on the horns: thin dark crescents following the horn's curvature
        for side in (-1, 1):
            o, inn = horn_curves(side, 1.0)
            for t in (0.22, 0.36, 0.5):
                a1, b1 = bez(*o, 1 - t), bez(*inn, t)
                a2, b2 = bez(*o, 1 - t - 0.045), bez(*inn, t + 0.045)
                a1, b1 = lerp(a1, b1, 0.07), lerp(b1, a1, 0.07)
                a2, b2 = lerp(a2, b2, 0.07), lerp(b2, a2, 0.07)
                bulge = lerp(lerp(a1, b1, 0.5), pol(R * 2, side * 30), 0.04)
                bulge2 = lerp(lerp(a2, b2, 0.5), pol(R * 2, side * 30), 0.06)
                path(ops, Path(a1).C(lerp(a1, bulge, .9), lerp(b1, bulge, .9), b1).L(b2).C(lerp(b2, bulge2, .9), lerp(a2, bulge2, .9), a2).Z().d(),
                     "#7E120B")

    # face plate: chrome disc in a dark ring (this is the "o" of the original medal)
    rd = 222
    ring = {"shape": "ellipse", "x": X((C - rd - 22, 0))[0], "y": X((0, C - rd - 22))[1], "width": W(2 * rd + 44), "height": W(2 * rd + 44), "stroke": "none"}
    disc = {"shape": "ellipse", "x": X((C - rd, 0))[0], "y": X((0, C - rd))[1], "width": W(2 * rd), "height": W(2 * rd)}
    if flat:
        ops.append(("draw_shape", dict(ring, fill=BLACK)))
        ops.append(("draw_shape", dict(disc, fill=BONE, stroke="none")))
    else:
        ops.append(("draw_shape", dict(ring, fill=grad("linear", [(0, "#2A0705"), (0.5, "#0B0B0B"), (1, "#FF9C80")], (C - 200, C - 200), (C + 200, C + 220)))))
        ops.append(("draw_shape", dict(disc, stroke=INK, strokeWidth=W(6), fill=grad("linear", [
            (0, "#FFFFFF"), (0.2, "#E9ECF1"), (0.45, "#9196A3"), (0.5, "#30323B"), (0.6, "#4D515D"), (0.78, "#6B1D16"), (0.9, RED), (1, "#FF9A78")],
            (C, C - rd), (C, C + rd)))))
        # wavy reflection band: makes the horizon flow instead of a ruler-straight line
        y0 = C + 6
        wave = Path((C - rd + 4, y0 + 10)).C((C - 120, y0 - 40), (C + 60, y0 + 46), (C + rd - 4, y0 - 4)) \
            .C((C + rd - 30, y0 + 70), (C + 120, y0 + 60), (C, y0 + 52)).C((C - 120, y0 + 46), (C - rd + 30, y0 + 70), (C - rd + 4, y0 + 10)).Z()
        path(ops, wave.d(), grad("linear", [(0, "#FFFFFF", 0.0), (0.5, "#C9CDD6", 0.35), (1, "#FFFFFF", 0.0)], (C - rd, y0), (C + rd, y0)))
        # rim falloff + hotspot
        ops.append(("draw_shape", dict(disc, stroke="none", fill={"gradient": {"kind": "radial", "start": list(X((C, C))), "end": list(X((C + rd, C))), "stops": [
            {"offset": 0, "color": "#000000", "opacity": 0}, {"offset": 0.75, "color": "#000000", "opacity": 0.04}, {"offset": 1, "color": "#000000", "opacity": 0.6}]}})))
        hx, hy = C - 120, C - 150
        hl = Path((hx - 70, hy + 30)).C((hx - 60, hy - 30), (hx + 30, hy - 60), (hx + 90, hy - 50)).C((hx + 20, hy - 30), (hx - 30, hy), (hx - 70, hy + 30)).Z()
        path(ops, hl.d(), grad("linear", [(0, "#FFFFFF", 0.95), (1, "#FFFFFF", 0.1)], (hx - 70, hy + 30), (hx + 90, hy - 50)))

    face(ops, flat)

def face(ops, flat):
    # angry eyes: the brow line is the eye's top edge, sloping down to the nose
    for s in (-1, 1):
        inner, outer = (C + s * 26, C - 46), (C + s * 172, C - 112)
        eye = Path(inner).C((C + s * 70, C - 72), (C + s * 130, C - 98), outer) \
            .C((C + s * 178, C - 40), (C + s * 96, C - 6), inner).Z()
        path(ops, eye.d(), BLACK if not flat else RED, INK, 6)
        if not flat:
            iris = Path((C + s * 62, C - 52)).C((C + s * 90, C - 70), (C + s * 130, C - 84), (C + s * 148, C - 84)) \
                .C((C + s * 146, C - 44), (C + s * 96, C - 26), (C + s * 62, C - 52)).Z()
            path(ops, iris.d(), grad("radial", [(0, "#FFB199"), (0.4, RED), (1, "#5A0E09")], (C + s * 112, C - 58), (C + s * 175, C - 58)))
            ops.append(("draw_shape", {"shape": "ellipse", "x": X((C + s * 118 - 9, 0))[0], "y": X((0, C - 74))[1], "width": W(18), "height": W(14), "fill": "#FFFFFF", "stroke": "none"}))

    # grin: crescent between two curves, corners flicked up
    Lc, Rc = (C - 200, C + 18), (C + 200, C + 18)
    top = (Lc, (C - 110, C + 78), (C + 110, C + 78), Rc)
    bot = (Rc, (C + 150, C + 230), (C - 150, C + 230), Lc)
    mouth = Path(Lc).C(top[1], top[2], Rc).C(bot[1], bot[2], Lc).Z()
    path(ops, mouth.d(), "#120406" if not flat else BLACK, INK, 8)
    tooth_fill = BONE if flat else grad("linear", [(0, "#FFFFFF"), (0.7, "#E4E6EC"), (1, "#9BA0AD")], (C, C + 40), (C, C + 150))

    def row(curve, n, depth, up, t0, t1):
        """One continuous zig-zag of fangs hanging off `curve`; sides are curved like real fangs."""
        pts = [bez(*curve, t0 + (t1 - t0) * i / n) for i in range(n + 1)]
        p = Path(pts[0])
        for i in range(n):
            a, b = pts[i], pts[i + 1]
            mid = lerp(a, b, 0.5)
            prof = math.sin(math.pi * (i + 0.5) / n) ** 0.6  # long in the middle, short at the corners
            tip = (mid[0], mid[1] + (-1 if up else 1) * depth * prof)
            p.C(lerp(a, tip, 0.5), (tip[0] - (b[0] - a[0]) * 0.12, tip[1] - (-1 if up else 1) * 8), tip) \
             .C((tip[0] + (b[0] - a[0]) * 0.12, tip[1] - (-1 if up else 1) * 8), lerp(b, tip, 0.5), b)
        # close along the lip, slightly outside so no gap shows
        back = [bez(*curve, t0 + (t1 - t0) * i / 6) for i in range(6, -1, -1)]
        for q in back:
            p.L((q[0], q[1] + (6 if up else -6)))
        return p.Z().d()

    path(ops, row(top, 10, 92, False, 0.06, 0.94), tooth_fill, INK, 4)
    bot_fw = (Lc, bot[2], bot[1], Rc)
    path(ops, row(bot_fw, 7, 62, True, 0.2, 0.8), tooth_fill, INK, 4)

# --- lettering -----------------------------------------------------------------------------
def lettering_paths():
    svg = open("/home/ddev/www/barullo/bocetos/disenos/logo/medalla-puas/lettering_trace.svg").read()
    return re.findall(r'<path d="([^"]+)"', svg)

def build(kind):
    ops = []
    if kind.startswith("solo"):
        S = 1080
        ops.append(("run_command", {"command": "artboard.setProps", "params": {"index": 0, "name": "medalla_diablillo", "x": 0, "y": 0, "width": S, "height": S}}))
        ops.append(("draw_shape", {"shape": "rectangle", "x": 0, "y": 0, "width": S, "height": S, "fill": BLACK, "stroke": "none"}))
        T.update(cx=540, cy=556, k=0.86)
        medal(ops, flat=kind.endswith("flat"))
        if not kind.endswith("flat"):
            T.update(cx=C, cy=C, k=1)
            sparkle(ops, 160, 230, 38); sparkle(ops, 930, 300, 26); sparkle(ops, 880, 900, 34); sparkle(ops, 170, 860, 20)
    else:
        Wd, Hd = 4760, 1864
        bg = RED if kind == "lockup_red" else BLACK
        ops.append(("run_command", {"command": "artboard.setProps", "params": {"index": 0, "name": "barullo_lockup", "x": 0, "y": 0, "width": Wd, "height": Hd}}))
        ops.append(("draw_shape", {"shape": "rectangle", "x": 0, "y": 0, "width": Wd, "height": Hd, "fill": bg, "stroke": "none"}))
        for d in lettering_paths():
            ops.append(("draw_path", {"d": d, "fill": BONE, "stroke": "none"}))
        T.update(cx=4010, cy=930, k=1.12)
        medal(ops, glow=(bg == BLACK))
    return ops

if __name__ == "__main__":
    kind, out = sys.argv[1], sys.argv[2]
    v = VC(connect="--connect" in sys.argv)
    if "--connect" in sys.argv:
        v.call("run_command", command="file.new", params={})
    for tool, args in build(kind):
        v.call(tool, **args)
    v.png("render_preview", out, max_side=1600)
    if "--save" in sys.argv:
        p = sys.argv[sys.argv.index("--save") + 1]
        v.call("export", path=p + ".vectorcraft", format="vectorcraft")
        v.call("export", path=p + ".svg", format="svg")
        v.call("export", path=p + ".png", format="png", scale=2 if kind.startswith("solo") else 1)
    v.close()
