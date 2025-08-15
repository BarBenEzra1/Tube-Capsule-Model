from datetime import datetime, timezone
from pathlib import Path
import json


LOG_FILE_PATH = Path(f"app/data/logs/simulation_{datetime.now(timezone.utc).strftime('%Y-%m-%d_%H-%M-%S')}.log")
LOG_JSON_FILE_PATH = Path(f"app/data/logs/simulation_{datetime.now(timezone.utc).strftime('%Y-%m-%d_%H-%M-%S')}.jsonl")


def now_iso():
    return datetime.now(timezone.utc).isoformat(timespec="milliseconds").replace("+00:00", "Z")


def log(t_s, event, **kv):
    parts = [f"t={t_s:.4f}s   event={event}   "] + [f"{k}={v}   " for k, v in kv.items()]
    with open(LOG_FILE_PATH, "a", encoding="utf-8") as f:
        f.write(" ".join(parts) + "\n")
    
    json_entry = {
        "t": round(t_s, 4),
        "event": event,
        **kv
    }
    with open(LOG_JSON_FILE_PATH, "a", encoding="utf-8") as f:
        f.write(json.dumps(json_entry, ensure_ascii=False) + "\n")