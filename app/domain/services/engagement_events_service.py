from app.data_access.engagement_events_da import EngagementEventsDataAccess
from app.database.config import SessionLocal
from app.database.models import EngagementEvent

_current_simulation_id: str | None = None
_engagement_events_data_access: EngagementEventsDataAccess | None = None
_current_system_id: int | None = None


def engagement_event_log(timestamp_s: float, event: str, **kv) -> None:
    """
    Log a simulation event to the PostgreSQL database.
    
    Args:
        timestamp_s: Time in seconds
        event: Event type/name
        **kv: Additional event data as key-value pairs
    """
    global _current_simulation_id, _current_system_id, _engagement_events_data_access
    
    if not _current_simulation_id or not _engagement_events_data_access:
        return
    
    try:
        _engagement_events_data_access.log_event(
            simulation_id=_current_simulation_id,
            system_id=_current_system_id,
            timestamp_s=timestamp_s,
            event=event,
            **kv
        )
    except Exception as e:
        print(f"Database logging failed: {e}")


def get_engagement_events(simulation_id: str, event: str | None = None, coil_id: int | None = None) -> list[EngagementEvent]:
    global _engagement_events_data_access
    
    if not _engagement_events_data_access:
        return []
    
    if event:
        return _engagement_events_data_access.get_events_by_event(simulation_id, event)
    elif coil_id:
        return _engagement_events_data_access.get_events_by_coil_id(simulation_id, coil_id)
    else:
        return _engagement_events_data_access.get_events(simulation_id)


def get_engagement_events_data_access() -> EngagementEventsDataAccess | None:
    """Get the current log data access instance"""
    global _engagement_events_data_access
    
    return _engagement_events_data_access


def initialize_engagement_events() -> EngagementEventsDataAccess:
    """Create a new log data access instance"""
    global _engagement_events_data_access
    
    db = SessionLocal()
    _engagement_events_data_access = EngagementEventsDataAccess(db) 
    return _engagement_events_data_access


def set_current_simulation_id(simulation_id: str) -> None:
    """Set the current simulation ID"""
    global _current_simulation_id
    _current_simulation_id = simulation_id


def set_current_system_id(system_id: int) -> None:
    """Set the current system ID"""
    global _current_system_id
    _current_system_id = system_id