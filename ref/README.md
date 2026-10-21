# 参考照片与测量脚本 / Reference photos & measurement scripts

本目录保留设计溯源：设备尺寸是怎么从照片反推出来的。

## 照片

10 张实拍，分辨率 1199×800 / 1200×800。原始素材清单里另有 3 张是 418 字节的
XML 错误占位（无图像内容），已从仓库移除。

| 文件 | 内容 |
| --- | --- |
| `front.jpg` | 正视图（竖直摆放），机身与按键测量主依据 |
| `2025110509382065.jpg` | 放电子秤上（75.8 g） |
| `2025110509382118.jpg` | 右侧斜掠视角 |
| `2025110509382459.jpg` | 全长右侧面正交视角，+X 侧四孔依据 |
| `2025110509383025.jpg` | 左下角特写 |
| `2025110509383175.jpg` | 背视图（XTEINK logo） |
| `2025110509383191.jpg` | 正面底部放大 |
| `2025110509383357.jpg` | 侧视 |
| `2025110509383389.jpg` | 端口端斜视，−X 侧三孔依据 |
| `2025110509383469.jpg` | 3/4 角部视角（挂绳孔交叉确认） |
| `2025110509382539.jpg` | microSD 配件（无设备几何信息） |

## 测量脚本

全部是 **PowerShell + System.Drawing**（WSL 侧 python3 没有 PIL）。

| 脚本 | 作用 |
| --- | --- |
| `scan.ps1` / `scan2.ps1` | 通用扫描，`-mode bbox|rows|cols` |
| `bb.ps1` / `bb2.ps1` | 包围盒 + mm/px 换算（`-img -thr -xmax -ymax`） |
| `bbox.ps1` / `rows.ps1` / `colscan.ps1` | 行/列亮度剖面 |
| `crop.ps1` | 最近邻放大裁切（`-img -out -x -y -w -h -scale`） |
| `m1.ps1`–`m4.ps1`, `side.ps1` | 具体测量用例 |
| `tmp/` | 端面/暗跑段/blob 检测的进阶脚本（`cropend.ps1`、`blobs.ps1`、`ascii.ps1`、`prof.ps1`、`endface.ps1`、`trim.ps1` 等）及其输出 PNG |

### 两个必须知道的坑

1. **`Add-Type -AssemblyName System.Drawing` 必须写在 `param(...)` 之后**。
   放前面会让所有 `param()` 默认值报
   `The assignment expression is not valid. The input to an assignment operator must be an object that is able to accept assignments`。

2. **`[System.Drawing.Bitmap]` 依赖上面的 `Add-Type`**。漏了会报
   `Unable to find type [System.Drawing.Bitmap]`。

## 用法示例

```bash
# 机身包围盒（正视图，阈值 100）
powershell.exe -NoProfile -ExecutionPolicy Bypass \
  -File 'C:\Users\jguo121\Documents\X4\ref\bb2.ps1' -img front.jpg -thr 100

# 端部放大 4 倍
powershell.exe -NoProfile -ExecutionPolicy Bypass \
  -File 'C:\Users\jguo121\Documents\X4\ref\tmp\cropend.ps1' \
  -src 2025110509383389.jpg -x0 800 -y0 330 -w 300 -h 160 -sc 4 -out e3389.png
```

> 这些脚本产出的数字最终收敛成了 `x4_case_fusion.py` 里 `P` 字典中标 `(*)` 的项，
> 误差约 ±1 mm。量产前请用卡尺复核。
