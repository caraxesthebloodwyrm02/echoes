"""Legacy intelligence modules for Echoes.

Mixin classes extracted from assistant_v2_core.py (Thread 3f decomposition):
- DirectoryAnalysisMixin  — directory structure analysis & reporting
- KnowledgeGraphMixin     — knowledge graph CRUD & search
- LegalAccountingMixin    — legal safeguards & cognitive accounting checks
- MultimodalMixin         — multimodal resonance processing
- QuantumStateMixin       — quantum state management wrappers
"""

from core_modules.directory_analysis_mixin import DirectoryAnalysisMixin
from core_modules.knowledge_graph_mixin import KnowledgeGraphMixin
from core_modules.legal_accounting_mixin import LegalAccountingMixin
from core_modules.multimodal_mixin import MultimodalMixin
from core_modules.quantum_state_mixin import QuantumStateMixin

__all__ = [
    "DirectoryAnalysisMixin",
    "KnowledgeGraphMixin",
    "LegalAccountingMixin",
    "MultimodalMixin",
    "QuantumStateMixin",
]
