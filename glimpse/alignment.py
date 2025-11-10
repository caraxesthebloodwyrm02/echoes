import hashlib
import inspect
import json
import logging
import time
import uuid
from collections.abc import Callable
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from enum import Enum
from typing import Any

import numpy as np
from openai import AsyncOpenAI

UTC = timezone.utc

# Type aliases
FunctionCall = dict[str, Any]
ToolCall = dict[str, Any]
ToolResult = dict[str, Any]


class ModelType(str, Enum):
    GPT4 = "gpt-4-1106-preview"
    GPT4_TURBO = "gpt-4-turbo"
    GPT35_TURBO = "gpt-3.5-turbo"
    GPT35_TURBO_16K = "gpt-3.5-turbo-16k"


class KnowledgeBase:
    """Simple in-memory knowledge base for demonstration."""

    def __init__(self):
        self.data = {}

    def add_document(self, doc_id: str, content: str, metadata: dict | None = None):
        self.data[doc_id] = {
            "content": content,
            "metadata": metadata or {},
            "timestamp": datetime.now(UTC).isoformat(),
        }

    def search(self, query: str, top_k: int = 3) -> list[dict]:
        """Simple keyword search (would be replaced with vector search in production)."""
        query_terms = set(query.lower().split())
        results = []

        for doc_id, doc in self.data.items():
            content = doc["content"].lower()
            matches = sum(1 for term in query_terms if term in content)
            if matches > 0:
                results.append(
                    {
                        "id": doc_id,
                        "score": matches / len(query_terms),
                        "content": doc["content"][:500] + "...",
                        "metadata": doc["metadata"],
                    }
                )

        return sorted(results, key=lambda x: x["score"], reverse=True)[:top_k]


# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)


@dataclass
class CacheConfig:
    """Configuration for response caching."""

    enabled: bool = True
    max_size: int = 1000
    ttl_seconds: int = 3600  # 1 hour


@dataclass
class CostMetrics:
    """Cost metrics for API calls."""

    input_cost: float
    output_cost: float
    total_cost: float
    input_tokens: int = 0
    output_tokens: int = 0
    model: str = ""


@dataclass
class AlignmentMetrics:
    """Metrics for measuring alignment with the AI provider."""

    response_time: float
    token_usage: dict[str, int]
    relevance: float
    coherence: float
    safety: float
    consistency: float = 0.0
    model_confidence: float = 0.0
    cost: CostMetrics | None = None


