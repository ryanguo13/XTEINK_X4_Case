Add-Type -AssemblyName System.Drawing
$img=[System.Drawing.Bitmap]::FromFile('C:\Users\jguo121\Documents\X4\ref\front.jpg')
function Lum($x,$y){ $p=$img.GetPixel($x,$y); return 0.299*$p.R+0.587*$p.G+0.114*$p.B }
Write-Output "== right edge profile: max dark x per row (y=130..700) =="
$prevMax=-1
for($y=130;$y -le 700;$y++){
  $max=-1
  for($x=740;$x -lt 800;$x++){ if((Lum $x $y) -lt 100){ $max=$x } }
  if($max -ne $prevMax){ Write-Output "y=$y maxdark=$max"; $prevMax=$max }
}
$img.Dispose()
