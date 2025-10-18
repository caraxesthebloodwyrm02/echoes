# MIT License
#
# Copyright (c) 2024 Echoes Project
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

# Direct filtering
from packages.security import PrivacyFilter

filter = PrivacyFilter()
safe_text = filter.mask("Contact john.doe@example.com at 555-123-4567")

# API middleware
from packages.security import PrivacyMiddleware

middleware = PrivacyMiddleware(filter_mode="mask")


@middleware.filter_response
def get_user():
    return {"email": "user@example.com", "phone": "555-123-4567"}


# Codebase scanning
# python -m packages.security.privacy_scanner . --extensions .py

# Alternative: Use the scanner programmatically
try:
    from packages.security.privacy_scanner import scan_directory

    results = scan_directory(".", extensions=[".py"])
    print(f"Privacy scan completed. Found {len(results)} potential issues.")
except ImportError:
    print(
        "Privacy scanner not available. Install packages.security to enable scanning."
    )
