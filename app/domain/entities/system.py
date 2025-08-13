import json
from pathlib import Path
from app.domain.entities.coil import Coil
from app.domain.entities.tube import Tube
from app.domain.entities.capsule import Capsule
from app.domain.services.coil_service import get_coil_by_id
from app.domain.services.tube_service import get_tube_by_id
from app.domain.services.capsule_service import get_capsule_by_id

class System:
    """
    Attributes:
        id (int): Unique identifier for the system
        tube_id (int): ID of the tube
        coil_ids_to_positions (dict[int, int]): IDs of the coils to their positions in the tube
        capsule_id (int): ID of the capsule
    """
    
    DATABASE_FILE_PATH = Path("app/data/system.jsonl") 

    def __init__(self, system_id: int, tube_id: int, coil_ids_to_positions: dict[int, int], capsule_id: int):
        self.is_system_valid()

        self.id = system_id
        self.tube_id = tube_id
        self.coil_ids_to_positions = coil_ids_to_positions
        self.capsule_id = capsule_id

        self.save_to_file()
    

    def save_to_file(self):
        with open(self.DATABASE_FILE_PATH, "a", encoding="utf-8") as f:
             f.write(json.dumps({"id": self.id, "tube_id": self.tube_id, "coil_ids_to_positions": self.coil_ids_to_positions, "capsule_id": self.capsule_id}) + "\n")


    def validate_coil_ids(self):
        if not Coil.DATABASE_FILE_PATH.exists():
            raise ValueError(f"Coil database file not found")

        for coil_id in self.coil_ids_to_positions.keys():
            if not get_coil_by_id(coil_id):
                raise ValueError(f"Coil with id {coil_id} not found")


    def validate_tube_id(self):
        if not Tube.DATABASE_FILE_PATH.exists():
            raise ValueError(f"Tube database file not found")

        if not get_tube_by_id(self.tube_id):
            raise ValueError(f"Tube with id {self.tube_id} not found")
    

    def validate_capsule_id(self):
        if not Capsule.DATABASE_FILE_PATH.exists():
            raise ValueError(f"Capsule database file not found")

        if not get_capsule_by_id(self.capsule_id):
            raise ValueError(f"Capsule with id {self.capsule_id} not found")
    

    def validate_coil_overlaps(self):
        """
        Validate that no coils overlap based on their position and length.
        The position + length of one coil should not be within the position + length of another coil.
        """
        coil_ranges = []
        
        # Collect all coil ranges (position to position + length)
        for coil_id, position in self.coil_ids_to_positions.items():
            coil = get_coil_by_id(coil_id)
            if coil:
                start = position
                end = position + coil.length
                coil_ranges.append((coil_id, start, end))
        
        # Check for overlaps between any two coils
        for i in range(len(coil_ranges)):
            for j in range(i + 1, len(coil_ranges)):
                coil1_id, start1, end1 = coil_ranges[i]
                coil2_id, start2, end2 = coil_ranges[j]
                
                # Check if coils overlap
                # Two ranges overlap if one starts before the other ends and vice versa
                if start1 < end2 and start2 < end1:
                    raise ValueError(f"Coils {coil1_id} and {coil2_id} overlap. "
                                   f"Coil {coil1_id} spans {start1}-{end1}, "
                                   f"Coil {coil2_id} spans {start2}-{end2}")

    def is_system_valid(self):
        self.validate_coil_ids()
        self.validate_tube_id()
        self.validate_capsule_id()
        self.validate_coil_overlaps()


    def __str__(self):
        return f"System(id={self.id}, tube_id={self.tube_id}, coil_ids_to_positions={self.coil_ids_to_positions}, capsule_id={self.capsule_id})"