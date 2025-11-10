# echoes/core/multimodal_processor.py
"""
Multimodal document processor for the Echoes AI Assistant.
Handles processing of various file types including text, PDFs, images, and audio.
"""

import mimetypes
from typing import Dict, List, Any, Optional
from pathlib import Path
from datetime import datetime, timezone
import json
import logging

logger = logging.getLogger(__name__)


class MultimodalProcessor:
    """Unified processor for handling different document modalities."""

    def __init__(self):
        self.supported_types = {
            # Text-based
            "text/plain": self._process_text_file,
            "text/markdown": self._process_text_file,
            "text/html": self._process_text_file,
            "application/json": self._process_json_file,
            "application/pdf": self._process_pdf_file,
            # Images
            "image/jpeg": self._process_image_file,
            "image/png": self._process_image_file,
            "image/gif": self._process_image_file,
            "image/bmp": self._process_image_file,
            "image/tiff": self._process_image_file,
            # Audio (future)
            "audio/mpeg": self._process_audio_file,
            "audio/wav": self._process_audio_file,
            "audio/ogg": self._process_audio_file,
            "audio/mp4": self._process_audio_file,  # For .m4a files
            "audio/aac": self._process_audio_file,
            "audio/flac": self._process_audio_file,
            "audio/webm": self._process_audio_file,
        }

        self._init_processors()

    def _init_processors(self):
        """Initialize processor dependencies."""
        self.pdf_processor = None
        self.image_processor = None
        self.audio_processor = None

        # Try to import optional dependencies
        try:
            import fitz  # PyMuPDF

            self.pdf_processor = fitz
            logger.info("PDF processing enabled (PyMuPDF)")
        except ImportError:
            logger.warning(
                "PDF processing disabled - install PyMuPDF: pip install PyMuPDF"
            )

        try:
            import pytesseract
            from PIL import Image

            self.image_processor = {"pytesseract": pytesseract, "PIL": Image}
            logger.info("Image processing enabled (Tesseract + PIL)")
        except ImportError:
            logger.warning(
                "Image processing disabled - install dependencies: pip install pytesseract pillow"
            )

        try:
            import speech_recognition as sr

            self.audio_processor = sr
            logger.info("Audio processing enabled (SpeechRecognition)")
        except ImportError:
            logger.warning(
                "Audio processing disabled - install dependencies: pip install SpeechRecognition"
            )

    def can_process(self, mime_type: str) -> bool:
        """Check if a MIME type can be processed."""
        return mime_type in self.supported_types

    def process_file(self, file_path: str) -> Optional[Dict[str, Any]]:
        """
        Process a file based on its MIME type.

        Args:
            file_path: Path to the file to process

        Returns:
            Dictionary with extracted content and metadata, or None if processing failed
        """
        file_path = Path(file_path)

        if not file_path.exists():
            logger.error(f"File not found: {file_path}")
            return None

        # Detect MIME type
        mime_type, _ = mimetypes.guess_type(str(file_path))

        if mime_type is None:
            # Fallback: try to detect based on extension
            ext = file_path.suffix.lower()
            mime_fallback = {
                ".txt": "text/plain",
                ".md": "text/markdown",
                ".html": "text/html",
                ".htm": "text/html",
                ".json": "application/json",
                ".pdf": "application/pdf",
                ".jpg": "image/jpeg",
                ".jpeg": "image/jpeg",
                ".png": "image/png",
                ".gif": "image/gif",
                ".bmp": "image/bmp",
                ".tiff": "image/tiff",
                ".mp3": "audio/mpeg",
                ".wav": "audio/wav",
                ".ogg": "audio/ogg",
                ".m4a": "audio/mp4",  # Apple MPEG-4 audio
                ".aac": "audio/aac",
                ".flac": "audio/flac",
                ".webm": "audio/webm",
            }
            mime_type = mime_fallback.get(ext)

        if mime_type is None or mime_type not in self.supported_types:
            logger.warning(f"Unsupported file type: {mime_type} for {file_path}")
            return None

        try:
            processor = self.supported_types[mime_type]
            return processor(file_path, mime_type)
        except Exception as e:
            logger.error(f"Error processing {file_path}: {str(e)}")
            return None

    def _process_text_file(self, file_path: Path, mime_type: str) -> Dict[str, Any]:
        """Process text-based files."""
        try:
            with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
                content = f.read()

            return {
                "content": content,
                "content_type": "text",
                "word_count": len(content.split()),
                "char_count": len(content),
                "metadata": self._extract_file_metadata(file_path, mime_type),
            }
        except Exception as e:
            raise Exception(f"Failed to read text file: {str(e)}")

    def _process_json_file(self, file_path: Path, mime_type: str) -> Dict[str, Any]:
        """Process JSON files."""
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                data = json.load(f)

            # Convert JSON to readable text
            content = json.dumps(data, indent=2, ensure_ascii=False)

            return {
                "content": content,
                "content_type": "json",
                "json_data": data,
                "metadata": self._extract_file_metadata(file_path, mime_type),
            }
        except Exception as e:
            raise Exception(f"Failed to parse JSON file: {str(e)}")

    def _process_pdf_file(
        self, file_path: Path, mime_type: str
    ) -> Optional[Dict[str, Any]]:
        """Process PDF files using PyMuPDF."""
        if not self.pdf_processor:
            raise Exception("PDF processing not available - install PyMuPDF")

        try:
            doc = self.pdf_processor.open(str(file_path))
            content = ""

            # Extract text from all pages
            for page_num in range(len(doc)):
                page = doc.load_page(page_num)
                content += page.get_text() + "\n"

            metadata = self._extract_file_metadata(file_path, mime_type)
            metadata.update(
                {
                    "pages": len(doc),
                    "pdf_metadata": (
                        dict(doc.metadata) if hasattr(doc, "metadata") else {}
                    ),
                }
            )

            return {
                "content": content.strip(),
                "content_type": "pdf",
                "word_count": len(content.split()),
                "char_count": len(content),
                "metadata": metadata,
            }
        except Exception as e:
            raise Exception(f"Failed to process PDF: {str(e)}")

    def _process_image_file(
        self, file_path: Path, mime_type: str
    ) -> Optional[Dict[str, Any]]:
        """Process image files using OpenAI GPT-4 Vision."""
        if not hasattr(self, "_openai_client"):
            try:
                from openai import OpenAI

                self._openai_client = OpenAI()
            except ImportError:
                logger.error("OpenAI client not available for image processing")
                raise Exception("OpenAI client required for image processing")

        try:
            import base64
            from PIL import Image

            # Open and validate image
            image = Image.open(str(file_path))

            # Convert to base64 for OpenAI API
            import io

            buffer = io.BytesIO()
            # Convert to RGB if necessary
            if image.mode != "RGB":
                image = image.convert("RGB")
            image.save(buffer, format="JPEG")
            image_base64 = base64.b64encode(buffer.getvalue()).decode("utf-8")

            # Analyze image with GPT-4 Vision
            response = self._openai_client.chat.completions.create(
                model="gpt-4o",  # Use GPT-4o which includes vision
                messages=[
                    {
                        "role": "user",
                        "content": [
                            {
                                "type": "text",
                                "text": "Analyze this image in detail. Describe what you see, any text content, the overall composition, colors, and key elements. Provide a comprehensive analysis.",
                            },
                            {
                                "type": "image_url",
                                "image_url": {
                                    "url": f"data:image/jpeg;base64,{image_base64}"
                                },
                            },
                        ],
                    }
                ],
                max_tokens=1000,
                temperature=0.1,
            )

            analysis_text = response.choices[0].message.content

            # Get image metadata
            metadata = self._extract_file_metadata(file_path, mime_type)
            metadata.update(
                {
                    "width": image.width,
                    "height": image.height,
                    "format": image.format,
                    "mode": image.mode,
                    "analysis_tokens": (
                        response.usage.completion_tokens
                        if hasattr(response, "usage")
                        else 0
                    ),
                }
            )

            return {
                "content": analysis_text,
                "content_type": "image_analysis",
                "word_count": len(analysis_text.split()),
                "char_count": len(analysis_text),
                "metadata": metadata,
                "has_text": True,
                "image_info": {
                    "dimensions": f"{image.width}x{image.height}",
                    "format": image.format,
                    "mode": image.mode,
                },
            }
        except Exception as e:
            logger.error(f"Failed to process image with OpenAI Vision: {str(e)}")
            raise Exception(f"Failed to process image: {str(e)}")

    def _process_audio_file(
        self, file_path: Path, mime_type: str
    ) -> Optional[Dict[str, Any]]:
        """Process audio files using OpenAI Whisper API."""
        if not hasattr(self, "_openai_client"):
            try:
                from openai import OpenAI

                self._openai_client = OpenAI()
            except ImportError:
                logger.error("OpenAI client not available for audio processing")
                raise Exception("OpenAI client required for audio processing")

        try:
            # Transcribe audio using Whisper API
            with open(str(file_path), "rb") as audio_file:
                transcript_response = self._openai_client.audio.transcriptions.create(
                    model="whisper-1",
                    file=audio_file,
                    response_format="verbose_json",
                    timestamp_granularities=["segment"],
                )

            # Extract transcription text
            transcription_text = transcript_response.text

            # Calculate audio duration and cost
            audio_duration_seconds = (
                transcript_response.duration
                if hasattr(transcript_response, "duration")
                else 0
            )
            audio_duration_minutes = audio_duration_seconds / 60

            # Whisper cost: $0.006 per minute
            transcription_cost = audio_duration_minutes * 0.006

            metadata = self._extract_file_metadata(file_path, mime_type)
            metadata.update(
                {
                    "audio_duration_seconds": audio_duration_seconds,
                    "audio_duration_minutes": audio_duration_minutes,
                    "transcription_cost": transcription_cost,
                    "language": (
                        transcript_response.language
                        if hasattr(transcript_response, "language")
                        else "unknown"
                    ),
                    "segments": (
                        len(transcript_response.segments)
                        if hasattr(transcript_response, "segments")
                        else 0
                    ),
                }
            )

            return {
                "content": transcription_text,
                "content_type": "audio_transcription",
                "word_count": len(transcription_text.split()),
                "char_count": len(transcription_text),
                "metadata": metadata,
                "audio_info": {
                    "duration_seconds": audio_duration_seconds,
                    "duration_formatted": f"{int(audio_duration_seconds // 3600):02d}:{int((audio_duration_seconds % 3600) // 60):02d}:{int(audio_duration_seconds % 60):02d}",
                    "estimated_cost": f"${transcription_cost:.4f}",
                    "language": (
                        transcript_response.language
                        if hasattr(transcript_response, "language")
                        else "unknown"
                    ),
                },
                "segments": (
                    transcript_response.segments
                    if hasattr(transcript_response, "segments")
                    else []
                ),
            }
        except Exception as e:
            logger.error(f"Failed to process audio with Whisper API: {str(e)}")
            raise Exception(f"Failed to process audio: {str(e)}")

    def _extract_file_metadata(self, file_path: Path, mime_type: str) -> Dict[str, Any]:
        """Extract basic file metadata."""
        stat = file_path.stat()

        return {
            "file_path": str(file_path),
            "file_name": file_path.name,
            "file_size": stat.st_size,
            "mime_type": mime_type,
            "last_modified": stat.st_mtime,
            "file_extension": file_path.suffix.lower(),
            "processed_at": datetime.now(timezone.utc).isoformat(),
        }

    def get_supported_types(self) -> List[str]:
        """Get list of supported MIME types."""
        return list(self.supported_types.keys())

    def get_processor_status(self) -> Dict[str, bool]:
        """Get status of different processors."""
        return {
            "pdf": self.pdf_processor is not None,
            "image": self.image_processor is not None,
            "audio": self.audio_processor is not None,
        }
