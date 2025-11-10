import argparse
import json
import os
import re
import time
from dataclasses import asdict, dataclass, field
from functools import lru_cache
from typing import Any
from urllib.parse import quote_plus

import requests

# OpenAI Integration for web search
try:
    import openai
    from openai import OpenAI

    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False
    openai = None
    OpenAI = None


@dataclass
class MediaItem:
    """Base class for media items (movies or TV series)."""

    title: str
    rank: int
    file: str
    year: str = "N/A"
    director: str = "Unknown"
    type: str = "Movie"
    relevance: float = 0.0  # For search result ranking
    cast: list[str] = field(default_factory=list)
    similar_titles: list[str] = field(default_factory=list)
    plot: str = "N/A"

    def to_dict(self) -> dict[str, Any]:
        """Convert the media item to a dictionary."""
        return asdict(self)


@dataclass
class Movie(MediaItem):
    """Class representing a movie."""

    rating: str = "N/A"
    genre: str = "Unknown"
    runtime: str = "N/A"

    def __post_init__(self):
        self.type = "Movie"


@dataclass
class TVSeries(MediaItem):
    """Class representing a TV series."""

    seasons: str = "N/A"
    episodes: str = "N/A"
    network: str = "Unknown"
    status: str = "Unknown"
    rating: str = "N/A"
    genre: str = "Unknown"

    def __post_init__(self):
        self.type = "TV Series"


