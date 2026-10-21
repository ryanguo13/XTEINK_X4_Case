# -*- coding: utf-8 -*-
"""
阅星曈 X4 (XTEINK X4) —— 两件套 3D 打印外壳 (Fusion 360 参数化脚本)
=====================================================================

运行方式 A (推荐, 免装任何东西):
    Fusion 里打开 实用工具 > 脚本和附加模块 > 脚本 标签 > 创建
    语言选 Python, 文件名 x4_case, 把本文件内容整段粘进去, 点 运行。

运行方式 B (通过 Fusion MCP):
    mcp({tool:"local-mcp_fusion_mcp_execute",
         args:{featureType:"script", object:{script:"<本文件内容>", readOnly:false}}})

--------------------------------------------------------------------------
设计说明
--------------------------------------------------------------------------
两件套:
  X4_back_shell   全包背壳: 背板 2.0 + 侧壁 1.8, 前口做 0.8 让位环
  X4_front_frame  前框: 面板 1.2 + 0.7 裙边, 裙边内侧 0.35 卡筋
  两者外侧轮廓齐平, 接缝落在侧壁, 卡筋卡进背壳前口的环形卡槽 (径向过盈 0.10)

风格: 方正工业风 —— 外形以直角为主, 只保留 3.0 mm 小圆角; 所有开孔避让保持利落,
      孔口不做倒角, 只做 0.5 外形圆角。

  ★ 圆角不是一个可以随便调大的数字, 它被两个硬约束夹住 (详细推导见 docs/TECH_SPEC.md):
      Ro = outer_cr   外形平面内圆角
      Ri = inner_cr   内腔平面内圆角
    (a) 角部壁厚 >= wall:  角部壁厚 = (Ro - Ri) + (2*clr + 2*wall - 2*clr) ... 实测见下表
    (b) 设备不磕角:        当前 inner_cr(3.0) > dev_cr(4.0) 时不成立, 需验算
    已验算的取值 (角部最小壁厚 / 角部设备间隙):
        Ro=6.8, Ri=5.0 -> 1.80 / 0.08   <-- 旧值, 圆角大且角部设备间隙只剩 0.08 mm
        Ro=3.0, Ri=3.0 -> 2.13 / 0.56   <-- 当前值, 更方正且角部余量更大
    改 Ro/Ri 后必须重跑本脚本看 [干涉] 一行是否为 OK。
按钮: 按需求"不做造型, 直接镂空"。电源键/翻页键所在的侧壁外表面另铣 0.6 浅凹台,
      手指可直接按到设备实体按键; 正面两条胶囊键同样直接开出贯穿窗口。
背面: 62.6 x 107.6 装饰面板内凹 0.5, 中心 φ60 磁吸环槽再下切 0.35,
      磁环落位后上方余料 1.15 mm。

坐标系 (设备中心为原点):
    X = 宽 69   (+X = 正面照右手侧: 电源/翻页/TF卡/RESET)
    Y = 高 114  (+Y = 顶部)
    Z = 厚 5.98 (0 = 设备背面, 5.98 = 设备正面/屏幕面)
    -X = 正面照左手侧 (USB-C / LED / 挂绳孔), 全部在设备下端同一短边上

侧边/正面开孔沿 Y 的位置来自照片像素测量, 误差约 ±1 mm。
打印前请用卡尺复核 P 里带 (*) 的项 —— 只改数字重跑脚本即可。

打印朝向:
    背壳: 开口朝上, 背板贴床, 无需支撑
    前框: 面板贴床, 裙边朝上, 无需支撑
"""

import adsk.core
import adsk.fusion
import math
import os

