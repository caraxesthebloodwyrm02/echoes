#!/usr/bin/env python3
"""
Image Classification Evaluation Script
=====================================

This script evaluates a trained image classification model.

Usage:
    python evaluate_image_classifier.py --model_path models/best_model.pth --dataset cifar10

Author: Echoes AI Assistant
"""

import argparse
import json
import sys
from pathlib import Path
import torch
from sklearn.metrics import classification_report, confusion_matrix
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np

# Add the machine_learning directory to Python path
sys.path.insert(0, str(Path(__file__).parent.parent))

from image_classification.classifier import ImageClassifier, get_class_names


def plot_confusion_matrix(cm, class_names, save_path=None):
    """Plot confusion matrix."""
    plt.figure(figsize=(10, 8))
    sns.heatmap(
        cm,
        annot=True,
        fmt="d",
        cmap="Blues",
        xticklabels=class_names,
        yticklabels=class_names,
    )
    plt.title("Confusion Matrix")
    plt.xlabel("Predicted")
    plt.ylabel("True")
    plt.xticks(rotation=45)
    plt.yticks(rotation=45)
    plt.tight_layout()

    if save_path:
        plt.savefig(save_path)
        print(f"Confusion matrix saved to {save_path}")
    else:
        plt.show()


def evaluate_model_detailed(
    model_path, dataset_name="cifar10", batch_size=32, data_dir="./data"
):
    """Evaluate model with detailed metrics."""
    print("🔧 Loading model...")
    classifier = ImageClassifier()
    classifier.load_model(model_path)

    print(f"📥 Loading {dataset_name} test dataset...")
    _, _, test_loader = classifier.load_dataset(
        dataset_name=dataset_name, batch_size=batch_size, data_dir=data_dir
    )

    print("🧪 Running detailed evaluation...")

    # Get predictions and true labels
    classifier.model.eval()
    all_preds = []
    all_labels = []

    with torch.no_grad():
        for inputs, labels in test_loader:
            inputs = inputs.to(classifier.device)
            outputs = classifier.model(inputs)
            _, preds = torch.max(outputs, 1)

            all_preds.extend(preds.cpu().numpy())
            all_labels.extend(labels.numpy())

    # Convert to numpy arrays
    all_preds = np.array(all_preds)
    all_labels = np.array(all_labels)

    # Calculate metrics
    class_names = get_class_names(dataset_name)

    # Classification report
    report = classification_report(
        all_labels, all_preds, target_names=class_names, output_dict=True
    )

    # Confusion matrix
    cm = confusion_matrix(all_labels, all_preds)

    return {
        "classification_report": report,
        "confusion_matrix": cm.tolist(),
        "class_names": class_names,
        "predictions": all_preds.tolist(),
        "true_labels": all_labels.tolist(),
    }


def main():
    parser = argparse.ArgumentParser(description="Evaluate Image Classification Model")
    parser.add_argument(
        "--model_path", type=str, required=True, help="Path to trained model"
    )
    parser.add_argument(
        "--dataset",
        type=str,
        default="cifar10",
        choices=["cifar10", "cifar100", "mnist", "fashionmnist"],
        help="Dataset to evaluate on",
    )
    parser.add_argument("--batch_size", type=int, default=32, help="Batch size")
    parser.add_argument("--data_dir", type=str, default="./data", help="Data directory")
    parser.add_argument(
        "--output_dir",
        type=str,
        default="./evaluation_results",
        help="Output directory for results",
    )
    parser.add_argument(
        "--generate_plots", action="store_true", help="Generate confusion matrix plot"
    )

    args = parser.parse_args()

    # Check if model exists
    if not Path(args.model_path).exists():
        print(f"❌ Model not found: {args.model_path}")
        sys.exit(1)

    # Create output directory
    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    print("[STARTING] Starting Model Evaluation")
    print("=" * 50)
    print(f"Model: {args.model_path}")
    print(f"Dataset: {args.dataset}")
    print(f"Output Directory: {output_dir}")
    print()

    try:
        # Run detailed evaluation
        results = evaluate_model_detailed(
            model_path=args.model_path,
            dataset_name=args.dataset,
            batch_size=args.batch_size,
            data_dir=args.data_dir,
        )

        # Save results
        results_path = output_dir / "evaluation_results.json"
        with open(results_path, "w") as f:
            json.dump(results, f, indent=2)

        # Print summary
        report = results["classification_report"]
        print("[RESULTS] Evaluation Results:")
        print("-" * 30)
        print(f"Overall Accuracy: {report['accuracy']:.2f}")
        print(f"Macro Precision: {report['macro avg']['precision']:.4f}")
        print(f"Macro Recall: {report['macro avg']['recall']:.4f}")
        print(f"Macro F1-Score: {report['macro avg']['f1-score']:.4f}")
        print()
        print("[DETAILS] Detailed Classification Report:")
        print("-" * 40)

        # Print per-class metrics
        class_names = results["class_names"]
        for i, class_name in enumerate(class_names):
            if class_name in report:  # Handle case where class might not be in report
                metrics = report[class_name]
                print(
                    f"{class_name:<30} "
                    f"{metrics['precision']:6.2f} "
                    f"{metrics['recall']:6.2f} "
                    f"{metrics['f1-score']:6.2f} "
                    f"{int(metrics['support']):<6d}"
                )

        # Generate confusion matrix plot if requested
        if args.generate_plots:
            print("\n[RESULTS] Generating confusion matrix plot...")
            cm = np.array(results["confusion_matrix"])
            plot_path = output_dir / "confusion_matrix.png"
            plot_confusion_matrix(cm, class_names, save_path=str(plot_path))

        print("\n[SUCCESS] Evaluation complete!")
        print(f"[SAVED] Results saved to: {results_path}")

        if args.generate_plots:
            print(f"[PLOT] Confusion matrix saved to: {plot_path}")

    except Exception as e:
        print(f"[ERROR] Error during evaluation: {str(e)}")
        import traceback

        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
