import sys

sys.path.append("e:/Projects/Echoes")

from find import WebSearcher

# Test web search directly
searcher = WebSearcher()
print("Testing web search...")
results = searcher._search_movies("Office")
print(f"Found {len(results)} results:")
for result in results:
    print(f"- {result}")
