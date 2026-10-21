Add-Type -AssemblyName System.Drawing
$img = [System.Drawing.Bitmap]::FromFile('C:\Users\jguo121\Documents\X4\ref\front.jpg')
$w=$img.Width; $h=$img.Height
$minX=$w; $maxX=0; $minY=$h; $maxY=0
for($y=0;$y -lt $h;$y+=1){
  for($x=0;$x -lt $w;$x+=1){
    $p=$img.GetPixel($x,$y)
    $lum=0.299*$p.R+0.587*$p.G+0.114*$p.B
    if($lum -lt 110){
      if($x -lt $minX){$minX=$x}
      if($x -gt $maxX){$maxX=$x}
      if($y -lt $minY){$minY=$y}
      if($y -gt $maxY){$maxY=$y}
    }
  }
}
Write-Output "bbox $minX $minY $maxX $maxY"
$img.Dispose()
