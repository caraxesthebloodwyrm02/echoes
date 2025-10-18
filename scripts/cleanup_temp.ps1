$tempDir = 'E:\Projects\Development\.temp'
$ageThreshold = (Get-Date).AddHours(-24)  # Delete files older than 24 hours
Get-ChildItem -Path $tempDir -Recurse | Where-Object {
    $_.LastWriteTime -lt $ageThreshold -and
    -not (Get-FileLock -Path $_.FullName)  # Custom function to check if file is locked
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
