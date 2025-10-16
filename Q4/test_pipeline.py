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

"""Basic tests for the roadmap analytics pipeline."""

from data_analytics_comprehension_pipeline import RoadmapAnalyticsPipeline


def test_load_records_fallback():
    """Test loading records with no data source."""
    pipeline = RoadmapAnalyticsPipeline()
    records = pipeline.load_records()
    assert len(records) > 0
    assert all(isinstance(r, dict) for r in records)


def test_load_records_from_csv(tmp_path):
    """Test loading records from CSV."""
    csv_content = """title,phase,status,priority,owner,start_date,due_date,progress,objective
Test Item,Planning,Not Started,Medium,Test Owner,2024-01-01,2024-12-31,0,Test objective"""
    csv_file = tmp_path / "test.csv"
    csv_file.write_text(csv_content)

    pipeline = RoadmapAnalyticsPipeline(csv_file)
    records = pipeline.load_records()
    assert len(records) == 1
    assert records[0]["title"] == "Test Item"


def test_metrics():
    """Test metrics calculation."""
    pipeline = RoadmapAnalyticsPipeline()
    pipeline.load_records()
    pipeline.update_management_model(pipeline.load_records())
    metrics = pipeline.metrics()
    assert "total" in metrics
    assert "in_progress" in metrics
    assert "completed" in metrics
    assert "on_hold" in metrics
