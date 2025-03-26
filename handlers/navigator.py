from aiogram import Router, types, F
from aiogram.types import CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from services.file_manager import list_directory, get_full_path, get_all_subfolders
from keyboards.navigator import build_navigation_keyboard, build_upload_folder_keyboard, build_navigation_keyboard_with_select
from keyboards.main_menu import get_main_menu
from utils.is_admin import is_admin
from config import BASE_DIR
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
import os
from urllib.parse import quote, unquote
from keyboards.navigator import get_path_by_key
from keyboards.navigator import store_path


router = Router()

class AdminStates(StatesGroup):
    waiting_for_target_folder = State()
    waiting_for_subfolder_name = State()
    waiting_for_upload_folder = State()
    waiting_for_upload_navigation = State()
    waiting_for_file_upload = State()
    waiting_for_create_navigation = State()
    waiting_for_new_folder_name = State()

@router.message(F.text.in_({"/start", "📂 Открыть файлы"}))
async def start_command(message: types.Message):
    print(f"👤 ID пользователя: {message.from_user.id}")
    is_admin_user = is_admin(message.from_user.id)
    is_admin_user = is_admin(message.from_user.id)  
    reply_kb = get_main_menu(is_admin=is_admin_user)


    folders, files = list_directory()
    kb = build_navigation_keyboard("", folders, files)

    if kb:
        await message.answer("Выберите папку:", reply_markup=kb)
    else:
        await message.answer("📂 Папка пуста.")



@router.message(F.text.in_({"/help", "ℹ️ Помощь"}))
async def help_command(message: types.Message):
    text = (
        "🤖 *Файловая библиотека*\n\n"
        "Этот бот предназначен для удобного доступа к файлам и папкам прямо из Telegram.\n"
        "Здесь вы можете найти необходимую документацию, инструкции, отчёты и другие полезные материалы.\n\n"
        "📂 Используйте кнопку или команду /start для начала навигации.\n"
        "Если возникли вопросы — напишите разработчику 😉"
    )
    await message.answer(text, parse_mode="Markdown", reply_markup=get_main_menu())

@router.callback_query(F.data.startswith("open:"))
async def open_folder(callback: CallbackQuery):
    key = callback.data.split(":", 1)[1]
    path = get_path_by_key(key)

    folders, files = list_directory(path)
    kb = build_navigation_keyboard(path, folders, files)
    if kb:
        await callback.message.edit_text(f"📂 Папка: /{path or ''}", reply_markup=kb)
    else:
        await callback.message.edit_text("📂 Эта папка пуста.")


@router.callback_query(F.data.startswith("file:"))
async def send_file(callback: CallbackQuery):
    key = callback.data.split(":", 1)[1]
    path = get_path_by_key(key)
    full_path = get_full_path(path)

    try:
        await callback.message.answer_document(types.FSInputFile(full_path))
        await callback.answer("✅ Файл отправлен")
    except Exception as e:
        print(f"Ошибка при отправке файла: {e}")
        await callback.answer("❌ Ошибка при отправке файла", show_alert=True)
# --- Админ-панель ---
@router.message(F.text == "🛠 Админ-панель")
async def admin_panel(message: types.Message, state: FSMContext):
    if not is_admin(message.from_user.id):
        return await message.answer("⛔ У вас нет доступа.")

    folders, _ = list_directory()
    if not folders:
        return await message.answer("📁 В корне нет папок для выбора.")

    kb = InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(
                text=f"📁 {name}",
                callback_data=f"admin_create:{store_path(name)}"
            )
        ]
        for name in folders
    ])
    await message.answer("Выберите папку, в которую хотите создать подпапку:", reply_markup=kb)
    await state.set_state(AdminStates.waiting_for_target_folder)

# --- Обработка выбора папки для создания подпапки ---
@router.callback_query(F.data.startswith("admin_create:"), AdminStates.waiting_for_target_folder)
async def choose_target_folder(callback: CallbackQuery, state: FSMContext):
    key = callback.data.split(":", 1)[1]
    folder = get_path_by_key(key)

    await state.update_data(target_folder=folder)
    await callback.message.answer(f"✏️ Введите название новой папки внутри `{folder}`", parse_mode="Markdown")
    await state.set_state(AdminStates.waiting_for_subfolder_name)

# --- Создание новой подпапки ---
@router.message(AdminStates.waiting_for_subfolder_name)
async def create_subfolder(message: types.Message, state: FSMContext):
    data = await state.get_data()
    parent = data.get("target_folder")
    subfolder = message.text.strip()

    if ".." in subfolder or subfolder.startswith("/"):
        await message.answer("⛔ Неверное имя папки.")
        await state.clear()
        return

    full_path = os.path.join(BASE_DIR, parent, subfolder)
    try:
        os.makedirs(full_path, exist_ok=True)
        await message.answer(f"✅ Папка `{parent}/{subfolder}` создана.", parse_mode="Markdown")
    except Exception as e:
        await message.answer(f"❌ Ошибка при создании папки: {e}")
    await state.clear()

