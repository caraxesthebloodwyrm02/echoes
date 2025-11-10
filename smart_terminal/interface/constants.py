from enum import Enum, auto


class FeedbackType(Enum):
    """Types of contextual feedback that can be provided."""

    SUGGESTION = "suggestion"
    WARNING = "warning"
    TIP = "tip"
    EXPLANATION = "explanation"
    PERFORMANCE = "performance"
    SECURITY = "security"
    BEST_PRACTICE = "best_practice"


class SuggestionMode(Enum):
    """Terminal suggestion display modes."""

    NONE = auto()  # No suggestions
    BASIC = auto()  # Basic suggestions
    EXACT = auto()  # Exact match suggestions only
    FUZZY = auto()  # Fuzzy matching suggestions
    SMART = auto()  # AI-powered smart suggestions

    def next(self):
        """Get the next suggestion mode in rotation."""
        cls = self.__class__
        members = list(cls)
        index = members.index(self) + 1
        if index >= len(members):
            index = 0
        return members[index]

    def __str__(self):
        return self.name.title()
