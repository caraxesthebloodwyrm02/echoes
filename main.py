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
Echoes Main REPL System
========================

Interactive command-line interface for the Echoes platform featuring:
- AI Assistant for natural language interactions
- Batch Processing with budget protection
- Task automation and orchestration
- Integrated tools and workflows

Commands:
  /help              - Show available commands
  /batch             - Batch processing menu
  /assistant         - Start AI assistant mode
  /budget            - Check budget status
  /files             - Show input/output files
  /quit              - Exit the system

Batch Processing Commands:
  /batch dry-run     - Run batch processor in dry-run mode
  /batch summarize   - Batch summarize all input files
  /batch rephrase    - Batch rephrase all input files
  /batch actions     - Extract actions from all input files
  /batch status      - Show batch processing status
"""

import os
import subprocess
import sys
from pathlib import Path

from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Add src to path for imports
src_path = Path(__file__).parent / "src"
sys.path.insert(0, str(src_path))

try:
    from utils.budget_guard import check_budget, load_budget
except ImportError:
    print("❌ Error: Batch processing modules not found. Please run from project root.")
    sys.exit(1)


class EchoesREPL:
    """Main REPL system for Echoes platform."""

    def __init__(self):
        self.current_mode = "main"
        self.commands = {
            "main": self._handle_main_command,
            "batch": self._handle_batch_command,
            "assistant": self._handle_assistant_command,
        }

    def run(self):
        """Main REPL loop."""
        self._print_welcome()

        while True:
            try:
                # Show prompt based on current mode
                if self.current_mode == "main":
                    prompt = "echoes> "
                elif self.current_mode == "batch":
                    prompt = "echoes/batch> "
                elif self.current_mode == "assistant":
                    prompt = "echoes/assistant> "
                else:
                    prompt = "echoes> "

                user_input = input(prompt).strip()

                if not user_input:
                    continue

                # Handle mode switching
                if user_input.startswith("/"):
                    self._handle_command(user_input)
                else:
                    # Handle mode-specific input
                    handler = self.commands.get(
                        self.current_mode, self._handle_main_command
                    )
                    handler(user_input)

            except KeyboardInterrupt:
                print("\n\nGoodbye!")
                break
            except EOFError:
                print("\n\nGoodbye!")
                break
            except Exception as e:
                print(f"Error: {e}")
                print("Type /help for assistance or /quit to exit.\n")

    def _print_welcome(self):
        """Print welcome banner."""
        banner = """
================================================================================
                    ECHOES PLATFORM
================================================================================

  Multi-Modal AI Platform with Batch Processing & Budget Control

  Type /help for commands or start chatting naturally
  Use /batch for batch processing operations
  Use /assistant for AI assistant mode

================================================================================
        """
        print(banner)

        # Show system status
        self._show_system_status()

    def _show_system_status(self):
        """Show current system status."""
        print("System Status:")
        print("  * Environment loaded")
        print("  * Batch processing ready")
        print("  * Budget protection active")

        # Show budget status
        ok, remaining, data = check_budget()
        budget_status = "ACTIVE" if ok else "EXHAUSTED"
        print(
            f"  {budget_status} Budget: ${remaining:.2f} remaining (${data['spent']:.2f} spent, {data['calls']} calls)"
        )

        # Show file counts
        input_dir = src_path / "data" / "input_samples"
        output_dir = src_path / "data" / "outputs"

        input_count = len(list(input_dir.glob("*.txt"))) if input_dir.exists() else 0
        output_count = len(list(output_dir.glob("*.txt"))) if output_dir.exists() else 0

        print(f"  Files: {input_count} input, {output_count} output")
        print()

    def _handle_command(self, command):
        """Handle slash commands."""
        cmd = command.lower()

        if cmd in ["/quit", "/exit", "quit", "exit"]:
            print("\nGoodbye!")
            sys.exit(0)

        elif cmd == "/help":
            self._show_help()

        elif cmd == "/budget":
            self._show_budget_status()

        elif cmd == "/files":
            self._show_files()

        elif cmd.startswith("/batch"):
            self._handle_batch_command(command)

        elif cmd == "/assistant":
            self._enter_assistant_mode()

        elif cmd == "/main":
            self.current_mode = "main"
            print("Switched to main mode")

        else:
            print(f"Unknown command: {command}")
            print("Type /help for available commands")

    def _handle_main_command(self, input_text):
        """Handle main mode input - could be natural language or direct commands."""
        # For now, treat as command or show help
        if input_text.lower() in ["help", "h", "?"]:
            self._show_help()
        elif input_text.lower().startswith("batch"):
            self._handle_batch_command(input_text)
        elif input_text.lower().startswith("budget"):
            self._show_budget_status()
        else:
            print("Echoes REPL - Type /help for commands or use /assistant for AI chat")
            print(f"You said: {input_text}")

    def _handle_batch_command(self, command):
        """Handle batch processing commands."""
        parts = command.split()
        subcommand = parts[1] if len(parts) > 1 else ""

        if subcommand == "dry-run":
            self._run_batch_processor(dry_run=True)
        elif subcommand in ["summarize", "rephrase", "actions"]:
            self._run_batch_processor(task=subcommand)
        elif subcommand == "status":
            self._show_batch_status()
        elif subcommand == "":
            self._show_batch_help()
        else:
            print(f"Unknown batch command: {subcommand}")
            self._show_batch_help()

    def _handle_assistant_command(self, input_text):
        """Handle assistant mode input."""
        print("Assistant mode not yet implemented")
        print("Use /main to return to main mode")

    def _show_help(self):
        """Show help information."""
        help_text = """
================================================================================
                           HELP
