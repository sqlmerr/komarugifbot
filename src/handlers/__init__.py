from aiogram import Router
from . import basic, addgif


def register_routers() -> Router:
    router = Router()

    router.include_routers(
        basic.router,
        addgif.router
    )

    return router
