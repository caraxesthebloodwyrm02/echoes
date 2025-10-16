$logFile = "e:\Projects\Development\monitoring\performance.log"
$intervalSeconds = 300  # 5 minute intervals

function Write-PerformanceLog {
    param($message)
    $timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
    "$timestamp - $message" | Add-Content -Path $logFile
}

while ($true) {
    try {
        # Memory metrics
        $memory = Get-Counter '\Memory\Available MBytes' -ErrorAction Stop
        $memoryAvailable = $memory.CounterSamples[0].CookedValue

        # CPU metrics
        $cpu = Get-Counter '\Processor(_Total)\% Processor Time' -ErrorAction Stop
        $cpuUsage = $cpu.CounterSamples[0].CookedValue

        # Process specific metrics
        $codeiumProcess = Get-Process | Where-Object { $_.Name -like "*codeium*" } | Select-Object CPU, WorkingSet
        $windsurfProcess = Get-Process | Where-Object { $_.Name -like "*windsurf*" } | Select-Object CPU, WorkingSet

        # Log the metrics
        Write-PerformanceLog "Memory Available: $memoryAvailable MB"
        Write-PerformanceLog "CPU Usage: $cpuUsage%"
        if ($codeiumProcess) {
            Write-PerformanceLog "Codeium CPU: $($codeiumProcess.CPU) | Memory: $([math]::Round($codeiumProcess.WorkingSet/1MB, 2)) MB"
        }
        if ($windsurfProcess) {
            Write-PerformanceLog "Windsurf CPU: $($windsurfProcess.CPU) | Memory: $([math]::Round($windsurfProcess.WorkingSet/1MB, 2)) MB"
        }
    }
    catch {
        Write-PerformanceLog "Error collecting metrics: $_"
    }

    Start-Sleep -Seconds $intervalSeconds
}
