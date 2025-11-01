# Unicode and Emoji Handling Rules
## Preventing Encoding Issues in Python Scripts

### Problem
Unicode characters (especially emojis) can cause encoding issues when running Python scripts on Windows systems, leading to errors like:
```
UnicodeEncodeError: 'charmap' codec can't encode character '\U0001f680' in position 125: character maps to <undefined>
```

### Solution
Always use ASCII-only characters in production scripts and replace Unicode characters with descriptive ASCII equivalents.

### Common Unicode Character Replacements

#### Status Indicators
- ✅ → `[PASS]` or `[SUCCESS]`
- ❌ → `[FAIL]` or `[ERROR]`
- ⚠️ → `[WARN]` or `[WARNING]`
- ✓ → `[OK]` or `[DONE]`
- ✗ → `[ERROR]` or `[FAILED]`

#### Emojis and Symbols
- 🚀 → `[DEPLOY]` or `[LAUNCH]`
- 🎯 → `[TARGET]` or `[GOAL]`
- 🎉 → `[SUCCESS]` or `[CELEBRATION]`
- 💡 → `[IDEA]` or `[TIP]`
- 🏆 → `[WIN]` or `[ACHIEVEMENT]`
- 📊 → `[STATS]` or `[METRICS]`
- 📝 → `[NOTE]` or `[LOG]`
- 🔍 → `[SEARCH]` or `[FIND]`
- 🔧 → `[TOOL]` or `[CONFIG]`
- ⚙️ → `[CONFIG]` or `[SETTINGS]`
- 📁 → `[DIR]` or `[FOLDER]`
- 📄 → `[FILE]` or `[DOCUMENT]`
- 🧪 → `[TEST]` or `[EXPERIMENT]`
- 📋 → `[CLIP]` or `[COPY]`

#### Progress Indicators (Spinner Characters)
- ⠋ → `[1]` or `[-]`
- ⠙ → `[2]` or `[\]`
- ⠹ → `[3]` or `[|]`
- ⠸ → `[4]` or `[/]`
- ⠼ → `[5]` or `[-]`
- ⠴ → `[6]` or `[\]`
- ⠦ → `[7]` or `[|]`
- ⠧ → `[8]` or `[/]`
- ⠇ → `[9]` or `[-]`
- ⠏ → `[0]` or `[\]`

### Best Practices

#### 1. Code Standards
```python
# GOOD: ASCII-only
print("[SUCCESS] Deployment completed!")

# BAD: Unicode characters
print("✅ Deployment completed!")
```

#### 2. File Handling
```python
# GOOD: Explicit UTF-8 encoding
with open('file.py', 'r', encoding='utf-8') as f:
    content = f.read()

# BAD: Default encoding (may fail on Windows)
with open('file.py', 'r') as f:
    content = f.read()
```

#### 3. Validation
```python
# Use validation functions before deployment
if not validate_no_unicode(content, filename):
    content = sanitize_unicode_content(content)
```

#### 4. Testing
```bash
# Test encoding compatibility
python3 -c "open('script.py').read()"

# Check for Unicode characters
python3 -c "
with open('script.py', 'r', encoding='utf-8') as f:
    content = f.read()
unicode_chars = [c for c in content if ord(c) > 127]
print(f'Found {len(unicode_chars)} Unicode characters')
"
```

### Implementation

#### Validation Function
```python
def validate_no_unicode(content: str, filename: str = "file") -> bool:
    """Validate that content contains no problematic Unicode characters"""
    unicode_chars = []
    for i, char in enumerate(content):
        if ord(char) > 127:
            unicode_chars.append((i, char, f"U+{ord(char):04X}"))

    if unicode_chars:
        print(f"[WARN] Found {len(unicode_chars)} Unicode characters in {filename}")
        return False
    return True
```

