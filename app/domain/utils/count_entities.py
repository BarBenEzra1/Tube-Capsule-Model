from pathlib import Path


def count_entities(path: Path) -> int:
    try:
        with open(path, "rb") as f:
            # Count newline characters
            return sum(buf.count(b"\n") for buf in iter(lambda: f.read(1 << 20), b""))
    except FileNotFoundError:
        return 0
