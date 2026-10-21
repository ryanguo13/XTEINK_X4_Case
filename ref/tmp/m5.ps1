Add-Type -AssemblyName System.Drawing
$img=[System.Drawing.Bitmap]::FromFile('C:\Users\jguo121\Documents\X4\ref\2025110509383025.jpg')
function Lum($x,$y){ $p=$img.GetPixel($x,$y); return 0.299*$p.R+0.587*$p.G+0.114*$p.B }
Write-Output ("size {0}x{1}" -f $img.Width,$img.Height)
# histogram of luminance in band
$hist=@{}
for($y=395;$y -le 460;$y+=3){ for($x=120;$x -lt 1160;$x+=3){ $v=[int]((Lum $x $y)/10)*10; $hist[$v]=1+$hist[$v] } }
$hist.GetEnumerator() | Sort-Object Name | ForEach-Object { Write-Output ("lum>={0}: {1}" -f $_.Name,$_.Value) }
$img.Dispose()
