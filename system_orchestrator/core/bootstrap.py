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
System Bootstrap - Initialize and orchestrate the entire system
"""

import importlib
import logging
import signal
import sys
import threading
from pathlib import Path
from typing import Any, Dict, Optional

from rich.console import Console
from rich.logging import RichHandler
from rich.panel import Panel
from rich.table import Table

from system_orchestrator.core.config import ConfigManager
from system_orchestrator.core.container import ServiceContainer
from system_orchestrator.monitoring.system_monitor import ProcessManager, SystemMonitor
from system_orchestrator.networking.http_client import HTTPClient, OpenAIClient
from system_orchestrator.platform.windows_integration import (
    IS_WINDOWS,
    WINDOWS_MODULES_AVAILABLE,
    PlatformDetector,
)
from system_orchestrator.security.encryption import CredentialManager

console = Console()
logger = logging.getLogger(__name__)


class SystemOrchestrator:
    """
    Main system orchestrator

    Responsibilities:
    - Bootstrap runtime environment
    - Initialize all subsystems
    - Manage lifecycle (startup, shutdown)
    - Coordinate services
    - Handle system events
    """

    def __init__(self):
        self.console = Console()
        self.logger = None  # Initialized in setup_logging
        self.config_manager: Optional[ConfigManager] = None
        self.container: Optional[ServiceContainer] = None
        self.system_monitor: Optional[SystemMonitor] = None
        self.http_client: Optional[HTTPClient] = None
        self.openai_client: Optional[OpenAIClient] = None
        self.credential_manager: Optional[CredentialManager] = None
        self.process_manager: Optional[ProcessManager] = None

        self._shutdown_event = threading.Event()
        self._initialized = False

    def setup_logging(self, config: Optional[ConfigManager] = None):
        """Initialize logging with rotating handlers and rich formatting"""
        log_level = config.get("log_level", "INFO") if config else "INFO"
        logs_dir = config.system_config.logs_dir if config else Path("logs")
        logs_dir.mkdir(parents=True, exist_ok=True)

        # Create rotating file handler
        from logging.handlers import RotatingFileHandler

        log_file = logs_dir / "orchestrator.log"
        file_handler = RotatingFileHandler(
            log_file, maxBytes=10 * 1024 * 1024, backupCount=5
        )  # 10MB
        file_handler.setLevel(logging.DEBUG)
        file_formatter = logging.Formatter(
            "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
        )
        file_handler.setFormatter(file_formatter)

        # Create rich console handler
        console_handler = RichHandler(
            console=self.console, rich_tracebacks=True, tracebacks_show_locals=True
        )
        console_handler.setLevel(getattr(logging, log_level))

        # Configure root logger
        logging.basicConfig(
            level=logging.DEBUG,
            handlers=[file_handler, console_handler],
            format="%(message)s",
        )

        self.logger = logging.getLogger(__name__)
        self.logger.info("Logging initialized")

    def detect_platform(self) -> Dict[str, Any]:
        """Detect platform and system information"""
        self.logger.info("Detecting platform...")

        platform_info = PlatformDetector.get_platform_info()

        # Display platform info
        table = Table(title="Platform Information")
        table.add_column("Property", style="cyan")
        table.add_column("Value", style="green")

        for key, value in platform_info.items():
            table.add_row(key, str(value))

        self.console.print(table)

        return platform_info

    def inject_dependencies(self):
        """Inject dependencies into service container"""
        self.logger.info("Injecting dependencies...")

        self.container = ServiceContainer()

        # Register singletons
        self.container.register_singleton("config_manager", self.config_manager)
        self.container.register_singleton("system_monitor", self.system_monitor)
        self.container.register_singleton("http_client", self.http_client)
        self.container.register_singleton("openai_client", self.openai_client)
        self.container.register_singleton("credential_manager", self.credential_manager)
        self.container.register_singleton("process_manager", self.process_manager)

        self.logger.info(f"Registered {len(self.container._singletons)} services")

    def wire_modules(self):
        """Dynamically wire modules using importlib and reflection"""
        self.logger.info("Wiring modules dynamically...")

        modules = [
            "system_orchestrator.monitoring.system_monitor",
            "system_orchestrator.networking.http_client",
            "system_orchestrator.security.encryption",
        ]

        if IS_WINDOWS and WINDOWS_MODULES_AVAILABLE:
            modules.append("system_orchestrator.platform.windows_integration")

        for module_name in modules:
            try:
                module = importlib.import_module(module_name)
                self.logger.debug(f"Loaded module: {module_name}")
            except Exception as e:
                self.logger.error(f"Failed to load module {module_name}: {e}")

    def setup_signal_handlers(self):
        """Setup signal handlers for graceful shutdown"""

        def signal_handler(signum, frame):
            self.logger.info(f"Received signal {signum}, initiating shutdown...")
            self._shutdown_event.set()
            self.shutdown()

        signal.signal(signal.SIGINT, signal_handler)
        signal.signal(signal.SIGTERM, signal_handler)

        self.logger.info("Signal handlers registered")

    def bootstrap(self):
        """Bootstrap the entire system"""
        self.console.print(
            Panel.fit(
                "[bold cyan]System Orchestrator[/bold cyan]\n"
                "[green]Windows 11 + Windsurf + Python[/green]\n"
                "[yellow]Initializing...[/yellow]",
                border_style="blue",
            )
        )

        # Step 1: Load configuration
        self.config_manager = ConfigManager()

        # Step 2: Setup logging
        self.setup_logging(self.config_manager)

        # Step 3: Detect platform
        platform_info = self.detect_platform()

        # Step 4: Initialize subsystems
        self.logger.info("Initializing subsystems...")

        # Monitoring
        interval = self.config_manager.get("monitor_interval_seconds", 60)
        self.system_monitor = SystemMonitor(interval_seconds=interval)
        self.process_manager = ProcessManager()

        # Networking
        timeout = self.config_manager.get("http_timeout", 30)
        retries = self.config_manager.get("max_retries", 3)
        self.http_client = HTTPClient(timeout=timeout, max_retries=retries)

        # OpenAI
        api_key = self.config_manager.system_config.openai_api_key
        model = self.config_manager.system_config.openai_model
        if api_key:
            self.openai_client = OpenAIClient(api_key=api_key, model=model)
            self.logger.info("OpenAI client initialized")
        else:
            self.logger.warning("OpenAI API key not found, client not initialized")

        # Security
        use_keyring = self.config_manager.system_config.use_credential_manager
        self.credential_manager = CredentialManager(use_system_keyring=use_keyring)

        # Step 5: Inject dependencies
        self.inject_dependencies()

        # Step 6: Wire modules
        self.wire_modules()

        # Step 7: Setup signal handlers
        self.setup_signal_handlers()

        # Step 8: Start background monitoring
        if self.config_manager.get("monitoring.enabled", True):
            self.system_monitor.start()
            self.logger.info("Background monitoring started")

        self._initialized = True

        self.console.print(
            Panel.fit(
                "[bold green]✓ System Orchestrator Initialized[/bold green]\n"
                f"[cyan]Platform:[/cyan] {platform_info['system']}\n"
                f"[cyan]Python:[/cyan] {platform_info['python_implementation']}\n"
                f"[cyan]Monitoring:[/cyan] Active ({interval}s interval)",
                border_style="green",
            )
        )

        self.logger.info("System orchestrator bootstrap complete")

    def verify_environment(self) -> Dict[str, bool]:
        """Verify environment health and configuration integrity"""
        self.logger.info("Verifying environment health...")

        checks = {
            "config_loaded": self.config_manager is not None,
            "logging_active": self.logger is not None,
            "container_ready": self.container is not None
            and len(self.container._singletons) > 0,
            "monitoring_active": self.system_monitor is not None
            and self.system_monitor._monitoring,
            "http_client_ready": self.http_client is not None,
            "platform_detected": IS_WINDOWS,
        }

        # Display verification results
        table = Table(title="Environment Health Check")
        table.add_column("Check", style="cyan")
        table.add_column("Status", style="bold")

        for check, passed in checks.items():
            status = "[green]✓ PASS[/green]" if passed else "[red]✗ FAIL[/red]"
            table.add_row(check, status)

        self.console.print(table)

        all_passed = all(checks.values())
        if all_passed:
            self.logger.info("All environment checks passed")
        else:
            self.logger.warning("Some environment checks failed")

        return checks

    def get_diagnostics(self) -> Dict[str, Any]:
        """Get structured diagnostics and telemetry"""
        diagnostics = {
            "initialized": self._initialized,
            "platform": PlatformDetector.get_platform_info(),
            "services": {
                "config": self.config_manager is not None,
                "monitoring": self.system_monitor is not None,
                "http": self.http_client is not None,
                "openai": self.openai_client is not None,
                "security": self.credential_manager is not None,
            },
        }

        # Add metrics if available
        if self.system_monitor:
            metrics = self.system_monitor.get_latest_metrics()
            if metrics:
                diagnostics["metrics"] = {
                    "cpu_percent": metrics.cpu_percent,
                    "memory_percent": metrics.memory_percent,
                    "disk_usage_percent": metrics.disk_usage_percent,
                    "process_count": metrics.process_count,
                }

        return diagnostics

    def shutdown(self):
        """Graceful shutdown"""
        if not self._initialized:
            return

        self.logger.info("Shutting down system orchestrator...")

        # Stop monitoring
        if self.system_monitor:
            self.system_monitor.stop()
            self.logger.info("Monitoring stopped")

        # Close HTTP clients
        if self.http_client:
            self.http_client.close()
            self.logger.info("HTTP client closed")

        # Clear container
        if self.container:
            self.container.clear()
            self.logger.info("Service container cleared")

        self._initialized = False

        self.console.print(
            Panel.fit(
                "[bold yellow]System Orchestrator Shutdown Complete[/bold yellow]",
                border_style="yellow",
            )
        )


def main():
    """Main entry point"""
    orchestrator = SystemOrchestrator()

    try:
        # Bootstrap system
        orchestrator.bootstrap()

        # Verify environment
        orchestrator.verify_environment()

        # Get diagnostics
        diagnostics = orchestrator.get_diagnostics()
        orchestrator.logger.info(f"System diagnostics: {diagnostics}")

        # Keep running until shutdown signal
        orchestrator.logger.info(
            "System orchestrator running. Press Ctrl+C to shutdown."
        )
        orchestrator._shutdown_event.wait()

    except KeyboardInterrupt:
        orchestrator.logger.info("Keyboard interrupt received")
    except Exception as e:
        orchestrator.logger.error(f"Fatal error: {e}", exc_info=True)
        sys.exit(1)
    finally:
        orchestrator.shutdown()


if __name__ == "__main__":
    main()


__all__ = ["SystemOrchestrator", "main"]
