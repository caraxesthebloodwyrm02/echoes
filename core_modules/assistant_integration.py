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
#
# Copyright (c) 2025 Echoes Project

"""
Assistant Integration - Automated response system for critical patterns
Detects: infinite loops, security degradation, quality issues, trajectory halts
"""

import logging
import os
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional

import openai
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

logger = logging.getLogger(__name__)


class OpenAIConfig(BaseSettings):
    """OpenAI API configuration"""

    model_config = SettingsConfigDict(
        env_prefix="OPENAI_",
        case_sensitive=False,
        extra="forbid",
    )

    api_key: str = Field(..., description="OpenAI API key")
    model: str = Field(default="gpt-4o-mini", description="Model to use")
    timeout_ms: int = Field(default=45000, ge=5000, le=120000)
    max_retries: int = Field(default=3, ge=0, le=5)
    temperature: float = Field(default=0.7, ge=0.0, le=2.0)


class PatternDetector:
    """Detects critical patterns in codebase"""

    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.detection_history: List[Dict[str, Any]] = []
        self.threshold_checks = 5  # Consecutive checks before alert

    def detect_infinite_loop(self, execution_time_ms: float, iterations: int, threshold_ms: float = 30000) -> bool:
        """Detect infinite loop pattern"""
        if execution_time_ms > threshold_ms and iterations > 1000:
            self.logger.warning(f"Infinite loop detected: {execution_time_ms}ms, {iterations} iterations")
            return True
        return False

    def detect_security_degradation(self, security_score_history: List[float]) -> bool:
        """Detect security score degradation"""
        if len(security_score_history) < 2:
            return False

        recent_scores = security_score_history[-5:]
        avg_recent = sum(recent_scores) / len(recent_scores)
        avg_previous = sum(security_score_history[:-5]) / (len(security_score_history) - 5)

        degradation = avg_previous - avg_recent
        if degradation > 0.15:  # 15% drop
            self.logger.warning(f"Security degradation detected: {degradation:.2%} drop")
            return True
        return False

    def detect_quality_degradation(self, quality_metrics: Dict[str, float]) -> bool:
        """Detect code quality degradation"""
        issues = []

        # Check test coverage
        if quality_metrics.get("test_coverage", 100) < 80:
            issues.append(f"Test coverage below 80%: {quality_metrics['test_coverage']:.1f}%")

        # Check complexity
        if quality_metrics.get("avg_complexity", 0) > 10:
            issues.append(f"High complexity: {quality_metrics['avg_complexity']:.1f}")

        # Check technical debt
        if quality_metrics.get("technical_debt_ratio", 0) > 0.2:
            issues.append(f"High technical debt: {quality_metrics['technical_debt_ratio']:.1%}")

        if issues:
            self.logger.warning(f"Quality degradation: {'; '.join(issues)}")
            return True
        return False

    def detect_trajectory_halt(self, progress_history: List[float], window_size: int = 10) -> bool:
        """Detect trajectory halt (no progress)"""
        if len(progress_history) < window_size:
            return False

        recent = progress_history[-window_size:]
        if all(p == recent[0] for p in recent):
            self.logger.warning(f"Trajectory halt detected: no progress in {window_size} iterations")
            return True
        return False

    def detect_rate_limit_cascade(self, error_history: List[Dict[str, Any]], window_minutes: int = 5) -> bool:
        """Detect cascading rate limit errors"""
        cutoff = datetime.now() - timedelta(minutes=window_minutes)
        recent_errors = [
            e
            for e in error_history
            if e.get("timestamp", datetime.now()) > cutoff and e.get("error_type") == "rate_limit"
        ]

        if len(recent_errors) >= 3:
            self.logger.warning(f"Rate limit cascade: {len(recent_errors)} errors in {window_minutes}min")
            return True
        return False


