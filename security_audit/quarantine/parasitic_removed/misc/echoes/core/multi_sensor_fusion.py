"""
Multi-Sensor Feature Fusion for Unified Input Comprehension
===========================================================

Implements comprehensive sensor data integration and feature fusion
across multiple modalities including inertial sensors, environmental sensors,
biometric sensors, and contextual sensors for rich multimodal understanding.
"""

import logging
from dataclasses import dataclass, field
from enum import Enum
from typing import Any

import numpy as np

logger = logging.getLogger(__name__)


class SensorType(Enum):
    """Types of sensors supported in the fusion system."""

    INERTIAL = "inertial"  # Accelerometer, gyroscope, magnetometer
    ENVIRONMENTAL = "environmental"  # Temperature, humidity, pressure, light
    BIOMETRIC = "biometric"  # Heart rate, skin conductance, respiration
    AUDIO = "audio"  # Microphone arrays, directional audio
    VISUAL = "visual"  # Cameras, depth sensors, thermal
    CONTEXTUAL = "contextual"  # Location, time, activity context
    TEXT = "text"  # Text input, OCR, speech-to-text


@dataclass
class SensorData:
    """Container for sensor measurement data."""

    sensor_id: str
    sensor_type: SensorType
    timestamp: float
    data: np.ndarray | dict[str, Any] | str
    metadata: dict[str, Any] = field(default_factory=dict)
    confidence: float = 1.0
    calibration_status: str = "uncalibrated"


@dataclass
class FusionFeature:
    """Represents a fused feature from multiple sensor inputs."""

    feature_name: str
    feature_type: str
    value: float | np.ndarray | str
    confidence: float
    contributing_sensors: list[str]
    fusion_method: str
    timestamp: float


