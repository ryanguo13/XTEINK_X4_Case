Add-Type -AssemblyName System.Drawing
$img=[System.Drawing.Bitmap]::FromFile('C:\Users\jguo121\Documents\X4\ref\front.jpg')
$w=$img.Width;$h=$img.Height
function Lum($x,$y){ $p=$img.GetPixel($x,$y); return 0.299*$p.R+0.587*$p.G+0.114*$p.B }
# 1) vertical extent of body at several columns (dark<100)
Write-Output "== body vertical extent (col, firstDark, lastDark) =="
foreach($x in 433,440,500,600,700,745,752,760,766,770,774){
  $first=-1;$last=-1
  for($y=0;$y -lt $h;$y++){ if((Lum $x $y) -lt 100){ if($first -lt 0){$first=$y}; $last=$y } }
  Write-Output "col $x : $first .. $last"
}
Write-Output "== body horizontal extent at rows =="
foreach($y in 140,200,300,400,500,600,620,700,710,720){
  $first=-1;$last=-1
  for($x=380;$x -lt 860;$x++){ if((Lum $x $y) -lt 100){ if($first -lt 0){$first=$x}; $last=$x } }
  Write-Output "row $y : $first .. $last"
}
Write-Output "== rows 615..705 runs (dark<95) =="
foreach($y in 615,625,635,645,655,660,665,670,675,680,685,690,695){
  $runs=@();$in=$false;$s=0
  for($x=400;$x -lt 800;$x++){ $d=(Lum $x $y) -lt 95
    if($d -and -not $in){$in=$true;$s=$x}
    if((-not $d) -and $in){$in=$false;$runs+="$s-$($x-1)"} }
  if($in){$runs+="$s-799"}
  Write-Output "row $y : $($runs -join ' ')"
}
$img.Dispose()
