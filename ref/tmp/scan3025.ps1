Add-Type -AssemblyName System.Drawing
$img=[System.Drawing.Bitmap]::FromFile("C:\Users\jguo121\Documents\X4\ref\2025110509383025.jpg")
Write-Output ("size {0}x{1}" -f $img.Width,$img.Height)
for($y=280;$y -le 470;$y+=10){
  $c=0
  for($x=200;$x -le 900;$x+=4){
    $p=$img.GetPixel($x,$y); $l=($p.R+$p.G+$p.B)/3
    if($l -lt 110){$c++}
  }
  Write-Output ("y={0} dark={1}" -f $y,$c)
}
