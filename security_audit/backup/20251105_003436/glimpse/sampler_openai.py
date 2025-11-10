"""
OpenAI-backed sampler for Glimpse using direct OpenAI API calls.
Bypasses the wrapper layer for direct access to OpenAI's API.
"""
import logging

import openai

from glimpse.Glimpse import Draft

from .cache_helpers import cached_openai_call

logger = logging.getLogger(__name__)


def _map_openai_error_to_status(exc: Exception) -> str:
    """Map OpenAI exceptions to GlimpseResult status values."""
    import openai

    if isinstance(exc, openai.RateLimitError):
        return "rate_limited"
    if isinstance(exc, openai.AuthenticationError):
        return "auth_error"
    if isinstance(exc, openai.BadRequestError):
        return "bad_request"
    if isinstance(exc, openai.NotFoundError):
        return "not_found"
    if isinstance(exc, openai.UnprocessableEntityError):
        return "unprocessable"
    if isinstance(exc, openai.PermissionError):
        return "permission_denied"
    if isinstance(exc, openai.InternalServerError):
        return "server_error"
    # Fallback
    return "error"


async def _essence_only_fallback(draft: Draft) -> tuple[str, str, str | None, bool]:
    """Return a minimal essence-only result when full API fails."""
    # Simple heuristic: extract key nouns/verbs from input and goal
    tokens = draft.input_text.split() + draft.goal.split()
    # Remove stopwords and keep first few meaningful words
    stopwords = {
        "the",
        "a",
        "an",
        "and",
        "or",
        "but",
        "in",
        "on",
        "at",
        "to",
        "for",
        "of",
        "with",
        "by",
        "is",
        "are",
        "was",
        "were",
    }
    filtered = [t for t in tokens if t.lower() not in stopwords][:8]
    essence = f"Essence (fallback): {' '.join(filtered)} | constraints: {draft.constraints or 'none'}"
    return "", essence, None, False


@cached_openai_call()
async def _openai_chat_completion(
    messages: list[dict],
    model: str,
    temperature: float,
    max_tokens: int | None,
    **kwargs,
) -> dict:
    """Cached wrapper around the actual OpenAI chat completion using direct API."""
    # Create AsyncOpenAI client directly (no wrapper)
    client = openai.AsyncOpenAI()

    # Direct API call - bypassing the wrapper
    response = await client.chat.completions.create(
        messages=messages,
        model=model,
        temperature=temperature,
        max_tokens=max_tokens,
        **kwargs,
    )

    # Return the response as a dict (compatible with existing code)
    return response.model_dump()


async def openai_sampler(draft: Draft) -> tuple[str, str, str | None, bool]:
    """
    OpenAI-backed sampler compatible with GlimpseEngine.
    Returns (sample, essence, delta, aligned) tuple.
    """
    # Simple prompt construction; can be refined with templates
    system_message = {
        "role": "system",
        "content": (
            "You are a helpful assistant. Provide a concise response "
            "that fulfills the user's goal, respecting any constraints."
        ),
    }
    user_content = f"Goal: {draft.goal}\nInput: {draft.input_text}"
    if draft.constraints:
        user_content += f"\nConstraints: {draft.constraints}"
    user_message = {"role": "user", "content": user_content}
    messages = [system_message, user_message]

    try:
        response = await _openai_chat_completion(
            messages=messages,
            model="gpt-4o-mini",
            temperature=0.7,
            max_tokens=256,
        )
        content = response["choices"][0]["message"]["content"]
        # Derive a short essence from the content
        essence = content.split(".")[0].strip() if content else ""
        return content, essence, None, True
    except Exception as e:
        status = _map_openai_error_to_status(e)
        logger.warning(
            "openai_sampler_mapped_error",
            extra={"status": status, "error": str(e), "draft": draft},
        )
        # Attempt essence-only fallback for transient or recoverable errors
        if status in {"rate_limited", "server_error", "error"}:
            sample, essence, delta, aligned = await _essence_only_fallback(draft)
            return sample, f"{essence} (status: {status})", delta, aligned
        # For client errors (auth, bad request, etc.), return a clear error essence
        error_essence = f"Error: {status}. Unable to generate response."
        return "", error_essence, None, False


# Register as the default sampler if desired by importing this module
# Example: from glimpse.sampler_openai import openai_sampler as default_sampler
