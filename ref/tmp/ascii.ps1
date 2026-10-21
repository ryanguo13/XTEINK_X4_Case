param($f='C:\Users\jguo121\Documents\X4\ref\2025110509383025.jpg',$x0=100,$x1=1160,$y0=390,$y1=480,$sx=8,$sy=4)
Add-Type -AssemblyName System.Drawing
$img=[System.Drawing.Bitmap]::FromFile($f)
function Lum($x,$y){ $p=$img.GetPixel($x,$y); return 0.299*$p.R+0.587*$p.G+0.114*$p.B }
$scale='@#%*+=-:. '
for($y=$y0;$y -le $y1;$y+=$sy){
  $line=""
  for($x=$x0;$x -le $x1;$x+=$sx){
    $v=Lum $x $y
    $i=[int]([math]::Floor($v/256.0*10)); if($i -gt 9){$i=9}
    $line += $scale[$i]
  }
  Write-Output ("{0,4} {1}" -f $y,$line)
}
Write-Output ("     x from {0} step {1}" -f $x0,$sx)
$img.Dispose()
