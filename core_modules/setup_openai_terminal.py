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
OpenAI Terminal API Setup Script
Automated setup for OpenAI API terminal usage
"""

import os
import platform
import subprocess
import sys


def run_command(cmd, description=""):
    """Run command with error handling"""
    print(f"🔧 {description}")
    try:
        if isinstance(cmd, str):
            cmd = cmd.split()
        result = subprocess.run(cmd, capture_output=True, text=True, check=True)
        print("✅ Success")
        return result.stdout.strip()
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed: {e.stderr}")
        return None
    except FileNotFoundError:
        print(f"❌ Command not found: {cmd[0]}")
        return None


def check_prerequisites():
    """Check Python and pip"""
    print("🔍 Checking prerequisites...")

    # Check Python
    python_version = f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}"
    print(f"✅ Python {python_version} detected")

    # Check pip
    try:
        pip_version = run_command("pip --version", "Checking pip")
        if pip_version:
            print("✅ Pip available")
    except:
        print("❌ Pip not found. Please install pip first.")
        return False

    return True


def install_openai_sdk():
    """Install OpenAI SDK"""
    print("\n📦 Installing OpenAI SDK...")
    return run_command("pip install openai", "Installing openai package")


def set_api_key():
    """Guide user to set API key"""
    print("\n🔑 API Key Setup")
    print("-" * 20)
    print("Get your API key from: https://platform.openai.com/account/api-keys")
    print()

    api_key = input("Enter your OpenAI API key (or press Enter to skip): ").strip()

    if api_key:
        # Set environment variable
        if platform.system() == "Windows":
            # Windows PowerShell/command prompt
            os.system(f'setx OPENAI_API_KEY "{api_key}"')
            print("✅ Environment variable set for Windows")
            print("   Note: Restart your terminal for changes to take effect")
        else:
            # macOS/Linux
            shell_rc = (
                os.path.expanduser("~/.bashrc")
                if os.path.exists(os.path.expanduser("~/.bashrc"))
                else os.path.expanduser("~/.zshrc")
            )
            with open(shell_rc, "a") as f:
                f.write(f'\nexport OPENAI_API_KEY="{api_key}"\n')
            print(f"✅ Added to {shell_rc}")
            print("   Run: source ~/.bashrc (or restart terminal)")

        # Set for current session
        os.environ["OPENAI_API_KEY"] = api_key
        print("✅ API key set for current session")
        return True
    else:
        print("⚠️ API key not set. You'll need to set OPENAI_API_KEY manually")
        return False


def test_installation():
    """Test OpenAI CLI installation"""
    print("\n🧪 Testing Installation...")
    result = run_command("python -m openai --help", "Testing OpenAI CLI")
    return result is not None


def run_api_test():
    """Run a simple API test"""
    print("\n🚀 Running API Test...")

    # Simple completion test
    test_cmd = [
        "python",
        "-m",
        "openai",
        "api",
        "completions.create",
        "-m",
        "gpt-3.5-turbo-instruct",
        "-p",
        "Say 'Hello from OpenAI API!' and nothing else.",
    ]

    print('Testing: python -m openai api completions.create -m gpt-3.5-turbo-instruct -p "Say Hello"')
    result = run_command(test_cmd, "Running completion test")

    if result:
        print("✅ API test successful!")
        print("📝 Response preview:")
        # Parse the JSON response to show the text
        try:
            import json

            response_data = json.loads(result)
            if "choices" in response_data and response_data["choices"]:
                text = response_data["choices"][0].get("text", "").strip()
                print(f'   "{text}"')
        except:
            print("   (Could not parse response)")
    else:
        print("❌ API test failed")
        print("   Check your API key and internet connection")

    return result is not None


def create_example_script():
    """Create example script for common API calls"""
    script_content = """#!/bin/bash
# OpenAI API Examples Script
# Run various OpenAI API calls from terminal

echo "🤖 OpenAI API Examples"
echo "======================"

# Set your API key (replace with actual key)
export OPENAI_API_KEY="sk-your-api-key-here"

echo "1. Text Completion:"
echo "python -m openai api completions.create -m gpt-3.5-turbo-instruct -p \"Write a haiku about coding\""
python -m openai api completions.create -m gpt-3.5-turbo-instruct -p "Write a haiku about coding" | head -20

echo -e "\n2. Chat Completion:"
echo "python -m openai api chat.completions.create -m gpt-4 -g \"You are a helpful assistant.\" -g \"Explain recursion in simple terms\""
python -m openai api chat.completions.create -m gpt-4 -g "You are a helpful assistant." -g "Explain recursion in simple terms" | head -20

echo -e "\n3. Embeddings:"
echo "python -m openai api embeddings.create -m text-embedding-ada-002 -i \"Artificial intelligence\""
python -m openai api embeddings.create -m text-embedding-ada-002 -i "Artificial intelligence" | head -10

echo -e "\n✅ Examples completed!"
"""

    script_name = "openai_examples.sh" if platform.system() != "Windows" else "openai_examples.ps1"

    try:
        with open(script_name, "w") as f:
            if platform.system() == "Windows":
                # Convert to PowerShell
                script_content = script_content.replace("#!/bin/bash", "# PowerShell OpenAI Examples")
                script_content = script_content.replace("export ", "$env:")
                script_content = script_content.replace("python -m", "python -m")
                f.write(script_content)
            else:
                f.write(script_content)

        # Make executable on Unix
        if platform.system() != "Windows":
            os.chmod(script_name, 0o755)

        print(f"✅ Created example script: {script_name}")
        print(f"   Edit it with your API key and run: ./{script_name}")

    except Exception as e:
        print(f"❌ Failed to create example script: {e}")


def main():
    print("🚀 OpenAI Terminal API Setup")
    print("=" * 40)
    print("This script will set up OpenAI API for terminal usage")
    print()

    # Check prerequisites
    if not check_prerequisites():
        print("❌ Prerequisites not met. Please install Python and pip first.")
        sys.exit(1)

    # Install SDK
    if not install_openai_sdk():
        print("❌ Failed to install OpenAI SDK")
        sys.exit(1)

    # Set API key
    api_key_set = set_api_key()

    # Test installation
    if not test_installation():
        print("❌ OpenAI CLI not working properly")
        sys.exit(1)

    # Test API (only if key was set)
    if api_key_set:
        api_test_passed = run_api_test()
    else:
        print("⚠️ Skipping API test (no API key provided)")
        api_test_passed = False

    # Create examples
    create_example_script()

    print("\n" + "=" * 40)
    print("🎉 SETUP COMPLETE!")
    print("=" * 40)

    if api_key_set and api_test_passed:
        print("✅ Full setup successful!")
        print("   You can now use OpenAI API from terminal")
    elif api_key_set:
        print("⚠️ Setup mostly complete, but API test failed")
        print("   Check your API key and try again")
    else:
        print("⚠️ Setup complete, but API key not configured")
        print("   Set OPENAI_API_KEY and test with the examples")

    print()
    print("📚 Next Steps:")
    print("   1. Restart your terminal (to load environment variables)")
    print("   2. Run: python -m openai --help")
    print('   3. Try: python -m openai api completions.create -m gpt-3.5-turbo-instruct -p "Hello world"')


if __name__ == "__main__":
    main()