#### Sanitization Function
```python
def sanitize_unicode_content(content: str) -> str:
    """Replace Unicode characters with ASCII equivalents"""
    replacements = {
        '✅': '[PASS]',
        '❌': '[FAIL]',
        '⚠️': '[WARN]',
        '🚀': '[DEPLOY]',
        # ... add more as needed
    }

    for unicode_char, ascii_equiv in replacements.items():
        content = content.replace(unicode_char, ascii_equiv)

    return content
```

### Automated Tools

#### Pre-commit Hook (Python)
```python
# .pre-commit-config.yaml
repos:
  - repo: local
    hooks:
      - id: unicode-check
        name: Check for Unicode characters
        entry: python3 -c "
import sys
content = open(sys.argv[1]).read()
unicode_chars = [c for c in content if ord(c) > 127]
if unicode_chars:
    print(f'Found {len(unicode_chars)} Unicode characters in {sys.argv[1]}')
    sys.exit(1)
"
        language: system
        files: \.py$
```

#### GitHub Actions Check
```yaml
# .github/workflows/unicode-check.yml
name: Unicode Check
on: [push, pull_request]

jobs:
  unicode-check:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Check for Unicode characters
        run: |
          find . -name "*.py" -exec python3 -c "
          import sys
          content = open(sys.argv[1]).read()
          unicode_chars = [c for c in content if ord(c) > 127]
          if unicode_chars:
              print(f'Found {len(unicode_chars)} Unicode characters in {sys.argv[1]}')
              sys.exit(1)
          " {} \;
```

### Migration Strategy

#### 1. Identify Problem Files
```bash
# Find files with Unicode characters
find . -name "*.py" -exec bash -c '
    chars=$(grep -P "[^\x00-\x7F]" "$1" | wc -l)
    if [ "$chars" -gt 0 ]; then
        echo "$1: $chars Unicode characters"
    fi
' _ {} \;
```

#### 2. Batch Replacement
```python
# batch_replace_unicode.py
import os
import glob

def batch_replace_unicode(directory):
    replacements = {
        '✅': '[PASS]',
        '❌': '[FAIL]',
        # ... add all replacements
    }

    for filepath in glob.glob(os.path.join(directory, '**/*.py'), recursive=True):
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()

        original_content = content
        for unicode_char, ascii_equiv in replacements.items():
            content = content.replace(unicode_char, ascii_equiv)

        if content != original_content:
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(content)
            print(f"Updated: {filepath}")

if __name__ == "__main__":
    batch_replace_unicode('.')
```

### Common Issues and Fixes

#### Issue 1: Print Statements with Emojis
```python
# BEFORE (causes encoding errors)
print("🚀 Starting deployment...")

# AFTER (encoding safe)
print("[DEPLOY] Starting deployment...")
```

#### Issue 2: String Literals in Code
```python
# BEFORE (causes encoding errors)
error_msg = "❌ Deployment failed"

# AFTER (encoding safe)
error_msg = "[FAIL] Deployment failed"
```

#### Issue 3: Comments with Unicode
```python
# BEFORE (causes encoding issues)
# ✅ This function works correctly

# AFTER (encoding safe)
# [PASS] This function works correctly
```

### Enforcement

#### Code Review Checklist
- [ ] No Unicode characters in production scripts
- [ ] All status messages use ASCII equivalents
- [ ] File I/O uses explicit UTF-8 encoding
- [ ] Unicode validation passes in CI/CD

#### Team Guidelines
1. **Never use Unicode characters in production code**
2. **Always use ASCII equivalents for status indicators**
3. **Test encoding compatibility before deployment**
4. **Use validation tools to catch issues early**

### References

- [Python Unicode HOWTO](https://docs.python.org/3/howto/unicode.html)
- [Character Encoding Issues](https://www.joelonsoftware.com/2003/10/08/the-absolute-minimum-every-software-developer-absolutely-positively-must-know-about-unicode-and-character-sets-no-excuses/)
- [UTF-8 Encoding Best Practices](https://utf8everywhere.org/)

---

**Remember**: When in doubt, replace Unicode with ASCII. Better safe than sorry!
