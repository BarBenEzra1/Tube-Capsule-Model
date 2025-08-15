from datetime import datetime, timezone
from fastapi import APIRouter, Depends, status, Response
from sqlalchemy.orm import Session
from app.database.config import get_db
from app.domain.schemas.simulation_schemas import SimulationRequest
from app.domain.services.simulation_service import get_valid_simulation_run, run_simulation_by_system_id
import gzip


router = APIRouter(prefix="/simulation", tags=["Simulation"])


@router.post("/", status_code=status.HTTP_200_OK)
async def run_simulation(simulation_request: SimulationRequest):
    """Run simulation and download results as JSON (optionally compressed)"""
    
    simulation_response = run_simulation_by_system_id(simulation_request.system_id)
    json_content = simulation_response.model_dump_json(indent=2)
    
    timestamp = datetime.now(timezone.utc).strftime('%Y-%m-%d_%H-%M-%S')
    
    compressed_content = gzip.compress(json_content.encode('utf-8'))
    filename = f"simulation_result_{timestamp}.json.gz"
    headers = {
        "Content-Disposition": f'attachment; filename="{filename}"',
        "Content-Type": "application/gzip"
    }
    return Response(content=compressed_content, media_type="application/gzip", headers=headers)


@router.get("/{simulation_id}")
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
