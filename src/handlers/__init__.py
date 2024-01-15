from aiogram import Router
from . import basic, addgif, catalog


def register_routers() -> Router:
    router = Router()

    router.include_routers(
        basic.router,
        addgif.router,
        catalog.router
    )

    return router
