param($src='C:\Users\jguo121\Documents\X4\ref\2025110509383389.jpg',$x0=800,$y0=330,$w=300,$h=160,$sc=4,$out='C:\Users\jguo121\Documents\X4\ref\tmp\e3389.png')
Add-Type -AssemblyName System.Drawing
$img=[System.Drawing.Bitmap]::FromFile($src)
$rect=New-Object System.Drawing.Rectangle($x0,$y0,$w,$h)
$crop=$img.Clone($rect,$img.PixelFormat)
$big=New-Object System.Drawing.Bitmap([int]($w*$sc),[int]($h*$sc))
$g=[System.Drawing.Graphics]::FromImage($big)
$g.InterpolationMode=[System.Drawing.Drawing2D.InterpolationMode]::NearestNeighbor
$g.PixelOffsetMode=[System.Drawing.Drawing2D.PixelOffsetMode]::Half
$g.DrawImage($crop,0,0,$big.Width,$big.Height)
$big.Save($out,[System.Drawing.Imaging.ImageFormat]::Png)
Write-Output ("saved {0} {1}x{2}" -f $out,$big.Width,$big.Height)
$g.Dispose();$big.Dispose();$crop.Dispose();$img.Dispose()
