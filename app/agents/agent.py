import logging
import re

import openai

from app.agents.models import AgentConfig, ConversationHistory

logger = logging.getLogger(__name__)

_INJECTION_PATTERNS = [
    re.compile(r"ignore\s+(all\s+)?previous\s+instructions", re.IGNORECASE),
    re.compile(r"ignore\s+(all\s+)?above", re.IGNORECASE),
    re.compile(r"you\s+are\s+now\s+(a|an)\b", re.IGNORECASE),
    re.compile(r"system\s*:\s*", re.IGNORECASE),
    re.compile(r"\bDAN\s+mode\b", re.IGNORECASE),
    re.compile(r"pretend\s+you\s+(are|can)\b", re.IGNORECASE),
    re.compile(r"act\s+as\s+if\s+you\b", re.IGNORECASE),
    re.compile(r"override\s+(your\s+)?instructions", re.IGNORECASE),
]


def sanitize_prompt(text: str) -> str:
    """Strip known prompt-injection patterns from user input.

    Conservative blocklist approach: neutralizes role-override attempts
    without breaking legitimate queries.
    """
    sanitized = text
    for pattern in _INJECTION_PATTERNS:
        sanitized = pattern.sub("[filtered]", sanitized)
    return sanitized


class Agent:
    """Base agent class"""

    def __init__(self, config: AgentConfig):
        self.config = config
        self.history = ConversationHistory(agent_name=config.name)
        logger.info(f"Agent '{config.name}' initialized")

    async def process(self, user_input: str) -> str:
        """Process user input and return response"""
        try:
            user_input = sanitize_prompt(user_input)

            # Add user message to history
            self.history.add_message("user", user_input)

            # Prepare messages for API
            messages = [
                {"role": "system", "content": self.config.instructions},
                *self.history.get_messages_for_api(),
            ]

            # Get response from OpenAI directly (no wrapper)
            client = openai.AsyncOpenAI()
            response = await client.chat.completions.create(
                messages=messages,
                model=self.config.model,
                temperature=self.config.model_settings.temperature,
                max_tokens=self.config.model_settings.max_tokens,
            )

            assistant_message = response.choices[0].message.content

            # Add assistant response to history
            self.history.add_message("assistant", assistant_message)

            logger.info(f"Agent '{self.config.name}' processed input successfully")
            return assistant_message

        except Exception as e:
            logger.error(f"Agent '{self.config.name}' error: {str(e)}")
            raise

    def reset_history(self):
        """Reset conversation history"""
        self.history = ConversationHistory(agent_name=self.config.name)
        logger.info(f"Agent '{self.config.name}' history reset")

    def get_history(self) -> ConversationHistory:
        """Get conversation history"""
        return self.history
