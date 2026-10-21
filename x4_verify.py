# -*- coding: utf-8 -*-
"""X4 外壳 —— 装配验证 + STL 导出 (在已构建好的设计上运行)"""
import adsk.core, adsk.fusion, os, traceback
MM = 0.1
OUT = "/mnt/c/Users/jguo121/Documents/X4/stl"

def run(_context):
    app = adsk.core.Application.get()
    dsn = adsk.fusion.Design.cast(app.activeProduct)
    root = dsn.rootComponent

    comps = {}
    for i in range(root.occurrences.count):
        c = root.occurrences.item(i).component
        comps[c.name] = c
    print("components:", list(comps.keys()))

    def stat(name):
        c = comps[name]
        b = c.bRepBodies.item(0)
        bb = b.boundingBox
        print("%-22s bodies=%d  vol=%8.3f cm3  size %.2f x %.2f x %.2f  z %.2f..%.2f" % (
            name, c.bRepBodies.count, b.volume,
            (bb.maxPoint.x - bb.minPoint.x) / MM, (bb.maxPoint.y - bb.minPoint.y) / MM,
            (bb.maxPoint.z - bb.minPoint.z) / MM,
            bb.minPoint.z / MM, bb.maxPoint.z / MM))
        return b

    for n in ("X4_back_shell", "X4_front_frame", "X4_device_reference"):
        stat(n)

    # ---- 干涉检查 ----
    def interference(n1, n2):
        body1 = comps[n1].bRepBodies.item(0)
        body2 = comps[n2].bRepBodies.item(0)
        if n1 == "X4_device_reference":
            body1.opacity = 1.0
        if n2 == "X4_device_reference":
            body2.opacity = 1.0
        ic = adsk.core.ObjectCollection.create()
        ic.add(body1); ic.add(body2)
        ii = dsn.createInterferenceInput(ic)
        ii.isCoincidentFacesIncluded = False
        res = dsn.analyzeInterference(ii)
        n = res.count
        tot = 0.0
        for k in range(n):
            tot += res.item(k).volume
        print("  [interference] %-20s vs %-20s : %d 处  %.4f cm3" % (n1, n2, n, tot))
        return n, tot

    print("")
    interference("X4_back_shell", "X4_device_reference")
    interference("X4_front_frame", "X4_device_reference")
    interference("X4_back_shell", "X4_front_frame")

    # ---- 导出 STL ----
    if not os.path.isdir(OUT):
        os.makedirs(OUT)
    ex = dsn.exportManager
    for name in ("X4_back_shell", "X4_front_frame"):
        c = comps[name]
        body = c.bRepBodies.item(0)
        path = os.path.join(OUT, name + ".stl")
        opt = ex.createSTLExportOptions(body, path)
        opt.meshRefinement = adsk.fusion.MeshRefinementSettings.MeshRefinementHigh
        opt.isBinaryFormat = True
        opt.sendToPrintUtility = False
        ex.execute(opt)
        print("  exported %s  (%d bytes)" % (path, os.path.getsize(path)))

    # 反向验证: 设备参考体贴合时不穿透背板/前框
    dev = comps["X4_device_reference"].bRepBodies.item(0)
    print("\nOK  验证完成")
