# MIT License
#
# Copyright (c) 2024 Echoes Project
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

# MIT License
# Copyright (c) 2025 Echoes Project

"""
System Monitoring with psutil
Background monitoring for CPU, memory, disk, network, processes
"""

import logging
import threading
import time
from dataclasses import dataclass
from datetime import datetime
from typing import Dict, List, Optional

import psutil

logger = logging.getLogger(__name__)


@dataclass
class SystemMetrics:
    """System metrics snapshot"""

    timestamp: datetime
    cpu_percent: float
    memory_percent: float
    memory_used_gb: float
    memory_total_gb: float
    disk_usage_percent: float
    disk_used_gb: float
    disk_total_gb: float
    network_sent_mb: float
    network_recv_mb: float
    process_count: int
    thread_count: int


class SystemMonitor:
    """
    Background system monitoring using psutil

    Features:
    - CPU usage tracking
    - Memory monitoring
    - Disk I/O statistics
    - Network statistics
    - Process monitoring
    - Thread-safe background monitoring
    """

    def __init__(self, interval_seconds: int = 60):
        self.interval_seconds = interval_seconds
        self.logger = logging.getLogger(__name__)
        self._monitoring = False
        self._monitor_thread: Optional[threading.Thread] = None
        self._metrics_history: List[SystemMetrics] = []
        self._max_history = 1000
        self._lock = threading.Lock()

    def start(self):
        """Start background monitoring"""
        if self._monitoring:
            self.logger.warning("Monitoring already started")
            return

        self._monitoring = True
        self._monitor_thread = threading.Thread(
            target=self._monitor_loop, daemon=True, name="SystemMonitor"
        )
        self._monitor_thread.start()
        self.logger.info(
            f"System monitoring started (interval: {self.interval_seconds}s)"
        )

    def stop(self):
        """Stop background monitoring"""
        self._monitoring = False
        if self._monitor_thread:
            self._monitor_thread.join(timeout=5)
        self.logger.info("System monitoring stopped")

    def _monitor_loop(self):
        """Background monitoring loop"""
        while self._monitoring:
            try:
                metrics = self._collect_metrics()

                with self._lock:
                    self._metrics_history.append(metrics)
                    # Keep only last N metrics
                    if len(self._metrics_history) > self._max_history:
                        self._metrics_history.pop(0)

                self.logger.debug(
                    f"Metrics: CPU={metrics.cpu_percent:.1f}% "
                    f"MEM={metrics.memory_percent:.1f}% "
                    f"DISK={metrics.disk_usage_percent:.1f}%"
                )

            except Exception as e:
                self.logger.error(f"Error collecting metrics: {e}")

            time.sleep(self.interval_seconds)

    def _collect_metrics(self) -> SystemMetrics:
        """Collect current system metrics"""
        # CPU
        cpu_percent = psutil.cpu_percent(interval=1)

        # Memory
        mem = psutil.virtual_memory()
        memory_percent = mem.percent
        memory_used_gb = mem.used / (1024**3)
        memory_total_gb = mem.total / (1024**3)

        # Disk
        disk = psutil.disk_usage("/")
        disk_usage_percent = disk.percent
        disk_used_gb = disk.used / (1024**3)
        disk_total_gb = disk.total / (1024**3)

        # Network
        net = psutil.net_io_counters()
        network_sent_mb = net.bytes_sent / (1024**2)
        network_recv_mb = net.bytes_recv / (1024**2)

        # Processes
        process_count = len(psutil.pids())

        # Threads
        thread_count = sum(
            p.num_threads()
            for p in psutil.process_iter(["num_threads"])
            if p.info["num_threads"]
        )

        return SystemMetrics(
            timestamp=datetime.now(),
            cpu_percent=cpu_percent,
            memory_percent=memory_percent,
            memory_used_gb=memory_used_gb,
            memory_total_gb=memory_total_gb,
            disk_usage_percent=disk_usage_percent,
            disk_used_gb=disk_used_gb,
            disk_total_gb=disk_total_gb,
            network_sent_mb=network_sent_mb,
            network_recv_mb=network_recv_mb,
            process_count=process_count,
            thread_count=thread_count,
        )

    def get_latest_metrics(self) -> Optional[SystemMetrics]:
        """Get latest metrics snapshot"""
        with self._lock:
            return self._metrics_history[-1] if self._metrics_history else None

    def get_metrics_history(self, count: int = 10) -> List[SystemMetrics]:
        """Get recent metrics history"""
        with self._lock:
            return self._metrics_history[-count:]

    def get_process_info(self, pid: Optional[int] = None) -> Dict:
        """Get detailed process information"""
        try:
            proc = psutil.Process(pid) if pid else psutil.Process()

            return {
                "pid": proc.pid,
                "name": proc.name(),
                "status": proc.status(),
                "cpu_percent": proc.cpu_percent(interval=0.1),
                "memory_percent": proc.memory_percent(),
                "memory_info": proc.memory_info()._asdict(),
                "num_threads": proc.num_threads(),
                "create_time": datetime.fromtimestamp(proc.create_time()),
            }
        except Exception as e:
            self.logger.error(f"Error getting process info: {e}")
            return {}

    def list_processes(self, filter_name: Optional[str] = None) -> List[Dict]:
        """List all processes or filter by name"""
        processes = []

        for proc in psutil.process_iter(
            ["pid", "name", "cpu_percent", "memory_percent"]
        ):
            try:
                info = proc.info
                if filter_name and filter_name.lower() not in info["name"].lower():
                    continue
                processes.append(info)
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                pass

        return processes

    def kill_process(self, pid: int, force: bool = False) -> bool:
        """Kill process by PID"""
        try:
            proc = psutil.Process(pid)
            if force:
                proc.kill()
            else:
                proc.terminate()
            self.logger.info(f"Process {pid} {'killed' if force else 'terminated'}")
            return True
        except Exception as e:
            self.logger.error(f"Error killing process {pid}: {e}")
            return False


class ProcessManager:
    """System process management"""

    def __init__(self):
        self.logger = logging.getLogger(__name__)

    def execute_command(self, command: str, shell: bool = True) -> Dict[str, str]:
        """Execute system command"""
        import subprocess

        try:
            result = subprocess.run(
                command, shell=shell, capture_output=True, text=True, timeout=30
            )

            return {
                "stdout": result.stdout,
                "stderr": result.stderr,
                "returncode": result.returncode,
            }
        except subprocess.TimeoutExpired:
            self.logger.error(f"Command timeout: {command}")
            return {"error": "Timeout"}
        except Exception as e:
            self.logger.error(f"Command execution error: {e}")
            return {"error": str(e)}

    def tasklist(self, filter_name: Optional[str] = None) -> str:
        """Run tasklist command (Windows)"""
        cmd = "tasklist"
        if filter_name:
            cmd += f' /FI "IMAGENAME eq {filter_name}"'

        result = self.execute_command(cmd)
        return result.get("stdout", "")

    def taskkill(self, pid: int, force: bool = False) -> bool:
        """Kill process using taskkill (Windows)"""
        cmd = f"taskkill /PID {pid}"
        if force:
            cmd += " /F"

        result = self.execute_command(cmd)
        return result.get("returncode") == 0

    def netstat(self) -> str:
        """Run netstat command"""
        result = self.execute_command("netstat -an")
        return result.get("stdout", "")


__all__ = ["SystemMonitor", "ProcessManager", "SystemMetrics"]
