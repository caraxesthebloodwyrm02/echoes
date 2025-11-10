"""
Batching helpers for Glimpse to reduce OpenAI API calls.
Groups similar drafts and issues combined requests when possible.
"""

import asyncio
import logging
from typing import List, Tuple, Any
import openai
from glimpse.Glimpse import Draft

logger = logging.getLogger(__name__)


def can_batch(drafts: List[Draft]) -> bool:
    """
    Simple heuristic: allow batching if all drafts share the same goal
    and constraints, and the total input length is reasonable.
    """
    if not drafts:
        return False
    goals = {d.goal for d in drafts}
    constraints = {d.constraints for d in drafts}
    total_len = sum(len(d.input_text) for d in drafts)
    return len(goals) == 1 and len(constraints) == 1 and total_len < 4000


async def batch_chat_completion(
    messages_batch: List[List[dict]],
    model: str,
    temperature: float,
    max_tokens: int | None,
) -> List[dict]:
    """
    Naive batch implementation: run requests concurrently but limit concurrency.
    Returns responses in the same order as inputs.
    Direct OpenAI API calls - bypassing the wrapper.
    """
    # Create AsyncOpenAI client directly (no wrapper)
    client = openai.AsyncOpenAI()

    # Limit concurrency to avoid rate limits
    semaphore = asyncio.Semaphore(5)

    async def call_one(messages):
        async with semaphore:
            # Direct API call - bypassing the wrapper
            response = await client.chat.completions.create(
                messages=messages,
                model=model,
                temperature=temperature,
                max_tokens=max_tokens,
            )
            # Return compatible dict format
            return response.model_dump()

    tasks = [call_one(messages) for messages in messages_batch]
    return await asyncio.gather(*tasks, return_exceptions=True)


def construct_batch_prompt(drafts: List[Draft]) -> Tuple[List[List[dict]], List[int]]:
    """
    Convert a list of drafts into a list of message lists and return the slice indices.
    Each draft gets its own user message in a shared system context.
    """
    if not drafts:
        return [], []
    system_msg = {
        "role": "system",
        "content": (
            "You are a helpful assistant. For each user input below, provide a concise response "
            "that fulfills the shared goal and respects any constraints. Separate responses with a line break."
        ),
    }
    # Create a single combined prompt with numbered inputs
    combined_user = "\n".join(f"{i+1}. {d.input_text}" for i, d in enumerate(drafts))
    shared_goal = drafts[0].goal
    shared_constraints = drafts[0].constraints
    user_content = f"Goal: {shared_goal}\nConstraints: {shared_constraints}\n\nInputs:\n{combined_user}"
    user_msg = {"role": "user", "content": user_content}
    # For simplicity, we return one combined messages list; callers can split responses later.
    return [[system_msg, user_msg]], [len(drafts)]
