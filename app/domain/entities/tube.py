import json
from pathlib import Path


class Tube:
    """
    Attributes:
        id (int): Unique identifier for the tube
        length (float): Length of the tube in meters
    """
    
    DATABASE_FILE_PATH = Path("app/data/tube.jsonl") 

    def __init__(self, tube_id: int, length: float):
        self.id = tube_id
        self.length = length

        self.save_to_file()
    

    def save_to_file(self):
        with open(self.DATABASE_FILE_PATH, "a", encoding="utf-8") as f:
             f.write(json.dumps({"id": self.id, "length": self.length}) + "\n")


    def __str__(self):
        return f"Tube(id={self.id}, length={self.length}m)"