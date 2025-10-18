#!/usr/bin/env python3
"""
Expanded Model Evaluation Test Suite

This comprehensive test suite addresses rate‑limiting issues and provides robust
evaluation capabilities for AI models with proper error handling and performance
monitoring.
"""

# --------------------------------------------------------------------------- #
# Imports
# --------------------------------------------------------------------------- #

import json
import logging
import statistics
import subprocess
import threading
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from contextlib import contextmanager
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

# --------------------------------------------------------------------------- #
# Logging configuration
# --------------------------------------------------------------------------- #

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[logging.FileHandler("model_eval.log"), logging.StreamHandler()],
)
logger = logging.getLogger(__name__)

# --------------------------------------------------------------------------- #
# Rate‑limit data structures
# --------------------------------------------------------------------------- #


@dataclass
class RateLimitMetrics:
    """Collect metrics about rate‑limit handling."""

    requests_made: int = 0
    rate_limit_hits: int = 0
    retries_attempted: int = 0
    successful_requests: int = 0
    failed_requests: int = 0
    response_times: List[float] = field(default_factory=list)
    errors: Dict[str, int] = field(default_factory=dict)

    @property
    def success_rate(self) -> float:
        return (
            self.successful_requests / self.requests_made
            if self.requests_made
            else 0.0
        )

    @property
    def average_response_time(self) -> float:
        return statistics.mean(self.response_times) if self.response_times else 0.0


@dataclass
class RateLimitConfig:
    """Configuration that drives the rate‑limit handler."""

    max_retries: int = 5
    base_delay: float = 1.0  # seconds
    max_delay: float = 60.0  # seconds
    backoff_factor: float = 2.0
    rate_limit_window: float = 60.0  # seconds
    max_requests_per_window: int = 30
    concurrent_limit: int = 3


# --------------------------------------------------------------------------- #
# Rate‑limit handler (exponential back‑off + circuit breaker)
# --------------------------------------------------------------------------- #


class RateLimitHandler:
    """Execute a callable respecting rate‑limits and retry policy."""

    def __init__(self, config: RateLimitConfig) -> None:
        self.config = config
        self.metrics = RateLimitMetrics()
        self.request_times: List[datetime] = []
        self.circuit_breaker_tripped = False
        self.last_failure_time: Optional[datetime] = None
        self.consecutive_failures = 0
        self.lock = threading.Lock()

    # --------------------------------------------------------------------- #
    # Private helpers
    # --------------------------------------------------------------------- #

    def _is_rate_limited(self) -> bool:
        """True if we have already sent too many requests inside the window."""
        now = datetime.now()
        # Keep only timestamps inside the sliding window
        self.request_times = [
            t
            for t in self.request_times
            if (now - t).total_seconds() < self.config.rate_limit_window
        ]
        return len(self.request_times) >= self.config.max_requests_per_window

    def _calculate_backoff_delay(self, attempt: int) -> float:
        delay = self.config.base_delay * (self.config.backoff_factor ** attempt)
        return min(delay, self.config.max_delay)

    @staticmethod
    def _detect_rate_limit_error(error_output: str) -> bool:
        """Very small heuristic – good enough for the demo."""
        indicators = [
            "rate limit",
            "too many requests",
            "429",
            "throttle",
            "quota exceeded",
        ]
        return any(ind.lower() in error_output.lower() for ind in indicators)

    def _update_metrics(
        self, success: bool, response_time: float, error: Optional[str] = None
    ) -> None:
        with self.lock:
            self.metrics.requests_made += 1
            self.metrics.response_times.append(response_time)

            if success:
                self.metrics.successful_requests += 1
                self.consecutive_failures = 0
            else:
                self.metrics.failed_requests += 1
                self.consecutive_failures += 1
                self.last_failure_time = datetime.now()
                if error:
                    self.metrics.errors[error] = self.metrics.errors.get(error, 0) + 1

    def _wait_for_rate_limit_reset(self) -> None:
        """Sleep just enough for the oldest request to fall out of the window."""
        if not self.request_times:
            return
        oldest = min(self.request_times)
        wait = self.config.rate_limit_window - (
            datetime.now() - oldest
        ).total_seconds()
        if wait > 0:
            logger.info("Waiting %.1f s for rate‑limit reset", wait)
            time.sleep(wait)

    # --------------------------------------------------------------------- #
    # Circuit‑breaker context manager
    # --------------------------------------------------------------------- #

    @contextmanager
    def circuit_breaker_context(self):
        """Raise if the circuit is open, otherwise allow the wrapped call."""
        if self.circuit_breaker_tripped:
            # Reset after a cool‑down period (5 min)
            if self.last_failure_time and (
                datetime.now() - self.last_failure_time
            ).total_seconds() > 300:
                self.circuit_breaker_tripped = False
                self.consecutive_failures = 0
                logger.info("Circuit breaker reset – resuming requests")
            else:
                raise RuntimeError(
                    "Circuit breaker is open – too many consecutive failures"
                )

        try:
            yield
        except Exception:
            if self.consecutive_failures >= 5:
                self.circuit_breaker_tripped = True
                logger.error("Circuit breaker tripped")
            raise

    # --------------------------------------------------------------------- #
    # Public API
    # --------------------------------------------------------------------- #

    def execute_with_retry(self, func, *args, **kwargs) -> Tuple[Any, float]:
        """
        Run ``func`` with rate‑limit checks, exponential back‑off and
        circuit‑breaker protection. Returns a tuple ``(result, elapsed_seconds)``.
        """
        start = time.time()

        for attempt in range(self.config.max_retries + 1):
            try:
                with self.circuit_breaker_context():
                    if self._is_rate_limited():
                        logger.warning("Rate limit reached – waiting")
                        self._wait_for_rate_limit_reset()

                    # Record the request moment (protected by lock)
                    with self.lock:
                        self.request_times.append(datetime.now())

                    # Execute the wrapped call
                    result = func(*args, **kwargs)

                    elapsed = time.time() - start
                    self._update_metrics(True, elapsed)
                    return result, elapsed

            except Exception as exc:
                elapsed = time.time() - start
                err_str = str(exc)

                self.metrics.retries_attempted += 1

                if self._detect_rate_limit_error(err_str):
                    self.metrics.rate_limit_hits += 1
                    logger.warning("Rate‑limit error on attempt %d", attempt + 1)

                if attempt < self.config.max_retries:
                    delay = self._calculate_backoff_delay(attempt)
                    logger.info("Backing off for %.1f s", delay)
                    time.sleep(delay)
                else:
                    self._update_metrics(False, elapsed, err_str)
                    raise

        # Should never be reached
        raise RuntimeError("Unexpected exit from retry loop")


