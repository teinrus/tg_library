import os
from config import BASE_DIR
from urllib.parse import quote, unquote
def list_directory(path=""):
    full_path = os.path.join(BASE_DIR, path)
    items = os.listdir(full_path)
    folders = []
    files = []

    for item in items:
        full_item_path = os.path.join(full_path, item)
        if os.path.isdir(full_item_path):
            folders.append(item)
        else:
            files.append(item)

    return folders, files

def get_full_path(relative_path):
    return os.path.join(BASE_DIR, relative_path)




def get_all_subfolders(base_path):
    subfolders = []
    for root, dirs, _ in os.walk(base_path):
        for d in dirs:
            full_path = os.path.join(root, d)
            rel_path = os.path.relpath(full_path, base_path)
            subfolders.append(rel_path)
    return subfolders
