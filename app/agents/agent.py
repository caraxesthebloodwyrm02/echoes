import logging
import openai
from app.agents.models import AgentConfig, ConversationHistory

logger = logging.getLogger(__name__)


class Agent:
    """Base agent class"""

    def __init__(self, config: AgentConfig):
        self.config = config
        self.history = ConversationHistory(agent_name=config.name)
        logger.info(f"Agent '{config.name}' initialized")

    async def process(self, user_input: str) -> str:
        """Process user input and return response"""
        try:
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
