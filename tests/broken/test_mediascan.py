"""
Tests for MediaScan library.
"""

import json
import tempfile
from pathlib import Path

import pytest

from mediascan import MediaScanner, Movie, TVSeries


class TestMediaScanner:
    """Test cases for MediaScanner class."""

    def setup_method(self):
        """Set up test fixtures."""
        self.temp_dir = tempfile.mkdtemp()
        self.test_data = [
            {
                "title": "Test Movie",
                "year": "2023",
                "director": "Test Director",
                "type": "movie",
            },
            {
                "title": "Test TV Series",
                "year": "2022",
                "director": "Test Director",
                "type": "tv",
                "seasons": "2",
                "episodes": "20",
            },
        ]

        # Create test JSON file
        self.test_file = Path(self.temp_dir) / "test.json"
        with open(self.test_file, "w") as f:
            json.dump(self.test_data, f)

    def teardown_method(self):
        """Clean up test fixtures."""
        import shutil

        shutil.rmtree(self.temp_dir)

    def test_scanner_initialization(self):
        """Test scanner initialization."""
        scanner = MediaScanner(self.temp_dir)
        assert scanner.search_directory.exists()

        with pytest.raises(Exception):
            MediaScanner("/nonexistent/path")

    def test_find_by_title_exact_match(self):
        """Test finding media by exact title."""
        scanner = MediaScanner(self.temp_dir)
        result = scanner.find_by_title("Test Movie")

        assert result is not None
        assert isinstance(result, Movie)
        assert result.title == "Test Movie"
        assert result.director == "Test Director"
        assert result.rank == 1

    def test_find_by_title_partial_match(self):
        """Test finding media by partial title."""
        scanner = MediaScanner(self.temp_dir)
        result = scanner.find_by_title("TV Series")

        assert result is not None
        assert isinstance(result, TVSeries)
        assert result.title == "Test TV Series"
        assert result.seasons == "2"
        assert result.episodes == "20"

    def test_find_by_title_not_found(self):
        """Test searching for non-existent title."""
        scanner = MediaScanner(self.temp_dir)
        result = scanner.find_by_title("Nonexistent Movie")

        assert result is None

    def test_find_by_director(self):
        """Test finding media by director."""
        scanner = MediaScanner(self.temp_dir)
        results = scanner.find_by_director("Test Director")

        assert len(results) == 2
        assert all(item.director == "Test Director" for item in results)
        assert isinstance(results[0], Movie)
        assert isinstance(results[1], TVSeries)

    def test_list_all(self):
        """Test listing all media items."""
        scanner = MediaScanner(self.temp_dir)
        results = scanner.list_all()

        assert len(results) == 2
        assert results[0].rank == 1
        assert results[1].rank == 2

    def test_list_all_with_limit(self):
        """Test listing media items with limit."""
        scanner = MediaScanner(self.temp_dir)
        results = scanner.list_all(limit=1)

        assert len(results) == 1
        assert results[0].rank == 1

    def test_get_stats(self):
        """Test getting database statistics."""
        scanner = MediaScanner(self.temp_dir)
        stats = scanner.get_stats()

        assert stats["json_files"] == 1
        assert stats["total_items"] == 2
        assert stats["search_directory"] == self.temp_dir
        assert stats["cache_size"] == 0

    def test_cache_functionality(self):
        """Test that caching works."""
        scanner = MediaScanner(self.temp_dir)

        # First search
        result1 = scanner.find_by_title("Test Movie")
        assert result1 is not None

        # Second search should use cache
        result2 = scanner.find_by_title("Test Movie")
        assert result2 is not None
        assert result1.title == result2.title

        # Check cache size
        stats = scanner.get_stats()
        assert stats["cache_size"] > 0

        # Clear cache
        scanner.clear_cache()
        stats = scanner.get_stats()
        assert stats["cache_size"] == 0

    def test_invalid_json_file(self):
        """Test handling of invalid JSON files."""
        # Create invalid JSON file
        invalid_file = Path(self.temp_dir) / "invalid.json"
        with open(invalid_file, "w") as f:
            f.write("{ invalid json }")

        scanner = MediaScanner(self.temp_dir)
        # Should not raise exception, just skip invalid file
        result = scanner.find_by_title("Test Movie")
        assert result is not None


class TestMediaItem:
    """Test cases for MediaItem classes."""

    def test_movie_creation(self):
        """Test Movie object creation."""
        movie = Movie(
            "Test Movie", 1, "/path/to/file.json", year="2023", director="Test Director"
        )

        assert movie.title == "Test Movie"
        assert movie.rank == 1
        assert movie.filepath == "/path/to/file.json"
        assert movie.year == "2023"
        assert movie.director == "Test Director"
        assert movie.type == "Movie"

    def test_tv_series_creation(self):
        """Test TVSeries object creation."""
        tv_series = TVSeries(
            "Test Show",
            1,
            "/path/to/file.json",
            year="2022",
            director="Test Director",
            seasons="5",
            episodes="50",
        )

        assert tv_series.title == "Test Show"
        assert tv_series.type == "TV Series"
        assert tv_series.seasons == "5"
        assert tv_series.episodes == "50"

    def test_to_dict(self):
        """Test to_dict method."""
        movie = Movie(
            "Test Movie", 1, "/path/to/file.json", year="2023", director="Test Director"
        )
        movie_dict = movie.to_dict()

        expected_keys = {"title", "rank", "filepath", "year", "director", "type"}
        assert set(movie_dict.keys()) == expected_keys
        assert movie_dict["title"] == "Test Movie"

    def test_tv_series_to_dict(self):
        """Test TVSeries to_dict method includes seasons and episodes."""
        tv_series = TVSeries(
            "Test Show", 1, "/path/to/file.json", seasons="5", episodes="50"
        )
        tv_dict = tv_series.to_dict()

        assert "seasons" in tv_dict
        assert "episodes" in tv_dict
        assert tv_dict["seasons"] == "5"
        assert tv_dict["episodes"] == "50"


if __name__ == "__main__":
    pytest.main([__file__])
