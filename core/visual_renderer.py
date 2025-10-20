"""
Visual Preview Renderer - Glimpse
Generates visual representations and previews of trajectories
"""

from __future__ import annotations
from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional
from enum import Enum
import time
import json
import random

try:
    from PIL import Image, ImageDraw, ImageFont  # type: ignore

    PIL_AVAILABLE = True
except ImportError:  # pragma: no cover - optional dependency
    Image = ImageDraw = ImageFont = None  # type: ignore
    PIL_AVAILABLE = False


class VisualizationMode(Enum):
    """Different visualization modes for trajectories"""

    TIMELINE = "timeline"  # Linear timeline view
    TREE = "tree"  # Branching tree structure
    GRAPH = "graph"  # Network graph
    FLOW = "flow"  # Flow diagram
    HEATMAP = "heatmap"  # Intensity heatmap


@dataclass
class VisualElement:
    """A single visual element in the preview"""

    element_type: str  # node, edge, marker, annotation
    position: Dict[str, float]  # x, y coordinates
    properties: Dict[str, Any]  # color, size, label, etc.
    timestamp: float

    def to_dict(self) -> Dict[str, Any]:
        return {
            "type": self.element_type,
            "position": self.position,
            "properties": self.properties,
            "timestamp": self.timestamp,
        }


@dataclass
class PreviewFrame:
    """A single frame in the visual preview"""

    frame_id: int
    timestamp: float
    elements: List[VisualElement]
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "frame_id": self.frame_id,
            "timestamp": self.timestamp,
            "elements": [e.to_dict() for e in self.elements],
            "metadata": self.metadata,
        }


