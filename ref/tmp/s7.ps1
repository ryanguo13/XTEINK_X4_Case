Add-Type -AssemblyName System.Drawing
$img=New-Object System.Drawing.Bitmap("C:\Users\jguo121\Documents\X4\ref\2025110509383025.jpg")
# 在 x=880 (靠右侧, 无孔) 找暗带的上下边界, 用于求 px/mm
Write-Output "--- column x=880 ---"
for($y=340;$y -le 520;$y+=2){
  $p=$img.GetPixel(880,$y); Write-Output ("y={0} l={1}" -f $y,[int](($p.R+$p.G+$p.B)/3))
}
