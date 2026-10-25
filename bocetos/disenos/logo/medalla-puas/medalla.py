"""Barullo medal ("la o") redesign — spiky chrome octogram, drawn in VectorCraft via MCP.
python3 medalla.py <variant A|B|C> <out.png> [--connect] [--save path.vectorcraft]"""
import math, sys
from vc import VC

S = 1080; C = S / 2
RED, RED_D, BLACK, BONE = "#E63B2E", "#7A120C", "#0B0B0B", "#F2EFE8"

def pol(r, a, cx=C, cy=C):
    a = math.radians(a - 90)  # 0deg = up
    return (cx + r * math.cos(a), cy + r * math.sin(a))

def d_of(pts):
    return "M" + " L".join(f"{x:.2f} {y:.2f}" for x, y in pts) + " Z"

def lin(stops, p0, p1):
    return {"gradient": {"kind": "linear", "stops": [{"offset": o, "color": c} for o, c in stops],
                         "start": [round(p0[0], 2), round(p0[1], 2)], "end": [round(p1[0], 2), round(p1[1], 2)]}}

def rad(stops, p0, p1, focal=None):
    g = {"kind": "radial", "stops": [{"offset": o, "color": c} for o, c in stops],
         "start": [round(p0[0], 2), round(p0[1], 2)], "end": [round(p1[0], 2), round(p1[1], 2)]}
    if focal: g["focal"] = [round(focal[0], 2), round(focal[1], 2)]
    return {"gradient": g}

LIGHT = [(0, "#FFFFFF"), (0.35, "#EEF0F4"), (1, "#6E7383")]
DARK = [(0, "#9EA3B0"), (0.4, "#3A3D47"), (1, "#0E0F13")]

def spike(ops, ang, r0, R, half, light_left=True, warm=False):
    """Faceted chrome cone: two triangles split along the axis, gradients run base->tip."""
    bl, br, mid, tip = pol(r0, ang - half), pol(r0, ang + half), pol(r0 - 6, ang), pol(R, ang)
    lit = (ang % 360) > 180  # light comes from upper-left
    left, right = (LIGHT, DARK) if lit else (DARK, LIGHT)
    if warm:  # bottom spikes catch the red floor glow
        right = [(0, "#FFD2C2"), (0.4, "#FF5A3C"), (1, "#3A0805")] if not lit else right
        left = [(0, "#FFD2C2"), (0.4, "#FF5A3C"), (1, "#3A0805")] if lit else left
    ax = pol((r0 + R) / 2 - (R - r0) * 0.25, ang)  # gradient runs from the ridge out to each edge
    ops.append(("draw_path", {"d": d_of([bl, tip, mid]), "fill": lin(left, ax, pol(r0 + 8, ang - half)), "stroke": "none"}))
    ops.append(("draw_path", {"d": d_of([mid, tip, br]), "fill": lin(right, ax, pol(r0 + 8, ang + half)), "stroke": "none"}))

def octogram(r_out, rot=0, cx=C, cy=C):
    ri = r_out * math.cos(math.radians(45)) / math.cos(math.radians(22.5))
    return [pol(r_out if i % 2 == 0 else ri, rot + i * 22.5, cx, cy) for i in range(16)]

def octagon(r, rot=22.5, cx=C, cy=C):
    return [pol(r, rot + i * 45, cx, cy) for i in range(8)]

def sparkle(ops, x, y, r, color="#FFFFFF"):
    k = r * 0.12
    pts = [(x, y - r), (x + k, y - k), (x + r, y), (x + k, y + k), (x, y + r), (x - k, y + k), (x - r, y), (x - k, y - k)]
    ops.append(("draw_path", {"d": d_of(pts), "fill": color, "stroke": "none"}))

