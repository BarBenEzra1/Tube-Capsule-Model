from fastapi import APIRouter, Depends, status, Response
from sqlalchemy.orm import Session
from app.database.config import get_db
from app.domain.schemas.simulation_schemas import CompleteFlowRequest, SimulationRequest
from app.domain.services.simulation_service import create_all_simulation_entities, get_valid_simulation_run, run_simulation_by_system_id
from app.domain.utils.compress_json import compress_json


router = APIRouter(prefix="/simulation", tags=["Simulation"])


@router.post("/complete-flow", status_code=status.HTTP_200_OK)
async def run_complete_flow_simulation(complete_flow_request: CompleteFlowRequest):
    """Create all entities from provided data and run simulation, returning results as compressed JSON"""
    
    try:
        system_id = create_all_simulation_entities(complete_flow_request)
        
        simulation_response = run_simulation_by_system_id(system_id)
        compressed_content, headers = compress_json(simulation_response)

        return Response(content=compressed_content, media_type="application/gzip", headers=headers)
        
    except ValueError as e:
        return Response(
            content=f"Validation error: {str(e)}", 
            status_code=400,
            media_type="text/plain"
        )
    except Exception as e:
        return Response(
            content=f"Internal server error: {str(e)}", 
            status_code=500,
            media_type="text/plain"
        )


@router.post("/", status_code=status.HTTP_200_OK)
async def run_simulation(simulation_request: SimulationRequest):
    """Run simulation and download results as compressed JSON"""
    
    try:
        simulation_response = run_simulation_by_system_id(simulation_request.system_id)
        compressed_content, headers = compress_json(simulation_response)

        return Response(content=compressed_content, media_type="application/gzip", headers=headers)
    
    except ValueError as e:
        return Response(
            content=f"Validation error: {str(e)}", 
            status_code=400,
            media_type="text/plain"
        )
    except Exception as e:
        return Response(
            content=f"Internal server error: {str(e)}", 
            status_code=500,
            media_type="text/plain"
        )


@router.get("/{simulation_id}")
async def get_simulation_run(simulation_id: str, db: Session = Depends(get_db)):
    """Get a simulation run by its ID"""
    simulation_run = get_valid_simulation_run(simulation_id, db)
    
    return {
        "simulation_id": simulation_run.id,
        "system_id": simulation_run.system_id,
        "total_travel_time_s": simulation_run.total_travel_time_s,
        "final_velocity_mps": simulation_run.final_velocity_mps,
        "total_energy_consumed_j": simulation_run.total_energy_consumed_j,
        "status": simulation_run.status,
        "started_at": simulation_run.started_at,
        "completed_at": simulation_run.completed_at,
    }
