"""
tool_validator.py
-----------------
Validation and safety utilities for tool-calling operations in Echoes Assistant.
Ensures structured, safe, and context-aware updates before applying code or document edits.
"""

import re
import json
import ast
from typing import List, Dict, Any, Union


class ToolValidationError(Exception):
    """Raised when the tool payload fails validation."""


class SyntaxValidationError(Exception):
    """Raised when code syntax validation fails."""


def validate_edit_payload(edits: List[Dict[str, Any]]) -> bool:
    """
    Validates a list of edit objects for canmore.update_textdoc or similar tools.
    Ensures required keys exist and are correctly typed.
    """
    required_keys = {"pattern", "multiple", "replacement"}
    for idx, edit in enumerate(edits):
        if not isinstance(edit, dict):
            raise ToolValidationError(f"Edit #{idx} must be a dictionary, got {type(edit).__name__}")

        missing = required_keys - set(edit.keys())
        if missing:
            raise ToolValidationError(f"Edit #{idx} missing required keys: {missing}")

        # Optional but recommended
        if "old_string" in edit and not isinstance(edit["old_string"], str):
            raise ToolValidationError(f"Edit #{idx} field 'old_string' must be a string")

        # Type checks
        if not isinstance(edit["pattern"], str) or not isinstance(edit["replacement"], str):
            raise ToolValidationError(f"Edit #{idx} pattern and replacement must be strings")

        if not isinstance(edit["multiple"], bool):
            raise ToolValidationError(f"Edit #{idx} multiple must be a boolean")

    return True


def generate_synced_edits(context: Dict[str, str], updates: Dict[str, str]) -> List[Dict[str, Any]]:
    """
    Creates a set of synchronized edit objects based on context mappings.
    context: {identifier: existing_code_snippet}
    updates: {identifier: new_code_snippet}
    """
    edits = []
    for name, new_code in updates.items():
        old_snippet = context.get(name)
        if not old_snippet:
            raise ToolValidationError(f"Context missing expected key '{name}' for update generation.")
        edits.append({
            "pattern": re.escape(old_snippet),
            "multiple": False,
            "replacement": new_code,
            "old_string": old_snippet
        })
    return edits


def validate_json_structure(payload: Union[str, Dict[str, Any]]) -> bool:
    """
    Ensures the JSON payload is valid before passing to a tool.
    """
    try:
        json.loads(payload) if isinstance(payload, str) else json.dumps(payload)
        return True
    except json.JSONDecodeError as e:
        raise ToolValidationError(f"Invalid JSON structure: {e}")


def validate_syntax(code: str) -> bool:
    """
    Validates Python syntax for updated code snippets.
    Returns True if valid, otherwise raises SyntaxValidationError.
    """
    try:
        ast.parse(code)
        return True
    except SyntaxError as e:
        raise SyntaxValidationError(f"Syntax error: {e.msg} (line {e.lineno})")


def lint_feedback(error_message: str) -> str:
    """
    Generates a quick heuristic fix suggestion for known syntax errors.
    """
    if "unexpected EOF" in error_message.lower():
        return "❗Possible unclosed bracket, quote, or parenthesis."
    if "expected expression" in error_message.lower():
        return "⚠️ Check for stray symbols or missing values near reported line."
    if "invalid syntax" in error_message.lower():
        return "💡 Try re-checking indentation or misplaced operators."
    return "Syntax error detected — inspect affected lines manually."


def safe_apply_edits(
    current_code: str,
    edits: List[Dict[str, Any]],
    validate_syntax_after: bool = True
) -> str:
    """
    Applies validated edits safely to code and optionally checks syntax.
    Returns the updated code string if successful.
    """
    validate_edit_payload(edits)
    updated_code = current_code

    for edit in edits:
        pattern = re.compile(edit["pattern"], re.DOTALL)
        if not pattern.search(updated_code):
            raise ToolValidationError(f"Pattern not found in current code: {edit['pattern']}")
        updated_code = pattern.sub(edit["replacement"], updated_code, count=0 if edit["multiple"] else 1)

    if validate_syntax_after:
        validate_syntax(updated_code)

    return updated_code


def summarize_edits(edits: List[Dict[str, Any]]) -> str:
    """
    Returns a human-readable summary of what the edits are doing.
    """
    summary_lines = []
    for idx, edit in enumerate(edits):
        summary_lines.append(
            f"Edit {idx+1}: Replace pattern '{edit['pattern'][:30]}...' "
            f"({'multiple' if edit['multiple'] else 'single'})"
        )
    return "\n".join(summary_lines)


# Example usage:
if __name__ == "__main__":
    # Example context and update
    context_example = {"roi_data": "    'ROI ($/mo)': [4500, 12500, 5600]"}
    updates_example = {"roi_data": "    'ROI ($/mo)': [5000, 13000, 7000]"}

    edits = generate_synced_edits(context_example, updates_example)
    print("Generated edits:\n", json.dumps(edits, indent=2))

    code = "data = pd.DataFrame({\n    'ROI ($/mo)': [4500, 12500, 5600]\n})"
    new_code = safe_apply_edits(code, edits)
    print("\n✅ Code updated successfully:\n", new_code)
