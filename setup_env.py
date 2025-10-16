#!/usr/bin/env python3
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

"""
Echoes Environment Setup Helper
Helps configure the environment after critical fixes
"""

import shutil
from pathlib import Path


def main():
    project_root = Path(__file__).parent
    env_template = project_root / ".env.template"
    env_file = project_root / ".env"

    print("Echoes Environment Setup Helper")
    print("=" * 40)

    # Check if .env already exists
    if env_file.exists():
        print("✓ .env file already exists")
        return

    # Copy template to .env
    if env_template.exists():
        shutil.copy(env_template, env_file)
        print("✓ Created .env file from template")
        print()
        print("IMPORTANT: Please edit .env file and add your OpenAI API key:")
        print("  OPENAI_API_KEY=sk-your-actual-api-key-here")
        print()
        print("After updating .env, run:")
        print("  python tools/validate_configuration.py")
    else:
        print("⚠ .env.template not found")
        # Create basic .env file
        env_content = """# Echoes Environment Configuration
OPENAI_API_KEY=your-api-key-here
OPENAI_MODEL=gpt-4o-mini
OPENAI_MAX_RETRIES=3
OPENAI_TIMEOUT=30
APP_ENV=development
DEBUG=true
"""
        env_file.write_text(env_content)
        print("✓ Created basic .env file")
        print("  Please edit it with your actual OpenAI API key")


if __name__ == "__main__":
    main()
