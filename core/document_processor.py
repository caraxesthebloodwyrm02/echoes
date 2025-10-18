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

"""Batch document processing utilities."""

import glob
import logging
from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List, Optional

from utils.path_resolver import PathResolver

# Import privacy filter
try:
    from packages.security.privacy_filter import PrivacyFilter

    privacy_filter = PrivacyFilter()
except ImportError:
    # Fallback if privacy filter not available
    privacy_filter = None


@dataclass
class ProcessingResult:
    """Result of document processing."""

    file_path: Path
    success: bool
    error_message: Optional[str] = None
    processed_content: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None


class DocumentProcessor:
    """Batch document processor with error handling and logging."""

    def __init__(
        self,
        input_dir: str,
        output_dir: str,
        file_pattern: str = "*.txt",
        max_workers: int = 4,
        logger: Optional[logging.Logger] = None,
    ):
        """Initialize document processor."""
        self.input_dir = Path(input_dir)
        self.output_dir = Path(output_dir)
        self.file_pattern = file_pattern
        self.max_workers = max_workers
        self.logger = logger or logging.getLogger(__name__)

        # Ensure output directory exists
        path_resolver = PathResolver()
        path_resolver.ensure_directory(self.output_dir)

    def discover_files(self) -> List[Path]:
        """Discover files matching the pattern."""
        try:
            pattern = str(self.input_dir / self.file_pattern)
            files = [Path(f) for f in glob.glob(pattern)]
            self.logger.info(
                f"Discovered {len(files)} files matching '{self.file_pattern}'"
            )
            return files
        except Exception as e:
            self.logger.error(f"Error discovering files: {e}")
            return []

    def process_file(self, file_path: Path) -> ProcessingResult:
        """Process a single document file."""
        try:
            self.logger.debug(f"Processing file: {file_path}")

            # Read file content
            content = file_path.read_text(encoding="utf-8")

            # Apply privacy filtering to input content if available
            if privacy_filter:
                original_content = content
                content = privacy_filter.mask(content)
                if content != original_content:
                    self.logger.info(f"Applied privacy filtering to {file_path}")

            # Apply processing logic (can be customized)
            processed_content = self._process_content(content, file_path)

            # Apply additional privacy filtering to processed content if available
            if privacy_filter:
                processed_content = privacy_filter.mask(processed_content)

            # Generate output path
            output_path = self._generate_output_path(file_path)

            # Write processed content
            output_path.write_text(processed_content, encoding="utf-8")

            # Create metadata
            metadata = {
                "original_size": len(content),
                "processed_size": len(processed_content),
                "timestamp": file_path.stat().st_mtime,
                "output_path": str(output_path),
                "privacy_filtered": privacy_filter is not None,
            }

            return ProcessingResult(
                file_path=file_path,
                success=True,
                processed_content=processed_content,
                metadata=metadata,
            )

        except Exception as e:
            error_msg = f"Failed to process {file_path}: {str(e)}"
            self.logger.error(error_msg)
            return ProcessingResult(
                file_path=file_path, success=False, error_message=error_msg
            )

    def _process_content(self, content: str, file_path: Path) -> str:
        """Process the content of a document (override in subclasses)."""
        # Default processing: basic text cleaning
        return content.strip()

    def _generate_output_path(self, input_path: Path) -> Path:
        """Generate output path for processed file."""
        relative_path = input_path.relative_to(self.input_dir)
        return self.output_dir / relative_path

    def run_batch(self) -> List[ProcessingResult]:
        """Run batch processing on all discovered files."""
        files = self.discover_files()
        if not files:
            self.logger.warning("No files found for processing")
            return []

        results = []
        self.logger.info(f"Starting batch processing of {len(files)} files")

        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            future_to_file = {
                executor.submit(self.process_file, file_path): file_path
                for file_path in files
            }

            for future in as_completed(future_to_file):
                result = future.result()
                results.append(result)

                if result.success:
                    self.logger.info(f"Successfully processed: {result.file_path}")
                else:
                    self.logger.error(f"Failed to process: {result.file_path}")

        successful = sum(1 for r in results if r.success)
        self.logger.info(
            f"Batch processing complete: {successful}/{len(results)} successful"
        )

        return results

    def run_maintenance(self) -> Dict[str, Any]:
        """Run maintenance tasks on processed files."""
        try:
            # Clean up temporary files
            temp_files = list(self.output_dir.glob("*.tmp"))
            for temp_file in temp_files:
                temp_file.unlink()
                self.logger.info(f"Cleaned up temporary file: {temp_file}")

            # Validate processed files
            processed_files = list(self.output_dir.rglob("*"))
            valid_files = [
                f for f in processed_files if f.is_file() and f.stat().st_size > 0
            ]

            return {
                "temp_files_cleaned": len(temp_files),
                "valid_files": len(valid_files),
                "total_files": len(processed_files),
                "success": True,
            }

        except Exception as e:
            error_msg = f"Maintenance failed: {str(e)}"
            self.logger.error(error_msg)
            return {"error": error_msg, "success": False}


def create_document_processor(
    input_dir: str, output_dir: str, **kwargs
) -> DocumentProcessor:
    """Factory function to create a document processor."""
    return DocumentProcessor(input_dir=input_dir, output_dir=output_dir, **kwargs)
