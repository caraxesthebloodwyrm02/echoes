# audit_echoes_core.ps1
# Comprehensive audit of echoes_core directory before deletion

$OutputFile = "echoes_core_audit_$(Get-Date -Format 'yyyyMMdd_HHmmss').txt"

function Write-Section {
    param($Title)
    $separator = "=" * 80
    Add-Content $OutputFile "`n$separator"
    Add-Content $OutputFile $Title
    Add-Content $OutputFile "$separator`n"
}

# Start audit
"ECHOES_CORE DIRECTORY AUDIT" | Out-File $OutputFile
"Generated: $(Get-Date)" | Add-Content $OutputFile
"Project Path: $PWD" | Add-Content $OutputFile

# 1. Check if echoes_core exists
Write-Section "1. DIRECTORY EXISTENCE CHECK"
if (Test-Path echoes_core) {
    "✅ echoes_core directory EXISTS" | Add-Content $OutputFile
} else {
    "❌ echoes_core directory NOT FOUND" | Add-Content $OutputFile
    "Checking for 'core' directory instead..." | Add-Content $OutputFile
    if (Test-Path core) {
        "✅ Found 'core' directory instead" | Add-Content $OutputFile
        $targetDir = "core"
    } else {
        "❌ Neither echoes_core nor core directory found. Exiting." | Add-Content $OutputFile
        Write-Host "Audit complete. See: $OutputFile"
        exit
    }
}

# Determine which directory to audit
$targetDir = if (Test-Path echoes_core) { "echoes_core" } else { "core" }
"Auditing directory: $targetDir" | Add-Content $OutputFile