class VisualRenderer:
    """
    Generates visual previews of trajectories in real-time.
    Supports multiple visualization modes and cause-effect mapping.
    """

    def __init__(self, mode: VisualizationMode = VisualizationMode.TIMELINE):
        self.mode = mode
        self.frames: List[PreviewFrame] = []
        self.current_frame_id = 0
        self.color_schemes = self._initialize_color_schemes()
        self.glyph_palettes = self._initialize_glyph_palettes()
        self.ansi_enabled = True

    def _initialize_color_schemes(self) -> Dict[str, Dict[str, str]]:
        """Initialize color schemes for different trajectory states"""
        return {
            "expanding": {"primary": "#4CAF50", "secondary": "#81C784", "accent": "#A5D6A7"},  # Green
            "converging": {"primary": "#2196F3", "secondary": "#64B5F6", "accent": "#90CAF9"},  # Blue
            "pivoting": {"primary": "#FF9800", "secondary": "#FFB74D", "accent": "#FFCC80"},  # Orange
            "stable": {"primary": "#9E9E9E", "secondary": "#BDBDBD", "accent": "#E0E0E0"},  # Gray
            "uncertain": {"primary": "#9C27B0", "secondary": "#BA68C8", "accent": "#CE93D8"},  # Purple
        }

    def _initialize_glyph_palettes(self) -> Dict[str, Dict[str, str]]:
        """Glyph palettes for richer terminal rendering."""
        return {
            "dense": {
                "expanding": "▲",
                "converging": "▼",
                "pivoting": "◆",
                "stable": "■",
                "uncertain": "?",
                "particle": "•",
            },
            "light": {
                "expanding": "/",
                "converging": "\\",
                "pivoting": "*",
                "stable": "-",
                "uncertain": ".",
                "particle": "·",
            },
        }

    def render_trajectory_point(self, point_data: Dict[str, Any], index: int) -> VisualElement:
        """Render a single trajectory point"""
        direction = point_data.get("direction", "uncertain")
        confidence = point_data.get("confidence", 0.5)

        colors = self.color_schemes.get(direction, self.color_schemes["uncertain"])

        element = VisualElement(
            element_type="node",
            position={"x": index * 50, "y": 100 + (confidence - 0.5) * 100},
            properties={
                "color": colors["primary"],
                "size": 10 + confidence * 20,
                "label": point_data.get("content", "")[:20],
                "direction": direction,
                "confidence": confidence,
                "glow": confidence > 0.7,
            },
            timestamp=point_data.get("timestamp", time.time()),
        )

        return element

    def render_cause_effect_chain(self, chain: List[str], base_x: float, base_y: float) -> List[VisualElement]:
        """Render cause-effect chain as connected elements"""
        elements = []

        for i, cause in enumerate(chain):
            element = VisualElement(
                element_type="chain_link",
                position={"x": base_x - i * 30, "y": base_y + i * 15},
                properties={
                    "color": "#FFC107",  # Amber for cause-effect
                    "size": 8,
                    "label": cause,
                    "opacity": 1.0 - (i * 0.2),
                    "arrow": True,
                },
                timestamp=time.time(),
            )
            elements.append(element)

        return elements

    def render_timeline(self, trajectory_data: Dict[str, Any]) -> PreviewFrame:
        """Render timeline visualization"""
        elements = []

        recent_points = trajectory_data.get("recent_points", [])

        for i, point in enumerate(recent_points):
            # Render main point
            node = self.render_trajectory_point(point, i)
            elements.append(node)

            # Render cause-effect chain if available
            chain = point.get("cause_effect_chain", [])
            if chain:
                chain_elements = self.render_cause_effect_chain(chain, node.position["x"], node.position["y"] - 30)
                elements.extend(chain_elements)

            # Add connecting edge to previous point
            if i > 0:
                edge = VisualElement(
                    element_type="edge",
                    position={
                        "x1": (i - 1) * 50,
                        "y1": elements[i - 1].position["y"],
                        "x2": i * 50,
                        "y2": node.position["y"],
                    },
                    properties={"color": "#666666", "width": 2, "style": "solid"},
                    timestamp=time.time(),
                )
                elements.append(edge)

        frame = PreviewFrame(
            frame_id=self.current_frame_id,
            timestamp=time.time(),
            elements=elements,
            metadata={
                "mode": self.mode.value,
                "point_count": len(recent_points),
                "current_direction": trajectory_data.get("current_direction", "uncertain"),
            },
        )

        self.current_frame_id += 1
        self.frames.append(frame)

        return frame

    def render_tree(self, trajectory_data: Dict[str, Any]) -> PreviewFrame:
        """Render tree/branching visualization"""
        elements = []

        segments = trajectory_data.get("segments", [])

        for i, segment in enumerate(segments):
            # Render segment as branch
            base_x = 200
            base_y = i * 80

            node = VisualElement(
                element_type="branch",
                position={"x": base_x, "y": base_y},
                properties={
                    "color": self.color_schemes[segment.get("dominant_direction", "uncertain")]["primary"],
                    "width": segment.get("avg_confidence", 0.5) * 100,
                    "label": f"Segment {i}: {segment.get('dominant_direction', 'unknown')}",
                    "duration": segment.get("duration", 0),
                },
                timestamp=time.time(),
            )
            elements.append(node)

        frame = PreviewFrame(
            frame_id=self.current_frame_id,
            timestamp=time.time(),
            elements=elements,
            metadata={"mode": self.mode.value, "segment_count": len(segments)},
        )

        self.current_frame_id += 1
        self.frames.append(frame)

        return frame

    def render_flow(self, trajectory_data: Dict[str, Any]) -> PreviewFrame:
        """Render flow diagram showing trajectory momentum"""
        elements = []

        current_direction = trajectory_data.get("current_direction", "uncertain")
        confidence = trajectory_data.get("confidence", 0.5)

        # Central flow indicator
        center = VisualElement(
            element_type="flow_center",
            position={"x": 250, "y": 200},
            properties={
                "color": self.color_schemes[current_direction]["primary"],
                "size": 50 + confidence * 50,
                "label": current_direction.upper(),
                "pulse": True,
                "intensity": confidence,
            },
            timestamp=time.time(),
        )
        elements.append(center)

        # Flow particles
        for i in range(int(confidence * 10)):
            particle = VisualElement(
                element_type="particle",
                position={"x": 250 + (i - 5) * 20, "y": 200 + (i % 3 - 1) * 30},
                properties={
                    "color": self.color_schemes[current_direction]["accent"],
                    "size": 5,
                    "velocity": confidence,
                    "opacity": 0.7,
                },
                timestamp=time.time(),
            )
            elements.append(particle)

        frame = PreviewFrame(
            frame_id=self.current_frame_id,
            timestamp=time.time(),
            elements=elements,
            metadata={"mode": self.mode.value, "direction": current_direction, "confidence": confidence},
        )

        self.current_frame_id += 1
        self.frames.append(frame)

        return frame

    def render_heatmap(self, input_context: Dict[str, Any]) -> PreviewFrame:
        """Render heatmap showing editing intensity"""
        elements = []

        activity = input_context.get("recent_activity", [])

        # Create heatmap grid
        grid_size = 10
        heat_values = [[0 for _ in range(grid_size)] for _ in range(grid_size)]

        # Populate heat values based on activity
        for event in activity:
            pos = event.get("position", 0)
            grid_x = min(pos % grid_size, grid_size - 1)
            grid_y = min(pos // grid_size, grid_size - 1)
            heat_values[grid_y][grid_x] += 1

        # Render grid cells
        max_heat = max(max(row) for row in heat_values) if heat_values else 1

        for y in range(grid_size):
            for x in range(grid_size):
                heat = heat_values[y][x]
                intensity = heat / max_heat if max_heat > 0 else 0

                cell = VisualElement(
                    element_type="heatmap_cell",
                    position={"x": x * 30, "y": y * 30},
                    properties={
                        "color": self._heat_color(intensity),
                        "size": 28,
                        "intensity": intensity,
                        "value": heat,
                    },
                    timestamp=time.time(),
                )
                elements.append(cell)

        frame = PreviewFrame(
            frame_id=self.current_frame_id,
            timestamp=time.time(),
            elements=elements,
            metadata={"mode": self.mode.value, "max_heat": max_heat},
        )

        self.current_frame_id += 1
        self.frames.append(frame)

        return frame

    def _heat_color(self, intensity: float) -> str:
        """Generate color based on heat intensity"""
        if intensity < 0.2:
            return "#E3F2FD"  # Very light blue
        elif intensity < 0.4:
            return "#90CAF9"  # Light blue
        elif intensity < 0.6:
            return "#FDD835"  # Yellow
        elif intensity < 0.8:
            return "#FF9800"  # Orange
        else:
            return "#F44336"  # Red

    def render(self, trajectory_data: Dict[str, Any], input_context: Optional[Dict[str, Any]] = None) -> PreviewFrame:
        """Render based on current visualization mode"""
        if self.mode == VisualizationMode.TIMELINE:
            return self.render_timeline(trajectory_data)
        elif self.mode == VisualizationMode.TREE:
            return self.render_tree(trajectory_data)
        elif self.mode == VisualizationMode.FLOW:
            return self.render_flow(trajectory_data)
        elif self.mode == VisualizationMode.HEATMAP:
            if input_context:
                return self.render_heatmap(input_context)
            else:
                return self.render_timeline(trajectory_data)
        else:
            return self.render_timeline(trajectory_data)

    def set_mode(self, mode: VisualizationMode):
        """Change visualization mode"""
        self.mode = mode

    def export_animation(self, filepath: str, frame_limit: Optional[int] = None):
        """Export animation data as JSON"""
        frames_to_export = self.frames[-frame_limit:] if frame_limit else self.frames

        animation_data = {
            "total_frames": len(frames_to_export),
            "mode": self.mode.value,
            "frames": [f.to_dict() for f in frames_to_export],
            "color_schemes": self.color_schemes,
        }

        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(animation_data, f, indent=2)

    def clear_frames(self):
        """Clear all frames"""
        self.frames.clear()
        self.current_frame_id = 0

    def get_latest_frame(self) -> Optional[PreviewFrame]:
        """Get the most recent frame"""
        return self.frames[-1] if self.frames else None

    def generate_ascii_preview(
        self,
        frame: PreviewFrame,
        width: int = 80,
        height: int = 20,
        blur: Optional[float] = None,
        palette: str = "dense",
        use_ansi: bool = False,
    ) -> str:
        """Generate ASCII preview with optional ANSI colors."""
        glyphs = self.glyph_palettes.get(palette, self.glyph_palettes["dense"])
        grid = [[" " for _ in range(width)] for _ in range(height)]
        color_grid: List[List[Optional[str]]] = [[None for _ in range(width)] for _ in range(height)]

        for element in frame.elements:
            if element.element_type in ["node", "flow_center"]:
                x = int(element.position.get("x", 0)) % width
                y = int(element.position.get("y", 0)) % height

                direction = element.properties.get("direction", "uncertain")
                char = glyphs.get(direction, glyphs.get("uncertain", "●"))

                if 0 <= y < height and 0 <= x < width:
                    grid[y][x] = char
                    color_grid[y][x] = self.color_schemes.get(direction, self.color_schemes["uncertain"]).get("primary")
            elif element.element_type == "particle":
                x = int(element.position.get("x", 0)) % width
                y = int(element.position.get("y", 0)) % height
                if 0 <= y < height and 0 <= x < width:
                    grid[y][x] = glyphs.get("particle", "·")
                    color_grid[y][x] = self.color_schemes.get(
                        element.properties.get("direction", "uncertain"), self.color_schemes["uncertain"]
                    ).get("accent")

        blur_val = blur
        if blur_val is None:
            try:
                blur_val = float(frame.metadata.get("blur", 0.0))
            except Exception:
                blur_val = 0.0
        blur_val = max(0.0, min(1.0, blur_val or 0.0))

        if blur_val > 0.0:
            drop_prob = 0.3 + 0.5 * blur_val
            for y in range(height):
                for x in range(width):
                    if grid[y][x] != " " and random.random() < drop_prob * 0.4:
                        grid[y][x] = glyphs.get("particle", ".") if blur_val < 0.6 else " "
                        if grid[y][x] == " ":
                            color_grid[y][x] = None

        if use_ansi and self.ansi_enabled:
            return self._render_with_ansi(grid, color_grid)

        lines = ["".join(row) for row in grid]
        return "\n".join(lines)

    def _render_with_ansi(self, glyph_grid: List[List[str]], color_grid: List[List[Optional[str]]]) -> str:
        """Render grid with ANSI escape codes."""

        def hex_to_rgb(hex_color: str) -> tuple[int, int, int]:
            hex_color = hex_color.lstrip("#")
            return tuple(int(hex_color[i : i + 2], 16) for i in (0, 2, 4))

        lines = []
        current_color = None
        for row, colors in zip(glyph_grid, color_grid):
            segments = []
            current_color = None
            for char, hex_color in zip(row, colors):
                if hex_color and char != " ":
                    rgb = hex_to_rgb(hex_color)
                    ansi = f"\033[38;2;{rgb[0]};{rgb[1]};{rgb[2]}m"
                    if current_color != ansi:
                        segments.append(ansi)
                        current_color = ansi
                else:
                    if current_color is not None:
                        segments.append("\033[0m")
                        current_color = None
                segments.append(char)
            if current_color is not None:
                segments.append("\033[0m")
            lines.append("".join(segments))
        return "\n".join(lines)

    def generate_image_preview(
        self,
        frame: PreviewFrame,
        width: int = 640,
        height: int = 360,
        background: str = "#111111",
        font_path: Optional[str] = None,
    ) -> Optional[Image.Image]:
        """Generate a PIL Image preview if Pillow is available."""
        if not PIL_AVAILABLE:
            return None

        image = Image.new("RGB", (width, height), background)
        draw = ImageDraw.Draw(image)

        try:
            font = ImageFont.truetype(font_path or "arial.ttf", 16)
        except Exception:
            font = ImageFont.load_default()

        for element in frame.elements:
            color = element.properties.get("color", "#FFFFFF")
            x = float(element.position.get("x", 0))
            y = float(element.position.get("y", 0))
            char = element.properties.get("label", "")[:2] or "●"

            draw.text((x, y), char, fill=color, font=font)

        return image
