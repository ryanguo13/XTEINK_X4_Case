Add-Type -AssemblyName System.Drawing
$img=[System.Drawing.Bitmap]::FromFile("C:\Users\jguo121\Documents\X4\ref\2025110509383025.jpg")
# 端面暗带 y 345..470 内, 统计每列"很暗"(<40)的像素数 → 洞
$vals=@()
for($x=0;$x -lt $img.Width;$x++){
  $c=0
  for($y=345;$y -le 475;$y++){
    $p=$img.GetPixel($x,$y); if((($p.R+$p.G+$p.B)/3) -lt 45){$c++}
  }
  $vals += ,@($x,$c)
}
# 打印聚簇
$run=$null
foreach($v in $vals){
  if($v[1] -ge 6){
    if($run -eq $null){$run=@($v[0],$v[0],0)}
    $run[1]=$v[0]; $run[2]=[Math]::Max($run[2],$v[1])
  } else {
    if($run -ne $null){ Write-Output ("hole x {0}..{1} w={2} maxdark={3}" -f $run[0],$run[1],($run[1]-$run[0]+1),$run[2]); $run=$null }
  }
}
Write-Output "--- vertical extents of each cluster ---"
foreach($r in @(@(200,500),@(560,720),@(740,900))){
  $y0=999;$y1=0
  for($x=$r[0];$x -le $r[1];$x++){
    for($y=330;$y -le 490;$y++){
      $p=$img.GetPixel($x,$y); if((($p.R+$p.G+$p.B)/3) -lt 45){ if($y -lt $y0){$y0=$y}; if($y -gt $y1){$y1=$y} }
    }
  }
  Write-Output ("x {0}..{1}  y {2}..{3}  h={4}" -f $r[0],$r[1],$y0,$y1,($y1-$y0+1))
}
