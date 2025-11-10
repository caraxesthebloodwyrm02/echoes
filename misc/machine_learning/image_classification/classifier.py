"""
Image Classification Module for Echoes
=====================================

This module provides comprehensive image classification capabilities including:
- Dataset loading and preprocessing
- CNN model architectures
- Training and evaluation utilities
- Model persistence and loading

Author: Echoes AI Assistant
"""

import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import DataLoader, random_split
from torchvision import datasets, transforms, models
import matplotlib.pyplot as plt
import numpy as np
from pathlib import Path
import time
from typing import Dict, List, Tuple, Optional, Union
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class ImageClassifier:
    """
    Comprehensive image classification system using PyTorch.

    Supports:
    - CIFAR-10, CIFAR-100, MNIST, FashionMNIST datasets
    - Custom CNN architectures
    - Pre-trained models (ResNet, VGG, etc.)
    - Training, validation, and testing
    - Model saving/loading
    """

    def __init__(
        self,
        model_type: str = "custom_cnn",
        num_classes: int = 10,
        device: Optional[str] = None,
    ):
        """
        Initialize the image classifier.

        Args:
            model_type: Type of model ('custom_cnn', 'resnet18', 'resnet50', 'vgg16')
            num_classes: Number of output classes
            device: Device to run on ('cuda', 'cpu', or None for auto-detect)
        """
        self.model_type = model_type
        self.num_classes = num_classes
        self.device = device or ("cuda" if torch.cuda.is_available() else "cpu")
        self.model = None
        self.criterion = None
        self.optimizer = None
        self.scheduler = None

        logger.info(
            f"Initializing {model_type} model with {num_classes} classes on {self.device}"
        )

    def build_model(self) -> nn.Module:
        """
        Build the neural network model based on model_type.

        Returns:
            PyTorch model
        """
        if self.model_type == "custom_cnn":
            model = CustomCNN(num_classes=self.num_classes)
        elif self.model_type == "resnet18":
            model = models.resnet18(pretrained=True)
            model.fc = nn.Linear(model.fc.in_features, self.num_classes)
        elif self.model_type == "resnet50":
            model = models.resnet50(pretrained=True)
            model.fc = nn.Linear(model.fc.in_features, self.num_classes)
        elif self.model_type == "vgg16":
            model = models.vgg16(pretrained=True)
            model.classifier[6] = nn.Linear(4096, self.num_classes)
        else:
            raise ValueError(f"Unknown model type: {self.model_type}")

        self.model = model.to(self.device)
        return self.model

    def setup_training(
        self,
        learning_rate: float = 0.001,
        weight_decay: float = 1e-4,
        use_scheduler: bool = True,
    ):
        """
        Set up optimizer, loss function, and learning rate scheduler.

        Args:
            learning_rate: Learning rate for optimizer
            weight_decay: Weight decay for regularization
            use_scheduler: Whether to use learning rate scheduler
        """
        if self.model is None:
            raise ValueError("Model not built. Call build_model() first.")

        self.criterion = nn.CrossEntropyLoss()
        self.optimizer = optim.Adam(
            self.model.parameters(), lr=learning_rate, weight_decay=weight_decay
        )

        if use_scheduler:
            self.scheduler = optim.lr_scheduler.StepLR(
                self.optimizer, step_size=7, gamma=0.1
            )

    def load_dataset(
        self,
        dataset_name: str = "cifar10",
        batch_size: int = 32,
        data_dir: str = "./data",
    ) -> Tuple[DataLoader, DataLoader, DataLoader]:
        """
        Load and preprocess dataset.

        Args:
            dataset_name: Name of dataset ('cifar10', 'cifar100', 'mnist', 'fashionmnist')
            batch_size: Batch size for data loaders
            data_dir: Directory to store dataset

        Returns:
            Tuple of (train_loader, val_loader, test_loader)
        """
        # Define transforms
        if dataset_name in ["mnist", "fashionmnist"]:
            # Grayscale datasets
            transform = transforms.Compose(
                [transforms.ToTensor(), transforms.Normalize((0.1307,), (0.3081,))]
            )
        else:
            # RGB datasets
            transform = transforms.Compose(
                [
                    transforms.RandomHorizontalFlip(),
                    transforms.RandomCrop(32, padding=4),
                    transforms.ToTensor(),
                    transforms.Normalize(
                        (0.4914, 0.4822, 0.4465), (0.2023, 0.1994, 0.2010)
                    ),
                ]
            )

            # Test transform (no augmentation)
            test_transform = transforms.Compose(
                [
                    transforms.ToTensor(),
                    transforms.Normalize(
                        (0.4914, 0.4822, 0.4465), (0.2023, 0.1994, 0.2010)
                    ),
                ]
            )

        # Load dataset
        if dataset_name == "cifar10":
            train_dataset = datasets.CIFAR10(
                data_dir, train=True, download=True, transform=transform
            )
            test_dataset = datasets.CIFAR10(
                data_dir, train=False, download=True, transform=test_transform
            )
        elif dataset_name == "cifar100":
            train_dataset = datasets.CIFAR100(
                data_dir, train=True, download=True, transform=transform
            )
            test_dataset = datasets.CIFAR100(
                data_dir, train=False, download=True, transform=test_transform
            )
        elif dataset_name == "mnist":
            train_dataset = datasets.MNIST(
                data_dir, train=True, download=True, transform=transform
            )
            test_dataset = datasets.MNIST(
                data_dir, train=False, download=True, transform=transform
            )
        elif dataset_name == "fashionmnist":
            train_dataset = datasets.FashionMNIST(
                data_dir, train=True, download=True, transform=transform
            )
            test_dataset = datasets.FashionMNIST(
                data_dir, train=False, download=True, transform=transform
            )
        else:
            raise ValueError(f"Unknown dataset: {dataset_name}")

        # Split training data into train/val
        train_size = int(0.8 * len(train_dataset))
        val_size = len(train_dataset) - train_size
        train_dataset, val_dataset = random_split(train_dataset, [train_size, val_size])

        # Create data loaders
        train_loader = DataLoader(
            train_dataset, batch_size=batch_size, shuffle=True, num_workers=2
        )
        val_loader = DataLoader(
            val_dataset, batch_size=batch_size, shuffle=False, num_workers=2
        )
        test_loader = DataLoader(
            test_dataset, batch_size=batch_size, shuffle=False, num_workers=2
        )

        logger.info(f"Loaded {dataset_name} dataset:")
        logger.info(f"  Train: {len(train_dataset)} samples")
        logger.info(f"  Val: {len(val_dataset)} samples")
        logger.info(f"  Test: {len(test_dataset)} samples")

        return train_loader, val_loader, test_loader

    def train_epoch(self, train_loader: DataLoader) -> float:
        """Train for one epoch."""
        self.model.train()
        running_loss = 0.0
        correct = 0
        total = 0

        for inputs, labels in train_loader:
            inputs, labels = inputs.to(self.device), labels.to(self.device)

            self.optimizer.zero_grad()
            outputs = self.model(inputs)
            loss = self.criterion(outputs, labels)
            loss.backward()
            self.optimizer.step()

            running_loss += loss.item()
            _, predicted = outputs.max(1)
            total += labels.size(0)
            correct += predicted.eq(labels).sum().item()

        epoch_loss = running_loss / len(train_loader)
        epoch_acc = 100.0 * correct / total

        return epoch_loss, epoch_acc

    def validate(self, val_loader: DataLoader) -> Tuple[float, float]:
        """Validate the model."""
        self.model.eval()
        running_loss = 0.0
        correct = 0
        total = 0

        with torch.no_grad():
            for inputs, labels in val_loader:
                inputs, labels = inputs.to(self.device), labels.to(self.device)

                outputs = self.model(inputs)
                loss = self.criterion(outputs, labels)

                running_loss += loss.item()
                _, predicted = outputs.max(1)
                total += labels.size(0)
                correct += predicted.eq(labels).sum().item()

        val_loss = running_loss / len(val_loader)
        val_acc = 100.0 * correct / total

        return val_loss, val_acc

    def train(
        self,
        train_loader: DataLoader,
        val_loader: DataLoader,
        num_epochs: int = 10,
        save_path: Optional[str] = None,
    ) -> Dict[str, List[float]]:
        """
        Train the model.

        Args:
            train_loader: Training data loader
            val_loader: Validation data loader
            num_epochs: Number of training epochs
            save_path: Path to save the best model

        Returns:
            Dictionary with training history
        """
        if self.model is None or self.criterion is None or self.optimizer is None:
            raise ValueError(
                "Model not properly set up. Call build_model() and setup_training() first."
            )

        history = {"train_loss": [], "train_acc": [], "val_loss": [], "val_acc": []}

        best_val_acc = 0.0

        logger.info(f"Starting training for {num_epochs} epochs...")

        for epoch in range(num_epochs):
            start_time = time.time()

            # Train
            train_loss, train_acc = self.train_epoch(train_loader)

            # Validate
            val_loss, val_acc = self.validate(val_loader)

            # Update learning rate
            if self.scheduler:
                self.scheduler.step()

            # Save best model
            if val_acc > best_val_acc and save_path:
                best_val_acc = val_acc
                self.save_model(save_path)
                logger.info(f"Saved best model with val_acc: {val_acc:.2f}%")

            # Log progress
            epoch_time = time.time() - start_time
            logger.info(
                f"Epoch {epoch+1}/{num_epochs} - "
                f"Train Loss: {train_loss:.4f}, Train Acc: {train_acc:.2f}% - "
                f"Val Loss: {val_loss:.4f}, Val Acc: {val_acc:.2f}% - "
                f"Time: {epoch_time:.2f}s"
            )

            # Store history
            history["train_loss"].append(train_loss)
            history["train_acc"].append(train_acc)
            history["val_loss"].append(val_loss)
            history["val_acc"].append(val_acc)

        logger.info(
            f"Training completed. Best validation accuracy: {best_val_acc:.2f}%"
        )
        return history

    def evaluate(self, test_loader: DataLoader) -> Dict[str, float]:
        """
        Evaluate the model on test data.

        Args:
            test_loader: Test data loader

        Returns:
            Dictionary with evaluation metrics
        """
        if self.model is None:
            raise ValueError(
                "Model not loaded. Call build_model() or load_model() first."
            )

        self.model.eval()
        test_loss = 0.0
        correct = 0
        total = 0

        with torch.no_grad():
            for inputs, labels in test_loader:
                inputs, labels = inputs.to(self.device), labels.to(self.device)

                outputs = self.model(inputs)
                loss = self.criterion(outputs, labels)

                test_loss += loss.item()
                _, predicted = outputs.max(1)
                total += labels.size(0)
                correct += predicted.eq(labels).sum().item()

        test_loss /= len(test_loader)
        test_acc = 100.0 * correct / total

        results = {
            "test_loss": test_loss,
            "test_accuracy": test_acc,
            "total_samples": total,
            "correct_predictions": correct,
        }

        logger.info(f"Test Results - Loss: {test_loss:.4f}, Accuracy: {test_acc:.2f}%")
        return results

    def predict(self, image: torch.Tensor) -> Tuple[int, float]:
        """
        Make prediction on a single image.

        Args:
            image: Input image tensor

        Returns:
            Tuple of (predicted_class, confidence)
        """
        if self.model is None:
            raise ValueError(
                "Model not loaded. Call build_model() or load_model() first."
            )

        self.model.eval()
        with torch.no_grad():
            image = image.to(self.device)
            outputs = self.model(image)
            probabilities = torch.nn.functional.softmax(outputs, dim=1)
            confidence, predicted = torch.max(probabilities, 1)

        return predicted.item(), confidence.item()

    def save_model(self, path: str):
        """Save model state to file."""
        torch.save(
            {
                "model_state_dict": self.model.state_dict(),
                "model_type": self.model_type,
                "num_classes": self.num_classes,
                "optimizer_state_dict": (
                    self.optimizer.state_dict() if self.optimizer else None
                ),
                "scheduler_state_dict": (
                    self.scheduler.state_dict() if self.scheduler else None
                ),
            },
            path,
        )
        logger.info(f"Model saved to {path}")

    def load_model(self, path: str):
        """Load model state from file."""
        checkpoint = torch.load(path, map_location=self.device)

        # Rebuild model if not already built
        if self.model is None:
            self.model_type = checkpoint.get("model_type", self.model_type)
            self.num_classes = checkpoint.get("num_classes", self.num_classes)
            self.build_model()

        self.model.load_state_dict(checkpoint["model_state_dict"])

        if self.optimizer and "optimizer_state_dict" in checkpoint:
            self.optimizer.load_state_dict(checkpoint["optimizer_state_dict"])

        if self.scheduler and "scheduler_state_dict" in checkpoint:
            self.scheduler.load_state_dict(checkpoint["scheduler_state_dict"])

        logger.info(f"Model loaded from {path}")