class WebSearcher:
    """Class to handle web searches for media."""

    def __init__(self, api_key: str | None = None):
        self.google_api_key = api_key or os.getenv("GOOGLE_API_KEY")
        self.search_engine_id = os.getenv("GOOGLE_SEARCH_ENGINE_ID")
        self.openai_api_key = os.getenv("OPENAI_API_KEY")
        self.omdb_key = os.getenv("OMDB_API_KEY")

        # Initialize OpenAI client if available
        self.openai_client = None
        if OPENAI_AVAILABLE and self.openai_api_key:
            try:
                self.openai_client = OpenAI(api_key=self.openai_api_key)
            except Exception as e:
                print(f"⚠️ Failed to initialize OpenAI client: {e}")

        self.session = requests.Session()
        self.session.headers.update(
            {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
            }
        )
        self.rate_limit = 5  # Max requests per minute
        self.last_request_time = 0

    def _rate_limit(self) -> None:
        """Enforce rate limiting."""
        elapsed = time.time() - self.last_request_time
        if elapsed < 60 / self.rate_limit:
            time.sleep((60 / self.rate_limit) - elapsed)
        self.last_request_time = time.time()

    def search_web(
        self, query: str, media_type: str = "movie", year: int | None = None
    ) -> list[dict[str, Any]]:
        """Search for media on the web."""
        try:
            self._rate_limit()

            # Construct search query
            search_query = query
            if media_type and media_type.lower() != "any":
                search_query += f" {media_type}"
            if year:
                search_query += f" {year}"

            # Try OpenAI web search first if available
            if self.openai_client:
                print("🤖 Using OpenAI web search")
                return self._openai_search(search_query)

            # Try Google Custom Search API second if credentials are available
            if self.google_api_key and self.search_engine_id:
                print("🌐 Using Google Custom Search API")
                return self._google_search(search_query)

            # Fallback to TVMaze API
            print("🌐 Using TVMaze API fallback")
            return self._fallback_search(search_query, media_type)

        except Exception as e:
            print(f"⚠️ Web search error: {e}")
            return []

    def _openai_search(self, query: str) -> list[dict[str, Any]]:
        """
        Search for media metadata using OpenAI's API with fallback handling.

        Args:
            query: Search query string

        Returns:
            List of normalized media items, or empty list on failure
        """
        if not self.openai_client:
            return []

        try:
            model = self._select_openai_model()
            if not model:
                return []

            response = self._query_openai(model, query)
            if not response:
                return []

            return self._parse_openai_response(response, query)

        except Exception as e:
            print(f"⚠️ OpenAI search failed: {e}")
            return []

    def _select_openai_model(self) -> str | None:
        """Select the best available OpenAI model for search."""
        search_models = [
            "gpt-4o-search-preview",
            "gpt-4o",
            "gpt-4-turbo-preview",
            "gpt-4",
        ]

        for model in search_models:
            try:
                # Simple validation that the model is available
                self.openai_client.models.retrieve(model)
                return model
            except Exception:
                continue
        return None

    def _query_openai(self, model: str, query: str) -> str | None:
        """Execute the OpenAI API query with rate limiting."""
        try:
            self._rate_limit()
            response = self.openai_client.chat.completions.create(
                model=model,
                messages=[
                    {
                        "role": "user",
                        "content": f"""Search for media matching: {query}
                    Return results as a JSON array with fields: 
                    title, year, type, director, rating, genre, runtime, 
                    network (TV only), cast, similar_titles, plot""",
                    }
                ],
                max_tokens=1000,
                temperature=0.3,
            )
            return response.choices[0].message.content
        except Exception as e:
            print(f"⚠️ OpenAI API error: {e}")
            return None

    def _parse_openai_response(
        self, response: str, original_query: str
    ) -> list[dict[str, Any]]:
        """Parse and validate the OpenAI API response."""
        try:
            # Try to extract JSON from markdown code blocks
            json_match = re.search(r"```(?:json)?\n(.*?)\n```", response, re.DOTALL)
            if json_match:
                results = json.loads(json_match.group(1))
            else:
                # Fallback to direct JSON parse
                results = json.loads(response)

            if not isinstance(results, list):
                results = [results]

            return self._normalize_openai_results(results, original_query)

        except json.JSONDecodeError:
            return self._parse_openai_text_response(response, original_query)

    def _normalize_openai_results(self, results: list[dict], query: str) -> list[dict]:
        """Normalize OpenAI results to a consistent format."""
        normalized = []
        for item in results[:5]:  # Limit to top 5 results
            if not isinstance(item, dict):
                continue

            normalized_item = {
                "title": item.get("title", query.split("(")[0].strip()),
                "year": str(item.get("year", "N/A")),
                "type": (
                    "TV Series"
                    if str(item.get("type", "")).lower() in ("tv", "tv series", "show")
                    else "Movie"
                ),
                "director": str(
                    item.get("director") or item.get("showrunner") or "Unknown"
                ),
                "rating": str(item.get("rating", "N/A")),
                "genre": str(item.get("genre", "Unknown")),
                "runtime": str(item.get("runtime", "N/A")),
                "network": str(
                    item.get("network", "Unknown")
                    if item.get("type") == "TV Series"
                    else "N/A"
                ),
                "cast": self._normalize_list(item.get("cast", [])),
                "similar_titles": self._normalize_list(item.get("similar_titles", [])),
                "plot": str(item.get("plot", "N/A") or "N/A"),
                "source": "OpenAI Search",
            }
            normalized.append(normalized_item)

        return normalized or self._parse_openai_text_response(str(results), query)

    def _normalize_list(self, value: str | list[str] | None) -> list[str]:
        """Convert string or list input to a clean list of strings."""
        if isinstance(value, str):
            return [v.strip() for v in re.split(r"[;,\n]", value) if v.strip()]
        return [str(v).strip() for v in value if str(v).strip()] if value else []

    def _parse_openai_text_response(
        self, content: str, original_query: str
    ) -> list[dict[str, Any]]:
        """Parse text response from OpenAI when JSON fails."""
        # Simple text parsing for basic information
        lines = content.split("\n")
        results = []

        for line in lines[:5]:  # Limit to 5 results
            if any(
                keyword in line.lower()
                for keyword in ["movie", "film", "tv", "series", "show"]
            ):
                # Extract basic info from the line
                year_match = re.search(r"\b(19|20)\d{2}\b", line)
                year = year_match.group(0) if year_match else "N/A"

                media_type = "Movie"
                if any(tv_word in line.lower() for tv_word in ["tv", "series", "show"]):
                    media_type = "TV Series"

                results.append(
                    {
                        "title": original_query,
                        "year": year,
                        "type": media_type,
                        "source": "OpenAI Search",
                        "director": "Unknown",
                        "rating": "N/A",
                        "genre": "Unknown",
                        "runtime": "N/A",
                        "network": "Unknown",
                        "cast": [],
                        "similar_titles": [],
                        "plot": line.strip(),
                    }
                )

        if not results:
            # Return at least one result with basic info
            results.append(
                {
                    "title": original_query,
                    "year": "N/A",
                    "type": "Movie",
                    "source": "OpenAI Search",
                    "director": "Unknown",
                    "rating": "N/A",
                    "genre": "Unknown",
                    "runtime": "N/A",
                    "network": "Unknown",
                    "cast": [],
                    "similar_titles": [],
                    "plot": "N/A",
                }
            )

        return results

    def _google_search(self, query: str) -> list[dict[str, Any]]:
        """Search using Google Custom Search API."""
        url = "https://www.googleapis.com/customsearch/v1"
        params = {
            "q": query,
            "key": self.google_api_key,
            "cx": self.search_engine_id,
            "num": 5,  # Limit to 5 results
        }

        response = self.session.get(url, params=params, timeout=10)
        response.raise_for_status()
        data = response.json()

        results = []
        for item in data.get("items", []):
            # Extract metadata from title and snippet
            title = item.get("title", "")
            snippet = item.get("snippet", "")

            # Try to extract year from title (common pattern: "Title (Year)")
            year_match = re.search(r"\((\d{4})\)", title)
            year = year_match.group(1) if year_match else "N/A"

            # Try to determine type from title/snippet
            media_type = "Movie"  # Default
            if (
                "tv" in title.lower()
                or "series" in title.lower()
                or "season" in snippet.lower()
            ):
                media_type = "TV Series"

            # Extract rating if mentioned (e.g., "8.5/10")
            rating_match = re.search(r"(\d+(?:\.\d+)?)/10", snippet)
            rating = rating_match.group(1) if rating_match else "N/A"

            results.append(
                {
                    "title": re.sub(
                        r"\s*\(\d{4}\).*", "", title
                    ),  # Remove year from title
                    "year": year,
                    "type": media_type,
                    "source": "Google Search",
                    "director": "Unknown",
                    "rating": rating,
                    "genre": "Unknown",
                    "runtime": "N/A",
                    "link": item.get("link", ""),
                    "snippet": snippet,
                }
            )
        return results

    def _fallback_search(self, query: str, media_type: str) -> list[dict[str, Any]]:
        """Fallback search using public APIs."""
        if media_type.lower() == "movie":
            return self._search_movies(query)
        elif media_type.lower() == "tv":
            return self._search_tv_shows(query)
        else:
            # For 'any' type, try both movies and TV shows
            movie_results = self._search_movies(query)
            tv_results = self._search_tv_shows(query)
            return movie_results + tv_results

    def _search_movies(self, query: str) -> list[dict[str, Any]]:
        """Search for movies using TVMaze API (as fallback since OMDb demo keys don't work)."""
        try:
            # Use TVMaze for movies too (it has movie data)
            url = f"https://api.tvmaze.com/search/shows?q={quote_plus(query)}"
            response = self.session.get(url, timeout=10)
            response.raise_for_status()
            shows = response.json()

            results = []
            for show in shows[:5]:  # Limit to 5 results
                show_data = show.get("show", {})
                if show_data:
                    # Filter for movies if possible, or include all as general media
                    if not show_data.get("type") or show_data.get("type") == "Scripted":
                        # Treat as movie/general media
                        network = show_data.get("network", {})

                        results.append(
                            {
                                "title": show_data.get("name", "Unknown"),
                                "year": (
                                    show_data.get("premiered", "")[:4]
                                    if show_data.get("premiered")
                                    else "N/A"
                                ),
                                "type": "Movie",
                                "source": "TVMaze",
                                "director": "Unknown",  # TVMaze doesn't provide director info
                                "rating": (
                                    str(
                                        show_data.get("rating", {}).get(
                                            "average", "N/A"
                                        )
                                    )
                                    if show_data.get("rating")
                                    else "N/A"
                                ),
                                "genre": (
                                    ", ".join(
                                        [
                                            g.get("name", "Unknown")
                                            for g in show_data.get("genres", [])[:3]
                                        ]
                                    )
                                    if show_data.get("genres")
                                    else "Unknown"
                                ),
                                "runtime": (
                                    f"{show_data.get('runtime', 0)} min"
                                    if show_data.get("runtime")
                                    else "N/A"
                                ),
                            }
                        )
            return results

        except Exception:
            # Return mock data for testing
            return [
                {
                    "title": f"{query} (Demo - Web Search)",
                    "year": "2023",
                    "type": "Movie",
                    "source": "Demo",
                    "director": "Demo Director",
                    "rating": "8.0",
                    "genre": "Drama, Sci-Fi",
                    "runtime": "120 min",
                }
            ]

    def _search_tv_shows(self, query: str) -> list[dict[str, Any]]:
        """Search for TV shows using TVMaze API."""
        try:
            url = f"https://api.tvmaze.com/search/shows?q={quote_plus(query)}"
            response = self.session.get(url, timeout=10)
            response.raise_for_status()
            shows = response.json()

            results = []
            for show in shows[:5]:  # Limit to 5 results
                show_data = show.get("show", {})
                if show_data:
                    # Get detailed show information
                    show_id = show_data.get("id")
                    network = show_data.get("network", {})

                    # Try to get episode count
                    episodes = "N/A"
                    if show_id:
                        try:
                            episodes_url = (
                                f"https://api.tvmaze.com/shows/{show_id}/episodes"
                            )
                            episodes_response = self.session.get(
                                episodes_url, timeout=5
                            )
                            if episodes_response.status_code == 200:
                                episodes_list = episodes_response.json()
                                episodes = (
                                    str(len(episodes_list)) if episodes_list else "N/A"
                                )
                        except:
                            pass

                    results.append(
                        {
                            "title": show_data.get("name", "Unknown"),
                            "year": (
                                show_data.get("premiered", "")[:4]
                                if show_data.get("premiered")
                                else "N/A"
                            ),
                            "type": "TV Series",
                            "seasons": str(show_data.get("seasons", "N/A")),
                            "episodes": episodes,
                            "network": (
                                network.get("name", "Unknown") if network else "Unknown"
                            ),
                            "source": "TVMaze",
                            "genre": (
                                ", ".join(
                                    [
                                        g.get("name", "Unknown")
                                        for g in show_data.get("genres", [])[:3]
                                    ]
                                )
                                if show_data.get("genres")
                                else "Unknown"
                            ),
                            "rating": (
                                show_data.get("rating", {}).get("average", "N/A")
                                if show_data.get("rating")
                                else "N/A"
                            ),
                            "status": show_data.get("status", "Unknown"),
                        }
                    )
            return results

        except Exception:
            return []


