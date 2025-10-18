#!/usr/bin/env python3
"""
Core implementation for the expanded model‑evaluation test suite.

All heavy‑lifting (rate‑limit handling, model inference, reporting, etc.) lives
here so that the thin wrapper script can simply import and call ``main()``.
"""

# --------------------------------------------------------------------------- #
# Standard library imports
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
# Data classes – rate‑limit metrics & configuration
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
# Rate‑limit handler (exponential back‑off + circuit‑breaker)
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
        now = datetime.now()
        self.request_times = [
            t
            for t in self.request_times
            if (now - t).total_seconds() < self.config.rate_limit_window
        ]
        return len(self.request_times) >= self.config.max_requests_per_window

    def _calculate_backoff_delay(self, attempt: int) -> float:
        return min(
            self.config.base_delay * (self.config.backoff_factor ** attempt),
            self.config.max_delay,
        )

    @staticmethod
    def _detect_rate_limit_error(error_output: str) -> bool:
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
        if self.circuit_breaker_tripped:
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
    # Public retry wrapper
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

                    with self.lock:
                        self.request_times.append(datetime.now())

                    result = func(*args, **kwargs)

                    elapsed = time.time() - start
                    self._update_metrics(True, elapsed)
                    return result, elapsed

            except Exception as exc:
                elapsed = time.time() - start
                err_msg = str(exc)

                self.metrics.retries_attempted += 1

                if self._detect_rate_limit_error(err_msg):
                    self.metrics.rate_limit_hits += 1
                    logger.warning(
                        "Rate‑limit error on attempt %d", attempt + 1
                    )

                if attempt < self.config.max_retries:
                    delay = self._calculate_backoff_delay(attempt)
                    logger.info("Backing off for %.1f s", delay)
                    time.sleep(delay)
                else:
                    self._update_metrics(False, elapsed, err_msg)
                    raise

        raise RuntimeError("Unexpected exit from retry loop")


# --------------------------------------------------------------------------- #
# Model evaluator – runs prompts against Ollama models
# --------------------------------------------------------------------------- #


