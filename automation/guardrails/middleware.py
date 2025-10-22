import json
from .ingest_docs import parse_security_protocols
from .rate_limiter import RateLimiter as _TokenBucketLimiter
from .schemas import (
    ToolCallResponse,
    ToolCallStatus,
    RateLimitConfig,
    AuthenticationConfig,
    ToolValidationSchema,
    ErrorDetail,
)


class ValidationError(Exception):
    pass


class TupleCompatibleResponse:
    """Wrapper supporting tuple unpacking and ToolCallResponse attribute access."""

    def __init__(self, response: ToolCallResponse):
        self._response = response

    def __iter__(self):
        """Support tuple unpacking: result, error = response."""
        yield self._response.data
        yield self._response.error

    def __getitem__(self, index):
        """Support indexing for tuple unpacking."""
        if index == 0:
            return self._response.data
        elif index == 1:
            return self._response.error
        else:
            raise IndexError(f"Index {index} out of range")

    def __getattr__(self, name):
        """Delegate to wrapped response."""
        return getattr(self._response, name)

    def __repr__(self):
        return repr(self._response)


class _TupleResponse(tuple):
    """A tuple that also supports attribute access for ToolCallResponse compatibility."""

    def __new__(cls, data, error, response_obj=None):
        # Convert ErrorDetail to dict for legacy test compatibility
        if error is not None and hasattr(error, "model_dump"):
            error_dict = error.model_dump()
        elif error is not None and hasattr(error, "__dict__"):
            error_dict = dict(error)
        else:
            error_dict = error

        instance = super().__new__(cls, (data, error_dict))
        instance._response = response_obj
        return instance

    def __getattr__(self, name):
        """Delegate to wrapped response if available."""
        if self._response is not None:
            return getattr(self._response, name)
        raise AttributeError(f"'{type(self).__name__}' object has no attribute '{name}'")


class RateLimiter:
    """Compatibility wrapper that accepts RateLimitConfig or int.

    Raises RateLimitExceededError when rate limit is exceeded (for enhanced tests).
    """

    def __init__(self, cfg: RateLimitConfig | int = 60):
        if isinstance(cfg, int):
            rate = cfg / 60.0
            capacity = cfg
        else:
            rate = float(cfg.requests_per_minute) / 60.0
            capacity = int(cfg.burst_capacity)
        self._limiter = _TokenBucketLimiter(rate=rate, capacity=capacity)

    def is_allowed(self) -> bool:
        """Check if request is allowed. Raises RateLimitExceededError if not."""
        self._limiter.try_consume("global")
        return True

    def allow(self, key: str = "global") -> bool:
        """Allow a request without raising exception. Returns bool."""
        return self._limiter.allow(key)

    def reset(self) -> None:
        """Reset the rate limiter to initial state."""
        self._limiter.reset()


