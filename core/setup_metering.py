#!/usr/bin/env python3
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

"""
Cost Metering & Quotas Setup
Automates Task: "Cost Metering & Quotas" - Resource tracking and limits
"""

import json
import sys
from datetime import datetime
from pathlib import Path


class MeteringSetup:
    """Setup cost metering and quota management system"""

    def __init__(self):
        self.q4_root = Path(__file__).parent.parent

    def create_metering_models(self):
        """Create data models for cost tracking"""
        models_file = self.q4_root / "metering_models.py"

        code = '''"""
Cost Metering and Quota Models
"""

from dataclasses import dataclass
from datetime import datetime
from typing import Optional, Dict, Any
from enum import Enum

class ResourceType(Enum):
    """Types of resources to meter"""
    API_CALL = "api_call"
    COMPUTE_TIME = "compute_time"
    STORAGE = "storage"
    BANDWIDTH = "bandwidth"
    DATABASE_QUERY = "database_query"

@dataclass
class UsageRecord:
    """Record of resource usage"""
    user_id: str
    resource_type: ResourceType
    quantity: float
    cost: float
    timestamp: datetime
    metadata: Optional[Dict[str, Any]] = None

    def to_dict(self):
        return {
            "user_id": self.user_id,
            "resource_type": self.resource_type.value,
            "quantity": self.quantity,
            "cost": self.cost,
            "timestamp": self.timestamp.isoformat(),
            "metadata": self.metadata
        }

@dataclass
class Quota:
    """Resource quota definition"""
    user_id: str
    resource_type: ResourceType
    limit: float
    period: str  # "daily", "monthly", "yearly"
    current_usage: float = 0.0

    def is_exceeded(self) -> bool:
        """Check if quota is exceeded"""
        return self.current_usage >= self.limit

    def remaining(self) -> float:
        """Get remaining quota"""
        return max(0, self.limit - self.current_usage)

    def usage_percentage(self) -> float:
        """Get usage as percentage"""
        return (self.current_usage / self.limit * 100) if self.limit > 0 else 0

@dataclass
class CostRate:
    """Cost rate for a resource type"""
    resource_type: ResourceType
    rate_per_unit: float
    currency: str = "USD"

    def calculate_cost(self, quantity: float) -> float:
        """Calculate cost for given quantity"""
        return quantity * self.rate_per_unit
'''

        with open(models_file, "w") as f:
            f.write(code)

        print(f"✓ Created metering models: {models_file}")
        return models_file

    def create_metering_service(self):
        """Create metering service implementation"""
        service_file = self.q4_root / "metering_service.py"

        code = '''"""
Cost Metering Service
Tracks resource usage and enforces quotas
"""

from typing import Dict, List, Optional
from datetime import datetime, timedelta
from collections import defaultdict
from metering_models import UsageRecord, Quota, CostRate, ResourceType
import json
from pathlib import Path

class MeteringService:
    """Service for tracking costs and enforcing quotas"""

    def __init__(self, storage_path: Optional[Path] = None):
        self.storage_path = storage_path or Path("metering_data.json")
        self.usage_records: List[UsageRecord] = []
        self.quotas: Dict[str, Dict[ResourceType, Quota]] = defaultdict(dict)
        self.cost_rates: Dict[ResourceType, CostRate] = self._default_rates()
        self.load_data()

    def _default_rates(self) -> Dict[ResourceType, CostRate]:
        """Default cost rates"""
        return {
            ResourceType.API_CALL: CostRate(ResourceType.API_CALL, 0.001),
            ResourceType.COMPUTE_TIME: CostRate(ResourceType.COMPUTE_TIME, 0.10),
            ResourceType.STORAGE: CostRate(ResourceType.STORAGE, 0.023),
            ResourceType.BANDWIDTH: CostRate(ResourceType.BANDWIDTH, 0.09),
            ResourceType.DATABASE_QUERY: CostRate(ResourceType.DATABASE_QUERY, 0.0001),
        }

    def record_usage(self, user_id: str, resource_type: ResourceType,
                    quantity: float, metadata: Optional[Dict] = None) -> UsageRecord:
        """Record resource usage"""
        cost = self.cost_rates[resource_type].calculate_cost(quantity)

        record = UsageRecord(
            user_id=user_id,
            resource_type=resource_type,
            quantity=quantity,
            cost=cost,
            timestamp=datetime.now(),
            metadata=metadata
        )

        self.usage_records.append(record)

        # Update quota usage
        if user_id in self.quotas and resource_type in self.quotas[user_id]:
            self.quotas[user_id][resource_type].current_usage += quantity

        self.save_data()
        return record

    def set_quota(self, user_id: str, resource_type: ResourceType,
                  limit: float, period: str = "monthly"):
        """Set quota for a user"""
        if user_id not in self.quotas:
            self.quotas[user_id] = {}

        self.quotas[user_id][resource_type] = Quota(
            user_id=user_id,
            resource_type=resource_type,
            limit=limit,
            period=period
        )
        self.save_data()

    def check_quota(self, user_id: str, resource_type: ResourceType,
                   quantity: float) -> bool:
        """Check if usage would exceed quota"""
        if user_id not in self.quotas or resource_type not in self.quotas[user_id]:
            return True  # No quota set, allow

        quota = self.quotas[user_id][resource_type]
        return (quota.current_usage + quantity) <= quota.limit

    def get_usage_summary(self, user_id: str,
                         start_date: Optional[datetime] = None) -> Dict:
        """Get usage summary for a user"""
        if start_date is None:
            start_date = datetime.now() - timedelta(days=30)

        user_records = [r for r in self.usage_records
                       if r.user_id == user_id and r.timestamp >= start_date]

        total_cost = sum(r.cost for r in user_records)

        by_resource = defaultdict(lambda: {"quantity": 0, "cost": 0})
        for record in user_records:
            by_resource[record.resource_type.value]["quantity"] += record.quantity
            by_resource[record.resource_type.value]["cost"] += record.cost

        return {
            "user_id": user_id,
            "period_start": start_date.isoformat(),
            "period_end": datetime.now().isoformat(),
            "total_cost": total_cost,
            "total_records": len(user_records),
            "by_resource": dict(by_resource)
        }

    def get_quota_status(self, user_id: str) -> Dict:
        """Get quota status for a user"""
        if user_id not in self.quotas:
            return {"user_id": user_id, "quotas": {}}

        status = {}
        for resource_type, quota in self.quotas[user_id].items():
            status[resource_type.value] = {
                "limit": quota.limit,
                "current_usage": quota.current_usage,
                "remaining": quota.remaining(),
                "usage_percentage": quota.usage_percentage(),
                "exceeded": quota.is_exceeded()
            }

        return {"user_id": user_id, "quotas": status}

    def reset_quotas(self, user_id: Optional[str] = None):
        """Reset quota usage counters"""
        if user_id:
            if user_id in self.quotas:
                for quota in self.quotas[user_id].values():
                    quota.current_usage = 0.0
        else:
            for user_quotas in self.quotas.values():
                for quota in user_quotas.values():
                    quota.current_usage = 0.0

        self.save_data()

    def save_data(self):
        """Save metering data to disk"""
        data = {
            "usage_records": [r.to_dict() for r in self.usage_records[-1000:]],  # Keep last 1000
            "quotas": {
                user_id: {
                    rt.value: {
                        "limit": q.limit,
                        "period": q.period,
                        "current_usage": q.current_usage
                    }
                    for rt, q in quotas.items()
                }
                for user_id, quotas in self.quotas.items()
            }
        }

        with open(self.storage_path, 'w') as f:
            json.dump(data, f, indent=2)

    def load_data(self):
        """Load metering data from disk"""
        if not self.storage_path.exists():
            return

        try:
            with open(self.storage_path) as f:
                data = json.load(f)

            # Load quotas
            for user_id, quotas in data.get("quotas", {}).items():
                for rt_str, quota_data in quotas.items():
                    rt = ResourceType(rt_str)
                    self.quotas[user_id][rt] = Quota(
                        user_id=user_id,
                        resource_type=rt,
                        limit=quota_data["limit"],
                        period=quota_data["period"],
                        current_usage=quota_data["current_usage"]
                    )
        except Exception as e:
            print(f"Warning: Could not load metering data: {e}")
'''

        with open(service_file, "w") as f:
            f.write(code)

        print(f"✓ Created metering service: {service_file}")
        return service_file

    def create_metering_middleware(self):
        """Create middleware for automatic metering"""
        middleware_file = self.q4_root / "metering_middleware.py"

        code = '''"""
Metering Middleware
Automatically tracks API usage and enforces quotas
"""

from functools import wraps
from typing import Callable
from metering_service import MeteringService
from metering_models import ResourceType
import time

class MeteringMiddleware:
    """Middleware for automatic resource metering"""

    def __init__(self, metering_service: MeteringService):
        self.service = metering_service

    def meter_api_call(self, user_id: str):
        """Decorator to meter API calls"""
        def decorator(func: Callable):
            @wraps(func)
            def wrapper(*args, **kwargs):
                # Check quota before execution
                if not self.service.check_quota(user_id, ResourceType.API_CALL, 1):
                    raise Exception(f"API call quota exceeded for user {user_id}")

                # Execute function
                result = func(*args, **kwargs)

                # Record usage
                self.service.record_usage(
                    user_id=user_id,
                    resource_type=ResourceType.API_CALL,
                    quantity=1,
                    metadata={"function": func.__name__}
                )

                return result
            return wrapper
        return decorator

    def meter_compute_time(self, user_id: str):
        """Decorator to meter compute time"""
        def decorator(func: Callable):
            @wraps(func)
            def wrapper(*args, **kwargs):
                start_time = time.time()

                result = func(*args, **kwargs)

                elapsed = time.time() - start_time

                # Record usage (in seconds)
                self.service.record_usage(
                    user_id=user_id,
                    resource_type=ResourceType.COMPUTE_TIME,
                    quantity=elapsed,
                    metadata={"function": func.__name__, "elapsed_seconds": elapsed}
                )

                return result
            return wrapper
        return decorator

# Example usage
if __name__ == "__main__":
    service = MeteringService()
    middleware = MeteringMiddleware(service)

    # Set quotas
    service.set_quota("user123", ResourceType.API_CALL, 1000, "monthly")
    service.set_quota("user123", ResourceType.COMPUTE_TIME, 3600, "monthly")

    @middleware.meter_api_call("user123")
    @middleware.meter_compute_time("user123")
    def example_api_function():
        time.sleep(0.1)
        return {"status": "success"}

    # Call the function
    result = example_api_function()

    # Check usage
    summary = service.get_usage_summary("user123")
    print(f"Usage summary: {summary}")

    quota_status = service.get_quota_status("user123")
    print(f"Quota status: {quota_status}")
'''

        with open(middleware_file, "w") as f:
            f.write(code)

        print(f"✓ Created metering middleware: {middleware_file}")
        return middleware_file

    def create_metering_dashboard(self):
        """Create simple dashboard for viewing metrics"""
        dashboard_file = self.q4_root / "metering_dashboard.py"

        code = '''"""
Cost Metering Dashboard
Simple CLI dashboard for viewing usage and quotas
"""

from metering_service import MeteringService
from metering_models import ResourceType
from datetime import datetime, timedelta

class MeteringDashboard:
    """CLI dashboard for metering data"""

    def __init__(self, service: MeteringService):
        self.service = service

    def display_user_summary(self, user_id: str):
        """Display usage summary for a user"""
        print("="*60)
        print(f"Usage Summary for {user_id}")
        print("="*60)

        summary = self.service.get_usage_summary(user_id)

        print(f"Period: {summary['period_start']} to {summary['period_end']}")
        print(f"Total Cost: ${summary['total_cost']:.4f}")
        print(f"Total Records: {summary['total_records']}")

        print("\\nBy Resource Type:")
        for resource, data in summary['by_resource'].items():
            print(f"  {resource}:")
            print(f"    Quantity: {data['quantity']:.2f}")
            print(f"    Cost: ${data['cost']:.4f}")

        print("\\n" + "="*60)
        print("Quota Status")
        print("="*60)

        quota_status = self.service.get_quota_status(user_id)

        if not quota_status['quotas']:
            print("No quotas set")
        else:
            for resource, status in quota_status['quotas'].items():
                exceeded = "⚠ EXCEEDED" if status['exceeded'] else "✓ OK"
                print(f"{resource}: {exceeded}")
                print(f"  Usage: {status['current_usage']:.2f} / {status['limit']:.2f}")
                print(f"  Remaining: {status['remaining']:.2f}")
                print(f"  Percentage: {status['usage_percentage']:.1f}%")

if __name__ == "__main__":
    service = MeteringService()
    dashboard = MeteringDashboard(service)

    # Example: Display summary for a user
    dashboard.display_user_summary("user123")
'''

        with open(dashboard_file, "w") as f:
            f.write(code)

        print(f"✓ Created metering dashboard: {dashboard_file}")
        return dashboard_file

    def generate_report(self):
        """Generate setup completion report"""
        report = {
            "task": "Cost Metering & Quotas",
            "status": "Completed",
            "timestamp": datetime.now().isoformat(),
            "components": [
                "Metering data models (metering_models.py)",
                "Metering service (metering_service.py)",
                "Metering middleware (metering_middleware.py)",
                "Metering dashboard (metering_dashboard.py)",
            ],
            "features": [
                "Resource usage tracking",
                "Cost calculation",
                "Quota management",
                "Usage summaries",
                "Automatic metering via decorators",
                "CLI dashboard",
            ],
            "resource_types": [
                "API calls",
                "Compute time",
                "Storage",
                "Bandwidth",
                "Database queries",
            ],
            "next_steps": [
                "Import MeteringService in your application",
                "Set quotas for users: service.set_quota(user_id, ResourceType.API_CALL, 1000)",
                "Use decorators to meter functions: @middleware.meter_api_call(user_id)",
                "View usage: python metering_dashboard.py",
                "Integrate with billing system",
            ],
        }

        report_file = Path(__file__).parent / "metering_setup_report.json"
        with open(report_file, "w") as f:
            json.dump(report, f, indent=2)

        print(f"\n✓ Setup report saved: {report_file}")
        return report


def main():
    """Main setup execution"""
    print("=" * 60)
    print("Cost Metering & Quotas Setup")
    print("=" * 60)

    setup = MeteringSetup()

    # Create all components
    setup.create_metering_models()
    setup.create_metering_service()
    setup.create_metering_middleware()
    setup.create_metering_dashboard()

    # Generate report
    report = setup.generate_report()

    print("\n" + "=" * 60)
    print("✓ Cost Metering & Quotas - COMPLETED")
    print("=" * 60)
    print("\nNext Steps:")
    for step in report["next_steps"]:
        print(f"  • {step}")

    return 0


if __name__ == "__main__":
    sys.exit(main())
