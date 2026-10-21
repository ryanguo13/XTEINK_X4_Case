Add-Type -AssemblyName System.Drawing
$img = [System.Drawing.Bitmap]::FromFile('C:\Users\jguo121\Documents\X4\ref\front.jpg')
$w=$img.Width; $h=$img.Height
function Col($x){
  $parts=@(); $start=-1
  for($y=0;$y -lt $h;$y++){
    $p=$img.GetPixel($x,$y); $lum=0.299*$p.R+0.587*$p.G+0.114*$p.B
    $dark = $lum -lt 120
    if($dark -and $start -lt 0){$start=$y}
    if((-not $dark) -and $start -ge 0){$parts += "$start-$($y-1)"; $start=-1}
  }
  if($start -ge 0){$parts += "$start-$($h-1)"}
  Write-Output "col $x : $($parts -join ' ')"
}
foreach($x in 445,470,520,600,700,745,760){ Col $x }
$img.Dispose()
