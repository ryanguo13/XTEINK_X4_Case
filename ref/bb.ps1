param([string]$img,[int]$thr=120)
Add-Type -AssemblyName System.Drawing
$b=[System.Drawing.Bitmap]::FromFile($img)
$w=$b.Width;$h=$b.Height
$minX=$w;$maxX=-1;$minY=$h;$maxY=-1
for($y=0;$y -lt $h;$y++){
  for($x=0;$x -lt $w;$x++){
    $p=$b.GetPixel($x,$y);$l=0.299*$p.R+0.587*$p.G+0.114*$p.B
    if($l -lt $thr){
      if($x -lt $minX){$minX=$x}; if($x -gt $maxX){$maxX=$x}
      if($y -lt $minY){$minY=$y}; if($y -gt $maxY){$maxY=$y}
    }
  }
}
Write-Output "$img BBOX x $minX..$maxX y $minY..$maxY w $($maxX-$minX+1) h $($maxY-$minY+1) ratio $([math]::Round(($maxY-$minY+1)/($maxX-$minX+1),4))"
$b.Dispose()
