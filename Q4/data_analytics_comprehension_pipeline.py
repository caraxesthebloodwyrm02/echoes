"""Analytics pipeline aligned with the Drucker roadmap dashboard.

The goal is to generate roadmap-aware insights, update the
`DruckerFoundationModel`, and produce dashboard-compatible metrics.
"""

from __future__ import annotations

import logging
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional

import pandas as pd
import plotly.express as px
from drucker_management import DEFAULT_ROADMAP_ITEMS, DruckerFoundationModel

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)


class RoadmapAnalyticsPipeline:
    """Generate analytics compatible with the Dash roadmap dashboard."""

    def __init__(self, data_source: Optional[Path] = None):
        self.data_source = data_source
        self.model = DruckerFoundationModel(DEFAULT_ROADMAP_ITEMS)

    # ------------------------------------------------------------------
    # Data ingestion & harmonisation
    # ------------------------------------------------------------------
    def load_records(self) -> List[Dict[str, Any]]:
        """Load roadmap records from CSV or fallback to defaults."""

        if self.data_source and self.data_source.exists():
            df = pd.read_csv(self.data_source)
            logger.info("Loaded %d rows from %s", len(df), self.data_source)
            required_columns = {
                "title",
                "phase",
                "status",
                "priority",
                "owner",
                "start_date",
                "due_date",
                "progress",
                "objective",
            }
            missing = required_columns.difference(df.columns)
            if missing:
                raise ValueError("Missing required columns: %s" % sorted(missing))
            df = df.assign(id=range(1, len(df) + 1), notes="")
            return df.to_dict("records")

        logger.warning("No datasource provided; using DEFAULT_ROADMAP_ITEMS")
        return DEFAULT_ROADMAP_ITEMS

    def update_management_model(self, records: Iterable[Dict[str, Any]]) -> None:
        """Replace the model's roadmap with provided records."""

        self.model.ingest_roadmap(records)

    # ------------------------------------------------------------------
    # Analytical outputs
    # ------------------------------------------------------------------
    def build_status_summary(self) -> pd.DataFrame:
        counts = self.model.status_counts()
        return pd.DataFrame([{"status": status, "count": value} for status, value in counts.items()])

    def build_phase_summary(self) -> pd.DataFrame:
        counts = self.model.phase_counts()
        return pd.DataFrame([{"phase": phase, "count": value} for phase, value in counts.items()])

    def build_progress_snapshot(self) -> pd.DataFrame:
        return pd.DataFrame(self.model.to_records())[["title", "phase", "status", "progress", "due_date"]]

    def metrics(self) -> Dict[str, int]:
        return self.model.metrics()

    # ------------------------------------------------------------------
    # Visualisations for offline review (optional)
    # ------------------------------------------------------------------
    def status_chart(self) -> px.pie:
        df = self.build_status_summary()
        return px.pie(df, names="status", values="count", title="Roadmap Status Distribution")

    def phase_chart(self) -> px.bar:
        df = self.build_phase_summary()
        return px.bar(df, x="phase", y="count", color="phase", title="Roadmap Phase Mix")

    def progress_chart(self) -> px.bar:
        df = self.build_progress_snapshot()
        return px.bar(
            df.sort_values("progress"),
            x="title",
            y="progress",
            color="phase",
            title="Progress by Initiative",
        )

    # ------------------------------------------------------------------
    # Export helpers
    # ------------------------------------------------------------------
    def export_records(self, target: Path) -> None:
        df = pd.DataFrame(self.model.to_records())
        df.to_csv(target, index=False)
        logger.info("Exported roadmap dataset to %s", target)

    def export_metrics(self, target: Path) -> None:
        df = pd.DataFrame([self.metrics()])
        df.to_csv(target, index=False)
        logger.info("Exported roadmap metrics to %s", target)


def run_pipeline(data_source: Optional[str] = None, export_dir: Optional[str] = None) -> RoadmapAnalyticsPipeline:
    pipeline = RoadmapAnalyticsPipeline(Path(data_source) if data_source else None)

    records = pipeline.load_records()
    pipeline.update_management_model(records)

    metrics = pipeline.metrics()
    logger.info("Portfolio metrics: %s", metrics)

    if export_dir:
        target_dir = Path(export_dir)
        target_dir.mkdir(parents=True, exist_ok=True)
        pipeline.export_records(target_dir / "roadmap_records.csv")
        pipeline.export_metrics(target_dir / "roadmap_metrics.csv")

    return pipeline


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Run roadmap analytics pipeline")
    parser.add_argument("--data_source", type=str, help="Path to CSV data source")
    parser.add_argument("--export_dir", type=str, help="Directory to export results")

    args = parser.parse_args()
    run_pipeline(data_source=args.data_source, export_dir=args.export_dir)
