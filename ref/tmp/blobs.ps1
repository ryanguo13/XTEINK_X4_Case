param($f='C:\Users\jguo121\Documents\X4\ref\2025110509383025.jpg',$thr=13,$y0=395,$y1=475)
Add-Type -AssemblyName System.Drawing
$img=[System.Drawing.Bitmap]::FromFile($f)
function Lum($x,$y){ $p=$img.GetPixel($x,$y); return 0.299*$p.R+0.587*$p.G+0.114*$p.B }
$cols=@()
for($x=120;$x -lt 1150;$x++){
  $mn=999
  for($y=$y0;$y -le $y1;$y++){ $v=Lum $x $y; if($v -lt $mn){$mn=$v} }
  $cols += ,@($x,$mn)
}
$run=$null
foreach($c in $cols){
  if($c[1] -lt $thr){
    if($run -eq $null){ $run=@($c[0],$c[0]) }
    $run[1]=$c[0]
  } else {
    if($run -ne $null){
      if(($run[1]-$run[0]) -ge 3){ Write-Output ("run x {0}..{1}  w={2}" -f $run[0],$run[1],($run[1]-$run[0]+1)) }
      $run=$null
    }
  }
}
if($run -ne $null){ Write-Output ("run x {0}..{1}  w={2}" -f $run[0],$run[1],($run[1]-$run[0]+1)) }
$img.Dispose()
