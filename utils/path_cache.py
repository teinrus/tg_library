# utils/path_cache.py
import uuid

path_map = {}

def save_path(path: str) -> str:
    key = str(uuid.uuid4())  # можно использовать и hash(path), но uuid безопаснее
    path_map[key] = path
    return key

def get_path(key: str) -> str:
    return path_map.get(key)