class MediaSearcher:
    def __init__(self, search_dir: str):
        self.search_dir = search_dir
        self._file_cache = {}  # Cache for parsed JSON files
        self._last_modified = {}  # Track file modification times
        self._index = self._build_index()  # In-memory search index
        self.web_searcher = WebSearcher()  # Add web search capability

    def validate_json_file(self, filepath: str) -> bool:
        """Validate if a file contains valid JSON."""
        try:
            with open(filepath, encoding="utf-8") as f:
                json.load(f)
            return True
        except (json.JSONDecodeError, UnicodeDecodeError, PermissionError, OSError):
            return False

    def _build_index(self) -> dict[str, list[dict[str, Any]]]:
        """Build an in-memory search index for faster lookups."""
        index = {}
        skip_dirs = [
            ".root_backup",
            "node_modules",
            "__pycache__",
            ".git",
            "venv",
            ".git",
            ".svn",
            "__pycache__",
            "*.pyc",
            "*.log",
            ".DS_Store",
            ".idea",
            ".vscode",
            ".agent",
            "node_modules",
            "workspace",
            "virtualenv",
            "venv",
            ".venv",
            ".env",
            ".emacs.d",
            ".ssh",
            ".aws",
            ".docker",
            ".kube",
        ]
        skip_files = [
            "backup",
            "temp",
            "tmp",
            "test",
            "spec",
            "mock",
            "sample",
            "example",
        ]

        for root, _, files in os.walk(self.search_dir):
            for file in files:
                if not file.endswith(".json"):
                    continue

                filepath = os.path.join(root, file)

                # Skip known problematic directories
                if any(
                    skip_dir in filepath.replace("\\", "/").split("/")
                    for skip_dir in skip_dirs
                ):
                    continue

                # Skip known problematic files
                if any(skip_file in filepath.lower() for skip_file in skip_files):
                    continue

                try:
                    # Skip files that are too large (>5MB)
                    if os.path.getsize(filepath) > 5 * 1024 * 1024:  # 5MB
                        print(f"⚠️ Skipping large file: {filepath}")
                        continue

                    # Validate JSON before processing
                    if not self.validate_json_file(filepath):
                        print(f"⚠️ Skipping invalid JSON: {filepath}")
                        continue

                    data = self._load_json_file(filepath)
                    if data:
                        index[filepath] = data
                except Exception as e:
                    print(f"⚠️ Error processing {filepath}: {e}")
                    continue

        return index

    @lru_cache(maxsize=128)
    def _load_json_file(self, filepath: str) -> list[dict[str, Any]] | None:
        """Load and cache JSON files with LRU caching and robust error handling."""
        try:
            with open(filepath, encoding="utf-8") as f:
                try:
                    content = f.read().strip()
                    if not content:
                        print(f"⚠️ Empty file: {filepath}")
                        return None

                    # Try to parse as JSON
                    data = json.loads(content)
                    if not isinstance(data, list):
                        if isinstance(data, dict):
                            data = [data]  # Convert single dict to list of one dict
                        else:
                            print(f"⚠️ Expected JSON array or object in {filepath}")
                            return None
                    return data

                except json.JSONDecodeError as e:
                    # Try to recover from common JSON issues
                    try:
                        # Try to fix common JSON issues
                        content = content.replace("'", '"')  # Fix single quotes
                        content = re.sub(
                            r",\s*]", "]", content
                        )  # Remove trailing commas
                        content = re.sub(
                            r",\s*}", "}", content
                        )  # Remove trailing commas
                        content = re.sub(
                            r"//.*$", "", content, flags=re.MULTILINE
                        )  # Remove comments
                        data = json.loads(content)
                        if not isinstance(data, list):
                            data = [data] if isinstance(data, dict) else None
                        if data:
                            print(f"⚠️ Fixed JSON in {filepath} (was malformed)")
                            return data
                    except:
                        pass

                    print(f"⚠️ Invalid JSON in {filepath}: {e}")
                    return None

        except (PermissionError, OSError) as e:
            print(f"⚠️ Error reading {filepath}: {e}")
        except Exception as e:
            print(f"⚠️ Unexpected error with {filepath}: {e}")
        return None

    def _calculate_relevance(
        self, item: dict[str, Any], query: str, year: str | None = None
    ) -> float:
        """Calculate relevance score for search results."""
        score = 0.0
        title = item.get("title", "").lower()
        query = query.lower()

        # Title match (exact match scores highest)
        if query == title:
            score += 100
        elif query in title:
            # Partial match based on position and completeness
            if title.startswith(query):
                score += 60
            else:
                score += 40
        elif any(word in title for word in query.split() if len(word) > 2):
            # Word-level matching for longer queries
            matching_words = sum(
                1 for word in query.split() if len(word) > 2 and word in title
            )
            query_words = len([w for w in query.split() if len(w) > 2])
            if query_words > 0:
                score += (matching_words / query_words) * 30

        # Year match bonus
        if year and str(item.get("year")) == str(year):
            score += 30

        # Type bonus (prefer exact matches)
        if item.get("type", "").lower() in ["movie", "tv series"]:
            score += 10

        # Quality bonus for web results with real data
        if item.get("director") and item.get("director") != "Unknown":
            score += 15
        if item.get("rating") and item.get("rating") != "N/A":
            score += 10

        return score

    def search_media(
        self,
        query: str,
        media_type: str | None = None,
        year: str | int | None = None,
        min_rating: float = 0.0,
        limit: int = 10,
        use_web: bool = True,
        web_only: bool = False,
    ) -> list[MediaItem]:
        """
        Search for media items with advanced filtering and ranking.

        Args:
            query: Search query
            media_type: Filter by type ('movie' or 'tv')
            year: Filter by release year
            min_rating: Minimum rating (0-10)
            limit: Maximum number of results to return
            use_web: Whether to include web search results

        Returns:
            List of matching MediaItem objects, sorted by relevance
        """
        local_results = []
        web_results = []
        year = str(year) if year is not None else None

        # Skip local search if web_only is True
        if not web_only:
            local_results = []
            for filepath, file_data in self._index.items():
                if filepath not in self._file_cache:
                    continue

                for item in self._file_cache[filepath]:
                    if not self._matches_query(item, query):
                        continue

                    if (
                        media_type
                        and item.get("type", "").lower() != media_type.lower()
                    ):
                        continue

                    if year and str(item.get("year")) != str(year):
                        continue

                    relevance = self._calculate_relevance(item, query, year)
                    if relevance < min_rating * 10:
                        continue

                    media_item = self._create_media_item(item, filepath)
                    if media_item:
                        media_item.relevance = relevance
                        local_results.append(media_item)
        else:
            local_results = []

        # Always include web search if explicitly requested or if local results are sparse
        if use_web and (not local_results or len(local_results) < 5 or web_only):
            try:
                web_items = self.web_searcher.search_web(
                    query, media_type or "any", year
                )
                for i, item in enumerate(web_items, 1):
                    # Calculate relevance for web results
                    web_relevance = self._calculate_relevance(item, query, year)
                    # Normalize cast and similar titles to lists
                    cast = item.get("cast", [])
                    if isinstance(cast, str):
                        cast = [
                            member.strip()
                            for member in re.split(r"[;,\n]", cast)
                            if member.strip()
                        ]

                    similar = item.get("similar_titles", item.get("similar", []))
                    if isinstance(similar, str):
                        similar = [
                            title.strip()
                            for title in re.split(r"[;,\n]", similar)
                            if title.strip()
                        ]

                    media_dict = {
                        "title": item.get("title", "Unknown"),
                        "rank": i + len(local_results),
                        "year": item.get("year", "N/A"),
                        "type": item.get("type", "Movie"),
                        "director": item.get("director", "Unknown"),
                        "rating": item.get("rating", "N/A"),
                        "genre": item.get("genre", "Unknown"),
                        "runtime": item.get("runtime", "N/A"),
                        "network": item.get("network", "Unknown"),
                        "seasons": item.get("seasons", "N/A"),
                        "episodes": item.get("episodes", "N/A"),
                        "status": item.get("status", "Unknown"),
                        "cast": cast,
                        "similar_titles": similar,
                        "plot": item.get("plot", item.get("snippet", "N/A")),
                    }

                    source = item.get("source", "web")
                    media_obj = self._create_media_item(media_dict, f"web:{source}")
                    if media_obj:
                        media_obj.relevance = web_relevance
                        web_results.append(media_obj)
            except Exception as e:
                print(f"⚠️ Web search failed: {e}")

        # Combine and sort results
        all_results = local_results + web_results
        all_results.sort(key=lambda x: x.relevance, reverse=True)
        return all_results[:limit]

    def _create_media_item(
        self, item: dict[str, Any], filepath: str
    ) -> MediaItem | None:
        """
        Create a strongly-typed MediaItem (Movie or TVSeries) from raw dicts.

        Args:
            item: Raw item dictionary, potentially aggregated from local files or
                  web providers (OpenAI, Google, TVMaze). Missing fields are
                  normalized with safe defaults, and list-like fields are
                  coerced to lists.
            filepath: Source identifier for the item. For web results this is a
                      synthetic value like 'web:OpenAI Search'; for local files
                      this is an absolute path.

        Returns:
            Movie or TVSeries instance with normalized fields and no side effects.
            Returns None if normalization fails unexpectedly.
        """
        try:
            # Normalize common metadata
            cast = item.get("cast", [])
            if isinstance(cast, str):
                cast = [
                    member.strip()
                    for member in re.split(r"[;,\n]", cast)
                    if member.strip()
                ]

            similar = item.get("similar_titles", [])
            if isinstance(similar, str):
                similar = [
                    title.strip()
                    for title in re.split(r"[;,\n]", similar)
                    if title.strip()
                ]

            common_fields = {
                "title": item.get("title", "Unknown"),
                "rank": item.get("rank", 0),
                "file": filepath,
                "year": str(item.get("year", "N/A")),  # Ensure year is a string
                "director": item.get("director", "Unknown"),
                "cast": cast,
                "similar_titles": similar,
                "plot": item.get("plot", "N/A"),
            }

            media_type = str(item.get("type", item.get("media_type", "Movie"))).lower()

            if media_type in ("tv", "tv series", "series") or "seasons" in item:
                return TVSeries(
                    **common_fields,
                    seasons=str(item.get("seasons", "N/A")),
                    episodes=str(item.get("episodes", "N/A")),
                    network=item.get("network", "Unknown"),
                    status=item.get("status", "Unknown"),
                    rating=str(item.get("rating", "N/A")),
                    genre=item.get("genre", "Unknown"),
                )
            else:
                return Movie(
                    **common_fields,
                    rating=str(item.get("rating", "N/A")),
                    genre=item.get("genre", "Unknown"),
                    runtime=str(item.get("runtime", "N/A")),
                )
        except Exception as e:
            print(f"⚠️ Error creating media item: {e}")
            return None

    def rebuild_index(self) -> None:
        """Rebuild the search index (useful after file changes)."""
        self._index = self._build_index()
        print(f"🔄 Search index rebuilt with {len(self._index)} files")


