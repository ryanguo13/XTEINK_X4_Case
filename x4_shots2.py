# -*- coding: utf-8 -*-
"""侧视图修正: 不用 viewExtents 强制, 只 fit"""
import adsk.core, adsk.fusion, os, time
OUT = "C:/Users/jguo121/Documents/X4/shots"

def run(_context):
    app = adsk.core.Application.get()
    dsn = adsk.fusion.Design.cast(app.activeProduct)
    root = dsn.rootComponent
    occ = {root.occurrences.item(i).component.name: root.occurrences.item(i)
           for i in range(root.occurrences.count)}
    for o in occ.values():
        o.isLightBulbOn = True
    vp = app.activeViewport
    V = adsk.core.ViewOrientations

    def shot(name, orient):
        cam = vp.camera
        cam.isFitView = True
        cam.viewOrientation = orient
        vp.camera = cam
        vp.fit()
        vp.refresh(); adsk.doEvents(); time.sleep(0.4)
        p = OUT + "/" + name + ".png"
        vp.saveAsImageFile(p, 1600, 1200)
        print("  %-24s %8d" % (name, os.path.getsize(p)))

    shot("05_right_side", V.RightViewOrientation)
    shot("06_left_side", V.LeftViewOrientation)
    shot("11_top_edge", V.TopViewOrientation)
    shot("12_bottom_edge", V.BottomViewOrientation)
    print("DONE")
