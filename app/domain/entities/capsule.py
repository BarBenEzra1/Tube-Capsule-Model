class Capsule:
    """
    Attributes:
        id (int): Unique identifier for the capsule
        mass (float): Mass of the capsule in kilograms
        initial_velocity (float): Initial velocity of the capsule in m/s
    """
    
    def __init__(self, capsule_id: int, mass: float, initial_velocity: float):
        self.id = capsule_id
        self.mass = mass
        self.initial_velocity = initial_velocity
    
    def __str__(self):
        return f"Capsule(id={self.id}, mass={self.mass}kg, initial_velocity={self.initial_velocity}m/s)"