class CustomCNN(nn.Module):
    """Custom CNN architecture for image classification."""

    def __init__(self, num_classes: int = 10):
        super(CustomCNN, self).__init__()
        self.features = nn.Sequential(
            nn.Conv2d(3, 64, kernel_size=3, padding=1),
            nn.BatchNorm2d(64),
            nn.ReLU(inplace=True),
            nn.Conv2d(64, 64, kernel_size=3, padding=1),
            nn.BatchNorm2d(64),
            nn.ReLU(inplace=True),
            nn.MaxPool2d(kernel_size=2, stride=2),
            nn.Conv2d(64, 128, kernel_size=3, padding=1),
            nn.BatchNorm2d(128),
            nn.ReLU(inplace=True),
            nn.Conv2d(128, 128, kernel_size=3, padding=1),
            nn.BatchNorm2d(128),
            nn.ReLU(inplace=True),
            nn.MaxPool2d(kernel_size=2, stride=2),
            nn.Conv2d(128, 256, kernel_size=3, padding=1),
            nn.BatchNorm2d(256),
            nn.ReLU(inplace=True),
            nn.Conv2d(256, 256, kernel_size=3, padding=1),
            nn.BatchNorm2d(256),
            nn.ReLU(inplace=True),
            nn.MaxPool2d(kernel_size=2, stride=2),
        )

        self.classifier = nn.Sequential(
            nn.Dropout(0.5),
            nn.Linear(256 * 4 * 4, 512),
            nn.ReLU(inplace=True),
            nn.Dropout(0.5),
            nn.Linear(512, num_classes),
        )

    def forward(self, x):
        x = self.features(x)
        x = x.view(x.size(0), -1)
        x = self.classifier(x)
        return x


