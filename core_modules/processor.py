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
Multimodal AI Processing Pipeline
Handles image, audio, and text processing with cross-modal reasoning
"""

import io
from typing import Any, Dict, List, Union

import numpy as np
import torch
import torchaudio
import torchvision.transforms as transforms
from PIL import Image
from torchvision.models import resnet50
from transformers import CLIPModel, CLIPProcessor


class MultimodalProcessor:
    """Unified processor for multiple data modalities"""

    def __init__(self):
        # Initialize models
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

        # CLIP for image-text understanding
        self.clip_model = CLIPModel.from_pretrained("openai/clip-vit-base-patch32")
        self.clip_processor = CLIPProcessor.from_pretrained("openai/clip-vit-base-patch32")
        self.clip_model.to(self.device)

        # ResNet for image classification
        self.resnet = resnet50(pretrained=True)
        self.resnet.eval()
        self.resnet.to(self.device)

        # Image preprocessing
        self.image_transform = transforms.Compose(
            [
                transforms.Resize(256),
                transforms.CenterCrop(224),
                transforms.ToTensor(),
                transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225]),
            ]
        )

    def process_image(self, image_input: Union[str, bytes, Image.Image]) -> Dict[str, Any]:
        """Process image input and extract features"""
        # Load image
        if isinstance(image_input, str):
            image = Image.open(image_input).convert("RGB")
        elif isinstance(image_input, bytes):
            image = Image.open(io.BytesIO(image_input)).convert("RGB")
        else:
            image = image_input

        # CLIP processing
        inputs = self.clip_processor(images=image, return_tensors="pt")
        inputs = {k: v.to(self.device) for k, v in inputs.items()}

        with torch.no_grad():
            image_features = self.clip_model.get_image_features(**inputs)
            image_features = image_features / image_features.norm(dim=-1, keepdim=True)

        # ResNet classification
        tensor_image = self.image_transform(image).unsqueeze(0).to(self.device)
        with torch.no_grad():
            resnet_features = self.resnet(tensor_image)

        return {
            "clip_features": image_features.cpu().numpy(),
            "resnet_logits": resnet_features.cpu().numpy(),
            "image_size": image.size,
            "format": image.format,
        }

    def process_text(self, text: str) -> Dict[str, Any]:
        """Process text input and extract features"""
        inputs = self.clip_processor(text=[text], return_tensors="pt")
        inputs = {k: v.to(self.device) for k, v in inputs.items()}

        with torch.no_grad():
            text_features = self.clip_model.get_text_features(**inputs)
            text_features = text_features / text_features.norm(dim=-1, keepdim=True)

        return {
            "text_features": text_features.cpu().numpy(),
            "text_length": len(text),
            "word_count": len(text.split()),
        }

    def cross_modal_similarity(self, image_features: np.ndarray, text_features: np.ndarray) -> float:
        """Calculate similarity between image and text features"""
        # Cosine similarity
        similarity = np.dot(image_features.flatten(), text_features.flatten())
        return float(similarity)

    def multimodal_reasoning(self, image_path: str, text_queries: List[str]) -> Dict[str, Any]:
        """Perform cross-modal reasoning between image and text"""
        # Process image
        image_data = self.process_image(image_path)

        # Process text queries
        text_results = []
        similarities = []

        for query in text_queries:
            text_data = self.process_text(query)
            similarity = self.cross_modal_similarity(image_data["clip_features"], text_data["text_features"])

            text_results.append(text_data)
            similarities.append(similarity)

        # Find best matching query
        best_idx = np.argmax(similarities)

        return {
            "image_analysis": image_data,
            "text_analyses": text_results,
            "similarities": similarities,
            "best_match": {
                "query": text_queries[best_idx],
                "similarity": similarities[best_idx],
                "index": best_idx,
            },
            "reasoning": f"Image most closely matches: '{text_queries[best_idx]}' "
            f"(similarity: {similarities[best_idx]:.3f})",
        }


class AudioProcessor:
    """Audio processing capabilities"""

    def __init__(self):
        self.sample_rate = 16000

    def process_audio(self, audio_path: str) -> Dict[str, Any]:
        """Process audio file and extract features"""
        try:
            # Load audio
            waveform, sample_rate = torchaudio.load(audio_path)

            # Resample if needed
            if sample_rate != self.sample_rate:
                resampler = torchaudio.transforms.Resample(sample_rate, self.sample_rate)
                waveform = resampler(waveform)

            # Convert to mono if stereo
            if waveform.shape[0] > 1:
                waveform = torch.mean(waveform, dim=0, keepdim=True)

            # Extract MFCC features
            mfcc_transform = torchaudio.transforms.MFCC(
                sample_rate=self.sample_rate,
                n_mfcc=13,
                melkwargs={"n_fft": 400, "hop_length": 160, "n_mels": 23},
            )

            mfcc = mfcc_transform(waveform)

            return {
                "waveform": waveform.numpy(),
                "mfcc": mfcc.numpy(),
                "duration": waveform.shape[1] / self.sample_rate,
                "sample_rate": self.sample_rate,
            }

        except Exception as e:
            return {"error": str(e)}


# Example usage
def demo_multimodal_processing():
    """Demonstrate multimodal capabilities"""
    # Removed unused variables: processor, audio_processor, text_queries
    return {
        "multimodal_processor": "initialized",
        "audio_processor": "initialized",
        "capabilities": [
            "image-text similarity",
            "image classification",
            "audio feature extraction",
        ],
    }


if __name__ == "__main__":
    demo_multimodal_processing()
