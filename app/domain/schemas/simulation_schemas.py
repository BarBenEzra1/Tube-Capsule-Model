from pydantic import BaseModel, Field
from typing import Optional, List


class SimulationRequest(BaseModel):
    system_id: int = Field(gt=0, description="Valid system ID to run simulation on")


class TrajectoryPoint(BaseModel):
    time: float = Field(ge=0, description="Time in seconds")
    position: float = Field(ge=0, description="Position in meters")
    velocity: float = Field(ge=0, description="Velocity in m/s")
    acceleration: float = Field(description="Acceleration in m/s²")


class CoilActivation(BaseModel):
    coil_id: int = Field(gt=0, description="Coil ID")
    activation_time_from_t0: float = Field(ge=0, description="When coil activates (seconds)")
    engagement_duration: float = Field(ge=0, description="How long the coil applied force before the capsule left it (seconds)")
    force_applied: float = Field(description="Force applied by coil (Newtons)")


class SimulationResult(BaseModel):
    system_id: int
    total_travel_time: float = Field(ge=0, description="Total time to traverse tube (seconds)")
    final_velocity: float = Field(ge=0, description="Final velocity at tube end (m/s)")
    max_velocity: float = Field(ge=0, description="Maximum velocity reached (m/s)")
    trajectory: List[TrajectoryPoint] = Field(description="Capsule trajectory data")
    coil_activations: List[CoilActivation] = Field(description="Coil activation sequence")
    energy_consumed: float = Field(ge=0, description="Total energy consumed (Joules)")


class SimulationError(BaseModel):
    system_id: int
    error_message: str
    error_code: str


class SimulationResponse(BaseModel):
    success: bool
    result: Optional[SimulationResult] = None
    error: Optional[SimulationError] = None 