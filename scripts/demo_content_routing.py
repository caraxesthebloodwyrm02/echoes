# scripts/demo_content_routing.py
from pathlib import Path
import json

# Import highway core (intelligent router)
from app.domains.arts.investlab.hub_investlab.hub.highway import (
    highway,
    DataType,
)

CONTENT_DIR = Path("content")

def main():
    if not CONTENT_DIR.exists():
        print("No content/ directory found.")
        return

    files = [p for p in CONTENT_DIR.iterdir() if p.is_file()]
    if not files:
        print("No files in content/ to route.")
        return

    results = []
    for f in files:
        payload = {
            "file_path": str(f.as_posix()),
            "file_name": f.name,
            "ext": f.suffix.lower(),
            "category": "content",
        }
        # Send as CONTENT to exercise multi-hop routing (entertainment/insights/finance -> media)
        packet_id = highway.send_data(
            source="content_scanner",
            destination="media",
            data_type=DataType.CONTENT,
            payload=payload,
        )
        # Inspect routing history from highway cache
        packet = highway.data_cache.get(packet_id)
        history = packet.routing_history if packet else []
        results.append({
            "file": f.name,
            "packet_id": packet_id,
            "routing_history": history,
        })

    print(json.dumps(results, indent=2))

if __name__ == "__main__":
    main()
