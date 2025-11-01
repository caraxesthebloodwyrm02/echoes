"""
Train of Thought Tracker - Maintains chains of reasoning and identifies critical cross-links
Tracks the flow of ideas, connections between concepts, and emergent patterns
"""
import logging
import json
from typing import Dict, Any, List, Optional, Set, Tuple, NamedTuple
from datetime import datetime, timedelta
from collections import defaultdict, deque
from dataclasses import dataclass, field, asdict
from enum import Enum

try:
    import networkx as nx
    NETWORKX_AVAILABLE = True
except ImportError:
    nx = None
    NETWORKX_AVAILABLE = False
    logger = logging.getLogger(__name__)
    logger.warning("NetworkX not available. Graph features will be limited.")

logger = logging.getLogger(__name__)

class ThoughtType(Enum):
    """Types of thoughts in the chain"""
    HYPOTHESIS = "hypothesis"
    QUESTION = "question"
    OBSERVATION = "observation"
    CONCLUSION = "conclusion"
    ANALYSIS = "analysis"
    SYNTHESIS = "synthesis"
    CRITIQUE = "critique"
    INSIGHT = "insight"
    DECISION = "decision"
    ACTION = "action"

class LinkType(Enum):
    """Types of links between thoughts"""
    CAUSAL = "causal"  # A causes B
    LOGICAL = "logical"  # A logically follows B
    CONTRADICTORY = "contradictory"  # A contradicts B
    SUPPORTING = "supporting"  # A supports B
    REFINING = "refining"  # A refines B
    GENERALIZING = "generalizing"  # A generalizes from B
    SPECIFYING = "specifying"  # A specifies B
    ANALOGICAL = "analogical"  # A is analogous to B
    TEMPORAL = "temporal"  # A occurs before B
    CRITICAL = "critical"  # Critical cross-link between different chains

@dataclass
class ThoughtLink:
    """Represents a link between two thoughts"""
    from_thought: str
    to_thought: str
    link_type: LinkType
    strength: float  # 0.0 to 1.0
    evidence: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class ThoughtChain:
    """A chain of connected thoughts"""
    id: str
    thoughts: List[str]  # Thought IDs in order
    start_time: datetime
    end_time: Optional[datetime] = None
    theme: str = ""
    confidence: float = 0.5
    resolved: bool = False
    metadata: Dict[str, Any] = field(default_factory=dict)

