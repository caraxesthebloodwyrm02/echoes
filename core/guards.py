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

import html
import os
import re
import time

import backoff
from pydantic import BaseModel, validator


class Prompt(BaseModel):
    text: str

    @validator("text")
    def no_injection(cls, v):
        # Block obvious jailbreak patterns
        if re.search(r"(ignore|disregard|previous|system)", v, re.I):
            raise ValueError("Potential prompt injection detected")
        return html.escape(v)[:800]


class CircuitBreaker:
    def __init__(self, max_failures=3, reset_timeout=60):
        self.failures, self.last_fail = 0, 0
        self.max_failures, self.reset_timeout = max_failures, reset_timeout

    def call(self, func, *a, **k):
        if (
            time.time() - self.last_fail < self.reset_timeout
            and self.failures >= self.max_failures
        ):
            raise RuntimeError("Circuit breaker open")
        try:
            r = func(*a, **k)
            self.failures = 0
            return r
        except Exception as e:
            self.failures += 1
            self.last_fail = time.time()
            raise e


@backoff.on_exception(backoff.expo, Exception, max_tries=3)
def openai_safe_call(messages):
    import openai

    openai.api_key = os.getenv("OPENAI_API_KEY")
    return openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=messages,
        temperature=0,
        max_tokens=250,
    )
