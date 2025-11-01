import os

# Comprehensive list of Python standard library modules that could conflict
stdlib_modules = {
    # Core modules
    'abc', 'argparse', 'ast', 'asyncio', 'base64', 'bisect', 'calendar', 'cmath', 'collections', 'contextlib',
    'copy', 'copyreg', 'csv', 'dataclasses', 'datetime', 'decimal', 'difflib', 'enum', 'functools', 'gc',
    'hashlib', 'heapq', 'http', 'inspect', 'io', 'itertools', 'json', 'logging', 'math', 'os', 'pathlib',
    'pickle', 'platform', 'random', 're', 'string', 'subprocess', 'sys', 'threading', 'time', 'tokenize',
    'traceback', 'types', 'typing', 'unicodedata', 'urllib', 'warnings', 'weakref', 'xml', 'zipimport',

    # Additional modules that might conflict
    'token', 'html', 'email', 'gettext', 'docutils', '_pytest', 'mypy', 'pprint', 'numbers', 'packaging',

    # Internal modules (with underscores)
    '_io', '_warnings', '_decimal', '_pydecimal',
}

def identify_files_to_rename():
    """Identify files in core directory that need to be renamed"""
    core_dir = 'core'
    files_to_rename = []

    if os.path.exists(core_dir):
        for filename in os.listdir(core_dir):
            if filename.endswith('.py'):
                module_name = filename[:-3]  # Remove .py extension
                if module_name in stdlib_modules:
                    old_path = os.path.join(core_dir, filename)
                    new_path = os.path.join(core_dir, f'agent_{filename}')
                    files_to_rename.append((old_path, new_path))

    return files_to_rename

if __name__ == '__main__':
    files_to_rename = identify_files_to_rename()
    print(f"Found {len(files_to_rename)} files that need to be renamed:")
    for old_path, new_path in files_to_rename:
        print(f"  {old_path} -> {new_path}")
