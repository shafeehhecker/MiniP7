"""
Database access layer for Mini-P7.
Provides simple CRUD operations for Activity records.
"""
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from typing import List, Dict, Optional

from models import Base, ActivityRecord
from activity import Activity


_engine = None
_SessionLocal = None


def init_db(db_path: str = "mini_p6.db"):
    """Initialize the database (create tables if needed)."""
    global _engine, _SessionLocal
    _engine = create_engine(f"sqlite:///{db_path}", echo=False)
    Base.metadata.create_all(_engine)
    _SessionLocal = sessionmaker(bind=_engine)


def get_session() -> Session:
    if _SessionLocal is None:
        init_db()
    return _SessionLocal()


# ------------------------------------------------------------------
# CRUD helpers
# ------------------------------------------------------------------

def load_all_activities() -> Dict[str, Activity]:
    """
    Load all activities from DB and return as {id: Activity} dict.

    Performance: uses a single query with row mapping for direct dict creation.
    """
    with get_session() as session:
        # Use execute with row mapping for slightly faster conversion
        rows = session.execute(
            "SELECT id, name, duration, predecessors, ES, EF, LS, LF, total_float, is_critical "
            "FROM activity_record"
        ).mappings().all()
        result = {}
        for row in rows:
            # Convert predecessors string to tuple (same as Activity's expected format)
            preds = tuple(p.strip() for p in row["predecessors"].split(",") if p.strip())
            result[row["id"]] = Activity(
                id=row["id"],
                name=row["name"],
                duration=row["duration"],
                predecessors=preds,
                ES=row["ES"],
                EF=row["EF"],
                LS=row["LS"],
                LF=row["LF"],
                total_float=row["total_float"],
                is_critical=row["is_critical"],
            )
        return result


def save_activity(activity: Activity):
    """
    Insert or update a single activity.

    Uses session.merge to combine the check and write in one operation.
    """
    with get_session() as session:
        # Convert to record and merge (insert or update based on primary key)
        record = _activity_to_record(activity)
        session.merge(record)
        session.commit()


def save_all_activities(activities: Dict[str, Activity]):
    """
    Bulk save / update all activities (used after CPM run).

    Performance: loads all existing IDs in one query, then uses
    bulk_insert_mappings / bulk_update_mappings to minimise round trips.
    """
    with get_session() as session:
        # 1. Get all existing IDs in one go
        existing_ids = {row[0] for row in session.query(ActivityRecord.id).all()}

        # 2. Separate activities into inserts and updates
        insert_mappings = []
        update_mappings = []
        for act in activities.values():
            mapping = {
                "id": act.id,
                "name": act.name,
                "duration": act.duration,
                "predecessors": ",".join(act.predecessors),
                "ES": act.ES,
                "EF": act.EF,
                "LS": act.LS,
                "LF": act.LF,
                "total_float": act.total_float,
                "is_critical": act.is_critical,
            }
            if act.id in existing_ids:
                update_mappings.append(mapping)
            else:
                insert_mappings.append(mapping)

        # 3. Perform bulk operations
        if insert_mappings:
            session.bulk_insert_mappings(ActivityRecord, insert_mappings)
        if update_mappings:
            # Bulk update requires that we specify which columns to update
            # Since we need to update all columns except primary key, we use
            # bulk_update_mappings with all fields.
            session.bulk_update_mappings(ActivityRecord, update_mappings)

        session.commit()


def delete_activity(activity_id: str):
    """Remove an activity from the database."""
    with get_session() as session:
        record = session.get(ActivityRecord, activity_id)
        if record:
            session.delete(record)
            session.commit()


def activity_id_exists(activity_id: str) -> bool:
    with get_session() as session:
        # Use exists subquery for efficiency
        return session.query(ActivityRecord).filter(ActivityRecord.id == activity_id).first() is not None


# ------------------------------------------------------------------
# Conversion helpers (unchanged in behaviour, but adapted to tuple)
# ------------------------------------------------------------------

def _record_to_activity(r: ActivityRecord) -> Activity:
    # Convert to tuple (matching improved Activity)
    preds = tuple(p.strip() for p in r.predecessors.split(",") if p.strip())
    return Activity(
        id=r.id,
        name=r.name,
        duration=r.duration,
        predecessors=preds,
        ES=r.ES,
        EF=r.EF,
        LS=r.LS,
        LF=r.LF,
        total_float=r.total_float,
        is_critical=r.is_critical,
    )


def _activity_to_record(a: Activity) -> ActivityRecord:
    # Join tuple into a comma‑separated string
    return ActivityRecord(
        id=a.id,
        name=a.name,
        duration=a.duration,
        predecessors=",".join(a.predecessors),
        ES=a.ES,
        EF=a.EF,
        LS=a.LS,
        LF=a.LF,
        total_float=a.total_float,
        is_critical=a.is_critical,
    )


def _update_record(record: ActivityRecord, a: Activity):
    # (Kept for internal use if needed, but not used in current functions)
    record.name = a.name
    record.duration = a.duration
    record.predecessors = ",".join(a.predecessors)
    record.ES = a.ES
    record.EF = a.EF
    record.LS = a.LS
    record.LF = a.LF
    record.total_float = a.total_float
    record.is_critical = a.is_critical
