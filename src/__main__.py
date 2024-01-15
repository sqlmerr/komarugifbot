import os
import dotenv
import asyncio

from loguru import logger

from aiogram import Bot, Dispatcher, F
from aiogram.enums import ParseMode
from src.handlers import register_routers
from src.middlewares import UserMiddleware, ThrottlingMiddleware

from src.commands import set_bot_commands
from src.db import User, Gif
from beanie import init_beanie
from motor.motor_asyncio import AsyncIOMotorClient

dotenv.load_dotenv()


async def pass_call(call):
    await call.answer()


async def main():
    logger.info("Initializing MongoDB")
    mongo = AsyncIOMotorClient(os.getenv("MONGO_URL"))
    await init_beanie(database=mongo.komarugifbot, document_models=[User, Gif])

    bot = Bot(token=os.getenv("BOT_TOKEN"), parse_mode=ParseMode.HTML)
    dp = Dispatcher()
    
    router = register_routers()
    dp.include_router(router)
    
    dp.callback_query.register(pass_call, F.data == "pass")

    dp.message.middleware(ThrottlingMiddleware())
    dp.callback_query.middleware(ThrottlingMiddleware())

    dp.message.middleware(UserMiddleware())
    dp.callback_query.middleware(UserMiddleware())

    await set_bot_commands(bot)


    logger.info('Starting Bot')
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot, allowed_updates=dp.resolve_used_update_types())


if __name__ == '__main__':
    asyncio.run(main())
