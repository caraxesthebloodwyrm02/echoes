PALETTE = {
    "accent": "",
    "title": "",
    "text": "",
    "reset": "",
}


def safe_symbol(symbol: str) -> str:
    if not symbol:
        return "?"
    return str(symbol)
