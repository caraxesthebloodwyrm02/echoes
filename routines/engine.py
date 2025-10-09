from typing import List, Dict, Any, Callable


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


