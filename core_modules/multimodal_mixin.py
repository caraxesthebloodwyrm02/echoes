"""Multimodal Resonance Glimpse mixin for EchoesAssistantV2.

Extracted from assistant_v2_core.py (lines 3732–4152) as part of the
god-module decomposition.  Depends on ``KnowledgeGraphMixin`` — the host
class must inherit ``KnowledgeGraphMixin`` *before* this mixin so that
``add_knowledge_node``, ``add_memory_fragment``, ``search_knowledge_graph``
and ``retrieve_relevant_memories`` are available on ``self``.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

# numpy with fallback — matches the host module's pattern
try:
    import numpy as np
except ImportError:

    def _mean(data):
        return sum(data) / len(data) if data else 0

    np = type("obj", (object,), {"mean": _mean})()  # type: ignore[assignment]


class MultimodalMixin:
    """Multimodal file processing, resonance analysis, cross-modal insights."""

    # -- Attribute stubs for type checkers (set by the host class) -----------
    enable_multimodal_resonance: bool
    multimodal_engine: Any

    # -- Public API ----------------------------------------------------------

    def process_multimodal_file(self, file_path: str, extraction_target: str = "text") -> dict[str, Any]:
        """Process a multimodal file with resonance-based understanding.

        Args:
            file_path: Path to the file to process
            extraction_target: Target modality for extraction (text, vision, audio, etc.)

        Returns:
            Processing result with resonance analysis
        """
        if not self.enable_multimodal_resonance:
            return {
                "success": False,
                "error": "Multimodal resonance Glimpse not enabled",
            }

        try:
            result = self.multimodal_engine.process_multimodal_file(file_path, extraction_target)

            # Add knowledge graph integration
            if result["success"]:
                # Extract entities from file path and add to knowledge graph
                file_name = Path(file_path).stem
                entities = self.knowledge_graph.extract_entities_and_concepts(file_name)

                # Add file as knowledge node
                node_id = f"file_{hash(file_path)}"
                self.add_knowledge_node(
                    node_id=node_id,
                    node_type="multimodal_file",
                    label=file_name,
                    description=f"Multimodal file: {Path(file_path).suffix}",
                    properties={
                        "file_path": file_path,
                        "modality": result["modality_vector"]["modality_type"],
                        "resonance_strength": result["resonance_analysis"]["resonance_strength"],
                        "extraction_target": extraction_target,
                        "quality_factor": result["modality_vector"]["quality_factor"],
                    },
                )

                # Add memory about processing
                self.add_memory_fragment(
                    content=f"Processed multimodal file {file_name} with resonance {result['resonance_analysis']['resonance_strength']:.2f}",
                    context={
                        "file_path": file_path,
                        "processing_result": result,
                        "extraction_target": extraction_target,
                    },
                    importance=result["resonance_analysis"]["resonance_strength"],
                )

                result["knowledge_graph_integration"] = {
                    "node_id": node_id,
                    "entities_extracted": entities,
                    "memory_created": True,
                }

            return result

        except Exception as e:
            return {"success": False, "error": str(e)}

    def analyze_multimodal_directory(self, directory_path: str, extraction_target: str = "text") -> dict[str, Any]:
        """Analyze all files in a directory with multimodal resonance.

        Args:
            directory_path: Path to directory to analyze
            extraction_target: Target modality for extraction

        Returns:
            Comprehensive analysis of directory multimodal content
        """
        if not self.enable_multimodal_resonance:
            return {
                "success": False,
                "error": "Multimodal resonance Glimpse not enabled",
            }

        try:
            directory = Path(directory_path)
            if not directory.exists():
                return {
                    "success": False,
                    "error": f"Directory not found: {directory_path}",
                }

            # Get all files
            files = []
            for ext in self.multimodal_engine.modality_vectors.keys():
                files.extend(directory.glob(f"*{ext}"))

            if not files:
                return {
                    "success": False,
                    "error": f"No supported multimodal files found in {directory_path}",
                }

            # Process files and optimize strategy
            file_paths = [str(f) for f in files]
            optimization_strategy = self.multimodal_engine.optimize_processing_strategy(file_paths, extraction_target)

            # Process high resonance files first
            processed_files = []
            modality_distribution = {}
            total_resonance = 0

            for file_analysis in optimization_strategy["strategy"]["file_analyses"]:
                file_path = file_analysis["file_path"]
                result = self.process_multimodal_file(file_path, extraction_target)

                if result["success"]:
                    processed_files.append(
                        {
                            "file_path": file_path,
                            "processing_result": result,
                            "analysis": file_analysis,
                        }
                    )

                    # Track modality distribution
                    modality = result["modality_vector"]["modality_type"]
                    modality_distribution[modality] = modality_distribution.get(modality, 0) + 1
                    total_resonance += result["resonance_analysis"]["resonance_strength"]

            # Create summary memory
            self.add_memory_fragment(
                content=f"Analyzed {len(processed_files)} multimodal files in {directory_path}",
                context={
                    "directory": directory_path,
                    "files_processed": len(processed_files),
                    "modality_distribution": modality_distribution,
                    "average_resonance": (total_resonance / len(processed_files) if processed_files else 0),
                    "extraction_target": extraction_target,
                },
                importance=0.8,
            )

            return {
                "success": True,
                "directory_analysis": {
                    "directory_path": directory_path,
                    "total_files_found": len(files),
                    "files_processed": len(processed_files),
                    "modality_distribution": modality_distribution,
                    "average_resonance": (total_resonance / len(processed_files) if processed_files else 0),
                    "optimization_strategy": optimization_strategy["strategy"],
                    "processed_files": processed_files,
                },
            }

        except Exception as e:
            return {"success": False, "error": str(e)}

    def get_cross_modal_insights(self, file_path: str) -> dict[str, Any]:
        """Get cross-modal transformation insights for a file.

        Args:
            file_path: Path to file to analyze

        Returns:
            Cross-modal insights and recommendations
        """
        if not self.enable_multimodal_resonance:
            return {
                "success": False,
                "error": "Multimodal resonance Glimpse not enabled",
            }

        try:
            insights = self.multimodal_engine.get_cross_modal_insights(file_path)

            if insights["success"]:
                # Enhance with knowledge graph context
                file_name = Path(file_path).stem
                related_knowledge = self.search_knowledge_graph(file_name, limit=3)

                insights["knowledge_graph_context"] = related_knowledge

                # Get resonant files for each recommended transformation
                for rec in insights["insights"]["recommended_transformations"]:
                    target_modality = rec["transformation"].split("_to_")[-1]
                    resonant_files = self.multimodal_engine.find_resonant_files(target_modality, 0.6)
                    rec["similar_files"] = resonant_files[:3]  # Top 3 similar files

            return insights

        except Exception as e:
            return {"success": False, "error": str(e)}

    def find_resonant_content(self, target_modality: str, min_resonance: float = 0.5) -> dict[str, Any]:
        """Find content that resonates with target modality.

        Args:
            target_modality: Target modality to find resonant content for
            min_resonance: Minimum resonance threshold

        Returns:
            List of resonant files and content
        """
        if not self.enable_multimodal_resonance:
            return {
                "success": False,
                "error": "Multimodal resonance Glimpse not enabled",
            }

        try:
            resonant_files = self.multimodal_engine.find_resonant_files(target_modality, min_resonance)

            # Enhance with knowledge graph information
            enhanced_results = []
            for file_info in resonant_files:
                file_name = Path(file_info["file_path"]).stem

                # Search knowledge graph for related entities
                related_knowledge = self.search_knowledge_graph(file_name, limit=2)

                # Get relevant memories
                relevant_memories = self.retrieve_relevant_memories(file_name, limit=2)

                enhanced_results.append(
                    {
                        **file_info,
                        "knowledge_context": related_knowledge,
                        "related_memories": relevant_memories,
                    }
                )

            return {
                "success": True,
                "target_modality": target_modality,
                "min_resonance": min_resonance,
                "resonant_files": enhanced_results,
                "total_found": len(enhanced_results),
            }

        except Exception as e:
            return {"success": False, "error": str(e)}

    def create_resonant_understanding(self, query: str, modality_preference: str | None = None) -> dict[str, Any]:
        """Create understanding by resonating across multiple modalities.

        Args:
            query: Query or topic to understand
            modality_preference: Preferred modality for understanding

        Returns:
            Multimodal understanding with resonance analysis
        """
        if not self.enable_multimodal_resonance:
            return {
                "success": False,
                "error": "Multimodal resonance Glimpse not enabled",
            }

        try:
            # Search knowledge graph for entities
            knowledge_results = self.search_knowledge_graph(query, limit=5)

            # Find resonant multimodal content
            target_modality = modality_preference or "text"
            resonant_content = self.find_resonant_content(target_modality, 0.6)

            # Retrieve relevant memories
            relevant_memories = self.retrieve_relevant_memories(query, limit=3)

            # Build multimodal context
            multimodal_context = {
                "query": query,
                "target_modality": target_modality,
                "knowledge_entities": knowledge_results.get("results", []),
                "resonant_files": resonant_content.get("resonant_files", []),
                "relevant_memories": relevant_memories.get("memories", []),
                "resonance_strength": (
                    np.mean([f["resonance_strength"] for f in resonant_content.get("resonant_files", [])])
                    if resonant_content.get("resonant_files")
                    else 0
                ),
            }

            # Generate enhanced response with multimodal context
            enhanced_prompt = f"""You are an AI assistant with advanced multimodal understanding capabilities.

