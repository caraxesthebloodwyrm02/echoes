#!/usr/bin/env python3
"""
CI/CD Pipeline Manager
Version 1.0.0

Automated deployment pipeline with security scanning and container optimization.
"""

import json
import logging
import subprocess
import time
from dataclasses import asdict, dataclass
from datetime import datetime
from pathlib import Path
from typing import Dict, List


@dataclass
class PipelineStage:
    """Represents a pipeline stage."""

    name: str
    enabled: bool
    timeout_seconds: int
    dependencies: List[str]
    commands: List[str]
    on_failure: str  # "stop", "continue", "retry"


@dataclass
class DeploymentResult:
    """Result of a deployment operation."""

    timestamp: datetime
    stage: str
    success: bool
    duration_ms: float
    output: str
    error: str
    artifacts: Dict


class PipelineManager:
    """
    Manages CI/CD pipeline execution with security and optimization.
    """

    def __init__(self, config_file: str = "pipeline_config.json"):
        self.config_file = config_file
        self.pipeline_stages: List[PipelineStage] = []
        self.deployment_history: List[DeploymentResult] = []
        self.config = self._load_config()
        self.logger = self._setup_logging()

    def _load_config(self) -> Dict:
        """Load pipeline configuration."""
        default_config = {
            "pipeline": {
                "name": "IDEA Security Pipeline",
                "trigger": "on_push",
                "parallel_stages": True,
                "fail_fast": True,
            },
            "stages": {
                "security_scan": {
                    "enabled": True,
                    "timeout_seconds": 300,
                    "dependencies": [],
                    "commands": [
                        "python security_guardrails.py",
                        "python vulnerability_analyzer.py",
                        "python contributor_accountability.py",
                    ],
                    "on_failure": "stop",
                },
                "test_execution": {
                    "enabled": True,
                    "timeout_seconds": 600,
                    "dependencies": ["security_scan"],
                    "commands": [
                        "python test_runner.py",
                        "python -m pytest 6/maps/tests/ -v --cov=utils --cov=idea_system --cov=delivery_management --cov=smart_search",
                    ],
                    "on_failure": "stop",
                },
                "container_build": {
                    "enabled": True,
                    "timeout_seconds": 900,
                    "dependencies": ["test_execution"],
                    "commands": [
                        "docker build -t idea-system:latest .",
                        "docker build -t idea-system:$(date +%Y%m%d_%H%M%S) .",
                    ],
                    "on_failure": "stop",
                },
                "container_scan": {
                    "enabled": True,
                    "timeout_seconds": 600,
                    "dependencies": ["container_build"],
                    "commands": [
                        "docker run --rm -v /var/run/docker.sock:/var/run/docker.sock aquasecurity/trivy:latest image idea-system:latest",
                        "docker scan idea-system:latest || true",
                    ],
                    "on_failure": "continue",
                },
                "optimization_check": {
                    "enabled": True,
                    "timeout_seconds": 300,
                    "dependencies": ["container_scan"],
                    "commands": [
                        "python container_auto_tuner.py",
                        "python guardrails_monitor.py",
                    ],
                    "on_failure": "continue",
                },
                "deployment": {
                    "enabled": True,
                    "timeout_seconds": 600,
                    "dependencies": ["optimization_check"],
                    "commands": [
                        "docker-compose down || true",
                        "docker-compose up -d",
                        "sleep 30",
                        "curl -f http://localhost:8000/health || exit 1",
                    ],
                    "on_failure": "stop",
                },
            },
            "notifications": {
                "slack_webhook": "",
                "teams_webhook": "",
                "email_recipients": [],
            },
        }

        try:
            if Path(self.config_file).exists():
                with open(self.config_file, "r") as f:
                    user_config = json.load(f)
                    self._deep_merge(default_config, user_config)
        except Exception as e:
            self.logger.warning(f"Could not load config: {e}")

        # Create pipeline stages
        for stage_name, stage_data in default_config["stages"].items():
            stage = PipelineStage(
                name=stage_name,
                enabled=stage_data["enabled"],
                timeout_seconds=stage_data["timeout_seconds"],
                dependencies=stage_data["dependencies"],
                commands=stage_data["commands"],
                on_failure=stage_data["on_failure"],
            )
            self.pipeline_stages.append(stage)

        return default_config

    def _deep_merge(self, base: Dict, update: Dict):
        """Deep merge configuration dictionaries."""
        for key, value in update.items():
            if key in base and isinstance(base[key], dict) and isinstance(value, dict):
                self._deep_merge(base[key], value)
            else:
                base[key] = value

    def _setup_logging(self) -> logging.Logger:
        """Setup logging configuration."""
        logging.basicConfig(
            level=logging.INFO,
            format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
            handlers=[logging.FileHandler("pipeline.log"), logging.StreamHandler()],
        )
        return logging.getLogger("PipelineManager")

    def execute_stage(self, stage: PipelineStage) -> DeploymentResult:
        """Execute a single pipeline stage."""
        start_time = time.time()
        self.logger.info(f"Executing stage: {stage.name}")

        try:
            # Check dependencies
            for dep in stage.dependencies:
                dep_stage = next((s for s in self.pipeline_stages if s.name == dep), None)
                if dep_stage:
                    dep_result = next((r for r in self.deployment_history if r.stage == dep), None)
                    if not dep_result or not dep_result.success:
                        raise Exception(f"Dependency {dep} failed or not executed")

            # Execute commands
            output_lines = []
            error_lines = []

            for cmd in stage.commands:
                self.logger.info(f"Running: {cmd}")
                result = subprocess.run(
                    cmd.split(),
                    capture_output=True,
                    text=True,
                    timeout=stage.timeout_seconds,
                )

                output_lines.extend(result.stdout.split("\n"))
                error_lines.extend(result.stderr.split("\n"))

                if result.returncode != 0 and stage.on_failure == "stop":
                    raise Exception(f"Command failed: {cmd}")

            duration = (time.time() - start_time) * 1000

            deployment_result = DeploymentResult(
                timestamp=datetime.now(),
                stage=stage.name,
                success=True,
                duration_ms=duration,
                output="\n".join(output_lines),
                error="\n".join(error_lines),
                artifacts={"commands_executed": len(stage.commands)},
            )

            self.logger.info(f"Stage {stage.name} completed successfully in {duration:.0f}ms")
            return deployment_result

        except subprocess.TimeoutExpired:
            duration = (time.time() - start_time) * 1000
            error_msg = f"Stage {stage.name} timed out after {stage.timeout_seconds}s"

            deployment_result = DeploymentResult(
                timestamp=datetime.now(),
                stage=stage.name,
                success=False,
                duration_ms=duration,
                output="",
                error=error_msg,
                artifacts={},
            )

            self.logger.error(error_msg)
            return deployment_result

        except Exception as e:
            duration = (time.time() - start_time) * 1000

            deployment_result = DeploymentResult(
                timestamp=datetime.now(),
                stage=stage.name,
                success=False,
                duration_ms=duration,
                output="",
                error=str(e),
                artifacts={},
            )

            self.logger.error(f"Stage {stage.name} failed: {e}")
            return deployment_result

    def execute_pipeline(self) -> bool:
        """Execute the complete pipeline."""
        self.logger.info("Starting pipeline execution...")

        all_successful = True

        # Execute stages in dependency order
        executed_stages = set()

        while len(executed_stages) < len([s for s in self.pipeline_stages if s.enabled]):
            made_progress = False

            for stage in self.pipeline_stages:
                if not stage.enabled:
                    continue

                if stage.name in executed_stages:
                    continue

                # Check if all dependencies are satisfied
                deps_satisfied = all(dep in executed_stages for dep in stage.dependencies)

                if deps_satisfied:
                    result = self.execute_stage(stage)
                    self.deployment_history.append(result)

                    executed_stages.add(stage.name)
                    made_progress = True

                    if not result.success and self.config["pipeline"]["fail_fast"]:
                        self.logger.error("Pipeline failed and fail_fast is enabled")
                        return False

            if not made_progress:
                # Check for circular dependencies or missing stages
                pending_stages = [
                    s.name
                    for s in self.pipeline_stages
                    if s.enabled and s.name not in executed_stages
                ]
                if pending_stages:
                    self.logger.error(
                        f"Cannot execute stages due to unmet dependencies: {pending_stages}"
                    )
                    return False
                break

        # Check overall success
        failed_stages = [r for r in self.deployment_history if not r.success]
        if failed_stages:
            self.logger.warning(f"Pipeline completed with {len(failed_stages)} failed stages")
            all_successful = False

        return all_successful

    def generate_pipeline_report(self) -> str:
        """Generate comprehensive pipeline report."""
        report = []
        report.append("🚀 PIPELINE EXECUTION REPORT")
        report.append("=" * 50)
        report.append(f"Generated: {datetime.now().isoformat()}")
        report.append("")

        # Pipeline summary
        total_stages = len([s for s in self.pipeline_stages if s.enabled])
        successful_stages = len([r for r in self.deployment_history if r.success])
        failed_stages = len([r for r in self.deployment_history if not r.success])

        report.append(f"Total Stages: {total_stages}")
        report.append(f"Successful: {successful_stages}")
        report.append(f"Failed: {failed_stages}")
        report.append("")

        # Stage details
        report.append("STAGE DETAILS:")
        for result in self.deployment_history:
            status = "✅" if result.success else "❌"
            report.append(f"  {status} {result.stage}: {result.duration_ms:.0f}ms")

            if result.output:
                # Show first few lines of output
                output_lines = result.output.split("\n")[:3]
                for line in output_lines:
                    if line.strip():
                        report.append(f"    {line}")

            if not result.success and result.error:
                report.append(f"    Error: {result.error}")
            report.append("")

        return "\n".join(report)

    def save_pipeline_data(self):
        """Save pipeline execution data."""
        # Save deployment history
        history_data = [asdict(r) for r in self.deployment_history[-50:]]
        for result in history_data:
            result["timestamp"] = result["timestamp"].isoformat()

        with open("pipeline_history.json", "w") as f:
            json.dump(history_data, f, indent=2)


def main():
    """Main pipeline execution."""
    manager = PipelineManager()

    print("🚀 Starting IDEA Security Pipeline...")
    print("=" * 50)

    # Execute pipeline
    start_time = time.time()
    success = manager.execute_pipeline()
    total_time = (time.time() - start_time) * 1000

    # Generate and display report
    report = manager.generate_pipeline_report()
    print(report)

    # Save data
    manager.save_pipeline_data()

    # Final status
    if success:
        print(f"\n✅ Pipeline completed successfully in {total_time:.0f}ms")
        return 0
    else:
        print(f"\n❌ Pipeline completed with failures in {total_time:.0f}ms")
        return 1


if __name__ == "__main__":
    import sys

    sys.exit(main())
