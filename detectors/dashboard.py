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

"""Detector Dashboard using Dash."""

import json
from datetime import datetime
from pathlib import Path

import dash
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from dash import Input, Output, dcc, html

from detectors import DetectorManager
from detectors.anomaly_detector import AnomalyDetector


def load_detector_metrics():
    """Load metrics from all detectors."""
    manager = DetectorManager()
    anomaly_detector = AnomalyDetector()
    manager.register_detector(anomaly_detector)

    return manager.get_all_metrics()


def parse_audit_logs():
    """Parse audit logs to create FP/FN metrics (simplified)."""
    logs_dir = Path("logs")
    audit_data = []

    if logs_dir.exists():
        for log_file in logs_dir.glob("detector_audit.log*"):
            try:
                with open(log_file, "r") as f:
                    for line in f:
                        if '"detector":"anomaly_detector"' in line:
                            json_start = line.find("{")
                            if json_start >= 0:
                                entry = json.loads(line[json_start:])
                                audit_data.append(entry)
            except Exception:
                continue

    return audit_data


def create_dashboard():
    """Create the Dash dashboard."""
    app = dash.Dash(__name__, title="Detector Dashboard")

    # Load data
    metrics = load_detector_metrics()
    audit_data = parse_audit_logs()

    # Create metrics summary
    total_detections = sum(m["total_detections"] for m in metrics.values())
    total_actions = sum(m["actions_taken"] for m in metrics.values())

    # Create figures
    # Detection counts by tier
    tier_data = {}
    for detector, m in metrics.items():
        for tier, count in m["by_tier"].items():
            tier_data[tier] = tier_data.get(tier, 0) + count

    tier_fig = go.Figure(
        data=[
            go.Bar(
                x=list(tier_data.keys()),
                y=list(tier_data.values()),
                marker_color=["blue", "orange", "red"],
            )
        ]
    )
    tier_fig.update_layout(
        title="Detections by Tier", xaxis_title="Tier", yaxis_title="Count"
    )

    # Timeline of detections (if audit data available)
    if audit_data:
        df = pd.DataFrame(audit_data)
        if "timestamp" in df.columns:
            df["timestamp"] = pd.to_datetime(df["timestamp"])
            timeline_fig = px.histogram(
                df, x="timestamp", color="tier", title="Detection Timeline"
            )
        else:
            timeline_fig = go.Figure()
            timeline_fig.update_layout(title="No Timeline Data Available")
    else:
        timeline_fig = go.Figure()
        timeline_fig.update_layout(title="No Audit Data Available")

    # FP/FN metrics (simplified - would need manual labeling in real implementation)
    fp_fn_data = {
        "True Positive": total_actions,
        "False Positive": 0,  # Would need manual labeling
        "False Negative": 0,  # Would need manual labeling
        "True Negative": max(0, total_detections - total_actions),
    }

    confusion_fig = go.Figure(
        data=[
            go.Bar(
                x=list(fp_fn_data.keys()),
                y=list(fp_fn_data.values()),
                marker_color="lightblue",
            )
        ]
    )
    confusion_fig.update_layout(
        title="Confusion Matrix (Simplified)",
        xaxis_title="Classification",
        yaxis_title="Count",
    )

    # Layout
    app.layout = html.Div(
        [
            html.H1("Detector Dashboard", style={"textAlign": "center"}),
            # Summary cards
            html.Div(
                [
                    html.Div(
                        [html.H3(f"{total_detections}"), html.P("Total Detections")],
                        className="summary-card",
                    ),
                    html.Div(
                        [html.H3(f"{total_actions}"), html.P("Actions Taken")],
                        className="summary-card",
                    ),
                    html.Div(
                        [html.H3(f"{len(metrics)}"), html.P("Active Detectors")],
                        className="summary-card",
                    ),
                ],
                style={
                    "display": "flex",
                    "justifyContent": "space-around",
                    "margin": "20px",
                },
            ),
            # Charts
            html.Div(
                [
                    dcc.Graph(figure=tier_fig),
                    dcc.Graph(figure=timeline_fig),
                    dcc.Graph(figure=confusion_fig),
                ]
            ),
            # Refresh button
            html.Button("Refresh Data", id="refresh-button", n_clicks=0),
            html.Div(id="last-updated", children=f"Last updated: {datetime.now()}"),
            # CSS
            html.Style(
                """
            .summary-card {
                border: 1px solid #ddd;
                border-radius: 5px;
                padding: 20px;
                text-align: center;
                background-color: #f9f9f9;
                flex: 1;
                margin: 10px;
            }
        """
            ),
        ]
    )

    @app.callback(
        Output("last-updated", "children"), Input("refresh-button", "n_clicks")
    )
    def update_timestamp(n_clicks):
        return f"Last updated: {datetime.now()}"

    return app


if __name__ == "__main__":
    app = create_dashboard()
    app.run_server(debug=True, host="0.0.0.0", port=8050)
