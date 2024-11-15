import logging
from aiogram import Bot, Dispatcher, types, Router
from aiogram.filters import Command
from aiogram.types import ChatMemberStatus
from aiogram.types import ChatPermissions
from database import add_user, init_db
import asyncio

# Укажите ваш токен и ID канала
API_TOKEN = '7130345766:AAEHrYTxSEnBCvWB4BNuOMp40kQmcRGtZX8'
CHAT_ID = '@testbut8'

# Инициализация логгера
logging.basicConfig(level=logging.INFO)

# Инициализация бота
bot = Bot(token=API_TOKEN)
dp = Dispatcher()

# Инициализация роутера
router = Router()

# Инициализация базы данных
init_db()


async def check_user_in_channel(user_id):
    """Проверка, состоит ли пользователь уже в канале"""
    try:
        member = await bot.get_chat_member(chat_id=CHAT_ID, user_id=user_id)
        return member.status in [ChatMemberStatus.MEMBER, ChatMemberStatus.ADMINISTRATOR, ChatMemberStatus.OWNER]
    except Exception as e:
        logging.error(f"Ошибка при проверке статуса пользователя: {e}")
        return False


@router.message(Command("start"))
async def start_command(message: types.Message):
    user_id = message.from_user.id
    username = message.from_user.username

    # Проверка, состоит ли пользователь уже в канале
    is_member = await check_user_in_channel(user_id)

    if is_member:
        # Пользователь уже в канале, отправляем сообщение и ссылку на канал
        await message.answer("Вы уже состоите в нашем канале! Вот ссылка для перехода:")
        await message.answer(f"👉 [Перейти в канал](https://t.me/{CHAT_ID[1:]})", disable_web_page_preview=True)
    else:
        # Попытка одобрить запрос на присоединение к каналу (если это возможно)
        try:
            await bot.approve_chat_join_request(chat_id=CHAT_ID, user_id=user_id)
            await message.answer("Вы успешно присоединились к каналу! Добро пожаловать!")

            # Сохранение данных в базе
            add_user(user_id, username)
        except Exception as e:
            await message.answer("Не удалось добавить вас в канал. Пожалуйста, свяжитесь с администратором.")
            logging.error(f"Ошибка при добавлении в канал: {e}")


async def main():
    dp.include_router(router)
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
