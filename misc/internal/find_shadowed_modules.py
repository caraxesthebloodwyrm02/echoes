import os
import sys


def get_stdlib_modules():
    """Get a set of all standard library module names"""
    stdlib = set()

    # Get the standard library path
    stdlib_paths = [
        p for p in sys.path if "site-packages" not in p and "dist-packages" not in p
    ]

    # Walk through all standard library paths
    for path in stdlib_paths:
        if os.path.exists(path):
            for root, dirs, files in os.walk(path):
                for file in files:
                    if file.endswith(".py"):
                        module_name = file[:-3]  # Remove .py extension
                        if module_name == "__init__":
                            continue
                        stdlib.add(module_name)

    return stdlib


def find_shadowed_modules(project_path):
    """Find Python files in the project that shadow standard library modules"""
    stdlib = get_stdlib_modules()
    shadowed = []

    for root, dirs, files in os.walk(project_path):
        # Skip virtual environment and other non-source directories
        if any(
            skip in root for skip in [".venv", "venv", "__pycache__", ".git", ".github"]
        ):
            continue

        for file in files:
            if file.endswith(".py") and not file.startswith("agent_"):
                module_name = file[:-3]  # Remove .py extension
                if module_name in stdlib:
                    full_path = os.path.join(root, file)
                    shadowed.append((module_name, full_path))

    return shadowed


def generate_report(shadowed_modules, output_file="shadowed_modules_report.txt"):
    """Generate a report of shadowed modules"""
    if not shadowed_modules:
        print("No shadowed modules found!")
        return

    with open(output_file, "w") as f:
        f.write("# Shadowed Python Standard Library Modules Report\n\n")
        f.write(
            f"Found {len(shadowed_modules)} modules that shadow Python standard library names:\n\n"
        )

        for module_name, file_path in sorted(shadowed_modules):
            rel_path = os.path.relpath(file_path)
            f.write(f"- {module_name}: {rel_path}\n")

            # Suggest new name
            dir_name = os.path.dirname(file_path)
            new_name = f"agent_{os.path.basename(file_path)}"
            new_path = os.path.join(dir_name, new_name)
            f.write(f"  Suggested rename: {rel_path} -> {os.path.relpath(new_path)}\n")

            # Check if the file contains imports that might need updating
            try:
                with open(file_path, encoding="utf-8") as mod_file:
                    content = mod_file.read()
                    if "import " in content or "from " in content:
                        f.write(
                            "  Note: This file contains imports that may need updating\n"
                        )
            except Exception as e:
                f.write(f"  Warning: Could not read file for analysis: {e}\n")

            f.write("\n")

    print(f"Report generated: {os.path.abspath(output_file)}")


if __name__ == "__main__":
    project_path = os.path.dirname(os.path.abspath(__file__))
    shadowed = find_shadowed_modules(project_path)
    generate_report(shadowed)
