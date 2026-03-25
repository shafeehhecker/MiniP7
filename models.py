"""
Database models for Mini-P7 using SQLAlchemy + SQLite.
"""
from sqlalchemy import Boolean, Column, Integer, String
from sqlalchemy.orm import declarative_base

Base = declarative_base()


class ActivityRecord(Base):
    """Persistent storage for an Activity."""
    __tablename__ = "activities"   # FIX: db.py was querying 'activity_record' — unified here

    id           = Column(String,  primary_key=True)
    name         = Column(String,  nullable=False)
    duration     = Column(Integer, nullable=False, default=0)
    predecessors = Column(String,  default="")   # comma-separated IDs
    resource     = Column(String,  default="")   # FIX: was missing
    description  = Column(String,  default="")   # FIX: was missing

    # CPM results (cached after last schedule run)
    ES          = Column(Integer, default=0)
    EF          = Column(Integer, default=0)
    LS          = Column(Integer, default=0)
    LF          = Column(Integer, default=0)
    total_float = Column(Integer, default=0)
    free_float  = Column(Integer, default=0)   # FIX: was missing
    is_critical = Column(Boolean, default=False)
