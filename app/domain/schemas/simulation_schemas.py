from pydantic import BaseModel, Field
from typing import Optional, List


class SimulationRequest(BaseModel):
    system_id: int = Field(gt=0, description="Valid system ID to run simulation on")


class PositionVsTimePoint(BaseModel):
    time: float = Field(ge=0, description="Time in seconds")
    position: float = Field(ge=0, description="Position in meters")


class VelocityVsTimePoint(BaseModel):
    time: float = Field(ge=0, description="Time in seconds")
    velocity: float = Field(ge=0, description="Velocity in m/s")


class AccelerationVsTimePoint(BaseModel):
    time: float = Field(ge=0, description="Time in seconds")
    acceleration: float = Field(description="Acceleration in m/s²")


class SimulationResult(BaseModel):
    system_id: int
    total_travel_time: float = Field(ge=0, description="Total time to traverse tube (seconds)")
    final_velocity: float = Field(ge=0, description="Final velocity at tube end (m/s)")
    position_vs_time_trajectory: List[PositionVsTimePoint] = Field(description="Capsule position vs time trajectory")
    velocity_vs_time_trajectory: List[VelocityVsTimePoint] = Field(description="Capsule velocity vs time trajectory")
    acceleration_vs_time_trajectory: List[AccelerationVsTimePoint] = Field(description="Capsule acceleration vs time trajectory")
    coil_engagement_logs: list[dict[str, float | int | str]] = Field(description="Logs of coil engagement")


class SimulationError(BaseModel):
    system_id: int
    error_message: str
    error_code: str


class SimulationResponse(BaseModel):
    success: bool
    result: Optional[SimulationResult] = None
    error: Optional[SimulationError] = None 