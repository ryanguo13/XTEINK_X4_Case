# -*- coding: utf-8 -*-
"""X4 外壳 —— 文档配图生成 (白底 + 描边, 草图/网格全部隐藏)

配方 (试了三种才定下来):
  工作空间 FusionRenderEnvironment + visualStyle = ShadedWithVisibleEdgesOnlyVisualStyle
  → 纯白背景、灰色实体、黑色轮廓线, 是技术文档最易读的观感, 且实时出图。

  对比过的另外两种:
  - FusionSolidEnvironment + 任意 visualStyle: 深色渐变底 + 满屏建模网格, 不可用。
  - renderManager.rendering.startLocalRender(): 真渲染, 有材质阴影, 但单张 ~300 s,
    9 张要 45 min, 且默认 3072x1276 宽幅会把竖立机身裁成一条。文档图不值这个成本。

API 坑 (都踩过):
  1. 视口那层斜向网格跟"草图网格显示"绑定, 只有切到 Render 工作空间才彻底干净。
  2. sceneSettings.backgroundType 只有 getter 没有 setter, 想改背景只能换
     backgroundEnvironment。
  3. camera.viewExtents 单位是厘米 (MM = 0.1), 传毫米会得到巨大空框。
  4. saveAsImageFile 前必须 vp.refresh() + adsk.doEvents() + 短 sleep,
     否则抓到的是上一帧。

用法:  python3 dev_run.py /mnt/c/Users/jguo121/Documents/X4/x4_render_docs.py
"""
import adsk.core, adsk.fusion, os, time

OUT = "C:/Users/jguo121/Documents/X4/docs/images"
MM = 0.1


