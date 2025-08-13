from fastapi import APIRouter, HTTPException, status

from app.domain.schemas.capsule_schemas import CapsuleCreate, CapsuleResponse, CapsulesListResponse, CapsuleUpdate
from app.domain.services.capsule_service import read_all_capsules, delete_capsule_by_id, get_capsule_by_id, update_capsule_by_id

from app.domain.entities.capsule import Capsule
from app.domain.utils.get_next_id import get_next_id


router = APIRouter(prefix="/capsules", tags=["Capsules"])

@router.post("/", response_model=dict, status_code=status.HTTP_201_CREATED)
async def create_capsule(capsule: CapsuleCreate):
    """Create new capsule entity"""
    
    capsule = Capsule(capsule_id=get_next_id(Capsule.DATABASE_FILE_PATH), mass=capsule.mass, initial_velocity=capsule.initial_velocity)

    return {"id": capsule.id}


@router.get("/{capsule_id}", response_model=CapsuleResponse, status_code=status.HTTP_200_OK)
async def get_capsule_by_id(capsule_id: int):
    """Get capsule entity by id"""
    capsule = get_capsule_by_id(capsule_id)
    if capsule is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Capsule not found"
        )
        
    return CapsuleResponse(id=capsule.id, mass=capsule.mass, initial_velocity=capsule.initial_velocity)


@router.get("/", response_model=CapsulesListResponse, status_code=status.HTTP_200_OK)
async def get_all_capsules():
    """Get all capsules"""
    capsules_data = read_all_capsules()  # returns list[dict]
    
    entities = [
        CapsuleResponse(id=capsule["id"], mass=capsule["mass"], initial_velocity=capsule["initial_velocity"])
        for capsule in capsules_data
    ]
    
    return CapsulesListResponse(entities=entities)

@router.put("/{capsule_id}", status_code=status.HTTP_200_OK)
async def update_capsule(capsule_id: int, capsule: CapsuleUpdate):
    """Update capsule (full replace)"""
    updated = update_capsule_by_id(capsule_id=capsule_id, new_mass=capsule.mass, new_initial_velocity=capsule.initial_velocity)
    if updated is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Capsule not found")

    return CapsuleResponse(id=updated.id, mass=updated.mass, initial_velocity=updated.initial_velocity)


@router.delete("/{capsule_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_capsule(capsule_id: int):
    """Delete capsule by id"""
    deleted = delete_capsule_by_id(capsule_id)
    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Capsule not found"
        )
        
    return {}