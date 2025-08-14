import math


def get_traverse_time_for_constant_velocity(velocity: float, length: float) -> float:
    return length / velocity

    
def get_traverse_time_for_acceleration(initial_velocity: float, final_velocity: float, acceleration: float) -> float:
    return (final_velocity - initial_velocity) / acceleration


def get_final_velocity(initial_velocity: float, acceleration: float, length: float) -> float:
    return math.sqrt(initial_velocity**2 + 2 * acceleration * length)
    
    
def get_acceleration(force_applied: float, mass: float) -> float:
    return force_applied / mass
