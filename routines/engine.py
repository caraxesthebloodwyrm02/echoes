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

from typing import Any, Callable, Dict, List


class RoutineEngine:
    def __init__(self) -> None:
        self.steps: List[str] = [
            "summarize_last_session",
            "scaffold_and_discuss_gaps",
            "real_world_referencing",
            "trust_process",
            "scope_focus",
            "assign_mixture_of_experts",
            "diversify_and_allocate",
            "run_parallel_workflows",
            "merge_parallel_outputs",
            "summarize_and_document",
        ]

    def run(self, handlers: Dict[str, Callable[[], Any]]) -> List[Any]:
        results: List[Any] = []
        for step in self.steps:
            if step in handlers:
                results.append(handlers[step]())
        return results


def example_handlers_with_macro() -> Dict[str, Callable[[], Any]]:
    """Provide example handlers wiring to macro workflow for integration tests/demos."""
    from workflows.macro import macro_parallel, merge_outputs

    def run_parallel_workflows() -> Any:
        layers = {
            "big": lambda: {"summary": "big picture"},
            "medium": lambda: {"details": ["a", "b"]},
            "fast": lambda: {"draft": True},
        }
        return macro_parallel(layers)

    def merge_parallel_outputs() -> Any:
        outputs = run_parallel_workflows()
        return merge_outputs(outputs)

    return {
        "run_parallel_workflows": run_parallel_workflows,
        "merge_parallel_outputs": merge_parallel_outputs,
    }
