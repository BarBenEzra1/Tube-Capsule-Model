from pydantic import BaseModel, Field


class TubeCreate(BaseModel):
    length: float = Field(gt=0, description="Length must be positive")


class TubeResponse(BaseModel):
    id: int
    length: float


class TubeUpdate(BaseModel):
    length: float


class TubesListResponse(BaseModel):
    entities: list[TubeResponse]

