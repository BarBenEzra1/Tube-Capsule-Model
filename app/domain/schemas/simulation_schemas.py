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


class ForceAppliedVsTimePoint(BaseModel):
    time: float = Field(ge=0, description="Time in seconds")
    force_applied: float = Field(description="Force applied (N)")


class TotalEnergyConsumedVsTimePoint(BaseModel):
    time: float = Field(ge=0, description="Time in seconds")
    total_energy_consumed: float = Field(ge=0, description="Total energy consumed (J)")


class SimulationResult(BaseModel):
    simulation_id: str
    system_id: int
    system_details: dict[str, float | int | str | dict | list] = Field(description="Details of the system")
    total_travel_time: float = Field(ge=0, description="Total time to traverse tube (seconds)")
    final_velocity: float = Field(ge=0, description="Final velocity at tube end (m/s)")
    total_energy_consumed: float = Field(ge=0, description="Total energy consumed (J)")
    position_vs_time_trajectory: List[PositionVsTimePoint] = Field(description="Capsule position vs time trajectory")
    velocity_vs_time_trajectory: List[VelocityVsTimePoint] = Field(description="Capsule velocity vs time trajectory")
    acceleration_vs_time_trajectory: List[AccelerationVsTimePoint] = Field(description="Capsule acceleration vs time trajectory")
    force_applied_vs_time_trajectory: List[ForceAppliedVsTimePoint] = Field(description="Force applied vs time trajectory")
    total_energy_consumed_vs_time_trajectory: List[TotalEnergyConsumedVsTimePoint] = Field(description="Total energy consumed vs time trajectory")
    coil_engagement_logs: list[dict[str, float | int | str]] = Field(description="Logs of coil engagement")


class SimulationError(BaseModel):
    system_id: int
    error_message: str
    error_code: str


class SimulationResponse(BaseModel):
    success: bool
    result: Optional[SimulationResult] = None
    error: Optional[SimulationError] = None 