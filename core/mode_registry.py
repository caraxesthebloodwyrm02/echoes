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
ModeRegistry - Central registry for all mode handlers
"""

from abc import ABC, abstractmethod
from typing import Any, Dict, Optional


class ModeHandler(ABC):
    """Base class for mode handlers"""

    def __init__(self):
        self.mode_name = "base"
        self.description = "Base mode handler"
        self.config = {}

    @abstractmethod
    def format_response(self, response: Dict[str, Any], context: Dict[str, Any]) -> str:
        """Format response according to mode specifications"""

    @abstractmethod
    def get_mode_config(self) -> Dict[str, Any]:
        """Get mode-specific configuration"""

    def preprocess_prompt(self, prompt: str, context: Dict[str, Any]) -> str:
        """Preprocess prompt before routing (optional override)"""
        return prompt

    def postprocess_response(self, response: str, context: Dict[str, Any]) -> str:
        """Postprocess response after generation (optional override)"""
        return response


class ModeRegistry:
    """Registry for managing mode handlers"""

    def __init__(self):
        self.modes: Dict[str, ModeHandler] = {}
        self.default_mode = "conversational"

    def register_mode(self, mode_name: str, handler: ModeHandler):
        """Register a mode handler"""
        handler.mode_name = mode_name
        self.modes[mode_name] = handler

    def get_mode(self, mode_name: str) -> Optional[ModeHandler]:
        """Get a mode handler by name"""
        return self.modes.get(mode_name)

    def get_default_mode(self) -> ModeHandler:
        """Get the default mode handler"""
        return self.modes.get(self.default_mode)

    def list_modes(self) -> Dict[str, str]:
        """List all registered modes with descriptions"""
        return {name: handler.description for name, handler in self.modes.items()}

    def set_default_mode(self, mode_name: str):
        """Set the default mode"""
        if mode_name in self.modes:
            self.default_mode = mode_name
        else:
            raise ValueError(f"Mode '{mode_name}' not registered")
