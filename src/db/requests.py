from .models import User, Gif


async def get_user(user_id: int):
    return await User.find_one(User.user_id == user_id)


async def get_last_gif_id() -> int:
    last_gif = await Gif.all(limit=1, sort=-Gif.gif_id).to_list()
    if not last_gif:
        return 0
    return last_gif[0].gif_id