class ModelEvaluator:
    """Run inference on a set of prompts with robust error handling."""

    def __init__(
        self, models: List[str], questions_dir: Path, output_dir: Path
    ) -> None:
        self.models = models
        self.questions_dir = questions_dir
        self.output_dir = output_dir

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
        self.executor = ThreadPoolExecutor(max_workers=cfg.concurrent_limit)

    # --------------------------------------------------------------------- #
    # Utility helpers
    # --------------------------------------------------------------------- #

    @staticmethod
    def _ensure_dir(p: Path) -> None:
        p.mkdir(parents=True, exist_ok=True)

    def _question_files(self) -> List[Path]:
        return sorted(self.questions_dir.glob("*.txt"))

    # --------------------------------------------------------------------- #
    # Inference wrapper
    # --------------------------------------------------------------------- #

    def _run_ollama(self, model: str, prompt: str) -> str:
        result = subprocess.run(
            ["ollama", "run", model, prompt],
            capture_output=True,
            timeout=600,
        )

        # Decode output safely
        try:
            stdout = result.stdout.decode('utf-8', errors='replace')
            stderr = result.stderr.decode('utf-8', errors='replace')
        except UnicodeDecodeError:
            # Fallback to latin-1 which can decode any byte sequence
            stdout = result.stdout.decode('latin-1', errors='replace')
            stderr = result.stderr.decode('latin-1', errors='replace')

        if result.returncode != 0:
            raise RuntimeError(stderr.strip() or stdout.strip())
        return stdout.strip()

    def run_model_inference(self, model: str, prompt: str) -> str:
        try:
            response, elapsed = self.rate_limiter.execute_with_retry(
                self._run_ollama, model, prompt
            )
            logger.info("Inference completed in %.2f s", elapsed)
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
        qid = question_file.stem
        model_dir = self.output_dir / model.replace(":", "_")
        self._ensure_dir(model_dir)
        out_path = model_dir / f"{qid}.md"

        start = time.time()
        try:
            prompt = question_file.read_text(encoding="utf-8")
            answer = self.run_model_inference(model, prompt)
            duration = time.time() - start

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
                    self.executor.submit(
                        self.evaluate_single_question, model, qfile
                    )
                )

        results: List[Dict[str, Any]] = []
        for fut in as_completed(futures):
            try:
                res = fut.result()
                results.append(res)
                if res["success"]:
                    logger.info(
                        "SUCCESS %s / %s (%.2f s)",
                        res["question_id"],
                        res["model"],
                        res["processing_time"],
                    )
                else:
                    logger.error(
                        "FAILED %s / %s – %s",
                        res["question_id"],
                        res["model"],
                        res.get("error", "unknown"),
                    )
            except Exception as exc:
                logger.error("Unexpected error while collecting results: %s", exc)

        self.executor.shutdown(wait=True)

        report = self._build_report(results)
        self._save_report(report)
        logger.info("Evaluation complete – results under %s", self.output_dir)

        return report

    def run_load_test(self, model: str, num_requests: int = 30) -> None:
        """Run a load test for the specified model"""
        from load_tester import LoadTester, LoadTestConfig, print_load_test_summary

        logger.info(f"Running load test for {model}")

        config = LoadTestConfig(
            model=model,
            concurrent_requests=3,
            total_requests=num_requests,
            ramp_up_time=10.0
        )

        tester = LoadTester(config)
        result = tester.run_load_test()
        print_load_test_summary(result)

    # --------------------------------------------------------------------- #
    # Reporting helpers
    # --------------------------------------------------------------------- #

    def _build_report(self, results: List[Dict[str, Any]]) -> Dict[str, Any]:
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
                    statistics.mean(
                        [r["processing_time"] for r in model_success]
                    )
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
                    statistics.mean(
                        [r["processing_time"] for r in q_success]
                    )
                    if q_success
                    else 0.0
                ),
            }

        return report

    def _save_report(self, report: Dict[str, Any]) -> None:
        out_file = self.output_dir / "evaluation_metrics.json"
        out_file.write_text(
            json.dumps(report, indent=2, default=str), encoding="utf-8"
        )
        logger.info("Metrics written to %s", out_file)


# --------------------------------------------------------------------------- #
# Entry‑point (called by the thin wrapper)
# --------------------------------------------------------------------------- #

def main() -> None:
    """Run the full evaluation workflow."""
    MODELS = ["mistral:7b-instruct"]
    QUESTIONS_DIR = Path(__file__).parent / "questions"
    OUTPUT_ROOT = Path(__file__).parent / "evaluations"
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    OUTPUT_DIR = OUTPUT_ROOT / f"run_{timestamp}"

    evaluator = ModelEvaluator(MODELS, QUESTIONS_DIR, OUTPUT_DIR)

    try:
        logger.info("Starting comprehensive evaluation")
        report = evaluator.run_comprehensive_evaluation()

        # --------------------------------------------------------------- #
        # Optional quick load‑test
        # --------------------------------------------------------------- #
        if input("Run load test? (y/N): ").strip().lower().startswith("y"):
            for m in MODELS:
                evaluator.run_load_test(m, num_requests=30)

        # --------------------------------------------------------------- #
        # Print a short summary
        # --------------------------------------------------------------- #
        print("\nEvaluation Summary")
        print(f"Total evaluations      : {report['total_evaluations']}")
        print(
            f"Overall success rate   : {report['overall_success_rate']:.2%}"
        )
        print(
            f"Rate‑limit hits        : {report['rate_limiting_metrics']['rate_limit_hits']}"
        )
        print(
            f"Retries attempted      : {report['rate_limiting_metrics']['retries_attempted']}"
        )
        print(
            f"Avg. response time     : {report['rate_limiting_metrics']['average_response_time']:.2f}s"
        )
        print(f"\nResults stored in   : {OUTPUT_DIR.resolve()}")

    except KeyboardInterrupt:
        logger.warning("Evaluation interrupted by user")
    except Exception as exc:
        logger.error("Fatal error – %s", exc)
        raise


if __name__ == "__main__":
    main()
