class Segment:
    """
    Base class for segments in the tube-capsule system.
    
    Attributes:
        id (int): Unique identifier for the segment
        traverse_time (float): Time taken by the capsule to traverse the segment, in seconds
        start_time (float): Start time of the capsule within the segment, in seconds
        length (float): Length of the segment, in meters
        starting_position (float): Starting position of the segment relative to the beginning of the tube, in meters
        related_coil_id (int, optional): ID of the coil associated with this segment. None for first segment.
    """
    
    def __init__(self, segment_id: int, traverse_time: float, start_time: float, length: float, starting_position: float, related_coil_id: int = None):
        self.id = segment_id
        self.traverse_time = traverse_time
        self.start_time = start_time
        self.length = length
        self.starting_position = starting_position
        self.related_coil_id = related_coil_id
    
    def __str__(self):
        return f"Segment(id={self.id}, traverse_time={self.traverse_time}s, start_time={self.start_time}s, length={self.length}m, starting_position={self.starting_position}m, related_coil_id={self.related_coil_id})"
 