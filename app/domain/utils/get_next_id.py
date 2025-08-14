import json
from pathlib import Path


def get_next_id(path: Path) -> int:
    """
    Get the next available ID by finding the maximum ID in the file and adding 1.
    """
    try:
        if not path.exists():
            return 1
            
        max_id = 0
        with open(path, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line:
                    try:
                        record = json.loads(line)
                        if "id" in record and isinstance(record["id"], int):
                            max_id = max(max_id, record["id"])
                    except json.JSONDecodeError:
                        continue  # Skip malformed lines
        
        return max_id + 1
    except Exception:
        return 1