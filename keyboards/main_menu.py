from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

def get_main_menu(is_admin=False):
    keyboard = [
        [KeyboardButton(text="📂 Открыть файлы")],
        [KeyboardButton(text="ℹ️ Помощь")]
    ]


    keyboard.append([KeyboardButton(text="📤 Загрузить файл")])
    keyboard.append([KeyboardButton(text="🗂 Создать папку")])  
    return ReplyKeyboardMarkup(keyboard=keyboard, resize_keyboard=True)
