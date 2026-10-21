Add-Type -AssemblyName System.Drawing
$img=New-Object System.Drawing.Bitmap("C:\Users\jguo121\Documents\X4\ref\2025110509383025.jpg")
# 端面上三个"极黑"洞口: 阈值 25, 扫描 y 380..500
$cols=@()
for($x=150;$x -le 1000;$x++){
  $n=0;$y0=9999;$y1=-1
  for($y=380;$y -le 500;$y++){
    $p=$img.GetPixel($x,$y)
    if((($p.R+$p.G+$p.B)/3) -lt 25){ $n++; if($y -lt $y0){$y0=$y}; if($y -gt $y1){$y1=$y} }
  }
  if($n -ge 3){ $cols += ,@($x,$n,$y0,$y1) }
}
# 聚簇
$cs=$null;$prev=-9;$out=@()
foreach($c in $cols){
  if($c[0] - $prev -gt 6){
    if($cs -ne $null){$out += ,$cs}
    $cs=@($c[0],$c[0],9999,-1)
  }
  $cs[1]=$c[0]
  if($c[2] -lt $cs[2]){$cs[2]=$c[2]}
  if($c[3] -gt $cs[3]){$cs[3]=$c[3]}
  $prev=$c[0]
}
if($cs -ne $null){$out += ,$cs}
foreach($o in $out){
  Write-Output ("blob x {0}..{1} (w {2})  y {3}..{4} (h {5})  cx {6}" -f $o[0],$o[1],($o[1]-$o[0]+1),$o[2],$o[3],($o[3]-$o[2]+1),([int](($o[0]+$o[1])/2)))
}
