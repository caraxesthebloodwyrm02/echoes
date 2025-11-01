"""
Image Classification Package for Echoes
======================================

This package provides comprehensive image classification capabilities:

Modules:
- classifier.py: Main ImageClassifier class with training and evaluation
- train.py: Training script for image classification models
- evaluate.py: Evaluation script with detailed metrics
- demo.py: Demo script for showcasing trained models

Supported Models:
- CustomCNN: Custom convolutional neural network
- ResNet18/50: Pre-trained ResNet models
- VGG16: Pre-trained VGG model

Supported Datasets:
- CIFAR-10/100: RGB images (32x32)
- MNIST: Handwritten digits (28x28 grayscale)
- FashionMNIST: Fashion items (28x28 grayscale)

Usage:
    from machine_learning.image_classification.classifier import ImageClassifier

    # Initialize classifier
    classifier = ImageClassifier(model_type='custom_cnn', num_classes=10)

    # Build model and setup training
    classifier.build_model()
    classifier.setup_training()

    # Load dataset and train
    train_loader, val_loader, test_loader = classifier.load_dataset('cifar10')
    history = classifier.train(train_loader, val_loader, num_epochs=10)

Author: Echoes AI Assistant
"""

from .classifier import ImageClassifier, CustomCNN, plot_training_history, get_class_names

__all__ = [
    'ImageClassifier',
    'CustomCNN',
    'plot_training_history',
    'get_class_names'
]
