"""
Intent Awareness Engine - Advanced natural language understanding
Detects user intent, extracts entities, and maintains conversation context
"""

import logging
import re
from typing import Dict, Any, List, Optional, Set, Tuple, NamedTuple
from datetime import datetime
from collections import defaultdict, deque
from dataclasses import dataclass, field
from enum import Enum

logger = logging.getLogger(__name__)


class IntentType(Enum):
    """Types of user intents"""

    QUESTION = "question"
    COMMAND = "command"
    REQUEST = "request"
    EXPLANATION = "explanation"
    CREATION = "creation"
    ANALYSIS = "analysis"
    COMPARISON = "comparison"
    PROBLEM_SOLVING = "problem_solving"
    LEARNING = "learning"
    SOCIAL = "social"
    EXPLORATION = "exploration"
    VALIDATION = "validation"
    CLARIFICATION = "clarification"


class EntityType(Enum):
    """Types of entities that can be identified"""

    PERSON = "person"
    ORGANIZATION = "organization"
    LOCATION = "location"
    TECHNOLOGY = "technology"
    CONCEPT = "concept"
    PROCESS = "process"
    TOOL = "tool"
    METRIC = "metric"
    DATE_TIME = "date_time"
    NUMERICAL = "numerical"
    DOCUMENT = "document"
    CODE = "code"
    PROJECT = "project"


@dataclass
class Entity:
    """Represents an identified entity"""

    text: str
    type: EntityType
    confidence: float
    context: str
    start_pos: int
    end_pos: int
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class Intent:
    """Represents detected user intent"""

    type: IntentType
    confidence: float
    keywords: List[str]
    context: str
    parameters: Dict[str, Any] = field(default_factory=dict)


@dataclass
class ThoughtNode:
    """A node in the train of thought"""

    id: str
    content: str
    timestamp: datetime
    entities: List[Entity]
    intent: Intent
    parent_ids: List[str] = field(default_factory=list)
    child_ids: List[str] = field(default_factory=list)
    cross_links: List[str] = field(default_factory=list)
    importance: float = 0.5
    metadata: Dict[str, Any] = field(default_factory=dict)