class SensorFusionEngine:
    """
    Glimpse for fusing features from multiple sensors across different modalities.
    Implements various fusion strategies including early fusion, late fusion,
    and hybrid approaches.
    """

    def __init__(self):
        self.active_sensors: dict[str, SensorData] = {}
        self.fusion_history: list[FusionFeature] = []
        self.fusion_strategies = {
            "early_fusion": self._early_fusion,
            "late_fusion": self._late_fusion,
            "hybrid_fusion": self._hybrid_fusion,
            "attention_fusion": self._attention_based_fusion,
            "graph_fusion": self._graph_based_fusion,
        }

        # Sensor compatibility matrix
        self.compatibility_matrix = self._build_compatibility_matrix()

    def register_sensor(self, sensor_data: SensorData) -> bool:
        """
        Register a sensor with the fusion Glimpse.

        Args:
            sensor_data: SensorData object containing sensor information

        Returns:
            bool: True if registration successful
        """
        try:
            self.active_sensors[sensor_data.sensor_id] = sensor_data
            logger.info(
                f"Registered sensor {sensor_data.sensor_id} of type {sensor_data.sensor_type.value}"
            )
            return True
        except Exception as e:
            logger.error(f"Failed to register sensor {sensor_data.sensor_id}: {str(e)}")
            return False

    def update_sensor_data(self, sensor_id: str, new_data: SensorData) -> bool:
        """
        Update data for an existing sensor.

        Args:
            sensor_id: ID of the sensor to update
            new_data: New SensorData object

        Returns:
            bool: True if update successful
        """
        if sensor_id not in self.active_sensors:
            logger.warning(f"Sensor {sensor_id} not registered")
            return False

        self.active_sensors[sensor_id] = new_data
        return True

    def fuse_sensor_features(
        self,
        sensor_ids: list[str],
        fusion_strategy: str = "hybrid_fusion",
        target_feature: str = "multimodal_context",
    ) -> FusionFeature | None:
        """
        Fuse features from multiple sensors using specified strategy.

        Args:
            sensor_ids: List of sensor IDs to fuse
            fusion_strategy: Fusion strategy to use
            target_feature: Name of the target fused feature

        Returns:
            FusionFeature object or None if fusion fails
        """
        # Validate sensor availability
        available_sensors = [sid for sid in sensor_ids if sid in self.active_sensors]
        if len(available_sensors) < 2:
            logger.warning("Need at least 2 sensors for fusion")
            return None

        # Get sensor data
        sensor_data = [self.active_sensors[sid] for sid in available_sensors]

        # Apply fusion strategy
        if fusion_strategy not in self.fusion_strategies:
            logger.error(f"Unknown fusion strategy: {fusion_strategy}")
            return None

        try:
            fusion_method = self.fusion_strategies[fusion_strategy]
            fused_value, confidence = fusion_method(sensor_data, target_feature)

            # Create fusion feature
            feature = FusionFeature(
                feature_name=target_feature,
                feature_type=self._infer_feature_type(sensor_data),
                value=fused_value,
                confidence=confidence,
                contributing_sensors=available_sensors,
                fusion_method=fusion_strategy,
                timestamp=np.datetime64("now").astype(float),
            )

            # Record in history
            self.fusion_history.append(feature)

            logger.info(
                f"Successfully fused features from {len(available_sensors)} sensors using {fusion_strategy}"
            )
            return feature

        except Exception as e:
            logger.error(f"Fusion failed: {str(e)}")
            return None

    def _early_fusion(
        self, sensor_data: list[SensorData], target_feature: str
    ) -> tuple[Any, float]:
        """
        Early fusion: Combine raw sensor data before feature extraction.
        Best for highly correlated sensors.
        """
        # Convert all data to numerical arrays
        numerical_data = []
        total_confidence = 0

        for sensor in sensor_data:
            if isinstance(sensor.data, np.ndarray):
                numerical_data.append(sensor.data)
            elif isinstance(sensor.data, dict):
                # Flatten dict to numerical array
                flattened = self._flatten_dict_to_array(sensor.data)
                numerical_data.append(flattened)
            elif isinstance(sensor.data, (int, float)):
                numerical_data.append(np.array([sensor.data]))
            else:
                # Skip non-numerical data for early fusion
                continue

            total_confidence += sensor.confidence

        if not numerical_data:
            raise ValueError("No numerical data available for early fusion")

        # Concatenate and normalize
        combined_data = np.concatenate(numerical_data)
        combined_data = (combined_data - np.mean(combined_data)) / (
            np.std(combined_data) + 1e-8
        )

        confidence = total_confidence / len(sensor_data)
        return combined_data, confidence

    def _late_fusion(
        self, sensor_data: list[SensorData], target_feature: str
    ) -> tuple[Any, float]:
        """
        Late fusion: Extract features from each sensor, then combine.
        Best for independent sensor modalities.
        """
        individual_features = []
        weights = []

        for sensor in sensor_data:
            feature = self._extract_sensor_features(sensor)
            individual_features.append(feature)

            # Weight by confidence and sensor type compatibility
            weight = sensor.confidence * self._get_sensor_weight(sensor)
            weights.append(weight)

        # Weighted combination
        weights = np.array(weights)
        weights = weights / np.sum(weights)  # Normalize

        if all(isinstance(f, (int, float)) for f in individual_features):
            # Numerical features - weighted average
            combined = np.average(individual_features, weights=weights)
        elif all(isinstance(f, np.ndarray) for f in individual_features):
            # Array features - weighted sum
            combined = sum(w * f for w, f in zip(weights, individual_features))
        else:
            # Mixed features - create feature vector
            combined = {
                "individual_features": individual_features,
                "weights": weights.tolist(),
                "combined_score": np.average(
                    [self._quantify_feature(f) for f in individual_features],
                    weights=weights,
                ),
            }

        confidence = np.average([s.confidence for s in sensor_data], weights=weights)
        return combined, confidence

    def _hybrid_fusion(
        self, sensor_data: list[SensorData], target_feature: str
    ) -> tuple[Any, float]:
        """
        Hybrid fusion: Combine early and late fusion approaches.
        Best for complex multimodal scenarios.
        """
        # Early fusion on raw data
        try:
            early_result, early_confidence = self._early_fusion(
                sensor_data, target_feature
            )
        except:
            early_result, early_confidence = None, 0.0

        # Late fusion on processed features
        late_result, late_confidence = self._late_fusion(sensor_data, target_feature)

        # Combine results based on confidence
        total_confidence = early_confidence + late_confidence

        if total_confidence == 0:
            return late_result, late_confidence

        # Weighted combination favoring higher confidence method
        early_weight = early_confidence / total_confidence
        late_weight = late_confidence / total_confidence

        if isinstance(early_result, np.ndarray) and isinstance(late_result, np.ndarray):
            combined = early_weight * early_result + late_weight * late_result
        elif isinstance(early_result, dict) and isinstance(late_result, dict):
            combined = {
                "early_fusion": early_result,
                "late_fusion": late_result,
                "combined_score": early_weight * self._quantify_feature(early_result)
                + late_weight * self._quantify_feature(late_result),
            }
        else:
            # Default to late fusion result
            combined = late_result

        confidence = max(early_confidence, late_confidence)
        return combined, confidence

    def _attention_based_fusion(
        self, sensor_data: list[SensorData], target_feature: str
    ) -> tuple[Any, float]:
        """
        Attention-based fusion: Use attention mechanism to weigh sensor contributions.
        Best for scenarios with varying sensor reliability.
        """
        # Extract features from all sensors
        features = [self._extract_sensor_features(sensor) for sensor in sensor_data]

        # Compute attention weights based on sensor characteristics
        attention_weights = self._compute_attention_weights(sensor_data, features)

        # Apply attention-weighted combination
        if all(isinstance(f, np.ndarray) for f in features):
            combined = sum(w * f for w, f in zip(attention_weights, features))
        else:
            # For mixed feature types, use weighted scoring
            scores = [self._quantify_feature(f) for f in features]
            combined_score = np.dot(attention_weights, scores)
            combined = {
                "attention_weights": attention_weights.tolist(),
                "individual_scores": scores,
                "combined_score": combined_score,
                "features": features,
            }

        confidence = np.mean([s.confidence for s in sensor_data])
        return combined, confidence

    def _graph_based_fusion(
        self, sensor_data: list[SensorData], target_feature: str
    ) -> tuple[Any, float]:
        """
        Graph-based fusion: Model sensor relationships as a graph.
        Best for understanding sensor interdependencies.
        """
        # Create sensor relationship graph
        sensor_graph = self._build_sensor_graph(sensor_data)

        # Compute graph-based fusion weights
        graph_weights = self._compute_graph_weights(sensor_graph)

        # Extract features and apply graph weights
        features = [self._extract_sensor_features(sensor) for sensor in sensor_data]

        if all(isinstance(f, np.ndarray) for f in features):
            combined = sum(w * f for w, f in zip(graph_weights, features))
        else:
            scores = [self._quantify_feature(f) for f in features]
            combined_score = np.dot(graph_weights, scores)
            combined = {
                "graph_weights": graph_weights.tolist(),
                "individual_scores": scores,
                "combined_score": combined_score,
                "sensor_relationships": sensor_graph,
            }

        confidence = np.mean([s.confidence for s in sensor_data])
        return combined, confidence

    def _extract_sensor_features(self, sensor: SensorData) -> Any:
        """Extract meaningful features from sensor data."""
        if sensor.sensor_type == SensorType.INERTIAL:
            return self._extract_inertial_features(sensor.data)
        elif sensor.sensor_type == SensorType.ENVIRONMENTAL:
            return self._extract_environmental_features(sensor.data)
        elif sensor.sensor_type == SensorType.BIOMETRIC:
            return self._extract_biometric_features(sensor.data)
        elif sensor.sensor_type == SensorType.AUDIO:
            return self._extract_audio_features(sensor.data)
        elif sensor.sensor_type == SensorType.VISUAL:
            return self._extract_visual_features(sensor.data)
        elif sensor.sensor_type == SensorType.CONTEXTUAL:
            return self._extract_contextual_features(sensor.data)
        elif sensor.sensor_type == SensorType.TEXT:
            return self._extract_text_features(sensor.data)
        else:
            return sensor.data

    def _extract_inertial_features(self, data: np.ndarray) -> np.ndarray:
        """Extract features from inertial sensor data (accel, gyro, mag)."""
        if len(data.shape) == 1:
            # Single axis
            return np.array([np.mean(data), np.std(data), np.max(data)])
        else:
            # Multi-axis
            features = []
            for axis in range(data.shape[1]):
                axis_data = data[:, axis]
                features.extend(
                    [np.mean(axis_data), np.std(axis_data), np.max(axis_data)]
                )
            return np.array(features)

    def _extract_environmental_features(self, data: dict[str, Any]) -> np.ndarray:
        """Extract features from environmental sensor data."""
        features = []
        for key, value in data.items():
            if isinstance(value, (int, float)):
                features.append(float(value))
        return np.array(features) if features else np.array([0.0])

    def _extract_biometric_features(self, data: dict[str, Any]) -> np.ndarray:
        """Extract features from biometric sensor data."""
        # Focus on physiological signals
        features = []
        if "heart_rate" in data:
            features.append(data["heart_rate"])
        if "skin_conductance" in data:
            features.append(data["skin_conductance"])
        if "respiration_rate" in data:
            features.append(data["respiration_rate"])
        return np.array(features) if features else np.array([0.0])

    def _extract_audio_features(self, data: np.ndarray) -> np.ndarray:
        """Extract features from audio data."""
        # Simple spectral features
        if len(data) == 0:
            return np.array([0.0])

        # RMS energy, zero crossings, spectral centroid approximation
        rms = np.sqrt(np.mean(data**2))
        zero_crossings = np.sum(np.abs(np.diff(np.sign(data)))) / len(data)
        spectral_centroid = np.sum(np.arange(len(data)) * np.abs(data)) / np.sum(
            np.abs(data)
        )

        return np.array([rms, zero_crossings, spectral_centroid])

    def _extract_visual_features(self, data: np.ndarray) -> np.ndarray:
        """Extract features from visual data."""
        # Basic image features
        if len(data.shape) == 3:  # HWC format
            # Color histogram features
            features = []
            for channel in range(data.shape[2]):
                hist, _ = np.histogram(data[:, :, channel], bins=8, range=(0, 256))
                features.extend(hist / np.sum(hist))  # Normalize
            return np.array(features)
        else:
            return np.array([np.mean(data), np.std(data)])

    def _extract_contextual_features(self, data: dict[str, Any]) -> np.ndarray:
        """Extract features from contextual data."""
        features = []
        if "location" in data:
            # Simple location encoding
            features.extend(
                [data["location"].get("lat", 0), data["location"].get("lon", 0)]
            )
        if "time_of_day" in data:
            # Time encoding (0-23 hours)
            features.append(data["time_of_day"] / 24.0)
        if "activity" in data:
            # Simple activity encoding
            activity_map = {"stationary": 0, "walking": 1, "running": 2}
            features.append(activity_map.get(data["activity"], 0))
        return np.array(features) if features else np.array([0.0])

    def _extract_text_features(self, data: str) -> np.ndarray:
        """Extract features from text data."""
        if not data:
            return np.array([0.0])

        # Simple text features
        word_count = len(data.split())
        char_count = len(data)
        avg_word_length = char_count / word_count if word_count > 0 else 0

        return np.array([word_count, char_count, avg_word_length])

    def _compute_attention_weights(
        self, sensors: list[SensorData], features: list[Any]
    ) -> np.ndarray:
        """Compute attention weights for sensors based on their characteristics."""
        weights = []

        for sensor, feature in zip(sensors, features):
            weight = sensor.confidence

            # Boost weight for higher-quality data
            if sensor.calibration_status == "calibrated":
                weight *= 1.2

            # Modality-specific adjustments
            if sensor.sensor_type == SensorType.BIOMETRIC:
                weight *= 1.3  # Biometric data often most informative
            elif sensor.sensor_type == SensorType.VISUAL:
                weight *= 1.1  # Visual data rich but can be noisy

            # Feature quality adjustment
            if hasattr(feature, "__len__") and len(feature) > 10:
                weight *= 1.1  # Richer features get higher weight

            weights.append(weight)

        # Normalize
        weights = np.array(weights)
        return weights / np.sum(weights)

    def _build_sensor_graph(self, sensors: list[SensorData]) -> dict[str, Any]:
        """Build a graph representing sensor relationships."""
        graph = {"nodes": [], "edges": []}

        for sensor in sensors:
            graph["nodes"].append(
                {
                    "id": sensor.sensor_id,
                    "type": sensor.sensor_type.value,
                    "confidence": sensor.confidence,
                }
            )

        # Add edges based on sensor compatibility
        for i, sensor1 in enumerate(sensors):
            for j, sensor2 in enumerate(sensors):
                if i != j:
                    compatibility = self.compatibility_matrix.get(
                        (sensor1.sensor_type, sensor2.sensor_type), 0.5
                    )
                    if compatibility > 0.3:  # Only add meaningful connections
                        graph["edges"].append(
                            {
                                "source": sensor1.sensor_id,
                                "target": sensor2.sensor_id,
                                "weight": compatibility,
                            }
                        )

        return graph

    def _compute_graph_weights(self, sensor_graph: dict[str, Any]) -> np.ndarray:
        """Compute fusion weights based on graph structure."""
        # Simple centrality-based weighting
        node_weights = {}

        for node in sensor_graph["nodes"]:
            # Count connections
            connection_count = sum(
                1
                for edge in sensor_graph["edges"]
                if edge["source"] == node["id"] or edge["target"] == node["id"]
            )
            # Weight by connections and confidence
            node_weights[node["id"]] = connection_count * node["confidence"]

        # Normalize
        total_weight = sum(node_weights.values())
        if total_weight == 0:
            return np.ones(len(sensor_graph["nodes"])) / len(sensor_graph["nodes"])

        return np.array(
            [node_weights[node["id"]] / total_weight for node in sensor_graph["nodes"]]
        )

    def _build_compatibility_matrix(self) -> dict[tuple[SensorType, SensorType], float]:
        """Build matrix of sensor type compatibilities for fusion."""
        # Define how well different sensor types work together
        compatibilities = {
            (SensorType.INERTIAL, SensorType.ENVIRONMENTAL): 0.7,
            (SensorType.INERTIAL, SensorType.BIOMETRIC): 0.8,
            (SensorType.INERTIAL, SensorType.CONTEXTUAL): 0.9,
            (SensorType.ENVIRONMENTAL, SensorType.BIOMETRIC): 0.6,
            (SensorType.ENVIRONMENTAL, SensorType.CONTEXTUAL): 0.8,
            (SensorType.BIOMETRIC, SensorType.CONTEXTUAL): 0.7,
            (SensorType.AUDIO, SensorType.VISUAL): 0.9,
            (SensorType.AUDIO, SensorType.TEXT): 0.8,
            (SensorType.VISUAL, SensorType.TEXT): 0.9,
            (SensorType.TEXT, SensorType.CONTEXTUAL): 0.6,
        }

        # Make symmetric
        symmetric_compat = {}
        for (t1, t2), compat in compatibilities.items():
            symmetric_compat[(t1, t2)] = compat
            symmetric_compat[(t2, t1)] = compat

        # Default compatibility for same types
        for sensor_type in SensorType:
            symmetric_compat[(sensor_type, sensor_type)] = 1.0

        return symmetric_compat

    def _get_sensor_weight(self, sensor: SensorData) -> float:
        """Get base weight for a sensor type."""
        weights = {
            SensorType.BIOMETRIC: 1.2,  # Often most informative
            SensorType.VISUAL: 1.1,  # Rich data
            SensorType.AUDIO: 1.0,  # Good contextual info
            SensorType.INERTIAL: 0.9,  # Motion context
            SensorType.ENVIRONMENTAL: 0.8,  # Background context
            SensorType.CONTEXTUAL: 0.7,  # Meta information
            SensorType.TEXT: 1.0,  # Direct semantic content
        }
        return weights.get(sensor.sensor_type, 1.0)

    def _flatten_dict_to_array(self, data: dict[str, Any]) -> np.ndarray:
        """Flatten dictionary to numerical array."""
        values = []
        for key, value in data.items():
            if isinstance(value, (int, float)):
                values.append(float(value))
            elif isinstance(value, list) and all(
                isinstance(v, (int, float)) for v in value
            ):
                values.extend([float(v) for v in value])
        return np.array(values) if values else np.array([0.0])

    def _quantify_feature(self, feature: Any) -> float:
        """Convert feature to numerical score for weighting."""
        if isinstance(feature, (int, float)):
            return float(feature)
        elif isinstance(feature, np.ndarray):
            return float(np.mean(np.abs(feature)))
        elif isinstance(feature, dict):
            if "combined_score" in feature:
                return feature["combined_score"]
            return float(len(feature))  # Fallback to size
        else:
            return 1.0  # Default score

    def _infer_feature_type(self, sensors: list[SensorData]) -> str:
        """Infer the type of fused feature."""
        types = [s.sensor_type.value for s in sensors]
        if len(set(types)) == 1:
            return f"{types[0]}_fused"
        else:
            return "multimodal_fused"

    def get_fusion_history(self, limit: int = 10) -> list[FusionFeature]:
        """Get recent fusion history."""
        return self.fusion_history[-limit:] if self.fusion_history else []

    def get_sensor_status(self) -> dict[str, dict[str, Any]]:
        """Get status of all registered sensors."""
        return {
            sensor_id: {
                "type": sensor.sensor_type.value,
                "confidence": sensor.confidence,
                "calibration": sensor.calibration_status,
                "last_update": sensor.timestamp,
            }
            for sensor_id, sensor in self.active_sensors.items()
        }
