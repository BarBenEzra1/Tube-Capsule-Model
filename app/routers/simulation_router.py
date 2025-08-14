from datetime import datetime, timezone
from fastapi import APIRouter, status, Response
from app.domain.schemas.simulation_schemas import SimulationRequest, SimulationResponse
from app.domain.services.simulation_service import run_simulation_by_system_id


router = APIRouter(prefix="/simulation", tags=["Simulation"])


@router.post("/", status_code=status.HTTP_200_OK)
async def run_simulation(simulation_request: SimulationRequest):
    """Run simulation"""
    
    simulation_response = run_simulation_by_system_id(simulation_request.system_id)
    json_content = simulation_response.model_dump_json(indent=2)
    
    filename = f"simulation_result_{datetime.now(timezone.utc).strftime('%Y-%m-%d_%H-%M-%S')}.json"
    headers = {"Content-Disposition": f'attachment; filename="{filename}"'}
    return Response(content=json_content, media_type="application/json", headers=headers)