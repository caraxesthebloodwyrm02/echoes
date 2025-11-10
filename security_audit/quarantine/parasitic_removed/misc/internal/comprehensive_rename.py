import os
import subprocess


def get_all_stdlib_modules():
    """Get a comprehensive list of all Python standard library modules"""
    stdlib_modules = set()

    # Common standard library modules
    common_stdlib = {
        # Core modules
        "abc",
        "argparse",
        "ast",
        "asyncio",
        "base64",
        "bisect",
        "calendar",
        "cmath",
        "collections",
        "contextlib",
        "copy",
        "copyreg",
        "csv",
        "dataclasses",
        "datetime",
        "decimal",
        "difflib",
        "enum",
        "functools",
        "gc",
        "hashlib",
        "heapq",
        "http",
        "inspect",
        "io",
        "itertools",
        "json",
        "logging",
        "math",
        "os",
        "pathlib",
        "pickle",
        "platform",
        "random",
        "re",
        "string",
        "subprocess",
        "sys",
        "threading",
        "time",
        "tokenize",
        "traceback",
        "types",
        "typing",
        "unicodedata",
        "urllib",
        "warnings",
        "weakref",
        "xml",
        "zipimport",
        # Additional modules that commonly cause conflicts
        "token",
        "html",
        "email",
        "gettext",
        "docutils",
        "_pytest",
        "mypy",
        "pprint",
        "numbers",
        "packaging",
        "anyio",
        "_ssl",
        "concurrent",
        "queue",
        "ssl",
        "socket",
        "select",
        "mmap",
        "msvcrt",
        "winreg",
        "winsound",
        "posix",
        "pwd",
        "spwd",
        "grp",
        "crypt",
        "termios",
        "tty",
        "pty",
        "fcntl",
        "pipes",
        "resource",
        "nis",
        "syslog",
        "optparse",
        "getopt",
        "readline",
        "rlcompleter",
        "sqlite3",
        "zlib",
        "gzip",
        "bz2",
        "lzma",
        "zipfile",
        "tarfile",
        "configparser",
        "netrc",
        "xdrlib",
        "plistlib",
        "hmac",
        "secrets",
        "contextvars",
        "multiprocessing",
        "_thread",
        "dummy_thread",
        "codecs",
        "stringprep",
        "textwrap",
        "binary",
        "struct",
        "site",
        "atexit",
        "future",
        "keyword",
        "symtable",
        "symbol",
        "tabnanny",
        "pyclbr",
        "py_compile",
        "compileall",
        "dis",
        "pickletools",
        "reprlib",
        "fractions",
        "statistics",
        "collections.abc",
        "array",
        "__future__",
        "sched",
        "_contextvars",
        "concurrent.futures",
        "_multiprocessing",
    }

    stdlib_modules.update(common_stdlib)
    return stdlib_modules


def rename_shadowing_files():
    """Rename all files in core directory that shadow stdlib modules"""
    stdlib_modules = get_all_stdlib_modules()
    core_dir = "core"

    renamed_files = []

    if os.path.exists(core_dir):
        for filename in os.listdir(core_dir):
            if filename.endswith(".py"):
                module_name = filename[:-3]  # Remove .py extension
                if module_name in stdlib_modules:
                    old_path = os.path.join(core_dir, filename)
                    new_filename = f"agent_{filename}"
                    new_path = os.path.join(core_dir, new_filename)

                    if not os.path.exists(new_path):
                        try:
                            # Use subprocess to run the ren command
                            result = subprocess.run(
                                ["ren", old_path, new_filename],
                                capture_output=True,
                                text=True,
                                cwd=os.getcwd(),
                            )
                            if result.returncode == 0:
                                renamed_files.append((old_path, new_path))
                                print(f"RENAMED: {old_path} -> {new_path}")
                            else:
                                print(f"ERROR renaming {old_path}: {result.stderr}")
                        except Exception as e:
                            print(f"ERROR renaming {old_path}: {e}")

    return renamed_files


if __name__ == "__main__":
    print("Renaming all files that shadow Python standard library modules...")
    renamed = rename_shadowing_files()
    print(f"\nRenamed {len(renamed)} files total")
    for old, new in renamed:
        print(f"  {old} -> {new}")
