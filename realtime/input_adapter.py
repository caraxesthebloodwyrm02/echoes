"""
Input Adaptation Layer - Glimpse
Handles real-time input processing and dynamic adaptation
"""

from __future__ import annotations
from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional, Callable
from enum import Enum
import time
import difflib


class InputEventType(Enum):
    """Types of input events"""
    INSERT = "insert"
    DELETE = "delete"
    REPLACE = "replace"
    UNDO = "undo"
    REDO = "redo"
    SELECTION = "selection"


@dataclass
class InputEvent:
    """Represents a single input event"""
    event_type: InputEventType
    timestamp: float
    position: int
    content: str
    previous_content: str = ""
    delta: str = ""  # The actual change
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "type": self.event_type.value,
            "timestamp": self.timestamp,
            "position": self.position,
            "content": self.content[:50],  # Truncate for logging
            "delta": self.delta
        }


@dataclass
class AdaptationContext:
    """Context for adaptive suggestions and predictions"""
    current_content: str
    cursor_position: int
    recent_events: List[InputEvent]
    suggestions: List[str] = field(default_factory=list)
    confidence: float = 0.5
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "content_length": len(self.current_content),
            "cursor_position": self.cursor_position,
            "event_count": len(self.recent_events),
            "suggestions": self.suggestions,
            "confidence": self.confidence
        }


