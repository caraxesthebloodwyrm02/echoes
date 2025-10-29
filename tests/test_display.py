from core.display_utils import safe_symbol, PALETTE

def test_safe_symbol_basic():
    s = safe_symbol('✿')
    assert isinstance(s, str)
    assert len(s) >= 1

def test_palette_keys():
    for k in ("accent", "title", "text", "reset"):
        assert k in PALETTE
