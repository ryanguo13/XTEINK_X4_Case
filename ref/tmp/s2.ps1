Add-Type -AssemblyName System.Drawing
$f="C:\Users\jguo121\Documents\X4\ref\2025110509383389.jpg"
$img=[System.Drawing.Bitmap]::FromFile($f)
# 机身纵向暗带 y 400..453 (上表面亮), 逐列找最深/最亮以定位端口
for($x=880;$x -le 1120;$x+=4){
  $min=255;$max=0
  for($y=395;$y -le 455;$y++){
    $p=$img.GetPixel($x,$y); $l=($p.R+$p.G+$p.B)/3
    if($l -lt $min){$min=$l}
    if($l -gt $max){$max=$l}
  }
  Write-Output ("x={0} min={1} max={2}" -f $x,[int]$min,[int]$max)
}