class OpenAIAlignmentChecker:
    # Model pricing (USD per 1K tokens) - updated with latest models
    MODEL_PRICING = {
        "gpt-4-1106-preview": {"input": 0.01, "output": 0.03, "context": 128000},
        "gpt-4-turbo": {"input": 0.01, "output": 0.03, "context": 128000},
        "gpt-4": {"input": 0.03, "output": 0.06, "context": 8192},
        "gpt-3.5-turbo": {"input": 0.0015, "output": 0.002, "context": 4096},
        "gpt-3.5-turbo-16k": {"input": 0.003, "output": 0.004, "context": 16384},
    }

    # Confidence thresholds for model upgrades
    CONFIDENCE_THRESHOLDS = {
        "gpt-3.5-turbo": 0.7,  # 70% confidence threshold to upgrade to GPT-4
        "gpt-3.5-turbo-16k": 0.7,
        "gpt-4": 0.9,  # 90% confidence threshold to use GPT-4-Turbo
        "gpt-4-turbo": 0.8,  # 80% confidence threshold to stay on GPT-4-Turbo
    }

    def __init__(
        self,
        api_key: str | None = None,
        default_model: str = "gpt-4-1106-preview",
        cache_config: CacheConfig | None = None,
        knowledge_base: KnowledgeBase | None = None,
    ):
        self.client = AsyncOpenAI(api_key=api_key) if api_key else AsyncOpenAI()
        self.default_model = default_model
        self.metrics_history = []
        self.conversation_history = {}
        self.cache = {}
        self.cache_config = cache_config or CacheConfig()
        self.knowledge_base = knowledge_base or KnowledgeBase()
        self.domain_terms = {
            "nlp": [
                "transformer",
                "attention",
                "embeddings",
                "tokenization",
                "fine-tuning",
                "llm",
                "prompt engineering",
            ],
            "ml": [
                "gradient descent",
                "backpropagation",
                "overfitting",
                "regularization",
                "loss function",
                "optimizer",
            ],
            "mlops": [
                "pipeline",
                "deployment",
                "monitoring",
                "drift detection",
                "model serving",
                "feature store",
            ],
            "ai_safety": [
                "alignment",
                "interpretability",
                "robustness",
                "fairness",
                "bias mitigation",
            ],
        }
        self.system_prompt = """You are an expert AI assistant specializing in machine learning, natural language processing, and technical problem-solving.

Guidelines for responses:
- Be specific and technical when explaining concepts
- Provide concrete examples and code when relevant
- Use domain-specific terminology appropriately
- Give actionable, practical advice
- Avoid generic filler phrases like "How can I help you further?"
- Focus on being helpful, accurate, and comprehensive
- When using tools, explain what you're doing and why
- Maintain context throughout conversations

If asked something outside your expertise, acknowledge this and provide the best guidance possible."""

        self.few_shot_examples = {
            "explanation": [
                {"role": "user", "content": "Explain how transformers work"},
                {
                    "role": "assistant",
                    "content": "Transformers are a type of neural network architecture that revolutionized natural language processing. They use self-attention mechanisms to process input data in parallel, unlike recurrent neural networks that process data sequentially. The key components are:\n\n1. **Self-Attention**: Allows each word to attend to all other words in the input, capturing long-range dependencies\n2. **Multi-Head Attention**: Uses multiple attention heads to capture different types of relationships\n3. **Feed-Forward Networks**: Process each position independently with the same MLP\n4. **Positional Encoding**: Adds position information since transformers don't have recurrence\n\nThis parallel processing enables transformers to handle much longer sequences and train faster than RNNs or LSTMs.",
                },
            ],
            "code": [
                {
                    "role": "user",
                    "content": "Show me a PyTorch implementation of a transformer",
                },
                {
                    "role": "assistant",
                    "content": "```python\nimport torch\nimport torch.nn as nn\nimport torch.nn.functional as F\n\nclass MultiHeadAttention(nn.Module):\n    def __init__(self, d_model, num_heads):\n        super().__init__()\n        self.d_model = d_model\n        self.num_heads = num_heads\n        self.d_k = d_model // num_heads\n        \n        self.W_q = nn.Linear(d_model, d_model)\n        self.W_k = nn.Linear(d_model, d_model)\n        self.W_v = nn.Linear(d_model, d_model)\n        self.W_o = nn.Linear(d_model, d_model)\n    \n    def forward(self, x):\n        batch_size = x.size(0)\n        \n        # Linear transformations\n        Q = self.W_q(x).view(batch_size, -1, self.num_heads, self.d_k).transpose(1, 2)\n        K = self.W_k(x).view(batch_size, -1, self.num_heads, self.d_k).transpose(1, 2)\n        V = self.W_v(x).view(batch_size, -1, self.num_heads, self.d_k).transpose(1, 2)\n        \n        # Attention scores\n        scores = torch.matmul(Q, K.transpose(-2, -1)) / (self.d_k ** 0.5)\n        attention = F.softmax(scores, dim=-1)\n        \n        # Apply attention to values\n        context = torch.matmul(attention, V)\n        context = context.transpose(1, 2).contiguous().view(batch_size, -1, self.d_model)\n        \n        return self.W_o(context)\n\nclass TransformerBlock(nn.Module):\n    def __init__(self, d_model, num_heads, d_ff, dropout=0.1):\n        super().__init__()\n        self.attention = MultiHeadAttention(d_model, num_heads)\n        self.norm1 = nn.LayerNorm(d_model)\n        self.norm2 = nn.LayerNorm(d_model)\n        self.feed_forward = nn.Sequential(\n            nn.Linear(d_model, d_ff),\n            nn.ReLU(),\n            nn.Linear(d_ff, d_model)\n        )\n        self.dropout = nn.Dropout(dropout)\n    \n    def forward(self, x):\n        # Multi-head attention with residual connection\n        attn_out = self.attention(x)\n        x = self.norm1(x + self.dropout(attn_out))\n        \n        # Feed-forward with residual connection\n        ff_out = self.feed_forward(x)\n        x = self.norm2(x + self.dropout(ff_out))\n        \n        return x\n```",
                },
            ],
        }
        self.registered_functions: dict[str, Callable] = {}
        self.function_descriptions: list[dict] = []

    def _get_cache_key(self, prompt: str, model: str, temperature: float) -> str:
        """Generate a cache key for the given parameters."""
        key_str = f"{model}:{temperature}:{prompt}"
        return hashlib.md5(key_str.encode()).hexdigest()

    def _get_cached_response(self, cache_key: str) -> dict | None:
        """Get a cached response if it exists and hasn't expired."""
        if not self.cache_config.enabled:
            return None

        cached = self.cache.get(cache_key)
        if not cached:
            return None

        cached_time = datetime.fromisoformat(cached["timestamp"])
        if (
            datetime.now(UTC) - cached_time
        ).total_seconds() > self.cache_config.ttl_seconds:
            del self.cache[cache_key]
            return None

        return cached["response"]

    def _add_to_cache(self, cache_key: str, response: dict):
        """Add a response to the cache."""
        if not self.cache_config.enabled:
            return

        if len(self.cache) >= self.cache_config.max_size:
            # Remove oldest entry
            oldest_key = next(iter(self.cache))
            del self.cache[oldest_key]

        self.cache[cache_key] = {
            "response": response,
            "timestamp": datetime.now(UTC).isoformat(),
        }

    def _select_model(
        self, prompt: str, conversation_id: str = None, confidence: float = 1.0
    ) -> tuple[str, int, float]:
        """Select appropriate model and parameters based on query complexity and confidence."""
        # Check for domain-specific terms
        domain_score = sum(
            1
            for terms in self.domain_terms.values()
            for term in terms
            if term.lower() in prompt.lower()
        )

        # Check conversation history for context
        context_length = (
            len(self.conversation_history.get(conversation_id, []))
            if conversation_id
            else 0
        )

        # Determine base model and parameters
        if domain_score > 3 or context_length > 3 or len(prompt.split()) > 200:
            base_model = "gpt-4-turbo"
            max_tokens = 1000
            temperature = 0.3
        elif any(q in prompt.lower() for q in ["explain", "how to", "guide", "help"]):
            base_model = "gpt-3.5-turbo-16k"
            max_tokens = 800
            temperature = 0.7
        else:
            base_model = "gpt-3.5-turbo"
            max_tokens = 400
            temperature = 0.5

        # Apply confidence-based model selection
        if confidence < self.CONFIDENCE_THRESHOLDS.get(base_model, 0.7):
            if base_model.startswith("gpt-3.5"):
                # Upgrade to a more capable model
                base_model = "gpt-4-turbo"
                max_tokens = 1200
                temperature = 0.3
            elif base_model == "gpt-4" and confidence < 0.5:
                # For very low confidence, use the most capable model
                base_model = "gpt-4-turbo"

        return base_model, max_tokens, temperature

    def _calculate_cost(
        self, model: str, prompt_tokens: int, completion_tokens: int
    ) -> CostMetrics:
        """Calculate cost based on token usage and model pricing."""
        if model not in self.MODEL_PRICING:
            model = "gpt-3.5-turbo"  # Default to a known model

        pricing = self.MODEL_PRICING[model]
        input_cost = (prompt_tokens / 1000) * pricing["input"]
        output_cost = (completion_tokens / 1000) * pricing["output"]

        return CostMetrics(
            input_cost=round(input_cost, 6),
            output_cost=round(output_cost, 6),
            total_cost=round(input_cost + output_cost, 6),
            input_tokens=prompt_tokens,
            output_tokens=completion_tokens,
            model=model,
        )

    def _compress_response(self, text: str) -> str:
        """Compress long responses to save tokens."""
        if len(text) < 1000:  # Don't compress short responses
            return text

        try:
            # Simple compression: remove extra whitespace and newlines
            compressed = " ".join(text.split())
            if len(compressed) < len(text) * 0.9:  # Only if we save at least 10%
                return compressed
        except:
            pass

        return text

    def _decompress_response(self, text: str) -> str:
        """Decompress a previously compressed response."""
        # In a real implementation, this would reverse the compression
        # For now, we just return as-is since our compression is lossless
        return text

    def register_function(self, func: Callable) -> Callable:
        """Decorator to register a function for tool calling."""
        sig = inspect.signature(func)
        params = {"type": "object", "properties": {}, "required": []}

        for name, param in sig.parameters.items():
            if name == "self":
                continue

            param_type = "string"
            if param.annotation == int:
                param_type = "integer"
            elif param.annotation == float:
                param_type = "number"
            elif param.annotation == bool:
                param_type = "boolean"

            params["properties"][name] = {"type": param_type}
            if param.default == inspect.Parameter.empty:
                params["required"].append(name)

        self.registered_functions[func.__name__] = func
        self.function_descriptions.append(
            {
                "name": func.__name__,
                "description": func.__doc__ or "",
                "parameters": params,
            }
        )

        return func

    async def _execute_tool_call(
        self, tool_call: Any, tool_call_id: str | None = None
    ) -> ToolResult:
        """Execute a tool call returned by the model and format the response."""
        try:
            function_obj = tool_call.function
            function_name = function_obj.name
            arguments_str = function_obj.arguments or "{}"
            tool_call_id = tool_call_id or getattr(tool_call, "id", None)
        except AttributeError:
            function_name = tool_call.get("function", {}).get("name")
            arguments_str = tool_call.get("function", {}).get("arguments", "{}")
            tool_call_id = tool_call_id or tool_call.get("id")

        if not function_name:
            tool_call_id = tool_call_id or f"call_{uuid.uuid4().hex}"
            return {
                "tool_call_id": tool_call_id or "unknown_tool",
                "role": "tool",
                "content": "Error: Tool call missing function name",
            }

        try:
            function_args = json.loads(arguments_str) if arguments_str else {}
        except json.JSONDecodeError as e:
            tool_call_id = tool_call_id or f"call_{uuid.uuid4().hex}"
            return {
                "tool_call_id": tool_call_id or function_name,
                "role": "tool",
                "content": f"Error: Invalid JSON arguments - {str(e)}",
            }

        tool_call_id = (
            tool_call_id or getattr(tool_call, "id", None) or f"call_{uuid.uuid4().hex}"
        )

        if function_name not in self.registered_functions:
            return {
                "tool_call_id": tool_call_id or function_name,
                "role": "tool",
                "content": f"Error: Function {function_name} not found",
            }

        func = self.registered_functions[function_name]

        try:
            result = func(**function_args)
            if inspect.isawaitable(result):
                result = await result

            if not isinstance(result, str):
                result = json.dumps(result)

            return {
                "tool_call_id": tool_call_id or function_name,
                "role": "tool",
                "content": result or "",
            }
        except Exception as e:
            return {
                "tool_call_id": tool_call_id or function_name,
                "role": "tool",
                "content": f"Error: {str(e)}",
            }

    def _sanitize_prompt(
        self, raw_prompt: str, history: list[dict[str, str]] = None
    ) -> str:
        """
        * If the prompt is empty → produce a clarifying question that references
          the last assistant reply if we have one, otherwise a generic one.
        * If the prompt is non‑empty → strip spaces and return it unchanged.
        """
        history = history or []
        txt = raw_prompt.strip() if raw_prompt else ""
        if not txt:
            if history:
                # Grab the most recent assistant turn, shorten a bit
                last = next(
                    (
                        m["content"]
                        for m in reversed(history)
                        if m["role"] == "assistant"
                    ),
                    "",
                )
                if last:
                    snippet = (
                        last.split(".")[0][:70] + "..."
                        if "." in last
                        else last[:70] + "..."
                    )
                    return f"You previously mentioned: {snippet}\nWhat would you like to discuss next?"
            return "Could you please clarify your question?"
        return txt

    def _extract_content(self, response: dict[str, Any]) -> str:
        """
        Safely pull the assistant's text out of an OpenAI chat completion payload.
        If anything is missing we return a clear fallback string instead of raising.
        """
        try:
            # Normal successful shape:
            # {"choices": [{"message": {"content": "...", "role": "assistant"}}], ...}
            content = response["choices"][0]["message"]["content"]
            return content.strip() if content else ""
        except (KeyError, IndexError, TypeError) as exc:
            # Log the whole payload – it is invaluable when the API changes.
            logging.error(
                "Malformed OpenAI response – falling back to safe message: %s", exc
            )
            logging.debug("Full response payload: %s", response)
            return "I apologize, but I encountered an issue processing your request. Could you rephrase your question?"

    async def _call_openai_chat(
        self,
        messages: list[dict[str, str]],
        model: str = "gpt-4-1106-preview",
        **kwargs,
    ) -> tuple[str, dict[str, Any]]:
        """
        Centralised wrapper that:
          * retries transient errors,
          * always returns content string and response dict,
          * logs the raw response for diagnostics.
        """
        MAX_RETRIES = 3
        RETRY_DELAY = 1.5  # seconds

        payload = {"model": model, "messages": messages, **kwargs}

        for attempt in range(1, MAX_RETRIES + 1):
            try:
                raw = await self.client.chat.completions.create(**payload)

                # Log the HTTP response status
                if hasattr(raw, "_response") and hasattr(raw._response, "status_code"):
                    status_code = raw._response.status_code
                else:
                    status_code = "200 OK"
                logging.info(
                    f'HTTP Request: POST https://api.openai.com/v1/chat/completions "{status_code}"'
                )

                response_dict = (
                    raw.model_dump() if hasattr(raw, "model_dump") else dict(raw)
                )
                content = self._extract_content(response_dict)

                return content, response_dict

            except Exception as e:
                error_type = type(e).__name__
                if "rate" in str(e).lower() or "429" in str(e):
                    logging.warning(
                        "Rate limited (attempt %d/%d): %s", attempt, MAX_RETRIES, e
                    )
                elif "timeout" in str(e).lower():
                    logging.warning(
                        "Timeout (attempt %d/%d): %s", attempt, MAX_RETRIES, e
                    )
                else:
                    logging.warning(
                        "API error (attempt %d/%d, %s): %s",
                        attempt,
                        MAX_RETRIES,
                        error_type,
                        e,
                    )

                # If we get here we need to retry or give up
                if attempt < MAX_RETRIES:
                    await asyncio.sleep(RETRY_DELAY)

        # All retries exhausted – return a deterministic fallback
        logging.error("All OpenAI retries failed – returning safe fallback.")
        fallback_content = "I apologize, but I'm experiencing technical difficulties. Could you try asking your question again?"
        fallback_response = {
            "choices": [{"message": {"content": fallback_content, "tool_calls": None}}],
            "usage": {"prompt_tokens": 0, "completion_tokens": 0, "total_tokens": 0},
        }
        return fallback_content, fallback_response

    async def get_completion(
        self,
        prompt: str,
        conversation_id: str = None,
        use_knowledge_base: bool = True,
        **kwargs,
    ) -> dict:
        """Get completion with automatic model selection, cost tracking, and tool calling."""
        # Sanitize the prompt to handle empty inputs gracefully
        prompt = self._sanitize_prompt(prompt)

        # Check cache first
        cache_key = self._get_cache_key(
            prompt, self.default_model, kwargs.get("temperature", 0.7)
        )
        cached = self._get_cached_response(cache_key)
        if cached:
            return cached

        # Prepare messages with conversation history and knowledge base context
        messages = [{"role": "system", "content": self.system_prompt}]
        messages.append({"role": "user", "content": prompt})

        # Add knowledge base context if enabled
        if use_knowledge_base and self.knowledge_base:
            kb_results = self.knowledge_base.search(prompt, top_k=2)
            if kb_results:
                context = "\n\n".join([r["content"] for r in kb_results])
                messages.insert(
                    1,
                    {
                        "role": "system",
                        "content": f"Relevant context from knowledge base:\n{context}",
                    },
                )

        # Add conversation history if available
        if conversation_id and conversation_id in self.conversation_history:
            messages = self.conversation_history[conversation_id] + messages

        # Add few-shot examples if relevant
        if any(q in prompt.lower() for q in ["explain", "how to", "guide"]):
            messages = self.few_shot_examples["explanation"] + messages
        elif any(q in prompt.lower() for q in ["code", "implement", "example"]):
            messages = self.few_shot_examples["code"] + messages

        # Initial model selection
        model, max_tokens, temperature = self._select_model(
            prompt, conversation_id, confidence=kwargs.pop("confidence", 1.0)
        )

        # Prepare API parameters
        params = {
            "model": model,
            "max_tokens": kwargs.pop("max_tokens", max_tokens),
            "temperature": kwargs.pop("temperature", temperature),
            **kwargs,
        }

        # Add function descriptions if any are registered
        if self.function_descriptions:
            params["tools"] = [
                {"type": "function", "function": desc}
                for desc in self.function_descriptions
            ]
            params["tool_choice"] = "auto"

        try:
            initial_response_text, initial_response = await self._call_openai_chat(
                messages, **params
            )

            message = initial_response["choices"][0]["message"]
            tool_calls = getattr(message, "tool_calls", None)
            normalized_tool_calls: list[dict[str, Any]] = []
            tool_responses: list[dict[str, Any]] = []
            final_response = initial_response
            final_response_text = initial_response_text

            if tool_calls:
                normalized_tool_calls = [
                    self._normalize_tool_call(tc) for tc in tool_calls
                ]

                # Execute tool calls and collect responses
                for tool_call in tool_calls:
                    tool_responses.append(await self._execute_tool_call(tool_call))

                # Add assistant tool call metadata
                messages.append(
                    {"role": "assistant", "tool_calls": normalized_tool_calls}
                )
                messages.extend(tool_responses)

                # Get final completion with tool results
                final_response_text, final_response = await self._call_openai_chat(
                    messages,
                    model=model,
                    max_tokens=max_tokens,
                    temperature=temperature,
                )

            # Compress long responses to save tokens
            content = final_response_text
            content = self._compress_response(content)

            # Update conversation history
            if conversation_id:
                history = self.conversation_history.setdefault(conversation_id, [])

                history.append({"role": "user", "content": prompt})
                history.append({"role": "assistant", "content": content})

                if normalized_tool_calls:
                    history.append(
                        {"role": "assistant", "tool_calls": normalized_tool_calls}
                    )
                if tool_responses:
                    history.extend(
                        [
                            {
                                "role": "tool",
                                "tool_call_id": r.get("tool_call_id"),
                                "content": r.get("content", ""),
                            }
                            for r in tool_responses
                        ]
                    )

            # Calculate token usage and cost
            usage = final_response.get("usage", {})
            input_tokens = usage.get(
                "prompt_tokens",
                len(" ".join([msg.get("content", "") for msg in messages]).split()),
            )
            output_tokens = usage.get(
                "completion_tokens", len(content.split()) if content else 0
            )
            total_tokens = usage.get("total_tokens", input_tokens + output_tokens)

            # Create a usage object for compatibility
            usage_obj = type(
                "Usage",
                (),
                {
                    "prompt_tokens": input_tokens,
                    "completion_tokens": output_tokens,
                    "total_tokens": total_tokens,
                },
            )()

            cost_metrics = self._calculate_cost(model, input_tokens, output_tokens)

            result = {
                "content": content,
                "model": model,
                "max_tokens": max_tokens,
                "temperature": temperature,
                "tokens_used": usage_obj.total_tokens,
                "prompt_tokens": usage_obj.prompt_tokens,
                "completion_tokens": usage_obj.completion_tokens,
                "cost": cost_metrics,
                "finish_reason": "stop",  # Default finish reason
                "cached": False,
            }

            # Cache the response
            self._add_to_cache(cache_key, result)

            return result
        except Exception as e:
            logging.error(f"Error with {model}: {str(e)}")
            raise

    def _calculate_consistency(self, response: str, history: list) -> float:
        """Calculate consistency with previous responses in the conversation."""
        if not history:
            return 1.0  # No history to compare with

        # Simple implementation: check for contradictions with previous responses
        previous_responses = " ".join(
            [msg["content"] for msg in history if msg["role"] == "assistant"]
        )
        common_terms = set(response.lower().split()) & set(
            previous_responses.lower().split()
        )
        return min(1.0, len(common_terms) / 10)  # Normalize to 0-1 range

    def analyze_response(
        self,
        response: str,
        prompt: str,
        conversation_history: list = None,
        model: str = "unknown",
    ) -> AlignmentMetrics:
        """Analyze the response for quality metrics."""
        words = response.split()
        sentences = [s for s in response.split(". ") if s]

        # Calculate domain-specific relevance
        relevance = self._calculate_relevance(response, prompt)

        # Check for domain-specific terms in the response
        domain_terms_found = []
        for domain, terms in self.domain_terms.items():
            for term in terms:
                if term.lower() in response.lower():
                    domain_terms_found.append(term)

        # Calculate consistency with conversation history
        consistency = self._calculate_consistency(response, conversation_history or [])

        # Calculate model confidence (based on response length, domain terms, and coherence)
        word_count = len(words)
        sentence_count = len(sentences)
        word_count / max(1, sentence_count)

        # Confidence increases with more domain terms, moderate sentence length, and coherence
        term_confidence = min(1.0, len(domain_terms_found) * 0.2)
        length_confidence = min(
            1.0, word_count / 50
        )  # 50 words is considered a good length
        coherence_metric = min(
            1.0, sentence_count / 5
        )  # More sentences = more coherent

        model_confidence = (
            term_confidence * 0.4 + length_confidence * 0.3 + coherence_metric * 0.3
        )

        # Adjust confidence based on model capabilities
        if "gpt-4" in model:
            model_confidence *= 1.1  # Slight boost for more capable models

        # Calculate safety (simple implementation - would use a more sophisticated approach in production)
        safety_keywords = ["illegal", "harmful", "dangerous", "hate", "violence"]
        safety_score = 1.0 - min(
            1.0, sum(1 for word in safety_keywords if word in response.lower()) * 0.2
        )

        return AlignmentMetrics(
            response_time=0,
            token_usage={"prompt": len(prompt.split()), "completion": word_count},
            relevance=min(1.0, relevance + (len(domain_terms_found) * 0.1)),
            coherence=min(1.0, coherence_metric * 1.1),  # Slight boost for coherence
            safety=max(0.5, safety_score),  # Never go below 0.5 for safety
            consistency=consistency,
            model_confidence=min(
                0.99, model_confidence
            ),  # Cap at 0.99 to allow for improvement
        )

    def _calculate_relevance(self, response: str, prompt: str) -> float:
        prompt_terms = set(prompt.lower().split())
        response_terms = set(response.lower().split())
        return (
            min(1.0, len(prompt_terms.intersection(response_terms)) / len(prompt_terms))
            if prompt_terms
            else 0.0
        )

    async def evaluate_conversation(
        self, conversation_flows: list[list[dict[str, str]]]
    ) -> dict:
        """Evaluate multi-turn conversations."""
        results = []

        for flow in conversation_flows:
            conversation_id = str(hash(tuple(msg["content"] for msg in flow)))
            conversation_results = []

            for turn in flow:
                try:
                    # Only process user messages, skip assistant messages (they're placeholders)
                    if turn.get("role") == "assistant":
                        continue

                    start = time.time()

                    # Get conversation history for this flow so far
                    history = self.conversation_history.get(conversation_id, [])

                    # Sanitize the prompt using conversation context
                    sanitized_prompt = self._sanitize_prompt(turn["content"], history)

                    result = await self.get_completion(
                        prompt=sanitized_prompt, conversation_id=conversation_id
                    )

                    # Analyze response with conversation context
                    metrics = self.analyze_response(
                        response=result["content"],
                        prompt=turn["content"],
                        conversation_history=history,
                    )
                    metrics.response_time = time.time() - start

                    # Add cost metrics
                    metrics.cost = result["cost"]

                    # Store detailed results
                    turn_result = {
                        "prompt": turn["content"],
                        "response": result["content"],
                        "model_used": result["model"],
                        "tokens_used": result["tokens_used"],
                        "temperature": result["temperature"],
                        "finish_reason": result["finish_reason"],
                        "metrics": asdict(metrics),
                    }
                    conversation_results.append(turn_result)

                except Exception as e:
                    logging.error(f"Conversation turn failed: {str(e)}")

            results.extend(conversation_results)

        return (
            self._summarize(results)
            if results
            else {
                "summary": {
                    "total_tests": 0,
                    "total_cost": 0,
                    "total_input_tokens": 0,
                    "total_output_tokens": 0,
                    "cache_hits": 0,
                    "average_metrics": {
                        "response_time": 0,
                        "relevance": 0,
                        "coherence": 0,
                        "safety": 0,
                        "consistency": 0,
                        "model_confidence": 0,
                    },
                    "model_distribution": {},
                    "model_costs": {},
                    "average_temperature": 0,
                    "recommendations": ["No conversation turns completed successfully"],
                },
                "details": [],
            }
        )

    async def evaluate(self, test_cases: list[dict[str, str]]) -> dict:
        """Evaluate single-turn prompts."""
        results = []

        for test in test_cases:
            try:
                start = time.time()
                result = await self.get_completion(test["prompt"])

                metrics = self.analyze_response(
                    response=result["content"], prompt=test["prompt"]
                )
                metrics.response_time = time.time() - start
                metrics.cost = result["cost"]

                results.append(
                    {
                        "prompt": test["prompt"],
                        "response": result["content"],
                        "model_used": result["model"],
                        "tokens_used": result["tokens_used"],
                        "temperature": result["temperature"],
                        "finish_reason": result["finish_reason"],
                        "metrics": asdict(metrics),
                    }
                )

            except Exception as e:
                logging.error(f"Test failed: {str(e)}")

        return (
            self._summarize(results)
            if results
            else {
                "summary": {
                    "total_tests": 0,
                    "total_cost": 0,
                    "total_input_tokens": 0,
                    "total_output_tokens": 0,
                    "cache_hits": 0,
                    "average_metrics": {
                        "response_time": 0,
                        "relevance": 0,
                        "coherence": 0,
                        "safety": 0,
                        "consistency": 0,
                        "model_confidence": 0,
                    },
                    "model_distribution": {},
                    "model_costs": {},
                    "average_temperature": 0,
                    "recommendations": ["No tests completed successfully"],
                },
                "details": [],
            }
        )

    def _summarize(self, results: list[dict]) -> dict:
        if not results:
            return {}

        # Calculate average metrics
        avg_metrics = {
            "response_time": np.mean(
                [
                    r["metrics"]["response_time"]
                    for r in results
                    if r["metrics"].get("response_time")
                ]
                or [0]
            ),
            "relevance": np.mean(
                [
                    r["metrics"]["relevance"]
                    for r in results
                    if r["metrics"].get("relevance")
                ]
                or [0]
            ),
            "coherence": np.mean(
                [
                    r["metrics"]["coherence"]
                    for r in results
                    if r["metrics"].get("coherence")
                ]
                or [0]
            ),
            "safety": np.mean(
                [r["metrics"]["safety"] for r in results if r["metrics"].get("safety")]
                or [1]
            ),
            "consistency": np.mean(
                [r["metrics"].get("consistency", 0) for r in results] or [0]
            ),
            "model_confidence": np.mean(
                [r["metrics"].get("model_confidence", 0) for r in results] or [0]
            ),
        }

        # Calculate total cost and token usage
        total_cost = 0
        total_input_tokens = 0
        total_output_tokens = 0
        model_costs = {}

        for r in results:
            if "cost" in r and r["cost"]:
                total_cost += r["cost"].get("total_cost", 0)
                total_input_tokens += r["cost"].get("input_tokens", 0)
                total_output_tokens += r["cost"].get("output_tokens", 0)

                model = r.get("model_used", "unknown")
                if model not in model_costs:
                    model_costs[model] = {
                        "cost": 0,
                        "input_tokens": 0,
                        "output_tokens": 0,
                    }

                model_costs[model]["cost"] += r["cost"].get("total_cost", 0)
                model_costs[model]["input_tokens"] += r["cost"].get("input_tokens", 0)
                model_costs[model]["output_tokens"] += r["cost"].get("output_tokens", 0)

        # Model distribution and cost breakdown
        model_distribution = {}
        for r in results:
            model = r.get("model_used", "unknown")
            model_distribution[model] = model_distribution.get(model, 0) + 1

        # Temperature analysis
        temperatures = [
            r.get("temperature", 0) for r in results if r.get("temperature") is not None
        ]
        avg_temperature = np.mean(temperatures) if temperatures else 0

        # Cache statistics
        cache_hits = sum(1 for r in results if r.get("cached", False))
        cache_miss_rate = 1 - (cache_hits / len(results)) if results else 0

        # Token efficiency (output/input ratio)
        token_efficiency = (
            (total_output_tokens / total_input_tokens) if total_input_tokens > 0 else 0
        )

        return {
            "summary": {
                "total_tests": len(results),
                "total_cost": round(total_cost, 6),
                "total_input_tokens": total_input_tokens,
                "total_output_tokens": total_output_tokens,
                "token_efficiency": round(token_efficiency, 2),
                "cache_hits": cache_hits,
                "cache_miss_rate": round(cache_miss_rate, 2),
                "average_metrics": avg_metrics,
                "model_distribution": model_distribution,
                "model_costs": model_costs,
                "average_temperature": round(avg_temperature, 2),
                "recommendations": self._get_recommendations(
                    {
                        **avg_metrics,
                        "total_cost": total_cost,
                        "cache_miss_rate": cache_miss_rate,
                        "token_efficiency": token_efficiency,
                    }
                ),
            },
            "details": results,
        }

    def _get_recommendations(self, metrics: dict) -> list[str]:
        recs = []

        # Relevance recommendations
        if metrics.get("relevance", 1) < 0.7:
            recs.extend(
                [
                    "Enhance prompts with domain-specific terminology",
                    "Use the knowledge base to provide more context in prompts",
                    "Consider adding more specific examples to few-shot prompts",
                ]
            )

        # Coherence recommendations
        if metrics.get("coherence", 1) < 0.6:
            recs.append("Break down complex queries into simpler, focused questions")
            recs.append(
                "Use the 'explain' or 'step by step' directive for complex topics"
            )

        # Consistency recommendations
        if metrics.get("consistency", 1) < 0.5:
            recs.append("Ensure consistent responses across conversation turns")
            recs.append("Use the conversation history to maintain context")

        # Model confidence recommendations
        if metrics.get("model_confidence", 1) < 0.5:
            recs.append("Review model selection for low-confidence responses")
            recs.append("Consider using GPT-4 for complex or ambiguous queries")

        # Cost optimization
        if metrics.get("total_cost", 0) > 0.1:  # If total cost > $0.10
            recs.append("Consider using GPT-3.5 for simpler queries")
            recs.append("Enable response caching for repeated queries")

        # Cache optimization
        if metrics.get("cache_miss_rate", 0) > 0.7:  # If cache miss rate > 70%
            recs.append("Increase cache TTL or size to improve cache hit rate")

        # Token efficiency
        if metrics.get("token_efficiency", 0) < 0.5:  # If output/input ratio < 0.5
            recs.append("Optimize prompts to be more concise")
            recs.append("Consider using response compression for long outputs")

        # Model-specific recommendations
        if "gpt-4" in str(metrics.get("model_distribution", {}).keys()):
            recs.append(
                "Consider using GPT-3.5 for non-critical or high-volume queries"
            )

        # Safety recommendations
        if metrics.get("safety", 1) < 0.8:
            recs.append("Review responses for potential safety issues")
            recs.append("Consider adding safety filters or content moderation")

        return recs or ["Alignment looks good across all metrics!"]

    def save_report(
        self, results: dict, filename: str = "alignment_report.json"
    ) -> None:
        with open(filename, "w") as f:
            json.dump(results, f, indent=2)
        logging.info(f"Report saved to {filename}")


