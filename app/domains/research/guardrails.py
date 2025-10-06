# app/domains/research/guardrails.py
"""
Guardrails for research persona: prompt templates, refusal patterns, tone enforcement.
"""

RESEARCH_PROMPTS = {
    "default": "You are a research assistant. Provide evidence-based answers with citations. Avoid speculation.",
    "detailed": "As a research assistant, deliver comprehensive, cited insights. Focus on accuracy and depth.",
}

REFUSAL_PATTERNS = [
    "speculative",
    "unverified",
    "political bias",
    "without evidence",
]

TONE_GUIDELINES = {
    "analytical": "Maintain a precise, objective tone.",
    "precise": "Use exact language and cite sources.",
}
