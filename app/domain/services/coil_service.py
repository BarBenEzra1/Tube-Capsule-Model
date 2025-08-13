from app.domain.entities.coil import Coil
import os, json
from pathlib import Path
import tempfile


def count_coils() -> int:
    try:
        with open(Coil.DATABASE_FILE_PATH, "rb") as f:
            # Count newline characters
            return sum(buf.count(b"\n") for buf in iter(lambda: f.read(1 << 20), b""))
    except FileNotFoundError:
        return 0


def get_next_id() -> int:
    try:
        with open(Coil.DATABASE_FILE_PATH, "rb") as f:
            if f.seek(0, os.SEEK_END) == 0:  # empty
                return 1
            # scan back to last line
            pos = -1
            while -pos <= f.tell():
                f.seek(pos, os.SEEK_END)
                if f.read(1) == b"\n":
                    break
                pos -= 1
            last = f.readline().decode("utf-8").strip()
            return (json.loads(last)["id"] if last else 0) + 1
    except FileNotFoundError:
        return 1


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
                return Coil(coil_id=record["id"], length=record["length"], force_applied=record["force_applied"])
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

    # Important: avoid re-saving when constructing the domain object
    return Coil(coil_id=updated_record["id"], length=updated_record["length"], force_applied=updated_record["force_applied"])