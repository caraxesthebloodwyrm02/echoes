# app/harmony/diff_service.py
from typing import Any, Dict, List, Tuple


def _is_number(x):
    return isinstance(x, (int, float))


def _ordered(items):
    # deterministic ordering for output
    return sorted(items, key=lambda s: str(s))


def compare_value(path: str, a: Any, b: Any, cfg: Dict) -> List[Dict]:
    changes = []
    if a == b:
        return changes
    # numeric tolerance
    if _is_number(a) and _is_number(b):
        eps = cfg.get("epsilon", 0.0)
        if abs(a - b) <= eps:
            return changes
        change_type = "value"
    elif type(a) != type(b):
        change_type = "type"
    else:
        change_type = "value"
    changes.append({"path": path, "from": a, "to": b, "change_type": change_type})
    return changes


def compare_dict(path: str, a: Dict, b: Dict, cfg: Dict) -> Tuple[List[Dict], List, List]:
    added = []
    removed = []
    modified = []
    a_keys = set(a.keys())
    b_keys = set(b.keys())
    for k in _ordered(list(b_keys - a_keys)):
        added.append({"path": f"{path}.{k}" if path else k, "value": b[k]})
    for k in _ordered(list(a_keys - b_keys)):
        removed.append({"path": f"{path}.{k}" if path else k, "value": a[k]})
    for k in _ordered(list(a_keys & b_keys)):
        pa = a[k]
        pb = b[k]
        p = f"{path}.{k}" if path else k
        if isinstance(pa, dict) and isinstance(pb, dict):
            sub_mod = compare_dict(p, pa, pb, cfg)
            modified.extend(sub_mod[2])
            added.extend(sub_mod[0])
            removed.extend(sub_mod[1])
        elif isinstance(pa, list) and isinstance(pb, list):
            sub_added, sub_removed, sub_modified = compare_list(p, pa, pb, cfg)
            added.extend(sub_added)
            removed.extend(sub_removed)
            modified.extend(sub_modified)
        else:
            modified.extend(compare_value(p, pa, pb, cfg))
    return added, removed, modified


def compare_list(path: str, a: List, b: List, cfg: Dict) -> Tuple[List, List, List]:
    # default index-based comparison
    added = []
    removed = []
    modified = []
    maxlen = max(len(a), len(b))
    for i in range(maxlen):
        pa = a[i] if i < len(a) else None
        pb = b[i] if i < len(b) else None
        p = f"{path}[{i}]"
        if i >= len(a):
            added.append({"path": p, "value": pb})
        elif i >= len(b):
            removed.append({"path": p, "value": pa})
        else:
            if isinstance(pa, dict) and isinstance(pb, dict):
                sub_added, sub_removed, sub_modified = compare_dict(p, pa, pb, cfg)
                added.extend(sub_added)
                removed.extend(sub_removed)
                modified.extend(sub_modified)
            elif isinstance(pa, list) and isinstance(pb, list):
                sa, sr, sm = compare_list(p, pa, pb, cfg)
                added.extend(sa)
                removed.extend(sr)
                modified.extend(sm)
            else:
                modified.extend(compare_value(p, pa, pb, cfg))
    return added, removed, modified


def diff(harmony: Dict, melody: Dict, cfg: Dict | None = None) -> Dict:
    cfg = cfg or {}
    added, removed, modified = compare_dict("", harmony, melody, cfg)
    result = {
        "added": added,
        "removed": removed,
        "modified": modified,
        "metrics": {
            "added_count": len(added),
            "removed_count": len(removed),
            "modified_count": len(modified),
        },
    }
    return result