class TrainOfThoughtTracker:
    """Tracks and analyzes trains of thought"""
    
    def __init__(self):
        # Network representation of thoughts (fallback to dict if networkx not available)
        if NETWORKX_AVAILABLE:
            self.thought_network = nx.DiGraph()
        else:
            self.thought_network = {}  # Fallback to dict
        self.thought_metadata = {}
        
        # Chain tracking
        self.chains = {}
        self.active_chains = set()
        self.chain_history = deque(maxlen=100)
        
        # Link patterns and heuristics
        self.link_indicators = {
            LinkType.CAUSAL: [
                "because", "since", "due to", "as a result", "therefore", "thus", "hence", "consequently",
                "leads to", "causes", "results in", "triggers", "provokes", "elicits"
            ],
            LinkType.LOGICAL: [
                "therefore", "thus", "hence", "consequently", "so", "then", "accordingly", "for this reason",
                "it follows that", "logically", "necessarily", "must be", "implies"
            ],
            LinkType.CONTRADICTORY: [
                "but", "however", "although", "despite", "whereas", "while", "conversely", "on the other hand",
                "in contrast", "nevertheless", "nonetheless", "yet", "still"
            ],
            LinkType.SUPPORTING: [
                "also", "additionally", "furthermore", "moreover", "in addition", "besides", "what's more",
                "similarly", "likewise", "in the same way", "equally"
            ],
            LinkType.REFINING: [
                "specifically", "particularly", "especially", "notably", "in particular", "more precisely",
                "to be more specific", "that is to say", "i.e.", "namely"
            ],
            LinkType.GENERALIZING: [
                "in general", "generally", "typically", "usually", "commonly", "often", "broadly",
                "overall", "in most cases", "as a rule"
            ],
            LinkType.ANALOGICAL: [
                "like", "similar to", "analogous to", "comparable to", "just as", "in the same way as",
                "resembles", "mirrors", "reflects", "is like"
            ]
        }
        
        # Critical link detection thresholds
        self.critical_link_thresholds = {
            "cross_chain_strength": 0.7,
            "entity_overlap": 0.6,
            "concept_similarity": 0.8,
            "temporal_proximity": 300  # 5 minutes
        }
        
        # Pattern detection
        self.pattern_detectors = {
            "problem_solution": self._detect_problem_solution_pattern,
            "hypothesis_testing": self._detect_hypothesis_testing_pattern,
            "iterative_refinement": self._detect_iterative_refinement_pattern,
            "concept_synthesis": self._detect_concept_synthesis_pattern,
            "decision_making": self._detect_decision_making_pattern,
        }
    
    def add_thought(self, thought_id: str, content: str, thought_type: ThoughtType, 
                    entities: List[str] = None, parent_thoughts: List[str] = None) -> str:
        """Add a new thought to the tracker"""
        
        # Add to network (conditional on networkx availability)
        if NETWORKX_AVAILABLE:
            self.thought_network.add_node(thought_id)
        else:
            # Fallback: just store in dict
            if thought_id not in self.thought_network:
                self.thought_network[thought_id] = {}
        
        # Store metadata
        self.thought_metadata[thought_id] = {
            "content": content,
            "type": thought_type.value,
            "entities": entities or [],
            "timestamp": datetime.now(),
            "parents": parent_thoughts or [],
            "children": [],
            "cross_links": [],
            "importance": self._calculate_thought_importance(content, thought_type, entities),
        }
        
        # Link to parent thoughts
        if parent_thoughts:
            for parent_id in parent_thoughts:
                if NETWORKX_AVAILABLE:
                    if parent_id in self.thought_network:
                        link_type = self._infer_link_type(content, parent_id)
                        strength = self._calculate_link_strength(thought_id, parent_id, link_type)
                        
                        self._create_link(parent_id, thought_id, link_type, strength)
                        
                        # Update parent/child relationships
                        self.thought_metadata[parent_id]["children"].append(thought_id)
                        self.thought_metadata[thought_id]["parents"].append(parent_id)
                else:
                    # Fallback: just update metadata
                    if parent_id in self.thought_metadata:
                        self.thought_metadata[parent_id]["children"].append(thought_id)
                        self.thought_metadata[thought_id]["parents"].append(parent_id)
        
        # Update or create chains
        self._update_chains(thought_id)
        
        # Find critical cross-links
        self._find_critical_cross_links(thought_id)
        
        return thought_id
    
    def _calculate_thought_importance(self, content: str, thought_type: ThoughtType, entities: List[str]) -> float:
        """Calculate the importance score of a thought"""
        importance = 0.5  # Base importance
        
        # Type-based importance
        type_importance = {
            ThoughtType.INSIGHT: 0.9,
            ThoughtType.DECISION: 0.8,
            ThoughtType.CONCLUSION: 0.7,
            ThoughtType.HYPOTHESIS: 0.6,
            ThoughtType.QUESTION: 0.6,
            ThoughtType.ANALYSIS: 0.5,
            ThoughtType.OBSERVATION: 0.4,
            ThoughtType.SYNTHESIS: 0.7,
            ThoughtType.CRITIQUE: 0.5,
            ThoughtType.ACTION: 0.8,
        }
        
        importance += type_importance.get(thought_type, 0.5) * 0.3
        
        # Content-based importance
        if any(indicator in content.lower() for indicator in ["important", "critical", "key", "essential"]):
            importance += 0.1
        
        # Entity-based importance
        if entities and len(entities) > 2:
            importance += 0.1
        
        # Length-based importance (longer thoughts might be more detailed)
        if len(content.split()) > 20:
            importance += 0.1
        
        return min(importance, 1.0)
    
    def _infer_link_type(self, content: str, parent_id: str) -> LinkType:
        """Infer the type of link based on content analysis"""
        if parent_id not in self.thought_metadata:
            return LinkType.LOGICAL
        
        parent_content = self.thought_metadata[parent_id]["content"]
        combined_text = f"{parent_content} {content}".lower()
        
        # Check for link type indicators
        for link_type, indicators in self.link_indicators.items():
            if any(indicator in combined_text for indicator in indicators):
                return link_type
        
        # Default inference based on thought types
        parent_type = ThoughtType(self.thought_metadata[parent_id]["type"])
        current_type = ThoughtType(self.thought_metadata[parent_id]["type"])
        
        if parent_type == ThoughtType.QUESTION and current_type == ThoughtType.ANALYSIS:
            return LinkType.LOGICAL
        elif parent_type == ThoughtType.HYPOTHESIS and current_type == ThoughtType.CONCLUSION:
            return LinkType.LOGICAL
        elif parent_type == ThoughtType.OBSERVATION and current_type == ThoughtType.INSIGHT:
            return LinkType.CAUSAL
        elif parent_type == ThoughtType.ANALYSIS and current_type == ThoughtType.SYNTHESIS:
            return LinkType.SUPPORTING
        
        return LinkType.LOGICAL
    
    def _calculate_link_strength(self, from_id: str, to_id: str, link_type: LinkType) -> float:
        """Calculate the strength of a link between two thoughts"""
        if from_id not in self.thought_metadata or to_id not in self.thought_metadata:
            return 0.5
        
        from_meta = self.thought_metadata[from_id]
        to_meta = self.thought_metadata[to_id]
        
        # Base strength by link type
        type_strength = {
            LinkType.CRITICAL: 0.9,
            LinkType.CAUSAL: 0.8,
            LinkType.LOGICAL: 0.7,
            LinkType.CONTRADICTORY: 0.6,
            LinkType.SUPPORTING: 0.5,
            LinkType.REFINING: 0.6,
            LinkType.GENERALIZING: 0.5,
            LinkType.SPECIFYING: 0.6,
            LinkType.ANALOGICAL: 0.4,
            LinkType.TEMPORAL: 0.3,
        }
        
        strength = type_strength.get(link_type, 0.5)
        
        # Entity overlap bonus
        from_entities = set(from_meta["entities"])
        to_entities = set(to_meta["entities"])
        if from_entities and to_entities:
            overlap = len(from_entities & to_entities) / len(from_entities | to_entities)
            strength += overlap * 0.2
        
        # Temporal proximity bonus
        time_diff = (to_meta["timestamp"] - from_meta["timestamp"]).total_seconds()
        if time_diff < 60:  # Within 1 minute
            strength += 0.1
        elif time_diff < 300:  # Within 5 minutes
            strength += 0.05
        
        # Importance alignment bonus
        importance_diff = abs(from_meta["importance"] - to_meta["importance"])
        strength += (1.0 - importance_diff) * 0.1
        
        return min(strength, 1.0)
    
    def _create_link(self, from_id: str, to_id: str, link_type: LinkType, strength: float):
        """Create a link between two thoughts"""
        if self.thought_network.has_edge(from_id, to_id):
            # Update existing link if stronger
            existing = self.thought_network[from_id][to_id]
            if strength > existing.get("strength", 0):
                self.thought_network[from_id][to_id].update({
                    "link_type": link_type.value,
                    "strength": strength,
                    "updated_at": datetime.now().isoformat()
                })
        else:
            self.thought_network.add_edge(from_id, to_id, 
                link_type=link_type.value,
                strength=strength,
                created_at=datetime.now().isoformat()
            )
    
    def _update_chains(self, thought_id: str):
        """Update thought chains based on the new thought"""
        thought_meta = self.thought_metadata[thought_id]
        
        # Try to extend existing chains
        for chain_id, chain in list(self.chains.items()):
            if chain.resolved:
                continue
            
            # Check if this thought naturally extends the chain
            if self._should_extend_chain(chain, thought_id):
                chain.thoughts.append(thought_id)
                chain.end_time = datetime.now()
                chain.confidence = min(chain.confidence + 0.1, 1.0)
                self.active_chains.add(chain_id)
                return
        
        # Create new chain if no existing chain fits
        if thought_meta["type"] in [ThoughtType.HYPOTHESIS.value, ThoughtType.QUESTION.value]:
            new_chain = ThoughtChain(
                id=f"chain_{len(self.chains) + 1}_{datetime.now().strftime('%H%M%S')}",
                thoughts=[thought_id],
                start_time=datetime.now(),
                theme=self._extract_theme(thought_id),
                confidence=0.5
            )
            self.chains[new_chain.id] = new_chain
            self.active_chains.add(new_chain.id)
    
    def _should_extend_chain(self, chain: ThoughtChain, thought_id: str) -> bool:
        """Determine if a thought should extend an existing chain"""
        if not chain.thoughts:
            return False
        
        last_thought_id = chain.thoughts[-1]
        if last_thought_id not in self.thought_metadata:
            return False
        
        # Check if directly linked
        if self.thought_network.has_edge(last_thought_id, thought_id):
            return True
        
        # Check thematic consistency
        chain_theme = chain.theme.lower()
        thought_theme = self._extract_theme(thought_id).lower()
        
        # Simple theme overlap check
        theme_words = set(chain_theme.split())
        thought_words = set(thought_theme.split())
        
        if theme_words and thought_words:
            overlap = len(theme_words & thought_words) / len(theme_words | thought_words)
            return overlap > 0.3
        
        return False
    
    def _extract_theme(self, thought_id: str) -> str:
        """Extract the theme/topic of a thought"""
        if thought_id not in self.thought_metadata:
            return ""
        
        content = self.thought_metadata[thought_id]["content"]
        entities = self.thought_metadata[thought_id]["entities"]
        
        # Use entities as primary theme indicators
        if entities:
            return " ".join(entities[:3])  # Top 3 entities
        
        # Fallback to keyword extraction (simple)
        words = content.lower().split()
        # Filter out common words
        filtered = [w for w in words if len(w) > 3 and w not in 
                   ["this", "that", "with", "from", "they", "have", "been", "said", "each"]]
        
        return " ".join(filtered[:5]) if filtered else content[:50]
    
    def _find_critical_cross_links(self, thought_id: str):
        """Find critical cross-links between different thought chains"""
        if thought_id not in self.thought_metadata:
            return
        
        current_entities = set(self.thought_metadata[thought_id]["entities"])
        current_chain = self._get_thought_chain(thought_id)
        
        for other_id, other_meta in self.thought_metadata.items():
            if other_id == thought_id:
                continue
            
            other_chain = self._get_thought_chain(other_id)
            
            # Only consider cross-chain links
            if current_chain == other_chain:
                continue
            
            # Check for strong entity overlap
            other_entities = set(other_meta["entities"])
            if current_entities and other_entities:
                overlap = len(current_entities & other_entities) / len(current_entities | other_entities)
                
                if overlap > self.critical_link_thresholds["entity_overlap"]:
                    # Create critical cross-link
                    self._create_link(thought_id, other_id, LinkType.CRITICAL, overlap)
                    
                    # Update cross-links in metadata
                    self.thought_metadata[thought_id]["cross_links"].append(other_id)
                    self.thought_metadata[other_id]["cross_links"].append(thought_id)
    
    def _get_thought_chain(self, thought_id: str) -> Optional[str]:
        """Get the chain that contains a thought"""
        for chain_id, chain in self.chains.items():
            if thought_id in chain.thoughts:
                return chain_id
        return None
    
    def detect_patterns(self) -> Dict[str, List[Dict[str, Any]]]:
        """Detect various patterns in the train of thought"""
        patterns = {}
        
        for pattern_name, detector in self.pattern_detectors.items():
            try:
                patterns[pattern_name] = detector()
            except Exception as e:
                logger.warning(f"Pattern detector {pattern_name} failed: {e}")
                patterns[pattern_name] = []
        
        return patterns
    
    def _detect_problem_solution_pattern(self) -> List[Dict[str, Any]]:
        """Detect problem-solution patterns"""
        patterns = []
        
        for chain_id, chain in self.chains.items():
            if len(chain.thoughts) < 2:
                continue
            
            problem_thoughts = []
            solution_thoughts = []
            
            for thought_id in chain.thoughts:
                if thought_id not in self.thought_metadata:
                    continue
                
                meta = self.thought_metadata[thought_id]
                content = meta["content"].lower()
                
                if any(word in content for word in ["problem", "issue", "error", "bug", "challenge", "difficulty"]):
                    problem_thoughts.append(thought_id)
                elif any(word in content for word in ["solution", "fix", "resolve", "solve", "answer", "implement"]):
                    solution_thoughts.append(thought_id)
            
            if problem_thoughts and solution_thoughts:
                patterns.append({
                    "chain_id": chain_id,
                    "pattern": "problem_solution",
                    "problems": problem_thoughts,
                    "solutions": solution_thoughts,
                    "confidence": min(len(problem_thoughts) + len(solution_thoughts), 10) / 10
                })
        
        return patterns
    
    def _detect_hypothesis_testing_pattern(self) -> List[Dict[str, Any]]:
        """Detect hypothesis-testing patterns"""
        patterns = []
        
        for chain_id, chain in self.chains.items():
            hypotheses = []
            tests = []
            conclusions = []
            
            for thought_id in chain.thoughts:
                if thought_id not in self.thought_metadata:
                    continue
                
                meta = self.thought_metadata[thought_id]
                thought_type = meta["type"]
                
                if thought_type == ThoughtType.HYPOTHESIS.value:
                    hypotheses.append(thought_id)
                elif thought_type == ThoughtType.ANALYSIS.value:
                    tests.append(thought_id)
                elif thought_type == ThoughtType.CONCLUSION.value:
                    conclusions.append(thought_id)
            
            if hypotheses and (tests or conclusions):
                patterns.append({
                    "chain_id": chain_id,
                    "pattern": "hypothesis_testing",
                    "hypotheses": hypotheses,
                    "tests": tests,
                    "conclusions": conclusions,
                    "confidence": 0.8
                })
        
        return patterns
    
    def _detect_iterative_refinement_pattern(self) -> List[Dict[str, Any]]:
        """Detect iterative refinement patterns"""
        patterns = []
        
        # Look for chains with multiple refinement links
        for chain_id, chain in self.chains.items():
            refinement_links = 0
            
            for i in range(len(chain.thoughts) - 1):
                from_id = chain.thoughts[i]
                to_id = chain.thoughts[i + 1]
                
                if self.thought_network.has_edge(from_id, to_id):
                    edge_data = self.thought_network[from_id][to_id]
                    if edge_data.get("link_type") == LinkType.REFINING.value:
                        refinement_links += 1
            
            if refinement_links >= 2:
                patterns.append({
                    "chain_id": chain_id,
                    "pattern": "iterative_refinement",
                    "refinement_count": refinement_links,
                    "confidence": min(refinement_links / 5, 1.0)
                })
        
        return patterns
    
    def _detect_concept_synthesis_pattern(self) -> List[Dict[str, Any]]:
        """Detect concept synthesis patterns"""
        patterns = []
        
        # Look for thoughts that synthesize multiple previous concepts
        for thought_id, meta in self.thought_metadata.items():
            if meta["type"] == ThoughtType.SYNTHESIS.value:
                # Check if it has multiple parents from different chains
                parent_chains = set()
                for parent_id in meta["parents"]:
                    parent_chain = self._get_thought_chain(parent_id)
                    if parent_chain:
                        parent_chains.add(parent_chain)
                
                if len(parent_chains) > 1:
                    patterns.append({
                        "thought_id": thought_id,
                        "pattern": "concept_synthesis",
                        "source_chains": list(parent_chains),
                        "confidence": 0.9
                    })
        
        return patterns
    
    def _detect_decision_making_pattern(self) -> List[Dict[str, Any]]:
        """Detect decision-making patterns"""
        patterns = []
        
        for chain_id, chain in self.chains.items():
            decisions = []
            analyses = []
            
            for thought_id in chain.thoughts:
                if thought_id not in self.thought_metadata:
                    continue
                
                meta = self.thought_metadata[thought_id]
                thought_type = meta["type"]
                
                if thought_type == ThoughtType.DECISION.value:
                    decisions.append(thought_id)
                elif thought_type == ThoughtType.ANALYSIS.value:
                    analyses.append(thought_id)
            
            if decisions and analyses:
                patterns.append({
                    "chain_id": chain_id,
                    "pattern": "decision_making",
                    "analyses": analyses,
                    "decisions": decisions,
                    "confidence": 0.8
                })
        
        return patterns
    
    def get_critical_insights(self) -> List[Dict[str, Any]]:
        """Extract critical insights from the thought network"""
        insights = []
        
        # High-importance thoughts with many connections
        for thought_id, meta in self.thought_metadata.items():
            importance = meta["importance"]
            connections = len(self.thought_network.in_edges(thought_id)) + len(self.thought_network.out_edges(thought_id))
            
            if importance > 0.7 and connections > 2:
                insights.append({
                    "thought_id": thought_id,
                    "content": meta["content"][:200] + "..." if len(meta["content"]) > 200 else meta["content"],
                    "importance": importance,
                    "connections": connections,
                    "type": meta["type"],
                    "entities": meta["entities"],
                    "insight_type": "high_importance_hub"
                })
        
        # Thoughts with critical cross-links
        for thought_id, meta in self.thought_metadata.items():
            if meta["cross_links"]:
                insights.append({
                    "thought_id": thought_id,
                    "content": meta["content"][:200] + "..." if len(meta["content"]) > 200 else meta["content"],
                    "cross_links": meta["cross_links"],
                    "insight_type": "cross_chain_connector"
                })
        
        # Sort by importance and return top insights
        return sorted(insights, key=lambda x: x.get("importance", 0), reverse=True)[:10]
    
    def export_thought_network(self) -> Dict[str, Any]:
        """Export the entire thought network for analysis"""
        export_data = {
            "thoughts": self.thought_metadata,
            "links": [],
            "chains": {cid: asdict(chain) for cid, chain in self.chains.items()},
            "patterns": self.detect_patterns(),
            "critical_insights": self.get_critical_insights(),
            "export_timestamp": datetime.now().isoformat()
        }
        
        # Export links
        for from_id, to_id, data in self.thought_network.edges(data=True):
            export_data["links"].append({
                "from": from_id,
                "to": to_id,
                "type": data.get("link_type"),
                "strength": data.get("strength"),
                "created_at": data.get("created_at")
            })
        
        return export_data

# Global train of thought tracker
thought_tracker = TrainOfThoughtTracker()