def print_search_results(results: list[MediaItem], query: str) -> None:
    """Print formatted search results with enhanced media information."""
    if not results:
        print(f"❌ No results found for: {query}")
        print(
            "💡 Tip: Try 'Web Search' (option 3) for comprehensive movie/TV database results"
        )
        return

    print(f"\n🔍 Search Results for: {query}")
    print("=" * 80)

    for i, item in enumerate(results, 1):
        info = item.to_dict()

        # Highlight web results with better formatting
        if "web:" in info["file"]:
            print(f"\n{i}. 🎬 {info['title']} ({info['type']}) 🌐")
        else:
            print(f"\n{i}. 🎬 {info['title']} ({info['type']})")

        print(f"   ⭐ Relevance: {info['relevance']:.1f}/100")
        print(f"   📅 Year: {info['year']}")

        # Display plot summary if available
        if hasattr(item, "plot") and item.plot and item.plot != "N/A":
            print(f"\n   📜 {item.plot}")

        if info["type"] == "TV Series":
            print(f"\n   📺 Seasons: {info.get('seasons', 'N/A')}")
            print(f"   🎞️ Episodes: {info.get('episodes', 'N/A')}")
            if info.get("network", "Unknown") != "Unknown":
                print(f"   📡 Network: {info['network']}")
            if info.get("status", "Unknown") != "Unknown":
                print(f"   📺 Status: {info['status']}")

        # Display cast members if available
        if hasattr(item, "cast") and item.cast:
            print(
                f"\n   👥 Cast: {', '.join(item.cast[:5])}"
                + ("..." if len(item.cast) > 5 else "")
            )

        # Display similar titles if available
        if hasattr(item, "similar_titles") and item.similar_titles:
            print(f"   🔄 Similar to: {', '.join(item.similar_titles[:3])}")

        print(f"\n   🎥 Director: {info['director']}")

        # Show additional details if available from web search
        if "web:" in info["file"]:
            if hasattr(item, "rating") and item.rating != "N/A":
                print(f"   ⭐ Rating: {item.rating}/10")
            if hasattr(item, "genre") and item.genre != "Unknown":
                print(f"   🎭 Genre: {item.genre}")
            if hasattr(item, "runtime") and item.runtime != "N/A":
                print(f"   ⏱️ Runtime: {item.runtime}")

        print(f"\n   📁 Source: {info['file']}")
        print("-" * 80)


