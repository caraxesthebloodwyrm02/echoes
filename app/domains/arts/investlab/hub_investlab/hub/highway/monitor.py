#!/usr/bin/env python3
"""
Highway Monitor - Real-time monitoring and optimization of the highway system
"""

import os
import json
import time
from datetime import datetime
from typing import Dict, List, Any
from highway import Highway, get_highway
from highway.router import get_highway_router
from highway.development_bridge import get_development_bridge

class HighwayMonitor:
    """Real-time monitoring and optimization of the highway system"""

    def __init__(self):
        self.highway = get_highway()
        self.router = get_highway_router()
        self.dev_bridge = get_development_bridge()
        self.monitor_log = []
        self.optimization_suggestions = []
        self.project_root = "D:\\hub\\hub"
        
        # Monitoring intervals (seconds)
        self.intervals = {
            'highway_status': 30,
            'routing_performance': 60,
            'development_sync': 300,
            'cross_module_learning': 180
        }

    def start_monitoring(self):
        """Start the highway monitoring system"""
        print("🛣️  Highway Monitor Starting...")
        print("📊 Real-time monitoring of intelligent routing system")
        print("=" * 60)
        
        try:
            while True:
                self._monitor_cycle()
                time.sleep(30)  # Base monitoring interval
        except KeyboardInterrupt:
            print("\n🛑 Highway Monitor stopped by user")
            self._generate_final_report()

    def _monitor_cycle(self):
        """One complete monitoring cycle"""
        cycle_data = {
            'timestamp': datetime.now().isoformat(),
            'highway_status': self._check_highway_status(),
            'routing_performance': self._check_routing_performance(),
            'development_sync': self._check_development_sync(),
            'cross_module_learning': self._check_cross_module_learning(),
            'optimization_suggestions': []
        }

        # Generate optimization suggestions
        cycle_data['optimization_suggestions'] = self._generate_optimizations(cycle_data)

        # Log the cycle
        self.monitor_log.append(cycle_data)

        # Display current status
        self._display_status(cycle_data)

    def _check_highway_status(self) -> Dict[str, Any]:
        """Check current highway status"""
        status = self.highway.get_highway_status()
        
        return {
            'modules_active': len([m for m in status['modules'].values() if m['status'] == 'active']),
            'total_packets': status['performance_metrics']['total_packets_routed'],
            'success_rate': self._calculate_success_rate(status),
            'cached_packets': status['cached_packets']
        }

    def _check_routing_performance(self) -> Dict[str, Any]:
        """Check routing performance metrics"""
        status = self.highway.get_highway_status()
        metrics = status['performance_metrics']
        
        return {
            'average_route_time': metrics['average_route_time'],
            'successful_routes': metrics['successful_routes'],
            'failed_routes': metrics['failed_routes'],
            'learning_improvements': metrics['learning_improvements']
        }

    def _check_development_sync(self) -> Dict[str, Any]:
        """Check development project sync status"""
        return self.dev_bridge.get_bridge_status()

    def _check_cross_module_learning(self) -> Dict[str, Any]:
        """Check cross-module learning status"""
        return self.router.monitor_cross_module_learnings()

    def _calculate_success_rate(self, status: Dict[str, Any]) -> float:
        """Calculate routing success rate"""
        metrics = status['performance_metrics']
        total = metrics['successful_routes'] + metrics['failed_routes']
        if total == 0:
            return 0.0
        return (metrics['successful_routes'] / total) * 100

    def _generate_optimizations(self, cycle_data: Dict[str, Any]) -> List[str]:
        """Generate optimization suggestions"""
        suggestions = []

        # Highway optimization suggestions
        if cycle_data['highway_status']['success_rate'] < 85:
            suggestions.append("⚠️  Low success rate detected - consider checking module connectivity")

        if cycle_data['highway_status']['cached_packets'] > 1000:
            suggestions.append("📦 High cache usage - consider reducing TTL or increasing cleanup frequency")

        # Routing performance suggestions
        if cycle_data['routing_performance']['average_route_time'] > 5.0:
            suggestions.append("⏱️  High route time - consider optimizing routing algorithm")

        # Development sync suggestions
        dev_status = cycle_data['development_sync']
        if dev_status.get('projects_found', 0) == 0:
            suggestions.append("🔍 No external projects found - check E:\\projects\\development path")

        # Cross-module learning suggestions
        learnings = cycle_data['cross_module_learning']
        for category, data in learnings.items():
            if isinstance(data, dict) and data.get('last_learning'):
                last_learning = datetime.fromisoformat(data['last_learning'])
                if (datetime.now() - last_learning).days > 1:
                    suggestions.append(f"📈 {category} - consider triggering learning cycle")

        return suggestions

    def _display_status(self, cycle_data: Dict[str, Any]):
        """Display current monitoring status"""
        print(f"\n📊 Highway Status - {datetime.now().strftime('%H:%M:%S')}")
        print("-" * 40)
        
        # Highway status
        highway = cycle_data['highway_status']
        print(f"🛣️  Modules Active: {highway['modules_active']}/7")
        print(f"📦 Packets Routed: {highway['total_packets']}")
        print(f"✅ Success Rate: {highway['success_rate']:.1f}%")
        print(f"💾 Cached Packets: {highway['cached_packets']}")

        # Routing performance
        routing = cycle_data['routing_performance']
        print(f"⏱️  Avg Route Time: {routing['average_route_time']:.2f}s")
        print(f"🎯 Successful Routes: {routing['successful_routes']}")
        print(f"❌ Failed Routes: {routing['failed_routes']}")

        # Development sync
        dev = cycle_data['development_sync']
        print(f"🏗️  External Projects: {dev.get('projects_found', 0)}")
        print(f"🔗 Sync Log: {len(dev.get('sync_log', []))} entries")

        # Cross-module learning
        learning = cycle_data['cross_module_learning']
        total_learnings = sum(len(data) if isinstance(data, dict) else 0 for data in learning.values())
        print(f"🧠 Cross-Module Learnings: {total_learnings}")

        # Optimization suggestions
        if cycle_data['optimization_suggestions']:
            print("\n💡 Optimization Suggestions:")
            for suggestion in cycle_data['optimization_suggestions']:
                print(f"   {suggestion}")

    def _generate_final_report(self):
        """Generate final monitoring report"""
        report = {
            'total_cycles': len(self.monitor_log),
            'start_time': self.monitor_log[0]['timestamp'] if self.monitor_log else None,
            'end_time': self.monitor_log[-1]['timestamp'] if self.monitor_log else None,
            'average_success_rate': self._calculate_average_success_rate(),
            'total_optimizations': len(self.optimization_suggestions),
            'final_status': self.highway.get_highway_status()
        }

        # Save report
        report_path = os.path.join(self.project_root, "highway", "monitoring_report.json")
        os.makedirs(os.path.dirname(report_path), exist_ok=True)
        
        with open(report_path, 'w') as f:
            json.dump(report, f, indent=2, default=str)

        print(f"📋 Final report saved to: {report_path}")

    def _calculate_average_success_rate(self) -> float:
        """Calculate average success rate across all cycles"""
        if not self.monitor_log:
            return 0.0
        
        success_rates = [cycle['highway_status']['success_rate'] for cycle in self.monitor_log]
        return sum(success_rates) / len(success_rates)

    def get_real_time_dashboard(self) -> Dict[str, Any]:
        """Get real-time dashboard data"""
        return {
            'highway_status': self.highway.get_highway_status(),
            'routing_performance': self.router.monitor_cross_module_learnings(),
            'development_sync': self.dev_bridge.get_bridge_status(),
            'monitoring_log': self.monitor_log[-10:] if len(self.monitor_log) > 10 else self.monitor_log,
            'optimization_suggestions': self.optimization_suggestions[-5:] if len(self.optimization_suggestions) > 5 else self.optimization_suggestions,
            'timestamp': datetime.now().isoformat()
        }

    def trigger_optimization(self, optimization_type: str) -> Dict[str, Any]:
        """Trigger specific optimizations"""
        results = {'type': optimization_type, 'success': False, 'details': {}}

        if optimization_type == 'cache_cleanup':
            # Clear old cached packets
            results['details']['cleared_packets'] = self._cleanup_cache()
            results['success'] = True

        elif optimization_type == 'module_health_check':
            # Check all module health
            results['details'] = self._check_module_health()
            results['success'] = True

        elif optimization_type == 'routing_optimization':
            # Optimize routing based on performance
            results['details'] = self._optimize_routing()
            results['success'] = True

        elif optimization_type == 'development_sync':
            # Force sync with development projects
            results['details'] = self.dev_bridge.sync_with_external_projects()
            results['success'] = True

        return results

    def _cleanup_cache(self) -> int:
        """Clean up old cached packets"""
        # This would be implemented based on highway cache structure
        return 0

    def _check_module_health(self) -> Dict[str, Any]:
        """Check health of all modules"""
        health = {}
        for module_name in self.highway.modules:
            status = self.highway.get_module_status(module_name)
            health[module_name] = {
                'status': status['status'],
                'last_activity': status['last_activity'],
                'data_types': len(status['data_types']),
                'capabilities': len(status['capabilities'])
            }
        return health

    def _optimize_routing(self) -> Dict[str, Any]:
        """Optimize routing based on performance data"""
        # This would implement routing optimization logic
        return {
            'routes_optimized': 0,
            'performance_improvement': 0.0,
            'timestamp': datetime.now().isoformat()
        }

    def export_highway_data(self, format: str = 'json') -> str:
        """Export highway data for analysis"""
        export_data = {
            'highway_status': self.highway.get_highway_status(),
            'routing_performance': self.router.monitor_cross_module_learnings(),
            'development_bridge': self.dev_bridge.get_bridge_status(),
            'monitoring_log': self.monitor_log,
            'export_timestamp': datetime.now().isoformat()
        }

        export_path = os.path.join(self.project_root, "highway", f"export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.{format}")
        os.makedirs(os.path.dirname(export_path), exist_ok=True)

        if format == 'json':
            with open(export_path, 'w') as f:
                json.dump(export_data, f, indent=2, default=str)

        return export_path

# Global monitor instance
highway_monitor = HighwayMonitor()

def get_highway_monitor() -> HighwayMonitor:
    """Get the global highway monitor instance"""
    return highway_monitor

def start_monitoring():
    """Start the highway monitoring system"""
    return highway_monitor.start_monitoring()

def get_dashboard() -> Dict[str, Any]:
    """Get real-time dashboard data"""
    return highway_monitor.get_real_time_dashboard()

def trigger_optimization(optimization_type: str) -> Dict[str, Any]:
    """Trigger specific optimizations"""
    return highway_monitor.trigger_optimization(optimization_type)