# 2. List ALL Python files
Write-Section "2. ALL PYTHON FILES (sorted by size)"
try {
    Get-ChildItem $targetDir/*.py -ErrorAction Stop | 
        Select-Object Name, @{Name="Size(KB)";Expression={[math]::Round($_.Length/1KB, 2)}} | 
        Sort-Object "Size(KB)" -Descending | 
        Format-Table -AutoSize | 
        Out-String | 
        Add-Content $OutputFile
} catch {
    "Error listing files: $_" | Add-Content $OutputFile
}

# 3. Find potential CUSTOM code
Write-Section "3. FILES WITH POTENTIAL CUSTOM CODE"
"Searching for: class Echoes, class Assistant, OPENAI_API, API_KEY, FastAPI, @app., @router." | Add-Content $OutputFile
try {
    $customCode = Get-ChildItem $targetDir/*.py -ErrorAction Stop | 
        Select-String -Pattern "class Echoes|class Assistant|OPENAI_API|API_KEY|FastAPI|@app\.|@router\." -List
    
    if ($customCode) {
        $customCode | ForEach-Object {
            "`nFile: $($_.Path)" | Add-Content $OutputFile
            "Match: $($_.Line)" | Add-Content $OutputFile
        }
    } else {
        "❌ No custom code patterns found" | Add-Content $OutputFile
    }
} catch {
    "Error searching for custom code: $_" | Add-Content $OutputFile
}

# 4. Find library code patterns
Write-Section "4. FILES WITH LIBRARY CODE PATTERNS"
"Searching for: scipy, numpy internals, mathematical algorithms" | Add-Content $OutputFile
try {
    $libraryCode = Get-ChildItem $targetDir/*.py -ErrorAction Stop | 
        Select-String -Pattern "from scipy|import numpy|from numpy|_stats_py|distributions|_entropy|_continuous" -List
    
    if ($libraryCode) {
        $libraryCode | ForEach-Object {
            "File: $($_.Filename) - Contains library code" | Add-Content $OutputFile
        }
    } else {
        "✅ No obvious library code patterns found" | Add-Content $OutputFile
    }
} catch {
    "Error searching for library code: $_" | Add-Content $OutputFile
}

# 5. Check imports FROM echoes_core in the rest of the project
Write-Section "5. FILES THAT IMPORT FROM $targetDir"
try {
    $imports = Get-ChildItem -Recurse -Include *.py -Exclude $targetDir | 
        Select-String "from $targetDir|import $targetDir" | 
        Select-Object Path, LineNumber, Line
    
    if ($imports) {
        $imports | ForEach-Object {
            "`nFile: $($_.Path)" | Add-Content $OutputFile
            "Line $($_.LineNumber): $($_.Line)" | Add-Content $OutputFile
        }
    } else {
        "✅ No imports from $targetDir found in other files" | Add-Content $OutputFile
    }
} catch {
    "Error searching for imports: $_" | Add-Content $OutputFile
}

# 6. Find config/settings files
Write-Section "6. CONFIGURATION FILES"
try {
    $configFiles = Get-ChildItem $targetDir/*config*.py, $targetDir/*settings*.py, $targetDir/version.py -ErrorAction SilentlyContinue
    
    if ($configFiles) {
        $configFiles | ForEach-Object {
            "`nFile: $($_.Name)" | Add-Content $OutputFile
            "First 10 lines:" | Add-Content $OutputFile
            Get-Content $_.FullName -TotalCount 10 | Add-Content $OutputFile
        }
    } else {
        "❌ No configuration files found" | Add-Content $OutputFile
    }
} catch {
    "Error finding config files: $_" | Add-Content $OutputFile
}

# 7. Small files (likely custom code)
Write-Section "7. SMALL FILES (<5KB) - Likely Custom Code"
try {
    $smallFiles = Get-ChildItem $targetDir/*.py -ErrorAction Stop | 
        Where-Object {$_.Length -lt 5KB} | 
        Select-Object Name, @{Name="Size(KB)";Expression={[math]::Round($_.Length/1KB, 2)}}
    
    if ($smallFiles) {
        $smallFiles | Format-Table -AutoSize | Out-String | Add-Content $OutputFile
    } else {
        "No files smaller than 5KB found" | Add-Content $OutputFile
    }
} catch {
    "Error finding small files: $_" | Add-Content $OutputFile
}

# 8. Large files (likely library code)
Write-Section "8. LARGE FILES (>20KB) - Likely Library Code"
try {
    $largeFiles = Get-ChildItem $targetDir/*.py -ErrorAction Stop | 
        Where-Object {$_.Length -gt 20KB} | 
        Select-Object Name, @{Name="Size(KB)";Expression={[math]::Round($_.Length/1KB, 2)}}
    
    if ($largeFiles) {
        $largeFiles | Format-Table -AutoSize | Out-String | Add-Content $OutputFile
    } else {
        "No files larger than 20KB found" | Add-Content $OutputFile
    }
} catch {
    "Error finding large files: $_" | Add-Content $OutputFile
}

# 9. Files starting with underscore (private/internal modules)
Write-Section "9. PRIVATE MODULE FILES (starting with _)"
try {
    $privateFiles = Get-ChildItem $targetDir/_*.py -ErrorAction SilentlyContinue | 
        Select-Object Name
    
    if ($privateFiles) {
        $privateFiles | Format-Table -AutoSize | Out-String | Add-Content $OutputFile
        "These are typically internal library modules - safe to delete" | Add-Content $OutputFile
    } else {
        "No private module files found" | Add-Content $OutputFile
    }
} catch {
    "Error finding private modules: $_" | Add-Content $OutputFile
}

# 10. Sample content from suspicious files
Write-Section "10. SAMPLE CONTENT FROM KEY FILES"
$suspiciousFiles = @("distro.py", "agent_json.py", "_stats_py.py", "__init__.py", "version.py")
foreach ($file in $suspiciousFiles) {
    $filePath = Join-Path $targetDir $file
    if (Test-Path $filePath) {
        "`n--- Content from $file (first 20 lines) ---" | Add-Content $OutputFile
        Get-Content $filePath -TotalCount 20 -ErrorAction SilentlyContinue | Add-Content $OutputFile
    }
}

# Summary
Write-Section "11. SUMMARY & RECOMMENDATIONS"
$fileCount = (Get-ChildItem $targetDir/*.py -ErrorAction SilentlyContinue).Count
"Total Python files: $fileCount" | Add-Content $OutputFile
"`nNext steps:" | Add-Content $OutputFile
"1. Review this audit file" | Add-Content $OutputFile
"2. Share it for analysis" | Add-Content $OutputFile
"3. Identify files to keep (move to app/)" | Add-Content $OutputFile
"4. Safely delete the rest" | Add-Content $OutputFile

Write-Host "`n✅ Audit complete!" -ForegroundColor Green
Write-Host "📄 Output saved to: $OutputFile" -ForegroundColor Cyan
Write-Host "`nPlease share this file for analysis.`n" -ForegroundColor Yellow