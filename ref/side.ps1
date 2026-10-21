param([int]$thr=100)
Add-Type -AssemblyName System.Drawing
$b=[System.Drawing.Bitmap]::FromFile('C:\Users\jguo121\Documents\X4\ref\2025110509382459.jpg')
$w=$b.Width;$h=$b.Height
function Lum($x,$y){ $p=$b.GetPixel($x,$y); return 0.299*$p.R+0.587*$p.G+0.114*$p.B }
Write-Output "size $w x $h"
# body silhouette: dark pixels
$minX=$w;$maxX=-1;$minY=$h;$maxY=-1
for($y=0;$y -lt $h;$y++){ for($x=0;$x -lt $w;$x++){ if((Lum $x $y) -lt 90){ if($x -lt $minX){$minX=$x}; if($x -gt $maxX){$maxX=$x}; if($y -lt $minY){$minY=$y}; if($y -gt $maxY){$maxY=$y} } } }
Write-Output "bbox x $minX..$maxX y $minY..$maxY"
# find the side face band rows, then scan for light (recessed) features inside it
foreach($y in 395,400,405,410,415,420,425,430){
  $runs=@();$in=$false;$s=0
  for($x=0;$x -lt $w;$x++){ $v=(Lum $x $y); $isFeat=($v -gt 60)
    if($isFeat -and -not $in){$in=$true;$s=$x}
    if((-not $isFeat) -and $in){$in=$false;$runs+="$s-$($x-1)"} }
  if($in){$runs+="$s-$($w-1)"}
  Write-Output "row $y brightruns: $($runs -join ' ')"
}
$b.Dispose()
