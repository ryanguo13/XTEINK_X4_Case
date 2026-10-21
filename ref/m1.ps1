Add-Type -AssemblyName System.Drawing
$img=[System.Drawing.Bitmap]::FromFile('C:\Users\jguo121\Documents\X4\ref\2025110509383191.jpg')
$w=$img.Width;$h=$img.Height
Write-Output "size $w x $h"
# horizontal scan lines: report runs of light(>150) and mid, and dark(<80)
function RowL($y){
  $out=@();$prev=$null;$start=0
  for($x=0;$x -lt $w;$x++){
    $p=$img.GetPixel($x,$y);$lum=0.299*$p.R+0.587*$p.G+0.114*$p.B
    $c = if($lum -gt 150){'L'} elseif($lum -gt 60){'M'} else {'D'}
    if($c -ne $prev){ if($prev -ne $null){$out+="$prev$start-$($x-1)"}; $prev=$c;$start=$x }
  }
  $out+="$prev$start-$($w-1)"
  Write-Output "row $y : $($out -join ' ')"
}
foreach($y in 20,60,120,200,270,300,340,400,450,470,485,500,520,545,560,575,600){ RowL $y }
function ColL($x){
  $out=@();$prev=$null;$start=0
  for($y=0;$y -lt $h;$y++){
    $p=$img.GetPixel($x,$y);$lum=0.299*$p.R+0.587*$p.G+0.114*$p.B
    $c = if($lum -gt 150){'L'} elseif($lum -gt 60){'M'} else {'D'}
    if($c -ne $prev){ if($prev -ne $null){$out+="$prev$start-$($y-1)"}; $prev=$c;$start=$y }
  }
  $out+="$prev$start-$($h-1)"
  Write-Output "col $x : $($out -join ' ')"
}
foreach($x in 90,150,300,420,470,600,700,900,1000,1100,1130){ ColL $x }
$img.Dispose()
