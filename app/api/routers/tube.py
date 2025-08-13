from fastapi import APIRouter, HTTPException, status

from app.domain.schemas.tube_schemas import TubeCreate, TubeResponse, TubesListResponse, TubeUpdate
from app.domain.services.tube_service import read_all_tubes, get_next_id, delete_tube_by_id, get_tube_by_id, update_tube_by_id

from app.domain.entities.tube import Tube


router = APIRouter(prefix="/tubes", tags=["tubes"])

@router.post("/", response_model=dict, status_code=status.HTTP_201_CREATED)
async def create_tube(tube: TubeCreate):
    """Create new tube entity"""
    
    tube = Tube(tube_id=get_next_id(), length=tube.length)

    return {"id": tube.id}


@router.get("/{tube_id}", response_model=TubeResponse, status_code=status.HTTP_200_OK)
async def get_tube_by_id(tube_id: int):
    """Get tube entity by id"""
    tube = get_tube_by_id(tube_id)
    if tube is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Tube not found"
        )
        
    return TubeResponse(id=tube.id, length=tube.length)


@router.get("/", response_model=TubesListResponse, status_code=status.HTTP_200_OK)
async def get_all_tubes():
    """Get all tubes"""
    tubes_data = read_all_tubes()  # returns list[dict]
    
    entities = [
        TubeResponse(id=tube["id"], length=tube["length"])
        for tube in tubes_data
    ]
    
    return TubesListResponse(entities=entities)

@router.put("/{tube_id}", status_code=status.HTTP_200_OK)
async def update_tube(tube_id: int, tube: TubeUpdate):
    """Update tube (full replace)"""
    updated = update_tube_by_id(tube_id=tube_id, new_length=tube.length)
    if updated is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Tube not found")

    return TubeResponse(id=updated.id, length=updated.length)


@router.delete("/{tube_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_tube(tube_id: int):
    """Delete tube by id"""
    deleted = delete_tube_by_id(tube_id)
    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Tube not found"
        )
        
    return {}