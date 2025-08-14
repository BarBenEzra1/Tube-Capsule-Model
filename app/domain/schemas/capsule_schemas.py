from pydantic import BaseModel, Field


class CapsuleCreate(BaseModel):
    mass: float = Field(gt=0, description="Mass must be positive")
    initial_velocity: float = Field(gt=0, description="Initial velocity must be positive")


class CapsuleResponse(BaseModel):
    id: int
    mass: float
    initial_velocity: float


class CapsuleUpdate(BaseModel):
    mass: float
    initial_velocity: float


class CapsulesListResponse(BaseModel):
    entities: list[CapsuleResponse]

