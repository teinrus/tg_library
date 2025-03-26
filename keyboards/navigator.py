from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
import os
import uuid

# Временное хранилище путей (можно заменить на Redis, если нужно постоянство)
callback_storage = {}

def store_path(path: str) -> str:
    key = str(uuid.uuid4())[:8]
    callback_storage[key] = path
    return key

def get_path_by_key(key: str) -> str:
    return callback_storage.get(key)

def build_navigation_keyboard(path, folders, files):
    keyboard = []

    for folder in folders:
        folder_path = f"{path}/{folder}" if path else folder
        key = store_path(folder_path)
        keyboard.append([
            InlineKeyboardButton(
                text=f"📁 {folder}",
                callback_data=f"open:{key}"
            )
        ])

    for file in files:
        file_path = f"{path}/{file}" if path else file
        key = store_path(file_path)
        keyboard.append([
            InlineKeyboardButton(
                text=f"📄 {file}",
                callback_data=f"file:{key}"
            )
        ])

    if path:
        parent = "/".join(path.split("/")[:-1])
        key = store_path(parent)
        keyboard.append([
            InlineKeyboardButton(
                text="🔙 Назад",
                callback_data=f"open:{key}"
            )
        ])

    return InlineKeyboardMarkup(inline_keyboard=keyboard) if keyboard else None

def build_upload_folder_keyboard(current_path, folders):
    buttons = []

    for folder in folders:
        folder_path = os.path.join(current_path, folder) if current_path else folder
        key = store_path(folder_path)
        buttons.append([
            InlineKeyboardButton(
                text=f"📁 {folder}",
                callback_data=f"uploadnav:{key}"
            )
        ])

    key = store_path(current_path)
    buttons.append([
        InlineKeyboardButton(
            text="✅ Выбрать эту папку",
            callback_data=f"uploadselect:{key}"
        )
    ])

    if current_path:
        parent_path = os.path.dirname(current_path)
        key = store_path(parent_path)
        buttons.append([
            InlineKeyboardButton(
                text="🔙 Назад",
                callback_data=f"uploadnav:{key}"
            )
        ])

    return InlineKeyboardMarkup(inline_keyboard=buttons)

def build_navigation_keyboard_with_select(current_path, folders, action_prefix: str):
    buttons = []

    for folder in folders:
        folder_path = os.path.join(current_path, folder) if current_path else folder
        key = store_path(folder_path)
        buttons.append([
            InlineKeyboardButton(
                text=f"📁 {folder}",
                callback_data=f"{action_prefix}:{key}"
            )
        ])

    key = store_path(current_path)
    buttons.append([
        InlineKeyboardButton(
            text="✅ Выбрать эту папку",
            callback_data=f"{action_prefix}_select:{key}"
        )
    ])

    if current_path:
        parent_path = os.path.dirname(current_path)
        key = store_path(parent_path)
        buttons.append([
            InlineKeyboardButton(
                text="🔙 Назад",
                callback_data=f"{action_prefix}:{key}"
            )
        ])

    return InlineKeyboardMarkup(inline_keyboard=buttons)