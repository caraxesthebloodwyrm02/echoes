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
