"""Flying-carpet motion: inextensible travelling waves for the rug + verlet fringes. Pure numpy.

python3 rug_motion.py <cache.npy>   precomputes the looping fringe simulation.
"""
import math, os, sys
import numpy as np

FPS = 30
LOOP = 180                       # 6 s loop
KW, KH, KIL = 420, 200, 10       # knot grid from rug_tex.py
L = 4.2                          # rug length (x), knots are 1 cm
WD = L * KH / KW                 # rug width (y)
NX, NY = 168, 80                 # grid segments
TAU = 2 * math.pi
W0 = TAU / LOOP                  # loop angular frequency (per frame)

# ---------------------------------------------------------------- rug motion
s_ = np.linspace(-L / 2, L / 2, NX + 1)
v_ = np.linspace(-WD / 2, WD / 2, NY + 1)
S, V = np.meshgrid(s_, v_)       # (NY+1, NX+1)
ds = L / NX

def rug_points(f):
    """World positions (NY+1, NX+1, 3) of the rug surface at (fractional) frame f."""
    t = f * W0
    u = (S + L / 2) / L                              # 0 at front, 1 at trailing end
    env = 0.55 + 0.75 * u ** 1.5                     # trailing end flutters more
    th = env * (0.30 * np.sin(TAU * S / 3.4 - 2 * t + 0.35 * V)
                + 0.10 * np.sin(TAU * S / 1.55 - 3 * t + 1.1 - 0.6 * V)
                + 0.03 * np.sin(TAU * S / 0.9 - 5 * t + 0.4 + 1.3 * V))
    # front edge rolls up a little, breathing with the loop
    th += -0.42 * np.clip((-S - (L / 2 - 0.55)) / 0.55, 0, 1) ** 2 * (1 + 0.15 * np.sin(2 * t + 0.8))
    # integrate arc length from the centre outwards -> no stretching along the rug
    c, sn = np.cos(th), np.sin(th)
    i0 = NX // 2
    x = np.zeros_like(S); z = np.zeros_like(S)
    mid_c = 0.5 * (c[:, 1:] + c[:, :-1]) * ds; mid_s = 0.5 * (sn[:, 1:] + sn[:, :-1]) * ds
    x[:, i0 + 1:] = np.cumsum(mid_c[:, i0:], axis=1)
    z[:, i0 + 1:] = np.cumsum(mid_s[:, i0:], axis=1)
    x[:, :i0] = -np.cumsum(mid_c[:, :i0][:, ::-1], axis=1)[:, ::-1]
    z[:, :i0] = -np.cumsum(mid_s[:, :i0][:, ::-1], axis=1)[:, ::-1]
    # across the width: a gentle twist travelling with the wave + soft cupping
    phi = 0.10 * np.sin(TAU * S / 3.0 - 2 * t + 2.0) * env
    y = V * np.cos(phi)
    z = z + V * np.sin(phi) + (0.05 + 0.02 * np.sin(t * 2 + 1.3)) * (V / (WD / 2)) ** 2
    z = z - z.mean()
    P = np.stack([x, y, z], -1)
    # rigid float: bob, roll, pitch, yaw (integer harmonics of the loop)
    roll = 0.05 * np.sin(t + 0.4) + 0.02 * np.sin(2 * t)
    pitch = 0.035 * np.sin(t + 2.1)
    yaw = 0.03 * np.sin(t + 1.0)
    cr, sr, cp, sp, cy, sy = math.cos(roll), math.sin(roll), math.cos(pitch), math.sin(pitch), math.cos(yaw), math.sin(yaw)
    Rx = np.array([[1, 0, 0], [0, cr, -sr], [0, sr, cr]])
    Ry = np.array([[cp, 0, sp], [0, 1, 0], [-sp, 0, cp]])
    Rz = np.array([[cy, -sy, 0], [sy, cy, 0], [0, 0, 1]])
    P = P @ (Rz @ Ry @ Rx).T
    P[..., 2] += 0.05 * math.sin(t + 0.3) + 0.015 * math.sin(3 * t)
    return P

# ---------------------------------------------------------------- fringe sim
NB = 26                           # bundles per end
PER = 4                           # threads per bundle
NS = NB * PER
SEG = 14
FL = 0.24                         # fringe length
KNOT = 2                          # node index where each bundle is tied
rng = np.random.default_rng(11)
lengths = FL * rng.uniform(0.85, 1.12, (2, NS))
seglen = lengths / SEG
# anchor v-positions along the edge, inside the binding
va = np.linspace(-WD / 2 + 0.05, WD / 2 - 0.05, NS)

