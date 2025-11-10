import os
import shutil

# List of files to rename based on the conflicts found
files_to_rename = [
    ("core/appdirs.py", "core/agent_appdirs.py"),
    ("core/aws.py", "core/agent_aws.py"),
    ("core/azure.py", "core/agent_azure.py"),
    ("core/codeql.py", "core/agent_codeql.py"),
    ("core/conftest.py", "core/agent_conftest.py"),
    ("core/dask.py", "core/agent_dask.py"),
    ("core/emoji.py", "core/agent_emoji.py"),
    ("core/gcp.py", "core/agent_gcp.py"),
    ("core/git.py", "core/agent_git.py"),
    ("core/glue.py", "core/agent_glue.py"),
    ("core/graphviz.py", "core/agent_graphviz.py"),
    ("core/ipython.py", "core/agent_ipython.py"),
    ("core/jupyter.py", "core/agent_jupyter.py"),
    ("core/jwt.py", "core/agent_jwt.py"),
    ("core/notebook.py", "core/agent_notebook.py"),
    ("core/objgraph.py", "core/agent_objgraph.py"),
    ("core/panel.py", "core/agent_panel.py"),
    ("core/psycopg2.py", "core/agent_psycopg2.py"),
    ("core/pymysql.py", "core/agent_pymysql.py"),
    ("core/pyodbc.py", "core/agent_pyodbc.py"),
    ("core/pytables.py", "core/agent_pytables.py"),
    ("core/render.py", "core/agent_render.py"),
    ("core/rich.py", "core/agent_rich.py"),
    ("core/sankey.py", "core/agent_sankey.py"),
    ("core/tables.py", "core/agent_tables.py"),
    ("core/tracemalloc.py", "core/agent_tracemalloc.py"),
    ("core/turbogears.py", "core/agent_turbogears.py"),
    ("core/uvloop.py", "core/agent_uvloop.py"),
    ("core/varnish.py", "core/agent_varnish.py"),
    ("core/websockets.py", "core/agent_websockets.py"),
    ("core/wheel.py", "core/agent_wheel.py"),
]

renamed_count = 0
for old_path, new_path in files_to_rename:
    if os.path.exists(old_path) and not os.path.exists(new_path):
        try:
            os.rename(old_path, new_path)
            print(f"Renamed {old_path} -> {new_path}")
            renamed_count += 1
        except Exception as e:
            print(f"Error renaming {old_path}: {e}")
    elif os.path.exists(new_path):
        print(f"Skipping {old_path} - {new_path} already exists")
    else:
        print(f"Skipping {old_path} - file does not exist")

print(f"\nTotal files renamed: {renamed_count}")
