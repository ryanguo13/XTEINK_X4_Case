param([string]$img,[int]$thr=200,[string]$mode='bbox')
Add-Type -AssemblyName System.Drawing
$b=[System.Drawing.Bitmap]::FromFile($img)
$w=$b.Width;$h=$b.Height
function Lum($p){ return 0.299*$p.R+0.587*$p.G+0.114*$p.B }
# bbox of pixels darker than thr
$minX=$w;$maxX=-1;$minY=$h;$maxY=-1
for($y=0;$y -lt $h;$y++){
  for($x=0;$x -lt $w;$x++){
    if((Lum $b.GetPixel($x,$y)) -lt $thr){
      if($x -lt $minX){$minX=$x}; if($x -gt $maxX){$maxX=$x}
      if($y -lt $minY){$minY=$y}; if($y -gt $maxY){$maxY=$y}
    }
  }
}
Write-Output "BBOX x $minX..$maxX  y $minY..$maxY  w $($maxX-$minX+1) h $($maxY-$minY+1)"
if($mode -eq 'rows'){
  foreach($y in $args){
    $out=@();$prev=$null;$start=0
    for($x=0;$x -lt $w;$x++){
      $c = if((Lum $b.GetPixel($x,$y)) -lt $thr){'D'}else{'L'}
      if($c -ne $prev){ if($prev -ne $null){$out+="$prev$start-$($x-1)"}; $prev=$c;$start=$x }
    }
    $out+="$prev$start-$($w-1)"
    Write-Output "row $y : $($out -join ' ')"
  }
}
if($mode -eq 'cols'){
  foreach($x in $args){
    $out=@();$prev=$null;$start=0
    for($y=0;$y -lt $h;$y++){
      $c = if((Lum $b.GetPixel($x,$y)) -lt $thr){'D'}else{'L'}
      if($c -ne $prev){ if($prev -ne $null){$out+="$prev$start-$($y-1)"}; $prev=$c;$start=$y }
    }
    $out+="$prev$start-$($h-1)"
    Write-Output "col $x : $($out -join ' ')"
  }
}
$b.Dispose()
