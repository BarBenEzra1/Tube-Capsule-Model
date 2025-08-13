from app.domain.entities.system import System
import os, json
from pathlib import Path
import tempfile


def count_systems() -> int:
    try:
        with open(System.DATABASE_FILE_PATH, "rb") as f:
            # Count newline characters
            return sum(buf.count(b"\n") for buf in iter(lambda: f.read(1 << 20), b""))
    except FileNotFoundError:
        return 0


def get_next_id() -> int:
    try:
        with open(System.DATABASE_FILE_PATH, "rb") as f:
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


def read_all_systems():
    systems = []
    try:
        with open(System.DATABASE_FILE_PATH, "r", encoding="utf-8") as f:
            for line in f:
                if line.strip():
                    systems.append(json.loads(line))
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
                return System(system_id=record["id"], tube_id=record["tube_id"], coil_ids=record["coil_ids"], capsule_id=record["capsule_id"])
    return None



def update_system_by_id(system_id: int, new_tube_id: int, new_coil_ids: list[int], new_capsule_id: int) -> System | None:
    """
    Replace the record with id == system_id. Returns the updated System or None if not found.
    Uses an atomic write (temp file + replace) to avoid corruption.
    """
    if not System.DATABASE_FILE_PATH.exists():
        return None

    found = False
    updated_record = None

    System.DATABASE_FILE_PATH.parent.mkdir(parents=True, exist_ok=True)
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
                    rec["coil_ids"] = new_coil_ids
                    rec["capsule_id"] = new_capsule_id
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
    os.replace(tmp_path, System.DATABASE_FILE_PATH)

    return System(system_id=updated_record["id"], tube_id=updated_record["tube_id"], coil_ids=updated_record["coil_ids"], capsule_id=updated_record["capsule_id"])