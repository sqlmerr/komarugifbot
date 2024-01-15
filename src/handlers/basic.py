import random

from loguru import logger

from aiogram import Router, F
from aiogram.types import Message
from aiogram.filters import Command

from src.db import User
from src import stickers

router = Router()


@router.message(Command("start"))
async def start_cmd(message: Message, user: User):
    if not user:
        user = User(
            user_id=message.from_user.id
        )

        await user.insert()
        logger.debug(f"registered new user with id {message.from_user.id}")

    await message.answer_sticker(random.choice(stickers))
    await message.reply(f"<b>Привет, {message.from_user.full_name}.</b>\nЯ бот - гифки с комару. Думаю все понятно, здесь можно получить разные гифки с комару, или добавить свои!")
