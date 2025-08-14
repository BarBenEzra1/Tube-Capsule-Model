from datetime import datetime, timezone
from pathlib import Path


LOG_FILE_PATH = Path("app/data/simulation.log")


def now_iso():
    return datetime.now(timezone.utc).isoformat(timespec="milliseconds").replace("+00:00", "Z")


def log(t_s, event, **kv):
    parts = [f"t={t_s:.4f}s event={event}"] + [f"{k}={v}" for k, v in kv.items()]
    with open(LOG_FILE_PATH, "a", encoding="utf-8") as f:
        f.write(" ".join(parts) + "\n")