# ============================================================================
# 参数 (mm)
# ============================================================================
P = dict(
    # ---------------- 设备本体 ----------------
    dev_w=69.0, dev_h=114.0, dev_d=5.98, dev_cr=4.0,

    # ---------------- 壳体通用 ----------------
    wall=1.8,            # 背壳侧壁厚
    clr=0.35,            # 设备与内腔单边间隙
    back_t=2.0,          # 背板厚
    frame_t=1.2,         # 前框面板厚
    outer_cr=3.0,        # 外形平面内圆角 (方正化: 6.8 -> 3.0)
    inner_cr=3.0,        # 内腔圆角     (方正化: 5.0 -> 3.0, 角部壁厚 2.13 / 设备间隙 0.56)

    # ---------------- 两件套卡接 ----------------
    rebate_d=0.80,       # 背壳前口让位(前口环壁剩下的厚度 = wall - rebate_d = 1.0)
    skirt_gap=0.10,      # 裙边内表面与让位面径向间隙
    skirt_h=1.20,        # 裙边高度
    ridge_p=0.35,        # 裙边卡筋径向凸出
    groove_d=0.35,       # 背壳卡槽径向深度 (过盈 = ridge_p - skirt_gap - groove_d = 0.10)
    ridge_z0=5.30,       # 卡筋/卡槽 Z 起
    ridge_z1=5.70,       # 卡筋/卡槽 Z 止

    # ---------------- 屏幕窗口 ----------------
    scr_w=55.4, scr_h=92.4,     # 4.3" 480x800 @ ~220ppi 有效显示区
    scr_top=6.5,                # (*) 屏幕顶边到设备顶边
    win_clr=0.50, win_cr=1.5,      # 窗口圆角同步收方正 (2.5 -> 1.5)

    # ---------------- 正面两条胶囊按键 (直接镂空) ----------------
    fk_yc=4.40,          # (*) 按键轴线距设备底边
    fk1_len=24.0, fk2_len=21.9, fk_gap=1.5,
    fk_h=2.60, fk_clr=0.40, fk_cr=1.30,   # clr 收紧到 0.4 -> 两键间留 0.7 竖筋

    # ---------------- +X 侧 ----------------
    pwr_y=33.3, pwr_h=9.2, pwr_kh=2.60,      # (*) 电源键
    pg_y=3.4,   pg_h=19.3, pg_kh=2.60,       # (*) 翻页摇杆
    tf_y=-14.0, tf_h=14.0, tf_kh=1.80,       # (*) TF 卡槽
    rst_y=-27.0, rst_d=1.6,                  # (*) RESET 针孔
    side_relief=0.60,                        # 按键处外表面浅凹台深度
    relief_pad_y=2.5, relief_pad_z=0.8,

    # ---------------- -X 侧 (设备左侧长边, 集中在下端) ----------------
    usbc_y=-35.0, usbc_w=9.0, usbc_h=3.4,    # (*) USB-C
    led_y=-42.5,  led_d=1.6,                 # (*) 充电指示灯
    lany_y=-50.0, lany_w=5.0, lany_h=3.6,    # (*) 挂绳孔
    lany_cr=1.2,

    # ---------------- 背面 ----------------
    panel_w=62.6, panel_h=107.6, panel_cr=1.5, panel_depth=0.50,
    ring_od=60.0, ring_id=57.6, ring_depth=0.35,     # 磁吸环 (φ60 环, 2.4 宽)

    # ---------------- 正面按键沉台 (让按键浅陷 0.6, 保证按键凸起时仍可按) ----------------
    kb_d=0.60, kb_clr=1.00,          # 沉台深 / 沉台单边再放大

    # ---------------- 内腔缓冲垫沉台 (贴 4 个 12x12 泡棉垫) ----------------
    pad_w=12.0, pad_h=12.0, pad_depth=0.40, pad_dx=22.0, pad_dy=45.0,

    # ---------------- 外观 ----------------
    edge_fillet=0.5,     # 背壳底面 / 前框顶面 环形倒圆
    frame_top_fillet=0.4,  # 前框顶面倒圆 (原为硬编码 0.4, 提为参数)

    # ---------------- 输出 ----------------
    out_dir="C:/Users/jguo121/Documents/X4/stl",
)

MM = 0.1              # 1 mm = 0.1 cm
FAR = 300.0           # 贯穿切割用的"足够远"距离 (比 through-all 稳)