class InputAdapter:
    """
    Manages input events and provides real-time adaptation.
    This is the middle layer that transforms raw input into meaningful trajectory data.
    """
    
    def __init__(self, buffer_size: int = 50):
        self.buffer_size = buffer_size
        self.current_content = ""
        self.cursor_position = 0
        self.event_history: List[InputEvent] = []
        self.undo_stack: List[str] = []
        self.redo_stack: List[str] = []
        self.suggestion_providers: List[Callable] = []
        
    def register_suggestion_provider(self, provider: Callable[[AdaptationContext], List[str]]):
        """Register a custom suggestion provider function"""
        self.suggestion_providers.append(provider)
    
    def process_insert(self, position: int, text: str) -> InputEvent:
        """Process text insertion"""
        previous = self.current_content
        self.undo_stack.append(previous)
        self.redo_stack.clear()
        
        # Insert text at position
        before = self.current_content[:position]
        after = self.current_content[position:]
        self.current_content = before + text + after
        self.cursor_position = position + len(text)
        
        event = InputEvent(
            event_type=InputEventType.INSERT,
            timestamp=time.time(),
            position=position,
            content=self.current_content,
            previous_content=previous,
            delta=text
        )
        
        self._add_event(event)
        return event
    
    def process_delete(self, start: int, end: int) -> InputEvent:
        """Process text deletion"""
        previous = self.current_content
        self.undo_stack.append(previous)
        self.redo_stack.clear()
        
        deleted = self.current_content[start:end]
        before = self.current_content[:start]
        after = self.current_content[end:]
        self.current_content = before + after
        self.cursor_position = start
        
        event = InputEvent(
            event_type=InputEventType.DELETE,
            timestamp=time.time(),
            position=start,
            content=self.current_content,
            previous_content=previous,
            delta=deleted
        )
        
        self._add_event(event)
        return event
    
    def process_replace(self, start: int, end: int, text: str) -> InputEvent:
        """Process text replacement"""
        previous = self.current_content
        self.undo_stack.append(previous)
        self.redo_stack.clear()
        
        replaced = self.current_content[start:end]
        before = self.current_content[:start]
        after = self.current_content[end:]
        self.current_content = before + text + after
        self.cursor_position = start + len(text)
        
        event = InputEvent(
            event_type=InputEventType.REPLACE,
            timestamp=time.time(),
            position=start,
            content=self.current_content,
            previous_content=previous,
            delta=f"{replaced} → {text}"
        )
        
        self._add_event(event)
        return event
    
    def undo(self) -> Optional[InputEvent]:
        """Undo last operation"""
        if not self.undo_stack:
            return None
        
        self.redo_stack.append(self.current_content)
        previous = self.current_content
        self.current_content = self.undo_stack.pop()
        
        event = InputEvent(
            event_type=InputEventType.UNDO,
            timestamp=time.time(),
            position=self.cursor_position,
            content=self.current_content,
            previous_content=previous,
            delta="undo"
        )
        
        self._add_event(event)
        return event
    
    def redo(self) -> Optional[InputEvent]:
        """Redo last undone operation"""
        if not self.redo_stack:
            return None
        
        self.undo_stack.append(self.current_content)
        previous = self.current_content
        self.current_content = self.redo_stack.pop()
        
        event = InputEvent(
            event_type=InputEventType.REDO,
            timestamp=time.time(),
            position=self.cursor_position,
            content=self.current_content,
            previous_content=previous,
            delta="redo"
        )
        
        self._add_event(event)
        return event
    
    def _add_event(self, event: InputEvent):
        """Add event to history with buffer management"""
        self.event_history.append(event)
        if len(self.event_history) > self.buffer_size:
            self.event_history.pop(0)
    
    def get_adaptation_context(self) -> AdaptationContext:
        """Get current adaptation context with suggestions"""
        recent = self.event_history[-10:] if len(self.event_history) >= 10 else self.event_history
        
        context = AdaptationContext(
            current_content=self.current_content,
            cursor_position=self.cursor_position,
            recent_events=recent,
            suggestions=[],
            confidence=0.5
        )
        
        # Generate suggestions from registered providers
        for provider in self.suggestion_providers:
            try:
                suggestions = provider(context)
                context.suggestions.extend(suggestions)
            except Exception:
                pass  # Silently fail individual providers
        
        # Built-in suggestion logic
        if not context.suggestions:
            context.suggestions = self._generate_default_suggestions()
        
        # Compute confidence based on recent event patterns
        context.confidence = self._compute_adaptation_confidence()
        
        return context
    
    def _generate_default_suggestions(self) -> List[str]:
        """Generate default suggestions based on current content"""
        suggestions = []
        
        # Simple word completion
        if self.current_content:
            # Get last word
            words = self.current_content.split()
            if words:
                last_word = words[-1]
                if len(last_word) >= 2:
                    # Very basic prediction - in real impl, use ML model
                    common_continuations = {
                        "the": ["the world", "the system", "the future"],
                        "real": ["realtime", "reality", "realization"],
                        "visual": ["visualization", "visually", "visual feedback"],
                        "traj": ["trajectory", "trajectories"],
                    }
                    
                    for prefix, completions in common_continuations.items():
                        if last_word.lower().startswith(prefix):
                            suggestions.extend(completions)
                            break
        
        return suggestions[:3]  # Limit to top 3
    
    def _compute_adaptation_confidence(self) -> float:
        """Compute confidence in current adaptations"""
        if len(self.event_history) < 3:
            return 0.3
        
        recent = self.event_history[-5:]
        
        # Confidence based on event consistency
        insert_count = sum(1 for e in recent if e.event_type == InputEventType.INSERT)
        delete_count = sum(1 for e in recent if e.event_type == InputEventType.DELETE)
        
        if insert_count > delete_count * 2:
            return 0.8  # Consistent building
        elif delete_count > insert_count * 2:
            return 0.6  # Consistent editing
        else:
            return 0.5  # Mixed activity
    
    def compute_diff(self, other_content: str) -> List[str]:
        """Compute diff between current and other content"""
        lines1 = self.current_content.splitlines()
        lines2 = other_content.splitlines()
        
        diff = difflib.unified_diff(lines1, lines2, lineterm='')
        return list(diff)
    
    def get_recent_activity(self, count: int = 10) -> List[Dict[str, Any]]:
        """Get recent input activity"""
        recent = self.event_history[-count:] if len(self.event_history) >= count else self.event_history
        return [e.to_dict() for e in recent]
    
    def get_typing_velocity(self) -> float:
        """Compute typing velocity (chars per second)"""
        if len(self.event_history) < 2:
            return 0.0
        
        recent = self.event_history[-10:]
        if not recent:
            return 0.0
        
        time_span = recent[-1].timestamp - recent[0].timestamp
        if time_span == 0:
            return 0.0
        
        total_chars = sum(len(e.delta) for e in recent if e.event_type == InputEventType.INSERT)
        return total_chars / time_span
    
    def get_edit_intensity(self) -> float:
        """Compute edit intensity (edits per second)"""
        if len(self.event_history) < 2:
            return 0.0
        
        recent = self.event_history[-20:]
        if not recent:
            return 0.0
        
        time_span = recent[-1].timestamp - recent[0].timestamp
        if time_span == 0:
            return 0.0
        
        return len(recent) / time_span
    
    def clear(self):
        """Clear all state"""
        self.current_content = ""
        self.cursor_position = 0
        self.event_history.clear()
        self.undo_stack.clear()
        self.redo_stack.clear()
