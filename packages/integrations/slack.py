from __future__ import annotations

import json
import os
import urllib.request
from typing import Optional


def send_slack_message(text: str, webhook_url: Optional[str] = None) -> int:
    """Send a simple Slack message via Incoming Webhook.

    Returns HTTP status code.
    """
    url = webhook_url or os.getenv("SLACK_WEBHOOK_URL", "")
    if not url:
        raise ValueError("Missing Slack webhook URL (env SLACK_WEBHOOK_URL)")
    data = json.dumps({"text": text}).encode("utf-8")
    req = urllib.request.Request(
        url, data=data, headers={"Content-Type": "application/json"}
    )
    with urllib.request.urlopen(req) as resp:  # nosec - controlled webhook
        return resp.getcode()
