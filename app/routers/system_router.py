from fastapi import APIRouter, HTTPException, status
from app.domain.schemas.system_schemas import SystemCreate, SystemResponse, SystemsListResponse, SystemUpdate
from app.domain.services.system_service import UpdateSystemStatus, read_all_systems, delete_system_by_id, get_system_by_id, update_system_by_id
from app.domain.entities.system import System
from app.domain.utils.get_next_id import get_next_id
from app.domain.services.coil_service import convert_coil_positions_to_dict, convert_dict_to_coil_positions


router = APIRouter(prefix="/systems", tags=["Systems"])


@router.post("/", response_model=dict, status_code=status.HTTP_201_CREATED)
async def create_system(system: SystemCreate):
    """Create new system entity"""
    
    coil_dict = convert_coil_positions_to_dict(system.coil_ids_to_positions)
    
    system = System(system_id=get_next_id(System.DATABASE_FILE_PATH), tube_id=system.tube_id, coil_ids_to_positions=coil_dict, capsule_id=system.capsule_id)

    return {"id": system.id}


@router.get("/{system_id}", response_model=SystemResponse, status_code=status.HTTP_200_OK)
async def get_system(system_id: int):
    """Get system entity by id"""
    system = get_system_by_id(system_id)
    if system is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="System not found"
        )
    
    coil_positions = convert_dict_to_coil_positions(system.coil_ids_to_positions)
    
    return SystemResponse(id=system.id, tube_id=system.tube_id, coil_ids_to_positions=coil_positions, capsule_id=system.capsule_id)


@router.get("/", response_model=SystemsListResponse, status_code=status.HTTP_200_OK)
async def get_all_systems():
    """Get all systems"""
    systems_data = read_all_systems()  # returns list[dict]
    
    entities = []
    for system in systems_data:
        coil_positions = convert_dict_to_coil_positions(system["coil_ids_to_positions"])
        entities.append(
            SystemResponse(id=system["id"], tube_id=system["tube_id"], coil_ids_to_positions=coil_positions, capsule_id=system["capsule_id"])
        )
    
    return SystemsListResponse(entities=entities)


@router.put("/{system_id}", status_code=status.HTTP_200_OK)
async def update_system(system_id: int, system: SystemUpdate):
    """Update system (full replace)"""
    
    coil_dict = convert_coil_positions_to_dict(system.coil_ids_to_positions)
    
    updated_status = update_system_by_id(system_id=system_id, new_tube_id=system.tube_id, new_coil_ids_to_positions=coil_dict, new_capsule_id=system.capsule_id)
    if updated_status[0] == UpdateSystemStatus.NOT_FOUND:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="System not found")
    elif updated_status[0] == UpdateSystemStatus.INVALID_SYSTEM:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=updated_status[1])

    system = get_system_by_id(system_id)
    coil_positions = convert_dict_to_coil_positions(system.coil_ids_to_positions)
    
    return SystemResponse(id=system.id, tube_id=system.tube_id, coil_ids_to_positions=coil_positions, capsule_id=system.capsule_id)


@router.delete("/{system_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_system(system_id: int, force_delete_related_entities: bool = False):
    """Delete system by id"""
    deleted = delete_system_by_id(system_id, force_delete_related_entities)
    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="System not found"
        )
        
    return {}