"""Flatten traced lettering, de-jag with RDP, emit polygon subpaths as JSON [[ [x,y],... ], ...]."""
import re, json, math, sys
svg = open("lettering_trace.svg").read()
ds = re.findall(r'<path d="([^"]+)"', svg)

def rdp(pts, eps):
    if len(pts) < 3: return pts
    (x1, y1), (x2, y2) = pts[0], pts[-1]
    L = math.hypot(x2 - x1, y2 - y1) or 1e-9
    dmax, idx = 0, 0
    for i in range(1, len(pts) - 1):
        x0, y0 = pts[i]
        d = abs((y2 - y1) * x0 - (x2 - x1) * y0 + x2 * y1 - y2 * x1) / L
        if d > dmax: dmax, idx = d, i
    if dmax > eps: return rdp(pts[:idx + 1], eps)[:-1] + rdp(pts[idx:], eps)
    return [pts[0], pts[-1]]

subs = []
for d in ds:
    toks = re.findall(r"[MLCZ]|-?[\d.]+", d)
    i, cur, pts = 0, None, []
    while i < len(toks):
        t = toks[i]
        if t == "M":
            if pts: subs.append(pts)
            cur = (float(toks[i + 1]), float(toks[i + 2])); pts = [cur]; i += 3
        elif t == "L":
            cur = (float(toks[i + 1]), float(toks[i + 2])); pts.append(cur); i += 3
        elif t == "C":
            c = [float(x) for x in toks[i + 1:i + 7]]
            for k in range(1, 9):
                u = k / 8
                x = (1-u)**3*cur[0] + 3*(1-u)**2*u*c[0] + 3*(1-u)*u*u*c[2] + u**3*c[4]
                y = (1-u)**3*cur[1] + 3*(1-u)**2*u*c[1] + 3*(1-u)*u*u*c[3] + u**3*c[5]
                pts.append((x, y))
            cur = (c[4], c[5]); i += 7
        elif t == "Z":
            subs.append(pts); pts = []; i += 1
        else: i += 1
    if pts: subs.append(pts)
eps = float(sys.argv[1]) if len(sys.argv) > 1 else 9
def ring(s):
    far = max(range(len(s)), key=lambda i: (s[i][0] - s[0][0]) ** 2 + (s[i][1] - s[0][1]) ** 2)
    a, b = rdp(s[:far + 1], eps), rdp(s[far:] + [s[0]], eps)
    return a[:-1] + b[:-1]
out = [[[round(x, 1), round(y, 1)] for x, y in ring(s)] for s in subs if len(s) > 3]
json.dump(out, open("lettering.json", "w"))
print(len(out), sum(len(s) for s in out))
