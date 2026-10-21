Add-Type -AssemblyName System.Drawing
$img=New-Object System.Drawing.Bitmap("C:\Users\jguo121\Documents\X4\ref\2025110509383389.jpg")
# 3389: 端面暗带. 先定暗带上下边界 (取 x=250 无孔列)
$dark=@()
for($x=140;$x -le 1100;$x++){
  $n=0
  for($y=395;$y -le 470;$y++){
    $p=$img.GetPixel($x,$y); if((($p.R+$p.G+$p.B)/3) -lt 45){$n++}
  }
  $dark += ,@($x,$n)
}
# 打印列剖面, 找出暗度接近 0 的区段 (即"洞")
$s=""
foreach($d in $dark){
  if($d[0] % 10 -eq 0){
    $s += if($d[1] -le 5){'.'} elseif($d[1] -le 40){'+'} else {'#'}
  }
}
Write-Output "profile(x step10, y395-470, thr45):"
Write-Output $s
