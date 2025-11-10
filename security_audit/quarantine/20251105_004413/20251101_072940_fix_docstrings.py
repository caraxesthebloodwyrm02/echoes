#!/usr/bin/env python3

# Read the file
with open("assistant_v2_core.py", "r", encoding="utf-8") as f:
    content = f.read()

# Remove all triple-quoted docstrings
# Simple approach: remove lines that start with triple quotes
lines = content.split("\n")
new_lines = []
skip_until = None

for line in lines:
    stripped = line.strip()
    if skip_until:
        if stripped.endswith('"""') or stripped.endswith("'''"):
            skip_until = None
        continue
    elif (
        (stripped.startswith('"""') or stripped.startswith("'''"))
        and not stripped.endswith('"""')
        and not stripped.endswith("'''")
    ):
        # Start of multi-line docstring
        skip_until = stripped[:3]
        continue
    elif stripped.startswith('"""') or stripped.startswith("'''"):
        # Single line or end of multi-line docstring
        continue
    else:
        new_lines.append(line)

# Write back
with open("assistant_v2_core_fixed.py", "w", encoding="utf-8") as f:
    f.write("\n".join(new_lines))

print("Created assistant_v2_core_fixed.py without docstrings")