def chrome_ball(ops, r):
    box = {"shape": "ellipse", "x": C - r, "y": C - r, "width": 2 * r, "height": 2 * r, "stroke": "none"}
    ops.append(("draw_shape", dict(box, fill=lin([(0, "#F4F6FA"), (0.3, "#C9CDD6"), (0.47, "#8D92A0"), (0.5, "#1C1D23"), (0.62, "#3C3F49"),
                                                  (0.8, "#6B2019"), (0.92, RED), (1, "#FF9C73")], (C, C - r), (C, C + r)))))
    g = {"gradient": {"kind": "radial", "start": [C, C], "end": [C + r, C], "stops": [
        {"offset": 0, "color": "#000000", "opacity": 0}, {"offset": 0.7, "color": "#000000", "opacity": 0.05},
        {"offset": 0.93, "color": "#000000", "opacity": 0.55}, {"offset": 1, "color": "#000000", "opacity": 0.8}]}}
    ops.append(("draw_shape", dict(box, fill=g)))
    hx, hy = C - r * 0.42, C - r * 0.5
    ops.append(("draw_shape", {"shape": "ellipse", "x": hx - r * 0.22, "y": hy - r * 0.13, "width": r * 0.44, "height": r * 0.26, "stroke": "none",
                               "fill": {"gradient": {"kind": "radial", "start": [hx, hy], "end": [hx + r * 0.22, hy], "stops": [
                                   {"offset": 0, "color": "#FFFFFF", "opacity": 1}, {"offset": 1, "color": "#FFFFFF", "opacity": 0}]}}}))

def embossed_star(ops, r, cx=C, cy=C):
    ops.append(("draw_path", {"d": d_of(octogram(r * 1.12, 0, cx, cy)), "fill": "#121318", "stroke": "none"}))
    ops.append(("draw_path", {"d": d_of(octogram(r * 1.04, 0, cx, cy)), "stroke": "none",
                              "fill": lin([(0, "#FFFFFF"), (0.5, "#9AA0AE"), (1, "#20222A")], pol(r, -45, cx, cy), pol(r, 135, cx, cy))}))
    ops.append(("draw_path", {"d": d_of(octogram(r * 0.93, 0, cx, cy)), "stroke": "none",
                              "fill": lin([(0, "#FF6B55"), (0.55, RED), (1, RED_D)], pol(r, -40, cx, cy), pol(r, 140, cx, cy))}))
    # hollow centre (the original medal's octagon), chrome rim + black well + stud
    ops.append(("draw_path", {"d": d_of(octagon(r * 0.42, 22.5, cx, cy)), "stroke": "none",
                              "fill": lin([(0, "#2A0705"), (1, "#FFC0A8")], pol(r * 0.42, -45, cx, cy), pol(r * 0.42, 135, cx, cy))}))
    ops.append(("draw_path", {"d": d_of(octagon(r * 0.34, 22.5, cx, cy)), "fill": BLACK, "stroke": "none"}))
    stud(ops, cx, cy, r * 0.17)

def stud(ops, x, y, r):
    """Small chrome cone seen from the front (8 facets)."""
    for i in range(8):
        a0, a1 = i * 45, i * 45 + 45
        p0, p1 = pol(r, a0, x, y), pol(r, a1, x, y)
        lum = (math.cos(math.radians((a0 + 22.5) - 315)) + 1) / 2
        g = int(30 + lum * 225)
        col = f"#{g:02X}{g:02X}{min(255, g + 8):02X}"
        ops.append(("draw_path", {"d": d_of([(x, y), p0, p1]), "fill": col, "stroke": "none"}))

