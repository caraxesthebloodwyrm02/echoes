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
SQLAlchemy ORM Models for Q4 Roadmap
"""

from datetime import datetime

from sqlalchemy import (
    CheckConstraint,
    Column,
    Date,
    DateTime,
    ForeignKey,
    Integer,
    Numeric,
    String,
    Text,
)
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

Base = declarative_base()


class RoadmapItem(Base):
    """Roadmap item model"""

    __tablename__ = "roadmap_items"

    id = Column(Integer, primary_key=True)
    title = Column(String(255), nullable=False)
    phase = Column(String(50), nullable=False)
    status = Column(String(50), nullable=False)
    priority = Column(String(20), nullable=False)
    owner = Column(String(100), nullable=False)
    start_date = Column(Date, nullable=False)
    due_date = Column(Date, nullable=False)
    progress = Column(Integer, default=0)
    objective = Column(Text)
    notes = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    audit_logs = relationship("RoadmapAudit", back_populates="roadmap_item")

    __table_args__ = (
        CheckConstraint(
            "progress >= 0 AND progress <= 100", name="check_progress_range"
        ),
    )

    def to_dict(self):
        """Convert to dictionary"""
        return {
            "id": self.id,
            "title": self.title,
            "phase": self.phase,
            "status": self.status,
            "priority": self.priority,
            "owner": self.owner,
            "start_date": self.start_date.isoformat() if self.start_date else None,
            "due_date": self.due_date.isoformat() if self.due_date else None,
            "progress": self.progress,
            "objective": self.objective,
            "notes": self.notes,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }


class RoadmapAudit(Base):
    """Audit log for roadmap changes"""

    __tablename__ = "roadmap_audit"

    id = Column(Integer, primary_key=True)
    roadmap_item_id = Column(Integer, ForeignKey("roadmap_items.id"))
    action = Column(String(50), nullable=False)
    old_value = Column(JSONB)
    new_value = Column(JSONB)
    changed_by = Column(String(100))
    changed_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    roadmap_item = relationship("RoadmapItem", back_populates="audit_logs")


class RoadmapMetrics(Base):
    """Historical metrics snapshots"""

    __tablename__ = "roadmap_metrics"

    id = Column(Integer, primary_key=True)
    metric_date = Column(Date, nullable=False)
    total_items = Column(Integer)
    completed_items = Column(Integer)
    in_progress_items = Column(Integer)
    not_started_items = Column(Integer)
    completion_rate = Column(Numeric(5, 2))
    created_at = Column(DateTime, default=datetime.utcnow)
