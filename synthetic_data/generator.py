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
Synthetic Data Generation System
Privacy-preserving data augmentation using SDV and Faker
"""

import json
import os
from datetime import datetime
from typing import Any, Dict, List

import numpy as np
import pandas as pd
from faker import Faker
from sdv.metadata import SingleTableMetadata
from sdv.single_table import CopulaGANSynthesizer, CTGANSynthesizer, TVAESynthesizer


class SyntheticDataGenerator:
    """Advanced synthetic data generation with multiple techniques"""

    def __init__(self):
        self.fake = Faker()
        self.generators = {
            "ctgan": CTGANSynthesizer,
            "tvae": TVAESynthesizer,
            "copula": CopulaGANSynthesizer,
        }

    def detect_metadata(self, data: pd.DataFrame) -> SingleTableMetadata:
        """Automatically detect data metadata"""
        metadata = SingleTableMetadata()
        metadata.detect_from_dataframe(data)
        return metadata

    def generate_synthetic_data(
        self,
        real_data: pd.DataFrame,
        num_samples: int,
        method: str = "ctgan",
        privacy_level: str = "balanced",
    ) -> pd.DataFrame:
        """Generate synthetic data using specified method"""

        if method not in self.generators:
            raise ValueError(f"Unknown method: {method}")

        # Detect metadata
        metadata = self.detect_metadata(real_data)

        # Configure synthesizer based on privacy level
        synthesizer_class = self.generators[method]

        if method == "ctgan":
            synthesizer = synthesizer_class(
                metadata, epochs=100 if privacy_level == "high" else 50, verbose=True
            )
        elif method == "tvae":
            synthesizer = synthesizer_class(
                metadata,
                epochs=100 if privacy_level == "high" else 50,
                compress_dims=(128, 64) if privacy_level == "high" else (64, 32),
                decompress_dims=(64, 128) if privacy_level == "high" else (32, 64),
                verbose=True,
            )
        else:  # copula
            synthesizer = synthesizer_class(metadata)

        # Train synthesizer
        print(f"Training {method} synthesizer with privacy level: {privacy_level}...")
        synthesizer.fit(real_data)

        # Generate synthetic data
        print(f"Generating {num_samples} synthetic samples...")
        synthetic_data = synthesizer.sample(num_samples)

        # Validate synthetic data
        validation_report = self.validate_synthetic_data(real_data, synthetic_data)

        return synthetic_data, validation_report

    def augment_with_faker(
        self, data: pd.DataFrame, column_mappings: Dict[str, str]
    ) -> pd.DataFrame:
        """Augment data with Faker-generated values"""

        augmented_data = data.copy()

        faker_methods = {
            "name": self.fake.name,
            "email": self.fake.email,
            "address": self.fake.address,
            "phone": self.fake.phone_number,
            "company": self.fake.company,
            "job": self.fake.job,
            "city": self.fake.city,
            "country": self.fake.country,
            "date": lambda: self.fake.date_this_decade().isoformat(),
            "ssn": self.fake.ssn,
            "credit_card": self.fake.credit_card_number,
        }

        for column, faker_type in column_mappings.items():
            if column in augmented_data.columns and faker_type in faker_methods:
                print(f"Augmenting column '{column}' with {faker_type} data...")
                augmented_data[column] = [
                    faker_methods[faker_type]() for _ in range(len(augmented_data))
                ]

        return augmented_data

    def create_hybrid_dataset(
        self,
        real_data: pd.DataFrame,
        synthetic_ratio: float = 0.5,
        method: str = "ctgan",
    ) -> pd.DataFrame:
        """Create hybrid dataset mixing real and synthetic data"""

        num_synthetic = int(len(real_data) * synthetic_ratio)
        num_real = len(real_data) - num_synthetic

        # Generate synthetic data
        synthetic_data, _ = self.generate_synthetic_data(
            real_data, num_synthetic, method
        )

        # Sample real data
        real_sample = real_data.sample(n=num_real, random_state=42)

        # Combine datasets
        hybrid_data = pd.concat([real_sample, synthetic_data], ignore_index=True)

        # Shuffle
        hybrid_data = hybrid_data.sample(frac=1, random_state=42).reset_index(drop=True)

        return hybrid_data

    def validate_synthetic_data(
        self, real_data: pd.DataFrame, synthetic_data: pd.DataFrame
    ) -> Dict[str, Any]:
        """Validate synthetic data quality and privacy"""

        validation_report = {
            "dataset_sizes": {"real": len(real_data), "synthetic": len(synthetic_data)},
            "column_analysis": {},
            "privacy_checks": {},
            "quality_metrics": {},
        }

        # Column-wise analysis
        for column in real_data.columns:
            if column in synthetic_data.columns:
                real_col = real_data[column]
                synth_col = synthetic_data[column]

                # Basic statistics
                real_stats = {
                    "mean": real_col.mean()
                    if pd.api.types.is_numeric_dtype(real_col)
                    else None,
                    "std": real_col.std()
                    if pd.api.types.is_numeric_dtype(real_col)
                    else None,
                    "unique_count": real_col.nunique(),
                    "null_count": real_col.isnull().sum(),
                }

                synth_stats = {
                    "mean": synth_col.mean()
                    if pd.api.types.is_numeric_dtype(synth_col)
                    else None,
                    "std": synth_col.std()
                    if pd.api.types.is_numeric_dtype(synth_col)
                    else None,
                    "unique_count": synth_col.nunique(),
                    "null_count": synth_col.isnull().sum(),
                }

                validation_report["column_analysis"][column] = {
                    "real_stats": real_stats,
                    "synthetic_stats": synth_stats,
                    "distribution_similarity": self._calculate_distribution_similarity(
                        real_col, synth_col
                    ),
                }

        # Privacy checks (basic uniqueness)
        real_unique_rows = len(real_data.drop_duplicates())
        synth_unique_rows = len(synthetic_data.drop_duplicates())

        validation_report["privacy_checks"] = {
            "real_uniqueness_ratio": real_unique_rows / len(real_data),
            "synthetic_uniqueness_ratio": synth_unique_rows / len(synthetic_data),
            "duplicate_synthetic_rows": len(synthetic_data) - synth_unique_rows,
        }

        # Quality metrics
        validation_report["quality_metrics"] = {
            "column_coverage": len(set(real_data.columns) & set(synthetic_data.columns))
            / len(real_data.columns),
            "row_coverage": len(synthetic_data) / len(real_data),
        }

        return validation_report

    def _calculate_distribution_similarity(self, real_col, synth_col) -> float:
        """Calculate similarity between real and synthetic distributions"""
        try:
            if pd.api.types.is_numeric_dtype(
                real_col
            ) and pd.api.types.is_numeric_dtype(synth_col):
                # Kolmogorov-Smirnov test for numerical data
                from scipy.stats import ks_2samp

                statistic, p_value = ks_2samp(real_col.dropna(), synth_col.dropna())
                # Convert to similarity score (1 - statistic)
                return max(0, 1 - statistic)
            else:
                # Jaccard similarity for categorical data
                real_unique = set(real_col.dropna().unique())
                synth_unique = set(synth_col.dropna().unique())
                intersection = len(real_unique & synth_unique)
                union = len(real_unique | synth_unique)
                return intersection / union if union > 0 else 0
        except Exception:
            return 0.0

    def save_generation_pipeline(self, config: Dict[str, Any], filename: str):
        """Save data generation pipeline configuration"""
        os.makedirs("synthetic_data/pipelines", exist_ok=True)

        config["timestamp"] = datetime.now().isoformat()
        config["version"] = "1.0"

        with open(f"synthetic_data/pipelines/{filename}.json", "w") as f:
            json.dump(config, f, indent=2)

    def load_generation_pipeline(self, filename: str) -> Dict[str, Any]:
        """Load data generation pipeline configuration"""
        with open(f"synthetic_data/pipelines/{filename}.json", "r") as f:
            return json.load(f)


class PrivacyPreservingAugmentation:
    """Advanced privacy-preserving data augmentation"""

    def __init__(self):
        self.generator = SyntheticDataGenerator()

    def anonymize_dataset(
        self, data: pd.DataFrame, sensitive_columns: List[str], k_anonymity: int = 5
    ) -> pd.DataFrame:
        """Apply k-anonymity and synthetic augmentation"""

        # Identify quasi-identifiers (columns that could identify individuals)
        quasi_identifiers = [
            col for col in data.columns if col not in sensitive_columns
        ]

        # Apply generalization to quasi-identifiers
        anonymized_data = data.copy()

        for col in quasi_identifiers:
            if pd.api.types.is_numeric_dtype(data[col]):
                # Generalize numerical data by binning
                anonymized_data[col] = pd.cut(data[col], bins=k_anonymity, labels=False)
            else:
                # Generalize categorical data by frequency-based grouping
                value_counts = data[col].value_counts()
                rare_values = value_counts[value_counts < k_anonymity].index
                anonymized_data[col] = data[col].replace(rare_values, "OTHER")

        # Generate synthetic data for sensitive columns
        synthetic_sensitive, _ = self.generator.generate_synthetic_data(
            data[sensitive_columns], len(data), method="copula"
        )

        # Combine anonymized quasi-identifiers with synthetic sensitive data
        final_data = pd.concat(
            [anonymized_data[quasi_identifiers], synthetic_sensitive], axis=1
        )

        return final_data

    def differential_privacy_augmentation(
        self, data: pd.DataFrame, epsilon: float = 1.0
    ) -> pd.DataFrame:
        """Apply differential privacy to numerical columns"""

        augmented_data = data.copy()

        for col in data.select_dtypes(include=[np.number]).columns:
            # Add Laplace noise for differential privacy
            sensitivity = data[col].max() - data[col].min()
            noise_scale = sensitivity / epsilon

            noise = np.random.laplace(0, noise_scale, len(data))
            augmented_data[col] = data[col] + noise

            # Clip to original range
            augmented_data[col] = np.clip(
                augmented_data[col], data[col].min(), data[col].max()
            )

        return augmented_data


def demo_synthetic_data_generation():
    """Demonstrate synthetic data generation capabilities"""

    # Create sample dataset
    np.random.seed(42)

    sample_data = pd.DataFrame(
        {
            "age": np.random.normal(35, 10, 1000).astype(int),
            "income": np.random.normal(50000, 20000, 1000),
            "score": np.random.uniform(0, 100, 1000),
            "category": np.random.choice(["A", "B", "C", "D"], 1000),
            "is_active": np.random.choice([True, False], 1000),
        }
    )

    generator = SyntheticDataGenerator()

    # Generate synthetic data
    synthetic_data, validation = generator.generate_synthetic_data(
        sample_data, 500, method="ctgan", privacy_level="balanced"
    )

    print("Synthetic data generation completed!")
    print(f"Original data shape: {sample_data.shape}")
    print(f"Synthetic data shape: {synthetic_data.shape}")
    print(f"Validation metrics: {validation['quality_metrics']}")

    # Create hybrid dataset
    hybrid_data = generator.create_hybrid_dataset(sample_data, synthetic_ratio=0.3)

    print(f"Hybrid data shape: {hybrid_data.shape}")

    # Privacy-preserving augmentation
    privacy_engine = PrivacyPreservingAugmentation()
    anonymized_data = privacy_engine.anonymize_dataset(
        sample_data, sensitive_columns=["income"], k_anonymity=3
    )

    print(f"Anonymized data shape: {anonymized_data.shape}")

    return {
        "synthetic_generation": "completed",
        "hybrid_creation": "completed",
        "privacy_preservation": "completed",
    }


if __name__ == "__main__":
    demo_synthetic_data_generation()
