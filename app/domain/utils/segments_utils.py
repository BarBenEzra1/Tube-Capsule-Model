from app.domain.entities.acceleration_segment import AccelerationSegment
from app.domain.entities.capsule import Capsule
from app.domain.entities.constant_velocity_segment import ConstantVelocitySegment
from app.domain.entities.tube import Tube
from app.domain.entities.systemCoil import SystemCoil
from app.domain.utils.physics_utils import get_traverse_time_for_constant_velocity, get_acceleration, get_final_velocity, get_traverse_time_for_acceleration
from app.domain.services.engagement_events_service import engagement_event_log

def run_first_segment(system_coils: list[SystemCoil], capsule: Capsule, tube: Tube) -> ConstantVelocitySegment:
    engagement_event_log(0.0, "run_start", velocity_mps=capsule.initial_velocity, position_m=0)

    if len(system_coils) == 0:
        return ConstantVelocitySegment(
                id=1, 
                traverse_time=get_traverse_time_for_constant_velocity(capsule.initial_velocity, tube.length),
                start_time=0, 
                length=tube.length, 
                starting_position=0, 
                related_coil_id=None, 
                velocity=capsule.initial_velocity,
            )

    else:
        first_coil = system_coils[0]
        first_coil_id = first_coil.coil_id
        first_coil_middle_position = first_coil.position + round(first_coil.coil.length / 2, 6)

        time_to_reach_first_coil = get_traverse_time_for_constant_velocity(capsule.initial_velocity, first_coil.position)
        
        engagement_event_log(time_to_reach_first_coil, "coil_enter", coil_id=first_coil_id, position_m=first_coil.position, velocity_mps=capsule.initial_velocity)

        return ConstantVelocitySegment(
                segment_id=1, 
                traverse_time=get_traverse_time_for_constant_velocity(capsule.initial_velocity, first_coil_middle_position),
                start_time=0, 
                length=first_coil_middle_position, 
                starting_position=0, 
                related_coil_id=first_coil_id, 
                velocity=capsule.initial_velocity,
            )


def run_constant_velocity_segment(acceleration_coil: SystemCoil, next_coil: SystemCoil | None, tube: Tube, current_velocity: float, time_so_far: float, segment_id: int) -> ConstantVelocitySegment:
    prev_coil_end_position = acceleration_coil.position + acceleration_coil.coil.length
    seg_len = (
        next_coil.position + round(next_coil.coil.length / 2, 6) - prev_coil_end_position
        if next_coil is not None
        else tube.length - prev_coil_end_position
    )
    traverse_time = get_traverse_time_for_constant_velocity(current_velocity, seg_len)

    constant_velocity_segment = ConstantVelocitySegment(
        segment_id=segment_id,
        traverse_time=traverse_time,
        start_time=time_so_far,
        length=seg_len,
        starting_position=prev_coil_end_position,
        related_coil_id=acceleration_coil.coil_id,
        velocity=current_velocity,
    )

    if next_coil is not None:
        dist_to_next_coil = next_coil.position - prev_coil_end_position
        time_to_reach_next_coil = get_traverse_time_for_constant_velocity(current_velocity, dist_to_next_coil)
        engagement_event_log(time_so_far + time_to_reach_next_coil, "coil_enter", coil_id=next_coil.coil_id, position_m=next_coil.position, velocity_mps=current_velocity)

    return constant_velocity_segment


def run_acceleration_segment(system_coil: SystemCoil, capsule: Capsule, current_velocity: float, time_so_far: float, segment_id: int) -> AccelerationSegment:
    middle_coil_position = system_coil.position + round(system_coil.coil.length / 2, 6)
    end_coil_position = system_coil.position + system_coil.coil.length

    acceleration = get_acceleration(system_coil.coil.force_applied, capsule.mass)
    acceleration_segment_length = round((end_coil_position - system_coil.position) / 2, 6)
    final_velocity = get_final_velocity(current_velocity, acceleration, acceleration_segment_length)
    traverse_time = get_traverse_time_for_acceleration(current_velocity, final_velocity, acceleration)
    energy_consumed = system_coil.coil.force_applied * acceleration_segment_length

    engagement_event_log(time_so_far, "coil_midpoint_accel", coil_id=system_coil.coil_id, velocity_mps=current_velocity, acceleration_mps2=acceleration, force_applied_n=system_coil.coil.force_applied, position_m=middle_coil_position)
    engagement_event_log(time_so_far + traverse_time, "coil_exit", coil_id=system_coil.coil_id, velocity_mps=final_velocity, acceleration_duration_s=traverse_time, acceleration_segment_length_m=acceleration_segment_length, energy_consumed_j=energy_consumed, position_m=end_coil_position)

    acceleration_segment = AccelerationSegment(
        segment_id=segment_id,
        related_coil_id=system_coil.coil_id,
        start_time=time_so_far,
        starting_position=middle_coil_position,
        length=acceleration_segment_length,
        start_velocity=current_velocity,
        final_velocity=final_velocity,
        acceleration=acceleration,
        traverse_time=traverse_time,
        energy_consumed=energy_consumed
    )

    return acceleration_segment


def run_last_segment(last_coil: SystemCoil, tube: Tube, current_velocity: float, time_so_far: float, segment_id: int) -> ConstantVelocitySegment:
    engagement_event_log(time_so_far, "run_end", position_m=tube.length, velocity_mps=current_velocity)

    constant_velocity_segment = ConstantVelocitySegment(
        segment_id=segment_id + 1,
        traverse_time=0,
        start_time=time_so_far,
        length=tube.length,
        starting_position=tube.length,
        related_coil_id=None,
        velocity=current_velocity,
    )

    return constant_velocity_segment