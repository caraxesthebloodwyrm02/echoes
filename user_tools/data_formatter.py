"""
User-defined tool: data_formatter
Description: Format data in various ways
Created: 2025-11-02T09:06:51.698768
"""


def data_formatter(data, format_type="json"):
    if format_type == "json":
        return json.dumps(data, indent=2)
    elif format_type == "csv":
        if isinstance(data, dict):
            return ",".join(data.keys())
        return str(data)
    elif format_type == "summary":
        return f"Data with {len(data)} items"
    else:
        return str(data)
