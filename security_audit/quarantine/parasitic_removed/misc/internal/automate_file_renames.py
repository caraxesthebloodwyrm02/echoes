import os
import shutil

# List of files that need to be renamed/moved
# Format: (source_path, destination_path)
files_to_rename = [
    # Standard library module conflicts
    ("core/typing.py", "core/agent_typing.py"),
    ("core/collections.py", "core/agent_collections.py"),
    ("core/functools.py", "core/agent_functools.py"),
    ("core/traceback.py", "core/agent_traceback.py"),
    ("core/types.py", "core/agent_types.py"),
    ("core/logging.py", "core/agent_logging.py"),
    ("core/http.py", "core/agent_http.py"),
    ("core/warnings.py", "core/agent_warnings.py"),
    ("core/string.py", "core/agent_string.py"),
    ("core/subprocess.py", "core/agent_subprocess.py"),
    ("core/ast.py", "core/agent_ast.py"),
    ("core/pathlib.py", "core/agent_pathlib.py"),
    ("core/inspect.py", "core/agent_inspect.py"),
    ("core/dataclasses.py", "core/agent_dataclasses.py"),
    ("core/typing_extensions.py", "core/agent_typing_extensions.py"),
    ("core/tokenize.py", "core/agent_tokenize.py"),
    ("core/xml.py", "core/agent_xml.py"),
    ("core/_io.py", "core/agent__io.py"),
    ("core/_warnings.py", "core/agent__warnings.py"),
    ("core/token.py", "core/agent_token.py"),
    ("core/html.py", "core/agent_html.py"),
    ("core/email.py", "core/agent_email.py"),
    ("core/gettext.py", "core/agent_gettext.py"),
    ("core/docutils.py", "core/agent_docutils.py"),
    ("core/_pytest.py", "core/agent__pytest.py"),
    ("core/mypy.py", "core/agent_mypy.py"),
    ("core/pprint.py", "core/agent_pprint.py"),
    ("core/numbers.py", "core/agent_numbers.py"),
    ("core/packaging.py", "core/agent_packaging.py"),
    ("core/pickle.py", "core/agent_pickle.py"),
    ("core/anyio.py", "core/agent_anyio.py"),
    ("core/_ssl.py", "core/agent__ssl.py"),
    ("core/concurrent.py", "core/agent_concurrent.py"),
]


def rename_files():
    """Rename/move files from source to destination"""
    renamed_count = 0
    skipped_count = 0

    for source, destination in files_to_rename:
        if os.path.exists(source):
            # Create destination directory if it doesn't exist
            dest_dir = os.path.dirname(destination)
            if dest_dir and not os.path.exists(dest_dir):
                os.makedirs(dest_dir)

            # Check if destination already exists
            if os.path.exists(destination):
                print(f"SKIP: {destination} already exists")
                skipped_count += 1
                continue

            # Rename/move the file
            try:
                shutil.move(source, destination)
                print(f"RENAMED: {source} -> {destination}")
                renamed_count += 1
            except Exception as e:
                print(f"ERROR renaming {source}: {e}")
        else:
            print(f"SKIP: {source} does not exist")
            skipped_count += 1

    print(f"\nSummary: {renamed_count} files renamed, {skipped_count} files skipped")


if __name__ == "__main__":
    print("Files to be renamed:")
    for source, dest in files_to_rename:
        print(f"  {source} -> {dest}")
    print("\nStarting rename operation...\n")
    rename_files()
