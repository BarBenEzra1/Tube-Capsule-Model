import os, json
from pathlib import Path


def get_next_id(path: Path) -> int:
    try:
        with open(path, "rb") as f:
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