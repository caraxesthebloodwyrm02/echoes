# final_core_cleanup.ps1
# Irfan's one-shot cleanup for Echoes/core

$CoreDir = "core"
$Conflicts = @(
    # Python stdlib
    "typing", "collections", "functools", "traceback", "types", "logging", "http", "warnings", "string",
    "subprocess", "ast", "pathlib", "inspect", "dataclasses", "typing_extensions", "token", "html", "email",
    "_pytest", "mypy", "gettext", "docutils", "pprint", "numbers", "packaging", "anyio", "_ssl", "concurrent",
    "queue", "hmac", "pyarrow", "ctypes", "secrets", "array", "gzip", "plistlib", "resource", "statistics",
    "io", "_io", "_warnings",
    # Common 3rd party
    "annotated_types", "requests", "coverage"
)

Write-Host "Scanning $CoreDir for shadowing files..."

$Renamed = 0
foreach ($name in $Conflicts) {
    $old = Join-Path $CoreDir "$name.py"
    if (Test-Path $old) {
        $new = Join-Path $CoreDir "agent_$name.py"
        try {
            ren $old "agent_$name.py"
            Write-Host "Renamed $old -> $new"
            $Renamed++
        }
        catch {
            Write-Host "ERROR renaming $old : $_"
        }
    }
}

Write-Host "`nTotal files renamed: $Renamed"