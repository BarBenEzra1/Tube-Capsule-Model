import json
from pathlib import Path


class Capsule:
    """
    Attributes:
        id (int): Unique identifier for the capsule
        mass (float): Mass of the capsule in kilograms
        initial_velocity (float): Initial velocity of the capsule in m/s
    """
    
    DATABASE_FILE_PATH = Path("app/data/capsule.jsonl") 


    def __init__(self, capsule_id: int, mass: float, initial_velocity: float):
        self.id = capsule_id
        self.mass = mass
        self.initial_velocity = initial_velocity

        self.save_to_file()


    def save_to_file(self):
        with open(self.DATABASE_FILE_PATH, "a", encoding="utf-8") as f:
            f.write(json.dumps({"id": self.id, "mass": self.mass, "initial_velocity": self.initial_velocity}) + "\n")
    

    def __str__(self):
        return f"Capsule(id={self.id}, mass={self.mass}kg, initial_velocity={self.initial_velocity}m/s)"