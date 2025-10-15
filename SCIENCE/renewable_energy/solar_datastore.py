# MIT License
#
# Copyright (c) 2024 Echoes Project
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

# solar_datastore.py
# Module to integrate JSON data with a simple JSON-based datastore (knowledge graph simulation)

import json
import os
from typing import Any, Dict

DATASTORE_FILE = "solar_datastore.json"


def load_datastore() -> Dict[str, Any]:
    """Load the datastore from file."""
    if os.path.exists(DATASTORE_FILE):
        with open(DATASTORE_FILE, "r") as f:
            return json.load(f)
    return {"entries": []}


def save_datastore(data: Dict[str, Any]):
    """Save the datastore to file."""
    with open(DATASTORE_FILE, "w") as f:
        json.dump(data, f, indent=4)


def insert_into_datastore(json_file: str):
    """Read JSON file and insert into datastore."""
    with open(json_file, "r") as f:
        data = json.load(f)

    datastore = load_datastore()
    datastore["entries"].append(data)
    save_datastore(datastore)
    print(f"Inserted data from {json_file} into datastore.")


# CLI
if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Solar Datastore Integration")
    parser.add_argument(
        "--json_file", type=str, required=True, help="JSON file to insert"
    )
    args = parser.parse_args()
    insert_into_datastore(args.json_file)