================================================================================
  MAIN COMMANDS:
    /help              - Show this help message
    /batch             - Batch processing menu
    /assistant         - Start AI assistant mode
    /budget            - Show budget status
    /files             - Show input/output files
    /quit              - Exit the system

  BATCH PROCESSING:
    /batch dry-run     - Test processing without API calls
    /batch summarize   - Summarize all input files
    /batch rephrase    - Rephrase all input files
    /batch actions     - Extract actions from files
    /batch status      - Show batch processing status

  EXAMPLES:
    /batch dry-run     (test without spending)
    /batch summarize   (process all files)
    /budget            (check spending)
================================================================================
        """
        print(help_text)

    def _show_budget_status(self):
        """Show detailed budget status."""
        ok, remaining, data = check_budget()

        status_icon = "ACTIVE" if ok else "EXHAUSTED"
        status_text = "ACTIVE" if ok else "EXHAUSTED"

        print("\nBUDGET STATUS")
        print(f"Status: {status_icon}")
        print(f"Remaining Budget: ${remaining:.2f}")
        print(f"Total Spent: ${data['spent']:.2f}")
        print(f"API Calls: {data['calls']}")
        print(f"Cost per Call: ${data['spent'] / max(data['calls'], 1):.4f}")
        print()

    def _show_files(self):
        """Show input and output files."""
        input_dir = src_path / "data" / "input_samples"
        output_dir = src_path / "data" / "outputs"

        print("INPUT FILES:")
        if input_dir.exists():
            files = list(input_dir.glob("*.txt"))
            if files:
                for f in sorted(files):
                    size = f.stat().st_size
                    print(f"  {f.name} ({size} bytes)")
            else:
                print("  (no .txt files found)")
        else:
            print("  (input directory not found)")

        print("\nOUTPUT FILES:")
        if output_dir.exists():
            files = list(output_dir.glob("*.txt"))
            if files:
                for f in sorted(files):
                    size = f.stat().st_size
                    print(f"  {f.name} ({size} bytes)")
            else:
                print("  (no output files found)")
        else:
            print("  (output directory not found)")
        print()

    def _show_batch_help(self):
        """Show batch processing help."""
        help_text = """
BATCH PROCESSING COMMANDS:
  /batch dry-run     - Test processing without API calls
  /batch summarize   - Summarize all .txt files in input_samples/
  /batch rephrase    - Rephrase all .txt files
  /batch actions     - Extract actionable items from files
  /batch status      - Show current batch processing status

SETUP:
  Place .txt files in src/data/input_samples/
  Outputs will appear in src/data/outputs/

NOTES:
  - Dry-run mode doesn't spend credits
  - Processing stops if budget is exhausted
  - Check /budget for spending status
        """
        print(help_text)

    def _run_batch_processor(self, task="summarize", dry_run=False):
        """Run the batch processor with given parameters."""
        print("Starting batch processing...")
        print(f"   Task: {task}")
        print(f"   Mode: {'DRY RUN' if dry_run else 'LIVE'}")

        # Build command
        cmd = [sys.executable, str(src_path / "batch_processor.py")]
        cmd.append(f"--task={task}")
        if dry_run:
            cmd.append("--dry-run")

        try:
            # Run the batch processor
            result = subprocess.run(cmd, cwd=src_path, capture_output=True, text=True)

            # Show output
            if result.stdout:
                print("\nBATCH PROCESSOR OUTPUT:")
                print(result.stdout)

            if result.stderr:
                print("\nSTDERR:")
                print(result.stderr)

            if result.returncode == 0:
                print("Batch processing completed successfully")
            else:
                print(f"Batch processing failed (exit code: {result.returncode})")

        except Exception as e:
            print(f"Error running batch processor: {e}")

        print()

    def _show_batch_status(self):
        """Show batch processing status."""
        print("BATCH PROCESSING STATUS")
        print("=" * 40)

        # Check directories
        input_dir = src_path / "data" / "input_samples"
        output_dir = src_path / "data" / "outputs"
        log_file = src_path / "logs" / "budget.json"

        dirs_status = []
        dirs_status.append(("Input Directory", input_dir.exists()))
        dirs_status.append(("Output Directory", output_dir.exists()))
        dirs_status.append(("Logs Directory", log_file.parent.exists()))

        for name, exists in dirs_status:
            status = "[OK]" if exists else "[MISSING]"
            print(f"{status} {name}")

        # Show file counts
        input_count = len(list(input_dir.glob("*.txt"))) if input_dir.exists() else 0
        output_count = len(list(output_dir.glob("*.txt"))) if output_dir.exists() else 0

        print("\nFiles:")
        print(f"   Input: {input_count} .txt files")
        print(f"   Output: {output_count} processed files")

        # Show recent budget activity
        if log_file.exists():
            try:
                data = load_budget()
                print("\nRecent Activity:")
                print(
                    f"   Last {min(5, data['calls'])} calls used ${data['spent']:.2f}"
                )
                print(f"   Total Spent: ${data['spent']:.2f}")
                print(f"   API Calls: {data['calls']}")
            except:
                print("   (unable to read budget data)")

        print()

    def _enter_assistant_mode(self):
        """Enter assistant mode (placeholder for now)."""
        print("Assistant mode not yet implemented")
        print("AI Assistant integration coming soon!")
        print("Use /main to return to main menu")
        self.current_mode = "assistant"


def main():
    """Main entry point."""
    # Check for required environment variables
    if not os.environ.get("OPENAI_API_KEY"):
        print("Warning: OPENAI_API_KEY not found in environment")
        print("Batch processing will fail without API key\n")

    # Start REPL
    repl = EchoesREPL()
    repl.run()


if __name__ == "__main__":
    main()
