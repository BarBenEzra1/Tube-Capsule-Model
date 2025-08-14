import os
import json
from app.domain.services.log_service import LOG_FILE_PATH, LOG_JSON_FILE_PATH
from app.domain.services.segments_service import run_segments_simulation
from app.domain.services.system_service import get_system_by_id, get_system_coils
from app.domain.services.tube_service import get_tube_by_id
from app.domain.services.capsule_service import get_capsule_by_id
from app.domain.schemas.simulation_schemas import SimulationResponse, SimulationError, SimulationResult, PositionVsTimePoint, VelocityVsTimePoint, AccelerationVsTimePoint
from app.domain.entities.acceleration_segment import AccelerationSegment
from app.domain.entities.system import System


def run_simulation_by_system_id(system_id: int) -> SimulationResponse:
    system = get_system_by_id(system_id)

    if system is None:
        return SimulationResponse(success=False, error=SimulationError(system_id=system_id, error_message="System not found", error_code="SYSTEM_NOT_FOUND"))
    
    os.makedirs(LOG_FILE_PATH.parent, exist_ok=True)
    os.makedirs(LOG_JSON_FILE_PATH.parent, exist_ok=True)

    # Write the title and system details BEFORE starting simulation
    with open(LOG_FILE_PATH, "a", encoding="utf-8") as f:
        f.write(f"==================================================\n")
        f.write(f"Running simulation for system with ID {system.id}\n")
        f.write(f"==================================================\n")
        f.write(f"System Details:\n")
        f.write(f"{format_system_details(system)}\n\n")

    # Run the simulation (this will append logs to the same file)
    segments = run_segments_simulation(system)

    # Write the end marker
    with open(LOG_FILE_PATH, "a", encoding="utf-8") as f:
        f.write(f"\n==================================================\n")
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

    with open(LOG_JSON_FILE_PATH, "r", encoding="utf-8") as f:
        coil_engagement_logs = [json.loads(line) for line in f]

    simulation_result = SimulationResult(
        system_id=system_id,
        total_travel_time=sum(segment.traverse_time for segment in segments),
        final_velocity=segments[-1].final_velocity if isinstance(segments[-1], AccelerationSegment) else segments[-1].velocity,
        max_velocity=max(segment.final_velocity if isinstance(segment, AccelerationSegment) else segment.velocity for segment in segments),
        position_vs_time_trajectory=position_vs_time_trajectory,
        velocity_vs_time_trajectory=velocity_vs_time_trajectory,
        acceleration_vs_time_trajectory=acceleration_vs_time_trajectory,
        coil_engagement_logs=coil_engagement_logs,
    )

    return SimulationResponse(success=True, result=simulation_result)


def format_system_details(system: System) -> str:
    # Fetch related entities
    tube = get_tube_by_id(system.tube_id)
    capsule = get_capsule_by_id(system.capsule_id)
    coils = get_system_coils(system)
    
    lines = []
    lines.append(f"System ID: {system.id}")
    lines.append("")
    
    # Tube details
    if tube:
        lines.append(f"Tube:")
        lines.append(f"  - ID: {tube.id}")
        lines.append(f"  - Length: {tube.length} m")
    else:
        lines.append(f"Tube: Not found (ID: {system.tube_id})")
    lines.append("")
    
    # Capsule details
    if capsule:
        lines.append(f"Capsule:")
        lines.append(f"  - ID: {capsule.id}")
        lines.append(f"  - Mass: {capsule.mass} kg")
        lines.append(f"  - Initial Velocity: {capsule.initial_velocity} m/s")
    else:
        lines.append(f"Capsule: Not found (ID: {system.capsule_id})")
    lines.append("")
    
    # Coils details
    lines.append(f"Coils ({len(coils)} total):")
    if coils:
        # Sort coils by position for nice display
        sorted_coil_positions = sorted(system.coil_ids_to_positions.items(), key=lambda x: x[1])
        for coil_id, position in sorted_coil_positions:
            coil = coils.get(coil_id)
            if coil:
                lines.append(f"  - Coil {coil_id}:")
                lines.append(f"    • Position: {position} m")
                lines.append(f"    • Length: {coil.length} m")
                lines.append(f"    • Force Applied: {coil.force_applied} N")
                lines.append(f"    • Range: {position} m - {position + coil.length} m")
            else:
                lines.append(f"  - Coil {coil_id}: Not found (Position: {position} m)")
    else:
        lines.append("  - No coils found")
    
    return "\n".join(lines)