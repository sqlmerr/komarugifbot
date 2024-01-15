from beanie import Document, Indexed, Link


class User(Document):
    user_id: Indexed(int, unique=True)


class Gif(Document):
    user: Link[User]
    gif_id: Indexed(int, unique=True)
    file_id: str
    title: str
    description: str
    verified: bool = False
