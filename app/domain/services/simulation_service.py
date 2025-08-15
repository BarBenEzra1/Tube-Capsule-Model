from app.data_access.simulation_da import SimulationRunDataAccess
from app.database.config import SessionLocal
from app.database.models import SimulationRun
from app.domain.services.engagement_events_service import initialize_engagement_events, get_engagement_events, set_current_simulation_id, set_current_system_id
from app.domain.services.segments_service import run_simulation_and_get_segments
from app.domain.services.system_service import get_system_by_id, get_system_coils
from app.domain.services.tube_service import get_tube_by_id
from app.domain.services.capsule_service import get_capsule_by_id
from app.domain.schemas.simulation_schemas import SimulationResponse, SimulationError, SimulationResult, PositionVsTimePoint, VelocityVsTimePoint, AccelerationVsTimePoint
from app.domain.entities.acceleration_segment import AccelerationSegment
from app.domain.entities.segment import Segment
from app.domain.entities.system import System

_current_simulation_id: str | None = None
_current_system_id: int | None = None
_log_data_access: SimulationRunDataAccess | None = None


def run_simulation_by_system_id(system_id: int) -> SimulationResponse:
    system = get_system_by_id(system_id)

    if system is None:
        return SimulationResponse(success=False, error=SimulationError(system_id=system_id, error_message="System not found", error_code="SYSTEM_NOT_FOUND"))
    
    initialize_engagement_events()
    simulation_id = simulation_start_log(system)
    segments = run_simulation_and_get_segments(system)
    position_vs_time_trajectory, velocity_vs_time_trajectory, acceleration_vs_time_trajectory, total_travel_time, final_velocity, total_energy_consumed = get_simulation_results(segments)

    simulation_complete_log(
        total_travel_time=total_travel_time,
        final_velocity=final_velocity,
        total_energy_consumed=total_energy_consumed
    )
    
    db_events = get_engagement_events(simulation_id)
    coil_engagement_logs = [
        {
            "t_s": event.timestamp_s,
            "event": event.event,
            **event.event_data
        } for event in db_events
    ]

    simulation_result = SimulationResult(
        simulation_id=simulation_id,
        system_id=system_id,
        system_details=format_system_details_for_simulation_result(system),
        total_travel_time=total_travel_time,
        final_velocity=final_velocity,
        total_energy_consumed=total_energy_consumed,
        position_vs_time_trajectory=position_vs_time_trajectory,
        velocity_vs_time_trajectory=velocity_vs_time_trajectory,
        acceleration_vs_time_trajectory=acceleration_vs_time_trajectory,
        coil_engagement_logs=coil_engagement_logs,
    )

    return SimulationResponse(success=True, result=simulation_result)


def get_simulation_results(segments: list[Segment]):
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

    total_travel_time = sum(segment.traverse_time for segment in segments)
    final_velocity = segments[-1].final_velocity if isinstance(segments[-1], AccelerationSegment) else segments[-1].velocity
    total_energy_consumed = sum(
        segment.energy_consumed for segment in segments 
        if isinstance(segment, AccelerationSegment)
    )

    return position_vs_time_trajectory, velocity_vs_time_trajectory, acceleration_vs_time_trajectory, total_travel_time, final_velocity, total_energy_consumed


def format_system_details_for_simulation_result(system: System) -> dict[str, float | int | str | dict | list]:
    tube = get_tube_by_id(system.tube_id)
    capsule = get_capsule_by_id(system.capsule_id)
    coils = get_system_coils(system)

    return {
        "tube": {
            "id": tube.id,
            "length": tube.length,
        },
        "capsule": {
            "id": capsule.id,
            "mass": capsule.mass,
            "initial_velocity": capsule.initial_velocity,
        },
        "coils": [
            {
                "id": coil.id,
                "length": coil.length,
                "force_applied": coil.force_applied,
                "position": system.coil_ids_to_positions[coil.id]
            }
            for coil in coils.values()
        ],
    }


def simulation_start_log(system: System) -> str:
    """
    Initialize logging for a new simulation run.
    Returns the simulation_id that should be used for all subsequent logs.
    """
    global _current_simulation_id, _current_system_id, _log_data_access
    
    db = SessionLocal()
    _log_data_access = SimulationRunDataAccess(db)
    
    _current_simulation_id = _log_data_access.start_simulation_run(system.id)
    set_current_simulation_id(_current_simulation_id)

    _current_system_id = system.id
    set_current_system_id(_current_system_id)
    
    return _current_simulation_id


def simulation_complete_log(total_travel_time: float, final_velocity: float, total_energy_consumed: float = None) -> None:
    """Complete the current simulation run with summary statistics"""
    global _current_simulation_id, _log_data_access
    
    if _current_simulation_id and _log_data_access:
        try:
            _log_data_access.complete_simulation_run(
                simulation_id=_current_simulation_id,
                total_travel_time=total_travel_time,
                final_velocity=final_velocity,
                total_energy_consumed=total_energy_consumed
            )
        except Exception as e:
            print(f"Failed to complete simulation logging: {e}")
    
    # Reset global state
    _current_simulation_id = None
    _current_system_id = None
    _log_data_access = None


def get_simulation_run(simulation_id: str) -> SimulationRun | None:
    """Get a simulation run by its ID"""
    global _log_data_access
    return _log_data_access.get_simulation_run(simulation_id)


def get_valid_simulation_run(simulation_id: str) -> SimulationRun:
    """Get a valid simulation run by its ID"""
    simulation_run = _log_data_access.get_simulation_run(simulation_id)

    if not simulation_run:
        raise ValueError(f"Simulation run with id {simulation_id} not found")
    
    if simulation_run.status != "completed":
        raise ValueError(f"Simulation run with id {simulation_id} is not completed")

    return simulation_run


def get_current_simulation_id() -> str | None:
    """Get the current simulation ID"""
    return _current_simulation_id


def get_current_system_id() -> int | None:
    """Get the current system ID"""
    return _current_system_id