from datetime import datetime


def add_timestamp() -> str:
    return datetime.now().isoformat()
