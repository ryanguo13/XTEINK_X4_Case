param(
  [string]$inDir = "C:\Users\jguo121\Documents\X4\docs\images",
  [string]$outDir = "C:\Users\jguo121\Documents\X4\docs\images_trim",
  [int]$pad = 40,
  [int]$thr = 246
)
Add-Type -AssemblyName System.Drawing
$files = Get-ChildItem -Path $inDir -Filter *.png
foreach ($f in $files) {
  $bmp = New-Object System.Drawing.Bitmap($f.FullName)
  $w = $bmp.Width; $h = $bmp.Height
  $minX = $w; $minY = $h; $maxX = -1; $maxY = -1
  # 每隔 2 px 采样足够找边界, 再回退到逐行/逐列精扫边缘条带
  for ($y = 0; $y -lt $h; $y += 2) {
    for ($x = 0; $x -lt $w; $x += 2) {
      $c = $bmp.GetPixel($x, $y)
      if ($c.R -lt $thr -or $c.G -lt $thr -or $c.B -lt $thr) {
        if ($x -lt $minX) { $minX = $x }
        if ($x -gt $maxX) { $maxX = $x }
        if ($y -lt $minY) { $minY = $y }
        if ($y -gt $maxY) { $maxY = $y }
      }
    }
  }
  if ($maxX -lt 0) { Write-Output ("SKIP(blank) " + $f.Name); $bmp.Dispose(); continue }
  $x0 = [Math]::Max(0, $minX - $pad)
  $y0 = [Math]::Max(0, $minY - $pad)
  $x1 = [Math]::Min($w - 1, $maxX + $pad)
  $y1 = [Math]::Min($h - 1, $maxY + $pad)
  $nw = $x1 - $x0 + 1; $nh = $y1 - $y0 + 1
  $rect = New-Object System.Drawing.Rectangle($x0, $y0, $nw, $nh)
  $dst = New-Object System.Drawing.Bitmap($nw, $nh)
  $g = [System.Drawing.Graphics]::FromImage($dst)
  $g.DrawImage($bmp, (New-Object System.Drawing.Rectangle(0, 0, $nw, $nh)), $rect, [System.Drawing.GraphicsUnit]::Pixel)
  $g.Dispose()
  $out = Join-Path $outDir $f.Name
  $dst.Save($out, [System.Drawing.Imaging.ImageFormat]::Png)
  $dst.Dispose(); $bmp.Dispose()
  Write-Output ("{0,-30} {1}x{2} -> {3}x{4}" -f $f.Name, $w, $h, $nw, $nh)
}