class GuardrailMiddleware:
    """Middleware to enforce security protocols parsed from documentation."""

    def __init__(
        self,
        doc_path,
        rate_limit_config: RateLimitConfig | int = 60,
        auth_config: AuthenticationConfig | None = None,
        validation_schemas: dict | None = None,
        max_prompt_length: int = 4096,
    ):
        self.protocols = parse_security_protocols(doc_path)
        self.rate_limiter = RateLimiter(rate_limit_config)
        self.max_prompt_length = max_prompt_length
        self.auth_config = auth_config or AuthenticationConfig()
        self.validation_schemas = validation_schemas or {}

    def _validate_authentication(self, headers: dict) -> dict:
        if not self.auth_config.require_authentication:
            return {"success": True}
        token = headers.get(self.auth_config.token_header, "")
        if not token.startswith(self.auth_config.token_prefix):
            return {"success": False, "code": "invalid_token_format"}
        raw = token[len(self.auth_config.token_prefix) :]
        if raw not in self.auth_config.allowed_tokens:
            return {"success": False, "code": "invalid_token"}
        return {"success": True}

    def _validate_against_schema(self, schema: ToolValidationSchema, params: dict) -> dict:
        errors = []
        for rule in schema.parameters:
            name = rule.field
            if rule.required and name not in params:
                errors.append(
                    {
                        "field": name,
                        "error": "missing_field",
                        "message": f"Missing required field: {name}",
                    }
                )
                continue
            if name not in params:
                continue
            val = params[name]
            if rule.type == "string" and not isinstance(val, str):
                errors.append({"field": name, "error": "invalid_type"})
            if rule.type == "integer" and not isinstance(val, int):
                errors.append({"field": name, "error": "invalid_type"})
            if isinstance(val, str):
                if rule.min_length is not None and len(val) < rule.min_length:
                    errors.append({"field": name, "error": "min_length"})
                if rule.max_length is not None and len(val) > rule.max_length:
                    errors.append({"field": name, "error": "max_length"})
            if isinstance(val, (int, float)):
                if rule.min_value is not None and val < rule.min_value:
                    errors.append({"field": name, "error": "min_value"})
                if rule.max_value is not None and val > rule.max_value:
                    errors.append({"field": name, "error": "max_value"})
            if rule.allowed_values is not None and val not in rule.allowed_values:
                errors.append({"field": name, "error": "invalid_value"})
        return {"valid": len(errors) == 0, "errors": errors}

    def validate_request(self, request_body, headers=None, tool_name: str | None = None):
        """Validate request. Returns response supporting both tuple and attribute access.

        Legacy tests unpack as: result, error = guardrail.validate_request(...)
        Enhanced tests use: response = guardrail.validate_request(...); response.status

        Returns:
            _TupleResponse: Tuple that also supports attribute access via wrapped ToolCallResponse
        """
        try:
            return self._validate_request_impl(request_body, headers, tool_name)
        except Exception as e:
            response = ToolCallResponse(
                status=ToolCallStatus.EXECUTION_ERROR,
                error=ErrorDetail(
                    code="internal_server_error",
                    message=f"Unexpected error: {str(e)}",
                    details={"error": str(e)},
                ),
            )
            return _TupleResponse(None, response.error, response)

    def _validate_request_impl(self, request_body, headers=None, tool_name: str | None = None):
        """Implementation of validate_request."""
        headers = headers or {}

        # Handle None or non-dict request body
        if request_body is None or not isinstance(request_body, (dict, str)):
            response = ToolCallResponse(
                status=ToolCallStatus.VALIDATION_ERROR,
                error=ErrorDetail(
                    code="validation_error",
                    message="Invalid request body",
                    details={
                        "errors": [
                            {
                                "error": "invalid_request",
                                "message": "Request body must be a dict or JSON string",
                            }
                        ]
                    },
                ),
            )
            return _TupleResponse(None, response.error, response)

        # JSON parsing
        if isinstance(request_body, str):
            try:
                request_body = json.loads(request_body)
            except Exception as e:
                response = ToolCallResponse(
                    status=ToolCallStatus.VALIDATION_ERROR,
                    error=ErrorDetail(
                        code="invalid_json",
                        message="Invalid JSON",
                        details={"error": str(e)},
                    ),
                )
                return _TupleResponse(None, response.error, response)

        # Authentication check FIRST (before field validation)
        auth_result = self._validate_authentication(headers)
        if not auth_result.get("success", False) and self.auth_config.require_authentication:
            response = ToolCallResponse(
                status=ToolCallStatus.AUTH_ERROR,
                error=ErrorDetail(
                    code=auth_result.get("code", "invalid_token"),
                    message="Authentication failed",
                ),
            )
            return _TupleResponse(None, response.error, response)

        # Rate limiting check
        if not self.rate_limiter.allow():
            response = ToolCallResponse(
                status=ToolCallStatus.RATE_LIMIT_EXCEEDED,
                error=ErrorDetail(
                    code="rate_limit_exceeded",
                    message="Rate limit exceeded",
                    details={"retry_after_seconds": 1},
                ),
            )
            return _TupleResponse(None, response.error, response)

        # Schema validation (optional) - if schema is provided, use it instead of prompt/stage
        if tool_name:
            schema = self.validation_schemas.get(tool_name)
            if isinstance(schema, ToolValidationSchema):
                res = self._validate_against_schema(schema, request_body)
                if not res["valid"]:
                    response = ToolCallResponse(
                        status=ToolCallStatus.VALIDATION_ERROR,
                        error=ErrorDetail(
                            code="validation_error",
                            message="Schema validation failed",
                            details={"errors": res["errors"]},
                        ),
                    )
                    return _TupleResponse(None, response.error, response)
                # Schema validation passed, skip prompt/stage checks
            else:
                # No schema found, check for prompt/stage
                errors = []
                if "prompt" not in request_body or not isinstance(request_body.get("prompt"), str):
                    errors.append(
                        {
                            "field": "prompt",
                            "error": "missing_field",
                            "message": "Missing or invalid 'prompt' field",
                        }
                    )
                if "stage" not in request_body or not isinstance(request_body.get("stage"), str):
                    errors.append(
                        {
                            "field": "stage",
                            "error": "missing_field",
                            "message": "Missing or invalid 'stage' field",
                        }
                    )

                if errors:
                    response = ToolCallResponse(
                        status=ToolCallStatus.VALIDATION_ERROR,
                        error=ErrorDetail(
                            code="validation_error",
                            message="Validation failed",
                            details={"errors": errors},
                        ),
                    )
                    return _TupleResponse(None, response.error, response)
        else:
            # No schema provided, require prompt and stage
            errors = []
            if "prompt" not in request_body or not isinstance(request_body.get("prompt"), str):
                errors.append(
                    {
                        "field": "prompt",
                        "error": "missing_field",
                        "message": "Missing or invalid 'prompt' field",
                    }
                )
            if "stage" not in request_body or not isinstance(request_body.get("stage"), str):
                errors.append(
                    {
                        "field": "stage",
                        "error": "missing_field",
                        "message": "Missing or invalid 'stage' field",
                    }
                )

            if errors:
                response = ToolCallResponse(
                    status=ToolCallStatus.VALIDATION_ERROR,
                    error=ErrorDetail(
                        code="validation_error",
                        message="Validation failed",
                        details={"errors": errors},
                    ),
                )
                return _TupleResponse(None, response.error, response)

            # Validate prompt length
            if len(request_body["prompt"]) > self.max_prompt_length:
                response = ToolCallResponse(
                    status=ToolCallStatus.VALIDATION_ERROR,
                    error=ErrorDetail(
                        code="prompt_too_long",
                        message=f"'prompt' exceeds maximum length of {self.max_prompt_length}",
                        details={"max": self.max_prompt_length},
                    ),
                )
                return _TupleResponse(None, response.error, response)

        response = ToolCallResponse(
            status=ToolCallStatus.SUCCESS,
            data={"message": "Validation successful"},
        )
        return _TupleResponse(response.data, None, response)
