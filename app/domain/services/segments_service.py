from app.domain.entities.segment import Segment
from app.domain.entities.system import System
from app.domain.services.capsule_service import get_capsule_by_id
from app.domain.services.system_service import get_system_coils
from app.domain.entities.coil import Coil
from app.domain.entities.systemCoil import SystemCoil
from app.domain.services.tube_service import get_tube_by_id
from app.domain.utils.segments_utils import run_first_segment, get_constant_velocity_segment_followed_by_acceleration, get_acceleration_segment


# First segment starts at 0 and ends at the middle of the first coil
# Every coil contributes 2 segments:
# 1. Acceleration segment
#    - Acceleration segment is the segment where the capsule is accelerating, 
#      which is the segment between the middle of the current coil and the end of it
#
# 2. Constant velocity segment
#    - Constant velocity segment is the segment where the capsule is moving at a constant velocity
#      which is the segment between the end of the current coil and the middle of the next coil
#      or the segment between the end of the current coil and the end of the tube

def run_segments_simulation(system: System) -> list[Segment]:
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
            accel_seg = get_acceleration_segment(
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
            const_seg = get_constant_velocity_segment_followed_by_acceleration(
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

        return segments


def get_system_coils_by_asc_position(system: System) -> list[SystemCoil]:
    system_coils_by_asc_position = sorted(system.coil_ids_to_positions.items(), key=lambda x: x[1])
    coils: dict[int, Coil] = get_system_coils(system)

    return [SystemCoil(coil_id=coil_id, position=position, coil=coils[coil_id]) for coil_id, position in system_coils_by_asc_position]