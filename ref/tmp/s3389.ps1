Add-Type -AssemblyName System.Drawing
$f="C:\Users\jguo121\Documents\X4\ref\2025110509383389.jpg"
$img=[System.Drawing.Bitmap]::FromFile($f)
Write-Output ("size {0}x{1}" -f $img.Width,$img.Height)
# 1) 找暗带行范围 (x 300..500 采样)
for($y=300;$y -le 480;$y+=5){
  $c=0
  for($x=250;$x -le 550;$x+=5){
    $p=$img.GetPixel($x,$y); if((($p.R+$p.G+$p.B)/3) -lt 130){$c++}
  }
  Write-Output ("row y={0} dark={1}" -f $y,$c)
}
