#!/usr/bin/env python3
"""
Automatic test generation for new modules.
Usage: python automation/test_generator.py app/domains/science/science_module.py
"""
import ast
import sys
from pathlib import Path


class TestGenerator:
    def __init__(self, source_file: str):
        self.source_file = Path(source_file)
        self.test_file = self._get_test_path()

    def _get_test_path(self) -> Path:
        """Convert source path to test path."""
        # app/domains/science/science_module.py -> tests/test_science_module.py
        parts = self.source_file.parts
        if parts and parts[0] in {"app", "packages", "src"}:
            module_name = f"test_{self.source_file.stem}.py"
            return Path("tests") / module_name
        return Path("tests") / f"test_{self.source_file.stem}.py"

    def extract_functions(self) -> list[dict]:
        """Extract public functions and detect async."""
        with open(self.source_file, "r", encoding="utf-8") as f:
            tree = ast.parse(f.read())
        functions: list[dict] = []
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                if not node.name.startswith("_"):
                    functions.append(
                        {
                            "name": node.name,
                            "args": [a.arg for a in node.args.args if a.arg != "self"],
                            "is_async": False,
                        }
                    )
            elif isinstance(node, ast.AsyncFunctionDef):
                if not node.name.startswith("_"):
                    functions.append(
                        {
                            "name": node.name,
                            "args": [a.arg for a in node.args.args if a.arg != "self"],
                            "is_async": True,
                        }
                    )
        return functions

    def _arrange_for_arg(self, arg: str) -> str:
        a = arg.lower()
        if "id" in a:
            return f'{arg} = "test-id-123"'
        if "name" in a:
            return f'{arg} = "test_name"'
        if "query" in a:
            return f'{arg} = "test query"'
        if "data" in a:
            return f'{arg} = {"{"}"key": "value"{"}"}'
        return f"{arg} = None  # TODO: provide appropriate test data"

    def generate_test_template(self, functions: list[dict]) -> str:
        module_path = str(self.source_file).replace("/", ".").replace("\\", ".").replace(".py", "")
        imports = f"""import pytest\nfrom {module_path} import {', '.join(f['name'] for f in functions)}\n\n\n"""
        blocks: list[str] = []
        for func in functions:
            async_prefix = "async " if func["is_async"] else ""
            await_prefix = "await " if func["is_async"] else ""
            pytest_mark = "@pytest.mark.asyncio\n" if func["is_async"] else ""
            params = ", ".join(func["args"]) if func["args"] else ""
            arrange = (
                "\n    ".join(self._arrange_for_arg(a) for a in func["args"])
                if func["args"]
                else "pass  # No parameters"
            )
            block = f"""{pytest_mark}{async_prefix}def test_{func['name']}_happy_path():
    \"\"\"Test {func['name']} with valid inputs.\"\"\"
    # Arrange
    {arrange}

    # Act
    result = {await_prefix}{func['name']}({params})

    # Assert
    assert result is not None
    # TODO: add specific assertions

"""
            blocks.append(block)
        return imports + "\n".join(blocks)

    def generate(self, overwrite: bool = False):
        if self.test_file.exists() and not overwrite:
            print(f"⚠️  Test file already exists: {self.test_file}")
            print("   Use --overwrite to replace it")
            return
        functions = self.extract_functions()
        if not functions:
            print(f"⚠️  No public functions found in {self.source_file}")
            return
        content = self.generate_test_template(functions)
        self.test_file.parent.mkdir(parents=True, exist_ok=True)
        with open(self.test_file, "w", encoding="utf-8") as f:
            f.write(content)
        print(f"✅ Generated test file: {self.test_file}")
        print(f"   Found {len(functions)} functions to test")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python automation/test_generator.py <source_file.py> [--overwrite]")
        sys.exit(1)
    gen = TestGenerator(sys.argv[1])
    gen.generate(overwrite="--overwrite" in sys.argv)
