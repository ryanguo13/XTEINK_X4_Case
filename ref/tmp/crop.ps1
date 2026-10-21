param([string]$img,[string]$out,[int]$x,[int]$y,[int]$w,[int]$h,[double]$s=2.0)
Add-Type -AssemblyName System.Drawing
$b=[System.Drawing.Bitmap]::FromFile($img)
$r=New-Object System.Drawing.Rectangle($x,$y,$w,$h)
$c=$b.Clone($r,$b.PixelFormat)
$nw=[int]($w*$s); $nh=[int]($h*$s)
$d=New-Object System.Drawing.Bitmap($nw,$nh)
$g=[System.Drawing.Graphics]::FromImage($d)
$g.InterpolationMode='NearestNeighbor'
$g.PixelOffsetMode='Half'
$g.DrawImage($c,0,0,$nw,$nh)
$d.Save($out,[System.Drawing.Imaging.ImageFormat]::Png)
Write-Output "$out $nw x $nh"
