from fastapi import APIRouter, HTTPException, status

from app.domain.schemas.system_schemas import SystemCreate, SystemResponse, SystemsListResponse, SystemUpdate
from app.domain.services.system_service import read_all_systems, get_next_id, delete_system_by_id, get_system_by_id, update_system_by_id

from app.domain.entities.system import System


router = APIRouter(prefix="/systems", tags=["Systems"])

@router.post("/", response_model=dict, status_code=status.HTTP_201_CREATED)
async def create_system(system: SystemCreate):
    """Create new system entity"""
    
    system = System(system_id=get_next_id(), tube_id=system.tube_id, coil_ids=system.coil_ids, capsule_id=system.capsule_id)

    return {"id": system.id}


@router.get("/{system_id}", response_model=SystemResponse, status_code=status.HTTP_200_OK)
async def get_system_by_id(system_id: int):
    """Get system entity by id"""
    system = get_system_by_id(system_id)
    if system is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="System not found"
        )
        
    return SystemResponse(id=system.id, tube_id=system.tube_id, coil_ids=system.coil_ids, capsule_id=system.capsule_id)


@router.get("/", response_model=SystemsListResponse, status_code=status.HTTP_200_OK)
async def get_all_systems():
    """Get all systems"""
    systems_data = read_all_systems()  # returns list[dict]
    
    entities = [
        SystemResponse(id=system["id"], tube_id=system["tube_id"], coil_ids=system["coil_ids"], capsule_id=system["capsule_id"])
        for system in systems_data
    ]
    
    return SystemsListResponse(entities=entities)

@router.put("/{system_id}", status_code=status.HTTP_200_OK)
async def update_system(system_id: int, system: SystemUpdate):
    """Update system (full replace)"""
    updated = update_system_by_id(system_id=system_id, new_tube_id=system.tube_id, new_coil_ids=system.coil_ids, new_capsule_id=system.capsule_id)
    if updated is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="System not found")

    return SystemResponse(id=updated.id, tube_id=updated.tube_id, coil_ids=updated.coil_ids, capsule_id=updated.capsule_id)


@router.delete("/{system_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_system(system_id: int):
    """Delete system by id"""
    deleted = delete_system_by_id(system_id)
    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="System not found"
        )
        
    return {}