Add-Type -AssemblyName System.Drawing
$f="C:\Users\jguo121\Documents\X4\ref\2025110509383025.jpg"
$img=[System.Drawing.Bitmap]::FromFile($f)
# 端面暗带: 找 y 中心及各列最暗值
foreach($y in 400,415,430,445){
  Write-Output "=== row $y ==="
  $s=""
  for($x=200;$x -le 1000;$x+=5){
    $p=$img.GetPixel($x,$y); $l=($p.R+$p.G+$p.B)/3
    $ch = if($l -lt 60){'#'} elseif($l -lt 100){'+'} elseif($l -lt 150){'.'} else {' '}
    $s += $ch
  }
  Write-Output $s
}
