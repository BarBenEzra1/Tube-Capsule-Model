class Coil:
    """
    Represents an accelerating coil in the tube-capsule system.
    
    Attributes:
        id (int): Unique identifier for the coil
        length (float): Length of the coil in meters
        force_applied (float): Force applied by the coil in Newtons
    """
    
    def __init__(self, coil_id: int, length: float, force_applied: float):
        self.id = coil_id
        self.length = length
        self.force_applied = force_applied
    
    def __str__(self):
        return f"Coil(id={self.id}, length={self.length}m, force={self.force_applied}N)"