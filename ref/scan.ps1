Add-Type -AssemblyName System.Drawing
$img = [System.Drawing.Bitmap]::FromFile('C:\Users\jguo121\Documents\X4\ref\front.jpg')
$w=$img.Width; $h=$img.Height
function Row($y){
  $parts=@(); $start=-1
  for($x=0;$x -lt $w;$x++){
    $p=$img.GetPixel($x,$y); $lum=0.299*$p.R+0.587*$p.G+0.114*$p.B
    $dark = $lum -lt 110
    if($dark -and $start -lt 0){$start=$x}
    if((-not $dark) -and $start -ge 0){$parts += "$start-$($x-1)"; $start=-1}
  }
  if($start -ge 0){$parts += "$start-$($w-1)"}
  Write-Output "row $y : $($parts -join ' ')"
}
foreach($y in 150,200,300,400,500,600,700,730,745,755,765,775,785){ Row $y }
$img.Dispose()
