# secure_shoebox.ps1
# Script to secure .shoebox directory structure

# Configuration
$basePath = "$PSScriptRoot\.shoebox"
$adminGroup = [System.Security.Principal.NTAccount]("BUILTIN\Administrators")
$systemAccount = [System.Security.Principal.NTAccount]("NT AUTHORITY\SYSTEM")
$currentUser = [System.Security.Principal.WindowsIdentity]::GetCurrent().Name

# Create directories if they don't exist
$directories = @('cache', 'backup', 'config', 'logs')
foreach ($dir in $directories) {
    $fullPath = Join-Path -Path $basePath -ChildPath $dir
    if (-not (Test-Path $fullPath)) {
        New-Item -ItemType Directory -Path $fullPath -Force | Out-Null
        Write-Host "Created directory: $fullPath"
    } else {
        Write-Host "Directory exists: $fullPath"
    }
}

# Function to set permissions
function Set-SecurePermissions {
    param (
        [string]$path,
        [string]$description
    )
    
    Write-Host "Securing: $path - $description"
    
    try {
        $acl = Get-Acl -Path $path
        
        # Disable inheritance and remove all existing rules
        $acl.SetAccessRuleProtection($true, $false)
        $acl.Access | ForEach-Object { $acl.RemoveAccessRule($_) | Out-Null }
        
        # Add admin full control
        $rule = New-Object System.Security.AccessControl.FileSystemAccessRule(
            $adminGroup,
            'FullControl',
            'ContainerInherit,ObjectInherit',
            'None',
            'Allow'
        )
        $acl.AddAccessRule($rule)
        
        # Add SYSTEM full control
        $rule = New-Object System.Security.AccessControl.FileSystemAccessRule(
            $systemAccount,
            'FullControl',
            'ContainerInherit,ObjectInherit',
            'None',
            'Allow'
        )
        $acl.AddAccessRule($rule)
        
        # Apply the ACL
        Set-Acl -Path $path -AclObject $acl -ErrorAction Stop
        
        # Hide the directory
        (Get-Item $path).Attributes = 'Hidden'
        
        return $true
    }
    catch {
        Write-Error "Failed to secure $path : $_"
        return $false
    }
}

# Secure each directory
$results = @{}
foreach ($dir in $directories) {
    $fullPath = Join-Path -Path $basePath -ChildPath $dir
    $results[$dir] = Set-SecurePermissions -path $fullPath -description $dir
}

# Create a security report
$report = @"
Shoebox Security Configuration Report
==================================
Date: $(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')
User: $currentUser

Directory Permissions:
"@

foreach ($dir in $directories) {
    $fullPath = Join-Path -Path $basePath -ChildPath $dir
    $status = if ($results[$dir]) { 'SECURED' } else { 'FAILED' }
    $report += "`n- $dir : $status"
    
    try {
        $acl = Get-Acl -Path $fullPath
        $report += "`n  Owner: $($acl.Owner)"
        $report += "`n  Permissions:"
        $acl.Access | ForEach-Object {
            $report += "`n    - $($_.IdentityReference) : $($_.FileSystemRights) ($($_.AccessControlType))"
        }
    }
    catch {
        $report += "`n  [ERROR: Could not retrieve permissions]"
    }
}

# Save the report
$reportPath = Join-Path -Path $basePath -ChildPath "security_report_$(Get-Date -Format 'yyyyMMdd_HHmmss').txt"
$report | Out-File -FilePath $reportPath -Encoding utf8

Write-Host "`nSecurity configuration complete. Report saved to: $reportPath"
Write-Host "Please review the report and verify all settings are as expected.`n"

# Display a summary
$successCount = ($results.Values | Where-Object { $_ -eq $true }).Count
$totalCount = $results.Count
Write-Host "Summary: $successCount of $totalCount directories secured successfully"

# Return success only if all directories were secured
if ($successCount -eq $totalCount) {
    exit 0
} else {
    exit 1
}
