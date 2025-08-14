from app.domain.entities.segment import Segment


class ConstantVelocitySegment(Segment):
    """
    A segment where the capsule travels at constant velocity.
    
    Attributes:
        id (int): Unique identifier for the segment
        traverse_time (float): Time taken by the capsule to traverse the segment, in seconds
        start_time (float): Start time of the capsule within the segment, in seconds
        length (float): Length of the segment, in meters
        starting_position (float): Starting position of the segment relative to the beginning of the tube, in meters
        related_coil_id (int, optional): ID of the coil associated with this segment. None for first segment.
        velocity (float): Constant velocity of the capsule in this segment, in m/s
    """
    
    def __init__(self, segment_id: int, traverse_time: float, start_time: float, length: float, starting_position: float, velocity: float, related_coil_id: int = None):
        super().__init__(segment_id, traverse_time, start_time, length, starting_position, related_coil_id)
        self.velocity = velocity
    

    def __str__(self):
        return f"ConstantVelocitySegment(id={self.id}, traverse_time={self.traverse_time}s, start_time={self.start_time}s, length={self.length}m, starting_position={self.starting_position}m, velocity={self.velocity}m/s)"