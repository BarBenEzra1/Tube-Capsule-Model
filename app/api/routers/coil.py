from fastapi import APIRouter, HTTPException, status

from app.domain.schemas.coil_schemas import CoilCreate, CoilResponse, CoilsListResponse, CoilUpdate
from app.domain.services.coil_service import read_all_coils, get_next_id, delete_coil_by_id, get_coil_by_id, update_coil_by_id

from app.domain.entities.coil import Coil


router = APIRouter(prefix="/coils", tags=["Coils"])

@router.post("/", response_model=dict, status_code=status.HTTP_201_CREATED)
async def create_coil(coil: CoilCreate):
    """Create new coil entity"""
    
    coil = Coil(coil_id=get_next_id(), length=coil.length, force_applied=coil.force_applied)

    return {"id": coil.id}


@router.get("/{coil_id}", response_model=CoilResponse, status_code=status.HTTP_200_OK)
async def get_coil_by_id(coil_id: int):
    """Get coil entity by id"""
    coil = get_coil_by_id(coil_id)
    if coil is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Coil not found"
        )
        
    return CoilResponse(id=coil.id, length=coil.length, force_applied=coil.force_applied)


@router.get("/", response_model=CoilsListResponse, status_code=status.HTTP_200_OK)
async def get_all_coils():
    """Get all coils"""
    coils_data = read_all_coils()  # returns list[dict]
    
    entities = [
        CoilResponse(id=coil["id"], length=coil["length"], force_applied=coil["force_applied"])
        for coil in coils_data
    ]
    
    return CoilsListResponse(entities=entities)

@router.put("/{coil_id}", status_code=status.HTTP_200_OK)
async def update_coil(coil_id: int, coil: CoilUpdate):
    """Update coil (full replace)"""
    updated = update_coil_by_id(coil_id=coil_id, new_length=coil.length, new_force_applied=coil.force_applied)
    if updated is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Coil not found")

    return CoilResponse(id=updated.id, length=updated.length, force_applied=updated.force_applied)


@router.delete("/{coil_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_coil(coil_id: int):
    """Delete coil by id"""
    deleted = delete_coil_by_id(coil_id)
    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Coil not found"
        )
        
    return {}