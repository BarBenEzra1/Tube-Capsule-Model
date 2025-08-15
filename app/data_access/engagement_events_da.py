from typing import List
from sqlalchemy.orm import Session
from sqlalchemy import and_

from app.database.models import EngagementEvent


class EngagementEventsDataAccess:
    """Data access class for handling engagement events data"""
    
    def __init__(self, db: Session):
        self.db = db

    def log_event(self, simulation_id: str, system_id: int, timestamp_s: float, event: str, **event_data) -> None:
        """Log a simulation event to the database"""
        
        force_applied_n = event_data.get('force_applied_n')
        energy_consumed_j = event_data.get('energy_consumed_j')
        acceleration_mps2 = event_data.get('acceleration_mps2')

        event = EngagementEvent(
            simulation_id=simulation_id,
            system_id=system_id,
            timestamp_s=round(timestamp_s, 4),
            event=event,
            coil_id=event_data.get('coil_id'),
            position_m=event_data.get('position_m'),
            velocity_mps=event_data.get('velocity_mps'),
            acceleration_mps2=acceleration_mps2 if acceleration_mps2 is not None else 0,
            acceleration_duration_s=event_data.get('acceleration_duration_s'),
            acceleration_segment_length_m=event_data.get('acceleration_segment_length_m'),
            force_applied_n=force_applied_n if force_applied_n is not None else 0,
            energy_consumed_j=energy_consumed_j if energy_consumed_j is not None else 0
        )
        
        self.db.add(event)
        self.db.commit()
    
        
    def get_events(self, simulation_id: str) -> List[EngagementEvent]:
        """Get all events for a simulation run ordered by timestamp"""
        return self.db.query(EngagementEvent).filter(
            EngagementEvent.simulation_id == simulation_id
        ).order_by(EngagementEvent.timestamp_s).all()
    

    def get_events_by_event(self, simulation_id: str, event: str) -> List[EngagementEvent]:
        """Get events of a specific type for a simulation run"""
        return self.db.query(EngagementEvent).filter(
            and_(
                EngagementEvent.simulation_id == simulation_id,
                EngagementEvent.event == event
            )
        ).order_by(EngagementEvent.timestamp_s).all()
    

    def get_events_by_coil_id(self, simulation_id: str, coil_id: int) -> List[EngagementEvent]:
        """Get all events related to a specific coil"""
        return self.db.query(EngagementEvent).filter(
            and_(
                EngagementEvent.simulation_id == simulation_id,
                EngagementEvent.coil_id == coil_id
            )
        ).order_by(EngagementEvent.timestamp_s).all()