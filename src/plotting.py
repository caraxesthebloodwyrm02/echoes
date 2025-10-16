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

"""Interactive plotting utilities using Plotly.

Converts static PNG outputs from o3 experiments into interactive 3D HTML
with camera controls, sliders, and toggles.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any, Dict

import numpy as np
import plotly.graph_objects as go


def create_interactive_html(data: Dict[str, Any], output_path: Path) -> None:
    """Create interactive Plotly 3D visualization from analysis JSON.

    Parameters
    ----------
    data
        Analysis JSON data with 'vectors' key containing normalized vectors
    output_path
        Path to save HTML file
    """
    vectors = data["vectors"]

    # Extract vectors
    influence = np.array(vectors["influence"])
    productivity = np.array(vectors["productivity"])
    creativity = np.array(vectors["creativity"])
    efficiency = np.array(vectors["efficiency"])

    # Create figure
    fig = go.Figure()

    # Origin point
    origin = [0, 0, 0]

    # Vector configurations
    vector_configs = [
        (influence, "Influence", "blue"),
        (productivity, "Productivity", "green"),
        (creativity, "Creativity", "purple"),
        (efficiency, "Efficiency (Balance)", "red"),
    ]

    # Add vectors as cones
    for vec, name, color in vector_configs:
        # Arrow shaft (line)
        fig.add_trace(
            go.Scatter3d(
                x=[0, vec[0]],
                y=[0, vec[1]],
                z=[0, vec[2]],
                mode="lines",
                line=dict(color=color, width=6),
                name=name,
                showlegend=True,
            )
        )

        # Arrow head (cone)
        fig.add_trace(
            go.Cone(
                x=[vec[0]],
                y=[vec[1]],
                z=[vec[2]],
                u=[vec[0] * 0.15],
                v=[vec[1] * 0.15],
                w=[vec[2] * 0.15],
                colorscale=[[0, color], [1, color]],
                showscale=False,
                name=f"{name} (head)",
                showlegend=False,
            )
        )

    # Add origin marker
    fig.add_trace(
        go.Scatter3d(
            x=[0],
            y=[0],
            z=[0],
            mode="markers",
            marker=dict(size=8, color="black"),
            name="Origin",
            showlegend=True,
        )
    )

    # Layout with controls
    classification = data.get("classification", {})
    metrics = data.get("metrics", {})

    title_text = (
        f"Trajectory Efficiency Analysis<br>"
        f"<sub>Classification: {classification.get('label', 'N/A')} | "
        f"Score: {metrics.get('efficiency_score', 0):.3f} | "
        f"Balance: {metrics.get('balance_angle_deg', 0):.1f}°</sub>"
    )

    fig.update_layout(
        title=title_text,
        scene=dict(
            xaxis_title="X (Conceptual)",
            yaxis_title="Y (Emotional)",
            zaxis_title="Z (Energetic)",
            xaxis=dict(range=[-1.2, 1.2]),
            yaxis=dict(range=[-1.2, 1.2]),
            zaxis=dict(range=[-1.2, 1.2]),
            aspectmode="cube",
        ),
        showlegend=True,
        legend=dict(
            x=0.02,
            y=0.98,
            bgcolor="rgba(255,255,255,0.8)",
        ),
        width=900,
        height=700,
    )

    # Add camera controls via updatemenus
    fig.update_layout(
        updatemenus=[
            dict(
                type="buttons",
                direction="left",
                buttons=[
                    dict(
                        args=[{"scene.camera.eye": {"x": 1.5, "y": 1.5, "z": 1.5}}],
                        label="Default View",
                        method="relayout",
                    ),
                    dict(
                        args=[{"scene.camera.eye": {"x": 2.5, "y": 0, "z": 0}}],
                        label="X-Axis View",
                        method="relayout",
                    ),
                    dict(
                        args=[{"scene.camera.eye": {"x": 0, "y": 2.5, "z": 0}}],
                        label="Y-Axis View",
                        method="relayout",
                    ),
                    dict(
                        args=[{"scene.camera.eye": {"x": 0, "y": 0, "z": 2.5}}],
                        label="Z-Axis View",
                        method="relayout",
                    ),
                ],
                pad={"r": 10, "t": 10},
                showactive=True,
                x=0.0,
                xanchor="left",
                y=1.15,
                yanchor="top",
            ),
        ]
    )

    # Add annotations with metrics
    annotations_text = (
        f"<b>Pairwise Angles:</b><br>"
        f"Influence ↔ Productivity: {metrics.get('pairwise_angles_deg', {}).get('influence_productivity', 0):.1f}°<br>"
        f"Influence ↔ Creativity: {metrics.get('pairwise_angles_deg', {}).get('influence_creativity', 0):.1f}°<br>"
        f"Productivity ↔ Creativity: {metrics.get('pairwise_angles_deg', {}).get('productivity_creativity', 0):.1f}°"
    )

    fig.add_annotation(
        text=annotations_text,
        xref="paper",
        yref="paper",
        x=0.98,
        y=0.02,
        xanchor="right",
        yanchor="bottom",
        showarrow=False,
        bgcolor="rgba(255,255,255,0.9)",
        bordercolor="black",
        borderwidth=1,
        font=dict(size=10),
    )

    # Save HTML
    output_path.parent.mkdir(parents=True, exist_ok=True)
    fig.write_html(str(output_path))