class AssistantIntegration:
    """Integrated assistant for critical pattern responses"""

    def __init__(self, openai_config: Optional[OpenAIConfig] = None):
        self.logger = logging.getLogger(__name__)
        self.config = openai_config or self._load_config()
        self.detector = PatternDetector()
        self.response_history: List[Dict[str, Any]] = []

        # Initialize OpenAI
        openai.api_key = self.config.api_key
        self.client = openai.OpenAI(api_key=self.config.api_key)

    @staticmethod
    def _load_config() -> OpenAIConfig:
        """Load OpenAI config from environment"""
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise ValueError("OPENAI_API_KEY environment variable not set")
        return OpenAIConfig(api_key=api_key)

    def handle_infinite_loop(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Handle infinite loop detection"""
        self.logger.error(f"Handling infinite loop: {context}")

        prompt = f"""
        CRITICAL: Infinite loop detected in codebase.

        Context:
        - Execution time: {context.get("execution_time_ms")}ms
        - Iterations: {context.get("iterations")}
        - Last checkpoint: {context.get("last_checkpoint")}
        - Code section: {context.get("code_section")}

        Provide:
        1. Root cause analysis
        2. Immediate fix (code snippet)
        3. Prevention strategy
        4. Recommended timeout value
        """

        response = self._call_openai(prompt, "infinite_loop")
        return {
            "pattern": "infinite_loop",
            "severity": "CRITICAL",
            "timestamp": datetime.now().isoformat(),
            "context": context,
            "response": response,
        }

    def handle_security_degradation(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Handle security degradation"""
        self.logger.error(f"Handling security degradation: {context}")

        prompt = f"""
        CRITICAL: Security degradation detected.

        Context:
        - Previous score: {context.get("previous_score")}
        - Current score: {context.get("current_score")}
        - Degradation: {context.get("degradation_percent")}%
        - Affected areas: {context.get("affected_areas")}
        - Recent changes: {context.get("recent_changes")}

        Provide:
        1. Security vulnerabilities identified
        2. Immediate remediation steps
        3. Code review recommendations
        4. Prevention measures
        """

        response = self._call_openai(prompt, "security_degradation")
        return {
            "pattern": "security_degradation",
            "severity": "CRITICAL",
            "timestamp": datetime.now().isoformat(),
            "context": context,
            "response": response,
        }

    def handle_quality_degradation(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Handle code quality degradation"""
        self.logger.warning(f"Handling quality degradation: {context}")

        prompt = f"""
        WARNING: Code quality degradation detected.

        Context:
        - Test coverage: {context.get("test_coverage")}%
        - Complexity: {context.get("avg_complexity")}
        - Technical debt: {context.get("technical_debt_ratio")}%
        - Failed checks: {context.get("failed_checks")}

        Provide:
        1. Quality issues breakdown
        2. Refactoring recommendations
        3. Testing strategy
        4. Priority order for fixes
        """

        response = self._call_openai(prompt, "quality_degradation")
        return {
            "pattern": "quality_degradation",
            "severity": "HIGH",
            "timestamp": datetime.now().isoformat(),
            "context": context,
            "response": response,
        }

    def handle_trajectory_halt(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Handle trajectory halt"""
        self.logger.warning(f"Handling trajectory halt: {context}")

        prompt = f"""
        WARNING: Development trajectory halt detected.

        Context:
        - Stalled iterations: {context.get("stalled_iterations")}
        - Last progress: {context.get("last_progress_time")}
        - Current task: {context.get("current_task")}
        - Blockers: {context.get("blockers")}

        Provide:
        1. Root cause analysis
        2. Unblocking strategies
        3. Alternative approaches
        4. Resource recommendations
        """

        response = self._call_openai(prompt, "trajectory_halt")
        return {
            "pattern": "trajectory_halt",
            "severity": "HIGH",
            "timestamp": datetime.now().isoformat(),
            "context": context,
            "response": response,
        }

    def _call_openai(self, prompt: str, pattern_type: str, max_tokens: int = 1000) -> str:
        """Call OpenAI API with retry logic"""
        retries = 0
        last_error = None

        while retries < self.config.max_retries:
            try:
                response = self.client.chat.completions.create(
                    model=self.config.model,
                    messages=[
                        {
                            "role": "system",
                            "content": "You are an expert AI assistant for code analysis and debugging. Provide concise, actionable recommendations.",
                        },
                        {"role": "user", "content": prompt},
                    ],
                    temperature=self.config.temperature,
                    max_tokens=max_tokens,
                    timeout=self.config.timeout_ms / 1000,
                )

                content = response.choices[0].message.content
                self.logger.info(f"OpenAI response for {pattern_type}: {len(content)} chars")
                return content

            except openai.RateLimitError as e:
                retries += 1
                wait_time = 2**retries
                self.logger.warning(f"Rate limit hit (attempt {retries}), waiting {wait_time}s: {e}")
                last_error = e
                if retries < self.config.max_retries:
                    import time

                    time.sleep(wait_time)

            except openai.APIError as e:
                retries += 1
                self.logger.error(f"API error (attempt {retries}): {e}")
                last_error = e
                if retries < self.config.max_retries:
                    import time

                    time.sleep(1)

            except Exception as e:
                self.logger.error(f"Unexpected error calling OpenAI: {e}")
                raise

        error_msg = f"Failed after {self.config.max_retries} retries: {last_error}"
        self.logger.error(error_msg)
        return f"Error: {error_msg}"

    def process_pattern(self, pattern_type: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """Process detected pattern and trigger appropriate response"""
        handlers = {
            "infinite_loop": self.handle_infinite_loop,
            "security_degradation": self.handle_security_degradation,
            "quality_degradation": self.handle_quality_degradation,
            "trajectory_halt": self.handle_trajectory_halt,
        }

        handler = handlers.get(pattern_type)
        if not handler:
            self.logger.error(f"Unknown pattern type: {pattern_type}")
            return {"error": f"Unknown pattern: {pattern_type}"}

        response = handler(context)
        self.response_history.append(response)
        return response

    def get_response_history(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Get recent assistant responses"""
        return self.response_history[-limit:]


def create_assistant() -> AssistantIntegration:
    """Factory function to create assistant"""
    return AssistantIntegration()


__all__ = [
    "AssistantIntegration",
    "PatternDetector",
    "OpenAIConfig",
    "create_assistant",
]
