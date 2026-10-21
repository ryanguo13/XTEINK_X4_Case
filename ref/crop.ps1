param([string]$img,[string]$out,[int]$x,[int]$y,[int]$w,[int]$h,[double]$scale=3)
Add-Type -AssemblyName System.Drawing
$b=[System.Drawing.Bitmap]::FromFile($img)
$rect=New-Object System.Drawing.Rectangle($x,$y,$w,$h)
$c=$b.Clone($rect,$b.PixelFormat)
$nw=[int]($w*$scale); $nh=[int]($h*$scale)
$o=New-Object System.Drawing.Bitmap($nw,$nh)
$g=[System.Drawing.Graphics]::FromImage($o)
$g.InterpolationMode=[System.Drawing.Drawing2D.InterpolationMode]::NearestNeighbor
$g.PixelOffsetMode=[System.Drawing.Drawing2D.PixelOffsetMode]::Half
$g.DrawImage($c,0,0,$nw,$nh)
$o.Save($out,[System.Drawing.Imaging.ImageFormat]::Png)
$g.Dispose();$o.Dispose();$c.Dispose();$b.Dispose()
Write-Output "saved $out ${nw}x${nh}"
