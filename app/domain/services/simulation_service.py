from app.data_access.simulation_da import SimulationRunDataAccess
from app.database.config import SessionLocal
from sqlalchemy.orm import Session
from app.database.models import SimulationRun
from app.domain.entities.coil import Coil
from app.domain.services.engagement_events_service import initialize_engagement_events, get_engagement_events
from app.domain.services.segments_service import run_simulation_and_get_segments
from app.domain.services.system_service import get_system_by_id, get_system_coils
from app.domain.services.tube_service import get_tube_by_id
from app.domain.services.capsule_service import get_capsule_by_id
from app.domain.schemas.simulation_schemas import SimulationResult, PositionVsTimePoint, VelocityVsTimePoint, AccelerationVsTimePoint, ForceAppliedVsTimePoint, TotalEnergyConsumedVsTimePoint
from app.domain.entities.acceleration_segment import AccelerationSegment
from app.domain.entities.segment import Segment
from app.domain.entities.system import System
from app.domain.entities.capsule import Capsule
from app.domain.entities.tube import Tube
from app.domain.schemas.simulation_schemas import CompleteFlowRequest
from app.domain.utils.get_next_id import get_next_id

_current_system_id: int | None = None
_simulation_run_data_access: SimulationRunDataAccess | None = None


def run_simulation_by_system_id(system_id: int) -> SimulationResult:
    system = get_system_by_id(system_id)

    if system is None:
        raise ValueError(f"System with id {system_id} not found")
    
    system_details = format_system_details(system)
    simulation_id = simulation_start(system, system_details)

    try:
        initialize_engagement_events(simulation_id, system_id)

        segments = run_simulation_and_get_segments(system)

        coils = get_system_coils(system)
        position_vs_time_trajectory, velocity_vs_time_trajectory, acceleration_vs_time_trajectory, force_applied_vs_time, total_energy_consumed_metrics, total_travel_time_s, final_velocity_mps, total_energy_consumed_j = get_simulation_results(segments, coils)

        update_simulation_run_to_completed(
            simulation_id=simulation_id,
            total_travel_time_s=total_travel_time_s,
            final_velocity_mps=final_velocity_mps,
            total_energy_consumed_j=total_energy_consumed_j
        )
    
        coil_engagement_logs = get_coil_engagement_logs(simulation_id)

        return SimulationResult(
            simulation_id=simulation_id,
            system_id=system_id,
            system_details=system_details,
            total_travel_time_s=total_travel_time_s,
            final_velocity_mps=final_velocity_mps,
            total_energy_consumed_j=total_energy_consumed_j,
            position_vs_time_trajectory=position_vs_time_trajectory,
            velocity_vs_time_trajectory=velocity_vs_time_trajectory,
            acceleration_vs_time_trajectory=acceleration_vs_time_trajectory,
            force_applied_vs_time_trajectory=force_applied_vs_time,
            total_energy_consumed_vs_time_trajectory=total_energy_consumed_metrics,
            coil_engagement_logs=coil_engagement_logs,
        )

    except Exception as e:
        update_simulation_run_to_failed(simulation_id)
        raise e


def get_simulation_results(segments: list[Segment], coils: dict[int, Coil]):
    position_vs_time_trajectory = []
    velocity_vs_time_trajectory = []
    acceleration_vs_time_trajectory = []
    force_applied_vs_time = []
    total_energy_consumed_metrics = []
    total_energy_consumed_j = 0
    
    for segment in segments:
        is_accel = isinstance(segment, AccelerationSegment)
        coil = coils[segment.related_coil_id] if segment.related_coil_id else None

        position_vs_time_trajectory.append(
            PositionVsTimePoint(
                time=segment.start_time,
                position=segment.starting_position
            )
        )

        velocity_vs_time_trajectory.append(
            VelocityVsTimePoint(
                time=segment.start_time,
                velocity=segment.final_velocity if is_accel else segment.velocity
            )
        )

        acceleration_vs_time_trajectory.append(
            AccelerationVsTimePoint(
                time=segment.start_time,
                acceleration=segment.acceleration if is_accel else 0
            )
        )

        force_applied_vs_time.append(
            ForceAppliedVsTimePoint(
                time=segment.start_time,
                force_applied=coil.force_applied if is_accel and coil else 0
            )
        )

        total_energy_consumed_j += segment.energy_consumed if is_accel else 0

        total_energy_consumed_metrics.append(
            TotalEnergyConsumedVsTimePoint(
                time=segment.start_time,
                total_energy_consumed_j=total_energy_consumed_j
            )
        )

    total_travel_time_s = sum(segment.traverse_time for segment in segments)
    final_velocity_mps = segments[-1].final_velocity if isinstance(segments[-1], AccelerationSegment) else segments[-1].velocity
    total_energy_consumed_j = sum(
        segment.energy_consumed for segment in segments 
        if isinstance(segment, AccelerationSegment)
    )

    return position_vs_time_trajectory, velocity_vs_time_trajectory, acceleration_vs_time_trajectory, force_applied_vs_time, total_energy_consumed_metrics, total_travel_time_s, final_velocity_mps, total_energy_consumed_j


