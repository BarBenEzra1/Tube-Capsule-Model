from pydantic import BaseModel, Field


class CoilCreate(BaseModel):
    length: float = Field(gt=0, description="Length must be positive")
    force_applied: float


class CoilResponse(BaseModel):
    id: int
    length: float
    force_applied: float


class CoilUpdate(BaseModel):
    length: float
    force_applied: float


class CoilsListResponse(BaseModel):
    entities: list[CoilResponse]