Add-Type -AssemblyName System.Drawing
$img=[System.Drawing.Bitmap]::FromFile('C:\Users\jguo121\Documents\X4\ref\front.jpg')
function Lum($x,$y){ $p=$img.GetPixel($x,$y); return 0.299*$p.R+0.587*$p.G+0.114*$p.B }
# screen light region: lum>140 inside body. Find per-row light span
Write-Output "== light span per row =="
foreach($y in 145,150,155,160,170,180,300,500,600,620,630,640,650,660,670,680,690){
  $first=-1;$last=-1
  for($x=430;$x -lt 770;$x++){ if((Lum $x $y) -gt 140){ if($first -lt 0){$first=$x}; $last=$x } }
  Write-Output "row $y : light $first..$last"
}
Write-Output "== light span per col =="
foreach($x in 440,450,455,460,465,470,600,730,735,740,745,750,755,760){
  $first=-1;$last=-1
  for($y=125;$y -lt 700;$y++){ if((Lum $x $y) -gt 140){ if($first -lt 0){$first=$y}; $last=$y } }
  Write-Output "col $x : light $first..$last"
}
Write-Output "== bottom bezel: front keys outline detection rows 600-700, scan for mid-gray"
foreach($y in 640,650,655,660,665,670){
  $runs=@();$in=$false;$s=0
  for($x=430;$x -lt 770;$x++){ $v=(Lum $x $y); $d=($v -gt 18 -and $v -lt 70)
    if($d -and -not $in){$in=$true;$s=$x}
    if((-not $d) -and $in){$in=$false;$runs+="$s-$($x-1)"} }
  if($in){$runs+="$s-769"}
  Write-Output "row $y midruns: $($runs -join ' ')"
}
$img.Dispose()
