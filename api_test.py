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

import os

from openai import OpenAI

# Simple API test
api_key = os.getenv("OPENAI_API_KEY") or os.getenv("OPENAI_API_KEY_ECHOES")
print(f"API Key found: {bool(api_key)}")

if api_key:
    client = OpenAI(api_key=api_key)
    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {
                    "role": "user",
                    "content": "Hello, can you respond with 'API_TEST_SUCCESS' if you receive this?",
                }
            ],
            max_tokens=10,
        )
        result = response.choices[0].message.content.strip()
        print(f"API Response: {result}")
        if "API_TEST_SUCCESS" in result.upper():
            print("SUCCESS: API is working!")
        else:
            print("WARNING: API responded but not as expected")
    except Exception as e:
        print(f"API Error: {e}")
else:
    print("ERROR: No API key found")
