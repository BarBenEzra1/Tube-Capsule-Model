import gzip
from datetime import datetime, timezone


def compress_json(json_content: str) -> tuple[bytes, dict]:
    json_content = json_content.model_dump_json(indent=2)
    
    timestamp = datetime.now(timezone.utc).strftime('%Y-%m-%d_%H-%M-%S')
    
    compressed_content = gzip.compress(json_content.encode('utf-8'))
    filename = f"simulation_result_{timestamp}.json.gz"
    headers = {
        "Content-Disposition": f'attachment; filename="{filename}"',
        "Content-Type": "application/gzip"
    }

    return compressed_content, headers