# MediaScan

A lightweight Python library for searching media items (movies, TV series) in JSON files.

## Features

- 🔍 **Simple Search**: Find media by title or director
- 📺 **Multi-Type Support**: Handle both movies and TV series
- 🚀 **Fast & Efficient**: Built-in caching and optimized JSON parsing
- 🛠️ **Easy to Use**: Clean, intuitive API
- 📦 **Zero Dependencies**: Pure Python implementation

## Installation

```bash
pip install mediascan
```

## Quick Start

```python
from mediascan import MediaScanner

# Initialize scanner
scanner = MediaScanner("/path/to/your/json/files")

# Search by title
movie = scanner.find_by_title("Inception")
if movie:
    print(f"Found: {movie.title}")
    print(f"Director: {movie.director}")
    print(f"Rank: {movie.rank}")

# Search by director
nolan_movies = scanner.find_by_director("Nolan")
for movie in nolan_movies:
    print(f"- {movie.title}")

# List all items
all_media = scanner.list_all(limit=10)
for item in all_media:
    print(f"{item.title} ({item.type})")
```

## Command Line Usage

```bash
# Search by title
mediascan search "Inception" /path/to/movies

# Search by director
mediascan director "Nolan" /path/to/movies

# List all items
mediascan list /path/to/movies --limit 10

# Export to CSV
mediascan export /path/to/movies output.csv

# Show statistics
mediascan stats /path/to/movies
```

## JSON File Format

MediaScan expects JSON files with an array of media objects:

```json
[
  {
    "title": "Inception",
    "year": "2010",
    "director": "Christopher Nolan",
    "type": "movie"
  },
  {
    "title": "Breaking Bad",
    "year": "2008",
    "director": "Vince Gilligan",
    "type": "tv",
    "seasons": "5",
    "episodes": "62"
  }
]
```

## API Reference

### MediaScanner

Main class for searching media files.

#### Methods

- `find_by_title(title: str) -> Optional[MediaItem]`
- `find_by_director(director: str) -> List[MediaItem]`
- `list_all(limit: Optional[int] = None) -> List[MediaItem]`
- `get_stats() -> Dict[str, Any]`
- `clear_cache() -> None`

### MediaItem

Base class for all media items.

#### Properties

- `title: str`
- `rank: int`
- `filepath: str`
- `year: str`
- `director: str`
- `type: str`

#### Methods

- `to_dict() -> Dict[str, Any]`

### Subclasses

- `Movie`: Standard movie items
- `TVSeries`: TV series with additional `seasons` and `episodes` properties

## Utilities

```python
from mediascan.utils import format_media_info, export_to_csv

# Format media info as string
info_text = format_media_info(movie)
print(info_text)

# Export to CSV
export_to_csv(all_media, "output.csv")
```

## Error Handling

```python
from mediascan.exceptions import MediaScanError, JSONParseError

try:
    scanner = MediaScanner("/invalid/path")
except MediaScanError as e:
    print(f"Error: {e}")
```

## Development

```bash
# Clone repository
git clone https://github.com/yourusername/mediascan.git
cd mediascan

# Install development dependencies
pip install -e ".[dev]"

# Run tests
pytest

# Run linting
black mediascan/
flake8 mediascan/
mypy mediascan/
```

## License

MIT License - see LICENSE file for details.

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

## Changelog

### 0.1.0
- Initial release
- Basic search functionality
- CLI interface
- CSV export capability