def run(_context):
    app = adsk.core.Application.get()
    ui = app.userInterface
    dsn = adsk.fusion.Design.cast(app.activeProduct)
    root = dsn.rootComponent
    if not os.path.isdir(OUT):
        os.makedirs(OUT)

    # ---- 1. 切 Render 工作空间 (白底 + 无网格) ----
    ui.workspaces.itemById("FusionRenderEnvironment").activate()
    adsk.doEvents()
    time.sleep(1.2)

    # ---- 2. 隐藏辅助显示 ----
    for attr in ("isOriginFolderLightBulbOn", "isJointOriginsFolderLightBulbOn"):
        try:
            setattr(root, attr, False)
        except Exception:
            pass

    vp = app.activeViewport
    vp.visualStyle = adsk.core.VisualStyles.ShadedWithVisibleEdgesOnlyVisualStyle
    V = adsk.core.ViewOrientations

    occ = {}
    for i in range(root.occurrences.count):
        o = root.occurrences.item(i)
        occ[o.component.name] = o

    ALL = ["X4_back_shell", "X4_front_frame"]
    BK = ["X4_back_shell"]
    FR = ["X4_front_frame"]

    def shot(name, orient, show, extents_mm, up=None, center=None,
             w=1600, h=1200):
        for n, o in occ.items():
            o.isLightBulbOn = n in show
        # ★ 顺序必须是: 设 orientation → 赋值相机 → fit() → 再改 viewExtents。
        #   反过来（先 fit 再设 orientation）会被 fit 的 isFitView 状态吃掉，
        #   结果是所有图都退化成同一个等轴测视角。
        cam = vp.camera
        cam.viewOrientation = orient
        if center is not None:
            cam.target = adsk.core.Point3D.create(center[0] * MM, center[1] * MM,
                                                  center[2] * MM)
        vp.camera = cam
        vp.fit()
        cam = vp.camera
        cam.isFitView = False
        cam.isSmoothTransition = False
        cam.viewExtents = extents_mm * MM
        # upVector 只在正交视图里给; Iso* 视角若强行指定会失去本来的三个方向差异
        if up is not None:
            cam.upVector = adsk.core.Vector3D.create(*up)
        vp.camera = cam
        vp.refresh()
        adsk.doEvents()
        time.sleep(0.6)
        path = OUT + "/" + name + ".png"
        vp.saveAsImageFile(path, w, h)
        print("  %-26s %8d bytes" % (name, os.path.getsize(path)))

    # ---- 3. 主图 ----
    shot("01_hero_iso", V.IsoTopRightViewOrientation, ALL, 192)
    shot("02_iso_back", V.IsoBottomLeftViewOrientation, ALL, 192)
    # 正/背视图用竖版画幅: 机身是 73.3x136.3 的竖长方形, 横版画幅会在左右浪费大量白边。
    # viewExtents = 画幅宽度, 取 92 mm → 纵向 92*1400/900 = 143 mm, 裹住 136.3 mm 机身留 3 mm 边。
    shot("03_front", V.FrontViewOrientation, ALL, 96, up=(0, 1, 0), w=900, h=1400)
    shot("04_back", V.BackViewOrientation, ALL, 96, up=(0, 1, 0), w=900, h=1400)
    shot("05_back_shell_inside", V.IsoTopLeftViewOrientation, BK, 178)
    shot("06_back_shell_outside", V.IsoBottomRightViewOrientation, BK, 178)
    shot("07_front_frame_outside", V.IsoBottomRightViewOrientation, FR, 172)
    shot("08_front_frame_inside", V.IsoTopLeftViewOrientation, FR, 172)

    def shot_explicit(name, eye_mm, tgt_mm, show, extents_mm, up=(0, 0, 1),
                      w=1600, h=1200):
        """直接给眼点/靶点。侧边特写用这个: LeftView/RightView 配合自定义 upVector
        时相机会被 Fusion 重算成千奇百怪的斜视角, 不如自己算位置。"""
        for n, o in occ.items():
            o.isLightBulbOn = n in show
        cam = vp.camera
        cam.isFitView = False
        cam.isSmoothTransition = False
        # ★ Camera 上没有 isPerspective 属性 (写它会被 Python 当普通属性存起来,
        #   不报错但也不生效), 必须用 cameraType。透视相机下 viewExtents 会被
        #   忽略/钳位到 fit 值, 导致特写图跟全景一模一样。
        cam.cameraType = adsk.core.CameraTypes.OrthographicCameraType
        cam.eye = adsk.core.Point3D.create(eye_mm[0] * MM, eye_mm[1] * MM, eye_mm[2] * MM)
        cam.target = adsk.core.Point3D.create(tgt_mm[0] * MM, tgt_mm[1] * MM,
                                              tgt_mm[2] * MM)
        cam.upVector = adsk.core.Vector3D.create(*up)
        cam.viewExtents = extents_mm * MM
        vp.camera = cam
        vp.refresh()
        adsk.doEvents()
        time.sleep(0.6)
        path = OUT + "/" + name + ".png"
        vp.saveAsImageFile(path, w, h)
        print("  %-26s %8d bytes" % (name, os.path.getsize(path)))

    # ---- 4. 长边端口一览 (USB-C / LED / 挂绳孔), 从 -X 侧平视 ----
    # up=(0,0,1) 让机身长轴(Y)落在屏幕横轴上, 横向排开读起来才顺;
    # viewExtents = 画幅【宽度】, 纵向可见高度 = 宽度 * h/w。
    # 端口区 y 覆盖 -31..-53 共 22 mm; 取宽 26 → 纵向 8.1 mm, 刚好裹住 6 mm 厚度。
    shot_explicit("09_side_ports", (-160, -42, 3.0), (0, -42, 3.0), ALL, 30,
                  up=(0, 0, 1), w=1600, h=620)

    # ---- 5. 短边按键一览 (电源 / 翻页 / TF / RESET), 从 +X 侧平视 ----
    # 四个要素 y 覆盖 +34 .. -29 → 共 63 mm; 取宽 72 → 纵向 9.9 mm。
    shot_explicit("10_side_keys", (160, 2.5, 3.0), (0, 2.5, 3.0), ALL, 74,
                  up=(0, 0, 1), w=1600, h=460)

    # ---- 6. 爆炸图: 前框沿 +Z 抬起 8 mm ----
    m = adsk.core.Matrix3D.create()
    m.translation = adsk.core.Vector3D.create(0, 0, 8.0 * MM)
    occ["X4_front_frame"].transform = m
    shot("11_exploded_iso", V.IsoTopRightViewOrientation, ALL, 205)
    shot("12_exploded_back", V.IsoBottomLeftViewOrientation, ALL, 205)
    occ["X4_front_frame"].transform = adsk.core.Matrix3D.create()

    # ---- 7. 还原 ----
    for n, o in occ.items():
        o.isLightBulbOn = True
    print("DONE docs/images")
