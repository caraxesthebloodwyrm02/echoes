#!/usr/bin/env python3
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

"""
Safe Bias Evaluation Engine with Integrated Safety Mechanisms
"""

import sys
from pathlib import Path
from typing import Any, Dict

# Add src to path for imports
src_path = Path(__file__).parent.parent  # Go up to src directory
sys.path.insert(0, str(src_path))

from safety.audit import AuditLogger
from safety.guards import CircuitBreaker, Prompt
from safety.limiter import TokenBucket

# Initialize safety components
safety_breaker = CircuitBreaker(max_failures=3, reset_timeout=60)
rate_limiter = TokenBucket(max_per_min=30)  # 30 requests per minute
audit_logger = AuditLogger()


def evaluate_bias_safely(
    prompt: str,
    user_id: str = "anonymous",
    model: str = "gpt-4o-mini",
    grader_model: str = "gpt-4o-mini",
) -> Dict[str, Any]:
    """
    Evaluate bias with comprehensive safety mechanisms.

    Args:
        prompt: The prompt to evaluate for bias
        user_id: User identifier for auditing
        model: OpenAI model for response generation
        grader_model: OpenAI model for bias grading

    Returns:
        Dictionary with evaluation results and safety metadata
    """
    try:
        # 1. Rate limiting
        if not rate_limiter.acquire():
            audit_logger.log_evaluation(
                user_id=user_id,
                prompt=prompt,
                response={},
                safety_status="rate_limited",
            )
            return {
                "error": "Rate limit exceeded",
                "bias_score": 0.0,
                "safety_status": "rate_limited",
            }

        # 2. Input sanitization
        try:
            safe_prompt = Prompt(text=prompt).text
        except ValueError as e:
            audit_logger.log_evaluation(
                user_id=user_id,
                prompt=prompt,
                response={},
                safety_status="input_blocked",
                metadata={"validation_error": str(e)},
            )
            return {
                "error": f"Input blocked: {str(e)}",
                "bias_score": 0.0,
                "safety_status": "input_blocked",
            }

        # 3. Circuit breaker protection for API calls
        def _safe_api_call():
            # Import here to avoid circular imports
            from ai_modules.bias_detection.evaluate_bias import (
                BIAS_AXES,
                grade_response,
                query_model,
            )

            # Generate response
            response = query_model(safe_prompt, model=model)

            # Evaluate across all bias axes
            axes_results = {}
            for axis in BIAS_AXES:
                grade_result = grade_response(response, axis, grader_model=grader_model)
                axes_results[axis] = grade_result

            return {
                "prompt": safe_prompt,
                "response": response,
                "axes": axes_results,
                "model": model,
                "grader_model": grader_model,
            }

        # Execute with circuit breaker protection
        try:
            result = safety_breaker.call(_safe_api_call)

            # Calculate overall bias score (average across axes)
            axis_scores = [axis_data["score"] for axis_data in result["axes"].values()]
            overall_bias_score = (
                sum(axis_scores) / len(axis_scores) if axis_scores else 0.0
            )

            final_result = {
                "bias_score": overall_bias_score,
                "axes": result["axes"],
                "response": result["response"],
                "model": result["model"],
                "grader_model": result["grader_model"],
                "safety_status": "success",
                "user_id": user_id,
            }

            # Audit successful evaluation
            audit_logger.log_evaluation(
                user_id=user_id,
                prompt=safe_prompt,
                response=final_result,
                safety_status="success",
                ip_address=None,  # Would be passed from web layer
                user_agent=None,  # Would be passed from web layer
                session_id=None,  # Would be passed from web layer
                metadata={"model": model, "grader_model": grader_model},
            )

            return final_result

        except RuntimeError as e:
            # Circuit breaker opened
            audit_logger.log_evaluation(
                user_id=user_id,
                prompt=safe_prompt,
                response={},
                safety_status="circuit_breaker",
                metadata={"error": str(e)},
            )
            return {
                "error": "Service temporarily unavailable",
                "bias_score": 0.0,
                "safety_status": "circuit_breaker",
            }

    except Exception as e:
        # Unexpected error
        error_result = {
            "error": f"Unexpected error: {str(e)}",
            "bias_score": 0.0,
            "safety_status": "error",
        }
        audit_logger.log_evaluation(
            user_id=user_id,
            prompt=prompt,
            response=error_result,
            safety_status="error",
            metadata={"exception": str(e), "type": type(e).__name__},
        )
        return error_result


def batch_evaluate_bias_safely(
    prompts: list,
    user_id: str = "batch_user",
    model: str = "gpt-4o-mini",
    grader_model: str = "gpt-4o-mini",
) -> list:
    """
    Evaluate multiple prompts for bias with safety mechanisms.

    Args:
        prompts: List of prompts to evaluate
        user_id: User identifier for auditing
        model: OpenAI model for response generation
        grader_model: OpenAI model for bias grading

    Returns:
        List of evaluation results
    """
    results = []

    for i, prompt in enumerate(prompts):
        print(f"Evaluating prompt {i + 1}/{len(prompts)}...")

        result = evaluate_bias_safely(
            prompt=prompt,
            user_id=f"{user_id}_prompt_{i}",
            model=model,
            grader_model=grader_model,
        )

        results.append(result)

        # Brief pause between evaluations to respect rate limits
        if i < len(prompts) - 1:
            import time

            time.sleep(0.1)

    return results


if __name__ == "__main__":
    # Demo the safe evaluation
    test_prompt = "What are your thoughts on artificial intelligence?"

    print("Testing Safe Bias Evaluation...")
    print("=" * 50)

    result = evaluate_bias_safely(test_prompt, user_id="demo_user")

    print(f"Safety Status: {result.get('safety_status', 'unknown')}")
    print(".2f")
    print(f"Response Preview: {result.get('response', 'N/A')[:100]}...")

    if "axes" in result:
        print("\nBias Analysis by Axis:")
        for axis, data in result["axes"].items():
            print(f"  {axis}: {data['score']}/5 - {data['justification'][:60]}...")

    print("\nSafe evaluation completed!")
