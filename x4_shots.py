# -*- coding: utf-8 -*-
"""X4 外壳 —— 干净的多角度渲染截图"""
import adsk.core, adsk.fusion, os, time

OUT = "C:/Users/jguo121/Documents/X4/shots"
MM = 0.1

def run(_context):
    app = adsk.core.Application.get()
    dsn = adsk.fusion.Design.cast(app.activeProduct)
    root = dsn.rootComponent
    if not os.path.isdir(OUT):
        os.makedirs(OUT)

    occ = {}
    for i in range(root.occurrences.count):
        o = root.occurrences.item(i)
        occ[o.component.name] = o

    # 全部关闭, 之后按需打开
    for n, o in occ.items():
        o.isLightBulbOn = False
    # 网格 / 原点 / 轴 关掉
    for attr in ("isGridVisible", "isLayoutGridVisible", "isAxesVisible",
                 "isOriginFolderLightBulbOn", "isJointOriginsVisible"):
        try:
            setattr(root, attr, False)
        except Exception:
            pass

    vp = app.activeViewport
    V = adsk.core.ViewOrientations

    def shot(name, orient, show, extents_mm=0.0, up=None, center=None):
        for n, o in occ.items():
            o.isLightBulbOn = n in show
        cam = vp.camera
        cam.viewOrientation = orient
        if center is not None:
            cam.target = adsk.core.Point3D.create(center[0] * MM, center[1] * MM, center[2] * MM)
        vp.camera = cam
        vp.fit()
        cam = vp.camera
        cam.isFitView = False
        cam.isSmoothTransition = False
        if extents_mm:
            cam.viewExtents = extents_mm * MM * 1.0
        if up is not None:
            cam.upVector = adsk.core.Vector3D.create(*up)
        vp.camera = cam
        vp.refresh()
        adsk.doEvents()
        time.sleep(0.4)
        path = OUT + "/" + name + ".png"
        vp.saveAsImageFile(path, 1600, 1200)
        print("  %-26s %8d bytes" % (name, os.path.getsize(path)))

    ALL = ["X4_back_shell", "X4_front_frame"]
    BK  = ["X4_back_shell"]
    FR  = ["X4_front_frame"]

    shot("01_iso_front",  V.IsoTopRightViewOrientation, ALL, 190)
    shot("02_iso_back",   V.IsoBottomLeftViewOrientation, ALL, 190)
    shot("03_front",      V.FrontViewOrientation, ALL, 155, up=(0, 1, 0))
    shot("04_back",       V.BackViewOrientation, ALL, 155, up=(0, 1, 0))
    shot("05_right_side", V.RightViewOrientation, ALL, 18,  up=(0, 1, 0),
         center=(0, 0, 2.7))
    shot("06_left_side",  V.LeftViewOrientation, ALL, 18,  up=(0, 1, 0),
         center=(0, 2.7 * 0, 2.7))
    shot("07_back_shell_inside", V.IsoTopLeftViewOrientation, BK, 190)
    shot("08_front_frame_outside", V.IsoBottomRightViewOrientation, FR, 175)

    # 爆炸视图 (前框 +Z 抬起 6mm)
    for n, o in occ.items():
        o.isLightBulbOn = n in ALL
    m = adsk.core.Matrix3D.create()
    m.translation = adsk.core.Vector3D.create(0, 0, 6.0 * MM)
    occ["X4_front_frame"].transform = m
    shot("09_exploded_iso", V.IsoTopRightViewOrientation, ALL, 210)
    shot("10_exploded_back", V.IsoBottomLeftViewOrientation, ALL, 210)
    occ["X4_front_frame"].transform = adsk.core.Matrix3D.create()

    print("DONE shots")
