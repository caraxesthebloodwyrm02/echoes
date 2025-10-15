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

import json
from pathlib import Path

try:
    from plyer import notification

    _HAS_PLYER = True
except Exception:
    _HAS_PLYER = False

LAST_NOTIFY = Path("automation/cache/last_notification.json")
LAST_NOTIFY.parent.mkdir(parents=True, exist_ok=True)


class Notifier:
    """Simple cross-environment notification helper.

    - Uses plyer.notification when available (desktop notifications).
    - Falls back to writing a small JSON file and printing a console line.
    """

    @staticmethod
    def notify(title: str, message: str, timeout: int = 5) -> None:
        payload = {
            "title": title,
            "message": message,
            "ts": __import__("datetime").datetime.utcnow().isoformat() + "Z",
        }

        # Try desktop notification first
        if _HAS_PLYER:
            try:
                notification.notify(title=title, message=message, timeout=timeout)
            except Exception:
                # fall through to file-based notification
                pass

        # Always write last notification so external watchers can pick it up
        try:
            with open(LAST_NOTIFY, "w") as f:
                json.dump(payload, f)
        except Exception:
            pass

        # Console fallback
        print(f"[NOTIFY] {title}: {message}")
