#!/usr/bin/env python3
"""
Database Persistence Layer Setup
Automates Task: "Database Persistence Layer" - PostgreSQL setup with data models
"""

import json
import os
import sys
from datetime import datetime
from pathlib import Path


class DatabaseSetup:
    """Automates database persistence layer setup"""

    def __init__(self):
        self.db_name = os.getenv("DB_NAME", "q4_roadmap")
        self.db_user = os.getenv("DB_USER", "q4_user")
        self.db_password = os.getenv("DB_PASSWORD", "q4_secure_pass")
        self.db_host = os.getenv("DB_HOST", "localhost")
        self.db_port = os.getenv("DB_PORT", "5432")

    def create_env_file(self):
        """Create .env file with database credentials"""
        env_file = Path(__file__).parent.parent / ".env.db"

        with open(env_file, "w") as f:
            f.write(
                f"""# Database Configuration
DB_NAME={self.db_name}
DB_USER={self.db_user}
DB_PASSWORD={self.db_password}
DB_HOST={self.db_host}
DB_PORT={self.db_port}
DATABASE_URL=postgresql://{self.db_user}:{self.db_password}@{self.db_host}:{self.db_port}/{self.db_name}
"""
            )

        print(f"✓ Created database environment file: {env_file}")

    def create_schema_sql(self):
        """Generate SQL schema for Q4 roadmap"""
        schema_file = Path(__file__).parent.parent / "schema.sql"

        schema = """-- Q4 Roadmap Database Schema

CREATE TABLE IF NOT EXISTS roadmap_items (
    id SERIAL PRIMARY KEY,
    title VARCHAR(255) NOT NULL,
    phase VARCHAR(50) NOT NULL,
    status VARCHAR(50) NOT NULL,
    priority VARCHAR(20) NOT NULL,
    owner VARCHAR(100) NOT NULL,
    start_date DATE NOT NULL,
    due_date DATE NOT NULL,
    progress INTEGER DEFAULT 0 CHECK (progress >= 0 AND progress <= 100),
    objective TEXT,
    notes TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_roadmap_status ON roadmap_items(status);
CREATE INDEX idx_roadmap_phase ON roadmap_items(phase);
CREATE INDEX idx_roadmap_priority ON roadmap_items(priority);
CREATE INDEX idx_roadmap_owner ON roadmap_items(owner);

-- Audit log table
CREATE TABLE IF NOT EXISTS roadmap_audit (
    id SERIAL PRIMARY KEY,
    roadmap_item_id INTEGER REFERENCES roadmap_items(id),
    action VARCHAR(50) NOT NULL,
    old_value JSONB,
    new_value JSONB,
    changed_by VARCHAR(100),
    changed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Metrics table
CREATE TABLE IF NOT EXISTS roadmap_metrics (
    id SERIAL PRIMARY KEY,
    metric_date DATE NOT NULL,
    total_items INTEGER,
    completed_items INTEGER,
    in_progress_items INTEGER,
    not_started_items INTEGER,
    completion_rate DECIMAL(5,2),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Function to update updated_at timestamp
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Trigger to auto-update updated_at
CREATE TRIGGER update_roadmap_items_updated_at
    BEFORE UPDATE ON roadmap_items
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

-- View for dashboard metrics
CREATE OR REPLACE VIEW dashboard_metrics AS
SELECT
    COUNT(*) as total_items,
    SUM(CASE WHEN status = 'Completed' THEN 1 ELSE 0 END) as completed,
    SUM(CASE WHEN status = 'In Progress' THEN 1 ELSE 0 END) as in_progress,
    SUM(CASE WHEN status = 'Not Started' THEN 1 ELSE 0 END) as not_started,
    ROUND(100.0 * SUM(CASE WHEN status = 'Completed' THEN 1 ELSE 0 END) / COUNT(*), 2) as completion_rate
FROM roadmap_items;

-- View for phase breakdown
CREATE OR REPLACE VIEW phase_breakdown AS
SELECT
    phase,
    COUNT(*) as total,
    SUM(CASE WHEN status = 'Completed' THEN 1 ELSE 0 END) as completed,
    SUM(CASE WHEN status = 'In Progress' THEN 1 ELSE 0 END) as in_progress,
    SUM(CASE WHEN status = 'Not Started' THEN 1 ELSE 0 END) as not_started
FROM roadmap_items
GROUP BY phase;

COMMENT ON TABLE roadmap_items IS 'Q4 roadmap tracking with Drucker principles';
COMMENT ON TABLE roadmap_audit IS 'Audit trail for all roadmap changes';
COMMENT ON TABLE roadmap_metrics IS 'Historical metrics snapshots';
"""

        with open(schema_file, "w") as f:
            f.write(schema)

        print(f"✓ Created database schema: {schema_file}")
        return schema_file

    def create_orm_models(self):
        """Create SQLAlchemy ORM models"""
        models_file = Path(__file__).parent.parent / "models.py"

        models_code = '''"""
SQLAlchemy ORM Models for Q4 Roadmap
"""

from datetime import datetime, date
from typing import Optional
from sqlalchemy import Column, Integer, String, Date, Text, DateTime, Numeric, ForeignKey, CheckConstraint
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import JSONB

Base = declarative_base()

class RoadmapItem(Base):
    """Roadmap item model"""
    __tablename__ = 'roadmap_items'

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
        CheckConstraint('progress >= 0 AND progress <= 100', name='check_progress_range'),
    )

    def to_dict(self):
        """Convert to dictionary"""
        return {
            'id': self.id,
            'title': self.title,
            'phase': self.phase,
            'status': self.status,
            'priority': self.priority,
            'owner': self.owner,
            'start_date': self.start_date.isoformat() if self.start_date else None,
            'due_date': self.due_date.isoformat() if self.due_date else None,
            'progress': self.progress,
            'objective': self.objective,
            'notes': self.notes,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }

class RoadmapAudit(Base):
    """Audit log for roadmap changes"""
    __tablename__ = 'roadmap_audit'

    id = Column(Integer, primary_key=True)
    roadmap_item_id = Column(Integer, ForeignKey('roadmap_items.id'))
    action = Column(String(50), nullable=False)
    old_value = Column(JSONB)
    new_value = Column(JSONB)
    changed_by = Column(String(100))
    changed_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    roadmap_item = relationship("RoadmapItem", back_populates="audit_logs")

class RoadmapMetrics(Base):
    """Historical metrics snapshots"""
    __tablename__ = 'roadmap_metrics'

    id = Column(Integer, primary_key=True)
    metric_date = Column(Date, nullable=False)
    total_items = Column(Integer)
    completed_items = Column(Integer)
    in_progress_items = Column(Integer)
    not_started_items = Column(Integer)
    completion_rate = Column(Numeric(5, 2))
    created_at = Column(DateTime, default=datetime.utcnow)
'''

        with open(models_file, "w") as f:
            f.write(models_code)

        print(f"✓ Created ORM models: {models_file}")
        return models_file

    def create_db_manager(self):
        """Create database manager utility"""
        manager_file = Path(__file__).parent.parent / "db_manager.py"

        manager_code = '''"""
Database Manager for Q4 Roadmap
Provides high-level database operations
"""

import os
from typing import List, Optional, Dict, Any
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from models import Base, RoadmapItem, RoadmapAudit, RoadmapMetrics
from datetime import date, datetime

class DatabaseManager:
    """Manages database connections and operations"""

    def __init__(self, database_url: Optional[str] = None):
        self.database_url = database_url or os.getenv(
            "DATABASE_URL",
            "postgresql://q4_user:q4_secure_pass@localhost:5432/q4_roadmap"
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

    def update_item(self, item_id: int, updates: Dict[str, Any]) -> Optional[RoadmapItem]:
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
            completed = sum(1 for item in items if item.status == 'Completed')
            in_progress = sum(1 for item in items if item.status == 'In Progress')
            not_started = sum(1 for item in items if item.status == 'Not Started')

            return {
                'total_items': total,
                'completed': completed,
                'in_progress': in_progress,
                'not_started': not_started,
                'completion_rate': round(100 * completed / total, 2) if total > 0 else 0
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
                total_items=metrics['total_items'],
                completed_items=metrics['completed'],
                in_progress_items=metrics['in_progress'],
                not_started_items=metrics['not_started'],
                completion_rate=metrics['completion_rate']
            )
            session.add(snapshot)
            session.commit()
        finally:
            session.close()
'''

        with open(manager_file, "w") as f:
            f.write(manager_code)

        print(f"✓ Created database manager: {manager_file}")
        return manager_file

    def generate_report(self):
        """Generate setup completion report"""
        report = {
            "task": "Database Persistence Layer",
            "status": "Completed",
            "timestamp": datetime.now().isoformat(),
            "components": [
                "Environment configuration (.env.db)",
                "SQL schema (schema.sql)",
                "ORM models (models.py)",
                "Database manager (db_manager.py)",
            ],
            "database_config": {
                "name": self.db_name,
                "user": self.db_user,
                "host": self.db_host,
                "port": self.db_port,
            },
            "next_steps": [
                "Install PostgreSQL if not already installed",
                "Create database: createdb " + self.db_name,
                "Create user: createuser " + self.db_user,
                "Run schema: psql -d " + self.db_name + " -f schema.sql",
                "Test connection: python -c 'from db_manager import DatabaseManager; db = DatabaseManager(); db.create_tables()'",
            ],
        }

        report_file = Path(__file__).parent / "database_setup_report.json"
        with open(report_file, "w") as f:
            json.dump(report, f, indent=2)

        print(f"\n✓ Setup report saved: {report_file}")
        return report


def main():
    """Main setup execution"""
    print("=" * 60)
    print("Database Persistence Layer Setup")
    print("=" * 60)

    setup = DatabaseSetup()

    # Create all components
    setup.create_env_file()
    setup.create_schema_sql()
    setup.create_orm_models()
    setup.create_db_manager()

    # Generate report
    report = setup.generate_report()

    print("\n" + "=" * 60)
    print("✓ Database Persistence Layer - COMPLETED")
    print("=" * 60)
    print("\nNext Steps:")
    for step in report["next_steps"]:
        print(f"  • {step}")

    return 0


if __name__ == "__main__":
    sys.exit(main())
