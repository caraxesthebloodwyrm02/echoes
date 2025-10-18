"""
Core Trajectory Engine - Glimpse
Tracks and visualizes the trajectory of creative/developmental work in real time
"""

from __future__ import annotations
from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional, Callable
from enum import Enum
import time
import json
from collections import deque


class TrajectoryDirection(Enum):
    """Represents the direction/momentum of current trajectory"""
    EXPANDING = "expanding"  # Growing, building up
    CONVERGING = "converging"  # Narrowing down, focusing
    PIVOTING = "pivoting"  # Changing direction
    STABLE = "stable"  # Maintaining course
    UNCERTAIN = "uncertain"  # Unclear direction


@dataclass
class TrajectoryPoint:
    """A single point in the trajectory timeline"""
    timestamp: float
    content: str
    metadata: Dict[str, Any] = field(default_factory=dict)
    direction: TrajectoryDirection = TrajectoryDirection.UNCERTAIN
    confidence: float = 0.5  # 0-1 scale
    cause_effect_chain: List[str] = field(default_factory=list)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "timestamp": self.timestamp,
            "content": self.content,
            "metadata": self.metadata,
            "direction": self.direction.value,
            "confidence": self.confidence,
            "cause_effect_chain": self.cause_effect_chain
        }


@dataclass
class TrajectorySegment:
    """Represents a segment of the trajectory with coherent direction"""
    start_time: float
    end_time: float
    points: List[TrajectoryPoint]
    dominant_direction: TrajectoryDirection
    avg_confidence: float
    
    def duration(self) -> float:
        return self.end_time - self.start_time
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "start_time": self.start_time,
            "end_time": self.end_time,
            "duration": self.duration(),
            "points": [p.to_dict() for p in self.points],
            "dominant_direction": self.dominant_direction.value,
            "avg_confidence": self.avg_confidence
        }


