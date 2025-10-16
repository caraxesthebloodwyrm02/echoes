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
