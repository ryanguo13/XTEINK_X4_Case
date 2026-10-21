Add-Type -AssemblyName System.Drawing
$img=New-Object System.Drawing.Bitmap("C:\Users\jguo121\Documents\X4\ref\2025110509383389.jpg")
Write-Output ("size {0}x{1}" -f $img.Width,$img.Height)
# 端面暗带找 y 范围: 用 x=300 (无孔区) 扫列
$ys=@()
for($y=380;$y -le 480;$y++){
  $p=$img.GetPixel(300,$y); $l=($p.R+$p.G+$p.B)/3
  $ys += ,@($y,[int]$l)
}
$ys | ForEach-Object { Write-Output ("y={0} l={1}" -f $_[0],$_[1]) } | Select-Object -First 60
