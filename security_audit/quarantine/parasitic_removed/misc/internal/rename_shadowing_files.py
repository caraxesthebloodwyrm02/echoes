import sys
from pathlib import Path


def get_stdlib_modules():
    """Get a set of all standard library module names"""
    stdlib = set(sys.stdlib_module_names)

    # Add additional common modules that might not be in stdlib_module_names
    additional_stdlib = {
        "_pytest",
        "pytest",
        "numpy",
        "pandas",
        "matplotlib",
        "scipy",
        "sklearn",
        "tensorflow",
        "torch",
        "requests",
        "flask",
        "django",
        "sqlalchemy",
        "pydantic",
        "typing_extensions",
        "pytest_cov",
        "coverage",
        "pylint",
        "flake8",
        "mypy",
        "black",
        "isort",
        "mypy_extensions",
        "docutils",
        "sphinx",
        "setuptools",
        "pip",
        "wheel",
        "virtualenv",
        "pipenv",
        "poetry",
    }

    # Add common test module names
    test_modules = {
        "conftest",
        "test_utils",
        "test_helpers",
        "fixtures",
        "factories",
        "mocks",
        "fakes",
        "stubs",
        "helpers",
        "utils",
    }

    return stdlib.union(additional_stdlib).union(test_modules)


def should_rename_file(filepath):
    """Determine if a file should be renamed"""
    # Skip files that already have a prefix
    if filepath.stem.startswith(("agent_", "core_", "echoes_", "test_", "_")):
        return False

    # Skip __init__.py and other special files
    if filepath.stem in ("__init__", "__main__", "__about__"):
        return False

    return True


def rename_files(directory):
    """Rename Python files in the given directory that shadow stdlib modules"""
    stdlib_modules = get_stdlib_modules()
    renamed_count = 0

    # Look for Python files in the directory and its subdirectories
    for filepath in Path(directory).rglob("*.py"):
        if not should_rename_file(filepath):
            continue

        module_name = filepath.stem
        if module_name in stdlib_modules:
            new_filename = f"agent_{filepath.name}"
            new_path = filepath.with_name(new_filename)

            # Skip if the target file already exists
            if new_path.exists():
                print(f"Skipping {filepath}: {new_filename} already exists")
                continue

            # Rename the file
            print(f"Renaming {filepath} to {new_path}")
            filepath.rename(new_path)
            renamed_count += 1

    return renamed_count


def main():
    # Get the project root directory
    project_root = Path(__file__).parent

    # Directories to scan for shadowed modules
    directories_to_scan = [
        project_root / "core",
        project_root / "c_o_r_e",
        project_root / "echoes",
        project_root / "app",
    ]

    total_renamed = 0
    for directory in directories_to_scan:
        if directory.exists():
            print(f"\nScanning directory: {directory}")
            renamed = rename_files(directory)
            total_renamed += renamed
            print(f"Renamed {renamed} files in {directory}")

    print(f"\nTotal files renamed: {total_renamed}")
    if total_renamed > 0:
        print(
            "\nNote: After renaming, you may need to update import statements in your code."
        )


if __name__ == "__main__":
    main()