def main():
    # Parse command line arguments
    parser = argparse.ArgumentParser(
        description="Media Search - Find movies and TV shows",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python find.py "Her"                    # Search for "Her"
  python find.py "Eternal Sunshine"      # Search with web results
  python find.py "The Office" --year 2005 # Filter by year
  python find.py "Breaking Bad" --type tv # TV series only
  python find.py --rebuild                # Rebuild search index
  python find.py --local-only             # Local files only
        """,
    )

    parser.add_argument("query", nargs="?", help="Search query for movies/TV shows")

    parser.add_argument("--year", "-y", type=int, help="Filter by release year")

    parser.add_argument(
        "--type",
        "-t",
        choices=["movie", "tv", "any"],
        default="any",
        help="Filter by media type (default: any)",
    )

    parser.add_argument(
        "--local-only",
        "-l",
        action="store_true",
        help="Search local files only (no web search)",
    )

    parser.add_argument(
        "--web-only", "-w", action="store_true", help="Search web only (no local files)"
    )

    parser.add_argument(
        "--rebuild", "-r", action="store_true", help="Rebuild search index and exit"
    )

    parser.add_argument(
        "--interactive", "-i", action="store_true", help="Start in interactive mode"
    )

    parser.add_argument(
        "--limit", type=int, default=10, help="Maximum number of results (default: 10)"
    )

    args = parser.parse_args()

    # Initialize searcher
    search_directory = "e:/Projects/Echoes"
    searcher = MediaSearcher(search_directory)

    # Handle rebuild command
    if args.rebuild:
        print("🔄 Rebuilding search index...")
        searcher.rebuild_index()
        return

    # Interactive mode
    if args.interactive or not args.query:
        interactive_mode(searcher)
        return

    # Direct search mode
    print(f"\n🔍 Searching for: {args.query}")
    if args.year:
        print(f"📅 Year: {args.year}")
    if args.type != "any":
        print(f"🎬 Type: {args.type}")

    use_web = not args.local_only
    if args.web_only:
        use_web = True

    start_time = time.time()
    results = searcher.search_media(
        query=args.query,
        media_type=args.type if args.type != "any" else None,
        year=args.year,
        limit=args.limit,
        use_web=use_web,
        web_only=args.web_only,
    )
    search_time = time.time() - start_time

    print_search_results(results, args.query)
    print(f"\n⏱️  Found {len(results)} results in {search_time:.2f} seconds")

    # Show details for first result if available
    if results:
        print("\n🎬 Press Enter to see details for top result, or 'q' to quit: ", end="")
        choice = input().strip().lower()
        if choice != "q":
            show_detailed_view(results[0])


def interactive_mode(searcher: MediaSearcher) -> None:
    """Interactive mode with menu options."""
    print("\n🎬 Welcome to Media Search!")
    print("💡 Use --help for command line options")

    while True:
        print("\n🎥 Media Search - Interactive Mode")
        print("=" * 40)
        print("1. Search Media")
        print("2. Filter by Year")
        print("3. 🌐 Web Search Only")
        print("4. Rebuild Index")
        print("5. Exit")
        choice = input("Select option (1-5): ").strip()

        if choice == "5":
            break

        if choice in ("1", "2", "3"):
            query = input("Enter search query: ").strip()
            year = None
            use_web = choice == "3"

            if choice == "2":
                year = input("Enter year (or leave blank): ").strip()
                if not year:
                    year = None

            start_time = time.time()
            results = searcher.search_media(query=query, year=year, use_web=use_web)
            search_time = time.time() - start_time

            if use_web:
                print("\n🌐 Web Search Results:")
            else:
                print("\n📁 Local File Search Results:")

            print_search_results(results, query)
            print(f"\n⏱️  Found {len(results)} results in {search_time:.2f} seconds")

            if results:
                print("\n🎬 View details or (q)uit: ", end="")
                selection = input().strip().lower()

                if selection != "q" and selection.isdigit():
                    idx = int(selection) - 1
                    if 0 <= idx < len(results):
                        show_detailed_view(results[idx])

        elif choice == "4":
            searcher.rebuild_index()


def show_detailed_view(item: MediaItem) -> None:
    """Show detailed view of a media item."""
    print("\n" + "=" * 80)
    print(f"🎬 {item.title} ({item.type})")
    print("=" * 80)
    print(f"📅 Year: {item.year}")
    print(f"🎥 Director: {item.director}")

    if hasattr(item, "seasons"):
        print(f"📺 Seasons: {item.seasons}")
        print(f"🎞️ Episodes: {item.episodes}")
        if hasattr(item, "network"):
            print(f"📡 Network: {item.network}")
        if hasattr(item, "status"):
            print(f"📺 Status: {item.status}")

    # Show additional web search details
    if "web:" in item.file:
        if hasattr(item, "rating"):
            print(f"⭐ Rating: {item.rating}/10")
        if hasattr(item, "genre"):
            print(f"🎭 Genre: {item.genre}")
        if hasattr(item, "runtime"):
            print(f"⏱️ Runtime: {item.runtime}")

    print(f"📁 Source: {item.file}")
    print("=" * 80)


if __name__ == "__main__":
    main()
