param([string]$img,[string]$out,[int]$x0,[int]$y0,[int]$w,[int]$h,[double]$s=2.0)
Add-Type -AssemblyName System.Drawing
$b=New-Object System.Drawing.Bitmap($img)
$r=New-Object System.Drawing.Rectangle($x0,$y0,$w,$h)
$c=$b.Clone($r,$b.PixelFormat)
$nw=[int]($w*$s); $nh=[int]($h*$s)
$d=New-Object System.Drawing.Bitmap($nw,$nh)
$g=[System.Drawing.Graphics]::FromImage($d)
$g.InterpolationMode='NearestNeighbor'
$g.DrawImage($c,0,0,$nw,$nh)
$d.Save($out,[System.Drawing.Imaging.ImageFormat]::Png)
Write-Output ("ok {0} {1}x{2}" -f $out,$nw,$nh)
