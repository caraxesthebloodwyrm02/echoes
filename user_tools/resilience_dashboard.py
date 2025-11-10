#!/usr/bin/env python3
"""
Resilience Dashboard - Real-time System Health Monitoring
Based on 18-hour optimization experience

Features:
- Real-time health monitoring
- Third-party dependency tracking
- Interruption prevention alerts
- Performance metrics visualization
"""

import asyncio
import logging
from datetime import datetime
from typing import Dict, Any, List
from dataclasses import dataclass
from enum import Enum

from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.responses import HTMLResponse

class HealthStatus(Enum):
    HEALTHY = "healthy"
    WARNING = "warning"
    CRITICAL = "critical"
    UNKNOWN = "unknown"

@dataclass
class HealthMetric:
    name: str
    status: HealthStatus
    value: float
    threshold: float
    last_updated: datetime
    description: str

@dataclass
class DependencyStatus:
    name: str
    status: HealthStatus
    response_time: float
    error_rate: float
    last_check: datetime
    circuit_breaker_active: bool

class ResilienceDashboard:
    """Comprehensive resilience monitoring dashboard"""

    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.health_metrics: Dict[str, HealthMetric] = {}
        self.dependencies: Dict[str, DependencyStatus] = {}
        self.alerts: List[Dict[str, Any]] = []
        self.performance_history: List[Dict[str, Any]] = []
        self.connected_clients: List[WebSocket] = []

        # Initialize health checks
        self._initialize_health_checks()
        self._initialize_dependency_monitoring()

    def _initialize_health_checks(self):
        """Initialize system health monitoring"""
        self.health_metrics = {
            "cpu_usage": HealthMetric(
                "CPU Usage", HealthStatus.HEALTHY, 0.0, 80.0,
                datetime.now(), "Percentage of CPU utilization"
            ),
            "memory_usage": HealthMetric(
                "Memory Usage", HealthStatus.HEALTHY, 0.0, 85.0,
                datetime.now(), "Percentage of memory utilization"
            ),
            "response_time": HealthMetric(
                "Response Time", HealthStatus.HEALTHY, 0.0, 1000.0,
                datetime.now(), "Average API response time in ms"
            ),
            "error_rate": HealthMetric(
                "Error Rate", HealthStatus.HEALTHY, 0.0, 5.0,
                datetime.now(), "Percentage of failed requests"
            ),
            "selective_attention_efficiency": HealthMetric(
                "Selective Attention", HealthStatus.HEALTHY, 84.0, 70.0,
                datetime.now(), "Cognitive load reduction percentage"
            )
        }

    def _initialize_dependency_monitoring(self):
        """Initialize third-party dependency monitoring"""
        self.dependencies = {
            "openai_api": DependencyStatus(
                "OpenAI API", HealthStatus.HEALTHY, 200.0, 0.0,
                datetime.now(), False
            ),
            "vector_index": DependencyStatus(
                "Vector Index", HealthStatus.HEALTHY, 50.0, 0.0,
                datetime.now(), False
            ),
            "cache_system": DependencyStatus(
                "Cache System", HealthStatus.HEALTHY, 10.0, 0.0,
                datetime.now(), False
            ),
            "database": DependencyStatus(
                "Database", HealthStatus.HEALTHY, 100.0, 0.0,
                datetime.now(), False
            )
        }

    async def update_health_metrics(self):
        """Update all health metrics"""
        try:
            # Simulate metric collection (replace with actual monitoring)
            import psutil

            # Update CPU usage
            cpu_percent = psutil.cpu_percent(interval=1)
            self.health_metrics["cpu_usage"].value = cpu_percent
            self.health_metrics["cpu_usage"].status = (
                HealthStatus.WARNING if cpu_percent > 70 else HealthStatus.CRITICAL if cpu_percent > 90 else HealthStatus.HEALTHY
            )
            self.health_metrics["cpu_usage"].last_updated = datetime.now()

            # Update memory usage
            memory = psutil.virtual_memory()
            memory_percent = memory.percent
            self.health_metrics["memory_usage"].value = memory_percent
            self.health_metrics["memory_usage"].status = (
                HealthStatus.WARNING if memory_percent > 75 else HealthStatus.CRITICAL if memory_percent > 95 else HealthStatus.HEALTHY
            )
            self.health_metrics["memory_usage"].last_updated = datetime.now()

            # Simulate other metrics
            self.health_metrics["response_time"].value = 250.0 + (hash(str(datetime.now())) % 200)
            self.health_metrics["error_rate"].value = max(0, 2.0 + (hash(str(datetime.now())) % 5))

            # Check for alerts
            await self._check_for_alerts()

        except Exception as e:
            self.logger.error(f"Failed to update health metrics: {e}")

    async def update_dependency_status(self):
        """Update third-party dependency status"""
        for name, dependency in self.dependencies.items():
            try:
                # Simulate dependency check (replace with actual health checks)
                import random
                response_time = 50 + random.random() * 300
                error_rate = random.random() * 10

                dependency.response_time = response_time
                dependency.error_rate = error_rate
                dependency.last_check = datetime.now()
                dependency.circuit_breaker_active = error_rate > 8.0

                # Update status based on metrics
                if error_rate > 8.0 or response_time > 500:
                    dependency.status = HealthStatus.CRITICAL
                elif error_rate > 5.0 or response_time > 300:
                    dependency.status = HealthStatus.WARNING
                else:
                    dependency.status = HealthStatus.HEALTHY

            except Exception as e:
                self.logger.error(f"Failed to update dependency {name}: {e}")
                dependency.status = HealthStatus.CRITICAL
                dependency.circuit_breaker_active = True

    async def _check_for_alerts(self):
        """Check for conditions that require alerts"""
        current_time = datetime.now()

        for name, metric in self.health_metrics.items():
            if metric.status == HealthStatus.CRITICAL:
                alert = {
                    "id": len(self.alerts) + 1,
                    "type": "critical",
                    "source": name,
                    "message": f"Critical threshold exceeded for {name}: {metric.value:.2f} (threshold: {metric.threshold})",
                    "timestamp": current_time.isoformat(),
                    "acknowledged": False
                }
                self.alerts.append(alert)
                await self._broadcast_alert(alert)

    async def _broadcast_alert(self, alert: Dict[str, Any]):
        """Broadcast alert to all connected clients"""
        message = {
            "type": "alert",
            "data": alert
        }
        for client in self.connected_clients:
            try:
                await client.send_json(message)
            except Exception as e:
                self.logger.error(f"Failed to send alert to client: {e}")
                self.connected_clients.remove(client)

    async def get_dashboard_data(self) -> Dict[str, Any]:
        """Get comprehensive dashboard data"""
        return {
            "health_metrics": {
                name: {
                    "name": metric.name,
                    "status": metric.status.value,
                    "value": metric.value,
                    "threshold": metric.threshold,
                    "last_updated": metric.last_updated.isoformat(),
                    "description": metric.description
                }
                for name, metric in self.health_metrics.items()
            },
            "dependencies": {
                name: {
                    "name": dep.name,
                    "status": dep.status.value,
                    "response_time": dep.response_time,
                    "error_rate": dep.error_rate,
                    "last_check": dep.last_check.isoformat(),
                    "circuit_breaker_active": dep.circuit_breaker_active
                }
                for name, dep in self.dependencies.items()
            },
            "alerts": self.alerts[-10:],  # Last 10 alerts
            "performance_history": self.performance_history[-100:],  # Last 100 data points
            "system_health": self._calculate_overall_health(),
            "timestamp": datetime.now().isoformat()
        }

    def _calculate_overall_health(self) -> Dict[str, Any]:
        """Calculate overall system health score"""
        total_metrics = len(self.health_metrics)
        healthy_metrics = sum(1 for m in self.health_metrics.values() if m.status == HealthStatus.HEALTHY)
        critical_metrics = sum(1 for m in self.health_metrics.values() if m.status == HealthStatus.CRITICAL)

        health_score = (healthy_metrics / total_metrics) * 100 if total_metrics > 0 else 0

        if critical_metrics > 0:
            overall_status = HealthStatus.CRITICAL
        elif health_score < 80:
            overall_status = HealthStatus.WARNING
        else:
            overall_status = HealthStatus.HEALTHY

        return {
            "status": overall_status.value,
            "score": health_score,
            "healthy_metrics": healthy_metrics,
            "total_metrics": total_metrics,
            "critical_metrics": critical_metrics
        }

    async def register_websocket_client(self, websocket: WebSocket):
        """Register a new WebSocket client for real-time updates"""
        await websocket.accept()
        self.connected_clients.append(websocket)

        # Send initial data
        dashboard_data = await self.get_dashboard_data()
        await websocket.send_json({
            "type": "initial_data",
            "data": dashboard_data
        })

    def unregister_websocket_client(self, websocket: WebSocket):
        """Unregister a WebSocket client"""
        if websocket in self.connected_clients:
            self.connected_clients.remove(websocket)

    async def broadcast_updates(self):
        """Broadcast updates to all connected clients"""
        if not self.connected_clients:
            return

        dashboard_data = await self.get_dashboard_data()
        message = {
            "type": "update",
            "data": dashboard_data
        }

        for client in self.connected_clients[:]:  # Copy list to avoid modification during iteration
            try:
                await client.send_json(message)
            except Exception as e:
                self.logger.error(f"Failed to send update to client: {e}")
                self.connected_clients.remove(client)

