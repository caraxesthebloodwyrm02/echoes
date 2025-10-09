import concurrent.futures
from typing import Callable, Dict, Any


def run_layer(name: str, fn: Callable[[], Dict[str, Any]]) -> Dict[str, Any]:
    result = fn()
    result["layer"] = name
    return result


def macro_parallel(layers: Dict[str, Callable[[], Dict[str, Any]]]) -> Dict[str, Dict[str, Any]]:
    outputs: Dict[str, Dict[str, Any]] = {}
    with concurrent.futures.ThreadPoolExecutor(max_workers=len(layers)) as pool:
        future_to_name = {pool.submit(run_layer, name, fn): name for name, fn in layers.items()}
        for fut in concurrent.futures.as_completed(future_to_name):
            name = future_to_name[fut]
            outputs[name] = fut.result()
    return outputs


def merge_outputs(outputs: Dict[str, Dict[str, Any]]) -> Dict[str, Any]:
    merged: Dict[str, Any] = {"layers": list(outputs.keys()), "results": outputs}
    return merged