def edge_frame(P, end):
    """Anchor points + outward tangent at an end (0 front, 1 back) for every thread."""
    col = 0 if end == 0 else -1
    nb = 1 if end == 0 else -2
    edge = P[:, col]; inner = P[:, nb]
    vv = v_
    out = edge - inner
    out /= np.linalg.norm(out, axis=1, keepdims=True)
    A = np.stack([np.interp(va, vv, edge[:, k]) for k in range(3)], -1)
    T = np.stack([np.interp(va, vv, out[:, k]) for k in range(3)], -1)
    T /= np.linalg.norm(T, axis=1, keepdims=True)
    return A, T

def simulate():
    sub = 10
    dt = 1.0 / (FPS * sub)
    g = np.array([0, 0, -9.8 * 0.4])
    warm = 3
    total = (warm + 1) * LOOP
    pos = np.zeros((2, NS, SEG + 1, 3)); prev = None
    for end in (0, 1):
        A, T = edge_frame(rug_points(0), end)
        for i in range(SEG + 1):
            pos[end, :, i] = A + T * seglen[end][:, None] * i
    prev = pos.copy()
    rec = np.zeros((2, LOOP, 2, NS, SEG + 1, 3))      # last two loops
    phase = rng.uniform(0, TAU, NS)
    for F in range(total):
        for k in range(sub):
            f = F + k / sub
            P = rug_points(f)
            t = f * W0
            for end in (0, 1):
                A, T = edge_frame(P, end)
                # relative wind of flight (+x) with looping gusts per thread
                gust = 0.6 + 0.4 * np.sin(3 * t + phase) * np.sin(2 * t + 0.5 * phase)
                wind = np.zeros((NS, 3))
                wind[:, 0] = 4.2 * gust
                wind[:, 1] = 0.5 * np.sin(2 * t + phase)
                wind[:, 2] = 0.3 * np.sin(4 * t + phase * 1.7)
                p = pos[end]; q = prev[end]
                vel = (p - q) * 0.985
                acc = g[None, None] + wind[:, None] * np.linspace(0.2, 1.0, SEG + 1)[None, :, None]
                new = p + vel + acc * dt * dt
                new[:, 0] = A
                new[:, 1] = A + T * seglen[end][:, None]       # root leaves the weave along the rug
                prev[end] = p; pos[end] = new
                ia = np.arange(SEG)[None, :, None]
                wa = np.where(ia <= 1, 0.0, 0.5)
                wb = np.where(ia == 0, 0.0, np.where(ia == 1, 1.0, 0.5))
                for it in range(8):
                    p = pos[end]
                    d = p[:, 1:] - p[:, :-1]
                    ln = np.linalg.norm(d, axis=2, keepdims=True) + 1e-9
                    corr = (ln - seglen[end][:, None, None]) / ln * d
                    p[:, :-1] += corr * wa
                    p[:, 1:] -= corr * wb
                    # bending: pull towards the midpoint of neighbours a little
                    p[:, 2:-1] += 0.03 * (0.5 * (p[:, 1:-2] + p[:, 3:]) - p[:, 2:-1])
                    # tie: knot node of each bundle shares a centre
                    kn = p[:, KNOT].reshape(NB, PER, 3)
                    cen = kn.mean(1, keepdims=True)
                    p[:, KNOT] = (kn + (cen - kn) * 0.85).reshape(NS, 3)
                    # keep threads under the rug when blown back over it
                    sgn = 1 if end == 0 else -1
                    nrm = np.cross(T, np.array([0, 1, 0])[None])
                    nrm /= np.linalg.norm(nrm, axis=1, keepdims=True)
                    nrm *= np.sign(nrm[:, 2:3] + 1e-9)          # rug's upward normal near the edge
                    rel = p - A[:, None]
                    inside = (rel * T[:, None]).sum(-1) < -0.002
                    up = (rel * nrm[:, None]).sum(-1)
                    bad = inside & (up > -0.012)
                    p[bad] -= (up[bad] + 0.012)[:, None] * np.broadcast_to(nrm[:, None], p.shape)[bad]
                    pos[end] = p
        if F >= (warm - 1) * LOOP:
            rec[F // LOOP - (warm - 1), F % LOOP] = pos
    # loop B[0] physically follows loop A[LOOP-1]: crossfade A -> B over the cycle for a seamless wrap
    A, B = rec
    print('fringe loop drift between cycles', float(np.abs(B - A).max()))
    w = (np.arange(LOOP) / LOOP)[:, None, None, None, None]
    return (1 - w) * B + w * A


if __name__ == '__main__':
    np.save(sys.argv[1], simulate())