def plot_training_history(
    history: Dict[str, List[float]], save_path: Optional[str] = None
):
    """Plot training history."""
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 4))

    # Loss plot
    ax1.plot(history["train_loss"], label="Train Loss")
    ax1.plot(history["val_loss"], label="Val Loss")
    ax1.set_title("Loss")
    ax1.set_xlabel("Epoch")
    ax1.set_ylabel("Loss")
    ax1.legend()

    # Accuracy plot
    ax2.plot(history["train_acc"], label="Train Acc")
    ax2.plot(history["val_acc"], label="Val Acc")
    ax2.set_title("Accuracy")
    ax2.set_xlabel("Epoch")
    ax2.set_ylabel("Accuracy (%)")
    ax2.legend()

    plt.tight_layout()

    if save_path:
        plt.savefig(save_path)
        logger.info(f"Training history plot saved to {save_path}")
    else:
        plt.show()


def get_class_names(dataset_name: str) -> List[str]:
    """Get class names for a dataset."""
    if dataset_name == "cifar10":
        return [
            "airplane",
            "automobile",
            "bird",
            "cat",
            "deer",
            "dog",
            "frog",
            "horse",
            "ship",
            "truck",
        ]
    elif dataset_name == "cifar100":
        # CIFAR-100 has 100 classes, returning first 20 for brevity
        return [f"class_{i}" for i in range(100)]
    elif dataset_name == "mnist":
        return [str(i) for i in range(10)]
    elif dataset_name == "fashionmnist":
        return [
            "T-shirt/top",
            "Trouser",
            "Pullover",
            "Dress",
            "Coat",
            "Sandal",
            "Shirt",
            "Sneaker",
            "Bag",
            "Ankle boot",
        ]
    else:
        return [f"class_{i}" for i in range(10)]
