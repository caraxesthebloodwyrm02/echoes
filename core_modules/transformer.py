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

# src/modules/transformer.py
import os
import sys

# Add project root to path for imports
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, PROJECT_ROOT)

from utils.openai_integration import get_openai_integration


def transform_text(task, text, model=None, max_tokens=300):
    """
    Perform a transformation using our streamlined OpenAI integration.
    Returns (result_text, usage_dict, model_used)
    """
    # Get our OpenAI integration instance
    openai_integration = get_openai_integration()

    if not openai_integration.is_configured:
        raise RuntimeError("OpenAI integration not configured. Check OPENAI_API_KEY.")

    # Use model from integration if not specified
    if model is None:
        model = openai_integration.model

    # Create system prompt based on task
    system_prompts = {
        "summarize": "You are an expert at creating concise, accurate summaries. Summarize the given text while preserving all key information and main points.",
        "rephrase": "You are a skilled writer who can rephrase text while maintaining the original meaning. Rephrase the given text to make it clearer and more engaging.",
        "actions": "You are an analyst who extracts actionable items from text. Identify all tasks, actions, and recommendations mentioned in the text. Format them as a clear, numbered list.",
        "analyze": "You are an expert analyst. Provide a detailed analysis of the given text, including key themes, insights, and observations.",
    }

    system_prompt = system_prompts.get(task.lower(), f"You are a precise text transformer that can {task} any input.")

    try:
        # Use our integration to make the API call with custom messages
        response = openai_integration.create_chat_completion(
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": text},
            ],
            model=model,
            temperature=0.3,  # Lower temperature for more consistent results
            max_tokens=max_tokens,
        )

        if response is None:
            raise RuntimeError("OpenAI API call failed - no response received")

        # Create usage dict (our integration doesn't return usage yet, so create a basic one)
        usage = {
            "prompt_tokens": len(text.split()) * 1.3,  # Rough estimate
            "completion_tokens": len(response.split()) * 1.3,  # Rough estimate
            "total_tokens": (len(text.split()) + len(response.split())) * 1.3,
        }

        return response.strip(), usage, model

    except Exception as e:
        raise RuntimeError(f"Text transformation failed: {e}")
