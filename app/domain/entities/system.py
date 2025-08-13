import json
from pathlib import Path
from app.domain.entities.coil import Coil
from app.domain.entities.tube import Tube
from app.domain.entities.capsule import Capsule

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
        self.is_system_valid()

        self.id = system_id
        self.tube_id = tube_id
        self.coil_ids = coil_ids
        self.capsule_id = capsule_id

        self.save_to_file()
    

    def save_to_file(self):
        with open(self.DATABASE_FILE_PATH, "a", encoding="utf-8") as f:
             f.write(json.dumps({"id": self.id, "tube_id": self.tube_id, "coil_ids": self.coil_ids, "capsule_id": self.capsule_id}) + "\n")


    def validate_coil_ids(self):
        for coil_id in self.coil_ids:
            if not Coil.DATABASE_FILE_PATH.exists():
                raise ValueError(f"Coil with id {coil_id} not found")


    def validate_tube_id(self):
        if not Tube.DATABASE_FILE_PATH.exists():
            raise ValueError(f"Tube with id {self.tube_id} not found")
    

    def validate_capsule_id(self):
        if not Capsule.DATABASE_FILE_PATH.exists():
            raise ValueError(f"Capsule with id {self.capsule_id} not found")
    

    def is_system_valid(self):
        self.validate_coil_ids()
        self.validate_tube_id()
        self.validate_capsule_id()




    def __str__(self):
        return f"System(id={self.id}, tube_id={self.tube_id}, coil_ids={self.coil_ids}, capsule_id={self.capsule_id})"