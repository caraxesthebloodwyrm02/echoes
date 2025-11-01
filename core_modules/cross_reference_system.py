"""
Contextual Cross-Reference System - Intelligent understanding and cross-referencing
Provides deep contextual understanding and meaningful connections across topics
"""
import logging
import re
import random
from typing import Dict, Any, List, Optional, Set, Tuple
from datetime import datetime
from collections import defaultdict, deque
import json

logger = logging.getLogger(__name__)

class CrossReferenceSystem:
    """Intelligent system for understanding and cross-referencing concepts"""
    
    def __init__(self):
        # Knowledge domains and their relationships
        self.domains = {
            "technology": {
                "keywords": ["software", "hardware", "programming", "algorithm", "data", "system", "network"],
                "related": ["science", "mathematics", "engineering", "business"],
                "concepts": ["abstraction", "optimization", "scalability", "efficiency", "automation"]
            },
            "science": {
                "keywords": ["research", "experiment", "theory", "hypothesis", "analysis", "discovery"],
                "related": ["mathematics", "technology", "philosophy", "medicine"],
                "concepts": ["causality", "correlation", "empiricism", "falsifiability", "peer review"]
            },
            "business": {
                "keywords": ["market", "strategy", "revenue", "customer", "product", "competition"],
                "related": ["economics", "psychology", "technology", "law"],
                "concepts": ["value proposition", "competitive advantage", "ROI", "market fit", "scalability"]
            },
            "mathematics": {
                "keywords": ["equation", "theorem", "proof", "logic", "calculation", "pattern"],
                "related": ["science", "technology", "philosophy", "art"],
                "concepts": ["elegance", "rigor", "abstraction", "generalization", "formalism"]
            },
            "art": {
                "keywords": ["creative", "design", "aesthetic", "expression", "style", "medium"],
                "related": ["psychology", "technology", "philosophy", "mathematics"],
                "concepts": ["composition", "harmony", "contrast", "narrative", "symbolism"]
            },
            "philosophy": {
                "keywords": ["ethics", "logic", "metaphysics", "epistemology", "reasoning", "meaning"],
                "related": ["psychology", "mathematics", "science", "art"],
                "concepts": ["dualism", "rationalism", "empiricism", "existentialism", "utilitarianism"]
            },
            "psychology": {
                "keywords": ["behavior", "cognition", "emotion", "mental", "therapy", "development"],
                "related": ["biology", "sociology", "philosophy", "business"],
                "concepts": ["cognitive bias", "motivation", "learning", "personality", "social dynamics"]
            },
        }
        
        # Concept mapping for deeper understanding
        self.concept_map = defaultdict(set)
        self._build_concept_map()
        
        # Conversation context tracking
        self.conversation_history = deque(maxlen=50)
        self.topic_flow = []
        self.user_interests = defaultdict(float)
        
        # Analogy and metaphor database
        self.analogies = {
            "programming": ["like writing a recipe", "like giving directions", "like conducting an orchestra"],
            "learning": ["like building a house", "like growing a garden", "like solving a puzzle"],
            "problem solving": ["like detective work", "like navigating a maze", "like untangling knots"],
            "creativity": ["like exploring new territory", "like mixing colors", "like improvising music"],
        }
        
        # Pattern recognition for common themes
        self.patterns = {
            "cause_effect": ["because", "therefore", "leads to", "results in", "causes"],
            "comparison": ["like", "similar to", "unlike", "different from", "whereas"],
            "process": ["first", "then", "next", "finally", "step by step"],
            "classification": ["types of", "kinds of", "categories", "groups", "classes"],
        }
    
    def _build_concept_map(self):
        """Build a comprehensive concept mapping"""
        for domain, info in self.domains.items():
            for keyword in info["keywords"]:
                self.concept_map[keyword].add(domain)
            for concept in info["concepts"]:
                self.concept_map[concept].add(domain)
    
    def analyze_context(self, text: str) -> Dict[str, Any]:
        """Analyze text to extract contextual information"""
        text_lower = text.lower()
        
        # Identify domains
        identified_domains = set()
        domain_scores = defaultdict(float)
        
        for domain, info in self.domains.items():
            score = 0
            for keyword in info["keywords"]:
                if keyword in text_lower:
                    score += text_lower.count(keyword)
            for concept in info["concepts"]:
                if concept in text_lower:
                    score += text_lower.count(concept) * 1.5  # Concepts weighted higher
            
            if score > 0:
                identified_domains.add(domain)
                domain_scores[domain] = score
        
        # Detect patterns
        detected_patterns = []
        for pattern_type, indicators in self.patterns.items():
            if any(indicator in text_lower for indicator in indicators):
                detected_patterns.append(pattern_type)
        
        # Extract key concepts
        key_concepts = self._extract_key_concepts(text)
        
        # Identify relationships
        relationships = self._identify_relationships(text, identified_domains)
        
        return {
            "domains": list(identified_domains),
            "domain_scores": dict(domain_scores),
            "patterns": detected_patterns,
            "key_concepts": key_concepts,
            "relationships": relationships,
            "complexity": self._assess_complexity(text),
            "sentiment": self._detect_sentiment(text),
        }
    
    def _extract_key_concepts(self, text: str) -> List[str]:
        """Extract key concepts from text"""
        # Simple extraction based on capitalized words and domain keywords
        concepts = []
        
        # Find capitalized words (potential concepts)
        capitalized = re.findall(r'\b[A-Z][a-z]+(?:[A-Z][a-z]+)*\b', text)
        concepts.extend(capitalized)
        
        # Find domain-specific terms
        text_lower = text.lower()
        for domain, info in self.domains.items():
            for concept in info["concepts"]:
                if concept in text_lower:
                    concepts.append(concept)
        
        # Remove duplicates and return
        return list(set(concepts))
    
    def _identify_relationships(self, text: str, domains: Set[str]) -> List[Dict[str, str]]:
        """Identify relationships between concepts and domains"""
        relationships = []
        text_lower = text.lower()
        
        # Check for domain connections
        for domain in domains:
            related_domains = self.domains[domain]["related"]
            for related in related_domains:
                if related in domains:
                    relationships.append({
                        "type": "domain_connection",
                        "from": domain,
                        "to": related,
                        "nature": "interdisciplinary"
                    })
        
        # Check for causal relationships
        if any(word in text_lower for word in ["because", "causes", "leads to", "results in"]):
            relationships.append({
                "type": "causal",
                "nature": "cause_effect"
            })
        
        # Check for comparisons
        if any(word in text_lower for word in ["like", "similar", "unlike", "different"]):
            relationships.append({
                "type": "comparison",
                "nature": "analogy_or_contrast"
            })
        
        return relationships
    
    def _assess_complexity(self, text: str) -> str:
        """Assess the complexity of the text"""
        sentences = text.split('.')
        avg_sentence_length = sum(len(s.split()) for s in sentences) / len(sentences) if sentences else 0
        
        # Count technical terms
        tech_terms = 0
        text_lower = text.lower()
        for domain_info in self.domains.values():
            tech_terms += sum(1 for term in domain_info["keywords"] if term in text_lower)
            tech_terms += sum(1 for concept in domain_info["concepts"] if concept in text_lower)
        
        if avg_sentence_length > 20 or tech_terms > 5:
            return "high"
        elif avg_sentence_length > 12 or tech_terms > 2:
            return "medium"
        else:
            return "low"
    
    def _detect_sentiment(self, text: str) -> str:
        """Simple sentiment detection"""
        positive_words = ["good", "great", "excellent", "amazing", "wonderful", "fantastic", "love", "perfect"]
        negative_words = ["bad", "terrible", "awful", "hate", "worst", "horrible", "difficult", "problem"]
        
        text_lower = text.lower()
        positive_count = sum(1 for word in positive_words if word in text_lower)
        negative_count = sum(1 for word in negative_words if word in text_lower)
        
        if positive_count > negative_count:
            return "positive"
        elif negative_count > positive_count:
            return "negative"
        else:
            return "neutral"
    
    def generate_cross_references(self, context: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Generate relevant cross-references based on context"""
        cross_refs = []
        
        domains = context.get("domains", [])
        key_concepts = context.get("key_concepts", [])
        
        # Cross-reference between domains
        for domain in domains:
            related_domains = self.domains[domain]["related"]
            for related in related_domains:
                if related in domains:
                    cross_refs.append({
                        "type": "interdisciplinary",
                        "connection": f"{domain} ↔ {related}",
                        "explanation": f"The principles of {domain} often apply to {related}",
                        "example": self._get_interdisciplinary_example(domain, related)
                    })
        
        # Concept-based cross-references
        for concept in key_concepts:
            related_concepts = self._find_related_concepts(concept)
            for related in related_concepts:
                cross_refs.append({
                    "type": "conceptual",
                    "connection": f"{concept} → {related}",
                    "explanation": f"{concept} is closely related to {related}",
                    "insight": self._get_concept_insight(concept, related)
                })
        
        return cross_refs[:5]  # Return top 5
    
    def _find_related_concepts(self, concept: str) -> List[str]:
        """Find concepts related to the given concept"""
        related = []
        concept_lower = concept.lower()
        
        for domain, info in self.domains.items():
            for domain_concept in info["concepts"]:
                if domain_concept != concept and (
                    concept_lower in domain_concept.lower() or 
                    domain_concept.lower() in concept_lower
                ):
                    related.append(domain_concept)
        
        return related[:3]
    
    def _get_interdisciplinary_example(self, domain1: str, domain2: str) -> str:
        """Get an example showing the connection between two domains"""
        examples = {
            ("technology", "business"): "Using technology to create business value through automation and efficiency",
            ("science", "mathematics"): "Mathematical models that describe scientific phenomena and predict outcomes",
            ("art", "psychology"): "How artistic expression affects human psychology and emotional wellbeing",
            ("philosophy", "technology"): "Ethical considerations in technological development and AI",
            ("psychology", "business"): "Understanding consumer behavior to improve business strategies",
        }
        
        key = (domain1, domain2) if (domain1, domain2) in examples else (domain2, domain1)
        return examples.get(key, f"The intersection of {domain1} and {domain2} offers unique insights")
    
    def _get_concept_insight(self, concept1: str, concept2: str) -> str:
        """Get an insight about the relationship between two concepts"""
        return f"Understanding {concept1} helps clarify {concept2} through shared principles and patterns"
    
    def create_contextual_analogy(self, topic: str, target_domain: str) -> str:
        """Create an analogy explaining a topic in terms of another domain"""
        if topic.lower() in self.analogies:
            analogies = self.analogies[topic.lower()]
            return f"{topic} is {random.choice(analogies)}."
        
        # Generate custom analogy
        if target_domain in self.domains:
            domain_info = self.domains[target_domain]
            key_concept = random.choice(domain_info["concepts"])
            return f"Think of {topic} like {key_concept} in {target_domain} - it follows similar principles."
        
        return f"{topic} can be understood through patterns and relationships that appear in many fields."
    
    def track_conversation_flow(self, user_message: str, assistant_response: str):
        """Track the flow of conversation to understand context better"""
        context = self.analyze_context(user_message)
        
        # Update conversation history
        self.conversation_history.append({
            "timestamp": datetime.now().isoformat(),
            "user_message": user_message,
            "assistant_response": assistant_response,
            "context": context
        })
        
        # Track topic evolution
        if context["domains"]:
            self.topic_flow.append({
                "timestamp": datetime.now().isoformat(),
                "domains": context["domains"],
                "key_concepts": context["key_concepts"]
            })
        
        # Update user interests
        for domain in context["domains"]:
            self.user_interests[domain] += 0.1
        
        # Keep only recent interests
        if len(self.user_interests) > 10:
            sorted_interests = sorted(self.user_interests.items(), key=lambda x: x[1], reverse=True)
            self.user_interests = dict(sorted_interests[:8])
    
    def get_contextual_suggestions(self, current_topic: str) -> List[str]:
        """Get suggestions based on conversation context and user interests"""
        suggestions = []
        
        # Based on user interests
        if self.user_interests:
            top_interest = max(self.user_interests.items(), key=lambda x: x[1])
            suggestions.append(f"Since you're interested in {top_interest[0]}, we could explore how it connects to {current_topic}")
        
        # Based on conversation flow
        if self.topic_flow:
            recent_domains = self.topic_flow[-1]["domains"]
            for domain in recent_domains:
                if domain != current_topic.lower():
                    suggestions.append(f"Let's connect {current_topic} to what we discussed about {domain}")
        
        # Based on patterns
        suggestions.append("Have you considered the broader implications of this?")
        suggestions.append("How might this apply in a different context?")
        
        return suggestions[:3]
    
    def get_knowledge_graph_summary(self) -> Dict[str, Any]:
        """Get a summary of the knowledge graph and connections"""
        return {
            "total_domains": len(self.domains),
            "domain_connections": sum(len(info["related"]) for info in self.domains.values()),
            "conversation_topics": list(self.user_interests.keys()),
            "topic_evolution": self.topic_flow[-5:] if self.topic_flow else [],
            "concept_depth": len(self.concept_map),
        }

# Global cross-reference system instance
cross_reference_system = CrossReferenceSystem()
