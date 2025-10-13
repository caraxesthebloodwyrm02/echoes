import json
from pathlib import Path
from typing import Optional

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
        payload = {"title": title, "message": message, "ts": __import__("datetime").datetime.utcnow().isoformat() + "Z"}

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
