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
<<<<<<< Updated upstream
=======


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



>>>>>>> Stashed changes
