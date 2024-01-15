import math
import random

from loguru import logger
from typing import List

from aiogram import Router, F, Bot
from aiogram.types import Message, CallbackQuery, InlineKeyboardButton
from aiogram.filters import Command
from aiogram.utils.keyboard import InlineKeyboardBuilder

from src.db import User, Gif
from src.utils import url_builder
from src import stickers

router = Router()
PER_PAGE = 3

async def pagination(gifs: List[Gif], current_page: int):
    b = InlineKeyboardBuilder()
    
    for gif in gifs[current_page*PER_PAGE:(current_page + 1)*PER_PAGE]:
        b.button(
            text=gif.title,
            callback_data=f"gif:{gif.gif_id}"
        )
    
    last_page = math.ceil(len(gifs) / PER_PAGE)
    
    bottom_buttons = []
    if current_page != 0:
        bottom_buttons.append(
            InlineKeyboardButton(
                text="⏪", callback_data=f"catalog:{current_page - 1}"
            )
        )
    else:
        bottom_buttons.append(
            InlineKeyboardButton(
                text="⛔️", callback_data=f"pass"
            )
        )
    
    bottom_buttons.append(
        InlineKeyboardButton(
            text=f"{current_page + 1}/{last_page}", callback_data="pass"
        )
    )
    
    if current_page != 0:
        bottom_buttons.append(
            InlineKeyboardButton(
                text="⏩", callback_data=f"catalog:{current_page + 1}"
            )
        )
    else:
        bottom_buttons.append(
            InlineKeyboardButton(
                text="⛔️", callback_data=f"pass"
            )
        )
    
    b.adjust(1)
    b.row(*bottom_buttons)
    return b.as_markup()


@router.message(Command("catalog"))
async def catalog_cmd(message: Message):
    await message.answer_sticker(random.choice(stickers))
    gifs = await Gif.find_many(Gif.verified == True).to_list()
    reply_markup = await pagination(gifs, 0)
    await message.reply("<b>Каталог гифок с комару</b>", reply_markup=reply_markup)


@router.callback_query(F.data.startswith("catalog:"))
async def navigate_catalog(call: CallbackQuery):
    page = int(call.data.split(":")[1])
    gifs = await Gif.find_many(Gif.verified == True).to_list()
    reply_markup = await pagination(gifs, page)
    await call.answer()
    await call.message.edit_reply_markup(reply_markup=reply_markup)
    

@router.callback_query(F.data.startswith("gif:"))
async def choose_gif(call: CallbackQuery):
    gif = await Gif.find_one(Gif.gif_id == int(call.data.split(":")[1]), fetch_links=True)
    if not gif:
        await call.answer()
        return
    user = await call.bot.get_chat(gif.user.user_id)
    text = (
        f"🍌 <b>Гиф от {'@' + user.username if user.username else user.first_name}</b>\n\n"
        f"<b>Название: </b><i>{gif.title}</i>\n"
        f"<b>Описание: </b><i>{gif.description}</i>\n"
    )
    
    await call.answer()
    await call.message.answer_animation(
        gif.file_id, 
        caption=text, 
        reply_markup=url_builder(["Автор", f"tg://user?id={user.id}"])
    )
