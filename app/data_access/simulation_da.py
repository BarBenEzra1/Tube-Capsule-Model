from datetime import datetime, timezone
from typing import List
from sqlalchemy.orm import Session
from sqlalchemy import desc
import uuid

from app.database.models import SimulationRun


class SimulationRunDataAccess:
    """Data access class for handling simulation run data"""
    
    def __init__(self, db: Session):
        self.db = db
    
    def start_simulation_run(self, system_id: int) -> str:
        """Start a new simulation run and return the simulation ID"""
        simulation_id = f"sim_{datetime.now(timezone.utc).strftime('%Y%m%d_%H%M%S')}_{uuid.uuid4().hex[:8]}"
        
        simulation_run = SimulationRun(
            id=simulation_id,
            system_id=system_id,
            started_at=datetime.now(timezone.utc),
            status="running"
        )
        
        self.db.add(simulation_run)
        self.db.commit()
        
        return simulation_id
        
    
    def complete_simulation_run(self, simulation_id: str, total_travel_time: float, final_velocity: float, total_energy_consumed: float = None) -> None:
        """Mark a simulation run as completed and update summary statistics"""
        
        simulation_run = self.db.query(SimulationRun).filter(
            SimulationRun.id == simulation_id
        ).first()
        
        if simulation_run:
            simulation_run.total_travel_time = total_travel_time
            simulation_run.final_velocity = final_velocity
            simulation_run.total_energy_consumed = total_energy_consumed
            simulation_run.completed_at = datetime.now(timezone.utc)
            simulation_run.status = "completed"
            
            self.db.commit()

    
    def get_recent_simulation_runs(self, limit: int = 10) -> List[SimulationRun]:
        """Get recent simulation runs"""
        return self.db.query(SimulationRun).order_by(
            desc(SimulationRun.started_at)
        ).limit(limit).all()
    

    def get_simulation_run(self, simulation_id: str) -> SimulationRun | None:
        """Get a specific simulation run"""
        return self.db.query(SimulationRun).filter(
            SimulationRun.id == simulation_id
        ).first() 