class TrajectoryEngine:
    """
    Core engine that tracks and analyzes trajectory in real-time.
    Maintains a rolling window of recent activity and computes trajectory metrics.
    """
    
    def __init__(self, window_size: int = 100, segment_threshold: int = 10):
        self.window_size = window_size
        self.segment_threshold = segment_threshold
        self.points: deque[TrajectoryPoint] = deque(maxlen=window_size)
        self.segments: List[TrajectorySegment] = []
        self.current_direction = TrajectoryDirection.UNCERTAIN
        self.direction_analyzers: List[Callable] = []
        
    def register_analyzer(self, analyzer: Callable[[List[TrajectoryPoint]], TrajectoryDirection]):
        """Register custom direction analyzer functions"""
        self.direction_analyzers.append(analyzer)
    
    def add_point(self, content: str, metadata: Optional[Dict[str, Any]] = None) -> TrajectoryPoint:
        """Add a new point to the trajectory"""
        direction = self._analyze_direction(content)
        point = TrajectoryPoint(
            timestamp=time.time(),
            content=content,
            metadata=metadata or {},
            direction=direction,
            confidence=0.0,
            cause_effect_chain=self._trace_cause_effect(content)
        )
        
        self.points.append(point)
        point.confidence = self._compute_confidence()
        self._update_segments()
        self.current_direction = point.direction
        
        return point
    
    def _analyze_direction(self, content: str) -> TrajectoryDirection:
        """Analyze the direction based on content and history"""
        if len(self.points) < 2:
            return TrajectoryDirection.UNCERTAIN
        
        # Run custom analyzers if registered
        for analyzer in self.direction_analyzers:
            direction = analyzer(list(self.points))
            if direction != TrajectoryDirection.UNCERTAIN:
                return direction
        
        # Default simple heuristic
        recent = list(self.points)[-5:]
        content_lengths = [len(p.content) for p in recent]
        
        if len(content_lengths) < 2:
            return TrajectoryDirection.UNCERTAIN
        
        # Trend analysis
        trend = content_lengths[-1] - content_lengths[0]
        variance = max(content_lengths) - min(content_lengths)
        
        if trend > variance * 0.5:
            return TrajectoryDirection.EXPANDING
        elif trend < -variance * 0.5:
            return TrajectoryDirection.CONVERGING
        elif variance > sum(content_lengths) / len(content_lengths) * 0.3:
            return TrajectoryDirection.PIVOTING
        else:
            return TrajectoryDirection.STABLE
    
    def _compute_confidence(self) -> float:
        """Compute confidence score based on trajectory coherence"""
        if len(self.points) < 3:
            return 0.3
        
        recent = list(self.points)[-10:]
        directions = [p.direction for p in recent if p.direction != TrajectoryDirection.UNCERTAIN]
        
        if not directions:
            return 0.3
        
        most_common = max(set(directions), key=directions.count)
        consistency = directions.count(most_common) / len(directions)
        
        return min(0.95, 0.4 + 0.6 * consistency)
    
    def _trace_cause_effect(self, content: str) -> List[str]:
        """Trace cause-effect chain from recent trajectory"""
        chain = []
        
        if len(self.points) == 0:
            chain.append("Initial input")
        else:
            recent = list(self.points)[-3:]
            for p in recent:
                if p.content:
                    # Simplified cause tracking
                    preview = p.content[:30] + "..." if len(p.content) > 30 else p.content
                    chain.append(f"← {preview}")
        
        return chain
    
    def _update_segments(self):
        """Update trajectory segments when patterns change"""
        if len(self.points) < self.segment_threshold:
            return
        
        # Check if we should create a new segment
        recent_points = list(self.points)[-self.segment_threshold:]
        directions = [p.direction for p in recent_points]
        
        # If dominant direction changed, create new segment
        dominant = max(set(directions), key=directions.count)
        
        if not self.segments or self.segments[-1].dominant_direction != dominant:
            avg_conf = sum(p.confidence for p in recent_points) / len(recent_points)
            segment = TrajectorySegment(
                start_time=recent_points[0].timestamp,
                end_time=recent_points[-1].timestamp,
                points=recent_points.copy(),
                dominant_direction=dominant,
                avg_confidence=avg_conf
            )
            self.segments.append(segment)
    
    def get_current_state(self) -> Dict[str, Any]:
        """Get current trajectory state snapshot"""
        return {
            "timestamp": time.time(),
            "current_direction": self.current_direction.value,
            "total_points": len(self.points),
            "segments": len(self.segments),
            "recent_points": [p.to_dict() for p in list(self.points)[-5:]],
            "confidence": self._compute_confidence()
        }
    
    def get_trajectory_summary(self) -> Dict[str, Any]:
        """Get comprehensive trajectory summary"""
        return {
            "total_points": len(self.points),
            "total_segments": len(self.segments),
            "current_direction": self.current_direction.value,
            "segments": [s.to_dict() for s in self.segments[-5:]],  # Last 5 segments
            "trajectory_health": self._compute_health_score()
        }
    
    def _compute_health_score(self) -> float:
        """Compute overall trajectory health (0-1)"""
        if not self.points:
            return 0.0
        
        avg_confidence = sum(p.confidence for p in self.points) / len(self.points)
        consistency = 1.0 if self.segments else 0.5
        
        return (avg_confidence + consistency) / 2
    
    def predict_next_states(self, lookahead: int = 3) -> List[Dict[str, Any]]:
        """Predict potential next states based on current trajectory"""
        predictions = []
        
        if len(self.points) < 5:
            return [{"state": "insufficient_data", "probability": 1.0}]
        
        current_dir = self.current_direction
        confidence = self._compute_confidence()
        
        # Generate predictions based on current momentum
        if current_dir == TrajectoryDirection.EXPANDING:
            predictions.append({
                "direction": TrajectoryDirection.EXPANDING.value,
                "probability": confidence * 0.7,
                "description": "Continue building/expanding current path"
            })
            predictions.append({
                "direction": TrajectoryDirection.STABLE.value,
                "probability": (1 - confidence) * 0.5,
                "description": "Stabilize at current scope"
            })
        elif current_dir == TrajectoryDirection.CONVERGING:
            predictions.append({
                "direction": TrajectoryDirection.CONVERGING.value,
                "probability": confidence * 0.7,
                "description": "Continue narrowing/focusing"
            })
            predictions.append({
                "direction": TrajectoryDirection.PIVOTING.value,
                "probability": (1 - confidence) * 0.4,
                "description": "Pivot to new direction"
            })
        else:
            predictions.append({
                "direction": current_dir.value,
                "probability": 0.5,
                "description": f"Continue in {current_dir.value} mode"
            })
        
        return predictions[:lookahead]
    
    def clear(self):
        """Clear trajectory history"""
        self.points.clear()
        self.segments.clear()
        self.current_direction = TrajectoryDirection.UNCERTAIN
    
    def export_trajectory(self, filepath: str):
        """Export full trajectory to JSON file"""
        data = {
            "export_time": time.time(),
            "summary": self.get_trajectory_summary(),
            "all_points": [p.to_dict() for p in self.points],
            "all_segments": [s.to_dict() for s in self.segments]
        }
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2)
