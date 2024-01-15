from aiogram import Bot
from aiogram.types import BotCommandScopeDefault, BotCommand


async def set_bot_commands(bot: Bot):
    commands = [
        BotCommand(command="start", description="start"),
        BotCommand(command="addgif", description="добавить гифку с комару в базу"),
        BotCommand(command="catalog", description="каталог гифок с комару")
    ]

    return await bot.set_my_commands(
        commands,
        BotCommandScopeDefault()
    )
