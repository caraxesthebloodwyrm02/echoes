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
Database Manager for Q4 Roadmap
Provides high-level database operations
"""

import os
from datetime import date
from typing import Any, Dict, List, Optional

from models import Base, RoadmapItem, RoadmapMetrics
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker


class DatabaseManager:
    """Manages database connections and operations"""

    def __init__(self, database_url: Optional[str] = None):
        self.database_url = database_url or os.getenv(
            "DATABASE_URL",
            "postgresql://q4_user:q4_secure_pass@localhost:5432/q4_roadmap",
        )
        self.engine = create_engine(self.database_url)
        self.SessionLocal = sessionmaker(bind=self.engine)

    def create_tables(self):
        """Create all tables"""
        Base.metadata.create_all(self.engine)

    def get_session(self) -> Session:
        """Get a new database session"""
        return self.SessionLocal()

    def add_roadmap_item(self, item_data: Dict[str, Any]) -> RoadmapItem:
        """Add a new roadmap item"""
        session = self.get_session()
        try:
            item = RoadmapItem(**item_data)
            session.add(item)
            session.commit()
            session.refresh(item)
            return item
        finally:
            session.close()

    def get_all_items(self) -> List[RoadmapItem]:
        """Get all roadmap items"""
        session = self.get_session()
        try:
            return session.query(RoadmapItem).all()
        finally:
            session.close()

    def get_item_by_id(self, item_id: int) -> Optional[RoadmapItem]:
        """Get a specific roadmap item"""
        session = self.get_session()
        try:
            return session.query(RoadmapItem).filter(RoadmapItem.id == item_id).first()
        finally:
            session.close()

    def update_item(
        self, item_id: int, updates: Dict[str, Any]
    ) -> Optional[RoadmapItem]:
        """Update a roadmap item"""
        session = self.get_session()
        try:
            item = session.query(RoadmapItem).filter(RoadmapItem.id == item_id).first()
            if item:
                for key, value in updates.items():
                    setattr(item, key, value)
                session.commit()
                session.refresh(item)
            return item
        finally:
            session.close()

    def delete_item(self, item_id: int) -> bool:
        """Delete a roadmap item"""
        session = self.get_session()
        try:
            item = session.query(RoadmapItem).filter(RoadmapItem.id == item_id).first()
            if item:
                session.delete(item)
                session.commit()
                return True
            return False
        finally:
            session.close()

    def get_metrics(self) -> Dict[str, Any]:
        """Get current roadmap metrics"""
        session = self.get_session()
        try:
            items = session.query(RoadmapItem).all()
            total = len(items)
            completed = sum(1 for item in items if item.status == "Completed")
            in_progress = sum(1 for item in items if item.status == "In Progress")
            not_started = sum(1 for item in items if item.status == "Not Started")

            return {
                "total_items": total,
                "completed": completed,
                "in_progress": in_progress,
                "not_started": not_started,
                "completion_rate": (
                    round(100 * completed / total, 2) if total > 0 else 0
                ),
            }
        finally:
            session.close()

    def snapshot_metrics(self):
        """Save current metrics snapshot"""
        session = self.get_session()
        try:
            metrics = self.get_metrics()
            snapshot = RoadmapMetrics(
                metric_date=date.today(),
                total_items=metrics["total_items"],
                completed_items=metrics["completed"],
                in_progress_items=metrics["in_progress"],
                not_started_items=metrics["not_started"],
                completion_rate=metrics["completion_rate"],
            )
            session.add(snapshot)
            session.commit()
        finally:
            session.close()