def corner_metrics(Ro, Ri, hw, hh, clr, wall, dev_cr, n=720):
    """角部几何实测: 返回 (角部最小壁厚, 角部设备间隙)。

    圆角同尺寸矩形的角部不能用"半宽差"算，必须采样求最小距离。
    """
    def pts(a_hw, a_hh, r):
        out = []
        for cx, cy, a0 in ((a_hw - r, a_hh - r, 0.0), (-a_hw + r, a_hh - r, 90.0),
                           (-a_hw + r, -a_hh + r, 180.0), (a_hw - r, -a_hh + r, 270.0)):
            for i in range(n + 1):
                a = math.radians(a0 + 90.0 * i / n)
                out.append((cx + r * math.cos(a), cy + r * math.sin(a)))
        return out

    tub_hw, tub_hh = hw + clr + wall, hh + clr + wall
    cav_hw, cav_hh = hw + clr, hh + clr
    O = pts(tub_hw, tub_hh, Ro)
    I = pts(cav_hw, cav_hh, Ri)
    D = pts(hw, hh, dev_cr)

    def mind(A, B):
        st = max(1, len(A) // 180)
        return min(math.hypot(p[0] - q[0], p[1] - q[1])
                   for p in A[::st] for q in B[::st])

    return mind(O, I), mind(I, D)


def V(mm):
    return adsk.core.ValueInput.createByReal(mm * MM)


def P3(x, y, z=0.0):
    return adsk.core.Point3D.create(x * MM, y * MM, z * MM)


# ============================================================================
# 几何小工具
# ============================================================================
def rrect_g(sk, pt, x0, y0, x1, y1, r):
    """圆角矩形轮廓 (逆时针闭合), pt(x,y) 负责把局部 mm 映射成草图点。"""
    r = max(0.05, min(r, (x1 - x0) / 2.0 - 0.05, (y1 - y0) / 2.0 - 0.05))
    L, A = sk.sketchCurves.sketchLines, sk.sketchCurves.sketchArcs
    q = math.pi / 2.0
    L.addByTwoPoints(pt(x0 + r, y0), pt(x1 - r, y0))
    A.addByCenterStartSweep(pt(x1 - r, y0 + r), pt(x1 - r, y0), q)
    L.addByTwoPoints(pt(x1, y0 + r), pt(x1, y1 - r))
    A.addByCenterStartSweep(pt(x1 - r, y1 - r), pt(x1, y1 - r), q)
    L.addByTwoPoints(pt(x1 - r, y1), pt(x0 + r, y1))
    A.addByCenterStartSweep(pt(x0 + r, y1 - r), pt(x0 + r, y1), q)
    L.addByTwoPoints(pt(x0, y1 - r), pt(x0, y0 + r))
    A.addByCenterStartSweep(pt(x0 + r, y0 + r), pt(x0, y0 + r), q)


def rrect(sk, x0, y0, x1, y1, r):
    """圆角矩形轮廓, 逆时针闭合。"""
    rrect_g(sk, P3, x0, y0, x1, y1, r)


def side_map(sk, wx):
    """返回 mm->草图点 的映射函数。用于 YZ 平面族 (草图局部 u,v 与世界 Y,Z 不一致)。
    世界坐标点 (wx, wy, wz) 投影到草图局部的 (u, v)。"""
    o, xa, ya, za = sk.transform.getAsCoordinateSystem()

    def pt(wy, wz):
        d = adsk.core.Vector3D.create(wx * MM - o.x, wy * MM - o.y, wz * MM - o.z)
        return adsk.core.Point3D.create(d.dotProduct(xa), d.dotProduct(ya), 0.0)
    return pt


def rrect_area(x0, y0, x1, y1, r):
    r = max(0.05, min(r, (x1 - x0) / 2.0 - 0.05, (y1 - y0) / 2.0 - 0.05))
    return (x1 - x0) * (y1 - y0) - (4.0 - math.pi) * r * r


def prof_area_mm2(pr):
    return pr.areaProperties(adsk.fusion.CalculationAccuracy.LowCalculationAccuracy).area / (MM * MM)


def pick_profile(sk, expect=None, tag="", tol=0.35):
    best = None
    for i in range(sk.profiles.count):
        pr = sk.profiles.item(i)
        a = prof_area_mm2(pr)
        if expect is None:
            if best is None or a > best[0]:
                best = (a, pr)
        else:
            if best is None or abs(a - expect) < abs(best[0] - expect):
                best = (a, pr)
    if best is None:
        raise RuntimeError("草图无有效轮廓: " + tag)
    if expect is not None:
        err = abs(best[0] - expect) / max(expect, 1e-6)
        print("    [profile] %-18s area=%9.1f / expect=%9.1f  err=%5.2f%%" % (tag, best[0], expect, err * 100))
        if err > tol:
            raise RuntimeError("轮廓面积不匹配: %s (%.1f vs %.1f)" % (tag, best[0], expect))
    return best[1]


def rect_prof(sk, x0, y0, x1, y1, tag=""):
    sk.sketchCurves.sketchLines.addTwoPointRectangle(P3(x0, y0), P3(x1, y1))
    return pick_profile(sk, (x1 - x0) * (y1 - y0), tag)


def rr_prof(sk, x0, y0, x1, y1, r, tag=""):
    rrect(sk, x0, y0, x1, y1, r)
    return pick_profile(sk, rrect_area(x0, y0, x1, y1, r), tag)


def ring_prof(sk, hw_in, hh_in, r_in, hw_out, hh_out, r_out, tag=""):
    """外框 - 内框 的环形轮廓。"""
    rrect(sk, -hw_out, -hh_out, hw_out, hh_out, r_out)
    rrect(sk, -hw_in, -hh_in, hw_in, hh_in, r_in)
    a = rrect_area(-hw_out, -hh_out, hw_out, hh_out, r_out) - \
        rrect_area(-hw_in, -hh_in, hw_in, hh_in, r_in)
    return pick_profile(sk, a, tag)


def circle_prof(sk, cx, cy, d, tag=""):
    sk.sketchCurves.sketchCircles.addByCenterRadius(P3(cx, cy), d / 2.0 * MM)
    return pick_profile(sk, math.pi * (d / 2.0) ** 2, tag)


# ============================================================================
# 特征小工具
# ============================================================================
CUT = adsk.fusion.FeatureOperations.CutFeatureOperation
NEW = adsk.fusion.FeatureOperations.NewBodyFeatureOperation
JOIN = adsk.fusion.FeatureOperations.JoinFeatureOperation
ED = adsk.fusion.ExtentDirections
POS = ED.PositiveExtentDirection     # 沿草图平面法向 (+Z / +X)
NEG = ED.NegativeExtentDirection


def off_plane(comp, base, z_mm):
    inp = comp.constructionPlanes.createInput()
    inp.setByOffset(base, V(z_mm))
    return comp.constructionPlanes.add(inp)


def extrude(comp, prof, op, dist_mm, positive=True, name="", target=None):
    """拉伸。target 用于限定"这次切削只能动哪个实体"。

    ★ 必须传 target 的理由（踩过的坑）:
    CutFeatureOperation 的默认作用域是"整个设计"，不是"当前零件"。前框裙边的
    内腔切削轮廓 (in_hw = red_hw + skirt_gap) 从径向看把背壳前口那道 1.0 宽的环壁
    (cav_hw..red_hw) 也包在里面，于是前框的切削会把背壳的环壁咬掉一块，
    并把它从主体上分离成一个 0.2 cm3 的碎实体。
    给 participantBodies 赋值后，切削只作用于指定的实体，不再越界。
    """
    ex = comp.features.extrudeFeatures
    inp = ex.createInput(prof, op)
    if target is not None and op in (CUT, adsk.fusion.FeatureOperations.IntersectFeatureOperation):
        # 注意: participantBodies 的正确类型是 list[BRepBody]，不是 ObjectCollection
        # （传 ObjectCollection 会报 TypeError: argument 2 of type 'std::vector<...>'）
        inp.participantBodies = list(target if isinstance(target, (list, tuple)) else [target])
    inp.setOneSideExtent(adsk.fusion.DistanceExtentDefinition.create(V(abs(dist_mm))),
                         POS if positive else NEG)
    f = ex.add(inp)
    if name:
        f.name = name
    return f


def extrude_two(comp, prof, op, d_pos, d_neg, name=""):
    ex = comp.features.extrudeFeatures
    inp = ex.createInput(prof, op)
    inp.setTwoSidesExtent(adsk.fusion.DistanceExtentDefinition.create(V(d_pos)),
                          adsk.fusion.DistanceExtentDefinition.create(V(d_neg)))
    f = ex.add(inp)
    if name:
        f.name = name
    return f


def fillet_z_loop(comp, body, z_mm, r_mm, label="", tol=0.02):
    """把恰好位于 z_mm 平面上的整圈边一起倒圆 (调用前该平面应只有一圈边)。"""
    coll = adsk.core.ObjectCollection.create()
    n = 0
    for i in range(body.edges.count):
        e = body.edges.item(i)
        v0, v1 = e.startVertex, e.endVertex
        if v0 is None or v1 is None:
            continue
        if abs(v0.geometry.z - z_mm * MM) < tol * MM and abs(v1.geometry.z - z_mm * MM) < tol * MM:
            coll.add(e)
            n += 1
    if n == 0:
        print("    [fillet] %s: 无 z=%.2f 的边, 跳过" % (label, z_mm))
        return None
    fi = comp.features.filletFeatures.createInput()
    fi.addConstantRadiusEdgeSet(coll, V(r_mm), True)
    f = comp.features.filletFeatures.add(fi)
    print("    [fillet] %-18s %d 条边 @ z=%.2f r=%.2f" % (label, n, z_mm, r_mm))
    return f


# ============================================================================
def run(_context: str):
    app = adsk.core.Application.get()
    print("Fusion", app.version)

    # 清理旧文档, 保证从空开始
    for i in range(app.documents.count - 1, -1, -1):
        d0 = app.documents.item(i)
        if d0.isModified is False or d0.isModified is True:
            d0.close(False)

    doc = app.documents.add(adsk.core.DocumentTypes.FusionDesignDocumentType)
    dsn = adsk.fusion.Design.cast(app.activeProduct)
    try:
        dsn.designType = adsk.fusion.DesignTypes.ParametricDesignType
    except Exception:
        pass
    try:
        dsn.fusionUnitsManager.defaultLengthUnits = "mm"
    except Exception:
        pass
    root = dsn.rootComponent

    W, H, D = P["dev_w"], P["dev_h"], P["dev_d"]
    hw, hh = W / 2.0, H / 2.0
    zf = D                                        # 前框面板起始 Z
    tub_hw = hw + P["clr"] + P["wall"]            # 壳体外形半宽
    tub_hh = hh + P["clr"] + P["wall"]
    cav_hw, cav_hh = hw + P["clr"], hh + P["clr"] # 内腔半尺寸
    red_hw = tub_hw - P["rebate_d"]               # 前口让位面半宽
    red_hh = tub_hh - P["rebate_d"]
    red_cr = P["outer_cr"] - P["rebate_d"]
    z0 = zf - P["skirt_h"]                        # 裙边/卡筋 起始 Z
    in_hw = red_hw + P["skirt_gap"]               # 裙边内表面
    in_hh = red_hh + P["skirt_gap"]
    in_cr = red_cr + P["skirt_gap"]
    tip_hw = in_hw - P["ridge_p"]                 # 卡筋内顶点
    tip_hh = in_hh - P["ridge_p"]
    groove_hw = red_hw - P["groove_d"]            # 卡槽底 (径向)
    groove_hh = red_hh - P["groove_d"]

    print("")
    print("  外形    %.2f x %.2f x %.2f mm" % (2 * tub_hw, 2 * tub_hh, P["back_t"] + D + P["frame_t"]))
    print("  内腔    %.2f x %.2f x %.2f mm" % (2 * cav_hw, 2 * cav_hh, D))
    print("  前口环壁 %.2f | 裙边厚 %.2f | 卡筋径向过盈 %.2f | 磁环上方余料 %.2f" % (
        red_hw - cav_hw, tub_hw - in_hw,
        tip_hw - groove_hw, P["back_t"] - P["panel_depth"] - P["ring_depth"]))
    print("  平面圆角 外 %.2f / 内 %.2f (角部壁厚 %.2f, 角部设备间隙 %.2f)" % (
        P["outer_cr"], P["inner_cr"],
        *corner_metrics(P["outer_cr"], P["inner_cr"], hw, hh,
                        P["clr"], P["wall"], P["dev_cr"])))
    print("")

    # ========================================================================
    # 1) 全包背壳
    # ========================================================================
    back = root.occurrences.addNewComponent(adsk.core.Matrix3D.create()).component
    back.name = "X4_back_shell"
    print("[1] 全包背壳")

    # 1.1 外形主体 Z: -back_t .. dev_d
    sk = back.sketches.add(back.xYConstructionPlane)
    rrect(sk, -tub_hw, -tub_hh, tub_hw, tub_hh, P["outer_cr"])
    body = extrude_two(back, pick_profile(sk, tag="outer_solid"), NEW,
                       zf, P["back_t"], "back_shell_body").bodies.item(0)
    body.name = "back_shell"

    # 1.2 外底面整圈倒圆
    fillet_z_loop(back, body, -P["back_t"], P["edge_fillet"], "back_bottom")

    # 1.3 掏内腔 (底板留 back_t)
    sk = back.sketches.add(back.xYConstructionPlane)
    rrect(sk, -cav_hw, -cav_hh, cav_hw, cav_hh, P["inner_cr"])
    extrude(back, pick_profile(sk, tag="cavity"), CUT, FAR, True, "cavity", target=body)

    # 1.4 前口让位: 只切外圈环带 (red_hw .. 外形+2), Z: z0..zf
    pl = off_plane(back, back.xYConstructionPlane, z0)
    sk = back.sketches.add(pl)
    pr = ring_prof(sk, red_hw, red_hh, red_cr,
                   tub_hw + 2, tub_hh + 2, P["outer_cr"] + 0.5, "front_rebate")
    extrude(back, pr, CUT, FAR, True, "front_rebate", target=body)

    # 1.5 卡点环槽: 让位面再多吃 groove_d, Z: ridge_z0..ridge_z1
    pl = off_plane(back, back.xYConstructionPlane, P["ridge_z0"])
    sk = back.sketches.add(pl)
    pr = ring_prof(sk, groove_hw, groove_hh, red_cr - P["groove_d"],
                   tub_hw + 2, tub_hh + 2, P["outer_cr"] + 0.5, "snap_groove")
    extrude(back, pr, CUT, P["ridge_z1"] - P["ridge_z0"], True, "snap_groove", target=body)

    # 1.6 背面装饰面板内凹 (自外底面往上 panel_depth)
    pl = off_plane(back, back.xYConstructionPlane, -P["back_t"])
    sk = back.sketches.add(pl)
    pr = rr_prof(sk, -P["panel_w"] / 2, -P["panel_h"] / 2,
                 P["panel_w"] / 2, P["panel_h"] / 2, P["panel_cr"], "back_panel")
    extrude(back, pr, CUT, P["panel_depth"], True, "back_panel", target=body)

    # 1.7 磁吸环槽 (自面板底再下切 ring_depth)
    pl = off_plane(back, back.xYConstructionPlane, -P["back_t"] + P["panel_depth"])
    sk = back.sketches.add(pl)
    sk.sketchCurves.sketchCircles.addByCenterRadius(P3(0, 0), P["ring_od"] / 2.0 * MM)
    sk.sketchCurves.sketchCircles.addByCenterRadius(P3(0, 0), P["ring_id"] / 2.0 * MM)
    a_ring = math.pi * ((P["ring_od"] / 2.0) ** 2 - (P["ring_id"] / 2.0) ** 2)
    extrude(back, pick_profile(sk, a_ring, "ring_groove"), CUT, P["ring_depth"], True,
            "ring_groove", target=body)

    # 1.8 内腔 4 个缓冲垫沉台
    for sx in (-1, 1):
        for sy in (-1, 1):
            sk = back.sketches.add(back.xYConstructionPlane)
            cx, cy = sx * P["pad_dx"], sy * P["pad_dy"]
            pr = rr_prof(sk, cx - P["pad_w"] / 2, cy - P["pad_h"] / 2,
                         cx + P["pad_w"] / 2, cy + P["pad_h"] / 2, 2.0, "pad")
            extrude(back, pr, CUT, P["pad_depth"], False, "pad_pocket", target=body)

    # 1.9 侧壁开孔 —— 草图基准 = yZConstructionPlane (草图 u=+Y, v=+Z, 法向 +X)
    zc = D / 2.0

    def side(yc, ylen, zlen, sign, label, circle_d=None, arc_r=0.0, depth=None):
        """在 ±X 侧壁按 (yc, zc) 为中心开贯穿孔, 或从 (tub_hw-depth) 起铣凹台。"""
        if depth is None:                      # 贯穿
            plane = back.yZConstructionPlane
            dist = tub_hw + 3.0
        else:                                  # 浅凹台
            plane = off_plane(back, back.yZConstructionPlane, sign * (tub_hw - depth))
            dist = depth + 3.0
        sk = back.sketches.add(plane)
        pt = side_map(sk, 0.0 if depth is None else sign * (tub_hw - depth))
        # 世界坐标下的孔矩形: Y 区间 / Z 区间
        ya0, ya1 = yc - ylen / 2.0, yc + ylen / 2.0
        za0, za1 = zc - zlen / 2.0, zc + zlen / 2.0
        if circle_d:
            sk.sketchCurves.sketchCircles.addByCenterRadius(pt(yc, zc), circle_d / 2.0 * MM)
            pr = pick_profile(sk, math.pi * (circle_d / 2.0) ** 2, label)
        else:
            rrect_g(sk, pt, ya0, za0, ya1, za1, arc_r)
            pr = pick_profile(sk, rrect_area(ya0, za0, ya1, za1, arc_r), label)
        extrude(back, pr, CUT, dist, sign > 0, label, target=body)

    # +X: 电源键 / 翻页摇杆 —— 先铣 0.6 浅凹台, 再开贯穿孔
    for yc, yl, kh, lab in ((P["pwr_y"], P["pwr_h"], P["pwr_kh"], "pwr"),
                            (P["pg_y"], P["pg_h"], P["pg_kh"], "page")):
        side(yc, yl + 2 * P["relief_pad_y"], kh + 2 * P["relief_pad_z"], 1,
             lab + "_relief", arc_r=0.0, depth=P["side_relief"])
        side(yc, yl, kh, 1, lab + "_hole")
    # +X: TF 卡槽 / RESET
    side(P["tf_y"], P["tf_h"], P["tf_kh"], 1, "tf_slot")
    side(P["rst_y"], 0, 0, 1, "reset_hole", circle_d=P["rst_d"])
    # -X: USB-C / LED / 挂绳孔
    side(P["usbc_y"], P["usbc_w"], P["usbc_h"], -1, "usbc")
    side(P["led_y"], 0, 0, -1, "led_hole", circle_d=P["led_d"])
    side(P["lany_y"], P["lany_w"], P["lany_h"], -1, "lanyard", arc_r=P["lany_cr"])

    print("  背壳完成  体积 %.2f cm3" % body.volume)

    # ========================================================================
    # 2) 前框
    # ========================================================================
    fr = root.occurrences.addNewComponent(adsk.core.Matrix3D.create()).component
    fr.name = "X4_front_frame"
    print("[2] 前框")

    # 2.1 裙边实体 Z: z0..zf
    sk = fr.sketches.add(off_plane(fr, fr.xYConstructionPlane, z0))
    rrect(sk, -tub_hw, -tub_hh, tub_hw, tub_hh, P["outer_cr"])
    skirt = extrude(fr, pick_profile(sk, tag="skirt"), NEW, P["skirt_h"], True, "skirt").bodies.item(0)

    # 2.2 裙边内腔: 卡筋带以外全掏空
    #     target=skirt: 否则切削会越界咬到背壳前口环壁 (见 extrude() 注释)
    for zlo, zhi, lab in ((z0, P["ridge_z0"], "skirt_lo"), (P["ridge_z1"], zf, "skirt_hi")):
        sk = fr.sketches.add(off_plane(fr, fr.xYConstructionPlane, zlo))
        rrect(sk, -in_hw, -in_hh, in_hw, in_hh, in_cr)
        extrude(fr, pick_profile(sk, tag=lab), CUT, zhi - zlo, True, lab, target=skirt)

    # 2.3 卡筋带: 只留 tip_hw..in_hw 一圈
    sk = fr.sketches.add(off_plane(fr, fr.xYConstructionPlane, P["ridge_z0"]))
    rrect(sk, -tip_hw, -tip_hh, tip_hw, tip_hh, in_cr - P["ridge_p"])
    extrude(fr, pick_profile(sk, tag="ridge_band"), CUT, P["ridge_z1"] - P["ridge_z0"], True,
            "ridge_band", target=skirt)

    # 2.4 面板 Z: zf..zf+frame_t, 与裙边并成一个实体
    sk = fr.sketches.add(off_plane(fr, fr.xYConstructionPlane, zf))
    rrect(sk, -tub_hw, -tub_hh, tub_hw, tub_hh, P["outer_cr"])
    plate = extrude(fr, pick_profile(sk, tag="plate"), NEW, P["frame_t"], True, "plate").bodies.item(0)
    ci = fr.features.combineFeatures.createInput(plate, _oc([skirt]))
    ci.operation = JOIN
    fr.features.combineFeatures.add(ci)

    # 2.5 外顶面整圈倒圆
    fillet_z_loop(fr, plate, zf + P["frame_t"], P["frame_top_fillet"], "frame_top")

    # 2.6 屏幕窗口
    wwin = P["scr_w"] + 2 * P["win_clr"]
    hwin = P["scr_h"] + 2 * P["win_clr"]
    y_c = (hh - P["scr_top"]) - P["scr_h"] / 2.0
    sk = fr.sketches.add(fr.xYConstructionPlane)
    pr = rr_prof(sk, -wwin / 2, y_c - hwin / 2, wwin / 2, y_c + hwin / 2, P["win_cr"], "screen_win")
    extrude(fr, pr, CUT, FAR, True, "screen_window", target=plate)
    print("  屏幕窗口 %.2f x %.2f  Yc=%.2f  上边框 %.1f / 下边框 %.1f" % (
        wwin, hwin, y_c, hh - (y_c + hwin / 2), (y_c - hwin / 2) + hh))

    # 2.7 正面两条胶囊按键镂空
    yk = -hh + P["fk_yc"]
    kh = P["fk_h"] + 2 * P["fk_clr"]
    x_cur = -(P["fk1_len"] + P["fk_gap"] + P["fk2_len"]) / 2.0
    for i, flen in enumerate((P["fk1_len"], P["fk2_len"])):
        # 贯穿开窗
        sk = fr.sketches.add(fr.xYConstructionPlane)
        pr = rr_prof(sk, x_cur - P["fk_clr"], yk - kh / 2,
                     x_cur + flen + P["fk_clr"], yk + kh / 2, P["fk_cr"], "front_key%d" % (i + 1))
        extrude(fr, pr, CUT, FAR, True, "front_key_%d" % (i + 1), target=plate)
        # 外表面 0.6 沉台 (只向外/上下放大, 内侧贴死 → 两键之间的竖筋不会被吞掉)
        c = P["kb_clr"]
        xo0 = x_cur - P["fk_clr"] - (c if i == 0 else 0.0)
        xo1 = x_cur + flen + P["fk_clr"] + (0.0 if i == 0 else c)
        sk = fr.sketches.add(off_plane(fr, fr.xYConstructionPlane, zf + P["frame_t"] - P["kb_d"]))
        pr = rr_prof(sk, xo0, yk - kh / 2 - c,
                     xo1, yk + kh / 2 + c, P["fk_cr"] + c,
                     "front_key%d_cb" % (i + 1))
        extrude(fr, pr, CUT, P["kb_d"], True, "front_key_%d_counterbore" % (i + 1), target=plate)
        print("  正面按键 %d: X %.2f .. %.2f  Yc=%.2f" % (i + 1, x_cur, x_cur + flen, yk))
        x_cur += flen + P["fk_gap"]

    print("  前框完成  体积 %.2f cm3" % plate.volume)

    # ========================================================================
    # 3) 设备参考体 (仅检查干涉, 不打印)
    # ========================================================================
    rc = root.occurrences.addNewComponent(adsk.core.Matrix3D.create()).component
    rc.name = "X4_device_reference"
    sk = rc.sketches.add(rc.xYConstructionPlane)
    rrect(sk, -hw, -hh, hw, hh, P["dev_cr"])
    dev = extrude(rc, pick_profile(sk, tag="device"), NEW, D, True, "device").bodies.item(0)
    try:
        dev.opacity = 0.30
        rc.isLightBulbOn = True
    except Exception:
        pass

    print("")
    # ========================================================================
    # 4) 干涉检查、导出 STL
    # ========================================================================
    back_b = biggest(back)
    frame_b = biggest(fr)

    # 4.1 干涉检查 (只算实体重叠, 不算面贴合)
    def ifc(b1, b2, tag):
        try:
            ic = adsk.core.ObjectCollection.create()
            ic.add(b1)
            ic.add(b2)
            ii = dsn.createInterferenceInput(ic)
            ii.isCoincidentFacesIncluded = False
            res = dsn.analyzeInterference(ii)
            tot = sum(res.item(k).volume for k in range(res.count))
            print("    [干涉] %-26s %d 处  %.5f cm3%s" % (
                tag, res.count, tot, "  <— 需修正" if tot > 1e-5 else "  OK"))
        except Exception as e:
            print("    [干涉] %s 跳过 (%s)" % (tag, e))

    ifc(back_b, dev, "背壳 vs 设备")
    ifc(frame_b, dev, "前框 vs 设备")
    ifc(back_b, frame_b, "背壳 vs 前框")

    # 4.2 导出 STL
    out = P["out_dir"].rstrip("/")
    try:
        if not os.path.isdir(out):
            os.makedirs(out)
    except Exception:
        pass
    for b, nm in ((back_b, "X4_back_shell"), (frame_b, "X4_front_frame")):
        try:
            path = out + "/" + nm + ".stl"
            opt = dsn.exportManager.createSTLExportOptions(b, path)
            opt.meshRefinement = adsk.fusion.MeshRefinementSettings.MeshRefinementHigh
            opt.isBinaryFormat = True
            opt.sendToPrintUtility = False
            dsn.exportManager.execute(opt)
            print("    [STL] %s" % path)
        except Exception as e:
            print("    [STL] %s 失败: %s" % (nm, e))

    print("")
    print("DONE  X4_back_shell + X4_front_frame (+ X4_device_reference)")
    print("     设备放入后总厚 %.2f mm, 外形 %.2f x %.2f mm" % (
        P["back_t"] + D + P["frame_t"], 2 * tub_hw, 2 * tub_hh))


def biggest(comp):
    best = None
    for i in range(comp.bRepBodies.count):
        b = comp.bRepBodies.item(i)
        a = abs(b.volume)
        if best is None or a > best[0]:
            best = (a, b)
    return best[1]


def _oc(items):
    c = adsk.core.ObjectCollection.create()
    for it in items:
        c.add(it)
    return c
