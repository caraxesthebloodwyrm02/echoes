# 1️⃣ Read the file in one string
$content = Get-Content .pre-commit-config.yaml -Raw

# 2️⃣ Add the --- header if missing
if ($content -notmatch "^\-\-\-") {
    $content = "---`n" + $content
}

# 3️⃣ Convert every CRLF → LF
$lfContent = $content -replace "`r`n", "`n"

# 4️⃣ Strip any trailing whitespace on each line
$lfContent = $lfContent -replace "[ \t]+$",""

# 5️⃣ Write the file back – **no CRLF added**
[IO.File]::WriteAllText('.pre-commit-config.yaml',
                        $lfContent,
                        [Text.Encoding]::UTF8)
