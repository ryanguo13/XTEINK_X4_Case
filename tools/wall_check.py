# -*- coding: utf-8 -*-
"""STL 壁厚自检 —— 找出 < 1 mm 的薄壁 (嘉立创退回的判据)。

判据: 对每个三角面片取内部采样点, 沿"指向实体内部"的面法向打射线, 最近的
另一侧表面距离就是该处的局部料厚。

三轮过滤 (都是"测量方法"层面的, 不改模型):
  1. 掠射   命中面与射线夹角过小 (|cos| < COS_TOL) —— 圆角/倒角与平面相切处
            会成排出现 0.0x 的假读数。
  2. 碎面   源面片或命中面片是细长条 (内切圆半径 < RIN_TOL) —— STL 在相切
            过渡带上会切出 0.1~0.2 mm 宽的窄条, 采样点本身离两条边都只有
            0.03 mm, 量出来必然是 0.00。
只依赖标准库。
用法: python3 tools/wall_check.py stl/X4_back_shell.stl [更多.stl ...]
退出码: 有薄壁 -> 1
"""
import math
import struct
import sys

LIMIT = 1.0      # 报警阈值 mm
MAXD = 3.0       # 射线最远距离 (超过就算够厚了)
CELL = 2.0       # 空间网格
EPS = 5e-3       # 起点离面偏移, 避免自交
MIN_LEN = 1e-3
COS_TOL = 0.25   # 射线与命中面 |cos| 下限, 低于视为掠射
RIN_TOL = 0.08   # 面片内切圆半径下限 mm, 低于视为碎面


def load(path):
    d = open(path, "rb").read()
    n = struct.unpack("<I", d[80:84])[0]
    tris, o = [], 84
    for _ in range(n):
        v = struct.unpack("<12f", d[o:o + 48])
        a = (v[3], v[4], v[5])
        b = (v[6], v[7], v[8])
        c = (v[9], v[10], v[11])
        o += 50
        ux, uy, uz = b[0] - a[0], b[1] - a[1], b[2] - a[2]
        vx, vy, vz = c[0] - a[0], c[1] - a[1], c[2] - a[2]
        nx = uy * vz - uz * vy
        ny = uz * vx - ux * vz
        nz = ux * vy - uy * vx
        L = math.sqrt(nx * nx + ny * ny + nz * nz)
        if L < 1e-12:
            continue
        # 内切圆半径 r = 2A/P = (2 * L/2) / P
        p = (math.dist(a, b) + math.dist(b, c) + math.dist(c, a))
        rin = L / p if p > 1e-12 else 0.0
        tris.append((a, b, c, (nx / L, ny / L, nz / L), L / 2.0, rin))
    return tris


class Grid(object):
    def __init__(self, tris):
        self.cells = {}
        for i, t in enumerate(tris):
            a, b, c = t[0], t[1], t[2]
            x0 = int(math.floor(min(a[0], b[0], c[0]) / CELL))
            x1 = int(math.floor(max(a[0], b[0], c[0]) / CELL))
            y0 = int(math.floor(min(a[1], b[1], c[1]) / CELL))
            y1 = int(math.floor(max(a[1], b[1], c[1]) / CELL))
            z0 = int(math.floor(min(a[2], b[2], c[2]) / CELL))
            z1 = int(math.floor(max(a[2], b[2], c[2]) / CELL))
            for ix in range(x0, x1 + 1):
                for iy in range(y0, y1 + 1):
                    for iz in range(z0, z1 + 1):
                        self.cells.setdefault((ix, iy, iz), []).append(i)

    def near(self, p, r):
        out, seen = [], set()
        x0 = int(math.floor((p[0] - r) / CELL))
        x1 = int(math.floor((p[0] + r) / CELL))
        y0 = int(math.floor((p[1] - r) / CELL))
        y1 = int(math.floor((p[1] + r) / CELL))
        z0 = int(math.floor((p[2] - r) / CELL))
        z1 = int(math.floor((p[2] + r) / CELL))
        for ix in range(x0, x1 + 1):
            for iy in range(y0, y1 + 1):
                for iz in range(z0, z1 + 1):
                    for i in self.cells.get((ix, iy, iz), ()):
                        if i not in seen:
                            seen.add(i)
                            out.append(i)
        return out


