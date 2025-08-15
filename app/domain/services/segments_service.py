from app.domain.entities.segment import Segment
from app.domain.entities.system import System
from app.domain.services.capsule_service import get_capsule_by_id
from app.domain.services.system_service import get_system_coils
from app.domain.entities.coil import Coil
from app.domain.entities.systemCoil import SystemCoil
from app.domain.services.tube_service import get_tube_by_id
from app.domain.utils.segments_utils import run_first_segment, run_constant_velocity_segment, run_acceleration_segment, run_last_segment

# The tube is treated as being divided into segments based on coil positions.
# If the tube contains no coils, it is treated as a single constant velocity segment from start to end.
# For tubes with coils, the segmentation follows this pattern:
# 1. First segment (constant velocity): From the tube's beginning (position 0) to the midpoint of the first coil.
# 2. For each coil, two segments are created:
#   •	Acceleration segment: From the coil's midpoint to the coil's end, where the capsule accelerates due to the coil's force.
#   •	Constant velocity segment: From the coil’s end to either the midpoint of the next coil (if it exists) or to the tube’s end (for the last coil).

def run_simulation_and_get_segments(system: System) -> list[Segment]:
    capsule = get_capsule_by_id(system.capsule_id)
    system_coils = get_system_coils_by_asc_position(system)
    tube = get_tube_by_id(system.tube_id)

    segments = []

    first_segment = run_first_segment(system_coils, capsule, tube)
    segments.append(first_segment)

    time_so_far = first_segment.traverse_time
    current_velocity = capsule.initial_velocity
    seg_index = 1

    for i, coil in enumerate(system_coils):
        # 1) Acceleration segment
        accel_seg = run_acceleration_segment(
            coil, 
            capsule, 
            current_velocity, 
            time_so_far, 
            seg_index
        )
        segments.append(accel_seg)

        time_so_far += accel_seg.traverse_time
        current_velocity = accel_seg.final_velocity
        seg_index += 1

        # 2) Constant-velocity segment
        next_coil = system_coils[i + 1] if i + 1 < len(system_coils) else None
        const_seg = run_constant_velocity_segment(
            coil, 
            next_coil,
            tube,
            current_velocity,
            time_so_far, 
            seg_index
        )

        segments.append(const_seg)

        time_so_far += const_seg.traverse_time
        seg_index += 1

    if len(system_coils) > 0:
        last_segment = run_last_segment(system_coils[-1], tube, current_velocity, time_so_far, seg_index)
        segments.append(last_segment)

    return segments


def get_system_coils_by_asc_position(system: System) -> list[SystemCoil]:
    system_coils_by_asc_position = dict(sorted(system.coil_ids_to_positions.items(), key=lambda x: x[1]))
    coils: dict[int, Coil] = get_system_coils(system)

    return [SystemCoil(coil_id=coil_id, position=position, coil=coils[coil_id]) for coil_id, position in system_coils_by_asc_position.items()]