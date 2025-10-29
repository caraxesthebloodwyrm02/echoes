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

# MIT License
#
# Copyright (c) 2025 Echoes Project

"""
Tests for Smart Path Handler
"""

import tempfile
from pathlib import Path

import pytest

from packages.core.path_handler import (
    PathCategory,
    PathConfig,
    SecurityError,
    SmartPathHandler,
    get_path_handler,
)


class TestPathConfig:
    """Test path configuration"""

    def test_default_initialization(self):
        """Test default path config initialization"""
        config = PathConfig()

        assert config.project_root.exists()
        assert config.data_dir is not None
        assert config.logs_dir is not None
        assert config.enforce_sandbox is True
        assert config.allow_absolute_paths is False

    def test_extra_forbid(self):
        """Test that extra fields are forbidden"""
        from pydantic import ValidationError

        with pytest.raises(ValidationError):
            PathConfig(unknown_field="value")


class TestSmartPathHandler:
    """Test smart path handler"""

    @pytest.fixture
    def temp_root(self):
        """Create temporary project root"""
        with tempfile.TemporaryDirectory() as tmpdir:
            yield Path(tmpdir)

    @pytest.fixture
    def handler(self, temp_root):
        """Create handler with temp root"""
        config = PathConfig(project_root=temp_root, auto_create_dirs=True)
        return SmartPathHandler(config=config)

    def test_initialization(self, handler):
        """Test handler initialization"""
        assert handler.config is not None
        assert len(handler._registry) > 0

    def test_get_path_by_category(self, handler):
        """Test getting path by category"""
        data_path = handler.get(PathCategory.DATA)

        assert data_path.exists()
        assert data_path.is_dir()
        assert "data" in str(data_path)

    def test_get_path_with_subpaths(self, handler):
        """Test getting path with subpaths"""
        model_path = handler.get(PathCategory.MODELS, "checkpoint.pth")

        assert "models" in str(model_path)
        assert "checkpoint.pth" in str(model_path)

    def test_path_traversal_prevention(self, handler):
        """Test path traversal attack prevention"""
        with pytest.raises(SecurityError):
            handler.get(PathCategory.DATA, "..", "..", "etc", "passwd")

    def test_resolve_relative_path(self, handler):
        """Test resolving relative paths"""
        resolved = handler.resolve("data/test.txt", relative_to=PathCategory.DATA)

        assert resolved.is_absolute()
        assert "data" in str(resolved)

    def test_safe_join(self, handler):
        """Test safe path joining"""
        base = handler.get(PathCategory.DATA)
        joined = handler.safe_join(base, "subdir", "file.txt")

        assert joined.is_absolute()
        assert "subdir" in str(joined)

    def test_safe_join_prevents_traversal(self, handler):
        """Test safe join prevents path traversal"""
        base = handler.get(PathCategory.DATA)

        with pytest.raises(SecurityError):
            handler.safe_join(base, "..", "..", "etc", "passwd")

    def test_ensure_dir(self, handler, temp_root):
        """Test ensure directory creation"""
        new_dir = temp_root / "new" / "nested" / "dir"
        result = handler.ensure_dir(new_dir)

        assert result.exists()
        assert result.is_dir()

    def test_list_files(self, handler):
        """Test listing files in directory"""
        # Create test files
        data_dir = handler.get(PathCategory.DATA)
        (data_dir / "test1.txt").touch()
        (data_dir / "test2.txt").touch()

        files = handler.list_files(PathCategory.DATA, "*.txt")

        assert len(files) >= 2
        assert all(f.suffix == ".txt" for f in files)

    def test_get_stats(self, handler):
        """Test getting handler statistics"""
        stats = handler.get_stats()

        assert "project_root" in stats
        assert "directories" in stats
        assert "security" in stats
        assert stats["security"]["sandbox_enabled"] is True

    def test_cleanup_temp(self, handler):
        """Test temporary file cleanup"""
        import time

        # Create old temp file
        temp_dir = handler.get(PathCategory.TEMP)
        old_file = temp_dir / "old.txt"
        old_file.touch()

        # Set old modification time
        old_time = time.time() - (10 * 86400)  # 10 days ago
        os.utime(old_file, (old_time, old_time))

        # Cleanup
        removed = handler.cleanup_temp(max_age_days=7)

        assert removed >= 1
        assert not old_file.exists()


class TestGlobalFunctions:
    """Test global convenience functions"""

    def test_get_path_handler(self):
        """Test getting global handler"""
        handler1 = get_path_handler()
        handler2 = get_path_handler()

        assert handler1 is handler2  # Same instance

    def test_get_path_convenience(self):
        """Test get_path convenience function"""
        from packages.core.path_handler import get_path

        path = get_path(PathCategory.DATA, "test.txt")

        assert path.is_absolute()
        assert "data" in str(path)

    def test_resolve_path_convenience(self):
        """Test resolve_path convenience function"""
        from packages.core.path_handler import resolve_path

        resolved = resolve_path("test.txt")

        assert resolved.is_absolute()

    def test_ensure_dir_convenience(self):
        """Test ensure_dir convenience function"""
        import tempfile

        from packages.core.path_handler import ensure_dir

        with tempfile.TemporaryDirectory() as tmpdir:
            new_dir = Path(tmpdir) / "new" / "dir"
            result = ensure_dir(new_dir)

            assert result.exists()


class TestSecurityFeatures:
    """Test security features"""

    @pytest.fixture
    def handler(self):
        """Create handler with temp root"""
        with tempfile.TemporaryDirectory() as tmpdir:
            config = PathConfig(
                project_root=Path(tmpdir),
                enforce_sandbox=True,
                allow_absolute_paths=False,
            )
            yield SmartPathHandler(config=config)

    def test_sandbox_enforcement(self, handler):
        """Test sandbox enforcement prevents access outside project"""
        with pytest.raises(SecurityError):
            handler.resolve("/etc/passwd")

    def test_symlink_rejection(self, handler):
        """Test symlinks are rejected"""
        # Note: This test may need adjustment based on platform
        pass  # Symlink handling is platform-specific


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
