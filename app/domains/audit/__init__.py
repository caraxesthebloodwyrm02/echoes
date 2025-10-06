# HarmonyHub Audit Tool - Petri-Inspired AI Safety Auditing Framework
"""
This module implements a Petri-inspired auditing tool for AI safety research,
adapted for HarmonyHub's cross-domain ecosystem. It provides tools for auditing
language models for hidden objectives, with practical automation for monetization
and ethical compliance.
"""

__version__ = "0.1.0"
__author__ = "HarmonyHub Team"

from .audit_core import AuditEngine
from .model_trainer import ModelTrainer
from .blind_audit_game import BlindAuditGame
from .interpretability_tools import InterpretabilityTools
from .data_prep import DataPrep
from .evaluation import EvaluationMetrics

__all__ = [
    "AuditEngine",
    "ModelTrainer",
    "BlindAuditGame",
    "InterpretabilityTools",
    "DataPrep",
    "EvaluationMetrics",
]
