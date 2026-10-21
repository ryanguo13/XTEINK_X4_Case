param([string]$img='C:\Users\jguo121\Documents\X4\ref\2025110509383389.jpg')
Add-Type -AssemblyName System.Drawing
$b=New-Object System.Drawing.Bitmap($img)
$w=$b.Width;$h=$b.Height
function Lum($x,$y){ $p=$b.GetPixel($x,$y); return 0.299*$p.R+0.587*$p.G+0.114*$p.B }
Write-Output ("size {0} x {1}" -f $w,$h)
# 1) body horizontal extent along the end-face band (y 400..430)
$minX=$w;$maxX=-1
for($x=0;$x -lt $w;$x++){
  $dark=0
  for($y=395;$y -le 445;$y++){ if((Lum $x $y) -lt 90){$dark++} }
  if($dark -ge 5){ if($x -lt $minX){$minX=$x}; if($x -gt $maxX){$maxX=$x} }
}
Write-Output ("body band x {0}..{1}  w={2}" -f $minX,$maxX,($maxX-$minX+1))
# 2) find very-dark blobs (holes) inside band: thr 30
$cols=@()
for($x=$minX;$x -le $maxX;$x++){
  $n=0;$y0=9999;$y1=-1
  for($y=395;$y -le 460;$y++){
    if((Lum $x $y) -lt 30){ $n++; if($y -lt $y0){$y0=$y}; if($y -gt $y1){$y1=$y} }
  }
  $cols += ,@($x,$n,$y0,$y1)
}
$cs=$null;$prev=-99;$out=@()
foreach($c in $cols){
  if($c[1] -lt 3){ if($cs -ne $null){$out += ,$cs; $cs=$null}; $prev=$c[0]; continue }
  if($cs -eq $null -or ($c[0]-$prev) -gt 8){
    if($cs -ne $null){$out += ,$cs}
    $cs=@($c[0],$c[0],9999,-1)
  }
  $cs[1]=$c[0]
  if($c[2] -lt $cs[2]){$cs[2]=$c[2]}
  if($c[3] -gt $cs[3]){$cs[3]=$c[3]}
  $prev=$c[0]
}
if($cs -ne $null){$out += ,$cs}
$mmpx = 69.0/($maxX-$minX+1)
Write-Output ("mm/px = {0}" -f [math]::Round($mmpx,5))
foreach($o in $out){
  $bw=$o[1]-$o[0]+1
  $cx=($o[0]+$o[1])/2.0
  $cy=($o[2]+$o[3])/2.0
  # x measured from band centre, +X = image right
  $dxmm = ($cx - ($minX+$maxX)/2.0)*$mmpx
  Write-Output ("blob x {0}..{1} w={2}px ({3}mm)  y {4}..{5} h={6}px  cx={7} cy={8}  dX={9}mm" -f $o[0],$o[1],$bw,[math]::Round($bw*$mmpx,2),$o[2],$o[3],($o[3]-$o[2]+1),[math]::Round($cx,1),[math]::Round($cy,1),[math]::Round($dxmm,2))
}
$b.Dispose()
