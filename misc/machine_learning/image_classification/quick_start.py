#!/usr/bin/env python3
"""
Quick Start Script for Image Classification
==========================================

This script provides a quick way to train and test an image classification model.

Usage:
    python quick_start.py

This will:
1. Train a simple model on CIFAR-10 for 2 epochs
2. Evaluate the model
3. Show a demo with 3 sample predictions

Author: Echoes AI Assistant
"""

import sys
import subprocess
from pathlib import Path


def run_command(cmd, description):
    """Run a command and check for success."""
    print(f"\nRunning {description}...")
    try:
        result = subprocess.run(
            cmd, shell=True, check=True, capture_output=True, text=True
        )
        print(f"✓ {description} completed successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"✗ {description} failed:")
        print(e.stderr)
        return False


def main():
    print("Starting Image Classification Training")
    print("=" * 60)

    # Check if we're in the right directory
    if not Path("machine_learning/image_classification").exists():
        print("Please run this script from the Echoes project root directory")
        sys.exit(1)

    # Dependencies are already installed, skip installation step
    print("Dependencies already installed, proceeding with training...")

    # Step 2: Train a quick model (2 epochs)
    train_cmd = (
        "python -m machine_learning.image_classification.train "
        "--dataset cifar10 "
        "--model custom_cnn "
        "--epochs 2 "
        "--batch_size 64 "
        "--learning_rate 0.01 "
        "--experiment_name quick_start "
        "--data_dir ./data"
    )

    if not run_command(train_cmd, "Training quick model (2 epochs)"):
        sys.exit(1)

    # Step 3: Evaluate the model
    eval_cmd = (
        "python -m machine_learning.image_classification.evaluate "
        "--model_path models/quick_start/best_model.pth "
        "--dataset cifar10 "
        "--data_dir ./data"
    )

    if not run_command(eval_cmd, "Evaluating trained model"):
        sys.exit(1)

    # Step 4: Run demo
    demo_cmd = (
        "python -m machine_learning.image_classification.demo "
        "--model_path models/quick_start/best_model.pth "
        "--dataset cifar10 "
        "--num_samples 3 "
        "--data_dir ./data "
        "--save_plot demo_results.png"
    )

    if not run_command(demo_cmd, "Running demo with 3 samples"):
        sys.exit(1)

    print("\n" + "=" * 60)
    print("Training completed successfully!")
    print()
    print("Check the following files:")
    print("  - models/quick_start/best_model.pth (trained model)")
    print("  - models/quick_start/training_history.json (training metrics)")
    print("  - models/quick_start/training_history.png (training plot)")
    print("  - models/quick_start/test_results.json (evaluation results)")
    print("  - demo_results.png (demo predictions)")
    print()
    print("Next steps:")
    print("  - Train for more epochs: --epochs 20")
    print("  - Try different models: --model resnet18")
    print("  - Use different datasets: --dataset fashionmnist")
    print(
        "  - Run full evaluation: python -m machine_learning.image_classification.evaluate --generate_plots"
    )


if __name__ == "__main__":
    main()
