$tempDir = 'D:\SharedData\TempFiles'
$ageThreshold = (Get-Date).AddHours(-1)  # Delete files older than 1 hour

Get-ChildItem -Path $tempDir -Recurse | Where-Object {
    $_.LastWriteTime -lt $ageThreshold -and
    -not (Get-FileLock -Path $_.FullName)
} | Remove-Item -Force

function Get-FileLock {
    param([string]$Path)
    try {
        $file = [System.IO.File]::Open($Path, 'Open', 'Read', 'None')
        $file.Close()
        return $false
    } catch {
        return $true
    }
}
