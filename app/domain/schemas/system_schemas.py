from pydantic import BaseModel, Field


class CoilPosition(BaseModel):
    coilId: int = Field(gt=0, description="Valid coil ID")
    position: int = Field(ge=0, description="Position in the tube (must be non-negative)")


class SystemCreate(BaseModel):
    tube_id: int = Field(gt=0, description="Valid tube id must be provided")
    coil_ids_to_positions: list[CoilPosition] = Field(description="List of coil positions")
    capsule_id: int = Field(gt=0, description="Valid capsule id must be provided")


class SystemResponse(BaseModel):
    id: int
    tube_id: int
    coil_ids_to_positions: list[CoilPosition]
    capsule_id: int


class SystemUpdate(BaseModel):
    tube_id: int
    coil_ids_to_positions: list[CoilPosition] = Field(description="List of coil positions")
    capsule_id: int


class SystemsListResponse(BaseModel):
    entities: list[SystemResponse]

