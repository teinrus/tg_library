import asyncio
from aiogram import Bot, Dispatcher, types
from config import API_TOKEN
from handlers import navigator
from aiogram.fsm.storage.memory import MemoryStorage

async def main():
    bot = Bot(token=API_TOKEN)
    dp = Dispatcher(storage=MemoryStorage())  # ← обязательно!

    # Подключаем роутеры
    dp.include_router(navigator.router)




    print("✅ Бот запущен")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
