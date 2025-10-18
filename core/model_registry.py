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

"""
Model Registry - Centralized Model Management and Versioning
Provides model storage, versioning, metadata management, and deployment tracking.
"""

import json
import logging
import hashlib
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Union
import pickle

from sklearn.base import BaseEstimator


class ModelRegistry:
    """
    Centralized registry for ML models with versioning and metadata management.

    Features:
    - Model versioning and lineage tracking
    - Metadata storage (performance metrics, training info, etc.)
    - Model serialization and persistence
    - Deployment tracking and rollback capabilities
    - Model comparison and A/B testing support
    """

    def __init__(self, registry_path: Union[str, Path] = "automl/models"):
        """
        Initialize the model registry.

        Args:
            registry_path: Directory to store models and metadata
        """
        self.registry_path = Path(registry_path)
        self.registry_path.mkdir(parents=True, exist_ok=True)
        self.logger = logging.getLogger(__name__)

        # Registry metadata file
        self.metadata_file = self.registry_path / "registry.json"
        self._load_registry()

    def _load_registry(self) -> None:
        """Load existing registry metadata."""
        if self.metadata_file.exists():
            try:
                with open(self.metadata_file, 'r') as f:
                    self.registry = json.load(f)
            except Exception as e:
                self.logger.warning(f"Failed to load registry metadata: {e}")
                self.registry = {}
        else:
            self.registry = {}

    def _save_registry(self) -> None:
        """Save registry metadata to disk."""
        try:
            with open(self.metadata_file, 'w') as f:
                json.dump(self.registry, f, indent=2, default=str)
        except Exception as e:
            self.logger.error(f"Failed to save registry metadata: {e}")

    def register_model(
        self,
        model: BaseEstimator,
        name: str,
        metadata: Optional[Dict[str, Any]] = None,
        performance_metrics: Optional[Dict[str, Any]] = None,
        training_info: Optional[Dict[str, Any]] = None,
        tags: Optional[List[str]] = None
    ) -> str:
        """
        Register a new model version in the registry.

        Args:
            model: The trained model to register
            name: Model name (used for versioning)
            metadata: Additional model metadata
            performance_metrics: Model performance metrics
            training_info: Information about model training
            tags: Tags for model categorization

        Returns:
            Model version ID
        """
        # Generate version ID based on model content
        model_hash = self._generate_model_hash(model)
        version_id = f"{name}_v{int(datetime.now().timestamp())}"

        # Create model entry
        model_entry = {
            'version_id': version_id,
            'name': name,
            'model_hash': model_hash,
            'created_at': datetime.now().isoformat(),
            'metadata': metadata or {},
            'performance_metrics': performance_metrics or {},
            'training_info': training_info or {},
            'tags': tags or [],
            'status': 'active',
            'deployment_history': []
        }

        # Save model to disk
        model_path = self.registry_path / f"{version_id}.pkl"
        try:
            with open(model_path, 'wb') as f:
                pickle.dump(model, f)
            model_entry['model_path'] = str(model_path)
        except Exception as e:
            self.logger.error(f"Failed to save model {version_id}: {e}")
            raise

        # Update registry
        if name not in self.registry:
            self.registry[name] = []

        self.registry[name].append(model_entry)
        self._save_registry()

        self.logger.info(f"✅ Registered model: {version_id}")

        return version_id

    def get_model(self, name: str, version: Optional[str] = None) -> Optional[BaseEstimator]:
        """
        Retrieve a model from the registry.

        Args:
            name: Model name
            version: Specific version (latest if not specified)

        Returns:
            The loaded model or None if not found
        """
        if name not in self.registry:
            return None

        versions = self.registry[name]

        if version:
            # Find specific version
            for v in versions:
                if v['version_id'] == version:
                    return self._load_model_from_entry(v)
        else:
            # Get latest active version
            active_versions = [v for v in versions if v.get('status') == 'active']
            if active_versions:
                # Sort by creation time (latest first)
                active_versions.sort(key=lambda x: x['created_at'], reverse=True)
                return self._load_model_from_entry(active_versions[0])

        return None

    def _load_model_from_entry(self, entry: Dict[str, Any]) -> Optional[BaseEstimator]:
        """Load model from registry entry."""
        try:
            model_path = entry.get('model_path')
            if model_path and Path(model_path).exists():
                with open(model_path, 'rb') as f:
                    return pickle.load(f)
            else:
                self.logger.warning(f"Model file not found: {model_path}")
        except Exception as e:
            self.logger.error(f"Failed to load model {entry.get('version_id')}: {e}")

        return None

    def list_models(self, name: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        List models in the registry.

        Args:
            name: Specific model name (all if not specified)

        Returns:
            List of model information
        """
        if name:
            return self.registry.get(name, [])
        else:
            # Return all models
            all_models = []
            for model_name, versions in self.registry.items():
                for version in versions:
                    version['model_name'] = model_name
                    all_models.append(version)
            return all_models

    def update_model_status(
        self,
        name: str,
        version: str,
        status: str,
        reason: Optional[str] = None
    ) -> bool:
        """
        Update the status of a model version.

        Args:
            name: Model name
            version: Version ID
            status: New status ('active', 'deprecated', 'archived')
            reason: Reason for status change

        Returns:
            True if successful, False otherwise
        """
        if name not in self.registry:
            return False

        for model_entry in self.registry[name]:
            if model_entry['version_id'] == version:
                old_status = model_entry.get('status', 'unknown')
                model_entry['status'] = status
                model_entry['status_updated_at'] = datetime.now().isoformat()
                if reason:
                    model_entry['status_change_reason'] = reason

                # Log deployment history
                if status in ['active', 'deprecated']:
                    model_entry['deployment_history'].append({
                        'timestamp': datetime.now().isoformat(),
                        'action': f"status_changed_to_{status}",
                        'old_status': old_status,
                        'reason': reason
                    })

                self._save_registry()
                self.logger.info(f"✅ Updated {name} {version} status to {status}")
                return True

        return False

    def compare_models(
        self,
        model_names: List[str],
        metric: str = 'accuracy'
    ) -> Dict[str, Any]:
        """
        Compare multiple models based on performance metrics.

        Args:
            model_names: List of model names to compare
            metric: Metric to compare on

        Returns:
            Comparison results
        """
        comparison = {
            'models': [],
            'best_model': None,
            'metric': metric,
            'comparison_timestamp': datetime.now().isoformat()
        }

        best_score = float('-inf')
        best_model_info = None

        for model_name in model_names:
            versions = self.registry.get(model_name, [])
            if not versions:
                continue

            # Get latest active version
            active_versions = [v for v in versions if v.get('status') == 'active']
            if not active_versions:
                continue

            latest_version = max(active_versions, key=lambda x: x['created_at'])

            metrics = latest_version.get('performance_metrics', {})
            score = metrics.get(metric, 0)

            model_info = {
                'name': model_name,
                'version': latest_version['version_id'],
                'score': score,
                'metrics': metrics,
                'created_at': latest_version['created_at']
            }

            comparison['models'].append(model_info)

            if score > best_score:
                best_score = score
                best_model_info = model_info

        if best_model_info:
            comparison['best_model'] = best_model_info

        return comparison

    def get_model_history(self, name: str) -> List[Dict[str, Any]]:
        """
        Get the version history for a model.

        Args:
            name: Model name

        Returns:
            List of version information in chronological order
        """
        versions = self.registry.get(name, [])
        # Sort by creation time
        versions.sort(key=lambda x: x['created_at'])
        return versions

    def archive_old_versions(
        self,
        name: str,
        keep_versions: int = 5,
        archive_threshold_days: int = 30
    ) -> int:
        """
        Archive old model versions to save space.

        Args:
            name: Model name
            keep_versions: Number of recent versions to keep
            archive_threshold_days: Minimum age for archiving

        Returns:
            Number of versions archived
        """
        if name not in self.registry:
            return 0

        versions = self.registry[name]
        versions.sort(key=lambda x: x['created_at'], reverse=True)  # Newest first

        archived_count = 0

        # Keep the most recent versions
        for i, version in enumerate(versions):
            if i < keep_versions:
                continue  # Keep this version

            # Check if old enough to archive
            created_at = datetime.fromisoformat(version['created_at'])
            age_days = (datetime.now() - created_at).days

            if age_days >= archive_threshold_days and version.get('status') != 'active':
                version['status'] = 'archived'
                version['archived_at'] = datetime.now().isoformat()
                archived_count += 1

        if archived_count > 0:
            self._save_registry()
            self.logger.info(f"🗂️ Archived {archived_count} old versions of {name}")

        return archived_count

    def _generate_model_hash(self, model: BaseEstimator) -> str:
        """Generate a hash of the model's parameters and structure."""
        try:
            # Get model parameters
            params_str = str(sorted(model.get_params().items()))

            # Add model class name for uniqueness
            model_str = f"{model.__class__.__name__}:{params_str}"

            # Generate hash
            return hashlib.sha256(model_str.encode()).hexdigest()[:16]

        except Exception:
            # Fallback hash based on current time
            return hashlib.sha256(str(datetime.now()).encode()).hexdigest()[:16]

    def get_registry_stats(self) -> Dict[str, Any]:
        """Get statistics about the model registry."""
        stats = {
            'total_models': len(self.registry),
            'total_versions': sum(len(versions) for versions in self.registry.values()),
            'active_models': 0,
            'deprecated_models': 0,
            'archived_models': 0,
            'storage_used_mb': 0
        }

        for model_name, versions in self.registry.items():
            for version in versions:
                status = version.get('status', 'unknown')
                if status == 'active':
                    stats['active_models'] += 1
                elif status == 'deprecated':
                    stats['deprecated_models'] += 1
                elif status == 'archived':
                    stats['archived_models'] += 1

                # Estimate storage (rough calculation)
                model_path = version.get('model_path')
                if model_path and Path(model_path).exists():
                    stats['storage_used_mb'] += Path(model_path).stat().st_size / (1024 * 1024)

        return stats
