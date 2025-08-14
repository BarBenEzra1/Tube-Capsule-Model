from fastapi import APIRouter, HTTPException, status

from app.domain.schemas.simulation_schemas import SimulationRequest, SimulationResponse
from app.domain.services.simulation_service import run_simulation_by_system_id


router = APIRouter(prefix="/simulation", tags=["Simulation"])


@router.post("/", response_model=SimulationResponse, status_code=status.HTTP_200_OK)
async def run_simulation(simulation_request: SimulationRequest):
    """Run simulation"""
    
    return run_simulation_by_system_id(simulation_request.system_id)