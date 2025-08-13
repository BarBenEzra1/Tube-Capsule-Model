import json
from pathlib import Path


class System:
    """
    Attributes:
        id (int): Unique identifier for the system
        tube_id (int): ID of the tube
        coil_ids (list[int]): IDs of the coils
        capsule_id (int): ID of the capsule
    """
    
    DATABASE_FILE_PATH = Path("app/data/system.jsonl") 

    def __init__(self, system_id: int, tube_id: int, coil_ids: list[int], capsule_id: int):
        self.id = system_id
        self.tube_id = tube_id
        self.coil_ids = coil_ids
        self.capsule_id = capsule_id

        self.save_to_file()
    

    def save_to_file(self):
        with open(self.DATABASE_FILE_PATH, "a", encoding="utf-8") as f:
             f.write(json.dumps({"id": self.id, "tube_id": self.tube_id, "coil_ids": self.coil_ids, "capsule_id": self.capsule_id}) + "\n")


    def __str__(self):
        return f"System(id={self.id}, tube_id={self.tube_id}, coil_ids={self.coil_ids}, capsule_id={self.capsule_id})"