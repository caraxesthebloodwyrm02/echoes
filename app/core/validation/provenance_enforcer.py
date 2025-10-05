"""
Provenance Enforcer Middleware

Ensures all API responses containing assertions include proper provenance.
Adds X-Provenance-Checked header to validated responses.
"""

import json
import logging

from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.types import ASGIApp

logger = logging.getLogger(__name__)


class ProvenanceEnforcerMiddleware(BaseHTTPMiddleware):
    """
    Middleware to enforce provenance on all assertion-containing responses.

    This middleware:
    1. Inspects outgoing JSON responses
    2. Checks for 'assertions' or 'assertion' keys
    3. Validates that each assertion includes provenance
    4. Returns 500 error if provenance is missing
    5. Adds X-Provenance-Checked header if validation passes

    Critical for preventing hallucinations and ensuring traceability.
    """

    def __init__(self, app: ASGIApp, enforce_strict: bool = True):
        """
        Initialize middleware.

        Args:
            app: The ASGI application
            enforce_strict: If True, reject responses missing provenance.
                           If False, only log warnings.
        """
        super().__init__(app)
        self.enforce_strict = enforce_strict

    async def dispatch(self, request: Request, call_next):
        """Process request and enforce provenance on response."""

        # Call next middleware/route
        response: Response = await call_next(request)

        # Only check JSON responses
        content_type = response.headers.get("content-type", "")
        if "application/json" not in content_type:
            return response

        # Read response body
        body = b""
        async for chunk in response.body_iterator:
            body += chunk

        # Try to parse JSON
        try:
            payload = json.loads(body.decode())
        except json.JSONDecodeError:
            # Not valid JSON, return as-is
            return Response(
                content=body,
                status_code=response.status_code,
                headers=dict(response.headers),
                media_type=response.media_type,
            )

        # Check for assertions in response
        provenance_check_result = self._check_provenance(payload, request.url.path)

        if not provenance_check_result["valid"]:
            if self.enforce_strict:
                logger.error(
                    f"Provenance enforcement failed for {request.url.path}: "
                    f"{provenance_check_result['reason']}"
                )
                return Response(
                    content=json.dumps(
                        {
                            "detail": "Provenance validation failed",
                            "reason": provenance_check_result["reason"],
                            "path": request.url.path,
                        }
                    ),
                    status_code=500,
                    media_type="application/json",
                )
            else:
                logger.warning(
                    f"Provenance missing (non-strict mode) for {request.url.path}: "
                    f"{provenance_check_result['reason']}"
                )

        # Add provenance check header
        headers = dict(response.headers)
        headers["X-Provenance-Checked"] = "true" if provenance_check_result["valid"] else "false"
        headers["X-Provenance-Count"] = str(provenance_check_result.get("count", 0))

        return Response(
            content=json.dumps(payload),
            status_code=response.status_code,
            headers=headers,
            media_type="application/json",
        )

    def _check_provenance(self, payload: dict, path: str) -> dict:
        """
        Check if payload contains assertions with provenance.

        Returns:
            dict with 'valid' (bool), 'reason' (str), and 'count' (int)
        """
        # Skip provenance check for certain paths
        skip_paths = ["/health", "/metrics", "/docs", "/openapi.json"]
        if any(path.startswith(skip_path) for skip_path in skip_paths):
            return {"valid": True, "reason": "Path excluded from provenance checks"}

        # Check if payload contains assertions (list)
        if "assertions" in payload and isinstance(payload["assertions"], list):
            total_count = 0
            for idx, assertion in enumerate(payload["assertions"]):
                if not isinstance(assertion, dict):
                    continue

                # Check for provenance key
                if "provenance" not in assertion:
                    return {
                        "valid": False,
                        "reason": f"Assertion at index {idx} missing provenance",
                        "count": total_count,
                    }

                # Check provenance is not empty
                provenance = assertion["provenance"]
                if not provenance or (isinstance(provenance, list) and len(provenance) == 0):
                    return {
                        "valid": False,
                        "reason": f"Assertion at index {idx} has empty provenance",
                        "count": total_count,
                    }

                # Count provenance sources
                if isinstance(provenance, list):
                    total_count += len(provenance)
                else:
                    total_count += 1

            logger.info(
                f"Provenance check passed: {total_count} sources for {len(payload['assertions'])} assertions"
            )
            return {"valid": True, "reason": "All assertions have provenance", "count": total_count}

        # Check if payload contains single assertion
        if "assertion" in payload and isinstance(payload["assertion"], dict):
            assertion = payload["assertion"]

            if "provenance" not in assertion:
                return {
                    "valid": False,
                    "reason": "Assertion missing provenance",
                    "count": 0,
                }

            provenance = assertion["provenance"]
            if not provenance or (isinstance(provenance, list) and len(provenance) == 0):
                return {
                    "valid": False,
                    "reason": "Assertion has empty provenance",
                    "count": 0,
                }

            count = len(provenance) if isinstance(provenance, list) else 1
            return {"valid": True, "reason": "Assertion has provenance", "count": count}

        # No assertions found in payload - this is okay
        return {"valid": True, "reason": "No assertions in response"}
