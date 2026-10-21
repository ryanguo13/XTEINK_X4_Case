param([string]$img,[int]$thr=120,[int]$x0=380,[int]$x1=1050,[string]$ys)
Add-Type -AssemblyName System.Drawing
$b=[System.Drawing.Bitmap]::FromFile($img)
foreach($y in $ys.Split(',')){
  $y=[int]$y
  $out=@();$prev=$null;$start=$x0
  for($x=$x0;$x -le $x1;$x++){
    $p=$b.GetPixel($x,$y);$l=0.299*$p.R+0.587*$p.G+0.114*$p.B
    $c = if($l -lt $thr){'D'}else{'L'}
    if($c -ne $prev){ if($prev -ne $null){$out+="$prev$start-$($x-1)"}; $prev=$c;$start=$x }
  }
  $out+="$prev$start-$x1"
  Write-Output "row $y : $($out -join ' ')"
}
$b.Dispose()