Query: {query}
Target Modality: {target_modality}
Resonance Strength: {multimodal_context["resonance_strength"]:.2f}

Knowledge Context:
- Entities found: {len(multimodal_context["knowledge_entities"])}
- Resonant files: {len(multimodal_context["resonant_files"])}
- Relevant memories: {len(multimodal_context["relevant_memories"])}

Provide a comprehensive response that leverages this multimodal understanding. Consider the different types of content (vision, text, audio, structured data) and their relationships."""

            response = self.chat(query, system_prompt=enhanced_prompt, stream=False)

            # Create memory of this multimodal understanding
            self.add_memory_fragment(
                content=f"Created multimodal understanding for query: {query}",
                context={
                    "query": query,
                    "modality_preference": modality_preference,
                    "resonance_strength": multimodal_context["resonance_strength"],
                    "entities_used": len(multimodal_context["knowledge_entities"]),
                    "files_used": len(multimodal_context["resonant_files"]),
                },
                importance=multimodal_context["resonance_strength"],
            )

            return {
                "success": True,
                "multimodal_understanding": {
                    "query": query,
                    "response": response,
                    "context": multimodal_context,
                    "resonance_analysis": {
                        "overall_resonance": multimodal_context["resonance_strength"],
                        "modality_preference": target_modality,
                        "cross_modal_insights": len(resonant_content.get("resonant_files", [])),
                    },
                },
            }

        except Exception as e:
            return {"success": False, "error": str(e)}

    def get_multimodal_statistics(self) -> dict[str, Any]:
        """Get comprehensive statistics about multimodal resonance Glimpse.

        Returns:
            Multimodal processing statistics
        """
        if not self.enable_multimodal_resonance:
            return {
                "success": False,
                "error": "Multimodal resonance Glimpse not enabled",
            }

        try:
            stats = self.multimodal_engine.get_resonance_statistics()

            return {
                "success": True,
                "multimodal_stats": stats["statistics"],
                "message": "Multimodal resonance statistics retrieved successfully",
            }
        except Exception as e:
            return {"success": False, "error": str(e)}

    def optimize_multimodal_workflow(
        self, files: list[str], objective: str = "comprehensive_analysis"
    ) -> dict[str, Any]:
        """Optimize multimodal processing workflow for specific objectives.

        Args:
            files: List of files to process
            objective: Processing objective (comprehensive_analysis, quick_insights, deep_understanding)

        Returns:
            Optimized workflow strategy
        """
        if not self.enable_multimodal_resonance:
            return {
                "success": False,
                "error": "Multimodal resonance Glimpse not enabled",
            }

        try:
            # Determine optimal target modality based on objective
            target_modality_map = {
                "comprehensive_analysis": "text",
                "visual_insights": "vision",
                "data_extraction": "structured",
                "pattern_recognition": "geometric",
                "content_synthesis": "text",
            }

            target_modality = target_modality_map.get(objective, "text")

            # Get optimization strategy
            strategy = self.multimodal_engine.optimize_processing_strategy(files, target_modality)

            if strategy["success"]:
                workflow_strategy = strategy["strategy"]

                # Add processing recommendations based on objective
                if objective == "comprehensive_analysis":
                    workflow_strategy["recommendations"] = [
                        "Process high resonance files first for initial insights",
                        "Use cross-modal bridges to extract hidden relationships",
                        "Leverage knowledge graph for entity connections",
                    ]
                elif objective == "quick_insights":
                    workflow_strategy["recommendations"] = [
                        "Focus on files with extraction complexity < 0.6",
                        "Prioritize text and structured modalities",
                        "Use semantic enhancement for faster understanding",
                    ]
                elif objective == "deep_understanding":
                    workflow_strategy["recommendations"] = [
                        "Process all files regardless of resonance strength",
                        "Apply cross-modal mapping for comprehensive insights",
                        "Integrate with knowledge graph for contextual depth",
                    ]

                # Add estimated processing time
                total_complexity = sum(f["complexity"] for f in workflow_strategy["file_analyses"])
                workflow_strategy["estimated_complexity"] = total_complexity
                workflow_strategy["processing_tier"] = (
                    "fast" if total_complexity < 5 else "medium" if total_complexity < 15 else "complex"
                )

            return {
                "success": True,
                "objective": objective,
                "target_modality": target_modality,
                "workflow_strategy": workflow_strategy,
            }

        except Exception as e:
            return {"success": False, "error": str(e)}
