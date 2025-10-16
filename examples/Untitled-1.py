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

"""Run this model in Python

> pip install azure-ai-inference
"""

import os

from azure.ai.inference import ChatCompletionsClient
from azure.ai.inference.models import ToolMessage
from azure.core.credentials import AzureKeyCredential

# To authenticate with the model you will need to generate a personal access token (PAT)
# in your GitHub settings.
# Create your PAT token by following instructions here:
# https://docs.github.com/en/authentication/keeping-your-account-and-data-secure/managing-your-personal-access-tokens
client = ChatCompletionsClient(
    endpoint="https://models.github.ai/inference",
    credential=AzureKeyCredential(os.environ["GITHUB_TOKEN"]),
    api_version="2024-08-01-preview",
)

messages = []

tools = []

response_format = "text"

MAX_ROUNDS = 20  # Safety guard to prevent infinite loops

for _round_idx in range(MAX_ROUNDS):
    response = client.complete(
        messages=messages,
        model="openai/gpt-4.1",
        tools=tools,
        response_format=response_format,
        temperature=1,
        top_p=1,
    )

    if response.choices[0].message.tool_calls:
        print(response.choices[0].message.tool_calls)
        messages.append(response.choices[0].message)
        for tool_call in response.choices[0].message.tool_calls:
            messages.append(
                ToolMessage(
                    content=locals()[tool_call.function.name](),
                    tool_call_id=tool_call.id,
                )
            )
    else:
        print(f"[Model Response] {response.choices[0].message.content}")
        break
else:
    print("[WARN] Maximum iterations reached without terminating. Check tool behavior.")
