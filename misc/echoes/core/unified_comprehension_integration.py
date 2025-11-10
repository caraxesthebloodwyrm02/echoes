"""
Unified Input Comprehension Integration
=======================================

Demonstrates integration of the Unified Comprehension System with EchoesAssistantV2
for advanced multimodal understanding capabilities.
"""

import asyncio
from typing import Dict, Any, List
import logging

from .unified_comprehension import (
    UnifiedComprehensionSystem,
    UnifiedInput,
    InputModality,
    ProcessingContext,
)
from .adaptive_fidelity import ProcessingContext as FidelityContext

logger = logging.getLogger(__name__)


class UnifiedComprehensionIntegration:
    """
    Integration layer for Unified Comprehension System with EchoesAssistantV2.

    Provides seamless multimodal input processing with adaptive fidelity,
    cross-channel signal processing, multi-sensor fusion, and semantic alignment.
    """

    def __init__(self):
        self.comprehension_system = UnifiedComprehensionSystem()
        self.integration_stats = {
            "total_processed": 0,
            "modalities_processed": {},
            "fidelity_distribution": {},
            "alignment_strength": 0.0,
        }

    async def process_multimodal_input(
        self,
        text: str = None,
        image_path: str = None,
        audio_path: str = None,
        sensor_data: Dict[str, Any] = None,
        context: ProcessingContext = ProcessingContext.CONVERSATION,
        user_preferences: Dict[str, Any] = None,
    ) -> Dict[str, Any]:
        """
        Process multimodal input through the unified comprehension pipeline.

        Args:
            text: Text input
            image_path: Path to image file
            audio_path: Path to audio file
            sensor_data: Sensor data dictionary
            context: Processing context
            user_preferences: User-specific preferences

        Returns:
            Comprehensive processing results
        """
        inputs_to_process = []
        results = {}

        # Create input objects for each modality
        if text:
            text_input = UnifiedInput(
                modality=InputModality.TEXT,
                data=text,
                context=context,
                metadata={"source": "user_input"},
            )
            inputs_to_process.append(("text", text_input))

        if image_path:
            image_input = UnifiedInput(
                modality=InputModality.IMAGE,
                data=image_path,
                context=context,
                metadata={"file_path": image_path},
            )
            inputs_to_process.append(("image", image_input))

        if audio_path:
            audio_input = UnifiedInput(
                modality=InputModality.AUDIO,
                data=audio_path,
                context=context,
                metadata={"file_path": audio_path},
            )
            inputs_to_process.append(("audio", audio_input))

        if sensor_data:
            sensor_input = UnifiedInput(
                modality=InputModality.SENSOR,
                data=sensor_data,
                context=context,
                metadata={"sensor_types": list(sensor_data.keys())},
            )
            inputs_to_process.append(("sensor", sensor_input))

        # Process all inputs
        for modality_name, input_obj in inputs_to_process:
            try:
                logger.info(f"Processing {modality_name} input...")
                result = await self.comprehension_system.process_unified_input(
                    input_obj, user_preferences
                )

                results[modality_name] = {
                    "processed_data": result.processed_data,
                    "confidence": result.confidence,
                    "fidelity_level": result.fidelity_level.value,
                    "semantic_embedding_shape": result.semantic_embedding.shape,
                    "cross_modal_alignments": len(result.cross_modal_alignments),
                    "sensor_fusions": len(result.sensor_fusions),
                    "processing_metadata": result.processing_metadata,
                }

                # Update stats
                self._update_stats(result)

                logger.info(
                    f"Successfully processed {modality_name} with {result.fidelity_level.value} fidelity"
                )

            except Exception as e:
                logger.error(f"Failed to process {modality_name}: {str(e)}")
                results[modality_name] = {"error": str(e)}

        # Create multimodal fusion if multiple modalities present
        if len(results) > 1:
            try:
                multimodal_result = await self._create_multimodal_fusion(
                    results, context, user_preferences
                )
                results["multimodal_fusion"] = multimodal_result
            except Exception as e:
                logger.warning(f"Multimodal fusion failed: {str(e)}")

        return {
            "results": results,
            "system_status": self.comprehension_system.get_system_status(),
            "integration_stats": self.integration_stats,
        }

    async def _create_multimodal_fusion(
        self,
        individual_results: Dict[str, Any],
        context: ProcessingContext,
        user_preferences: Dict[str, Any],
    ) -> Dict[str, Any]:
        """Create multimodal fusion from individual modality results."""
        # Prepare multimodal data
        multimodal_data = {}
        for modality, result in individual_results.items():
            if "error" not in result:
                multimodal_data[modality] = result["processed_data"]

        # Create multimodal input
        multimodal_input = UnifiedInput(
            modality=InputModality.MULTIMODAL,
            data=multimodal_data,
            context=context,
            metadata={"component_modalities": list(multimodal_data.keys())},
        )

        # Process multimodal input
        fusion_result = await self.comprehension_system.process_unified_input(
            multimodal_input, user_preferences
        )

        return {
            "fused_data": fusion_result.processed_data,
            "fusion_confidence": fusion_result.confidence,
            "fusion_fidelity": fusion_result.fidelity_level.value,
            "semantic_embedding_shape": fusion_result.semantic_embedding.shape,
            "total_alignments": len(fusion_result.cross_modal_alignments),
            "total_fusions": len(fusion_result.sensor_fusions),
        }

    def _update_stats(self, result):
        """Update integration statistics."""
        self.integration_stats["total_processed"] += 1

        # Update modality counts
        modality = result.modality.value
        if modality not in self.integration_stats["modalities_processed"]:
            self.integration_stats["modalities_processed"][modality] = 0
        self.integration_stats["modalities_processed"][modality] += 1

        # Update fidelity distribution
        fidelity = result.fidelity_level.value
        if fidelity not in self.integration_stats["fidelity_distribution"]:
            self.integration_stats["fidelity_distribution"][fidelity] = 0
        self.integration_stats["fidelity_distribution"][fidelity] += 1

        # Update alignment strength (rolling average)
        if result.cross_modal_alignments:
            avg_alignment = np.mean(
                [a.get("strength", 0) for a in result.cross_modal_alignments]
            )
            current_avg = self.integration_stats["alignment_strength"]
            self.integration_stats["alignment_strength"] = (
                current_avg * (self.integration_stats["total_processed"] - 1)
                + avg_alignment
            ) / self.integration_stats["total_processed"]

    def get_semantic_paths(
        self, concept1: str, concept2: str, max_hops: int = 3
    ) -> List[List[str]]:
        """
        Find semantic paths between concepts using the Archer framework.

        Args:
            concept1: First concept ID
            concept2: Second concept ID
            max_hops: Maximum path length

        Returns:
            List of semantic paths
        """
        return self.comprehension_system.archer_framework.find_semantic_paths(
            concept1, concept2, max_hops
        )

    def export_semantic_graph(self, format: str = "json") -> str:
        """
        Export the semantic alignment graph.

        Args:
            format: Export format ('json', 'graphml')

        Returns:
            Graph representation as string
        """
        return self.comprehension_system.archer_framework.export_semantic_graph(format)

    def optimize_system(self) -> bool:
        """Optimize the unified comprehension system."""
        return self.comprehension_system.optimize_system()

    async def shutdown(self):
        """Shutdown the integration system."""
        await self.comprehension_system.shutdown()


