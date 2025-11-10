"""
Example usage of the MediaScan library.
"""

from mediascan import MediaScanner
from mediascan.exceptions import MediaScanError
from mediascan.utils import export_to_csv, format_media_info


def main():
    """Demonstrate MediaScan functionality."""

    # Initialize the scanner
    try:
        scanner = MediaScanner("C:/Users/irfan/Documents")
    except MediaScanError as e:
        print(f"Error initializing scanner: {e}")
        return

    print("🎬 MediaScan Demo")
    print("=" * 50)

    # Example 1: Search by title
    print("\n1. Searching for 'Eternal Sunshine of the Spotless Mind':")
    movie = scanner.find_by_title("Eternal Sunshine of the Spotless Mind")
    if movie:
        print(format_media_info(movie))
    else:
        print("Movie not found")

    # Example 2: Search by director
    print("\n2. Searching for movies by 'Michel Gondry':")
    movies = scanner.find_by_director("Michel Gondry")
    for movie in movies:
        print(f"  - {movie.title} (Rank: {movie.rank})")

    # Example 3: List first 5 items
    print("\n3. First 5 media items:")
    items = scanner.list_all(limit=5)
    for item in items:
        print(f"  {item.rank}. {item.title} ({item.type})")

    # Example 4: Get statistics
    print("\n4. Database statistics:")
    stats = scanner.get_stats()
    for key, value in stats.items():
        print(f"  {key}: {value}")

    # Example 5: Export to CSV
    print("\n5. Exporting all items to CSV:")
    all_items = scanner.list_all()
    if all_items:
        export_to_csv(all_items, "media_export.csv")
        print(f"  Exported {len(all_items)} items to media_export.csv")
    else:
        print("  No items to export")


if __name__ == "__main__":
    main()
