"""
Command line interface for MediaScan.
"""

import argparse
import sys

from .core import MediaScanner
from .exceptions import MediaScanError
from .utils import export_to_csv, format_media_info


def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        description="Search for media items in JSON files",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  mediascan search "Inception" /path/to/movies
  mediascan director "Nolan" /path/to/movies
  mediascan list /path/to/movies --limit 10
  mediascan export /path/to/movies output.csv
        """,
    )

    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # Search command
    search_parser = subparsers.add_parser("search", help="Search by title")
    search_parser.add_argument("title", help="Title to search for")
    search_parser.add_argument("directory", help="Directory to search in")

    # Director command
    director_parser = subparsers.add_parser("director", help="Search by director")
    director_parser.add_argument("director", help="Director name to search for")
    director_parser.add_argument("directory", help="Directory to search in")

    # List command
    list_parser = subparsers.add_parser("list", help="List all media items")
    list_parser.add_argument("directory", help="Directory to search in")
    list_parser.add_argument(
        "--limit", type=int, help="Maximum number of items to show"
    )

    # Export command
    export_parser = subparsers.add_parser("export", help="Export to CSV")
    export_parser.add_argument("directory", help="Directory to search in")
    export_parser.add_argument("output", help="Output CSV file")

    # Stats command
    stats_parser = subparsers.add_parser("stats", help="Show database statistics")
    stats_parser.add_argument("directory", help="Directory to analyze")

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        sys.exit(1)

    try:
        scanner = MediaScanner(args.directory)

        if args.command == "search":
            result = scanner.find_by_title(args.title)
            if result:
                print(format_media_info(result))
            else:
                print(f"No media found with title containing: {args.title}")
                sys.exit(1)

        elif args.command == "director":
            results = scanner.find_by_director(args.director)
            if results:
                print(f"Found {len(results)} media items by {args.director}:")
                for item in results:
                    print(f"  - {item.title} (Rank: {item.rank})")
            else:
                print(f"No media found by director: {args.director}")
                sys.exit(1)

        elif args.command == "list":
            results = scanner.list_all(limit=args.limit)
            if results:
                print(f"Found {len(results)} media items:")
                for item in results:
                    print(f"  - {item.title} ({item.type}, Rank: {item.rank})")
            else:
                print("No media items found")
                sys.exit(1)

        elif args.command == "export":
            results = scanner.list_all()
            export_to_csv(results, args.output)
            print(f"Exported {len(results)} items to {args.output}")

        elif args.command == "stats":
            stats = scanner.get_stats()
            print("Media Database Statistics:")
            print(f"  JSON files: {stats['json_files']}")
            print(f"  Total items: {stats['total_items']}")
            print(f"  Search directory: {stats['search_directory']}")
            print(f"  Cache size: {stats['cache_size']}")

    except MediaScanError as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)
    except KeyboardInterrupt:
        print("\nOperation cancelled by user", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
