param($f='C:\Users\jguo121\Documents\X4\ref\2025110509383025.jpg')
Add-Type -AssemblyName System.Drawing
$img=[System.Drawing.Bitmap]::FromFile($f)
function Lum($x,$y){ $p=$img.GetPixel($x,$y); return 0.299*$p.R+0.587*$p.G+0.114*$p.B }
Write-Output ("size {0}x{1}" -f $img.Width,$img.Height)
# per-column min luminance in the face band, printed compressed
for($x=0;$x -lt $img.Width;$x+=10){
  $mn=999; $mx=-1; $smn=999
  for($y=400;$y -le 470;$y++){ $v=Lum $x $y; if($v -lt $mn){$mn=$v}; if($v -gt $mx){$mx=$v}; }
  Write-Output ("{0,4} min={1,4:N0} max={2,4:N0}" -f $x,$mn,$mx)
}
$img.Dispose()
