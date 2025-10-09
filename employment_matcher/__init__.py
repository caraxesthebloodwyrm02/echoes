# Employment Opportunity Matcher
# Semantic Skill Matching with Conceptual Foundation

"""
SEMANTIC_DIMENSIONS define what "semantic" really means in this context:
- intent_understanding: What the skill actually accomplishes (not just the label)
- context_awareness: How the skill applies in different domains/roles
- relationship_mapping: How skills relate and complement each other
"""

SEMANTIC_DIMENSIONS = {
    "intent_understanding": "What the skill actually accomplishes (not just the label)",
    "context_awareness": "How the skill applies in different domains/roles",
    "relationship_mapping": "How skills relate and complement each other",
}

# Traditional vs Semantic Approach
TRADITIONAL_APPROACH = {
    "python": ["keyword search", "exact matches only"],
    "limitation": "Treats 'Python' and 'Python programming' as different entities",
}

SEMANTIC_APPROACH = {
    "python": {
        "synonyms": ["python programming", "python development"],
        "related": ["data science", "pandas", "software engineering"],
        "contexts": ["web_development", "data_science", "automation"],
    }
}

# Modular Architecture Definition
MODULAR_ARCHITECTURE = {
    "embedding_layer": {
        "purpose": "Convert text to semantic vectors",
        "responsibility": "Understand skill meaning beyond surface text",
        "inputs": ["raw_skills", "job_descriptions"],
        "outputs": ["semantic_vectors", "confidence_scores"],
    },
    "context_filter": {
        "purpose": "Apply domain-specific understanding",
        "responsibility": "Weight skills differently based on context",
        "inputs": ["semantic_vectors", "domain_context"],
        "outputs": ["context_aware_embeddings"],
    },
    "relationship_mapper": {
        "purpose": "Model skill interdependencies",
        "responsibility": "Understand skill hierarchies and complements",
        "inputs": ["context_aware_embeddings", "skill_ontology"],
        "outputs": ["enhanced_similarity_matrix"],
    },
    "validation_engine": {
        "purpose": "Ensure matches make intuitive sense",
        "responsibility": "Bridge statistical strength with human judgment",
        "inputs": ["enhanced_similarity_matrix", "feedback_data"],
        "outputs": ["validated_matches", "explanation_reports"],
    },
}
