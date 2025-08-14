from enum import Enum
from app.domain.entities.system import System
import os, json
from pathlib import Path
import tempfile
from app.domain.entities.coil import Coil
from app.domain.services.coil_service import get_coil_by_id
from app.domain.services.tube_service import get_tube_by_id
from app.domain.services.capsule_service import get_capsule_by_id


class UpdateSystemStatus(Enum):
    SUCCESS = "success"
    INVALID_SYSTEM = "invalid_system"
    NOT_FOUND = "not_found"


def read_all_systems():
    systems = []
    try:
        with open(System.DATABASE_FILE_PATH, "r", encoding="utf-8") as f:
            for line in f:
                if line.strip():
                    record = json.loads(line)
                    # Convert string keys to integers for coil_ids_to_positions
                    record["coil_ids_to_positions"] = {int(k): v for k, v in record["coil_ids_to_positions"].items()}
                    systems.append(record)
    except FileNotFoundError:
        pass
    return systems


def delete_system_by_id(system_id: int) -> bool:
    if not System.DATABASE_FILE_PATH.exists():
        return False

    found = False
    lines_to_keep = []

    with open(System.DATABASE_FILE_PATH, "r", encoding="utf-8") as f:
        for line in f:
            if not line.strip():
                continue
            record = json.loads(line)
            if record.get("id") == system_id:
                found = True
                continue  # skip adding this one
            lines_to_keep.append(line)

    if found:
        with open(System.DATABASE_FILE_PATH, "w", encoding="utf-8") as f:
            f.writelines(lines_to_keep)

    return found


def get_system_by_id(system_id: int) -> System | None:
    if not System.DATABASE_FILE_PATH.exists():
        return None

    with open(System.DATABASE_FILE_PATH, "r", encoding="utf-8") as f:
        for line in f:
            s = line.strip()
            if not s:
                continue
            try:
                record = json.loads(s)
            except json.JSONDecodeError:
                continue
            if record.get("id") == system_id:
                # Convert string keys to integers for coil_ids_to_positions
                coil_ids_to_positions = {int(k): v for k, v in record["coil_ids_to_positions"].items()}
                return System(system_id=record["id"], tube_id=record["tube_id"], coil_ids_to_positions=coil_ids_to_positions, capsule_id=record["capsule_id"], save_to_file=False)
    return None


def update_system_by_id(system_id: int, new_tube_id: int, new_coil_ids_to_positions: dict[int, int], new_capsule_id: int) -> tuple[UpdateSystemStatus, str | None]:
    """
    Replace the record with id == system_id. Returns the updated System or None if not found.
    Uses an atomic write (temp file + replace) to avoid corruption.
    """
    if not System.DATABASE_FILE_PATH.exists():
        return UpdateSystemStatus.NOT_FOUND, None

    found = False

    system = get_system_by_id(system_id)
    if system is None:
        return UpdateSystemStatus.NOT_FOUND, None
    
    new_system = System(system_id=system_id, tube_id=new_tube_id, coil_ids_to_positions=new_coil_ids_to_positions, capsule_id=new_capsule_id, save_to_file=False)
    try:
        new_system.is_system_valid()
    except ValueError as e:
        return UpdateSystemStatus.INVALID_SYSTEM, e.args[0]
    
    with tempfile.NamedTemporaryFile("w", delete=False, dir=str(System.DATABASE_FILE_PATH.parent), encoding="utf-8") as tmp:
        tmp_path = Path(tmp.name)
        with open(System.DATABASE_FILE_PATH, "r", encoding="utf-8") as src:
            for line in src:
                s = line.strip()
                if not s:
                    continue
                try:
                    rec = json.loads(s)
                except json.JSONDecodeError:
                    # keep malformed lines as-is to avoid data loss
                    tmp.write(line)
                    continue

                if rec.get("id") == system_id:
                    rec["tube_id"] = new_tube_id
                    rec["coil_ids_to_positions"] = new_coil_ids_to_positions
                    rec["capsule_id"] = new_capsule_id
                    found = True

                tmp.write(json.dumps(rec, ensure_ascii=False) + "\n")

    if not found:
        # no change; remove temp file
        try:
            tmp_path.unlink(missing_ok=True)
        finally:
            return UpdateSystemStatus.NOT_FOUND, None

    # atomic replace
    os.replace(tmp_path, System.DATABASE_FILE_PATH)

    return UpdateSystemStatus.SUCCESS, None


def get_system_coils(system: System) -> dict[int, Coil]:
    coils = {}
    
    for coil_id in system.coil_ids_to_positions.keys():
        coil = get_coil_by_id(coil_id)
        
        if coil:
            coils[coil_id] = coil
        
    return coils