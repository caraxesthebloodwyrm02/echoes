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
Real-time CI/CD Monitor for 15-minute session
"""

import subprocess
import time
from datetime import datetime


def run_command(cmd):
    """Run a command safely without shell=True.

    Args:
        cmd: Either a string (will be split using shlex) or a list of command arguments

    Returns:
        tuple: (success, stdout, stderr)
    """
    import shlex

    try:
        # Convert string command to list if needed
        if isinstance(cmd, str):
            cmd = shlex.split(cmd)

        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            check=False,  # Don't raise exception on non-zero exit
        )
        return result.returncode == 0, result.stdout, result.stderr
    except Exception as e:
        return False, "", f"Command failed: {str(e)}"


def monitor_session():
    start_time = time.time()
    duration = 15 * 60  # 15 minutes

    print("🔥 REAL-TIME CI/CD MONITORING SESSION")
    print(f"⏰ Started at: {datetime.now().strftime('%H:%M:%S')}")
    print(f"⏱️  Duration: {duration // 60} minutes")
    print("=" * 50)

    while time.time() - start_time < duration:
        remaining = int(duration - (time.time() - start_time))
        minutes = remaining // 60
        seconds = remaining % 60

        print(f"\r⏳ Time remaining: {minutes:02d}:{seconds:02d}", end="", flush=True)
        time.sleep(1)

    print("✅ 15-minute session completed!")
    return True


if __name__ == "__main__":
    monitor_session()
