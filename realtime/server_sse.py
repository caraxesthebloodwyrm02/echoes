"""
Simple SSE server for Glimpse using Python stdlib only.
Exposes endpoints:
- GET /events  : Server-Sent Events stream of preview frames
- POST /input  : Submit prompt updates {"prompt": str, "stage": "draft"|"final"}
- GET /health  : Returns 200 OK for readiness checks

The server embeds a Glimpse orchestrator and broadcasts frames on every input.
"""
from __future__ import annotations

import json
import threading
import time
from http.server import ThreadingHTTPServer, BaseHTTPRequestHandler
from typing import List, Dict, Any
from queue import Queue, Empty
from pathlib import Path

from realtime_preview import create_glimpse


class SSEHub:
    """Thread-safe hub to manage SSE client queues and broadcast messages."""
    def __init__(self) -> None:
        self._clients: List[Queue] = []
        self._lock = threading.Lock()

    def add_client(self) -> Queue:
        q: Queue = Queue()
        with self._lock:
            self._clients.append(q)
        return q

    def remove_client(self, q: Queue) -> None:
        with self._lock:
            if q in self._clients:
                self._clients.remove(q)

    def broadcast(self, data: Dict[str, Any]) -> None:
        payload = json.dumps(data, ensure_ascii=False)
        with self._lock:
            for q in list(self._clients):
                try:
                    q.put_nowait(payload)
                except Exception:
                    # best-effort
                    pass


class ServerState:
    def __init__(self, base_path: Path) -> None:
        self.system = create_glimpse(mode="timeline", enable_security=False, base_path=base_path)
        self.system.start()
        self.hub = SSEHub()
        self.current_stage: str = "draft"  # "draft"|"final"
        self.job_id_counter: int = 0
        # Register event callback to broadcast frames
        self.system.register_event_callback(self._on_event)

    def _on_event(self, event: Dict[str, Any]):
        try:
            frame = event.get("preview")
            if not frame:
                return
            # Determine blur by stage (draft more blurry)
            stage = self.current_stage
            blur = 0.7 if stage == "draft" else 0.1
            ascii_preview = self.system.renderer.generate_ascii_preview(frame, blur=blur)

            data = {
                "type": "preview",
                "stage": stage,
                "job_id": self.job_id_counter,
                "frame": frame.to_dict(),
                "ascii": ascii_preview,
                "ts": time.time(),
            }
            self.hub.broadcast(data)
        except Exception:
            # Prevent callback exceptions from crashing
            pass


class PreviewRequestHandler(BaseHTTPRequestHandler):
    server_version = "GlimpseSSE/0.1"

    def do_GET(self):  # type: ignore[override]
        if self.path == "/events":
            return self._handle_events()
        if self.path == "/health":
            return self._handle_health()
        self.send_error(404, "Not Found")

    def do_POST(self):  # type: ignore[override]
        if self.path == "/input":
            return self._handle_input()
        self.send_error(404, "Not Found")

    # Helpers
    @property
    def state(self) -> ServerState:
        # type: ignore[attr-defined]
        return self.server.state  # provided by start_server()

    def _handle_health(self):
        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.end_headers()
        self.wfile.write(b"{\"status\":\"ok\"}")

    def _handle_events(self):
        self.send_response(200)
        self.send_header("Content-Type", "text/event-stream")
        self.send_header("Cache-Control", "no-cache")
        self.send_header("Connection", "keep-alive")
        self.end_headers()

        client_q = self.state.hub.add_client()
        try:
            # Initial comment to open stream
            try:
                self.wfile.write(b": connected\n\n")
                self.wfile.flush()
            except Exception:
                return

            while True:
                try:
                    payload = client_q.get(timeout=30.0)
                    msg = f"event: preview\ndata: {payload}\n\n".encode("utf-8")
                    self.wfile.write(msg)
                    self.wfile.flush()
                except Empty:
                    # keepalive
                    try:
                        self.wfile.write(b": keepalive\n\n")
                        self.wfile.flush()
                    except Exception:
                        break
                except Exception:
                    break
        finally:
            self.state.hub.remove_client(client_q)

    def _handle_input(self):
        # Read JSON body
        length = int(self.headers.get("Content-Length", "0"))
        body = self.rfile.read(length) if length > 0 else b"{}"
        try:
            data = json.loads(body.decode("utf-8"))
        except Exception:
            data = {}
        prompt = data.get("prompt", "")
        stage = data.get("stage", "draft")
        if stage not in ("draft", "final"):
            stage = "draft"
        self.state.current_stage = stage

        # Replace entire content with prompt
        adapter = self.state.system.input_adapter
        start = 0
        end = len(adapter.current_content)
        self.state.system.process_input(action="replace", start=start, end=end, text=prompt)

        # bump job id on new prompt content change
        self.state.job_id_counter += 1

        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.end_headers()
        resp = {
            "ok": True,
            "job_id": self.state.job_id_counter,
            "stage": stage,
            "len": len(prompt),
        }
        self.wfile.write(json.dumps(resp).encode("utf-8"))


def start_server(host: str = "127.0.0.1", port: int = 8765, base_path: Path | None = None) -> ThreadingHTTPServer:
    server = ThreadingHTTPServer((host, port), PreviewRequestHandler)
    # attach state
    server.state = ServerState(base_path or Path(__file__).parent)  # type: ignore[attr-defined]
    t = threading.Thread(target=server.serve_forever, name="SSEServer", daemon=True)
    t.start()
    return server


if __name__ == "__main__":
    start_server()
    print("SSE server running at http://127.0.0.1:8765")
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        pass
