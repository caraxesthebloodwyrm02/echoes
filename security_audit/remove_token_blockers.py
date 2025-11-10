#!/usr/bin/env python3
"""
Emergency Token Blocking Pattern Removal
CRITICAL: Functions that block iteration through token level limiting
"""

import re
from pathlib import Path

def remove_token_blocking_patterns():
    """Remove token blocking patterns that prevent iteration."""
    print("🚨 REMOVING TOKEN BLOCKING PATTERNS...")
    
    # Critical files with token blocking
    critical_files = [
        "ATLAS/ATLAS.py",
        "echoes/config.py", 
        "echoes/core.py"
    ]
    
    echoes_root = Path(__file__).parent.parent
    
    for file_path in critical_files:
        full_path = echoes_root / file_path
        if full_path.exists():
            print(f"\n🔧 Fixing: {file_path}")
            
            try:
                with open(full_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                original_content = content
                
                # CRITICAL FIX 1: Remove DEFAULT_MAX_TOKENS constant
                content = re.sub(r'DEFAULT_MAX_TOKENS\s*=\s*\d+', '# DEFAULT_MAX_TOKENS REMOVED - BLOCKING TOKEN ITERATION', content)
                
                # CRITICAL FIX 2: Remove token blocking logic "opts.max_tokens or DEFAULT_MAX_TOKENS"
                content = re.sub(r'self\.max_tokens\s*=\s*opts\.max_tokens\s*or\s*DEFAULT_MAX_TOKENS', 'self.max_tokens = opts.max_tokens', content)
                content = re.sub(r'self\.max_tokens\s*=\s*max_tokens\s*or\s*\d+', 'self.max_tokens = max_tokens', content)
                
                # CRITICAL FIX 3: Remove Field default for max_tokens
                content = re.sub(r'default_max_tokens:\s*int\s*=\s*Field\([^)]*\)', '# default_max_tokens REMOVED - BLOCKING TOKEN ITERATION', content)
                
                # CRITICAL FIX 4: Remove token override patterns
                content = re.sub(r'max_tokens:\s*int\s*=\s*DEFAULT_MAX_TOKENS', 'max_tokens: int | None = None', content)
                
                if content != original_content:
                    with open(full_path, 'w', encoding='utf-8') as f:
                        f.write(content)
                    print(f"   ✅ Token blocking patterns removed from {file_path}")
                else:
                    print(f"   ℹ️ No changes needed for {file_path}")
                    
            except Exception as e:
                print(f"   ❌ Error fixing {file_path}: {e}")
    
    print("\n✅ Token blocking patterns removed")
    print("🔄 Token iteration now unblocked")
    print("🎯 Users can now iterate through ANY token level without blocking")

if __name__ == "__main__":
    remove_token_blocking_patterns()