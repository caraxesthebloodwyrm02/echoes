"""
Glimpse Tkinter Live Preview UI (SSE client).
- Starts or connects to an SSE server (server_sse.py) on localhost.
- Sends prompt updates via POST /input with draft/final stages using debounce.
- Receives preview frames via Server-Sent Events and renders ASCII in a monospace view.

Pure stdlib implementation.
"""

from __future__ import annotations

import json
import threading
import time
import urllib.request
import urllib.error
import urllib.parse
from dataclasses import dataclass
from typing import Optional

import tkinter as tk
from tkinter import font as tkfont

# Local imports (server and system)
try:
    from server_sse import start_server
except Exception:
    start_server = None  # optional; we will connect if already running

DEFAULT_HOST = "127.0.0.1"
DEFAULT_PORT = 8765
SSE_URL = f"http://{DEFAULT_HOST}:{DEFAULT_PORT}/events"
INPUT_URL = f"http://{DEFAULT_HOST}:{DEFAULT_PORT}/input"


@dataclass
class DebounceTimers:
    draft_after: Optional[str] = None
    final_after: Optional[str] = None


class SSEListener(threading.Thread):
    def __init__(self, url: str, on_preview, on_status):
        super().__init__(name="SSEListener", daemon=True)
        self.url = url
        self.on_preview = on_preview  # callable(dict)
        self.on_status = on_status  # callable(str)
        self._stop = threading.Event()

    def stop(self):
        self._stop.set()

    def run(self):
        backoff = 0.5
        while not self._stop.is_set():
            try:
                req = urllib.request.Request(self.url, headers={"Accept": "text/event-stream"})
                resp = urllib.request.urlopen(req, timeout=30)
                self.on_status("connected")
                event_type = None
                data_lines = []

                while not self._stop.is_set():
                    line = resp.readline()  # type: ignore[attr-defined]
                    if not line:
                        break
                    s = line.decode("utf-8", errors="replace").rstrip("\r\n")
                    if s.startswith(":"):
                        continue  # comment/keepalive
                    if s.startswith("event:"):
                        event_type = s[6:].strip()
                    elif s.startswith("data:"):
                        data_lines.append(s[5:].strip())
                    elif s == "":
                        if event_type and data_lines:
                            try:
                                payload = json.loads("\n".join(data_lines))
                                if event_type == "preview":
                                    self.on_preview(payload)
                            except Exception:
                                pass
                        event_type = None
                        data_lines = []
                try:
                    resp.close()
                except Exception:
                    pass
                self.on_status("disconnected; retrying")
            except Exception:
                self.on_status("connect_failed; retrying")
            # backoff
            time.sleep(backoff)
            backoff = min(5.0, backoff * 1.5)


class LivePreviewApp:
    def __init__(self, root: tk.Tk):
        self.root = root
        self.root.title("Glimpse Live Preview (Tk + SSE)")

        # Fonts
        try:
            mono = tkfont.Font(family="Consolas", size=10)
        except Exception:
            mono = tkfont.Font(family="Courier New", size=10)
        self.mono = mono

        # Layout
        container = tk.Frame(root)
        container.pack(fill=tk.BOTH, expand=True)

        left = tk.Frame(container)
        left.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        right = tk.Frame(container, width=520)
        right.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)

        # Prompt box
        tk.Label(left, text="Prompt").pack(anchor="w")
        self.prompt = tk.Text(left, height=8, wrap="word")
        self.prompt.pack(fill=tk.BOTH, expand=True)
        self.prompt.bind("<KeyRelease>", self.on_key)

        # Controls
        controls = tk.Frame(left)
        controls.pack(fill=tk.X)
        tk.Label(controls, text="Debounce:").pack(side=tk.LEFT)
        self.debounce_var = tk.IntVar(value=120)
        tk.Entry(controls, width=5, textvariable=self.debounce_var).pack(side=tk.LEFT)
        tk.Label(controls, text="ms   ").pack(side=tk.LEFT)
        self.status_var = tk.StringVar(value="disconnected")
        tk.Label(controls, textvariable=self.status_var).pack(side=tk.RIGHT)

        # Preview area
        tk.Label(right, text="Live Preview (ASCII)").pack(anchor="w")
        self.preview = tk.Text(right, height=28, wrap="none")
        self.preview.configure(font=self.mono)
        self.preview.pack(fill=tk.BOTH, expand=True)
        self.preview.configure(state=tk.DISABLED)

        # Debounce timers
        self.timers = DebounceTimers()

        # SSE listener
        self.listener = SSEListener(SSE_URL, self._on_preview_event, self._on_status)

        # Start/ensure server, then connect
        self._ensure_server()
        self.listener.start()

        # Initial content
        self.prompt.insert("1.0", "forest with green trees, sunny day, hiker perspective")
        self._schedule_updates()

    # Networking helpers
    def _ensure_server(self):
        # Quick health check; if fails and start_server available, start locally.
        ok = self._health_check()
        if not ok and start_server is not None:
            try:
                start_server()
                # wait a bit for bind
                time.sleep(0.2)
            except Exception:
                pass

    def _health_check(self) -> bool:
        try:
            resp = urllib.request.urlopen(f"http://{DEFAULT_HOST}:{DEFAULT_PORT}/health", timeout=0.8)
            return resp.status == 200
        except Exception:
            return False

    def _post_input(self, prompt: str, stage: str):
        data = json.dumps({"prompt": prompt, "stage": stage}).encode("utf-8")
        req = urllib.request.Request(INPUT_URL, data=data, headers={"Content-Type": "application/json"}, method="POST")
        try:
            urllib.request.urlopen(req, timeout=2)
        except Exception:
            pass

    # Event handlers
    def on_key(self, _event=None):
        self._schedule_updates()

    def _schedule_updates(self):
        # cancel previous
        if self.timers.draft_after:
            try:
                self.root.after_cancel(self.timers.draft_after)
            except Exception:
                pass
        if self.timers.final_after:
            try:
                self.root.after_cancel(self.timers.final_after)
            except Exception:
                pass

        try:
            debounce_ms = max(30, int(self.debounce_var.get()))
        except Exception:
            debounce_ms = 120

        # schedule draft and final
        self.timers.draft_after = self.root.after(debounce_ms, self._send_stage, "draft")
        self.timers.final_after = self.root.after(int(debounce_ms * 4), self._send_stage, "final")

    def _send_stage(self, stage: str):
        content = self.prompt.get("1.0", tk.END)
        self._post_input(content, stage)

    # SSE callbacks (from background thread)
    def _on_preview_event(self, payload: dict):
        ascii_preview = payload.get("ascii", "")
        stage = payload.get("stage", "draft")
        # marshal to main thread
        self.root.after(0, self._render_ascii, ascii_preview, stage)

    def _on_status(self, s: str):
        # marshal to main thread
        self.root.after(0, lambda: self.status_var.set(s))

    # UI updates (main thread)
    def _render_ascii(self, text: str, stage: str):
        self.preview.configure(state=tk.NORMAL)
        self.preview.delete("1.0", tk.END)
        self.preview.insert("1.0", text)
        self.preview.configure(state=tk.DISABLED)
        self.root.title(f"Glimpse Live Preview (Tk + SSE) - {stage}")

    def close(self):
        try:
            self.listener.stop()
        except Exception:
            pass


def main():
    root = tk.Tk()
    app = LivePreviewApp(root)

    def on_close():
        try:
            app.close()
        finally:
            root.destroy()

    root.protocol("WM_DELETE_WINDOW", on_close)
    root.geometry("1000x700")
    root.mainloop()


if __name__ == "__main__":
    main()