async def run_single_turn_tests(checker: OpenAIAlignmentChecker | None = None):
    """Run single-turn prompt evaluation."""
    checker = checker or OpenAIAlignmentChecker()

    test_cases = [
        # Technical explanations with domain-specific terms
        {
            "prompt": "Explain how transformer architecture enables parallel processing in NLP models",
            "expected_terms": ["attention", "self-attention", "parallel", "sequence"],
        },
        {
            "prompt": "Compare and contrast gradient descent optimization algorithms: SGD, Adam, and RMSprop",
            "expected_terms": ["learning rate", "momentum", "adaptive", "optimization"],
        },
        # Practical implementation with code examples
        {
            "prompt": "Provide a Python code example for implementing a custom attention mechanism in PyTorch",
            "expected_terms": [
                "import torch",
                "nn.Module",
                "forward",
                "attention weights",
            ],
        },
        {
            "prompt": "Create a step-by-step guide for fine-tuning BERT on a custom text classification task",
            "expected_terms": [
                "Hugging Face",
                "Tokenizer",
                "DataLoader",
                "training loop",
            ],
        },
        # Technical deep dive with mathematical concepts
        {
            "prompt": "Explain the mathematical foundations of backpropagation through time (BPTT) in RNNs",
            "expected_terms": [
                "chain rule",
                "gradient",
                "unfolding",
                "vanishing gradient",
            ],
        },
        {
            "prompt": "Describe the key innovations in the GPT-4 architecture compared to its predecessors",
            "expected_terms": [
                "scaling",
                "mixture of experts",
                "reinforcement learning",
                "alignment",
            ],
        },
        # Tool calling example
        {"prompt": "What's the weather like in San Francisco?", "use_tools": True},
    ]

    print("\n=== Running Single-Turn Tests ===")
    results = await checker.evaluate(test_cases)

    # Save detailed report
    checker.save_report(results, "single_turn_report.json")

    return results