# Initialize dashboard
dashboard = ResilienceDashboard()

# Create FastAPI app for dashboard
app = FastAPI(title="EchoesAI Resilience Dashboard")

@app.get("/", response_class=HTMLResponse)
async def get_dashboard():
    """Serve the dashboard HTML"""
    return """
    <!DOCTYPE html>
    <html>
    <head>
        <title>EchoesAI Resilience Dashboard</title>
        <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
        <style>
            body { font-family: Arial, sans-serif; margin: 20px; background: #f5f5f5; }
            .dashboard { display: grid; grid-template-columns: 1fr 1fr; gap: 20px; }
            .card { background: white; padding: 20px; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }
            .metric { margin: 10px 0; padding: 10px; border-left: 4px solid #ddd; }
            .metric.healthy { border-left-color: #4CAF50; }
            .metric.warning { border-left-color: #FF9800; }
            .metric.critical { border-left-color: #F44336; }
            .alert { background: #ffebee; border: 1px solid #f44336; padding: 10px; margin: 5px 0; border-radius: 4px; }
            .status-indicator { display: inline-block; width: 12px; height: 12px; border-radius: 50%; margin-right: 8px; }
            .status-healthy { background: #4CAF50; }
            .status-warning { background: #FF9800; }
            .status-critical { background: #F44336; }
        </style>
    </head>
    <body>
        <h1>EchoesAI Resilience Dashboard</h1>
        <div class="dashboard">
            <div class="card">
                <h2>System Health</h2>
                <div id="health-metrics"></div>
            </div>
            <div class="card">
                <h2>Dependencies</h2>
                <div id="dependencies"></div>
            </div>
            <div class="card">
                <h2>Recent Alerts</h2>
                <div id="alerts"></div>
            </div>
            <div class="card">
                <h2>Performance Chart</h2>
                <canvas id="performance-chart"></canvas>
            </div>
        </div>

        <script>
            const ws = new WebSocket('ws://localhost:8000/ws');

            ws.onmessage = function(event) {
                const data = JSON.parse(event.data);

                if (data.type === 'update' || data.type === 'initial_data') {
                    updateDashboard(data.data);
                } else if (data.type === 'alert') {
                    addAlert(data.data);
                }
            };

            function updateDashboard(data) {
                // Update health metrics
                const healthDiv = document.getElementById('health-metrics');
                healthDiv.innerHTML = '';

                Object.values(data.health_metrics).forEach(metric => {
                    const metricDiv = document.createElement('div');
                    metricDiv.className = `metric ${metric.status}`;
                    metricDiv.innerHTML = `
                        <span class="status-indicator status-${metric.status}"></span>
                        <strong>${metric.name}:</strong> ${metric.value.toFixed(2)} (${metric.status})
                        <br><small>${metric.description}</small>
                    `;
                    healthDiv.appendChild(metricDiv);
                });

                // Update dependencies
                const depsDiv = document.getElementById('dependencies');
                depsDiv.innerHTML = '';

                Object.values(data.dependencies).forEach(dep => {
                    const depDiv = document.createElement('div');
                    depDiv.className = `metric ${dep.status}`;
                    depDiv.innerHTML = `
                        <span class="status-indicator status-${dep.status}"></span>
                        <strong>${dep.name}:</strong> ${dep.status}
                        <br><small>Response: ${dep.response_time.toFixed(0)}ms, Error Rate: ${dep.error_rate.toFixed(1)}%</small>
                        ${dep.circuit_breaker_active ? '<br><small>Circuit Breaker: ACTIVE</small>' : ''}
                    `;
                    depsDiv.appendChild(depDiv);
                });

                // Update alerts
                const alertsDiv = document.getElementById('alerts');
                alertsDiv.innerHTML = '';

                data.alerts.forEach(alert => {
                    const alertDiv = document.createElement('div');
                    alertDiv.className = 'alert';
                    alertDiv.innerHTML = `
                        <strong>${alert.type.toUpperCase()}:</strong> ${alert.message}
                        <br><small>${new Date(alert.timestamp).toLocaleString()}</small>
                    `;
                    alertsDiv.appendChild(alertDiv);
                });
            }

            function addAlert(alert) {
                // Handle real-time alerts
                console.log('New alert:', alert);
            }
        </script>
    </body>
    </html>
    """

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """WebSocket endpoint for real-time updates"""
    await dashboard.register_websocket_client(websocket)
    try:
        while True:
            await websocket.receive_text()
    except WebSocketDisconnect:
        dashboard.unregister_websocket_client(websocket)

@app.get("/api/dashboard")
async def get_dashboard_data():
    """Get dashboard data as JSON"""
    return await dashboard.get_dashboard_data()

@app.post("/api/acknowledge-alert/{alert_id}")
async def acknowledge_alert(alert_id: int):
    """Acknowledge an alert"""
    for alert in dashboard.alerts:
        if alert["id"] == alert_id:
            alert["acknowledged"] = True
            return {"status": "acknowledged"}
    return {"status": "not_found"}

if __name__ == "__main__":
    import uvicorn

    # Start background monitoring
    async def monitor_background():
        while True:
            await dashboard.update_health_metrics()
            await dashboard.update_dependency_status()
            await dashboard.broadcast_updates()
            await asyncio.sleep(5)  # Update every 5 seconds

    # Start monitoring in background
    asyncio.create_task(monitor_background())

    # Run the dashboard
    uvicorn.run(app, host="0.0.0.0", port=8000)