def horn(ops, side):
    """Ribbed curved horn: tapering segments along a curve, each split light/dark."""
    n = 9
    pts = []
    for i in range(n + 1):
        t = i / n
        a = side * (30 + 4 * t - 14 * t * t)          # sweeps out then hooks back in
        r = 255 + 210 * t
        w = 46 * (1 - t) ** 0.8 + 2
        pts.append((pol(r, a), w, a))
    for i in range(n):
        (p0, w0, a0), (p1, w1, a1) = pts[i], pts[i + 1]
        nx0 = (math.cos(math.radians(a0)), math.sin(math.radians(a0)))
        nx1 = (math.cos(math.radians(a1)), math.sin(math.radians(a1)))
        l0, r0 = (p0[0] - nx0[0] * w0, p0[1] - nx0[1] * w0), (p0[0] + nx0[0] * w0, p0[1] + nx0[1] * w0)
        l1, r1 = (p1[0] - nx1[0] * w1, p1[1] - nx1[1] * w1), (p1[0] + nx1[0] * w1, p1[1] + nx1[1] * w1)
        bulge = 1.12  # each rib swells a little in the middle
        m0, m1 = p0, p1
        ops.append(("draw_path", {"d": d_of([l0, m0, m1, l1]), "stroke": "none", "fill": lin(LIGHT, m0, (l0[0] * bulge - m0[0] * (bulge - 1), l0[1] * bulge - m0[1] * (bulge - 1)))}))
        ops.append(("draw_path", {"d": d_of([m0, r0, r1, m1]), "stroke": "none", "fill": lin(DARK, m0, r0)}))
        ops.append(("draw_path", {"d": d_of([l0, r0, (r0[0] + (r1[0] - r0[0]) * 0.12, r0[1] + (r1[1] - r0[1]) * 0.12), (l0[0] + (l1[0] - l0[0]) * 0.12, l0[1] + (l1[1] - l0[1]) * 0.12)]),
                                  "fill": "#14151A", "stroke": "none"}))

def grin(ops):
    """Wide smile between two arcs, fangs along both."""
    n = 11
    top = [(C + x, C + 15 + 0.0012 * (220 * 220 - x * x) * 0.12 - 5) for x in [-220 + i * 440 / n for i in range(n + 1)]]
    bot = [(C + x, C + 15 + 0.0012 * (220 * 220 - x * x) * 2.5) for x in [-220 + i * 440 / n for i in range(n + 1)]]
    ops.append(("draw_path", {"d": d_of(top + bot[::-1]), "fill": "#07070A", "stroke": "none"}))
    tooth = lambda a, b, tip: ("draw_path", {"d": d_of([a, b, tip]), "stroke": "none",
                                             "fill": lin([(0, "#FFFFFF"), (0.6, "#C3C7D0"), (1, "#5F6472")], ((a[0] + b[0]) / 2, (a[1] + b[1]) / 2), tip)})
    for i in range(n):
        a, b = top[i], top[i + 1]
        depth = 0.55 * (bot[i][1] - top[i][1] + bot[i + 1][1] - top[i + 1][1]) / 2
        ops.append(tooth(a, b, ((a[0] + b[0]) / 2, (a[1] + b[1]) / 2 + depth)))
    for i in range(1, n - 1):
        a, b = bot[i], bot[i + 1]
        depth = 0.4 * (bot[i][1] - top[i][1])
        ops.append(tooth(a, b, ((a[0] + b[0]) / 2, (a[1] + b[1]) / 2 - depth)))
    ops.append(("draw_path", {"d": "M" + " L".join(f"{x:.1f} {y:.1f}" for x, y in top), "fill": "none", "stroke": "#E8EAF0", "strokeWidth": 5}))

def build_flat(variant, ink=RED, bg=BLACK):
    ops = [("run_command", {"command": "artboard.setProps", "params": {"index": 0, "name": f"medalla_{variant}_plana", "x": 0, "y": 0, "width": S, "height": S}}),
           ("draw_shape", {"shape": "rectangle", "x": 0, "y": 0, "width": S, "height": S, "fill": bg, "stroke": "none"})]
    P = lambda pts, f: ops.append(("draw_path", {"d": d_of(pts), "fill": f, "stroke": "none"}))
    sp = lambda a, r0, R, h: P([pol(r0, a - h), pol(R, a), pol(r0, a + h)], ink)
    if variant == "A":
        for i in range(16): sp(i * 22.5 + 11.25, 230, 400, 6.5)
        for i in range(8): sp(i * 45 + 22.5, 230, 455, 9)
        for i in range(8): sp(i * 45, 200, 515, 13)
        P(octogram(285 * 1.12), bg); P(octogram(285 * 1.0), ink); P(octogram(285 * 0.9), bg); P(octogram(285 * 0.82), ink)
        P(octagon(285 * 0.38), bg); P(octagon(285 * 0.2), ink)
    else:
        for i in range(16): sp(i * 22.5 + 11.25, 260, 505 if i % 2 == 0 else 420, 9 if i % 2 == 0 else 7)
        ops.append(("draw_shape", {"shape": "ellipse", "x": C - 300, "y": C - 300, "width": 600, "height": 600, "fill": ink, "stroke": "none"}))
        P(octogram(205 * 1.12), bg); P(octogram(205 * 0.96), ink); P(octagon(205 * 0.42), bg); P(octagon(205 * 0.22), ink)
        for i in range(8):
            x, y = pol(262, i * 45 + 22.5); P(octagon(14, 22.5, x, y), bg)
    return ops

