from app.domain.entities.coil import Coil
import os, json
from pathlib import Path
import tempfile

from app.domain.schemas.system_schemas import CoilPosition


def read_all_coils():
    coils = []
    try:
        with open(Coil.DATABASE_FILE_PATH, "r", encoding="utf-8") as f:
            for line in f:
                if line.strip():
                    coils.append(json.loads(line))
    except FileNotFoundError:
        pass
    return coils


def delete_coil_by_id(coil_id: int) -> bool:
    if not Coil.DATABASE_FILE_PATH.exists():
        return False

    found = False
    lines_to_keep = []

    with open(Coil.DATABASE_FILE_PATH, "r", encoding="utf-8") as f:
        for line in f:
            if not line.strip():
                continue
            record = json.loads(line)
            if record.get("id") == coil_id:
                found = True
                continue  # skip adding this one
            lines_to_keep.append(line)

    if found:
        with open(Coil.DATABASE_FILE_PATH, "w", encoding="utf-8") as f:
            f.writelines(lines_to_keep)

    return found


def get_coil_by_id(coil_id: int) -> Coil | None:
    if not Coil.DATABASE_FILE_PATH.exists():
        return None

    with open(Coil.DATABASE_FILE_PATH, "r", encoding="utf-8") as f:
        for line in f:
            s = line.strip()
            if not s:
                continue
            try:
                record = json.loads(s)
            except json.JSONDecodeError:
                continue
            if record.get("id") == coil_id:
                return Coil(coil_id=record["id"], length=record["length"], force_applied=record["force_applied"], save_to_file=False)
    return None


def update_coil_by_id(coil_id: int, new_length: float, new_force_applied: float) -> Coil | None:
    """
    Replace the record with id == coil_id. Returns the updated Coil or None if not found.
    Uses an atomic write (temp file + replace) to avoid corruption.
    """
    if not Coil.DATABASE_FILE_PATH.exists():
        return None

    found = False
    updated_record = None

    Coil.DATABASE_FILE_PATH.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.NamedTemporaryFile("w", delete=False, dir=str(Coil.DATABASE_FILE_PATH.parent), encoding="utf-8") as tmp:
        tmp_path = Path(tmp.name)
        with open(Coil.DATABASE_FILE_PATH, "r", encoding="utf-8") as src:
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

                if rec.get("id") == coil_id:
                    rec["length"] = new_length
                    rec["force_applied"] = new_force_applied
                    found = True
                    updated_record = rec

                tmp.write(json.dumps(rec, ensure_ascii=False) + "\n")

    if not found:
        # no change; remove temp file
        try:
            tmp_path.unlink(missing_ok=True)
        finally:
            return None

    # atomic replace
    os.replace(tmp_path, Coil.DATABASE_FILE_PATH)

    return Coil(coil_id=updated_record["id"], length=updated_record["length"], force_applied=updated_record["force_applied"], save_to_file=False)


def convert_coil_positions_to_dict(coil_positions: list[CoilPosition]) -> dict[int, float]:
    """Convert list of CoilPosition objects to dictionary format expected by System entity"""
    return {cp.coilId: cp.position for cp in coil_positions}


def convert_dict_to_coil_positions(coil_dict: dict[int, float]) -> list[CoilPosition]:
    """Convert dictionary format to list of CoilPosition objects for API responses"""
    return [CoilPosition(coilId=coil_id, position=position) for coil_id, position in coil_dict.items()]