# --------------------------------------------------------------------------- #
# Model evaluator – the heart of the test‑suite
# --------------------------------------------------------------------------- #


class ModelEvaluator:
    """Run inference on a set of prompts with robust error handling."""

    def __init__(
        self, models: List[str], questions_dir: Path, output_dir: Path
    ) -> None:
        self.models = models
        self.questions_dir = questions_dir
        self.output_dir = output_dir

        # Rate‑limit configuration (feel free to tune)
        cfg = RateLimitConfig(
            max_retries=5,
            base_delay=2.0,
            max_delay=120.0,
            backoff_factor=1.5,
            rate_limit_window=60.0,
            max_requests_per_window=20,
            concurrent_limit=2,
        )
        self.rate_limiter = RateLimitHandler(cfg)

        # A small thread‑pool for concurrent requests
        self.executor = ThreadPoolExecutor(max_workers=cfg.concurrent_limit)

    # --------------------------------------------------------------------- #
    # Helper utilities
    # --------------------------------------------------------------------- #

    @staticmethod
    def _ensure_dir(path: Path) -> None:
        path.mkdir(parents=True, exist_ok=True)

    def _question_files(self) -> List[Path]:
        return sorted(self.questions_dir.glob("*.txt"))

    # --------------------------------------------------------------------- #
    # Inference wrapper
    # --------------------------------------------------------------------- #

    def _run_ollama(self, model: str, prompt: str) -> str:
        """Call ``ollama run`` – raise on non‑zero exit."""
        result = subprocess.run(
            ["ollama", "run", model, prompt],
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            timeout=600,  # 10 min per request (generous)
        )
        if result.returncode != 0:
            raise RuntimeError(
                result.stderr.strip() or result.stdout.strip()
            )
        return result.stdout.strip()

    def run_model_inference(self, model: str, prompt: str) -> str:
        """Public entry point – retries + rate‑limit handling."""
        try:
            response, elapsed = self.rate_limiter.execute_with_retry(
                self._run_ollama, model, prompt
            )
            logger.info("Inference completed in %.2f s", elapsed)
            return response
        except Exception as exc:
            logger.error("Inference failed after retries: %s", exc)
            return f"ERROR: {exc}"

    # --------------------------------------------------------------------- #
    # Single‑question evaluation
    # --------------------------------------------------------------------- #

    def evaluate_single_question(
        self, model: str, question_file: Path
    ) -> Dict[str, Any]:
        """Run one prompt through one model and write a markdown report."""
        qid = question_file.stem
        model_dir = self.output_dir / model.replace(":", "_")
        self._ensure_dir(model_dir)
        out_path = model_dir / f"{qid}.md"

        start = time.time()
        try:
            # Load prompt
            prompt = question_file.read_text(encoding="utf-8")

            # Get LLM answer
            answer = self.run_model_inference(model, prompt)

            # Timing
            duration = time.time() - start

            # Write human‑readable markdown
            out_path.write_text(
                f"# {qid.replace('_', ' ').title()}\n\n"
                f"## Model: {model}\n\n"
                f"## Processing Time: {duration:.2f}s\n\n"
                f"## Prompt\n\n```\n{prompt}\n```\n\n"
                f"## Response\n\n{answer}",
                encoding="utf-8",
            )

            return {
                "question_id": qid,
                "model": model,
                "success": True,
                "processing_time": duration,
                "response_length": len(answer),
                "output_file": str(out_path),
            }

        except Exception as exc:
            duration = time.time() - start
            logger.error("Failed %s / %s: %s", qid, model, exc)
            return {
                "question_id": qid,
                "model": model,
                "success": False,
                "processing_time": duration,
                "error": str(exc),
            }

    # --------------------------------------------------------------------- #
    # Full evaluation run
    # --------------------------------------------------------------------- #

    def run_comprehensive_evaluation(self) -> Dict[str, Any]:
        logger.info(
            "Starting evaluation: %d questions × %d models",
            len(self._question_files()),
            len(self.models),
        )

        futures = []
        for model in self.models:
            for qfile in self._question_files():
                futures.append(
                    self.executor.submit(self.evaluate_single_question, model, qfile)
                )

        results: List[Dict[str, Any]] = []
        for fut in as_completed(futures):
            try:
                res = fut.result()
                results.append(res)
                if res["success"]:
                    logger.info(
                        "✅ %s / %s (%.2f s)",
                        res["question_id"],
                        res["model"],
                        res["processing_time"],
                    )
                else:
                    logger.error(
                        "❌ %s / %s – %s",
                        res["question_id"],
                        res["model"],
                        res.get("error", "unknown"),
                    )
            except Exception as exc:
                logger.error("Unexpected error while collecting results: %s", exc)

        # Shut down the thread‑pool (no more tasks will be submitted)
        self.executor.shutdown(wait=True)

        report = self._build_report(results)
        self._save_report(report)
        logger.info("Evaluation complete – results stored under %s", self.output_dir)

        return report

    # --------------------------------------------------------------------- #
    # Reporting helpers
    # --------------------------------------------------------------------- #

    def _build_report(self, results: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Aggregate per‑model / per‑question statistics."""
        total = len(results)
        successes = [r for r in results if r["success"]]
        report: Dict[str, Any] = {
            "timestamp": datetime.now().isoformat(),
            "total_questions": len(self._question_files()),
            "total_models": len(self.models),
            "total_evaluations": total,
            "overall_success_rate": len(successes) / total if total else 0.0,
            "rate_limiting_metrics": {
                "requests_made": self.rate_limiter.metrics.requests_made,
                "rate_limit_hits": self.rate_limiter.metrics.rate_limit_hits,
                "retries_attempted": self.rate_limiter.metrics.retries_attempted,
                "success_rate": self.rate_limiter.metrics.success_rate,
                "average_response_time": self.rate_limiter.metrics.average_response_time,
                "error_breakdown": self.rate_limiter.metrics.errors,
            },
            "model_performance": {},
            "question_performance": {},
        }

        # Model‑level aggregation
        for model in self.models:
            model_res = [r for r in results if r["model"] == model]
            model_success = [r for r in model_res if r["success"]]
            report["model_performance"][model] = {
                "total_evaluations": len(model_res),
                "successful_evaluations": len(model_success),
                "success_rate": len(model_success) / len(model_res)
                if model_res
                else 0.0,
                "average_processing_time": (
                    statistics.mean([r["processing_time"] for r in model_success])
                    if model_success
                    else 0.0
                ),
            }

        # Question‑level aggregation
        for qfile in self._question_files():
            qid = qfile.stem
            q_res = [r for r in results if r["question_id"] == qid]
            q_success = [r for r in q_res if r["success"]]
            report["question_performance"][qid] = {
                "total_evaluations": len(q_res),
                "successful_evaluations": len(q_success),
                "success_rate": len(q_success) / len(q_res) if q_res else 0.0,
                "average_processing_time": (
                    statistics.mean([r["processing_time"] for r in q_success])
                    if q_success
                    else 0.0
                ),
            }

        return report

    def _save_report(self, report: Dict[str, Any]) -> None:
        out_file = self.output_dir / "evaluation_metrics.json"
        out_file.write_text(json.dumps(report, indent=2, default=str), encoding="utf-8")
        logger.info("Metrics written to %s", out_file)

    # --------------------------------------------------------------------- #
    # Optional load‑test utilities
    # --------------------------------------------------------------------- #

    def _simple_ollama_call(self, model: str, prompt: str) -> str:
        """Very thin wrapper used by the load‑test (no retry/metrics)."""
        result = subprocess.run(
            ["ollama", "run", model, prompt],
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            timeout=60,
        )
        if result.returncode != 0:
            raise RuntimeError(
                result.stderr.strip() or result.stdout.strip()
            )
        return result.stdout.strip()

    def _load_test_request(
        self, model: str, prompt: str, request_id: int
    ) -> Dict[str, Any]:
        try:
            resp, elapsed = self.rate_limiter.execute_with_retry(
                lambda: self._simple_ollama_call(model, prompt)
            )
            return {
                "success": True,
                "request_id": request_id,
                "response_time": elapsed,
                "response_length": len(resp),
            }
        except Exception as exc:
            return {"success": False, "request_id": request_id, "error": str(exc)}

    def run_load_test(self, model: str, num_requests: int = 50) -> Dict[str, Any]:
        """Fire a burst of requests to discover rate‑limit thresholds."""
        logger.info("Load‑test: %s – %d requests", model, num_requests)
        prompt = "What is the capital of France?"

        start = time.time()
        futures = [
            self.executor.submit(self._load_test_request, model, prompt, i)
            for i in range(num_requests)
        ]

        results = [f.result() for f in as_completed(futures)]

        total = time.time() - start
        successes = [r for r in results if r["success"]]
        failures = [r for r in results if not r["success"]]

        report = {
            "model": model,
            "total_requests": num_requests,
            "successful_requests": len(successes),
            "failed_requests": len(failures),
            "success_rate": len(successes) / num_requests if num_requests else 0.0,
            "total_time": total,
            "requests_per_second": num_requests / total if total else 0.0,
            "rate_limiting_detected": self.rate_limiter.metrics.rate_limit_hits > 0,
            "rate_limit_metrics": self.rate_limiter.metrics.__dict__,
        }

        # Persist load‑test report
        out_path = (
            self.output_dir
            / f"load_test_{model.replace(':', '_')}_{datetime.now():%Y%m%d_%H%M%S}.json"
        )
        out_path.write_text(json.dumps(report, indent=2, default=str), encoding="utf-8")
        logger.info("Load‑test report saved to %s", out_path)

        return report


# --------------------------------------------------------------------------- #
# Entry‑point
# --------------------------------------------------------------------------- #

def main() -> None:
    """Kick‑off the whole evaluation process."""

    # ------------------------------------------------------------------- #
    # Configuration – adapt to your environment
    # ------------------------------------------------------------------- #
    MODELS = ["mistral:7b-instruct"]
    QUESTIONS_DIR = Path(__file__).parent / "questions"
    OUTPUT_ROOT = Path(__file__).parent / "evaluations"
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    OUTPUT_DIR = OUTPUT_ROOT / f"run_{timestamp}"

    evaluator = ModelEvaluator(MODELS, QUESTIONS_DIR, OUTPUT_DIR)

    try:
        # --------------------------------------------------------------- #
        # 1️⃣  Run the full evaluation
        # --------------------------------------------------------------- #
        logger.info("🚀 Starting comprehensive evaluation")
        report = evaluator.run_comprehensive_evaluation()

        # --------------------------------------------------------------- #
        # 2️⃣  Optional: fire a quick load‑test
        # --------------------------------------------------------------- #
        if input("Run load test? (y/N): ").strip().lower().startswith("y"):
            for m in MODELS:
                evaluator.run_load_test(m, num_requests=30)

        # --------------------------------------------------------------- #
        # 3️⃣  Print a concise summary
        # --------------------------------------------------------------- #
        print("\n📊 Evaluation Summary")
        print(f"Total evaluations      : {report['total_evaluations']}")
        print(f"Overall success rate   : {report['overall_success_rate']:.2%}")
        print(f"Rate‑limit hits        : {report['rate_limiting_metrics']['rate_limit_hits']}")
        print(f"Retries attempted      : {report['rate_limiting_metrics']['retries_attempted']}")
        print(
            f"Avg. response time     : {report['rate_limiting_metrics']['average_response_time']:.2f}s"
        )
        print(f"\n📁 Results stored in   : {OUTPUT_DIR.resolve()}")

    except KeyboardInterrupt:
        logger.warning("Evaluation interrupted by user")
    except Exception as exc:
        logger.error("Fatal error – %s", exc)
        raise


if __name__ == "__main__":
    main()
