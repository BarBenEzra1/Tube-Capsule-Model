from pydantic import BaseModel


class SystemCreate(BaseModel):
    tube_id: int
    coil_ids_to_positions: dict[int, int]
    capsule_id: int


class SystemResponse(BaseModel):
    id: int
    tube_id: int
    coil_ids_to_positions: dict[int, int]
    capsule_id: int


class SystemUpdate(BaseModel):
    tube_id: int
    coil_ids_to_positions: dict[int, int]
    capsule_id: int


class SystemsListResponse(BaseModel):
    entities: list[SystemResponse]

