#!/usr/bin/env python3
"""
Image Classification Training Script
===================================

This script trains an image classification model using the Echoes ML framework.

Usage:
    python train_image_classifier.py --dataset cifar10 --model custom_cnn --epochs 20

Author: Echoes AI Assistant
"""

import argparse
import json
import sys
from pathlib import Path

# Add the machine_learning directory to Python path
sys.path.insert(0, str(Path(__file__).parent.parent))

from image_classification.classifier import ImageClassifier, plot_training_history


def main():
    parser = argparse.ArgumentParser(description="Train Image Classification Model")
    parser.add_argument(
        "--dataset",
        type=str,
        default="cifar10",
        choices=["cifar10", "cifar100", "mnist", "fashionmnist"],
        help="Dataset to use",
    )
    parser.add_argument(
        "--model",
        type=str,
        default="custom_cnn",
        choices=["custom_cnn", "resnet18", "resnet50", "vgg16"],
        help="Model architecture",
    )
    parser.add_argument(
        "--epochs", type=int, default=10, help="Number of training epochs"
    )
    parser.add_argument("--batch_size", type=int, default=32, help="Batch size")
    parser.add_argument(
        "--learning_rate", type=float, default=0.001, help="Learning rate"
    )
    parser.add_argument("--data_dir", type=str, default="./data", help="Data directory")
    parser.add_argument(
        "--output_dir",
        type=str,
        default="./models",
        help="Output directory for saving models",
    )
    parser.add_argument(
        "--experiment_name",
        type=str,
        default="experiment_1",
        help="Experiment name for saving results",
    )

    args = parser.parse_args()

    # Create output directory
    output_dir = Path(args.output_dir) / args.experiment_name
    output_dir.mkdir(parents=True, exist_ok=True)

    # Save training configuration
    config = vars(args)
    with open(output_dir / "config.json", "w") as f:
        json.dump(config, f, indent=2)

    print("Starting Image Classification Training")
    print("=" * 50)
    print(f"Dataset: {args.dataset}")
    print(f"Model: {args.model}")
    print(f"Epochs: {args.epochs}")
    print(f"Batch Size: {args.batch_size}")
    print(f"Learning Rate: {args.learning_rate}")
    print(f"Output Directory: {output_dir}")
    print()

    try:
        # Initialize classifier
        print("Initializing classifier...")
        classifier = ImageClassifier(model_type=args.model)

        # Build model
        model = classifier.build_model()
        print("Model built:", args.model)

        # Setup training
        classifier.setup_training(learning_rate=args.learning_rate)
        print("Training setup complete")

        # Load dataset
        print(f"Loading {args.dataset} dataset...")
        train_loader, val_loader, test_loader = classifier.load_dataset(
            dataset_name=args.dataset,
            batch_size=args.batch_size,
            data_dir=args.data_dir,
        )
        print("Dataset loaded")

        # Train model
        print(f"Training for {args.epochs} epochs...")
        model_path = output_dir / "best_model.pth"
        history = classifier.train(
            train_loader=train_loader,
            val_loader=val_loader,
            num_epochs=args.epochs,
            save_path=str(model_path),
        )
        print("Training complete")

        # Save training history
        history_path = output_dir / "training_history.json"
        with open(history_path, "w") as f:
            json.dump(history, f, indent=2)

        # Plot training history
        plot_path = output_dir / "training_history.png"
        plot_training_history(history, save_path=str(plot_path))
        print("Training history saved")

        # Evaluate on test set
        print("Evaluating on test set...")
        test_results = classifier.evaluate(test_loader)

        # Save test results
        results_path = output_dir / "test_results.json"
        with open(results_path, "w") as f:
            json.dump(test_results, f, indent=2)

        print("Evaluation complete")
        print()
        print("Final Results:")
        print("-" * 30)
        print(f"Test Accuracy: {test_results['test_accuracy']:.2f}%")
        print(f"Test Loss: {test_results['test_loss']:.4f}")
        print(f"Total Samples: {test_results['total_samples']}")
        print(f"Correct Predictions: {test_results['correct_predictions']}")
        print()
        print("Model saved to:", model_path)
        print("Training history saved to:", history_path)
        print("Training plot saved to:", plot_path)
        print("Test results saved to:", results_path)

        print("\nTraining completed successfully!")

    except Exception as e:
        print(f"Error during training: {str(e)}")
        import traceback

        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