def cast(o, d, tris, idx, skip):
    """Möller-Trumbore: 返回 (最近正向交点距离, 命中面片索引) 或 None。"""
    best, besti = MAXD, -1
    for i in idx:
        if i == skip:
            continue
        a, b, c = tris[i][0], tris[i][1], tris[i][2]
        e1x, e1y, e1z = b[0] - a[0], b[1] - a[1], b[2] - a[2]
        e2x, e2y, e2z = c[0] - a[0], c[1] - a[1], c[2] - a[2]
        px = d[1] * e2z - d[2] * e2y
        py = d[2] * e2x - d[0] * e2z
        pz = d[0] * e2y - d[1] * e2x
        det = e1x * px + e1y * py + e1z * pz
        if -1e-10 < det < 1e-10:
            continue
        inv = 1.0 / det
        tx, ty, tz = o[0] - a[0], o[1] - a[1], o[2] - a[2]
        u = (tx * px + ty * py + tz * pz) * inv
        if u < 0.0 or u > 1.0:
            continue
        qx = ty * e1z - tz * e1y
        qy = tz * e1x - tx * e1z
        qz = tx * e1y - ty * e1x
        v = (d[0] * qx + d[1] * qy + d[2] * qz) * inv
        if v < 0.0 or u + v > 1.0:
            continue
        t = (e2x * qx + e2y * qy + e2z * qz) * inv
        if not (MIN_LEN < t < best):
            continue
        if tris[i][5] < RIN_TOL:                      # 命中碎面
            continue
        na = tris[i][3]
        if abs(d[0] * na[0] + d[1] * na[1] + d[2] * na[2]) < COS_TOL:
            continue                                  # 掠射
        best, besti = t, i
    return (best, besti) if besti >= 0 else None


def samples(a, b, c):
    """三角面片内的采样点 (重心坐标, 避开边界)。"""
    for w in ((0.3334, 0.3333, 0.3333), (0.70, 0.15, 0.15),
              (0.15, 0.70, 0.15), (0.15, 0.15, 0.70)):
        yield (w[0] * a[0] + w[1] * b[0] + w[2] * c[0],
               w[0] * a[1] + w[1] * b[1] + w[2] * c[1],
               w[0] * a[2] + w[1] * b[2] + w[2] * c[2])


def scan(path):
    tris = load(path)
    grid = Grid(tris)
    hits = []
    for i, t in enumerate(tris):
        a, b, c, n, ar, rin = t
        if rin < RIN_TOL:                              # 源面片是碎面
            continue
        idx = grid.near(a, MAXD)
        for s in samples(a, b, c):
            for sgn in (-1.0, 1.0):
                o = (s[0] + sgn * n[0] * EPS,
                     s[1] + sgn * n[1] * EPS,
                     s[2] + sgn * n[2] * EPS)
                d = (sgn * n[0], sgn * n[1], sgn * n[2])
                r = cast(o, d, tris, idx, i)
                if r is not None:
                    hits.append((r[0], s[0], s[1], s[2], d))
    hits.sort(key=lambda h: h[0])
    thin = []
    for h in hits:
        if h[0] >= LIMIT:
            continue
        thin.append(h)
    uniq = []
    for h in thin:
        if all(math.hypot(h[1] - u[1], h[2] - u[2]) > 2.0
               or abs(h[3] - u[3]) > 2.0 for u in uniq):
            uniq.append(h)
    xs = [p[0] for t in tris for p in t[:3]]
    ys = [p[1] for t in tris for p in t[:3]]
    zs = [p[2] for t in tris for p in t[:3]]
    print("=" * 76)
    print("%s   %d tris   bbox X %.1f..%.1f  Y %.1f..%.1f  Z %.1f..%.1f" % (
        path, len(tris), min(xs), max(xs), min(ys), max(ys), min(zs), max(zs)))
    if not uniq:
        print("  OK   最小壁厚 %.2f mm" % (hits[0][0] if hits else float("inf")))
    else:
        print("  !    %d 处 < %.1f mm 薄壁 (最薄 %.2f mm):" % (len(uniq), LIMIT, uniq[0][0]))
        for t, x, y, z, d in uniq[:40]:
            print("       %.2f mm   @X=%7.2f  Y=%7.2f  Z=%5.2f" % (t, x, y, z))
    return len(uniq), (hits[0][0] if hits else float("inf"))


if __name__ == "__main__":
    bad = 0
    for p in sys.argv[1:]:
        n, mn = scan(p)
        bad += n
    sys.exit(1 if bad else 0)