def get_coil_engagement_logs(simulation_id: str) -> list[dict[str, float | int | str]]:
    db_events = get_engagement_events(simulation_id)
    coil_engagement_logs = []

    fields = [
        "coil_id",
        "position_m",
        "velocity_mps",
        "acceleration_mps2",
        "acceleration_duration_s",
        "acceleration_segment_length_m",
        "force_applied_n",
        "energy_consumed_j"
    ]

    for event in db_events:
        log_entry = {
            "t_s": event.timestamp_s,
            "event": event.event
        }
        log_entry.update({
            field: getattr(event, field)
            for field in fields
            if getattr(event, field) is not None
        })
        coil_engagement_logs.append(log_entry)

    return coil_engagement_logs


def format_system_details(system: System) -> dict[str, float | int | str | dict | list]:
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


def create_all_simulation_entities(complete_flow_request: CompleteFlowRequest) -> int:
    tube_id = get_next_id(Tube.DATABASE_FILE_PATH)
    Tube(
        tube_id=tube_id, 
        length=complete_flow_request.tube.length
    )
    
    capsule_id = get_next_id(Capsule.DATABASE_FILE_PATH)
    Capsule(
        capsule_id=capsule_id,
        mass=complete_flow_request.capsule.mass,
        initial_velocity=complete_flow_request.capsule.initial_velocity
    )
    
    coil_ids_to_positions = {}
    for coil_data in complete_flow_request.coils:
        coil_id = get_next_id(Coil.DATABASE_FILE_PATH)
        Coil(
            coil_id=coil_id,
            length=coil_data.length,
            force_applied=coil_data.force_applied
        )
        coil_ids_to_positions[coil_id] = coil_data.position
    
    system_id = get_next_id(System.DATABASE_FILE_PATH)
    System(
        system_id=system_id,
        tube_id=tube_id,
        coil_ids_to_positions=coil_ids_to_positions,
        capsule_id=capsule_id
    )

    return system_id


def simulation_start(system: System, system_details: dict[str, float | int | str | dict | list]) -> str:
    """
    Initialize logging for a new simulation run.
    Returns the simulation_id that should be used for all subsequent logs.
    """
    global _current_system_id, _simulation_run_data_access
    
    _current_system_id = system.id

    db = SessionLocal()
    _simulation_run_data_access = SimulationRunDataAccess(db)
    
    return _simulation_run_data_access.insert_simulation_run(system.id, system_details)


def update_simulation_run_to_completed(simulation_id: str, total_travel_time_s: float, final_velocity_mps: float, total_energy_consumed_j: float = None) -> SimulationRun | None:
    """Complete the current simulation run with summary statistics"""
    global _simulation_run_data_access
    
    if _simulation_run_data_access:
        try:
            simulation_run = _simulation_run_data_access.simulation_complete(
                simulation_id=simulation_id,
                total_travel_time_s=total_travel_time_s,
                final_velocity_mps=final_velocity_mps,
                total_energy_consumed_j=total_energy_consumed_j
            )

            return simulation_run
        except Exception as e:
            print(f"Failed to complete simulation logging: {e}")
            return None
    

def update_simulation_run_to_failed(simulation_id: str) -> SimulationRun | None:
    """Fail the current simulation run with an error message"""
    global _simulation_run_data_access
    
    if _simulation_run_data_access:
        return _simulation_run_data_access.simulation_failed(simulation_id)
    

def get_simulation_run(simulation_id: str) -> SimulationRun | None:
    """Get a simulation run by its ID"""
    global _simulation_run_data_access
    return _simulation_run_data_access.get_simulation_run_by_id(simulation_id)


def get_valid_simulation_run(simulation_id: str, db: Session) -> SimulationRun:
    """Get a valid simulation run by its ID"""
    global _simulation_run_data_access

    _simulation_run_data_access = SimulationRunDataAccess(db)
    simulation_run = _simulation_run_data_access.get_simulation_run_by_id(simulation_id)

    if not simulation_run:
        raise ValueError(f"Simulation run with id {simulation_id} not found")
    
    if simulation_run.status != "completed":
        raise ValueError(f"Simulation run with id {simulation_id} is not completed")

    return simulation_run


def get_current_system_id() -> int | None:
    """Get the current system ID"""
    global _current_system_id
    
    return _current_system_id