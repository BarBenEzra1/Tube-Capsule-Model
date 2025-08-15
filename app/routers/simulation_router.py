from datetime import datetime, timezone
from fastapi import APIRouter, status, Response
from app.domain.schemas.simulation_schemas import SimulationRequest
from app.domain.services.simulation_service import run_simulation_by_system_id
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
