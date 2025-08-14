from app.domain.entities.constant_velocity_segment import ConstantVelocitySegment
from app.domain.services.segments_service import run_segments_simulation
from app.domain.services.system_service import get_system_by_id
from app.domain.schemas.simulation_schemas import SimulationResponse, SimulationError, SimulationResult, TrajectoryPoint, CoilActivation
from app.domain.entities.acceleration_segment import AccelerationSegment
from pathlib import Path

LOG_FILE_PATH = Path("app/data/simulation.log")

def run_simulation_by_system_id(system_id: int):
    system = get_system_by_id(system_id)

    if system is None:
        return SimulationResponse(success=False, error=SimulationError(system_id=system_id, error_message="System not found", error_code="SYSTEM_NOT_FOUND"))
    
    LOG_FILE_PATH.touch(exist_ok=True)

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


    total_travel_time = sum(segment.traverse_time for segment in segments)
    final_velocity = segments[-1].final_velocity
    max_velocity = max(segment.velocity for segment in segments)
    trajectory = [
        TrajectoryPoint( # Time step is set by the segment's traverse time
            time=segment.start_time,
            position=segment.starting_position,
            velocity=segment.velocity,
            acceleration=segment.acceleration
        )
        for segment in segments
    ]

    coil_activations = []
    for i,segment in enumerate(segments[:-1]):
        if i == 0:
            continue

        if isinstance(segment, AccelerationSegment):
            constant_velocity_segment: ConstantVelocitySegment = segments[i + 1]




            # coil_activations.append(CoilActivation(
            #     coil_id=segment.related_coil_id,
            #     position=system.coil_ids_to_positions[segment.related_coil_id],
            #     engagement_start_time_from_t0=segment.start_time,
            #     engagement_duration=segment.traverse_time,
            #     start_velocity=segment.start_velocity,
            #     final_velocity=segment.final_velocity,
            #     force_applied=segment.acceleration
            # ))


    energy_consumed = sum(segment.energy_consumed for segment in segments)

    return SimulationResult(
        system_id=system_id,
        total_travel_time=total_travel_time,
        final_velocity=final_velocity,
        max_velocity=max_velocity,
        trajectory=trajectory,
        coil_activations=coil_activations,
        energy_consumed=energy_consumed
    )
