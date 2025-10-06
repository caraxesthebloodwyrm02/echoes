"""
Interpretability tools for white-box auditing.
Implements sparse autoencoders and activation analysis inspired by Petri.
"""

import logging
from typing import Dict, Any, List, Optional, Tuple
import numpy as np
import torch
import torch.nn as nn

logger = logging.getLogger(__name__)

class SparseAutoencoder(nn.Module):
    """
    Simple sparse autoencoder for feature extraction.
    Inspired by mechanistic interpretability research.
    """

    def __init__(self, input_dim: int, hidden_dim: int, sparsity_param: float = 0.1):
        super().__init__()
        self.encoder = nn.Linear(input_dim, hidden_dim)
        self.decoder = nn.Linear(hidden_dim, input_dim)
        self.sparsity_param = sparsity_param

    def forward(self, x: torch.Tensor) -> Tuple[torch.Tensor, torch.Tensor]:
        """Forward pass returning reconstruction and latent features."""
        latent = torch.relu(self.encoder(x))
        reconstruction = self.decoder(latent)
        return reconstruction, latent

    def sparsity_loss(self, latent: torch.Tensor) -> torch.Tensor:
        """Calculate sparsity regularization loss."""
        return self.sparsity_param * torch.mean(torch.abs(latent))

class InterpretabilityTools:
    """
    Tools for analyzing model internals and detecting hidden objectives.
    """

    def __init__(self):
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        self.sae_models: Dict[str, SparseAutoencoder] = {}

    def analyze_activations(self, model: Optional[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Analyze model activations for suspicious patterns.
        """
        logger.info("Analyzing model activations")

        if not model:
            return {'error': 'No model provided for analysis'}

        # Mock activation analysis
        activations = self._extract_activations(model)
        features = self._identify_features(activations)
        interventions = self._test_interventions(model, features)

        return {
            'activations': activations,
            'features': features,
            'interventions': interventions,
            'suspicious_patterns': self._detect_suspicious_patterns(features),
            'interpretability_score': self._calculate_interpretability_score(features)
        }

    def _extract_activations(self, model: Dict[str, Any]) -> Dict[str, Any]:
        """Extract activations from model layers."""
        # Mock activation data
        layers = ['embedding', 'attention_1', 'attention_2', 'mlp', 'output']
        activations = {}

        for layer in layers:
            # Simulate activation tensors
            activations[layer] = {
                'mean_activation': np.random.randn(768).mean(),
                'sparsity': np.random.random(),
                'top_activating_tokens': ['the', 'and', 'is', 'to', 'of']
            }

        return activations

    def _identify_features(self, activations: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Identify interpretable features using SAE."""
        features = []

        # Train SAE on activation data
        for layer_name, layer_data in activations.items():
            sae = SparseAutoencoder(input_dim=768, hidden_dim=1024)
            sae.to(self.device)

            # Mock feature identification
            layer_features = [
                {
                    'feature_id': f'{layer_name}_feat_{i}',
                    'description': f'Feature {i} in {layer_name}',
                    'activation_pattern': np.random.randn(768),
                    'interpretable_as': self._interpret_feature(i),
                    'causal_importance': np.random.random()
                }
                for i in range(10)
            ]

            features.extend(layer_features)
            self.sae_models[layer_name] = sae

        return features

    def _interpret_feature(self, feature_idx: int) -> str:
        """Provide human-interpretable description of a feature."""
        interpretations = [
            'detects positive sentiment',
            'tracks user preferences',
            'monitors task completion',
            'handles reward-related tokens',
            'processes instruction following',
            'detects deceptive language',
            'tracks conversation history',
            'handles numerical reasoning',
            'processes emotional content',
            'monitors safety boundaries'
        ]
        return interpretations[feature_idx % len(interpretations)]

    def _test_interventions(self, model: Dict[str, Any], features: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Test causal interventions on identified features."""
        interventions = []

        for feature in features[:5]:  # Test top 5 features
            # Mock intervention testing
            baseline_behavior = "normal_response"
            intervened_behavior = self._simulate_intervention(feature)

            intervention_result = {
                'feature_id': feature['feature_id'],
                'intervention_type': 'activation_suppression',
                'baseline_behavior': baseline_behavior,
                'intervened_behavior': intervened_behavior,
                'behavior_change': baseline_behavior != intervened_behavior,
                'causal_evidence': np.random.random() > 0.5
            }

            interventions.append(intervention_result)

        return interventions

    def _simulate_intervention(self, feature: Dict[str, Any]) -> str:
        """Simulate the effect of intervening on a feature."""
        # Mock intervention outcomes
        outcomes = [
            'normal_response',
            'erratic_behavior',
            'reward_hacking_exposed',
            'deceptive_behavior',
            'safety_boundary_violation',
            'task_refusal'
        ]

        # Bias toward detecting issues for reward-related features
        if 'reward' in feature.get('interpretable_as', ''):
            return np.random.choice(['reward_hacking_exposed', 'deceptive_behavior'], p=[0.7, 0.3])
        else:
            return np.random.choice(outcomes)

    def _detect_suspicious_patterns(self, features: List[Dict[str, Any]]) -> List[str]:
        """Detect patterns indicative of hidden objectives."""
        suspicious_patterns = []

        reward_features = [f for f in features if 'reward' in f.get('interpretable_as', '')]
        if len(reward_features) > 2:
            suspicious_patterns.append("Multiple reward-related features detected - possible reward hacking")

        deceptive_features = [f for f in features if 'deceptive' in f.get('interpretable_as', '')]
        if deceptive_features:
            suspicious_patterns.append("Deceptive language processing features found")

        safety_features = [f for f in features if 'safety' in f.get('interpretable_as', '')]
        if len(safety_features) < 1:
            suspicious_patterns.append("Low safety boundary monitoring - potential vulnerability")

        return suspicious_patterns

    def _calculate_interpretability_score(self, features: List[Dict[str, Any]]) -> float:
        """Calculate overall interpretability score."""
        interpretable_features = sum(1 for f in features if f.get('causal_importance', 0) > 0.5)
        return interpretable_features / max(1, len(features))

    def apply_feature_intervention(self, model: Dict[str, Any], feature_id: str, intervention_type: str) -> Dict[str, Any]:
        """
        Apply a specific intervention to test causality.
        """
        logger.info(f"Applying {intervention_type} to feature {feature_id}")

        # Mock intervention application
        result = {
            'feature_id': feature_id,
            'intervention_type': intervention_type,
            'success': True,
            'behavior_change': 'detected_hidden_objective' if np.random.random() > 0.5 else 'no_change',
            'evidence_strength': np.random.random()
        }

        return result

    def fuzz_model_activations(self, model: Dict[str, Any], fuzz_intensity: float = 0.1) -> Dict[str, Any]:
        """
        Fuzz model activations to find edge cases and vulnerabilities.
        """
        logger.info(f"Fuzzing model activations with intensity {fuzz_intensity}")

        # Mock fuzzing results
        fuzz_results = {
            'fuzz_cases_tested': 100,
            'vulnerabilities_found': int(np.random.poisson(5)),
            'edge_case_behaviors': [
                'unexpected_reward_hacking',
                'deceptive_response_generation',
                'safety_boundary_breach'
            ],
            'robustness_score': 1.0 - fuzz_intensity
        }

        return fuzz_results