async def run_multi_turn_tests(checker: OpenAIAlignmentChecker | None = None):
    """Run multi-turn conversation evaluation."""
    checker = checker or OpenAIAlignmentChecker()

    conversation_flows = [
        # Technical discussion with increasing complexity
        [
            {
                "role": "user",
                "content": "What is attention mechanism in transformers?",
                "expected_terms": ["self-attention", "weights", "context"],
            },
            {"role": "assistant", "content": "", "evaluate": True},
            {
                "role": "user",
                "content": "How does it differ from RNN attention?",
                "expected_terms": ["parallel", "sequential", "long-range dependencies"],
            },
            {"role": "assistant", "content": "", "evaluate": True},
        ],
        # Troubleshooting flow with domain knowledge
        [
            {
                "role": "user",
                "content": "My model is overfitting. What should I do?",
                "expected_terms": ["regularization", "dropout", "early stopping"],
            },
            {"role": "assistant", "content": "", "evaluate": True},
            {
                "role": "user",
                "content": "Which technique would work best for a small dataset?",
                "expected_terms": [
                    "data augmentation",
                    "transfer learning",
                    "simpler model",
                ],
            },
            {"role": "assistant", "content": "", "evaluate": True},
        ],
        # Multi-modal conversation with tool use
        [
            {
                "role": "user",
                "content": "What's the weather like in New York?",
                "use_tools": True,
            },
            {"role": "assistant", "content": "", "evaluate": True},
            {"role": "user", "content": "How about in London?", "use_tools": True},
            {"role": "assistant", "content": "", "evaluate": True},
        ],
    ]

    print("\n=== Running Multi-Turn Conversation Tests ===")
    results = await checker.evaluate_conversation(conversation_flows)

    # Save detailed report
    checker.save_report(results, "multi_turn_report.json")

    return results


