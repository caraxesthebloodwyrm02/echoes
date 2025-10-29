"""
Prometheus metrics server for Glimpse.
Exposes a /metrics endpoint that can be scraped by Prometheus.
"""
import asyncio
import logging
from typing import Optional
from aiohttp import web
from prometheus_client import generate_latest

logger = logging.getLogger(__name__)

class MetricsServer:
    """HTTP server to expose Prometheus metrics."""
    
    def __init__(self, host: str = '0.0.0.0', port: int = 8000):
        self.host = host
        self.port = port
        self.app = web.Application()
        self.runner: Optional[web.AppRunner] = None
        self.site: Optional[web.TCPSite] = None
        
        # Setup routes
        self.app.router.add_get('/metrics', self.handle_metrics)
        self.app.router.add_get('/health', self.handle_health)
    
    async def handle_metrics(self, request: web.Request) -> web.Response:
        """Handle /metrics endpoint."""
        try:
            from .metrics import get_metrics
            metrics_data = get_metrics()
            return web.Response(
                body=metrics_data,
                content_type='text/plain; version=0.0.4'
            )
        except Exception as e:
            logger.error("Failed to generate metrics", exc_info=True)
            return web.Response(
                status=500,
                text=f"Failed to generate metrics: {str(e)}"
            )
    
    async def handle_health(self, request: web.Request) -> web.Response:
        """Handle /health endpoint."""
        return web.json_response({"status": "healthy"})
    
    async def start(self) -> None:
        """Start the metrics server."""
        self.runner = web.AppRunner(self.app)
        await self.runner.setup()
        self.site = web.TCPSite(self.runner, self.host, self.port)
        await self.site.start()
        logger.info(f"Metrics server started at http://{self.host}:{self.port}")
    
    async def stop(self) -> None:
        """Stop the metrics server."""
        if self.site:
            await self.site.stop()
        if self.runner:
            await self.runner.cleanup()
        logger.info("Metrics server stopped")

# Global metrics server instance
_metrics_server: Optional[MetricsServer] = None

async def start_metrics_server(host: str = '0.0.0.0', port: int = 8000) -> None:
    """Start the global metrics server."""
    global _metrics_server
    if _metrics_server is None:
        _metrics_server = MetricsServer(host=host, port=port)
        await _metrics_server.start()

async def stop_metrics_server() -> None:
    """Stop the global metrics server."""
    global _metrics_server
    if _metrics_server:
        await _metrics_server.stop()
        _metrics_server = None

def get_metrics_server() -> Optional[MetricsServer]:
    """Get the global metrics server instance."""
    return _metrics_server

# For running the server directly for testing
async def main():
    import signal
    import sys
    
    # Configure logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # Start the server
    server = MetricsServer(port=8000)
    await server.start()
    
    # Handle shutdown
    async def shutdown(signal, loop):
        logger.info("Shutting down metrics server...")
        await server.stop()
        loop.stop()
    
    # Register signal handlers
    loop = asyncio.get_running_loop()
    for sig in (signal.SIGINT, signal.SIGTERM):
        loop.add_signal_handler(
            sig, 
            lambda s=sig: asyncio.create_task(shutdown(s, loop))
        )
    
    # Keep the server running
    while True:
        await asyncio.sleep(3600)  # Sleep for a long time

if __name__ == "__main__":
    asyncio.run(main())
