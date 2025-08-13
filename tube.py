class Tube:
    """
    Attributes:
        id (int): Unique identifier for the tube
        length (float): Length of the tube in meters
    """
    
    def __init__(self, tube_id: int, length: float):
        self.id = tube_id
        self.length = length
    
    def __str__(self):
        return f"Tube(id={self.id}, length={self.length}m)"