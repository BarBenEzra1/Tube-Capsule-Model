from app.domain.entities.capsule import Capsule
import os, json
from pathlib import Path
import tempfile


def count_capsules() -> int:
    try:
        with open(Capsule.DATABASE_FILE_PATH, "rb") as f:
            # Count newline characters
            return sum(buf.count(b"\n") for buf in iter(lambda: f.read(1 << 20), b""))
    except FileNotFoundError:
        return 0


def get_next_id() -> int:
    try:
        with open(Capsule.DATABASE_FILE_PATH, "rb") as f:
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


def read_all_capsules():
    capsules = []
    try:
        with open(Capsule.DATABASE_FILE_PATH, "r", encoding="utf-8") as f:
            for line in f:
                if line.strip():
                    capsules.append(json.loads(line))
    except FileNotFoundError:
        pass
    return capsules


def delete_capsule_by_id(capsule_id: int) -> bool:
    if not Capsule.DATABASE_FILE_PATH.exists():
        return False

    found = False
    lines_to_keep = []

    with open(Capsule.DATABASE_FILE_PATH, "r", encoding="utf-8") as f:
        for line in f:
            if not line.strip():
                continue
            record = json.loads(line)
            if record.get("id") == capsule_id:
                found = True
                continue  # skip adding this one
            lines_to_keep.append(line)

    if found:
        with open(Capsule.DATABASE_FILE_PATH, "w", encoding="utf-8") as f:
            f.writelines(lines_to_keep)

    return found


def get_capsule_by_id(capsule_id: int) -> Capsule | None:
    if not Capsule.DATABASE_FILE_PATH.exists():
        return None

    with open(Capsule.DATABASE_FILE_PATH, "r", encoding="utf-8") as f:
        for line in f:
            s = line.strip()
            if not s:
                continue
            try:
                record = json.loads(s)
            except json.JSONDecodeError:
                continue
            if record.get("id") == capsule_id:
                return Capsule(capsule_id=record["id"], mass=record["mass"], initial_velocity=record["initial_velocity"])
    return None



def update_capsule_by_id(capsule_id: int, new_mass: float, new_initial_velocity: float) -> Capsule | None:
    """
    Replace the record with id == capsule_id. Returns the updated Capsule or None if not found.
    Uses an atomic write (temp file + replace) to avoid corruption.
    """
    if not Capsule.DATABASE_FILE_PATH.exists():
        return None

    found = False
    updated_record = None

    Capsule.DATABASE_FILE_PATH.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.NamedTemporaryFile("w", delete=False, dir=str(Capsule.DATABASE_FILE_PATH.parent), encoding="utf-8") as tmp:
        tmp_path = Path(tmp.name)
        with open(Capsule.DATABASE_FILE_PATH, "r", encoding="utf-8") as src:
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

                if rec.get("id") == capsule_id:
                    rec["mass"] = new_mass
                    rec["initial_velocity"] = new_initial_velocity
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
    os.replace(tmp_path, Capsule.DATABASE_FILE_PATH)

    # Important: avoid re-saving when constructing the domain object
    return Capsule(capsule_id=updated_record["id"], mass=updated_record["mass"], initial_velocity=updated_record["initial_velocity"])