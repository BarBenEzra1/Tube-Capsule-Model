import json
from pathlib import Path


class Coil:
    """
    Represents an accelerating coil in the tube-capsule system.
    
    Attributes:
        id (int): Unique identifier for the coil
        length (float): Length of the coil in meters
        force_applied (float): Force applied by the coil in Newtons
    """

    DATABASE_FILE_PATH = Path("app/data/coil.jsonl") 

    def __init__(self, coil_id: int, length: float, force_applied: float, save_to_file: bool = True):
        self.id = coil_id
        self.length = length
        self.force_applied = force_applied

        if save_to_file:
            self.save_to_file()


    def save_to_file(self):
        with open(self.DATABASE_FILE_PATH, "a", encoding="utf-8") as f:
             f.write(json.dumps({"id": self.id, "length": self.length, "force_applied": self.force_applied}) + "\n")
    

    def __str__(self):
        return f"Coil(id={self.id}, length={self.length}m, force={self.force_applied}N)"