class IntentAwarenessEngine:
    """Advanced intent detection and entity extraction system"""

    def __init__(self):
        # Intent patterns with keywords and regex
        self.intent_patterns = {
            IntentType.QUESTION: {
                "keywords": [
                    "what",
                    "why",
                    "how",
                    "when",
                    "where",
                    "who",
                    "which",
                    "can",
                    "could",
                    "would",
                    "should",
                    "is",
                    "are",
                    "do",
                    "does",
                    "did",
                ],
                "patterns": [
                    r"\?",
                    r"^(what|why|how|when|where|who|which|can|could|would|should|is|are|do|does|did) .+",
                    r".+ \?$",
                ],
                "weight": 0.8,
            },
            IntentType.COMMAND: {
                "keywords": [
                    "create",
                    "make",
                    "build",
                    "generate",
                    "write",
                    "code",
                    "implement",
                    "develop",
                    "design",
                    "draw",
                    "compose",
                ],
                "patterns": [
                    r"^(create|make|build|generate|write|code|implement|develop|design|draw|compose) .+",
                    r".+ (now|please)",
                ],
                "weight": 0.9,
            },
            IntentType.REQUEST: {
                "keywords": [
                    "help",
                    "assist",
                    "support",
                    "guide",
                    "show",
                    "tell",
                    "explain",
                    "describe",
                    "provide",
                    "give",
                ],
                "patterns": [
                    r"^(help|assist|support|guide|show|tell|explain|describe|provide|give) .+",
                    r".+ (help|assist|support)",
                ],
                "weight": 0.7,
            },
            IntentType.ANALYSIS: {
                "keywords": [
                    "analyze",
                    "examine",
                    "review",
                    "assess",
                    "evaluate",
                    "compare",
                    "contrast",
                    "break down",
                ],
                "patterns": [
                    r"^(analyze|examine|review|assess|evaluate|compare|contrast|break down) .+",
                    r".+ (analysis|review)",
                ],
                "weight": 0.8,
            },
            IntentType.COMPARISON: {
                "keywords": [
                    "compare",
                    "versus",
                    "vs",
                    "difference",
                    "better",
                    "worse",
                    "pros",
                    "cons",
                    "advantages",
                    "disadvantages",
                ],
                "patterns": [
                    r".+ (versus|vs|compared to) .+",
                    r".+ (difference|differences) .+",
                    r"pros and cons .+",
                ],
                "weight": 0.8,
            },
            IntentType.PROBLEM_SOLVING: {
                "keywords": [
                    "problem",
                    "issue",
                    "bug",
                    "error",
                    "fix",
                    "solve",
                    "resolve",
                    "troubleshoot",
                    "debug",
                ],
                "patterns": [
                    r".+ (problem|issue|bug|error) .+",
                    r"^(fix|solve|resolve|troubleshoot|debug) .+",
                    r".+ not working",
                ],
                "weight": 0.9,
            },
            IntentType.LEARNING: {
                "keywords": [
                    "learn",
                    "understand",
                    "study",
                    "teach",
                    "explain",
                    "tutorial",
                    "guide",
                    "course",
                ],
                "patterns": [
                    r"^(learn|understand|study|teach) .+",
                    r".+ (learn|understand|study) .+",
                    r"how to .+",
                ],
                "weight": 0.7,
            },
            IntentType.CREATION: {
                "keywords": [
                    "create",
                    "make",
                    "build",
                    "design",
                    "invent",
                    "develop",
                    "compose",
                    "write",
                    "generate",
                ],
                "patterns": [
                    r"^(create|make|build|design|invent|develop|compose|write|generate) .+",
                    r".+ from scratch",
                ],
                "weight": 0.8,
            },
            IntentType.EXPLORATION: {
                "keywords": [
                    "explore",
                    "discover",
                    "investigate",
                    "research",
                    "find",
                    "search",
                    "look into",
                ],
                "patterns": [
                    r"^(explore|discover|investigate|research|find|search|look into) .+",
                    r".+ (exploration|discovery)",
                ],
                "weight": 0.7,
            },
            IntentType.VALIDATION: {
                "keywords": [
                    "correct",
                    "right",
                    "wrong",
                    "verify",
                    "validate",
                    "confirm",
                    "check",
                    "review",
                ],
                "patterns": [
                    r".+ (correct|right|wrong)\?$",
                    r"^(verify|validate|confirm|check) .+",
                    r"is this .+",
                ],
                "weight": 0.8,
            },
            IntentType.CLARIFICATION: {
                "keywords": [
                    "clarify",
                    "explain more",
                    "what do you mean",
                    "elaborate",
                    "specify",
                    "detail",
                ],
                "patterns": [
                    r".+ (clarify|explain more|what do you mean|elaborate|specify|detail)"
                ],
                "weight": 0.7,
            },
            IntentType.SOCIAL: {
                "keywords": [
                    "hello",
                    "hi",
                    "hey",
                    "thanks",
                    "thank you",
                    "goodbye",
                    "bye",
                    "how are you",
                    "feeling",
                ],
                "patterns": [
                    r"^(hello|hi|hey|thanks|thank you|goodbye|bye|how are you)",
                    r".+ (feeling|doing)",
                ],
                "weight": 0.9,
            },
        }

        # Entity patterns
        self.entity_patterns = {
            EntityType.PERSON: [
                r"\b[A-Z][a-z]+ [A-Z][a-z]+\b",  # First Last
                r"\b(Mr|Mrs|Ms|Dr|Prof)\.?\s+[A-Z][a-z]+\b",  # Title + Name
            ],
            EntityType.ORGANIZATION: [
                r"\b[A-Z][a-z]+(?:\s+[A-Z][a-z]+)*(?:\s+Inc|Corp|LLC|Ltd|Co|Company|Corporation)\b",
                r"\b(Google|Microsoft|Apple|Amazon|Facebook|Tesla|OpenAI|GitHub)\b",
            ],
            EntityType.LOCATION: [
                r"\b[A-Z][a-z]+(?:\s+[A-Z][a-z]+)*(?:,\s*[A-Z]{2})?\b",  # City, State
                r"\b(United States|United Kingdom|New York|California|London|Paris|Tokyo)\b",
            ],
            EntityType.TECHNOLOGY: [
                r"\b(Python|JavaScript|Java|C\+\+|React|Angular|Vue|Node\.js|Django|Flask|FastAPI)\b",
                r"\b(AI|ML|machine learning|deep learning|neural network|algorithm|API|database|SQL|NoSQL)\b",
                r"\b(Docker|Kubernetes|AWS|Azure|GCP|Git|GitHub|GitLab|CI\/CD)\b",
            ],
            EntityType.TOOL: [
                r"\b(vim|emacs|vscode|visual studio|intellij|eclipse|postman|docker|kubectl)\b",
                r"\b(git|npm|pip|conda|brew|apt|yum|chocolatey)\b",
            ],
            EntityType.CONCEPT: [
                r"\b(agile|scrum|kanban|devops|microservices|monolith|serverless|saas|paas|iaas)\b",
                r"\b(mvc|mvp|mvvm|rest|graphql|grpc|oauth|jwt|ssl|tls)\b",
            ],
            EntityType.PROCESS: [
                r"\b(deployment|testing|development|design|planning|review|refactoring|optimization)\b",
                r"\b(onboarding|integration|migration|backup|restore|monitoring|logging)\b",
            ],
            EntityType.METRIC: [
                r"\b\d+%\b|\b\d+\.\d+%\b",  # Percentages
                r"\$\d+(?:,\d{3})*(?:\.\d{2})?\b",  # Currency
                r"\b\d+(?:\.\d+)?\s*(?:ms|s|min|hr|hours|days|weeks|months|years)\b",  # Time
            ],
            EntityType.DATE_TIME: [
                r"\b\d{1,2}\/\d{1,2}\/\d{4}\b",  # MM/DD/YYYY
                r"\b\d{4}-\d{2}-\d{2}\b",  # YYYY-MM-DD
                r"\b(January|February|March|April|May|June|July|August|September|October|November|December)\s+\d{1,2},?\s+\d{4}\b",
            ],
            EntityType.CODE: [
                r"`[^`]+`",  # Inline code
                r"```[\s\S]*?```",  # Code blocks
            ],
            EntityType.DOCUMENT: [
                r"\b\w+\.(pdf|doc|docx|txt|md|json|yaml|yml|xml|csv)\b",
                r"\b(README|CHANGELOG|LICENSE|CONTRIBUTING)\b",
            ],
        }

        # Thought tracking
        self.thoughts = {}
        self.thought_chain = deque(maxlen=100)
        self.entity_graph = defaultdict(set)
        self.intent_history = deque(maxlen=50)

    def detect_intent(self, text: str) -> Intent:
        """Detect the primary intent from user text"""
        text_lower = text.lower()
        scores = {}

        for intent_type, pattern_info in self.intent_patterns.items():
            score = 0.0

            # Check keywords
            keyword_matches = sum(
                1 for kw in pattern_info["keywords"] if kw in text_lower
            )
            if keyword_matches > 0:
                score += (keyword_matches / len(pattern_info["keywords"])) * 0.6

            # Check regex patterns
            pattern_matches = sum(
                1
                for pattern in pattern_info["patterns"]
                if re.search(pattern, text, re.IGNORECASE)
            )
            if pattern_matches > 0:
                score += (pattern_matches / len(pattern_info["patterns"])) * 0.4

            # Apply weight
            score *= pattern_info.get("weight", 1.0)

            if score > 0:
                scores[intent_type] = score

        # Select highest scoring intent
        if scores:
            best_intent = max(scores.items(), key=lambda x: x[1])

            # Extract relevant keywords
            keywords = []
            for kw in self.intent_patterns[best_intent[0]]["keywords"]:
                if kw in text_lower:
                    keywords.append(kw)

            return Intent(
                type=best_intent[0],
                confidence=min(best_intent[1], 1.0),
                keywords=keywords,
                context=text,
                parameters=self._extract_intent_parameters(best_intent[0], text),
            )

        # Default to exploration if no clear intent
        return Intent(
            type=IntentType.EXPLORATION,
            confidence=0.3,
            keywords=[],
            context=text,
            parameters={},
        )

    def _extract_intent_parameters(
        self, intent_type: IntentType, text: str
    ) -> Dict[str, Any]:
        """Extract parameters specific to the intent type"""
        params = {}

        if intent_type == IntentType.QUESTION:
            # Extract question words and what they're asking about
            if re.search(r"\bwhat\b", text, re.IGNORECASE):
                params["question_type"] = "what"
            elif re.search(r"\bwhy\b", text, re.IGNORECASE):
                params["question_type"] = "why"
            elif re.search(r"\bhow\b", text, re.IGNORECASE):
                params["question_type"] = "how"
            elif re.search(r"\bwhen\b", text, re.IGNORECASE):
                params["question_type"] = "when"
            elif re.search(r"\bwhere\b", text, re.IGNORECASE):
                params["question_type"] = "where"
            elif re.search(r"\bwho\b", text, re.IGNORECASE):
                params["question_type"] = "who"

        elif intent_type == IntentType.COMPARISON:
            # Extract items being compared
            vs_match = re.search(
                r"(.+?)\s+(?:versus|vs|compared to|or)\s+(.+)", text, re.IGNORECASE
            )
            if vs_match:
                params["item1"] = vs_match.group(1).strip()
                params["item2"] = vs_match.group(2).strip()

        elif intent_type == IntentType.PROBLEM_SOLVING:
            # Extract problem description
            error_match = re.search(
                r"(error|issue|problem|bug)[^:]*:\s*(.+)", text, re.IGNORECASE
            )
            if error_match:
                params["error_type"] = error_match.group(1)
                params["error_description"] = error_match.group(2)

        return params

    def extract_entities(self, text: str) -> List[Entity]:
        """Extract entities from text"""
        entities = []

        for entity_type, patterns in self.entity_patterns.items():
            for pattern in patterns:
                for match in re.finditer(pattern, text):
                    entity_text = match.group().strip()

                    # Calculate confidence based on pattern specificity
                    confidence = (
                        0.8
                        if entity_type
                        in [EntityType.TECHNOLOGY, EntityType.ORGANIZATION]
                        else 0.6
                    )

                    # Additional confidence boost for capitalized entities
                    if entity_text[0].isupper():
                        confidence += 0.1

                    # Extract context (surrounding words)
                    start = max(0, match.start() - 20)
                    end = min(len(text), match.end() + 20)
                    context = text[start:end].strip()

                    entity = Entity(
                        text=entity_text,
                        type=entity_type,
                        confidence=min(confidence, 1.0),
                        context=context,
                        start_pos=match.start(),
                        end_pos=match.end(),
                        metadata={
                            "pattern": pattern,
                            "detected_at": datetime.now().isoformat(),
                        },
                    )
                    entities.append(entity)

        # Remove duplicates and sort by confidence
        unique_entities = []
        seen = set()
        for entity in sorted(entities, key=lambda x: x.confidence, reverse=True):
            key = (entity.text.lower(), entity.type)
            if key not in seen:
                seen.add(key)
                unique_entities.append(entity)

        return unique_entities

    def create_thought_node(
        self, text: str, parent_ids: List[str] = None
    ) -> ThoughtNode:
        """Create a new thought node with intent and entities"""
        node_id = (
            f"thought_{len(self.thoughts) + 1}_{datetime.now().strftime('%H%M%S')}"
        )

        # Detect intent and extract entities
        intent = self.detect_intent(text)
        entities = self.extract_entities(text)

        # Calculate importance based on intent and entities
        importance = 0.5
        if intent.confidence > 0.8:
            importance += 0.2
        if len(entities) > 3:
            importance += 0.1
        if intent.type in [
            IntentType.PROBLEM_SOLVING,
            IntentType.COMMAND,
            IntentType.QUESTION,
        ]:
            importance += 0.2

        node = ThoughtNode(
            id=node_id,
            content=text,
            timestamp=datetime.now(),
            entities=entities,
            intent=intent,
            parent_ids=parent_ids or [],
            importance=min(importance, 1.0),
            metadata={
                "word_count": len(text.split()),
                "has_question": "?" in text,
                "has_code": bool(re.search(r"`[^`]+`|```[\s\S]*?```", text)),
            },
        )

        # Store the thought
        self.thoughts[node_id] = node
        self.thought_chain.append(node_id)

        # Update entity graph
        for entity in entities:
            self.entity_graph[entity.text.lower()].add(node_id)

        # Update intent history
        self.intent_history.append(intent.type.value)

        # Find cross-links to existing thoughts
        self._find_cross_links(node)

        return node

    def _find_cross_links(self, node: ThoughtNode):
        """Find cross-links between this thought and previous thoughts"""
        for other_id, other_node in self.thoughts.items():
            if other_id == node.id:
                continue

            # Check for shared entities
            shared_entities = set()
            for entity in node.entities:
                entity_key = entity.text.lower()
                if entity_key in self.entity_graph:
                    if other_id in self.entity_graph[entity_key]:
                        shared_entities.add(entity_key)

            # Check for intent similarity
            intent_similarity = (
                1.0 if node.intent.type == other_node.intent.type else 0.0
            )

            # Check for semantic similarity (simple keyword overlap)
            node_words = set(node.content.lower().split())
            other_words = set(other_node.content.lower().split())
            word_overlap = len(node_words & other_words) / max(
                len(node_words | other_words), 1
            )

            # Create cross-link if strong connection
            link_strength = (
                len(shared_entities) * 0.4
                + intent_similarity * 0.3
                + word_overlap * 0.3
            )
            if link_strength > 0.5:
                node.cross_links.append(other_id)
                other_node.cross_links.append(node.id)

    def get_thought_chain(self, limit: int = 10) -> List[ThoughtNode]:
        """Get the recent chain of thoughts"""
        recent_ids = list(self.thought_chain)[-limit:]
        return [self.thoughts[tid] for tid in recent_ids if tid in self.thoughts]

    def find_critical_links(self) -> List[Tuple[str, str, float]]:
        """Find critical cross-links between thoughts"""
        links = []

        for node_id, node in self.thoughts.items():
            for linked_id in node.cross_links:
                if linked_id in self.thoughts:
                    # Calculate link importance
                    importance = (
                        node.importance + self.thoughts[linked_id].importance
                    ) / 2

                    # Count shared entities
                    node_entities = {e.text.lower() for e in node.entities}
                    linked_entities = {
                        e.text.lower() for e in self.thoughts[linked_id].entities
                    }
                    shared_count = len(node_entities & linked_entities)

                    link_strength = importance * (1 + shared_count * 0.2)
                    links.append((node_id, linked_id, link_strength))

        # Sort by strength and return top links
        return sorted(links, key=lambda x: x[2], reverse=True)[:10]

    def get_entity_evolution(self, entity_name: str) -> List[ThoughtNode]:
        """Track how an entity evolves through the conversation"""
        entity_key = entity_name.lower()
        if entity_key not in self.entity_graph:
            return []

        thought_ids = self.entity_graph[entity_key]
        return [self.thoughts[tid] for tid in thought_ids if tid in self.thoughts]

    def get_intent_flow(self) -> Dict[str, Any]:
        """Analyze the flow of intents through conversation"""
        if not self.intent_history:
            return {}

        intent_counts = defaultdict(int)
        for intent in self.intent_history:
            intent_counts[intent] += 1

        # Detect intent transitions
        transitions = defaultdict(int)
        for i in range(1, len(self.intent_history)):
            transition = f"{self.intent_history[i-1]} → {self.intent_history[i]}"
            transitions[transition] += 1

        return {
            "total_intents": len(self.intent_history),
            "intent_distribution": dict(intent_counts),
            "common_transitions": dict(
                sorted(transitions.items(), key=lambda x: x[1], reverse=True)[:5]
            ),
            "current_focus": self.intent_history[-1] if self.intent_history else None,
        }

    def summarize_conversation_state(self) -> Dict[str, Any]:
        """Get a comprehensive summary of the conversation state"""
        recent_thoughts = self.get_thought_chain(5)
        critical_links = self.find_critical_links()
        intent_flow = self.get_intent_flow()

        # Extract key themes from recent entities
        recent_entities = []
        for thought in recent_thoughts:
            recent_entities.extend(thought.entities)

        entity_counts = defaultdict(int)
        for entity in recent_entities:
            entity_counts[entity.type.value] += 1

        return {
            "thought_count": len(self.thoughts),
            "recent_thoughts": [
                {
                    "id": t.id,
                    "content": (
                        t.content[:100] + "..." if len(t.content) > 100 else t.content
                    ),
                    "intent": t.intent.type.value,
                    "importance": t.importance,
                    "entity_count": len(t.entities),
                }
                for t in recent_thoughts
            ],
            "critical_links": [
                {"from": link[0], "to": link[1], "strength": link[2]}
                for link in critical_links[:5]
            ],
            "intent_flow": intent_flow,
            "entity_distribution": dict(entity_counts),
            "most_connected_entities": [
                entity
                for entity, connections in sorted(
                    [(e, len(ids)) for e, ids in self.entity_graph.items()],
                    key=lambda x: x[1],
                    reverse=True,
                )[:5]
            ],
        }


# Global intent awareness engine
intent_engine = IntentAwarenessEngine()