@router.message(F.text == "🗂 Создать папку")
async def start_folder_create(message: types.Message, state: FSMContext):
    if not is_admin(message.from_user.id):
        return await message.answer("⛔ У вас нет доступа.")

    folders, _ = list_directory("")
    kb = build_navigation_keyboard_with_select("", folders, "createpath")
    await message.answer("📁 Выберите, где создать новую папку:", reply_markup=kb)
    await state.set_state(AdminStates.waiting_for_create_navigation)
@router.message(F.text == "📤 Загрузить файл")
async def start_upload_navigation(message: types.Message, state: FSMContext):
    if not is_admin(message.from_user.id):
        return await message.answer("⛔ У вас нет доступа.")

    folders, _ = list_directory("")  # корень
    kb = build_upload_folder_keyboard("", folders)
    await message.answer("📁 Выберите папку для загрузки файла:", reply_markup=kb)
    await state.set_state(AdminStates.waiting_for_upload_navigation)

    
@router.callback_query(F.data.startswith("createpath:"), AdminStates.waiting_for_create_navigation)
async def navigate_create_folders(callback: CallbackQuery, state: FSMContext):
    key = callback.data.split(":", 1)[1]
    path = get_path_by_key(key)

    folders, _ = list_directory(path)
    kb = build_navigation_keyboard_with_select(path, folders, "createpath")
    await callback.message.edit_text(f"📂 Текущая папка: /{path or ''}", reply_markup=kb)
@router.callback_query(F.data.startswith("createpath_select:"), AdminStates.waiting_for_create_navigation)
async def confirm_create_folder_path(callback: CallbackQuery, state: FSMContext):
    key = callback.data.split(":", 1)[1]
    path = get_path_by_key(key)

    await state.update_data(target_folder=path)
    await callback.message.answer(f"✏️ Введите название новой папки, которую хотите создать внутри `{path}`", parse_mode="Markdown")
    await state.set_state(AdminStates.waiting_for_new_folder_name)
@router.message(AdminStates.waiting_for_new_folder_name)
async def create_subfolder_from_nav(message: types.Message, state: FSMContext):
    data = await state.get_data()
    parent = data.get("target_folder")
    subfolder = message.text.strip()

    if ".." in subfolder or subfolder.startswith("/"):
        await message.answer("⛔ Неверное имя папки.")
        await state.clear()
        return

    full_path = os.path.join(BASE_DIR, parent, subfolder)
    try:
        os.makedirs(full_path, exist_ok=True)
        await message.answer(f"✅ Папка `{parent}/{subfolder}` создана.", parse_mode="Markdown")
    except Exception as e:
        await message.answer(f"❌ Ошибка при создании папки: {e}")

    await state.clear()

@router.callback_query(F.data.startswith("uploadnav:"), AdminStates.waiting_for_upload_navigation)
async def navigate_upload_folders(callback: CallbackQuery, state: FSMContext):
    key = callback.data.split(":", 1)[1]
    path = get_path_by_key(key)

    folders, _ = list_directory(path)
    kb = build_upload_folder_keyboard(path, folders)
    await callback.message.edit_text(f"📂 Папка: /{path or ''}", reply_markup=kb)
@router.message(AdminStates.waiting_for_file_upload, F.document)
async def handle_file_upload(message: types.Message, state: FSMContext):
    data = await state.get_data()
    folder = data.get("upload_folder")
    document = message.document

    if not document:
        return await message.answer("⛔ Ожидается файл.")

    file_path = os.path.join(BASE_DIR, folder, document.file_name)

    # Получаем файл через Bot API
    file = await message.bot.get_file(document.file_id)
    await message.bot.download_file(file.file_path, destination=file_path)

    await message.answer(f"✅ Файл `{document.file_name}` загружен в `{folder}`.", parse_mode="Markdown")
    await state.clear()

@router.callback_query(F.data.startswith("uploadselect:"), AdminStates.waiting_for_upload_navigation)
async def select_folder_for_upload(callback: CallbackQuery, state: FSMContext):
    key = callback.data.split(":", 1)[1]
    path = get_path_by_key(key)

    if not path:
        return await callback.message.answer("⛔ Ошибка: путь не найден.")

    await state.update_data(upload_folder=path)
    await callback.message.answer(f"📎 Отправьте файл, который нужно загрузить в `{path}`", parse_mode="Markdown")
    await state.set_state(AdminStates.waiting_for_file_upload)
