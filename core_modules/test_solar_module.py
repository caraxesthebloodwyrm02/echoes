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

import json
import os
import tempfile

from solar_datastore import insert_into_datastore, load_datastore

from SCIENCE.renewable_energy.solar_module import (
    export_solar_summary_as_json,
)


def test_export_function():
    parsed_data = {"location": "Test", "irradiance": 100}
    inspiration_vectors = ["test"]
    semantic_scores = {"score": 0.5}

    result = export_solar_summary_as_json(parsed_data, inspiration_vectors, semantic_scores)
    data = json.loads(result)
    assert data["parsed_data"]["location"] == "Test"


def test_datastore_integration():
    test_data = {
        "parsed_data": {"location": "Test"},
        "inspiration_vectors": [],
        "semantic_scores": {},
    }
    with tempfile.NamedTemporaryFile(mode="w", delete=False, suffix=".json") as tmp:
        json.dump(test_data, tmp)
        tmp_name = tmp.name

    try:
        insert_into_datastore(tmp_name)
        datastore = load_datastore()
        assert len(datastore["entries"]) == 1
    finally:
        os.unlink(tmp_name)
        if os.path.exists("solar_datastore.json"):
            os.remove("solar_datastore.json")
