#!/usr/bin/env python3
"""
Image Classification Demo Script
===============================

This script demonstrates a trained image classification model by making predictions
on sample images from the test dataset.

Usage:
    python demo_image_classifier.py --model_path models/best_model.pth --dataset cifar10 --num_samples 5

Author: Echoes AI Assistant
"""

import argparse
import sys
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import torch
from torchvision import datasets, transforms

# Add the machine_learning directory to Python path
sys.path.insert(0, str(Path(__file__).parent.parent))

from image_classification.classifier import ImageClassifier, get_class_names


def denormalize(tensor, mean=(0.4914, 0.4822, 0.4465), std=(0.2023, 0.1994, 0.2010)):
    """Denormalize tensor for visualization."""
    for t, m, s in zip(tensor, mean, std):
        t.mul_(s).add_(m)
    return tensor


def show_predictions(
    model_path, dataset_name="cifar10", num_samples=5, data_dir="./data"
):
    """Show model predictions on sample images."""
    print("🔧 Loading model...")
    classifier = ImageClassifier()
    classifier.load_model(model_path)

    # Set up dataset transforms for display
    if dataset_name in ["mnist", "fashionmnist"]:
        transform = transforms.Compose([transforms.ToTensor()])
        mean = (0.1307,)
        std = (0.3081,)
    else:
        transform = transforms.Compose([transforms.ToTensor()])
        mean = (0.4914, 0.4822, 0.4465)
        std = (0.2023, 0.1994, 0.2010)

    # Load test dataset
    print(f"📥 Loading {dataset_name} test dataset...")
    if dataset_name == "cifar10":
        dataset = datasets.CIFAR10(
            data_dir, train=False, download=True, transform=transform
        )
    elif dataset_name == "cifar100":
        dataset = datasets.CIFAR100(
            data_dir, train=False, download=True, transform=transform
        )
    elif dataset_name == "mnist":
        dataset = datasets.MNIST(
            data_dir, train=False, download=True, transform=transform
        )
    elif dataset_name == "fashionmnist":
        dataset = datasets.FashionMNIST(
            data_dir, train=False, download=True, transform=transform
        )
    else:
        raise ValueError(f"Unknown dataset: {dataset_name}")

    class_names = get_class_names(dataset_name)

    # Create figure for displaying results
    fig, axes = plt.subplots(num_samples, 1, figsize=(8, 3 * num_samples))
    if num_samples == 1:
        axes = [axes]

    print(f"🎯 Making predictions on {num_samples} sample images...")

    correct_predictions = 0

    for i in range(num_samples):
        # Get random sample
        idx = np.random.randint(len(dataset))
        image, true_label = dataset[idx]

        # Make prediction
        pred_class, confidence = classifier.predict(image.unsqueeze(0))

        # Check if prediction is correct
        is_correct = pred_class == true_label
        correct_predictions += int(is_correct)

        # Denormalize for display
        display_image = denormalize(image.clone(), mean=mean, std=std)
        display_image = torch.clamp(display_image, 0, 1)

        # Convert to numpy for plotting
        if dataset_name in ["mnist", "fashionmnist"]:
            # Grayscale to RGB for consistent plotting
            display_image = display_image.squeeze().numpy()
            display_image = np.stack([display_image] * 3, axis=-1)
        else:
            display_image = display_image.permute(1, 2, 0).numpy()

        # Plot
        axes[i].imshow(display_image)
        axes[i].axis("off")

        color = "green" if is_correct else "red"
        status = "Correct" if is_correct else "Wrong"

        title = f"{status}: True={class_names[true_label]} | Pred={class_names[pred_class]} | Conf={confidence:.3f}"
        axes[i].set_title(title, color=color, fontsize=10)

    plt.tight_layout()

    # Print summary
    accuracy = correct_predictions / num_samples * 100
    print("\nDemo Results:")
    print(f"Accuracy: {accuracy:.1f}%")
    print(f"Correct predictions: {correct_predictions}/{num_samples}")

    return fig


def main():
    parser = argparse.ArgumentParser(description="Image Classification Demo")
    parser.add_argument(
        "--model_path", type=str, required=True, help="Path to trained model"
    )
    parser.add_argument(
        "--dataset",
        type=str,
        default="cifar10",
        choices=["cifar10", "cifar100", "mnist", "fashionmnist"],
        help="Dataset the model was trained on",
    )
    parser.add_argument(
        "--num_samples", type=int, default=5, help="Number of sample images to show"
    )
    parser.add_argument("--data_dir", type=str, default="./data", help="Data directory")
    parser.add_argument(
        "--save_plot",
        type=str,
        default=None,
        help="Path to save the demo plot (optional)",
    )

    args = parser.parse_args()

    # Check if model exists
    if not Path(args.model_path).exists():
        print(f"Model not found: {args.model_path}")
        sys.exit(1)

    print("Starting Image Classification Demo")
    print("=" * 50)
    print(f"Model: {args.model_path}")
    print(f"Dataset: {args.dataset}")
    print(f"Samples: {args.num_samples}")
    print()

    try:
        # Run demo
        fig = show_predictions(
            model_path=args.model_path,
            dataset_name=args.dataset,
            num_samples=args.num_samples,
            data_dir=args.data_dir,
        )

        # Save or show plot
        if args.save_plot:
            fig.savefig(args.save_plot)
            print(f"Demo plot saved to: {args.save_plot}")
        else:
            plt.show()

        print("\nDemo completed successfully!")

    except Exception as e:
        print(f"Error during demo: {str(e)}")
        import traceback

        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
