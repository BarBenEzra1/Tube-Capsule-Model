from fastapi import APIRouter, Query, Depends
from sqlalchemy.orm import Session
from app.database.config import get_db

from app.domain.services.engagement_events_service import get_engagement_events
from app.domain.services.simulation_service import get_valid_simulation_run

router = APIRouter(prefix="/analytics", tags=["Analytics"])


@router.get("/simulation-runs/{simulation_id}", response_model=dict)
async def get_simulation_run(simulation_id: str, db: Session = Depends(get_db)):
    """Get a simulation run by its ID"""
    simulation_run = get_valid_simulation_run(simulation_id, db)
    
    return {
        "simulation_id": simulation_run.id,
        "system_id": simulation_run.system_id,
        "total_travel_time": simulation_run.total_travel_time,
        "final_velocity": simulation_run.final_velocity,
        "total_energy_consumed": simulation_run.total_energy_consumed,
        "status": simulation_run.status,
        "started_at": simulation_run.started_at,
        "completed_at": simulation_run.completed_at,
    }


@router.get("/simulation-runs/{simulation_id}/engagement-events")
async def get_simulation_engagement_events(simulation_id: str, event: str | None = Query(None, description="Filter by event type"), coil_id: int | None = Query(None, description="Filter by coil ID"), db: Session = Depends(get_db)):
    """Get all events for a specific simulation run"""
    get_valid_simulation_run(simulation_id, db)

    engagement_events = get_engagement_events(simulation_id, event, coil_id, db)
    
    return [
        {
            "id": event.id,
            "timestamp_s": event.timestamp_s,
            "event": event.event,
            "coil_id": event.coil_id,
            "position_m": event.position_m,
            "velocity_mps": event.velocity_mps,
            "acceleration_mps2": event.acceleration_mps2,
            "acceleration_duration_s": event.acceleration_duration_s,
            "acceleration_segment_length_m": event.acceleration_segment_length_m,
            "force_applied_n": event.force_applied_n,
            "energy_consumed_j": event.energy_consumed_j,
        }
        for event in engagement_events
    ]


@router.get("/simulation-runs/{simulation_id}/metrics")
async def get_simulation_metrics(simulation_id: str, db: Session = Depends(get_db)):
    """Get position, velocity, and acceleration trajectory for a simulation"""
    get_valid_simulation_run(simulation_id, db)

    events = get_engagement_events(simulation_id, db=db)
    
    position_trajectory = []    
    velocity_trajectory = []
    acceleration_trajectory = []
    force_applied_vs_time = []
    total_energy_consumed_metrics = []

    total_energy_consumed = 0

    for event in events:
        timestamp = event.timestamp_s
        
        position_trajectory.append({
            "t_s": timestamp,
            "position_m": event.position_m
        })
        
        velocity_trajectory.append({
            "t_s": timestamp,
            "velocity_mps": event.velocity_mps
        })
        
        acceleration_trajectory.append({
            "t_s": timestamp,
            "acceleration_mps2": event.acceleration_mps2
        })

        force_applied_vs_time.append({
            "t_s": timestamp,
            "force_applied_n": event.force_applied_n
        })

        total_energy_consumed += event.energy_consumed_j

        total_energy_consumed_metrics.append({
            "t_s": timestamp,
            "total_energy_consumed_j": total_energy_consumed
        })
    
    return {
        "simulation_id": simulation_id,
        "position_vs_time": position_trajectory,
        "velocity_vs_time": velocity_trajectory,
        "acceleration_vs_time": acceleration_trajectory,
        "force_applied_vs_time": force_applied_vs_time,
        "total_energy_consumed_vs_time": total_energy_consumed_metrics
    }


@router.get("/simulation-runs/{simulation_id}/energy-consumption")
async def get_energy_consumption_analysis(simulation_id: str, db: Session = Depends(get_db)):
    """Get energy consumption analysis by coil"""
    get_valid_simulation_run(simulation_id, db)

    energy_consumed_events = get_engagement_events(simulation_id, "coil_exit", db=db)
    
    coil_energy_consumption = {}
    total_energy = 0
    
    for event in energy_consumed_events:
        coil_id = event.coil_id
        energy = event.energy_consumed_j
        
        if coil_id and energy:
            coil_energy_consumption[coil_id] = energy
            total_energy += energy
    
    return {
        "simulation_id": simulation_id,
        "total_energy_consumed_j": total_energy,
        "energy_by_coil": coil_energy_consumption,
        "coil_count": len(coil_energy_consumption)
    }