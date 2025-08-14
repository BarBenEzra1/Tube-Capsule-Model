from app.domain.services.segments_service import run_segments_simulation
from app.domain.services.system_service import get_system_by_id
from app.domain.schemas.simulation_schemas import SimulationResponse, SimulationError, SimulationResult, PositionVsTimePoint, VelocityVsTimePoint, AccelerationVsTimePoint
from app.domain.entities.acceleration_segment import AccelerationSegment
from pathlib import Path

LOG_FILE_PATH = Path("app/data/simulation.log")

def run_simulation_by_system_id(system_id: int):
    system = get_system_by_id(system_id)

    if system is None:
        return SimulationResponse(success=False, error=SimulationError(system_id=system_id, error_message="System not found", error_code="SYSTEM_NOT_FOUND"))
    
    LOG_FILE_PATH.touch(exist_ok=True)

    segments = []

    with open(LOG_FILE_PATH, "a", encoding="utf-8") as f:
        f.write(f"==================================================\n")
        f.write(f"Running simulation for system with ID {system.id}\n")
        f.write(f"==================================================\n")
        f.write(f"System Details:\n")
        f.write(f"{system}\n")

        segments = run_segments_simulation(system)

        f.write(f"==================================================\n")
        f.write(f"End of simulation\n")
        f.write(f"==================================================\n")

    position_vs_time_trajectory = [
        PositionVsTimePoint(
            time=segment.start_time,
            position=segment.starting_position,
        )
        for segment in segments
    ]
    velocity_vs_time_trajectory = [
        VelocityVsTimePoint(
            time=segment.start_time,
            velocity=segment.final_velocity if isinstance(segment, AccelerationSegment) else segment.velocity,
        )
        for segment in segments
    ]
    acceleration_vs_time_trajectory = [
        AccelerationVsTimePoint(
            time=segment.start_time,
            acceleration=segment.acceleration if isinstance(segment, AccelerationSegment) else 0,
        )
        for segment in segments
    ]

    return SimulationResult(
        system_id=system_id,
        total_travel_time=sum(segment.traverse_time for segment in segments),
        final_velocity=segments[-1].final_velocity,
        max_velocity=max(segment.get_final_velocity() for segment in segments),
        position_vs_time_trajectory=position_vs_time_trajectory,
        velocity_vs_time_trajectory=velocity_vs_time_trajectory,
        acceleration_vs_time_trajectory=acceleration_vs_time_trajectory,
    )
