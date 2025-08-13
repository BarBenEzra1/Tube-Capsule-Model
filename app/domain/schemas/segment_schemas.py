from pydantic import BaseModel, Field


class SegmentCreate(BaseModel):
    traverse_time: float = Field(gt=0, description="Traverse time must be positive")
    start_time: float = Field(gt=0, description="Start time must be positive")
    length: float = Field(gt=0, description="Length must be positive")
    starting_position: float = Field(gt=0, description="Starting position must be positive")
    related_coil_id: int


class SegmentResponse(BaseModel):
    id: int
    traverse_time: float
    start_time: float
    length: float
    starting_position: float
    related_coil_id: int


class SegmentUpdate(BaseModel):
    traverse_time: float
    start_time: float
    length: float
    starting_position: float
    related_coil_id: int


class SegmentsListResponse(BaseModel):
    entities: list[SegmentResponse]