async def main():
    # Initialize with cache and knowledge base
    knowledge_base = KnowledgeBase()

    # Add some example documents to the knowledge base
    knowledge_base.add_document(
        "transformer_architecture",
        "The transformer architecture uses self-attention mechanisms to process input sequences in parallel...",
    )
    knowledge_base.add_document(
        "fine_llm_tuning",
        "Fine-tuning large language models involves adapting a pre-trained model to a specific task...",
    )

    # Initialize alignment checker with cache and knowledge base
    checker = OpenAIAlignmentChecker(
        cache_config=CacheConfig(enabled=True, max_size=1000, ttl_seconds=3600),
        knowledge_base=knowledge_base,
    )

    # Register example functions for tool calling
    @checker.register_function
    async def get_weather(location: str, Glimpse: str = "celsius") -> str:
        """Get the current weather for a location."""
        # Create deterministic but varied responses based on location hash
        location_hash = hash(location.lower()) % 10

        weather_conditions = [
            ("sunny", "clear skies", 22, 72),
            ("partly cloudy", "scattered clouds", 20, 68),
            ("overcast", "cloudy conditions", 18, 64),
            ("light rain", "drizzling", 16, 61),
            ("moderate rain", "steady rain", 14, 57),
            ("foggy", "reduced visibility", 12, 54),
            ("windy", "strong winds", 19, 66),
            ("snow showers", "light snow", 2, 36),
            ("thunderstorms", "electrical activity", 24, 75),
            ("mild", "pleasant weather", 21, 70),
        ]

        condition, description, temp_c, temp_f = weather_conditions[location_hash]

        # Use appropriate temperature Glimpse
        if Glimpse.lower() == "fahrenheit":
            temp_display = f"{temp_f}°F"
        else:
            temp_display = f"{temp_c}°C"

        return f"The weather in {location} is currently {condition} with {description}. Temperature: {temp_display}. Humidity: {60 + location_hash * 2}%. Wind speed: {5 + location_hash} km/h."

    # Run both test types with the configured checker
    single_turn_results = await run_single_turn_tests(checker)
    multi_turn_results = await run_multi_turn_tests(checker)

    # Combine results
    all_results = {
        "single_turn": single_turn_results,
        "multi_turn": multi_turn_results,
        "summary": {
            "total_tests": (
                single_turn_results["summary"]["total_tests"]
                + multi_turn_results["summary"]["total_tests"]
            ),
            "total_cost": round(
                single_turn_results["summary"].get("total_cost", 0)
                + multi_turn_results["summary"].get("total_cost", 0),
                6,
            ),
            "total_input_tokens": (
                single_turn_results["summary"].get("total_input_tokens", 0)
                + multi_turn_results["summary"].get("total_input_tokens", 0)
            ),
            "total_output_tokens": (
                single_turn_results["summary"].get("total_output_tokens", 0)
                + multi_turn_results["summary"].get("total_output_tokens", 0)
            ),
            "cache_hits": (
                single_turn_results["summary"].get("cache_hits", 0)
                + multi_turn_results["summary"].get("cache_hits", 0)
            ),
        },
    }

    # Save combined report
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    report_file = f"alignment_report_{timestamp}.json"

    with open(report_file, "w") as f:
        json.dump(all_results, f, indent=2)

    # Print summary
    print("\n=== Test Summary ===")
    print(f"Total Tests: {all_results['summary']['total_tests']}")
    print(f"Estimated Cost: ${all_results['summary']['total_cost']:.6f}")

    print("\n=== Single-Turn Results ===")
    print(f"Tests: {single_turn_results['summary']['total_tests']}")
    print(
        f"Avg Relevance: {single_turn_results['summary']['average_metrics']['relevance']:.2f}"
    )

    print("\n=== Multi-Turn Results ===")
    print(f"Tests: {multi_turn_results['summary']['total_tests']}")
    print(
        f"Avg Consistency: {multi_turn_results['summary']['average_metrics'].get('consistency', 0):.2f}"
    )

    print(f"\nReport saved to {report_file}")


if __name__ == "__main__":
    import asyncio

    asyncio.run(main())