def build(variant):
    ops = [("run_command", {"command": "artboard.setProps", "params": {"index": 0, "name": f"medalla_{variant}", "x": 0, "y": 0, "width": S, "height": S}})]
    ops.append(("draw_shape", {"shape": "rectangle", "x": 0, "y": 0, "width": S, "height": S, "fill": BLACK, "stroke": "none"}))
    # red floor glow behind the object
    ops.append(("draw_shape", {"shape": "ellipse", "x": C - 470, "y": C - 300, "width": 940, "height": 900, "stroke": "none",
                               "fill": rad([(0, "#5A0E09"), (0.55, "#250504"), (1, BLACK)], (C, C + 160), (C + 470, C + 160))}))
    if variant == "A":
        # The octogram IS the object: its 8 tips stretch into long spikes, 8 short ones in between.
        for i in range(16):
            a = i * 22.5 + 11.25
            spike(ops, a, 230, 400, 6.5, warm=(95 < a < 265))
        for i in range(8):
            a = i * 45 + 22.5
            spike(ops, a, 230, 455, 9, warm=(95 < a < 265))
        for i in range(8):
            spike(ops, i * 45, 200, 515, 13, warm=(95 < i * 45 < 265))
        embossed_star(ops, 285)
    else:
        n_long = 16
        for i in range(n_long):
            a = i * 360 / n_long + 11.25
            spike(ops, a, 260, 505 if i % 2 == 0 else 420, 9 if i % 2 == 0 else 7, warm=(100 < a < 260))
        chrome_ball(ops, 300)
        if variant == "B":
            embossed_star(ops, 205)
            for i in range(8):
                x, y = pol(262, i * 45 + 22.5)
                stud(ops, x, y, 16)
        else:  # C: horned grin — the octogram becomes the mouth/face plate
            for side in (-1, 1):
                horn(ops, side)
            for side in (-1, 1):  # angry eyes: chrome rim + red lozenge
                ex = C + side * 100
                eye = [(ex - side * 85, C - 105), (ex + side * 60, C - 60), (ex + side * 10, C - 15), (ex - side * 55, C - 45)]
                inner = [(ex - side * 62, C - 92), (ex + side * 42, C - 60), (ex + side * 8, C - 30), (ex - side * 42, C - 52)]
                ops.append(("draw_path", {"d": d_of(eye), "stroke": "none", "fill": lin(LIGHT, (ex, C - 105), (ex, C - 15))}))
                ops.append(("draw_path", {"d": d_of(inner), "fill": RED, "stroke": "none"}))
            grin(ops)
            embossed_star(ops, 52, C, C - 190)  # third eye: the Barullo medal on the forehead
    # specular highlight + sparkles
    sparkle(ops, C - 330, C - 300, 46); sparkle(ops, C + 360, C - 220, 30); sparkle(ops, C + 300, C + 370, 38); sparkle(ops, C - 390, C + 250, 22)
    return ops

if __name__ == "__main__":
    variant, out = sys.argv[1], sys.argv[2]
    v = VC(connect="--connect" in sys.argv)
    if "--connect" in sys.argv:
        v.call("run_command", command="file.new", params={"width": S, "height": S})
    for tool, args in (build_flat(variant[0]) if variant.endswith('flat') else build(variant)):
        v.call(tool, **args)
    v.png("render_preview", out, max_side=1080)
    if "--save" in sys.argv:  # base path without extension (Windows-style, the CLI is a Windows exe)
        p = sys.argv[sys.argv.index("--save") + 1]
        v.call("export", path=p + ".vectorcraft", format="vectorcraft")
        v.call("export", path=p + ".svg", format="svg")
        v.call("export", path=p + ".png", format="png", scale=2)
    v.close()