# Integration with EchoesAssistantV2
class EnhancedEchoesAssistant:
    """
    Enhanced version of EchoesAssistantV2 with unified comprehension capabilities.
    """

    def __init__(self, *args, **kwargs):
        # Initialize base assistant
        from ..assistant_v2_core import EchoesAssistantV2

        self.base_assistant = EchoesAssistantV2(*args, **kwargs)

        # Add unified comprehension
        self.unified_comprehension = UnifiedComprehensionIntegration()

        # Enhanced capabilities
        self.multimodal_enabled = True

    async def enhanced_chat(
        self,
        message: str,
        image_path: str = None,
        audio_path: str = None,
        sensor_data: Dict[str, Any] = None,
        **kwargs,
    ) -> Dict[str, Any]:
        """
        Enhanced chat with multimodal comprehension.

        Args:
            message: Text message
            image_path: Optional image file path
            audio_path: Optional audio file path
            sensor_data: Optional sensor data
            **kwargs: Additional arguments for base chat

        Returns:
            Enhanced response with multimodal processing results
        """
        # Process multimodal input first
        comprehension_results = (
            await self.unified_comprehension.process_multimodal_input(
                text=message,
                image_path=image_path,
                audio_path=audio_path,
                sensor_data=sensor_data,
                context=ProcessingContext.CONVERSATION,
                user_preferences=kwargs.get("user_preferences"),
            )
        )

        # Generate base response
        base_response = await self.base_assistant.chat(message, **kwargs)

        # Enhance response with comprehension insights
        enhanced_response = {
            "base_response": base_response,
            "comprehension_results": comprehension_results,
            "multimodal_insights": self._extract_multimodal_insights(
                comprehension_results
            ),
            "semantic_paths": [],  # Could be populated based on conversation context
            "system_status": self.unified_comprehension.comprehension_system.get_system_status(),
        }

        return enhanced_response

    def _extract_multimodal_insights(
        self, comprehension_results: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Extract key insights from multimodal processing."""
        insights = {
            "modalities_processed": len(comprehension_results.get("results", {})),
            "fidelity_levels": {},
            "confidence_scores": {},
            "semantic_alignments": 0,
            "sensor_fusions": 0,
        }

        results = comprehension_results.get("results", {})
        for modality, result in results.items():
            if isinstance(result, dict) and "error" not in result:
                insights["fidelity_levels"][modality] = result.get(
                    "fidelity_level", "unknown"
                )
                insights["confidence_scores"][modality] = result.get("confidence", 0.0)
                insights["semantic_alignments"] += result.get(
                    "cross_modal_alignments", 0
                )
                insights["sensor_fusions"] += result.get("sensor_fusions", 0)

        # Add multimodal fusion insights
        if "multimodal_fusion" in results:
            fusion = results["multimodal_fusion"]
            insights["fusion_confidence"] = fusion.get("fusion_confidence", 0.0)
            insights["fusion_fidelity"] = fusion.get("fusion_fidelity", "unknown")

        return insights

    async def analyze_semantic_relationships(
        self, concepts: List[str]
    ) -> Dict[str, Any]:
        """
        Analyze semantic relationships between concepts using the Archer framework.

        Args:
            concepts: List of concept identifiers to analyze

        Returns:
            Analysis of semantic relationships
        """
        relationships = {}

        # Find paths between concept pairs
        for i, concept1 in enumerate(concepts):
            for concept2 in concepts[i + 1 :]:
                paths = self.unified_comprehension.get_semantic_paths(
                    concept1, concept2
                )
                if paths:
                    relationships[f"{concept1}_{concept2}"] = {
                        "paths_found": len(paths),
                        "shortest_path": paths[0] if paths else None,
                        "path_strength": len(paths[0]) if paths else 0,
                    }

        return {
            "concepts_analyzed": concepts,
            "relationships_found": len(relationships),
            "relationship_details": relationships,
            "semantic_graph_stats": self.unified_comprehension.comprehension_system.archer_framework.get_alignment_statistics(),
        }


# Example usage and testing functions
async def demo_unified_comprehension():
    """Demonstrate the unified comprehension system."""
    print("🚀 Unified Input Comprehension System Demo")
    print("=" * 50)

    # Initialize system
    integration = UnifiedComprehensionIntegration()

    # Example 1: Text processing
    print("\n📝 Processing text input...")
    text_input = UnifiedInput(
        modality=InputModality.TEXT,
        data="The weather today is sunny with a temperature of 75°F and humidity at 45%.",
        context=ProcessingContext.CONVERSATION,
    )

    text_result = await integration.comprehension_system.process_unified_input(
        text_input
    )
    print(f"Text processed with {text_result.fidelity_level.value} fidelity")
    print(f"Confidence: {text_result.confidence:.2f}")

    # Example 2: Sensor data processing
    print("\n📊 Processing sensor data...")
    sensor_data = {
        "sensor_id": "weather_station_001",
        "type": "environmental",
        "data": {"temperature": 75.0, "humidity": 45.0, "pressure": 1013.25},
        "metadata": {"location": "outdoor", "calibrated": True},
    }

    sensor_input = UnifiedInput(
        modality=InputModality.SENSOR,
        data=sensor_data,
        context=ProcessingContext.ANALYSIS,
    )

    sensor_result = await integration.comprehension_system.process_unified_input(
        sensor_input
    )
    print(f"Sensor data processed with {sensor_result.fidelity_level.value} fidelity")
    print(f"Semantic alignments: {len(sensor_result.cross_modal_alignments)}")

    # Example 3: Multimodal fusion
    print("\n🔗 Processing multimodal fusion...")
    multimodal_data = {
        "text": "The outdoor conditions are perfect for a walk.",
        "sensor": sensor_data,
    }

    multimodal_input = UnifiedInput(
        modality=InputModality.MULTIMODAL,
        data=multimodal_data,
        context=ProcessingContext.ANALYSIS,
    )

    multimodal_result = await integration.comprehension_system.process_unified_input(
        multimodal_input
    )
    print(
        f"Multimodal fusion completed with {multimodal_result.fidelity_level.value} fidelity"
    )
    print(f"Fusion confidence: {multimodal_result.confidence:.2f}")

    # Show system status
    print("\n📊 System Status:")
    status = integration.comprehension_system.get_system_status()
    print(f"- Processed inputs: {status['processing_history']}")
    print(f"- Active channels: {status['cross_channel_parser']['active_channels']}")
    print(
        f"- Registered sensors: {len(status['sensor_fusion_engine']['active_sensors'])}"
    )
    print(f"- Semantic nodes: {status['archer_framework']['total_nodes']}")
    print(f"- Semantic edges: {status['archer_framework']['total_edges']}")

    print("\n✅ Unified comprehension demo completed!")


if __name__ == "__main__":
    # Run demo
    asyncio.run(demo_unified_comprehension())
