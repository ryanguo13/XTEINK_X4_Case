param([string]$img,[int]$thr=120,[int]$xmax=1050,[int]$ymax=700)
Add-Type -AssemblyName System.Drawing
$b=[System.Drawing.Bitmap]::FromFile($img)
$w=[math]::Min($b.Width,$xmax);$h=[math]::Min($b.Height,$ymax)
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
$W=$maxX-$minX+1; $H=$maxY-$minY+1
Write-Output "$([System.IO.Path]::GetFileName($img)) x $minX..$maxX y $minY..$maxY w $W h $H  H/W=$([math]::Round($H/$W,4))  mm/px_vert=$([math]::Round(114.0/$H,5)) mm/px_horiz=$([math]::Round(69.0/$W,5))"
$b.Dispose()
