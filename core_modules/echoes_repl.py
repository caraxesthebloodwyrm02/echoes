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

import logging


class EchoesREPL:
    def __init__(self, config):
        self.config = config
        self.logger = logging.getLogger(__name__)
        self.current_mode = "main"
        self.commands = {
            "main": self._handle_main_command,
            "batch": self._handle_batch_command,
            "assistant": self._handle_assistant_command,
        }

    def run(self):
        self._print_welcome()
        while True:
            try:
                prompt = self._get_prompt()
                user_input = input(prompt).strip()
                if not user_input:
                    continue
                if user_input.startswith("/"):
                    self._handle_command(user_input)
                else:
                    handler = self.commands.get(self.current_mode, self._handle_main_command)
                    handler(user_input)
            except (KeyboardInterrupt, EOFError):
                print("\nGoodbye!")
                break
            except Exception as e:
                self.logger.error(f"Error: {e}")
                print("Type /help for assistance or /quit to exit.\n")

    def _print_welcome(self):
        print("Welcome to Echoes Platform")

    def _get_prompt(self):
        return f"echoes/{self.current_mode}> "

    def _handle_command(self, command):
        pass

    def _handle_main_command(self, command):
        pass

    def _handle_batch_command(self, command):
        pass

    def _handle_assistant_command(self, command):
        pass
